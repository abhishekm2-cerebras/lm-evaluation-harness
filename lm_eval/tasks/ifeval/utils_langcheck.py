from lm_eval.tasks.ifeval.langcheck_utils import clean_for_english, run_language_check
from lm_eval.tasks.ifeval.utils import (
    InputExample,
    extract_answer_after_last_think_close,
    test_instruction_following_loose,
    test_instruction_following_strict,
)

# Languages that Jais-family models are designed to generate.
_ALLOWED_RESPONSE_LANGUAGES = {"en", "ar"}


def process_docs(dataset):
    """Exclude samples whose language:response_language is not English or Arabic."""

    def _keep(doc):
        for inst_id, kw in zip(doc["instruction_id_list"], doc["kwargs"]):
            if inst_id == "language:response_language":
                lang = kw.get("language") if isinstance(kw, dict) else None
                if lang not in _ALLOWED_RESPONSE_LANGUAGES:
                    return False
        return True

    return dataset.filter(_keep)


def process_results(doc, results):
    inp = InputExample(
        key=doc["key"],
        instruction_id_list=doc["instruction_id_list"],
        prompt=doc["prompt"],
        kwargs=doc["kwargs"],
    )
    response_raw = str(results[0]) if results and results[0] is not None else ""
    response = extract_answer_after_last_think_close(response_raw)

    # Apply clean_for_english per reference (evaluation.py)
    cleaned = clean_for_english(response)

    # Instruction following (always computed, no gating)
    out_strict = test_instruction_following_strict(inp, cleaned)
    out_loose = test_instruction_following_loose(inp, cleaned)

    # Language + repetition gate
    lang_check_passed = run_language_check(cleaned)

    # Langcheck-gated metrics (zeroed if language check fails)
    if lang_check_passed:
        langcheck_strict_list = out_strict.follow_instruction_list
        langcheck_loose_list = out_loose.follow_instruction_list
    else:
        langcheck_strict_list = [False] * len(out_strict.follow_instruction_list)
        langcheck_loose_list = [False] * len(out_loose.follow_instruction_list)

    return {
        # Without langcheck (normal IFEval)
        "prompt_level_strict_acc": out_strict.follow_all_instructions,
        "inst_level_strict_acc": out_strict.follow_instruction_list,
        "prompt_level_loose_acc": out_loose.follow_all_instructions,
        "inst_level_loose_acc": out_loose.follow_instruction_list,
        # With langcheck
        "prompt_level_strict_langcheck_acc": all(langcheck_strict_list),
        "inst_level_strict_langcheck_acc": langcheck_strict_list,
        "prompt_level_loose_langcheck_acc": all(langcheck_loose_list),
        "inst_level_loose_langcheck_acc": langcheck_loose_list,
        # Language check pass rate
        "language_check_acc": lang_check_passed,
    }


def agg_inst_level_acc(items):
    flat_items = [item for sublist in items for item in sublist]
    if not flat_items:
        return 0.0
    return sum(flat_items) / len(flat_items)
