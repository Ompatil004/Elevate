const express = require('express');
const axios = require('axios');
const auth = require('../middleware/auth');
const {
  testMLRoute,
  checkHealth,
  getRecommendWorkout,
  getRecommendMeal,
  chat,
  generateCreativeMealPlan,
  startExerciseTracking,
  getSupportedExercises
} = require('../controllers/MLController');

const router = express.Router();

// @route    GET api/ml/test
// @desc     Test ML route
// @access   Public
router.get('/test', testMLRoute);

// @route    GET api/ml/health
// @desc     Check ML backend health
// @access   Public
router.get('/health', checkHealth);

// @route    POST api/ml/recommend-workout
// @desc     Get workout recommendation
// @access   Private
router.post('/recommend-workout', auth, getRecommendWorkout);

// @route    POST api/ml/recommend-meal
// @desc     Get meal recommendation
// @access   Private
router.post('/recommend-meal', auth, getRecommendMeal);

// @route    POST api/ml/chat
// @desc     Chat with the AI assistant
// @access   Private
router.post('/chat', auth, chat);

// @route    POST api/ml/generate-meal-plan-creative
// @desc     Generate a creative meal plan
// @access   Private
router.post('/generate-meal-plan-creative', auth, generateCreativeMealPlan);

// @route    POST api/ml/start-exercise-tracking
// @desc     Start exercise tracking session
// @access   Private
router.post('/start-exercise-tracking', auth, startExerciseTracking);

// @route    GET api/ml/get-supported-exercises
// @desc     Get list of supported exercises
// @access   Private
router.get('/get-supported-exercises', auth, getSupportedExercises);

// Note: Personalized recommendations remain in this file as they use User model
// @route    POST api/ml/get-personalized-recommendations
// @desc     Get personalized meal and workout recommendations based on user profile
// @access   Private
router.post('/get-personalized-recommendations', auth, async (req, res) => {
  try {
    // Get the user's profile data
    const User = require('../models/User');
    const user = await User.findById(req.user.id);

    if (!user) {
      return res.status(404).json({ error: 'User not found' });
    }

    // Prepare data for ML model requests based on user profile
    const workoutData = {
      goal: user.fitnessGoals && user.fitnessGoals.length > 0 ? user.fitnessGoals[0] : 'Strength',
      experience: user.experienceLevel || 'Beginner',
      equipment_available: user.equipmentAvailable || [],
      time_available: user.timeAvailable || 30,
      target_muscle_group: user.targetMuscleGroup || 'full-body',
      injury_history: user.injuryHistory || [],
      preferred_exercise_type: user.preferredExerciseType || 'cardio',
      intensity_level: user.intensityLevel || 'moderate',
      frequency_per_week: user.frequencyPerWeek || 3,
      focus_area: user.focusArea || 'strength',
      gym_or_home: user.gymOrHome || 'home',
      specific_body_part: user.targetMuscleGroup || null
    };

    const mealData = {
      goal: user.fitnessGoals && user.fitnessGoals.length > 0 ? user.fitnessGoals[0] : 'Maintain',
      calorie_target: user.weight ? Math.round(user.weight * 22) / 3 : 600, // Approximate daily calorie divided by 3 for single meal
      meal_type: req.body.meal_type || 'Lunch',
      dietary_restrictions: user.dietaryPreferences || [],
      allergies: user.allergies || [],
      meal_time: user.mealTime || 'moderate',
      budget: user.budget || 15,
      protein_target: user.proteinTarget || 25,
      carb_target: user.carbTarget || 45,
      fat_target: user.fatTarget || 15,
      preferred_cuisine: user.preferredCuisine || 'italian',
      cooking_skill: user.cookingSkill || 'intermediate',
      ingredients: user.ingredients || [],
      avoid_ingredients: user.avoidIngredients || [],
      spice_level: user.spiceLevel || 3,
      prep_time: user.prepTime || 30
    };

    // Make requests to ML backend for both workout and meal recommendations
    const [workoutResponse, mealResponse] = await Promise.allSettled([
      axios.post(`${process.env.ML_BACKEND_URL || 'http://localhost:8000'}/ml/recommend-workout`, workoutData, {
        headers: { 'Content-Type': 'application/json' }
      }),
      axios.post(`${process.env.ML_BACKEND_URL || 'http://localhost:8000'}/ml/recommend-meal`, mealData, {
        headers: { 'Content-Type': 'application/json' }
      })
    ]);

    const recommendations = {
      workout: workoutResponse.status === 'fulfilled' ? workoutResponse.value.data : { error: 'Workout recommendation failed' },
      meal: mealResponse.status === 'fulfilled' ? mealResponse.value.data : { error: 'Meal recommendation failed' }
    };

    res.json(recommendations);
  } catch (error) {
    console.error('Error getting personalized recommendations:', error.message);
    res.status(500).json({ error: 'Error getting personalized recommendations', details: error.message });
  }
});

module.exports = router;