/**
 * sessionUtils.js
 *
 * BUG-F10 fix: clearUserScopedCache() and syncUserSession() were duplicated
 * identically in both Login.jsx and Register.jsx. Extracted here as the single
 * authoritative source so a bug fix or cache-key addition only needs to happen
 * in one place.
 */

import { StorageKeys } from './storage';

export const buildSessionUser = (user = {}) => ({
  id: user.id || user._id || null,
  _id: user._id || user.id || null,
  email: user.email || '',
  name: user.name || user.full_name || '',
  full_name: user.full_name || user.name || '',
  age: user.age ?? null,
  weight: user.weight ?? null,
  height: user.height ?? null,
  gender: user.gender || null,
  goal: user.goal || null,
  experience: user.experience || null,
  dietary_preference: user.dietary_preference || null,
  allergies: Array.isArray(user.allergies) ? user.allergies : [],
  equipment: Array.isArray(user.equipment) ? user.equipment : [],
  body_issues: Array.isArray(user.body_issues) ? user.body_issues : [],
  days_per_week: user.days_per_week ?? null,
  avatar: user.avatar || null,
  firstWorkoutDay: user.firstWorkoutDay ?? null,
  registrationDate: user.registrationDate ?? null,
  profileComplete: Boolean(user.profileComplete),
});

export const persistSessionUser = (user = {}) => {
  try {
    sessionStorage.setItem('user', JSON.stringify(buildSessionUser(user)));
    localStorage.removeItem('user');
    return true;
  } catch {
    return false;
  }
};

/**
 * Removes all cache keys that are scoped to the currently logged-in user.
 * Call this before writing a new session so stale data from a previous user
 * session is never served to the incoming user.
 */
export const clearUserScopedCache = () => {
  const scopedKeys = [
    StorageKeys.NUTRITION_CACHE,
    StorageKeys.NUTRITION_CACHE_DATE,
    StorageKeys.NUTRITION_CACHE_INVALID,
    StorageKeys.TODAY_WORKOUT_DONE,
    StorageKeys.TODAY_MEALS_DONE,
    StorageKeys.WATER_INTAKE,
    StorageKeys.SLEEP_HOURS,
    StorageKeys.ACTIVITY_HISTORY,
    StorageKeys.USER_AVATAR,
    'workoutPlan',
    'workoutPlanTimestamp',
    'workoutPlanProfile',
    'checkedFoods',
    'lockedMeals',
    'tickTimes',
    'todayProgressStatus',
    '_macroSync',
  ];
  scopedKeys.forEach((k) => {
    localStorage.removeItem(k);
    sessionStorage.removeItem(k);
  });
};

/**
 * Compares the incoming user's identity against the previously stored session.
 * If the identity changed (different user logged in) clear the user-scoped cache
 * so the incoming user never sees the previous user's data.
 *
 * @param {object} newUser - User object from the login/register API response.
 */
export const syncUserSession = (newUser) => {
  let prev = {};
  try {
    prev = JSON.parse(sessionStorage.getItem('user') || '{}');
  } catch {
    prev = {};
  }
  const prevIdentity = prev?.id || prev?.email || '';
  const nextIdentity = newUser?.id || newUser?.email || '';
  if (prevIdentity && nextIdentity && prevIdentity !== nextIdentity) {
    clearUserScopedCache();
  }
};
