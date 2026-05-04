"""
API endpoints for chatbot functionality.
"""

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from django.db.models import Q
import logging

from apps.core.permissions import IsStudent, IsMentor
from .models import ChatSession, ChatMessage, ChatFeedback
from .service import ChatbotService
from .serializers import (
    ChatSessionSerializer,
    ChatSessionDetailSerializer,
    ChatMessageCreateSerializer,
    ChatMessageSerializer,
    ChatFeedbackCreateSerializer,
    ChatFeedbackSerializer,
    ChatSessionStatsSerializer,
)

logger = logging.getLogger(__name__)


class ChatSessionListCreateView(APIView):
    """List all chat sessions or create a new one."""
    
    permission_classes = [IsAuthenticated, IsStudent]
    
    def get(self, request):
        """Get all chat sessions for the user."""
        try:
            service = ChatbotService(request.user)
            sessions = service.get_user_sessions()
            serializer = ChatSessionSerializer(sessions, many=True)
            return Response({
                'success': True,
                'data': serializer.data
            })
        except Exception as e:
            logger.error(f"Error fetching sessions: {str(e)}")
            return Response({
                'success': False,
                'error': 'Failed to fetch sessions'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def post(self, request):
        """Create a new chat session."""
        try:
            title = request.data.get('title', 'Career Guidance Chat')
            service = ChatbotService(request.user)
            session = service.create_session(title)
            serializer = ChatSessionSerializer(session)
            return Response({
                'success': True,
                'data': serializer.data,
                'message': 'Chat session created'
            }, status=status.HTTP_201_CREATED)
        except Exception as e:
            logger.error(f"Error creating session: {str(e)}")
            return Response({
                'success': False,
                'error': 'Failed to create session'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class ChatSessionDetailView(APIView):
    """Retrieve, update, or delete a chat session."""
    
    permission_classes = [IsAuthenticated, IsStudent]
    
    def get_session(self, session_id: int, user):
        """Helper to get session and check permission."""
        try:
            return ChatSession.objects.get(id=session_id, user=user)
        except ChatSession.DoesNotExist:
            return None
    
    def get(self, request, session_id):
        """Get a specific chat session with all messages."""
        try:
            session = self.get_session(session_id, request.user)
            if not session:
                return Response({
                    'success': False,
                    'error': 'Session not found'
                }, status=status.HTTP_404_NOT_FOUND)
            
            serializer = ChatSessionDetailSerializer(session)
            return Response({
                'success': True,
                'data': serializer.data
            })
        except Exception as e:
            logger.error(f"Error fetching session: {str(e)}")
            return Response({
                'success': False,
                'error': 'Failed to fetch session'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def put(self, request, session_id):
        """Update session title."""
        try:
            session = self.get_session(session_id, request.user)
            if not session:
                return Response({
                    'success': False,
                    'error': 'Session not found'
                }, status=status.HTTP_404_NOT_FOUND)
            
            title = request.data.get('title')
            if title:
                session.title = title
                session.save()
            
            serializer = ChatSessionSerializer(session)
            return Response({
                'success': True,
                'data': serializer.data,
                'message': 'Session updated'
            })
        except Exception as e:
            logger.error(f"Error updating session: {str(e)}")
            return Response({
                'success': False,
                'error': 'Failed to update session'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def delete(self, request, session_id):
        """Delete a chat session."""
        try:
            session = self.get_session(session_id, request.user)
            if not session:
                return Response({
                    'success': False,
                    'error': 'Session not found'
                }, status=status.HTTP_404_NOT_FOUND)
            
            service = ChatbotService(request.user)
            service.delete_session(session)
            return Response({
                'success': True,
                'message': 'Session deleted'
            })
        except Exception as e:
            logger.error(f"Error deleting session: {str(e)}")
            return Response({
                'success': False,
                'error': 'Failed to delete session'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class ChatMessageView(APIView):
    """Send and receive chat messages."""
    
    permission_classes = [IsAuthenticated, IsStudent]
    
    def post(self, request, session_id):
        """Send a message to the chatbot."""
        try:
            # Verify session ownership
            session = ChatSession.objects.get(id=session_id, user=request.user)
            
            # Validate message
            serializer = ChatMessageCreateSerializer(data=request.data)
            if not serializer.is_valid():
                return Response({
                    'success': False,
                    'error': serializer.errors
                }, status=status.HTTP_400_BAD_REQUEST)
            
            user_message = serializer.validated_data['content']
            
            # Generate response
            service = ChatbotService(request.user)
            assistant_response, msg_obj = service.send_message(session, user_message)
            
            # Get updated message history
            messages = ChatMessage.objects.filter(session=session).order_by('-created_at')[:2]
            message_data = ChatMessageSerializer(reversed(messages), many=True).data
            
            return Response({
                'success': True,
                'data': message_data,
                'message': 'Message sent successfully'
            })
        
        except ChatSession.DoesNotExist:
            return Response({
                'success': False,
                'error': 'Session not found'
            }, status=status.HTTP_404_NOT_FOUND)
        
        except ValueError as e:
            return Response({
                'success': False,
                'error': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)
        
        except Exception as e:
            logger.error(f"Error sending message: {str(e)}")
            return Response({
                'success': False,
                'error': 'Failed to send message. Please try again.'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class ChatFeedbackView(APIView):
    """Submit feedback on chatbot responses."""
    
    permission_classes = [IsAuthenticated, IsStudent]
    
    def post(self, request):
        """Submit feedback for a message."""
        try:
            serializer = ChatFeedbackCreateSerializer(data=request.data)
            if not serializer.is_valid():
                return Response({
                    'success': False,
                    'error': serializer.errors
                }, status=status.HTTP_400_BAD_REQUEST)
            
            message_id = serializer.validated_data['message_id']
            rating = serializer.validated_data['rating']
            comment = serializer.validated_data.get('comment', '')
            
            # Verify message belongs to user's session
            try:
                message = ChatMessage.objects.get(id=message_id)
                if message.session.user != request.user:
                    return Response({
                        'success': False,
                        'error': 'Unauthorized'
                    }, status=status.HTTP_403_FORBIDDEN)
            except ChatMessage.DoesNotExist:
                return Response({
                    'success': False,
                    'error': 'Message not found'
                }, status=status.HTTP_404_NOT_FOUND)
            
            # Create or update feedback
            feedback, created = ChatFeedback.objects.update_or_create(
                message=message,
                defaults={'rating': rating, 'comment': comment}
            )
            
            response_serializer = ChatFeedbackSerializer(feedback)
            return Response({
                'success': True,
                'data': response_serializer.data,
                'message': 'Feedback submitted successfully'
            }, status=status.HTTP_201_CREATED if created else status.HTTP_200_OK)
        
        except Exception as e:
            logger.error(f"Error submitting feedback: {str(e)}")
            return Response({
                'success': False,
                'error': 'Failed to submit feedback'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class ChatSessionStatsView(APIView):
    """Get statistics about a chat session."""
    
    permission_classes = [IsAuthenticated, IsStudent]
    
    def get(self, request, session_id):
        """Get session statistics."""
        try:
            session = ChatSession.objects.get(id=session_id, user=request.user)
            service = ChatbotService(request.user)
            stats = service.get_session_stats(session)
            serializer = ChatSessionStatsSerializer(stats)
            return Response({
                'success': True,
                'data': serializer.data
            })
        except ChatSession.DoesNotExist:
            return Response({
                'success': False,
                'error': 'Session not found'
            }, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            logger.error(f"Error fetching stats: {str(e)}")
            return Response({
                'success': False,
                'error': 'Failed to fetch statistics'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class ChatSessionArchiveView(APIView):
    """Archive a chat session."""
    
    permission_classes = [IsAuthenticated, IsStudent]
    
    def post(self, request, session_id):
        """Archive a session."""
        try:
            session = ChatSession.objects.get(id=session_id, user=request.user)
            service = ChatbotService(request.user)
            service.archive_session(session)
            return Response({
                'success': True,
                'message': 'Session archived'
            })
        except ChatSession.DoesNotExist:
            return Response({
                'success': False,
                'error': 'Session not found'
            }, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            logger.error(f"Error archiving session: {str(e)}")
            return Response({
                'success': False,
                'error': 'Failed to archive session'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class MentorChatView(APIView):
    """
    POST /api/chatbot/mentor/chat/
    Unrestricted AI chat for mentors. Directly proxies to OpenRouter API.
    No topic restrictions — mentor can ask anything.
    Body: { message: str, history: [ {role: 'user'|'assistant', content: str} ] }
    """
    permission_classes = [IsAuthenticated, IsMentor]

    def post(self, request):
        message = request.data.get('message', '').strip()
        if not message:
            return Response(
                {'success': False, 'error': 'message is required.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        history = request.data.get('history', [])
        if not isinstance(history, list):
            history = []

        # Keep last 20 history messages to limit token usage
        history = history[-20:]

        try:
            from .providers import ProviderFactory
            provider = ProviderFactory.create_provider()

            system_prompt = (
                "You are an expert AI assistant for mentors on the Virtual Internship Hub platform. "
                "You help mentors guide students, provide career advice, evaluate student work, "
                "suggest learning resources, and answer any questions they have. "
                "You have no topic restrictions — answer all mentor questions fully and helpfully. "
                "Be professional, insightful, and thorough."
            )

            messages = [{'role': 'system', 'content': system_prompt}]
            for h in history:
                if h.get('role') in ('user', 'assistant') and h.get('content'):
                    messages.append({'role': h['role'], 'content': h['content']})
            messages.append({'role': 'user', 'content': message})

            response_text = provider.generate_response(
                messages,
                temperature=0.7,
                max_tokens=800
            )

            return Response({
                'success': True,
                'data': {
                    'reply': response_text,
                    'role': 'assistant',
                }
            })

        except Exception as e:
            logger.error(f"Mentor chat error: {str(e)}")
            return Response({
                'success': False,
                'error': 'AI service temporarily unavailable. Please try again.'
            }, status=status.HTTP_503_SERVICE_UNAVAILABLE)
