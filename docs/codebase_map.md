# Codebase Structural Map

## test_meal_engine_fixes.py
```python
# Add backend app directory to path
    # 1. Test swap options
    # 2. Test suggest_daily_meals with scale factor
```

## backend-node\persistence_qa.js
```javascript
  "app.use('/api/auth', authRoutes)",
  // [Logic Hidden]
  "app.use('/api/profile', profileRoutes)",
  // [Logic Hidden]
  "app.use('/api/users', usersRoutes)",
  // [Logic Hidden]
  "app.use('/api/admin', checkAdminIP)",
  // [Logic Hidden]
  "app.use('/api/admin', (req, res, next) =>",
  // [Logic Hidden]
  "app.use('/api/admin', adminAuthRoutes)",
  // [Logic Hidden]
  "app.use('/api/admin/users', adminUserRoutes)",
  // [Logic Hidden]
  "app.use('/api/admin/system', adminSystemRoutes)",
  // [Logic Hidden]
  "app.use('/api/admin/content', adminContentRoutes)",
  // [Logic Hidden]
  "app.get('/health'",
  // [Logic Hidden]
const missing = requiredSnippets.filter((snippet) => !serverCode.includes(snippet));
  // [Logic Hidden]
  missing.forEach((snippet) => console.error(` - ${snippet}`));
  // [Logic Hidden]
```

## backend-node\python_api_contract_qa.js
```javascript
  '@app.post("/workout")',
  // [Logic Hidden]
  '@app.post("/workout/async")',
  // [Logic Hidden]
  '@app.get("/workout/status/{job_id}")',
  // [Logic Hidden]
  '@app.post("/workout/cache/invalidate")',
  // [Logic Hidden]
  '@app.get("/api/models/status")',
  // [Logic Hidden]
  '@app.post("/api/models/warmup")',
  // [Logic Hidden]
  '@app.get("/api/weekly-plan")',
  // [Logic Hidden]
  '@app.get("/api/swap-options")',
  // [Logic Hidden]
  '@app.post("/api/swap-rest-to-workout")',
  // [Logic Hidden]
  '@app.post("/api/swap-workout-to-rest")',
  // [Logic Hidden]
  '@router.put("/update")',
  // [Logic Hidden]
const missingFrontend = frontendMustUse.filter((snippet) => !frontendApi.includes(snippet));
  // [Logic Hidden]
const missingServer = pythonMustExposeInServer.filter((snippet) => !pythonServer.includes(snippet));
  // [Logic Hidden]
const missingProfile = pythonMustExposeInProfileRouter.filter((snippet) => !pythonProfile.includes(snippet));
  // [Logic Hidden]
    missingFrontend.forEach((snippet) => console.error(` - ${snippet}`));
  // [Logic Hidden]
    missingServer.forEach((snippet) => console.error(` - ${snippet}`));
  // [Logic Hidden]
    missingProfile.forEach((snippet) => console.error(` - ${snippet}`));
  // [Logic Hidden]
```

## backend-node\server.js
```javascript
// Bug #49 fixed: GOOGLE_CLIENT_ID added to required vars — without it OAuth endpoints crash at runtime
const missingEnv = requiredEnv.filter((k) => !process.env[k]);
  // [Logic Hidden]
const isPlaceholderSecret = (value = '') => {
  // [Logic Hidden]
const isLocalMongoUri = (uri = '') => {
  // [Logic Hidden]
// SEC-34: Prevent running with placeholder/default secrets outside test env.
// SEC-22: Prevent accidental non-TLS Mongo usage in production unless explicitly overridden.
// BUG-N3 fix: gate app.listen() behind the MongoDB 'connected' event so the
  // [Logic Hidden]
// server never opens its port before the database is ready.
// Enhanced: retry with diagnostics instead of instant crash on first failure.
const connectWithRetry = async (attempt = 1) => {
  // [Logic Hidden]
            await new Promise(resolve => setTimeout(resolve, MONGO_RETRY_DELAY_MS));
  // [Logic Hidden]
// Middleware
// SEC-9 fix: validate CORS origins at startup.
// Missing or wildcard '*' origins in production cause immediate exit.
// SEC-1: Parse cookies for HttpOnly token authentication
app.use(cookieParser());
  // [Logic Hidden]
const corsOrigins = process.env.CORS_ORIGINS.split(',').map((o) => o.trim()).filter(Boolean);
  // [Logic Hidden]
app.use(cors({ origin: corsOrigins, credentials: true }));
  // [Logic Hidden]
// SEC-40: Enforce conservative body-size limits to reduce payload abuse / memory pressure.
// Python proxy routes use a dedicated parser so only one JSON middleware runs per request.
app.use((req, res, next) => {
  // [Logic Hidden]
app.use(express.urlencoded({ extended: false, limit: DEFAULT_JSON_LIMIT }));
  // [Logic Hidden]
// SEC-36: Baseline security headers (helmet-lite without extra dependency).
app.use((req, res, next) => {
  // [Logic Hidden]
// SEC-12: CSRF protection using the Signed Double-Submit Cookie pattern.
// - A CSRF cookie is set when the client calls GET /api/csrf-token
// - Every state-mutating request (POST/PUT/DELETE) must include the CSRF
//   token in the 'x-csrf-token' header or the request is rejected with 403.
// - Login/register/Google OAuth are explicitly exempted because:
//     a) They accept only JSON (not form submissions) which browsers can't
//        auto-forge without CORS preflight.
//     b) A valid auth cookie doesn't yet exist before login completes.
    getSecret: () => process.env.JWT_SECRET,      // reuse the app secret
  // [Logic Hidden]
    // __Host- cookies require HTTPS + Secure and are invalid on local HTTP dev.
    getTokenFromRequest: (req) =>
  // [Logic Hidden]
// Exempt auth endpoints from CSRF (they establish the session).
app.use((req, res, next) => {
  // [Logic Hidden]
// Normalize CSRF failures to JSON so frontend can handle and refresh token gracefully.
app.use((err, req, res, next) => {
  // [Logic Hidden]
// Expose the CSRF token to the SPA so it can include it in subsequent requests.
app.get('/api/csrf-token', (req, res) => {
  // [Logic Hidden]
// ARCH-6: Attach a unique x-request-id to every request for distributed tracing.
// Preserves the incoming header if a reverse-proxy (nginx/ALB) already set it.
app.use((req, _res, next) => {
  // [Logic Hidden]
    // Echo back so clients / downstream services can correlate logs
// Routes
// PERF-1 / BUG-N1 fix: Cache maintenance mode in memory with a 30-second TTL
// to avoid a MongoDB round-trip on EVERY non-admin request.
app.use(async (req, res, next) => {
  // [Logic Hidden]
        // Serve from cache
        // Continue on middleware errors to avoid total outage.
app.use('/api/auth', authRoutes);
  // [Logic Hidden]
app.use('/api/profile', profileRoutes);
  // [Logic Hidden]
app.use('/api/python', pythonProxyRoutes);
  // [Logic Hidden]
app.use('/api/users', usersRoutes);
  // [Logic Hidden]
app.use('/api/admin', checkAdminIP);
  // [Logic Hidden]
// BUG-N4 fix: skip the blanket adminApiLimiter for /login — that route applies
// its own stricter adminLoginLimiter, so applying both was double-limiting logins.
app.use('/api/admin', (req, res, next) => {
  // [Logic Hidden]
app.use('/api/admin', adminAuthRoutes);
  // [Logic Hidden]
app.use('/api/admin/users', adminUserRoutes);
  // [Logic Hidden]
app.use('/api/admin/system', adminSystemRoutes);
  // [Logic Hidden]
app.use('/api/admin/content', adminContentRoutes);
  // [Logic Hidden]
// ARCH-1: Versioned API routes (/api/v1/…)
// Both /api/ and /api/v1/ are active simultaneously for backward compatibility.
// New clients should use /api/v1/; deprecation warnings will be added to /api/
// once the frontend has been fully migrated.
app.use('/api/v1/auth',           authRoutes);
  // [Logic Hidden]
app.use('/api/v1/profile',        profileRoutes);
  // [Logic Hidden]
app.use('/api/v1/python',         pythonProxyRoutes);
  // [Logic Hidden]
app.use('/api/v1/users',          usersRoutes);
  // [Logic Hidden]
app.use('/api/v1/admin',          checkAdminIP);
  // [Logic Hidden]
app.use('/api/v1/admin', (req, res, next) => {
  // [Logic Hidden]
app.use('/api/v1/admin',          adminAuthRoutes);
  // [Logic Hidden]
app.use('/api/v1/admin/users',    adminUserRoutes);
  // [Logic Hidden]
app.use('/api/v1/admin/system',   adminSystemRoutes);
  // [Logic Hidden]
app.use('/api/v1/admin/content',  adminContentRoutes);
  // [Logic Hidden]
// Health check
app.get('/health', (req, res) => {
  // [Logic Hidden]
// Test database connection
// Bug #16 fixed: restrict this endpoint to non-production environments only
// to prevent information leakage (user count + DB connectivity status).
app.get('/test-db', async (req, res) => {
  // [Logic Hidden]
    // Expose only when explicitly enabled in local development.
        // Bug #48 fixed: use estimatedDocumentCount() — much faster for large collections
// BUG-N3 fix: listen only after MongoDB is connected to avoid accepting
// requests against an unready database.
mongoose.connection.once('connected', () => {
  // [Logic Hidden]
    server = app.listen(PORT, () => {
  // [Logic Hidden]
// BUG-N9 fix: Graceful shutdown to close MongoDB and HTTP server cleanly
const gracefulShutdown = async (signal) => {
  // [Logic Hidden]
    // Arm force-exit BEFORE awaiting anything so it can't be skipped.
    const forceExit = setTimeout(() => {
  // [Logic Hidden]
    const closeServer = () => new Promise((resolve) => {
  // [Logic Hidden]
process.on('SIGTERM', () => gracefulShutdown('SIGTERM'));
  // [Logic Hidden]
process.on('SIGINT',  () => gracefulShutdown('SIGINT'));
  // [Logic Hidden]
```

## backend-node\middleware\adminAuth.js
```javascript
const normalizeKey = (key) =>
  // [Logic Hidden]
const isSensitiveKey = (key) => {
  // [Logic Hidden]
    (candidate) => normalizeKey(candidate) === normalized
  // [Logic Hidden]
const redactSensitive = (payload) => {
  // [Logic Hidden]
      JSON.stringify(payload, (key, value) => {
  // [Logic Hidden]
const normalizeIp = (rawIp = '') =>
  // [Logic Hidden]
// SEC-5 fix: only trust x-forwarded-for when explicitly running behind a
// known reverse proxy (TRUST_PROXY=1 in env). Without it, a client can
// supply any IP to bypass the admin IP whitelist.
const extractClientIp = (req) => {
  // [Logic Hidden]
    // Take the first (leftmost) address — the originating client.
    // Header present but proxy not trusted — use socket address to prevent spoofing.
/**
 * Verify admin token and check owner role.
 */
const requireOwner = async (req, res, next) => {
  // [Logic Hidden]
    // Prefer the HttpOnly admin cookie; header fallback is intentionally removed.
// Bug #27 fix: track failed audit log writes so data loss is visible in logs.
/**
 * Log successful admin action responses for audit.
 * Bug #27 fix: failures are now logged with action context and counted so
 * ops can detect audit data loss by grepping "AUDIT_LOG_FAILURE".
 */
const logAdminAction = (action, targetType = null) => (req, res, next) => {
  // [Logic Hidden]
  res.json = function patchedJson(data) {
  // [Logic Hidden]
      }).catch((error) => {
  // [Logic Hidden]
        // Bug #27 fix: log action name + running failure count so these are
        // never silently lost — searchable via "AUDIT_LOG_FAILURE".
/** Expose failure counter for health checks / tests. */
const getFailedAuditCount = () => _failedAuditCount;
  // [Logic Hidden]
/**
 * Optional IP allow-list for admin endpoints.
 */
const checkAdminIP = (req, res, next) => {
  // [Logic Hidden]
  const allowedIPs = whitelist.split(',').map((ip) => normalizeIp(ip));
  // [Logic Hidden]
```

## backend-node\middleware\adminRateLimit.js
```javascript
const parsePositiveInt = (value, fallback) => {
  // [Logic Hidden]
const normalizeIp = (rawIp = '') =>
  // [Logic Hidden]
const extractClientIp = (req) => {
  // [Logic Hidden]
  keyGenerator: (req) => normalizeIp(extractClientIp(req))
  // [Logic Hidden]
// Bug #43 / #45 fixed: rate limiters for public auth endpoints
```

## backend-node\middleware\auth.js
```javascript
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
  // [Logic Hidden]
    // SEC-1 (modified): accept HttpOnly cookie, fall back to x-auth-token header for cross-site deployments (e.g. Render)
        // Session expiration check commented out as requested so sessions do not expire.
        /*
        */
        // PERF-4: isSuspended is now embedded in the JWT payload, so we can
        // avoid a DB round-trip on every request.
        //
        // - If the field is present in the token: enforce it immediately.
        // - If the field is missing (legacy tokens issued before this change):
        //   fall back to a DB lookup. Old tokens expire within 7 days.
            // Fast path — no DB hit needed.
            // Legacy token — do the DB lookup as a safe fallback.
        // SEC-2 fix: only log in dev; never expose token details in production
```

## backend-node\middleware\validate.js
```javascript
/**
 * ARCH-5: Centralized input validation schemas using express-validator.
 *
 * Usage in routes:
 *   const { validate, registerRules, loginRules } = require('../middleware/validate');
 *   router.post('/register', authRegisterLimiter, registerRules(), validate, handler);
  // [Logic Hidden]
 *
 * All validation errors are returned in a consistent shape:
 *   { success: false, errors: [{ field, message }] }
 */
/**
 * Runs accumulated validators and short-circuits with 422 if any fail.
 * Call this as the *last* middleware before the route handler.
 */
const validate = (req, res, next) => {
  // [Logic Hidden]
            errors: errors.array().map(e => ({ field: e.path, message: e.msg })),
  // [Logic Hidden]
// ── Auth routes ──────────────────────────────────────────────────────────────
const registerRules = () => [
  // [Logic Hidden]
const loginRules = () => [
  // [Logic Hidden]
const forgotPasswordRules = () => [
  // [Logic Hidden]
const resetPasswordRules = () => [
  // [Logic Hidden]
// ── Profile routes ────────────────────────────────────────────────────────────
const profileUpdateRules = () => [
  // [Logic Hidden]
// ── Admin routes ──────────────────────────────────────────────────────────────
const adminLoginRules = () => [
  // [Logic Hidden]
const mongoIdRules = (paramName = 'id') => [
  // [Logic Hidden]
```

## backend-node\models\User.js
```javascript
/**
 * BUG-N7 / ARCH-3: User.js
 *
 * Refactored from a flat schema to use named sub-schemas per domain:
 *   - SecuritySchema  — auth, passwords, suspension, admin access
 *   - FitnessProfileSchema — physical stats, goals, equipment
 *   - ActivityMetricsSchema — streaks, patterns, rest preferences
 *
 * Single-collection approach retained (no data migration needed).
 * Fields are identical — only organizational structure changed.
 */
// ─────────────────────────────────────────────────────────────────────────────
// Sub-schema: Security & Access Control
// Owns all authentication, password management, and account-status data.
// ─────────────────────────────────────────────────────────────────────────────
  // Account Status
  // Password management
  // Admin login tracking
// ─────────────────────────────────────────────────────────────────────────────
// Sub-schema: Fitness Profile
// Physical characteristics and training preferences.
// ─────────────────────────────────────────────────────────────────────────────
    // Bug #6c: Added 'Maintenance' (full word) + 'Maintain' (short form used in meal engine).
// ─────────────────────────────────────────────────────────────────────────────
// Sub-schema: Daily Trend Entry (element type for the trends array)
// ─────────────────────────────────────────────────────────────────────────────
  // Macro nutrients logged for the day
  // Hydration & recovery
  // Skipped exercises tracking
// ─────────────────────────────────────────────────────────────────────────────
// Root User Schema
// Composes sub-schemas by spreading them inline so the MongoDB document
// shape is unchanged — no migration required.
// ─────────────────────────────────────────────────────────────────────────────
  // ── Identity ───────────────────────────────────────────────────────────────
  // ── Domain sub-schemas ─────────────────────────────────────────────────────
  // Security / access-control fields (inlined for single-collection simplicity)
  // Fitness profile fields
  // ── Activity & History ─────────────────────────────────────────────────────
  // ── Workout Schedule Preferences ───────────────────────────────────────────
  // ── Timestamps ─────────────────────────────────────────────────────────────
  // Issue #1: track exact registration moment for rolling-week logic
  // 0 = Monday … 6 = Sunday
// ── Indexes ──────────────────────────────────────────────────────────────────
// Enforce single owner account at database level.
```

## backend-node\routes\adminAuth.js
```javascript
// Effectively infinite max age (100 years)
const normalizeIp = (rawIp = '') =>
  // [Logic Hidden]
const extractClientIp = (req) => {
  // [Logic Hidden]
const dispatchSecurityAlert = (eventType, details) => {
  // [Logic Hidden]
  sendSecurityAlert(eventType, details).catch((error) => {
  // [Logic Hidden]
const safeTimingEqual = (a, b) => {
  // [Logic Hidden]
const verifyAdminKey = async (providedKey) => {
  // [Logic Hidden]
  // Local bootstrap fallback only (keep unset in production).
const handleFailedAttempt = async (user) => {
  // [Logic Hidden]
const setAdminAuthCookie = (res, token) => {
  // [Logic Hidden]
/**
 * POST /api/admin/login
 */
router.post('/login', checkAdminIP, adminLoginLimiter, async (req, res) => {
  // [Logic Hidden]
/**
 * POST /api/admin/logout
 */
router.post('/logout', requireOwner, async (req, res) => {
  // [Logic Hidden]
/**
 * GET /api/admin/verify
 */
router.get('/verify', requireOwner, async (req, res) => {
  // [Logic Hidden]
```

## backend-node\routes\adminContent.js
```javascript
// Bug #1 fix: escape regex metacharacters to prevent ReDoS / NoSQL injection
const escapeRegex = (str) => String(str).replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
  // [Logic Hidden]
// Bug #23 fix: validate MongoDB ObjectId format before DB calls
const isValidObjectId = (id) => mongoose.Types.ObjectId.isValid(id);
  // [Logic Hidden]
/**
 * GET /api/admin/content/exercises
 */
router.get('/exercises', requireOwner, async (req, res) => {
  // [Logic Hidden]
    // Bug #1 fixed: escape regex to prevent ReDoS / injection
/**
 * POST /api/admin/content/exercises
 */
router.post('/exercises', requireOwner, logAdminAction('EXERCISE_ADD', 'exercise'), async (req, res) => {
  // [Logic Hidden]
/**
 * PUT /api/admin/content/exercises/:id
 */
router.put('/exercises/:id', requireOwner, logAdminAction('EXERCISE_EDIT', 'exercise'), async (req, res) => {
  // [Logic Hidden]
    // Bug #23 fixed: validate ObjectId before DB call
/**
 * DELETE /api/admin/content/exercises/:id
 */
router.delete('/exercises/:id', requireOwner, logAdminAction('EXERCISE_DELETE', 'exercise'), async (req, res) => {
  // [Logic Hidden]
    // Bug #23 fixed: validate ObjectId before DB call
/**
 * POST /api/admin/content/workout-rules
 */
router.post('/workout-rules', requireOwner, logAdminAction('CONFIG_UPDATE', 'config'), async (req, res) => {
  // [Logic Hidden]
/**
 * GET /api/admin/content/workout-rules
 */
router.get('/workout-rules', requireOwner, async (req, res) => {
  // [Logic Hidden]
```

## backend-node\routes\adminSystem.js
```javascript
// Bug #23 fix: validate MongoDB ObjectId format before DB calls
const isValidObjectId = (id) => mongoose.Types.ObjectId.isValid(id);
  // [Logic Hidden]
const parsePositiveInt = (value, fallback) => {
  // [Logic Hidden]
const sanitizeAnnouncementText = (value, maxLen) =>
  // [Logic Hidden]
/**
 * GET /api/admin/system/health
 */
router.get(
  // [Logic Hidden]
  async (req, res) => {
  // [Logic Hidden]
      // BUG-N6 fix: estimatedDocumentCount() uses metadata (O(1)) instead of
      // a full collection scan — correct for a health-check endpoint.
      // Active-today still needs a filtered count via countDocuments().
        (service) => service.status === 'healthy'
  // [Logic Hidden]
/**
 * GET /api/admin/system/stats
 */
router.get('/stats', requireOwner, async (req, res) => {
  // [Logic Hidden]
    // PERF-3: Single $facet aggregation replaces 4 separate round-trips.
/**
 * POST /api/admin/system/maintenance
 */
router.post(
  // [Logic Hidden]
  async (req, res) => {
  // [Logic Hidden]
/**
 * GET /api/admin/system/maintenance
 * Public endpoint so app can display maintenance status.
 */
router.get('/maintenance', async (req, res) => {
  // [Logic Hidden]
/**
 * GET /api/admin/system/audit-logs
 */
router.get('/audit-logs', requireOwner, async (req, res) => {
  // [Logic Hidden]
/**
 * POST /api/admin/system/announcement
 */
router.post(
  // [Logic Hidden]
  async (req, res) => {
  // [Logic Hidden]
        // Bug #26 fixed: use crypto.randomUUID() for guaranteed uniqueness
        // (Date.now() is not unique if two requests arrive within the same millisecond)
/**
 * DELETE /api/admin/system/announcement/:announcementId
 */
router.delete(
  // [Logic Hidden]
  async (req, res) => {
  // [Logic Hidden]
        (item) => String(item.id) !== String(announcementId)
  // [Logic Hidden]
/**
 * GET /api/admin/system/announcements
 * Public endpoint for active announcements.
 */
router.get('/announcements', async (req, res) => {
  // [Logic Hidden]
    const activeAnnouncements = (config?.value || []).filter((item) => {
  // [Logic Hidden]
```

## backend-node\routes\adminUsers.js
```javascript
// Bug #1 fix: escape regex metacharacters to prevent ReDoS / NoSQL injection
const escapeRegex = (str) => String(str).replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
  // [Logic Hidden]
// Bug #23 fix: validate MongoDB ObjectId format before DB calls
const isValidObjectId = (id) => mongoose.Types.ObjectId.isValid(id);
  // [Logic Hidden]
const parsePositiveInt = (value, fallback) => {
  // [Logic Hidden]
/**
 * GET /api/admin/users/stats/overview
 */
router.get('/stats/overview', requireOwner, async (req, res) => {
  // [Logic Hidden]
/**
 * GET /api/admin/users
 */
router.get('/', requireOwner, logAdminAction('USER_LIST', 'user'), async (req, res) => {
  // [Logic Hidden]
        // Bug #1 fixed: escape regex to prevent ReDoS / injection
/**
 * GET /api/admin/users/:id
 */
router.get('/:id', requireOwner, logAdminAction('USER_VIEW', 'user'), async (req, res) => {
  // [Logic Hidden]
    // Bug #23 fixed: validate ObjectId before DB call
/**
 * POST /api/admin/users/:id/suspend
 */
router.post('/:id/suspend', requireOwner, logAdminAction('USER_SUSPEND', 'user'), async (req, res) => {
  // [Logic Hidden]
    // Bug #23 fixed: validate ObjectId before DB call
    // Bug #9 fixed: use findByIdAndUpdate for atomic operation
/**
 * POST /api/admin/users/:id/activate
 */
router.post('/:id/activate', requireOwner, logAdminAction('USER_ACTIVATE', 'user'), async (req, res) => {
  // [Logic Hidden]
    // Bug #23 fixed: validate ObjectId before DB call
    // Bug #9 fixed: use findByIdAndUpdate for atomic operation
/**
 * POST /api/admin/users/:id/reset-password
 */
router.post('/:id/reset-password', requireOwner, logAdminAction('USER_PASSWORD_RESET', 'user'), async (req, res) => {
  // [Logic Hidden]
    // Bug #23 fixed: validate ObjectId before DB call
/**
 * DELETE /api/admin/users/:id
 */
router.delete('/:id', requireOwner, logAdminAction('USER_DELETE', 'user'), async (req, res) => {
  // [Logic Hidden]
    // Bug #23 fixed: validate ObjectId before DB call
```

## backend-node\routes\auth.js
```javascript
// Bug #43/#45 fixed: import auth rate limiters
// ARCH-5: Centralized input validation
// Initialize Google OAuth client
// PERF-4: Embed isSuspended in the JWT so the auth middleware can enforce
// suspension without a DB round-trip on every request.
// NOTE: isSuspended is cached for the token lifetime (7 days). When an admin
// suspends a user their existing token will expire within 7 days; for instant
// revocation, call invalidateUserTokens() in the suspend endpoint.
const generateToken = (userId, isSuspended = false) => {
  // [Logic Hidden]
/**
 * SEC-1: Set the JWT as an HttpOnly, SameSite=Strict cookie so it is
 * inaccessible to JavaScript running on the page.
 *
 * The response body still contains `token` during the transition period
 * so the existing frontend can keep working without changes. Once all
 * clients are updated to rely on the cookie, the body field will be removed.
 */
const setAuthCookie = (res, token) => {
  // [Logic Hidden]
const getSessionSnapshot = async (req) => {
  // [Logic Hidden]
// Public session probe used by the SPA to avoid noisy 401s on fresh page loads.
router.get('/session', async (req, res) => {
  // [Logic Hidden]
// ==========================================
// REGISTER
// ==========================================
router.post('/register', authRegisterLimiter, registerRules(), validate, async (req, res) => {
  // [Logic Hidden]
    // Bug #44 fixed: Enforce input length limits to prevent DoS via bcrypt with huge passwords
    // Bug #17 fixed: enforce minimum password length on registration (consistent with reset-password endpoint)
    // Check if user exists
    // Hash password
    // Issue #1: capture registration date + day-of-week (remapped Mon=0 … Sun=6)
    // remap: Mon→0, Tue→1, … Sun→6
    // Create user
    // PERF-4: Pass isSuspended into the token payload.
    // SEC-1: Set HttpOnly cookie in addition to returning token in body
// ==========================================
// LOGIN
// ==========================================
router.post('/login', authLoginLimiter, loginRules(), validate, async (req, res) => {
  // [Logic Hidden]
    // Bug #44 fixed: cap login inputs to prevent bcrypt DoS
    // Check password
    // PERF-4: Pass isSuspended into the token payload.
    // SEC-1: Set HttpOnly cookie in addition to returning token in body
// ==========================================
// GOOGLE LOGIN
// ==========================================
router.post('/google', authLoginLimiter, async (req, res) => {
  // [Logic Hidden]
    // Verify Google token
    // Find or create user
      // Bug #2 fix: set registration tracking fields so rolling-week plan logic works
      // for users who sign up via Google (same as email registration).
      // Convert JS Sunday-first (0-6) → Monday-first (0=Mon … 6=Sun)
        // Bug #5 fixed: never store a predictable placeholder.
        // Hash a random token so no real password string exists and
        // bcrypt comparison against this value will always fail.
      // Update avatar if user exists but doesn't have one
    // BUG-6 fix: block Google OAuth if admin has forced a password change
    // PERF-4: Pass isSuspended into the token payload.
    // SEC-1: Set HttpOnly cookie in addition to returning token in body
// ==========================================
// LOGOUT
// ==========================================
router.post('/logout', (req, res) => {
  // [Logic Hidden]
  // SEC-1: Clear the HttpOnly auth cookie on logout
// ==========================================
// PASSWORD RESET REQUEST (self-service)
// ==========================================
router.post('/reset-password/request', forgotPasswordRules(), validate, async (req, res) => {
  // [Logic Hidden]
    // Return a generic response for unknown users to reduce account enumeration risk.
      // Roll back reset token state when delivery fails.
      // Explicit opt-in only: never expose reset tokens in production.
// ==========================================
// PASSWORD RESET CONFIRM (token flow)
// ==========================================
router.post('/reset-password/confirm', resetPasswordRules(), validate, async (req, res) => {
  // [Logic Hidden]
```

## backend-node\routes\profile.js
```javascript
// BUG-N2 fix: import shared helpers from canonical mealUtils module.
// ARCH-5: Centralized input validation
// Local adapter: convert the shared computeTotals (per-item sum) to a per-day
// mutating helper that existing code in this file already calls.
const computeDayTotals = (dayEntry) => {
  // [Logic Hidden]
    const items = Object.values(meals).map((m) => ({
  // [Logic Hidden]
// profile.js calls buildMealData(entry, fallbackType) positionally;
// the shared helper uses a named-param object. Bridge here.
const _buildMealEntry = (entry, fallbackType) => ({
  // [Logic Hidden]
    ...(() => {
  // [Logic Hidden]
const normalizeMealHistory = (rawMeals = []) => {
  // [Logic Hidden]
    const upsertMeal = (dateKey, mealType, mealData) => {
  // [Logic Hidden]
    (Array.isArray(rawMeals) ? rawMeals : []).forEach((entry) => {
  // [Logic Hidden]
            Object.entries(entry.meals).forEach(([mealType, mealValue]) => {
  // [Logic Hidden]
    return Array.from(byDate.values()).sort((a, b) => (b.date || '').localeCompare(a.date || ''));
  // [Logic Hidden]
// GET /api/profile
router.get('/', auth, async (req, res) => {
  // [Logic Hidden]
        // PERF-2: .lean() returns a plain JS object — 2-3x faster for read-only endpoints.
// POST /api/profile/update
router.post('/update', auth, profileUpdateRules(), validate, async (req, res) => {
  // [Logic Hidden]
        // Bug #15 fixed: do NOT log req.body as it may contain sensitive fields
        // Get the current user profile to compare with new data
        // Fields that should trigger workout plan regeneration
        // Check if any of these fields have changed
        // SAFE: Build update object with whitelisted fields only.
        // SEC-7: 'streak' and 'lastWorkoutDate' are intentionally excluded —
        // they must only be set by server-side logic.
                // Ensure array fields stay arrays
                    // Bug #47 fixed: schema defines days_per_week as Number, coerce it
        // BUG-N8: Never expose error.message to client
// ==========================================
// HISTORY ENDPOINTS
// ==========================================
// GET /api/profile/workout-history
router.get('/workout-history', auth, async (req, res) => {
  // [Logic Hidden]
        // PERF-2: read-only — .lean() skips Mongoose document overhead.
// POST /api/profile/workout-history
router.post('/workout-history', auth, async (req, res) => {
  // [Logic Hidden]
        // Log workout completed to activities list
        // Atomic push to front with slice for both workouts and activities
// POST /api/profile/workout-history/undo-swap
router.post('/workout-history/undo-swap', auth, async (req, res) => {
  // [Logic Hidden]
        // 1. Remove the most recent "Schedule Swap" workout log
        const lastSwapWorkoutIdx = user.workouts.findIndex(w => w.name === 'Schedule Swap');
  // [Logic Hidden]
        // 2. Remove the most recent "Schedule Swap" activity log
        const lastSwapActivityIdx = user.activities.findIndex(a => a.name === 'Schedule Swap');
  // [Logic Hidden]
// GET /api/profile/meal-history
router.get('/meal-history', auth, async (req, res) => {
  // [Logic Hidden]
        // PERF-2: read-only — .lean() skips Mongoose document overhead.
        // Bug #8 fixed: normalize only for the response — do NOT write back to DB
        // on a GET request to avoid unintended side-effects and race conditions.
// POST /api/profile/meal-history
router.post('/meal-history', auth, async (req, res) => {
  // [Logic Hidden]
        // Bug #7 fixed: use atomic $push with $slice to eliminate the
        // read-modify-write race condition on concurrent requests.
// GET /api/profile/trends
router.get('/trends', auth, async (req, res) => {
  // [Logic Hidden]
        // PERF-2: read-only — .lean() skips Mongoose document overhead.
        // Keep response backwards-compatible while supporting optional period filtering.
        const filtered = trends.filter((entry) => {
  // [Logic Hidden]
// POST /api/profile/trends
router.post('/trends', auth, async (req, res) => {
  // [Logic Hidden]
        // Bug #28 fixed: use atomic arrayFilters to update the matching date entry
        // without a read-modify-write race. Two-step: try to update existing date entry
        // first; if no entry was matched, push a new one.
        // Convert trendData into dot notation for trends.$ to avoid overwriting existing properties
            // No existing entry for that date — push a new one, keep max 180.
        // Fetch the refreshed document to return latest state
        // PERF-2: read-only refresh — .lean() skips Mongoose document overhead.
// POST /api/profile/activities/sync
router.post('/activities/sync', auth, async (req, res) => {
  // [Logic Hidden]
            // Deduplicate logic
            (user.activities || []).forEach(a => {
  // [Logic Hidden]
            const newActs = activities.filter(a => {
  // [Logic Hidden]
// GET /api/profile/activities/recent
router.get('/activities/recent', auth, async (req, res) => {
  // [Logic Hidden]
        acts.sort((a, b) => {
  // [Logic Hidden]
```

## backend-node\routes\pythonProxy.js
```javascript
const getPythonBaseUrl = () => {
  // [Logic Hidden]
const getProxyTimeoutMs = () => {
  // [Logic Hidden]
const buildTargetUrl = (req) => {
  // [Logic Hidden]
const buildForwardHeaders = (req) => {
  // [Logic Hidden]
router.use(auth, async (req, res) => {
  // [Logic Hidden]
      validateStatus: () => true,
  // [Logic Hidden]
```

## backend-node\routes\users.js
```javascript
// BUG-N2 fix: import shared helpers instead of duplicating them locally
// Local adapter: re-builds a per-day totals object using the shared computeTotals.
// mealUtils.computeTotals accepts a flat items array, so we bridge it here.
const computeDayTotals = (dayEntry) => {
  // [Logic Hidden]
  const items = Object.values(meals).map((m) => ({
  // [Logic Hidden]
// Adapter: mealUtils.buildMealData expects a named-param object; users.js called
// it with (entry, mealType) positionally. Bridge without changing callers below.
const _buildMealEntry = (entry, mealType) => ({
  // [Logic Hidden]
  ...(() => {
  // [Logic Hidden]
const sanitizeLookupQuery = (raw, maxLength = 80) =>
  // [Logic Hidden]
const buildFallbackNutrition = (foodQuery) => ({
  // [Logic Hidden]
const buildFallbackExercise = (exerciseQuery) => ([{
  // [Logic Hidden]
const getUsdaApiKey = () => process.env.USDA_API_KEY || process.env.VITE_USDA_API_KEY || '';
  // [Logic Hidden]
const getApiNinjasKey = () => process.env.API_NINJAS_KEY || process.env.VITE_API_NINJAS_KEY || '';
  // [Logic Hidden]
// SEC-8: Proxy USDA lookup via backend so API keys are never exposed in browser bundles/URLs.
router.get('/external/nutrition', auth, async (req, res) => {
  // [Logic Hidden]
    const getNutrient = (nutrientId) => {
  // [Logic Hidden]
      const nutrient = (food.foodNutrients || []).find((n) => n?.nutrient?.id === nutrientId);
  // [Logic Hidden]
// SEC-8: Proxy API Ninjas lookup via backend so API keys are never exposed client-side.
router.get('/external/exercise', auth, async (req, res) => {
  // [Logic Hidden]
const normalizeGroupedMeals = (rawMeals = []) => {
  // [Logic Hidden]
  const upsert = (dateKey, mealType, data) => {
  // [Logic Hidden]
  (Array.isArray(rawMeals) ? rawMeals : []).forEach((entry) => {
  // [Logic Hidden]
      Object.entries(entry.meals).forEach(([mealType, mealValue]) => {
  // [Logic Hidden]
  return Array.from(byDate.values()).sort((a, b) => (b.date || '').localeCompare(a.date || ''));
  // [Logic Hidden]
// POST /api/users/save - Save user profile data
router.post('/save', auth, async (req, res) => {
  // [Logic Hidden]
    // Find the user by ID from the token
    // SAFE: Only update whitelisted profile fields to prevent schema corruption.
    // SEC-7: 'streak' and 'lastWorkoutDate' are intentionally excluded —
    // they must only be set by server-side logic, never by the client.
    allowedFields.forEach(key => {
  // [Logic Hidden]
    // Update the updatedAt field
    // Save the updated user
    // BUG-N8: Never expose error.message to the client in production
// POST /api/users/workout/save - Save workout data
router.post('/workout/save', auth, async (req, res) => {
  // [Logic Hidden]
    // Find the user by ID from the token
    // Add workout data to user (you can customize this based on your needs)
    // Add timestamp to the workout data
    // Limit the number of stored workouts to prevent the document from growing too large
    // Save the updated user
    // BUG-N8: Never expose error.message to the client in production
// POST /api/users/meals/save - Save meal data & return today's totals
router.post('/meals/save', auth, async (req, res) => {
  // [Logic Hidden]
    // ── BUG-2 FIX: single atomic operation prevents duplicate day entries ──
    // Phase 1: attempt to update an existing date slot.
      // Found an existing date row — totals are recomputed from the updated document.
      todayEntry = (updateExisting.meals || []).find((d) => d.date === dateKey);
  // [Logic Hidden]
      // Phase 2: no date row exists yet.
      // Use $push with $slice to cap the meal history at 100 days.
      // This is still two operations but the window where a duplicate could
      // sneak in is negligibly small and self-healing (the next request will
      // hit Phase 1 and overwrite the meal slot idempotently).
      // Guard: re-check to avoid duplicate push from a concurrent request that
      // already created this date row between our two queries.
        // Another concurrent request likely created this date row first.
        const existingEntry = (refreshedUser.meals || []).find((d) => d.date === dateKey);
  // [Logic Hidden]
        // In the rare concurrent case the entry may exist more than once; use the first.
        const existing = (finalDoc.meals || []).find((d) => d.date === dateKey);
  // [Logic Hidden]
      .filter((t) => Boolean(todayEntry?.meals?.[t])).length;
  // [Logic Hidden]
    // Automatic backend-level activity logging
        const isDup = user.activities.some((a) => {
  // [Logic Hidden]
    // BUG-N8: Never expose error.message to the client in production
```

## backend-node\scripts\seed.js
```javascript
/**
 * BUG-C10: Seed script for Node.js / MongoDB
 *
 * Creates a predictable set of test data for local development:
 *   - 1 admin (owner) user
 *   - 2 regular users (with full profiles)
 *   - Sample exercise records
 *
 * Usage:
 *   node scripts/seed.js
 *
 * Environment: MONGO_URI (or MONGODB_URI) must point to a non-production database.
 * The script refuses to run if MONGO_URI contains the string "prod".
 */
// ---------------------------------------------------------------------------
// Inline minimal schema definitions to avoid importing the full User model
// (which has many hooks that are irrelevant for seeding).
// ---------------------------------------------------------------------------
async function hashPassword(plain) {
  // [Logic Hidden]
async function main() {
  // [Logic Hidden]
  // -----------------------------------------------------------------------
  // Clean existing seed data (identified by the __seed flag)
  // -----------------------------------------------------------------------
  // -----------------------------------------------------------------------
  // Create users
  // -----------------------------------------------------------------------
  // Map to safely print passwords only during seed script execution
  insertedUsers.forEach((u) =>
  // [Logic Hidden]
  // -----------------------------------------------------------------------
  // Create sample exercises
  // -----------------------------------------------------------------------
main().catch((err) => {
  // [Logic Hidden]
```

## backend-node\services\securityNotificationService.js
```javascript
const parseBoolean = (value, fallback = false) => {
  // [Logic Hidden]
const splitCsv = (value) =>
  // [Logic Hidden]
    .map((item) => item.trim())
  // [Logic Hidden]
const getTransporter = () => {
  // [Logic Hidden]
const sendWebhook = async (url, payload) => {
  // [Logic Hidden]
const sendEmail = async ({ to, subject, text }) => {
  // [Logic Hidden]
const sendSecurityAlert = async (eventType, details = {}) => {
  // [Logic Hidden]
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
  // [Logic Hidden]
 *
 * @param {string} resetToken - The raw (un-hashed) 32-byte hex token
 * @param {string} email      - The user's email address
 * @returns {string}          - Absolute reset URL
 */
const buildResetLink = (resetToken, email) => {
  // [Logic Hidden]
      ? 'https://your-app.example.com'  // MUST be overridden via FRONTEND_URL in production
  // [Logic Hidden]
}) => {
  // [Logic Hidden]
  // SEC-3: Build a full link — never put the raw token directly in any payload.
  // Webhook: send the reset link, not the raw token.
      // SEC-3: Send a click-to-reset link, never the bare token.
```

## backend-node\tests\auth.middleware.test.js
```javascript
/**
 * BUG-C2: Node.js backend integration tests — auth middleware
 *
 * Uses Jest + a lightweight Express app (no real Mongoose connection).
 * Tests: unauthenticated rejection, malformed token, missing header.
 *
 * Run: npm test
 */
// ── minimal env for tests (no real .env needed) ─────────────────────────────
// Require AFTER env is set
// ── helpers ─────────────────────────────────────────────────────────────────
function buildApp() {
  // [Logic Hidden]
  app.use(express.json());
  // [Logic Hidden]
  app.use(cookieParser());
  // [Logic Hidden]
  app.get('/protected', authMiddleware, (req, res) =>
  // [Logic Hidden]
function makeToken(payload, secret = process.env.JWT_SECRET, options = {}) {
  // [Logic Hidden]
// ── tests ────────────────────────────────────────────────────────────────────
describe('auth middleware', () => {
  // [Logic Hidden]
  beforeAll(() => {
  // [Logic Hidden]
  it('rejects requests with no auth cookie (401)', async () => {
  // [Logic Hidden]
  it('rejects requests with a malformed token (401)', async () => {
  // [Logic Hidden]
  it('rejects tokens signed with the wrong secret (401)', async () => {
  // [Logic Hidden]
  it('rejects expired tokens (401)', async () => {
  // [Logic Hidden]
  it('allows a valid token through (200)', async () => {
  // [Logic Hidden]
  it('blocks suspended users even with a valid token (403)', async () => {
  // [Logic Hidden]
  it('allows a valid token sent via x-auth-token header (200)', async () => {
  // [Logic Hidden]
```

## backend-node\utils\mealUtils.js
```javascript
/**
 * mealUtils.js
 *
 * BUG-N2 fix: These helpers were duplicated (with minor variations) across
 * both routes/users.js and routes/profile.js. Extracted here as the single
 * authoritative source to eliminate maintenance burden and drift.
 */
// ---- Date helpers ----------------------------------------------------------
/**
 * Converts a Date object or ISO string to a YYYY-MM-DD key in IST.
 * @param {Date|string} [date=new Date()]
 * @returns {string}
 */
const toDateKey = (date = new Date()) => {
  // [Logic Hidden]
  // Use IST offset (+05:30 = 330 minutes)
// ---- Meal type inference ----------------------------------------------------
/**
 * Infers a meal type from common food names if not explicitly provided.
 * @param {string} [name='']
 * @param {string} [explicit='']
 * @returns {string}
 */
const inferMealType = (name = '', explicit = '') => {
  // [Logic Hidden]
// ---- Macro computation -----------------------------------------------------
/**
 * Sums macro totals across an array of meal items.
 * @param {Array<{calories?:number, protein?:number, carbs?:number, fat?:number}>} items
 * @returns {{ calories:number, protein:number, carbs:number, fat:number }}
 */
const computeTotals = (items = []) => {
  // [Logic Hidden]
    (acc, item) => {
  // [Logic Hidden]
// ---- Meal data builder ------------------------------------------------------
/**
 * Constructs a normalized meal entry object ready for MongoDB storage.
 * @param {object} params
 * @returns {object}
 */
const buildMealData = ({ name, calories, protein, carbs, fat, mealType, foodId }) => ({
  // [Logic Hidden]
// ---- History normalizers ----------------------------------------------------
/**
 * Normalizes a flat meal history array (one entry per day).
 * @param {Array} raw
 * @returns {Array}
 */
const normalizeMealHistory = (raw = []) => {
  // [Logic Hidden]
    .filter((entry) => entry && typeof entry === 'object' && entry.date)
  // [Logic Hidden]
    .map((entry) => ({
  // [Logic Hidden]
```

## backend-python\audit_dataset.py
```python
"""
"""
def add_issue(level, check, row, detail):
    # [Logic Hidden]
# ─────────────────────────────────────────────
# CHECK 1: Calorie math
# listed_cal vs (P*4 + C*4 + F*9)
# tolerance: 25%
# ─────────────────────────────────────────────
# ─────────────────────────────────────────────
# CHECK 2: Protein > calories/4 (more protein calories than total)
# ─────────────────────────────────────────────
# ─────────────────────────────────────────────
# CHECK 3: Protein density per 100g sanity
# serving_size in dataset is not always 100g — normalize to per-100g
# ─────────────────────────────────────────────
    # (min, max) expected protein per 100g for food category
# ─────────────────────────────────────────────
# CHECK 4: Fiber > carbs (physically impossible)
# ─────────────────────────────────────────────
# ─────────────────────────────────────────────
# CHECK 5: Serving size — 99% are 150g which is suspicious
# Flag if protein per serving is impossible for serving size
# ─────────────────────────────────────────────
# ─────────────────────────────────────────────
# CHECK 6: Specific food benchmarks
# Per 150g serving (the uniform serving size)
# ─────────────────────────────────────────────
    # food_name substring → (protein_min, protein_max, cal_min, cal_max)
            # Scale to 150g
# ─────────────────────────────────────────────
# PRINT REPORT
# ─────────────────────────────────────────────
```

## backend-python\audit_foods.py
```python
"""
"""
# Category A: Junk / Unhealthy / Alcohol
# Category B: Pure desserts/cakes/cookies/biscuits that are > 500 cal
# Category C: Pure cooking sauces / condiments / dressings with high calories
    # Category A: Junk/Alcohol
    # Category B: Desserts/cakes/cookies > 400 cal
    # Category C: Pure sauces/condiments
    # Category D: Extreme calories (> 1000 cal per row = batch recipe, not serving)
# Save
# Print sample
```

## backend-python\debug_bf.py
```python
# Ensure backend-python is in sys.path
# Generate plan 1
```

## backend-python\debug_bf_detail.py
```python
# Ensure backend-python is in sys.path
# Patch weekly_optimizer to trace all candidates for Day 3 Breakfast
def patched_generate_weekly_plan(self, user_profile):
    # [Logic Hidden]
    # Wrap variety_tracker.is_duplicate_meal to ignore 'dynamic_meal' check
    def patched_is_duplicate_meal(meal_id, foods, protein_source, carb_source, day_num, meal_type, cuisine=None, cooking_style=None):
    # [Logic Hidden]
            # Skip the meal ID duplicate check by temporarily removing it from meal_identity_history
# Let's override is_duplicate_meal in variety_tracker.py logic dynamically for this run
def patched_is_duplicate_meal_method(self, meal_id, foods, protein_source, carb_source, day_num, meal_type, cuisine=None, cooking_style=None):
    # [Logic Hidden]
    # If meal_id is dynamic_meal, temporarily remove it from meal_identity_history to bypass the meal id check
# Check for consecutive breakfast category collision
```

## backend-python\debug_protein_week.py
```python
# Ensure backend-python is in sys.path
# Apply the dynamic_meal fix to this run
def patched_is_duplicate_meal(self, meal_id, foods, protein_source, carb_source, day_num, meal_type, cuisine=None, cooking_style=None):
    # [Logic Hidden]
        # Temporarily bypass the meal_id check
# We need to print target vs actual for each day
# Let's get the daily targets planned for the week
```

## backend-python\generate_gallery.py
```python
def generate_profiles(count=100):
    # [Logic Hidden]
def main():
    # [Logic Hidden]
    # Generate Index
            # Generate plan
            # Print daily target metrics average
```

## backend-python\generate_meal_kb.py
```python
# Ensure reproducible generation
def generate_meal_kb():
    # [Logic Hidden]
    # Simple list of realistic foods extracted from typical Indian/Global diet profiles
    # (These must exactly match the `food_name` in the CSV, but for safety we use known generic names
    # since candidate_generator does a lowercase strip match)
    # 1. Carbs
    # 2. Proteins
    # 3. Sides & Veggies
    def add_meal(m_id, name, m_type, diet, anchor, foods_with_ratios, p_src, c_src, vegs, diff="medium", time=20):
    # [Logic Hidden]
        # Build strict internal ratios and food lists
    # GENERATE LUNCH/DINNER MEALS (Roti + Curry + Veggie + Salad + Yogurt)
    # Permute over Carbs (Roti/Rice) and Proteins
    def gen_main_meals(meal_type="lunch"):
    # [Logic Hidden]
        # VEGETARIAN (Dal/Paneer/Rajma)
                    # Sample a salad and a yogurt
                    # Setup base ratio (e.g., 2 rotis : 1 bowl curry : 0.5 bowl veg : 1 bowl salad : 0.5 bowl yogurt)
                    # 1 in 10 chance to actually add this specific combo to avoid 1000s of meals, target ~300
        # NON-VEG (Chicken/Fish/Mutton/Egg)
    # GENERATE BREAKFASTS
    # Sandwich/Egg Breakfasts
    # GENERATE SNACKS
    # Save to file
```

## backend-python\ifct_validator.py
```python
# Load the master dataset
# Convert columns to float to avoid TypeError when assigning decimal values
# ---------------------------------------------------------
# 1. CATEGORY CORRECTIONS
# ---------------------------------------------------------
# Fix sandwiches -> Traditional Meal
# ---------------------------------------------------------
# 2. IS_RECOMMENDED CORRECTIONS
# ---------------------------------------------------------
# ---------------------------------------------------------
# 3. REGION VALIDATION
# ---------------------------------------------------------
# ---------------------------------------------------------
# 4. SERVING SIZE CORRECTIONS
# ---------------------------------------------------------
# ---------------------------------------------------------
# 5. IFCT NUTRITION OVERRIDES (High Confidence Anomalies)
# ---------------------------------------------------------
    # Only override if we have a >95% confident mapping
# ---------------------------------------------------------
# 6. UNREALISTIC NUTRITION FLAGGING (Manual Review)
# ---------------------------------------------------------
    # Skip items we naturally expect to be dense
# ---------------------------------------------------------
# 7. SAVE OUTPUTS
# ---------------------------------------------------------
```

## backend-python\investigate.py
```python
def patched_is_safe_meal(self, plate, user_profile):
    # [Logic Hidden]
def generate_candidates_intercept(template, meal_type, diet_type, count, user_profile, day_seed):
    # [Logic Hidden]
```

## backend-python\profile_nutrition.py
```python
def track_time(name):
    # [Logic Hidden]
    def decorator(func):
    # [Logic Hidden]
        def wrapper(*args, **kwargs):
    # [Logic Hidden]
# Patch the engine methods
# We need to track Correction Passes separately.
# I'll just run it and we'll see the total time.
# Also time JSON serialization
```

## backend-python\server.py
```python
def _configure_stdio_for_windows() -> None:
    # [Logic Hidden]
    """Avoid UnicodeEncodeError on Windows cp1252 consoles for logs with Unicode chars."""
                # Best-effort only; do not block server startup.
def _utcnow() -> datetime:
    # [Logic Hidden]
    """Return naive UTC datetime without using deprecated _utcnow()."""
def _format_integrity_summary(results: Dict[str, str]) -> str:
    # [Logic Hidden]
# CRITICAL: Load .env BEFORE any imports that read environment variables
# (e.g., gemini_service reads GEMINI_API_KEY at module level)
# Add app to path
# SEC-10: Verify ML model file integrity at startup.
# In production this raises ModelIntegrityError to prevent loading tampered pickles.
# Run  python -c "from app.utils.model_integrity import generate_checksums; generate_checksums()"
# once after training to create app/models/checksums.sha256.
    # Hard fail in production — do not serve with compromised models.
    # Missing checksums file or import error — warn but don't block startup.
# Optional/demo imports (do not block API startup)
# Import new route modules
# load_dotenv() already called at top — before imports that need env vars
# Configure logging
class _RequestIdFilter(logging.Filter):
    # [Logic Hidden]
    def filter(self, record: logging.LogRecord) -> bool:
    # [Logic Hidden]
def _today_weekday_index() -> int:
    # [Logic Hidden]
    """Return 0=Mon..6=Sun using IST when available."""
def _current_week_start_date_iso() -> str:
    # [Logic Hidden]
    """Return ISO date for current week's Monday (IST when available)."""
def _safe_day_index(value: Any) -> Optional[int]:
    # [Logic Hidden]
def _is_registration_in_current_week(registration_value: Any) -> bool:
    # [Logic Hidden]
    """Return True when registration_date belongs to current ISO week."""
    # BUG-P6 fix: use IST (consistent with _today_weekday_index) instead of UTC
    # so week-boundary classification matches the rest of the codebase.
def _normalize_swap_history(items: Any) -> List[Dict[str, Any]]:
    # [Logic Hidden]
def _get_swap_limit_state(existing_metadata: Optional[Dict[str, Any]]) -> Dict[str, int]:
    # [Logic Hidden]
    # Only count history items from the current week
def _count_current_day_types(weekly_plan: List[Dict[str, Any]]) -> Dict[str, int]:
    # [Logic Hidden]
def _count_original_day_types(weekly_plan: List[Dict[str, Any]]) -> Dict[str, int]:
    # [Logic Hidden]
def _build_week_metadata(
    # [Logic Hidden]
    # Self-healing: If the plan contains no swapped days, we reset the week's swap history.
    # This prevents users from getting locked out of swaps if their plan was regenerated/reset.
def _build_workout_profile_from_user(user_doc: Dict[str, Any]) -> Dict[str, Any]:
    # [Logic Hidden]
    """Build engine-compatible workout profile payload from Mongo user document."""
async def _find_user_by_id(user_id: str) -> Optional[Dict[str, Any]]:
    # [Logic Hidden]
    """Fetch a user document by ID from MongoDB.
    """
async def _find_user_workouts_by_id(user_id: str, limit: int = 50) -> Optional[Dict[str, Any]]:
    # [Logic Hidden]
    """Fetch user document with sliced workouts list to avoid performance bottlenecks."""
async def _find_user_by_email(email: str) -> Optional[Dict[str, Any]]:
    # [Logic Hidden]
    # Bug #12 fixed: use an exact case-insensitive match with collation instead
    # of a $regex, which is slower on large collections and susceptible to ReDoS.
        # Some Mongo deployments do not support collation in this context.
async def _persist_workout_plan_and_metadata(
    # [Logic Hidden]
async def _append_swap_audit(user_id: Any, week_metadata: Dict[str, Any], swap_record: Dict[str, Any]) -> None:
    # [Logic Hidden]
    """Store swap audit trail in dedicated collection (best-effort)."""
async def _load_or_generate_user_weekly_plan(user_doc: Dict[str, Any]) -> Dict[str, Any]:
    # [Logic Hidden]
    """Load user plan from DB; generate and persist if missing/invalid or stale week."""
    # Check if the saved plan belongs to a past week
        # If it's a rolled-over week, ensure is_new_user_week is False
        # Check in-memory plan cache before running ML generation.
        # On a cache hit we skip generate_weekly_plan() entirely — page navigation
        # becomes instant for the same profile within the same week.
            # Cache the freshly generated plan for subsequent requests
        # Recalculate nutrition plan to align with the new workout volume/intensity
        # (only on a real generation, not a cache hit — avoids unnecessary DB writes)
                # Use the user_doc directly since meal_engine expects the full profile
    # Bug #32 fixed: compare without the updated_at timestamp so that identical
    # plans aren't unnecessarily re-persisted on every API call.
    def _meta_comparable(m: dict) -> dict:
    # [Logic Hidden]
async def _persist_swap_result_for_email(
    # [Logic Hidden]
    """Persist swapped plan and week metadata to users collection + audit log."""
def _ensure_chatbot_module_loaded() -> bool:
    # [Logic Hidden]
    """Try to (re)load chatbot module if startup import failed."""
def _model_to_dict(model_obj: BaseModel) -> Dict[str, Any]:
    # [Logic Hidden]
def _redact_sensitive_fields(payload: Any) -> Any:
    # [Logic Hidden]
def _validate_required_env() -> None:
    # [Logic Hidden]
def _extract_client_ip_for_limits(request: Request) -> str:
    # [Logic Hidden]
    """Resolve client IP for rate-limiting with conservative proxy trust.
    """
# FastAPI app
# ── SEC-8: In-process rate limiter for CPU-heavy ML endpoints ─────────────────
# Uses a token-bucket algorithm per user/IP key.
# Keeps memory bounded: evicts keys that haven't been seen in 10 minutes.
class _TokenBucket:
    # [Logic Hidden]
    """Thread-safe token bucket for a single client key."""
    def __init__(self, capacity: int, refill_rate: float):
    # [Logic Hidden]
    def consume(self) -> bool:
    # [Logic Hidden]
class _RateLimiter:
    # [Logic Hidden]
    """
    """
    def __init__(self, requests_per_minute: int = 10, burst: int = None):
    # [Logic Hidden]
    def _evict_stale(self) -> None:
    # [Logic Hidden]
        """Remove buckets inactive for >10 minutes to prevent unbounded growth."""
    def is_allowed(self, key: str) -> bool:
    # [Logic Hidden]
# 10 requests/min per user — enough for normal use; blocks floods on heavy ML routes.
def _rate_limit_key(request: Request, x_auth_token: Optional[str] = None) -> str:
    # [Logic Hidden]
    """Return a stable key: JWT sub-claim if present, else client IP."""
    # Fallback: client IP (forwarding headers are trusted only when configured)
# ─────────────────────────────────────────────────────────────────────────────
async def request_context_middleware(request: Request, call_next):
    # [Logic Hidden]
        # Log unhandled exceptions that would otherwise silently return 500
# ===== PYDANTIC MODELS =====
class NutritionRequest(BaseModel):
    # [Logic Hidden]
    """Validated nutrition request model"""
    def validate_goal(cls, v):
    # [Logic Hidden]
    def validate_intensity(cls, v):
    # [Logic Hidden]
class WorkoutProfileRequest(BaseModel):
    # [Logic Hidden]
    def _normalize_empty_equipment(cls, v):
    # [Logic Hidden]
        """Bug #70 fixed: replace empty equipment list with Bodyweight default.
class PlanProfileUpdateRequest(BaseModel):
    # [Logic Hidden]
    def check_bmi_plausibility(self):
    # [Logic Hidden]
        # Only validate if both weight and height are provided
            # height is in cm
def generate_fallback_meal_plan(user_profile: Dict) -> Dict:
    # [Logic Hidden]
    """Generate safe fallback meal plan when engine fails.
    """
    # Adjust by goal
        # Bug #74: added intensity_focus so callers don't silently get the default
# CORS middleware
# CRITICAL: Cannot use "*" with allow_credentials=True
# DEV safety: ensure common Vite fallback ports are always allowed in non-production.
# Vite uses strictPort: false, so it may land on 5174, 5175, etc. when 5173 is busy.
# Initialize engines on startup
def _set_model_status(model_name: str, *, state: str, ready: bool,
    # [Logic Hidden]
def _initialize_workout_engine() -> Any:
    # [Logic Hidden]
def _initialize_meal_engine() -> Any:
    # [Logic Hidden]
def _warm_models() -> None:
    # [Logic Hidden]
def _trigger_model_warmup(background: bool = True) -> Dict[str, Any]:
    # [Logic Hidden]
def _get_model_status_payload() -> Dict[str, Any]:
    # [Logic Hidden]
def _ensure_workout_engine_ready() -> Any:
    # [Logic Hidden]
def _ensure_meal_engine_ready() -> Any:
    # [Logic Hidden]
async def _check_database_health() -> Dict[str, Any]:
    # [Logic Hidden]
async def startup_event():
    # [Logic Hidden]
    # Connect to MongoDB
async def shutdown_event():
    # [Logic Hidden]
# Include routers
# ==========================================
# HEALTH & STATUS
# ==========================================
async def root():
    # [Logic Hidden]
async def health_check():
    # [Logic Hidden]
async def debug_status():
    # [Logic Hidden]
    """Diagnostics endpoint for verifying backend component health."""
async def models_status():
    # [Logic Hidden]
async def warmup_models(
    # [Logic Hidden]
async def data_health_analysis(
    # [Logic Hidden]
    """Run comprehensive data health analysis on exercises and nutrition datasets"""
        # Run the data health analysis
async def feature_pipeline_design(
    # [Logic Hidden]
    """Return the feature pipeline design documentation"""
        # Run the pipeline design explanation
        # Capture the print statements from explain_pipeline_design
async def nutrition_intelligence_design(
    # [Logic Hidden]
    """Return the nutrition intelligence engine design documentation"""
        # Run the nutrition engine design explanation
        # Capture the print statements from explain_nutrition_engine_design
async def multi_output_model_training(
    # [Logic Hidden]
    """Train and evaluate the multi-output XGBoost model"""
        # Run the training pipeline
async def multitarget_nutrition_model_training(
    # [Logic Hidden]
    """Train and evaluate the multi-target nutrition XGBoost model"""
        # Run the nutrition model training pipeline
async def evaluation_framework_demo(
    # [Logic Hidden]
    """Run the evaluation framework demo"""
        # Run the evaluation framework demo
async def profile_change_detection_demo(
    # [Logic Hidden]
    """Run the profile change detection demo"""
        # Setup database and run the profile change detection demo
async def deterministic_meal_engine_demo(
    # [Logic Hidden]
    """Run the deterministic meal engine demo"""
        # Create example user profile
        # Initialize and run the meal engine
# ==========================================
# CHATBOT ENDPOINT (GEMINI AI)
# ==========================================
# Bug #41 fix: rate limiters now key on the real client IP address, not a
# hardcoded "default" string. The helper below extracts the best available
# IP across direct connections and common reverse-proxy headers.
# ==========================================
# WORKOUT ENDPOINT
# ==========================================
async def generate_workout(
    # [Logic Hidden]
    """Generate workout plan using local ML engine with rate limiting"""
    # SEC-8: Enforce per-user rate limit before any expensive ML work.
        # Safely extract fields with defaults â€” include ALL profile fields
        # Fetch user document with sliced workout history
        # Check in-memory plan cache before running ML generation.
        # Cache key is deterministic: it combines profile fields + ISO-week number.
        # A hit means the same profile already generated a plan this week — no ML needed.
            # Generate workout (ML computation happens here)
            # Store the freshly generated plan so subsequent page visits are instant
        # Compute progression state and structured coaching feedback
        # Persist the generated weekly plan when a valid user_id is supplied.
def _cleanup_async_workout_jobs() -> None:
    # [Logic Hidden]
    """Evict stale/completed jobs and cap memory use for async job state."""
async def _generate_workout_job(job_id: str, profile_data: Dict[str, Any]) -> None:
    # [Logic Hidden]
        # Compute progression state and structured coaching feedback
        # Persist generated weekly plan if user doc exists
async def generate_workout_async(profile: WorkoutProfileRequest, background_tasks: BackgroundTasks):
    # [Logic Hidden]
    """Start background workout generation and return a polling job id."""
    # Fast path: return server-side cached plan immediately when available.
async def get_workout_status(job_id: str):
    # [Logic Hidden]
async def invalidate_workout_cache(profile: Dict[str, Any]):
    # [Logic Hidden]
# ==========================================
# WEEKLY PLAN & SWAP OPTIONS ENDPOINTS
# ==========================================
async def get_weekly_plan(
    # [Logic Hidden]
    """Return user's persisted weekly plan with week-level metadata."""
async def get_workout_swap_options(
    # [Logic Hidden]
    """Return swap eligibility and available target rest days for a specific day."""
# ==========================================
# NUTRITION SWAP ENDPOINT
# ==========================================
class SwapRequest(BaseModel):
    # [Logic Hidden]
    # Pass these so swaps are scaled to the same nutrition as the current item
async def get_swap_options(
    # [Logic Hidden]
    """Return swap alternatives for a given food item using Swap_Group from dataset"""
def _perform_undo_swap(weekly_plan: List[Dict[str, Any]], day_a_idx: int, day_b_idx: int) -> List[Dict[str, Any]]:
    # [Logic Hidden]
async def _persist_undo_swap_result(
    # [Logic Hidden]
# ==========================================
# REST DAY SWAP ENDPOINT
# ==========================================
class SwapRestDayRequest(BaseModel):
    # [Logic Hidden]
    """Request to swap a rest day with the next workout day"""
    # Deprecated identity field kept optional for backward compatibility.
    # User identity is resolved from JWT, not request payload.
class SwapWorkoutToRestRequest(BaseModel):
    # [Logic Hidden]
    """Request to move a workout day onto a future rest day."""
    # Deprecated identity field kept optional for backward compatibility.
    # User identity is resolved from JWT, not request payload.
async def swap_rest_day(
    # [Logic Hidden]
    """
    """
        # SEC-29 fix: resolve user identity from JWT (header/cookie), not payload email.
        # Validate current plan
        # Check if it is an undo swap
        # Check if the specified day is actually a rest day
        # Find next eligible workout day in the same week (no wrap-around)
        # Perform the swap using the workout engine
async def swap_workout_to_rest(
    # [Logic Hidden]
    """Move an original workout day to a selected future original rest day."""
        # SEC-29 fix: resolve user identity from JWT (header/cookie), not payload email.
        # Validate current plan
# ==========================================
# NUTRITION ENDPOINT
# ==========================================
async def generate_nutrition(
    # [Logic Hidden]
    """
    """
    # SEC-8: Enforce per-user rate limit before any expensive ML work.
    # Alias so existing code using 'request' still works.
        # ===== STEP 1: LOG INCOMING REQUEST =====
        # Require authenticated user for expensive nutrition generation.
        # ===== STEP 2: VALIDATE ENGINES INITIALIZED =====
        # ===== STEP 3: PREPARE USER PROFILE =====
        # ===== STEP 4: GENERATE MEAL PLAN =====
        # Validate meal plan structure
        # ===== STEP 5: VALIDATE MEAL DATA =====
        # Ensure all meals have required fields
        # ===== STEP 6: BUILD RESPONSE =====
        # Return generic server error; detailed trace stays in logs.
# ==========================================
# PROFILE UPDATE ENDPOINT
# ==========================================
async def update_profile(
    # [Logic Hidden]
    """Update user profile and regenerate workouts based on new parameters"""
        # **CRITICAL: Force regenerate workout plan with updated profile**
        # Log the exact data being sent to workout engine
        # Generate new workout plan
        # **Validate generated plan**
        # **Generate new nutrition plan**
            # Fallback if only daily meal API exists
        # **Return regenerated plans**
# ==========================================
# SAFE PROFILE UPDATE ENDPOINT (Production Ready)
# ==========================================
async def update_profile_safe(
    # [Logic Hidden]
    """
    """
    # Initialize response structure
        # ===== STEP 1: LOG INCOMING REQUEST =====
        # ===== STEP 2: VALIDATE INPUT =====
        # ===== STEP 3: AUTHENTICATION =====
        # Load user document from DB to merge profile updates and support generation
        # ===== STEP 4: EXTRACT PROFILE DATA =====
        # Keep only valid profile fields
        # Build complete user profile by merging existing DB document with current updates
        # If only 'name' was changed, update DB and return success early
        # ===== STEP 5: REGENERATE WORKOUT PLAN (ISOLATED) =====
        # ===== STEP 6: REGENERATE NUTRITION PLAN (ISOLATED) =====
                # Get workout plan for nutrition calculation (use regenerated or generate fresh)
        # ===== STEP 6.5: PERSIST PROFILE AND GENERATED PLANS TO MONGODB =====
            # Save profile updates
            # Save workout plan and week metadata if generated
            # Save nutrition plan if generated
        # ===== STEP 7: BUILD SUCCESS RESPONSE =====
        # Log final status
# ==========================================
# GENERATE PLAN ENDPOINT (Called by Frontend ProfileSetup)
# ==========================================
async def generate_plan(
    # [Logic Hidden]
    """Generate full workout + nutrition plan from profile data"""
        # Generate workout plan
        # Generate nutrition plan — BUG FIX: use generated workout to derive intensity
            # Derive workout intensity from the generated plan
            # Calculate intensity from exercise volume
        # Bug #11 fixed: persist the generated plans to MongoDB (best-effort)
                    # Also persist nutrition plan
                # Non-fatal: plans are still returned to the client
# ==========================================
# ERROR HANDLER
# ==========================================
async def http_exception_handler(request, exc):
    # [Logic Hidden]
async def general_exception_handler(request, exc):
    # [Logic Hidden]
    """Catch-all exception handler — logs full details server-side and returns
    """
# ─────────────────────────────────────────────────────────────────────────────
# Priority 1: Exercise Variation Ladder — POST /api/workout/session-result
# ─────────────────────────────────────────────────────────────────────────────
class SessionResultRequest(BaseModel):
    # [Logic Hidden]
    """Request body for workout session result."""
async def workout_session_result(
    # [Logic Hidden]
    """
    """
        # Get variation suggestion from the exercise dataset
        # Get progression update
# ─────────────────────────────────────────────────────────────────────────────
# Priority 3: Daily Log — POST /api/daily-log + GET /api/daily-log/week
# ─────────────────────────────────────────────────────────────────────────────
class DailyLogRequest(BaseModel):
    # [Logic Hidden]
    """Request body for daily check-in."""
async def save_daily_log(
    # [Logic Hidden]
    """Save a daily sleep/water check-in for the adaptive modifier."""
        # Upsert — one log per user per day
async def get_weekly_logs(
    # [Logic Hidden]
    """Get last 7 daily logs for the current user."""
        # Compute weekly averages
        # Calculate biometrics adaptive modifier reasoning
```

## backend-python\test_A.py
```python
"""Test section A: Init, format_serving, blocklist, diet filter, targets"""
def ok(label, cond, got="", exp=""):
    # [Logic Hidden]
def warn(label, cond, got="", exp=""):
    # [Logic Hidden]
# ─── INIT ───
# ─── FORMAT_SERVING ───
# ─── BLOCKLIST ───
# Verify no blocklist items in loaded pool
# ─── DIET FILTERS ───
# Meat in veg pool check
# Dairy in vegan pool check
# Unknown diet raises ValueError
# ─── ALLERGY FILTERS ───
# ─── DAILY TARGETS ───
# ─── SUMMARY ───
```

## backend-python\test_B.py
```python
"""Test section B: Plan generation for 3 profiles + determinism + swap tests"""
def ok(label, cond, got="", exp=""):
    # [Logic Hidden]
def warn(label, cond, got="", exp=""):
    # [Logic Hidden]
def check_plan(label, result):
    # [Logic Hidden]
    # All meal types filled
    # Required fields
    # No blocklist foods
    # Calorie accuracy
    # Meal roles: lunch should generally be heaviest
    # Swap options
    # Breakfast uniqueness across 7 days
    # Validation warnings count
    # Serving values are reasonable strings, not 'X unit unit'
# ── PLAN TESTS ───────────────────────────────────────────────────────────────
# ── DETERMINISM ──────────────────────────────────────────────────────────────
# ── SWAP TESTS ───────────────────────────────────────────────────────────────
# Check all swap options have required keys
# Swap food != original food
# Swap calories within ±40x of original (very loose to catch gross errors)
# Public API: get_swap_options
# ── ALLERGY PLAN TESTS (single plan each) ────────────────────────────────────
# Vegan + gluten (most restrictive)
# ── EDGE CASES ───────────────────────────────────────────────────────────────
# Null profile fields
# Summary structure
# ── FINAL SUMMARY ─────────────────────────────────────────────────────────────
```

## backend-python\test_meal.py
```python
# Disable verbose debug logs for testing
            # Extract meal_name from first item or generate combo name
```

## backend-python\test_meal_engine.py
```python
def test_engine():
    # [Logic Hidden]
        # vary the profile slightly to get new plans
        # Verify
                # Check for desserts/spreads
                # Check combo constraints
                # Check portion sizes
```

## backend-python\test_meal_engine_crash.py
```python
def test():
    # [Logic Hidden]
        # --- Variety Check ---
        # --- Swap Options Quality Test ---
```

## backend-python\test_meal_quality.py
```python
# Test with a real Indian user profile
# 1. Check targets
# 2. Generate weekly plan
# 3. Analyze each day
# 4. Diversity analysis
# 5. Snack quality check
# 6. Allergen check
            # Check if 'nut' appears - should be filtered
# 7. Profile 2: Female weight loss vegetarian
```

## backend-python\test_trace.py
```python
def trace_calls(frame, event, arg):
    # [Logic Hidden]
```

## backend-python\train.py
```python
# Define paths
# Create models folder if it doesn't exist
def train_models():
    # [Logic Hidden]
    # Initialize the feature pipeline
    # --- 1. Train Meal Model ---
    # --- 2. Train Multi-Output Workout Model ---
        # Initialize the multi-output model
        # Create synthetic training data based on exercise properties
        # This simulates having historical workout data
        # Prepare features and targets
        # Split data for training and validation
        # Train the multi-output model
        # Save the multi-output model
        # Also save individual models for backward compatibility if needed
        # (keeping the old models for compatibility with existing code)
        # Individual XGBoost models for WorkoutEngine (using correct filenames)
        # Volume model (uses sets as proxy for volume level)
        # Intensity model (uses intensity column)
        # Split model (classifier for workout split type)
        # Frequency model (days per week prediction)
        # Sets model
        # Reps model (multi-output for reps_low and reps_high)
        # Rest model
        # Progression model
        # Label encoders
    # --- 3. Train Multi-Target Nutrition Model ---
        # Initialize the multi-target nutrition model
        # Create synthetic training data for nutrition model
        # Generate synthetic user profiles
        # Calculate BMR and TDEE
        # Calculate TDEE based on activity level
        # Adjust TDEE based on goal
        # Generate target values based on features
            # Meal distribution
            # Ensure meal calories are positive and within reasonable bounds
            # Calculate total calories
            # Calculate macros based on goal
        # Convert to numpy array
        # Split data for training and validation
        # Train the multi-target nutrition model
        # Save the multi-target nutrition model
```

## backend-python\validate_personas.py
```python
# Add backend-python to path
# Helper to build workout histories
def make_workout_history(weeks_count: int):
    # [Logic Hidden]
        # 1 workout per week to satisfy consistent weeks check
def make_plateau_history():
    # [Logic Hidden]
        # 3 sessions spaced 2 days apart
def make_long_history(count: int):
    # [Logic Hidden]
def main():
    # [Logic Hidden]
    # Ensure output directory exists
    # Initialize engines
    # Define personas
    # Tracking results
        # Time generation
        # 1. Compute progression state first (simulating server.py logic)
        # 2. Call generate_weekly_plan
        # Parse selected exercises
        # Save output file
        # --- Rule Validations ---
        # Validate P1: Bodyweight exercises only
                # bodyweight only allows none, body weight, bodyweight, assisted, pullup bar (if assisted/bodyweight)
        # Validate P2: High intensity for advanced strength lifter
            # Just ensure plan has compound exercises
        # Validate P3: Deload triggered
            # Verify reduced sets
        # Validate P5: Plateau check
            # Check if Push-Up was swapped out for Decline, Tempo, or Diamond Push-Up
        # Validate P6: Shoulder Injury
        # Validate P7: No Equipment
        # Validate P8: Gym preferences
            # Full gym user should have high-value loaded exercises
                # Warning only or validation
        # Validate P10: History slicing and execution time
        # Validate P11: Contradictory user
    # Output Markdown Checklist Report
```

## backend-python\verify_meal_endpoints.py
```python
def run_nutrition_audit():
    # [Logic Hidden]
    # Initialize both engines to verify compat
    # Personas definition
    # Audit loop
        # 1. Target Calculations Audit
        # Protein limit check
        # 2. Meal Plan Generation Audit
        # Generate via wrapper to test workout volume adjustment
        # Rest day check
        # Check that no masalas or invalid foods got recommended
                # Enforce portion boundaries
                    # Spices / junk blacklist check
                        # Some names contain "veg" or "soup" which is fine, but check they aren't raw masalas
                    # Snack quality check
                        # Ensure no heavy main course dishes are recommended as snacks
                    # Allergen checking
    # Mock some UI portion calculations to verify portion logic
    # Simple JS-equivalent python portion estimator to test rules
    def py_portion_estimator(name, cal):
    # [Logic Hidden]
        # fallback
```

## backend-python\verify_production_fixes.py
```python
# Configure logging to show only warnings/errors during test execution
# Adjust path to import app modules
def generate_mock_profiles(count=100):
    # [Logic Hidden]
def verify_all_rules():
    # [Logic Hidden]
            # Generate the weekly plan
            # (generate_meal_plan integrates V6 and adjustments)
            # Check weekly plan days
                    # 1. Assert breakfast, lunch, dinner are not empty
                    # Verify each food item
                        # 2. Carbs & macro validation (must not be zero unless food naturally contains 0)
                        # 3. Duplicate food in the same day check
                        # 4. Unrealistic portion sizes check
                        # 5. Strict Meal Rules check
                            # Breakfast: no curries, soups, salads, heavy rice
                            # Dinner: no milkshake, tea, coffee
                            # Lunch: no milkshake, coffee
                            # Snack: no heavy meals (rice, chapati, curry, roti)
                # 6. Verify daily target deviation
                # High protein goals have more tolerance due to realistic whole-food constraints
                # Base allowed deviation
                # Adjust allowed deviation based on Calorie-to-Protein Ratio (CPR) constraint
```

## backend-python\app\__init__.py
```python
"""
"""
```

## backend-python\app\adaptive_modifier.py
```python
# -*- coding: utf-8 -*-
"""
"""
def compute_adaptive_modifiers(
    # [Logic Hidden]
    """
    """
    # ── Sleep-based recovery modifier ────────────────────────────────────────
    # Compare against the user's personal sleep target, not a fixed 8h cutoff.
    # ── Hydration-based modifier ───────────────────────────────────────────────
    # Ratio-based check against the user's personalised water target.
    # Plan Section 6: > 30% deficit → reduce cardio; 10-30% deficit → tip only.
    # ── Workout attendance modifier ───────────────────────────────────────────
    # ── Clamp intensity delta to reasonable bounds ────────────────────────────
def apply_modifiers_to_workout_stats(
    # [Logic Hidden]
    """
    """
    # Apply intensity delta
    # Bonus sets
    # Skip volume flag
    # Deload flag overrides everything
```

## backend-python\app\analyze_data.py
```python
def search(name):
    # [Logic Hidden]
```

## backend-python\app\biometric_normalizer.py
```python
class BiometricNormalizer:
    # [Logic Hidden]
    """Normalize raw biometric inputs to 1-10 score ranges."""
    def _to_float(value: Any, default: float) -> float:
    # [Logic Hidden]
    def parse_sleep_hours(cls, value: Any, default: float = 7.0) -> float:
    # [Logic Hidden]
    def parse_water_liters(cls, value: Any, default: float = 2.5) -> float:
    # [Logic Hidden]
    def normalize_sleep(cls, value: Any) -> float:
    # [Logic Hidden]
        # Pass through plausible score-style inputs.
    def normalize_hydration(cls, value: Any) -> float:
    # [Logic Hidden]
        # Pass through plausible score-style inputs.
            # Distinguish likely liters from explicit score values: tiny hydration values
            # like 1.2L should still map through hydration logic.
```

## backend-python\app\circuit_breaker.py
```python
"""
    # 1. Simple retry with exponential backoff (no circuit breaker):
    def call_something():
    # [Logic Hidden]
    # 2. Full circuit breaker (opens after N consecutive failures):
"""
# ──────────────────────────────────────────────────────────────────────────────
# Simple retry decorator (tenacity-backed)
# ──────────────────────────────────────────────────────────────────────────────
def with_retry(
    # [Logic Hidden]
    """
    """
    def decorator(fn):
    # [Logic Hidden]
        def wrapper(*args, **kwargs):
    # [Logic Hidden]
# ──────────────────────────────────────────────────────────────────────────────
# Full Circuit Breaker
# ──────────────────────────────────────────────────────────────────────────────
class _State(Enum):
    # [Logic Hidden]
class CircuitBreakerOpen(RuntimeError):
    # [Logic Hidden]
    """Raised when a call is attempted while the circuit breaker is OPEN."""
class CircuitBreaker:
    # [Logic Hidden]
    """
    """
    def __init__(
    # [Logic Hidden]
    # ------------------------------------------------------------------
    # Public interface
    # ------------------------------------------------------------------
    def state(self) -> str:
    # [Logic Hidden]
    def call(self, fn, *args, **kwargs):
    # [Logic Hidden]
        """
        """
    # ------------------------------------------------------------------
    # Internal state machine
    # ------------------------------------------------------------------
    def _maybe_transition(self):
    # [Logic Hidden]
    def _on_success(self):
    # [Logic Hidden]
    def _on_failure(self):
    # [Logic Hidden]
# ──────────────────────────────────────────────────────────────────────────────
# Pre-built circuit breakers for Elevate external dependencies
# ──────────────────────────────────────────────────────────────────────────────
#: Circuit breaker for Gemini API calls (chatbot + workout config generation).
#: Opens after 5 consecutive failures; retries after 60 s.
#: Circuit breaker for any future external REST API calls.
```

## backend-python\app\data_health_analysis.py
```python
def analyze_exercises_data(file_path):
    # [Logic Hidden]
    """
    """
        # 1. Missing Values Analysis
        # 2. Duplicate Analysis
        # 3. Data Types and Consistency
        # 4. Categorical Variable Analysis
            # Check for inconsistent entries (potential typos)
        # 5. Numerical Variables Summary
        # 6. Equipment Analysis
        # 7. Target Muscle Analysis
        # 8. Difficulty Level Analysis
        # 9. Potential Issues Summary
def analyze_nutrition_data(file_path):
    # [Logic Hidden]
    """
    """
        # 1. Missing Values Analysis
        # 2. Duplicate Analysis
        # 3. Data Types and Consistency
        # 4. Categorical Variable Analysis
        # 5. Nutritional Values Analysis
                # Check for negative values (invalid)
                # Check for extremely high values (potential outliers)
        # 6. Meal Type Analysis
        # 7. Dietary Tags Analysis
        # 8. Potential Issues Summary
def analyze_class_imbalance(df, column_name):
    # [Logic Hidden]
    """
    """
        # Flag highly imbalanced classes (less than 5% or more than 70%)
def analyze_feature_gaps(user_profile_example=None):
    # [Logic Hidden]
    """
    """
    # Define expected user profile features
    # Potential gaps in current datasets
    # Recommend new columns to add
def generate_comprehensive_report(exercises_df, nutrition_df):
    # [Logic Hidden]
    """
    """
def generate_data_cleaning_strategy(exercises_df, nutrition_df):
    # [Logic Hidden]
    """
    """
def main():
    # [Logic Hidden]
    """
    """
    # BUG-P9 fix: use __file__-relative paths so this script works regardless
    # of the current working directory. Previously used hardcoded relative paths
    # like 'backend-python/data/...' which broke when run from any other directory.
    # Analyze exercises data
    # Analyze nutrition data
    # Perform class imbalance analysis if dataframes exist
        # Common categorical columns in exercises data
        # Common categorical columns in nutrition data
    # Analyze feature gaps
    # Generate data cleaning strategy
    # Generate comprehensive report
```

## backend-python\app\db.py
```python
# MongoDB connection settings
# Global client variable
def _is_local_mongo_uri(uri: str) -> bool:
    # [Logic Hidden]
def _validate_mongo_security(uri: str) -> None:
    # [Logic Hidden]
async def connect_to_mongo():
    # [Logic Hidden]
    """Connect to MongoDB"""
        # Test the connection
async def close_mongo_connection():
    # [Logic Hidden]
    """Close MongoDB connection"""
def get_database():
    # [Logic Hidden]
    """Get the database instance"""
    # Extract database name from the connection string
    # Handle different MongoDB URI formats
        # Format: mongodb://host:port/database_name
        # or mongodb://username:password@host:port/database_name
            # Remove query parameters if present
        # Format: mongodb+srv://host/database_name
            # Remove query parameters if present
        # Fallback: extract from custom format
            # Remove query parameters if present
    # Ensure the database name is valid (doesn't contain dots)
        # If database name contains dots, use the default
def get_user_collection():
    # [Logic Hidden]
    """Get the user collection instance"""
def get_workout_history_collection():
    # [Logic Hidden]
    """Get the workout history collection instance"""
def get_meal_history_collection():
    # [Logic Hidden]
    """Get the meal history collection instance"""
def get_workout_completion_collection():
    # [Logic Hidden]
    """Get the workout completion collection instance"""
def get_meal_completion_collection():
    # [Logic Hidden]
    """Get the meal completion collection instance"""
def get_weekly_meal_plans_collection():
    # [Logic Hidden]
    """Get the weekly meal plans collection instance"""
```

## backend-python\app\deterministic_meal_engine.py
```python
"""
"""
# ---------------------------------------------------------------------------
# MODULE-LEVEL CONSTANTS
# ---------------------------------------------------------------------------
# Blueprints: each entry is a list of required meal_roles for a meal slot.
# The engine picks a random blueprint then fills each role from the food pool.
# Availability scoring weights
# Cuisine/region bonus for variety
# Foods to exclude from recommendations — unrealistic for daily meal planning
# Words that identify a food as a non-meal (raw bases, desserts, sugary drinks).
# NOTE: overly-broad descriptors were removed because they falsely rejected healthy
# composite dishes (verified against nutrition_production_final_v4.csv):
#   - 'sauce'   matched 17 valid mains (e.g. "Paneer In Butter Sauce",
#               "Baked Eggs In Tomato Sauce", "Spaghetti With Paneer Balls...").
#   - 'filling' was redundant with the more-specific 'curd filling' (same 2 dessert
#               items) while risking future false positives.
# Genuine unhealthy/non-meal filters are intentionally retained below.
# ---------------------------------------------------------------------------
# PHASE 1 — WEEKLY VARIETY TRACKER
# ---------------------------------------------------------------------------
class WeeklyVarietyTracker:
    # [Logic Hidden]
    """
    """
    def __init__(self):
    # [Logic Hidden]
    def meal_history(self, meal_type: str) -> Set[str]:
    # [Logic Hidden]
    def record_meal(self, meal_type: str, components: List[Dict]):
    # [Logic Hidden]
        """Register a chosen meal so future days can avoid repeats."""
    def record_cuisine(self, region: str):
    # [Logic Hidden]
    def record_template(self, bp_idx: int):
    # [Logic Hidden]
    def variety_penalty(self, meal_type: str, components: List[Dict],
    # [Logic Hidden]
        """Return a penalty score (≥0) that is subtracted from the meal score."""
            # Repeated food name
            # Repeated family within the last 3 days (approx 12 main meals)
            # Repeated protein source
            # Repeated carb
        # Repeated cuisine
        # Repeated template
# ---------------------------------------------------------------------------
# PHASE 2 — PORTION OPTIMIZER
# ---------------------------------------------------------------------------
def get_food_family(name: str, swap_group: str) -> str:
    # [Logic Hidden]
def is_realistic_meal_identity(meal_type: str, components: List[pd.Series]) -> bool:
    # [Logic Hidden]
    """
    """
    # Lunch/Dinner must contain a Cooked Staple if it uses Breakfast/Snack mains
def optimize_portions(components: List[pd.Series],
    # [Logic Hidden]
    """
    """
def _format_serving(qty: float, unit: str, name: str = '', cal: float = 0.0) -> str:
    # [Logic Hidden]
    """Produce a human-readable serving string based on food type and calories."""
    # If explicitly pieces
    # If no name or calories provided, fallback to basic formatting
    # 1. Eggs
    # 2. Roti / Chapati / Paratha / Naan / Bread
    # 3. Idli / Dosa / Uttapam / Vada
    # 4. Whole fruits
    # 5. Beverages
    # 6. Tea & Coffee
    # 7. Dal, Sambar, Kadhi, Soups, Salad, Yogurt, Raita
    # 8. Rice, Pulao, Biryani, Noodles, Pasta
    # 9. Protein Bars
    # 10. Nuts & Seeds
    # Fallback for G / ML
        # For foods not caught above, format as `[X]g`
    # Basic fallback
# ---------------------------------------------------------------------------
# PHASE 6 — MEAL SCORER
# ---------------------------------------------------------------------------
def score_meal(components: List[Dict],
    # [Logic Hidden]
    """
    """
    # 1. Macro Accuracy (30 pts)
    # 2. Weekly Variety (20 pts) — subtract variety_penalty capped at 20
    # 3. Meal Completeness (15 pts)
    # 4. Portion Realism (10 pts) — penalise components at their min/max boundary
    # 5. Budget (10 pts)
    # 6. Availability (10 pts)
    # 7. Cuisine rotation (5 pts)
# ---------------------------------------------------------------------------
# PHASE 5 — SWAP ENGINE
# ---------------------------------------------------------------------------
def build_swap_options(component: Dict,
    # [Logic Hidden]
    """
    """
    # We convert to a list of dicts for much faster filtering compared to DataFrame masks
    # Only pick rows matching role
    # Convert to native list of dicts for fast iteration
    # Filter by meal_type to avoid cross-meal swaps (e.g. dinner biryani in breakfast swap)
        # Case insensitive check
    # Nutrition similarity filter — try tight window first, then widen
    # Prefer same swap_group first
    # Score by availability + budget
    # Take top N
    # Convert numeric values that were float64 to python floats for JSON safety
        # Determine the ideal multiplier to match calories
        # Snap to valid portion step
        # If the unit is piece/unit, force step to integer
        # Calculate multiplier that represents the actual physical steps
        # Note: p_step in metadata is in the same unit as serving_quantity.
        # So we figure out the ideal raw quantity, snap it to step, then find the true multiplier.
# ---------------------------------------------------------------------------
# MAIN ENGINE CLASS
# ---------------------------------------------------------------------------
class MealEngine:
    # [Logic Hidden]
    """
    """
    def __init__(self,
    # [Logic Hidden]
            # Normalise string columns
            # Inner join on food_id
            # Drop desserts, spreads, sauces — never appear as base meals
        # ---- Calorie / macro target parameters ----
    # ------------------------------------------------------------------
    # HELPERS — determinism
    # ------------------------------------------------------------------
    def _user_entropy(self, profile: Dict) -> str:
    # [Logic Hidden]
    def _profile_fp(self, profile: Dict) -> str:
    # [Logic Hidden]
    def _seed(self, ue: str, fp: str, week: int, day: int, mt: str) -> int:
    # [Logic Hidden]
    # ------------------------------------------------------------------
    # PHASE: DAILY TARGETS
    # ------------------------------------------------------------------
    def calculate_daily_targets(self, profile: Dict) -> Dict:
    # [Logic Hidden]
    # ------------------------------------------------------------------
    # PHASE 7 — NUTRITION RULE ENGINE (diet + allergy filter)
    # ------------------------------------------------------------------
    def _apply_nutrition_rules(self, profile: Dict) -> pd.DataFrame:
    # [Logic Hidden]
            # Guard against mislabeled CSV rows: exclude fish/meat even if is_vegetarian=True
            # Guard against mislabeled rows: exclude fish/meat/dairy for vegan
        # Extra safety check to drop any roles that slipped through
    # ------------------------------------------------------------------
    # PHASE 3 & 4 — CANDIDATE GENERATION (blueprint + meal_time aware)
    # ------------------------------------------------------------------
    def _generate_candidates(self,
    # [Logic Hidden]
        """
        """
        # Filter pool by meal_type from nutrition CSV
        # meal_type column values: Breakfast, Lunch, Dinner, Snack, Beverage
        # Precompute available items by role to avoid pandas mask evaluation in hot loop
        # Apply rejected_names filter ONCE upfront
        # Convert history to set ONCE for O(1) lookups
            # Prefer unused templates first
                # Least-recently used
                # Try to match pair_group for cohesion (e.g. Idli + Sambar)
                # Graceful Fallbacks if strict filtering exhausts options
                    # Fallback 1: Try from full pool ignoring meal_time and pair_group
                # Prefer less-recently used foods (variety)
                # Availability-weighted sampling with tie-breaking noise for variety
    # ------------------------------------------------------------------
    # PHASE 8 — WEEKLY VALIDATOR
    # ------------------------------------------------------------------
    def _validate_plan(self, plan: Dict) -> Dict:
    # [Logic Hidden]
        """
        """
                # CHECK 1 & 2: Duplicate meals across days
            # CHECK 3 & 4: Desserts, Spreads, strict completeness rules
                # Check for structural completeness
                # Check condiment portion sizes
            # CHECK 5: Meal Completeness per day
                # combo_meal counts as both protein and carb
            # CHECK 6: Portion Realism — already enforced in optimize_portions
            # CHECK 7 & 8: Budget/Availability — enforced in scoring
    # ------------------------------------------------------------------
    # MAIN: GENERATE WEEKLY PLAN
    # ------------------------------------------------------------------
    def generate_weekly_plan(self, profile: Dict) -> Dict:
    # [Logic Hidden]
                    # Fallback 1: re-try with fewer candidates
                    # Fallback 2: if still empty, use robust multi-role fallbacks
                    # Inline Validation: If fails, regenerate this meal slot
                    # Reject invalid strict rules during generation loops to save validator passes
                        # Validation Passed!
                    # If failed but it's the last retry, accept it anyway
                    # Register chosen meal in tracker
                        # Build swap options — pass meal_time to avoid cross-meal swaps
        # Phase 8: Weekly Validator — runs once, then corrects failed meals
        # Correction loop: regenerate only failed (day, meal_type) slots (up to 3 passes)
                    # Use correction_pass as additional seed entropy
                    # Replace the slot
                # Re-validate after corrections
    # ------------------------------------------------------------------
    # SUMMARY & SHOPPING LIST
    # ------------------------------------------------------------------
    def _build_summary(self, plan: Dict, targets: Dict) -> Dict:
    # [Logic Hidden]
    # ------------------------------------------------------------------
    # PHASE 5 — PUBLIC SWAP API
    # ------------------------------------------------------------------
    def get_swap_options(self,
    # [Logic Hidden]
        """
        """
```

## backend-python\app\evaluation_framework.py
```python
"""
"""
class ModelEvaluator:
    # [Logic Hidden]
    """
    """
    def __init__(self, model_name: str, model_type: str = "regression"):
    # [Logic Hidden]
        # Setup logging
        # Initialize metrics
    def _setup_logging(self) -> logging.Logger:
    # [Logic Hidden]
        """
        """
        # Create formatter
        # Console handler
        # File handler
    def _rmse(self, y_true: np.ndarray, y_pred: np.ndarray) -> float:
    # [Logic Hidden]
        """Root Mean Square Error"""
    def _mae(self, y_true: np.ndarray, y_pred: np.ndarray) -> float:
    # [Logic Hidden]
        """Mean Absolute Error"""
    def _precision(self, y_true: np.ndarray, y_pred: np.ndarray) -> float:
    # [Logic Hidden]
        """Precision score"""
    def _recall(self, y_true: np.ndarray, y_pred: np.ndarray) -> float:
    # [Logic Hidden]
        """Recall score"""
    def _safety_compliance(self, y_true: np.ndarray, y_pred: np.ndarray, safety_bounds: Dict = None) -> float:
    # [Logic Hidden]
        """
        """
            # Default safety bounds for nutrition/workout models
        # Calculate how many predictions are within bounds
    def evaluate_model(self,
    # [Logic Hidden]
        """
        """
        # Make predictions
        # Calculate metrics
        # Feature importance (if available)
        # Store results
    def detect_drift(self, X_current: pd.DataFrame, X_reference: pd.DataFrame, threshold: float = None) -> Dict:
    # [Logic Hidden]
        """
        """
        # Compare statistical properties of features
                # Perform Kolmogorov-Smirnov test for distribution similarity
        # Overall drift assessment
    def compare_models(self,
    # [Logic Hidden]
        """
        """
        # Initialize models
        # Train models
        # Evaluate models
        # Cross-validation comparison
    def plot_feature_importance(self, feature_importance: Dict, top_n: int = 10) -> plt.Figure:
    # [Logic Hidden]
        """
        """
        # Sort features by importance
    def plot_predictions_vs_actual(self, y_true: np.ndarray, y_pred: np.ndarray) -> plt.Figure:
    # [Logic Hidden]
        """
        """
    def generate_report(self, results: Dict, model_comparison: Dict = None) -> str:
    # [Logic Hidden]
        """
        """
        """
        """
class ABTestFramework:
    # [Logic Hidden]
    """
    """
    def __init__(self, control_model, treatment_model, test_name: str = "A/B Test"):
    # [Logic Hidden]
        # Setup logging
    def _setup_logging(self) -> logging.Logger:
    # [Logic Hidden]
        """
        """
    def run_ab_test(self,
    # [Logic Hidden]
        """
        """
        # Get predictions from both models
        # Calculate metrics for both models
        # Perform statistical test (paired t-test)
        # Determine significance
def create_evaluation_folder_structure():
    # [Logic Hidden]
    """
    """
def example_execution_flow():
    # [Logic Hidden]
    """
    """
    # Create sample data
    # Simulated workout data
    # Simulated targets (sets, reps, rest_time, intensity)
    # Split data
    # Initialize evaluator
    # Train a sample model
    # Evaluate the model
    # Compare models
    # Detect drift
    # Create slightly different reference data
    # A/B Testing example
    # Generate report
    # Save results
    # Create folder structure
    # Run example execution
```

## backend-python\app\feature_pipeline.py
```python
"""
"""
class FeaturePipeline:
    # [Logic Hidden]
    """
    """
    def __init__(self):
    # [Logic Hidden]
        # Initialize encoders
        # Fit encoders with default values
        # Scaler for numerical features
        # Feature names for reference
        # Define target mappings
    def _fit_encoders(self):
    # [Logic Hidden]
        """Fit encoders with default values"""
        # Experience levels
        # Fitness goals
        # Gender
        # Equipment (will be fitted when first data comes in)
        # Injury flags (will be fitted when first data comes in)
    def validate_input(self, user_profile: Dict) -> Dict:
    # [Logic Hidden]
        """
        """
        # Required fields with defaults
        # Accept both raw biometric inputs and already-scored inputs.
        # Validate ranges
    def calculate_derived_features(self, user_profile: Dict) -> Dict:
    # [Logic Hidden]
        """
        """
        # Ensure recovery metrics are normalized even if callers bypass validate_input.
        # BMI calculation
        # Experience score (numerical representation)
        # Recovery score — 4-factor model (sleep, hydration, stress, fatigue)
        # Consistency score (already normalized)
        # Equipment richness score (normalized count of equipment)
        # Intensity capacity score (combines experience and recovery)
        # ── Progressive overload delta (redesigned multi-factor formula) ──
        #
        # progression_delta = base_rate × adherence × recovery × experience_mod
        #
        # base_rate:       3-7 % depending on experience
        # adherence:       0.6 × completion + 0.4 × streak_factor
        # recovery:        4-factor recovery score (computed above)
        # experience_mod:  Beginner 0.70 | Intermediate 1.00 | Advanced 1.15
        #
        # Adherence score: blend completion proxy (consistency) with streak
        # Age-adjusted capacity (older users may need adjusted intensity)
    def encode_features(self, user_profile: Dict) -> np.ndarray:
    # [Logic Hidden]
        """
        """
        # Encode categorical features
        # Experience encoding
            # If new value, use the most common (Beginner = 0)
        # Goal encoding
            # If new value, use the most common (Muscle Gain = 0)
        # Gender encoding
            # If new value, default to Male = 0
        # Equipment multi-hot encoding
            # If new equipment list, fit and transform
        # Injury multi-hot encoding
            # If new injury list, fit and transform
        # Create feature vector
        # Concatenate with encoded equipment and injury vectors
    def scale_features(self, feature_vector: np.ndarray) -> np.ndarray:
    # [Logic Hidden]
        """
        """
        # Reshape if needed
        # Fit scaler if not already fitted
        # Transform features
    def process_user_profile(self, user_profile: Dict) -> np.ndarray:
    # [Logic Hidden]
        """
        """
        # Step 1: Validate input
        # Step 2: Calculate derived features
        # Step 3: Encode features
        # Step 4: Scale features
    def get_feature_importance_template(self) -> Dict:
    # [Logic Hidden]
        """
        """
    def cold_start_strategy(self, user_profile: Dict) -> Dict:
    # [Logic Hidden]
        """
        """
        # For new users with limited history, use demographic and goal-based templates
        # Base template on experience and goal
        # Adjust for goal
def explain_pipeline_design():
    # [Logic Hidden]
    """
    """
    """)
    """)
    """)
    """)
    """)
    """)
    """)
    # Example usage
    # Example user profile
    # Process the profile
    # Show cold start strategy
    # Explain the design
```

## backend-python\app\gemini_service.py
```python
# Configuration handled in server.py
# Explicitly load environment variables before reading them
# ===== LAZY INITIALIZATION WITH MODEL FALLBACK =====
def _get_model() -> Optional[genai.GenerativeModel]:
    # [Logic Hidden]
    """Lazily initialize the Gemini model on first use with automatic fallback."""
    # Fast path: already initialized for the same key.
    # If key changed during runtime, allow re-initialization without server restart.
        # Bug #4: Show a helpful, actionable message when the key is missing.
    # Resolve candidates dynamically inside the function after dotenv has loaded
    # Enhanced diagnostic: Log API key presence (masked)
    # Try each model candidate until one works
            # Validation call: avoid tiny token limits and ensure we can read text output.
def is_gemini_available() -> bool:
    # [Logic Hidden]
    """Return True only when a Gemini model is actually initialized and usable."""
def generate_workout_config(profile: Dict[str, Any], intensity: float) -> Optional[Tuple[int, str, int, list]]:
    # [Logic Hidden]
    """
    """
    """
        # ARCH-7: Route through circuit breaker — if Gemini is repeatedly
        # failing (quota, network outage) the circuit opens and we skip
        # further calls until the breaker resets.
        def _call():
    # [Logic Hidden]
# ===== CHATBOT =====
# Maximum conversation history to send to Gemini (prevents token overflow)
# Maximum characters per user message
# ===== OFFLINE FALLBACK RESPONSES =====
# Enhanced offline responses that actually provide value when API is unavailable
def _get_fallback_response(message: str) -> str:
    # [Logic Hidden]
    """Return a helpful offline response when the AI is unavailable."""
    # Check for motivation-related keywords first (before general workout)
    # Check for form/technique keywords
def _build_contextual_offline_response(user_message: str, profile: Dict[str, Any], chat_history: list = None) -> str:
    # [Logic Hidden]
    """Return a deterministic offline reply that reflects the current conversation context."""
def _extract_message_text(msg: Dict[str, Any]) -> str:
    # [Logic Hidden]
def _map_role(role: Any) -> str:
    # [Logic Hidden]
def _build_system_prompt(profile: Dict[str, Any]) -> str:
    # [Logic Hidden]
    """Build the system prompt with user profile context."""
    def _safe_join(val):
    # [Logic Hidden]
"""
def _trim_history(history: list) -> list:
    # [Logic Hidden]
    """Trim conversation history to prevent token overflow."""
def get_chatbot_response(user_message: str, profile: Dict[str, Any], chat_history: list = None) -> str:
    # [Logic Hidden]
    """
    """
    # Sanitize input
    # If model is unavailable, use smart offline fallback
    # Build conversation context from history
        def _call():
    # [Logic Hidden]
        # ARCH-7: circuit breaker guards chatbot calls
        # If quota exhausted, use fallback
```

## backend-python\app\hybrid_volume_optimizer.py
```python
"""
"""
# -*- coding: utf-8 -*-
class HybridVolumeOptimizer:
    # [Logic Hidden]
    """
    """
    def __init__(self):
    # [Logic Hidden]
        # ML models (optional - will use rules if not available)
        # Try to load ML models
        # Progression engine for multi-factor overload
        # Rule-based configuration
    def _try_load_ml_models(self):
    # [Logic Hidden]
        """Try to load ML models, gracefully degrade if not available"""
            # Silently fail - will use rules
    def calculate_optimal_sets(
    # [Logic Hidden]
        """
        """
        # Phase 1: Rule-based starting point
        # Phase 2: User-specific adaptation (if history available)
        # Phase 3: ML adjustment (if model available)
            # Blend ML prediction with rule-based (weight depends on data confidence)
        # Apply safety caps
    def calculate_optimal_reps(
    # [Logic Hidden]
        """
        """
        # Phase 1: Rule-based starting point
        # Phase 2: User-specific adaptation
        # Phase 3: ML adjustment
            # Blend rep ranges
        # Apply age-based safety adjustments
    def _get_rule_based_sets(self, user_profile: Dict, exercise_type: str) -> int:
    # [Logic Hidden]
        """Phase 1: Get rule-based starting sets"""
        # Base sets from experience
        # Adjust for goal
        # Adjust for exercise type
        # Age adjustment (safety)
    def _get_rule_based_reps(self, user_profile: Dict, intensity: float) -> str:
    # [Logic Hidden]
        """Phase 1: Get rule-based starting reps"""
        # Base reps from goal
        # Adjust for experience
            # Beginners benefit from higher reps (practice, lighter weight)
            # Advanced can handle lower reps with heavier weight
        # Adjust for intensity
    def _adapt_based_on_history(
    # [Logic Hidden]
        """Phase 2: Adapt sets based on user's workout history — uses ProgressionEngine when available"""
        # ── Use ProgressionEngine if available ──
                # Build current params from base
                # Estimate completion from recent history
        # ── Fallback: original heuristic ──
    def _adapt_reps_based_on_history(
    # [Logic Hidden]
        """Phase 2: Adapt rep range based on user's history"""
        # Analyze recent performance
        # Check if user consistently hits top of rep range
        # Adjust rep range based on performance
            # User consistently hits top  increase difficulty
            # User struggling  decrease difficulty
    def _predict_with_ml_model(self, user_profile: Dict, target: str) -> float:
    # [Logic Hidden]
        """Phase 3: Predict using ML model if available"""
        # This would use the loaded ML models
        # For now, return rule-based fallback
    def _apply_safety_caps(self, sets: int, user_profile: Dict) -> int:
    # [Logic Hidden]
        """Apply safety caps based on user characteristics"""
        # Age caps
        # Experience caps
        # Injury considerations
        # Absolute bounds
    def _apply_age_based_rep_adjustments(self, rep_range: str, user_profile: Dict) -> str:
    # [Logic Hidden]
        """Apply age-based safety adjustments to rep range"""
            # Older adults: higher reps, lighter weight
            # Ensure minimum rep of 8 for safety
            # Younger users: moderate reps, focus on form
    def _shift_rep_range(self, rep_range: str, shift: int) -> str:
    # [Logic Hidden]
        """Shift rep range up or down"""
    def _blend_rep_ranges(self, range1: str, range2: str, weight: float) -> str:
    # [Logic Hidden]
        """Blend two rep ranges based on confidence weight"""
    def get_volume_recommendation(
    # [Logic Hidden]
        """
        """
        # Calculate intensity based on goal
        # Calculate optimal sets and reps
        # Calculate rest time
        # Build reasoning
    def _calculate_rest_time(self, intensity: float, user_profile: Dict) -> int:
    # [Logic Hidden]
        """Calculate rest time based on intensity and goal"""
        # Base rest from intensity
        # Age adjustment
        # Goal adjustment
    def _build_reasoning(
    # [Logic Hidden]
        """Build human-readable reasoning for recommendations"""
        # Experience reason
        # Goal reason
        # Age reason
        # History-based reason
# Singleton pattern
def get_hybrid_optimizer():
    # [Logic Hidden]
    """Get or create hybrid optimizer instance"""
```

## backend-python\app\main.py
```python
# ===========================================================================
# DEPRECATED — Bug #19 fixed
# ===========================================================================
# This module (app/main.py) is a legacy FastAPI application that is no longer
# the active server entry point.
#
# The canonical server is:  backend-python/server.py  (uvicorn target: server:app)
#
# app/main.py is retained for reference only. Do NOT import or launch this file.
# All active routes, Pydantic models, and business logic live in server.py.
# ===========================================================================
# Bug #6 fix: in-process rate limiter for /workout endpoint.
# Stores (timestamps deque) per IP. Max 30 requests per 5 minutes (more lenient for legitimate usage).
def _utcnow() -> datetime:
    # [Logic Hidden]
# ---------------------------------------------------------------------------
# Auth helpers shared by endpoints in main.py
# ---------------------------------------------------------------------------
def _require_user_id_from_token(token: str, request_id: str = "") -> str:
    # [Logic Hidden]
    """Decode the JWT and return the user_id string, or raise 401."""
async def _find_user_by_id(user_id: str):
    # [Logic Hidden]
    """Return the MongoDB user document for *user_id*, or None."""
# ---------------------------------------------------------------------------
def _check_workout_rate_limit(ip: str) -> Tuple[bool, int]:
    # [Logic Hidden]
    """Return (allowed, retry_after_seconds)."""
    # Prune stale client buckets periodically to avoid unbounded memory growth.
    # Remove timestamps outside the window
# ===== LOGGING CONFIGURATION =====
async def startup_event():
    # [Logic Hidden]
async def shutdown_event():
    # [Logic Hidden]
# ===== CORS CONFIGURATION (FIXED) =====
# CRITICAL: Cannot use "*" with allow_credentials=True
# Must specify exact origins
# ===== MODELS =====
class UserProfile(BaseModel):
    # [Logic Hidden]
class ProfileUpdateRequest(BaseModel):
    # [Logic Hidden]
    """Pydantic model for profile update with validation"""
class WorkoutPlanRequest(BaseModel):
    # [Logic Hidden]
class MealPlanRequest(BaseModel):
    # [Logic Hidden]
class NutritionRequest(BaseModel):
    # [Logic Hidden]
class NutritionSwapRequest(BaseModel):
    # [Logic Hidden]
# ===== MISSING ENDPOINTS (ADD THESE) =====
async def save_user_profile(profile: UserProfile):
    # [Logic Hidden]
    """Save user profile"""
async def save_workout_plan(data: dict):
    # [Logic Hidden]
    """Save workout plan"""
async def save_meal_plan(data: dict):
    # [Logic Hidden]
    """Save meal plan"""
async def save_progress(data: dict):
    # [Logic Hidden]
    """Save user progress"""
async def generate_workout_plan(request: Request):
    # [Logic Hidden]
    """
    """
        # Parse request body manually
        # Issue #1 – detect new user via firstWorkoutDay field
# ─────────────────────────────────────────────────────────────────────────────
# Issue #4 – Async workout generation with caching + polling
# ─────────────────────────────────────────────────────────────────────────────
# In-memory job store (process-scoped; for production use Redis)
async def _generate_plan_background(job_id: str, profile: dict):
    # [Logic Hidden]
    """Background task: generate workout plan and store result in _async_jobs."""
async def generate_workout_async(profile: dict, background_tasks: BackgroundTasks):
    # [Logic Hidden]
    """
    """
    # Check cache first
async def get_workout_status(job_id: str):
    # [Logic Hidden]
    """Poll for async plan generation result (Issue #4)."""
async def invalidate_workout_cache(profile: dict):
    # [Logic Hidden]
    """Invalidate cached plan for a profile (call after significant profile changes)."""
# Add these endpoints BEFORE the bottom of the file
async def generate_plan(profile: dict):
    # [Logic Hidden]
    """Generate AI workout and meal plan"""
async def generate_nutrition(request: NutritionRequest):
    # [Logic Hidden]
async def swap_food(request: NutritionSwapRequest):
    # [Logic Hidden]
async def update_profile_endpoint(profile: UserProfile):
    # [Logic Hidden]
    """
    """
        # Validate required fields
        # Simulate database update (replace with actual DB logic)
async def update_profile_and_regenerate(profile: UserProfile):
    # [Logic Hidden]
    """Update user profile and regenerate workout/meal plans if needed"""
        # Bug #49 fixed: load the EXISTING profile from DB before comparing,
        # so we compare new values against what is actually stored,
        # NOT against hardcoded default strings like "intermediate" / "general_fitness".
        # Determine if changes require plan regeneration by comparing to stored values
        def _changed(field: str) -> bool:
    # [Logic Hidden]
            """True when the new value differs from what was previously stored."""
            # For lists, compare sorted to ignore ordering differences
        # Persist the updated profile to DB
        # Regenerate workout plan if needed
        # Regenerate meal plan if needed
async def update_profile_safe(profile_data: ProfileUpdateRequest, request: Request):
    # [Logic Hidden]
    """
    """
    # Initialize response structure
        # ===== STEP 1: LOG INCOMING REQUEST =====
        # ===== STEP 2: VALIDATE INPUT =====
        # ===== STEP 3: AUTHENTICATE VIA JWT =====
        # ===== STEP 4: LOAD EXISTING PROFILE FROM DB =====
            # Bug #4 fixed: query the real user document instead of hardcoded defaults
            # Build a comparable flat profile from the stored document
        # ===== STEP 5: MERGE AND UPDATE PROFILE =====
        # ===== STEP 6: SAVE TO DATABASE =====
            # Bug #4 fixed: persist merged profile to MongoDB
        # ===== STEP 7: DETECT CHANGES FOR REGENERATION =====
        def check_workout_changes(old: dict, new: dict) -> bool:
    # [Logic Hidden]
            """Check if changes affect workout plans"""
        def check_meal_changes(old: dict, new: dict) -> bool:
    # [Logic Hidden]
            """Check if changes affect meal plans"""
        # ===== STEP 8: REGENERATE WORKOUT (ISOLATED - FAILURE WON'T BLOCK PROFILE UPDATE) =====
                # Replace with actual regeneration logic
                # workout_result = await regenerate_workout(user_id, updated_profile)
        # ===== STEP 9: REGENERATE MEAL (ISOLATED - FAILURE WON'T BLOCK PROFILE UPDATE) =====
                # Replace with actual regeneration logic
                # meal_result = await regenerate_meal(user_id, updated_profile)
        # ===== STEP 10: BUILD SUCCESS RESPONSE =====
        # Set appropriate status based on errors
# ─────────────────────────────────────────────────────────────────────────────
# Smart rest-day adjustment + 48h muscle-recovery validation
# ─────────────────────────────────────────────────────────────────────────────
class AdjustRestDaysRequest(BaseModel):
    # [Logic Hidden]
    """Request body for /workout/adjust-rest-days"""
    # Optional: days (0=Mon…6=Sun) the user explicitly wants as rest days.
    # Optional: persist preferences to the user record (requires email in profile)
async def adjust_rest_days(request: AdjustRestDaysRequest):
    # [Logic Hidden]
    """
    """
        # Clamp preferred rest days to valid range
        # Determine experience + workout day count
        # Respect user preference when they request fewer days than the recommendation.
        # Build the split
        # Determine final rest positions
            # Use exactly the preferred positions
            # Fill remaining rest slots with the smart algorithm
            # More preferences than rest slots available — use smart placement
        # Build the 7-day plan
        # Validate 48-hour muscle-group recovery
        # Persist preferences to MongoDB (best-effort, won't fail the request)
class SwapRestDayRequest(BaseModel):
    # [Logic Hidden]
    """Request to swap a rest day with the next workout day"""
async def swap_rest_day(request: SwapRestDayRequest):
    # [Logic Hidden]
    """
    """
        # Validate the rest day index
        # Validate current plan
        # Check if the specified day is actually a rest day
        # Find next workout day
        # Perform the swap
        # Optionally save the swapped plan to user preferences
# ===== EXISTING ENDPOINTS =====
async def health_check():
    # [Logic Hidden]
async def get_weekly_plan(request: WorkoutPlanRequest):
    # [Logic Hidden]
    """Generate weekly workout plan"""
async def get_daily_meals(request: MealPlanRequest):
    # [Logic Hidden]
    """Generate daily meal plan"""
# ===== STARTUP =====
async def startup_event():
    # [Logic Hidden]
async def shutdown_event():
    # [Logic Hidden]
```

## backend-python\app\meal_engine.py
```python
"""
"""
class MealEngine:
    # [Logic Hidden]
    """
    """
    def __init__(self):
    # [Logic Hidden]
    def _normalize_intensity(self, value: str) -> str:
    # [Logic Hidden]
    def _day_name_from_workout(self, day: Dict) -> str:
    # [Logic Hidden]
    def _infer_intensity_from_workout_day(self, day: Dict) -> str:
    # [Logic Hidden]
    def _build_intensity_by_day(self, user_profile: Dict, fallback_intensity: str) -> Dict[str, str]:
    # [Logic Hidden]
    def _scale_meal_item(self, item: Dict, factor: float) -> Dict:
    # [Logic Hidden]
            # Source of truth: nutrition sub-dict (set by portion_optimizer)
        # food_name / name consistency
        # serving string scaling
    def _apply_intensity_adjustments(self, weekly_plan: Dict, intensity_by_day: Dict[str, str], profile: Dict = None) -> Dict:
    # [Logic Hidden]
        """Apply day-level intensity targets to a generated weekly meal plan without redundant scaling."""
        # V6 now keys weekly_plan by day name (Monday..Sunday) directly.
        # Keep a fallback mapping for any legacy Day_N keys that may exist in the cache.
        # Reverse: day_name -> Day_N key used in plan_week() daily_targets
        # daily_targets is still keyed as Day_1..Day_7 from WeeklyMacroPlanner.plan_week()
            # Resolve to a human-readable day name
                    # V6 WeeklyOptimizer already optimises portions for each day's
                    # intensity-adjusted calorie target — do NOT scale again here.
                    # Scaling would cause protein to swing ±15% across days even
                    # though the weekly plan intentionally keeps protein constant.
            # Retrieve the planned target: try legacy Day_N key first, then day_name directly
    # ─────────────────────────────────────────────
    #  suggest_daily_meals — called by /nutrition
    # ─────────────────────────────────────────────
    def suggest_daily_meals(self, user_profile: Dict,
    # [Logic Hidden]
        """
        """
    # ─────────────────────────────────────────────
    #  generate_meal_plan — weekly with workout integration
    # ─────────────────────────────────────────────
    def generate_meal_plan(self, profile: Dict,
    # [Logic Hidden]
        """
        """
        # Call V6 Engine
        # Apply intensity adjustments on top of the V6 plan
    def get_swap_options(self, food_name: str, meal_type: str,
    # [Logic Hidden]
        """
        """
        # 1. Find the target node
        # Step 1a: exact match
        # Step 1b: substring match fallback
        def get_node_role(node: Dict) -> str:
    # [Logic Hidden]
            # Fallback mapping using keywords or category
        # Determine target calories and macros
        # Extract User Diet (case-insensitive sub-string match)
        def _is_diet_compatible(meal_diet: str, user_diet: str) -> bool:
    # [Logic Hidden]
        # Extract Allergies and Exclusions
        # Collect suitable options from FoodGraph
            # Must be nutrition-valid
            # Exclude zero nutrition
            # Diet compatibility
            # Suitability check
            # Allergy Check
        # Regional Preference priorities
        def snap_portion(grams, node):
    # [Logic Hidden]
        def _scale_and_score(node):
    # [Logic Hidden]
            # Grams needed to hit calorie target
            # Snap portion
            # Compute macro score
            # Role compatibility score
            # Family penalty (Phase 7: Prevent same-family swaps)
            # Cuisine preference score
            # Sorting key: 1) Same role, 2) Family penalty, 3) Same cuisine preference, 4) Similar macros
        # Sort based on multi-criteria key
        # Format results
def get_meal_engine():
    # [Logic Hidden]
```

## backend-python\app\ml_utils.py
```python
# --- PATH CONFIGURATION ---
class MLService:
    # [Logic Hidden]
    def __init__(self):
    # [Logic Hidden]
        # 1. Define Paths (Priority: Processed > Raw)
    def load_data(self):
    # [Logic Hidden]
        # --- LOAD EXERCISES ---
        # --- LOAD NUTRITION ---
        # Safety Fills to prevent crashes
    def calculate_macros(self, user):
    # [Logic Hidden]
        """ Calculates BMR & Macros based on Goal """
    def recommend_workout(self, user_profile, equipment_list):
    # [Logic Hidden]
        """ Generates the Fixed Plan (Objective #1) """
        # 1. Equipment Filter
        # 2. Injury Filter (Objective #1 - Safety)
        # 3. Split Logic
            # Muscle Mapping
                    # --- OBJECTIVE #17: PROGRESSIVE OVERLOAD ---
    def recommend_meals(self, goal, preference, allergies, target_calories):
    # [Logic Hidden]
        """ Generates Meal Plan (Objective #2) """
    def recommend_weekly_meals(self, goal, preference, allergies, weekly_workout_plan):
    # [Logic Hidden]
        """ Generates a fixed weekly meal plan aligned with the workout structure """
        # Generate a meal plan for each day of the week
            # Calculate daily calories based on workout intensity
            # For now, use a consistent daily calorie target
            # Define meal targets for each day
                    # Default meal if none found
    def recommend_weekly_workout(self, user_profile, equipment_list):
    # [Logic Hidden]
        """ Generates a 7-day weekly workout plan that repeats by default """
        # 1. Equipment Filter
        # 2. Injury Filter (Safety)
        # 3. Weekly Split based on experience and days per week
        # Define weekly schedule based on experience and days
                # Add light stretching or recovery activities
                # Add cardio exercises
                    # Default cardio if none found
                # Add light movement and stretching
                # Muscle Mapping for workout days
                        # Determine sets/reps based on experience
    # --- NEW: SWAP FUNCTION (Restored for your Button) ---
    def get_alternative_meal(self, swap_group, exclude_name):
    # [Logic Hidden]
        """ Finds a different meal in the same group """
# Create Singleton
```

## backend-python\app\multi_output_xgboost_model.py
```python
"""
"""
class MultiOutputXGBoostModel:
    # [Logic Hidden]
    """
    """
    def __init__(self, random_state: int = 42):
    # [Logic Hidden]
        # Safety bounds for predictions
        # Initialize the base model
        # Wrap with MultiOutputRegressor
    def _prepare_features(self, df: pd.DataFrame) -> Tuple[pd.DataFrame, np.ndarray]:
    # [Logic Hidden]
        """
        """
        # Define feature columns (these should match your feature pipeline output)
        # Select features
        # Ensure all values are numeric
        # Store feature names
        # Define target columns
    def _create_synthetic_data(self, n_samples: int = 1000) -> pd.DataFrame:
    # [Logic Hidden]
        """
        """
        # Generate synthetic user profiles
        # Generate realistic target values based on features
        # Sets: More experienced users tend to do more sets
        # Reps: Beginners do higher reps, advanced do lower reps for strength
        # Rest time: More intense workouts need more rest
        # Intensity: Based on experience and recovery
        # Ensure targets are within bounds
    def train(self,
    # [Logic Hidden]
        """
        """
        # Prepare training data
            # If X_train is already processed
        # Prepare validation data if provided
        # Hyperparameter tuning
            # Define parameter grid
            # Use TimeSeriesSplit for temporal data
            # Perform randomized search
            # Fit the random search
            # Update model with best parameters
            # Train with default parameters
        # Evaluate the model
    def _calculate_rmse(self, y_true: np.ndarray, y_pred: np.ndarray) -> Dict[str, float]:
    # [Logic Hidden]
        """
        """
    def _extract_feature_importance(self) -> Dict[str, List[float]]:
    # [Logic Hidden]
        """
        """
    def predict(self, X: pd.DataFrame) -> np.ndarray:
    # [Logic Hidden]
        """
        """
        # Prepare features
        # Make predictions
        # Apply safety layer
    def _apply_safety_layer(self, predictions: np.ndarray, X: pd.DataFrame) -> np.ndarray:
    # [Logic Hidden]
        """
        """
        # Create a copy to avoid modifying original
        # Clamp each target within safe bounds
        # Apply beginner intensity cap
                # Assuming experience_encoded is at index 5 based on feature order
            # For beginners (experience_encoded == 0), cap intensity at 0.7
        # Apply set bounds based on experience
            # For beginners, cap sets at 4
    def save_model(self, model_path: str = None) -> str:
    # [Logic Hidden]
        """
        """
        # Create directory if it doesn't exist
        # Prepare model info
        # Save the model package
    def load_model(self, model_path: str):
    # [Logic Hidden]
        """
        """
        # Calculate and verify checksum
        # For now, we'll just log the checksum - in production, this would be compared to a known good value
        # Verify required keys exist
    def evaluate(self, X_test: pd.DataFrame, y_test: np.ndarray) -> Dict:
    # [Logic Hidden]
        """
        """
        # Calculate metrics
        # Calculate RMSE per target
        # Calculate R score
def create_training_pipeline():
    # [Logic Hidden]
    """
    """
    # Initialize the model
    # Create synthetic training data
    # Prepare features and targets
    # Split the data (time-based split)
    # Further split training for validation
    # Train the model
    # Evaluate on test set
    # Save the model
    # Demonstrate inference
    # Show feature importance
def production_notes():
    # [Logic Hidden]
    """
    """
    """
    # Run the complete pipeline
    # Print production notes
```

## backend-python\app\multitarget_nutrition_model.py
```python
"""
"""
class MultiTargetNutritionModel:
    # [Logic Hidden]
    """
    """
    def __init__(self, random_state: int = 42):
    # [Logic Hidden]
        # Initialize the base model
        # Wrap with MultiOutputRegressor
    def _prepare_features(self, df: pd.DataFrame) -> Tuple[pd.DataFrame, np.ndarray]:
    # [Logic Hidden]
        """
        """
        # Define feature columns (these should match your user profile features)
        # Select features
        # Ensure all values are numeric
        # Store feature names
        # Define target columns
    def _create_synthetic_data(self, n_samples: int = 1000) -> pd.DataFrame:
    # [Logic Hidden]
        """
        """
        # Generate synthetic user profiles
        # Calculate BMR using Mifflin-St Jeor equation
        # Calculate TDEE based on activity level
        # Adjust TDEE based on goal
        # Generate realistic target values based on features
        # Calorie distribution by meal
        # Calculate total calories
        # Calculate macros based on goal and dietary preferences
        # Protein requirements (g per kg body weight)
        # Carbs and fats based on goal
        # Apply macros based on goal
        # Ensure protein is calculated properly
        # Recalculate carbs to account for protein and fat
        # Ensure all targets are within reasonable bounds
    def train(self,
    # [Logic Hidden]
        """
        """
        # Prepare training data
            # Create a temporary dataframe with features and targets to use _prepare_features
            # If X_train is already processed
        # Prepare validation data if provided
        # Hyperparameter tuning
            # Define parameter distributions
            # Use TimeSeriesSplit for temporal data
            # Perform randomized search with MAE as the scoring metric
            # Fit the random search
            # Update model with best parameters
            # Train with default parameters
        # Evaluate the model
    def _calculate_mae(self, y_true: np.ndarray, y_pred: np.ndarray) -> Dict[str, float]:
    # [Logic Hidden]
        """
        """
    def _calculate_rmse(self, y_true: np.ndarray, y_pred: np.ndarray) -> Dict[str, float]:
    # [Logic Hidden]
        """
        """
    def _extract_feature_importance(self) -> Dict[str, List[float]]:
    # [Logic Hidden]
        """
        """
    def predict(self, X: pd.DataFrame) -> np.ndarray:
    # [Logic Hidden]
        """
        """
        # Prepare features
            # Create a temporary dataframe to use _prepare_features
            # Add placeholder target columns to satisfy _prepare_features
        # Make predictions
        # Apply post-processing constraints
    def _apply_post_processing_constraints(self, predictions: np.ndarray, X: pd.DataFrame) -> np.ndarray:
    # [Logic Hidden]
        """
        """
        # Create a copy to avoid modifying original
        # Calculate original total calories per sample
        # Calculate target TDEE for each sample (this would come from user profile in practice)
        # For demonstration, we'll calculate it based on the features
            # Calculate BMR and TDEE based on features
            # Activity multipliers
            # TDEE calculation
            # Adjust based on goal
            # If X is not a DataFrame, use a default approach
        # Adjust meal calories to match TDEE target
                # Apply adjustment to meal calories
        # Now adjust macros proportionally to match the new total calories
        # Calculate new total calories after adjustment
        # Adjust protein, carbs, and fats proportionally
                # Calculate the ratio of each macro to the total
                # Apply the same ratios to the new total calories
                # But ensure they stay within reasonable bounds
        # Apply bounds to ensure realistic values
        # Meal calories bounds
        # Macro bounds
    def save_model(self, model_path: str = None) -> str:
    # [Logic Hidden]
        """
        """
        # Create directory if it doesn't exist
        # Prepare model info
        # Save the model package
    def load_model(self, model_path: str):
    # [Logic Hidden]
        """
        """
        # Calculate and verify checksum
        # For now, we'll just log the checksum - in production, this would be compared to a known good value
        # Verify required keys exist
    def evaluate(self, X_test: pd.DataFrame, y_test: np.ndarray) -> Dict:
    # [Logic Hidden]
        """
        """
        # Calculate metrics
        # Calculate MAE and RMSE per target
        # Calculate R score
def create_nutrition_training_pipeline():
    # [Logic Hidden]
    """
    """
    # Initialize the model
    # Create synthetic training data
    # Prepare features and targets
    # Split the data (time-based split)
    # Further split training for validation
    # Train the model
    # Evaluate on test set
    # Save the model
    # Demonstrate inference
    # Show feature importance for the first target (breakfast calories)
def validation_checks(model: MultiTargetNutritionModel, X_test: pd.DataFrame, y_test: np.ndarray):
    # [Logic Hidden]
    """
    """
    # Make predictions
    # Check 1: Total calories match TDEE target (approximately)
    # Check 2: All values are positive
    # Check 3: Values are within reasonable bounds
    # Check 4: Protein, carbs, and fats sum is approximately equal to total calories
    # Run the complete pipeline
    # Perform validation checks
    # Create test data for validation
```

## backend-python\app\nutrition_intelligence.py
```python
"""
"""
class NutritionIntelligenceEngine:
    # [Logic Hidden]
    """
    """
    def __init__(self, nutrition_data_path: str = None):
    # [Logic Hidden]
        # Initialize multi-target nutrition model
        # Load nutrition data
            # Fallback data
        # Define macro ratios by goal
        # Activity multipliers
        # Protein requirements (g per kg of body weight)
        # Encode categorical variables for the model
    def validate_user_input(self, user_profile: Dict) -> Dict:
    # [Logic Hidden]
        """
        """
        # Required fields with defaults
        # Validate ranges
    def calculate_derived_metrics(self, user_profile: Dict) -> Dict:
    # [Logic Hidden]
        """
        """
        # Validate and clamp extreme values
        # BMR calculation (Mifflin-St Jeor Equation)
        # Clamp BMR to reasonable range
        # TDEE calculation
        # Clamp TDEE to reasonable range
        # Calorie target based on goal
        # Clamp calorie target to reasonable range
        # Protein requirement (g per kg body weight)
        # Clamp protein requirement to reasonable range
        # Macro targets based on goal
        # Convert to grams
        # Fiber minimum (25g for women, 38g for men, or 14g per 1000 calories)
    def apply_hard_constraints(self, foods_df: pd.DataFrame, user_profile: Dict) -> pd.DataFrame:
    # [Logic Hidden]
        """
        """
        # Exclude allergens (only if column exists)
                # Log warning but continue
        # Dietary preference constraints
        # Food dislikes
        # Remove null calorie entries
    def calculate_meal_splits(self, daily_calories: float) -> Dict[str, float]:
    # [Logic Hidden]
        """
        """
    def select_meals_for_day(self, available_foods: pd.DataFrame,
    # [Logic Hidden]
        """
        """
            # Filter by meal type if available
                # Try to match meal type, but fall back to all if none match
            # Avoid recently used meals (3-day rule)
                # Check if 'name' column exists before filtering
            # If no foods left after filtering, use original set
            # If still empty, use fallback foods
            # Select meals that best match target calories
            # If no meals were selected, use fallback
    def _get_fallback_foods(self, meal_type: str) -> pd.DataFrame:
    # [Logic Hidden]
        """
        """
        # Create minimal fallback foods based on meal type
    def _get_fallback_meal(self, meal_type: str, target_calories: float) -> List[Dict]:
    # [Logic Hidden]
        """
        """
    def _select_meals_by_calories(self, foods_df: pd.DataFrame, target_calories: float, meal_type: str) -> List[Dict]:
    # [Logic Hidden]
        """
        """
        # Sort by proximity to target calories
            # If this food fits reasonably well
        # If no meals were selected, pick the closest one
    def generate_weekly_plan(self, user_profile: Dict) -> Dict:
    # [Logic Hidden]
        """
        """
        # Validate and derive metrics
        # Prepare features for the multi-target model
        # Use the multi-target model to predict nutrition parameters
            # Extract predictions
            # Fallback to original method
        # Apply hard constraints
        # Create meal splits based on model predictions
        # Generate weekly plan
            # Get previous days' meals for diversity
            # Select meals for this day
            # Add to tracking
        # Calculate weekly consistency score
        # Generate shopping list
        # Create final output
    def _prepare_features_for_model(self, user_profile: Dict) -> pd.DataFrame:
    # [Logic Hidden]
        """
        """
        # Create a single-row DataFrame with the user's features
    def _calculate_weekly_consistency(self, weekly_plan: Dict, user_profile: Dict) -> float:
    # [Logic Hidden]
        """
        """
        # Calculate actual totals
        # Calculate target totals for the week
        # Calculate consistency score (0-1, where 1 is perfect)
        # Average consistency (clamped between 0 and 1)
    def _generate_shopping_list(self, weekly_plan: Dict) -> Dict:
    # [Logic Hidden]
        """
        """
    def _calculate_weekly_macros(self, weekly_plan: Dict) -> Dict:
    # [Logic Hidden]
        """
        """
    def swap_meal(self, weekly_plan: Dict, day: str, meal_type: str, new_meal: str) -> Dict:
    # [Logic Hidden]
        """
        """
        # This would implement meal swapping logic
        # For now, we'll just return the plan unchanged
        # In a full implementation, this would validate the swap against constraints
def explain_nutrition_engine_design():
    # [Logic Hidden]
    """
    """
    """)
    """)
    """)
    """)
    """)
    """)
    # Example usage
    # Example user profile
    # Generate weekly plan
    # Explain the design
```

## backend-python\app\plan_cache.py
```python
# -*- coding: utf-8 -*-
"""
"""
# ─────────────────────────────────────────────────────────────────────────────
# Optional Redis import
# ─────────────────────────────────────────────────────────────────────────────
class PlanCache:
    # [Logic Hidden]
    """
    """
    def __init__(self, redis_host: str = 'localhost', redis_port: int = 6379,
    # [Logic Hidden]
    def _disable_redis(self, reason: str) -> None:
    # [Logic Hidden]
    # ─────────────────────────────────────────────────────────────────────────
    # Key generation
    # ─────────────────────────────────────────────────────────────────────────
    def _generate_key(self, profile: dict, week_offset: int = 0) -> str:
    # [Logic Hidden]
        """Deterministic cache key from stable profile fields + ISO-week number."""
            # Bug fix: Include body metrics in cache key so weight/height/age
            # changes produce a new plan instead of returning stale cached plan
    # ─────────────────────────────────────────────────────────────────────────
    # Public API
    # ─────────────────────────────────────────────────────────────────────────
    def get(self, profile: dict) -> Optional[Dict]:
    # [Logic Hidden]
        """Return cached plan, or None if missing/expired."""
        # Level 1 – memory
        # Level 2 – Redis
                    # Warm L1
    def set(self, profile: dict, plan: dict) -> None:
    # [Logic Hidden]
        """Store plan in both levels."""
        # Level 1
        # Level 2
    def invalidate(self, profile: dict) -> None:
    # [Logic Hidden]
        """Remove cached plan for a profile (call after profile change)."""
    def clear_all(self) -> None:
    # [Logic Hidden]
        """Clear all in-memory entries (Redis keys survive process lifetime)."""
# ─────────────────────────────────────────────────────────────────────────────
# Singleton factory
# ─────────────────────────────────────────────────────────────────────────────
def get_plan_cache() -> PlanCache:
    # [Logic Hidden]
```

## backend-python\app\pose_tracker.py
```python
# --- Import MediaPipe safely ---
def _ensure_cv2() -> bool:
    # [Logic Hidden]
class PoseTracker:
    # [Logic Hidden]
    def __init__(self):
    # [Logic Hidden]
    def _configure_detector(self, exercise_name):
    # [Logic Hidden]
    def process_frame(self, frame):
    # [Logic Hidden]
        # Handle case where AI is not available
            # Return original frame with error message if AI is not available
            # Return original frame with error indication
            # --- 1. BICEP CURL (Arms) ---
            # --- 2. SQUAT (Legs) ---
            # --- 3. PUSH-UP (Chest) ---
                # Calculate Elbow Angle
                # Push-up Logic (Check if body is horizontal roughly)
            # --- CHECK COMPLETION ---
        # ... (Drawing code remains the same)
        # Draw Scoreboard
    def set_exercise(self, exercise_name):
    # [Logic Hidden]
        """Switch the tracking logic based on user selection"""
        # Reset the exercise state before setting a new exercise
        # Set target reps based on exercise type (could be customized per exercise)
    def calculate_angle(self, a, b, c):
    # [Logic Hidden]
        """Calculate angle between three points"""
    def get_confidence(self, landmarks):
    # [Logic Hidden]
        """Return an average visibility score for the current landmarks."""
    def check_form_correctness(self, pose_landmarks):
    # [Logic Hidden]
        """Check if the current pose matches the expected form for the exercise"""
            # Define exercise-specific form checks
                # For bicep curl, check if shoulders are stable and not swinging
                # Check if shoulders are relatively stable (not moving excessively)
                # Check if the elbow is moving in the correct plane
                # Check if the movement is primarily in the sagittal plane (front-back)
                # For bicep curls, the wrist should stay relatively in line with the shoulder
                # For squat, check if knees track over toes and back stays straight
                # Check if knee tracks over ankle (not collapsing inward)
                # Check if hips and shoulders stay aligned
                # For pushup, check if body stays in straight line
                # Check if body is in straight line (shoulder-hip-ankle alignment)
                # For shoulder press, check if core stays engaged and movement is vertical
                # Check if torso remains relatively vertical (not leaning back excessively)
                # For lunge, check if front knee tracks over toe and back leg is stable
                # Check if knee tracks over ankle (not collapsing inward)
            # Default to True if exercise not recognized
    def process_frame(self, frame):
    # [Logic Hidden]
        # Create space for exercise GIF on the left side of the frame
        # Assuming the original frame dimensions
        # Create a new frame with extra space on the left for the GIF
        # Place the original camera frame on the right side
        # Draw a border to separate the GIF area from the camera feed
        # Add exercise name in the GIF area
        # Add instruction text in the GIF area
            # Check if pose detection was successful
                # Handle case where no pose landmarks were detected
                # Return early since there are no landmarks to process
            # Show error message on the frame
            # Determine if the form is correct based on the exercise and current stage
            # Define colors based on form correctness
                # Green for correct form
                # Red for incorrect form
            # Draw Skeleton with color based on form correctness
            # We need to draw each connection individually to control colors
                # --- GET KEY BODY POINTS ---
                # Left Side
                # --- EXERCISE LOGIC SWITCHER ---
                # Define exercise-specific thresholds
                # Only update rep counting if exercise is not completed
                    # 1. BICEP CURL (Arm Angle)
                    # 2. SQUAT (Knee Angle)
                        # Angle between Hip, Knee, Ankle
                    # 3. PUSHUP (Elbow Angle + Body Alignment)
                    # 4. SHOULDER PRESS (Shoulder-Elbow-Wrist, but vertical)
                    # 5. LUNGE (Hip-Knee-Ankle like squat, but different threshold)
                # Check if exercise is completed (after all sets)
                # Assuming target reps are set elsewhere - default to 10 for demo purposes
                    # Exercise completed - show green tick and disable interaction
                    # Keep the skeleton visible but prevent rep counting
                    # Draw a semi-transparent overlay to indicate completion
                    # Draw green tick symbol
                    # Draw a large green tick mark
                    # Add completion text
                    # Add rep count
                    # Mark as completed to prevent further interaction
                    # Still draw the skeleton but don't update rep count
                    # We'll draw the skeleton with a neutral color since the exercise is done
                    # Regular UI when exercise is ongoing
                    # Draw Blue Box for text on the camera feed side
                    # Exercise Name
                    # Counter
                    # Stage
    def handle_camera_error(self, frame, error_message):
    # [Logic Hidden]
        """Handle camera-related errors gracefully"""
            # Show error message on the frame
    def handle_pose_detection_failure(self, frame):
    # [Logic Hidden]
        """Handle pose detection failures gracefully"""
            # Show message indicating pose detection is not working
    def handle_no_pose_landmarks(self, combined_frame, gif_width):
    # [Logic Hidden]
        """Handle case where no pose landmarks are detected"""
        # Show message in the camera area that pose is not detected
    def is_exercise_finished(self):
    # [Logic Hidden]
        """Check if the exercise is completed"""
    def skip_current_exercise(self):
    # [Logic Hidden]
        """Mark the current exercise as skipped"""
    def is_exercise_skipped_flag(self):
    # [Logic Hidden]
        """Check if the current exercise was skipped"""
    def reset_exercise_state(self):
    # [Logic Hidden]
        """Reset the exercise state to allow a new exercise"""
    def start_workout_session(self, workout_plan):
    # [Logic Hidden]
        """Initialize a new workout session with the given plan"""
        # Set the first exercise
    def mark_exercise_completed(self):
    # [Logic Hidden]
        """Mark the current exercise as completed and add to completed list"""
            # Update streak when exercise is completed
            # Log the activity for analytics
    def mark_exercise_skipped(self):
    # [Logic Hidden]
        """Mark the current exercise as skipped and add to skipped list"""
            # Update streak when exercise is skipped
            # Log the activity for analytics
    def is_workout_completed(self):
    # [Logic Hidden]
        """Check if all exercises in the workout have been completed or skipped"""
    def get_current_exercise_index(self):
    # [Logic Hidden]
        """Get the index of the current exercise in the workout plan"""
        # Find the current exercise in the plan
    def get_next_exercise(self):
    # [Logic Hidden]
        """Get the next exercise in the workout plan"""
    def move_to_next_exercise(self):
    # [Logic Hidden]
        """Move to the next exercise in the workout plan"""
    def update_streak(self, workout_completed_today=True):
    # [Logic Hidden]
        """Update the workout streak based on consecutive days"""
            # Increment completed workouts count
            # Increment skipped workouts count
            # First workout
            # Calculate days since last workout
                # Consecutive day - increment streak
                # Same day - no change to streak
                # Break in streak - reset to 1
        # Update intensity based on streak
    def update_intensity_based_on_streak(self):
    # [Logic Hidden]
        """Gradually increase intensity based on streak"""
        # Store previous values to determine if there was a change
        # Increase intensity gradually based on streak
        # Every 3 days of streak, slightly increase intensity
        # Adjust reps and sets based on intensity
        # Cap the increases to ensure safety
        # Generate explanation for intensity change
    def get_intensity_explanation(self):
    # [Logic Hidden]
        """Get explanation for current intensity level"""
    def get_adjusted_workout_params(self):
    # [Logic Hidden]
        """Get the adjusted workout parameters based on streak"""
    def adjust_meal_macros_for_intensity(self, base_macros):
    # [Logic Hidden]
        """Adjust meal plan macros based on workout intensity"""
        # Increase calories and protein based on intensity
        # Increase calories proportionally to intensity
        # Increase protein for muscle recovery based on intensity
        # Slightly adjust carbs and fats based on workout intensity
    def adjust_meal_plan_by_experience_level(self, base_macros):
    # [Logic Hidden]
        """Adjust meal plan based on experience level"""
            # Beginner: Recovery focused - moderate calories, balanced nutrients
            # Add more recovery-focused nutrients
            # Intermediate: Higher protein for muscle building and repair
            # Add more protein-focused nutrients
            # Advanced: Performance focused - higher calories, optimized macros
            # Add performance-focused nutrients
            # Default to base macros if level is unknown
    def get_meal_plan_recommendations(self):
    # [Logic Hidden]
        """Get specific meal plan recommendations based on experience level"""
    def load_exercise_dataset(self):
    # [Logic Hidden]
        """Load the exercise dataset from the data files"""
        # fixed path: backend-python/data (not app/data)
        # Load exercise data
    def validate_exercise_dataset(self):
    # [Logic Hidden]
        """Validate the exercise dataset against current workout execution logic"""
        # Required columns for workout execution logic
        # Additional columns for sets, reps, and difficulty
            # Check required columns exist
            # Check if exercise has the required body keypoints for posture detection
            # This is implicit in MediaPipe - we assume all exercises can use the standard landmarks
            # but we should check if Target_Muscle is properly defined
            # Check if equipment is properly defined
            # Check if difficulty is properly defined
            # Check if exercise has metadata for sets and reps
            # Determine if exercise is valid
        # Prepare validation report
    def evaluate_dataset_sufficiency(self):
    # [Logic Hidden]
        """Evaluate whether the current dataset is sufficient for all supported goals, levels, and exercises"""
        # Load exercise data
        # Load nutrition data
        # Define supported goals
        # Define experience levels
        # Define equipment categories
        # Define target muscle groups
        # Define difficulty levels
        # Evaluate exercise dataset sufficiency
            # Count exercises by goal (based on equipment and muscle groups)
                # For now, we'll count exercises that could support each goal
                # This is a simplified approach - in reality, you'd need more complex logic
            # Count exercises by experience level
                # Get unique difficulties
            # Count exercises by equipment
                # Get unique equipment
            # Count exercises by target muscle
                # Get unique muscles
            # Count exercises by difficulty
        # Evaluate nutrition dataset sufficiency
            # Count meals by dietary preference
            # Count meals by type
            # Get allergen coverage
            # Get calorie ranges
        # Identify gaps in exercise variety
            # Check if all muscle groups are covered
            # Check if all equipment categories are covered
            # Check if all difficulty levels are covered
        # Identify gaps in meal data
            # Check if all dietary preferences are covered
            # Check if all meal types are covered
        # Overall sufficiency assessment
        # Generate recommendations based on gaps
        # Combine all evaluations
    def get_analytics_data(self):
    # [Logic Hidden]
        """Get analytics data for charts based on user activity"""
        # Calculate various metrics for analytics
        # Count meal logs from activity log
        # Prepare analytics data
    def get_last_meal_log(self):
    # [Logic Hidden]
        """Get the most recent meal log from activity log"""
    def calculate_trends(self):
    # [Logic Hidden]
        """Calculate daily, weekly, and overall trends from activity data"""
        # Initialize trend data
        # Get activity log
        # Convert timestamps to datetime objects
                    # If parsing fails, skip this entry
        # Sort by timestamp
        # Calculate daily trends (last 7 days)
            # Only consider last 7 days for daily trends
                # Count workouts
                # Count meals
        # Fill in missing days with 0
        # Calculate weekly trends (last 4 weeks)
            # Calculate week number for i weeks ago
            # Count activities for this week
        # Calculate overall trends
        # Calculate consistency metrics
        # Calculate trend analysis
        # Analyze daily workout trend
        # Analyze weekly workout trend
    def update_activity_log(self, activity_type, details=None):
    # [Logic Hidden]
        """Log user activity for analytics tracking"""
        # Store in a temporary log (in a real app, this would go to a database)
        # Keep only recent activities (last 30 entries)
    def log_meal_completion(self, meal_info, calories_consumed=None):
    # [Logic Hidden]
        """Log meal completion for analytics tracking"""
        # Store in activity log
        # Keep only recent activities (last 30 entries)
    def calculate_skip_rate(self):
    # [Logic Hidden]
        """Calculate the skip rate for the user"""
    def calculate_average_form_accuracy(self):
    # [Logic Hidden]
        """Calculate the average form accuracy based on stored scores"""
    def add_form_accuracy_score(self, score):
    # [Logic Hidden]
        """Add a form accuracy score to the tracking list"""
        # Limit to last 20 scores to keep it recent
    def get_exercise_stats(self):
    # [Logic Hidden]
        """Return a compatibility summary used by the refactored tests/UI."""
        # Detectors return 0–100; normalise to 0.0–1.0 for build_form_feedback
    def get_tracking_statistics(self):
    # [Logic Hidden]
        """Return the tracking coverage summary expected by the regression tests."""
    def evaluate_upgrade_readiness(self):
    # [Logic Hidden]
        """Evaluate if user is ready to upgrade from Beginner to Intermediate or Intermediate to Advanced"""
        # Calculate various metrics
        # Define thresholds based on current level
            # Beginner to Intermediate thresholds
            # Intermediate to Advanced thresholds (stricter requirements)
            # Already at highest level or unknown level
        # Calculate readiness score (0-100)
        # Streak contribution (0-40 points)
        # Skip rate contribution (0-30 points)
        # Form accuracy contribution (0-30 points)
        # Store the score and check if upgrade is suggested
        # Check if user meets all criteria for upgrade suggestion
        # Generate explanation for upgrade readiness
            # Explain what's needed to reach the next level
    def suggest_upgrade(self):
    # [Logic Hidden]
        """Return upgrade suggestion if user is ready"""
            # Customize message based on current level
    def draw_styled_landmarks(self, image, pose_landmarks, landmark_color, connection_color):
    # [Logic Hidden]
        """Draw landmarks and connections with custom colors based on form correctness"""
        # Draw connections
            # Get coordinates
            # Convert to pixel coordinates
            # Draw line with specified connection color
        # Draw landmarks
            # Convert to pixel coordinates
            # Draw landmark point with specified landmark color
```

## backend-python\app\prescription_targets.py
```python
# -*- coding: utf-8 -*-
"""
"""
# ── Water targets (ml) ─────────────────────────────────────────────────────
    # Alias keys used in existing codebase
def get_water_target(goal: str, age: Union[int, float]) -> int:
    # [Logic Hidden]
    """
    """
# ── Sleep targets (hours) ──────────────────────────────────────────────────
    # Alias keys
def get_sleep_target(level: str, *, optimal: bool = True) -> float:
    # [Logic Hidden]
    """
    """
# ── Convenience: both targets in one call ──────────────────────────────────
def get_prescription_targets(goal: str, level: str, age: Union[int, float]) -> dict:
    # [Logic Hidden]
    """
    """
```

## backend-python\app\profile_change_detection.py
```python
"""
"""
# Configuration
# BUG-4 fix: Use lazy initialization so the module can be imported even when
# Redis / Celery are not available (e.g., unit tests, fresh developer machines).
def _get_redis_client():
    # [Logic Hidden]
    """Return a cached Redis client, creating it on first use."""
def _get_celery_app():
    # [Logic Hidden]
    """Return a cached Celery application, creating it on first use."""
class ChangeType(Enum):
    # [Logic Hidden]
    """Types of profile changes that trigger regeneration"""
class ProfileChange:
    # [Logic Hidden]
    """Represents a detected profile change"""
class ProfileChangeDetector:
    # [Logic Hidden]
    """
    """
    def __init__(self):
    # [Logic Hidden]
    def _setup_logging(self) -> logging.Logger:
    # [Logic Hidden]
        """Setup logging for the detector"""
        # Prevent handler growth when this class is instantiated repeatedly.
    def _generate_profile_hash(self, profile: Dict) -> str:
    # [Logic Hidden]
        """Generate a hash of the profile for comparison"""
        # Only include fields that matter for regeneration
        # Convert to JSON string and hash
    def _get_cached_profile_hash(self, user_id: str) -> Optional[str]:
    # [Logic Hidden]
        """Retrieve cached profile hash from Redis"""
    def _set_cached_profile_hash(self, user_id: str, profile_hash: str):
    # [Logic Hidden]
        """Store profile hash in Redis"""
        # Cache for 30 days
    def _invalidate_plan_cache(self, user_id: str):
    # [Logic Hidden]
        """Invalidate cached plans for the user"""
    def _get_previous_profile(self, user_id: str) -> Optional[Dict]:
    # [Logic Hidden]
        """Retrieve previous profile from Redis"""
    def _store_current_profile(self, user_id: str, profile: Dict):
    # [Logic Hidden]
        """Store current profile in Redis"""
        # Store for 30 days
    def detect_changes(self, user_id: str, current_profile: Dict) -> List[ProfileChange]:
    # [Logic Hidden]
        """
        """
        # Validate the incoming profile data
        # Get previous profile hash
        # If hashes are different, there are changes
            # Get previous profile to determine what changed
                # Compare each field that matters for regeneration
            # Update cached hash and profile
    def _compare_profile_fields(self, user_id: str, old_profile: Dict, new_profile: Dict) -> List[ProfileChange]:
    # [Logic Hidden]
        """Compare profile fields and detect changes"""
        # Compare goal
        # Compare experience
        # Compare equipment
        # Compare injuries
        # Compare days per week
        # Compare weight (with threshold)
        # Compare height
        # Compare age
    def _validate_profile_data(self, profile: Dict) -> Dict:
    # [Logic Hidden]
        """Validate and sanitize profile data"""
        # Validate age range (18-80)
        # Validate weight range (40-200 kg)
        # Validate height range (120-250 cm)
        # Validate days per week (1-7)
        # Validate experience level
        # Validate goal
        # Validate equipment list
        # Validate body issues list
def trigger_regeneration_task(self, user_id: str, changes: List[Dict]):
    # [Logic Hidden]
    """
    """
        # Invalidate cache
        # Here you would call the actual regeneration logic
        # For example: regenerate_workout_plan(user_id) or regenerate_nutrition_plan(user_id)
        # This is a placeholder for the actual regeneration logic
        # Update change records to mark as triggered
            # In a real implementation, you would update the database record
            # update_change_record(change)
        # Retry the task
class ProfileChangeManager:
    # [Logic Hidden]
    """
    """
    def __init__(self):
    # [Logic Hidden]
    def process_profile_update(self, user_id: str, profile: Dict) -> Dict:
    # [Logic Hidden]
        """
        """
            # Detect changes
            # Convert changes to serializable format
            # Check if regeneration is already in progress
            # Trigger regeneration task
            # Track the job
            # Clean up old job records (keep only recent ones)
    def _cleanup_old_jobs(self):
    # [Logic Hidden]
        """Clean up old job records to prevent memory leaks"""
            # Remove jobs older than 1 hour
    def get_job_status(self, user_id: str) -> Dict:
    # [Logic Hidden]
        """Get the status of a regeneration job for a user"""
# Database Schema Changes
"""
def setup_database():
    # [Logic Hidden]
    """Setup database tables for profile change tracking"""
    # Execute schema changes
def example_usage():
    # [Logic Hidden]
    """
    """
    # Initialize the manager
    # Example user profile
    # Initial profile
    # Process initial profile (should not trigger regeneration)
    # Update profile with significant changes
    # Process updated profile (should trigger regeneration)
        # Show detected changes
    # Try to update again with same profile (should not trigger regeneration)
    # Check job status
    # Setup database
    # Run example
```

## backend-python\app\progression_engine.py
```python
"""
"""
# ── CONSTANTS ──
class ProgressionMethod(str, Enum):
    # [Logic Hidden]
# ── CORE CALCULATIONS ──
def calculate_adherence_score(
    # [Logic Hidden]
    """
    """
def calculate_recovery_factor(
    # [Logic Hidden]
    """
    """
def calculate_progression_delta(
    # [Logic Hidden]
    """
    """
# ── SAFETY OVERRIDES ──
def apply_age_safety_caps(
    # [Logic Hidden]
    """
    """
        # rest is advisory — returned via get_age_modifiers, not changed here
def get_age_modifiers(age: int, base_exercises: int = 6, base_rest: int = 60) -> Dict:
    # [Logic Hidden]
    """
    """
def build_form_feedback(form_score: float, exercise_name: str = '') -> Dict:
    # [Logic Hidden]
    """
    """
def get_streak_adjustments(
    # [Logic Hidden]
# ── PROGRESSION METHOD SELECTOR ──
def select_progression_method(
    # [Logic Hidden]
# ── EXERCISE VARIATION LADDER ──
def get_exercise_variation_suggestion(
    # [Logic Hidden]
    """
    """
        # Try loading the default dataset
    # Find exercise in dataset (case-insensitive partial match)
        # Try partial match
        # Excellent form → progress to harder variation
        # Poor form → regress to easier variation
# ── STAGE/READINESS HELPERS ──
def is_bodyweight_exercise(name: str, exercises_df=None) -> bool:
    # [Logic Hidden]
    # 1. Check EXERCISE_METADATA registry first
        # Check case-insensitive
def calculate_readiness_data(sleep_score: float, fatigue_score: float, stress_level: float) -> dict:
    # [Logic Hidden]
def calculate_consistent_weeks(workout_history: List[Dict]) -> int:
    # [Logic Hidden]
# ── MAIN ENGINE ──
class ProgressionEngine:
    # [Logic Hidden]
    """Stateless, deterministic progression engine."""
    def evaluate_deload(self, workout_history: List[Dict], readiness_score: int, fatigue_level: float, avg_form_score: float) -> bool:
    # [Logic Hidden]
        # High fatigue emergency override
    def detect_plateaus(self, workout_history: List[Dict], exercises_df=None) -> Dict:
    # [Logic Hidden]
    def get_progression_state(self, user_profile: Dict, workout_history: List[Dict], exercises_df=None) -> Dict:
    # [Logic Hidden]
        # Authoritative phase mapping: deload takes precedence
    def generate_structured_coaching_feedback(self, state: Dict, user_profile: Dict) -> Dict:
    # [Logic Hidden]
    def parse_history(self, workout_history: List[Dict]) -> Dict:
    # [Logic Hidden]
        """
        """
            # Parse date, fallback to old if not present
                    # simplistic parse
    def compute_progression(
    # [Logic Hidden]
        # Calculate progression state
        # Form score gates progression: if form is below 50%,
        # force MAINTAIN regardless of other factors
        # Check for plateau on the movement pattern of this exercise
            # Apply biometrics-based volume gating: skip volume/rep increases if attendance is low
        # Autoregulation: Optimal readiness (+5%), Fatigued (-10%)
        # Apply weekly sleep/hydration-based modifiers
# ── SINGLETON ──
def get_progression_engine() -> ProgressionEngine:
    # [Logic Hidden]
```

## backend-python\app\run_profile.py
```python
def main():
    # [Logic Hidden]
```

## backend-python\app\test_regression_meal_engine.py
```python
def run_regression_tests():
    # [Logic Hidden]
    # Setup
    # Scenarios
            # We must override the total_cal explicitly for the test,
            # since generate_weekly_plan derives it from profile math
            # We'll just generate the plan and check outputs
            # Print Monday to verify realistic output
            # Validation assertions on the entire weekly plan
                    # 1. Structural completeness for Lunch/Dinner
                    # 2. Rejection Rules
                        # Condiment cap
                        # Rasam powder/spice test
                        # Absurd scaling test (e.g. 5 dosas)
```

## backend-python\app\train_meal_model.py
```python
def train_meal_model():
    # [Logic Hidden]
    """Train XGBoost model for meal recommendations"""
    # Create models directory if not exists
    # Load nutrition data
    # Create synthetic training data for meal recommendations
    # Create features
    # Simulate user profiles
    # Generate training data
        # User target macros
        # Meal macros (from actual data)
        # Intensity and goal
        # Dietary preference match
        # Calculate label (1 = good recommendation, 0 = bad)
        # Good if macros are within 80-120% of target
    # Encode categorical variables
    # Prepare features
    # Split data
    # Train XGBoost model
    # Evaluate
    # Save model
    # Save encoders
```

## backend-python\app\train_model.py
```python
# PERFORMANCE SAFETY: Memory-efficient training script for scalable model generation
# SCALABILITY: Designed to handle configurable dataset sizes without memory overflow
# OPTIMIZATION: Uses efficient pandas operations and XGBoost for fast training
# SECURITY NOTE: This training script generates synthetic data for model training
# The actual user data should never be stored or processed in plain text
# All real user data must be handled through secure API endpoints with proper authentication
# Ensure models directory exists
# ==========================================
# 1. GENERATE TRAINING DATA (Simulated)
# ==========================================
# We simulate users to teach the model patterns
# e.g., High BMI + Beginner = Low Intensity
# e.g., Low Age + Muscle Gain = High Intensity
# SCALABILITY CONSIDERATION: Dataset size can be adjusted based on available memory
# For production: Consider increasing data_size for better model generalization
# MEMORY EFFICIENCY: Using numpy arrays for efficient memory usage
# PRIVACY NOTICE: This script uses synthetic/fake data for training only
# No real user data is collected, stored, or processed in this script
# All data is randomly generated and does not represent real individuals
# PERFORMANCE: Efficient data generation using vectorized numpy operations
# SCALABILITY: Vectorized function for efficient label calculation
def determine_intensity_vectorized(df):
    # [Logic Hidden]
    """Vectorized function to calculate intensity levels efficiently"""
    # Calculate BMI for all rows at once
    # Initialize score array
    # Apply age factors efficiently
    # Apply BMI factors efficiently
    # Apply goal factors efficiently
    # Classify based on scores efficiently
# PERFORMANCE: Use vectorized function instead of apply for efficiency
# ==========================================
# 2. PREPROCESS DATA
# ==========================================
# Convert text to numbers (XGBoost only understands numbers)
# PERFORMANCE: Efficient preprocessing using vectorized operations
# SCALABILITY: Encoding happens in-memory without intermediate file storage
# MEMORY EFFICIENCY: Using pandas indexing for efficient column access
# SECURITY NOTE: Data encoding happens locally in memory and is not persisted
# The encoders will be saved securely for use in the prediction pipeline
# PERFORMANCE: Efficient label encoding using pandas vectorized operations
# ==========================================
# 3. TRAIN XGBOOST MODEL
# ==========================================
# PERFORMANCE: XGBoost is optimized for speed and memory efficiency
# SCALABILITY: XGBoost handles large datasets efficiently with built-in parallelization
# MEMORY EFFICIENCY: XGBoost uses optimized data structures to minimize memory usage
# SECURITY NOTE: Model training happens in isolated environment
# No sensitive data is transmitted over networks during training
# Model parameters are configured to prevent overfitting to specific user data
# SCALABILITY: XGBoost parameters optimized for performance and generalization
# n_estimators: Number of boosting rounds (balance between performance and speed)
# max_depth: Limits tree depth to prevent overfitting and control memory usage
# learning_rate: Controls step size to ensure stable convergence
# PERFORMANCE: Efficient train-test split with reproducible results
# PERFORMANCE: Calculate accuracy on test set to validate model quality
# ==========================================
# 4. SAVE ARTIFACTS
# ==========================================
# We need to save the model AND the encoders to use them in the real app
# PERFORMANCE: Efficient serialization using joblib for fast loading in production
# SCALABILITY: Model files are compact and can be loaded quickly for predictions
# MEMORY EFFICIENCY: joblib provides efficient compression for model serialization
# SECURITY NOTICE: Model files are saved to local filesystem with restricted access
# These files should be protected with appropriate file system permissions
# The model does not contain personally identifiable information (PII)
# since it was trained on synthetic data
# PERFORMANCE: Use joblib for efficient model serialization
# joblib is optimized for scikit-learn and XGBoost models, providing faster load/save
```

## backend-python\app\update_metadata.py
```python
def main():
    # [Logic Hidden]
    # Merge to get food_name and category
    # Add new columns
    # Define regex patterns
    # 1. Update Condiments
    # Exceptions (e.g., Masala Dosa)
    # 2. Update Beverages
    # 3. Update Desserts
    # 4. Mark Primary Meals
    # Save to CSV
```

## backend-python\app\workout_engine.py
```python
# -*- coding: utf-8 -*-
# Import progression engine
# Issue #3 – YouTube video fallback
# Issue #4 – plan caching
def _utcnow() -> datetime:
    # [Logic Hidden]
class WorkoutEngine:
    # [Logic Hidden]
    def __init__(self):
    # [Logic Hidden]
        # Initialize feature pipeline
        # Media URL reliability cache (avoid repeated dead-link checks)
        # BUG-P8 fix: Event that is set once _lazy_load_wger finishes.
        # Callers that need WGER GIFs can do: engine._wger_ready_event.wait(timeout=5)
        # Exercises confirmed to have no matching GIF — must not use random fallbacks.
        # Initialize multi-output XGBoost model
        # Initialize progression engine
        # Get base directory
        # HOME_WORKOUT_ONLY mode: load home dataset first (fail-fast if missing)
        # Load exercises from CSV or create fallback
                # Standardize column names to TitleCase format to match expected format
                # If _home_only_mode is True but exercises_home_v1.csv is missing, OR if _home_only_mode is False,
                # load the standard processed/raw files and filter them in memory if _home_only_mode is True.
                    # Fallback exercises
                # Standardize column names
                # Apply home equipment filter in memory if in home-only mode and loaded full CSV
            # Fill missing values
        # Load ML models
        # Initialize hybrid optimizer (rule-based + ML hooks + user adaptation)
        # Issue #4 – Load WGER in a background thread so __init__ returns quickly
        # Issue #3 – YouTube service (lazy singleton, opt-in only)
        # Keep disabled by default because GIF/image fallbacks now cover all exercises.
        # Issue #4 – plan cache (lazy singleton)
        # High-confidence exact/fuzzy mappings harvested from local audit output.
        # Load GIF blacklist — exercises with no valid exercise-specific media.
    def _lazy_load_wger(self):
    # [Logic Hidden]
        """Background thread: build WGER media index without blocking startup."""
    def _normalize_exercise_name(self, name: str) -> str:
    # [Logic Hidden]
    def _create_user_entropy(self, profile: dict) -> str:
    # [Logic Hidden]
    def _create_profile_fingerprint(self, profile: dict) -> str:
    # [Logic Hidden]
    def _build_day_seed(self, profile: dict, focus: str, day_idx: int) -> int:
    # [Logic Hidden]
    def _build_intensity_metrics(self, intensity_data) -> Dict:
    # [Logic Hidden]
        """Build intensity metrics dict for workout day.
        """
        # Handle legacy float input
        # Handle new Dict input
    def _extract_movement_tokens(self, value: str) -> set:
    # [Logic Hidden]
        """Return canonical movement tokens for strict name matching."""
    def _name_similarity_score(self, source_name: str, candidate_name: str) -> float:
    # [Logic Hidden]
    def _is_confident_name_match(self, source_name: str, candidate_name: str, strict: bool = True) -> bool:
    # [Logic Hidden]
    def _extract_wger_video_id(self, video_url: str) -> Optional[int]:
    # [Logic Hidden]
    def _get_wger_exercise_name_by_id(self, exercise_id: int) -> str:
    # [Logic Hidden]
    def _is_wger_video_url_compatible(self, video_url: str, exercise_name: str) -> bool:
    # [Logic Hidden]
        """Accept WGER video fallback only when its canonical exercise name matches."""
        # Avoid making blocking HTTP requests during plan generation.
        # Check cache only; if not in cache, assume compatible (lenient fallback).
    def _load_gif_blacklist(self, base_dir: Optional[str] = None) -> None:
    # [Logic Hidden]
        """Load gif_blacklist.json built by build_exercise_gif_map.py."""
    def _is_gif_blacklisted(self, exercise_name: str) -> bool:
    # [Logic Hidden]
        """Return True if the exercise is confirmed to have no matching GIF."""
    def _initialize_audit_media_index(self, base_dir: Optional[str] = None) -> None:
    # [Logic Hidden]
        """Load high-confidence exercise-name -> media mappings from audit artifacts."""
                # First matching artifact is sufficient.
    def _get_audit_media_for_name(self, exercise_name: str) -> str:
    # [Logic Hidden]
        """Resolve media from locally-audited mappings with strict confidence checks."""
    def _extract_wger_name(self, exercise: Dict) -> str:
    # [Logic Hidden]
    def _normalize_wger_media_url(self, value: str) -> str:
    # [Logic Hidden]
        """Normalize WGER media paths to absolute URLs."""
    def _extract_wger_media_url(self, exercise: Dict) -> str:
    # [Logic Hidden]
            # Prefer animated GIFs first when available.
            # Then prefer main image, else first available image.
        # Fall back to videos only when image/GIF is unavailable.
    def _initialize_wger_media_index(self):
    # [Logic Hidden]
        """Build a local name -> media URL map from WGER API for robust fallback media."""
    def _get_wger_media_for_name(self, exercise_name: str) -> str:
    # [Logic Hidden]
        # If background loading failed or has not completed, try a one-time
        # synchronous initialization so we can still provide specific media.
    def _get_related_wger_media_for_name(self, exercise_name: str) -> str:
    # [Logic Hidden]
        """Relaxed name-based lookup used only before generic fallback.
        """
    def _get_exercise_specific_wger_fallback_pool(self, exercise_name: str, target_muscle: str = '') -> List[str]:
    # [Logic Hidden]
        """Return only name-relevant WGER media candidates (no generic random pool)."""
    def _get_row_value(self, row, candidates: List[str], default=''):
    # [Logic Hidden]
        """Return first matching value from row by trying multiple key styles."""
    def _parse_duration_seconds(self, reps_value) -> int:
    # [Logic Hidden]
        """Parse time-based reps strings like '5 min' or '30-45 seconds'."""
    def _is_trackable_exercise(self, name: str, reps_value, explicit: Optional[bool] = None) -> bool:
    # [Logic Hidden]
        """
        """
    def _classify_exercise_mode(self, name: str, equipment: str, reps_value,
    # [Logic Hidden]
        """Classify whether an exercise needs camera tracking or timer-only mode."""
        # Look up movement pattern from global mapping service
    def _build_search_embed_url(self, exercise_name: str, unique_suffix: str = '') -> str:
    # [Logic Hidden]
    def _get_exercise_primary_media_url(self, exercise: Dict) -> str:
    # [Logic Hidden]
    def _set_exercise_media_url(self, exercise: Dict, media_url: str) -> None:
    # [Logic Hidden]
    def _enforce_unique_media_per_day(self, exercises: List[Dict]) -> List[Dict]:
    # [Logic Hidden]
        """Keep media stable per exercise; avoid random duplicate rewrites."""
                # Preserve originally resolved media rather than forcing substitutions.
    # Known exercise-media CDN domains we trust without live HTTP checks.
    # The frontend's onError handler will fall back gracefully if a URL fails.
    # No-YouTube visual fallback URLs (stable direct GIFs) used when source media is unavailable.
    # Exact-name fallbacks for known rows that still have no direct media URL.
    # Keys must match _normalize_exercise_name(name).
        # Curated overrides for custom/non-dataset exercise names used by the planner.
    def _pick_deterministic_fallback(self, options: List[str], exercise_name: str) -> str:
    # [Logic Hidden]
    def _get_gif_fallback_for_target(self, target_muscle: str, exercise_name: str = '', allow_generic: bool = False) -> str:
    # [Logic Hidden]
        # Prefer exercise-name-aware WGER fallback pools for better per-exercise
        # specificity and reduced repeated generic media.
        # Avoid random muscle-group substitutions unless explicitly requested.
        # Unknown muscle group: choose from global fallback pool using exercise-name hash.
    def _get_gif_fallback_for_exercise_name(self, exercise_name: str) -> str:
    # [Logic Hidden]
    def _check_url_reachable(self, url: str, accept_any_response: bool = False) -> bool:
    # [Logic Hidden]
        """Best-effort live URL check with short timeout + in-memory cache.
        """
                # Accept 4xx errors too (e.g., 403 forbidden but server is up)
                # Some hosts block HEAD but allow GET.
    def _validate_media_url(self, url: str) -> bool:
    # [Logic Hidden]
        """
        """
        # YouTube embed URLs are always accepted
        # Fast check: trusted CDN domains - accept without live check
        # Frontend has onError handlers to fall back gracefully
            # Accept trusted domains directly (wger, imgur, etc.)
            # ExerciseDB: trust them directly to avoid slow live HTTP checks!
            # The frontend has fallback handling for dead links.
        # Accept any URL that looks like a media file by extension
            # Be more lenient - accept if the URL structure looks valid
        # For wger-style URLs that have /image/ in the path
    def _resolve_exercise_media(self, row) -> Dict[str, str]:
    # [Logic Hidden]
        """
        """
        # Short-circuit: blacklisted exercises have no valid exercise-specific GIF.
        # Return 'none' so the frontend shows its text/illustration placeholder.
            # 0. Pre-fetched Wger image from exercises_processed.csv — most reliable,
            #    since exercisedb.io has been returning HTTP 500 errors.
            # 0b. Local audited name->media mapping (non-generic URLs only).
            # 1. Exact WGER live-API match from cached index.
            # 2. Dataset image-like URLs (prefer over video).
            # 3. Conservative fuzzy WGER match for better per-exercise specificity.
            # 3b. Relaxed related WGER match before generic fallback.
            # 4. Keep dataset video URL as a last optional candidate.
        # Force exact-name GIF overrides first for known rows missing image/GIF media.
        # Prefer strict name-based GIF fallback over video/youtube when direct sources fail.
        # Use any existing video URL only when no image/GIF fallback was possible.
        # Use any existing YouTube URL only when no image/GIF/video fallback was possible.
        # Issue #3 – YouTube fallback: prefer YouTube over an unvalidated URL candidate.
        # NOTE: Generic muscle-group fallback is intentionally disabled.
        # We do NOT fall back to a random GIF for a different exercise — use 'none' instead.
        # (The allow_generic=True path previously here caused wrong GIFs to be shown.)
        # Optional final YouTube search embed only when YouTube fallback is enabled.
    def _load_ml_models(self):
    # [Logic Hidden]
        """Load pre-trained ML models in parallel using ThreadPoolExecutor.
        """
            # ----------------------------------------------------------------
            # Step 1: Load the multi-output model first (it uses a custom
            # .load_model() method that manages its own internal state and
            # must not run concurrently with itself).
            # ----------------------------------------------------------------
            # ----------------------------------------------------------------
            # Step 2: Load all remaining models IN PARALLEL.
            # Each entry is (attr_name, file_path, label_for_log).
            # ----------------------------------------------------------------
            def _load_one(spec):
    # [Logic Hidden]
                """Load a single model file and return (attr_name, model_or_None, label, found)."""
            # Use up to 8 workers — all models are small enough that I/O is the
            # bottleneck, not CPU. More workers → faster parallelism.
            # Assign results to instance attributes in the original order
    def filter_by_equipment(self, exercises: pd.DataFrame, available_equipment: List[str]) -> pd.DataFrame:
    # [Logic Hidden]
        """Filter exercises by available equipment - HOME-V1 POLICY ENFORCEMENT.
        """
            # ── Load home-v1 synonym + policy files ───────────────────────
            # ── Build allowed CSV value set from profile equipment labels ──
                # Handle "Jump Rope" label directly
            # ── Row-level filter with Rope split logic ─────────────────────
            def _is_allowed(eq_lc: str, nm_lc: str) -> bool:
    # [Logic Hidden]
    def filter_by_injuries(self, exercises: pd.DataFrame, body_issues: List[str]) -> pd.DataFrame:
    # [Logic Hidden]
        """Filter exercises to avoid injuries - RULE-BASED SAFETY LOGIC"""
                    # Rule-based safety logic: filter out exercises with shoulder forbidden terms
    def _build_feature_vector(self, profile: dict) -> np.ndarray:
    # [Logic Hidden]
        """Build a comprehensive feature vector using the feature pipeline"""
        # Use the feature pipeline to process the user profile
        # Process through the feature pipeline
    def _get_multi_output_predictions(self, profile: dict) -> list:
    # [Logic Hidden]
    def _get_intensity_adjustment(self, profile: dict) -> float:
    # [Logic Hidden]
        """Get intensity adjustment based on ML model or rules - HYBRID APPROACH"""
        # Try to use multi-output model if available
                # Extract intensity from the predictions (assuming it's the 5th element: [sets, reps_low, reps_high, rest_time, intensity])
        # Fall back to original logic
    def _get_optimized_workout_split(self, profile: dict, days_per_week: int) -> List[str]:
    # [Logic Hidden]
        """Get workout split optimized by ML model with rule-based validation - HYBRID APPROACH"""
    def _get_optimized_training_volume(self, profile: dict) -> tuple:
    # [Logic Hidden]
        """Get optimized training volume (sets, reps, rest) using ML with rule-based validation - HYBRID APPROACH"""
    def _get_optimized_sets(self, profile: dict) -> int:
    # [Logic Hidden]
        """Get optimized number of sets using ML with rule-based validation - HYBRID APPROACH"""
    def _get_optimized_reps(self, profile: dict, intensity: float) -> str:
    # [Logic Hidden]
        """Get optimized rep range using ML with rule-based validation - HYBRID APPROACH"""
    def _get_optimized_rest_time(self, profile: dict) -> int:
    # [Logic Hidden]
        """Get optimized rest time using ML with rule-based validation - HYBRID APPROACH"""
    def _get_optimized_frequency(self, profile: dict) -> int:
    # [Logic Hidden]
        """Get optimized training frequency using ML with rule-based validation - HYBRID APPROACH"""
    def _get_optimized_progression(self, profile: dict) -> Dict:
    # [Logic Hidden]
        """Get optimized progression timing using ML with rule-based validation - HYBRID APPROACH"""
    def _generate_dynamic_split(self, days_per_week: int, goal: str) -> List[str]:
    # [Logic Hidden]
        """Generate workout split based on days and goal - RULE-BASED LOGIC"""
    def _calculate_rest_days(self, days_per_week: int, profile: dict = None, intensity: float = None) -> List[int]:
    # [Logic Hidden]
        """Calculate optimal rest days in the week using intensity-aware logic"""
    def _create_optimal_schedule(self, weekly_plan: List[Dict], rest_days: List[int]) -> List[Dict]:
    # [Logic Hidden]
        """Create week schedule with rest days - HYBRID APPROACH"""
    def _calculate_exercise_count(self, experience: str, goal: str) -> int:
    # [Logic Hidden]
        """Calculate number of exercises per workout - RULE-BASED LOGIC"""
    def _calculate_sets(self, experience: str, goal: str) -> int:
    # [Logic Hidden]
        """Calculate number of sets - RULE-BASED LOGIC"""
    def _calculate_reps(self, goal: str, intensity: float) -> str:
    # [Logic Hidden]
        """Calculate rep range based on goal - RULE-BASED LOGIC"""
    def _calculate_rest_time(self, goal: str, experience: str) -> int:
    # [Logic Hidden]
        """Calculate rest time between sets - RULE-BASED LOGIC"""
    def _adjust_reps_for_intensity(self, base_reps: str, intensity: float) -> str:
    # [Logic Hidden]
        """Adjust reps based on intensity - RULE-BASED LOGIC"""
    def _estimate_reps_avg(self, reps_range: str) -> float:
    # [Logic Hidden]
        """Estimate avg reps from a range string like '8-12'"""
    def _apply_age_based_caps(self, profile: dict, sets: int, reps: str, rest_time: int, intensity: float) -> tuple:
    # [Logic Hidden]
        """Apply age-based safety caps to workout parameters - RULE-BASED SAFETY LOGIC"""
        # Log initial values before applying rules
        # Apply age-appropriate limits
            # For older adults, reduce intensity and volume
            # Adjust reps to safer range for older adults
                # Handle cases where reps is not in x-y format
            # Log changes applied by rules
            # For younger individuals, focus on form over heavy loads
            # Higher rep ranges for skill development
                # Handle cases where reps is not in x-y format
            # Log changes applied by rules
    def _filter_biomechanics(self, exercises: pd.DataFrame, profile: dict) -> pd.DataFrame:
    # [Logic Hidden]
        """Filter exercises based on biomechanical safety - RULE-BASED SAFETY LOGIC"""
            # For beginners, filter out complex movements
                # Avoid overly complex exercises for beginners
            # Use Check_Type column if available (e.g., filter out cardio for strength-focused plans)
                # For strength-focused goals, prioritize strength exercises
                    # For endurance-focused goals, include more cardio exercises
            # Use Risk_Level column if available (assuming lower risk is better for beginners)
                    # Filter out high-risk exercises for beginners
                    # For seniors, only allow low-risk exercises
                # If Risk_Level column doesn't exist, create a basic risk assessment based on other factors
            # Additional biomechanical filters based on age
                # Avoid high-impact exercises for seniors
            # Log the results of biomechanical filtering
    def _infer_rest_days_count(self, profile: dict, intensity: float, sets: int, reps: str, num_exercises: int) -> int:
    # [Logic Hidden]
        """Decide rest days based on weekly load + profile (MODEL-DRIVEN LOGIC)"""
    # ──────────────────────────────────────────────────────────────────────────
    # Issue #1 – Rolling week: build an adaptive partial week for new users
    # ──────────────────────────────────────────────────────────────────────────
    def _is_registration_in_current_week(self, registration_value) -> bool:
    # [Logic Hidden]
        """Return True when registration date belongs to the current ISO week."""
    def _calculate_partial_week_ratio(self, total_available: int,
    # [Logic Hidden]
        """Return a safe workout/rest split for shortened new-user weeks."""
    def _select_partial_week_splits(self, workout_day_count: int,
    # [Logic Hidden]
        """Choose a practical split for short onboarding weeks."""
    def _ensure_non_consecutive_rests(self, rest_positions: Set[int],
    # [Logic Hidden]
        """Shift rest days when possible so two rests are never adjacent."""
            # Try moving current rest one day forward.
            # Try moving previous rest one day backward.
            # Keep only one of the consecutive rests as a safe fallback.
    def _build_partial_week_rest_positions(self, available_indices: List[int],
    # [Logic Hidden]
        """Place rest days across available days while preserving day-one onboarding."""
        # Keep registration day as workout to avoid a dead first impression.
    def _build_new_user_plan(self, profile: dict, split: List[str],
    # [Logic Hidden]
        """Build an adaptive onboarding week that starts from registration day."""
    def generate_weekly_plan(self, profile: dict, workout_history: List[Dict] = None,
    # [Logic Hidden]
        """
        """
        # Issue #4 – try cache first
        # Work on a local copy so transient generation fields never mutate caller state.
        # If caller does not provide week_offset, derive one from ISO year/week.
        # This keeps generation deterministic within a week while rotating weekly.
        # --- Detect new user start day from profile if not supplied ---
        # --- Base Variables ---
        # Experience-based weekly frequency with conservative progression gates.
        # Respect explicit user preference when it is lower than recommendation.
        # --- Inject Gemini AI Intelligence Config ---
        # FIX: Disabled synchronous LLM call during workout generation to prevent 3-8s latency
        # --- Step 2: Get workout split ---
        # --- Step 3: Distribute rest days ---
            # Issue #2 – use smart intensity-based rest placement
        # --- Step 4: Build the 7-day schedule ---
        # --- Inject debug_trace into each day of the plan for transparency and testing ---
        # Issue #4 – cache the result
    def _get_split_for_experience(self, experience: str, workout_days: int, goal: str, workout_history: List[Dict] = None) -> List[str]:
    # [Logic Hidden]
        """
        """
        # Stateful rotation: Determine the last workout focus from history
        def _rotate(base: List[str]) -> List[str]:
    # [Logic Hidden]
    def _distribute_rest_days(self, workout_days: int, split: List[str]) -> List[int]:
    # [Logic Hidden]
        """
        """
            # Many rest days - alternate workout/rest, fill remaining at end
    # ──────────────────────────────────────────────────────────────────────────
    # Issue #2 – Smart rest day placement based on workout intensity
    # ──────────────────────────────────────────────────────────────────────────
    def _calculate_workout_intensity_score(self, focus: str, experience: str,
    # [Logic Hidden]
        """
        """
        # Compound / heavy days are more stressful
        # Goal modifier
    def _get_muscle_group_from_focus(self, focus: str) -> Set[str]:
    # [Logic Hidden]
        """Return a simplified set of primary muscles for overlap detection."""
    def _validate_muscle_recovery(self, schedule: List[Dict]) -> Dict:
    # [Logic Hidden]
        """
        """
        # Build (day_index, focus) for workout days only, sorted by day
    def _calculate_smart_rest_days(self, split: List[str], rest_count: int,
    # [Logic Hidden]
        """
        """
        # --- Step 1: evenly-spaced base grid ---
        # place rest days at round(interval * i) for i in 1..rest_count
        # Deduplicate while preserving order
        # If dedup removed some, fill from end of week
        # --- Step 2: build day→split-slot map from base positions ---
        # --- Step 3: micro-adjust — move rest to immediately after heavy days ---
                # Check if the day AFTER the rest is heavy — if so, rest is already well placed
            # rest_pos already follows a heavy day — perfect, no adjustment needed
            # (we only adjust when rest is NOT after a heavy day, handled below)
        # Find heavy days that are NOT followed by a rest
                # Try to swap: remove the furthest rest and insert after this heavy day
                # Only if it doesn't create consecutive rests
                    # Remove the rest that's farthest from the heavy day
    def _build_weekly_plan(self, profile: dict, split: List[str], rest_positions: List[int]) -> List[Dict]:
    # [Logic Hidden]
        """Build the full 7-day plan with exercises for workout days and rest for rest days.
        """
        # First pass: map each non-rest day to its split focus so we can generate rest reasons
        def _get_rest_reason(day_idx: int) -> str:
    # [Logic Hidden]
            """Return a human-readable reason this day is a rest day."""
            # Check if preceding day was high-intensity
            # Check if following day is high-intensity — pre-load rest
            # Generic mid-week / end-week rest
        # Cross-day exercise deduplication: no exercise should appear twice in the same week
                # Track which exercises were used this week to prevent cross-day repeats
                # Calculate day intensity metrics (returns a dict with intensity_score, category, etc.)
    def swap_rest_with_next_workout(self, weekly_plan: List[Dict], rest_day_index: int,
    # [Logic Hidden]
        """Swap an original rest day with the next original workout day in the same week."""
        # Find the next workout day in the same week only (no wrap-around).
    def swap_workout_with_future_rest(self, weekly_plan: List[Dict], workout_day_index: int,
    # [Logic Hidden]
        """Swap an original workout day with a future original rest day."""
    def _get_warmup_for_focus(self, focus: str, exercises: List[Dict] = None, day_seed: int = 0) -> List[Dict]:
    # [Logic Hidden]
        """Return a muscle-targeted warm-up block (max 6 drills) dynamically and randomly."""
        # Fallback to focus_to_muscles mapping if target_muscles is empty
        # Fallback parsing for custom focus names.
        # Preserve order while removing duplicates.
        # 1. Pick drills from target muscle groups
        # 2. If we need more drills to reach a minimum of 4, fill from 'general' category
    def _get_exercises_for_day(self, focus: str, goal: str, experience: str,
    # [Logic Hidden]
        """
        """
        # --- Muscle group mapping ---
        # Bug #1a Fix: Map beginner sub-focus variants to standard muscle groups
        # so the existing muscle_map lookup still works correctly.
        # Focus-specific distribution: keep two primary muscles loaded and
        # use additional mapped muscles as accessories where applicable.
        # Compound exercise indicators (multi-joint movements)
        # --- Exercise count by experience ---
        # For Full Body days, use the higher end; for isolation days, use the lower end
        # Bug #1 Fix: Gender-based volume adjustment
        # Research: Women have lower absolute strength but similar relative strength
        # and better recovery capacity. Reduce volume by 1-2 exercises for safety.
            # Reduce exercise count by 1 for female users (lower absolute volume)
            # Minimal adjustment for "Other" gender
        # Experience-based volume targets per muscle group.
        # Build per-muscle quotas with priority for primary muscles.
        def _assign_round_robin(targets: Dict[str, int], muscles: List[str], cap: int,
    # [Logic Hidden]
        # --- Get exercise parameters based on goal + experience ---
        # --- Filter exercise pool ---
        # Bodyweight-always terms (always allowed regardless of equipment selection)
        # Equipment filter
        # IMPORTANT: empty equipment list = bodyweight ONLY (not "show everything")
        # Strip sentinel values the frontend may send
            # User has no equipment — restrict to bodyweight exercises only
            # Expand equipment synonyms: bridge ALL frontend UI labels → dataset Equipment column values.
            # Dataset values: 'Assisted','Band','Barbell','Body Weight','Bosu Ball','Cable',
            # 'Dumbbell','Elliptical Machine','Ez Barbell','Hammer','Kettlebell',
            # 'Leverage Machine','Medicine Ball','Olympic Barbell','Resistance Band','Roller',
            # 'Rope','Skierg Machine','Sled Machine','Smith Machine','Stability Ball',
            # 'Stationary Bike','Stepmill Machine','Tire','Trap Bar',
            # 'Upper Body Ergometer','Weighted','Wheel Roller'
                # Dumbbells
                # Barbells
                # Kettlebell
                # Cable
                # Machines
                # Resistance/bands
                # Cardio/specialty machines
                # Free accessories
                # Catch-all labels (legacy / user typed values)
        # Injury filter
                    # Rule-based safety logic: filter out exercises with shoulder forbidden terms
        # Biomechanical safety filter
        # --- Select exercises per target muscle, compound first ---
        # Merge local + cross-day used names to prevent any repetition
            # Get candidates for this muscle
            # Mark compound vs isolation
            # --- SEEDED SHUFFLE: true variety per day, stable per (user, day, week) ---
            # Shuffle within each priority tier so we don't always get A-Z first.
            # Uses day_seed which is a large hash unique to (user_id, focus, day_index, week).
            # Keep compounds first (better programming order), then isolation
            # Pick exercises for this muscle (avoid duplicates across days too)
        # If we don't have enough, fill from remaining pool (also shuffled)
        # Cap at target_count
        # Keep compounds first but preserve seeded shuffled order within each tier.
        # Apply age-based safety caps
                # Safely parse rest time
        # Clean internal fields
        # Fallback if still empty
    def _get_exercise_params(self, goal: str, experience: str, profile: dict) -> Dict:
    # [Logic Hidden]
        """
        """
        # Check Gemini extracted config first
        # Try progression engine first
                # Static baseline
        # Fallback: static tables
        # Bug #1f Fix: Gender-based intensity adjustment
        # Research-based adjustments for physiological differences
        # Parse rest time from string (e.g., "60 seconds" → 60)
            # Females: Higher rep ranges for hypertrophy, better recovery capacity
            # Reduce sets by 1 for beginners to prevent overtraining
            # Shorter rest periods for female users (10-15% reduction)
            # Women recover faster between sets due to hormonal differences
            # "Other" gender: minimal adjustment (5% changes)
            # Male users: standard rest times
        # Format rest time back to string
    def _calculate_day_intensity(self, exercises: List[Dict], experience: str, goal: str, profile: dict = None) -> Dict:
    # [Logic Hidden]
        """
        """
        # Exercise intensity coefficients (METs-based)
            # Compound movements - high intensity
            # Isolation movements - moderate intensity
            # Bodyweight exercises
            # Base exercise intensity
            # Match exercise name to intensity coefficient
            # Volume factor (sets × reps)
            # ── FIX: coerce sets/reps to safe types before arithmetic ──
            # The ML pipeline can return sets/reps as int, float, str, or dict.
            # Calling `'-' in int_value` raises TypeError; `dict * int` raises TypeError.
            # Safely convert sets to int
            # Safely convert reps to a numeric value
            # Calculate exercise intensity contribution
        # Normalize intensity score (0-1 scale)
        # Typical workout has 5-8 exercises
        # Apply Phase 3 readiness autoregulation and deload scaling
            # Autoregulation: Optimal readiness (+5%), Fatigued (-10%)
            # Deload: -20% intensity
        # Calorie multiplier based on intensity
        # Rest day: 0.90, Light: 0.95, Moderate: 1.00, Hard: 1.10, Very Hard: 1.18
        # Categorize intensity
    def _get_fallback_exercises(self, params: Dict) -> List[Dict]:
    # [Logic Hidden]
        """Return safe fallback exercises when database filtering yields nothing."""
# ==========================================
# FACTORY FUNCTION
# ==========================================
def get_workout_engine():
    # [Logic Hidden]
    """Get or create the singleton WorkoutEngine instance"""
```

## backend-python\app\youtube_service.py
```python
# -*- coding: utf-8 -*-
"""
"""
# ─────────────────────────────────────────────────────────────────────────────
# Optional Google API client
# ─────────────────────────────────────────────────────────────────────────────
class YouTubeExerciseService:
    # [Logic Hidden]
    """
    # Returns: "https://www.youtube.com/embed/<video_id>"  or  ""
    """
        # Reliable, commonly indexed fitness channels
    # Reliable hardcoded video IDs for common exercises (no API needed)
    def __init__(self):
    # [Logic Hidden]
            # Still functional! build_search_embed_url works without API key
    def build_search_embed_url(self, exercise_name: str) -> str:
    # [Logic Hidden]
        """Return a YouTube embed search URL that does not consume Data API quota."""
    def _get_known_video_url(self, exercise_name: str) -> str:
    # [Logic Hidden]
        """Check if we have a hardcoded video ID for this exercise."""
        # Exact match
        # Partial match (e.g., "barbell back squat" contains "squat")
    # ──────────────────────────────────────────────────────────────────────────
    def search_exercise_video(self, exercise_name: str) -> str:
    # [Logic Hidden]
        """
        """
        # First: Check hardcoded known videos (no API needed, always works)
        # No API key/client available: fall back to search embed URL.
        # Quota already exhausted in this process: skip API calls.
            # Prefer known trusted channels, otherwise take first result
        # Graceful fallback (no quota usage) when API fails or yields no match.
# ─────────────────────────────────────────────────────────────────────────────
# Singleton factory
# ─────────────────────────────────────────────────────────────────────────────
def get_youtube_service() -> YouTubeExerciseService:
    # [Logic Hidden]
```

## backend-python\app\core\__init__.py
```python
# app/core package
```

## backend-python\app\core\auth.py
```python
def extract_auth_token_from_request(
    # [Logic Hidden]
    """Resolve auth token from header first, then HttpOnly cookie."""
def require_user_id_from_token(x_auth_token: Optional[str], request_id: Optional[str] = None) -> str:
    # [Logic Hidden]
    """Decode JWT and return user id, raising HTTP 401 on missing/invalid token."""
def require_user_id_from_request(
    # [Logic Hidden]
    """Extract auth token from request, then require and return user id."""
```

## backend-python\app\core\responses.py
```python
def _utcnow() -> datetime:
    # [Logic Hidden]
    """Return naive UTC datetime without using deprecated utcnow()."""
def api_success(message: str, data: Optional[Dict[str, Any]] = None, **extra: Any) -> Dict[str, Any]:
    # [Logic Hidden]
    """Standard success envelope while retaining backward-compatible top-level fields."""
```

## backend-python\app\detectors\base_detector.py
```python
class BaseDetector:
    # [Logic Hidden]
    """
    """
    def __init__(self, config: Dict[str, Any]):
    # [Logic Hidden]
    def calculate_angle(self, a: List[float], b: List[float], c: List[float]) -> float:
    # [Logic Hidden]
        """Calculate angle between three points (a, b, c) at joint b."""
    def get_keypoints(self, landmarks) -> Dict[str, List[float]]:
    # [Logic Hidden]
        """Extract main joint keypoints from landmarks."""
        # MediaPipe Pose landmark indices:
        # L_Shoulder=11, R_Shoulder=12, L_Elbow=13, R_Elbow=14, L_Wrist=15, R_Wrist=16
        # L_Hip=23, R_Hip=24, L_Knee=25, R_Knee=26, L_Ankle=27, R_Ankle=28
    def get_confidence(self, landmarks) -> float:
    # [Logic Hidden]
        """Calculate mean confidence (visibility) of active tracking landmarks."""
        # Determine relevant joints based on configured tracking joint
    def count_reps(self, landmarks, state_data: Dict[str, Any]) -> Tuple[int, str]:
    # [Logic Hidden]
        """Perform state-machine based rep counting with hysteresis and ROM check."""
    def check_form(self, landmarks) -> List[str]:
    # [Logic Hidden]
        """Perform form validation and update self.feedback."""
    def get_feedback(self) -> List[str]:
    # [Logic Hidden]
        """Get the latest structured feedback messages."""
    def calculate_form_score(self, landmarks) -> int:
    # [Logic Hidden]
        """Calculate a dynamic form score from 0 to 100."""
```

## backend-python\app\detectors\curl_detector.py
```python
class CurlDetector(BaseDetector):
    # [Logic Hidden]
    """
    """
    def count_reps(self, landmarks, state_data: Dict[str, Any]) -> Tuple[int, str]:
    # [Logic Hidden]
        # State machine: down (extended) -> up (contracted) -> down (extended)
    def check_form(self, landmarks) -> List[str]:
    # [Logic Hidden]
            # Check shoulder stability (avoid swinging)
    def calculate_form_score(self, landmarks) -> int:
    # [Logic Hidden]
```

## backend-python\app\detectors\detector_factory.py
```python
# Class registry mapping movement patterns to detector classes
class DetectorFactory:
    # [Logic Hidden]
    # Keyword → movement_pattern fallback when exercise isn't in the mapping
    def reset(cls):
    # [Logic Hidden]
        """Reset factory state. Useful for testing."""
    def load_configs(cls):
    # [Logic Hidden]
        # Load exercise mapping
            # Build lowercase key map for case-insensitive lookup
        # Load movement rules
    def _infer_pattern(cls, exercise_name: str) -> str:
    # [Logic Hidden]
        """Infer the movement pattern from exercise name keywords."""
    def get_detector(cls, exercise_name: str) -> BaseDetector:
    # [Logic Hidden]
        """
        """
        # 1. Try exact key match
        # 2. Try case-insensitive match
        # 3. Get the movement pattern
            # Keyword-based inference for exercises not in the mapping
        # Look up detector class from the registry
        # Get thresholds for the pattern
        # Return instantiated detector
    def get_exercise_config(cls, exercise_name: str) -> Dict[str, Any]:
    # [Logic Hidden]
        """Get the config for an exercise, with case-insensitive and fallback support."""
    def get_mapping(cls) -> Dict[str, Any]:
    # [Logic Hidden]
```

## backend-python\app\detectors\generic_detector.py
```python
class GenericDetector(BaseDetector):
    # [Logic Hidden]
    """
    """
    def count_reps(self, landmarks, state_data: Dict[str, Any]) -> Tuple[int, str]:
    # [Logic Hidden]
        # Calculate a general metric based on average change in major joint angles
    def check_form(self, landmarks) -> List[str]:
    # [Logic Hidden]
    def calculate_form_score(self, landmarks) -> int:
    # [Logic Hidden]
```

## backend-python\app\detectors\hinge_detector.py
```python
class HingeDetector(BaseDetector):
    # [Logic Hidden]
    """
    """
    def count_reps(self, landmarks, state_data: Dict[str, Any]) -> Tuple[int, str]:
    # [Logic Hidden]
    def check_form(self, landmarks) -> List[str]:
    # [Logic Hidden]
            # Check if back is rounding by looking at hip and knee angles
            # In a deadlift, knees should remain soft (not bent as deep as a squat)
    def calculate_form_score(self, landmarks) -> int:
    # [Logic Hidden]
```

## backend-python\app\detectors\lunge_detector.py
```python
class LungeDetector(BaseDetector):
    # [Logic Hidden]
    """
    """
    def count_reps(self, landmarks, state_data: Dict[str, Any]) -> Tuple[int, str]:
    # [Logic Hidden]
    def check_form(self, landmarks) -> List[str]:
    # [Logic Hidden]
            # Check knee alignment relative to ankle (e.g. knee collapsing inward or outward too far)
    def calculate_form_score(self, landmarks) -> int:
    # [Logic Hidden]
```

## backend-python\app\detectors\plank_detector.py
```python
class PlankDetector(BaseDetector):
    # [Logic Hidden]
    """
    """
    def count_reps(self, landmarks, state_data: Dict[str, Any]) -> Tuple[int, str]:
    # [Logic Hidden]
        # Planks are isometric, we count the hold time (represented as reps / hold duration)
                # Increment counter every 5 seconds of plank hold
    def check_form(self, landmarks) -> List[str]:
    # [Logic Hidden]
    def calculate_form_score(self, landmarks) -> int:
    # [Logic Hidden]
```

## backend-python\app\detectors\pull_detector.py
```python
class PullDetector(BaseDetector):
    # [Logic Hidden]
    """
    """
    def count_reps(self, landmarks, state_data: Dict[str, Any]) -> Tuple[int, str]:
    # [Logic Hidden]
        # Pull exercises have contraction at the bottom or top depending on geometry
        # Let's support standard state machine where 'down' means contracted (elbow angle is small)
    def check_form(self, landmarks) -> List[str]:
    # [Logic Hidden]
        # Check posture/leaning angle
            # We want to check torso stability
    def calculate_form_score(self, landmarks) -> int:
    # [Logic Hidden]
```

## backend-python\app\detectors\push_detector.py
```python
class PushDetector(BaseDetector):
    # [Logic Hidden]
    """
    """
    def count_reps(self, landmarks, state_data: Dict[str, Any]) -> Tuple[int, str]:
    # [Logic Hidden]
    def check_form(self, landmarks) -> List[str]:
    # [Logic Hidden]
        # Check body alignment (e.g. saggy hips in pushups)
        # Check if elbows are flaring too wide
    def calculate_form_score(self, landmarks) -> int:
    # [Logic Hidden]
```

## backend-python\app\detectors\raise_detector.py
```python
class RaiseDetector(BaseDetector):
    # [Logic Hidden]
    """
    """
    def count_reps(self, landmarks, state_data: Dict[str, Any]) -> Tuple[int, str]:
    # [Logic Hidden]
    def check_form(self, landmarks) -> List[str]:
    # [Logic Hidden]
            # Check if raising arms too high above head (usually lateral raises stop near 90 deg)
    def calculate_form_score(self, landmarks) -> int:
    # [Logic Hidden]
```

## backend-python\app\detectors\squat_detector.py
```python
class SquatDetector(BaseDetector):
    # [Logic Hidden]
    """
    """
    def count_reps(self, landmarks, state_data: Dict[str, Any]) -> Tuple[int, str]:
    # [Logic Hidden]
        # Knee angle (left side primarily, or average if confident)
        # State machine: UP -> DOWN -> UP
    def check_form(self, landmarks) -> List[str]:
    # [Logic Hidden]
            # Check knee alignment (knees collapsing inward)
            # Check if torso is leaning too far forward
    def calculate_form_score(self, landmarks) -> int:
    # [Logic Hidden]
```

## backend-python\app\models\__init__.py
```python
"""Application data models package."""
```

## backend-python\app\models\user.py
```python
class GenderEnum(str, Enum):
    # [Logic Hidden]
class GoalEnum(str, Enum):
    # [Logic Hidden]
class ActivityLevelEnum(str, Enum):
    # [Logic Hidden]
class ExperienceLevelEnum(str, Enum):
    # [Logic Hidden]
class DietaryPreferenceEnum(str, Enum):
    # [Logic Hidden]
class UserBase(BaseModel):
    # [Logic Hidden]
class UserCreate(UserBase):
    # [Logic Hidden]
class UserUpdate(BaseModel):
    # [Logic Hidden]
class UserInDB(UserBase):
    # [Logic Hidden]
class WorkoutHistory(BaseModel):
    # [Logic Hidden]
class MealHistory(BaseModel):
    # [Logic Hidden]
class WorkoutCompletion(BaseModel):
    # [Logic Hidden]
class MealCompletion(BaseModel):
    # [Logic Hidden]
class MealItemTick(BaseModel):
    # [Logic Hidden]
class MealHistoryEntry(BaseModel):
    # [Logic Hidden]
```

## backend-python\app\nutrition_engine\candidate_generator.py
```python
def _unfreeze(obj):
    # [Logic Hidden]
# ── Phase 0 Diagnostics ───────────────────────────────────────────────────
# JSONL file that accumulates one structured record per generate_candidates() call.
# Writing is best-effort: if the file cannot be written (permissions, disk full, etc.)
# the exception is caught and logged so meal generation is never blocked.
def _write_candidate_metrics(record: dict) -> None:
    # [Logic Hidden]
    """Append one JSON object to the candidate-generation metrics JSONL file.
    """
# ── Meal-type suitability score thresholds ────────────────────────────────
# Foods scoring below these thresholds for a given meal type are rejected.
# Meal-type role guard: dish_family values not permitted for a meal type.
# These replace the old hardcoded keyword lists and are metadata-driven.
# Side dish alternatives — used when a blueprint calls for a dominant/banned item
class DailyMealContext:
    # [Logic Hidden]
    """
    """
    def record_meal(self, plate: List[Dict]) -> None:
    # [Logic Hidden]
        """Call after a meal is finalized to update the daily context."""
    def diversity_weight(self, node: Dict) -> float:
    # [Logic Hidden]
        """
        """
        # Exponential decay: first repeat -> 0.5, second -> 0.25, etc.
def is_allowed_other_region_food_in_maharashtra(food_name: str) -> bool:
    # [Logic Hidden]
class CandidateGenerator:
    # [Logic Hidden]
    """
    """
    def __init__(self, food_graph):
    # [Logic Hidden]
        # Build food name -> node mapping
    def _map_food_to_blueprint_role(self, food: Dict, template_role: str = "") -> str:
    # [Logic Hidden]
        # Priority 0: Hard name/dish_family overrides — must come before category checks
        # Raita/pachadi is always a side dish regardless of category or food_group
        # Carb-based bases (sandwich, wrap, roll, toast, roti, paratha, chapati, naan, dosa, idli, poha, upma, oats, rice, bread, pasta, etc.)
            # If it is a carb base but contains a major protein keyword, it behaves as the protein main
        # Soup/shorba is always a side/soup
        # Chutney/pickle
        # Salad/kachumber - sprouted salads or salads with meat/dairy function as protein sources
        # 1. food_group/category + template_role
        # 2. dish_family
        # 3. Normalized category field from dataset (case-insensitive and plural-robust)
        # 4. Configuration-driven pattern map in nutrition_rules.yaml
        # 5. Food name matching as absolute last resort (log METADATA_FALLBACK_WARNING)
    def _fuzzy_match_food(self, query: str) -> dict:
    # [Logic Hidden]
        # 1. Exact match
        # 2. Handle common aliases BEFORE substring matching
        # NOTE: aliases that map to "tossed salad" are REMOVED — they caused
        # Tossed Salad to dominate every meal slot.
            # Re-run fuzzy match with the alias
        # Exact partial match
        # 3. Simple Substring matching (e.g. "masoor dal" inside "whole masoor (masoor ki dal)")
        # 4. Fallback to difflib
    def _find_closest_valid_replacement(self, invalid_node: Dict, diet_type: str, meal_type: str) -> Optional[Dict]:
    # [Logic Hidden]
        """Find the closest nutrition-valid replacement for an invalid food node.
        """
            # Must be nutrition-valid
            # Diet compatibility
            # Meal-type suitability
            # Score
    def _is_meal_type_suitable(self, food_name: str, meal_type: str) -> bool:
    # [Logic Hidden]
        """
        """
        # Legacy keyword guard for 'other' dish_family foods — avoids regressions
    def _is_diet_compatible(self, meal_diet: str, user_diet: str) -> bool:
    # [Logic Hidden]
        # Normalize common aliases
        # NonVeg: all diet types are compatible (non-veg users can eat veg food)
    def _get_user_patterns(self, user_profile: Dict):
    # [Logic Hidden]
    def _is_safe_meal_with_reason(self, plate: List[Dict], user_profile: Dict) -> Tuple[bool, str]:
    # [Logic Hidden]
        # Verify each food item in the plate
            # Check blocklist
            # Check allergies (against name and allergens field)
            # Check never recommend
    def generate_candidates(
    # [Logic Hidden]
        """
        """
        # ── Phase 0: Full rejection statistics ───────────────────────────────
        # Each key maps to one specific rejection rule.  Counters are incremented
        # inside the filter loop and written to the JSONL metrics file at the end.
        # SOURCE 1: Meal Blueprint Library
        # SOURCE 2: Dynamic Semantic Generation — template-driven (Phase 1A)
            # Allergy / never-recommend check
            # Structural composition check — returns (bool, reason_str)
                # Map reason string to the appropriate rejection counter
            # Hard post-validation: no duplicate food_ids within the plate
            # Hard post-validation: no duplicate food names (case-insensitive)
            # Quick Quality Filter — returns (passed, penalty, reason)
            # Track soft cuisine incompatibility for diagnostics (not a reject)
            # We do not count it under rejection_stats as it is a soft penalty, not a rejection
            # Attach penalty score for use by meal_scorer
        # ── Phase 1B: YAML-configurable diversity filter ──────────────────
        # Simple proxy scoring function for the diversity filter
        def _score_plate(plate):
    # [Logic Hidden]
        # If still empty — build a guaranteed fallback plate
        # ── Phase 0: Log summary + write JSONL metrics ────────────────────
        # Human-readable summary log (always)
        # Structured JSONL record — best-effort
    def _is_valid_composition(self, plate: List[Dict], meal_type: str, template: Dict = None) -> bool:
    # [Logic Hidden]
        """
        """
        # Template role validation (required and forbidden roles)
            # Enforce required roles for dynamic combos, with combo_meal flexibility
                # Forbidden roles checked only for dynamic combos (blueprints are pre-curated)
        # 1. Deduplication by food_id
        # 2. dish_family collision check (new in v4)
        # 3. Per-item meal-type suitability (hard type + score threshold)
        # Analyze components
    def _is_valid_composition_with_reason(
    # [Logic Hidden]
                # Forbidden role check only applies to dynamic candidates.
                # Blueprint meals are pre-curated combinations and may contain
                # side/raita/salad foods that a template forbids — those are fine.
        # ── V6 Meal Realism Checks ───────────────────────────────────────────
        # Enforce meal size limits on all plates (blueprint and dynamic)
        # Enforce at most one optional side dish on all plates
        # --- Phase 2: Blueprint validation ---
        # Categorize every food in the plate into blueprint roles using our helper
        # Blueprint meals (from meal library, have meal_id) are pre-curated — skip Phase 2
                # Hard requirement: (Protein OR Dairy) AND Carb
                # Dairy/raita (curd/yogurt/milk) is a valid protein source at breakfast
                # Hard requirement: Protein AND Carb
                # Soft preference: Vegetable + Side (relaxed — prevents all-empty slots)
                # Hard requirement: Protein AND Carb
                # Soft preference: Vegetable + Side (relaxed — prevents all-empty slots)
                # Required: At least one of: protein, dairy, fruit
        # --- Phase 3: Compatibility Engine ---
        # Helper classification functions prioritizing metadata
        def check_rice(item):
    # [Logic Hidden]
        def check_sandwich(item):
    # [Logic Hidden]
        def check_pasta(item):
    # [Logic Hidden]
        def check_chapati(item):
    # [Logic Hidden]
        def check_milkshake(item):
    # [Logic Hidden]
        def check_curry(item):
    # [Logic Hidden]
        def check_starch(item):
    # [Logic Hidden]
        def check_main(item):
    # [Logic Hidden]
        def check_complete_meal(item):
    # [Logic Hidden]
        def check_protein_main(item):
    # [Logic Hidden]
        # Check all unique pairs
                # 1. Rice + Sandwich/Burger/Roll
                # 2. Rice + Pasta/Noodles/Macaroni
                # 3. Chapati + Pasta/Noodles/Macaroni
                # 4. Milkshake/Smoothie + Curry
                # 5. Two main starches
                # 6. Two complete meals
                # 7. Two protein mains (unless defined by blueprint)
    def _log_composition_reject(
    # [Logic Hidden]
        """Emit a structured DEBUG record describing a composition rejection.
        """
    def _get_blueprint_candidates(
    # [Logic Hidden]
        # Default: all compatible meals are candidates (overridden for NonVeg below)
        # For NonVeg users: strongly prefer NonVeg blueprints so actual meat/fish/egg
        # meals appear regularly, not just the occasional egg item from a veg-heavy pool.
        # Strategy: use NonVeg-only pool first; fall back to veg blueprints only if the
        # NonVeg pool is empty for this meal_type.
                # Put Maharashtrian blueprints first
                # Keep the order: Maharashtrian first
            # Use ~70% NonVeg, ~30% Veg.  Always include at least a handful of veg
            # options so the meal has side dishes (dal, sabzi, salad, etc.).
                # Safety: fall back to everything compatible
        # Regional filtering for Maharashtrian preference
                    # Apply per-item allowlist check only — weekly cuisine limit is
                    # enforced at meal-blueprint level by WeeklyOptimizer, not here.
        # ── V6 meal size constants — driven by meal_blueprints config ──────────
            # ── Blueprint pruning (V6) ──────────────────────────────────
            # Classify each food in the blueprint into mandatory vs optional-side.
            # If the resulting plate would exceed the size limit, keep all mandatory
            # items and randomly retain at most ONE optional side dish.
                # Classify using a fast name-based heuristic (no graph lookup yet)
                # Keep one random side at most
                # Trim further if still over limit (e.g. many mandatory items)
                # Replace dominant/banned side items with a varied alternative
                    # Check individual node diet compatibility (vegetarian/vegan safety)
                    # Vegetarian users: block all non-veg foods (meat, fish, AND eggs)
                    # Check individual node user safety (allergies, exclusions, blocklist)
                    # Cross-meal exclusion
                    # Check weekly food repeat limit
                    # Check recommendation flag
                    # Within-plate deduplication by food_id
    def _quick_quality_filter(
    # [Logic Hidden]
        """
        """
        # Load bounds from config
        # ── Per-item tracking ────────────────────────────────────────────
        # Load cuisine compatibility map from config
        # Soft penalty accumulator
            # Hard: duplicate dish_family
            # Hard: duplicate primary_ingredient when role is protein_main
            # Soft: track cuisine
            # Soft: track cooking style
        # ── Hard: calorie bounds (pre-optimization estimate) ─────────────
            # Only reject if clearly out of range (pre-optimization estimate, not exact)
            # Using scaling factor range [0.3, 3.0] to check feasibility
        # ── Soft: incompatible cuisine mix ───────────────────────────────
            # Find if any two cuisines belong to different groups
                # Incompatible cuisine mix: soft penalty instead of hard reject
        # Cuisine repetition: penalise if any cuisine appears >1 time
        # Cooking style repetition: penalise if any style appears >1 time
    def _quick_quality_filter_with_reason(
    # [Logic Hidden]
        """Thin wrapper around _quick_quality_filter that also returns a reason string.
        """
    def _build_fallback_meal(
    # [Logic Hidden]
        """
        """
        def _is_eligible(node: dict, check_variety: bool = True, check_regional: bool = True) -> bool:
    # [Logic Hidden]
            # V6: Skip foods with zero/invalid nutrition data
                    # Per-item allowlist check only — weekly cuisine limit is enforced at
                    # meal-blueprint level by WeeklyOptimizer, not at the side-dish level.
        # Sort by protein_density descending
        # Slot 1: best protein source
        # Slot 2: best carb that does not repeat dish_family
        # For Lunch and Dinner, we also want a vegetable and a side dish (salad/raita/soup)
            # Slot 3: Vegetable side
            # Slot 4: Salad/Raita/Soup side
            # Slot 3: Side dish if meal target calories are high (> 800 kcal) for other meals (breakfast/snack)
    def _pick_food_for_role(
    # [Logic Hidden]
        """Pick one food item that satisfies a template slot role.
        """
        # Role → category/dish_family hints for weighted sampling
        # Split candidates into preferred (match role categories) and fallback
            # Exclude starch foods from protein_main slot to avoid incompatible_two_starches conflicts
            # Exclude main carbs, protein mains, and combo meals from side/non-main roles
    def _get_base_scores(self, goal: str, meal_type: str, diet_type: str, target_cuisine: str, expected_roles: set) -> Dict[str, float]:
    # [Logic Hidden]
        # Goal-based weight vectors: (protein_density, role_match, cuisine_match, compatibility)
            # Diet-type multiplier: strongly prefer foods matching user's diet
    def _get_dynamic_candidates(
    # [Logic Hidden]
        """Template-driven dynamic candidate generation (Phase 1A).
        """
        # Expected meal roles per meal_type (for role_match score)
        # Pre-filter: diet + meal-type suitability + exclusion
            # Diet compatibility: Veg users must never see NonVeg/egg foods;
            # Vegan users must see only Vegan foods.
            # V6: Skip foods with zero/invalid nutrition data
            # Regional filtering for Maharashtrian preference
                    # Per-item allowlist check only — weekly cuisine limit is enforced
                    # at meal-blueprint level by WeeklyOptimizer, not at side-dish level.
        # If daily protein target is high, boost foods with high protein density
        def _goal_score(node: dict) -> float:
    # [Logic Hidden]
            # Apply DailyMealContext diversity weight
            # Apply Weekly variety soft penalty
                # Check weekly dish family frequency
                # Check weekly cuisine frequency
                # Check weekly breakfast category frequency to avoid repeating categories consecutively or too often
        # Determine required slots from template; fall back to a sensible default
            # Template has no required slots — use a bare protein+carb default so
            # dynamic generation still produces something useful.
        # Generate N candidate plates, each filled slot-by-slot from the template
                    # Never overwrite semantics["meal_role"]
                # --- Blueprint Completion ---
                # Step 1: Identify which blueprint roles are already satisfied by the current candidate foods
                # Step 2: For each unsatisfied required role, select the best available food
                # that fills that role and is compatible with the existing candidate.
                    # Check if template forbids this role
                # Step 3: Revalidate the complete candidate
                # Step 4: If invalid, Compatibility Replacement
                        def _replacement_score(node):
    # [Logic Hidden]
                        # Try up to 5 compatible replacements
                                # Log COMPATIBILITY_REJECTION
                                # Track compatibility rejection count at generator state
    def _diversity_filter(self, candidates: List[List[Dict]], top_n_percent: float = 0.5, score_fn=None) -> List[List[Dict]]:
    # [Logic Hidden]
        """
        """
            # Generate signature
        # Sort by score if provided so we keep the best diverse candidates
        # Keep only the requested top percentage based on variety
```

## backend-python\app\nutrition_engine\config.py
```python
def load_nutrition_rules():
    # [Logic Hidden]
```

## backend-python\app\nutrition_engine\daily_rule_engine.py
```python
class DailyRuleEngine:
    # [Logic Hidden]
    """
    """
    def __init__(self):
    # [Logic Hidden]
    def evaluate_context(self, user_profile: Dict, day_index: int, meal_type: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
    # [Logic Hidden]
        """
        """
        # 1. Day of week rules
            # Weekends allow more elaborate cooking
            # Weekdays
        # 2. Workout Rules
        # 3. Weather / Season Rules
```

## backend-python\app\nutrition_engine\engine.py
```python
class NutritionEngineV6:
    # [Logic Hidden]
    """
    """
    def __init__(self, data_dir: str = 'data', config_dir: str = 'config', db_client=None):
    # [Logic Hidden]
    def generate_plan(self, user_profile: Dict[str, Any], user_id: str = "mock_user", week_start: str = "2026-06-22") -> Dict[str, Any]:
    # [Logic Hidden]
        """
        """
        # 1. Check cache first
            # Instantiate request-scoped modules
            # Generate the weekly layout
            # 3. Optimize ingredients (batch reuse)
            # DISABLED: IngredientOptimizer swaps food_ids without fetching correct macros/units,
            # violating strict food identity and causing duplicates within the same meal.
            # weekly_plan = self.ingredient_optimizer.optimize(weekly_plan)
            # 4. Validate the generated plan holistically
            # New Serialized Validation Step
            # 5. Save to Cache if valid
                # Log all validation failures using structured logging
    def generate_meal_swaps(self, user_profile: Dict[str, Any], week_start: str, day: int, meal_type: str, original_meal: Dict[str, Any], user_id: str = "mock_user", count: int = 3) -> List[Dict[str, Any]]:
    # [Logic Hidden]
        """
        """
        # 1. Check Cache
        # Extract original properties for validation
        # We need a template that matches the original meal structure
                # Prevent suggesting the exact same meal
                # Validation
                # Structural Bounds Check
                # Optional weight/prep bounds, but typically we want them somewhat similar
        # 3. Save to Cache
```

## backend-python\app\nutrition_engine\food_graph.py
```python
# Required fields that every node MUST have after loading.
# Missing any of these causes a startup failure — do NOT silently continue.
def _freeze(obj):
    # [Logic Hidden]
    """
    """
def _map_category_to_meal_role(category: str) -> str:
    # [Logic Hidden]
    """Map broad food categories to specific compatibility matrix meal roles."""
def _build_cuisine_keyword_map() -> dict:
    # [Logic Hidden]
    """
    """
    # Preserve YAML ordering (most-specific first)
def _detect_cuisine_by_keywords(food_name: str) -> Optional[str]:
    # [Logic Hidden]
    """
    """
def normalize_cuisine_name(name: str) -> str:
    # [Logic Hidden]
def _csv_region_to_cuisine(region: str) -> str:
    # [Logic Hidden]
    """
    """
class FoodGraph:
    # [Logic Hidden]
    """
    """
    def __init__(self, ingredient_db_path: str, recipe_db_path: str, relationship_path: str, nutrition_csv_path: str):
    # [Logic Hidden]
    def _load_layers(self):
    # [Logic Hidden]
            # 1. Load Ingredients
            # 2. Load Recipes
            # 3. Load Relationships (optional, fallback to empty if missing)
            # 4. Load Nutrition
            # Combine meta
            # Check for is_recommended flag in any metadata
            # Merge into a single node dictionary
                # Sanitize is_vegan and is_vegetarian against incorrect database entries
                # Fetch baseline database nutrients
                # Logical Portion Normalization & Serving Limits (Phase 3, 4, 5, 8)
                    # Plain boiled/poached egg — enforce per-egg serving bounds
                    # without overriding macros (those come correctly from CSV).
                # Perform macro scaling for standard items
                # Calorie validation and correction logic (Phase 2)
                # Inject standard serving limits
                # ── Nutrition Validation (config-driven, Part 5) ──────────────
                # ── Regional cuisine resolution — data-first strategy ────────
                # Priority 1: CSV region column → cuisine via config map
                # Priority 2: metadata regional_cuisine field
                # Priority 3: YAML cuisine_keyword_map fallback (emits warning)
                # Priority 4: Pan Indian default (emits warning)
                    # Data-driven: trust the dataset region column if it is specific
                    # Specific metadata is missing and CSV region is not specific (or is Pan Indian / missing).
                    # Run keyword detection to find a specific cuisine.
                # Construct the raw node structure
                # Validate, log warnings, and apply fallbacks for missing metadata
                # ── Serving metadata & conversion for household units ──
                # In-memory Serving unit & quantity exposure
                # 2. food_group
                # 3. meal_role
                # 4. dish_family
                # 5. cuisine
                # 6. cooking_style
                # 7. breakfast_category (runtime only)
                    # We check patterns against: food_name, dish_family, cuisine, food_group, meal_role
                # ── Nutrition validity flag ───────────────────────────
            # ── STARTUP INTEGRITY VALIDATION ────────────────────────────────
            # Fail fast if any node is structurally corrupt.
            # Do NOT silently accept bad data — fix the dataset instead.
                # Log each bad node and raise exception - Fail Fast as user requested
            # ── FREEZE ALL NODES ────────────────────────────────────────────
            # After freezing, no code may modify nodes in-place.
            # Every consumer MUST copy.deepcopy() before mutating.
    def get_node(self, food_id: str) -> Optional[Any]:
    # [Logic Hidden]
        """Returns the frozen node for a food_id, or None."""
    def get_all_nodes(self) -> Dict[str, Any]:
    # [Logic Hidden]
        """
        """
    def get_ingredients(self) -> Dict[str, Any]:
    # [Logic Hidden]
    def get_recipes(self) -> Dict[str, Any]:
    # [Logic Hidden]
    def get_compatibility_score(self, role: str, node: Any) -> int:
    # [Logic Hidden]
        """Returns how compatible this node is with a specific role."""
    def filter_by_hard_constraints(self, diet_type: str, max_prep_time: int) -> List[str]:
    # [Logic Hidden]
        """Returns a list of food_ids that pass basic static filters."""
```

## backend-python\app\nutrition_engine\food_utils.py
```python
def _load_suitability_blocks():
    # [Logic Hidden]
    """Load meal_suitability_blocks from nutrition_rules.yaml once at import time."""
        # Fallback defaults if YAML is missing/unreadable
def get_food_family(name: str, swap_group: str = '') -> str:
    # [Logic Hidden]
    # ── Granular families for swap-option matching ──────────────────────────
    # Rice-based staples
    # Roti / Bread family — so swaps for roti only return other breads
    # Dal & Lentils
    # Animal proteins — separate families for better swaps
    # Paneer / Tofu
    # Vegetables / Curry / Sabzi
def get_primary_unit(food_name: str) -> str:
    # [Logic Hidden]
    """
    """
    # Precise overrides first
def get_meal_suitability(food_name: str, meal_type: str) -> int:
    # [Logic Hidden]
    """
    """
    # ── Config-driven hard blocks (loaded once at import) ────────────────────
    # 1. Foods blocked from ALL meal types (sweets/desserts)
    # 2. Foods that are breakfast-only (score 0 for lunch/dinner/snack)
```

## backend-python\app\nutrition_engine\ingredient_optimizer.py
```python
class IngredientOptimizer:
    # [Logic Hidden]
    """
    """
    def __init__(self, food_graph):
    # [Logic Hidden]
    def optimize(self, weekly_plan: Dict[str, Any]) -> Dict[str, Any]:
    # [Logic Hidden]
        """
        """
        # Track ingredient usage across the week
        # Identify sparse ingredients (used only once) and try to map them to dominant ones in the same family
            # Find dominant item
            # If the dominant item is used multiple times, swap single-use items to it
                        # Perform swap in the plan
    def _apply_swap(self, weekly_plan: Dict, old_id: str, new_id: str, new_name: str):
    # [Logic Hidden]
                        # Note: we should strictly fetch the new node's nutrition, but for a
                        # simple semantic swap within the same family, macros are usually similar.
                        # Update semantics
```

## backend-python\app\nutrition_engine\meal_scorer.py
```python
class MealScorer:
    # [Logic Hidden]
    """
    """
    def __init__(self, variety_tracker=None):
    # [Logic Hidden]
        # New Scoring Weights based on user specifications: 60% Nutrition, 40% Culinary
    def score_candidate_plate(self, plate: List[Dict], target_macros: Dict, current_day: int, meal_type: str = "unknown", goal: str = "Maintenance", previous_meals: List = None, preferred_region: str = None) -> Dict[str, Any]:
    # [Logic Hidden]
        """
        """
        # 1. Macro Accuracy (25%)
        # 2. Semantic Compatibility (25%)
        # 3. Meal Completeness (15%)
        # In this implementation, the Candidate Generator ensures required roles exist.
        # But we can reward having preferred optional items.
        # 4. Realism & Satisfaction (15%)
        # 5. Weekly Variety (10%)
        # 6. Portion Realism (5%)
        # 7. Budget & Availability (5%) - Stubbed for future expansion
        # 8. Regional Score (Phase 7 preference boost)
            # Map aliases for Pan Indian / All India
        # 60% nutrition / 40% culinary weight distribution
    def score_culinary(self, plate: List[Dict], current_day: int) -> float:
    # [Logic Hidden]
        """
        """
        # We re-weight this to be out of 100 based on the weights used in score_candidate_plate
        # The culinary weights sum to 0.40 (10 + 5 + 10 + 10 + 5 portion)
        # We'll just sum them up directly using the same weights to keep relative scoring intact.
    def _score_macros(self, plate: List[Dict], target: Dict, goal: str) -> float:
    # [Logic Hidden]
        # Goal-aware continuous macro scoring
        # Normalize weights if some macros are omitted in target
        # Convert diff to a 0-100 score
    def _score_semantics(self, plate: List[Dict]) -> float:
    # [Logic Hidden]
        # Phase 3: Evaluate compatibility matrix
        # Check all unique pairs
                # Check A -> B
                # Check B -> A
                # Use the lowest compatibility score
        # Phase 7: Continuous compatibility scoring with rewards and penalties from YAML
        # Lowercase helper variables
        # Check Rewards
        # Check Penalties
        # 1. Rice + Sandwich
        # 2. Milkshake + Curry
        # 3. Two heavy starches
        # 4. Three dairy items
        # 5. Soup, raita and salad together
    def _score_completeness(self, plate: List[Dict]) -> float:
    # [Logic Hidden]
        """
        """
        # Structural bonuses (soft rewards instead of hard failures)
    def _score_realism(self, plate: List[Dict]) -> float:
    # [Logic Hidden]
        # Penalize weird combinations
        # Penalize if it only contains side dishes
        # Phase 3: Reward Food Group Diversity
        # Texture/Temperature variety
        # Satiety / Volume density heuristic
        # If total volume is high but calories are low, good for weight loss
    def _score_variety(self, plate: List[Dict], current_day: int, meal_type: str = "unknown") -> float:
    # [Logic Hidden]
        # Compute abstract Meal Signature
        # Get historical usage count
        # Exponential Decay (Decay factor 1.5)
        # Load penalties from config
        # Consecutive breakfast category penalty
        # Cuisine repeat penalty
            # Continuous soft variety penalties
            # 1. Same food consecutive days
            # 2. Same food repeats
            # 3. Same dish family repeats
            # Grocery Optimization: Raw ingredient reuse scoring
                # Check if ingredient was used in previous days
    def _score_portion(self, plate: List[Dict]) -> float:
    # [Logic Hidden]
            # Penalize absurd quantities for realistic units
```

## backend-python\app\nutrition_engine\nutrition_calculator.py
```python
def calculate_base_daily_targets(user_profile: Dict[str, Any]) -> Dict[str, float]:
    # [Logic Hidden]
    # Normalize goal
    # Normalize activity level
    # BMR
    # Activity multiplier
    # Goal adjustments
class WeeklyMacroPlanner:
    # [Logic Hidden]
    """
    """
    def _infer_intensity_from_workout_day(self, day: Dict) -> str:
    # [Logic Hidden]
    def plan_week(self, user_profile: Dict[str, Any]) -> Dict[str, Dict[str, float]]:
    # [Logic Hidden]
        # Map day 1-7 to workout intensity
            # Carbs absorb the variance
class MealMacroDistributor:
    # [Logic Hidden]
    """
    """
    # Each tuple: (calories, protein, carbs, fat)
        # Rest day: balanced, slightly lighter lunch, no workout fuel needed
        # Light day: slight calorie shift toward lunch
        # Moderate day: standard distribution
        # Hard day: more fuel at lunch (pre-workout window), protein-heavy dinner
        # Very hard: maximize carb availability pre-workout, high protein dinner
    def distribute(self, daily_target: Dict[str, Any]) -> Dict[str, Dict[str, float]]:
    # [Logic Hidden]
```

## backend-python\app\nutrition_engine\nutrition_rule_engine.py
```python
class NutritionRuleEngine:
    # [Logic Hidden]
    """
    """
    def __init__(self, config_path: str):
    # [Logic Hidden]
    def _load_rules(self) -> Dict:
    # [Logic Hidden]
    def get_goal_multipliers(self, goal: str) -> Dict:
    # [Logic Hidden]
        """Returns the specific protein/fat multipliers and calorie offsets for a given goal."""
        # Fallback to maintenance if goal not found
    def get_meal_distribution(self, meal_type: str) -> Dict:
    # [Logic Hidden]
        """Returns the percentage distribution and minimums for a specific meal."""
            # Default generic distribution if not defined
```

## backend-python\app\nutrition_engine\plan_cache.py
```python
class WeeklyPlanManager:
    # [Logic Hidden]
    """
    """
    def __init__(self, db_client=None):
    # [Logic Hidden]
    def _generate_profile_hash(self, user_profile: Dict) -> str:
    # [Logic Hidden]
        """Generates a hash of the user's macro targets, diet type, and restrictions."""
            # Include both keys so a change to either invalidates the cached plan
    def get_valid_plan(self, user_id: str, user_profile: Dict, week_start: str) -> Optional[Dict]:
    # [Logic Hidden]
        """
        """
            # Verify profile hasn't changed significantly
    def save_plan(self, user_id: str, user_profile: Dict, week_start: str, plan_data: Dict) -> str:
    # [Logic Hidden]
        """
        """
            # Deactivate older plans for this week
    def get_cached_swaps(self, user_id: str, user_profile: Dict, week_start: str, day: int, meal_type: str, meal_hash: str) -> Optional[List[Dict]]:
    # [Logic Hidden]
        """
        """
    def save_cached_swaps(self, user_id: str, user_profile: Dict, week_start: str, day: int, meal_type: str, meal_hash: str, swaps: List[Dict]):
    # [Logic Hidden]
        """
        """
            # Upsert
```

## backend-python\app\nutrition_engine\plate_builder.py
```python
class PlateBuilder:
    # [Logic Hidden]
    """
    """
    def __init__(self, food_graph):
    # [Logic Hidden]
    def build_plate(self, anchor: Dict, template: Dict[str, Any], valid_nodes: List[Dict], meal_type: str) -> List[Dict]:
    # [Logic Hidden]
        """
        """
        # Fill Required Roles
        # Phase 4.9: Plate Completeness Check
        # The optimizer should *never* repair an incomplete plate.
        # Fill Optional Roles
            # Check anchor's structural_rules
            # Add if preferred, or 50% chance for variety if not
    def _find_best_match_for_role(self, role: str, valid_nodes: List[Dict], current_plate: List[Dict], anchor: Dict, meal_type: str) -> Dict:
    # [Logic Hidden]
            # Phase 4.9: Must not be forbidden by anchor's structural rules
            # Must not have exact 0 compatibility
        # Sort by compatibility
        # Pick from top 3 to ensure some variety
```

## backend-python\app\nutrition_engine\portion_optimizer.py
```python
# Per-food calorie caps: prevents any single side item from being over-scaled
# Keys are substrings matched against food_name.lower()
# Overrides for salad-like foods: max bowls regardless of protein target
def _format_serving(qty: float, unit: str, name: str = '', cal: float = 0.0) -> str:
    # [Logic Hidden]
    """Produce a clean human-readable serving string based on database unit and quantity."""
    # Fallback
def _get_portion_profile(food_name: str, unit: str, base_qty: float) -> List[float]:
    # [Logic Hidden]
    # Deprecated: Static lists capped quantities too low for high-calorie goals (e.g., max 250g rice).
    # We now rely on dynamic p_step, p_min, and p_max to allow proper scaling.
class PortionOptimizer:
    # [Logic Hidden]
    """
    """
    def __init__(self):
    # [Logic Hidden]
    def get_max_capacity(self, components: List[Dict]) -> Tuple[float, float]:
    # [Logic Hidden]
        """Calculates the absolute maximum calories and protein a plate can provide based on household constraints."""
            def get_val(keys, default=None):
    # [Logic Hidden]
    def optimize_portions(self, components: List[Dict], target_macros: Dict) -> List[Dict]:
    # [Logic Hidden]
        """
        """
        def get_priority_level(food: Dict, unit: str) -> int:
    # [Logic Hidden]
            # 1. Protein — scale first to hit protein/calorie targets
            # 2. Carbohydrates / Staple — fill calorie gap second
            # 3. Vegetables — volumetric, scale third
            # 4. Side Dishes (Salad, Raita, Curd, Fruits, Chutney, Soup, Drink) — scale last
            # 5. Fats / Oils / Condiments — never scale these up
        # 1. Initialize State
            def get_val(keys, default=None):
    # [Logic Hidden]
            # Fetch priority keys from metadata, semantics, or root
            # Fallbacks
            # Apply specific overrides from config/rules
            # ── V6 Realistic household serving caps ───────────────────────────
            # Roti / Paratha / Chapati / Naan / Bread — max 5 pieces
            # Rice / Pulao / Biryani — max 3 bowls
            # Dal / Curry / Sabzi / Paneer / Meat / Egg — max 3 bowls
            # Milk / Yogurt / Lassi / Drinks — max 2 glasses/cups
            # Snapping min/pref/max to steps
            # Apply side foods calorie cap
        # 2. Initial Analytical Scaling (with Protein Awareness if target_pro is provided)
                # Group items
                    # Solve equations:
                    # x_p * C_p + x_c * C_c = T_C
                    # x_p * P_p + x_c * P_c = T_P
                    # Fallback to decoupled heuristic if solved values are out of bounds or negative
                    # Decoupled heuristic if only one group is present
                # Clamp multipliers to safe range
                # Apply multipliers and snap
                # Standard calorie-only scaling
            # Recalculate current values
        # 3. Fine-tuning Greedy Scaling with Protein and Calorie Awareness
            # ── Phase 1: Fine-tune Protein using Group 1 (Protein-rich foods) ──
            # Track the combination that minimises the protein error to avoid overshoot.
                    # Sort increments by protein density (protein per calorie) descending
                    # Sort decrements by protein density ascending (to minimize calorie impact when dropping protein)
                # Track best protein configuration
            # Restore best protein quantities before calorie phase
            # ── Phase 2: Fine-tune Calories using Group 2 (Carb/other foods) ──
            # Track the combination that minimises the combined calorie+protein error.
                    # Sort by priority, then least scaled ratio
                    # Sort by reverse priority, then most scaled ratio
                # Track best combined configuration
            # Restore the best overall combination before building the result
            # Standard Calorie-only Greedy Fine-Tuning
        # 3. Build Result list
def optimize_portions(components: List[Dict], target_cal: float) -> Tuple[List[Dict], float]:
    # [Logic Hidden]
    """
    """
```

## backend-python\app\nutrition_engine\serving_validator.py
```python
"""
"""
# ---------------------------------------------------------------------------
# Serving unit whitelist — keyed on food name keyword (lowercase)
# Checked in order; first match wins.
# ---------------------------------------------------------------------------
    # keywords                              allowed units
# Units that are NEVER valid for any food (catch-all corruption markers)
# Foods that must NEVER be measured in these units even from the catch-all
def is_valid_serving_unit(food_name: str, unit: str) -> Tuple[bool, str]:
    # [Logic Hidden]
    """
    """
    # 1. Check food-specific forbidden map first (most specific)
    # 2. Walk whitelist rules — first match is authoritative
            # matched a rule but unit is wrong
    # 3. No whitelist rule matched — only reject if the unit is in the global forbidden set
def compute_food_hash(food_id: str, nutrition: Dict, serving_unit: str) -> str:
    # [Logic Hidden]
    """
    """
    # Round nutrition to 1dp to avoid float noise
class FoodIdentityValidator:
    # [Logic Hidden]
    """
    """
    def __init__(self, food_graph):
    # [Logic Hidden]
        # Build food_id → canonical node lookup
    def validate_item(self, item: Dict) -> Tuple[bool, List[str]]:
    # [Logic Hidden]
        """
        """
        # --- Check 1: food_id exists ---
            # Try case-insensitive fuzzy — food_id might have suffix
        # --- Check 2: food_name matches database ---
        # --- Check 3: nutrition belongs to food_id ---
        # We can't check absolute cal equality (scaled by portion), but we can
        # ensure the item's per-100g calories are not wildly different from the DB.
        # For scaled items check that nutrition is derivable from the DB (ratio check).
        # Estimate expected calories at the given serving_qty
        # db_cal is per 1 serving (serving_size_g grams)
            # The ratio should be consistent (within ±30% for scaling differences)
            # item nutrition = db_nutrition * scale_factor
            # We just verify the item calories are positive and not astronomically wrong
        # --- Check 4: serving unit valid ---
        # --- Check 5: food_name is not empty ---
        # --- Check 6: nutrition not null ---
    def validate_plan(self, weekly_plan: Dict) -> Dict:
    # [Logic Hidden]
        """
        """
                    # food_hash check — detect if same food_id shows different nutrition
                    # Per-item identity check
```

## backend-python\app\nutrition_engine\template_manager.py
```python
class TemplateManager:
    # [Logic Hidden]
    """
    """
    def __init__(self, template_path: str):
    # [Logic Hidden]
    def _load_templates(self):
    # [Logic Hidden]
            # Basic validation
    def get_templates_for_meal(self, meal_type: str, region: str = "pan_indian") -> List[Dict[str, Any]]:
    # [Logic Hidden]
        """
        """
        # Start with regional templates
        # Fallback to pan_indian if no regional templates exist
        # Sort by priority descending
    def filter_feasible_templates(self, templates: List[Dict[str, Any]], target_macros: Dict[str, float]) -> List[Dict[str, Any]]:
    # [Logic Hidden]
        """
        """
            # Default to very loose bounds if not explicitly defined
    def validate_template_schema(self, template: Dict[str, Any]) -> bool:
    # [Logic Hidden]
        """
        """
```

## backend-python\app\nutrition_engine\variety_tracker.py
```python
class WeeklyVarietyTracker:
    # [Logic Hidden]
    """
    """
    def __init__(self):
    # [Logic Hidden]
    def reset(self):
    # [Logic Hidden]
        # Family Tracking to prevent multiple "Breads" or "Curries"
        # New Phase 4 Strict Trackers
        # V6 Weekly counters & breakfast rotation trackers
    def get_snapshot(self) -> Dict:
    # [Logic Hidden]
    def restore_snapshot(self, snapshot: Dict):
    # [Logic Hidden]
    def meal_history(self, meal_type: str) -> Set[str]:
    # [Logic Hidden]
    def get_days_foods_used(self, day_num: int) -> Set[str]:
    # [Logic Hidden]
        """Returns the set of food_ids already assigned to ANY meal slot today.
    # --- V6 Interfaces ---
    def calculate_variety_penalty(self, food_id: str, family: str, current_day: int) -> float:
    # [Logic Hidden]
        # Penalize if food eaten in last 4 days
        # Penalize repeated family
    def record_food(self, food_id: str, family: str, current_day: int):
    # [Logic Hidden]
    # --- Legacy Interfaces (Still supported for transition) ---
    def record_meal(self, meal_type: str, components: List[Dict]):
    # [Logic Hidden]
        """Register a chosen meal so future days can avoid repeats."""
    def record_cuisine(self, region: str):
    # [Logic Hidden]
    def record_template(self, bp_idx: int):
    # [Logic Hidden]
    def variety_penalty(self, meal_type: str, components: List[Dict],
    # [Logic Hidden]
        """Return a penalty score (≥0) that is subtracted from the meal score."""
            # Repeated food name
            # Repeated family within the last 3 days (approx 12 main meals)
            # Repeated protein source
            # Repeated carb
        # Repeated cuisine
        # Repeated template
    def record_meal_selection(self, meal_id: str, foods: List[str], protein_source: str, carb_source: str, vegetables: List[str], day_num: int, cuisine: str = None, cooking_style: str = None, meal_signature: str = None, food_ids: List[str] = None, breakfast_category: str = None):
    # [Logic Hidden]
        # Track food_ids across ALL meal slots for cross-meal exclusion
            # Fallback: use food names as ids when food_ids not provided
    def is_duplicate_meal(self, meal_id: str, foods: List[str], protein_source: str, carb_source: str, day_num: int, meal_type: str, cuisine: str = None, cooking_style: str = None) -> bool:
    # [Logic Hidden]
        # 1. Same exact food: Cannot repeat within X days.
        # We can't check same_day duplicate directly because the user wants "Same exact food Cannot repeat within N days"
        # but specifically tailored to the meal_type's rule. Let's adjust is_same_day_duplicate
        # Only truly neutral, tiny-portion staple sides are exempt from the
        # repeat check. Main carbs like rotis and rice are NOT exempt so the
        # engine is forced to diversify them across the week.
        # 2. Same meal identity: Cannot repeat within X days.
        # 3. Same protein source: Maximum X consecutive meals.
        # 4. Same cuisine: Maximum X times/day.
        # 5. Same cooking method: Maximum X consecutive meals.
```

## backend-python\app\nutrition_engine\weekly_optimizer.py
```python
class WeeklyOptimizer:
    # [Logic Hidden]
    """
    """
    def __init__(self, candidate_generator: CandidateGenerator, meal_scorer: MealScorer, portion_optimizer: PortionOptimizer, template_manager: TemplateManager, variety_tracker: WeeklyVarietyTracker):
    # [Logic Hidden]
        # Phase 4.9 Planners
    def _get_meal_cuisine(self, candidate_plate: List[Dict]) -> str:
    # [Logic Hidden]
        """
        """
    def generate_weekly_plan(self, user_profile: Dict[str, Any]) -> Dict[str, Any]:
    # [Logic Hidden]
        """
        """
        # Normalize profile keys
            # Eggetarian: vegetarian + eggs (treat as Vegetarian but allow egg foods)
        # Day name mapping (Day_1 = Monday .. Day_7 = Sunday)
            # 1. Plan Explicit Weekly Targets (cycles calories based on workout intensity)
            # Full week reset for variety tracker
            # ── iterate over every day (Day_1 … Day_7) ──────────────────────────
                # Use a human-readable day name as the plan key so both
                # meal_engine.py and the frontend can look up by "Monday" etc.
                # Snapshot at the start of the day
                # 2. Distribute daily target explicitly to 4 meals based on intensity ratios
                # Retry loop for per-day validation
                # Use configuration-driven daily retry limit instead of hardcoding attempts < 1
                    # Snapshot before this attempt
                    # Create a fresh daily context for diversity tracking
                    # Ensure snack is always processed last so it can fill remaining macro gap
                        # Apply running deficit to current target, but cap min to 50% to prevent negative runaway targets
                        # 3. Get Templates and filter by static schema (loose bounds)
                            # Fallback to all templates, let the data-driven validation handle it
                        # Cross-meal exclusion: collect food_ids already committed to earlier meals today
                        # Pass 1: Strict constraints (Rotation & Portion limits)
                        # Seed = day_num * 1000 + meal_type_idx * 100 + attempts
                        # This guarantees a unique shuffle for every (day, meal_type, attempt) combination
                        # Dynamic candidate distribution
                            # Data-driven template feasibility check
                                # Reject the template
                                # Enforce rotation & same-day duplicate prevention
                                # Supplement Policy Engine & Whey Limitation
                                            # Prefer whole foods over whey for low protein targets
                                            # For high targets, require whey + something else (not whey alone)
                                # --- FAST PRUNING ---
                                # Check if this plate can mathematically reach the macro targets before running SciPy
                                # Use 0.50 for all meal types — 0.75 was too aggressive and caused near-zero acceptance
                        # Optimize portions and score all strict candidates
                            # Best effort tracking (ignores 85% rule and visual balance)
                            # Enforce Visual Plate Balance
                            # Must hit between 85% and 115% of target protein for strict pass
                        # Perform Weighted Selection for Strict Pass
                            # Strict consecutive breakfast category filter
                            # Scaled Softmax to avoid overflow
                        # Pass 2: Fallback constraints if strict pass failed to find anything
                                    # Fallback frequency checking
                                    # Enforce rotation & same-day duplicate prevention in fallback
                            # Optimize and score fallback pool
                                # Best effort tracking (ignores 85% rule and visual balance)
                                # Enforce Visual Plate Balance
                                # Strict consecutive breakfast category filter in fallback
                        # Pass 4: Final Emergency Fallback
                        # 6. Apply Best Plate
                            # 7. Track variety
                            # Update daily context with this meal's ingredients
                            # Attach score breakdown to selected items
                            # Compute Meal Signature
                                # Use best available candidate even if it didn't pass all strict constraints
                    # 8. Strict Per-Day Validation
                    # Soft Constraint Relaxation — tolerances driven by nutrition_rules.yaml
                    # [daily_validator.calories/protein.first_attempt / second_attempt / final]
                        # Rollback variety tracker for this attempt
                    # Rollback to the start of the day to clean up failed attempts' pollution
                    # Replay/record the chosen best_day_plan to variety tracker
                                # Compute Meal Signature
                # Store under the standard day key (Day_1, Day_2, ...)
            # ── end of per-day loop ──────────────────────────────────────────────
            # Calculate duration and stats, log structured weekly summary
            # Always return the weekly plan after one full pass! (Never throw away 6 good days just because 1 failed)
    def _is_plate_visually_balanced(self, optimized_plate: List[Dict]) -> bool:
    # [Logic Hidden]
        """
        """
            # Identify carbs
            # Identify proteins/curries
        # Dry meal check (e.g. Chicken + Rice but no gravy)
            # Maybe it's a dry protein and a dry carb, which is too dry
        # Missing carb base check for main meals (Lunch/Dinner)
        # Assuming lunch/dinner usually have a carb base or are a combo meal
        # Since we don't have meal_type here easily, we rely on the candidate generator rules
        # If we have a significant amount of carbs, we need a proportional amount of protein/curry to eat it with
        # Is it just Dal + Raita? (Missing carb base but has high protein/side volume)
            # It's possible for low carb diets, so we let it pass if macros demand it,
            # but usually candidate generator will ensure a carb base exists if required.
```

## backend-python\app\nutrition_engine\weekly_validator.py
```python
class WeeklyValidator:
    # [Logic Hidden]
    """
    """
    def __init__(self):
    # [Logic Hidden]
    def validate_plan(self, weekly_plan: Dict[str, Any], user_profile: Dict[str, Any], daily_targets: Dict[str, float]) -> Dict[str, Any]:
    # [Logic Hidden]
        """
        """
        # Check holistic limits
        # Phase 5: The "Indian Family Test"
    def _indian_family_test(self, weekly_plan: Dict[str, Any], report: Dict[str, Any]):
    # [Logic Hidden]
        """
        """
                # Curry needs a carb
                    # Could be eating just dal or just chicken curry
                    # Exempt if it's soup or stew
                # Excessive dryness
                # Double heavy proteins
    def _map_food_to_blueprint_role(self, food: Dict, template_role: str = "") -> str:
    # [Logic Hidden]
        # Priority 0: Hard name/dish_family overrides — must come before category checks
        # Raita/pachadi is always a side dish regardless of category or food_group
        # Carb-based bases (sandwich, wrap, roll, toast, roti, paratha, chapati, naan, dosa, idli, poha, upma, oats, rice, bread, pasta, etc.)
            # If it is a carb base but contains a major protein keyword, it behaves as the protein main
        # Soup/shorba is always a side/soup
        # Chutney/pickle
        # Salad/kachumber - sprouted salads or salads with meat/dairy function as protein sources
        # 1. food_group/category + template_role
        # 2. dish_family
        # 3. Normalized category field from dataset (case-insensitive and plural-robust)
        # 4. Configuration-driven pattern map in nutrition_rules.yaml
        # 5. Food name matching as absolute last resort
    def validate_serialized_plan(self, serialized_plan: Dict[str, Any], daily_targets: Dict[str, float], user_profile: Dict[str, Any] = None) -> Dict[str, Any]:
    # [Logic Hidden]
        # Allergy checking setup
                    # Allergy check
                    # Same-day food duplicate check
                    # Nutrition
                    # Unit sanity
                # Blueprint validation check — aligned with generator rules (relaxed)
                # Hard requirements: Protein + Carb (prevents truly broken meals)
                # Soft requirements: Vegetable, Side, Fruit/Dairy (warnings only)
                    # Dairy/raita counts as protein at breakfast (curd/yogurt IS a protein source)
                # ── V6 Meal Realism Warnings (observability only) ─────────────────
```

## backend-python\app\routes\__init__.py
```python
# Routes package
```

## backend-python\app\routes\chatbot.py
```python
class ChatRequest(BaseModel):
    # [Logic Hidden]
# --- Rate Limiting variables ---
def _get_client_ip(request: Request) -> str:
    # [Logic Hidden]
    """Extract the best-effort real client IP from the request for rate limiting."""
async def chatbot_endpoint(
    # [Logic Hidden]
    """
    """
        # --- Rate Limiting ---
                # Drop stale entries first, then enforce strict max size to prevent memory growth.
        # --- Validate Input ---
        # --- Get AI Response ---
        # Fetch real-time activity and workout history
        # Check if reply is from fallback
```

## backend-python\app\routes\food_database.py
```python
"""
"""
# Load food database
def load_food_database():
    # [Logic Hidden]
    """Load food database from CSV"""
        # Categorize by meal type
            # Map meal types
            # Determine if vegetarian
            # Get swap group
            # Get goal
            # Get allergens
def categorize_food(name: str) -> str:
    # [Logic Hidden]
    """Categorize food based on name"""
async def get_food_database():
    # [Logic Hidden]
    """
    """
```

## backend-python\app\routes\meal_plan.py
```python
def _utcnow() -> datetime:
    # [Logic Hidden]
def _build_user_filter(user_id: str) -> Dict[str, Any]:
    # [Logic Hidden]
def _generate_profile_hash(profile: dict) -> str:
    # [Logic Hidden]
    """Generate SHA256 hash using specific profile fields."""
async def _archive_old_plans(user_id: str):
    # [Logic Hidden]
    """Marks all ACTIVE plans for this user as ARCHIVED."""
async def _generate_and_save_new_plan(user_id: str, profile: dict) -> dict:
    # [Logic Hidden]
    """Force new generation, archive old, save new ACTIVE, return."""
    # Generate new plan
        # Ensure we pass the correct structure
        # _generate_nutrition_plan from profile.py called generate_meal_plan(profile=profile, weekly_workout_plan=[])
        # If it's V6, let's just use generate_plan.
        # Wait, the engine wrapper in meal_engine.py might still have generate_meal_plan
        # But we saw in app.meal_engine that it wraps V6. Let's call the wrapper method,
        # or use get_meal_engine().generate_plan(profile) if available.
        # Actually in profile.py it called meal_engine.generate_meal_plan(profile, weekly_workout_plan=[])
        # We will try both interfaces just to be safe
        # V6 engine returns Day_1..Day_7 keys but frontend expects Monday..Sunday.
        # Remap here so every day shows its own unique meals.
    # Expire in 7 days
    # Return without the _id to make it JSON serializable
async def get_meal_plan(
    # [Logic Hidden]
    """
    """
    # Need regeneration (either missing, hash mismatch, or expired)
async def force_generate_meal_plan(
    # [Logic Hidden]
    """Force new generation, archive old plan, create new ACTIVE plan, return."""
```

## backend-python\app\routes\meal_tracking.py
```python
def _utcnow() -> datetime:
    # [Logic Hidden]
def _meal_progress_col():
    # [Logic Hidden]
def _meal_history_col():
    # [Logic Hidden]
class InitDayRequest(BaseModel):
    # [Logic Hidden]
class TickItemRequest(BaseModel):
    # [Logic Hidden]
async def init_day_meals(req: InitDayRequest):
    # [Logic Hidden]
    """Initialize a day's meal plan with tickable items"""
async def tick_item(req: TickItemRequest):
    # [Logic Hidden]
    """Tick/untick a meal item. Cannot modify if meal is locked."""
    # Bug #14 fixed: use atomic $set directly on the specific array element
    # to avoid the read-modify-write race condition.  We first validate the
    # document exists and that the item index is in range, then apply an
    # atomic update using dot-notation for the nested array position.
    # Lightweight validation read (only fetches the fields we need)
    # Bug #31 fixed: use timezone-aware UTC timestamps for consistency
    # Atomic update of just the specific item fields
    # Optimistically set updated fields
async def get_day_progress(user_id: str, date: str):
    # [Logic Hidden]
async def get_meal_history(user_id: str):
    # [Logic Hidden]
async def get_meal_history_by_date(user_id: str, date: str):
    # [Logic Hidden]
async def _save_to_history(user_id: str, date: str, meal_type: str, meal: dict):
    # [Logic Hidden]
    """Atomically upsert a completed meal into the history collection.
    """
    # Upsert the document and set the completed meal atomically
```

## backend-python\app\routes\profile.py
```python
# Prescription targets — single source of truth for water/sleep goals
    def get_prescription_targets(goal, level, age):
    # [Logic Hidden]
# Priority 3 — Adaptive modifier: adjust intensity/volume based on last 7 daily check-ins
def _utcnow() -> datetime:
    # [Logic Hidden]
# Import engine factories (lazy init at call-time).
def _get_plan_cache_if_available():
    # [Logic Hidden]
# Pydantic models
class ProfileUpdateRequest(BaseModel):
    # [Logic Hidden]
    """Profile update request with validation - includes all fields needed for plan regeneration"""
def get_current_user_from_token(
    # [Logic Hidden]
    """
    """
        # Node backend signs token as: { user: { id: "..." } }
# Fields that affect workout plans
# Fields that affect nutrition plans
def _normalize_for_compare(value: Any) -> Any:
    # [Logic Hidden]
def _has_value_change(old_value: Any, new_value: Any) -> bool:
    # [Logic Hidden]
def _build_profile_fingerprint(profile: Dict[str, Any]) -> str:
    # [Logic Hidden]
def _build_plan_profile(user_doc: Dict[str, Any], user_id: str) -> Dict[str, Any]:
    # [Logic Hidden]
def _build_user_filter(user_id: str) -> Dict[str, Any]:
    # [Logic Hidden]
def _is_cold_start(user_doc: Dict[str, Any], daily_log_count: int = 0) -> bool:
    # [Logic Hidden]
    """
    """
async def _load_adaptive_modifiers(user_id: str, water_target_ml: int = 2750, sleep_target_hours: float = 8.0) -> Dict[str, Any]:
    # [Logic Hidden]
    """Fetch last 7 daily check-ins and compute adaptive modifiers."""
def _generate_workout_plan(user_profile: Dict[str, Any], request_id: str, adaptive_mods: Dict[str, Any] = None) -> Dict[str, Any]:
    # [Logic Hidden]
        # Build workout_stats enriched with adaptive modifiers so the
        # progression engine can apply sleep/hydration-based adjustments.
def _generate_nutrition_plan(
    # [Logic Hidden]
async def update_profile(
    # [Logic Hidden]
    """
    """
    # Response structure
        # Compute prescription targets (water + sleep) for this user
        # Priority 3: Load adaptive modifiers from last 7 daily check-ins.
        # Done once and passed to both plan generators so they share the same
        # adjustment context for this profile update.
        # Cold-start detection: skip adaptive modifier in Week 1 (per plan Section 11).
        # Cold-start onboarding message (empty string when not applicable)
        # Prescription targets included in every plan response so frontend
        # can display the correct water / sleep goals to the user.
async def get_current_user_profile(
    # [Logic Hidden]
    """Get current user profile"""
        # Remove sensitive data
```

## backend-python\app\routes\workout.py
```python
"""
"""
# Placeholder — actual endpoints registered in server.py until migration complete.
```

## backend-python\app\services\exercise_metadata.py
```python
def normalize_name(name: str) -> str:
    # [Logic Hidden]
    """Normalize exercise names to prevent mismatches from spacing or casing."""
def _load_mapping():
    # [Logic Hidden]
    # Determine config file path relative to this file (app/services/exercise_metadata.py)
    # The config directory is at app/config/
    # Validate mapping entry structure & normalize keys
        # Ensure contract keys are present
# Initialize and validate mapping at module startup
def get_exercise_metadata(name: str) -> dict:
    # [Logic Hidden]
    """Get the full metadata contract dictionary for a given exercise name."""
def get_movement_pattern(name: str) -> str:
    # [Logic Hidden]
    """Get the movement pattern string for a given exercise name."""
def is_trackable(name: str) -> bool:
    # [Logic Hidden]
    """Get the trackability flag for a given exercise name."""
```

## backend-python\app\utils\__init__.py
```python
# Utils package
```

## backend-python\app\utils\activity_logger.py
```python
def _utcnow() -> datetime:
    # [Logic Hidden]
class ActivityType:
    # [Logic Hidden]
    """Activity type constants for consistent logging"""
async def log_user_activity(
    # [Logic Hidden]
    """
    """
        # Bug #67 fixed: guard against invalid ObjectId strings to prevent uncaught bson.errors.InvalidId
        # Add optional fields
        # Don't raise - logging failure shouldn't break the main operation
```

## backend-python\app\utils\db_safe_write.py
```python
def _utcnow() -> datetime:
    # [Logic Hidden]
class SafeWriteResult:
    # [Logic Hidden]
    """Result wrapper for safe database operations"""
    def __init__(self, matched_count: int, modified_count: int, upserted_id=None):
    # [Logic Hidden]
async def safe_update_one(
    # [Logic Hidden]
    """
    """
        # Verify acknowledgment
        # Log results
        # Check if document was found (when not upserting)
async def safe_insert_one(
    # [Logic Hidden]
    """
    """
async def safe_find_one(
    # [Logic Hidden]
    """
    """
def db_operation_handler(max_retries: int = 2, timeout: int = 10):
    # [Logic Hidden]
    """
    """
    def decorator(func):
    # [Logic Hidden]
        async def wrapper(*args, **kwargs):
    # [Logic Hidden]
                    # Add timeout
                    # Don't retry on certain errors
                # Wait before retry (exponential backoff)
            # All retries failed
```

## backend-python\app\utils\model_integrity.py
```python
"""
"""
# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
# Model files that MUST pass integrity checks.
# Filenames are resolved against app/models first, then backend-python/models.
    # Canonical app/models artifacts
    # Decomposition models used in normal production inference paths
    # Legacy encoder / model filenames still referenced by older trainers/loaders
# Optional model artifacts. If missing, app can safely fall back to other models.
class ModelIntegrityError(RuntimeError):
    # [Logic Hidden]
    """Raised when a model file fails its SHA-256 check."""
# ---------------------------------------------------------------------------
# Core helpers
# ---------------------------------------------------------------------------
def _sha256_file(path: Path) -> str:
    # [Logic Hidden]
    """Return the hex SHA-256 digest of *path* (streaming, memory-safe)."""
def _resolve_model_path(filename: str) -> Path:
    # [Logic Hidden]
    """Resolve filename from canonical models dir, then legacy fallback dir."""
def _load_checksums() -> dict[str, str]:
    # [Logic Hidden]
    """Parse ``checksums.sha256`` → ``{filename: expected_hex}``."""
                # Strip leading "./" if present (sha256sum compat)
# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------
def generate_checksums() -> None:
    # [Logic Hidden]
    """
    """
def verify_all_models(strict: bool = True) -> dict[str, str]:
    # [Logic Hidden]
    """
    """
            # No checksum recorded yet — warn but don't fail hard in dev.
    # Optional models are validated when present, but do not fail startup when missing.
def verify_single_model(rel_path: str) -> bool:
    # [Logic Hidden]
    """
    """
```

## backend-python\app\utils\movement_mapper.py
```python
# Centralised registry populated at initialization and pre-populated with core exercises
def get_movement_metadata(name: str, target_muscle: str = "") -> Dict[str, str]:
    # [Logic Hidden]
    """
    """
    # 1. Exact registry lookup
    # 2. Case-insensitive registry lookup
    # 1. Cardio / Full Body
    # 2. Chest (Horizontal Push vs Isolation)
    # 3. Back (Pulls)
            # Default to horizontal pull for back if unsure
    # 4. Shoulders (Vertical Push vs Isolation)
    # 5. Legs (Squat, Hinge, Lunge, Isolation)
    # 6. Arms (Biceps/Triceps/Forearms) -> Mostly Isolation
    # 7. Core (Waist) -> Anti-rotation, flexion, etc.
    # Fallback overrides based purely on name keywords
    # Cache/register it for future exact lookups
```

## backend-python\scratch\check_db.py
```python
# Load env
async def main():
    # [Logic Hidden]
    # Let's check collections
```

## backend-python\scratch\check_logs.py
```python
async def main():
    # [Logic Hidden]
    # Check swap_history collection
        # Check if it belongs to user
```

## backend-python\scratch\check_plan.py
```python
async def main():
    # [Logic Hidden]
```

## backend-python\scratch\check_protein.py
```python
# Add parent directory to path
def run_protein_audit():
    # [Logic Hidden]
    # Initialize engine
    # Calculate expected daily targets
    # Generate fresh plan by using unique user_id and week_start to avoid cache
        # Check validation status
```

## backend-python\scratch\check_timestamps.py
```python
async def main():
    # [Logic Hidden]
```

## backend-python\scratch\debug_portion_run.py
```python
# We can intercept portion_optimizer's optimize_portions or just look at candidate generator output
def new_optimize(components, target_macros):
    # [Logic Hidden]
```

## backend-python\scratch\fix_dataset_values.py
```python
"""
"""
def is_placeholder(row):
    # [Logic Hidden]
    """Detect rows with the placeholder pattern (20 kcal, 1g prot, 3g carbs, 0.5g fat)"""
# Correct nutritional values per 150g serving
# Tuple: (calories, protein_g, carbs_g, fat_g, fiber_g)
def strip_prefix(name):
    # [Logic Hidden]
def main():
    # [Logic Hidden]
    # Build lookup for non-placeholder base foods
        # 1. Apply specific corrections
        # 2. Fix placeholder values
        # 3. Fix zero calorie foods
    # Backup original
```

## backend-python\scratch\generate_and_test_5_plans.py
```python
class LogCaptureHandler(logging.Handler):
    # [Logic Hidden]
    def __init__(self):
    # [Logic Hidden]
    def emit(self, record):
    # [Logic Hidden]
# Adjust path to import app modules
# Configure logging before importing app
def run_tests():
    # [Logic Hidden]
    # Track weekly counts across generated plans
        # Check 6: Any meal where weekly_plan = null or empty
                # Check 1: Rice + Sandwich in the same meal
                # Check 2: Chapati + Pasta in the same meal
                # Track food counts and check calories
                    # Calories
                    # Check 7: Mixed Vegetable Soup showing 449 kcal
                    # Check 8: Chapati showing 505 kcal
                    # Track counts
        # Check 4: Paneer Pea Sandwich appearing more than twice in the week
        # Check 5: Greek Yogurt appearing more than twice in the week
        # Check 3: Same food in breakfast two days in a row
            # Find intersection of foods
            # Remove generic items like beverages (tea, coffee, lemonade, or water)
    # Check Step 4 - Look for specific log entries
```

## backend-python\scratch\inspect_all_days.py
```python
# Ensure backend-python is in sys.path
async def run_test():
    # [Logic Hidden]
    # Check for Rice + Sandwich or Chapati + Pasta
            # Checks
```

## backend-python\scratch\inspect_data.py
```python
def inspect_csv():
    # [Logic Hidden]
def inspect_json():
    # [Logic Hidden]
```

## backend-python\scratch\search_cg.py
```python
# Force stdout to be utf-8 or ascii-safe
```

## backend-python\scratch\test_plan_fixed.py
```python
# Engine returns 'weekly_plan' key (not 'plan')
```

## backend-python\scratch\test_plan_inspector.py
```python
# Ensure backend-python is in sys.path
async def run_test():
    # [Logic Hidden]
```

## backend-python\scratch\test_portion.py
```python
class DebugPortionOptimizer(PortionOptimizer):
    # [Logic Hidden]
    def optimize_portions(self, components, target_macros):
    # [Logic Hidden]
        # Override to print all combinations
```

## backend-python\scratch\test_portion4.py
```python
class DebugOptimizer(PortionOptimizer):
    # [Logic Hidden]
    def optimize_portions(self, components, target_macros):
    # [Logic Hidden]
```

## backend-python\scratch\test_portion6.py
```python
# We will read app/nutrition_engine/portion_optimizer.py and run its exact optimize_portions with print statements
# Instead, let's just trace the real optimize_portions
def trace_calls(frame, event, arg):
    # [Logic Hidden]
            # Check variables
```

## backend-python\scratch\test_portion7.py
```python
def trace_calls(frame, event, arg):
    # [Logic Hidden]
```

## backend-python\scratch\test_portion_opt.py
```python
# Add parent directory to path
# Mocking the state list similar to portion_optimizer.py
# Day 4 lunch items:
# 1. Spicy Tori Sabzi (Priority 3 - Vegetable)
# 2. High Protein Bisi Bele Bath (Brown Rice) (Priority 2 - Carb)
# 3. Poached Egg (Priority 1 - Protein)
# 4. Pineapple Souffle (Priority 4 - Fruit/Dessert/Side)
def get_priority_level(food, unit):
    # [Logic Hidden]
def run_new_optimization():
    # [Logic Hidden]
    # 1. State setup
    # 2. Analytical Scaling with Protein Awareness
    # Categorize items
        # Solve equations:
        # x_p * C_p + x_c * C_c = T_C
        # x_p * P_p + x_c * P_c = T_P
        # If Kramer solved values are out of bounds or negative, fallback to decoupled heuristic
            # x_p matches protein target using Group 1 (protein foods)
            # x_c matches remaining calories using Group 2 (carb/other foods)
        # Clamp multipliers to safe range
        # Apply to items
        # Standard calorie-based scaling
    # 3. Macro-Aware Greedy Fine-Tuning
    # Phase 1: Fine-tune Protein (Group 1)
            # Pick highest protein-to-calorie density
            # Pick lowest protein-to-calorie density to minimize calorie impact
    # Phase 2: Fine-tune Calories (Group 2/3/4)
            # Sort by priority, then least scaled ratio
            # Sort by reverse priority, then most scaled ratio
```

## backend-python\scratch\test_swap.py
```python
async def main():
    # [Logic Hidden]
    # Try swap Day 1 (rest) with next workout (Day 2)
    # Check if they are identical
```

## backend-python\scratch\update_engine.py
```python
# Replace the validation step
        # New Serialized Validation Step
        # 5. Save to Cache if valid
"""
        # Assuming the validator checks the average or takes the dictionary of daily targets.
        # 5. Save to Cache if valid""", new_validation)
```

## backend-python\scratch\update_validator.py
```python
# Add config import
# Add validate_serialized_plan method
    def validate_serialized_plan(self, serialized_plan: Dict[str, Any], daily_targets: Dict[str, float]) -> Dict[str, Any]:
    # [Logic Hidden]
                    # Nutrition
                    # Unit sanity
"""
```

## backend-python\scratch\update_weekly.py
```python
# Add import
# Update attempts
# We'll just leave the meal loop as is for now since it's already doing candidates internally,
# and the "Day" loop retries everything for that day.
# But wait, the user specifically asked for "Hierarchical Retry". Let's add Week-level retry.
# We can wrap the `for day_key` loop in a week_retry loop.
            # 1. Plan Explicit Weekly Targets (cycles calories based on workout intensity)
            # Full week reset for variety tracker
"""
# And close the week_attempts loop
"""
```

## backend-python\scripts\audit_blueprint_metadata.py
```python
"""Read-only audit of meal-blueprint food metadata (Task 7).
"""
# Allow "import app.*" when run from backend-python/
def main() -> int:
    # [Logic Hidden]
    # Non-zero exit if problems found, so CI can flag it. Report-only otherwise.
```

## backend-python\scripts\audit_dataset.py
```python
def main():
    # [Logic Hidden]
    # Report structure
    # 1. Critical: Duplicate IDs
    # 2. Critical: Exact Duplicate Names
    # Process rows
        # Build rough alias map (e.g. Curd Rice / Dahi Rice)
        # Simple alias detection heuristics
        # 3. Critical: Impossible Macros (Deviation > 15%)
        # 4. Warnings: Contradictions
    # Convert alias map to suggestions
    # Write JSON report
    # Write MD report
```

## backend-python\scripts\benchmark_suite.py
```python
def generate_random_profiles(count=100):
    # [Logic Hidden]
def main():
    # [Logic Hidden]
            # Aggregate stats
                        # Portion Realism check (simplistic heuristic for benchmark)
    # Calculate aggregates
## 📊 Core KPIs
## 📉 Failure Analysis
## 🗜️ Constraint Pressure
## 🔄 Recovery
## 📈 Details
"""
```

## backend-python\scripts\benchmark_v7.py
```python
# Ensure project root is in PYTHONPATH
# Setup basic logging
def generate_random_profiles(num_profiles=100) -> list:
    # [Logic Hidden]
        # High protein means 2.2g per kg, standard 1.6g. Say roughly 100-220g.
        # Feasibility Heuristics
def run_benchmark():
    # [Logic Hidden]
    # Get total foods
            # We skip cache for benchmarking by forcing a unique week or user
                # Analyze plan
                        # Derive meal signature for diversity tracking
                    # Calculate daily errors
    # Compile Results
```

## backend-python\scripts\build_knowledge_graph.py
```python
class KnowledgeGraphBuilder:
    # [Logic Hidden]
    def __init__(self, data_path: str, output_path: str):
    # [Logic Hidden]
    def build_graph(self):
    # [Logic Hidden]
        # Build nodes
            # Simulated basic recipe metadata that would be built offline
        # Simulated Compatibility Matrix Builder
        # In a real run, this parses the separate food_metadata.csv or runs LLM rules
                # Find sambar
```

## backend-python\scripts\build_semantic_graph.py
```python
def load_json_if_exists(filepath):
    # [Logic Hidden]
def infer_food_semantics(row):
    # [Logic Hidden]
    # Defaults and confidence
    # 1. Infer Family & Type using multiple signals (name, cat, subcat)
        # Fallback based on macros
    # 2. Infer Plate Role & Meal Role
    # 3. Suitability Scoring
    # Contextual check: e.g. "sandwich" isn't strictly breakfast if it has chicken
    # 4. Servings
    # 5. Metadata
def infer_relationships(food_id, name, semantics):
    # [Logic Hidden]
    # Structured relationship objects
def main():
    # [Logic Hidden]
        # Check idempotency
        # Generate Metadata
        # Tracking metrics for report
        # Generate Relationships
    # Save Outputs
```

## backend-python\scripts\clean_and_expand_dataset.py
```python
# Define the paths
# Unhealthy patterns to remove
# New healthy dataset additions
    # Breakfast
    # Lunch Main
    # Dinner Main
    # Sides (can be attached to lunch/dinner)
    # Snacks
# Ensure we have the same columns as the target dataframe
def process_data():
    # [Logic Hidden]
        # Rename to consistent capitalized columns if they have variants
        # 1. Filter out unhealthy items based on name matching
        # 3. Add new healthy items
        # If dataset has extra columns (like food_category or goal_tag), handle them
                    # Assign food_category based on meal type or name
                    def get_cat(row):
    # [Logic Hidden]
        # Drop duplicates to prevent stacking the 50 healthy items on repeated runs
        # Save to both locations
        # In processed CSV we also save
```

## backend-python\scripts\create_indexes.py
```python
#!/usr/bin/env python3
"""
"""
# Add parent directory to path
async def create_indexes():
    # [Logic Hidden]
    """Create all necessary MongoDB indexes"""
        # Test connection
        # Users collection
        # Weekly workout metadata / swap tracking
        # User daily logs
        # Weight logs
        # Plan regenerations
        # Workout history
        # Meal history
        # Activity logs
        # Swap audit logs
```

## backend-python\scripts\data_validator.py
```python
class DataValidator:
    # [Logic Hidden]
    def __init__(self, df: pd.DataFrame):
    # [Logic Hidden]
    def run_all_checks(self) -> bool:
    # [Logic Hidden]
    def check_duplicates(self):
    # [Logic Hidden]
    def check_negative_values(self):
    # [Logic Hidden]
    def check_missing_macros(self):
    # [Logic Hidden]
        # We allow 0, but not NaN or completely blank if calories > 0
    def check_macro_calorie_balance(self):
    # [Logic Hidden]
        # Calories should roughly equal (protein*4 + carbs*4 + fat*9)
        # We allow a 20% margin of error due to rounding, fiber, etc.
            # Find items with > 25% variance where calories > 10 (ignore very low cal items)
    def check_impossible_portions(self):
    # [Logic Hidden]
        # e.g., protein > serving size
    def check_categorization(self):
    # [Logic Hidden]
```

## backend-python\scripts\dataset_cleanup.py
```python
def clean_dataset():
    # [Logic Hidden]
    # Cleanups
        # 1. Eggitarian fix
        # 2. Vegan fix
        # 3. Russian Salad usage penalty
                # Lower the score across all meals to make it a fallback, not a favorite
        # 4. Murmura (Puffed rice) shouldn't be a primary dinner side.
        # 5. Deviled eggs and heavy eggs shouldn't naturally accompany Pulao as a side.
        # Make paneer pulao highly prioritized for lunch/dinner so it doesn't just randomly appear in odd combos
```

## backend-python\scripts\enrich_food_knowledge_base.py
```python
def enrich_knowledge_base():
    # [Logic Hidden]
    # Track existing high-protein vegan items
        # 1. Add meal_priority if missing, migrate from meal_suitability
        # 2. Add Nutrition Capacity
            # We don't have nutrition facts here because they are in the graph, but we can guess or leave placeholders.
            # Wait, `food_metadata.json` doesn't contain macros. The macro data is in `nutrition_data.json`.
            # Let's just add default schemas for now.
        # 3. Add Nutrition Tags
    # Add new high-protein items if not present
```

## backend-python\scripts\final_dietary_purge.py
```python
def run_purge():
    # [Logic Hidden]
    # We must be careful with 'kheer' to not match 'kheere' (cucumber).
    # We will use word boundaries for short/ambiguous words
    def is_unhealthy(name):
    # [Logic Hidden]
    # Build report
        # find the matched word for the reason
    # Drop rows
```

## backend-python\scripts\fix_allergens.py
```python
# We will read from the V2 file and overwrite it to keep all the 3-tier nutrition updates
def run_allergen_fix():
    # [Logic Hidden]
    # Dictionary of robust keywords for Indian and global foods
    # Exceptions that might match but shouldn't (e.g., coconut is not a tree nut for FDA strictly but sometimes is, water chestnut is not)
    # Actually, we will just use regex word boundaries
        # Match whole words or substrings properly. For instance, 'nut' matches 'nutrela' if we aren't careful, but soy takes precedence.
        # We'll use word boundaries where appropriate or just direct substring if it's safe.
        # Special overrides for "coconut" -> Not a tree nut for our strict definition, unless specifically requested
        # Special overrides: if 'peanut' is found, it's not a 'tree nut', but the word 'nut' might trigger 'tree nut'.
        # If 'nutrela' is found, it has 'nut' but it's soy.
        # Black coffee / Green tea -> no milk!
        # Plain oats are technically GF in some places, but user specifically said "Oats -> Gluten (only if not certified gluten-free)"
        # So we keep Gluten for oats.
        # Vegan foods shouldn't have dairy/egg/meat
            # Sort to make it deterministic
```

## backend-python\scripts\fix_v4.py
```python
def fix_dataset():
    # [Logic Hidden]
    # Load with keep_default_na=False to see exactly what is in the CSV
    # Check calories issue
        # If difference > 25% (or 10%), fix it
    # Remove the duplicate 'calories' column if it exists
    # Check allergens issue
    # We will ensure the string is exactly "None" but to prevent pandas read_csv from reading it as NaN
    # by default, we can just use "None". If user script fails, it's because of pandas.
    # Actually, we can use `"None"` (with quotes) or "None".
    # Let's just explicitly write it.
    # Save it back
```

## backend-python\scripts\generate_evidence_v6.py
```python
def format_plate(meal_name, plate, target_macros):
    # [Logic Hidden]
def main():
    # [Logic Hidden]
        # Display the targets from the engine's internal planner
```

## backend-python\scripts\generate_food_metadata.py
```python
def is_recipe(food_name: str, category: str) -> bool:
    # [Logic Hidden]
    # Categories that are inherently recipes
def generate_food_metadata(csv_path: str, output_dir: str):
    # [Logic Hidden]
        # Base metadata
            # It's a recipe
            # It's a raw ingredient
    # Save the splits
```

## backend-python\scripts\generate_production_dataset.py
```python
def fix_allergens(allergen_str):
    # [Logic Hidden]
def generate_natural_description(name, category, goal, region, p, c, f, is_high_protein):
    # [Logic Hidden]
def get_diet_type(name):
    # [Logic Hidden]
def calculate_macros(protein, carbs, fat):
    # [Logic Hidden]
def get_boolean_flags(name, protein, carbs, fat, fiber, allergens, diet_type):
    # [Logic Hidden]
def estimate_micros(category, serving_size):
    # [Logic Hidden]
def determine_beverage_meal_type(name):
    # [Logic Hidden]
def determine_meal_type(name, cat, cal):
    # [Logic Hidden]
def determine_region(name):
    # [Logic Hidden]
def generate_new_foods():
    # [Logic Hidden]
    # We want ~500 new foods to reach 1500+ total
        # Adjust macros based on variation
        # Occasional flag
def run_pipeline():
    # [Logic Hidden]
    # Apply corrections to existing rows
        # Clean up existing description
        # Ensure exact macro consistency just in case
    # Generate 500+ new rows
    # Combine and deduplicate
    # Save
```

## backend-python\scripts\generate_v3_dataset.py
```python
def rewrite_description(row):
    # [Logic Hidden]
    # Building features
    # Special for beverages
def run_audit():
    # [Logic Hidden]
        # 1. Light Beverage Macro Override
        # 2. Strict Calorie Enforcement
        # 3. Dietary Flag & Allergen Deep Audit
        # Rebuild allergens list
        # 4. Meal Type Fixes
        # 5. Goal Mapping
        # 6. Rewrite Description
```

## backend-python\scripts\ifct_validation_pipeline.py
```python
def clean_name(name):
    # [Logic Hidden]
def run_pipeline():
    # [Logic Hidden]
    # Prepare IFCT mapping
        # 1. Fuzzy Match
            # Helper to safely parse IFCT float
            def sf(val):
    # [Logic Hidden]
            # Map values
            # enerc is kJ. 1 kcal = 4.184 kJ
            # Vitamin A = Retinol + BetaCarotene/6
            # For unmatched, we keep current but ensure macro math is strictly correct
        # 3. Boolean and Allergen verification (Deep Audit)
        # Check Meal Type
```

## backend-python\scripts\multi_reference_pipeline.py
```python
def clean_name(name):
    # [Logic Hidden]
def run_pipeline():
    # [Logic Hidden]
    # Clean up IFCT
    # Clean up Nut CSV
    def sf(val):
    # [Logic Hidden]
    # Iterate production dataset
        # ----------------------------------------------------
        # PRIORITY 1: IFCT 2017
        # ----------------------------------------------------
        # ----------------------------------------------------
        # PRIORITY 2: NUTRITION.CSV
        # ----------------------------------------------------
        # ----------------------------------------------------
        # PRIORITY 3: FALLBACK
        # ----------------------------------------------------
        # ----------------------------------------------------
        # BOOLEAN & ALLERGEN VALIDATION
        # ----------------------------------------------------
        # Vegan / Vegetarian Logic
        # Build Allergens perfectly
```

## backend-python\scripts\preprocess_food_metadata.py
```python
"""
"""
# ── Path configuration ──────────────────────────────────────────────────────
# ── Classification Maps ──────────────────────────────────────────────────────
# Each entry is (keyword, family). First match wins.
# Entries are ordered specific → generic to avoid early generic matches.
# Human curators can override any entry directly in the JSON files.
    # Specific rice dishes (must come before generic "rice")
    # Flatbreads
    # South Indian
    # Lentils
    # Grilled / Baked / Roasted
    # Kebabs & Tandoor
    # Curried dishes
    # Dry / stir-fried veg
    # Sides / condiments
    # Beverages
    # Breakfast
    # Snacks / munchies
    # Desserts
    # Eggs
    # Spice blends / condiments (classify last to avoid false matches)
    # Non-veg proteins (specific compounds first)
    # Veg proteins
    # Grains / carb primaries
    # Dairy
def classify(food_name: str) -> dict:
    # [Logic Hidden]
    """
    """
def enrich_database(db_path: pathlib.Path, dry_run: bool = False) -> dict:
    # [Logic Hidden]
    """
    """
        # dish_family — only set if missing or "other"
        # primary_ingredient — only set if missing or "other"
def print_report(db_name: str, stats: dict):
    # [Logic Hidden]
def main():
    # [Logic Hidden]
```

## backend-python\scripts\purge_unhealthy_foods.py
```python
def is_unhealthy(name):
    # [Logic Hidden]
    # 1. Desserts, Sweets, High Sugar
    # 2. Deep Fried / Greasy / High Glycemic
    # 3. Processed Fast Food
    # 4. Ultra-Rich / Heavy Cream Curries
    # Check if name contains any unhealthy keywords
            # Handle some exceptions like "sweet potato" which is healthy
    # Explicit full string matches for specific bad items observed
def run_purge():
    # [Logic Hidden]
    # 1. Purge Unhealthy Foods
    # Keep track of what we delete for the report
    # Filter the dataset
    # 2. Fix Meal Timings (Move heavy proteins to Lunch/Dinner)
        # Heavy curries or meat shouldn't be breakfast
```

## backend-python\scripts\qa_plan_dumper.py
```python
def generate_random_profile(i):
    # [Logic Hidden]
def run_qa():
    # [Logic Hidden]
                # State tracking for variety
                # Ensure we only keep unique flags
```

## backend-python\scripts\red_team_audit.py
```python
def run_audit():
    # [Logic Hidden]
    # 1 & 2. Diet & Suitability
        # Check Vegetarian for eggs/meat
            # Exclude paneer tikka etc
        # Check Vegan for dairy/honey/meat
        # Meal Suitability
        def get_score(m):
    # [Logic Hidden]
        # Portion Realism
    # Template Feasibility
                # Check if template has anchor
                # If template allows > 80g protein but only requires low protein roles
```

## backend-python\scripts\seed.py
```python
#!/usr/bin/env python3
"""
"""
# Load .env from backend-python/
# ---------------------------------------------------------------------------
# Connect
# ---------------------------------------------------------------------------
# ---------------------------------------------------------------------------
# Clean previous seed data
# ---------------------------------------------------------------------------
# ---------------------------------------------------------------------------
# Sample nutrition plans
# ---------------------------------------------------------------------------
# ---------------------------------------------------------------------------
# Sample workout plans
# ---------------------------------------------------------------------------
# ---------------------------------------------------------------------------
# Insert
# ---------------------------------------------------------------------------
```

## backend-python\scripts\test_weekly_plan_comprehensive.py
```python
def test_profiles():
    # [Logic Hidden]
                    # Track for duplicates
```

## backend-python\scripts\ultimate_validation_pipeline.py
```python
def run_ultimate_validation():
    # [Logic Hidden]
    # Trackers for the final report
    # ---------------------------------------------------------
    # STEP 12: DUPLICATES & STEP 13: KEEP HEALTHY
    # ---------------------------------------------------------
    # Drop exact string duplicates
    # Drop "Diet", "Healthy", "Premium" versions if they exist
    # (Just regex drop since user asked to drop premium/diet variants)
    # Wait, the previous script purged most "Diet" and "Healthy" desserts.
    # Let's keep it simple: drop specific adjectives from start of string to see if base exists?
    # Or just keep it as is since we did an exhaustive purge already.
    # We will just drop exact case-insensitive duplicates.
    # ---------------------------------------------------------
    # STEP 2 & 3: DATA CORRUPTION & CALORIE CONSISTENCY
    # ---------------------------------------------------------
    def fix_corruption(row):
    # [Logic Hidden]
        # Prevent P+C+F > Serving
        # Negative micros
        # Calorie Consistency
    # ---------------------------------------------------------
    # STEP 4 & 5: IFCT VALIDATION (BEST EFFORT MATCH)
    # ---------------------------------------------------------
    def sf(val):
    # [Logic Hidden]
    def apply_ifct(row):
    # [Logic Hidden]
            # Map IFCT macros if available
    # ---------------------------------------------------------
    # STEP 6: ALLERGENS
    # ---------------------------------------------------------
    def recalculate_allergens(row):
    # [Logic Hidden]
    # ---------------------------------------------------------
    # STEP 7: DIETARY FLAGS
    # ---------------------------------------------------------
    def validate_flags(row):
    # [Logic Hidden]
        # Hard rules
        # STEP 8: GI REVIEW
        # STEP 9: GOAL VALIDATION
        # Rule: Weight loss = protein > 10 OR (fiber > 3 and cals < 300)
    # Save the file
    # Generate Report
```

## backend-python\scripts\validate_and_fix_v3.py
```python
def run_validation():
    # [Logic Hidden]
    # Validation Rules
        # 1. Macro validation
        # 2. Micronutrient limits (Cap extreme generated values)
        # 3. Boolean and Allergen verification
        # High Protein / Low Carb flags
        # Build Allergens perfectly
        # 4. Meal Type and Goal verification
        # Ensures no blank meal types
        # 5. Cooking Method & Region verification
```

## backend-python\scripts\validate_dataset.py
```python
def validate_dataset(csv_path: str) -> bool:
    # [Logic Hidden]
    # 1. Duplicate IDs
    # 2. Duplicate Names
    # 3. Impossible Macros
    # 1g Protein = 4 kcal, 1g Carb = 4 kcal, 1g Fat = 9 kcal
    # Give a 20% tolerance due to fiber and rounding
        # In a real strict environment, we'd fail here. We will just log warnings for now if we don't want to crash immediately on edge cases,
        # but the spec says "fail to start".
    # 4. Missing Portions
    # 5. Missing Semantics
```

## backend-python\tests\run_regression.py
```python
# Ensure the backend is in path
def run_regression():
    # [Logic Hidden]
            # We instantiate per-profile to reset variety tracker state cleanly
            # Using generate_plan from engine
            # Validation: Macros within tolerance
            # Just some basic macro checks on the generated stats vs target
```

## backend-python\tests\test_candidate_generator.py
```python
class TestCandidateGenerator(unittest.TestCase):
    # [Logic Hidden]
    def setUp(self):
    # [Logic Hidden]
    def test_generate_lunch_candidates(self):
    # [Logic Hidden]
        # Generate 3 candidates for a Vegetarian diet
    def test_forbidden_roles_not_included(self):
    # [Logic Hidden]
```

## backend-python\tests\test_candidate_health.py
```python
"""
"""
# Path is relative to the project root (backend-python/).
def _load_metrics() -> list:
    # [Logic Hidden]
def test_lunch_acceptance_rate():
    # [Logic Hidden]
def test_fallback_usage_rate():
    # [Logic Hidden]
def test_generation_time():
    # [Logic Hidden]
def test_metrics_file_has_recent_records():
    # [Logic Hidden]
def test_all_meal_types_represented():
    # [Logic Hidden]
```

## backend-python\tests\test_chatbot_refactored.py
```python
def client():
    # [Logic Hidden]
    """Import server and create a TestClient with MongoDB patched out."""
        # Use environment variables set for testing
class TestChatbotDefensiveHelpers:
    # [Logic Hidden]
    def test_extract_message_text(self):
    # [Logic Hidden]
    def test_map_role(self):
    # [Logic Hidden]
class TestChatbotEndpoints:
    # [Logic Hidden]
    def test_consent_sanitization(self, client):
    # [Logic Hidden]
            # Clear rate limit dict for test reliability
            # Check profile passed to get_chatbot_response
    def test_consent_preservation(self, client):
    # [Logic Hidden]
            # Clear rate limit dict for test reliability
    def test_circuit_breaker_offline_fallback(self, client):
    # [Logic Hidden]
            # Clear rate limit dict for test reliability
    def test_fallback_reply_offline_mode_flag(self, client):
    # [Logic Hidden]
            # Clear rate limit dict for test reliability
    def test_rate_limiting(self, client):
    # [Logic Hidden]
            # First request passes
            # Second request immediately after is limited
```

## backend-python\tests\test_chatbot_sanity_flow.py
```python
def client():
    # [Logic Hidden]
    """Import server and create a TestClient with MongoDB patched out."""
        # Simple mock for mongo db client
        # Ensure rate limit cooldown is disabled for tests
def test_chatbot_sanity_flow(client):
    # [Logic Hidden]
    """
    """
    # 5 follow-up questions representing a conversation flow
    # Run test WITH health-consent enabled
        # Append user message and model response to history
    # Verify model remembers context in the last response (should mention muscle, beginner, or no equipment)
    # Check if the AI's summary contains key terms from previous turns
    # At least some of the topics should be mentioned
    # Run test WITHOUT health-consent enabled
```

## backend-python\tests\test_engine.py
```python
class TestNutritionEngine(unittest.TestCase):
    # [Logic Hidden]
    def setUp(self):
    # [Logic Hidden]
    def test_end_to_end_generation(self):
    # [Logic Hidden]
        # Verify the plates are not empty if there were matches
    def test_validation_failure_graceful(self):
    # [Logic Hidden]
    def test_generation_uncaught_exception_graceful(self):
    # [Logic Hidden]
```

## backend-python\tests\test_golden_profiles.py
```python
class TestGoldenProfiles(unittest.TestCase):
    # [Logic Hidden]
    def setUp(self):
    # [Logic Hidden]
    def _run_profile(self, user_profile):
    # [Logic Hidden]
    def test_golden_senior_maintenance(self):
    # [Logic Hidden]
    def test_golden_vegan_muscle_gain(self):
    # [Logic Hidden]
    def test_golden_pcos_weight_loss(self):
    # [Logic Hidden]
    def _assert_plan_quality(self, plan):
    # [Logic Hidden]
        # Weekly asserts
                # We need to verify capacity limits, realism score etc once implemented.
                    # Assert no repeated consecutive breakfast if possible, or just gather them
                # Assert completeness > 85%
                # Assert portion limits
                    # Placeholder until actual checks
```

## backend-python\tests\test_health_endpoint.py
```python
"""
"""
def client():
    # [Logic Hidden]
    """Import server and create a TestClient with MongoDB patched out."""
    # Patch motor AsyncIOMotorClient before server imports it
        # Prevent re-use of a cached module with a real DB connection
class TestHealthEndpoint:
    # [Logic Hidden]
    def test_health_returns_200(self, client):
    # [Logic Hidden]
        # Accept 200 OK
    def test_health_returns_json_with_status(self, client):
    # [Logic Hidden]
            # Server health check should have some status field
```

## backend-python\tests\test_meal_scorer.py
```python
class MockVarietyTracker:
    # [Logic Hidden]
    def __init__(self):
    # [Logic Hidden]
    def calculate_variety_penalty(self, food_id, family, current_day):
    # [Logic Hidden]
class TestMealScorer(unittest.TestCase):
    # [Logic Hidden]
    def setUp(self):
    # [Logic Hidden]
    def test_score_candidate_plate(self):
    # [Logic Hidden]
    def test_penalize_weird_combinations(self):
    # [Logic Hidden]
```

## backend-python\tests\test_metadata_serialization.py
```python
class TestMetadataSerialization(unittest.TestCase):
    # [Logic Hidden]
    def setUpClass(cls):
    # [Logic Hidden]
    def test_classify_exercise_mode_contains_pattern(self):
    # [Logic Hidden]
        """Test that _classify_exercise_mode includes movement_pattern and preserves legacy keys."""
                # Check that movement_pattern is correct
                # Check that existing keys are preserved
                # Check types
    def test_warmups_contain_movement_pattern(self):
    # [Logic Hidden]
        """Test that generated warmup exercises contain movement_pattern."""
    def test_fallback_exercises_contain_movement_pattern(self):
    # [Logic Hidden]
        """Test that fallback exercises contain movement_pattern."""
            # Verify specific fallbacks from _get_fallback_exercises code
    def test_workout_generation_contains_movement_pattern(self):
    # [Logic Hidden]
        """Test that generated workout exercises contain movement_pattern."""
```

## backend-python\tests\test_nutrition_engine_comprehensive.py
```python
def engine():
    # [Logic Hidden]
def test_nutrition_targets_weight_loss(engine):
    # [Logic Hidden]
    # BMR = 10*80 + 6.25*170 - 5*30 + 5 = 800 + 1062.5 - 150 + 5 = 1717.5
    # TDEE = 1717.5 * 1.375 = 2361.56
    # Weight Loss Goal Mult = 0.85
    # Kcal = 2361.56 * 0.85 = 2007.3
def test_nutrition_targets_maintenance(engine):
    # [Logic Hidden]
    # BMR = 10*70 + 6.25*175 - 5*30 + 5 = 700 + 1093.75 - 150 + 5 = 1648.75
    # TDEE = 1648.75 * 1.55 = 2555.56
    # Maintenance Goal Mult = 1.00
    # Kcal = 2555.56
def test_nutrition_targets_muscle_gain(engine):
    # [Logic Hidden]
    # BMR = 10*60 + 6.25*160 - 5*30 + 5 = 600 + 1000 - 150 + 5 = 1455
    # TDEE = 1455 * 1.725 = 2509.875
    # Muscle Gain Goal Mult = 1.10
    # Kcal = 2509.875 * 1.10 = 2760.86
def test_diet_and_allergies(engine):
    # [Logic Hidden]
def test_meal_quality_and_duplicates(engine):
    # [Logic Hidden]
        # Completeness Check
        # Track duplicates
        # Realistic portions
def test_performance(engine):
    # [Logic Hidden]
```

## backend-python\tests\test_portion_optimizer.py
```python
# Add backend-python to path
def test_portion_optimizer_basic():
    # [Logic Hidden]
    # Assert macros are optimized reasonably close to target
    # Assert portion limits are respected
def test_portion_optimizer_salad_cap():
    # [Logic Hidden]
    # Raita is capped at 100 calories or 1.5 bowls by portion optimizer rules
```

## backend-python\tests\test_pose_tracker_refactored.py
```python
# Create a mock landmark class for testing
class MockLandmark:
    # [Logic Hidden]
    def __init__(self, x, y, visibility=0.9):
    # [Logic Hidden]
def make_mock_landmarks():
    # [Logic Hidden]
    # Return 33 landmarks mapping to MediaPipe points
def reset_factory():
    # [Logic Hidden]
    """Reset DetectorFactory state before each test to avoid stale caches."""
# ---- DetectorFactory selection tests ----
def test_detector_factory_exact_match():
    # [Logic Hidden]
    """Verify factory returns SquatDetector for an exercise that exists in the mapping."""
    # "Barbell Full Squat" is an actual entry in exercise_mapping.json
def test_detector_factory_keyword_fallback():
    # [Logic Hidden]
    """Verify factory uses keyword fallback for exercises NOT in the mapping."""
    # "Barbell Squat" is not in the mapping, but keyword "squat" should match
    # "Dumbbell Bicep Curl" is not in the mapping, but keyword "curl"/"bicep" should match
def test_detector_factory_unknown_fallback():
    # [Logic Hidden]
    """Verify fallback to GenericDetector for completely unknown exercise."""
def test_detector_factory_case_insensitive():
    # [Logic Hidden]
    """Verify case-insensitive lookup works for exercises in the mapping."""
    # "barbell full squat" (lowercase) should still match "Barbell Full Squat"
# ---- Confidence tests ----
def test_confidence_filtering():
    # [Logic Hidden]
    # All visible
    # Low visibility
# ---- Rep counting tests ----
def test_squat_rep_counting():
    # [Logic Hidden]
    # Mock landmarks for up position (knee angle near 180)
    # Deep squat (knee angle < 90)
    # Rise back up
# ---- PoseTracker integration tests ----
def test_untrackable_exercise():
    # [Logic Hidden]
    # "Alternate Lateral Pulldown" is in the mapping with trackable: false
def test_api_compatibility():
    # [Logic Hidden]
def test_exercise_switching():
    # [Logic Hidden]
def test_confidence_smoothing_and_form_score(monkeypatch):
    # [Logic Hidden]
    class MockPoseLandmarks:
    # [Logic Hidden]
        def __init__(self, landmarks):
    # [Logic Hidden]
    class MockResults:
    # [Logic Hidden]
        def __init__(self, landmarks):
    # [Logic Hidden]
    # Frame 1
    # Fast forward to trigger form score storage (every 30 frames)
def test_form_score_storage_limit():
    # [Logic Hidden]
    # add_form_accuracy_score limits to 20 scores
def test_tracking_statistics():
    # [Logic Hidden]
```

## backend-python\tests\test_profile_meal_regen.py
```python
# Ensure backend-python is in sys.path
def client():
    # [Logic Hidden]
        # Override dependency
        # Clean up
def test_profile_update_nutrition_regeneration(client):
    # [Logic Hidden]
    # Mock database functions and safe_find_one/safe_update_one
    # Safe update mock result
    # Mock meal engine generation
    # Apply patches
         # Mock insert_one on weekly_plans collection
         # Headers with auth token
         # Update dietary_preference to trigger nutrition regeneration
         # Verify responses
```

## backend-python\tests\test_python_api_contract.py
```python
class PythonApiContractTests(unittest.TestCase):
    # [Logic Hidden]
    def setUpClass(cls):
    # [Logic Hidden]
    def test_server_exposes_required_workout_endpoints(self):
    # [Logic Hidden]
    def test_profile_router_exposes_update_endpoint(self):
    # [Logic Hidden]
```

## backend-python\tests\test_template_manager.py
```python
class TestMealTemplates(unittest.TestCase):
    # [Logic Hidden]
    def setUp(self):
    # [Logic Hidden]
        # We assume tests are run from the backend-python root
    def test_file_exists(self):
    # [Logic Hidden]
    def test_templates_load(self):
    # [Logic Hidden]
        # Test fallback
    def test_template_schema(self):
    # [Logic Hidden]
    def test_sorting_by_priority(self):
    # [Logic Hidden]
```

## backend-python\tests\test_token_utils.py
```python
"""
"""
# ── test constants ────────────────────────────────────────────────────────────
def create_token(payload: dict, secret: str = SECRET, expires_in: int = 3600) -> str:
    # [Logic Hidden]
    """Helper: build a JWT the same way server.py does."""
def decode_token(token: str, secret: str = SECRET) -> dict:
    # [Logic Hidden]
    """Helper: decode and verify a JWT."""
# ── tests ─────────────────────────────────────────────────────────────────────
class TestTokenRoundTrip:
    # [Logic Hidden]
    def test_valid_token_decodes_correctly(self):
    # [Logic Hidden]
    def test_expired_token_raises(self):
    # [Logic Hidden]
    def test_wrong_secret_raises(self):
    # [Logic Hidden]
    def test_malformed_token_raises(self):
    # [Logic Hidden]
    def test_missing_exp_claim_still_decodes(self):
    # [Logic Hidden]
        """Tokens without exp should decode — server.py sets options explicitly."""
class TestSuspensionClaim:
    # [Logic Hidden]
    """Verifies that isSuspended can be read from the token payload."""
    def test_is_suspended_false_by_default(self):
    # [Logic Hidden]
    def test_suspended_user_flag_preserved(self):
    # [Logic Hidden]
    def test_missing_suspension_claim_returns_none(self):
    # [Logic Hidden]
```

## backend-python\tests\test_variety_tracker.py
```python
def test_variety_tracker_basic():
    # [Logic Hidden]
    # Verify initial empty histories
    # Record some meals
    # Check that tracking works
    # Calculate penalty for repeating cuisine
    # Note: calculate_variety_penalty penalizes recent items in item_history and family_history
    # Eaten 1 day ago (2 - 1 = 1 < 3), penalty should be >= 50
def test_variety_tracker_snapshot():
    # [Logic Hidden]
    # Record a meal on day 1
    # Take a snapshot
    # Record another meal
    # Restore the snapshot
    # Check that fish is removed but chicken remains
```

## backend-python\tests\test_workout_e2e_flow.py
```python
# --- Mock Datetime ---
class FrozenDatetime(datetime.datetime):
    # [Logic Hidden]
    def utcnow(cls):
    # [Logic Hidden]
    def now(cls, tz=None):
    # [Logic Hidden]
# --- Mock Database Adapters ---
class MockMongoCollection:
    # [Logic Hidden]
    def __init__(self, db_store, name):
    # [Logic Hidden]
    async def find_one(self, query, projection=None):
    # [Logic Hidden]
    async def update_one(self, query, update_dict, upsert=False):
    # [Logic Hidden]
        # Apply $set operator
class MockDatabase:
    # [Logic Hidden]
    def __init__(self, db_store):
    # [Logic Hidden]
# --- Test Fixtures ---
def setup_e2e_mocks(monkeypatch):
    # [Logic Hidden]
    # Lock time inputs to be deterministic
    # Mock Gemini AI calls
    # Disable network threads and requests
# ==============================================================================
# 1. End-To-End Lifecycle Validation with Debug Trace Checks
# ==============================================================================
def test_profile_update_to_persisted_fetch_e2e_flow(monkeypatch):
    # [Logic Hidden]
    """
    """
    # Intercept Database requests
    # Mock Auth layer to decode user_id directly from header token
    # Update to 4 days, Female adjustments (reps shift +2, rest -15%)
    # --- PUT Profile Update ---
    # --- DB Verification ---
    # Verify debug_trace exists in persisted DB plan
    # --- GET Fetched Plan Parity & Parity Checks ---
    # Verify frontend-received payload has debug traces
# ==============================================================================
# 2. Concurrency & Race-Condition Validation
# ==============================================================================
def test_concurrent_profile_updates_no_state_leakage(monkeypatch):
    # [Logic Hidden]
    """
    """
    # Create two users with distinct targets
    # Run updates in parallel threads
    def call_update(user_id, payload):
    # [Logic Hidden]
    # Both must succeed
    # Verify User A did not get overwritten or corrupted by User B
    # Verify User B did not get corrupted by User A
# ==============================================================================
# 3. Real MongoDB Integration Test (Conditional on connection)
# ==============================================================================
async def test_real_mongodb_connection_persistence_if_available():
    # [Logic Hidden]
    """
    """
        # Create real Async Motor Client
    # Database instance setup
    # 1. Setup clean record
        # 2. Simulate plan generation
        # 3. Direct real write to Mongo
        # 4. Direct real read from Mongo
        # Verify the structure inside real Mongo
        # Clean up database
```

## backend-python\tests\test_workout_planner_comprehensive.py
```python
# --- Freeze Datetime Mock ---
class FrozenDatetime(datetime.datetime):
    # [Logic Hidden]
    def utcnow(cls):
    # [Logic Hidden]
    def now(cls, tz=None):
    # [Logic Hidden]
def freeze_determinism(monkeypatch):
    # [Logic Hidden]
    # Freeze time in workout engine to ensure reproducible week/day matching
    # Mock Gemini to be unavailable so we don't trigger real network calls / quota blocks
    # Mock background WGER loader to prevent starting slow threads that make network calls
    # Mock synchronous WGER media index load to prevent slow API requests
    # Mock network reachability check to prevent slow network request timeouts during tests
    # Seed the system random generator
# ==============================================================================
# 1. Determinism and Stability Test
# ==============================================================================
def test_determinism_under_fixed_profile():
    # [Logic Hidden]
    """Verify that calling generate_weekly_plan twice returns identical plans."""
    # Convert to JSON to verify deep equality
# ==============================================================================
# 2. Age-Based Safety Clamps
# ==============================================================================
def test_senior_age_safety_filters():
    # [Logic Hidden]
    """Verify that seniors (>65 years) do not receive high-impact exercises."""
# ==============================================================================
# 3. Frequency Gates
# ==============================================================================
def test_frequency_gating_beginner():
    # [Logic Hidden]
    """Verify that beginner training days are capped to 3 unless streak/consistency triggers unlocked."""
    # 1. Base beginner (should be capped at 3 days even though requesting 4)
    # 2. Progression beginner (streak >= 21 and consistency >= 0.85 unlocks 4 days)
def test_frequency_gating_intermediate():
    # [Logic Hidden]
    """Verify that intermediate training days are capped to 4 unless unlocked to 5."""
    # 1. Base intermediate (capped at 4 days even though requesting 5)
    # 2. Progression intermediate (streak >= 42 and consistency >= 0.90 unlocks 5 days)
def test_frequency_gating_advanced():
    # [Logic Hidden]
    """Verify that advanced training days are capped to 5 unless unlocked to 6."""
    # 1. Base advanced (capped at 5 days even though requesting 6)
    # 2. Progression advanced (streak >= 10 and consistency >= 0.80 unlocks 6 days)
# ==============================================================================
# 4. Gender-Based Parameter Adjustments
# ==============================================================================
def test_gender_parameter_adjustments_female():
    # [Logic Hidden]
    """Verify female parameter shifts: hypertrophy reps shift (+2), shorter rest (-15%), beginner sets reduction."""
    # 1. Hypertrophy Rep range shift & rest reduction
                    # Intermediate Female hypertrophic reps should be shifted (+2) from 8-12 to 10-14
                    # Base hypertrophy rest is 60-90s. 60s * 0.85 = 51s rest string "51 seconds".
    # 2. Beginner sets reduction
                    # Standard beginner is 3 sets, female beginner gets reduced to 2 sets
# ==============================================================================
# 5. Priority Conflict Resolution
# ==============================================================================
def test_injury_override_trumps_hypertrophy_goal():
    # [Logic Hidden]
    """Verify that injury exclusion filters trump goal-based muscle selections (e.g. knee injury excludes leg day loading)."""
    # Find knee-restricted exercises in database
def test_safety_clamp_overrides_frequency_boost():
    # [Logic Hidden]
    """Verify that beginner safety clamps override streak-based frequency overrides."""
    # Even with high streak/consistency, a beginner is clamped at max 4 workout days
# ==============================================================================
# 6. Weekly Schedule Structure & deduplication
# ==============================================================================
def test_weekly_schedule_structure_and_no_consecutive_exercises():
    # [Logic Hidden]
    """Verify restReason generation, warmup separation, and that exercises do not repeat across the week."""
        # 1. Structure checks
            # Check restReason is present and populated
            # Check warmups are separated
            # Check exercises list has only main exercises (no warmup drill in 'exercises')
                # Check cross-day exercise deduplication
# ==============================================================================
# 7. Regression Lock Snapshot Test
# ==============================================================================
def test_regression_lock_snapshot():
    # [Logic Hidden]
    """Lock in plan generation results via stable cryptographic hash check of output names."""
    # Extract only day names and sorted lists of exercise names
    # Expected MD5 snapshot hash for intermediate, 4-day male hypertrophy, dumbbell-only plan
# ==============================================================================
# 8. API Response Contract Parity Test
# ==============================================================================
def test_api_contract_response_parity(monkeypatch):
    # [Logic Hidden]
    """Verify the FastAPI server response schema matches the expected shape and keys."""
    # Mock authentication to allow test running offline without MongoDB
    # Mock find_user_workouts to return None (no prior workouts)
    # Request workout generation
    # Verify workout day structures
            # Ensure no warmups are leaked into the exercises list in API output
```

## backend-python\tests\test_workout_progression_regression.py
```python
# 1. Movement Mapping Test
def test_movement_mapping():
    # [Logic Hidden]
    """Verify that Push-Up variations resolve correctly to horizontal_push."""
# 2. Equipment Constraint Test
def test_equipment_constraint():
    # [Logic Hidden]
    """Verify that if available equipment is empty, dumbbell-only exercises are not returned."""
    # Generate exercises with no equipment
    # Verify no selected exercise requires dumbbells
# 3. Injury Constraint Test
def test_injury_constraint():
    # [Logic Hidden]
    """Verify that exercises flagged as avoid are filtered out for specific injuries."""
    # Identify which exercises in the CSV are restricted for "shoulder" issues
    # We should have some restricted shoulder exercises
    # Generate exercises with 'shoulder' issue
    # Verify none of the returned exercises are shoulder-restricted
# 4. History Truncation Test
async def test_history_truncation(monkeypatch):
    # [Logic Hidden]
    """Verify that _find_user_workouts_by_id respects MongoDB $slice to only load the last 50 entries."""
    # Mock the database client and find_one method
    # Patch the database connection
    # Call the database helper with limit=50
    # Assert find_one was called with the correct projection containing $slice of -50
# 5. Home Workout Only & Warm-up Separation Test
def test_home_workout_only_and_warmup_separation():
    # [Logic Hidden]
    """Verify that only home equipment exercises are loaded, and that weekly plans separate warm-ups from main exercises."""
    # 1. Verify only home equipment exercises are in the database
    # 2. Generate weekly plan and verify separate warm-up count
            # Check warmups are populated
            # Check exercises list has only main exercises (no warmup exercises should be in 'exercises' list)
            # Check that exercises_total is correct and only counts main exercises
```

## backend-python\tests\verify_v6_stabilization.py
```python
# Ensure backend-python is in sys.path
class TestV6Stabilization(unittest.TestCase):
    # [Logic Hidden]
    def setUp(self):
    # [Logic Hidden]
        # Force fresh initialization
        # Setup log capture on root logger to capture all output
    def tearDown(self):
    # [Logic Hidden]
    def test_v6_stabilization_assertions(self):
    # [Logic Hidden]
        # Helper classification functions prioritizing metadata
        def check_rice(item):
    # [Logic Hidden]
        def check_sandwich(item):
    # [Logic Hidden]
        def check_pasta(item):
    # [Logic Hidden]
        def check_chapati(item):
    # [Logic Hidden]
        # Generate 5 weekly plans and run assertions
            # Use unique week_start and user_id to bypass caching
            # Assert 1: Generate 5 weekly plans and verify none have weekly_plan = null
            # Assertions for each plan
                    # Assert 2: verify no meal contains Rice + Sandwich combination
                    # Assert 3: verify no meal contains Chapati + Pasta combination
                    # Assert 4: verify no breakfast repeats the same breakfast_category on consecutive days
                    # Accumulate food counts for weekly limit check
            # Assert 5: verify the same food_id does not appear more than food_repeat_limit times across the week
            # Note: We exempt common side items like raitas/salads/condiments/fruits/beverages from strict limits.
            # Only main carb/protein items are checked.
                # Find matching food node
                    # Skip common sides/drinks/condiments/snacks
        # Assert 6: Verify COMPATIBILITY_REJECTION if present (optional on clean runs with high acceptance rates)
        # Assert 7: Verify WEEKLY_SUMMARY appears in logs after each generation
```

## frontend\fix_macros.py
```python
# Add getMealHistory to api imports
'''
```

## frontend\refactor.py
```python
"""
# Find all occurrences of waterGoal calculations and replace them
```

## frontend\vite.config.js
```javascript
      // All /api traffic (including /api/python) goes through Node so auth + CSRF apply.
  // BUG-C2: Vitest configuration
        functions: 60,
  // [Logic Hidden]
```

## frontend\public\sw.js
```javascript
const staleWhileRevalidate = async (request, cacheName) => {
  // [Logic Hidden]
    .then((response) => {
  // [Logic Hidden]
    .catch(() => null);
  // [Logic Hidden]
self.addEventListener('install', (event) => {
  // [Logic Hidden]
    caches.open(STATIC_CACHE).then((cache) => cache.addAll(STATIC_ASSETS)).catch(() => undefined)
  // [Logic Hidden]
self.addEventListener('activate', (event) => {
  // [Logic Hidden]
    caches.keys().then((keys) =>
  // [Logic Hidden]
          .filter((key) => ![STATIC_CACHE, RUNTIME_CACHE].includes(key))
  // [Logic Hidden]
          .map((key) => caches.delete(key))
  // [Logic Hidden]
self.addEventListener('fetch', (event) => {
  // [Logic Hidden]
  // SEC-20: do not cache third-party resources in service worker.
  // This avoids indefinite caching of remote assets without integrity validation.
```

## frontend\src\App.jsx
```javascript
const Login     = lazy(() => import('./pages/Login'));
  // [Logic Hidden]
const Register  = lazy(() => import('./pages/Register'));
  // [Logic Hidden]
const Dashboard = lazy(() => import('./pages/Dashboard'));
  // [Logic Hidden]
const ProfileSetup = lazy(() => import('./pages/ProfileSetup'));
  // [Logic Hidden]
const Workout   = lazy(() => import('./pages/Workout'));
  // [Logic Hidden]
const Nutrition = lazy(() => import('./pages/Nutrition'));
  // [Logic Hidden]
const Chatbot   = lazy(() => import('./pages/Chatbot'));
  // [Logic Hidden]
const DashboardActionIdeas = lazy(() => import('./pages/DashboardActionIdeas'));
  // [Logic Hidden]
const ForgotPassword = lazy(() => import('./pages/ForgotPassword'));
  // [Logic Hidden]
const AdminLogin = lazy(() => import('./pages/admin/AdminLogin'));
  // [Logic Hidden]
const AdminRoute = lazy(() => import('./components/admin/AdminRoute'));
  // [Logic Hidden]
const AdminLayout = lazy(() => import('./components/admin/AdminLayout'));
  // [Logic Hidden]
const AdminDashboard = lazy(() => import('./pages/admin/Dashboard'));
  // [Logic Hidden]
const AdminUsers = lazy(() => import('./pages/admin/Users'));
  // [Logic Hidden]
const AdminContent = lazy(() => import('./pages/admin/Content'));
  // [Logic Hidden]
const AdminSystem = lazy(() => import('./pages/admin/System'));
  // [Logic Hidden]
const AdminAudit = lazy(() => import('./pages/admin/Audit'));
  // [Logic Hidden]
// ------------------------------------------------------------------
// Full-screen loader that matches the dark theme — prevents white flash
// on Suspense boundary while lazy chunks are loading.
// ------------------------------------------------------------------
const PageLoader = () => (
  // [Logic Hidden]
// ------------------------------------------------------------------
// Inner app — lives inside BrowserRouter so it can call useNavigate
// and useNotification (both need their respective providers).
// ------------------------------------------------------------------
function AppInner({ isAuthenticated, setIsAuthenticated }) {
  // [Logic Hidden]
  const handleLogout = useCallback((reason = 'manual') => {
  // [Logic Hidden]
    // Best-effort server logout to clear HttpOnly cookie.
    logoutUser().catch(() => {});
  // [Logic Hidden]
      // The notification will briefly appear but the route guard redirects instantly.
      // This is intentional — we want the user to know why they were logged out.
            ? <Dashboard onLogout={() => handleLogout('manual')} />
  // [Logic Hidden]
// ------------------------------------------------------------------
// Root component — reads auth state synchronously on first render
// by validating the existing HttpOnly cookie session via /profile.
// ------------------------------------------------------------------
export default function App() {
  // [Logic Hidden]
  const verifyAuthSession = useCallback(async () => {
  // [Logic Hidden]
  // Resolve cookie-backed session at startup.
  useEffect(() => {
  // [Logic Hidden]
  // Keep auth state in sync when tab regains focus or user metadata changes.
  useEffect(() => {
  // [Logic Hidden]
    const onStorage = (e) => {
  // [Logic Hidden]
    const onFocus = () => verifyAuthSession();
  // [Logic Hidden]
    return () => {
  // [Logic Hidden]
```

## frontend\src\api.js
```javascript
// ===== API CONFIGURATION =====
// Auth endpoints (login/register) are on Node.js backend (port 5000)
// Protected Python endpoints are reached through the Node backend proxy.
// Export base URLs for use in components
// Bug #53 fixed: POSE_TRACKING_BASE_URL export removed — no consumer in the codebase
// SEC-12: Cache the CSRF token after first fetch.
// The token changes on every GET /api/csrf-token call, so we only fetch once
// per session (it is invalidated automatically on logout via cookie clear).
const getCsrfToken = async () => {
  // [Logic Hidden]
// Call on app startup so the CSRF cookie is set before any mutation
// Reset cache on logout
export const resetCsrfCache = () => { _csrfToken = null; };
  // [Logic Hidden]
// Create axios instance for AUTH endpoints (Node.js backend)
// Create axios instance for protected WORKOUT/NUTRITION endpoints via Node proxy.
// Timeout set to 60s: workout engine calls Gemini AI + XGBoost models which can
// take 30-50s on first generation (cold start) or for complex profiles.
// Request interceptor for Auth API — attach CSRF token (SEC-1 complete: no localStorage fallback)
    async (config) => {
  // [Logic Hidden]
        // SEC-1 (complete): user auth is fully HttpOnly cookie — no x-auth-token header needed.
        // withCredentials: true on the instance handles cookie sending automatically.
        // Fallback for cross-site deployments (e.g. Render): send token header if stored in localStorage
        // SEC-12: attach CSRF token for state-mutating requests
    (error) => Promise.reject(error)
  // [Logic Hidden]
// Reset cached CSRF token when a mutating request is rejected with 403.
// This allows the next request to fetch a fresh token automatically.
    (response) => response,
  // [Logic Hidden]
    (error) => {
  // [Logic Hidden]
const _slimStringList = (value, maxItems = 24) =>
  // [Logic Hidden]
        .map((item) => (typeof item === 'string' ? item : String(item ?? '')).trim())
  // [Logic Hidden]
const _pickWorkoutProfile = (profile) => {
  // [Logic Hidden]
const _slimWorkoutDayForNutrition = (day) => {
  // [Logic Hidden]
            ? day.exercises.map((ex) => ({
  // [Logic Hidden]
const _pickNutritionPayload = (payload) => {
  // [Logic Hidden]
const _slimFitnessPayload = (url, data) => {
  // [Logic Hidden]
// ARCH-7: Wrap FitnessAPI with circuit breaker to protect against Python backend downtime.
// The interceptor checks the breaker state BEFORE sending each request.
    async (config) => {
  // [Logic Hidden]
        // ARCH-7: Use circuit-breaker preflight so OPEN can transition to HALF_OPEN probe.
        // Auth cookie is sent to Node; Node forwards the JWT to Python as x-auth-token.
        // Fallback for cross-site deployments (e.g. Render): send token header if stored in localStorage
    (error) => Promise.reject(error)
  // [Logic Hidden]
// ARCH-7: Record failures/successes from the Python backend into the circuit breaker.
// CRITICAL FIX: Do NOT record CircuitOpenError as a backend failure — it's a client-side
// preflight rejection, not an actual backend error. Recording it would cause the failure
// counter to increment indefinitely while OPEN, preventing recovery.
    (response) => {
  // [Logic Hidden]
    (error) => {
  // [Logic Hidden]
        // Skip circuit breaker's own errors — they are NOT backend failures
// ===== AUTH ENDPOINTS (Node.js backend - port 5000) =====
export const registerUser = (userData) => AuthAPI.post('/auth/register', userData);
  // [Logic Hidden]
export const loginUser = (userData) => AuthAPI.post('/auth/login', userData);
  // [Logic Hidden]
export const loginWithGoogle = (tokenId) => AuthAPI.post('/auth/google', { token: tokenId });
  // [Logic Hidden]
export const logoutUser = () => AuthAPI.post('/auth/logout');
  // [Logic Hidden]
export const requestPasswordReset = (payload) => AuthAPI.post('/auth/reset-password/request', payload);
  // [Logic Hidden]
export const confirmPasswordReset = (payload) => AuthAPI.post('/auth/reset-password/confirm', payload);
  // [Logic Hidden]
export const getSessionStatus = () => AuthAPI.get('/auth/session');
  // [Logic Hidden]
// ===== PROFILE ENDPOINTS (Node.js backend - port 5000) =====
export const getProfile = () => AuthAPI.get('/profile');
  // [Logic Hidden]
export const saveProfile = (profileData) => AuthAPI.post('/profile/update', profileData);
  // [Logic Hidden]
export const saveUserProfile = (profileData) => AuthAPI.post('/profile/update', profileData);
  // [Logic Hidden]
export const saveTrends = (trendData) => AuthAPI.post('/profile/trends', trendData);
  // [Logic Hidden]
export const getTrends = (period = 'week') => AuthAPI.get(`/profile/trends?period=${period}`);
  // [Logic Hidden]
export const saveUserWorkoutToNode = (workoutData) => AuthAPI.post('/users/workout/save', workoutData);
  // [Logic Hidden]
export const saveUserMealToNode = (mealData) => AuthAPI.post('/users/meals/save', mealData);
  // [Logic Hidden]
export const getExternalNutritionData = (query) => AuthAPI.get('/users/external/nutrition', { params: { query } });
  // [Logic Hidden]
export const getExternalExerciseData = (muscle) => AuthAPI.get('/users/external/exercise', { params: { muscle } });
  // [Logic Hidden]
// ===== ADMIN ENDPOINTS (Node.js backend - port 5000) =====
export const adminLogin = (payload) => AuthAPI.post('/admin/login', payload);
  // [Logic Hidden]
export const adminLogout = () => AuthAPI.post('/admin/logout');
  // [Logic Hidden]
export const adminVerify = () => AuthAPI.get('/admin/verify');
  // [Logic Hidden]
export const adminGetUsers = (params) => AuthAPI.get('/admin/users', { params });
  // [Logic Hidden]
export const adminGetUserStats = () => AuthAPI.get('/admin/users/stats/overview');
  // [Logic Hidden]
export const adminGetUser = (id) => AuthAPI.get(`/admin/users/${id}`);
  // [Logic Hidden]
export const adminSuspendUser = (id, reason) => AuthAPI.post(`/admin/users/${id}/suspend`, { reason });
  // [Logic Hidden]
export const adminActivateUser = (id) => AuthAPI.post(`/admin/users/${id}/activate`);
  // [Logic Hidden]
export const adminResetUserPassword = (id) => AuthAPI.post(`/admin/users/${id}/reset-password`);
  // [Logic Hidden]
export const adminDeleteUser = (id) => AuthAPI.delete(`/admin/users/${id}`);
  // [Logic Hidden]
export const adminGetHealth = () => AuthAPI.get('/admin/system/health');
  // [Logic Hidden]
export const adminGetSystemStats = () => AuthAPI.get('/admin/system/stats');
  // [Logic Hidden]
export const adminGetMaintenance = () => AuthAPI.get('/admin/system/maintenance');
  // [Logic Hidden]
export const adminSetMaintenance = (payload) => AuthAPI.post('/admin/system/maintenance', payload);
  // [Logic Hidden]
export const adminGetAuditLogs = (params) => AuthAPI.get('/admin/system/audit-logs', { params });
  // [Logic Hidden]
export const adminCreateAnnouncement = (payload) => AuthAPI.post('/admin/system/announcement', payload);
  // [Logic Hidden]
export const adminDeleteAnnouncement = (announcementId) =>
  // [Logic Hidden]
export const adminGetAnnouncements = () => AuthAPI.get('/admin/system/announcements');
  // [Logic Hidden]
export const adminGetExercises = (params) => AuthAPI.get('/admin/content/exercises', { params });
  // [Logic Hidden]
export const adminCreateExercise = (payload) => AuthAPI.post('/admin/content/exercises', payload);
  // [Logic Hidden]
export const adminUpdateExercise = (id, payload) => AuthAPI.put(`/admin/content/exercises/${id}`, payload);
  // [Logic Hidden]
export const adminDeleteExercise = (id) => AuthAPI.delete(`/admin/content/exercises/${id}`);
  // [Logic Hidden]
export const adminGetWorkoutRules = () => AuthAPI.get('/admin/content/workout-rules');
  // [Logic Hidden]
export const adminSetWorkoutRules = (rules) => AuthAPI.post('/admin/content/workout-rules', { rules });
  // [Logic Hidden]
// ===== WORKOUT/NUTRITION ENDPOINTS (Python backend - port 8000) =====
export const updateProfileAndRegenerateWorkouts = (profileData) =>
  // [Logic Hidden]
export const getWeeklyWorkoutPlan = () =>
  // [Logic Hidden]
export const getWorkoutSwapOptions = (dayIndex) =>
  // [Logic Hidden]
export const generateNutritionPlan = (payload) => {
  // [Logic Hidden]
        wrappedPromise.cancel = () => nutritionRequestController?.abort();
  // [Logic Hidden]
        .then((response) => {
  // [Logic Hidden]
        .catch((error) => {
  // [Logic Hidden]
        .finally(() => {
  // [Logic Hidden]
    retPromise.cancel = () => nutritionRequestController?.abort();
  // [Logic Hidden]
export const getNutritionSwapOptions = (payload) =>
  // [Logic Hidden]
export const swapRestToWorkout = (payload) =>
  // [Logic Hidden]
export const swapWorkoutToRest = (payload) =>
  // [Logic Hidden]
export const clearWorkoutPlanCache = () => {
  // [Logic Hidden]
export const suggestDailyMeals = (profileData, intensityFocus) =>
  // [Logic Hidden]
const _pickChatProfile = (profile, includeSensitive = false) => {
  // [Logic Hidden]
        Object.entries(compact).filter(([, value]) => {
  // [Logic Hidden]
export const sendChatbotMessage = (message, profile, history, options = {}) => {
  // [Logic Hidden]
    // Sanitize history: only keep role + text as strings, drop booleans/nulls,
    // and cap at 50 entries to stay within backend max_length validation.
        .filter((msg) => msg && typeof msg === 'object' && msg.role && msg.text)
  // [Logic Hidden]
        .map(({ role, text }) => ({ role: String(role), content: String(text) }));
  // [Logic Hidden]
export const generateAIPlan = (profileData) =>
  // [Logic Hidden]
export const saveWorkoutPlan = (workoutData) =>
  // [Logic Hidden]
export const saveWorkoutCompletion = (workoutData) =>
  // [Logic Hidden]
export const getWorkoutHistory = () =>
  // [Logic Hidden]
export const saveWorkoutHistory = (data) =>
  // [Logic Hidden]
export const undoWorkoutSwapHistory = () =>
  // [Logic Hidden]
export const saveMealPlan = (mealData) =>
  // [Logic Hidden]
export const saveMealCompletion = (mealData) =>
  // [Logic Hidden]
export const getMealHistory = () =>
  // [Logic Hidden]
export const saveMealHistory = (data) =>
  // [Logic Hidden]
export const updateStreak = (streakData) =>
  // [Logic Hidden]
export const getUserProgress = () =>
  // [Logic Hidden]
// ─────────────────────────────────────────────────────────────────────────────
// Workout helpers (Issue #4 – async generation + caching)
// ─────────────────────────────────────────────────────────────────────────────
/**
 * Standard synchronous plan generation with request coalescing.
 * - If multiple components ask for /workout at the same time, they share one request.
 * - Returns { promise, cancel } so callers can abort on unmount (Bug #63 fix).
 */
export const generateWorkout = (profileData) => {
  // [Logic Hidden]
        wrappedPromise.cancel = () => workoutRequestController?.abort();
  // [Logic Hidden]
    // Bug #63 fix: create a fresh AbortController for each new request
        .then((response) => {
  // [Logic Hidden]
        .catch((error) => {
  // [Logic Hidden]
        .finally(() => {
  // [Logic Hidden]
    retPromise.cancel = () => workoutRequestController?.abort();
  // [Logic Hidden]
/**
 * Async plan generation with polling (Issue #4).
 * Returns cached plan immediately when available; otherwise polls until done.
 *
 * @param {object} profileData  - Full user profile
 * @param {(pct:number)=>void} [onProgress] - Optional progress callback (0-100)
  // [Logic Hidden]
 * @param {number} pollMs       - Polling interval in ms (default 2000)
 * @param {number} maxWait      - Max wait in ms (default 60000)
 */
) => {
  // [Logic Hidden]
    return new Promise((resolve, reject) => {
  // [Logic Hidden]
        const cleanup = () => {
  // [Logic Hidden]
        const finishResolve = (value) => {
  // [Logic Hidden]
        const finishReject = (err) => {
  // [Logic Hidden]
        const onAbort = () => {
  // [Logic Hidden]
        timer = setInterval(async () => {
  // [Logic Hidden]
                        // Bug #62 fix: increment normally up to 89%
                        // Bug #62 fix: after 90% signal indeterminate state (-1) so
                        // the UI can switch to a spinner instead of a stuck bar.
/** Invalidate the server-side plan cache when profile changes significantly. */
export const invalidateWorkoutCache = async (profileData) => {
  // [Logic Hidden]
        // best-effort – silent on failure
// ─────────────────────────────────────────────────────────────────────────────
// Priority 1: POST /api/workout/session-result — submit exercise form score,
//             receive variation suggestion and progression update.
// ─────────────────────────────────────────────────────────────────────────────
/**
 * Send exercise session result to Python backend.
 * @param {object} payload - { exercise_name, form_score, rep_count }
 * @returns {Promise} axios response
 */
export const postSessionResult = (payload) =>
  // [Logic Hidden]
// ─────────────────────────────────────────────────────────────────────────────
// Priority 3: Daily check-in endpoints
// ─────────────────────────────────────────────────────────────────────────────
/**
 * Save daily sleep/water/workout check-in.
 * @param {object} payload - { sleep_hours, water_ml, workout_completed, date? }
 */
export const saveDailyLog = (payload) =>
  // [Logic Hidden]
/** Get last 7 daily check-in logs + summary for the current user. */
export const getWeeklyLogs = () =>
  // [Logic Hidden]
// Legacy compatibility exports for activity tracking
export const logActivityToBackend = (activityData) =>
  // [Logic Hidden]
export const getRecentActivities = (limit = 20) =>
  // [Logic Hidden]
export const syncActivitiesToBackend = (activities) =>
  // [Logic Hidden]
```

## frontend\src\main.jsx
```javascript
// Bug #39 fixed: listen for service worker updates so stale content is reloaded
  window.addEventListener('load', () => {
  // [Logic Hidden]
      .then((registration) => {
  // [Logic Hidden]
        registration.addEventListener('updatefound', () => {
  // [Logic Hidden]
          newWorker.addEventListener('statechange', () => {
  // [Logic Hidden]
            // When the new SW has activated and there was a previous controller,
            // the page is stale — reload to pick up the fresh assets.
      .catch((err) => {
  // [Logic Hidden]
```

## frontend\src\components\AuroraBackground.jsx
```javascript
/**
 * AuroraBackground  (v3 — Theme-Aware Dual Mode)
 * ──────────────────────────────────────────────
 * Dark mode:  Original aurora mesh-gradient orbs + drifting star-field canvas + grain
 * Light mode: Warm pastel gradient background with soft glowing orbs — NO stars
 *             (stars look bad on light backgrounds)
 *
 * • Detects [data-theme] on <body> via MutationObserver — updates without full re-mount
 * • Fixed position, full viewport, z-index 0, pointer-events none
 */
/* ── Dark-mode CSS ────────────────────────────────────────────────────────── */
  /* Orbs */
/* ── Light-mode CSS ───────────────────────────────────────────────────────── */
    /* Warm, premium off-white base — not stark white */
  /* Very subtle cross-gradient base layer */
  /* Soft lavender — top-left */
  /* Soft sky-blue — top-right */
  /* Soft mint — bottom-left */
  /* Soft rose — bottom-right */
  /* Very subtle light grain */
/* ── Star-field canvas hook (dark mode only) ─────────────────────────────── */
function useStarfield(canvasRef, active) {
  // [Logic Hidden]
  useEffect(() => {
  // [Logic Hidden]
    const rand = (a, b) => Math.random() * (b - a) + a;
  // [Logic Hidden]
    const buildStars = (W, H) => {
  // [Logic Hidden]
    function pickColor() {
  // [Logic Hidden]
    const resize = () => {
  // [Logic Hidden]
    const draw = () => {
  // [Logic Hidden]
    const vis = () => { paused = document.hidden; };
  // [Logic Hidden]
    return () => {
  // [Logic Hidden]
/* ── Component ───────────────────────────────────────────────────────────── */
export default function AuroraBackground() {
  // [Logic Hidden]
  // Watch body[data-theme] so we re-render when user toggles theme
    () => document.body.getAttribute('data-theme') !== 'light'
  // [Logic Hidden]
  useEffect(() => {
  // [Logic Hidden]
    const observer = new MutationObserver(() => {
  // [Logic Hidden]
    return () => observer.disconnect();
  // [Logic Hidden]
  // Light mode — warm pastel gradient, NO stars
```

## frontend\src\components\ConfirmDialog.jsx
```javascript
const ConfirmDialog = ({ show, message, onConfirm, onCancel }) => {
  // [Logic Hidden]
  useEffect(() => {
  // [Logic Hidden]
      // Lock background scroll
      // Unlock background scroll
    // Cleanup function
  // [Logic Hidden]
    return () => {
  // [Logic Hidden]
    <div className="confirm-modal-backdrop" onClick={() => onCancel(false)}>
  // [Logic Hidden]
      <div className="confirm-modal-card" onClick={(e) => e.stopPropagation()}>
  // [Logic Hidden]
          <button className="confirm-modal-btn-cancel" onClick={() => onCancel(false)}>Cancel</button>
  // [Logic Hidden]
          <button className="confirm-modal-btn-confirm" onClick={() => onConfirm(true)}>Confirm</button>
  // [Logic Hidden]
```

## frontend\src\components\FloatingBubblesBackground.jsx
```javascript
// FloatingBubblesBackground has been replaced by AuroraBackground.
// This file re-exports AuroraBackground under the old name so any
// legacy import of FloatingBubblesBackground still compiles without errors.
```

## frontend\src\components\Navbar.jsx
```javascript
/**
 * Shared Navbar component — Responsive Refactor.
 *
 * Props
 * ─────
 *  navigate      (fn)     — react-router-dom navigate function
  // [Logic Hidden]
 *  activePage    (str)    — 'dashboard' | 'workout' | 'nutrition' | 'chatbot'
 *  onLogout      (fn)     — called when user clicks Logout
 *  rightContent  (node)   — optional extra icon buttons to insert before Logout
 */
const getStyles = (isDark) => ({
  // [Logic Hidden]
export default function Navbar({ navigate, activePage, onLogout, rightContent, isDark = true }) {
  // [Logic Hidden]
  const [notifications, setNotifications] = useState(() => getFromStorage('active_notifications', []));
  // [Logic Hidden]
  // Sync notifications with localStorage
  useEffect(() => {
  // [Logic Hidden]
    const syncNotifs = () => {
  // [Logic Hidden]
    return () => {
  // [Logic Hidden]
  // Dismiss notification
  const dismissNotification = (id) => {
  // [Logic Hidden]
    const updated = notifications.filter((n) => n.id !== id);
  // [Logic Hidden]
  // Close notifications dropdown on click outside
  useEffect(() => {
  // [Logic Hidden]
    const handleClickOutside = (event) => {
  // [Logic Hidden]
    return () => document.removeEventListener('mousedown', handleClickOutside);
  // [Logic Hidden]
  // Close menu when clicking escape
  useEffect(() => {
  // [Logic Hidden]
    const handleEsc = (e) => {
  // [Logic Hidden]
    return () => window.removeEventListener('keydown', handleEsc);
  // [Logic Hidden]
  // Prevent background scrolling when menu is open
  useEffect(() => {
  // [Logic Hidden]
    return () => {
  // [Logic Hidden]
  const toggleMenu = () => setIsMobileMenuOpen(!isMobileMenuOpen);
  // [Logic Hidden]
  const closeMenu = () => setIsMobileMenuOpen(false);
  // [Logic Hidden]
  const handleNavClick = (path, isActive) => {
  // [Logic Hidden]
          onClick={() => navigate('/dashboard')}
  // [Logic Hidden]
          onKeyDown={(e) => {
  // [Logic Hidden]
          {NAV_ITEMS.map(({ key, label, path }) => {
  // [Logic Hidden]
                onClick={() => handleNavClick(path, isActive)}
  // [Logic Hidden]
              onClick={() => setShowNotif(!showNotif)}
  // [Logic Hidden]
                  notifications.map((n, idx) => (
  // [Logic Hidden]
                        onClick={(e) => {
  // [Logic Hidden]
            onKeyDown={(e) => e.key === 'Enter' && onLogout?.()}
  // [Logic Hidden]
          {NAV_ITEMS.map(({ key, label, path }) => {
  // [Logic Hidden]
                onClick={() => handleNavClick(path, isActive)}
  // [Logic Hidden]
            onClick={() => {
  // [Logic Hidden]
```

## frontend\src\components\NotificationProvider.jsx
```javascript
/* eslint-disable react-refresh/only-export-components */
export const useNotification = () => {
  // [Logic Hidden]
export const NotificationProvider = ({ children }) => {
  // [Logic Hidden]
  const showNotification = useCallback((message, type = 'info', duration = 4000) => {
  // [Logic Hidden]
    setNotifications(prev => [...prev, notification]);
  // [Logic Hidden]
    // Auto-remove notification after duration
    setTimeout(() => {
  // [Logic Hidden]
      setNotifications(prev => prev.filter(n => n.id !== id));
  // [Logic Hidden]
  const showError = useCallback((message, duration = 5000) => {
  // [Logic Hidden]
  const showSuccess = useCallback((message, duration = 4000) => {
  // [Logic Hidden]
  const showWarning = useCallback((message, duration = 4000) => {
  // [Logic Hidden]
  const showInfo = useCallback((message, duration = 4000) => {
  // [Logic Hidden]
  const removeNotification = useCallback((id) => {
  // [Logic Hidden]
    setNotifications(prev => prev.filter(n => n.id !== id));
  // [Logic Hidden]
const NotificationList = ({ notifications, removeNotification }) => {
  // [Logic Hidden]
      {notifications.map((notification) => (
  // [Logic Hidden]
          onClose={() => removeNotification(notification.id)}
  // [Logic Hidden]
const NotificationItem = ({ notification, onClose }) => {
  // [Logic Hidden]
  const getNotificationStyles = () => {
  // [Logic Hidden]
```

## frontend\src\components\PoseDetector.jsx
```javascript
// ─── COMPREHENSIVE MOVEMENT PATTERNS ──
// Pattern mapping for 1300+ exercise dataset via keyword matching
const getLegacyFallback = (name) => {
  // [Logic Hidden]
    if (kws.some(kw => lower.includes(kw))) return pat;
  // [Logic Hidden]
// ─── Speed category for adaptive smoothing & frame skip ──
// ─── ANGLE MATH ──
const calcAngle = (a, b, c) => {
  // [Logic Hidden]
// ─── Adaptive EMA smoother ──
// Fast exercises (curls): high alpha (0.50) = more responsive to quick movement
// Slow exercises (squats): low alpha (0.25) = smoother, less jitter
const emaSmooth = (prev, curr, alpha) => ({
  // [Logic Hidden]
const getAlpha = (pattern) => {
  // [Logic Hidden]
const getFrameSkip = (pattern) => {
  // [Logic Hidden]
// Minimum visibility threshold for reliable angle calculations
const getPrimaryVisibility = (pattern, pts) => {
  // [Logic Hidden]
const smoothPoint = (prev, curr, alpha) => {
  // [Logic Hidden]
// ─── FORM SAFETY RULES per pattern ──
const checkForm = (pattern, angles, calibration = {}) => {
  // [Logic Hidden]
      // Shoulder angle here is not torso tilt; only flag extreme compensation.
      // Personalized tolerance: allow users with different limb lengths/mobility
      // to move slightly above the default target without false "bad form" warnings.
// ─── REP COUNTING CONFIG with ROM validation ──
// Hysteresis band to avoid jitter-based double counting
export default function PoseDetector({
  // [Logic Hidden]
  // Bug #2 Fix: Warming message auto-dismiss timer
  // Auto-dismiss timer for warming message
  useEffect(() => {
  // [Logic Hidden]
    // When model loads, notify parent and set 3-second warming message
      // Notify parent about loading status
      // Clear any existing timer
      // Auto-dismiss after 3 seconds
      warmingTimerRef.current = setTimeout(() => {
  // [Logic Hidden]
    // Cleanup on unmount
    return () => {
  // [Logic Hidden]
  // EMA smoothed landmarks
  // Frame counter for skip logic
  // Track the last warning to avoid repeating the same message
  // Rep state — 3-phase state machine
    // Calf-specific: track ankle Y position
    // Hold detection for isometric exercises
    // Stabilize brief landmark dropouts
  // ─── Initialise MediaPipe ──
  useEffect(() => {
  // [Logic Hidden]
    (async () => {
  // [Logic Hidden]
        // Warm CDN/model caches before creating the detector for faster first use.
    return () => { active = false; };
  // [Logic Hidden]
  // ─── Reset state on exercise change ──
  useEffect(() => {
  // [Logic Hidden]
  // ─────────────────────────────────────
  //  MAIN ANALYSIS & DRAWING
  // ─────────────────────────────────────
  const analyzeAndDraw = useCallback((rawLandmarks, canvas, isPredictionStale = false) => {
  // [Logic Hidden]
    const toPoint = (idx) => ({
  // [Logic Hidden]
    // Extract raw points
    // Apply adaptive EMA smoothing based on exercise speed
    // Calculate all angles
    // ─── CONFIDENCE GATE ──
    // Personalized baseline update for shoulder raises.
    // We only adapt baseline on confident frames to avoid jitter drift.
    // ─── FORM CHECK with dedup ──
    // Only fire feedback if: different warning than last, and enough time passed
    // Require warning stability across multiple confident frames to avoid jitter false alarms.
    // ─── REP COUNTING — 3-phase state machine with ROM validation ──
      // ── CALF RAISE: Use ankle Y-position delta instead of angle ──
      // Detect upward movement (heel raise = Y decreases)
        // Coming back down
      // ── Standard angle-based rep counting ──
      // Track angle extremes during the rep for ROM validation
        // "Normal" — angle starts high (rest), goes low (contracted), back to high
        // rest → contracting (angle drops below down threshold)
        // contracting → extended (angle rises above up threshold) → count rep if ROM valid
          // Validate ROM before counting
            // Partial rep — reset without counting
            // Feedback for partial reps (debounced)
        // "Inverted" — angle starts high, drops to contracted, rises back
      // ── HOLD DETECTION for planks/isometric core ──
          // Report every 5 seconds held
    // ─── DRAWING ──
    const drawLine = (a, b) => {
  // [Logic Hidden]
    // Skeleton connections
    // ─── ANGLE ARC + TEXT on key joints ──
    const drawAngleArc = (a, b, c, angle, label) => {
  // [Logic Hidden]
      // Arc
      // Text background
    // Show key angles per pattern
      CURL:    () => { drawAngleArc(l_sh, l_el, l_wr, leftElbow, 'L Elbow'); drawAngleArc(r_sh, r_el, r_wr, rightElbow, 'R Elbow'); },
  // [Logic Hidden]
      PRESS:   () => { drawAngleArc(l_sh, l_el, l_wr, leftElbow, 'L Elbow'); drawAngleArc(r_sh, r_el, r_wr, rightElbow, 'R Elbow'); },
  // [Logic Hidden]
      SQUAT:   () => { drawAngleArc(l_hi, l_kn, l_an, leftKnee, 'L Knee'); drawAngleArc(r_hi, r_kn, r_an, rightKnee, 'R Knee'); drawAngleArc(l_sh, l_hi, l_kn, leftHip, 'L Hip'); },
  // [Logic Hidden]
      HINGE:   () => { drawAngleArc(l_sh, l_hi, l_kn, leftHip, 'L Hip'); drawAngleArc(r_sh, r_hi, r_kn, rightHip, 'R Hip'); },
  // [Logic Hidden]
      LUNGE:   () => { drawAngleArc(l_hi, l_kn, l_an, leftKnee, 'L Knee'); drawAngleArc(r_hi, r_kn, r_an, rightKnee, 'R Knee'); },
  // [Logic Hidden]
      RAISE:   () => { drawAngleArc(l_hi, l_sh, l_el, leftShoulder, 'L Shoulder'); drawAngleArc(r_hi, r_sh, r_el, rightShoulder, 'R Shoulder'); },
  // [Logic Hidden]
      CORE:    () => { drawAngleArc(l_sh, l_hi, l_kn, leftHip, 'L Hip'); drawAngleArc(r_sh, r_hi, r_kn, rightHip, 'R Hip'); },
  // [Logic Hidden]
      CALF:    () => { drawAngleArc(l_hi, l_kn, l_an, leftKnee, 'L Knee'); },
  // [Logic Hidden]
    (showAngles[pattern] || (() => {
  // [Logic Hidden]
    // ─── Draw JOINT NODES ──
    // ─── Rep stage indicator (small HUD) ──
  // ─── Processing loop with adaptive frame skipping ──
  useEffect(() => {
  // [Logic Hidden]
    const processVideo = () => {
  // [Logic Hidden]
          // Adaptive frame skip based on exercise speed
            // Bug #1 fix: log frame errors for debugging; don't crash the animation loop.
            // Notify user every ~30 dropped frames to avoid feedback spam
    return () => {
  // [Logic Hidden]
/* eslint-disable-next-line react-refresh/only-export-components */
```

## frontend\src\components\TimerExerciseMode.jsx
```javascript
const formatClock = (seconds) => {
  // [Logic Hidden]
}) => {
  // [Logic Hidden]
  const handleSetComplete = useCallback(() => {
  // [Logic Hidden]
      if (typeof onComplete === 'function') {
  // [Logic Hidden]
  useEffect(() => {
  // [Logic Hidden]
    const timer = setInterval(() => {
  // [Logic Hidden]
      setTimeLeft((prev) => {
  // [Logic Hidden]
          setTimeout(() => {
  // [Logic Hidden]
    return () => clearInterval(timer);
  // [Logic Hidden]
  useEffect(() => {
  // [Logic Hidden]
    const timer = setInterval(() => {
  // [Logic Hidden]
      setRestTimeLeft((prev) => {
  // [Logic Hidden]
          setTimeout(() => {
  // [Logic Hidden]
            setCurrentSet((current) => current + 1);
  // [Logic Hidden]
    return () => clearInterval(timer);
  // [Logic Hidden]
  const handleToggle = () => {
  // [Logic Hidden]
    setIsPaused((prev) => !prev);
  // [Logic Hidden]
            onClick={() => setRestTimeLeft(0)}
  // [Logic Hidden]
              onClick={() => {
  // [Logic Hidden]
                if (typeof onSkip === 'function') {
  // [Logic Hidden]
```

## frontend\src\components\UserProfile.jsx
```javascript
const UserProfile = () => {
  // [Logic Hidden]
    const handleChange = (e) => {
  // [Logic Hidden]
        setFormData(prev => ({
  // [Logic Hidden]
    const handleSubmit = async (e) => {
  // [Logic Hidden]
```

## frontend\src\components\admin\AdminActionDialog.jsx
```javascript
export default function AdminActionDialog({
  // [Logic Hidden]
  useEffect(() => {
  // [Logic Hidden]
    return () => {
  // [Logic Hidden]
  const canConfirm = useMemo(() => {
  // [Logic Hidden]
    <div style={backdropStyle} onClick={() => onCancel?.()}>
  // [Logic Hidden]
      <div style={cardStyle} onClick={(e) => e.stopPropagation()}>
  // [Logic Hidden]
              onChange={(e) => setReason(e.target.value)}
  // [Logic Hidden]
              onChange={(e) => setPhrase(e.target.value)}
  // [Logic Hidden]
          <button className="admin-btn secondary" type="button" onClick={() => onCancel?.()}>
  // [Logic Hidden]
            onClick={() => onConfirm?.({ reason: reason.trim(), phrase: phrase.trim() })}
  // [Logic Hidden]
```

## frontend\src\components\admin\AdminLayout.jsx
```javascript
export default function AdminLayout() {
  // [Logic Hidden]
  const handleLogout = async () => {
  // [Logic Hidden]
      // Best-effort logout.
          {navItems.map((item) => (
  // [Logic Hidden]
              className={({ isActive }) =>
  // [Logic Hidden]
```

## frontend\src\components\admin\AdminRoute.jsx
```javascript
export default function AdminRoute() {
  // [Logic Hidden]
  useEffect(() => {
  // [Logic Hidden]
    const verify = async () => {
  // [Logic Hidden]
        // Handled below by unauthorized state.
    return () => {
  // [Logic Hidden]
```

## frontend\src\components\dashboard\ActivityChart.jsx
```javascript
/**
 * BUG-F2/F8: ActivityChart.jsx
 *
 * Extracted from Dashboard.jsx (was at line 1361-1485).
 * A memoized SVG line/area chart with hover tooltips for tracking
 * daily/weekly fitness metrics (workout, water, sleep, meal, calories).
 *
 * Props
 * -----
 * data       : number[]   — data points to plot
 * mode       : 'all' | 'water' | 'sleep' | 'meal' | 'workout'
 * period     : 'week' | 'month'
 * xLabels    : string[]   — optional custom x-axis labels (default: Mon-Sun)
 */
const isSamePrimitiveArray = (a, b) => {
  // [Logic Hidden]
const ActivityChart = React.memo(({ data, mode, period, xLabels: propXLabels }) => {
  // [Logic Hidden]
  const getPoint = (i) => {
  // [Logic Hidden]
        {yLabels.map((label, i) => (
  // [Logic Hidden]
        {xLabels.map((day, i) => {
  // [Logic Hidden]
        {data.map((val, i) => {
  // [Logic Hidden]
            <g key={i} onMouseEnter={() => setHoveredPoint(i)} onMouseLeave={() => setHoveredPoint(null)}>
  // [Logic Hidden]
        {hoveredPoint !== null && (() => {
  // [Logic Hidden]
}, (prevProps, nextProps) => {
  // [Logic Hidden]
```

## frontend\src\components\workout\WorkoutDayCard.jsx
```javascript
/**
 * WorkoutDayCard.jsx
 *
 * BUG-F2/F8: Extracted from Workout.jsx (lines 1978–2111).
 * Renders a single day card in the weekly workout grid.
 * Pure presentational component — no API calls.
 *
 * Props:
 *   day             – plan day object from Python backend
 *   dayIdx          – 0-6 (Mon-Sun)
 *   status          – 'TODAY' | 'COMPLETED' | 'PAST' | 'NOT_STARTED' | 'REST' | 'NO PLAN' | 'UPCOMING'
 *   isRest          – boolean
 *   isPlaceholder   – boolean
 *   isToday         – boolean
 *   layout          – responsive layout tokens from Workout.jsx
 *   styles          – base styles object from Workout.jsx
 *   weekdayNames    – ['Monday', …, 'Sunday']
 *   onStartWorkout  – (dayIdx: number) => void
  // [Logic Hidden]
 *   onSwapToRest    – (dayIdx: number) => void
  // [Logic Hidden]
 *   canSwapToRest   – boolean
 */
// Status → badge colours (avoids recomputing inline)
}) => {
  // [Logic Hidden]
  const previewExercises = dayExercises.filter((ex) => !ex?.is_warmup);
  // [Logic Hidden]
  // Card style based on status
      onClick={() => !isPlaceholder && !isRest && onStartWorkout(dayIdx)}
  // [Logic Hidden]
              {displayExercises.slice(0, 3).map((ex, i) => (
  // [Logic Hidden]
                  onClick={(e) => { e.stopPropagation(); onStartWorkout(dayIdx); }}
  // [Logic Hidden]
                  onClick={(e) => { e.stopPropagation(); onStartWorkout(dayIdx); }}
  // [Logic Hidden]
                  onClick={(e) => { e.stopPropagation(); onSwapToRest(dayIdx); }}
  // [Logic Hidden]
```

## frontend\src\context\ThemeContext.jsx
```javascript
/**
 * ThemeContext — global light/dark mode management
 * Persists user preference to localStorage as 'elevate_theme'.
 * Applies a `data-theme` attribute on <body> so CSS variables work globally.
 */
const ThemeContext = createContext({ theme: 'dark', toggleTheme: () => {} });
  // [Logic Hidden]
export function ThemeProvider({ children }) {
  // [Logic Hidden]
  const [theme, setTheme] = useState(() => {
  // [Logic Hidden]
  useEffect(() => {
  // [Logic Hidden]
  const toggleTheme = () => setTheme(prev => prev === 'dark' ? 'light' : 'dark');
  // [Logic Hidden]
// eslint-disable-next-line react-refresh/only-export-components
export const useTheme = () => useContext(ThemeContext);
  // [Logic Hidden]
```

## frontend\src\data\quotes.js
```javascript
  // --- THE DAVID GOGGINS / JOCKO WILLINK TIER (Extreme Discipline) ---
  // --- THE STOIC / BRUTAL TRUTH TIER ---
  // --- THE BODYBUILDING / IRON TIER ---
  // --- THE "DARK MOTIVATION" TIER ---
  // --- SHORT & PUNCHY (For Mobile Layouts) ---
  // --- CONTINUATION (To ensure zero repeats for months) ---
```

## frontend\src\pages\Chatbot.jsx
```javascript
// ===== STYLES =====
const getStyles = (isDark) => ({
  // [Logic Hidden]
function renderMarkdown(text) {
  // [Logic Hidden]
  const flushList = () => {
  // [Logic Hidden]
          {listItems.map((item, i) => (
  // [Logic Hidden]
  const flushTable = () => {
  // [Logic Hidden]
      const parseRow = (rowStr) => {
  // [Logic Hidden]
          .map(s => s.trim())
  // [Logic Hidden]
          .filter((s, idx, arr) => idx > 0 && idx < arr.length - 1);
  // [Logic Hidden]
        .filter(r => r.trim() && !r.includes('---'))
  // [Logic Hidden]
        .map(r => parseRow(r));
  // [Logic Hidden]
                  {headerRow.map((h, i) => (
  // [Logic Hidden]
              {bodyRows.map((row, i) => (
  // [Logic Hidden]
                  {row.map((cell, j) => (
  // [Logic Hidden]
  const processInline = (line) => {
  // [Logic Hidden]
    return parts.flatMap((part, i) => {
  // [Logic Hidden]
      return subparts.map((subpart, j) => {
  // [Logic Hidden]
  lines.forEach((line, i) => {
  // [Logic Hidden]
    // Table detection
    // List detection
    // Blockquote detection
function TypingIndicator({ styles }) {
  // [Logic Hidden]
function Chatbot() {
  // [Logic Hidden]
  useEffect(() => {
  // [Logic Hidden]
    const loadProfile = async () => {
  // [Logic Hidden]
    return () => {
  // [Logic Hidden]
  useEffect(() => {
  // [Logic Hidden]
  useEffect(() => {
  // [Logic Hidden]
  useEffect(() => {
  // [Logic Hidden]
      const timer = setTimeout(() => setError(null), 5000);
  // [Logic Hidden]
      return () => clearTimeout(timer);
  // [Logic Hidden]
  const sendMessage = useCallback(async (text) => {
  // [Logic Hidden]
    cooldownTimerRef.current = setTimeout(() => setCooldown(false), 1500);
  // [Logic Hidden]
      setMessages(prev => [...prev, botMsg]);
  // [Logic Hidden]
      setMessages(prev => [...prev, {
  // [Logic Hidden]
      setTimeout(() => inputRef.current?.focus(), 100);
  // [Logic Hidden]
  const handleSubmit = (e) => {
  // [Logic Hidden]
  const handleKeyDown = (e) => {
  // [Logic Hidden]
  const clearChat = () => {
  // [Logic Hidden]
  const handleLogout = () => {
  // [Logic Hidden]
      onConfirm: (confirmed) => {
  // [Logic Hidden]
                  {SUGGESTIONS.map((s, i) => (
  // [Logic Hidden]
                      onClick={() => sendMessage(s.text)}
  // [Logic Hidden]
                {messages.map((msg, i) => (
  // [Logic Hidden]
                  onChange={(e) => {
  // [Logic Hidden]
        onConfirm={() => {
  // [Logic Hidden]
        onCancel={() => {
  // [Logic Hidden]
```

## frontend\src\pages\Dashboard.jsx
```javascript
// --- FULL PREMIUM STYLES (JS Object - Static Only) ---
// --- RESPONSIVE CSS STRING (Animations, Media Queries, Hover States) ---
  * {
  /* ===== HOVER EFFECTS ===== */
  /* ===== ANIMATIONS ===== */
  /* ===== SCROLLBAR ===== */
  /* ===== ANIMATIONS (Entry/Exit) ===== */
  /* ===== RESPONSIVE MEDIA QUERIES ===== */
  /* Extra Small Mobile (320px - 480px) */
  /* Small Mobile (481px - 768px) */
  /* Tablet (769px - 1024px) */
  /* Desktop (1025px+) */
// --- CHART COMPONENT ---
const ActivityChart = React.memo(({ data, mode, period, xLabels: propXLabels }) => {
  // [Logic Hidden]
  const getPoint = (i) => {
  // [Logic Hidden]
        {yLabels.map((label, i) => (
  // [Logic Hidden]
        {xLabels.map((day, i) => {
  // [Logic Hidden]
        {data.map((val, i) => {
  // [Logic Hidden]
            <g key={i} onMouseEnter={() => setHoveredPoint(i)} onMouseLeave={() => setHoveredPoint(null)}>
  // [Logic Hidden]
        {hoveredPoint !== null && (() => {
  // [Logic Hidden]
}, (prevProps, nextProps) => {
  // [Logic Hidden]
// --- DEFAULT HISTORY ---
// Switch this value to: 'minimal' | 'bold' | 'glass' | 'orbitFusion' | 'glassSlideNeo' | 'neonRadial'
const getHeroActionTheme = (variantName, stateKey) => {
  // [Logic Hidden]
// Progress circle score is now computed dynamically inside Dashboard component
// based on real daily metrics (workout done, meals logged, water intake, sleep hours).
// This function is kept only as a fallback for status-only contexts.
  // [Logic Hidden]
const getFallbackRadialScore = (status) => {
  // [Logic Hidden]
const getHeroActionMeta = (status) => {
  // [Logic Hidden]
const calculateOverallTrendScore = (entry, calorieGoal, waterGoal) => {
  // [Logic Hidden]
function Dashboard({ onLogout }) {
  // [Logic Hidden]
  // --- STATE DECLARATIONS ---
  // ✅ FIX 2: Cross-page macro update — called when meal is saved from Nutrition page
  // Sets absolute macro values (not incremental) from today's totals returned by the backend
  const _setMacrosFromTotals = (totals) => {
  // [Logic Hidden]
      setMacros((prev) => ({
  // [Logic Hidden]
  const _updateMacrosFromMeal = async (mealData) => {
  // [Logic Hidden]
      setMacros((prev) => {
  // [Logic Hidden]
  const [notifications, setNotifications] = useState(() => getFromStorage('active_notifications', []));
  // [Logic Hidden]
  useEffect(() => {
  // [Logic Hidden]
  useEffect(() => {
  // [Logic Hidden]
    const handleResize = () => setViewportWidth(window.innerWidth);
  // [Logic Hidden]
    return () => window.removeEventListener('resize', handleResize);
  // [Logic Hidden]
  const currentQuote = useMemo(() => {
  // [Logic Hidden]
  // --- Compute dailyProgress (0-100) from real daily metrics ---
  //
  // ✅ Breakdown (25 pts each):
  //   Workout: granular per exercise (completedCount / totalCount) × 25
  //   Meals:   exact per meal (0, 1, 2, or 3 of B/L/D) × 25
  //   Water:   intake / (weight × 0.033L) × 25, updates on every glass added
  //   Sleep:   hours / 7h × 25, updates on every 30-min increment
  //
  // Triggers: status, water, sleep (all already live state), mealsLoggedToday, workoutProgress
  useEffect(() => {
  // [Logic Hidden]
      // 1. Workout (25 pts) — granular per-exercise ratio
      //    If full workout done via status flag, give full 25.
      //    Otherwise use workoutProgress (0-1) from _workoutSync.
      // 2. Meals (25 pts) — exact per-meal credit (breakfast/lunch/dinner = ~8.3pts each)
      // 3. Water (25 pts) — intake vs personal goal (weight × 0.033 L), updates per glass
      // 4. Sleep (25 pts) — hours / 7h, updates every +30 min logged
      // Prevent progress bar from going up just because of pre-filled sleep data
  useEffect(() => {
  // [Logic Hidden]
    const unsubWater = syncBridge.subscribe(SyncTypes.WATER_ADDED, (data) => {
  // [Logic Hidden]
      setWater((prev) => (Math.abs(prev - amount) > 0.001 ? amount : prev));
  // [Logic Hidden]
    const unsubSleep = syncBridge.subscribe(SyncTypes.SLEEP_UPDATED, (data) => {
  // [Logic Hidden]
      setSleep((prev) => (Math.abs(prev - amount) > 0.001 ? amount : prev));
  // [Logic Hidden]
    const unsubMeal = syncBridge.subscribe(SyncTypes.MEAL_COMPLETED, (data) => {
  // [Logic Hidden]
    const unsubWorkoutProgress = syncBridge.subscribe(SyncTypes.WORKOUT_PROGRESS, (data) => {
  // [Logic Hidden]
    const unsubWorkoutDone = syncBridge.subscribe(SyncTypes.WORKOUT_COMPLETED, (data) => {
  // [Logic Hidden]
    return () => {
  // [Logic Hidden]
  const getWorkoutPlanForDate = (dateObj) => {
  // [Logic Hidden]
      return plan.find((d) => (d?.day_of_week ?? -1) === idx) || plan[idx] || null;
  // [Logic Hidden]
  const isRestDayForDate = (dateObj) => {
  // [Logic Hidden]
    // 1. Explicit type from backend engine
    // 2. Focus field
    // 3. Label / note
  const normalizeMealEntries = (rawMeals = []) => {
  // [Logic Hidden]
    (Array.isArray(rawMeals) ? rawMeals : []).forEach((entry) => {
  // [Logic Hidden]
        Object.values(entry.meals).forEach((meal) => {
  // [Logic Hidden]
  // --- EFFECTS & LIFECYCLE ---
  // Fetch user and init dashboard
  useEffect(() => {
  // [Logic Hidden]
    const fetchUserData = async () => {
  // [Logic Hidden]
        // Start background preloading of workout cache and pose assets after 3s delay
          setTimeout(() => {
  // [Logic Hidden]
            // 1. Warm workout plan cache if missing or expired
              getWeeklyWorkoutPlan().then((workoutResponse) => {
  // [Logic Hidden]
              }).catch((err) => {
  // [Logic Hidden]
            // 2. Warm nutrition plan cache
              import('../api').then(({ generateNutritionPlan }) => {
  // [Logic Hidden]
                generateNutritionPlan(profileData).then((response) => {
  // [Logic Hidden]
                    // Add profile hash for cache validation in Nutrition.jsx
                }).catch(err => console.warn('[Dashboard] Background nutrition cache warmup failed:', err));
  // [Logic Hidden]
            // 3. Preload MediaPipe pose assets in background
            preloadPoseAssets().catch((err) => {
  // [Logic Hidden]
        // ✅ BACKEND SYNC: Parse MongoDB history instead of localStorage
        // Normalize meal history because backend can return either grouped day objects
        // or flat meal entries depending on write path.
        // Calculate exact macros eaten TODAY from MongoDB
        // ✅ FIX: Only count meals with actual calories as "completed".
        // Zero-calorie entries from old sessions / partial saves must not inflate mealsLoggedToday.
        const mealsToday = normalizedMeals.filter(m => {
  // [Logic Hidden]
        mealsToday.forEach(m => {
  // [Logic Hidden]
        // Fallback hydration from local checked/locked state so values persist across
        // refresh/relogin even when backend meal-history write is still catching up.
          const todayPlan = cachedNutrition?.days?.find((d) => d?.date === todayStr) || cachedNutrition?.days?.[0];
  // [Logic Hidden]
            todayPlan.meals.forEach((meal) => {
  // [Logic Hidden]
              (meal?.foods || []).forEach((food) => {
  // [Logic Hidden]
        // ✅ FIX: Round all macro values to integers
        // ✅ FIX: Only use meal_type (not .name) to identify meal type — avoids false positives
        // where old entries with name="Breakfast" (meal_type undefined) are counted as completed.
          mealsToday.map((m) => String(m.meal_type || m.mealType || '').toLowerCase()).filter(Boolean)
  // [Logic Hidden]
        // ✅ Count exactly how many of breakfast/lunch/dinner have been logged today (0-3)
        setMealsLoggedToday(MAIN_MEALS.filter(t => completedMealTypesToday.has(t)).length);
  // [Logic Hidden]
        const mealsDoneToday = ['breakfast', 'lunch', 'dinner'].every((type) =>
  // [Logic Hidden]
            // On rest day, meal completion is sufficient to mark day as completed.
        // ✅ FIX 1: Macro targets from nutrition plan's daily_target (computed by Python TDEE engine)
        // Priority: cached nutrition plan → goal-based defaults
        (data.workouts || []).forEach(w => {
  // [Logic Hidden]
        normalizedMeals.forEach(m => {
  // [Logic Hidden]
        (Array.isArray(data.recent_activities) ? data.recent_activities : []).forEach((a) => {
  // [Logic Hidden]
        (Array.isArray(persistedActivities) ? persistedActivities : []).forEach((a) => {
  // [Logic Hidden]
        combinedHistory.forEach((item) => {
  // [Logic Hidden]
        deduped.sort((a, b) => {
  // [Logic Hidden]
        // ✅ Avatar Sync
        // ✅ State Sync from DB Trends (Water, Sleep, Streak)
           // Synchronize today's latest data points
           const todayRecord = data.trends.find(t => String(t.date).startsWith(todayStr));
  // [Logic Hidden]
             // ✅ KEY FIX: localStorage is updated synchronously on every button click, while the
             // backend lags by the debounce window (500ms). If the user reduced water then
             // quickly refreshed (before the debounce fired), the DB still holds the OLD value.
             // Prefer localStorage for today's session if it holds a valid number.
             // IMPORTANT: initialise lastSaved.current to match whatever we just set into
             // state (localStorage-preferred). This ensures the debounce diff check fires
             // correctly even when the user reduces water back to the same value that is
             // stored in the DB (e.g. add 0→0.25 then remove 0.25→0: if lastSaved were the
             // DB value 0 the diff would be 0===0 and the save would be silently skipped).
            // Sync to Python AI coach on load
           // ✅ FIX: Advanced Streak Calculation incorporating Rest Days
           // A day is "completed" if meal_completed AND (workout_completed OR isRestDay)
           // Build a map: date-string -> trend entry (pick latest if duplicates)
           data.trends.forEach(t => {
  // [Logic Hidden]
           // Walk backwards from today, day by day
             // Streak is only extended if user actually completes the main daily tasks.
           setStats((prev) => ({ ...prev, streak: currentStreak }));
  // [Logic Hidden]
           // ✅ FIX: Build weekly progress from backend trends data
           const weekData = days.map((day, index) => {
  // [Logic Hidden]
           // Fallback to workout count - Calculate consecutive streak properly
           const completedWorkouts = workouts.filter(w => w.completed || String(w.status).toLowerCase() === 'completed' || w.completedAt);
  // [Logic Hidden]
           const uniqueDays = new Set(completedWorkouts.map(w => (w.completedAt || w.date || '').split('T')[0]));
  // [Logic Hidden]
           setStats((prev) => ({ ...prev, streak: currentStreak }));
  // [Logic Hidden]
           // ✅ FIX: Still build weekly progress even without trends
           setWeeklyProgress(days.map((day, i) => ({ day, status: i < ourIdx ? 'missed' : 'pending' })));
  // [Logic Hidden]
        // Derive definitive status
        const todayRecordForStatus = data.trends && Array.isArray(data.trends) ? data.trends.find(t => String(t.date).startsWith(todayStr)) : null;
  // [Logic Hidden]
        // Fallback calculations if trend data is lagging
        const workoutsTodayArray = (data.workouts || []).filter((w) => {
  // [Logic Hidden]
          // Only completed workout records should count toward today's done status.
        // Fetch weekly averages for adaptive coaching card
    fetchUserData().then((derivedStatus) => {
  // [Logic Hidden]
      // Run daily reset AFTER backend data is loaded.
      // NOTE: checkDailyReset no longer zeroes macros — DB values are authoritative.
      // ✅ FIX: Call checkDayReset to properly set workout→meal→done status flow
    // eslint-disable-next-line react-hooks/exhaustive-deps
  // ✅ NEW: Load activities from backend on mount
  useEffect(() => {
  // [Logic Hidden]
  // Session recovery on mount
  useEffect(() => {
  // [Logic Hidden]
    const recoverSession = () => {
  // [Logic Hidden]
        // ✅ UPDATED: Use storage utility
          // ✅ UPDATED: Use storage utility
  // ✅ FIXED: Daily reset logic with storage utilities
  // BUG WAS HERE: The old condition `lastActivityDate !== today || dailyResetPerformed !== today`
  // would fire on EVERY fresh login (when keys don't exist in storage), wiping
  // TODAY_WORKOUT_DONE / TODAY_MEALS_DONE even though the day hadn't changed.
  //
  // FIX: Only clear session flags when lastActivityDate exists AND is a DIFFERENT day
  // (i.e. the user is logging in on a new calendar day). On a fresh login same day,
  // just write the tracking keys without clearing anything.
  const checkDailyReset = async () => {
  // [Logic Hidden]
      // ✅ KEY FIX: only reset if we KNOW it was a different day previously
      // Always stamp today so future checks detect a new day correctly
        // A real calendar day has rolled over — clear yesterday's session state
        // Clear notification flags for the old day
        keysToRemove.forEach(k => removeFromStorage(k));
  // [Logic Hidden]
      // If lastActivityDate is null/empty (first login ever) OR same as today,
      // do NOT clear any flags — the backend data loaded by fetchUserData() is authoritative.
  // ✅ FIX 2: Cross-page macro sync — re-fetch today's data when user returns to Dashboard
  useEffect(() => {
  // [Logic Hidden]
    const handlePageVisibilityChange = async () => {
  // [Logic Hidden]
          // Re-fetch profile to get updated meal data (e.g., after completing meals on Nutrition page)
          // ✅ FIX: Same calories>0 guard as in fetchUserData — only real meals count
          const mealsToday = normalizedMeals.filter(m => {
  // [Logic Hidden]
          mealsToday.forEach(m => {
  // [Logic Hidden]
          setMacros(prev => ({
  // [Logic Hidden]
          // ✅ PA-6: Also refresh the chart so it reflects latest data
          // ✅ FIX: Re-evaluate central button status using fresh backend data.
          // This ensures when user returns from Nutrition page after completing meals,
          // the button correctly shows "START WORKOUT" instead of "ALL SET".
            ? data.trends.find(t => String(t.date).startsWith(todayStr))
  // [Logic Hidden]
          const workoutsTodayVis = (data.workouts || []).filter(w => {
  // [Logic Hidden]
          // ✅ FIX: Only use meal_type (not .name) so old flat entries don\'t produce false meal counts
            mealsToday.map(m => String(m.meal_type || m.mealType || '').toLowerCase()).filter(Boolean)
  // [Logic Hidden]
          const mealsDone = ['breakfast', 'lunch', 'dinner'].every(t => completedMealTypes.has(t));
  // [Logic Hidden]
          // ✅ Keep mealsLoggedToday in sync after visibility refresh
          setMealsLoggedToday(MAIN_MEALS_VIS.filter(t => completedMealTypes.has(t)).length);
  // [Logic Hidden]
    return () => document.removeEventListener('visibilitychange', handlePageVisibilityChange);
  // [Logic Hidden]
    // eslint-disable-next-line react-hooks/exhaustive-deps
  // ✅ BUG FIX: Listen for macro sync from Nutrition page via localStorage 'storage' event
  // Also handles mealsCount key so the progress circle updates immediately per-meal.
  useEffect(() => {
  // [Logic Hidden]
    const handleStorageSync = (e) => {
  // [Logic Hidden]
            setMacros(prev => ({
  // [Logic Hidden]
            // ✅ If Nutrition page signals the meal count, update circle immediately
      // ✅ Listen for exercise-by-exercise workout progress from Workout page
    return () => window.removeEventListener('storage', handleStorageSync);
  // [Logic Hidden]
  const addNotification = useCallback((message, type = 'info') => {
  // [Logic Hidden]
    setNotifications((prev) => [...prev, newNotification]);
  // [Logic Hidden]
      () => setNotifications((prev) => prev.filter((n) => n.id !== newNotification.id)),
  // [Logic Hidden]
  const dismissNotification = (id) =>
  // [Logic Hidden]
    setNotifications((prev) => prev.filter((n) => n.id !== id));
  // [Logic Hidden]
  const handleClickOutside = (event) => {
  // [Logic Hidden]
  useEffect(() => {
  // [Logic Hidden]
    return () => document.removeEventListener('mousedown', handleClickOutside);
  // [Logic Hidden]
  // ✅ FIXED: logActivity uses storage utility AND saves to backend
  // Added ISO timestamp so deduplication works correctly in loadActivitiesFromBackend
  const logActivity = async (type, name, details) => {
  // [Logic Hidden]
    // Update local state and storage first (for immediate UI feedback)
    setRecentHistory((prev) => {
  // [Logic Hidden]
    // Also save to backend for persistence across sessions
      // Don't break the UI if backend logging fails
  const removeLastLog = (type) => {
  // [Logic Hidden]
    setRecentHistory((prev) => {
  // [Logic Hidden]
      const index = prev.findIndex((item) => item.type === type);
  // [Logic Hidden]
  // ✅ NEW: Load activities from backend on mount
  const loadActivitiesFromBackend = async () => {
  // [Logic Hidden]
        // Merge with local storage activities (in case some were logged while offline)
        // Create a map to deduplicate by type/name/details/timestamp
        // Add backend activities first (they're the authoritative source)
        backendActivities.forEach(activity => {
  // [Logic Hidden]
        // Add local activities that might not be synced yet
        localActivities.forEach(activity => {
  // [Logic Hidden]
        // Convert to array and sort by timestamp (most recent first)
        merged.sort((a, b) => {
  // [Logic Hidden]
        // Update state and localStorage
      // Fall back to localStorage if backend fails
  // ✅ UPDATED: Notification tracking with storage utilities
  const hasNotificationBeenShownToday = (notificationId) => {
  // [Logic Hidden]
  const markNotificationAsShownToday = (notificationId) => {
  // [Logic Hidden]
  const checkWaterThresholdNotifications = useCallback((oldWater, newWater) => {
  // [Logic Hidden]
        setTimeout(() => setShowWaterCelebration(false), 4000);
  // [Logic Hidden]
  const checkSleepThresholdNotifications = useCallback((oldSleep, newSleep) => {
  // [Logic Hidden]
        setTimeout(() => setShowSleepCelebration(false), 4000);
  // [Logic Hidden]
  // ✅ UPDATED: Reminder tracking with storage utilities
  const hasDailyReminderBeenShown = (reminderType) => {
  // [Logic Hidden]
  const markDailyReminderAsShown = (reminderType) => {
  // [Logic Hidden]
  const checkDailyReminders = () => {
  // [Logic Hidden]
          setNotifications((prev) => {
  // [Logic Hidden]
            const exists = prev.some((n) => n.id === newNotification.id);
  // [Logic Hidden]
      // Morning hydration reminder
          setNotifications((prev) => {
  // [Logic Hidden]
            const exists = prev.some((n) => n.id === newNotification.id);
  // [Logic Hidden]
      // Afternoon hydration check
          setNotifications((prev) => {
  // [Logic Hidden]
            const exists = prev.some((n) => n.id === newNotification.id);
  // [Logic Hidden]
  useEffect(() => {
  // [Logic Hidden]
    const interval = setInterval(() => {
  // [Logic Hidden]
    return () => clearInterval(interval);
  // [Logic Hidden]
    // eslint-disable-next-line react-hooks/exhaustive-deps
  // Removed: Empty resize listener that did nothing (was a waste of resources)
  const checkInterruptedSessions = () => {
  // [Logic Hidden]
      // ✅ UPDATED: Use storage utility
  // ✅ UPDATED: Workout session management with storage utilities
  const startWorkoutSession = (sessionDetails = null) => {
  // [Logic Hidden]
  const endWorkoutSession = () => {
  // [Logic Hidden]
  useEffect(() => {
  // [Logic Hidden]
    // updateChart is intentionally excluded to avoid effect loops from function identity changes.
  // [Logic Hidden]
    // eslint-disable-next-line react-hooks/exhaustive-deps
  // Separate lightweight local-only chart update for water/sleep/all live changes
  useEffect(() => {
  // [Logic Hidden]
      setChartData(prev => {
  // [Logic Hidden]
  // ✅ FIXED: Debounce-sync water & sleep to MongoDB trends
  // BUG WAS HERE: lastSaved.current was written BEFORE the async save completed.
  // If saveTrends() silently failed, the ref already matched the new values so the
  // next button click produced no diff and the save was never retried.
  //
  // FIX: Only update the ref on success; roll it back on failure so the next
  // state change (or page visibility change) re-triggers the save attempt.
  useEffect(() => {
  // [Logic Hidden]
    const timer = setTimeout(async () => {
  // [Logic Hidden]
      // Optimistically record what we're about to save
        // Sync with the Python daily logs backend
          // Re-fetch weekly logs to update dashboard card
        // Roll back so the next value change will retry the write
    return () => clearTimeout(timer);
  // [Logic Hidden]
  const updateRecoveryScore = (currentWater, currentSleep) => {
  // [Logic Hidden]
    setStats((prev) => ({ ...prev, focusScore: Math.floor(score) }));
  // [Logic Hidden]
   // ✅ FIX 4: Use StorageKeys for water persistence
   const handleWaterAdd = useCallback(() => {
  // [Logic Hidden]
  const handleWaterRemove = useCallback(() => {
  // [Logic Hidden]
  // ✅ UPDATED: useCallback for sleep handlers
  // ✅ FIX 4: Use StorageKeys for sleep persistence
  const handleSleepAdd = useCallback(() => {
  // [Logic Hidden]
  const handleSleepRemove = useCallback(() => {
  // [Logic Hidden]
  const fetchExternalNutritionData = async (foodQuery) => {
  // [Logic Hidden]
      // Using USDA FoodData Central API (Requires API key)
        // Return mock nutrition data as fallback
      const timeoutId = setTimeout(() => controller.abort(), 10000);
  // [Logic Hidden]
        // Return fallback data if API fails
      // Extract nutrients from USDA format
      const getNutrient = (nutrientId) => {
  // [Logic Hidden]
          n => n.nutrient?.id === nutrientId
  // [Logic Hidden]
      // USDA Nutrient IDs:
      // 1008 = Energy (kcal)
      // 1003 = Protein (g)
      // 1005 = Carbohydrate (g)
      // 1004 = Fat (g)
      // 1079 = Fiber (g)
      // Return fallback data on error
  const fetchExternalExerciseData = async (exerciseQuery) => {
  // [Logic Hidden]
        // Return mock exercise data as fallback
      const timeoutId = setTimeout(() => controller.abort(), 10000);
  // [Logic Hidden]
        // Return fallback data if API fails
      // Return fallback data on error
  const enrichDataWithExternalAPIs = async () => {
  // [Logic Hidden]
  // ✅ UPDATED: Cached data uses storage utilities
  const getCachedEnrichedData = async () => {
  // [Logic Hidden]
  useEffect(() => {
  // [Logic Hidden]
    const maybeEnrich = async () => {
  // [Logic Hidden]
    // eslint-disable-next-line react-hooks/exhaustive-deps
  const updateChart = async (mode, period) => {
  // [Logic Hidden]
        // --- MONTH VIEW: Group into 4 weeks ---
        trends.forEach((entry) => {
  // [Logic Hidden]
        const series = weekBuckets.map((bucket) => {
  // [Logic Hidden]
            const scores = bucket.map((entry) => calculateOverallTrendScore(entry, calorieGoal, waterGoal));
  // [Logic Hidden]
            const avg = scores.reduce((sum, score) => sum + score, 0) / Math.max(1, scores.length);
  // [Logic Hidden]
            const scoreSum = bucket.reduce((sum, e) => sum + (e?.workout_completed ? 100 : (e?.workout_partial ? 50 : 0)), 0);
  // [Logic Hidden]
            const totalCal = bucket.reduce((s, e) => s + (e?.calories || 0), 0);
  // [Logic Hidden]
            const total = bucket.reduce((s, e) => s + (e?.water_intake || e?.water_glasses || 0), 0);
  // [Logic Hidden]
            const total = bucket.reduce((s, e) => s + (e?.sleep_duration || e?.sleep_hours || 0), 0);
  // [Logic Hidden]
        // --- WEEK VIEW: 7-day slots Mon-Sun ---
        trends.forEach((entry) => {
  // [Logic Hidden]
          // Exclude entries that are before the start of the current week
        // Keep today's slot live for selected realtime modes.
  const saveTrendsToBackend = async (trendData) => {
  // [Logic Hidden]
  // ✅ UPDATED: Trends uses storage utilities
  const _updateTrends = async () => {
  // [Logic Hidden]
      // ✅ UPDATED: Use storage utilities
      // ✅ FIX: Send flat macro fields instead of nested `macros` object.
      // The Mongoose schema now expects top-level `calories`, `protein`, `carbs`, `fat`.
  const updateLocalTrendData = (trendData) => {
  // [Logic Hidden]
  // ✅ UPDATED: Day reset uses deriving from backend or fallback to storage
  const checkDayReset = async (forceWorkoutDone, forceMealDone) => {
  // [Logic Hidden]
      // Streak is now computed from backend trends in fetchUserData.
      // Do NOT override with stale localStorage values.
      // ✅ UPDATED: Use storage utility
  const getTodaysWorkoutDay = () => {
  // [Logic Hidden]
      const todayPlan = workoutPlan.find((day) => (day?.day_of_week ?? -1) === todayIdx) || null;
  // [Logic Hidden]
  const handleAction = async () => {
  // [Logic Hidden]
  const showConfirmDialog = (message, onConfirm) =>
  // [Logic Hidden]
  const handleConfirm = () => {
  // [Logic Hidden]
  const handleCancelConfirm = () => {
  // [Logic Hidden]
  // ✅ FIX: Delegate logout to App.jsx via onLogout prop.
  //    This ensures App.jsx's isAuthenticated flips to false BEFORE navigate()
  //    is called, so the route guard never sees a logged-in user on /login.
  const handleLogout = () => {
  // [Logic Hidden]
    showConfirmDialog('Log out of Elevate?', (confirmed) => {
  // [Logic Hidden]
        if (typeof onLogout === 'function') {
  // [Logic Hidden]
          // onLogout() clears storage, sets isAuthenticated=false, and navigates
          // Fallback if prop wasn't passed
  // ✅ BUG FIX 1: Listen for macro sync signals from Nutrition page
  // When user switches back to Dashboard tab, read _macroSync from localStorage
  useEffect(() => {
  // [Logic Hidden]
    const handleVisibilityChange = () => {
  // [Logic Hidden]
            // Only apply if the signal is recent (within last 5 minutes)
              setMacros(prev => ({
  // [Logic Hidden]
            // Clear the signal after consuming it
    return () => document.removeEventListener('visibilitychange', handleVisibilityChange);
  // [Logic Hidden]
          <div style={styles.modalOverlay} onClick={() => setShowImageModal(false)}>
  // [Logic Hidden]
            <div style={styles.modalContent} onClick={(e) => e.stopPropagation()}>
  // [Logic Hidden]
                onClick={() => setShowImageModal(false)}
  // [Logic Hidden]
              {[...Array(20)].map((_, i) => (
  // [Logic Hidden]
              {[...Array(20)].map((_, i) => (
  // [Logic Hidden]
                onClick={() => navigate('/profile-setup', { state: { isEditing: true } })}
  // [Logic Hidden]
              {(() => {
  // [Logic Hidden]
                // Always use computed daily progress so first render starts at 0%.
                {weeklyProgress.map((item, i) => (
  // [Logic Hidden]
                  ].map(({ label, name }) => {
  // [Logic Hidden]
            {(() => {
  // [Logic Hidden]
            {(() => {
  // [Logic Hidden]
                  {['all', 'workout', 'meal', 'sleep', 'water'].map((m) => (
  // [Logic Hidden]
                      onClick={() => setChartMode(m)}
  // [Logic Hidden]
                  {['week', 'month'].map((p) => (
  // [Logic Hidden]
                      onClick={() => setChartPeriod(p)}
  // [Logic Hidden]
              {(() => {
  // [Logic Hidden]
                const todaysHistory = recentHistory.filter(h => {
  // [Logic Hidden]
                  // fallback: entries without timestamp (legacy) — try the old heuristic
              todaysHistory.map((h, i) => (
  // [Logic Hidden]
            {notifications.map((notification) => (
  // [Logic Hidden]
                    onClick={() => dismissNotification(notification.id)}
  // [Logic Hidden]
// Helper function to calculate dynamic water goal in Liters
  // [Logic Hidden]
const getDynamicWaterGoal = (weightKg = 70, sleepHours = 0, workoutCompleted = false) => {
  // [Logic Hidden]
  // Base requirement: 33ml per kg
  // +500ml on workout days
  // +250ml if sleep is poor (< 7 hours)
```

## frontend\src\pages\DashboardActionIdeas.jsx
```javascript
function DashboardActionIdeas() {
  // [Logic Hidden]
  const score = useMemo(() => {
  // [Logic Hidden]
  const stepStatus = useMemo(() => {
  // [Logic Hidden]
  const premiumCleanCard = useMemo(() => {
  // [Logic Hidden]
    () => [
  // [Logic Hidden]
  const coachInsight = useMemo(() => {
  // [Logic Hidden]
  const ringMetrics = useMemo(() => {
  // [Logic Hidden]
  const levelData = useMemo(() => {
  // [Logic Hidden]
    () => ['Strength', 'Mobility', 'Endurance', 'Sleep', 'Focus', 'Recovery'],
  // [Logic Hidden]
  const radarMetrics = useMemo(() => {
  // [Logic Hidden]
  const toRadarPoint = useCallback((idx, value, radius = 72, cx = 90, cy = 90) => {
  // [Logic Hidden]
    () => radarMetrics.map((v, idx) => toRadarPoint(idx, v)).join(' '),
  // [Logic Hidden]
  const weakestRadarAxis = useMemo(() => {
  // [Logic Hidden]
    /* Idea 33: Universal Adaptive CSS */
          onClick={() => navigate('/dashboard')}
  // [Logic Hidden]
            {Object.entries(STATUS_META).map(([key, value]) => {
  // [Logic Hidden]
                  onClick={() => setStatus(key)}
  // [Logic Hidden]
              {STEP_TITLES.map((title, i) => {
  // [Logic Hidden]
              ].map((item, idx) => {
  // [Logic Hidden]
                {levelData.milestones.map((m) => (
  // [Logic Hidden]
                {[25, 50, 75, 100].map((scale) => (
  // [Logic Hidden]
                    points={radarAxes.map((_, idx) => toRadarPoint(idx, scale)).join(' ')}
  // [Logic Hidden]
                {radarAxes.map((axis, idx) => {
  // [Logic Hidden]
                {radarMetrics.map((v, idx) => {
  // [Logic Hidden]
              {Array.from({ length: 28 }).map((_, i) => {
  // [Logic Hidden]
              ].map((item) => (
  // [Logic Hidden]
              {[30, 45, 60, 20, 80, 50, 0].map((val, i) => {
  // [Logic Hidden]
              {premiumCleanCard.chips.map((chip) => (
  // [Logic Hidden]
              {startActionAlternatives.map((item) => {
  // [Logic Hidden]
```

## frontend\src\pages\ForgotPassword.jsx
```javascript
function ForgotPassword() {
  // [Logic Hidden]
  const handleRequest = async (event) => {
  // [Logic Hidden]
        setConfirmData((prev) => ({
  // [Logic Hidden]
        setConfirmData((prev) => ({
  // [Logic Hidden]
  const handleConfirmChange = (event) => {
  // [Logic Hidden]
    setConfirmData((prev) => ({ ...prev, [name]: value }));
  // [Logic Hidden]
  const handleConfirm = async (event) => {
  // [Logic Hidden]
      setTimeout(() => {
  // [Logic Hidden]
  const handleUseDifferentEmail = () => {
  // [Logic Hidden]
                        onChange={(event) => setRequestEmail(event.target.value)}
  // [Logic Hidden]
                        onClick={() => setShowPasswords((prev) => !prev)}
  // [Logic Hidden]
```

## frontend\src\pages\Login.jsx
```javascript
const clearUserScopedCache = () => {
  // [Logic Hidden]
  scopedKeys.forEach((k) => localStorage.removeItem(k));
  // [Logic Hidden]
const syncUserSession = (newUser) => {
  // [Logic Hidden]
function Login({ setIsAuthenticated }) {
  // [Logic Hidden]
  useEffect(() => {
  // [Logic Hidden]
      // Don't blindly redirect to /dashboard — a new user may have a token
      // but no profile data yet. Check profile completeness first.
        .then(({ data }) => {
  // [Logic Hidden]
        .catch(() => {
  // [Logic Hidden]
          // Token is invalid/expired — stay on login
    loadGoogleSDK('google-signin-button', handleGoogleResponse, (errorMessage) => showError(errorMessage, 5000));
  // [Logic Hidden]
    // eslint-disable-next-line react-hooks/exhaustive-deps
  const handleGoogleResponse = async (response) => {
  // [Logic Hidden]
  const handleChange = (e) => {
  // [Logic Hidden]
  const handleSubmit = async (e) => {
  // [Logic Hidden]
            // Require goal, age AND weight — a new user won't have all three
                    onClick={() => setShowPassword(!showPassword)}
  // [Logic Hidden]
```

## frontend\src\pages\Nutrition.jsx
```javascript
// Local-timezone date string helper is now imported from storage.js
function Nutrition() {
  // [Logic Hidden]
  // Swap state
  const isMealUnlocked = (mealType, dayIdx) => {
  // [Logic Hidden]
        (meal) => String(meal?.meal_type || "").toLowerCase() === prevMealType
  // [Logic Hidden]
  const getUnlockMessage = (mealType) => {
  // [Logic Hidden]
  useEffect(() => {
  // [Logic Hidden]
    // eslint-disable-next-line react-hooks/exhaustive-deps
  // ✅ BUG FIX 2: Backend Persistence to Frontend
  useEffect(() => {
  // [Logic Hidden]
    mealHistory.forEach((dayEntry) => {
  // [Logic Hidden]
      const dayPlan = weeklyPlan.days.find((d) => d.date === dayEntry.date);
  // [Logic Hidden]
      Object.values(dayEntry.meals).forEach((mealData) => {
  // [Logic Hidden]
        const planMeal = dayPlan.meals.find((m) => m.meal_type === mealData.meal_type);
  // [Logic Hidden]
          // Backend saved individual food items — match by name
          mealData.foods.forEach((food) => {
  // [Logic Hidden]
            const planFood = planMeal.foods.find((f) => f.name === food.name);
  // [Logic Hidden]
          // ✅ FIX: Backend only saves meal totals (foods: []), but the meal IS locked.
          // Synthetically mark ALL plan foods for this meal as checked to restore tick UI.
          planMeal.foods.forEach((planFood) => {
  // [Logic Hidden]
  const getTodayWorkoutIntensity = (workoutPlan = []) => {
  // [Logic Hidden]
    const todayPlan = workoutPlan.find((d) => (d?.day_of_week ?? -1) === todayIdx) || workoutPlan[todayIdx];
  // [Logic Hidden]
    const totalSets = exercises.reduce((sum, ex) => {
  // [Logic Hidden]
  const getWorkoutPlanForNutrition = async (profile) => {
  // [Logic Hidden]
    // Do not block nutrition load on workout generation when cache is missing.
    // Use moderate intensity now; warm workout cache in background for next visit.
    generateWorkout(profile).then((workoutResponse) => {
  // [Logic Hidden]
    }).catch((err) => {
  // [Logic Hidden]
  const isTodayRestDay = () => {
  // [Logic Hidden]
      const todayPlan = workoutPlan.find((d) => (d?.day_of_week ?? -1) === todayIdx) || workoutPlan[todayIdx];
  // [Logic Hidden]
      // 1. Explicit type from backend engine
      // 2. Focus field
      // 3. Label / note
  /* ──────────────────────────────────────────
   *  FETCH — builds 7-day plan from backend
   *  ✅ FIX 7: Date-aware caching with profile hash
   *  ✅ FIX 8: Cache invalidation on profile change
   * ────────────────────────────────────────── */
  const fetchNutritionPlan = async () => {
  // [Logic Hidden]
      // ✅ FIX 7+8: Check if we have a valid cached plan for today with same profile
      // ✅ PA-7: Use LOCAL timezone for consistent date across pages
        // Use cached plan — no network request needed
      // Clear invalidation flag since we're fetching fresh
        // Save daily target
        // Build 7-day display from weekly_plan the backend now returns
          // Get the matching day from the backend weekly plan
          // Build meals array from the backend day object
            const foods = items.map((item, idx) => ({
  // [Logic Hidden]
              calories: Math.round(foods.reduce((s, f) => s + f.calories, 0)),
  // [Logic Hidden]
              protein_g: Math.round(foods.reduce((s, f) => s + f.protein_g, 0) * 10) / 10,
  // [Logic Hidden]
              carbs_g: Math.round(foods.reduce((s, f) => s + f.carbs_g, 0) * 10) / 10,
  // [Logic Hidden]
              fat_g: Math.round(foods.reduce((s, f) => s + f.fat_g, 0) * 10) / 10,
  // [Logic Hidden]
          // Daily totals = sum of all meal totals
            calories: Math.round(meals.reduce((s, m) => s + m.totals.calories, 0)),
  // [Logic Hidden]
            protein_g: Math.round(meals.reduce((s, m) => s + m.totals.protein_g, 0) * 10) / 10,
  // [Logic Hidden]
            carbs_g: Math.round(meals.reduce((s, m) => s + m.totals.carbs_g, 0) * 10) / 10,
  // [Logic Hidden]
            fat_g: Math.round(meals.reduce((s, m) => s + m.totals.fat_g, 0) * 10) / 10,
  // [Logic Hidden]
        // ✅ FIX: Re-run loadHistory to tick off the newly generated food items
        // using the backend completed meal history (in case the plan regenerated).
  /* ──────────────────────────────────────────
   *  CHECKING / LOCKING meals
   * ────────────────────────────────────────── */
  const loadHistory = async () => {
  // [Logic Hidden]
      // ✅ Populate lockedMeals directly from backed up daily history
      const todayEntry = historyData.find(d => d.date === todayDate);
  // [Logic Hidden]
        Object.values(todayEntry.meals).forEach(mealData => {
  // [Logic Hidden]
              // ✅ FIX: Backfill checkedFoods for this locked meal using the current
              // nutrition plan from localStorage cache. The backend only stores meal totals
              // (not individual food items), so we reconstruct from the local plan.
                // StorageKeys.NUTRITION_CACHE = 'nutritionPlan'
                    (m) => String(m.meal_type || '').toLowerCase() === mealTypeKey
  // [Logic Hidden]
                    planMeal.foods.forEach((food) => {
  // [Logic Hidden]
                // Non-critical — checkedFoods will remain partially populated
      // Fallback
  const loadCheckedFoods = () => setCheckedFoods(safeJSONParse("checkedFoods", {}));
  // [Logic Hidden]
  const handleCheckFood = (foodId, mealName, mealType, dayIdx) => {
  // [Logic Hidden]
    // Check if ALL items in this meal are now ticked
        (m) => m.name === mealName || String(m.meal_type || '').toLowerCase() === normalizedMealType
  // [Logic Hidden]
        const allChecked = meal.foods.every(f => newChecked[`${today}-${f.id}`]);
  // [Logic Hidden]
            foods: meal.foods.map(f => ({
  // [Logic Hidden]
          let dateEntry = updatedHistory.find(e => e.date === today);
  // [Logic Hidden]
          dateEntry.total_calories = Object.values(dateEntry.meals).reduce((s, m) => s + (m.calories || 0), 0);
  // [Logic Hidden]
          dateEntry.total_protein = Object.values(dateEntry.meals).reduce((s, m) => s + (m.protein || 0), 0);
  // [Logic Hidden]
          dateEntry.total_carbs = Object.values(dateEntry.meals).reduce((s, m) => s + (m.carbs || 0), 0);
  // [Logic Hidden]
          dateEntry.total_fat = Object.values(dateEntry.meals).reduce((s, m) => s + (m.fat || 0), 0);
  // [Logic Hidden]
          updatedHistory.sort((a, b) => b.date.localeCompare(a.date));
  // [Logic Hidden]
            .catch(err => console.error("Error saving meal history to db", err));
  // [Logic Hidden]
          setExpandedDates(prev => ({ ...prev, [today]: true }));
  // [Logic Hidden]
          const mealsCountLocal = ['breakfast', 'lunch', 'dinner'].filter(t => Boolean(dateEntry.meals?.[t])).length;
  // [Logic Hidden]
          // Sync with Node Database & consume todayTotals for Dashboard macro update
          }).then(res => {
  // [Logic Hidden]
            // ✅ BUG FIX: Consume todayTotals from backend to signal Dashboard
              // Count how many of breakfast/lunch/dinner are done so far in this session
              const mealsCount = ['breakfast', 'lunch', 'dinner'].filter(t => Boolean(dateEntry.meals?.[t])).length;
  // [Logic Hidden]
              // Direct activity logging backup
              }).catch(err => console.error("Failed to log activity backup on frontend", err));
  // [Logic Hidden]
          }).catch(err => console.error("Failed to sync meal to node db", err));
  // [Logic Hidden]
          // ✅ FIX 6: Snacks are OPTIONAL for day completion
          // Only Breakfast + Lunch + Dinner are required — Snack is bonus calories
          const allMealsDone = requiredMeals.every((mealType) => Boolean(dateEntry.meals?.[mealType]));
  // [Logic Hidden]
          // Keep trend/graph state in sync after every completed meal.
          }).catch((err) => console.error("Failed to sync trends after meal update", err));
  // [Logic Hidden]
  /* ──────────────────────────────────────────
   *  SWAP — fetches alternatives from backend
   * ────────────────────────────────────────── */
  const openSwapModal = async (food, mealType, dayIdx) => {
  // [Logic Hidden]
  const confirmSwap = () => {
  // [Logic Hidden]
    const updatedDays = weeklyPlan.days.map((day, i) => {
  // [Logic Hidden]
      const updatedMeals = day.meals.map(meal => {
  // [Logic Hidden]
        const updatedFoods = meal.foods.map(f => {
  // [Logic Hidden]
          calories: Math.round(updatedFoods.reduce((s, f) => s + f.calories, 0)),
  // [Logic Hidden]
          protein_g: Math.round(updatedFoods.reduce((s, f) => s + f.protein_g, 0) * 10) / 10,
  // [Logic Hidden]
          carbs_g: Math.round(updatedFoods.reduce((s, f) => s + f.carbs_g, 0) * 10) / 10,
  // [Logic Hidden]
          fat_g: Math.round(updatedFoods.reduce((s, f) => s + f.fat_g, 0) * 10) / 10,
  // [Logic Hidden]
        calories: Math.round(updatedMeals.reduce((s, m) => s + m.totals.calories, 0)),
  // [Logic Hidden]
        protein_g: Math.round(updatedMeals.reduce((s, m) => s + m.totals.protein_g, 0) * 10) / 10,
  // [Logic Hidden]
        carbs_g: Math.round(updatedMeals.reduce((s, m) => s + m.totals.carbs_g, 0) * 10) / 10,
  // [Logic Hidden]
        fat_g: Math.round(updatedMeals.reduce((s, m) => s + m.totals.fat_g, 0) * 10) / 10,
  // [Logic Hidden]
  /* ──────────────────────────────────────────
   *  RENDER
   * ────────────────────────────────────────── */
  // ✅ BUG FIX 4: Logout confirmation handler for Navbar
  const handleLogout = () => {
  // [Logic Hidden]
  const selectedDayConsumedTotals = (() => {
  // [Logic Hidden]
    // Build a local fallback from current tick/lock state so refresh/relogin does not
    // temporarily show 0 before backend history sync completes.
    (selectedDay.meals || []).forEach((meal) => {
  // [Logic Hidden]
      (meal?.foods || []).forEach((food) => {
  // [Logic Hidden]
    // Removed unused history variables to pass lint
                onClick={() => setShowHistory(true)}
  // [Logic Hidden]
          onConfirm={() => {
  // [Logic Hidden]
          onCancel={() => setConfirmDialog({ show: false, message: "", onConfirm: null })}
  // [Logic Hidden]
                onClick={() => setShowHistory(true)}
  // [Logic Hidden]
          onConfirm={() => {
  // [Logic Hidden]
          onCancel={() => setConfirmDialog({ show: false, message: "", onConfirm: null })}
  // [Logic Hidden]
              onClick={() => setShowHistory(true)}
  // [Logic Hidden]
          {weeklyPlan.days.map((day, index) => (
  // [Logic Hidden]
            <div key={day.date} onClick={() => setSelectedDayIndex(index)} className="day-card-hover" style={{ ...styles.dayCard, ...(selectedDayIndex === index ? styles.dayCardSelected : {}), ...(day.is_today ? styles.dayCardToday : {}), opacity: day.is_future && selectedDayIndex !== index ? 0.6 : 1 }}>
  // [Logic Hidden]
          {selectedDay?.meals.map((meal, mealIndex) => {
  // [Logic Hidden]
            const checkedCount = meal.foods.filter(f => checkedFoods[`${selectedDay.date}-${f.id}`] || isCompleted).length;
  // [Logic Hidden]
          onClose={() => setShowHistory(false)} today={today}
  // [Logic Hidden]
        <div style={styles.swapModal} onClick={() => setSwapModal({ show: false, food: null, mealType: null, dayIndex: null })}>
  // [Logic Hidden]
          <div style={styles.swapModalCard} onClick={e => e.stopPropagation()}>
  // [Logic Hidden]
              <button onClick={() => setSwapModal({ show: false, food: null, mealType: null, dayIndex: null })} style={{ background: "var(--app-border)", borderRadius: "50%", width: "36px", height: "36px", display: "flex", alignItems: "center", justifyContent: "center", color: "var(--app-text-muted)", border: "1px solid var(--app-border)", fontSize: "16px", cursor: "pointer", transition: "all 0.2s ease" }} className="icon-hover">✕</button>
  // [Logic Hidden]
                  swapOptions.map((option, i) => {
  // [Logic Hidden]
                    <div key={i} onClick={() => setSelectedSwap(option)} style={{
  // [Logic Hidden]
              <button onClick={() => setSwapModal({ show: false, food: null, mealType: null, dayIndex: null })} style={{ flex: 1, padding: "14px", borderRadius: "14px", background: "var(--app-surface2)", color: "var(--app-text)", border: "1px solid var(--app-border)", fontWeight: "700", cursor: "pointer", fontSize: "14px" }}>Cancel</button>
  // [Logic Hidden]
        onConfirm={() => {
  // [Logic Hidden]
            // Default action: logout
        onCancel={() => setConfirmDialog({ show: false, message: "", onConfirm: null })}
  // [Logic Hidden]
function MacroStat({ value, label, color, icon }) {
  // [Logic Hidden]
function MealCard({ meal, isLocked, isSequenceLocked, unlockMessage, checkedFoods, tickTimes, today, checkedCount, totalCount, onCheckFood, onSwapFood, dayIndex, isFutureDay }) {
  // [Logic Hidden]
        {meal.foods.map((food) => {
  // [Logic Hidden]
              <div onClick={() => !isDisabled && onCheckFood(food.id, meal.name, meal.meal_type, dayIndex)} style={{
  // [Logic Hidden]
              <button className="swap-btn-hover" onClick={() => !isDisabled && onSwapFood(food, meal.meal_type, dayIndex)} disabled={isDisabled} style={{ ...styles.swapBtn, ...(isDisabled ? { opacity: 0.3, cursor: "not-allowed" } : {}) }}>🔄</button>
  // [Logic Hidden]
function HistoryPanel({ mealHistory, expandedDates, setExpandedDates, expandedMeals, setExpandedMeals, onClose, today }) {
  // [Logic Hidden]
        mealHistory.map((dayEntry) => {
  // [Logic Hidden]
              <div onClick={() => setExpandedDates(prev => ({ ...prev, [dayEntry.date]: !prev[dayEntry.date] }))} style={{
  // [Logic Hidden]
                  {["breakfast", "lunch", "dinner", "snack"].map((mealType) => {
  // [Logic Hidden]
                        <div onClick={() => setExpandedMeals(prev => ({ ...prev, [mealKey]: !prev[mealKey] }))} style={{
  // [Logic Hidden]
                            {(meal.foods || []).map((food, fIdx) => (
  // [Logic Hidden]
function getFallbackServing(nameStr, calValue) {
  // [Logic Hidden]
  // 1. Eggs
  // 2. Roti / Chapati / Paratha / Naan / Bread
  // 3. Idli / Dosa / Uttapam / Vada
  // 4. Whole fruits
  // 5. Beverages & Liquid Shakes (ml/glass)
  // 6. Tea & Coffee
  // 7. Dal, Sambar, Kadhi, Soups, Salad, Yogurt, Raita
  // 8. Rice, Pulao, Biryani, Noodles, Pasta
  // 9. Protein Bars
  // 10. Nuts & Seeds
  // Fallback to Grams
```

## frontend\src\pages\ProfileSetup.jsx
```javascript
// --- STYLES ---
  // NEW: Cancel Button Style
const MultiSelect = ({ name, options, value, onChange, isOpen, onToggle, isNoneChecked }) => {
  // [Logic Hidden]
          {options.map((option, index) => {
  // [Logic Hidden]
                onMouseEnter={(e) => !isOptionDisabled && (e.currentTarget.style.background = '#f8fafc')}
  // [Logic Hidden]
                onMouseLeave={(e) => (e.currentTarget.style.background = isChecked ? '#f8fafc' : 'transparent')}
  // [Logic Hidden]
                  onChange={(e) => onChange(e, name)}
  // [Logic Hidden]
          {value.map(item => <div key={item} style={styles.selectedTag}>✓ {item}</div>)}
  // [Logic Hidden]
function ProfileSetup() {
  // [Logic Hidden]
  // State for regeneration timing dialog
  // Function to clear workout plan cache to force regeneration
  const _clearWorkoutPlanCache = () => {
  // [Logic Hidden]
      // Bug #5 Fix: Use the exact keys Workout.jsx reads to ensure invalidation works.
      // Legacy keys (in case any old code wrote them)
  // Function to clear meal plan cache to force regeneration
  const _clearMealPlanCache = () => {
  // [Logic Hidden]
      // Bug #5 Fix: Use the exact keys Nutrition.jsx reads to ensure cache invalidation works.
      // Volatile daily state that belongs to the old plan
      // Legacy keys (in case any old code wrote them)
  const getMondayIndexToday = () => {
  // [Logic Hidden]
  const getPlanItemIndex = (item, fallbackIdx) => {
  // [Logic Hidden]
  const mergeWorkoutPlanFromToday = (currentPlan, regeneratedPlan) => {
  // [Logic Hidden]
    (Array.isArray(currentPlan) ? currentPlan : []).forEach((item, i) => {
  // [Logic Hidden]
    regeneratedPlan.forEach((item, i) => {
  // [Logic Hidden]
  useEffect(() => {
  // [Logic Hidden]
    // 1. BLOCK BACK BUTTON
    const handlePopState = () => {
  // [Logic Hidden]
    // 2. LOAD EXISTING DATA
    const loadData = async () => {
  // [Logic Hidden]
            // Determine if user is editing based on existing profile data
            // If editing, prefill form
            // Check if user has Google avatar
    // 3. LOAD AVATAR
    return () => window.removeEventListener('popstate', handlePopState);
  // [Logic Hidden]
    // eslint-disable-next-line react-hooks/exhaustive-deps
  useEffect(() => {
  // [Logic Hidden]
    const handleClickOutside = (event) => {
  // [Logic Hidden]
    return () => document.removeEventListener('mousedown', handleClickOutside);
  // [Logic Hidden]
  const handleImageUpload = (event) => {
  // [Logic Hidden]
      reader.onloadend = () => {
  // [Logic Hidden]
  const handleRemoveImage = (e) => {
  // [Logic Hidden]
  const handleChange = (e) => {
  // [Logic Hidden]
  const handleCheckbox = (e, type) => {
  // [Logic Hidden]
    // Treat 'None (Bodyweight Only)' and 'None' as mutually-exclusive "none" options
      updatedList = checked ? [value] : updatedList.filter(item => !noneValues.includes(item));
  // [Logic Hidden]
      // Remove any "none" selection when a real equipment item is checked
      updatedList = updatedList.filter(item => !noneValues.includes(item));
  // [Logic Hidden]
      updatedList = checked ? [...updatedList, value] : updatedList.filter(item => item !== value);
  // [Logic Hidden]
  const handleSubmit = async (e) => {
  // [Logic Hidden]
    // Build profile update payload
    // Compare against server-loaded baseline profile, not cached local profile.
    // Check what changes affect workout regeneration
    // Priority 0 Bug 4 Fix: Use delta thresholds instead of naive equality.
    // Weight changes < 10 kg don't change exercise selection — only TDEE/meal plan.
    // Age changes < 5 years don't meaningfully change volume prescription.
    // If changes affect plans, ask timing for existing users.
    // No plan-impacting changes (e.g. name/avatar only), update directly without regeneration.
  /**
   * Handle regeneration timing choice
   */
  const handleRegenerateChoice = async (choice) => {
  // [Logic Hidden]
  /**
   * Perform the actual profile update
   * @param {Object} profileUpdate - The profile data to update
   * @param {string} timing - 'immediate' or 'next_week'
   */
  const performProfileUpdate = async (profileUpdate, timing, options = {}) => {
  // [Logic Hidden]
    // Priority 0 Bug 3 Fix: Clear localStorage caches BEFORE the API call.
    // Without this, Workout.jsx and Nutrition.jsx read the old 24-hr cached plan
    // even after the server has regenerated a new one.
      // ✅ CRITICAL FIX: Save profile to Node backend (port 5000 / MongoDB) FIRST.
      // The Dashboard reads from Node via getProfile(). If we skip this step,
      // the Dashboard sees no goal/weight and instantly redirects back to /profile-setup.
        // Call the Python backend to regenerate workout/nutrition plans
          onRetry: (attempt) => {
  // [Logic Hidden]
        // ✅ FIX 10: Invalidate nutrition cache so Nutrition page fetches fresh plan
        // Also set profile update timestamp for cross-page awareness
        // ✅ Persist regenerated nutrition plan with proper StorageKeys
        // Wrap raw plan in cache-compatible format that Nutrition.jsx expects
          // ✅ FIX PA-5: profileHash MUST match the format Nutrition.jsx uses at line 185:
          //    `${profile.weight}-${profile.height}-${profile.goal}-${profile.dietary_preference || ''}-${profile.age}`
          // Normalize multiple backend nutrition shapes to the frontend cache shape.
          // Supported: { days: [...] }, { meals: [...] }, { weekly_plan: { Monday: {...} } }
            normalizedDays = dayNames.map((dayName, idx) => {
  // [Logic Hidden]
              const meals = ['breakfast', 'lunch', 'dinner', 'snack'].map((mealType) => {
  // [Logic Hidden]
                const foods = items.map((item, foodIdx) => ({
  // [Logic Hidden]
                  calories: foods.reduce((sum, f) => sum + (Number(f.calories) || 0), 0),
  // [Logic Hidden]
                  protein_g: Math.round(foods.reduce((sum, f) => sum + (Number(f.protein_g) || 0), 0) * 10) / 10,
  // [Logic Hidden]
                  carbs_g: Math.round(foods.reduce((sum, f) => sum + (Number(f.carbs_g) || 0), 0) * 10) / 10,
  // [Logic Hidden]
                  fat_g: Math.round(foods.reduce((sum, f) => sum + (Number(f.fat_g) || 0), 0) * 10) / 10,
  // [Logic Hidden]
                calories: meals.reduce((sum, meal) => sum + (Number(meal?.totals?.calories) || 0), 0),
  // [Logic Hidden]
                protein_g: Math.round(meals.reduce((sum, meal) => sum + (Number(meal?.totals?.protein_g) || 0), 0) * 10) / 10,
  // [Logic Hidden]
                carbs_g: Math.round(meals.reduce((sum, meal) => sum + (Number(meal?.totals?.carbs_g) || 0), 0) * 10) / 10,
  // [Logic Hidden]
                fat_g: Math.round(meals.reduce((sum, meal) => sum + (Number(meal?.totals?.fat_g) || 0), 0) * 10) / 10,
  // [Logic Hidden]
          // ✅ PA-7: Use local timezone date, same format as Dashboard/Nutrition
        // Update user data in localStorage
        // Show success notification
        // Redirect to dashboard after short delay
        setTimeout(() => { navigate('/dashboard'); }, 1500);
  // [Logic Hidden]
          setTimeout(() => navigate('/'), 2000);
  // [Logic Hidden]
        <button onClick={() => navigate('/dashboard')} style={styles.cancelBtn}>
  // [Logic Hidden]
        <button onClick={() => { logoutSafe(); navigate('/'); }} style={styles.cancelBtn}>
  // [Logic Hidden]
                  <div style={styles.avatarImage} onClick={() => fileInputRef.current.click()}>
  // [Logic Hidden]
                <label style={styles.uploadLabel} onClick={() => fileInputRef.current.click()}>
  // [Logic Hidden]
                    <input style={styles.input} type="text" value={firstName} onChange={(e) => setFirstName(e.target.value)} placeholder="John" required />
  // [Logic Hidden]
                    <input style={styles.input} type="text" value={lastName} onChange={(e) => setLastName(e.target.value)} placeholder="Doe" />
  // [Logic Hidden]
                      // ── Essential (bodyweight baseline) ────────────────
                      // ── Upgrade Kit ────────────────────────────────────
                      // ── Accessories ────────────────────────────────────
                    onToggle={() => setOpenDropdown(openDropdown === 'equipment' ? null : 'equipment')}
  // [Logic Hidden]
                    onToggle={() => setOpenDropdown(openDropdown === 'allergies' ? null : 'allergies')}
  // [Logic Hidden]
                    onToggle={() => setOpenDropdown(openDropdown === 'body_issues' ? null : 'body_issues')}
  // [Logic Hidden]
                onClick={() => handleRegenerateChoice('next_week')}
  // [Logic Hidden]
                onClick={() => handleRegenerateChoice('immediate')}
  // [Logic Hidden]
              onClick={() => handleRegenerateChoice('cancel')}
  // [Logic Hidden]
```

## frontend\src\pages\Register.jsx
```javascript
const clearUserScopedCache = () => {
  // [Logic Hidden]
    scopedKeys.forEach((k) => localStorage.removeItem(k));
  // [Logic Hidden]
const syncUserSession = (newUser) => {
  // [Logic Hidden]
const Register = () => {
  // [Logic Hidden]
    // Initialize Google SDK after component mounts
    useEffect(() => {
  // [Logic Hidden]
        loadGoogleSDK('google-signup-button', handleGoogleResponse, (errorMessage) => {
  // [Logic Hidden]
            // Hide notification after 5 seconds
            setTimeout(() => {
  // [Logic Hidden]
        // eslint-disable-next-line react-hooks/exhaustive-deps
    const handleGoogleResponse = async (response) => {
  // [Logic Hidden]
            // Send the Google token to our backend
            // Save token and user info
            // Since Google users are already registered, redirect to profile setup or dashboard
    const handleChange = (e) => {
  // [Logic Hidden]
    const handleRegister = async (e) => {
  // [Logic Hidden]
            // 1. Call Node.js Backend
            // 2. SUCCESS: Show stylish message instead of alert
            // 3. Wait 2 seconds, then go to Login
            setTimeout(() => {
  // [Logic Hidden]
                                        onFocus={() => setFocused('fullname')}
  // [Logic Hidden]
                                        onBlur={() => setFocused(null)}
  // [Logic Hidden]
                                        onFocus={() => setFocused('email')}
  // [Logic Hidden]
                                        onBlur={() => setFocused(null)}
  // [Logic Hidden]
                                        onFocus={() => setFocused('password')}
  // [Logic Hidden]
                                        onBlur={() => setFocused(null)}
  // [Logic Hidden]
                                        onClick={() => setShowPassword(!showPassword)}
  // [Logic Hidden]
```

## frontend\src\pages\Workout.jsx
```javascript
// Define full weekday names array
// --- STYLES (Your Exact Styles Preserved) ---
// History dynamically fetched from node
const getTodayIdx = () => {
  // [Logic Hidden]
  // Use IST to stay aligned with date handling across the app/backend.
const isRestDay = (day) => {
  // [Logic Hidden]
  // 1. Explicit type field from backend engine (most reliable)
  // 2. Focus field containing 'rest' (e.g. "Rest Day", "Rest", "Active Recovery")
  // 3. Day label or note containing 'rest'
  // 4. No exercises AND type is not 'workout' → treat as rest
const getDayStatus = (day, todayIdx, completedIds = new Set()) => {
  // [Logic Hidden]
  // Days before registration are explicitly marked as "past" by the backend.
const findNextWorkoutDayIndex = (plan, todayIdx) => {
  // [Logic Hidden]
const getFutureOriginalRestDays = (plan, sourceDayIdx, todayIdx) => {
  // [Logic Hidden]
  return safe.filter((day) => {
  // [Logic Hidden]
const getWeekStartDateIso = () => {
  // [Logic Hidden]
const buildWeekMetadataFromPlan = (weeklyPlan = [], existingMetadata = null) => {
  // [Logic Hidden]
  const currentCounts = plan.reduce((acc, day) => {
  // [Logic Hidden]
  const originalCounts = plan.reduce((acc, day) => {
  // [Logic Hidden]
const formatSwapTimestamp = (value) => {
  // [Logic Hidden]
const Workout = () => {
  // [Logic Hidden]
  // State declarations
  const [weekMetadata, setWeekMetadata] = useState(() => getFromStorage(StorageKeys.WORKOUT_WEEK_METADATA, null));
  // [Logic Hidden]
  // ✅ FIX: Track completed day indices in React state, hydrated from backend on mount.
  // Old approach read localStorage keys ('workout_done_Monday') which reset on every new browser session.
  // Posture processing state
  // ✅ FIX: Pre-hydrate exerciseStatus from localStorage so red ticks survive refresh without a network call.
  const [exerciseStatus, setExerciseStatus] = useState(() => {
  // [Logic Hidden]
      // Clear stale cache from a different day — don't show yesterday's skips today
  // Priority 1: variation suggestion returned by /api/workout/session-result
  // Bug #2 Fix: Pose detector loading state
  useEffect(() => {
  // [Logic Hidden]
    const handleResize = () => setViewportWidth(window.innerWidth);
  // [Logic Hidden]
    return () => window.removeEventListener('resize', handleResize);
  // [Logic Hidden]
  const showConfirmDialog = useCallback((message, onConfirm) => {
  // [Logic Hidden]
  const handleConfirm = () => {
  // [Logic Hidden]
  const handleCancelConfirm = () => {
  // [Logic Hidden]
  const normalizeMediaUrl = (url) => {
  // [Logic Hidden]
    // Convert giphy page URLs to direct media links.
  const getExerciseMediaCandidates = (exercise) => {
  // [Logic Hidden]
    return raw.map(normalizeMediaUrl).filter((trimmed) => {
  // [Logic Hidden]
  // A plan is renderable if it has at least one exercise. Exercises without a GIF
  // show a styled placeholder — that is intentional and correct. We only reject
  // plans that are completely empty or structurally malformed.
  const planHasRenderableMedia = (candidatePlan) => {
  // [Logic Hidden]
  const isVideoUrl = (url) => {
  // [Logic Hidden]
    return ['.mp4', '.webm', '.ogg', '.mov', '.m3u8'].some((ext) => clean.endsWith(ext));
  // [Logic Hidden]
  // Issue #3 – detect YouTube embed URLs returned by youtube_service.py
  const isYouTubeUrl = (url) => {
  // [Logic Hidden]
  const getMovementCue = (exerciseName = '') => {
  // [Logic Hidden]
  const parseDurationToSeconds = useCallback((value) => {
  // [Logic Hidden]
    const nums = matches.map((n) => parseInt(n, 10)).filter((n) => !Number.isNaN(n));
  // [Logic Hidden]
  const getTargetSets = (exercise) => {
  // [Logic Hidden]
  const getTargetReps = (exercise) => {
  // [Logic Hidden]
  const getRestSeconds = (exercise) => {
  // [Logic Hidden]
  const getExerciseDurationSeconds = useCallback((exercise) => {
  // [Logic Hidden]
  const getExerciseStatusKey = (exercise) => {
  // [Logic Hidden]
  const isPoseTrackableExercise = useCallback((exercise) => {
  // [Logic Hidden]
    if (nonTrackableKeywords.some((kw) => lower.includes(kw))) {
  // [Logic Hidden]
  const exerciseNeedsCamera = useCallback((exercise) => {
  // [Logic Hidden]
  const isTimedExercise = useCallback((exercise) => {
  // [Logic Hidden]
  const formatDurationClock = (seconds) => {
  // [Logic Hidden]
  // Shown when an exercise has no GIF/image available (blacklisted or failed to load).
  const renderExerciseNoGifPlaceholder = (exerciseName) => {
  // [Logic Hidden]
    const emoji = (() => {
  // [Logic Hidden]
  const handleMediaError = () => {
  // [Logic Hidden]
    setMediaUrlIndex((prev) => prev + 1);
  // [Logic Hidden]
  const renderActiveExerciseMedia = () => {
  // [Logic Hidden]
    // If the exercise is explicitly marked as having no GIF (blacklisted on backend),
    // show the no-GIF placeholder immediately without attempting to load any image.
    // Issue #3 – YouTube embed (from youtube_service.py fallback)
  useEffect(() => {
  // [Logic Hidden]
  const saveLog = async (name, details, dayName = '') => {
  // [Logic Hidden]
      // ✅ FIX: Store both ISO timestamp AND local date string.
      // `date` (ISO) is used for display; `dateStr` (YYYY-MM-DD local) is used for today-matching
      // in fetchHistory so it works correctly in all timezones (not just UTC).
    // Save to node backend instead of localstorage
  useEffect(() => {
  // [Logic Hidden]
  // ===== HELPER FUNCTIONS =====
  /**
   * Create fallback workout plan if backend returns empty
   */
  const createFallbackPlan = () => {
  // [Logic Hidden]
    return dayNames.map((day, idx) => ({
  // [Logic Hidden]
  /**
   * Normalize plan to always have 7 days
   */
  const normalizeToSevenDays = (plan) => {
  // [Logic Hidden]
    // Pad with rest days if less than 7
    // Trim if more than 7
  useEffect(() => {
  // [Logic Hidden]
    // Track if component is mounted to prevent state updates after unmount
    // Preload pose assets when user reaches workout page for faster camera startup.
    preloadPoseAssets().catch((err) => {
  // [Logic Hidden]
    const fetchWorkoutPlan = async (forceRefresh = false, profileData = null) => {
  // [Logic Hidden]
      const tryLoadPersistedPlan = async (reason = 'normal') => {
  // [Logic Hidden]
        // Authentication is handled via HttpOnly cookies (SEC-1)
        // ✅ FIX: Use fresh profile from API instead of stale localStorage.user
        // localStorage.user only has {id, name, email} — no fitness profile fields!
        // **Check if cached plan exists and is not expired**
        // Always hydrate immediately from any cached plan for fast first paint.
          // Cache valid for 24 hours
        // Try reading already persisted weekly plan first. This avoids blank workout pages
        // after relogin when generation is rate-limited or temporarily unavailable.
        // **Fetch new plan from server using FULL profile data**
        // ===== VALIDATE RESPONSE STRUCTURE =====
        // Backend returns: { success: true, workout: [...], exercises_count: number }
        // Check for workout array (could be at response.data.workout OR response.data.data.workout)
          // ✅ Correct structure: { success: true, workout: [...] }
          // Fallback for alternative structure: { success: true, data: { weekly_plan: [...] } }
        // Validate workout plan is not empty
          // Don't throw - use fallback
        // Validate plan has 7 days
          // **Cache the new plan**
        // Classify error for better user feedback
          // Rate limited - show retry_after time
          // Don't show error popup for rate limiting - just log it
          // Network error - backend not reachable
          // For rate limiting, just log without showing error popup
    const checkAndFetchPlan = async () => {
  // [Logic Hidden]
        // Always fetch profile first to get latest data
        // Bug #5 fix: use safe JSON parsing — corrupted localStorage won't crash the page.
        // Issue #1 – include registration day so the engine can generate a rolling week plan.
        // Normalize arrays for comparison (sort to ensure consistent order)
        const normalizeForComparison = (obj) => {
  // [Logic Hidden]
        const hasLegacyDemoData = Array.isArray(cachedPlan) && cachedPlan.some((day) =>
  // [Logic Hidden]
          Array.isArray(day?.exercises) && day.exercises.some((ex) => String(ex?.id || '').startsWith('demo-bicep-'))
  // [Logic Hidden]
          // ✅ FIX: Pass the fresh profile to fetchWorkoutPlan
    const fetchHistory = async () => {
  // [Logic Hidden]
        // ✅ FIX: Derive which day indices were completed TODAY from the backend.
        (Array.isArray(history) ? history : []).forEach((entry) => {
  // [Logic Hidden]
          // ✅ FIX: Hydrate per-exercise skip/complete status from backend on re-login.
          // The backend now stores exercise_status_by_name and per-exercise status in the exercises array.
          if (statusByName || exercisesWithStatus.some(e => e?.status)) {
  // [Logic Hidden]
            // Re-build exerciseStatus keyed by exercise status key (name|sets|reps|warmup)
            // We match by name since the full key isn't stored — close enough for display.
            exercisesWithStatus.forEach((ex) => {
  // [Logic Hidden]
                // Store under name as a simplified key (the status key formula needs sets/reps too,
                // but we fall back to a name-based match for display purposes)
              setExerciseStatus((prev) => ({ ...prev, ...restoredStatus }));
  // [Logic Hidden]
              // Also update localStorage cache
          // Fully completed days (not partial) add to completedDayIndices
    // Cleanup function to prevent state updates on unmount
  // [Logic Hidden]
    return () => {
  // [Logic Hidden]
    // eslint-disable-next-line react-hooks/exhaustive-deps
  useEffect(() => {
  // [Logic Hidden]
      timer = setInterval(() => {
  // [Logic Hidden]
        setRestTimeLeft((prev) => prev - 1);
  // [Logic Hidden]
      setCurrentSet((prev) => prev + 1);
  // [Logic Hidden]
    return () => clearInterval(timer);
  // [Logic Hidden]
  useEffect(() => {
  // [Logic Hidden]
      const timer = setInterval(() => {
  // [Logic Hidden]
        setExerciseTimeLeft((prev) => Math.max(0, prev - 1));
  // [Logic Hidden]
      return () => clearInterval(timer);
  // [Logic Hidden]
  const toDayIndex = useCallback((value, fallback = 0) => {
  // [Logic Hidden]
  const normalizeWeeklyPlan = useCallback((rawPlan = []) => {
  // [Logic Hidden]
    // Create a map from the backend response
      (Array.isArray(rawPlan) ? rawPlan : []).map((d) => {
  // [Logic Hidden]
    // Map all 7 days, filling missing ones with placeholders
    return days.map((label, idx) =>
  // [Logic Hidden]
  // displayPlan is just the plan - backend handles swapping now
    () => new Map(displayPlan.map((day, idx) => [toDayIndex(day?.day_of_week, idx), day])),
  // [Logic Hidden]
    (a, b) => toDayIndex(a?.day_of_week, 0) - toDayIndex(b?.day_of_week, 0)
  // [Logic Hidden]
  // ✅ FIX: Use state-based completedDayIndices (hydrated from backend on mount) instead of
  // reading volatile localStorage keys on every render.  Falls back to localStorage keys + plan
  // is_completed flags for the first render before the backend response arrives.
  const completedIds = (() => {
  // [Logic Hidden]
    // Also read is_completed from the plan itself (set when session finishes or loaded from cache)
    displayPlan.forEach((d, idx) => {
  // [Logic Hidden]
      // Legacy localStorage fallback (keeps backward compat until history fetch completes)
  const handleRestDayDecision = useCallback(async () => {
  // [Logic Hidden]
      async (confirmed) => {
  // [Logic Hidden]
        // User clicked cancel/close - do nothing
          // User wants to rest - keep the plan as is
        // User clicked "Cancel" - wants to workout, swap rest day with next workout day
          // Check if user is logged in (Authentication is handled via HttpOnly cookies)
          // Get user email - try localStorage first, then fetch from API if needed
          // If email not found in localStorage, try fetching from API
            // Update the workout plan with the swapped version from backend
            // Save to storage
            // DON'T save a decision - the plan is already swapped from backend
            // The displayPlan local swap logic should NOT apply here
            // Log schedule swap to workout history & activities!
            // Server responded with error
            // Request made but no response
            // Error setting up request
  const getSwapEmail = async () => {
  // [Logic Hidden]
  const canSwapWorkoutToRest = (dayIdx) => {
  // [Logic Hidden]
  const openWorkoutToRestModal = (dayIdx) => {
  // [Logic Hidden]
  const handleConfirmWorkoutToRestSwap = async () => {
  // [Logic Hidden]
      // Authentication is handled via HttpOnly cookies
        // Log schedule swap to workout history & activities!
  const handleDayClick = useCallback((dayIdx) => {
  // [Logic Hidden]
  useEffect(() => {
  // [Logic Hidden]
    const timer = setTimeout(() => {
  // [Logic Hidden]
    return () => clearTimeout(timer);
  // [Logic Hidden]
  const releaseCameraStream = () => {
  // [Logic Hidden]
    stream.getTracks().forEach((track) => track.stop());
  // [Logic Hidden]
  const ensureCameraStream = async () => {
  // [Logic Hidden]
  const emitWorkoutProgress = (completedCount, totalCount, fullyDone = false) => {
  // [Logic Hidden]
  const startCamera = async () => {
  // [Logic Hidden]
  const stopCamera = () => {
  // [Logic Hidden]
  const handleExerciseSelect = (ex) => {
  // [Logic Hidden]
  const moveToExercise = async (nextExercise) => {
  // [Logic Hidden]
  const handleExerciseComplete = async () => {
  // [Logic Hidden]
    const completedCount = Object.values(nextStatus).filter((s) => s === 'completed').length;
  // [Logic Hidden]
    const currentIndex = activeDay.exercises.findIndex((e) =>
  // [Logic Hidden]
    // Priority 1: Send exercise result to Python backend for variation suggestion.
      const completedSoFar = Object.values({ ...exerciseStatus, [getExerciseStatusKey(activeExercise)]: 'completed' }).filter(s => s === 'completed').length;
  // [Logic Hidden]
      // Stop the camera stream first
      // Set loading state
      }).then(res => {
  // [Logic Hidden]
      }).catch(async () => {
  // [Logic Hidden]
        // Fallback: silently finish if API fails so the user doesn't get stuck
  const handleExerciseSkipped = async (exercise = activeExercise) => {
  // [Logic Hidden]
    const completedCount = Object.values(nextStatus).filter((s) => s === 'completed').length;
  // [Logic Hidden]
    }).catch((error) => console.error('Failed to sync skip status:', error));
  // [Logic Hidden]
    const currentIndex = activeDay.exercises.findIndex((e) =>
  // [Logic Hidden]
  const handleRepUpdate = (repsCount) => {
  // [Logic Hidden]
  const finishSession = async (isPartial = false, snapshot = null) => {
  // [Logic Hidden]
        (exercise) => statusSnapshot[getExerciseStatusKey(exercise)] === 'completed'
  // [Logic Hidden]
        // ALSO log activity to the backend for the Dashboard's Activity section!
      // ✅ FIX: Persist exerciseStatus to localStorage so red/green ticks survive a browser refresh.
      // Key is scoped to today's date + day name to avoid stale data bleeding into other days.
        // Clear partial status cache since session is now fully done
        // ✅ FIX: Update completedDayIndices React state so the UI reflects completion immediately.
          setCompletedDayIndices((prev) => new Set([...prev, completedDayIdx]));
  // [Logic Hidden]
        // ✅ FIX: Mark is_completed:true on plan state + localStorage cache so it survives refresh.
        setPlan((prevPlan) => {
  // [Logic Hidden]
          const updatedPlan = prevPlan.map((d) =>
  // [Logic Hidden]
          // Persist the updated completion flag to cache
        // ✅ FIX: Persist exercise_status so skipped/completed ticks are restored on re-login.
        // Build a name-keyed map (readable) alongside the raw status key map.
        (activeDay.exercises || []).forEach((ex) => {
  // [Logic Hidden]
           exercises: activeDay.exercises.map(ex => ({
  // [Logic Hidden]
      // ✅ FIX: Sync workout_completed to backend trends so Dashboard streak works
  const handleLogout = () => {
  // [Logic Hidden]
    showConfirmDialog("Log out of Elevate?", (confirmed) => {
  // [Logic Hidden]
          /* ── Base animations (session panels etc.) ── */
          /* ── Card hover lift ── */
          /* ── Nav & Icon hovers ── */
          /* ── Active card pulse ── */
          /* ── Exercise list item hover ── */
          /* ── Session buttons ── */
          /* ── History cards ── */
              <button style={styles.iconButton} className="icon-hover" onClick={() => setShowHistory(!showHistory)} title="Past Workouts">🕒</button>
  // [Logic Hidden]
                    .map((day, idx) => {
  // [Logic Hidden]
                      const previewExercises = dayExercises.filter((ex) => !ex?.is_warmup);
  // [Logic Hidden]
                          onClick={() => !isPlaceholder && isToday && handleDayClick(dayIdx)}
  // [Logic Hidden]
                                  {displayExercises.slice(0, 3).map((ex, i) => (
  // [Logic Hidden]
                                    onClick={() => handleDayClick(dayIdx)}
  // [Logic Hidden]
                                      onClick={() => openWorkoutToRestModal(dayIdx)}
  // [Logic Hidden]
                        onClick={async () => {
  // [Logic Hidden]
                          const hasProgress = Object.values(exerciseStatus).some(s => s === 'completed' || s === 'skipped');
  // [Logic Hidden]
                              async (confirmed) => {
  // [Logic Hidden]
                    {(() => {
  // [Logic Hidden]
                        : (activeDay.exercises || []).filter((exercise) => exercise?.is_warmup);
  // [Logic Hidden]
                      const mainExercises = (activeDay.exercises || []).filter((exercise) => !exercise?.is_warmup);
  // [Logic Hidden]
                      const renderExerciseItem = (exercise, index, isWarmupSection = false) => {
  // [Logic Hidden]
                        // ✅ FIX: Also look up via __byname__ key for status hydrated from backend on re-login.
                        // Backend hydration uses name-based keys since the full key (name|sets|reps|warmup)
                        // isn't stored on the server. The full key takes precedence if present.
                            onClick={() => !isCompleted && !isSkipped && handleExerciseSelect(exercise)}
  // [Logic Hidden]
                              {warmupExercises.map((exercise, index) => renderExerciseItem(exercise, index, true))}
  // [Logic Hidden]
                          {mainExercises.map((exercise, index) => renderExerciseItem(exercise, index, false))}
  // [Logic Hidden]
                          {Object.values(exerciseStatus).some(s => s === 'completed' || s === 'skipped') && (
  // [Logic Hidden]
                              onClick={() => {
  // [Logic Hidden]
                                  async (confirmed) => {
  // [Logic Hidden]
                        <button onClick={() => setVariationResult(null)} style={{ position: 'absolute', top: 8, right: 10, background: 'none', border: 'none', color: 'var(--app-text-muted)', fontSize: '16px', cursor: 'pointer' }}>✕</button>
  // [Logic Hidden]
                      <button style={styles.btnDone} className="btn-done" onClick={() => handleExerciseSkipped(activeExercise)}>SKIP TO NEXT</button>
  // [Logic Hidden]
                        onSkip={() => handleExerciseSkipped(activeExercise)}
  // [Logic Hidden]
                             <button onClick={() => setRestTimeLeft(0)} style={{marginTop: '30px', background: 'var(--btn-skip-bg)', border: 'none', color: 'var(--btn-skip-text)', padding: '10px 20px', borderRadius: '8px', cursor: 'pointer', fontWeight: 'bold'}}>Skip Rest</button>
  // [Logic Hidden]
                {getFutureOriginalRestDays(displayPlan, swapWorkoutDayIndex, todayIdx).map((day) => {
  // [Logic Hidden]
                      onClick={() => setSelectedTargetRestDayIndex(idx)}
  // [Logic Hidden]
                  onClick={() => {
  // [Logic Hidden]
              <button onClick={() => setShowHistory(false)} style={{background:'none', border:'none', color:'var(--app-text)', fontSize:'20px', cursor:'pointer'}}>✕</button>
  // [Logic Hidden]
                onClick={() => setHistoryTab('workout')}
  // [Logic Hidden]
                onClick={() => setHistoryTab('swap')}
  // [Logic Hidden]
                  pastWorkouts.map((day, i) => (
  // [Logic Hidden]
                    <div key={i} style={styles.historyItem} className="history-card" onClick={() => setSelectedHistory(selectedHistory === i ? null : i)}>
  // [Logic Hidden]
                    .map((entry, idx) => {
  // [Logic Hidden]
                  onClick={async () => {
  // [Logic Hidden]
```

## frontend\src\pages\admin\AdminLogin.jsx
```javascript
export default function AdminLogin() {
  // [Logic Hidden]
  const handleChange = (event) => {
  // [Logic Hidden]
    setFormData((prev) => ({ ...prev, [name]: value }));
  // [Logic Hidden]
  const handleSubmit = async (event) => {
  // [Logic Hidden]
```

## frontend\src\pages\admin\Audit.jsx
```javascript
export default function AdminAudit() {
  // [Logic Hidden]
  const params = useMemo(() => {
  // [Logic Hidden]
  const fetchLogs = useCallback(async () => {
  // [Logic Hidden]
      setPagination((prev) => ({
  // [Logic Hidden]
  useEffect(() => {
  // [Logic Hidden]
  const setPage = (nextPage) => {
  // [Logic Hidden]
    setPagination((prev) => ({
  // [Logic Hidden]
          onChange={(event) => {
  // [Logic Hidden]
            setPagination((prev) => ({ ...prev, page: 1 }));
  // [Logic Hidden]
          {ACTION_OPTIONS.map((action) => (
  // [Logic Hidden]
                logs.map((log) => (
  // [Logic Hidden]
        <button className="admin-btn secondary" onClick={() => setPage((pagination.page || 1) - 1)}>
  // [Logic Hidden]
        <button className="admin-btn secondary" onClick={() => setPage((pagination.page || 1) + 1)}>
  // [Logic Hidden]
```

## frontend\src\pages\admin\Content.jsx
```javascript
export default function AdminContent() {
  // [Logic Hidden]
  const fetchContent = async () => {
  // [Logic Hidden]
  useEffect(() => {
  // [Logic Hidden]
  const resetForm = () => {
  // [Logic Hidden]
  const handleChange = (event) => {
  // [Logic Hidden]
    setForm((prev) => ({
  // [Logic Hidden]
  const toList = (raw) =>
  // [Logic Hidden]
      .map((item) => item.trim())
  // [Logic Hidden]
  const buildPayload = () => ({
  // [Logic Hidden]
  const handleSaveExercise = async (event) => {
  // [Logic Hidden]
  const handleEdit = (exercise) => {
  // [Logic Hidden]
  const handleDelete = async (id) => {
  // [Logic Hidden]
    const exercise = exercises.find((item) => item._id === id);
  // [Logic Hidden]
  const confirmDeleteExercise = async () => {
  // [Logic Hidden]
  const handleSaveRules = async () => {
  // [Logic Hidden]
          onChange={(event) => {
  // [Logic Hidden]
            // Validate JSON live so the admin gets immediate feedback
                exercises.map((exercise) => (
  // [Logic Hidden]
                        <button className="admin-btn secondary" type="button" onClick={() => handleEdit(exercise)}>
  // [Logic Hidden]
                        <button className="admin-btn danger" type="button" onClick={() => handleDelete(exercise._id)}>
  // [Logic Hidden]
        onCancel={() => setDeleteDialog({ show: false, exerciseId: '', exerciseName: '' })}
  // [Logic Hidden]
```

## frontend\src\pages\admin\Dashboard.jsx
```javascript
const safeNumber = (value) => {
  // [Logic Hidden]
export default function AdminDashboard() {
  // [Logic Hidden]
  const fetchDashboardData = async () => {
  // [Logic Hidden]
  useEffect(() => {
  // [Logic Hidden]
  const goalDistribution = useMemo(() => {
  // [Logic Hidden]
            {goalDistribution.map((goal) => {
  // [Logic Hidden]
function StatCard({ label, value, danger = false }) {
  // [Logic Hidden]
function HealthCard({ title, status }) {
  // [Logic Hidden]
```

## frontend\src\pages\admin\System.jsx
```javascript
export default function AdminSystem() {
  // [Logic Hidden]
  const totalFromGoalDistribution = useMemo(() => {
  // [Logic Hidden]
    return distribution.reduce((sum, item) => sum + (Number(item?.count) || 0), 0);
  // [Logic Hidden]
  const fetchSystemData = async () => {
  // [Logic Hidden]
  useEffect(() => {
  // [Logic Hidden]
  const handleMaintenanceSubmit = async (event) => {
  // [Logic Hidden]
  const handleCreateAnnouncement = async (event) => {
  // [Logic Hidden]
  const handleDeleteAnnouncement = async (announcementId) => {
  // [Logic Hidden]
    const target = announcements.find((item) => item.id === announcementId);
  // [Logic Hidden]
  const confirmDeleteAnnouncement = async () => {
  // [Logic Hidden]
                  onChange={(event) =>
  // [Logic Hidden]
                    setMaintenance((prev) => ({ ...prev, enabled: event.target.checked }))
  // [Logic Hidden]
                onChange={(event) =>
  // [Logic Hidden]
                  setMaintenance((prev) => ({ ...prev, message: event.target.value }))
  // [Logic Hidden]
                  onChange={(event) =>
  // [Logic Hidden]
                    setAnnouncementForm((prev) => ({ ...prev, title: event.target.value }))
  // [Logic Hidden]
                  onChange={(event) =>
  // [Logic Hidden]
                    setAnnouncementForm((prev) => ({ ...prev, message: event.target.value }))
  // [Logic Hidden]
                  onChange={(event) =>
  // [Logic Hidden]
                    setAnnouncementForm((prev) => ({ ...prev, type: event.target.value }))
  // [Logic Hidden]
                {announcements.map((item) => (
  // [Logic Hidden]
                      <button className="admin-btn danger" type="button" onClick={() => handleDeleteAnnouncement(item.id)}>
  // [Logic Hidden]
        onCancel={() => setDeleteDialog({ show: false, announcementId: '', title: '' })}
  // [Logic Hidden]
function InfoCard({ title, value }) {
  // [Logic Hidden]
```

## frontend\src\pages\admin\Users.jsx
```javascript
export default function AdminUsers() {
  // [Logic Hidden]
  const queryParams = useMemo(() => {
  // [Logic Hidden]
  const fetchUsers = useCallback(async () => {
  // [Logic Hidden]
      setPagination((prev) => ({
  // [Logic Hidden]
  useEffect(() => {
  // [Logic Hidden]
  const runAction = async (userId, actionFn) => {
  // [Logic Hidden]
  const handleSuspend = (userId) => {
  // [Logic Hidden]
    const user = users.find((item) => item._id === userId);
  // [Logic Hidden]
  const handleActivate = (userId) => {
  // [Logic Hidden]
    runAction(userId, () => adminActivateUser(userId));
  // [Logic Hidden]
  const handleResetPassword = (userId) => {
  // [Logic Hidden]
    runAction(userId, async () => {
  // [Logic Hidden]
  const handleDelete = (userId) => {
  // [Logic Hidden]
    const user = users.find((item) => item._id === userId);
  // [Logic Hidden]
  const confirmActionDialog = async ({ reason }) => {
  // [Logic Hidden]
      await runAction(userId, () => adminSuspendUser(userId, reason || 'Administrative action'));
  // [Logic Hidden]
      await runAction(userId, () => adminDeleteUser(userId));
  // [Logic Hidden]
  const setPage = (nextPage) => {
  // [Logic Hidden]
    setPagination((prev) => ({
  // [Logic Hidden]
          onChange={(event) => {
  // [Logic Hidden]
            setPagination((prev) => ({ ...prev, page: 1 }));
  // [Logic Hidden]
          onChange={(event) => {
  // [Logic Hidden]
            setPagination((prev) => ({ ...prev, page: 1 }));
  // [Logic Hidden]
                users.map((user) => {
  // [Logic Hidden]
                            <button className="admin-btn secondary" disabled={busy} onClick={() => handleSuspend(user._id)}>
  // [Logic Hidden]
                            <button className="admin-btn secondary" disabled={busy} onClick={() => handleActivate(user._id)}>
  // [Logic Hidden]
                            <button className="admin-btn secondary" disabled={busy} onClick={() => handleResetPassword(user._id)}>
  // [Logic Hidden]
                            <button className="admin-btn danger" disabled={busy} onClick={() => handleDelete(user._id)}>
  // [Logic Hidden]
        <button className="admin-btn secondary" onClick={() => setPage((pagination.page || 1) - 1)}>
  // [Logic Hidden]
        <button className="admin-btn secondary" onClick={() => setPage((pagination.page || 1) + 1)}>
  // [Logic Hidden]
        onCancel={() => setActionDialog({ show: false, type: '', userId: '', userName: '' })}
  // [Logic Hidden]
```

## frontend\src\services\profileApi.js
```javascript
// API service for profile updates with plan regeneration.
// Authenticated Python calls go through the Node proxy so the HttpOnly auth cookie
// is read by elevate-11 and forwarded to Python as x-auth-token server-side.
// Request timeout in milliseconds
const getCsrfToken = async () => {
  // [Logic Hidden]
const summarizeProfileForLog = (profileData) => {
  // [Logic Hidden]
/**
 * Create axios instance with custom configuration
 */
/**
 * Request interceptor
 */
  async (config) => {
  // [Logic Hidden]
  (error) => Promise.reject(error)
  // [Logic Hidden]
/**
 * Response interceptor - Global error handling
 */
  (response) => response,
  // [Logic Hidden]
  (error) => {
  // [Logic Hidden]
    // Keep logs minimal to avoid leaking payloads or server internals in browser consoles.
/**
 * Classify error types for better handling
 */
export const classifyError = (error) => {
  // [Logic Hidden]
  // Network error (no response from server)
  // HTTP error responses
/**
 * Update user profile and regenerate workout/meal plans if needed
 * Uses the safe endpoint with graceful degradation
 */
export const updateProfileWithRegeneration = async (profileData, options = {}) => {
  // [Logic Hidden]
      // Health check before making the request (optional, can be disabled)
          // Continue anyway - backend might still respond
      // Retry delay (exponential backoff)
        await new Promise(resolve => setTimeout(resolve, delay));
  // [Logic Hidden]
      // Make the request with timeout
      const timeoutId = setTimeout(() => controller.abort(), timeout);
  // [Logic Hidden]
      // Log what was regenerated
      // Don't retry for certain error types
      // If this was the last attempt, break and throw
  // All retries failed, throw formatted error
/**
 * Alternative endpoint for basic profile update (no regeneration)
 */
export const updateProfileBasic = async (profileData) => {
  // [Logic Hidden]
/**
 * Get available profile endpoints from backend
 */
export const getProfileEndpoints = async () => {
  // [Logic Hidden]
/**
 * Check backend health
 */
export const checkBackendHealth = async () => {
  // [Logic Hidden]
```

## frontend\src\utils\circuitBreaker.js
```javascript
/**
 * ARCH-7: circuitBreaker.js
 *
 * Lightweight client-side circuit breaker for FitnessAPI (Python backend).
 * Protects the frontend from hammering an unreachable Python service.
 *
 * States:
 *   CLOSED  – normal operation, requests pass through
 *   OPEN    – service detected as down, requests fail fast
 *   HALF    – after cooldown, one probe request is allowed through
 *
 * Configuration is intentionally conservative:
 *   - Opens after 3 consecutive failures
 *   - Stays open for 30 seconds before probing
 *   - Resets on any successful response
 */
  /**
   * Check whether a request is allowed right now.
   * - If OPEN and cooldown not elapsed: throw CircuitOpenError.
   * - If OPEN and cooldown elapsed: transition to HALF and allow one probe.
   */
    // Cooldown elapsed — allow one probe request.
  /** Record a successful backend response. */
  /** Record a failed backend response/network error. */
  /**
   * Wrap an async axios call. Throws a CircuitOpenError immediately if OPEN.
   * Records success/failure and transitions state accordingly.
   *
   * @param {() => Promise<any>} fn - Async function that calls the backend
  // [Logic Hidden]
   * @returns {Promise<any>}
   */
    // Network errors, timeouts, and 5xx responses count as failures.
    // 4xx client errors (bad input) do NOT count.
  /** Manually reset (e.g. after a user-triggered retry) */
// Singleton for the Python backend
```

## frontend\src\utils\googleAuth.js
```javascript
// Reusable Google Auth Utility Functions
// Common Google SDK loading function
  // [Logic Hidden]
export const loadGoogleSDK = (buttonId, onSuccess, onError) => {
  // [Logic Hidden]
    // Bug #34 fixed: check if the script tag already exists to prevent duplicates.
    // Multiple components (Login, Register) each called loadGoogleSDK on mount,
    // causing N script tags and N SDK initialisations for N components.
        // Script already in DOM: if SDK is already loaded, initialise immediately;
        // otherwise, piggyback on the existing script's load event.
            existing.addEventListener('load', () => initGoogleButton(buttonId, onSuccess, onError));
  // [Logic Hidden]
    // Load Google SDK script
    script.onload = () => {
  // [Logic Hidden]
    script.onerror = () => {
  // [Logic Hidden]
const clearElementChildren = (element) => {
  // [Logic Hidden]
// Bug #34 fix: extracted SDK-dependent initialisation into its own function
  // [Logic Hidden]
// so it can be called both from a fresh script load and from the dedup path.
const initGoogleButton = (buttonId, onSuccess, onError) => {
  // [Logic Hidden]
            // Use environment variable instead of hardcoded ID
                // Show visible error in the button container
// Common Google login initialization function
  // [Logic Hidden]
export const initializeGoogleLogin = (containerId, onSuccessCallback, onErrorCallback, clientIdOverride = null) => {
  // [Logic Hidden]
            // Try both Vite and React App environment variable names
            // Use override if provided, otherwise use environment variable
                // Show a warning if the client ID is not configured
                    configButton.onclick = () => {
  // [Logic Hidden]
            // Validate client ID format (should end with '.googleusercontent.com')
                    errorButton.onclick = () => {
  // [Logic Hidden]
            // Check if the button container exists before rendering
                // Clear the container first to ensure no conflicts
                // Apply custom styling after the button is rendered
                setTimeout(() => {
  // [Logic Hidden]
            // Show fallback button if initialization fails
                fallbackButton.onclick = () => {
  // [Logic Hidden]
```

## frontend\src\utils\poseModelPreload.js
```javascript
export const getModelAssetUrl = (model) =>
  // [Logic Hidden]
const warmFetch = async (url) => {
  // [Logic Hidden]
    // no-cors keeps preload robust across CDN CORS policies.
    // Best-effort warmup. PoseDetector will perform full load fallback.
export const preloadPoseAssets = async () => {
  // [Logic Hidden]
  preloadPromise = (async () => {
  // [Logic Hidden]
    // Optimize: Deduplicate and preload only the primary heavy model to save bandwidth.
```

## frontend\src\utils\sessionUtils.js
```javascript
/**
 * sessionUtils.js
 *
 * BUG-F10 fix: clearUserScopedCache() and syncUserSession() were duplicated
 * identically in both Login.jsx and Register.jsx. Extracted here as the single
 * authoritative source so a bug fix or cache-key addition only needs to happen
 * in one place.
 */
export const buildSessionUser = (user = {}) => ({
  // [Logic Hidden]
export const persistSessionUser = (user = {}) => {
  // [Logic Hidden]
/**
 * Removes all cache keys that are scoped to the currently logged-in user.
 * Call this before writing a new session so stale data from a previous user
 * session is never served to the incoming user.
 */
export const clearUserScopedCache = () => {
  // [Logic Hidden]
  scopedKeys.forEach((k) => {
  // [Logic Hidden]
/**
 * Compares the incoming user's identity against the previously stored session.
 * If the identity changed (different user logged in) clear the user-scoped cache
 * so the incoming user never sees the previous user's data.
 *
 * @param {object} newUser - User object from the login/register API response.
 */
export const syncUserSession = (newUser) => {
  // [Logic Hidden]
```

## frontend\src\utils\storage.js
```javascript
/**
 * Centralized localStorage management
 * Provides type-safe key constants and error-handling wrappers
 */
  // Auth
  // Activity & History
  // User Profile
  // Streak & Progress
  // Daily Tracking
  // Workout Sessions
  // Water & Sleep
  // Nutrition Cache
  // Profile Change Tracking
  // Cached Data
  // Notification Tracking
  // Dynamic notification keys (helper function below)
  // [Logic Hidden]
  getNotificationKey: (id) => `notification_${id}_last_shown`,
  // [Logic Hidden]
  getReminderKey: (type) => `reminder_${type}_last_shown`,
  // [Logic Hidden]
  getWorkoutDoneKey: (dateStr) => `workout_done_${dateStr}`
  // [Logic Hidden]
// SEC-2: Keep sensitive profile/health/session caches in sessionStorage by default.
const _getPrimaryStore = (key) => (SESSION_PREFERRED_KEYS.has(key) ? sessionStorage : localStorage);
  // [Logic Hidden]
const _getFallbackStore = (key) => (SESSION_PREFERRED_KEYS.has(key) ? localStorage : null);
  // [Logic Hidden]
const getUserPrefix = () => {
  // [Logic Hidden]
    // Ignore
const getNamespacedKey = (key) => {
  // [Logic Hidden]
/**
 * Returns a formatted date string (YYYY-MM-DD) strictly in Indian Standard Time (Asia/Kolkata)
 */
export const getLocalDateStr = (d = new Date()) => {
  // [Logic Hidden]
  const year = parts.find(p => p.type === 'year').value;
  // [Logic Hidden]
  const month = parts.find(p => p.type === 'month').value;
  // [Logic Hidden]
  const day = parts.find(p => p.type === 'day').value;
  // [Logic Hidden]
/**
 * Returns today's date in YYYY-MM-DD format strictly in Indian Standard Time (Asia/Kolkata)
 */
export const getTodayStr = () => getLocalDateStr();
  // [Logic Hidden]
/**
 * Safe retrieval from localStorage with error handling
 * @param {string} key - Storage key
 * @param {any} defaultValue - Default value if key not found
 * @returns {any} Retrieved value or defaultValue
 */
export const getFromStorage = (key, defaultValue = null) => {
  // [Logic Hidden]
        // Migrate legacy localStorage value into session storage on read.
    // Try to parse as JSON, otherwise return as string
      // If parsing fails, return the raw string (for simple values)
/**
 * Safe storage to localStorage with error handling
 * @param {string} key - Storage key
 * @param {any} value - Value to store (will be JSON stringified)
 * @returns {boolean} Success status
 */
export const setToStorage = (key, value) => {
  // [Logic Hidden]
    // Purge old localStorage copies when sensitive keys are session-backed.
/**
 * Safe removal from localStorage
 * @param {string} key - Storage key to remove
 * @returns {boolean} Success status
 */
export const removeFromStorage = (key) => {
  // [Logic Hidden]
/**
 * Clear all localStorage data
 * @returns {boolean} Success status
 */
export const clearAllStorage = () => {
  // [Logic Hidden]
/**
 * Safe logout — removes auth-related and volatile session keys only.
 * Preserves non-sensitive cached data (nutrition plan, workout plan, etc.)
 * so a re-login restores state instantly without extra API calls.
 *
 * Call this INSTEAD of localStorage.clear() on logout.
 * @returns {boolean} Success status
 */
export const logoutSafe = () => {
  // [Logic Hidden]
    // SEC-1 (complete): auth token now lives in an HttpOnly cookie managed by the server.
    // Remove stale 'token' key that may have been set by older app versions.
    // Volatile daily state that should reset on logout
      // Nutrition volatile keys
      // Cached plans (different user may have different profile)
    volatileKeys.forEach(key => {
  // [Logic Hidden]
    // Also clear any dynamic workout_done_* and notification_* keys
      if (key && dynamicPrefixes.some(prefix => key.startsWith(prefix))) {
  // [Logic Hidden]
    // Clear sessionStorage (chat history etc.)
    // Fallback: nuclear clear if selective removal fails
/**
 * Get multiple values at once
 * @param {string[]} keys - Array of storage keys
 * @returns {object} Object with key-value pairs
 */
export const getMultipleFromStorage = (keys) => {
  // [Logic Hidden]
  keys.forEach((key) => {
  // [Logic Hidden]
/**
 * Set multiple values at once
 * @param {object} entries - Object with key-value pairs
 * @returns {boolean} Success status (all or nothing)
 */
export const setMultipleToStorage = (entries) => {
  // [Logic Hidden]
    Object.entries(entries).forEach(([key, value]) => {
  // [Logic Hidden]
/**
 * Check if a key exists in storage
 * @param {string} key - Storage key
 * @returns {boolean} True if key exists
 */
export const keyExistsInStorage = (key) => {
  // [Logic Hidden]
/**
 * Get storage size (approximate, in characters)
 * @returns {number} Total size of localStorage
 */
export const getStorageSize = () => {
  // [Logic Hidden]
// ─────────────────────────────────────────────────────────────────────────────
// Bug #5 fix – Named exports matching the plan's safeJSONParse interface.
// These are thin wrappers over the existing safe helpers above so there is
// no duplicate logic.
// ─────────────────────────────────────────────────────────────────────────────
/**
 * safeJSONParse – parse a localStorage key as JSON, return defaultValue on any error.
 * Corrupted data is automatically removed from localStorage.
 */
export const safeJSONParse = (key, defaultValue = null) => {
  // [Logic Hidden]
      // Ignore cleanup failures; returning fallback keeps app stable.
/**
 * safeJSONStringify – write a value to localStorage as JSON, silently handles quota errors.
 */
export const safeJSONStringify = (key, value) => setToStorage(key, value);
  // [Logic Hidden]
// Legacy compatibility exports
export const markSessionStart = () => {
  // [Logic Hidden]
    // no-op
```

## frontend\src\utils\syncBridge.js
```javascript
class DashboardSyncBridge {
  // [Logic Hidden]
      window.addEventListener('storage', (event) => {
  // [Logic Hidden]
    if (!type || typeof callback !== 'function') {
  // [Logic Hidden]
      return () => {};
  // [Logic Hidden]
    return () => {
  // [Logic Hidden]
    callbacks.forEach((callback) => {
  // [Logic Hidden]
```

## frontend\src\__tests__\ConfirmDialog.test.jsx
```javascript
/**
 * BUG-C2: Frontend component tests — ConfirmDialog
 * Verifies rendering, user interactions, and scroll-lock side effect.
 *
 * Run: npm run test:unit
 */
describe('ConfirmDialog', () => {
  // [Logic Hidden]
  beforeEach(() => {
  // [Logic Hidden]
  it('renders nothing when show=false', () => {
  // [Logic Hidden]
      <ConfirmDialog show={false} message="Are you sure?" onConfirm={() => {}} onCancel={() => {}} />
  // [Logic Hidden]
  it('renders the message and buttons when show=true', () => {
  // [Logic Hidden]
      <ConfirmDialog show={true} message="Delete this item?" onConfirm={() => {}} onCancel={() => {}} />
  // [Logic Hidden]
  it('calls onConfirm with true when Confirm button is clicked', () => {
  // [Logic Hidden]
      <ConfirmDialog show={true} message="Continue?" onConfirm={onConfirm} onCancel={() => {}} />
  // [Logic Hidden]
  it('calls onCancel with false when Cancel button is clicked', () => {
  // [Logic Hidden]
      <ConfirmDialog show={true} message="Continue?" onConfirm={() => {}} onCancel={onCancel} />
  // [Logic Hidden]
  it('calls onCancel when backdrop is clicked', () => {
  // [Logic Hidden]
      <ConfirmDialog show={true} message="Close me" onConfirm={() => {}} onCancel={onCancel} />
  // [Logic Hidden]
    // Click the backdrop (first child = .confirm-modal-backdrop)
  it('locks body scroll when shown', () => {
  // [Logic Hidden]
      <ConfirmDialog show={true} message="test" onConfirm={() => {}} onCancel={() => {}} />
  // [Logic Hidden]
  it('restores body scroll when unmounted', () => {
  // [Logic Hidden]
      <ConfirmDialog show={true} message="test" onConfirm={() => {}} onCancel={() => {}} />
  // [Logic Hidden]
```

## frontend\src\__tests__\poseRouting.test.js
```javascript
describe('PoseDetector Routing & Metadata Propagation', () => {
  // [Logic Hidden]
  const route = (exercise) => {
  // [Logic Hidden]
  it('routes Dumbbell Biceps Curl to CURL', () => {
  // [Logic Hidden]
  it('routes Archer Push Up to PRESS', () => {
  // [Logic Hidden]
  it('routes Barbell Back Squat to SQUAT', () => {
  // [Logic Hidden]
  it('routes Pull Up to HINGE (via vertical_pull)', () => {
  // [Logic Hidden]
  it('routes Lateral Raise to RAISE', () => {
  // [Logic Hidden]
  it('routes Plank to CORE', () => {
  // [Logic Hidden]
  it('routes Unknown Exercise to GENERIC', () => {
  // [Logic Hidden]
  it('falls back to getLegacyFallback when movement_pattern is absent (legacy support)', () => {
  // [Logic Hidden]
    // Legacy client cache/fallback compatibility check
```

## frontend\src\__tests__\setup.js
```javascript
// Test setup file for Vitest + jsdom
// Runs before every test file
// Mock matchMedia (not available in jsdom)
  value: (query) => ({
  // [Logic Hidden]
    addListener: () => {},
  // [Logic Hidden]
    removeListener: () => {},
  // [Logic Hidden]
    addEventListener: () => {},
  // [Logic Hidden]
    removeEventListener: () => {},
  // [Logic Hidden]
    dispatchEvent: () => false,
  // [Logic Hidden]
// Mock IntersectionObserver (not in jsdom)
// Mock localStorage
const localStorageMock = (() => {
  // [Logic Hidden]
    getItem: (k) => store[k] ?? null,
  // [Logic Hidden]
    setItem: (k, v) => { store[k] = String(v); },
  // [Logic Hidden]
    removeItem: (k) => { delete store[k]; },
  // [Logic Hidden]
    clear: () => { store = {}; },
  // [Logic Hidden]
    key: (i) => Object.keys(store)[i] ?? null,
  // [Logic Hidden]
```

## frontend\src\__tests__\storage.test.js
```javascript
/**
 * BUG-C2: Frontend unit tests — storage utilities
 * Tests the core localStorage wrapper in utils/storage.js
 *
 * Run: npm run test:unit
 */
describe('storage utilities', () => {
  // [Logic Hidden]
  beforeEach(() => {
  // [Logic Hidden]
  describe('setToStorage / getFromStorage', () => {
  // [Logic Hidden]
    it('stores and retrieves a plain string', () => {
  // [Logic Hidden]
    it('stores and retrieves a JSON-serialisable object', () => {
  // [Logic Hidden]
    it('returns null for a key that has never been set', () => {
  // [Logic Hidden]
    it('overwrites an existing value', () => {
  // [Logic Hidden]
  describe('StorageKeys', () => {
  // [Logic Hidden]
    it('exports TOKEN key', () => {
  // [Logic Hidden]
```

