import React, { useState, useEffect, useRef } from 'react';
import { useChat } from '../contexts/ChatContext';
import DashboardLayout from '../components/DashboardLayout';
import ChatMessage from '../components/ChatMessage';
import { Card, CardHeader, CardBody } from '../components/CardComponents';
import { EmptyState, Alert } from '../components/ProgressAndUtilityComponents';
import ConfirmModal from '../components/ConfirmModal';

const ChatPage = () => {
  const {
    sessions,
    currentSession,
    messages,
    loading,
    error,
    fetchSessions,
    createSession,
    loadSession,
    sendMessage,
    deleteSession,
    submitFeedback,
  } = useChat();
  
  const [inputValue, setInputValue] = useState('');
  const [selectedFeedback, setSelectedFeedback] = useState(null);
  const [feedbackRating, setFeedbackRating] = useState(0);
  const [feedbackComment, setFeedbackComment] = useState('');
  const [confirmModal, setConfirmModal] = useState(null);
  const [initialising, setInitialising] = useState(true);
  const initDone = useRef(false);
  const messagesEndRef = useRef(null);

  // Single initialisation: fetch sessions, then load the most recent one.
  // Never auto-create — let the user click "+ New Chat".
  useEffect(() => {
    if (initDone.current) return;  // StrictMode guard — run once only
    initDone.current = true;

    const init = async () => {
      setInitialising(true);
      await fetchSessions();
      setInitialising(false);
    };
    init();
  }, [fetchSessions]);

  // Auto-load most recent existing session once sessions are fetched
  useEffect(() => {
    if (initialising) return;
    if (currentSession) return;      // already have one
    if (sessions.length === 0) return; // nothing to load, show welcome screen
    loadSession(sessions[0].id);
  }, [initialising]); // only re-run when initialising flips to false

  // Scroll to bottom when messages change
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const handleSend = async () => {
    if (!inputValue.trim() || !currentSession) return;
    
    const message = inputValue;
    setInputValue('');
    await sendMessage(message);
  };

  const handleNewChat = async () => {
    await createSession();
  };

  const handleDeleteSession = async (sessionId, e) => {
    e.stopPropagation();
    setConfirmModal({
      title: 'Delete conversation?',
      message: 'This chat and all its messages will be permanently removed.',
      confirmLabel: 'Delete',
      danger: true,
      onConfirm: async () => {
        await deleteSession(sessionId);
        fetchSessions();
      },
    });
  };

  const handleSubmitFeedback = async () => {
    if (selectedFeedback && feedbackRating > 0) {
      const success = await submitFeedback(
        selectedFeedback,
        feedbackRating,
        feedbackComment
      );
      if (success) {
        setSelectedFeedback(null);
        setFeedbackRating(0);
        setFeedbackComment('');
      }
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  return (
    <DashboardLayout>
      {/* Chat layout: viewport-relative height so sidebar scroll always works */}
      <div className="flex gap-4 h-[calc(100vh-7rem)]">
        {/* Sidebar - Sessions List */}
        <div className="hidden lg:flex flex-col w-64 xl:w-72 shrink-0">
          {/* Use plain div (not Card) so flex-col + overflow chain is direct */}
          <div className="flex flex-col h-full bg-white rounded-lg border border-slate-200 shadow-sm overflow-hidden">
            <div className="shrink-0 p-4 border-b border-slate-200 space-y-3">
              <h2 className="text-base font-bold text-slate-900">💬 Conversations</h2>
              <button
                onClick={handleNewChat}
                className="w-full bg-blue-600 text-white py-2 px-4 rounded-lg hover:bg-blue-700 transition font-medium text-sm"
              >
                + New Chat
              </button>
            </div>
            <div className="flex-1 overflow-y-auto p-2">
              {initialising ? (
                <div className="p-4 text-center text-slate-400 text-sm">Loading...</div>
              ) : sessions.length === 0 ? (
                <div className="p-4 text-center text-slate-500 text-sm">
                  No conversations yet. Start a new one!
                </div>
              ) : (
                sessions.map((session) => (
                  <div
                    key={session.id}
                    onClick={() => loadSession(session.id)}
                    className={`p-3 mb-1.5 rounded-lg cursor-pointer transition-all ${
                      currentSession?.id === session.id
                        ? 'bg-blue-100 border border-blue-300'
                        : 'hover:bg-slate-100 border border-transparent'
                    }`}
                  >
                    <div className="flex items-start justify-between gap-2">
                      <div className="flex-1 min-w-0">
                        <p className="font-semibold text-slate-900 truncate text-sm">
                          {session.title}
                        </p>
                        <p className="text-xs text-slate-500 mt-0.5">
                          {new Date(session.updated_at).toLocaleDateString()}
                        </p>
                        <p className="text-xs text-slate-400">
                          {session.message_count || 0} msg{session.message_count !== 1 ? 's' : ''}
                        </p>
                      </div>
                      <button
                        onClick={(e) => handleDeleteSession(session.id, e)}
                        className="shrink-0 text-slate-300 hover:text-red-500 transition text-base leading-none pt-0.5"
                        title="Delete conversation"
                      >
                        ✕
                      </button>
                    </div>
                  </div>
                ))
              )}
            </div>
          </div>
        </div>

        {/* Main Chat Area */}
        <div className="flex-1 flex flex-col min-w-0">
          {initialising ? (
            <div className="flex items-center justify-center flex-1 bg-white rounded-lg border border-slate-200">
              <div className="text-center">
                <div className="w-8 h-8 border-2 border-blue-600 border-t-transparent rounded-full animate-spin mx-auto mb-3" />
                <p className="text-slate-500 text-sm">Loading conversations...</p>
              </div>
            </div>
          ) : currentSession ? (
            <div className="flex flex-col h-full bg-white rounded-lg border border-slate-200 shadow-sm overflow-hidden">
              {/* Header */}
              <div className="shrink-0 px-5 py-4 border-b border-slate-200 bg-gradient-to-r from-indigo-50 to-blue-50">
                <div className="flex items-center justify-between">
                  <div>
                    <h2 className="text-2xl font-bold text-slate-900">{currentSession.title}</h2>
                    <p className="text-sm text-slate-600 mt-1">
                      {messages.length} messages
                    </p>
                  </div>
                  <div className="text-2xl">💬</div>
                </div>
              </div>

              {/* Messages */}
              <div className="flex-1 overflow-y-auto p-6 space-y-4">
                {messages.length === 0 ? (
                  <div className="flex items-center justify-center h-full">
                    <div className="text-center max-w-md">
                      <h3 className="text-2xl font-bold text-slate-900 mb-3">
                        Welcome to Career Guidance! 👋
                      </h3>
                      <p className="text-slate-600 mb-6">
                        I'm here to help you with career development, freelancing tips, skill recommendations, and portfolio advice.
                      </p>
                      <div className="grid grid-cols-2 gap-3">
                        <div className="bg-blue-50 p-3 rounded-lg border border-blue-200">
                          <p className="font-semibold text-blue-900 text-sm">💼 Freelancing</p>
                          <p className="text-xs text-blue-700">Career paths & tips</p>
                        </div>
                        <div className="bg-green-50 p-3 rounded-lg border border-green-200">
                          <p className="font-semibold text-green-900 text-sm">🎯 Domains</p>
                          <p className="text-xs text-green-700">Find your niche</p>
                        </div>
                        <div className="bg-purple-50 p-3 rounded-lg border border-purple-200">
                          <p className="font-semibold text-purple-900 text-sm">📚 Skills</p>
                          <p className="text-xs text-purple-700">What to learn</p>
                        </div>
                        <div className="bg-orange-50 p-3 rounded-lg border border-orange-200">
                          <p className="font-semibold text-orange-900 text-sm">🎨 Portfolio</p>
                          <p className="text-xs text-orange-700">Showcase work</p>
                        </div>
                      </div>
                      <p className="text-xs text-slate-500 mt-4">
                        Try asking: "What skills should I learn for freelancing?"
                      </p>
                    </div>
                  </div>
                ) : (
                  messages.map((msg, idx) => (
                    <ChatMessage
                      key={idx}
                      message={msg}
                      onFeedbackClick={() => setSelectedFeedback(msg.id)}
                    />
                  ))
                )}
                {loading && (
                  <div className="flex justify-start">
                    <div className="bg-slate-100 rounded-lg px-4 py-3 rounded-bl-none border border-slate-200">
                      <div className="flex gap-2">
                        <div className="w-2 h-2 bg-slate-500 rounded-full animate-bounce"></div>
                        <div className="w-2 h-2 bg-slate-500 rounded-full animate-bounce" style={{ animationDelay: '0.1s' }}></div>
                        <div className="w-2 h-2 bg-slate-500 rounded-full animate-bounce" style={{ animationDelay: '0.2s' }}></div>
                      </div>
                    </div>
                  </div>
                )}
                {error && (
                  <Alert type="error" title="Error" message={error} />
                )}
                <div ref={messagesEndRef} />
              </div>

              {/* Input Area */}
              <div className="border-t border-slate-200 p-4 bg-slate-50">
                <div className="flex gap-3">
                  <textarea
                    value={inputValue}
                    onChange={(e) => setInputValue(e.target.value)}
                    onKeyPress={handleKeyPress}
                    placeholder="Ask me about career development..."
                    disabled={loading}
                    rows="3"
                    className="flex-1 p-3 border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-600 disabled:opacity-50 disabled:bg-slate-100 resize-none text-sm"
                  />
                  <button
                    onClick={handleSend}
                    disabled={loading || !inputValue.trim()}
                    className="bg-blue-600 text-white px-6 py-3 rounded-lg hover:bg-blue-700 transition disabled:opacity-50 disabled:cursor-not-allowed self-end font-medium text-sm"
                  >
                    Send →
                  </button>
                </div>
              </div>
            </div>
          ) : (
            /* No session selected — show welcome screen */
            <div className="flex flex-col items-center justify-center flex-1 bg-white rounded-lg border border-slate-200 text-center p-8">
              <div className="text-5xl mb-4">💬</div>
              <h3 className="text-xl font-bold text-slate-900 mb-2">Start a conversation</h3>
              <p className="text-slate-500 text-sm mb-6 max-w-xs">
                Get career guidance, freelancing tips, skill recommendations and more from your AI assistant.
              </p>
              <button
                onClick={handleNewChat}
                className="px-6 py-2.5 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition font-medium text-sm"
              >
                + New Chat
              </button>
            </div>
          )}
        </div>
      </div>

      {/* Feedback Modal */}
      {selectedFeedback && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <Card className="max-w-sm w-full mx-4">
            <CardBody>
              <h3 className="text-lg font-bold mb-4 text-slate-900">Rate this response</h3>
              
              <div className="flex justify-center gap-3 mb-4">
                {[1, 2, 3, 4, 5].map((rating) => (
                  <button
                    key={rating}
                    onClick={() => setFeedbackRating(rating)}
                    className={`text-3xl transition transform ${
                      feedbackRating >= rating ? 'scale-110' : 'opacity-40'
                    }`}
                  >
                    {rating <= 2 ? '👎' : rating === 3 ? '😐' : '👍'}
                  </button>
                ))}
              </div>

              <textarea
                value={feedbackComment}
                onChange={(e) => setFeedbackComment(e.target.value)}
                placeholder="Optional: Share your feedback..."
                rows="3"
                className="w-full p-3 border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-600 resize-none mb-4 text-sm"
              />

              <div className="flex gap-3">
                <button
                  onClick={() => setSelectedFeedback(null)}
                  className="flex-1 px-4 py-2 border border-slate-300 rounded-lg hover:bg-slate-50 transition text-sm font-medium"
                >
                  Cancel
                </button>
                <button
                  onClick={handleSubmitFeedback}
                  disabled={feedbackRating === 0}
                  className="flex-1 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition disabled:opacity-50 text-sm font-medium"
                >
                  Submit
                </button>
              </div>
            </CardBody>
          </Card>
        </div>
      )}
      <ConfirmModal config={confirmModal} onClose={() => setConfirmModal(null)} />
    </DashboardLayout>
  );
};

export default ChatPage;
