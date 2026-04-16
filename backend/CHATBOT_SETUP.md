# Chatbot Configuration Guide

## Environment Variables

Add these to your `.env` file in the backend directory:

### LLM Provider Setup

```bash
# Choose one of: mock, openrouter, openai
LLM_PROVIDER=mock
```

#### Option 1: Mock Provider (Development/Testing)
No API key required. Returns predefined responses.
```bash
LLM_PROVIDER=mock
```

#### Option 2: OpenRouter Provider
1. Sign up at https://openrouter.ai
2. Get your API key from the dashboard
3. Add to .env:
```bash
LLM_PROVIDER=openrouter
OPENROUTER_API_KEY=sk-or-v1-xxxxxxxxxxxxx
OPENROUTER_MODEL=mistralai/mistral-7b-instruct
```

Available models at OpenRouter:
- `mistralai/mistral-7b-instruct` (Free)
- `meta-llama/llama-2-70b-chat` (Open)
- `nousresearch/nous-hermes-2-mixtral-8x7b-dpo` (Good quality)

#### Option 3: OpenAI Provider
1. Sign up at https://openai.com
2. Get your API key from https://platform.openai.com/api-keys
3. Add to .env:
```bash
LLM_PROVIDER=openai
OPENAI_API_KEY=sk-proj-xxxxxxxxxxxxx
OPENAI_MODEL=gpt-3.5-turbo
```

Available models:
- `gpt-3.5-turbo` (Cheaper, fast)
- `gpt-4` (More capable, expensive)

## Backend Installation

### 1. Apply Migrations
```bash
cd backend
.\venv\Scripts\python manage.py migrate
```

### 2. Create Superuser (Optional)
```bash
.\venv\Scripts\python manage.py createsuperuser
```

### 3. Access Django Admin
```
http://localhost:8000/django-admin
```
You can manage chat sessions and view feedback in the admin panel.

## Frontend Integration

### 1. Install Dependencies (if needed)
```bash
cd frontend
npm install
```

### 2. Add ChatProvider to App.jsx
```jsx
import { ChatProvider } from './contexts/ChatContext';
import ChatPage from './pages/ChatPage';
import FloatingChatButton from './components/FloatingChatButton';

export default function App() {
  return (
    <ChatProvider>
      <Routes>
        {/* Your existing routes */}
        <Route path="/chat" element={<ChatPage />} />
        {/* ... */}
      </Routes>
      
      {/* Add floating button to all pages */}
      <FloatingChatButton />
    </ChatProvider>
  );
}
```

### 3. Add Route (if using routing)
```jsx
<Route path="/chat" element={<ChatPage />} />
```

## Testing the Chatbot

### 1. Start Backend
```bash
cd backend
.\venv\Scripts\python manage.py runserver
```

### 2. Start Frontend
```bash
cd frontend
npm run dev
```

### 3. Test Endpoints
```bash
# Create a session
curl -X POST http://localhost:8000/api/chatbot/sessions/ \
  -H "Authorization: Bearer <your_token>" \
  -H "Content-Type: application/json" \
  -d '{"title": "Test Chat"}'

# Send a message
curl -X POST http://localhost:8000/api/chatbot/sessions/1/messages/ \
  -H "Authorization: Bearer <your_token>" \
  -H "Content-Type: application/json" \
  -d '{"content": "What skills should I learn?"}'
```

## Database Schema

### ChatSession
- `id`: Primary key
- `user`: Foreign key to User
- `title`: Session title
- `created_at`: Creation timestamp
- `updated_at`: Last update timestamp
- `is_archived`: Whether session is archived

### ChatMessage
- `id`: Primary key
- `session`: Foreign key to ChatSession
- `role`: "user", "assistant", or "system"
- `content`: Message text
- `tokens_used`: Token count (optional)
- `created_at`: Creation timestamp

### ChatFeedback
- `id`: Primary key
- `message`: Foreign key to ChatMessage (unique)
- `rating`: 1-5 star rating
- `comment`: User feedback comment
- `created_at`: Creation timestamp

## Performance Tips

1. **Limit Message History**: Keep last 10 messages for context to save tokens
2. **Cache Sessions**: Sessions are cached in the ChatProvider context
3. **Implement Pagination**: For users with many sessions
4. **Virtual Scrolling**: For chats with hundreds of messages

## Security Best Practices

1. **Never commit .env files** - Use .env.example as template
2. **Rotate API keys regularly** - Change keys every 90 days
3. **Use rate limiting** - Add to API views if needed
4. **Validate input** - All inputs are validated on backend
5. **HTTPS only** - Use HTTPS in production
6. **CORS configuration** - Only allow your frontend domain

## Troubleshooting

### Issue: 401 Unauthorized
**Solution**: Make sure user is logged in and token is valid

### Issue: 404 Not Found
**Solution**: Verify the chatbot app is added to INSTALLED_APPS

### Issue: Empty response from chatbot
**Solution**: 
- Check LLM_PROVIDER setting
- Verify API key is correct
- Check API rate limits
- Look at server logs for errors

### Issue: Slow responses
**Solution**:
- Using mock provider for testing?
- Reduce max_tokens in service.py
- Check internet connection
- Verify API provider status

### Issue: Database errors
**Solution**: Run migrations
```bash
.\venv\Scripts\python manage.py migrate
```

## Customization

### Change System Prompt
Edit `apps/chatbot/service.py` - modify `SYSTEM_PROMPT` variable

### Adjust Response Length
In `apps/chatbot/service.py`, modify:
```python
max_tokens=500  # Change to desired length
```

### Customize Chat Widget Styling
Modify `ChatWidget.jsx` and `ChatPage.jsx` - all components use Tailwind CSS

### Add New LLM Provider
1. Create new provider class in `providers.py`
2. Implement `generate_response()` method
3. Register in `ProviderFactory`

## Monitoring & Analytics

View statistics for each chat session:
```bash
curl http://localhost:8000/api/chatbot/sessions/1/stats/ \
  -H "Authorization: Bearer <your_token>"
```

## Next Steps

1. Configure your preferred LLM provider
2. Run migrations
3. Test in development
4. Add to production settings
5. Monitor usage and gather feedback

For issues or questions, refer to the integration guide!
