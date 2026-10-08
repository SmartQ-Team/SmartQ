import { useQuery } from '@tanstack/react-query';
import { motion } from 'framer-motion';
import { Api } from '../lib/api';

export default function AnalyticsPage() {
  const { data, isLoading } = useQuery({
    queryKey: ['analytics'],
    queryFn: Api.analytics,
    refetchInterval: 8000,
  });

  if (isLoading || !data) return <div className="text-center py-24 text-gray-400">Loading…</div>;

  const kpis = [
    { label: 'Served today', value: data.summary.served },
    { label: 'Avg wait (min)', value: data.summary.avg_wait },
    { label: 'Avg service (min)', value: data.summary.avg_service },
    { label: 'Max queue length', value: data.summary.max_queue },
    { label: 'No-shows', value: data.summary.no_shows },
    { label: 'Cancellations', value: data.summary.cancelled },
  ];

  const maxPeak = Math.max(1, ...data.peak_periods.map((p) => p.count));

  return (
    <div>
      <h1 className="font-display text-4xl font-bold text-ufh-blue mb-1">Queue Analytics</h1>
      <p className="text-gray-500 mb-8">{data.department} — today</p>

      <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-4 mb-10">
        {kpis.map((k, i) => (
          <motion.div
            key={k.label}
            initial={{ opacity: 0, y: 8 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: i * 0.04 }}
            className="kpi"
          >
            <div className="text-[10px] uppercase tracking-wider text-gray-400 font-semibold">{k.label}</div>
            <div className="mt-2 font-display font-bold text-2xl text-ufh-blue">{k.value}</div>
          </motion.div>
        ))}
      </div>

      <div className="grid lg:grid-cols-2 gap-6">
        <div className="card p-6">
          <h3 className="font-display font-bold text-ufh-blue mb-6">
            Peak Periods (arrivals per hour)
          </h3>
          {data.peak_periods.length === 0 && (
            <p className="text-gray-400 text-sm">No data yet today.</p>
          )}
          <div className="space-y-4">
            {data.peak_periods.map((p) => (
              <div key={p.hour}>
                <div className="flex justify-between text-sm mb-1">
                  <span className="text-gray-500 font-medium">{p.hour}</span>
                  <span className="font-bold text-ufh-blue">{p.count}</span>
                </div>
                <div className="h-3 rounded-full bg-gray-100 overflow-hidden">
                  <motion.div
                    initial={{ width: 0 }}
                    animate={{ width: `${(p.count / maxPeak) * 100}%` }}
                    transition={{ duration: 0.8, ease: 'easeOut' }}
                    className="h-full bg-gradient-to-r from-ufh-gold to-ufh-goldDark rounded-full"
                  />
                </div>
              </div>
            ))}
          </div>
        </div>

        <div className="card">
          <div className="px-6 py-5">
            <h3 className="font-display font-bold text-ufh-blue">
              Counter Utilisation (served today)
            </h3>
          </div>
          <table className="w-full text-sm">
            <thead>
              <tr className="bg-ufh-blue text-white text-left">
               <th className="px-6 py-3">Counter</th>
               <th className="px-6 py-3">Department</th>
               <th className="px-6 py-3 text-right">Students served</th>
              </tr>
            </thead>
          <tbody>
            {data.counters.length === 0 && (
              <tr><td colSpan={3} className="px-6 py-6 text-center text-gray-400">No active counters.</td></tr>
          )}
          {data.counters.map((c) => (
            <tr key={`${c.department}-${c.counter}`} className="border-b border-gray-100">
              <td className="px-6 py-4">{c.counter}</td>
              <td className="px-6 py-4 text-gray-500 text-xs">{c.department}</td>
              <td className="px-6 py-4 text-right font-semibold text-ufh-blue">{c.served}</td>
            </tr>
          ))}
          </tbody>
        </table>
        </div>
      </div>
    </div>
  );
}