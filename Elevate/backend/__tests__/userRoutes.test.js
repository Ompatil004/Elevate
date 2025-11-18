const request = require('supertest');
const mongoose = require('mongoose');
const app = require('../app'); // Main Express app
const User = require('../models/User');
const jwt = require('jsonwebtoken');

// Mock data
const mockUserData = {
  name: 'Test User',
  email: 'test@example.com',
  password: 'password123'
};

const mockUpdatedProfile = {
  name: 'Updated Test User',
  height: 180,
  weight: 75,
  age: 30,
  activityLevel: 'active',
  dietPreference: 'balanced',
  profileSetupComplete: true
};

// JWT secret from environment or default
const JWT_SECRET = process.env.JWT_SECRET || 'default_jwt_secret';

describe('User API Endpoints', () => {
  let authToken;
  let userId;

  beforeAll(async () => {
    // Clean up any existing test data
    await User.deleteMany({ email: mockUserData.email });
  });

  afterAll(async () => {
    await User.deleteMany({ email: mockUserData.email });
    await mongoose.connection.close();
  });

  describe('POST /api/users/register', () => {
    it('should register a new user', async () => {
      const res = await request(app)
        .post('/api/users/register')
        .send(mockUserData)
        .expect(200);

      expect(res.body).toHaveProperty('token');
      expect(res.body.user).toHaveProperty('id');
      expect(res.body.user.email).toBe(mockUserData.email);
      
      // Store the token and user ID for subsequent tests
      authToken = res.body.token;
      userId = res.body.user.id;
    });

    it('should not register a user with duplicate email', async () => {
      const res = await request(app)
        .post('/api/users/register')
        .send(mockUserData)
        .expect(400);

      expect(res.body.msg).toBe('User already exists');
    });
  });

  describe('POST /api/users/login', () => {
    it('should login an existing user', async () => {
      const res = await request(app)
        .post('/api/users/login')
        .send({
          email: mockUserData.email,
          password: mockUserData.password
        })
        .expect(200);

      expect(res.body).toHaveProperty('token');
      expect(res.body.user).toHaveProperty('id');
      expect(res.body.user.email).toBe(mockUserData.email);
    });

    it('should not login with incorrect password', async () => {
      const res = await request(app)
        .post('/api/users/login')
        .send({
          email: mockUserData.email,
          password: 'wrongpassword'
        })
        .expect(400);

      expect(res.body.msg).toBe('Invalid Credentials');
    });
  });

  describe('GET /api/users/profile', () => {
    it('should get user profile with valid token', async () => {
      const res = await request(app)
        .get('/api/users/profile')
        .set('x-auth-token', authToken)
        .expect(200);

      expect(res.body).toHaveProperty('_id', userId);
      expect(res.body.email).toBe(mockUserData.email);
    });

    it('should not get profile without token', async () => {
      const res = await request(app)
        .get('/api/users/profile')
        .expect(401);

      expect(res.body.msg).toBe('No token, authorization denied');
    });
  });

  describe('PUT /api/users/profile', () => {
    it('should update user profile with valid token', async () => {
      const res = await request(app)
        .put('/api/users/profile')
        .set('x-auth-token', authToken)
        .send(mockUpdatedProfile)
        .expect(200);

      expect(res.body.name).toBe(mockUpdatedProfile.name);
      expect(res.body.height).toBe(mockUpdatedProfile.height);
      expect(res.body.weight).toBe(mockUpdatedProfile.weight);
      expect(res.body.age).toBe(mockUpdatedProfile.age);
      expect(res.body.activityLevel).toBe(mockUpdatedProfile.activityLevel);
      expect(res.body.dietPreference).toBe(mockUpdatedProfile.dietPreference);
      expect(res.body.profileSetupComplete).toBe(mockUpdatedProfile.profileSetupComplete);
    });

    it('should not update profile without token', async () => {
      const res = await request(app)
        .put('/api/users/profile')
        .send(mockUpdatedProfile)
        .expect(401);

      expect(res.body.msg).toBe('No token, authorization denied');
    });

    it('should not update profile with invalid token', async () => {
      const res = await request(app)
        .put('/api/users/profile')
        .set('x-auth-token', 'invalid-token')
        .send(mockUpdatedProfile)
        .expect(401);

      expect(res.body.msg).toBe('Token is not valid');
    });
  });
});