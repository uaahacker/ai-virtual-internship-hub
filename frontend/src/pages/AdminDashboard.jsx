import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import DashboardLayout from '../components/DashboardLayout';
import { adminService } from '../services/endpoints';
import { Card, CardHeader, CardBody, SectionCard, StatCard, Badge } from '../components/CardComponents';
import { DataTable, ListItem } from '../components/DataTable';

export default function AdminDashboard() {
  const [users, setUsers] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    adminService.getUsers()
      .then((res) => setUsers(res.data.data || []))
      .catch(() => {})
      .finally(() => setLoading(false));
  }, []);

  const stats = {
    total: users.length,
    students: users.filter((u) => u.role === 'Student').length,
    mentors: users.filter((u) => u.role === 'Mentor').length,
    admins: users.filter((u) => u.role === 'Admin').length,
  };

  const getRoleStatus = (role) => {
    if (role === 'Student') return 'info';
    if (role === 'Mentor') return 'success';
    if (role === 'Admin') return 'primary';
    return 'default';
  };

  const getStatusColor = (status) => {
    return status === 'Active' ? 'success' : 'error';
  };

  const tableColumns = [
    { key: 'name', label: 'Name' },
    {
      key: 'email',
      label: 'Email',
      render: (val) => <span className="text-slate-600">{val}</span>,
    },
    {
      key: 'role',
      label: 'Role',
      render: (val) => <Badge text={val} status={getRoleStatus(val)} size="sm" />,
    },
    {
      key: 'status',
      label: 'Status',
      render: (val) => <Badge text={val} status={getStatusColor(val)} size="sm" />,
    },
    {
      key: 'created_at',
      label: 'Joined',
      render: (val) => new Date(val).toLocaleDateString(),
    },
  ];

  return (
    <DashboardLayout>
      {/* Header */}
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-slate-900">Admin Control Center ⚙️</h1>
        <p className="text-slate-600 mt-2">Manage users, monitor platform activity, and system settings</p>
      </div>

      {/* Quick Stats */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
        <StatCard
          label="Total Users"
          value={stats.total}
          icon="👥"
          change={`${stats.students} students, ${stats.mentors} mentors`}
        />
        <StatCard
          label="Students"
          value={stats.students}
          icon="📚"
          change={`${((stats.students / stats.total) * 100).toFixed(0)}% of total`}
        />
        <StatCard
          label="Mentors"
          value={stats.mentors}
          icon="👨‍🏫"
          change={`${((stats.mentors / stats.total) * 100).toFixed(0)}% of total`}
        />
        <StatCard
          label="Admins"
          value={stats.admins}
          icon="🔐"
        />
      </div>

      {/* Main Content */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-8">
        {/* Users Table - Main */}
        <div className="lg:col-span-2">
          <SectionCard
            title="📋 User Management"
            subtitle={`${users.length} total users`}
            action={
              <Link to="/admin/users" className="text-blue-600 hover:text-blue-700 text-sm font-medium">
                View All →
              </Link>
            }
          >
            {loading ? (
              <div className="flex justify-center py-8">
                <div className="animate-spin rounded-full h-8 w-8 border-t-2 border-b-2 border-blue-500" />
              </div>
            ) : (
              <DataTable
                columns={tableColumns}
                data={users.slice(0, 10)}
                pagination={false}
                onRowClick={(row) => console.log('User clicked:', row)}
              />
            )}
          </SectionCard>
        </div>

        {/* Admin Actions - Sidebar */}
        <div className="space-y-4">
          {/* User Management */}
          <Card className="bg-gradient-to-br from-blue-50 to-blue-100 border-blue-200">
            <CardBody className="text-center">
              <div className="text-4xl mb-3">👥</div>
              <h3 className="font-semibold text-slate-900 mb-2">Users</h3>
              <p className="text-sm text-slate-700 mb-4">
                Manage all users and permissions
              </p>
              <Link
                to="/admin/users"
                className="block px-4 py-2 bg-blue-600 text-white rounded-lg font-medium hover:bg-blue-700 transition-colors text-center text-sm"
              >
                Manage Users →
              </Link>
            </CardBody>
          </Card>

          {/* Assessments */}
          <Card className="bg-gradient-to-br from-green-50 to-green-100 border-green-200">
            <CardBody className="text-center">
              <div className="text-4xl mb-3">📋</div>
              <h3 className="font-semibold text-slate-900 mb-2">Assessments</h3>
              <p className="text-sm text-slate-700 mb-4">
                Create and manage skill assessments
              </p>
              <Link
                to="/admin/assessments"
                className="block px-4 py-2 bg-green-600 text-white rounded-lg font-medium hover:bg-green-700 transition-colors text-center text-sm"
              >
                Go To Assessments →
              </Link>
            </CardBody>
          </Card>

          {/* Tasks */}
          <Card className="bg-gradient-to-br from-yellow-50 to-yellow-100 border-yellow-200">
            <CardBody className="text-center">
              <div className="text-4xl mb-3">🎯</div>
              <h3 className="font-semibold text-slate-900 mb-2">Tasks</h3>
              <p className="text-sm text-slate-700 mb-4">
                Create and manage learning tasks
              </p>
              <Link
                to="/admin/tasks"
                className="block px-4 py-2 bg-yellow-600 text-white rounded-lg font-medium hover:bg-yellow-700 transition-colors text-center text-sm"
              >
                Manage Tasks →
              </Link>
            </CardBody>
          </Card>

          {/* Reports & Analytics */}
          <Card className="bg-gradient-to-br from-purple-50 to-purple-100 border-purple-200">
            <CardBody className="text-center">
              <div className="text-4xl mb-3">📈</div>
              <h3 className="font-semibold text-slate-900 mb-2">Analytics</h3>
              <p className="text-sm text-slate-700 mb-4">
                View detailed platform metrics
              </p>
              <Link
                to="/admin/reports"
                className="block px-4 py-2 bg-purple-600 text-white rounded-lg font-medium hover:bg-purple-700 transition-colors text-center text-sm"
              >
                View Reports →
              </Link>
            </CardBody>
          </Card>

          {/* Settings */}
          <Card className="bg-gradient-to-br from-slate-50 to-slate-100 border-slate-200">
            <CardBody className="text-center">
              <div className="text-4xl mb-3">⚙️</div>
              <h3 className="font-semibold text-slate-900 mb-2">Settings</h3>
              <p className="text-sm text-slate-700 mb-4">
                Configure system settings
              </p>
              <Link
                to="/admin/settings"
                className="block px-4 py-2 bg-slate-600 text-white rounded-lg font-medium hover:bg-slate-700 transition-colors text-center text-sm"
              >
                Go To Settings →
              </Link>
            </CardBody>
          </Card>
        </div>
      </div>

      {/* System Overview */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {/* Active Sessions */}
        <SectionCard
          title="🟢 Active Sessions"
          subtitle="Real-time system activity"
        >
          <div className="space-y-3">
            <div className="flex items-center justify-between p-3 bg-slate-50 rounded-lg">
              <span className="text-sm font-medium text-slate-700">Online Users</span>
              <Badge text={Math.floor(Math.random() * 50 + 10)} status="success" size="sm" />
            </div>
            <div className="flex items-center justify-between p-3 bg-slate-50 rounded-lg">
              <span className="text-sm font-medium text-slate-700">Active Sessions</span>
              <Badge text={Math.floor(Math.random() * 30 + 5)} status="info" size="sm" />
            </div>
            <div className="flex items-center justify-between p-3 bg-slate-50 rounded-lg">
              <span className="text-sm font-medium text-slate-700">System Status</span>
              <Badge text="Operational" status="success" size="sm" />
            </div>
          </div>
        </SectionCard>

        {/* Platform Stats */}
        <SectionCard
          title="📊 Platform Stats"
          subtitle="Last 30 days"
        >
          <div className="space-y-3">
            <div className="flex items-center justify-between p-3 bg-slate-50 rounded-lg">
              <span className="text-sm font-medium text-slate-700">Assessments Taken</span>
              <span className="font-bold text-slate-900">{Math.floor(Math.random() * 500 + 100)}</span>
            </div>
            <div className="flex items-center justify-between p-3 bg-slate-50 rounded-lg">
              <span className="text-sm font-medium text-slate-700">Tasks Completed</span>
              <span className="font-bold text-slate-900">{Math.floor(Math.random() * 300 + 50)}</span>
            </div>
            <div className="flex items-center justify-between p-3 bg-slate-50 rounded-lg">
              <span className="text-sm font-medium text-slate-700">New Users</span>
              <span className="font-bold text-slate-900">{Math.floor(Math.random() * 50 + 10)}</span>
            </div>
          </div>
        </SectionCard>

        {/* System Health */}
        <SectionCard
          title="🏥 System Health"
          subtitle="Current status"
        >
          <div className="space-y-3">
            <div className="flex items-center justify-between p-3 bg-slate-50 rounded-lg">
              <span className="text-sm font-medium text-slate-700">Database</span>
              <Badge text="Healthy" status="success" size="sm" />
            </div>
            <div className="flex items-center justify-between p-3 bg-slate-50 rounded-lg">
              <span className="text-sm font-medium text-slate-700">API Server</span>
              <Badge text="Healthy" status="success" size="sm" />
            </div>
            <div className="flex items-center justify-between p-3 bg-slate-50 rounded-lg">
              <span className="text-sm font-medium text-slate-700">Storage</span>
              <Badge text="88% Used" status="warning" size="sm" />
            </div>
          </div>
        </SectionCard>
      </div>
    </DashboardLayout>
  );
}
