import { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import axios from 'axios';

const BASE = import.meta.env.VITE_API_URL || 'http://127.0.0.1:8000';

export default function RegisterPage() {
  const nav = useNavigate();
  const [form, setForm] = useState({
    first_name: '', last_name: '', username: '', email: '',
    password1: '', password2: '', student_number: '',
  });
  const [errors, setErrors] = useState<Record<string, string[]>>({});
  const [busy, setBusy] = useState(false);

  function upd(k: string, v: string) { setForm((f) => ({ ...f, [k]: v })); }

  async function submit(e: React.FormEvent) {
    e.preventDefault();
    setBusy(true);
    setErrors({});
    try {
      // Use the existing Django template form endpoint (it accepts POST + redirects).
      // For SPA we'd add a JSON registration endpoint; see note below.
      const params = new URLSearchParams(form as any);
      await axios.post(`${BASE}/register/`, params, {
        withCredentials: true,
        headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
        maxRedirects: 0,
        validateStatus: (s) => s < 400 || s === 302,
      });
      nav('/login');
    } catch (e: any) {
      // fall through — the template renders errors, but in SPA we show generic
      setErrors({ __all__: ['Registration failed. Please check your details.'] });
    } finally {
      setBusy(false);
    }
  }

  const field = (label: string, key: string, type = 'text') => (
    <div className="mb-4">
      <label className="block text-sm font-medium text-gray-700 mb-1">{label}</label>
      <input
        type={type}
        value={(form as any)[key]}
        onChange={(e) => upd(key, e.target.value)}
        className="w-full rounded-2xl border-2 border-gray-200 focus:border-ufh-blue outline-none px-4 py-3 transition"
        required
      />
      {errors[key]?.map((m) => (
        <p key={m} className="text-xs text-red-600 mt-1">{m}</p>
      ))}
    </div>
  );

  return (
    <div className="min-h-screen grid lg:grid-cols-2">
      <div className="hidden lg:flex bg-gradient-to-br from-ufh-deep via-ufh-blue to-ufh-dark text-white p-14 flex-col justify-center">
        <h1 className="font-display text-5xl font-bold mb-4">Join SmartQ</h1>
        <p className="text-ufh-gold font-semibold text-lg mb-4">University of Fort Hare</p>
        <p className="text-white/75 max-w-md">
          Create your student account and stop wasting study time in physical queues.
        </p>
      </div>

      <div className="flex items-center justify-center p-8 overflow-y-auto">
        <form onSubmit={submit} className="w-full max-w-md">
          <h2 className="font-display text-3xl font-bold text-ufh-blue mb-1">
            Student Registration
          </h2>
          <p className="text-gray-500 mb-8">Fill in your details to create an account.</p>

          {errors.__all__ && (
            <div className="mb-4 p-3 rounded-xl bg-red-50 border border-red-200 text-red-700 text-sm">
              {errors.__all__.join(' ')}
            </div>
          )}

          {field('First name', 'first_name')}
          {field('Last name', 'last_name')}
          {field('Username', 'username')}
          {field('Email', 'email', 'email')}
          {field('Password', 'password1', 'password')}
          {field('Password confirmation', 'password2', 'password')}
          {field('Student number', 'student_number')}

          <button disabled={busy} className="btn-gold w-full mt-2">
            {busy ? 'Creating account…' : 'Create Account'}
          </button>
          <p className="mt-4 text-center text-sm text-gray-500">
            Already have an account?{' '}
            <Link to="/login" className="text-ufh-blue font-semibold hover:underline">Login here</Link>
          </p>
        </form>
      </div>
    </div>
  );
}