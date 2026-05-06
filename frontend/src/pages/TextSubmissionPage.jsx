import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import { taskService, submissionService } from '../services/endpoints';
import DashboardLayout from '../components/DashboardLayout';

// ── Score helpers ─────────────────────────────────────────────────────────────

function ScoreCircle({ value, label, color = 'blue' }) {
  const colors = {
    blue:   { ring: 'stroke-blue-500',   bg: 'text-blue-600' },
    green:  { ring: 'stroke-green-500',  bg: 'text-green-600' },
    orange: { ring: 'stroke-orange-400', bg: 'text-orange-600' },
    red:    { ring: 'stroke-red-400',    bg: 'text-red-600' },
    purple: { ring: 'stroke-purple-500', bg: 'text-purple-600' },
  };
  const c = colors[color] || colors.blue;
  const pct = Math.min(100, Math.max(0, value));
  const circumference = 2 * Math.PI * 28; // r=28
  const dashOffset = circumference * (1 - pct / 100);

  return (
    <div className="flex flex-col items-center">
      <svg width="72" height="72" viewBox="0 0 72 72">
        <circle cx="36" cy="36" r="28" fill="none" stroke="#e5e7eb" strokeWidth="5" />
        <circle
          cx="36" cy="36" r="28" fill="none"
          className={c.ring} strokeWidth="5"
          strokeDasharray={circumference} strokeDashoffset={dashOffset}
          strokeLinecap="round" transform="rotate(-90 36 36)"
        />
        <text x="36" y="40" textAnchor="middle" fontSize="14" fontWeight="700" className={c.bg} fill="currentColor">
          {Math.round(pct)}
        </text>
      </svg>
      <span className="text-xs text-gray-500 mt-0.5 text-center">{label}</span>
    </div>
  );
}

function ReadinessBadge({ label }) {
  const styles = {
    'Excellent':    'bg-green-100 text-green-800 border-green-200',
    'Good':         'bg-blue-100 text-blue-800 border-blue-200',
    'Satisfactory': 'bg-yellow-100 text-yellow-800 border-yellow-200',
    'Needs Work':   'bg-red-100 text-red-800 border-red-200',
  };
  return (
    <span className={`inline-block px-3 py-1 text-sm font-semibold rounded-full border ${styles[label] || styles['Needs Work']}`}>
      {label}
    </span>
  );
}

// ── Main page ─────────────────────────────────────────────────────────────────

export default function TextSubmissionPage() {
  const { assignmentId } = useParams();
  const { user } = useAuth();
  const navigate = useNavigate();

  const [assignment, setAssignment] = useState(null);
  const [existingSubmission, setExistingSubmission] = useState(null);
  const [textContent, setTextContent] = useState('');
  const [notes, setNotes] = useState('');
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState('');
  const [evalResult, setEvalResult] = useState(null);

  const wordCount = textContent.trim().split(/\s+/).filter(Boolean).length;

  useEffect(() => {
    if (!user) { navigate('/login'); return; }
    loadData();
  }, [assignmentId]);

  const loadData = async () => {
    setLoading(true);
    try {
      const [assignRes, subRes] = await Promise.all([
        taskService.getAssignmentDetail(assignmentId),
        submissionService.getByAssignment(assignmentId),
      ]);
      if (assignRes.data.success) setAssignment(assignRes.data.data);
      if (subRes.data.success && subRes.data.data) {
        const sub = subRes.data.data;
        setExistingSubmission(sub);
        setTextContent(sub.text_content || '');
        setNotes(sub.notes || '');
        if (sub.ai_evaluation) setEvalResult(sub.ai_evaluation);
      }
    } catch (err) {
      setError('Error loading assignment details.');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = async () => {
    if (!textContent.trim()) { setError('Please write your submission before submitting.'); return; }
    if (wordCount < 20) { setError('Your submission is too short. Please write at least 20 words.'); return; }
    setError('');
    setSubmitting(true);
    try {
      const res = await submissionService.submitText({
        assignment_id: parseInt(assignmentId, 10),
        text_content: textContent,
        notes,
      });
      if (res.data.success) {
        const sub = res.data.data;
        setExistingSubmission(sub);
        setEvalResult(sub.ai_evaluation || null);
      } else {
        setError(res.data.error?.text_content?.[0] || res.data.error || 'Submission failed.');
      }
    } catch (err) {
      setError(err.response?.data?.error?.text_content?.[0] || 'Error submitting work. Please try again.');
    } finally {
      setSubmitting(false);
    }
  };

  if (loading) {
    return (
      <DashboardLayout>
        <div className="flex items-center justify-center py-20">
          <div className="text-center">
            <div className="inline-block w-8 h-8 border-4 border-gray-200 border-t-blue-600 rounded-full animate-spin mb-3" />
            <p className="text-gray-500 text-sm">Loading assignment...</p>
          </div>
        </div>
      </DashboardLayout>
    );
  }

  return (
    <DashboardLayout>
      <div className="max-w-3xl mx-auto pb-12 px-4">

        {/* Back button */}
        <button
          onClick={() => navigate('/student/tasks/my-tasks')}
          className="flex items-center gap-2 text-sm text-gray-500 hover:text-gray-800 mb-6 mt-2"
        >
          ← Back to My Tasks
        </button>

        {/* Task info */}
        {assignment && (
          <div className="bg-white rounded-xl border border-gray-100 shadow-sm p-5 mb-6">
            <div className="flex flex-wrap gap-2 mb-2">
              <span className="px-2 py-0.5 bg-blue-50 text-blue-700 text-xs rounded-full font-medium">
                {assignment.task?.domain || assignment.domain}
              </span>
              <span className="px-2 py-0.5 bg-gray-100 text-gray-600 text-xs rounded-full">
                {assignment.task?.difficulty || assignment.difficulty}
              </span>
              <span className="px-2 py-0.5 bg-purple-50 text-purple-700 text-xs rounded-full">
                {assignment.task?.task_type || assignment.task_type}
              </span>
            </div>
            <h1 className="text-xl font-bold text-gray-900">
              {assignment.task?.title || assignment.title}
            </h1>
            {assignment.task?.description && (
              <p className="mt-2 text-sm text-gray-600">{assignment.task.description}</p>
            )}
          </div>
        )}

        {/* AI Evaluation result (shown after submission) */}
        {evalResult && (
          <div className="bg-white rounded-xl border border-gray-100 shadow-sm p-6 mb-6">
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-lg font-semibold text-gray-900">AI Evaluation Result</h2>
              <ReadinessBadge label={evalResult.readiness_label} />
            </div>

            {/* Score circles */}
            <div className="flex flex-wrap justify-around gap-4 py-4 border-y border-gray-100 mb-5">
              <ScoreCircle value={evalResult.ai_score} label="Overall" color="blue" />
              <ScoreCircle value={evalResult.readability_score} label="Readability" color="purple" />
              <ScoreCircle value={evalResult.vocabulary_diversity} label="Vocabulary" color="green" />
              <ScoreCircle value={evalResult.grammar_score} label="Grammar" color="orange" />
              <ScoreCircle value={evalResult.originality_score} label="Originality" color={evalResult.originality_score >= 70 ? 'green' : 'red'} />
            </div>

            {/* Stats row */}
            <div className="flex flex-wrap gap-4 text-sm text-gray-600 mb-5">
              <span>{evalResult.word_count} words</span>
              <span>·</span>
              <span>{evalResult.sentence_count} sentences</span>
            </div>

            {/* Strengths */}
            {evalResult.strengths?.length > 0 && (
              <div className="mb-4">
                <h3 className="text-sm font-semibold text-green-700 mb-2">Strengths</h3>
                <ul className="space-y-1">
                  {evalResult.strengths.map((s, i) => (
                    <li key={i} className="flex items-start gap-2 text-sm text-gray-700">
                      <span className="text-green-500 mt-0.5">✓</span>
                      <span>{s}</span>
                    </li>
                  ))}
                </ul>
              </div>
            )}

            {/* Areas for improvement */}
            {evalResult.improvements?.length > 0 && (
              <div className="mb-4">
                <h3 className="text-sm font-semibold text-orange-700 mb-2">Areas for Improvement</h3>
                <ul className="space-y-1">
                  {evalResult.improvements.map((s, i) => (
                    <li key={i} className="flex items-start gap-2 text-sm text-gray-700">
                      <span className="text-orange-400 mt-0.5">→</span>
                      <span>{s}</span>
                    </li>
                  ))}
                </ul>
              </div>
            )}

            {/* Grammar issues */}
            {evalResult.grammar_issues?.length > 0 && (
              <div className="mb-4">
                <h3 className="text-sm font-semibold text-red-700 mb-2">Grammar Issues Detected</h3>
                <ul className="space-y-1">
                  {evalResult.grammar_issues.map((issue, i) => (
                    <li key={i} className="text-xs text-red-700 bg-red-50 px-2 py-1 rounded">
                      {issue}
                    </li>
                  ))}
                </ul>
              </div>
            )}

            <p className="text-xs text-gray-400 mt-4">
              You can re-submit to improve your score. The latest submission will be evaluated.
            </p>
          </div>
        )}

        {/* Text submission form */}
        <div className="bg-white rounded-xl border border-gray-100 shadow-sm p-6">
          <h2 className="text-lg font-semibold text-gray-900 mb-1">
            {existingSubmission ? 'Update Your Submission' : 'Submit Your Work'}
          </h2>
          <p className="text-sm text-gray-500 mb-4">
            Write your response below. Your submission will be automatically evaluated for readability,
            vocabulary, grammar, and originality.
          </p>

          {error && (
            <div className="mb-4 p-3 bg-red-50 border border-red-200 rounded-lg text-sm text-red-700">
              {error}
            </div>
          )}

          <div className="mb-4">
            <div className="flex justify-between items-center mb-1">
              <label className="text-sm font-medium text-gray-700">Your Written Work</label>
              <span className={`text-xs ${wordCount < 20 ? 'text-red-500' : wordCount >= 200 ? 'text-green-600' : 'text-yellow-600'}`}>
                {wordCount} words {wordCount < 200 ? `(aim for 200+)` : '✓'}
              </span>
            </div>
            <textarea
              value={textContent}
              onChange={(e) => setTextContent(e.target.value)}
              rows={14}
              placeholder="Write your submission here. Be thorough — at least 200 words recommended for a good evaluation score. For Content Writing tasks, include an introduction, body with supporting details, and a conclusion."
              className="w-full border border-gray-200 rounded-lg p-3 text-sm text-gray-800 placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-500 resize-y"
            />
          </div>

          <div className="mb-5">
            <label className="text-sm font-medium text-gray-700 block mb-1">Notes (optional)</label>
            <input
              type="text"
              value={notes}
              onChange={(e) => setNotes(e.target.value)}
              placeholder="Any notes for your mentor..."
              maxLength={500}
              className="w-full border border-gray-200 rounded-lg p-2.5 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>

          <div className="flex gap-3">
            <button
              onClick={handleSubmit}
              disabled={submitting || !textContent.trim()}
              className="flex-1 py-2.5 bg-blue-600 text-white rounded-lg font-medium text-sm hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
            >
              {submitting ? (
                <span className="flex items-center justify-center gap-2">
                  <span className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin" />
                  Evaluating...
                </span>
              ) : existingSubmission ? 'Re-submit & Re-evaluate' : 'Submit & Evaluate'}
            </button>
            <button
              onClick={() => navigate('/student/tasks/my-tasks')}
              className="px-5 py-2.5 bg-gray-100 text-gray-700 rounded-lg font-medium text-sm hover:bg-gray-200 transition-colors"
            >
              Cancel
            </button>
          </div>
        </div>
      </div>
    </DashboardLayout>
  );
}
