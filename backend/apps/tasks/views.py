"""
Views for Task and TaskAssignment endpoints.
"""

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone

from apps.core.permissions import IsStudent, IsMentor, IsAdmin
from .models import Task, TaskAssignment, TaskMCQ, TaskCompletion, TaskMCQAttempt, TaskEvaluation
from apps.portfolios.models import Portfolio, PortfolioItem
from .serializers import (
    TaskSerializer,
    TaskCreateSerializer,
    TaskAssignmentSerializer,
    TaskAssignmentUpdateSerializer,
    TaskAssignmentAcceptSerializer,
    RecommendedTaskSerializer,
    TaskMCQSerializer,
    TaskCompletionSerializer,
    TaskCompletionCreateSerializer,
    TaskMCQAttemptSerializer,
    TaskMCQAttemptSubmitSerializer,
    TaskEvaluationSerializer,
    TaskEvaluationUpdateSerializer,
    PortfolioSerializer,
    PortfolioDetailSerializer,
    PortfolioUpdateSerializer,
    PortfolioItemSerializer,
    PortfolioItemDetailSerializer,
    PortfolioItemUpdateSerializer,
)
from .recommendation_service import TaskRecommendationService
from .portfolio_service import PortfolioService


class TaskListView(APIView):
    permission_classes = [IsAuthenticated, IsStudent]

    def get(self, request):
        domain_filter = request.query_params.get('domain')
        difficulty_filter = request.query_params.get('difficulty')
        tasks = Task.objects.filter(is_active=True)
        if domain_filter:
            tasks = tasks.filter(domain=domain_filter)
        if difficulty_filter:
            tasks = tasks.filter(difficulty=difficulty_filter)
        serializer = TaskSerializer(tasks, many=True)
        return Response({'success': True, 'data': serializer.data})


class TaskDetailView(APIView):
    permission_classes = [IsAuthenticated, IsStudent]

    def get(self, request, pk):
        try:
            task = Task.objects.get(pk=pk, is_active=True)
        except Task.DoesNotExist:
            return Response({'success': False, 'error': 'Task not found.'}, status=status.HTTP_404_NOT_FOUND)
        serializer = TaskSerializer(task)
        return Response({'success': True, 'data': serializer.data})


class TaskCreateView(APIView):
    permission_classes = [IsAuthenticated, IsMentor]

    def post(self, request):
        serializer = TaskCreateSerializer(data=request.data)
        if not serializer.is_valid():
            return Response({'success': False, 'error': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
        task = serializer.save(created_by=request.user)
        return Response({'success': True, 'data': TaskSerializer(task).data}, status=status.HTTP_201_CREATED)


class RecommendedTasksView(APIView):
    permission_classes = [IsAuthenticated, IsStudent]

    def get(self, request):
        student = request.user
        recommendations = TaskRecommendationService.get_recommendations_for_student(student, limit=10)
        result = []
        for rec in recommendations:
            task = rec['task']
            assignment, created = TaskAssignment.objects.get_or_create(
                student=student,
                task=task,
                defaults={'status': 'recommended', 'recommended_score': rec['score'], 'recommendation_reason': rec['reason']}
            )
            serializer = RecommendedTaskSerializer(assignment)
            result.append(serializer.data)
        return Response({'success': True, 'data': result})


class MyTasksView(APIView):
    permission_classes = [IsAuthenticated, IsStudent]

    def get(self, request):
        status_filter = request.query_params.get('status')
        assignments = TaskAssignment.objects.filter(student=request.user).select_related('task').exclude(status='recommended')
        if status_filter:
            assignments = assignments.filter(status=status_filter)
        serializer = TaskAssignmentSerializer(assignments, many=True)
        return Response({'success': True, 'data': serializer.data})


class AcceptTaskView(APIView):
    permission_classes = [IsAuthenticated, IsStudent]

    def post(self, request, assignment_id):
        try:
            assignment = TaskAssignment.objects.get(pk=assignment_id, student=request.user)
        except TaskAssignment.DoesNotExist:
            return Response({'success': False, 'error': 'Assignment not found.'}, status=status.HTTP_404_NOT_FOUND)
        serializer = TaskAssignmentAcceptSerializer(data=request.data)
        if not serializer.is_valid():
            return Response({'success': False, 'error': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
        accept = serializer.validated_data['accept']
        if accept:
            if assignment.status != 'recommended':
                return Response({'success': False, 'error': 'Only recommended tasks can be accepted.'}, status=status.HTTP_400_BAD_REQUEST)
            assignment.status = 'accepted'
            assignment.accepted_at = timezone.now()
            assignment.save()
            return Response({'success': True, 'data': TaskAssignmentSerializer(assignment).data})
        else:
            if assignment.status == 'recommended':
                assignment.delete()
                return Response({'success': True, 'message': 'Recommendation declined.'})
            else:
                return Response({'success': False, 'error': 'Cannot decline accepted/in-progress tasks.'}, status=status.HTTP_400_BAD_REQUEST)


class UpdateTaskAssignmentView(APIView):
    permission_classes = [IsAuthenticated, IsStudent]

    def put(self, request, assignment_id):
        try:
            assignment = TaskAssignment.objects.get(pk=assignment_id, student=request.user)
        except TaskAssignment.DoesNotExist:
            return Response({'success': False, 'error': 'Assignment not found.'}, status=status.HTTP_404_NOT_FOUND)
        serializer = TaskAssignmentUpdateSerializer(data=request.data, partial=True)
        if not serializer.is_valid():
            return Response({'success': False, 'error': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
        new_status = serializer.validated_data.get('status', assignment.status)
        new_progress = serializer.validated_data.get('progress_percentage', assignment.progress_percentage)
        valid_transitions = {'recommended': ['accepted'], 'accepted': ['in_progress'], 'in_progress': ['completed'], 'completed': []}
        if new_status != assignment.status:
            if new_status not in valid_transitions.get(assignment.status, []):
                return Response({'success': False, 'error': f'Cannot transition from {assignment.status} to {new_status}.'}, status=status.HTTP_400_BAD_REQUEST)
            assignment.status = new_status
            if new_status == 'in_progress':
                assignment.started_at = timezone.now()
            elif new_status == 'completed':
                assignment.completed_at = timezone.now()
        if new_progress != assignment.progress_percentage:
            assignment.progress_percentage = new_progress
        assignment.save()
        return Response({'success': True, 'data': TaskAssignmentSerializer(assignment).data})


class TaskAssignmentDetailView(APIView):
    permission_classes = [IsAuthenticated, IsStudent]

    def get(self, request, assignment_id):
        try:
            assignment = TaskAssignment.objects.get(pk=assignment_id, student=request.user)
        except TaskAssignment.DoesNotExist:
            return Response({'success': False, 'error': 'Assignment not found.'}, status=status.HTTP_404_NOT_FOUND)
        serializer = TaskAssignmentSerializer(assignment)
        return Response({'success': True, 'data': serializer.data})


class RequestMentorReviewView(APIView):
    permission_classes = [IsAuthenticated, IsStudent]

    def post(self, request, assignment_id):
        try:
            assignment = TaskAssignment.objects.get(pk=assignment_id, student=request.user)
        except TaskAssignment.DoesNotExist:
            return Response({'success': False, 'error': 'Assignment not found.'}, status=status.HTTP_404_NOT_FOUND)
        if assignment.status != 'completed':
            return Response({'success': False, 'error': 'Can only request review for completed tasks.'}, status=status.HTTP_400_BAD_REQUEST)
        assignment.mentor_review_requested = True
        assignment.mentor_review_status = 'requested'
        assignment.save()
        return Response({'success': True, 'data': TaskAssignmentSerializer(assignment).data})


class TaskMCQListView(APIView):
    permission_classes = [IsAuthenticated, IsStudent]

    def get(self, request, task_id):
        try:
            task = Task.objects.get(pk=task_id, is_active=True)
        except Task.DoesNotExist:
            return Response({'success': False, 'error': 'Task not found.'}, status=status.HTTP_404_NOT_FOUND)
        mcq_questions = TaskMCQ.objects.filter(task=task, is_active=True).order_by('order')
        serializer = TaskMCQSerializer(mcq_questions, many=True)
        return Response({'success': True, 'data': {'task_id': task.id, 'task_title': task.title, 'total_questions': len(mcq_questions), 'questions': serializer.data}})


class CompleteTaskView(APIView):
    permission_classes = [IsAuthenticated, IsStudent]

    def post(self, request, assignment_id):
        try:
            assignment = TaskAssignment.objects.get(pk=assignment_id, student=request.user)
        except TaskAssignment.DoesNotExist:
            return Response({'success': False, 'error': 'Assignment not found.'}, status=status.HTTP_404_NOT_FOUND)
        if assignment.status == 'completed':
            return Response({'success': False, 'error': 'Task already completed.'}, status=status.HTTP_400_BAD_REQUEST)
        serializer = TaskCompletionCreateSerializer(data=request.data)
        if not serializer.is_valid():
            return Response({'success': False, 'error': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
        assignment.status = 'completed'
        assignment.completed_at = timezone.now()
        assignment.save()
        completion = TaskCompletion.objects.create(task_assignment=assignment, reflective_text=serializer.validated_data.get('reflective_text', ''), completed_at=timezone.now())
        return Response({'success': True, 'data': {'completion_id': completion.id, 'task_id': assignment.task.id, 'task_title': assignment.task.title}})


class SubmitMCQAttemptsView(APIView):
    permission_classes = [IsAuthenticated, IsStudent]

    def post(self, request, completion_id):
        try:
            completion = TaskCompletion.objects.get(pk=completion_id)
            assignment = completion.task_assignment
        except TaskCompletion.DoesNotExist:
            return Response({'success': False, 'error': 'Task completion not found.'}, status=status.HTTP_404_NOT_FOUND)
        if assignment.student != request.user:
            return Response({'success': False, 'error': 'Unauthorized.'}, status=status.HTTP_403_FORBIDDEN)
        serializer = TaskMCQAttemptSubmitSerializer(data=request.data)
        if not serializer.is_valid():
            return Response({'success': False, 'error': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
        student_answers = serializer.validated_data['student_answers']
        duration_seconds = serializer.validated_data.get('duration_seconds', 0)
        mcq_questions = TaskMCQ.objects.filter(task=assignment.task, is_active=True).values('id', 'correct_answer')
        correct_count = 0
        total_count = mcq_questions.count()
        for question in mcq_questions:
            q_id = str(question['id'])
            if q_id in student_answers and student_answers[q_id] == question['correct_answer']:
                correct_count += 1
        mcq_score = (correct_count / total_count * 100) if total_count > 0 else 0
        attempt = TaskMCQAttempt.objects.create(task_completion=completion, student_answers=student_answers, total_questions=total_count, correct_answers=correct_count, mcq_score=mcq_score, duration_seconds=duration_seconds, is_submitted=True, submitted_at=timezone.now())
        evaluation = TaskEvaluation.objects.create(task_completion=completion, mcq_score=mcq_score, final_score=mcq_score, status='pending')
        return Response({'success': True, 'data': {'evaluation_id': evaluation.id, 'mcq_score': mcq_score, 'correct_answers': correct_count, 'total_questions': total_count}})


class TaskEvaluationDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, evaluation_id):
        try:
            evaluation = TaskEvaluation.objects.get(pk=evaluation_id)
        except TaskEvaluation.DoesNotExist:
            return Response({'success': False, 'error': 'Evaluation not found.'}, status=status.HTTP_404_NOT_FOUND)
        assignment = evaluation.task_completion.task_assignment
        if assignment.student != request.user and not request.user.groups.filter(name='Mentor').exists():
            return Response({'success': False, 'error': 'Unauthorized.'}, status=status.HTTP_403_FORBIDDEN)
        serializer = TaskEvaluationSerializer(evaluation)
        return Response({'success': True, 'data': serializer.data})


class MentorEvaluateTaskView(APIView):
    permission_classes = [IsAuthenticated, IsMentor]

    def post(self, request, evaluation_id):
        try:
            evaluation = TaskEvaluation.objects.get(pk=evaluation_id)
        except TaskEvaluation.DoesNotExist:
            return Response({'success': False, 'error': 'Evaluation not found.'}, status=status.HTTP_404_NOT_FOUND)
        assignment = evaluation.task_completion.task_assignment
        if assignment.student.studentprofile.mentor_assigned != request.user:
            return Response({'success': False, 'error': 'This student is not assigned to you.'}, status=status.HTTP_403_FORBIDDEN)
        serializer = TaskEvaluationUpdateSerializer(data=request.data)
        if not serializer.is_valid():
            return Response({'success': False, 'error': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
        mentor_score = serializer.validated_data['mentor_score']
        final_score = (evaluation.mcq_score + mentor_score) / 2
        evaluation.mentor_score = mentor_score
        evaluation.final_score = final_score
        evaluation.mentor_feedback = serializer.validated_data.get('mentor_feedback', '')
        evaluation.strengths = serializer.validated_data.get('strengths', [])
        evaluation.weaknesses = serializer.validated_data.get('weaknesses', [])
        evaluation.suggestions = serializer.validated_data.get('suggestions', [])
        evaluation.evaluated_by = request.user
        evaluation.evaluated_at = timezone.now()
        evaluation.status = 'evaluated'
        evaluation.save()
        try:
            portfolio_item = PortfolioService.create_portfolio_item(evaluation)
        except Exception as e:
            print(f"Error creating portfolio item: {str(e)}")
        result_serializer = TaskEvaluationSerializer(evaluation)
        return Response({'success': True, 'message': 'Task evaluation completed.', 'data': result_serializer.data})


class GetMyPortfolioView(APIView):
    permission_classes = [IsAuthenticated, IsStudent]

    def get(self, request):
        try:
            portfolio = Portfolio.objects.get(student=request.user)
        except Portfolio.DoesNotExist:
            return Response({'success': False, 'message': 'Portfolio not found.'}, status=status.HTTP_404_NOT_FOUND)
        serializer = PortfolioDetailSerializer(portfolio)
        return Response({'success': True, 'data': serializer.data})


class PortfolioDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, portfolio_id):
        try:
            portfolio = Portfolio.objects.get(id=portfolio_id)
        except Portfolio.DoesNotExist:
            return Response({'success': False, 'message': 'Portfolio not found.'}, status=status.HTTP_404_NOT_FOUND)
        if portfolio.user != request.user and not portfolio.is_public:
            return Response({'success': False, 'message': 'Permission denied.'}, status=status.HTTP_403_FORBIDDEN)
        serializer = PortfolioDetailSerializer(portfolio)
        return Response({'success': True, 'data': serializer.data})


class UpdatePortfolioView(APIView):
    permission_classes = [IsAuthenticated, IsStudent]

    def put(self, request, portfolio_id):
        try:
            portfolio = Portfolio.objects.get(id=portfolio_id)
        except Portfolio.DoesNotExist:
            return Response({'success': False, 'message': 'Portfolio not found.'}, status=status.HTTP_404_NOT_FOUND)
        if portfolio.user != request.user:
            return Response({'success': False, 'message': 'Permission denied.'}, status=status.HTTP_403_FORBIDDEN)
        serializer = PortfolioUpdateSerializer(portfolio, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({'success': True, 'message': 'Portfolio updated.', 'data': PortfolioDetailSerializer(portfolio).data})
        return Response({'success': False, 'errors': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)


class PortfolioItemDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, item_id):
        try:
            item = PortfolioItem.objects.get(id=item_id)
        except PortfolioItem.DoesNotExist:
            return Response({'success': False, 'message': 'Portfolio item not found.'}, status=status.HTTP_404_NOT_FOUND)
        if item.portfolio.user != request.user and not item.portfolio.is_public:
            return Response({'success': False, 'message': 'Permission denied.'}, status=status.HTTP_403_FORBIDDEN)
        serializer = PortfolioItemDetailSerializer(item)
        return Response({'success': True, 'data': serializer.data})


class UpdatePortfolioItemView(APIView):
    permission_classes = [IsAuthenticated, IsStudent]

    def put(self, request, item_id):
        try:
            item = PortfolioItem.objects.get(id=item_id)
        except PortfolioItem.DoesNotExist:
            return Response({'success': False, 'message': 'Portfolio item not found.'}, status=status.HTTP_404_NOT_FOUND)
        if item.portfolio.user != request.user:
            return Response({'success': False, 'message': 'Permission denied.'}, status=status.HTTP_403_FORBIDDEN)
        serializer = PortfolioItemUpdateSerializer(item, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({'success': True, 'message': 'Portfolio item updated.', 'data': PortfolioItemDetailSerializer(item).data})
        return Response({'success': False, 'errors': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)


class PortfolioStatsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, portfolio_id):
        try:
            portfolio = Portfolio.objects.get(id=portfolio_id)
        except Portfolio.DoesNotExist:
            return Response({'success': False, 'message': 'Portfolio not found.'}, status=status.HTTP_404_NOT_FOUND)
        if portfolio.user != request.user and not portfolio.is_public:
            return Response({'success': False, 'message': 'Permission denied.'}, status=status.HTTP_403_FORBIDDEN)
        stats = PortfolioService.get_portfolio_stats(portfolio)
        return Response({'success': True, 'data': stats})


class ExportPortfolioView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, portfolio_id):
        try:
            portfolio = Portfolio.objects.get(id=portfolio_id)
        except Portfolio.DoesNotExist:
            return Response({'success': False, 'message': 'Portfolio not found.'}, status=status.HTTP_404_NOT_FOUND)
        if portfolio.user != request.user and not portfolio.is_public:
            return Response({'success': False, 'message': 'Permission denied.'}, status=status.HTTP_403_FORBIDDEN)
        export_data = PortfolioService.export_portfolio_as_json(portfolio)
        return Response({'success': True, 'data': export_data})
"""
Views for Task and TaskAssignment endpoints.
"""

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone

from apps.core.permissions import IsStudent, IsMentor, IsAdmin
from .models import Task, TaskAssignment, TaskMCQ, TaskCompletion, TaskMCQAttempt, TaskEvaluation
from apps.portfolios.models import Portfolio, PortfolioItem
from .serializers import (
    TaskSerializer,
    TaskCreateSerializer,
    TaskAssignmentSerializer,
    TaskAssignmentUpdateSerializer,
    TaskAssignmentAcceptSerializer,
    RecommendedTaskSerializer,
    TaskMCQSerializer,
    TaskCompletionSerializer,
    TaskCompletionCreateSerializer,
    TaskMCQAttemptSerializer,
    TaskMCQAttemptSubmitSerializer,
    TaskEvaluationSerializer,
    TaskEvaluationUpdateSerializer,
    PortfolioSerializer,
    PortfolioDetailSerializer,
    PortfolioUpdateSerializer,
    PortfolioItemSerializer,
    PortfolioItemDetailSerializer,
    PortfolioItemUpdateSerializer,
)
from .recommendation_service import TaskRecommendationService
from .portfolio_service import PortfolioService


class TaskListView(APIView):
    """
    GET /api/tasks/
    List all active tasks (student view - no edit).
    """
    permission_classes = [IsAuthenticated, IsStudent]

    def get(self, request):
        domain_filter = request.query_params.get('domain')
        difficulty_filter = request.query_params.get('difficulty')

        tasks = Task.objects.filter(is_active=True)

        if domain_filter:
            tasks = tasks.filter(domain=domain_filter)
        if difficulty_filter:
            tasks = tasks.filter(difficulty=difficulty_filter)

        serializer = TaskSerializer(tasks, many=True)
        return Response({'success': True, 'data': serializer.data})


class TaskDetailView(APIView):
    """
    GET /api/tasks/{id}/
    View task details (student view).
    """
    permission_classes = [IsAuthenticated, IsStudent]

    def get(self, request, pk):
        try:
            task = Task.objects.get(pk=pk, is_active=True)
        except Task.DoesNotExist:
            return Response(
                {'success': False, 'error': {'code': 404, 'message': 'Task not found.'}},
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = TaskSerializer(task)
        return Response({'success': True, 'data': serializer.data})


class TaskCreateView(APIView):
    """
    POST /api/tasks/create/
    Create new task (mentor/admin only).
    """
    permission_classes = [IsAuthenticated, IsMentor]

    def post(self, request):
        serializer = TaskCreateSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(
                {'success': False, 'error': serializer.errors},
                status=status.HTTP_400_BAD_REQUEST,
            )

        task = serializer.save(created_by=request.user)
        return Response(
            {'success': True, 'message': 'Task created successfully.', 'data': TaskSerializer(task).data},
            status=status.HTTP_201_CREATED,
        )


class RecommendedTasksView(APIView):
    """
    GET /api/tasks/recommended/
    Get recommended tasks for logged-in student based on their profile.
    """
    permission_classes = [IsAuthenticated, IsStudent]

    def get(self, request):
        student = request.user
        recommendations = TaskRecommendationService.get_recommendations_for_student(
            student, limit=10
        )

        result = []
        for rec in recommendations:
            task = rec['task']
            
            assignment, created = TaskAssignment.objects.get_or_create(
                student=student,
                task=task,
                defaults={
                    'status': 'recommended',
                    'recommended_score': rec['score'],
                    'recommendation_reason': rec['reason'],
                }
            )

            serializer = RecommendedTaskSerializer(assignment)
            result.append(serializer.data)

        return Response({'success': True, 'data': result})


class MyTasksView(APIView):
    """
    GET /api/tasks/my-tasks/
    Get all tasks assigned/accepted/in-progress/completed by student.
    """
    permission_classes = [IsAuthenticated, IsStudent]

    def get(self, request):
        status_filter = request.query_params.get('status')
        
        assignments = TaskAssignment.objects.filter(
            student=request.user
        ).select_related('task').exclude(status='recommended')

        if status_filter:
            assignments = assignments.filter(status=status_filter)

        serializer = TaskAssignmentSerializer(assignments, many=True)
        return Response({'success': True, 'data': serializer.data})


class AcceptTaskView(APIView):
    """
    POST /api/tasks/assignments/{assignment_id}/accept/
    Accept a recommended task.
    """
    permission_classes = [IsAuthenticated, IsStudent]

    def post(self, request, assignment_id):
        try:
            assignment = TaskAssignment.objects.get(pk=assignment_id, student=request.user)
        except TaskAssignment.DoesNotExist:
            return Response(
                {'success': False, 'error': {'code': 404, 'message': 'Assignment not found.'}},
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = TaskAssignmentAcceptSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(
                {'success': False, 'error': serializer.errors},
                status=status.HTTP_400_BAD_REQUEST,
            )

        accept = serializer.validated_data['accept']

        if accept:
            if assignment.status != 'recommended':
                return Response(
                    {
                        'success': False,
                        'error': {'code': 400, 'message': 'Only recommended tasks can be accepted.'},
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )

            assignment.status = 'accepted'
            assignment.accepted_at = timezone.now()
            assignment.save()

            return Response(
                {
                    'success': True,
                    'message': 'Task accepted successfully.',
                    'data': TaskAssignmentSerializer(assignment).data,
                }
            )
        else:
            if assignment.status == 'recommended':
                assignment.delete()
                return Response(
                    {'success': True, 'message': 'Recommendation declined.'}
                )
            else:
                return Response(
                    {
                        'success': False,
                        'error': {'code': 400, 'message': 'Cannot decline accepted/in-progress tasks.'},
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )


class UpdateTaskAssignmentView(APIView):
    """
    PUT /api/tasks/assignments/{assignment_id}/
    Update task assignment status and progress (student).
    """
    permission_classes = [IsAuthenticated, IsStudent]

    def put(self, request, assignment_id):
        try:
            assignment = TaskAssignment.objects.get(pk=assignment_id, student=request.user)
        except TaskAssignment.DoesNotExist:
            return Response(
                {'success': False, 'error': {'code': 404, 'message': 'Assignment not found.'}},
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = TaskAssignmentUpdateSerializer(data=request.data, partial=True)
        if not serializer.is_valid():
            return Response(
                {'success': False, 'error': serializer.errors},
                status=status.HTTP_400_BAD_REQUEST,
            )

        new_status = serializer.validated_data.get('status', assignment.status)
        new_progress = serializer.validated_data.get('progress_percentage', assignment.progress_percentage)

        valid_transitions = {
            'recommended': ['accepted'],
            'accepted': ['in_progress'],
            'in_progress': ['completed'],
            'completed': [],
        }

        if new_status != assignment.status:
            if new_status not in valid_transitions.get(assignment.status, []):
                return Response(
                    {
                        'success': False,
                        'error': {
                            'code': 400,
                            'message': f'Cannot transition from {assignment.status} to {new_status}.',
                        },
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )

            assignment.status = new_status

            if new_status == 'in_progress':
                assignment.started_at = timezone.now()
            elif new_status == 'completed':
                assignment.completed_at = timezone.now()

        if new_progress != assignment.progress_percentage:
            assignment.progress_percentage = new_progress

        assignment.save()

        return Response(
            {
                'success': True,
                'message': 'Task assignment updated successfully.',
                'data': TaskAssignmentSerializer(assignment).data,
            }
        )


class TaskAssignmentDetailView(APIView):
    """
    GET /api/tasks/assignments/{assignment_id}/
    View task assignment details.
    """
    permission_classes = [IsAuthenticated, IsStudent]

    def get(self, request, assignment_id):
        try:
            assignment = TaskAssignment.objects.get(pk=assignment_id, student=request.user)
        except TaskAssignment.DoesNotExist:
            return Response(
                {'success': False, 'error': {'code': 404, 'message': 'Assignment not found.'}},
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = TaskAssignmentSerializer(assignment)
        return Response({'success': True, 'data': serializer.data})


class RequestMentorReviewView(APIView):
    """
    POST /api/tasks/assignments/{assignment_id}/request-review/
    Request mentor review for a task (student).
    """
    permission_classes = [IsAuthenticated, IsStudent]

    def post(self, request, assignment_id):
        try:
            assignment = TaskAssignment.objects.get(pk=assignment_id, student=request.user)
        except TaskAssignment.DoesNotExist:
            return Response(
                {'success': False, 'error': {'code': 404, 'message': 'Assignment not found.'}},
                status=status.HTTP_404_NOT_FOUND,
            )

        if assignment.status != 'completed':
            return Response(
                {
                    'success': False,
                    'error': {'code': 400, 'message': 'Can only request review for completed tasks.'},
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        assignment.mentor_review_requested = True
        assignment.mentor_review_status = 'requested'
        assignment.save()

        return Response(
            {
                'success': True,
                'message': 'Mentor review requested.',
                'data': TaskAssignmentSerializer(assignment).data,
            }
        )


class TaskMCQListView(APIView):
    """
    GET /api/tasks/{task_id}/mcq-questions/
    Get all MCQ questions for a task.
    """
    permission_classes = [IsAuthenticated, IsStudent]

    def get(self, request, task_id):
        try:
            task = Task.objects.get(pk=task_id, is_active=True)
        except Task.DoesNotExist:
            return Response(
                {'success': False, 'error': {'code': 404, 'message': 'Task not found.'}},
                status=status.HTTP_404_NOT_FOUND,
            )

        mcq_questions = TaskMCQ.objects.filter(task=task, is_active=True).order_by('order')
        serializer = TaskMCQSerializer(mcq_questions, many=True)

        return Response({
            'success': True,
            'data': {
                'task_id': task.id,
                'task_title': task.title,
                'total_questions': len(mcq_questions),
                'questions': serializer.data,
            }
        })


class CompleteTaskView(APIView):
    """
    POST /api/tasks/assignments/{assignment_id}/complete/
    Mark task as completed and create TaskCompletion record.
    Student provides optional reflective text.
    """
    permission_classes = [IsAuthenticated, IsStudent]

    def post(self, request, assignment_id):
        try:
            assignment = TaskAssignment.objects.get(pk=assignment_id, student=request.user)
        except TaskAssignment.DoesNotExist:
            return Response(
                {'success': False, 'error': {'code': 404, 'message': 'Assignment not found.'}},
                status=status.HTTP_404_NOT_FOUND,
            )

        if assignment.status == 'completed':
            return Response(
                {'success': False, 'error': {'code': 400, 'message': 'Task already completed.'}},
                status=status.HTTP_400_BAD_REQUEST,
            )

        serializer = TaskCompletionCreateSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(
                {'success': False, 'error': {'code': 400, 'message': serializer.errors}},
                status=status.HTTP_400_BAD_REQUEST,
            )

        assignment.status = 'completed'
        assignment.completed_at = timezone.now()
        assignment.save()

        completion = TaskCompletion.objects.create(
            task_assignment=assignment,
            reflective_text=serializer.validated_data.get('reflective_text', ''),
            completed_at=timezone.now(),
        )

        return Response({
            'success': True,
            'message': 'Task marked as completed. Please proceed to MCQ quiz.',
            'data': {
                'completion_id': completion.id,
                'task_id': assignment.task.id,
                'task_title': assignment.task.title,
            }
        })


class SubmitMCQAttemptsView(APIView):
    """
    POST /api/tasks/completions/{completion_id}/submit-mcq/
    Submit MCQ answers and calculate score.
    """
    permission_classes = [IsAuthenticated, IsStudent]

    def post(self, request, completion_id):
        try:
            completion = TaskCompletion.objects.get(pk=completion_id)
            assignment = completion.task_assignment
        except TaskCompletion.DoesNotExist:
            return Response(
                {'success': False, 'error': {'code': 404, 'message': 'Task completion not found.'}},
                status=status.HTTP_404_NOT_FOUND,
            )

        if assignment.student != request.user:
            return Response(
                {'success': False, 'error': {'code': 403, 'message': 'Unauthorized.'}},
                status=status.HTTP_403_FORBIDDEN,
            )

        serializer = TaskMCQAttemptSubmitSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(
                {'success': False, 'error': {'code': 400, 'message': serializer.errors}},
                status=status.HTTP_400_BAD_REQUEST,
            )

        student_answers = serializer.validated_data['student_answers']
        duration_seconds = serializer.validated_data.get('duration_seconds', 0)

        mcq_questions = TaskMCQ.objects.filter(
            task=assignment.task,
            is_active=True
        ).values('id', 'correct_answer')

        correct_count = 0
        total_count = mcq_questions.count()

        for question in mcq_questions:
            q_id = str(question['id'])
            if q_id in student_answers and student_answers[q_id] == question['correct_answer']:
                correct_count += 1

        mcq_score = (correct_count / total_count * 100) if total_count > 0 else 0

        attempt = TaskMCQAttempt.objects.create(
            task_completion=completion,
            student_answers=student_answers,
            total_questions=total_count,
            correct_answers=correct_count,
            mcq_score=mcq_score,
            duration_seconds=duration_seconds,
            is_submitted=True,
            submitted_at=timezone.now(),
        )

        evaluation = TaskEvaluation.objects.create(
            task_completion=completion,
            mcq_score=mcq_score,
            final_score=mcq_score,
            status='pending',
        )

        return Response({
            'success': True,
            'message': 'MCQ submitted successfully.',
            'data': {
                'evaluation_id': evaluation.id,
                'mcq_score': mcq_score,
                'correct_answers': correct_count,
                'total_questions': total_count,
                'percentage': f"{(correct_count/total_count*100):.2f}" if total_count > 0 else "0.00",
            }
        })


class TaskEvaluationDetailView(APIView):
    """
    GET /api/tasks/evaluations/{evaluation_id}/
    Get evaluation details for a completed task.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request, evaluation_id):
        try:
            evaluation = TaskEvaluation.objects.get(pk=evaluation_id)
        except TaskEvaluation.DoesNotExist:
            return Response(
                {'success': False, 'error': {'code': 404, 'message': 'Evaluation not found.'}},
                status=status.HTTP_404_NOT_FOUND,
            )

        assignment = evaluation.task_completion.task_assignment
        if assignment.student != request.user and not request.user.groups.filter(name='Mentor').exists():
            return Response(
                {'success': False, 'error': {'code': 403, 'message': 'Unauthorized.'}},
                status=status.HTTP_403_FORBIDDEN,
            )

        serializer = TaskEvaluationSerializer(evaluation)
        return Response({
            'success': True,
            'data': serializer.data
        })


class MentorEvaluateTaskView(APIView):
    """
    POST /api/tasks/evaluations/{evaluation_id}/evaluate/
    Mentor submits manual evaluation with score and feedback.
    """
    permission_classes = [IsAuthenticated, IsMentor]

    def post(self, request, evaluation_id):
        try:
            evaluation = TaskEvaluation.objects.get(pk=evaluation_id)
        except TaskEvaluation.DoesNotExist:
            return Response(
                {'success': False, 'error': {'code': 404, 'message': 'Evaluation not found.'}},
                status=status.HTTP_404_NOT_FOUND,
            )

        assignment = evaluation.task_completion.task_assignment

        if assignment.student.studentprofile.mentor_assigned != request.user:
            return Response(
                {'success': False, 'error': {'code': 403, 'message': 'This student is not assigned to you.'}},
                status=status.HTTP_403_FORBIDDEN,
            )

        serializer = TaskEvaluationUpdateSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(
                {'success': False, 'error': {'code': 400, 'message': serializer.errors}},
                status=status.HTTP_400_BAD_REQUEST,
            )

        mentor_score = serializer.validated_data['mentor_score']
        final_score = (evaluation.mcq_score + mentor_score) / 2

        evaluation.mentor_score = mentor_score
        evaluation.final_score = final_score
        evaluation.mentor_feedback = serializer.validated_data.get('mentor_feedback', '')
        evaluation.strengths = serializer.validated_data.get('strengths', [])
        evaluation.weaknesses = serializer.validated_data.get('weaknesses', [])
        evaluation.suggestions = serializer.validated_data.get('suggestions', [])
        evaluation.evaluated_by = request.user
        evaluation.evaluated_at = timezone.now()
        evaluation.status = 'evaluated'
        evaluation.save()

        try:
            portfolio_item = PortfolioService.create_portfolio_item(evaluation)
        except Exception as e:
            print(f"Error creating portfolio item: {str(e)}")

        result_serializer = TaskEvaluationSerializer(evaluation)
        return Response({
            'success': True,
            'message': 'Task evaluation completed.',
            'data': result_serializer.data
        })


class GetMyPortfolioView(APIView):
    """
    GET /api/portfolios/me/
    Get current user's portfolio.
    """
    permission_classes = [IsAuthenticated, IsStudent]

    def get(self, request):
        try:
            portfolio = Portfolio.objects.get(student=request.user)
        except Portfolio.DoesNotExist:
            return Response({
                'success': False,
                'message': 'Portfolio not found. Complete a task evaluation to generate one.'
            }, status=status.HTTP_404_NOT_FOUND)

        serializer = PortfolioDetailSerializer(portfolio)
        return Response({
            'success': True,
            'data': serializer.data
        })


class PortfolioDetailView(APIView):
    """
    GET /api/portfolios/<id>/
    Get specific portfolio (if public or own).
    """
    permission_classes = [IsAuthenticated]

    def get(self, request, portfolio_id):
        try:
            portfolio = Portfolio.objects.get(id=portfolio_id)
        except Portfolio.DoesNotExist:
            return Response({
                'success': False,
                'message': 'Portfolio not found.'
            }, status=status.HTTP_404_NOT_FOUND)

        if portfolio.user != request.user and not portfolio.is_public:
            return Response({
                'success': False,
                'message': 'You do not have permission to view this portfolio.'
            }, status=status.HTTP_403_FORBIDDEN)

        serializer = PortfolioDetailSerializer(portfolio)
        return Response({
            'success': True,
            'data': serializer.data
        })


class UpdatePortfolioView(APIView):
    """
    PUT /api/portfolios/<id>/update/
    Update portfolio info (title, bio, visibility).
    """
    permission_classes = [IsAuthenticated, IsStudent]

    def put(self, request, portfolio_id):
        try:
            portfolio = Portfolio.objects.get(id=portfolio_id)
        except Portfolio.DoesNotExist:
            return Response({
                'success': False,
                'message': 'Portfolio not found.'
            }, status=status.HTTP_404_NOT_FOUND)

        if portfolio.user != request.user:
            return Response({
                'success': False,
                'message': 'You can only update your own portfolio.'
            }, status=status.HTTP_403_FORBIDDEN)

        serializer = PortfolioUpdateSerializer(portfolio, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({
                'success': True,
                'message': 'Portfolio updated successfully.',
                'data': PortfolioDetailSerializer(portfolio).data
            })

        return Response({
            'success': False,
            'errors': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)


class PortfolioItemDetailView(APIView):
    """
    GET /api/portfolio-items/<id>/
    Get portfolio item details.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request, item_id):
        try:
            item = PortfolioItem.objects.get(id=item_id)
        except PortfolioItem.DoesNotExist:
            return Response({
                'success': False,
                'message': 'Portfolio item not found.'
            }, status=status.HTTP_404_NOT_FOUND)

        if item.portfolio.user != request.user and not item.portfolio.is_public:
            return Response({
                'success': False,
                'message': 'You do not have permission to view this item.'
            }, status=status.HTTP_403_FORBIDDEN)

        serializer = PortfolioItemDetailSerializer(item)
        return Response({
            'success': True,
            'data': serializer.data
        })


class UpdatePortfolioItemView(APIView):
    """
    PUT /api/portfolio-items/<id>/update/
    Update portfolio item display settings.
    """
    permission_classes = [IsAuthenticated, IsStudent]

    def put(self, request, item_id):
        try:
            item = PortfolioItem.objects.get(id=item_id)
        except PortfolioItem.DoesNotExist:
            return Response({
                'success': False,
                'message': 'Portfolio item not found.'
            }, status=status.HTTP_404_NOT_FOUND)

        if item.portfolio.user != request.user:
            return Response({
                'success': False,
                'message': 'You can only update your own portfolio items.'
            }, status=status.HTTP_403_FORBIDDEN)

        serializer = PortfolioItemUpdateSerializer(item, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({
                'success': True,
                'message': 'Portfolio item updated successfully.',
                'data': PortfolioItemDetailSerializer(item).data
            })

        return Response({
            'success': False,
            'errors': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)


class PortfolioStatsView(APIView):
    """
    GET /api/portfolios/<id>/stats/
    Get portfolio statistics and analytics.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request, portfolio_id):
        try:
            portfolio = Portfolio.objects.get(id=portfolio_id)
        except Portfolio.DoesNotExist:
            return Response({
                'success': False,
                'message': 'Portfolio not found.'
            }, status=status.HTTP_404_NOT_FOUND)

        if portfolio.user != request.user and not portfolio.is_public:
            return Response({
                'success': False,
                'message': 'You do not have permission to view this portfolio.'
            }, status=status.HTTP_403_FORBIDDEN)

        stats = PortfolioService.get_portfolio_stats(portfolio)
        return Response({
            'success': True,
            'data': stats
        })


class ExportPortfolioView(APIView):
    """
    GET /api/portfolios/<id>/export/
    Export portfolio data as JSON.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request, portfolio_id):
        try:
            portfolio = Portfolio.objects.get(id=portfolio_id)
        except Portfolio.DoesNotExist:
            return Response({
                'success': False,
                'message': 'Portfolio not found.'
            }, status=status.HTTP_404_NOT_FOUND)

        if portfolio.user != request.user and not portfolio.is_public:
            return Response({
                'success': False,
                'message': 'You do not have permission to export this portfolio.'
            }, status=status.HTTP_403_FORBIDDEN)

        export_data = PortfolioService.export_portfolio_as_json(portfolio)
        return Response({
            'success': True,
            'data': export_data
        })
"""
Views for Task and TaskAssignment endpoints.
"""

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone

from apps.core.permissions import IsStudent, IsMentor, IsAdmin
from .models import Task, TaskAssignment, TaskMCQ, TaskCompletion, TaskMCQAttempt, TaskEvaluation
from apps.portfolios.models import Portfolio, PortfolioItem
from .serializers import (
    TaskSerializer,
    TaskCreateSerializer,
    TaskAssignmentSerializer,
    TaskAssignmentUpdateSerializer,
    TaskAssignmentAcceptSerializer,
    RecommendedTaskSerializer,
    TaskMCQSerializer,
    TaskCompletionSerializer,
    TaskCompletionCreateSerializer,
    TaskMCQAttemptSerializer,
    TaskMCQAttemptSubmitSerializer,
    TaskEvaluationSerializer,
    TaskEvaluationUpdateSerializer,
    PortfolioSerializer,
    PortfolioDetailSerializer,
    PortfolioUpdateSerializer,
    PortfolioItemSerializer,
    PortfolioItemDetailSerializer,
    PortfolioItemUpdateSerializer,
)
from .recommendation_service import TaskRecommendationService
from .portfolio_service import PortfolioService


class TaskListView(APIView):
    """
    GET /api/tasks/
    List all active tasks (student view - no edit).
    """
    permission_classes = [IsAuthenticated, IsStudent]

    def get(self, request):
        domain_filter = request.query_params.get('domain')
        difficulty_filter = request.query_params.get('difficulty')

        tasks = Task.objects.filter(is_active=True)

        if domain_filter:
            tasks = tasks.filter(domain=domain_filter)
        if difficulty_filter:
            tasks = tasks.filter(difficulty=difficulty_filter)

        serializer = TaskSerializer(tasks, many=True)
        return Response({'success': True, 'data': serializer.data})


class TaskDetailView(APIView):
    """
    GET /api/tasks/{id}/
    View task details (student view).
    """
    permission_classes = [IsAuthenticated, IsStudent]

    def get(self, request, pk):
        try:
            task = Task.objects.get(pk=pk, is_active=True)
        except Task.DoesNotExist:
            return Response(
                {'success': False, 'error': {'code': 404, 'message': 'Task not found.'}},
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = TaskSerializer(task)
        return Response({'success': True, 'data': serializer.data})


class TaskCreateView(APIView):
    """
    POST /api/tasks/create/
    Create new task (mentor/admin only).
    """
    permission_classes = [IsAuthenticated, IsMentor]

    def post(self, request):
        serializer = TaskCreateSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(
                {'success': False, 'error': serializer.errors},
                status=status.HTTP_400_BAD_REQUEST,
            )

        task = serializer.save(created_by=request.user)
        return Response(
            {'success': True, 'message': 'Task created successfully.', 'data': TaskSerializer(task).data},
            status=status.HTTP_201_CREATED,
        )


class RecommendedTasksView(APIView):
    """
    GET /api/tasks/recommended/
    Get recommended tasks for logged-in student based on their profile.
    """
    permission_classes = [IsAuthenticated, IsStudent]

    def get(self, request):
        student = request.user
        recommendations = TaskRecommendationService.get_recommendations_for_student(
            student, limit=10
        )

        # Get or create TaskAssignment records for these recommendations
        result = []
        for rec in recommendations:
            task = rec['task']
            
            # Get existing assignment or create new recommendation
            assignment, created = TaskAssignment.objects.get_or_create(
                student=student,
                task=task,
                defaults={
                    'status': 'recommended',
                    'recommended_score': rec['score'],
                    'recommendation_reason': rec['reason'],
                }
            )

            serializer = RecommendedTaskSerializer(assignment)
            result.append(serializer.data)

        return Response({'success': True, 'data': result})


class MyTasksView(APIView):
    """
    GET /api/tasks/my-tasks/
    Get all tasks assigned/accepted/in-progress/completed by student.
    """
    permission_classes = [IsAuthenticated, IsStudent]

    def get(self, request):
        status_filter = request.query_params.get('status')
        
        assignments = TaskAssignment.objects.filter(
            student=request.user
        ).select_related('task').exclude(status='recommended')

        if status_filter:
            assignments = assignments.filter(status=status_filter)

        serializer = TaskAssignmentSerializer(assignments, many=True)
        return Response({'success': True, 'data': serializer.data})


class AcceptTaskView(APIView):
    """
    POST /api/tasks/assignments/{assignment_id}/accept/
    Accept a recommended task.
    """
    permission_classes = [IsAuthenticated, IsStudent]

    def post(self, request, assignment_id):
        try:
            assignment = TaskAssignment.objects.get(pk=assignment_id, student=request.user)
        except TaskAssignment.DoesNotExist:
            return Response(
                {'success': False, 'error': {'code': 404, 'message': 'Assignment not found.'}},
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = TaskAssignmentAcceptSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(
                {'success': False, 'error': serializer.errors},
                status=status.HTTP_400_BAD_REQUEST,
            )

        accept = serializer.validated_data['accept']

        if accept:
            if assignment.status != 'recommended':
                return Response(
                    {
                        'success': False,
                        'error': {'code': 400, 'message': 'Only recommended tasks can be accepted.'},
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )

            assignment.status = 'accepted'
            assignment.accepted_at = timezone.now()
            assignment.save()

            return Response(
                {
                    'success': True,
                    'message': 'Task accepted successfully.',
                    'data': TaskAssignmentSerializer(assignment).data,
                }
            )
        else:
            # Decline
            if assignment.status == 'recommended':
                assignment.delete()
                return Response(
                    {'success': True, 'message': 'Recommendation declined.'}
                )
            else:
                return Response(
                    {
                        'success': False,
                        'error': {'code': 400, 'message': 'Cannot decline accepted/in-progress tasks.'},
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )


class UpdateTaskAssignmentView(APIView):
    """
    PUT /api/tasks/assignments/{assignment_id}/
    Update task assignment status and progress (student).
    """
    permission_classes = [IsAuthenticated, IsStudent]

    def put(self, request, assignment_id):
        try:
            assignment = TaskAssignment.objects.get(pk=assignment_id, student=request.user)
        except TaskAssignment.DoesNotExist:
            return Response(
                {'success': False, 'error': {'code': 404, 'message': 'Assignment not found.'}},
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = TaskAssignmentUpdateSerializer(data=request.data, partial=True)
        if not serializer.is_valid():
            return Response(
                {'success': False, 'error': serializer.errors},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Update fields
        new_status = serializer.validated_data.get('status', assignment.status)
        new_progress = serializer.validated_data.get('progress_percentage', assignment.progress_percentage)

        # Validate status transitions
        valid_transitions = {
            'recommended': ['accepted'],
            'accepted': ['in_progress'],
            'in_progress': ['completed'],
            'completed': [],
        }

        if new_status != assignment.status:
            if new_status not in valid_transitions.get(assignment.status, []):
                return Response(
                    {
                        'success': False,
                        'error': {
                            'code': 400,
                            'message': f'Cannot transition from {assignment.status} to {new_status}.',
                        },
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )

            assignment.status = new_status

            # Update timestamps
            if new_status == 'in_progress':
                assignment.started_at = timezone.now()
            elif new_status == 'completed':
                assignment.completed_at = timezone.now()

        if new_progress != assignment.progress_percentage:
            assignment.progress_percentage = new_progress

        assignment.save()

        return Response(
            {
                'success': True,
                'message': 'Task assignment updated successfully.',
                'data': TaskAssignmentSerializer(assignment).data,
            }
        )


class TaskAssignmentDetailView(APIView):
    """
    GET /api/tasks/assignments/{assignment_id}/
    View task assignment details.
    """
    permission_classes = [IsAuthenticated, IsStudent]

    def get(self, request, assignment_id):
        try:
            assignment = TaskAssignment.objects.get(pk=assignment_id, student=request.user)
        except TaskAssignment.DoesNotExist:
            return Response(
                {'success': False, 'error': {'code': 404, 'message': 'Assignment not found.'}},
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = TaskAssignmentSerializer(assignment)
        return Response({'success': True, 'data': serializer.data})


class RequestMentorReviewView(APIView):
    """
    POST /api/tasks/assignments/{assignment_id}/request-review/
    Request mentor review for a task (student).
    """
    permission_classes = [IsAuthenticated, IsStudent]

    def post(self, request, assignment_id):
        try:
            assignment = TaskAssignment.objects.get(pk=assignment_id, student=request.user)
        except TaskAssignment.DoesNotExist:
            return Response(
                {'success': False, 'error': {'code': 404, 'message': 'Assignment not found.'}},
                status=status.HTTP_404_NOT_FOUND,
            )

        if assignment.status != 'completed':
            return Response(
                {
                    'success': False,
                    'error': {'code': 400, 'message': 'Can only request review for completed tasks.'},
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        assignment.mentor_review_requested = True
        assignment.mentor_review_status = 'requested'
        assignment.save()

        return Response(
            {
                'success': True,
                'message': 'Mentor review requested.',
                'data': TaskAssignmentSerializer(assignment).data,
            }
        )


class TaskMCQListView(APIView):
    """
    GET /api/tasks/{task_id}/mcq-questions/
    Get all MCQ questions for a task.
    """
    permission_classes = [IsAuthenticated, IsStudent]

    def get(self, request, task_id):
        try:
            task = Task.objects.get(pk=task_id, is_active=True)
        except Task.DoesNotExist:
            return Response(
                {'success': False, 'error': {'code': 404, 'message': 'Task not found.'}},
                status=status.HTTP_404_NOT_FOUND,
            )

        mcq_questions = TaskMCQ.objects.filter(task=task, is_active=True).order_by('order')
        serializer = TaskMCQSerializer(mcq_questions, many=True)

        return Response({
            'success': True,
            'data': {
                'task_id': task.id,
                'task_title': task.title,
                'total_questions': len(mcq_questions),
                'questions': serializer.data,
            }
        })


class CompleteTaskView(APIView):
    """
    POST /api/tasks/assignments/{assignment_id}/complete/
    Mark task as completed and create TaskCompletion record.
    Student provides optional reflective text.
    """
    permission_classes = [IsAuthenticated, IsStudent]

    def post(self, request, assignment_id):
        try:
            assignment = TaskAssignment.objects.get(pk=assignment_id, student=request.user)
        except TaskAssignment.DoesNotExist:
            return Response(
                {'success': False, 'error': {'code': 404, 'message': 'Assignment not found.'}},
                status=status.HTTP_404_NOT_FOUND,
            )

        if assignment.status == 'completed':
            return Response(
                {'success': False, 'error': {'code': 400, 'message': 'Task already completed.'}},
                status=status.HTTP_400_BAD_REQUEST,
            )

        serializer = TaskCompletionCreateSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(
                {'success': False, 'error': {'code': 400, 'message': serializer.errors}},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Mark assignment as completed
        assignment.status = 'completed'
        assignment.completed_at = timezone.now()
        assignment.save()

        # Create TaskCompletion record
        completion = TaskCompletion.objects.create(
            task_assignment=assignment,
            reflective_text=serializer.validated_data.get('reflective_text', ''),
            completed_at=timezone.now(),
        )

        return Response({
            'success': True,
            'message': 'Task marked as completed. Please proceed to MCQ quiz.',
            'data': {
                'completion_id': completion.id,
                'task_id': assignment.task.id,
                'task_title': assignment.task.title,
            }
        })


class SubmitMCQAttemptsView(APIView):
    """
    POST /api/tasks/completions/{completion_id}/submit-mcq/
    Submit MCQ answers and calculate score.
    """
    permission_classes = [IsAuthenticated, IsStudent]

    def post(self, request, completion_id):
        try:
            completion = TaskCompletion.objects.get(pk=completion_id)
            assignment = completion.task_assignment
        except TaskCompletion.DoesNotExist:
            return Response(
                {'success': False, 'error': {'code': 404, 'message': 'Task completion not found.'}},
                status=status.HTTP_404_NOT_FOUND,
            )

        # Verify student owns this completion
        if assignment.student != request.user:
            return Response(
                {'success': False, 'error': {'code': 403, 'message': 'Unauthorized.'}},
                status=status.HTTP_403_FORBIDDEN,
            )

        serializer = TaskMCQAttemptSubmitSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(
                {'success': False, 'error': {'code': 400, 'message': serializer.errors}},
                status=status.HTTP_400_BAD_REQUEST,
            )

        student_answers = serializer.validated_data['student_answers']
        duration_seconds = serializer.validated_data.get('duration_seconds', 0)

        # Get all MCQ questions for this task
        mcq_questions = TaskMCQ.objects.filter(
            task=assignment.task,
            is_active=True
        ).values('id', 'correct_answer')

        # Calculate correct answers
        correct_count = 0
        total_count = mcq_questions.count()

        for question in mcq_questions:
            q_id = str(question['id'])
            if q_id in student_answers and student_answers[q_id] == question['correct_answer']:
                correct_count += 1

        # Calculate score (0-100)
        mcq_score = (correct_count / total_count * 100) if total_count > 0 else 0

        # Create MCQAttempt record
        attempt = TaskMCQAttempt.objects.create(
            task_completion=completion,
            student_answers=student_answers,
            total_questions=total_count,
            correct_answers=correct_count,
            mcq_score=mcq_score,
            duration_seconds=duration_seconds,
            is_submitted=True,
            submitted_at=timezone.now(),
        )

        # Create TaskEvaluation with MCQ score
        evaluation = TaskEvaluation.objects.create(
            task_completion=completion,
            mcq_score=mcq_score,
            final_score=mcq_score,  # Initially same as MCQ score
            status='pending',  # Pending mentor evaluation
        )

        return Response({
            'success': True,
            'data': {
                'evaluation_id': evaluation.id,
                'mcq_score': mcq_score,
                'correct_answers': correct_count,
                'total_questions': total_count,
            }
        })

        return Response({
            'success': True,
            'message': 'MCQ submitted successfully.',
            'data': {
                'evaluation_id': evaluation.id,
                'mcq_score': mcq_score,
                'correct_answers': correct_count,
                'total_questions': total_count,
                'percentage': f"{(correct_count/total_count*100):.2f}" if total_count > 0 else "0.00",
            }
        })


class TaskEvaluationDetailView(APIView):
    """
    GET /api/tasks/evaluations/{evaluation_id}/
    Get evaluation details for a completed task.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request, evaluation_id):
        try:
            evaluation = TaskEvaluation.objects.get(pk=evaluation_id)
        except TaskEvaluation.DoesNotExist:
            return Response(
                {'success': False, 'error': {'code': 404, 'message': 'Evaluation not found.'}},
                status=status.HTTP_404_NOT_FOUND,
            )

        # Verify user owns this evaluation or is mentor
        assignment = evaluation.task_completion.task_assignment
        if assignment.student != request.user and not request.user.groups.filter(name='Mentor').exists():
            return Response(
                {'success': False, 'error': {'code': 403, 'message': 'Unauthorized.'}},
                status=status.HTTP_403_FORBIDDEN,
            )

        serializer = TaskEvaluationSerializer(evaluation)
        return Response({
            'success': True,
            'data': serializer.data
        })


class MentorEvaluateTaskView(APIView):
    """
    POST /api/tasks/evaluations/{evaluation_id}/evaluate/
    Mentor submits manual evaluation with score and feedback.
    """
    permission_classes = [IsAuthenticated, IsMentor]

    def post(self, request, evaluation_id):
        try:
            evaluation = TaskEvaluation.objects.get(pk=evaluation_id)
        except TaskEvaluation.DoesNotExist:
            return Response(
                {'success': False, 'error': {'code': 404, 'message': 'Evaluation not found.'}},
                status=status.HTTP_404_NOT_FOUND,
            )

        assignment = evaluation.task_completion.task_assignment

        # Verify mentor is assigned to student
        if assignment.student.studentprofile.mentor_assigned != request.user:
            return Response(
                {'success': False, 'error': {'code': 403, 'message': 'This student is not assigned to you.'}},
                status=status.HTTP_403_FORBIDDEN,
            )

        serializer = TaskEvaluationUpdateSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(
                {'success': False, 'error': {'code': 400, 'message': serializer.errors}},
                status=status.HTTP_400_BAD_REQUEST,
            )

        mentor_score = serializer.validated_data['mentor_score']
        
        # Calculate final score (average of MCQ and mentor scores)
        final_score = (evaluation.mcq_score + mentor_score) / 2

        # Update evaluation
        evaluation.mentor_score = mentor_score
        evaluation.final_score = final_score
        evaluation.mentor_feedback = serializer.validated_data.get('mentor_feedback', '')
        evaluation.strengths = serializer.validated_data.get('strengths', [])
        evaluation.weaknesses = serializer.validated_data.get('weaknesses', [])
        evaluation.suggestions = serializer.validated_data.get('suggestions', [])
        evaluation.evaluated_by = request.user
        evaluation.evaluated_at = timezone.now()
        evaluation.status = 'evaluated'
        evaluation.save()

        # Auto-generate portfolio item when evaluation is completed
        try:
            portfolio_item = PortfolioService.create_portfolio_item(evaluation)
        except Exception as e:
            # Log error but don't fail the evaluation
            print(f"Error creating portfolio item: {str(e)}")

        result_serializer = TaskEvaluationSerializer(evaluation)
        return Response({
            'success': True,
            'message': 'Task evaluation completed.',
            'data': result_serializer.data
        })


class GetMyPortfolioView(APIView):
    """
    GET /api/portfolios/me/
    Get current user's portfolio.
    """
    permission_classes = [IsAuthenticated, IsStudent]

    def get(self, request):
        """Retrieve student's portfolio."""
        try:
            portfolio = Portfolio.objects.get(student=request.user)
        except Portfolio.DoesNotExist:
            return Response({
                'success': False,
                'message': 'Portfolio not found. Complete a task evaluation to generate one.'
            }, status=status.HTTP_404_NOT_FOUND)

        serializer = PortfolioDetailSerializer(portfolio)
        return Response({
            'success': True,
            'data': serializer.data
        })


class PortfolioDetailView(APIView):
    """
    GET /api/portfolios/<id>/
    Get specific portfolio (if public or own).
    """
    permission_classes = [IsAuthenticated]

    def get(self, request, portfolio_id):
        """Retrieve portfolio details."""
        try:
            portfolio = Portfolio.objects.get(id=portfolio_id)
        except Portfolio.DoesNotExist:
            return Response({
                'success': False,
                'message': 'Portfolio not found.'
            }, status=status.HTTP_404_NOT_FOUND)

        # Check permissions: own portfolio or public
        if portfolio.user != request.user and not portfolio.is_public:
            return Response({
                'success': False,
                'message': 'You do not have permission to view this portfolio.'
            }, status=status.HTTP_403_FORBIDDEN)

        serializer = PortfolioDetailSerializer(portfolio)
        return Response({
            'success': True,
            'data': serializer.data
        })


class UpdatePortfolioView(APIView):
    """
    PUT /api/portfolios/<id>/update/
    Update portfolio info (title, bio, visibility).
    """
    permission_classes = [IsAuthenticated, IsStudent]

    def put(self, request, portfolio_id):
        """Update portfolio."""
        try:
            portfolio = Portfolio.objects.get(id=portfolio_id)
        except Portfolio.DoesNotExist:
            return Response({
                'success': False,
                'message': 'Portfolio not found.'
            }, status=status.HTTP_404_NOT_FOUND)

        # Check ownership
        if portfolio.user != request.user:
            return Response({
                'success': False,
                'message': 'You can only update your own portfolio.'
            }, status=status.HTTP_403_FORBIDDEN)

        serializer = PortfolioUpdateSerializer(portfolio, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({
                'success': True,
                'message': 'Portfolio updated successfully.',
                'data': PortfolioDetailSerializer(portfolio).data
            })

        return Response({
            'success': False,
            'errors': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)


class PortfolioItemDetailView(APIView):
    """
    GET /api/portfolio-items/<id>/
    Get portfolio item details.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request, item_id):
        """Retrieve portfolio item details."""
        try:
            item = PortfolioItem.objects.get(id=item_id)
        except PortfolioItem.DoesNotExist:
            return Response({
                'success': False,
                'message': 'Portfolio item not found.'
            }, status=status.HTTP_404_NOT_FOUND)

        # Check permissions: own item or public portfolio
        if item.portfolio.user != request.user and not item.portfolio.is_public:
            return Response({
                'success': False,
                'message': 'You do not have permission to view this item.'
            }, status=status.HTTP_403_FORBIDDEN)

        serializer = PortfolioItemDetailSerializer(item)
        return Response({
            'success': True,
            'data': serializer.data
        })


class UpdatePortfolioItemView(APIView):
    """
    PUT /api/portfolio-items/<id>/update/
    Update portfolio item display settings.
    """
    permission_classes = [IsAuthenticated, IsStudent]

    def put(self, request, item_id):
        """Update portfolio item."""
        try:
            item = PortfolioItem.objects.get(id=item_id)
        except PortfolioItem.DoesNotExist:
            return Response({
                'success': False,
                'message': 'Portfolio item not found.'
            }, status=status.HTTP_404_NOT_FOUND)

        # Check ownership
        if item.portfolio.user != request.user:
            return Response({
                'success': False,
                'message': 'You can only update your own portfolio items.'
            }, status=status.HTTP_403_FORBIDDEN)

        serializer = PortfolioItemUpdateSerializer(item, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({
                'success': True,
                'message': 'Portfolio item updated successfully.',
                'data': PortfolioItemDetailSerializer(item).data
            })

        return Response({
            'success': False,
            'errors': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)


class PortfolioStatsView(APIView):
    """
    GET /api/portfolios/<id>/stats/
    Get portfolio statistics and analytics.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request, portfolio_id):
        """Retrieve portfolio statistics."""
        try:
            portfolio = Portfolio.objects.get(id=portfolio_id)
        except Portfolio.DoesNotExist:
            return Response({
                'success': False,
                'message': 'Portfolio not found.'
            }, status=status.HTTP_404_NOT_FOUND)

        # Check permissions
        if portfolio.user != request.user and not portfolio.is_public:
            return Response({
                'success': False,
                'message': 'You do not have permission to view this portfolio.'
            }, status=status.HTTP_403_FORBIDDEN)

        stats = PortfolioService.get_portfolio_stats(portfolio)
        return Response({
            'success': True,
            'data': stats
        })


class ExportPortfolioView(APIView):
    """
    GET /api/portfolios/<id>/export/
    Export portfolio data as JSON.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request, portfolio_id):
        """Export portfolio."""
        try:
            portfolio = Portfolio.objects.get(id=portfolio_id)
        except Portfolio.DoesNotExist:
            return Response({
                'success': False,
                'message': 'Portfolio not found.'
            }, status=status.HTTP_404_NOT_FOUND)

        # Check permissions
        if portfolio.user != request.user and not portfolio.is_public:
            return Response({
                'success': False,
                'message': 'You do not have permission to export this portfolio.'
            }, status=status.HTTP_403_FORBIDDEN)

        export_data = PortfolioService.export_portfolio_as_json(portfolio)
        return Response({
            'success': True,
            'data': export_data
        })
