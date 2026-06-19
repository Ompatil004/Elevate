import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { adminLogin } from '../../api';
import './Admin.css';

export default function AdminLogin() {
  const [formData, setFormData] = useState({
    email: '',
    password: '',
    adminKey: ''
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const navigate = useNavigate();

  const handleChange = (event) => {
    const { name, value } = event.target;
    setFormData((prev) => ({ ...prev, [name]: value }));
  };

  const handleSubmit = async (event) => {
    event.preventDefault();
    setError('');
    setLoading(true);

    try {
      await adminLogin(formData);
      navigate('/admin/dashboard', { replace: true });
    } catch (err) {
      setError(err.response?.data?.message || 'Admin login failed');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="admin-shell admin-login-wrap">
      <div className="admin-login-card">
        <section className="admin-login-hero">
          <div>
            <div className="admin-kicker">Owner Workspace</div>
            <h1>Elevate Control Room</h1>
            <p>
              Secure operations portal for owner-level administration across users,
              content, configuration, and system health.
            </p>
          </div>
          <ul className="admin-login-list">
            <li>Dedicated admin token with separate secret.</li>
            <li>Audit trail for privileged actions.</li>
            <li>Single owner enforced at database index level.</li>
          </ul>
        </section>

        <section className="admin-login-form">
          <div className="admin-card-title">
            <h2>Admin Sign In</h2>
            <p>Use owner email, password, and admin key.</p>
          </div>

          {error ? <div className="admin-alert">{error}</div> : null}

          <form onSubmit={handleSubmit}>
            <div className="admin-field">
              <label htmlFor="admin-email">Email</label>
              <input
                id="admin-email"
                name="email"
                type="email"
                className="admin-input"
                value={formData.email}
                onChange={handleChange}
                required
              />
            </div>

            <div className="admin-field">
              <label htmlFor="admin-password">Password</label>
              <input
                id="admin-password"
                name="password"
                type="password"
                className="admin-input"
                value={formData.password}
                onChange={handleChange}
                required
              />
            </div>

            <div className="admin-field">
              <label htmlFor="admin-key">Admin Key</label>
              <input
                id="admin-key"
                name="adminKey"
                type="password"
                className="admin-input"
                value={formData.adminKey}
                onChange={handleChange}
                required
              />
            </div>

            <button className="admin-btn" type="submit" disabled={loading}>
              {loading ? 'Authenticating...' : 'Access Admin Panel'}
            </button>
          </form>
        </section>
      </div>
    </div>
  );
}
