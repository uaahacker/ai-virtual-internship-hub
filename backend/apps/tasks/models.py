"""
Task Management models for internship-style task recommendations and tracking.

Collections:
  - tasks: title, domain, difficulty, required_skills, task_type, learning_outcomes
  - task_assignments: student, task, assigned_by, status, progress, mentor_review
"""

from django.db import models
from django.conf import settings
from django.utils import timezone


class Task(models.Model):
    """
    Represents an internship-style task/project assigned to students.
    Maps to 'tasks' collection.
    """

    DOMAIN_CHOICES = [
        ('Graphic Design', 'Graphic Design'),
        ('Content Writing', 'Content Writing'),
        ('Programming', 'Programming'),
        ('Freelancing', 'Freelancing'),
        ('E-Commerce', 'E-Commerce'),
        ('QuickBooks', 'QuickBooks'),
        ('AutoCAD', 'AutoCAD'),
        ('Data Analytics', 'Data Analytics'),
        ('Digital Marketing', 'Digital Marketing'),
        ('WordPress', 'WordPress'),
    ]

    DIFFICULTY_CHOICES = [
        ('Beginner', 'Beginner'),
        ('Intermediate', 'Intermediate'),
        ('Advanced', 'Advanced'),
    ]

    TASK_TYPE_CHOICES = [
        ('Design', 'Design Project'),
        ('Development', 'Development Project'),
        ('Content', 'Content Creation'),
        ('Analysis', 'Data Analysis'),
        ('Marketing', 'Marketing Campaign'),
        ('Research', 'Research Task'),
        ('Other', 'Other'),
    ]

    # Basic Info
    title = models.CharField(max_length=255)
    description = models.TextField()
    domain = models.CharField(max_length=50, choices=DOMAIN_CHOICES)
    difficulty = models.CharField(max_length=15, choices=DIFFICULTY_CHOICES)
    task_type = models.CharField(max_length=20, choices=TASK_TYPE_CHOICES)

    # Learning & Skills
    required_skills = models.JSONField(
        default=list,
        help_text='List of skills needed (e.g., ["Illustrator", "Color Theory"])',
    )
    learning_outcomes = models.JSONField(
        default=list,
        help_text='What student will learn (e.g., ["Master typography", "Design logos"])',
    )

    # Timeline
    estimated_duration = models.IntegerField(
        help_text='Estimated duration in minutes',
    )

    # Status
    is_active = models.BooleanField(default=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='tasks_created',
    )
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'tasks'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.title} ({self.domain} - {self.difficulty})"


class TaskAssignment(models.Model):
    """
    Tracks a task assignment to a student, including recommendation.
    Maps to 'task_assignments' collection.
    """

    STATUS_CHOICES = [
        ('recommended', 'Recommended'),
        ('accepted', 'Accepted'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('declined', 'Declined'),
    ]

    MENTOR_REVIEW_CHOICES = [
        ('not_requested', 'Not Requested'),
        ('requested', 'Requested'),
        ('approved', 'Approved'),
        ('needs_revision', 'Needs Revision'),
    ]

    # Core Relations
    student = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='task_assignments',
    )
    task = models.ForeignKey(
        Task,
        on_delete=models.CASCADE,
        related_name='assignments',
    )
    assigned_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='assignments_created',
    )

    # Status Tracking
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='recommended',
    )
    progress_percentage = models.IntegerField(
        default=0,
        help_text='0-100% progress on task',
    )

    # Recommendation Score
    recommended_score = models.FloatField(
        default=0.0,
        help_text='Score 0-100 indicating how well matched this task is',
    )
    recommendation_reason = models.TextField(
        blank=True,
        default='',
        help_text='Why this task was recommended to the student',
    )
    recommendation_explanation = models.JSONField(
        default=dict,
        help_text='Structured per-component explanation of the recommendation score',
    )

    # Mentor Review
    mentor_review_requested = models.BooleanField(default=False)
    mentor_review_status = models.CharField(
        max_length=20,
        choices=MENTOR_REVIEW_CHOICES,
        default='not_requested',
    )
    mentor_feedback = models.TextField(
        blank=True,
        default='',
        help_text='Mentor\'s review feedback',
    )

    # Timestamps
    created_at = models.DateTimeField(default=timezone.now)
    accepted_at = models.DateTimeField(null=True, blank=True)
    started_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'task_assignments'
        ordering = ['-created_at']
        unique_together = ('student', 'task')  # Prevent duplicate assignments

    def __str__(self):
        return f"{self.task.title} -> {self.student.name} ({self.status})"


class TaskMCQ(models.Model):
    """
    MCQ questions for task follow-up evaluation.
    Each task can have multiple MCQ questions to assess learning.
    """

    DIFFICULTY_CHOICES = [
        ('Easy', 'Easy'),
        ('Medium', 'Medium'),
        ('Hard', 'Hard'),
    ]

    task = models.ForeignKey(
        Task,
        on_delete=models.CASCADE,
        related_name='mcq_questions',
        help_text='Task this MCQ belongs to',
    )

    # Question Content
    question_text = models.TextField(
        help_text='The MCQ question',
    )
    difficulty = models.CharField(
        max_length=10,
        choices=DIFFICULTY_CHOICES,
        default='Medium',
    )

    # Options (A, B, C, D)
    option_a = models.TextField()
    option_b = models.TextField()
    option_c = models.TextField()
    option_d = models.TextField()

    # Correct Answer
    correct_answer = models.CharField(
        max_length=1,
        choices=[('A', 'A'), ('B', 'B'), ('C', 'C'), ('D', 'D')],
    )

    # Explanation & Help
    explanation = models.TextField(
        blank=True,
        default='',
        help_text='Explanation for the correct answer',
    )

    # Order
    order = models.IntegerField(
        default=0,
        help_text='Question order within the quiz',
    )

    # Status
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'task_mcq_questions'
        ordering = ['task', 'order']

    def __str__(self):
        return f"Q{self.order + 1}: {self.question_text[:50]}... ({self.task.title})"


class TaskCompletion(models.Model):
    """
    Records when a student marks a task as completed.
    Includes reflective text about what they learned.
    """

    task_assignment = models.OneToOneField(
        TaskAssignment,
        on_delete=models.CASCADE,
        related_name='completion',
        help_text='The task assignment being completed',
    )

    # Completion Info
    completed_at = models.DateTimeField(default=timezone.now)
    reflective_text = models.TextField(
        blank=True,
        default='',
        help_text='Student\'s reflection on what they learned',
    )

    # Status
    is_submitted = models.BooleanField(default=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'task_completions'
        ordering = ['-completed_at']

    def __str__(self):
        return f"Completion: {self.task_assignment.task.title} by {self.task_assignment.student.name}"


class TaskMCQAttempt(models.Model):
    """
    Records student's answers to MCQ questions for a task completion.
    Calculates MCQ score based on correct answers.
    """

    task_completion = models.OneToOneField(
        TaskCompletion,
        on_delete=models.CASCADE,
        related_name='mcq_attempt',
        help_text='The task completion this MCQ attempt belongs to',
    )

    # Answers (stored as JSONField: {mcq_id: "A", mcq_id: "B", ...})
    student_answers = models.JSONField(
        default=dict,
        help_text='Student\'s MCQ answers: {question_id: "answer_choice"}',
    )

    # Score Calculation
    total_questions = models.IntegerField(default=0)
    correct_answers = models.IntegerField(default=0)
    mcq_score = models.FloatField(
        default=0.0,
        help_text='Score calculated from MCQ: 0-100',
    )

    # Timing
    started_at = models.DateTimeField(auto_now_add=True)
    submitted_at = models.DateTimeField(null=True, blank=True)
    duration_seconds = models.IntegerField(
        default=0,
        help_text='Time taken to complete quiz in seconds',
    )

    # Status
    is_submitted = models.BooleanField(default=False)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'task_mcq_attempts'
        ordering = ['-submitted_at']

    def __str__(self):
        task_title = self.task_completion.task_assignment.task.title
        student_name = self.task_completion.task_assignment.student.name
        return f"MCQ Attempt: {task_title} by {student_name} (Score: {self.mcq_score})"


class TaskEvaluation(models.Model):
    """
    Final evaluation of a completed task combining:
    - MCQ performance score
    - Mentor manual review score
    - Learning assessment
    """

    STATUS_CHOICES = [
        ('pending', 'Pending Evaluation'),
        ('evaluated', 'Evaluated'),
        ('approved', 'Approved'),
        ('needs_revision', 'Needs Revision'),
    ]

    task_completion = models.OneToOneField(
        TaskCompletion,
        on_delete=models.CASCADE,
        related_name='evaluation',
        help_text='The task completion being evaluated',
    )

    # Score Components
    mcq_score = models.FloatField(
        default=0.0,
        help_text='Score from MCQ: 0-100',
    )
    mentor_score = models.FloatField(
        null=True,
        blank=True,
        help_text='Manual score from mentor: 0-100 (null if not yet evaluated)',
    )
    final_score = models.FloatField(
        default=0.0,
        help_text='Final combined score: 0-100 (avg of MCQ + mentor, or MCQ if no mentor)',
    )

    # Feedback Components
    mentor_feedback = models.TextField(
        blank=True,
        default='',
        help_text='Detailed feedback from mentor',
    )
    strengths = models.JSONField(
        default=list,
        help_text='List of student\'s strengths demonstrated in task',
    )
    weaknesses = models.JSONField(
        default=list,
        help_text='List of areas for improvement',
    )
    suggestions = models.JSONField(
        default=list,
        help_text='List of suggestions for improvement',
    )

    # Status Tracking
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending',
    )
    evaluated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='task_evaluations_given',
        help_text='Mentor who evaluated this task',
    )
    evaluated_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text='When mentor completed the evaluation',
    )

    # Timestamps
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'task_evaluations'
        ordering = ['-created_at']

    def __str__(self):
        task_title = self.task_completion.task_assignment.task.title
        student_name = self.task_completion.task_assignment.student.name
        return f"Evaluation: {task_title} by {student_name} (Final: {self.final_score})"
