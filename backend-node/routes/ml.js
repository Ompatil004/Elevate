const express = require('express');
const axios = require('axios');
const auth = require('../middleware/auth');

const router = express.Router();

// Proxy to external ML service
const ML_SERVICE_URL = process.env.ML_SERVICE_URL || 'http://localhost:8000';
const POSE_SERVICE_URL = process.env.POSE_SERVICE_URL || 'http://localhost:8001'; // Our new pose detection service

// @route    POST api/ml/predict_meal
// @desc     Get meal prediction from ML service
// @access   Private
router.post('/predict_meal', auth, async (req, res) => {
  try {
    const { goal, calorie_target, dietary_restrictions } = req.body;

    const response = await axios.post(`${ML_SERVICE_URL}/ml/recommend-meal`, {
      goal,
      calorie_target,
      dietary_restrictions
    });

    res.json(response.data);
  } catch (error) {
    console.error('ML Service Error:', error.response?.data || error.message);
    res.status(500).json({ msg: 'Error getting meal prediction from ML service' });
  }
});

// @route    POST api/ml/suggest_workout
// @desc     Get workout suggestion from ML service
// @access   Private
router.post('/suggest_workout', auth, async (req, res) => {
  try {
    const { goal, experience } = req.body;

    const response = await axios.post(`${ML_SERVICE_URL}/ml/recommend-workout`, {
      goal,
      experience
    });

    res.json(response.data);
  } catch (error) {
    console.error('ML Service Error:', error.response?.data || error.message);
    res.status(500).json({ msg: 'Error getting workout suggestion from ML service' });
  }
});

// @route    POST api/ml/chat
// @desc     Chat with AI assistant
// @access   Private
router.post('/chat', auth, async (req, res) => {
  try {
    const { message, context } = req.body;

    // In a real implementation, this would call an actual AI chat service
    // For now, returning a mock response
    res.json({
      response: "This is a mock response from the AI chatbot. In a real implementation, this would connect to an AI service like GPT or LLaMA with RAG."
    });
  } catch (error) {
    console.error('Chat Service Error:', error.message);
    res.status(500).json({ msg: 'Error communicating with chat service' });
  }
});

// @route    POST api/ml/set-exercise
// @desc     Set the current exercise for pose detection
// @access   Private
router.post('/set-exercise', auth, async (req, res) => {
  try {
    const { exercise_name } = req.body;

    const response = await axios.post(`${POSE_SERVICE_URL}/set_exercise`, {
      exercise_name
    });

    res.json(response.data);
  } catch (error) {
    console.error('Pose Service Error:', error.response?.data || error.message);
    res.status(500).json({ msg: 'Error communicating with pose detection service' });
  }
});

// @route    GET api/ml/get-reps
// @desc     Get the current rep count from pose detection
// @access   Private
router.get('/get-reps', auth, async (req, res) => {
  try {
    const response = await axios.get(`${POSE_SERVICE_URL}/get_reps`);

    res.json(response.data);
  } catch (error) {
    console.error('Pose Service Error:', error.response?.data || error.message);
    res.status(500).json({ msg: 'Error communicating with pose detection service' });
  }
});

// @route    GET api/ml/video-feed
// @desc     Proxy the video feed from pose detection service
// @access   Private
router.get('/video-feed', auth, async (req, res) => {
  try {
    // This would require a more complex proxy setup to stream the video
    // For now, we'll redirect to the pose service directly
    res.redirect(`${POSE_SERVICE_URL}/video_feed`);
  } catch (error) {
    console.error('Pose Service Error:', error.response?.data || error.message);
    res.status(500).json({ msg: 'Error accessing video feed from pose detection service' });
  }
});

module.exports = router;