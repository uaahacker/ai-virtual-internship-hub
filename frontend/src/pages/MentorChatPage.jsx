import { useState, useRef, useEffect } from 'react';
import { useAuth } from '../contexts/AuthContext';
import { mentorService } from '../services/endpoints';
import DashboardLayout from '../components/DashboardLayout';

function MessageBubble({ message }) {
  const isUser = message.role === 'user';
  return (
    <div className={`flex ${isUser ? 'justify-end' : 'justify-start'} mb-4`}>
      {!isUser && (
        <div className="w-8 h-8 bg-gray-900 rounded-full flex items-center justify-center text-white text-sm font-bold mr-2 flex-shrink-0 mt-1">
          AI
        </div>
      )}
      <div
        className={`max-w-[75%] px-4 py-3 rounded-2xl text-sm leading-relaxed whitespace-pre-wrap ${
          isUser
            ? 'bg-gray-900 text-white rounded-br-sm'
            : 'bg-white border border-gray-200 text-gray-800 rounded-bl-sm shadow-sm'
        }`}
      >
        {message.content}
      </div>
      {isUser && (
        <div className="w-8 h-8 bg-blue-600 rounded-full flex items-center justify-center text-white text-sm font-bold ml-2 flex-shrink-0 mt-1">
          M
        </div>
      )}
    </div>
  );
}

const SUGGESTED_PROMPTS = [
  'How can I effectively evaluate a student\'s task submission?',
  'What are the best practices for giving constructive feedback?',
  'How do I guide a student who is struggling with freelancing?',
  'Suggest a learning roadmap for a Data Analytics student',
  'How do I identify skill gaps in a student\'s portfolio?',
];

export default function MentorChatPage() {
  const { user } = useAuth();
  const [messages, setMessages] = useState([
    {
      role: 'assistant',
      content: `Hello ${user?.name || 'Mentor'}! 👋\n\nI'm your AI assistant with no topic restrictions. You can ask me anything — from evaluating student work, suggesting learning resources, mentoring strategies, career advice, technical questions, or anything else.\n\nHow can I help you today?`,
    },
  ]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const messagesEndRef = useRef(null);
  const textareaRef = useRef(null);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const sendMessage = async (text) => {
    const msg = (text || input).trim();
    if (!msg || loading) return;

    setInput('');
    setError('');
    const userMsg = { role: 'user', content: msg };
    const newMessages = [...messages, userMsg];
    setMessages(newMessages);
    setLoading(true);

    // Build history excluding the welcome message
    const historyForApi = newMessages
      .slice(1) // skip the static welcome message
      .slice(-20)
      .map(m => ({ role: m.role, content: m.content }));

    try {
      const res = await mentorService.chat(msg, historyForApi.slice(0, -1));
      if (res.data.success) {
        setMessages(prev => [...prev, { role: 'assistant', content: res.data.data.reply }]);
      } else {
        setError(res.data.error || 'Failed to get response');
      }
    } catch (err) {
      setError('AI service unavailable. Please try again.');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };

  const clearChat = () => {
    setMessages([{
      role: 'assistant',
      content: `Hello ${user?.name || 'Mentor'}! 👋\n\nI'm your AI assistant with no topic restrictions. How can I help you today?`,
    }]);
    setError('');
  };

  return (
    <DashboardLayout>
      <div className="flex flex-col h-[calc(100vh-80px)] max-w-4xl mx-auto">
        {/* Header */}
        <div className="flex items-center justify-between pb-4 border-b border-gray-200 mb-4">
          <div>
            <h1 className="text-2xl font-bold text-gray-900">AI Assistant</h1>
            <p className="text-sm text-gray-500 mt-0.5">
              Unrestricted AI — ask anything about mentoring, evaluations, learning, or any topic
            </p>
          </div>
          <div className="flex items-center gap-2">
            <span className="flex items-center gap-1.5 px-3 py-1.5 bg-green-50 text-green-700 text-xs font-medium rounded-full border border-green-200">
              <span className="w-1.5 h-1.5 bg-green-500 rounded-full animate-pulse" />
              AI Online
            </span>
            <button
              onClick={clearChat}
              className="px-3 py-1.5 text-xs font-medium text-gray-600 border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors"
            >
              Clear Chat
            </button>
          </div>
        </div>

        {/* Messages */}
        <div className="flex-1 overflow-y-auto px-1 pb-4">
          {messages.map((msg, idx) => (
            <MessageBubble key={idx} message={msg} />
          ))}
          {loading && (
            <div className="flex justify-start mb-4">
              <div className="w-8 h-8 bg-gray-900 rounded-full flex items-center justify-center text-white text-sm font-bold mr-2 flex-shrink-0 mt-1">
                AI
              </div>
              <div className="bg-white border border-gray-200 rounded-2xl rounded-bl-sm px-4 py-3 shadow-sm">
                <div className="flex gap-1.5 items-center">
                  <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0ms' }} />
                  <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '150ms' }} />
                  <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '300ms' }} />
                </div>
              </div>
            </div>
          )}
          {error && (
            <div className="text-center mb-4">
              <span className="inline-block px-4 py-2 bg-red-50 border border-red-200 text-red-700 text-sm rounded-lg">
                ⚠️ {error}
              </span>
            </div>
          )}
          <div ref={messagesEndRef} />
        </div>

        {/* Suggested prompts — shown only at start */}
        {messages.length === 1 && (
          <div className="mb-4">
            <p className="text-xs text-gray-400 mb-2">Suggested questions:</p>
            <div className="flex flex-wrap gap-2">
              {SUGGESTED_PROMPTS.map((prompt, idx) => (
                <button
                  key={idx}
                  onClick={() => sendMessage(prompt)}
                  className="px-3 py-2 bg-white border border-gray-200 text-xs text-gray-700 rounded-lg hover:bg-gray-50 hover:border-gray-300 transition-colors text-left"
                >
                  {prompt}
                </button>
              ))}
            </div>
          </div>
        )}

        {/* Input */}
        <div className="border-t border-gray-200 pt-4">
          <div className="flex gap-3 items-end">
            <textarea
              ref={textareaRef}
              value={input}
              onChange={e => setInput(e.target.value)}
              onKeyDown={handleKeyDown}
              placeholder="Ask me anything… (Shift+Enter for new line)"
              rows={2}
              className="flex-1 px-4 py-3 border border-gray-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-gray-900 resize-none text-sm"
              disabled={loading}
            />
            <button
              onClick={() => sendMessage()}
              disabled={!input.trim() || loading}
              className="px-5 py-3 bg-gray-900 text-white font-medium rounded-xl hover:bg-gray-700 disabled:opacity-40 disabled:cursor-not-allowed transition-colors flex-shrink-0"
            >
              {loading ? (
                <div className="w-5 h-5 border-2 border-white border-t-transparent rounded-full animate-spin" />
              ) : (
                '↑ Send'
              )}
            </button>
          </div>
          <p className="text-xs text-gray-400 mt-2 text-center">
            Powered by OpenRouter AI · No topic restrictions for mentors
          </p>
        </div>
      </div>
    </DashboardLayout>
  );
}
