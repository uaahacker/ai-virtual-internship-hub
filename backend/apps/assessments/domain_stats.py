"""
Optional domain statistics service for aggregating assessment performance.
Add this to views.py if you want domain-based analytics.

Usage:
  from .views import DomainStatsService
  stats = DomainStatsService.get_student_domain_stats(student_id)
"""

from django.db.models import Avg, Count, Q
from .models import AssessmentAttempt, Assessment


class DomainStatsService:
    """Aggregate assessment statistics by domain."""

    @staticmethod
    def get_student_domain_stats(student_id):
        """
        Get aggregated performance stats for a student by domain.
        
        Returns:
        {
            "domain_name": {
                "attempts": 3,
                "avg_score": 75.5,
                "latest_level": "Intermediate",
                "progress": "improving"
            }
        }
        """
        attempts = AssessmentAttempt.objects.filter(
            student_id=student_id
        ).select_related('assessment')

        domain_stats = {}

        for attempt in attempts:
            domain = attempt.assessment.domain
            
            if domain not in domain_stats:
                domain_stats[domain] = {
                    'attempts': 0,
                    'scores': [],
                    'levels': [],
                    'latest_date': attempt.attempted_at,
                }

            domain_stats[domain]['attempts'] += 1
            domain_stats[domain]['scores'].append(attempt.percentage)
            domain_stats[domain]['levels'].append(attempt.skill_level)
            
            if attempt.attempted_at > domain_stats[domain]['latest_date']:
                domain_stats[domain]['latest_date'] = attempt.attempted_at

        # Calculate aggregates
        formatted_stats = {}
        for domain, data in domain_stats.items():
            scores = data['scores']
            avg_score = sum(scores) / len(scores) if scores else 0
            
            # Determine progress
            if len(scores) > 1:
                progress = 'improving' if scores[-1] > scores[0] else 'stable'
            else:
                progress = 'new'

            formatted_stats[domain] = {
                'attempts': data['attempts'],
                'avg_score': round(avg_score, 2),
                'latest_score': scores[-1] if scores else 0,
                'highest_score': max(scores) if scores else 0,
                'latest_level': data['levels'][-1] if data['levels'] else 'Beginner',
                'progress': progress,
                'latest_attempt': data['latest_date'].isoformat(),
            }

        return formatted_stats

    @staticmethod
    def get_domain_leaderboard(domain_name, limit=10):
        """
        Get top performers in a specific domain.
        
        Returns list of {student_name, avg_score, attempts}
        """
        attempts = AssessmentAttempt.objects.filter(
            assessment__domain=domain_name
        ).select_related('student', 'assessment')

        student_scores = {}
        for attempt in attempts:
            student_id = attempt.student.id
            if student_id not in student_scores:
                student_scores[student_id] = {
                    'name': attempt.student.name,
                    'scores': [],
                }
            student_scores[student_id]['scores'].append(attempt.percentage)

        # Calculate averages
        leaderboard = []
        for student_id, data in student_scores.items():
            avg_score = sum(data['scores']) / len(data['scores'])
            leaderboard.append({
                'student_name': data['name'],
                'avg_score': round(avg_score, 2),
                'attempts': len(data['scores']),
            })

        # Sort by score descending
        leaderboard.sort(key=lambda x: x['avg_score'], reverse=True)
        return leaderboard[:limit]

    @staticmethod
    def get_student_skill_progression(student_id, domain=None):
        """
        Get skill progression over time.
        
        Returns:
        [
            {date, domain, score, level},
            ...
        ]
        """
        query = AssessmentAttempt.objects.filter(student_id=student_id)
        
        if domain:
            query = query.filter(assessment__domain=domain)
        
        query = query.select_related('assessment').order_by('attempted_at')

        progression = []
        for attempt in query:
            progression.append({
                'date': attempt.attempted_at.isoformat(),
                'domain': attempt.assessment.domain,
                'score': attempt.percentage,
                'level': attempt.skill_level,
                'strengths': attempt.strengths,
                'weaknesses': attempt.weaknesses,
            })

        return progression


# Optional: Add this to views.py if you want a REST endpoint

"""
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

class DomainStatsView(APIView):
    '''
    GET /api/assessments/stats/domain
    Get student's domain performance statistics.
    '''
    permission_classes = [IsAuthenticated, IsStudent]

    def get(self, request):
        stats = DomainStatsService.get_student_domain_stats(request.user.id)
        return Response({'success': True, 'data': stats})


class DomainLeaderboardView(APIView):
    '''
    GET /api/assessments/stats/leaderboard?domain=Programming
    Get top performers in a domain.
    '''
    permission_classes = [IsAuthenticated, IsStudent]

    def get(self, request):
        domain = request.query_params.get('domain')
        if not domain:
            return Response(
                {'success': False, 'error': 'domain parameter required'},
                status=400
            )
        leaderboard = DomainStatsService.get_domain_leaderboard(domain)
        return Response({'success': True, 'data': leaderboard})


class SkillProgressionView(APIView):
    '''
    GET /api/assessments/stats/progression?domain=Programming
    Get student's skill progression over time.
    '''
    permission_classes = [IsAuthenticated, IsStudent]

    def get(self, request):
        domain = request.query_params.get('domain')
        progression = DomainStatsService.get_student_skill_progression(
            request.user.id,
            domain=domain
        )
        return Response({'success': True, 'data': progression})


# Add to urls.py:
# path('stats/domain/', DomainStatsView.as_view()),
# path('stats/leaderboard/', DomainLeaderboardView.as_view()),
# path('stats/progression/', SkillProgressionView.as_view()),
"""
