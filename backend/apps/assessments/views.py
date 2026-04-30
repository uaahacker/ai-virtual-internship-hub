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

        # 4.5) Calculate detailed breakdown and analysis
        detailed_breakdown = calculate_performance_breakdown(questions, submitted_answers)
        
        # Calculate strengths and weaknesses based on performance
        correct_questions = [
            q for q in questions 
            if submitted_answers.get(str(q.id)) == q.correct_option
        ]
        incorrect_questions = [
            q for q in questions 
            if submitted_answers.get(str(q.id)) != q.correct_option
        ]
        
        strengths = [
            f"Correctly answered {len(correct_questions)} out of {total} questions"
        ]
        if correct_questions:
            strengths.append(
                f"Strong grasp of core concepts ({(len(correct_questions)/total)*100:.0f}% accuracy)"
            )
        
        weaknesses = []
        if incorrect_questions:
            weak_pct = (len(incorrect_questions) / total) * 100
            weaknesses.append(
                f"Need improvement in {len(incorrect_questions)} areas ({weak_pct:.0f}% of questions)"
            )
            if skill_level == 'Advanced':
                weaknesses.append("Focus on the few challenging areas to maintain excellence")
            elif skill_level == 'Intermediate':
                weaknesses.append("Review the concepts you found challenging")
            else:
                weaknesses.append("Prioritize studying the fundamental concepts you missed")
        
        next_steps = recommendation.get('improvement_areas', [])
        
        # 5) Store attempt with detailed analysis
        attempt = AssessmentAttempt.objects.create(
            student=request.user,
            assessment=assessment,
            answers=submitted_answers,
            score=correct,
            total_questions=total,
            percentage=round(percentage, 2),
            skill_level=skill_level,
            recommended_domains=[recommendation],
            detailed_breakdown=detailed_breakdown,
            strengths=strengths,
            weaknesses=weaknesses,
            next_steps=next_steps,
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
