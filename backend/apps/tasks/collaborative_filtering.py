"""
Enhanced memory-based collaborative filtering for task recommendations.

Builds a rich student × task interaction matrix from multiple behavioural signals:
  - Task assignment status (accepted / in_progress / completed)
  - MCQ quiz score (blended in when available)
  - Mentor review outcome (approved / needs_revision)
  - Domain engagement frequency (repeated domain choices per student)

Student similarity is computed as a weighted blend of:
  - Interaction-vector cosine similarity (when students share >= 1 task)
  - Domain-profile cosine similarity (10-dim assessment score vector, always available)

All intermediate scores are attached to each result dict under the 'cf_debug' key
so they can be stored in TaskAssignment.recommendation_explanation for analytics.

Public API
----------
get_collaborative_recommendations(target_student, available_task_ids, limit=20)
    Full pipeline. Returns list of result dicts (see docstring below).

build_interaction_matrix(student_ids=None)
    Build the raw interaction matrix. Exposed for unit tests.

compute_neighbors(target_student_id, interactions, domain_counts, domain_profiles)
    Find K nearest neighbours. Exposed for unit tests.

predict_task_scores(target_student_id, available_task_ids, interactions, neighbors)
    Predict scores for unseen tasks. Exposed for unit tests.
"""

import logging
from typing import Dict, List, Optional, Tuple

import numpy as np

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Domain constants (must match apps/tasks/ml_engine.py)
# ---------------------------------------------------------------------------

DOMAINS: List[str] = [
    'Graphic Design', 'Content Writing', 'Programming', 'Freelancing',
    'E-Commerce', 'QuickBooks', 'AutoCAD', 'Data Analytics',
    'Digital Marketing', 'WordPress',
]
DOMAIN_INDEX: Dict[str, int] = {d: i for i, d in enumerate(DOMAINS)}
N_DOMAINS: int = len(DOMAINS)

# ---------------------------------------------------------------------------
# Interaction signal weights
# ---------------------------------------------------------------------------

# Base interaction score (0-100) derived from task assignment status.
# 'declined' produces 0 and is excluded from the matrix entirely.
STATUS_BASE: Dict[str, float] = {
    'recommended': 10.0,
    'accepted':    30.0,
    'in_progress': 50.0,
    'completed':   65.0,
    'declined':     0.0,
}

# When a completed task has a quiz score, blend it in:
#   interaction = status_base + MCQ_BLEND_WEIGHT * mcq_score  (capped at 100)
MCQ_BLEND_WEIGHT: float = 0.35

# Mentor review bonus / penalty applied on top of the blended score.
MENTOR_ADJUSTMENT: Dict[str, float] = {
    'approved':       +10.0,
    'requested':       +2.0,
    'needs_revision':  -8.0,
    'not_requested':    0.0,
}

# ---------------------------------------------------------------------------
# Similarity hyper-parameters
# ---------------------------------------------------------------------------

# Minimum tasks a neighbour must have interacted with to be considered.
MIN_NEIGHBOR_INTERACTIONS: int = 1

# Minimum shared tasks between two students to blend in interaction-cosine.
MIN_SHARED_TASKS: int = 1

# Maximum number of nearest neighbours to use.
K_NEIGHBORS: int = 7

# Weight split: interaction-cosine vs domain-profile-cosine.
INTERACTION_SIM_WEIGHT: float = 0.55
DOMAIN_SIM_WEIGHT: float = 0.45


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _interaction_score(
    status: str,
    mcq_score: Optional[float],
    mentor_review_status: str,
) -> float:
    """
    Compute a single interaction score (0-100) from behavioural signals.

    Higher means stronger positive engagement with the task.
    """
    if status == 'declined':
        return 0.0

    base: float = STATUS_BASE.get(status, 0.0)

    # MCQ blend: only for completed tasks that have a quiz score
    if mcq_score is not None and status == 'completed':
        blended = base + MCQ_BLEND_WEIGHT * float(mcq_score)
    else:
        blended = base

    adj: float = MENTOR_ADJUSTMENT.get(mentor_review_status or 'not_requested', 0.0)
    return float(np.clip(blended + adj, 0.0, 100.0))


def _cosine(a: np.ndarray, b: np.ndarray) -> float:
    """Cosine similarity, returns 0 when either vector is zero-norm."""
    na, nb = float(np.linalg.norm(a)), float(np.linalg.norm(b))
    if na == 0.0 or nb == 0.0:
        return 0.0
    return float(np.dot(a, b) / (na * nb))


def _interaction_vector(
    task_scores: Dict[int, float],
    all_task_ids: List[int],
) -> np.ndarray:
    """Build a dense interaction vector over the universe of known task IDs."""
    tid_to_idx: Dict[int, int] = {tid: i for i, tid in enumerate(all_task_ids)}
    vec = np.zeros(len(all_task_ids))
    for tid, score in task_scores.items():
        idx = tid_to_idx.get(tid)
        if idx is not None:
            vec[idx] = score / 100.0  # normalise to [0, 1]
    return vec


def _domain_profile_from_db(student_id: int) -> np.ndarray:
    """
    Build a 10-dim domain score vector from assessment attempts.
    Djongo-safe: single-collection query with select_related.
    """
    from apps.assessments.models import AssessmentAttempt  # avoid circular at module level

    vec = np.zeros(N_DOMAINS)
    try:
        for attempt in (
            AssessmentAttempt.objects
            .filter(student_id=student_id)
            .select_related('assessment')
        ):
            idx = DOMAIN_INDEX.get(attempt.assessment.domain)
            if idx is not None:
                vec[idx] = max(vec[idx], attempt.percentage / 100.0)
    except Exception as exc:
        logger.warning("CF: could not build domain profile for student %s: %s", student_id, exc)
    return vec


# ---------------------------------------------------------------------------
# Public builders
# ---------------------------------------------------------------------------

def build_interaction_matrix(
    student_ids: Optional[List[int]] = None,
) -> Tuple[Dict[int, Dict[int, float]], Dict[int, Dict[str, int]]]:
    """
    Build the student × task interaction matrix and per-student domain counts.

    Uses three Djongo-safe queries (single-collection each):
      1. TaskAssignment   — status + mentor_review_status
      2. TaskCompletion   — maps assignment → completion
      3. TaskMCQAttempt   — mcq_score per completion

    Args:
        student_ids: optional filter; when None all students are included.

    Returns:
        interactions  : {student_id: {task_id: interaction_score_0_to_100}}
        domain_counts : {student_id: {domain: number_of_engaged_tasks}}
    """
    from apps.tasks.models import TaskAssignment, TaskCompletion, TaskMCQAttempt

    # ── 1. Fetch relevant task assignments ────────────────────────────────
    qs = (
        TaskAssignment.objects
        .filter(status__in=['accepted', 'in_progress', 'completed'])
        .select_related('task')
    )
    if student_ids is not None:
        qs = qs.filter(student_id__in=student_ids)

    assignments: List = list(qs)
    if not assignments:
        return {}, {}

    assignment_by_id: Dict[int, object] = {a.id: a for a in assignments}
    assignment_ids: List[int] = list(assignment_by_id.keys())

    # ── 2. Map assignment → completion ────────────────────────────────────
    completion_by_assignment: Dict[int, int] = {}  # assignment_id → completion_id
    for completion in TaskCompletion.objects.filter(task_assignment_id__in=assignment_ids):
        completion_by_assignment[completion.task_assignment_id] = completion.id

    # ── 3. Fetch MCQ scores ───────────────────────────────────────────────
    completion_ids: List[int] = list(completion_by_assignment.values())
    mcq_by_completion: Dict[int, float] = {}
    if completion_ids:
        for attempt in TaskMCQAttempt.objects.filter(
            task_completion_id__in=completion_ids,
            is_submitted=True,
        ):
            # Keep highest score if somehow attempted more than once
            cid = attempt.task_completion_id
            existing = mcq_by_completion.get(cid, -1.0)
            if float(attempt.mcq_score or 0) > existing:
                mcq_by_completion[cid] = float(attempt.mcq_score or 0)

    # ── 4. Build matrices ─────────────────────────────────────────────────
    interactions: Dict[int, Dict[int, float]] = {}
    domain_counts: Dict[int, Dict[str, int]] = {}

    for assignment in assignments:
        sid: int = assignment.student_id
        tid: int = assignment.task_id
        domain: str = assignment.task.domain

        comp_id = completion_by_assignment.get(assignment.id)
        mcq_score = mcq_by_completion.get(comp_id) if comp_id else None

        score = _interaction_score(
            status=assignment.status,
            mcq_score=mcq_score,
            mentor_review_status=assignment.mentor_review_status or 'not_requested',
        )
        if score <= 0.0:
            continue

        if sid not in interactions:
            interactions[sid] = {}
            domain_counts[sid] = {}

        # Keep highest score if a student has multiple assignments for the same task
        if score > interactions[sid].get(tid, -1.0):
            interactions[sid][tid] = score

        domain_counts[sid][domain] = domain_counts[sid].get(domain, 0) + 1

    return interactions, domain_counts


def compute_neighbors(
    target_student_id: int,
    interactions: Dict[int, Dict[int, float]],
    domain_counts: Dict[int, Dict[str, int]],  # noqa: ARG001 — kept for future use
    domain_profiles: Optional[Dict[int, np.ndarray]] = None,
) -> List[Dict]:
    """
    Find the K most similar students to the target student.

    Similarity = blend of interaction-cosine (when shared tasks exist)
                 and domain-profile-cosine (always available).

    Returns:
        List of neighbour dicts sorted by similarity descending:
        [
          {
            'student_id':      int,
            'similarity':      float,    # final blended similarity
            'interaction_sim': float,    # cosine on interaction vectors
            'domain_sim':      float,    # cosine on 10-dim domain profile
            'n_shared_tasks':  int,
            'n_tasks':         int,
          }
        ]
    """
    target_tasks: Dict[int, float] = interactions.get(target_student_id, {})

    # Universe of all task IDs across all students (sorted for determinism)
    all_task_ids: List[int] = sorted(
        {tid for scores in interactions.values() for tid in scores}
    )
    if not all_task_ids:
        return []

    if domain_profiles is None:
        domain_profiles = {}

    target_int_vec: np.ndarray = _interaction_vector(target_tasks, all_task_ids)
    target_dom_vec: np.ndarray = domain_profiles.get(
        target_student_id,
        _domain_profile_from_db(target_student_id),
    )

    neighbours: List[Dict] = []

    for sid, task_scores in interactions.items():
        if sid == target_student_id:
            continue
        if len(task_scores) < MIN_NEIGHBOR_INTERACTIONS:
            continue

        shared = set(target_tasks) & set(task_scores)
        n_shared = len(shared)

        # Interaction-based cosine (only meaningful when tasks overlap)
        if n_shared >= MIN_SHARED_TASKS:
            neighbor_int_vec = _interaction_vector(task_scores, all_task_ids)
            int_sim = _cosine(target_int_vec, neighbor_int_vec)
        else:
            int_sim = 0.0

        # Domain-profile cosine (assessment-score based, always available)
        neighbor_dom_vec = domain_profiles.get(sid, _domain_profile_from_db(sid))
        dom_sim = _cosine(target_dom_vec, neighbor_dom_vec)

        # Combined similarity
        if n_shared >= MIN_SHARED_TASKS:
            sim = INTERACTION_SIM_WEIGHT * int_sim + DOMAIN_SIM_WEIGHT * dom_sim
        else:
            sim = dom_sim  # pure domain similarity as cold-start fallback

        if sim > 0.05:  # discard near-zero neighbours
            neighbours.append({
                'student_id':      sid,
                'similarity':      round(sim, 4),
                'interaction_sim': round(int_sim, 4),
                'domain_sim':      round(dom_sim, 4),
                'n_shared_tasks':  n_shared,
                'n_tasks':         len(task_scores),
            })

    neighbours.sort(key=lambda x: x['similarity'], reverse=True)
    return neighbours[:K_NEIGHBORS]


def predict_task_scores(
    target_student_id: int,
    available_task_ids: List[int],
    interactions: Dict[int, Dict[int, float]],
    neighbours: List[Dict],
) -> List[Dict]:
    """
    Predict interaction scores for tasks the target student has not engaged with.

    Uses similarity-weighted average of neighbour interaction scores.

    Returns:
        List sorted by predicted_score descending:
        [
          {
            'task_id':                int,
            'predicted_score':        float,   # 0-100
            'neighbor_count':         int,
            'neighbor_contributions': [...],   # debug: per-neighbour scores
            'reason':                 str,
          }
        ]
    """
    target_engaged: set = set(interactions.get(target_student_id, {}).keys())
    predictions: List[Dict] = []

    for task_id in available_task_ids:
        if task_id in target_engaged:
            continue  # target already has an interaction signal for this task

        weighted_sum = 0.0
        weight_total = 0.0
        contributions: List[Dict] = []

        for neighbour in neighbours:
            sid = neighbour['student_id']
            score = interactions.get(sid, {}).get(task_id)
            if score is None:
                continue
            sim = neighbour['similarity']
            weighted_sum += sim * score
            weight_total += sim
            contributions.append({
                'student_id': sid,
                'similarity': neighbour['similarity'],
                'score':      score,
            })

        if weight_total == 0.0:
            continue

        predicted = round(weighted_sum / weight_total, 2)
        n = len(contributions)
        predictions.append({
            'task_id':                task_id,
            'predicted_score':        predicted,
            'neighbor_count':         n,
            'neighbor_contributions': contributions,
            'reason': (
                f'{n} similar student(s) scored {predicted:.0f}% on this task '
                f'(similarity-weighted average)'
            ),
        })

    predictions.sort(key=lambda x: x['predicted_score'], reverse=True)
    return predictions


# ---------------------------------------------------------------------------
# Main entry point
# ---------------------------------------------------------------------------

def get_collaborative_recommendations(
    target_student,
    available_task_ids: List[int],
    limit: int = 20,
) -> List[Dict]:
    """
    Full collaborative filtering pipeline.

    Args:
        target_student    : Django User instance (Student role)
        available_task_ids: task IDs the student has NOT yet been assigned
        limit             : maximum results to return

    Returns:
        List of dicts (at most `limit` items), sorted by predicted_score descending:
        [
          {
            'task_id':         int,
            'predicted_score': float,   # 0-100
            'neighbor_count':  int,
            'reason':          str,
            'cf_debug': {
              'n_neighbors_found':       int,
              'interaction_matrix_size': int,
              'target_interactions':     int,
              'neighbors': [            # per-neighbour debug (no student_id exposed)
                {'similarity', 'interaction_sim', 'domain_sim',
                 'n_shared_tasks', 'n_tasks'}
              ],
              'neighbor_contributions': [{'similarity', 'score'}, ...],
            },
          }
        ]
    """
    target_id: int = target_student.id

    # ── Build interaction matrix (all students) ───────────────────────────
    interactions, domain_counts = build_interaction_matrix()

    if len(interactions) < 2:
        logger.debug("CF: not enough interaction data (found %d students)", len(interactions))
        return []

    # ── Batch-fetch domain profiles for all relevant students ─────────────
    # (One DB query over multiple students is much cheaper than per-student calls)
    all_student_ids: List[int] = list(interactions.keys())
    if target_id not in all_student_ids:
        all_student_ids.append(target_id)

    from apps.assessments.models import AssessmentAttempt

    domain_profiles: Dict[int, np.ndarray] = {}
    try:
        for attempt in (
            AssessmentAttempt.objects
            .filter(student_id__in=all_student_ids)
            .select_related('assessment')
        ):
            sid = attempt.student_id
            if sid not in domain_profiles:
                domain_profiles[sid] = np.zeros(N_DOMAINS)
            idx = DOMAIN_INDEX.get(attempt.assessment.domain)
            if idx is not None:
                domain_profiles[sid][idx] = max(
                    domain_profiles[sid][idx],
                    attempt.percentage / 100.0,
                )
    except Exception as exc:
        logger.warning("CF: could not batch-fetch domain profiles: %s", exc)

    # ── Find nearest neighbours ───────────────────────────────────────────
    neighbours = compute_neighbors(
        target_student_id=target_id,
        interactions=interactions,
        domain_counts=domain_counts,
        domain_profiles=domain_profiles,
    )

    if not neighbours:
        logger.debug("CF: no neighbours found for student %s", target_id)
        return []

    # ── Predict scores for available tasks ────────────────────────────────
    predictions = predict_task_scores(
        target_student_id=target_id,
        available_task_ids=available_task_ids,
        interactions=interactions,
        neighbours=neighbours,
    )

    # ── Attach debug info (omit student_ids to avoid leaking user IDs) ────
    debug_neighbors = [
        {k: v for k, v in n.items() if k != 'student_id'}
        for n in neighbours
    ]

    results: List[Dict] = []
    for pred in predictions[:limit]:
        # Strip student_ids from per-neighbour contributions too
        safe_contributions = [
            {'similarity': c['similarity'], 'score': c['score']}
            for c in pred.get('neighbor_contributions', [])
        ]
        results.append({
            'task_id':         pred['task_id'],
            'predicted_score': pred['predicted_score'],
            'neighbor_count':  pred['neighbor_count'],
            'reason':          pred['reason'],
            'cf_debug': {
                'n_neighbors_found':       len(neighbours),
                'interaction_matrix_size': len(interactions),
                'target_interactions':     len(interactions.get(target_id, {})),
                'neighbors':               debug_neighbors,
                'neighbor_contributions':  safe_contributions,
            },
        })

    return results
