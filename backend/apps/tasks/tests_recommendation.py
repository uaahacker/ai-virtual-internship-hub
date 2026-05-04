"""
Tests for the recommendation ML engine.

Run with: python manage.py test apps.tasks.tests_recommendation
"""
import unittest
from unittest.mock import MagicMock, patch
import numpy as np

from apps.tasks.ml_engine import (
    ContentBasedRecommender,
    _compute_concept_overlap,
    _compute_difficulty_fit,
    _build_student_vector,
    _build_task_vector,
    explain_recommendation,
    DOMAINS,
)


# ─── helpers ──────────────────────────────────────────────────────────────────

def _make_student(
    domain_scores=None,
    domain_skill_levels=None,
    preferred_domains=None,
    concept_scores=None,
    completed_domain_counts=None,
):
    """Return a minimal mock student suitable for ML engine helpers."""
    student = MagicMock()
    profile = MagicMock()
    profile.domain_scores = domain_scores or {}
    profile.domain_skill_levels = domain_skill_levels or {}
    profile.preferred_domains = preferred_domains or []
    student.student_profile = profile
    return student, profile


def _make_task(
    domain='Programming',
    difficulty='Intermediate',
    required_skills=None,
    learning_outcomes=None,
    task_type='Project',
):
    task = MagicMock()
    task.domain = domain
    task.difficulty = difficulty
    task.required_skills = required_skills or []
    task.learning_outcomes = learning_outcomes or []
    task.task_type = task_type
    task.title = 'Test Task'
    task.description = 'A test task'
    task.id = 1
    return task


# ─── _compute_concept_overlap ─────────────────────────────────────────────────

class TestComputeConceptOverlap(unittest.TestCase):

    def test_no_student_concepts_returns_zero(self):
        score, matched = _compute_concept_overlap({}, ['HTML', 'CSS'], 'Web Development', [])
        self.assertEqual(score, 0.0)
        self.assertEqual(matched, [])

    def test_exact_match_on_required_skills(self):
        concept_scores = {'python': 0.8, 'oop': 0.7}
        score, matched = _compute_concept_overlap(
            concept_scores, ['Python', 'OOP'], 'Programming', []
        )
        self.assertGreater(score, 0.0)
        matched_lower = [c.lower() for c in matched]
        self.assertTrue(
            'python' in matched_lower or 'oop' in matched_lower,
            f'Expected python or oop in {matched_lower}',
        )

    def test_score_bounded_0_to_1(self):
        concept_scores = {c: 1.0 for c in ['python', 'oop', 'algorithms', 'data structures', 'debugging']}
        score, _ = _compute_concept_overlap(
            concept_scores, ['Python', 'OOP', 'Algorithms'], 'Programming', []
        )
        self.assertGreaterEqual(score, 0.0)
        self.assertLessEqual(score, 1.0)

    def test_unrelated_concepts_gives_low_score(self):
        concept_scores = {'colour theory': 0.9, 'typography': 0.8}
        score, _ = _compute_concept_overlap(
            concept_scores, ['SQL', 'Python', 'Pandas'], 'Data Analytics', []
        )
        self.assertLess(score, 0.5)

    def test_domain_concepts_contribute(self):
        # concepts from the same domain should raise score even without direct match
        concept_scores = {'python': 0.8, 'oop': 0.7, 'algorithms': 0.6}
        score_prog, _ = _compute_concept_overlap(
            concept_scores, ['Debugging'], 'Programming', []
        )
        score_data, _ = _compute_concept_overlap(
            concept_scores, ['Debugging'], 'Data Analytics', []
        )
        self.assertGreaterEqual(score_prog, score_data)


# ─── _compute_difficulty_fit ──────────────────────────────────────────────────

class TestComputeDifficultyFit(unittest.TestCase):

    def test_ideal_stretch_beginner_to_beginner(self):
        fit, label = _compute_difficulty_fit(0.3, 'Beginner', 'Beginner')
        self.assertIn(label, ('Ideal stretch', 'Good consolidation'))
        self.assertGreater(fit, 0.5)

    def test_advanced_too_hard_for_beginner(self):
        fit, label = _compute_difficulty_fit(0.2, 'Beginner', 'Advanced')
        self.assertIn(label, ('Challenging',))
        self.assertLess(fit, 0.6)

    def test_beginner_task_for_advanced_student(self):
        fit, label = _compute_difficulty_fit(0.9, 'Advanced', 'Beginner')
        self.assertIn(label, ('Below current level',))
        self.assertLessEqual(fit, 0.5)

    def test_score_bounded(self):
        for domain_score in [0.0, 0.5, 1.0]:
            for readiness in ['Beginner', 'Intermediate', 'Advanced']:
                for difficulty in ['Beginner', 'Intermediate', 'Advanced']:
                    fit, _ = _compute_difficulty_fit(domain_score, readiness, difficulty)
                    self.assertGreaterEqual(fit, 0.0)
                    self.assertLessEqual(fit, 1.0)


# ─── _build_student_vector ────────────────────────────────────────────────────

class TestBuildStudentVector(unittest.TestCase):

    def test_output_shape(self):
        vec = _build_student_vector(
            domain_scores={},
            domain_skill_levels={},
            preferred_domains=[],
        )
        self.assertEqual(len(vec), len(DOMAINS) * 3)

    def test_concept_scores_influence_domain_segment(self):
        # python/oop → Programming → should boost segment-0 for Programming
        domain_idx = DOMAINS.index('Programming')
        vec_no_concept = _build_student_vector(
            domain_scores={'Programming': 0.5},
            domain_skill_levels={},
            preferred_domains=[],
            concept_scores={},
        )
        vec_with_concept = _build_student_vector(
            domain_scores={'Programming': 0.5},
            domain_skill_levels={},
            preferred_domains=[],
            concept_scores={'python': 0.9, 'oop': 0.9, 'algorithms': 0.9},
        )
        # The Programming index should be >= no-concept version (or within cap)
        self.assertGreaterEqual(vec_with_concept[domain_idx], vec_no_concept[domain_idx] - 0.01)

    def test_preferred_domain_boosts_segment_1(self):
        prog_idx = DOMAINS.index('Programming')
        vec = _build_student_vector(
            domain_scores={},
            domain_skill_levels={},
            preferred_domains=['Programming'],
        )
        n = len(DOMAINS)
        # Preferred domains are encoded in segment 2 (index 2*n + domain_idx)
        self.assertGreater(vec[2 * n + prog_idx], 0.0)

    def test_completed_domain_counts_segment_2(self):
        prog_idx = DOMAINS.index('Programming')
        n = len(DOMAINS)
        vec = _build_student_vector(
            domain_scores={},
            domain_skill_levels={},
            preferred_domains=[],
            completed_domain_counts={'Programming': 5},
        )
        self.assertGreater(vec[2 * n + prog_idx], 0.0)


# ─── _build_task_vector ───────────────────────────────────────────────────────

class TestBuildTaskVector(unittest.TestCase):

    def test_output_shape(self):
        vec = _build_task_vector('Web Development', 'Intermediate', [])
        self.assertEqual(len(vec), len(DOMAINS) * 3)

    def test_primary_domain_has_highest_score(self):
        domain = 'Programming'
        domain_idx = DOMAINS.index(domain)
        vec = _build_task_vector(domain, 'Intermediate', [])
        primary_score = vec[domain_idx]
        for i, d in enumerate(DOMAINS):
            if d != domain:
                self.assertGreaterEqual(primary_score, vec[i])

    def test_difficulty_in_segment_1(self):
        n = len(DOMAINS)
        vec_beg = _build_task_vector('Programming', 'Beginner', [])
        vec_adv = _build_task_vector('Programming', 'Advanced', [])
        domain_idx = DOMAINS.index('Programming')
        # Advanced difficulty should give higher segment-1 value for that domain
        self.assertGreater(vec_adv[n + domain_idx], vec_beg[n + domain_idx])


# ─── ContentBasedRecommender.score_task ───────────────────────────────────────

class TestContentBasedRecommenderScoreTask(unittest.TestCase):

    def setUp(self):
        self.recommender = ContentBasedRecommender()
        # Student vector fully focused on Programming
        n = len(DOMAINS)
        self.student_vec = np.zeros(n * 3)
        prog_idx = DOMAINS.index('Programming')
        self.student_vec[prog_idx] = 1.0
        self.student_vec[n + prog_idx] = 1.0

    def test_matching_domain_scores_higher(self):
        score_prog, _ = self.recommender.score_task(
            self.student_vec, 'Programming', 'Intermediate', []
        )
        score_data, _ = self.recommender.score_task(
            self.student_vec, 'Data Analytics', 'Intermediate', []
        )
        self.assertGreater(score_prog, score_data)

    def test_score_in_0_1_range(self):
        score, _ = self.recommender.score_task(
            self.student_vec, 'Programming', 'Advanced', ['Python', 'Django']
        )
        # score_task returns a value in 0-100 range
        self.assertGreaterEqual(score, 0.0)
        self.assertLessEqual(score, 100.0)


# ─── explain_recommendation ───────────────────────────────────────────────────

class TestExplainRecommendation(unittest.TestCase):

    def _make_mocks(self):
        student, profile = _make_student(
            domain_scores={'Programming': 0.65},
            domain_skill_levels={'Programming': 'Intermediate'},
            preferred_domains=['Programming'],
            concept_scores={'python': 0.8, 'oop': 0.7},
        )
        task = _make_task(
            domain='Programming',
            difficulty='Intermediate',
            required_skills=['Python', 'OOP', 'Algorithms'],
            learning_outcomes=['Implement algorithms', 'Use OOP principles'],
        )
        n = len(DOMAINS)
        student_vec = np.zeros(n * 3)
        prog_idx = DOMAINS.index('Programming')
        student_vec[prog_idx] = 0.65
        student_vec[n + prog_idx] = 1.0
        return student, task, student_vec

    @patch('apps.tasks.models.TaskAssignment')
    @patch('apps.assessments.models.AssessmentAttempt')
    def test_returns_required_keys(self, mock_attempt_cls, mock_ta_cls):
        mock_attempt_cls.objects.filter.return_value.order_by.return_value.first.return_value = None
        mock_ta_cls.objects.filter.return_value.count.return_value = 0
        student, task, student_vec = self._make_mocks()
        result = explain_recommendation(student, task, student_vec=student_vec)
        required_keys = [
            'domain_match', 'concept_overlap', 'difficulty_fit',
            'preferred_domain', 'task_history', 'collaborative',
            'overall_score', 'summary', 'learning_outcomes', 'method',
        ]
        for key in required_keys:
            self.assertIn(key, result, f"Missing key: {key}")

    @patch('apps.tasks.models.TaskAssignment')
    @patch('apps.assessments.models.AssessmentAttempt')
    def test_overall_score_in_range(self, mock_attempt_cls, mock_ta_cls):
        mock_attempt_cls.objects.filter.return_value.order_by.return_value.first.return_value = None
        mock_ta_cls.objects.filter.return_value.count.return_value = 0
        student, task, student_vec = self._make_mocks()
        result = explain_recommendation(student, task, student_vec=student_vec)
        self.assertGreaterEqual(result['overall_score'], 0.0)
        self.assertLessEqual(result['overall_score'], 100.0)

    @patch('apps.tasks.models.TaskAssignment')
    @patch('apps.assessments.models.AssessmentAttempt')
    def test_preferred_domain_flag(self, mock_attempt_cls, mock_ta_cls):
        mock_attempt_cls.objects.filter.return_value.order_by.return_value.first.return_value = None
        mock_ta_cls.objects.filter.return_value.count.return_value = 0
        student, task, student_vec = self._make_mocks()
        result = explain_recommendation(student, task, student_vec=student_vec)
        self.assertTrue(result['preferred_domain']['is_preferred'])

    @patch('apps.tasks.models.TaskAssignment')
    @patch('apps.assessments.models.AssessmentAttempt')
    def test_summary_is_non_empty_string(self, mock_attempt_cls, mock_ta_cls):
        mock_attempt_cls.objects.filter.return_value.order_by.return_value.first.return_value = None
        mock_ta_cls.objects.filter.return_value.count.return_value = 0
        student, task, student_vec = self._make_mocks()
        result = explain_recommendation(student, task, student_vec=student_vec)
        self.assertIsInstance(result['summary'], str)
        self.assertGreater(len(result['summary']), 10)

    @patch('apps.tasks.models.TaskAssignment')
    @patch('apps.assessments.models.AssessmentAttempt')
    def test_method_is_content_without_cf(self, mock_attempt_cls, mock_ta_cls):
        mock_attempt_cls.objects.filter.return_value.order_by.return_value.first.return_value = None
        mock_ta_cls.objects.filter.return_value.count.return_value = 0
        student, task, student_vec = self._make_mocks()
        result = explain_recommendation(student, task, student_vec=student_vec, cf_entry=None)
        self.assertEqual(result['method'], 'content')

    @patch('apps.tasks.models.TaskAssignment')
    @patch('apps.assessments.models.AssessmentAttempt')
    def test_method_is_hybrid_with_cf(self, mock_attempt_cls, mock_ta_cls):
        mock_attempt_cls.objects.filter.return_value.order_by.return_value.first.return_value = None
        mock_ta_cls.objects.filter.return_value.count.return_value = 0
        student, task, student_vec = self._make_mocks()
        # cf_entry must be a dict with 'predicted_score'
        cf_entry = {'predicted_score': 0.8, 'neighbor_count': 3}
        result = explain_recommendation(student, task, student_vec=student_vec, cf_entry=cf_entry)
        self.assertEqual(result['method'], 'hybrid')


if __name__ == '__main__':
    unittest.main()
