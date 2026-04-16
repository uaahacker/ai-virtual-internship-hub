"""
Portfolio API Views for managing student portfolios and items.
"""

from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.db.models import Avg, Count

from .models import Portfolio, PortfolioItem
from .serializers import PortfolioSerializer, PortfolioItemSerializer


class PortfolioViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Portfolio CRUD operations and stats.
    """
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = PortfolioSerializer

    def get_queryset(self):
        """Students only see their own portfolio"""
        user = self.request.user
        if user.role == 'Student':
            return Portfolio.objects.filter(user=user)
        return Portfolio.objects.all()

    @action(detail=False, methods=['get'])
    def me(self, request):
        """Get current user's portfolio"""
        portfolio, created = Portfolio.objects.get_or_create(user=request.user)
        serializer = self.get_serializer(portfolio)
        return Response({
            'success': True,
            'data': serializer.data
        })

    @action(detail=True, methods=['get'])
    def stats(self, request, pk=None):
        """Get portfolio statistics"""
        portfolio = self.get_object()
        items = portfolio.items.all()
        
        stats = {
            'total_items': items.count(),
            'average_score': items.aggregate(Avg('score'))['score__avg'] or 0.0,
            'total_score': items.aggregate(Count('score'))['score__count'] or 0,
            'by_domain': {}
        }
        
        # Group by domain
        for item in items:
            domain = item.task_domain
            if domain not in stats['by_domain']:
                stats['by_domain'][domain] = {
                    'count': 0,
                    'average_score': 0.0
                }
            stats['by_domain'][domain]['count'] += 1
        
        # Calculate domain averages
        for domain in stats['by_domain']:
            domain_items = items.filter(task_domain=domain)
            stats['by_domain'][domain]['average_score'] = (
                domain_items.aggregate(Avg('score'))['score__avg'] or 0.0
            )
        
        return Response({
            'success': True,
            'data': stats
        })


class PortfolioItemViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Portfolio Items - individual portfolio entries.
    """
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = PortfolioItemSerializer

    def get_queryset(self):
        """Students only see items in their portfolio"""
        user = self.request.user
        if user.role == 'Student':
            return PortfolioItem.objects.filter(portfolio__user=user)
        return PortfolioItem.objects.all()

    def destroy(self, request, *args, **kwargs):
        """Remove item from portfolio"""
        instance = self.get_object()
        # Check ownership
        if instance.portfolio.user != request.user:
            return Response(
                {'success': False, 'error': 'Unauthorized'},
                status=status.HTTP_403_FORBIDDEN
            )
        self.perform_destroy(instance)
        return Response({'success': True})
