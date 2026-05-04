import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import { analyticsService } from '../services/endpoints';
import DashboardLayout from '../components/DashboardLayout';

const StatCard = ({ title, value, subtitle }) => (
  <div className="bg-white border border-gray-200 rounded-lg p-6 hover:shadow-md transition-shadow">
    <div>
      <p className="text-gray-600 text-sm font-medium">{title}</p>
      <p className="text-3xl font-bold text-gray-900 mt-2">{value}</p>
      {subtitle && <p className="text-gray-500 text-xs mt-1">{subtitle}</p>}
    </div>
  </div>
);

const PopularDomainsTable = ({ domains }) => (
  <div className="bg-white border border-gray-200 rounded-lg p-6">
    <h3 className="text-lg font-semibold text-gray-900 mb-4">Popular Domains</h3>
    <div className="overflow-x-auto">
      <table className="w-full">
        <thead>
          <tr className="border-b border-gray-200">
            <th className="text-left py-3 px-4 text-sm font-semibold text-gray-700">Domain</th>
            <th className="text-center py-3 px-4 text-sm font-semibold text-gray-700">Tasks Completed</th>
          </tr>
        </thead>
        <tbody>
          {domains && domains.slice(0, 10).map((domain, idx) => (
            <tr key={idx} className="border-b border-gray-100 hover:bg-gray-50">
              <td className="py-3 px-4 text-sm text-gray-900">{domain.domain}</td>
              <td className="py-3 px-4 text-sm text-gray-700 text-center font-medium">{domain.completions}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  </div>
);

const MentorLoadTable = ({ mentors }) => (
  <div className="bg-white border border-gray-200 rounded-lg p-6">
    <h3 className="text-lg font-semibold text-gray-900 mb-4">Mentor Workload Distribution</h3>
    <div className="overflow-x-auto">
      <table className="w-full">
        <thead>
          <tr className="border-b border-gray-200">
            <th className="text-left py-3 px-4 text-sm font-semibold text-gray-700">Mentor</th>
            <th className="text-center py-3 px-4 text-sm font-semibold text-gray-700">Students Assigned</th>
            <th className="text-center py-3 px-4 text-sm font-semibold text-gray-700">Evaluations Done</th>
          </tr>
        </thead>
        <tbody>
          {mentors && mentors.map((mentor, idx) => (
            <tr key={idx} className="border-b border-gray-100 hover:bg-gray-50">
              <td className="py-3 px-4 text-sm text-gray-900">{mentor.mentor_name}</td>
              <td className="py-3 px-4 text-sm text-gray-700 text-center">{mentor.students_assigned}</td>
              <td className="py-3 px-4 text-sm text-gray-700 text-center font-medium">{mentor.evaluations_completed}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  </div>
);

const ClusterDistributionCard = ({ clusters }) => {
  if (!clusters || clusters.length === 0) return null;
  const total = clusters.reduce((sum, c) => sum + c.count, 0);
  const COLORS = {
    Explorer:   { bar: 'bg-gray-400',   badge: 'bg-gray-100 text-gray-700'   },
    Developing: { bar: 'bg-blue-400',   badge: 'bg-blue-100 text-blue-700'   },
    Competent:  { bar: 'bg-green-400',  badge: 'bg-green-100 text-green-700' },
    Expert:     { bar: 'bg-yellow-400', badge: 'bg-yellow-100 text-yellow-700' },
  };
  return (
    <div className="bg-white border border-gray-200 rounded-lg p-6">
      <h3 className="text-lg font-semibold text-gray-900 mb-1">Student Cluster Distribution</h3>
      <p className="text-sm text-gray-500 mb-4">How students are grouped by performance and skill pattern</p>
      <div className="space-y-4">
        {clusters.map((cluster) => {
          const pct = total > 0 ? Math.round((cluster.count / total) * 100) : 0;
          const colors = COLORS[cluster.label] || COLORS.Explorer;
          return (
            <div key={cluster.label}>
              <div className="flex items-center justify-between mb-1">
                <div className="flex items-center gap-2">
                  <span className={`text-xs px-2 py-0.5 rounded-full font-medium ${colors.badge}`}>
                    {cluster.label}
                  </span>
                  <span className="text-sm text-gray-700 font-medium">{cluster.display_name}</span>
                </div>
                <div className="flex items-center gap-3 text-right">
                  <span className="text-sm font-bold text-gray-900">{cluster.count} students</span>
                  {cluster.avg_score > 0 && (
                    <span className="text-xs text-gray-500">avg {cluster.avg_score}%</span>
                  )}
                </div>
              </div>
              <div className="w-full bg-gray-100 rounded-full h-2">
                <div
                  className={`h-2 rounded-full ${colors.bar}`}
                  style={{ width: `${pct}%` }}
                />
              </div>
              <p className="text-xs text-gray-400 mt-0.5">{pct}% of all students</p>
            </div>
          );
        })}
      </div>
    </div>
  );
};

const AdminAnalyticsDashboard = () => {
  const navigate = useNavigate();
  const { user, loading } = useAuth();
  const [analytics, setAnalytics] = useState(null);
  const [fetching, setFetching] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    if (!loading && user?.role !== 'Admin') {
      navigate('/login');
      return;
    }

    const fetchAnalytics = async () => {
      try {
        const response = await analyticsService.getAdminAnalytics();
        if (response.data.success) {
          setAnalytics(response.data.data);
        } else {
          setError('Failed to load analytics');
        }
      } catch (err) {
        setError(err.message || 'Error loading analytics');
      } finally {
        setFetching(false);
      }
    };

    if (!loading && user) {
      fetchAnalytics();
    }
  }, [user, loading, navigate]);

  if (loading || fetching) {
    return (
      <DashboardLayout>
        <div className="flex items-center justify-center min-h-screen">
          <div className="animate-spin rounded-full h-8 w-8 border border-gray-300 border-t-gray-900"></div>
        </div>
      </DashboardLayout>
    );
  }

  if (error) {
    return (
      <DashboardLayout>
        <div className="p-6 bg-red-50 border border-red-200 rounded-lg">
          <p className="text-red-800">Error: {error}</p>
        </div>
      </DashboardLayout>
    );
  }

  if (!analytics) {
    return (
      <DashboardLayout>
        <div className="p-6 bg-gray-50 border border-gray-200 rounded-lg">
          <p className="text-gray-700">No analytics data available</p>
        </div>
      </DashboardLayout>
    );
  }

  const systemMetrics = analytics.system_metrics || {};

  return (
    <DashboardLayout>
      <div className="space-y-6">
        {/* Header */}
        <div>
          <h1 className="text-3xl font-bold text-gray-900">System Analytics</h1>
          <p className="text-gray-600 mt-2">Monitor overall platform activity and performance</p>
        </div>

        {/* System Metrics Grid */}
        <div>
          <h2 className="text-xl font-semibold text-gray-900 mb-4">System Metrics</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            <StatCard
              title="Total Users"
              value={systemMetrics.total_users || 0}
            />
            <StatCard
              title="Total Students"
              value={systemMetrics.total_students || 0}
            />
            <StatCard
              title="Total Mentors"
              value={systemMetrics.total_mentors || 0}
            />
            <StatCard
              title="Total Admins"
              value={systemMetrics.total_admins || 0}
            />
          </div>
        </div>

        {/* Activity Metrics */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          <StatCard
            title="Assessments Attempted"
            value={systemMetrics.assessments_attempts || 0}
          />
          <StatCard
            title="Tasks Completed"
            value={systemMetrics.tasks_completed || 0}
          />
          <StatCard
            title="Total Evaluations"
            value={systemMetrics.total_evaluations || 0}
          />
          <StatCard
            title="Average Performance"
            value={`${(systemMetrics.average_system_performance || 0).toFixed(1)}%`}
          />
        </div>

        {/* Detailed Tables */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <PopularDomainsTable domains={analytics.popular_domains} />
          <MentorLoadTable mentors={analytics.mentor_load_distribution} />
        </div>

        {/* Cluster Distribution */}
        {analytics.student_cluster_distribution?.length > 0 && (
          <ClusterDistributionCard clusters={analytics.student_cluster_distribution} />
        )}
      </div>
    </DashboardLayout>
  );
};

export default AdminAnalyticsDashboard;
