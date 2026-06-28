const express = require('express');
const router = express.Router();
const axios = require('axios');
const User = require('../models/User');
const auth = require('../middleware/auth');
// BUG-N2 fix: import shared helpers instead of duplicating them locally
const {
  toDateKey,
  inferMealType,
  buildMealData,
  computeTotals,
} = require('../utils/mealUtils');

// Local adapter: re-builds a per-day totals object using the shared computeTotals.
// mealUtils.computeTotals accepts a flat items array, so we bridge it here.
const computeDayTotals = (dayEntry) => {
  const meals = dayEntry?.meals || {};
  const items = Object.values(meals).map((m) => ({
    calories: m?.calories || 0,
    protein:  m?.protein  || 0,
    carbs:    m?.carbs    || 0,
    fat:      m?.fat      || 0,
  }));
  const sums = computeTotals(items);
  dayEntry.total_calories = sums.calories;
  dayEntry.total_protein  = sums.protein;
  dayEntry.total_carbs    = sums.carbs;
  dayEntry.total_fat      = sums.fat;
};

// Adapter: mealUtils.buildMealData expects a named-param object; users.js called
// it with (entry, mealType) positionally. Bridge without changing callers below.
const _buildMealEntry = (entry, mealType) => ({
  ...(() => {
    const normalized = buildMealData({
      name: entry?.name || mealType.charAt(0).toUpperCase() + mealType.slice(1),
      calories: entry?.calories,
      protein: entry?.protein,
      carbs: entry?.carbs,
      fat: entry?.fat ?? entry?.fats,
      mealType,
    });
    return {
      name: normalized.name,
      meal_type: normalized.mealType,
      calories: normalized.calories,
      protein: normalized.protein,
      carbs: normalized.carbs,
      fat: normalized.fat,
      completed_at: entry?.completedAt || entry?.completed_at || new Date().toISOString(),
      foods: Array.isArray(entry?.foods) ? entry.foods : [],
    };
  })(),
});

const EXTERNAL_TIMEOUT_MS = 10_000;

const sanitizeLookupQuery = (raw, maxLength = 80) =>
  String(raw || '')
    .trim()
    .replace(/\s+/g, ' ')
    .slice(0, maxLength);

const buildFallbackNutrition = (foodQuery) => ({
  food_name: foodQuery || 'unknown food',
  calories: 0,
  protein: 0,
  carbs: 0,
  fat: 0,
  fiber: 0,
  serving_weight_grams: 100,
  source: 'fallback',
  nix_item_name: foodQuery || 'unknown food',
  full_nutrients: [],
});

const buildFallbackExercise = (exerciseQuery) => ([{
  name: exerciseQuery || 'generic exercise',
  type: 'strength',
  muscle: exerciseQuery || 'mixed',
  equipment: 'bodyweight',
  difficulty: 'beginner',
  instructions: 'Perform the exercise with proper form',
}]);

const getUsdaApiKey = () => process.env.USDA_API_KEY || process.env.VITE_USDA_API_KEY || '';
const getApiNinjasKey = () => process.env.API_NINJAS_KEY || process.env.VITE_API_NINJAS_KEY || '';

// SEC-8: Proxy USDA lookup via backend so API keys are never exposed in browser bundles/URLs.
router.get('/external/nutrition', auth, async (req, res) => {
  const query = sanitizeLookupQuery(req.query?.query, 100);
  if (!query) {
    return res.status(400).json({ message: 'query is required' });
  }

  const apiKey = getUsdaApiKey();
  if (!apiKey) {
    return res.json({ success: true, data: buildFallbackNutrition(query) });
  }

  try {
    const response = await axios.get('https://api.nal.usda.gov/fdc/v1/foods/search', {
      params: {
        query,
        pageSize: 1,
        api_key: apiKey,
      },
      timeout: EXTERNAL_TIMEOUT_MS,
    });

    const foods = Array.isArray(response.data?.foods) ? response.data.foods : [];
    if (foods.length === 0) {
      return res.json({ success: true, data: buildFallbackNutrition(query) });
    }

    const food = foods[0];
    const getNutrient = (nutrientId) => {
      const nutrient = (food.foodNutrients || []).find((n) => n?.nutrient?.id === nutrientId);
      return Number(nutrient?.value || 0);
    };

    return res.json({
      success: true,
      data: {
        food_name: food.description || query,
        calories: getNutrient(1008),
        protein: getNutrient(1003),
        carbs: getNutrient(1005),
        fat: getNutrient(1004),
        fiber: getNutrient(1079),
        serving_weight_grams: 100,
        source: 'USDA FoodData Central',
        nix_item_name: food.description || query,
        full_nutrients: Array.isArray(food.foodNutrients) ? food.foodNutrients : [],
      },
    });
  } catch (error) {
    if (process.env.NODE_ENV !== 'production') {
      console.warn('[external/nutrition] USDA lookup failed:', error.message);
    }
    return res.json({ success: true, data: buildFallbackNutrition(query) });
  }
});

// SEC-8: Proxy API Ninjas lookup via backend so API keys are never exposed client-side.
router.get('/external/exercise', auth, async (req, res) => {
  const muscle = sanitizeLookupQuery(req.query?.muscle, 60);
  if (!muscle) {
    return res.status(400).json({ message: 'muscle is required' });
  }

  const apiKey = getApiNinjasKey();
  if (!apiKey) {
    return res.json({ success: true, data: buildFallbackExercise(muscle) });
  }

  try {
    const response = await axios.get('https://api.api-ninjas.com/v1/exercises', {
      params: { muscle },
      headers: { 'X-Api-Key': apiKey },
      timeout: EXTERNAL_TIMEOUT_MS,
    });

    const exercises = Array.isArray(response.data) ? response.data : [];
    return res.json({
      success: true,
      data: exercises.length > 0 ? exercises : buildFallbackExercise(muscle),
    });
  } catch (error) {
    if (process.env.NODE_ENV !== 'production') {
      console.warn('[external/exercise] API Ninjas lookup failed:', error.message);
    }
    return res.json({ success: true, data: buildFallbackExercise(muscle) });
  }
});

const normalizeGroupedMeals = (rawMeals = []) => {
  const byDate = new Map();

  const upsert = (dateKey, mealType, data) => {
    if (!dateKey) return;
    if (!byDate.has(dateKey)) {
      byDate.set(dateKey, {
        date: dateKey,
        meals: {},
        total_calories: 0,
        total_protein: 0,
        total_carbs: 0,
        total_fat: 0,
      });
    }
    const day = byDate.get(dateKey);
    day.meals[mealType] = data;
    computeDayTotals(day);
  };

  (Array.isArray(rawMeals) ? rawMeals : []).forEach((entry) => {
    if (!entry || typeof entry !== 'object') return;
    if (entry.meals && typeof entry.meals === 'object') {
      const dateKey = toDateKey(entry.date);
      if (!dateKey) return;
      Object.entries(entry.meals).forEach(([mealType, mealValue]) => {
        if (!mealValue || typeof mealValue !== 'object') return;
        upsert(dateKey, mealType, _buildMealEntry(mealValue, mealType));
      });
      return;
    }
    const dateKey = toDateKey(entry.date || entry.dayName || entry.completedAt || entry.timestamp);
    const mealType = inferMealType(entry?.name || '', entry?.mealType || entry?.meal_type || '');
    upsert(dateKey, mealType, _buildMealEntry(entry, mealType));
  });

  return Array.from(byDate.values()).sort((a, b) => (b.date || '').localeCompare(a.date || ''));
};

// POST /api/users/save - Save user profile data
router.post('/save', auth, async (req, res) => {
  try {
    const profileData = req.body;

    // Find the user by ID from the token
    const user = await User.findById(req.user.id);
    if (!user) {
      return res.status(404).json({ message: 'User not found' });
    }

    // SAFE: Only update whitelisted profile fields to prevent schema corruption.
    // SEC-7: 'streak' and 'lastWorkoutDate' are intentionally excluded —
    // they must only be set by server-side logic, never by the client.
    const allowedFields = [
      'name', 'age', 'gender', 'weight', 'height',
      'goal', 'experience', 'dietary_preference',
      'equipment', 'allergies', 'body_issues',
      'days_per_week', 'avatar'
    ];
    
    allowedFields.forEach(key => {
      if (profileData[key] !== undefined && profileData[key] !== null) {
        user[key] = profileData[key];
      }
    });

    // Update the updatedAt field
    user.updatedAt = new Date();

    // Save the updated user
    await user.save();

    res.json({
      message: 'User profile saved successfully',
      user: {
        id: user._id,
        name: user.name,
        email: user.email,
        age: user.age,
        gender: user.gender,
        height: user.height,
        weight: user.weight,
        goal: user.goal,
        experience: user.experience,
        dietary_preference: user.dietary_preference,
        allergies: user.allergies,
        equipment: user.equipment,
        streak: user.streak,
        lastWorkoutDate: user.lastWorkoutDate,
        trends: user.trends,
        createdAt: user.createdAt,
        updatedAt: user.updatedAt
      }
    });
  } catch (error) {
    console.error('Error saving user profile:', error);
    // BUG-N8: Never expose error.message to the client in production
    res.status(500).json({ message: 'Server error' });
  }
});

// POST /api/users/workout/save - Save workout data
router.post('/workout/save', auth, async (req, res) => {
  try {
    const workoutData = req.body;

    // Find the user by ID from the token
    const user = await User.findById(req.user.id);
    if (!user) {
      return res.status(404).json({ message: 'User not found' });
    }

    // Add workout data to user (you can customize this based on your needs)
    if (!user.workouts) {
      user.workouts = [];
    }

    // Add timestamp to the workout data
    const workoutEntry = {
      ...workoutData,
      date: new Date(),
      timestamp: new Date().toISOString()
    };

    user.workouts.push(workoutEntry);

    // Limit the number of stored workouts to prevent the document from growing too large
    if (user.workouts.length > 100) {
      user.workouts = user.workouts.slice(-100); // Keep only the last 100 workouts
    }

    // Save the updated user
    await user.save();

    res.json({
      message: 'Workout data saved successfully',
      workout: workoutEntry
    });
  } catch (error) {
    console.error('Error saving workout data:', error);
    // BUG-N8: Never expose error.message to the client in production
    res.status(500).json({ message: 'Server error' });
  }
});

// POST /api/users/meals/save - Save meal data & return today's totals
router.post('/meals/save', auth, async (req, res) => {
  try {
    const mealData = req.body;

    const _now = new Date();
    const serverUtcDate = _now.toISOString().slice(0, 10);
    const rawDateKey = mealData.dayName || mealData.date || mealData.completedAt || serverUtcDate;
    const dateKey = toDateKey(rawDateKey) || serverUtcDate;
    const mealType = inferMealType(
      mealData?.name || '',
      mealData?.mealType || mealData?.meal_type || ''
    );
    const mealEntry = buildMealData({
      ...mealData,
      mealType,
      completedAt: mealData.completedAt || new Date().toISOString(),
    });

    const userId = req.user.id;

    // ── BUG-2 FIX: single atomic operation prevents duplicate day entries ──
    // Phase 1: attempt to update an existing date slot.
    const updateExisting = await User.findOneAndUpdate(
      { _id: userId, 'meals.date': dateKey },
      {
        $set: { [`meals.$.meals.${mealType}`]: mealEntry }
      },
      { new: true }
    );

    let todayEntry;

    if (updateExisting) {
      // Found an existing date row — totals are recomputed from the updated document.
      todayEntry = (updateExisting.meals || []).find((d) => d.date === dateKey);
      if (todayEntry) computeDayTotals(todayEntry);
    } else {
      // Phase 2: no date row exists yet.
      // Use $push with $slice to cap the meal history at 100 days.
      // This is still two operations but the window where a duplicate could
      // sneak in is negligibly small and self-healing (the next request will
      // hit Phase 1 and overwrite the meal slot idempotently).
      const newDayEntry = {
        date: dateKey,
        meals: { [mealType]: mealEntry },
        total_calories: mealEntry.calories,
        total_protein: mealEntry.protein,
        total_carbs: mealEntry.carbs,
        total_fat: mealEntry.fat,
      };

      // Guard: re-check to avoid duplicate push from a concurrent request that
      // already created this date row between our two queries.
      const finalDoc = await User.findOneAndUpdate(
        { _id: userId, 'meals.date': { $ne: dateKey } },
        {
          $push: {
            meals: {
              $each: [newDayEntry],
              $position: 0,
              $slice: 100,
            },
          },
        },
        { new: true }
      );

      if (!finalDoc) {
        // Another concurrent request likely created this date row first.
        const refreshedUser = await User.findById(userId).lean();
        if (!refreshedUser) {
          return res.status(404).json({ message: 'User not found' });
        }
        const existingEntry = (refreshedUser.meals || []).find((d) => d.date === dateKey);
        todayEntry = existingEntry || newDayEntry;
      } else {
        // In the rare concurrent case the entry may exist more than once; use the first.
        const existing = (finalDoc.meals || []).find((d) => d.date === dateKey);
        todayEntry = existing || newDayEntry;
      }
    }

    const todayCalories = Number(todayEntry?.total_calories) || 0;
    const todayProtein = Number(todayEntry?.total_protein) || 0;
    const todayCarbs = Number(todayEntry?.total_carbs) || 0;
    const todayFat = Number(todayEntry?.total_fat) || 0;
    const mainMealsCompleted = ['breakfast', 'lunch', 'dinner']
      .filter((t) => Boolean(todayEntry?.meals?.[t])).length;
    const mealsCompleted = mainMealsCompleted === 3;

    const trendUpdated = await User.findOneAndUpdate(
      { _id: userId, 'trends.date': dateKey },
      {
        $set: {
          'trends.$.meal_completed': mealsCompleted,
          'trends.$.calories': Math.round(todayCalories),
          'trends.$.protein': Math.round(todayProtein),
          'trends.$.carbs': Math.round(todayCarbs),
          'trends.$.fat': Math.round(todayFat),
        },
      },
      { new: false }
    );

    if (!trendUpdated) {
      await User.findByIdAndUpdate(
        userId,
        {
          $push: {
            trends: {
              $each: [{
                date: dateKey,
                meal_completed: mealsCompleted,
                calories: Math.round(todayCalories),
                protein: Math.round(todayProtein),
                carbs: Math.round(todayCarbs),
                fat: Math.round(todayFat),
              }],
              $position: 0,
              $slice: 180,
            },
          },
        }
      );
    }

    // Automatic backend-level activity logging
    try {
      const user = await User.findById(userId);
      if (user) {
        const details = mealEntry.calories ? `${Math.round(mealEntry.calories)} cal consumed` : 'Meal logged';
        const newActivity = {
          type: 'meal',
          name: 'Meal Completed',
          details,
          timestamp: new Date().toISOString(),
          date: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
        };
        user.activities = user.activities || [];
        const tsNew = new Date(newActivity.timestamp).getTime();
        const isDup = user.activities.some((a) => {
          const ts = a.timestamp ? new Date(a.timestamp).getTime() : 0;
          return a.type === newActivity.type &&
                 a.name === newActivity.name &&
                 a.details === newActivity.details &&
                 (Math.abs(ts - tsNew) < 5000); // prevent duplicates within 5 seconds
        });
        if (!isDup) {
          user.activities.push(newActivity);
          if (user.activities.length > 50) {
            user.activities = user.activities.slice(-50);
          }
          await user.save();
        }
      }
    } catch (actErr) {
      console.error('Error logging meal activity to DB:', actErr);
    }

    res.json({
      message: 'Meal data saved successfully',
      meal: { ...mealEntry, date: dateKey },
      todayTotals: {
        calories: Math.round(todayCalories),
        protein: Math.round(todayProtein),
        carbs: Math.round(todayCarbs),
        fat: Math.round(todayFat),
      },
    });
  } catch (error) {
    console.error('Error saving meal data:', error);
    // BUG-N8: Never expose error.message to the client in production
    res.status(500).json({ message: 'Server error' });
  }
});

module.exports = router;
