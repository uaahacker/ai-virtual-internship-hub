"""
Migration: Create Task and TaskAssignment models with recommendation system.

Creates:
  - Task model: title, domain, difficulty, required_skills, task_type, learning_outcomes
  - TaskAssignment model: student, task, assigned_by, status, progress, mentor_review
"""

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Task',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=255)),
                ('description', models.TextField()),
                ('domain', models.CharField(
                    choices=[
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
                    ],
                    max_length=50,
                )),
                ('difficulty', models.CharField(
                    choices=[
                        ('Beginner', 'Beginner'),
                        ('Intermediate', 'Intermediate'),
                        ('Advanced', 'Advanced'),
                    ],
                    max_length=15,
                )),
                ('task_type', models.CharField(
                    choices=[
                        ('Design', 'Design Project'),
                        ('Development', 'Development Project'),
                        ('Content', 'Content Creation'),
                        ('Analysis', 'Data Analysis'),
                        ('Marketing', 'Marketing Campaign'),
                        ('Research', 'Research Task'),
                        ('Other', 'Other'),
                    ],
                    max_length=20,
                )),
                ('required_skills', models.JSONField(default=list, help_text='List of skills needed')),
                ('learning_outcomes', models.JSONField(default=list, help_text='What student will learn')),
                ('estimated_duration', models.IntegerField(help_text='Estimated duration in minutes')),
                ('is_active', models.BooleanField(default=True)),
                ('created_at', models.DateTimeField(default=django.utils.timezone.now)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('created_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='tasks_created', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'db_table': 'tasks',
                'ordering': ['-created_at'],
            },
        ),
        migrations.CreateModel(
            name='TaskAssignment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('status', models.CharField(
                    choices=[
                        ('recommended', 'Recommended'),
                        ('accepted', 'Accepted'),
                        ('in_progress', 'In Progress'),
                        ('completed', 'Completed'),
                        ('declined', 'Declined'),
                    ],
                    default='recommended',
                    max_length=20,
                )),
                ('progress_percentage', models.IntegerField(default=0, help_text='0-100% progress on task')),
                ('recommended_score', models.FloatField(default=0.0, help_text='Score 0-100 indicating match quality')),
                ('recommendation_reason', models.TextField(blank=True, default='', help_text='Why this task was recommended')),
                ('mentor_review_requested', models.BooleanField(default=False)),
                ('mentor_review_status', models.CharField(
                    choices=[
                        ('not_requested', 'Not Requested'),
                        ('requested', 'Requested'),
                        ('approved', 'Approved'),
                        ('needs_revision', 'Needs Revision'),
                    ],
                    default='not_requested',
                    max_length=20,
                )),
                ('mentor_feedback', models.TextField(blank=True, default='', help_text='Mentor review feedback')),
                ('created_at', models.DateTimeField(default=django.utils.timezone.now)),
                ('accepted_at', models.DateTimeField(blank=True, null=True)),
                ('started_at', models.DateTimeField(blank=True, null=True)),
                ('completed_at', models.DateTimeField(blank=True, null=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('assigned_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='assignments_created', to=settings.AUTH_USER_MODEL)),
                ('student', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='task_assignments', to=settings.AUTH_USER_MODEL)),
                ('task', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='assignments', to='tasks.task')),
            ],
            options={
                'db_table': 'task_assignments',
                'ordering': ['-created_at'],
                'unique_together': {('student', 'task')},
            },
        ),
    ]
