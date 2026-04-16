import React, { createContext, useContext, useState, useCallback } from 'react';

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
      const token = localStorage.getItem('access_token');
      const response = await fetch('/api/chatbot/sessions/', {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
      });
      
      if (!response.ok) throw new Error('Failed to fetch sessions');
      
      const data = await response.json();
      setSessions(data.data || []);
    } catch (err) {
      setError(err.message);
      console.error('Error fetching sessions:', err);
    }
  }, []);

  // Create new session
  const createSession = useCallback(async (title = 'Career Guidance Chat') => {
    try {
      setError(null);
      setLoading(true);
      const token = localStorage.getItem('access_token');
      const response = await fetch('/api/chatbot/sessions/', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ title }),
      });
      
      if (!response.ok) throw new Error('Failed to create session');
      
      const data = await response.json();
      const newSession = data.data;
      setSessions(prev => [newSession, ...prev]);
      setCurrentSession(newSession);
      setMessages([]);
      return newSession;
    } catch (err) {
      setError(err.message);
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
      const token = localStorage.getItem('access_token');
      const response = await fetch(`/api/chatbot/sessions/${sessionId}/`, {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
      });
      
      if (!response.ok) throw new Error('Failed to load session');
      
      const data = await response.json();
      const session = data.data;
      setCurrentSession(session);
      setMessages(session.messages || []);
    } catch (err) {
      setError(err.message);
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

      const token = localStorage.getItem('access_token');
      const response = await fetch(`/api/chatbot/sessions/${currentSession.id}/messages/`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ content }),
      });
      
      if (!response.ok) throw new Error('Failed to send message');
      
      const data = await response.json();
      // Replace messages with server response (includes both user and assistant)
      setMessages(prev => {
        // Remove the optimistically added user message and add server messages
        const filtered = prev.filter(m => m.content !== content || m.role !== 'user');
        return [...filtered, ...data.data];
      });
    } catch (err) {
      setError(err.message);
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
      const token = localStorage.getItem('access_token');
      const response = await fetch(`/api/chatbot/sessions/${sessionId}/`, {
        method: 'DELETE',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
      });
      
      if (!response.ok) throw new Error('Failed to delete session');
      
      setSessions(prev => prev.filter(s => s.id !== sessionId));
      if (currentSession?.id === sessionId) {
        setCurrentSession(null);
        setMessages([]);
      }
    } catch (err) {
      setError(err.message);
      console.error('Error deleting session:', err);
    }
  }, [currentSession]);

  // Submit feedback
  const submitFeedback = useCallback(async (messageId, rating, comment = '') => {
    try {
      const token = localStorage.getItem('access_token');
      const response = await fetch('/api/chatbot/feedback/', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ message_id: messageId, rating, comment }),
      });
      
      if (!response.ok) throw new Error('Failed to submit feedback');
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
};

export const useChat = () => {
  const context = useContext(ChatContext);
  if (!context) {
    throw new Error('useChat must be used within ChatProvider');
  }
  return context;
};
