import { Link } from 'react-router-dom';
import { FiUser, FiBarChart2, FiTarget, FiArrowRight } from 'react-icons/fi';

export default function StudentProfileCard({ profile, user }) {
  if (!profile) {
    return (
      <div className="bg-white rounded-xl shadow-sm p-6 border border-gray-200">
        <div className="text-center py-8">
          <FiUser className="mx-auto text-gray-300 mb-3" size={32} />
          <p className="text-sm text-gray-500 mb-4">Profile not yet initialized.</p>
          <Link
            to="/student/profile"
            className="inline-flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg text-sm font-medium hover:bg-blue-700 transition"
          >
            Create Profile
            <FiArrowRight size={16} />
          </Link>
        </div>
      </div>
    );
  }

  return (
    <div className="bg-white rounded-xl shadow-sm p-6 border border-gray-200">
      <div className="flex items-start justify-between mb-6">
        <div className="flex items-center gap-4">
          <div className="w-12 h-12 bg-gradient-to-br from-blue-400 to-blue-600 rounded-full flex items-center justify-center">
            <FiUser className="text-white" size={24} />
          </div>
          <div>
            <h3 className="font-semibold text-gray-900">{user?.name}</h3>
            <p className="text-xs text-gray-500">Student</p>
          </div>
        </div>
        <Link
          to="/student/profile"
          className="px-3 py-1 text-xs font-medium text-blue-600 hover:text-blue-700 hover:bg-blue-50 rounded transition"
        >
          View Profile
        </Link>
      </div>

      <div className="space-y-4">
        {/* Progress */}
        <div>
          <div className="flex items-center justify-between mb-2">
            <span className="text-xs font-semibold text-gray-700 flex items-center gap-1">
              <FiBarChart2 size={14} />
              Progress
            </span>
            <span className="text-sm font-bold text-blue-600">{Math.round(profile.progress_score)}%</span>
          </div>
          <div className="w-full bg-gray-200 rounded-full h-2">
            <div
              className="bg-blue-500 h-2 rounded-full transition-all"
              style={{ width: `${Math.min(profile.progress_score, 100)}%` }}
            />
          </div>
        </div>

        {/* Domain Stats */}
        <div className="grid grid-cols-2 gap-3 pt-2 border-t border-gray-200">
          <div>
            <p className="text-xs text-gray-500 mb-1">Strongest</p>
            <p className="text-sm font-semibold text-gray-900 truncate">
              {profile.strongest_domain || 'N/A'}
            </p>
          </div>
          <div>
            <p className="text-xs text-gray-500 mb-1">Tasks Done</p>
            <p className="text-sm font-semibold text-gray-900">{profile.completed_tasks_count}</p>
          </div>
        </div>

        {/* Skills */}
        {profile.selected_skills && profile.selected_skills.length > 0 && (
          <div className="pt-3 border-t border-gray-200">
            <p className="text-xs font-semibold text-gray-700 mb-2 flex items-center gap-1">
              <FiTarget size={12} />
              Skills
            </p>
            <div className="flex flex-wrap gap-1">
              {profile.selected_skills.slice(0, 3).map((skill, idx) => (
                <span
                  key={idx}
                  className="px-2 py-0.5 bg-blue-100 text-blue-700 rounded text-xs font-medium"
                >
                  {skill}
                </span>
              ))}
              {profile.selected_skills.length > 3 && (
                <span className="px-2 py-0.5 bg-gray-100 text-gray-600 rounded text-xs font-medium">
                  +{profile.selected_skills.length - 3}
                </span>
              )}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
