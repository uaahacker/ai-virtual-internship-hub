"""
Submission models — FR4: Automated Text Evaluation.

Tracks student text submissions (content writing tasks) with
AI-computed NLP metrics: readability, vocabulary diversity,
grammar quality, originality (TF-IDF plagiarism check).
"""

from django.db import models
from django.conf import settings
from django.utils import timezone


class Submission(models.Model):
    """Text submission by a student for a task assignment."""

    SUBMISSION_TYPE_CHOICES = [
        ('text', 'Text / Essay'),
        ('file', 'File Upload'),
    ]

    assignment = models.ForeignKey(
        'tasks.TaskAssignment',
        on_delete=models.CASCADE,
        related_name='submissions',
    )
    submitted_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='submissions',
    )
    submission_type = models.CharField(
        max_length=10,
        choices=SUBMISSION_TYPE_CHOICES,
        default='text',
    )
    # Text submission content (FR4 – NLP evaluation)
    text_content = models.TextField(
        blank=True,
        help_text='Written work submitted by the student for AI evaluation.',
    )
    file_url = models.CharField(max_length=500, blank=True)
    notes = models.TextField(blank=True)
    submitted_at = models.DateTimeField(default=timezone.now)

    class Meta:
        db_table = 'submissions'
        ordering = ['-submitted_at']

    def __str__(self):
        return f"Submission #{self.pk} by {self.submitted_by.email}"


class AIEvaluation(models.Model):
    """
    NLP-based automated evaluation of a text submission.
    Populated by evaluation_service.evaluate_text_submission().
    """

    READINESS_CHOICES = [
        ('Needs Work', 'Needs Work'),
        ('Satisfactory', 'Satisfactory'),
        ('Good', 'Good'),
        ('Excellent', 'Excellent'),
    ]

    submission = models.OneToOneField(
        Submission,
        on_delete=models.CASCADE,
        related_name='ai_evaluation',
    )
    ai_score = models.FloatField(default=0.0, help_text='Overall AI score 0-100')
    readability_score = models.FloatField(default=0.0)
    vocabulary_diversity = models.FloatField(default=0.0)
    grammar_score = models.FloatField(default=0.0)
    originality_score = models.FloatField(
        default=100.0,
        help_text='100 = fully original, lower = similarity detected',
    )
    word_count = models.IntegerField(default=0)
    sentence_count = models.IntegerField(default=0)
    readiness_label = models.CharField(
        max_length=20,
        choices=READINESS_CHOICES,
        default='Needs Work',
    )
    feedback = models.TextField(blank=True)
    strengths = models.JSONField(default=list)
    improvements = models.JSONField(default=list)
    grammar_issues = models.JSONField(default=list)
    # Legacy field kept for compatibility
    plagiarism_score = models.FloatField(default=0.0)
    remarks = models.TextField(blank=True)
    generated_at = models.DateTimeField(default=timezone.now)

    class Meta:
        db_table = 'ai_evaluations'

    def __str__(self):
        return f"AI Eval #{self.pk} — {self.readiness_label} ({self.ai_score:.1f}/100)"


class MentorEvaluation(models.Model):
    """Mentor override / manual grading of a submission."""

    submission = models.OneToOneField(
        Submission,
        on_delete=models.CASCADE,
        related_name='mentor_evaluation',
    )
    mentor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='evaluations_given',
    )
    final_score = models.FloatField(default=0.0)
    feedback = models.TextField(blank=True)
    evaluated_at = models.DateTimeField(default=timezone.now)

    class Meta:
        db_table = 'mentor_evaluations'

    def __str__(self):
        return f"Mentor Eval #{self.pk} — {self.final_score}/100"
