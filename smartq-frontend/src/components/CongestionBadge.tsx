import type { Congestion } from '../lib/api';

const map: Record<string, string> = {
  Normal: 'bg-emerald-100 text-emerald-700',
  Moderate: 'bg-amber-100 text-amber-700',
  Congested: 'bg-red-100 text-red-700',
};

export default function CongestionBadge({ c }: { c: Congestion }) {
  return (
    <span className={`chip ${map[c.label] || 'bg-gray-100 text-gray-700'}`}>
      {c.label}
    </span>
  );
}