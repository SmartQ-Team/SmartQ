import { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { Api, apiError } from '../lib/api';
import { useAuth } from '../lib/auth';
import logo from '../assets/smartq-logo.png';

export default function RegisterPage() {
  const nav = useNavigate();
  const { setMe } = useAuth();

  const [form, setForm] = useState({
    first_name: '',
    last_name: '',
    username: '',
    email: '',
    password1: '',
    password2: '',
    student_number: '',
  });
  const [errors, setErrors] = useState<Record<string, string[]>>({});
  const [busy, setBusy] = useState(false);

  function upd(k: string, v: string) {
    setForm((f) => ({ ...f, [k]: v }));
  }

  async function submit(e: React.FormEvent) {
    e.preventDefault();
    setBusy(true);
    setErrors({});
    try {
      // Post to Django's JSON register endpoint (see api_views_registration.py)
      const user = await Api.register(form);
      setMe(user);
      nav(user.is_staff_role ? '/staff' : '/services', { replace: true });
    } catch (err) {
      const data = (err as any)?.response?.data;
      if (data && typeof data === 'object') {
        setErrors(data);
      } else {
        setErrors({ __all__: [apiError(err)] });
      }
    } finally {
      setBusy(false);
    }
  }

  const field = (label: string, key: string, type = 'text', required = true) => (
    <div className="mb-4">
      <label className="block text-sm font-medium text-gray-700 mb-1">{label}</label>
      <input
        type={type}
        value={(form as any)[key]}
        onChange={(e) => upd(key, e.target.value)}
        className="w-full rounded-2xl border-2 border-gray-200 focus:border-ufh-blue outline-none px-4 py-3 transition"
        required={required}
      />
      {errors[key]?.map((m) => (
        <p key={m} className="text-xs text-red-600 mt-1">{m}</p>
      ))}
    </div>
  );

  return (
    <div className="min-h-screen grid lg:grid-cols-2">
      {/* ---------- Left: hero panel ---------- */}
      <div className="relative bg-gradient-to-br from-ufh-deep via-ufh-blue to-ufh-dark text-white p-8 lg:p-14 flex flex-col justify-center overflow-hidden">
        <div className="absolute inset-0 opacity-10 bg-[radial-gradient(circle_at_30%_20%,white,transparent_40%)]" />
        <div className="relative max-w-md">
          <img src={logo} alt="SmartQ" className="w-16 h-16 mb-8 rounded-2xl shadow-2xl" />
          <h1 className="font-display text-4xl lg:text-5xl font-bold leading-tight mb-4">
            Join SmartQ
          </h1>
          <p className="text-ufh-gold font-semibold text-lg mb-4">
            University of Fort Hare
          </p>
          <p className="text-white/75 text-lg leading-relaxed">
            Create your student account and stop wasting study time in physical queues.
          </p>
        </div>
      </div>

      {/* ---------- Right: form panel ---------- */}
      <div className="flex items-center justify-center p-8 bg-white overflow-y-auto">
        <form onSubmit={submit} className="w-full max-w-md py-6">
          <h2 className="font-display text-3xl font-bold text-ufh-blue mb-1">
            Student Registration
          </h2>
          <p className="text-gray-500 mb-8">Fill in your details to create an account.</p>

          {errors.__all__ && (
            <div className="mb-5 p-3 rounded-xl bg-red-50 border border-red-200 text-red-700 text-sm">
              {errors.__all__.join(' ')}
            </div>
          )}

          {field('First name', 'first_name')}
          {field('Last name', 'last_name')}
          {field('Username', 'username')}
          {field('Email', 'email', 'email')}

          {/* Password with help text */}
          <div className="mb-4">
            <label className="block text-sm font-medium text-gray-700 mb-1">Password</label>
            <input
              type="password"
              value={form.password1}
              onChange={(e) => upd('password1', e.target.value)}
              className="w-full rounded-2xl border-2 border-gray-200 focus:border-ufh-blue outline-none px-4 py-3 transition"
              required
            />
            <ul className="mt-3 space-y-1.5 text-xs text-gray-500 leading-relaxed list-disc list-inside">
              <li>Your password can't be too similar to your other personal information.</li>
              <li>Your password must contain at least 8 characters.</li>
              <li>Your password can't be a commonly used password.</li>
              <li>Your password can't be entirely numeric.</li>
            </ul>
            {errors.password1?.map((m) => (
              <p key={m} className="text-xs text-red-600 mt-2">{m}</p>
            ))}
          </div>

          {/* Password confirmation with help text */}
          <div className="mb-4">
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Password confirmation
            </label>
            <input
              type="password"
              value={form.password2}
              onChange={(e) => upd('password2', e.target.value)}
              className="w-full rounded-2xl border-2 border-gray-200 focus:border-ufh-blue outline-none px-4 py-3 transition"
              required
            />
            <p className="mt-2 text-xs text-gray-500">
              Enter the same password as before, for verification.
            </p>
            {errors.password2?.map((m) => (
              <p key={m} className="text-xs text-red-600 mt-2">{m}</p>
            ))}
          </div>

          {field('Student number', 'student_number')}

          <button disabled={busy} className="btn-gold w-full mt-2">
            {busy ? 'Creating account…' : 'Create Account'}
          </button>

          <p className="mt-6 text-center text-sm text-gray-500">
            Already have an account?{' '}
            <Link to="/login" className="text-ufh-blue font-semibold hover:underline">
              Login here
            </Link>
          </p>
        </form>
      </div>
    </div>
  );
}