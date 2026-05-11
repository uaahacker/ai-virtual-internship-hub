from django.db import migrations, models


def backfill_has_set_password(apps, schema_editor):
    """
    Users who registered via email/password (google_id is blank) already have a
    real password, so mark them as has_set_password=True.
    Google-only users (google_id is set) keep the default False.
    """
    User = apps.get_model('accounts', 'User')
    User.objects.filter(google_id='').update(has_set_password=True)


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0007_google_oauth_fields'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='has_set_password',
            field=models.BooleanField(default=False),
        ),
        migrations.RunPython(backfill_has_set_password, migrations.RunPython.noop),
    ]
