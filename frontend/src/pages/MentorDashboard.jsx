import { useState, useEffect } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import DashboardLayout from '../components/DashboardLayout';
import { useAuth } from '../contexts/AuthContext';
import { profileService, mentorService, analyticsService } from '../services/endpoints';

export default function MentorDashboard() {
  const { user } = useAuth();
  const navigate = useNavigate();
  const [profile, setProfile] = useState(null);
  const [assignedStudents, setAssignedStudents] = useState([]);
  const [pendingReviews, setPendingReviews] = useState([]);
  const [analytics, setAnalytics] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    loadDashboard();
  }, []);

  const loadDashboard = async () => {
    try {
      setLoading(true);
      const [profileRes, studentsRes, reviewsRes] = await Promise.all([
        profileService.getMentorProfile(),
        mentorService.getAssignedStudents(),
        mentorService.getPendingReviews(),
      ]);
      if (profileRes.data.success) setProfile(profileRes.data.data);
      if (studentsRes.data.success) setAssignedStudents(studentsRes.data.data);
      if (reviewsRes.data.success) setPendingReviews(reviewsRes.data.data);

      // Analytics — non-critical
      try {
        const analyticsRes = await analyticsService.getMentorAnalytics();
        if (analyticsRes.data.success) setAnalytics(analyticsRes.data.data);
      } catch (_) {}
    } catch (err) {
      setError('Failed to load dashboard data');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const avgScore = analytics?.average_task_score ?? 0;
  const totalReviewed = analytics?.total_tasks_reviewed ?? 0;
  const needsAttention = assignedStudents.filter(s => s.pending_review_count > 0).length;
  const capacity = profile ? Math.round((assignedStudents.length / (profile.max_students || 10)) * 100) : 0;

  return (
    <DashboardLayout>
      {/* Page Header */}
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900">
          Welcome, {user?.name} 👨‍🏫
        </h1>
        <p className="text-gray-500 mt-1">
          {profile?.expertise_domains?.join(', ') || 'Mentor'} · Mentor Dashboard
        </p>
      </div>

      {error && (
        <div className="mb-6 p-4 bg-red-50 border border-red-200 rounded-lg text-red-700 text-sm">{error}</div>
      )}

      {/* ── Stat Row ── */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
        {[
          { label: 'Assigned Students', value: loading ? '—' : assignedStudents.length, icon: '👥', sub: `${capacity}% capacity` },
          { label: 'Pending Reviews', value: loading ? '—' : pendingReviews.length, icon: '📋', sub: pendingReviews.length > 0 ? 'Action needed' : 'All clear!', warn: pendingReviews.length > 0 },
          { label: 'Tasks Reviewed', value: loading ? '—' : totalReviewed, icon: '✅', sub: 'Total evaluated' },
          { label: 'Avg Task Score', value: loading ? '—' : `${avgScore.toFixed(1)}%`, icon: '📊', sub: 'Across your students' },
        ].map(stat => (
          <div key={stat.label} className={`bg-white rounded-xl border ${stat.warn ? 'border-yellow-300 bg-yellow-50' : 'border-gray-200'} p-5`}>
            <div className="text-2xl mb-2">{stat.icon}</div>
            <div className="text-2xl font-bold text-gray-900">{stat.value}</div>
            <div className="text-xs font-medium text-gray-600 mt-1">{stat.label}</div>
            <div className={`text-xs mt-1 ${stat.warn ? 'text-yellow-700 font-semibold' : 'text-gray-400'}`}>{stat.sub}</div>
          </div>
        ))}
      </div>

      {/* ── Main Grid ── */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">

        {/* LEFT: Pending Reviews */}
        <div className="lg:col-span-2 space-y-6">

          {/* Pending Reviews Panel */}
          <div className="bg-white rounded-xl border border-gray-200 overflow-hidden">
            <div className="flex items-center justify-between px-6 py-4 border-b border-gray-100">
              <div>
                <h2 className="font-semibold text-gray-900">📋 Pending Reviews</h2>
                <p className="text-xs text-gray-500 mt-0.5">{pendingReviews.length} submission{pendingReviews.length !== 1 ? 's' : ''} awaiting your review</p>
              </div>
              {pendingReviews.length > 0 && (
                <Link to="/mentor/reviews" className="text-sm font-medium text-blue-600 hover:text-blue-700">
                  View all →
                </Link>
              )}
            </div>
            <div className="divide-y divide-gray-100">
              {loading ? (
                [...Array(3)].map((_, i) => (
                  <div key={i} className="px-6 py-4">
                    <div className="h-5 bg-gray-100 rounded animate-pulse w-3/4 mb-2" />
                    <div className="h-4 bg-gray-100 rounded animate-pulse w-1/2" />
                  </div>
                ))
              ) : pendingReviews.length === 0 ? (
                <div className="px-6 py-10 text-center">
                  <div className="text-3xl mb-2">✅</div>
                  <p className="text-sm font-medium text-gray-700">All caught up!</p>
                  <p className="text-xs text-gray-400 mt-1">No pending reviews right now.</p>
                </div>
              ) : (
                pendingReviews.slice(0, 6).map(review => (
                  <div
                    key={review.id}
                    className="px-6 py-4 hover:bg-yellow-50 cursor-pointer transition-colors"
                    onClick={() => navigate(`/mentor/reviews/${review.id}`)}
                  >
                    <div className="flex items-start justify-between">
                      <div className="flex-1 min-w-0">
                        <p className="font-medium text-gray-900 truncate">{review.task__title}</p>
                        <p className="text-xs text-gray-500 mt-0.5">
                          by <span className="font-medium text-gray-700">{review.student__name}</span>
                          {review.completed_at && (
                            <span> · {new Date(review.completed_at).toLocaleDateString()}</span>
                          )}
                        </p>
                      </div>
                      <span className="ml-3 flex-shrink-0 px-2.5 py-1 bg-orange-100 text-orange-700 text-xs font-medium rounded-full">
                        {review.task__domain}
                      </span>
                    </div>
                  </div>
                ))
              )}
            </div>
          </div>

          {/* My Students Panel */}
          <div className="bg-white rounded-xl border border-gray-200 overflow-hidden">
            <div className="flex items-center justify-between px-6 py-4 border-b border-gray-100">
              <div>
                <h2 className="font-semibold text-gray-900">👥 My Students</h2>
                <p className="text-xs text-gray-500 mt-0.5">{assignedStudents.length} / {profile?.max_students || 10} capacity</p>
              </div>
              <div className="flex gap-2">
                <Link to="/mentor/select-students" className="px-3 py-1.5 bg-gray-900 text-white text-xs font-medium rounded-lg hover:bg-gray-700 transition">
                  + Add Students
                </Link>
                {assignedStudents.length > 4 && (
                  <Link to="/mentor/students" className="text-sm font-medium text-blue-600 hover:text-blue-700">
                    View all →
                  </Link>
                )}
              </div>
            </div>
            <div className="divide-y divide-gray-100">
              {loading ? (
                [...Array(3)].map((_, i) => (
                  <div key={i} className="px-6 py-4">
                    <div className="h-5 bg-gray-100 rounded animate-pulse w-3/4 mb-2" />
                    <div className="h-4 bg-gray-100 rounded animate-pulse w-1/2" />
                  </div>
                ))
              ) : assignedStudents.length === 0 ? (
                <div className="px-6 py-10 text-center">
                  <div className="text-3xl mb-2">👥</div>
                  <p className="text-sm font-medium text-gray-700">No students yet</p>
                  <p className="text-xs text-gray-400 mt-1">Browse and add students from your domain.</p>
                  <Link to="/mentor/select-students" className="inline-block mt-3 px-4 py-2 bg-gray-900 text-white text-xs font-medium rounded-lg hover:bg-gray-700">
                    Select Students →
                  </Link>
                </div>
              ) : (
                assignedStudents.slice(0, 5).map(student => (
                  <div
                    key={student.student_id}
                    className="px-6 py-4 hover:bg-gray-50 cursor-pointer transition-colors"
                    onClick={() => navigate(`/mentor/students/${student.student_id}`)}
                  >
                    <div className="flex items-center justify-between">
                      <div className="flex-1 min-w-0">
                        <div className="flex items-center gap-2">
                          <p className="font-medium text-gray-900">{student.student_name}</p>
                          {student.pending_review_count > 0 && (
                            <span className="px-2 py-0.5 bg-yellow-100 text-yellow-700 text-xs font-semibold rounded-full">
                              {student.pending_review_count} review{student.pending_review_count !== 1 ? 's' : ''}
                            </span>
                          )}
                          {student.cluster_label && (
                            <span className={`px-2 py-0.5 text-xs font-medium rounded-full ${
                              student.cluster_label === 'Expert'     ? 'bg-yellow-100 text-yellow-700' :
                              student.cluster_label === 'Competent'  ? 'bg-green-100 text-green-700'  :
                              student.cluster_label === 'Developing' ? 'bg-blue-100 text-blue-700'    :
                                                                       'bg-gray-100 text-gray-600'
                            }`}>
                              {student.cluster_display_name || student.cluster_label}
                            </span>
                          )}
                        </div>
                        <p className="text-xs text-gray-500 mt-0.5">
                          {student.strongest_domain || 'No domain yet'} · {student.completed_tasks_count} tasks done
                        </p>
                      </div>
                      <div className="ml-4 text-right flex-shrink-0">
                        <div className="text-sm font-bold text-gray-900">{Math.round(student.progress_score || 0)}%</div>
                        <div className="text-xs text-gray-400">progress</div>
                      </div>
                    </div>
                    {/* Progress bar */}
                    <div className="mt-2 w-full bg-gray-100 rounded-full h-1.5">
                      <div
                        className="bg-gray-700 h-1.5 rounded-full"
                        style={{ width: `${Math.min(100, student.progress_score || 0)}%` }}
                      />
                    </div>
                  </div>
                ))
              )}
            </div>
          </div>
        </div>

        {/* RIGHT: Profile + Quick Actions */}
        <div className="space-y-5">
          {/* Mentor Profile Card */}
          <div className="bg-white rounded-xl border border-gray-200 p-5">
            <div className="flex items-center gap-3 mb-4">
              <div className="w-12 h-12 bg-gray-900 rounded-full flex items-center justify-center text-white font-bold text-lg">
                {user?.name?.charAt(0)?.toUpperCase()}
              </div>
              <div>
                <p className="font-semibold text-gray-900">{user?.name}</p>
                <p className="text-xs text-gray-500">{user?.email}</p>
              </div>
            </div>
            {profile && (
              <div className="space-y-2">
                <div className="flex flex-wrap gap-1.5">
                  {(profile.expertise_domains || []).map(d => (
                    <span key={d} className="px-2.5 py-1 bg-gray-100 text-gray-700 text-xs font-medium rounded-full">{d}</span>
                  ))}
                </div>
                {profile.bio && (
                  <p className="text-xs text-gray-500 mt-2 line-clamp-3">{profile.bio}</p>
                )}
                {profile.rating > 0 && (
                  <p className="text-xs text-yellow-600 font-medium mt-1">⭐ {profile.rating.toFixed(1)} rating</p>
                )}
              </div>
            )}
          </div>

          {/* Quick Actions */}
          <div className="bg-white rounded-xl border border-gray-200 p-5">
            <h3 className="font-semibold text-gray-900 mb-3 text-sm">Quick Actions</h3>
            <div className="space-y-2">
              {[
                { label: '📋 Review Submissions', to: '/mentor/reviews', color: 'bg-yellow-50 hover:bg-yellow-100 text-yellow-800 border-yellow-200', badge: pendingReviews.length },
                { label: '👥 My Students', to: '/mentor/students', color: 'bg-blue-50 hover:bg-blue-100 text-blue-800 border-blue-200' },
                { label: '➕ Select Students', to: '/mentor/select-students', color: 'bg-green-50 hover:bg-green-100 text-green-800 border-green-200' },
                { label: '📈 Analytics', to: '/mentor/analytics', color: 'bg-purple-50 hover:bg-purple-100 text-purple-800 border-purple-200' },
                { label: '💬 AI Assistant', to: '/mentor/chat', color: 'bg-gray-50 hover:bg-gray-100 text-gray-800 border-gray-200' },
              ].map(action => (
                <Link
                  key={action.to}
                  to={action.to}
                  className={`flex items-center justify-between w-full px-4 py-2.5 text-sm font-medium rounded-lg border transition-colors ${action.color}`}
                >
                  <span>{action.label}</span>
                  {action.badge > 0 && (
                    <span className="px-2 py-0.5 bg-red-500 text-white text-xs rounded-full">{action.badge}</span>
                  )}
                </Link>
              ))}
            </div>
          </div>

          {/* Domain Distribution from Analytics */}
          {analytics?.domain_distribution && Object.keys(analytics.domain_distribution).length > 0 && (
            <div className="bg-white rounded-xl border border-gray-200 p-5">
              <h3 className="font-semibold text-gray-900 mb-3 text-sm">Students by Domain</h3>
              <div className="space-y-2">
                {Object.entries(analytics.domain_distribution).slice(0, 5).map(([domain, count]) => (
                  <div key={domain} className="flex items-center justify-between text-xs">
                    <span className="text-gray-600 truncate">{domain}</span>
                    <span className="font-semibold text-gray-900 ml-2">{count}</span>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      </div>
    </DashboardLayout>
  );
}

