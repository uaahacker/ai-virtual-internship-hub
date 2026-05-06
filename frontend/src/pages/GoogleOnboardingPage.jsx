import { useState } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import { toast } from 'react-toastify';

const ALL_DOMAINS = [
  'Graphic Design', 'Content Writing', 'Programming', 'Freelancing',
  'E-Commerce', 'QuickBooks', 'AutoCAD', 'Data Analytics',
  'Digital Marketing', 'WordPress',
];

export default function GoogleOnboardingPage() {
  const { state } = useLocation();
  const navigate = useNavigate();
  const { googleLogin } = useAuth();

  const [step, setStep] = useState(1); // 1 = role, 2 = domains
  const [role, setRole] = useState('Student');
  const [selectedDomains, setSelectedDomains] = useState([]);
  const [loading, setLoading] = useState(false);

  // Guard: redirect if arrived without Google state
  if (!state?.idToken) {
    navigate('/login');
    return null;
  }

  const { idToken, googleEmail, googleName } = state;

  const toggleDomain = (d) =>
    setSelectedDomains((prev) => (prev.includes(d) ? prev.filter((x) => x !== d) : [...prev, d]));

  const handleFinish = async () => {
    if (selectedDomains.length === 0) {
      toast.error('Please select at least one domain.');
      return;
    }
    setLoading(true);
    try {
      // Complete Google sign-in with chosen role
      const user = await googleLogin(idToken, role);

      // Now update profile with selected domains
      const { profileService } = await import('../services/endpoints');
      const domainField = role === 'Student' ? 'preferred_domains' : 'expertise_domains';
      try {
        if (role === 'Student') {
          await profileService.updateStudentProfile({ [domainField]: selectedDomains });
        } else {
          await profileService.updateMentorProfile({ [domainField]: selectedDomains });
        }
      } catch {
        // Domain update failing shouldn't block login
      }

      toast.success(`Welcome to VIHub, ${user.name}!`);
      navigate(role === 'Student' ? '/student/dashboard' : '/mentor/dashboard');
    } catch (err) {
      const msg = err.response?.data?.error?.message || 'Failed to complete registration.';
      toast.error(msg);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-primary-50 to-blue-50 flex items-center justify-center p-4">
      <div className="w-full max-w-md bg-white rounded-2xl shadow-xl overflow-hidden">
        {/* Header */}
        <div className="bg-gradient-to-r from-primary-600 to-primary-700 px-8 py-6 text-white">
          <div className="flex items-center gap-3 mb-1">
            <div className="w-10 h-10 bg-white/20 rounded-full flex items-center justify-center text-lg font-bold">
              {googleName?.charAt(0)?.toUpperCase()}
            </div>
            <div>
              <p className="font-semibold text-lg leading-tight">{googleName}</p>
              <p className="text-white/70 text-xs">{googleEmail}</p>
            </div>
          </div>
          <p className="text-white/80 text-sm mt-3">
            Almost done! Just a couple of things to set up your account.
          </p>
          {/* Step indicator */}
          <div className="flex items-center gap-2 mt-4">
            <div className={`w-6 h-6 rounded-full flex items-center justify-center text-xs font-bold border-2 ${step >= 1 ? 'bg-white text-primary-700 border-white' : 'bg-white/30 border-white/50'}`}>1</div>
            <div className="flex-1 h-0.5 bg-white/30" />
            <div className={`w-6 h-6 rounded-full flex items-center justify-center text-xs font-bold border-2 ${step >= 2 ? 'bg-white text-primary-700 border-white' : 'bg-white/30 border-white/50'}`}>2</div>
          </div>
        </div>

        <div className="px-8 py-6">
          {/* ── Step 1: Role selection ── */}
          {step === 1 && (
            <>
              <h2 className="text-xl font-bold text-gray-900 mb-1">I am joining as a…</h2>
              <p className="text-sm text-gray-500 mb-6">Choose your role on the platform.</p>

              <div className="space-y-3 mb-8">
                {[
                  { value: 'Student', emoji: '🎓', desc: 'Learn skills, complete tasks, build your portfolio.' },
                  { value: 'Mentor', emoji: '👨‍🏫', desc: 'Guide students, assign tasks, review their work.' },
                ].map(({ value, emoji, desc }) => (
                  <button
                    key={value}
                    type="button"
                    onClick={() => setRole(value)}
                    className={`w-full text-left p-4 rounded-xl border-2 transition ${
                      role === value
                        ? 'border-primary-600 bg-primary-50'
                        : 'border-gray-200 hover:border-gray-300'
                    }`}
                  >
                    <div className="flex items-center gap-3">
                      <span className="text-2xl">{emoji}</span>
                      <div>
                        <p className={`font-semibold ${role === value ? 'text-primary-700' : 'text-gray-800'}`}>{value}</p>
                        <p className="text-xs text-gray-500">{desc}</p>
                      </div>
                      {role === value && <span className="ml-auto text-primary-600 text-lg">✓</span>}
                    </div>
                  </button>
                ))}
              </div>

              <button
                onClick={() => setStep(2)}
                className="w-full py-3 bg-primary-600 text-white rounded-xl font-semibold hover:bg-primary-700 transition"
              >
                Continue →
              </button>
            </>
          )}

          {/* ── Step 2: Domain selection ── */}
          {step === 2 && (
            <>
              <h2 className="text-xl font-bold text-gray-900 mb-1">
                {role === 'Student' ? 'Areas of interest' : 'Your expertise'}
              </h2>
              <p className="text-sm text-gray-500 mb-4">
                {role === 'Student'
                  ? 'Helps us recommend the right tasks and mentor for you.'
                  : 'Domains you will guide students in.'}
              </p>

              <div className="grid grid-cols-2 gap-2 mb-2">
                {ALL_DOMAINS.map((d) => {
                  const active = selectedDomains.includes(d);
                  return (
                    <button
                      key={d}
                      type="button"
                      onClick={() => toggleDomain(d)}
                      className={`px-3 py-3 rounded-lg border-2 text-sm font-medium text-left transition ${
                        active
                          ? 'border-primary-600 bg-primary-50 text-primary-700'
                          : 'border-gray-200 text-gray-600 hover:border-gray-300'
                      }`}
                    >
                      {active && <span className="mr-1">✓</span>}{d}
                    </button>
                  );
                })}
              </div>

              {selectedDomains.length > 0 && (
                <p className="text-xs text-primary-600 font-medium mb-4">
                  {selectedDomains.length} domain{selectedDomains.length > 1 ? 's' : ''} selected
                </p>
              )}

              <div className="flex gap-3 mt-4">
                <button
                  type="button"
                  onClick={() => setStep(1)}
                  className="flex-1 py-3 border-2 border-gray-300 text-gray-700 rounded-xl font-semibold hover:bg-gray-50 transition"
                >
                  ← Back
                </button>
                <button
                  onClick={handleFinish}
                  disabled={loading || selectedDomains.length === 0}
                  className="flex-1 py-3 bg-primary-600 text-white rounded-xl font-semibold hover:bg-primary-700 transition disabled:opacity-50"
                >
                  {loading ? 'Setting up…' : 'Finish →'}
                </button>
              </div>
            </>
          )}
        </div>
      </div>
    </div>
  );
}
