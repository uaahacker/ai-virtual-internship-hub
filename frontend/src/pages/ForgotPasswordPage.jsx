import { useState } from 'react';
import { Link } from 'react-router-dom';
import { FiMail, FiArrowLeft, FiCopy, FiCheck } from 'react-icons/fi';
import { toast } from 'react-toastify';
import { authService } from '../services/endpoints';

export default function ForgotPasswordPage() {
  const [email, setEmail] = useState('');
  const [loading, setLoading] = useState(false);
  const [submitted, setSubmitted] = useState(false);
  const [resetToken, setResetToken] = useState('');
  const [resetUrl, setResetUrl] = useState('');
  const [copied, setCopied] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    try {
      const res = await authService.forgotPassword(email);
      if (res.data.success) {
        setSubmitted(true);
        // Token returned in response (no SMTP configured)
        if (res.data.token) setResetToken(res.data.token);
        if (res.data.reset_url) setResetUrl(res.data.reset_url);
      }
    } catch (err) {
      toast.error(err.response?.data?.error?.message || 'Something went wrong. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const copyToken = () => {
    navigator.clipboard.writeText(resetToken).then(() => {
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    });
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-slate-50 to-blue-50 p-4">
      <div className="w-full max-w-md">
        {/* Card */}
        <div className="bg-white rounded-2xl shadow-xl p-8">
          {/* Back link */}
          <Link
            to="/login"
            className="inline-flex items-center gap-2 text-sm text-slate-500 hover:text-slate-700 mb-6 transition-colors"
          >
            <FiArrowLeft size={16} />
            Back to Login
          </Link>

          {!submitted ? (
            <>
              <div className="text-center mb-8">
                <div className="w-16 h-16 bg-blue-100 rounded-full flex items-center justify-center mx-auto mb-4">
                  <FiMail size={28} className="text-blue-600" />
                </div>
                <h1 className="text-2xl font-bold text-slate-900">Forgot Password?</h1>
                <p className="text-slate-500 mt-2 text-sm">
                  Enter your email address and we'll generate a password reset token for you.
                </p>
              </div>

              <form onSubmit={handleSubmit} className="space-y-5">
                <div>
                  <label className="block text-sm font-medium text-slate-700 mb-1">Email Address</label>
                  <div className="relative">
                    <FiMail className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" size={18} />
                    <input
                      type="email"
                      value={email}
                      onChange={(e) => setEmail(e.target.value)}
                      placeholder="your@email.com"
                      required
                      className="w-full pl-10 pr-4 py-3 border border-slate-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent outline-none transition text-sm"
                    />
                  </div>
                </div>

                <button
                  type="submit"
                  disabled={loading}
                  className="w-full py-3 bg-blue-600 text-white rounded-lg font-semibold hover:bg-blue-700 focus:ring-4 focus:ring-blue-300 transition disabled:opacity-50 text-sm"
                >
                  {loading ? 'Generating Token...' : 'Generate Reset Token'}
                </button>
              </form>

              <p className="text-center mt-6 text-sm text-slate-500">
                Remember your password?{' '}
                <Link to="/login" className="text-blue-600 font-semibold hover:underline">
                  Log in
                </Link>
              </p>
            </>
          ) : (
            <>
              <div className="text-center mb-6">
                <div className="w-16 h-16 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-4">
                  <FiCheck size={28} className="text-green-600" />
                </div>
                <h1 className="text-2xl font-bold text-slate-900">Token Generated</h1>
                <p className="text-slate-500 mt-2 text-sm">
                  Use the token below to reset your password. It expires in 24 hours.
                </p>
              </div>

              {resetToken && (
                <div className="bg-slate-50 border border-slate-200 rounded-xl p-4 mb-5">
                  <div className="flex items-center justify-between mb-2">
                    <span className="text-xs font-semibold text-slate-500 uppercase tracking-wide">Reset Token</span>
                    <button
                      onClick={copyToken}
                      className="flex items-center gap-1 text-xs text-blue-600 hover:text-blue-700 font-medium transition"
                    >
                      {copied ? <FiCheck size={13} /> : <FiCopy size={13} />}
                      {copied ? 'Copied!' : 'Copy'}
                    </button>
                  </div>
                  <p className="text-xs font-mono text-slate-700 break-all">{resetToken}</p>
                </div>
              )}

              <Link
                to={`/reset-password?token=${resetToken}`}
                className="block w-full py-3 bg-blue-600 text-white rounded-lg font-semibold hover:bg-blue-700 text-center transition text-sm"
              >
                Reset Password Now
              </Link>

              <button
                onClick={() => { setSubmitted(false); setEmail(''); setResetToken(''); }}
                className="w-full mt-3 py-2.5 text-slate-600 text-sm hover:text-slate-800 transition"
              >
                Use a different email
              </button>
            </>
          )}
        </div>
      </div>
    </div>
  );
}
