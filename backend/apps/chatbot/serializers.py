"""
Serializers for chatbot API endpoints.
"""

from rest_framework import serializers
from django.contrib.auth.models import User
from .models import ChatSession, ChatMessage, ChatFeedback


class ChatMessageSerializer(serializers.ModelSerializer):
    """Serializer for chat messages."""
    
    class Meta:
        model = ChatMessage
        fields = ['id', 'role', 'content', 'created_at']
        read_only_fields = ['id', 'created_at']


class ChatSessionSerializer(serializers.ModelSerializer):
    """Serializer for chat sessions."""
    
    message_count = serializers.SerializerMethodField()
    
    class Meta:
        model = ChatSession
        fields = ['id', 'title', 'created_at', 'updated_at', 'is_archived', 'message_count']
        read_only_fields = ['id', 'created_at', 'updated_at', 'message_count']
    
    def get_message_count(self, obj):
        return obj.messages.count()


class ChatSessionDetailSerializer(serializers.ModelSerializer):
    """Detailed serializer for chat sessions with messages."""
    
    messages = ChatMessageSerializer(many=True, read_only=True)
    
    class Meta:
        model = ChatSession
        fields = ['id', 'title', 'created_at', 'updated_at', 'is_archived', 'messages']
        read_only_fields = ['id', 'created_at', 'updated_at', 'messages']


class ChatMessageCreateSerializer(serializers.Serializer):
    """Serializer for creating/sending chat messages."""
    
    content = serializers.CharField(
        max_length=5000,
        min_length=1,
        help_text="The chat message content"
    )
    
    def validate_content(self, value):
        if not value.strip():
            raise serializers.ValidationError("Message cannot be empty or whitespace only")
        return value.strip()


class ChatFeedbackSerializer(serializers.ModelSerializer):
    """Serializer for chat feedback."""
    
    class Meta:
        model = ChatFeedback
        fields = ['id', 'message', 'rating', 'comment', 'created_at']
        read_only_fields = ['id', 'created_at']


class ChatFeedbackCreateSerializer(serializers.Serializer):
    """Serializer for creating chat feedback."""
    
    message_id = serializers.IntegerField()
    rating = serializers.IntegerField(min_value=1, max_value=5)
    comment = serializers.CharField(required=False, allow_blank=True, max_length=1000)
    
    def validate_comment(self, value):
        return value.strip() if value else None


class ChatSessionStatsSerializer(serializers.Serializer):
    """Serializer for chat session statistics."""
    
    session_id = serializers.IntegerField()
    title = serializers.CharField()
    user_messages = serializers.IntegerField()
    assistant_messages = serializers.IntegerField()
    total_messages = serializers.IntegerField()
    created_at = serializers.DateTimeField()
    updated_at = serializers.DateTimeField()
    duration_minutes = serializers.IntegerField()


class ChatResponseSerializer(serializers.Serializer):
    """Serializer for chat response."""
    
    success = serializers.BooleanField()
    message = serializers.CharField(required=False)
    data = serializers.JSONField(required=False)
    error = serializers.CharField(required=False)
