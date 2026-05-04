"""Analytics service layer for generating analytics data"""
from django.db.models import Avg, Count, Q, F
from django.utils import timezone
from datetime import timedelta
from .models import TaskAssignment, TaskEvaluation, TaskCompletion, TaskMCQAttempt
from apps.accounts.models import StudentProfile, MentorProfile, User
from .ml_engine import DomainPredictor


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
        
        # Cluster info from student profile
        cluster_info = {}
        try:
            profile = student.student_profile
            cluster_info = {
                'cluster_id':      profile.cluster_id,
                'cluster_label':   profile.cluster_label,
                'cluster_summary': profile.cluster_summary or {},
            }
        except Exception:
            pass

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
            'cluster_info': cluster_info,
        }

    @staticmethod
    def get_domain_predictions(student):
        """
        Return ML-predicted domain recommendations for this student.
        Calls DomainPredictor which uses recency-weighted scoring + softmax.
        """
        try:
            return DomainPredictor.predict(student)
        except Exception:
            return []


class MentorAnalyticsService:
    """Service for mentor-specific analytics"""

    @staticmethod
    def get_mentor_analytics(mentor):
        """Get comprehensive analytics for a mentor"""
        from apps.accounts.models import StudentProfile

        # Total assigned students
        assigned_students = StudentProfile.objects.filter(
            mentor_assigned=mentor
        ).count()

        # Get mentor's student IDs to avoid deep ORM traversals
        mentor_student_ids = list(
            StudentProfile.objects.filter(mentor_assigned=mentor)
            .values_list('user_id', flat=True)
        )

        # Pending mentor reviews (via TaskAssignment — avoids cross-collection join)
        pending_reviews = (
            TaskAssignment.objects.filter(
                student_id__in=mentor_student_ids,
                mentor_review_requested=True,
                mentor_review_status='requested',
            ).count()
            if mentor_student_ids else 0
        )

        # Student performance overview — evaluations done by mentor
        student_evaluations = TaskEvaluation.objects.filter(
            evaluated_by=mentor,
            status='evaluated',
        )

        students_performance = {}
        domain_distribution = {}
        total_score = 0.0
        eval_count = 0

        for eval_obj in student_evaluations:
            try:
                tc = eval_obj.task_completion
                ta = tc.task_assignment
                student = ta.student
                domain = ta.task.domain
            except Exception:
                continue

            if student.id not in students_performance:
                students_performance[student.id] = {
                    'name': student.name,
                    'email': student.email,
                    'tasks_evaluated': 0,
                    'scores': [],
                    'average_score': 0,
                }

            students_performance[student.id]['tasks_evaluated'] += 1
            students_performance[student.id]['scores'].append(eval_obj.final_score)
            total_score += eval_obj.final_score
            eval_count += 1
            domain_distribution[domain] = domain_distribution.get(domain, 0) + 1

        # Calculate per-student averages
        for perf in students_performance.values():
            if perf['scores']:
                perf['average_score'] = round(sum(perf['scores']) / len(perf['scores']), 2)
            del perf['scores']  # Remove raw scores from response

        # Add cluster info to each student entry
        if students_performance:
            profiles_map = {
                p.user_id: p
                for p in StudentProfile.objects.filter(
                    user_id__in=list(students_performance.keys())
                )
            }
            for sid, perf in students_performance.items():
                profile = profiles_map.get(sid)
                if profile:
                    summary = profile.cluster_summary or {}
                    perf['cluster_label']        = profile.cluster_label
                    perf['cluster_display_name'] = summary.get('display_name', profile.cluster_label)
                else:
                    perf['cluster_label']        = 'Explorer'
                    perf['cluster_display_name'] = 'Explorer'

        avg_score = round(total_score / eval_count, 2) if eval_count > 0 else 0.0

        return {
            'total_assigned_students': assigned_students,
            'pending_reviews': pending_reviews,
            'students_performance': list(students_performance.values()),
            'domain_distribution': domain_distribution,
            'total_tasks_reviewed': eval_count,
            'average_task_score': avg_score,
        }


class AdminAnalyticsService:
    """Service for admin-specific analytics"""

    @staticmethod
    def get_admin_analytics():
        """Get comprehensive analytics for admin"""
        
        # Total users by role
        total_students = User.objects.filter(role='Student').count()
        total_mentors = User.objects.filter(role='Mentor').count()
        total_admins = User.objects.filter(role='Admin').count()
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
        
        # Mentor load distribution (pure Python to avoid Djongo cross-collection join issues)
        mentor_load_list = []
        for mp in MentorProfile.objects.select_related('user'):
            student_count = StudentProfile.objects.filter(mentor_assigned=mp.user).count()
            eval_count = TaskEvaluation.objects.filter(
                evaluated_by=mp.user, status='evaluated'
            ).count()
            mentor_load_list.append({
                'mentor_id': mp.user.id,
                'mentor_name': mp.user.name,
                'students_assigned': student_count,
                'evaluations_completed': eval_count,
            })
        
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
        
        # Enhanced cluster distribution — computed in Python to avoid
        # cross-collection joins and JSON field aggregations in MongoDB.
        all_profiles = list(StudentProfile.objects.all())

        # group by cluster_id
        from collections import defaultdict
        cluster_groups: dict = defaultdict(list)
        for p in all_profiles:
            cluster_groups[p.cluster_id].append(p)

        _CLUSTER_ORDER = {0: 'Explorer', 1: 'Developing', 2: 'Competent', 3: 'Expert'}
        _CLUSTER_GENERIC_NAME = {
            0: 'Early Explorers',
            1: 'Developing Learners',
            2: 'Skilled Practitioners',
            3: 'High Achievers',
        }

        cluster_breakdown = []
        for cid in sorted(_CLUSTER_ORDER.keys()):
            group = cluster_groups.get(cid, [])
            count = len(group)
            avg_scores = [
                p.cluster_summary.get('avg_assessment_score', 0)
                for p in group
                if p.cluster_summary
            ]
            avg_score = round(sum(avg_scores) / len(avg_scores), 1) if avg_scores else 0.0
            # Use first non-generic display_name found in group as representative
            display_names = [
                p.cluster_summary.get('display_name', '')
                for p in group
                if p.cluster_summary and p.cluster_summary.get('display_name')
            ]
            display_name = _CLUSTER_GENERIC_NAME.get(cid, _CLUSTER_ORDER.get(cid, ''))
            cluster_breakdown.append({
                'label':        _CLUSTER_ORDER.get(cid, str(cid)),
                'count':        count,
                'display_name': display_name,
                'avg_score':    avg_score,
            })

        return {
            'system_metrics': system_metrics,
            'popular_domains': popular_domains,
            'mentor_load_distribution': mentor_load_list,
            'student_cluster_distribution': cluster_breakdown,
        }
