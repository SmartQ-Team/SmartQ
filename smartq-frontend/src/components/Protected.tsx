import { Navigate, Outlet } from 'react-router-dom';
import { useAuth } from '../lib/auth';

export function RequireAuth() {
  const { me, isLoading } = useAuth();
  if (isLoading) return <div className="min-h-screen grid place-items-center text-gray-400">Loading…</div>;
  if (!me) return <Navigate to="/login" replace />;
  return <Outlet />;
}

export function RequireStaff() {
  const { me, isLoading } = useAuth();
  if (isLoading) return null;
  if (!me?.is_staff_role) return <Navigate to="/services" replace />;
  return <Outlet />;
}