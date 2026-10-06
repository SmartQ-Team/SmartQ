import { useEffect, useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { motion, AnimatePresence } from 'framer-motion';
import { Api, apiError } from '../lib/api';
import { useAuth } from '../lib/auth';
import logo from '../assets/smartq-logo.png';

const SLIDES = [
  {
    title: 'Better Queue. Study Smarter.',
    body: 'Join campus service queues from your phone and track your turn live.',
    icon: '🎓',
  },
  {
    title: 'Live Updates Every Second',
    body: 'Position, students ahead, and estimated waiting time — always current.',
    icon: '⚡',
  },
  {
    title: 'Built for UFH Departments',
    body: 'Finance · ICT Support · and more — all in one place.',
    icon: '🏛️',
  },
];

const SLIDE_INTERVAL_MS = 5000;

export default function LoginPage() {
  const { me, setMe } = useAuth();
  const nav = useNavigate();
  const [username, setU] = useState('');
  const [password, setP] = useState('');
  const [err, setErr] = useState('');
  const [busy, setBusy] = useState(false);
  const [slide, setSlide] = useState(0);

  // Auto-advance the hero carousel
  useEffect(() => {
    const id = setInterval(() => {
      setSlide((s) => (s + 1) % SLIDES.length);
    }, SLIDE_INTERVAL_MS);
    return () => clearInterval(id);
  }, []);

  // If already logged in, redirect immediately
  useEffect(() => {
    if (me) {
      nav(me.is_staff_role ? '/staff' : '/services', { replace: true });
    }
  }, [me, nav]);

  async function submit(e: React.FormEvent) {
    e.preventDefault();
    setErr('');
    setBusy(true);
    try {
      const user = await Api.login(username, password);
      setMe(user);
      nav(user.is_staff_role ? '/staff' : '/services', { replace: true });
    } catch (e) {
      setErr(apiError(e));
    } finally {
      setBusy(false);
    }
  }

  return (
    <div className="min-h-screen grid lg:grid-cols-2">
      {/* ---------- Left: hero panel with carousel ---------- */}
      <div className="relative bg-gradient-to-br from-ufh-deep via-ufh-blue to-ufh-dark text-white p-8 lg:p-14 flex flex-col justify-center overflow-hidden">
        <div className="absolute inset-0 opacity-10 bg-[radial-gradient(circle_at_30%_20%,white,transparent_40%)]" />

        <div className="relative max-w-md w-full">
          {/* Logo */}
          <img
            src={logo}
            alt="SmartQ"
            className="w-16 h-16 mb-10 rounded-2xl shadow-2xl"
          />

          {/* Carousel slides */}
          <div className="relative min-h-[220px]">
            <AnimatePresence mode="wait">
              <motion.div
                key={slide}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -20 }}
                transition={{ duration: 0.5, ease: 'easeOut' }}
                className="absolute inset-0"
              >
                <div className="text-4xl mb-4">{SLIDES[slide].icon}</div>
                <h1 className="font-display text-4xl lg:text-5xl font-bold leading-tight mb-4">
                  {SLIDES[slide].title}
                </h1>
                <p className="text-white/75 text-lg leading-relaxed">
                  {SLIDES[slide].body}
                </p>
              </motion.div>
            </AnimatePresence>
          </div>

          {/* Dots */}
          <div className="mt-10 flex gap-2">
            {SLIDES.map((_, i) => (
              <button
                key={i}
                onClick={() => setSlide(i)}
                className={`h-1.5 rounded-full transition-all duration-300 ${
                  i === slide ? 'w-10 bg-ufh-gold' : 'w-4 bg-white/30 hover:bg-white/50'
                }`}
                aria-label={`Show slide ${i + 1}`}
              />
            ))}
          </div>
        </div>
      </div>

      {/* ---------- Right: login form ---------- */}
      <div className="flex items-center justify-center p-8 bg-white">
        <form onSubmit={submit} className="w-full max-w-sm">
          <h2 className="font-display text-3xl font-bold text-ufh-blue mb-1">
            Sign in to SmartQ
          </h2>
          <p className="text-gray-500 mb-8">Welcome back.</p>

          {err && (
            <div className="mb-4 p-3 rounded-xl bg-red-50 border border-red-200 text-red-700 text-sm">
              {err}
            </div>
          )}

          <label className="block text-sm font-medium text-gray-700 mb-1">
            Username
          </label>
          <input
            value={username}
            onChange={(e) => setU(e.target.value)}
            className="w-full rounded-2xl border-2 border-gray-200 focus:border-ufh-blue outline-none px-4 py-3 mb-4 transition"
            autoFocus
            required
          />

          <label className="block text-sm font-medium text-gray-700 mb-1">
            Password
          </label>
          <input
            type="password"
            value={password}
            onChange={(e) => setP(e.target.value)}
            className="w-full rounded-2xl border-2 border-gray-200 focus:border-ufh-blue outline-none px-4 py-3 mb-6 transition"
            required
          />

          <button type="submit" disabled={busy} className="btn-gold w-full">
            {busy ? 'Signing in…' : 'Login'}
          </button>

          <p className="mt-6 text-center text-sm text-gray-500">
            New student?{' '}
            <Link to="/register" className="text-ufh-blue font-semibold hover:underline">
              Create an account
            </Link>
          </p>
        </form>
      </div>
    </div>
  );
}