import { Link, useNavigate, useLocation } from 'react-router-dom';
import { motion } from 'framer-motion';
import { useQuery, useQueryClient } from '@tanstack/react-query';
import { useAuth } from '../lib/auth';
import { Api } from '../lib/api';
import { LiveNotifications } from './Toast';
import logo from '../assets/smartq-logo.png';

const studentNav = [
  { to: '/services', label: 'Services', icon: '🎫' },
  { to: '/queue', label: 'My Queue', icon: '📊' },
  { to: '/notifications', label: 'Alerts', icon: '🔔' },
  { to: '/report', label: 'Report', icon: '🚩' },
];
const staffNav = [
  { to: '/staff', label: 'Dashboard', icon: '📊' },
  { to: '/staff/analytics', label: 'Analytics', icon: '📈' },
  { to: '/notifications', label: 'Alerts', icon: '🔔' },
  { to: '/report', label: 'Report', icon: '🚩' },
];

function isRouteActive(currentPath: string, target: string): boolean {
  // Exact match always wins
  if (currentPath === target) return true;
  // Dashboard ("/staff") must ONLY match exactly, otherwise /staff/analytics
  // and /staff/queue/3 would also light it up.
  if (target === '/staff') return false;
  // For everything else, prefix-match: /staff/queue/3 keeps "Analytics" off,
  // but /notifications/123 keeps "Alerts" on.
  return currentPath.startsWith(target + '/');
}

export default function AppShell({ children }: { children: React.ReactNode }) {
  const { me } = useAuth();
  const nav = useNavigate();
  const location = useLocation();
  const qc = useQueryClient();
  const isStaff = me?.is_staff_role;
  const navItems = isStaff ? staffNav : studentNav;
  const currentPath = location.pathname;

  const { data: poll } = useQuery({
    queryKey: ['notifPoll'],
    queryFn: Api.notificationsPoll,
    enabled: !!me,
    refetchInterval: 3000,
  });

  async function handleLogout() {
    qc.setQueryData(['me'], undefined);
    nav('/login', { replace: true });
    Api.logout().catch((err) => {
      console.warn('Server logout failed:', err);
    });
  }

  return (
    <div className="min-h-screen flex flex-col">
      <LiveNotifications />

      <header className="sticky top-0 z-40 bg-gradient-to-r from-ufh-deep via-ufh-blue to-ufh-dark border-b border-white/10">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 py-4 flex items-center justify-between gap-4">
          <Link to={isStaff ? '/staff' : '/services'} className="flex items-center gap-3 shrink-0">
            <img src={logo} alt="SmartQ" className="w-10 h-10 rounded-xl shadow-lg" />
            <div className="leading-none">
              <div className="text-white font-display font-bold text-lg">SmartQ</div>
              <div className="text-ufh-gold text-[10px] tracking-wide font-semibold uppercase">
                University of Fort Hare
              </div>
            </div>
          </Link>

          <nav className="hidden md:flex items-center gap-1">
            {navItems.map((n) => {
              const active = isRouteActive(currentPath, n.to);
              return (
                <Link
                  key={n.to}
                  to={n.to}
                  className={`px-4 py-2 rounded-xl text-sm font-medium transition-all ${
                    active
                      ? 'bg-white/15 text-white'
                      : 'text-white/70 hover:text-white hover:bg-white/5'
                  }`}
                >
                  <span className="mr-1.5">{n.icon}</span>
                  {n.label}
                </Link>
              );
            })}
          </nav>

          <div className="flex items-center gap-3">
            <Link
              to="/notifications"
              className="relative w-10 h-10 rounded-xl bg-white/10 grid place-items-center hover:bg-white/20 transition"
              aria-label="Notifications"
            >
              <span>🔔</span>
              {!!poll?.unread && (
                <span className="absolute -top-1 -right-1 min-w-[18px] h-[18px] rounded-full bg-ufh-gold text-ufh-dark text-[10px] font-bold grid place-items-center px-1 animate-pulse">
                  {poll.unread}
                </span>
              )}
            </Link>

            <div className="hidden sm:block text-white/90 text-sm">
              Hello, <span className="font-semibold">{me?.first_name || me?.username}</span>
            </div>

            <button
              onClick={handleLogout}
              className="rounded-xl border border-white/40 text-white px-4 py-2 text-sm font-semibold hover:bg-white hover:text-ufh-blue transition"
            >
              Logout
            </button>
          </div>
        </div>
      </header>

      <motion.main
        initial={{ opacity: 0, y: 8 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.25 }}
        className="flex-1 max-w-7xl w-full mx-auto px-4 sm:px-6 py-8"
      >
        {children}
      </motion.main>

      <nav className="md:hidden sticky bottom-0 z-40 bg-white/95 backdrop-blur-xl border-t border-black/5">
        <div className="grid grid-cols-4">
          {navItems.map((n) => {
            const active = isRouteActive(currentPath, n.to);
            return (
              <Link
                key={n.to}
                to={n.to}
                className={`flex flex-col items-center py-3 text-[11px] transition ${
                  active ? 'text-ufh-blue font-semibold' : 'text-gray-500'
                }`}
              >
                <span className="text-lg">{n.icon}</span>
                {n.label}
              </Link>
            );
          })}
        </div>
      </nav>

      <footer className="bg-ufh-deep text-white/75 text-xs py-5 text-center px-4">
        SmartQ · University of Fort Hare · Capstone 2026
      </footer>
    </div>
  );
}