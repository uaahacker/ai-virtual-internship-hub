import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import { mentorService, taskService } from '../services/endpoints';
import DashboardLayout from '../components/DashboardLayout';

export default function MentorReviewTaskPage() {
  const { assignmentId } = useParams();
  const navigate = useNavigate();
  const { user } = useAuth();
  const [review, setReview] = useState(null);
  const [mentorScore, setMentorScore] = useState(70);
  const [feedback, setFeedback] = useState('');
  const [strengths, setStrengths] = useState('');
  const [weaknesses, setWeaknesses] = useState('');
  const [suggestions, setSuggestions] = useState('');
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState(false);

  useEffect(() => {
    if (user?.role !== 'Mentor') { navigate('/'); return; }
    fetchReview();
  }, [assignmentId, user, navigate]);

  const fetchReview = async () => {
    try {
      setLoading(true);
      const response = await mentorService.getPendingReviews();
      if (response.data.success) {
        const found = response.data.data.find(r => r.id === parseInt(assignmentId));
        if (found) {
          setReview(found);
          if (found.mcq_score != null) {
            setMentorScore(Math.round(found.mcq_score));
          }
        } else {
          setError('Review not found or already completed.');
        }
      } else {
        setError('Failed to load review.');
      }
    } catch (err) {
      setError('Error loading review.');
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = async () => {
    if (!feedback.trim()) { setError('Please enter feedback for the student.'); return; }
    if (!review.evaluation_id) {
      setError('No evaluation record found. The student may not have submitted their MCQ yet.');
      return;
    }
    try {
      setSubmitting(true);
      setError('');
      const toList = (str) => str.split('\n').map(s => s.trim()).filter(Boolean);
      const response = await taskService.mentorEvaluateTask(review.evaluation_id, {
        mentor_score: mentorScore,
        mentor_feedback: feedback,
        strengths: toList(strengths),
        weaknesses: toList(weaknesses),
        suggestions: toList(suggestions),
      });
      if (response.data.success) {
        setSuccess(true);
        setTimeout(() => navigate('/mentor/reviews'), 1800);
      } else {
        setError(response.data.error?.message || 'Failed to submit evaluation.');
      }
    } catch (err) {
      setError(err.response?.data?.error?.message || 'Error submitting evaluation.');
    } finally {
      setSubmitting(false);
    }
  };

  const finalScore = review?.mcq_score != null
    ? ((review.mcq_score + mentorScore) / 2).toFixed(1)
    : mentorScore.toFixed(1);

  const scoreColor = (s) => s >= 80 ? 'text-green-600' : s >= 60 ? 'text-yellow-600' : 'text-red-600';
  const barColor = (s) => s >= 80 ? 'bg-green-400' : s >= 60 ? 'bg-yellow-400' : 'bg-red-400';

  if (loading) {
    return (
      <DashboardLayout>
        <div className="flex items-center justify-center py-20">
          <div className="animate-spin rounded-full h-8 w-8 border border-gray-300 border-t-gray-900"></div>
        </div>
      </DashboardLayout>
    );
  }

  if (!review) {
    return (
      <DashboardLayout>
        <div className="max-w-3xl mx-auto">
          <button onClick={() => navigate('/mentor/reviews')}
            className="mb-6 flex items-center gap-2 text-blue-600 hover:text-blue-700 font-medium text-sm">
            ← Back to Reviews
          </button>
          <div className="bg-red-50 border border-red-200 rounded-xl p-8 text-center">
            <p className="text-red-700 font-medium">{error || 'Review not found'}</p>
          </div>
        </div>
      </DashboardLayout>
    );
  }

  if (success) {
    return (
      <DashboardLayout>
        <div className="max-w-3xl mx-auto">
          <div className="bg-green-50 border border-green-200 rounded-xl p-10 text-center">
            <div className="text-5xl mb-3">✅</div>
            <h2 className="text-xl font-bold text-green-800 mb-1">Evaluation Submitted!</h2>
            <p className="text-green-700 text-sm">Student's portfolio will be updated. Redirecting...</p>
          </div>
        </div>
      </DashboardLayout>
    );
  }

  return (
    <DashboardLayout>
      <div className="max-w-3xl mx-auto pb-10">
        <button onClick={() => navigate('/mentor/reviews')}
          className="mb-6 flex items-center gap-2 text-blue-600 hover:text-blue-700 font-medium text-sm">
          ← Back to Reviews
        </button>

        <h1 className="text-2xl font-bold text-gray-900 mb-1">📝 Evaluate Task</h1>
        <p className="text-sm text-gray-500 mb-6">Review the student's work and assign a score to complete the evaluation.</p>

        {error && (
          <div className="mb-4 p-4 bg-red-50 border border-red-200 rounded-lg text-red-700 text-sm">{error}</div>
        )}

        {/* Task + Student Info */}
        <div className="bg-white border border-gray-200 rounded-xl p-6 mb-5">
          <div className="flex items-start justify-between flex-wrap gap-3">
            <div>
              <h2 className="text-xl font-bold text-gray-900">{review.task__title}</h2>
              <p className="text-sm text-gray-500 mt-1">
                by <span className="font-medium text-gray-700">{review['student__name']}</span>
                {review.completed_at && (
                  <span> · {new Date(review.completed_at).toLocaleDateString()}</span>
                )}
              </p>
            </div>
            <span className="px-3 py-1 bg-indigo-100 text-indigo-700 text-sm font-semibold rounded-full">
              {review.task__domain}
            </span>
          </div>
          {review.task__description && (
            <p className="mt-3 text-sm text-gray-600 border-t border-gray-100 pt-3">{review.task__description}</p>
          )}
          <div className="grid grid-cols-2 sm:grid-cols-3 gap-4 mt-4">
            <div className="bg-gray-50 rounded-lg p-3">
              <p className="text-xs text-gray-500 uppercase font-semibold">Difficulty</p>
              <p className="font-semibold text-gray-800 mt-0.5 capitalize">{review.task__difficulty || '—'}</p>
            </div>
            <div className="bg-gray-50 rounded-lg p-3">
              <p className="text-xs text-gray-500 uppercase font-semibold">Progress</p>
              <p className="font-semibold text-gray-800 mt-0.5">{review.progress_percentage ?? 0}%</p>
            </div>
            <div className="bg-blue-50 rounded-lg p-3">
              <p className="text-xs text-blue-600 uppercase font-semibold">MCQ Score</p>
              <p className={`font-bold mt-0.5 ${review.mcq_score != null ? scoreColor(review.mcq_score) : 'text-gray-400'}`}>
                {review.mcq_score != null ? `${review.mcq_score.toFixed(1)}%` : 'N/A'}
              </p>
            </div>
          </div>
        </div>

        {/* Student Reflection */}
        {review.reflective_text && (
          <div className="bg-blue-50 border border-blue-100 rounded-xl p-5 mb-5">
            <h3 className="text-sm font-semibold text-blue-800 mb-2">💬 Student's Reflection</h3>
            <p className="text-sm text-blue-700 leading-relaxed whitespace-pre-wrap">{review.reflective_text}</p>
          </div>
        )}

        {/* Score Input */}
        <div className="bg-white border border-gray-200 rounded-xl p-6 mb-5">
          <h3 className="text-base font-semibold text-gray-900 mb-4">🎯 Mentor Score (0–100)</h3>
          <div className="flex items-center gap-4 mb-3">
            <input
              type="range" min="0" max="100" step="1"
              value={mentorScore}
              onChange={(e) => setMentorScore(parseInt(e.target.value))}
              className="flex-1 h-2 accent-indigo-600"
            />
            <input
              type="number" min="0" max="100"
              value={mentorScore}
              onChange={(e) => setMentorScore(Math.min(100, Math.max(0, parseInt(e.target.value) || 0)))}
              className="w-20 text-center border border-gray-300 rounded-lg px-2 py-1.5 text-lg font-bold focus:outline-none focus:ring-2 focus:ring-indigo-500"
            />
          </div>
          <div className="w-full bg-gray-100 rounded-full h-2.5 mb-3">
            <div className={`h-2.5 rounded-full transition-all ${barColor(mentorScore)}`} style={{ width: `${mentorScore}%` }} />
          </div>
          {review.mcq_score != null && (
            <div className="flex items-center justify-between text-sm mt-3 bg-gray-50 rounded-lg px-4 py-3">
              <span className="text-gray-500">MCQ: <strong>{review.mcq_score.toFixed(1)}%</strong></span>
              <span className="text-gray-400">+</span>
              <span className="text-gray-500">Mentor: <strong>{mentorScore}%</strong></span>
              <span className="text-gray-400">=</span>
              <span className={`font-bold ${scoreColor(parseFloat(finalScore))}`}>
                Final: {finalScore}%
              </span>
            </div>
          )}
        </div>

        {/* Feedback */}
        <div className="bg-white border border-gray-200 rounded-xl p-6 mb-5">
          <h3 className="text-base font-semibold text-gray-900 mb-1">💬 Feedback <span className="text-red-500">*</span></h3>
          <p className="text-xs text-gray-500 mb-3">Detailed feedback that the student will see</p>
          <textarea
            value={feedback}
            onChange={(e) => setFeedback(e.target.value)}
            placeholder="Write your evaluation feedback here..."
            rows={5}
            className="w-full border border-gray-300 rounded-lg px-4 py-3 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500 resize-none"
          />
          <p className="text-xs text-gray-400 mt-1">{feedback.length} / 2000</p>
        </div>

        {/* Strengths / Weaknesses / Suggestions */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
          {[{ label: '💪 Strengths', state: strengths, setter: setStrengths, placeholder: 'One per line\nGood research skills\nClear presentation' },
            { label: '⚠️ Areas to Improve', state: weaknesses, setter: setWeaknesses, placeholder: 'One per line\nNeeds more detail\nPractice time management' },
            { label: '💡 Suggestions', state: suggestions, setter: setSuggestions, placeholder: 'One per line\nWatch tutorial X\nTry project Y' },
          ].map(({ label, state, setter, placeholder }) => (
            <div key={label}>
              <label className="block text-sm font-semibold text-gray-700 mb-1">{label}</label>
              <p className="text-xs text-gray-400 mb-2">One item per line (optional)</p>
              <textarea
                value={state}
                onChange={(e) => setter(e.target.value)}
                placeholder={placeholder}
                rows={4}
                className="w-full border border-gray-200 rounded-lg px-3 py-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500 resize-none"
              />
            </div>
          ))}
        </div>

        {/* Action Buttons */}
        <div className="flex gap-3">
          <button
            onClick={handleSubmit}
            disabled={submitting || !feedback.trim()}
            className="flex-1 py-3 bg-indigo-600 text-white rounded-xl font-semibold hover:bg-indigo-700 disabled:opacity-50 transition"
          >
            {submitting ? 'Submitting Evaluation...' : '✅ Submit Evaluation'}
          </button>
          <button
            onClick={() => navigate('/mentor/reviews')}
            disabled={submitting}
            className="px-6 py-3 border border-gray-300 text-gray-700 rounded-xl font-semibold hover:bg-gray-50 disabled:opacity-50 transition"
          >
            Cancel
          </button>
        </div>
      </div>
    </DashboardLayout>
  );
}
