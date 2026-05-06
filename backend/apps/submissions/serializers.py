"""
Serializers for the Submissions app (FR4: Automated Text Evaluation).
"""

from rest_framework import serializers
from .models import Submission, AIEvaluation, MentorEvaluation


class AIEvaluationSerializer(serializers.ModelSerializer):
    class Meta:
        model = AIEvaluation
        fields = [
            'id', 'ai_score', 'readability_score', 'vocabulary_diversity',
            'grammar_score', 'originality_score', 'word_count', 'sentence_count',
            'readiness_label', 'feedback', 'strengths', 'improvements',
            'grammar_issues', 'generated_at',
        ]


class MentorEvaluationSerializer(serializers.ModelSerializer):
    mentor_name = serializers.CharField(source='mentor.name', read_only=True)

    class Meta:
        model = MentorEvaluation
        fields = ['id', 'mentor_name', 'final_score', 'feedback', 'evaluated_at']


class SubmissionSerializer(serializers.ModelSerializer):
    ai_evaluation = AIEvaluationSerializer(read_only=True)
    mentor_evaluation = MentorEvaluationSerializer(read_only=True)
    submitted_by_name = serializers.CharField(source='submitted_by.name', read_only=True)

    class Meta:
        model = Submission
        fields = [
            'id', 'assignment', 'submitted_by_name', 'submission_type',
            'text_content', 'notes', 'submitted_at',
            'ai_evaluation', 'mentor_evaluation',
        ]
        read_only_fields = ['submitted_at']


class SubmitTextSerializer(serializers.Serializer):
    """Input serializer for text submission."""
    assignment_id = serializers.IntegerField()
    text_content = serializers.CharField(
        min_length=10,
        max_length=20000,
        error_messages={
            'min_length': 'Submission must be at least 10 characters.',
            'max_length': 'Submission must not exceed 20,000 characters.',
        },
    )
    notes = serializers.CharField(required=False, allow_blank=True, max_length=500)
