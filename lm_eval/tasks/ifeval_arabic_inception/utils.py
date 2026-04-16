"""Process results for Inception Arabic IFEval with language check.

Ports Inception's 3-stage evaluation (language check → strict → strict+langcheck)
into the lm-eval harness process_results interface.
"""

import dataclasses
import json
import unicodedata
from typing import Dict, List, Optional, Union

import regex
import regex as re  # Inception uses `import regex as re` for Unicode \p{} support

from lm_eval.tasks.ifeval_arabic_inception import instructions_registry


# ---------------------------------------------------------------------------
# Thinking-tag stripping (project convention)
# ---------------------------------------------------------------------------

THINKING_CLOSE_TAGS = (
    "</think>",
    "</think_fast>",
    "</think_faster>",
)


def extract_answer_after_last_think_close(text: str) -> str:
    last_match_idx = -1
    last_tag = None
    for tag in THINKING_CLOSE_TAGS:
        idx = text.rfind(tag)
        if idx > last_match_idx:
            last_match_idx = idx
            last_tag = tag
    if last_match_idx == -1 or last_tag is None:
        return text
    return text[last_match_idx + len(last_tag) :]


# ---------------------------------------------------------------------------
# Unicode cleanup  (ported from Inception evaluation.py lines 28-56)
# ---------------------------------------------------------------------------

_INVISIBLE_CHAR_MAP = {
    0x200B: None,  # ZERO WIDTH SPACE
    0x200C: None,  # ZERO WIDTH NON-JOINER
    0x200D: None,  # ZERO WIDTH JOINER
    0xFEFF: None,  # ZERO WIDTH NO-BREAK SPACE (BOM)
    0x00A0: 0x20,  # NO-BREAK SPACE → regular space
    0x202A: None,  # LEFT-TO-RIGHT EMBEDDING
    0x202B: None,  # RIGHT-TO-LEFT EMBEDDING
    0x202C: None,  # POP DIRECTIONAL FORMATTING
    0x202D: None,  # LEFT-TO-RIGHT OVERRIDE
    0x202E: None,  # RIGHT-TO-LEFT OVERRIDE
    0x2066: None,  # LEFT-TO-RIGHT ISOLATE
    0x2067: None,  # RIGHT-TO-LEFT ISOLATE
    0x2068: None,  # FIRST STRONG ISOLATE
    0x2069: None,  # POP DIRECTIONAL ISOLATE
}


def clean_for_english(text: str) -> str:
    text = unicodedata.normalize("NFKC", text)
    text = text.translate(_INVISIBLE_CHAR_MAP)
    text = "".join(
        ch for ch in text if unicodedata.category(ch) not in ("Cc", "Cf")
    )
    text = re.sub(r"\s+", " ", text)
    return text.strip()


# ---------------------------------------------------------------------------
# Language validation  (ported from Inception evaluation.py lines 147-265)
# ---------------------------------------------------------------------------


def is_valid_arabic_text(
    text: str, allowed_english_percentage: float = 0.05
) -> bool:
    all_letters_pattern = r"\p{L}+"
    arabic_pattern = (
        r"^[\u0600-\u06FF\u0750-\u077F"
        r"\u08A0-\u08FF\uFB50-\uFDFF"
        r"\uFE70-\uFEFF]+$"
    )
    english_pattern = r"^[a-zA-Z]+$"
    letter_sequences = regex.findall(all_letters_pattern, text)
    if not letter_sequences:
        return False
    total_words = len(letter_sequences)
    arabic_word_count = 0
    english_word_count = 0
    for seq in letter_sequences:
        if regex.fullmatch(arabic_pattern, seq):
            arabic_word_count += 1
        elif regex.fullmatch(english_pattern, seq):
            english_word_count += 1
        else:
            return False
    if english_word_count / total_words > allowed_english_percentage:
        return False
    return arabic_word_count > 0


def is_valid_english_text(text: str) -> bool:
    arabic_punctuation = "،؛؟"
    if any(char in arabic_punctuation for char in text):
        return False
    arabic_letters_pattern = (
        r"[\u0600-\u06FF"
        r"\u0750-\u077F"
        r"\u08A0-\u08FF"
        r"\uFB50-\uFDFF"
        r"\uFE70-\uFEEF]"
    )
    if re.search(arabic_letters_pattern, text):
        return False
    rejected_scripts = [
        r"[\u0590-\u05FF]",
        r"[\u0400-\u04FF]",
        r"[\u4E00-\u9FFF]",
        r"[\u3040-\u309F]",
        r"[\u30A0-\u30FF]",
        r"[\uAC00-\uD7AF]",
    ]
    for pat in rejected_scripts:
        if re.search(pat, text):
            return False
    return True


def is_valid_ar_en_text(text: str) -> bool:
    arabic_blocks = (
        r"\u0600-\u06FF"
        r"\u0750-\u077F"
        r"\u08A0-\u08FF"
        r"\uFB50-\uFDFF"
        r"\uFE70-\uFEFF"
        r"\u2080-\u2089"
    )
    allowed_letters_pattern = r"[A-Za-z" + arabic_blocks + r"]+"
    if not regex.search(allowed_letters_pattern, text):
        return False
    for seq in regex.findall(r"\p{L}+", text):
        if not regex.fullmatch(allowed_letters_pattern, seq):
            return False
    return True


def is_correct_language(response: str, lang: List[str]) -> bool:
    lang_list = sorted(set(lang))
    if not lang_list:
        return True
    if set(lang_list) == {"ar", "en"}:
        return is_valid_ar_en_text(response)
    single = lang_list[0]
    if single == "ar":
        return is_valid_arabic_text(response)
    if single == "en":
        return is_valid_english_text(response)
    raise ValueError(f"Unsupported languages: {lang}")


# ---------------------------------------------------------------------------
# Repetition detectors  (ported from Inception evaluation.py lines 211-250)
# ---------------------------------------------------------------------------


def has_repeated_sentences(response: str, max_repeats: int = 2) -> bool:
    sentences = [s.strip() for s in re.split(r"[.!?]", response) if s.strip()]
    for i in range(len(sentences) - max_repeats):
        if len(sentences[i].split()) < 3:
            continue
        if all(
            sentences[i] == sentences[i + j] for j in range(max_repeats + 1)
        ):
            return True
    return False


def has_repeated_words(response: str, min_repeats: int = 7) -> bool:
    pattern = re.compile(r"\b[0-9A-Za-z\u0621-\u064A]+\b")
    words = pattern.findall(response)
    count = 1
    for prev, curr in zip(words, words[1:]):
        if curr == prev:
            count += 1
            if count >= min_repeats:
                return True
        else:
            count = 1
    return False


def has_consecutive_repeated_ngrams(response: str, min_n: int = 5) -> bool:
    text = re.sub(r"[^\w\s]", "", response)
    words = re.findall(r"\b\w+\b", text)
    total = len(words)
    if total < 3 * min_n:
        return False
    max_n = min(total // 3, 60)
    for n in range(min_n, max_n + 1):
        for i in range(total - 3 * n + 1):
            base = tuple(words[i : i + n])
            count = 1
            j = i + n
            while j + n <= total and tuple(words[j : j + n]) == base:
                count += 1
                j += n
            if count >= 3:
                return True
    return False


# ---------------------------------------------------------------------------
# Preprocessing for language check
# (ported from Inception evaluation.py lines 268-317)
# ---------------------------------------------------------------------------


def _preprocess_for_langcheck(response: str) -> str:
    """Strip code fences, JSON punctuation, subscript digits, etc."""
    if "P.P.S." in response:
        response = response.split("P.P.S.")[0]
    response = re.sub(r"^```(?:\w*)\n?", "", response)
    response = re.sub(r"\n?```$", "", response)
    response = re.sub(r'[{}\[\]:,"]', "", response)
    response = re.sub(r"[₀₁₂₃₄₅₆₇₈₉`*]", "", response)
    return response


def run_language_check(response: str, lang: List[str]) -> bool:
    """Combined language + repetition check. Returns True if valid."""
    preprocessed = _preprocess_for_langcheck(response)

    # Repetition checks always run, even if lang is empty
    if has_repeated_words(preprocessed):
        return False
    if has_repeated_sentences(preprocessed):
        return False
    if has_consecutive_repeated_ngrams(preprocessed):
        return False

    # Language validity (default to English if lang is missing/empty)
    if not lang or lang == "":
        lang = ["en"]
    return is_correct_language(preprocessed, lang)


# ---------------------------------------------------------------------------
# Dataclasses
# ---------------------------------------------------------------------------


@dataclasses.dataclass
class InputExample:
    key: int
    instruction_id_list: List[str]
    prompt: str
    kwargs: List[Dict[str, Optional[Union[str, int]]]]
    lang: Optional[List[str]] = None


@dataclasses.dataclass
class OutputExample:
    instruction_id_list: List[str]
    prompt: str
    response: str
    follow_all_instructions: bool
    follow_instruction_list: List[bool]


# ---------------------------------------------------------------------------
# Instruction following evaluation  (ported from Inception evaluation.py)
# ---------------------------------------------------------------------------


def test_instruction_following_strict(
    inp: InputExample, response: str
) -> OutputExample:
    instruction_list = inp.instruction_id_list
    is_following_list = []
    for idx, instr_id in enumerate(instruction_list):
        if instr_id not in instructions_registry.INSTRUCTION_DICT:
            is_following_list.append(False)
            continue
        cls = instructions_registry.INSTRUCTION_DICT[instr_id]
        inst = cls(instr_id)
        filtered_kwargs = {k: v for k, v in inp.kwargs[idx].items() if v is not None}
        inst.build_description(**filtered_kwargs)
        args = inst.get_instruction_args()
        if args and "prompt" in args:
            inst.build_description(prompt=inp.prompt)
        is_following_list.append(
            bool(response.strip() and inst.check_following(response))
        )
    return OutputExample(
        instruction_id_list=instruction_list,
        prompt=inp.prompt,
        response=response,
        follow_all_instructions=all(is_following_list),
        follow_instruction_list=is_following_list,
    )


# ---------------------------------------------------------------------------
# lm-eval harness interface
# ---------------------------------------------------------------------------


def process_results(doc, results):
    response_raw = str(results[0]) if results and results[0] is not None else ""
    response_after_think = extract_answer_after_last_think_close(response_raw)
    response = clean_for_english(response_after_think)

    # Parse kwargs (HF datasets may store as string)
    kwargs = doc["kwargs"]
    if isinstance(kwargs, str):
        kwargs = json.loads(kwargs)

    lang = doc.get("lang")
    # Coerce bare strings to lists
    if isinstance(lang, str):
        lang = [lang] if lang else []

    inp = InputExample(
        key=doc["key"],
        instruction_id_list=doc["instruction_id_list"],
        prompt=doc["prompt"],
        kwargs=kwargs,
        lang=lang,
    )

    # Stage 1: strict instruction following (no language gating)
    out_strict = test_instruction_following_strict(inp, response)

    # Stage 2: language check
    lang_check_passed = run_language_check(response, lang)

    # Stage 3: strict with language gating
    if lang_check_passed:
        langcheck_follow_list = out_strict.follow_instruction_list
    else:
        langcheck_follow_list = [False] * len(out_strict.follow_instruction_list)

    return {
        "prompt_level_strict_acc": out_strict.follow_all_instructions,
        "inst_level_strict_acc": out_strict.follow_instruction_list,
        "prompt_level_strict_langcheck_acc": all(langcheck_follow_list),
        "inst_level_strict_langcheck_acc": langcheck_follow_list,
        "language_check_acc": lang_check_passed,
    }


def agg_inst_level_acc(items):
    flat_items = [item for sublist in items for item in sublist]
    if not flat_items:
        return 0.0
    return sum(flat_items) / len(flat_items)
