import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import { taskService } from '../services/endpoints';
import { FiCheckCircle, FiArrowRight, FiFileText } from 'react-icons/fi';
import DashboardLayout from '../components/DashboardLayout';

export default function TaskCompletionPage() {
  const { assignmentId } = useParams();
  const { user } = useAuth();
  const navigate = useNavigate();

  const [task, setTask] = useState(null);
  const [reflectionText, setReflectionText] = useState('');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [submitting, setSubmitting] = useState(false);
  const [success, setSuccess] = useState(false);

  useEffect(() => {
    if (!user) {
      navigate('/login');
      return;
    }
    fetchTaskDetails();
  }, [user, navigate, assignmentId]);

  const fetchTaskDetails = async () => {
    try {
      setLoading(true);
      const response = await taskService.getAssignmentDetail(assignmentId);
      if (response.data.success) {
        setTask(response.data.data);
      } else {
        setError(response.data.error?.message || 'Failed to load task');
      }
    } catch (err) {
      setError('Error loading task details');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const handleCompleteTask = async () => {
    try {
      setSubmitting(true);
      setError('');

      const response = await taskService.completeTask(assignmentId, reflectionText);

      if (response.data.success) {
        setSuccess(true);
        
        // Navigate to MCQ quiz after 2 seconds
        setTimeout(() => {
          const completionId = response.data.data.completion_id;
          const taskId = response.data.data.task_id;
          navigate(`/student/tasks/mcq/${completionId}/${taskId}`, {
            state: { taskTitle: response.data.data.task_title }
          });
        }, 2000);
      } else {
        setError(response.data.error?.message || 'Failed to complete task');
      }
    } catch (err) {
      setError('Error completing task');
      console.error(err);
    } finally {
      setSubmitting(false);
    }
  };

  if (loading) {
    return (
      <DashboardLayout>
        <div className="flex items-center justify-center py-16">
          <div className="text-center">
            <div className="inline-block w-8 h-8 border-4 border-gray-200 border-t-gray-900 rounded-full animate-spin mb-4"></div>
            <p className="text-gray-600">Loading task details...</p>
          </div>
        </div>
      </DashboardLayout>
    );
  }

  return (
    <DashboardLayout>
      <div className="max-w-2xl mx-auto pb-8">
        {/* Success Message */}
        {success && (
          <div className="mb-6 p-4 bg-green-50 border border-green-200 rounded-lg">
            <div className="flex items-center gap-3 text-green-700">
              <FiCheckCircle size={24} />
              <span className="font-medium">Task marked as completed! Redirecting to quiz...</span>
            </div>
          </div>
        )}

        {/* Error Message */}
        {error && (
          <div className="mb-6 p-4 bg-red-50 border border-red-200 rounded-lg text-red-700">
            {error}
          </div>
        )}

        {/* Main Content */}
        {!success && task && (
          <>
            {/* Task Header */}
            <div className="bg-white rounded-lg border border-gray-200 p-8 mb-6">
              <div className="flex items-start gap-4 mb-6">
                <div className="w-12 h-12 rounded-full bg-gradient-to-br from-blue-400 to-blue-600 flex items-center justify-center text-white flex-shrink-0">
                  <FiCheckCircle size={24} />
                </div>
                <div className="flex-1">
                  <h1 className="text-3xl font-bold text-gray-900 mb-2">{task.task_title}</h1>
                  <p className="text-gray-600">Complete this task and reflect on your learning</p>
                </div>
              </div>

              {/* Task Info Grid */}
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4 p-4 bg-gray-50 rounded-lg">
                <div>
                  <p className="text-xs font-medium text-gray-600 uppercase">Domain</p>
                  <p className="text-lg font-bold text-gray-900 mt-1">{task.task_domain}</p>
                </div>
                <div>
                  <p className="text-xs font-medium text-gray-600 uppercase">Difficulty</p>
                  <p className="text-lg font-bold text-gray-900 mt-1">{task.task_difficulty}</p>
                </div>
                <div>
                  <p className="text-xs font-medium text-gray-600 uppercase">Status</p>
                  <p className="text-lg font-bold text-gray-900 mt-1 capitalize">{task.status}</p>
                </div>
                <div>
                  <p className="text-xs font-medium text-gray-600 uppercase">Progress</p>
                  <p className="text-lg font-bold text-gray-900 mt-1">{task.progress_percentage}%</p>
                </div>
              </div>
            </div>

            {/* Task Description */}
            <div className="bg-white rounded-lg border border-gray-200 p-6 mb-6">
              <h2 className="text-xl font-bold text-gray-900 mb-4">Task Description</h2>
              <div className="text-gray-700 whitespace-pre-wrap mb-6">
                {task.task_details?.description}
              </div>

              {/* Learning Outcomes */}
              {task.task_details?.learning_outcomes?.length > 0 && (
                <div>
                  <h3 className="font-semibold text-gray-900 mb-3">Learning Outcomes</h3>
                  <ul className="space-y-2">
                    {task.task_details.learning_outcomes.map((outcome, idx) => (
                      <li key={idx} className="flex gap-3 text-gray-700">
                        <span className="text-blue-600 font-bold">✓</span>
                        <span>{outcome}</span>
                      </li>
                    ))}
                  </ul>
                </div>
              )}
            </div>

            {/* Reflective Text Box */}
            <div className="bg-white rounded-lg border border-gray-200 p-6">
              <div className="flex items-center gap-3 mb-4">
                <FiFileText className="text-blue-600" size={24} />
                <h2 className="text-xl font-bold text-gray-900">Your Reflection</h2>
              </div>

              <p className="text-gray-600 mb-4">
                Briefly describe what you learned, challenges faced, and how you'd approach similar tasks in the future. This helps your mentor understand your learning journey.
              </p>

              <textarea
                value={reflectionText}
                onChange={(e) => setReflectionText(e.target.value)}
                placeholder="Share your reflections about this task... (optional)"
                className="w-full h-32 px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 resize-none"
                maxLength={2000}
              />

              <div className="flex justify-between items-center mt-3">
                <p className="text-sm text-gray-600">{reflectionText.length}/2000 characters</p>
              </div>

              {/* Completion Info */}
              <div className="mt-6 p-4 bg-blue-50 border border-blue-200 rounded-lg">
                <p className="text-blue-900 text-sm">
                  <strong>Next Step:</strong> After marking this task complete, you'll take a MCQ quiz to assess your learning. Your mentor will review both the quiz score and this reflection to provide comprehensive feedback.
                </p>
              </div>

              {/* Action Buttons */}
              <div className="flex gap-4 mt-6">
                <button
                  onClick={() => navigate(`/student/tasks/my-tasks`)}
                  className="flex-1 px-6 py-3 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 transition font-medium"
                  disabled={submitting}
                >
                  Cancel
                </button>
                <button
                  onClick={handleCompleteTask}
                  disabled={submitting || !task}
                  className="flex-1 px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition font-medium flex items-center justify-center gap-2 disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  {submitting ? 'Completing...' : 'Mark Complete & Take Quiz'}
                  {!submitting && <FiArrowRight size={18} />}
                </button>
              </div>
            </div>
          </>
        )}
      </div>
    </DashboardLayout>
  );
}
