import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import { analyticsService } from '../services/endpoints';
import DashboardLayout from '../components/DashboardLayout';

const StatCard = ({ title, value, subtitle, icon: Icon }) => (
  <div className="bg-white border border-gray-200 rounded-lg p-6 hover:shadow-md transition-shadow">
    <div className="flex justify-between items-start">
      <div>
        <p className="text-gray-600 text-sm font-medium">{title}</p>
        <p className="text-3xl font-bold text-gray-900 mt-2">{value}</p>
        {subtitle && <p className="text-gray-500 text-xs mt-1">{subtitle}</p>}
      </div>
      {Icon && <Icon className="w-8 h-8 text-gray-400" />}
    </div>
  </div>
);

const DomainBreakdownTable = ({ domains }) => (
  <div className="bg-white border border-gray-200 rounded-lg p-6">
    <h3 className="text-lg font-semibold text-gray-900 mb-4">Domain Breakdown</h3>
    <div className="overflow-x-auto">
      <table className="w-full">
        <thead>
          <tr className="border-b border-gray-200">
            <th className="text-left py-3 px-4 text-sm font-semibold text-gray-700">Domain</th>
            <th className="text-center py-3 px-4 text-sm font-semibold text-gray-700">Tasks</th>
            <th className="text-center py-3 px-4 text-sm font-semibold text-gray-700">Avg Score</th>
          </tr>
        </thead>
        <tbody>
          {domains && Object.entries(domains).map(([domain, data], idx) => (
            <tr key={idx} className="border-b border-gray-100 hover:bg-gray-50">
              <td className="py-3 px-4 text-sm text-gray-900">{domain}</td>
              <td className="py-3 px-4 text-sm text-gray-700 text-center">{data.tasks_completed}</td>
              <td className="py-3 px-4 text-sm text-gray-700 text-center">
                {isNaN(data.average_score) ? 'N/A' : `${data.average_score.toFixed(1)}%`}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  </div>
);

const SkillTrendTable = ({ trends }) => (
  <div className="bg-white border border-gray-200 rounded-lg p-6">
    <h3 className="text-lg font-semibold text-gray-900 mb-4">Skill Improvement Trend</h3>
    {(!trends || trends.length === 0) ? (
      <div className="text-center py-8 text-gray-400">
        <p className="text-sm">No evaluated tasks yet.</p>
        <p className="text-xs mt-1">Complete and submit tasks to see your score trend here.</p>
      </div>
    ) : (
      <div className="overflow-x-auto">
        <table className="w-full">
          <thead>
            <tr className="border-b border-gray-200">
              <th className="text-left py-3 px-4 text-sm font-semibold text-gray-700">Task</th>
              <th className="text-left py-3 px-4 text-sm font-semibold text-gray-700">Domain</th>
              <th className="text-center py-3 px-4 text-sm font-semibold text-gray-700">Score</th>
              <th className="text-center py-3 px-4 text-sm font-semibold text-gray-700">Date</th>
            </tr>
          </thead>
          <tbody>
            {trends.map((trend, idx) => (
              <tr key={idx} className="border-b border-gray-100 hover:bg-gray-50">
                <td className="py-3 px-4 text-sm text-gray-900">{trend.task || 'N/A'}</td>
                <td className="py-3 px-4 text-sm text-gray-500">{trend.domain || '—'}</td>
                <td className="py-3 px-4 text-sm text-gray-700 text-center">
                  {trend.score != null ? `${Number(trend.score).toFixed(1)}%` : 'N/A'}
                </td>
                <td className="py-3 px-4 text-sm text-gray-700 text-center">
                  {trend.date ? new Date(trend.date).toLocaleDateString() : '—'}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    )}
  </div>
);

const StudentAnalyticsDashboard = () => {
  const navigate = useNavigate();
  const { user, loading } = useAuth();
  const [analytics, setAnalytics] = useState(null);
  const [fetching, setFetching] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    if (!loading && user?.role !== 'Student') {
      navigate('/login');
      return;
    }

    const fetchAnalytics = async () => {
      try {
        const response = await analyticsService.getStudentAnalytics();
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

  return (
    <DashboardLayout>
      <div className="space-y-6">
        {/* Header */}
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Analytics Dashboard</h1>
          <p className="text-gray-600 mt-2">View your learning progress and statistics</p>
        </div>

        {/* Main Stats Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          <StatCard
            title="Total Assessments"
            value={analytics.total_assessments_attempted || 0}
          />
          <StatCard
            title="Completed Tasks"
            value={analytics.completed_tasks || 0}
          />
          <StatCard
            title="Average MCQ Score"
            value={`${(analytics.average_mcq_score || 0).toFixed(1)}%`}
          />
          <StatCard
            title="Average Final Score"
            value={`${(analytics.average_final_score || 0).toFixed(1)}%`}
          />
          <StatCard
            title="Strongest Domain"
            value={analytics.strongest_domain || 'N/A'}
            subtitle={`${(analytics.strongest_domain_score || 0).toFixed(1)}%`}
          />
          <StatCard
            title="Weakest Domain"
            value={analytics.weakest_domain || 'N/A'}
            subtitle={`${(analytics.weakest_domain_score || 0).toFixed(1)}%`}
          />
        </div>

        {/* Recommended Domain */}
        <div className="bg-gradient-to-r from-gray-50 to-gray-100 border border-gray-200 rounded-lg p-6">
          <h3 className="text-lg font-semibold text-gray-900">Recommended Next Domain</h3>
          <p className="text-gray-600 mt-2">
            Based on your progress, we recommend focusing on:
          </p>
          <p className="text-2xl font-bold text-gray-900 mt-3">
            {analytics.recommended_next_domain || 'N/A'}
          </p>
          <p className="text-sm text-gray-600 mt-2">
            This domain has the lowest completion rate in your portfolio
          </p>
        </div>

        {/* Detailed Tables */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <DomainBreakdownTable domains={analytics.domain_breakdown} />
          <SkillTrendTable trends={analytics.skill_improvement_trend} />
        </div>
      </div>
    </DashboardLayout>
  );
};

export default StudentAnalyticsDashboard;
