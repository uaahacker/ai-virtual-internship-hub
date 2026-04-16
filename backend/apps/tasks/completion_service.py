"""
Task Completion and Evaluation Service.

Handles business logic for:
- Task completion workflow
- MCQ scoring calculations
- Final evaluation scoring (MCQ + mentor)
- Performance analysis and feedback
"""

from django.utils import timezone
from django.db import models
from .models import (
    TaskAssignment, TaskCompletion, TaskMCQ, TaskMCQAttempt, TaskEvaluation
)


class TaskCompletionService:
    """Service for managing task completion and evaluation workflow."""

    @staticmethod
    def mark_task_complete(assignment, reflective_text=''):
        """
        Mark a task assignment as completed and create completion record.
        
        Args:
            assignment: TaskAssignment instance
            reflective_text: Optional reflection from student
            
        Returns:
            TaskCompletion instance
        """
        assignment.status = 'completed'
        assignment.completed_at = timezone.now()
        assignment.save()

        completion = TaskCompletion.objects.create(
            task_assignment=assignment,
            reflective_text=reflective_text,
            completed_at=timezone.now(),
        )
        
        return completion

    @staticmethod
    def calculate_mcq_score(student_answers, task):
        """
        Calculate MCQ score from student answers.
        
        Args:
            student_answers: Dict {question_id: answer_choice}
            task: Task instance
            
        Returns:
            Dict with score, correct_count, total_count
        """
        mcq_questions = TaskMCQ.objects.filter(
            task=task,
            is_active=True
        ).values('id', 'correct_answer')

        correct_count = 0
        total_count = mcq_questions.count()

        for question in mcq_questions:
            q_id = str(question['id'])
            if q_id in student_answers:
                if student_answers[q_id] == question['correct_answer']:
                    correct_count += 1

        # Calculate score (0-100)
        mcq_score = (correct_count / total_count * 100) if total_count > 0 else 0
        
        return {
            'mcq_score': mcq_score,
            'correct_count': correct_count,
            'total_count': total_count,
            'percentage': round((correct_count / total_count * 100), 2) if total_count > 0 else 0,
        }

    @staticmethod
    def create_mcq_attempt(completion, student_answers, duration_seconds=0):
        """
        Create a TaskMCQAttempt record and calculate score.
        
        Args:
            completion: TaskCompletion instance
            student_answers: Dict {question_id: answer_choice}
            duration_seconds: Time taken in seconds
            
        Returns:
            TaskMCQAttempt instance with calculated score
        """
        task = completion.task_assignment.task
        score_data = TaskCompletionService.calculate_mcq_score(student_answers, task)

        attempt = TaskMCQAttempt.objects.create(
            task_completion=completion,
            student_answers=student_answers,
            total_questions=score_data['total_count'],
            correct_answers=score_data['correct_count'],
            mcq_score=score_data['mcq_score'],
            duration_seconds=duration_seconds,
            is_submitted=True,
            submitted_at=timezone.now(),
        )
        
        return attempt

    @staticmethod
    def create_initial_evaluation(completion, mcq_score):
        """
        Create initial TaskEvaluation after MCQ submission.
        MCQ score becomes the initial final score (will be updated when mentor evaluates).
        
        Args:
            completion: TaskCompletion instance
            mcq_score: Float 0-100
            
        Returns:
            TaskEvaluation instance
        """
        evaluation = TaskEvaluation.objects.create(
            task_completion=completion,
            mcq_score=mcq_score,
            final_score=mcq_score,  # Initially, final = MCQ score
            status='pending',  # Pending mentor evaluation
        )
        
        return evaluation

    @staticmethod
    def complete_mentor_evaluation(evaluation, mentor_score, mentor_feedback='', 
                                  strengths=None, weaknesses=None, suggestions=None,
                                  evaluated_by=None):
        """
        Complete evaluation with mentor feedback and scoring.
        Calculates final_score as average of MCQ and mentor scores.
        
        Args:
            evaluation: TaskEvaluation instance
            mentor_score: Float 0-100
            mentor_feedback: Text feedback
            strengths: List of strengths
            weaknesses: List of weaknesses
            suggestions: List of suggestions
            evaluated_by: User (mentor) instance
            
        Returns:
            Updated TaskEvaluation instance
        """
        if strengths is None:
            strengths = []
        if weaknesses is None:
            weaknesses = []
        if suggestions is None:
            suggestions = []

        # Calculate final score (average of MCQ + mentor scores)
        final_score = (evaluation.mcq_score + mentor_score) / 2

        evaluation.mentor_score = mentor_score
        evaluation.final_score = final_score
        evaluation.mentor_feedback = mentor_feedback
        evaluation.strengths = strengths
        evaluation.weaknesses = weaknesses
        evaluation.suggestions = suggestions
        evaluation.evaluated_by = evaluated_by
        evaluation.evaluated_at = timezone.now()
        evaluation.status = 'evaluated'
        evaluation.save()
        
        return evaluation

    @staticmethod
    def get_performance_analysis(mcq_score, mentor_score=None):
        """
        Analyze performance based on scores.
        
        Args:
            mcq_score: Float 0-100
            mentor_score: Float 0-100 or None
            
        Returns:
            Dict with performance insights
        """
        final_score = mcq_score
        if mentor_score is not None:
            final_score = (mcq_score + mentor_score) / 2

        # Determine performance level
        if final_score >= 90:
            performance_level = 'Excellent'
            color = 'green'
        elif final_score >= 80:
            performance_level = 'Very Good'
            color = 'blue'
        elif final_score >= 70:
            performance_level = 'Good'
            color = 'cyan'
        elif final_score >= 60:
            performance_level = 'Fair'
            color = 'yellow'
        else:
            performance_level = 'Needs Improvement'
            color = 'red'

        return {
            'final_score': final_score,
            'performance_level': performance_level,
            'color': color,
            'mcq_score': mcq_score,
            'mentor_score': mentor_score,
        }

    @staticmethod
    def get_student_task_stats(student):
        """
        Get statistics for student's completed and evaluated tasks.
        
        Args:
            student: User instance (student)
            
        Returns:
            Dict with task statistics
        """
        completed_tasks = TaskCompletion.objects.filter(
            task_assignment__student=student
        ).count()

        evaluated_tasks = TaskEvaluation.objects.filter(
            status__in=['evaluated', 'approved'],
            task_completion__task_assignment__student=student
        ).count()

        # Calculate average scores
        evaluations = TaskEvaluation.objects.filter(
            status__in=['evaluated', 'approved'],
            task_completion__task_assignment__student=student
        ).values('mcq_score', 'mentor_score', 'final_score')

        avg_mcq_score = 0
        avg_final_score = 0
        
        if evaluations.count() > 0:
            avg_mcq_score = sum(e['mcq_score'] for e in evaluations) / evaluations.count()
            final_scores = [e['final_score'] for e in evaluations if e['final_score']]
            if final_scores:
                avg_final_score = sum(final_scores) / len(final_scores)

        return {
            'total_completed_tasks': completed_tasks,
            'total_evaluated_tasks': evaluated_tasks,
            'average_mcq_score': round(avg_mcq_score, 2),
            'average_final_score': round(avg_final_score, 2),
            'completion_rate': round((completed_tasks / max(TaskCompletion.objects.filter(
                task_assignment__student=student
            ).count(), 1)) * 100, 2),
        }
