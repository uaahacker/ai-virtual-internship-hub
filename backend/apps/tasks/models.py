"""
Stub models for Tasks module (future implementation).
Aligned with class diagram and ERD.
"""

from django.db import models
from django.conf import settings
from django.utils import timezone


class Task(models.Model):
    """Stub: Task created by mentor/admin."""
    DIFFICULTY_CHOICES = [
        ('Easy', 'Easy'), ('Intermediate', 'Intermediate'), ('Hard', 'Hard'),
    ]
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    difficulty = models.CharField(max_length=15, choices=DIFFICULTY_CHOICES, default='Easy')
    category = models.CharField(max_length=100, blank=True)
    estimated_duration = models.IntegerField(null=True, blank=True, help_text='Minutes')
    deadline = models.DateTimeField(null=True, blank=True)
    ai_evaluation_enabled = models.BooleanField(default=False)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name='tasks_created')
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        db_table = 'tasks'

    def __str__(self):
        return self.title


class TaskAssignment(models.Model):
    """Stub: Links a task to a student."""
    STATUS_CHOICES = [
        ('Assigned', 'Assigned'), ('In Progress', 'In Progress'),
        ('Submitted', 'Submitted'), ('Completed', 'Completed'),
    ]
    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name='assignments')
    student = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='task_assignments')
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='Assigned')
    assigned_date = models.DateTimeField(default=timezone.now)

    class Meta:
        db_table = 'task_assignments'

    def __str__(self):
        return f"{self.task.title} -> {self.student.name}"
