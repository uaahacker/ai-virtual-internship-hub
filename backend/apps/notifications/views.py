"""
Views for Notifications, Announcements, and Direct Messages.
"""

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth import get_user_model
from django.db.models import Q

from apps.accounts.models import StudentProfile
from .models import Notification, Announcement, DirectMessage

User = get_user_model()


def _create_notification(user, title, message, notification_type='system', link=''):
    """Helper — silently creates a Notification."""
    try:
        Notification.objects.create(
            user=user,
            title=title,
            message=message,
            notification_type=notification_type,
            link=link,
        )
    except Exception:
        pass


# ─── Notifications ─────────────────────────────────────────────────────────

class NotificationListView(APIView):
    """GET /api/notifications/ — list last 50 notifications for current user."""
    permission_classes = [IsAuthenticated]

    def get(self, request):
        notifications = Notification.objects.filter(user=request.user)[:50]
        data = [
            {
                'id': n.id,
                'title': n.title,
                'message': n.message,
                'notification_type': n.notification_type,
                'link': n.link,
                'status': n.status,
                'created_at': n.created_at.isoformat(),
            }
            for n in notifications
        ]
        return Response({'success': True, 'data': data})


class NotificationUnreadCountView(APIView):
    """GET /api/notifications/unread-count/"""
    permission_classes = [IsAuthenticated]

    def get(self, request):
        count = Notification.objects.filter(user=request.user, status='Unread').count()
        return Response({'success': True, 'data': {'count': count}})


class NotificationMarkReadView(APIView):
    """POST /api/notifications/<pk>/read/"""
    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        try:
            n = Notification.objects.get(pk=pk, user=request.user)
            n.status = 'Read'
            n.save(update_fields=['status'])
            return Response({'success': True})
        except Notification.DoesNotExist:
            return Response({'success': False, 'error': 'Not found'}, status=status.HTTP_404_NOT_FOUND)


class NotificationMarkAllReadView(APIView):
    """POST /api/notifications/read-all/"""
    permission_classes = [IsAuthenticated]

    def post(self, request):
        Notification.objects.filter(user=request.user, status='Unread').update(status='Read')
        return Response({'success': True})


# ─── Announcements ─────────────────────────────────────────────────────────

class AnnouncementListCreateView(APIView):
    """
    GET  /api/notifications/announcements/  — list announcements visible to current user
    POST /api/notifications/announcements/  — create (Admin or Mentor only)
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        role = request.user.role
        qs = Announcement.objects.select_related('created_by').all()

        if role == 'Student':
            qs = qs.filter(Q(audience='All') | Q(audience='Students'))
        elif role == 'Mentor':
            # Mentors see All/Mentor announcements + their own
            qs = qs.filter(
                Q(audience='All') | Q(audience='Mentors') | Q(created_by=request.user)
            )
        # Admin sees everything

        data = [
            {
                'id': a.id,
                'title': a.title,
                'content': a.content,
                'audience': a.audience,
                'created_by_name': a.created_by.name if a.created_by else 'System',
                'created_by_role': a.created_by.role if a.created_by else '',
                'created_at': a.created_at.isoformat(),
                'is_own': a.created_by_id == request.user.id,
            }
            for a in qs[:100]
        ]
        return Response({'success': True, 'data': data})

    def post(self, request):
        role = request.user.role
        if role not in ('Admin', 'Mentor'):
            return Response(
                {'success': False, 'error': 'Not authorised.'},
                status=status.HTTP_403_FORBIDDEN,
            )

        title = (request.data.get('title') or '').strip()
        content = (request.data.get('content') or '').strip()
        audience = request.data.get('audience', 'All')

        if not title or not content:
            return Response(
                {'success': False, 'error': 'Title and content are required.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Mentors post to their students only
        if role == 'Mentor':
            audience = 'Students'

        announcement = Announcement.objects.create(
            title=title,
            content=content,
            created_by=request.user,
            audience=audience,
        )

        # Auto-notify target users
        try:
            if role == 'Admin':
                target_users = list(
                    User.objects.filter(status='Active').exclude(id=request.user.id)
                )
            else:
                # Mentor: only assigned students
                student_ids = StudentProfile.objects.filter(
                    mentor_assigned=request.user
                ).values_list('user_id', flat=True)
                target_users = list(User.objects.filter(id__in=student_ids))

            Notification.objects.bulk_create([
                Notification(
                    user=u,
                    title=title,
                    message=f"{request.user.name}: {content[:120]}",
                    notification_type='announcement',
                    link='/student/announcements' if u.role == 'Student' else '/mentor/announcements',
                )
                for u in target_users
            ])
        except Exception:
            pass

        return Response(
            {'success': True, 'message': 'Announcement posted.', 'data': {'id': announcement.id}},
            status=status.HTTP_201_CREATED,
        )


class AnnouncementDeleteView(APIView):
    """DELETE /api/notifications/announcements/<pk>/"""
    permission_classes = [IsAuthenticated]

    def delete(self, request, pk):
        try:
            ann = Announcement.objects.get(pk=pk)
        except Announcement.DoesNotExist:
            return Response({'success': False, 'error': 'Not found.'}, status=status.HTTP_404_NOT_FOUND)

        if request.user.role != 'Admin' and ann.created_by_id != request.user.id:
            return Response({'success': False, 'error': 'Not authorised.'}, status=status.HTTP_403_FORBIDDEN)

        ann.delete()
        return Response({'success': True})


# ─── Direct Messages ────────────────────────────────────────────────────────

class DirectMessageConversationView(APIView):
    """
    GET /api/notifications/messages/?with=<user_id>  — fetch conversation thread
    Also marks received messages as read.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        other_id = request.query_params.get('with')
        if not other_id:
            return Response(
                {'success': False, 'error': '?with=<user_id> is required.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            other_user = User.objects.get(id=other_id)
        except User.DoesNotExist:
            return Response({'success': False, 'error': 'User not found.'}, status=status.HTTP_404_NOT_FOUND)

        messages = DirectMessage.objects.filter(
            Q(sender=request.user, receiver=other_user) |
            Q(sender=other_user, receiver=request.user)
        ).select_related('sender').order_by('created_at')

        # Mark incoming as read
        DirectMessage.objects.filter(
            sender=other_user, receiver=request.user, is_read=False
        ).update(is_read=True)

        data = [
            {
                'id': m.id,
                'sender_id': m.sender_id,
                'sender_name': m.sender.name,
                'content': m.content,
                'is_read': m.is_read,
                'created_at': m.created_at.isoformat(),
                'is_mine': m.sender_id == request.user.id,
            }
            for m in messages
        ]
        return Response({
            'success': True,
            'data': data,
            'other_user': {'id': other_user.id, 'name': other_user.name, 'role': other_user.role},
        })


class DirectMessageSendView(APIView):
    """POST /api/notifications/messages/send/"""
    permission_classes = [IsAuthenticated]

    def post(self, request):
        receiver_id = request.data.get('receiver_id')
        content = (request.data.get('content') or '').strip()

        if not receiver_id or not content:
            return Response(
                {'success': False, 'error': 'receiver_id and content are required.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            receiver = User.objects.get(id=receiver_id)
        except User.DoesNotExist:
            return Response({'success': False, 'error': 'Receiver not found.'}, status=status.HTTP_404_NOT_FOUND)

        msg = DirectMessage.objects.create(
            sender=request.user,
            receiver=receiver,
            content=content,
        )

        # Notify receiver
        link = '/student/mentor-chat' if receiver.role == 'Student' else f'/mentor/students/{request.user.id}/chat'
        _create_notification(
            user=receiver,
            title=f'Message from {request.user.name}',
            message=content[:120],
            notification_type='message',
            link=link,
        )

        return Response({
            'success': True,
            'data': {
                'id': msg.id,
                'sender_id': msg.sender_id,
                'sender_name': msg.sender.name,
                'content': msg.content,
                'is_read': msg.is_read,
                'created_at': msg.created_at.isoformat(),
                'is_mine': True,
            },
        }, status=status.HTTP_201_CREATED)


class DirectMessageUnreadCountView(APIView):
    """GET /api/notifications/messages/unread-count/"""
    permission_classes = [IsAuthenticated]

    def get(self, request):
        count = DirectMessage.objects.filter(receiver=request.user, is_read=False).count()
        return Response({'success': True, 'data': {'count': count}})
