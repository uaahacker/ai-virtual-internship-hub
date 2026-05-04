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
SYSTEM_PROMPT = """You are an AI career guidance chatbot for an internship hub platform.
You specialise in helping students grow in the following 10 freelancing and professional domains:
  Graphic Design, Content Writing, Programming, Freelancing, E-Commerce,
  QuickBooks, AutoCAD, Data Analytics, Digital Marketing, WordPress.

Your scope is LIMITED to:
1. Career guidance within the 10 domains above
2. Skill improvement tips specific to those domains
3. Task and project roadmap suggestions
4. Portfolio improvement advice for those domains
5. Freelancing strategies — finding clients, pricing, platforms

IMPORTANT CONSTRAINTS:
- Responses should be focused and actionable (under 250 words typically)
- Always tailor advice to the student's specific domains and skill level when their profile is provided
- When asked about topics outside your scope, politely redirect to your areas of expertise
- Be encouraging and supportive
- Suggest concrete next steps and resources

DO NOT:
- Provide general life advice unrelated to career
- Write code or provide technical implementation details
- Make guarantees about job outcomes
- Engage in topics unrelated to career guidance in the 10 domains listed"""


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

        # Personalise the system prompt with the student's domain profile
        personalized_prompt = SYSTEM_PROMPT
        try:
            profile = self.user.student_profile
            preferred = profile.preferred_domains or []
            strongest = profile.strongest_domain or None
            weakest   = profile.weakest_domain or None
            skill_scores = profile.skill_scores_by_domain or {}
            completed = getattr(profile, 'completed_tasks_count', 0)
            progress  = getattr(profile, 'progress_score', 0)

            lines = ["\n\nStudent Profile Context (use this to personalise every response):"]
            lines.append(f"- Preferred/Attempted Domains: {', '.join(preferred) if preferred else 'Not selected yet'}")
            if strongest:
                score = skill_scores.get(strongest, '')
                lines.append(f"- Strongest Domain: {strongest}" + (f" (score: {round(score)}%)" if score else ''))
            if weakest and weakest != strongest:
                score = skill_scores.get(weakest, '')
                lines.append(f"- Needs Improvement: {weakest}" + (f" (score: {round(score)}%)" if score else ''))
            if skill_scores:
                score_list = ', '.join(f"{d}: {round(s)}%" for d, s in sorted(skill_scores.items(), key=lambda x: -x[1]))
                lines.append(f"- Domain Scores: {score_list}")
            lines.append(f"- Tasks Completed: {completed}")
            lines.append(f"- Progress Score: {progress}")
            lines.append("Tailor ALL advice to these domains and skill levels. Reference specific domain names in your responses.")
            personalized_prompt += '\n'.join(lines)
        except Exception:
            pass  # No student profile — use generic prompt (mentor or admin user)

        # Build message context
        context = [{'role': 'system', 'content': personalized_prompt}]

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
                max_tokens=700
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
