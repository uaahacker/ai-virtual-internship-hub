from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tasks', '0002_taskcompletion_alter_task_learning_outcomes_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='taskassignment',
            name='recommendation_explanation',
            field=models.JSONField(
                default=dict,
                help_text='Structured per-component explanation of the recommendation score',
            ),
        ),
    ]
