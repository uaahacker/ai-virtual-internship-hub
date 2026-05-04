"""
Assessment views – student-protected endpoints.
"""

from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from apps.core.permissions import IsStudent
from apps.accounts.models import StudentProfile
from .models import Assessment, Question, AssessmentAttempt
from .serializers import (
    AssessmentListSerializer,
    AssessmentDetailSerializer,
    SubmitAnswersSerializer,
    AttemptResultSerializer,
)
from .recommendation import generate_recommendation, calculate_performance_breakdown
from .nlp_feedback import generate_feedback, generate_structured_feedback
from .evaluation_engine import evaluate as run_evaluation
from apps.tasks.ml_engine import StudentClusterer


def _update_student_domain_profile(user):
    """
    Recompute and persist domain summary fields on StudentProfile from ALL
    assessment attempts.  Called after every submission so that:
      - StudentProfile.strongest_domain / weakest_domain stay current
      - StudentProfile.skill_scores_by_domain reflects best score per domain
      - StudentProfile.assessment_summary holds full score history per domain
      - StudentProfile.preferred_domains includes every attempted domain
    """
    all_attempts = (
        AssessmentAttempt.objects
        .filter(student=user)
        .select_related('assessment')
    )

    domain_best: dict = {}          # domain → best domain_score (0-100)
    assessment_summary: dict = {}   # domain → [scores list]

    for a in all_attempts:
        d = a.assessment.domain
        score = float(a.domain_score)
        # Keep highest score per domain
        if d not in domain_best or score > domain_best[d]:
            domain_best[d] = score
        if d not in assessment_summary:
            assessment_summary[d] = []
        assessment_summary[d].append(score)

    if not domain_best:
        return

    profile, _ = StudentProfile.objects.get_or_create(user=user)

    strongest = max(domain_best, key=domain_best.get)
    weakest   = min(domain_best, key=domain_best.get)

    # Merge attempted domains into preferred_domains (keep existing + add new)
    existing_preferred = list(profile.preferred_domains or [])
    merged_preferred = list(dict.fromkeys(existing_preferred + list(domain_best.keys())))

    profile.strongest_domain     = strongest
    profile.weakest_domain       = weakest
    profile.skill_scores_by_domain = domain_best
    profile.assessment_summary   = assessment_summary
    profile.preferred_domains    = merged_preferred
    profile.save(update_fields=[
        'strongest_domain', 'weakest_domain',
        'skill_scores_by_domain', 'assessment_summary', 'preferred_domains',
    ])


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

        # Fetch cluster context for richer feedback
        _cluster_label = 'Explorer'
        _completed_tasks = 0
        try:
            _sp = request.user.student_profile
            _cluster_label = _sp.cluster_label or 'Explorer'
            _completed_tasks = _sp.completed_tasks_count or 0
        except Exception:
            pass

        # Generate structured NLP feedback (local, no external API)
        nlp_feedback = generate_structured_feedback(
            domain=assessment.domain,
            percentage=percentage,
            skill_level=skill_level,
            correct_count=correct,
            total_count=total,
            readiness_level=eval_result['readiness_level'],
            suggested_task_type=eval_result['recommended_task_type'],
            strengths=eval_result['strength_tags'],
            weaknesses=eval_result['weakness_tags'],
            improvement_areas=next_steps,
            concept_scores=eval_result['concept_scores'],
            attempt_number=attempt_number,
            previous_percentage=previous_percentage,
            improvement_delta=eval_result['improvement_delta'],
            cluster_label=_cluster_label,
            completed_tasks_count=_completed_tasks,
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
            feedback=nlp_feedback,
        )

        # 5.1) Update student cluster (async-safe — must not block submission)
        try:
            StudentClusterer.update_student_cluster(request.user)
        except Exception:
            pass

        # 5.2) Sync StudentProfile domain summary fields so mentor filtering,
        #      auto-assign, and the AI chatbot all see up-to-date domain data.
        try:
            _update_student_domain_profile(request.user)
        except Exception:
            pass

        # 6) Return result
        result = AttemptResultSerializer(attempt).data
        result['recommendation'] = recommendation
        # feedback is already inside result (from serializer)

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
        # Regenerate structured feedback if not yet stored (old attempts)
        if not result.get('feedback'):
            try:
                result['feedback'] = generate_structured_feedback(
                    domain=attempt.assessment.domain,
                    percentage=float(attempt.percentage),
                    skill_level=attempt.skill_level,
                    correct_count=attempt.score,
                    total_count=attempt.total_questions,
                    readiness_level=attempt.readiness_level,
                    suggested_task_type=attempt.recommended_task_type,
                    strengths=attempt.strengths,
                    weaknesses=attempt.weaknesses,
                    concept_scores=attempt.concept_scores or {},
                )
            except Exception:
                pass
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


# ──────────────────────────────────────────────────────────────
# Admin Assessment Management
# ──────────────────────────────────────────────────────────────

from apps.core.permissions import IsAdmin


class AdminAssessmentListView(APIView):
    """
    GET  /api/assessments/admin/  – list ALL assessments (incl. inactive) with question counts
    POST /api/assessments/admin/  – create a new assessment
    """
    permission_classes = [IsAuthenticated, IsAdmin]

    def get(self, request):
        assessments = Assessment.objects.all().order_by('domain', 'title')
        data = []
        for a in assessments:
            q_count = Question.objects.filter(assessment=a).count()
            data.append({
                'id': a.id,
                'title': a.title,
                'domain': a.domain,
                'description': a.description,
                'time_limit': a.time_limit,
                'is_active': a.is_active,
                'question_count': q_count,
                'created_at': a.created_at.isoformat(),
            })
        return Response({'success': True, 'data': data})

    def post(self, request):
        title = request.data.get('title', '').strip()
        domain = request.data.get('domain', '').strip()
        description = request.data.get('description', '').strip()
        time_limit = request.data.get('time_limit')
        is_active = request.data.get('is_active', True)

        if not title or not domain:
            return Response(
                {'success': False, 'error': {'code': 400, 'message': 'title and domain are required.'}},
                status=status.HTTP_400_BAD_REQUEST,
            )

        valid_domains = [d[0] for d in Assessment.DOMAIN_CHOICES]
        if domain not in valid_domains:
            return Response(
                {'success': False, 'error': {'code': 400, 'message': f'Invalid domain. Choose from: {", ".join(valid_domains)}'}},
                status=status.HTTP_400_BAD_REQUEST,
            )

        assessment = Assessment.objects.create(
            title=title,
            domain=domain,
            description=description,
            time_limit=time_limit if time_limit else None,
            is_active=is_active,
            created_by=request.user,
        )
        return Response({
            'success': True,
            'message': 'Assessment created successfully.',
            'data': {
                'id': assessment.id,
                'title': assessment.title,
                'domain': assessment.domain,
                'description': assessment.description,
                'time_limit': assessment.time_limit,
                'is_active': assessment.is_active,
                'question_count': 0,
                'created_at': assessment.created_at.isoformat(),
            }
        }, status=status.HTTP_201_CREATED)


class AdminAssessmentManageView(APIView):
    """
    GET    /api/assessments/admin/<pk>/  – fetch single assessment with all questions (incl. correct answers)
    PUT    /api/assessments/admin/<pk>/  – update assessment metadata + optionally replace questions
    DELETE /api/assessments/admin/<pk>/  – delete assessment
    PATCH  /api/assessments/admin/<pk>/  – toggle is_active
    """
    permission_classes = [IsAuthenticated, IsAdmin]

    def _get_assessment(self, pk):
        try:
            return Assessment.objects.get(pk=pk)
        except Assessment.DoesNotExist:
            return None

    def get(self, request, pk):
        assessment = self._get_assessment(pk)
        if not assessment:
            return Response({'success': False, 'error': {'code': 404, 'message': 'Assessment not found.'}},
                            status=status.HTTP_404_NOT_FOUND)
        questions = Question.objects.filter(assessment=assessment).order_by('order')
        questions_data = [
            {
                'id': q.id,
                'text': q.text,
                'option_a': q.option_a,
                'option_b': q.option_b,
                'option_c': q.option_c,
                'option_d': q.option_d,
                'correct_option': q.correct_option,
                'order': q.order,
            }
            for q in questions
        ]
        return Response({'success': True, 'data': {
            'id': assessment.id,
            'title': assessment.title,
            'domain': assessment.domain,
            'description': assessment.description,
            'time_limit': assessment.time_limit,
            'is_active': assessment.is_active,
            'questions': questions_data,
            'created_at': assessment.created_at.isoformat(),
        }})

    def put(self, request, pk):
        assessment = self._get_assessment(pk)
        if not assessment:
            return Response({'success': False, 'error': {'code': 404, 'message': 'Assessment not found.'}},
                            status=status.HTTP_404_NOT_FOUND)

        for field in ['title', 'domain', 'description', 'time_limit', 'is_active']:
            if field in request.data:
                setattr(assessment, field, request.data[field] if request.data[field] != '' else getattr(assessment, field))
        assessment.save()

        return Response({'success': True, 'message': 'Assessment updated.', 'data': {
            'id': assessment.id, 'title': assessment.title, 'domain': assessment.domain,
            'is_active': assessment.is_active, 'time_limit': assessment.time_limit,
        }})

    def patch(self, request, pk):
        """Toggle is_active."""
        assessment = self._get_assessment(pk)
        if not assessment:
            return Response({'success': False, 'error': {'code': 404, 'message': 'Assessment not found.'}},
                            status=status.HTTP_404_NOT_FOUND)
        assessment.is_active = not assessment.is_active
        assessment.save(update_fields=['is_active'])
        return Response({'success': True, 'message': f'Assessment {"activated" if assessment.is_active else "deactivated"}.', 'data': {'is_active': assessment.is_active}})

    def delete(self, request, pk):
        assessment = self._get_assessment(pk)
        if not assessment:
            return Response({'success': False, 'error': {'code': 404, 'message': 'Assessment not found.'}},
                            status=status.HTTP_404_NOT_FOUND)
        assessment.delete()
        return Response({'success': True, 'message': 'Assessment deleted successfully.'})


class AdminAssessmentQuestionView(APIView):
    """
    POST   /api/assessments/admin/<pk>/questions/  – add a question to an assessment
    DELETE /api/assessments/admin/<pk>/questions/<qid>/  – remove a specific question
    """
    permission_classes = [IsAuthenticated, IsAdmin]

    def post(self, request, pk):
        try:
            assessment = Assessment.objects.get(pk=pk)
        except Assessment.DoesNotExist:
            return Response({'success': False, 'error': {'code': 404, 'message': 'Assessment not found.'}},
                            status=status.HTTP_404_NOT_FOUND)

        required = ['text', 'option_a', 'option_b', 'option_c', 'option_d', 'correct_option']
        for f in required:
            if not request.data.get(f, '').strip():
                return Response({'success': False, 'error': {'code': 400, 'message': f'{f} is required.'}},
                                status=status.HTTP_400_BAD_REQUEST)

        if request.data['correct_option'].upper() not in ('A', 'B', 'C', 'D'):
            return Response({'success': False, 'error': {'code': 400, 'message': 'correct_option must be A, B, C or D.'}},
                            status=status.HTTP_400_BAD_REQUEST)

        last_order = Question.objects.filter(assessment=assessment).count()
        q = Question.objects.create(
            assessment=assessment,
            text=request.data['text'],
            option_a=request.data['option_a'],
            option_b=request.data['option_b'],
            option_c=request.data['option_c'],
            option_d=request.data['option_d'],
            correct_option=request.data['correct_option'].upper(),
            order=last_order + 1,
        )
        return Response({'success': True, 'message': 'Question added.', 'data': {
            'id': q.id, 'text': q.text, 'correct_option': q.correct_option, 'order': q.order,
        }}, status=status.HTTP_201_CREATED)


class AdminAssessmentQuestionDeleteView(APIView):
    """DELETE /api/assessments/admin/<pk>/questions/<qid>/"""
    permission_classes = [IsAuthenticated, IsAdmin]

    def delete(self, request, pk, qid):
        try:
            q = Question.objects.get(pk=qid, assessment_id=pk)
        except Question.DoesNotExist:
            return Response({'success': False, 'error': {'code': 404, 'message': 'Question not found.'}},
                            status=status.HTTP_404_NOT_FOUND)
        q.delete()
        return Response({'success': True, 'message': 'Question deleted.'})


class AdminTaskListView(APIView):
    """
    GET /api/assessments/admin/tasks/  – list all tasks (admin view with full details)
    """
    permission_classes = [IsAuthenticated, IsAdmin]

    def get(self, request):
        from apps.tasks.models import Task, TaskAssignment
        tasks = Task.objects.all().order_by('-created_at')
        data = []
        for t in tasks:
            assignment_count = TaskAssignment.objects.filter(task=t).count()
            completed_count = TaskAssignment.objects.filter(task=t, status='completed').count()
            data.append({
                'id': t.id,
                'title': t.title,
                'domain': t.domain,
                'difficulty': t.difficulty,
                'is_active': t.is_active,
                'estimated_duration': t.estimated_duration,
                'assignment_count': assignment_count,
                'completed_count': completed_count,
                'created_at': t.created_at.isoformat() if t.created_at else None,
            })
        return Response({'success': True, 'data': data})


class AdminTaskToggleView(APIView):
    """PATCH /api/assessments/admin/tasks/<pk>/toggle/ – toggle task active status"""
    permission_classes = [IsAuthenticated, IsAdmin]

    def patch(self, request, pk):
        from apps.tasks.models import Task
        try:
            task = Task.objects.get(pk=pk)
        except Task.DoesNotExist:
            return Response({'success': False, 'error': {'code': 404, 'message': 'Task not found.'}},
                            status=status.HTTP_404_NOT_FOUND)
        task.is_active = not task.is_active
        task.save(update_fields=['is_active'])
        return Response({'success': True, 'message': f'Task {"activated" if task.is_active else "deactivated"}.', 'data': {'is_active': task.is_active}})

