import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { Link } from 'react-router-dom';
import { motion, AnimatePresence } from 'framer-motion';
import { useEffect, useRef, useState } from 'react';
import { Api, apiError } from '../lib/api';
import { useToast } from '../components/Toast';

const statusTone: Record<string, string> = {
  WAITING: 'bg-blue-100 text-blue-700',
  CALLED: 'bg-ufh-gold text-ufh-dark',
  ARRIVED: 'bg-indigo-100 text-indigo-700',
  SERVING: 'bg-purple-100 text-purple-700',
  COMPLETED: 'bg-emerald-100 text-emerald-700',
  CANCELLED: 'bg-gray-200 text-gray-700',
  NO_SHOW: 'bg-red-100 text-red-700',
};

export default function MyQueuePage() {
  const qc = useQueryClient();
  const { push } = useToast();
  const { data } = useQuery({
    queryKey: ['myQueue'],
    queryFn: Api.myQueue,
    refetchInterval: 3000,
  });
  const entry = data?.entry;
  const lastStatus = useRef<string | null>(null);
  const [alerted, setAlerted] = useState(false);

  // Request browser notification permission once
  useEffect(() => {
    if ('Notification' in window && Notification.permission === 'default') {
      Notification.requestPermission();
    }
  }, []);

  // Chime + vibrate + browser notification on CALLED transition
  useEffect(() => {
    if (!entry) return;
    if (entry.status === 'CALLED' && lastStatus.current !== 'CALLED' && !alerted) {
      chime();
      if (navigator.vibrate) navigator.vibrate([300, 150, 300]);
      if ('Notification' in window && Notification.permission === 'granted') {
        new Notification('SmartQ: You are up next!', {
          body: 'Proceed to the service point now.',
        });
      }
      setAlerted(true);
    }
    lastStatus.current = entry.status;
  }, [entry, alerted]);

  const cancelMut = useMutation({
    mutationFn: (id: number) => Api.cancel(id),
    onSuccess: () => {
      push('Your queue entry was cancelled.', 'info');
      qc.invalidateQueries({ queryKey: ['myQueue'] });
      qc.invalidateQueries({ queryKey: ['services'] });
    },
    onError: (e) => push(apiError(e), 'error'),
  });

  const lateMut = useMutation({
    mutationFn: (id: number) => Api.markLate(id),
    onSuccess: () => {
      push('Staff informed that you are running late.', 'warning');
      qc.invalidateQueries({ queryKey: ['myQueue'] });
    },
    onError: (e) => push(apiError(e), 'error'),
  });

  if (!entry) {
    return (
      <div className="text-center py-24">
        <div className="text-6xl mb-4">🎫</div>
        <h2 className="font-display text-2xl font-bold text-ufh-blue mb-2">
          You're not in any queue
        </h2>
        <p className="text-gray-500 mb-6">Join a service to get started.</p>
        <Link to="/services" className="btn-gold">Browse Services</Link>
      </div>
    );
  }

  const isCalled = entry.status === 'CALLED';
  const isArrived = entry.status === 'ARRIVED' || entry.status === 'SERVING';
  const isEnded = !data?.active;

  return (
    <div className="max-w-2xl mx-auto">
      <AnimatePresence>
        {isCalled && (
          <motion.div
            initial={{ opacity: 0, y: -8 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0 }}
            className="mb-6 p-5 rounded-2xl bg-gradient-to-r from-ufh-gold/30 to-ufh-goldDark/30 border-2 border-ufh-gold text-center animate-flash"
          >
            <div className="font-display font-bold text-xl text-ufh-dark">
              📢 YOU ARE BEING CALLED NOW
            </div>
            <div className="text-sm text-ufh-dark/70 mt-1">
              Please proceed to {entry.department_name}.
            </div>
          </motion.div>
        )}
      </AnimatePresence>

      {isArrived && (
        <div className="mb-6 p-4 rounded-2xl bg-emerald-50 border border-emerald-200 text-emerald-800 text-center">
          ✅ You have arrived — please wait at the service point.
        </div>
      )}

      {isEnded && (
        <div className="mb-6 p-4 rounded-2xl bg-gray-100 border border-gray-200 text-gray-700 text-center">
          ✅ Your queue entry has ended. You may now join a new queue.
        </div>
      )}

      <motion.div
        initial={{ opacity: 0, scale: 0.97 }}
        animate={{ opacity: 1, scale: 1 }}
        className="card"
      >
        <div className="accent-bar" />
        <div className="p-8 text-center">
          <div className="text-sm text-gray-400 font-semibold uppercase tracking-widest">
            {entry.department_name} · {entry.service_name}
          </div>

          <div className="my-6 relative inline-block">
            {isCalled && (
              <>
                <span className="absolute inset-0 rounded-full border-4 border-ufh-gold animate-pulseRing" />
                <span className="absolute inset-0 rounded-full border-4 border-ufh-gold animate-pulseRing" style={{ animationDelay: '0.5s' }} />
              </>
            )}
            <div className="font-display font-bold text-6xl text-ufh-blue tracking-tight">
              {entry.queue_number}
            </div>
          </div>

          <div className="mt-3">
            <span className={`chip ${statusTone[entry.status] || 'bg-gray-100 text-gray-700'}`}>
              {entry.status_display}
            </span>
            {entry.running_late && (
              <span className="chip bg-amber-100 text-amber-700 ml-2">
                ⏰ Running late
              </span>
            )}
          </div>

          <div className="grid grid-cols-3 gap-4 py-6 mt-6 border-y border-gray-100">
            <Stat label="Now Serving" value={data?.currently_serving || '—'} />
            <Stat label="Students Ahead" value={data?.ahead ?? 0} />
            <Stat label="Est. Wait" value={`~${data?.estimate ?? 0} min`} />
          </div>

          <div className="mt-6 text-xs text-gray-400">Live updates every 3 seconds</div>

          <div className="mt-6 flex flex-col sm:flex-row gap-3 justify-center">
            <Link to="/services" className="btn-ghost">Back</Link>

            {entry.status === 'WAITING' && !entry.running_late && (
              <button
                onClick={() => lateMut.mutate(entry.id)}
                disabled={lateMut.isPending}
                className="rounded-2xl border-2 border-ufh-gold text-ufh-goldDark font-semibold px-5 py-3 hover:bg-ufh-gold hover:text-ufh-dark transition"
              >
                ⏰ I will run late
              </button>
            )}

            {(entry.status === 'WAITING' || entry.status === 'CALLED') && (
              <button
                onClick={() => {
                  if (confirm('Cancel your queue entry?')) cancelMut.mutate(entry.id);
                }}
                disabled={cancelMut.isPending}
                className="rounded-2xl bg-red-500 text-white font-semibold px-5 py-3 hover:bg-red-600 transition"
              >
                Cancel Queue
              </button>
            )}
          </div>
        </div>
      </motion.div>
    </div>
  );
}

function Stat({ label, value }: { label: string; value: any }) {
  return (
    <div>
      <div className="text-xs uppercase tracking-wider text-gray-400 font-semibold">{label}</div>
      <div className="mt-1 font-display font-bold text-2xl text-ufh-blue">{value}</div>
    </div>
  );
}

function chime() {
  try {
    const AC = (window as any).AudioContext || (window as any).webkitAudioContext;
    const ctx = new AC();
    const t = ctx.currentTime;
    [880, 1174.66, 1567.98].forEach((f, i) => {
      const o = ctx.createOscillator();
      const g = ctx.createGain();
      o.frequency.value = f;
      o.connect(g); g.connect(ctx.destination);
      const start = t + i * 0.45;
      g.gain.setValueAtTime(0.0001, start);
      g.gain.exponentialRampToValueAtTime(0.35, start + 0.02);
      g.gain.exponentialRampToValueAtTime(0.0001, start + 0.35);
      o.start(start); o.stop(start + 0.4);
    });
  } catch { /* audio blocked */ }
}