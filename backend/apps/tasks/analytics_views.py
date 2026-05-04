"""
Analytics views for Task analytics endpoints.
"""

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated

from apps.core.permissions import IsStudent, IsMentor, IsAdmin
from .analytics import StudentAnalyticsService, MentorAnalyticsService, AdminAnalyticsService


class DomainPredictionView(APIView):
    """
    Predict the best freelancing domain(s) for the current student.
    GET /api/tasks/analytics/domain-prediction/

    Returns a prediction from the trained RandomForest model when available,
    or falls back to the heuristic recency-weighted predictor.
    """
    permission_classes = [IsAuthenticated, IsStudent]

    def get(self, request):
        try:
            from apps.tasks.domain_predictor import DomainPredictorML
            result = DomainPredictorML.predict(request.user)
            return Response({'success': True, 'data': result})
        except Exception as e:
            import traceback
            traceback.print_exc()
            return Response(
                {'success': False, 'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class StudentAnalyticsView(APIView):
    """
    Endpoint for retrieving student analytics data.
    GET /api/tasks/analytics/student/
    """
    permission_classes = [IsAuthenticated, IsStudent]

    def get(self, request):
        try:
            analytics = StudentAnalyticsService.get_student_analytics(request.user)
            return Response({
                'success': True,
                'data': analytics
            })
        except Exception as e:
            import traceback
            error_trace = traceback.format_exc()
            print(f"Error in StudentAnalyticsView: {str(e)}\n{error_trace}")
            return Response({
                'success': False,
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class MentorAnalyticsView(APIView):
    """
    Endpoint for retrieving mentor analytics data.
    GET /api/tasks/analytics/mentor/
    """
    permission_classes = [IsAuthenticated, IsMentor]

    def get(self, request):
        try:
            analytics = MentorAnalyticsService.get_mentor_analytics(request.user)
            return Response({
                'success': True,
                'data': analytics
            })
        except Exception as e:
            return Response({
                'success': False,
                'error': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)


class AdminAnalyticsView(APIView):
    """
    Endpoint for retrieving admin analytics data.
    GET /api/tasks/analytics/admin/
    """
    permission_classes = [IsAuthenticated, IsAdmin]

    def get(self, request):
        try:
            analytics = AdminAnalyticsService.get_admin_analytics()
            return Response({
                'success': True,
                'data': analytics
            })
        except Exception as e:
            return Response({
                'success': False,
                'error': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)


class ClusterOverviewView(APIView):
    """
    Lightweight cluster overview for admin.
    GET /api/tasks/analytics/clusters/

    Returns per-cluster counts, avg scores, and display names in one call
    without loading the full admin analytics payload.
    """
    permission_classes = [IsAuthenticated, IsAdmin]

    def get(self, request):
        try:
            from apps.accounts.models import StudentProfile
            from collections import defaultdict

            all_profiles = list(StudentProfile.objects.all())
            cluster_groups: dict = defaultdict(list)
            for p in all_profiles:
                cluster_groups[p.cluster_id].append(p)

            _CLUSTER_ORDER  = {0: 'Explorer', 1: 'Developing', 2: 'Competent', 3: 'Expert'}
            _GENERIC_NAMES  = {
                0: 'Early Explorers',
                1: 'Developing Learners',
                2: 'Skilled Practitioners',
                3: 'High Achievers',
            }
            _DESCRIPTIONS = {
                0: 'Students who are just beginning their learning journey.',
                1: 'Students making consistent progress across domains.',
                2: 'Students with solid skills ready for advanced work.',
                3: 'Top performers with strong multi-domain expertise.',
            }

            total   = len(all_profiles)
            result  = []
            for cid in sorted(_CLUSTER_ORDER.keys()):
                group = cluster_groups.get(cid, [])
                count = len(group)
                avg_scores = [
                    p.cluster_summary.get('avg_assessment_score', 0)
                    for p in group
                    if p.cluster_summary
                ]
                avg_score = round(sum(avg_scores) / len(avg_scores), 1) if avg_scores else 0.0
                result.append({
                    'cluster_id':   cid,
                    'label':        _CLUSTER_ORDER[cid],
                    'display_name': _GENERIC_NAMES[cid],
                    'description':  _DESCRIPTIONS[cid],
                    'count':        count,
                    'percentage':   round(count / total * 100, 1) if total else 0.0,
                    'avg_score':    avg_score,
                })

            return Response({'success': True, 'data': result})
        except Exception as e:
            return Response({'success': False, 'error': str(e)},
                            status=status.HTTP_400_BAD_REQUEST)
