import React, { useState, useEffect, useRef } from 'react';
import { useChat } from '../contexts/ChatContext';
import ChatMessage from './ChatMessage';

const ChatWidget = ({ isOpen, onClose, isMinimized, onMinimize }) => {
  const {
    currentSession,
    messages,
    loading,
    error,
    createSession,
    sendMessage,
  } = useChat();
  
  const [inputValue, setInputValue] = useState('');
  const [isInitializing, setIsInitializing] = useState(false);
  const messagesEndRef = useRef(null);

  // Auto-scroll to bottom
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  // Initialize session on first open
  useEffect(() => {
    if (isOpen && !currentSession && !isInitializing) {
      setIsInitializing(true);
      createSession().finally(() => setIsInitializing(false));
    }
  }, [isOpen, currentSession, createSession, isInitializing]);

  const handleSend = async () => {
    if (!inputValue.trim()) return;
    
    const message = inputValue;
    setInputValue('');
    await sendMessage(message);
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  if (!isOpen) return null;

  return (
    <div className="fixed bottom-0 right-0 w-96 h-96 bg-white border-l border-t border-gray-300 shadow-2xl flex flex-col rounded-tl-lg">
      {/* Header */}
      <div className="flex items-center justify-between p-4 bg-gradient-to-r from-blue-600 to-blue-700 text-white rounded-tl-lg">
        <div className="flex items-center gap-2">
          <div className="w-2 h-2 rounded-full bg-green-400 animate-pulse"></div>
          <span className="font-semibold">Career Guidance Bot</span>
        </div>
        <div className="flex gap-2">
          <button
            onClick={() => onMinimize(!isMinimized)}
            className="hover:bg-blue-800 p-1 rounded transition"
            title={isMinimized ? 'Expand' : 'Minimize'}
          >
            {isMinimized ? '▲' : '▼'}
          </button>
          <button
            onClick={onClose}
            className="hover:bg-red-600 p-1 rounded transition"
            title="Close"
          >
            ✕
          </button>
        </div>
      </div>

      {isMinimized ? null : (
        <>
          {/* Messages Area */}
          <div className="flex-1 overflow-y-auto p-4 space-y-4 bg-gray-50">
            {messages.length === 0 ? (
              <div className="flex items-center justify-center h-full text-gray-500 text-center">
                <div>
                  <p className="text-lg font-semibold mb-2">Welcome! 👋</p>
                  <p className="text-sm">Ask me about:</p>
                  <ul className="text-xs mt-2 space-y-1">
                    <li>• Freelancing tips</li>
                    <li>• Recommended domains</li>
                    <li>• Skill development</li>
                    <li>• Portfolio advice</li>
                  </ul>
                </div>
              </div>
            ) : (
              messages.map((msg, idx) => (
                <ChatMessage key={idx} message={msg} />
              ))
            )}
            {loading && (
              <div className="flex justify-start">
                <div className="bg-gray-200 rounded-lg px-4 py-2 rounded-bl-none">
                  <div className="flex gap-1">
                    <div className="w-2 h-2 bg-gray-500 rounded-full animate-bounce"></div>
                    <div className="w-2 h-2 bg-gray-500 rounded-full animate-bounce delay-100"></div>
                    <div className="w-2 h-2 bg-gray-500 rounded-full animate-bounce delay-200"></div>
                  </div>
                </div>
              </div>
            )}
            {error && (
              <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-2 rounded text-sm">
                Error: {error}
              </div>
            )}
            <div ref={messagesEndRef} />
          </div>

          {/* Input Area */}
          <div className="border-t border-gray-300 p-4 bg-white">
            <div className="flex gap-2">
              <textarea
                value={inputValue}
                onChange={(e) => setInputValue(e.target.value)}
                onKeyPress={handleKeyPress}
                placeholder="Ask about your career..."
                disabled={loading}
                rows="2"
                className="flex-1 p-2 border border-gray-300 rounded resize-none focus:outline-none focus:ring-2 focus:ring-blue-600 disabled:opacity-50"
              />
              <button
                onClick={handleSend}
                disabled={loading || !inputValue.trim()}
                className="bg-blue-600 text-white px-3 py-2 rounded hover:bg-blue-700 transition disabled:opacity-50 disabled:cursor-not-allowed self-end"
                title="Send message (Ctrl+Enter)"
              >
                ▶
              </button>
            </div>
          </div>
        </>
      )}
    </div>
  );
};

export default ChatWidget;
