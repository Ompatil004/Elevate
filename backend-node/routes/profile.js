const express = require('express');
const router = express.Router();
const auth = require('../middleware/auth');
const User = require('../models/User');

console.log('🔵 Profile routes loaded');

// GET /api/profile
router.get('/', auth, async (req, res) => {
    try {
        console.log('🔍 GET /api/profile called');
        console.log('👤 User ID from token:', req.user?.id);

        const user = await User.findById(req.user.id).select('-password');

        if (!user) {
            console.log('❌ User not found in database');
            return res.status(404).json({ message: 'User not found' });
        }

        console.log('✅ Profile found:', user.username);
        res.json(user);
    } catch (err) {
        console.error('❌ Error:', err);
        res.status(500).json({ message: 'Server error' });
    }
});

// POST /api/profile/update
router.post('/update', auth, async (req, res) => {
    try {
        console.log('📝 POST /api/profile/update called');
        console.log('👤 User ID:', req.user.id);
        console.log('📦 Data:', req.body);

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
                console.log(`🔄 Field '${field}' changed, triggering workout regeneration`);
                break;
            }
        }

        // Update the user profile
        const user = await User.findByIdAndUpdate(req.user.id, req.body, { new: true }).select('-password');

        // If profile changes require workout regeneration, clear the old plan from frontend cache
        if (shouldRegenerateWorkout) {
            console.log('🔄 Workout plan needs regeneration due to profile changes');
            // In a real implementation, we might want to trigger a background job to regenerate the plan
            // For now, we'll just notify the frontend that it needs to regenerate the plan
        }

        console.log('✅ Profile updated');
        res.json({
            success: true,
            user,
            workout_regeneration_needed: shouldRegenerateWorkout
        });
    } catch (err) {
        console.error('❌ Error:', err);
        res.status(500).json({ success: false, message: err.message });
    }
});

module.exports = router;