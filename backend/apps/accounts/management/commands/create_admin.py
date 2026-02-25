"""
Management command: create_admin
Creates an admin user for the platform.

Usage:
    python manage.py create_admin
    python manage.py create_admin --email admin@hub.com --password Admin@123 --name "Platform Admin"
"""

from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model

User = get_user_model()


class Command(BaseCommand):
    help = 'Creates an Admin user for the AI-Supported Virtual Internship Hub.'

    def add_arguments(self, parser):
        parser.add_argument('--email', type=str, default='admin@hub.com')
        parser.add_argument('--password', type=str, default='Admin@123')
        parser.add_argument('--name', type=str, default='Platform Admin')

    def handle(self, *args, **options):
        email = options['email']
        password = options['password']
        name = options['name']

        if User.objects.filter(email__iexact=email).exists():
            self.stdout.write(self.style.WARNING(f'Admin user "{email}" already exists. Skipping.'))
            return

        user = User.objects.create_superuser(
            email=email,
            name=name,
            password=password,
        )
        self.stdout.write(self.style.SUCCESS(
            f'Admin user created successfully!\n'
            f'  Email:    {user.email}\n'
            f'  Name:     {user.name}\n'
            f'  Role:     {user.role}\n'
            f'  Password: {password}'
        ))
