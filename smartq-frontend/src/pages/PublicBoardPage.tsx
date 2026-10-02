import { useQuery } from '@tanstack/react-query';
import { useEffect, useRef, useState } from 'react';
import { Api } from '../lib/api';
import logo from '../assets/smartq-logo.png';

export default function PublicBoardPage() {
  const { data } = useQuery({
    queryKey: ['board'],
    queryFn: Api.board,
    refetchInterval: 2000,
  });

  const [clock, setClock] = useState(new Date().toLocaleTimeString());
  const prev = useRef<Record<string, string | null>>({});

  useEffect(() => {
    const t = setInterval(() => setClock(new Date().toLocaleTimeString()), 1000);
    return () => clearInterval(t);
  }, []);

  useEffect(() => {
    if (!data) return;
    data.boards.forEach((b) => {
      const key = b.service;
      if (prev.current[key] !== undefined && b.now_serving && prev.current[key] !== b.now_serving) {
        chime();
      }
      prev.current[key] = b.now_serving;
    });
  }, [data]);

  return (
    <div className="min-h-screen bg-gradient-to-br from-ufh-deep via-ufh-dark to-ufh-blue text-white">
      <header className="flex items-center gap-6 px-8 pt-6">
        <div className="flex items-center gap-3">
            <img src={logo} alt="SmartQ" className="w-12 h-12 rounded-xl" />
            <span className="text-ufh-gold font-display font-extrabold text-3xl tracking-wide">SmartQ</span>
        </div>
        <span className="flex-1 text-white/80 text-lg">
          Live Service Board — University of Fort Hare
        </span>
        <span className="text-ufh-gold font-display font-bold text-2xl tabular-nums">{clock}</span>
      </header>

      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6 p-8">
        {data?.boards.map((b) => (
          <div
            key={b.service_id}
            className="rounded-3xl border border-ufh-gold/40 bg-white/5 backdrop-blur-md text-center p-7"
          >
            <p className="text-xs uppercase tracking-widest text-white/60 mb-1">{b.department}</p>
            <h3 className="font-display font-bold text-white mb-3">{b.service}</h3>
            <div className="font-display font-extrabold text-ufh-gold tracking-widest text-6xl leading-none my-3 drop-shadow-[0_0_24px_rgba(255,184,28,0.45)]">
              {b.now_serving || '—'}
            </div>
            <p className="text-sm text-white/70">
              {b.counter ? `Counter: ${b.counter}` : 'No active call'}
            </p>
            <p className="text-xs text-white/50 mt-1">{b.waiting} waiting</p>
          </div>
        ))}
        {(!data || data.boards.length === 0) && (
          <p className="text-white/60 col-span-full text-center py-24">No active services.</p>
        )}
      </div>
    </div>
  );
}

function chime() {
  try {
    const AC = (window as any).AudioContext || (window as any).webkitAudioContext;
    const ctx = new AC();
    const t = ctx.currentTime;
    [523.25, 783.99].forEach((f, i) => {
      const o = ctx.createOscillator();
      const g = ctx.createGain();
      o.frequency.value = f;
      o.connect(g); g.connect(ctx.destination);
      const start = t + i * 0.25;
      g.gain.setValueAtTime(0.0001, start);
      g.gain.exponentialRampToValueAtTime(0.3, start + 0.03);
      g.gain.exponentialRampToValueAtTime(0.0001, start + 0.5);
      o.start(start); o.stop(start + 0.55);
    });
  } catch { /* audio blocked */ }
}