"""
MCQ Evaluation Engine.

Replaces the raw score counter with a structured, multi-dimensional evaluator
that produces concept-wise scores, a weighted domain score, a readiness level,
a skill profile vector, improvement tracking across attempts, and task-type
recommendations — all without any external API calls.

Public API
----------
    result = evaluate(assessment, questions, submitted_answers, student)

    result keys:
        total_score          int       raw correct count
        total_questions      int
        percentage           float     raw percentage (for backward compat.)
        domain_score         float     weighted score 0-100
        skill_level          str       Beginner / Intermediate / Advanced
        readiness_level      str       Novice / Developing / Competent / Proficient / Expert
        concept_scores       dict      {concept: {correct, total, weighted_score, score_pct}}
        strength_tags        list[str] concepts with score_pct >= STRENGTH_THRESHOLD
        weakness_tags        list[str] concepts with score_pct <  WEAKNESS_THRESHOLD
        skill_profile_vector dict      {concept: proficiency 0-1}
        improvement_delta    float|None percentage-point delta vs previous attempt (None=first)
        recommended_task_type str      practice / project / challenge
        recommended_next_step str      single sentence next-step guidance
        detailed_breakdown   dict      per-question {text, submitted, correct_option,
                                         is_correct, concept, difficulty_weight}
"""

from __future__ import annotations
from typing import Dict, List, Optional, Any

# Thresholds
STRENGTH_THRESHOLD = 75.0     # concept score_pct >= this → strength tag
WEAKNESS_THRESHOLD = 50.0     # concept score_pct <  this → weakness tag

# 5-tier readiness mapping (weighted domain score → level)
_READINESS_TIERS = [
    (90.0, 'Expert'),
    (75.0, 'Proficient'),
    (60.0, 'Competent'),
    (40.0, 'Developing'),
    (0.0,  'Novice'),
]

# Backward-compatible 3-tier skill level
_SKILL_TIERS = [
    (80.0, 'Advanced'),
    (50.0, 'Intermediate'),
    (0.0,  'Beginner'),
]

# Recommended task type per readiness level
_TASK_TYPE_MAP = {
    'Novice':     'practice',
    'Developing': 'practice',
    'Competent':  'project',
    'Proficient': 'project',
    'Expert':     'challenge',
}

# Next-step guidance per readiness level
_NEXT_STEP_MAP = {
    'Novice':     'Focus on foundational learning materials and retake this assessment after studying the basics.',
    'Developing': 'Review the concepts you found challenging and attempt beginner-level practice tasks.',
    'Competent':  'Apply your knowledge by working on small guided projects in this domain.',
    'Proficient': 'Take on real project tasks and start building a portfolio to demonstrate your skills.',
    'Expert':     'Pursue advanced challenge tasks and consider mentoring others or taking on freelance work.',
}

# Default concept name used when a question has no concept tag
_DEFAULT_CONCEPT = 'General'


def _derive_readiness(weighted_score: float) -> str:
    """Map a weighted domain score (0-100) to a 5-tier readiness level."""
    for threshold, level in _READINESS_TIERS:
        if weighted_score >= threshold:
            return level
    return 'Novice'


def _derive_skill_level(percentage: float) -> str:
    """Map raw percentage to 3-tier skill level (backward compat.)."""
    for threshold, level in _SKILL_TIERS:
        if percentage >= threshold:
            return level
    return 'Beginner'


def _compute_concept_scores(
    questions: list,
    submitted_answers: Dict[str, str],
) -> Dict[str, Dict[str, Any]]:
    """
    Group questions by concept and compute per-concept scores.

    Each concept entry:
        correct          int    number of correct answers in this concept
        total            int    total questions in this concept
        total_weight     float  sum of difficulty_weight for all Qs in concept
        correct_weight   float  sum of difficulty_weight for correct Qs
        score_pct        float  simple accuracy % (correct/total * 100)
        weighted_score   float  weighted accuracy % (correct_weight/total_weight * 100)
    """
    concept_data: Dict[str, Dict[str, Any]] = {}

    for q in questions:
        concept = (q.concept or '').strip() or _DEFAULT_CONCEPT
        q_id = str(q.id)
        submitted = submitted_answers.get(q_id)
        is_correct = submitted is not None and submitted == q.correct_option
        weight = float(q.difficulty_weight) if q.difficulty_weight else 1.0

        if concept not in concept_data:
            concept_data[concept] = {
                'correct': 0,
                'total': 0,
                'total_weight': 0.0,
                'correct_weight': 0.0,
            }

        concept_data[concept]['total'] += 1
        concept_data[concept]['total_weight'] += weight

        if is_correct:
            concept_data[concept]['correct'] += 1
            concept_data[concept]['correct_weight'] += weight

    # Derive percentages
    result = {}
    for concept, data in concept_data.items():
        total = data['total']
        total_weight = data['total_weight']
        correct = data['correct']
        correct_weight = data['correct_weight']

        score_pct = (correct / total * 100) if total > 0 else 0.0
        weighted_score = (correct_weight / total_weight * 100) if total_weight > 0 else 0.0

        result[concept] = {
            'correct': correct,
            'total': total,
            'total_weight': round(total_weight, 3),
            'correct_weight': round(correct_weight, 3),
            'score_pct': round(score_pct, 2),
            'weighted_score': round(weighted_score, 2),
        }

    return result


def _compute_domain_score(
    questions: list,
    submitted_answers: Dict[str, str],
) -> float:
    """
    Compute a single weighted domain score (0-100).

    Uses each question's difficulty_weight so harder questions carry more weight.
    """
    total_weight = sum(float(q.difficulty_weight) for q in questions)
    if total_weight == 0:
        return 0.0

    correct_weight = sum(
        float(q.difficulty_weight)
        for q in questions
        if submitted_answers.get(str(q.id)) == q.correct_option
    )

    return round(correct_weight / total_weight * 100, 2)


def _build_skill_profile_vector(
    concept_scores: Dict[str, Dict[str, Any]],
) -> Dict[str, float]:
    """
    Build a normalised proficiency vector {concept: 0.0-1.0}.

    Uses weighted_score / 100 so each value is in [0, 1].
    This vector can be consumed by ml_engine for richer recommendations.
    """
    return {
        concept: round(data['weighted_score'] / 100.0, 4)
        for concept, data in concept_scores.items()
    }


def _get_improvement_delta(
    student,
    assessment_domain: str,
    current_percentage: float,
) -> Optional[float]:
    """
    Return the percentage-point change vs the most recent previous attempt
    for the same domain.

    Returns None if this is the student's first attempt in this domain.
    Avoids circular imports by importing AssessmentAttempt locally.
    """
    from .models import AssessmentAttempt
    prev = (
        AssessmentAttempt.objects
        .filter(student=student, assessment__domain=assessment_domain)
        .order_by('-attempted_at')
        .values_list('percentage', flat=True)
        .first()
    )
    if prev is None:
        return None
    return round(current_percentage - float(prev), 2)


def _build_detailed_breakdown(
    questions: list,
    submitted_answers: Dict[str, str],
) -> Dict[str, Any]:
    """
    Per-question analysis dict.

    Extends the legacy format with concept and difficulty_weight so the
    frontend can render concept-grouped breakdowns.
    """
    breakdown = {}
    for q in questions:
        q_id = str(q.id)
        submitted = submitted_answers.get(q_id, 'Not answered')
        is_correct = submitted == q.correct_option
        breakdown[q_id] = {
            'text': q.text[:120],
            'submitted': submitted,
            'correct_option': q.correct_option,
            'is_correct': is_correct,
            'concept': (q.concept or '').strip() or _DEFAULT_CONCEPT,
            'difficulty_weight': float(q.difficulty_weight),
            'explanation': (
                'Correctly answered!'
                if is_correct
                else f'Correct answer: {q.correct_option}. You selected: {submitted}.'
            ),
        }
    return breakdown


def _build_tag_lists(
    concept_scores: Dict[str, Dict[str, Any]],
) -> tuple[List[str], List[str]]:
    """
    Derive strength and weakness concept tags.

    strength_tags: concepts where score_pct >= STRENGTH_THRESHOLD
    weakness_tags: concepts where score_pct <  WEAKNESS_THRESHOLD
    """
    strength_tags = [
        c for c, d in concept_scores.items()
        if d['score_pct'] >= STRENGTH_THRESHOLD
    ]
    weakness_tags = [
        c for c, d in concept_scores.items()
        if d['score_pct'] < WEAKNESS_THRESHOLD
    ]
    return sorted(strength_tags), sorted(weakness_tags)


def evaluate(
    assessment,
    questions: list,
    submitted_answers: Dict[str, str],
    student,
) -> Dict[str, Any]:
    """
    Run full MCQ evaluation and return a structured result dict.

    This is the single entry point called by SubmitAssessmentView.

    Args:
        assessment:        Assessment model instance
        questions:         list of Question model instances
        submitted_answers: {str(question_id): 'A'/'B'/'C'/'D'}
        student:           User model instance (for improvement delta lookup)

    Returns:
        Structured evaluation result (see module docstring for full schema).
    """
    total = len(questions)
    if total == 0:
        raise ValueError('Assessment has no questions.')

    # ── Raw correct count and simple percentage ────────────────────────────
    correct_count = sum(
        1 for q in questions
        if submitted_answers.get(str(q.id)) == q.correct_option
    )
    percentage = round(correct_count / total * 100, 2)

    # ── Weighted domain score ──────────────────────────────────────────────
    domain_score = _compute_domain_score(questions, submitted_answers)

    # ── Tier derivations ───────────────────────────────────────────────────
    skill_level = _derive_skill_level(percentage)
    readiness_level = _derive_readiness(domain_score)
    recommended_task_type = _TASK_TYPE_MAP[readiness_level]
    recommended_next_step = _NEXT_STEP_MAP[readiness_level]

    # ── Concept-wise scoring ───────────────────────────────────────────────
    concept_scores = _compute_concept_scores(questions, submitted_answers)

    # ── Tags ───────────────────────────────────────────────────────────────
    strength_tags, weakness_tags = _build_tag_lists(concept_scores)

    # ── Skill profile vector ───────────────────────────────────────────────
    skill_profile_vector = _build_skill_profile_vector(concept_scores)

    # ── Improvement delta ──────────────────────────────────────────────────
    improvement_delta = _get_improvement_delta(
        student, assessment.domain, percentage
    )

    # ── Per-question breakdown ─────────────────────────────────────────────
    detailed_breakdown = _build_detailed_breakdown(questions, submitted_answers)

    # ── Legacy strengths / weaknesses list (human-readable sentences) ──────
    strengths = [f"Strong understanding of: {', '.join(strength_tags)}"] if strength_tags else [
        f"Correctly answered {correct_count} out of {total} questions."
    ]
    weaknesses = [f"Needs work on: {', '.join(weakness_tags)}"] if weakness_tags else []

    return {
        # core scores
        'total_score': correct_count,
        'total_questions': total,
        'percentage': percentage,
        'domain_score': domain_score,
        # levels
        'skill_level': skill_level,
        'readiness_level': readiness_level,
        # concept analysis
        'concept_scores': concept_scores,
        'strength_tags': strength_tags,
        'weakness_tags': weakness_tags,
        'skill_profile_vector': skill_profile_vector,
        # progress tracking
        'improvement_delta': improvement_delta,
        # next steps
        'recommended_task_type': recommended_task_type,
        'recommended_next_step': recommended_next_step,
        # legacy / detailed
        'detailed_breakdown': detailed_breakdown,
        'strengths': strengths,
        'weaknesses': weaknesses,
    }
