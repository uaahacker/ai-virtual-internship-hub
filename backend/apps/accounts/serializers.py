"""
Serializers for authentication and user management.
"""

from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from .models import StudentProfile, MentorProfile

User = get_user_model()


class RegisterSerializer(serializers.ModelSerializer):
    """Handles user registration with password validation."""

    password = serializers.CharField(write_only=True, min_length=8)
    password_confirm = serializers.CharField(write_only=True, min_length=8)
    role = serializers.ChoiceField(choices=[('Student', 'Student'), ('Mentor', 'Mentor')])

    class Meta:
        model = User
        fields = ['name', 'email', 'password', 'password_confirm', 'role']

    def validate_email(self, value):
        if User.objects.filter(email__iexact=value).exists():
            raise serializers.ValidationError('A user with this email already exists.')
        return value.lower()

    def validate(self, attrs):
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError({'password_confirm': 'Passwords do not match.'})
        # Run Django password validators
        validate_password(attrs['password'])
        return attrs

    def create(self, validated_data):
        validated_data.pop('password_confirm')
        return User.objects.create_user(**validated_data)


class LoginSerializer(serializers.Serializer):
    """Validates login credentials."""

    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)


class UserSerializer(serializers.ModelSerializer):
    """Read-only user representation."""
    profile_picture_url = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['id', 'name', 'email', 'role', 'status', 'created_at', 'profile_picture_url']
        read_only_fields = fields

    def get_profile_picture_url(self, obj):
        if not obj.profile_picture:
            return None
        request = self.context.get('request')
        if request:
            return request.build_absolute_uri(obj.profile_picture.url)
        # Fallback: build URL from MEDIA_URL without request
        from django.conf import settings
        base = getattr(settings, 'MEDIA_BASE_URL', '').rstrip('/')
        return f"{base}{obj.profile_picture.url}" if base else obj.profile_picture.url


class StudentProfileSerializer(serializers.ModelSerializer):
    """Serializer for StudentProfile with nested user data."""

    user_name = serializers.CharField(source='user.name', read_only=True)
    user_email = serializers.CharField(source='user.email', read_only=True)
    mentor_name = serializers.CharField(source='mentor_assigned.name', read_only=True, allow_null=True)

    class Meta:
        model = StudentProfile
        fields = [
            'id', 'user', 'user_name', 'user_email',
            'bio',
            'selected_skills',
            'preferred_domains',
            'assessment_summary',
            'skill_scores_by_domain',
            'strongest_domain',
            'weakest_domain',
            'progress_score',
            'completed_tasks_count',
            'mentor_assigned', 'mentor_name',
            'created_at', 'updated_at',
        ]
        read_only_fields = [
            'id', 'user', 'user_name', 'user_email',
            'assessment_summary', 'skill_scores_by_domain',
            'strongest_domain', 'weakest_domain', 'progress_score',
            'completed_tasks_count', 'created_at', 'updated_at',
        ]


class MentorProfileSerializer(serializers.ModelSerializer):
    """Serializer for MentorProfile with nested user data."""

    user_name = serializers.CharField(source='user.name', read_only=True)
    user_email = serializers.CharField(source='user.email', read_only=True)

    class Meta:
        model = MentorProfile
        fields = [
            'id', 'user', 'user_name', 'user_email',
            'expertise_domains', 'bio', 'max_students', 
            'current_student_count', 'rating',
            'created_at', 'updated_at',
        ]
        read_only_fields = [
            'id', 'user', 'user_name', 'user_email',
            'current_student_count', 'rating', 'created_at', 'updated_at',
        ]


class MentorFeedbackSerializer(serializers.Serializer):
    """Serializer for submitting mentor feedback on tasks."""
    feedback = serializers.CharField(max_length=1000, required=True)
    approval_status = serializers.ChoiceField(
        choices=['approved', 'needs_revision'],
        required=True
    )


class MentorAssignmentSerializer(serializers.Serializer):
    """Serializer for assigning mentor to student."""
    mentor_id = serializers.IntegerField(required=True)
    reason = serializers.CharField(max_length=500, required=False, allow_blank=True)


class StudentProfileDetailSerializer(serializers.ModelSerializer):
    """Detailed student profile for mentor dashboard."""
    
    user_name = serializers.CharField(source='user.name', read_only=True)
    user_email = serializers.CharField(source='user.email', read_only=True)

    class Meta:
        model = StudentProfile
        fields = [
            'id', 'user_name', 'user_email', 'bio',
            'preferred_domains', 'selected_skills',
            'strongest_domain', 'weakest_domain',
            'progress_score', 'completed_tasks_count',
            'assessment_summary', 'skill_scores_by_domain',
            'created_at', 'updated_at'
        ]
        read_only_fields = fields


class AssignedStudentListSerializer(serializers.Serializer):
    """Simplified student list for mentor's dashboard."""
    student_id = serializers.IntegerField()
    student_name = serializers.CharField()
    student_email = serializers.CharField()
    preferred_domains = serializers.ListField()
    progress_score = serializers.FloatField()
    completed_tasks_count = serializers.IntegerField()
    pending_review_count = serializers.IntegerField()


class UpdateProfileSerializer(serializers.ModelSerializer):
    """Serializer for updating user profile (name and picture)."""
    
    class Meta:
        model = User
        fields = ['name', 'profile_picture']


class ChangePasswordSerializer(serializers.Serializer):
    """Serializer for changing user password."""
    
    old_password = serializers.CharField(write_only=True, required=True)
    new_password = serializers.CharField(write_only=True, required=True, min_length=8)
    new_password_confirm = serializers.CharField(write_only=True, required=True, min_length=8)
    
    def validate_new_password(self, value):
        validate_password(value)
        return value
    
    def validate(self, attrs):
        if attrs['new_password'] != attrs['new_password_confirm']:
            raise serializers.ValidationError({'new_password_confirm': 'Passwords do not match.'})
        return attrs


class ForgotPasswordSerializer(serializers.Serializer):
    """Accepts an email and generates a password-reset token."""
    email = serializers.EmailField()


class ResetPasswordSerializer(serializers.Serializer):
    """Validates the reset token and new passwords."""
    token = serializers.UUIDField()
    new_password = serializers.CharField(write_only=True, min_length=8)
    new_password_confirm = serializers.CharField(write_only=True, min_length=8)

    def validate_new_password(self, value):
        validate_password(value)
        return value

    def validate(self, attrs):
        if attrs['new_password'] != attrs['new_password_confirm']:
            raise serializers.ValidationError({'new_password_confirm': 'Passwords do not match.'})
        return attrs
