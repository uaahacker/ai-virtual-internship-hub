import React, { createContext, useContext, useState, useCallback } from 'react';
import api from '../services/api';

// Chat context for managing chatbot state
const ChatContext = createContext();

export const ChatProvider = ({ children }) => {
  const [sessions, setSessions] = useState([]);
  const [currentSession, setCurrentSession] = useState(null);
  const [messages, setMessages] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  // Fetch all sessions
  const fetchSessions = useCallback(async () => {
    try {
      setError(null);
      const response = await api.get('/chatbot/sessions/');
      setSessions(response.data.data || []);
    } catch (err) {
      const errorMsg = err.message || 'Failed to fetch sessions';
      setError(errorMsg);
      console.error('Error fetching sessions:', err);
    }
  }, []);

  // Create new session
  const createSession = useCallback(async (title = 'Career Guidance Chat') => {
    try {
      setError(null);
      setLoading(true);
      const response = await api.post('/chatbot/sessions/', { title });
      const newSession = response.data.data;
      setSessions(prev => [newSession, ...prev]);
      setCurrentSession(newSession);
      setMessages([]);
      return newSession;
    } catch (err) {
      setError(err.message || 'Failed to create session');
      console.error('Error creating session:', err);
    } finally {
      setLoading(false);
    }
  }, []);

  // Load session
  const loadSession = useCallback(async (sessionId) => {
    try {
      setError(null);
      setLoading(true);
      const response = await api.get(`/chatbot/sessions/${sessionId}/`);
      const session = response.data.data;
      setCurrentSession(session);
      setMessages(session.messages || []);
    } catch (err) {
      setError(err.message || 'Failed to load session');
      console.error('Error loading session:', err);
    } finally {
      setLoading(false);
    }
  }, []);

  // Send message
  const sendMessage = useCallback(async (content) => {
    if (!currentSession) {
      setError('No active session');
      return;
    }

    try {
      setError(null);
      setLoading(true);
      
      // Add user message optimistically
      const userMessage = {
        role: 'user',
        content,
        created_at: new Date().toISOString(),
      };
      setMessages(prev => [...prev, userMessage]);

      const response = await api.post(`/chatbot/sessions/${currentSession.id}/messages/`, { content }, { timeout: 150000 }); // 2.5 min — free LLMs can be slow
      
      // Replace messages with server response (includes both user and assistant)
      setMessages(prev => {
        // Remove the optimistically added user message and add server messages
        const filtered = prev.filter(m => m.content !== content || m.role !== 'user');
        return [...filtered, ...response.data.data];
      });
    } catch (err) {
      setError(err.message || 'Failed to send message');
      // Remove optimistically added message on error
      setMessages(prev => prev.filter(m => m.content !== content || m.role !== 'user'));
      console.error('Error sending message:', err);
    } finally {
      setLoading(false);
    }
  }, [currentSession]);

  // Delete session
  const deleteSession = useCallback(async (sessionId) => {
    try {
      setError(null);
      await api.delete(`/chatbot/sessions/${sessionId}/`);
      setSessions(prev => prev.filter(s => s.id !== sessionId));
      if (currentSession?.id === sessionId) {
        setCurrentSession(null);
        setMessages([]);
      }
    } catch (err) {
      setError(err.message || 'Failed to delete session');
      console.error('Error deleting session:', err);
    }
  }, [currentSession]);

  // Submit feedback
  const submitFeedback = useCallback(async (messageId, rating, comment = '') => {
    try {
      await api.post('/chatbot/feedback/', { message_id: messageId, rating, comment });
      return true;
    } catch (err) {
      console.error('Error submitting feedback:', err);
      return false;
    }
  }, []);

  const value = {
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
  };

  return (
    <ChatContext.Provider value={value}>
      {children}
    </ChatContext.Provider>
  );
}

export const useChat = () => {
  const context = useContext(ChatContext);
  if (!context) {
    throw new Error('useChat must be used within ChatProvider');
  }
  return context;
};
