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
)

urlpatterns = [
    path('', AssessmentListView.as_view(), name='assessment-list'),
    path('my-attempts/', StudentAttemptsListView.as_view(), name='my-attempts'),
    path('<int:pk>/', AssessmentDetailView.as_view(), name='assessment-detail'),
    path('<int:pk>/submit', SubmitAssessmentView.as_view(), name='assessment-submit'),
    path('attempts/<int:pk>/', AttemptDetailView.as_view(), name='attempt-detail'),
]
