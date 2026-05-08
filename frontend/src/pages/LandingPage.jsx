import React, { useEffect, useRef, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';

/* ─── Animated counter hook ─────────────────────────────────── */
const useCounter = (target, duration = 2000, start = false) => {
  const [count, setCount] = useState(0);
  useEffect(() => {
    if (!start) return;
    let startTime = null;
    const step = (timestamp) => {
      if (!startTime) startTime = timestamp;
      const progress = Math.min((timestamp - startTime) / duration, 1);
      setCount(Math.floor(progress * target));
      if (progress < 1) requestAnimationFrame(step);
    };
    requestAnimationFrame(step);
  }, [target, duration, start]);
  return count;
};

/* ─── Intersection observer hook ────────────────────────────── */
const useInView = () => {
  const ref = useRef(null);
  const [inView, setInView] = useState(false);
  useEffect(() => {
    const obs = new IntersectionObserver(([e]) => { if (e.isIntersecting) setInView(true); }, { threshold: 0.2 });
    if (ref.current) obs.observe(ref.current);
    return () => obs.disconnect();
  }, []);
  return [ref, inView];
};

/* ─── Stats Counter Component ───────────────────────────────── */
const StatItem = ({ value, label, suffix = '+' }) => {
  const [ref, inView] = useInView();
  const count = useCounter(value, 1800, inView);
  return (
    <div ref={ref} className="text-center">
      <div className="text-4xl md:text-5xl font-black text-white mb-2">
        {count.toLocaleString()}{suffix}
      </div>
      <div className="text-blue-200 text-sm font-medium uppercase tracking-wider">{label}</div>
    </div>
  );
};

/* ─── Main Component ─────────────────────────────────────────── */
const LandingPage = () => {
  const navigate = useNavigate();
  const { user } = useAuth();
  const [scrollY, setScrollY] = useState(0);

  useEffect(() => {
    if (user) {
      const map = { Student: '/student/dashboard', Mentor: '/mentor/dashboard', Admin: '/admin/dashboard' };
      navigate(map[user.role] || '/login');
    }
  }, [user, navigate]);

  useEffect(() => {
    const onScroll = () => setScrollY(window.scrollY);
    window.addEventListener('scroll', onScroll, { passive: true });
    return () => window.removeEventListener('scroll', onScroll);
  }, []);

  const domains = [
    { icon: '🎨', name: 'Graphic Design', color: 'from-pink-500 to-rose-500' },
    { icon: '✍️', name: 'Content Writing', color: 'from-amber-500 to-orange-500' },
    { icon: '💻', name: 'Programming', color: 'from-cyan-500 to-blue-500' },
    { icon: '🌐', name: 'Freelancing', color: 'from-emerald-500 to-teal-500' },
    { icon: '🛒', name: 'E-Commerce', color: 'from-violet-500 to-purple-500' },
    { icon: '📊', name: 'QuickBooks', color: 'from-green-500 to-emerald-600' },
    { icon: '📐', name: 'AutoCAD', color: 'from-sky-500 to-indigo-500' },
    { icon: '📈', name: 'Data Analytics', color: 'from-blue-500 to-violet-500' },
    { icon: '📣', name: 'Digital Marketing', color: 'from-fuchsia-500 to-pink-500' },
    { icon: '🔧', name: 'WordPress', color: 'from-teal-500 to-cyan-500' },
  ];

  const features = [
    {
      icon: '🎯',
      title: 'AI-Powered Assessments',
      desc: 'Adaptive MCQ tests evaluate your real skill level across 10 professional domains with intelligent scoring.',
      glow: 'shadow-blue-500/30',
    },
    {
      icon: '🤖',
      title: 'Personal AI Career Bot',
      desc: 'Chat with an intelligent AI tutor that knows your strengths and delivers tailored career guidance 24/7.',
      glow: 'shadow-purple-500/30',
    },
    {
      icon: '📋',
      title: 'Real-World Tasks',
      desc: 'Industry-grade assignments reviewed by expert mentors. Build proof-of-skill with every submission.',
      glow: 'shadow-emerald-500/30',
    },
    {
      icon: '🧑‍🏫',
      title: 'Expert Mentor Network',
      desc: 'Get matched to a dedicated mentor who reviews your work, scores it, and provides written feedback.',
      glow: 'shadow-amber-500/30',
    },
    {
      icon: '📂',
      title: 'Professional Portfolio',
      desc: 'Auto-generated portfolio with PDF export, skill scores, and a timeline of every completed project.',
      glow: 'shadow-rose-500/30',
    },
    {
      icon: '📊',
      title: 'Smart Analytics',
      desc: 'Rich dashboards show domain progress, completion rates, and personalized improvement roadmaps.',
      glow: 'shadow-cyan-500/30',
    },
  ];

  const steps = [
    { n: '01', title: 'Create Your Account', desc: 'Sign up as a Student or Mentor in under 60 seconds using email or Google.', icon: '👤' },
    { n: '02', title: 'Take Domain Assessments', desc: 'Complete AI-evaluated MCQ tests to map your current skill level across 10 domains.', icon: '📝' },
    { n: '03', title: 'Get AI Recommendations', desc: 'Our system recommends the most relevant tasks and learning paths for your profile.', icon: '💡' },
    { n: '04', title: 'Build & Get Reviewed', desc: 'Complete real tasks, submit your work, and receive mentor scores + written feedback.', icon: '🏆' },
  ];

  return (
    <div className="min-h-screen bg-[#040d21] overflow-x-hidden">

      {/* ── Ambient background blobs ─────────────────────────── */}
      <div className="fixed inset-0 pointer-events-none z-0 overflow-hidden">
        <div className="absolute top-[-10%] left-[-5%] w-[600px] h-[600px] rounded-full bg-blue-700/20 blur-[120px]" />
        <div className="absolute top-[30%] right-[-10%] w-[500px] h-[500px] rounded-full bg-indigo-600/20 blur-[120px]" />
        <div className="absolute bottom-[10%] left-[20%] w-[400px] h-[400px] rounded-full bg-cyan-600/15 blur-[100px]" />
      </div>

      {/* ── NAV ──────────────────────────────────────────────── */}
      <nav
        className="sticky top-0 z-50 transition-all duration-300"
        style={{
          background: scrollY > 40 ? 'rgba(4,13,33,0.92)' : 'transparent',
          backdropFilter: scrollY > 40 ? 'blur(16px)' : 'none',
          borderBottom: scrollY > 40 ? '1px solid rgba(255,255,255,0.08)' : '1px solid transparent',
        }}
      >
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            {/* Logo */}
            <div className="flex items-center gap-3">
              <div className="relative w-9 h-9">
                <div className="absolute inset-0 bg-gradient-to-br from-blue-400 to-indigo-600 rounded-xl rotate-6 opacity-70" />
                <div className="relative w-9 h-9 bg-gradient-to-br from-blue-500 to-indigo-600 rounded-xl flex items-center justify-center text-lg font-black text-white shadow-lg shadow-blue-500/40">
                  V
                </div>
              </div>
              <span className="text-white font-bold text-lg tracking-tight">
                Virtual Internship <span className="text-blue-400">Hub</span>
              </span>
            </div>
            {/* Buttons */}
            <div className="flex gap-3">
              <button
                onClick={() => navigate('/login')}
                className="px-5 py-2 text-sm text-white/80 hover:text-white border border-white/10 hover:border-white/30 rounded-lg transition"
              >
                Sign In
              </button>
              <button
                onClick={() => navigate('/register')}
                className="px-5 py-2 text-sm bg-gradient-to-r from-blue-500 to-indigo-600 hover:from-blue-400 hover:to-indigo-500 text-white rounded-lg font-semibold transition shadow-lg shadow-blue-500/30"
              >
                Get Started
              </button>
            </div>
          </div>
        </div>
      </nav>

      {/* ── HERO ─────────────────────────────────────────────── */}
      <section className="relative z-10 max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 pt-24 pb-20">
        {/* VU Badge */}
        <div className="flex justify-center mb-8">
          <div className="inline-flex items-center gap-3 px-5 py-2.5 rounded-full bg-white/5 border border-white/10 backdrop-blur-sm">
            <img
              src="https://www.vu.edu.pk/Content/images/VUlogoNew.png"
              alt="Virtual University of Pakistan"
              className="h-8 w-auto object-contain"
              onError={(e) => { e.target.style.display = 'none'; }}
            />
            <span className="text-blue-200 text-sm font-medium">Virtual University of Pakistan — Final Year Project 2026</span>
          </div>
        </div>

        <div className="text-center mb-16">
          <h1 className="text-5xl md:text-7xl font-black text-white mb-6 leading-tight tracking-tight">
            Your AI-Powered Path to
            <br />
            <span className="bg-gradient-to-r from-blue-400 via-cyan-400 to-indigo-400 bg-clip-text text-transparent">
              Freelancing Success
            </span>
          </h1>
          <p className="text-lg md:text-xl text-blue-200/80 max-w-2xl mx-auto mb-10 leading-relaxed">
            The Virtual Internship Hub bridges the gap between university education and the freelancing economy.
            Get assessed, matched to real tasks, mentored, and portfolio-ready — all in one platform.
          </p>
          <div className="flex gap-4 justify-center flex-wrap">
            <button
              onClick={() => navigate('/register')}
              className="group px-8 py-4 bg-gradient-to-r from-blue-500 to-indigo-600 hover:from-blue-400 hover:to-indigo-500 text-white rounded-xl font-bold text-base transition shadow-2xl shadow-blue-500/40 hover:shadow-blue-500/60 hover:-translate-y-0.5 transform"
            >
              Start for Free
              <span className="ml-2 group-hover:translate-x-1 inline-block transition-transform">→</span>
            </button>
            <button
              onClick={() => navigate('/login')}
              className="px-8 py-4 border border-white/20 hover:border-white/40 text-white/80 hover:text-white rounded-xl font-bold text-base transition hover:-translate-y-0.5 transform"
            >
              Sign In
            </button>
          </div>
        </div>

        {/* 3D Floating Feature Cards */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 max-w-4xl mx-auto">
          {[
            { icon: '🎯', label: 'Smart Assessments', sub: '10 Domains' },
            { icon: '🤖', label: 'AI Career Bot', sub: '24/7 Guidance' },
            { icon: '🧑‍🏫', label: 'Mentor Reviews', sub: 'Expert Feedback' },
            { icon: '📂', label: 'PDF Portfolio', sub: 'Auto-Generated' },
          ].map((c, i) => (
            <div
              key={i}
              className="group relative bg-gradient-to-b from-white/10 to-white/5 border border-white/10 rounded-2xl p-5 text-center cursor-default hover:border-blue-400/40 transition-all duration-300 hover:-translate-y-2"
              style={{
                boxShadow: '0 8px 32px rgba(0,0,0,0.3)',
                transform: `perspective(800px) rotateX(${i % 2 === 0 ? '4' : '-4'}deg) rotateY(${i < 2 ? '4' : '-4'}deg)`,
                transition: 'transform 0.4s ease, box-shadow 0.4s ease, border-color 0.3s ease',
              }}
              onMouseEnter={(e) => {
                e.currentTarget.style.transform = 'perspective(800px) rotateX(0deg) rotateY(0deg) translateY(-8px)';
                e.currentTarget.style.boxShadow = '0 20px 60px rgba(59,130,246,0.25)';
              }}
              onMouseLeave={(e) => {
                e.currentTarget.style.transform = `perspective(800px) rotateX(${i % 2 === 0 ? '4' : '-4'}deg) rotateY(${i < 2 ? '4' : '-4'}deg)`;
                e.currentTarget.style.boxShadow = '0 8px 32px rgba(0,0,0,0.3)';
              }}
            >
              <div className="text-3xl mb-2">{c.icon}</div>
              <div className="text-white font-bold text-sm">{c.label}</div>
              <div className="text-blue-300/70 text-xs mt-1">{c.sub}</div>
            </div>
          ))}
        </div>
      </section>

      {/* ── STATS BAR ─────────────────────────────────────────── */}
      <section className="relative z-10 border-y border-white/8 py-14 bg-white/3 backdrop-blur-sm">
        <div className="max-w-5xl mx-auto px-4 grid grid-cols-2 md:grid-cols-4 gap-8">
          <StatItem value={10} label="Freelancing Domains" suffix="" />
          <StatItem value={500} label="Practice Tasks" />
          <StatItem value={200} label="MCQ Questions" />
          <StatItem value={3} label="User Roles Supported" suffix="" />
        </div>
      </section>

      {/* ── ABOUT SECTION ────────────────────────────────────── */}
      <section className="relative z-10 max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-24">
        <div className="grid md:grid-cols-2 gap-16 items-center">
          <div>
            <div className="inline-block px-4 py-1.5 rounded-full bg-blue-500/10 border border-blue-400/20 text-blue-300 text-xs font-semibold uppercase tracking-widest mb-6">
              About the Platform
            </div>
            <h2 className="text-4xl md:text-5xl font-black text-white mb-6 leading-tight">
              What is the Virtual<br />
              <span className="bg-gradient-to-r from-blue-400 to-cyan-400 bg-clip-text text-transparent">Internship Hub?</span>
            </h2>
            <p className="text-blue-200/70 text-base leading-relaxed mb-5">
              VIHub is an AI-driven internship and skill-development platform designed for university students
              aiming to enter the freelancing market. It combines intelligent assessments, real-world tasks,
              and expert mentorship into one seamless learning journey.
            </p>
            <p className="text-blue-200/70 text-base leading-relaxed mb-8">
              Students take domain-specific MCQ assessments, receive AI-generated task recommendations,
              submit work for mentor review, and build a scored portfolio — all tracked through rich analytics dashboards.
            </p>
            <div className="flex flex-wrap gap-3">
              {['AI-Powered', 'Mentor Evaluated', 'Portfolio Ready', 'Free to Use'].map(tag => (
                <span key={tag} className="px-4 py-1.5 rounded-full bg-white/5 border border-white/10 text-white/70 text-sm">
                  ✓ {tag}
                </span>
              ))}
            </div>
          </div>

          {/* Platform overview visual */}
          <div className="relative">
            <div className="grid grid-cols-2 gap-4">
              {[
                { title: 'Students', desc: 'Take assessments, complete tasks, get mentor feedback, build portfolios', icon: '👨‍🎓', border: 'border-blue-500/30' },
                { title: 'Mentors', desc: 'Create tasks with MCQs, review submissions, evaluate student portfolios', icon: '🧑‍🏫', border: 'border-indigo-500/30' },
                { title: 'Admins', desc: 'Manage users, oversee platform analytics, assign mentors to students', icon: '⚙️', border: 'border-cyan-500/30' },
                { title: 'AI System', desc: 'Powers recommendations, chatbot guidance, and domain scoring engine', icon: '🤖', border: 'border-purple-500/30' },
              ].map((r, i) => (
                <div
                  key={i}
                  className={`bg-white/5 border ${r.border} rounded-2xl p-5 hover:bg-white/8 transition-all duration-300 hover:-translate-y-1`}
                  style={{ boxShadow: '0 4px 20px rgba(0,0,0,0.2)' }}
                >
                  <div className="text-2xl mb-3">{r.icon}</div>
                  <div className="text-white font-bold text-sm mb-1">{r.title}</div>
                  <div className="text-blue-200/60 text-xs leading-relaxed">{r.desc}</div>
                </div>
              ))}
            </div>
          </div>
        </div>
      </section>

      {/* ── DOMAINS ──────────────────────────────────────────── */}
      <section className="relative z-10 py-20 border-t border-white/8">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-14">
            <div className="inline-block px-4 py-1.5 rounded-full bg-indigo-500/10 border border-indigo-400/20 text-indigo-300 text-xs font-semibold uppercase tracking-widest mb-4">
              10 Professional Domains
            </div>
            <h2 className="text-4xl md:text-5xl font-black text-white mb-4">
              What You Can Learn
            </h2>
            <p className="text-blue-200/60 max-w-xl mx-auto">
              Every domain includes AI assessments, real tasks, mentor reviews, and a scored portfolio entry.
            </p>
          </div>
          <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-5 gap-4">
            {domains.map((d, i) => (
              <div
                key={i}
                className="group relative rounded-2xl overflow-hidden cursor-default"
                style={{ boxShadow: '0 4px 24px rgba(0,0,0,0.25)' }}
              >
                <div className={`absolute inset-0 bg-gradient-to-br ${d.color} opacity-10 group-hover:opacity-20 transition-opacity duration-300`} />
                <div className={`relative border border-white/10 group-hover:border-white/20 rounded-2xl p-5 text-center transition-all duration-300 group-hover:-translate-y-1 bg-white/5`}>
                  <div className="text-3xl mb-3">{d.icon}</div>
                  <div className="text-white text-sm font-semibold leading-tight">{d.name}</div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* ── FEATURES ─────────────────────────────────────────── */}
      <section className="relative z-10 max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-24">
        <div className="text-center mb-16">
          <div className="inline-block px-4 py-1.5 rounded-full bg-cyan-500/10 border border-cyan-400/20 text-cyan-300 text-xs font-semibold uppercase tracking-widest mb-4">
            Platform Features
          </div>
          <h2 className="text-4xl md:text-5xl font-black text-white mb-4">
            Everything You Need to Succeed
          </h2>
        </div>
        <div className="grid md:grid-cols-3 gap-6">
          {features.map((f, i) => (
            <div
              key={i}
              className={`group relative bg-gradient-to-b from-white/8 to-white/3 border border-white/10 rounded-2xl p-7 hover:border-white/25 transition-all duration-400 hover:-translate-y-2 shadow-xl ${f.glow}`}
              style={{ boxShadow: '0 8px 32px rgba(0,0,0,0.3)' }}
              onMouseEnter={(e) => { e.currentTarget.style.boxShadow = `0 20px 60px rgba(59,130,246,0.2)`; }}
              onMouseLeave={(e) => { e.currentTarget.style.boxShadow = '0 8px 32px rgba(0,0,0,0.3)'; }}
            >
              <div className="text-4xl mb-5">{f.icon}</div>
              <h3 className="text-white font-bold text-lg mb-3">{f.title}</h3>
              <p className="text-blue-200/60 text-sm leading-relaxed">{f.desc}</p>
            </div>
          ))}
        </div>
      </section>

      {/* ── HOW IT WORKS ─────────────────────────────────────── */}
      <section className="relative z-10 border-t border-white/8 py-24 bg-white/2">
        <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-16">
            <div className="inline-block px-4 py-1.5 rounded-full bg-emerald-500/10 border border-emerald-400/20 text-emerald-300 text-xs font-semibold uppercase tracking-widest mb-4">
              Simple Process
            </div>
            <h2 className="text-4xl md:text-5xl font-black text-white">How It Works</h2>
          </div>
          <div className="grid md:grid-cols-4 gap-6">
            {steps.map((s, i) => (
              <div key={i} className="relative">
                {/* Connector line */}
                {i < steps.length - 1 && (
                  <div className="hidden md:block absolute top-10 left-[calc(50%+48px)] w-[calc(100%-40px)] h-px bg-gradient-to-r from-white/20 to-transparent" />
                )}
                <div
                  className="group bg-gradient-to-b from-white/8 to-white/3 border border-white/10 rounded-2xl p-6 text-center hover:border-blue-400/30 transition-all duration-300 hover:-translate-y-2"
                  style={{ boxShadow: '0 4px 24px rgba(0,0,0,0.25)' }}
                >
                  <div className="w-16 h-16 mx-auto mb-5 rounded-2xl bg-gradient-to-br from-blue-500/20 to-indigo-500/20 border border-blue-400/20 flex items-center justify-center text-2xl">
                    {s.icon}
                  </div>
                  <div className="text-blue-400/50 text-xs font-black mb-2 tracking-widest">STEP {s.n}</div>
                  <h3 className="text-white font-bold text-sm mb-3">{s.title}</h3>
                  <p className="text-blue-200/50 text-xs leading-relaxed">{s.desc}</p>
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* ── CTA ──────────────────────────────────────────────── */}
      <section className="relative z-10 max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-24 text-center">
        <div
          className="relative rounded-3xl overflow-hidden p-12 border border-white/10"
          style={{ background: 'linear-gradient(135deg, rgba(59,130,246,0.15), rgba(99,102,241,0.15))', boxShadow: '0 0 80px rgba(59,130,246,0.15)' }}
        >
          <div className="absolute inset-0 bg-gradient-to-br from-blue-500/5 to-indigo-600/5" />
          <div className="relative">
            <h2 className="text-4xl md:text-5xl font-black text-white mb-5">
              Ready to Start Your Journey?
            </h2>
            <p className="text-blue-200/70 text-lg mb-8 max-w-xl mx-auto">
              Join students already building skills, completing tasks, and creating portfolios on VIHub — completely free.
            </p>
            <button
              onClick={() => navigate('/register')}
              className="px-10 py-4 bg-gradient-to-r from-blue-500 to-indigo-600 hover:from-blue-400 hover:to-indigo-500 text-white rounded-xl font-bold text-base transition shadow-2xl shadow-blue-500/40 hover:shadow-blue-500/60 hover:-translate-y-0.5 transform"
            >
              Create Free Account →
            </button>
          </div>
        </div>
      </section>

      {/* ── FOOTER ───────────────────────────────────────────── */}
      <footer className="relative z-10 border-t border-white/10 pt-14 pb-10">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          {/* Top row */}
          <div className="grid md:grid-cols-3 gap-10 mb-12">
            {/* Brand */}
            <div>
              <div className="flex items-center gap-2 mb-4">
                <div className="w-8 h-8 bg-gradient-to-br from-blue-500 to-indigo-600 rounded-lg flex items-center justify-center text-white font-black text-sm">V</div>
                <span className="text-white font-bold">Virtual Internship Hub</span>
              </div>
              <p className="text-blue-200/50 text-sm leading-relaxed">
                An AI-powered platform connecting students to freelancing success through assessments,
                tasks, mentorship, and portfolios.
              </p>
            </div>

            {/* Platform links */}
            <div>
              <div className="text-white/60 text-xs font-semibold uppercase tracking-widest mb-4">Platform</div>
              <ul className="space-y-2">
                {['Sign Up', 'Sign In', '10 Domains', 'AI Career Bot', 'Mentor Network'].map(l => (
                  <li key={l}>
                    <button
                      onClick={() => navigate(l === 'Sign Up' ? '/register' : l === 'Sign In' ? '/login' : '/')}
                      className="text-blue-200/50 hover:text-white text-sm transition"
                    >
                      {l}
                    </button>
                  </li>
                ))}
              </ul>
            </div>

            {/* VU Logo + Institution */}
            <div>
              <div className="text-white/60 text-xs font-semibold uppercase tracking-widest mb-4">Developed Under</div>
              <div className="flex items-center gap-4 mb-5">
                <img
                  src="https://www.vu.edu.pk/Content/images/VUlogoNew.png"
                  alt="Virtual University of Pakistan"
                  className="h-14 w-auto object-contain opacity-90"
                  onError={(e) => { e.target.replaceWith(Object.assign(document.createElement('div'), { className: 'w-14 h-14 rounded-xl bg-blue-800/60 flex items-center justify-center text-white text-xs font-bold text-center', textContent: 'VU' })); }}
                />
                <div>
                  <div className="text-white font-semibold text-sm">Virtual University</div>
                  <div className="text-blue-200/50 text-xs">of Pakistan</div>
                </div>
              </div>
              <div className="text-blue-200/40 text-xs leading-relaxed">
                Final Year Project — Computer Science<br />
                Batch 2021–2025
              </div>
            </div>
          </div>

          {/* Divider */}
          <div className="border-t border-white/8 pt-8">
            <div className="flex flex-col md:flex-row justify-between items-center gap-6">
              {/* Copyright */}
              <p className="text-blue-200/40 text-sm">
                &copy; 2026 Virtual Internship Hub · All rights reserved
              </p>

              {/* Developer Credits */}
              <div className="flex items-center gap-3 px-6 py-3 rounded-2xl bg-white/5 border border-white/10">
                <div className="flex -space-x-2">
                  <div className="w-8 h-8 rounded-full bg-gradient-to-br from-blue-400 to-blue-600 border-2 border-[#040d21] flex items-center justify-center text-white text-xs font-bold">U</div>
                  <div className="w-8 h-8 rounded-full bg-gradient-to-br from-indigo-400 to-indigo-600 border-2 border-[#040d21] flex items-center justify-center text-white text-xs font-bold">S</div>
                </div>
                <div>
                  <div className="text-white/50 text-xs uppercase tracking-widest mb-0.5">Developed by</div>
                  <div className="text-white text-sm font-semibold">Ubaid Ullah & Syed Aitzaz Ali Shah</div>
                  
                </div>
                <div className="ml-2 text-blue-400 text-lg">⚡</div>
              </div>
            </div>
          </div>
        </div>
      </footer>
    </div>
  );
};

export default LandingPage;
