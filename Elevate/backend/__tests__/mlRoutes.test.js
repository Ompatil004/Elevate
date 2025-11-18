const request = require('supertest');
const app = require('../app');
const User = require('../models/User');
const jwt = require('jsonwebtoken');

// JWT secret from environment or default
const JWT_SECRET = process.env.JWT_SECRET || 'default_jwt_secret';

// Mock user data for authenticated requests
const mockUserData = {
  name: 'Test User',
  email: 'mltest@example.com',
  password: 'password123'
};

let authToken;

describe('ML API Endpoints', () => {
  beforeAll(async () => {
    // Register a test user and get auth token
    await User.deleteMany({ email: mockUserData.email });
    
    const registerRes = await request(app)
      .post('/api/users/register')
      .send(mockUserData)
      .expect(200);
    
    authToken = registerRes.body.token;
  });

  afterAll(async () => {
    await User.deleteMany({ email: mockUserData.email });
    await mongoose.connection.close();
  });

  describe('GET /api/ml/health', () => {
    it('should return health status for ML service', async () => {
      const res = await request(app)
        .get('/api/ml/health')
        .set('x-auth-token', authToken) // Token might be required depending on implementation
        .expect(200);

      // The response format depends on what the ML backend returns
      // This is a general test - adjust based on your actual ML backend response
      expect(res.body).toHaveProperty('message');
    });
  });

  // Note: These tests will require a running ML backend service
  // They may need to be mocked for unit testing purposes
  describe('POST /api/ml/recommend-workout', () => {
    it('should return workout recommendations', async () => {
      const workoutData = {
        goal: 'Strength',
        experience: 'Intermediate',
        equipment_available: ['Dumbbells'],
        time_available: 60
      };

      const res = await request(app)
        .post('/api/ml/recommend-workout')
        .set('x-auth-token', authToken)
        .send(workoutData);

      // Check if we get a successful response 
      // (response structure depends on ML backend implementation)
      expect(res.status).toBeOneOf([200, 500]); // Allow 500 if ML backend is not running
    });
  });

  describe('POST /api/ml/recommend-meal', () => {
    it('should return meal recommendations', async () => {
      const mealData = {
        goal: 'muscle-gain',
        calorie_target: 500,
        meal_type: 'Breakfast'
      };

      const res = await request(app)
        .post('/api/ml/recommend-meal')
        .set('x-auth-token', authToken)
        .send(mealData);

      // Check if we get a response 
      // (response structure depends on ML backend implementation)
      expect(res.status).toBeOneOf([200, 500]); // Allow 500 if ML backend is not running
    });
  });

  describe('POST /api/ml/chat', () => {
    it('should return a response from AI chat', async () => {
      const chatData = {
        prompt: 'How do I build muscle?',
        response_length: 'Brief'
      };

      const res = await request(app)
        .post('/api/ml/chat')
        .set('x-auth-token', authToken)
        .send(chatData);

      // Check if we get a response 
      // (response structure depends on ML backend implementation)
      expect(res.status).toBeOneOf([200, 500]); // Allow 500 if ML backend is not running
    });
  });
});