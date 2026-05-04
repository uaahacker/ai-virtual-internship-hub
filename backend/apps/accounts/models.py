"""
Custom User model aligned with the class/ER diagrams.

Collection: users
Fields: id, name, email (unique), password_hash, role, status, created_at
"""

from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models
from django.utils import timezone


class UserManager(BaseUserManager):
    """Custom manager for the User model."""

    def create_user(self, email, name, password=None, role='Student', **extra_fields):
        if not email:
            raise ValueError('Email address is required.')
        email = self.normalize_email(email)
        user = self.model(email=email, name=name, role=role, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, name, password=None, **extra_fields):
        extra_fields.setdefault('role', 'Admin')
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('status', 'Active')
        return self.create_user(email, name, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    """
    Custom user model matching the database design diagrams.
    Roles: Student, Mentor, Admin
    """

    ROLE_CHOICES = [
        ('Student', 'Student'),
        ('Mentor', 'Mentor'),
        ('Admin', 'Admin'),
    ]

    STATUS_CHOICES = [
        ('Active', 'Active'),
        ('Inactive', 'Inactive'),
    ]

    name = models.CharField(max_length=150)
    email = models.EmailField(unique=True)
    profile_picture = models.ImageField(upload_to='profile_pictures/', null=True, blank=True)
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='Student')
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='Active')
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(default=timezone.now)

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['name']

    class Meta:
        db_table = 'users'
        verbose_name = 'User'
        verbose_name_plural = 'Users'

    def __str__(self):
        return f"{self.name} ({self.email}) - {self.role}"


class StudentProfile(models.Model):
    """
    Extended profile for Student users.
    Collection: student_profiles
    """

    SKILL_LEVELS = [
        ('Beginner', 'Beginner'),
        ('Intermediate', 'Intermediate'),
        ('Advanced', 'Advanced'),
    ]

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='student_profile',
        limit_choices_to={'role': 'Student'},
    )
    bio = models.TextField(blank=True, default='')
    selected_skills = models.JSONField(
        default=list,
        help_text='List of skill names student is interested in',
    )
    preferred_domains = models.JSONField(
        default=list,
        help_text='List of preferred learning domains',
    )
    assessment_summary = models.JSONField(
        default=dict,
        help_text='Summary of assessment attempts {domain: [scores]}',
    )
    skill_scores_by_domain = models.JSONField(
        default=dict,
        help_text='Highest score per domain {domain: score}',
    )
    strongest_domain = models.CharField(
        max_length=100,
        blank=True,
        default='',
        help_text='Domain with highest score',
    )
    weakest_domain = models.CharField(
        max_length=100,
        blank=True,
        default='',
        help_text='Domain with lowest score',
    )
    progress_score = models.FloatField(
        default=0.0,
        help_text='Overall progress score (0-100)',
    )
    completed_tasks_count = models.IntegerField(
        default=0,
        help_text='Number of tasks completed',
    )
    # ML clustering fields — updated by StudentClusterer after each assessment
    cluster_id = models.IntegerField(
        default=0,
        help_text='KMeans cluster assignment (0-3)',
    )
    cluster_label = models.CharField(
        max_length=20,
        default='Explorer',
        help_text='Human-readable cluster label (Explorer/Developing/Competent/Expert)',
    )
    cluster_summary = models.JSONField(
        default=dict,
        help_text='Rich cluster summary: display_name, description, dominant_domain, skill_level, scores',
    )
    mentor_assigned = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='mentored_students',
        limit_choices_to={'role': 'Mentor'},
        help_text='Assigned mentor, if any',
    )
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'student_profiles'
        verbose_name = 'Student Profile'
        verbose_name_plural = 'Student Profiles'

    def __str__(self):
        return f"Profile: {self.user.name}"


class MentorProfile(models.Model):
    """
    Extended profile for Mentor users.
    Collection: mentor_profiles
    """

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='mentor_profile',
        limit_choices_to={'role': 'Mentor'},
    )
    expertise_domains = models.JSONField(
        default=list,
        help_text='List of domains mentor specializes in',
    )
    bio = models.TextField(blank=True, default='', help_text='Mentor biography')
    max_students = models.IntegerField(
        default=10,
        help_text='Maximum number of students mentor can supervise',
    )
    current_student_count = models.IntegerField(
        default=0,
        help_text='Current number of assigned students',
    )
    rating = models.FloatField(
        default=0.0,
        help_text='Mentor rating (0-5) based on student feedback',
    )
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'mentor_profiles'
        verbose_name = 'Mentor Profile'
        verbose_name_plural = 'Mentor Profiles'

    def __str__(self):
        return f"Mentor Profile: {self.user.name}"
