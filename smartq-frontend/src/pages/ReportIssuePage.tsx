import { useState } from 'react';
import { useMutation } from '@tanstack/react-query';
import { useNavigate } from 'react-router-dom';
import { Api, apiError } from '../lib/api';
import { useToast } from '../components/Toast';

export default function ReportIssuePage() {
  const [category, setCategory] = useState('Bug');
  const [description, setDescription] = useState('');
  const nav = useNavigate();
  const { push } = useToast();

  const m = useMutation({
    mutationFn: () => Api.reportIssue(category, description),
    onSuccess: (data: any) => {
      push(data.message, data.delivered ? 'success' : 'warning');
      nav(-1);
    },
    onError: (e) => push(apiError(e), 'error'),
  });

  return (
    <div className="max-w-xl mx-auto">
      <div className="card p-6">
        <h1 className="font-display text-2xl font-bold text-ufh-blue mb-1">Report a Problem</h1>
        <p className="text-sm text-gray-500 mb-6">
          Your report is emailed directly to the administrator and recorded in the audit log.
        </p>

        <label className="block text-sm font-medium text-gray-700 mb-1">Category</label>
        <select
          value={category}
          onChange={(e) => setCategory(e.target.value)}
          className="w-full rounded-2xl border-2 border-gray-200 focus:border-ufh-blue outline-none px-4 py-3 mb-4 transition"
        >
          <option>Bug</option>
          <option>Design / UI</option>
          <option>Performance</option>
          <option>Other</option>
        </select>

        <label className="block text-sm font-medium text-gray-700 mb-1">Describe the problem</label>
        <textarea
          value={description}
          onChange={(e) => setDescription(e.target.value)}
          rows={6}
          placeholder="What happened? What did you expect?"
          className="w-full rounded-2xl border-2 border-gray-200 focus:border-ufh-blue outline-none px-4 py-3 mb-6 transition resize-none"
        />

        <button
          onClick={() => m.mutate()}
          disabled={m.isPending || !description.trim()}
          className="btn-gold w-full"
        >
          {m.isPending ? 'Sending…' : 'Send Report'}
        </button>
      </div>
    </div>
  );
}