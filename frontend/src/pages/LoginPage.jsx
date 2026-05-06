import { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import { toast } from 'react-toastify';
import { FiMail, FiLock } from 'react-icons/fi';

export default function LoginPage() {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [loading, setLoading] = useState(false);
  const { login } = useAuth();
  const navigate = useNavigate();
  
  console.log('✅ LoginPage rendered');

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    try {
      const user = await login(email, password);
      toast.success('Login successful!');
      const dashPath = {
        Student: '/student/dashboard',
        Mentor: '/mentor/dashboard',
        Admin: '/admin/dashboard',
      };
      navigate(dashPath[user.role] || '/login');
    } catch (err) {
      const msg = err.response?.data?.error?.message || 'Login failed. Please try again.';
      toast.error(msg);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex">
      {/* Left side – illustration area */}
      <div className="hidden lg:flex lg:w-1/2 bg-gradient-to-br from-primary-600 to-primary-800 items-center justify-center p-12">
        <div className="text-center text-white max-w-md">
          {/* Placeholder illustration */}
          <div className="mx-auto mb-8 w-64 h-64 bg-white/10 rounded-2xl flex items-center justify-center">
            <svg className="w-40 h-40 text-white/80" viewBox="0 0 200 200" fill="none">
              <circle cx="100" cy="80" r="35" stroke="currentColor" strokeWidth="3" fill="currentColor" fillOpacity="0.1"/>
              <path d="M45 170c0-30 25-55 55-55s55 25 55 55" stroke="currentColor" strokeWidth="3" fill="currentColor" fillOpacity="0.1"/>
              <rect x="130" y="40" width="40" height="50" rx="5" stroke="currentColor" strokeWidth="2" fill="currentColor" fillOpacity="0.1"/>
              <line x1="138" y1="52" x2="162" y2="52" stroke="currentColor" strokeWidth="2"/>
              <line x1="138" y1="60" x2="158" y2="60" stroke="currentColor" strokeWidth="2"/>
              <line x1="138" y1="68" x2="162" y2="68" stroke="currentColor" strokeWidth="2"/>
              <line x1="138" y1="76" x2="155" y2="76" stroke="currentColor" strokeWidth="2"/>
            </svg>
          </div>
          <h2 className="text-3xl font-bold mb-4">AI-Supported Virtual Internship Hub</h2>
          <p className="text-white/80 text-lg">
            Build your freelancing career with AI-powered skill assessments,
            personalized recommendations, and guided internship tasks.
          </p>
        </div>
      </div>

      {/* Right side – login form */}
      <div className="flex-1 flex items-center justify-center p-8 bg-white">
        <div className="w-full max-w-md">
          {/* Mobile logo */}
          <div className="lg:hidden text-center mb-8">
            <div className="inline-flex items-center gap-3 mb-2">
              <div className="w-10 h-10 bg-primary-600 rounded-lg flex items-center justify-center">
                <span className="text-white font-bold text-sm">VIH</span>
              </div>
              <span className="font-bold text-lg text-gray-800">Virtual Internship Hub</span>
            </div>
          </div>

          <div className="text-center mb-8">
            <h1 className="text-3xl font-bold text-gray-900">Login</h1>
            <p className="text-gray-500 mt-2">Welcome back! Please enter your credentials.</p>
          </div>

          <form onSubmit={handleSubmit} className="space-y-5">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Email Address</label>
              <div className="relative">
                <FiMail className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400" size={18} />
                <input
                  type="email"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  placeholder="Email Address"
                  required
                  className="w-full pl-10 pr-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent outline-none transition"
                />
              </div>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Password</label>
              <div className="relative">
                <FiLock className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400" size={18} />
                <input
                  type="password"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  placeholder="Password"
                  required
                  className="w-full pl-10 pr-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent outline-none transition"
                />
              </div>
            </div>

            <div className="flex items-center justify-between text-sm">
              <label className="flex items-center gap-2">
                <input type="checkbox" className="rounded border-gray-300 text-primary-600 focus:ring-primary-500" />
                <span className="text-gray-600">Remember me</span>
              </label>
              <Link to="/forgot-password" className="text-primary-600 hover:underline">Forgot Password?</Link>
            </div>

            <button
              type="submit"
              disabled={loading}
              className="w-full py-3 bg-primary-600 text-white rounded-lg font-semibold hover:bg-primary-700 focus:ring-4 focus:ring-primary-300 transition disabled:opacity-50"
            >
              {loading ? 'Signing in...' : 'Login'}
            </button>
          </form>

          <p className="text-center mt-6 text-gray-600">
            Don't have an account?{' '}
            <Link to="/register" className="text-primary-600 font-semibold hover:underline">
              Register
            </Link>
          </p>
        </div>
      </div>
    </div>
  );
}
