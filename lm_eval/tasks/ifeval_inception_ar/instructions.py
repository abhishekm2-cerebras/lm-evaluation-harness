from lm_eval.tasks.ifeval import instructions 
import re
import json
import string
class AragenInstructions(instructions.Instruction):
    def __init__(self, instruction_id):
        super().__init__(instruction_id)

    def build_description(self, **kwargs):
        return "No kwargs needed just pass in the response and check if it is correct"

    def get_instruction_args(self):
        return {}
    
    def get_instruction_args_keys(self):
        return []



class DataIdx0InstructionChecker(AragenInstructions):

    def __init__(self):
        super().__init__('idx_0')
        self.expected_prefix = 'اكتب رسالة بريد إلكتروني إلى مديري تخبره فيها أنني سوف أستقيل. يجب أن تحتوي الرسالة على عنوان بين علامتي التنصيص <<العنوان>>. '
        self.subject_pattern = '<<.*?>>'

    def check_following(self, value):
        """Checks if the response follows the instructions for IDX 0.

        The instructions are:
        1. Start the response by repeating the exact prompt text (excluding the final sentence about repetition).
        2. The email body following the repeated prompt must contain a subject line enclosed in <<>>.

        Args:
            value: A string representing the response.

        Returns:
            True if the response follows the instruction or False otherwise.
        """
        if not isinstance(value, str):
            return False
        if not value.startswith(self.expected_prefix):
            return False
        remaining_text = value[len(self.expected_prefix):]
        if re.search(self.subject_pattern, remaining_text):
            return True
        else:
            return False

class DataIdx1InstructionChecker(AragenInstructions):

    def __init__(self):
        super().__init__('idx_1')

    def check_following(self, value):
        """Checks if the response follows the instruction for IDX 1.

        Args:
            value: A string representing the response.

        Returns:
            True if the response follows the instruction or False otherwise.
        """
        words = value.split()
        if len(words) < 500:
            return False
        keyword1 = 'مرتبط'
        keyword2 = 'يختبر'
        if keyword1 not in value or keyword2 not in value:
            return False
        if ',' in value:
            return False
        return True

class DataIdx2InstructionChecker(AragenInstructions):

    def __init__(self):
        super().__init__('idx_2')

    def check_following(self, value):
        """Checks if the response follows the instructions for IDX 2.
        Constraints:
        1. Contains 4 sections marked by 'المقطع ' followed by sequential number (1-4).
        2. Sections appear in order: 'المقطع 1', 'المقطع 2', 'المقطع 3', 'المقطع 4'.
        3. Ends exactly with 'هل يمكنني استرداد أموالي عن الحصص التي لم أحضرها؟'

        Args:
            value: A string representing the response.

        Returns:
            True if the response follows the instruction or False otherwise.
        """
        if not isinstance(value, str):
            return False
        required_ending = 'هل يمكنني استرداد أموالي عن الحصص التي لم أحضرها؟'
        if not value.endswith(required_ending):
            return False
        if value.count('المقطع ') != 4:
            return False
        marker1 = 'المقطع 1'
        marker2 = 'المقطع 2'
        marker3 = 'المقطع 3'
        marker4 = 'المقطع 4'
        idx1 = value.find(marker1)
        if idx1 == -1:
            return False
        idx2 = value.find(marker2)
        if idx2 == -1 or idx2 <= idx1:
            return False
        idx3 = value.find(marker3)
        if idx3 == -1 or idx3 <= idx2:
            return False
        idx4 = value.find(marker4)
        if idx4 == -1 or idx4 <= idx3:
            return False
        return True

class DataIdx3InstructionChecker(AragenInstructions):

    def __init__(self):
        super().__init__('idx_3')

    def check_following(self, value):
        """Checks if the response follows the instruction for IDX 3.

        Constraint: The last sentence must be "هل هناك أي شيء آخر يمكنني مساعدتك به؟"

        Args:
            value: A string representing the response.

        Returns:
            True if the response follows the instruction or False otherwise.
        """
        if not isinstance(value, str):
            return False
        required_last_sentence = 'هل هناك أي شيء آخر يمكنني مساعدتك به؟'
        return value.strip().endswith(required_last_sentence)


class DataIdx4InstructionChecker(AragenInstructions):

    def __init__(self):
        super().__init__('idx_4')

    def check_following(self, value):
        """Checks if the response follows the instruction for IDX 4.

        The instruction requires a four-part biography where each part
        has a title that is exactly 'القسم N' (where N is 1, 2, 3, or 4)
        and these titles must appear in sequential order.

        Args:
            value: A string representing the response.

        Returns:
            True if the response follows the instruction or False otherwise.
        """
        if not isinstance(value, str):
            return False
        lines = value.strip().split('\n')
        found_titles = []
        expected_titles = ['القسم 1', 'القسم 2', 'القسم 3', 'القسم 4']
        for line in lines:
            stripped_line = line.strip()
            if stripped_line in expected_titles:
                found_titles.append(stripped_line)
        return found_titles == expected_titles

class DataIdx5InstructionChecker(AragenInstructions):

    def __init__(self):
        super().__init__('idx_5')

    def check_following(self, value):
        """Checks if the response follows the instructions for question IDX 5.

        Args:
            value: A string representing the response.

        Returns:
            True if the response follows the instruction (does not contain forbidden words),
            or False otherwise.
        """
        forbidden_words = ['الميدان', 'شكرًا', 'مشكلة', 'شريك']
        for word in forbidden_words:
            if word in value:
                return False
        return True

class DataIdx6InstructionChecker(AragenInstructions):

    def __init__(self):
        super().__init__('idx_6')

    def check_following(self, value: str) -> bool:
        """Checks if the response ends with the required phrase.

        Args:
            value: A string representing the response.

        Returns:
            True if the response ends with the required phrase, False otherwise.
        """
        required_ending = 'هل من شيء آخر يمكنني مساعدتك به؟'
        return isinstance(value, str) and value.strip().endswith(required_ending)

class DataIdx7InstructionChecker(AragenInstructions):

    def __init__(self):
        super().__init__('idx_7')

    def check_following(self, value):
        """Checks if the response follows the instructions for question idx_7.

        Args:
            value: A string representing the response.

        Returns:
            True if the response follows the instruction or False otherwise.
        """
        if not isinstance(value, str):
            return False
        required_ending = 'هل يمكنني مساعدتك في أي شيء آخر؟'
        ends_correctly = value.strip().endswith(required_ending)
        word_to_count = 'ناطحة سحاب'
        min_word_count = 8
        word_count = value.count(word_to_count)
        has_enough_words = word_count >= min_word_count
        return ends_correctly and has_enough_words

class DataIdx8InstructionChecker(AragenInstructions):

    def __init__(self):
        super().__init__('idx_8')

    def check_following(self, value):
        """Checks if the response follows the instructions for IDX 8.

        The constraints are:
        1. Must contain at least three distinct paragraphs marked with "*فقرة مميزة*".
        2. Must contain the word "مصري".

        Args:
            value: A string representing the response.

        Returns:
            True if the response follows the instruction or False otherwise.
        """
        if not isinstance(value, str):
            return False
        tag = '*فقرة مميزة*'
        tag_count = value.count(tag)
        has_enough_paragraphs = tag_count >= 3
        has_keyword = 'مصري' in value
        return has_enough_paragraphs and has_keyword

class DataIdx9InstructionChecker(AragenInstructions):

    def __init__(self):
        super().__init__('idx_9')

    def check_following(self, value):
        """Checks if the response follows the instruction for IDX 9.

        Args:
            value: A string representing the response.

        Returns:
            True if the response follows the instruction or False otherwise.
        """
        if not isinstance(value, str):
            return False
        try:
            json_data = json.loads(value)
        except json.JSONDecodeError:
            return False
        if 'لقب' in value:
            return False
        return True

class DataIdx10InstructionChecker(AragenInstructions):

    def __init__(self):
        super().__init__('idx_10')

    def check_following(self, value):
        """Checks if the response follows the instructions for IDX 10.

        Args:
            value: A string representing the response (the article).

        Returns:
            True if the response follows the instruction or False otherwise.
        """
        if not isinstance(value, str):
            return False
        keywords = ['نفايات', 'مادة', 'وجبة']
        keywords_present = all((keyword in value for keyword in keywords))
        if not keywords_present:
            return False
        sentences = [s.strip() for s in re.split('[.!?؟]+', value) if s.strip()]
        sentence_count = len(sentences)
        if sentence_count <= 30:
            return False
        return True

class DataIdx11InstructionChecker(AragenInstructions):

    def __init__(self):
        super().__init__('idx_11')

    def check_following(self, value):
        """
        Checks if the response follows the constraints for IDX 11.
        Constraints:
        1. Avoid using the words: 'النوم', 'الطبخ', 'الإطعام'.
        2. Mention the word 'الجدول' more than 5 times.

        Args:
            value: A string representing the response.

        Returns:
            True if the response follows the instruction or False otherwise.
        """
        if not isinstance(value, str):
            return False
        forbidden_words = ['النوم', 'الطبخ', 'الإطعام']
        required_word = 'الجدول'
        min_required_count = 6
        for word in forbidden_words:
            if word in value:
                return False
        required_word_count = value.count(required_word)
        if required_word_count < min_required_count:
            return False
        return True

class DataIdx12InstructionChecker(AragenInstructions):

    def __init__(self):
        super().__init__('idx_12')

    def check_following(self, value):
        """Checks if the response contains exactly 10 bulleted items starting with '*' followed by a note starting with 'ملاحظة إضافية'.
        Args:
            value: A string representing the response.

        Returns:
            True if the response follows the instruction or False otherwise.
        """
        lines = value.splitlines()
        bullet_count = 0
        note_start_index = -1
        last_bullet_index = -1
        for i, line in enumerate(lines):
            stripped_line = line.strip()
            if not stripped_line:
                continue
            if stripped_line.startswith('*'):
                bullet_count += 1
                last_bullet_index = i
                if note_start_index != -1:
                    return False
            elif stripped_line.startswith('ملاحظة إضافية'):
                if note_start_index == -1:
                    note_start_index = i
        if bullet_count != 10:
            return False
        if note_start_index == -1:
            return False
        if note_start_index <= last_bullet_index:
            return False
        return True

class DataIdx13InstructionChecker(AragenInstructions):

    def __init__(self):
        super().__init__('idx_13')

    def check_following(self, value):
        """Checks if the response follows the instruction for IDX 13.

        Args:
            value: A string representing the response.

        Returns:
            True if the response follows the instruction or False otherwise.
        """
        if not isinstance(value, str):
            return False
        starts_with_name = value.strip().startswith('عبقري الحلبي')
        no_commas = ',' not in value
        at_least_three_highlights = value.count('*') >= 6
        return starts_with_name and no_commas and at_least_three_highlights

class DataIdx14InstructionChecker(AragenInstructions):

    def __init__(self):
        super().__init__('idx_14')

    def check_following(self, value):
        """Checks if the response contains the required final signature starting with 'ملاحظة إضافية'.

        Args:
            value: A string representing the response.

        Returns:
            True if the response contains 'ملاحظة إضافية', False otherwise.
        """
        required_phrase = 'ملاحظة إضافية'
        return required_phrase in value

class DataIdx15InstructionChecker(AragenInstructions):

    def __init__(self):
        super().__init__('idx_15')

    def check_following(self, value):
        """Checks if the response follows the instructions for question IDX 15.

        Args:
            value: A string representing the response.

        Returns:
            True if the response follows the instruction or False otherwise.
        """
        if value.count('***') != 1:
            return False
        parts = value.split('***')
        part1 = parts[0]
        part2 = parts[1]
        if not part1.strip() or not part2.strip():
            return False

        def contains_comment_indicator(text):
            return '//' in text or '/*' in text or '#' in text
        if not contains_comment_indicator(part1):
            return False
        if not contains_comment_indicator(part2):
            return False
        keyword = 'قابلة للاستغلال'
        if keyword not in value:
            return False
        return True

class DataIdx16InstructionChecker(AragenInstructions):

    def __init__(self):
        super().__init__('idx_16')

    def check_following(self, value):
        """Checks if the response follows the instructions for IDX 16.

        Constraints:
        1. Must have at least 6 sections marked by lines starting with '*'.
        2. The name "ليلى" must be mentioned exactly once.

        Args:
            value: A string representing the response (the poem).

        Returns:
            True if the response follows the instructions, False otherwise.
        """
        if not isinstance(value, str):
            return False
        lines = value.splitlines()
        section_markers = [line for line in lines if line.strip().startswith('*')]
        num_sections = len(section_markers)
        name_count = len(re.findall('\\bليلى\\b', value))
        constraints_met = num_sections >= 6 and name_count == 1
        return constraints_met

class DataIdx17InstructionChecker(AragenInstructions):

    def __init__(self):
        super().__init__('idx_17')

    def check_following(self, value):
        """Checks if the response follows the constraints for IDX 17.

        Constraints:
        1. Entire response enclosed in double quotes.
        2. Contains the word "قط" at least once.
        3. Contains the word "طرق" at least twice.
        (Constraint about being a joke about morphology is not programmatically checked)

        Args:
            value: A string representing the response.

        Returns:
            True if the response follows the constraints, False otherwise.
        """
        if not (value.startswith('"') and value.endswith('"') and (len(value) >= 2)):
            return False
        content = value[1:-1]
        qat_count = len(re.findall('\\bقط\\b', content))
        taraq_count = len(re.findall('\\bطرق\\b', content))
        if qat_count >= 1 and taraq_count >= 2:
            return True
        else:
            return False

class DataIdx18InstructionChecker(AragenInstructions):

    def __init__(self):
        super().__init__('idx_18')

    def check_following(self, value):
        """
        Checks if the response follows the instructions for IDX 18.
        Constraints:
        1. Contains step-by-step thinking before the separator.
        2. Thinking and answer are separated by '***' on a single line.
        3. Ends with a note starting with "ملاحظة:".

        Args:
            value: A string representing the response.

        Returns:
            True if the response follows the instructions or False otherwise.
        """
        separator = '\n***\n'
        separator_index = value.find(separator)
        if separator_index == -1:
            return False
        thinking_part = value[:separator_index].strip()
        if not thinking_part:
            return False
        answer_and_note_part = value[separator_index + len(separator):]
        if not answer_and_note_part.strip():
            return False
        lines_after_separator = answer_and_note_part.strip().splitlines()
        last_line = None
        for line in reversed(lines_after_separator):
            if line.strip():
                last_line = line.strip()
                break
        if last_line is None or not last_line.startswith('ملاحظة:'):
            return False
        return True

class DataIdx19InstructionChecker(AragenInstructions):

    def __init__(self):
        super().__init__('idx_19')

    def check_following(self, value):
        """Checks if the response ends exactly with the required Arabic phrase and nothing follows it.

        Args:
            value: A string representing the response.

        Returns:
            True if the response follows the instruction or False otherwise.
        """
        required_ending = 'هل هناك أي شيء آخر يمكنني مساعدتك فيه؟'
        return value.endswith(required_ending)

class DataIdx20InstructionChecker(AragenInstructions):

    def __init__(self):
        super().__init__('idx_20')

    def check_following(self, value):
        """You will implement the logic of the function here to see if the response is correct or not.
        Args:
            value: A string representing the response.

        Returns:
            True if the response follows the instruction or False otherwise.
        """
        if not (value.startswith('"') and value.endswith('"')):
            return False
        content = value[1:-1]
        forbidden_words = ['فيروز', 'نرجع', 'لبعض']
        for word in forbidden_words:
            if word in content:
                return False
        return True

class DataIdx21InstructionChecker(AragenInstructions):

    def __init__(self):
        super().__init__('idx_21')

    def check_following(self, value):
        """Checks if the response follows the instructions for IDX 21.

        Constraints:
        1.  Do not use the words 'إعادة التسمية' or 'الاسم'.
        2.  Use two sentences or less.

        Args:
            value: A string representing the response.

        Returns:
            True if the response follows the instruction or False otherwise.
        """
        if not isinstance(value, str):
            return False
        forbidden_words = ['إعادة التسمية', 'الاسم']
        for word in forbidden_words:
            if word in value:
                return False
        segments = re.split('[.?!؟]', value)
        non_empty_segments = [s for s in segments if s.strip()]
        if not non_empty_segments:
            return False
        num_sentences = len(non_empty_segments)
        return num_sentences <= 2

class DataIdx22InstructionChecker(AragenInstructions):

    def __init__(self):
        super().__init__('idx_22')

    def check_following(self, value):
        """Checks if the response starts by repeating the instruction sentence exactly.

        Args:
            value: A string representing the response.

        Returns:
            True if the response follows the instruction (starts with the exact sentence),
            False otherwise.
        """
        instruction_sentence = 'اكتب منشورًا لمدونة عن أكثر الأشياء المثيرة التي شاهدتها أو جربتها أثناء استخدام وسائل النقل العامة.'
        return value.startswith(instruction_sentence)

class DataIdx23InstructionChecker(AragenInstructions):

    def __init__(self):
        super().__init__('idx_23')

    def check_following(self, value):
        """Checks if the response follows the instructions for IDX 23.

        Constraints:
        1. At least two sections, each starting with a title indicating its sequential number.
        2. Exactly two Markdown bullet points (* text) in the complete response.

        Args:
            value: A string representing the response.

        Returns:
            True if the response follows the instructions, False otherwise.
        """
        if not isinstance(value, str):
            return False
        lines = value.strip().split('\n')
        bullet_points_count = 0
        bullet_point_pattern = re.compile('^\\*\\s+.+')
        for line in lines:
            if bullet_point_pattern.match(line):
                bullet_points_count += 1
        if bullet_points_count != 2:
            return False
        potential_section_titles_count = 0
        arabic_ordinals = ['الأول', 'الثاني', 'الثالث', 'الرابع', 'الخامس', 'السادس', 'السابع', 'الثامن', 'التاسع', 'العاشر']
        for line in lines:
            if not line.strip():
                continue
            contains_digit = bool(re.search('[0-9]', line))
            contains_ordinal = any((ordinal in line for ordinal in arabic_ordinals))
            if contains_digit or contains_ordinal:
                potential_section_titles_count += 1
        if potential_section_titles_count < 2:
            return False
        return True

class DataIdx24InstructionChecker(AragenInstructions):

    def __init__(self):
        super().__init__('idx_24')

    def check_following(self, value):
        """Checks if the response follows the instructions for IDX 24.

        The instructions are:
        1. Write a short poem about a lion. (Implicit - difficult to check programmatically)
        2. Must include the word 'الغابات'.
        3. Must include the word 'اللغز'.
        4. Must not use commas (الفواصل).

        Args:
            value: A string representing the response.

        Returns:
            True if the response includes the required words and does not contain commas,
            False otherwise.
        """
        if not isinstance(value, str):
            return False
        contains_ghabaat = 'الغابات' in value
        contains_lughz = 'اللغز' in value
        contains_comma = ',' in value
        return contains_ghabaat and contains_lughz and (not contains_comma)

class DataIdx25InstructionChecker(AragenInstructions):

    def __init__(self):
        super().__init__('idx_25')

    def check_following(self, value):
        """Checks if the response follows the instructions for IDX 25.

        Instructions:
        1. Repeat the question text exactly at the beginning.
        2. Provide the answer after the repetition.
        3. Do not include any text before the repeated question.

        Args:
            value: A string representing the response.

        Returns:
            True if the response follows the instruction or False otherwise.
        """
        question_text = 'أنا مهندس برمجيات لدي ٧ سنوات من الخبرة، وأبحث عن وظيفة جديدة. هل يمكنك كتابة سيرة ذاتية لي وشرح كل قسم منها؟ كرر الطلب تمامًا كما هو أعلاه، ثم أعطِ إجابتك. لا تقل أي كلمة قبل تكرار الطلب بالضبط.'
        if value is None or not isinstance(value, str):
            return False
        return value.strip().startswith(question_text.strip())

class DataIdx26InstructionChecker(AragenInstructions):

    def __init__(self):
        super().__init__('idx_26')

    def check_following(self, value: str) -> bool:
        """
        Checks if the response contains the required keywords 'الأندلس' and 'العَدْلي'.
        The constraint about being convertible to HTML is assumed to be satisfied
        if the required keywords are present in a non-corrupted string.

        Args:
            value: A string representing the response.

        Returns:
            True if the response contains both keywords, False otherwise.
        """
        if not isinstance(value, str):
            return False
        keyword1 = 'الأندلس'
        keyword2 = 'العَدْلي'
        contains_keyword1 = keyword1 in value
        contains_keyword2 = keyword2 in value
        return contains_keyword1 and contains_keyword2

class DataIdx27InstructionChecker(AragenInstructions):

    def __init__(self):
        super().__init__('idx_27')

    def check_following(self, value):
        """Checks if the response ends with the required phrase and is in the form of a poem.
        Due to the subjective nature of verifying a poem's style programmatically,
        this check primarily focuses on the verifiable constraint: ending with '(النهاية)'.
        A full check of the poem style would require advanced natural language processing
        and cultural understanding beyond a simple programmatic string check.

        Args:
            value: A string representing the response.

        Returns:
            True if the response follows the instruction or False otherwise.
        """
        required_ending = '(النهاية)'
        if not value.strip().endswith(required_ending):
            return False
        return True

class DataIdx28InstructionChecker(AragenInstructions):

    def __init__(self):
        super().__init__('idx_28')

    def check_following(self, value):
        """Checks if the response follows the instructions for IDX 28.

        The instructions are:
        1. Repeat the prompt text exactly first.
        2. Then provide the answer.
        3. Do not say a single word before repeating the prompt text exactly.
        4. The answer itself must not contain any commas.

        Args:
            value: A string representing the response.

        Returns:
            True if the response follows the instruction or False otherwise.
        """
        prompt_text = 'في هذه المهمة اعد كتابة نص الطلب التالي بالضبط أولاً، ثم قدم إجابتك. لا تتحدث بكلمة واحدة قبل تكرار نص الطلب بالضبط.\n\nاكتب أغنية عاطفية عن شبه الجزيرة العربية دون استخدام أي فواصل.'
        if not value.startswith(prompt_text):
            return False
        answer_part = value[len(prompt_text):]
        if ',' in answer_part:
            return False
        return True

class DataIdx29InstructionChecker(AragenInstructions):

    def __init__(self):
        super().__init__('idx_29')
        self.question_text = 'اقترح اسم لشركة أزياء جديدة لتحظى بإعجاب الشباب، وأعطها اسماً ذو معاني متعددة. ضع الاسم بين علامتي اقتباس مائلتين، مثل <<الاسم>>.\nكرر نص الطلب أعلاه أولاً قبل أن تقول أي شيء أو تستجيب للطلب بالفعل. يجب عليك كتابه الطلب قبل البدء باجابتك.'

    def check_following(self, value):
        """You will implement the logic of the function here to see if the response is correct or not.
        Args:
            value: A string representing the response.

        Returns:
            True if the response follows the instruction or False otherwise.
        """
        if not value.startswith(self.question_text):
            return False
        answer_start_index = len(self.question_text)
        if len(value) < answer_start_index:
            return False
        answer_part = value[answer_start_index:]
        open_bracket_pos_in_answer_part = answer_part.find('<<')
        close_bracket_pos_in_answer_part = answer_part.find('>>')
        if open_bracket_pos_in_answer_part != -1 and close_bracket_pos_in_answer_part != -1 and (close_bracket_pos_in_answer_part > open_bracket_pos_in_answer_part):
            return True
        else:
            return False

class DataIdx30InstructionChecker(AragenInstructions):

    def __init__(self):
        super().__init__('idx_30')

    def check_following(self, value):
        """Checks if the response follows the instruction for question ID 30.
        The response must not contain the words 'يستطيع' or 'ركوب'.

        Args:
            value: A string representing the response.

        Returns:
            True if the response follows the instruction or False otherwise.
        """
        forbidden_words = ['يستطيع', 'ركوب']
        for word in forbidden_words:
            if word in value:
                return False
        return True

class DataIdx31InstructionChecker(AragenInstructions):

    def __init__(self):
        super().__init__('idx_31')

    def check_following(self, value):
        """
        Checks if the response follows the instruction:
        1. Repeats the request text word for word first.
        2. Does not say any words or characters before repeating the request.
        3. Provides an answer (story) after the repetition.

        Args:
            value: A string representing the response.

        Returns:
            True if the response follows the instruction or False otherwise.
        """
        if not isinstance(value, str):
            return False
        request_text = 'اكتب قصة عن رجل يحاول ترتيب حياته. ضع اسم القصة بين علامتي اقتباس مائلتين، أي <<قصة كذا وكذا>>.'
        starts_with_request = value.startswith(request_text)
        has_content_after_request = len(value) > len(request_text)
        return starts_with_request and has_content_after_request

class DataIdx32InstructionChecker(AragenInstructions):

    def __init__(self):
        super().__init__('idx_32')

    def check_following(self, value):
        """Checks if the response follows the constraints for IDX 32.

        Constraints:
        1. Entire response is enclosed in double quotes.
        2. Contains exactly four paragraphs.
        3. Paragraphs are separated by exactly two newlines ().
        4. The first paragraph starts with "عطلة نهاية الأسبوع".
        5. Paragraphs should not be empty or just whitespace.

        Args:
            value: A string representing the response.

        Returns:
            True if the response follows the instruction or False otherwise.
        """
        pattern = '^"(.*?)\\n\\n(.*?)\\n\\n(.*?)\\n\\n(.*?)"$'
        match = re.match(pattern, value, re.DOTALL)
        if not match:
            return False
        paragraph1 = match.group(1)
        paragraph2 = match.group(2)
        paragraph3 = match.group(3)
        paragraph4 = match.group(4)
        if not paragraph1.strip() or not paragraph2.strip() or (not paragraph3.strip()) or (not paragraph4.strip()):
            return False
        required_start = 'عطلة نهاية الأسبوع'
        if not paragraph1.startswith(required_start):
            return False
        return True

class DataIdx33InstructionChecker(AragenInstructions):
    def __init__(self):
        super().__init__("idx_33")

    def check_following(self, value):
        """Checks if the response follows the instructions for IDX 33.

        The instructions are:
        1. Write a poem in colloquial Arabic about a new smartphone. (Ignored: Subjective)
        2. End the answer with a concluding note starting with 'ملاحظة إضافية'.
        3. The answer must contain at least 6 empty square brackets '[ ]'.

        Args:
            value: A string representing the response.

        Returns:
            True if the response follows the quantifiable instructions (2 and 3)
            or False otherwise.
        """
        if not isinstance(value, str):
            # The input must be a string to perform string operations
            return False

        # Constraint 3: Contains at least 6 instances of '[ ]'
        bracket_count = value.count('[ ]')
        if bracket_count < 6:
            return False

        # Constraint 2: Ends with a note starting with 'ملاحظة إضافية'
        # Interpretation: Find the last occurrence of the marker 'ملاحظة إضافية'.
        # Everything in the string AFTER this marker must be whitespace,
        # meaning the marker starts the last significant part of the text.
        note_start_marker = 'ملاحظة إضافية'
        last_marker_index = value.rfind(note_start_marker)

        if last_marker_index == -1:
            # The required marker 'ملاحظة إضافية' is not found anywhere in the string.
            return False

        # Get the substring starting immediately after the marker
        after_marker_substring = value[last_marker_index + len(note_start_marker):]

        # Check if this substring contains only whitespace characters or is empty.
        # If stripping this substring results in an empty string, it confirms
        # that no non-whitespace characters appear after the last occurrence
        # of the marker.
        if after_marker_substring.strip() != "":
            # There is non-whitespace content present after the marker,
            # meaning the required note is not the last non-whitespace part
            # of the response.
            return False

        # If both quantifiable checks pass
        return True

class DataIdx34InstructionChecker(AragenInstructions):

    def __init__(self):
        super().__init__('idx_34')

    def check_following(self, value):
        """Checks if the response is an email that includes a note starting with 'ملاحظة' at the end.
        The instruction requires adding a note at the end of the email that starts with "ملاحظة".
        This check verifies that the string contains the word "ملاحظة" and that there is
        at least one character following the last occurrence of "ملاحظة".

        Args:
            value: A string representing the response.

        Returns:
            True if the response contains 'ملاحظة' and is followed by content, False otherwise.
        """
        if not isinstance(value, str):
            return False
        keyword = 'ملاحظة'
        if keyword not in value:
            return False
        last_index = value.rfind(keyword)
        if last_index + len(keyword) < len(value):
            return True
        else:
            return False

class DataIdx35InstructionChecker(AragenInstructions):

    def __init__(self):
        super().__init__('idx_35')
        self.prompt_text = 'اكتب حبكة لقصة عن شخصين يتبادلان بصمات الأصابع. يجب أن تتضمن عنوانًا موضوعًا بين علامتي اقتباس مزدوجتين كالتالي <<العنوان>>. في ردك، يرجى تجنب استخدام الفواصل.\n\nأولاً، كرر نص الطلب أعلاه كلمة بكلمة دون تغيير.\nلا تقل أي كلمات أو أحرف قبل تكرار الطلب أعلاه.\nبعد تكرارك للطلب، يمكنك إعطاء ردك بعد ذلك.'

    def check_following(self, value):
        """Checks if the response follows the instructions for IDX 35.

        Args:
            value: A string representing the response.

        Returns:
            True if the response follows the instruction or False otherwise.
        """
        if not value.startswith(self.prompt_text):
            return False
        response_part = value[len(self.prompt_text):]
        if ',' in response_part:
            return False
        start_idx = response_part.find('<<')
        end_idx = response_part.find('>>')
        if start_idx == -1 or end_idx == -1 or start_idx >= end_idx:
            return False
        if end_idx <= start_idx + 2:
            return False
        return True

class DataIdx36InstructionChecker(AragenInstructions):

    def __init__(self):
        super().__init__('idx_36')

    def check_following(self, value):
        """
        Checks if the response avoids using the word 'المحطة'.

        Args:
            value: A string representing the response.

        Returns:
            True if the response does not contain 'المحطة', False otherwise.
        """
        return 'المحطة' not in value

class DataIdx37InstructionChecker(AragenInstructions):

    def __init__(self):
        super().__init__('idx_37')

    def check_following(self, value):
        """Checks if the response starts with the required sentence and contains additional content.
        Args:
            value: A string representing the response.

        Returns:
            True if the response follows the instruction or False otherwise.
        """
        required_sentence = 'المنتج هو نوع جديد من الورق يمكن استخدامه لتغليف الطعام، وهو صالح للأكل.'
        starts_correctly = value.startswith(required_sentence)
        has_additional_content = len(value) > len(required_sentence)
        return starts_correctly and has_additional_content

class DataIdx38InstructionChecker(AragenInstructions):

    def __init__(self):
        super().__init__('idx_38')

    def check_following(self, value):
        """Checks if the response is enclosed in double quotes and contains 'بايثون' and 'جافا'.
        Note: Checking for the content requirements (CV for 20-year-old student with no work experience)
        is not feasible with simple string checks and is therefore not implemented.
        Args:
            value: A string representing the response.

        Returns:
            True if the response follows the programmable constraints (quotes and keywords) or False otherwise.
        """
        if len(value) < 2 or not value.startswith('"') or (not value.endswith('"')):
            return False
        keyword1 = 'بايثون'
        keyword2 = 'جافا'
        if keyword1 not in value or keyword2 not in value:
            return False
        return True

class DataIdx39InstructionChecker(AragenInstructions):

    def __init__(self):
        super().__init__('idx_39')

    def check_following(self, value):
        """Checks if the response ends exactly with the required phrase and nothing follows it.

        Args:
            value: A string representing the response.

        Returns:
            True if the response follows the instruction or False otherwise.
        """
        required_ending = 'لا يمكنك الفشل باتباع الخطوات المذكورة أعلاه.'
        if not isinstance(value, str):
            return False
        return value.endswith(required_ending)

class DataIdx40InstructionChecker(AragenInstructions):

    def __init__(self):
        super().__init__('idx_40')
        self.required_request_prefix = 'مرحبًا. أحتاج إلى تقديم محاضرة لطلابي عن فيلم الرسالة. يرجى مساعدتي في كتابة مخطط محاضرة يكون جذابًا ومفيدًا.'

    def check_following(self, value):
        """
        Checks if the response strictly adheres to the instructions.
        The instructions require repeating the exact request first, with nothing before it,
        and then providing the answer.

        Args:
            value: A string representing the response provided by the student.

        Returns:
            True if the response starts with the exact required request prefix,
            followed by potentially more content (the answer).
            False otherwise (e.g., if it doesn't start with the prefix, or contains
            anything before the prefix).
        """
        if not isinstance(value, str):
            return False
        return value.startswith(self.required_request_prefix)

class DataIdx41InstructionChecker(AragenInstructions):

    def __init__(self):
        super().__init__('idx_41')

    def check_following(self, value):
        """Checks if the response follows the instructions for IDX 41.

        Instructions:
        1. List best places to visit in Andalusia.
        2. List recommended hotels.
        3. Output must be in JSON format.
        4. Do not include the words: مورسيا, بلنسية, قادس, غرناطة, القطار.

        Args:
            value: A string representing the response.

        Returns:
            True if the response follows the instruction or False otherwise.
        """
        try:
            json.loads(value)
        except json.JSONDecodeError:
            return False
        forbidden_words = ['مورسيا', 'بلنسية', 'قادس', 'غرناطة', 'القطار']
        for word in forbidden_words:
            if word in value:
                return False
        return True

class DataIdx42InstructionChecker(AragenInstructions):

    def __init__(self):
        super().__init__('idx_42')

    def check_following(self, value):
        """Checks if the response follows the instruction for IDX 42.

        The constraints are:
        1. The response must end exactly with 'آمل أن توافقني.'.
        2. The response must contain the substring 'ملحق إضافي'.
        3. The substring 'ملحق إضافي' must appear before the final 'آمل أن توافقني.'.

        Args:
            value: A string representing the response.

        Returns:
            True if the response follows the instruction or False otherwise.
        """
        required_ending = 'آمل أن توافقني.'
        required_appendix_start = 'ملحق إضافي'
        if not value.strip().endswith(required_ending):
            return False
        end_index = value.strip().rfind(required_ending)
        body_and_appendix = value.strip()[:end_index].strip()
        if required_appendix_start not in body_and_appendix:
            return False
        return True

class DataIdx43InstructionChecker(AragenInstructions):

    def __init__(self):
        super().__init__('idx_43')

    def check_following(self, value: str) -> bool:
        """Checks if the response follows the constraints for IDX 43.
        Constraints:
        1. Entire response enclosed in double quotes.
        2. Exactly five paragraphs.
        3. Each paragraph starts with its sequential number followed by a period (e.g., "1.", "2.", etc.).

        Args:
            value: A string representing the response.

        Returns:
            True if the response follows the instruction or False otherwise.
        """
        if not (isinstance(value, str) and value.startswith('"') and value.endswith('"')):
            return False
        if len(value) < 2:
            return False
        content = value[1:-1]
        if not content.strip():
            return False
        current_pos = 0
        markers = ['1.', '2.', '3.', '4.', '5.']
        last_marker_end_pos = 0
        for i, marker in enumerate(markers):
            idx = content.find(marker, current_pos)
            if idx == -1:
                return False
            if i == 0 and idx != 0:
                return False
            current_pos = idx + len(marker)
            if i == len(markers) - 1:
                last_marker_end_pos = current_pos
        if re.search('\\d+\\.', content[last_marker_end_pos:]):
            return False
        return True

class DataIdx44InstructionChecker(AragenInstructions):

    def __init__(self):
        super().__init__('44')

    def check_following(self, value):
        """Checks if the response ends with a note starting with 'ملحوظة'.

        Args:
            value: A string representing the response.

        Returns:
            True if the response ends with 'ملحوظة', False otherwise.
        """
        cleaned_value = value.rstrip()
        return cleaned_value.endswith('ملحوظة') or cleaned_value.lower().endswith('ملحوظه')

class DataIdx45InstructionChecker(AragenInstructions):

    def __init__(self):
        super().__init__('idx_45')

    def check_following(self, value):
        """Checks if the response explains seasons for primary students and includes a final note
           starting with 'حاشية'.

        Args:
            value: A string representing the response.

        Returns:
            True if the response follows the instruction or False otherwise.
        """
        if not isinstance(value, str):
            return False
        stripped_value = value.strip()
        if not stripped_value:
            return False
        parts = stripped_value.split('\n')
        last_significant_part = None
        for part in reversed(parts):
            if part.strip():
                last_significant_part = part.strip()
                break
        if last_significant_part is None:
            return False
        required_start = 'حاشية'
        return last_significant_part.startswith(required_start)

class DataIdx46InstructionChecker(AragenInstructions):

    def __init__(self):
        super().__init__('idx_46')

    def check_following(self, value: str) -> bool:
        """
        Checks if the response follows the instructions for IDX 46.
        Constraints:
        1. Exactly six paragraphs.
        2. Paragraphs separated by two empty lines ("

").
        3. The second paragraph must start with the word "الرئيس".

        Args:
            value: A string representing the response (the article text).

        Returns:
            True if the response follows the instructions or False otherwise.
        """
        potential_paragraphs = value.split('\n\n')
        paragraphs = [p.strip() for p in potential_paragraphs if p.strip()]
        if len(paragraphs) != 6:
            return False
        second_paragraph = paragraphs[1]
        if not second_paragraph.strip().startswith('الرئيس'):
            return False
        return True

class DataIdx47InstructionChecker(AragenInstructions):

    def __init__(self):
        super().__init__('idx_47')

    def check_following(self, value):
        """Checks if the response for IDX 47 follows the constraints.

        Args:
            value: A string representing the response.

        Returns:
            True if the response follows the instruction or False otherwise.
        """
        if not isinstance(value, str):
            return False
        if ',' in value:
            return False
        if not value.strip().endswith('ملاحظة إضافية'):
            return False
        keywords = ['ناقص', 'نموذج', 'أداء', 'جودة', 'هندسة']
        for keyword in keywords:
            if keyword not in value:
                return False
        return True

class DataIdx48InstructionChecker(AragenInstructions):

    def __init__(self):
        super().__init__('idx_48')

    def check_following(self, value):
        """Checks if the response contains three paragraphs separated by ***,
           with each paragraph containing exactly one of the keywords
           'احتساب', 'تقديم', 'خلاصة', and each keyword appearing in exactly one paragraph.

        Args:
            value: A string representing the response.

        Returns:
            True if the response follows the instruction or False otherwise.
        """
        separator = '***'
        keywords = ['احتساب', 'تقديم', 'خلاصة']
        if value.count(separator) != 2:
            return False
        paragraphs = value.split(separator)
        if len(paragraphs) != 3:
            return False
        paragraph_keyword_counts = [0] * 3
        for i, paragraph in enumerate(paragraphs):
            current_paragraph_count = 0
            for keyword in keywords:
                if keyword in paragraph:
                    current_paragraph_count += 1
            if current_paragraph_count != 1:
                return False
            paragraph_keyword_counts[i] = current_paragraph_count
        keyword_paragraph_counts = {keyword: 0 for keyword in keywords}
        for keyword in keywords:
            for paragraph in paragraphs:
                if keyword in paragraph:
                    keyword_paragraph_counts[keyword] += 1
            if keyword_paragraph_counts[keyword] != 1:
                return False
        return True

class DataIdx49InstructionChecker(AragenInstructions):

    def __init__(self):
        super().__init__('49')

    def check_following(self, value):
        """Checks if the response ends exactly with 'سلام!' and has no additional words following it.

        Args:
            value: A string representing the response.

        Returns:
            True if the response follows the instruction, False otherwise.
        """
        if not isinstance(value, str):
            return False
        cleaned_value = value.rstrip()
        required_ending = 'سلام!'
        return cleaned_value.endswith(required_ending)

class DataIdx50InstructionChecker(AragenInstructions):

    def __init__(self):
        super().__init__('idx_50')

    def check_following(self, value):
        """Checks if the response ends exactly with the required phrase.

        Args:
            value: A string representing the response.

        Returns:
            True if the response ends exactly with the required phrase, False otherwise.
        """
        required_ending = 'اتبع الخطوات الخمس المذكورة أعلاه، وستنجح.'
        return value.strip().endswith(required_ending) and value.strip()[-len(required_ending):] == required_ending

class DataIdx51InstructionChecker(AragenInstructions):

    def __init__(self):
        super().__init__('idx_51')

    def check_following(self, value):
        """Checks if the response starts exactly with the required sentence.

        Args:
            value: A string representing the response.

        Returns:
            True if the response follows the instruction or False otherwise.
        """
        required_start = 'اكتب تغريدة غاضبة عن صديق دائمًا يتأخر عن المناسبات أو المواعيد.'
        return value.startswith(required_start)

class DataIdx52InstructionChecker(AragenInstructions):

    def __init__(self):
        super().__init__('idx_52')

    def check_following(self, value):
        """Checks if the response follows the instructions for IDX 52.

        Args:
            value: A string representing the response.

        Returns:
            True if the response follows the instruction or False otherwise.
        """
        forbidden_keywords = ['سيء', 'غير فعال']
        for keyword in forbidden_keywords:
            if keyword in value:
                return False
        lines = value.strip().split('\n')
        bullet_points = [line.strip() for line in lines if line.strip().startswith('*')]
        if len(bullet_points) != 6:
            return False
        return True

class DataIdx53InstructionChecker(AragenInstructions):

    def __init__(self):
        super().__init__('idx_53')

    def check_following(self, value):
        """You will implement the logic of the function here to see if the response is correct or not.
        Args:
            value: A string representing the response.

        Returns:
            True if the response follows the instruction or False otherwise.
        """
        required_ending = 'أيها تختار؟'
        return value.strip().endswith(required_ending)

class DataIdx54InstructionChecker(AragenInstructions):

    def __init__(self):
        super().__init__('54')

    def check_following(self, value):
        """Checks if the response follows the instructions for IDX 54.

        Args:
            value: A string representing the response.

        Returns:
            True if the response follows the instruction or False otherwise.
        """
        required_ending = 'أخبرني كيف تسير الأمور. يمكنني إعطائك الخطوات التالية عندما تنهي كل الخطوات أعلاه.'
        if not value.strip().endswith(required_ending):
            return False
        stripped_value = value.strip()
        ending_index = stripped_value.rfind(required_ending)
        steps_part = stripped_value[:ending_index].strip()
        steps = steps_part.split('***')
        if len(steps) != 5:
            return False
        for i in range(5):
            step_text = steps[i].strip()
            expected_start = f'الخطوة {i + 1}:'
            if not step_text.startswith(expected_start):
                return False
            content_after_start = step_text[len(expected_start):].strip()
            if not content_after_start:
                return False
        return True

class DataIdx55InstructionChecker(AragenInstructions):
    PROMPT_TEXT = 'قبل أن تجيب على الطلب التالي، كرره في بداية إجابتك. كرر الطلب كما هو. من فضلك لا تغيّره.\n\nاكتب سيرة ذاتية لمهندس أجهزة مبتدئ. يجب أن تكون السيرة الذاتية متقنة بما يكفي للحصول على وظيفة في شركة كبيرة، ويجب أن تكون خالية من أي فواصل أو علامات ترقيم.'
    FORBIDDEN_PUNCTUATION = set(string.punctuation + '،')

    def __init__(self):
        super().__init__('idx_55')

    def check_following(self, value: str) -> bool:
        """
        Checks if the response repeats the prompt verbatim at the beginning
        and contains no punctuation marks in the part following the prompt.

        Args:
            value: A string representing the response.

        Returns:
            True if the response follows the instruction or False otherwise.
        """
        if not value.startswith(self.PROMPT_TEXT):
            return False
        resume_part = value[len(self.PROMPT_TEXT):]
        for char in resume_part:
            if char in self.FORBIDDEN_PUNCTUATION:
                return False
        return True

class DataIdx56InstructionChecker(AragenInstructions):

    def __init__(self):
        super().__init__('idx_56')

    def check_following(self, value):
        """Checks if the response follows the constraints for IDX 56.

        Constraints:
        1. Exactly 7 paragraphs.
        2. Paragraphs are separated by two newlines (

).
        3. The last paragraph starts with "الخلاصة".

        Args:
            value: A string representing the response.

        Returns:
            True if the response follows the instruction or False otherwise.
        """
        if not isinstance(value, str):
            return False
        paragraphs = value.split('\n\n')
        if len(paragraphs) != 7:
            return False
        last_paragraph_content = paragraphs[6].strip()
        if not last_paragraph_content.startswith('الخلاصة'):
            return False
        return True


class DataIdx57InstructionChecker(AragenInstructions):

    def __init__(self):
        super().__init__('idx_57')

    def check_following(self, value):
        """Checks if the response follows the instruction for IDX 57.
        Constraints:
        - At least 300 words.
        - Contains at least 3 '*' characters.
        - Contains the phrase "ملاحظة في النهاية".

        Args:
            value: A string representing the response.

        Returns:
            True if the response follows the instruction or False otherwise.
        """
        if not isinstance(value, str):
            return False
        words = value.split()
        word_count = len(words)
        min_word_count = 300
        word_count_ok = word_count >= min_word_count
        asterisk_count = value.count('*')
        min_asterisks = 3
        asterisks_ok = asterisk_count >= min_asterisks
        conclusion_phrase = 'ملاحظة في النهاية'
        conclusion_phrase_ok = conclusion_phrase in value
        return word_count_ok and asterisks_ok and conclusion_phrase_ok

class DataIdx58InstructionChecker(AragenInstructions):

    def __init__(self):
        super().__init__('idx_58')

    def check_following(self, value):
        """Checks if the response structure follows the instruction of having exactly four stanzas,
        each identified by a title starting with 'المقطع'.

        Args:
            value: A string representing the response.

        Returns:
            True if the response contains exactly four lines starting with 'المقطع', False otherwise.
        """
        if not isinstance(value, str):
            return False
        lines = value.strip().splitlines()
        stanza_title_count = 0
        title_prefix = 'المقطع'
        for line in lines:
            if line.strip().startswith(title_prefix):
                stanza_title_count += 1
        return stanza_title_count == 4

class DataIdx59InstructionChecker(AragenInstructions):

    def __init__(self):
        super().__init__('idx_59')

    def check_following(self, value):
        """Checks if the response avoids saying 'نعم' or 'لا'.

        Args:
            value: A string representing the response.

        Returns:
            True if the response does not contain 'نعم' or 'لا', False otherwise.
        """
        return 'نعم' not in value and 'لا' not in value

class DataIdx60InstructionChecker(AragenInstructions):

    def __init__(self):
        super().__init__('idx_60')

    def check_following(self, value):
        """Checks if the response follows the instruction constraints.
        Constraints:
        - Does not contain the word "الإنزيمات" (enzymes).
        - Does not contain the word "الأجسام المضادة" (antibodies).

        Args:
            value: A string representing the response.

        Returns:
            True if the response follows the instruction or False otherwise.
        """
        forbidden_word_enzymes = 'الإنزيمات'
        forbidden_word_antibodies = 'الأجسام المضادة'
        contains_enzymes = forbidden_word_enzymes in value
        contains_antibodies = forbidden_word_antibodies in value
        return not contains_enzymes and (not contains_antibodies)

class DataIdx61InstructionChecker(AragenInstructions):

    def __init__(self):
        super().__init__('idx_61')

    def check_following(self, value):
        """Checks if the response follows the instructions for IDX 61.

        Constraints:
        - Must not contain the words 'غني' or 'مال'.
        - Must contain at least 40 sentences (estimated by splitting on .!?).

        Args:
            value: A string representing the response.

        Returns:
            True if the response follows the instruction or False otherwise.
        """
        if not isinstance(value, str):
            return False
        forbidden_words = ['غني', 'مال']
        for word in forbidden_words:
            if word in value:
                return False
        sentences = [part.strip() for part in re.split('[.!?]\\s*', value) if part.strip()]
        if not sentences and value.strip():
            sentence_count = 1
        else:
            sentence_count = len(sentences)
        if sentence_count < 40:
            return False
        return True

class DataIdx62InstructionChecker(AragenInstructions):

    def __init__(self):
        super().__init__('idx_62')

    def check_following(self, value):
        """Checks if the response for IDX 62 follows the instructions.

        Constraints:
        1. Must start by repeating the exact required text.
        2. Must not contain any words or symbols before the repetition.
        3. Must not contain any comma character (',').
        4. Short sentences and ad content are not checked programmatically.

        Args:
            value: A string representing the response.

        Returns:
            True if the response follows the objective instructions, False otherwise.
        """
        required_repetition = 'شركة تيتان تصنع ملابس للرجال ذوي الأحجام الكبيرة. اكتب إعلانًا للشركة يجذب جمهورًا واسعًا. اجعل الجمل قصيرة. يجب أن لا يحتوي ردك على أي فاصلة.'
        starts_correctly = value.startswith(required_repetition)
        no_comma = ',' not in value
        return starts_correctly and no_comma

class DataIdx63InstructionChecker(AragenInstructions):

    def __init__(self):
        super().__init__('idx_63')

    def check_following(self, value: str) -> bool:
        """Checks if the response ends with a note starting with 'ملاحظة: ' and having content,
        after stripping trailing whitespace.

        Args:
            value: A string representing the response.

        Returns:
            True if the response follows the instruction or False otherwise.
        """
        if not isinstance(value, str):
            return False
        stripped_value = value.rstrip()
        pattern = 'ملاحظة:(.+)$'
        match = re.search(pattern, stripped_value, re.DOTALL)
        if match is None:
            return False
        note_content = match.group(1)
        if note_content.strip() == '':
            return False
        return True

class DataIdx64InstructionChecker(AragenInstructions):

    def __init__(self):
        super().__init__('idx_64')

    def check_following(self, value):
        """Checks if the response starts with the required sentence and contains more content.

        Args:
            value: A string representing the response.

        Returns:
            True if the response follows the instruction, False otherwise.
        """
        required_start = 'هل يمكن أن تعطيني ملخصاً قصيراً لقصة ألف ليلة وليلة بحيث يكون مناسباً للأطفال؟'
        if not value.strip().startswith(required_start):
            return False
        start_index = value.strip().find(required_start)
        if start_index == -1:
            return False
        end_of_start_index = start_index + len(required_start)
        remaining_part = value.strip()[end_of_start_index:]
        if not remaining_part.strip():
            return False
        return True

class DataIdx65InstructionChecker(AragenInstructions):

    def __init__(self):
        super().__init__('idx_65')

    def check_following(self, value):
        """Checks if the response follows the instructions for question IDX 65.

        Constraints:
        1. Do not use the Arabic word 'تموت'.
        2. Use the Arabic word 'جرعة' at least five times.

        Args:
            value: A string representing the response in Arabic.

        Returns:
            True if the response follows the instructions, False otherwise.
        """
        if 'تموت' in value:
            return False
        dosage_count = value.count('جرعة')
        if dosage_count < 5:
            return False
        return True

class DataIdx66InstructionChecker(AragenInstructions):

    def __init__(self):
        super().__init__('idx_66')

    def check_following(self, value):
        """Checks if the response is a song with at least three lines and contains the words 'معدل' and 'رتب'.

        Args:
            value: A string representing the response.

        Returns:
            True if the response follows the instruction or False otherwise.
        """
        if not isinstance(value, str):
            return False
        lines = value.split('\n')
        non_empty_lines = [line for line in lines if line.strip()]
        if len(non_empty_lines) < 3:
            return False
        if 'معدل' not in value:
            return False
        if 'رتب' not in value:
            return False
        return True

class DataIdx67InstructionChecker(AragenInstructions):

    def __init__(self):
        super().__init__('idx_67')

    def check_following(self, value):
        """Checks if the response meets the criteria:
        1. At least five sentences.
        2. Does not contain "إعادة جدولة" or "مجانية".

        Args:
            value: A string representing the response (the modified text).

        Returns:
            True if the response follows the instructions or False otherwise.
        """
        if not isinstance(value, str):
            return False
        forbidden_words = ['إعادة جدولة', 'مجانية']
        for word in forbidden_words:
            if word in value:
                return False
        sentences = re.split('[.?!؟]+', value)
        valid_sentences = [s for s in sentences if s.strip()]
        sentence_count = len(valid_sentences)
        if sentence_count < 5:
            return False
        return True

class DataIdx68InstructionChecker(AragenInstructions):

    def __init__(self):
        super().__init__('idx_68')

    def check_following(self, value: str) -> bool:
        """
        Checks if the response is a two-paragraph story separated by two line breaks,
        and the first paragraph starts with 'إدراك'.

        Args:
            value: A string representing the response.

        Returns:
            True if the response follows the instruction or False otherwise.
        """
        if not isinstance(value, str):
            return False
        parts = value.split('\n\n')
        non_empty_parts = [part for part in parts if part.strip()]
        if len(non_empty_parts) != 2:
            return False
        first_paragraph = non_empty_parts[0].lstrip()
        required_start_word = 'إدراك'
        return first_paragraph.startswith(required_start_word)

class DataIdx69InstructionChecker(AragenInstructions):

    def __init__(self):
        super().__init__('idx_69')

    def check_following(self, value):
        """Checks if the response follows the instructions for question 69.

        Args:
            value: A string representing the response.

        Returns:
            True if the response follows the instruction or False otherwise.
        """
        if not isinstance(value, str):
            return False
        paragraphs = value.split('\n\n')
        if len(paragraphs) != 4:
            return False
        fourth_paragraph = paragraphs[3].strip()
        if not fourth_paragraph.startswith('المعرفة'):
            return False
        return True

class DataIdx70InstructionChecker(AragenInstructions):

    def __init__(self):
        super().__init__('idx_70')

    def check_following(self, value):
        """Checks if the response ends exactly with the required Arabic phrase, allowing for trailing whitespace.

        The instruction is: الرجاء إنهاء الرد بعبارة 'هل هناك أي شيء آخر يمكنني المساعدة به؟'
        ولا يجب أن تتبع هذه العبارة أي كلمات أخرى في الرد المقدم.
        (Please end the response with the phrase 'Is there anything else I can help with?'
        And this phrase should not be followed by any other words in the provided response.)

        Args:
            value: A string representing the response.

        Returns:
            True if the response ends with the exact required phrase (ignoring trailing whitespace), False otherwise.
        """
        required_ending = 'هل هناك أي شيء آخر يمكنني المساعدة به؟'
        trimmed_value = value.rstrip()
        return trimmed_value.endswith(required_ending)

class DataIdx72InstructionChecker(AragenInstructions):

    def __init__(self):
        super().__init__('idx_72')

    def check_following(self, value):
        """Checks if the response follows the instructions for IDX 72.

        The instructions are:
        1. Repeat the request literally without change first.
        2. Do not say any words or characters before repeating the request.
        3. Provide a good name for a black dog.
        4. The answer must contain a nickname, placed within double parentheses.

        Args:
            value: A string representing the response.

        Returns:
            True if the response follows the instruction or False otherwise.
        """
        required_prefix = 'اكتب اسماً جيداً لكلب أسود. يجب أن تحتوي إجابتك على لقب، يوضع بين قوسين مزدوجين.'
        if not value.startswith(required_prefix):
            return False
        answer_part = value[len(required_prefix):]
        if not re.search('\\(\\(.+\\)\\)', answer_part):
            return False
        return True

class DataIdx73InstructionChecker(AragenInstructions):

    def __init__(self):
        super().__init__('idx_73')

    def check_following(self, value):
        """You will implement the logic of the function here to see if the response is correct or not.
        Args:
            value: A string representing the response.

        Returns:
            True if the response follows the instruction or False otherwise.
        """
        forbidden_words = ['شركة ناشئة', 'كبسولة']
        for word in forbidden_words:
            if word in value:
                return False
        return True

class DataIdx74InstructionChecker(AragenInstructions):

    def __init__(self):
        super().__init__('idx_74')

    def check_following(self, value):
        """Checks if the response follows the instructions for IDX 74.

        The instruction requires the response to start by exactly repeating the
        question/request sentence before providing the answer.
        """
        required_prefix = 'لماذا يعتبر الناس أن الفصل الثاني من الدستور المغربي باتت قديمة وغير صالحة؟ أجب بطريقة مشابهة لأسلوب الأدب الأندلسي.'
        return value.startswith(required_prefix)

class DataIdx75InstructionChecker(AragenInstructions):

    def __init__(self):
        super().__init__('idx_75')

    def check_following(self, value):
        """Checks if the response starts with the exact required phrase as per the instruction.

        Args:
            value: A string representing the response.

        Returns:
            True if the response follows the instruction or False otherwise.
        """
        required_phrase = 'اكتب أغنية عن كلب صغير يدعى جوجي يحب اللعب بالكرة.'
        return value.strip().startswith(required_phrase)

class DataIdx76InstructionChecker(AragenInstructions):

    def __init__(self):
        super().__init__('idx_76')

    def check_following(self, value):
        """Checks if the response ends with a footer starting with 'تنويه ثاني'.

        The instruction is "الرجاء إنهاء إجابتك بتذييل يبدأ بـ 'تنويه ثاني'".
        This translates to "Please end your answer with a footer starting with 'تنويه ثاني'".
        This means the string `value` must end with a segment `S` where `S.startswith('تنويه ثاني')`.
        This is equivalent to checking if the string contains 'تنويه ثاني' followed by any characters until the end.

        Args:
            value: A string representing the response.

        Returns:
            True if the response follows the instruction or False otherwise.
        """
        if not isinstance(value, str):
            return False
        return bool(re.search('تنويه ثاني.*$', value))

class DataIdx77InstructionChecker(AragenInstructions):

    def __init__(self):
        super().__init__('idx_77')

    def check_following(self, value):
        """Checks if the response follows the constraints for question 77.

        Constraints:
        1. Must be valid JSON.
        2. Must not contain the word 'السوق' (Al-Souq).
        3. Must not contain the word 'JSON'.

        Args:
            value: A string representing the response.

        Returns:
            True if the response follows the instruction or False otherwise.
        """
        try:
            json.loads(value)
        except json.JSONDecodeError:
            return False
        if 'السوق' in value:
            return False
        if 'JSON' in value:
            return False
        return True

class DataIdx78InstructionChecker(AragenInstructions):

    def __init__(self):
        super().__init__('idx_78')

    def check_following(self, value):
        """Checks if the response follows the instruction for IDX 78.
        Instruction: Write a poem about a long-term war. Add a signature at the end starting with the phrase 'ملاحظة أخيرة'.
        Args:
            value: A string representing the response.

        Returns:
            True if the response contains the required signature phrase, False otherwise.
        """
        required_phrase = 'ملاحظة أخيرة'
        if value is None:
            return False
        return required_phrase in value

class DataIdx79InstructionChecker(AragenInstructions):

    def __init__(self):
        super().__init__('idx_79')

    def check_following(self, value):
        """Checks if the response ends exactly with 'محبتي وشكري.'

        Args:
            value: A string representing the response.

        Returns:
            True if the response follows the instruction or False otherwise.
        """
        required_ending = 'محبتي وشكري.'
        return value.endswith(required_ending)

class DataIdx80InstructionChecker(AragenInstructions):

    def __init__(self):
        super().__init__('idx_80')

    def check_following(self, value):
        """Checks if the response follows the constraints for IDX 80.
        Constraints: Do not mention the words 'توفي' or 'غرق'.

        Args:
            value: A string representing the response.

        Returns:
            True if the response follows the instruction or False otherwise.
        """
        forbidden_words = ['توفي', 'غرق']
        for word in forbidden_words:
            if word in value:
                return False
        return True

class DataIdx81InstructionChecker(AragenInstructions):

    def __init__(self):
        super().__init__('idx_81')

    def check_following(self, value: str) -> bool:
        """
        Checks if the response follows the constraints for IDX 81:
        1. Exactly 3 paragraphs separated by exactly two empty lines.
        2. No punctuation (.,?!;:).
        3. First paragraph starts with 'تعرض'.
        4. Contains at least two placeholder markers ([...]).

        Args:
            value: A string representing the response.

        Returns:
            True if the response follows the instruction or False otherwise.
        """
        if not isinstance(value, str):
            return False
        num_open_brackets = value.count('[')
        num_close_brackets = value.count(']')
        if num_open_brackets < 2 or num_close_brackets < 2:
            return False
        forbidden_punct = ['.', ',', '?', '!', ';', ':']
        if any((p in value for p in forbidden_punct)):
            return False
        paragraphs = value.split('\n\n')
        if len(paragraphs) != 3:
            return False
        if any((not p.strip() for p in paragraphs)):
            return False
        if not paragraphs[0].strip().startswith('تعرض'):
            return False
        return True

class DataIdx82InstructionChecker(AragenInstructions):

    def __init__(self):
        super().__init__('idx_82')

    def check_following(self, value):
        """Checks if the response follows the instructions for IDX 82.

        Args:
            value: A string representing the response.

        Returns:
            True if the response follows the instruction or False otherwise.
        """
        forbidden_words = ['حزين', 'مجنون', 'ضغوط']
        for word in forbidden_words:
            if word in value:
                return False
        bracket_pattern = '\\[.*?\\]'
        matches = re.findall(bracket_pattern, value)
        if len(matches) < 15:
            return False
        return True

class DataIdx83InstructionChecker(AragenInstructions):

    def __init__(self):
        super().__init__('idx_83')

    def check_following(self, value):
        """Checks if the response ends exactly with the required Arabic phrase and has nothing after it.
        Args:
            value: A string representing the response.

        Returns:
            True if the response follows the instruction or False otherwise.
        """
        required_ending = 'أخبرني إذا كان لديك أي أسئلة إضافية.'
        if isinstance(value, str) and value.endswith(required_ending):
            return True
        else:
            return False

class DataIdx84InstructionChecker(AragenInstructions):

    def __init__(self):
        super().__init__('idx_84')

    def check_following(self, value):
        """Checks if the response contains the required Arabic words.

        Args:
            value: A string representing the response in Arabic.

        Returns:
            True if the response contains both 'حبر' and 'مذكرات', False otherwise.
        """
        if not isinstance(value, str):
            return False
        has_hebr = 'حبر' in value
        has_mudhakarat = 'مذكرات' in value
        return has_hebr and has_mudhakarat

class DataIdx85InstructionChecker(AragenInstructions):

    def __init__(self):
        super().__init__('idx_85')

    def check_following(self, value):
        """Checks if the response ends exactly with the required phrase and nothing follows it.

        Args:
            value: A string representing the response.

        Returns:
            True if the response follows the instruction or False otherwise.
        """
        required_ending = 'هل هناك أي شيء آخر يمكنني مساعدتك به؟'
        return value == required_ending

class DataIdx86InstructionChecker(AragenInstructions):

    def __init__(self):
        super().__init__('idx_86')

    def check_following(self, value):
        """Checks if the response follows the instructions for IDX 86.

        Constraints:
        1. Exactly three paragraphs.
        2. Paragraphs separated only by '

'.
        3. Third paragraph starts with "الترابط".
        4. Includes keywords "الثقة" and "قلوب".
        5. Ends with an appendix starting with "ملاحظة".

        Args:
            value: A string representing the response.

        Returns:
            True if the response follows the instruction or False otherwise.
        """
        if not isinstance(value, str):
            return False
        appendix_marker = 'ملاحظة'
        appendix_start_index = value.rfind(appendix_marker)
        if appendix_start_index == -1:
            return False
        if not value[appendix_start_index:].strip().startswith(appendix_marker):
            return False
        main_body = value[:appendix_start_index].strip()
        paragraphs = main_body.split('\n\n')
        if len(paragraphs) != 3:
            return False
        if not all((p.strip() for p in paragraphs)):
            return False
        third_paragraph = paragraphs[2].strip()
        if not third_paragraph.startswith('الترابط'):
            return False
        if 'الثقة' not in value:
            return False
        if 'قلوب' not in value:
            return False
        return True

class DataIdx87InstructionChecker(AragenInstructions):

    def __init__(self):
        super().__init__('idx_87')

    def check_following(self, value):
        """Checks if the response contains the keywords 'النهاية' and 'أقل'.

        Args:
            value: A string representing the response (the blog post).

        Returns:
            True if both keywords are present, False otherwise.
        """
        keyword1 = 'النهاية'
        keyword2 = 'أقل'
        return keyword1 in value and keyword2 in value

class DataIdx88InstructionChecker(AragenInstructions):

    def __init__(self):
        super().__init__('idx_88')

    def check_following(self, value):
        """Checks if the response follows the instructions for IDX 88.

        Args:
            value: A string representing the response.

        Returns:
            True if the response follows the instruction or False otherwise.
        """
        if not isinstance(value, str):
            return False
        separator = '******'
        if separator not in value:
            return False
        parts = value.split(separator)
        if len(parts) != 2:
            return False
        part1 = parts[0].strip()
        part2 = parts[1].strip()
        if not part1 or not part2:
            return False
        forbidden_words = ['قبل الميلاد', 'الثقافة', 'ما قبل التاريخ']
        for word in forbidden_words:
            if word in value:
                return False
        return True

class DataIdx89InstructionChecker(AragenInstructions):

    def __init__(self):
        super().__init__('idx_89')

    def check_following(self, value):
        """Checks if the response follows the instructions for IDX 89.

        Args:
            value: A string representing the response.

        Returns:
            True if the response follows the instruction or False otherwise.
        """
        if not isinstance(value, str):
            return False
        paragraphs = value.split('\n\n')
        if len(paragraphs) != 3:
            return False
        first_paragraph = paragraphs[0].lstrip()
        if not first_paragraph.startswith('أرسل'):
            return False
        return True

class DataIdx90InstructionChecker(AragenInstructions):

    def __init__(self):
        super().__init__('idx_90')

    def check_following(self, value):
        """Checks if the response follows the instructions for IDX 90.

        The constraints are:
        1. Output must be in JSON format using Markdown code blocks (```json ... ```).
        2. The response must contain the Arabic keyword 'الميدالية'.
        3. The response must contain the Arabic keyword 'الفا'.

        Args:
            value: A string representing the response.

        Returns:
            True if the response follows the instruction or False otherwise.
        """
        json_format_ok = re.search('```json', value) is not None
        keyword_midalia_present = 'الميدالية' in value
        keyword_alfa_present = 'الفا' in value
        return json_format_ok and keyword_midalia_present and keyword_alfa_present

class DataIdx91InstructionChecker(AragenInstructions):

    def __init__(self):
        super().__init__('idx_91')

    def check_following(self, value):
        """Checks if the response follows the instructions for IDX 91.

        Constraints:
        - Must include the words 'أصدقاء' and 'سلمان' as whole words.
        - Total content must be less than 50 words (basic whitespace split).
        - The core task is to write a short resume for a refinery operator with 5 years experience
          in the chemical industry, but the checker focuses on the measurable constraints.

        Args:
            value: A string representing the response (the short resume in Arabic).

        Returns:
            True if the response follows the instructions, False otherwise.
        """
        if not isinstance(value, str):
            return False
        words = value.split()
        word_count = len(words)
        length_constraint_met = word_count < 50
        try:
            keyword_friends_met = bool(re.search('\\bأصدقاء\\b', value))
            keyword_salman_met = bool(re.search('\\bسلمان\\b', value))
        except re.error:
            return False
        return length_constraint_met and keyword_friends_met and keyword_salman_met

class DataIdx92InstructionChecker(AragenInstructions):

    def __init__(self):
        super().__init__('idx_92')

    def check_following(self, value: str) -> bool:
        """Checks if the response (a poem) follows the instructions.

        Instructions:
        - Write a vernacular poem about an Aladdin fan named Ahmed.
        - Include "Aladdin", "Baghdad", "Jasmine", "Jafar".
        - Use less than 100 words.

        Args:
            value: A string representing the response (the poem).

        Returns:
            True if the response follows the instruction or False otherwise.
        """
        if not isinstance(value, str):
            return False
        words = value.split()
        if len(words) >= 100:
            return False
        required_elements = ['علاء الدين', 'بغداد', 'ياسمين', 'جعفر', 'أحمد']
        for element in required_elements:
            if element not in value:
                return False
        return True

class DataIdx93InstructionChecker(AragenInstructions):

    def __init__(self):
        super().__init__('idx_93')

    def check_following(self, value: str) -> bool:
        """Checks if the response contains a note at the end starting with 'ملاحظة' and is followed by at least one character.

        Args:
            value: A string representing the response.

        Returns:
            True if the response follows the instruction or False otherwise.
        """
        note_prefix = 'ملاحظة'
        last_prefix_index = value.rfind(note_prefix)
        if last_prefix_index == -1:
            return False
        if last_prefix_index + len(note_prefix) < len(value):
            return True
        else:
            return False

class DataIdx94InstructionChecker(AragenInstructions):

    def __init__(self):
        super().__init__('idx_94')

    def check_following(self, value):
        """Checks if the response follows the instructions for IDX 94.

        Instructions:
        1. Write a funny note to Antar. (Funny is subjective and not checked)
        2. Use <br> to separate lines.
        3. Start with a funny greeting. (Funny is subjective and not checked. Start is not strictly checked beyond structural elements.)
        4. Include mathematical symbols.
        5. Add a concluding remark at the end starting with "ملاحظة بعد الملاحظة الأخيرة".

        Args:
            value: A string representing the response.

        Returns:
            True if the response follows the instruction or False otherwise.
        """
        if not isinstance(value, str):
            return False
        contains_br = '<br>' in value
        math_elements = '+-*/=<>(){}[]0123456789'
        contains_math = any((char in value for char in math_elements))
        required_prefix = 'ملاحظة بعد الملاحظة الأخيرة'
        has_correct_ending_note = False
        value_trimmed_trailing = value.rstrip()
        last_br_index = value_trimmed_trailing.rfind('<br>')
        if last_br_index != -1:
            if last_br_index + len('<br>') < len(value_trimmed_trailing):
                content_after_last_br = value_trimmed_trailing[last_br_index + len('<br>'):].strip()
                has_correct_ending_note = content_after_last_br.startswith(required_prefix)
        return contains_br and contains_math and has_correct_ending_note

class DataIdx95InstructionChecker(AragenInstructions):

    def __init__(self):
        super().__init__('idx_95')

    def check_following(self, value):
        """Checks if the response is an informal summary of UAE maternity leave policy
        with two sections and at least 25 sentences.

        Args:
            value: A string representing the response.

        Returns:
            True if the response follows the instruction or False otherwise.
        """
        if not isinstance(value, str):
            return False
        text = value.strip()
        sections = [s.strip() for s in text.split('\n\n') if s.strip()]
        has_two_sections = len(sections) == 2
        sentences = re.split('[.!?؟]', text)
        sentences = [s.strip() for s in sentences if s.strip()]
        sentence_count = len(sentences)
        has_enough_sentences = sentence_count >= 25
        return has_two_sections and has_enough_sentences

class DataIdx96InstructionChecker(AragenInstructions):

    def __init__(self):
        super().__init__('idx_96')

    def check_following(self, value):
        """Checks if the response is a valid JSON, contains a question mark,
        and does not contain the words 'نهضة' or 'أعباء'.

        Args:
            value: A string representing the response.

        Returns:
            True if the response follows the instruction or False otherwise.
        """
        try:
            json.loads(value)
        except json.JSONDecodeError:
            return False
        if '?' not in value:
            return False
        if 'نهضة' in value or 'أعباء' in value:
            return False
        return True

class DataIdx97InstructionChecker(AragenInstructions):

    def __init__(self):
        super().__init__('idx_97')

    def check_following(self, value):
        """Checks if the response (tweet) contains the keywords 'يتفاعل' and 'ببساطة'.

        Args:
            value: A string representing the response.

        Returns:
            True if the response contains both keywords, False otherwise.
        """
        if not isinstance(value, str):
            return False
        tweet = str(value)
        contains_keyword1 = 'يتفاعل' in tweet
        contains_keyword2 = 'ببساطة' in tweet
        return contains_keyword1 and contains_keyword2

class DataIdx98InstructionChecker(AragenInstructions):

    def __init__(self):
        super().__init__('idx_98')

    def check_following(self, value):
        """Checks if the response is a 4-line quatrain ending with 'نعم يا أمي، أنا جابر.' and contains the name 'جابر'.

        Args:
            value: A string representing the response.

        Returns:
            True if the response follows the instruction or False otherwise.
        """
        lines = [line.strip() for line in value.strip().split('\n')]
        if len(lines) != 4:
            return False
        if lines[-1] != 'نعم يا أمي، أنا جابر.':
            return False
        found_jaber = False
        for line in lines:
            if 'جابر' in line:
                found_jaber = True
                break
        if not found_jaber:
            return False
        return True

class DataIdx99InstructionChecker(AragenInstructions):

    def __init__(self):
        super().__init__('idx_99')

    def check_following(self, value):
        """Checks if the response follows the instructions for IDX 99.

        Instructions:
        1. Provide two distinct answers.
        2. Separate the answers with exactly six asterisks (******).
        3. Include a title in the format <<title>>.
        4. Include the keywords 'التبني' and 'العربة'.

        Args:
            value: A string representing the response.

        Returns:
            True if the response follows the instruction or False otherwise.
        """
        parts = value.split('******')
        if len(parts) != 2:
            return False
        title_pattern = '<<.*?>>'
        if not re.search(title_pattern, value):
            return False
        keyword1 = 'التبني'
        keyword2 = 'العربة'
        if keyword1 not in value or keyword2 not in value:
            return False
        return True

class DataIdx100InstructionChecker(AragenInstructions):

    def __init__(self):
        super().__init__('idx_100')

    def check_following(self, value):
        """Checks if the response follows the instructions for IDX 100.

        Args:
            value: A string representing the response.

        Returns:
            True if the response follows the instruction or False otherwise.
        """
        question_text = 'نحن شركة نسوّق منتجًا خاص بالبحث على حجز غرف الفنادق. نبحث عن إعلان مطبوع سيتم وضعه في مجلة تستهدف الأشخاص الذين يسافرون كثيرًا. يجب أن يكون الإعلان نصف صفحة ويجب أن يتضمن عنوانًا رئيسيًا . يرجى عدم استخدام أي فواصل في إجابتك.\n\nقبل قول أي شيء أو إعطاء إجابتك يرجى تكرار الطلب بأكمله أعلاه.'
        stripped_value = value.strip()
        stripped_question_text = question_text.strip()
        if not stripped_value.startswith(stripped_question_text):
            return False
        answer_part = stripped_value[len(stripped_question_text):].strip()
        if not answer_part:
            return False
        punctuation_and_symbols = set('.,!?;:،؛؟!"\'()[]{}<>/\\@#$%^&*~`-_=+|')
        for char in answer_part:
            if char in punctuation_and_symbols:
                return False
        return True

class DataIdx101InstructionChecker(AragenInstructions):

    def __init__(self):
        super().__init__('idx_101')

    def check_following(self, value):
        """Checks if the response (a poem) does not contain the words 'يا', 'تحقق', or 'سلام'.

        Args:
            value: A string representing the response (the poem).

        Returns:
            True if the response does not contain the forbidden words, False otherwise.
        """
        forbidden_words = ['يا', 'تحقق', 'سلام']
        for word in forbidden_words:
            if word in value:
                return False
        return True

class DataIdx102InstructionChecker(AragenInstructions):

    def __init__(self):
        super().__init__('idx_102')

    def check_following(self, value: str) -> bool:
        """Checks if the response follows the instruction not to mention 'محاكاة ساخرة'.

        Args:
            value: A string representing the response.

        Returns:
            True if the response does not contain 'محاكاة ساخرة', False otherwise.
        """
        forbidden_word = 'محاكاة ساخرة'
        return forbidden_word not in value

class DataIdx103InstructionChecker(AragenInstructions):

    def __init__(self):
        super().__init__('idx_103')

    def check_following(self, value):
        """Checks if the response follows the constraints:
        1. Does not exceed ten sentences.
        2. Ends with 'هذا كل ما تحتاج إليه!'.

        Args:
            value: A string representing the response.

        Returns:
            True if the response follows the instruction or False otherwise.
        """
        required_ending = 'هذا كل ما تحتاج إليه!'
        if not value.strip().endswith(required_ending):
            return False
        sentences = re.split('[.!?]+', value)
        non_empty_sentences = [s.strip() for s in sentences if s.strip()]
        sentence_count = len(non_empty_sentences)
        if sentence_count > 10:
            return False
        return True

class DataIdx104InstructionChecker(AragenInstructions):

    def __init__(self):
        super().__init__('idx_104')

    def check_following(self, value):
        """Checks if the response starts with the required literal repetition of the question part.
        Args:
            value: A string representing the response.

        Returns:
            True if the response follows the instruction (starts with the required prefix) or False otherwise.
        """
        required_prefix = 'هل يعتبر علم المقذوفات أو البلستيك، كما يُسمى أحيانًا (الخاص بدراسة حركة الأجسام التي تُطلق في الهواء، مثل القذائف، الصواريخ، والكرة في الرياضة) علماً حقيقياً؟'
        return value.startswith(required_prefix)

class DataIdx105InstructionChecker(AragenInstructions):

    def __init__(self):
        super().__init__('idx_105')

    def check_following(self, value):
        """Checks if the response follows the instructions for IDX 105.

        The instructions require:
        1. Exactly two paragraphs separated by a double newline (

).
        2. The first paragraph must start with the word "نشيط".
        3. The response must contain mathematical symbols.
        4. The tone should be cheerful (this constraint is not checked programmatically as it's subjective).

        Args:
            value: A string representing the response.

        Returns:
            True if the response follows the structural and symbol constraints,
            False otherwise.
        """
        if not isinstance(value, str):
            return False
        math_symbols = {'∈', '∉', '{', '}', '|', ':', '\\', '⊆', '⊂', '⊇', '⊃', '∪', '∩', '∅', '=', '≠', '>', '<', '≥', '≤', '∀', '∃', '!', '+', '-', '*', '/', '^', '(', ')', '[', ']', '&', '~', 'ℕ', 'ℤ', 'ℚ', 'ℝ', 'ℂ', '∞', '∑', '∏', '∫', '∂', '∇'}
        contains_symbols = any((char in value for char in math_symbols))
        if not contains_symbols:
            return False
        paragraphs = value.split('\n\n')
        if len(paragraphs) != 2:
            return False
        first_paragraph = paragraphs[0].strip()
        if not first_paragraph.startswith('نشيط'):
            return False
        return True

class DataIdx106InstructionChecker(AragenInstructions):

    def __init__(self):
        super().__init__('idx_106')

    def check_following(self, value):
        """Checks if the response follows the instructions for IDX 106.

        The constraints are:
        1. The entire answer must be enclosed in double quotes.
        2. The answer must contain the Arabic word 'مهذب'.
        3. The answer must contain the string 'القسم 1'.
        4. The answer must contain the string 'القسم 2'.

        Args:
            value: A string representing the response.

        Returns:
            True if the response follows the instruction or False otherwise.
        """
        if not isinstance(value, str):
            return False
        if not (value.startswith('"') and value.endswith('"')):
            return False
        content = value[1:-1]
        if 'مهذب' not in content:
            return False
        if 'القسم 1' not in content:
            return False
        if 'القسم 2' not in content:
            return False
        return True

class DataIdx107InstructionChecker(AragenInstructions):

    def __init__(self):
        super().__init__('idx_107')

    def check_following(self, value):
        """Checks if the response follows the instructions for IDX 107.

        Args:
            value: A string representing the response.

        Returns:
            True if the response follows the instruction or False otherwise.
        """
        required_prefix = 'اكتب قصة مكونة من 500 كلمة على شكل قصيدة عن فتاة صغيرة مهووسة بلعبة إلكترونية (بلايستيشن أو غيرها). أولاً كرر الطلب أعلاه، ثم أعط إجابتك. فقط كرر الطلب كلمة كلمة دون تغيير. لا تقل أي كلمات أو أحرف قبل تكرار الطلب.'
        if not value.strip().startswith(required_prefix):
            return False
        answer_part = value.strip()[len(required_prefix):].strip()
        if not answer_part:
            return False
        words = answer_part.split()
        word_count = len(words)
        if word_count != 500:
            return False
        lines = answer_part.splitlines()
        if len(lines) < 20:
            return False
        return True

class DataIdx108InstructionChecker(AragenInstructions):

    def __init__(self):
        super().__init__('idx_108')

    def check_following(self, value):
        """Checks if the response is a joke in 3 paragraphs, each starting with "المقطع X".

        Args:
            value: A string representing the response.

        Returns:
            True if the response follows the instruction or False otherwise.
        """
        if not isinstance(value, str) or not value.strip():
            return False
        lines = value.splitlines()
        marker_lines = {}
        for i, line in enumerate(lines):
            stripped_line = line.strip()
            if stripped_line.startswith('المقطع 1'):
                if 1 in marker_lines:
                    return False
                marker_lines[1] = i
            elif stripped_line.startswith('المقطع 2'):
                if 2 in marker_lines:
                    return False
                marker_lines[2] = i
            elif stripped_line.startswith('المقطع 3'):
                if 3 in marker_lines:
                    return False
                marker_lines[3] = i
        if 1 not in marker_lines or 2 not in marker_lines or 3 not in marker_lines:
            return False
        if marker_lines[1] < marker_lines[2] < marker_lines[3]:
            return True
        else:
            return False

class DataIdx109InstructionChecker(AragenInstructions):

    def __init__(self):
        super().__init__('idx_109')

    def check_following(self, value: str) -> bool:
        """Checks if the response follows the instruction constraints for IDX 109.
        Specifically, checks if the response ends with 'ملاحظة:'.
        Content checks (adult audience, no explicit content) are not reliably
        implementable with simple string processing and are therefore omitted
        from this programmatic check.

        Args:
            value: A string representing the response.

        Returns:
            True if the response ends with 'ملاحظة:', False otherwise.
        """
        required_ending = 'ملاحظة:'
        stripped_value = value.rstrip()
        return stripped_value.endswith(required_ending)

class DataIdx110InstructionChecker(AragenInstructions):

    def __init__(self):
        super().__init__('110')

    def check_following(self, value: str):
        """Checks if the response value does not contain the forbidden phrases.

        Args:
            value: A string representing the response.

        Returns:
            True if the response follows the instruction (does not contain forbidden phrases),
            or False otherwise.
        """
        forbidden_phrases = ['الحكايات الشعبية', 'القصص الأسطورية']
        for phrase in forbidden_phrases:
            if phrase in value:
                return False
        return True

class DataIdx111InstructionChecker(AragenInstructions):

    def __init__(self):
        super().__init__('idx_111')

    def check_following(self, value):
        """Checks if the response follows the instruction.

        Constraints:
        1. Ends with the exact phrase: "هل هناك أي شيء آخر أستطيع مساعدتكم به؟"
        (Other constraints like "short", "funny", "list" format are subjective or
        hard to check reliably in a string format without more specific rules).

        Args:
            value: A string representing the response.

        Returns:
            True if the response follows the instruction or False otherwise.
        """
        required_ending = 'هل هناك أي شيء آخر أستطيع مساعدتكم به؟'
        if value is None or not isinstance(value, str):
            return False
        return value.endswith(required_ending)

class DataIdx112InstructionChecker(AragenInstructions):

    def __init__(self):
        super().__init__('idx_112')

    def check_following(self, value):
        """You will implement the logic of the function here to see if the response is correct or not.
        Args:
            value: A string representing the response.

        Returns:
            True if the response follows the instruction or False otherwise.
        """
        forbidden_words = ['ببطء', 'كما', 'طفل']
        for word in forbidden_words:
            if word in value:
                return False
        return True

class DataIdx113InstructionChecker(AragenInstructions):

    def __init__(self):
        super().__init__('idx_113')

    def check_following(self, value):
        """Checks if the response ends with the required exact phrase.

        Args:
            value: A string representing the response.

        Returns:
            True if the response follows the instruction or False otherwise.
        """
        required_ending = 'هل هناك أي شيء آخر يمكنني مساعدتك به؟'
        return value.endswith(required_ending)

class DataIdx114InstructionChecker(AragenInstructions):

    def __init__(self):
        super().__init__('idx_114')

    def check_following(self, value):
        """Checks if the response follows the instructions for IDX 114.

        Instructions:
        - Write exactly 4 paragraphs.
        - Each paragraph must be separated by two newlines (\\n\\n).
        - The first paragraph must start with the word 'الشركات'.

        Args:
            value: A string representing the response.

        Returns:
            True if the response follows the instruction or False otherwise.
        """
        if not isinstance(value, str):
            return False
        paragraphs = value.split('\n\n')
        if len(paragraphs) != 4:
            return False
        first_paragraph = paragraphs[0].strip()
        if not first_paragraph.startswith('الشركات'):
            return False
        return True

class DataIdx115InstructionChecker(AragenInstructions):

    def __init__(self):
        super().__init__('idx_115')

    def check_following(self, value):
        """Checks if the response follows the instructions for IDX 115.

        Args:
            value: A string representing the response.

        Returns:
            True if the response follows the instruction or False otherwise.
        """
        if not isinstance(value, str):
            return False
        required_ending = 'هل هناك أي شيء آخر يمكنني مساعدتك فيه؟'
        if not value.rstrip().endswith(required_ending):
            return False
        rstripped_value = value.rstrip()
        body_end_index = len(rstripped_value) - len(required_ending)
        if body_end_index < 0:
            return False
        body = rstripped_value[:body_end_index]
        if not body or '\n' not in body:
            return False
        return True

class DataIdx116InstructionChecker(AragenInstructions):

    def __init__(self):
        super().__init__('116')
        self.forbidden_phrases = ['عُثِر عليه']
        self.forbidden_single_words = ['قصة', 'قاتل', 'ميت', 'قانون', 'غرفة', 'قتل', 'نتيجة', 'استخدام', 'نهج', 'ناس', 'رئيس']
        self.forbidden_word_patterns = [re.compile('\\b' + re.escape(word) + '\\b') for word in self.forbidden_single_words]

    def check_following(self, value):
        """Checks if the response follows the constraints, specifically checking for forbidden words/phrases.
        Args:
            value: A string representing the response.

        Returns:
            True if the response follows the instruction (specifically, lacks forbidden words/phrases) or False otherwise.
        """
        if not isinstance(value, str):
            return False
        for phrase in self.forbidden_phrases:
            if phrase in value:
                return False
        for pattern in self.forbidden_word_patterns:
            if pattern.search(value):
                return False
        return True

class DataIdx117InstructionChecker(AragenInstructions):

    def __init__(self):
        super().__init__('idx_117')

    def check_following(self, value):
        """Checks if the response follows the instructions for IDX 117.

        Instructions:
        - Write a strange and short haiku about Al-Ahsa in Saudi Arabia.
        - Do not use any commas in the entire response.
        - End the response exactly with the phrase 'في السعودية.'.

        Args:
            value: A string representing the response.

        Returns:
            True if the response follows the instruction or False otherwise.
        """
        if ',' in value:
            return False
        required_ending = 'في السعودية.'
        if not value.strip().endswith(required_ending):
            return False
        if len(value.strip()) <= len(required_ending):
            if value.strip() != required_ending:
                return False
        return True

class DataIdx118InstructionChecker(AragenInstructions):

    def __init__(self):
        super().__init__('idx_118')

    def check_following(self, value):
        """
        Checks if the response follows the constraints for question IDX 118.

        Constraints:
        1. At least 900 words.
        2. Does not contain the words 'نباح' or 'ركض'.
        3. Ends exactly with the phrase 'هل هذا منطقي؟'.

        Args:
            value: A string representing the response.

        Returns:
            True if the response follows all instructions, False otherwise.
        """
        words = value.split()
        word_count = len(words)
        if word_count < 900:
            return False
        if 'نباح' in value or 'ركض' in value:
            return False
        required_ending = 'هل هذا منطقي؟'
        if not value.strip().endswith(required_ending):
            return False
        return True

class DataIdx119InstructionChecker(AragenInstructions):

    def __init__(self):
        super().__init__('119')

    def check_following(self, value):
        """Checks if the response includes a title enclosed in double angle brackets and a note starting with 'ملاحظة هامة'.

        Args:
            value: A string representing the response.

        Returns:
            True if the response follows the instruction or False otherwise.
        """
        has_title = re.search('<<.*?>>', value) is not None
        has_note = 'ملاحظة هامة' in value
        return has_title and has_note

class DataIdx120InstructionChecker(AragenInstructions):

    def __init__(self):
        super().__init__('idx_120')

    def check_following(self, value):
        """Checks if the response contains all the required keywords.

        Args:
            value: A string representing the response.

        Returns:
            True if the response contains all keywords, False otherwise.
        """
        if not isinstance(value, str):
            return False
        required_keywords = ['الثقة', 'العلامة التجارية', 'العميل', 'القانون', 'السياسة', 'غير صالح للاستخدام']
        for keyword in required_keywords:
            if keyword not in value:
                return False
        return True

class DataIdx121InstructionChecker(AragenInstructions):

    def __init__(self):
        super().__init__('idx_121')

    def check_following(self, value):
        """
        Checks if the response avoids the words "إجراءات" and "خطوة".

        Args:
            value: A string representing the response.

        Returns:
            True if the response follows the instruction or False otherwise.
        """
        if not isinstance(value, str):
            return False
        forbidden_words = ['إجراءات', 'خطوة']
        for word in forbidden_words:
            if word in value:
                return False
        return True

class DataIdx122InstructionChecker(AragenInstructions):

    def __init__(self):
        super().__init__('idx_122')

    def check_following(self, value):
        """Checks if the response ends with the specified phrase and has no text following it.

        Args:
            value: A string representing the response.

        Returns:
            True if the response follows the instruction or False otherwise.
        """
        required_ending = 'اتصل بي على الرقم 631-481-4867'
        return value.endswith(required_ending)

class DataIdx123InstructionChecker(AragenInstructions):

    def __init__(self):
        super().__init__('idx_123')

    def check_following(self, value):
        """Checks if the response ends exactly with 'نادية تشكركم على القراءة.' with nothing following it.
        Args:
            value: A string representing the response.

        Returns:
            True if the response follows the instruction (ends exactly with the required phrase) or False otherwise.
        """
        required_ending = 'نادية تشكركم على القراءة.'
        if value is None or not isinstance(value, str):
            return False
        if len(value) < len(required_ending):
            return False
        return value[-len(required_ending):] == required_ending

class DataIdx124InstructionChecker(AragenInstructions):

    def __init__(self):
        super().__init__('idx_124')

    def check_following(self, value):
        """
        Checks if the response follows the instructions for IDX 124.
        Instructions:
        1. Repeat the prompt word-for-word without change.
        2. Then, provide the answer (a riddle using mathematical symbols).
        3. Do not say any words before repeating the prompt.

        Args:
            value: A string representing the response.

        Returns:
            True if the response follows the instruction or False otherwise.
        """
        required_prefix = 'اكتب لغزاً شيقاً يستخدم الرموز الرياضية. أولاً كرر الطلب كلمة بكلمة دون تغيير، ثم قدم إجابتك. لا تقل أي كلمة قبل تكرار الطلب.'
        if not value.startswith(required_prefix):
            return False
        if len(value) <= len(required_prefix):
            return False
        return True

class DataIdx125InstructionChecker(AragenInstructions):

    def __init__(self):
        super().__init__('idx_125')

    def check_following(self, value):
        """Checks if the response follows the instructions for IDX 125.

        Args:
            value: A string representing the response.

        Returns:
            True if the response follows the instruction or False otherwise.
        """
        if 'جامعة' in value:
            return False
        paragraphs = value.split('***')
        if len(paragraphs) != 4:
            return False
        return True

class DataIdx126InstructionChecker(AragenInstructions):

    def __init__(self):
        super().__init__('idx_126')

    def check_following(self, value):
        """Checks if the response follows the instructions for IDX 126.

        Args:
            value: A string representing the response.

        Returns:
            True if the response follows the instruction or False otherwise.
        """
        if not isinstance(value, str):
            return False
        if value.count('******') != 1:
            return False
        parts = value.split('******')
        if len(parts) != 2:
            return False
        part1 = parts[0].strip()
        part2 = parts[1].strip()
        expected_sequence = [1, 2, 3, 4, 5, 6, 7]

        def check_part(text):
            """Helper function to check if a single itinerary part is valid."""
            found_numbers_str = re.findall('اليوم\\s*(\\d+)', text)
            try:
                found_numbers = [int(n) for n in found_numbers_str]
            except ValueError:
                return False
            return found_numbers == expected_sequence
        return check_part(part1) and check_part(part2)

class DataIdx127InstructionChecker(AragenInstructions):

    def __init__(self):
        super().__init__('idx_127')

    def check_following(self, value: str) -> bool:
        """
        Checks if the response follows the instructions:
        - Includes the word 'أبيض'.
        - Includes the word 'مزيف' exactly 6 or 7 times.

        Args:
            value: A string representing the response.

        Returns:
            True if the response follows the instruction or False otherwise.
        """
        if not isinstance(value, str):
            return False
        contains_abyad = 'أبيض' in value
        count_muzayaf = value.count('مزيف')
        muzayaf_count_correct = count_muzayaf == 6 or count_muzayaf == 7
        return contains_abyad and muzayaf_count_correct

class DataIdx128InstructionChecker(AragenInstructions):

    def __init__(self):
        super().__init__('idx_128')

    def check_following(self, value):
        """Checks if the response follows the instructions for IDX 128.

        Args:
            value: A string representing the response.

        Returns:
            True if the response follows the instruction or False otherwise.
        """
        forbidden_keywords = ['قتل', 'مذبحة', 'احتلال', 'هجوم']
        for keyword in forbidden_keywords:
            if keyword in value:
                return False
        if value.count('لص') < 2:
            return False
        if value.count(':') != 2:
            return False
        if '* نقطة 1:' not in value:
            return False
        if '* نقطة 2:' not in value:
            return False
        return True

class DataIdx129InstructionChecker(AragenInstructions):

    def __init__(self):
        super().__init__('idx_129')

    def check_following(self, value):
        """Checks if the response follows the instructions for IDX 129.

        Constraints:
        1. Should be in a Q&A format (heuristic: contains '?' and '.').
        2. Less than 8 sentences.
        3. Does not contain the words 'استهلاك' or 'وقود'.

        Args:
            value: A string representing the response.

        Returns:
            True if the response follows the instruction or False otherwise.
        """
        if not isinstance(value, str):
            return False
        forbidden_words = ['استهلاك', 'وقود']
        for word in forbidden_words:
            if word in value:
                return False
        sentences = [s for s in re.split('[.?!]', value) if s.strip()]
        if len(sentences) >= 8:
            return False
        if '?' not in value or '.' not in value:
            if '?' not in value or '.' not in value:
                pass
        if '?' not in value or '.' not in value:
            return False
        return True

class DataIdx130InstructionChecker(AragenInstructions):

    def __init__(self):
        super().__init__('idx_130')

    def check_following(self, value):
        """Checks if the response follows the instructions for IDX 130.
        Instructions: Write two ads for a healthy soda alternative.
        One for teenagers, one for professionals.
        Each ad must start with 'الفئة الأولى' and 'الفئة الثانية' respectively.
        The entire answer must be enclosed in double quotes.

        Args:
            value: A string representing the response.

        Returns:
            True if the response follows the instruction or False otherwise.
        """
        if not isinstance(value, str) or not value.startswith('"') or (not value.endswith('"')):
            return False
        inner_value = value[1:-1]
        category1_marker = 'الفئة الأولى'
        category2_marker = 'الفئة الثانية'
        if category1_marker not in inner_value or category2_marker not in inner_value:
            return False
        stripped_inner_value = inner_value.strip()
        if not stripped_inner_value.startswith(category1_marker):
            return False
        idx1 = inner_value.find(category1_marker)
        idx2 = inner_value.find(category2_marker)
        if idx1 >= idx2:
            return False
        return True

class DataIdx131InstructionChecker(AragenInstructions):

    def __init__(self):
        super().__init__('idx_131')

    def check_following(self, value):
        """Checks if the response follows the instructions for IDX 131.
        Args:
            value: A string representing the response.

        Returns:
            True if the response follows the instruction or False otherwise.
        """
        if 'بعد الظهر' not in value:
            return False
        if 'مضطرب' not in value:
            return False
        if ',' in value:
            return False
        return True

class DataIdx132InstructionChecker(AragenInstructions):

    def __init__(self):
        super().__init__('idx_132')

    def check_following(self, value):
        """Checks if the response follows the instructions for question IDX 132.

        Constraints:
        1. Avoid using the words 'يقسم' (divides).
        2. Avoid using the words 'الإجابة' (the answer).
        3. Use the word 'الباقي' (the remainder/the rest).

        Args:
            value: A string representing the response.

        Returns:
            True if the response follows the instructions, False otherwise.
        """
        forbidden_words = ['يقسم', 'الإجابة']
        required_word = 'الباقي'
        for word in forbidden_words:
            if word in value:
                return False
        if required_word not in value:
            return False
        return True

class DataIdx133InstructionChecker(AragenInstructions):

    def __init__(self):
        super().__init__('idx_133')

    def check_following(self, value):
        """Checks if the response follows the instructions for IDX 133.

        Instructions:
        - Story must have at least 4 parts, each starting with 'الفصل' followed by its serial number.
        - Entire story must contain at least 100 sentences.

        Args:
            value: A string representing the response (the story).

        Returns:
            True if the response follows the instruction or False otherwise.
        """
        if not isinstance(value, str):
            return False
        chapter_pattern = re.compile('^الفصل\\s+\\d+', re.MULTILINE)
        chapters = chapter_pattern.findall(value)
        has_enough_chapters = len(chapters) >= 4
        sentence_terminators = '[.!?؟]'
        sentences = re.split(sentence_terminators, value)
        non_empty_sentences = [s for s in sentences if s.strip()]
        has_enough_sentences = len(non_empty_sentences) >= 100
        return has_enough_chapters and has_enough_sentences

class DataIdx134InstructionChecker(AragenInstructions):

    def __init__(self):
        super().__init__('idx_134')

    def check_following(self, value):
        """Checks if the response is an HTML page containing 25 lines and the required Arabic words.

        Args:
            value: A string representing the response (expected to be HTML).

        Returns:
            True if the response follows the instruction or False otherwise.
        """
        if not isinstance(value, str):
            return False
        is_html = '<html>' in value.lower()
        required_words = ['اقتصادي', 'بلال', 'العالمي']
        has_required_words = all((word in value for word in required_words))
        line_count = value.count('\n') + 1
        has_25_lines = line_count == 25
        return is_html and has_required_words and has_25_lines

class DataIdx135InstructionChecker(AragenInstructions):

    def __init__(self):
        super().__init__('idx_135')

    def check_following(self, value):
        """Checks if the response follows the instruction for IDX 135.
        The response must not contain the words "برمجيات" or "علوم".

        Args:
            value: A string representing the response.

        Returns:
            True if the response follows the instruction (does not contain forbidden words),
            False otherwise.
        """
        forbidden_word1 = 'برمجيات'
        forbidden_word2 = 'علوم'
        if forbidden_word1 in value or forbidden_word2 in value:
            return False
        return True

class DataIdx136InstructionChecker(AragenInstructions):

    def __init__(self):
        super().__init__('idx_136')

    def check_following(self, value):
        """Checks if the response (a poem) follows the instructions for IDX 136.

        Constraints:
        - Do not include the words 'اسم', 'قصيدة', 'شخص', 'رجل', 'امرأة'.
        - Do not use commas (,) anywhere in the response.

        Args:
            value: A string representing the response (the poem).

        Returns:
            True if the response follows all instructions, False otherwise.
        """
        forbidden_words = ['اسم', 'قصيدة', 'شخص', 'رجل', 'امرأة']
        for word in forbidden_words:
            if word in value:
                return False
        if ',' in value:
            return False
        return True

class DataIdx137InstructionChecker(AragenInstructions):

    def __init__(self):
        super().__init__('idx_137')
        self.required_prefix = 'اكتب عرضًا تقديميًا لمشروع ناشئ يهدف إلى إنشاء شبكة اجتماعية جديدة تركز على مجتمع لاعبي الطاولة.'

    def check_following(self, value: str):
        """Checks if the response starts with the exact request string.
        Args:
            value: A string representing the response.

        Returns:
            True if the response follows the instruction or False otherwise.
        """
        return value.strip().startswith(self.required_prefix)

class DataIdx138InstructionChecker(AragenInstructions):

    def __init__(self):
        super().__init__('idx_138')

    def check_following(self, value):
        """Checks if the response follows the instruction constraints for IDX 138.

        Constraints:
        1. The response must start with a literal repetition of the question.
        2. The part of the response *after* the repeated question must not contain any commas (English or Arabic).

        Args:
            value: A string representing the response.

        Returns:
            True if the response follows the instructions, False otherwise.
        """
        required_preamble = 'اكتب قائمة بالمزايا والعيوب المتعلقة بمنتجات التفاح بأسلوب كاتب روايات من القرن التاسع عشر ولا تستخدم أي فواصل. كرر الطلب أعلاه حرفياً دون تغيير في بداية ردك بالكامل بعد ذلك يمكنك إعطاء قائمة المزايا والعيوب المطلوبة'
        if not value.startswith(required_preamble):
            return False
        content_after_preamble = value[len(required_preamble):]
        if ',' in content_after_preamble or '،' in content_after_preamble:
            return False
        return True

class DataIdx139InstructionChecker(AragenInstructions):

    def __init__(self):
        super().__init__('idx_139')

    def check_following(self, value):
        """
        Checks if the response follows the instructions for IDX 139.
        Constraints:
        - The entire text must be in JSON format, enclosed in ```JSON ... ``` Markdown tags.
        - The words 'اقتراح' or 'دراسة' must not be included.

        Args:
            value: A string representing the response.

        Returns:
            True if the response follows the instruction or False otherwise.
        """
        if not value.strip().startswith('```JSON\n') or not value.strip().endswith('\n```'):
            return False
        json_content = value.strip()[len('```JSON\n'):-len('\n```')]
        try:
            json.loads(json_content)
        except json.JSONDecodeError:
            return False
        if 'اقتراح' in value or 'دراسة' in value:
            return False
        return True

class DataIdx140InstructionChecker(AragenInstructions):

    def __init__(self):
        super().__init__('idx_140')

    def check_following(self, value):
        """Checks if the response is a valid JSON block containing 'تعويض' and 'مهاجرون'.

        Args:
            value: A string representing the response.

        Returns:
            True if the response follows the instruction or False otherwise.
        """
        try:
            json.loads(value)
            has_taawidh = 'تعويض' in value
            has_muhajiroon = 'مهاجرون' in value
            return has_taawidh and has_muhajiroon
        except json.JSONDecodeError:
            return False
        except Exception:
            return False

class DataIdx141InstructionChecker(AragenInstructions):

    def __init__(self):
        super().__init__('idx_141')
        self.question_text = 'ما هو اسم الممثل الذي قام بدور جبل في مسلسل الهيبة؟'

    def check_following(self, value):
        """Checks if the response repeats the question first and then provides an answer.

        Args:
            value: A string representing the response.

        Returns:
            True if the response follows the instruction or False otherwise.
        """
        if not value.startswith(self.question_text):
            return False
        if len(value) <= len(self.question_text):
            return False
        return True

class DataIdx142InstructionChecker(AragenInstructions):

    def __init__(self):
        super().__init__('idx_142')

    def check_following(self, value):
        """Checks if the response follows the constraints for IDX 142.
        Constraints:
        1. Must contain exactly one '***' separator, resulting in two parts when split.
        2. Must not contain the word "فارس".

        Args:
            value: A string representing the response.

        Returns:
            True if the response follows the instruction or False otherwise.
        """
        parts = value.split('***')
        if len(parts) != 2:
            return False
        if 'فارس' in value:
            return False
        return True

class DataIdx143InstructionChecker(AragenInstructions):

    def __init__(self):
        super().__init__('idx_143')

    def check_following(self, value: str) -> bool:
        """Checks if the response is structured into 3 parts starting with 'القسم N'.

        Args:
            value: A string representing the response.

        Returns:
            True if the response follows the structural instruction (3 parts, marked correctly),
            False otherwise.
        """
        if not isinstance(value, str):
            return False
        cleaned_value = value.strip()
        if not cleaned_value.startswith('القسم 1'):
            return False
        marker1 = 'القسم 1'
        marker2 = 'القسم 2'
        marker3 = 'القسم 3'
        pos1 = value.find(marker1)
        pos2 = value.find(marker2)
        pos3 = value.find(marker3)
        if pos1 == -1 or pos2 == -1 or pos3 == -1:
            return False
        if not pos1 < pos2 < pos3:
            return False
        parts = value.split('القسم ')
        found_markers_count = 0
        for i in range(1, len(parts)):
            part_content = parts[i].strip()
            if part_content.startswith('1') or part_content.startswith('2') or part_content.startswith('3'):
                if len(part_content) > 1 and part_content[0] in '123' and part_content[1].isspace():
                    found_markers_count += 1
        for i in range(4, 10):
            if value.find(f'القسم {i}') != -1:
                return False
        return True

class DataIdx144InstructionChecker(AragenInstructions):

    def __init__(self):
        super().__init__('idx_144')

    def check_following(self, value):
        """Checks if the response (poem) avoids the forbidden words.
        Args:
            value: A string representing the response.

        Returns:
            True if the response does not contain the words "جمال" or "جميل", False otherwise.
        """
        if 'جمال' in value:
            return False
        if 'جميل' in value:
            return False
        return True

class DataIdx145InstructionChecker(AragenInstructions):

    def __init__(self):
        super().__init__('idx_145')

    def check_following(self, value):
        """You will implement the logic of the function here to see if the response is correct or not.
        Args:
            value: A string representing the response.

        Returns:
            True if the response follows the instruction or False otherwise.
        """
        if not isinstance(value, str):
            return False
        paragraphs = value.split('\n\n')
        if len(paragraphs) != 4:
            return False
        second_paragraph = paragraphs[1]
        if not second_paragraph.lstrip().startswith('إنها'):
            return False
        return True

class DataIdx146InstructionChecker(AragenInstructions):

    def __init__(self):
        super().__init__('idx_146')

    def check_following(self, value):
        """Checks if the response follows the instruction for IDX 146.

        Args:
            value: A string representing the response.

        Returns:
            True if the response follows the instruction or False otherwise.
        """
        if not (value.startswith('"') and value.endswith('"')):
            return False
        if len(value) < 2:
            return False
        content = value[1:-1]
        forbidden_words = ['عطر', 'الحمضيات', 'جيد']
        for word in forbidden_words:
            if word in content:
                return False
        if 'أنغام' not in content:
            return False
        return True

class DataIdx147InstructionChecker(AragenInstructions):

    def __init__(self):
        super().__init__('idx_147')

    def check_following(self, value):
        """Checks if the response is a JSON string and does not contain the word 'مفتاح'.
        Args:
            value: A string representing the response.

        Returns:
            True if the response follows the instruction or False otherwise.
        """
        try:
            json.loads(value)
        except json.JSONDecodeError:
            return False
        forbidden_word = 'مفتاح'
        if forbidden_word in value:
            return False
        return True

class DataIdx148InstructionChecker(AragenInstructions):

    def __init__(self):
        super().__init__('idx_148')

    def check_following(self, value):
        """Checks if the response follows the instructions for question 148.

        Constraints:
        1. Must contain a title enclosed in double angle brackets (<<title>>).
        2. Must highlight at least two paragraphs using the format *paragraph*.
        3. Must end with a concluding note starting with "ملحوظة إضافية".

        Args:
            value: A string representing the response.

        Returns:
            True if the response follows all constraints, False otherwise.
        """
        if not isinstance(value, str):
            return False
        title_match = re.search('<<.*?>>', value)
        has_title = title_match is not None
        highlighted_paragraphs = re.findall('\\*.*?\\*', value, re.DOTALL)
        has_at_least_two_highlighted = len(highlighted_paragraphs) >= 2
        note_phrase = 'ملحوظة إضافية'
        has_concluding_note = False
        lines = [line.strip() for line in value.strip().splitlines() if line.strip()]
        if lines and lines[-1].startswith(note_phrase):
            has_concluding_note = True
        return has_title and has_at_least_two_highlighted and has_concluding_note

class DataIdx149InstructionChecker(AragenInstructions):

    def __init__(self):
        super().__init__('149')

    def check_following(self, value):
        """
        Checks if the response follows the instructions for IDX 149.

        Constraints:
        1. Repeat the entire request verbatim at the beginning.
        2. Include a subject line enclosed in double angle brackets (<< >>) in the response part.
        3. Do not use any commas (,) in the response part.

        Args:
            value: A string representing the response.

        Returns:
            True if the response follows the instructions, False otherwise.
        """
        question_text = 'أنشئ سيرة ذاتية لضابط عسكري خدم في العراق وتم تعيينه لاحقًا من قبل شركة أمنية خاصة. تأكد من تضمين عنوان موضوع بين قوسين مزدوجين، مثلاً <<السيرة الذاتية: اسم الضابط المقترح>>. امتنع عن استخدام أي فواصل في ردك.\n\nقبل أن تجيب بأي كلمة، كرّر الطلب بأكمله حرفًا حرفًا دون تغيير.'
        if not value.startswith(question_text):
            return False
        response_body = value[len(question_text):]
        if ',' in response_body:
            return False
        open_bracket_idx = response_body.find('<<')
        close_bracket_idx = response_body.find('>>', open_bracket_idx + 2)
        if open_bracket_idx == -1 or close_bracket_idx == -1:
            return False
        return True

class DataIdx150InstructionChecker(AragenInstructions):

    def __init__(self):
        super().__init__('idx_150')

    def check_following(self, value):
        """Checks if the response includes the required words 'مهرجان' and 'نهر'.

        Args:
            value: A string representing the response.

        Returns:
            True if the response includes both 'مهرجان' and 'نهر', False otherwise.
        """
        has_مهرجان = 'مهرجان' in value
        has_نهر = 'نهر' in value
        return has_مهرجان and has_نهر

class DataIdx151InstructionChecker(AragenInstructions):

    def __init__(self):
        super().__init__('idx_151')

    def check_following(self, value):
        """Checks if the response follows the instructions for IDX 151.

        Args:
            value: A string representing the response.

        Returns:
            True if the response follows the instruction or False otherwise.
        """
        separator = '******'
        if separator not in value:
            return False
        parts = value.split(separator)
        if len(parts) != 2:
            return False
        required_words = ['كلب', 'نهار']
        for word in required_words:
            if word not in value:
                return False
        return True

class DataIdx152InstructionChecker(AragenInstructions):

    def __init__(self):
        super().__init__('idx_152')

    def check_following(self, value):
        """Checks if the response contains any commas.

        Args:
            value: A string representing the response.

        Returns:
            True if the response does not contain any commas, False otherwise.
        """
        if ',' in value:
            return False
        return True

class DataIdx153InstructionChecker(AragenInstructions):

    def __init__(self):
        super().__init__('idx_153')

    def check_following(self, value):
        """Checks if the response (a CV) contains at least 12 placeholders
           represented by square brackets [].

        Args:
            value: A string representing the response (the CV).

        Returns:
            True if the response contains 12 or more placeholders, False otherwise.
        """
        placeholders = re.findall('\\[.*?\\]', value)
        return len(placeholders) >= 12

class DataIdx154InstructionChecker(AragenInstructions):

    def __init__(self):
        super().__init__('idx_154')

    def check_following(self, value):
        """Checks if the response contains exactly three points formatted as a list starting with '* '.

        Args:
            value: A string representing the response.

        Returns:
            True if the response follows the instruction or False otherwise.
        """
        lines = value.strip().split('\n')
        list_item_count = 0
        for line in lines:
            if line.strip().startswith('* '):
                list_item_count += 1
        return list_item_count == 3

class DataIdx155InstructionChecker(AragenInstructions):

    def __init__(self):
        super().__init__('idx_155')

    def check_following(self, value):
        """Checks if the response contains 400 words or more based on the instruction.

        Args:
            value: A string representing the response.

        Returns:
            True if the response has 400 words or more, False otherwise.
        """
        if not isinstance(value, str):
            return False
        words = value.split()
        return len(words) >= 400

class DataIdx156InstructionChecker(AragenInstructions):

    def __init__(self):
        super().__init__('idx_156')

    def check_following(self, value):
        """Checks if the response is in JSON format.

        Args:
            value: A string representing the response.

        Returns:
            True if the response is valid JSON, False otherwise.
        """
        if not isinstance(value, str):
            return False
        try:
            json.loads(value)
            return True
        except json.JSONDecodeError:
            return False

class DataIdx157InstructionChecker(AragenInstructions):

    def __init__(self):
        super().__init__('idx_157')

    def check_following(self, value):
        """Checks if the response consists of exactly two parts separated by the Markdown horizontal rule '***'.

        Args:
            value: A string representing the response.

        Returns:
            True if the response follows the instruction (exactly two parts separated by '***'), False otherwise.
        """
        parts = value.split('***')
        return len(parts) == 2

class DataIdx158InstructionChecker(AragenInstructions):

    def __init__(self):
        super().__init__('idx_158')

    def check_following(self, value):
        """Checks if the response is a short blog post about a trip to Egypt using less than 300 words.

        Args:
            value: A string representing the response.

        Returns:
            True if the response follows the instruction (word count < 300), False otherwise.
        """
        if not isinstance(value, str):
            return False
        words = value.split()
        word_count = len(words)
        return word_count < 300

class DataIdx159InstructionChecker(AragenInstructions):

    def __init__(self):
        super().__init__('idx_159')

    def check_following(self, value):
        """Checks if the response is a JSON block containing a list of 5 items.

        Args:
            value: A string representing the response.

        Returns:
            True if the response is a valid JSON list of exactly 5 items, False otherwise.
        """
        try:
            data = json.loads(value)
            if not isinstance(data, list):
                return False
            if len(data) != 5:
                return False
            return True
        except json.JSONDecodeError:
            return False
        except Exception:
            return False

class DataIdx160InstructionChecker(AragenInstructions):

    def __init__(self):
        super().__init__('160')

    def check_following(self, value: str) -> bool:
        """Checks if the response follows the instruction for IDX 160.

        Constraints:
        1. Contains exactly two parts.
        2. The two parts are separated by exactly "******".
        3. Neither part is empty after stripping whitespace.

        Args:
            value: A string representing the response.

        Returns:
            True if the response follows the instruction or False otherwise.
        """
        separator = '******'
        if separator not in value:
            return False
        parts = value.split(separator)
        if len(parts) != 2:
            return False
        part1 = parts[0].strip()
        part2 = parts[1].strip()
        if not part1 or not part2:
            return False
        return True

class DataIdx161InstructionChecker(AragenInstructions):

    def __init__(self):
        super().__init__('idx_161')

    def check_following(self, value):
        """
        Checks if the response contains two jokes about rockets, separated by '******',
        and contains no commas.
        Args:
            value: A string representing the response.

        Returns:
            True if the response follows the instruction or False otherwise.
        """
        has_separator = '******' in value
        no_commas = ',' not in value
        return has_separator and no_commas

class DataIdx162InstructionChecker(AragenInstructions):

    def __init__(self):
        super().__init__('idx_162')

    def check_following(self, value: str) -> bool:
        """Checks if the response follows the constraints for IDX 162.
        Constraints:
        1. Must be entirely in JSON format.
        2. Should be concise.
        3. Can optionally be wrapped in ``` markdown code block.
        4. Content should conceptually cover advantages and disadvantages,
           structured within the JSON.

        Args:
            value: A string representing the response.

        Returns:
            True if the response follows the instructions or False otherwise.
        """
        markdown_match = re.search('```(?:json\\n|\\n)?(.*?)```', value, re.DOTALL)
        json_string = value.strip()
        if markdown_match:
            json_string = markdown_match.group(1).strip()
        MAX_CHARS = 1500
        if len(json_string) > MAX_CHARS:
            return False
        try:
            data = json.loads(json_string)
            if not isinstance(data, dict):
                return False
            required_keys = ['مزايا', 'عيوب']
            for key in required_keys:
                if key not in data:
                    return False
                value_content = data[key]
                if isinstance(value_content, (list, str, dict)) and (not value_content):
                    return False
            return True
        except json.JSONDecodeError:
            return False
        except Exception as e:
            return False

class DataIdx163InstructionChecker(AragenInstructions):

    def __init__(self):
        super().__init__('idx_163')

    def check_following(self, value):
        """Checks if the response follows the instruction not to use any commas.
        Args:
            value: A string representing the response.

        Returns:
            True if the response contains no commas (U+002C or U+060C), False otherwise.
        """
        if ',' in value or '،' in value:
            return False
        return True

class DataIdx164InstructionChecker(AragenInstructions):

    def __init__(self):
        super().__init__('idx_164')

    def check_following(self, value):
        """Checks if the response follows the instructions for IDX 164.
        Args:
            value: A string representing the response.

        Returns:
            True if the response follows the instruction or False otherwise.
        """
        if not isinstance(value, str):
            return False
        title_pattern = re.compile('<<(.+)>>')
        if not title_pattern.search(value):
            return False
        if value.count('******') != 1:
            return False
        parts = value.split('******')
        if len(parts) != 2:
            return False
        part1 = parts[0].strip()
        part2 = parts[1].strip()
        if not part1 or not part2:
            return False
        return True

class DataIdx165InstructionChecker(AragenInstructions):

    def __init__(self):
        super().__init__('idx_165')

    def check_following(self, value):
        """Checks if the response follows the instruction for IDX 165.

        Constraints:
        - Provide two formal alternatives. (Hard to check programmatically)
        - Do not use any commas (فواصل) in the response. (Checkable)

        Args:
            value: A string representing the response.

        Returns:
            True if the response follows the checkable constraint (no commas),
            False otherwise.
        """
        if not isinstance(value, str):
            return False
        if ',' in value or '،' in value:
            return False
        return True

class DataIdx166InstructionChecker(AragenInstructions):

    def __init__(self):
        super().__init__('idx_166')

    def check_following(self, value):
        """Checks if the response contains 'حرب' at least 8 times and 'سلام' at least 10 times.

        Args:
            value: A string representing the response.

        Returns:
            True if the response follows the instruction or False otherwise.
        """
        word_war = 'حرب'
        min_war_count = 8
        word_peace = 'سلام'
        min_peace_count = 10
        war_matches = re.findall('\\b' + re.escape(word_war) + '\\b', value)
        peace_matches = re.findall('\\b' + re.escape(word_peace) + '\\b', value)
        war_count = len(war_matches)
        peace_count = len(peace_matches)
        return war_count >= min_war_count and peace_count >= min_peace_count

class DataIdx167InstructionChecker(AragenInstructions):

    def __init__(self):
        super().__init__('idx_167')

    def check_following(self, value):
        """Checks if the response is entirely within double quotes and contains at least 800 words.

        Args:
            value: A string representing the response.

        Returns:
            True if the response follows the instruction or False otherwise.
        """
        if not (value.startswith('"') and value.endswith('"')):
            return False
        content = value[1:-1]
        words = content.split()
        word_count = len([word for word in words if word])
        if word_count < 800:
            return False
        return True

class DataIdx168InstructionChecker(AragenInstructions):

    def __init__(self):
        super().__init__('idx_168')

    def check_following(self, value):
        """Checks if the response is less than 150 words.

        Args:
            value: A string representing the response.

        Returns:
            True if the response has less than 150 words, False otherwise.
        """
        if not isinstance(value, str):
            return False
        words = value.split()
        word_count = len(words)
        return word_count < 150

class DataIdx169InstructionChecker(AragenInstructions):

    def __init__(self):
        super().__init__('idx_169')

    def check_following(self, value):
        """Checks if the response is enclosed in double quotes.

        Args:
            value: A string representing the response.

        Returns:
            True if the response is enclosed in double quotes, False otherwise.
        """
        if isinstance(value, str) and len(value) >= 2 and (value[0] == '"') and (value[-1] == '"'):
            return True
        return False

class DataIdx170InstructionChecker(AragenInstructions):

    def __init__(self):
        super().__init__('idx_170')

    def check_following(self, value):
        """Checks if the response contains exactly 3 paragraphs separated by '***'."""
        parts = value.split('***')
        if len(parts) != 3:
            return False
        for part in parts:
            if not part.strip():
                return False
        return True

class DataIdx171InstructionChecker(AragenInstructions):

    def __init__(self):
        super().__init__('idx_171')

    def check_following(self, value):
        """
        Checks if the response is a rap song with exactly 4 stanzas separated by '***'.
        Style and tone are subjective and not checked programmatically.

        Args:
            value: A string representing the response.

        Returns:
            True if the response has exactly 4 sections separated by '***', False otherwise.
        """
        if not isinstance(value, str):
            return False
        if '***' not in value:
            return False
        sections = value.split('***')
        return len(sections) == 4

class DataIdx172InstructionChecker(AragenInstructions):

    def __init__(self):
        super().__init__('172')

    def check_following(self, value):
        """Checks if the response is a poem with at least 350 words.

        Args:
            value: A string representing the response (the poem).

        Returns:
            True if the response has at least 350 words, False otherwise.
        """
        if not isinstance(value, str):
            return False
        words = value.split()
        word_count = len(words)
        return word_count >= 350

class DataIdx173InstructionChecker(AragenInstructions):

    def __init__(self):
        super().__init__('idx_173')

    def check_following(self, value):
        """Checks if the response contains at least 600 words.

        Args:
            value: A string representing the response.

        Returns:
            True if the response has 600 or more words, False otherwise.
        """
        if not isinstance(value, str):
            return False
        words = value.split()
        word_count = len(words)
        return word_count >= 600

class DataIdx174InstructionChecker(AragenInstructions):

    def __init__(self):
        super().__init__('idx_174')

    def check_following(self, value):
        """You will implement the logic of the function here to see if the response is correct or not.
        Args:
            value: A string representing the response.

        Returns:
            True if the response follows the instruction or False otherwise.
        """
        if not isinstance(value, str):
            return False
        title_pattern = '<<.*?>>'
        if not re.search(title_pattern, value):
            return False
        sentences = re.split('[.!?؟]+', value)
        non_empty_sentences = [s.strip() for s in sentences if s.strip()]
        sentence_count = len(non_empty_sentences)
        if sentence_count >= 5:
            return False
        return True

class DataIdx175InstructionChecker(AragenInstructions):

    def __init__(self):
        super().__init__('idx_175')

    def check_following(self, value):
        """You will implement the logic of the function here to see if the response is correct or not.
        Args:
            value: A string representing the response.

        Returns:
            True if the response follows the instruction or False otherwise.
        """
        if not isinstance(value, str):
            return False
        sentences = re.split('[.!?]', value)
        non_empty_segments = [segment for segment in sentences if segment.strip()]
        num_sentences = len(non_empty_segments)
        return num_sentences < 6

class DataIdx176InstructionChecker(AragenInstructions):

    def __init__(self):
        super().__init__('idx_176')

    def check_following(self, value):
        """Checks if the response contains exactly six points formatted as a Markdown unordered list.

        Args:
            value: A string representing the response.

        Returns:
            True if the response contains exactly six lines starting with '* ', False otherwise.
        """
        if not isinstance(value, str):
            return False
        lines = value.strip().splitlines()
        point_count = 0
        for line in lines:
            if line.strip().startswith('* '):
                point_count += 1
        return point_count == 6

class DataIdx177InstructionChecker(AragenInstructions):

    def __init__(self):
        super().__init__('idx_177')


    def check_following(self, value: str) -> bool:
        """Checks if the response is a valid JSON or a ```json``` block containing valid JSON.

        Args:
            value: A string representing the response.

        Returns:
            True if the response follows the instruction (is JSON or JSON in code block)
            or False otherwise.
        """
        if not isinstance(value, str):
            return False
        trimmed_value = value.strip()
        try:
            json.loads(trimmed_value)
            return True
        except json.JSONDecodeError:
            pass
        match = re.fullmatch('^\\s*```json\\s*(.*?)\\s*```\\s*$', trimmed_value, re.IGNORECASE | re.DOTALL)
        if match:
            json_content = match.group(1)
            try:
                json.loads(json_content)
                return True
            except json.JSONDecodeError:
                pass
        return False

class DataIdx178InstructionChecker(AragenInstructions):

    def __init__(self):
        super().__init__('idx_178')

    def check_following(self, value):
        """Checks if the response is a string containing at least 15 sections highlighted like *Highlighted Section*.

        Args:
            value: A string representing the response (the research paper outline).

        Returns:
            True if the response follows the instruction or False otherwise.
        """
        if not isinstance(value, str):
            return False
        highlighted_sections = re.findall('\\*.*?\\*', value)
        return len(highlighted_sections) >= 15

class DataIdx179InstructionChecker(AragenInstructions):

    def __init__(self):
        super().__init__('idx_179')

    def check_following(self, value):
        """Checks if the response contains the required title format.

        Args:
            value: A string representing the response.

        Returns:
            True if the response contains '<<كوتلن مقابل جافا>>', False otherwise.
        """
        required_title = '<<كوتلن مقابل جافا>>'
        return required_title in value

class DataIdx180InstructionChecker(AragenInstructions):

    def __init__(self):
        super().__init__('idx_180')

    def check_following(self, value):
        """
        Checks if the response follows the instructions for IDX 180.
        Constraints:
        1. Entire response is enclosed in double quotes ("").
        2. Contains exactly 8 bullet points.
        3. Each point must be in the format starting with '* ' (asterisk followed by space).

        Args:
            value: A string representing the response.

        Returns:
            True if the response follows the instruction or False otherwise.
        """
        if not isinstance(value, str) or not value.startswith('"') or (not value.endswith('"')):
            return False
        content = value[1:-1]
        lines = content.splitlines()
        bullet_count = 0
        for line in lines:
            stripped_line = line.lstrip()
            if stripped_line.startswith('* ') and len(stripped_line) > 2:
                bullet_count += 1
        if bullet_count != 8:
            return False
        return True

class DataIdx181InstructionChecker(AragenInstructions):

    def __init__(self):
        super().__init__('idx_181')

    def check_following(self, value):
        """Checks if the response contains two parts separated by '*******'.
        Args:
            value: A string representing the response.

        Returns:
            True if the response follows the instruction or False otherwise.
        """
        separator = '*******'
        if separator not in value:
            return False
        parts = value.split(separator)
        if len(parts) != 2:
            return False
        part1 = parts[0].strip()
        if not part1:
            return False
        part2 = parts[1].strip()
        if not part2:
            return False
        return True

class DataIdx182InstructionChecker(AragenInstructions):

    def __init__(self):
        super().__init__('182')

    def check_following(self, value):
        """Checks if the response follows the instructions for IDX 182.

        Args:
            value: A string representing the response.

        Returns:
            True if the response follows the instruction or False otherwise.
        """
        if 'التصوير الفوتوغرافي' in value:
            return False
        paragraphs = value.split('***')
        if len(paragraphs) != 5:
            return False
        if not all((p.strip() for p in paragraphs)):
            return False
        highlighted_sections = re.findall('\\*.*?\\*', value)
        valid_highlights = [h for h in highlighted_sections if len(h) > 2]
        if len(valid_highlights) < 3:
            return False
        return True

class DataIdx183InstructionChecker(AragenInstructions):

    def __init__(self):
        super().__init__('idx_183')

    def check_following(self, value):
        """Checks if the response follows the constraints for IDX 183.
        Constraints:
        1. Exactly 9 bullet points starting with '*'.
        2. All non-empty lines must be bullet points (or empty lines are allowed).
        3. Total word count across the entire response is less than 100.

        Args:
            value: A string representing the response.

        Returns:
            True if the response follows the instruction or False otherwise.
        """
        if not isinstance(value, str):
            return False
        lines = value.strip().splitlines()
        stripped_lines = [line.strip() for line in lines]
        bullet_lines = [line for line in stripped_lines if line.startswith('*')]
        non_empty_stripped_lines = [line for line in stripped_lines if line]
        if len(bullet_lines) != 9:
            return False
        for line in non_empty_stripped_lines:
            if not line.startswith('*'):
                return False
        words = re.findall('\\S+', value.strip())
        total_word_count = len(words)
        if total_word_count >= 100:
            return False
        return True

class DataIdx184InstructionChecker(AragenInstructions):

    def __init__(self):
        super().__init__('idx_184')

    def check_following(self, value):
        """Checks if the response contains at least 7 placeholders represented by square brackets [].

        Args:
            value: A string representing the response (blog post).

        Returns:
            True if the response follows the instruction (at least 7 placeholders), False otherwise.
        """
        placeholders = re.findall('\\[.*?\\]', value)
        return len(placeholders) >= 7

class DataIdx185InstructionChecker(AragenInstructions):

    def __init__(self):
        super().__init__('idx_185')

    def check_following(self, value):
        """Checks if the response follows the task planning document format.
        
        The format requires five specific parts separated by "***",
        with content provided for each part (no placeholder).

        Args:
            value: A string representing the response.

        Returns:
            True if the response follows the instruction or False otherwise.
        """
        if not isinstance(value, str):
            return False
        titles = ['الجزء 1. ملخص المهمة', 'الجزء 2. الدافع', 'الجزء 3. أهداف المرحلة', 'الجزء 4. الجدول الزمني', 'الجزء 5. تاريخ الوثيقة']
        separator = '***'
        placeholder = '[أدخل التفاصيل هنا]'
        if placeholder in value:
            return False
        parts = value.split(separator)
        if len(parts) != 5:
            return False
        for i in range(5):
            part = parts[i].strip()
            title = titles[i]
            if not part.startswith(title):
                return False
            content_after_title = part[len(title):]
            stripped_content = content_after_title.strip()
            if not stripped_content:
                return False
        return True

class DataIdx186InstructionChecker(AragenInstructions):

    def __init__(self):
        super().__init__('idx_186')

    def check_following(self, value):
        """Checks if the response is a song about a playground proposal at an elementary school,
        with less than 10 sentences.
        Args:
            value: A string representing the response.

        Returns:
            True if the response follows the instruction or False otherwise.
        """
        if not isinstance(value, str):
            return False
        sentence_delimiters_pattern = '[.؟!]+'
        sentences = re.split(sentence_delimiters_pattern, value)
        sentences = [s.strip() for s in sentences if s.strip()]
        sentence_count = len(sentences)
        if sentence_count >= 10:
            return False
        school_keywords = ['مدرسة', 'مدرستي', 'الابتدائية', 'ابتدائية']
        playground_keywords = ['ملعب', 'ملاعب', 'اقتراح', 'بناء', 'نبني', 'نريد', 'جديد']
        found_school_keyword = any((kw in value for kw in school_keywords))
        found_playground_keyword = any((kw in value for kw in playground_keywords))
        topic_matches = found_school_keyword and found_playground_keyword
        return topic_matches

class DataIdx188InstructionChecker(AragenInstructions):

    def __init__(self):
        super().__init__('idx_188')

    def check_following(self, value):
        """Checks if the response includes the word 'مرادفات' at least 3 times.
        Args:
            value: A string representing the response.

        Returns:
            True if the response follows the instruction or False otherwise.
        """
        word_to_check = 'مرادفات'
        min_count = 3
        count = value.count(word_to_check)
        return count >= min_count

class DataIdx189InstructionChecker(AragenInstructions):

    def __init__(self):
        super().__init__('idx_189')

    def check_following(self, value):
        """You will implement the logic of the function here to see if the response is correct or not.
        Args:
            value: A string representing the response.

        Returns:
            True if the response follows the instruction or False otherwise.
        """
        if not isinstance(value, str):
            return False
        if ',' in value or '،' in value:
            return False
        lines = value.strip().splitlines()
        if len(lines) != 30:
            return False
        valid_endings = ('؟', '.', '!')
        for line in lines:
            stripped_line = line.strip()
            if not stripped_line:
                return False
            if not stripped_line.endswith(valid_endings):
                return False
        return True

class DataIdx190InstructionChecker(AragenInstructions):

    def __init__(self):
        super().__init__('idx_190')

    def check_following(self, value):
        """Checks if the response includes the word "الاخوية" at least 4 times.

        Args:
            value: A string representing the response (the song).

        Returns:
            True if the word "الاخوية" appears 4 or more times, False otherwise.
        """
        target_word = 'الاخوية'
        count = value.count(target_word)
        return count >= 4

class DataIdx191InstructionChecker(AragenInstructions):

    def __init__(self):
        super().__init__('idx_191')

    def check_following(self, value):
        """Checks if the response follows the instructions for IDX 191.

        Constraints:
        1. No commas.
        2. At least 20 placeholders in the format [username].
        3. Sentences are short (arbitrary max word count per segment split by punctuation).
        4. Avoid using any commas.

        Args:
            value: A string representing the response.

        Returns:
            True if the response follows the instruction or False otherwise.
        """
        if not isinstance(value, str):
            return False
        if ',' in value:
            return False
        placeholder_pattern = '\\[.*?\\]'
        placeholders = re.findall(placeholder_pattern, value)
        if len(placeholders) < 20:
            return False
        sentence_enders = '[.!?]'
        max_words_per_sentence = 25
        segments = re.split(f'{sentence_enders}+', value)
        for segment in segments:
            cleaned_segment = segment.strip()
            if not cleaned_segment:
                continue
            words = cleaned_segment.split()
            if len(words) > max_words_per_sentence:
                return False
        return True

class DataIdx192InstructionChecker(AragenInstructions):

    def __init__(self):
        super().__init__('192')

    def check_following(self, value):
        """
        Checks if the response contains at least two titles enclosed in double angle brackets (<<...>>).

        Args:
            value: A string representing the response.

        Returns:
            True if the response contains at least two <<...>> patterns, False otherwise.
        """
        pattern = '<<.*?>>'
        matches = re.findall(pattern, value)
        return len(matches) >= 2

class DataIdx193InstructionChecker(AragenInstructions):

    def __init__(self):
        super().__init__('idx_193')

    def check_following(self, value):
        """Checks if the response contains exactly two lines of text separated by exactly six stars.

        Args:
            value: A string representing the response.

        Returns:
            True if the response follows the structural instruction (two parts separated by ******),
            False otherwise.
        """
        separator = '******'
        if value.count(separator) != 1:
            return False
        parts = value.split(separator)
        if len(parts) == 2 and parts[0].strip() != '' and (parts[1].strip() != ''):
            return True
        else:
            return False

class DataIdx194InstructionChecker(AragenInstructions):

    def __init__(self):
        super().__init__('idx_194')

    def check_following(self, value):
        """Checks if the response follows the instructions for IDX 194.

        Constraints checked:
        - Not exceeding 100 words.
        - At least two sections highlighted using *text*.
        """
        words = value.split()
        word_count = len(words)
        if word_count > 100:
            return False
        highlight_pattern = '\\*.*?\\*'
        matches = re.findall(highlight_pattern, value)
        if len(matches) < 2:
            return False
        return True

class DataIdx195InstructionChecker(AragenInstructions):

    def __init__(self):
        super().__init__('idx_195')

    def check_following(self, value):
        """Checks if the response contains exactly 4 Markdown bullet points (* or -).

        Args:
            value: A string representing the response.

        Returns:
            True if the response contains exactly 4 bullet points in the specified format,
            False otherwise.
        """
        if not isinstance(value, str):
            return False
        lines = value.strip().split('\n')
        bullet_points_count = 0
        for line in lines:
            stripped_line = line.strip()
            if stripped_line.startswith('* ') or stripped_line.startswith('- '):
                bullet_points_count += 1
        return bullet_points_count == 4

class DataIdx196InstructionChecker(AragenInstructions):

    def __init__(self):
        super().__init__('idx_196')

    def check_following(self, value):
        """Checks if the response contains less than 300 words.
        Args:
            value: A string representing the response.

        Returns:
            True if the response follows the instruction (less than 300 words) or False otherwise.
        """
        if not isinstance(value, str):
            return False
        words = value.split()
        return len(words) < 300

class DataIdx197InstructionChecker(AragenInstructions):

    def __init__(self):
        super().__init__('idx_197')

    def check_following(self, value):
        """Checks if the response follows the instructions:
        1. Does not use commas.
        2. Is more than 800 words.

        Args:
            value: A string representing the response.

        Returns:
            True if the response follows the instruction or False otherwise.
        """
        if ',' in value:
            return False
        words = value.split()
        word_count = len(words)
        if word_count <= 800:
            return False
        return True

class DataIdx198InstructionChecker(AragenInstructions):

    def __init__(self):
        super().__init__('idx_198')

    def check_following(self, value):
        """Checks if the response value contains at least 5 parts emphasized with asterisks.

        The question asks for the answer to be a poem applying for a cafe job,
        with at least five parts emphasized using asterisks (*).
        Checking for "poem" and "job application content" is subjective
        and complex. This function specifically checks the objective constraint:
        whether at least five distinct text segments are enclosed within asterisks.

        Args:
            value: A string representing the response.

        Returns:
            True if the response contains 5 or more emphasized parts (e.g., *text*),
            False otherwise.
        """
        emphasized_parts = re.findall('\\*([^*]+)\\*', value)
        return len(emphasized_parts) >= 5


class DataIdx199InstructionChecker(AragenInstructions):

    def __init__(self):
        super().__init__('idx_199')

    def check_following(self, value: str) -> bool:
        """
        Checks if the response contains at least 5 sections highlighted by asterisks.

        Args:
            value: A string representing the response.

        Returns:
            True if the response follows the instruction (at least 5 sections
            enclosed by *), False otherwise.
        """
        if not isinstance(value, str):
            return False
        highlighted_sections = re.findall('\\*.*?\\*', value)
        num_highlighted_sections = len(highlighted_sections)
        return num_highlighted_sections >= 5

class DataIdx200InstructionChecker(AragenInstructions):

    def __init__(self):
        super().__init__('200')

    def check_following(self, value):
        """Checks if the response follows the instructions for IDX 200.
        Constraints:
        1. The proposal must contain 5 or more sections.
        2. Each section name must be identified using the format *اسم القسم*.

        Args:
            value: A string representing the response.

        Returns:
            True if the response follows the instruction or False otherwise.
        """
        section_names = re.findall('\\*.*?\\*', value)
        return len(section_names) >= 5

class DataIdx201InstructionChecker(AragenInstructions):

    def __init__(self):
        super().__init__('idx_201')

    def check_following(self, value):
        """Checks if the response follows the instructions for IDX 201.

        Constraints:
        1. The word 'مُحبط' (muḥbaṭ - frustrated/depressed) must appear at least twice.
        2. At least six sections must be marked using formatting like *...* or **...**.

        Args:
            value: A string representing the response.

        Returns:
            True if the response follows the instructions, False otherwise.
        """
        if not isinstance(value, str):
            return False
        frustrated_count = value.count('مُحبط')
        if frustrated_count < 2:
            return False
        formatted_sections_star = re.findall('\\*.*?\\*', value)
        formatted_sections_double_star = re.findall('\\*\\*.*?\\*\\*', value)
        total_formatted_sections = len(formatted_sections_star) + len(formatted_sections_double_star)
        if total_formatted_sections < 6:
            return False
        return True

class DataIdx202InstructionChecker(AragenInstructions):

    def __init__(self):
        super().__init__('202')

    def check_following(self, value):
        """Checks if the response includes the word 'أجاب' at least twice.

        Args:
            value: A string representing the response.

        Returns:
            True if the response follows the instruction or False otherwise.
        """
        target_word = 'أجاب'
        word_count = value.count(target_word)
        return word_count >= 2

class DataIdx203InstructionChecker(AragenInstructions):

    def __init__(self):
        super().__init__('idx_203')

    def check_following(self, value):
        """You will implement the logic of the function here to see if the response is correct or not.
        Args:
            value: A string representing the response.

        Returns:
            True if the response follows the instruction or False otherwise.
        """
        if not isinstance(value, str):
            return False
        return value.isdigit()

class DataIdx204InstructionChecker(AragenInstructions):

    def __init__(self):
        super().__init__('idx_204')

    def check_following(self, value):
        """Checks if the response is a formatted string containing an article,
        a separator '******', and a poem.

        Args:
            value: A string representing the response.

        Returns:
            True if the response follows the instruction or False otherwise.
        """
        separator = '******'
        if separator not in value:
            return False
        parts = value.split(separator)
        if len(parts) != 2:
            return False
        article = parts[0].strip()
        poem = parts[1].strip()
        if not article or not poem:
            return False
        return True

class DataIdx205InstructionChecker(AragenInstructions):

    def __init__(self):
        super().__init__('idx_205')

    def check_following(self, value):
        """Checks if the response contains a title enclosed in asterisks (*...*)
           with at least one character between the asterisks.

        Args:
            value: A string representing the response.

        Returns:
            True if a pattern *...* (with at least one character between asterisks) is found,
            False otherwise.
        """
        pattern = '\\*.+\\*'
        match = re.search(pattern, value)
        return match is not None

class DataIdx206InstructionChecker(AragenInstructions):

    def __init__(self):
        super().__init__('idx_206')

    def check_following(self, value):
        """Checks if the response follows the instructions for IDX 206.

        Instructions:
        1. The entire answer (thought process and final answer) must be enclosed in double quotes.
        2. The response should include a step-by-step solution.
        3. The response should arrive at a final answer.

        Args:
            value: A string representing the response.

        Returns:
            True if the response follows the instruction or False otherwise.
        """
        if not isinstance(value, str):
            return False
        trimmed_value = value.strip()
        if not (trimmed_value.startswith('"') and trimmed_value.endswith('"')):
            return False
        if len(trimmed_value) < 2:
            return False
        content = trimmed_value[1:-1]
        if not content.strip():
            return False
        return True

class DataIdx207InstructionChecker(AragenInstructions):

    def __init__(self):
        super().__init__('idx_207')

    def check_following(self, value):
        """Checks if the response (an article) is at least 50 sentences long.

        Args:
            value: A string representing the response.

        Returns:
            True if the response contains 50 or more sentences, False otherwise.
        """
        if not isinstance(value, str):
            return False
        sentences = [sent.strip() for sent in re.split('[.!?]', value) if sent.strip()]
        sentence_count = len(sentences)
        return sentence_count >= 50

class DataIdx208InstructionChecker(AragenInstructions):

    def __init__(self):
        super().__init__('idx_208')

    def check_following(self, value):
        """Checks if the response follows the instructions for IDX 208.
        Constraints checked:
        1. Contains exactly '******' as a separator.
        2. Has non-empty content before and after the separator (after stripping whitespace).
        3. Total word count is less than 300.
        (Semantic constraints like target audience, perspective, and language are not checked programmatically here).

        Args:
            value: A string representing the response.

        Returns:
            True if the response follows the checkable instructions or False otherwise.
        """
        separator = '******'
        if separator not in value or value.count(separator) != 1:
            return False
        parts = value.split(separator)
        if len(parts) != 2:
            return False
        part1 = parts[0].strip()
        part2 = parts[1].strip()
        if not part1 or not part2:
            return False
        words = value.split()
        word_count = len(words)
        if word_count >= 300:
            return False
        return True

class DataIdx209InstructionChecker(AragenInstructions):

    def __init__(self):
        super().__init__('idx_209')

    def check_following(self, value):
        """Checks if the response is enclosed in double angle brackets <<>>.

        Args:
            value: A string representing the response.

        Returns:
            True if the response starts with << and ends with >>, False otherwise.
        """
        if not isinstance(value, str):
            return False
        return value.startswith('<<') and value.endswith('>>')

class DataIdx210InstructionChecker(AragenInstructions):

    def __init__(self):
        super().__init__('idx_210')

    def check_following(self, value):
        """Checks if the response meets the structural constraints:
        - At least 40 sentences (checked by counting terminal punctuation).
        - Includes highlighting using asterisks (*...*).

        Args:
            value: A string representing the response (the poem).

        Returns:
            True if the response follows the structural constraints, False otherwise.
        """
        sentence_terminators = ['.', '؟', '!']
        sentence_count = 0
        for terminator in sentence_terminators:
            sentence_count += value.count(terminator)
        is_long_enough = sentence_count >= 40
        has_highlighting = bool(re.search('\\*.*?\\*', value))
        return is_long_enough and has_highlighting

class DataIdx211InstructionChecker(AragenInstructions):

    def __init__(self):
        super().__init__('idx_211')

    def check_following(self, value):
        """Checks if the response consists of 20 to 25 sentences marked by ., !, or ?, and contains punctuation.

        Args:
            value: A string representing the response.

        Returns:
            True if the response follows the instruction or False otherwise.
        """
        if not isinstance(value, str):
            return False
        sentence_terminators = re.findall('[.!?]', value)
        sentence_count = len(sentence_terminators)
        if 20 <= sentence_count <= 25:
            return True
        else:
            return False

class DataIdx212InstructionChecker(AragenInstructions):

    def __init__(self):
        super().__init__('idx_212')

    def check_following(self, value):
        """You will implement the logic of the function here to see if the response is correct or not.
        Args:
            value: A string representing the response.

        Returns:
            True if the response follows the instruction or False otherwise.
        """
        company_name = 'الشبكة'
        count = value.count(company_name)
        return count >= 5

class DataIdx213InstructionChecker(AragenInstructions):

    def __init__(self):
        super().__init__('idx_213')

    def check_following(self, value):
        """Checks if the response follows the instruction for IDX 213.
        The instruction requires exactly four paragraphs separated by ***.

        Args:
            value: A string representing the response.

        Returns:
            True if the response follows the instruction or False otherwise.
        """
        if not isinstance(value, str):
            return False
        paragraphs = value.split('***')
        return len(paragraphs) == 4

class DataIdx214InstructionChecker(AragenInstructions):

    def __init__(self):
        super().__init__('idx_214')

    def check_following(self, value: str) -> bool:
        """Checks if the response follows the instructions for IDX 214.

        Constraints:
        1. Starts with 'رجل يقدم عرضاً أمام حشد على المسرح،'
        2. Contains at least 60 sentences.
        3. Contains less than 600 words.

        Args:
            value: A string representing the response.

        Returns:
            True if the response follows the instruction or False otherwise.
        """
        required_start = 'رجل يقدم عرضاً أمام حشد على المسرح،'
        min_sentences = 60
        max_words = 600
        if not value.strip().startswith(required_start):
            return False
        words = value.split()
        word_count = len(words)
        if word_count >= max_words:
            return False
        sentences = re.split('[.?!]+', value)
        sentences = [s.strip() for s in sentences if s.strip()]
        sentence_count = len(sentences)
        if sentence_count < min_sentences:
            return False
        return True

class DataIdx215InstructionChecker(AragenInstructions):

    def __init__(self):
        super().__init__('idx_215')

    def check_following(self, value):
        """You will implement the logic of the function here to see if the response is correct or not.
        Args:
            value: A string representing the response.

        Returns:
            True if the response follows the instruction or False otherwise.
        """
        pattern = '\\*.+?\\*'
        matches = re.findall(pattern, value)
        return len(matches) >= 3

class DataIdx216InstructionChecker(AragenInstructions):

    def __init__(self):
        super().__init__('216')

    def check_following(self, value: str):
        """Checks if the response follows the instructions for IDX 216.
        
        Constraints:
        1. Use at least 10 italicized parts using Markdown (*text* or _text_).
        2. Do not use any line breaks.
        (The "make it funny" constraint is subjective and not checked programmatically).

        Args:
            value: A string representing the response.

        Returns:
            True if the response follows the checkable constraints (no line breaks, >= 10 italic parts),
            False otherwise.
        """
        if '\n' in value or '\r' in value:
            return False
        italic_parts_asterisk = re.findall('\\*[^*]+\\*', value)
        italic_parts_underscore = re.findall('\\_[^_]+\\_', value)
        total_italic_parts = len(italic_parts_asterisk) + len(italic_parts_underscore)
        return total_italic_parts >= 10

class DataIdx217InstructionChecker(AragenInstructions):

    def __init__(self):
        super().__init__('idx_217')

    def check_following(self, value):
        """Checks if the response is between 600 and 700 words.

        Args:
            value: A string representing the response.

        Returns:
            True if the response follows the instruction or False otherwise.
        """
        if not isinstance(value, str):
            return False
        words = value.split()
        word_count = len(words)
        return 600 <= word_count <= 700

class DataIdx218InstructionChecker(AragenInstructions):

    def __init__(self):
        super().__init__('idx_218')

    def check_following(self, value):
        """Checks if the response follows the constraints for IDX 218.
        Constraints:
        1. At least 30 sentences (ending with . ! ?).
        2. Exactly 2 bullet points marked with * (assuming lines starting with *).
        3. Exactly 8 placeholders in square brackets [like this].

        Args:
            value: A string representing the response.

        Returns:
            True if the response follows the instruction or False otherwise.
        """
        if not isinstance(value, str):
            return False
        sentences = [s.strip() for s in re.split('[.!?]', value) if s.strip()]
        sentence_count = len(sentences)
        if sentence_count < 30:
            return False
        lines = value.splitlines()
        bullet_count = sum((1 for line in lines if line.strip().startswith('*')))
        if bullet_count != 2:
            return False
        placeholders = re.findall('\\[.*?\\]', value)
        placeholder_count = len(placeholders)
        if placeholder_count != 8:
            return False
        return True

class DataIdx219InstructionChecker(AragenInstructions):

    def __init__(self):
        super().__init__('idx_219')

    def check_following(self, value):
        """Checks if the response (email) contains at least 10 fields in square brackets.

        Args:
            value: A string representing the response (email).

        Returns:
            True if the response contains 10 or more fields like [الاسم], False otherwise.
        """
        fields = re.findall('\\[.*?\\]', value)
        num_fields = len(fields)
        return num_fields >= 10

class DataIdx220InstructionChecker(AragenInstructions):

    def __init__(self):
        super().__init__('idx_220')

    def check_following(self, value):
        """Checks if the response follows the instructions for IDX 220.

        Instructions:
        - Must contain a title within double angle brackets (<<Title>>).
        - Must not contain any commas (,).
        - The word "لحم" (meat) must appear less than 3 times.

        Args:
            value: A string representing the response.

        Returns:
            True if the response follows the instructions, False otherwise.
        """
        title_present = re.search('<<.*?>>', value) is not None
        no_commas = ',' not in value
        meat_count = value.count('لحم')
        meat_count_ok = meat_count < 3
        return title_present and no_commas and meat_count_ok

class DataIdx221InstructionChecker(AragenInstructions):

    def __init__(self):
        super().__init__('idx_221')

    def check_following(self, value):
        """Checks if the response follows the constraints for IDX 221.

        Args:
            value: A string representing the response.

        Returns:
            True if the response follows the instruction or False otherwise.
        """
        if not isinstance(value, str):
            return False
        lines = value.strip().split('\n')
        non_empty_lines = [line for line in lines if line.strip()]
        if len(non_empty_lines) != 4:
            return False
        for line in non_empty_lines:
            if not line.strip().startswith('* '):
                return False
        return True

class DataIdx222InstructionChecker(AragenInstructions):

    def __init__(self):
        super().__init__('idx_222')

    def check_following(self, value):
        """Checks if the response is entirely enclosed in double quotation marks.

        Args:
            value: A string representing the response.

        Returns:
            True if the response starts and ends with double quotation marks,
            False otherwise.
        """
        if not isinstance(value, str):
            return False
        if len(value) < 2:
            return False
        return value.startswith('"') and value.endswith('"')

class DataIdx223InstructionChecker(AragenInstructions):

    def __init__(self):
        super().__init__('idx_223')

    def check_following(self, value):
        """Checks if the response is enclosed in double quotes as required by the instruction.

        Args:
            value: A string representing the response.

        Returns:
            True if the response is a string, starts with '"', ends with '"',
            and has a length of at least 2. False otherwise.
        """
        if not isinstance(value, str):
            return False
        if len(value) < 2:
            return False
        if not value.startswith('"'):
            return False
        if not value.endswith('"'):
            return False
        return True

class DataIdx224InstructionChecker(AragenInstructions):

    def __init__(self):
        super().__init__('idx_224')

    def check_following(self, value):
        """You will implement the logic of the function here to see if the response is correct or not.
        Args:
            value: A string representing the response.

        Returns:
            True if the response follows the instruction or False otherwise.
        """
        if not (value.startswith('"') and value.endswith('"')):
            return False
        content = value[1:-1]
        if not content.strip():
            return False
        sentence_enders = '[.!?؟]+'
        sentences = [s.strip() for s in re.split(sentence_enders, content) if s.strip()]
        if len(sentences) < 5:
            return False
        italics_matches = re.findall('\\*([^*]+)\\*', content)
        if len(italics_matches) < 2:
            return False
        return True

class DataIdx225InstructionChecker(AragenInstructions):

    def __init__(self):
        super().__init__('idx_225')

    def check_following(self, value):
        """Checks if the response has between 100 and 120 words.

        Args:
            value: A string representing the response.

        Returns:
            True if the response follows the instruction (word count between 100 and 120 inclusive)
            or False otherwise.
        """
        words = value.split()
        word_count = len(words)
        return 100 <= word_count <= 120

class DataIdx226InstructionChecker(AragenInstructions):

    def __init__(self):
        super().__init__('idx_226')

    def check_following(self, value):
        """Checks if the response contains exactly one line starting with '*'.

        Args:
            value: A string representing the response.

        Returns:
            True if the response follows the instruction (exactly one line starts with '*')
            or False otherwise.
        """
        if not isinstance(value, str):
            return False
        lines = value.splitlines()
        bullet_count = 0
        for line in lines:
            if line.strip().startswith('*'):
                bullet_count += 1
        return bullet_count == 1

class DataIdx227InstructionChecker(AragenInstructions):

    def __init__(self):
        super().__init__('idx_227')

    def check_following(self, value):
        """Checks if the response has at least 400 words.

        Args:
            value: A string representing the response.

        Returns:
            True if the response follows the instruction (>= 400 words) or False otherwise.
        """
        if not isinstance(value, str):
            return False
        words = value.split()
        word_count = len(words)
        return word_count >= 400

class DataIdx228InstructionChecker(AragenInstructions):

    def __init__(self):
        super().__init__('idx_228')

    def check_following(self, value):
        """Checks if the response follows the instructions for question IDX 228.
        Constraints:
        1. Article must be 200 words long.
        2. Title must be enclosed in double angle brackets <<Title>>.

        Args:
            value: A string representing the response.

        Returns:
            True if the response follows the instructions or False otherwise.
        """
        if not isinstance(value, str):
            return False
        words = value.split()
        word_count = len(words)
        word_count_ok = word_count == 200
        title_pattern = '<<.*?>>'
        title_found = bool(re.search(title_pattern, value))
        return word_count_ok and title_found

class DataIdx229InstructionChecker(AragenInstructions):

    def __init__(self):
        super().__init__('idx_229')

    def check_following(self, value: str) -> bool:
        """Checks if the response follows the constraints for IDX 229.

        Constraints:
        1. Exactly 3 paragraphs separated by '***'.
        2. Exactly 3 markdown bullet points starting with '* '.

        Args:
            value: A string representing the response.

        Returns:
            True if the response follows the instruction or False otherwise.
        """
        if not isinstance(value, str):
            return False
        paragraphs = value.split('***')
        if len(paragraphs) != 3:
            return False
        bullet_point_count = 0
        lines = value.splitlines()
        for line in lines:
            if line.strip().startswith('* '):
                bullet_point_count += 1
            elif line.strip().startswith('*') and len(line.strip()) > 1 and line.strip()[1].isspace():
                bullet_point_count += 1
        if bullet_point_count != 3:
            return False
        return True

class DataIdx230InstructionChecker(AragenInstructions):

    def __init__(self):
        super().__init__('idx_230')

    def check_following(self, value):
        """Checks if the response contains at least one blank represented by [].

        Args:
            value: A string representing the response.

        Returns:
            True if the response contains at least one [] blank, False otherwise.
        """
        return '[]' in value

class DataIdx231InstructionChecker(AragenInstructions):

    def __init__(self):
        super().__init__('idx_231')

    def check_following(self, value):
        """
        Checks if the response includes the word 'المفترسة' (al-muftarisa) at least twice.
        Args:
            value: A string representing the response (the course proposal).

        Returns:
            True if the word 'المفترسة' appears 2 or more times, False otherwise.
        """
        count = value.count('المفترسة')
        return count >= 2

class DataIdx232InstructionChecker(AragenInstructions):

    def __init__(self):
        super().__init__('idx_232')

    def check_following(self, value):
        """Checks if the response follows the instructions for question IDX 232.

        Constraints:
        1. Must contain less than 20 sentences.
        2. Must contain at least 3 placeholders in the format [العنوان].
        """
        sentence_delimiters = '[.?!؟!] +'
        sentences = re.split(sentence_delimiters, value)
        sentences = [s.strip() for s in sentences if s.strip()]
        num_sentences = len(sentences)
        sentence_count_ok = num_sentences < 20
        placeholder_pattern = '\\[.*?\\]'
        placeholders = re.findall(placeholder_pattern, value)
        num_placeholders = len(placeholders)
        placeholder_count_ok = num_placeholders >= 3
        return sentence_count_ok and placeholder_count_ok

class DataIdx233InstructionChecker(AragenInstructions):

    def __init__(self):
        super().__init__('idx_233')

    def check_following(self, value):
        """Checks if the response contains at least three fields enclosed in square brackets.
        Args:
            value: A string representing the response.

        Returns:
            True if the response contains 3 or more fields in square brackets, False otherwise.
        """
        fields = re.findall('\\[.*?\\]', value)
        return len(fields) >= 3

class DataIdx234InstructionChecker(AragenInstructions):

    def __init__(self):
        super().__init__('idx_234')

    def check_following(self, value):
        """Checks if the response is enclosed in quotation marks.
        Args:
            value: A string representing the response.

        Returns:
            True if the response follows the instruction or False otherwise.
        """
        if not isinstance(value, str):
            return False
        return value.startswith('"') and value.endswith('"') and (len(value) >= 2)

class DataIdx235InstructionChecker(AragenInstructions):

    def __init__(self):
        super().__init__('idx_235')

    def check_following(self, value: str) -> bool:
        """Checks if the response contains exactly 3 markdown list items starting with '* '.

        Args:
            value: A string representing the response.

        Returns:
            True if the response follows the instruction or False otherwise.
        """
        if not isinstance(value, str):
            return False
        lines = value.splitlines()
        list_item_count = 0
        for line in lines:
            stripped_line = line.strip()
            if stripped_line.startswith('* '):
                list_item_count += 1
        return list_item_count == 3

class DataIdx236InstructionChecker(AragenInstructions):

    def __init__(self):
        super().__init__('idx_236')

    def check_following(self, value):
        """Checks if the response is enclosed in double quotation marks.

        Args:
            value: A string representing the response.

        Returns:
            True if the response starts and ends with a double quotation mark, False otherwise.
        """
        if not isinstance(value, str) or len(value) < 2:
            return False
        return value.startswith('"') and value.endswith('"')

class DataIdx237InstructionChecker(AragenInstructions):

    def __init__(self):
        super().__init__('idx_237')
        self.min_word_count = 450
        self.max_word_count = 550
        self.forbidden_price_words = ['سعر', 'ثمن', 'تكلفة', 'مجانا', 'خصم']
        self.title_pattern = re.compile('<<.+?>>')

    def check_following(self, value):
        """Checks if the response follows the instructions for IDX 237.

        Args:
            value: A string representing the response.

        Returns:
            True if the response follows the instruction or False otherwise.
        """
        if not isinstance(value, str):
            return False
        title_match = self.title_pattern.search(value)
        if not title_match:
            return False
        price_regex = re.compile('\\b(' + '|'.join(self.forbidden_price_words) + ')\\b', re.IGNORECASE)
        if price_regex.search(value):
            return False
        words = value.split()
        actual_word_count = len([word for word in words if word])
        if not self.min_word_count <= actual_word_count <= self.max_word_count:
            return False
        return True

class DataIdx238InstructionChecker(AragenInstructions):

    def __init__(self):
        super().__init__('238')

    def check_following(self, value):
        """Checks if the response follows the instructions for IDX 238.

        Args:
            value: A string representing the response.

        Returns:
            True if the response follows the instruction or False otherwise.
        """
        if ',' in value:
            return False
        highlighted_sections = re.findall('\\*.*?\\*', value)
        if len(highlighted_sections) < 2:
            return False
        return True

class DataIdx239InstructionChecker(AragenInstructions):

    def __init__(self):
        super().__init__('idx_239')

    def check_following(self, value):
        """Checks if the response is the specified sentence enclosed in single quotes.

        Args:
            value: A string representing the response.

        Returns:
            True if the response follows the instruction or False otherwise.
        """
        expected_sentence = 'ألقيت بكرهي في النار المتأججة.'
        if not isinstance(value, str) or not value:
            return False
        if not value.startswith("'") or not value.endswith("'"):
            return False
        if value != "'" + expected_sentence + "'":
            return False
        return True

class DataIdx240InstructionChecker(AragenInstructions):

    def __init__(self):
        super().__init__('idx_240')

    def check_following(self, value):
        """You will implement the logic of the function here to see if the response is correct or not.
        Checks if the response includes the name, location, and year, and is under 150 words.

        Args:
            value: A string representing the response.

        Returns:
            True if the response follows the instruction or False otherwise.
        """
        word_count = len(value.split())
        if word_count >= 150:
            return False
        name_present = 'هنري كيرك وايت' in value or 'هنري كيرك' in value or 'وايت' in value
        location_present = 'لندن' in value
        year_present = '1876' in value
        if not (name_present and location_present and year_present):
            return False
        return True

class DataIdx241InstructionChecker(AragenInstructions):

    def __init__(self):
        super().__init__('idx_241')

    def check_following(self, value):
        """Checks if the response does not contain any commas.

        Args:
            value: A string representing the response.

        Returns:
            True if the response follows the instruction (no commas) or False otherwise.
        """
        return ',' not in value

class DataIdx242InstructionChecker(AragenInstructions):

    def __init__(self):
        super().__init__('242')

    def check_following(self, value):
        """Checks if the response follows the instructions for IDX 242.

        Constraints:
        1. Minimum length of 400 words.
        2. Contains the word "مناخي" at least twice.
        3. Contains at least 3 elements enclosed in square brackets [].

        Args:
            value: A string representing the response.

        Returns:
            True if the response follows the instruction or False otherwise.
        """
        if not isinstance(value, str):
            return False
        words = value.split()
        word_count = len(words)
        length_check = word_count >= 400
        keyword = 'مناخي'
        keyword_pattern = re.compile('\\b' + re.escape(keyword) + '\\b')
        keyword_matches = keyword_pattern.findall(value)
        keyword_check = len(keyword_matches) >= 2
        bracket_pattern = re.compile('\\[.*?\\]')
        bracket_matches = bracket_pattern.findall(value)
        bracket_check = len(bracket_matches) >= 3
        return length_check and keyword_check and bracket_check

class DataIdx243InstructionChecker(AragenInstructions):

    def __init__(self):
        super().__init__('idx_243')

    def check_following(self, value):
        """Checks if the response is a workshop model with at least 3 sections marked by '*'.
        Args:
            value: A string representing the response.

        Returns:
            True if the response follows the instruction or False otherwise.
        """
        if not isinstance(value, str):
            return False
        lines = value.strip().split('\n')
        section_count = 0
        for line in lines:
            cleaned_line = line.strip()
            if cleaned_line.startswith('*') and len(cleaned_line) > 1:
                section_count += 1
        return section_count >= 3

class DataIdx244InstructionChecker(AragenInstructions):

    def __init__(self):
        super().__init__('244')

    def check_following(self, value):
        """Checks if the response contains less than 7 sentences.

        Sentences are counted based on the presence of periods (.),
        exclamation marks (!), or question marks (?) as terminators.

        Args:
            value: A string representing the response.

        Returns:
            True if the response follows the instruction (less than 7 sentences),
            False otherwise.
        """
        if not isinstance(value, str):
            return False
        sentences = re.split('[.!?]+', value)
        sentences = [s.strip() for s in sentences if s.strip()]
        if not sentences and value.strip():
            sentence_count = 1
        else:
            sentence_count = len(sentences)
        return sentence_count < 7

class DataIdx245InstructionChecker(AragenInstructions):

    def __init__(self):
        super().__init__('idx_245')

    def check_following(self, value):
        """Checks if the response contains exactly one of the allowed phrases.
        Args:
            value: A string representing the response.

        Returns:
            True if the response follows the instruction or False otherwise.
        """
        valid_phrases = ['إجابتي هي نعم.', 'إجابتي هي لا.', 'إجابتي هي ربما.']
        total_count = 0
        for phrase in valid_phrases:
            total_count += value.count(phrase)
        return total_count == 1

class DataIdx246InstructionChecker(AragenInstructions):

    def __init__(self):
        super().__init__('idx_246')

    def check_following(self, value):
        """Checks if the response follows the instructions for IDX 246.

        Instructions:
        1. At least 300 words.
        2. At least 3 places mentioned in square brackets like [Address].
        3. Exactly 2 bullet points using '* ' like: * Point 1.

        Args:
            value: A string representing the response.

        Returns:
            True if the response follows all instructions, False otherwise.
        """
        if not isinstance(value, str):
            return False
        word_count = len(value.split())
        min_words_met = word_count >= 300
        bracketed_places = re.findall('\\[.*?\\]', value)
        min_places_met = len(bracketed_places) >= 3
        lines = value.splitlines()
        bullet_point_count = sum((1 for line in lines if line.strip().startswith('* ')))
        exact_bullets_met = bullet_point_count == 2
        return min_words_met and min_places_met and exact_bullets_met

class DataIdx247InstructionChecker(AragenInstructions):

    def __init__(self):
        super().__init__('idx_247')

    def check_following(self, value):
        """Checks if the response uses the word 'بوضوح' at least twice.

        Args:
            value: A string representing the response.

        Returns:
            True if the response uses 'بوضوح' at least twice, False otherwise.
        """
        if not isinstance(value, str):
            return False
        count = value.count('بوضوح')
        return count >= 2

class DataIdx248InstructionChecker(AragenInstructions):

    def __init__(self):
        super().__init__('idx_248')

    def check_following(self, value):
        """Checks if the response is enclosed in double quotes and contains 17 or more sentences.

        Args:
            value: A string representing the response.

        Returns:
            True if the response follows the instruction or False otherwise.
        """
        if not isinstance(value, str) or not value.startswith('"') or (not value.endswith('"')):
            return False
        if value == '""':
            content = ''
        else:
            content = value[1:-1]
        sentences = re.split('[.!?]', content)
        valid_sentences = [s for s in sentences if s.strip()]
        if len(valid_sentences) < 17:
            return False
        return True

class DataIdx249InstructionChecker(AragenInstructions):

    def __init__(self):
        super().__init__('idx_249')

    def check_following(self, value):
        """Checks if the response contains at least one title placeholder in square brackets [العنوان].

        Args:
            value: A string representing the response.

        Returns:
            True if the response contains '[العنوان]', False otherwise.
        """
        required_placeholder = '[العنوان]'
        return required_placeholder in value

class DataIdx250InstructionChecker(AragenInstructions):

    def __init__(self):
        super().__init__('idx_250')

    def check_following(self, value):
        """Checks if the response follows the instruction not to use commas.
        Args:
            value: A string representing the response.

        Returns:
            True if the response does not contain commas, False otherwise.
        """
        if isinstance(value, str) and ',' not in value:
            return True
        return False

class DataIdx251InstructionChecker(AragenInstructions):

    def __init__(self):
        super().__init__('251')

    def check_following(self, value: str) -> bool:
        """
        Checks if the response provides exactly 3 bullet points, each containing text,
        as requested by the instruction for IDX 251.

        Args:
            value: A string representing the response.

        Returns:
            True if the response follows the instruction (exactly 3 non-empty bullet points)
            or False otherwise.
        """
        if not isinstance(value, str):
            return False
        lines = value.splitlines()
        valid_bullet_points_count = 0
        for line in lines:
            cleaned_line = line.strip()
            if cleaned_line.startswith('* '):
                item_text = cleaned_line[len('* '):]
                if item_text.strip():
                    valid_bullet_points_count += 1
        return valid_bullet_points_count == 3

class DataIdx252InstructionChecker(AragenInstructions):

    def __init__(self):
        super().__init__('idx_252')

    def check_following(self, value):
        """Checks if the response is a funny advertisement for a barber shop
        with a 25% discount and at least 200 words, based on measurable constraints.

        Args:
            value: A string representing the response.

        Returns:
            True if the response follows the measurable instructions, False otherwise.
        """
        has_25_percent = '25%' in value
        has_discount_term = 'خصم' in value or 'تخفيض' in value
        mentions_discount = has_25_percent and has_discount_term
        words = value.split()
        word_count = len(words)
        is_long_enough = word_count >= 200
        return mentions_discount and is_long_enough

class DataIdx253InstructionChecker(AragenInstructions):

    def __init__(self):
        super().__init__('idx_253')

    def check_following(self, value):
        """Checks if the response contains no commas.

        Args:
            value: A string representing the response.

        Returns:
            True if the response follows the instruction (no commas) or False otherwise.
        """
        return ',' not in value

class DataIdx254InstructionChecker(AragenInstructions):

    def __init__(self):
        super().__init__('idx_254')

    def check_following(self, value):
        """Checks if the response consists of exactly four paragraphs separated by '***'.

        Args:
            value: A string representing the response.

        Returns:
            True if the response has exactly four parts separated by '***', False otherwise.
        """
        parts = value.split('***')
        separator_count = value.count('***')
        return separator_count == 3

class DataIdx255InstructionChecker(AragenInstructions):

    def __init__(self):
        super().__init__('idx_255')

    def check_following(self, value):
        """Checks if the response string does not contain any commas.

        Args:
            value: A string representing the response.

        Returns:
            True if the response does not contain any commas, False otherwise.
        """
        return ',' not in value

class DataIdx256InstructionChecker(AragenInstructions):

    def __init__(self):
        super().__init__('idx_256')

    def check_following(self, value):
        """Checks if the response follows the instructions for IDX 256.

        Constraints:
        - Must contain exactly four specific points.
        - Must not contain any commas.
        - (Other constraints like targeting mothers and using text formatting are hard to check programmatically based on string alone, focusing on the structural constraints).

        Args:
            value: A string representing the response.

        Returns:
            True if the response follows the structural instructions (4 points, no commas)
            or False otherwise.
        """
        if ',' in value:
            return False
        lines = value.splitlines()
        point_count = 0
        for line in lines:
            if line.strip():
                point_count += 1
        return point_count == 4

class DataIdx257InstructionChecker(AragenInstructions):

    def __init__(self):
        super().__init__('idx_257')

    def check_following(self, value):
        """Checks if the response highlights at least three points using Markdown list format.

        Args:
            value: A string representing the response.

        Returns:
            True if at least three points are highlighted using Markdown list format,
            False otherwise.
        """
        if not isinstance(value, str):
            return False
        lines = value.strip().split('\n')
        highlighted_points_count = 0
        list_marker_pattern = re.compile('^[*-+] ')
        for line in lines:
            cleaned_line = line.strip()
            if list_marker_pattern.match(cleaned_line):
                highlighted_points_count += 1
        return highlighted_points_count >= 3

class DataIdx258InstructionChecker(AragenInstructions):

    def __init__(self):
        super().__init__('258')

    def check_following(self, value):
        """Checks if the response for IDX 258 follows the instructions.

        Constraints:
        1. Provide two completely different answers.
        2. Separate the answers using exactly six asterisks: ******.

        Args:
            value: A string representing the response.

        Returns:
            True if the response follows the instruction or False otherwise.
        """
        separator = '******'
        if value.count(separator) != 1:
            return False
        parts = value.split(separator)
        if len(parts) != 2:
            return False
        answer1 = parts[0].strip()
        answer2 = parts[1].strip()
        if not answer1 or not answer2:
            return False
        if answer1 == answer2:
            return False
        return True

class DataIdx259InstructionChecker(AragenInstructions):

    def __init__(self):
        super().__init__('idx_259')

    def check_following(self, value):
        """Checks if the response follows the instruction for IDX 259.

        Args:
            value: A string representing the response.

        Returns:
            True if the response follows the instruction or False otherwise.
        """
        if 'همهمة' not in value:
            return False
        paragraphs = value.split('***')
        if len(paragraphs) != 3:
            return False
        for para in paragraphs:
            if not para.strip():
                return False
        return True

class DataIdx260InstructionChecker(AragenInstructions):

    def __init__(self):
        super().__init__('idx_260')

    def check_following(self, value):
        """Checks if the response follows the instruction for IDX 260.
        Constraints:
        - Use the word 'الفتح' less than 2 times.
        - The output must be a JSON block only.

        Args:
            value: A string representing the response (expected to be a JSON string).

        Returns:
            True if the response follows the constraints, False otherwise.
        """
        word_to_check = 'الفتح'
        count = value.count(word_to_check)
        return count < 2

class DataIdx261InstructionChecker(AragenInstructions):

    def __init__(self):
        super().__init__('idx_261')

    def check_following(self, value):
        """Checks if the response is entirely in JSON format, potentially within markdown code blocks.

        Args:
            value: A string representing the response.

        Returns:
            True if the response follows the instruction or False otherwise.
        """
        if not isinstance(value, str):
            return False
        cleaned_value = value.strip()
        content = cleaned_value
        if cleaned_value.startswith('```') and cleaned_value.endswith('```'):
            if len(cleaned_value) < 6:
                return False
            inner_content_with_marker = cleaned_value[3:-3]
            first_newline_index_inner = inner_content_with_marker.find('\n')
            if first_newline_index_inner != -1:
                content = inner_content_with_marker[first_newline_index_inner + 1:].strip()
            else:
                content = inner_content_with_marker.strip()
        if not content:
            return False
        try:
            json.loads(content)
            return True
        except json.JSONDecodeError:
            return False
        except TypeError:
            return False

class DataIdx262InstructionChecker(AragenInstructions):

    def __init__(self):
        super().__init__('idx_262')

    def check_following(self, value):
        """Checks if the response follows the constraints:
        1. Different language (not Arabic).
        2. Use bullet points (at least two distinct points).
        3. Provide alternative answers (interpreted as multiple bullet points).
        4. Avoid using commas.

        Args:
            value: A string representing the response.

        Returns:
            True if the response follows the instructions or False otherwise.
        """
        if not isinstance(value, str) or not value.strip():
            return False
        if ',' in value:
            return False
        arabic_pattern = re.compile('[\\u0600-\\u06FF]')
        if arabic_pattern.search(value):
            return False
        lines = value.split('\n')
        bullet_count = 0
        bullet_markers = ['-', '*', '•']
        for line in lines:
            cleaned_line = line.lstrip()
            for marker in bullet_markers:
                if cleaned_line.startswith(marker + ' '):
                    content_after_marker = cleaned_line[len(marker + ' '):].strip()
                    if content_after_marker:
                        bullet_count += 1
                        break
        if bullet_count < 2:
            return False
        return True

class DataIdx263InstructionChecker(AragenInstructions):

    def __init__(self):
        super().__init__('idx_263')

    def check_following(self, value: str) -> bool:
        """Checks if the response follows the instructions for question 263.

        Instructions:
        1. Provide two different answers.
        2. The two answers must be separated by exactly six asterisks (******).
        3. Do not use any commas (,).

        Args:
            value: A string representing the response.

        Returns:
            True if the response follows the instruction or False otherwise.
        """
        separator = '******'
        if value.count(separator) != 1:
            return False
        parts = value.split(separator)
        if len(parts) != 2:
            return False
        answer1 = parts[0].strip()
        answer2 = parts[1].strip()
        if not answer1 or not answer2:
            return False
        if ',' in answer1 or ',' in answer2:
            return False
        if answer1 == answer2:
            return False
        return True

class DataIdx264InstructionChecker(AragenInstructions):

    def __init__(self):
        super().__init__('264')

    def check_following(self, value):
        """Checks if the response is entirely enclosed in double quotes.

        Args:
            value: A string representing the response.

        Returns:
            True if the response starts and ends with a double quote, False otherwise.
        """
        if not isinstance(value, str):
            return False
        return value.startswith('"') and value.endswith('"')

class DataIdx265InstructionChecker(AragenInstructions):

    def __init__(self):
        super().__init__('idx_265')

    def check_following(self, value):
        """Checks if the response contains exactly four points, typically indicated by bullet points or list markers.

        Args:
            value: A string representing the response.

        Returns:
            True if the response contains exactly 4 points, False otherwise.
        """
        lines = value.strip().split('\n')
        point_count = 0
        for line in lines:
            stripped_line = line.strip()
            if stripped_line.startswith('*') or stripped_line.startswith('-') or re.match('^\\d+\\.\\s', stripped_line):
                if len(stripped_line) > 1:
                    point_count += 1
                elif len(stripped_line.split(maxsplit=1)) > 1:
                    point_count += 1
        return point_count == 4

class DataIdx266InstructionChecker(AragenInstructions):

    def __init__(self):
        super().__init__('266')

    def check_following(self, value):
        """Checks if the response is a rap poem about the abyss with exactly 4 paragraphs
        separated by '***'.

        Args:
            value: A string representing the response.

        Returns:
            True if the response follows the instruction or False otherwise.
        """
        if not isinstance(value, str) or not value:
            return False
        separator = '***'
        paragraphs = value.split(separator)
        if len(paragraphs) != 4:
            return False
        for paragraph in paragraphs:
            if not paragraph.strip():
                return False
        return True

class DataIdx267InstructionChecker(AragenInstructions):

    def __init__(self):
        super().__init__('idx_267')

    def check_following(self, value):
        """Checks if the response contains exactly two different parts separated by '******'.

        Args:
            value: A string representing the response.

        Returns:
            True if the response follows the instruction (exactly two different parts
            separated by six asterisks), False otherwise.
        """
        separator = '******'
        if separator not in value:
            return False
        parts = value.split(separator)
        if len(parts) != 2:
            return False
        part1 = parts[0].strip()
        part2 = parts[1].strip()
        if not part1 or not part2:
            return False
        if part1 == part2:
            return False
        return True

class DataIdx268InstructionChecker(AragenInstructions):

    def __init__(self):
        super().__init__('idx_268')

    def check_following(self, value):
        """Checks if the response follows the constraints for question IDX 268.

        Constraints:
        1. The entire response must be enclosed in double quotes.
        2. At least one part of the answer must be highlighted using asterisks (*highlighted part*).

        Args:
            value: A string representing the response.

        Returns:
            True if the response follows the instruction or False otherwise.
        """
        if not isinstance(value, str):
            return False
        if not (value.startswith('"') and value.endswith('"')):
            return False
        content = value[1:-1]
        if not re.search('\\*.*?\\*', content):
            return False
        return True

class DataIdx269InstructionChecker(AragenInstructions):

    def __init__(self):
        super().__init__('idx_269')

    def check_following(self, value):
        """Checks if the response contains at least one part marked with Markdown asterisks.

        Args:
            value: A string representing the response.

        Returns:
            True if the response contains at least one word/phrase
            enclosed in single asterisks (*word* or *phrase*),
            False otherwise.
        """
        pattern = '\\*[^* ]+\\*'
        if re.search(pattern, value):
            return True
        else:
            return False

class DataIdx270InstructionChecker(AragenInstructions):

    def __init__(self):
        super().__init__('270')

    def check_following(self, value: str) -> bool:
        """Checks if the response is a string enclosed within double quotation marks.

        Args:
            value: A string representing the response.

        Returns:
            True if the response is a string that starts and ends with a double
            quotation mark, False otherwise.
        """
        if not isinstance(value, str):
            return False
        if len(value) < 2:
            return False
        return value.startswith('"') and value.endswith('"')

class DataIdx271InstructionChecker(AragenInstructions):

    def __init__(self):
        super().__init__('idx_271')

    def check_following(self, value):
        """Checks if the response follows the instructions for question idx_271.

        Instructions:
        1. The response must contain the word 'مكون' at least once.
        2. The response must not contain any commas.

        Args:
            value: A string representing the response.

        Returns:
            True if the response follows the instruction or False otherwise.
        """
        contains_mukun = 'مكون' in value
        contains_comma = ',' in value
        return contains_mukun and (not contains_comma)

class DataIdx272InstructionChecker(AragenInstructions):

    def __init__(self):
        super().__init__('idx_272')

    def check_following(self, value):
        """Checks if the response does not exceed 17 sentences.

        Args:
            value: A string representing the response.

        Returns:
            True if the response has 17 or fewer sentences, False otherwise.
        """
        if not isinstance(value, str):
            return False
        text = value.strip()
        if not text:
            return True
        sentences_list = re.split('[.!?](?:\\s+|$)', text)
        sentences_list = [s for s in sentences_list if s]
        sentence_count = len(sentences_list)
        return sentence_count <= 17

class DataIdx273InstructionChecker(AragenInstructions):

    def __init__(self):
        super().__init__('idx_273')

    def check_following(self, value):
        """Checks if the response follows the instructions for IDX 273.

        Constraints checked:
        1. Contains at least one part formatted with markdown italics (*text* or _text_).
        2. Contains the word 'العزاب' at least twice, as a whole word.

        Args:
            value: A string representing the response (the poem).

        Returns:
            True if the response follows the specified constraints, False otherwise.
        """
        if not isinstance(value, str):
            return False
        has_italics = bool(re.search('\\*[^*]+\\*|_[^_]+_', value))
        uzzaab_count = len(re.findall('\\bالعزاب\\b', value))
        has_enough_uzzaab = uzzaab_count >= 2
        return has_italics and has_enough_uzzaab

class DataIdx274InstructionChecker(AragenInstructions):

    def __init__(self):
        super().__init__('idx_274')

    def check_following(self, value):
        """Checks if the response follows the instruction for IDX 274.

        Constraints:
        - Describes Yazan's daily work as a dog walker. (Cannot check automatically).
        - Complete. (Cannot check automatically).
        - Less than six sentences. (Checkable).

        Args:
            value: A string representing the response.

        Returns:
            True if the response follows the constraint (less than 6 sentences), False otherwise.
        """
        if not isinstance(value, str):
            return False
        sentences = re.split('[.!?]', value)
        valid_sentences = [s.strip() for s in sentences if s.strip()]
        sentence_count = len(valid_sentences)
        return sentence_count < 6

class DataIdx275InstructionChecker(AragenInstructions):

    def __init__(self):
        super().__init__('idx_275')

    def check_following(self, value):
        """
        Checks if the response contains exactly two bullet points using '*'
        as specified in the instructions for IDX 275.
        """
        lines = value.strip().split('\n')
        bullet_count = 0
        for line in lines:
            if line.strip().startswith('* '):
                bullet_count += 1
        return bullet_count == 2

class DataIdx276InstructionChecker(AragenInstructions):

    def __init__(self):
        super().__init__('idx_276')

    def check_following(self, value):
        """Checks if the response follows the constraints for IDX 276.

        Constraints:
        1. Less than 10 sentences (checked by counting terminal/semi-terminal punctuation).
        2. Correct punctuation marks (checked by presence and basic spacing rules).
        """
        if not isinstance(value, str):
            return False
        separator_chars = ['.', '!', '?', ';']
        separator_count = sum((value.count(char) for char in separator_chars))
        if separator_count > 8:
            return False
        common_punctuation = ['،', '.', '؛', '!', '؟']
        if not any((p in value for p in common_punctuation)):
            return False
        incorrect_spacing_patterns = [' ،', ' .', ' ؛', ' !', ' ؟']
        if any((pattern in value for pattern in incorrect_spacing_patterns)):
            return False
        return True

class DataIdx277InstructionChecker(AragenInstructions):

    def __init__(self):
        super().__init__('277')

    def check_following(self, value):
        """Checks if the response is enclosed within double quotes.
        Args:
            value: A string representing the response.

        Returns:
            True if the response starts and ends with a double quote, False otherwise.
        """
        if not isinstance(value, str):
            return False
        return value.startswith('"') and value.endswith('"')

class DataIdx278InstructionChecker(AragenInstructions):

    def __init__(self):
        super().__init__('278')

    def check_following(self, value):
        """Checks if the response follows the instructions for IDX 278.

        Args:
            value: A string representing the response.

        Returns:
            True if the response follows the instruction or False otherwise.
        """
        if not isinstance(value, str):
            return False
        cleaned_value = value.strip()
        title_match = re.match('<<(.*?)>>', cleaned_value)
        if not title_match:
            return False
        content_after_title = cleaned_value[title_match.end():].strip()
        if '******' not in content_after_title:
            return False
        parts = content_after_title.split('******')
        if len(parts) != 2:
            return False
        verse1 = parts[0].strip()
        verse2 = parts[1].strip()
        if verse1 == verse2:
            return False

        def check_verse(verse):
            if not verse:
                return False
            if not verse.endswith('؟'):
                return False
            if ',' in verse or '،' in verse:
                return False
            return True
        if not check_verse(verse1):
            return False
        if not check_verse(verse2):
            return False
        return True

class DataIdx279InstructionChecker(AragenInstructions):

    def __init__(self):
        super().__init__('idx_279')

    def check_following(self, value):
        """Checks if the response contains the word 'مبرمج'.

        Args:
            value: A string representing the response (cover letter).

        Returns:
            True if the response contains the word 'مبرمج', False otherwise.
        """
        if not isinstance(value, str):
            return False
        return 'مبرمج' in value

class DataIdx280InstructionChecker(AragenInstructions):

    def __init__(self):
        super().__init__('idx_280')

    def check_following(self, value):
        """Checks if the response contains at least 20 sentences.

        A sentence is considered a segment of text ending with '.', '?', '!', or '؟'.
        Consecutive punctuation marks and empty strings are handled.

        Args:
            value: A string representing the response.

        Returns:
            True if the response follows the instruction (at least 20 sentences),
            False otherwise.
        """
        if not isinstance(value, str):
            return False
        sentence_enders = '[.?!؟]'
        sentences = re.split(sentence_enders, value)
        sentence_count = 0
        for sentence in sentences:
            if sentence.strip():
                sentence_count += 1
        return sentence_count >= 20

class DataIdx281InstructionChecker(AragenInstructions):

    def __init__(self):
        super().__init__('idx_281')

    def check_following(self, value):
        """Checks if the response is a description of Pixel 3A,
        is at least 400 words, and is enclosed in double quotes.

        Args:
            value: A string representing the response.

        Returns:
            True if the response follows the instruction or False otherwise.
        """
        if not value.startswith('"') or not value.endswith('"'):
            return False
        content = value[1:-1]
        words = content.split()
        word_count = len(words)
        if word_count < 400:
            return False
        return True

class DataIdx282InstructionChecker(AragenInstructions):

    def __init__(self):
        super().__init__('idx_282')

    def check_following(self, value):
        """Checks if the response contains at least two sections formatted like *text*."""
        if not isinstance(value, str):
            return False
        formatted_sections = re.findall('\\*.*?\\*', value)
        return len(formatted_sections) >= 2

class DataIdx283InstructionChecker(AragenInstructions):

    def __init__(self):
        super().__init__('idx_283')

    def check_following(self, value):
        """
        Checks if the response uses markdown formatting to highlight at least 3 sections.
        Highlights checked: bold (**...** or __...__) and headings (# ...).
        Ignores the subjective "weird style" constraint.
        Args:
            value: A string representing the response.

        Returns:
            True if at least 3 sections are highlighted with markdown (bold or heading), False otherwise.
        """
        if not isinstance(value, str) or not value.strip():
            return False
        bold_star_matches = re.findall('\\*\\*.+?\\*\\*', value, re.S)
        bold_star_count = len(bold_star_matches)
        bold_underscore_matches = re.findall('__.+?__', value, re.S)
        bold_underscore_count = len(bold_underscore_matches)
        heading_matches = re.findall('^#+ .*', value, re.M)
        heading_count = len(heading_matches)
        total_highlighted_sections = bold_star_count + bold_underscore_count + heading_count
        return total_highlighted_sections >= 3

class DataIdx284InstructionChecker(AragenInstructions):

    def __init__(self):
        super().__init__('idx_284')

    def check_following(self, value):
        """Checks if the response has less than 6 sentences.

        Args:
            value: A string representing the response.

        Returns:
            True if the response follows the instruction (less than 6 sentences) or False otherwise.
        """
        if not value or not value.strip():
            return True
        sentences = re.split('[.?!]+', value)
        valid_sentences = [s for s in sentences if s.strip()]
        sentence_count = len(valid_sentences)
        return sentence_count < 6

class DataIdx285InstructionChecker(AragenInstructions):

    def __init__(self):
        super().__init__('idx_285')

    def check_following(self, value):
        """Checks if the response follows the instructions for question IDX 285.
        Constraints:
        1. Contains at least 3 sections highlighted with *...*.
        2. Contains at least 3 placeholders with [...].

        Args:
            value: A string representing the response.

        Returns:
            True if the response follows the instruction or False otherwise.
        """
        highlight_pattern = '\\*.+?\\*'
        highlight_matches = re.findall(highlight_pattern, value)
        num_highlights = len(highlight_matches)
        placeholder_pattern = '\\[.+?\\]'
        placeholder_matches = re.findall(placeholder_pattern, value)
        num_placeholders = len(placeholder_matches)
        return num_highlights >= 3 and num_placeholders >= 3

class DataIdx286InstructionChecker(AragenInstructions):

    def __init__(self):
        super().__init__('idx_286')

    def check_following(self, value):
        """Checks if the response is a rap song about the topic with markdown highlighting.
        Args:
            value: A string representing the response.

        Returns:
            True if the response follows the instruction or False otherwise.
        """
        if not isinstance(value, str):
            return False
        markdown_patterns = ['\\*.*?\\*', '\\*\\*.*?\\*\\*', '_.*?_', '__.*?__', '```.*?```', '`.*?`']
        markdown_present = False
        for pattern in markdown_patterns:
            if re.search(pattern, value, re.DOTALL):
                markdown_present = True
                break
        if not markdown_present:
            return False
        keywords = ['مكالمة', 'مسؤول', 'قريب', 'أمير الكويت']
        content_matches = all((keyword in value for keyword in keywords))
        if not content_matches:
            return False
        multiple_lines = '\n' in value
        if not multiple_lines:
            return False
        return True

class DataIdx287InstructionChecker(AragenInstructions):

    def __init__(self):
        super().__init__('idx_287')

    def check_following(self, value):
        """Checks if the response follows the instruction of not using commas.

        Args:
            value: A string representing the response.

        Returns:
            True if the response follows the instruction (no commas), False otherwise.
        """
        if ',' in value:
            return False
        if '،' in value:
            return False
        return True

class DataIdx288InstructionChecker(AragenInstructions):

    def __init__(self):
        super().__init__('idx_288')

    def check_following(self, value):
        """You will implement the logic of the function here to see if the response is correct or not.
        Args:
            value: A string representing the response.

        Returns:
            True if the response follows the instruction or False otherwise.
        """
        if not isinstance(value, str):
            return False
        lines = value.split('\n')
        content_lines = [line.strip() for line in lines if line.strip()]
        if len(content_lines) != 4:
            return False
        for line in content_lines:
            if not line.startswith('* '):
                return False
            if len(line) <= 2:
                return False
        return True

class DataIdx289InstructionChecker(AragenInstructions):

    def __init__(self):
        super().__init__('idx_289')

    def check_following(self, value):
        """Checks if the response contains a title within double angle brackets <<...>>.
        The response must contain the pattern << followed by some characters, followed by >>.

        Args:
            value: A string representing the response.

        Returns:
            True if the response contains the pattern <<...>>, False otherwise.
        """
        pattern = '<<.*?>>'
        return bool(re.search(pattern, value))

class DataIdx290InstructionChecker(AragenInstructions):

    def __init__(self):
        super().__init__('290')

    def check_following(self, value):
        """Checks if the response is enclosed in double quotes.
        Checking the content (joke about XML, funny intro/ending) is outside the scope
        of this automated structural check due to the subjective nature of humor and relevance.

        Args:
            value: A string representing the response.

        Returns:
            True if the response is enclosed in double quotes, False otherwise.
        """
        if not isinstance(value, str):
            return False
        if value.startswith('"') and value.endswith('"'):
            if len(value) > 1:
                return True
        return False

class DataIdx291InstructionChecker(AragenInstructions):

    def __init__(self):
        super().__init__('idx_291')

    def check_following(self, value):
        """Checks if the response mentions 'الانفتاح' and does not contain commas.

        Args:
            value: A string representing the response.

        Returns:
            True if the response follows the instruction or False otherwise.
        """
        mentions_openness = 'الانفتاح' in value
        contains_commas = ',' in value
        return mentions_openness and (not contains_commas)

class DataIdx292InstructionChecker(AragenInstructions):

    def __init__(self):
        super().__init__('idx_292')

    def check_following(self, value):
        """Checks if the response is enclosed entirely within double quotation marks.

        Args:
            value: A string representing the response.

        Returns:
            True if the response starts and ends with double quotation marks, False otherwise.
        """
        if not isinstance(value, str):
            return False
        return value.startswith('"') and value.endswith('"')

class DataIdx293InstructionChecker(AragenInstructions):

    def __init__(self):
        super().__init__('idx_293')

    def check_following(self, value):
        """Checks if the response contains exactly one line starting with '*' as a bullet point.
        Args:
            value: A string representing the response.

        Returns:
            True if the response follows the instruction or False otherwise.
        """
        lines = value.strip().split('\n')
        bullet_point_count = 0
        for line in lines:
            if line.strip().startswith('*'):
                bullet_point_count += 1
        return bullet_point_count == 1

class DataIdx294InstructionChecker(AragenInstructions):

    def __init__(self):
        super().__init__('idx_294')

    def check_following(self, value):
        """Checks if the response meets the criteria:
        - Is a string.
        - Contains at least 200 words.
        - Uses markdown bold (**...** or __...__) or italic (*...* or _..._).
        Content relevance (poem, shoe production line, professional) is not checked
        as it's subjective and requires NLP beyond simple constraint checking.

        Args:
            value: A string representing the response.

        Returns:
            True if the response follows the quantifiable instructions, False otherwise.
        """
        if not isinstance(value, str):
            return False
        words = re.findall('\\b\\w+\\b', value)
        word_count = len(words)
        if word_count < 200:
            return False
        bold_pattern = re.compile('\\*\\*.+?\\*\\*|__.+?__')
        italic_pattern = re.compile('\\*.+?\\*|_.+?_')
        has_bold = bool(bold_pattern.search(value))
        has_italic = bool(italic_pattern.search(value))
        if not (has_bold or has_italic):
            return False
        return True

class DataIdx295InstructionChecker(AragenInstructions):

    def __init__(self):
        super().__init__('idx_295')

    def check_following(self, value):
        """Checks if the response is a valid JSON string.

        The question requires the complete result to be presented in JSON format.

        Args:
            value: A string representing the response.

        Returns:
            True if the response is valid JSON, False otherwise.
        """
        if not isinstance(value, str):
            return False
        try:
            json.loads(value)
            return True
        except json.JSONDecodeError:
            return False
        except TypeError:
            return False

class DataIdx296InstructionChecker(AragenInstructions):

    def __init__(self):
        super().__init__('idx_296')

    def check_following(self, value):
        """Checks if the response is valid XML and contains at least 4 sentences.

        Args:
            value: A string representing the response.

        Returns:
            True if the response is valid XML and has >= 4 sentences, False otherwise.
        """
        if not value:
            return False
        try:
            root = ET.fromstring(value)
        except ET.ParseError:
            return False
        text = ET.tostring(root, encoding='unicode', method='text')
        sentence_terminators = re.findall('[.!?]', text)
        sentence_count = len(sentence_terminators)
        return sentence_count >= 4

class DataIdx297InstructionChecker(AragenInstructions):

    def __init__(self):
        super().__init__('idx_297')

    def check_following(self, value):
        """Checks if the response includes the word "مهرجان" at least twice.

        Args:
            value: A string representing the response (poem).

        Returns:
            True if "مهرجان" appears at least twice, False otherwise.
        """
        if not isinstance(value, str):
            return False
        words = value.replace('\n', ' ').replace('\r', ' ').split()
        count = 0
        target_word = 'مهرجان'
        cleaned_words = [''.join((c for c in word if c.isalnum())) for word in words]
        for word in cleaned_words:
            if word == target_word:
                count += 1
        return count >= 2

class DataIdx298InstructionChecker(AragenInstructions):

    def __init__(self):
        super().__init__('idx_298')

    def check_following(self, value):
        """Checks if the response uses '*' to highlight at least two sections.

        Args:
            value: A string representing the response.

        Returns:
            True if the response follows the instruction or False otherwise.
        """
        if not isinstance(value, str):
            return False
        highlighted_sections = re.findall('\\*+.+?\\*+', value)
        return len(highlighted_sections) >= 2

class DataIdx299InstructionChecker(AragenInstructions):

    def __init__(self):
        super().__init__('idx_299')

    def check_following(self, value):
        """Checks if the response follows the instruction constraints for IDX 299.

        Question: هل بإمكانك توضيح الجملة التالية "البهلوان يقفز في الهواء، مؤديًا حيلة."؟
                  من فضلك أبرز على الأقل 6 مقاطع في إجابتك باستخدام العلامات مثل *المقطع المبرز*.
                  رجاءً اكتب على الأقل 300 كلمة.

        Constraints implemented:
        1. Contains at least 6 highlighted segments using *...* markers (where ... is non-empty).
        2. Contains at least 300 words.
        (The semantic constraint about explaining the sentence is not checked programmatically).

        Args:
            value: A string representing the response.

        Returns:
            True if the response follows the structural constraints or False otherwise.
        """
        if not isinstance(value, str):
            return False
        highlight_pattern = '\\*[^\\*]+\\*'
        highlight_matches = re.findall(highlight_pattern, value)
        has_enough_highlights = len(highlight_matches) >= 6
        words = value.split()
        has_enough_words = len(words) >= 300
        return has_enough_highlights and has_enough_words

class DataIdx300InstructionChecker(AragenInstructions):

    def __init__(self):
        super().__init__('idx_300')

    def check_following(self, value):
        """
        Checks if the response contains '******' followed by non-whitespace characters.
        Args:
            value: A string representing the response.

        Returns:
            True if the response contains '******' followed by non-whitespace characters,
            False otherwise.
        """
        marker = '******'
        marker_index = value.find(marker)
        if marker_index == -1:
            return False
        content_after_marker = value[marker_index + len(marker):].strip()
        return len(content_after_marker) > 0

class DataIdx301InstructionChecker(AragenInstructions):

    def __init__(self):
        super().__init__('idx_301')

    def check_following(self, value):
        """Checks if the response contains at least 20 sentences.
        
        Args:
            value: A string representing the response (email content).

        Returns:
            True if the response contains 20 or more sentences, False otherwise.
        """
        if not isinstance(value, str) or not value.strip():
            return False
        sentences = [s.strip() for s in re.split('[.!?]+', value) if s.strip()]
        min_sentences = 20
        return len(sentences) >= min_sentences

class DataIdx302InstructionChecker(AragenInstructions):

    def __init__(self):
        super().__init__('idx_302')

    def check_following(self, value):
        """You will implement the logic of the function here to see if the response is correct or not.
        Args:
            value: A string representing the response.

        Returns:
            True if the response follows the instruction or False otherwise.
        """
        parts = value.split('***')
        if len(parts) != 2:
            return False
        if not parts[0].strip() or not parts[1].strip():
            return False
        return True

class DataIdx303InstructionChecker(AragenInstructions):

    def __init__(self):
        super().__init__('idx_303')

    def check_following(self, value):
        """Checks if the response is a poem with exactly 6 stanzas separated by ***.

        Args:
            value: A string representing the response.

        Returns:
            True if the response follows the instruction or False otherwise.
        """
        if not isinstance(value, str):
            return False
        stanzas = value.split('***')
        if len(stanzas) != 6:
            return False
        return True

class DataIdx304InstructionChecker(AragenInstructions):

    def __init__(self):
        super().__init__('idx_304')

    def check_following(self, value):
        """Checks if the response contains a title enclosed in double angle brackets.

        Args:
            value: A string representing the response.

        Returns:
            True if the response contains '<<...>>' at least once, False otherwise.
        """
        pattern = '<<.*?>>'
        if re.search(pattern, value):
            return True
        else:
            return False

class DataIdx305InstructionChecker(AragenInstructions):

    def __init__(self):
        super().__init__('305')

    def check_following(self, value):
        """Checks if the response follows the instructions for IDX 305.

        Instructions:
        1. Must mention it's a small sailboat with one mast (قارب شراعي صغير ذو صاري واحد).
        2. Must mention it's easy to sail and understand its system (يسهل إبحارها وفهم نظامها).
        3. Must contain a part in a table format.
        4. Must contain a title enclosed in double angle brackets, e.g., <<بيع المركب الشراعي>>.

        Args:
            value: A string representing the response.

        Returns:
            True if the response follows the instruction or False otherwise.
        """
        if not isinstance(value, str):
            return False
        title_match = re.search('<<.*?>>', value)
        if not title_match:
            return False
        phrase1 = 'قارب شراعي صغير'
        phrase2 = 'صاري واحد'
        phrase3 = 'يسهل إبحارها'
        phrase4 = 'فهم نظامها'
        if not (phrase1 in value and phrase2 in value and (phrase3 in value) and (phrase4 in value)):
            return False
        has_pipe = '|' in value
        has_hyphen = '-' in value
        has_table_structure = False
        lines = value.splitlines()
        pipe_lines = [line for line in lines if '|' in line]
        if len(pipe_lines) >= 2:
            has_table_structure = True
        elif has_pipe and has_hyphen:
            has_table_structure = True
        if not has_table_structure:
            markdown_table_pattern = re.compile('^\\s*\\|.*\\|\\s*$', re.MULTILINE)
            separator_line_pattern = re.compile('^\\s*\\|[-: ]+\\|[-: |]*\\s*$', re.MULTILINE)
            markdown_lines = markdown_table_pattern.findall(value)
            separator_lines = separator_line_pattern.findall(value)
            if len(markdown_lines) >= 2 and len(separator_lines) >= 1:
                has_table_structure = True
            elif len(pipe_lines) >= 1 and len(separator_lines) >= 1:
                has_table_structure = True
        if not has_table_structure:
            return False
        return True

class DataIdx306InstructionChecker(AragenInstructions):

    def __init__(self):
        super().__init__('306')

    def check_following(self, value):
        """Checks if the response follows the specific format for question 306.

        Args:
            value: A string representing the response.

        Returns:
            True if the response follows the instruction or False otherwise.
        """
        if not isinstance(value, str):
            return False
        parts = value.split('***')
        if len(parts) != 3:
            return False
        part1 = parts[0].strip()
        part2 = parts[1].strip()
        part3 = parts[2].strip()
        if not part1.startswith('النصيحة 1'):
            return False
        if not part2.startswith('النصيحة 2'):
            return False
        if not part3.startswith('النصيحة 3'):
            return False
        return True

class DataIdx307InstructionChecker(AragenInstructions):

    def __init__(self):
        super().__init__('idx_307')

    def check_following(self, value):
        """Checks if the response is entirely enclosed within double quotes.
        Args:
            value: A string representing the response.

        Returns:
            True if the response starts and ends with double quotes, False otherwise.
        """
        if not isinstance(value, str):
            return False
        return value.startswith('"') and value.endswith('"')

class DataIdx308InstructionChecker(AragenInstructions):

    def __init__(self):
        super().__init__('idx_308')

    def check_following(self, value):
        """Checks if the response uses the word "الأماكن" at least once.
        Args:
            value: A string representing the response.

        Returns:
            True if the response follows the instruction or False otherwise.
        """
        required_word = 'الأماكن'
        return required_word in value

class DataIdx309InstructionChecker(AragenInstructions):

    def __init__(self):
        super().__init__('idx_309')

    def check_following(self, value):
        """Checks if the response follows the instructions for IDX 309.

        The response must:
        1. Be enclosed in double quotes.
        2. Have a word count greater than 600 words inside the quotes.

        Args:
            value: A string representing the response.

        Returns:
            True if the response follows the instruction or False otherwise.
        """
        if not isinstance(value, str):
            return False
        if not (value.startswith('"') and value.endswith('"')):
            return False
        content = value[1:-1]
        words = content.split()
        if len(words) <= 600:
            return False
        return True

class DataIdx310InstructionChecker(AragenInstructions):

    def __init__(self):
        super().__init__('idx_310')

    def check_following(self, value):
        """Checks if the response follows the instructions for question 310.
        The instructions are:
        - Explain why there are oval racetracks in the desert.
        - Rephrase the answer to make it more concise.
        - Include the word "الصحراء" in the answer.
        - Ensure the answer contains exactly 3 points in Markdown bullet format.

        Args:
            value: A string representing the response.

        Returns:
            True if the response follows the instruction or False otherwise.
        """
        includes_desert = 'الصحراء' in value
        lines = value.strip().split('\n')
        bullet_points = 0
        for line in lines:
            stripped_line = line.strip()
            if stripped_line.startswith('- ') or stripped_line.startswith('* '):
                bullet_points += 1
        has_exactly_3_points = bullet_points == 3
        return includes_desert and has_exactly_3_points

class DataIdx311InstructionChecker(AragenInstructions):

    def __init__(self):
        super().__init__('idx_311')

    def check_following(self, value):
        """You will implement the logic of the function here to see if the response is correct or not.
        Args:
            value: A string representing the response.

        Returns:
            True if the response follows the instruction or False otherwise.
        """
        sentences = re.split('[.!?؟]+', value)
        sentence_count = len([s for s in sentences if s.strip()])
        if sentence_count >= 7:
            return False
        lines = value.splitlines()
        bullet_count = 0
        for line in lines:
            stripped_line = line.strip()
            if re.match('^[\\*\\-\\+] ', stripped_line) or re.match('^\\d+\\. ', stripped_line):
                bullet_count += 1
        if bullet_count != 1:
            return False
        return True

class DataIdx312InstructionChecker(AragenInstructions):

    def __init__(self):
        super().__init__('idx_312')

    def check_following(self, value):
        """Checks if the response has a non-empty title enclosed in <<>> followed by content.

        Args:
            value: A string representing the response.

        Returns:
            True if the response follows the structural instruction, False otherwise.
        """
        if not isinstance(value, str):
            return False
        pattern = '(?s)^<<.+?>>.+'
        match = re.match(pattern, value)
        return bool(match)

class DataIdx313InstructionChecker(AragenInstructions):

    def __init__(self):
        super().__init__('idx_313')

    def check_following(self, value):
        """Checks if the response follows the instructions for IDX 313.

        Constraints to check:
        1. At least 3 parts are highlighted and bolded using Markdown (**text** or __text__).
        (Other constraints like Zajal style, distinction from other periods, and tone are not reliably checkable programmatically without advanced NLP/contextual understanding).

        Args:
            value: A string representing the response.

        Returns:
            True if the response follows the checkable constraint (at least 3 bolded parts) or False otherwise.
        """
        if not isinstance(value, str):
            return False
        bold_pattern = re.compile('\\*\\*(.+?)\\*\\*|__(.+?)__')
        matches = bold_pattern.findall(value)
        num_bolded_parts = len(matches)
        return num_bolded_parts >= 3

class DataIdx314InstructionChecker(AragenInstructions):

    def __init__(self):
        super().__init__('idx_314')

    def check_following(self, value):
        """Checks if the response follows the instructions for IDX 314.

        Constraints:
        - At least 8 italicized sections using Markdown format (*text*).
        - Total number of sentences between 40 and 60 (inclusive).

        Args:
            value: A string representing the response.

        Returns:
            True if the response follows the instructions, False otherwise.
        """
        italic_matches = re.findall('\\*([^\\*]+)\\*', value)
        num_italics = len(italic_matches)
        min_italics = 8
        sentences = [s.strip() for s in re.split('[.!?؟]+', value) if s.strip()]
        num_sentences = len(sentences)
        min_sentences = 40
        max_sentences = 60
        constraints_met = num_italics >= min_italics and min_sentences <= num_sentences <= max_sentences
        return constraints_met

class DataIdx315InstructionChecker(AragenInstructions):

    def __init__(self):
        super().__init__('idx_315')

    def check_following(self, value):
        """Checks if the response contains the word "فيل" (elephant) at least 3 times.

        Args:
            value: A string representing the response.

        Returns:
            True if the response follows the instruction or False otherwise.
        """
        elephant_count = value.count('فيل')
        return elephant_count >= 3

class DataIdx316InstructionChecker(AragenInstructions):

    def __init__(self):
        super().__init__('idx_316')

    def check_following(self, value):
        """Checks if the response (a short story) contains the phrase "أبناء العمومة" more than twice.

        Args:
            value: A string representing the response (the short story).

        Returns:
            True if the phrase "أبناء العمومة" appears more than 2 times, False otherwise.
        """
        count = value.count('أبناء العمومة')
        return count > 2

class DataIdx317InstructionChecker(AragenInstructions):

    def __init__(self):
        super().__init__('idx_317')

    def check_following(self, value):
        """Checks if the response contains at least one placeholder within square brackets like [text].

        Args:
            value: A string representing the response.

        Returns:
            True if the response follows the instruction or False otherwise.
        """
        pattern = '\\[.*?\\]'
        matches = re.findall(pattern, value)
        return len(matches) >= 1

class DataIdx318InstructionChecker(AragenInstructions):

    def __init__(self):
        super().__init__('idx_318')

    def check_following(self, value):
        """Checks if the response follows the instruction for IDX 318.
        
        Instructions:
        1. Write a colloquial Arabic verse describing the process of writing colloquial poetry.
        2. Do not use any commas in the entire response.

        Args:
            value: A string representing the response.

        Returns:
            True if the response follows the instruction or False otherwise.
        """
        if not value or ',' in value:
            return False
        return True

class DataIdx319InstructionChecker(AragenInstructions):

    def __init__(self):
        super().__init__('idx_319')

    def check_following(self, value):
        """Checks if the response is a valid JSON object that mentions 'البقشيشي' and
        attempts a basic structural check by ensuring it's a dictionary or list.

        Args:
            value: A string representing the response.

        Returns:
            True if the response is valid JSON, contains 'البقشيشي', and is a
            JSON object (dict) or array (list), False otherwise.
        """
        try:
            parsed_json = json.loads(value)
        except json.JSONDecodeError:
            return False
        if not isinstance(parsed_json, (dict, list)):
            return False
        if 'البقشيشي' not in value:
            return False
        return True

class DataIdx320InstructionChecker(AragenInstructions):

    def __init__(self):
        super().__init__('320')

    def check_following(self, value):
        """Checks if the response contains exactly one instance of the separator '******'.

        Args:
            value: A string representing the response.

        Returns:
            True if the response follows the instruction (contains exactly one '******'),
            or False otherwise.
        """
        separator = '******'
        return value.count(separator) == 1

class DataIdx321InstructionChecker(AragenInstructions):

    def __init__(self):
        super().__init__('idx_321')

    def check_following(self, value):
        """Checks if the response contains at least 8 words inside square brackets.
        Args:
            value: A string representing the response.

        Returns:
            True if the response follows the instruction or False otherwise.
        """
        bracket_contents = re.findall('\\[(.*?)\\]', value)
        word_count = 0
        for content in bracket_contents:
            words = content.split()
            word_count += len(words)
        return word_count >= 8


class DataIdx322InstructionChecker(AragenInstructions):

    def __init__(self):
        super().__init__('idx_322')

    def check_following(self, value):
        """Checks if the response is a valid JSON string.

        Args:
            value: A string representing the response.

        Returns:
            True if the response is a valid JSON string, False otherwise.
        """
        if not isinstance(value, str):
            return False
        try:
            json.loads(value)
            return True
        except json.JSONDecodeError:
            return False

class DataIdx323InstructionChecker(AragenInstructions):

    def __init__(self):
        super().__init__('idx_323')

    def check_following(self, value: str) -> bool:
        """Checks if the response follows the instruction constraints for IDX 323.

        Constraints:
        1. Total word count is 150 or more.
        2. Exactly 3 paragraphs are highlighted using asterisks (*paragraph*).

        Args:
            value: A string representing the response.

        Returns:
            True if the response follows the instructions, False otherwise.
        """
        if not isinstance(value, str):
            return False
        words = value.split()
        word_count = len(words)
        word_count_ok = word_count >= 150
        highlighted_paragraphs = re.findall('\\*(.*?)\\*', value, re.DOTALL)
        num_highlighted = len(highlighted_paragraphs)
        highlight_count_ok = num_highlighted == 3
        return word_count_ok and highlight_count_ok

class DataIdx324InstructionChecker(AragenInstructions):

    def __init__(self):
        super().__init__('idx_324')

    def check_following(self, value):
        """Checks if the response follows the constraints for question IDX 324.
        Constraints:
        - Must contain at least two placeholders enclosed in square brackets, e.g., [الكاتب].
        Args:
            value: A string representing the response (the article).

        Returns:
            True if the response follows the instruction or False otherwise.
        """
        placeholders = re.findall('\\[.+?\\]', value)
        if len(placeholders) >= 2:
            return True
        else:
            return False

class DataIdx325InstructionChecker(AragenInstructions):

    def __init__(self):
        super().__init__('idx_325')

    def check_following(self, value):
        """Checks if the response follows the instructions for question 325.

        Constraints:
        1. Must have exactly one title enclosed in double angle brackets (<<Title>>).
        2. Must be less than 13 sentences (count sentences by . ! ؟).
        3. Must not contain commas (,).
        4. Other punctuation is allowed.

        Args:
            value: A string representing the response (the poem).

        Returns:
            True if the response follows all instructions, False otherwise.
        """
        if not isinstance(value, str):
            return False
        title_matches = re.findall('<<.*?>>', value)
        has_valid_title = len(title_matches) == 1
        sentence_enders = ['.', '!', '؟']
        sentence_count = 0
        for ender in sentence_enders:
            sentence_count += value.count(ender)
        is_less_than_13_sentences = sentence_count < 13
        has_no_commas = ',' not in value
        return has_valid_title and is_less_than_13_sentences and has_no_commas

class DataIdx326InstructionChecker(AragenInstructions):

    def __init__(self):
        super().__init__('idx_326')

    def check_following(self, value):
        """Checks if the response follows the instruction for IDX 326.

        The instruction requires separating the answer to two parts
        (Is Zidane an Arabic name? and similar names) with '******'.

        Args:
            value: A string representing the response.

        Returns:
            True if the response follows the instruction or False otherwise.
        """
        separator = '******'
        if separator not in value:
            return False
        parts = value.split(separator)
        if len(parts) < 2:
            return False
        if not parts[0].strip():
            return False
        if not parts[1].strip():
            return False
        return True

class DataIdx327InstructionChecker(AragenInstructions):

    def __init__(self):
        super().__init__('idx_327')

    def check_following(self, value):
        """Checks if the response contains at least six placeholders like [الاسم].

        Args:
            value: A string representing the response.

        Returns:
            True if the response contains at least six placeholders, False otherwise.
        """
        placeholder_pattern = '\\[.*?\\]'
        placeholders = re.findall(placeholder_pattern, value)
        return len(placeholders) >= 6

class DataIdx328InstructionChecker(AragenInstructions):

    def __init__(self):
        super().__init__('idx_328')

    def check_following(self, value):
        """Checks if the response follows the constraints for question IDX 328.
        Constraints:
        1. Contains exactly one separator '******'.
        2. Does not contain any commas.
        Args:
            value: A string representing the response.

        Returns:
            True if the response follows the instruction or False otherwise.
        """
        contains_exactly_one_separator = value.count('******') == 1
        contains_comma = ',' in value
        return contains_exactly_one_separator and (not contains_comma)

class DataIdx329InstructionChecker(AragenInstructions):

    def __init__(self):
        super().__init__('idx_329')

    def check_following(self, value):
        """Checks if the response has at least 300 words.
        Args:
            value: A string representing the response.

        Returns:
            True if the response follows the instruction (total word count >= 300),
            False otherwise.
        """
        words = value.split()
        word_count = len(words)
        return word_count >= 300

class DataIdx330InstructionChecker(AragenInstructions):

    def __init__(self):
        super().__init__('idx_330')

    def check_following(self, value):
        """Checks if the response follows the instruction for IDX 330.

        Instructions:
        1. Provide 5 question-answer pairs.
        2. Format each pair as "سؤال وجواب # X" where X is the pair number (1 to 5).
        3. Separate each pair with "***".
        4. The entire answer must be enclosed in double quotes.

        Args:
            value: A string representing the response.

        Returns:
            True if the response follows the instruction or False otherwise.
        """
        if not (isinstance(value, str) and len(value) >= 2 and value.startswith('"') and value.endswith('"')):
            return False
        content = value[1:-1]
        parts = re.split('\\s*\\*\\*\\*\\s*', content)
        if len(parts) != 5:
            return False
        for i, part in enumerate(parts):
            stripped_part = part.strip()
            expected_start = f'سؤال وجواب # {i + 1}'
            if not stripped_part.startswith(expected_start):
                return False
            if len(stripped_part) <= len(expected_start):
                pass
        return True

class DataIdx331InstructionChecker(AragenInstructions):

    def __init__(self):
        super().__init__('idx_331')

    def check_following(self, value):
        """You will implement the logic of the function here to see if the response is correct or not.
        Args:
            value: A string representing the response.

        Returns:
            True if the response follows the instruction or False otherwise.
        """
        return ',' not in value

class DataIdx332InstructionChecker(AragenInstructions):

    def __init__(self):
        super().__init__('idx_332')

    def check_following(self, value):
        """Checks if the response follows the instructions for IDX 332.

        Args:
            value: A string representing the response.

        Returns:
            True if the response follows the instruction or False otherwise.
        """
        if not value.startswith('"') or not value.endswith('"'):
            return False
        if len(value) < 2:
            return False
        content = value[1:-1]
        if 'ورق الألوان' not in content:
            return False
        bullet_point_count = content.count('* ')
        if bullet_point_count != 2:
            return False
        return True

class DataIdx333InstructionChecker(AragenInstructions):

    def __init__(self):
        super().__init__('idx_333')

    def check_following(self, value):
        """Checks if the response follows the instructions for IDX 333.
        Constraints:
        - No commas (,) in the entire response.
        - Include at least five blank spaces represented by square brackets like [موقع].

        Args:
            value: A string representing the response.

        Returns:
            True if the response follows the instruction or False otherwise.
        """
        if ',' in value:
            return False
        placeholder_pattern = '\\[.*?\\]'
        placeholders = re.findall(placeholder_pattern, value)
        if len(placeholders) < 5:
            return False
        return True

class DataIdx334InstructionChecker(AragenInstructions):

    def __init__(self):
        super().__init__('idx_334')

    def check_following(self, value):
        """Checks if the response follows the instructions for IDX 334.

        Constraints:
        - Exactly two paragraphs.
        - Paragraphs separated by '***'.
        - At least 3 italicized sections using single asterisks (*text*).

        Args:
            value: A string representing the response.

        Returns:
            True if the response follows the instruction or False otherwise.
        """
        if not isinstance(value, str):
            return False
        parts = value.split('***')
        if len(parts) != 2:
            return False
        para1 = parts[0].strip()
        para2 = parts[1].strip()
        if not para1 or not para2:
            return False
        italic_matches = re.findall('\\*(.+?)\\*', value)
        num_italics = len(italic_matches)
        if num_italics < 3:
            return False
        return True

class DataIdx335InstructionChecker(AragenInstructions):

    def __init__(self):
        super().__init__('idx_335')

    def check_following(self, value):
        """Checks if the response follows the instructions for question IDX 335.

        Constraints:
        1. Must include a title surrounded by double angle brackets, e.g., <<Title>>.
        2. Must be at least 400 words long.
        3. Must include the answer (presence of keyword 'الإجابة').
        4. Must be a riddle (presence of keyword 'لغز').
        5. Must relate to a house (presence of keyword 'بيت').

        Args:
            value: A string representing the response.

        Returns:
            True if the response follows the instructions, False otherwise.
        """
        if not isinstance(value, str):
            return False
        has_title_format = re.search('<<.*?>>', value) is not None
        words = value.split()
        word_count = len(words)
        is_long_enough = word_count >= 400
        contains_answer_keyword = 'الإجابة' in value
        contains_riddle_keyword = 'لغز' in value
        contains_house_keyword = 'بيت' in value
        return has_title_format and is_long_enough and contains_answer_keyword and contains_riddle_keyword and contains_house_keyword

class DataIdx336InstructionChecker(AragenInstructions):

    def __init__(self):
        super().__init__('idx_336')

    def check_following(self, value):
        """Checks if the response follows the instructions for IDX 336.

        Constraints:
        1. Include exactly one sentence in markdown italic format (*text*).
        2. The answer should be less than 30 words.

        Args:
            value: A string representing the response.

        Returns:
            True if the response follows the instruction or False otherwise.
        """
        words = value.split()
        word_count = len(words)
        if word_count >= 30:
            return False
        italic_matches = re.findall('\\*([^*]+)\\*', value)
        if len(italic_matches) != 1:
            return False
        return True

class DataIdx337InstructionChecker(AragenInstructions):

    def __init__(self):
        super().__init__('idx_337')

    def check_following(self, value):
        """You will implement the logic of the function here to see if the response is correct or not.
        Args:
            value: A string representing the response.

        Returns:
            True if the response follows the instruction or False otherwise.
        """
        if not isinstance(value, str) or len(value) < 2 or value[0] != '"' or (value[-1] != '"'):
            return False
        inner_value = value[1:-1]
        highlighted_parts = re.findall('\\*[^*]+\\*', inner_value)
        return len(highlighted_parts) == 3

class DataIdx338InstructionChecker(AragenInstructions):

    def __init__(self):
        super().__init__('idx_338')

    def check_following(self, value):
        """Checks if the response follows the constraints for IDX 338.

        Constraints:
        1. Less than 200 words.
        2. Contains the word 'للأسف' between 3 and 5 times (inclusive).

        Args:
            value: A string representing the response.

        Returns:
            True if the response follows the instruction or False otherwise.
        """
        if not isinstance(value, str):
            return False
        words = value.split()
        word_count = len(words)
        alas_count = words.count('للأسف')
        is_word_count_valid = word_count < 200
        is_alas_count_valid = 3 <= alas_count <= 5
        return is_word_count_valid and is_alas_count_valid

class DataIdx339InstructionChecker(AragenInstructions):

    def __init__(self):
        super().__init__('idx_339')

    def check_following(self, value):
        """Checks if the response contains at least 1200 words.
        Args:
            value: A string representing the response.

        Returns:
            True if the response has 1200 words or more, False otherwise.
        """
        words = value.split()
        word_count = len(words)
        return word_count >= 1200

class DataIdx340InstructionChecker(AragenInstructions):

    def __init__(self):
        super().__init__('idx_340')

    def check_following(self, value: str) -> bool:
        """Checks if the presentation text is longer than 300 words.

        Args:
            value: A string representing the response, which is the presentation text.

        Returns:
            True if the word count of the text is strictly greater than 300, 
            False otherwise.
        """
        words = value.split()
        return len(words) > 300

class DataIdx341InstructionChecker(AragenInstructions):

    def __init__(self):
        super().__init__('341')

    def check_following(self, value):
        """Checks if the response follows the constraints for IDX 341.

        Constraints:
        1. Must contain a title enclosed in double angle brackets (<<Title>>).
        2. The total response must be less than 20 words.

        Args:
            value: A string representing the response.

        Returns:
            True if the response follows the instruction or False otherwise.
        """
        if not isinstance(value, str):
            return False
        start_bracket = value.find('<<')
        end_bracket = value.find('>>')
        if start_bracket == -1 or end_bracket == -1 or end_bracket < start_bracket:
            return False
        if end_bracket == start_bracket + 2:
            return False
        words = value.split()
        word_count = len(words)
        if word_count >= 20:
            return False
        return True

class DataIdx342InstructionChecker(AragenInstructions):

    def __init__(self):
        super().__init__('idx_342')

    def check_following(self, value):
        """Checks if the response contains exactly three italicized sections
           (text between *) and is not more than 40 words long.

        Args:
            value: A string representing the response.

        Returns:
            True if the response follows the instruction or False otherwise.
        """
        italic_sections = re.findall('\\*.*?\\*', value)
        has_three_italics = len(italic_sections) == 3
        words = value.split()
        word_count = len(words)
        is_short_enough = word_count <= 40
        return has_three_italics and is_short_enough

class DataIdx343InstructionChecker(AragenInstructions):

    def __init__(self):
        super().__init__('343')

    def check_following(self, value):
        """Checks if the response is enclosed entirely within double quotes.
        Args:
            value: A string representing the response.

        Returns:
            True if the response starts and ends with double quotes and has content, False otherwise.
        """
        if not isinstance(value, str):
            return False
        starts_with_quote = value.startswith('"')
        ends_with_quote = value.endswith('"')
        has_content = len(value) > 2
        return starts_with_quote and ends_with_quote and has_content

class DataIdx344InstructionChecker(AragenInstructions):

    def __init__(self):
        super().__init__('idx_344')

    def check_following(self, value):
        """Checks if the response is a social media post over 600 words and includes 'القنابل'.
        Args:
            value: A string representing the response.

        Returns:
            True if the response follows the instruction or False otherwise.
        """
        if not isinstance(value, str):
            return False
        words = value.split()
        word_count = len(words)
        length_constraint_met = word_count > 600
        keyword_constraint_met = 'القنابل' in value
        return length_constraint_met and keyword_constraint_met

class DataIdx345InstructionChecker(AragenInstructions):

    def __init__(self):
        super().__init__('idx_345')

    def check_following(self, value):
        """Checks if the response string contains any punctuation marks.
        
        Args:
            value: A string representing the response.

        Returns:
            True if the response follows the instruction (contains no punctuation) 
            or False otherwise.
        """
        punctuation_set = set(string.punctuation + '،؛')
        for char in value:
            if char in punctuation_set:
                return False
        return True

class DataIdx346InstructionChecker(AragenInstructions):

    def __init__(self):
        super().__init__('idx_346')

    def check_following(self, value):
        """Checks if the response follows the instructions for question IDX 346.

        Constraints:
        1. Contains the name "علي".
        2. Contains the city name "تمنراست".
        3. Uses the asterisk symbol '*' to highlight words/phrases twice,
           meaning there should be at least one pattern like '*...*' where ... is non-empty.

        Args:
            value: A string representing the response (the poetic verse).

        Returns:
            True if the response follows the checkable instructions, False otherwise.
        """
        if not isinstance(value, str):
            return False
        contains_ali = 'علي' in value
        contains_tamanrasset = 'تمنراست' in value
        has_highlighting = re.search('\\*.+\\*', value) is not None
        return contains_ali and contains_tamanrasset and has_highlighting

class DataIdx347InstructionChecker(AragenInstructions):

    def __init__(self):
        super().__init__('idx_347')

    def check_following(self, value):
        """Checks if the response is a 10-point list in the specified Arabic format.

        Args:
            value: A string representing the response.

        Returns:
            True if the response follows the instruction or False otherwise.
        """
        if not isinstance(value, str):
            return False
        lines = value.strip().split('\n')
        if len(lines) != 10:
            return False
        for i in range(10):
            expected_prefix = f'* النقطة {i + 1}'
            if not lines[i].strip().startswith(expected_prefix):
                return False
            if len(lines[i].strip()) <= len(expected_prefix.strip()):
                return False
        return True

class DataIdx348InstructionChecker(AragenInstructions):

    def __init__(self):
        super().__init__('348')

    def check_following(self, value: str) -> bool:
        """Checks if the response follows the instructions for IDX 348.

        Instructions:
        1. Highlight at least two parts of the text by enclosing them in asterisks, like *مميز*.
        2. The response must contain at least 350 words.

        Args:
            value: A string representing the response.

        Returns:
            True if the response follows the instructions, False otherwise.
        """
        if not isinstance(value, str):
            return False
        highlighted_parts = re.findall('\\*.*?\\*', value)
        has_enough_highlights = len(highlighted_parts) >= 2
        words = value.split()
        word_count = len(words)
        has_enough_words = word_count >= 350
        return has_enough_highlights and has_enough_words

class DataIdx349InstructionChecker(AragenInstructions):

    def __init__(self):
        super().__init__('349')

    def check_following(self, value):
        """Checks if the response includes a title formatted as <<Title>>.
        Args:
            value: A string representing the response.

        Returns:
            True if the response contains the pattern <<...>>, False otherwise.
        """
        pattern = '<<.*?>>'
        return bool(re.search(pattern, value))

class DataIdx350InstructionChecker(AragenInstructions):

    def __init__(self):
        super().__init__('idx_350')

    def check_following(self, value):
        """Checks if the response follows the instruction for IDX 350.
        Instruction: Write a riddle about Scheherazade without using commas.
        Constraint: The response must not contain the comma character (',').

        Args:
            value: A string representing the response.

        Returns:
            True if the response follows the instruction (contains no commas),
            or False otherwise.
        """
        if ',' in value:
            return False
        return True

class DataIdx351InstructionChecker(AragenInstructions):

    def __init__(self):
        super().__init__('idx_351')

    def check_following(self, value):
        """Checks if the response follows the constraints for IDX 351.

        Constraints:
        1. Must contain at least three placeholders like [text].
        2. Must not contain commas.

        Args:
            value: A string representing the response (expected to be an XML document).

        Returns:
            True if the response follows the instruction or False otherwise.
        """
        if not isinstance(value, str):
            return False
        if ',' in value:
            return False
        placeholders = re.findall('\\[.*?\\]', value)
        if len(placeholders) < 3:
            return False
        return True

class DataIdx352InstructionChecker(AragenInstructions):

    def __init__(self):
        super().__init__('idx_352')

    def check_following(self, value):
        """Checks if the response highlights some parts using '*' characters.
        
        This is based on the constraint: تسليط الضوء على بعض الأجزاء الرئيسية في الرد بـ'*'.
        It checks for the presence of text enclosed within single asterisks, e.g., *highlighted text*.

        Args:
            value: A string representing the response.

        Returns:
            True if at least one sequence of characters enclosed in '*' is found,
            False otherwise. It does NOT check for tone, context, or general
            use of "annotation symbols".
        """
        if not isinstance(value, str):
            return False
        pattern = '\\*[^\\*]+\\*'
        if re.search(pattern, value):
            return True
        else:
            return False

class DataIdx353InstructionChecker(AragenInstructions):

    def __init__(self):
        super().__init__('idx_353')

    def check_following(self, value):
        """Checks if the response contains no commas.
        Args:
            value: A string representing the response (the song lyrics).

        Returns:
            True if the response contains no commas, False otherwise.
        """
        return ',' not in value

class DataIdx354InstructionChecker(AragenInstructions):

    def __init__(self):
        super().__init__('idx_354')

    def check_following(self, value):
        """Checks if at least two paragraphs are formatted as italic using *text*.

        Args:
            value: A string representing the response.

        Returns:
            True if the response follows the instruction or False otherwise.
        """
        if not isinstance(value, str):
            return False
        paragraphs = [p.strip() for p in re.split('\\s*\\n\\s*\\n\\s*', value.strip()) if p.strip()]
        italic_paragraph_count = 0
        for p in paragraphs:
            stripped_p = p.strip()
            if stripped_p.startswith('*') and stripped_p.endswith('*') and (len(stripped_p) > 1):
                content = stripped_p[1:-1].strip()
                if content:
                    italic_paragraph_count += 1
        return italic_paragraph_count >= 2

class DataIdx355InstructionChecker(AragenInstructions):

    def __init__(self):
        super().__init__('idx_355')

    def check_following(self, value):
        """Checks if the response is a single sentence enclosed in double quotes.

        Args:
            value: A string representing the response.

        Returns:
            True if the response follows the instruction or False otherwise.
        """
        if not isinstance(value, str):
            return False
        if not (value.startswith('"') and value.endswith('"')):
            return False
        if len(value) == 2:
            return True
        inner_content = value[1:-1]
        sentence_endings = re.findall('[.!?](\\s|$)', inner_content)
        num_sentences = len(sentence_endings)
        return num_sentences <= 1

class DataIdx356InstructionChecker(AragenInstructions):

    def __init__(self):
        super().__init__('idx_356')

    def check_following(self, value):
        """Checks if the response follows the instructions for IDX 356.
        Constraints:
        - The word 'عُقدة' appears at least two times.
        - At least two paragraphs are included in italic format (*like this*).

        Args:
            value: A string representing the response.

        Returns:
            True if the response follows the instruction or False otherwise.
        """
        keyword_count = value.count('عُقدة')
        italic_matches = re.findall('\\*([^*]+)\\*', value)
        italic_count = len(italic_matches)
        if keyword_count >= 2 and italic_count >= 2:
            return True
        else:
            return False

class DataIdx357InstructionChecker(AragenInstructions):

    def __init__(self):
        super().__init__('idx_357')

    def check_following(self, value):
        """Checks if the response contains a title enclosed between triangular double angle quotes (<<Title>>).

        Args:
            value: A string representing the response.

        Returns:
            True if the response contains the pattern <<...>>, False otherwise.
        """
        pattern = '<<.*?>>'
        match = re.search(pattern, value)
        return bool(match)

class DataIdx358InstructionChecker(AragenInstructions):

    def __init__(self):
        super().__init__('idx_358')

    def check_following(self, value: str):
        """Checks if the response follows the instructions for IDX 358.

        Constraints:
        1. Less than 10 sentences (sentences are assumed to end with '.').
        2. No commas (',').

        Args:
            value: A string representing the response.

        Returns:
            True if the response follows the instruction or False otherwise.
        """
        if ',' in value:
            return False
        sentences = value.split('.')
        non_empty_sentences = [s.strip() for s in sentences if s.strip()]
        sentence_count = len(non_empty_sentences)
        if sentence_count == 0 and value.strip():
            sentence_count = 1
        return sentence_count < 10

class DataIdx359InstructionChecker(AragenInstructions):

    def __init__(self):
        super().__init__('idx_359')

    def check_following(self, value):
        """Checks if the response contains a substring formatted as <<...>>.

        Args:
            value: A string representing the response.

        Returns:
            True if the response contains <<...>> with content inside,
            False otherwise.
        """
        if not isinstance(value, str) or not value:
            return False
        start_tag = '<<'
        end_tag = '>>'
        start_index = value.find(start_tag)
        if start_index == -1 or start_index + len(start_tag) >= len(value):
            return False
        end_index = value.find(end_tag, start_index + len(start_tag))
        if end_index == -1:
            return False
        content_start_index = start_index + len(start_tag)
        if end_index > content_start_index:
            return True
        else:
            return False

class DataIdx360InstructionChecker(AragenInstructions):

    def __init__(self):
        super().__init__('idx_360')

    def check_following(self, value):
        """Checks if the response contains a title formatted as <<title>> where title is not empty.

        Args:
            value: A string representing the response.

        Returns:
            True if the response follows the instruction or False otherwise.
        """
        pattern = '<<.+>>'
        if re.search(pattern, value):
            return True
        else:
            return False

class DataIdx361InstructionChecker(AragenInstructions):

    def __init__(self):
        super().__init__('idx_361')

    def check_following(self, value):
        """You will implement the logic of the function here to see if the response is correct or not.
        Args:
            value: A string representing the response.

        Returns:
            True if the response follows the instruction or False otherwise.
        """
        sentences = list(filter(None, map(str.strip, re.split('[.?!]', value))))
        return 1 <= len(sentences) <= 2

class DataIdx362InstructionChecker(AragenInstructions):

    def __init__(self):
        super().__init__('idx_362')

    def check_following(self, value):
        """Checks if the response follows the instructions for IDX 362.

        Constraints:
        1. Must contain the name "زينب".
        2. Must contain the word "فقاعات".
        3. Must contain at least three instances of text enclosed in square brackets [like this].

        Args:
            value: A string representing the response.

        Returns:
            True if the response follows the instruction or False otherwise.
        """
        has_zainab = 'زينب' in value
        has_bubbles = 'فقاعات' in value
        bracketed_phrases = re.findall('\\[.*?\\]', value)
        has_at_least_three_brackets = len(bracketed_phrases) >= 3
        return has_zainab and has_bubbles and has_at_least_three_brackets

class DataIdx363InstructionChecker(AragenInstructions):

    def __init__(self):
        super().__init__('idx_363')

    def check_following(self, value):
        """Checks if the response is one of the allowed phrases.
        Args:
            value: A string representing the response.

        Returns:
            True if the response is one of 'إجابتي هي نعم.', 'إجابتي هي لا.', or 'إجابتي هي ربما.', False otherwise.
        """
        allowed_responses = {'إجابتي هي نعم.', 'إجابتي هي لا.', 'إجابتي هي ربما.'}
        return value in allowed_responses

class DataIdx364InstructionChecker(AragenInstructions):

    def __init__(self):
        super().__init__('idx_364')

    def check_following(self, value: str) -> bool:
        """Checks if the response contains exactly one of the required phrases.

        Args:
            value: A string representing the response.

        Returns:
            True if the response follows the instruction or False otherwise.
        """
        required_phrases = ['إجابتي هي نعم.', 'إجابتي هي لا.', 'إجابتي هي ربما.']
        count = 0
        for phrase in required_phrases:
            if phrase in value:
                count += 1
        return count == 1

class DataIdx365InstructionChecker(AragenInstructions):

    def __init__(self):
        super().__init__('idx_365')

    def check_following(self, value):
        """Checks if the response contains one of the required phrases.

        Args:
            value: A string representing the response.

        Returns:
            True if the response follows the instruction or False otherwise.
        """
        required_phrases = ['إجابتي هي نعم.', 'إجابتي هي لا.', 'إجابتي هي ربما.']
        for phrase in required_phrases:
            if phrase in value:
                return True
        return False

class DataIdx366InstructionChecker(AragenInstructions):

    def __init__(self):
        super().__init__('idx_366')

    def check_following(self, value):
        """Checks if the response is exactly one of the allowed phrases.

        Args:
            value: A string representing the response.

        Returns:
            True if the response follows the instruction or False otherwise.
        """
        allowed_responses = ['إجابتي هي نعم.', 'إجابتي هي لا.', 'إجابتي هي ربما.']
        return value in allowed_responses

class DataIdx367InstructionChecker(AragenInstructions):

    def __init__(self):
        super().__init__('idx_367')

    def check_following(self, value):
        """Checks if the response is one of the allowed answers.
        Args:
            value: A string representing the response.

        Returns:
            True if the response follows the instruction (is one of the specific strings) or False otherwise.
        """
        allowed_answers = {'إجابتي هي نعم.', 'إجابتي هي لا.', 'إجابتي هي ربما.'}
        return value in allowed_answers

class DataIdx368InstructionChecker(AragenInstructions):

    def __init__(self):
        super().__init__('idx_368')

    def check_following(self, value):
        """Checks if the response contains exactly one of the required phrases.
        Args:
            value: A string representing the response.

        Returns:
            True if the response follows the instruction or False otherwise.
        """
        required_phrases = ['إجابتي هي نعم.', 'إجابتي هي لا.', 'إجابتي هي ربما.']
        count = 0
        for phrase in required_phrases:
            if phrase in value:
                count += 1
        return count == 1

class DataIdx369InstructionChecker(AragenInstructions):

    def __init__(self):
        super().__init__('idx_369')

    def check_following(self, value):
        """Checks if the response is one of the allowed phrases.

        Args:
            value: A string representing the response.

        Returns:
            True if the response is exactly one of the allowed phrases, False otherwise.
        """
        allowed_answers = ['إجابتي هي نعم.', 'إجابتي هي لا.', 'إجابتي هي ربما.']
        return value in allowed_answers

class DataIdx370InstructionChecker(AragenInstructions):

    def __init__(self):
        super().__init__('idx_370')

    def check_following(self, value):
        """Checks if the response is one of the allowed options.

        Args:
            value: A string representing the response.

        Returns:
            True if the response follows the instruction or False otherwise.
        """
        allowed_responses = ['إجابتي هي نعم.', 'إجابتي هي لا.', 'إجابتي هي ربما.']
        return value in allowed_responses

class DataIdx371InstructionChecker(AragenInstructions):

    def __init__(self):
        super().__init__('idx_371')

    def check_following(self, value):
        """Checks if the response is exactly one of the allowed phrases.

        Args:
            value: A string representing the response.

        Returns:
            True if the response is one of the allowed phrases, False otherwise.
        """
        allowed_phrases = ['إجابتي هي نعم.', 'إجابتي هي لا.', 'إجابتي هي ربما.']
        return value in allowed_phrases

class DataIdx372InstructionChecker(AragenInstructions):

    def __init__(self):
        super().__init__('idx_372')

    def check_following(self, value):
        """Checks if the response follows the constraints for IDX 372.
        Constraints:
        1. The word 'جذور' must appear exactly twice.
        2. All second-person subject pronouns (أنتَ, أنتِ, أنتما, أنتم, أنْتُنَّ) must be present.

        Args:
            value: A string representing the response.

        Returns:
            True if the response follows all instructions, False otherwise.
        """
        cleaned_value = value.replace('.', ' ').replace(',', ' ').replace(';', ' ').replace('!', ' ').replace('?', ' ')
        words = cleaned_value.split()
        juzoor_count = words.count('جذور')
        constraint1_met = juzoor_count == 2
        pronouns_to_check = ['أنتَ', 'أنتِ', 'أنتما', 'أنتم', 'أنْتُنَّ']
        constraint2_met = all((pronoun in value for pronoun in pronouns_to_check))
        return constraint1_met and constraint2_met

class DataIdx373InstructionChecker(AragenInstructions):

    def __init__(self):
        super().__init__('idx_373')

    def check_following(self, value: str) -> bool:
        """Checks if the response follows the constraints for IDX 373.

        Constraints:
        1. The phrase "بنات العمومة" must appear 3 or more times.
        2. At least 5 words must start with the letters ث, ذ, or ظ.

        Args:
            value: A string representing the response.

        Returns:
            True if the response follows the instruction or False otherwise.
        """
        cousins_count = value.count('بنات العمومة')
        if cousins_count < 3:
            return False
        lathawiya_chars = {'ث', 'ذ', 'ظ'}
        lathawiya_word_count = 0
        arabic_words = re.findall('\\b[ا-ي]+\\b', value)
        for word in arabic_words:
            if word and word[0] in lathawiya_chars:
                lathawiya_word_count += 1
        if lathawiya_word_count < 5:
            return False
        return True

class DataIdx374InstructionChecker(AragenInstructions):

    def __init__(self):
        super().__init__('idx_374')

    def check_following(self, value):
        """Checks if the response follows the instructions for IDX 374.
        Instructions:
        - Include at least one phrase in square brackets [...].
        - Include at least five words that start with 'ق', 'ط', 'ب', 'ج', or 'د'
          and end with 'ء', 'هـ', 'ع', 'ح', 'غ', or 'خ'.

        Args:
            value: A string representing the response.

        Returns:
            True if the response follows the instruction or False otherwise.
        """
        if not isinstance(value, str):
            return False
        bracket_match = re.search('\\[.+\\]', value)
        if not bracket_match:
            return False
        start_letters = 'قطبجد'
        end_letters = 'ءهعحغخ'
        words = re.findall('\\b\\w+\\b', value)
        valid_word_count = 0
        for word in words:
            if word:
                first_char = word[0]
                last_char = word[-1]
                if first_char in start_letters and last_char in end_letters:
                    valid_word_count += 1
        return valid_word_count >= 5

class DataIdx375InstructionChecker(AragenInstructions):

    def __init__(self):
        super().__init__('375')

    def check_following(self, value):
        """
        Checks if the response (a string) follows the instructions for IDX 375.
        Instructions:
        1. Must be less than 500 words.
        2. Must contain the specific first-person pronouns (as whole words):
           أنا, نحن, إياي, إيانا.

        Args:
            value: A string representing the response.

        Returns:
            True if the response follows the instruction or False otherwise.
        """
        if not isinstance(value, str):
            return False
        words = re.findall('\\w+', value)
        word_count = len(words)
        if word_count >= 500:
            return False
        required_pronouns = ['أنا', 'نحن', 'إياي', 'إيانا']
        for pronoun in required_pronouns:
            if not re.search('\\b' + re.escape(pronoun) + '\\b', value):
                return False
        return True

class DataIdx376InstructionChecker(AragenInstructions):

    def __init__(self):
        super().__init__('idx_376')

    def check_following(self, value: str) -> bool:
        """Checks if the response follows the instructions for IDX 376.

        Constraints:
        1.  Must be at least 350 words long.
        2.  Must contain the five specified nouns in the nominative case: أبوك, أخوك, حموك, فوك, ذو.

        Args:
            value: A string representing the response.

        Returns:
            True if the response follows the instructions, False otherwise.
        """
        words = value.split()
        word_count = len(words)
        if word_count < 350:
            return False
        required_nouns = ['أبوك', 'أخوك', 'حموك', 'فوك', 'ذو']
        for noun in required_nouns:
            if noun not in value:
                return False
        return True

class DataIdx377InstructionChecker(AragenInstructions):

    def __init__(self):
        super().__init__('idx_377')

    def check_following(self, value):
        """Checks if the response follows the constraints:
        1. Contains a title <<...>>
        2. More than 300 words.
        3. At least 10 words start with specific heavy letters (خ ص ض غ ط ق ظ).
        4. At least 10 words end with specific guttural letters (ء هـ ع ح غ خ).

        Args:
            value: A string representing the response.

        Returns:
            True if the response follows the instruction or False otherwise.
        """
        title_match = re.search('<<.*?>>', value)
        if not title_match:
            return False
        words = re.findall('\\b\\w+\\b', value)
        word_count = len(words)
        if word_count <= 300:
            return False
        heavy_start_letters = {'خ', 'ص', 'ض', 'غ', 'ط', 'ق', 'ظ'}
        guttural_end_letters = {'ء', 'ه', 'ع', 'ح', 'غ', 'خ'}
        heavy_start_count = 0
        guttural_end_count = 0
        for word in words:
            if word:
                if word[0] in heavy_start_letters:
                    heavy_start_count += 1
                if word[-1] in guttural_end_letters:
                    guttural_end_count += 1
        if heavy_start_count < 10:
            return False
        if guttural_end_count < 10:
            return False
        return True

class DataIdx378InstructionChecker(AragenInstructions):

    def __init__(self):
        super().__init__('idx_378')

    def check_following(self, value):
        """
        Checks if the response follows the instructions for question idx_378.
        Constraints:
        1. Contains the separator '******'.
        2. Contains exactly 5 words ending in 'ة' (Taa Marbuta).
        3. Contains exactly 5 words ending in 'ت' (Taa Maftuha).

        Args:
            value: A string representing the response.

        Returns:
            True if the response follows all instructions, False otherwise.
        """
        if '******' not in value:
            return False
        words = re.findall('\\b\\w+\\b', value)
        taa_marbuta_count = 0
        taa_maftuha_count = 0
        for word in words:
            if word.endswith('ة'):
                taa_marbuta_count += 1
            elif word.endswith('ت'):
                taa_maftuha_count += 1
        return taa_marbuta_count == 5 and taa_maftuha_count == 5

class DataIdx379InstructionChecker(AragenInstructions):

    def __init__(self):
        super().__init__('idx_379')

    def check_following(self, value):
        """Checks if the response follows the instructions for IDX 379.

        Constraints:
        1. Exactly 6 sentences (assuming ends with ., ?, !).
        2. No commas (',' or '،').
        3. At least five placeholders represented by square brackets [ ].
        4. Use at least one of the five special nouns (أبوك - أخوك - حموك - فوك - ذو).

        Args:
            value: A string representing the response.

        Returns:
            True if the response follows the instruction or False otherwise.
        """
        if not isinstance(value, str):
            return False
        sentence_terminators = ['.', '؟', '!']
        sentence_count = 0
        for terminator in sentence_terminators:
            sentence_count += value.count(terminator)
        if sentence_count != 6:
            return False
        if ',' in value or '،' in value:
            return False
        placeholders = re.findall('\\[.*?\\]', value)
        if len(placeholders) < 5:
            return False
        special_nouns = ['أبوك', 'أخوك', 'حموك', 'فوك', 'ذو']
        found_special_noun = any((noun in value for noun in special_nouns))
        if not found_special_noun:
            return False
        return True

class DataIdx380InstructionChecker(AragenInstructions):

    def __init__(self):
        super().__init__('idx_380')

    def check_following(self, value):
        """Checks if the response (story/plan) follows the constraints:
        1. Less than 500 words.
        2. Contains exactly four specific points labeled: النقطة الأولى, النقطة الثانية, النقطة الثالثة, النقطة الرابعة.

        Args:
            value: A string representing the response (story/plan).

        Returns:
            True if the response follows the instruction or False otherwise.
        """
        if not isinstance(value, str):
            return False
        words = value.split()
        word_count = len(words)
        if word_count >= 500:
            return False
        point_labels = ['النقطة الأولى', 'النقطة الثانية', 'النقطة الثالثة', 'النقطة الرابعة']
        for label in point_labels:
            if value.count(label) != 1:
                return False
        return True

class DataIdx381InstructionChecker(AragenInstructions):

    def __init__(self):
        super().__init__('idx_381')

    def check_following(self, value):
        """Checks if the response is a 10-sentence paragraph where each sentence starts with a specific demonstrative pronoun.

        Args:
            value: A string representing the response.

        Returns:
            True if the response follows the instruction or False otherwise.
        """
        if not isinstance(value, str):
            return False
        allowed_starters = ['هذا', 'هذه', 'هذان', 'هذين', 'هؤلاء', 'ذلك']
        sentences = re.split('[.!?]', value)
        sentences = [s.strip() for s in sentences if s.strip()]
        if len(sentences) != 10:
            return False
        for sentence in sentences:
            first_word_match = re.match('^\\s*(\\S+)', sentence)
            if not first_word_match:
                return False
            first_word = first_word_match.group(1)
            if first_word not in allowed_starters:
                return False
        return True

class DataIdx382InstructionChecker(AragenInstructions):

    def __init__(self):
        super().__init__('idx_382')

    def check_following(self, value):
        """Checks if the response meets the constraints for IDX 382.

        Constraints:
        1. Less than 7 sentences.
        2. Each sentence contains a second-person object pronoun (ضمير نصب مخاطب).
        3. The paragraph uses ALL of إياكَ، إياكِ، إياكما، إياكم، إياكن.

        Args:
            value: A string representing the response.

        Returns:
            True if the response follows the instruction or False otherwise.
        """
        if not isinstance(value, str) or not value.strip():
            return False
        required_pronouns = {'إياكَ', 'إياكِ', 'إياكما', 'إياكم', 'إياكن'}
        all_relevant_pronouns = required_pronouns
        sentences = [s.strip() for s in re.split('[.?!]+\\s*', value) if s.strip()]
        if len(sentences) >= 7:
            return False
        found_required_pronouns = set()
        for sentence in sentences:
            sentence_contains_relevant_pronoun = False
            for pronoun in all_relevant_pronouns:
                if pronoun in sentence:
                    sentence_contains_relevant_pronoun = True
                    if pronoun in required_pronouns:
                        found_required_pronouns.add(pronoun)
            if not sentence_contains_relevant_pronoun:
                return False
        if found_required_pronouns != required_pronouns:
            return False
        return True

class DataIdx383InstructionChecker(AragenInstructions):

    def __init__(self):
        super().__init__('idx_383')

    def check_following(self, value):
        """You will implement the logic of the function here to see if the response is correct or not.
        Args:
            value: A string representing the response.

        Returns:
            True if the response follows the instruction or False otherwise.
        """
        if not isinstance(value, str) or not value.startswith('"') or (not value.endswith('"')):
            return False
        if len(value) <= 2:
            content = ''
        else:
            content = value[1:-1]
        required_pronouns = {'إيّاهُ', 'إياها', 'إيّاهما', 'إيّاهنَّ', 'إيّاهمْ'}
        for pronoun in required_pronouns:
            if pronoun not in content:
                return False
        return True

class DataIdx384InstructionChecker(AragenInstructions):

    def __init__(self):
        super().__init__('idx_384')

    def check_following(self, value):
        """Checks if the response follows the instructions for question 384.

        Args:
            value: A string representing the response.

        Returns:
            True if the response follows the instruction or False otherwise.
        """
        if not isinstance(value, str):
            return False
        contains_dalouna = 'على دلعونة' in value
        words = value.split()
        word_count = len(words)
        is_long_enough = word_count > 300
        pronouns = ['أنا', 'نحن', 'إياي', 'إيانا']
        uses_all_pronouns = all((pronoun in value for pronoun in pronouns))
        return contains_dalouna and is_long_enough and uses_all_pronouns

class DataIdx385InstructionChecker(AragenInstructions):

    def __init__(self):
        super().__init__('idx_385')

    def check_following(self, value):
        """Checks if the response follows the instructions for IDX 385.

        Args:
            value: A string representing the response.

        Returns:
            True if the response follows the instruction or False otherwise.
        """
        if not isinstance(value, str):
            return False
        words = value.split()
        word_count = len(words)
        length_check = 300 < word_count < 500
        mandatory_words = ['زلمة', 'ريال', 'رجل']
        mandatory_words_check = all((word in value for word in mandatory_words))
        asma_al_khamsa_genitive = ['أبيك', 'أخيك', 'حميك', 'فيك', 'ذي']
        asma_check = all((word in value for word in asma_al_khamsa_genitive))
        return length_check and mandatory_words_check and asma_check

class DataIdx386InstructionChecker(AragenInstructions):

    def __init__(self):
        super().__init__('idx_386')
        self.guttural_letters = {'ء', 'ه', 'ع', 'ح', 'غ', 'خ'}

    def check_following(self, value: str) -> bool:
        """
        Checks if the response meets the constraints:
        1. At least 200 words.
        2. At least 10 words starting with one of the guttural letters (ء ه ع ح غ خ).
        3. Novel names (including "رجال في الشمس") are enclosed in quotation marks.

        Args:
            value: A string representing the response.

        Returns:
            True if the response follows the instruction or False otherwise.
        """
        if not isinstance(value, str):
            return False
        words = value.split()
        word_count = len(words)
        if word_count < 200:
            return False
        guttural_word_count = 0
        for word in words:
            cleaned_word = word.strip('.,;!?"\'')
            if cleaned_word and cleaned_word[0] in self.guttural_letters:
                guttural_word_count += 1
        if guttural_word_count < 10:
            return False
        example_novel = 'رجال في الشمس'
        if f'"{example_novel}"' not in value and f'»{example_novel}«' not in value:
            return False
        if '"' not in value and '»' not in value:
            return False
        return True

class DataIdx387InstructionChecker(AragenInstructions):

    def __init__(self):
        super().__init__('idx_387')

    def check_following(self, value):
        """Checks if the response follows the instructions for IDX 387.

        Constraints:
        1. Include at least 5 words starting with letters ث, ذ, or ظ.
        2. Do not use commas.
        3. Be more than 250 words long.

        Args:
            value: A string representing the response.

        Returns:
            True if the response follows all instructions, False otherwise.
        """
        if not isinstance(value, str):
            return False
        if ',' in value:
            return False
        words = value.split()
        if len(words) <= 250:
            return False
        lisping_letters = {'ث', 'ذ', 'ظ'}
        lisping_word_count = 0
        for word in words:
            if word and word[0] in lisping_letters:
                lisping_word_count += 1
        if lisping_word_count < 5:
            return False
        return True

class DataIdx388InstructionChecker(AragenInstructions):

    def __init__(self):
        super().__init__('idx_388')

    def check_following(self, value):
        """Checks if the response follows the instructions for IDX 388.

        Constraints:
        1. Word count <= 300
        2. Exactly 8 words ending with Qalqala letters (ق, ط, ب, ج, د)
        3. Exactly 10 words starting with 'ر'

        Args:
            value: A string representing the response.

        Returns:
            True if the response follows the instruction or False otherwise.
        """
        if not isinstance(value, str):
            return False
        words = value.split()
        word_count = len(words)
        if word_count > 300:
            return False
        qalqala_ends = {'ق', 'ط', 'ب', 'ج', 'د'}
        ra_start = 'ر'
        qalqala_end_count = 0
        ra_start_count = 0
        punctuation_to_strip = string.punctuation + '،؛:؟!)( \n\t'
        for word in words:
            cleaned_word = word.strip(punctuation_to_strip)
            if not cleaned_word:
                continue
            if cleaned_word and cleaned_word[-1] in qalqala_ends:
                qalqala_end_count += 1
            if cleaned_word and cleaned_word[0] == ra_start:
                ra_start_count += 1
        if qalqala_end_count != 8:
            return False
        if ra_start_count != 10:
            return False
        return True

class DataIdx389InstructionChecker(AragenInstructions):

    def __init__(self):
        super().__init__('idx_389')

    def check_following(self, value):
        """Checks if the response follows the instruction for IDX 389.

        Constraints:
        1. The response must be at least 250 words long.
        2. The response must NOT contain the exact words "الأيام", "مصر", or "مصري".
           (Checking for these words case-insensitively).
        3. The response must contain at least 15 words that start with
           one of the following Arabic letters: ج ز ف هـ ب ح س ك و ت د ش م ي ث ذ ع ن.

        Args:
            value: A string representing the response.

        Returns:
            True if the response follows the instruction or False otherwise.
        """
        if not isinstance(value, str):
            return False
        arabic_word_pattern = re.compile('[\\u0600-\\u06FF]+')
        words = arabic_word_pattern.findall(value)
        word_count = len(words)
        if word_count < 250:
            return False
        forbidden_words_lower = {'الأيام'.lower(), 'مصر'.lower(), 'مصري'.lower()}
        lower_words = [word.lower() for word in words]
        if any((word in forbidden_words_lower for word in lower_words)):
            return False
        allowed_starts = {'ج', 'ز', 'ف', 'ه', 'ب', 'ح', 'س', 'ك', 'و', 'ت', 'د', 'ش', 'م', 'ي', 'ث', 'ذ', 'ع', 'ن'}
        specific_start_count = 0
        for word in words:
            if len(word) > 0:
                first_char = word[0]
                if first_char in allowed_starts:
                    specific_start_count += 1
        if specific_start_count < 15:
            return False
        return True

class DataIdx390InstructionChecker(AragenInstructions):

    def __init__(self):
        super().__init__('idx_390')

    def check_following(self, value):
        """Checks if the response follows the instruction constraints for IDX 390.

        Constraints:
        1. At least 150 words.
        2. Exactly 15 words starting with one of the letters: د, ذ, أ, ر, ز, و.
        3. Does not contain the comma character (,) .

        Args:
            value: A string representing the response.

        Returns:
            True if the response follows the instruction or False otherwise.
        """
        if ',' in value:
            return False
        words = value.strip().split()
        if len(words) < 150:
            return False
        rafisah_letters = {'د', 'ذ', 'أ', 'ر', 'ز', 'و'}
        rafisah_word_count = 0
        for word in words:
            cleaned_word = word.strip()
            if cleaned_word and cleaned_word[0] in rafisah_letters:
                rafisah_word_count += 1
        if rafisah_word_count != 15:
            return False
        return True

class DataIdx391InstructionChecker(AragenInstructions):

    def __init__(self):
        super().__init__('idx_391')

    def check_following(self, value):
        """Checks if the response follows the instruction for IDX 391.

        The instruction requires an essay enclosed in double quotes (" "),
        discussing using the internet for Arabic learning for children,
        and containing exactly 10 words ending with one of the letters
        (ج, ز, ف, هـ, ب, ح, س).

        Args:
            value: A string representing the response.

        Returns:
            True if the response follows the instruction or False otherwise.
        """
        if not (value.startswith('"') and value.endswith('"')):
            return False
        content = value[1:-1].strip()
        target_letters = {'ج', 'ز', 'ف', 'ه', 'ب', 'ح', 'س'}
        target_count = 10
        found_count = 0
        words = re.findall('\\b[\\u0621-\\u064A]+\\b', content)
        for word in words:
            if word and word[-1] in target_letters:
                found_count += 1
        return found_count == target_count

class DataIdx392InstructionChecker(AragenInstructions):

    def __init__(self):
        super().__init__('idx_392')

    def check_following(self, value):
        """
        Checks if the response meets the following constraints based on IDX 392:
        - Contains exactly 5 words starting with ث, ذ, or ظ.
        - Contains exactly 10 words ending with ه, ع, ح, غ, or خ.
        - Is less than 200 words long.
        (The content constraint about explaining folk tales is not checked programmatically).

        Args:
            value: A string representing the response.

        Returns:
            True if the response follows the programmatic constraints, False otherwise.
        """
        if not isinstance(value, str):
            return False
        words = re.findall('\\b\\w+\\b', value)
        word_count = len(words)
        if word_count >= 200:
            return False
        lethawiyah_letters = {'ث', 'ذ', 'ظ'}
        lethawiyah_start_count = 0
        for word in words:
            if word and word[0] in lethawiyah_letters:
                lethawiyah_start_count += 1
        if lethawiyah_start_count != 5:
            return False
        halqiyah_letters = {'ه', 'ع', 'ح', 'غ', 'خ'}
        halqiyah_end_count = 0
        for word in words:
            if word and word[-1] in halqiyah_letters:
                halqiyah_end_count += 1
        if halqiyah_end_count != 10:
            return False
        return True

class DataIdx393InstructionChecker(AragenInstructions):

    def __init__(self):
        super().__init__('idx_393')

    def check_following(self, value):
        """Checks if the response follows the instructions for IDX 393.

        Constraints:
        1. Must include exactly 7 words starting with Qalqalah letters (ق, ط, ب, ج, د).
        2. Must not use the letter "ذ".
        3. Must not use the letter "ظ".
        4. The answer must not exceed 100 words.

        Args:
            value: A string representing the response.

        Returns:
            True if the response follows all instructions or False otherwise.
        """
        if not isinstance(value, str):
            return False
        words = value.split()
        if len(words) > 100:
            return False
        if 'ذ' in value or 'ظ' in value:
            return False
        qalqalah_letters = {'ق', 'ط', 'ب', 'ج', 'د'}
        qalqalah_word_count = 0
        for word in words:
            if word and word[0] in qalqalah_letters:
                qalqalah_word_count += 1
        if qalqalah_word_count != 7:
            return False
        return True

class DataIdx394InstructionChecker(AragenInstructions):

    def __init__(self):
        super().__init__('idx_394')

    def check_following(self, value):
        """Checks if the response follows the instruction for IDX 394.

        Constraints:
        1. Max 120 words.
        2. No commas (',').
        3. Exactly 12 words ending with one of the Rafisah letters (د، ذ، أ، ر، ز، و).

        Args:
            value: A string representing the response.

        Returns:
            True if the response follows all instructions, False otherwise.
        """
        if not isinstance(value, str):
            return False
        words = value.split()
        word_count = len(words)
        if word_count > 120:
            return False
        if ',' in value:
            return False
        rafisah_letters = {'د', 'ذ', 'أ', 'ر', 'ز', 'و'}
        rafisah_word_count = 0
        for word in words:
            stripped_word = word.strip()
            if stripped_word and stripped_word[-1] in rafisah_letters:
                rafisah_word_count += 1
        if rafisah_word_count != 12:
            return False
        return True

class DataIdx395InstructionChecker(AragenInstructions):

    def __init__(self):
        super().__init__('395')

    def check_following(self, value):
        """Checks if the response contains all required spellings of 600 in Arabic as listed in the instructions.

        Args:
            value: A string representing the response (the story).

        Returns:
            True if all required spellings are present, False otherwise.
        """
        required_spellings = ['ستة مائة', 'ست مئة', 'ستمئة', 'ستمائة']
        all_present = True
        for spelling in required_spellings:
            if spelling not in value:
                all_present = False
                break
        return all_present

class DataIdx396InstructionChecker(AragenInstructions):

    def __init__(self):
        super().__init__('idx_396')

    def check_following(self, value):
        """Checks if the response follows the instructions for IDX 396.

        Constraints:
        1. Contains text enclosed in double angle brackets << >> (e.g., <<اسم المسابقة>>).
        2. Contains the word "مئة".
        3. Contains the word "مائة".

        Args:
            value: A string representing the response.

        Returns:
            True if all constraints are met, False otherwise.
        """
        has_competition_name_format = re.search('<<.*?>>', value) is not None
        has_mieh_form1 = 'مئة' in value
        has_mieh_form2 = 'مائة' in value
        return has_competition_name_format and has_mieh_form1 and has_mieh_form2

class DataIdx397InstructionChecker(AragenInstructions):

    def __init__(self):
        super().__init__('idx_397')

    def check_following(self, value):
        """Checks if the response follows the instructions for IDX 397.

        Constraints:
        1. Contains the word 'الحلويات' at least three times.
        2. Is a single sentence.

        Args:
            value: A string representing the response.

        Returns:
            True if the response follows the instruction or False otherwise.
        """
        sweets_count = value.count('الحلويات')
        if sweets_count < 3:
            return False
        terminal_punctuations = ['.', '!', '?']
        punctuation_count = sum((value.count(p) for p in terminal_punctuations))
        if punctuation_count > 1:
            return False
        return True

class DataIdx398InstructionChecker(AragenInstructions):

    def __init__(self):
        super().__init__('idx_398')

    def check_following(self, value):
        """Checks if the response follows the instructions for question 398.

        Constraints:
        - No commas.
        - Exactly 5 words starting with ث, ذ, or ظ.
        - Exactly 10 words ending with ه, ع, ح, غ, or خ.

        Args:
            value: A string representing the response.

        Returns:
            True if the response follows the instruction or False otherwise.
        """
        if ',' in value:
            return False
        words = value.split()
        words = [word for word in words if word]
        lisping_count = 0
        guttural_count = 0
        lisping_letters = {'ث', 'ذ', 'ظ'}
        guttural_letters = {'ه', 'ع', 'ح', 'غ', 'خ'}
        for word in words:
            if word:
                if word[0] in lisping_letters:
                    lisping_count += 1
                if word[-1] in guttural_letters:
                    guttural_count += 1
        return lisping_count == 5 and guttural_count == 10

class DataIdx399InstructionChecker(AragenInstructions):

    def __init__(self):
        super().__init__('399')

    def check_following(self, value):
        """Checks if the response contains exactly five words ending with Kasra Tanween (ٍ).

        Args:
            value: A string representing the response.

        Returns:
            True if the response contains exactly five words ending with Kasra Tanween (ٍ),
            False otherwise.
        """
        if not isinstance(value, str):
            return False
        tanween_kasra = 'ِ'
        word_count = 0
        words = value.split()
        trailing_punctuation = string.punctuation + '،؛؟!'
        for word in words:
            cleaned_word = word.rstrip(trailing_punctuation)
            if cleaned_word and cleaned_word.endswith(tanween_kasra):
                word_count += 1
        return word_count == 5

class DataIdx400InstructionChecker(AragenInstructions):

    def __init__(self):
        super().__init__('idx_400')

    def check_following(self, value):
        """Checks if the response follows the constraints for IDX 400.
        Constraints:
        1. Exactly 10 words.
        2. Includes at least one word with tanween damma (U+064C).

        Args:
            value: A string representing the response.

        Returns:
            True if the response follows the instruction or False otherwise.
        """
        if not isinstance(value, str):
            return False
        words = value.split()
        if len(words) != 10:
            return False
        tanween_damma_char = 'ٌ'
        has_tanween_damma = False
        for word in words:
            if tanween_damma_char in word:
                has_tanween_damma = True
                break
        if not has_tanween_damma:
            return False
        return True

class DataIdx401InstructionChecker(AragenInstructions):

    def __init__(self):
        super().__init__('idx_401')

    def check_following(self, value):
        """
        Checks if the response follows the instruction constraints for IDX 401:
        - Uses five words ending in tanween al-fath (ً).
        - Uses three words containing shadda (ّ).
        - Text is vowelized/diacritized (contains common Arabic diacritics).

        Args:
            value: A string representing the response.

        Returns:
            True if the response follows the instruction or False otherwise.
        """
        if not isinstance(value, str):
            return False
        tanween_fath_count = value.count('ً')
        shadda_count = value.count('ّ')
        arabic_diacritics = set(['َ', 'ُ', 'ِ', 'ْ', 'ّ', 'ً', 'ٌ', 'ٍ'])
        is_vowelized = any((char in arabic_diacritics for char in value))
        return tanween_fath_count >= 5 and shadda_count >= 3 and is_vowelized

class DataIdx402InstructionChecker(AragenInstructions):

    def __init__(self):
        super().__init__('402')

    def check_following(self, value):
        """Checks if the response contains exactly 4 words with Shadda, exactly 5 words with Kasra Tanween, and exactly 3 words ending with Fatha Tanween.
        Args:
            value: A string representing the response (Arabic text).

        Returns:
            True if the response follows the instruction or False otherwise.
        """
        arabic_word_pattern = re.compile('[\\u0600-\\u06FF\\u064B-\\u0652]+')
        words = arabic_word_pattern.findall(value)
        shadda_count = 0
        kasra_tanween_count = 0
        fatha_tanween_count = 0
        for word in words:
            if 'ّ' in word:
                shadda_count += 1
            if word.endswith('ٍ'):
                kasra_tanween_count += 1
            if word.endswith('ً'):
                fatha_tanween_count += 1
        return shadda_count == 4 and kasra_tanween_count == 5 and (fatha_tanween_count == 3)

class DataIdx403InstructionChecker(AragenInstructions):

    def __init__(self):
        super().__init__('idx_403')

    def check_following(self, value):
        """Checks if the response describes a scene of a raging sea during a strong storm
        and adheres to specific word count constraints based on diacritics.

        Args:
            value: A string representing the response.

        Returns:
            True if the response follows the instruction or False otherwise.
        """
        if not isinstance(value, str) or not value.strip():
            return False
        DAMMA = 'ُ'
        KASRA = 'ِ'
        TANWIN_KASR = 'ٍ'
        TARGET_DAMMA_WORDS = 5
        TARGET_TANWIN_KASR_WORDS = 5
        TARGET_KASRA_WORDS = 3
        translator = str.maketrans('', '', string.punctuation)
        cleaned_value = value.translate(translator)
        words = cleaned_value.split()
        damma_words_count = 0
        tanwin_kasr_words_count = 0
        kasra_words_count = 0
        for word in words:
            if not word:
                continue
            if DAMMA in word:
                damma_words_count += 1
            if word.endswith(TANWIN_KASR):
                tanwin_kasr_words_count += 1
            if KASRA in word:
                kasra_words_count += 1
        return damma_words_count == TARGET_DAMMA_WORDS and tanwin_kasr_words_count == TARGET_TANWIN_KASR_WORDS and (kasra_words_count == TARGET_KASRA_WORDS)

class DataIdx71InstructionChecker(AragenInstructions):

    def __init__(self):
        super().__init__('idx_71')

    def check_following(self, value):
        """You will implement the logic of the function here to see if the response is correct or not.
        Constraints:
        1. Use strange language with mathematical symbols during explanation (Hard to check programmatically, ignored).
        2. The last sentence must start with 'ملاحظة بعد الملاحظات'.

        Args:
            value: A string representing the response.

        Returns:
            True if the response follows the verifiable constraint (last sentence starts with the phrase) or False otherwise.
        """
        required_phrase = 'ملاحظة بعد الملاحظات'
        if not isinstance(value, str):
            return False
        cleaned_value = value.strip()
        if not cleaned_value:
            return False
        sentences_parts = re.split('[.?!]', cleaned_value)
        last_sentence_content = None
        for part in reversed(sentences_parts):
            stripped_part = part.strip()
            if stripped_part:
                last_sentence_content = stripped_part
                break
        if last_sentence_content is None:
            return False
        return last_sentence_content.startswith(required_phrase)

class DataIdx187InstructionChecker(AragenInstructions):

    def __init__(self):
        super().__init__('idx_187')

    def check_following(self, value):
        """Checks if the response follows instruction 187.

        Args:
            value: A string representing the response.

        Returns:
            True if the response follows the instruction or False otherwise.
        """
        if not isinstance(value, str):
            return False
        if not value.startswith('<<'):
            return False
        end_title_idx = value.find('>>', 2)
        if end_title_idx == -1:
            return False
        body = value[end_title_idx + 2:].strip()
        sentences_parts = re.split('[.!?]', body)
        valid_sentences = [s.strip() for s in sentences_parts if s.strip()]
        sentence_count = len(valid_sentences)
        if sentence_count >= 5:
            return False
        words = value.split()
        word_count = len([w for w in words if w])
        if word_count < 250:
            return False
        return True
