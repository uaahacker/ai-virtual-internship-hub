import { useState, useEffect, useCallback } from 'react';
import DashboardLayout from '../components/DashboardLayout';
import { adminService } from '../services/endpoints';
import { Badge } from '../components/CardComponents';
import ConfirmModal from '../components/ConfirmModal';
import { toast } from 'react-toastify';

const ROLES = ['Student', 'Mentor', 'Admin'];
const STATUSES = ['Active', 'Inactive'];
const DOMAINS = [
  'Graphic Design', 'Content Writing', 'Programming', 'Freelancing',
  'E-Commerce', 'QuickBooks', 'AutoCAD', 'Data Analytics', 'Digital Marketing', 'WordPress',
];

const ROLE_COLORS = { Student: 'info', Mentor: 'success', Admin: 'primary' };
const STATUS_COLORS = { Active: 'success', Inactive: 'error' };

function UserModal({ user, onClose, onSave }) {
  const isEdit = !!user?.id;
  const [form, setForm] = useState({
    name: user?.name || '',
    email: user?.email || '',
    role: user?.role || 'Student',
    status: user?.status || 'Active',
    password: '',
  });
  const [saving, setSaving] = useState(false);

  const handle = (e) => setForm((p) => ({ ...p, [e.target.name]: e.target.value }));

  const submit = async (e) => {
    e.preventDefault();
    setSaving(true);
    try {
      if (isEdit) {
        const payload = { name: form.name, email: form.email, role: form.role, status: form.status };
        await adminService.updateUser(user.id, payload);
        toast.success('User updated successfully');
      } else {
        await adminService.createUser(form);
        toast.success('User created successfully');
      }
      onSave();
      onClose();
    } catch (err) {
      toast.error(err.response?.data?.error?.message || 'Failed to save user');
    } finally {
      setSaving(false);
    }
  };

  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-xl shadow-xl w-full max-w-md">
        <div className="flex items-center justify-between px-6 py-4 border-b border-slate-200">
          <h2 className="text-lg font-bold text-slate-900">{isEdit ? 'Edit User' : 'Create New User'}</h2>
          <button onClick={onClose} className="text-slate-400 hover:text-slate-600 text-xl leading-none">✕</button>
        </div>
        <form onSubmit={submit} className="p-6 space-y-4">
          <div>
            <label className="block text-sm font-medium text-slate-700 mb-1">Full Name *</label>
            <input name="name" value={form.name} onChange={handle} required
              className="w-full border border-slate-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500" />
          </div>
          <div>
            <label className="block text-sm font-medium text-slate-700 mb-1">Email *</label>
            <input name="email" type="email" value={form.email} onChange={handle} required
              className="w-full border border-slate-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500" />
          </div>
          {!isEdit && (
            <div>
              <label className="block text-sm font-medium text-slate-700 mb-1">Password *</label>
              <input name="password" type="password" value={form.password} onChange={handle} required minLength={8}
                className="w-full border border-slate-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
                placeholder="Min 8 characters" />
            </div>
          )}
          <div className="grid grid-cols-2 gap-3">
            <div>
              <label className="block text-sm font-medium text-slate-700 mb-1">Role *</label>
              <select name="role" value={form.role} onChange={handle}
                className="w-full border border-slate-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500">
                {ROLES.map((r) => <option key={r}>{r}</option>)}
              </select>
            </div>
            <div>
              <label className="block text-sm font-medium text-slate-700 mb-1">Status</label>
              <select name="status" value={form.status} onChange={handle}
                className="w-full border border-slate-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500">
                {STATUSES.map((s) => <option key={s}>{s}</option>)}
              </select>
            </div>
          </div>
          <div className="flex gap-3 pt-2">
            <button type="button" onClick={onClose}
              className="flex-1 px-4 py-2 border border-slate-300 rounded-lg text-sm font-medium hover:bg-slate-50 transition">
              Cancel
            </button>
            <button type="submit" disabled={saving}
              className="flex-1 px-4 py-2 bg-blue-600 text-white rounded-lg text-sm font-medium hover:bg-blue-700 transition disabled:opacity-50">
              {saving ? 'Saving...' : isEdit ? 'Save Changes' : 'Create User'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}

function ResetPasswordModal({ user, onClose }) {
  const [password, setPassword] = useState('');
  const [saving, setSaving] = useState(false);

  const submit = async (e) => {
    e.preventDefault();
    setSaving(true);
    try {
      await adminService.resetPassword(user.id, password);
      toast.success(`Password reset for ${user.name}`);
      onClose();
    } catch (err) {
      toast.error(err.response?.data?.error?.message || 'Failed to reset password');
    } finally {
      setSaving(false);
    }
  };

  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-xl shadow-xl w-full max-w-sm">
        <div className="flex items-center justify-between px-6 py-4 border-b border-slate-200">
          <h2 className="text-lg font-bold text-slate-900">Reset Password</h2>
          <button onClick={onClose} className="text-slate-400 hover:text-slate-600 text-xl leading-none">✕</button>
        </div>
        <form onSubmit={submit} className="p-6 space-y-4">
          <p className="text-sm text-slate-600">Setting new password for <strong>{user.name}</strong> ({user.email})</p>
          <div>
            <label className="block text-sm font-medium text-slate-700 mb-1">New Password *</label>
            <input type="password" value={password} onChange={(e) => setPassword(e.target.value)}
              required minLength={8} placeholder="Min 8 characters"
              className="w-full border border-slate-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500" />
          </div>
          <div className="flex gap-3">
            <button type="button" onClick={onClose}
              className="flex-1 px-4 py-2 border border-slate-300 rounded-lg text-sm font-medium hover:bg-slate-50 transition">Cancel</button>
            <button type="submit" disabled={saving}
              className="flex-1 px-4 py-2 bg-orange-600 text-white rounded-lg text-sm font-medium hover:bg-orange-700 transition disabled:opacity-50">
              {saving ? 'Resetting...' : 'Reset Password'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}

export default function AdminUsersPage() {
  const [users, setUsers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState('');
  const [roleFilter, setRoleFilter] = useState('');
  const [statusFilter, setStatusFilter] = useState('');
  const [userModal, setUserModal] = useState(null);   // null | { id?, name, email, role, status }
  const [resetModal, setResetModal] = useState(null); // null | user object
  const [confirmModal, setConfirmModal] = useState(null);

  const load = useCallback(async () => {
    setLoading(true);
    try {
      const res = await adminService.getUsers();
      setUsers(res.data.data || []);
    } catch {
      toast.error('Failed to load users');
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => { load(); }, [load]);

  const filtered = users.filter((u) => {
    const q = search.toLowerCase();
    const matchSearch = !q || u.name?.toLowerCase().includes(q) || u.email?.toLowerCase().includes(q);
    const matchRole = !roleFilter || u.role === roleFilter;
    const matchStatus = !statusFilter || u.status === statusFilter;
    return matchSearch && matchRole && matchStatus;
  });

  const handleToggleStatus = (user) => {
    const next = user.status === 'Active' ? 'Inactive' : 'Active';
    setConfirmModal({
      title: `${next === 'Active' ? 'Activate' : 'Deactivate'} User`,
      message: `Are you sure you want to ${next === 'Active' ? 'activate' : 'deactivate'} ${user.name}?`,
      danger: next === 'Inactive',
      confirmLabel: next === 'Active' ? 'Activate' : 'Deactivate',
      onConfirm: async () => {
        await adminService.updateUser(user.id, { status: next });
        toast.success(`User ${next === 'Active' ? 'activated' : 'deactivated'}`);
        load();
      },
    });
  };

  const handleDelete = (user) => {
    setConfirmModal({
      title: 'Delete User',
      message: `Permanently delete ${user.name} (${user.email})? This cannot be undone.`,
      danger: true,
      confirmLabel: 'Delete',
      onConfirm: async () => {
        await adminService.deleteUser(user.id);
        toast.success('User deleted');
        load();
      },
    });
  };

  return (
    <DashboardLayout>
      <div className="mb-6 flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-slate-900">👥 User Management</h1>
          <p className="text-slate-500 text-sm mt-1">{users.length} total users</p>
        </div>
        <button onClick={() => setUserModal({})}
          className="shrink-0 px-4 py-2 bg-blue-600 text-white rounded-lg text-sm font-medium hover:bg-blue-700 transition">
          + Create User
        </button>
      </div>

      {/* Filters */}
      <div className="flex flex-col sm:flex-row gap-3 mb-5">
        <input value={search} onChange={(e) => setSearch(e.target.value)}
          placeholder="Search name or email..."
          className="flex-1 border border-slate-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500" />
        <select value={roleFilter} onChange={(e) => setRoleFilter(e.target.value)}
          className="border border-slate-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500">
          <option value="">All Roles</option>
          {ROLES.map((r) => <option key={r}>{r}</option>)}
        </select>
        <select value={statusFilter} onChange={(e) => setStatusFilter(e.target.value)}
          className="border border-slate-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500">
          <option value="">All Statuses</option>
          {STATUSES.map((s) => <option key={s}>{s}</option>)}
        </select>
      </div>

      {/* Table */}
      <div className="bg-white rounded-xl border border-slate-200 shadow-sm overflow-hidden">
        {loading ? (
          <div className="flex justify-center items-center py-16">
            <div className="w-8 h-8 border-2 border-blue-600 border-t-transparent rounded-full animate-spin" />
          </div>
        ) : filtered.length === 0 ? (
          <div className="text-center py-16 text-slate-500">No users found.</div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="bg-slate-50 border-b border-slate-200">
                  <th className="text-left px-4 py-3 font-semibold text-slate-600">Name</th>
                  <th className="text-left px-4 py-3 font-semibold text-slate-600">Email</th>
                  <th className="text-left px-4 py-3 font-semibold text-slate-600">Role</th>
                  <th className="text-left px-4 py-3 font-semibold text-slate-600">Status</th>
                  <th className="text-left px-4 py-3 font-semibold text-slate-600">Joined</th>
                  <th className="text-right px-4 py-3 font-semibold text-slate-600">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100">
                {filtered.map((u) => (
                  <tr key={u.id} className="hover:bg-slate-50 transition">
                    <td className="px-4 py-3 font-medium text-slate-900">{u.name}</td>
                    <td className="px-4 py-3 text-slate-600">{u.email}</td>
                    <td className="px-4 py-3"><Badge text={u.role} status={ROLE_COLORS[u.role] || 'default'} size="sm" /></td>
                    <td className="px-4 py-3"><Badge text={u.status} status={STATUS_COLORS[u.status] || 'default'} size="sm" /></td>
                    <td className="px-4 py-3 text-slate-500">{u.created_at ? new Date(u.created_at).toLocaleDateString() : '—'}</td>
                    <td className="px-4 py-3">
                      <div className="flex items-center justify-end gap-1">
                        <button onClick={() => setUserModal(u)} title="Edit"
                          className="p-1.5 text-slate-500 hover:text-blue-600 hover:bg-blue-50 rounded transition text-base">✏️</button>
                        <button onClick={() => setResetModal(u)} title="Reset Password"
                          className="p-1.5 text-slate-500 hover:text-orange-600 hover:bg-orange-50 rounded transition text-base">🔑</button>
                        <button onClick={() => handleToggleStatus(u)} title={u.status === 'Active' ? 'Deactivate' : 'Activate'}
                          className="p-1.5 text-slate-500 hover:text-yellow-600 hover:bg-yellow-50 rounded transition text-base">
                          {u.status === 'Active' ? '🔒' : '🔓'}
                        </button>
                        <button onClick={() => handleDelete(u)} title="Delete"
                          className="p-1.5 text-slate-500 hover:text-red-600 hover:bg-red-50 rounded transition text-base">🗑️</button>
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
        Showing {filtered.length} of {users.length} users
      </div>

      {userModal !== null && (
        <UserModal user={userModal} onClose={() => setUserModal(null)} onSave={load} />
      )}
      {resetModal && (
        <ResetPasswordModal user={resetModal} onClose={() => setResetModal(null)} />
      )}
      <ConfirmModal config={confirmModal} onClose={() => setConfirmModal(null)} />
    </DashboardLayout>
  );
}
