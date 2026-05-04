import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import DashboardLayout from '../components/DashboardLayout';
import { assessmentService } from '../services/endpoints';
import { toast } from 'react-toastify';
import { FiClock, FiChevronLeft, FiChevronRight, FiSend } from 'react-icons/fi';
import ConfirmModal from '../components/ConfirmModal';

export default function TakeAssessment() {
  const { id } = useParams();
  const navigate = useNavigate();
  const [assessment, setAssessment] = useState(null);
  const [loading, setLoading] = useState(true);
  const [answers, setAnswers] = useState({});
  const [currentQ, setCurrentQ] = useState(0);
  const [submitting, setSubmitting] = useState(false);
  const [confirmModal, setConfirmModal] = useState(null);

  useEffect(() => {
    assessmentService.detail(id)
      .then((res) => setAssessment(res.data.data))
      .catch(() => toast.error('Failed to load assessment.'))
      .finally(() => setLoading(false));
  }, [id]);

  const handleSelect = (questionId, option) => {
    setAnswers({ ...answers, [String(questionId)]: option });
  };

  const handleSubmit = async () => {
    if (!assessment) return;
    const total = assessment.questions.length;
    const answered = Object.keys(answers).length;

    const doSubmit = async () => {
      setSubmitting(true);
      try {
        const res = await assessmentService.submit(id, answers);
        toast.success('Assessment submitted!');
        navigate(`/student/results/${res.data.data.id}`);
      } catch (err) {
        const msg = err.response?.data?.error?.message || 'Submission failed.';
        toast.error(msg);
      } finally {
        setSubmitting(false);
      }
    };

    if (answered < total) {
      setConfirmModal({
        title: 'Submit with unanswered questions?',
        message: `You've answered ${answered} of ${total} questions. Unanswered questions will be marked wrong.`,
        confirmLabel: 'Submit Anyway',
        danger: false,
        onConfirm: doSubmit,
      });
    } else {
      await doSubmit();
    }
  };

  if (loading) {
    return (
      <DashboardLayout>
        <div className="text-center py-16 text-gray-400">Loading assessment...</div>
      </DashboardLayout>
    );
  }

  if (!assessment) {
    return (
      <DashboardLayout>
        <div className="text-center py-16 text-gray-400">Assessment not found.</div>
      </DashboardLayout>
    );
  }

  const questions = assessment.questions || [];
  const question = questions[currentQ];
  const totalQ = questions.length;

  return (
    <DashboardLayout>
      {/* Header */}
      <div className="mb-6">
        <h1 className="text-2xl font-bold text-gray-900">{assessment.title}</h1>
        <p className="text-gray-500 mt-1">{assessment.domain} • {totalQ} questions</p>
      </div>

      {/* Progress bar */}
      <div className="mb-6">
        <div className="flex items-center justify-between text-xs text-gray-500 mb-1">
          <span>Question {currentQ + 1} of {totalQ}</span>
          <span>{Object.keys(answers).length} answered</span>
        </div>
        <div className="w-full bg-gray-200 rounded-full h-2">
          <div
            className="bg-primary-600 h-2 rounded-full transition-all"
            style={{ width: `${((currentQ + 1) / totalQ) * 100}%` }}
          />
        </div>
      </div>

      {/* Question card */}
      <div className="bg-white rounded-xl shadow-sm p-8 mb-6">
        <h2 className="text-lg font-semibold text-gray-800 mb-6">
          {currentQ + 1}. {question.text}
        </h2>

        <div className="space-y-3">
          {Object.entries(question.options).map(([key, value]) => {
            const selected = answers[String(question.id)] === key;
            return (
              <button
                key={key}
                onClick={() => handleSelect(question.id, key)}
                className={`w-full text-left p-4 rounded-lg border-2 transition flex items-center gap-3 ${
                  selected
                    ? 'border-primary-600 bg-primary-50 text-primary-800'
                    : 'border-gray-200 hover:border-primary-300 hover:bg-gray-50 text-gray-700'
                }`}
              >
                <span className={`w-8 h-8 rounded-full border-2 flex items-center justify-center text-sm font-bold flex-shrink-0 ${
                  selected
                    ? 'border-primary-600 bg-primary-600 text-white'
                    : 'border-gray-300 text-gray-500'
                }`}>
                  {key}
                </span>
                <span className="text-sm">{value}</span>
              </button>
            );
          })}
        </div>
      </div>

      {/* Navigation buttons */}
      <div className="flex items-center justify-between">
        <button
          onClick={() => setCurrentQ(Math.max(0, currentQ - 1))}
          disabled={currentQ === 0}
          className="flex items-center gap-2 px-4 py-2 border border-gray-300 rounded-lg text-sm font-medium text-gray-600 hover:bg-gray-50 disabled:opacity-40 transition"
        >
          <FiChevronLeft /> Previous
        </button>

        <div className="flex gap-2">
          {/* Question indicators */}
          {questions.map((q, idx) => (
            <button
              key={q.id}
              onClick={() => setCurrentQ(idx)}
              className={`w-8 h-8 rounded-full text-xs font-medium transition ${
                idx === currentQ
                  ? 'bg-primary-600 text-white'
                  : answers[String(q.id)]
                    ? 'bg-green-100 text-green-700 border border-green-300'
                    : 'bg-gray-100 text-gray-500 hover:bg-gray-200'
              }`}
            >
              {idx + 1}
            </button>
          ))}
        </div>

        {currentQ < totalQ - 1 ? (
          <button
            onClick={() => setCurrentQ(currentQ + 1)}
            className="flex items-center gap-2 px-4 py-2 bg-primary-600 text-white rounded-lg text-sm font-medium hover:bg-primary-700 transition"
          >
            Next <FiChevronRight />
          </button>
        ) : (
          <button
            onClick={handleSubmit}
            disabled={submitting}
            className="flex items-center gap-2 px-6 py-2 bg-green-600 text-white rounded-lg text-sm font-semibold hover:bg-green-700 transition disabled:opacity-50"
          >
            <FiSend /> {submitting ? 'Submitting...' : 'Submit Assessment'}
          </button>
        )}
      </div>
      <ConfirmModal config={confirmModal} onClose={() => setConfirmModal(null)} />
    </DashboardLayout>
  );
}
