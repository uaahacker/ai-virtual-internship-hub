from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0003_user_profile_picture'),
    ]

    operations = [
        migrations.AddField(
            model_name='studentprofile',
            name='cluster_id',
            field=models.IntegerField(default=0, help_text='KMeans cluster assignment (0-3)'),
        ),
        migrations.AddField(
            model_name='studentprofile',
            name='cluster_label',
            field=models.CharField(
                default='Explorer',
                help_text='Human-readable cluster label (Explorer/Developing/Competent/Expert)',
                max_length=20,
            ),
        ),
    ]
