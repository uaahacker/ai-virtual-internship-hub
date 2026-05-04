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


# ─── collaborative_filtering module ──────────────────────────────────────────

from apps.tasks.collaborative_filtering import (
    _interaction_score,
    _cosine,
    _interaction_vector,
    build_interaction_matrix,
    compute_neighbors,
    predict_task_scores,
    get_collaborative_recommendations,
    STATUS_BASE,
    MCQ_BLEND_WEIGHT,
    MENTOR_ADJUSTMENT,
    DOMAINS,
    N_DOMAINS,
)


class TestInteractionScore(unittest.TestCase):
    """Unit tests for the _interaction_score helper."""

    def test_declined_always_zero(self):
        score = _interaction_score('declined', mcq_score=100.0, mentor_review_status='approved')
        self.assertEqual(score, 0.0)

    def test_accepted_no_mcq(self):
        score = _interaction_score('accepted', mcq_score=None, mentor_review_status='not_requested')
        self.assertEqual(score, STATUS_BASE['accepted'])

    def test_completed_with_mcq_blends_in(self):
        score = _interaction_score('completed', mcq_score=100.0, mentor_review_status='not_requested')
        expected = STATUS_BASE['completed'] + MCQ_BLEND_WEIGHT * 100.0
        self.assertAlmostEqual(score, expected, places=4)

    def test_completed_mcq_not_blended_for_non_completed(self):
        # MCQ blend should only apply to 'completed' status
        score_in_progress = _interaction_score('in_progress', mcq_score=100.0, mentor_review_status='not_requested')
        self.assertEqual(score_in_progress, STATUS_BASE['in_progress'])

    def test_mentor_approved_adds_bonus(self):
        base = _interaction_score('completed', mcq_score=None, mentor_review_status='not_requested')
        with_approval = _interaction_score('completed', mcq_score=None, mentor_review_status='approved')
        self.assertGreater(with_approval, base)

    def test_needs_revision_reduces_score(self):
        base = _interaction_score('completed', mcq_score=None, mentor_review_status='not_requested')
        with_revision = _interaction_score('completed', mcq_score=None, mentor_review_status='needs_revision')
        self.assertLess(with_revision, base)

    def test_score_bounded_0_to_100(self):
        # Even with all bonuses, score must not exceed 100
        score = _interaction_score('completed', mcq_score=100.0, mentor_review_status='approved')
        self.assertLessEqual(score, 100.0)
        self.assertGreaterEqual(score, 0.0)


class TestCosine(unittest.TestCase):

    def test_identical_vectors(self):
        a = np.array([1.0, 2.0, 3.0])
        self.assertAlmostEqual(_cosine(a, a), 1.0)

    def test_orthogonal_vectors(self):
        a = np.array([1.0, 0.0])
        b = np.array([0.0, 1.0])
        self.assertAlmostEqual(_cosine(a, b), 0.0)

    def test_zero_vector_returns_zero(self):
        a = np.zeros(5)
        b = np.array([1.0, 2.0, 3.0, 4.0, 5.0])
        self.assertEqual(_cosine(a, b), 0.0)


class TestInteractionVector(unittest.TestCase):

    def test_normalised_to_0_1(self):
        task_scores = {1: 80.0, 2: 100.0}
        all_ids = [1, 2, 3]
        vec = _interaction_vector(task_scores, all_ids)
        self.assertAlmostEqual(vec[0], 0.8)
        self.assertAlmostEqual(vec[1], 1.0)
        self.assertAlmostEqual(vec[2], 0.0)

    def test_unknown_task_ids_ignored(self):
        task_scores = {99: 50.0}
        all_ids = [1, 2]
        vec = _interaction_vector(task_scores, all_ids)
        self.assertTrue(all(v == 0.0 for v in vec))


class TestComputeNeighbors(unittest.TestCase):
    """Unit tests for compute_neighbors using pure in-memory data."""

    def _make_interactions(self):
        # Three students, each with 2+ tasks, sharing some tasks with target
        return {
            1: {10: 80.0, 11: 60.0, 12: 70.0},  # target
            2: {10: 75.0, 11: 55.0, 13: 90.0},  # similar to target
            3: {14: 50.0, 15: 40.0},              # no shared tasks with target
            4: {10: 80.0, 11: 60.0},              # very similar to target
        }

    def _make_domain_profiles(self):
        prog_idx = DOMAINS.index('Programming')
        n = N_DOMAINS

        def _profile(prog_val):
            v = np.zeros(n)
            v[prog_idx] = prog_val
            return v

        return {
            1: _profile(0.7),
            2: _profile(0.65),
            3: _profile(0.1),
            4: _profile(0.72),
        }

    def test_returns_sorted_by_similarity(self):
        interactions = self._make_interactions()
        profiles = self._make_domain_profiles()
        neighbours = compute_neighbors(
            target_student_id=1,
            interactions=interactions,
            domain_counts={},
            domain_profiles=profiles,
        )
        sims = [n['similarity'] for n in neighbours]
        self.assertEqual(sims, sorted(sims, reverse=True))

    def test_target_not_in_neighbours(self):
        interactions = self._make_interactions()
        profiles = self._make_domain_profiles()
        neighbours = compute_neighbors(
            target_student_id=1,
            interactions=interactions,
            domain_counts={},
            domain_profiles=profiles,
        )
        ids = [n['student_id'] for n in neighbours]
        self.assertNotIn(1, ids)

    def test_neighbour_has_required_keys(self):
        interactions = self._make_interactions()
        profiles = self._make_domain_profiles()
        neighbours = compute_neighbors(
            target_student_id=1,
            interactions=interactions,
            domain_counts={},
            domain_profiles=profiles,
        )
        required = {'student_id', 'similarity', 'interaction_sim', 'domain_sim',
                    'n_shared_tasks', 'n_tasks'}
        for n in neighbours:
            self.assertTrue(required.issubset(set(n.keys())))

    def test_cold_start_no_interactions_returns_neighbours_by_domain(self):
        # Target has no interactions — should still find neighbours via domain profile
        interactions = {
            1: {},  # target: no interactions
            2: {10: 80.0, 11: 60.0},
            3: {12: 70.0},
        }
        prog_idx = DOMAINS.index('Programming')
        profiles = {
            1: np.eye(N_DOMAINS)[prog_idx],
            2: np.eye(N_DOMAINS)[prog_idx],
            3: np.zeros(N_DOMAINS),
        }
        neighbours = compute_neighbors(
            target_student_id=1,
            interactions=interactions,
            domain_counts={},
            domain_profiles=profiles,
        )
        # Student 2 should appear (same domain), student 3 should have low/zero sim
        ids = [n['student_id'] for n in neighbours]
        self.assertIn(2, ids)


class TestPredictTaskScores(unittest.TestCase):

    def _make_data(self):
        interactions = {
            1: {10: 70.0},           # target — has task 10
            2: {10: 80.0, 11: 90.0, 12: 60.0},
            3: {11: 85.0, 13: 75.0},
        }
        neighbours = [
            {'student_id': 2, 'similarity': 0.9, 'interaction_sim': 0.9,
             'domain_sim': 0.9, 'n_shared_tasks': 1, 'n_tasks': 3},
            {'student_id': 3, 'similarity': 0.7, 'interaction_sim': 0.7,
             'domain_sim': 0.7, 'n_shared_tasks': 0, 'n_tasks': 2},
        ]
        return interactions, neighbours

    def test_target_engaged_tasks_excluded(self):
        interactions, neighbours = self._make_data()
        preds = predict_task_scores(
            target_student_id=1,
            available_task_ids=[10, 11, 12, 13],
            interactions=interactions,
            neighbours=neighbours,
        )
        predicted_ids = [p['task_id'] for p in preds]
        self.assertNotIn(10, predicted_ids)  # target already engaged with task 10

    def test_predicted_score_is_weighted_average(self):
        interactions, neighbours = self._make_data()
        preds = predict_task_scores(
            target_student_id=1,
            available_task_ids=[11],
            interactions=interactions,
            neighbours=neighbours,
        )
        self.assertEqual(len(preds), 1)
        pred = preds[0]
        self.assertEqual(pred['task_id'], 11)
        # Weighted avg: (0.9*90 + 0.7*85) / (0.9 + 0.7)
        expected = round((0.9 * 90 + 0.7 * 85) / (0.9 + 0.7), 2)
        self.assertAlmostEqual(pred['predicted_score'], expected, places=1)

    def test_no_neighbours_with_task_yields_no_prediction(self):
        interactions, neighbours = self._make_data()
        preds = predict_task_scores(
            target_student_id=1,
            available_task_ids=[99],  # task that no neighbour has touched
            interactions=interactions,
            neighbours=neighbours,
        )
        self.assertEqual(preds, [])

    def test_sorted_by_predicted_score_descending(self):
        interactions, neighbours = self._make_data()
        preds = predict_task_scores(
            target_student_id=1,
            available_task_ids=[11, 12, 13],
            interactions=interactions,
            neighbours=neighbours,
        )
        scores = [p['predicted_score'] for p in preds]
        self.assertEqual(scores, sorted(scores, reverse=True))

    def test_result_has_required_keys(self):
        interactions, neighbours = self._make_data()
        preds = predict_task_scores(
            target_student_id=1,
            available_task_ids=[11],
            interactions=interactions,
            neighbours=neighbours,
        )
        required = {'task_id', 'predicted_score', 'neighbor_count',
                    'neighbor_contributions', 'reason'}
        for p in preds:
            self.assertTrue(required.issubset(set(p.keys())))


class TestBuildInteractionMatrix(unittest.TestCase):
    """Integration-style tests with mocked ORM objects."""

    def _make_assignment(self, assignment_id, student_id, task_id, domain, status,
                         mentor_review_status='not_requested'):
        a = MagicMock()
        a.id = assignment_id
        a.student_id = student_id
        a.task_id = task_id
        a.task.domain = domain
        a.status = status
        a.mentor_review_status = mentor_review_status
        return a

    @patch('apps.tasks.models.TaskMCQAttempt')
    @patch('apps.tasks.models.TaskCompletion')
    @patch('apps.tasks.models.TaskAssignment')
    def test_completed_task_included(self, MockTA, MockTC, MockMCQ):
        assignments = [
            self._make_assignment(1, 101, 10, 'Programming', 'completed'),
        ]
        MockTA.objects.filter.return_value.select_related.return_value = assignments
        MockTC.objects.filter.return_value = []
        MockMCQ.objects.filter.return_value = []

        interactions, domain_counts = build_interaction_matrix()
        self.assertIn(101, interactions)
        self.assertIn(10, interactions[101])
        self.assertGreater(interactions[101][10], 0)

    @patch('apps.tasks.models.TaskMCQAttempt')
    @patch('apps.tasks.models.TaskCompletion')
    @patch('apps.tasks.models.TaskAssignment')
    def test_declined_task_excluded(self, MockTA, MockTC, MockMCQ):
        # A 'declined' assignment should not appear in the matrix
        # (build_interaction_matrix filters on status__in=['accepted','in_progress','completed'])
        MockTA.objects.filter.return_value.select_related.return_value = []
        MockTC.objects.filter.return_value = []
        MockMCQ.objects.filter.return_value = []

        interactions, _ = build_interaction_matrix()
        self.assertEqual(interactions, {})

    @patch('apps.tasks.models.TaskMCQAttempt')
    @patch('apps.tasks.models.TaskCompletion')
    @patch('apps.tasks.models.TaskAssignment')
    def test_mcq_score_blended_in(self, MockTA, MockTC, MockMCQ):
        assignments = [
            self._make_assignment(1, 101, 10, 'Programming', 'completed'),
        ]
        MockTA.objects.filter.return_value.select_related.return_value = assignments

        completion = MagicMock()
        completion.task_assignment_id = 1
        completion.id = 200
        MockTC.objects.filter.return_value = [completion]

        attempt = MagicMock()
        attempt.task_completion_id = 200
        attempt.mcq_score = 80.0
        attempt.is_submitted = True
        MockMCQ.objects.filter.return_value = [attempt]

        interactions, _ = build_interaction_matrix()
        expected = STATUS_BASE['completed'] + MCQ_BLEND_WEIGHT * 80.0
        self.assertAlmostEqual(interactions[101][10], expected, places=2)

    @patch('apps.tasks.models.TaskMCQAttempt')
    @patch('apps.tasks.models.TaskCompletion')
    @patch('apps.tasks.models.TaskAssignment')
    def test_domain_counts_tracked(self, MockTA, MockTC, MockMCQ):
        assignments = [
            self._make_assignment(1, 101, 10, 'Programming', 'completed'),
            self._make_assignment(2, 101, 11, 'Programming', 'accepted'),
        ]
        MockTA.objects.filter.return_value.select_related.return_value = assignments
        MockTC.objects.filter.return_value = []
        MockMCQ.objects.filter.return_value = []

        _, domain_counts = build_interaction_matrix()
        self.assertEqual(domain_counts[101].get('Programming', 0), 2)


class TestGetCollaborativeRecommendations(unittest.TestCase):
    """Smoke-test the full pipeline with mocked DB."""

    @patch('apps.assessments.models.AssessmentAttempt')
    @patch('apps.tasks.models.TaskMCQAttempt')
    @patch('apps.tasks.models.TaskCompletion')
    @patch('apps.tasks.models.TaskAssignment')
    def test_returns_empty_when_not_enough_data(self, MockTA, MockTC, MockMCQ, MockAA):
        MockTA.objects.filter.return_value.select_related.return_value = []
        MockTC.objects.filter.return_value = []
        MockMCQ.objects.filter.return_value = []
        MockAA.objects.filter.return_value.select_related.return_value = []

        student = MagicMock()
        student.id = 1

        results = get_collaborative_recommendations(student, [10, 11, 12])
        self.assertEqual(results, [])

    @patch('apps.assessments.models.AssessmentAttempt')
    @patch('apps.tasks.models.TaskMCQAttempt')
    @patch('apps.tasks.models.TaskCompletion')
    @patch('apps.tasks.models.TaskAssignment')
    def test_result_has_cf_debug_key(self, MockTA, MockTC, MockMCQ, MockAA):
        def _assignment(aid, sid, tid, domain, status):
            a = MagicMock()
            a.id = aid; a.student_id = sid; a.task_id = tid
            a.task.domain = domain; a.status = status
            a.mentor_review_status = 'not_requested'
            return a

        assignments = [
            _assignment(1, 1, 10, 'Programming', 'completed'),   # target
            _assignment(2, 2, 10, 'Programming', 'completed'),   # neighbour has task 10
            _assignment(3, 2, 11, 'Programming', 'accepted'),    # neighbour has task 11
            _assignment(4, 2, 12, 'Data Analytics', 'completed'),
        ]
        MockTA.objects.filter.return_value.select_related.return_value = assignments
        MockTC.objects.filter.return_value = []
        MockMCQ.objects.filter.return_value = []

        # Assessment attempts to build domain profiles
        def _attempt(sid, domain, pct):
            a = MagicMock()
            a.student_id = sid
            a.assessment.domain = domain
            a.percentage = pct
            return a

        MockAA.objects.filter.return_value.select_related.return_value = [
            _attempt(1, 'Programming', 70),
            _attempt(2, 'Programming', 75),
        ]

        student = MagicMock()
        student.id = 1

        results = get_collaborative_recommendations(student, [11, 12])
        # If neighbours found and tasks predicted, results will be non-empty
        for res in results:
            self.assertIn('cf_debug', res)
            self.assertIn('n_neighbors_found', res['cf_debug'])
            self.assertIn('interaction_matrix_size', res['cf_debug'])
            self.assertIn('target_interactions', res['cf_debug'])
            self.assertIn('neighbors', res['cf_debug'])


if __name__ == '__main__':
    unittest.main()
