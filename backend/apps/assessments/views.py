"""
Assessment views – student-protected endpoints.
"""

from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from apps.core.permissions import IsStudent
from .models import Assessment, Question, AssessmentAttempt
from .serializers import (
    AssessmentListSerializer,
    AssessmentDetailSerializer,
    SubmitAnswersSerializer,
    AttemptResultSerializer,
)
from .recommendation import generate_recommendation, calculate_performance_breakdown
from .nlp_feedback import generate_feedback
from .evaluation_engine import evaluate as run_evaluation
from apps.tasks.ml_engine import StudentClusterer


class AssessmentListView(APIView):
    """
    GET /api/assessments/
    Student-only: lists active assessments.
    """
    permission_classes = [IsAuthenticated, IsStudent]

    def get(self, request):
        assessments = Assessment.objects.filter(is_active=True)
        serializer = AssessmentListSerializer(assessments, many=True)
        return Response({'success': True, 'data': serializer.data})


class AssessmentDetailView(APIView):
    """
    GET /api/assessments/<id>/
    Student-only: returns assessment with questions (no correct answers).
    """
    permission_classes = [IsAuthenticated, IsStudent]

    def get(self, request, pk):
        try:
            assessment = Assessment.objects.get(pk=pk)
            if not assessment.is_active:
                raise Assessment.DoesNotExist
        except Assessment.DoesNotExist:
            return Response(
                {'success': False, 'error': {'code': 404, 'message': 'Assessment not found.'}},
                status=status.HTTP_404_NOT_FOUND,
            )
        serializer = AssessmentDetailSerializer(assessment)
        return Response({'success': True, 'data': serializer.data})


class SubmitAssessmentView(APIView):
    """
    POST /api/assessments/<id>/submit
    Student-only: submit answers, calculate score, save attempt, return recommendation.

    Sequence (matches sequence diagram):
      1. Receive answers from student via WebInterface
      2. Validate answers
      3. Calculate score (AI Evaluation Engine - simplified)
      4. Generate recommendation
      5. Store attempt in DB
      6. Return result to student
    """
    permission_classes = [IsAuthenticated, IsStudent]

    def post(self, request, pk):
        # 1) Fetch assessment
        try:
            assessment = Assessment.objects.get(pk=pk)
            if not assessment.is_active:
                raise Assessment.DoesNotExist
        except Assessment.DoesNotExist:
            return Response(
                {'success': False, 'error': {'code': 404, 'message': 'Assessment not found.'}},
                status=status.HTTP_404_NOT_FOUND,
            )

        # 2) Validate input
        serializer = SubmitAnswersSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        submitted_answers = serializer.validated_data['answers']

        # 3 + 4) Run full evaluation engine
        # Returns concept scores, weighted domain score, readiness level,
        # skill profile vector, improvement delta, tags, and next step.
        questions = list(Question.objects.filter(assessment=assessment))
        total = len(questions)

        if total == 0:
            return Response(
                {'success': False, 'error': {'code': 400, 'message': 'This assessment has no questions.'}},
                status=status.HTTP_400_BAD_REQUEST,
            )

        eval_result = run_evaluation(assessment, questions, submitted_answers, request.user)

        percentage   = eval_result['percentage']
        correct      = eval_result['total_score']
        skill_level  = eval_result['skill_level']

        # 4b) Domain-level recommendation (existing rules engine, unchanged)
        recommendation = generate_recommendation(assessment.domain, percentage)
        next_steps = recommendation.get('improvement_areas', [])
        if eval_result['recommended_next_step']:
            next_steps = [eval_result['recommended_next_step']] + next_steps

        # 4.6) NLP-generated feedback paragraph (local, no external API)
        previous_attempts = AssessmentAttempt.objects.filter(
            student=request.user,
            assessment__domain=assessment.domain,
        ).order_by('-attempted_at')

        attempt_number = previous_attempts.count() + 1
        previous_percentage = None
        if previous_attempts.exists():
            previous_percentage = float(previous_attempts.first().percentage)

        nlp_feedback = generate_feedback(
            domain=assessment.domain,
            percentage=percentage,
            skill_level=skill_level,
            correct_count=correct,
            total_count=total,
            strengths=eval_result['strength_tags'],
            weaknesses=eval_result['weakness_tags'],
            improvement_areas=next_steps,
            attempt_number=attempt_number,
            previous_percentage=previous_percentage,
        )

        # 5) Persist attempt with all structured evaluation fields
        attempt = AssessmentAttempt.objects.create(
            student=request.user,
            assessment=assessment,
            answers=submitted_answers,
            score=correct,
            total_questions=total,
            percentage=percentage,
            skill_level=skill_level,
            recommended_domains=[recommendation],
            detailed_breakdown=eval_result['detailed_breakdown'],
            strengths=eval_result['strengths'],
            weaknesses=eval_result['weaknesses'],
            next_steps=next_steps,
            # new rich fields
            concept_scores=eval_result['concept_scores'],
            domain_score=eval_result['domain_score'],
            readiness_level=eval_result['readiness_level'],
            skill_profile_vector=eval_result['skill_profile_vector'],
            improvement_delta=eval_result['improvement_delta'],
            recommended_task_type=eval_result['recommended_task_type'],
        )

        # 5.1) Update student cluster (async-safe — must not block submission)
        try:
            StudentClusterer.update_student_cluster(request.user)
        except Exception:
            pass

        # 6) Return result
        result = AttemptResultSerializer(attempt).data
        result['recommendation'] = recommendation
        result['feedback'] = nlp_feedback

        return Response(
            {
                'success': True,
                'message': 'Assessment submitted successfully.',
                'data': result,
            },
            status=status.HTTP_201_CREATED,
        )


class AttemptDetailView(APIView):
    """
    GET /api/assessments/attempts/<id>/
    Student-only: view a past attempt's result.
    """
    permission_classes = [IsAuthenticated, IsStudent]

    def get(self, request, pk):
        try:
            attempt = AssessmentAttempt.objects.get(pk=pk, student=request.user)
        except AssessmentAttempt.DoesNotExist:
            return Response(
                {'success': False, 'error': {'code': 404, 'message': 'Attempt not found.'}},
                status=status.HTTP_404_NOT_FOUND,
            )
        result = AttemptResultSerializer(attempt).data
        # Re-attach recommendation from stored data
        if attempt.recommended_domains:
            result['recommendation'] = attempt.recommended_domains[0]
        return Response({'success': True, 'data': result})


class StudentAttemptsListView(APIView):
    """
    GET /api/assessments/my-attempts/
    Student-only: lists all past attempts for the logged-in student.
    """
    permission_classes = [IsAuthenticated, IsStudent]

    def get(self, request):
        attempts = AssessmentAttempt.objects.filter(student=request.user)
        serializer = AttemptResultSerializer(attempts, many=True)
        return Response({'success': True, 'data': serializer.data})
