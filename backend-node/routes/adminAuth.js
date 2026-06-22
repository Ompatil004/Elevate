const express = require('express');
const bcrypt = require('bcryptjs');
const crypto = require('crypto');
const jwt = require('jsonwebtoken');
const User = require('../models/User');
const AdminAuditLog = require('../models/AdminAuditLog');
const { checkAdminIP, requireOwner } = require('../middleware/adminAuth');
const { adminLoginLimiter } = require('../middleware/adminRateLimit');
const { sendSecurityAlert } = require('../services/securityNotificationService');

const router = express.Router();

const MAX_ATTEMPTS = parseInt(process.env.ADMIN_MAX_LOGIN_ATTEMPTS || '5', 10);
const LOCKOUT_MINUTES = parseInt(
  process.env.ADMIN_LOCKOUT_DURATION_MINUTES || '30',
  10
);
// Effectively infinite max age (100 years)
const ADMIN_COOKIE_MAX_AGE_MS = 100 * 365 * 24 * 60 * 60 * 1000;

const _trustProxy = String(process.env.TRUST_PROXY || '0').trim() === '1';

const normalizeIp = (rawIp = '') =>
  String(rawIp)
    .trim()
    .replace('::ffff:', '')
    .replace('::1', '127.0.0.1');

const extractClientIp = (req) => {
  const forwardedFor = req.headers['x-forwarded-for'];
  if (forwardedFor && _trustProxy) {
    return forwardedFor.split(',')[0].trim();
  }
  return normalizeIp(req.socket?.remoteAddress || req.ip || '');
};

const dispatchSecurityAlert = (eventType, details) => {
  sendSecurityAlert(eventType, details).catch((error) => {
    console.error(`Security alert dispatch failed (${eventType}):`, error.message);
  });
};

const safeTimingEqual = (a, b) => {
  const aBuf = Buffer.from(String(a || ''));
  const bBuf = Buffer.from(String(b || ''));

  if (aBuf.length !== bBuf.length) {
    return false;
  }

  return crypto.timingSafeEqual(aBuf, bBuf);
};

const verifyAdminKey = async (providedKey) => {
  const hashedKey = process.env.ADMIN_SECRET_KEY_HASH;
  if (hashedKey) {
    return bcrypt.compare(String(providedKey || ''), hashedKey);
  }

  // Local bootstrap fallback only (keep unset in production).
  if (process.env.NODE_ENV === 'production') {
    return false;
  }

  const plainKey = process.env.ADMIN_SECRET_KEY || '';
  if (!plainKey) return false;

  return safeTimingEqual(providedKey, plainKey);
};

const handleFailedAttempt = async (user) => {
  user.adminLoginAttempts = (user.adminLoginAttempts || 0) + 1;

  let lockedUntil = null;
  if (user.adminLoginAttempts >= MAX_ATTEMPTS) {
    lockedUntil = new Date(Date.now() + LOCKOUT_MINUTES * 60000);
    user.adminLockedUntil = lockedUntil;
    user.adminLoginAttempts = 0;
  }

  await user.save();
  return lockedUntil;
};

const setAdminAuthCookie = (res, token) => {
  res.cookie('elevate_admin_token', token, {
    httpOnly: true,
    secure: process.env.NODE_ENV === 'production',
    sameSite: process.env.NODE_ENV === 'production' ? 'strict' : 'lax',
    maxAge: ADMIN_COOKIE_MAX_AGE_MS,
    path: '/',
  });
};

/**
 * POST /api/admin/login
 */
router.post('/login', checkAdminIP, adminLoginLimiter, async (req, res) => {
  try {
    const { email, password, adminKey } = req.body;
    const clientIp = extractClientIp(req);

    if (!email || !password || !adminKey) {
      return res
        .status(400)
        .json({ message: 'Email, password, and admin key required' });
    }

    const user = await User.findOne({ email });

    if (!user || user.role !== 'owner') {
      return res.status(401).json({ message: 'Invalid credentials' });
    }

    if (user.isSuspended) {
      return res.status(403).json({ message: 'Owner account is suspended' });
    }

    if (user.adminLockedUntil && new Date() < new Date(user.adminLockedUntil)) {
      const minutesLeft = Math.ceil(
        (new Date(user.adminLockedUntil) - new Date()) / 60000
      );
      return res.status(403).json({
        message: `Account locked. Try again in ${minutesLeft} minutes.`
      });
    }

    const [isPasswordValid, isAdminKeyValid] = await Promise.all([
      bcrypt.compare(password, user.password),
      verifyAdminKey(adminKey)
    ]);

    if (!isPasswordValid || !isAdminKeyValid) {
      const lockedUntil = await handleFailedAttempt(user);

      await AdminAuditLog.create({
        ownerId: user._id,
        action: 'ADMIN_LOGIN_FAILED',
        targetType: 'owner',
        details: {
          reason: 'Invalid admin credentials',
          attemptsAfterFailure: user.adminLoginAttempts
        },
        ipAddress: clientIp,
        userAgent: req.get('user-agent')
      });

      dispatchSecurityAlert('ADMIN_LOGIN_FAILED', {
        ownerId: user._id.toString(),
        ownerEmail: user.email,
        attemptsAfterFailure: user.adminLoginAttempts,
        lockoutThreshold: MAX_ATTEMPTS,
        ipAddress: clientIp,
        userAgent: req.get('user-agent')
      });

      if (lockedUntil) {
        await AdminAuditLog.create({
          ownerId: user._id,
          action: 'SECURITY_LOCKOUT',
          targetType: 'owner',
          details: {
            reason: 'Too many failed admin login attempts'
          },
          ipAddress: clientIp,
          userAgent: req.get('user-agent')
        });

        dispatchSecurityAlert('SECURITY_LOCKOUT', {
          ownerId: user._id.toString(),
          ownerEmail: user.email,
          lockedUntil,
          lockoutDurationMinutes: LOCKOUT_MINUTES,
          ipAddress: clientIp,
          userAgent: req.get('user-agent')
        });

        return res.status(403).json({
          message: `Too many failed attempts. Account locked for ${LOCKOUT_MINUTES} minutes.`,
          lockedUntil
        });
      }

      return res.status(401).json({ message: 'Invalid credentials' });
    }

    user.adminLoginAttempts = 0;
    user.adminLockedUntil = null;
    user.adminLastLoginAt = new Date();
    await user.save();

    const tokenExpiry = process.env.ADMIN_SESSION_EXPIRY || '2h';
    const adminJwtSecret = process.env.ADMIN_JWT_SECRET;

    if (!adminJwtSecret) {
      return res.status(500).json({
        message: 'ADMIN_JWT_SECRET is required for admin authentication'
      });
    }

    const token = jwt.sign(
      {
        type: 'admin',
        user: {
          id: user._id.toString(),
          role: 'owner',
          email: user.email
        }
      },
      adminJwtSecret
    );
    setAdminAuthCookie(res, token);

    await AdminAuditLog.create({
      ownerId: user._id,
      action: 'LOGIN',
      targetType: 'owner',
      ipAddress: clientIp,
      userAgent: req.get('user-agent')
    });

    return res.json({
      message: 'Admin login successful',
      owner: {
        id: user._id,
        name: user.name,
        email: user.email,
        role: 'owner',
        lastLoginAt: user.adminLastLoginAt
      },
      expiresIn: tokenExpiry
    });
  } catch (error) {
    console.error('Admin login error:', error);
    return res.status(500).json({
      message: 'Server error'
    });
  }
});

/**
 * POST /api/admin/logout
 */
router.post('/logout', requireOwner, async (req, res) => {
  try {
    await AdminAuditLog.create({
      ownerId: req.owner.id,
      action: 'LOGOUT',
      targetType: 'owner',
      ipAddress: extractClientIp(req),
      userAgent: req.get('user-agent')
    });
  } catch (error) {
    console.error('Logout logging error:', error.message);
  }

  res.clearCookie('elevate_admin_token', {
    path: '/',
    sameSite: process.env.NODE_ENV === 'production' ? 'strict' : 'lax',
    secure: process.env.NODE_ENV === 'production',
  });

  return res.json({ message: 'Logged out successfully' });
});

/**
 * GET /api/admin/verify
 */
router.get('/verify', requireOwner, async (req, res) => {
  try {
    const user = await User.findById(req.owner.id).select(
      'name email role adminLastLoginAt'
    );

    if (!user) {
      return res.status(401).json({ valid: false, message: 'User not found' });
    }

    return res.json({
      valid: true,
      owner: {
        id: user._id,
        name: user.name,
        email: user.email,
        role: user.role,
        lastLoginAt: user.adminLastLoginAt
      }
    });
  } catch (error) {
    return res.status(401).json({ valid: false, message: 'Invalid token' });
  }
});

module.exports = router;
