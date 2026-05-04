// Reusable task card component for displaying task information.
import { useState } from 'react';

function ExplanationPanel({ explanation }) {
  if (!explanation || !explanation.components) return null;

  const components = explanation.components || {};
  const rows = [
    {
      key: 'domain_match',
      label: 'Domain match',
      data: components.domain_match || explanation.domain_match,
      icon: '🎯',
    },
    {
      key: 'concept_overlap',
      label: 'Concept overlap',
      data: components.concept_overlap || explanation.concept_overlap,
      icon: '🧠',
    },
    {
      key: 'difficulty_fit',
      label: 'Difficulty fit',
      data: components.difficulty_fit || explanation.difficulty_fit,
      icon: '📈',
    },
    {
      key: 'task_history',
      label: 'Task history',
      data: components.task_history || explanation.task_history,
      icon: '📋',
    },
    {
      key: 'preferred_domain',
      label: 'Preferred domain',
      data: components.preferred_domain || explanation.preferred_domain,
      icon: '⭐',
    },
    {
      key: 'collaborative',
      label: 'Peer signal',
      data: components.collaborative || explanation.collaborative,
      icon: '👥',
    },
  ].filter((r) => r.data && typeof r.data.score === 'number');

  if (rows.length === 0) return null;

  return (
    <div className="mt-3 space-y-2">
      {rows.map(({ key, label, data, icon }) => (
        <div key={key}>
          <div className="flex justify-between text-xs mb-0.5">
            <span className="text-gray-600">
              {icon} {label}
              {data.label ? <span className="ml-1 text-gray-400">— {data.label}</span> : null}
            </span>
            <span className="font-medium text-gray-700">{Math.round(data.score)}%</span>
          </div>
          <div className="h-1.5 bg-gray-100 rounded-full overflow-hidden">
            <div
              className={`h-full rounded-full transition-all ${
                data.score >= 75
                  ? 'bg-green-500'
                  : data.score >= 50
                  ? 'bg-blue-500'
                  : data.score >= 25
                  ? 'bg-yellow-500'
                  : 'bg-gray-300'
              }`}
              style={{ width: `${Math.min(100, Math.round(data.score))}%` }}
            />
          </div>
          {data.detail && (
            <p className="text-xs text-gray-400 mt-0.5">{data.detail}</p>
          )}
          {data.matched_concepts?.length > 0 && (
            <div className="flex flex-wrap gap-1 mt-1">
              {data.matched_concepts.slice(0, 4).map((c) => (
                <span
                  key={c}
                  className="px-1.5 py-0.5 text-xs bg-blue-50 text-blue-700 rounded"
                >
                  {c}
                </span>
              ))}
            </div>
          )}
        </div>
      ))}
    </div>
  );
}

export default function TaskCard({
  task,
  isRecommended = false,
  matchScore = null,
  reason = '',
  explanation = null,
  onAccept = null,
  onDecline = null,
}) {
  const [showWhy, setShowWhy] = useState(false);
  const taskData = task.task_details || task;

  // The explanation may be nested under task.recommendation_explanation
  const structuredExplanation =
    explanation ||
    task.recommendation_explanation ||
    null;

  const DIFFICULTY_COLORS = {
    Beginner: 'bg-green-100 text-green-800',
    Intermediate: 'bg-yellow-100 text-yellow-800',
    Advanced: 'bg-red-100 text-red-800',
  };

  return (
    <div className="bg-white rounded-lg border border-gray-200 p-6 hover:shadow-lg transition-shadow">
      <div className="mb-4">
        <div className="flex items-start justify-between mb-2">
          <h3 className="text-lg font-bold text-gray-900 flex-1">
            {taskData.title}
          </h3>
          {matchScore !== null && isRecommended && (
            <div className="ml-4 text-right">
              <div className="text-2xl font-bold text-gray-900">
                {Math.round(matchScore)}%
              </div>
              <div className="text-xs text-gray-500">Match</div>
            </div>
          )}
        </div>
        <p className="text-sm text-gray-600">{taskData.domain}</p>
      </div>

      <p className="text-gray-600 text-sm mb-4 line-clamp-2">
        {taskData.description}
      </p>

      <div className="flex items-center gap-2 mb-4">
        <span
          className={`px-2 py-1 text-xs font-medium rounded ${
            DIFFICULTY_COLORS[taskData.difficulty] || 'bg-gray-100 text-gray-800'
          }`}
        >
          {taskData.difficulty}
        </span>
        <span className="text-xs text-gray-500">
          ⏱ {taskData.estimated_duration} mins
        </span>
        {taskData.task_type && (
          <span className="text-xs text-gray-500 bg-gray-50 px-1.5 py-0.5 rounded">
            {taskData.task_type}
          </span>
        )}
      </div>

      {isRecommended && reason && (
        <div className="mb-3 p-3 bg-blue-50 border border-blue-200 rounded">
          <p className="text-xs text-blue-900">
            <span className="font-semibold">Why recommended: </span>
            {reason}
          </p>
        </div>
      )}

      {isRecommended && structuredExplanation && (
        <div className="mb-3">
          <button
            onClick={() => setShowWhy((v) => !v)}
            className="text-xs text-blue-600 hover:text-blue-800 font-medium flex items-center gap-1"
          >
            {showWhy ? '▲ Hide' : '▼ Show'} score breakdown
          </button>
          {showWhy && (
            <div className="mt-2 p-3 bg-gray-50 border border-gray-200 rounded">
              <ExplanationPanel explanation={structuredExplanation} />
              {structuredExplanation.learning_outcomes?.length > 0 && (
                <div className="mt-3">
                  <p className="text-xs font-medium text-gray-700 mb-1">
                    You&apos;ll learn:
                  </p>
                  <ul className="space-y-0.5">
                    {structuredExplanation.learning_outcomes.slice(0, 3).map((o, i) => (
                      <li key={i} className="text-xs text-gray-600 flex items-start gap-1">
                        <span className="text-green-500 mt-0.5">✓</span> {o}
                      </li>
                    ))}
                  </ul>
                </div>
              )}
            </div>
          )}
        </div>
      )}

      {taskData.required_skills?.length > 0 && (
        <div className="mb-4">
          <p className="text-xs font-medium text-gray-700 mb-2">Required Skills:</p>
          <div className="flex flex-wrap gap-1">
            {taskData.required_skills.slice(0, 3).map((skill, idx) => (
              <span key={idx} className="px-2 py-1 text-xs bg-gray-100 text-gray-700 rounded">
                {skill}
              </span>
            ))}
            {taskData.required_skills.length > 3 && (
              <span className="px-2 py-1 text-xs text-gray-500">
                +{taskData.required_skills.length - 3} more
              </span>
            )}
          </div>
        </div>
      )}

      {isRecommended && onAccept && onDecline && (
        <div className="flex gap-2 pt-4 border-t border-gray-200">
          <button
            onClick={onAccept}
            className="flex-1 px-3 py-2 bg-gray-900 text-white text-sm font-medium rounded hover:bg-gray-800 transition"
          >
            Accept Task
          </button>
          <button
            onClick={onDecline}
            className="flex-1 px-3 py-2 border border-gray-300 text-gray-700 text-sm font-medium rounded hover:bg-gray-50 transition"
          >
            Decline
          </button>
        </div>
      )}
    </div>
  );
}

