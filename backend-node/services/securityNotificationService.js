const axios = require('axios');
const nodemailer = require('nodemailer');

const parseBoolean = (value, fallback = false) => {
  if (typeof value === 'boolean') return value;
  if (typeof value !== 'string') return fallback;

  const normalized = value.trim().toLowerCase();
  if (['1', 'true', 'yes', 'on'].includes(normalized)) return true;
  if (['0', 'false', 'no', 'off'].includes(normalized)) return false;
  return fallback;
};

const splitCsv = (value) =>
  String(value || '')
    .split(',')
    .map((item) => item.trim())
    .filter(Boolean);

let transporterCache;

const getTransporter = () => {
  if (transporterCache !== undefined) {
    return transporterCache;
  }

  const host = process.env.SMTP_HOST;
  const user = process.env.SMTP_USER;
  const pass = process.env.SMTP_PASS;
  const port = parseInt(process.env.SMTP_PORT || '587', 10);

  if (!host || !user || !pass || Number.isNaN(port)) {
    transporterCache = null;
    return transporterCache;
  }

  transporterCache = nodemailer.createTransport({
    host,
    port,
    secure: parseBoolean(process.env.SMTP_SECURE, false),
    auth: {
      user,
      pass
    }
  });

  return transporterCache;
};

const sendWebhook = async (url, payload) => {
  if (!url) return false;
  await axios.post(url, payload, { timeout: 8000 });
  return true;
};

const sendEmail = async ({ to, subject, text }) => {
  const transporter = getTransporter();
  if (!transporter) return false;

  const from = process.env.SMTP_FROM || process.env.SMTP_USER;
  if (!from) return false;

  await transporter.sendMail({ from, to, subject, text });
  return true;
};

const sendSecurityAlert = async (eventType, details = {}) => {
  const payload = {
    eventType,
    timestamp: new Date().toISOString(),
    details
  };

  let delivered = false;
  const errors = [];

  if (process.env.SECURITY_ALERT_WEBHOOK_URL) {
    try {
      const webhookOk = await sendWebhook(process.env.SECURITY_ALERT_WEBHOOK_URL, payload);
      delivered = delivered || webhookOk;
    } catch (error) {
      errors.push(`webhook: ${error.message}`);
    }
  }

  const alertRecipients = splitCsv(process.env.SECURITY_ALERT_EMAIL);
  if (alertRecipients.length > 0) {
    try {
      const emailOk = await sendEmail({
        to: alertRecipients.join(','),
        subject: `[Elevate Security] ${eventType}`,
        text: `${eventType}\n\n${JSON.stringify(payload, null, 2)}`
      });
      delivered = delivered || emailOk;
    } catch (error) {
      errors.push(`email: ${error.message}`);
    }
  }

  if (!delivered && errors.length > 0) {
    throw new Error(errors.join(' | '));
  }

  return {
    delivered,
    channelsConfigured:
      Boolean(process.env.SECURITY_ALERT_WEBHOOK_URL) || alertRecipients.length > 0
  };
};

/**
 * SEC-3 fix: Build a signed reset URL instead of sending the raw token.
 *
 * The URL carries the token as a query parameter over HTTPS, which is far
 * safer than pasting the bare token into an email body where it may be:
 *   - logged by email servers
 *   - visible in email-client previews
 *   - captured by security scanners in the email pipeline
 *
 * Set FRONTEND_URL in the Node backend's .env (e.g. https://app.example.com).
 *
 * @param {string} resetToken - The raw (un-hashed) 32-byte hex token
 * @param {string} email      - The user's email address
 * @returns {string}          - Absolute reset URL
 */
const buildResetLink = (resetToken, email) => {
  const base =
    (process.env.FRONTEND_URL || '').replace(/\/$/, '') ||
    (process.env.NODE_ENV === 'production'
      ? 'https://your-app.example.com'  // MUST be overridden via FRONTEND_URL in production
      : 'http://localhost:5173');

  const params = new URLSearchParams({ token: resetToken, email });
  return `${base}/reset-password?${params.toString()}`;
};

const sendPasswordResetToken = async ({
  userEmail,
  userName,
  resetToken,
  expiresInMinutes,
  requestedBy
}) => {
  if (!userEmail || !resetToken) {
    throw new Error('Reset token delivery payload is incomplete');
  }

  // SEC-3: Build a full link — never put the raw token directly in any payload.
  const resetLink = buildResetLink(resetToken, userEmail);

  // Webhook: send the reset link, not the raw token.
  const webhookPayload = {
    userEmail,
    userName: userName || 'User',
    resetLink,            // SEC-3: link only, no raw token
    expiresInMinutes,
    requestedAt: new Date().toISOString(),
    requestedBy: {
      id: requestedBy?.id,
      email: requestedBy?.email,
      name: requestedBy?.name
    }
  };

  const isAdminInitiated = Boolean(requestedBy?.id);
  const introLine = isAdminInitiated
    ? 'An administrator has initiated a password reset for your Elevate account.'
    : 'You requested a password reset for your Elevate account.';

  let delivered = false;
  const channels = [];
  const errors = [];

  if (process.env.PASSWORD_RESET_WEBHOOK_URL) {
    try {
      const webhookOk = await sendWebhook(process.env.PASSWORD_RESET_WEBHOOK_URL, webhookPayload);
      if (webhookOk) {
        delivered = true;
        channels.push('webhook');
      }
    } catch (error) {
      errors.push(`webhook: ${error.message}`);
    }
  }

  try {
    const emailOk = await sendEmail({
      to: userEmail,
      subject: 'Elevate — reset your password',
      // SEC-3: Send a click-to-reset link, never the bare token.
      text: [
        `Hi ${userName || 'there'},`,
        '',
        introLine,
        '',
        'Click the link below to reset your password:',
        resetLink,
        '',
        `This link expires in ${expiresInMinutes} minutes.`,
        '',
        'If you cannot click the link, copy and paste it into your browser.',
        '',
        'If you did not request this action, contact support immediately.',
        '',
        '— The Elevate Team'
      ].join('\n')
    });

    if (emailOk) {
      delivered = true;
      channels.push('email');
    }
  } catch (error) {
    errors.push(`email: ${error.message}`);
  }

  if (!delivered) {
    const reason = errors.length
      ? errors.join(' | ')
      : 'No secure reset delivery channel is configured';
    throw new Error(reason);
  }

  return { delivered: true, channels };
};

module.exports = {
  sendSecurityAlert,
  sendPasswordResetToken
};