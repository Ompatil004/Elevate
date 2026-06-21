import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { confirmPasswordReset, requestPasswordReset } from '../api';
import '../App.css';

function ForgotPassword() {
  const navigate = useNavigate();

  const [step, setStep] = useState('request');
  const [requestEmail, setRequestEmail] = useState('');
  const [accountEmail, setAccountEmail] = useState('');
  const [requestLoading, setRequestLoading] = useState(false);
  const [requestError, setRequestError] = useState('');
  const [requestMessage, setRequestMessage] = useState('');
  const [devResetToken, setDevResetToken] = useState('');

  const [confirmData, setConfirmData] = useState({
    resetToken: '',
    newPassword: '',
    confirmPassword: ''
  });
  const [confirmLoading, setConfirmLoading] = useState(false);
  const [confirmError, setConfirmError] = useState('');
  const [confirmMessage, setConfirmMessage] = useState('');
  const [showPasswords, setShowPasswords] = useState(false);

  const handleRequest = async (event) => {
    event.preventDefault();
    const normalizedEmail = requestEmail.trim();

    if (!normalizedEmail) {
      setRequestError('Email is required');
      return;
    }

    setRequestError('');
    setRequestMessage('');
    setDevResetToken('');
    setConfirmError('');
    setConfirmMessage('');
    setRequestLoading(true);

    try {
      const response = await requestPasswordReset({ email: normalizedEmail });
      const message = response.data?.message || 'Reset instructions sent if the account exists.';
      setRequestMessage(message);
      setAccountEmail(normalizedEmail);
      setStep('confirm');

      const returnedToken = response.data?.resetToken || '';
      if (returnedToken) {
        setDevResetToken(returnedToken);
        setConfirmData((prev) => ({
          ...prev,
          resetToken: returnedToken
        }));
      } else {
        setConfirmData((prev) => ({
          ...prev,
          resetToken: ''
        }));
      }
    } catch (error) {
      setRequestError(error.response?.data?.message || 'Failed to process reset request');
    } finally {
      setRequestLoading(false);
    }
  };

  const handleConfirmChange = (event) => {
    const { name, value } = event.target;
    setConfirmData((prev) => ({ ...prev, [name]: value }));
  };

  const handleConfirm = async (event) => {
    event.preventDefault();
    setConfirmError('');
    setConfirmMessage('');

    const email = accountEmail.trim();
    const resetToken = confirmData.resetToken.trim();
    const newPassword = confirmData.newPassword;
    const confirmPassword = confirmData.confirmPassword;

    if (!email) {
      setConfirmError('Please request a reset token first');
      setStep('request');
      return;
    }

    if (!email || !resetToken || !newPassword || !confirmPassword) {
      setConfirmError('All fields are required');
      return;
    }

    if (newPassword.length < 8) {
      setConfirmError('New password must be at least 8 characters long');
      return;
    }

    if (newPassword !== confirmPassword) {
      setConfirmError('Passwords do not match');
      return;
    }

    setConfirmLoading(true);
    try {
      await confirmPasswordReset({ email, resetToken, newPassword });
      setConfirmMessage('Password reset successful. Redirecting to login...');
      setTimeout(() => {
        navigate('/login', { replace: true });
      }, 1400);
    } catch (error) {
      setConfirmError(error.response?.data?.message || 'Failed to reset password');
    } finally {
      setConfirmLoading(false);
    }
  };

  const handleUseDifferentEmail = () => {
    setStep('request');
    setRequestMessage('');
    setRequestError('');
    setConfirmError('');
    setConfirmMessage('');
    setDevResetToken('');
    setConfirmData({
      resetToken: '',
      newPassword: '',
      confirmPassword: ''
    });
  };

  return (
    <div className="login-container dark-theme">
      <div className="fitness-bg-element">🔒</div>
      <div className="fitness-bg-element">📩</div>
      <div className="fitness-bg-element">🛡️</div>
      <div className="fitness-bg-element">🔑</div>

      <div className="animated-orb orb-1" />
      <div className="animated-orb orb-2" />
      <div className="animated-orb orb-3" />

      <div className="login-card dark-card" style={{ maxWidth: '560px', width: '100%' }}>
        <div
          className="login-right"
          style={{
            padding: 'clamp(18px, 4vw, 42px) clamp(16px, 4vw, 34px)'
          }}
        >
          <div className="right-content">
            <div className="welcome-header" style={{ marginBottom: '24px' }}>
              <h3>Reset Password</h3>
              <p className="login-subtitle">
                {step === 'request'
                  ? 'Step 1 of 2: enter your account email once.'
                  : 'Step 2 of 2: enter your token and set a new password.'}
              </p>
            </div>

            {step === 'request' ? (
              <>
                {requestError ? <div className="alert-custom">{requestError}</div> : null}
                {requestMessage ? (
                  <div
                    className="alert-custom"
                    style={{
                      backgroundColor: 'rgba(34, 197, 94, 0.1)',
                      color: '#4ade80',
                      border: '1px solid rgba(34, 197, 94, 0.2)'
                    }}
                  >
                    {requestMessage}
                  </div>
                ) : null}

                <form onSubmit={handleRequest}>
                  <div className="form-group-custom">
                    <label htmlFor="request-email">
                      <span className="label-icon">📧</span>
                      Account Email
                    </label>
                    <div className="input-wrapper">
                      <input
                        id="request-email"
                        type="email"
                        placeholder="Enter your account email"
                        value={requestEmail}
                        onChange={(event) => setRequestEmail(event.target.value)}
                        required
                      />
                      <div className="input-underline" />
                    </div>
                  </div>

                  <button className="btn-login" type="submit" disabled={requestLoading}>
                    <span className="btn-text">
                      {requestLoading ? 'Sending token...' : 'Send Reset Token'}
                    </span>
                    <span className="btn-icon">→</span>
                  </button>
                </form>
              </>
            ) : (
              <>
                <div
                  className="stat-box"
                  style={{
                    marginBottom: '14px',
                    background: 'rgba(15, 23, 42, 0.08)',
                    border: '1px solid rgba(15, 23, 42, 0.16)',
                    color: '#1f2937'
                  }}
                >
                  Resetting password for: <strong>{accountEmail}</strong>
                </div>

                {devResetToken ? (
                  <div
                    className="stat-box"
                    style={{
                      marginBottom: '14px',
                      background: 'rgba(245, 158, 11, 0.14)',
                      border: '1px solid rgba(245, 158, 11, 0.3)',
                      color: '#92400e',
                      wordBreak: 'break-all'
                    }}
                  >
                    Development token: {devResetToken}
                  </div>
                ) : null}

                {confirmError ? <div className="alert-custom">{confirmError}</div> : null}
                {confirmMessage ? (
                  <div
                    className="alert-custom"
                    style={{
                      backgroundColor: 'rgba(34, 197, 94, 0.1)',
                      color: '#4ade80',
                      border: '1px solid rgba(34, 197, 94, 0.2)'
                    }}
                  >
                    {confirmMessage}
                  </div>
                ) : null}

                <form onSubmit={handleConfirm}>
                  <div className="form-group-custom">
                    <label htmlFor="reset-token">
                      <span className="label-icon">🎟️</span>
                      Reset Token
                    </label>
                    <div className="input-wrapper">
                      <input
                        id="reset-token"
                        name="resetToken"
                        type="text"
                        placeholder="Paste the token sent to your email"
                        value={confirmData.resetToken}
                        onChange={handleConfirmChange}
                        required
                      />
                      <div className="input-underline" />
                    </div>
                  </div>

                  <div className="form-group-custom">
                    <label htmlFor="new-password">
                      <span className="label-icon">🔑</span>
                      New Password
                    </label>
                    <div className="input-wrapper">
                      <input
                        id="new-password"
                        name="newPassword"
                        type={showPasswords ? 'text' : 'password'}
                        value={confirmData.newPassword}
                        onChange={handleConfirmChange}
                        required
                      />
                      <div className="input-underline" />
                    </div>
                  </div>

                  <div className="form-group-custom">
                    <label htmlFor="confirm-password">
                      <span className="label-icon">🔐</span>
                      Confirm New Password
                    </label>
                    <div className="input-wrapper">
                      <input
                        id="confirm-password"
                        name="confirmPassword"
                        type={showPasswords ? 'text' : 'password'}
                        value={confirmData.confirmPassword}
                        onChange={handleConfirmChange}
                        required
                      />
                      <button
                        type="button"
                        onClick={() => setShowPasswords((prev) => !prev)}
                        className="password-toggle"
                      >
                        {showPasswords ? '👁️' : '👁️‍🗨️'}
                      </button>
                      <div className="input-underline" />
                    </div>
                  </div>

                  <button className="btn-login" type="submit" disabled={confirmLoading}>
                    <span className="btn-text">
                      {confirmLoading ? 'Updating password...' : 'Reset Password'}
                    </span>
                    <span className="btn-icon">→</span>
                  </button>
                </form>

                <button
                  type="button"
                  className="social-btn"
                  style={{ marginTop: '12px' }}
                  onClick={handleUseDifferentEmail}
                >
                  Use a different email
                </button>
              </>
            )}

            <div className="login-footer" style={{ marginTop: '16px' }}>
              <small>
                Remembered your password? <Link to="/login" className="signup-link">Back to sign in</Link>
              </small>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

export default ForgotPassword;