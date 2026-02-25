"""
Serializers for the assessments app.
"""

from rest_framework import serializers
from .models import Assessment, Question, AssessmentAttempt


class QuestionListSerializer(serializers.ModelSerializer):
    """Questions displayed to students (without correct answer)."""
    options = serializers.SerializerMethodField()

    class Meta:
        model = Question
        fields = ['id', 'text', 'options', 'order']

    def get_options(self, obj):
        return obj.get_options()


class AssessmentListSerializer(serializers.ModelSerializer):
    """Summary representation for assessment list."""
    question_count = serializers.SerializerMethodField()

    class Meta:
        model = Assessment
        fields = ['id', 'title', 'domain', 'description', 'time_limit', 'question_count']

    def get_question_count(self, obj):
        return Question.objects.filter(assessment=obj).count()


class AssessmentDetailSerializer(serializers.ModelSerializer):
    """Full assessment with questions (no correct answers exposed)."""
    questions = QuestionListSerializer(many=True, read_only=True)

    class Meta:
        model = Assessment
        fields = ['id', 'title', 'domain', 'description', 'time_limit', 'questions']


class SubmitAnswersSerializer(serializers.Serializer):
    """
    Input: { "answers": { "<question_id>": "A", ... } }
    """
    answers = serializers.DictField(
        child=serializers.CharField(max_length=1),
        help_text='Map of question_id -> selected option (A/B/C/D)',
    )

    def validate_answers(self, value):
        if not value:
            raise serializers.ValidationError('Answers cannot be empty.')
        valid_options = {'A', 'B', 'C', 'D'}
        for qid, option in value.items():
            if option.upper() not in valid_options:
                raise serializers.ValidationError(
                    f'Invalid option "{option}" for question {qid}. Must be A, B, C, or D.'
                )
        return {k: v.upper() for k, v in value.items()}


class AttemptResultSerializer(serializers.ModelSerializer):
    """Read-only result returned after submission."""
    assessment_title = serializers.CharField(source='assessment.title', read_only=True)
    assessment_domain = serializers.CharField(source='assessment.domain', read_only=True)

    class Meta:
        model = AssessmentAttempt
        fields = [
            'id', 'assessment', 'assessment_title', 'assessment_domain',
            'score', 'total_questions', 'percentage',
            'skill_level', 'recommended_domains', 'attempted_at',
        ]
        read_only_fields = fields
