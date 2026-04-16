import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import { mentorService } from '../services/endpoints';
import { FiArrowLeft, FiCheckCircle } from 'react-icons/fi';

export default function MentorReviewTaskPage() {
  const { assignmentId } = useParams();
  const navigate = useNavigate();
  const { user } = useAuth();
  const [review, setReview] = useState(null);
  const [feedback, setFeedback] = useState('');
  const [status, setStatus] = useState('approved');
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');

  useEffect(() => {
    if (user?.role !== 'Mentor') {
      navigate('/');
      return;
    }
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
        } else {
          setError('Review not found');
        }
      } else {
        setError('Failed to load review');
      }
    } catch (err) {
      setError('Error loading review');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const handleSubmitReview = async () => {
    if (!feedback.trim()) {
      setError('Please enter feedback');
      return;
    }

    try {
      setSubmitting(true);
      setError('');
      const response = await mentorService.submitReview(assignmentId, {
        mentor_feedback: feedback,
        mentor_review_status: status,
      });

      if (response.data.success) {
        setSuccess('Review submitted successfully!');
        setTimeout(() => {
          navigate('/mentor/pending-reviews');
        }, 1500);
      } else {
        setError(response.data.error?.message || 'Failed to submit review');
      }
    } catch (err) {
      setError('Error submitting review');
      console.error(err);
    } finally {
      setSubmitting(false);
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 py-8 px-4">
        <div className="flex items-center justify-center py-16">
          <div className="text-center">
            <div className="inline-block w-8 h-8 border-4 border-gray-200 border-t-gray-900 rounded-full animate-spin mb-4"></div>
            <p className="text-gray-600">Loading review...</p>
          </div>
        </div>
      </div>
    );
  }

  if (!review) {
    return (
      <div className="min-h-screen bg-gray-50 py-8 px-4">
        <div className="max-w-3xl mx-auto">
          <button
            onClick={() => navigate('/mentor/pending-reviews')}
            className="mb-6 flex items-center gap-2 text-blue-600 hover:text-blue-700 font-medium"
          >
            <FiArrowLeft size={18} /> Back to Reviews
          </button>
          <div className="bg-white rounded-lg p-8 text-center border border-gray-200">
            <p className="text-gray-600 mb-4">{error || 'Review not found'}</p>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 py-8 px-4">
      <div className="max-w-3xl mx-auto">
        {/* Back Button */}
        <button
          onClick={() => navigate('/mentor/pending-reviews')}
          className="mb-6 flex items-center gap-2 text-blue-600 hover:text-blue-700 font-medium"
        >
          <FiArrowLeft size={18} /> Back to Reviews
        </button>

        {error && (
          <div className="mb-6 p-4 bg-red-50 border border-red-200 rounded text-red-700">
            {error}
          </div>
        )}

        {success && (
          <div className="mb-6 p-4 bg-green-50 border border-green-200 rounded text-green-700 flex items-center gap-2">
            <FiCheckCircle size={20} />
            {success}
          </div>
        )}

        {/* Task Information */}
        <div className="bg-white rounded-lg p-6 mb-6 border border-gray-200">
          <h1 className="text-3xl font-bold text-gray-900 mb-2">{review.task__title}</h1>
          <p className="text-gray-600 mb-4">From: {review.student__name}</p>

          <div className="grid grid-cols-2 md:grid-cols-4 gap-4 pt-4 border-t border-gray-200">
            <div>
              <p className="text-xs text-gray-600 uppercase">Domain</p>
              <p className="font-semibold text-gray-900 mt-1">{review.task__domain}</p>
            </div>
            <div>
              <p className="text-xs text-gray-600 uppercase">Status</p>
              <p className="font-semibold text-gray-900 mt-1 capitalize">{review.status}</p>
            </div>
            <div>
              <p className="text-xs text-gray-600 uppercase">Progress</p>
              <p className="font-semibold text-gray-900 mt-1">{review.progress_percentage}%</p>
            </div>
            <div>
              <p className="text-xs text-gray-600 uppercase">Completed</p>
              <p className="font-semibold text-gray-900 mt-1">
                {review.completed_at
                  ? new Date(review.completed_at).toLocaleDateString()
                  : 'N/A'}
              </p>
            </div>
          </div>
        </div>

        {/* Review Form */}
        <div className="bg-white rounded-lg p-6 border border-gray-200">
          <h2 className="text-2xl font-bold text-gray-900 mb-6">Submit Your Review</h2>

          {/* Approval Status */}
          <div className="mb-6">
            <label className="block text-sm font-medium text-gray-700 mb-3">
              Approval Status
            </label>
            <div className="space-y-3">
              <label className="flex items-center">
                <input
                  type="radio"
                  name="status"
                  value="approved"
                  checked={status === 'approved'}
                  onChange={(e) => setStatus(e.target.value)}
                  className="w-4 h-4 text-gray-900"
                />
                <span className="ml-3 text-gray-700">
                  <span className="font-medium">Approved ✓</span>
                  <p className="text-sm text-gray-500">Task completed successfully</p>
                </span>
              </label>
              <label className="flex items-center">
                <input
                  type="radio"
                  name="status"
                  value="needs_revision"
                  checked={status === 'needs_revision'}
                  onChange={(e) => setStatus(e.target.value)}
                  className="w-4 h-4 text-gray-900"
                />
                <span className="ml-3 text-gray-700">
                  <span className="font-medium">Needs Revision</span>
                  <p className="text-sm text-gray-500">Task requires improvements</p>
                </span>
              </label>
            </div>
          </div>

          {/* Feedback Text */}
          <div className="mb-6">
            <label htmlFor="feedback" className="block text-sm font-medium text-gray-700 mb-2">
              Feedback & Comments
            </label>
            <textarea
              id="feedback"
              value={feedback}
              onChange={(e) => setFeedback(e.target.value)}
              placeholder="Provide detailed feedback for the student..."
              rows="8"
              maxLength={1000}
              className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-gray-900 resize-none"
            />
            <p className="text-xs text-gray-500 mt-2">
              {feedback.length}/1000 characters
            </p>
          </div>

          {/* Action Buttons */}
          <div className="flex gap-3">
            <button
              onClick={handleSubmitReview}
              disabled={submitting}
              className="flex-1 px-6 py-3 bg-gray-900 text-white rounded-lg hover:bg-gray-800 disabled:opacity-50 font-medium transition"
            >
              {submitting ? 'Submitting...' : 'Submit Review'}
            </button>
            <button
              onClick={() => navigate('/mentor/pending-reviews')}
              disabled={submitting}
              className="flex-1 px-6 py-3 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 disabled:opacity-50 font-medium transition"
            >
              Cancel
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
