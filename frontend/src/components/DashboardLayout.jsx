import { NavLink, useNavigate, useLocation } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import { useState } from 'react';

export default function DashboardLayout({ children }) {
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();
  const [sidebarOpen, setSidebarOpen] = useState(true);

  const handleLogout = async () => {
    await logout();
    navigate('/login');
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
                  {user?.role === 'Student' && '📚 Student Dashboard'}
                  {user?.role === 'Mentor' && '👨‍🏫 Mentor Dashboard'}
                  {user?.role === 'Admin' && '⚙️ Admin Dashboard'}
                </h2>
              </div>
            </div>
            <div className="flex items-center gap-4">
              <button className="p-2 hover:bg-slate-100 rounded-lg transition-colors text-slate-700">
                🔔
              </button>
              <button className="p-2 hover:bg-slate-100 rounded-lg transition-colors text-slate-700">
                ⚙️
              </button>
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
        { path: '/assessments', label: 'Assessments', icon: '📋' },
        { path: '/tasks/recommended', label: 'Recommended', icon: '🎯' },
        { path: '/portfolio', label: 'Portfolio', icon: '🎨' },
        { path: '/chat', label: 'Chat AI', icon: '💬' },
      ];
    case 'Mentor':
      return [
        { path: '/mentor/dashboard', label: 'Dashboard', icon: '📊' },
        { path: '/mentor/students', label: 'Students', icon: '👥' },
        { path: '/mentor/assessments', label: 'Assessments', icon: '📋' },
        { path: '/mentor/reviews', label: 'Reviews', icon: '✓' },
      ];
    case 'Admin':
      return [
        { path: '/admin/dashboard', label: 'Dashboard', icon: '📊' },
        { path: '/admin/users', label: 'Users', icon: '👥' },
        { path: '/admin/assessments', label: 'Assessments', icon: '📋' },
        { path: '/admin/tasks', label: 'Tasks', icon: '🎯' },
        { path: '/admin/reports', label: 'Reports', icon: '📈' },
      ];
    default:
      return [];
  }
}
