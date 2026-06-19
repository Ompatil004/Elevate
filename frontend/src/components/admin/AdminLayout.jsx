import { NavLink, Outlet, useNavigate, useOutletContext } from 'react-router-dom';
import { adminLogout } from '../../api';
import '../../pages/admin/Admin.css';

const navItems = [
  { path: '/admin/dashboard', label: 'Dashboard', short: 'DB' },
  { path: '/admin/users', label: 'Users', short: 'US' },
  { path: '/admin/content', label: 'Content', short: 'CT' },
  { path: '/admin/system', label: 'System', short: 'SY' },
  { path: '/admin/audit', label: 'Audit', short: 'AU' }
];

export default function AdminLayout() {
  const routeContext = useOutletContext() || {};
  const ownerInfo = routeContext.ownerInfo || null;
  const navigate = useNavigate();

  const handleLogout = async () => {
    try {
      await adminLogout();
    } catch {
      // Best-effort logout.
    } finally {
      navigate('/admin/login', { replace: true });
    }
  };

  return (
    <div className="admin-shell admin-layout">
      <aside className="admin-sidebar">
        <div className="admin-brand">
          <h1>Elevate Admin</h1>
          <p>Owner Control Panel</p>
        </div>

        <nav className="admin-nav">
          {navItems.map((item) => (
            <NavLink
              key={item.path}
              to={item.path}
              className={({ isActive }) =>
                `admin-nav-link ${isActive ? 'active' : ''}`
              }
            >
              <strong>{item.short}</strong> <span>{item.label}</span>
            </NavLink>
          ))}
        </nav>

        <div className="admin-owner">
          <strong>{ownerInfo?.name || 'Owner'}</strong>
          <small>{ownerInfo?.email || '-'}</small>
          <div style={{ marginTop: '10px' }}>
            <button className="admin-btn danger" type="button" onClick={handleLogout}>
              Logout
            </button>
          </div>
        </div>
      </aside>

      <main className="admin-main">
        <Outlet />
      </main>
    </div>
  );
}
