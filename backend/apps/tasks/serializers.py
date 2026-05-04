"""
Serializers for Task and TaskAssignment models.
"""

from rest_framework import serializers
from .models import (
    Task, TaskAssignment, TaskMCQ, TaskCompletion, 
    TaskMCQAttempt, TaskEvaluation
)
from apps.portfolios.models import Portfolio, PortfolioItem


class TaskSerializer(serializers.ModelSerializer):
    """Serializer for Task list/detail views."""
    created_by_name = serializers.CharField(source='created_by.name', read_only=True)

    class Meta:
        model = Task
        fields = [
            'id', 'title', 'description', 'domain', 'difficulty',
            'task_type', 'required_skills', 'learning_outcomes',
            'estimated_duration', 'is_active', 'created_by_name',
            'created_at', 'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'created_by_name']


class TaskCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating tasks (admin/mentor only)."""

    class Meta:
        model = Task
        fields = [
            'title', 'description', 'domain', 'difficulty',
            'task_type', 'required_skills', 'learning_outcomes',
            'estimated_duration', 'is_active',
        ]


class TaskAssignmentSerializer(serializers.ModelSerializer):
    """Serializer for TaskAssignment list/detail."""
    task_title = serializers.CharField(source='task.title', read_only=True)
    task_domain = serializers.CharField(source='task.domain', read_only=True)
    task_difficulty = serializers.CharField(source='task.difficulty', read_only=True)
    student_name = serializers.CharField(source='student.name', read_only=True)
    assigned_by_name = serializers.CharField(source='assigned_by.name', read_only=True)
    task_details = TaskSerializer(source='task', read_only=True)

    class Meta:
        model = TaskAssignment
        fields = [
            'id', 'student', 'student_name', 'task', 'task_title',
            'task_details', 'task_domain', 'task_difficulty',
            'assigned_by', 'assigned_by_name', 'status',
            'progress_percentage', 'recommended_score',
            'recommendation_reason', 'mentor_review_requested',
            'mentor_review_status', 'mentor_feedback',
            'created_at', 'accepted_at', 'started_at',
            'completed_at', 'updated_at',
        ]
        read_only_fields = [
            'id', 'assigned_by', 'accepted_at', 'started_at',
            'completed_at', 'created_at', 'updated_at',
            'task_title', 'task_domain', 'task_difficulty',
            'student_name', 'assigned_by_name', 'task_details',
        ]


class TaskAssignmentUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating task assignment status/progress."""

    class Meta:
        model = TaskAssignment
        fields = ['status', 'progress_percentage', 'mentor_review_requested']


class TaskAssignmentAcceptSerializer(serializers.Serializer):
    """Serializer for accepting a recommended task."""
    accept = serializers.BooleanField(required=True)

    def validate_accept(self, value):
        if not isinstance(value, bool):
            raise serializers.ValidationError("Accept must be a boolean value.")
        return value


class RecommendedTaskSerializer(serializers.ModelSerializer):
    """
    Serializer for recommended tasks with recommendation details.
    Includes assignment info if already assigned.
    """
    task_title = serializers.CharField(source='task.title', read_only=True)
    task_domain = serializers.CharField(source='task.domain', read_only=True)
    task_difficulty = serializers.CharField(source='task.difficulty', read_only=True)
    task_details = TaskSerializer(source='task', read_only=True)
    is_accepted = serializers.SerializerMethodField()

    class Meta:
        model = TaskAssignment
        fields = [
            'id', 'task', 'task_title', 'task_domain', 'task_difficulty',
            'task_details', 'recommended_score', 'recommendation_reason',
            'recommendation_explanation',
            'status', 'is_accepted', 'created_at',
        ]
        read_only_fields = fields

    def get_is_accepted(self, obj):
        return obj.status != 'recommended'


class MentorTaskReviewSerializer(serializers.ModelSerializer):
    """Serializer for mentor to review tasks."""
    task_title = serializers.CharField(source='task.title', read_only=True)
    student_name = serializers.CharField(source='student.name', read_only=True)

    class Meta:
        model = TaskAssignment
        fields = [
            'id', 'student', 'student_name', 'task', 'task_title',
            'status', 'progress_percentage', 'mentor_review_requested',
            'mentor_review_status', 'mentor_feedback', 'completed_at',
        ]
        read_only_fields = [
            'id', 'student', 'student_name', 'task', 'task_title',
            'status', 'progress_percentage', 'mentor_review_requested',
            'completed_at',
        ]


class MentorFeedbackSubmitSerializer(serializers.Serializer):
    """Serializer for submitting mentor feedback on a task."""
    mentor_feedback = serializers.CharField(max_length=1000, required=True)
    mentor_review_status = serializers.ChoiceField(
        choices=['approved', 'needs_revision'],
        required=True
    )


class TaskMCQSerializer(serializers.ModelSerializer):
    """Serializer for TaskMCQ with all options and answers."""

    class Meta:
        model = TaskMCQ
        fields = [
            'id', 'task', 'question_text', 'difficulty',
            'option_a', 'option_b', 'option_c', 'option_d',
            'explanation', 'order',
        ]
        read_only_fields = ['id', 'task']


class TaskMCQWithAnswerSerializer(serializers.ModelSerializer):
    """Serializer for TaskMCQ used in quiz (includes correct answer for grading)."""

    class Meta:
        model = TaskMCQ
        fields = [
            'id', 'question_text', 'difficulty',
            'option_a', 'option_b', 'option_c', 'option_d',
            'correct_answer', 'explanation', 'order',
        ]
        read_only_fields = fields


class TaskCompletionSerializer(serializers.ModelSerializer):
    """Serializer for TaskCompletion."""
    task_title = serializers.CharField(
        source='task_assignment.task.title',
        read_only=True
    )
    student_name = serializers.CharField(
        source='task_assignment.student.name',
        read_only=True
    )

    class Meta:
        model = TaskCompletion
        fields = [
            'id', 'task_assignment', 'task_title', 'student_name',
            'reflective_text', 'completed_at', 'is_submitted',
            'created_at', 'updated_at',
        ]
        read_only_fields = [
            'id', 'task_assignment', 'task_title', 'student_name',
            'completed_at', 'created_at', 'updated_at',
        ]


class TaskCompletionCreateSerializer(serializers.Serializer):
    """Serializer for completing a task."""
    reflective_text = serializers.CharField(
        max_length=2000,
        required=False,
        allow_blank=True,
        help_text='Student\'s reflection on what they learned'
    )


class TaskMCQAttemptSerializer(serializers.ModelSerializer):
    """Serializer for MCQ quiz attempt (submission)."""

    class Meta:
        model = TaskMCQAttempt
        fields = [
            'id', 'task_completion', 'student_answers', 'total_questions',
            'correct_answers', 'mcq_score', 'duration_seconds',
            'is_submitted', 'started_at', 'submitted_at', 'created_at',
        ]
        read_only_fields = [
            'id', 'task_completion', 'total_questions', 'correct_answers',
            'mcq_score', 'is_submitted', 'started_at', 'submitted_at', 'created_at',
        ]


class TaskMCQAttemptSubmitSerializer(serializers.Serializer):
    """Serializer for submitting MCQ answers."""
    student_answers = serializers.JSONField(
        help_text='Answers in format: {question_id: "A", question_id: "B", ...}'
    )
    duration_seconds = serializers.IntegerField(
        required=False,
        default=0,
        help_text='Time taken to complete quiz in seconds'
    )


class TaskEvaluationSerializer(serializers.ModelSerializer):
    """Serializer for TaskEvaluation with all scoring components."""
    task_title = serializers.CharField(
        source='task_completion.task_assignment.task.title',
        read_only=True
    )
    student_name = serializers.CharField(
        source='task_completion.task_assignment.student.name',
        read_only=True
    )
    evaluated_by_name = serializers.CharField(
        source='evaluated_by.name',
        read_only=True
    )

    class Meta:
        model = TaskEvaluation
        fields = [
            'id', 'task_completion', 'task_title', 'student_name',
            'mcq_score', 'mentor_score', 'final_score',
            'mentor_feedback', 'strengths', 'weaknesses', 'suggestions',
            'status', 'evaluated_by', 'evaluated_by_name',
            'evaluated_at', 'created_at', 'updated_at',
        ]
        read_only_fields = [
            'id', 'task_completion', 'task_title', 'student_name',
            'mcq_score', 'final_score', 'evaluated_by_name',
            'created_at', 'updated_at',
        ]


class TaskEvaluationCreationSerializer(serializers.Serializer):
    """Serializer for creating initial evaluation after MCQ completion."""
    pass


class TaskEvaluationUpdateSerializer(serializers.Serializer):
    """Serializer for mentor to update evaluation with manual feedback."""
    mentor_score = serializers.FloatField(
        min_value=0.0,
        max_value=100.0,
        required=True,
        help_text='Manual score from mentor (0-100)'
    )
    mentor_feedback = serializers.CharField(
        max_length=2000,
        required=False,
        allow_blank=True,
        help_text='Detailed feedback from mentor'
    )
    strengths = serializers.ListField(
        child=serializers.CharField(max_length=500),
        required=False,
        help_text='List of strengths demonstrated'
    )
    weaknesses = serializers.ListField(
        child=serializers.CharField(max_length=500),
        required=False,
        help_text='List of areas for improvement'
    )
    suggestions = serializers.ListField(
        child=serializers.CharField(max_length=500),
        required=False,
        help_text='List of suggestions for improvement'
    )


class PortfolioItemSerializer(serializers.ModelSerializer):
    """Serializer for PortfolioItem with all details."""

    class Meta:
        model = PortfolioItem
        fields = [
            'id', 'portfolio', 'task_title', 'task_domain', 'task_difficulty',
            'task_type', 'completion_date', 'evaluation_date', 'mcq_score',
            'mentor_score', 'final_score', 'skills_demonstrated',
            'student_reflection', 'project_summary', 'mentor_feedback_summary',
            'strengths_summary', 'is_featured', 'display_order', 'created_at',
        ]
        read_only_fields = [
            'id', 'portfolio', 'completion_date', 'evaluation_date',
            'mcq_score', 'mentor_score', 'final_score', 'created_at',
            'project_summary', 'mentor_feedback_summary', 'strengths_summary',
        ]


class PortfolioItemDetailSerializer(serializers.ModelSerializer):
    """Detailed serializer for single portfolio item display."""

    class Meta:
        model = PortfolioItem
        fields = [
            'id', 'task_title', 'task_domain', 'task_difficulty', 'task_type',
            'completion_date', 'evaluation_date', 'mcq_score', 'mentor_score',
            'final_score', 'skills_demonstrated', 'student_reflection',
            'project_summary', 'mentor_feedback_summary', 'strengths_summary',
            'is_featured', 'display_order',
        ]
        read_only_fields = fields


class PortfolioItemCreateSerializer(serializers.Serializer):
    """Serializer for creating portfolio items (internal use)."""
    task_evaluation_id = serializers.IntegerField(required=True)


class PortfolioSerializer(serializers.ModelSerializer):
    """Serializer for Portfolio with summary info."""
    student_name = serializers.CharField(source='user.name', read_only=True)
    items_count = serializers.SerializerMethodField()

    class Meta:
        model = Portfolio
        fields = [
            'id', 'user', 'student_name', 'title', 'bio', 'is_public',
            'total_items', 'average_score', 'items_count', 'created_at', 'updated_at',
        ]
        read_only_fields = [
            'id', 'user', 'student_name', 'total_items', 'average_score',
            'created_at', 'updated_at',
        ]

    def get_items_count(self, obj):
        return obj.items.count()


class PortfolioDetailSerializer(serializers.ModelSerializer):
    """Detailed portfolio serializer with all items."""
    student_name = serializers.CharField(source='user.name', read_only=True)
    items = PortfolioItemSerializer(many=True, read_only=True)

    class Meta:
        model = Portfolio
        fields = [
            'id', 'user', 'student_name', 'title', 'bio', 'is_public',
            'total_items', 'average_score', 'items', 'created_at', 'updated_at',
        ]
        read_only_fields = [
            'id', 'user', 'student_name', 'total_items', 'average_score',
            'items', 'created_at', 'updated_at',
        ]


class PortfolioUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating portfolio info."""

    class Meta:
        model = Portfolio
        fields = ['title', 'bio', 'is_public']


class PortfolioItemUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating portfolio item display settings."""

    class Meta:
        model = PortfolioItem
        fields = ['is_featured', 'display_order']


