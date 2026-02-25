from django.contrib import admin
from .models import Assessment, Question, AssessmentAttempt


class QuestionInline(admin.TabularInline):
    model = Question
    extra = 1


@admin.register(Assessment)
class AssessmentAdmin(admin.ModelAdmin):
    list_display = ['title', 'domain', 'is_active', 'created_at']
    list_filter = ['domain', 'is_active']
    inlines = [QuestionInline]


@admin.register(AssessmentAttempt)
class AssessmentAttemptAdmin(admin.ModelAdmin):
    list_display = ['student', 'assessment', 'score', 'percentage', 'skill_level', 'attempted_at']
    list_filter = ['skill_level']
