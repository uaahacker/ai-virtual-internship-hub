import { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import DashboardLayout from '../components/DashboardLayout';
import { assessmentService } from '../services/endpoints';
import { FiAward, FiTrendingUp, FiArrowLeft, FiCheckCircle, FiAlertCircle, FiBookOpen } from 'react-icons/fi';

export default function AssessmentResult() {
  const { attemptId } = useParams();
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    assessmentService.getAttempt(attemptId)
      .then((res) => setResult(res.data.data))
      .catch(() => {})
      .finally(() => setLoading(false));
  }, [attemptId]);

  if (loading) {
    return (
      <DashboardLayout>
        <div className="text-center py-16 text-gray-400">Loading results...</div>
      </DashboardLayout>
    );
  }

  if (!result) {
    return (
      <DashboardLayout>
        <div className="text-center py-16 text-gray-400">Result not found.</div>
      </DashboardLayout>
    );
  }

  const rec = result.recommendation || {};
  const level = result.skill_level;

  const levelConfig = {
    Advanced: {
      color: 'text-green-600',
      bg: 'bg-green-100',
      border: 'border-green-300',
      icon: FiCheckCircle,
      ringColor: 'ring-green-400',
      barColor: 'bg-green-500',
    },
    Intermediate: {
      color: 'text-yellow-600',
      bg: 'bg-yellow-100',
      border: 'border-yellow-300',
      icon: FiTrendingUp,
      ringColor: 'ring-yellow-400',
      barColor: 'bg-yellow-500',
    },
    Beginner: {
      color: 'text-red-500',
      bg: 'bg-red-100',
      border: 'border-red-300',
      icon: FiAlertCircle,
      ringColor: 'ring-red-400',
      barColor: 'bg-red-400',
    },
  };

  const cfg = levelConfig[level] || levelConfig.Beginner;
  const LevelIcon = cfg.icon;

  return (
    <DashboardLayout>
      <Link
        to="/student/assessments"
        className="inline-flex items-center gap-2 text-sm text-gray-500 hover:text-primary-600 mb-6"
      >
        <FiArrowLeft /> Back to Assessments
      </Link>

      {/* Score overview */}
      <div className="bg-white rounded-xl shadow-sm p-8 mb-6">
        <div className="flex flex-col md:flex-row items-center gap-8">
          {/* Score circle */}
          <div className="flex-shrink-0">
            <div className={`w-36 h-36 rounded-full border-8 ${cfg.border} flex flex-col items-center justify-center ring-4 ${cfg.ringColor} ring-offset-2`}>
              <span className={`text-3xl font-bold ${cfg.color}`}>{result.percentage}%</span>
              <span className="text-xs text-gray-500">{result.score}/{result.total_questions}</span>
            </div>
          </div>

          {/* Info */}
          <div className="flex-1 text-center md:text-left">
            <h1 className="text-2xl font-bold text-gray-900 mb-1">
              {result.assessment_title}
            </h1>
            <p className="text-gray-500 mb-4">{result.assessment_domain}</p>

            <div className="flex items-center gap-3 justify-center md:justify-start mb-3">
              <span className={`inline-flex items-center gap-1.5 px-3 py-1.5 rounded-full text-sm font-semibold ${cfg.bg} ${cfg.color}`}>
                <LevelIcon size={16} /> {level}
              </span>
              <span className={`inline-flex items-center gap-1.5 px-3 py-1.5 rounded-full text-sm font-medium ${cfg.bg} ${cfg.color}`}>
                Strength: {rec.strength || '—'}
              </span>
            </div>

            <p className="text-sm text-gray-600">{rec.message}</p>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Recommended Roles */}
        <div className="bg-white rounded-xl shadow-sm p-6">
          <h2 className="text-lg font-semibold text-gray-800 flex items-center gap-2 mb-4">
            <FiAward className="text-primary-600" /> Recommended Freelancing Roles
          </h2>
          {(rec.recommended_roles || []).length > 0 ? (
            <ul className="space-y-3">
              {rec.recommended_roles.map((role, idx) => (
                <li key={idx} className="flex items-center gap-3 p-3 bg-gray-50 rounded-lg">
                  <span className="w-8 h-8 bg-primary-100 text-primary-600 rounded-full flex items-center justify-center text-sm font-bold">
                    {idx + 1}
                  </span>
                  <span className="text-sm font-medium text-gray-700">{role}</span>
                </li>
              ))}
            </ul>
          ) : (
            <p className="text-gray-400 text-sm">No specific roles recommended.</p>
          )}
        </div>

        {/* Suggestions */}
        <div className="bg-white rounded-xl shadow-sm p-6">
          <h2 className="text-lg font-semibold text-gray-800 flex items-center gap-2 mb-4">
            <FiBookOpen className="text-primary-600" /> Suggestions & Next Steps
          </h2>
          {(rec.suggestions || []).length > 0 ? (
            <ul className="space-y-3">
              {rec.suggestions.map((s, idx) => (
                <li key={idx} className="flex items-start gap-3 text-sm text-gray-700">
                  <span className="mt-0.5 w-5 h-5 bg-primary-50 text-primary-600 rounded-full flex items-center justify-center text-xs flex-shrink-0">
                    {idx + 1}
                  </span>
                  {s}
                </li>
              ))}
            </ul>
          ) : (
            <p className="text-gray-400 text-sm">No additional suggestions.</p>
          )}
        </div>
      </div>

      {/* Actions */}
      <div className="mt-6 flex gap-4">
        <Link
          to="/student/assessments"
          className="px-5 py-2.5 bg-primary-600 text-white rounded-lg text-sm font-semibold hover:bg-primary-700 transition"
        >
          Take Another Assessment
        </Link>
        <Link
          to="/student/dashboard"
          className="px-5 py-2.5 border border-gray-300 text-gray-700 rounded-lg text-sm font-medium hover:bg-gray-50 transition"
        >
          Back to Dashboard
        </Link>
      </div>
    </DashboardLayout>
  );
}
