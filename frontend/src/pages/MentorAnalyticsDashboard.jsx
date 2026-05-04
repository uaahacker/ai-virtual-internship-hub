import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import { analyticsService } from '../services/endpoints';
import DashboardLayout from '../components/DashboardLayout';

const CLUSTER_COLORS = {
  Explorer:   { bar: 'bg-gray-400',   badge: 'bg-gray-100 text-gray-700',   ring: 'border-gray-300'  },
  Developing: { bar: 'bg-blue-400',   badge: 'bg-blue-100 text-blue-700',   ring: 'border-blue-300'  },
  Competent:  { bar: 'bg-green-400',  badge: 'bg-green-100 text-green-700', ring: 'border-green-300' },
  Expert:     { bar: 'bg-yellow-400', badge: 'bg-yellow-100 text-yellow-700', ring: 'border-yellow-300' },
};

const StatCard = ({ title, value, subtitle, icon, color = 'blue' }) => {
  const colorMap = {
    blue:   'from-blue-50 to-blue-100 border-blue-200 text-blue-700',
    green:  'from-green-50 to-green-100 border-green-200 text-green-700',
    orange: 'from-orange-50 to-orange-100 border-orange-200 text-orange-700',
    purple: 'from-purple-50 to-purple-100 border-purple-200 text-purple-700',
    red:    'from-red-50 to-red-100 border-red-200 text-red-700',
    slate:  'from-slate-50 to-slate-100 border-slate-200 text-slate-700',
  };
  return (
    <div className={`bg-gradient-to-br ${colorMap[color]} border rounded-xl p-5 hover:shadow-md transition-shadow`}>
      <div className="flex items-start justify-between">
        <div>
          <p className="text-xs font-semibold uppercase tracking-wide opacity-70">{title}</p>
          <p className="text-3xl font-bold mt-1">{value ?? '—'}</p>
          {subtitle && <p className="text-xs mt-1 opacity-70">{subtitle}</p>}
        </div>
        {icon && <span className="text-3xl">{icon}</span>}
      </div>
    </div>
  );
};

const ScoreBadge = ({ score }) => {
  if (score == null || isNaN(score)) return <span className="text-gray-400 text-sm">N/A</span>;
  const color = score >= 80 ? 'bg-green-100 text-green-700' : score >= 60 ? 'bg-yellow-100 text-yellow-700' : 'bg-red-100 text-red-700';
  return <span className={`text-xs font-bold px-2 py-0.5 rounded-full ${color}`}>{score.toFixed(1)}%</span>;
};

const ClusterDistribution = ({ students }) => {
  const groups = {};
  (students || []).forEach((s) => {
    const label = s.cluster_label || 'Explorer';
    if (!groups[label]) groups[label] = { count: 0, display_name: s.cluster_display_name || label, scores: [] };
    groups[label].count += 1;
    if (s.average_score) groups[label].scores.push(s.average_score);
  });
  const total = (students || []).length;
  const ORDER = ['Explorer', 'Developing', 'Competent', 'Expert'];
  return (
    <div className="bg-white border border-gray-200 rounded-xl p-6">
      <h3 className="text-lg font-bold text-gray-900 mb-1">🤖 AI — Student Cluster Distribution</h3>
      <p className="text-sm text-gray-500 mb-5">ML-based grouping of your students by performance &amp; skill pattern</p>
      <div className="space-y-4">
        {ORDER.map((label) => {
          const g = groups[label];
          if (!g) return null;
          const pct = total > 0 ? Math.round((g.count / total) * 100) : 0;
          const avgScore = g.scores.length ? (g.scores.reduce((a, b) => a + b, 0) / g.scores.length).toFixed(1) : null;
          const c = CLUSTER_COLORS[label] || CLUSTER_COLORS.Explorer;
          return (
            <div key={label}>
              <div className="flex items-center justify-between mb-1">
                <div className="flex items-center gap-2">
                  <span className={`text-xs px-2 py-0.5 rounded-full font-semibold ${c.badge}`}>{label}</span>
                  <span className="text-sm text-gray-700 font-medium">{g.display_name}</span>
                </div>
                <div className="flex items-center gap-3">
                  <span className="text-sm font-bold text-gray-900">{g.count} student{g.count !== 1 ? 's' : ''}</span>
                  {avgScore && <span className="text-xs text-gray-500">avg {avgScore}%</span>}
                </div>
              </div>
              <div className="w-full bg-gray-100 rounded-full h-2.5">
                <div className={`h-2.5 rounded-full ${c.bar} transition-all`} style={{ width: `${pct}%` }} />
              </div>
              <p className="text-xs text-gray-400 mt-0.5">{pct}% of your students</p>
            </div>
          );
        })}
        {total === 0 && <p className="text-sm text-gray-500 py-4 text-center">No student data yet.</p>}
      </div>
    </div>
  );
};

const AIInsights = ({ analytics }) => {
  if (!analytics) return null;
  const students = analytics.students_performance || [];
  const avgScore = analytics.average_task_score || 0;
  const pending = analytics.pending_reviews || 0;
  const domainDist = analytics.domain_distribution || {};
  const insights = [];
  const sorted = [...students].filter(s => s.average_score > 0).sort((a, b) => b.average_score - a.average_score);
  if (sorted.length > 0) {
    insights.push({ icon: '🏆', color: 'green', title: 'Top Performer', text: `${sorted[0].name} leads with ${sorted[0].average_score.toFixed(1)}% avg score (${sorted[0].cluster_display_name || sorted[0].cluster_label} tier).` });
  }
  const atRisk = students.filter(s => s.average_score > 0 && s.average_score < 60);
  if (atRisk.length > 0) {
    insights.push({ icon: '⚠️', color: 'red', title: 'Needs Attention', text: `${atRisk.length} student${atRisk.length > 1 ? 's' : ''} scoring below 60% — consider targeted feedback.` });
  }
  const experts = students.filter(s => s.cluster_label === 'Expert');
  if (experts.length > 0) {
    insights.push({ icon: '⭐', color: 'yellow', title: 'Expert Students', text: `${experts.length} student${experts.length > 1 ? 's' : ''} reached Expert level. Consider assigning advanced tasks.` });
  }
  if (pending > 3) {
    insights.push({ icon: '📋', color: 'orange', title: 'Review Backlog', text: `${pending} tasks pending review. Clearing these will help students progress faster.` });
  } else if (pending === 0 && analytics.total_tasks_reviewed > 0) {
    insights.push({ icon: '✅', color: 'green', title: 'All Caught Up', text: 'No pending reviews. Great job staying on top of evaluations!' });
  }
  const domainEntries = Object.entries(domainDist).sort((a, b) => b[1] - a[1]);
  if (domainEntries.length > 0) {
    insights.push({ icon: '📌', color: 'blue', title: 'Most Active Domain', text: `${domainEntries[0][0]} has the most evaluated tasks (${domainEntries[0][1]}). Students are engaged here.` });
  }
  if (avgScore > 0) {
    const level = avgScore >= 80 ? 'excellent' : avgScore >= 65 ? 'good' : avgScore >= 50 ? 'moderate' : 'needs improvement';
    insights.push({ icon: '📊', color: 'purple', title: 'Cohort Performance', text: `Your students average score is ${avgScore.toFixed(1)}% — ${level} overall cohort performance.` });
  }
  if (analytics.total_tasks_reviewed === 0) {
    insights.push({ icon: '💡', color: 'slate', title: 'Get Started', text: 'No evaluations yet. Once you review student tasks, AI insights will appear here.' });
  }
  const colorMap = {
    green: 'bg-green-50 border-green-200 text-green-700',
    red: 'bg-red-50 border-red-200 text-red-700',
    orange: 'bg-orange-50 border-orange-200 text-orange-700',
    blue: 'bg-blue-50 border-blue-200 text-blue-700',
    purple: 'bg-purple-50 border-purple-200 text-purple-700',
    yellow: 'bg-yellow-50 border-yellow-200 text-yellow-700',
    slate: 'bg-slate-50 border-slate-200 text-slate-700',
  };
  return (
    <div className="bg-white border border-gray-200 rounded-xl p-6">
      <h3 className="text-lg font-bold text-gray-900 mb-1">🧠 AI Insights</h3>
      <p className="text-sm text-gray-500 mb-5">Automated observations from your student data</p>
      <div className="space-y-3">
        {insights.map((ins, i) => (
          <div key={i} className={`flex items-start gap-3 p-3 rounded-lg border ${colorMap[ins.color]}`}>
            <span className="text-xl shrink-0 mt-0.5">{ins.icon}</span>
            <div>
              <p className="font-semibold text-sm">{ins.title}</p>
              <p className="text-xs mt-0.5 opacity-90">{ins.text}</p>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

const StudentPerformanceTable = ({ students }) => (
  <div className="bg-white border border-gray-200 rounded-xl p-6">
    <h3 className="text-lg font-bold text-gray-900 mb-4">📋 Student Performance</h3>
    <div className="overflow-x-auto">
      <table className="w-full">
        <thead>
          <tr className="border-b border-gray-200">
            <th className="text-left py-3 px-4 text-xs font-semibold text-gray-500 uppercase">Student</th>
            <th className="text-center py-3 px-4 text-xs font-semibold text-gray-500 uppercase">Cluster</th>
            <th className="text-center py-3 px-4 text-xs font-semibold text-gray-500 uppercase">Tasks Reviewed</th>
            <th className="text-center py-3 px-4 text-xs font-semibold text-gray-500 uppercase">Avg Score</th>
            <th className="text-center py-3 px-4 text-xs font-semibold text-gray-500 uppercase">Progress</th>
          </tr>
        </thead>
        <tbody>
          {(students || []).length === 0 && (
            <tr><td colSpan={5} className="py-8 text-center text-gray-400 text-sm">No evaluations yet</td></tr>
          )}
          {(students || []).map((s, idx) => {
            const c = CLUSTER_COLORS[s.cluster_label] || CLUSTER_COLORS.Explorer;
            const score = s.average_score || 0;
            const barW = Math.min(100, Math.max(0, score));
            const barColor = score >= 80 ? 'bg-green-400' : score >= 60 ? 'bg-yellow-400' : 'bg-red-400';
            return (
              <tr key={idx} className="border-b border-gray-100 hover:bg-gray-50">
                <td className="py-3 px-4">
                  <div className="flex items-center gap-2">
                    <div className="w-7 h-7 rounded-full bg-gradient-to-br from-blue-400 to-indigo-600 flex items-center justify-center text-white text-xs font-bold shrink-0">
                      {s.name?.[0]?.toUpperCase() || '?'}
                    </div>
                    <div>
                      <p className="text-sm font-medium text-gray-900">{s.name}</p>
                      <p className="text-xs text-gray-500">{s.email}</p>
                    </div>
                  </div>
                </td>
                <td className="py-3 px-4 text-center">
                  <span className={`text-xs px-2 py-0.5 rounded-full font-semibold ${c.badge}`}>
                    {s.cluster_label || 'Explorer'}
                  </span>
                </td>
                <td className="py-3 px-4 text-center text-sm font-medium text-gray-700">{s.tasks_evaluated}</td>
                <td className="py-3 px-4 text-center"><ScoreBadge score={s.average_score} /></td>
                <td className="py-3 px-4">
                  <div className="w-full bg-gray-100 rounded-full h-2 min-w-[60px]">
                    <div className={`h-2 rounded-full ${barColor}`} style={{ width: `${barW}%` }} />
                  </div>
                </td>
              </tr>
            );
          })}
        </tbody>
      </table>
    </div>
  </div>
);

const DomainDistributionTable = ({ distribution }) => {
  const entries = Object.entries(distribution || {}).sort((a, b) => b[1] - a[1]);
  const max = entries[0]?.[1] || 1;
  const DOMAIN_ICONS = {
    'Graphic Design': '🎨', 'Content Writing': '✍️', 'Programming': '💻',
    'Freelancing': '💼', 'E-Commerce': '🛒', 'QuickBooks': '📊',
    'AutoCAD': '📐', 'Data Analytics': '📈', 'Digital Marketing': '📣', 'WordPress': '🌐',
  };
  return (
    <div className="bg-white border border-gray-200 rounded-xl p-6">
      <h3 className="text-lg font-bold text-gray-900 mb-1">🗂️ Domain Breakdown</h3>
      <p className="text-sm text-gray-500 mb-5">Tasks evaluated per domain</p>
      {entries.length === 0 && <p className="text-sm text-gray-400 py-4 text-center">No domain data yet.</p>}
      <div className="space-y-3">
        {entries.map(([domain, count]) => (
          <div key={domain}>
            <div className="flex items-center justify-between mb-1">
              <span className="text-sm text-gray-800 font-medium flex items-center gap-1.5">
                <span>{DOMAIN_ICONS[domain] || '📂'}</span>{domain}
              </span>
              <span className="text-sm font-bold text-gray-700">{count}</span>
            </div>
            <div className="w-full bg-gray-100 rounded-full h-2">
              <div className="h-2 rounded-full bg-indigo-400" style={{ width: `${Math.round((count / max) * 100)}%` }} />
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

const AttentionList = ({ students }) => {
  const atRisk = (students || []).filter(s => s.average_score > 0 && s.average_score < 60).sort((a, b) => a.average_score - b.average_score);
  const unexplored = (students || []).filter(s => s.tasks_evaluated === 0);
  if (atRisk.length === 0 && unexplored.length === 0) return null;
  return (
    <div className="bg-white border border-red-200 rounded-xl p-6">
      <h3 className="text-lg font-bold text-gray-900 mb-1">⚠️ Needs Attention</h3>
      <p className="text-sm text-gray-500 mb-4">Students who may need extra support</p>
      <div className="space-y-2">
        {atRisk.map((s, i) => (
          <div key={i} className="flex items-center justify-between p-3 bg-red-50 border border-red-100 rounded-lg">
            <div className="flex items-center gap-2">
              <span className="text-lg">📉</span>
              <div>
                <p className="text-sm font-semibold text-gray-900">{s.name}</p>
                <p className="text-xs text-gray-500">{s.email}</p>
              </div>
            </div>
            <ScoreBadge score={s.average_score} />
          </div>
        ))}
        {unexplored.map((s, i) => (
          <div key={`u${i}`} className="flex items-center justify-between p-3 bg-orange-50 border border-orange-100 rounded-lg">
            <div className="flex items-center gap-2">
              <span className="text-lg">💤</span>
              <div>
                <p className="text-sm font-semibold text-gray-900">{s.name}</p>
                <p className="text-xs text-gray-500">No tasks reviewed yet</p>
              </div>
            </div>
            <span className="text-xs text-orange-600 font-semibold">Inactive</span>
          </div>
        ))}
      </div>
    </div>
  );
};

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
    if (!loading && user) fetchAnalytics();
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
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Mentor Analytics</h1>
          <p className="text-gray-600 mt-2">Monitor your students, AI cluster insights, and evaluation workload</p>
        </div>

        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <StatCard title="Assigned Students" value={analytics.total_assigned_students || 0} icon="👥" color="blue" />
          <StatCard title="Pending Reviews" value={analytics.pending_reviews || 0} subtitle="Awaiting evaluation" icon="📋" color="orange" />
          <StatCard title="Tasks Reviewed" value={analytics.total_tasks_reviewed || 0} icon="✅" color="green" />
          <StatCard title="Avg Task Score" value={analytics.average_task_score ? `${analytics.average_task_score.toFixed(1)}%` : '—'} subtitle="Across all evaluations" icon="📊" color="purple" />
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <ClusterDistribution students={analytics.students_performance} />
          <AIInsights analytics={analytics} />
        </div>

        <AttentionList students={analytics.students_performance} />

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <StudentPerformanceTable students={analytics.students_performance} />
          <DomainDistributionTable distribution={analytics.domain_distribution} />
        </div>
      </div>
    </DashboardLayout>
  );
};

export default MentorAnalyticsDashboard;
