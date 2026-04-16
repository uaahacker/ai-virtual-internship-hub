# ✅ Chatbot Integration Checklist

Complete this checklist to fully integrate the chatbot into your project.

## Backend Integration

- [ ] Verify chatbot app is in `INSTALLED_APPS` in `config/settings.py`
- [ ] Verify chatbot URLs are included in `config/urls.py`
- [ ] Run migrations: `python manage.py migrate chatbot`
- [ ] Test backend with: `python manage.py check`
- [ ] Create superuser if needed: `python manage.py createsuperuser`
- [ ] Access admin at: `http://localhost:8000/django-admin/`

## Environment Setup

- [ ] Copy `.env.example` to `.env` (if not already done)
- [ ] Set `LLM_PROVIDER=mock` for development
- [ ] (Optional) Add API keys for production providers:
  - [ ] OpenRouter key: `OPENROUTER_API_KEY`
  - [ ] OpenAI key: `OPENAI_API_KEY`

## Frontend Integration

### Step 1: Add Context Provider
- [ ] Update `src/App.jsx`:
  ```jsx
  import { ChatProvider } from './contexts/ChatContext';
  
  export default function App() {
    return (
      <ChatProvider>
        {/* Your existing app content */}
      </ChatProvider>
    );
  }
  ```

### Step 2: Add Routes (if using routing)
- [ ] Add ChatPage route in your routing configuration:
  ```jsx
  <Route path="/chat" element={<ChatPage />} />
  ```

### Step 3: Add Floating Button
- [ ] Add to main layout:
  ```jsx
  import FloatingChatButton from './components/FloatingChatButton';
  
  return (
    <>
      {/* Your content */}
      <FloatingChatButton />
    </>
  );
  ```

### Step 4: Update Navigation (Optional)
- [ ] Add link to ChatPage in your navigation
- [ ] Add chat icon/button to dashboard

## Testing

### Backend Testing
- [ ] Run: `python manage.py check`
- [ ] Run migrations: `python manage.py migrate`
- [ ] Test API endpoints with curl or Postman

### Frontend Testing
- [ ] Start dev server: `npm run dev`
- [ ] Test floating button appears
- [ ] Click button to open chat widget
- [ ] Send test message: "What skills should I learn?"
- [ ] Mock provider should return career guidance response
- [ ] Test feedback submission
- [ ] Test session management
- [ ] Test on mobile viewport

### Integration Testing
- [ ] User can create chat sessions
- [ ] Messages persist across page reloads
- [ ] User can rate responses
- [ ] User can delete sessions
- [ ] Floating button works on all pages
- [ ] No console errors

## Configuration

### Mock Provider (Development)
```env
LLM_PROVIDER=mock
```

### OpenRouter (Optional - Production)
```env
LLM_PROVIDER=openrouter
OPENROUTER_API_KEY=sk-or-v1-xxxxxxxxxxxxx
OPENROUTER_MODEL=mistralai/mistral-7b-instruct
```

### OpenAI (Optional - Production)
```env
LLM_PROVIDER=openai
OPENAI_API_KEY=sk-proj-xxxxxxxxxxxxx
OPENAI_MODEL=gpt-3.5-turbo
```

## File Locations

### Backend Files
```
backend/
├── apps/chatbot/              ← NEW
│   ├── models.py
│   ├── providers.py
│   ├── service.py
│   ├── views.py
│   ├── serializers.py
│   ├── urls.py
│   ├── admin.py
│   ├── apps.py
│   └── migrations/
├── config/
│   ├── settings.py            ← UPDATED (added chatbot to INSTALLED_APPS)
│   └── urls.py                ← UPDATED (added chatbot URLs)
├── CHATBOT_SETUP.md           ← NEW
└── apps/chatbot/README.md     ← NEW
```

### Frontend Files
```
frontend/
├── src/
│   ├── contexts/
│   │   └── ChatContext.jsx    ← NEW
│   ├── components/
│   │   ├── ChatWidget.jsx     ← NEW
│   │   └── FloatingChatButton.jsx ← NEW
│   └── pages/
│       └── ChatPage.jsx       ← NEW
└── CHATBOT_INTEGRATION_GUIDE.md ← NEW
```

## Database Changes

The following tables will be created after migration:
- `chatbot_chatsession` - Chat sessions
- `chatbot_chatmessage` - Chat messages
- `chatbot_chatfeedback` - User feedback

## API Endpoints Available

After integration, these endpoints will be available:
```
POST   /api/chatbot/sessions/
GET    /api/chatbot/sessions/
GET    /api/chatbot/sessions/{id}/
PUT    /api/chatbot/sessions/{id}/
DELETE /api/chatbot/sessions/{id}/
POST   /api/chatbot/sessions/{id}/messages/
POST   /api/chatbot/feedback/
GET    /api/chatbot/sessions/{id}/stats/
POST   /api/chatbot/sessions/{id}/archive/
```

## Verification Checklist

### Backend
- [ ] `python manage.py check` returns no errors
- [ ] `python manage.py showmigrations chatbot` shows migrations
- [ ] Admin interface works: `/django-admin/`

### Frontend
- [ ] No console errors
- [ ] FloatingChatButton appears
- [ ] Chat widget opens/closes smoothly
- [ ] Messages send and receive correctly
- [ ] Mock provider responds appropriately

### Integration
- [ ] Everything works together
- [ ] User authentication flows properly
- [ ] Messages persist
- [ ] No CORS errors

## Troubleshooting

### Backend Issues
- **Migration error?** → Run `python manage.py migrate`
- **Import error?** → Check INSTALLED_APPS in settings.py
- **No responses?** → Check LLM_PROVIDER setting

### Frontend Issues
- **ChatContext error?** → Wrap app with ChatProvider
- **API 401?** → Check JWT token is valid
- **No messages?** → Check browser network tab for API calls

### Database Issues
- **Foreign key error?** → Ensure migrations are applied
- **Table not found?** → Run migrations again
- **Permission denied?** → Check user authentication

## Performance Optimization (Optional)

- [ ] Add Redis caching for sessions
- [ ] Implement message pagination
- [ ] Add virtual scrolling for large chats
- [ ] Optimize database queries

## Production Deployment

- [ ] Set `DEBUG=False` in `.env`
- [ ] Configure real LLM provider (OpenAI/OpenRouter)
- [ ] Set strong `DJANGO_SECRET_KEY`
- [ ] Configure CORS for production domain
- [ ] Set up database backups
- [ ] Monitor API usage and costs
- [ ] Enable HTTPS
- [ ] Set up rate limiting

## Documentation Review

- [ ] Read `CHATBOT_SETUP.md` for setup details
- [ ] Read `CHATBOT_INTEGRATION_GUIDE.md` for frontend
- [ ] Review `README.md` in chatbot app
- [ ] Check implementation summary

## Post-Deployment

- [ ] Monitor error logs
- [ ] Gather user feedback
- [ ] Adjust system prompt if needed
- [ ] Track API usage
- [ ] Plan future enhancements

---

## Quick Command Reference

```bash
# Backend setup
cd backend
.\venv\Scripts\python manage.py migrate
.\venv\Scripts\python manage.py runserver

# Frontend setup
cd frontend
npm run dev

# Create superuser
python manage.py createsuperuser

# Test API
curl -H "Authorization: Bearer $TOKEN" \
     http://localhost:8000/api/chatbot/sessions/
```

---

## Getting Help

1. Check the setup guides in `/backend/CHATBOT_SETUP.md`
2. Review the integration guide in `/frontend/CHATBOT_INTEGRATION_GUIDE.md`
3. Check the README in `/backend/apps/chatbot/README.md`
4. Look at the implementation summary at project root
5. Review inline code comments

---

**Status:** ✅ All components ready for integration

**Next Step:** Start with Backend Integration above →
