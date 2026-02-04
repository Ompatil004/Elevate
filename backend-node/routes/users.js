const express = require('express');
const router = express.Router();
const User = require('../models/User');
const auth = require('../middleware/auth'); // ADD THIS

// Test route to verify the file is loaded
router.get('/test', (req, res) => {
  res.json({ message: 'Users route is loaded correctly!' });
});

// POST /api/users/save - Save user profile data
router.post('/save', auth, async (req, res) => {
  try {
    const profileData = req.body;

    // Find the user by ID from the token
    const user = await User.findById(req.user.userId || req.user.id);
    if (!user) {
      return res.status(404).json({ message: 'User not found' });
    }

    // Update user profile with the provided data
    Object.keys(profileData).forEach(key => {
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
    res.status(500).json({ message: 'Server error', error: error.message });
  }
});

// POST /api/users/workout/save - Save workout data
router.post('/workout/save', auth, async (req, res) => {
  try {
    const workoutData = req.body;

    // Find the user by ID from the token
    const user = await User.findById(req.user.userId || req.user.id);
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
    res.status(500).json({ message: 'Server error', error: error.message });
  }
});

// POST /api/users/meals/save - Save meal data
router.post('/meals/save', auth, async (req, res) => {
  try {
    const mealData = req.body;

    // Find the user by ID from the token
    const user = await User.findById(req.user.userId || req.user.id);
    if (!user) {
      return res.status(404).json({ message: 'User not found' });
    }

    // Add meal data to user (you can customize this based on your needs)
    if (!user.meals) {
      user.meals = [];
    }

    // Add timestamp to the meal data
    const mealEntry = {
      ...mealData,
      date: new Date(),
      timestamp: new Date().toISOString()
    };

    user.meals.push(mealEntry);

    // Limit the number of stored meals to prevent the document from growing too large
    if (user.meals.length > 100) {
      user.meals = user.meals.slice(-100); // Keep only the last 100 meals
    }

    // Save the updated user
    await user.save();

    res.json({
      message: 'Meal data saved successfully',
      meal: mealEntry
    });
  } catch (error) {
    console.error('Error saving meal data:', error);
    res.status(500).json({ message: 'Server error', error: error.message });
  }
});

module.exports = router;