"""
Shared permission classes for role-based access control.
"""

from rest_framework.permissions import BasePermission


class IsStudent(BasePermission):
    """Allow access only to users with role='Student'."""

    def has_permission(self, request, view):
        return (
            request.user
            and request.user.is_authenticated
            and request.user.role == 'Student'
        )


class IsMentor(BasePermission):
    """Allow access only to users with role='Mentor'."""

    def has_permission(self, request, view):
        return (
            request.user
            and request.user.is_authenticated
            and request.user.role == 'Mentor'
        )


class IsAdmin(BasePermission):
    """Allow access only to users with role='Admin'."""

    def has_permission(self, request, view):
        return (
            request.user
            and request.user.is_authenticated
            and request.user.role == 'Admin'
        )
