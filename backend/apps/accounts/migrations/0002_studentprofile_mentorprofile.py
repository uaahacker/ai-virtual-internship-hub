# Generated migration for StudentProfile and MentorProfile models

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='StudentProfile',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('bio', models.TextField(blank=True, default='')),
                ('selected_skills', models.JSONField(default=list, help_text='List of skill names student is interested in')),
                ('preferred_domains', models.JSONField(default=list, help_text='List of preferred learning domains')),
                ('assessment_summary', models.JSONField(default=dict, help_text='Summary of assessment attempts {domain: [scores]}')),
                ('skill_scores_by_domain', models.JSONField(default=dict, help_text='Highest score per domain {domain: score}')),
                ('strongest_domain', models.CharField(blank=True, default='', help_text='Domain with highest score', max_length=100)),
                ('weakest_domain', models.CharField(blank=True, default='', help_text='Domain with lowest score', max_length=100)),
                ('progress_score', models.FloatField(default=0.0, help_text='Overall progress score (0-100)')),
                ('completed_tasks_count', models.IntegerField(default=0, help_text='Number of tasks completed')),
                ('created_at', models.DateTimeField(default=django.utils.timezone.now)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('mentor_assigned', models.ForeignKey(blank=True, help_text='Assigned mentor, if any', limit_choices_to={'role': 'Mentor'}, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='mentored_students', to=settings.AUTH_USER_MODEL)),
                ('user', models.OneToOneField(limit_choices_to={'role': 'Student'}, on_delete=django.db.models.deletion.CASCADE, related_name='student_profile', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Student Profile',
                'verbose_name_plural': 'Student Profiles',
                'db_table': 'student_profiles',
            },
        ),
        migrations.CreateModel(
            name='MentorProfile',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('expertise_domains', models.JSONField(default=list, help_text='List of domains mentor specializes in')),
                ('bio', models.TextField(blank=True, default='', help_text='Mentor biography')),
                ('max_students', models.IntegerField(default=10, help_text='Maximum number of students mentor can supervise')),
                ('current_student_count', models.IntegerField(default=0, help_text='Current number of assigned students')),
                ('rating', models.FloatField(default=0.0, help_text='Mentor rating (0-5) based on student feedback')),
                ('created_at', models.DateTimeField(default=django.utils.timezone.now)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('user', models.OneToOneField(limit_choices_to={'role': 'Mentor'}, on_delete=django.db.models.deletion.CASCADE, related_name='mentor_profile', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Mentor Profile',
                'verbose_name_plural': 'Mentor Profiles',
                'db_table': 'mentor_profiles',
            },
        ),
    ]
