const express = require('express');
const router = express.Router();
const auth = require('../middleware/auth');
const User = require('../models/User');
// BUG-N2 fix: import shared helpers from canonical mealUtils module.
const {
  toDateKey,
  inferMealType,
  buildMealData,
  computeTotals,
} = require('../utils/mealUtils');
// ARCH-5: Centralized input validation
const { validate, profileUpdateRules } = require('../middleware/validate');

if (process.env.NODE_ENV !== 'production') {
  console.log('🔵 Profile routes loaded');
}

// Local adapter: convert the shared computeTotals (per-item sum) to a per-day
// mutating helper that existing code in this file already calls.
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

// profile.js calls buildMealData(entry, fallbackType) positionally;
// the shared helper uses a named-param object. Bridge here.
const _buildMealEntry = (entry, fallbackType) => ({
    ...(() => {
        const mealType = entry?.meal_type || entry?.mealType || fallbackType || 'snack';
        const normalized = buildMealData({
            name: entry?.name || (fallbackType ? fallbackType.charAt(0).toUpperCase() + fallbackType.slice(1) : 'Meal'),
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
            completed_at: entry?.completed_at || entry?.completedAt || entry?.timestamp || new Date().toISOString(),
            completed_time_str: entry?.completed_time_str,
            foods: Array.isArray(entry?.foods) ? entry.foods : [],
        };
    })(),
});

const normalizeMealHistory = (rawMeals = []) => {
    const byDate = new Map();

    const upsertMeal = (dateKey, mealType, mealData) => {
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
        day.meals[mealType] = mealData;
        computeDayTotals(day);
    };

    (Array.isArray(rawMeals) ? rawMeals : []).forEach((entry) => {
        if (!entry || typeof entry !== 'object') return;

        if (entry.meals && typeof entry.meals === 'object') {
            const dateKey = toDateKey(entry.date);
            if (!dateKey) return;
            Object.entries(entry.meals).forEach(([mealType, mealValue]) => {
                if (!mealValue || typeof mealValue !== 'object') return;
                upsertMeal(dateKey, mealType, _buildMealEntry(mealValue, mealType));
            });
            return;
        }

        const dateKey = toDateKey(entry.date || entry.dayName || entry.completedAt || entry.timestamp);
        const mealType = inferMealType(entry?.name || '', entry?.meal_type || entry?.mealType || '');
        upsertMeal(dateKey, mealType, _buildMealEntry(entry, mealType));
    });

    return Array.from(byDate.values()).sort((a, b) => (b.date || '').localeCompare(a.date || ''));
};

// GET /api/profile
router.get('/', auth, async (req, res) => {
    try {
        if (process.env.NODE_ENV !== 'production') {
            console.log('🔍 GET /api/profile called, user:', req.user?.id);
        }

        // PERF-2: .lean() returns a plain JS object — 2-3x faster for read-only endpoints.
        const user = await User.findById(req.user.id)
            .select('-password -role -isSuspended -adminLoginAttempts -passwordResetTokenHash -passwordResetTokenExpiresAt')
            .lean();

        if (!user) {
            return res.status(404).json({ message: 'User not found' });
        }

        res.json(user);
    } catch (err) {
        console.error('❌ GET /api/profile error:', err);
        res.status(500).json({ message: 'Server error' });
    }
});

// POST /api/profile/update
router.post('/update', auth, profileUpdateRules(), validate, async (req, res) => {
    try {
        if (process.env.NODE_ENV !== 'production') {
            console.log('📝 POST /api/profile/update, user:', req.user.id);
        }
        // Bug #15 fixed: do NOT log req.body as it may contain sensitive fields

        // Get the current user profile to compare with new data
        const currentUser = await User.findById(req.user.id);
        if (!currentUser) {
            return res.status(404).json({ message: 'User not found' });
        }

        // Fields that should trigger workout plan regeneration
        const profileFieldsThatTriggerRegeneration = [
            'goal', 'experience', 'equipment', 'body_issues', 'days_per_week', 'weight', 'height', 'age'
        ];

        // Check if any of these fields have changed
        let shouldRegenerateWorkout = false;
        for (const field of profileFieldsThatTriggerRegeneration) {
            if (req.body[field] !== undefined && req.body[field] !== currentUser[field]) {
                shouldRegenerateWorkout = true;
                if (process.env.NODE_ENV !== 'production') {
                    console.log(`🔄 Field '${field}' changed, triggering workout regeneration`);
                }
                break;
            }
        }

        // SAFE: Build update object with whitelisted fields only.
        // SEC-7: 'streak' and 'lastWorkoutDate' are intentionally excluded —
        // they must only be set by server-side logic.
        const allowedFields = [
            'name', 'age', 'gender', 'weight', 'height',
            'goal', 'experience', 'dietary_preference',
            'equipment', 'allergies', 'body_issues',
            'days_per_week', 'avatar'
        ];
        const updateData = {};
        for (const field of allowedFields) {
            if (req.body[field] !== undefined) {
                // Ensure array fields stay arrays
                if (['equipment', 'allergies', 'body_issues'].includes(field)) {
                    updateData[field] = Array.isArray(req.body[field]) ? req.body[field] : [];
                } else if (['age', 'weight', 'height'].includes(field)) {
                    const num = Number(req.body[field]);
                    if (!isNaN(num)) updateData[field] = num;
                } else if (field === 'days_per_week') {
                    // Bug #47 fixed: schema defines days_per_week as Number, coerce it
                    const num = Number(req.body[field]);
                    if (!isNaN(num) && num >= 1 && num <= 7) updateData[field] = num;
                } else {
                    updateData[field] = req.body[field];
                }
            }
        }
        updateData.updatedAt = new Date();
        
        const user = await User.findByIdAndUpdate(
            req.user.id,
            { $set: updateData },
            { new: true, runValidators: true }
        ).select('-password');

        if (process.env.NODE_ENV !== 'production') {
            console.log('✅ Profile updated for user:', req.user.id);
        }
        res.json({
            success: true,
            user,
            workout_regeneration_needed: shouldRegenerateWorkout
        });
    } catch (err) {
        console.error('❌ POST /api/profile/update error:', err);
        // BUG-N8: Never expose error.message to client
        res.status(500).json({ success: false, message: 'Server error' });
    }
});

// ==========================================
// HISTORY ENDPOINTS
// ==========================================

// GET /api/profile/workout-history
router.get('/workout-history', auth, async (req, res) => {
    try {
        // PERF-2: read-only — .lean() skips Mongoose document overhead.
        const user = await User.findById(req.user.id).select('workouts').lean();
        if (!user) return res.status(404).json({ message: 'User not found' });
        res.json(user.workouts || []);
    } catch (err) {
        res.status(500).json({ message: 'Server error' });
    }
});

// POST /api/profile/workout-history
router.post('/workout-history', auth, async (req, res) => {
    try {
        // Atomic push to front with slice and prevent full document validation bloat
        const updatedUser = await User.findByIdAndUpdate(
            req.user.id,
            {
                $push: {
                    workouts: {
                        $each: [req.body],
                        $position: 0,
                        $slice: 50
                    }
                }
            },
            { new: true }
        );
        
        res.json({ success: true, history: updatedUser.workouts });
    } catch (err) {
        res.status(500).json({ message: 'Server error' });
    }
});

// GET /api/profile/meal-history
router.get('/meal-history', auth, async (req, res) => {
    try {
        // PERF-2: read-only — .lean() skips Mongoose document overhead.
        const user = await User.findById(req.user.id).select('meals').lean();
        if (!user) return res.status(404).json({ message: 'User not found' });
        // Bug #8 fixed: normalize only for the response — do NOT write back to DB
        // on a GET request to avoid unintended side-effects and race conditions.
        const normalized = normalizeMealHistory(user.meals || []);
        res.json(normalized);
    } catch (err) {
        res.status(500).json({ message: 'Server error' });
    }
});

// POST /api/profile/meal-history
router.post('/meal-history', auth, async (req, res) => {
    try {
        // Bug #7 fixed: use atomic $push with $slice to eliminate the
        // read-modify-write race condition on concurrent requests.
        const incoming = req.body;
        const entries = Array.isArray(incoming) ? incoming : (incoming && typeof incoming === 'object' ? [incoming] : []);

        if (entries.length === 0) {
            const user = await User.findById(req.user.id).select('meals').lean();
            if (!user) return res.status(404).json({ message: 'User not found' });
            return res.json({ success: true, history: normalizeMealHistory(user.meals || []) });
        }

        const updatedUser = await User.findByIdAndUpdate(
            req.user.id,
            {
                $push: {
                    meals: {
                        $each: entries,
                        $slice: -100   // keep the most-recent 100 entries
                    }
                }
            },
            { new: true }
        );

        if (!updatedUser) return res.status(404).json({ message: 'User not found' });

        res.json({ success: true, history: normalizeMealHistory(updatedUser.meals || []) });
    } catch (err) {
        res.status(500).json({ message: 'Server error' });
    }
});


// GET /api/profile/trends
router.get('/trends', auth, async (req, res) => {
    try {
        // PERF-2: read-only — .lean() skips Mongoose document overhead.
        const user = await User.findById(req.user.id).select('trends').lean();
        if (!user) return res.status(404).json({ message: 'User not found' });

        const period = req.query.period || 'week';
        const trends = user.trends || [];

        // Keep response backwards-compatible while supporting optional period filtering.
        if (period === 'all') {
            return res.json(trends);
        }

        const now = new Date();
        const days = period === 'month' ? 30 : 7;
        const cutoff = new Date(now);
        cutoff.setDate(now.getDate() - days);

        const filtered = trends.filter((entry) => {
            const entryDate = new Date(entry?.date);
            return !Number.isNaN(entryDate.getTime()) && entryDate >= cutoff;
        });

        res.json(filtered);
    } catch (err) {
        res.status(500).json({ message: 'Server error' });
    }
});

// POST /api/profile/trends
router.post('/trends', auth, async (req, res) => {
    try {
        const trendData = req.body || {};

        if (!trendData.date) {
            return res.status(400).json({ message: 'date is required' });
        }

        // Bug #28 fixed: use atomic arrayFilters to update the matching date entry
        // without a read-modify-write race. Two-step: try to update existing date entry
        // first; if no entry was matched, push a new one.
        // Convert trendData into dot notation for trends.$ to avoid overwriting existing properties
        const setQuery = {};
        for (const [key, value] of Object.entries(trendData)) {
            if (key !== 'date') { 
                setQuery[`trends.$.${key}`] = value;
            }
        }

        const updateResult = Object.keys(setQuery).length > 0
            ? await User.findOneAndUpdate(
                { _id: req.user.id, 'trends.date': trendData.date },
                { $set: setQuery },
                { new: false }  // we only care if a match occurred
            )
            : await User.findOne({ _id: req.user.id, 'trends.date': trendData.date });

        if (!updateResult) {
            // No existing entry for that date — push a new one, keep max 180.
            const updated = await User.findByIdAndUpdate(
                req.user.id,
                {
                    $push: {
                        trends: {
                            $each: [trendData],
                            $position: 0,
                            $slice: 180
                        }
                    }
                },
                { new: true }
            );
            if (!updated) return res.status(404).json({ message: 'User not found' });
            return res.json({ success: true, trends: updated.trends });
        }

        // Fetch the refreshed document to return latest state
        // PERF-2: read-only refresh — .lean() skips Mongoose document overhead.
        const refreshed = await User.findById(req.user.id).select('trends').lean();
        res.json({ success: true, trends: refreshed?.trends || [] });
    } catch (err) {
        res.status(500).json({ message: 'Server error' });
    }
});



// POST /api/profile/activities/sync
router.post('/activities/sync', auth, async (req, res) => {
    try {
        const user = await User.findById(req.user.id);
        if (!user) return res.status(404).json({ message: 'User not found' });
        const { activities } = req.body;
        if (Array.isArray(activities) && activities.length > 0) {
            // Deduplicate logic
            const existingMap = new Map();
            (user.activities || []).forEach(a => {
                const ts = a.timestamp ? new Date(a.timestamp).getTime() : 0;
                existingMap.set(`${a.type}|${a.name}|${a.details}|${ts || a.date}`, true);
            });
            const newActs = activities.filter(a => {
                const ts = a.timestamp ? new Date(a.timestamp).getTime() : 0;
                return !existingMap.has(`${a.type}|${a.name}|${a.details}|${ts || a.date}`);
            });
            if (newActs.length > 0) {
                user.activities.push(...newActs);
                await user.save();
            }
        }
        res.json({ success: true });
    } catch (err) {
        res.status(500).json({ message: 'Server Error' });
    }
});

// GET /api/profile/activities/recent
router.get('/activities/recent', auth, async (req, res) => {
    try {
        const user = await User.findById(req.user.id).select('activities').lean();
        if (!user) return res.status(404).json({ message: 'User not found' });
        let acts = user.activities || [];
        acts.sort((a, b) => {
            const ta = a.timestamp ? new Date(a.timestamp).getTime() : new Date(a.date).getTime();
            const tb = b.timestamp ? new Date(b.timestamp).getTime() : new Date(b.date).getTime();
            return tb - ta;
        });
        const limit = parseInt(req.query.limit) || 20;
        res.json({ success: true, data: acts.slice(0, limit) });
    } catch (err) {
        res.status(500).json({ message: 'Server Error' });
    }
});

module.exports = router;