import { useEffect, useMemo, useState } from 'react';
import {
  adminCreateAnnouncement,
  adminDeleteAnnouncement,
  adminGetAnnouncements,
  adminGetHealth,
  adminGetMaintenance,
  adminGetSystemStats,
  adminSetMaintenance
} from '../../api';
import AdminActionDialog from '../../components/admin/AdminActionDialog';

const EMPTY_ANNOUNCEMENT = {
  title: '',
  message: '',
  type: 'info'
};

export default function AdminSystem() {
  const [health, setHealth] = useState(null);
  const [stats, setStats] = useState(null);
  const [maintenance, setMaintenance] = useState({ enabled: false, message: '' });
  const [announcements, setAnnouncements] = useState([]);
  const [deleteDialog, setDeleteDialog] = useState({ show: false, announcementId: '', title: '' });
  const [announcementForm, setAnnouncementForm] = useState(EMPTY_ANNOUNCEMENT);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  const totalFromGoalDistribution = useMemo(() => {
    const distribution = stats?.goalDistribution;
    if (!Array.isArray(distribution)) return 0;
    return distribution.reduce((sum, item) => sum + (Number(item?.count) || 0), 0);
  }, [stats]);

  const fetchSystemData = async () => {
    setLoading(true);
    setError('');

    try {
      const [healthRes, statsRes, maintenanceRes, announcementsRes] = await Promise.all([
        adminGetHealth(),
        adminGetSystemStats(),
        adminGetMaintenance(),
        adminGetAnnouncements()
      ]);

      setHealth(healthRes.data || null);
      setStats(statsRes.data || null);
      setMaintenance({
        enabled: Boolean(maintenanceRes.data?.enabled),
        message: maintenanceRes.data?.message || 'System is under maintenance. Please try again later.'
      });
      setAnnouncements(announcementsRes.data?.announcements || []);
    } catch (err) {
      setError(err.response?.data?.message || 'Failed to load system data');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchSystemData();
  }, []);

  const handleMaintenanceSubmit = async (event) => {
    event.preventDefault();
    setError('');

    try {
      await adminSetMaintenance(maintenance);
      await fetchSystemData();
    } catch (err) {
      setError(err.response?.data?.message || 'Failed to update maintenance mode');
    }
  };

  const handleCreateAnnouncement = async (event) => {
    event.preventDefault();
    setError('');

    try {
      await adminCreateAnnouncement(announcementForm);
      setAnnouncementForm(EMPTY_ANNOUNCEMENT);
      await fetchSystemData();
    } catch (err) {
      setError(err.response?.data?.message || 'Failed to create announcement');
    }
  };

  const handleDeleteAnnouncement = async (announcementId) => {
    const target = announcements.find((item) => item.id === announcementId);
    setDeleteDialog({
      show: true,
      announcementId,
      title: target?.title || 'this announcement',
    });
  };

  const confirmDeleteAnnouncement = async () => {
    const announcementId = deleteDialog.announcementId;
    setDeleteDialog({ show: false, announcementId: '', title: '' });
    if (!announcementId) return;

    setError('');
    try {
      await adminDeleteAnnouncement(announcementId);
      await fetchSystemData();
    } catch (err) {
      setError(err.response?.data?.message || 'Failed to delete announcement');
    }
  };

  return (
    <section>
      <div className="admin-page-head">
        <div>
          <h2>System Management</h2>
          <p>Health, maintenance controls, statistics, and announcements.</p>
        </div>
        <button className="admin-btn secondary" type="button" onClick={fetchSystemData}>
          Refresh
        </button>
      </div>

      {error ? <div className="admin-alert">{error}</div> : null}

      {loading ? (
        <div className="admin-card">Loading system data...</div>
      ) : (
        <>
          <div className="admin-grid cards-3" style={{ marginBottom: '14px' }}>
            <InfoCard title="Overall Health" value={String(health?.overall || 'unknown').toUpperCase()} />
            <InfoCard title="Estimated Users" value={String(totalFromGoalDistribution)} />
            <InfoCard title="Recent Growth Points" value={String(stats?.userGrowth?.length || 0)} />
          </div>

          <div className="admin-card" style={{ marginBottom: '14px' }}>
            <h3 style={{ marginTop: 0 }}>Maintenance Mode</h3>
            <form className="admin-inline-form" onSubmit={handleMaintenanceSubmit}>
              <label className="admin-note">
                <input
                  type="checkbox"
                  checked={maintenance.enabled}
                  onChange={(event) =>
                    setMaintenance((prev) => ({ ...prev, enabled: event.target.checked }))
                  }
                  style={{ marginRight: '8px' }}
                />
                Enable maintenance mode
              </label>
              <textarea
                className="admin-textarea"
                value={maintenance.message}
                onChange={(event) =>
                  setMaintenance((prev) => ({ ...prev, message: event.target.value }))
                }
              />
              <button className="admin-btn" type="submit">Save Maintenance Settings</button>
            </form>
          </div>

          <div className="admin-grid cards-3" style={{ marginBottom: '14px' }}>
            <div className="admin-card" style={{ gridColumn: 'span 2' }}>
              <h3 style={{ marginTop: 0 }}>Create Announcement</h3>
              <form className="admin-inline-form" onSubmit={handleCreateAnnouncement}>
                <input
                  className="admin-input"
                  placeholder="Announcement title"
                  value={announcementForm.title}
                  onChange={(event) =>
                    setAnnouncementForm((prev) => ({ ...prev, title: event.target.value }))
                  }
                  required
                />
                <textarea
                  className="admin-textarea"
                  placeholder="Announcement message"
                  value={announcementForm.message}
                  onChange={(event) =>
                    setAnnouncementForm((prev) => ({ ...prev, message: event.target.value }))
                  }
                  required
                />
                <select
                  className="admin-select"
                  value={announcementForm.type}
                  onChange={(event) =>
                    setAnnouncementForm((prev) => ({ ...prev, type: event.target.value }))
                  }
                >
                  <option value="info">Info</option>
                  <option value="warning">Warning</option>
                  <option value="success">Success</option>
                  <option value="error">Error</option>
                </select>
                <button className="admin-btn" type="submit">Publish Announcement</button>
              </form>
            </div>

            <div className="admin-card">
              <h3 style={{ marginTop: 0 }}>Service Snapshot</h3>
              <div className="admin-note">Database: {health?.services?.database?.status || 'unknown'}</div>
              <div className="admin-note">Node: {health?.services?.nodeBackend?.status || 'unknown'}</div>
              <div className="admin-note">
                Uptime: {Math.floor(Number(health?.services?.nodeBackend?.uptime || 0))}s
              </div>
            </div>
          </div>

          <div className="admin-card">
            <h3 style={{ marginTop: 0 }}>Active Announcements</h3>
            {announcements.length === 0 ? (
              <div className="admin-empty">No active announcements.</div>
            ) : (
              <div className="admin-grid" style={{ gap: '10px' }}>
                {announcements.map((item) => (
                  <div key={item.id} className="admin-card" style={{ padding: '12px' }}>
                    <div style={{ display: 'flex', justifyContent: 'space-between', gap: '10px' }}>
                      <div>
                        <strong>{item.title}</strong>
                        <div className="admin-note">{item.type || 'info'}</div>
                      </div>
                      <button className="admin-btn danger" type="button" onClick={() => handleDeleteAnnouncement(item.id)}>
                        Delete
                      </button>
                    </div>
                    <p style={{ marginTop: '8px', marginBottom: 0 }}>{item.message}</p>
                  </div>
                ))}
              </div>
            )}
          </div>
        </>
      )}

      <AdminActionDialog
        show={deleteDialog.show}
        title="Delete announcement"
        message={`Delete ${deleteDialog.title}? This action cannot be undone.`}
        confirmLabel="Delete Announcement"
        requirePhrase="DELETE"
        onCancel={() => setDeleteDialog({ show: false, announcementId: '', title: '' })}
        onConfirm={confirmDeleteAnnouncement}
      />
    </section>
  );
}

function InfoCard({ title, value }) {
  return (
    <div className="admin-card">
      <div className="admin-stat-label">{title}</div>
      <div className="admin-stat-value">{value}</div>
    </div>
  );
}
