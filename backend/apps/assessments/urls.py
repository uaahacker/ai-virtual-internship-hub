"""
URL routes for assessments app.
"""

from django.urls import path
from .views import (
    AssessmentListView,
    AssessmentDetailView,
    SubmitAssessmentView,
    AttemptDetailView,
    StudentAttemptsListView,
    AdminAssessmentListView,
    AdminAssessmentManageView,
    AdminAssessmentQuestionView,
    AdminAssessmentQuestionDeleteView,
    AdminTaskListView,
    AdminTaskToggleView,
)

urlpatterns = [
    path('', AssessmentListView.as_view(), name='assessment-list'),
    path('my-attempts/', StudentAttemptsListView.as_view(), name='my-attempts'),
    path('<int:pk>/', AssessmentDetailView.as_view(), name='assessment-detail'),
    path('<int:pk>/submit', SubmitAssessmentView.as_view(), name='assessment-submit'),
    path('attempts/<int:pk>/', AttemptDetailView.as_view(), name='attempt-detail'),

    # Admin management
    path('admin/', AdminAssessmentListView.as_view(), name='admin-assessment-list'),
    path('admin/tasks/', AdminTaskListView.as_view(), name='admin-task-list'),
    path('admin/tasks/<int:pk>/toggle/', AdminTaskToggleView.as_view(), name='admin-task-toggle'),
    path('admin/<int:pk>/', AdminAssessmentManageView.as_view(), name='admin-assessment-manage'),
    path('admin/<int:pk>/questions/', AdminAssessmentQuestionView.as_view(), name='admin-assessment-questions'),
    path('admin/<int:pk>/questions/<int:qid>/', AdminAssessmentQuestionDeleteView.as_view(), name='admin-assessment-question-delete'),
]
