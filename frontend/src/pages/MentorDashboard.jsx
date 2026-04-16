import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import DashboardLayout from '../components/DashboardLayout';
import MentorProfileCard from '../components/MentorProfileCard';
import { useAuth } from '../contexts/AuthContext';
import { profileService, mentorService } from '../services/endpoints';
import { FiUsers, FiClipboard, FiMessageSquare, FiArrowRight } from 'react-icons/fi';

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
      
      // Load mentor profile
      const profileRes = await profileService.getMentorProfile();
      setProfile(profileRes.data.data);
      
      // Load assigned students
      const studentsRes = await mentorService.getAssignedStudents();
      if (studentsRes.data.success) {
        setAssignedStudents(studentsRes.data.data);
      }
      
      // Load pending reviews
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
      <div className="mb-8">
        <h1 className="text-2xl font-bold text-gray-900">
          Welcome, {user?.name}!
        </h1>
        <p className="text-gray-500 mt-1">Mentor Dashboard — manage your assigned students and task reviews.</p>
      </div>

      {error && (
        <div className="mb-6 p-4 bg-red-50 border border-red-200 rounded text-red-700">
          {error}
        </div>
      )}

      {/* Profile Card */}
      {!loading && profile && (
        <div className="mb-8">
          <MentorProfileCard profile={profile} user={user} />
        </div>
      )}

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
        {[
          {
            label: 'Assigned Students',
            value: assignedStudents.length,
            icon: FiUsers,
            color: 'text-blue-600 bg-blue-100',
          },
          { 
            label: 'Pending Reviews', 
            value: pendingReviews.length, 
            icon: FiMessageSquare, 
            color: 'text-yellow-600 bg-yellow-100' 
          },
          { 
            label: 'Mentor Rating', 
            value: profile?.rating?.toFixed(1) || '—', 
            icon: FiClipboard, 
            color: 'text-green-600 bg-green-100' 
          },
        ].map((card) => (
          <div key={card.label} className="bg-white rounded-xl shadow-sm p-6 flex items-center gap-4">
            <div className={`w-12 h-12 rounded-lg flex items-center justify-center ${card.color}`}>
              <card.icon size={22} />
            </div>
            <div>
              <p className="text-2xl font-bold text-gray-900">{card.value}</p>
              <p className="text-sm text-gray-500">{card.label}</p>
            </div>
          </div>
        ))}
      </div>

      {/* Assigned Students and Pending Reviews */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Assigned Students */}
        <div className="bg-white rounded-xl shadow-sm p-6">
          <div className="flex items-center justify-between mb-6">
            <h2 className="text-lg font-semibold text-gray-800">Assigned Students ({assignedStudents.length})</h2>
            {assignedStudents.length > 0 && (
              <button
                onClick={() => navigate('/mentor/students')}
                className="text-blue-600 hover:text-blue-700 text-sm font-medium flex items-center gap-1"
              >
                View All <FiArrowRight size={14} />
              </button>
            )}
          </div>
          
          {assignedStudents.length === 0 ? (
            <div className="text-center py-12 text-gray-400">
              <FiUsers className="mx-auto mb-3" size={40} />
              <p>No students assigned yet.</p>
            </div>
          ) : (
            <div className="space-y-3">
              {assignedStudents.slice(0, 5).map(student => (
                <div
                  key={student.student_id}
                  onClick={() => navigate(`/mentor/students/${student.student_id}`)}
                  className="p-4 border border-gray-200 rounded-lg hover:border-blue-300 hover:bg-blue-50 cursor-pointer transition"
                >
                  <div className="flex items-center justify-between">
                    <div className="flex-1">
                      <h3 className="font-medium text-gray-900">{student.student_name}</h3>
                      <p className="text-sm text-gray-500">{student.strongest_domain}</p>
                    </div>
                    {student.pending_review_count > 0 && (
                      <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-yellow-100 text-yellow-800">
                        {student.pending_review_count} review{student.pending_review_count !== 1 ? 's' : ''}
                      </span>
                    )}
                  </div>
                  <div className="mt-2 text-xs text-gray-600">
                    Progress: {student.progress_score}% • Tasks: {student.completed_tasks_count}
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Pending Reviews */}
        <div className="bg-white rounded-xl shadow-sm p-6">
          <div className="flex items-center justify-between mb-6">
            <h2 className="text-lg font-semibold text-gray-800">Pending Reviews ({pendingReviews.length})</h2>
            {pendingReviews.length > 0 && (
              <button
                onClick={() => navigate('/mentor/reviews')}
                className="text-blue-600 hover:text-blue-700 text-sm font-medium flex items-center gap-1"
              >
                View All <FiArrowRight size={14} />
              </button>
            )}
          </div>

          {pendingReviews.length === 0 ? (
            <div className="text-center py-12 text-gray-400">
              <FiClipboard className="mx-auto mb-3" size={40} />
              <p>No pending reviews.</p>
            </div>
          ) : (
            <div className="space-y-3">
              {pendingReviews.slice(0, 5).map(review => (
                <div
                  key={review.id}
                  onClick={() => navigate(`/mentor/reviews/${review.id}`)}
                  className="p-4 border border-yellow-200 bg-yellow-50 rounded-lg hover:bg-yellow-100 cursor-pointer transition"
                >
                  <div className="flex items-center justify-between">
                    <div className="flex-1">
                      <h3 className="font-medium text-gray-900">{review.task__title}</h3>
                      <p className="text-sm text-gray-600">By: {review.student__name}</p>
                    </div>
                  </div>
                  <div className="mt-2 flex items-center justify-between text-xs text-gray-600">
                    <span>{review.task__domain}</span>
                    <span>Progress: {review.progress_percentage}%</span>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </DashboardLayout>
  );
}
