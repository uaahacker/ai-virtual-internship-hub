import { createContext, useContext, useState, useEffect, useCallback, useRef } from 'react';
import { notificationService } from '../services/endpoints';
import { useAuth } from './AuthContext';

const NotificationContext = createContext(null);

export function NotificationProvider({ children }) {
  const { user } = useAuth();
  const [notifications, setNotifications] = useState([]);
  const [unreadCount, setUnreadCount] = useState(0);
  const intervalRef = useRef(null);

  const refreshNotifications = useCallback(async () => {
    if (!user) return;
    try {
      const res = await notificationService.list();
      if (res.data.success) {
        const list = res.data.data || [];
        setNotifications(list);
        setUnreadCount(list.filter((n) => n.status === 'Unread').length);
      }
    } catch {
      // silent
    }
  }, [user]);

  useEffect(() => {
    if (!user) {
      setNotifications([]);
      setUnreadCount(0);
      return;
    }
    refreshNotifications();
    intervalRef.current = setInterval(refreshNotifications, 30000);
    return () => clearInterval(intervalRef.current);
  }, [user, refreshNotifications]);

  const markRead = useCallback(async (id) => {
    try {
      await notificationService.markRead(id);
      setNotifications((prev) =>
        prev.map((n) => (n.id === id ? { ...n, status: 'Read' } : n))
      );
      setUnreadCount((c) => Math.max(0, c - 1));
    } catch {
      // silent
    }
  }, []);

  const markAllRead = useCallback(async () => {
    try {
      await notificationService.markAllRead();
      setNotifications((prev) => prev.map((n) => ({ ...n, status: 'Read' })));
      setUnreadCount(0);
    } catch {
      // silent
    }
  }, []);

  return (
    <NotificationContext.Provider value={{ notifications, unreadCount, markRead, markAllRead, refreshNotifications }}>
      {children}
    </NotificationContext.Provider>
  );
}

export function useNotification() {
  const ctx = useContext(NotificationContext);
  if (!ctx) throw new Error('useNotification must be used within NotificationProvider');
  return ctx;
}
