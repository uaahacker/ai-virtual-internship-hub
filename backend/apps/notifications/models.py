"""
Stub models for Notifications module (future).
"""

from django.db import models
from django.conf import settings
from django.utils import timezone


class Notification(models.Model):
    """Stub"""
    STATUS_CHOICES = [('Read', 'Read'), ('Unread', 'Unread')]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='notifications')
    message = models.TextField()
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='Unread')
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        db_table = 'notifications'

    def __str__(self):
        return f"Notification for {self.user.name}: {self.message[:50]}"
