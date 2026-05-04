import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import { mentorService } from '../services/endpoints';
import { FiMessageSquare, FiArrowRight } from 'react-icons/fi';
import DashboardLayout from '../components/DashboardLayout';

export default function MentorPendingReviewsPage() {
  const { user } = useAuth();
  const navigate = useNavigate();
  const [reviews, setReviews] = useState([]);
  const [filteredReviews, setFilteredReviews] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [filterDomain, setFilterDomain] = useState('all');
  const [sortBy, setSortBy] = useState('recent');

  const DOMAINS = [
    'Graphic Design',
    'Content Writing',
    'Programming',
    'Freelancing',
    'E-Commerce',
    'QuickBooks',
    'AutoCAD',
    'Data Analytics',
    'Digital Marketing',
    'WordPress',
  ];

  useEffect(() => {
    if (user?.role !== 'Mentor') {
      navigate('/');
      return;
    }
    fetchPendingReviews();
  }, [user, navigate]);

  const fetchPendingReviews = async () => {
    try {
      setLoading(true);
      const response = await mentorService.getPendingReviews();
      if (response.data.success) {
        setReviews(response.data.data);
        setFilteredReviews(response.data.data);
      } else {
        setError(response.data.error?.message || 'Failed to load reviews');
      }
    } catch (err) {
      setError('Error loading reviews');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const applyFiltersAndSort = () => {
    let filtered = reviews;

    // Apply domain filter
    if (filterDomain !== 'all') {
      filtered = filtered.filter(r => r.task__domain === filterDomain);
    }

    // Apply sort
    if (sortBy === 'recent') {
      filtered.sort((a, b) => new Date(b.completed_at) - new Date(a.completed_at));
    } else if (sortBy === 'oldest') {
      filtered.sort((a, b) => new Date(a.completed_at) - new Date(b.completed_at));
    } else if (sortBy === 'name') {
      filtered.sort((a, b) => a.task__title.localeCompare(b.task__title));
    }

    setFilteredReviews(filtered);
  };

  useEffect(() => {
    applyFiltersAndSort();
  }, [filterDomain, sortBy, reviews]);

  return (
    <DashboardLayout>
      <div className="max-w-5xl mx-auto pb-8">
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900 mb-2">Pending Task Reviews</h1>
          <p className="text-gray-600">
            {reviews.length} task{reviews.length !== 1 ? 's' : ''} awaiting your review.
          </p>
        </div>

        {error && (
          <div className="mb-6 p-4 bg-red-50 border border-red-200 rounded text-red-700">
            {error}
          </div>
        )}

        {loading ? (
          <div className="flex items-center justify-center py-16">
            <div className="text-center">
              <div className="inline-block w-8 h-8 border-4 border-gray-200 border-t-gray-900 rounded-full animate-spin mb-4"></div>
              <p className="text-gray-600">Loading reviews...</p>
            </div>
          </div>
        ) : reviews.length === 0 ? (
          <div className="bg-white rounded-lg p-8 text-center border border-gray-200">
            <FiMessageSquare className="mx-auto mb-4 text-gray-400" size={48} />
            <p className="text-gray-600 mb-4">No pending reviews at this time.</p>
            <button
              onClick={() => navigate('/mentor/dashboard')}
              className="px-4 py-2 bg-gray-900 text-white rounded-lg hover:bg-gray-800"
            >
              Back to Dashboard
            </button>
          </div>
        ) : (
          <>
            {/* Filters */}
            <div className="bg-white rounded-lg p-6 mb-6 border border-gray-200">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Filter by Domain
                  </label>
                  <select
                    value={filterDomain}
                    onChange={(e) => setFilterDomain(e.target.value)}
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-gray-900"
                  >
                    <option value="all">All Domains</option>
                    {DOMAINS.map(domain => (
                      <option key={domain} value={domain}>{domain}</option>
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
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-gray-900"
                  >
                    <option value="recent">Most Recent</option>
                    <option value="oldest">Oldest First</option>
                    <option value="name">Task Name (A-Z)</option>
                  </select>
                </div>
              </div>
            </div>

            {/* Reviews List */}
            <div className="space-y-4">
              {filteredReviews.map(review => (
                <div
                  key={review.id}
                  className="bg-white rounded-lg border border-yellow-200 bg-yellow-50 p-6 hover:shadow-md transition"
                >
                  <div className="flex items-start justify-between gap-4">
                    <div className="flex-1">
                      <div className="flex items-center gap-3 mb-2">
                        <FiMessageSquare className="text-yellow-600" size={22} />
                        <h3 className="text-lg font-bold text-gray-900">{review.task__title}</h3>
                      </div>

                      <p className="text-sm text-gray-600 mb-3">
                        From: <span className="font-medium">{review.student__name}</span>
                      </p>

                      <div className="flex gap-6 text-sm text-gray-600">
                        <div>
                          <p className="text-xs text-gray-600 uppercase font-medium">Domain</p>
                          <p className="font-semibold text-gray-900 mt-1">{review.task__domain}</p>
                        </div>
                        <div>
                          <p className="text-xs text-gray-600 uppercase font-medium">Status</p>
                          <p className="font-semibold text-gray-900 mt-1 capitalize">{review.status}</p>
                        </div>
                        <div>
                          <p className="text-xs text-gray-600 uppercase font-medium">Progress</p>
                          <p className="font-semibold text-gray-900 mt-1">{review.progress_percentage}%</p>
                        </div>
                        <div>
                          <p className="text-xs text-gray-600 uppercase font-medium">Completed</p>
                          <p className="font-semibold text-gray-900 mt-1">
                            {new Date(review.completed_at).toLocaleDateString()}
                          </p>
                        </div>
                      </div>
                    </div>

                    <button
                      onClick={() => navigate(`/mentor/reviews/${review.id}`)}
                      className="px-6 py-3 bg-gray-900 text-white rounded-lg hover:bg-gray-800 transition whitespace-nowrap flex items-center gap-2 font-medium"
                    >
                      Review <FiArrowRight size={18} />
                    </button>
                  </div>
                </div>
              ))}
            </div>

            {filteredReviews.length === 0 && (
              <div className="bg-white rounded-lg p-8 text-center border border-gray-200">
                <p className="text-gray-600">No reviews match your filters.</p>
              </div>
            )}
          </>
        )}
      </div>
    </DashboardLayout>
  );
}
