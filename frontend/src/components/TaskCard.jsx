// Reusable task card component for displaying task information.

export default function TaskCard({
  task,
  isRecommended = false,
  matchScore = null,
  reason = '',
  onAccept = null,
  onDecline = null,
}) {
  const taskData = task.task_details || task;

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
      </div>

      {isRecommended && reason && (
        <div className="mb-4 p-3 bg-blue-50 border border-blue-200 rounded">
          <p className="text-xs text-blue-900">
            <span className="font-semibold">Why recommended: </span>
            {reason}
          </p>
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
