import { useState, useEffect } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import { taskService } from '../services/endpoints';
import DashboardLayout from '../components/DashboardLayout';

const DOMAIN_COLORS = {
  'Graphic Design': 'bg-pink-100 text-pink-700',
  'Content Writing': 'bg-yellow-100 text-yellow-700',
  'Programming': 'bg-blue-100 text-blue-700',
  'Freelancing': 'bg-green-100 text-green-700',
  'E-Commerce': 'bg-orange-100 text-orange-700',
  'QuickBooks': 'bg-teal-100 text-teal-700',
  'AutoCAD': 'bg-red-100 text-red-700',
  'Data Analytics': 'bg-indigo-100 text-indigo-700',
  'Digital Marketing': 'bg-purple-100 text-purple-700',
  'WordPress': 'bg-cyan-100 text-cyan-700',
};

const DIFFICULTY_COLORS = {
  Beginner: 'bg-green-100 text-green-700',
  Intermediate: 'bg-yellow-100 text-yellow-700',
  Advanced: 'bg-red-100 text-red-700',
};

export default function MentorTasksPage() {
  const { user } = useAuth();
  const navigate = useNavigate();
  const [tasks, setTasks] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [deletingId, setDeletingId] = useState(null);
  const [confirmDeleteId, setConfirmDeleteId] = useState(null);
  const [search, setSearch] = useState('');
  const [domainFilter, setDomainFilter] = useState('');

  useEffect(() => {
    if (user?.role !== 'Mentor') { navigate('/'); return; }
    fetchTasks();
  }, [user, navigate]);

  const fetchTasks = async () => {
    try {
      setLoading(true);
      const res = await taskService.getMentorTasks();
      if (res.data.success) setTasks(res.data.data);
      else setError(res.data.error || 'Failed to load tasks');
    } catch (err) {
      setError('Failed to load tasks');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const handleDelete = async (id) => {
    setDeletingId(id);
    try {
      const res = await taskService.deleteTask(id);
      if (res.data.success) {
        setTasks(prev => prev.filter(t => t.id !== id));
        setConfirmDeleteId(null);
      } else {
        setError(res.data.error || 'Delete failed');
      }
    } catch (err) {
      setError('Delete failed');
      console.error(err);
    } finally {
      setDeletingId(null);
    }
  };

  const domains = [...new Set(tasks.map(t => t.domain).filter(Boolean))].sort();
  const filtered = tasks.filter(t => {
    const matchSearch = !search || t.title.toLowerCase().includes(search.toLowerCase()) || t.description?.toLowerCase().includes(search.toLowerCase());
    const matchDomain = !domainFilter || t.domain === domainFilter;
    return matchSearch && matchDomain;
  });

  return (
    <DashboardLayout>
      <div className="max-w-6xl mx-auto pb-10">
        {/* Header */}
        <div className="flex items-center justify-between mb-8">
          <div>
            <h1 className="text-3xl font-bold text-gray-900">My Tasks</h1>
            <p className="text-gray-500 mt-1">Tasks you've created — {tasks.length} total</p>
          </div>
          <Link
            to="/mentor/tasks/create"
            className="px-5 py-2.5 bg-gray-900 text-white font-medium rounded-lg hover:bg-gray-700 transition flex items-center gap-2"
          >
            + Create Task
          </Link>
        </div>

        {error && (
          <div className="mb-6 p-4 bg-red-50 border border-red-200 rounded-lg text-red-700 text-sm">{error}</div>
        )}

        {/* Filters */}
        <div className="flex flex-wrap gap-3 mb-6">
          <input
            type="text"
            placeholder="Search tasks..."
            value={search}
            onChange={e => setSearch(e.target.value)}
            className="px-4 py-2 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-gray-900 w-64"
          />
          <select
            value={domainFilter}
            onChange={e => setDomainFilter(e.target.value)}
            className="px-4 py-2 border border-gray-300 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-gray-900"
          >
            <option value="">All Domains</option>
            {domains.map(d => <option key={d} value={d}>{d}</option>)}
          </select>
          {(search || domainFilter) && (
            <button
              onClick={() => { setSearch(''); setDomainFilter(''); }}
              className="px-4 py-2 text-sm text-gray-600 border border-gray-300 rounded-lg hover:bg-gray-50"
            >
              Clear
            </button>
          )}
        </div>

        {/* Content */}
        {loading ? (
          <div className="flex items-center justify-center py-20">
            <div className="inline-block w-8 h-8 border-4 border-gray-200 border-t-gray-900 rounded-full animate-spin" />
          </div>
        ) : filtered.length === 0 ? (
          <div className="bg-white rounded-xl border border-gray-200 p-12 text-center">
            <div className="text-5xl mb-4">📋</div>
            <p className="text-lg font-semibold text-gray-800 mb-2">
              {tasks.length === 0 ? "You haven't created any tasks yet" : "No tasks match your filters"}
            </p>
            <p className="text-gray-500 text-sm mb-6">
              {tasks.length === 0 ? "Create your first task for students to work on." : "Try a different search or domain filter."}
            </p>
            {tasks.length === 0 && (
              <Link
                to="/mentor/tasks/create"
                className="inline-block px-5 py-2.5 bg-gray-900 text-white font-medium rounded-lg hover:bg-gray-700 transition"
              >
                + Create Task
              </Link>
            )}
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-5">
            {filtered.map(task => (
              <div key={task.id} className="bg-white rounded-xl border border-gray-200 flex flex-col hover:shadow-md transition">
                {/* Card header */}
                <div className="p-5 flex-1">
                  <div className="flex items-start justify-between gap-2 mb-3">
                    <h3 className="font-semibold text-gray-900 text-base leading-snug flex-1">{task.title}</h3>
                    <span className={`flex-shrink-0 px-2.5 py-1 rounded-full text-xs font-medium ${DIFFICULTY_COLORS[task.difficulty] || 'bg-gray-100 text-gray-600'}`}>
                      {task.difficulty}
                    </span>
                  </div>

                  <div className="flex flex-wrap gap-1.5 mb-3">
                    <span className={`px-2.5 py-1 rounded-full text-xs font-medium ${DOMAIN_COLORS[task.domain] || 'bg-gray-100 text-gray-600'}`}>
                      {task.domain}
                    </span>
                    {task.task_type && (
                      <span className="px-2.5 py-1 rounded-full text-xs font-medium bg-gray-100 text-gray-600">
                        {task.task_type}
                      </span>
                    )}
                  </div>

                  <p className="text-sm text-gray-500 line-clamp-2 mb-3">{task.description}</p>

                  {task.required_skills?.length > 0 && (
                    <div className="flex flex-wrap gap-1">
                      {task.required_skills.slice(0, 3).map((s, i) => (
                        <span key={i} className="px-2 py-0.5 bg-gray-50 border border-gray-200 text-gray-600 text-xs rounded">
                          {s}
                        </span>
                      ))}
                      {task.required_skills.length > 3 && (
                        <span className="text-xs text-gray-400">+{task.required_skills.length - 3}</span>
                      )}
                    </div>
                  )}
                </div>

                {/* Card footer */}
                <div className="px-5 py-3 border-t border-gray-100 flex items-center justify-between gap-2">
                  <span className="text-xs text-gray-400">
                    {task.estimated_duration} min · {task.is_active ? '✅ Active' : '⏸ Inactive'}
                  </span>
                  <div className="flex gap-2">
                    <button
                      onClick={() => navigate(`/mentor/tasks/${task.id}/edit`)}
                      className="px-3 py-1.5 text-xs font-medium text-blue-700 bg-blue-50 border border-blue-200 rounded-lg hover:bg-blue-100 transition"
                    >
                      Edit
                    </button>
                    {confirmDeleteId === task.id ? (
                      <div className="flex gap-1">
                        <button
                          onClick={() => handleDelete(task.id)}
                          disabled={deletingId === task.id}
                          className="px-3 py-1.5 text-xs font-medium text-white bg-red-600 rounded-lg hover:bg-red-700 disabled:opacity-50 transition"
                        >
                          {deletingId === task.id ? '...' : 'Confirm'}
                        </button>
                        <button
                          onClick={() => setConfirmDeleteId(null)}
                          className="px-3 py-1.5 text-xs font-medium text-gray-600 bg-gray-100 rounded-lg hover:bg-gray-200 transition"
                        >
                          Cancel
                        </button>
                      </div>
                    ) : (
                      <button
                        onClick={() => setConfirmDeleteId(task.id)}
                        className="px-3 py-1.5 text-xs font-medium text-red-700 bg-red-50 border border-red-200 rounded-lg hover:bg-red-100 transition"
                      >
                        Delete
                      </button>
                    )}
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </DashboardLayout>
  );
}
