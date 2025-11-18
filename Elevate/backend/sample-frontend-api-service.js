// Sample API service file for frontend
// This would typically be placed in the frontend/src/services/api.js file

import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_BASE_URL || 'http://localhost:5000/api';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add token to requests if available
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token');
  if (token) {
    config.headers['x-auth-token'] = token;
  }
  return config;
});

// Authentication
export const authAPI = {
  register: (userData) => api.post('/users/register', userData),
  login: (userData) => api.post('/users/login', userData),
  getProfile: () => api.get('/users/profile'),
};

// Exercises
export const exercisesAPI = {
  getAllExercises: () => api.get('/exercises'),
  getExerciseById: (id) => api.get(`/exercises/${id}`),
  createExercise: (exerciseData) => api.post('/exercises', exerciseData),
  updateExercise: (id, exerciseData) => api.put(`/exercises/${id}`, exerciseData),
  deleteExercise: (id) => api.delete(`/exercises/${id}`),
};

// ML Services
export const mlAPI = {
  recommendWorkout: (workoutData) => api.post('/ml/recommend-workout', workoutData),
  recommendMeal: (mealData) => api.post('/ml/recommend-meal', mealData),
  chat: (chatData) => api.post('/ml/chat', chatData),
  generateCreativeMealPlan: (mealData) => api.post('/ml/generate-meal-plan-creative', mealData),
  startExerciseTracking: (trackingData) => api.post('/ml/start-exercise-tracking', trackingData),
  getSupportedExercises: () => api.get('/ml/get-supported-exercises'),
  getMLHealth: () => api.get('/ml/health'),
};

export default api;