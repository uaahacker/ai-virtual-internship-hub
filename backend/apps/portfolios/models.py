"""
Portfolio module containing Portfolio and PortfolioItem models
for tracking student achievements and completed tasks.
"""

from django.db import models
from django.conf import settings
from django.utils import timezone


class Portfolio(models.Model):
    """
    Portfolio for a student containing completed task items.
    One portfolio per student - auto-created on first task completion.
    """

    # Student Portfolio
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='portfolio',
        help_text='Student who owns this portfolio',
    )

    # Portfolio Info
    title = models.CharField(
        max_length=200,
        blank=True,
        default='',
        help_text='Portfolio title',
    )
    bio = models.TextField(
        blank=True,
        default='',
        help_text='Portfolio summary/bio',
    )

    # Metadata
    is_public = models.BooleanField(
        default=False,
        help_text='Whether portfolio is publicly viewable',
    )
    total_items = models.IntegerField(
        default=0,
        help_text='Count of completed portfolio items',
    )
    average_score = models.FloatField(
        default=0.0,
        help_text='Average score across all portfolio items',
    )

    # Timestamps
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'portfolios'
        ordering = ['-created_at']

    def __str__(self):
        return f"Portfolio: {self.user.name if hasattr(self.user, 'name') else self.user.username}"


class PortfolioItem(models.Model):
    """
    Individual portfolio item representing a completed and evaluated task.
    Auto-generated when task evaluation is completed.
    """

    # Relations
    portfolio = models.ForeignKey(
        Portfolio,
        on_delete=models.CASCADE,
        related_name='items',
        help_text='Portfolio this item belongs to',
    )
    task = models.ForeignKey(
        'tasks.Task',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        help_text='The task this item is based on',
    )
    task_evaluation = models.OneToOneField(
        'tasks.TaskEvaluation',
        on_delete=models.CASCADE,
        related_name='portfolio_item',
        null=True,
        blank=True,
        help_text='The evaluation this item is based on',
    )

    # Task Information (denormalized for performance)
    task_title = models.CharField(
        max_length=255,
        help_text='Task title',
    )
    task_domain = models.CharField(
        max_length=50,
        help_text='Task domain',
    )
    task_difficulty = models.CharField(
        max_length=15,
        help_text='Task difficulty level',
    )
    task_type = models.CharField(
        max_length=20,
        blank=True,
        default='',
    )

    # Completion Information
    completion_date = models.DateTimeField(
        help_text='When task was completed',
    )
    evaluation_date = models.DateTimeField(
        help_text='When evaluation was completed',
    )

    # Scores
    mcq_score = models.FloatField(
        default=0.0,
        help_text='MCQ quiz score',
    )
    mentor_score = models.FloatField(
        null=True,
        blank=True,
        help_text='Mentor evaluation score',
    )
    final_score = models.FloatField(
        default=0.0,
        help_text='Final combined score',
    )

    # Skill Information (from task)
    skills_demonstrated = models.JSONField(
        default=list,
        help_text='List of skills demonstrated in this task',
    )

    # Reflective Text (from student)
    student_reflection = models.TextField(
        blank=True,
        default='',
        help_text='Student\'s reflection on the task',
    )

    # Summary & Feedback (template-based)
    description = models.TextField(
        blank=True,
        default='',
        help_text='Concise professional summary of the project',
    )
    project_summary = models.TextField(
        blank=True,
        default='',
        help_text='Concise professional summary of the project',
    )
    mentor_feedback_summary = models.TextField(
        blank=True,
        default='',
        help_text='Key points from mentor feedback',
    )
    strengths_summary = models.TextField(
        blank=True,
        default='',
        help_text='Strengths demonstrated (bullet list)',
    )

    # Display Settings
    is_featured = models.BooleanField(
        default=False,
        help_text='Whether to feature this item prominently',
    )
    display_order = models.IntegerField(
        default=0,
        help_text='Order to display items in portfolio',
    )

    # Timestamps
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'portfolio_items'
        ordering = ['-completion_date']
        verbose_name = 'Portfolio Item'
        verbose_name_plural = 'Portfolio Items'

    def __str__(self):
        return f"Portfolio Item: {self.task_title} (Score: {self.final_score})"


class ExternalProfile(models.Model):
    """Stub for linking to external profiles."""
    PLATFORM_CHOICES = [('Upwork', 'Upwork'), ('Fiverr', 'Fiverr'), ('LinkedIn', 'LinkedIn')]
    portfolio = models.ForeignKey(Portfolio, on_delete=models.CASCADE, related_name='external_profiles')
    platform_name = models.CharField(max_length=50, choices=PLATFORM_CHOICES)
    profile_url = models.URLField()

    class Meta:
        db_table = 'external_profiles'
