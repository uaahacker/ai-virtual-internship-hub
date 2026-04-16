import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import DashboardLayout from '../components/DashboardLayout';
import StudentProfileCard from '../components/StudentProfileCard';
import { useAuth } from '../contexts/AuthContext';
import { assessmentService, profileService } from '../services/endpoints';
import { FiTrendingUp, FiClipboard, FiAward, FiArrowRight, FiBarChart2 } from 'react-icons/fi';

export default function StudentDashboard() {
  const { user } = useAuth();
  const [attempts, setAttempts] = useState([]);
  const [profile, setProfile] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const loadData = async () => {
      try {
        const [attemptsRes, profileRes] = await Promise.all([
          assessmentService.myAttempts(),
          profileService.getStudentProfile(),
        ]);
        setAttempts(attemptsRes.data.data || []);
        setProfile(profileRes.data.data);
      } catch (err) {
        console.error('Failed to load dashboard data:', err);
      } finally {
        setLoading(false);
      }
    };
    loadData();
  }, []);

  // Derive skill overview from latest attempts per domain
  const skillMap = {};
  attempts.forEach((a) => {
    const domain = a.assessment_domain;
    if (!skillMap[domain] || new Date(a.attempted_at) > new Date(skillMap[domain].attempted_at)) {
      skillMap[domain] = a;
    }
  });
  const skills = Object.values(skillMap);

  const levelColor = (level) => {
    if (level === 'Advanced') return 'text-green-600 bg-green-100';
    if (level === 'Intermediate') return 'text-yellow-600 bg-yellow-100';
    return 'text-red-500 bg-red-100';
  };

  const barColor = (pct) => {
    if (pct >= 80) return 'bg-green-500';
    if (pct >= 50) return 'bg-yellow-500';
    return 'bg-red-400';
  };

  return (
    <DashboardLayout>
      {/* Welcome header */}
      <div className="mb-8">
        <h1 className="text-2xl font-bold text-gray-900">
          Welcome, {user?.name}!
        </h1>
        <p className="text-gray-500 mt-1">Here's your skill overview and assessment history.</p>
      </div>

      {/* Profile Card */}
      {!loading && (
        <div className="mb-8">
          <StudentProfileCard profile={profile} user={user} />
        </div>
      )}

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Skill Overview Card */}
        <div className="lg:col-span-2 bg-white rounded-xl shadow-sm p-6">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-lg font-semibold text-gray-800 flex items-center gap-2">
              <FiTrendingUp className="text-primary-600" />
              Skill Overview
            </h2>
            {skills.length > 0 && (
              <span className="text-xs text-gray-400">{skills.length} domain(s) assessed</span>
            )}
          </div>

          {loading ? (
            <div className="text-center py-8 text-gray-400">Loading...</div>
          ) : skills.length === 0 ? (
            <div className="text-center py-8">
              <FiClipboard className="mx-auto text-gray-300 mb-3" size={40} />
              <p className="text-gray-500">No assessments taken yet.</p>
              <Link
                to="/student/assessments"
                className="inline-flex items-center gap-2 mt-4 px-4 py-2 bg-primary-600 text-white rounded-lg text-sm font-medium hover:bg-primary-700 transition"
              >
                Take Your First Assessment <FiArrowRight />
              </Link>
            </div>
          ) : (
            <div className="space-y-4">
              {skills.map((s) => (
                <div key={s.assessment_domain} className="flex items-center gap-4">
                  <div className="w-36 text-sm font-medium text-gray-700 truncate">
                    {s.assessment_domain}
                  </div>
                  <div className="flex-1 bg-gray-100 rounded-full h-3">
                    <div
                      className={`h-3 rounded-full transition-all ${barColor(s.percentage)}`}
                      style={{ width: `${Math.min(s.percentage, 100)}%` }}
                    />
                  </div>
                  <span className="text-sm font-semibold text-gray-700 w-12 text-right">
                    {s.percentage}%
                  </span>
                  <span className={`text-xs font-medium px-2 py-1 rounded-full ${levelColor(s.skill_level)}`}>
                    {s.skill_level}
                  </span>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Quick actions / CTA */}
        <div className="space-y-6">
          <div className="bg-white rounded-xl shadow-sm p-6">
            <h2 className="text-lg font-semibold text-gray-800 flex items-center gap-2 mb-4">
              <FiAward className="text-primary-600" />
              Take Assessment
            </h2>
            <p className="text-sm text-gray-500 mb-4">
              Assess your skills across multiple DigiSkills domains and get personalized recommendations.
            </p>
            <Link
              to="/student/assessments"
              className="inline-flex items-center gap-2 px-5 py-3 bg-primary-600 text-white rounded-lg font-semibold hover:bg-primary-700 transition w-full justify-center"
            >
              Browse Assessments <FiArrowRight />
            </Link>
          </div>

          {/* View Portfolio */}
          <div className="bg-white rounded-xl shadow-sm p-6">
            <h2 className="text-lg font-semibold text-gray-800 flex items-center gap-2 mb-4">
              📁 My Portfolio
            </h2>
            <p className="text-sm text-gray-500 mb-4">
              View your completed tasks and showcase your achievements.
            </p>
            <Link
              to="/student/portfolio"
              className="inline-flex items-center gap-2 px-5 py-3 bg-green-600 text-white rounded-lg font-semibold hover:bg-green-700 transition w-full justify-center"
            >
              View Portfolio <FiArrowRight />
            </Link>
          </div>

          {/* Analytics Dashboard */}
          <div className="bg-white rounded-xl shadow-sm p-6">
            <h2 className="text-lg font-semibold text-gray-800 flex items-center gap-2 mb-4">
              <FiBarChart2 className="text-blue-600" />
              Analytics
            </h2>
            <p className="text-sm text-gray-500 mb-4">
              Track your progress and view detailed learning analytics.
            </p>
            <Link
              to="/student/analytics"
              className="inline-flex items-center gap-2 px-5 py-3 bg-blue-600 text-white rounded-lg font-semibold hover:bg-blue-700 transition w-full justify-center"
            >
              View Analytics <FiArrowRight />
            </Link>
          </div>

          {/* Recent Attempts */}
          {attempts.length > 0 && (
            <div className="bg-white rounded-xl shadow-sm p-6">
              <h3 className="text-sm font-semibold text-gray-800 mb-3">Recent Attempts</h3>
              <div className="space-y-3">
                {attempts.slice(0, 4).map((a) => (
                  <Link
                    key={a.id}
                    to={`/student/results/${a.id}`}
                    className="block p-3 rounded-lg bg-gray-50 hover:bg-primary-50 transition"
                  >
                    <div className="flex items-center justify-between">
                      <span className="text-sm font-medium text-gray-700 truncate">
                        {a.assessment_title}
                      </span>
                      <span className={`text-xs font-medium px-2 py-0.5 rounded-full ${levelColor(a.skill_level)}`}>
                        {a.percentage}%
                      </span>
                    </div>
                    <span className="text-xs text-gray-400">
                      {new Date(a.attempted_at).toLocaleDateString()}
                    </span>
                  </Link>
                ))}
              </div>
            </div>
          )}
        </div>
      </div>
    </DashboardLayout>
  );
}
