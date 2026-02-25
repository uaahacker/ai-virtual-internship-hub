import { useState, useEffect } from 'react';
import DashboardLayout from '../components/DashboardLayout';
import { adminService } from '../services/endpoints';
import { FiUsers, FiShield, FiBookOpen } from 'react-icons/fi';

export default function AdminDashboard() {
  const [users, setUsers] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    adminService.getUsers()
      .then((res) => setUsers(res.data.data || []))
      .catch(() => {})
      .finally(() => setLoading(false));
  }, []);

  const roleBadge = (role) => {
    const colors = {
      Student: 'bg-blue-100 text-blue-700',
      Mentor: 'bg-green-100 text-green-700',
      Admin: 'bg-purple-100 text-purple-700',
    };
    return colors[role] || 'bg-gray-100 text-gray-700';
  };

  const statusBadge = (status) => {
    return status === 'Active'
      ? 'bg-green-100 text-green-700'
      : 'bg-red-100 text-red-700';
  };

  const stats = {
    total: users.length,
    students: users.filter((u) => u.role === 'Student').length,
    mentors: users.filter((u) => u.role === 'Mentor').length,
    admins: users.filter((u) => u.role === 'Admin').length,
  };

  return (
    <DashboardLayout>
      <div className="mb-8">
        <h1 className="text-2xl font-bold text-gray-900">Admin Dashboard</h1>
        <p className="text-gray-500 mt-1">Manage users and monitor platform activity.</p>
      </div>

      {/* Stats cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
        {[
          { label: 'Total Users', value: stats.total, icon: FiUsers, color: 'text-primary-600 bg-primary-100' },
          { label: 'Students', value: stats.students, icon: FiBookOpen, color: 'text-blue-600 bg-blue-100' },
          { label: 'Mentors', value: stats.mentors, icon: FiShield, color: 'text-green-600 bg-green-100' },
          { label: 'Admins', value: stats.admins, icon: FiShield, color: 'text-purple-600 bg-purple-100' },
        ].map((card) => (
          <div key={card.label} className="bg-white rounded-xl shadow-sm p-5 flex items-center gap-4">
            <div className={`w-11 h-11 rounded-lg flex items-center justify-center ${card.color}`}>
              <card.icon size={20} />
            </div>
            <div>
              <p className="text-2xl font-bold text-gray-900">{card.value}</p>
              <p className="text-xs text-gray-500">{card.label}</p>
            </div>
          </div>
        ))}
      </div>

      {/* Users table */}
      <div className="bg-white rounded-xl shadow-sm overflow-hidden">
        <div className="px-6 py-4 border-b">
          <h2 className="text-lg font-semibold text-gray-800">All Users</h2>
        </div>
        {loading ? (
          <div className="text-center py-12 text-gray-400">Loading users...</div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead className="bg-gray-50">
                <tr>
                  <th className="text-left px-6 py-3 text-xs font-semibold text-gray-500 uppercase">#</th>
                  <th className="text-left px-6 py-3 text-xs font-semibold text-gray-500 uppercase">Name</th>
                  <th className="text-left px-6 py-3 text-xs font-semibold text-gray-500 uppercase">Email</th>
                  <th className="text-left px-6 py-3 text-xs font-semibold text-gray-500 uppercase">Role</th>
                  <th className="text-left px-6 py-3 text-xs font-semibold text-gray-500 uppercase">Status</th>
                  <th className="text-left px-6 py-3 text-xs font-semibold text-gray-500 uppercase">Joined</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-100">
                {users.map((u, idx) => (
                  <tr key={u.id} className="hover:bg-gray-50 transition">
                    <td className="px-6 py-3 text-gray-500">{idx + 1}</td>
                    <td className="px-6 py-3 font-medium text-gray-800">{u.name}</td>
                    <td className="px-6 py-3 text-gray-600">{u.email}</td>
                    <td className="px-6 py-3">
                      <span className={`text-xs font-medium px-2.5 py-1 rounded-full ${roleBadge(u.role)}`}>
                        {u.role}
                      </span>
                    </td>
                    <td className="px-6 py-3">
                      <span className={`text-xs font-medium px-2.5 py-1 rounded-full ${statusBadge(u.status)}`}>
                        {u.status}
                      </span>
                    </td>
                    <td className="px-6 py-3 text-gray-500">
                      {new Date(u.created_at).toLocaleDateString()}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </DashboardLayout>
  );
}
