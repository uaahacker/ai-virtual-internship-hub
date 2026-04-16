import { useState, useEffect, useContext } from 'react';
import { useParams, useNavigate, useLocation } from 'react-router-dom';
import { AuthContext } from '../contexts/AuthContext';
import { taskService } from '../services/endpoints';
import { FiTrendingUp, FiCheckCircle, FiAlertCircle, FiHome, FiRefreshCw } from 'react-icons/fi';

export default function TaskEvaluationResultPage() {
  const { evaluationId } = useParams();
  const location = useLocation();
  const { user } = useContext(AuthContext);
  const navigate = useNavigate();

  const [evaluation, setEvaluation] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    if (!user) {
      navigate('/login');
      return;
    }
    fetchEvaluation();
  }, [user, navigate, evaluationId]);

  const fetchEvaluation = async () => {
    try {
      setLoading(true);
      const response = await taskService.getEvaluation(evaluationId);
      if (response.data.success) {
        setEvaluation(response.data.data);
      } else {
        setError(response.data.error?.message || 'Failed to load evaluation');
      }
    } catch (err) {
      setError('Error loading evaluation');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const getPerformanceColor = (score) => {
    if (score >= 90) return 'text-green-600';
    if (score >= 80) return 'text-blue-600';
    if (score >= 70) return 'text-cyan-600';
    if (score >= 60) return 'text-yellow-600';
    return 'text-red-600';
  };

  const getPerformanceLevel = (score) => {
    if (score >= 90) return 'Excellent';
    if (score >= 80) return 'Very Good';
    if (score >= 70) return 'Good';
    if (score >= 60) return 'Fair';
    return 'Needs Improvement';
  };

  const getScoreBadgeColor = (score) => {
    if (score >= 90) return 'bg-green-50 border-green-200 text-green-700';
    if (score >= 80) return 'bg-blue-50 border-blue-200 text-blue-700';
    if (score >= 70) return 'bg-cyan-50 border-cyan-200 text-cyan-700';
    if (score >= 60) return 'bg-yellow-50 border-yellow-200 text-yellow-700';
    return 'bg-red-50 border-red-200 text-red-700';
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center py-8 px-4">
        <div className="text-center">
          <div className="inline-block w-8 h-8 border-4 border-gray-200 border-t-gray-900 rounded-full animate-spin mb-4"></div>
          <p className="text-gray-600">Loading your evaluation results...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 py-8 px-4">
      <div className="max-w-4xl mx-auto">
        {error ? (
          <div className="bg-white rounded-lg border border-red-200 p-8 text-center">
            <FiAlertCircle className="mx-auto text-red-500 mb-4" size={48} />
            <p className="text-red-700 mb-6">{error}</p>
            <button
              onClick={() => navigate('/student/dashboard')}
              className="px-6 py-2 bg-gray-900 text-white rounded-lg hover:bg-gray-800"
            >
              Back to Dashboard
            </button>
          </div>
        ) : evaluation && (
          <>
            {/* Header */}
            <div className="bg-white rounded-lg border border-gray-200 p-8 mb-6">
              <div className="text-center mb-8">
                <h1 className="text-3xl font-bold text-gray-900 mb-2">Evaluation Results</h1>
                <p className="text-lg text-gray-600">{evaluation.task_title}</p>
              </div>

              {/* Main Score Display */}
              {evaluation.final_score !== null ? (
                <div className={`text-center p-8 rounded-lg border-2 ${getScoreBadgeColor(evaluation.final_score)}`}>
                  <p className="text-sm font-medium uppercase mb-2 opacity-75">Final Score</p>
                  <div className="text-6xl font-bold mb-2">
                    {evaluation.final_score.toFixed(1)}
                  </div>
                  <p className={`text-xl font-semibold ${getPerformanceColor(evaluation.final_score)}`}>
                    {getPerformanceLevel(evaluation.final_score)}
                  </p>
                </div>
              ) : (
                <div className="text-center p-8 bg-yellow-50 border border-yellow-200 rounded-lg">
                  <FiRefreshCw className="mx-auto text-yellow-600 mb-3" size={32} />
                  <p className="text-yellow-700 font-medium">Evaluation Pending</p>
                  <p className="text-yellow-600 text-sm mt-1">Your mentor is reviewing your work. Check back soon!</p>
                </div>
              )}
            </div>

            {/* Score Breakdown */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-6">
              {/* MCQ Score */}
              <div className="bg-white rounded-lg border border-gray-200 p-6">
                <div className="flex items-center gap-3 mb-4">
                  <div className="w-10 h-10 rounded-full bg-blue-100 flex items-center justify-center">
                    <FiCheckCircle className="text-blue-600" size={20} />
                  </div>
                  <h3 className="font-bold text-gray-900">Quiz Performance</h3>
                </div>
                <div className="text-3xl font-bold text-blue-600 mb-2">
                  {evaluation.mcq_score.toFixed(1)}%
                </div>
                <p className="text-sm text-gray-600">Based on MCQ answers</p>
                <div className="mt-3 w-full bg-gray-200 rounded-full h-2">
                  <div
                    className="bg-blue-600 h-2 rounded-full"
                    style={{ width: `${evaluation.mcq_score}%` }}
                  ></div>
                </div>
              </div>

              {/* Mentor Score */}
              <div className="bg-white rounded-lg border border-gray-200 p-6">
                <div className="flex items-center gap-3 mb-4">
                  <div className="w-10 h-10 rounded-full bg-purple-100 flex items-center justify-center">
                    <FiTrendingUp className="text-purple-600" size={20} />
                  </div>
                  <h3 className="font-bold text-gray-900">Mentor Review</h3>
                </div>
                {evaluation.mentor_score !== null ? (
                  <>
                    <div className="text-3xl font-bold text-purple-600 mb-2">
                      {evaluation.mentor_score.toFixed(1)}%
                    </div>
                    <p className="text-sm text-gray-600">Manual evaluation score</p>
                    <div className="mt-3 w-full bg-gray-200 rounded-full h-2">
                      <div
                        className="bg-purple-600 h-2 rounded-full"
                        style={{ width: `${evaluation.mentor_score}%` }}
                      ></div>
                    </div>
                  </>
                ) : (
                  <p className="text-sm text-gray-500 italic">Pending mentor evaluation</p>
                )}
              </div>
            </div>

            {/* Feedback Section */}
            {evaluation.mentor_feedback && (
              <div className="bg-white rounded-lg border border-gray-200 p-6 mb-6">
                <h3 className="font-bold text-gray-900 mb-4">Mentor Feedback</h3>
                <p className="text-gray-700 whitespace-pre-wrap">{evaluation.mentor_feedback}</p>
              </div>
            )}

            {/* Strengths, Weaknesses, Suggestions */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-6">
              {/* Strengths */}
              {evaluation.strengths && evaluation.strengths.length > 0 && (
                <div className="bg-green-50 border border-green-200 rounded-lg p-6">
                  <h4 className="font-bold text-green-900 mb-4 flex items-center gap-2">
                    <FiCheckCircle size={20} />
                    Strengths
                  </h4>
                  <ul className="space-y-2">
                    {evaluation.strengths.map((item, idx) => (
                      <li key={idx} className="text-green-800 flex gap-2">
                        <span className="text-green-600 font-bold">✓</span>
                        <span>{item}</span>
                      </li>
                    ))}
                  </ul>
                </div>
              )}

              {/* Weaknesses */}
              {evaluation.weaknesses && evaluation.weaknesses.length > 0 && (
                <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-6">
                  <h4 className="font-bold text-yellow-900 mb-4 flex items-center gap-2">
                    <FiAlertCircle size={20} />
                    Areas to Improve
                  </h4>
                  <ul className="space-y-2">
                    {evaluation.weaknesses.map((item, idx) => (
                      <li key={idx} className="text-yellow-800 flex gap-2">
                        <span className="text-yellow-600 font-bold">•</span>
                        <span>{item}</span>
                      </li>
                    ))}
                  </ul>
                </div>
              )}

              {/* Suggestions */}
              {evaluation.suggestions && evaluation.suggestions.length > 0 && (
                <div className="bg-blue-50 border border-blue-200 rounded-lg p-6">
                  <h4 className="font-bold text-blue-900 mb-4">Suggestions</h4>
                  <ul className="space-y-2">
                    {evaluation.suggestions.map((item, idx) => (
                      <li key={idx} className="text-blue-800 flex gap-2">
                        <span className="text-blue-600 font-bold">→</span>
                        <span>{item}</span>
                      </li>
                    ))}
                  </ul>
                </div>
              )}
            </div>

            {/* Status */}
            <div className="bg-white rounded-lg border border-gray-200 p-6 mb-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-gray-600 mb-1">Status</p>
                  <p className="text-lg font-bold text-gray-900 capitalize">{evaluation.status}</p>
                </div>
                {evaluation.evaluated_at && (
                  <div className="text-right">
                    <p className="text-sm text-gray-600 mb-1">Evaluated by</p>
                    <p className="text-lg font-bold text-gray-900">{evaluation.evaluated_by_name}</p>
                  </div>
                )}
              </div>
            </div>

            {/* Action Buttons */}
            <div className="flex gap-4">
              <button
                onClick={() => navigate('/student/tasks/my-tasks')}
                className="flex-1 px-6 py-3 bg-gray-900 text-white rounded-lg hover:bg-gray-800 transition font-medium flex items-center justify-center gap-2"
              >
                <FiHome size={18} />
                Back to My Tasks
              </button>
              <button
                onClick={() => navigate('/student/dashboard')}
                className="flex-1 px-6 py-3 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 transition font-medium"
              >
                Go to Dashboard
              </button>
            </div>
          </>
        )}
      </div>
    </div>
  );
}
