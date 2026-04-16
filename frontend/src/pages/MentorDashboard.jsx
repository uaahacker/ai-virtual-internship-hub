import { useState, useEffect } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import DashboardLayout from '../components/DashboardLayout';
import MentorProfileCard from '../components/MentorProfileCard';
import { useAuth } from '../contexts/AuthContext';
import { profileService, mentorService } from '../services/endpoints';
import { Card, CardHeader, CardBody, SectionCard, StatCard, Badge } from '../components/CardComponents';
import { EmptyState, Alert, LinearProgress } from '../components/ProgressAndUtilityComponents';

export default function MentorDashboard() {
  const { user } = useAuth();
  const navigate = useNavigate();
  const [profile, setProfile] = useState(null);
  const [assignedStudents, setAssignedStudents] = useState([]);
  const [pendingReviews, setPendingReviews] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    loadDashboardData();
  }, []);

  const loadDashboardData = async () => {
    try {
      setLoading(true);
      
      const profileRes = await profileService.getMentorProfile();
      setProfile(profileRes.data.data);
      
      const studentsRes = await mentorService.getAssignedStudents();
      if (studentsRes.data.success) {
        setAssignedStudents(studentsRes.data.data);
      }
      
      const reviewsRes = await mentorService.getPendingReviews();
      if (reviewsRes.data.success) {
        setPendingReviews(reviewsRes.data.data);
      }
    } catch (err) {
      setError('Failed to load dashboard data');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <DashboardLayout>
      {/* Header */}
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-slate-900">Welcome back, {user?.name}! 👨‍🏫</h1>
        <p className="text-slate-600 mt-2">Manage your students and review their task submissions</p>
      </div>

      {/* Error Alert */}
      {error && <Alert type="error" title="Error" message={error} />}

      {/* Quick Stats */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-8">
        <StatCard 
          label="Assigned Students" 
          value={assignedStudents.length} 
          icon="👥"
          change={`${Math.max(0, assignedStudents.filter(s => s.pending_review_count > 0).length)} pending`}
        />
        <StatCard 
          label="Pending Reviews" 
          value={pendingReviews.length} 
          icon="✓"
          change={pendingReviews.length > 0 ? `${Math.round((pendingReviews.length / Math.max(1, assignedStudents.length)) * 100)}% of students`  : 'All caught up!'}
          trend={pendingReviews.length === 0 ? 'up' : 'down'}
        />
        <StatCard 
          label="Mentor Rating" 
          value={profile?.rating?.toFixed(1) || '—'} 
          icon="⭐"
        />
      </div>

      {/* Profile Card */}
      {!loading && profile && (
        <div className="mb-8">
          <MentorProfileCard profile={profile} user={user} />
        </div>
      )}

      {/* Main Content Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-8">
        {/* Students - Left Section */}
        <div className="lg:col-span-2 space-y-6">
          {/* Assigned Students */}
          <SectionCard
            title="👥 Assigned Students"
            subtitle={`${assignedStudents.length} total students`}
            action={
              assignedStudents.length > 5 && (
                <Link to="/mentor/students" className="text-blue-600 hover:text-blue-700 text-sm font-medium">
                  View All →
                </Link>
              )
            }
          >
            {loading ? (
              <div className="space-y-3">
                {[...Array(3)].map((_, i) => (
                  <div key={i} className="h-20 bg-slate-100 rounded animate-pulse" />
                ))}
              </div>
            ) : assignedStudents.length === 0 ? (
              <EmptyState
                icon="👥"
                title="No students assigned"
                description="When students are assigned to you, they'll appear here"
              />
            ) : (
              <div className="divide-y divide-slate-200">
                {assignedStudents.slice(0, 5).map(student => (
                  <div
                    key={student.student_id}
                    onClick={() => navigate(`/mentor/students/${student.student_id}`)}
                    className="py-4 px-2 hover:bg-slate-50 cursor-pointer transition-colors rounded"
                  >
                    <div className="flex items-start justify-between mb-2">
                      <div className="flex-1">
                        <h4 className="font-semibold text-slate-900">{student.student_name}</h4>
                        <p className="text-xs text-slate-600 mt-1">{student.strongest_domain}</p>
                      </div>
                      {student.pending_review_count > 0 && (
                        <Badge text={`${student.pending_review_count} review${student.pending_review_count !== 1 ? 's' : ''}`} status="warning" size="sm" />
                      )}
                    </div>
                    <LinearProgress current={student.completed_tasks_count} total={student.completed_tasks_count + student.pending_review_count} label="Tasks" />
                  </div>
                ))}
              </div>
            )}
          </SectionCard>

          {/* Pending Reviews */}
          <SectionCard
            title="📋 Pending Reviews"
            subtitle={`${pendingReviews.length} submissions waiting`}
            action={
              pendingReviews.length > 5 && (
                <Link to="/mentor/reviews" className="text-blue-600 hover:text-blue-700 text-sm font-medium">
                  View All →
                </Link>
              )
            }
          >
            {loading ? (
              <div className="space-y-3">
                {[...Array(3)].map((_, i) => (
                  <div key={i} className="h-16 bg-slate-100 rounded animate-pulse" />
                ))}
              </div>
            ) : pendingReviews.length === 0 ? (
              <EmptyState
                icon="✓"
                title="All caught up!"
                description="No pending reviews. Great job staying on top of submissions!"
              />
            ) : (
              <div className="space-y-2">
                {pendingReviews.slice(0, 5).map(review => (
                  <div
                    key={review.id}
                    onClick={() => navigate(`/mentor/reviews/${review.id}`)}
                    className="p-4 border border-yellow-200 bg-yellow-50 rounded-lg hover:bg-yellow-100 transition-colors cursor-pointer"
                  >
                    <div className="flex items-center justify-between mb-2">
                      <div className="flex-1">
                        <h4 className="font-semibold text-slate-900">{review.task__title}</h4>
                        <p className="text-xs text-slate-600">By: {review.student__name}</p>
                      </div>
                      <Badge text={review.task__domain} status="info" size="sm" />
                    </div>
                    <div className="text-xs text-slate-600">
                      Submitted {new Date(review.submitted_at).toLocaleDateString()}
                    </div>
                  </div>
                ))}
              </div>
            )}
          </SectionCard>
        </div>

        {/* Quick Actions - Right Section */}
        <div className="space-y-4">
          {/* Students Quick Card */}
          <Card className="bg-gradient-to-br from-blue-50 to-blue-100 border-blue-200">
            <CardBody className="text-center">
              <div className="text-4xl mb-3">👥</div>
              <h3 className="font-semibold text-slate-900 mb-2">View Students</h3>
              <p className="text-sm text-slate-700 mb-4">
                Browse all assigned students and track progress
              </p>
              <Link
                to="/mentor/students"
                className="block px-4 py-2 bg-blue-600 text-white rounded-lg font-medium hover:bg-blue-700 transition-colors text-center text-sm"
              >
                Go To Students →
              </Link>
            </CardBody>
          </Card>

          {/* Reviews Quick Card */}
          <Card className="bg-gradient-to-br from-yellow-50 to-yellow-100 border-yellow-200">
            <CardBody className="text-center">
              <div className="text-4xl mb-3">✓</div>
              <h3 className="font-semibold text-slate-900 mb-2">Task Reviews</h3>
              <p className="text-sm text-slate-700 mb-4">
                Review student submissions and provide feedback
              </p>
              <Link
                to="/mentor/reviews"
                className="block px-4 py-2 bg-yellow-600 text-white rounded-lg font-medium hover:bg-yellow-700 transition-colors text-center text-sm"
              >
                Go To Reviews →
              </Link>
            </CardBody>
          </Card>

          {/* Analytics Card */}
          <Card className="bg-gradient-to-br from-green-50 to-green-100 border-green-200">
            <CardBody className="text-center">
              <div className="text-4xl mb-3">📈</div>
              <h3 className="font-semibold text-slate-900 mb-2">Analytics</h3>
              <p className="text-sm text-slate-700 mb-4">
                View mentoring progress and student performance
              </p>
              <Link
                to="/mentor/analytics"
                className="block px-4 py-2 bg-green-600 text-white rounded-lg font-medium hover:bg-green-700 transition-colors text-center text-sm"
              >
                View Analytics →
              </Link>
            </CardBody>
          </Card>

          {/* Messages Card */}
          <Card className="bg-gradient-to-br from-purple-50 to-purple-100 border-purple-200">
            <CardBody className="text-center">
              <div className="text-4xl mb-3">💬</div>
              <h3 className="font-semibold text-slate-900 mb-2">Messages</h3>
              <p className="text-sm text-slate-700 mb-4">
                Communicate with your students
              </p>
              <button className="block w-full px-4 py-2 bg-purple-600 text-white rounded-lg font-medium hover:bg-purple-700 transition-colors text-center text-sm">
                Open Messages →
              </button>
            </CardBody>
          </Card>
        </div>
      </div>
    </DashboardLayout>
  );
}
