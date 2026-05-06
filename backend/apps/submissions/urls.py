"""
URL patterns for the Submissions app (FR4: Automated Text Evaluation).
"""

from django.urls import path
from .views import (
    SubmitTextView,
    SubmissionDetailView,
    MySubmissionsView,
    AssignmentSubmissionView,
)

urlpatterns = [
    path('submit/', SubmitTextView.as_view(), name='submission-submit'),
    path('my/', MySubmissionsView.as_view(), name='submission-my'),
    path('<int:submission_id>/', SubmissionDetailView.as_view(), name='submission-detail'),
    path('assignment/<int:assignment_id>/', AssignmentSubmissionView.as_view(), name='submission-by-assignment'),
]
