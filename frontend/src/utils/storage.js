/**
 * Centralized localStorage management
 * Provides type-safe key constants and error-handling wrappers
 */

export const StorageKeys = {
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

/**
 * Safe retrieval from localStorage with error handling
 * @param {string} key - Storage key
 * @param {any} defaultValue - Default value if key not found
 * @returns {any} Retrieved value or defaultValue
 */
export const getFromStorage = (key, defaultValue = null) => {
  try {
    const item = localStorage.getItem(key);
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
    localStorage.setItem(key, stringValue);
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
    localStorage.removeItem(key);
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
      const stringValue = typeof value === 'string' ? value : JSON.stringify(value);
      localStorage.setItem(key, stringValue);
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
    return localStorage.getItem(key) !== null;
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
      if (localStorage.hasOwnProperty(key)) {
        size += localStorage[key].length + key.length;
      }
    }
    return size;
  } catch (error) {
    console.warn('[Storage] Error calculating storage size:', error.message);
    return 0;
  }
};