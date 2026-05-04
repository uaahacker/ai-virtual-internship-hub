"""
URL routes for accounts/auth app.
"""

from django.urls import path
from .views import (
    RegisterView, LoginView, LogoutView, MeView, AdminUserListView,
    StudentProfileView, StudentProfileDetailView,
    MentorProfileView, MentorProfileDetailView,
    MentorAssignedStudentsView, MentorStudentDetailView,
    MentorPendingReviewsView, MentorSubmitReviewView, MentorReviewHistoryView,
    MentorAvailableStudentsView, MentorSelfAssignStudentView, MentorUnassignStudentView,
    AutoAssignMentorView, UpdateProfileView, ChangePasswordView,
    AdminStatsView, AdminUserManageView, AdminCreateUserView, AdminResetPasswordView,
)

urlpatterns = [
    path('register', RegisterView.as_view(), name='auth-register'),
    path('login', LoginView.as_view(), name='auth-login'),
    path('logout', LogoutView.as_view(), name='auth-logout'),
    path('me', MeView.as_view(), name='auth-me'),
    
    # Account settings
    path('profile/update/', UpdateProfileView.as_view(), name='update-profile'),
    path('change-password/', ChangePasswordView.as_view(), name='change-password'),

    # Admin endpoints
    path('admin/stats/', AdminStatsView.as_view(), name='admin-stats'),
    path('admin/users', AdminUserListView.as_view(), name='admin-users'),
    path('admin/users/create/', AdminCreateUserView.as_view(), name='admin-create-user'),
    path('admin/users/<int:user_id>/', AdminUserManageView.as_view(), name='admin-manage-user'),
    path('admin/users/<int:user_id>/reset-password/', AdminResetPasswordView.as_view(), name='admin-reset-password'),

    # Profile endpoints
    path('profiles/student/', StudentProfileView.as_view(), name='student-profile'),
    path('profiles/student/<int:student_id>/', StudentProfileDetailView.as_view(), name='student-profile-detail'),
    path('profiles/mentor/', MentorProfileView.as_view(), name='mentor-profile'),
    path('profiles/mentor/<int:mentor_id>/', MentorProfileDetailView.as_view(), name='mentor-profile-detail'),

    # Mentor dashboard endpoints
    path('mentor/assigned-students/', MentorAssignedStudentsView.as_view(), name='mentor-assigned-students'),
    path('mentor/students/<int:student_id>/', MentorStudentDetailView.as_view(), name='mentor-student-detail'),
    path('mentor/pending-reviews/', MentorPendingReviewsView.as_view(), name='mentor-pending-reviews'),
    path('mentor/reviews/<int:assignment_id>/submit/', MentorSubmitReviewView.as_view(), name='mentor-submit-review'),
    path('mentor/review-history/', MentorReviewHistoryView.as_view(), name='mentor-review-history'),
    path('mentor/available-students/', MentorAvailableStudentsView.as_view(), name='mentor-available-students'),
    path('mentor/assign-student/', MentorSelfAssignStudentView.as_view(), name='mentor-assign-student'),
    path('mentor/unassign-student/<int:student_id>/', MentorUnassignStudentView.as_view(), name='mentor-unassign-student'),
    
    # Auto-assign mentor
    path('mentor/auto-assign/', AutoAssignMentorView.as_view(), name='auto-assign-mentor'),
]
