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
    """
    Full assessment with questions (no correct answers exposed).

    When AdaptiveTesting pre-computes an ordering it stores the sorted list
    on the instance as ``_adaptive_questions``.  We serve those; otherwise
    fall back to the default ``order`` field ordering.
    """
    questions = serializers.SerializerMethodField()

    class Meta:
        model = Assessment
        fields = ['id', 'title', 'domain', 'description', 'time_limit', 'questions']

    def get_questions(self, obj):
        qs = getattr(obj, '_adaptive_questions', None)
        if qs is None:
            qs = obj.questions.all()
        return QuestionListSerializer(qs, many=True).data


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
            'detailed_breakdown', 'strengths', 'weaknesses', 'next_steps',
            # rich evaluation fields
            'domain_score', 'readiness_level',
            'concept_scores', 'skill_profile_vector',
            'improvement_delta', 'recommended_task_type',
            # NLP feedback
            'feedback',
        ]
        read_only_fields = fields


class AttemptDetailedSerializer(serializers.ModelSerializer):
    """Detailed result including question-by-question analysis and recommendations."""
    assessment_title = serializers.CharField(source='assessment.title', read_only=True)
    assessment_domain = serializers.CharField(source='assessment.domain', read_only=True)

    class Meta:
        model = AssessmentAttempt
        fields = [
            'id', 'assessment', 'assessment_title', 'assessment_domain',
            'score', 'total_questions', 'percentage',
            'skill_level', 'recommended_domains', 'attempted_at',
            'detailed_breakdown', 'strengths', 'weaknesses', 'next_steps',
            # rich evaluation fields
            'domain_score', 'readiness_level',
            'concept_scores', 'skill_profile_vector',
            'improvement_delta', 'recommended_task_type',
        ]
        read_only_fields = fields
