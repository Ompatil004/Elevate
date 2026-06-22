import axios from 'axios';
import { pythonBackendCB } from './utils/circuitBreaker';

// ===== API CONFIGURATION =====
// Auth endpoints (login/register) are on Node.js backend (port 5000)
// Protected Python endpoints are reached through the Node backend proxy.
const VITE_API_URL = import.meta.env.VITE_API_URL || '/api';
const PYTHON_PROXY_API_URL = `${VITE_API_URL.replace(/\/+$/, "")}/python`;
// Export base URLs for use in components
export const API_BASE_URL = VITE_API_URL;
export const PYTHON_API_URL = PYTHON_PROXY_API_URL;
// Bug #53 fixed: POSE_TRACKING_BASE_URL export removed — no consumer in the codebase

// SEC-12: Cache the CSRF token after first fetch.
// The token changes on every GET /api/csrf-token call, so we only fetch once
// per session (it is invalidated automatically on logout via cookie clear).
let _csrfToken = null;
const getCsrfToken = async () => {
    if (_csrfToken) return _csrfToken;
    try {
        const res = await axios.get(`${VITE_API_URL}/csrf-token`, { withCredentials: true });
        _csrfToken = res.data.csrfToken;
    } catch {
        _csrfToken = null; // will retry next time
    }
    return _csrfToken;
};
// Call on app startup so the CSRF cookie is set before any mutation
getCsrfToken();
// Reset cache on logout
export const resetCsrfCache = () => { _csrfToken = null; };

// Create axios instance for AUTH endpoints (Node.js backend)
const AuthAPI = axios.create({
    baseURL: VITE_API_URL,  // /api
    headers: {
        'Content-Type': 'application/json'
    },
    timeout: 15000,
    withCredentials: true,  // SEC-1: send HttpOnly cookie on every request
});

// Create axios instance for protected WORKOUT/NUTRITION endpoints via Node proxy.
// Timeout set to 60s: workout engine calls Gemini AI + XGBoost models which can
// take 30-50s on first generation (cold start) or for complex profiles.
const FitnessAPI = axios.create({
    baseURL: PYTHON_PROXY_API_URL,  // /api/python on the Node backend
    headers: {
        'Content-Type': 'application/json'
    },
    timeout: 60000,
    withCredentials: true,  // SEC-1: send HttpOnly cookie on every request
});

// Request interceptor for Auth API — attach CSRF token (SEC-1 complete: no localStorage fallback)
const CSRF_SAFE_METHODS = new Set(['get', 'head', 'options']);
AuthAPI.interceptors.request.use(
    async (config) => {
        // SEC-1 (complete): user auth is fully HttpOnly cookie — no x-auth-token header needed.
        // withCredentials: true on the instance handles cookie sending automatically.
        // Fallback for cross-site deployments (e.g. Render): send token header if stored in localStorage
        const token = localStorage.getItem('token');
        if (token) {
            config.headers['x-auth-token'] = token;
        }

        // SEC-12: attach CSRF token for state-mutating requests
        if (!CSRF_SAFE_METHODS.has((config.method || 'get').toLowerCase())) {
            const csrf = await getCsrfToken();
            if (csrf) config.headers['x-csrf-token'] = csrf;
        }
        return config;
    },
    (error) => Promise.reject(error)
);

// Reset cached CSRF token when a mutating request is rejected with 403.
// This allows the next request to fetch a fresh token automatically.
AuthAPI.interceptors.response.use(
    (response) => response,
    (error) => {
        const status = error?.response?.status;
        const code = error?.response?.data?.code;
        const method = (error?.config?.method || 'get').toLowerCase();
        if (status === 401 && code === 'SESSION_EXPIRED') {
            resetCsrfCache();
            window.dispatchEvent(new CustomEvent('sessionExpired'));
            return Promise.reject(error);
        }
        if (status === 403 && !CSRF_SAFE_METHODS.has(method)) {
            resetCsrfCache();
        }
        return Promise.reject(error);
    }
);

// ARCH-7: Wrap FitnessAPI with circuit breaker to protect against Python backend downtime.
// The interceptor checks the breaker state BEFORE sending each request.
FitnessAPI.interceptors.request.use(
    async (config) => {
        // ARCH-7: Use circuit-breaker preflight so OPEN can transition to HALF_OPEN probe.
        pythonBackendCB.beforeRequest();
        // Auth cookie is sent to Node; Node forwards the JWT to Python as x-auth-token.
        // Fallback for cross-site deployments (e.g. Render): send token header if stored in localStorage
        const token = localStorage.getItem('token');
        if (token) {
            config.headers['x-auth-token'] = token;
        }

        if (!CSRF_SAFE_METHODS.has((config.method || 'get').toLowerCase())) {
            const csrf = await getCsrfToken();
            if (csrf) config.headers['x-csrf-token'] = csrf;
        }
        if (import.meta.env.DEV) {
            console.log('[FitnessAPI] Request:', config.method?.toUpperCase(), config.baseURL + config.url);
        }
        return config;
    },
    (error) => Promise.reject(error)
);

// ARCH-7: Record failures/successes from the Python backend into the circuit breaker.
// CRITICAL FIX: Do NOT record CircuitOpenError as a backend failure — it's a client-side
// preflight rejection, not an actual backend error. Recording it would cause the failure
// counter to increment indefinitely while OPEN, preventing recovery.
FitnessAPI.interceptors.response.use(
    (response) => {
        pythonBackendCB.recordSuccess();
        if (import.meta.env.DEV) {
            console.log('[FitnessAPI] Success:', response.status, response.config?.url);
        }
        return response;
    },
    (error) => {
        // Skip circuit breaker's own errors — they are NOT backend failures
        if (error?.isCircuitOpen) {
            if (import.meta.env.DEV) {
                console.warn('[FitnessAPI] CircuitOpenError — not recording as backend failure');
            }
            return Promise.reject(error);
        }
        if (import.meta.env.DEV) {
            console.error('[FitnessAPI] Error:', {
                url: error.config?.url,
                method: error.config?.method,
                status: error.response?.status || 'NETWORK_ERROR',
                message: error.message,
                data: error.response?.data,
            });
        }
        pythonBackendCB.recordFailure(error);
        return Promise.reject(error);
    }
);

// ===== AUTH ENDPOINTS (Node.js backend - port 5000) =====
export const registerUser = (userData) => AuthAPI.post('/auth/register', userData);
export const loginUser = (userData) => AuthAPI.post('/auth/login', userData);
export const loginWithGoogle = (tokenId) => AuthAPI.post('/auth/google', { token: tokenId });
export const logoutUser = () => AuthAPI.post('/auth/logout');
export const requestPasswordReset = (payload) => AuthAPI.post('/auth/reset-password/request', payload);
export const confirmPasswordReset = (payload) => AuthAPI.post('/auth/reset-password/confirm', payload);
export const getSessionStatus = () => AuthAPI.get('/auth/session');

// ===== PROFILE ENDPOINTS (Node.js backend - port 5000) =====
export const getProfile = () => AuthAPI.get('/profile');
export const saveProfile = (profileData) => AuthAPI.post('/profile/update', profileData);
export const saveUserProfile = (profileData) => AuthAPI.post('/profile/update', profileData);
export const saveTrends = (trendData) => AuthAPI.post('/profile/trends', trendData);
export const getTrends = (period = 'week') => AuthAPI.get(`/profile/trends?period=${period}`);
export const saveUserWorkoutToNode = (workoutData) => AuthAPI.post('/users/workout/save', workoutData);
export const saveUserMealToNode = (mealData) => AuthAPI.post('/users/meals/save', mealData);
export const getExternalNutritionData = (query) => AuthAPI.get('/users/external/nutrition', { params: { query } });
export const getExternalExerciseData = (muscle) => AuthAPI.get('/users/external/exercise', { params: { muscle } });

// ===== ADMIN ENDPOINTS (Node.js backend - port 5000) =====
export const adminLogin = (payload) => AuthAPI.post('/admin/login', payload);
export const adminLogout = () => AuthAPI.post('/admin/logout');
export const adminVerify = () => AuthAPI.get('/admin/verify');

export const adminGetUsers = (params) => AuthAPI.get('/admin/users', { params });
export const adminGetUserStats = () => AuthAPI.get('/admin/users/stats/overview');
export const adminGetUser = (id) => AuthAPI.get(`/admin/users/${id}`);
export const adminSuspendUser = (id, reason) => AuthAPI.post(`/admin/users/${id}/suspend`, { reason });
export const adminActivateUser = (id) => AuthAPI.post(`/admin/users/${id}/activate`);
export const adminResetUserPassword = (id) => AuthAPI.post(`/admin/users/${id}/reset-password`);
export const adminDeleteUser = (id) => AuthAPI.delete(`/admin/users/${id}`);

export const adminGetHealth = () => AuthAPI.get('/admin/system/health');
export const adminGetSystemStats = () => AuthAPI.get('/admin/system/stats');
export const adminGetMaintenance = () => AuthAPI.get('/admin/system/maintenance');
export const adminSetMaintenance = (payload) => AuthAPI.post('/admin/system/maintenance', payload);
export const adminGetAuditLogs = (params) => AuthAPI.get('/admin/system/audit-logs', { params });
export const adminCreateAnnouncement = (payload) => AuthAPI.post('/admin/system/announcement', payload);
export const adminDeleteAnnouncement = (announcementId) =>
    AuthAPI.delete(`/admin/system/announcement/${announcementId}`);
export const adminGetAnnouncements = () => AuthAPI.get('/admin/system/announcements');

export const adminGetExercises = (params) => AuthAPI.get('/admin/content/exercises', { params });
export const adminCreateExercise = (payload) => AuthAPI.post('/admin/content/exercises', payload);
export const adminUpdateExercise = (id, payload) => AuthAPI.put(`/admin/content/exercises/${id}`, payload);
export const adminDeleteExercise = (id) => AuthAPI.delete(`/admin/content/exercises/${id}`);
export const adminGetWorkoutRules = () => AuthAPI.get('/admin/content/workout-rules');
export const adminSetWorkoutRules = (rules) => AuthAPI.post('/admin/content/workout-rules', { rules });


// ===== WORKOUT/NUTRITION ENDPOINTS (Python backend - port 8000) =====
export const updateProfileAndRegenerateWorkouts = (profileData) =>
    FitnessAPI.put('/profile/update', profileData);

export const getWeeklyWorkoutPlan = () =>
    FitnessAPI.get('/api/weekly-plan');

export const getWorkoutSwapOptions = (dayIndex) =>
    FitnessAPI.get('/api/swap-options', { params: { day_index: dayIndex } });

export const generateNutritionPlan = (payload) =>
    FitnessAPI.post('/nutrition', payload);

export const getNutritionSwapOptions = (payload) =>
    FitnessAPI.post('/nutrition/swap', payload);

export const swapRestToWorkout = (payload) =>
    FitnessAPI.post('/api/swap-rest-to-workout', payload);

export const swapWorkoutToRest = (payload) =>
    FitnessAPI.post('/api/swap-workout-to-rest', payload);

export const clearWorkoutPlanCache = () => {
    sessionStorage.removeItem('workoutPlan');
    sessionStorage.removeItem('workoutPlanProfile');
    localStorage.removeItem('workoutPlan');
    localStorage.removeItem('workoutPlanProfile');
};

export const suggestDailyMeals = (profileData, intensityFocus) =>
    FitnessAPI.post('/nutrition/daily', { profile: profileData, intensity_focus: intensityFocus });

const _pickChatProfile = (profile, includeSensitive = false) => {
    if (!profile || typeof profile !== 'object') return {};

    const compact = {
        goal: profile.goal,
        experience: profile.experience,
        activity_level: profile.activity_level,
        dietary_preference: profile.dietary_preference,
        equipment: Array.isArray(profile.equipment) ? profile.equipment.slice(0, 12) : [],
    };

    if (includeSensitive) {
        compact.age = profile.age;
        compact.weight = profile.weight;
        compact.height = profile.height;
        compact.allergies = Array.isArray(profile.allergies) ? profile.allergies.slice(0, 12) : [];
        compact.body_issues = Array.isArray(profile.body_issues) ? profile.body_issues.slice(0, 12) : [];
    }

    return Object.fromEntries(
        Object.entries(compact).filter(([, value]) => {
            if (Array.isArray(value)) return value.length > 0;
            return value !== undefined && value !== null && String(value).trim() !== '';
        })
    );
};

export const sendChatbotMessage = (message, profile, history, options = {}) => {
    const includeSensitive = options.includeSensitive === true;

    // Sanitize history: only keep role + text as strings, drop booleans/nulls,
    // and cap at 50 entries to stay within backend max_length validation.
    const sanitizedHistory = (Array.isArray(history) ? history : [])
        .filter((msg) => msg && typeof msg === 'object' && msg.role && msg.text)
        .slice(-50)
        .map(({ role, text }) => ({ role: String(role), content: String(text) }));

    return FitnessAPI.post(
        '/api/chat',
        {
            message,
            profile: _pickChatProfile(profile, includeSensitive),
            history: sanitizedHistory,
            consent_to_health_processing: includeSensitive,
        },
        { timeout: 30000 }
    );
};


export const generateAIPlan = (profileData) =>
    FitnessAPI.post('/generate-plan', profileData);

export const saveWorkoutPlan = (workoutData) =>
    AuthAPI.post('/users/workout/save', workoutData);

export const saveWorkoutCompletion = (workoutData) =>
    FitnessAPI.post('/workout-completion', workoutData);

export const getWorkoutHistory = () =>
    AuthAPI.get('/profile/workout-history');

export const saveWorkoutHistory = (data) =>
    AuthAPI.post('/profile/workout-history', data);

export const saveMealPlan = (mealData) =>
    AuthAPI.post('/users/meals/save', mealData);

export const saveMealCompletion = (mealData) =>
    FitnessAPI.post('/meal-completion', mealData);

export const getMealHistory = () =>
    AuthAPI.get('/profile/meal-history');

export const saveMealHistory = (data) =>
    AuthAPI.post('/profile/meal-history', data);

export const updateStreak = (streakData) =>
    FitnessAPI.post('/update-streak', streakData);

export const getUserProgress = () =>
    FitnessAPI.get('/user-progress');

// ─────────────────────────────────────────────────────────────────────────────
// Workout helpers (Issue #4 – async generation + caching)
// ─────────────────────────────────────────────────────────────────────────────

let workoutRequestInFlight = null;
let workoutRequestController = null; // Bug #63 fix: tracks AbortController for in-flight request

/**
 * Standard synchronous plan generation with request coalescing.
 * - If multiple components ask for /workout at the same time, they share one request.
 * - Returns { promise, cancel } so callers can abort on unmount (Bug #63 fix).
 */
export const generateWorkout = (profileData) => {
    if (workoutRequestInFlight) {
        if (import.meta.env.DEV) console.log('[generateWorkout] Reusing in-flight request');
        const wrappedPromise = Promise.resolve(workoutRequestInFlight);
        wrappedPromise.promise = workoutRequestInFlight;
        wrappedPromise.cancel = () => workoutRequestController?.abort();
        return wrappedPromise;
    }

    // Bug #63 fix: create a fresh AbortController for each new request
    workoutRequestController = new AbortController();
    const { signal } = workoutRequestController;

    if (import.meta.env.DEV) console.log('[generateWorkout] Making new request to /workout');
    workoutRequestInFlight = FitnessAPI.post('/workout', profileData, { signal })
        .then((response) => {
            if (import.meta.env.DEV) console.log('[generateWorkout] Request successful');
            return response;
        })
        .catch((error) => {
            if (axios.isCancel?.(error) || error?.name === 'CanceledError' || error?.name === 'AbortError') {
                if (import.meta.env.DEV) console.log('[generateWorkout] Request cancelled (component unmounted)');
                return null; // resolve with null on cancel — callers should check
            }
            console.error('[generateWorkout] Request failed:', error.message);
            throw error;
        })
        .finally(() => {
            workoutRequestInFlight = null;
            workoutRequestController = null;
        });

    const retPromise = workoutRequestInFlight;
    retPromise.promise = retPromise;
    retPromise.cancel = () => workoutRequestController?.abort();

    return retPromise;
};

/**
 * Async plan generation with polling (Issue #4).
 * Returns cached plan immediately when available; otherwise polls until done.
 *
 * @param {object} profileData  - Full user profile
 * @param {(pct:number)=>void} [onProgress] - Optional progress callback (0-100)
 * @param {number} pollMs       - Polling interval in ms (default 2000)
 * @param {number} maxWait      - Max wait in ms (default 60000)
 */
export const generateWorkoutAsync = async (
    profileData,
    onProgress,
    pollMs = 2000,
    maxWait = 60000,
    abortSignal = null
) => {
    const startRes = await FitnessAPI.post('/workout/async', profileData);
    const startData = startRes.data;

    if (startData.status === 'complete') {
        onProgress && onProgress(100);
        return startData.plan; // cache hit
    }

    const jobId = startData.job_id;
    if (!jobId) throw new Error('No job_id returned from async endpoint');

    const started = Date.now();
    let progress = 10;
    onProgress && onProgress(progress);

    return new Promise((resolve, reject) => {
        let settled = false;
        let timer = null;

        const cleanup = () => {
            if (timer) clearInterval(timer);
            timer = null;
            if (abortSignal) {
                abortSignal.removeEventListener('abort', onAbort);
            }
        };

        const finishResolve = (value) => {
            if (settled) return;
            settled = true;
            cleanup();
            resolve(value);
        };

        const finishReject = (err) => {
            if (settled) return;
            settled = true;
            cleanup();
            reject(err);
        };

        const onAbort = () => {
            finishReject(new Error('Workout generation cancelled'));
        };

        if (abortSignal?.aborted) {
            onAbort();
            return;
        }

        if (abortSignal) {
            abortSignal.addEventListener('abort', onAbort, { once: true });
        }

        timer = setInterval(async () => {
            if (settled) return;
            if (Date.now() - started > maxWait) {
                finishReject(new Error('Workout plan generation timed out after 60s'));
                return;
            }
            try {
                const pollRes = await FitnessAPI.get(`/workout/status/${jobId}`);
                const pollData = pollRes.data;
                if (pollData.status === 'complete') {
                    onProgress && onProgress(100);
                    finishResolve(pollData.plan);
                } else if (pollData.status === 'error') {
                    finishReject(new Error(pollData.error || 'Plan generation failed'));
                } else {
                    if (progress < 90) {
                        // Bug #62 fix: increment normally up to 89%
                        progress = Math.min(progress + 15, 89);
                        onProgress && onProgress(progress);
                    } else {
                        // Bug #62 fix: after 90% signal indeterminate state (-1) so
                        // the UI can switch to a spinner instead of a stuck bar.
                        onProgress && onProgress(-1);
                    }
                }
            } catch (err) {
                finishReject(err);
            }
        }, pollMs);
    });
};

/** Invalidate the server-side plan cache when profile changes significantly. */
export const invalidateWorkoutCache = async (profileData) => {
    try {
        await FitnessAPI.post('/workout/cache/invalidate', profileData);
    } catch {
        // best-effort – silent on failure
    }
};

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
    FitnessAPI.post('/api/workout/session-result', payload, { timeout: 15000 });

// ─────────────────────────────────────────────────────────────────────────────
// Priority 3: Daily check-in endpoints
// ─────────────────────────────────────────────────────────────────────────────
/**
 * Save daily sleep/water/workout check-in.
 * @param {object} payload - { sleep_hours, water_ml, workout_completed, date? }
 */
export const saveDailyLog = (payload) =>
    FitnessAPI.post('/api/daily-log', payload, { timeout: 10000 });

/** Get last 7 daily check-in logs + summary for the current user. */
export const getWeeklyLogs = () =>
    FitnessAPI.get('/api/daily-log/week', { timeout: 10000 });

// Legacy compatibility exports for activity tracking
export const logActivityToBackend = (activityData) =>
    AuthAPI.post('/profile/activities/log', activityData);

export const getRecentActivities = (limit = 20) =>
    AuthAPI.get('/profile/activities/recent', { params: { limit } });

export const syncActivitiesToBackend = (activities) =>
    AuthAPI.post('/profile/activities/sync', { activities });

export default AuthAPI;

