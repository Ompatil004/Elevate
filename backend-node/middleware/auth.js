const jwt = require('jsonwebtoken');
const User = require('../models/User');

/**
 * SEC-1 (complete): Auth middleware — reads the JWT exclusively from the
 * HttpOnly `elevate_token` cookie. The legacy `x-auth-token` header fallback
 * has been removed now that all clients send the cookie.
 *
 * Cookie name: `elevate_token` (HttpOnly, SameSite=None, Secure in prod)
 *
 * If you are rolling back to header-based auth (e.g. for a native mobile
 * client), re-add: `|| req.header('x-auth-token')` to line 19.
 */
module.exports = async function(req, res, next) {
    // SEC-1: only accept the HttpOnly cookie — no header fallback.
    const token = req.cookies?.elevate_token;

    if (!token) {
        return res.status(401).json({ message: 'No token, authorization denied' });
    }

    try {
        const decoded = jwt.verify(token, process.env.JWT_SECRET);
        req.user = decoded.user || decoded;

        const sessionMaxMs = Number(process.env.SESSION_MAX_MS || 4 * 60 * 60 * 1000);
        const issuedAtMs = Number(decoded?.iat) * 1000;
        if (Number.isFinite(sessionMaxMs) && Number.isFinite(issuedAtMs) && sessionMaxMs > 0) {
            if (Date.now() - issuedAtMs > sessionMaxMs) {
                res.clearCookie('elevate_token', {
                    path: '/',
                    sameSite: process.env.NODE_ENV === 'production' ? 'none' : 'lax',
                    secure: process.env.NODE_ENV === 'production',
                });
                return res.status(401).json({
                    message: 'Session expired. Please log in again.',
                    code: 'SESSION_EXPIRED',
                });
            }
        }

        // PERF-4: isSuspended is now embedded in the JWT payload, so we can
        // avoid a DB round-trip on every request.
        //
        // - If the field is present in the token: enforce it immediately.
        // - If the field is missing (legacy tokens issued before this change):
        //   fall back to a DB lookup. Old tokens expire within 7 days.
        if (typeof req.user.isSuspended === 'boolean') {
            // Fast path — no DB hit needed.
            if (req.user.isSuspended) {
                return res.status(403).json({
                    message: 'Account is suspended. Please contact support.'
                });
            }
        } else {
            // Legacy token — do the DB lookup as a safe fallback.
            const user = await User.findById(req.user.id).select('isSuspended').lean();
            if (!user) {
                return res.status(401).json({ message: 'User not found' });
            }
            if (user.isSuspended) {
                return res.status(403).json({
                    message: 'Account is suspended. Please contact support.'
                });
            }
        }

        next();
    } catch (err) {
        // SEC-2 fix: only log in dev; never expose token details in production
        if (process.env.NODE_ENV !== 'production') {
            console.error('Auth error:', err.message);
        }
        res.status(401).json({ message: 'Token is not valid' });
    }
};
