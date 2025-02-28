# Copyright 2018 The Oppia Authors. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS-IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Tests for skill domain objects and methods defined on them."""

from __future__ import annotations

import datetime

from core import feconf
from core import utils
from core.constants import constants
from core.domain import skill_domain
from core.domain import state_domain
from core.tests import test_utils


class SkillDomainUnitTests(test_utils.GenericTestBase):
    """Test the skill domain object."""

    SKILL_ID = 'skill_id'
    MISCONCEPTION_ID = 0

    def setUp(self):
        super(SkillDomainUnitTests, self).setUp()
        example_1 = skill_domain.WorkedExample(
            state_domain.SubtitledHtml('2', '<p>Example Question 1</p>'),
            state_domain.SubtitledHtml('3', '<p>Example Explanation 1</p>')
        )
        skill_contents = skill_domain.SkillContents(
            state_domain.SubtitledHtml(
                '1', '<p>Explanation</p>'), [example_1],
            state_domain.RecordedVoiceovers.from_dict({
                'voiceovers_mapping': {
                    '1': {}, '2': {}, '3': {}
                }
            }),
            state_domain.WrittenTranslations.from_dict({
                'translations_mapping': {
                    '1': {}, '2': {}, '3': {}
                }
            })
        )
        misconceptions = [skill_domain.Misconception(
            self.MISCONCEPTION_ID, 'name', '<p>notes</p>',
            '<p>default_feedback</p>', True)]
        rubrics = [
            skill_domain.Rubric(
                constants.SKILL_DIFFICULTIES[0], ['<p>Explanation 1</p>']),
            skill_domain.Rubric(
                constants.SKILL_DIFFICULTIES[1], ['<p>Explanation 2</p>']),
            skill_domain.Rubric(
                constants.SKILL_DIFFICULTIES[2], ['<p>Explanation 3</p>'])]
        self.skill = skill_domain.Skill(
            self.SKILL_ID, 'Description', misconceptions, rubrics,
            skill_contents, feconf.CURRENT_MISCONCEPTIONS_SCHEMA_VERSION,
            feconf.CURRENT_RUBRIC_SCHEMA_VERSION,
            feconf.CURRENT_SKILL_CONTENTS_SCHEMA_VERSION, 'en', 0, 1,
            None, False, ['skill_id_2'],
            created_on=datetime.datetime.now(),
            last_updated=datetime.datetime.now())

    def _assert_validation_error(self, expected_error_substring):
        """Checks that the skill passes strict validation."""
        with self.assertRaisesRegex(
            utils.ValidationError, expected_error_substring):
            self.skill.validate()

    def test_skill_id_validation_fails_with_invalid_skill_id_type(self):
        with self.assertRaisesRegex(
            utils.ValidationError, 'Skill id should be a string'):
            skill_domain.Skill.require_valid_skill_id(10)

    def test_skill_id_validation_fails_with_invalid_skill_id_length(self):
        with self.assertRaisesRegex(
            utils.ValidationError, 'Invalid skill id'):
            skill_domain.Skill.require_valid_skill_id('abc')

    def test_valid_misconception_id(self):
        self.skill.next_misconception_id = 'invalid_id'
        self._assert_validation_error(
            'Expected misconception ID to be an integer')

    def test_get_all_html_content_strings(self):
        html_strings = self.skill.get_all_html_content_strings()
        self.assertEqual(len(html_strings), 8)

    def test_valid_misconception_name(self):
        misconception_name = 'This string is smaller than 50'
        self.skill.update_misconception_name(0, misconception_name)
        self.skill.validate()
        with self.assertRaisesRegex(
            ValueError,
            'There is no misconception with the given id.'
        ):
            self.skill.update_misconception_name(1, misconception_name)
        misconception_name = (
            'etiam non quam lacus suspendisse faucibus interdum posuere lorem '
            'ipsum dolor sit amet consectetur adipiscing elit duis tristique '
            'sollicitudin nibh sit amet commodo nulla facilisi')
        self.skill.update_misconception_name(0, misconception_name)
        self._assert_validation_error(
            'Misconception name should be less than 100 chars'
        )
        self.assertEqual(self.skill.get_incremented_misconception_id(0), 1)

    def test_update_contents_from_model(self):
        versioned_skill_contents = {
            'schema_version': 1,
            'skill_contents': {
                'explanation': {
                    'content_id': '1',
                    'html': '<p>Feedback</p>'
                    '<oppia-noninteractive-math raw_latex-with-valu'
                    'e="&amp;quot;+,-,-,+&amp;quot;">'
                    '</oppia-noninteractive-math>',
                },
                'recorded_voiceovers': {
                    'voiceovers_mapping': {
                        'explanation': {}
                    }
                },
                'written_translations': {
                    'translations_mapping': {
                        'explanation': {}
                    }
                },
                'worked_examples': [
                    {
                        'question': {
                            'html': '<p>A Question</p>'
                        },
                        'explanation': {
                            'html': '<p>An explanation</p>'
                        }
                    }
                ]
            }
        }
        self.skill.update_skill_contents_from_model(
            versioned_skill_contents,
            versioned_skill_contents['schema_version']
        )
        self.skill.validate()
        self.assertEqual(versioned_skill_contents['schema_version'], 2)
        self.assertEqual(
            versioned_skill_contents['skill_contents']['explanation'],
            {
                'content_id': '1',
                'html': '<p>Feedback</p><oppia-noninteractive-math '
                'math_content-with-v'
                'alue="{&amp;quot;raw_latex&amp;quot;: &amp;quot;+,-,-,+'
                '&amp;quot;, &amp;quot;svg_filename&amp;quot;: &amp;quot;&amp'
                ';quot;}"></oppia-noninteractive-math>',
            }
        )
        versioned_skill_contents['skill_contents']['explanation'] = {
            'content_id': '1',
            'html': '<oppia-noninteractive-svgdiagram '
                'svg_filename-with-value="&amp;quot;img1.svg&amp;quot;"'
                ' alt-with-value="&amp;quot;Image&amp;quot;">'
                '</oppia-noninteractive-svgdiagram>'
        }
        self.skill.update_skill_contents_from_model(
            versioned_skill_contents,
            versioned_skill_contents['schema_version']
        )
        self.skill.validate()
        self.assertEqual(versioned_skill_contents['schema_version'], 3)
        self.assertEqual(
            versioned_skill_contents['skill_contents']['explanation'],
            {
                'content_id': '1',
                'html': '<oppia-noninteractive-image '
                'alt-with-value="&amp;quot;Image&amp;quot;" '
                'caption-with-value="&amp;quot;&amp;quot;" '
                'filepath-with-value="&amp;quot;img1.svg&amp;quot;">'
                '</oppia-noninteractive-image>',
            }
        )
        versioned_skill_contents['skill_contents']['explanation']['html'] = (
            '<p><span>Test&nbsp;</span></p>'
        )
        self.skill.update_skill_contents_from_model(
            versioned_skill_contents,
            versioned_skill_contents['schema_version']
        )
        self.skill.validate()
        self.assertEqual(versioned_skill_contents['schema_version'], 4)
        self.assertEqual(
            versioned_skill_contents['skill_contents']['explanation'],
            {
                'content_id': '1',
                'html': '<p><span>Test </span></p>',
            }
        )

    def test_update_misconceptions_from_model(self):
        versioned_misconceptions = {
            'schema_version': 1,
            'misconceptions': [
                {
                    'misconception_id': self.MISCONCEPTION_ID,
                    'name': 'name',
                    'notes': '<p>notes</p>',
                    'feedback': '<p>feedback</p>',
                }
            ]
        }
        self.skill.update_misconceptions_from_model(
            versioned_misconceptions,
            versioned_misconceptions['schema_version']
        )
        self.skill.validate()
        self.assertEqual(versioned_misconceptions['schema_version'], 2)
        self.assertEqual(
            versioned_misconceptions['misconceptions'][0]['must_be_addressed'],
            True
        )
        versioned_misconceptions['misconceptions'][0]['feedback'] = (
            '<p>'
            'Feedback</p>'
            '<oppia-noninteractive-math raw_latex-with-valu'
            'e="&amp;quot;+,-,-,+&amp;quot;"></oppia-noninteractive-math>'
        )
        expected_feedback = (
            '<p>Feedback</p>'
            '<oppia-noninteractive-math math_content-with-v'
            'alue="{&amp;quot;raw_latex&amp;quot;: &amp;quot;+,-,-,+'
            '&amp;quot;, &amp;quot;svg_filename&amp;quot;: &amp;quot;&amp'
            ';quot;}"></oppia-noninteractive-math>'
        )
        self.skill.update_misconceptions_from_model(
            versioned_misconceptions,
            versioned_misconceptions['schema_version']
        )
        self.skill.validate()
        self.assertEqual(versioned_misconceptions['schema_version'], 3)
        self.assertEqual(
            versioned_misconceptions['misconceptions'][0]['feedback'],
            expected_feedback
        )
        self.skill.update_misconceptions_from_model(
            versioned_misconceptions,
            versioned_misconceptions['schema_version']
        )
        self.skill.validate()
        self.assertEqual(versioned_misconceptions['schema_version'], 4)
        versioned_misconceptions['misconceptions'][0]['feedback'] = (
            '<span>'
            'feedback&nbsp;</span>'
        )
        self.skill.update_misconceptions_from_model(
            versioned_misconceptions,
            versioned_misconceptions['schema_version']
        )
        self.assertEqual(versioned_misconceptions['schema_version'], 5)
        self.assertEqual(
            versioned_misconceptions['misconceptions'][0]['feedback'],
            '<span>feedback </span>'
        )

    def test_update_misconception_feedback(self):
        feedback = '<p>new_feedback</p>'
        self.skill.update_misconception_feedback(
            0, feedback)
        self.skill.validate()
        self.assertEqual(self.skill.misconceptions[0].feedback, feedback)
        with self.assertRaisesRegex(
            ValueError,
            'There is no misconception with the given id.'
        ):
            self.skill.update_misconception_feedback(1, feedback)

    def test_update_misconception_notes(self):
        new_notes = '<p>Update notes</p>'
        self.skill.update_misconception_notes(
            0, new_notes)
        self.skill.validate()
        self.assertEqual(self.skill.misconceptions[0].notes, new_notes)
        with self.assertRaisesRegex(
            ValueError,
            'There is no misconception with the given id.'
        ):
            self.skill.update_misconception_notes(1, new_notes)

    def test_update_misconception_must_be_addressed(self):
        must_be_addressed = False
        self.skill.update_misconception_must_be_addressed(
            0, must_be_addressed)
        self.skill.validate()
        self.assertEqual(
            self.skill.misconceptions[0].must_be_addressed,
            must_be_addressed
        )
        with self.assertRaisesRegex(
            ValueError,
            'There is no misconception with the given id.'
        ):
            self.skill.update_misconception_must_be_addressed(
                1, must_be_addressed)

    def test_delete_misconceptions(self):
        self.skill.delete_misconception(0)
        self.assertEqual(len(self.skill.misconceptions), 0)
        with self.assertRaisesRegex(
            ValueError,
            'There is no misconception with the given id.'
        ):
            self.skill.delete_misconception(0)

    def test_add_misconception(self):
        misconception = skill_domain.Misconception(
            self.MISCONCEPTION_ID + 1, 'name_2', '<p>notes_2</p>',
            '<p>default_feedback_2</p>', True)
        self.skill.add_misconception(misconception)
        self.skill.validate()
        self.assertEqual(self.skill.misconceptions[1], misconception)

    def test_delete_prerequisite_skill(self):
        with self.assertRaisesRegex(
            ValueError,
            'The skill to remove is not a prerequisite skill.'
        ):
            self.skill.delete_prerequisite_skill('some_id')
        self.skill.delete_prerequisite_skill('skill_id_2')
        self.assertEqual(len(self.skill.prerequisite_skill_ids), 0)

    def test_add_prerequisite_skill(self):
        self.skill.add_prerequisite_skill('skill_id_3')
        self.assertEqual(len(self.skill.prerequisite_skill_ids), 2)
        self.assertEqual(self.skill.prerequisite_skill_ids[1], 'skill_id_3')
        with self.assertRaisesRegex(
            ValueError,
            'The skill is already a prerequisite skill.'
        ):
            self.skill.add_prerequisite_skill('skill_id_2')

    def test_find_prerequisite_skill_id_index(self):
        # Disabling pylint protected access because this is a test.
        self.assertEqual(
            self.skill._find_prerequisite_skill_id_index('skill_id_2'), # pylint: disable=protected-access
            0
        )
        self.assertEqual(
            self.skill._find_prerequisite_skill_id_index('skill_id_3'), # pylint: disable=protected-access
            None
        )

    def test_update_explanation(self):
        new_explanation = state_domain.SubtitledHtml(
            '1',
            '<p>New Explanation</p>'
        )
        self.skill.update_explanation(new_explanation)
        self.skill.validate()
        self.assertEqual(
            self.skill.skill_contents.explanation,
            new_explanation
        )

    def test_update_rubric(self):
        difficulty = constants.SKILL_DIFFICULTIES[0]
        explanations = ['explanation1']
        self.skill.update_rubric(difficulty, explanations)
        with self.assertRaisesRegex(
            ValueError,
            'There is no rubric for the given difficulty.'
        ):
            self.skill.update_rubric('difficulty', explanations)

    def test_updates_on_skill(self):
        self.skill.update_description('Update Description')
        self.skill.update_language_code('de')
        self.skill.update_superseding_skill_id('1')
        self.skill.record_that_all_questions_are_merged(True)
        self.skill.validate()
        self.assertEqual(self.skill.description, 'Update Description')
        self.assertEqual(self.skill.language_code, 'de')
        self.assertEqual(self.skill.superseding_skill_id, '1')
        self.assertEqual(self.skill.all_questions_merged, True)

    def test_valid_misconception_must_be_addressed(self):
        self.skill.validate()
        must_be_addressed = 'False'
        with self.assertRaisesRegex(
            ValueError, 'must_be_addressed should be a bool value'):
            self.skill.update_misconception_must_be_addressed(
                0, must_be_addressed)

        self.skill.misconceptions[0].must_be_addressed = 'False'
        self._assert_validation_error(
            'Expected must_be_addressed to be a bool'
        )

    def test_rubrics_validation(self):
        self.skill.rubrics = 'rubric'
        self._assert_validation_error('Expected rubrics to be a list')

        self.skill.rubrics = ['rubric']
        self._assert_validation_error(
            'Expected each rubric to be a Rubric object')

        self.skill.rubrics = [
            skill_domain.Rubric(
                constants.SKILL_DIFFICULTIES[0], ['<p>Explanation</p>']),
            skill_domain.Rubric(
                constants.SKILL_DIFFICULTIES[0], ['<p>Another Explanation</p>'])
        ]
        self._assert_validation_error('Duplicate rubric found')

    def test_valid_rubric_difficulty(self):
        self.skill.rubrics = [skill_domain.Rubric(
            'invalid_difficulty', ['<p>Explanation</p>'])]
        self._assert_validation_error('Invalid difficulty received for rubric')

    def test_valid_rubric_difficulty_type(self):
        self.skill.rubrics = [skill_domain.Rubric(10, ['<p>Explanation</p>'])]
        self._assert_validation_error('Expected difficulty to be a string')

    def test_valid_rubric_explanation(self):
        self.skill.rubrics[0].explanations = 0
        self._assert_validation_error('Expected explanations to be a list')

        self.skill.rubrics[0].explanations = [0]
        self._assert_validation_error(
            'Expected each explanation to be a string')

    def test_rubric_present_for_all_difficulties(self):
        self.skill.validate()
        self.skill.rubrics = [
            skill_domain.Rubric(
                constants.SKILL_DIFFICULTIES[0], ['<p>Explanation 1</p>']),
            skill_domain.Rubric(
                constants.SKILL_DIFFICULTIES[1], ['<p>Explanation 2</p>'])
        ]
        self._assert_validation_error(
            'All 3 difficulties should be addressed in rubrics')

    def test_order_of_rubrics(self):
        self.skill.rubrics = [
            skill_domain.Rubric(
                constants.SKILL_DIFFICULTIES[1], ['<p>Explanation 1</p>']),
            skill_domain.Rubric(
                constants.SKILL_DIFFICULTIES[2], ['<p>Explanation 2</p>']),
            skill_domain.Rubric(
                constants.SKILL_DIFFICULTIES[0], ['<p>Explanation 3</p>'])
        ]
        self._assert_validation_error(
            'The difficulties should be ordered as follows')

    def test_description_validation(self):
        self.skill.description = 0
        self._assert_validation_error('Description should be a string')

        self.skill.description = (
            'etiam non quam lacus suspendisse faucibus interdum posuere lorem '
            'ipsum dolor sit amet consectetur adipiscing elit duis tristique '
            'sollicitudin nibh sit amet commodo nulla facilisi')
        self._assert_validation_error(
            'Skill description should be less than 100 chars')

    def test_prerequisite_skill_ids_validation(self):
        self.skill.prerequisite_skill_ids = 0
        self._assert_validation_error(
            'Expected prerequisite_skill_ids to be a list')
        self.skill.prerequisite_skill_ids = [0]
        self._assert_validation_error(
            'Expected each skill ID to be a string')

    def test_language_code_validation(self):
        self.skill.language_code = 0
        self._assert_validation_error('Expected language code to be a string')

        self.skill.language_code = 'xz'
        self._assert_validation_error('Invalid language code')

    def test_schema_versions_validation(self):
        self.skill.skill_contents_schema_version = 100
        self._assert_validation_error(
            'Expected skill contents schema version to be %s' %
            feconf.CURRENT_SKILL_CONTENTS_SCHEMA_VERSION)

        self.skill.skill_contents_schema_version = 'a'
        self._assert_validation_error(
            'Expected skill contents schema version to be an integer')

        self.skill.misconceptions_schema_version = 100
        self._assert_validation_error(
            'Expected misconceptions schema version to be %s' %
            feconf.CURRENT_MISCONCEPTIONS_SCHEMA_VERSION)

        self.skill.misconceptions_schema_version = 'a'
        self._assert_validation_error(
            'Expected misconceptions schema version to be an integer')

        self.skill.misconceptions_schema_version = 5
        self.skill.rubric_schema_version = 100
        self._assert_validation_error(
            'Expected rubric schema version to be %s' %
            feconf.CURRENT_RUBRIC_SCHEMA_VERSION)

        self.skill.rubric_schema_version = 'a'
        self._assert_validation_error(
            'Expected rubric schema version to be an integer')

    def test_misconception_validation(self):
        self.skill.misconceptions[0].feedback = 0
        self._assert_validation_error(
            'Expected misconception feedback to be a string')

        self.skill.misconceptions[0].notes = 0
        self._assert_validation_error(
            'Expected misconception notes to be a string')

        self.skill.misconceptions[0].name = 0
        self._assert_validation_error(
            'Expected misconception name to be a string')

        self.skill.misconceptions = ['']
        self._assert_validation_error(
            'Expected each misconception to be a Misconception object')

        self.skill.misconceptions = ''
        self._assert_validation_error('Expected misconceptions to be a list')

    def test_skill_contents_validation(self):
        self.skill.skill_contents.worked_examples = ''
        self._assert_validation_error('Expected worked examples to be a list')

        self.skill.skill_contents.worked_examples = [1]
        self._assert_validation_error(
            'Expected worked example to be a WorkedExample object')

        example = skill_domain.WorkedExample('question', 'explanation')
        self.skill.skill_contents.worked_examples = [example]
        self._assert_validation_error(
            'Expected example question to be a SubtitledHtml object')

        example = skill_domain.WorkedExample(
            state_domain.SubtitledHtml(
                '2', '<p>Example Question 1</p>'), 'explanation')
        self.skill.skill_contents.worked_examples = [example]
        self._assert_validation_error(
            'Expected example explanation to be a SubtitledHtml object')

        self.skill.skill_contents.explanation = 'explanation'
        self._assert_validation_error(
            'Expected skill explanation to be a SubtitledHtml object')

        self.skill.skill_contents = ''
        self._assert_validation_error(
            'Expected skill_contents to be a SkillContents object')

    def test_validate_duplicate_content_id(self):
        self.skill.skill_contents.worked_examples = (
            [skill_domain.WorkedExample(
                self.skill.skill_contents.explanation,
                self.skill.skill_contents.explanation)])
        self._assert_validation_error('Found a duplicate content id 1')

        example_1 = skill_domain.WorkedExample(
            state_domain.SubtitledHtml('4', '<p>Example Question 1</p>'),
            state_domain.SubtitledHtml('1', '<p>Example Explanation 1</p>')
        )
        self.skill.skill_contents.worked_examples = [example_1]
        self._assert_validation_error('Found a duplicate content id 1')

    def test_misconception_id_validation(self):
        self.skill.misconceptions = [
            skill_domain.Misconception(
                self.MISCONCEPTION_ID, 'name', '<p>notes</p>',
                '<p>default_feedback</p>', True),
            skill_domain.Misconception(
                self.MISCONCEPTION_ID, 'name 2', '<p>notes 2</p>',
                '<p>default_feedback</p>', True)]
        self._assert_validation_error('Duplicate misconception ID found')

    def test_skill_migration_validation(self):
        self.skill.superseding_skill_id = 'TestSkillId'
        self.skill.all_questions_merged = None
        self._assert_validation_error(
            'Expected a value for all_questions_merged when '
            'superseding_skill_id is set.')
        self.skill.superseding_skill_id = None
        self.skill.all_questions_merged = True
        self._assert_validation_error(
            'Expected a value for superseding_skill_id when '
            'all_questions_merged is True.')

    def test_create_default_skill(self):
        """Test the create_default_skill function."""
        rubrics = [
            skill_domain.Rubric(
                constants.SKILL_DIFFICULTIES[0],
                ['<p>[NOTE: Creator should fill this in]</p>']),
            skill_domain.Rubric(
                constants.SKILL_DIFFICULTIES[1],
                ['<p>[NOTE: Creator should fill this in]</p>']),
            skill_domain.Rubric(
                constants.SKILL_DIFFICULTIES[2],
                ['<p>[NOTE: Creator should fill this in]</p>'])]
        skill = skill_domain.Skill.create_default_skill(
            self.SKILL_ID, 'Description', rubrics)
        expected_skill_dict = {
            'id': self.SKILL_ID,
            'description': 'Description',
            'misconceptions': [],
            'rubrics': [rubric.to_dict() for rubric in rubrics],
            'skill_contents': {
                'explanation': {
                    'html': feconf.DEFAULT_SKILL_EXPLANATION,
                    'content_id': 'explanation'
                },
                'recorded_voiceovers': {
                    'voiceovers_mapping': {
                        'explanation': {}
                    }
                },
                'written_translations': {
                    'translations_mapping': {
                        'explanation': {}
                    }
                },
                'worked_examples': []
            },
            'misconceptions_schema_version': (
                feconf.CURRENT_MISCONCEPTIONS_SCHEMA_VERSION
            ),
            'rubric_schema_version': (
                feconf.CURRENT_RUBRIC_SCHEMA_VERSION
            ),
            'skill_contents_schema_version': (
                feconf.CURRENT_SKILL_CONTENTS_SCHEMA_VERSION
            ),
            'language_code': constants.DEFAULT_LANGUAGE_CODE,
            'next_misconception_id': 0,
            'version': 0,
            'superseding_skill_id': None,
            'all_questions_merged': False,
            'prerequisite_skill_ids': []
        }
        self.assertEqual(skill.to_dict(), expected_skill_dict)

    def test_conversion_to_and_from_dict(self):
        """Test that to_dict and from_dict preserve all data within a
        skill_contents and misconception object.
        """
        example_1 = skill_domain.WorkedExample(
            state_domain.SubtitledHtml('2', '<p>Example Question 1</p>'),
            state_domain.SubtitledHtml('3', '<p>Example Answer 1</p>')
        )
        skill_contents = skill_domain.SkillContents(
            state_domain.SubtitledHtml('1', '<p>Explanation</p>'), [example_1],
            state_domain.RecordedVoiceovers.from_dict({
                'voiceovers_mapping': {
                    '1': {}, '2': {}, '3': {}
                }
            }),
            state_domain.WrittenTranslations.from_dict({
                'translations_mapping': {
                    '1': {}, '2': {}, '3': {}
                }
            })
        )
        skill_contents_dict = skill_contents.to_dict()
        skill_contents_from_dict = skill_domain.SkillContents.from_dict(
            skill_contents_dict)

        misconceptions = skill_domain.Misconception(
            self.MISCONCEPTION_ID, 'Tag Name', '<p>Description</p>',
            '<p>Feedback</p>', True)
        misconceptions_dict = misconceptions.to_dict()
        misconceptions_from_dict = skill_domain.Misconception.from_dict(
            misconceptions_dict)

        rubric = skill_domain.Rubric(
            constants.SKILL_DIFFICULTIES[0], ['<p>Explanation</p>'])
        rubric_dict = rubric.to_dict()
        rubric_from_dict = skill_domain.Rubric.from_dict(rubric_dict)
        self.assertEqual(
            skill_contents_from_dict.to_dict(), skill_contents_dict)
        self.assertEqual(
            misconceptions_from_dict.to_dict(), misconceptions_dict)
        self.assertEqual(
            rubric_from_dict.to_dict(), rubric_dict)

    def test_skill_mastery_to_dict(self):
        expected_skill_mastery_dict = {
            'user_id': 'user',
            'skill_id': 'skill_id',
            'degree_of_mastery': '0.5'
        }
        observed_skill_mastery = skill_domain.UserSkillMastery.from_dict(
            expected_skill_mastery_dict)
        self.assertDictEqual(
            expected_skill_mastery_dict,
            observed_skill_mastery.to_dict())

    def test_update_worked_examples(self):
        question_1 = {
            'content_id': 'question_1',
            'html': '<p>Worked example question 1</p>'
        }
        explanation_1 = {
            'content_id': 'explanation_1',
            'html': '<p>Worked example explanation 1</p>'
        }
        question_2 = {
            'content_id': 'question_2',
            'html': '<p>Worked example question 2</p>'
        }
        explanation_2 = {
            'content_id': 'explanation_2',
            'html': '<p>Worked example explanation 2</p>'
        }
        worked_examples_dict_list = [{
            'question': question_1,
            'explanation': explanation_1
        }, {
            'question': question_2,
            'explanation': explanation_2
        }]

        worked_examples_object_list = [
            skill_domain.WorkedExample.from_dict(worked_example)
            for worked_example in worked_examples_dict_list]

        self.skill.update_worked_examples(worked_examples_object_list)
        self.skill.validate()

        # Delete the last worked_example.
        worked_examples_object_list.pop()

        self.skill.update_worked_examples(worked_examples_object_list)
        self.skill.validate()

    def test_require_valid_description_with_empty_description_raise_error(self):
        with self.assertRaisesRegex(
            Exception, 'Description field should not be empty'):
            self.skill.require_valid_description('')

    def test_misconception_id_range(self):
        self.skill.misconceptions[0].id = 5
        self._assert_validation_error(
            'The misconception with id 5 is out of bounds')

    def test_skill_export_import_returns_original_object(self):
        """Checks that to_dict and from_dict preserves all the data within a
        Skill during export and import.
        """
        skill_dict = self.skill.to_dict()
        skill_from_dict = skill_domain.Skill.from_dict(skill_dict)
        self.assertEqual(skill_from_dict.to_dict(), skill_dict)

    def test_serialize_and_deserialize_returns_unchanged_skill(self):
        """Checks that serializing and then deserializing a default skill
        works as intended by leaving the skill unchanged.
        """
        self.assertEqual(
            self.skill.to_dict(),
            skill_domain.Skill.deserialize(
                self.skill.serialize()).to_dict())

    def test_generate_skill_misconception_id(self):
        """Checks that skill misconception id is generated correctly."""
        self.assertEqual(
            self.skill.generate_skill_misconception_id(0),
            '%s-%d' % (self.skill.id, 0))
        self.assertEqual(
            self.skill.generate_skill_misconception_id(1),
            '%s-%d' % (self.skill.id, 1))

    def test_update_rubrics_from_model(self):
        """Checks that skill misconception id is generated correctly."""
        versioned_rubrics = {
            'schema_version': 1,
            'rubrics': [
                {'explanation': 'explanation1'},
                {'explanation': 'explanation2'}
            ]
        }

        skill_domain.Skill.update_rubrics_from_model(versioned_rubrics, 1)

        self.assertEqual(versioned_rubrics, {
            'schema_version': 2,
            'rubrics': [
                {'explanations': ['explanation1']},
                {'explanations': ['explanation2']}
            ]
        })
        versioned_rubrics['rubrics'][0]['explanations'] = [
        '<p>Explanation</p>'
        '<oppia-noninteractive-math raw_latex-with-valu'
        'e="&amp;quot;+,-,-,+&amp;quot;"></oppia-noninteractive-math>'
        ]
        skill_domain.Skill.update_rubrics_from_model(
            versioned_rubrics, 2)
        self.skill.validate()
        self.assertEqual(versioned_rubrics, {
            'schema_version': 3,
            'rubrics': [
                {
                    'explanations': [
                        (
                            '<p>Explanation</p>'
                            '<oppia-noninteractive-math math_content-with-v'
                            'alue="{&amp;quot;raw_latex&amp;quot;:'
                            ' &amp;quot;+,-,-,'
                            '+&amp;quot;, &amp;quot;svg_filename'
                            '&amp;quot;: &amp;quot;&amp'
                            ';quot;}"></oppia-noninteractive-math>'
                        )
                    ]
                 },
                {'explanations': ['explanation2']}
            ]
        })
        versioned_rubrics['rubrics'][0]['explanations'] = [(
            '<oppia-noninteractive-svgdiagram '
            'svg_filename-with-value="&amp;quot;img1.svg&amp;quot;"'
            ' alt-with-value="&amp;quot;Image&amp;quot;">'
            '</oppia-noninteractive-svgdiagram>'
        )]
        skill_domain.Skill.update_rubrics_from_model(
            versioned_rubrics, 3)
        self.skill.validate()
        self.assertEqual(versioned_rubrics, {
            'schema_version': 4,
            'rubrics': [
                {
                    'explanations': [
                        '<oppia-noninteractive-image '
                        'alt-with-value="&amp;quot;Image&amp;quot;" '
                        'caption-with-value="&amp;quot;&amp;quot;" '
                        'filepath-with-value="&amp;quot;img1.svg&amp;quot;">'
                        '</oppia-noninteractive-image>'
                    ]
                 },
                {'explanations': ['explanation2']}
            ]
        })
        versioned_rubrics['rubrics'][0]['explanations'] = [
            '<span>explanation&nbsp;</span>']
        skill_domain.Skill.update_rubrics_from_model(
            versioned_rubrics, 4)
        self.skill.validate()
        self.assertEqual(versioned_rubrics, {
            'schema_version': 5,
            'rubrics': [
                {
                    'explanations': ['<span>explanation </span>']
                 },
                {'explanations': ['explanation2']}
            ]
        })


class SkillChangeTests(test_utils.GenericTestBase):

    def test_skill_change_object_with_missing_cmd(self):
        with self.assertRaisesRegex(
            utils.ValidationError, 'Missing cmd key in change dict'):
            skill_domain.SkillChange({'invalid': 'data'})

    def test_skill_change_object_with_invalid_cmd(self):
        with self.assertRaisesRegex(
            utils.ValidationError, 'Command invalid is not allowed'):
            skill_domain.SkillChange({'cmd': 'invalid'})

    def test_skill_change_object_with_missing_attribute_in_cmd(self):
        with self.assertRaisesRegex(
            utils.ValidationError, (
                'The following required attributes are missing: '
                'new_value, old_value')):
            skill_domain.SkillChange({
                'cmd': 'update_skill_property',
                'property_name': 'name',
            })

    def test_skill_change_object_with_extra_attribute_in_cmd(self):
        with self.assertRaisesRegex(
            utils.ValidationError, (
                'The following extra attributes are present: invalid')):
            skill_domain.SkillChange({
                'cmd': 'add_skill_misconception',
                'new_misconception_dict': {
                    'id': 0, 'name': 'name', 'notes': '<p>notes</p>',
                    'feedback': '<p>default_feedback</p>'},
                'invalid': 'invalid'
            })

    def test_skill_change_object_with_invalid_skill_property(self):
        with self.assertRaisesRegex(
            utils.ValidationError, (
                'Value for property_name in cmd update_skill_property: '
                'invalid is not allowed')):
            skill_domain.SkillChange({
                'cmd': 'update_skill_property',
                'property_name': 'invalid',
                'old_value': 'old_value',
                'new_value': 'new_value',
            })

    def test_skill_change_object_with_invalid_skill_misconception_property(
            self):
        with self.assertRaisesRegex(
            utils.ValidationError, (
                'Value for property_name in cmd '
                'update_skill_misconceptions_property: invalid is not '
                'allowed')):
            skill_domain.SkillChange({
                'cmd': 'update_skill_misconceptions_property',
                'misconception_id': 'id',
                'property_name': 'invalid',
                'old_value': 'old_value',
                'new_value': 'new_value',
            })

    def test_skill_change_object_with_invalid_skill_contents_property(
            self):
        with self.assertRaisesRegex(
            utils.ValidationError, (
                'Value for property_name in cmd '
                'update_skill_contents_property: invalid is not allowed')):
            skill_domain.SkillChange({
                'cmd': 'update_skill_contents_property',
                'property_name': 'invalid',
                'old_value': 'old_value',
                'new_value': 'new_value',
            })

    def test_skill_change_object_with_add_skill_misconception(self):
        skill_change_object = skill_domain.SkillChange({
            'cmd': 'add_skill_misconception',
            'new_misconception_dict': {
                'id': 0, 'name': 'name', 'notes': '<p>notes</p>',
                'feedback': '<p>default_feedback</p>'},
        })

        self.assertEqual(skill_change_object.cmd, 'add_skill_misconception')
        self.assertEqual(
            skill_change_object.new_misconception_dict, {
                'id': 0, 'name': 'name', 'notes': '<p>notes</p>',
                'feedback': '<p>default_feedback</p>'})

    def test_skill_change_object_with_update_rubrics(self):
        skill_change_object = skill_domain.SkillChange({
            'cmd': 'update_rubrics',
            'difficulty': constants.SKILL_DIFFICULTIES[0],
            'explanations': ['<p>Explanation</p>']
        })

        self.assertEqual(skill_change_object.cmd, 'update_rubrics')
        self.assertEqual(
            skill_change_object.difficulty, constants.SKILL_DIFFICULTIES[0])
        self.assertEqual(
            skill_change_object.explanations, ['<p>Explanation</p>'])

    def test_skill_change_object_with_delete_skill_misconception(self):
        skill_change_object = skill_domain.SkillChange({
            'cmd': 'delete_skill_misconception',
            'misconception_id': 'id'
        })

        self.assertEqual(
            skill_change_object.cmd, 'delete_skill_misconception')
        self.assertEqual(skill_change_object.misconception_id, 'id')

    def test_skill_change_object_with_update_skill_misconceptions_property(
            self):
        skill_change_object = skill_domain.SkillChange({
            'cmd': 'update_skill_misconceptions_property',
            'misconception_id': 'id',
            'property_name': 'name',
            'new_value': 'new_value',
            'old_value': 'old_value'
        })

        self.assertEqual(
            skill_change_object.cmd, 'update_skill_misconceptions_property')
        self.assertEqual(skill_change_object.misconception_id, 'id')
        self.assertEqual(skill_change_object.property_name, 'name')
        self.assertEqual(skill_change_object.new_value, 'new_value')
        self.assertEqual(skill_change_object.old_value, 'old_value')

    def test_skill_change_object_with_update_skill_property(
            self):
        skill_change_object = skill_domain.SkillChange({
            'cmd': 'update_skill_property',
            'property_name': 'description',
            'new_value': 'new_value',
            'old_value': 'old_value'
        })

        self.assertEqual(skill_change_object.cmd, 'update_skill_property')
        self.assertEqual(skill_change_object.property_name, 'description')
        self.assertEqual(skill_change_object.new_value, 'new_value')
        self.assertEqual(skill_change_object.old_value, 'old_value')

    def test_skill_change_object_with_update_skill_contents_property(
            self):
        skill_change_object = skill_domain.SkillChange({
            'cmd': 'update_skill_contents_property',
            'property_name': 'explanation',
            'new_value': 'new_value',
            'old_value': 'old_value'
        })

        self.assertEqual(
            skill_change_object.cmd, 'update_skill_contents_property')
        self.assertEqual(skill_change_object.property_name, 'explanation')
        self.assertEqual(skill_change_object.new_value, 'new_value')
        self.assertEqual(skill_change_object.old_value, 'old_value')

    def test_skill_change_object_with_create_new(self):
        skill_change_object = skill_domain.SkillChange({
            'cmd': 'create_new'
        })

        self.assertEqual(skill_change_object.cmd, 'create_new')

    def test_skill_change_object_with_migrate_contents_schema_to_latest_version(
            self):
        skill_change_object = skill_domain.SkillChange({
            'cmd': 'migrate_contents_schema_to_latest_version',
            'from_version': 'from_version',
            'to_version': 'to_version',
        })

        self.assertEqual(
            skill_change_object.cmd,
            'migrate_contents_schema_to_latest_version')
        self.assertEqual(skill_change_object.from_version, 'from_version')
        self.assertEqual(skill_change_object.to_version, 'to_version')

    def test_skill_change_object_with_migrate_misconceptions_schema_to_latest_version( # pylint: disable=line-too-long
            self):
        skill_change_object = skill_domain.SkillChange({
            'cmd': 'migrate_misconceptions_schema_to_latest_version',
            'from_version': 'from_version',
            'to_version': 'to_version'
        })

        self.assertEqual(
            skill_change_object.cmd,
            'migrate_misconceptions_schema_to_latest_version')
        self.assertEqual(skill_change_object.from_version, 'from_version')
        self.assertEqual(skill_change_object.to_version, 'to_version')

    def test_skill_change_object_with_migrate_rubrics_schema_to_latest_version(
            self):
        skill_change_object = skill_domain.SkillChange({
            'cmd': 'migrate_rubrics_schema_to_latest_version',
            'from_version': 'from_version',
            'to_version': 'to_version'
        })

        self.assertEqual(
            skill_change_object.cmd,
            'migrate_rubrics_schema_to_latest_version')
        self.assertEqual(skill_change_object.from_version, 'from_version')
        self.assertEqual(skill_change_object.to_version, 'to_version')

    def test_to_dict(self):
        skill_change_dict = {
            'cmd': 'migrate_misconceptions_schema_to_latest_version',
            'from_version': 'from_version',
            'to_version': 'to_version'
        }
        skill_change_object = skill_domain.SkillChange(skill_change_dict)
        self.assertEqual(skill_change_object.to_dict(), skill_change_dict)


class SkillSummaryTests(test_utils.GenericTestBase):

    def setUp(self):
        super(SkillSummaryTests, self).setUp()
        current_time = datetime.datetime.utcnow()
        time_in_millisecs = utils.get_time_in_millisecs(current_time)
        self.skill_summary_dict = {
            'id': 'skill_id',
            'description': 'description',
            'language_code': 'en',
            'version': 1,
            'misconception_count': 1,
            'worked_examples_count': 1,
            'skill_model_created_on': time_in_millisecs,
            'skill_model_last_updated': time_in_millisecs
        }

        self.skill_summary = skill_domain.SkillSummary(
            'skill_id', 'description', 'en', 1, 1, 1,
            current_time, current_time)

    def test_skill_summary_gets_created(self):
        self.assertEqual(
            self.skill_summary.to_dict(), self.skill_summary_dict)

    def test_validation_passes_with_valid_properties(self):
        self.skill_summary.validate()

    def test_validation_fails_with_invalid_description(self):
        self.skill_summary.description = 0
        with self.assertRaisesRegex(
            utils.ValidationError, 'Description should be a string.'):
            self.skill_summary.validate()

    def test_validation_fails_with_empty_description(self):
        self.skill_summary.description = ''
        with self.assertRaisesRegex(
            utils.ValidationError, 'Description field should not be empty'):
            self.skill_summary.validate()

    def test_validation_fails_with_invalid_language_code(self):
        self.skill_summary.language_code = 0
        with self.assertRaisesRegex(
            utils.ValidationError,
            'Expected language code to be a string, received 0'):
            self.skill_summary.validate()

    def test_validation_fails_with_unallowed_language_code(self):
        self.skill_summary.language_code = 'invalid'
        with self.assertRaisesRegex(
            utils.ValidationError, 'Invalid language code: invalid'):
            self.skill_summary.validate()

    def test_validation_fails_with_invalid_misconception_count(self):
        self.skill_summary.misconception_count = '10'
        with self.assertRaisesRegex(
            utils.ValidationError,
            'Expected misconception_count to be an int, received \'10\''):
            self.skill_summary.validate()

    def test_validation_fails_with_negative_misconception_count(self):
        self.skill_summary.misconception_count = -1
        with self.assertRaisesRegex(
            utils.ValidationError, (
                'Expected misconception_count to be non-negative, '
                'received \'-1\'')):
            self.skill_summary.validate()

    def test_validation_fails_with_invalid_worked_examples_count(self):
        self.skill_summary.worked_examples_count = '10'
        with self.assertRaisesRegex(
            utils.ValidationError,
            'Expected worked_examples_count to be an int, received \'10\''):
            self.skill_summary.validate()

    def test_validation_fails_with_negative_worked_examples_count(self):
        self.skill_summary.worked_examples_count = -1
        with self.assertRaisesRegex(
            utils.ValidationError, (
                'Expected worked_examples_count to be non-negative, '
                'received \'-1\'')):
            self.skill_summary.validate()


class AugmentedSkillSummaryTests(test_utils.GenericTestBase):

    def setUp(self):
        super(AugmentedSkillSummaryTests, self).setUp()
        current_time = datetime.datetime.utcnow()
        self.time_in_millisecs = utils.get_time_in_millisecs(current_time)

        self.augmented_skill_summary = skill_domain.AugmentedSkillSummary(
            'skill_id', 'description', 'en', 1, 1, 1,
            ['topic1'], ['math'], current_time, current_time)

    def test_augmented_skill_summary_gets_created(self):
        augmented_skill_summary_dict = {
            'id': 'skill_id',
            'description': 'description',
            'language_code': 'en',
            'version': 1,
            'misconception_count': 1,
            'worked_examples_count': 1,
            'topic_names': ['topic1'],
            'classroom_names': ['math'],
            'skill_model_created_on': self.time_in_millisecs,
            'skill_model_last_updated': self.time_in_millisecs
        }
        self.assertEqual(
            self.augmented_skill_summary.to_dict(),
            augmented_skill_summary_dict)


class TopicAssignmentTests(test_utils.GenericTestBase):

    def setUp(self):
        super(TopicAssignmentTests, self).setUp()
        self.topic_assignments = skill_domain.TopicAssignment(
            'topic_id1', 'Topic1', 2, 1)

    def test_topic_assignments_gets_created(self):
        topic_assignments_dict = {
            'topic_id': 'topic_id1',
            'topic_name': 'Topic1',
            'topic_version': 2,
            'subtopic_id': 1,
        }
        self.assertEqual(
            self.topic_assignments.to_dict(),
            topic_assignments_dict)


class CategorizedSkillsTests(test_utils.GenericTestBase):

    def setUp(self):
        super(CategorizedSkillsTests, self).setUp()
        self.categorized_skills = skill_domain.CategorizedSkills()
        self.subtopic_titles = ['Subtopic Title 1', 'Subtopic Title 2']
        self.categorized_skills.add_topic('Topic Name', self.subtopic_titles)

    def test_validation_fails_with_duplicate_topic_name(self):
        with self.assertRaisesRegex(
            utils.ValidationError,
            'Topic name \'Topic Name\' is already added.'):
            self.categorized_skills.add_topic('Topic Name', [])

    def test_uncategorized_skill_gets_added(self):
        self.categorized_skills.add_uncategorized_skill(
            'Topic Name', 'skill_1', 'Description 1')

        self.assertEqual(self.categorized_skills.to_dict(), {
            'Topic Name': {
                'uncategorized': [{
                    'skill_id': 'skill_1',
                    'skill_description': 'Description 1',
                }],
                'Subtopic Title 1': [],
                'Subtopic Title 2': []
            }
        })

    def test_validation_fails_with_topic_name_not_added(self):
        with self.assertRaisesRegex(
            utils.ValidationError,
            'Topic name \'Topic Name 1\' is not added.'):
            self.categorized_skills.add_uncategorized_skill(
                'Topic Name 1', 'skill_1', 'Description 1')

    def test_subtopic_skill_gets_added(self):
        self.categorized_skills.add_subtopic_skill(
            'Topic Name', 'Subtopic Title 1', 'skill_2', 'Description 2')
        self.categorized_skills.add_subtopic_skill(
            'Topic Name', 'Subtopic Title 2', 'skill_3', 'Description 3')

        self.assertEqual(self.categorized_skills.to_dict(), {
            'Topic Name': {
                'uncategorized': [],
                'Subtopic Title 1': [{
                    'skill_id': 'skill_2',
                    'skill_description': 'Description 2'
                }],
                'Subtopic Title 2': [{
                    'skill_id': 'skill_3',
                    'skill_description': 'Description 3'
                }]
            }
        })

    def test_validation_fails_with_subtopic_title_not_added(self):
        with self.assertRaisesRegex(
            utils.ValidationError,
            'Subtopic title \'Subtopic Title 3\' is not added.'):
            self.categorized_skills.add_subtopic_skill(
                'Topic Name', 'Subtopic Title 3', 'skill_1', 'Description 1')


class ShortSkillSummaryTests(test_utils.GenericTestBase):

    def setUp(self):
        super(ShortSkillSummaryTests, self).setUp()
        self.skill_summary = skill_domain.SkillSummary(
            'skill_1', 'Description 1', 'en', 1,
            0, 0, datetime.datetime.now(), datetime.datetime.now())
        self.short_skill_summary = skill_domain.ShortSkillSummary(
            'skill_1', 'Description 1')

    def test_short_skill_summary_gets_created(self):
        short_skill_summary_dict = {
            'skill_id': 'skill_1',
            'skill_description': 'Description 1',
        }
        self.assertEqual(
            self.short_skill_summary.to_dict(),
            short_skill_summary_dict)

    def test_short_skill_summary_gets_created_from_skill_summary(self):
        short_skill_summary = (
            skill_domain.ShortSkillSummary.from_skill_summary(
                self.skill_summary))
        self.assertEqual(
            short_skill_summary.to_dict(),
            self.short_skill_summary.to_dict())
