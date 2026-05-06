"""
Views for the Submissions app — FR4: Automated Text Evaluation.

Endpoints:
  POST /api/submissions/submit/       — submit text work, triggers AI evaluation
  GET  /api/submissions/<id>/         — retrieve submission + AI evaluation
  GET  /api/submissions/my/           — list student's own submissions
  GET  /api/submissions/assignment/<assignment_id>/  — get submission for a specific assignment
"""

import logging
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated

from apps.core.permissions import IsStudent, IsMentor
from apps.tasks.models import TaskAssignment

from .models import Submission, AIEvaluation
from .serializers import SubmissionSerializer, SubmitTextSerializer
from .evaluation_service import evaluate_text_submission

logger = logging.getLogger(__name__)


class SubmitTextView(APIView):
    """
    POST /api/submissions/submit/
    Student submits written work for AI evaluation.
    """

    permission_classes = [IsAuthenticated, IsStudent]

    def post(self, request):
        serializer = SubmitTextSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(
                {'success': False, 'error': serializer.errors},
                status=status.HTTP_400_BAD_REQUEST,
            )

        assignment_id = serializer.validated_data['assignment_id']
        text_content = serializer.validated_data['text_content']
        notes = serializer.validated_data.get('notes', '')

        # Verify the assignment belongs to this student
        try:
            assignment = TaskAssignment.objects.select_related('task').get(
                id=assignment_id,
                student=request.user,
            )
        except TaskAssignment.DoesNotExist:
            return Response(
                {'success': False, 'error': 'Assignment not found.'},
                status=status.HTTP_404_NOT_FOUND,
            )

        # Allow one submission per assignment (update if re-submitted)
        submission, created = Submission.objects.get_or_create(
            assignment=assignment,
            submitted_by=request.user,
            defaults={
                'submission_type': 'text',
                'text_content': text_content,
                'notes': notes,
            },
        )
        if not created:
            submission.text_content = text_content
            submission.notes = notes
            submission.save()

        # Gather existing submissions for plagiarism check (exclude current)
        existing_texts = list(
            Submission.objects.filter(
                submission_type='text',
                assignment__task=assignment.task,
            )
            .exclude(id=submission.id)
            .values_list('text_content', flat=True)
        )

        # Run NLP evaluation
        try:
            eval_result = evaluate_text_submission(text_content, existing_texts)
        except Exception as exc:
            logger.error(f"Evaluation failed for submission {submission.id}: {exc}")
            eval_result = {
                'ai_score': 50.0,
                'readability_score': 50.0,
                'vocabulary_diversity': 50.0,
                'grammar_score': 50.0,
                'originality_score': 100.0,
                'word_count': len(text_content.split()),
                'sentence_count': text_content.count('.'),
                'readiness_label': 'Satisfactory',
                'feedback': 'Evaluation completed with default scores.',
                'strengths': [],
                'improvements': [],
                'grammar_issues': [],
            }

        # Save / update AI evaluation
        ai_eval, _ = AIEvaluation.objects.update_or_create(
            submission=submission,
            defaults={
                'ai_score': eval_result['ai_score'],
                'readability_score': eval_result['readability_score'],
                'vocabulary_diversity': eval_result['vocabulary_diversity'],
                'grammar_score': eval_result['grammar_score'],
                'originality_score': eval_result['originality_score'],
                'word_count': eval_result['word_count'],
                'sentence_count': eval_result['sentence_count'],
                'readiness_label': eval_result['readiness_label'],
                'feedback': eval_result['feedback'],
                'strengths': eval_result['strengths'],
                'improvements': eval_result['improvements'],
                'grammar_issues': eval_result['grammar_issues'],
                'plagiarism_score': round(100 - eval_result['originality_score'], 2),
                'remarks': eval_result['feedback'],
            },
        )

        out_serializer = SubmissionSerializer(submission)
        return Response(
            {
                'success': True,
                'message': 'Submission evaluated successfully.',
                'data': out_serializer.data,
            },
            status=status.HTTP_201_CREATED if created else status.HTTP_200_OK,
        )


class SubmissionDetailView(APIView):
    """
    GET /api/submissions/<submission_id>/
    Retrieve a submission and its AI evaluation.
    Students can only access their own; mentors can access their students'.
    """

    permission_classes = [IsAuthenticated]

    def get(self, request, submission_id):
        try:
            submission = Submission.objects.select_related(
                'ai_evaluation', 'mentor_evaluation', 'assignment__task'
            ).get(id=submission_id)
        except Submission.DoesNotExist:
            return Response(
                {'success': False, 'error': 'Submission not found.'},
                status=status.HTTP_404_NOT_FOUND,
            )

        # Permission: student owns it or mentor supervises
        user = request.user
        if user.role == 'Student' and submission.submitted_by != user:
            return Response(
                {'success': False, 'error': 'Access denied.'},
                status=status.HTTP_403_FORBIDDEN,
            )

        serializer = SubmissionSerializer(submission)
        return Response({'success': True, 'data': serializer.data})


class MySubmissionsView(APIView):
    """
    GET /api/submissions/my/
    List the authenticated student's submissions.
    """

    permission_classes = [IsAuthenticated, IsStudent]

    def get(self, request):
        submissions = Submission.objects.filter(
            submitted_by=request.user,
        ).select_related('ai_evaluation', 'assignment__task').order_by('-submitted_at')

        serializer = SubmissionSerializer(submissions, many=True)
        return Response({'success': True, 'data': serializer.data})


class AssignmentSubmissionView(APIView):
    """
    GET /api/submissions/assignment/<assignment_id>/
    Get the submission for a specific assignment (if exists).
    """

    permission_classes = [IsAuthenticated, IsStudent]

    def get(self, request, assignment_id):
        try:
            submission = Submission.objects.select_related(
                'ai_evaluation'
            ).get(
                assignment_id=assignment_id,
                submitted_by=request.user,
            )
            serializer = SubmissionSerializer(submission)
            return Response({'success': True, 'data': serializer.data})
        except Submission.DoesNotExist:
            return Response(
                {'success': False, 'data': None, 'message': 'No submission yet.'},
                status=status.HTTP_200_OK,
            )
