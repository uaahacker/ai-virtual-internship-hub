# chatbot — AI Career Guidance Chatbot

The `chatbot` app provides an AI-powered conversational assistant for career guidance. Students use it to ask questions about freelancing, career paths, and skill development. Mentors have a dedicated AI assistant variant.

---

## Table of Contents

1. [Models](#models)
2. [URL Reference](#url-reference)
3. [Chat Flow](#chat-flow)
4. [AI Providers](#ai-providers)
5. [Service Layer](#service-layer)
6. [Serializers](#serializers)

---

## Models

### `ChatSession`

A conversation session for a user.

| Field | Type | Notes |
|-------|------|-------|
| `user` | ForeignKey to User | Session owner |
| `title` | CharField | Auto-generated from first message or set by user |
| `is_archived` | BooleanField | Archived sessions hidden from active list |
| `created_at` | DateTimeField | |
| `updated_at` | DateTimeField | Auto-updated on new message |

---

### `ChatMessage`

One message within a `ChatSession`.

| Field | Type | Notes |
|-------|------|-------|
| `session` | ForeignKey to ChatSession | related_name=messages |
| `role` | CharField | user or assistant |
| `content` | TextField | Message text |
| `timestamp` | DateTimeField | Auto-set |
| `token_count` | IntegerField (nullable) | Approximate token usage |

---

## URL Reference

All URLs prefixed with `/api/chatbot/`.

| Method | Path | Permission | Description |
|--------|------|-----------|-------------|
| GET | `/sessions/` | Authenticated | List all sessions for current user |
| POST | `/sessions/create/` | Authenticated | Start a new chat session |
| GET | `/sessions/:id/` | Authenticated | Get session with message history |
| POST | `/sessions/:id/messages/` | Authenticated | Send a message and get AI response |
| DELETE | `/sessions/:id/delete/` | Authenticated | Delete a session |
| POST | `/sessions/:id/archive/` | Authenticated | Archive a session |
| GET | `/sessions/:id/messages/` | Authenticated | List messages in a session |

---

## Chat Flow

```
1. User opens ChatPage in frontend
2. GET /api/chatbot/sessions/ loads existing sessions
3. User starts new session or selects existing
4. User types message → POST /api/chatbot/sessions/:id/messages/
        body: { "content": "How do I get my first client on Upwork?" }
5. ChatService:
        a. Saves user message to ChatMessage
        b. Builds context: system prompt + last N messages from session
        c. Calls configured AI provider
        d. Saves assistant response to ChatMessage
        e. Updates ChatSession.updated_at
6. Response returned to frontend
```

---

## AI Providers

`apps/chatbot/providers.py` — multiple provider backends.

The active provider is selected based on which API key is configured in `.env`.

| Provider | Env Variable | Notes |
|----------|-------------|-------|
| `openai` | `OPENAI_API_KEY` | GPT-3.5/GPT-4 via OpenAI API |
| `gemini` | `GEMINI_API_KEY` | Google Gemini via Google AI API |
| `openrouter` | `OPENROUTER_API_KEY` | Multiple models via OpenRouter |
| `rule_based` | (none needed) | Fallback: keyword-matching responses |

The rule-based fallback answers common freelancing questions without any external API key, making the chatbot functional out of the box.

---

## Service Layer

`apps/chatbot/service.py` — `ChatService`

Encapsulates all business logic:

- `send_message(session, user_content)` — saves user message, calls provider, returns assistant message
- `build_context(session)` — assembles last N messages formatted for the provider
- `get_system_prompt(user)` — returns role-aware system prompt

**System Prompt (Student):**
"You are an AI career assistant for a virtual freelancing internship platform. Help students with freelancing skills, career advice, portfolio building, and task guidance. Be encouraging, practical, and concise."

**System Prompt (Mentor):**
"You are an AI assistant for mentors on a virtual internship platform. Help mentors with evaluation strategies, student guidance techniques, and freelancing domain knowledge."

---

## Serializers

| Serializer | Purpose |
|-----------|---------|
| `ChatSessionSerializer` | Session list (title, timestamps) |
| `ChatSessionDetailSerializer` | Session with full message history |
| `ChatMessageSerializer` | Individual message (role, content, timestamp) |
| `SendMessageSerializer` | Validates incoming user message content |
