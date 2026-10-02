import { Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider } from './lib/auth';
import { ToastProvider } from './components/Toast';
import AppShell from './components/AppShell';
import { RequireAuth, RequireStaff } from './components/Protected';

import LoginPage from './pages/LoginPage';
import RegisterPage from './pages/RegisterPage';
import StudentServicesPage from './pages/StudentServicesPage';
import MyQueuePage from './pages/MyQueuePage';
import NotificationsPage from './pages/NotificationsPage';
import ReportIssuePage from './pages/ReportIssuePage';
import StaffDashboardPage from './pages/StaffDashboardPage';
import StaffQueuePage from './pages/StaffQueuePage';
import AnalyticsPage from './pages/AnalyticsPage';
import PublicBoardPage from './pages/PublicBoardPage';

export default function App() {
  return (
    <AuthProvider>
      <ToastProvider>
        <Routes>
          {/* Public */}
          <Route path="/login" element={<LoginPage />} />
          <Route path="/register" element={<RegisterPage />} />
          <Route path="/board" element={<PublicBoardPage />} />

          {/* Protected */}
          <Route element={<RequireAuth />}>
            <Route
              path="/*"
              element={
                <AppShell>
                  <Routes>
                    <Route path="/" element={<Navigate to="/services" replace />} />
                    <Route path="/services" element={<StudentServicesPage />} />
                    <Route path="/queue" element={<MyQueuePage />} />
                    <Route path="/notifications" element={<NotificationsPage />} />
                    <Route path="/report" element={<ReportIssuePage />} />

                    <Route element={<RequireStaff />}>
                      <Route path="/staff" element={<StaffDashboardPage />} />
                      <Route path="/staff/queue/:id" element={<StaffQueuePage />} />
                      <Route path="/staff/analytics" element={<AnalyticsPage />} />
                    </Route>

                    <Route path="*" element={<Navigate to="/services" replace />} />
                  </Routes>
                </AppShell>
              }
            />
          </Route>
        </Routes>
      </ToastProvider>
    </AuthProvider>
  );
}