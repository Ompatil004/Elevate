import React, { useEffect } from 'react';

const ConfirmDialog = ({ show, message, onConfirm, onCancel }) => {
  useEffect(() => {
    if (show) {
      // Lock background scroll
      document.body.style.overflow = 'hidden';
    } else {
      // Unlock background scroll
      document.body.style.overflow = '';
    }

    // Cleanup function
    return () => {
      document.body.style.overflow = '';
    };
  }, [show]);

  if (!show) return null;

  return (
    <div className="confirm-modal-backdrop" onClick={onCancel}>
      <div className="confirm-modal-card" onClick={(e) => e.stopPropagation()}>
        <div style={{fontSize:'40px', marginBottom:'15px'}}>❓</div>
        <div className="confirm-modal-title">Confirm Action</div>
        <div className="confirm-modal-text">
          {message}
        </div>
        <div className="confirm-modal-btn-row">
          <button className="confirm-modal-btn-cancel" onClick={onCancel}>Cancel</button>
          <button className="confirm-modal-btn-confirm" onClick={onConfirm}>Confirm</button>
        </div>
      </div>
    </div>
  );
};

export default ConfirmDialog;