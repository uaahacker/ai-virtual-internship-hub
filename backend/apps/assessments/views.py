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
from .recommendation import generate_recommendation


class AssessmentListView(APIView):
    """
    GET /api/assessments/
    Student-only: lists active assessments.
    """
    permission_classes = [IsAuthenticated, IsStudent]

    def get(self, request):
        # NOTE: Djongo cannot filter on BooleanField directly, so filter in Python
        assessments = [a for a in Assessment.objects.all() if a.is_active]
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

        # 3) Calculate score
        questions = list(Question.objects.filter(assessment=assessment))
        total = len(questions)

        if total == 0:
            return Response(
                {'success': False, 'error': {'code': 400, 'message': 'This assessment has no questions.'}},
                status=status.HTTP_400_BAD_REQUEST,
            )

        correct = 0
        for question in questions:
            submitted = submitted_answers.get(str(question.id))
            if submitted and submitted == question.correct_option:
                correct += 1

        percentage = (correct / total) * 100

        # 4) Generate recommendation
        recommendation = generate_recommendation(assessment.domain, percentage)
        skill_level = recommendation['skill_level']

        # 5) Store attempt
        attempt = AssessmentAttempt.objects.create(
            student=request.user,
            assessment=assessment,
            answers=submitted_answers,
            score=correct,
            total_questions=total,
            percentage=round(percentage, 2),
            skill_level=skill_level,
            recommended_domains=[recommendation],
        )

        # 6) Return result
        result = AttemptResultSerializer(attempt).data
        result['recommendation'] = recommendation

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
