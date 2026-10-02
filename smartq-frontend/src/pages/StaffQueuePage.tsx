import { useParams } from 'react-router-dom';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { motion, AnimatePresence } from 'framer-motion';
import { Api, apiError } from '../lib/api';
import { useToast } from '../components/Toast';

export default function StaffQueuePage() {
  const { id } = useParams();
  const sid = Number(id);
  const qc = useQueryClient();
  const { push } = useToast();

  const { data, isLoading } = useQuery({
    queryKey: ['staffQueue', sid],
    queryFn: () => Api.staffQueue(sid),
    refetchInterval: 2500,
  });

  const invalidate = () => qc.invalidateQueries({ queryKey: ['staffQueue', sid] });

  const callNext = useMutation({
    mutationFn: () => Api.callNext(sid),
    onSuccess: (d: any) => { push(d.message, 'success'); invalidate(); },
    onError: (e) => push(apiError(e), 'error'),
  });

  const setStatus = useMutation({
    mutationFn: ({ entryId, s }: { entryId: number; s: 'arrived' | 'served' | 'no-show' }) => {
      if (s === 'arrived') return Api.markArrived(entryId);
      if (s === 'served') return Api.markServed(entryId);
      return Api.markNoShow(entryId);
    },
    onSuccess: () => invalidate(),
    onError: (e) => push(apiError(e), 'error'),
  });

  const reschedule = useMutation({
    mutationFn: ({ entryId, targetId }: { entryId: number; targetId?: number }) =>
      Api.reschedule(entryId, targetId),
    onSuccess: (d: any) => { push(d.message, 'success'); invalidate(); },
    onError: (e) => push(apiError(e), 'error'),
  });

  if (isLoading || !data) return <div className="text-center py-24 text-gray-400">Loading…</div>;

  const waiting = data.waiting;
  const active = data.active;

  return (
    <div>
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 mb-8">
        <div>
          <h1 className="font-display text-3xl font-bold text-ufh-blue">
            {data.service.department_name} — {data.service.name}
          </h1>
          <div className="flex flex-wrap gap-2 mt-3">
            <span className="chip bg-blue-100 text-blue-700">{waiting.length} waiting</span>
            <span className="chip bg-amber-100 text-amber-700">{active.length} active</span>
            <span className="chip bg-emerald-100 text-emerald-700">{data.service.counters} counters</span>
          </div>
        </div>
        <button
          onClick={() => callNext.mutate()}
          disabled={callNext.isPending}
          className="btn-gold text-lg !py-4 !px-6"
        >
          📢 Call Next Student
        </button>
      </div>

      <div className="grid lg:grid-cols-2 gap-6">
        <Panel title={`Waiting List (${waiting.length})`}>
          <table className="w-full text-sm">
            <thead>
              <tr className="text-left text-xs uppercase text-white bg-ufh-blue">
                <th className="px-4 py-3">#</th>
                <th className="px-4 py-3">Number</th>
                <th className="px-4 py-3">Student</th>
                <th className="px-4 py-3">Flags</th>
                <th className="px-4 py-3 text-right">Reschedule</th>
              </tr>
            </thead>
            <tbody>
              {waiting.length === 0 && (
                <tr><td colSpan={5} className="px-4 py-8 text-center text-gray-400">No students waiting.</td></tr>
              )}
              <AnimatePresence>
                {waiting.map((e) => (
                  <motion.tr
                    key={e.id}
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 1 }}
                    exit={{ opacity: 0 }}
                    className="border-b border-gray-100"
                  >
                    <td className="px-4 py-3 text-gray-500">{e.position}</td>
                    <td className="px-4 py-3 font-semibold text-ufh-blue">{e.queue_number}</td>
                    <td className="px-4 py-3">{e.student}</td>
                    <td className="px-4 py-3">
                      {e.running_late && <span className="chip bg-amber-100 text-amber-700">⏰ late</span>}
                    </td>
                    <td className="px-4 py-3 text-right">
                      {e.running_late && (
                        <select
                          onChange={(ev) => {
                            const v = ev.target.value;
                            if (!v) return;
                            reschedule.mutate({ entryId: e.id, targetId: v === 'end' ? undefined : Number(v) });
                            ev.target.value = '';
                          }}
                          className="rounded-lg border border-gray-200 text-xs px-2 py-1"
                          defaultValue=""
                        >
                          <option value="" disabled>Move after…</option>
                          <option value="end">to end</option>
                          {waiting.filter((w) => w.id !== e.id).map((w) => (
                            <option key={w.id} value={w.id}>after {w.queue_number}</option>
                          ))}
                        </select>
                      )}
                    </td>
                  </motion.tr>
                ))}
              </AnimatePresence>
            </tbody>
          </table>
        </Panel>

        <Panel title={`Active Calls (${active.length})`}>
          {active.length === 0 && (
            <div className="p-8 text-center text-gray-400 text-sm">No active calls.</div>
          )}
          <div className="p-4 space-y-3">
            <AnimatePresence>
              {active.map((e) => (
                <motion.div
                  key={e.id}
                  initial={{ opacity: 0, y: 6 }}
                  animate={{ opacity: 1, y: 0 }}
                  exit={{ opacity: 0 }}
                  className="rounded-2xl border border-ufh-gold/40 bg-ufh-gold/5 p-5"
                >
                  <div className="font-display font-bold text-2xl text-ufh-blue text-center">
                    {e.queue_number}
                  </div>
                  <div className="text-center text-xs text-gray-500 mt-1 mb-4">
                    {e.status_display} · {e.counter || 'No counter'}
                  </div>
                  <div className="flex flex-wrap justify-center gap-2">
                    {e.status === 'CALLED' && (
                      <button
                        onClick={() => setStatus.mutate({ entryId: e.id, s: 'arrived' })}
                        className="px-4 py-2 rounded-xl bg-indigo-500 text-white text-sm font-semibold hover:bg-indigo-600"
                      >
                        Arrived
                      </button>
                    )}
                    {(e.status === 'CALLED' || e.status === 'ARRIVED') && (
                      <button
                        onClick={() => setStatus.mutate({ entryId: e.id, s: 'served' })}
                        className="px-4 py-2 rounded-xl bg-emerald-500 text-white text-sm font-semibold hover:bg-emerald-600"
                      >
                        Served ✔
                      </button>
                    )}
                    {e.status === 'CALLED' && (
                      <button
                        onClick={() => setStatus.mutate({ entryId: e.id, s: 'no-show' })}
                        className="px-4 py-2 rounded-xl bg-red-500 text-white text-sm font-semibold hover:bg-red-600"
                      >
                        No-show
                      </button>
                    )}
                  </div>
                </motion.div>
              ))}
            </AnimatePresence>
          </div>
        </Panel>
      </div>
    </div>
  );
}

function Panel({ title, children }: { title: string; children: React.ReactNode }) {
  return (
    <div className="card">
      <div className="px-5 py-4 border-b border-gray-100">
        <h3 className="font-display font-bold text-ufh-blue">{title}</h3>
      </div>
      {children}
    </div>
  );
}