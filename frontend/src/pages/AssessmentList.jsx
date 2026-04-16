import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import DashboardLayout from '../components/DashboardLayout';
import { assessmentService } from '../services/endpoints';
import { Card, CardBody, SectionCard, Badge } from '../components/CardComponents';
import { EmptyState } from '../components/ProgressAndUtilityComponents';

export default function AssessmentList() {
  const [assessments, setAssessments] = useState([]);
  const [loading, setLoading] = useState(true);
  const [selectedDomain, setSelectedDomain] = useState(null);

  useEffect(() => {
    assessmentService.list()
      .then((res) => setAssessments(res.data.data || []))
      .catch(() => {})
      .finally(() => setLoading(false));
  }, []);

  // Get unique domains
  const domains = [...new Set(assessments.map(a => a.domain))];
  const filteredAssessments = selectedDomain
    ? assessments.filter(a => a.domain === selectedDomain)
    : assessments;

  const domainEmojis = {
    'Programming': '💻',
    'Content Writing': '✍️',
    'Graphic Design': '🎨',
    'Freelancing': '💼',
    'E-Commerce': '🛍️',
    'QuickBooks': '📊',
    'AutoCAD': '📐',
    'Data Analytics': '📈',
    'Digital Marketing': '📱',
    'WordPress': '🌐',
  };

  return (
    <DashboardLayout>
      {/* Header */}
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-slate-900">📋 Skill Assessments</h1>
        <p className="text-slate-600 mt-2">
          Test your knowledge across multiple domains and get personalized recommendations
        </p>
      </div>

      {/* Domain Filter */}
      {domains.length > 0 && (
        <div className="mb-8 flex flex-wrap gap-2">
          <button
            onClick={() => setSelectedDomain(null)}
            className={`px-4 py-2 rounded-lg font-medium transition-colors ${
              selectedDomain === null
                ? 'bg-blue-600 text-white'
                : 'bg-slate-200 text-slate-700 hover:bg-slate-300'
            }`}
          >
            All ({assessments.length})
          </button>
          {domains.map(domain => (
            <button
              key={domain}
              onClick={() => setSelectedDomain(domain)}
              className={`px-4 py-2 rounded-lg font-medium transition-colors ${
                selectedDomain === domain
                  ? 'bg-blue-600 text-white'
                  : 'bg-slate-200 text-slate-700 hover:bg-slate-300'
              }`}
            >
              {domainEmojis[domain] || '📌'} {domain} ({assessments.filter(a => a.domain === domain).length})
            </button>
          ))}
        </div>
      )}

      {/* Assessment Grid */}
      {loading ? (
        <div className="flex justify-center items-center py-16">
          <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-blue-500" />
        </div>
      ) : filteredAssessments.length === 0 ? (
        <EmptyState
          icon="🔍"
          title="No assessments found"
          description={selectedDomain ? `No assessments available for ${selectedDomain}` : 'Check back soon for new assessments'}
        />
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {filteredAssessments.map((a) => (
            <Card key={a.id} hover className="group">
              <CardBody className="p-6">
                {/* Domain Badge */}
                <div className="flex items-center justify-between mb-3">
                  <Badge text={a.domain} status="info" size="sm" />
                  <span className="text-2xl">{domainEmojis[a.domain] || '📌'}</span>
                </div>

                {/* Title */}
                <h3 className="text-lg font-semibold text-slate-900 mb-2 group-hover:text-blue-600 transition-colors">
                  {a.title}
                </h3>

                {/* Description */}
                <p className="text-sm text-slate-600 mb-4 line-clamp-2">
                  {a.description || 'Test your knowledge in this domain and get instant results.'}
                </p>

                {/* Meta Information */}
                <div className="flex items-center gap-4 text-xs text-slate-500 mb-4 pb-4 border-b border-slate-200">
                  <span className="flex items-center gap-1">
                    <span>❓</span> {a.question_count} questions
                  </span>
                  {a.time_limit && (
                    <span className="flex items-center gap-1">
                      <span>⏱️</span> {a.time_limit} min
                    </span>
                  )}
                </div>

                {/* CTA */}
                <Link
                  to={`/student/assessments/${a.id}`}
                  className="block w-full text-center px-4 py-2 bg-blue-600 text-white rounded-lg font-medium hover:bg-blue-700 transition-colors"
                >
                  Start Assessment →
                </Link>
              </CardBody>
            </Card>
          ))}
        </div>
      )}
    </DashboardLayout>
  );
}
