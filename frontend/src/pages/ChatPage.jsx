import React, { useState, useEffect, useRef } from 'react';
import { useChat } from '../contexts/ChatContext';
import DashboardLayout from '../components/DashboardLayout';
import { Card, CardHeader, CardBody } from '../components/CardComponents';
import { EmptyState, Alert } from '../components/ProgressAndUtilityComponents';

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
  const messagesEndRef = useRef(null);

  useEffect(() => {
    fetchSessions();
  }, [fetchSessions]);

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
    if (window.confirm('Are you sure you want to delete this chat?')) {
      await deleteSession(sessionId);
      fetchSessions();
    }
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
      <div className="flex gap-6 h-full">
        {/* Sidebar - Sessions List */}
        <div className="hidden lg:block w-72 flex-shrink-0">
          <Card className="flex flex-col h-full">
            <CardHeader className="border-b border-slate-200">
              <div className="flex items-center justify-between mb-4">
                <h2 className="text-lg font-bold text-slate-900">💬 Conversations</h2>
              </div>
              <button
                onClick={handleNewChat}
                className="w-full bg-blue-600 text-white py-2 px-4 rounded-lg hover:bg-blue-700 transition font-medium text-sm"
              >
                + New Chat
              </button>
            </CardHeader>
            <div className="flex-1 overflow-y-auto p-2">
              {sessions.length === 0 ? (
                <div className="p-4 text-center text-slate-500 text-sm">
                  No conversations yet. Start a new one!
                </div>
              ) : (
                sessions.map((session) => (
                  <div
                    key={session.id}
                    onClick={() => loadSession(session.id)}
                    className={`p-3 mb-2 rounded-lg cursor-pointer transition-all ${
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
                        <p className="text-xs text-slate-500 mt-1">
                          {new Date(session.updated_at).toLocaleDateString()}
                        </p>
                        <p className="text-xs text-slate-400 mt-0.5">
                          {session.message_count || 0} messages
                        </p>
                      </div>
                      <button
                        onClick={(e) => handleDeleteSession(session.id, e)}
                        className="text-slate-400 hover:text-red-600 transition text-lg leading-none"
                        title="Delete conversation"
                      >
                        ✕
                      </button>
                    </div>
                  </div>
                ))
              )}
            </div>
          </Card>
        </div>

        {/* Main Chat Area */}
        <div className="flex-1 flex flex-col">
          {currentSession ? (
            <Card className="flex flex-col h-full">
              {/* Header */}
              <CardHeader className="border-b border-slate-200 bg-gradient-to-r from-indigo-50 to-blue-50">
                <div className="flex items-center justify-between">
                  <div>
                    <h2 className="text-2xl font-bold text-slate-900">{currentSession.title}</h2>
                    <p className="text-sm text-slate-600 mt-1">
                      {messages.length} messages
                    </p>
                  </div>
                  <div className="text-3xl">💬</div>
                </div>
              </CardHeader>

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
                    <div
                      key={idx}
                      className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}
                    >
                      <div className="max-w-2xl">
                        <div
                          className={`px-4 py-3 rounded-lg ${
                            msg.role === 'user'
                              ? 'bg-blue-600 text-white rounded-br-none'
                              : 'bg-slate-100 text-slate-900 rounded-bl-none border border-slate-200'
                          }`}
                        >
                          <p className="break-words text-sm">{msg.content}</p>
                        </div>
                        <div className="flex items-center justify-between mt-2 px-1">
                          <p className="text-xs text-slate-500">
                            {new Date(msg.created_at).toLocaleTimeString([], {
                              hour: '2-digit',
                              minute: '2-digit'
                            })}
                          </p>
                          {msg.role === 'assistant' && (
                            <div className="flex gap-2">
                              <button
                                onClick={() => setSelectedFeedback(msg.id)}
                                className="text-xs text-slate-500 hover:text-green-600 transition"
                                title="Helpful"
                              >
                                👍
                              </button>
                              <button
                                onClick={() => setSelectedFeedback(msg.id)}
                                className="text-xs text-slate-500 hover:text-red-600 transition"
                                title="Not helpful"
                              >
                                👎
                              </button>
                            </div>
                          )}
                        </div>
                      </div>
                    </div>
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
            </Card>
          ) : (
            <EmptyState
              icon="💬"
              title="No conversation selected"
              description="Select a conversation or start a new chat to begin"
              action={
                <button
                  onClick={handleNewChat}
                  className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition font-medium"
                >
                  Start New Chat
                </button>
              }
            />
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
    </DashboardLayout>
  );
};

export default ChatPage;
