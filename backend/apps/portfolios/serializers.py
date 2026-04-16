"""
Serializers for Portfolio models
"""

from rest_framework import serializers
from .models import Portfolio, PortfolioItem


class PortfolioItemSerializer(serializers.ModelSerializer):
    """Serializer for PortfolioItem model"""
    
    class Meta:
        model = PortfolioItem
        fields = [
            'id',
            'portfolio',
            'task',
            'task_title',
            'task_domain',
            'task_difficulty',
            'task_type',
            'completion_date',
            'evaluation_date',
            'score',
            'feedback',
            'created_at',
            'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class PortfolioSerializer(serializers.ModelSerializer):
    """Serializer for Portfolio model with nested items"""
    
    items = PortfolioItemSerializer(many=True, read_only=True)
    items_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Portfolio
        fields = [
            'id',
            'user',
            'title',
            'bio',
            'is_public',
            'total_items',
            'average_score',
            'items',
            'items_count',
            'created_at',
            'updated_at'
        ]
        read_only_fields = ['id', 'user', 'total_items', 'average_score', 'created_at', 'updated_at']
    
    def get_items_count(self, obj):
        """Get count of items"""
        return obj.items.count()
