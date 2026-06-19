const jwt = require('jsonwebtoken');
const User = require('../models/User');
const AdminAuditLog = require('../models/AdminAuditLog');

const SENSITIVE_KEYS = new Set([
  'password',
  'newPassword',
  'oldPassword',
  'adminKey',
  'token',
  'tempPassword',
  'passwordResetToken',
  'passwordResetTokenHash',
  'passwordResetTokenExpiresAt'
]);

const normalizeKey = (key) =>
  String(key || '')
    .toLowerCase()
    .replace(/[^a-z0-9]/g, '');

const isSensitiveKey = (key) => {
  const normalized = normalizeKey(key);
  if (!normalized) return false;

  const exactMatch = Array.from(SENSITIVE_KEYS).some(
    (candidate) => normalizeKey(candidate) === normalized
  );

  if (exactMatch) return true;

  return (
    normalized.includes('password') ||
    normalized.includes('adminkey') ||
    normalized.includes('resettoken') ||
    normalized === 'token' ||
    normalized === 'authorization'
  );
};

const redactSensitive = (payload) => {
  if (!payload) return payload;

  try {
    return JSON.parse(
      JSON.stringify(payload, (key, value) => {
        if (isSensitiveKey(key)) {
          return '[REDACTED]';
        }
        return value;
      })
    );
  } catch {
    return { note: 'Unable to serialize payload safely' };
  }
};

const normalizeIp = (rawIp = '') =>
  String(rawIp)
    .trim()
    .replace('::ffff:', '')
    .replace('::1', '127.0.0.1');

// SEC-5 fix: only trust x-forwarded-for when explicitly running behind a
// known reverse proxy (TRUST_PROXY=1 in env). Without it, a client can
// supply any IP to bypass the admin IP whitelist.
const _trustProxy = String(process.env.TRUST_PROXY || '0').trim() === '1';

const extractClientIp = (req) => {
  const forwardedFor = req.headers['x-forwarded-for'];
  if (forwardedFor && _trustProxy) {
    // Take the first (leftmost) address — the originating client.
    return forwardedFor.split(',')[0].trim();
  }
  if (forwardedFor && !_trustProxy) {
    // Header present but proxy not trusted — use socket address to prevent spoofing.
    if (process.env.NODE_ENV !== 'production') {
      console.warn('[adminAuth] x-forwarded-for header ignored (TRUST_PROXY not set). ' +
                   'Set TRUST_PROXY=1 if running behind a reverse proxy.');
    }
  }
  return normalizeIp(req.socket?.remoteAddress || req.ip || '');
};

/**
 * Verify admin token and check owner role.
 */
const requireOwner = async (req, res, next) => {
  try {
    // Prefer the HttpOnly admin cookie; header fallback is intentionally removed.
    const token = req.cookies?.elevate_admin_token;

    if (!token) {
      return res.status(401).json({ message: 'No admin token provided' });
    }

    if (!process.env.ADMIN_JWT_SECRET) {
      return res.status(500).json({ message: 'Admin auth is not configured' });
    }

    const decoded = jwt.verify(token, process.env.ADMIN_JWT_SECRET);

    if (!decoded.user || decoded.type !== 'admin' || !decoded.user.id) {
      return res.status(403).json({ message: 'Owner access required' });
    }

    const owner = await User.findById(decoded.user.id).select(
      '_id name email role adminLockedUntil'
    );

    if (!owner || owner.role !== 'owner') {
      return res.status(403).json({ message: 'Owner access required' });
    }

    if (owner.adminLockedUntil && new Date() < new Date(owner.adminLockedUntil)) {
      return res.status(403).json({
        message: 'Account temporarily locked',
        lockedUntil: owner.adminLockedUntil
      });
    }

    req.owner = {
      id: owner._id.toString(),
      name: owner.name,
      email: owner.email,
      role: owner.role
    };

    next();
  } catch (err) {
    console.error('Admin auth error:', err.message);
    return res.status(401).json({ message: 'Invalid or expired admin token' });
  }
};

// Bug #27 fix: track failed audit log writes so data loss is visible in logs.
let _failedAuditCount = 0;

/**
 * Log successful admin action responses for audit.
 * Bug #27 fix: failures are now logged with action context and counted so
 * ops can detect audit data loss by grepping "AUDIT_LOG_FAILURE".
 */
const logAdminAction = (action, targetType = null) => (req, res, next) => {
  const originalJson = res.json.bind(res);

  res.json = function patchedJson(data) {
    if (res.statusCode >= 200 && res.statusCode < 300 && req.owner) {
      AdminAuditLog.create({
        ownerId: req.owner.id,
        action,
        targetType,
        targetId: req.params.id || req.params.userId || req.params.announcementId || null,
        details: {
          body: redactSensitive(req.body),
          query: redactSensitive(req.query),
          responseMeta: {
            statusCode: res.statusCode,
            hasBody: data !== undefined
          }
        },
        ipAddress: extractClientIp(req),
        userAgent: req.get('user-agent')
      }).catch((error) => {
        _failedAuditCount += 1;
        // Bug #27 fix: log action name + running failure count so these are
        // never silently lost — searchable via "AUDIT_LOG_FAILURE".
        console.error(
          `[AUDIT_LOG_FAILURE] count=${_failedAuditCount} action=${action} ownerId=${req.owner?.id} error=${error.message}`
        );
      });
    }

    return originalJson(data);
  };

  next();
};

/** Expose failure counter for health checks / tests. */
const getFailedAuditCount = () => _failedAuditCount;

/**
 * Optional IP allow-list for admin endpoints.
 */
const checkAdminIP = (req, res, next) => {
  const whitelist = process.env.ADMIN_IP_WHITELIST;
  if (!whitelist) {
    return next();
  }

  const allowedIPs = whitelist.split(',').map((ip) => normalizeIp(ip));
  const clientIP = extractClientIp(req);
  const normalizedClientIP = normalizeIp(clientIP);

  if (!allowedIPs.includes(normalizedClientIP)) {
    console.warn(`Admin access attempted from unauthorized IP: ${clientIP}`);
    return res.status(403).json({ message: 'Access denied from this location' });
  }

  return next();
};

module.exports = {
  requireOwner,
  logAdminAction,
  checkAdminIP,
  redactSensitive,
  getFailedAuditCount        // Bug #27 fix: expose for health checks / tests
};
