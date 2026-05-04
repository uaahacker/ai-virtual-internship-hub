"""
Notifications, Announcements, and Direct Messages.
"""

from django.db import models
from django.conf import settings
from django.utils import timezone


class Notification(models.Model):
    TYPE_CHOICES = [
        ('announcement', 'Announcement'),
        ('message', 'Direct Message'),
        ('task', 'Task Update'),
        ('review', 'Review'),
        ('system', 'System'),
    ]
    STATUS_CHOICES = [('Read', 'Read'), ('Unread', 'Unread')]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='notifications')
    title = models.CharField(max_length=200, default='')
    message = models.TextField()
    notification_type = models.CharField(max_length=20, choices=TYPE_CHOICES, default='system')
    link = models.CharField(max_length=200, blank=True, default='')
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='Unread')
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        db_table = 'notifications'
        ordering = ['-created_at']

    def __str__(self):
        return f"[{self.notification_type}] {self.user.name}: {self.message[:50]}"


class Announcement(models.Model):
    AUDIENCE_CHOICES = [
        ('All', 'Everyone'),
        ('Students', 'Students Only'),
        ('Mentors', 'Mentors Only'),
    ]

    title = models.CharField(max_length=255)
    content = models.TextField()
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='announcements',
    )
    audience = models.CharField(max_length=10, choices=AUDIENCE_CHOICES, default='All')
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        db_table = 'announcements'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.title} ({self.audience})"


class DirectMessage(models.Model):
    sender = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='sent_messages',
    )
    receiver = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='received_messages',
    )
    content = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        db_table = 'direct_messages'
        ordering = ['created_at']

    def __str__(self):
        return f"{self.sender.name} → {self.receiver.name}: {self.content[:50]}"
