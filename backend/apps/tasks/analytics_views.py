"""
Analytics views for Task analytics endpoints.
"""

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated

from apps.core.permissions import IsStudent, IsMentor, IsAdmin
from .analytics import StudentAnalyticsService, MentorAnalyticsService, AdminAnalyticsService


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
            return Response({
                'success': False,
                'error': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)


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
