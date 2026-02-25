import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import DashboardLayout from '../components/DashboardLayout';
import { assessmentService } from '../services/endpoints';
import { FiClock, FiHelpCircle, FiArrowRight } from 'react-icons/fi';

export default function AssessmentList() {
  const [assessments, setAssessments] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    assessmentService.list()
      .then((res) => setAssessments(res.data.data || []))
      .catch(() => {})
      .finally(() => setLoading(false));
  }, []);

  const domainColor = (domain) => {
    const colors = {
      'Programming': 'border-l-blue-500',
      'Content Writing': 'border-l-green-500',
      'Graphic Design': 'border-l-pink-500',
      'Freelancing': 'border-l-yellow-500',
      'E-Commerce': 'border-l-purple-500',
      'QuickBooks': 'border-l-orange-500',
      'AutoCAD': 'border-l-red-500',
      'Data Analytics': 'border-l-cyan-500',
      'Digital Marketing': 'border-l-indigo-500',
      'WordPress': 'border-l-teal-500',
    };
    return colors[domain] || 'border-l-gray-400';
  };

  return (
    <DashboardLayout>
      <div className="mb-8">
        <h1 className="text-2xl font-bold text-gray-900">Skill Assessments</h1>
        <p className="text-gray-500 mt-1">
          Choose a domain and test your skills. Get instant results and career recommendations.
        </p>
      </div>

      {loading ? (
        <div className="text-center py-16 text-gray-400">Loading assessments...</div>
      ) : assessments.length === 0 ? (
        <div className="text-center py-16 text-gray-400">
          <FiHelpCircle className="mx-auto mb-3" size={48} />
          <p>No assessments available yet. Please check back later.</p>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {assessments.map((a) => (
            <div
              key={a.id}
              className={`bg-white rounded-xl shadow-sm border-l-4 ${domainColor(a.domain)} hover:shadow-md transition`}
            >
              <div className="p-6">
                <span className="inline-block text-xs font-semibold text-primary-600 bg-primary-50 px-2 py-1 rounded mb-3">
                  {a.domain}
                </span>
                <h3 className="text-lg font-semibold text-gray-800 mb-2">{a.title}</h3>
                <p className="text-sm text-gray-500 mb-4 line-clamp-2">
                  {a.description || 'Test your knowledge in this domain.'}
                </p>
                <div className="flex items-center gap-4 text-xs text-gray-400 mb-5">
                  <span className="flex items-center gap-1">
                    <FiHelpCircle size={14} /> {a.question_count} questions
                  </span>
                  {a.time_limit && (
                    <span className="flex items-center gap-1">
                      <FiClock size={14} /> {a.time_limit} min
                    </span>
                  )}
                </div>
                <Link
                  to={`/student/assessments/${a.id}`}
                  className="inline-flex items-center gap-2 px-4 py-2 bg-primary-600 text-white rounded-lg text-sm font-medium hover:bg-primary-700 transition"
                >
                  Start Assessment <FiArrowRight />
                </Link>
              </div>
            </div>
          ))}
        </div>
      )}
    </DashboardLayout>
  );
}
