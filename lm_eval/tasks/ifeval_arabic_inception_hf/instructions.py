# Copyright 2023 The Google Research Authors.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Library of instructions."""

import collections
import json
import logging
import random
import re
import string
from typing import Dict, Optional, Sequence, Union, List

from collections import Counter
import unicodedata, re

import langdetect

from lm_eval.tasks.ifeval_arabic_inception_hf import instructions_util


logger = logging.getLogger(__name__)

_InstructionArgsDtype = Optional[Dict[str, Union[int, str, Sequence[str]]]]

_LANGUAGES = instructions_util.LANGUAGE_CODES

# The relational operation for comparison.
_COMPARISON_RELATION = ("less than", "at least", "exactly")

# The maximum number of sentences.
_MAX_NUM_SENTENCES = 20

# The number of placeholders.
_NUM_PLACEHOLDERS = 4

# The number of bullet lists.
_NUM_BULLETS = 5

# The options of constrained response.
_CONSTRAINED_RESPONSE_OPTIONS = (
    "My answer is yes.",
    "My answer is no.", 
    "My answer is maybe.",
    "إجابتي هي نعم.",
    "إجابتي هي لا.",
    "إجابتي هي ربما."
)

ARABIC_ALPHABET = "ابتثجحخدذرزسشصضطظعغفقكلمنهوي"


# The options of starter keywords.
_STARTER_OPTIONS = (
    "I would say",
    "My answer is",
    "I believe",
    "In my opinion",
    "I think",
    "I reckon",
    "I feel",
    "From my perspective",
    "As I see it",
    "According to me",
    "As far as I'm concerned",
    "To my understanding",
    "In my view",
    "My take on it is",
    "As per my perception",
    "أعتقد أن",
    "في رأيي",
    "جوابي هو",
    "من وجهة نظري",
    "حسب ما أرى"
)



# The options of ending keywords.
# TODO(jeffreyzhou) add more ending options
_ENDING_OPTIONS = (
    "Any other questions?", "Is there anything else I can help with?",
    "هل هناك أي أسئلة أخرى؟",
    "هل يمكنني المساعدة في شيء آخر؟"
    )

# The number of highlighted sections.
_NUM_HIGHLIGHTED_SECTIONS = 4

# The section splitter.
_SECTION_SPLITER = ("Section", "SECTION", "قسم", "الجزء")

# The number of sections.
_NUM_SECTIONS = 5

# The number of paragraphs.
_NUM_PARAGRAPHS = 5

# The postscript marker.
_POSTSCRIPT_MARKER = ("P.S.", "P.P.S", "م.", "ملحوظة")

# The number of keywords.
_NUM_KEYWORDS = 2

# The occurrences of a single keyword.
_KEYWORD_FREQUENCY = 3

# The occurrences of a single letter.
_LETTER_FREQUENCY = 10

# The occurrences of words with all capital letters.
_ALL_CAPITAL_WORD_FREQUENCY = 20

# The number of words in the response.
_NUM_WORDS_LOWER_LIMIT = 100
_NUM_WORDS_UPPER_LIMIT = 500


class Instruction:
    """An instruction template."""

    def __init__(self, instruction_id):
        self.id = instruction_id

    def build_description(self, **kwargs):
        raise NotImplementedError("`build_description` not implemented.")

    def get_instruction_args(self):
        raise NotImplementedError("`get_instruction_args` not implemented.")

    def get_instruction_args_keys(self):
        raise NotImplementedError("`get_instruction_args_keys` not implemented.")

    def check_following(self, value):
        raise NotImplementedError("`check_following` not implemented.")


class ResponseLanguageChecker(Instruction):
    """Check the language of the entire response."""

    def build_description(self, *, language=None):
        """Build the instruction description."""
        # For an Arabic-only benchmark, we always default to "ar".
        # The `language` arg is kept for potential fixed-test cases if needed.
        self._language = language or "ar"

        # The description can be made bilingual for clarity to the researcher
        # but the key is that the instruction to the LLM will be in one language.
        # Example instruction text could be:
        # "يجب أن تكون إجابتك بأكملها باللغة العربية، ولا يُسمح بأي لغة أخرى."
        # For consistency with IFEVAL, we can keep the English description.
        self._description_pattern = (
            "Your ENTIRE response should be in {language} language, no other "
            + "language is allowed."
        )
        return self._description_pattern.format(language=_LANGUAGES[self._language])

    def get_instruction_args(self):
        """Returns the keyword args of `build_description`."""
        return {"language": self._language}

    def get_instruction_args_keys(self):
        """Returns the args keys of `build_description`."""
        return ["language"]

    # def language_composition(self, text):
    #     words = re.findall(r'\b\w+\b', text)
    #     lang_counts = Counter()\
    #     import ipdb; ipdb.set_trace()
    #     for word in words:
    #         try:
    #             lang = langdetect.detect(word)
    #             lang_counts[lang] += 1
    #         except:
    #             pass

    #     total = sum(lang_counts.values())
    #     composition = {lang: round(count / total * 100, 2) for lang, count in lang_counts.items()}
    #     return composition

    def check_following(self, value):
        """Check if the language of the entire response follows the instruction.

        Args:
          value: A string representing the response.

        Returns:
          True if the language of `value` follows instruction; otherwise False.
        """
        assert isinstance(value, str)

        try:
            return langdetect.detect(value) == self._language
        except langdetect.LangDetectException as e:
            # Count as instruction is followed.
            logging.error(
                "Unable to detect language for text %s due to %s", value, e
            )  # refex: disable=pytotw.037
            return True


class NumberOfSentences(Instruction):
    """Check the number of sentences."""

    def build_description(self, *, num_sentences=None, relation=None):
        """Build the instruction description.

        Args:
          num_sentences: An integer specifying the number of sentences as a
            threshold.
          relation: A string in (`less than`, `at least`), defining the relational
            operator for comparison.
            Two relational comparisons are supported for now:
            if 'less than', the actual number of sentences < the threshold;
            if 'at least', the actual number of sentences >= the threshold.

        Returns:
          A string representing the instruction description.
        """
        # The number of sentences as a threshold for comparison.
        self._num_sentences_threshold = num_sentences
        if self._num_sentences_threshold is None or self._num_sentences_threshold < 0:
            self._num_sentences_threshold = random.randint(1, _MAX_NUM_SENTENCES)

        if relation is None:
            self._comparison_relation = random.choice(_COMPARISON_RELATION)
        elif relation not in _COMPARISON_RELATION:
            raise ValueError(
                "The supported relation for comparison must be in "
                f"{_COMPARISON_RELATION}, but {relation} is given."
            )
        else:
            self._comparison_relation = relation

        self._description_pattern = (
            "Your response should contain {relation} {num_sentences} sentences."
        )
        return self._description_pattern.format(
            relation=self._comparison_relation,
            num_sentences=self._num_sentences_threshold,
        )

    def get_instruction_args(self):
        """Returns the keyword args of `build_description`."""
        return {
            "num_sentences": self._num_sentences_threshold,
            "relation": self._comparison_relation,
        }

    def get_instruction_args_keys(self):
        """Returns the args keys of `build_description`."""
        return ["num_sentences", "relation"]

    def check_following(self, value):
        """Check if the number of sentences follows the instruction.

        Args:
          value: A string representing the response.

        Returns:
          True if the response follows the instruction.

        Raise:
            ValueError if the string in `instruction_args` is not in
            [`less_than`, `at_least`].
        """
        num_sentences = instructions_util.count_sentences(value)
        if self._comparison_relation == _COMPARISON_RELATION[0]:
            return num_sentences < self._num_sentences_threshold
        elif self._comparison_relation == _COMPARISON_RELATION[1]:
            return num_sentences >= self._num_sentences_threshold
        elif self._comparison_relation == _COMPARISON_RELATION[2]:
            return num_sentences == self._num_sentences_threshold


class PlaceholderChecker(Instruction):
    """Check the placeholders in template writing."""

    def build_description(self, *, num_placeholders=None):
        """Build the instruction description.

        Args:
          num_placeholders: An integer denoting the minimum number of
            placeholders required in the response.

        Returns:
          A string representing the instruction description.
        """
        self._num_placeholders = num_placeholders
        if self._num_placeholders is None or self._num_placeholders < 0:
            self._num_placeholders = random.randint(1, _NUM_PLACEHOLDERS)
        self._description_pattern = (
            "The response must contain at least {num_placeholders} placeholders "
            + "represented by square brackets, such as [address]."
        )
        return self._description_pattern.format(num_placeholders=self._num_placeholders)

    def get_instruction_args(self):
        """Returns the keyword args of `build_description`."""
        return {"num_placeholders": self._num_placeholders}

    def get_instruction_args_keys(self):
        """Returns the args keys of `build_description`."""
        return ["num_placeholders"]

    def check_following(self, value):
        """Check if the number of placeholders follows the instruction.

        Args:
          value: A string representing the response.

        Returns:
          True if the actual number of placeholders in the response is greater than
          or equal to `num_placeholders`; otherwise, False.
        """
        placeholders = re.findall(r"\[.*?\]", value)
        num_placeholders = len(placeholders)
        return num_placeholders >= self._num_placeholders


class BulletListChecker(Instruction):
    """Checks the bullet list in the prompt."""

    def build_description(self, *, num_bullets=None):
        """Build the instruction description.

        Args:
          num_bullets: An integer specifying the exact number of bullet lists
            that is required to appear in the response.

        Returns:
          A string representing the instruction description.
        """
        self._num_bullets = num_bullets
        if self._num_bullets is None or self._num_bullets < 0:
            self._num_bullets = random.randint(1, _NUM_BULLETS)
        self._description_pattern = (
            "Your answer must contain exactly {num_bullets} bullet points. "
            + "Use the markdown bullet points such as:\n"
            + "* This is point 1. \n"
            + "* This is point 2"
        )
        return self._description_pattern.format(num_bullets=self._num_bullets)

    def get_instruction_args(self):
        """Returns the keyword args of `build_description`."""
        return {"num_bullets": self._num_bullets}

    def get_instruction_args_keys(self):
        """Returns the args keys of `build_description`."""
        return ["num_bullets"]

    def check_following(self, value):
        r"""Check if the number of bullet lists meets the requirement.

        Args:
          value: A string representing the response. The response is expected to
            contain some bullet lists that start with `\*`.

        Returns:
          True if the actual number of bullet lists in the response meets the
          requirement.
        """
        bullet_lists = re.findall(r"^\s*\*[^\*].*$", value, flags=re.MULTILINE)
        bullet_lists_2 = re.findall(r"^\s*-.*$", value, flags=re.MULTILINE)
        num_bullet_lists = len(bullet_lists) + len(bullet_lists_2)
        return num_bullet_lists == self._num_bullets


class ConstrainedResponseChecker(Instruction):
    """Checks the constrained response."""

    def build_description(self):
        """Build the instruction description."""
        # A sequence of string(s) representing the options of the expected response.
        self._constrained_responses = _CONSTRAINED_RESPONSE_OPTIONS
        self._description_pattern = (
            "Answer with one of the following options: {response_options}"
        )
        return self._description_pattern.format(
            response_options=self._constrained_responses
        )

    def get_instruction_args(self):
        """Returns the keyword args of `build_description`."""
        return None

    def get_instruction_args_keys(self):
        """Returns the args keys of `build_description`."""
        return []

    def check_following(self, value):
        """Checks if the response matches the constrained options.

        Args:
          value: A string representing the response.

        Returns:
          True if the actual response contains one of the options in the constrained
          responses; otherwise False.
        """
        value = value.strip()
        for constrained_response in self._constrained_responses:
            if constrained_response in value:
                return True
        return False


class ConstrainedStartChecker(Instruction):
    """Checks the response start."""

    def build_description(self, *, starter=None):
        """Build the instruction description.

        Args:
          starter: A string representing the keyword that the response should start
            with.

        Returns:
          A string representing the instruction description.
        """
        self._starter = starter.strip() if isinstance(starter, str) else starter
        if self._starter is None:
            self._starter = random.choice(_STARTER_OPTIONS)
        self._description_pattern = (
            "During the conversation, when it is your turn, "
            + "please always start with {starter}"
        )
        return self._description_pattern.format(starter=self._starter)

    def get_instruction_args(self):
        """Returns the keyword args of `build_description`."""
        return {"starter": self._starter}

    def get_instruction_args_keys(self):
        """Returns the args keys of `build_description`."""
        return ["starter"]

    def check_following(self, value):
        """Checks if the response starts with the constrained keyword or phrase.

        Args:
          value: A string representing the response.

        Returns:
          True if the response starts with the given phrase or keyword that is
          contained in `instruction_args`; otherwise, False.
        """
        response_pattern = r"^\s*" + self._starter + r".*$"
        response_with_constrained_start = re.search(
            response_pattern, value, flags=re.MULTILINE
        )
        return True if response_with_constrained_start else False


class HighlightSectionChecker(Instruction):
    """Checks the highlighted section."""

    def build_description(self, *, num_highlights=None):
        """Build the instruction description.

        Args:
          num_highlights: An integer specifying the minimum number of highlighted
            sections.

        Returns:
          A string representing the instruction description.
        """
        self._num_highlights = num_highlights
        if self._num_highlights is None or self._num_highlights < 0:
            self._num_highlights = random.randint(1, _NUM_HIGHLIGHTED_SECTIONS)

        self._description_pattern = (
            "Highlight at least {num_highlights} sections in your answer with "
            + "markdown, i.e. *highlighted section*."
        )

        return self._description_pattern.format(num_highlights=self._num_highlights)

    def get_instruction_args(self):
        """Returns the keyword args of `build_description`."""
        return {"num_highlights": self._num_highlights}

    def get_instruction_args_keys(self):
        """Returns the args keys of `build_description`."""
        return ["num_highlights"]

    def check_following(self, value):
        """Checks if the number of highlighted sections meets the requirement.

        Args:
          value: a string representing the response. The response is expected to
            contain highlighted sections in the format of *highlighted*.

        Returns:
          True if the actual number of highlighted sections in the format of
          *highlighted sections* meets the minimum requirement; otherwise False.
        """
        num_highlights = 0
        highlights = re.findall(r"\*[^\n\*]*\*", value)
        double_highlights = re.findall(r"\*\*[^\n\*]*\*\*", value)
        for highlight in highlights:
            if highlight.strip("*").strip():
                num_highlights += 1
        for highlight in double_highlights:
            if highlight.removeprefix("**").removesuffix("**").strip():
                num_highlights += 1

        return num_highlights >= self._num_highlights


class SectionChecker(Instruction):
    """Checks the sections."""

    def build_description(self, *, section_spliter=None, num_sections=None):
        """Build the instruction description.

        Args:
          section_spliter: A string represents the section spliter keyword that
            marks a new section, i.e., `Section` or `SECTION`.
          num_sections: An integer specifying the number of sections.

        Returns:
          A string representing the instruction description.
        """
        self._section_spliter = (
            section_spliter.strip()
            if isinstance(section_spliter, str)
            else section_spliter
        )
        if self._section_spliter is None:
            self._section_spliter = random.choice(_SECTION_SPLITER)

        self._num_sections = num_sections
        if self._num_sections is None or self._num_sections < 0:
            self._num_sections = random.randint(1, _NUM_SECTIONS)

        self._description_pattern = (
            "Your response must have {num_sections} sections. Mark the beginning "
            + "of each section with {section_spliter} X, such as:\n"
            + "{section_spliter} 1\n"
            + "[content of section 1]\n"
            + "{section_spliter} 2\n"
            + "[content of section 2]"
        )

        return self._description_pattern.format(
            num_sections=self._num_sections, section_spliter=self._section_spliter
        )

    def get_instruction_args(self):
        """Returns the keyword args of `build_description`."""
        return {
            "section_spliter": self._section_spliter,
            "num_sections": self._num_sections,
        }

    def get_instruction_args_keys(self):
        """Returns the args keys of `build_description`."""
        return ["section_spliter", "num_sections"]

    def check_following(self, value):
        """Checks the response contains multiple sections.

        Args:
          value: A string representing the response. The response is expected
            to contain multiple sections (number of sections is greater than 1).
            A new section starts with `Section 1`, where the number denotes the
            section index.

        Returns:
          True if the number of sections in the response is greater than or equal to
          the minimum number of sections; otherwise, False.
        """
        try:
            section_splitter_patten = r"\s?" + self._section_spliter + r"\s?\d+\s?"
            sections = re.split(section_splitter_patten, value)
        
            num_sections = len(sections) - 1
            return num_sections >= self._num_sections
        except Exception as e:
            print(f"Error in SectionChecker: {e}")
            print(f"Value: {value}")
            return False


class ParagraphChecker(Instruction):
    """Checks the paragraphs."""

    def build_description(self, *, num_paragraphs=None):
        """Build the instruction description.

        Args:
          num_paragraphs: An integer specifying the number of paragraphs.

        Returns:
          A string representing the instruction description.
        """
        self._num_paragraphs = num_paragraphs
        if self._num_paragraphs is None or self._num_paragraphs < 0:
            self._num_paragraphs = random.randint(1, _NUM_PARAGRAPHS)

        self._description_pattern = (
            "There should be {num_paragraphs} paragraphs. "
            + "Paragraphs are separated with the markdown divider: ***"
        )

        return self._description_pattern.format(num_paragraphs=self._num_paragraphs)

    def get_instruction_args(self):
        """Returns the keyword args of `build_description`."""
        return {"num_paragraphs": self._num_paragraphs}

    def get_instruction_args_keys(self):
        """Returns the args keys of `build_description`."""
        return ["num_paragraphs"]

    def check_following(self, value):
        """Checks the response contains required number of paragraphs.

        Args:
          value: A string representing the response. The response may contain
            paragraphs that are separated by the markdown divider: `***`.

        Returns:
          True if the actual number of paragraphs is the same as required;
          otherwise, False.
        """
        paragraphs = re.split(r"\s?\*\*\*\s?", value)
        num_paragraphs = len(paragraphs)

        for index, paragraph in enumerate(paragraphs):
            if not paragraph.strip():
                if index == 0 or index == len(paragraphs) - 1:
                    num_paragraphs -= 1
                else:
                    return False

        return num_paragraphs == self._num_paragraphs


class PostscriptChecker(Instruction):
    """Checks the postscript."""

    def build_description(self, *, postscript_marker=None):
        """Build the instruction description.

        Args:
          postscript_marker: A string containing the keyword that marks the start
            of the postscript section.

        Returns:
          A string representing the instruction description.
        """
        self._postscript_marker = (
            postscript_marker.strip()
            if isinstance(postscript_marker, str)
            else postscript_marker
        )
        if self._postscript_marker is None:
            self._postscript_marker = random.choice(_POSTSCRIPT_MARKER)

        self._description_pattern = (
            "At the end of your response, please explicitly add a postscript "
            + "starting with {postscript}"
        )

        return self._description_pattern.format(postscript=self._postscript_marker)

    def get_instruction_args(self):
        """Returns the keyword args of `build_description`."""
        return {"postscript_marker": self._postscript_marker}

    def get_instruction_args_keys(self):
        """Returns the args keys of `build_description`."""
        return ["postscript_marker"]

    def check_following(self, value):
        """Checks if the response follows the postscript format."""
        value = value.lower().strip() # Keep lower for English, strip for all
        marker = self._postscript_marker

        # Build a robust pattern based on the marker
        if marker == "P.P.S":
            # Handles p.p.s, p. p. s., etc.
            postscript_pattern = r"\s*p\.\s?p\.\s?s.*$"
        elif marker == "P.S.":
            # Handles p.s., p. s., etc.
            postscript_pattern = r"\s*p\.\s?s\..*$"
        elif marker == "م.":
            # Handles "م." at the end of a line
            postscript_pattern = r"\s*م\..*$"
        elif marker == "ملحوظة":
            postscript_pattern = r"\s*ملحوظة.*$"
        else:
            # Generic fallback for other potential markers
            postscript_pattern = r"\s*" + re.escape(marker.lower()) + r".*$"

        # Use re.search since findall can be inefficient if we only need one match
        postscript = re.search(postscript_pattern, value, flags=re.MULTILINE)
        return True if postscript else False


class RephraseChecker(Instruction):
    """Checks the rephrase."""

    def build_description(self, *, original_message):
        """Build the instruction description.

        Args:
          original_message: A string representing the original message. The
            rephrased response should only change its words/sentences in between
            its two asterisks, for example, *change me*. Both original and rephrased
            messages should contain the changes in the form of *change me*.

        Returns:
          A string representing the instruction description.
        """
        if not self.is_change(original_message):
            raise ValueError(
                f"Message {original_message} does not contain changes "
                "in the form of *change me*."
            )

        self._reference_without_change = original_message
        self._description = (
            "Rephrasing: Your rephrased response should only"
            + "change the words/sentences in between two asterisks"
            + "such as *change me*."
        )
        return self._description

    def get_instruction_args(self):
        """Returns the keyword args of `build_description`."""
        return {"original_message": self._reference_without_change}

    def get_instruction_args_keys(self):
        """Returns the args keys of `build_description`."""
        return ["original_message"]

    def check_following(self, value):
        r"""Checks if the rephrasing follows the instruction.

        Args:
          value: A string representing the response, which is expected to rephras
            the string of `instruction_args`.

        Returns:
          True if `value` and `instruction_args` only differ by the words/sentences
          in between two asterisks such as *change me*; otherwise, False.
        """

        if not self.is_change(value):
            raise ValueError(
                f"value {value} does not contain changes in the form of *change me*."
            )

        response_without_changes = self.strip_changes(value)
        reference_without_changes = self.strip_changes(self._reference_without_change)

        return response_without_changes == reference_without_changes

    def is_change(self, response):
        """Check if there is change in the response in the form of *change me*."""
        return re.search(r"\*.*\*", response)

    def strip_changes(self, response):
        """Strips off the changes."""
        return re.sub(r"\*.*\*", "", response)


class KeywordChecker(Instruction):
    """Check the exisitence of certain keywords."""

    def build_description(self, *, keywords=None):
        """Build the instruction description.

        Args:
          keywords: A sequence of strings representing the keywords that are
            expected in the response.

        Returns:
          A string representing the instruction description.
        """

        if not keywords:
            self._keywords = instructions_util.generate_keywords(
                num_keywords=_NUM_KEYWORDS
            )
        else:
            self._keywords = keywords
        self._keywords = sorted(self._keywords)

        self._description_pattern = "Include keywords {keywords} in the response."

        return self._description_pattern.format(keywords=self._keywords)

    def get_instruction_args(self):
        """Returns the keyword args of `build_description`."""
        return {"keywords": self._keywords}

    def get_instruction_args_keys(self):
        """Returns the args keys of `build_description`."""
        return ["keywords"]

    def check_following(self, value):
        """Check if the response contain the expected keywords as whole words."""
        for keyword in self._keywords:
            try:
                # Use \b for word boundaries. It works reasonably well in modern
                # regex engines for Unicode. re.escape handles special characters.
                # We are not using IGNORECASE as it's not applicable to Arabic.
                pattern = r"\b" + re.escape(keyword) + r"\b"
                if not re.search(pattern, value):
                    return False
            except Exception as e:
                print(f"Error in KeywordChecker: {e}")
                print(f"Value: {value}")
                print(f"Keyword: {keyword}")
                return False
        return True


class KeywordFrequencyChecker(Instruction):
    """Check the keyword frequency."""

    def build_description(self, *, keyword=None, frequency=None, relation=None):
        """Build the instruction description.

        Args:
          keyword: A string representing a keyword that is expected in the response.
          frequency: An integer specifying the number of times `keyword` is expected
            to appear in the response.
          relation: A string in (`less than`, `at least`), defining the relational
            operator for comparison.
            Two relational comparisons are supported for now:
            if 'less than', the actual number of occurrences < frequency;
            if 'at least', the actual number of occurrences >= frequency.

        Returns:
          A string representing the instruction description.
        """
        if not keyword:
            self._keyword = instructions_util.generate_keywords(num_keywords=1)[0]
        else:
            self._keyword = keyword.strip()

        self._frequency = frequency
        if self._frequency is None or self._frequency < 0:
            self._frequency = random.randint(1, _KEYWORD_FREQUENCY)

        if relation is None:
            self._comparison_relation = random.choice(_COMPARISON_RELATION)
        elif relation not in _COMPARISON_RELATION:
            raise ValueError(
                "The supported relation for comparison must be in "
                f"{_COMPARISON_RELATION}, but {relation} is given."
            )
        else:
            self._comparison_relation = relation

        self._description_pattern = (
            "In your response, the word {keyword} should appear {relation} "
            + "{frequency} times."
        )

        return self._description_pattern.format(
            keyword=self._keyword,
            relation=self._comparison_relation,
            frequency=self._frequency,
        )

    def get_instruction_args(self):
        """Returns the keyword args of `build_description`."""
        return {
            "keyword": self._keyword,
            "frequency": self._frequency,
            "relation": self._comparison_relation,
        }

    def get_instruction_args_keys(self):
        """Returns the args keys of `build_description`."""
        return ["keyword", "frequency", "relation"]

    def check_following(self, value):
        """Checks if the response contain the keyword with required frequency."""
        # Match whole words only. Remove IGNORECASE flag.
        pattern = r"\b" + re.escape(self._keyword) + r"\b"
        actual_occurrences = len(re.findall(pattern, value))

        if self._comparison_relation == _COMPARISON_RELATION[0]: # less than
            return actual_occurrences < self._frequency
        elif self._comparison_relation == _COMPARISON_RELATION[1]: # at least
            return actual_occurrences >= self._frequency
        elif self._comparison_relation == _COMPARISON_RELATION[2]: # exactly
            return actual_occurrences == self._frequency


class NumberOfWords(Instruction):
    """Checks the number of words."""

    def build_description(self, *, num_words=None, relation=None):
        """Build the instruction description.

        Args:
          num_words: An integer specifying the number of words contained in the
            response.
          relation: A string in (`less than`, `at least`), defining the relational
            operator for comparison.
            Two relational comparisons are supported for now:
            if 'less than', the actual number of words < num_words;
            if 'at least', the actual number of words >= num_words.

        Returns:
          A string representing the instruction description.
        """

        self._num_words = num_words
        if self._num_words is None or self._num_words < 0:
            self._num_words = random.randint(
                _NUM_WORDS_LOWER_LIMIT, _NUM_WORDS_UPPER_LIMIT
            )

        if relation is None:
            self._comparison_relation = random.choice(_COMPARISON_RELATION)
        elif relation not in _COMPARISON_RELATION:
            raise ValueError(
                "The supported relation for comparison must be in "
                f"{_COMPARISON_RELATION}, but {relation} is given."
            )
        else:
            self._comparison_relation = relation

        self._description_pattern = "Answer with {relation} {num_words} words."

        return self._description_pattern.format(
            relation=self._comparison_relation, num_words=self._num_words
        )

    def get_instruction_args(self):
        """Returns the keyword args of `build_description`."""
        return {"num_words": self._num_words, "relation": self._comparison_relation}

    def get_instruction_args_keys(self):
        """Returns the args keys of `build_description`."""
        return ["num_words", "relation"]

    def check_following(self, value):
        """Checks if the response contains the expected number of words."""
        num_words = instructions_util.count_words(value)

        if self._comparison_relation == _COMPARISON_RELATION[0]:
            return num_words < self._num_words
        elif self._comparison_relation == _COMPARISON_RELATION[1]:
            return num_words >= self._num_words
        elif self._comparison_relation == _COMPARISON_RELATION[2]:
            return num_words == self._num_words


class JsonFormat(Instruction):
    """Check the Json format."""

    def build_description(self):
        self._description_pattern = (
            "Entire output should be wrapped in JSON format. You can use markdown"
            " ticks such as ```."
        )
        return self._description_pattern

    def get_instruction_args(self):
        """Returns the keyword args of `build_description`."""
        return None

    def get_instruction_args_keys(self):
        """Returns the args keys of `build_description`."""
        return []

    def check_following(self, value):
        value = (
            value.strip()
            .removeprefix("```json")
            .removeprefix("```Json")
            .removeprefix("```JSON")
            .removeprefix("```")
            .removesuffix("```")
            .strip()
        )
        try:
            json.loads(value)
        except ValueError:
            return False
        return True


class ParagraphFirstWordCheck(Instruction):
    """Check the paragraph and the first word of the nth paragraph."""

    def build_description(
        self, num_paragraphs=None, nth_paragraph=None, first_word=None
    ):
        r"""Build the instruction description.

        Args:
          num_paragraphs: An integer indicating the number of paragraphs expected
            in the response. A paragraph is a subset of the string that is
            expected to be separated by '\n\n'.
          nth_paragraph: An integer indicating the paragraph number that we look at.
            Note that n starts from 1.
          first_word: A string that represent the first word of the bth paragraph.

        Returns:
          A string representing the instruction description.
        """
        self._num_paragraphs = num_paragraphs
        if self._num_paragraphs is None or self._num_paragraphs < 0:
            self._num_paragraphs = random.randint(1, _NUM_PARAGRAPHS)

        self._nth_paragraph = nth_paragraph
        if (
            self._nth_paragraph is None
            or self._nth_paragraph <= 0
            or self._nth_paragraph > self._num_paragraphs
        ):
            self._nth_paragraph = random.randint(1, self._num_paragraphs + 1)

        self._first_word = first_word
        if self._first_word is None:
            self._first_word = instructions_util.generate_keywords(num_keywords=1)[0]
        self._first_word = self._first_word.lower()

        self._description_pattern = (
            "There should be {num_paragraphs} paragraphs. "
            + "Paragraphs and only paragraphs are separated with each other by two "
            + "new lines as if it was '\\n\\n' in python. "
            + "Paragraph {nth_paragraph} must start with word {first_word}."
        )

        return self._description_pattern.format(
            num_paragraphs=self._num_paragraphs,
            nth_paragraph=self._nth_paragraph,
            first_word=self._first_word,
        )

    def get_instruction_args(self):
        """Returns the keyword args of `build_description`."""
        return {
            "num_paragraphs": self._num_paragraphs,
            "nth_paragraph": self._nth_paragraph,
            "first_word": self._first_word,
        }

    def get_instruction_args_keys(self):
        """Returns the args keys of `build_description`."""
        return ["num_paragraphs", "nth_paragraph", "first_word"]

    def check_following(self, value):
        # ... (code for splitting paragraphs is fine) ...
        paragraphs = re.split(r"\n\n", value)
        num_paragraphs = len(paragraphs)

        # This part can be simplified
        valid_paragraphs = [p.strip() for p in paragraphs if p.strip()]
        num_paragraphs = len(valid_paragraphs)

        if self._nth_paragraph <= 0 or self._nth_paragraph > num_paragraphs:
            return False

        paragraph = valid_paragraphs[self._nth_paragraph - 1]
        words = paragraph.split()
        if not words:
            return False

        first_word_raw = words[0]

        # Define a comprehensive set of punctuation to strip from the word
        # Includes English, Arabic, and common symbols.
        punctuation_to_strip = r"""!"#$%&'()*+,-./:;<=>?@[]^_`{|}~،؛؟»«…"""
        first_word_clean = first_word_raw.strip(punctuation_to_strip)

        # Comparison should be case-insensitive for English and works for Arabic
        return num_paragraphs == self._num_paragraphs and first_word_clean.lower() == self._first_word.lower()


# TODO(jeffrey) add relation - at least/at most?
class KeySentenceChecker(Instruction):
    """Check the existence of certain key sentences."""

    def build_description(self, key_sentences=None, num_sentences=None):
        """Build the instruction description.

        Args:
          key_sentences: A sequences of strings representing the key sentences that
            are expected in the response.
          num_sentences: The number of key sentences that are expected to be seen in
            the response.

        Returns:
          A string representing the instruction description.
        """

        if not key_sentences:
            # TODO(jeffrey) make a generate sentences function? wonderwords package
            self._key_sentences = set(["For now, this is fine."])
        else:
            self._key_sentences = key_sentences

        if not num_sentences:
            self._num_sentences = random.randint(1, len(self._key_sentences))
        else:
            self._num_sentences = num_sentences

        self._description_pattern = (
            "Include {num_sentences} of the following sentences {key_sentences}"
        )

        return self._description_pattern.format(
            num_sentences=self._num_sentences, key_sentences=self._key_sentences
        )

    def get_instruction_args(self):
        """Returns the keyword args of `build_description`."""
        return {
            "num_sentences": self._num_sentences,
            "key_sentences": list(self._key_sentences),
        }

    def get_instruction_args_keys(self):
        """Returns the args keys of `build_description`."""
        return ["num_sentences", "key_sentences"]

    def check_following(self, value):
        """Checks if the response contains the expected key sentences."""
        count = 0
        # Define punctuation characters to remove for normalization
        punctuation_re = re.compile(f"[{re.escape(string.punctuation)}،؛؟]")

        # Normalize and create a set of sentences from the model's output
        # 1. Split into sentences using our robust function
        # 2. Lowercase (for English)
        # 3. Remove all punctuation
        # 4. Strip whitespace
        response_sentences = {
            punctuation_re.sub("", s).lower().strip()
            for s in instructions_util.split_into_sentences(value)
        }

        for key_sentence in self._key_sentences:
            # Normalize the key sentence in the same way
            normalized_key = punctuation_re.sub("", key_sentence).lower().strip()
            if normalized_key in response_sentences:
                count += 1

        return count >= self._num_sentences # Changed to 'at least' to match description


class ForbiddenWords(Instruction):
    """Checks that specified words are not used in response."""

    def build_description(self, forbidden_words=None):
        """Build the instruction description.

        Args:
          forbidden_words: A sequences of strings representing words that are not
            allowed in the response.

        Returns:
          A string representing the instruction description.
        """

        if not forbidden_words:
            self._forbidden_words = instructions_util.generate_keywords(
                num_keywords=_NUM_KEYWORDS
            )
        else:
            self._forbidden_words = list(set(forbidden_words))
        self._forbidden_words = sorted(self._forbidden_words)
        self._description_pattern = (
            "Do not include keywords {forbidden_words} in the response."
        )

        return self._description_pattern.format(forbidden_words=self._forbidden_words)

    def get_instruction_args(self):
        """Returns the keyword args of `build_description`."""
        return {"forbidden_words": self._forbidden_words}

    def get_instruction_args_keys(self):
        """Returns the args keys of `build_description`."""
        return ["forbidden_words"]

    def check_following(self, value):
        """Check if the response does not contain the forbidden keywords."""
        for word in self._forbidden_words:
            try:
                # Remove IGNORECASE flag as it's not needed for Arabic
                pattern = r"\b" + re.escape(word) + r"\b"
                if re.search(pattern, value):
                    return False
            except Exception as e:
                print(f"Error in ForbiddenWords: {e}")
                return False
        return True


class RephraseParagraph(Instruction):
    """Checks that the paragraph is rephrased."""

    def build_description(self, *, original_paragraph, low, high):
        """Builds the instruction description.

        Args:
          original_paragraph: A string presenting the original paragraph. The
            rephrases response should have betweeb low-high words in common.
          low: An integer presenting the lower bound of similar words.
          high: An integer representing the upper bound of similar words.

        Returns:
          A string representing the instruction description.
        """
        # TODO(jeffrey) make more encompassing
        self._original_paragraph = original_paragraph
        self._low = low
        self._high = high

        self._description = (
            "Rephrase the following paragraph: "
            + "{original_paragraph}\nYour response should have "
            + "between {low} and {high} of the same words. "
            + "Words are the same if and only if all of the "
            + "letters, ignoring cases, are the same. For "
            + "example, 'run' is the same as 'Run' but different "
            + "to 'ran'."
        )

        return self._description.format(
            original_paragraph=original_paragraph, low=self._low, high=self._high
        )

    def get_instruction_args(self):
        """Returns the keyword args of `build_description`."""
        return {
            "original_paragraph": self._original_paragraph,
            "low": self._low,
            "high": self._high,
        }

    def get_instruction_args_keys(self):
        """Returns the args keys of `build_description`."""
        return ["original_paragraph", "low", "high"]

    def check_following(self, value):
        # Use the Unicode-aware regex for finding words
        ar_en_word_pattern = r'[\w\u0600-\u06FF]+'
        val_words = re.findall(ar_en_word_pattern, value.lower())
        original_words = re.findall(ar_en_word_pattern, self._original_paragraph.lower())
        similar_words = 0

        dict_val = collections.Counter(val_words)
        dict_original = collections.Counter(original_words)

        for word in dict_original:
            similar_words += min(dict_original[word], dict_val[word])

        return self._low <= similar_words <= self._high


class TwoResponsesChecker(Instruction):
    """Check that two responses were given."""

    def build_description(self):
        """Build the instruction description."""
        self._description_pattern = (
            "Give two different responses. Responses and only responses should"
            " be separated by 6 asterisk symbols: ******."
        )
        return self._description_pattern

    def get_instruction_args(self):
        """Returns the keyword args of `build_description`."""
        return None

    def get_instruction_args_keys(self):
        """Returns the args keys of `build_description`."""
        return []

    def check_following(self, value):
        """Checks if the response has two different answers.

        Args:
          value: A string representing the response.

        Returns:
          True if two responses are detected and false otherwise.
        """
        valid_responses = list()
        responses = value.split("******")
        for index, response in enumerate(responses):
            if not response.strip():
                if index != 0 and index != len(responses) - 1:
                    return False
            else:
                valid_responses.append(response)
        return (
            len(valid_responses) == 2
            and valid_responses[0].strip() != valid_responses[1].strip()
        )


class RepeatPromptThenAnswer(Instruction):
    """Checks that Prompt is first repeated then answered."""

    def build_description(self, *, prompt_to_repeat=None):
        """Build the instruction description.

        Args:
          prompt_to_repeat: The prompt that is meant to be repeated.

        Returns:
          A string representing the instruction description.
        """
        if not prompt_to_repeat:
            raise ValueError("prompt_to_repeat must be set.")
        else:
            self._prompt_to_repeat = prompt_to_repeat
        self._description_pattern = (
            "First repeat the request word for word without change,"
            " then give your answer (1. do not say any words or characters"
            " before repeating the request; 2. the request you need to repeat"
            " does not include this sentence)"
        )
        return self._description_pattern

    def get_instruction_args(self):
        return {"prompt_to_repeat": self._prompt_to_repeat}

    def get_instruction_args_keys(self):
        """Returns the args keys of `build_description`."""
        return ["prompt_to_repeat"]

    def check_following(self, value):
        if value.strip().lower().startswith(self._prompt_to_repeat.strip().lower()):
            return True
        return False


class EndChecker(Instruction):
    """Checks that the prompt ends with a given phrase."""

    def build_description(self, *, end_phrase=None):
        """Build the instruction description.

        Args:
          end_phrase: A string representing the phrase the response should end with.

        Returns:
          A string representing the instruction description.
        """
        self._end_phrase = (
            end_phrase.strip() if isinstance(end_phrase, str) else end_phrase
        )
        if self._end_phrase is None:
            self._end_phrase = random.choice(_ENDING_OPTIONS)
        self._description_pattern = (
            "Finish your response with this exact phrase {ender}. "
            "No other words should follow this phrase."
        )
        return self._description_pattern.format(ender=self._end_phrase)

    def get_instruction_args(self):
        return {"end_phrase": self._end_phrase}

    def get_instruction_args_keys(self):
        """Returns the args keys of `build_description`."""
        return ["end_phrase"]

    def check_following(self, value):
        """Checks if the response ends with the expected phrase."""
        value = value.strip().strip('"').lower()
        self._end_phrase = self._end_phrase.strip().lower()
        return value.endswith(self._end_phrase)


class TitleChecker(Instruction):
    """Checks the response for a title."""

    def build_description(self):
        """Build the instruction description."""
        self._description_pattern = (
            "Your answer must contain a title, wrapped in double angular brackets,"
            " such as <<poem of joy>>."
        )
        return self._description_pattern

    def get_instruction_args(self):
        return None

    def get_instruction_args_keys(self):
        """Returns the args keys of `build_description`."""
        return []

    def check_following(self, value):
        """Checks if the response contains a title."""
        pattern = r"<<[^\n]+>>"
        re_pattern = re.compile(pattern)
        titles = re.findall(re_pattern, value)

        for title in titles:
            if title.lstrip("<").rstrip(">").strip():
                return True
        return False


class LetterFrequencyChecker(Instruction):
    """Checks letter frequency."""

    def build_description(self, *, letter=None, let_frequency=None, let_relation=None, relation=None, frequency=None):
        """Build the instruction description.

        Args:
          letter: A string representing a letter that is expected in the response.
          let_frequency: An integer specifying the number of times `keyword` is
            expected to appear in the response.
          let_relation: A string in (`less than`, `at least`), defining the
            relational operator for comparison. Two relational comparisons are
            supported for now; if 'less than', the actual number of
            occurrences < frequency; if 'at least', the actual number of
            occurrences >= frequency.

        Returns:
          A string representing the instruction description.
        """
        
        if let_relation is None and relation is not None:
            let_relation = relation
        if let_frequency is None and frequency is not None:
            let_frequency = frequency
        
        if let_relation not in _COMPARISON_RELATION and relation in _COMPARISON_RELATION:
            let_relation = relation
        if let_frequency not in _COMPARISON_RELATION and frequency in _COMPARISON_RELATION:
            let_frequency = frequency

        # ADAPTATION: If a letter is not provided, ALWAYS pick a random ARABIC letter.
        if not letter:
            self._letter = random.choice(ARABIC_ALPHABET)
        else:
            self._letter = letter.strip()
        # self._letter = self._letter.lower()

        self._frequency = let_frequency
        if self._frequency is None or self._frequency < 0:
            self._frequency = random.randint(1, _LETTER_FREQUENCY)

        if let_relation is None:
            self._comparison_relation = random.choice(_COMPARISON_RELATION)
        elif let_relation not in _COMPARISON_RELATION:
            raise ValueError(
                "The supported relation for comparison must be in "
                f"{_COMPARISON_RELATION}, but {let_relation} is given."
            )
        else:
            self._comparison_relation = let_relation

        self._description_pattern = (
            "In your response, the letter {letter} should appear {let_relation}"
            " {let_frequency} times."
        )

        return self._description_pattern.format(
            letter=self._letter,
            let_frequency=self._frequency,
            let_relation=self._comparison_relation,
        )

    def get_instruction_args(self):
        """Returns the keyword args of build description."""
        return {
            "letter": self._letter,
            "let_frequency": self._frequency,
            "let_relation": self._comparison_relation,
        }

    def get_instruction_args_keys(self):
        """Returns the args keys of `build_description`."""
        return ["letter", "let_frequency", "let_relation"]

    def check_following(self, value):
        """Checks that the response contains the letter at the right frequency."""
        # Normalizing to lower is fine for English and harmless for Arabic
        value = value.lower()
        letters = collections.Counter(value)
        
        # The letter to check should also be 'lowercased' for consistency
        letter_to_check = self._letter.lower()

        if self._comparison_relation == _COMPARISON_RELATION[0]: # less than
            return letters[letter_to_check] < self._frequency
        elif self._comparison_relation == _COMPARISON_RELATION[1]: # at least
            return letters[letter_to_check] >= self._frequency
        elif self._comparison_relation == _COMPARISON_RELATION[2]: # exactly
            return letters[letter_to_check] == self._frequency


# class CapitalLettersEnglishChecker(Instruction):
#     """Checks that the response is in english and is in all capital letters."""

#     def build_description(self):
#         """Build the instruction description."""
#         self._description_pattern = (
#             "Your entire response should be in English, and in all capital letters."
#         )
#         return self._description_pattern

#     def get_instruction_args(self):
#         return None

#     def get_instruction_args_keys(self):
#         """Returns the args keys of `build_description`."""
#         return []

#     def check_following(self, value):
#         """Checks that the response is in English and in all capital letters."""
#         assert isinstance(value, str)

#         try:
#             return value.isupper() and langdetect.detect(value) == "en"
#         except langdetect.LangDetectException as e:
#             # Count as instruction is followed.
#             logging.error(
#                 "Unable to detect language for text %s due to %s", value, e
#             )  # refex: disable=pytotw.037
#             return True


# class LowercaseLettersEnglishChecker(Instruction):
#     """Checks that the response is in english and is in all lowercase letters."""

#     def build_description(self):
#         """Build the instruction description."""
#         self._description_pattern = (
#             "Your entire response should be in English, and in all lowercase"
#             " letters. No capital letters are allowed."
#         )
#         return self._description_pattern

#     def get_instruction_args(self):
#         return None

#     def get_instruction_args_keys(self):
#         """Returns the args keys of `build_description`."""
#         return []

#     def check_following(self, value):
#         """Checks that the response is in English and in all lowercase letters."""
#         assert isinstance(value, str)

#         try:
#             return value.islower() and langdetect.detect(value) == "en"
#         except langdetect.LangDetectException as e:
#             # Count as instruction is followed.
#             logging.error(
#                 "Unable to detect language for text %s due to %s", value, e
#             )  # refex: disable=pytotw.037
#             return True


class CommaChecker(Instruction):
    """Checks the response for no commas."""

    def build_description(self):
        """Build the instruction description."""
        self._description_pattern = (
            "In your entire response, refrain from the use of any commas."
        )
        return self._description_pattern

    def get_instruction_args(self):
        return None

    def get_instruction_args_keys(self):
        """Returns the args keys of `build_description`."""
        return []

    def check_following(self, value):
        """Checks that the response does not contain commas (both English and Arabic)."""
        # Check for both English comma (,) and Arabic comma (،)
        return not (re.search(r"\,", value) or re.search(r"،", value))


# class CapitalWordFrequencyChecker(Instruction):
#     """Checks frequency of words with all capital letters."""

#     def build_description(
#         self,
#         capital_frequency=None,
#         capital_relation=None,
#     ):
#         """Build the instruction description.

#         Args:
#           capital_frequency: An integer that represents the number of words that
#             should be in all capital letters.
#           capital_relation: A string that is 'at least' or 'at most' that refers to
#             the frequency.

#         Returns:
#           A string representing the instruction description.
#         """
#         self._frequency = capital_frequency
#         if self._frequency is None:
#             self._frequency = random.randint(1, _ALL_CAPITAL_WORD_FREQUENCY)

#         self._comparison_relation = capital_relation
#         if capital_relation is None:
#             self._comparison_relation = random.choice(_COMPARISON_RELATION)
#         elif capital_relation not in _COMPARISON_RELATION:
#             raise ValueError(
#                 "The supported relation for comparison must be in "
#                 f"{_COMPARISON_RELATION}, but {capital_relation} is given."
#             )

#         self._description_pattern = (
#             "In your response, words with all capital letters should appear"
#             " {relation} {frequency} times."
#         )

#         return self._description_pattern.format(
#             frequency=self._frequency, relation=self._comparison_relation
#         )

#     def get_instruction_args(self):
#         """Returns the keyword args of build description."""
#         return {
#             "capital_frequency": self._frequency,
#             "capital_relation": self._comparison_relation,
#         }

#     def get_instruction_args_keys(self):
#         """Returns the args keys of `build_description`."""
#         return ["capital_frequency", "capital_relation"]

#     def check_following(self, value):
#         """Checks the frequency of words with all capital letters."""
#         # Hyphenated words will count as one word
#         words = instructions_util.nltk.word_tokenize(value)
#         capital_words = [word for word in words if word.isupper()]

#         capital_words = len(capital_words)

#         if self._comparison_relation == _COMPARISON_RELATION[0]:
#             return capital_words < self._frequency
#         else:
#             return capital_words >= self._frequency


class QuotationChecker(Instruction):
    """Checks response is wrapped with double quotation marks."""

    def build_description(self):
        """Build the instruction description."""
        self._description_pattern = (
            "Wrap your entire response with double quotation marks."
        )
        return self._description_pattern

    def get_instruction_args(self):
        """Returns the keyword args of build description."""
        return None

    def get_instruction_args_keys(self):
        """Returns the args keys of `build_description`."""
        return []

    def check_following(self, value):
        """Checks if the response is wrapped with double quotation marks."""
        value = value.strip()
        return len(value) > 1 and value[0] == '"' and value[-1] == '"'



class ListKeywordFrequencyChecker(Instruction):
    def build_description(self, *, letters=None, frequency=None, relation=None, position=None):
        """Build the instruction description.

        Args:
          keywords: A list of keywords that are expected in the response.
          frequency: An integer specifying the number of times `keywords` is expected
            to appear in the response.
          relation: A string in (`less than`, `at least`), defining the relational
            operator for comparison.
            Two relational comparisons are supported for now:
            if 'less than', the actual number of occurrences < frequency;
            if 'at least', the actual number of occurrences >= frequency.

        Returns:
          A string representing the instruction description.
        """
        assert letters is not None, "letters is required"
        assert position is not None, "position is required"
        assert relation is not None, "relation is required"
        assert frequency is not None, "frequency is required"

        self._letters = letters
        self._position = position
        self._relation = relation
        self._frequency = frequency

        self._description_pattern = (
            "In your response, the letter {letters} should appear {position} {relation} {frequency} times."
        )

        return self._description_pattern.format(
            letters=self._letters,
            position=self._position,
            relation=self._relation,
            frequency=self._frequency,
        )
    
    def get_instruction_args(self):
        return {
            "letters": self._letters,
            "position": self._position,
            "relation": self._relation,
            "frequency": self._frequency,
        }
    
    def get_instruction_args_keys(self):    
        return ["letters", "position", "relation", "frequency"]
    
    def check_following(self, value):
        """Checks that the response contains the letter at the right frequency."""
        count_dict = {letter: 0 for letter in self._letters}
        # Use the Unicode-aware regex
        words = re.findall(r'[\w\u0600-\u06FF]+', value)

        for word in words:
            if self._position == 'start':
                for letter in self._letters:
                    if word.startswith(letter):
                        count_dict[letter] += 1
            elif self._position == 'end':
                for letter in self._letters:
                    if word.endswith(letter):
                        count_dict[letter] += 1
        if self._relation == 'at least':
            return all(count_dict[letter] >= self._frequency for letter in self._letters) 
        elif self._relation == "less than":
            return all(count_dict[letter] < self._frequency for letter in self._letters)
        else:
            raise ValueError(f"Unsupported relation type: {self._relation}")


class ListKeywordExistenceChecker(Instruction):
    def build_description(self, *, keywords=None, mode=None):
        """Build the instruction description.

        Args:
          keywords: A list of keywords that are expected in the response.
          mode: A string in (`all`, `any`), defining the mode of the instruction.
        """
        assert keywords is not None, "keywords is required"
        assert mode is not None, "mode is required"

        self._keywords = keywords
        self._mode = mode

        self._description_pattern = (
            "In your response, the {mode} of the keywords {keywords} should appear."
        )

    
    def get_instruction_args(self):
        return {
            "keywords": self._keywords,
            "mode": self._mode,
        }
    
    def get_instruction_args_keys(self):
        return ["keywords", "mode"]
    
    def check_following(self, value):
        """Checks that the response contains the keywords in the right mode."""
        # Use the Unicode-aware regex
        words_in_response = set(re.findall(r'[\w\u0600-\u06FF]+', value))
        keywords_to_check = set(self._keywords)
        
        if self._mode == "all":
            return keywords_to_check.issubset(words_in_response)
        elif self._mode == "any":
            return not keywords_to_check.isdisjoint(words_in_response)
        else:
            raise ValueError(f"Unsupported mode type: {self._mode}")


class CountTashkeelChecker(Instruction):
    def build_description(self, *, tashkeel_name=None, count=None):
        """Build the instruction description.

        Args:
          tashkeel_name: A string in (`Kasratan`, `Dammatan`, `Fathatan`, `Shadda`), defining the tashkeel name.
          count: An integer specifying the number of times `tashkeel_name` is expected to appear in the response.
        """
        assert tashkeel_name is not None, "tashkeel_name is required"
        assert count is not None, "count is required"

        self._tashkeel_name = tashkeel_name
        self._count = count

        self._description_pattern = (
            "In your response, the {tashkeel_name} should appear {count} times."
        )

        return self._description_pattern.format(
            tashkeel_name=self._tashkeel_name,
            count=self._count,
        )
    
    def get_instruction_args(self):
        return {
            "tashkeel_name": self._tashkeel_name,
            "count": self._count,
        }
    
    def get_instruction_args_keys(self):
        return ["tashkeel_name", "count"]
    
    def check_following(self, value):
        """Checks that the response contains the tashkeel in the right count."""
        
        TASHKEEL = {
            # Tanwīn
            "Fathatan": "\u064B",  # ً
            "Dammatan": "\u064C",  # ٌ
            "Kasratan": "\u064D",  # ٍ
            # Short vowels
            "Fatha":     "\u064E",  # َ
            "Damma":     "\u064F",  # ُ
            "Kasra":     "\u0650",  # ِ
            # Shadda
            "Shadda":    "\u0651",  # ّ
        }

        # -------------  normalise once, count once  -------------------
        norm = unicodedata.normalize("NFKD", value)
        char_counts = Counter(c for c in norm if unicodedata.combining(c))

        name   = self._tashkeel_name
        needed = self._count

        if name not in TASHKEEL or not isinstance(needed, int) or needed < 0:
            raise ValueError(f"Bad requirement spec: {name} {needed}")

        mark = TASHKEEL[name]
        have = char_counts.get(mark, 0)
        return have == needed

        
        
        
            
            