import { useState, useEffect, useCallback } from 'react';
import DashboardLayout from '../components/DashboardLayout';
import { adminService } from '../services/endpoints';
import { Badge } from '../components/CardComponents';
import ConfirmModal from '../components/ConfirmModal';
import { toast } from 'react-toastify';

const DIFF_COLORS = { Beginner: 'success', Intermediate: 'warning', Advanced: 'error' };

export default function AdminTasksPage() {
  const [tasks, setTasks] = useState([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState('');
  const [domainFilter, setDomainFilter] = useState('');
  const [statusFilter, setStatusFilter] = useState('');
  const [confirmModal, setConfirmModal] = useState(null);

  const load = useCallback(async () => {
    setLoading(true);
    try {
      const res = await adminService.getTasks();
      setTasks(res.data.data || []);
    } catch {
      toast.error('Failed to load tasks');
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => { load(); }, [load]);

  const domains = [...new Set(tasks.map((t) => t.domain).filter(Boolean))].sort();

  const filtered = tasks.filter((t) => {
    const q = search.toLowerCase();
    const matchSearch = !q || t.title?.toLowerCase().includes(q) || t.domain?.toLowerCase().includes(q);
    const matchDomain = !domainFilter || t.domain === domainFilter;
    const matchStatus = !statusFilter || (statusFilter === 'active' ? t.is_active : !t.is_active);
    return matchSearch && matchDomain && matchStatus;
  });

  const handleToggle = (task) => {
    setConfirmModal({
      title: `${task.is_active ? 'Deactivate' : 'Activate'} Task`,
      message: `${task.is_active ? 'Deactivate' : 'Activate'} "${task.title}"?`,
      danger: task.is_active,
      confirmLabel: task.is_active ? 'Deactivate' : 'Activate',
      onConfirm: async () => {
        await adminService.toggleTask(task.id);
        toast.success(`Task ${task.is_active ? 'deactivated' : 'activated'}`);
        load();
      },
    });
  };

  const activeTasks = tasks.filter((t) => t.is_active).length;
  const totalAssignments = tasks.reduce((s, t) => s + (t.assignment_count || 0), 0);
  const totalCompleted = tasks.reduce((s, t) => s + (t.completed_count || 0), 0);

  return (
    <DashboardLayout>
      <div className="mb-6">
        <h1 className="text-2xl font-bold text-slate-900">🎯 Task Management</h1>
        <p className="text-slate-500 text-sm mt-1">View and manage all learning tasks on the platform</p>
      </div>

      {/* Stats row */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
        {[
          { label: 'Total Tasks', value: tasks.length, icon: '📋', color: 'blue' },
          { label: 'Active', value: activeTasks, icon: '✅', color: 'green' },
          { label: 'Total Assignments', value: totalAssignments, icon: '📌', color: 'purple' },
          { label: 'Completed', value: totalCompleted, icon: '🏆', color: 'orange' },
        ].map((s) => (
          <div key={s.label} className="bg-white rounded-xl border border-slate-200 shadow-sm p-4 flex items-center gap-3">
            <div className="text-2xl">{s.icon}</div>
            <div>
              <p className="text-xs text-slate-500 font-medium">{s.label}</p>
              <p className="text-xl font-bold text-slate-900">{s.value}</p>
            </div>
          </div>
        ))}
      </div>

      {/* Filters */}
      <div className="flex flex-col sm:flex-row gap-3 mb-5">
        <input value={search} onChange={(e) => setSearch(e.target.value)}
          placeholder="Search by title or domain..."
          className="flex-1 border border-slate-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500" />
        <select value={domainFilter} onChange={(e) => setDomainFilter(e.target.value)}
          className="border border-slate-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500">
          <option value="">All Domains</option>
          {domains.map((d) => <option key={d}>{d}</option>)}
        </select>
        <select value={statusFilter} onChange={(e) => setStatusFilter(e.target.value)}
          className="border border-slate-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500">
          <option value="">All Statuses</option>
          <option value="active">Active</option>
          <option value="inactive">Inactive</option>
        </select>
      </div>

      {/* Table */}
      <div className="bg-white rounded-xl border border-slate-200 shadow-sm overflow-hidden">
        {loading ? (
          <div className="flex justify-center items-center py-16">
            <div className="w-8 h-8 border-2 border-blue-600 border-t-transparent rounded-full animate-spin" />
          </div>
        ) : filtered.length === 0 ? (
          <div className="text-center py-16 text-slate-500">No tasks found.</div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="bg-slate-50 border-b border-slate-200">
                  <th className="text-left px-4 py-3 font-semibold text-slate-600">Title</th>
                  <th className="text-left px-4 py-3 font-semibold text-slate-600">Domain</th>
                  <th className="text-left px-4 py-3 font-semibold text-slate-600">Difficulty</th>
                  <th className="text-left px-4 py-3 font-semibold text-slate-600">Est. Hours</th>
                  <th className="text-left px-4 py-3 font-semibold text-slate-600">Assignments</th>
                  <th className="text-left px-4 py-3 font-semibold text-slate-600">Completed</th>
                  <th className="text-left px-4 py-3 font-semibold text-slate-600">Status</th>
                  <th className="text-right px-4 py-3 font-semibold text-slate-600">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100">
                {filtered.map((t) => (
                  <tr key={t.id} className="hover:bg-slate-50 transition">
                    <td className="px-4 py-3 font-medium text-slate-900 max-w-xs truncate">{t.title}</td>
                    <td className="px-4 py-3"><Badge text={t.domain} status="info" size="sm" /></td>
                    <td className="px-4 py-3">
                      <Badge text={t.difficulty} status={DIFF_COLORS[t.difficulty] || 'default'} size="sm" />
                    </td>
                    <td className="px-4 py-3 text-slate-500">{t.estimated_duration ? `${t.estimated_duration} min` : '—'}</td>
                    <td className="px-4 py-3 text-slate-600">{t.assignment_count || 0}</td>
                    <td className="px-4 py-3 text-slate-600">{t.completed_count || 0}</td>
                    <td className="px-4 py-3">
                      <Badge text={t.is_active ? 'Active' : 'Inactive'} status={t.is_active ? 'success' : 'error'} size="sm" />
                    </td>
                    <td className="px-4 py-3">
                      <div className="flex items-center justify-end">
                        <button onClick={() => handleToggle(t)}
                          title={t.is_active ? 'Deactivate' : 'Activate'}
                          className="p-1.5 text-slate-500 hover:text-yellow-600 hover:bg-yellow-50 rounded transition text-base">
                          {t.is_active ? '🔒' : '🔓'}
                        </button>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>

      <div className="mt-3 text-xs text-slate-400 text-right">
        Showing {filtered.length} of {tasks.length} tasks
      </div>

      <ConfirmModal config={confirmModal} onClose={() => setConfirmModal(null)} />
    </DashboardLayout>
  );
}
