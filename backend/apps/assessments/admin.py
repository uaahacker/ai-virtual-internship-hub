from django.contrib import admin
from .models import Assessment, Question, AssessmentAttempt


class QuestionInline(admin.TabularInline):
    model = Question
    extra = 1
    fields = ['order', 'text', 'correct_option', 'concept', 'difficulty_weight']
    readonly_fields = []
    show_change_link = True


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ['__str__', 'assessment', 'concept', 'difficulty_weight', 'correct_option']
    list_editable = ['concept', 'difficulty_weight']
    list_filter = ['assessment__domain', 'concept']
    search_fields = ['text', 'concept', 'assessment__title']
    ordering = ['assessment', 'order']
    fields = [
        'assessment', 'order', 'text',
        'option_a', 'option_b', 'option_c', 'option_d', 'correct_option',
        'concept', 'difficulty_weight',
    ]
    actions = ['clear_concepts', 'reset_difficulty_weights']

    @admin.action(description='Clear concept tags on selected questions')
    def clear_concepts(self, request, queryset):
        updated = queryset.update(concept='')
        self.message_user(request, f'{updated} question(s) had their concept cleared.')

    @admin.action(description='Reset difficulty weights to 1.0')
    def reset_difficulty_weights(self, request, queryset):
        updated = queryset.update(difficulty_weight=1.0)
        self.message_user(request, f'{updated} question(s) reset to weight 1.0.')


@admin.register(Assessment)
class AssessmentAdmin(admin.ModelAdmin):
    list_display = ['title', 'domain', 'is_active', 'created_at']
    list_filter = ['domain', 'is_active']
    inlines = [QuestionInline]


@admin.register(AssessmentAttempt)
class AssessmentAttemptAdmin(admin.ModelAdmin):
    list_display = [
        'student', 'assessment', 'score', 'percentage',
        'domain_score', 'readiness_level', 'skill_level',
        'improvement_delta', 'recommended_task_type', 'attempted_at',
    ]
    list_filter = ['skill_level', 'readiness_level', 'recommended_task_type', 'assessment__domain']
    search_fields = ['student__name', 'student__email', 'assessment__title']
    readonly_fields = [
        'student', 'assessment', 'answers',
        'score', 'total_questions', 'percentage',
        'domain_score', 'readiness_level',
        'concept_scores', 'skill_profile_vector',
        'improvement_delta', 'recommended_task_type',
        'strengths', 'weaknesses', 'skill_level',
        'recommended_domains', 'detailed_breakdown',
        'next_steps', 'attempted_at',
    ]
    fieldsets = [
        ('Submission', {
            'fields': ['student', 'assessment', 'answers', 'attempted_at'],
        }),
        ('Core Scores', {
            'fields': ['score', 'total_questions', 'percentage', 'domain_score'],
        }),
        ('Readiness & Skill', {
            'fields': ['readiness_level', 'skill_level', 'improvement_delta', 'recommended_task_type'],
        }),
        ('Concept Analysis', {
            'fields': ['concept_scores', 'skill_profile_vector'],
            'classes': ['collapse'],
        }),
        ('Recommendations', {
            'fields': ['recommended_domains', 'strengths', 'weaknesses', 'next_steps'],
            'classes': ['collapse'],
        }),
        ('Detailed Breakdown', {
            'fields': ['detailed_breakdown'],
            'classes': ['collapse'],
        }),
    ]
