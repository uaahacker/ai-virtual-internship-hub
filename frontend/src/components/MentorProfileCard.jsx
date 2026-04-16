import { Link } from 'react-router-dom';
import { FiUser, FiUsers, FiStar, FiArrowRight } from 'react-icons/fi';

export default function MentorProfileCard({ profile, user }) {
  if (!profile) {
    return (
      <div className="bg-white rounded-xl shadow-sm p-6 border border-gray-200">
        <div className="text-center py-8">
          <FiUser className="mx-auto text-gray-300 mb-3" size={32} />
          <p className="text-sm text-gray-500 mb-4">Profile not yet initialized.</p>
          <Link
            to="/mentor/profile"
            className="inline-flex items-center gap-2 px-4 py-2 bg-green-600 text-white rounded-lg text-sm font-medium hover:bg-green-700 transition"
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
          <div className="w-12 h-12 bg-gradient-to-br from-green-400 to-green-600 rounded-full flex items-center justify-center">
            <FiUser className="text-white" size={24} />
          </div>
          <div>
            <h3 className="font-semibold text-gray-900">{user?.name}</h3>
            <p className="text-xs text-gray-500">Mentor</p>
          </div>
        </div>
        <Link
          to="/mentor/profile"
          className="px-3 py-1 text-xs font-medium text-green-600 hover:text-green-700 hover:bg-green-50 rounded transition"
        >
          View Profile
        </Link>
      </div>

      <div className="space-y-4">
        {/* Students */}
        <div>
          <div className="flex items-center justify-between mb-2">
            <span className="text-xs font-semibold text-gray-700 flex items-center gap-1">
              <FiUsers size={14} />
              Students
            </span>
            <span className="text-sm font-bold text-green-600">
              {profile.current_student_count}/{profile.max_students}
            </span>
          </div>
          <div className="w-full bg-gray-200 rounded-full h-2">
            <div
              className="bg-green-500 h-2 rounded-full transition-all"
              style={{
                width: `${(profile.current_student_count / profile.max_students) * 100}%`,
              }}
            />
          </div>
        </div>

        {/* Rating & Availability */}
        <div className="grid grid-cols-2 gap-3 pt-2 border-t border-gray-200">
          <div>
            <p className="text-xs text-gray-500 mb-1 flex items-center gap-1">
              <FiStar size={12} />
              Rating
            </p>
            <p className="text-sm font-semibold text-yellow-600">{profile.rating.toFixed(1)}/5</p>
          </div>
          <div>
            <p className="text-xs text-gray-500 mb-1">Availability</p>
            <p
              className={`text-sm font-semibold ${
                profile.current_student_count < profile.max_students
                  ? 'text-green-600'
                  : 'text-red-600'
              }`}
            >
              {profile.current_student_count < profile.max_students ? 'Available' : 'Full'}
            </p>
          </div>
        </div>

        {/* Expertise Domains */}
        {profile.expertise_domains && profile.expertise_domains.length > 0 && (
          <div className="pt-3 border-t border-gray-200">
            <p className="text-xs font-semibold text-gray-700 mb-2">Expertise</p>
            <div className="flex flex-wrap gap-1">
              {profile.expertise_domains.slice(0, 3).map((domain, idx) => (
                <span
                  key={idx}
                  className="px-2 py-0.5 bg-green-100 text-green-700 rounded text-xs font-medium"
                >
                  {domain}
                </span>
              ))}
              {profile.expertise_domains.length > 3 && (
                <span className="px-2 py-0.5 bg-gray-100 text-gray-600 rounded text-xs font-medium">
                  +{profile.expertise_domains.length - 3}
                </span>
              )}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
