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
    TaskMCQCreateSerializer,
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


class MentorTaskListView(APIView):
    """GET /tasks/mentor-tasks/ — list tasks created by the logged-in mentor."""
    permission_classes = [IsAuthenticated, IsMentor]

    def get(self, request):
        tasks = Task.objects.filter(created_by=request.user).order_by('-created_at')
        serializer = TaskSerializer(tasks, many=True)
        return Response({'success': True, 'data': serializer.data})


class MentorTaskManageView(APIView):
    """
    PUT  /tasks/mentor-tasks/<pk>/  — update own task
    DELETE /tasks/mentor-tasks/<pk>/ — delete own task
    """
    permission_classes = [IsAuthenticated, IsMentor]

    def _get_own_task(self, pk, user):
        try:
            return Task.objects.get(pk=pk, created_by=user)
        except Task.DoesNotExist:
            return None

    def get(self, request, pk):
        task = self._get_own_task(pk, request.user)
        if not task:
            return Response(
                {'success': False, 'error': 'Task not found or not yours.'},
                status=status.HTTP_404_NOT_FOUND,
            )
        return Response({'success': True, 'data': TaskSerializer(task).data})

    def put(self, request, pk):
        task = self._get_own_task(pk, request.user)
        if not task:
            return Response(
                {'success': False, 'error': 'Task not found or not yours.'},
                status=status.HTTP_404_NOT_FOUND,
            )
        serializer = TaskCreateSerializer(task, data=request.data, partial=True)
        if not serializer.is_valid():
            return Response({'success': False, 'error': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
        task = serializer.save()
        return Response({'success': True, 'data': TaskSerializer(task).data})

    def delete(self, request, pk):
        task = self._get_own_task(pk, request.user)
        if not task:
            return Response(
                {'success': False, 'error': 'Task not found or not yours.'},
                status=status.HTTP_404_NOT_FOUND,
            )
        task_title = task.title
        task.delete()
        return Response({'success': True, 'message': f'Task "{task_title}" deleted.'})


class MentorTaskMCQView(APIView):
    """
    GET  /tasks/mentor-tasks/<task_id>/mcq/  — list all MCQ questions for a task (with answers)
    POST /tasks/mentor-tasks/<task_id>/mcq/  — add a new question
    Mentor must own the task.
    """
    permission_classes = [IsAuthenticated, IsMentor]

    def _get_own_task(self, task_id, user):
        try:
            return Task.objects.get(pk=task_id, created_by=user)
        except Task.DoesNotExist:
            return None

    def get(self, request, task_id):
        task = self._get_own_task(task_id, request.user)
        if not task:
            return Response({'success': False, 'error': 'Task not found or not yours.'}, status=status.HTTP_404_NOT_FOUND)
        questions = TaskMCQ.objects.filter(task=task).order_by('order')
        serializer = TaskMCQCreateSerializer(questions, many=True)
        return Response({'success': True, 'data': {'task_id': task.id, 'task_title': task.title, 'questions': serializer.data}})

    def post(self, request, task_id):
        task = self._get_own_task(task_id, request.user)
        if not task:
            return Response({'success': False, 'error': 'Task not found or not yours.'}, status=status.HTTP_404_NOT_FOUND)
        serializer = TaskMCQCreateSerializer(data=request.data)
        if not serializer.is_valid():
            return Response({'success': False, 'error': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
        question = serializer.save(task=task)
        return Response({'success': True, 'data': TaskMCQCreateSerializer(question).data}, status=status.HTTP_201_CREATED)


class MentorTaskMCQDetailView(APIView):
    """
    PUT    /tasks/mentor-tasks/<task_id>/mcq/<question_id>/  — update a question
    DELETE /tasks/mentor-tasks/<task_id>/mcq/<question_id>/  — delete a question
    Mentor must own the task.
    """
    permission_classes = [IsAuthenticated, IsMentor]

    def _get_question(self, task_id, question_id, user):
        try:
            task = Task.objects.get(pk=task_id, created_by=user)
            return TaskMCQ.objects.get(pk=question_id, task=task)
        except (Task.DoesNotExist, TaskMCQ.DoesNotExist):
            return None

    def put(self, request, task_id, question_id):
        question = self._get_question(task_id, question_id, request.user)
        if not question:
            return Response({'success': False, 'error': 'Question not found.'}, status=status.HTTP_404_NOT_FOUND)
        serializer = TaskMCQCreateSerializer(question, data=request.data, partial=True)
        if not serializer.is_valid():
            return Response({'success': False, 'error': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
        question = serializer.save()
        return Response({'success': True, 'data': TaskMCQCreateSerializer(question).data})

    def delete(self, request, task_id, question_id):
        question = self._get_question(task_id, question_id, request.user)
        if not question:
            return Response({'success': False, 'error': 'Question not found.'}, status=status.HTTP_404_NOT_FOUND)
        question.delete()
        return Response({'success': True})


class RecommendedTasksView(APIView):
    permission_classes = [IsAuthenticated, IsStudent]

    def get(self, request):
        try:
            student = request.user
            recommendations = TaskRecommendationService.get_recommendations_for_student(student, limit=10)
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
                        'recommendation_explanation': rec.get('explanation', {}),
                    }
                )
                # Refresh explanation on existing assignments (scores may have improved)
                if not created and rec.get('explanation'):
                    assignment.recommended_score = rec['score']
                    assignment.recommendation_reason = rec['reason']
                    assignment.recommendation_explanation = rec['explanation']
                    assignment.save(update_fields=[
                        'recommended_score', 'recommendation_reason',
                        'recommendation_explanation',
                    ])
                serializer = RecommendedTaskSerializer(assignment)
                result.append(serializer.data)
            
            # If no new recommendations, show already-recommended tasks
            if not result:
                existing_recommended = TaskAssignment.objects.filter(
                    student=student, 
                    status='recommended'
                ).select_related('task')
                for assignment in existing_recommended:
                    serializer = RecommendedTaskSerializer(assignment)
                    result.append(serializer.data)
            
            return Response({'success': True, 'data': result})
        except Exception as e:
            import traceback
            error_trace = traceback.format_exc()
            print(f"Error in RecommendedTasksView: {str(e)}\n{error_trace}")
            return Response(
                {'success': False, 'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


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
        portfolio = PortfolioService.get_or_create_portfolio(request.user)
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
        overview = PortfolioService.generate_portfolio_overview(portfolio)
        return Response({'success': True, 'data': {**stats, 'overview': overview}})


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


class TaskRecommendationExplanationView(APIView):
    """
    GET /tasks/assignments/<id>/explanation/
    Returns the structured per-component explanation for a recommended task.
    Students can only access their own assignments.
    Mentors/Admins can access any assignment.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request, assignment_id):
        try:
            assignment = TaskAssignment.objects.select_related('task', 'student').get(
                pk=assignment_id
            )
        except TaskAssignment.DoesNotExist:
            return Response(
                {'success': False, 'error': 'Assignment not found.'},
                status=status.HTTP_404_NOT_FOUND,
            )

        # Permission: students see only their own; mentors/admins see all
        if request.user.role == 'Student' and assignment.student_id != request.user.id:
            return Response(
                {'success': False, 'error': 'Permission denied.'},
                status=status.HTTP_403_FORBIDDEN,
            )

        explanation = assignment.recommendation_explanation or {}

        # If empty (old record), recompute live
        if not explanation:
            from .ml_engine import explain_recommendation, ContentBasedRecommender
            student_vec = ContentBasedRecommender.build_student_vector_from_db(
                assignment.student
            )
            explanation = explain_recommendation(
                student=assignment.student,
                task=assignment.task,
                student_vec=student_vec,
            )
            assignment.recommendation_explanation = explanation
            assignment.save(update_fields=['recommendation_explanation'])

        return Response({
            'success': True,
            'data': {
                'assignment_id': assignment.id,
                'task_title': assignment.task.title,
                'task_domain': assignment.task.domain,
                'recommended_score': assignment.recommended_score,
                'recommendation_reason': assignment.recommendation_reason,
                'explanation': explanation,
            },
        })
