"""
ML Engine for AI-Supported Virtual Internship Hub.

Provides four real ML/NLP capabilities:
1. ContentBasedRecommender   — cosine similarity on student + task feature vectors
2. CollaborativeRecommender  — user-based KNN on student-task MCQ score matrix
3. StudentClusterer          — KMeans clustering on domain performance vectors
4. DomainPredictor           — softmax-normalized scoring with recency decay

All computation is local; no external API calls.
Dependencies: numpy, scikit-learn (both in requirements.txt).
"""

import logging
import math
from typing import Dict, List, Optional, Tuple

import numpy as np

logger = logging.getLogger(__name__)

# ─────────────────────────────────────────────
# Constants
# ─────────────────────────────────────────────

DOMAINS = [
    'Graphic Design',
    'Content Writing',
    'Programming',
    'Freelancing',
    'E-Commerce',
    'QuickBooks',
    'AutoCAD',
    'Data Analytics',
    'Digital Marketing',
    'WordPress',
]
DOMAIN_INDEX: Dict[str, int] = {d: i for i, d in enumerate(DOMAINS)}
N_DOMAINS = len(DOMAINS)

DIFFICULTIES = ['Beginner', 'Intermediate', 'Advanced']
DIFFICULTY_INDEX = {d: i for i, d in enumerate(DIFFICULTIES)}

SKILL_LEVEL_SCORE = {'Beginner': 0.33, 'Intermediate': 0.66, 'Advanced': 1.0}

# KMeans cluster count — 4 learner archetypes
N_CLUSTERS = 4
CLUSTER_LABELS = {0: 'Explorer', 1: 'Developing', 2: 'Competent', 3: 'Expert'}

# Recency decay factor per attempt (most recent = 1.0, each older = × 0.85)
RECENCY_DECAY = 0.85


# ─────────────────────────────────────────────
# Vector builders
# ─────────────────────────────────────────────

def _build_student_vector(
    domain_scores: Dict[str, float],
    domain_skill_levels: Dict[str, str],
    preferred_domains: List[str],
    concept_scores: Optional[Dict[str, float]] = None,
    completed_domain_counts: Optional[Dict[str, int]] = None,
) -> np.ndarray:
    """
    Build a 30-dimensional student feature vector.

    Layout:
      [0:10]   normalised domain score (0-1) per DOMAINS order,
               boosted slightly by concept mastery in that domain
      [10:20]  skill level encoding (0, 0.33, 0.66, 1.0) per DOMAINS order
      [20:30]  preferred domain one-hot, boosted by task completion history

    Args:
        domain_scores: {domain: percentage_0_to_100}
        domain_skill_levels: {domain: 'Beginner'|'Intermediate'|'Advanced'}
        preferred_domains: list of domain strings
        concept_scores: optional {concept: weighted_score_0_to_100} from evaluation engine
        completed_domain_counts: optional {domain: n_completed_tasks} from task history

    Returns:
        numpy array of shape (30,)
    """
    vec = np.zeros(N_DOMAINS * 3, dtype=float)

    # ── Segment 0: domain scores ──────────────────────────────────────────
    for domain, score in domain_scores.items():
        idx = DOMAIN_INDEX.get(domain)
        if idx is not None:
            vec[idx] = float(score) / 100.0  # normalise

    # Blend in concept mastery: concept names are mapped to domains via keyword
    # matching; strong concepts lift the domain score slightly.
    if concept_scores:
        concept_domain_boost: Dict[int, float] = {}
        for concept, cscore in concept_scores.items():
            domain_for_concept = _infer_skill_domain(concept)
            if domain_for_concept is not None:
                didx = DOMAIN_INDEX.get(domain_for_concept)
                if didx is not None:
                    # Average concept boost (cap at 0.1 additional)
                    if didx not in concept_domain_boost:
                        concept_domain_boost[didx] = []
                    concept_domain_boost[didx].append(float(cscore) / 100.0)
        for didx, boosts in concept_domain_boost.items():
            boost = min(0.10, sum(boosts) / len(boosts) * 0.15)
            vec[didx] = min(1.0, vec[didx] + boost)

    # ── Segment 1: skill level ────────────────────────────────────────────
    for domain, level in domain_skill_levels.items():
        idx = DOMAIN_INDEX.get(domain)
        if idx is not None:
            vec[N_DOMAINS + idx] = SKILL_LEVEL_SCORE.get(level, 0.0)

    # ── Segment 2: preferred / experienced domains ────────────────────────
    for domain in preferred_domains:
        idx = DOMAIN_INDEX.get(domain)
        if idx is not None:
            vec[N_DOMAINS * 2 + idx] = 1.0

    # Task-completion history adds a softer signal (log-scaled, capped at 0.5)
    if completed_domain_counts:
        for domain, count in completed_domain_counts.items():
            idx = DOMAIN_INDEX.get(domain)
            if idx is not None:
                history_signal = min(0.5, math.log1p(count) / math.log1p(10))
                vec[N_DOMAINS * 2 + idx] = max(vec[N_DOMAINS * 2 + idx], history_signal)

    return vec


def _build_task_vector(
    task_domain: str,
    task_difficulty: str,
    required_skills: List[str],
    learning_outcomes: Optional[List[str]] = None,
    task_type: Optional[str] = None,
) -> np.ndarray:
    """
    Build a 30-dimensional task feature vector in the same space as student vectors.

    Layout:
      [0:10]   domain score signal — 1.0 for task domain; learning_outcomes add
               fractional votes to neighbouring domains
      [10:20]  difficulty signal mapped to skill level encoding for task domain;
               task_type adds cross-domain skill affinity
      [20:30]  required skills + learning outcome text vote for domain preference

    Args:
        task_domain: one of DOMAINS
        task_difficulty: 'Beginner' | 'Intermediate' | 'Advanced'
        required_skills: list of skill keyword strings
        learning_outcomes: optional list of outcome strings
        task_type: optional task type string

    Returns:
        numpy array of shape (30,)
    """
    vec = np.zeros(N_DOMAINS * 3, dtype=float)

    # ── Segment 0: primary domain signal ─────────────────────────────────
    domain_idx = DOMAIN_INDEX.get(task_domain)
    if domain_idx is not None:
        vec[domain_idx] = 1.0

    # Learning outcomes add fractional signals to related domains
    if learning_outcomes:
        for outcome in learning_outcomes:
            matched = _infer_skill_domain(outcome)
            if matched is not None:
                midx = DOMAIN_INDEX.get(matched)
                if midx is not None and midx != domain_idx:
                    vec[midx] += 0.2 / len(learning_outcomes)

    # ── Segment 1: difficulty + task_type signals ─────────────────────────
    diff_idx = DOMAIN_INDEX.get(task_domain)
    if diff_idx is not None:
        vec[N_DOMAINS + diff_idx] = SKILL_LEVEL_SCORE.get(task_difficulty, 0.33)

    # Task type adds domain-affinity in the skill plane
    _TASK_TYPE_DOMAIN_HINTS: Dict[str, List[str]] = {
        'Design':      ['Graphic Design'],
        'Development': ['Programming'],
        'Content':     ['Content Writing'],
        'Analysis':    ['Data Analytics'],
        'Marketing':   ['Digital Marketing'],
        'Research':    ['Content Writing', 'Data Analytics'],
    }
    if task_type:
        for hint_domain in _TASK_TYPE_DOMAIN_HINTS.get(task_type, []):
            hidx = DOMAIN_INDEX.get(hint_domain)
            if hidx is not None:
                vec[N_DOMAINS + hidx] = max(
                    vec[N_DOMAINS + hidx],
                    SKILL_LEVEL_SCORE.get(task_difficulty, 0.33) * 0.5,
                )

    # ── Segment 2: required skills + outcome keyword votes ────────────────
    all_signal_texts = list(required_skills or [])
    if learning_outcomes:
        all_signal_texts.extend(learning_outcomes)

    if all_signal_texts:
        for text in all_signal_texts:
            matched_domain = _infer_skill_domain(text)
            if matched_domain is not None:
                skill_domain_idx = DOMAIN_INDEX.get(matched_domain)
                if skill_domain_idx is not None:
                    vec[N_DOMAINS * 2 + skill_domain_idx] += 1.0 / len(all_signal_texts)

    return vec


# Keyword → domain mapping for skill inference
_SKILL_DOMAIN_KEYWORDS: Dict[str, List[str]] = {
    'Programming': ['python', 'javascript', 'html', 'css', 'react', 'django', 'flask',
                    'node', 'sql', 'api', 'code', 'programming', 'development', 'web',
                    'backend', 'frontend', 'fullstack', 'software', 'algorithm'],
    'Graphic Design': ['photoshop', 'illustrator', 'figma', 'canva', 'design', 'ui', 'ux',
                       'logo', 'branding', 'typography', 'colour', 'color', 'visual', 'banner',
                       'illustration', 'adobe', 'sketch', 'mockup'],
    'Content Writing': ['writing', 'blog', 'seo', 'copywriting', 'content', 'article',
                        'proofreading', 'editing', 'grammar', 'research', 'wordpress', 'medium'],
    'Data Analytics': ['excel', 'tableau', 'powerbi', 'sql', 'data', 'analytics', 'statistics',
                       'visualization', 'pandas', 'python', 'reporting', 'dashboard', 'bi'],
    'Digital Marketing': ['marketing', 'seo', 'sem', 'facebook', 'instagram', 'ads', 'ppc',
                          'social media', 'email', 'campaign', 'google ads', 'analytics'],
    'E-Commerce': ['shopify', 'amazon', 'ebay', 'ecommerce', 'product', 'listing', 'fba',
                   'dropshipping', 'store', 'woocommerce', 'payment', 'inventory'],
    'Freelancing': ['upwork', 'fiverr', 'proposal', 'client', 'bid', 'freelance', 'contract',
                    'communication', 'pricing', 'project management'],
    'WordPress': ['wordpress', 'elementor', 'plugin', 'theme', 'woocommerce', 'php', 'cms'],
    'QuickBooks': ['quickbooks', 'accounting', 'bookkeeping', 'invoice', 'payroll', 'ledger'],
    'AutoCAD': ['autocad', 'cad', 'drafting', '3d', 'modeling', 'technical drawing', 'blueprint'],
}


def _infer_skill_domain(skill: str) -> Optional[str]:
    """Map a skill keyword string to its closest domain using keyword matching."""
    skill_lower = skill.lower()
    best_domain = None
    best_count = 0
    for domain, keywords in _SKILL_DOMAIN_KEYWORDS.items():
        count = sum(1 for kw in keywords if kw in skill_lower)
        if count > best_count:
            best_count = count
            best_domain = domain
    return best_domain


# ─────────────────────────────────────────────
# Concept overlap scoring
# ─────────────────────────────────────────────

# Map concept tags (from evaluation_engine) to their primary domain
_CONCEPT_DOMAIN_MAP: Dict[str, str] = {
    # Graphic Design concepts
    'colour theory': 'Graphic Design', 'color theory': 'Graphic Design',
    'typography': 'Graphic Design', 'composition': 'Graphic Design',
    'design principles': 'Graphic Design', 'visual hierarchy': 'Graphic Design',
    'file formats': 'Graphic Design', 'UX principles': 'Graphic Design',
    'UI design': 'Graphic Design', 'accessibility': 'Graphic Design',
    'user research': 'Graphic Design',
    # Programming concepts
    'data types': 'Programming', 'functions': 'Programming', 'loops': 'Programming',
    'data structures': 'Programming', 'syntax': 'Programming', 'strings': 'Programming',
    'recursion': 'Programming', 'algorithms': 'Programming',
    'HTML': 'Programming', 'CSS': 'Programming', 'JavaScript': 'Programming',
    # Digital Marketing concepts
    'SEO': 'Digital Marketing', 'social media': 'Digital Marketing',
    'audience targeting': 'Digital Marketing', 'conversion': 'Digital Marketing',
    'platform strategy': 'Digital Marketing', 'advertising metrics': 'Digital Marketing',
    'analytics': 'Digital Marketing',
    # Content Writing concepts
    'copywriting': 'Content Writing', 'content strategy': 'Content Writing',
    # Data Analytics concepts
    'databases': 'Data Analytics', 'SQL': 'Data Analytics',
    'data visualization': 'Data Analytics', 'business intelligence': 'Data Analytics',
    'statistics': 'Data Analytics',
}


def _compute_concept_overlap(
    student_concept_scores: Dict[str, float],
    task_required_skills: List[str],
    task_domain: str,
    task_learning_outcomes: Optional[List[str]] = None,
) -> Tuple[float, List[str]]:
    """
    Compute how much the student's concept mastery overlaps with what the task requires.

    Returns:
        (overlap_score_0_to_1, list_of_matched_concept_names)
    """
    if not student_concept_scores:
        return 0.0, []

    # Gather all task-related concept signals from skill names + outcomes
    task_signals = list(task_required_skills or [])
    if task_learning_outcomes:
        task_signals.extend(task_learning_outcomes)
    task_signals.append(task_domain)

    # Find which student concepts map to this task's domain
    task_domain_concepts = [
        concept for concept, domain in _CONCEPT_DOMAIN_MAP.items()
        if domain == task_domain
    ]

    # Also match concepts whose name appears in skill/outcome text
    matched = []
    for concept in student_concept_scores:
        concept_lower = concept.lower()
        in_task_domain = concept in task_domain_concepts
        in_signals = any(concept_lower in sig.lower() for sig in task_signals)
        if in_task_domain or in_signals:
            matched.append(concept)

    if not matched:
        return 0.0, []

    # Score = average weighted_score of matched concepts, normalised 0-1
    avg_score = sum(student_concept_scores[c] for c in matched) / (len(matched) * 100.0)
    return min(1.0, avg_score), sorted(matched)


def _compute_difficulty_fit(
    student_domain_score: float,
    student_readiness: str,
    task_difficulty: str,
) -> Tuple[float, str]:
    """
    Score how appropriate the task difficulty is for the student.

    Prefers tasks that are slightly above the student's current level (stretch zone).
    Returns:
        (fit_score_0_to_1, label)
    """
    _READINESS_SCORE = {
        'Novice': 0.1, 'Developing': 0.3, 'Competent': 0.55,
        'Proficient': 0.75, 'Expert': 0.95, '': 0.0,
    }
    _DIFF_SCORE = {'Beginner': 0.2, 'Intermediate': 0.5, 'Advanced': 0.9}

    student_level = max(
        _READINESS_SCORE.get(student_readiness, 0.0),
        student_domain_score,
    )
    task_level = _DIFF_SCORE.get(task_difficulty, 0.5)
    gap = task_level - student_level

    # Optimal stretch: task is 0.1–0.3 above student level
    if 0.0 <= gap <= 0.3:
        score = 1.0 - gap / 0.3 * 0.2   # 0.8–1.0
        label = 'Ideal stretch'
    elif -0.1 <= gap < 0.0:
        score = 0.85                      # slightly easy — consolidation
        label = 'Good consolidation'
    elif gap > 0.3:
        score = max(0.3, 1.0 - gap)      # too hard
        label = 'Challenging'
    else:
        score = 0.5                       # too easy
        label = 'Below current level'

    return round(score, 3), label


def _cosine_similarity(a: np.ndarray, b: np.ndarray) -> float:
    """Compute cosine similarity between two vectors, returning 0 if either is zero."""
    norm_a = np.linalg.norm(a)
    norm_b = np.linalg.norm(b)
    if norm_a == 0 or norm_b == 0:
        return 0.0
    return float(np.dot(a, b) / (norm_a * norm_b))


# ─────────────────────────────────────────────
# 1. Content-Based Recommender
# ─────────────────────────────────────────────

class ContentBasedRecommender:
    """
    Recommends tasks to a student using cosine similarity between
    student feature vectors and task feature vectors.
    """

    @staticmethod
    def score_task(
        student_vec: np.ndarray,
        task_domain: str,
        task_difficulty: str,
        required_skills: List[str],
        learning_outcomes: Optional[List[str]] = None,
        task_type: Optional[str] = None,
    ) -> Tuple[float, str]:
        """
        Score a single task against a student vector.

        Returns:
            (similarity_score_0_to_100, explanation_string)
        """
        task_vec = _build_task_vector(
            task_domain, task_difficulty, required_skills,
            learning_outcomes=learning_outcomes, task_type=task_type,
        )
        similarity = _cosine_similarity(student_vec, task_vec)

        # Add a difficulty-appropriateness bonus:
        # Tasks slightly above the student's average skill level are preferred
        domain_idx = DOMAIN_INDEX.get(task_domain)
        student_domain_score = student_vec[domain_idx] if domain_idx is not None else 0.0
        task_diff_val = DIFFICULTY_INDEX.get(task_difficulty, 0) / 2.0  # 0, 0.5, 1.0

        # Stretch bonus: prefer tasks just above current level (up to +0.1)
        stretch = max(0.0, task_diff_val - student_domain_score)
        stretch_bonus = 0.1 * max(0.0, 1.0 - stretch * 3)  # bonus peaks at small gap

        total = min(1.0, similarity + stretch_bonus)

        explanation = (
            f"Content match {similarity * 100:.0f}% "
            f"(domain={task_domain}, difficulty={task_difficulty})"
        )
        return round(total * 100, 2), explanation

    @staticmethod
    def build_student_vector_from_db(student) -> np.ndarray:
        """
        Build a student feature vector directly from database objects,
        incorporating assessment domain scores, concept mastery, and task history.

        Args:
            student: User instance with related assessment_attempts and student_profile

        Returns:
            numpy array (30,)
        """
        from apps.assessments.models import AssessmentAttempt
        from apps.tasks.models import TaskAssignment

        attempts = AssessmentAttempt.objects.filter(
            student=student
        ).select_related('assessment').order_by('attempted_at')

        # Collect latest score + concept info per domain (most recent attempt wins)
        domain_scores: Dict[str, float] = {}
        domain_skill_levels: Dict[str, str] = {}
        merged_concept_scores: Dict[str, float] = {}   # concept → weighted_score

        for attempt in attempts:
            domain = attempt.assessment.domain
            domain_scores[domain] = attempt.percentage
            domain_skill_levels[domain] = attempt.skill_level
            # Merge concept_scores from the attempt (latest per concept wins)
            if attempt.concept_scores:
                for concept, cdata in attempt.concept_scores.items():
                    score = cdata.get('weighted_score', cdata.get('score_pct', 0.0))
                    merged_concept_scores[concept] = float(score)

        # Task completion history → domain counts
        completed_domain_counts: Dict[str, int] = {}
        try:
            for assignment in TaskAssignment.objects.filter(
                student=student, status='completed'
            ).select_related('task'):
                d = assignment.task.domain
                completed_domain_counts[d] = completed_domain_counts.get(d, 0) + 1
        except Exception:
            pass

        # Get preferred domains from student profile
        preferred_domains: List[str] = []
        try:
            preferred_domains = student.student_profile.preferred_domains or []
        except Exception:
            pass

        return _build_student_vector(
            domain_scores,
            domain_skill_levels,
            preferred_domains,
            concept_scores=merged_concept_scores or None,
            completed_domain_counts=completed_domain_counts or None,
        )


# ─────────────────────────────────────────────
# 2. Collaborative Filtering Recommender
# ─────────────────────────────────────────────

class CollaborativeRecommender:
    """
    User-based collaborative filtering.

    Delegates to apps.tasks.collaborative_filtering which builds a rich
    student × task interaction matrix from multiple behavioural signals:
      - Task assignment status (accepted / in_progress / completed)
      - MCQ quiz score (blended in when available)
      - Mentor review outcome (approved / needs_revision)
      - Domain engagement frequency

    The public interface is unchanged so callers in recommendation_service.py
    are not affected.
    """

    @staticmethod
    def get_recommendations(
        target_student,
        available_task_ids: List[int],
        already_assigned_ids: List[int],
        limit: int = 10,
    ) -> List[Dict]:
        """
        Generate collaborative recommendations for target_student.

        Returns:
            List of dicts:
            [{task_id, predicted_score, neighbor_count, reason, cf_debug}]
        """
        from apps.tasks.collaborative_filtering import get_collaborative_recommendations

        # Filter out already-assigned tasks before passing to CF
        filtered_ids = [
            tid for tid in available_task_ids
            if tid not in already_assigned_ids
        ]
        return get_collaborative_recommendations(
            target_student=target_student,
            available_task_ids=filtered_ids,
            limit=limit,
        )


# ─────────────────────────────────────────────
# 3. Student Clusterer
# ─────────────────────────────────────────────

# Per-cluster display adjectives and role nouns
_CLUSTER_ADJECTIVES: Dict[int, str] = {
    0: 'Aspiring',
    1: 'Developing',
    2: 'Skilled',
    3: 'Expert',
}
_CLUSTER_SKILL_LEVEL: Dict[int, str] = {
    0: 'Beginner',
    1: 'Intermediate',
    2: 'Intermediate',
    3: 'Advanced',
}
_DOMAIN_ROLE: Dict[str, str] = {
    'Graphic Design':    'Designer',
    'Content Writing':   'Writer',
    'Programming':       'Developer',
    'Freelancing':       'Freelancer',
    'E-Commerce':        'E-Commerce Specialist',
    'QuickBooks':        'Accountant',
    'AutoCAD':           'CAD Specialist',
    'Data Analytics':    'Data Analyst',
    'Digital Marketing': 'Marketer',
    'WordPress':         'WordPress Specialist',
}
_CLUSTER_GENERIC_NAME: Dict[int, str] = {
    0: 'Early Explorer',
    1: 'Balanced Learner',
    2: 'Well-Rounded Practitioner',
    3: 'High Achiever',
}


def _cluster_display_name(cluster_id: int, dominant_domain: Optional[str]) -> str:
    """Return a human-readable cluster name for a student."""
    if not dominant_domain:
        return _CLUSTER_GENERIC_NAME.get(cluster_id, 'Learner')
    role = _DOMAIN_ROLE.get(dominant_domain, dominant_domain + ' Practitioner')
    adj  = _CLUSTER_ADJECTIVES.get(cluster_id, 'Developing')
    return f"{adj} {role}"


def _build_cluster_summary(cluster_id: int, cluster_label: str, raw_data: Dict) -> Dict:
    """Build a rich per-student cluster summary dict for storage."""
    domain_scores: Dict[str, float] = raw_data.get('domain_scores', {})
    dominant_domain: Optional[str] = (
        max(domain_scores.items(), key=lambda kv: kv[1])[0]
        if domain_scores else None
    )
    display_name   = _cluster_display_name(cluster_id, dominant_domain)
    avg            = raw_data.get('avg_assessment_score', 0.0)
    completion_rate = raw_data.get('completion_rate', 0.0)
    trend_raw      = raw_data.get('improvement_trend', 0.0)

    if trend_raw > 0.1:
        trend_label = 'improving'
    elif trend_raw < -0.1:
        trend_label = 'declining'
    else:
        trend_label = 'stable'

    if cluster_id == 0:
        description = (
            f"You're beginning your learning journey"
            f"{f' in {dominant_domain}' if dominant_domain else ''}. "
            "Each assessment brings you closer to your goals."
        )
    elif cluster_id == 1:
        description = (
            f"You're making solid progress"
            f"{f' in {dominant_domain}' if dominant_domain else ''}. "
            "Keep practising to reach the Competent level."
        )
    elif cluster_id == 2:
        description = (
            f"Strong performance"
            f"{f' in {dominant_domain}' if dominant_domain else ''}! "
            "You're ready for advanced tasks. Push for Expert status."
        )
    else:
        description = (
            f"Outstanding results"
            f"{f' in {dominant_domain}' if dominant_domain else ''}! "
            "You're among the top performers. Consider mentoring others."
        )

    strengths    = [d for d, s in domain_scores.items() if s >= 60]
    focus_areas  = [d for d, s in domain_scores.items() if s < 40]

    return {
        'display_name':         display_name,
        'description':          description,
        'dominant_domain':      dominant_domain,
        'skill_level':          _CLUSTER_SKILL_LEVEL.get(cluster_id, 'Intermediate'),
        'avg_assessment_score': round(avg, 1),
        'completion_rate':      round(completion_rate, 2),
        'improvement_trend':    trend_label,
        'strengths':            strengths[:3],
        'focus_areas':          focus_areas[:2],
    }


class StudentClusterer:
    """
    Clusters students into skill archetypes using KMeans on a 23-dim feature
    vector that captures domain MCQ scores, task engagement, completion rate,
    improvement trend, and average task MCQ score.

    Clusters: 4 — Explorer, Developing, Competent, Expert.
    """

    # Number of features used for clustering
    N_CLUSTER_FEATURES = 23

    @staticmethod
    def _build_cluster_feature_vector(student) -> Tuple[np.ndarray, Dict]:
        """
        Build a 23-dim feature vector for a student and return supplementary data.

        Layout:
          [0:10]  domain MCQ assessment scores (0-1, latest per domain)
          [10:20] per-domain task engagement (log-scaled 0-1)
          [20]    overall task completion rate
          [21]    improvement trend (normalised slope of recent scores)
          [22]    average task MCQ score (0-1)

        Returns:
            (feature_vector np.ndarray shape (23,), raw_data dict)
        """
        from apps.assessments.models import AssessmentAttempt
        from apps.tasks.models import TaskAssignment

        feat = np.zeros(StudentClusterer.N_CLUSTER_FEATURES)

        # ── Domain assessment scores (dim 0–9) ───────────────────────────
        attempts = list(
            AssessmentAttempt.objects.filter(student=student)
            .select_related('assessment')
            .order_by('attempted_at')
        )
        domain_scores: Dict[str, float] = {}
        for attempt in attempts:
            domain = attempt.assessment.domain
            domain_scores[domain] = attempt.percentage  # latest wins

        for domain, score in domain_scores.items():
            idx = DOMAIN_INDEX.get(domain)
            if idx is not None:
                feat[idx] = score / 100.0

        # ── Per-domain task engagement (dim 10–19) ───────────────────────
        all_assignments = list(
            TaskAssignment.objects.filter(
                student=student,
                status__in=['accepted', 'in_progress', 'completed'],
            ).select_related('task')
        )
        domain_task_counts: Dict[str, int] = {}
        completed_count = 0
        total_count = len(all_assignments)
        for ta in all_assignments:
            d = ta.task.domain
            domain_task_counts[d] = domain_task_counts.get(d, 0) + 1
            if ta.status == 'completed':
                completed_count += 1

        for domain, count in domain_task_counts.items():
            idx = DOMAIN_INDEX.get(domain)
            if idx is not None:
                # log-scale: 1→0.43, 3→0.60, 10→1.0
                feat[N_DOMAINS + idx] = min(1.0, math.log1p(count) / math.log1p(10))

        # ── Summary stats (dim 20–22) ────────────────────────────────────
        feat[20] = completed_count / max(1, total_count)  # completion rate

        # Improvement trend: normalised linear slope of last 5 assessment scores
        if len(attempts) >= 2:
            recent = np.array([a.percentage for a in attempts[-5:]], dtype=float)
            x = np.arange(len(recent), dtype=float)
            x -= x.mean()
            y = recent - recent.mean()
            denom = float(np.dot(x, x))
            slope = float(np.dot(x, y) / denom) if denom > 0 else 0.0
            feat[21] = float(np.clip(slope / 30.0, -1.0, 1.0))

        # Average task MCQ score
        try:
            from apps.tasks.models import TaskCompletion, TaskMCQAttempt
            completion_ids = list(
                TaskCompletion.objects.filter(
                    task_assignment__student=student,
                    is_submitted=True,
                ).values_list('id', flat=True)
            )
            if completion_ids:
                mcq_attempts = list(
                    TaskMCQAttempt.objects.filter(
                        task_completion_id__in=completion_ids,
                        is_submitted=True,
                    )
                )
                if mcq_attempts:
                    feat[22] = sum(float(a.mcq_score or 0) for a in mcq_attempts) / (
                        len(mcq_attempts) * 100.0
                    )
        except Exception:
            pass

        raw_data = {
            'domain_scores':       domain_scores,
            'completion_rate':     float(feat[20]),
            'improvement_trend':   float(feat[21]),
            'avg_mcq_score':       float(feat[22]) * 100.0,
            'avg_assessment_score': (
                sum(domain_scores.values()) / len(domain_scores)
                if domain_scores else 0.0
            ),
        }
        return feat, raw_data

    @staticmethod
    def compute_cluster(student) -> Tuple[int, str]:
        """
        Compute the cluster assignment for a single student.

        Returns:
            (cluster_id: int, cluster_label: str)
        """
        feat, raw_data = StudentClusterer._build_cluster_feature_vector(student)

        if not raw_data['domain_scores']:
            return 0, CLUSTER_LABELS[0]  # Explorer — no data yet

        domain_vec   = feat[:N_DOMAINS]
        active       = domain_vec[domain_vec > 0]
        avg_score    = float(np.mean(active)) if len(active) > 0 else 0.0
        completion   = float(feat[20])
        trend        = float(feat[21])

        # Composite: weighted blend of MCQ score, completion rate, improvement
        composite = 0.6 * avg_score + 0.3 * completion + 0.1 * max(0.0, trend)

        if not np.any(domain_vec > 0) or composite < 0.27:
            cluster_id = 0
        elif composite < 0.49:
            cluster_id = 1
        elif composite < 0.67:
            cluster_id = 2
        else:
            cluster_id = 3

        return cluster_id, CLUSTER_LABELS[cluster_id]

    @staticmethod
    def compute_cluster_sklearn(all_students) -> Dict[int, Tuple[int, str]]:
        """
        Batch-compute clusters for all students using sklearn KMeans on
        a 23-dim feature vector. Falls back to rule-based if sklearn is
        unavailable or there are fewer students than N_CLUSTERS.

        Args:
            all_students: queryset or list of User objects with role='Student'

        Returns:
            {student_id: (cluster_id, cluster_label)}
        """
        try:
            from sklearn.cluster import KMeans
            from sklearn.preprocessing import StandardScaler
        except ImportError:
            logger.warning("scikit-learn not installed; falling back to rule-based clustering")
            return {s.id: StudentClusterer.compute_cluster(s) for s in all_students}

        student_list = list(all_students)
        if len(student_list) < N_CLUSTERS:
            return {s.id: StudentClusterer.compute_cluster(s) for s in student_list}

        matrix = []
        ids    = []
        for student in student_list:
            feat, _ = StudentClusterer._build_cluster_feature_vector(student)
            matrix.append(feat)
            ids.append(student.id)

        X = np.array(matrix)
        scaler   = StandardScaler()
        X_scaled = scaler.fit_transform(X)

        kmeans     = KMeans(n_clusters=N_CLUSTERS, random_state=42, n_init=10)
        raw_labels = kmeans.fit_predict(X_scaled)

        # Re-order cluster IDs so that 0=Explorer … 3=Expert
        # (sort by centroid mean across all 23 features)
        centroid_means = [
            float(np.mean(kmeans.cluster_centers_[c]))
            for c in range(N_CLUSTERS)
        ]
        ordered = sorted(range(N_CLUSTERS), key=lambda c: centroid_means[c])
        remap   = {old: new for new, old in enumerate(ordered)}

        result: Dict[int, Tuple[int, str]] = {}
        for student_id, raw_label in zip(ids, raw_labels):
            new_label = remap[int(raw_label)]
            result[student_id] = (new_label, CLUSTER_LABELS[new_label])

        return result

    @staticmethod
    def update_student_cluster(student) -> str:
        """
        Compute and persist cluster + cluster_summary for a single student.

        Returns:
            cluster label string
        """
        feat, raw_data = StudentClusterer._build_cluster_feature_vector(student)
        cluster_id, label = StudentClusterer.compute_cluster(student)
        summary = _build_cluster_summary(cluster_id, label, raw_data)

        try:
            from apps.accounts.models import StudentProfile
            profile, _ = StudentProfile.objects.get_or_create(user=student)
            profile.cluster_id      = cluster_id
            profile.cluster_label   = label
            profile.cluster_summary = summary
            profile.save(update_fields=['cluster_id', 'cluster_label', 'cluster_summary'])
        except Exception as e:
            logger.warning(f"Could not persist cluster for student {student.id}: {e}")
        return label


# ─────────────────────────────────────────────
# 4. Domain Predictor
# ─────────────────────────────────────────────

class DomainPredictor:
    """
    Predicts the best freelancing domain(s) for a student by combining:
    - Assessment performance per domain (with recency decay)
    - Student profile preferences
    - Cluster-level domain affinity

    Output: ranked list with confidence scores (sums to 1.0).
    """

    @staticmethod
    def predict(student) -> List[Dict]:
        """
        Return a ranked list of domains with confidence scores.

        Returns:
            [
              {
                'domain': str,
                'confidence': float,   # 0-1
                'score_basis': float,  # avg weighted MCQ score
                'reasoning': str,
              },
              ...
            ]
        """
        from apps.assessments.models import AssessmentAttempt

        attempts = list(
            AssessmentAttempt.objects.filter(student=student)
            .select_related('assessment')
            .order_by('attempted_at')
        )

        if not attempts:
            return []

        # ── Recency-weighted score per domain ──────────────────────────────
        domain_weighted: Dict[str, float] = {}
        domain_count: Dict[str, int] = {}

        n = len(attempts)
        for i, attempt in enumerate(attempts):
            domain = attempt.assessment.domain
            # Most recent attempt has weight 1.0; older decay by RECENCY_DECAY
            age = n - 1 - i
            weight = RECENCY_DECAY ** age
            score = attempt.percentage / 100.0 * weight

            domain_weighted[domain] = domain_weighted.get(domain, 0.0) + score
            domain_count[domain] = domain_count.get(domain, 0) + 1

        # Normalise by effective weight sum per domain
        raw_scores: Dict[str, float] = {}
        for domain in domain_weighted:
            count = domain_count[domain]
            # Effective weight sum for `count` attempts with decay
            eff_weight = sum(RECENCY_DECAY ** i for i in range(count))
            raw_scores[domain] = domain_weighted[domain] / eff_weight if eff_weight > 0 else 0.0

        # ── Preference bonus ──────────────────────────────────────────────
        preferred: List[str] = []
        try:
            preferred = student.student_profile.preferred_domains or []
        except Exception:
            pass

        for domain in preferred:
            if domain in raw_scores:
                raw_scores[domain] = min(1.0, raw_scores[domain] + 0.05)
            else:
                raw_scores[domain] = 0.05  # slight signal even without attempt

        if not raw_scores:
            return []

        # ── Softmax normalisation ─────────────────────────────────────────
        domains_list = list(raw_scores.keys())
        scores_array = np.array([raw_scores[d] for d in domains_list], dtype=float)

        # Softmax with temperature scaling (T=0.5 makes differences sharper)
        T = 0.5
        exp_scores = np.exp(scores_array / T)
        softmax_scores = exp_scores / exp_scores.sum()

        # ── Build result ──────────────────────────────────────────────────
        results = []
        for domain, confidence, raw in zip(domains_list, softmax_scores, scores_array):
            skill_level = _score_to_skill_level(raw)
            results.append({
                'domain': domain,
                'confidence': round(float(confidence), 4),
                'score_basis': round(float(raw) * 100, 1),
                'skill_level': skill_level,
                'reasoning': _domain_reasoning(domain, raw, skill_level),
            })

        results.sort(key=lambda x: x['confidence'], reverse=True)
        return results


def _score_to_skill_level(normalised_score: float) -> str:
    if normalised_score >= 0.8:
        return 'Advanced'
    elif normalised_score >= 0.5:
        return 'Intermediate'
    return 'Beginner'


def _domain_reasoning(domain: str, raw_score: float, skill_level: str) -> str:
    pct = round(raw_score * 100, 0)
    if skill_level == 'Advanced':
        return (
            f"Strong {domain} performance ({pct:.0f}% weighted average). "
            "Ready for freelancing in this domain."
        )
    elif skill_level == 'Intermediate':
        return (
            f"Solid {domain} foundation ({pct:.0f}% weighted average). "
            "A few more improvements and you'll be ready to freelance."
        )
    return (
        f"Early-stage {domain} knowledge ({pct:.0f}% weighted average). "
        "Focus on strengthening fundamentals before taking client work."
    )


# ─────────────────────────────────────────────
# 5. Structured explanation builder
# ─────────────────────────────────────────────

def explain_recommendation(
    student,
    task,
    student_vec: Optional[np.ndarray] = None,
    cf_entry: Optional[Dict] = None,
) -> Dict:
    """
    Build a structured, human-readable explanation of why a task is recommended.

    Returns a dict with per-component scores and a plain-text summary:
    {
      'domain_match':       {'score': 0-100, 'label': str, 'detail': str},
      'concept_overlap':    {'score': 0-100, 'matched_concepts': [...], 'detail': str},
      'difficulty_fit':     {'score': 0-100, 'label': str, 'detail': str},
      'preferred_domain':   {'score': 0-100, 'is_preferred': bool},
      'task_history':       {'score': 0-100, 'completed_in_domain': int},
      'collaborative':      {'score': 0-100, 'neighbor_count': int, 'detail': str},
      'overall_score':      float,
      'summary':            str,
      'learning_outcomes':  [...],
      'method':             'hybrid' | 'content',
    }
    """
    from apps.assessments.models import AssessmentAttempt
    from apps.tasks.models import TaskAssignment

    if student_vec is None:
        student_vec = ContentBasedRecommender.build_student_vector_from_db(student)

    domain_idx = DOMAIN_INDEX.get(task.domain)
    student_domain_score = float(student_vec[domain_idx]) if domain_idx is not None else 0.0

    # ── 1. Domain match ────────────────────────────────────────────────────
    domain_match_raw = student_domain_score  # 0-1
    if domain_match_raw >= 0.8:
        dm_label = 'Excellent'
    elif domain_match_raw >= 0.6:
        dm_label = 'Good'
    elif domain_match_raw >= 0.4:
        dm_label = 'Moderate'
    elif domain_match_raw > 0:
        dm_label = 'Basic'
    else:
        dm_label = 'No history'
    dm_detail = (
        f"You've scored {student_domain_score * 100:.0f}% on {task.domain} assessments."
        if student_domain_score > 0
        else f"No {task.domain} assessment yet — good domain to explore."
    )

    # ── 2. Concept overlap ─────────────────────────────────────────────────
    merged_concepts: Dict[str, float] = {}
    latest_readiness: str = ''
    try:
        for attempt in AssessmentAttempt.objects.filter(
            student=student
        ).select_related('assessment').order_by('attempted_at'):
            if attempt.concept_scores:
                for c, cdata in attempt.concept_scores.items():
                    score = cdata.get('weighted_score', cdata.get('score_pct', 0.0))
                    merged_concepts[c] = float(score)
            if attempt.assessment.domain == task.domain and attempt.readiness_level:
                latest_readiness = attempt.readiness_level
    except Exception:
        pass

    concept_score, matched_concepts = _compute_concept_overlap(
        merged_concepts,
        task.required_skills or [],
        task.domain,
        task.learning_outcomes or [],
    )
    if matched_concepts:
        co_detail = f"Your strong concepts: {', '.join(matched_concepts[:4])}."
    else:
        co_detail = f"No direct concept overlap found — this task will build new concepts."

    # ── 3. Difficulty fit ──────────────────────────────────────────────────
    diff_fit_score, diff_fit_label = _compute_difficulty_fit(
        student_domain_score,
        latest_readiness,
        task.difficulty,
    )
    diff_detail = (
        f"{task.difficulty} task — {diff_fit_label.lower()} "
        f"for your current {task.domain} level."
    )

    # ── 4. Preferred domain ────────────────────────────────────────────────
    preferred_domains: List[str] = []
    try:
        preferred_domains = student.student_profile.preferred_domains or []
    except Exception:
        pass
    is_preferred = task.domain in preferred_domains
    pref_score = 100.0 if is_preferred else 0.0

    # ── 5. Task history ────────────────────────────────────────────────────
    completed_in_domain = 0
    try:
        completed_in_domain = TaskAssignment.objects.filter(
            student=student, task__domain=task.domain, status='completed'
        ).count()
    except Exception:
        pass
    history_score = min(100.0, completed_in_domain * 20.0)  # 5 completions = 100%

    # ── 6. Collaborative signal ────────────────────────────────────────────
    cf_score_val = 0.0
    cf_neighbor_count = 0
    cf_detail = 'No collaborative data yet.'
    cf_debug = None
    if cf_entry and cf_entry.get('predicted_score') is not None:
        cf_score_val = float(cf_entry['predicted_score'])
        cf_neighbor_count = cf_entry.get('neighbor_count', 0)
        cf_debug = cf_entry.get('cf_debug')
        cf_detail = (
            f"{cf_neighbor_count} similar student(s) scored "
            f"{cf_score_val:.0f}% on this task."
        )

    # ── Weighted overall score ─────────────────────────────────────────────
    # Content component (cosine similarity with stretch bonus)
    task_vec = _build_task_vector(
        task.domain, task.difficulty, task.required_skills or [],
        learning_outcomes=task.learning_outcomes or [],
        task_type=getattr(task, 'task_type', None),
    )
    cb_sim = _cosine_similarity(student_vec, task_vec) * 100.0
    diff_val = DIFFICULTY_INDEX.get(task.difficulty, 0) / 2.0
    stretch = max(0.0, diff_val - student_domain_score)
    stretch_bonus = 0.1 * max(0.0, 1.0 - stretch * 3)
    cb_score = min(100.0, cb_sim + stretch_bonus * 100.0)

    if cf_entry and cf_entry.get('predicted_score') is not None:
        overall = 0.60 * cb_score + 0.40 * cf_score_val
        method = 'hybrid'
    else:
        overall = cb_score
        method = 'content'

    # ── Plain-text summary ─────────────────────────────────────────────────
    summary_parts = []
    if overall >= 85:
        summary_parts.append('Excellent match for your profile.')
    elif overall >= 70:
        summary_parts.append('Strong recommendation based on your skills.')
    elif overall >= 55:
        summary_parts.append('Good fit for your current level.')
    else:
        summary_parts.append('Recommended as a learning stretch.')

    if is_preferred:
        summary_parts.append(f'{task.domain} is in your preferred domains.')
    elif student_domain_score > 0:
        summary_parts.append(
            f'Your {student_domain_score * 100:.0f}% score in {task.domain} '
            f'makes you a good candidate for this {task.difficulty} task.'
        )
    else:
        summary_parts.append(
            f'This is a great opportunity to start building {task.domain} experience.'
        )

    if matched_concepts:
        summary_parts.append(f"Leverages your knowledge of: {', '.join(matched_concepts[:3])}.")

    if task.learning_outcomes:
        outcomes_preview = task.learning_outcomes[:2]
        summary_parts.append(f"You'll gain: {', '.join(outcomes_preview)}.")

    if cf_neighbor_count > 0:
        summary_parts.append(cf_detail)

    return {
        'domain_match': {
            'score': round(domain_match_raw * 100, 1),
            'label': dm_label,
            'detail': dm_detail,
        },
        'concept_overlap': {
            'score': round(concept_score * 100, 1),
            'matched_concepts': matched_concepts,
            'detail': co_detail,
        },
        'difficulty_fit': {
            'score': round(diff_fit_score * 100, 1),
            'label': diff_fit_label,
            'detail': diff_detail,
        },
        'preferred_domain': {
            'score': pref_score,
            'is_preferred': is_preferred,
        },
        'task_history': {
            'score': history_score,
            'completed_in_domain': completed_in_domain,
        },
        'collaborative': {
            'score': round(cf_score_val, 1),
            'neighbor_count': cf_neighbor_count,
            'detail': cf_detail,
            'debug': cf_debug,
        },
        'overall_score': round(min(overall, 100.0), 2),
        'summary': ' '.join(summary_parts),
        'learning_outcomes': task.learning_outcomes or [],
        'method': method,
    }


# ─────────────────────────────────────────────
# 6. Combined scoring (used by recommendation_service)
# ─────────────────────────────────────────────

def compute_hybrid_score(
    student,
    task,
    student_vec: Optional[np.ndarray] = None,
    cf_scores: Optional[Dict[int, Dict]] = None,
) -> Tuple[float, str]:
    """
    Compute a hybrid recommendation score combining content-based and
    collaborative scores.

    Weights: 60% content-based + 40% collaborative (or 100% content if no CF data).

    Returns:
        (final_score_0_to_100, explanation_string)
    """
    if student_vec is None:
        student_vec = ContentBasedRecommender.build_student_vector_from_db(student)

    # Content-based (now includes learning_outcomes + task_type)
    cb_score, cb_reason = ContentBasedRecommender.score_task(
        student_vec,
        task.domain,
        task.difficulty,
        task.required_skills or [],
        learning_outcomes=task.learning_outcomes or [],
        task_type=getattr(task, 'task_type', None),
    )

    # Collaborative
    cf_entry = (cf_scores or {}).get(task.id)
    if cf_entry and cf_entry.get('predicted_score') is not None:
        cf_score = float(cf_entry['predicted_score'])
        final = 0.60 * cb_score + 0.40 * cf_score
        explanation = f"Content: {cb_score:.0f}% | Collaborative: {cf_score:.0f}%"
    else:
        final = cb_score
        explanation = cb_reason

    return round(min(final, 100.0), 2), explanation
