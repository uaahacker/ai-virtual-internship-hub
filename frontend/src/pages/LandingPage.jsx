import React from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';

const LandingPage = () => {
  const navigate = useNavigate();
  const { user } = useAuth();

  // If user is logged in, show dashboard path
  React.useEffect(() => {
    if (user) {
      const dashboardPath = {
        Student: '/student/dashboard',
        Mentor: '/mentor/dashboard',
        Admin: '/admin/dashboard',
      };
      navigate(dashboardPath[user.role] || '/login');
    }
  }, [user, navigate]);

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-600 via-blue-500 to-blue-700">
      {/* Navigation */}
      <nav className="bg-white/10 backdrop-blur-md border-b border-white/20 sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <div className="flex items-center gap-2">
              <div className="w-8 h-8 bg-white rounded-lg flex items-center justify-center font-bold text-blue-600">
                📚
              </div>
              <span className="text-white font-bold text-xl">Virtual Internship Hub</span>
            </div>
            <div className="flex gap-4">
              <button
                onClick={() => navigate('/login')}
                className="px-6 py-2 text-white hover:bg-white/20 rounded-lg transition"
              >
                Login
              </button>
              <button
                onClick={() => navigate('/register')}
                className="px-6 py-2 bg-white text-blue-600 hover:bg-gray-100 rounded-lg transition font-semibold"
              >
                Sign Up
              </button>
            </div>
          </div>
        </div>
      </nav>

      {/* Hero Section */}
      <section className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-20">
        <div className="grid md:grid-cols-2 gap-12 items-center">
          {/* Left Content */}
          <div className="text-white">
            <h1 className="text-5xl md:text-6xl font-bold mb-6 leading-tight">
              Build Your Freelancing Career with AI-Powered Guidance
            </h1>
            <p className="text-xl text-blue-100 mb-8 leading-relaxed">
              Get personalized skill assessments, tailored recommendations, and guided internship tasks. 
              All powered by AI to accelerate your professional growth.
            </p>
            <div className="flex gap-4 flex-wrap">
              <button
                onClick={() => navigate('/register')}
                className="px-8 py-3 bg-white text-blue-600 hover:bg-gray-100 rounded-lg font-bold transition transform hover:scale-105"
              >
                Get Started Free
              </button>
              <button
                onClick={() => navigate('/login')}
                className="px-8 py-3 border-2 border-white text-white hover:bg-white/10 rounded-lg font-bold transition"
              >
                Sign In
              </button>
            </div>
          </div>

          {/* Right Visual */}
          <div className="relative">
            <div className="grid grid-cols-2 gap-4">
              <div className="bg-white/10 backdrop-blur-md border border-white/20 rounded-xl p-6 text-white hover:bg-white/20 transition">
                <div className="text-3xl mb-2">🎯</div>
                <h3 className="font-bold mb-2">Smart Assessments</h3>
                <p className="text-sm text-blue-100">AI-driven skill evaluation tests</p>
              </div>
              <div className="bg-white/10 backdrop-blur-md border border-white/20 rounded-xl p-6 text-white hover:bg-white/20 transition mt-6">
                <div className="text-3xl mb-2">💡</div>
                <h3 className="font-bold mb-2">AI Guidance</h3>
                <p className="text-sm text-blue-100">Personalized career recommendations</p>
              </div>
              <div className="bg-white/10 backdrop-blur-md border border-white/20 rounded-xl p-6 text-white hover:bg-white/20 transition">
                <div className="text-3xl mb-2">📋</div>
                <h3 className="font-bold mb-2">Real Tasks</h3>
                <p className="text-sm text-blue-100">Practical projects & assignments</p>
              </div>
              <div className="bg-white/10 backdrop-blur-md border border-white/20 rounded-xl p-6 text-white hover:bg-white/20 transition mt-6">
                <div className="text-3xl mb-2">🎓</div>
                <h3 className="font-bold mb-2">Mentorship</h3>
                <p className="text-sm text-blue-100">Expert mentor feedback & support</p>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section className="bg-white/10 backdrop-blur-md border-t border-b border-white/20 py-20">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <h2 className="text-4xl font-bold text-white text-center mb-16">Why Choose Virtual Internship Hub?</h2>
          
          <div className="grid md:grid-cols-3 gap-8">
            <div className="bg-white/5 rounded-xl p-8 border border-white/10 hover:border-white/30 transition">
              <div className="text-4xl mb-4">📊</div>
              <h3 className="text-xl font-bold text-white mb-3">Data-Driven Insights</h3>
              <p className="text-blue-100">
                Get detailed analytics on your progress, strengths, and areas for improvement with comprehensive dashboards.
              </p>
            </div>

            <div className="bg-white/5 rounded-xl p-8 border border-white/10 hover:border-white/30 transition">
              <div className="text-4xl mb-4">🚀</div>
              <h3 className="text-xl font-bold text-white mb-3">Career Acceleration</h3>
              <p className="text-blue-100">
                Fast-track your freelancing career with curated learning paths and hands-on projects tailored to your goals.
              </p>
            </div>

            <div className="bg-white/5 rounded-xl p-8 border border-white/10 hover:border-white/30 transition">
              <div className="text-4xl mb-4">🤝</div>
              <h3 className="text-xl font-bold text-white mb-3">Expert Support</h3>
              <p className="text-blue-100">
                Connect with experienced mentors who provide personalized feedback and guidance throughout your journey.
              </p>
            </div>

            <div className="bg-white/5 rounded-xl p-8 border border-white/10 hover:border-white/30 transition">
              <div className="text-4xl mb-4">🎨</div>
              <h3 className="text-xl font-bold text-white mb-3">Portfolio Building</h3>
              <p className="text-blue-100">
                Showcase your work with a professional portfolio that demonstrates your skills to potential clients.
              </p>
            </div>

            <div className="bg-white/5 rounded-xl p-8 border border-white/10 hover:border-white/30 transition">
              <div className="text-4xl mb-4">💬</div>
              <h3 className="text-xl font-bold text-white mb-3">AI Career Bot</h3>
              <p className="text-blue-100">
                Get instant answers to career questions and personalized guidance from our intelligent chatbot.
              </p>
            </div>

            <div className="bg-white/5 rounded-xl p-8 border border-white/10 hover:border-white/30 transition">
              <div className="text-4xl mb-4">✨</div>
              <h3 className="text-xl font-bold text-white mb-3">Continuous Learning</h3>
              <p className="text-blue-100">
                Access a constantly updated library of skills, resources, and best practices for freelance success.
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* How It Works */}
      <section className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-20">
        <h2 className="text-4xl font-bold text-white text-center mb-16">How It Works</h2>
        
        <div className="grid md:grid-cols-4 gap-8">
          <div className="text-center">
            <div className="w-16 h-16 bg-white/20 rounded-full flex items-center justify-center mx-auto mb-4 text-2xl">
              1️⃣
            </div>
            <h3 className="text-xl font-bold text-white mb-2">Sign Up</h3>
            <p className="text-blue-100">Create your account and choose your role (Student, Mentor, or Admin)</p>
          </div>

          <div className="text-center">
            <div className="w-16 h-16 bg-white/20 rounded-full flex items-center justify-center mx-auto mb-4 text-2xl">
              2️⃣
            </div>
            <h3 className="text-xl font-bold text-white mb-2">Take Assessment</h3>
            <p className="text-blue-100">Complete AI-powered skill assessments to identify your strengths</p>
          </div>

          <div className="text-center">
            <div className="w-16 h-16 bg-white/20 rounded-full flex items-center justify-center mx-auto mb-4 text-2xl">
              3️⃣
            </div>
            <h3 className="text-xl font-bold text-white mb-2">Get Recommendations</h3>
            <p className="text-blue-100">Receive personalized learning paths based on your goals</p>
          </div>

          <div className="text-center">
            <div className="w-16 h-16 bg-white/20 rounded-full flex items-center justify-center mx-auto mb-4 text-2xl">
              4️⃣
            </div>
            <h3 className="text-xl font-bold text-white mb-2">Build & Grow</h3>
            <p className="text-blue-100">Complete tasks, build portfolio, and advance your career</p>
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="bg-white/10 backdrop-blur-md border-t border-white/20 py-16">
        <div className="max-w-4xl mx-auto text-center px-4">
          <h2 className="text-4xl font-bold text-white mb-6">Ready to Launch Your Freelancing Career?</h2>
          <p className="text-xl text-blue-100 mb-8">
            Join hundreds of students already building their success with Virtual Internship Hub
          </p>
          <button
            onClick={() => navigate('/register')}
            className="px-10 py-4 bg-white text-blue-600 hover:bg-gray-100 rounded-lg font-bold text-lg transition transform hover:scale-105"
          >
            Get Started Now - It's Free!
          </button>
        </div>
      </section>

      {/* Footer */}
      <footer className="border-t border-white/20 py-8">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center">
            <div className="text-blue-100">
              <p>&copy; 2026 Virtual Internship Hub. All rights reserved.</p>
            </div>
            <div className="flex gap-6 text-blue-100">
              <a href="#" className="hover:text-white transition">About</a>
              <a href="#" className="hover:text-white transition">Contact</a>
              <a href="#" className="hover:text-white transition">Privacy</a>
            </div>
          </div>
        </div>
      </footer>
    </div>
  );
};

export default LandingPage;
