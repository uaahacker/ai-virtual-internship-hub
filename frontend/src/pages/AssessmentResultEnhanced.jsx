import { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import DashboardLayout from '../components/DashboardLayout';
import { assessmentService } from '../services/endpoints';
import {
  FiAward,
  FiTrendingUp,
  FiArrowLeft,
  FiCheckCircle,
  FiAlertCircle,
  FiBookOpen,
  FiTarget,
  FiChevronDown,
  FiChevronUp,
} from 'react-icons/fi';

export default function AssessmentResultEnhanced() {
  const { attemptId } = useParams();
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(true);
  const [expandedSections, setExpandedSections] = useState({
    strengths: true,
    weaknesses: true,
    nextSteps: true,
    breakdown: false,
  });

  useEffect(() => {
    assessmentService.getAttempt(attemptId)
      .then((res) => setResult(res.data.data))
      .catch(() => {})
      .finally(() => setLoading(false));
  }, [attemptId]);

  const toggleSection = (section) => {
    setExpandedSections((prev) => ({
      ...prev,
      [section]: !prev[section],
    }));
  };

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
  const breakdown = result.detailed_breakdown || {};
  const strengths = result.strengths || [];
  const weaknesses = result.weaknesses || [];
  const nextSteps = result.next_steps || [];

  const levelConfig = {
    Advanced: {
      color: 'text-green-600',
      bg: 'bg-green-50',
      border: 'border-green-300',
      icon: FiCheckCircle,
      ringColor: 'ring-green-400',
      barColor: 'bg-green-500',
      badge: 'bg-green-100 text-green-700',
    },
    Intermediate: {
      color: 'text-yellow-600',
      bg: 'bg-yellow-50',
      border: 'border-yellow-300',
      icon: FiTrendingUp,
      ringColor: 'ring-yellow-400',
      barColor: 'bg-yellow-500',
      badge: 'bg-yellow-100 text-yellow-700',
    },
    Beginner: {
      color: 'text-orange-600',
      bg: 'bg-orange-50',
      border: 'border-orange-300',
      icon: FiAlertCircle,
      ringColor: 'ring-orange-400',
      barColor: 'bg-orange-500',
      badge: 'bg-orange-100 text-orange-700',
    },
  };

  const cfg = levelConfig[level] || levelConfig.Beginner;
  const LevelIcon = cfg.icon;

  const getQuestionNumber = (index) => index + 1;

  return (
    <DashboardLayout>
      <Link
        to="/student/assessments"
        className="inline-flex items-center gap-2 text-sm text-gray-600 hover:text-gray-900 mb-6 transition"
      >
        <FiArrowLeft size={16} /> Back to Assessments
      </Link>

      {/* Main Score Card */}
      <div className={`rounded-lg shadow-sm border ${cfg.border} p-8 mb-6`} style={{ backgroundColor: cfg.bg }}>
        <div className="flex flex-col md:flex-row items-start gap-8">
          {/* Score Circle */}
          <div className="flex-shrink-0">
            <div
              className={`w-40 h-40 rounded-full border-4 ${cfg.border} flex flex-col items-center justify-center ring-4 ${cfg.ringColor} ring-offset-2`}
            >
              <span className={`text-4xl font-bold ${cfg.color}`}>{Math.round(result.percentage)}%</span>
              <span className="text-sm text-gray-600 mt-1">
                {result.score}/{result.total_questions} correct
              </span>
            </div>
          </div>

          {/* Assessment Info */}
          <div className="flex-1">
            <h1 className="text-3xl font-bold text-gray-900 mb-2">
              {result.assessment_title}
            </h1>
            <p className="text-gray-600 mb-4">{result.assessment_domain}</p>

            {/* Level Badge */}
            <div className="flex items-center gap-3 flex-wrap mb-6">
              <span className={`inline-flex items-center gap-1.5 px-4 py-2 rounded-full font-semibold text-sm ${cfg.badge}`}>
                <LevelIcon size={18} /> {level} Level
              </span>
              <span className={`inline-flex items-center gap-1.5 px-4 py-2 rounded-full font-medium text-sm ${cfg.badge}`}>
                Strength: {rec.strength || '—'}
              </span>
            </div>

            {/* Main Message */}
            <div className="bg-white bg-opacity-50 rounded-lg p-4 border border-gray-200">
              <p className="text-gray-700 leading-relaxed">{rec.message}</p>
              {rec.reason && (
                <p className="text-gray-600 text-sm mt-3 italic">
                  <span className="font-semibold">Why this level:</span> {rec.reason}
                </p>
              )}
            </div>
          </div>
        </div>
      </div>

      {/* Two Column Layout for Details */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-6">
        {/* Strengths Section */}
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
          <button
            onClick={() => toggleSection('strengths')}
            className="w-full flex items-center justify-between mb-4 hover:text-gray-900 transition"
          >
            <h2 className="text-lg font-semibold text-gray-900 flex items-center gap-2">
              <FiCheckCircle className="text-green-600" size={20} /> Your Strengths
            </h2>
            {expandedSections.strengths ? (
              <FiChevronUp size={20} />
            ) : (
              <FiChevronDown size={20} />
            )}
          </button>

          {expandedSections.strengths && (
            <ul className="space-y-3">
              {strengths.length > 0 ? (
                strengths.map((s, idx) => (
                  <li
                    key={idx}
                    className="flex items-start gap-3 p-3 bg-green-50 rounded-lg border border-green-100"
                  >
                    <span className="mt-0.5 w-6 h-6 bg-green-500 text-white rounded-full flex items-center justify-center text-xs font-bold flex-shrink-0">
                      ✓
                    </span>
                    <span className="text-sm text-gray-700">{s}</span>
                  </li>
                ))
              ) : (
                <p className="text-gray-500 text-sm">Keep working to build stronger foundations.</p>
              )}
            </ul>
          )}
        </div>

        {/* Weaknesses Section */}
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
          <button
            onClick={() => toggleSection('weaknesses')}
            className="w-full flex items-center justify-between mb-4 hover:text-gray-900 transition"
          >
            <h2 className="text-lg font-semibold text-gray-900 flex items-center gap-2">
              <FiAlertCircle className="text-orange-600" size={20} /> Areas to Improve
            </h2>
            {expandedSections.weaknesses ? (
              <FiChevronUp size={20} />
            ) : (
              <FiChevronDown size={20} />
            )}
          </button>

          {expandedSections.weaknesses && (
            <ul className="space-y-3">
              {weaknesses.length > 0 ? (
                weaknesses.map((w, idx) => (
                  <li
                    key={idx}
                    className="flex items-start gap-3 p-3 bg-orange-50 rounded-lg border border-orange-100"
                  >
                    <span className="mt-0.5 w-6 h-6 bg-orange-500 text-white rounded-full flex items-center justify-center text-xs font-bold flex-shrink-0">
                      !
                    </span>
                    <span className="text-sm text-gray-700">{w}</span>
                  </li>
                ))
              ) : (
                <p className="text-gray-500 text-sm">Great job! No significant areas to improve.</p>
              )}
            </ul>
          )}
        </div>
      </div>

      {/* Next Steps & Recommended Roles */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-6">
        {/* Next Steps */}
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
          <button
            onClick={() => toggleSection('nextSteps')}
            className="w-full flex items-center justify-between mb-4 hover:text-gray-900 transition"
          >
            <h2 className="text-lg font-semibold text-gray-900 flex items-center gap-2">
              <FiTarget className="text-blue-600" size={20} /> Next Steps
            </h2>
            {expandedSections.nextSteps ? (
              <FiChevronUp size={20} />
            ) : (
              <FiChevronDown size={20} />
            )}
          </button>

          {expandedSections.nextSteps && (
            <ol className="space-y-3">
              {nextSteps.length > 0 ? (
                nextSteps.map((step, idx) => (
                  <li key={idx} className="flex items-start gap-3 text-sm text-gray-700">
                    <span className="mt-0.5 w-6 h-6 bg-blue-500 text-white rounded-full flex items-center justify-center text-xs font-bold flex-shrink-0">
                      {idx + 1}
                    </span>
                    <span>{step}</span>
                  </li>
                ))
              ) : (
                <p className="text-gray-500 text-sm">Continue with advanced projects and practice.</p>
              )}
            </ol>
          )}
        </div>

        {/* Recommended Roles */}
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
          <h2 className="text-lg font-semibold text-gray-900 flex items-center gap-2 mb-4">
            <FiAward className="text-purple-600" size={20} /> Recommended Roles
          </h2>
          <ul className="space-y-2">
            {(rec.recommended_roles || []).length > 0 ? (
              rec.recommended_roles.map((role, idx) => (
                <li
                  key={idx}
                  className="flex items-center gap-3 p-3 bg-purple-50 rounded-lg border border-purple-100"
                >
                  <span className="w-6 h-6 bg-purple-500 text-white rounded-full flex items-center justify-center text-xs font-bold">
                    {idx + 1}
                  </span>
                  <span className="text-sm font-medium text-gray-700">{role}</span>
                </li>
              ))
            ) : (
              <p className="text-gray-500 text-sm">Explore roles in {result.assessment_domain}.</p>
            )}
          </ul>
        </div>
      </div>

      {/* Question Breakdown - Collapsible */}
      <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
        <button
          onClick={() => toggleSection('breakdown')}
          className="w-full flex items-center justify-between mb-4 hover:text-gray-900 transition"
        >
          <h2 className="text-lg font-semibold text-gray-900 flex items-center gap-2">
            <FiBookOpen className="text-gray-600" size={20} /> Question-by-Question Breakdown
          </h2>
          {expandedSections.breakdown ? (
            <FiChevronUp size={20} />
          ) : (
            <FiChevronDown size={20} />
          )}
        </button>

        {expandedSections.breakdown && (
          <div className="space-y-4">
            {Object.entries(breakdown).map(([qId, details], idx) => {
              const isCorrect = details.is_correct;
              return (
                <div
                  key={qId}
                  className={`p-4 rounded-lg border ${
                    isCorrect
                      ? 'bg-green-50 border-green-200'
                      : 'bg-red-50 border-red-200'
                  }`}
                >
                  <div className="flex items-start gap-3 mb-2">
                    <span className="flex-shrink-0">
                      {isCorrect ? (
                        <FiCheckCircle className="text-green-600" size={20} />
                      ) : (
                        <FiAlertCircle className="text-red-600" size={20} />
                      )}
                    </span>
                    <div className="flex-1">
                      <p className="font-semibold text-gray-900">
                        Question {getQuestionNumber(idx)}
                      </p>
                      <p className="text-sm text-gray-700 mt-1">{details.text}</p>
                      <div className="mt-2 text-sm">
                        <p className="text-gray-600">
                          <span className="font-semibold">Your answer:</span> {details.submitted}
                        </p>
                        {!isCorrect && (
                          <p className="text-gray-600">
                            <span className="font-semibold">Correct answer:</span>{' '}
                            {details.correct_option}
                          </p>
                        )}
                      </div>
                    </div>
                  </div>
                </div>
              );
            })}
          </div>
        )}
      </div>

      {/* Action Buttons */}
      <div className="mt-8 flex flex-col sm:flex-row gap-3 justify-center">
        <Link
          to="/student/assessments"
          className="px-6 py-2 bg-gray-900 text-white rounded-lg hover:bg-gray-800 transition text-center font-medium"
        >
          Back to Assessments
        </Link>
        <button
          onClick={() => window.print()}
          className="px-6 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 transition font-medium"
        >
          Print Results
        </button>
      </div>
    </DashboardLayout>
  );
}
