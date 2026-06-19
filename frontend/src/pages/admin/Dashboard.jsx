import { useEffect, useMemo, useState } from 'react';
import { adminGetHealth, adminGetUserStats } from '../../api';

const safeNumber = (value) => {
  const parsed = Number(value);
  return Number.isFinite(parsed) ? parsed : 0;
};

export default function AdminDashboard() {
  const [stats, setStats] = useState(null);
  const [health, setHealth] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  const fetchDashboardData = async () => {
    setLoading(true);
    setError('');

    try {
      const [statsRes, healthRes] = await Promise.all([
        adminGetUserStats(),
        adminGetHealth()
      ]);

      setStats(statsRes.data);
      setHealth(healthRes.data);
    } catch (err) {
      setError(err.response?.data?.message || 'Failed to load dashboard data');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchDashboardData();
  }, []);

  const goalDistribution = useMemo(() => {
    return Array.isArray(stats?.usersByGoal) ? stats.usersByGoal : [];
  }, [stats]);

  if (loading) {
    return <div className="admin-card">Loading dashboard...</div>;
  }

  return (
    <section>
      <div className="admin-page-head">
        <div>
          <h2>Dashboard Overview</h2>
          <p>Real-time owner insights into platform health and user activity.</p>
        </div>
        <button className="admin-btn secondary" type="button" onClick={fetchDashboardData}>
          Refresh
        </button>
      </div>

      {error ? <div className="admin-alert">{error}</div> : null}

      <div className="admin-grid cards-4" style={{ marginBottom: '14px' }}>
        <StatCard label="Total Users" value={safeNumber(stats?.totalUsers)} />
        <StatCard label="New This Week" value={safeNumber(stats?.newUsersThisWeek)} />
        <StatCard label="New This Month" value={safeNumber(stats?.newUsersThisMonth)} />
        <StatCard
          label="Suspended"
          value={safeNumber(stats?.suspendedUsers)}
          danger={safeNumber(stats?.suspendedUsers) > 0}
        />
      </div>

      <div className="admin-grid cards-3" style={{ marginBottom: '14px' }}>
        <HealthCard title="Overall" status={health?.overall} />
        <HealthCard title="Database" status={health?.services?.database?.status} />
        <HealthCard title="Node Backend" status={health?.services?.nodeBackend?.status} />
      </div>

      <div className="admin-card">
        <h3 style={{ marginTop: 0, marginBottom: '10px' }}>Goal Distribution</h3>
        {goalDistribution.length === 0 ? (
          <div className="admin-empty">No goal distribution data yet.</div>
        ) : (
          <div className="admin-grid" style={{ gap: '8px' }}>
            {goalDistribution.map((goal) => {
              const total = Math.max(safeNumber(stats?.totalUsers), 1);
              const width = Math.min((safeNumber(goal.count) / total) * 100, 100);
              return (
                <div key={String(goal._id)}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '4px' }}>
                    <span>{goal._id || 'Not Set'}</span>
                    <span>{safeNumber(goal.count)}</span>
                  </div>
                  <div style={{ height: '10px', borderRadius: '999px', background: 'rgba(170, 177, 195, 0.22)' }}>
                    <div
                      style={{
                        width: `${width}%`,
                        height: '100%',
                        borderRadius: '999px',
                        background: 'linear-gradient(120deg, #2dd4bf, #14b8a6)'
                      }}
                    />
                  </div>
                </div>
              );
            })}
          </div>
        )}
      </div>
    </section>
  );
}

function StatCard({ label, value, danger = false }) {
  return (
    <div className="admin-card">
      <div className="admin-stat-label">{label}</div>
      <div className="admin-stat-value" style={{ color: danger ? '#fca5a5' : undefined }}>
        {value}
      </div>
    </div>
  );
}

function HealthCard({ title, status }) {
  const normalized = String(status || 'unknown').toLowerCase();
  const cls = normalized === 'healthy' ? 'ok' : normalized === 'degraded' ? 'warn' : 'danger';

  return (
    <div className="admin-card">
      <div className="admin-stat-label">{title}</div>
      <span className={`admin-status ${cls}`}>{normalized.toUpperCase()}</span>
    </div>
  );
}
