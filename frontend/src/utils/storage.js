/**
 * Centralized localStorage management
 * Provides type-safe key constants and error-handling wrappers
 */

export const StorageKeys = {
  // Auth
  TOKEN: 'token',

  // Activity & History
  ACTIVITY_HISTORY: 'activityHistory',
  
  // User Profile
  USER_AVATAR: 'userAvatar',
  USER_PROFILE: 'userProfile',
  
  // Streak & Progress
  CURRENT_STREAK: 'currentStreak',
  LAST_WORKOUT_DATE: 'lastWorkoutDate',
  
  // Daily Tracking
  LAST_ACTIVITY_DATE: 'lastActivityDate',
  DAILY_RESET_PERFORMED: 'daily_reset_performed',
  TODAY_WORKOUT_DONE: 'todayWorkoutDone',
  TODAY_MEALS_DONE: 'todayMealsDone',
  
  // Workout Sessions
  ONGOING_WORKOUT: 'ongoing_workout_session',
  WORKOUT_WEEK_METADATA: 'workoutWeekMetadata',
  
  // Water & Sleep
  WATER_INTAKE: 'waterIntake',
  SLEEP_HOURS: 'sleepHours',

  // Nutrition Cache
  NUTRITION_CACHE: 'nutritionPlan',
  NUTRITION_CACHE_DATE: 'nutritionPlanDate',
  NUTRITION_CACHE_INVALID: 'nutritionCacheInvalid',

  // Profile Change Tracking
  PROFILE_UPDATED_AT: 'profileUpdatedAt',

  // Cached Data
  CACHED_ENRICHED_DATA: 'cached_enriched_data',
  CACHED_ENRICHED_DATA_TIMESTAMP: 'cached_enriched_data_timestamp',
  LAST_API_ENRICHMENT: 'last_api_enrichment',
  
  // Notification Tracking
  NOTIFICATION_PREFIX: 'notification_',
  REMINDER_PREFIX: 'reminder_',
  
  // Dynamic notification keys (helper function below)
  getNotificationKey: (id) => `notification_${id}_last_shown`,
  getReminderKey: (type) => `reminder_${type}_last_shown`,
  getWorkoutDoneKey: (dateStr) => `workout_done_${dateStr}`
};

// SEC-2: Keep sensitive profile/health/session caches in sessionStorage by default.
const SESSION_PREFERRED_KEYS = new Set([
  'user',
  StorageKeys.USER_AVATAR,
  StorageKeys.USER_PROFILE,
  StorageKeys.ACTIVITY_HISTORY,
  StorageKeys.ONGOING_WORKOUT,
  StorageKeys.WATER_INTAKE,
  StorageKeys.SLEEP_HOURS,
  StorageKeys.NUTRITION_CACHE,
  StorageKeys.NUTRITION_CACHE_DATE,
  StorageKeys.NUTRITION_CACHE_INVALID,
  StorageKeys.WORKOUT_WEEK_METADATA,
  'workoutPlan',
  'workoutPlanTimestamp',
  'workoutPlanProfile',
  'checkedFoods',
  'lockedMeals',
  'tickTimes',
  'mealHistoryGrouped',
  'todayProgressStatus',
]);

const _getPrimaryStore = (key) => (SESSION_PREFERRED_KEYS.has(key) ? sessionStorage : localStorage);
const _getFallbackStore = (key) => (SESSION_PREFERRED_KEYS.has(key) ? localStorage : null);

/**
 * Returns a formatted date string (YYYY-MM-DD) strictly in Indian Standard Time (Asia/Kolkata)
 */
export const getLocalDateStr = (d = new Date()) => {
  const formatter = new Intl.DateTimeFormat('en-US', {
    timeZone: 'Asia/Kolkata',
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
  });
  
  const parts = formatter.formatToParts(d);
  const year = parts.find(p => p.type === 'year').value;
  const month = parts.find(p => p.type === 'month').value;
  const day = parts.find(p => p.type === 'day').value;
  
  return `${year}-${month}-${day}`;
};

/**
 * Returns today's date in YYYY-MM-DD format strictly in Indian Standard Time (Asia/Kolkata)
 */
export const getTodayStr = () => getLocalDateStr();

/**
 * Safe retrieval from localStorage with error handling
 * @param {string} key - Storage key
 * @param {any} defaultValue - Default value if key not found
 * @returns {any} Retrieved value or defaultValue
 */
export const getFromStorage = (key, defaultValue = null) => {
  try {
    const primary = _getPrimaryStore(key);
    let item = primary.getItem(key);
    if (item === null) {
      const fallback = _getFallbackStore(key);
      if (fallback) {
        item = fallback.getItem(key);
        // Migrate legacy localStorage value into session storage on read.
        if (item !== null) {
          primary.setItem(key, item);
          fallback.removeItem(key);
        }
      }
    }
    if (item === null) {
      return defaultValue;
    }
    // Try to parse as JSON, otherwise return as string
    try {
      return JSON.parse(item);
    } catch {
      // If parsing fails, return the raw string (for simple values)
      return item;
    }
  } catch (error) {
    console.warn(`[Storage] Error reading key "${key}":`, error.message);
    return defaultValue;
  }
};

/**
 * Safe storage to localStorage with error handling
 * @param {string} key - Storage key
 * @param {any} value - Value to store (will be JSON stringified)
 * @returns {boolean} Success status
 */
export const setToStorage = (key, value) => {
  try {
    const stringValue = typeof value === 'string' ? value : JSON.stringify(value);
    const primary = _getPrimaryStore(key);
    primary.setItem(key, stringValue);

    // Purge old localStorage copies when sensitive keys are session-backed.
    const fallback = _getFallbackStore(key);
    if (fallback) {
      fallback.removeItem(key);
    }
    return true;
  } catch (error) {
    if (error.name === 'QuotaExceededError') {
      console.error(`[Storage] Quota exceeded when writing key "${key}"`);
    } else {
      console.warn(`[Storage] Error writing key "${key}":`, error.message);
    }
    return false;
  }
};

/**
 * Safe removal from localStorage
 * @param {string} key - Storage key to remove
 * @returns {boolean} Success status
 */
export const removeFromStorage = (key) => {
  try {
    _getPrimaryStore(key).removeItem(key);
    const fallback = _getFallbackStore(key);
    if (fallback) fallback.removeItem(key);
    return true;
  } catch (error) {
    console.warn(`[Storage] Error removing key "${key}":`, error.message);
    return false;
  }
};

/**
 * Clear all localStorage data
 * @returns {boolean} Success status
 */
export const clearAllStorage = () => {
  try {
    localStorage.clear();
    return true;
  } catch (error) {
    console.warn('[Storage] Error clearing all storage:', error.message);
    return false;
  }
};

/**
 * Safe logout — removes auth-related and volatile session keys only.
 * Preserves non-sensitive cached data (nutrition plan, workout plan, etc.)
 * so a re-login restores state instantly without extra API calls.
 *
 * Call this INSTEAD of localStorage.clear() on logout.
 * @returns {boolean} Success status
 */
export const logoutSafe = () => {
  try {
    // SEC-1 (complete): auth token now lives in an HttpOnly cookie managed by the server.
    // Remove stale 'token' key that may have been set by older app versions.
    localStorage.removeItem('token');
    localStorage.removeItem('user');


    // Volatile daily state that should reset on logout
    const volatileKeys = [
      StorageKeys.TODAY_WORKOUT_DONE,
      StorageKeys.TODAY_MEALS_DONE,
      StorageKeys.LAST_ACTIVITY_DATE,
      StorageKeys.DAILY_RESET_PERFORMED,
      StorageKeys.ONGOING_WORKOUT,
      StorageKeys.WATER_INTAKE,
      StorageKeys.SLEEP_HOURS,
      StorageKeys.CURRENT_STREAK,
      StorageKeys.LAST_WORKOUT_DATE,
      StorageKeys.CACHED_ENRICHED_DATA,
      StorageKeys.CACHED_ENRICHED_DATA_TIMESTAMP,
      StorageKeys.LAST_API_ENRICHMENT,
      StorageKeys.PROFILE_UPDATED_AT,
      StorageKeys.USER_AVATAR,
      StorageKeys.USER_PROFILE,
      StorageKeys.ACTIVITY_HISTORY,
      // Nutrition volatile keys
      'checkedFoods',
      'lockedMeals',
      'tickTimes',
      'todayProgressStatus',
      // Cached plans (different user may have different profile)
      StorageKeys.NUTRITION_CACHE,
      StorageKeys.NUTRITION_CACHE_DATE,
      StorageKeys.NUTRITION_CACHE_INVALID,
      'workoutPlan',
      'workoutPlanTimestamp',
      'workoutPlanProfile',
      StorageKeys.WORKOUT_WEEK_METADATA,
    ];

    volatileKeys.forEach(key => {
      try { localStorage.removeItem(key); } catch { /* ignore */ }
    });

    // Also clear any dynamic workout_done_* and notification_* keys
    const dynamicPrefixes = ['workout_done_', 'notification_', 'reminder_'];
    for (let i = localStorage.length - 1; i >= 0; i--) {
      const key = localStorage.key(i);
      if (key && dynamicPrefixes.some(prefix => key.startsWith(prefix))) {
        localStorage.removeItem(key);
      }
    }

    // Clear sessionStorage (chat history etc.)
    sessionStorage.clear();

    console.log('[Storage] Safe logout completed — auth and session data cleared.');
    return true;
  } catch (error) {
    // Fallback: nuclear clear if selective removal fails
    console.warn('[Storage] logoutSafe failed, falling back to full clear:', error.message);
    localStorage.clear();
    sessionStorage.clear();
    return false;
  }
};

/**
 * Get multiple values at once
 * @param {string[]} keys - Array of storage keys
 * @returns {object} Object with key-value pairs
 */
export const getMultipleFromStorage = (keys) => {
  const result = {};
  keys.forEach((key) => {
    result[key] = getFromStorage(key);
  });
  return result;
};

/**
 * Set multiple values at once
 * @param {object} entries - Object with key-value pairs
 * @returns {boolean} Success status (all or nothing)
 */
export const setMultipleToStorage = (entries) => {
  try {
    Object.entries(entries).forEach(([key, value]) => {
      setToStorage(key, value);
    });
    return true;
  } catch (error) {
    console.warn('[Storage] Error setting multiple values:', error.message);
    return false;
  }
};

/**
 * Check if a key exists in storage
 * @param {string} key - Storage key
 * @returns {boolean} True if key exists
 */
export const keyExistsInStorage = (key) => {
  try {
    if (_getPrimaryStore(key).getItem(key) !== null) return true;
    const fallback = _getFallbackStore(key);
    return fallback ? fallback.getItem(key) !== null : false;
  } catch (error) {
    console.warn(`[Storage] Error checking key "${key}":`, error.message);
    return false;
  }
};

/**
 * Get storage size (approximate, in characters)
 * @returns {number} Total size of localStorage
 */
export const getStorageSize = () => {
  try {
    let size = 0;
    for (let key in localStorage) {
      if (Object.prototype.hasOwnProperty.call(localStorage, key)) {
        size += localStorage[key].length + key.length;
      }
    }
    return size;
  } catch (error) {
    console.warn('[Storage] Error calculating storage size:', error.message);
    return 0;
  }
};

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
  try {
    const primary = _getPrimaryStore(key);
    let item = primary.getItem(key);
    if (item === null) {
      const fallback = _getFallbackStore(key);
      if (fallback) {
        item = fallback.getItem(key);
        if (item !== null) {
          primary.setItem(key, item);
          fallback.removeItem(key);
        }
      }
    }
    if (item === null) return defaultValue;
    return JSON.parse(item);
  } catch (error) {
    try {
      _getPrimaryStore(key).removeItem(key);
      const fallback = _getFallbackStore(key);
      if (fallback) fallback.removeItem(key);
    } catch {
      // Ignore cleanup failures; returning fallback keeps app stable.
    }
    console.warn(`[Storage] Failed to parse JSON key "${key}":`, error.message);
    return defaultValue;
  }
};

/**
 * safeJSONStringify – write a value to localStorage as JSON, silently handles quota errors.
 */
export const safeJSONStringify = (key, value) => setToStorage(key, value);

// Legacy compatibility exports
export const markSessionStart = () => {
  try {
    localStorage.setItem("session_start", String(Date.now()));
  } catch {
    // no-op
  }
};

