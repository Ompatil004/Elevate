// app.js - Express app without listening
const express = require('express');
const mongoose = require('mongoose');
const cors = require('cors');
const dotenv = require('dotenv');
const axios = require('axios');

dotenv.config();

const app = express();
const PORT = process.env.PORT || 5000;

// Middleware
const corsOptions = {
  origin: process.env.NODE_ENV === 'production'
    ? [process.env.FRONTEND_URL]
    : [
        'http://localhost:3000',  // Frontend development server
        'http://localhost:5173',  // Vite development server
        'http://localhost:8080',  // Alternative development server
        process.env.FRONTEND_URL,  // Production frontend URL from environment
      ].filter(Boolean),  // Remove any undefined values from the array
  credentials: true,
  optionsSuccessStatus: 200,
  allowedHeaders: [
    'Origin',
    'X-Requested-With', 
    'Content-Type',
    'Accept',
    'x-auth-token',  // Added for JWT authentication
    'Authorization'
  ]
};

app.use(cors(corsOptions));
app.use(express.json({ limit: '10mb' }));
app.use(express.urlencoded({ extended: true, limit: '10mb' }));

// Security headers
app.use((req, res, next) => {
  res.header('X-Content-Type-Options', 'nosniff');
  res.header('X-Frame-Options', 'DENY');
  res.header('X-XSS-Protection', '1; mode=block');
  if (process.env.NODE_ENV === 'production') {
    res.header('Strict-Transport-Security', 'max-age=63072000; includeSubDomains; preload');
  }
  next();
});

// MongoDB connection
const connectDB = require('./config/db');

connectDB();

// Import and use routes
const userRoutes = require('./routes/users');
const exerciseRoutes = require('./routes/exercises');
const mlRoutes = require('./routes/ml');
const testRoutes = require('./routes/test');

app.use('/api/users', userRoutes);
app.use('/api/exercises', exerciseRoutes);
app.use('/api/ml', mlRoutes);
app.use('/api/test', testRoutes);

// Health check endpoint
app.get('/', (req, res) => {
  res.json({ message: 'Elevate Backend API is running!' });
});

// API Documentation endpoint
app.get('/api/docs', (req, res) => {
  res.json({
    message: 'Elevate Backend API Documentation',
    endpoints: {
      auth: {
        register: 'POST /api/users/register',
        login: 'POST /api/users/login',
        profile: 'GET /api/users/profile (requires token)'
      },
      exercises: {
        getAll: 'GET /api/exercises',
        getById: 'GET /api/exercises/:id',
        create: 'POST /api/exercises (requires token)',
        update: 'PUT /api/exercises/:id (requires token)',
        delete: 'DELETE /api/exercises/:id (requires token)'
      },
      ml: {
        recommendWorkout: 'POST /api/ml/recommend-workout (requires token)',
        recommendMeal: 'POST /api/ml/recommend-meal (requires token)',
        chat: 'POST /api/ml/chat (requires token)',
        generateCreativeMealPlan: 'POST /api/ml/generate-meal-plan-creative (requires token)',
        startExerciseTracking: 'POST /api/ml/start-exercise-tracking (requires token)',
        getSupportedExercises: 'GET /api/ml/get-supported-exercises (requires token)',
        health: 'GET /api/ml/health'
      }
    },
    documentation: 'Visit /api/docs for this endpoint, /api/test for test endpoints'
  });
});

// Test endpoints for development
app.get('/api/test', (req, res) => {
  res.json({
    message: 'Test endpoint is working!',
    timestamp: new Date().toISOString(),
    environment: process.env.NODE_ENV || 'development'
  });
});

// ML backend proxy endpoint to connect with Backend-ml
app.get('/api/ml-health', async (req, res) => {
  try {
    const response = await axios.get(`${process.env.ML_BACKEND_URL || 'http://localhost:8000'}/health`);
    res.json({ status: 'ML backend is running', details: response.data });
  } catch (error) {
    res.status(500).json({ status: 'ML backend is not accessible', error: error.message });
  }
});

// Export the app instance for testing
module.exports = app;