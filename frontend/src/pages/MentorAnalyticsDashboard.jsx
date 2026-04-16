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

const StudentPerformanceTable = ({ students }) => (
  <div className="bg-white border border-gray-200 rounded-lg p-6">
    <h3 className="text-lg font-semibold text-gray-900 mb-4">Student Performance</h3>
    <div className="overflow-x-auto">
      <table className="w-full">
        <thead>
          <tr className="border-b border-gray-200">
            <th className="text-left py-3 px-4 text-sm font-semibold text-gray-700">Student Name</th>
            <th className="text-left py-3 px-4 text-sm font-semibold text-gray-700">Email</th>
            <th className="text-center py-3 px-4 text-sm font-semibold text-gray-700">Tasks Evaluated</th>
            <th className="text-center py-3 px-4 text-sm font-semibold text-gray-700">Avg Score</th>
          </tr>
        </thead>
        <tbody>
          {students && students.map((student, idx) => (
            <tr key={idx} className="border-b border-gray-100 hover:bg-gray-50">
              <td className="py-3 px-4 text-sm text-gray-900 font-medium">{student.name}</td>
              <td className="py-3 px-4 text-sm text-gray-700">{student.email}</td>
              <td className="py-3 px-4 text-sm text-gray-700 text-center">{student.tasks_evaluated}</td>
              <td className="py-3 px-4 text-sm text-gray-700 text-center">
                {isNaN(student.average_score) ? 'N/A' : `${student.average_score.toFixed(1)}%`}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  </div>
);

const DomainDistributionTable = ({ distribution }) => (
  <div className="bg-white border border-gray-200 rounded-lg p-6">
    <h3 className="text-lg font-semibold text-gray-900 mb-4">Domain-wise Student Distribution</h3>
    <div className="overflow-x-auto">
      <table className="w-full">
        <thead>
          <tr className="border-b border-gray-200">
            <th className="text-left py-3 px-4 text-sm font-semibold text-gray-700">Domain</th>
            <th className="text-center py-3 px-4 text-sm font-semibold text-gray-700">Students Working</th>
          </tr>
        </thead>
        <tbody>
          {distribution && Object.entries(distribution).map(([domain, count], idx) => (
            <tr key={idx} className="border-b border-gray-100 hover:bg-gray-50">
              <td className="py-3 px-4 text-sm text-gray-900">{domain}</td>
              <td className="py-3 px-4 text-sm text-gray-700 text-center font-medium">{count}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  </div>
);

const MentorAnalyticsDashboard = () => {
  const navigate = useNavigate();
  const { user, loading } = useAuth();
  const [analytics, setAnalytics] = useState(null);
  const [fetching, setFetching] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    if (!loading && user?.role !== 'Mentor') {
      navigate('/login');
      return;
    }

    const fetchAnalytics = async () => {
      try {
        const response = await analyticsService.getMentorAnalytics();
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
          <h1 className="text-3xl font-bold text-gray-900">Mentor Analytics</h1>
          <p className="text-gray-600 mt-2">Monitor your students and evaluation workload</p>
        </div>

        {/* Main Stats Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          <StatCard
            title="Assigned Students"
            value={analytics.total_assigned_students || 0}
          />
          <StatCard
            title="Pending Reviews"
            value={analytics.pending_mentor_reviews || 0}
            subtitle="Tasks awaiting evaluation"
          />
          <StatCard
            title="Evaluations Completed"
            value={analytics.total_evaluations_completed || 0}
          />
        </div>

        {/* Detailed Tables */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <StudentPerformanceTable students={analytics.students_performance} />
          <DomainDistributionTable distribution={analytics.domain_wise_student_distribution} />
        </div>
      </div>
    </DashboardLayout>
  );
};

export default MentorAnalyticsDashboard;
