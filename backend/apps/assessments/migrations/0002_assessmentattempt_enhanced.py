"""
Migration: Add enhanced assessment fields for detailed scoring and recommendations.

Adds:
  - detailed_breakdown: Per-question analysis
  - strengths: List of strengths
  - weaknesses: List of areas to improve
  - next_steps: Actionable next steps
"""

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('assessments', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='assessmentattempt',
            name='detailed_breakdown',
            field=models.JSONField(blank=True, default=dict, help_text='Per-question analysis {question_id: {text, submitted, correct, explanation}}'),
        ),
        migrations.AddField(
            model_name='assessmentattempt',
            name='strengths',
            field=models.JSONField(blank=True, default=list, help_text='List of topics/concepts answered correctly'),
        ),
        migrations.AddField(
            model_name='assessmentattempt',
            name='weaknesses',
            field=models.JSONField(blank=True, default=list, help_text='List of topics/concepts answered incorrectly'),
        ),
        migrations.AddField(
            model_name='assessmentattempt',
            name='next_steps',
            field=models.JSONField(blank=True, default=list, help_text='Actionable next steps based on performance'),
        ),
    ]
