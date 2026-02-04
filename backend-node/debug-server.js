require('dotenv').config();
const express = require('express');
const mongoose = require('mongoose');
const cors = require('cors');

const app = express();

// Middleware
app.use(express.json()); // Allows us to parse JSON bodies
app.use(cors({ origin: '*' })); // Allows Frontend to talk to Backend

console.log('Loading routes...');

try {
  console.log('Loading auth route...');
  app.use('/api/auth', require('./routes/auth'));
  console.log('✓ Auth route loaded');
  
  console.log('Loading profile route...');
  app.use('/api/profile', require('./routes/profile'));
  console.log('✓ Profile route loaded');
  
  console.log('Loading users route...');
  const usersRoute = require('./routes/users');
  console.log('✓ Users route module loaded, mounting at /api/users');
  app.use('/api/users', usersRoute);
  console.log('✓ Users route mounted');
} catch (error) {
  console.error('❌ Error loading routes:', error);
}

// Health check endpoint
app.get('/', (req, res) => {
    res.json({ message: 'Debug server running!' });
});

const PORT = 5002;
app.listen(PORT, () => console.log(`🚀 Debug server running on port ${PORT}`));