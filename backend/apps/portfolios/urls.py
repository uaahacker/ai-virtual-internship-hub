"""
URL configuration for Portfolios app
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import PortfolioViewSet, PortfolioItemViewSet

router = DefaultRouter()
router.register(r'portfolios', PortfolioViewSet, basename='portfolio')
router.register(r'portfolio-items', PortfolioItemViewSet, basename='portfolio-item')

urlpatterns = [
    path('', include(router.urls)),
]
