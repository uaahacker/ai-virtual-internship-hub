import React, { useState, useEffect, useRef } from 'react';
import { useChat } from '../contexts/ChatContext';

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

  // Load sessions on mount
  useEffect(() => {
    fetchSessions();
  }, [fetchSessions]);

  // Auto-scroll to bottom
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
    <div className="flex h-screen bg-gray-100">
      {/* Sidebar - Sessions List */}
      <div className="w-64 bg-white border-r border-gray-300 shadow-sm flex flex-col">
        <div className="p-4 border-b border-gray-300">
          <h1 className="text-xl font-bold text-gray-800 mb-4">Career Bot</h1>
          <button
            onClick={handleNewChat}
            className="w-full bg-blue-600 text-white py-2 px-4 rounded hover:bg-blue-700 transition font-medium"
          >
            + New Chat
          </button>
        </div>

        <div className="flex-1 overflow-y-auto">
          {sessions.length === 0 ? (
            <div className="p-4 text-center text-gray-500 text-sm">
              No conversations yet
            </div>
          ) : (
            sessions.map((session) => (
              <div
                key={session.id}
                onClick={() => loadSession(session.id)}
                className={`p-4 border-b border-gray-200 cursor-pointer transition ${
                  currentSession?.id === session.id
                    ? 'bg-blue-50 border-l-4 border-l-blue-600'
                    : 'hover:bg-gray-50'
                }`}
              >
                <div className="flex items-start justify-between gap-2">
                  <div className="flex-1 min-w-0">
                    <p className="font-semibold text-gray-800 truncate text-sm">
                      {session.title}
                    </p>
                    <p className="text-xs text-gray-500 mt-1">
                      {new Date(session.updated_at).toLocaleDateString()}
                    </p>
                    <p className="text-xs text-gray-400 mt-0.5">
                      {session.message_count} messages
                    </p>
                  </div>
                  <button
                    onClick={(e) => handleDeleteSession(session.id, e)}
                    className="text-gray-400 hover:text-red-600 transition text-lg leading-none"
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

      {/* Main Chat Area */}
      <div className="flex-1 flex flex-col">
        {currentSession ? (
          <>
            {/* Header */}
            <div className="bg-white border-b border-gray-300 p-6 shadow-sm">
              <h2 className="text-2xl font-bold text-gray-800">{currentSession.title}</h2>
              <p className="text-sm text-gray-500 mt-1">
                {messages.length} messages
              </p>
            </div>

            {/* Messages */}
            <div className="flex-1 overflow-y-auto p-6 space-y-4">
              {messages.length === 0 ? (
                <div className="flex items-center justify-center h-full text-center">
                  <div>
                    <h3 className="text-2xl font-bold text-gray-800 mb-4">
                      Welcome to Career Guidance! 👋
                    </h3>
                    <p className="text-gray-600 mb-4">
                      I'm here to help you with your professional development.
                    </p>
                    <div className="grid grid-cols-2 gap-4 mt-8">
                      <div className="bg-blue-50 p-4 rounded-lg">
                        <p className="font-semibold text-blue-900">💼 Freelancing</p>
                        <p className="text-sm text-blue-700">Career paths and tips</p>
                      </div>
                      <div className="bg-green-50 p-4 rounded-lg">
                        <p className="font-semibold text-green-900">🎯 Domains</p>
                        <p className="text-sm text-green-700">Find your specialty</p>
                      </div>
                      <div className="bg-purple-50 p-4 rounded-lg">
                        <p className="font-semibold text-purple-900">📚 Skills</p>
                        <p className="text-sm text-purple-700">What to learn next</p>
                      </div>
                      <div className="bg-orange-50 p-4 rounded-lg">
                        <p className="font-semibold text-orange-900">🎨 Portfolio</p>
                        <p className="text-sm text-orange-700">Show your best work</p>
                      </div>
                    </div>
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
                        className={`px-6 py-3 rounded-lg ${
                          msg.role === 'user'
                            ? 'bg-blue-600 text-white rounded-br-none'
                            : 'bg-gray-200 text-gray-900 rounded-bl-none'
                        }`}
                      >
                        <p className="break-words">{msg.content}</p>
                      </div>
                      {msg.role === 'assistant' && (
                        <div className="flex gap-2 mt-2 items-center">
                          <button
                            onClick={() => setSelectedFeedback(msg.id)}
                            className="text-xs text-gray-500 hover:text-gray-700 transition"
                          >
                            👍 Helpful
                          </button>
                          <button
                            onClick={() => setSelectedFeedback(msg.id)}
                            className="text-xs text-gray-500 hover:text-gray-700 transition"
                          >
                            👎 Not helpful
                          </button>
                        </div>
                      )}
                      <p className="text-xs text-gray-500 mt-1">
                        {new Date(msg.created_at).toLocaleTimeString()}
                      </p>
                    </div>
                  </div>
                ))
              )}
              {loading && (
                <div className="flex justify-start">
                  <div className="bg-gray-200 rounded-lg px-6 py-3 rounded-bl-none">
                    <div className="flex gap-2">
                      <div className="w-2 h-2 bg-gray-500 rounded-full animate-bounce"></div>
                      <div className="w-2 h-2 bg-gray-500 rounded-full animate-bounce delay-100"></div>
                      <div className="w-2 h-2 bg-gray-500 rounded-full animate-bounce delay-200"></div>
                    </div>
                  </div>
                </div>
              )}
              {error && (
                <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded">
                  Error: {error}
                </div>
              )}
              <div ref={messagesEndRef} />
            </div>

            {/* Input Area */}
            <div className="bg-white border-t border-gray-300 p-6">
              <div className="flex gap-3">
                <textarea
                  value={inputValue}
                  onChange={(e) => setInputValue(e.target.value)}
                  onKeyPress={handleKeyPress}
                  placeholder="Ask me about your career development..."
                  disabled={loading}
                  rows="3"
                  className="flex-1 p-3 border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-blue-600 disabled:opacity-50 resize-none"
                />
                <button
                  onClick={handleSend}
                  disabled={loading || !inputValue.trim()}
                  className="bg-blue-600 text-white px-6 py-3 rounded hover:bg-blue-700 transition disabled:opacity-50 disabled:cursor-not-allowed self-end font-medium"
                >
                  Send
                </button>
              </div>
            </div>
          </>
        ) : (
          <div className="flex items-center justify-center h-full">
            <div className="text-center">
              <p className="text-2xl text-gray-600 mb-4">No conversation selected</p>
              <button
                onClick={handleNewChat}
                className="bg-blue-600 text-white px-6 py-3 rounded hover:bg-blue-700 transition font-medium"
              >
                Start New Chat
              </button>
            </div>
          </div>
        )}
      </div>

      {/* Feedback Modal */}
      {selectedFeedback && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg shadow-lg p-6 max-w-sm w-full mx-4">
            <h3 className="text-lg font-bold mb-4">Rate this response</h3>
            
            <div className="flex justify-center gap-2 mb-4">
              {[1, 2, 3, 4, 5].map((rating) => (
                <button
                  key={rating}
                  onClick={() => setFeedbackRating(rating)}
                  className={`text-3xl transition ${
                    feedbackRating >= rating ? 'opacity-100' : 'opacity-30'
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
              className="w-full p-3 border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-blue-600 resize-none mb-4"
            />

            <div className="flex gap-3">
              <button
                onClick={() => setSelectedFeedback(null)}
                className="flex-1 px-4 py-2 border border-gray-300 rounded hover:bg-gray-50 transition"
              >
                Cancel
              </button>
              <button
                onClick={handleSubmitFeedback}
                disabled={feedbackRating === 0}
                className="flex-1 px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 transition disabled:opacity-50"
              >
                Submit
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default ChatPage;
