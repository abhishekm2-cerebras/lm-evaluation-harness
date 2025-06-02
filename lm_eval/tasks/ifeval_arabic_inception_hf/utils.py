import dataclasses
from typing import Dict, Optional, Union

from lm_eval.tasks.ifeval_arabic_inception_hf import instructions_registry


@dataclasses.dataclass
class InputExample:
    key: int
    instruction_id_list: list[str]
    prompt: str
    kwargs: list[Dict[str, Optional[Union[str, int]]]]


@dataclasses.dataclass
class OutputExample:
    instruction_id_list: list[str]
    prompt: str
    response: str
    follow_all_instructions: bool
    follow_instruction_list: list[bool]


def test_instruction_following_strict(
    inp,
    response,
):
    """Tests response to see if instructions are followed."""
    instruction_list = inp.instruction_id_list
    is_following_list = []

    for index, instruction_id in enumerate(instruction_list):
        if instruction_id in instructions_registry.INSTRUCTION_DICT:
            instruction_cls = instructions_registry.INSTRUCTION_DICT[instruction_id]
        else:
            is_following_list.append(False)
            continue
        
        instruction = instruction_cls(instruction_id)

        # Remove None values from kwargs to avoid unexpected keyword argument errors in build_description method.
        if isinstance(inp.kwargs, str):
            inp.kwargs = eval(inp.kwargs)
        kwargs = {k: v for k, v in inp.kwargs[index].items() if v}
        instruction.build_description(**kwargs)
        args = instruction.get_instruction_args()
        if args and "prompt" in args:
            instruction.build_description(prompt=inp.prompt)

        if response.strip() and instruction.check_following(response):
            is_following_list.append(True)
        else:
            is_following_list.append(False)

    return OutputExample(
        instruction_id_list=inp.instruction_id_list,
        prompt=inp.prompt,
        response=response,
        follow_all_instructions=all(is_following_list),
        follow_instruction_list=is_following_list,
    )


def test_instruction_following_loose(
    inp,
    response,
):
    """Tests response for an upper bound for following instructions."""
    r = response.split("\n")
    response_remove_first = "\n".join(r[1:]).strip()
    response_remove_last = "\n".join(r[:-1]).strip()
    response_remove_both = "\n".join(r[1:-1]).strip()
    revised_response = response.replace("*", "")
    revised_response_remove_first = response_remove_first.replace("*", "")
    revised_response_remove_last = response_remove_last.replace("*", "")
    revised_response_remove_both = response_remove_both.replace("*", "")
    all_responses = [
        response,
        revised_response,
        response_remove_first,
        response_remove_last,
        response_remove_both,
        revised_response_remove_first,
        revised_response_remove_last,
        revised_response_remove_both,
    ]
    instruction_list = inp.instruction_id_list
    is_following_list = []

    for index, instruction_id in enumerate(instruction_list):
        instruction_cls = instructions_registry.INSTRUCTION_DICT[instruction_id]

        instruction = instruction_cls(instruction_id)

        # Remove None values from kwargs to avoid unexpected keyword argument errors in build_description method.
        if isinstance(inp.kwargs, str):
            inp.kwargs = eval(inp.kwargs)
        kwargs = {k: v for k, v in inp.kwargs[index].items() if v}
        instruction.build_description(**kwargs)
        args = instruction.get_instruction_args()
        if args and "prompt" in args:
            instruction.build_description(prompt=inp.prompt)

        is_following = False
        for r in all_responses:
            if r.strip() and instruction.check_following(r):
                is_following = True
                break

        is_following_list.append(is_following)

    return OutputExample(
        instruction_id_list=inp.instruction_id_list,
        prompt=inp.prompt,
        response=response,
        follow_all_instructions=all(is_following_list),
        follow_instruction_list=is_following_list,
    )


def process_results(doc, results):
    inp = InputExample(
        key=doc["key"],
        instruction_id_list=doc["instruction_id_list"],
        prompt=doc["prompt"],
        kwargs=doc["kwargs"],
    )
    response = results[0]
    out_strict = test_instruction_following_strict(inp, response)
    out_loose = test_instruction_following_loose(inp, response)

    return {
        "prompt_level_strict_acc": out_strict.follow_all_instructions,
        "inst_level_strict_acc": out_strict.follow_instruction_list,
        "prompt_level_loose_acc": out_loose.follow_all_instructions,
        "inst_level_loose_acc": out_loose.follow_instruction_list,
    }


def agg_inst_level_acc(items):
    flat_items = [item for sublist in items for item in sublist]
    inst_level_acc = sum(flat_items) / len(flat_items)
    return inst_level_acc



"""
InputExample(key=4739, instruction_id_list=['keywords:frequency', 'keywords:list_existence'], prompt="اكتب قصة قصيرة تتحدث عن شجرة زيتون معمّرة تحكي ذكرياتها عبر الأجيال. يجب أن تحتوي القصة على  كلمة 'جذور' مكررة مرتين. ضمّن في اجابتك جميع ضمائر المخاطب الخاصة بالرفع: أنتَ - أنتِ - أنتما -  أنتم - أنْتُنَّ.  ", kwargs=[{'relation': 'at least', 'keyword': 'جذور', 'frequency': 2}, {'keywords': ['أنت', 'أنتما', 'أنتم', 'أنتن'], 'mode': 'all'}])

InputExample(key=4740, instruction_id_list=['keywords:frequency', 'keywords:letter_list_freq'], prompt='اكتب قصة شيقة ومؤثرة عن مرحلة البلوغ، تسلط الضوء على التغيرات والتح
 يات التي يمر بها المراهقين، مع التأكيد على أن تظهر كلمتي "بنات العمومة" أكثر من مرتين بطريقة طبيعية ومترابطة في سياق القصة. بالإضافة إلى ذلك، اجعل النص يحتوي بشكل مبدع عل
  خمس كلمات على الأقل تبدأ بالحروف اللثوية التالية: ث، ذ، ظ، بحيث تساهم في إثراء اللغة وجمال السرد.', kwargs=[{'relation': 'at least', 'keyword': 'بنات العمومة', 'frequency': 3}, {'letters': ['ث', 'ذ', 'ظ'], 'frequency': 5, 'relation': 'at least', 'position': 'start'}])

InputExample(key=4741, instruction_id_list=['detectable_content:number_placeholders', 'keywords:letter_list_freq', 'keywords:letter_list_freq'], prompt='اكتب مقالًا مفصلًا ب
 نوان "كيفية إجراء مقابلة عمل"، يشرح الخطوات الأساسية والنصائح العملية لإعطاء انطباع إيجابي. تأكد من تضمين على الأقل مكان حفظ داخل أقواس مربعة مثل [السؤال] بطريقة تتناسب م
  السياق. بالإضافة إلى ذلك، اجعل المقال يحتوي على خمس كلمات على الأقل تنتهي بالحروف الحلقية: ء، هـ، ع، ح، غ، خ وتبدأ بالحروف القلقلة ، حروف القلقلة هي : ق - ط - ب - ج - د ', kwargs=[{'num_placeholders': 1}, {'letters': ['ء', 'ه', 'ع', 'ح', 'غ', 'خ'], 'frequency': 5, 'relation': 'at least', 'position': 'end'}, {'letters': ['ق', 'ط', 'ب', 'ج', 'د'], 'frequency': 5, 'relation': 'at least', 'position': 'start'}])

InputExample(key=4772, instruction_id_list=['detectable_format:tashkeel'], prompt='أنشئ نصًّا قصيرًا عن فتاةٍ تُحبُّ النجومَ، واستخدم خمس كلمات تنتهي بتنوين الكسر؟', kwargs='[{"tashkeel_name": "Kasratan", "count": 5}]')

InputExample(key=4773, instruction_id_list=['detectable_format:tashkeel'], prompt='صِف مشهدًا عن شجرةٍ كبيرةٍ يُحلقُ حولها الطيورُ  أكتب ردك باستخدام ١٠ كلمات تتضمن تنوين الضم؟', kwargs='[{"tashkeel_name": "Dammatan", "count": 10}]')

InputExample(key=4774, instruction_id_list=['detectable_format:tashkeel', 'detectable_format:tashkeel'], prompt='اكتب قصةً عن ولدٍ يساعدُ عجوزًا في عبورِ الطريقِ، مستخدمًا خمس كل
 اتٍ تنتهي بتنوين الفتح، وثلاث كلماتٍ تحتوي على الشدة  مع الالتزام بتشكيل النص؟', kwargs='[{"tashkeel_name": "Fathatan", "count": 5}, {"tashkeel_name": "Shadda", "count": 3}]')

 letter_list_freq: at least
less than


{'tashkeel_name': 'Kasratan', 'count': 5}
{'tashkeel_name': 'Dammatan', 'count': 10}
{'tashkeel_name': 'Fathatan', 'count': 5}
{'tashkeel_name': 'Shadda', 'count': 3}
{'tashkeel_name': 'Shadda', 'count': 4}
{'tashkeel_name': 'Kasratan', 'count': 5}
{'tashkeel_name': 'Fatha', 'count': 3}
{'tashkeel_name': 'Damma', 'count': 5}
{'tashkeel_name': 'Kasratan', 'count': 5}
{'tashkeel_name': 'Kasra', 'count': 3}

"""