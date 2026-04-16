import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import { apiClient, API_BASE_URL } from '../services/api';

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
  const [viewMode, setViewMode] = useState('grid'); // 'grid' or 'list'

  // Fetch portfolio data
  useEffect(() => {
    loadPortfolio();
  }, []);

  const loadPortfolio = async () => {
    try {
      setLoading(true);
      setError(null);

      // Fetch portfolio
      const portfolioRes = await apiClient.get('/api/tasks/portfolios/me/');
      if (portfolioRes.data.success) {
        setPortfolio(portfolioRes.data.data);
        setFormData({
          title: portfolioRes.data.data.title || '',
          bio: portfolioRes.data.data.bio || '',
          is_public: portfolioRes.data.data.is_public || false,
        });

        // Fetch stats
        try {
          const statsRes = await apiClient.get(
            `/api/tasks/portfolios/${portfolioRes.data.data.id}/stats/`
          );
          if (statsRes.data.success) {
            setStats(statsRes.data.data);
          }
        } catch (err) {
          console.error('Error loading stats:', err);
        }
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
      const res = await apiClient.put(
        `/api/tasks/portfolios/${portfolio.id}/update/`,
        formData
      );
      if (res.data.success) {
        setPortfolio(res.data.data);
        setEditMode(false);
        alert('Portfolio updated successfully');
      }
    } catch (err) {
      alert(err.response?.data?.errors || 'Failed to update portfolio');
    }
  };

  const handleFormChange = (e) => {
    const { name, value, type, checked } = e.target;
    setFormData((prev) => ({
      ...prev,
      [name]: type === 'checkbox' ? checked : value,
    }));
  };

  const handleExport = async () => {
    try {
      const res = await apiClient.get(
        `/api/tasks/portfolios/${portfolio.id}/export/`
      );
      if (res.data.success) {
        // Download JSON file
        const dataStr = JSON.stringify(res.data.data, null, 2);
        const dataBlob = new Blob([dataStr], { type: 'application/json' });
        const url = URL.createObjectURL(dataBlob);
        const link = document.createElement('a');
        link.href = url;
        link.download = `portfolio-${new Date().toISOString().slice(0, 10)}.json`;
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
        URL.revokeObjectURL(url);
      }
    } catch (err) {
      alert('Failed to export portfolio');
    }
  };

  const handlePrint = () => {
    window.print();
  };

  // Filter and sort items
  const getVisibleItems = () => {
    if (!portfolio?.items) return [];

    let items = [...portfolio.items];

    // Filter by domain
    if (filterDomain !== 'all') {
      items = items.filter((item) => item.task_domain === filterDomain);
    }

    // Sort
    switch (sortBy) {
      case 'recent':
        items.sort((a, b) => new Date(b.completion_date) - new Date(a.completion_date));
        break;
      case 'oldest':
        items.sort((a, b) => new Date(a.completion_date) - new Date(b.completion_date));
        break;
      case 'highest-score':
        items.sort((a, b) => b.final_score - a.final_score);
        break;
      case 'lowest-score':
        items.sort((a, b) => a.final_score - b.final_score);
        break;
      default:
        break;
    }

    return items;
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
          <p className="text-gray-600">Loading portfolio...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen bg-gray-50 p-4">
        <div className="max-w-7xl mx-auto">
          <div className="bg-red-50 border border-red-200 rounded-lg p-4">
            <p className="text-red-800">{error}</p>
            <button
              onClick={() => navigate('/student/dashboard')}
              className="mt-4 px-4 py-2 bg-red-600 text-white rounded hover:bg-red-700"
            >
              Back to Dashboard
            </button>
          </div>
        </div>
      </div>
    );
  }

  if (!portfolio) {
    return (
      <div className="min-h-screen bg-gray-50 p-4">
        <div className="max-w-7xl mx-auto">
          <div className="bg-blue-50 border border-blue-200 rounded-lg p-8 text-center">
            <h2 className="text-2xl font-bold text-blue-900 mb-2">Portfolio Empty</h2>
            <p className="text-blue-800 mb-4">
              Complete and get evaluated on tasks to start building your portfolio.
            </p>
            <button
              onClick={() => navigate('/student/my-tasks')}
              className="px-6 py-2 bg-blue-600 text-white rounded hover:bg-blue-700"
            >
              View Available Tasks
            </button>
          </div>
        </div>
      </div>
    );
  }

  const domains = [...new Set(portfolio.items?.map((item) => item.task_domain) || [])];
  const visibleItems = getVisibleItems();

  return (
    <div className="min-h-screen bg-gray-50 print:bg-white">
      {/* Header */}
      <div className="bg-white shadow print:shadow-none print:border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          <div className="flex justify-between items-start">
            <div>
              <h1 className="text-3xl font-bold text-gray-900">{portfolio.title}</h1>
              {portfolio.student_name && (
                <p className="mt-1 text-gray-500">by {portfolio.student_name}</p>
              )}
              {portfolio.bio && <p className="mt-2 text-gray-600">{portfolio.bio}</p>}
              {portfolio.is_public && (
                <span className="inline-block mt-2 px-3 py-1 bg-green-100 text-green-800 text-sm rounded-full">
                  🌐 Public
                </span>
              )}
            </div>
            <div className="flex gap-2 print:hidden">
              <button
                onClick={() => setEditMode(!editMode)}
                className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 text-sm"
              >
                {editMode ? 'Cancel' : 'Edit'}
              </button>
              <button
                onClick={handleExport}
                className="px-4 py-2 bg-green-600 text-white rounded hover:bg-green-700 text-sm"
              >
                Export
              </button>
              <button
                onClick={handlePrint}
                className="px-4 py-2 bg-gray-600 text-white rounded hover:bg-gray-700 text-sm"
              >
                Print
              </button>
            </div>
          </div>

          {/* Stats Overview */}
          <div className="mt-6 grid grid-cols-2 sm:grid-cols-4 gap-4">
            <div className="bg-blue-50 rounded-lg p-4">
              <p className="text-gray-600 text-sm">Total Items</p>
              <p className="text-2xl font-bold text-blue-600">{portfolio.total_items}</p>
            </div>
            <div className="bg-green-50 rounded-lg p-4">
              <p className="text-gray-600 text-sm">Average Score</p>
              <p className="text-2xl font-bold text-green-600">
                {portfolio.average_score.toFixed(1)}%
              </p>
            </div>
            {stats && (
              <>
                <div className="bg-purple-50 rounded-lg p-4">
                  <p className="text-gray-600 text-sm">Highest Score</p>
                  <p className="text-2xl font-bold text-purple-600">{stats.max_score}%</p>
                </div>
                <div className="bg-orange-50 rounded-lg p-4">
                  <p className="text-gray-600 text-sm">Domains</p>
                  <p className="text-2xl font-bold text-orange-600">{Object.keys(stats.by_domain || {}).length}</p>
                </div>
              </>
            )}
          </div>
        </div>
      </div>

      {/* Edit Mode */}
      {editMode && (
        <div className="bg-white border-b shadow">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
            <form onSubmit={handleUpdatePortfolio} className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Portfolio Title
                </label>
                <input
                  type="text"
                  name="title"
                  value={formData.title}
                  onChange={handleFormChange}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  placeholder="Your Portfolio Title"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Bio / Summary
                </label>
                <textarea
                  name="bio"
                  value={formData.bio}
                  onChange={handleFormChange}
                  rows="3"
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  placeholder="Write a short bio about yourself..."
                />
              </div>

              <div className="flex items-center gap-3">
                <input
                  type="checkbox"
                  id="is_public"
                  name="is_public"
                  checked={formData.is_public}
                  onChange={handleFormChange}
                  className="h-4 w-4 text-blue-600 rounded"
                />
                <label htmlFor="is_public" className="text-sm text-gray-700">
                  Make portfolio public (visible to everyone)
                </label>
              </div>

              <button
                type="submit"
                className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700"
              >
                Save Changes
              </button>
            </form>
          </div>
        </div>
      )}

      {/* Main Content */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {portfolio.items && portfolio.items.length > 0 ? (
          <>
            {/* Filters */}
            <div className="bg-white rounded-lg shadow-sm p-4 mb-6 print:hidden">
              <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Filter by Domain
                  </label>
                  <select
                    value={filterDomain}
                    onChange={(e) => setFilterDomain(e.target.value)}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                  >
                    <option value="all">All Domains</option>
                    {domains.map((domain) => (
                      <option key={domain} value={domain}>
                        {domain}
                      </option>
                    ))}
                  </select>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Sort By
                  </label>
                  <select
                    value={sortBy}
                    onChange={(e) => setSortBy(e.target.value)}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                  >
                    <option value="recent">Most Recent</option>
                    <option value="oldest">Oldest First</option>
                    <option value="highest-score">Highest Score</option>
                    <option value="lowest-score">Lowest Score</option>
                  </select>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    View
                  </label>
                  <div className="flex gap-2">
                    <button
                      onClick={() => setViewMode('grid')}
                      className={`flex-1 px-3 py-2 rounded-lg border ${
                        viewMode === 'grid'
                          ? 'bg-blue-100 border-blue-300'
                          : 'bg-white border-gray-300'
                      }`}
                    >
                      Grid
                    </button>
                    <button
                      onClick={() => setViewMode('list')}
                      className={`flex-1 px-3 py-2 rounded-lg border ${
                        viewMode === 'list'
                          ? 'bg-blue-100 border-blue-300'
                          : 'bg-white border-gray-300'
                      }`}
                    >
                      List
                    </button>
                  </div>
                </div>
              </div>
            </div>

            {/* Items Display */}
            {viewMode === 'grid' ? (
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                {visibleItems.map((item) => (
                  <PortfolioItemCard
                    key={item.id}
                    item={item}
                    onViewDetails={() => navigate(`/student/portfolio/items/${item.id}`)}
                  />
                ))}
              </div>
            ) : (
              <div className="space-y-4">
                {visibleItems.map((item) => (
                  <PortfolioItemRow
                    key={item.id}
                    item={item}
                    onViewDetails={() => navigate(`/student/portfolio/items/${item.id}`)}
                  />
                ))}
              </div>
            )}
          </>
        ) : (
          <div className="text-center py-12">
            <p className="text-gray-500 text-lg">No portfolio items yet</p>
            <p className="text-gray-400 mt-2">Complete tasks to build your portfolio</p>
          </div>
        )}
      </div>
    </div>
  );
}

function PortfolioItemCard({ item, onViewDetails }) {
  return (
    <div
      onClick={onViewDetails}
      className="bg-white rounded-lg shadow hover:shadow-lg transition-shadow cursor-pointer overflow-hidden print:page-break-inside-avoid"
    >
      {item.is_featured && (
        <div className="bg-yellow-100 px-4 py-2 text-sm font-semibold text-yellow-800">
          ⭐ Featured
        </div>
      )}

      <div className="p-6">
        <div className="flex items-start justify-between mb-3">
          <div>
            <h3 className="text-lg font-bold text-gray-900">{item.task_title}</h3>
            <div className="flex gap-2 mt-2">
              <span className="px-2 py-1 bg-blue-100 text-blue-800 text-xs rounded">
                {item.task_domain}
              </span>
              <span className="px-2 py-1 bg-gray-100 text-gray-800 text-xs rounded">
                {item.task_difficulty}
              </span>
            </div>
          </div>
          <div className="text-right">
            <p className="text-2xl font-bold text-green-600">{item.final_score}%</p>
            <p className="text-xs text-gray-500">Final Score</p>
          </div>
        </div>

        {item.skills_demonstrated && item.skills_demonstrated.length > 0 && (
          <div className="mb-3">
            <p className="text-xs font-semibold text-gray-600 mb-2">Skills</p>
            <div className="flex flex-wrap gap-1">
              {item.skills_demonstrated.slice(0, 3).map((skill, idx) => (
                <span key={idx} className="px-2 py-1 bg-purple-100 text-purple-800 text-xs rounded">
                  {skill}
                </span>
              ))}
              {item.skills_demonstrated.length > 3 && (
                <span className="px-2 py-1 bg-purple-100 text-purple-800 text-xs rounded">
                  +{item.skills_demonstrated.length - 3}
                </span>
              )}
            </div>
          </div>
        )}

        <p className="text-sm text-gray-600 line-clamp-2 mb-3">
          {item.project_summary}
        </p>

        <div className="flex justify-between text-sm text-gray-500">
          <span>{new Date(item.completion_date).toLocaleDateString()}</span>
          <button
            onClick={(e) => {
              e.stopPropagation();
              onViewDetails();
            }}
            className="text-blue-600 hover:text-blue-800 font-medium print:hidden"
          >
            View →
          </button>
        </div>
      </div>
    </div>
  );
}

function PortfolioItemRow({ item, onViewDetails }) {
  return (
    <div
      onClick={onViewDetails}
      className="bg-white rounded-lg shadow hover:shadow-md transition-shadow cursor-pointer p-4 print:page-break-inside-avoid flex items-center justify-between"
    >
      <div className="flex-1">
        <h3 className="font-bold text-gray-900">{item.task_title}</h3>
        <div className="flex gap-2 mt-2">
          <span className="text-xs text-gray-600">{item.task_domain}</span>
          <span className="text-xs text-gray-600">{item.task_difficulty}</span>
          <span className="text-xs text-gray-600">
            {new Date(item.completion_date).toLocaleDateString()}
          </span>
        </div>
      </div>

      <div className="text-right">
        <p className="text-xl font-bold text-green-600">{item.final_score}%</p>
        <button
          onClick={(e) => {
            e.stopPropagation();
            onViewDetails();
          }}
          className="mt-2 text-blue-600 hover:text-blue-800 font-medium text-sm print:hidden"
        >
          View →
        </button>
      </div>
    </div>
  );
}
