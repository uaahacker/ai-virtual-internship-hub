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
        
        assessment_summary = {
            'total_attempts': attempts.count(),
            'domains_attempted': list(set(a.assessment.domain for a in attempts if a.assessment)),
            'average_score': sum(a.score_percentage for a in attempts) / attempts.count() if attempts.count() > 0 else 0,
            'strongest_domain': student_profile.strongest_domain,
            'weakest_domain': student_profile.weakest_domain,
        }
        
        # Get current tasks
        from apps.tasks.models import TaskAssignment
        current_tasks = TaskAssignment.objects.filter(
            student_id=student_id,
            status__in=['accepted', 'in_progress']
        ).values(
            'id', 'task__title', 'status', 'progress_percentage', 'created_at'
        )
        
        # Get pending review tasks
        pending_reviews = TaskAssignment.objects.filter(
            student_id=student_id,
            mentor_review_requested=True,
            mentor_review_status='requested'
        ).values(
            'id', 'task__title', 'status', 'progress_percentage', 'completed_at'
        )
        
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
                'current_tasks': list(current_tasks),
                'pending_review_tasks': list(pending_reviews),
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
        
        # Get all pending reviews for students assigned to this mentor
        pending_reviews = TaskAssignment.objects.filter(
            student__student_profile__mentor_assigned=request.user,
            mentor_review_requested=True,
            mentor_review_status='requested'
        ).select_related('student', 'task').values(
            'id', 'student__name', 'task__title', 'task__domain',
            'status', 'progress_percentage', 'completed_at'
        )
        
        return Response({
            'success': True,
            'data': list(pending_reviews)
        })


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
