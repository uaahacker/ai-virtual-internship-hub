"""
Task recommendation service using MCQ assessment results and student profile.

Logic:
1. Get student's assessment attempts and strongest/weakest domains
2. Get student's preferred skills and learning goals
3. Analyze task requirements and difficulty
4. Calculate match score (0-100) based on:
   - Domain match with strongest domains
   - Difficulty alignment with skill level
   - Skill match with required_skills
   - Learning alignment with outcomes
5. Generate recommendation reason
6. Return ranked recommendations
"""

from django.db.models import Count, Avg, Q
from decimal import Decimal
from .models import Task, TaskAssignment
from apps.assessments.models import AssessmentAttempt
from apps.accounts.models import StudentProfile


class TaskRecommendationService:
    """Service to recommend tasks to students based on their profile and performance."""

    # Weight factors for recommendation algorithm
    DOMAIN_MATCH_WEIGHT = 0.35
    DIFFICULTY_MATCH_WEIGHT = 0.25
    SKILL_MATCH_WEIGHT = 0.25
    TYPE_PREFERENCE_WEIGHT = 0.15

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
        Calculate match score (0-100) for task vs student.
        
        Factors:
        - Domain match (strongest/weakest domains)
        - Difficulty alignment (task difficulty vs student skill level)
        - Skill match (required skills vs student skills)
        - Task type preference
        """
        score = 0.0
        explanations = []

        # 1. Domain Match (35%)
        domain_score = TaskRecommendationService._calculate_domain_score(
            task, student_profile, assessment_profile
        )
        score += domain_score * TaskRecommendationService.DOMAIN_MATCH_WEIGHT
        explanations.append(f"Domain match: {domain_score:.0f}/100")

        # 2. Difficulty Match (25%)
        difficulty_score = TaskRecommendationService._calculate_difficulty_score(
            task, assessment_profile
        )
        score += difficulty_score * TaskRecommendationService.DIFFICULTY_MATCH_WEIGHT
        explanations.append(f"Difficulty match: {difficulty_score:.0f}/100")

        # 3. Skill Match (25%)
        skill_score = TaskRecommendationService._calculate_skill_score(
            task, student_profile
        )
        score += skill_score * TaskRecommendationService.SKILL_MATCH_WEIGHT
        explanations.append(f"Skill match: {skill_score:.0f}/100")

        # 4. Learning Outcomes (15%)
        learning_score = TaskRecommendationService._calculate_learning_score(
            task, assessment_profile
        )
        score += learning_score * TaskRecommendationService.TYPE_PREFERENCE_WEIGHT
        explanations.append(f"Learning opportunity: {learning_score:.0f}/100")

        return round(min(score, 100.0), 2), explanations

    @staticmethod
    def _calculate_domain_score(task, student_profile, assessment_profile):
        """Domain alignment score."""
        score = 50.0  # Base score

        strongest_domain = assessment_profile.get('strongest_domain')
        task_domain = task.domain

        if task_domain == strongest_domain:
            # Recommend tasks in strongest domain (practice expertise)
            score += 40
            return score

        if task_domain in assessment_profile.get('domains_attempted', []):
            # Already has some experience
            score += 20

        # Check student profile preferences
        preferred_domains = student_profile.get('preferred_domains', [])
        if task_domain in preferred_domains:
            score += 25

        return score

    @staticmethod
    def _calculate_difficulty_score(task, assessment_profile):
        """Difficulty alignment score."""
        student_level = assessment_profile.get('skill_level', 'Beginner')
        task_difficulty = task.difficulty

        # Perfect match
        if student_level == task_difficulty:
            return 100.0

        # Map skill levels to progression
        level_map = {'Beginner': 1, 'Intermediate': 2, 'Advanced': 3}
        difficulty_map = {'Beginner': 1, 'Intermediate': 2, 'Advanced': 3}

        student_val = level_map.get(student_level, 1)
        task_val = difficulty_map.get(task_difficulty, 1)

        # One level difference = 80 points
        # Two level difference = 50 points
        # More = 30 points
        diff = abs(student_val - task_val)

        if diff == 0:
            return 100.0
        elif diff == 1:
            return 80.0
        elif diff == 2:
            return 50.0
        else:
            return 30.0

    @staticmethod
    def _calculate_skill_score(task, student_profile):
        """Required skills match score."""
        required_skills = task.required_skills or []
        student_skills = student_profile.get('selected_skills', [])

        if not required_skills:
            return 70.0  # No specific skills required, moderate score

        if not student_skills:
            return 40.0  # Student has no skills listed

        # Calculate intersection
        matching_skills = set(required_skills) & set(student_skills)
        match_percentage = (len(matching_skills) / len(required_skills)) * 100

        return match_percentage

    @staticmethod
    def _calculate_learning_score(task, assessment_profile):
        """Learning opportunity score based on task type."""
        learning_outcomes = task.learning_outcomes or []

        if not learning_outcomes:
            return 60.0

        # More learning outcomes = better opportunity
        score = min(len(learning_outcomes) * 15, 100.0)
        return score

    @staticmethod
    def get_recommendations_for_student(student, limit=10):
        """
        Get top task recommendations for a student.
        
        Returns:
        [
            {
                'task': Task,
                'score': float,
                'reason': str,
                'explanations': [list of scoring factors],
            }
        ]
        """
        # Get student profile
        try:
            student_profile = student.student_profile
            profile_data = {
                'preferred_domains': student_profile.preferred_domains or [],
                'selected_skills': student_profile.selected_skills or [],
            }
        except:
            profile_data = {
                'preferred_domains': [],
                'selected_skills': [],
            }

        # Get assessment profile
        assessment_profile = TaskRecommendationService.get_student_assessment_profile(
            student
        )

        # Get all active tasks not already assigned to student
        already_assigned = TaskAssignment.objects.filter(student=student).values_list('task_id', flat=True)
        available_tasks = Task.objects.filter(is_active=True).exclude(id__in=already_assigned)

        # Calculate scores for each task
        recommendations = []
        for task in available_tasks:
            match_score, explanations = TaskRecommendationService.calculate_match_score(
                task, profile_data, assessment_profile
            )

            reason = TaskRecommendationService.generate_recommendation_reason(
                task, match_score, profile_data, assessment_profile
            )

            recommendations.append({
                'task': task,
                'score': match_score,
                'reason': reason,
                'explanations': explanations,
            })

        # Sort by score descending
        recommendations.sort(key=lambda x: x['score'], reverse=True)

        return recommendations[:limit]

    @staticmethod
    def generate_recommendation_reason(task, score, profile_data, assessment_profile):
        """
        Generate human-readable recommendation reason.
        
        Example:
        "This task is recommended because your Portfolio Project matches your 
        advanced Programming skills and interest in Web Development. Great 
        opportunity to build real-world experience!"
        """
        strongest_domain = assessment_profile.get('strongest_domain')
        skill_level = assessment_profile.get('skill_level')

        parts = []

        # Main reason
        if score >= 90:
            parts.append(f"Perfect match for you!")
        elif score >= 75:
            parts.append(f"This is a great fit for your profile!")
        elif score >= 60:
            parts.append(f"This task is well-suited for your level!")
        else:
            parts.append(f"This could be a good learning opportunity!")

        # Specific reason
        if task.domain == strongest_domain:
            parts.append(
                f"The {task.domain} domain aligns with your strongest area, "
                f"where you've shown excellent performance."
            )
        elif task.domain in assessment_profile.get('domains_attempted', []):
            parts.append(
                f"You have experience in {task.domain}, and this {task.difficulty.lower()} "
                f"task will help you deepen your skills."
            )

        # Difficulty
        if task.difficulty == skill_level:
            parts.append(f"The difficulty level is perfect for your {skill_level} skills.")
        elif skill_level == 'Advanced' and task.difficulty == 'Advanced':
            parts.append("This Advanced task will challenge your expertise.")
        elif skill_level == 'Beginner' and task.difficulty == 'Beginner':
            parts.append("This Beginner-level task is great for building fundamentals.")

        # Learning
        if task.learning_outcomes:
            parts.append(
                f"You'll gain valuable skills like {', '.join(task.learning_outcomes[:2])}."
            )

        reason = " ".join(parts)
        return reason

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

            # Don't create if already exists
            if TaskAssignment.objects.filter(student=student, task=task).exists():
                continue

            # Create recommendation
            assignment = TaskAssignment.objects.create(
                student=student,
                task=task,
                status='recommended',
                recommended_score=score,
                recommendation_reason=reason,
            )
            created_count += 1

        return created_count
