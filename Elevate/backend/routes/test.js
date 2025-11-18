const express = require('express');
const router = express.Router();

// @route    GET api/test
// @desc     Test route
// @access   Public
router.get('/', (req, res) => {
  res.json({ msg: 'Test route is working!' });
});

// @route    GET api/test/database
// @desc     Test database connection
// @access   Public
router.get('/database', async (req, res) => {
  try {
    // This would connect to your database to test the connection
    res.json({ 
      msg: 'Database connection test would go here',
      timestamp: new Date().toISOString(),
      status: 'connected' // This is a placeholder - you'd implement actual DB logic
    });
  } catch (err) {
    console.error(err.message);
    res.status(500).send('Database connection test failed');
  }
});

// @route    GET api/test/environment
// @desc     Test environment variables
// @access   Public
router.get('/environment', (req, res) => {
  res.json({
    environment: process.env.NODE_ENV || 'development',
    port: process.env.PORT || 5000,
    db_host: process.env.DB_HOST,
    ml_backend_url: process.env.ML_BACKEND_URL,
    timestamp: new Date().toISOString()
  });
});

// @route    POST api/test/echo
// @desc     Echo back the request body
// @access   Public
router.post('/echo', (req, res) => {
  res.json({
    message: 'Echo endpoint received your data',
    received: req.body,
    timestamp: new Date().toISOString()
  });
});

module.exports = router;