import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { motion } from 'framer-motion';
import { Api } from '../lib/api';

export default function NotificationsPage() {
  const qc = useQueryClient();
  const { data } = useQuery({
    queryKey: ['notifications'],
    queryFn: Api.notifications,
    refetchInterval: 5000,
  });

  const readAll = useMutation({
    mutationFn: Api.notificationsReadAll,
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ['notifications'] });
      qc.invalidateQueries({ queryKey: ['notifPoll'] });
      qc.invalidateQueries({ queryKey: ['me'] });
    },
  });

  return (
    <div className="max-w-4xl mx-auto">
      <div className="flex items-center justify-between mb-6 gap-4">
        <h1 className="font-display text-3xl font-bold text-ufh-blue">Notifications</h1>
        <button
          onClick={() => readAll.mutate()}
          className="btn-gold !py-2 !px-4 !text-sm"
        >
          Mark all as read
        </button>
      </div>

      <div className="card divide-y divide-gray-100">
        {data?.length === 0 && (
          <div className="p-12 text-center text-gray-400">No notifications yet.</div>
        )}
        {data?.map((n, i) => (
          <motion.div
            key={n.id}
            initial={{ opacity: 0, x: -8 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: i * 0.015 }}
            className={`p-4 sm:p-5 flex items-center justify-between gap-4 ${
              !n.read ? 'bg-ufh-gold/5' : ''
            }`}
          >
            <div className="flex-1 min-w-0">
              <div className="text-sm text-ufh-text">{n.message}</div>
              <div className="text-xs text-gray-400 mt-1">
                {new Date(n.created_at).toLocaleString()}
              </div>
            </div>
            {!n.read && (
              <span className="chip bg-ufh-gold text-ufh-dark">New</span>
            )}
          </motion.div>
        ))}
      </div>
    </div>
  );
}