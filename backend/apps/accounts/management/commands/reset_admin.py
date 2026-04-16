"""
Management command: reset_admin
Deletes all existing users and creates a fresh admin account.

Usage:
    python manage.py reset_admin
    python manage.py reset_admin --email admin@hub.com --password Admin@123 --name "Platform Admin"
"""

from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model

User = get_user_model()


class Command(BaseCommand):
    help = 'Resets database by deleting all users and creates a fresh Admin user.'

    def add_arguments(self, parser):
        parser.add_argument('--email', type=str, default='admin@hub.com')
        parser.add_argument('--password', type=str, default='Admin@123')
        parser.add_argument('--name', type=str, default='Platform Admin')

    def handle(self, *args, **options):
        email = options['email']
        password = options['password']
        name = options['name']

        # Delete all existing users
        user_count = User.objects.count()
        if user_count > 0:
            User.objects.all().delete()
            self.stdout.write(self.style.SUCCESS(
                f'✓ Deleted {user_count} existing user(s)'
            ))
        else:
            self.stdout.write(self.style.WARNING('No existing users to delete'))

        # Create fresh admin user
        user = User.objects.create_superuser(
            email=email,
            name=name,
            password=password,
        )
        self.stdout.write(self.style.SUCCESS(
            f'\n✓ Fresh admin user created successfully!\n'
            f'  Email:    {user.email}\n'
            f'  Name:     {user.name}\n'
            f'  Role:     {user.role}\n'
            f'  Status:   {user.status}\n'
            f'  Password: {password}'
        ))
