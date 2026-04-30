"""
Chatbot service layer for managing conversations and AI interactions.
"""

import logging
from typing import List, Dict, Optional, Tuple
from django.conf import settings
from django.utils import timezone

from .models import ChatSession, ChatMessage
from .providers import ProviderFactory

logger = logging.getLogger(__name__)

# System prompt that defines the chatbot's behavior and scope
SYSTEM_PROMPT = """You are an AI career guidance chatbot specializing in helping students with their professional development. 

Your scope is LIMITED to the following areas:
1. Freelancing career guidance - tips on starting freelancing, finding clients, pricing services
2. Recommended domains - suggesting career paths based on interests (Web Dev, Data Science, AI/ML, etc.)
3. Skill improvement tips - recommending which skills to develop and learning resources
4. Task roadmap suggestions - creating learning plans and project roadmaps
5. Portfolio improvement advice - helping improve portfolio projects and presentations

IMPORTANT CONSTRAINTS:
- Keep responses focused and concise (under 200 words typically)
- Provide actionable, specific advice
- When asked about topics outside your scope, politely redirect to your areas of expertise
- Be encouraging and supportive
- Ask clarifying questions to better understand the student's goals
- Suggest concrete next steps and resources

DO NOT:
- Provide general life advice unrelated to career
- Write code or provide technical implementation details
- Make guarantees about job outcomes
- Recommend specific companies without context
- Engage in topics unrelated to career guidance"""


class ChatbotService:
    """Service for managing chatbot conversations."""
    
    def __init__(self, user):
        """Initialize chatbot service with user."""
        self.user = user
        self.provider = ProviderFactory.create_provider()
        self.max_history_messages = 10  # Limit context to last 10 messages
    
    def create_session(self, title: str = "Career Guidance Chat") -> ChatSession:
        """Create a new chat session."""
        session = ChatSession.objects.create(
            user=self.user,
            title=title
        )
        logger.info(f"Created chat session {session.id} for user {self.user.id}")
        return session
    
    def get_or_create_session(self, session_id: Optional[int] = None) -> ChatSession:
        """Get existing session or create new one."""
        if session_id:
            try:
                session = ChatSession.objects.get(id=session_id, user=self.user)
                return session
            except ChatSession.DoesNotExist:
                logger.warning(f"Session {session_id} not found for user {self.user.id}")
        return self.create_session()
    
    def _get_conversation_context(self, session: ChatSession) -> List[Dict[str, str]]:
        """Get recent conversation history for context."""
        messages = ChatMessage.objects.filter(session=session).order_by('created_at')
        
        # Build message context
        context = [{'role': 'system', 'content': SYSTEM_PROMPT}]
        
        # Include recent messages (last N messages for token efficiency)
        recent_messages = messages[max(0, messages.count() - self.max_history_messages):]
        for msg in recent_messages:
            context.append({'role': msg.role, 'content': msg.content})
        
        return context
    
    def send_message(self, session: ChatSession, user_message: str) -> Tuple[str, ChatMessage]:
        """
        Send a message and get a response.
        
        Args:
            session: ChatSession instance
            user_message: User's message text
            
        Returns:
            Tuple of (response_text, saved_message_object)
        """
        # Validate message
        user_message = user_message.strip()
        if not user_message or len(user_message) > 5000:
            raise ValueError("Message must be between 1 and 5000 characters")
        
        # Save user message
        user_msg_obj = ChatMessage.objects.create(
            session=session,
            role='user',
            content=user_message
        )
        
        try:
            # Get conversation context
            context = self._get_conversation_context(session)
            
            # Generate response
            assistant_response = self.provider.generate_response(
                context,
                temperature=0.7,
                max_tokens=500
            )
            
            # Save assistant response
            assistant_msg_obj = ChatMessage.objects.create(
                session=session,
                role='assistant',
                content=assistant_response
            )
            
            # Update session timestamp
            session.updated_at = timezone.now()
            session.save()
            
            logger.info(f"Generated response for session {session.id}")
            return assistant_response, assistant_msg_obj
            
        except Exception as e:
            logger.error(f"Error generating response: {str(e)}")
            # Save error message
            error_msg = "I encountered an error processing your request. Please try again."
            assistant_msg_obj = ChatMessage.objects.create(
                session=session,
                role='assistant',
                content=error_msg
            )
            raise
    
    def get_session_history(self, session: ChatSession) -> List[Dict]:
        """Get all messages from a session."""
        messages = ChatMessage.objects.filter(session=session).order_by('created_at')
        return [
            {
                'id': msg.id,
                'role': msg.role,
                'content': msg.content,
                'created_at': msg.created_at.isoformat(),
            }
            for msg in messages
        ]
    
    def get_user_sessions(self) -> List[ChatSession]:
        """Get all sessions for the user."""
        return ChatSession.objects.filter(user=self.user, is_archived=False).order_by('-updated_at')
    
    def archive_session(self, session: ChatSession) -> None:
        """Archive a chat session."""
        session.is_archived = True
        session.save()
        logger.info(f"Archived session {session.id}")
    
    def delete_session(self, session: ChatSession) -> None:
        """Delete a chat session."""
        session_id = session.id
        session.delete()
        logger.info(f"Deleted session {session_id}")
    
    def get_session_stats(self, session: ChatSession) -> Dict:
        """Get statistics about a session."""
        messages = ChatMessage.objects.filter(session=session)
        user_messages = messages.filter(role='user').count()
        assistant_messages = messages.filter(role='assistant').count()
        
        return {
            'session_id': session.id,
            'title': session.title,
            'user_messages': user_messages,
            'assistant_messages': assistant_messages,
            'total_messages': user_messages + assistant_messages,
            'created_at': session.created_at.isoformat(),
            'updated_at': session.updated_at.isoformat(),
            'duration_minutes': round((session.updated_at - session.created_at).total_seconds() / 60),
        }
