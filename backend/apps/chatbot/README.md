# 🤖 AI-Powered Career Guidance Chatbot

A modular, production-ready chatbot system for career guidance integrated with Django + React.

## 📋 Features

✅ **Multi-session chat history** - Each user has separate conversation threads  
✅ **Provider abstraction** - Switch between LLM providers (OpenRouter, OpenAI, Mock)  
✅ **Per-user persistence** - All conversations saved and retrievable  
✅ **Feedback system** - Users can rate responses to improve quality  
✅ **Comprehensive scoping** - Limited to career guidance topics  
✅ **Responsive UI** - Works on desktop and mobile  
✅ **Zero hardcoded secrets** - Environment-based configuration  
✅ **Modular architecture** - Easy to extend and customize  

## 🏗 Architecture

### Backend Structure
```
apps/chatbot/
├── models.py              # Database models
├── providers.py           # LLM provider abstraction
├── service.py            # Business logic & conversation management
├── serializers.py        # API serializers
├── views.py              # API endpoints
├── urls.py               # Route configuration
├── admin.py              # Django admin setup
├── apps.py               # App configuration
├── migrations/           # Database migrations
└── management/           # (Future) Management commands
```

### Frontend Structure
```
frontend/src/
├── contexts/
│   └── ChatContext.jsx   # Chat state management
├── components/
│   ├── ChatWidget.jsx    # Minimizable chat interface
│   └── FloatingChatButton.jsx # Floating access button
├── pages/
│   └── ChatPage.jsx      # Full-page chat interface
└── services/
    └── api.js            # API integration (existing)
```

## 🔄 Data Flow

```
User Input
    ↓
[React Component]
    ↓
ChatContext (State Management)
    ↓
API Call with JWT Token
    ↓
[Django View] - Permission Check
    ↓
ChatbotService - Business Logic
    ↓
LLMProvider - Generate Response
    ↓
Database - Store Messages
    ↓
Response to Frontend
    ↓
[React Component] - Display Message
```

## 🔌 API Endpoints

### Session Management
```
POST   /api/chatbot/sessions/
       - Create new chat session
       - Body: { title: "Optional title" }

GET    /api/chatbot/sessions/
       - List all user's sessions
       - Response: [{ id, title, updated_at, message_count }]

GET    /api/chatbot/sessions/{id}/
       - Get session with all messages
       - Response: { id, title, messages: [] }

PUT    /api/chatbot/sessions/{id}/
       - Update session title
       - Body: { title: "New title" }

DELETE /api/chatbot/sessions/{id}/
       - Delete session permanently
```

### Messages
```
POST   /api/chatbot/sessions/{id}/messages/
       - Send message and get response
       - Body: { content: "User message" }
       - Response: { data: [userMsg, assistantMsg] }
```

### Feedback
```
POST   /api/chatbot/feedback/
       - Submit feedback on a response
       - Body: { message_id: 1, rating: 5, comment: "..." }
```

### Statistics
```
GET    /api/chatbot/sessions/{id}/stats/
       - Get session statistics
       - Response: { user_messages, assistant_messages, duration_minutes }
```

## 🚀 Quick Start

### Backend Setup
```bash
cd backend

# Install dependencies (if needed)
pip install requests

# Apply migrations
.\venv\Scripts\python manage.py migrate

# Run development server
.\venv\Scripts\python manage.py runserver
```

### Frontend Setup
```bash
cd frontend

# Add ChatProvider wrapper in App.jsx
# Add routes for ChatPage
# Add FloatingChatButton to layout

# Start dev server
npm run dev
```

## 🤝 Integration Example

### Basic Usage
```jsx
import { useChat } from './contexts/ChatContext';

function MyComponent() {
  const { 
    currentSession, 
    messages, 
    loading, 
    sendMessage, 
    createSession 
  } = useChat();

  const handleChat = async () => {
    if (!currentSession) {
      await createSession('My Learning Path');
    }
    await sendMessage('What skills should I develop?');
  };

  return (
    <button onClick={handleChat} disabled={loading}>
      Ask Career Questions
    </button>
  );
}
```

### Wrapping Your App
```jsx
import { ChatProvider } from './contexts/ChatContext';
import ChatPage from './pages/ChatPage';
import FloatingChatButton from './components/FloatingChatButton';

export default function App() {
  return (
    <ChatProvider>
      <YourAppComponents />
      <ChatPage />
      <FloatingChatButton />
    </ChatProvider>
  );
}
```

## 📊 Chatbot Scope

### ✅ What It Can Help With
- **Freelancing**: How to start, find clients, pricing strategies
- **Domains**: Tech specializations (Web Dev, Data Science, AI/ML, etc.)
- **Skills**: What to learn, learning resources, progression paths
- **Roadmap**: Learning plans, project ideas, career planning
- **Portfolio**: Showcasing work, portfolio structure, project presentation

### ❌ Out of Scope
- General life advice unrelated to career
- Code implementation or debugging
- Specific company recommendations
- Non-career related topics

## 🔐 Security Features

1. **JWT Authentication** - All endpoints require valid token
2. **User Isolation** - Users only access their own sessions
3. **Input Validation** - Message length limits (5000 chars max)
4. **API Key Management** - Environment-based, never hardcoded
5. **CORS Protection** - Frontend domain validation
6. **Rate Limiting** - Can be added per endpoint

## 🌍 LLM Provider Options

### 1. Mock Provider (Development)
Perfect for testing and development.
```bash
LLM_PROVIDER=mock
```

### 2. OpenRouter
Cost-effective, multiple models available.
```bash
LLM_PROVIDER=openrouter
OPENROUTER_API_KEY=your_key
OPENROUTER_MODEL=mistralai/mistral-7b-instruct
```

### 3. OpenAI
High-quality GPT models.
```bash
LLM_PROVIDER=openai
OPENAI_API_KEY=your_key
OPENAI_MODEL=gpt-3.5-turbo
```

## 📈 Database Schema

```sql
-- Chat Sessions
ChatSession (id, user_id, title, created_at, updated_at, is_archived)

-- Messages within sessions
ChatMessage (id, session_id, role, content, tokens_used, created_at)

-- User feedback
ChatFeedback (id, message_id, rating, comment, created_at)
```

## 🎨 UI Components

### ChatWidget
Minimizable floating widget with:
- Message history display
- Real-time typing indicator
- Responsive design
- Dark/light mode ready

### ChatPage
Full-page interface with:
- Session sidebar
- Message history
- Feedback rating system
- Session management

### FloatingChatButton
Persistent floating button:
- Quick access from any page
- Badge for unread messages
- Smooth animations

## 🧪 Testing

### Manual Testing Checklist
- [ ] Create new session
- [ ] Send various message types
- [ ] Submit feedback
- [ ] Delete sessions
- [ ] Load previous sessions
- [ ] Test on mobile view

### API Testing with cURL
```bash
# Get sessions
curl -H "Authorization: Bearer $TOKEN" \
     http://localhost:8000/api/chatbot/sessions/

# Create session
curl -X POST \
     -H "Authorization: Bearer $TOKEN" \
     -H "Content-Type: application/json" \
     -d '{"title":"Test"}' \
     http://localhost:8000/api/chatbot/sessions/
```

## 📝 Customization

### Change System Prompt
Edit `apps/chatbot/service.py`:
```python
SYSTEM_PROMPT = """Your custom system prompt here..."""
```

### Add Custom Provider
```python
# in providers.py
class CustomProvider(LLMProvider):
    def generate_response(self, messages, **kwargs) -> str:
        # Your implementation
        pass

# Register it
ProviderFactory.register_provider('custom', CustomProvider)
```

### Customize UI
All components use Tailwind CSS. Modify classes in:
- `ChatWidget.jsx`
- `ChatPage.jsx`
- `FloatingChatButton.jsx`

## 🐛 Debugging

### Enable Logging
```python
# settings.py
LOGGING = {
    'version': 1,
    'handlers': {
        'console': {'class': 'logging.StreamHandler'},
    },
    'loggers': {
        'apps.chatbot': {'handlers': ['console'], 'level': 'DEBUG'},
    },
}
```

### Check Database
```bash
.\venv\Scripts\python manage.py shell
>>> from apps.chatbot.models import ChatSession
>>> ChatSession.objects.all()
```

## 📚 Documentation

- [Setup Guide](CHATBOT_SETUP.md) - Installation and configuration
- [Integration Guide](../frontend/CHATBOT_INTEGRATION_GUIDE.md) - React integration
- [API Documentation](API_DOCS.md) - Detailed endpoint reference
- [Architecture Guide](ARCHITECTURE.md) - System design and patterns

## 🔗 Related Files

- Backend: `apps/chatbot/`
- Frontend: `src/contexts/ChatContext.jsx`, `src/pages/ChatPage.jsx`, `src/components/ChatWidget.jsx`
- Config: `config/urls.py`, `config/settings.py`

## 📞 Support

For issues or questions:
1. Check the [Setup Guide](CHATBOT_SETUP.md)
2. Review the integration examples
3. Check Django logs for errors
4. Verify LLM provider configuration

## 🚀 Future Enhancements

- [ ] Voice input/output
- [ ] Conversation export (PDF/Markdown)
- [ ] Multi-language support
- [ ] Conversation summarization
- [ ] Advanced analytics dashboard
- [ ] Integration with user portfolios
- [ ] Automated skill assessments
- [ ] Collaborative conversations

## 📄 License

Same as parent project.

---

Built with ❤️ for career guidance and learning.
