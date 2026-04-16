"""
URL routes for Tasks API endpoints.
"""

from django.urls import path
from .views import (
    TaskListView,
    TaskDetailView,
    TaskCreateView,
    RecommendedTasksView,
    MyTasksView,
    AcceptTaskView,
    UpdateTaskAssignmentView,
    TaskAssignmentDetailView,
    RequestMentorReviewView,
)

app_name = 'tasks'

urlpatterns = [
    # Task management (student)
    path('', TaskListView.as_view(), name='task-list'),
    path('<int:pk>/', TaskDetailView.as_view(), name='task-detail'),
    
    # Recommendations
    path('recommended/', RecommendedTasksView.as_view(), name='recommended-tasks'),
    
    # My tasks
    path('my-tasks/', MyTasksView.as_view(), name='my-tasks'),
    
    # Task creation (mentor)
    path('create/', TaskCreateView.as_view(), name='task-create'),
    
    # Task assignments
    path('assignments/<int:assignment_id>/', TaskAssignmentDetailView.as_view(), name='assignment-detail'),
    path('assignments/<int:assignment_id>/accept/', AcceptTaskView.as_view(), name='accept-task'),
    path('assignments/<int:assignment_id>/update/', UpdateTaskAssignmentView.as_view(), name='update-assignment'),
    path('assignments/<int:assignment_id>/request-review/', RequestMentorReviewView.as_view(), name='request-review'),
]
