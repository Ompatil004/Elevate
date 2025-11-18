const axios = require('axios');

// @desc    Test ML route
// @route   GET /api/ml/test
// @access  Public
const testMLRoute = (req, res) => {
  res.json({ msg: 'ML route is working!' });
};

// @desc    Check ML backend health
// @route   GET /api/ml/health
// @access  Public
const checkHealth = async (req, res) => {
  try {
    const response = await axios.get(`${process.env.ML_BACKEND_URL || 'http://localhost:8000'}/health`);
    res.json({ status: 'ML backend is running', details: response.data });
  } catch (error) {
    res.status(500).json({ status: 'ML backend is not accessible', error: error.message });
  }
};

// @desc    Get workout recommendation
// @route   POST /api/ml/recommend-workout
// @access  Private
const getRecommendWorkout = async (req, res) => {
  try {
    const response = await axios.post(`${process.env.ML_BACKEND_URL || 'http://localhost:8000'}/ml/recommend-workout`, req.body, {
      headers: {
        'Content-Type': 'application/json'
      }
    });
    res.json(response.data);
  } catch (error) {
    console.error('Error calling ML backend:', error.message);
    res.status(500).json({ error: 'Error getting workout recommendation', details: error.message });
  }
};

// @desc    Get meal recommendation
// @route   POST /api/ml/recommend-meal
// @access  Private
const getRecommendMeal = async (req, res) => {
  try {
    const response = await axios.post(`${process.env.ML_BACKEND_URL || 'http://localhost:8000'}/ml/recommend-meal`, req.body, {
      headers: {
        'Content-Type': 'application/json'
      }
    });
    res.json(response.data);
  } catch (error) {
    console.error('Error calling ML backend:', error.message);
    res.status(500).json({ error: 'Error getting meal recommendation', details: error.message });
  }
};

// @desc    Chat with the AI assistant
// @route   POST /api/ml/chat
// @access  Private
const chat = async (req, res) => {
  try {
    const response = await axios.post(`${process.env.ML_BACKEND_URL || 'http://localhost:8000'}/ml/chat`, req.body, {
      headers: {
        'Content-Type': 'application/json'
      }
    });
    res.json(response.data);
  } catch (error) {
    console.error('Error calling ML backend:', error.message);
    res.status(500).json({ error: 'Error with chat', details: error.message });
  }
};

// @desc    Generate a creative meal plan
// @route   POST /api/ml/generate-meal-plan-creative
// @access  Private
const generateCreativeMealPlan = async (req, res) => {
  try {
    const response = await axios.post(`${process.env.ML_BACKEND_URL || 'http://localhost:8000'}/ml/generate-meal-plan-creative`, req.body, {
      headers: {
        'Content-Type': 'application/json'
      }
    });
    res.json(response.data);
  } catch (error) {
    console.error('Error calling ML backend:', error.message);
    res.status(500).json({ error: 'Error generating meal plan', details: error.message });
  }
};

// @desc    Start exercise tracking session
// @route   POST /api/ml/start-exercise-tracking
// @access  Private
const startExerciseTracking = async (req, res) => {
  try {
    const response = await axios.post(`${process.env.ML_BACKEND_URL || 'http://localhost:8000'}/ml/start-exercise-tracking`, req.body, {
      headers: {
        'Content-Type': 'application/json'
      }
    });
    res.json(response.data);
  } catch (error) {
    console.error('Error calling ML backend:', error.message);
    res.status(500).json({ error: 'Error starting exercise tracking', details: error.message });
  }
};

// @desc    Get list of supported exercises
// @route   GET /api/ml/get-supported-exercises
// @access  Private
const getSupportedExercises = async (req, res) => {
  try {
    const response = await axios.get(`${process.env.ML_BACKEND_URL || 'http://localhost:8000'}/ml/get-supported-exercises`);
    res.json(response.data);
  } catch (error) {
    console.error('Error calling ML backend:', error.message);
    res.status(500).json({ error: 'Error getting supported exercises', details: error.message });
  }
};

module.exports = {
  testMLRoute,
  checkHealth,
  getRecommendWorkout,
  getRecommendMeal,
  chat,
  generateCreativeMealPlan,
  startExerciseTracking,
  getSupportedExercises
};