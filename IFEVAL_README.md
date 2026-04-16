# IFEval Tasks with Language Check

This document describes all IFEval task variants in this repository, their language validation checks, and how scores are computed.

## Task Overview

| Task Name | Dataset | Language | Lang Check | Loose Eval | Docs |
|---|---|---|---|---|---|
| `ifeval` | `google/IFEval` | English | No | Yes | 541 |
| `ifeval_langcheck` | `google/IFEval` | English | Yes | Yes | 541 |
| `ifeval_arabic_inception_hf` | `inceptionai/Arabic_IFEval` | Arabic | No | Yes | 404 |
| `ifeval_arabic_inception_hf_langcheck` | `inceptionai/Arabic_IFEval` | Arabic | Yes | Yes | 404 |
| `ifeval_arabic_inception` | Local JSONL (Inception) | Arabic | Yes (built-in) | No | 404 |

The base tasks (`ifeval`, `ifeval_arabic_inception_hf`) evaluate instruction following without any language quality gating. The `_langcheck` variants add a validation layer that zeros out scores for responses that fail language or repetition checks. `ifeval_arabic_inception` is a standalone port of Inception AI's evaluation with the language check built in.

---

## 1. English IFEval with Language Check (`ifeval_langcheck`)

**Task name**: `ifeval_langcheck`
**Files**: `lm_eval/tasks/ifeval/ifeval_langcheck.yaml`, `utils_langcheck.py`, `langcheck_utils.py`

### Validation Pipeline

Responses are validated by `validate_english_response()` in `langcheck_utils.py`. The checks run in order; the first failure short-circuits:

#### 1.1 Empty Response Check
An empty or whitespace-only response is rejected.

#### 1.2 Arabic Punctuation Check
The response is rejected if it contains any of these Arabic punctuation characters:
`،` (comma), `؛` (semicolon), `؟` (question mark), `٪` (percent), `٫` (decimal separator), `٬` (thousands separator), `۔` (full stop), `«`, `»` (guillemets).

#### 1.3 Non-English Word Check (Inception-style `\p{L}+`)
All letter-words in the response are found using the Unicode-aware regex `\p{L}+` (via the `regex` library). Every word must be purely English (`^[a-zA-Z]+$`). **No other language is allowed** — any Arabic, Hebrew, Chinese, Korean, Japanese, Cyrillic, Greek, or mixed-script word causes immediate rejection.

This catches:
- Arabic words (e.g., `مرحبا`)
- Other scripts (e.g., `שלום`, `你好`, `Привет`, `こんにちは`, `안녕`, `θ`)
- Mixed-script words where half the letters are from one script and half from another (e.g., `Helloمرحبا`)

Numbers, standard punctuation, and symbols are not letter-words and are ignored by this check.

#### 1.4 Repetition Detection (Inception-style, 3 detectors)
Before checking repetition, the response is preprocessed: code fences, JSON punctuation (`{}[]:,"`), subscript digits, backticks, and asterisks are stripped.

| Detector | Threshold | What it catches |
|---|---|---|
| Repeated words | **7+** consecutive identical words | Single-word loops (e.g., `hello hello hello hello hello hello hello`) |
| Repeated sentences | **3+** consecutive identical sentences of 3+ words | Sentence-level loops (e.g., `I am fine. I am fine. I am fine.`) |
| Repeated n-grams | **3+** consecutive identical n-grams (n = 5 to 60) | Long degenerate patterns (e.g., a 10-word phrase repeated 3 times) |

These thresholds are more lenient on small repeats than a naive 2-consecutive approach. A response like `"hello hello"` (2 consecutive) passes, but `"hello" * 7` does not. A sentence repeated twice passes, but three times does not.

### Metrics

| Metric | Aggregation | Description |
|---|---|---|
| `prompt_level_strict_acc` | mean | Fraction of prompts where all instructions pass (strict), langcheck-gated |
| `inst_level_strict_acc` | flatten + mean | Fraction of individual instructions that pass (strict), langcheck-gated |
| `prompt_level_loose_acc` | mean | Same as strict but tries 8 response variants (remove first/last lines, strip asterisks) |
| `inst_level_loose_acc` | flatten + mean | Instruction-level loose, langcheck-gated |

### How Scores Are Computed

1. Strip thinking tags (`</think>`, `</think_fast>`, `</think_faster>`).
2. Run `validate_english_response()`.
3. **If validation fails**: all 4 metrics are zeroed for this sample (all `False`). The sample still counts in the denominator.
4. **If validation passes**: run standard IFEval strict and loose evaluation. Return actual pass/fail per instruction.

---

## 2. Arabic IFEval with Language Check (`ifeval_arabic_inception_hf_langcheck`)

**Task name**: `ifeval_arabic_inception_hf_langcheck`
**Files**: `lm_eval/tasks/ifeval_arabic_inception_hf/ifeval_arabic_inception_hf_langcheck.yaml`, `utils_langcheck.py`; shared `lm_eval/tasks/ifeval/langcheck_utils.py`

### Validation Pipeline

Responses are validated by `validate_arabic_response()` plus an English word ratio check.

#### 2.1 Empty Response Check
Same as English.

#### 2.2 Script Validation
Each letter-word is classified as English, Arabic, or other. Words are split by iterating characters and grouping alphabetic characters with their combining marks (Arabic diacritics/tashkeel stay attached to base letters).

| Condition | Result |
|---|---|
| Word mixes Arabic + English letters | Reject |
| Word contains non-Arabic, non-English script (Hebrew, Chinese, etc.) | Reject |
| Word is purely English | Allow |
| Word is purely Arabic | Allow |

Both English and Arabic words are allowed because Arabic text commonly contains English abbreviations and technical terms.

#### 2.3 Repetition Detection (stricter thresholds)
Uses the older 2-consecutive n-gram approach:

| Detector | Threshold |
|---|---|
| Sentence repetition | Any n-gram of sentences (1 to 4) repeated 2 times consecutively |
| Word repetition | Any n-gram of words (1 to 6) repeated 2 times consecutively |

This means even `"مرحبا مرحبا"` (a single word repeated once) is flagged.

#### 2.4 English Word Ratio Cap (7%)
After the base validation passes, the ratio of purely English letter-words to total letter-words is computed. If the ratio exceeds **7%**, the response is rejected.

**Format exemption**: Samples where the output is expected to be HTML/JSON/JSONL are exempt from this ratio check. A sample is exempt if:
- Its `instruction_id_list` contains `detectable_format:json_format`, OR
- Its prompt text contains the word "html", "json", or "jsonl" (case-insensitive)

### Metrics

Same 4 metrics as the English langcheck task (strict + loose, prompt-level + instruction-level), all langcheck-gated.

### How Scores Are Computed

1. Strip thinking tags.
2. Run `validate_arabic_response()` (script + repetition checks).
3. If not format-exempt, check English word ratio > 7%.
4. **If any check fails**: all 4 metrics zeroed.
5. **If all pass**: run standard IFEval strict and loose evaluation.

---

## 3. Inception Arabic IFEval (`ifeval_arabic_inception`)

**Task name**: `ifeval_arabic_inception`
**Files**: `lm_eval/tasks/ifeval_arabic_inception/ifeval_arabic_inception.yaml`, `utils.py`, `instructions.py`, `instructions_registry.py`, `instructions_util.py`, `ar_input_data.jsonl`

This is a direct port of Inception AI's standalone Arabic IFEval evaluation. It uses a local JSONL dataset with a per-prompt `lang` field that controls which language check to apply.

### Dataset

404 Arabic prompts from Inception's `ar_input_v3_lang_final.jsonl`, each with a `lang` field:

| `lang` value | Count | Meaning |
|---|---|---|
| `["ar"]` | 352 | Response must be Arabic (up to 5% English allowed) |
| `["ar", "en"]` | 52 | Response can be mixed Arabic + English (for JSON, code, technical content) |

### Preprocessing

Before any checks, responses are:
1. Stripped of thinking tags (`</think>`, `</think_fast>`, `</think_faster>`).
2. Unicode-normalized (NFKC).
3. Cleaned of invisible characters (zero-width spaces, bidi marks, BOM).
4. Control/format characters removed (Unicode categories `Cc`, `Cf`).
5. Whitespace collapsed.

### Validation Pipeline (Language Check)

Before repetition and language checks, additional preprocessing strips code fences, JSON punctuation (`{}[]:,"`), subscript digits, backticks, and asterisks.

#### 3.1 Repetition Detection (3 detectors, same as English langcheck)

| Detector | Threshold | What it catches |
|---|---|---|
| `has_repeated_words` | **7+** consecutive identical words | Single-word loops |
| `has_repeated_sentences` | **3+** consecutive identical sentences (3+ words) | Sentence-level loops |
| `has_consecutive_repeated_ngrams` | **3+** consecutive identical n-grams (n = 5 to 60) | Long degenerate patterns |

Repetition checks always run, regardless of the `lang` field.

#### 3.2 Language Validation (per-prompt)

Dispatches based on the `lang` field:

**`lang = ["ar"]`** — `is_valid_arabic_text()`:
- Finds all letter-words via `\p{L}+`.
- Each word must be purely Arabic or purely English.
- Any other script (Hebrew, CJK, etc.) causes immediate rejection.
- English words are allowed up to **5%** of total letter-words.
- At least one Arabic word must be present.

**`lang = ["ar", "en"]`** — `is_valid_ar_en_text()`:
- Finds all letter-words via `\p{L}+`.
- Each word must consist only of Arabic or English letters (or a mix within the allowed ranges).
- No percentage cap — any mix of Arabic and English is fine.
- Any other script causes immediate rejection.

### Instruction Types

31 instruction types, including 6 that are not in the standard `ifeval_arabic_inception_hf` task:

| Instruction ID | Description | Unique to this task? |
|---|---|---|
| `detectable_format:word_repetition` | No word repeated 3+ times consecutively | Yes |
| `detectable_format:sent_repetition` | No sentence repeated more than once | Yes |
| `detectable_format:check_punct_lang` | Punctuation must match specified language (Arabic or English) | Yes |
| `detectable_format:tashkeel` | Exact count of a named Arabic diacritical mark | Different class name |
| `keywords:list_existence` | Check keyword list existence with modes (all/any) | Different class name |
| `keywords:letter_list_freq` | Check letter-based word frequency with Arabic normalization | Different class name |

### Metrics (5 total)

| Metric | Aggregation | Description |
|---|---|---|
| `prompt_level_strict_acc` | mean | Strict accuracy, **without** langcheck gating |
| `inst_level_strict_acc` | flatten + mean | Instruction-level strict, **without** langcheck gating |
| `prompt_level_strict_langcheck_acc` | mean | Strict accuracy, **with** langcheck gating (primary metric) |
| `inst_level_strict_langcheck_acc` | flatten + mean | Instruction-level strict, **with** langcheck gating |
| `language_check_acc` | mean | Fraction of prompts that pass the language + repetition check |

There is no loose evaluation (matches Inception's original design).

### How Scores Are Computed (3-stage pipeline)

1. **Stage 1 — Strict instruction following**: For each prompt, instantiate instruction checkers from the registry, call `check_following(response)`. Produces per-instruction boolean pass/fail. This runs regardless of language check results.

2. **Stage 2 — Language check**: Run repetition detectors + language validation (dispatched by `lang` field). Produces a single boolean per prompt.

3. **Stage 3 — Strict with language gating**: If language check passed, keep Stage 1 results. If language check failed, override all instructions to `False`.

Both Stage 1 and Stage 3 results are returned as separate metrics, so you can see the impact of language gating.

---

## Comparison of Repetition Detection

| Property | English langcheck / Inception Arabic | Arabic HF langcheck |
|---|---|---|
| Approach | Inception-style (3 separate detectors) | N-gram consecutive match |
| Preprocessing | Strip code fences, JSON punctuation, subscript digits | None |
| Word repetition threshold | 7+ consecutive identical words | 2 consecutive identical (any n-gram up to 6) |
| Sentence repetition threshold | 3+ consecutive identical (3+ words each) | 2 consecutive identical (any n-gram up to 4) |
| N-gram detection | n=5..60, requires 3+ consecutive matches | n=1..6, requires 2 consecutive matches |
| `"hello hello"` | Valid | Invalid |
| `"I am fine. I am fine."` | Valid | Invalid |
| `"hello" * 7` | Invalid | Invalid |
| `"I am fine." * 3` | Invalid | Invalid |

## Comparison of Language Validation

| Property | English langcheck | Arabic HF langcheck | Inception Arabic |
|---|---|---|---|
| Word detection | `\p{L}+` (Unicode letter sequences) | Character-by-character script profiling | `\p{L}+` (Unicode letter sequences) |
| English words | Allowed | Allowed (up to 7%, exempt for JSON/HTML) | Allowed (up to 5% for `lang=["ar"]`, unlimited for `lang=["ar","en"]`) |
| Arabic words | **Not allowed** (0% tolerance) | Allowed | Required for `lang=["ar"]` |
| Other scripts | Rejected immediately | Rejected immediately | Rejected immediately |
| Mixed-script words | Rejected (caught by `\p{L}+` — doesn't match any single-script pattern) | Rejected (explicit mixed-script check) | Rejected (doesn't match Arabic or English pattern) |
| Arabic punctuation | Rejected (`،؛؟٪٫٬۔«»`) | Not checked (expected in Arabic) | Not checked for Arabic; checked for English |
| Per-prompt language dispatch | No (always English) | No (always Arabic) | Yes (via `lang` field: `["ar"]`, `["ar","en"]`) |
