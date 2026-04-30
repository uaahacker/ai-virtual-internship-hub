"""Analytics service layer for generating analytics data"""
from django.db.models import Avg, Count, Q, F
from django.utils import timezone
from datetime import timedelta
from .models import TaskAssignment, TaskEvaluation, TaskCompletion, TaskMCQAttempt
from apps.accounts.models import StudentProfile, MentorProfile, User


class StudentAnalyticsService:
    """Service for student-specific analytics"""

    @staticmethod
    def get_student_analytics(student):
        """Get comprehensive analytics for a student"""
        
        # Total assessments attempted
        assessments_attempted = student.assessment_attempts.count()
        
        # Get all completed tasks with evaluations  
        completed_tasks = TaskAssignment.objects.filter(
            student=student, 
            status='completed'
        ).select_related('task', 'task_completion')
        
        evaluations = TaskEvaluation.objects.filter(
            task_completion__task_assignment__student=student,
            status='evaluated'
        )
        
        # Completed tasks count
        completed_tasks_count = completed_tasks.count()
        
        # Calculate averages and domain stats
        domain_stats = {}
        mcq_scores = []
        final_scores = []
        
        for eval_obj in evaluations:
            task = eval_obj.task_completion.task_assignment.task
            domain = task.domain
            
            if domain not in domain_stats:
                domain_stats[domain] = {
                    'count': 0,
                    'total_score': 0,
                    'scores': []
                }
            
            domain_stats[domain]['count'] += 1
            domain_stats[domain]['total_score'] += eval_obj.final_score
            domain_stats[domain]['scores'].append(eval_obj.final_score)
            
            mcq_scores.append(eval_obj.mcq_score)
            final_scores.append(eval_obj.final_score)
        
        # Calculate domain averages
        for domain in domain_stats:
            domain_stats[domain]['average'] = (
                domain_stats[domain]['total_score'] / domain_stats[domain]['count']
                if domain_stats[domain]['count'] > 0 else 0
            )
        
        # Find strongest and weakest domains
        strongest_domain = None
        weakest_domain = None
        strongest_score = -1
        weakest_score = 101
        
        for domain, stats in domain_stats.items():
            if stats['average'] > strongest_score:
                strongest_score = stats['average']
                strongest_domain = domain
            if stats['average'] < weakest_score:
                weakest_score = stats['average']
                weakest_domain = domain
        
        # Average scores
        avg_mcq_score = sum(mcq_scores) / len(mcq_scores) if mcq_scores else 0
        avg_final_score = sum(final_scores) / len(final_scores) if final_scores else 0
        
        # Get skill improvement trend (last 5 evaluations)  
        recent_evaluations = evaluations.order_by('-evaluated_at')[:5]
        skill_trend = [
            {
                'date': e.evaluated_at.strftime('%Y-%m-%d'),
                'score': e.final_score,
                'task': e.task_completion.task_assignment.task.title
            }
            for e in reversed(recent_evaluations)
        ]
        
        # Recommend next domain (domain with least attempts)
        recommended_domain = None
        min_attempts = float('inf')
        
        all_domains = ['Graphic Design', 'Content Writing', 'Programming', 'Freelancing', 'Marketing', 'Research', 'Software']
        
        for domain in all_domains:
            domain_count = domain_stats.get(domain, {}).get('count', 0)
            if domain_count < min_attempts:
                min_attempts = domain_count
                recommended_domain = domain
        
        return {
            'total_assessments_attempted': assessments_attempted,
            'completed_tasks': completed_tasks_count,
            'average_mcq_score': round(avg_mcq_score, 2),
            'average_final_score': round(avg_final_score, 2),
            'strongest_domain': strongest_domain,
            'strongest_domain_score': round(strongest_score, 2) if strongest_score >= 0 else None,
            'weakest_domain': weakest_domain,
            'weakest_domain_score': round(weakest_score, 2) if weakest_score <= 100 else None,
            'domain_breakdown': {
                domain: {
                    'tasks_completed': stats['count'],
                    'average_score': round(stats['average'], 2),
                    'scores': [round(s, 2) for s in stats['scores']]
                }
                for domain, stats in domain_stats.items()
            },
            'skill_improvement_trend': skill_trend,
            'recommended_next_domain': recommended_domain or 'Programming',
        }


class MentorAnalyticsService:
    """Service for mentor-specific analytics"""

    @staticmethod
    def get_mentor_analytics(mentor):
        """Get comprehensive analytics for a mentor"""
        
        # Total assigned students
        assigned_students = StudentProfile.objects.filter(
            mentor_assigned=mentor
        ).count()
        
        # Pending mentor reviews
        pending_reviews = TaskEvaluation.objects.filter(
            evaluated_by__isnull=True,
            task_completion__task_assignment__student__studentprofile__mentor_assigned=mentor
        ).count()
        
        # Student performance overview
        student_evaluations = TaskEvaluation.objects.filter(
            evaluated_by=mentor,
            status='evaluated'
        ).select_related('task_completion__task_assignment__student')
        
        students_performance = {}
        domain_distribution = {}
        
        for eval_obj in student_evaluations:
            student = eval_obj.task_completion.task_assignment.student
            domain = eval_obj.task_completion.task_assignment.task.domain
            
            if student.id not in students_performance:
                students_performance[student.id] = {
                    'name': student.get_full_name() or student.username,
                    'email': student.email,
                    'tasks_evaluated': 0,
                    'scores': [],
                    'average_score': 0
                }
            
            students_performance[student.id]['tasks_evaluated'] += 1
            students_performance[student.id]['scores'].append(eval_obj.final_score)
            
            if domain not in domain_distribution:
                domain_distribution[domain] = 0
            domain_distribution[domain] += 1
        
        # Calculate averages
        for student_id, perf in students_performance.items():
            if perf['scores']:
                perf['average_score'] = round(sum(perf['scores']) / len(perf['scores']), 2)
            del perf['scores']  # Remove individual scores from response
        
        return {
            'total_assigned_students': assigned_students,
            'pending_mentor_reviews': pending_reviews,
            'students_performance': list(students_performance.values()),
            'domain_wise_student_distribution': domain_distribution,
            'total_evaluations_completed': student_evaluations.count(),
        }


class AdminAnalyticsService:
    """Service for admin-specific analytics"""

    @staticmethod
    def get_admin_analytics():
        """Get comprehensive analytics for admin"""
        
        # Total users by role
        total_students = User.objects.filter(groups__name='Student').count()
        total_mentors = User.objects.filter(groups__name='Mentor').count()
        total_admins = User.objects.filter(groups__name='Admin').count()
        total_users = total_students + total_mentors + total_admins
        
        # Assessments attempted
        from apps.assessments.models import AssessmentAttempt
        assessments_attempted = AssessmentAttempt.objects.count()
        
        # Most popular domains
        domain_tasks = TaskAssignment.objects.filter(
            status='completed'
        ).values('task__domain').annotate(
            count=Count('id')
        ).order_by('-count')[:10]
        
        popular_domains = [
            {'domain': item['task__domain'], 'count': item['count']}
            for item in domain_tasks
        ]
        
        # Tasks completed
        tasks_completed = TaskAssignment.objects.filter(status='completed').count()
        
        # Mentor load distribution
        mentor_load = MentorProfile.objects.annotate(
            student_count=Count('user__studentprofile'),
            evaluations_count=Count(
                'user__taskevaluation',
                filter=Q(user__taskevaluation__status='evaluated')
            )
        ).values('user__id', 'user__get_full_name', 'student_count', 'evaluations_count')
        
        mentor_load_list = [
            {
                'mentor_id': item['user__id'],
                'mentor_name': item['user__get_full_name'],
                'students_assigned': item['student_count'],
                'evaluations_completed': item['evaluations_count']
            }
            for item in mentor_load
        ]
        
        # Average student performance
        all_evaluations = TaskEvaluation.objects.filter(
            status='evaluated'
        )
        
        avg_performance = 0
        if all_evaluations.exists():
            avg_performance = round(
                all_evaluations.aggregate(
                    avg_score=Avg('final_score')
                )['avg_score'], 2
            )
        
        # System metrics
        system_metrics = {
            'total_users': total_users,
            'total_students': total_students,
            'total_mentors': total_mentors,
            'total_admins': total_admins,
            'assessments_attempts': assessments_attempted,
            'tasks_completed': tasks_completed,
            'average_system_performance': avg_performance,
            'total_evaluations': all_evaluations.count(),
        }
        
        return {
            'system_metrics': system_metrics,
            'popular_domains': popular_domains,
            'mentor_load_distribution': mentor_load_list,
        }
