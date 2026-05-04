from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0004_studentprofile_cluster'),
    ]

    operations = [
        migrations.AddField(
            model_name='studentprofile',
            name='cluster_summary',
            field=models.JSONField(
                default=dict,
                help_text='Rich cluster summary: display_name, description, dominant_domain, skill_level, scores',
            ),
        ),
    ]
