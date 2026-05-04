import { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import { toast } from 'react-toastify';
import { FiUser, FiMail, FiLock, FiArrowLeft, FiArrowRight } from 'react-icons/fi';

const ALL_DOMAINS = [
  'Graphic Design', 'Content Writing', 'Programming', 'Freelancing',
  'E-Commerce', 'QuickBooks', 'AutoCAD', 'Data Analytics',
  'Digital Marketing', 'WordPress',
];

export default function RegisterPage() {
  const [step, setStep] = useState(1); // 1 = basic info, 2 = domain selection
  const [form, setForm] = useState({
    name: '',
    email: '',
    password: '',
    password_confirm: '',
    role: 'Student',
  });
  const [selectedDomains, setSelectedDomains] = useState([]);
  const [loading, setLoading] = useState(false);
  const { register } = useAuth();
  const navigate = useNavigate();

  const handleChange = (e) => {
    setForm({ ...form, [e.target.name]: e.target.value });
  };

  const toggleDomain = (domain) => {
    setSelectedDomains(prev =>
      prev.includes(domain) ? prev.filter(d => d !== domain) : [...prev, domain]
    );
  };

  const handleNext = (e) => {
    e.preventDefault();
    if (form.password !== form.password_confirm) {
      toast.error('Passwords do not match.');
      return;
    }
    if (form.password.length < 8) {
      toast.error('Password must be at least 8 characters.');
      return;
    }
    setStep(2);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (selectedDomains.length === 0) {
      toast.error('Please select at least one domain.');
      return;
    }
    setLoading(true);
    try {
      const payload = {
        ...form,
        ...(form.role === 'Student'
          ? { preferred_domains: selectedDomains }
          : { expertise_domains: selectedDomains }),
      };
      const user = await register(payload);
      toast.success('Registration successful!');
      const dashPath = {
        Student: '/student/dashboard',
        Mentor: '/mentor/dashboard',
      };
      navigate(dashPath[user.role] || '/login');
    } catch (err) {
      const msg = err.response?.data?.error?.message || 'Registration failed. Please try again.';
      toast.error(msg);
      setStep(1);
    } finally {
      setLoading(false);
    }
  };

  const domainLabel = form.role === 'Student'
    ? 'Select your areas of interest'
    : 'Select your expertise domains';

  return (
    <div className="min-h-screen flex">
      {/* Left panel */}
      <div className="hidden lg:flex lg:w-1/2 bg-gradient-to-br from-primary-600 to-primary-800 items-center justify-center p-12">
        <div className="text-center text-white max-w-md">
          <div className="mx-auto mb-8 w-64 h-64 bg-white/10 rounded-2xl flex items-center justify-center">
            <svg className="w-40 h-40 text-white/80" viewBox="0 0 200 200" fill="none">
              <circle cx="70" cy="80" r="28" stroke="currentColor" strokeWidth="3" fill="currentColor" fillOpacity="0.1"/>
              <circle cx="130" cy="80" r="28" stroke="currentColor" strokeWidth="3" fill="currentColor" fillOpacity="0.1"/>
              <path d="M30 170c0-22 18-40 40-40s40 18 40 40" stroke="currentColor" strokeWidth="3" fill="currentColor" fillOpacity="0.1"/>
              <path d="M90 170c0-22 18-40 40-40s40 18 40 40" stroke="currentColor" strokeWidth="3" fill="currentColor" fillOpacity="0.1"/>
              <path d="M95 45l5-10 5 10" stroke="currentColor" strokeWidth="2"/>
              <circle cx="100" cy="30" r="5" stroke="currentColor" strokeWidth="2" fill="currentColor" fillOpacity="0.2"/>
            </svg>
          </div>
          <h2 className="text-3xl font-bold mb-4">Join the Hub</h2>
          <p className="text-white/80 text-lg">
            Create your account and start building skills for a successful freelancing career.
          </p>
          {/* Step indicator */}
          <div className="flex items-center justify-center gap-3 mt-8">
            <div className={`w-8 h-8 rounded-full flex items-center justify-center text-sm font-bold border-2 ${step === 1 ? 'bg-white text-primary-700 border-white' : 'bg-white/30 text-white border-white/50'}`}>1</div>
            <div className="w-8 h-0.5 bg-white/40" />
            <div className={`w-8 h-8 rounded-full flex items-center justify-center text-sm font-bold border-2 ${step === 2 ? 'bg-white text-primary-700 border-white' : 'bg-white/30 text-white border-white/50'}`}>2</div>
          </div>
          <p className="text-white/70 text-sm mt-2">{step === 1 ? 'Account Info' : 'Choose Domains'}</p>
        </div>
      </div>

      {/* Right panel */}
      <div className="flex-1 flex items-center justify-center p-8 bg-white overflow-y-auto">
        <div className="w-full max-w-md">

          {/* ── STEP 1: basic info ── */}
          {step === 1 && (
            <>
              <div className="text-center mb-8">
                <h1 className="text-3xl font-bold text-gray-900">Register</h1>
                <p className="text-gray-500 mt-2">Create your free account — Step 1 of 2</p>
              </div>

              <form onSubmit={handleNext} className="space-y-4">
                {/* Role */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">I am a</label>
                  <div className="flex gap-3">
                    {['Student', 'Mentor'].map((role) => (
                      <button
                        key={role}
                        type="button"
                        onClick={() => { setForm({ ...form, role }); setSelectedDomains([]); }}
                        className={`flex-1 py-3 rounded-lg border-2 font-semibold text-sm transition ${
                          form.role === role
                            ? 'border-primary-600 bg-primary-50 text-primary-700'
                            : 'border-gray-200 text-gray-500 hover:border-gray-300'
                        }`}
                      >
                        {role}
                      </button>
                    ))}
                  </div>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Full Name</label>
                  <div className="relative">
                    <FiUser className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400" size={18} />
                    <input type="text" name="name" value={form.name} onChange={handleChange} placeholder="Full Name" required className="w-full pl-10 pr-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent outline-none transition" />
                  </div>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Email Address</label>
                  <div className="relative">
                    <FiMail className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400" size={18} />
                    <input type="email" name="email" value={form.email} onChange={handleChange} placeholder="Email Address" required className="w-full pl-10 pr-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent outline-none transition" />
                  </div>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Password</label>
                  <div className="relative">
                    <FiLock className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400" size={18} />
                    <input type="password" name="password" value={form.password} onChange={handleChange} placeholder="Min 8 characters" required minLength={8} className="w-full pl-10 pr-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent outline-none transition" />
                  </div>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Confirm Password</label>
                  <div className="relative">
                    <FiLock className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400" size={18} />
                    <input type="password" name="password_confirm" value={form.password_confirm} onChange={handleChange} placeholder="Confirm Password" required minLength={8} className="w-full pl-10 pr-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent outline-none transition" />
                  </div>
                </div>

                <button type="submit" className="w-full py-3 bg-primary-600 text-white rounded-lg font-semibold hover:bg-primary-700 focus:ring-4 focus:ring-primary-300 transition flex items-center justify-center gap-2">
                  Next <FiArrowRight size={18} />
                </button>
              </form>

              <p className="text-center mt-6 text-gray-600">
                Already have an account?{' '}
                <Link to="/login" className="text-primary-600 font-semibold hover:underline">Login</Link>
              </p>
            </>
          )}

          {/* ── STEP 2: domain selection ── */}
          {step === 2 && (
            <>
              <div className="text-center mb-6">
                <h1 className="text-2xl font-bold text-gray-900">{domainLabel}</h1>
                <p className="text-gray-500 mt-1 text-sm">
                  {form.role === 'Student'
                    ? 'These help us match you with the right mentor and tasks.'
                    : 'These are the domains you will guide students in.'}
                </p>
                <p className="text-xs text-gray-400 mt-1">Select at least 1 (can change later in profile)</p>
              </div>

              <form onSubmit={handleSubmit} className="space-y-4">
                <div className="grid grid-cols-2 gap-2">
                  {ALL_DOMAINS.map((domain) => {
                    const active = selectedDomains.includes(domain);
                    return (
                      <button
                        key={domain}
                        type="button"
                        onClick={() => toggleDomain(domain)}
                        className={`px-3 py-3 rounded-lg border-2 text-sm font-medium text-left transition ${
                          active
                            ? 'border-primary-600 bg-primary-50 text-primary-700'
                            : 'border-gray-200 text-gray-600 hover:border-gray-300 hover:bg-gray-50'
                        }`}
                      >
                        {active && <span className="mr-1">✓</span>}{domain}
                      </button>
                    );
                  })}
                </div>

                {selectedDomains.length > 0 && (
                  <p className="text-xs text-primary-600 font-medium">
                    {selectedDomains.length} domain{selectedDomains.length > 1 ? 's' : ''} selected
                  </p>
                )}

                <div className="flex gap-3 pt-2">
                  <button
                    type="button"
                    onClick={() => setStep(1)}
                    className="flex-1 py-3 border-2 border-gray-300 text-gray-700 rounded-lg font-semibold hover:bg-gray-50 transition flex items-center justify-center gap-2"
                  >
                    <FiArrowLeft size={16} /> Back
                  </button>
                  <button
                    type="submit"
                    disabled={loading || selectedDomains.length === 0}
                    className="flex-1 py-3 bg-primary-600 text-white rounded-lg font-semibold hover:bg-primary-700 focus:ring-4 focus:ring-primary-300 transition disabled:opacity-50"
                  >
                    {loading ? 'Creating account...' : 'Register'}
                  </button>
                </div>
              </form>
            </>
          )}

        </div>
      </div>
    </div>
  );
}
