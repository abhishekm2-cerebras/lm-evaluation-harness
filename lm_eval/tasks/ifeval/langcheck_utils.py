"""Language validation and repetition detection for IFEval langcheck.

Exact port of the language checking logic from Inception_IFEval/evaluation.py.
"""

import unicodedata

import regex as re


# ---------------------------------------------------------------------------
# Text cleaning (evaluation.py lines 28-56)
# ---------------------------------------------------------------------------

_INVISIBLE_CHAR_MAP = {
    0x200B: None,   # ZERO WIDTH SPACE
    0x200C: None,   # ZERO WIDTH NON-JOINER
    0x200D: None,   # ZERO WIDTH JOINER
    0xFEFF: None,   # ZERO WIDTH NO-BREAK SPACE (BOM)
    0x00A0: 0x20,   # NO-BREAK SPACE → regular space

    0x202A: None,   # LEFT-TO-RIGHT EMBEDDING
    0x202B: None,   # RIGHT-TO-LEFT EMBEDDING
    0x202C: None,   # POP DIRECTIONAL FORMATTING
    0x202D: None,   # LEFT-TO-RIGHT OVERRIDE
    0x202E: None,   # RIGHT-TO-LEFT OVERRIDE

    0x2066: None,   # LEFT-TO-RIGHT ISOLATE
    0x2067: None,   # RIGHT-TO-LEFT ISOLATE
    0x2068: None,   # FIRST STRONG ISOLATE
    0x2069: None,   # POP DIRECTIONAL ISOLATE
}


def clean_for_english(text: str) -> str:
    text = unicodedata.normalize("NFKC", text)
    text = text.translate(_INVISIBLE_CHAR_MAP)
    text = "".join(
        ch for ch in text
        if unicodedata.category(ch) not in ("Cc", "Cf")
    )
    text = re.sub(r"\s+", " ", text)
    return text.strip()


# ---------------------------------------------------------------------------
# Preprocessing before language / repetition checks (evaluation.py lines 276-281)
# ---------------------------------------------------------------------------

def _preprocess_for_langcheck(text: str) -> str:
    if "P.P.S." in text:
        text = text.split("P.P.S.")[0]
    text = re.sub(r'^```(?:\w*)\n?', '', text)
    text = re.sub(r'\n?```$', '', text)
    text = re.sub(r'[{}\[\]:,"]', '', text)
    text = re.sub(r'[₀₁₂₃₄₅₆₇₈₉`*]', '', text)
    return text


# ---------------------------------------------------------------------------
# Language validation (evaluation.py lines 172-192)
# ---------------------------------------------------------------------------

ARABIC_PUNCTUATION = "،؛؟"


def is_valid_english_text(text: str) -> bool:
    arabic_punctuation = "،؛؟"
    if any(char in arabic_punctuation for char in text):
        return False
    arabic_letters_pattern = (
        r'[\u0600-\u06FF'
        r'\u0750-\u077F'
        r'\u08A0-\u08FF'
        r'\uFB50-\uFDFF'
        r'\uFE70-\uFEEF]'
    )
    if re.search(arabic_letters_pattern, text):
        return False
    rejected_scripts = [
        r'[\u0590-\u05FF]', r'[\u0400-\u04FF]', r'[\u4E00-\u9FFF]',
        r'[\u3040-\u309F]', r'[\u30A0-\u30FF]', r'[\uAC00-\uD7AF]',
    ]
    for pat in rejected_scripts:
        if re.search(pat, text):
            return False
    return True


# ---------------------------------------------------------------------------
# Repetition detection (evaluation.py lines 211-250)
# ---------------------------------------------------------------------------

def has_repeated_sentences(response: str, max_repeats: int = 2) -> bool:
    sentences = [s.strip() for s in re.split(r'[.!?]', response) if s.strip()]
    for i in range(len(sentences) - max_repeats):
        if len(sentences[i].split()) < 3:
            continue
        if all(sentences[i] == sentences[i + j] for j in range(max_repeats + 1)):
            return True
    return False


def has_repeated_words(response: str, min_repeats: int = 7) -> bool:
    pattern = re.compile(r'\b[0-9A-Za-z\u0621-\u064A]+\b')
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
    text = re.sub(r'[^\w\s]', '', response)
    words = re.findall(r'\b\w+\b', text)
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
# Combined language check
# ---------------------------------------------------------------------------

def run_language_check(cleaned_response: str) -> bool:
    """Run language validation + repetition detection on a clean_for_english'd response.

    Args:
        cleaned_response: Text already processed by clean_for_english().

    Returns:
        True if the response passes all checks (valid English, no repetitions).
    """
    preprocessed = _preprocess_for_langcheck(cleaned_response)

    if not is_valid_english_text(preprocessed):
        return False

    if has_repeated_words(preprocessed):
        return False
    if has_repeated_sentences(preprocessed):
        return False
    if has_consecutive_repeated_ngrams(preprocessed):
        return False

    return True


# ---------------------------------------------------------------------------
# Arabic response validation (used by ifeval_arabic_inception_hf_langcheck)
# ---------------------------------------------------------------------------

ARABIC_IFEVAL_MAX_ENGLISH_RATIO = 0.07

_ENGLISH_WORD_RE = re.compile(r'^[a-zA-Z]+$')
_ARABIC_SCRIPT_RANGES = (
    (0x0600, 0x06FF), (0x0750, 0x077F), (0x08A0, 0x08FF),
    (0xFB50, 0xFDFF), (0xFE70, 0xFEFF), (0x1EE00, 0x1EEFF),
)


def _is_arabic_letter(ch: str) -> bool:
    if not ch.isalpha():
        return False
    cp = ord(ch)
    return any(s <= cp <= e for s, e in _ARABIC_SCRIPT_RANGES)


def _iter_letter_words(text: str) -> list[str]:
    current = []
    words = []
    for ch in text:
        if ch.isalpha() or (unicodedata.category(ch) in {"Mn", "Mc", "Me"} and current):
            current.append(ch)
        else:
            if current:
                words.append("".join(current))
                current = []
    if current:
        words.append("".join(current))
    return words


def compute_english_word_ratio(text: str) -> float:
    """Return the fraction of letter-words that are purely English."""
    english_count = 0
    total_count = 0
    for word in _iter_letter_words(text):
        total_count += 1
        if _ENGLISH_WORD_RE.fullmatch(word):
            english_count += 1
    if total_count == 0:
        return 0.0
    return english_count / total_count


def validate_arabic_response(text: str) -> tuple[bool, str]:
    if not text or not text.strip():
        return False, "empty_response"
    preprocessed = _preprocess_for_langcheck(text)
    if has_repeated_words(preprocessed):
        return False, "repeated_words"
    if has_repeated_sentences(preprocessed):
        return False, "repeated_sentences"
    if has_consecutive_repeated_ngrams(preprocessed):
        return False, "repeated_ngrams"
    return True, "ok"
