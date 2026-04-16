"""
Portfolio Service - handles portfolio generation and management.

Functions:
- Auto-generate portfolio items when tasks are completed
- Create/update portfolio summaries
- Calculate portfolio statistics
"""

from django.utils import timezone
from apps.portfolios.models import Portfolio, PortfolioItem


class PortfolioService:
    """Service for managing portfolio generation and updates."""

    @staticmethod
    def get_or_create_portfolio(student):
        """
        Get existing portfolio or create one for student.
        
        Args:
            student: User instance (student)
            
        Returns:
            Portfolio instance
        """
        portfolio, created = Portfolio.objects.get_or_create(
            user=student,
            defaults={
                'title': f"{student.name}'s Portfolio",
            }
        )
        return portfolio

    @staticmethod
    def generate_project_summary(task_title, task_description, duration_minutes, task_type):
        """
        Generate concise professional project summary.
        Template-based, no hallucination.
        
        Args:
            task_title: Title of the task
            task_description: Task description
            duration_minutes: Estimated duration
            task_type: Type of task (Design, Development, etc.)
            
        Returns:
            Concise summary string
        """
        # Template-based summaries - no AI hallucination
        templates = {
            'Design': "Completed {title}, a design project focused on creating visual solutions. Implemented design principles and deliverables as per project requirements within the estimated timeframe.",
            'Development': "Developed {title}, implementing technical features and functionality. Applied programming concepts and best practices to deliver a working solution.",
            'Content': "Created {title}, producing high-quality content. Researched, wrote, and refined content to meet project specifications and guidelines.",
            'Analysis': "Conducted {title}, analyzing data and providing insights. Used analytical tools and methods to extract meaningful information from datasets.",
            'Marketing': "Executed {title}, implementing marketing strategies and campaigns. Coordinated marketing activities and measured campaign effectiveness.",
            'Research': "Conducted research for {title}, gathering and synthesizing information. Used research methodologies to support project objectives.",
            'Other': "Completed {title}, fulfilling project requirements and deliverables within the specified timeline."
        }

        template = templates.get(task_type, templates['Other'])
        summary = template.format(title=task_title)
        
        return summary

    @staticmethod
    def generate_mentor_feedback_summary(mentor_feedback, strengths, weaknesses, suggestions):
        """
        Extract key points from mentor feedback for portfolio display.
        
        Args:
            mentor_feedback: Full mentor feedback text
            strengths: List of strengths
            weaknesses: List of weaknesses
            suggestions: List of suggestions
            
        Returns:
            Concise summary of feedback
        """
        if not mentor_feedback:
            return ""
        
        # Take first 300 characters of mentor feedback as summary
        # Clean up whitespace
        summary = mentor_feedback.strip()
        if len(summary) > 300:
            summary = summary[:297] + "..."
        
        return summary

    @staticmethod
    def generate_strengths_summary(strengths):
        """
        Convert strengths list to formatted bullet string.
        
        Args:
            strengths: List of strength strings
            
        Returns:
            Formatted bullet-point string
        """
        if not strengths:
            return ""
        
        # Format as bullet points
        bullets = "\n".join([f"• {s}" for s in strengths[:5]])  # Max 5 items
        return bullets

    @staticmethod
    def create_portfolio_item(task_evaluation):
        """
        Create a portfolio item from a completed task evaluation.
        
        Args:
            task_evaluation: TaskEvaluation instance
            
        Returns:
            PortfolioItem instance
        """
        student = task_evaluation.task_completion.task_assignment.student
        task = task_evaluation.task_completion.task_assignment.task
        completion = task_evaluation.task_completion

        # Get or create portfolio
        portfolio = PortfolioService.get_or_create_portfolio(student)

        # Generate summaries
        project_summary = PortfolioService.generate_project_summary(
            task.title,
            task.description,
            task.estimated_duration,
            task.task_type,
        )

        mentor_feedback_summary = PortfolioService.generate_mentor_feedback_summary(
            task_evaluation.mentor_feedback,
            task_evaluation.strengths,
            task_evaluation.weaknesses,
            task_evaluation.suggestions,
        )

        strengths_summary = PortfolioService.generate_strengths_summary(
            task_evaluation.strengths
        )

        # Get required skills from task
        skills_demonstrated = task.required_skills or []

        # Create portfolio item
        portfolio_item = PortfolioItem.objects.create(
            portfolio=portfolio,
            task_evaluation=task_evaluation,
            task_title=task.title,
            task_domain=task.domain,
            task_difficulty=task.difficulty,
            task_type=task.task_type,
            completion_date=completion.completed_at,
            evaluation_date=task_evaluation.evaluated_at or timezone.now(),
            mcq_score=task_evaluation.mcq_score,
            mentor_score=task_evaluation.mentor_score,
            final_score=task_evaluation.final_score,
            skills_demonstrated=skills_demonstrated,
            student_reflection=completion.reflective_text,
            project_summary=project_summary,
            mentor_feedback_summary=mentor_feedback_summary,
            strengths_summary=strengths_summary,
            display_order=portfolio.total_items,  # Add to end
        )

        # Update portfolio statistics
        PortfolioService.update_portfolio_stats(portfolio)

        return portfolio_item

    @staticmethod
    def update_portfolio_stats(portfolio):
        """
        Recalculate portfolio statistics.
        
        Args:
            portfolio: Portfolio instance
        """
        items = portfolio.items.all()
        
        # Count items
        total_items = items.count()
        portfolio.total_items = total_items

        # Calculate average score
        if total_items > 0:
            avg_score = sum(item.final_score for item in items) / total_items
            portfolio.average_score = round(avg_score, 2)
        else:
            portfolio.average_score = 0.0

        portfolio.save()

    @staticmethod
    def get_portfolio_stats(portfolio):
        """
        Get comprehensive portfolio statistics.
        
        Args:
            portfolio: Portfolio instance
            
        Returns:
            Dict with statistics
        """
        items = portfolio.items.all()

        # Domain breakdown
        domain_counts = {}
        for item in items:
            domain = item.task_domain
            domain_counts[domain] = domain_counts.get(domain, 0) + 1

        # Difficulty breakdown
        difficulty_counts = {}
        for item in items:
            difficulty = item.task_difficulty
            difficulty_counts[difficulty] = difficulty_counts.get(difficulty, 0) + 1

        # Score statistics
        if items.count() > 0:
            scores = [item.final_score for item in items]
            avg_score = sum(scores) / len(scores)
            max_score = max(scores)
            min_score = min(scores)
        else:
            avg_score = 0
            max_score = 0
            min_score = 0

        # Skills aggregation
        all_skills = []
        for item in items:
            all_skills.extend(item.skills_demonstrated)
        
        # Count skill occurrences
        skill_counts = {}
        for skill in all_skills:
            skill_counts[skill] = skill_counts.get(skill, 0) + 1

        return {
            'total_items': items.count(),
            'average_score': round(avg_score, 2),
            'max_score': max_score,
            'min_score': min_score,
            'by_domain': domain_counts,
            'by_difficulty': difficulty_counts,
            'top_skills': sorted(skill_counts.items(), key=lambda x: x[1], reverse=True)[:10],
        }

    @staticmethod
    def export_portfolio_as_json(portfolio):
        """
        Export portfolio data as JSON for sharing/archiving.
        
        Args:
            portfolio: Portfolio instance
            
        Returns:
            Dict with portfolio data
        """
        items = portfolio.items.all()

        return {
            'portfolio': {
                'title': portfolio.title,
                'student': portfolio.user.name if hasattr(portfolio.user, 'name') else portfolio.user.username,
                'bio': portfolio.bio,
                'created_at': portfolio.created_at.isoformat(),
                'total_items': portfolio.total_items,
                'average_score': portfolio.average_score,
            },
            'items': [
                {
                    'task_title': item.task_title,
                    'domain': item.task_domain,
                    'difficulty': item.task_difficulty,
                    'completion_date': item.completion_date.isoformat(),
                    'final_score': item.final_score,
                    'project_summary': item.project_summary,
                    'skills': item.skills_demonstrated,
                }
                for item in items
            ],
            'statistics': PortfolioService.get_portfolio_stats(portfolio),
        }
