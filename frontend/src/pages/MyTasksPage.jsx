import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { toast } from 'react-toastify';
import { useAuth } from '../contexts/AuthContext';
import { taskService } from '../services/endpoints';
import DashboardLayout from '../components/DashboardLayout';
import { ProgressModal } from '../components/ConfirmModal';

export default function MyTasksPage() {
  const { user } = useAuth();
  const navigate = useNavigate();
  const [tasks, setTasks] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [filterStatus, setFilterStatus] = useState('all'); // all, accepted, in_progress, completed
  const [selectedTask, setSelectedTask] = useState(null);
  const [updating, setUpdating] = useState(false);
  const [progressModal, setProgressModal] = useState(null);
  const [progressValue, setProgressValue] = useState(0);

  const STATUS_COLORS = {
    accepted: 'bg-blue-50 border-blue-200',
    in_progress: 'bg-yellow-50 border-yellow-200',
    completed: 'bg-green-50 border-green-200',
    declined: 'bg-red-50 border-red-200',
  };

  const STATUS_BADGES = {
    accepted: { bg: 'bg-blue-100', text: 'text-blue-800', label: 'Accepted' },
    in_progress: { bg: 'bg-yellow-100', text: 'text-yellow-800', label: 'In Progress' },
    completed: { bg: 'bg-green-100', text: 'text-green-800', label: 'Completed' },
    declined: { bg: 'bg-red-100', text: 'text-red-800', label: 'Declined' },
  };

  useEffect(() => {
    if (user?.role !== 'Student') {
      navigate('/');
      return;
    }
    fetchMyTasks();
  }, [user, navigate]);

  const fetchMyTasks = async () => {
    try {
      setLoading(true);
      const response = await taskService.getMyTasks();
      if (response.data.success) {
        setTasks(response.data.data || []);
      } else {
        setError(response.data.error?.message || 'Failed to load tasks');
      }
    } catch (err) {
      setError('Error loading tasks');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const handleStartTask = async (taskId) => {
    try {
      setUpdating(true);
      const response = await taskService.updateTaskProgress(taskId, {
        status: 'in_progress',
      });
      if (response.data.success) {
        setTasks(
          tasks.map(t => (t.id === taskId ? response.data.data : t))
        );
        setSelectedTask(response.data.data);
      } else {
        setError(response.data.error?.message || 'Failed to start task');
      }
    } catch (err) {
      setError('Error starting task');
      console.error(err);
    } finally {
      setUpdating(false);
    }
  };

  const handleUpdateProgress = async (taskId, progress) => {
    try {
      setUpdating(true);
      const response = await taskService.updateTaskProgress(taskId, {
        progress_percentage: progress,
      });
      if (response.data.success) {
        setTasks(
          tasks.map(t => (t.id === taskId ? response.data.data : t))
        );
        setSelectedTask(response.data.data);
      } else {
        setError(response.data.error?.message || 'Failed to update progress');
      }
    } catch (err) {
      setError('Error updating progress');
      console.error(err);
    } finally {
      setUpdating(false);
    }
  };

  const handleCompleteTask = (taskId) => {
    // Navigate to task completion page instead of directly marking complete
    navigate(`/student/tasks/complete/${taskId}`);
  };

  const handleRequestReview = async (taskId) => {
    try {
      setUpdating(true);
      const response = await taskService.requestMentorReview(taskId);
      if (response.data.success) {
        setTasks(
          tasks.map(t => (t.id === taskId ? response.data.data : t))
        );
        setSelectedTask(response.data.data);
        toast.success('Mentor review requested successfully!');
      } else {
        setError(response.data.error?.message || 'Failed to request review');
      }
    } catch (err) {
      setError('Error requesting review');
      console.error(err);
    } finally {
      setUpdating(false);
    }
  };

  const getFilteredTasks = () => {
    if (filterStatus === 'all') {
      return tasks;
    }
    return tasks.filter(t => t.status === filterStatus);
  };

  const filteredTasks = getFilteredTasks();
  const activeTask = selectedTask || filteredTasks[0];

  return (
    <DashboardLayout>
      <div className="pb-8">
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900 mb-2">My Tasks</h1>
          <p className="text-gray-600">
            Track your accepted tasks and monitor your progress.
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
              <p className="text-gray-600">Loading your tasks...</p>
            </div>
          </div>
        ) : tasks.length === 0 ? (
          <div className="bg-white rounded-lg p-8 text-center border border-gray-200">
            <p className="text-gray-600 mb-4">No tasks assigned yet.</p>
            <p className="text-sm text-gray-500">
              Check the Recommended Tasks section to accept and start working on tasks.
            </p>
          </div>
        ) : (
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            {/* Tasks List */}
            <div className="lg:col-span-1">
              <div className="bg-white rounded-lg border border-gray-200 overflow-hidden">
                <div className="p-4 border-b border-gray-200">
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Filter by Status
                  </label>
                  <select
                    value={filterStatus}
                    onChange={(e) => setFilterStatus(e.target.value)}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-gray-900"
                  >
                    <option value="all">All Statuses</option>
                    <option value="accepted">Accepted</option>
                    <option value="in_progress">In Progress</option>
                    <option value="completed">Completed</option>
                  </select>
                </div>

                <div className="divide-y divide-gray-200 max-h-96 overflow-y-auto">
                  {filteredTasks.map(task => (
                    <button
                      key={task.id}
                      onClick={() => setSelectedTask(task)}
                      className={`w-full text-left p-4 hover:bg-gray-50 transition ${
                        activeTask?.id === task.id ? 'bg-gray-100' : ''
                      }`}
                    >
                      <h3 className="font-medium text-gray-900 truncate">
                        {task.task_details?.title}
                      </h3>
                      <p className="text-sm text-gray-500 mt-1">
                        {task.task_details?.domain}
                      </p>
                      <div className="flex items-center justify-between mt-2">
                        <span
                          className={`text-xs px-2 py-1 rounded ${
                            STATUS_BADGES[task.status].bg
                          } ${STATUS_BADGES[task.status].text}`}
                        >
                          {STATUS_BADGES[task.status].label}
                        </span>
                        <span className="text-xs text-gray-500">
                          {task.progress_percentage}%
                        </span>
                      </div>
                    </button>
                  ))}
                </div>
              </div>
            </div>

            {/* Task Details */}
            {activeTask && (
              <div className="lg:col-span-2">
                <div className="bg-white rounded-lg border border-gray-200 p-6">
                  <div className="mb-6">
                    <h2 className="text-2xl font-bold text-gray-900 mb-2">
                      {activeTask.task_details?.title}
                    </h2>
                    <div className="flex items-center gap-4 mb-4">
                      <span className={`px-3 py-1 rounded text-sm font-medium ${
                        STATUS_BADGES[activeTask.status].bg
                      } ${STATUS_BADGES[activeTask.status].text}`}>
                        {STATUS_BADGES[activeTask.status].label}
                      </span>
                      <span className="text-sm text-gray-600">
                        {activeTask.task_details?.domain}
                      </span>
                      <span className="text-sm text-gray-600">
                        {activeTask.task_details?.difficulty}
                      </span>
                    </div>
                  </div>

                  <div className="mb-6">
                    <h3 className="font-medium text-gray-900 mb-2">Description</h3>
                    <p className="text-gray-600 text-sm leading-relaxed">
                      {activeTask.task_details?.description}
                    </p>
                  </div>

                  {activeTask.task_details?.required_skills?.length > 0 && (
                    <div className="mb-6">
                      <h3 className="font-medium text-gray-900 mb-2">Required Skills</h3>
                      <div className="flex flex-wrap gap-2">
                        {activeTask.task_details.required_skills.map((skill, idx) => (
                          <span
                            key={idx}
                            className="px-3 py-1 bg-gray-100 text-gray-700 text-sm rounded"
                          >
                            {skill}
                          </span>
                        ))}
                      </div>
                    </div>
                  )}

                  {activeTask.task_details?.learning_outcomes?.length > 0 && (
                    <div className="mb-6">
                      <h3 className="font-medium text-gray-900 mb-2">Learning Outcomes</h3>
                      <ul className="space-y-2">
                        {activeTask.task_details.learning_outcomes.map((outcome, idx) => (
                          <li key={idx} className="text-sm text-gray-600 flex items-start">
                            <span className="mr-2">•</span>
                            <span>{outcome}</span>
                          </li>
                        ))}
                      </ul>
                    </div>
                  )}

                  {/* Progress Bar */}
                  <div className="mb-6">
                    <div className="flex items-center justify-between mb-2">
                      <h3 className="font-medium text-gray-900">Progress</h3>
                      <span className="text-sm font-semibold text-gray-900">
                        {activeTask.progress_percentage}%
                      </span>
                    </div>
                    <div className="w-full bg-gray-200 rounded-full h-2">
                      <div
                        className="bg-gray-900 h-2 rounded-full transition-all"
                        style={{ width: `${activeTask.progress_percentage}%` }}
                      ></div>
                    </div>
                  </div>

                  {/* Action Buttons */}
                  <div className="flex gap-3 flex-wrap">
                    {activeTask.status === 'accepted' && (
                      <button
                        onClick={() => handleStartTask(activeTask.id)}
                        disabled={updating}
                        className="px-4 py-2 bg-gray-900 text-white rounded-lg hover:bg-gray-800 disabled:opacity-50"
                      >
                        Start Task
                      </button>
                    )}

                    {activeTask.status === 'in_progress' && (
                      <>
                        <button
                          onClick={() => {
                            setProgressValue(activeTask.progress_percentage);
                            setProgressModal({
                              value: activeTask.progress_percentage,
                              onChange: (v) => setProgressValue(v),
                              onConfirm: (v) => handleUpdateProgress(activeTask.id, v),
                            });
                          }}
                          disabled={updating}
                          className="px-4 py-2 bg-gray-200 text-gray-900 rounded-lg hover:bg-gray-300 disabled:opacity-50"
                        >
                          Update Progress
                        </button>
                        {/* FR4: Submit written work for AI evaluation */}
                        <button
                          onClick={() => navigate(`/student/tasks/submit-text/${activeTask.id}`)}
                          disabled={updating}
                          className="px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 disabled:opacity-50"
                        >
                          Submit Written Work
                        </button>
                        <button
                          onClick={() => handleCompleteTask(activeTask.id)}
                          disabled={updating}
                          className="px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 disabled:opacity-50"
                        >
                          Mark Complete
                        </button>
                      </>
                    )}

                    {activeTask.status === 'completed' && !activeTask.mentor_review_requested && (
                      <button
                        onClick={() => handleRequestReview(activeTask.id)}
                        disabled={updating}
                        className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50"
                      >
                        Request Mentor Review
                      </button>
                    )}

                    {activeTask.mentor_review_requested && activeTask.mentor_review_status !== 'reviewed' && (
                      <div className="px-4 py-2 bg-blue-50 text-blue-900 rounded-lg text-sm">
                        ✓ Review requested ({activeTask.mentor_review_status})
                      </div>
                    )}
                  </div>

                  {/* Mentor Evaluation Card — shown once mentor has reviewed */}
                  {activeTask.evaluation && (
                    <div className="mt-6 border border-indigo-200 rounded-xl overflow-hidden">
                      <div className="bg-indigo-600 px-5 py-3 flex items-center justify-between">
                        <h4 className="text-white font-semibold text-sm">📝 Mentor Evaluation</h4>
                        {activeTask.evaluation.evaluated_at && (
                          <span className="text-indigo-200 text-xs">
                            {new Date(activeTask.evaluation.evaluated_at).toLocaleDateString('en-US', { year: 'numeric', month: 'short', day: 'numeric' })}
                          </span>
                        )}
                      </div>

                      {/* Scores */}
                      <div className="grid grid-cols-3 divide-x divide-indigo-100 bg-indigo-50">
                        <div className="px-4 py-3 text-center">
                          <p className="text-xs text-indigo-500 font-medium uppercase tracking-wide">MCQ</p>
                          <p className="text-2xl font-bold text-indigo-700 mt-0.5">
                            {activeTask.evaluation.mcq_score != null ? activeTask.evaluation.mcq_score : '—'}
                            <span className="text-sm font-normal text-indigo-400">/100</span>
                          </p>
                        </div>
                        <div className="px-4 py-3 text-center">
                          <p className="text-xs text-purple-500 font-medium uppercase tracking-wide">Mentor</p>
                          <p className="text-2xl font-bold text-purple-700 mt-0.5">
                            {activeTask.evaluation.mentor_score != null ? activeTask.evaluation.mentor_score : '—'}
                            <span className="text-sm font-normal text-purple-400">/100</span>
                          </p>
                        </div>
                        <div className="px-4 py-3 text-center">
                          <p className="text-xs text-green-500 font-medium uppercase tracking-wide">Final</p>
                          <p className="text-2xl font-bold text-green-700 mt-0.5">
                            {activeTask.evaluation.final_score != null ? activeTask.evaluation.final_score : '—'}
                            <span className="text-sm font-normal text-green-400">/100</span>
                          </p>
                        </div>
                      </div>

                      <div className="p-5 space-y-4 bg-white">
                        {/* Feedback text */}
                        {activeTask.evaluation.mentor_feedback && (
                          <div>
                            <h5 className="text-sm font-semibold text-gray-700 mb-1">Feedback</h5>
                            <p className="text-sm text-gray-600 leading-relaxed whitespace-pre-wrap">
                              {activeTask.evaluation.mentor_feedback}
                            </p>
                          </div>
                        )}

                        {/* Strengths / Weaknesses / Suggestions */}
                        <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
                          {activeTask.evaluation.strengths?.length > 0 && (
                            <div className="bg-green-50 rounded-lg p-3">
                              <h5 className="text-xs font-bold text-green-700 uppercase tracking-wide mb-2">💪 Strengths</h5>
                              <ul className="space-y-1">
                                {activeTask.evaluation.strengths.map((s, i) => (
                                  <li key={i} className="text-xs text-green-800 flex items-start gap-1">
                                    <span className="mt-0.5 shrink-0">•</span>{s}
                                  </li>
                                ))}
                              </ul>
                            </div>
                          )}
                          {activeTask.evaluation.weaknesses?.length > 0 && (
                            <div className="bg-yellow-50 rounded-lg p-3">
                              <h5 className="text-xs font-bold text-yellow-700 uppercase tracking-wide mb-2">⚠️ To Improve</h5>
                              <ul className="space-y-1">
                                {activeTask.evaluation.weaknesses.map((w, i) => (
                                  <li key={i} className="text-xs text-yellow-800 flex items-start gap-1">
                                    <span className="mt-0.5 shrink-0">•</span>{w}
                                  </li>
                                ))}
                              </ul>
                            </div>
                          )}
                          {activeTask.evaluation.suggestions?.length > 0 && (
                            <div className="bg-blue-50 rounded-lg p-3">
                              <h5 className="text-xs font-bold text-blue-700 uppercase tracking-wide mb-2">💡 Suggestions</h5>
                              <ul className="space-y-1">
                                {activeTask.evaluation.suggestions.map((s, i) => (
                                  <li key={i} className="text-xs text-blue-800 flex items-start gap-1">
                                    <span className="mt-0.5 shrink-0">•</span>{s}
                                  </li>
                                ))}
                              </ul>
                            </div>
                          )}
                        </div>
                      </div>
                    </div>
                  )}
                </div>
              </div>
            )}
          </div>
        )}
      </div>
      <ProgressModal
        config={progressModal ? { ...progressModal, value: progressValue, onChange: setProgressValue } : null}
        onClose={() => setProgressModal(null)}
      />
    </DashboardLayout>
  );
}
