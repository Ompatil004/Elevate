import { BrowserRouter, Routes, Route, Navigate, useNavigate, useLocation } from 'react-router-dom';
import { useState, useEffect, lazy, Suspense, useCallback } from 'react';
import { NotificationProvider, useNotification } from './components/NotificationProvider';
import { logoutSafe } from './utils/storage';
import { getSessionStatus, logoutUser } from './api';
import { ThemeProvider } from './context/ThemeContext';
import AuroraBackground from './components/AuroraBackground';
import './App.css';

// Safe lazy loader that automatically reloads the tab once if a new deployment changed Vite chunk hashes
const safeLazy = (importFn) => lazy(async () => {
  const key = 'elevate_chunk_retry';
  try {
    const module = await importFn();
    sessionStorage.removeItem(key);
    return module;
  } catch (error) {
    const isChunkError = error?.message?.includes('dynamically imported module')
      || error?.message?.includes('Importing a module script failed')
      || error?.name === 'TypeError';

    if (isChunkError && !sessionStorage.getItem(key)) {
      sessionStorage.setItem(key, '1');
      console.warn('New app deployment detected — refreshing tab for updated assets...');
      window.location.reload();
    }
    throw error;
  }
});

const Login     = safeLazy(() => import('./pages/Login'));
const Register  = safeLazy(() => import('./pages/Register'));
const Dashboard = safeLazy(() => import('./pages/Dashboard'));
const ProfileSetup = safeLazy(() => import('./pages/ProfileSetup'));
const Workout   = safeLazy(() => import('./pages/Workout'));
const Nutrition = safeLazy(() => import('./pages/Nutrition'));
const Chatbot   = safeLazy(() => import('./pages/Chatbot'));
const DashboardActionIdeas = safeLazy(() => import('./pages/DashboardActionIdeas'));
const ForgotPassword = safeLazy(() => import('./pages/ForgotPassword'));
const AdminLogin = safeLazy(() => import('./pages/admin/AdminLogin'));
const AdminRoute = safeLazy(() => import('./components/admin/AdminRoute'));
const AdminLayout = safeLazy(() => import('./components/admin/AdminLayout'));
const AdminDashboard = safeLazy(() => import('./pages/admin/Dashboard'));
const AdminUsers = safeLazy(() => import('./pages/admin/Users'));
const AdminContent = safeLazy(() => import('./pages/admin/Content'));
const AdminSystem = safeLazy(() => import('./pages/admin/System'));
const AdminAudit = safeLazy(() => import('./pages/admin/Audit'));

// ------------------------------------------------------------------
// Full-screen loader that matches the dark theme — prevents white flash
// on Suspense boundary while lazy chunks are loading.
// ------------------------------------------------------------------
const PageLoader = () => (
  <div style={{
    display: 'flex', alignItems: 'center', justifyContent: 'center',
    minHeight: '100dvh', background: '#09090b', color: '#a5b4fc',
    fontSize: '1rem', fontFamily: "'Inter', sans-serif",
    letterSpacing: '0.5px', gap: '12px'
  }}>
    <span style={{
      width: 18, height: 18, borderRadius: '50%',
      border: '2px solid #6366f1', borderTopColor: 'transparent',
      animation: 'spin 0.7s linear infinite', display: 'inline-block'
    }} />
    Loading Elevate...
  </div>
);

// ------------------------------------------------------------------
// Inner app — lives inside BrowserRouter so it can call useNavigate
// and useNotification (both need their respective providers).
// ------------------------------------------------------------------
function AppInner({ isAuthenticated, setIsAuthenticated }) {
  const navigate = useNavigate();
  const location = useLocation();
  const isAdminRoute = location.pathname.startsWith('/admin');
  const { showError } = useNotification();

  const handleLogout = useCallback((reason = 'manual') => {
    // Best-effort server logout to clear HttpOnly cookie.
    logoutUser().catch(() => {});
    logoutSafe();
    setIsAuthenticated(false);
    if (reason === 'inactivity') {
      // The notification will briefly appear but the route guard redirects instantly.
      // This is intentional — we want the user to know why they were logged out.
      showError('Session expired due to inactivity. Please log in again.', 6000);
    }
    navigate('/login', { replace: true });
  }, [navigate, setIsAuthenticated, showError]);





  return (
    <>
      {!isAdminRoute && <AuroraBackground />}
      <Suspense fallback={<PageLoader />}>
      <Routes>
        <Route path="/admin/login" element={<AdminLogin />} />
        <Route path="/admin" element={<AdminRoute />}>
          <Route element={<AdminLayout />}>
            <Route path="dashboard" element={<AdminDashboard />} />
            <Route path="users" element={<AdminUsers />} />
            <Route path="content" element={<AdminContent />} />
            <Route path="system" element={<AdminSystem />} />
            <Route path="audit" element={<AdminAudit />} />
            <Route index element={<Navigate to="/admin/dashboard" replace />} />
            <Route path="*" element={<Navigate to="/admin/dashboard" replace />} />
          </Route>
        </Route>

        <Route
          path="/login"
          element={!isAuthenticated
            ? <Login setIsAuthenticated={setIsAuthenticated} />
            : <Navigate to="/dashboard" replace />}
        />
        <Route
          path="/register"
          element={!isAuthenticated ? <Register /> : <Navigate to="/dashboard" replace />}
        />
        <Route
          path="/forgot-password"
          element={!isAuthenticated ? <ForgotPassword /> : <Navigate to="/dashboard" replace />}
        />
        {/* SEC-3: Route for email reset links — ForgotPassword reads ?token=&email= from URL */}
        <Route
          path="/reset-password"
          element={!isAuthenticated ? <ForgotPassword /> : <Navigate to="/dashboard" replace />}
        />
        <Route
          path="/dashboard"
          element={isAuthenticated
            ? <Dashboard onLogout={() => handleLogout('manual')} />
            : <Navigate to="/login" replace />}
        />
        <Route
          path="/profile-setup"
          element={isAuthenticated ? <ProfileSetup onLogout={() => handleLogout('manual')} /> : <Navigate to="/login" replace />}
        />
        <Route
          path="/profile"
          element={isAuthenticated ? <ProfileSetup onLogout={() => handleLogout('manual')} /> : <Navigate to="/login" replace />}
        />
        <Route
          path="/workout"
          element={isAuthenticated ? <Workout onLogout={() => handleLogout('manual')} /> : <Navigate to="/login" replace />}
        />
        <Route
          path="/nutrition"
          element={isAuthenticated ? <Nutrition onLogout={() => handleLogout('manual')} /> : <Navigate to="/login" replace />}
        />
        <Route
          path="/chatbot"
          element={isAuthenticated ? <Chatbot onLogout={() => handleLogout('manual')} /> : <Navigate to="/login" replace />}
        />
        <Route
          path="/dashboard-action-ideas"
          element={isAuthenticated ? <DashboardActionIdeas /> : <Navigate to="/login" replace />}
        />
        <Route
          path="/"
          element={<Navigate to={isAuthenticated ? '/dashboard' : '/login'} replace />}
        />
        <Route path="*" element={<Navigate to="/login" replace />} />
      </Routes>
    </Suspense>
    </>
  );
}

// ------------------------------------------------------------------
// Root component — reads auth state synchronously on first render
// by validating the existing HttpOnly cookie session via /profile.
// ------------------------------------------------------------------
export default function App() {
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [authResolved, setAuthResolved] = useState(false);

  const verifyAuthSession = useCallback(async () => {
    try {
      const { data } = await getSessionStatus();
      setIsAuthenticated(Boolean(data?.authenticated));
    } catch {
      logoutSafe();
      setIsAuthenticated(false);
    } finally {
      setAuthResolved(true);
    }
  }, []);

  // Resolve cookie-backed session at startup.
  useEffect(() => {
    verifyAuthSession();
  }, [verifyAuthSession]);

  // Keep auth state in sync when tab regains focus or user metadata changes.
  useEffect(() => {
    const onStorage = (e) => {
      if (!e.key || e.key === 'user') {
        verifyAuthSession();
      }
    };
    const onFocus = () => verifyAuthSession();

    window.addEventListener('storage', onStorage);
    window.addEventListener('focus', onFocus);
    return () => {
      window.removeEventListener('storage', onStorage);
      window.removeEventListener('focus', onFocus);
    };
  }, [verifyAuthSession]);

  if (!authResolved) {
    return <PageLoader />;
  }

  return (
    <ThemeProvider>
      <NotificationProvider>
        <BrowserRouter>
          <AppInner
            isAuthenticated={isAuthenticated}
            setIsAuthenticated={setIsAuthenticated}
          />
        </BrowserRouter>
      </NotificationProvider>
    </ThemeProvider>
  );
}
