import { useState, useEffect, useContext } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { AuthContext } from '../contexts/AuthContext';
import { mentorService } from '../services/endpoints';
import { FiArrowLeft, FiBarChart3, FiCheckCircle, FiClock } from 'react-icons/fi';

export default function MentorStudentDetailPage() {
  const { studentId } = useParams();
  const navigate = useNavigate();
  const { user } = useContext(AuthContext);
  const [student, setStudent] = useState(null);
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (user?.role !== 'Mentor') {
      navigate('/');
      return;
    }
    fetchStudentDetail();
  }, [studentId, user, navigate]);

  const fetchStudentDetail = async () => {
    try {
      setLoading(true);
      const response = await mentorService.getStudentDetail(studentId);
      if (response.data.success) {
        setStudent(response.data.data);
      } else {
        setError(response.data.error?.message || 'Failed to load student details');
      }
    } catch (err) {
      setError('Error loading student details');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 py-8 px-4">
        <div className="flex items-center justify-center py-16">
          <div className="text-center">
            <div className="inline-block w-8 h-8 border-4 border-gray-200 border-t-gray-900 rounded-full animate-spin mb-4"></div>
            <p className="text-gray-600">Loading student details...</p>
          </div>
        </div>
      </div>
    );
  }

  if (!student) {
    return (
      <div className="min-h-screen bg-gray-50 py-8 px-4">
        <div className="max-w-4xl mx-auto">
          <button
            onClick={() => navigate('/mentor/students')}
            className="mb-6 flex items-center gap-2 text-blue-600 hover:text-blue-700 font-medium"
          >
            <FiArrowLeft size={18} /> Back to Students
          </button>
          <div className="bg-white rounded-lg p-8 text-center border border-gray-200">
            <p className="text-gray-600 mb-4">{error || 'Student not found'}</p>
            <button
              onClick={() => navigate('/mentor/students')}
              className="px-4 py-2 bg-gray-900 text-white rounded-lg hover:bg-gray-800"
            >
              Go Back
            </button>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 py-8 px-4">
      <div className="max-w-4xl mx-auto">
        {/* Back Button */}
        <button
          onClick={() => navigate('/mentor/students')}
          className="mb-6 flex items-center gap-2 text-blue-600 hover:text-blue-700 font-medium"
        >
          <FiArrowLeft size={18} /> Back to Students
        </button>

        {/* Student Header */}
        <div className="bg-white rounded-lg p-6 mb-6 border border-gray-200">
          <div className="flex items-start justify-between mb-4">
            <div>
              <h1 className="text-3xl font-bold text-gray-900">{student.student_name}</h1>
              <p className="text-gray-600 mt-1">{student.student_email}</p>
            </div>
            <div className="text-right">
              <p className="text-sm text-gray-600">Overall Progress</p>
              <p className="text-3xl font-bold text-gray-900">{student.progress_score}%</p>
            </div>
          </div>

          {student.bio && (
            <p className="text-gray-600 mb-4">{student.bio}</p>
          )}

          <div className="grid grid-cols-2 md:grid-cols-4 gap-4 pt-4 border-t border-gray-200">
            <div>
              <p className="text-xs text-gray-600 uppercase">Strongest Domain</p>
              <p className="font-semibold text-gray-900 mt-1">{student.strongest_domain || 'N/A'}</p>
            </div>
            <div>
              <p className="text-xs text-gray-600 uppercase">Weakest Domain</p>
              <p className="font-semibold text-gray-900 mt-1">{student.weakest_domain || 'N/A'}</p>
            </div>
            <div>
              <p className="text-xs text-gray-600 uppercase">Tasks Completed</p>
              <p className="font-semibold text-gray-900 mt-1">{student.completed_tasks_count}</p>
            </div>
            <div>
              <p className="text-xs text-gray-600 uppercase">Preferred Domains</p>
              <p className="font-semibold text-gray-900 mt-1">{student.preferred_domains?.length || 0}</p>
            </div>
          </div>
        </div>

        {/* Two Column Layout */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Left Column - Assessment & Profile */}
          <div className="lg:col-span-2 space-y-6">
            {/* Assessment Summary */}
            <div className="bg-white rounded-lg p-6 border border-gray-200">
              <div className="flex items-center gap-3 mb-4">
                <FiBarChart3 className="text-blue-600" size={24} />
                <h2 className="text-xl font-bold text-gray-900">Assessment Summary</h2>
              </div>

              <div className="space-y-3">
                <div>
                  <p className="text-sm text-gray-600 mb-1">Total Attempts</p>
                  <p className="text-2xl font-bold text-gray-900">
                    {student.assessment_summary?.total_attempts || 0}
                  </p>
                </div>
                <div>
                  <p className="text-sm text-gray-600 mb-1">Average Score</p>
                  <div className="flex items-center gap-2">
                    <div className="flex-1 bg-gray-200 rounded-full h-2">
                      <div
                        className="bg-gray-900 h-2 rounded-full"
                        style={{
                          width: `${student.assessment_summary?.average_score || 0}%`,
                        }}
                      ></div>
                    </div>
                    <span className="text-lg font-semibold text-gray-900">
                      {Math.round(student.assessment_summary?.average_score || 0)}%
                    </span>
                  </div>
                </div>
                <div>
                  <p className="text-sm text-gray-600 mb-2">Domains Attempted</p>
                  <div className="flex flex-wrap gap-2">
                    {student.assessment_summary?.domains_attempted?.map(domain => (
                      <span
                        key={domain}
                        className="px-3 py-1 bg-blue-100 text-blue-800 text-sm rounded-full"
                      >
                        {domain}
                      </span>
                    ))}
                  </div>
                </div>
              </div>
            </div>

            {/* Selected Skills */}
            {student.selected_skills?.length > 0 && (
              <div className="bg-white rounded-lg p-6 border border-gray-200">
                <h3 className="text-lg font-bold text-gray-900 mb-4">Selected Skills</h3>
                <div className="flex flex-wrap gap-2">
                  {student.selected_skills.map((skill, idx) => (
                    <span
                      key={idx}
                      className="px-3 py-1 bg-gray-100 text-gray-700 text-sm rounded-full"
                    >
                      {skill}
                    </span>
                  ))}
                </div>
              </div>
            )}

            {/* Preferred Domains */}
            {student.preferred_domains?.length > 0 && (
              <div className="bg-white rounded-lg p-6 border border-gray-200">
                <h3 className="text-lg font-bold text-gray-900 mb-4">Preferred Domains</h3>
                <div className="flex flex-wrap gap-2">
                  {student.preferred_domains.map((domain, idx) => (
                    <span
                      key={idx}
                      className="px-3 py-1 bg-green-100 text-green-800 text-sm rounded-full"
                    >
                      {domain}
                    </span>
                  ))}
                </div>
              </div>
            )}
          </div>

          {/* Right Column - Tasks */}
          <div className="space-y-6">
            {/* Current Tasks */}
            <div className="bg-white rounded-lg p-6 border border-gray-200">
              <div className="flex items-center gap-2 mb-4">
                <FiClock className="text-orange-600" size={20} />
                <h3 className="text-lg font-bold text-gray-900">Current Tasks</h3>
              </div>

              {student.current_tasks?.length === 0 ? (
                <p className="text-sm text-gray-500">No active tasks</p>
              ) : (
                <div className="space-y-2">
                  {student.current_tasks?.map((task, idx) => (
                    <div
                      key={idx}
                      className="p-3 bg-orange-50 border border-orange-200 rounded-lg"
                    >
                      <p className="font-medium text-gray-900 text-sm">{task.task__title}</p>
                      <p className="text-xs text-gray-600 mt-1">Status: {task.status}</p>
                      <p className="text-xs text-gray-600">Progress: {task.progress_percentage}%</p>
                    </div>
                  ))}
                </div>
              )}
            </div>

            {/* Pending Reviews */}
            <div className="bg-white rounded-lg p-6 border border-gray-200">
              <div className="flex items-center gap-2 mb-4">
                <FiCheckCircle className="text-yellow-600" size={20} />
                <h3 className="text-lg font-bold text-gray-900">Pending Reviews</h3>
              </div>

              {student.pending_review_tasks?.length === 0 ? (
                <p className="text-sm text-gray-500">No pending reviews</p>
              ) : (
                <div className="space-y-2">
                  {student.pending_review_tasks?.map((task, idx) => (
                    <button
                      key={idx}
                      onClick={() => navigate(`/mentor/reviews/${task.id}`)}
                      className="w-full text-left p-3 bg-yellow-50 hover:bg-yellow-100 border border-yellow-200 rounded-lg transition"
                    >
                      <p className="font-medium text-gray-900 text-sm">{task.task__title}</p>
                      <p className="text-xs text-gray-600 mt-1">
                        Completed: {task.completed_at ? new Date(task.completed_at).toLocaleDateString() : 'N/A'}
                      </p>
                    </button>
                  ))}
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
