import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { toast } from 'react-toastify';
import { useAuth } from '../contexts/AuthContext';
import api from '../services/api';
import DashboardLayout from '../components/DashboardLayout';

// ── Helpers ──────────────────────────────────────────────────────────────────

const GRADE_STYLES = {
  Distinction: 'bg-purple-600 text-white',
  A: 'bg-green-600 text-white',
  B: 'bg-blue-600 text-white',
  C: 'bg-yellow-500 text-white',
  D: 'bg-red-500 text-white',
};

const DOMAIN_COLORS = [
  'bg-blue-100 text-blue-800',
  'bg-purple-100 text-purple-800',
  'bg-green-100 text-green-800',
  'bg-orange-100 text-orange-800',
  'bg-pink-100 text-pink-800',
];

function getScoreColor(score) {
  if (score >= 90) return 'text-purple-700';
  if (score >= 80) return 'text-green-700';
  if (score >= 70) return 'text-blue-700';
  if (score >= 60) return 'text-yellow-700';
  return 'text-red-600';
}

function formatDate(dateStr) {
  if (!dateStr) return '—';
  return new Date(dateStr).toLocaleDateString('en-US', {
    year: 'numeric', month: 'short', day: 'numeric',
  });
}

// ── Sub-components ────────────────────────────────────────────────────────────

function OverviewSection({ overview }) {
  if (!overview) return null;
  const { top_domains, all_skills, improvement_trend, strengths_list, summary_sentence } = overview;

  return (
    <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-6 mb-6 print:border-0 print:shadow-none print:break-inside-avoid">
      <p className="text-gray-700 text-sm leading-relaxed mb-5">{summary_sentence}</p>
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {top_domains && top_domains.length > 0 && (
          <div>
            <h3 className="text-xs font-semibold text-gray-500 uppercase tracking-wide mb-2">Top Domains</h3>
            <div className="space-y-2">
              {top_domains.map((d, i) => (
                <div key={d.domain} className="flex items-center gap-2">
                  <span className={`px-2 py-0.5 text-xs rounded-full font-medium ${DOMAIN_COLORS[i % DOMAIN_COLORS.length]}`}>
                    {d.domain}
                  </span>
                  <span className="text-xs text-gray-500">{d.count} task{d.count !== 1 ? 's' : ''} · avg {d.avg_score}%</span>
                </div>
              ))}
            </div>
          </div>
        )}
        {all_skills && all_skills.length > 0 && (
          <div>
            <h3 className="text-xs font-semibold text-gray-500 uppercase tracking-wide mb-2">Key Skills</h3>
            <div className="flex flex-wrap gap-1">
              {all_skills.slice(0, 8).map((s) => (
                <span key={s.skill} className="px-2 py-0.5 bg-indigo-50 text-indigo-700 text-xs rounded-full">{s.skill}</span>
              ))}
            </div>
          </div>
        )}
        {strengths_list && strengths_list.length > 0 && (
          <div>
            <h3 className="text-xs font-semibold text-gray-500 uppercase tracking-wide mb-2">Demonstrated Strengths</h3>
            <ul className="space-y-1">
              {strengths_list.map((s, i) => (
                <li key={i} className="flex items-start gap-1 text-xs text-gray-700">
                  <span className="text-green-500 mt-0.5">✓</span>
                  <span>{s}</span>
                </li>
              ))}
            </ul>
          </div>
        )}
      </div>
      {improvement_trend && improvement_trend.length > 1 && (
        <div className="mt-5">
          <h3 className="text-xs font-semibold text-gray-500 uppercase tracking-wide mb-2">Score Progression</h3>
          <div className="flex items-end gap-1 h-12">
            {improvement_trend.map((point, i) => (
              <div key={i} className="flex-1 group relative" title={`${point.title}: ${point.score}%`}>
                <div
                  className={`w-full rounded-t transition-all ${i === improvement_trend.length - 1 ? 'bg-blue-500' : 'bg-gray-300 group-hover:bg-blue-300'}`}
                  style={{ height: `${Math.max(4, point.score)}%` }}
                />
              </div>
            ))}
          </div>
          <div className="flex justify-between text-xs text-gray-400 mt-1">
            <span>{improvement_trend[0]?.date}</span>
            <span>{improvement_trend[improvement_trend.length - 1]?.date}</span>
          </div>
        </div>
      )}
    </div>
  );
}

function GradeBadge({ grade }) {
  const cls = GRADE_STYLES[grade] || 'bg-gray-200 text-gray-700';
  return <span className={`inline-block px-2 py-0.5 text-xs font-bold rounded ${cls}`}>{grade}</span>;
}

function ScoreBar({ score }) {
  return (
    <div className="mt-1">
      <div className="flex items-center gap-2">
        <div className="flex-1 bg-gray-100 rounded-full h-1.5">
          <div
            className={`h-1.5 rounded-full ${score >= 80 ? 'bg-green-500' : score >= 60 ? 'bg-yellow-400' : 'bg-red-400'}`}
            style={{ width: `${Math.min(100, score)}%` }}
          />
        </div>
        <span className={`text-sm font-bold ${getScoreColor(score)}`}>{score.toFixed(1)}%</span>
      </div>
    </div>
  );
}

function PortfolioItemCard({ item, onViewDetails }) {
  return (
    <div
      onClick={onViewDetails}
      className="bg-white rounded-xl shadow-sm border border-gray-100 hover:shadow-md hover:border-blue-200 transition-all cursor-pointer overflow-hidden print:break-inside-avoid print:border print:shadow-none"
    >
      {item.is_featured && (
        <div className="bg-amber-50 border-b border-amber-100 px-4 py-1.5 text-xs font-semibold text-amber-700">⭐ Featured</div>
      )}
      <div className="p-5">
        <div className="flex items-start justify-between gap-3 mb-3">
          <div className="min-w-0 flex-1">
            <h3 className="font-semibold text-gray-900 text-sm leading-snug truncate">{item.task_title}</h3>
            <div className="flex flex-wrap gap-1 mt-1.5">
              <span className="px-2 py-0.5 bg-blue-50 text-blue-700 text-xs rounded-full">{item.task_domain}</span>
              <span className="px-2 py-0.5 bg-gray-100 text-gray-600 text-xs rounded-full">{item.task_difficulty}</span>
              <span className="px-2 py-0.5 bg-gray-100 text-gray-600 text-xs rounded-full">{item.task_type}</span>
            </div>
          </div>
          <GradeBadge grade={item.grade} />
        </div>
        <ScoreBar score={item.final_score} />
        {(item.mcq_score != null || item.mentor_score != null) && (
          <div className="flex gap-3 mt-2 text-xs text-gray-500">
            {item.mcq_score != null && <span>MCQ: <strong>{item.mcq_score.toFixed(1)}%</strong></span>}
            {item.mentor_score != null && <span>Mentor: <strong>{item.mentor_score.toFixed(1)}%</strong></span>}
          </div>
        )}
        {item.skills_demonstrated && item.skills_demonstrated.length > 0 && (
          <div className="mt-3 flex flex-wrap gap-1">
            {item.skills_demonstrated.slice(0, 4).map((skill, idx) => (
              <span key={idx} className="px-1.5 py-0.5 bg-indigo-50 text-indigo-700 text-xs rounded">{skill}</span>
            ))}
            {item.skills_demonstrated.length > 4 && (
              <span className="px-1.5 py-0.5 bg-gray-100 text-gray-500 text-xs rounded">+{item.skills_demonstrated.length - 4}</span>
            )}
          </div>
        )}
        {item.project_summary && (
          <p className="mt-3 text-xs text-gray-600 line-clamp-2 leading-relaxed">{item.project_summary}</p>
        )}
        {item.mentor_feedback_summary && (
          <p className="mt-2 text-xs text-blue-700 italic line-clamp-1">"{item.mentor_feedback_summary}"</p>
        )}
        <div className="mt-3 flex justify-between items-center text-xs text-gray-400">
          <span>{formatDate(item.completion_date)}</span>
          <button
            onClick={(e) => { e.stopPropagation(); onViewDetails(); }}
            className="text-blue-600 hover:text-blue-800 font-medium print:hidden"
          >View →</button>
        </div>
      </div>
    </div>
  );
}

function PortfolioItemRow({ item, onViewDetails }) {
  return (
    <div
      onClick={onViewDetails}
      className="bg-white rounded-xl shadow-sm border border-gray-100 hover:shadow-md hover:border-blue-200 transition-all cursor-pointer p-4 print:break-inside-avoid"
    >
      <div className="flex items-center gap-4">
        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-2 flex-wrap">
            <h3 className="font-semibold text-gray-900 text-sm">{item.task_title}</h3>
            <GradeBadge grade={item.grade} />
          </div>
          <div className="flex flex-wrap gap-2 mt-1 text-xs text-gray-500">
            <span>{item.task_domain}</span><span>·</span>
            <span>{item.task_difficulty}</span><span>·</span>
            <span>{item.task_type}</span><span>·</span>
            <span>{formatDate(item.completion_date)}</span>
          </div>
          {item.project_summary && (
            <p className="mt-1 text-xs text-gray-600 line-clamp-1">{item.project_summary}</p>
          )}
          {item.skills_demonstrated && item.skills_demonstrated.length > 0 && (
            <div className="flex flex-wrap gap-1 mt-1.5">
              {item.skills_demonstrated.slice(0, 5).map((skill, idx) => (
                <span key={idx} className="px-1.5 py-0.5 bg-indigo-50 text-indigo-700 text-xs rounded">{skill}</span>
              ))}
            </div>
          )}
        </div>
        <div className="text-right shrink-0 w-20">
          <p className={`text-xl font-bold ${getScoreColor(item.final_score)}`}>{item.final_score.toFixed(1)}%</p>
          <button
            onClick={(e) => { e.stopPropagation(); onViewDetails(); }}
            className="mt-1 text-blue-600 hover:text-blue-800 text-xs font-medium print:hidden"
          >View →</button>
        </div>
      </div>
    </div>
  );
}

// ── Main Page ─────────────────────────────────────────────────────────────────

export default function PortfolioPage() {
  const { user } = useAuth();
  const navigate = useNavigate();
  const [portfolio, setPortfolio] = useState(null);
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [editMode, setEditMode] = useState(false);
  const [formData, setFormData] = useState({});
  const [filterDomain, setFilterDomain] = useState('all');
  const [sortBy, setSortBy] = useState('recent');
  const [viewMode, setViewMode] = useState('grid');
  const [exporting, setExporting] = useState(false);

  useEffect(() => { loadPortfolio(); }, []);

  const loadPortfolio = async () => {
    try {
      setLoading(true);
      setError(null);
      const portfolioRes = await api.get('/tasks/portfolios/me/');
      if (portfolioRes.data.success) {
        setPortfolio(portfolioRes.data.data);
        setFormData({
          title: portfolioRes.data.data.title || '',
          bio: portfolioRes.data.data.bio || '',
          is_public: portfolioRes.data.data.is_public || false,
        });
        try {
          const statsRes = await api.get(`/tasks/portfolios/${portfolioRes.data.data.id}/stats/`);
          if (statsRes.data.success) setStats(statsRes.data.data);
        } catch (_) {}
      }
    } catch (err) {
      setError(err.response?.data?.message || 'Failed to load portfolio');
    } finally {
      setLoading(false);
    }
  };

  const handleUpdatePortfolio = async (e) => {
    e.preventDefault();
    try {
      const res = await api.put(`/tasks/portfolios/${portfolio.id}/update/`, formData);
      if (res.data.success) { setPortfolio(res.data.data); setEditMode(false); }
    } catch (err) {
      toast.error(err.response?.data?.errors || 'Failed to update portfolio');
    }
  };

  const handleFormChange = (e) => {
    const { name, value, type, checked } = e.target;
    setFormData((prev) => ({ ...prev, [name]: type === 'checkbox' ? checked : value }));
  };

  const handleExport = async () => {
    try {
      const res = await api.get(`/tasks/portfolios/${portfolio.id}/export/`);
      if (res.data.success) {
        const blob = new Blob([JSON.stringify(res.data.data, null, 2)], { type: 'application/json' });
        const url = URL.createObjectURL(blob);
        const link = document.createElement('a');
        link.href = url;
        link.download = `portfolio-${new Date().toISOString().slice(0, 10)}.json`;
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
        URL.revokeObjectURL(url);
      }
    } catch (_) { toast.error('Failed to export portfolio'); }
  };

  const handleDownloadPDF = async () => {
    if (!portfolio || exporting) return;
    try {
      setExporting(true);
      const res = await api.get(`/tasks/portfolios/${portfolio.id}/export-pdf/`, {
        responseType: 'blob',
      });
      const blob = new Blob([res.data], { type: 'application/pdf' });
      const url = URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      const safeName = (user?.name || 'Portfolio').replace(/\s+/g, '_');
      link.download = `VIHub_Portfolio_${safeName}_${new Date().toISOString().slice(0, 10)}.pdf`;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      URL.revokeObjectURL(url);
    } catch (_) {
      toast.error('Failed to generate PDF. Please try again.');
    } finally {
      setExporting(false);
    }
  };

  const getVisibleItems = () => {
    if (!portfolio?.items) return [];
    let items = [...portfolio.items];
    if (filterDomain !== 'all') items = items.filter((item) => item.task_domain === filterDomain);
    switch (sortBy) {
      case 'recent':       items.sort((a, b) => new Date(b.completion_date) - new Date(a.completion_date)); break;
      case 'oldest':       items.sort((a, b) => new Date(a.completion_date) - new Date(b.completion_date)); break;
      case 'highest-score': items.sort((a, b) => b.final_score - a.final_score); break;
      case 'lowest-score':  items.sort((a, b) => a.final_score - b.final_score); break;
    }
    return items;
  };

  if (loading) {
    return (
      <DashboardLayout>
        <div className="flex items-center justify-center py-20">
          <div className="text-center">
            <div className="animate-spin rounded-full h-10 w-10 border-b-2 border-blue-600 mx-auto mb-3" />
            <p className="text-gray-500 text-sm">Loading portfolio…</p>
          </div>
        </div>
      </DashboardLayout>
    );
  }

  if (error) {
    return (
      <DashboardLayout>
        <div className="max-w-2xl mx-auto bg-red-50 border border-red-200 rounded-xl p-6 mt-6">
          <p className="text-red-800">{error}</p>
          <button onClick={() => navigate('/student/dashboard')} className="mt-4 px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 text-sm">
            Back to Dashboard
          </button>
        </div>
      </DashboardLayout>
    );
  }

  if (!portfolio) {
    return (
      <DashboardLayout>
        <div className="max-w-2xl mx-auto bg-blue-50 border border-blue-200 rounded-xl p-8 text-center mt-6">
          <h2 className="text-xl font-bold text-blue-900 mb-2">Portfolio Empty</h2>
          <p className="text-blue-700 text-sm mb-4">Complete and get evaluated on tasks to start building your portfolio.</p>
          <button onClick={() => navigate('/student/tasks/my-tasks')} className="px-5 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 text-sm">
            View My Tasks
          </button>
        </div>
      </DashboardLayout>
    );
  }

  const domains = [...new Set(portfolio.items?.map((item) => item.task_domain) || [])];
  const visibleItems = getVisibleItems();
  const overview = portfolio.overview;

  return (
    <DashboardLayout>
    <div className="print:bg-white">
      {/* Header card */}
      <div className="bg-white border border-gray-100 rounded-xl shadow-sm p-6 mb-6">
        <div className="">
          <div className="flex justify-between items-start">
            <div className="flex items-start gap-4">
              {/* Profile picture */}
              {user?.profile_picture_url ? (
                <img
                  src={user.profile_picture_url}
                  alt={user.name}
                  className="w-16 h-16 rounded-full object-cover ring-2 ring-blue-200 shrink-0 print:w-12 print:h-12"
                />
              ) : (
                <div className="w-16 h-16 rounded-full bg-blue-100 text-blue-700 flex items-center justify-center text-2xl font-bold shrink-0 print:w-12 print:h-12">
                  {user?.name?.charAt(0)?.toUpperCase()}
                </div>
              )}
              <div>
              <h1 className="text-2xl font-bold text-gray-900">
                {portfolio.title || `${user?.name || 'My'}'s Portfolio`}
              </h1>
              {portfolio.student_name && <p className="text-sm text-gray-500 mt-0.5">by {portfolio.student_name}</p>}
              {portfolio.bio && <p className="mt-2 text-sm text-gray-600 max-w-xl">{portfolio.bio}</p>}
              {portfolio.is_public && (
                <span className="inline-block mt-2 px-2 py-0.5 bg-green-100 text-green-700 text-xs rounded-full">🌐 Public</span>
              )}
            </div>
            </div>
            <div className="flex gap-2 print:hidden">
              <button onClick={() => setEditMode(!editMode)} className="px-3 py-1.5 bg-blue-600 text-white rounded-lg hover:bg-blue-700 text-sm">
                {editMode ? 'Cancel' : 'Edit'}
              </button>
              <button onClick={handleExport} className="px-3 py-1.5 bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200 text-sm">Export JSON</button>
              <button
                onClick={handleDownloadPDF}
                disabled={exporting}
                className="px-3 py-1.5 bg-green-600 text-white rounded-lg hover:bg-green-700 text-sm flex items-center gap-1 disabled:opacity-60 disabled:cursor-not-allowed"
              >
                {exporting ? '⏳ Generating…' : '⬇ Download PDF'}
              </button>
            </div>
          </div>

          {/* Stats bar */}
          <div className="mt-5 grid grid-cols-2 sm:grid-cols-4 gap-3">
            <div className="bg-blue-50 rounded-lg p-3">
              <p className="text-xs text-gray-500">Total Items</p>
              <p className="text-xl font-bold text-blue-700">{portfolio.total_items}</p>
            </div>
            <div className="bg-green-50 rounded-lg p-3">
              <p className="text-xs text-gray-500">Average Score</p>
              <p className="text-xl font-bold text-green-700">{(portfolio.average_score || 0).toFixed(1)}%</p>
            </div>
            {stats && (
              <>
                <div className="bg-purple-50 rounded-lg p-3">
                  <p className="text-xs text-gray-500">Best Score</p>
                  <p className="text-xl font-bold text-purple-700">{(stats.max_score || 0).toFixed(1)}%</p>
                </div>
                <div className="bg-orange-50 rounded-lg p-3">
                  <p className="text-xs text-gray-500">Domains</p>
                  <p className="text-xl font-bold text-orange-700">{Object.keys(stats.by_domain || {}).length}</p>
                </div>
              </>
            )}
          </div>
        </div>
      </div>

      {/* Edit Form */}
      {editMode && (
        <div className="bg-white border border-gray-100 rounded-xl shadow-sm p-5 mb-5 print:hidden">
            <form onSubmit={handleUpdatePortfolio} className="space-y-4 max-w-xl">
              <div>
                <label className="block text-xs font-medium text-gray-700 mb-1">Title</label>
                <input type="text" name="title" value={formData.title} onChange={handleFormChange}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-blue-500 focus:border-transparent" />
              </div>
              <div>
                <label className="block text-xs font-medium text-gray-700 mb-1">Bio</label>
                <textarea name="bio" value={formData.bio} onChange={handleFormChange} rows={3}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  placeholder="Short professional summary…" />
              </div>
              <div className="flex items-center gap-2">
                <input type="checkbox" id="is_public" name="is_public" checked={formData.is_public} onChange={handleFormChange} className="h-4 w-4 text-blue-600 rounded" />
                <label htmlFor="is_public" className="text-xs text-gray-700">Make portfolio public</label>
              </div>
              <button type="submit" className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 text-sm">Save Changes</button>
            </form>
        </div>
      )}

      {/* Main Content */}
      <div>
        {/* Overview block */}
        {overview && <OverviewSection overview={overview} />}

        {portfolio.items && portfolio.items.length > 0 ? (
          <>
            {/* Filters */}
            <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-4 mb-5 print:hidden">
              <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
                <div>
                  <label className="block text-xs font-medium text-gray-700 mb-1">Domain</label>
                  <select value={filterDomain} onChange={(e) => setFilterDomain(e.target.value)}
                    className="w-full px-3 py-1.5 border border-gray-200 rounded-lg text-sm focus:ring-2 focus:ring-blue-500">
                    <option value="all">All Domains</option>
                    {domains.map((d) => <option key={d} value={d}>{d}</option>)}
                  </select>
                </div>
                <div>
                  <label className="block text-xs font-medium text-gray-700 mb-1">Sort By</label>
                  <select value={sortBy} onChange={(e) => setSortBy(e.target.value)}
                    className="w-full px-3 py-1.5 border border-gray-200 rounded-lg text-sm focus:ring-2 focus:ring-blue-500">
                    <option value="recent">Most Recent</option>
                    <option value="oldest">Oldest First</option>
                    <option value="highest-score">Highest Score</option>
                    <option value="lowest-score">Lowest Score</option>
                  </select>
                </div>
                <div>
                  <label className="block text-xs font-medium text-gray-700 mb-1">View</label>
                  <div className="flex gap-2">
                    {['grid', 'list'].map((mode) => (
                      <button key={mode} onClick={() => setViewMode(mode)}
                        className={`flex-1 px-3 py-1.5 rounded-lg border text-sm capitalize ${viewMode === mode ? 'bg-blue-600 border-blue-600 text-white' : 'bg-white border-gray-200 text-gray-600 hover:bg-gray-50'}`}>
                        {mode}
                      </button>
                    ))}
                  </div>
                </div>
              </div>
            </div>

            {/* Grade distribution chips */}
            {stats?.grade_distribution && (
              <div className="flex flex-wrap gap-2 mb-5 print:hidden">
                {Object.entries(stats.grade_distribution)
                  .filter(([, count]) => count > 0)
                  .map(([grade, count]) => (
                    <span key={grade} className={`px-2.5 py-1 text-xs font-semibold rounded-full ${GRADE_STYLES[grade] || 'bg-gray-200 text-gray-700'}`}>
                      {grade}: {count}
                    </span>
                  ))}
              </div>
            )}

            {viewMode === 'grid' ? (
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5">
                {visibleItems.map((item) => (
                  <PortfolioItemCard key={item.id} item={item}
                    onViewDetails={() => navigate(`/student/portfolio/items/${item.id}`)} />
                ))}
              </div>
            ) : (
              <div className="space-y-3">
                {visibleItems.map((item) => (
                  <PortfolioItemRow key={item.id} item={item}
                    onViewDetails={() => navigate(`/student/portfolio/items/${item.id}`)} />
                ))}
              </div>
            )}
          </>
        ) : (
          <div className="text-center py-16">
            <p className="text-gray-400 text-lg mb-1">No portfolio items yet</p>
            <p className="text-gray-400 text-sm">Complete tasks to build your portfolio</p>
          </div>
        )}
      </div>

      {/* Print-only footer */}
      <div className="hidden print:block pb-4 border-t mt-6 pt-4">
        <p className="text-xs text-gray-400 text-center">
          Generated from Virtual Internship Hub · {new Date().toLocaleDateString()}
        </p>
      </div>
    </div>
    </DashboardLayout>
  );
}
