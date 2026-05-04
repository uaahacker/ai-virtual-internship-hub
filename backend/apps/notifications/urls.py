from django.urls import path
from .views import (
    NotificationListView,
    NotificationUnreadCountView,
    NotificationMarkReadView,
    NotificationMarkAllReadView,
    AnnouncementListCreateView,
    AnnouncementDeleteView,
    DirectMessageConversationView,
    DirectMessageSendView,
    DirectMessageUnreadCountView,
)

urlpatterns = [
    # Notifications
    path('', NotificationListView.as_view(), name='notification-list'),
    path('unread-count/', NotificationUnreadCountView.as_view(), name='notification-unread-count'),
    path('<int:pk>/read/', NotificationMarkReadView.as_view(), name='notification-mark-read'),
    path('read-all/', NotificationMarkAllReadView.as_view(), name='notification-mark-all-read'),

    # Announcements
    path('announcements/', AnnouncementListCreateView.as_view(), name='announcement-list-create'),
    path('announcements/<int:pk>/', AnnouncementDeleteView.as_view(), name='announcement-delete'),

    # Direct messages
    path('messages/', DirectMessageConversationView.as_view(), name='dm-conversation'),
    path('messages/send/', DirectMessageSendView.as_view(), name='dm-send'),
    path('messages/unread-count/', DirectMessageUnreadCountView.as_view(), name='dm-unread-count'),
]
