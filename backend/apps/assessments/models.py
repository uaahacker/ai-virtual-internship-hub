"""
Assessment models aligned with database design diagrams.

Collections:
  - assessments: title, domain/category, time_limit
  - questions: assessment (FK), text, options[], correct_option
  - assessment_attempts: student (FK), assessment (FK), answers[], score,
                         percentage, skill_level, recommended_domains, attempted_at
"""

from django.db import models
from django.conf import settings
from django.utils import timezone


class Assessment(models.Model):
    """
    Represents a skill assessment / MCQ test for a specific domain.
    Maps to 'assessments' collection.
    """

    DOMAIN_CHOICES = [
        ('Graphic Design', 'Graphic Design'),
        ('Content Writing', 'Content Writing'),
        ('Programming', 'Programming'),
        ('Freelancing', 'Freelancing'),
        ('E-Commerce', 'E-Commerce'),
        ('QuickBooks', 'QuickBooks'),
        ('AutoCAD', 'AutoCAD'),
        ('Data Analytics', 'Data Analytics'),
        ('Digital Marketing', 'Digital Marketing'),
        ('WordPress', 'WordPress'),
    ]

    title = models.CharField(max_length=255)
    domain = models.CharField(max_length=50, choices=DOMAIN_CHOICES)
    description = models.TextField(blank=True, default='')
    time_limit = models.IntegerField(
        null=True, blank=True,
        help_text='Time limit in minutes (optional)',
    )
    is_active = models.BooleanField(default=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='created_assessments',
    )
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        db_table = 'assessments'
        ordering = ['domain', 'title']

    def __str__(self):
        return f"{self.title} ({self.domain})"


class Question(models.Model):
    """
    MCQ question belonging to an assessment.
    Maps to 'questions' collection.
    """

    assessment = models.ForeignKey(
        Assessment,
        on_delete=models.CASCADE,
        related_name='questions',
    )
    text = models.TextField()
    option_a = models.CharField(max_length=500)
    option_b = models.CharField(max_length=500)
    option_c = models.CharField(max_length=500)
    option_d = models.CharField(max_length=500)
    correct_option = models.CharField(
        max_length=1,
        choices=[('A', 'A'), ('B', 'B'), ('C', 'C'), ('D', 'D')],
    )
    order = models.IntegerField(default=0)
    # Concept tag enables concept-wise scoring (e.g. "recursion", "colour theory")
    concept = models.CharField(
        max_length=100,
        blank=True,
        default='',
        help_text='Concept or sub-topic this question tests (e.g. "loops", "typography")',
    )
    # Allows harder questions to carry more weight (default 1.0 = equal weight)
    difficulty_weight = models.FloatField(
        default=1.0,
        help_text='Scoring weight relative to other questions in the same assessment',
    )

    class Meta:
        db_table = 'questions'
        ordering = ['order']

    def __str__(self):
        return f"Q{self.order}: {self.text[:60]}"

    def get_options(self):
        return {
            'A': self.option_a,
            'B': self.option_b,
            'C': self.option_c,
            'D': self.option_d,
        }


class AssessmentAttempt(models.Model):
    """
    Records a student's attempt at an assessment along with
    score, percentage, skill level, and recommendation.
    Maps to 'assessment_attempts' collection.
    """

    SKILL_LEVELS = [
        ('Beginner', 'Beginner'),
        ('Intermediate', 'Intermediate'),
        ('Advanced', 'Advanced'),
    ]

    student = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='assessment_attempts',
    )
    assessment = models.ForeignKey(
        Assessment,
        on_delete=models.CASCADE,
        related_name='attempts',
    )
    answers = models.JSONField(
        default=dict,
        help_text='Dict mapping question_id -> selected_option (A/B/C/D)',
    )
    score = models.IntegerField(default=0)
    total_questions = models.IntegerField(default=0)
    percentage = models.FloatField(default=0.0)
    skill_level = models.CharField(max_length=15, choices=SKILL_LEVELS, default='Beginner')
    recommended_domains = models.JSONField(
        default=list,
        help_text='List of recommended domain/career objects',
    )
    # Enhanced fields for detailed analysis
    detailed_breakdown = models.JSONField(
        default=dict,
        blank=True,
        help_text='Per-question analysis {question_id: {text, submitted, correct, explanation}}',
    )
    strengths = models.JSONField(
        default=list,
        blank=True,
        help_text='List of topics/concepts answered correctly',
    )
    weaknesses = models.JSONField(
        default=list,
        blank=True,
        help_text='List of topics/concepts answered incorrectly',
    )
    next_steps = models.JSONField(
        default=list,
        blank=True,
        help_text='Actionable next steps based on performance',
    )
    # ── Rich evaluation fields ─────────────────────────────────────────────
    # concept_scores: {concept: {correct: int, total: int, score_pct: float}}
    concept_scores = models.JSONField(
        default=dict,
        blank=True,
        help_text='Per-concept score breakdown {concept: {correct, total, score_pct}}',
    )
    # domain_score: weighted score accounting for question difficulty_weight
    domain_score = models.FloatField(
        default=0.0,
        help_text='Weighted domain score (0-100) using question difficulty weights',
    )
    # readiness_level: finer-grained than skill_level
    # 'Novice' | 'Developing' | 'Competent' | 'Proficient' | 'Expert'
    readiness_level = models.CharField(
        max_length=15,
        default='Novice',
        help_text='5-tier readiness level derived from weighted domain score',
    )
    # skill_profile_vector: {concept: proficiency 0-1} for ML consumption
    skill_profile_vector = models.JSONField(
        default=dict,
        blank=True,
        help_text='Normalised proficiency per concept {concept: 0.0-1.0}',
    )
    # improvement_delta vs previous attempt in same domain
    improvement_delta = models.FloatField(
        null=True,
        blank=True,
        help_text='Percentage-point change from previous attempt in this domain (null = first attempt)',
    )
    # recommended_next_task_type: 'practice' | 'project' | 'challenge'
    recommended_task_type = models.CharField(
        max_length=20,
        default='practice',
        help_text='Recommended task type based on readiness level',
    )
    # NLP-generated structured feedback (generated locally, stored for dashboard access)
    feedback = models.JSONField(
        default=dict,
        blank=True,
        help_text=(
            'Structured feedback dict: {summary, strength, weakness, recommendation, '
            'suggested_task_type, tone, cluster_insight, mentor_insight, full_text}'
        ),
    )
    attempted_at = models.DateTimeField(default=timezone.now)

    class Meta:
        db_table = 'assessment_attempts'
        ordering = ['-attempted_at']

    def __str__(self):
        return (
            f"{self.student.name} - {self.assessment.title} "
            f"({self.percentage:.0f}%)"
        )
