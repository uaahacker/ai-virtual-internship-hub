import { useState, useCallback } from 'react';
import DashboardLayout from '../components/DashboardLayout';
import { useNotification } from '../contexts/NotificationContext';
import { FiBell, FiCheck, FiCheckCircle, FiAlertCircle, FiInfo, FiStar, FiRefreshCw } from 'react-icons/fi';
import { toast } from 'react-toastify';

const TYPE_META = {
  task:         { icon: '🎯', color: 'bg-blue-100 text-blue-700',    label: 'Task' },
  review:       { icon: '📋', color: 'bg-purple-100 text-purple-700', label: 'Review' },
  announcement: { icon: '📢', color: 'bg-yellow-100 text-yellow-700', label: 'Announcement' },
  message:      { icon: '💬', color: 'bg-green-100 text-green-700',   label: 'Message' },
  system:       { icon: '⚙️', color: 'bg-slate-100 text-slate-600',   label: 'System' },
};

function timeAgo(dateStr) {
  const diff = Math.floor((Date.now() - new Date(dateStr)) / 1000);
  if (diff < 60) return 'just now';
  if (diff < 3600) return `${Math.floor(diff / 60)}m ago`;
  if (diff < 86400) return `${Math.floor(diff / 3600)}h ago`;
  return `${Math.floor(diff / 86400)}d ago`;
}

export default function NotificationsPage() {
  const { notifications, unreadCount, markRead, markAllRead, refreshNotifications } = useNotification();
  const [filter, setFilter] = useState('all'); // 'all' | 'unread' | type
  const [refreshing, setRefreshing] = useState(false);

  const handleRefresh = useCallback(async () => {
    setRefreshing(true);
    await refreshNotifications();
    setRefreshing(false);
  }, [refreshNotifications]);

  const handleMarkAllRead = async () => {
    await markAllRead();
    toast.success('All notifications marked as read');
  };

  const filtered = notifications.filter((n) => {
    if (filter === 'unread') return n.status === 'Unread';
    if (filter === 'all') return true;
    return n.notification_type === filter;
  });

  const types = ['all', 'unread', ...Object.keys(TYPE_META)];

  return (
    <DashboardLayout>
      <div className="max-w-3xl mx-auto">
        {/* Header */}
        <div className="flex items-center justify-between mb-6">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 bg-blue-100 rounded-xl flex items-center justify-center">
              <FiBell size={20} className="text-blue-600" />
            </div>
            <div>
              <h1 className="text-2xl font-bold text-slate-900">Notifications</h1>
              <p className="text-sm text-slate-500">
                {unreadCount > 0 ? `${unreadCount} unread` : 'All caught up'}
              </p>
            </div>
          </div>
          <div className="flex items-center gap-2">
            <button
              onClick={handleRefresh}
              className={`p-2 rounded-lg border border-slate-200 hover:bg-slate-50 text-slate-600 transition ${refreshing ? 'animate-spin' : ''}`}
              title="Refresh"
            >
              <FiRefreshCw size={16} />
            </button>
            {unreadCount > 0 && (
              <button
                onClick={handleMarkAllRead}
                className="flex items-center gap-1.5 px-4 py-2 bg-blue-600 text-white text-sm font-medium rounded-lg hover:bg-blue-700 transition"
              >
                <FiCheckCircle size={15} />
                Mark all read
              </button>
            )}
          </div>
        </div>

        {/* Filter tabs */}
        <div className="flex gap-2 flex-wrap mb-5">
          {types.map((t) => {
            const meta = TYPE_META[t];
            const label = t === 'all' ? 'All' : t === 'unread' ? `Unread (${unreadCount})` : meta?.label || t;
            return (
              <button
                key={t}
                onClick={() => setFilter(t)}
                className={`px-3 py-1.5 rounded-full text-xs font-semibold transition border ${
                  filter === t
                    ? 'bg-blue-600 text-white border-blue-600'
                    : 'bg-white text-slate-600 border-slate-200 hover:bg-slate-50'
                }`}
              >
                {t !== 'all' && t !== 'unread' && <span className="mr-1">{meta?.icon}</span>}
                {label}
              </button>
            );
          })}
        </div>

        {/* Notification list */}
        {filtered.length === 0 ? (
          <div className="text-center py-20">
            <FiBell size={48} className="mx-auto text-slate-300 mb-4" />
            <p className="text-slate-500 font-medium">No notifications here</p>
            <p className="text-slate-400 text-sm mt-1">
              {filter === 'unread' ? 'You have no unread notifications.' : 'Nothing to show for this filter.'}
            </p>
          </div>
        ) : (
          <div className="space-y-2">
            {filtered.map((n) => {
              const meta = TYPE_META[n.notification_type] || TYPE_META.system;
              const isUnread = n.status === 'Unread';
              return (
                <div
                  key={n.id}
                  onClick={() => isUnread && markRead(n.id)}
                  className={`flex gap-4 p-4 rounded-xl border transition cursor-pointer group ${
                    isUnread
                      ? 'bg-blue-50 border-blue-200 hover:bg-blue-100'
                      : 'bg-white border-slate-200 hover:bg-slate-50'
                  }`}
                >
                  {/* Icon */}
                  <div className={`w-10 h-10 shrink-0 rounded-xl flex items-center justify-center text-lg ${meta.color}`}>
                    {meta.icon}
                  </div>

                  {/* Content */}
                  <div className="flex-1 min-w-0">
                    <div className="flex items-start justify-between gap-2">
                      <p className={`text-sm font-semibold ${isUnread ? 'text-slate-900' : 'text-slate-700'}`}>
                        {n.title}
                      </p>
                      <div className="flex items-center gap-2 shrink-0">
                        <span className="text-xs text-slate-400">{timeAgo(n.created_at)}</span>
                        {isUnread && (
                          <span className="w-2 h-2 rounded-full bg-blue-500 shrink-0" />
                        )}
                      </div>
                    </div>
                    <p className="text-sm text-slate-500 mt-0.5 line-clamp-2">{n.message}</p>
                    <div className="flex items-center justify-between mt-2">
                      <span className={`text-xs font-medium px-2 py-0.5 rounded-full ${meta.color}`}>
                        {meta.label}
                      </span>
                      {isUnread && (
                        <button
                          onClick={(e) => { e.stopPropagation(); markRead(n.id); }}
                          className="text-xs text-blue-600 hover:text-blue-800 flex items-center gap-1 opacity-0 group-hover:opacity-100 transition"
                        >
                          <FiCheck size={12} />
                          Mark read
                        </button>
                      )}
                    </div>
                  </div>
                </div>
              );
            })}
          </div>
        )}
      </div>
    </DashboardLayout>
  );
}
