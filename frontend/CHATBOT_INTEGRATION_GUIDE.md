# AI Chatbot Module Integration Guide

## Backend Setup (Already Completed)

### Database
The chatbot uses three models:
- **ChatSession**: Stores individual chat sessions per user
- **ChatMessage**: Stores messages within a session  
- **ChatFeedback**: Stores user feedback on responses

### API Endpoints
- `GET/POST /api/chatbot/sessions/` - List and create chat sessions
- `GET/PUT/DELETE /api/chatbot/sessions/{id}/` - Session management
- `POST /api/chatbot/sessions/{id}/messages/` - Send message and get response
- `POST /api/chatbot/feedback/` - Submit feedback on responses
- `GET /api/chatbot/sessions/{id}/stats/` - Get session statistics
- `POST /api/chatbot/sessions/{id}/archive/` - Archive a session

### LLM Provider Configuration
Set environment variables in `.env`:
```
# Choose provider: mock, openrouter, or openai
LLM_PROVIDER=mock

# For OpenRouter
OPENROUTER_API_KEY=your_key_here
OPENROUTER_MODEL=mistralai/mistral-7b-instruct

# For OpenAI
OPENAI_API_KEY=your_key_here
OPENAI_MODEL=gpt-3.5-turbo
```

## Frontend Integration

### 1. Add ChatProvider to App
Wrap your main app with ChatProvider:

```jsx
import { ChatProvider } from './contexts/ChatContext';
import ChatPage from './pages/ChatPage';
import FloatingChatButton from './components/FloatingChatButton';

function App() {
  return (
    <ChatProvider>
      {/* Your other routes */}
      <ChatPage />  {/* For dedicated chat interface */}
      <FloatingChatButton />  {/* For floating widget on other pages */}
    </ChatProvider>
  );
}
```

### 2. Using the Chat Hook in Components

```jsx
import { useChat } from '../contexts/ChatContext';

function MyComponent() {
  const {
    currentSession,
    messages,
    loading,
    error,
    sendMessage,
    createSession,
    loadSession,
    fetchSessions,
  } = useChat();

  const handleChat = async (message) => {
    if (!currentSession) {
      await createSession();
    }
    await sendMessage(message);
  };

  return (
    // Your component JSX
  );
}
```

### 3. Chat Components

#### ChatWidget
Minimizable chat widget (bottom-right corner):
```jsx
<ChatWidget
  isOpen={isOpen}
  onClose={() => setIsOpen(false)}
  isMinimized={isMinimized}
  onMinimize={setIsMinimized}
/>
```

#### ChatPage
Full-page chat interface with history:
```jsx
import ChatPage from './pages/ChatPage';

<ChatPage />
```

#### FloatingChatButton
Global floating button for quick access:
```jsx
<FloatingChatButton />
```

## Chatbot Scope & Capabilities

The chatbot is configured to help with:

### ✅ Supported Topics
1. **Freelancing Career Guidance**
   - Starting a freelancing career
   - Finding clients and pricing services
   - Building a freelance business

2. **Recommended Domains**
   - Web Development
   - Data Science
   - AI/Machine Learning
   - Mobile Development
   - UI/UX Design
   - DevOps
   - And more...

3. **Skill Improvement Tips**
   - Recommended technologies to learn
   - Learning resources
   - Skill progression paths

4. **Task Roadmap Suggestions**
   - Learning plans
   - Project ideas
   - Milestone planning

5. **Portfolio Improvement Advice**
   - Project presentation
   - Portfolio structure
   - Highlighting achievements

### ❌ Out of Scope
- General life advice
- Code implementation
- Specific company recommendations without context
- Non-career related topics

## LLM Providers

### Mock Provider (Development)
Returns predefined responses based on keywords. No API key required.

### OpenRouter
Supports multiple open-source models at competitive pricing.
- Setup: Get API key from openrouter.ai
- Models available: Mistral, Llama, Phi, etc.

### OpenAI
GPT models with high quality responses.
- Setup: Get API key from openai.com
- Models available: GPT-3.5-turbo, GPT-4, etc.

### Adding Custom Providers
1. Create a new provider class extending `LLMProvider`
2. Implement `generate_response()` method
3. Register using `ProviderFactory.register_provider()`

```python
class CustomProvider(LLMProvider):
    def generate_response(self, messages, **kwargs) -> str:
        # Your implementation
        pass

ProviderFactory.register_provider('custom', CustomProvider)
```

## Usage Examples

### Start a New Chat
```jsx
const { createSession } = useChat();

const startChat = async () => {
  await createSession('My Learning Journey');
};
```

### Send a Message
```jsx
const { sendMessage, currentSession } = useChat();

const askQuestion = async () => {
  if (currentSession) {
    await sendMessage('What skills should I learn for freelancing?');
  }
};
```

### View Chat History
```jsx
const { currentSession, messages } = useChat();

useEffect(() => {
  // Messages auto-update when session changes
  console.log('Current messages:', messages);
}, [messages]);
```

### Delete Old Conversations
```jsx
const { deleteSession } = useChat();

const cleanup = async (sessionId) => {
  await deleteSession(sessionId);
};
```

## Performance Optimization

### Message Caching
Messages are stored locally in React state and persisted in the database. Consider implementing:
- Local storage caching
- Session pagination for old messages
- Virtual scrolling for large message lists

### Token Limits
- Default max 500 tokens per response
- Adjustable via `generate_response()` parameters
- History limited to last 10 messages for context

## Error Handling

All errors are caught and user-friendly messages are displayed:
```jsx
const { error } = useChat();

if (error) {
  return <div className="error">{error}</div>;
}
```

## Security Considerations

1. **Authentication**: All API calls require valid JWT token
2. **Authorization**: Users can only access their own sessions
3. **Input Validation**: Message length limited to 5000 characters
4. **Rate Limiting**: Implement on backend if needed
5. **API Keys**: Never commit `.env` files with real keys

## Testing

### Manual Testing
1. Create a new session
2. Send various questions
3. Test feedback submission
4. Test session management
5. Verify message history persistence

### Automated Testing
```python
# Backend: Create tests in tests.py
from django.test import TestCase
from apps.chatbot.service import ChatbotService

class ChatbotServiceTest(TestCase):
    def test_create_session(self):
        # Test implementation
        pass
```

## Troubleshooting

### Issue: No response from chatbot
- Check LLM_PROVIDER setting
- Verify API keys are correct
- Check API rate limits
- Review server logs

### Issue: Messages not saving
- Verify user authentication
- Check database migrations were applied
- Ensure ChatSession exists for user

### Issue: CORS errors
- Verify CORS_ALLOWED_ORIGINS in settings
- Check API endpoint URLs
- Verify token format in requests

## Future Enhancements

1. Voice input/output support
2. Conversation summarization
3. Export chats as PDF
4. Multi-user collaboration
5. Advanced analytics
6. Personality customization
7. Integration with user portfolios
8. Automated skill assessment
