import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import DashboardLayout from '../components/DashboardLayout';
import { adminService } from '../services/endpoints';
import { toast } from 'react-toastify';
import ConfirmModal from '../components/ConfirmModal';
import { Badge } from '../components/CardComponents';

function StatCard({ icon, label, value, sub, color = 'blue' }) {
  const colorMap = {
    blue: 'from-blue-50 to-blue-100 border-blue-200 text-blue-700',
    green: 'from-green-50 to-green-100 border-green-200 text-green-700',
    purple: 'from-purple-50 to-purple-100 border-purple-200 text-purple-700',
    orange: 'from-orange-50 to-orange-100 border-orange-200 text-orange-700',
    red: 'from-red-50 to-red-100 border-red-200 text-red-700',
    slate: 'from-slate-50 to-slate-100 border-slate-200 text-slate-700',
  };
  return (
    <div className={`bg-gradient-to-br ${colorMap[color]} border rounded-xl p-5`}>
      <div className="flex items-start justify-between">
        <div>
          <p className="text-xs font-semibold uppercase tracking-wide opacity-70">{label}</p>
          <p className="text-3xl font-bold mt-1">{value ?? '—'}</p>
          {sub && <p className="text-xs mt-1 opacity-70">{sub}</p>}
        </div>
        <span className="text-3xl">{icon}</span>
      </div>
    </div>
  );
}

function QuickAction({ icon, title, desc, to, color }) {
  const colorMap = {
    blue: 'bg-blue-600 hover:bg-blue-700',
    green: 'bg-green-600 hover:bg-green-700',
    purple: 'bg-purple-600 hover:bg-purple-700',
    orange: 'bg-orange-600 hover:bg-orange-700',
    slate: 'bg-slate-600 hover:bg-slate-700',
  };
  return (
    <Link to={to}
      className="flex items-center gap-4 p-4 bg-white rounded-xl border border-slate-200 shadow-sm hover:shadow-md transition group">
      <div className={`w-10 h-10 rounded-lg ${colorMap[color]} flex items-center justify-center text-white text-lg shrink-0`}>
        {icon}
      </div>
      <div className="min-w-0">
        <p className="font-semibold text-slate-900 text-sm group-hover:text-blue-600 transition">{title}</p>
        <p className="text-xs text-slate-500 truncate">{desc}</p>
      </div>
      <span className="ml-auto text-slate-300 group-hover:text-blue-400 transition">→</span>
    </Link>
  );
}

const ROLE_COLORS = { Student: 'info', Mentor: 'success', Admin: 'primary' };

export default function AdminDashboard() {
  const [stats, setStats] = useState(null);
  const [loadingStats, setLoadingStats] = useState(true);
  const [autoAssigning, setAutoAssigning] = useState(false);
  const [confirmModal, setConfirmModal] = useState(null);

  useEffect(() => {
    adminService.getStats()
      .then((res) => setStats(res.data.data))
      .catch(() => toast.error('Failed to load stats'))
      .finally(() => setLoadingStats(false));
  }, []);

  const handleAutoAssign = () => {
    setConfirmModal({
      title: 'Auto-Assign Mentors',
      message: 'This will automatically assign mentors to all unassigned students based on domain matching. Continue?',
      confirmLabel: 'Run Auto-Assign',
      onConfirm: async () => {
        setAutoAssigning(true);
        try {
          const res = await adminService.autoAssignMentors();
          toast.success(res.data.message || 'Auto-assign complete');
          const s = await adminService.getStats();
          setStats(s.data.data);
        } catch (err) {
          toast.error(err.response?.data?.error?.message || 'Auto-assign failed');
        } finally {
          setAutoAssigning(false);
        }
      },
    });
  };

  const u = stats?.users || {};
  const t = stats?.tasks || {};
  const a = stats?.assessments || {};

  return (
    <DashboardLayout>
      <div className="mb-7">
        <h1 className="text-3xl font-bold text-slate-900">⚙️ Admin Control Center</h1>
        <p className="text-slate-500 mt-1 text-sm">Full platform management — users, assessments, tasks, and system operations</p>
      </div>

      {loadingStats ? (
        <div className="flex justify-center py-12">
          <div className="w-8 h-8 border-2 border-blue-600 border-t-transparent rounded-full animate-spin" />
        </div>
      ) : (
        <>
          <h2 className="text-xs font-semibold text-slate-400 uppercase tracking-wider mb-3">Users</h2>
          <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-4 mb-7">
            <StatCard icon="👥" label="Total" value={u.total} color="blue" />
            <StatCard icon="📚" label="Students" value={u.students}
              sub={`${u.total ? Math.round((u.students / u.total) * 100) : 0}% of total`} color="green" />
            <StatCard icon="👨‍🏫" label="Mentors" value={u.mentors} color="purple" />
            <StatCard icon="🔐" label="Admins" value={u.admins} color="orange" />
            <StatCard icon="✅" label="Active" value={u.active} color="green" />
            <StatCard icon="⚠️" label="Unassigned" value={u.unassigned_students}
              sub="students w/o mentor" color={u.unassigned_students > 0 ? 'red' : 'slate'} />
          </div>

          <h2 className="text-xs font-semibold text-slate-400 uppercase tracking-wider mb-3">Tasks & Assessments</h2>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-8">
            <StatCard icon="🎯" label="Total Tasks" value={t.total} sub={`${t.active} active`} color="blue" />
            <StatCard icon="📌" label="Assignments" value={t.total_assignments} sub={`${t.completed_assignments} completed`} color="green" />
            <StatCard icon="📋" label="Assessments" value={a.total} color="purple" />
            <StatCard icon="📊" label="Attempts" value={a.total_attempts} color="orange" />
          </div>
        </>
      )}

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2 space-y-3">
          <h2 className="text-xs font-semibold text-slate-400 uppercase tracking-wider mb-2">Quick Actions</h2>
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
            <QuickAction icon="👥" title="User Management" desc="Create, edit, delete users & reset passwords" to="/admin/users" color="blue" />
            <QuickAction icon="📋" title="Assessments" desc="Manage assessments and questions" to="/admin/assessments" color="green" />
            <QuickAction icon="🎯" title="Tasks" desc="View all tasks, toggle active status" to="/admin/tasks" color="purple" />
            <QuickAction icon="📈" title="Analytics" desc="Platform-wide performance reports" to="/admin/analytics" color="orange" />
            <QuickAction icon="📢" title="Announcements" desc="Post system-wide announcements" to="/admin/announcements" color="slate" />
          </div>

          <div className="bg-gradient-to-r from-indigo-50 to-blue-50 border border-indigo-200 rounded-xl p-5 mt-4">
            <div className="flex items-start gap-4">
              <div className="text-3xl">🤖</div>
              <div className="flex-1 min-w-0">
                <h3 className="font-bold text-slate-900">Auto-Assign Mentors</h3>
                <p className="text-sm text-slate-600 mt-1">
                  Automatically match {u.unassigned_students ?? '...'} unassigned students to mentors based on domain expertise.
                </p>
              </div>
              <button onClick={handleAutoAssign} disabled={autoAssigning}
                className="shrink-0 px-4 py-2 bg-indigo-600 text-white rounded-lg text-sm font-medium hover:bg-indigo-700 transition disabled:opacity-50">
                {autoAssigning ? 'Running...' : 'Run Now'}
              </button>
            </div>
          </div>
        </div>

        <div>
          <h2 className="text-xs font-semibold text-slate-400 uppercase tracking-wider mb-3">Recent Users</h2>
          <div className="bg-white rounded-xl border border-slate-200 shadow-sm overflow-hidden">
            {loadingStats ? (
              <div className="p-6 text-center text-slate-400 text-sm">Loading...</div>
            ) : (
              <>
                {(stats?.recent_users || []).map((ru) => (
                  <div key={ru.id} className="flex items-center gap-3 px-4 py-3 border-b border-slate-100 last:border-b-0">
                    <div className="w-8 h-8 rounded-full bg-gradient-to-br from-blue-400 to-indigo-600 flex items-center justify-center text-white text-sm font-bold shrink-0">
                      {ru.name?.[0]?.toUpperCase() || '?'}
                    </div>
                    <div className="flex-1 min-w-0">
                      <p className="text-sm font-medium text-slate-900 truncate">{ru.name}</p>
                      <p className="text-xs text-slate-500 truncate">{ru.email}</p>
                    </div>
                    <Badge text={ru.role} status={ROLE_COLORS[ru.role] || 'default'} size="sm" />
                  </div>
                ))}
                <div className="px-4 py-3 text-center">
                  <Link to="/admin/users" className="text-sm text-blue-600 hover:text-blue-700 font-medium">
                    View all users →
                  </Link>
                </div>
              </>
            )}
          </div>
        </div>
      </div>

      <ConfirmModal config={confirmModal} onClose={() => setConfirmModal(null)} />
    </DashboardLayout>
  );
}

