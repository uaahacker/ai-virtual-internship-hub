from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('notifications', '0002_announcement_directmessage_notification_fields'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='notification',
            options={'db_table': 'notifications', 'ordering': ['-created_at']},
        ),
    ]
