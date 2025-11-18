import axios from 'axios';

// Create an axios instance with base configuration
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:5000/api';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add request interceptor to include token in headers
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token');
    if (token) {
      config.headers['x-auth-token'] = token;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Add response interceptor to handle token expiration
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // Token might be expired or invalid, clear it
      localStorage.removeItem('token');
      // Optionally redirect to login page
      // window.location.href = '/auth';
    }
    return Promise.reject(error);
  }
);

// Authentication API calls
export const authAPI = {
  register: (userData) => api.post('/users/register', userData),
  login: (userData) => api.post('/users/login', userData),
  getProfile: () => api.get('/users/profile'),
  updateProfile: (userData) => api.put('/users/profile', userData),
  completeProfile: (profileData) => api.put('/users/complete-profile', profileData),
};

// Exercise API calls
export const exerciseAPI = {
  getAllExercises: () => api.get('/exercises'),
  getExerciseById: (id) => api.get(`/exercises/${id}`),
  createExercise: (exerciseData) => api.post('/exercises', exerciseData),
  updateExercise: (id, exerciseData) => api.put(`/exercises/${id}`, exerciseData),
  deleteExercise: (id) => api.delete(`/exercises/${id}`),
};

// ML Services API calls
export const mlAPI = {
  recommendWorkout: (workoutData) => api.post('/ml/recommend-workout', workoutData),
  recommendMeal: (mealData) => api.post('/ml/recommend-meal', mealData),
  chat: (chatData) => api.post('/ml/chat', chatData),
  generateCreativeMealPlan: (mealData) => api.post('/ml/generate-meal-plan-creative', mealData),
  startExerciseTracking: (trackingData) => api.post('/ml/start-exercise-tracking', trackingData),
  getSupportedExercises: () => api.get('/ml/get-supported-exercises'),
  getMLHealth: () => api.get('/ml/health'),
  getPersonalizedRecommendations: (requestData) => api.post('/ml/get-personalized-recommendations', requestData),
};

// Test API calls
export const testAPI = {
  getTest: () => api.get('/test'),
  getDBTest: () => api.get('/test/db'),
  getAuthTest: () => api.get('/test/auth'),
  getMLTest: () => api.get('/test/ml'),
};

export default api;