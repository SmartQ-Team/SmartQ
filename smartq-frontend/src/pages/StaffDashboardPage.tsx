import { useQuery } from '@tanstack/react-query';
import { Link } from 'react-router-dom';
import { motion } from 'framer-motion';
import { Api } from '../lib/api';
import CongestionBadge from '../components/CongestionBadge';

export default function StaffDashboardPage() {
  const { data, isLoading } = useQuery({
    queryKey: ['staffDashboard'],
    queryFn: Api.staffDashboard,
    refetchInterval: 4000,
  });

  if (isLoading) return <div className="text-center py-24 text-gray-400">Loading…</div>;
  if (!data) return null;

  const kpis = [
    { label: 'Waiting now', value: data.stats.waiting_total },
    { label: 'Served today', value: data.stats.served },
    { label: 'Avg wait (min)', value: data.stats.avg_wait },
    { label: 'No-shows', value: data.stats.no_shows },
    { label: 'Cancelled', value: data.stats.cancelled },
  ];

  return (
    <div>
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between mb-8 gap-4">
        <div>
          <h1 className="font-display text-4xl font-bold text-ufh-blue">
            {data.department || 'All Departments'} — Staff Dashboard
          </h1>
          <p className="text-gray-500">Live queue overview</p>
        </div>
        <Link to="/staff/analytics" className="btn-ghost self-start">View Analytics</Link>
      </div>

      <div className="grid grid-cols-2 md:grid-cols-5 gap-4 mb-10">
        {kpis.map((k, i) => (
          <motion.div
            key={k.label}
            initial={{ opacity: 0, y: 8 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: i * 0.05 }}
            className="kpi"
          >
            <div className="text-xs uppercase tracking-wider text-gray-400 font-semibold">{k.label}</div>
            <div className="mt-2 font-display font-bold text-3xl text-ufh-blue">{k.value}</div>
          </motion.div>
        ))}
      </div>

      <h2 className="font-display text-xl font-bold text-ufh-blue mb-4">Queues</h2>
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {data.cards.map((c) => (
          <div key={c.id} className="card">
            <div className="accent-bar" />
            <div className="p-6">
              <div className="flex items-start justify-between mb-4 gap-2">
                <h3 className="font-display font-bold text-lg text-ufh-blue">{c.name}</h3>
                <CongestionBadge c={c.congestion} />
              </div>
              <p className="text-sm text-gray-500 mb-4">{c.department_name}</p>
              <div className="grid grid-cols-2 gap-3 mb-5 text-sm">
                <div>
                  <div className="text-gray-400 text-xs uppercase font-semibold">Waiting</div>
                  <div className="font-bold text-ufh-blue">{c.waiting}</div>
                </div>
                <div className="text-right">
                  <div className="text-gray-400 text-xs uppercase font-semibold">Active calls</div>
                  <div className="font-bold text-ufh-blue">{c.active_calls} / {c.counters} counters</div>
                </div>
              </div>
              <Link to={`/staff/queue/${c.id}`} className="btn-blue w-full">
                Manage Queue
              </Link>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}