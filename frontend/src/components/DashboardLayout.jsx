import { NavLink, useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import { FiHome, FiClipboard, FiSettings, FiLogOut, FiUser } from 'react-icons/fi';

export default function DashboardLayout({ children }) {
  const { user, logout } = useAuth();
  const navigate = useNavigate();

  const handleLogout = async () => {
    await logout();
    navigate('/login');
  };

  const navItems = getNavItems(user?.role);

  return (
    <div className="flex min-h-screen bg-gray-50">
      {/* Sidebar */}
      <aside className="w-64 bg-white shadow-lg flex flex-col">
        {/* Logo */}
        <div className="p-6 border-b">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 bg-primary-600 rounded-lg flex items-center justify-center">
              <span className="text-white font-bold text-sm">VIH</span>
            </div>
            <div>
              <h1 className="font-bold text-sm text-gray-800 leading-tight">AI-Supported</h1>
              <p className="text-xs text-gray-500">Virtual Internship Hub</p>
            </div>
          </div>
        </div>

        {/* Navigation */}
        <nav className="flex-1 py-4 px-3 space-y-1">
          {navItems.map((item) => (
            <NavLink
              key={item.path}
              to={item.path}
              className={({ isActive }) =>
                `flex items-center gap-3 px-4 py-3 rounded-lg text-sm font-medium transition-colors ${
                  isActive
                    ? 'bg-primary-600 text-white shadow-md'
                    : 'text-gray-600 hover:bg-primary-50 hover:text-primary-700'
                }`
              }
            >
              <item.icon size={18} />
              {item.label}
            </NavLink>
          ))}
        </nav>

        {/* User info + Logout */}
        <div className="p-4 border-t">
          <div className="flex items-center gap-3 mb-3">
            <div className="w-9 h-9 bg-primary-100 rounded-full flex items-center justify-center">
              <FiUser className="text-primary-600" size={16} />
            </div>
            <div className="flex-1 min-w-0">
              <p className="text-sm font-medium text-gray-800 truncate">{user?.name}</p>
              <p className="text-xs text-gray-500">{user?.role}</p>
            </div>
          </div>
          <button
            onClick={handleLogout}
            className="flex items-center gap-2 w-full px-4 py-2 text-sm text-red-600 hover:bg-red-50 rounded-lg transition-colors"
          >
            <FiLogOut size={16} />
            Logout
          </button>
        </div>
      </aside>

      {/* Main content area */}
      <main className="flex-1 overflow-auto">
        {/* Top bar */}
        <header className="bg-white shadow-sm px-8 py-4 flex items-center justify-between">
          <div />
          <div className="flex items-center gap-4">
            <span className="text-sm text-gray-500">
              {user?.role} Dashboard
            </span>
            <div className="w-9 h-9 bg-primary-600 rounded-full flex items-center justify-center">
              <span className="text-white text-sm font-medium">
                {user?.name?.charAt(0)?.toUpperCase()}
              </span>
            </div>
          </div>
        </header>

        {/* Page content */}
        <div className="p-8">
          {children}
        </div>
      </main>
    </div>
  );
}

function getNavItems(role) {
  switch (role) {
    case 'Student':
      return [
        { path: '/student/dashboard', label: 'Dashboard', icon: FiHome },
        { path: '/student/assessments', label: 'Assessments', icon: FiClipboard },
        { path: '/student/dashboard', label: 'Settings', icon: FiSettings },
      ];
    case 'Mentor':
      return [
        { path: '/mentor/dashboard', label: 'Dashboard', icon: FiHome },
        { path: '/mentor/dashboard', label: 'Settings', icon: FiSettings },
      ];
    case 'Admin':
      return [
        { path: '/admin/dashboard', label: 'Dashboard', icon: FiHome },
        { path: '/admin/dashboard', label: 'Settings', icon: FiSettings },
      ];
    default:
      return [];
  }
}
