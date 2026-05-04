"""
Tests for apps/assessments/evaluation_engine.py

Covers:
  - weighted domain score calculation
  - concept score grouping and accuracy
  - skill_level / readiness_level tier derivation
  - strength / weakness tag classification
  - skill profile vector normalisation
  - improvement_delta (first vs subsequent attempts)
  - recommended task type mapping
  - detailed_breakdown per question
  - evaluate() integration (with mock objects, no DB)
  - edge cases: no concepts tagged, all correct, all wrong, single question
"""

from unittest import TestCase
from unittest.mock import MagicMock, patch

from apps.assessments.evaluation_engine import (
    _compute_concept_scores,
    _compute_domain_score,
    _derive_readiness,
    _derive_skill_level,
    _build_skill_profile_vector,
    _build_tag_lists,
    _build_detailed_breakdown,
    _get_improvement_delta,
    evaluate,
    STRENGTH_THRESHOLD,
    WEAKNESS_THRESHOLD,
    _DEFAULT_CONCEPT,
)


# ─────────────────────────────────────────────
# Helpers to build mock Question objects
# ─────────────────────────────────────────────

def _make_question(qid, correct_option, concept='', difficulty_weight=1.0, text='Test question'):
    q = MagicMock()
    q.id = qid
    q.text = text
    q.correct_option = correct_option
    q.concept = concept
    q.difficulty_weight = difficulty_weight
    return q


def _make_assessment(domain='Programming'):
    a = MagicMock()
    a.domain = domain
    return a


def _make_student():
    return MagicMock()


# ─────────────────────────────────────────────
# Unit tests – _derive_skill_level
# ─────────────────────────────────────────────

class TestDeriveSkillLevel(TestCase):
    def test_advanced(self):
        self.assertEqual(_derive_skill_level(80), 'Advanced')
        self.assertEqual(_derive_skill_level(100), 'Advanced')
        self.assertEqual(_derive_skill_level(95.5), 'Advanced')

    def test_intermediate(self):
        self.assertEqual(_derive_skill_level(50), 'Intermediate')
        self.assertEqual(_derive_skill_level(79.9), 'Intermediate')

    def test_beginner(self):
        self.assertEqual(_derive_skill_level(0), 'Beginner')
        self.assertEqual(_derive_skill_level(49.9), 'Beginner')


# ─────────────────────────────────────────────
# Unit tests – _derive_readiness
# ─────────────────────────────────────────────

class TestDeriveReadiness(TestCase):
    def test_expert(self):
        self.assertEqual(_derive_readiness(90), 'Expert')
        self.assertEqual(_derive_readiness(100), 'Expert')

    def test_proficient(self):
        self.assertEqual(_derive_readiness(75), 'Proficient')
        self.assertEqual(_derive_readiness(89.9), 'Proficient')

    def test_competent(self):
        self.assertEqual(_derive_readiness(60), 'Competent')
        self.assertEqual(_derive_readiness(74.9), 'Competent')

    def test_developing(self):
        self.assertEqual(_derive_readiness(40), 'Developing')
        self.assertEqual(_derive_readiness(59.9), 'Developing')

    def test_novice(self):
        self.assertEqual(_derive_readiness(0), 'Novice')
        self.assertEqual(_derive_readiness(39.9), 'Novice')


# ─────────────────────────────────────────────
# Unit tests – _compute_domain_score
# ─────────────────────────────────────────────

class TestComputeDomainScore(TestCase):
    def _answers(self, questions, correct_ids):
        return {str(q.id): q.correct_option if q.id in correct_ids else 'X'
                for q in questions}

    def test_all_correct_equal_weights(self):
        qs = [_make_question(i, 'A') for i in range(1, 6)]
        answers = {str(q.id): 'A' for q in qs}
        self.assertEqual(_compute_domain_score(qs, answers), 100.0)

    def test_all_wrong(self):
        qs = [_make_question(i, 'A') for i in range(1, 6)]
        answers = {str(q.id): 'B' for q in qs}
        self.assertEqual(_compute_domain_score(qs, answers), 0.0)

    def test_half_correct_equal_weights(self):
        qs = [_make_question(i, 'A') for i in range(1, 5)]  # 4 questions
        answers = {'1': 'A', '2': 'A', '3': 'B', '4': 'B'}
        self.assertEqual(_compute_domain_score(qs, answers), 50.0)

    def test_weighted_score_higher_weight_correct(self):
        # Q1 weight=1, Q2 weight=3. Correct only Q2 → 3/4 = 75%
        qs = [
            _make_question(1, 'A', difficulty_weight=1.0),
            _make_question(2, 'A', difficulty_weight=3.0),
        ]
        answers = {'1': 'B', '2': 'A'}  # Q1 wrong, Q2 correct
        self.assertAlmostEqual(_compute_domain_score(qs, answers), 75.0)

    def test_weighted_score_lower_weight_correct(self):
        # Q1 weight=3, Q2 weight=1. Correct only Q2 → 1/4 = 25%
        qs = [
            _make_question(1, 'A', difficulty_weight=3.0),
            _make_question(2, 'A', difficulty_weight=1.0),
        ]
        answers = {'1': 'B', '2': 'A'}  # Q1 wrong, Q2 correct
        self.assertAlmostEqual(_compute_domain_score(qs, answers), 25.0)

    def test_empty_questions(self):
        self.assertEqual(_compute_domain_score([], {}), 0.0)


# ─────────────────────────────────────────────
# Unit tests – _compute_concept_scores
# ─────────────────────────────────────────────

class TestComputeConceptScores(TestCase):
    def test_groups_by_concept(self):
        qs = [
            _make_question(1, 'A', concept='loops'),
            _make_question(2, 'A', concept='loops'),
            _make_question(3, 'A', concept='recursion'),
        ]
        answers = {'1': 'A', '2': 'B', '3': 'A'}  # loops: 1/2, recursion: 1/1
        scores = _compute_concept_scores(qs, answers)

        self.assertIn('loops', scores)
        self.assertIn('recursion', scores)
        self.assertEqual(scores['loops']['correct'], 1)
        self.assertEqual(scores['loops']['total'], 2)
        self.assertAlmostEqual(scores['loops']['score_pct'], 50.0)
        self.assertEqual(scores['recursion']['correct'], 1)
        self.assertAlmostEqual(scores['recursion']['score_pct'], 100.0)

    def test_no_concept_uses_default(self):
        qs = [_make_question(1, 'A', concept='')]
        answers = {'1': 'A'}
        scores = _compute_concept_scores(qs, answers)
        self.assertIn(_DEFAULT_CONCEPT, scores)

    def test_unanswered_counts_as_wrong(self):
        qs = [_make_question(1, 'A', concept='algebra')]
        scores = _compute_concept_scores(qs, {})  # no answer submitted
        self.assertEqual(scores['algebra']['correct'], 0)
        self.assertAlmostEqual(scores['algebra']['score_pct'], 0.0)


# ─────────────────────────────────────────────
# Unit tests – _build_tag_lists
# ─────────────────────────────────────────────

class TestBuildTagLists(TestCase):
    def _concept_scores(self, mapping):
        """mapping = {concept: score_pct}"""
        return {
            c: {'score_pct': pct, 'correct': 1, 'total': 1,
                'total_weight': 1.0, 'correct_weight': pct / 100,
                'weighted_score': pct}
            for c, pct in mapping.items()
        }

    def test_strength_above_threshold(self):
        cs = self._concept_scores({'typography': STRENGTH_THRESHOLD, 'colour': 100.0})
        strengths, weaknesses = _build_tag_lists(cs)
        self.assertIn('typography', strengths)
        self.assertIn('colour', strengths)
        self.assertEqual(weaknesses, [])

    def test_weakness_below_threshold(self):
        cs = self._concept_scores({'recursion': WEAKNESS_THRESHOLD - 1})
        strengths, weaknesses = _build_tag_lists(cs)
        self.assertEqual(strengths, [])
        self.assertIn('recursion', weaknesses)

    def test_between_thresholds_neither_tag(self):
        mid = (STRENGTH_THRESHOLD + WEAKNESS_THRESHOLD) / 2
        cs = self._concept_scores({'sql': mid})
        strengths, weaknesses = _build_tag_lists(cs)
        self.assertNotIn('sql', strengths)
        self.assertNotIn('sql', weaknesses)

    def test_tags_sorted(self):
        cs = self._concept_scores({'zebra': 100.0, 'alpha': 100.0})
        strengths, _ = _build_tag_lists(cs)
        self.assertEqual(strengths, sorted(strengths))


# ─────────────────────────────────────────────
# Unit tests – _build_skill_profile_vector
# ─────────────────────────────────────────────

class TestBuildSkillProfileVector(TestCase):
    def test_values_in_unit_range(self):
        concept_scores = {
            'loops':     {'weighted_score': 100.0, 'correct': 1, 'total': 1, 'score_pct': 100.0, 'total_weight': 1.0, 'correct_weight': 1.0},
            'recursion': {'weighted_score': 50.0,  'correct': 1, 'total': 2, 'score_pct': 50.0,  'total_weight': 2.0, 'correct_weight': 1.0},
            'variables': {'weighted_score': 0.0,   'correct': 0, 'total': 1, 'score_pct': 0.0,   'total_weight': 1.0, 'correct_weight': 0.0},
        }
        vector = _build_skill_profile_vector(concept_scores)
        for v in vector.values():
            self.assertGreaterEqual(v, 0.0)
            self.assertLessEqual(v, 1.0)
        self.assertAlmostEqual(vector['loops'], 1.0)
        self.assertAlmostEqual(vector['recursion'], 0.5)
        self.assertAlmostEqual(vector['variables'], 0.0)


# ─────────────────────────────────────────────
# Unit tests – _build_detailed_breakdown
# ─────────────────────────────────────────────

class TestBuildDetailedBreakdown(TestCase):
    def test_correct_question(self):
        q = _make_question(1, 'A', concept='loops', difficulty_weight=1.5, text='What is a loop?')
        breakdown = _build_detailed_breakdown([q], {'1': 'A'})
        self.assertTrue(breakdown['1']['is_correct'])
        self.assertEqual(breakdown['1']['concept'], 'loops')
        self.assertEqual(breakdown['1']['difficulty_weight'], 1.5)
        self.assertEqual(breakdown['1']['explanation'], 'Correctly answered!')

    def test_incorrect_question(self):
        q = _make_question(2, 'B', concept='recursion')
        breakdown = _build_detailed_breakdown([q], {'2': 'C'})
        self.assertFalse(breakdown['2']['is_correct'])
        self.assertIn('Correct answer: B', breakdown['2']['explanation'])

    def test_no_concept_falls_back_to_default(self):
        q = _make_question(3, 'A', concept='')
        breakdown = _build_detailed_breakdown([q], {'3': 'A'})
        self.assertEqual(breakdown['3']['concept'], _DEFAULT_CONCEPT)

    def test_unanswered_marked_not_correct(self):
        q = _make_question(4, 'A')
        breakdown = _build_detailed_breakdown([q], {})
        self.assertFalse(breakdown['4']['is_correct'])


# ─────────────────────────────────────────────
# Unit tests – _get_improvement_delta
# ─────────────────────────────────────────────

class TestGetImprovementDelta(TestCase):
    @patch('apps.assessments.models.AssessmentAttempt')
    def test_first_attempt_returns_none(self, MockAttempt):
        MockAttempt.objects.filter.return_value.order_by.return_value.values_list.return_value.first.return_value = None
        student = _make_student()
        result = _get_improvement_delta(student, 'Programming', 70.0)
        self.assertIsNone(result)

    @patch('apps.assessments.models.AssessmentAttempt')
    def test_improvement_positive(self, MockAttempt):
        MockAttempt.objects.filter.return_value.order_by.return_value.values_list.return_value.first.return_value = 60.0
        student = _make_student()
        result = _get_improvement_delta(student, 'Programming', 75.0)
        self.assertAlmostEqual(result, 15.0)

    @patch('apps.assessments.models.AssessmentAttempt')
    def test_improvement_negative(self, MockAttempt):
        MockAttempt.objects.filter.return_value.order_by.return_value.values_list.return_value.first.return_value = 80.0
        student = _make_student()
        result = _get_improvement_delta(student, 'Programming', 65.0)
        self.assertAlmostEqual(result, -15.0)


# ─────────────────────────────────────────────
# Integration tests – evaluate()
# ─────────────────────────────────────────────

class TestEvaluateIntegration(TestCase):
    """
    Tests the full evaluate() function with mock objects (no DB required).
    """

    def _run_evaluate(self, questions, answers, domain='Programming', previous=None):
        assessment = _make_assessment(domain)
        student = _make_student()
        with patch('apps.assessments.evaluation_engine._get_improvement_delta', return_value=previous):
            return evaluate(assessment, questions, answers, student)

    def test_basic_result_keys_present(self):
        qs = [_make_question(1, 'A')]
        result = self._run_evaluate(qs, {'1': 'A'})
        expected_keys = {
            'total_score', 'total_questions', 'percentage', 'domain_score',
            'skill_level', 'readiness_level', 'concept_scores',
            'strength_tags', 'weakness_tags', 'skill_profile_vector',
            'improvement_delta', 'recommended_task_type', 'recommended_next_step',
            'detailed_breakdown', 'strengths', 'weaknesses',
        }
        self.assertTrue(expected_keys.issubset(result.keys()))

    def test_all_correct(self):
        qs = [_make_question(i, 'A', concept='loops') for i in range(1, 6)]
        answers = {str(i): 'A' for i in range(1, 6)}
        result = self._run_evaluate(qs, answers)
        self.assertEqual(result['total_score'], 5)
        self.assertEqual(result['percentage'], 100.0)
        self.assertEqual(result['domain_score'], 100.0)
        self.assertEqual(result['skill_level'], 'Advanced')
        self.assertEqual(result['readiness_level'], 'Expert')
        self.assertIn('loops', result['strength_tags'])
        self.assertNotIn('loops', result['weakness_tags'])

    def test_all_wrong(self):
        qs = [_make_question(i, 'A', concept='loops') for i in range(1, 6)]
        answers = {str(i): 'B' for i in range(1, 6)}
        result = self._run_evaluate(qs, answers)
        self.assertEqual(result['total_score'], 0)
        self.assertEqual(result['domain_score'], 0.0)
        self.assertEqual(result['skill_level'], 'Beginner')
        self.assertEqual(result['readiness_level'], 'Novice')
        self.assertIn('loops', result['weakness_tags'])

    def test_weighted_domain_score_differs_from_percentage(self):
        # Q1 easy (weight 1), Q2 hard (weight 3). Student only answers Q2 correctly.
        qs = [
            _make_question(1, 'A', difficulty_weight=1.0),
            _make_question(2, 'A', difficulty_weight=3.0),
        ]
        answers = {'1': 'B', '2': 'A'}  # 1 correct out of 2 = 50% raw
        result = self._run_evaluate(qs, answers)
        self.assertAlmostEqual(result['percentage'], 50.0)
        self.assertAlmostEqual(result['domain_score'], 75.0)  # 3/4 weighted

    def test_multi_concept_breakdown(self):
        qs = [
            _make_question(1, 'A', concept='loops'),
            _make_question(2, 'A', concept='loops'),
            _make_question(3, 'A', concept='recursion'),
        ]
        answers = {'1': 'A', '2': 'B', '3': 'A'}
        result = self._run_evaluate(qs, answers)
        self.assertIn('loops', result['concept_scores'])
        self.assertIn('recursion', result['concept_scores'])
        self.assertAlmostEqual(result['concept_scores']['loops']['score_pct'], 50.0)
        self.assertAlmostEqual(result['concept_scores']['recursion']['score_pct'], 100.0)

    def test_skill_profile_vector_in_unit_range(self):
        qs = [_make_question(i, 'A', concept=f'c{i}') for i in range(1, 4)]
        answers = {'1': 'A', '2': 'B', '3': 'A'}
        result = self._run_evaluate(qs, answers)
        for val in result['skill_profile_vector'].values():
            self.assertGreaterEqual(val, 0.0)
            self.assertLessEqual(val, 1.0)

    def test_improvement_delta_passed_through(self):
        qs = [_make_question(1, 'A')]
        result = self._run_evaluate(qs, {'1': 'A'}, previous=12.5)
        self.assertAlmostEqual(result['improvement_delta'], 12.5)

    def test_improvement_delta_none_for_first_attempt(self):
        qs = [_make_question(1, 'A')]
        result = self._run_evaluate(qs, {'1': 'A'}, previous=None)
        self.assertIsNone(result['improvement_delta'])

    def test_recommended_task_type_novice(self):
        qs = [_make_question(i, 'A') for i in range(1, 6)]
        answers = {str(i): 'B' for i in range(1, 6)}  # all wrong → Novice
        result = self._run_evaluate(qs, answers)
        self.assertEqual(result['recommended_task_type'], 'practice')

    def test_recommended_task_type_expert(self):
        qs = [_make_question(i, 'A') for i in range(1, 11)]  # 10 qs
        answers = {str(i): 'A' for i in range(1, 11)}  # all correct → Expert
        result = self._run_evaluate(qs, answers)
        self.assertEqual(result['recommended_task_type'], 'challenge')

    def test_empty_assessment_raises(self):
        assessment = _make_assessment()
        student = _make_student()
        with self.assertRaises(ValueError):
            evaluate(assessment, [], {}, student)

    def test_single_question_correct(self):
        q = _make_question(1, 'C', concept='colour theory', difficulty_weight=2.0)
        result = self._run_evaluate([q], {'1': 'C'})
        self.assertEqual(result['total_score'], 1)
        self.assertEqual(result['domain_score'], 100.0)

    def test_unanswered_question_treated_as_wrong(self):
        q = _make_question(1, 'A', concept='typography')
        result = self._run_evaluate([q], {})  # no answers submitted
        self.assertEqual(result['total_score'], 0)
        self.assertIn('typography', result['weakness_tags'])

    def test_detailed_breakdown_contains_all_questions(self):
        qs = [_make_question(i, 'A') for i in range(1, 4)]
        answers = {'1': 'A', '2': 'B', '3': 'A'}
        result = self._run_evaluate(qs, answers)
        for q in qs:
            self.assertIn(str(q.id), result['detailed_breakdown'])
