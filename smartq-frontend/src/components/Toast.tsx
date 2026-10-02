import { createContext, useContext, useState, useCallback, useEffect, useRef } from 'react';
import { AnimatePresence, motion } from 'framer-motion';
import { useQuery } from '@tanstack/react-query';
import { Api } from '../lib/api';
import { useAuth } from '../lib/auth';

type Toast = { id: number; message: string; kind: 'info' | 'success' | 'warning' | 'error' };
type Ctx = { push: (msg: string, kind?: Toast['kind']) => void };
const ToastCtx = createContext<Ctx>({ push: () => {} });

export function ToastProvider({ children }: { children: React.ReactNode }) {
  const [toasts, setToasts] = useState<Toast[]>([]);

  const push = useCallback((message: string, kind: Toast['kind'] = 'info') => {
    const id = Date.now() + Math.random();
    setToasts((t) => [...t, { id, message, kind }]);
    setTimeout(() => setToasts((t) => t.filter((x) => x.id !== id)), 6000);
  }, []);

  return (
    <ToastCtx.Provider value={{ push }}>
      {children}
      <div className="fixed top-20 right-4 z-[100] space-y-3 w-80">
        <AnimatePresence>
          {toasts.map((t) => (
            <motion.div
              key={t.id}
              initial={{ opacity: 0, x: 60 }}
              animate={{ opacity: 1, x: 0 }}
              exit={{ opacity: 0, x: 60 }}
              className={`rounded-2xl shadow-float p-4 text-sm font-medium ${
                t.kind === 'success'
                  ? 'bg-emerald-500 text-white'
                  : t.kind === 'error'
                  ? 'bg-red-500 text-white'
                  : t.kind === 'warning'
                  ? 'bg-ufh-gold text-ufh-dark'
                  : 'bg-ufh-blue text-white'
              }`}
            >
              {t.message}
            </motion.div>
          ))}
        </AnimatePresence>
      </div>
    </ToastCtx.Provider>
  );
}

export const useToast = () => useContext(ToastCtx);

// Live notification bell poller — mounts once inside the app shell
export function LiveNotifications() {
  const { me } = useAuth();
  const { push } = useToast();

  // useRef to persist IDs across renders without triggering the effect
  const seenIds = useRef<Set<number> | null>(null);

  const { data } = useQuery({
    queryKey: ['notifPoll'],
    queryFn: Api.notificationsPoll,
    enabled: !!me,
    refetchInterval: 3000,
    refetchIntervalInBackground: true,
  });

  useEffect(() => {
    if (!data) return;

    // First poll — seed the "seen" set, no toast
    if (seenIds.current === null) {
      seenIds.current = new Set(data.latest.map((n) => n.id));
      return;
    }

    // Subsequent polls — toast only for genuinely new IDs
    const newIds: number[] = [];
    data.latest.forEach((n) => {
      if (!seenIds.current!.has(n.id)) {
        newIds.push(n.id);
        push('🔔 ' + n.message, 'warning');
      }
    });

    // Only mutate the ref if there were new items — no state update, no loop
    if (newIds.length > 0) {
      newIds.forEach((id) => seenIds.current!.add(id));
    }
  }, [data, push]);

  return null;
}