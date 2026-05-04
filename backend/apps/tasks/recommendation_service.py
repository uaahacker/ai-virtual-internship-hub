"""
Task recommendation service — ML-powered hybrid recommender.

Uses two complementary ML strategies:
  1. Content-Based Filtering (60% weight)
     - Builds 30-dim student and task feature vectors
     - Ranks tasks by cosine similarity in feature space
  2. Collaborative Filtering (40% weight, when data is available)
     - User-based KNN on student-task MCQ score interaction matrix
     - Finds K=5 most similar students; predicts missing entries

Falls back gracefully to content-only when CF data is insufficient.
All computation is local (numpy + optional sklearn); no external APIs.
"""

from django.db.models import Count, Avg, Q
from decimal import Decimal
from .models import Task, TaskAssignment
from apps.assessments.models import AssessmentAttempt
from apps.accounts.models import StudentProfile
from .ml_engine import (
    ContentBasedRecommender,
    CollaborativeRecommender,
    compute_hybrid_score,
    DomainPredictor,
    explain_recommendation,
)


class TaskRecommendationService:
    """
    Hybrid task recommendation service.

    Primary path: ContentBasedRecommender + CollaborativeRecommender from ml_engine.
    Fallback: lightweight domain-match heuristic when student has no history.
    """

    @staticmethod
    def get_student_assessment_profile(student):
        """
        Get student's assessment performance profile.
        
        Returns:
        {
            'strongest_domain': str,
            'weakest_domain': str,
            'skill_level': str,
            'avg_score': float,
            'attempts_by_domain': {domain: [scores]},
            'domains_attempted': [list of domains],
        }
        """
        attempts = AssessmentAttempt.objects.filter(student=student)
        
        if not attempts.exists():
            return {
                'strongest_domain': None,
                'weakest_domain': None,
                'skill_level': 'Beginner',
                'avg_score': 0.0,
                'attempts_by_domain': {},
                'domains_attempted': [],
            }

        # Group by domain
        domain_stats = {}
        for attempt in attempts:
            domain = attempt.assessment.domain
            if domain not in domain_stats:
                domain_stats[domain] = []
            domain_stats[domain].append({
                'percentage': attempt.percentage,
                'level': attempt.skill_level,
                'date': attempt.attempted_at,
            })

        # Calculate averages per domain
        domain_averages = {}
        for domain, scores in domain_stats.items():
            percentages = [s['percentage'] for s in scores]
            domain_averages[domain] = {
                'avg_score': sum(percentages) / len(percentages),
                'latest_level': scores[-1]['level'],
                'attempts': len(scores),
            }

        # Find strongest and weakest
        strongest = max(domain_averages.items(), key=lambda x: x[1]['avg_score']) if domain_averages else (None, {})
        weakest = min(domain_averages.items(), key=lambda x: x[1]['avg_score']) if domain_averages else (None, {})

        # Overall average
        all_scores = [a.percentage for a in attempts]
        avg_score = sum(all_scores) / len(all_scores) if all_scores else 0

        # Determine overall skill level
        if avg_score >= 80:
            skill_level = 'Advanced'
        elif avg_score >= 50:
            skill_level = 'Intermediate'
        else:
            skill_level = 'Beginner'

        return {
            'strongest_domain': strongest[0] if strongest[0] else None,
            'weakest_domain': weakest[0] if weakest[0] else None,
            'skill_level': skill_level,
            'avg_score': round(avg_score, 2),
            'domain_stats': domain_averages,
            'domains_attempted': list(domain_averages.keys()),
        }

    @staticmethod
    def calculate_match_score(task, student_profile, assessment_profile):
        """
        Legacy heuristic scorer — kept for backward compatibility with tests/views
        that call this directly. New code uses get_recommendations_for_student().
        """
        domain_scores = {}
        domain_skill_levels = {}
        for d, stats in assessment_profile.get('domain_stats', {}).items():
            domain_scores[d] = stats.get('avg_score', 0.0)
            domain_skill_levels[d] = stats.get('latest_level', 'Beginner')

        from .ml_engine import _build_student_vector
        student_vec = _build_student_vector(
            domain_scores,
            domain_skill_levels,
            student_profile.get('preferred_domains', []),
        )
        score, explanation = ContentBasedRecommender.score_task(
            student_vec, task.domain, task.difficulty, task.required_skills or []
        )
        return score, [explanation]

    @staticmethod
    def get_recommendations_for_student(student, limit=10):
        """
        Get top task recommendations for a student using hybrid ML scoring.

        Steps:
          1. Build student feature vector from assessment history (content-based)
          2. Run collaborative filtering on student-task interaction matrix
          3. Compute hybrid score (60% CB + 40% CF) for each available task
          4. Return top-N sorted by hybrid score

        Returns:
            [
                {
                    'task': Task,
                    'score': float,
                    'reason': str,
                    'explanations': list[str],
                    'method': str,   # 'hybrid' | 'content'
                }
            ]
        """
        already_assigned_ids = list(
            TaskAssignment.objects.filter(student=student)
            .values_list('task_id', flat=True)
        )
        available_tasks = list(
            Task.objects.filter(is_active=True)
            .exclude(id__in=already_assigned_ids)
        )

        if not available_tasks:
            return []

        student_vec = ContentBasedRecommender.build_student_vector_from_db(student)

        available_task_ids = [t.id for t in available_tasks]
        cf_results = CollaborativeRecommender.get_recommendations(
            target_student=student,
            available_task_ids=available_task_ids,
            already_assigned_ids=already_assigned_ids,
            limit=limit * 2,
        )
        cf_scores = {r['task_id']: r for r in cf_results}

        recommendations = []
        for task in available_tasks:
            hybrid_score, explanation = compute_hybrid_score(
                student=student,
                task=task,
                student_vec=student_vec,
                cf_scores=cf_scores,
            )

            cf_entry = cf_scores.get(task.id)
            structured = explain_recommendation(
                student=student,
                task=task,
                student_vec=student_vec,
                cf_entry=cf_entry,
            )
            method = structured['method']
            reason = structured['summary']

            recommendations.append({
                'task': task,
                'score': hybrid_score,
                'reason': reason,
                'explanations': [explanation],
                'explanation': structured,
                'method': method,
            })

        recommendations.sort(key=lambda x: x['score'], reverse=True)
        return recommendations[:limit]

    @staticmethod
    def _build_reason(task, score, method, cf_entry, student):
        """Build a human-readable explanation of why this task was recommended."""
        parts = []

        if score >= 85:
            parts.append("Excellent match for your profile.")
        elif score >= 70:
            parts.append("Strong recommendation based on your skills.")
        elif score >= 55:
            parts.append("Good fit for your current level.")
        else:
            parts.append("Recommended as a learning stretch.")

        if method == 'hybrid' and cf_entry:
            parts.append(cf_entry.get('reason', ''))
        else:
            try:
                profile = student.student_profile
                preferred = profile.preferred_domains or []
            except Exception:
                preferred = []

            if task.domain in preferred:
                parts.append(f"{task.domain} is in your preferred domains.")
            else:
                parts.append(
                    f"This {task.difficulty} {task.domain} task aligns with your assessment history."
                )

        if task.learning_outcomes:
            outcomes = task.learning_outcomes[:2]
            parts.append(f"You'll build skills in: {', '.join(outcomes)}.")

        return ' '.join(parts)

    @staticmethod
    def generate_recommendation_reason(task, score, profile_data, assessment_profile):
        """Legacy shim — delegates to _build_reason with no CF data."""
        return TaskRecommendationService._build_reason(task, score, 'content', None, None)

    @staticmethod
    def create_recommendations_for_student(student):
        """
        Create TaskAssignment records (recommendations) for a student
        based on available tasks. Typically called when:
        - Student completes an assessment
        - Mentor manually triggers recommendations
        - New tasks are created
        """
        recommendations = TaskRecommendationService.get_recommendations_for_student(
            student, limit=5
        )

        created_count = 0
        for rec in recommendations:
            task = rec['task']
            score = rec['score']
            reason = rec['reason']
            structured = rec.get('explanation', {})

            # Don't create if already exists
            if TaskAssignment.objects.filter(student=student, task=task).exists():
                continue

            # Create recommendation
            TaskAssignment.objects.create(
                student=student,
                task=task,
                status='recommended',
                recommended_score=score,
                recommendation_reason=reason,
                recommendation_explanation=structured,
            )
            created_count += 1

        return created_count
