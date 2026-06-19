const rateLimit = require('express-rate-limit');

const parsePositiveInt = (value, fallback) => {
  const parsed = parseInt(value, 10);
  if (Number.isNaN(parsed) || parsed <= 0) {
    return fallback;
  }
  return parsed;
};

const normalizeIp = (rawIp = '') =>
  String(rawIp)
    .trim()
    .replace('::ffff:', '')
    .replace('::1', '127.0.0.1');

const _trustProxy = String(process.env.TRUST_PROXY || '0').trim() === '1';

const extractClientIp = (req) => {
  const forwardedFor = req.headers['x-forwarded-for'];
  if (forwardedFor && _trustProxy) {
    return forwardedFor.split(',')[0].trim();
  }
  return normalizeIp(req.socket?.remoteAddress || req.ip || '');
};

const baseLimiterConfig = {
  standardHeaders: true,
  legacyHeaders: false,
  keyGenerator: (req) => normalizeIp(extractClientIp(req))
};

const adminLoginLimiter = rateLimit({
  ...baseLimiterConfig,
  windowMs:
    parsePositiveInt(process.env.ADMIN_LOGIN_RATE_LIMIT_WINDOW_MINUTES, 15) *
    60 *
    1000,
  max: parsePositiveInt(process.env.ADMIN_LOGIN_RATE_LIMIT_MAX, 10),
  message: {
    message: 'Too many admin login attempts. Please try again later.'
  }
});

const adminApiLimiter = rateLimit({
  ...baseLimiterConfig,
  windowMs:
    parsePositiveInt(process.env.ADMIN_API_RATE_LIMIT_WINDOW_MINUTES, 1) *
    60 *
    1000,
  max: parsePositiveInt(process.env.ADMIN_API_RATE_LIMIT_MAX, 120),
  message: {
    message: 'Too many admin API requests. Please slow down.'
  }
});

// Bug #43 / #45 fixed: rate limiters for public auth endpoints
const authLoginLimiter = rateLimit({
  ...baseLimiterConfig,
  windowMs: parsePositiveInt(process.env.AUTH_LOGIN_RATE_LIMIT_WINDOW_MINUTES, 15) * 60 * 1000,
  max: parsePositiveInt(process.env.AUTH_LOGIN_RATE_LIMIT_MAX, 10),
  message: {
    message: 'Too many login attempts from this IP. Please try again in 15 minutes.'
  }
});

const authRegisterLimiter = rateLimit({
  ...baseLimiterConfig,
  windowMs: parsePositiveInt(process.env.AUTH_REGISTER_RATE_LIMIT_WINDOW_MINUTES, 60) * 60 * 1000,
  max: parsePositiveInt(process.env.AUTH_REGISTER_RATE_LIMIT_MAX, 5),
  message: {
    message: 'Too many registration attempts from this IP. Please try again later.'
  }
});

module.exports = {
  adminLoginLimiter,
  adminApiLimiter,
  authLoginLimiter,
  authRegisterLimiter,
};
