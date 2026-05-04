"""
Migration: Add concept/difficulty-weight to Question;
           add rich evaluation fields to AssessmentAttempt.

New Question fields:
  - concept          (CharField, blank, default '')
  - difficulty_weight (FloatField, default 1.0)

New AssessmentAttempt fields:
  - concept_scores        (JSONField)
  - domain_score          (FloatField)
  - readiness_level       (CharField)
  - skill_profile_vector  (JSONField)
  - improvement_delta     (FloatField, nullable)
  - recommended_task_type (CharField)
"""

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('assessments', '0002_assessmentattempt_enhanced'),
    ]

    operations = [
        # ── Question extensions ────────────────────────────────────────────
        migrations.AddField(
            model_name='question',
            name='concept',
            field=models.CharField(
                blank=True,
                default='',
                help_text='Concept or sub-topic this question tests',
                max_length=100,
            ),
        ),
        migrations.AddField(
            model_name='question',
            name='difficulty_weight',
            field=models.FloatField(
                default=1.0,
                help_text='Scoring weight relative to other questions (default 1.0)',
            ),
        ),
        # ── AssessmentAttempt extensions ──────────────────────────────────
        migrations.AddField(
            model_name='assessmentattempt',
            name='concept_scores',
            field=models.JSONField(
                blank=True,
                default=dict,
                help_text='Per-concept score breakdown {concept: {correct, total, score_pct}}',
            ),
        ),
        migrations.AddField(
            model_name='assessmentattempt',
            name='domain_score',
            field=models.FloatField(
                default=0.0,
                help_text='Weighted domain score (0-100) using question difficulty weights',
            ),
        ),
        migrations.AddField(
            model_name='assessmentattempt',
            name='readiness_level',
            field=models.CharField(
                default='Novice',
                help_text='5-tier readiness level derived from weighted domain score',
                max_length=15,
            ),
        ),
        migrations.AddField(
            model_name='assessmentattempt',
            name='skill_profile_vector',
            field=models.JSONField(
                blank=True,
                default=dict,
                help_text='Normalised proficiency per concept {concept: 0.0-1.0}',
            ),
        ),
        migrations.AddField(
            model_name='assessmentattempt',
            name='improvement_delta',
            field=models.FloatField(
                blank=True,
                null=True,
                help_text='Percentage-point change from previous attempt in this domain',
            ),
        ),
        migrations.AddField(
            model_name='assessmentattempt',
            name='recommended_task_type',
            field=models.CharField(
                default='practice',
                help_text='Recommended task type based on readiness level',
                max_length=20,
            ),
        ),
    ]
