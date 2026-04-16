import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import DashboardLayout from '../components/DashboardLayout';
import StudentProfileCard from '../components/StudentProfileCard';
import { useAuth } from '../contexts/AuthContext';
import { assessmentService, profileService } from '../services/endpoints';
import { Card, CardHeader, CardBody, SectionCard, StatCard, Badge } from '../components/CardComponents';
import { ProgressIndicator, CircularProgress, EmptyState } from '../components/ProgressAndUtilityComponents';

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
  const avgScore = skills.length > 0 ? Math.round(skills.reduce((sum, s) => sum + s.percentage, 0) / skills.length) : 0;

  const getSkillStatus = (level) => {
    if (level === 'Advanced') return { status: 'success', icon: '✓' };
    if (level === 'Intermediate') return { status: 'warning', icon: '→' };
    return { status: 'error', icon: '!' };
  };

  const barColor = (pct) => {
    if (pct >= 80) return 'bg-green-500';
    if (pct >= 50) return 'bg-blue-500';
    return 'bg-yellow-500';
  };

  return (
    <DashboardLayout>
      {/* Welcome Section */}
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-slate-900">Welcome back, {user?.name}! 👋</h1>
        <p className="text-slate-600 mt-2">Track your progress and continue your learning journey</p>
      </div>

      {/* Quick Stats */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
        <StatCard label="Assessments Taken" value={attempts.length} icon="📋" />
        <StatCard label="Average Score" value={`${avgScore}%`} icon="⭐" />
        <StatCard label="Skills Mastered" value={skills.filter(s => s.skill_level === 'Advanced').length} icon="🎯" />
        <StatCard label="In Progress" value={skills.filter(s => s.skill_level === 'Intermediate').length} icon="🔄" />
      </div>

      {/* Profile Card */}
      {!loading && profile && (
        <div className="mb-8">
          <StudentProfileCard profile={profile} user={user} />
        </div>
      )}

      {/* Main Content Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-8">
        {/* Skill Overview - Left Section */}
        <div className="lg:col-span-2 space-y-6">
          {/* Skills Progress */}
          <SectionCard
            title="📊 Your Skills"
            subtitle={`${skills.length} domain(s) assessed`}
            action={
              <Link to="/student/assessments" className="text-blue-600 hover:text-blue-700 text-sm font-medium">
                Take More →
              </Link>
            }
          >
            {loading ? (
              <div className="space-y-3">
                {[...Array(3)].map((_, i) => (
                  <div key={i} className="h-8 bg-slate-100 rounded animate-pulse" />
                ))}
              </div>
            ) : skills.length === 0 ? (
              <EmptyState
                icon="📭"
                title="No assessments yet"
                description="Start by taking your first assessment to build your skill profile"
                action={
                  <Link
                    to="/student/assessments"
                    className="px-6 py-2 bg-blue-600 text-white rounded-lg font-medium hover:bg-blue-700 transition-colors"
                  >
                    Browse Assessments
                  </Link>
                }
              />
            ) : (
              <div className="space-y-4">
                {skills.map((s) => (
                  <div key={s.assessment_domain} className="p-4 bg-slate-50 rounded-lg hover:bg-slate-100 transition-colors">
                    <div className="flex items-start justify-between mb-2">
                      <div className="flex-1">
                        <h4 className="font-semibold text-slate-900">{s.assessment_domain}</h4>
                        <p className="text-xs text-slate-500">Last attempt: {new Date(s.attempted_at).toLocaleDateString()}</p>
                      </div>
                      <Badge
                        text={s.skill_level}
                        status={getSkillStatus(s.skill_level).status}
                        size="sm"
                      />
                    </div>
                    <ProgressIndicator
                      percentage={s.percentage}
                      label={`Performance: ${s.percentage}%`}
                      size="md"
                      showLabel={false}
                    />
                  </div>
                ))}
              </div>
            )}
          </SectionCard>

          {/* Recent Attempts */}
          {attempts.length > 0 && (
            <SectionCard
              title="📋 Recent Assessments"
              subtitle={`${attempts.length} total attempts`}
              action={
                <Link to="/assessments" className="text-blue-600 hover:text-blue-700 text-sm font-medium">
                  View All →
                </Link>
              }
            >
              <div className="divide-y divide-slate-200">
                {attempts.slice(0, 5).map((a) => (
                  <Link
                    key={a.id}
                    to={`/student/results/${a.id}`}
                    className="flex items-center justify-between py-3 px-2 hover:bg-slate-50 transition-colors rounded"
                  >
                    <div className="flex-1">
                      <h4 className="font-medium text-slate-900">{a.assessment_title}</h4>
                      <p className="text-xs text-slate-500">{a.assessment_domain}</p>
                    </div>
                    <div className="text-right">
                      <div className="font-semibold text-slate-900">{a.percentage}%</div>
                      <Badge text={a.skill_level} status={getSkillStatus(a.skill_level).status} size="sm" />
                    </div>
                  </Link>
                ))}
              </div>
            </SectionCard>
          )}
        </div>

        {/* Quick Access Cards - Right Section */}
        <div className="space-y-4">
          {/* Assessment CTA */}
          <Card className="bg-gradient-to-br from-blue-50 to-blue-100 border-blue-200">
            <CardBody className="text-center">
              <div className="text-4xl mb-3">📋</div>
              <h3 className="font-semibold text-slate-900 mb-2">Take Assessment</h3>
              <p className="text-sm text-slate-700 mb-4">
                Evaluate your skills and get personalized recommendations
              </p>
              <Link
                to="/student/assessments"
                className="block px-4 py-2 bg-blue-600 text-white rounded-lg font-medium hover:bg-blue-700 transition-colors text-center"
              >
                Browse →
              </Link>
            </CardBody>
          </Card>

          {/* Recommended Tasks CTA */}
          <Card className="bg-gradient-to-br from-green-50 to-green-100 border-green-200">
            <CardBody className="text-center">
              <div className="text-4xl mb-3">🎯</div>
              <h3 className="font-semibold text-slate-900 mb-2">Recommended Tasks</h3>
              <p className="text-sm text-slate-700 mb-4">
                Complete tailored tasks based on your skill level
              </p>
              <Link
                to="/student/tasks/recommended"
                className="block px-4 py-2 bg-green-600 text-white rounded-lg font-medium hover:bg-green-700 transition-colors text-center"
              >
                Explore →
              </Link>
            </CardBody>
          </Card>

          {/* Portfolio CTA */}
          <Card className="bg-gradient-to-br from-purple-50 to-purple-100 border-purple-200">
            <CardBody className="text-center">
              <div className="text-4xl mb-3">🎨</div>
              <h3 className="font-semibold text-slate-900 mb-2">My Portfolio</h3>
              <p className="text-sm text-slate-700 mb-4">
                Showcase your completed projects and achievements
              </p>
              <Link
                to="/student/portfolio"
                className="block px-4 py-2 bg-purple-600 text-white rounded-lg font-medium hover:bg-purple-700 transition-colors text-center"
              >
                View →
              </Link>
            </CardBody>
          </Card>

          {/* Analytics CTA */}
          <Card className="bg-gradient-to-br from-indigo-50 to-indigo-100 border-indigo-200">
            <CardBody className="text-center">
              <div className="text-4xl mb-3">📈</div>
              <h3 className="font-semibold text-slate-900 mb-2">View Analytics</h3>
              <p className="text-sm text-slate-700 mb-4">
                Track your progress and performance metrics
              </p>
              <Link
                to="/student/analytics"
                className="block px-4 py-2 bg-indigo-600 text-white rounded-lg font-medium hover:bg-indigo-700 transition-colors text-center"
              >
                View →
              </Link>
            </CardBody>
          </Card>
        </div>
      </div>
    </DashboardLayout>
  );
}
