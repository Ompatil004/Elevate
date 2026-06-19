import { useEffect, useMemo, useState } from 'react';

const backdropStyle = {
  position: 'fixed',
  inset: 0,
  background: 'rgba(9, 9, 11, 0.72)',
  backdropFilter: 'blur(4px)',
  zIndex: 9999,
  display: 'grid',
  placeItems: 'center',
  padding: '16px',
};

const cardStyle = {
  width: 'min(92vw, 520px)',
  background: '#18181b',
  border: '1px solid rgba(255,255,255,0.12)',
  borderRadius: '16px',
  boxShadow: '0 24px 60px rgba(0,0,0,0.5)',
  padding: '18px',
  color: '#e4e4e7',
};

const labelStyle = {
  display: 'block',
  marginBottom: '6px',
  fontSize: '13px',
  color: '#a1a1aa',
};

const inputStyle = {
  width: '100%',
  borderRadius: '10px',
  border: '1px solid rgba(255,255,255,0.12)',
  background: '#09090b',
  color: '#f4f4f5',
  padding: '10px 12px',
  fontSize: '14px',
};

export default function AdminActionDialog({
  show,
  title,
  message,
  confirmLabel = 'Confirm',
  cancelLabel = 'Cancel',
  requireReason = false,
  reasonLabel = 'Reason',
  requirePhrase = '',
  onConfirm,
  onCancel,
}) {
  const [reason, setReason] = useState('');
  const [phrase, setPhrase] = useState('');

  useEffect(() => {
    if (!show) {
      setReason('');
      setPhrase('');
      return;
    }

    document.body.style.overflow = 'hidden';
    return () => {
      document.body.style.overflow = '';
    };
  }, [show]);

  const canConfirm = useMemo(() => {
    if (requireReason && !reason.trim()) return false;
    if (requirePhrase && phrase.trim().toUpperCase() !== requirePhrase.toUpperCase()) return false;
    return true;
  }, [requireReason, reason, requirePhrase, phrase]);

  if (!show) return null;

  return (
    <div style={backdropStyle} onClick={() => onCancel?.()}>
      <div style={cardStyle} onClick={(e) => e.stopPropagation()}>
        <h3 style={{ margin: '0 0 8px 0' }}>{title || 'Confirm action'}</h3>
        <p style={{ margin: '0 0 14px 0', color: '#a1a1aa', lineHeight: 1.5 }}>{message}</p>

        {requireReason ? (
          <div style={{ marginBottom: '12px' }}>
            <label style={labelStyle}>{reasonLabel}</label>
            <textarea
              value={reason}
              onChange={(e) => setReason(e.target.value)}
              rows={3}
              style={{ ...inputStyle, resize: 'vertical', minHeight: '84px' }}
              placeholder="Enter reason"
            />
          </div>
        ) : null}

        {requirePhrase ? (
          <div style={{ marginBottom: '12px' }}>
            <label style={labelStyle}>Type {requirePhrase} to confirm</label>
            <input
              value={phrase}
              onChange={(e) => setPhrase(e.target.value)}
              style={inputStyle}
              placeholder={requirePhrase}
            />
          </div>
        ) : null}

        <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '10px', marginTop: '8px' }}>
          <button className="admin-btn secondary" type="button" onClick={() => onCancel?.()}>
            {cancelLabel}
          </button>
          <button
            className="admin-btn danger"
            type="button"
            disabled={!canConfirm}
            onClick={() => onConfirm?.({ reason: reason.trim(), phrase: phrase.trim() })}
          >
            {confirmLabel}
          </button>
        </div>
      </div>
    </div>
  );
}
