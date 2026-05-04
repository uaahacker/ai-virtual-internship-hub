from django.urls import path
from .views import (
    ChatSessionListCreateView,
    ChatSessionDetailView,
    ChatMessageView,
    ChatFeedbackView,
    ChatSessionStatsView,
    ChatSessionArchiveView,
    MentorChatView,
)

app_name = 'chatbot'

urlpatterns = [
    # Session management
    path('sessions/', ChatSessionListCreateView.as_view(), name='session-list-create'),
    path('sessions/<int:session_id>/', ChatSessionDetailView.as_view(), name='session-detail'),
    path('sessions/<int:session_id>/archive/', ChatSessionArchiveView.as_view(), name='session-archive'),
    path('sessions/<int:session_id>/stats/', ChatSessionStatsView.as_view(), name='session-stats'),
    
    # Messages
    path('sessions/<int:session_id>/messages/', ChatMessageView.as_view(), name='send-message'),
    
    # Feedback
    path('feedback/', ChatFeedbackView.as_view(), name='submit-feedback'),

    # Mentor unrestricted chat
    path('mentor/chat/', MentorChatView.as_view(), name='mentor-chat'),
]
