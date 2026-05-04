"""
Auth views: Register, Login, Me, Admin user list.
"""

from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate, get_user_model
from django.db import models

from .serializers import (
    RegisterSerializer, LoginSerializer, UserSerializer,
    StudentProfileSerializer, MentorProfileSerializer,
    UpdateProfileSerializer, ChangePasswordSerializer,
)
from .models import StudentProfile, MentorProfile
from apps.core.permissions import IsAdmin, IsStudent, IsMentor

User = get_user_model()


class RegisterView(APIView):
    """
    POST /api/auth/register
    Public. Registers Student or Mentor accounts only.
    """
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        # Immediately create profile with domain data provided at signup
        if user.role == 'Student':
            preferred = request.data.get('preferred_domains', [])
            if not isinstance(preferred, list):
                preferred = []
            StudentProfile.objects.get_or_create(
                user=user,
                defaults={'preferred_domains': preferred},
            )
        elif user.role == 'Mentor':
            expertise = request.data.get('expertise_domains', [])
            if not isinstance(expertise, list):
                expertise = []
            MentorProfile.objects.get_or_create(
                user=user,
                defaults={'expertise_domains': expertise},
            )

        tokens = _get_tokens(user)
        return Response(
            {
                'success': True,
                'message': 'Registration successful.',
                'data': {
                    'user': UserSerializer(user).data,
                    'tokens': tokens,
                },
            },
            status=status.HTTP_201_CREATED,
        )


class LoginView(APIView):
    """
    POST /api/auth/login
    Public. Returns JWT access + refresh tokens.
    """
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = authenticate(
            request,
            email=serializer.validated_data['email'].lower(),
            password=serializer.validated_data['password'],
        )

        if user is None:
            return Response(
                {'success': False, 'error': {'code': 401, 'message': 'Invalid email or password.'}},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        if user.status != 'Active':
            return Response(
                {'success': False, 'error': {'code': 403, 'message': 'Account is inactive.'}},
                status=status.HTTP_403_FORBIDDEN,
            )

        tokens = _get_tokens(user)
        return Response(
            {
                'success': True,
                'message': 'Login successful.',
                'data': {
                    'user': UserSerializer(user).data,
                    'tokens': tokens,
                },
            },
            status=status.HTTP_200_OK,
        )


class LogoutView(APIView):
    """
    POST /api/auth/logout
    Accepts refresh token and blacklists it (best-effort).
    Frontend should clear stored tokens.
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            refresh_token = request.data.get('refresh')
            if refresh_token:
                token = RefreshToken(refresh_token)
                token.blacklist()
        except Exception:
            pass  # Best-effort blacklist; frontend clears tokens regardless
        return Response({'success': True, 'message': 'Logged out successfully.'})


class MeView(APIView):
    """
    GET /api/auth/me
    Returns the currently authenticated user's profile.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response(
            {
                'success': True,
                'data': UserSerializer(request.user).data,
            }
        )


class AdminUserListView(APIView):
    """
    GET /api/auth/admin/users
    Admin-only: lists all users with roles.
    """
    permission_classes = [IsAuthenticated, IsAdmin]

    def get(self, request):
        users = User.objects.all().order_by('-created_at')
        return Response(
            {
                'success': True,
                'data': UserSerializer(users, many=True).data,
            }
        )


class StudentProfileView(APIView):
    """
    GET/PUT /api/profiles/student/
    Get or update the current student's profile.
    """
    permission_classes = [IsAuthenticated, IsStudent]

    def get(self, request):
        """Retrieve current student's profile (create if doesn't exist)."""
        profile, created = StudentProfile.objects.get_or_create(user=request.user)
        serializer = StudentProfileSerializer(profile)
        return Response({'success': True, 'data': serializer.data})

    def put(self, request):
        """Update current student's profile."""
        profile, created = StudentProfile.objects.get_or_create(user=request.user)
        
        # Only allow updates to editable fields
        editable_data = {
            'bio': request.data.get('bio', profile.bio),
            'selected_skills': request.data.get('selected_skills', profile.selected_skills),
            'preferred_domains': request.data.get('preferred_domains', profile.preferred_domains),
        }
        
        serializer = StudentProfileSerializer(
            profile,
            data={**StudentProfileSerializer(profile).data, **editable_data},
            partial=True,
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        
        return Response(
            {
                'success': True,
                'message': 'Profile updated successfully.',
                'data': serializer.data,
            }
        )


class StudentProfileDetailView(APIView):
    """
    GET /api/profiles/student/<student_id>/
    View another student's profile (public view).
    """
    permission_classes = [IsAuthenticated]

    def get(self, request, student_id):
        """Retrieve a specific student's profile."""
        try:
            user = User.objects.get(id=student_id, role='Student')
            profile, created = StudentProfile.objects.get_or_create(user=user)
            serializer = StudentProfileSerializer(profile)
            return Response({'success': True, 'data': serializer.data})
        except User.DoesNotExist:
            return Response(
                {'success': False, 'error': {'code': 404, 'message': 'Student not found.'}},
                status=status.HTTP_404_NOT_FOUND,
            )


class MentorProfileView(APIView):
    """
    GET/PUT /api/profiles/mentor/
    Get or update the current mentor's profile.
    """
    permission_classes = [IsAuthenticated, IsMentor]

    def get(self, request):
        """Retrieve current mentor's profile (create if doesn't exist)."""
        profile, created = MentorProfile.objects.get_or_create(user=request.user)
        serializer = MentorProfileSerializer(profile)
        return Response({'success': True, 'data': serializer.data})

    def put(self, request):
        """Update current mentor's profile."""
        profile, created = MentorProfile.objects.get_or_create(user=request.user)
        
        # Only allow updates to editable fields
        editable_data = {
            'expertise_domains': request.data.get('expertise_domains', profile.expertise_domains),
            'bio': request.data.get('bio', profile.bio),
            'max_students': request.data.get('max_students', profile.max_students),
        }
        
        serializer = MentorProfileSerializer(
            profile,
            data={**MentorProfileSerializer(profile).data, **editable_data},
            partial=True,
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        
        return Response(
            {
                'success': True,
                'message': 'Profile updated successfully.',
                'data': serializer.data,
            }
        )


class MentorProfileDetailView(APIView):
    """
    GET /api/profiles/mentor/<mentor_id>/
    View a specific mentor's profile (public view).
    """
    permission_classes = [IsAuthenticated]

    def get(self, request, mentor_id):
        """Retrieve a specific mentor's profile."""
        try:
            user = User.objects.get(id=mentor_id, role='Mentor')
            profile, created = MentorProfile.objects.get_or_create(user=user)
            serializer = MentorProfileSerializer(profile)
            return Response({'success': True, 'data': serializer.data})
        except User.DoesNotExist:
            return Response(
                {'success': False, 'error': {'code': 404, 'message': 'Mentor not found.'}},
                status=status.HTTP_404_NOT_FOUND,
            )


class MentorAssignedStudentsView(APIView):
    """
    GET /api/mentor/assigned-students/
    Get list of all students assigned to the current mentor.
    """
    permission_classes = [IsAuthenticated, IsMentor]

    def get(self, request):
        mentor_profile, _ = MentorProfile.objects.get_or_create(user=request.user)
        
        # Get all students assigned to this mentor
        students = StudentProfile.objects.filter(mentor_assigned=request.user)
        
        result = []
        for student_profile in students:
            # Count pending review tasks
            from apps.tasks.models import TaskAssignment
            pending_reviews = TaskAssignment.objects.filter(
                student=student_profile.user,
                mentor_review_requested=True,
                mentor_review_status='requested'
            ).count()
            
            result.append({
                'student_id': student_profile.user.id,
                'student_name': student_profile.user.name,
                'student_email': student_profile.user.email,
                'preferred_domains': student_profile.preferred_domains,
                'progress_score': student_profile.progress_score,
                'completed_tasks_count': student_profile.completed_tasks_count,
                'pending_review_count': pending_reviews,
                'strongest_domain': student_profile.strongest_domain,
                'cluster_label': student_profile.cluster_label,
                'cluster_display_name': (
                    student_profile.cluster_summary.get('display_name', student_profile.cluster_label)
                    if student_profile.cluster_summary else student_profile.cluster_label
                ),
            })
        
        return Response({'success': True, 'data': result})


class MentorStudentDetailView(APIView):
    """
    GET /api/mentor/students/<student_id>/
    Get detailed view of an assigned student with assessment summary and tasks.
    """
    permission_classes = [IsAuthenticated, IsMentor]

    def get(self, request, student_id):
        # Verify student is assigned to tis mentor
        try:
            student_profile = StudentProfile.objects.get(
                user_id=student_id,
                mentor_assigned=request.user
            )
        except StudentProfile.DoesNotExist:
            return Response(
                {'success': False, 'error': {'code': 403, 'message': 'This student is not assigned to you.'}},
                status=status.HTTP_403_FORBIDDEN,
            )
        
        # Get assessment summary
        from apps.assessments.models import AssessmentAttempt
        attempts = AssessmentAttempt.objects.filter(student_id=student_id)
        
        attempt_list = list(attempts.select_related('assessment'))
        assessment_summary = {
            'total_attempts': len(attempt_list),
            'domains_attempted': list(set(a.assessment.domain for a in attempt_list if a.assessment)),
            'average_score': round(
                sum(a.domain_score for a in attempt_list) / len(attempt_list), 1
            ) if attempt_list else 0,
            'strongest_domain': student_profile.strongest_domain,
            'weakest_domain': student_profile.weakest_domain,
        }
        
        # Get current tasks
        from apps.tasks.models import TaskAssignment
        current_tasks_qs = TaskAssignment.objects.filter(
            student_id=student_id,
            status__in=['accepted', 'in_progress']
        ).select_related('task')
        current_tasks = [
            {
                'id': ta.id,
                'task_title': ta.task.title,
                'status': ta.status,
                'progress_percentage': ta.progress_percentage,
                'created_at': ta.created_at.isoformat() if ta.created_at else None,
            }
            for ta in current_tasks_qs
        ]

        # Get pending review tasks
        pending_reviews_qs = TaskAssignment.objects.filter(
            student_id=student_id,
            mentor_review_requested=True,
            mentor_review_status='requested'
        ).select_related('task')
        pending_review_tasks = [
            {
                'id': ta.id,
                'task_title': ta.task.title,
                'status': ta.status,
                'progress_percentage': ta.progress_percentage,
                'completed_at': ta.completed_at.isoformat() if ta.completed_at else None,
            }
            for ta in pending_reviews_qs
        ]
        
        return Response({
            'success': True,
            'data': {
                'student_id': student_profile.user.id,
                'student_name': student_profile.user.name,
                'student_email': student_profile.user.email,
                'bio': student_profile.bio,
                'preferred_domains': student_profile.preferred_domains,
                'selected_skills': student_profile.selected_skills,
                'strongest_domain': student_profile.strongest_domain,
                'weakest_domain': student_profile.weakest_domain,
                'progress_score': student_profile.progress_score,
                'completed_tasks_count': student_profile.completed_tasks_count,
                'assessment_summary': assessment_summary,
                'current_tasks': current_tasks,
                'pending_review_tasks': pending_review_tasks,
            }
        })


class MentorPendingReviewsView(APIView):
    """
    GET /api/mentor/pending-reviews/
    Get all pending task reviews for the mentor's students.
    """
    permission_classes = [IsAuthenticated, IsMentor]

    def get(self, request):
        from apps.tasks.models import TaskAssignment

        # Avoid deep ORM traversal — get student IDs directly
        mentor_student_ids = list(
            StudentProfile.objects.filter(mentor_assigned=request.user)
            .values_list('user_id', flat=True)
        )

        pending_qs = TaskAssignment.objects.filter(
            student_id__in=mentor_student_ids,
            mentor_review_requested=True,
            mentor_review_status='requested',
        ).select_related('student', 'task')

        result = []
        for ta in pending_qs:
            # Traverse TaskAssignment → TaskCompletion → TaskEvaluation
            evaluation_id = None
            mcq_score = None
            reflective_text = ''
            try:
                completion = ta.completion
                reflective_text = completion.reflective_text or ''
                try:
                    evaluation_id = completion.evaluation.id
                    mcq_score = completion.evaluation.mcq_score
                except Exception:
                    pass
            except Exception:
                pass

            result.append({
                'id': ta.id,
                'student__name': ta.student.name,
                'student__id': ta.student.id,
                'task__title': ta.task.title,
                'task__domain': ta.task.domain,
                'task__description': ta.task.description,
                'task__difficulty': ta.task.difficulty,
                'status': ta.status,
                'progress_percentage': ta.progress_percentage,
                'completed_at': ta.completed_at.isoformat() if ta.completed_at else None,
                'evaluation_id': evaluation_id,
                'mcq_score': mcq_score,
                'reflective_text': reflective_text,
            })

        return Response({'success': True, 'data': result})


class MentorSubmitReviewView(APIView):
    """
    POST /api/mentor/reviews/<assignment_id>/submit/
    Submit mentor feedback/review for a task.
    """
    permission_classes = [IsAuthenticated, IsMentor]

    def post(self, request, assignment_id):
        from apps.tasks.models import TaskAssignment
        from apps.tasks.serializers import MentorFeedbackSubmitSerializer
        
        try:
            assignment = TaskAssignment.objects.select_related('student').get(pk=assignment_id)
        except TaskAssignment.DoesNotExist:
            return Response(
                {'success': False, 'error': {'code': 404, 'message': 'Task assignment not found.'}},
                status=status.HTTP_404_NOT_FOUND,
            )
        
        # Verify student is assigned to this mentor
        if assignment.student.student_profile.mentor_assigned != request.user:
            return Response(
                {'success': False, 'error': {'code': 403, 'message': 'This review is not for your student.'}},
                status=status.HTTP_403_FORBIDDEN,
            )
        
        # Verify review is requested
        if not assignment.mentor_review_requested:
            return Response(
                {'success': False, 'error': {'code': 400, 'message': 'No review requested for this task.'}},
                status=status.HTTP_400_BAD_REQUEST,
            )
        
        serializer = MentorFeedbackSubmitSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(
                {'success': False, 'error': serializer.errors},
                status=status.HTTP_400_BAD_REQUEST,
            )
        
        # Update assignment with feedback
        assignment.mentor_feedback = serializer.validated_data['mentor_feedback']
        assignment.mentor_review_status = serializer.validated_data['mentor_review_status']
        assignment.save()
        
        return Response({
            'success': True,
            'message': 'Review submitted successfully.',
            'data': {
                'id': assignment.id,
                'mentor_feedback': assignment.mentor_feedback,
                'mentor_review_status': assignment.mentor_review_status,
            }
        })


class MentorReviewHistoryView(APIView):
    """
    GET /api/mentor/review-history/
    Returns the 20 most recent task evaluations submitted by this mentor.
    """
    permission_classes = [IsAuthenticated, IsMentor]

    def get(self, request):
        from apps.tasks.models import TaskEvaluation

        evaluations = (
            TaskEvaluation.objects.filter(
                evaluated_by=request.user,
                status='evaluated',
            )
            .select_related(
                'task_completion__task_assignment__task',
                'task_completion__task_assignment__student',
            )
            .order_by('-evaluated_at')[:20]
        )

        result = []
        for ev in evaluations:
            try:
                ta = ev.task_completion.task_assignment
                result.append({
                    'evaluation_id': ev.id,
                    'assignment_id': ta.id,
                    'task_title': ta.task.title,
                    'task_domain': ta.task.domain,
                    'student_name': ta.student.name,
                    'student_id': ta.student.id,
                    'mcq_score': ev.mcq_score,
                    'mentor_score': ev.mentor_score,
                    'final_score': ev.final_score,
                    'evaluated_at': ev.evaluated_at.isoformat() if ev.evaluated_at else None,
                })
            except Exception:
                continue

        return Response({'success': True, 'data': result})


class MentorAvailableStudentsView(APIView):
    """
    GET /api/mentor/available-students/
    Returns students not yet assigned to any mentor, optionally filtered by domain.
    Mentor can use this to pick students to supervise.
    """
    permission_classes = [IsAuthenticated, IsMentor]

    def get(self, request):
        mentor_profile, _ = MentorProfile.objects.get_or_create(user=request.user)
        domain_filter = request.query_params.get('domain', None)

        # Students with no mentor assigned
        qs = StudentProfile.objects.filter(mentor_assigned__isnull=True)

        if domain_filter:
            # Filter by strongest domain OR preferred domains containing this domain
            qs = qs.filter(
                models.Q(strongest_domain__iexact=domain_filter) |
                models.Q(preferred_domains__icontains=domain_filter)
            )
        # No domain_filter → return ALL unassigned students so new students
        # (who haven't completed assessments yet) are always visible to mentors

        result = []
        for sp in qs.select_related('user')[:50]:
            result.append({
                'student_id': sp.user.id,
                'student_name': sp.user.name,
                'student_email': sp.user.email,
                'strongest_domain': sp.strongest_domain,
                'preferred_domains': sp.preferred_domains,
                'progress_score': sp.progress_score,
                'completed_tasks_count': sp.completed_tasks_count,
                'cluster_label': sp.cluster_label,
            })

        return Response({'success': True, 'data': result})


class MentorSelfAssignStudentView(APIView):
    """
    POST /api/mentor/assign-student/
    Mentor assigns a student to themselves.
    Body: { student_id: <int> }
    """
    permission_classes = [IsAuthenticated, IsMentor]

    def post(self, request):
        student_id = request.data.get('student_id')
        if not student_id:
            return Response(
                {'success': False, 'error': {'code': 400, 'message': 'student_id is required.'}},
                status=status.HTTP_400_BAD_REQUEST,
            )

        mentor_profile, _ = MentorProfile.objects.get_or_create(user=request.user)

        if mentor_profile.current_student_count >= mentor_profile.max_students:
            return Response(
                {'success': False, 'error': {'code': 400, 'message': 'You have reached your maximum student capacity.'}},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            student_profile = StudentProfile.objects.get(user_id=student_id)
        except StudentProfile.DoesNotExist:
            return Response(
                {'success': False, 'error': {'code': 404, 'message': 'Student not found.'}},
                status=status.HTTP_404_NOT_FOUND,
            )

        if student_profile.mentor_assigned is not None:
            return Response(
                {'success': False, 'error': {'code': 400, 'message': 'Student already has an assigned mentor.'}},
                status=status.HTTP_400_BAD_REQUEST,
            )

        student_profile.mentor_assigned = request.user
        student_profile.save()
        mentor_profile.current_student_count = StudentProfile.objects.filter(mentor_assigned=request.user).count()
        mentor_profile.save()

        return Response({
            'success': True,
            'message': f'{student_profile.user.name} has been assigned to you.',
            'data': {'student_id': student_id, 'student_name': student_profile.user.name}
        })


class MentorUnassignStudentView(APIView):
    """
    POST /api/mentor/unassign-student/<student_id>/
    Mentor removes a student from their list.
    """
    permission_classes = [IsAuthenticated, IsMentor]

    def post(self, request, student_id):
        try:
            student_profile = StudentProfile.objects.get(
                user_id=student_id,
                mentor_assigned=request.user
            )
        except StudentProfile.DoesNotExist:
            return Response(
                {'success': False, 'error': {'code': 404, 'message': 'Student not found or not assigned to you.'}},
                status=status.HTTP_404_NOT_FOUND,
            )

        student_profile.mentor_assigned = None
        student_profile.save()

        mentor_profile, _ = MentorProfile.objects.get_or_create(user=request.user)
        mentor_profile.current_student_count = StudentProfile.objects.filter(mentor_assigned=request.user).count()
        mentor_profile.save()

        return Response({
            'success': True,
            'message': 'Student unassigned successfully.',
        })


class AutoAssignMentorView(APIView):
    """
    POST /api/mentor/auto-assign/
    Auto-assign mentors to students based on recommended domain and mentor expertise.
    Admin/Mentor only.
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        from django.contrib.auth import get_user_model
        
        # Only admin or mentors can trigger auto-assign
        if request.user.role not in ['Admin', 'Mentor']:
            return Response(
                {'success': False, 'error': {'code': 403, 'message': 'Insufficient permissions.'}},
                status=status.HTTP_403_FORBIDDEN,
            )
        
        User = get_user_model()
        
        # Get students without mentors
        unassigned_students = StudentProfile.objects.filter(mentor_assigned__isnull=True)
        assigned_count = 0
        
        for student_profile in unassigned_students:
            # Get student's strongest domain
            domain = student_profile.strongest_domain or (
                student_profile.preferred_domains[0] if student_profile.preferred_domains else None
            )
            
            if not domain:
                continue
            
            # Find available mentors with this expertise
            mentors = MentorProfile.objects.filter(
                expertise_domains__contains=domain,
                current_student_count__lt=models.F('max_students')
            ).select_related('user').order_by('-rating')
            
            if mentors.exists():
                mentor = mentors.first()
                student_profile.mentor_assigned = mentor.user
                student_profile.save()
                
                # Update mentor's student count
                mentor.current_student_count += 1
                mentor.save()
                
                assigned_count += 1
        
        return Response({
            'success': True,
            'message': f'{assigned_count} students assigned to mentors.',
            'data': {'assigned_count': assigned_count}
        })


class UpdateProfileView(APIView):
    """
    PUT /api/auth/profile/update/
    Update current user's profile (name and profile picture).
    """
    permission_classes = [IsAuthenticated]

    def put(self, request):
        """Update user's name and profile picture."""
        serializer = UpdateProfileSerializer(
            request.user,
            data=request.data,
            partial=True
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        
        return Response({
            'success': True,
            'message': 'Profile updated successfully.',
            'data': UserSerializer(request.user).data,
        })


class ChangePasswordView(APIView):
    """
    POST /api/auth/change-password/
    Change the current user's password.
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        """Change user password."""
        serializer = ChangePasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        # Verify old password
        user = request.user
        if not user.check_password(serializer.validated_data['old_password']):
            return Response(
                {'success': False, 'error': 'Old password is incorrect.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Set new password
        user.set_password(serializer.validated_data['new_password'])
        user.save()
        
        return Response({
            'success': True,
            'message': 'Password changed successfully.',
        })


# ---------- Admin Management Views ----------

class AdminStatsView(APIView):
    """
    GET /api/auth/admin/stats/
    Returns platform-wide statistics for the admin dashboard.
    """
    permission_classes = [IsAuthenticated, IsAdmin]

    def get(self, request):
        from apps.tasks.models import Task, TaskAssignment, TaskCompletion
        from apps.assessments.models import Assessment, AssessmentAttempt

        total_users = User.objects.count()
        students = User.objects.filter(role='Student').count()
        mentors = User.objects.filter(role='Mentor').count()
        admins = User.objects.filter(role='Admin').count()
        active_users = User.objects.filter(status='Active').count()

        total_tasks = Task.objects.count()
        active_tasks = Task.objects.filter(is_active=True).count()
        total_assignments = TaskAssignment.objects.count()
        completed_assignments = TaskAssignment.objects.filter(status='completed').count()

        total_assessments = Assessment.objects.count()
        total_attempts = AssessmentAttempt.objects.count()

        unassigned_students = StudentProfile.objects.filter(mentor_assigned__isnull=True).count()

        # Recent activity: last 7 users
        recent_users = User.objects.order_by('-created_at')[:5]
        recent_users_data = [
            {'id': u.id, 'name': u.name, 'email': u.email, 'role': u.role, 'created_at': u.created_at.isoformat()}
            for u in recent_users
        ]

        return Response({
            'success': True,
            'data': {
                'users': {
                    'total': total_users,
                    'students': students,
                    'mentors': mentors,
                    'admins': admins,
                    'active': active_users,
                    'inactive': total_users - active_users,
                    'unassigned_students': unassigned_students,
                },
                'tasks': {
                    'total': total_tasks,
                    'active': active_tasks,
                    'inactive': total_tasks - active_tasks,
                    'total_assignments': total_assignments,
                    'completed_assignments': completed_assignments,
                },
                'assessments': {
                    'total': total_assessments,
                    'total_attempts': total_attempts,
                },
                'recent_users': recent_users_data,
            }
        })


class AdminUserManageView(APIView):
    """
    GET  /api/auth/admin/users/<user_id>/  – fetch single user
    PUT  /api/auth/admin/users/<user_id>/  – update name/email/role/status
    DELETE /api/auth/admin/users/<user_id>/  – delete user
    """
    permission_classes = [IsAuthenticated, IsAdmin]

    def get(self, request, user_id):
        try:
            user = User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return Response({'success': False, 'error': {'code': 404, 'message': 'User not found.'}},
                            status=status.HTTP_404_NOT_FOUND)
        return Response({'success': True, 'data': UserSerializer(user).data})

    def put(self, request, user_id):
        try:
            user = User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return Response({'success': False, 'error': {'code': 404, 'message': 'User not found.'}},
                            status=status.HTTP_404_NOT_FOUND)

        # Prevent admin from deactivating/deleting their own account
        if user == request.user and request.data.get('status') == 'Inactive':
            return Response({'success': False, 'error': {'code': 400, 'message': 'You cannot deactivate your own account.'}},
                            status=status.HTTP_400_BAD_REQUEST)

        allowed_fields = ['name', 'email', 'role', 'status']
        for field in allowed_fields:
            if field in request.data:
                if field == 'email':
                    new_email = request.data['email'].lower()
                    if User.objects.filter(email__iexact=new_email).exclude(pk=user_id).exists():
                        return Response({'success': False, 'error': {'code': 400, 'message': 'Email already in use.'}},
                                        status=status.HTTP_400_BAD_REQUEST)
                    setattr(user, field, new_email)
                elif field == 'role' and request.data['role'] not in ['Student', 'Mentor', 'Admin']:
                    return Response({'success': False, 'error': {'code': 400, 'message': 'Invalid role.'}},
                                    status=status.HTTP_400_BAD_REQUEST)
                elif field == 'status' and request.data['status'] not in ['Active', 'Inactive']:
                    return Response({'success': False, 'error': {'code': 400, 'message': 'Invalid status.'}},
                                    status=status.HTTP_400_BAD_REQUEST)
                else:
                    setattr(user, field, request.data[field])

        user.save()
        return Response({'success': True, 'message': 'User updated successfully.', 'data': UserSerializer(user).data})

    def delete(self, request, user_id):
        try:
            user = User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return Response({'success': False, 'error': {'code': 404, 'message': 'User not found.'}},
                            status=status.HTTP_404_NOT_FOUND)

        if user == request.user:
            return Response({'success': False, 'error': {'code': 400, 'message': 'You cannot delete your own account.'}},
                            status=status.HTTP_400_BAD_REQUEST)

        user.delete()
        return Response({'success': True, 'message': 'User deleted successfully.'})


class AdminCreateUserView(APIView):
    """
    POST /api/auth/admin/users/create/
    Admin creates a new user (any role, including Admin).
    """
    permission_classes = [IsAuthenticated, IsAdmin]

    def post(self, request):
        name = request.data.get('name', '').strip()
        email = request.data.get('email', '').strip().lower()
        password = request.data.get('password', '').strip()
        role = request.data.get('role', 'Student')
        user_status = request.data.get('status', 'Active')

        if not name or not email or not password:
            return Response({'success': False, 'error': {'code': 400, 'message': 'name, email and password are required.'}},
                            status=status.HTTP_400_BAD_REQUEST)

        if role not in ['Student', 'Mentor', 'Admin']:
            return Response({'success': False, 'error': {'code': 400, 'message': 'Invalid role.'}},
                            status=status.HTTP_400_BAD_REQUEST)

        if User.objects.filter(email__iexact=email).exists():
            return Response({'success': False, 'error': {'code': 400, 'message': 'Email already in use.'}},
                            status=status.HTTP_400_BAD_REQUEST)

        from django.contrib.auth.password_validation import validate_password
        try:
            validate_password(password)
        except Exception as e:
            return Response({'success': False, 'error': {'code': 400, 'message': str(e)}},
                            status=status.HTTP_400_BAD_REQUEST)

        user = User.objects.create_user(email=email, name=name, password=password, role=role)
        user.status = user_status
        if role == 'Admin':
            user.is_staff = True
        user.save()

        # Create matching profile
        if role == 'Student':
            StudentProfile.objects.get_or_create(user=user)
        elif role == 'Mentor':
            MentorProfile.objects.get_or_create(user=user)

        return Response({'success': True, 'message': 'User created successfully.', 'data': UserSerializer(user).data},
                        status=status.HTTP_201_CREATED)


class AdminResetPasswordView(APIView):
    """
    POST /api/auth/admin/users/<user_id>/reset-password/
    Admin sets a new password for any user.
    """
    permission_classes = [IsAuthenticated, IsAdmin]

    def post(self, request, user_id):
        try:
            user = User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return Response({'success': False, 'error': {'code': 404, 'message': 'User not found.'}},
                            status=status.HTTP_404_NOT_FOUND)

        new_password = request.data.get('new_password', '').strip()
        if not new_password or len(new_password) < 8:
            return Response({'success': False, 'error': {'code': 400, 'message': 'Password must be at least 8 characters.'}},
                            status=status.HTTP_400_BAD_REQUEST)

        user.set_password(new_password)
        user.save()
        return Response({'success': True, 'message': f'Password reset successfully for {user.email}.'})


# ---------- helpers ----------

def _get_tokens(user):
    refresh = RefreshToken.for_user(user)
    # Embed role in token payload for frontend convenience
    refresh['role'] = user.role
    refresh['name'] = user.name
    return {
        'access': str(refresh.access_token),
        'refresh': str(refresh),
    }
