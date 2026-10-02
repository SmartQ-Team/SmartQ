import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { Link } from 'react-router-dom';
import { motion } from 'framer-motion';
import { Api, apiError } from '../lib/api';
import { useToast } from '../components/Toast';
import CongestionBadge from '../components/CongestionBadge';

export default function StudentServicesPage() {
  const qc = useQueryClient();
  const { push } = useToast();

  const services = useQuery({ queryKey: ['services'], queryFn: Api.services, refetchInterval: 4000 });
  const myQ = useQuery({ queryKey: ['myQueue'], queryFn: Api.myQueue, refetchInterval: 4000 });

  const joinMut = useMutation({
    mutationFn: (id: number) => Api.join(id),
    onSuccess: (data) => {
      push(data.message, 'success');
      qc.invalidateQueries({ queryKey: ['myQueue'] });
      qc.invalidateQueries({ queryKey: ['services'] });
      qc.invalidateQueries({ queryKey: ['me'] });
    },
    onError: (e) => push(apiError(e), 'error'),
  });

  const hasActive = !!myQ.data?.entry;

  return (
    <div>
      <div className="mb-8">
        <h1 className="font-display text-4xl font-bold text-ufh-blue mb-2">Campus Services</h1>
        <p className="text-gray-500">Select a service to join its queue.</p>
      </div>

      {hasActive && myQ.data?.entry && (
        <Link
          to="/queue"
          className="block mb-6 p-4 rounded-2xl bg-ufh-gold/10 border border-ufh-gold/40 text-ufh-dark font-medium hover:bg-ufh-gold/20 transition"
        >
          You are currently in queue <span className="font-bold">{myQ.data.entry.queue_number}</span>{' '}
          for {myQ.data.entry.service_name}. <span className="underline">View live status →</span>
        </Link>
      )}

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {services.data?.map((s, i) => (
          <motion.div
            key={s.id}
            initial={{ opacity: 0, y: 12 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: i * 0.05 }}
            whileHover={{ y: -4 }}
            className="card"
          >
            <div className="accent-bar" />
            <div className="p-6">
              <div className="flex items-start justify-between mb-4 gap-2">
                <h3 className="font-display font-bold text-xl text-ufh-blue">{s.name}</h3>
                <CongestionBadge c={s.congestion} />
              </div>
              <p className="text-sm text-gray-500 mb-5">
                {s.department_name}
                {s.department_location && ` · ${s.department_location}`}
              </p>

              <div className="grid grid-cols-2 gap-3 mb-5">
                <div>
                  <div className="text-xs uppercase tracking-wide text-gray-400 font-semibold">Waiting</div>
                  <div className="font-display font-bold text-lg text-ufh-blue">{s.waiting}</div>
                </div>
                <div>
                  <div className="text-xs uppercase tracking-wide text-gray-400 font-semibold">Est. wait</div>
                  <div className="font-display font-bold text-lg text-ufh-gold">~{s.estimate} min</div>
                </div>
              </div>

              <button
                onClick={() => joinMut.mutate(s.id)}
                disabled={hasActive || joinMut.isPending}
                className={hasActive ? 'w-full rounded-2xl py-3 font-semibold bg-gray-200 text-gray-400 cursor-not-allowed' : 'btn-gold w-full'}
              >
                {hasActive ? '🔒 Already in a queue' : joinMut.isPending ? 'Joining…' : 'Join Queue'}
              </button>
            </div>
          </motion.div>
        ))}
      </div>
    </div>
  );
}