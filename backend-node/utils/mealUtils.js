/**
 * mealUtils.js
 *
 * BUG-N2 fix: These helpers were duplicated (with minor variations) across
 * both routes/users.js and routes/profile.js. Extracted here as the single
 * authoritative source to eliminate maintenance burden and drift.
 */

'use strict';

// ---- Date helpers ----------------------------------------------------------

/**
 * Converts a Date object or ISO string to a YYYY-MM-DD key in IST.
 * @param {Date|string} [date=new Date()]
 * @returns {string}
 */
const toDateKey = (date = new Date()) => {
  const d = date instanceof Date ? date : new Date(date);
  if (Number.isNaN(d.getTime())) return '';
  // Use IST offset (+05:30 = 330 minutes)
  const ist = new Date(d.getTime() + 330 * 60 * 1000);
  return ist.toISOString().slice(0, 10);
};

// ---- Meal type inference ----------------------------------------------------

const MEAL_TYPE_ORDER = ['breakfast', 'lunch', 'dinner', 'snack', 'pre_workout', 'post_workout'];

/**
 * Infers a meal type from common food names if not explicitly provided.
 * @param {string} [name='']
 * @param {string} [explicit='']
 * @returns {string}
 */
const inferMealType = (name = '', explicit = '') => {
  if (explicit) return explicit.toLowerCase();
  const n = name.toLowerCase();
  if (/breakfast|oat|egg|pancake|cereal|toast/.test(n)) return 'breakfast';
  if (/lunch|salad|sandwich|wrap/.test(n)) return 'lunch';
  if (/dinner|rice|chicken|pasta|steak/.test(n)) return 'dinner';
  if (/snack|bar|fruit|nuts|yogurt/.test(n)) return 'snack';
  if (/pre.*workout|pre-workout/.test(n)) return 'pre_workout';
  if (/post.*workout|post-workout|protein shake/.test(n)) return 'post_workout';
  return 'snack'; // safe default
};

// ---- Macro computation -----------------------------------------------------

/**
 * Sums macro totals across an array of meal items.
 * @param {Array<{calories?:number, protein?:number, carbs?:number, fat?:number}>} items
 * @returns {{ calories:number, protein:number, carbs:number, fat:number }}
 */
const computeTotals = (items = []) => {
  return items.reduce(
    (acc, item) => {
      acc.calories += Number(item.calories) || 0;
      acc.protein  += Number(item.protein)  || 0;
      acc.carbs    += Number(item.carbs)    || 0;
      acc.fat      += Number(item.fat)      || 0;
      return acc;
    },
    { calories: 0, protein: 0, carbs: 0, fat: 0 }
  );
};

// ---- Meal data builder ------------------------------------------------------

/**
 * Constructs a normalized meal entry object ready for MongoDB storage.
 * @param {object} params
 * @returns {object}
 */
const buildMealData = ({ name, calories, protein, carbs, fat, mealType, foodId }) => ({
  name:      String(name     || '').trim(),
  calories:  Number(calories || 0),
  protein:   Number(protein  || 0),
  carbs:     Number(carbs    || 0),
  fat:       Number(fat      || 0),
  mealType:  String(mealType || 'snack').toLowerCase(),
  foodId:    foodId || null,
  savedAt:   new Date(),
});

// ---- History normalizers ----------------------------------------------------

/**
 * Normalizes a flat meal history array (one entry per day).
 * @param {Array} raw
 * @returns {Array}
 */
const normalizeMealHistory = (raw = []) => {
  if (!Array.isArray(raw)) return [];
  return raw
    .filter((entry) => entry && typeof entry === 'object' && entry.date)
    .map((entry) => ({
      date:   entry.date,
      meals:  Array.isArray(entry.meals) ? entry.meals : [],
      totals: computeTotals(Array.isArray(entry.meals) ? entry.meals : []),
    }));
};

module.exports = {
  MEAL_TYPE_ORDER,
  toDateKey,
  inferMealType,
  computeTotals,
  buildMealData,
  normalizeMealHistory,
};
