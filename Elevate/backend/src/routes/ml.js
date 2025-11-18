const express = require('express');
const router = express.Router();
const axios = require('axios');
const auth = require('../middleware/auth');

// @route   POST api/ml/recommend-workout
// @desc    Get workout recommendations from ML model
// @access  Private
router.post('/recommend-workout', auth, async (req, res) => {
  try {
    const mlResponse = await axios.post(`${process.env.ML_BACKEND_URL || 'http://localhost:8000'}/ml/recommend-workout`, req.body);
    res.json(mlResponse.data);
  } catch (error) {
    console.error('ML Workout Recommendation error:', error.message);
    res.status(500).json({ msg: 'Error getting workout recommendations from ML model', error: error.message });
  }
});

// @route   POST api/ml/recommend-meal
// @desc    Get meal recommendations from ML model
// @access  Private
router.post('/recommend-meal', auth, async (req, res) => {
  try {
    const mlResponse = await axios.post(`${process.env.ML_BACKEND_URL || 'http://localhost:8000'}/ml/recommend-meal`, req.body);
    res.json(mlResponse.data);
  } catch (error) {
    console.error('ML Meal Recommendation error:', error.message);
    res.status(500).json({ msg: 'Error getting meal recommendations from ML model', error: error.message });
  }
});

// @route   POST api/ml/chat
// @desc    Chat with AI health assistant
// @access  Private
router.post('/chat', auth, async (req, res) => {
  try {
    const mlResponse = await axios.post(`${process.env.ML_BACKEND_URL || 'http://localhost:8000'}/ml/chat`, req.body);
    res.json(mlResponse.data);
  } catch (error) {
    console.error('ML Chat error:', error.message);
    res.status(500).json({ msg: 'Error communicating with AI health assistant', error: error.message });
  }
});

// @route   POST api/ml/generate-meal-plan-creative
// @desc    Generate creative meal plan using Gemini
// @access  Private
router.post('/generate-meal-plan-creative', auth, async (req, res) => {
  try {
    const mlResponse = await axios.post(`${process.env.ML_BACKEND_URL || 'http://localhost:8000'}/ml/generate-meal-plan-creative`, req.body);
    res.json(mlResponse.data);
  } catch (error) {
    console.error('ML Creative Meal Plan error:', error.message);
    res.status(500).json({ msg: 'Error generating creative meal plan', error: error.message });
  }
});

// @route   POST api/ml/start-exercise-tracking
// @desc    Start exercise tracking with computer vision
// @access  Private
router.post('/start-exercise-tracking', auth, async (req, res) => {
  try {
    const mlResponse = await axios.post(`${process.env.ML_BACKEND_URL || 'http://localhost:8000'}/ml/start-exercise-tracking`, req.body);
    res.json(mlResponse.data);
  } catch (error) {
    console.error('ML Exercise Tracking error:', error.message);
    res.status(500).json({ msg: 'Error starting exercise tracking', error: error.message });
  }
});

// @route   GET api/ml/get-supported-exercises
// @desc    Get list of supported exercises for computer vision
// @access  Private
router.get('/get-supported-exercises', auth, async (req, res) => {
  try {
    const mlResponse = await axios.get(`${process.env.ML_BACKEND_URL || 'http://localhost:8000'}/ml/get-supported-exercises`);
    res.json(mlResponse.data);
  } catch (error) {
    console.error('ML Supported Exercises error:', error.message);
    res.status(500).json({ msg: 'Error getting supported exercises', error: error.message });
  }
});

// @route   GET api/ml/health
// @desc    Get ML model status
// @access  Public
router.get('/health', async (req, res) => {
  try {
    const mlResponse = await axios.get(`${process.env.ML_BACKEND_URL || 'http://localhost:8000'}`);
    res.json(mlResponse.data);
  } catch (error) {
    console.error('ML Health check error:', error.message);
    res.status(500).json({ msg: 'Error getting ML model status', error: error.message });
  }
});

module.exports = router;