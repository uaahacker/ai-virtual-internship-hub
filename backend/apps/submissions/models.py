"""
Stub models for Submissions, AI Evaluations, Mentor Evaluations (future).
"""

from django.db import models
from django.conf import settings
from django.utils import timezone


class Submission(models.Model):
    """Stub"""
    assignment = models.ForeignKey('tasks.TaskAssignment', on_delete=models.CASCADE, related_name='submissions')
    submitted_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='submissions')
    file_url = models.CharField(max_length=500, blank=True)
    notes = models.TextField(blank=True)
    submitted_at = models.DateTimeField(default=timezone.now)

    class Meta:
        db_table = 'submissions'


class AIEvaluation(models.Model):
    """Stub"""
    submission = models.OneToOneField(Submission, on_delete=models.CASCADE, related_name='ai_evaluation')
    ai_score = models.FloatField(default=0)
    plagiarism_score = models.FloatField(default=0)
    remarks = models.TextField(blank=True)
    generated_at = models.DateTimeField(default=timezone.now)

    class Meta:
        db_table = 'ai_evaluations'


class MentorEvaluation(models.Model):
    """Stub"""
    submission = models.OneToOneField(Submission, on_delete=models.CASCADE, related_name='mentor_evaluation')
    mentor = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='evaluations_given')
    final_score = models.FloatField(default=0)
    feedback = models.TextField(blank=True)
    evaluated_at = models.DateTimeField(default=timezone.now)

    class Meta:
        db_table = 'mentor_evaluations'
