import { NavLink, useNavigate, useLocation } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import { useNotification } from '../contexts/NotificationContext';
import { useState, useRef, useEffect } from 'react';
import { FiSettings, FiLogOut, FiBell } from 'react-icons/fi';

export default function DashboardLayout({ children }) {
  const { user, logout } = useAuth();
  const { notifications, unreadCount, markRead, markAllRead } = useNotification();
  const navigate = useNavigate();
  const location = useLocation();
  const [sidebarOpen, setSidebarOpen] = useState(true);
  const [settingsMenuOpen, setSettingsMenuOpen] = useState(false);
  const [notifOpen, setNotifOpen] = useState(false);
  const notifRef = useRef(null);

  // Close notification panel on outside click
  useEffect(() => {
    function handleClickOutside(e) {
      if (notifRef.current && !notifRef.current.contains(e.target)) {
        setNotifOpen(false);
      }
    }
    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  const handleLogout = async () => {
    await logout();
    navigate('/login');
  };

  const handleSettingsClick = () => {
    if (user?.role === 'Student') {
      navigate('/student/settings');
    } else if (user?.role === 'Mentor') {
      navigate('/mentor/settings');
    }
    setSettingsMenuOpen(false);
  };

  const navItems = getNavItems(user?.role);

  return (
    <div className="flex min-h-screen bg-slate-50">
      {/* Mobile Sidebar Overlay */}
      {sidebarOpen && (
        <div
          className="fixed inset-0 bg-black bg-opacity-50 md:hidden z-30"
          onClick={() => setSidebarOpen(false)}
        />
      )}

      {/* Sidebar */}
      <aside
        className={`fixed md:relative left-0 top-0 h-screen w-64 bg-gradient-to-b from-slate-900 to-slate-800 text-white transition-transform duration-300 z-40 ${
          sidebarOpen ? 'translate-x-0' : '-translate-x-full'
        } md:translate-x-0`}
      >
        {/* Logo */}
        <div className="p-6 border-b border-slate-700">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 bg-gradient-to-br from-blue-500 to-blue-600 rounded-lg flex items-center justify-center font-bold text-white">
              🎓
            </div>
            <div>
              <h1 className="font-bold text-sm text-white">Virtual Hub</h1>
              <p className="text-xs text-slate-400">Internship Platform</p>
            </div>
          </div>
        </div>

        {/* Navigation */}
        <nav className="flex-1 py-4 px-2 space-y-1 overflow-y-auto">
          {navItems.map((item) => (
            <NavLink
              key={item.path}
              to={item.path}
              onClick={() => setSidebarOpen(false)}
              className={({ isActive }) =>
                `flex items-center gap-3 px-4 py-3 rounded-lg text-sm font-medium transition-all duration-200 ${
                  isActive
                    ? 'bg-blue-600 text-white shadow-lg'
                    : 'text-slate-300 hover:bg-slate-700 hover:text-white'
                }`
              }
            >
              <span className="text-lg">{item.icon}</span>
              {item.label}
            </NavLink>
          ))}
        </nav>

        {/* User Info */}
        <div className="p-4 border-t border-slate-700 space-y-4">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 bg-slate-700 rounded-full flex items-center justify-center font-bold">
              {user?.name?.charAt(0)?.toUpperCase()}
            </div>
            <div className="flex-1 min-w-0">
              <p className="text-sm font-medium text-white truncate">{user?.name}</p>
              <p className="text-xs text-slate-400 capitalize">{user?.role?.toLowerCase()}</p>
            </div>
          </div>
          <button
            onClick={handleLogout}
            className="w-full px-4 py-2 text-sm font-medium bg-slate-700 hover:bg-slate-600 rounded-lg transition-colors text-white"
          >
            Logout
          </button>
        </div>
      </aside>

      {/* Main Content */}
      <main className="flex-1 flex flex-col overflow-auto">
        {/* Top Bar */}
        <header className="bg-white border-b border-slate-200 sticky top-0 z-20">
          <div className="flex items-center justify-between px-4 md:px-8 py-4">
            <div className="flex items-center gap-4">
              <button
                onClick={() => setSidebarOpen(!sidebarOpen)}
                className="md:hidden p-2 hover:bg-slate-100 rounded-lg transition-colors"
              >
                {sidebarOpen ? '✕' : '☰'}
              </button>
              <div>
                <h2 className="text-lg font-semibold text-slate-900">
                  {getCurrentPageTitle(location.pathname, user?.role)}
                </h2>
              </div>
            </div>
            <div className="flex items-center gap-4">
              {/* Notification Bell */}
              <div className="relative" ref={notifRef}>
                <button
                  onClick={() => setNotifOpen((o) => !o)}
                  className="relative p-2 hover:bg-slate-100 rounded-lg transition-colors text-slate-700"
                  aria-label="Notifications"
                >
                  <FiBell size={20} />
                  {unreadCount > 0 && (
                    <span className="absolute top-1 right-1 w-4 h-4 bg-red-500 text-white text-xs rounded-full flex items-center justify-center leading-none">
                      {unreadCount > 9 ? '9+' : unreadCount}
                    </span>
                  )}
                </button>

                {/* Notification Dropdown */}
                {notifOpen && (
                  <div className="absolute right-0 mt-2 w-80 bg-white rounded-xl shadow-xl border border-gray-200 z-50 overflow-hidden">
                    <div className="flex items-center justify-between px-4 py-3 border-b border-gray-100">
                      <h3 className="font-semibold text-gray-700 text-sm">Notifications</h3>
                      {unreadCount > 0 && (
                        <button
                          onClick={() => markAllRead()}
                          className="text-xs text-indigo-600 hover:text-indigo-800 font-medium"
                        >
                          Mark all read
                        </button>
                      )}
                    </div>
                    <div className="max-h-72 overflow-y-auto divide-y divide-gray-50">
                      {notifications.length === 0 ? (
                        <p className="text-sm text-gray-400 text-center py-6">No notifications</p>
                      ) : (
                        notifications.slice(0, 20).map((n) => (
                          <div
                            key={n.id}
                            onClick={() => {
                              if (n.status === 'Unread') markRead(n.id);
                              if (n.link) { navigate(n.link); setNotifOpen(false); }
                            }}
                            className={`px-4 py-3 cursor-pointer hover:bg-gray-50 transition-colors ${n.status === 'Unread' ? 'bg-indigo-50' : ''}`}
                          >
                            <p className="text-sm font-medium text-gray-800 truncate">{n.title}</p>
                            <p className="text-xs text-gray-500 mt-0.5 truncate">{n.message}</p>
                            <p className="text-xs text-gray-400 mt-1">
                              {new Date(n.created_at).toLocaleDateString('en-US', { month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit' })}
                            </p>
                          </div>
                        ))
                      )}
                    </div>
                  </div>
                )}
              </div>
              <div className="relative">
                <button 
                  onClick={() => setSettingsMenuOpen(!settingsMenuOpen)}
                  className="p-2 hover:bg-slate-100 rounded-lg transition-colors text-slate-700"
                >
                  <FiSettings size={20} />
                </button>
                
                {/* Settings Dropdown */}
                {settingsMenuOpen && (
                  <div className="absolute right-0 mt-2 w-48 bg-white rounded-lg shadow-lg border border-gray-200 py-2 z-50">
                    <button
                      onClick={handleSettingsClick}
                      className="w-full px-4 py-2 text-left text-gray-700 hover:bg-gray-100 flex items-center gap-2 transition-colors"
                    >
                      <FiSettings size={16} />
                      Account Settings
                    </button>
                    <div className="border-t border-gray-200 my-2"></div>
                    <button
                      onClick={handleLogout}
                      className="w-full px-4 py-2 text-left text-red-600 hover:bg-red-50 flex items-center gap-2 transition-colors"
                    >
                      <FiLogOut size={16} />
                      Logout
                    </button>
                  </div>
                )}
              </div>
            </div>
          </div>
        </header>

        {/* Page Content */}
        <div className="flex-1 p-4 md:p-8 overflow-auto">
          <div className="max-w-7xl mx-auto">
            {children}
          </div>
        </div>
      </main>
    </div>
  );
}

function getNavItems(role) {
  switch (role) {
    case 'Student':
      return [
        { path: '/student/dashboard', label: 'Dashboard', icon: '📊' },
        { path: '/student/assessments', label: 'Assessments', icon: '📋' },
        { path: '/student/tasks/recommended', label: 'Recommended Tasks', icon: '🎯' },
        { path: '/student/tasks/my-tasks', label: 'My Tasks', icon: '✅' },
        { path: '/student/portfolio', label: 'Portfolio', icon: '🎨' },
        { path: '/student/analytics', label: 'Analytics', icon: '📈' },
        { path: '/student/chat', label: 'AI Chat', icon: '🤖' },
        { path: '/student/announcements', label: 'Announcements', icon: '📢' },
        { path: '/student/mentor-chat', label: 'Mentor Chat', icon: '💬' },
      ];
    case 'Mentor':
      return [
        { path: '/mentor/dashboard', label: 'Dashboard', icon: '📊' },
        { path: '/mentor/students', label: 'My Students', icon: '👥' },
        { path: '/mentor/select-students', label: 'Select Students', icon: '➕' },
        { path: '/mentor/tasks', label: 'My Tasks', icon: '📝' },
        { path: '/mentor/reviews', label: 'Reviews', icon: '📋' },
        { path: '/mentor/analytics', label: 'Analytics', icon: '📈' },
        { path: '/mentor/chat', label: 'AI Assistant', icon: '🤖' },
        { path: '/mentor/announcements', label: 'Announcements', icon: '📢' },
      ];
    case 'Admin':
      return [
        { path: '/admin/dashboard', label: 'Dashboard', icon: '📊' },
        { path: '/admin/analytics', label: 'Analytics', icon: '📈' },
        { path: '/admin/announcements', label: 'Announcements', icon: '📢' },
      ];
    default:
      return [];
  }
}

function getCurrentPageTitle(pathname, role) {
  const allItems = [
    ...getNavItems('Student'),
    ...getNavItems('Mentor'),
    ...getNavItems('Admin'),
  ];
  // Dynamic route match
  if (pathname.match(/\/mentor\/students\/\d+\/chat/)) return '💬 Direct Chat';
  const match = allItems.find(
    (item) => pathname === item.path || pathname.startsWith(item.path + '/')
  );
  if (match) return `${match.icon} ${match.label}`;
  if (role === 'Student') return '📚 Student Dashboard';
  if (role === 'Mentor') return '👨‍🏫 Mentor Dashboard';
  if (role === 'Admin') return '⚙️ Admin Dashboard';
  return 'Dashboard';
}
