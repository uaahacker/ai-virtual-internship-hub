"""
Models for chatbot conversations and history storage.
"""

from django.db import models
from django.conf import settings
from django.utils import timezone


class ChatSession(models.Model):
    """Model to store individual chat sessions per user."""
    
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='chat_sessions')
    title = models.CharField(
        max_length=200,
        default='Career Guidance Chat'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_archived = models.BooleanField(default=False)
    
    class Meta:
        ordering = ['-updated_at']
    
    def __str__(self):
        return f"{self.user.username} - {self.title} ({self.created_at.strftime('%Y-%m-%d')})"


class ChatMessage(models.Model):
    """Model to store individual messages in a chat session."""
    
    ROLE_CHOICES = [
        ('user', 'User'),
        ('assistant', 'Assistant'),
        ('system', 'System'),
    ]
    
    session = models.ForeignKey(ChatSession, on_delete=models.CASCADE, related_name='messages')
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)
    content = models.TextField()
    tokens_used = models.IntegerField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['created_at']
    
    def __str__(self):
        return f"{self.session.title} - {self.role}: {self.content[:50]}"


class ChatFeedback(models.Model):
    """Model to store user feedback on chatbot responses."""
    
    RATING_CHOICES = [
        (1, 'Very Unhelpful'),
        (2, 'Unhelpful'),
        (3, 'Neutral'),
        (4, 'Helpful'),
        (5, 'Very Helpful'),
    ]
    
    message = models.OneToOneField(ChatMessage, on_delete=models.CASCADE, related_name='feedback')
    rating = models.IntegerField(choices=RATING_CHOICES)
    comment = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Feedback on {self.message.id} - Rating: {self.rating}/5"
