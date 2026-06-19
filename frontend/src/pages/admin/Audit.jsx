import { useEffect, useMemo, useState } from 'react';
import { adminGetAuditLogs } from '../../api';

const ACTION_OPTIONS = [
  'LOGIN',
  'LOGOUT',
  'ADMIN_LOGIN_FAILED',
  'SECURITY_LOCKOUT',
  'USER_LIST',
  'USER_VIEW',
  'USER_SUSPEND',
  'USER_ACTIVATE',
  'USER_DELETE',
  'USER_PASSWORD_RESET',
  'CONFIG_UPDATE',
  'EXERCISE_ADD',
  'EXERCISE_EDIT',
  'EXERCISE_DELETE',
  'MAINTENANCE_TOGGLE',
  'ANNOUNCEMENT_CREATE',
  'ANNOUNCEMENT_DELETE',
  'SYSTEM_HEALTH_CHECK'
];

export default function AdminAudit() {
  const [logs, setLogs] = useState([]);
  const [pagination, setPagination] = useState({ page: 1, pages: 1, total: 0, limit: 50 });
  const [actionFilter, setActionFilter] = useState('');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  const params = useMemo(() => {
    const base = {
      page: pagination.page,
      limit: pagination.limit
    };

    if (actionFilter) {
      base.action = actionFilter;
    }

    return base;
  }, [pagination.page, pagination.limit, actionFilter]);

  const fetchLogs = async () => {
    setLoading(true);
    setError('');

    try {
      const response = await adminGetAuditLogs(params);
      setLogs(response.data?.logs || []);
      setPagination((prev) => ({
        ...prev,
        ...(response.data?.pagination || {})
      }));
    } catch (err) {
      setError(err.response?.data?.message || 'Failed to load audit logs');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchLogs();
  }, [params]);

  const setPage = (nextPage) => {
    setPagination((prev) => ({
      ...prev,
      page: Math.max(1, Math.min(nextPage, prev.pages || 1))
    }));
  };

  return (
    <section>
      <div className="admin-page-head">
        <div>
          <h2>Audit Logs</h2>
          <p>Immutable activity history for owner actions and privileged operations.</p>
        </div>
      </div>

      {error ? <div className="admin-alert">{error}</div> : null}

      <div className="admin-toolbar">
        <select
          className="admin-select"
          value={actionFilter}
          onChange={(event) => {
            setActionFilter(event.target.value);
            setPagination((prev) => ({ ...prev, page: 1 }));
          }}
          style={{ width: '280px' }}
        >
          <option value="">All actions</option>
          {ACTION_OPTIONS.map((action) => (
            <option key={action} value={action}>
              {action}
            </option>
          ))}
        </select>

        <button className="admin-btn secondary" type="button" onClick={fetchLogs}>
          Refresh
        </button>
      </div>

      {loading ? (
        <div className="admin-card">Loading audit logs...</div>
      ) : (
        <div className="admin-table-wrap">
          <table className="admin-table">
            <thead>
              <tr>
                <th>Timestamp</th>
                <th>Action</th>
                <th>Owner</th>
                <th>Target</th>
                <th>Details</th>
              </tr>
            </thead>
            <tbody>
              {logs.length === 0 ? (
                <tr>
                  <td colSpan={5}>
                    <div className="admin-empty">No audit entries found.</div>
                  </td>
                </tr>
              ) : (
                logs.map((log) => (
                  <tr key={log._id}>
                    <td>{log.timestamp ? new Date(log.timestamp).toLocaleString() : '-'}</td>
                    <td>{log.action}</td>
                    <td>
                      <strong>{log.ownerId?.name || 'Unknown'}</strong>
                      <div className="admin-note">{log.ownerId?.email || '-'}</div>
                    </td>
                    <td>
                      <div>{log.targetType || '-'}</div>
                      <div className="admin-note">{log.targetId || '-'}</div>
                    </td>
                    <td>
                      <pre
                        style={{
                          margin: 0,
                          whiteSpace: 'pre-wrap',
                          wordBreak: 'break-word',
                          fontSize: '0.72rem'
                        }}
                      >
                        {JSON.stringify(log.details || {}, null, 2)}
                      </pre>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      )}

      <div className="admin-toolbar" style={{ marginTop: '12px' }}>
        <button className="admin-btn secondary" onClick={() => setPage((pagination.page || 1) - 1)}>
          Previous
        </button>
        <div className="admin-note" style={{ alignSelf: 'center' }}>
          Page {pagination.page || 1} of {pagination.pages || 1}
        </div>
        <button className="admin-btn secondary" onClick={() => setPage((pagination.page || 1) + 1)}>
          Next
        </button>
      </div>
    </section>
  );
}
