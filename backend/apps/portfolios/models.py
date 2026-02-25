"""
Stub models for Portfolios module (future).
"""

from django.db import models
from django.conf import settings
from django.utils import timezone


class Portfolio(models.Model):
    """Stub"""
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='portfolios')
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        db_table = 'portfolios'


class PortfolioItem(models.Model):
    """Stub"""
    portfolio = models.ForeignKey(Portfolio, on_delete=models.CASCADE, related_name='items')
    task = models.ForeignKey('tasks.Task', on_delete=models.SET_NULL, null=True, blank=True)
    description = models.TextField(blank=True)

    class Meta:
        db_table = 'portfolio_items'


class ExternalProfile(models.Model):
    """Stub"""
    PLATFORM_CHOICES = [('Upwork', 'Upwork'), ('Fiverr', 'Fiverr'), ('LinkedIn', 'LinkedIn')]
    portfolio = models.ForeignKey(Portfolio, on_delete=models.CASCADE, related_name='external_profiles')
    platform_name = models.CharField(max_length=50, choices=PLATFORM_CHOICES)
    profile_url = models.URLField()

    class Meta:
        db_table = 'external_profiles'
