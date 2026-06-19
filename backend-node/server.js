require('dotenv').config();
const express = require('express');
const mongoose = require('mongoose');
const cors = require('cors');

const app = express();

// Bug #49 fixed: GOOGLE_CLIENT_ID added to required vars — without it OAuth endpoints crash at runtime
const requiredEnv = ['MONGO_URI', 'JWT_SECRET', 'ADMIN_JWT_SECRET', 'GOOGLE_CLIENT_ID', 'CORS_ORIGINS'];
const missingEnv = requiredEnv.filter((k) => !process.env[k]);

const isPlaceholderSecret = (value = '') => {
    const normalized = String(value || '').trim().toLowerCase();
    if (!normalized) return true;
    return (
        normalized.includes('change-me') ||
        normalized.includes('your-') ||
        normalized.includes('placeholder')
    );
};

const isLocalMongoUri = (uri = '') => {
    const normalized = String(uri || '').toLowerCase();
    return normalized.includes('localhost') || normalized.includes('127.0.0.1') || normalized.includes('::1');
};

if (!process.env.ADMIN_SECRET_KEY_HASH && !process.env.ADMIN_SECRET_KEY) {
    missingEnv.push('ADMIN_SECRET_KEY_HASH (or ADMIN_SECRET_KEY for local bootstrap)');
}

if (missingEnv.length > 0) {
    console.error(`❌ Missing required environment variables: ${missingEnv.join(', ')}`);
    process.exit(1);
}

// SEC-34: Prevent running with placeholder/default secrets outside test env.
if (process.env.NODE_ENV !== 'test') {
    const placeholderIssues = [];
    if (isPlaceholderSecret(process.env.JWT_SECRET)) placeholderIssues.push('JWT_SECRET');
    if (isPlaceholderSecret(process.env.ADMIN_JWT_SECRET)) placeholderIssues.push('ADMIN_JWT_SECRET');
    if (process.env.ADMIN_SECRET_KEY && isPlaceholderSecret(process.env.ADMIN_SECRET_KEY)) {
        placeholderIssues.push('ADMIN_SECRET_KEY');
    }

    if (placeholderIssues.length > 0) {
        console.error(`❌ Placeholder secrets are not allowed: ${placeholderIssues.join(', ')}`);
        process.exit(1);
    }
}

if (process.env.NODE_ENV === 'production' && process.env.ADMIN_SECRET_KEY) {
    console.warn('⚠️ ADMIN_SECRET_KEY is set in production. Prefer only ADMIN_SECRET_KEY_HASH.');
}

// SEC-22: Prevent accidental non-TLS Mongo usage in production unless explicitly overridden.
if (process.env.NODE_ENV === 'production') {
    const mongoUri = String(process.env.MONGO_URI || '').trim();
    const insecureMongo = mongoUri.startsWith('mongodb://') && !isLocalMongoUri(mongoUri);
    const allowInsecureMongo = String(process.env.ALLOW_INSECURE_MONGO || '0').trim() === '1';

    if (insecureMongo && !allowInsecureMongo) {
        console.error('❌ Insecure Mongo URI detected for production. Use mongodb+srv:// (TLS) or set ALLOW_INSECURE_MONGO=1 only for controlled private networks.');
        process.exit(1);
    }

    if (insecureMongo && allowInsecureMongo) {
        console.warn('⚠️ ALLOW_INSECURE_MONGO=1 enabled in production. Ensure network-level encryption and restricted access are enforced.');
    }
}

// BUG-N3 fix: gate app.listen() behind the MongoDB 'connected' event so the
// server never opens its port before the database is ready.
// Enhanced: retry with diagnostics instead of instant crash on first failure.
const MONGO_MAX_RETRIES = 3;
const MONGO_RETRY_DELAY_MS = 5000;

const connectWithRetry = async (attempt = 1) => {
    const uri = process.env.MONGO_URI;
    const maskedUri = uri.replace(/:\/\/([^:]+):([^@]+)@/, '://$1:****@'); // hide password

    console.log(`\n🔌 MongoDB connection attempt ${attempt}/${MONGO_MAX_RETRIES}`);
    console.log(`   URI: ${maskedUri}`);

    try {
        await mongoose.connect(uri, {
            serverSelectionTimeoutMS: 5000, // fail fast instead of 30s default
            socketTimeoutMS: 10000,
        });
        console.log('✅ MongoDB connected successfully');
        return true;
    } catch (err) {
        const isLocal = isLocalMongoUri(uri);
        console.error(`❌ MongoDB connection attempt ${attempt} failed: ${err.message}`);

        if (err.message.includes('ECONNREFUSED')) {
            console.error('');
            console.error('   ┌──────────────────────────────────────────────────────┐');
            console.error('   │  MongoDB is not running on the expected host/port.   │');
            if (isLocal) {
                console.error('   │                                                      │');
                console.error('   │  To fix (Windows):                                   │');
                console.error('   │    1. Open an Admin terminal                         │');
                console.error('   │    2. Run: net start MongoDB                         │');
                console.error('   │                                                      │');
                console.error('   │  Or start manually:                                  │');
                console.error('   │    mongod --dbpath C:\\data\\db                         │');
            } else {
                console.error('   │  Check your MONGO_URI in .env and ensure the         │');
                console.error('   │  remote server is accessible.                        │');
            }
            console.error('   └──────────────────────────────────────────────────────┘');
            console.error('');
        }

        if (attempt < MONGO_MAX_RETRIES) {
            console.log(`   ⏳ Retrying in ${MONGO_RETRY_DELAY_MS / 1000}s...`);
            await new Promise(resolve => setTimeout(resolve, MONGO_RETRY_DELAY_MS));
            return connectWithRetry(attempt + 1);
        }

        console.error(`❌ All ${MONGO_MAX_RETRIES} MongoDB connection attempts failed. Exiting.`);
        process.exit(1);
    }
};

connectWithRetry();

// Middleware
// SEC-9 fix: validate CORS origins at startup.
// Missing or wildcard '*' origins in production cause immediate exit.
if (!process.env.CORS_ORIGINS) {
    console.error('❌ CORS_ORIGINS environment variable is not set. Server cannot start.');
    process.exit(1);
}
const corsOrigins = process.env.CORS_ORIGINS.split(',').map((o) => o.trim()).filter(Boolean);
if (process.env.NODE_ENV === 'production' && corsOrigins.includes('*')) {
    console.error('❌ Wildcard "*" is not permitted for CORS_ORIGINS in production.');
    process.exit(1);
}
app.use(cors({ origin: corsOrigins, credentials: true }));
// SEC-40: Enforce conservative body-size limits to reduce payload abuse / memory pressure.
app.use(express.json({ limit: '100kb' }));
app.use(express.urlencoded({ extended: false, limit: '100kb' }));

// SEC-36: Baseline security headers (helmet-lite without extra dependency).
app.use((req, res, next) => {
    res.setHeader('X-Content-Type-Options', 'nosniff');
    res.setHeader('X-Frame-Options', 'DENY');
    res.setHeader('Referrer-Policy', 'no-referrer');
    res.setHeader('Permissions-Policy', 'camera=(), microphone=(), geolocation=()');
    if (process.env.NODE_ENV === 'production') {
        res.setHeader('Strict-Transport-Security', 'max-age=31536000; includeSubDomains');
    }
    next();
});

// SEC-1: Parse cookies for HttpOnly token authentication
const cookieParser = require('cookie-parser');
app.use(cookieParser());

// SEC-12: CSRF protection using the Signed Double-Submit Cookie pattern.
// - A CSRF cookie is set when the client calls GET /api/csrf-token
// - Every state-mutating request (POST/PUT/DELETE) must include the CSRF
//   token in the 'x-csrf-token' header or the request is rejected with 403.
// - Login/register/Google OAuth are explicitly exempted because:
//     a) They accept only JSON (not form submissions) which browsers can't
//        auto-forge without CORS preflight.
//     b) A valid auth cookie doesn't yet exist before login completes.
const { doubleCsrf } = require('csrf-csrf');
const isProd = process.env.NODE_ENV === 'production';
const csrfCookieName = isProd ? '__Host-psifi.x-csrf-token' : 'psifi.x-csrf-token';
const { generateToken: csrfGenerateToken, doubleCsrfProtection } = doubleCsrf({
    getSecret: () => process.env.JWT_SECRET,      // reuse the app secret
    // __Host- cookies require HTTPS + Secure and are invalid on local HTTP dev.
    cookieName: csrfCookieName,
    cookieOptions: {
        sameSite: isProd ? 'none' : 'lax',
        secure: isProd,
        httpOnly: true,
        path: '/',
    },
    getTokenFromRequest: (req) =>
        req.headers['x-csrf-token'] || req.body?._csrf,
    size: 64,
    ignoredMethods: ['GET', 'HEAD', 'OPTIONS'],
});

// Exempt auth endpoints from CSRF (they establish the session).
const CSRF_EXEMPT = new Set([
    '/api/auth/login', '/api/auth/register', '/api/auth/google', '/api/auth/logout',
    '/api/v1/auth/login', '/api/v1/auth/register', '/api/v1/auth/google', '/api/v1/auth/logout',
    '/api/admin/login', '/api/v1/admin/login',
]);
app.use((req, res, next) => {
    if (CSRF_EXEMPT.has(req.path)) return next();
    return doubleCsrfProtection(req, res, next);
});

// Normalize CSRF failures to JSON so frontend can handle and refresh token gracefully.
app.use((err, req, res, next) => {
    if (!err) return next();
    const msg = String(err?.message || '').toLowerCase();
    if (msg.includes('csrf')) {
        return res.status(403).json({
            message: 'CSRF token validation failed',
            code: 'CSRF_INVALID',
        });
    }
    return next(err);
});

// Expose the CSRF token to the SPA so it can include it in subsequent requests.
app.get('/api/csrf-token', (req, res) => {
    res.json({ csrfToken: csrfGenerateToken(req, res) });
});

// ARCH-6: Attach a unique x-request-id to every request for distributed tracing.
// Preserves the incoming header if a reverse-proxy (nginx/ALB) already set it.
const { randomUUID } = require('crypto');
app.use((req, _res, next) => {
    req.requestId = req.headers['x-request-id'] || randomUUID();
    // Echo back so clients / downstream services can correlate logs
    _res.setHeader('x-request-id', req.requestId);
    next();
});

// Routes
const authRoutes = require('./routes/auth');
const profileRoutes = require('./routes/profile');
const usersRoutes = require('./routes/users');
const adminAuthRoutes = require('./routes/adminAuth');
const adminUserRoutes = require('./routes/adminUsers');
const adminSystemRoutes = require('./routes/adminSystem');
const adminContentRoutes = require('./routes/adminContent');
const { adminApiLimiter } = require('./middleware/adminRateLimit');
const { checkAdminIP } = require('./middleware/adminAuth');

// PERF-1 / BUG-N1 fix: Cache maintenance mode in memory with a 30-second TTL
// to avoid a MongoDB round-trip on EVERY non-admin request.
let _maintenanceCache = { enabled: false, message: '', expiresAt: 0 };

app.use(async (req, res, next) => {
    if (req.path.startsWith('/api/admin') || req.path === '/health') {
        return next();
    }

    const now = Date.now();
    if (now < _maintenanceCache.expiresAt) {
        // Serve from cache
        if (_maintenanceCache.enabled) {
            return res.status(503).json({
                message: _maintenanceCache.message || 'System is under maintenance. Please try again later.',
                maintenance: true
            });
        }
        return next();
    }

    try {
        const SystemConfig = require('./models/SystemConfig');
        const config = await SystemConfig.findOne({ key: 'maintenanceMode' }).lean();
        _maintenanceCache = {
            enabled: config?.value?.enabled ?? false,
            message: config?.value?.message ?? '',
            expiresAt: now + 30_000, // 30-second TTL
        };

        if (_maintenanceCache.enabled) {
            return res.status(503).json({
                message: _maintenanceCache.message || 'System is under maintenance. Please try again later.',
                maintenance: true
            });
        }
    } catch (err) {
        console.error('[Maintenance middleware] Error checking maintenance mode:', err.message);
        // Continue on middleware errors to avoid total outage.
    }

    return next();
});

app.use('/api/auth', authRoutes);
app.use('/api/profile', profileRoutes);
app.use('/api/users', usersRoutes);
app.use('/api/admin', checkAdminIP);
// BUG-N4 fix: skip the blanket adminApiLimiter for /login — that route applies
// its own stricter adminLoginLimiter, so applying both was double-limiting logins.
app.use('/api/admin', (req, res, next) => {
    if (req.path === '/login') return next();
    return adminApiLimiter(req, res, next);
});
app.use('/api/admin', adminAuthRoutes);
app.use('/api/admin/users', adminUserRoutes);
app.use('/api/admin/system', adminSystemRoutes);
app.use('/api/admin/content', adminContentRoutes);

// ARCH-1: Versioned API routes (/api/v1/…)
// Both /api/ and /api/v1/ are active simultaneously for backward compatibility.
// New clients should use /api/v1/; deprecation warnings will be added to /api/
// once the frontend has been fully migrated.
app.use('/api/v1/auth',           authRoutes);
app.use('/api/v1/profile',        profileRoutes);
app.use('/api/v1/users',          usersRoutes);
app.use('/api/v1/admin',          checkAdminIP);
app.use('/api/v1/admin', (req, res, next) => {
    if (req.path === '/login') return next();
    return adminApiLimiter(req, res, next);
});
app.use('/api/v1/admin',          adminAuthRoutes);
app.use('/api/v1/admin/users',    adminUserRoutes);
app.use('/api/v1/admin/system',   adminSystemRoutes);
app.use('/api/v1/admin/content',  adminContentRoutes);

console.log('✅ All routes registered');

// Health check
app.get('/health', (req, res) => {
    res.json({ status: 'OK', message: 'Server is running' });
});

// Test database connection
// Bug #16 fixed: restrict this endpoint to non-production environments only
// to prevent information leakage (user count + DB connectivity status).
app.get('/test-db', async (req, res) => {
    // Expose only when explicitly enabled in local development.
    if (process.env.ENABLE_TEST_DB_ENDPOINT !== '1' || process.env.NODE_ENV === 'production') {
        return res.status(404).json({ message: 'Not found' });
    }
    try {
        const User = require('./models/User');
        // Bug #48 fixed: use estimatedDocumentCount() — much faster for large collections
        const count = await User.estimatedDocumentCount();
        res.json({
            status: 'OK',
            message: 'Database connected',
            userCount: count
        });
    } catch (err) {
        res.status(500).json({
            status: 'ERROR',
            message: 'Database connection failed'
        });
    }
});

const PORT = process.env.PORT || 5000;

// BUG-N3 fix: listen only after MongoDB is connected to avoid accepting
// requests against an unready database.
let server;
mongoose.connection.once('connected', () => {
    server = app.listen(PORT, () => {
        console.log(`🚀 Server running on http://localhost:${PORT}`);
        console.log('📍 Available routes:');
        console.log('   - POST http://localhost:5000/api/auth/register');
        console.log('   - POST http://localhost:5000/api/auth/login');
        console.log('   - GET  http://localhost:5000/api/profile');
        console.log('   - POST http://localhost:5000/api/profile/update');
    });
});

// BUG-N9 fix: Graceful shutdown to close MongoDB and HTTP server cleanly
const gracefulShutdown = async (signal) => {
    console.log(`\n${signal} received. Shutting down gracefully...`);
    // Arm force-exit BEFORE awaiting anything so it can't be skipped.
    const forceExit = setTimeout(() => {
        console.error('⚠️  Forced shutdown after timeout.');
        process.exit(1);
    }, 10000);
    forceExit.unref(); // Don't block the event loop if everything closes cleanly.

    const closeServer = () => new Promise((resolve) => {
        if (!server) return resolve();
        server.close(resolve);
    });
    await closeServer();
    try {
        await mongoose.connection.close();
        console.log('✅ MongoDB connection closed.');
    } catch (err) {
        console.error('Error closing MongoDB connection:', err);
    }
    clearTimeout(forceExit);
    process.exit(0);
};

process.on('SIGTERM', () => gracefulShutdown('SIGTERM'));
process.on('SIGINT',  () => gracefulShutdown('SIGINT'));
