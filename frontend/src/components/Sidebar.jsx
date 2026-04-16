import React, { useState } from 'react';
import { Link, useLocation } from 'react-router-dom';

const Sidebar = ({ userRole = 'student' }) => {
  const [isOpen, setIsOpen] = useState(true);
  const location = useLocation();

  const navigationItems = {
    student: [
      { label: 'Dashboard', path: '/student/dashboard', icon: '📊' },
      { label: 'Assessments', path: '/assessments', icon: '📋' },
      { label: 'Recommended Tasks', path: '/tasks/recommended', icon: '🎯' },
      { label: 'My Tasks', path: '/tasks/my-tasks', icon: '✓' },
      { label: 'Portfolio', path: '/portfolio', icon: '🎨' },
      { label: 'Chat with AI', path: '/chat', icon: '💬' },
    ],
    mentor: [
      { label: 'Dashboard', path: '/mentor/dashboard', icon: '📊' },
      { label: 'Students', path: '/mentor/students', icon: '👥' },
      { label: 'Assessments', path: '/mentor/assessments', icon: '📋' },
      { label: 'Task Reviews', path: '/mentor/reviews', icon: '✓' },
      { label: 'Analytics', path: '/mentor/analytics', icon: '📈' },
    ],
    admin: [
      { label: 'Dashboard', path: '/admin/dashboard', icon: '📊' },
      { label: 'Users', path: '/admin/users', icon: '👥' },
      { label: 'Assessments', path: '/admin/assessments', icon: '📋' },
      { label: 'Tasks', path: '/admin/tasks', icon: '🎯' },
      { label: 'Reports', path: '/admin/reports', icon: '📈' },
      { label: 'Settings', path: '/admin/settings', icon: '⚙️' },
    ],
  };

  const items = navigationItems[userRole] || navigationItems.student;
  const isActive = (path) => location.pathname === path;

  return (
    <>
      {/* Mobile Menu Button */}
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="fixed top-4 left-4 z-50 md:hidden bg-white p-2 rounded-lg shadow-md"
      >
        {isOpen ? '✕' : '☰'}
      </button>

      {/* Sidebar */}
      <aside
        className={`fixed left-0 top-0 h-screen w-64 bg-gradient-to-b from-slate-900 to-slate-800 text-white transition-transform duration-300 ease-in-out ${
          isOpen ? 'translate-x-0' : '-translate-x-full'
        } md:translate-x-0 md:relative z-40`}
      >
        {/* Logo Section */}
        <div className="p-6 border-b border-slate-700">
          <h1 className="text-2xl font-bold">🎓 Hub</h1>
          <p className="text-xs text-slate-400 mt-1">Career Development</p>
        </div>

        {/* Navigation */}
        <nav className="p-4 space-y-2">
          {items.map((item) => (
            <Link
              key={item.path}
              to={item.path}
              onClick={() => setIsOpen(false)}
              className={`flex items-center gap-3 px-4 py-3 rounded-lg transition-all duration-200 ${
                isActive(item.path)
                  ? 'bg-blue-600 text-white shadow-md'
                  : 'text-slate-300 hover:bg-slate-700 hover:text-white'
              }`}
            >
              <span className="text-lg">{item.icon}</span>
              <span className="font-medium text-sm">{item.label}</span>
            </Link>
          ))}
        </nav>

        {/* Bottom Section */}
        <div className="absolute bottom-0 left-0 right-0 p-4 border-t border-slate-700">
          <button className="w-full py-2 px-4 bg-slate-700 hover:bg-slate-600 rounded-lg text-sm font-medium transition-colors">
            Logout
          </button>
        </div>
      </aside>

      {/* Mobile Overlay */}
      {isOpen && (
        <div
          className="fixed inset-0 bg-black bg-opacity-50 md:hidden z-30"
          onClick={() => setIsOpen(false)}
        />
      )}
    </>
  );
};

export default Sidebar;
