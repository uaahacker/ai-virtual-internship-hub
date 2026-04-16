"""
Django admin configuration for chatbot models.
"""

from django.contrib import admin
from .models import ChatSession, ChatMessage, ChatFeedback


@admin.register(ChatSession)
class ChatSessionAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'title', 'created_at', 'updated_at', 'is_archived']
    list_filter = ['created_at', 'is_archived']
    search_fields = ['user__username', 'title']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Session Info', {'fields': ('user', 'title')}),
        ('Status', {'fields': ('is_archived',)}),
        ('Timestamps', {'fields': ('created_at', 'updated_at')}),
    )


@admin.register(ChatMessage)
class ChatMessageAdmin(admin.ModelAdmin):
    list_display = ['id', 'session', 'role', 'created_at', 'content_preview']
    list_filter = ['role', 'created_at', 'session__user']
    search_fields = ['session__title', 'content']
    readonly_fields = ['created_at']
    
    fieldsets = (
        ('Message Info', {'fields': ('session', 'role')}),
        ('Content', {'fields': ('content',)}),
        ('Metadata', {'fields': ('tokens_used', 'created_at')}),
    )
    
    def content_preview(self, obj):
        return obj.content[:50] + '...' if len(obj.content) > 50 else obj.content
    content_preview.short_description = 'Content'


@admin.register(ChatFeedback)
class ChatFeedbackAdmin(admin.ModelAdmin):
    list_display = ['id', 'message', 'rating', 'created_at']
    list_filter = ['rating', 'created_at']
    search_fields = ['message__content', 'comment']
    readonly_fields = ['created_at']
    
    fieldsets = (
        ('Feedback Info', {'fields': ('message', 'rating')}),
        ('Comment', {'fields': ('comment',)}),
        ('Metadata', {'fields': ('created_at',)}),
    )
