import { useEffect, useMemo, useState } from 'react';
import {
  adminActivateUser,
  adminDeleteUser,
  adminGetUsers,
  adminResetUserPassword,
  adminSuspendUser
} from '../../api';
import AdminActionDialog from '../../components/admin/AdminActionDialog';

export default function AdminUsers() {
  const [users, setUsers] = useState([]);
  const [pagination, setPagination] = useState({ page: 1, pages: 1, total: 0, limit: 15 });
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [notice, setNotice] = useState('');
  const [search, setSearch] = useState('');
  const [suspendedFilter, setSuspendedFilter] = useState('all');
  const [actionBusyId, setActionBusyId] = useState('');
  const [actionDialog, setActionDialog] = useState({ show: false, type: '', userId: '', userName: '' });

  const queryParams = useMemo(() => {
    const params = {
      page: pagination.page,
      limit: pagination.limit,
      sortBy: 'createdAt',
      sortOrder: 'desc'
    };

    if (search.trim()) params.search = search.trim();
    if (suspendedFilter !== 'all') params.isSuspended = suspendedFilter;

    return params;
  }, [pagination.page, pagination.limit, search, suspendedFilter]);

  const fetchUsers = async () => {
    setLoading(true);
    setError('');
    setNotice('');

    try {
      const response = await adminGetUsers(queryParams);
      setUsers(response.data?.users || []);
      setPagination((prev) => ({
        ...prev,
        ...(response.data?.pagination || {})
      }));
    } catch (err) {
      setError(err.response?.data?.message || 'Failed to load users');
    } finally {
      setLoading(false);
      setActionBusyId('');
    }
  };

  useEffect(() => {
    fetchUsers();
  }, [queryParams]);

  const runAction = async (userId, actionFn) => {
    setActionBusyId(userId);
    setError('');
    setNotice('');

    try {
      await actionFn();
      await fetchUsers();
    } catch (err) {
      setError(err.response?.data?.message || 'Action failed');
      setActionBusyId('');
    }
  };

  const handleSuspend = (userId) => {
    const user = users.find((item) => item._id === userId);
    setActionDialog({ show: true, type: 'suspend', userId, userName: user?.email || 'this user' });
  };

  const handleActivate = (userId) => {
    runAction(userId, () => adminActivateUser(userId));
  };

  const handleResetPassword = (userId) => {
    runAction(userId, async () => {
      const response = await adminResetUserPassword(userId);
      setNotice(response.data?.message || 'Password reset initiated and delivered securely.');
    });
  };

  const handleDelete = (userId) => {
    const user = users.find((item) => item._id === userId);
    setActionDialog({ show: true, type: 'delete', userId, userName: user?.email || 'this user' });
  };

  const confirmActionDialog = async ({ reason }) => {
    const { type, userId } = actionDialog;
    setActionDialog({ show: false, type: '', userId: '', userName: '' });

    if (!userId) return;
    if (type === 'suspend') {
      await runAction(userId, () => adminSuspendUser(userId, reason || 'Administrative action'));
      return;
    }
    if (type === 'delete') {
      await runAction(userId, () => adminDeleteUser(userId));
    }
  };

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
          <h2>User Management</h2>
          <p>Search, suspend, reactivate, reset password, and remove users.</p>
        </div>
      </div>

      {error ? <div className="admin-alert">{error}</div> : null}
      {notice ? <div className="admin-alert" style={{ background: 'rgba(34,197,94,0.12)', borderColor: 'rgba(34,197,94,0.35)', color: '#86efac' }}>{notice}</div> : null}

      <div className="admin-toolbar">
        <input
          className="admin-input"
          placeholder="Search name or email"
          value={search}
          onChange={(event) => {
            setSearch(event.target.value);
            setPagination((prev) => ({ ...prev, page: 1 }));
          }}
          style={{ maxWidth: '320px' }}
        />

        <select
          className="admin-select"
          value={suspendedFilter}
          onChange={(event) => {
            setSuspendedFilter(event.target.value);
            setPagination((prev) => ({ ...prev, page: 1 }));
          }}
          style={{ width: '180px' }}
        >
          <option value="all">All Users</option>
          <option value="true">Suspended</option>
          <option value="false">Active</option>
        </select>

        <button className="admin-btn secondary" type="button" onClick={fetchUsers}>
          Refresh
        </button>
      </div>

      <div className="admin-note" style={{ marginBottom: '8px' }}>
        Total users: {pagination.total || 0}
      </div>

      {loading ? (
        <div className="admin-card">Loading users...</div>
      ) : (
        <div className="admin-table-wrap">
          <table className="admin-table">
            <thead>
              <tr>
                <th>User</th>
                <th>Role</th>
                <th>Goal</th>
                <th>Status</th>
                <th>Created</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              {users.length === 0 ? (
                <tr>
                  <td colSpan={6}>
                    <div className="admin-empty">No users found.</div>
                  </td>
                </tr>
              ) : (
                users.map((user) => {
                  const busy = actionBusyId === user._id;
                  return (
                    <tr key={user._id}>
                      <td>
                        <strong>{user.name || 'Unknown'}</strong>
                        <div className="admin-note">{user.email}</div>
                      </td>
                      <td>{user.role || 'user'}</td>
                      <td>{user.goal || '-'}</td>
                      <td>
                        {user.isSuspended ? (
                          <span className="admin-status danger">Suspended</span>
                        ) : (
                          <span className="admin-status ok">Active</span>
                        )}
                      </td>
                      <td>{user.createdAt ? new Date(user.createdAt).toLocaleDateString() : '-'}</td>
                      <td>
                        <div className="admin-actions">
                          {user.role !== 'owner' && !user.isSuspended ? (
                            <button className="admin-btn secondary" disabled={busy} onClick={() => handleSuspend(user._id)}>
                              Suspend
                            </button>
                          ) : null}

                          {user.role !== 'owner' && user.isSuspended ? (
                            <button className="admin-btn secondary" disabled={busy} onClick={() => handleActivate(user._id)}>
                              Activate
                            </button>
                          ) : null}

                          {user.role !== 'owner' ? (
                            <button className="admin-btn secondary" disabled={busy} onClick={() => handleResetPassword(user._id)}>
                              Reset Pass
                            </button>
                          ) : null}

                          {user.role !== 'owner' ? (
                            <button className="admin-btn danger" disabled={busy} onClick={() => handleDelete(user._id)}>
                              Delete
                            </button>
                          ) : null}
                        </div>
                      </td>
                    </tr>
                  );
                })
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

      <AdminActionDialog
        show={actionDialog.show}
        title={actionDialog.type === 'delete' ? 'Delete user account' : 'Suspend user account'}
        message={
          actionDialog.type === 'delete'
            ? `Delete ${actionDialog.userName} permanently? This action cannot be undone.`
            : `Suspend ${actionDialog.userName}. A reason is required and will be logged.`
        }
        confirmLabel={actionDialog.type === 'delete' ? 'Delete User' : 'Suspend User'}
        requireReason={actionDialog.type === 'suspend'}
        reasonLabel="Suspension reason"
        requirePhrase={actionDialog.type === 'delete' ? 'DELETE' : ''}
        onCancel={() => setActionDialog({ show: false, type: '', userId: '', userName: '' })}
        onConfirm={confirmActionDialog}
      />
    </section>
  );
}
