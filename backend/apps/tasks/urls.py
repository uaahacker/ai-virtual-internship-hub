"""
URL routes for Tasks API endpoints.
"""

from django.urls import path
from .views import (
    TaskListView,
    TaskDetailView,
    TaskCreateView,
    MentorTaskListView,
    MentorTaskManageView,
    MentorTaskMCQView,
    MentorTaskMCQDetailView,
    RecommendedTasksView,
    MyTasksView,
    AcceptTaskView,
    UpdateTaskAssignmentView,
    TaskAssignmentDetailView,
    RequestMentorReviewView,
    TaskMCQListView,
    CompleteTaskView,
    SubmitMCQAttemptsView,
    TaskEvaluationDetailView,
    MentorEvaluateTaskView,
    GetMyPortfolioView,
    PortfolioDetailView,
    UpdatePortfolioView,
    PortfolioItemDetailView,
    UpdatePortfolioItemView,
    PortfolioStatsView,
    ExportPortfolioView,
    ExportPortfolioPDFView,
    TaskRecommendationExplanationView,
)
from .analytics_views import (
    StudentAnalyticsView,
    MentorAnalyticsView,
    AdminAnalyticsView,
    ClusterOverviewView,
    DomainPredictionView,
)

app_name = 'tasks'

urlpatterns = [
    path('', TaskListView.as_view(), name='task-list'),
    path('<int:pk>/', TaskDetailView.as_view(), name='task-detail'),

    path('recommended/', RecommendedTasksView.as_view(), name='recommended-tasks'),

    path('my-tasks/', MyTasksView.as_view(), name='my-tasks'),

    path('create/', TaskCreateView.as_view(), name='task-create'),
    path('mentor-tasks/', MentorTaskListView.as_view(), name='mentor-task-list'),
    path('mentor-tasks/<int:pk>/', MentorTaskManageView.as_view(), name='mentor-task-manage'),
    path('mentor-tasks/<int:task_id>/mcq/', MentorTaskMCQView.as_view(), name='mentor-task-mcq'),
    path('mentor-tasks/<int:task_id>/mcq/<int:question_id>/', MentorTaskMCQDetailView.as_view(), name='mentor-task-mcq-detail'),

    path('assignments/<int:assignment_id>/', TaskAssignmentDetailView.as_view(), name='assignment-detail'),
    path('assignments/<int:assignment_id>/accept/', AcceptTaskView.as_view(), name='accept-task'),
    path('assignments/<int:assignment_id>/update/', UpdateTaskAssignmentView.as_view(), name='update-assignment'),
    path('assignments/<int:assignment_id>/request-review/', RequestMentorReviewView.as_view(), name='request-review'),
    path('assignments/<int:assignment_id>/complete/', CompleteTaskView.as_view(), name='complete-task'),
    path('assignments/<int:assignment_id>/explanation/', TaskRecommendationExplanationView.as_view(), name='recommendation-explanation'),

    path('<int:task_id>/mcq-questions/', TaskMCQListView.as_view(), name='task-mcq-list'),
    path('completions/<int:completion_id>/submit-mcq/', SubmitMCQAttemptsView.as_view(), name='submit-mcq'),
    path('evaluations/<int:evaluation_id>/', TaskEvaluationDetailView.as_view(), name='evaluation-detail'),
    path('evaluations/<int:evaluation_id>/evaluate/', MentorEvaluateTaskView.as_view(), name='mentor-evaluate'),

    path('portfolios/me/', GetMyPortfolioView.as_view(), name='my-portfolio'),
    path('portfolios/<int:portfolio_id>/', PortfolioDetailView.as_view(), name='portfolio-detail'),
    path('portfolios/<int:portfolio_id>/update/', UpdatePortfolioView.as_view(), name='portfolio-update'),
    path('portfolios/<int:portfolio_id>/stats/', PortfolioStatsView.as_view(), name='portfolio-stats'),
    path('portfolios/<int:portfolio_id>/export/', ExportPortfolioView.as_view(), name='portfolio-export'),
    path('portfolios/<int:portfolio_id>/export-pdf/', ExportPortfolioPDFView.as_view(), name='portfolio-export-pdf'),
    path('portfolio-items/<int:item_id>/', PortfolioItemDetailView.as_view(), name='portfolio-item-detail'),
    path('portfolio-items/<int:item_id>/update/', UpdatePortfolioItemView.as_view(), name='portfolio-item-update'),

    path('analytics/student/', StudentAnalyticsView.as_view(), name='student-analytics'),
    path('analytics/mentor/', MentorAnalyticsView.as_view(), name='mentor-analytics'),
    path('analytics/admin/', AdminAnalyticsView.as_view(), name='admin-analytics'),
    path('analytics/clusters/', ClusterOverviewView.as_view(), name='cluster-overview'),
    path('analytics/domain-prediction/', DomainPredictionView.as_view(), name='domain-prediction'),
]