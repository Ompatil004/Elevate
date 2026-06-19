import { useEffect, useState } from 'react';
import { Navigate, Outlet } from 'react-router-dom';
import { adminVerify } from '../../api';

export default function AdminRoute() {
  const [status, setStatus] = useState('checking');
  const [ownerInfo, setOwnerInfo] = useState(null);

  useEffect(() => {
    let mounted = true;

    const verify = async () => {
      try {
        const response = await adminVerify();
        if (!mounted) return;

        if (response.data?.valid) {
          setOwnerInfo(response.data?.owner || null);
          setStatus('authorized');
          return;
        }
      } catch {
        // Handled below by unauthorized state.
      }

      if (mounted) {
        setStatus('unauthorized');
      }
    };

    verify();
    return () => {
      mounted = false;
    };
  }, []);

  if (status === 'checking') {
    return (
      <div className="admin-shell" style={{ display: 'grid', placeItems: 'center' }}>
        <div className="admin-card">Verifying admin session...</div>
      </div>
    );
  }

  if (status === 'unauthorized') {
    return <Navigate to="/admin/login" replace />;
  }

  return <Outlet context={{ ownerInfo }} />;
}