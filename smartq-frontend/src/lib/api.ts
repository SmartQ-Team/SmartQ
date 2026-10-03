import axios, { AxiosError } from 'axios';
import type { InternalAxiosRequestConfig } from 'axios';

const BASE = import.meta.env.VITE_API_URL || '';

export const api = axios.create({
  baseURL: `${BASE}/api`,
  withCredentials: true,
  xsrfCookieName: 'csrftoken',
  xsrfHeaderName: 'X-CSRFToken',
});

// Eagerly fetch CSRF cookie once on module load
api.get('/csrf/').catch(() => {});

// ---------- Cookie helper ----------
function readCookie(name: string): string | null {
  const match = document.cookie.match(new RegExp('(^|;\\s*)' + name + '=([^;]*)'));
  return match ? decodeURIComponent(match[2]) : null;
}

// ---------- CSRF bootstrap ----------
// Django rotates the CSRF token on login/logout, so we always fetch a fresh one
// before any unsafe request. The GET /csrf/ endpoint uses @ensure_csrf_cookie
// and returns a Set-Cookie header with the token.
export async function ensureCsrf(): Promise<string | null> {
  try {
    await api.get('/csrf/');
  } catch {
    // ignore — we'll still try with whatever cookie we have
  }
  return readCookie('csrftoken');
}

// ---------- Interceptor: attach X-CSRFToken on every unsafe request ----------
api.interceptors.request.use(async (config: InternalAxiosRequestConfig) => {
  const method = (config.method || 'get').toLowerCase();
  const unsafe = ['post', 'put', 'patch', 'delete'].includes(method);
  if (unsafe) {
    let token = readCookie('csrftoken');
    if (!token) {
      token = await ensureCsrf();
    }
    if (token) {
      config.headers = config.headers || {};
      config.headers['X-CSRFToken'] = token;
    }
  }
  return config;
});

// ---------- Error helper ----------
export function apiError(err: unknown): string {
  if (err instanceof AxiosError) {
    const data = err.response?.data as any;
    if (typeof data === 'string') return data;
    if (data?.detail) return data.detail;
    return err.message;
  }
  return 'Something went wrong';
}

// ---------- Types ----------
export type Role = 'STUDENT' | 'STAFF' | 'SUPERVISOR' | 'ADMIN';

export type Me = {
  id: number;
  username: string;
  first_name: string;
  last_name: string;
  email: string;
  role: Role;
  department_id: number | null;
  department_name: string | null;
  student_number: string | null;
  is_staff_role: boolean;
  unread_notifications: number;
};

export type Congestion = { label: 'Normal' | 'Moderate' | 'Congested'; css: string };

export type Service = {
  id: number;
  name: string;
  description: string;
  department_id: number;
  department_name: string;
  department_location: string;
  average_service_time_minutes: number;
  waiting: number;
  estimate: number;
  congestion: Congestion;
};

export type Department = {
  id: number;
  name: string;
  location: string;
  description: string;
  service_count: number;
};

export type EntryStatus =
  | 'WAITING' | 'CALLED' | 'ARRIVED' | 'SERVING'
  | 'COMPLETED' | 'CANCELLED' | 'NO_SHOW';

export type QueueEntry = {
  id: number;
  queue_number: string;
  status: EntryStatus;
  status_display: string;
  position: number;
  running_late: boolean;
  join_time: string;
  called_time: string | null;
  arrival_time: string | null;
  completion_time: string | null;
  waiting_time_minutes: number | null;
  service_id: number;
  service_name: string;
  department_name: string;
  department_location: string;
  student_username: string;
  counter_name: string | null;
};

export type MyQueue = {
  entry: QueueEntry | null;
  ahead?: number;
  estimate?: number;
  currently_serving?: string | null;
  active?: boolean;
};

export type QueueStatus = {
  queue_number: string;
  status: EntryStatus;
  status_display: string;
  ahead: number;
  estimate: number;
  currently_serving: string | null;
  running_late: boolean;
  active: boolean;
};

export type Notification = {
  id: number;
  message: string;
  created_at: string;
  read: boolean;
};

export type NotificationPoll = {
  unread: number;
  latest: { id: number; message: string; created_at: string }[];
};

export type StaffCard = {
  id: number;
  name: string;
  department_name: string;
  waiting: number;
  active_calls: number;
  counters: number;
  congestion: Congestion;
};

export type StaffDashboard = {
  department: string | null;
  stats: {
    waiting_total: number;
    served: number;
    no_shows: number;
    cancelled: number;
    avg_wait: number;
  };
  cards: StaffCard[];
};

export type StaffQueue = {
  service: { id: number; name: string; department_name: string; counters: number };
  waiting: {
    id: number; queue_number: string; position: number;
    student: string; running_late: boolean;
  }[];
  active: {
    id: number; queue_number: string; status: EntryStatus;
    status_display: string; counter: string | null;
  }[];
};

export type Analytics = {
  department: string;
  summary: {
    served: number; no_shows: number; cancelled: number;
    waiting_now: number; avg_wait: number; avg_service: number; max_queue: number;
  };
  peak_periods: { hour: string; count: number }[];
  counters: { counter: string; served: number }[];
};

export type Board = {
  boards: {
    service_id: number; service: string; department: string;
    now_serving: string | null; counter: string | null; waiting: number;
  }[];
};

// ---------- Endpoints ----------
export const Api = {
  login: (username: string, password: string) =>
    api.post<Me>('/login/', { username, password }).then((r) => r.data),
  logout: () => api.post('/logout/').then((r) => r.data),
  me: () => api.get<Me>('/me/').then((r) => r.data),

  services: () => api.get<Service[]>('/services/').then((r) => r.data),
  departments: () => api.get<Department[]>('/departments/').then((r) => r.data),
  join: (id: number) =>
    api.post<{ entry: QueueEntry; message: string }>(`/services/${id}/join/`).then((r) => r.data),

  myQueue: () => api.get<MyQueue>('/queue/my/').then((r) => r.data),
  queueStatus: (id: number) => api.get<QueueStatus>(`/queue/status/${id}/`).then((r) => r.data),
  cancel: (id: number) => api.post(`/queue/${id}/cancel/`).then((r) => r.data),
  markLate: (id: number) => api.post(`/queue/${id}/late/`).then((r) => r.data),

  notifications: () => api.get<Notification[]>('/notifications/').then((r) => r.data),
  notificationsPoll: () => api.get<NotificationPoll>('/notifications/poll/').then((r) => r.data),
  notificationsReadAll: () => api.post('/notifications/read-all/').then((r) => r.data),

  board: () => api.get<Board>('/board/').then((r) => r.data),

  staffDashboard: () => api.get<StaffDashboard>('/staff/dashboard/').then((r) => r.data),
  staffQueue: (id: number) => api.get<StaffQueue>(`/staff/queue/${id}/`).then((r) => r.data),
  callNext: (id: number) => api.post(`/staff/call-next/${id}/`).then((r) => r.data),
  markArrived: (id: number) => api.post(`/staff/entry/${id}/arrived/`).then((r) => r.data),
  markServed: (id: number) => api.post(`/staff/entry/${id}/served/`).then((r) => r.data),
  markNoShow: (id: number) => api.post(`/staff/entry/${id}/no-show/`).then((r) => r.data),
  reschedule: (id: number, targetId?: number) =>
    api.post(`/staff/entry/${id}/reschedule/`, { target_id: targetId ?? null }).then((r) => r.data),
  analytics: () => api.get<Analytics>('/staff/analytics/').then((r) => r.data),

  reportIssue: (category: string, description: string) =>
    api.post('/report/', { category, description }).then((r) => r.data),
};