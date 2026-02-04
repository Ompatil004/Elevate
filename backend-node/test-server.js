const express = require('express');
const mongoose = require('mongoose');
const cors = require('cors');

// Create a minimal test server
const app = express();

// Middleware
app.use(express.json());
app.use(cors({ origin: '*' }));

// Test route to see if the users route is working
app.get('/test-users-route', (req, res) => {
  try {
    const usersRoute = require('./routes/users');
    res.json({ message: 'Users route module loaded successfully', hasRoutes: !!usersRoute });
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

// Manually add the users route here for testing
app.use('/api/users-test', require('./routes/users'));

// Health check
app.get('/', (req, res) => {
    res.json({ message: 'Test server running!' });
});

const PORT = 5001;
app.listen(PORT, () => console.log(`🚀 Test server running on port ${PORT}`));