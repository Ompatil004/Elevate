const express = require('express');
const router = express.Router();
const User = require('../models/User');
const Exercise = require('../models/Exercise');

// Test endpoint for database connectivity
router.get('/db', async (req, res) => {
  try {
    // Test database connection by fetching a count
    const userCount = await User.countDocuments();
    const exerciseCount = await Exercise.countDocuments();
    
    res.json({
      status: 'Database connection successful',
      counts: {
        users: userCount,
        exercises: exerciseCount
      }
    });
  } catch (error) {
    res.status(500).json({ 
      status: 'Database connection failed', 
      error: error.message 
    });
  }
});

// Test endpoint for authentication middleware
router.get('/auth', (req, res) => {
  res.json({ 
    status: 'Authentication middleware working',
    message: 'If you see this, you passed the auth middleware',
    timestamp: new Date().toISOString()
  });
});

// Test endpoint for ML integration
router.get('/ml', async (req, res) => {
  res.json({
    status: 'ML integration test endpoint',
    message: 'This endpoint is ready to connect to ML services',
    timestamp: new Date().toISOString()
  });
});

// General test endpoint
router.get('/', (req, res) => {
  res.json({ 
    message: 'All test endpoints are working!',
    routes: [
      'GET /api/test/ - This endpoint',
      'GET /api/test/db - Database connectivity test',
      'GET /api/test/auth - Authentication middleware test',
      'GET /api/test/ml - ML integration test'
    ],
    timestamp: new Date().toISOString()
  });
});

module.exports = router;