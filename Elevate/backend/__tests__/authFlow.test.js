const request = require('supertest');
const mongoose = require('mongoose');
const app = require('../app'); // Main Express app
const User = require('../models/User');
const jwt = require('jsonwebtoken');

// Mock data
const mockUserData = {
  name: 'Test User',
  email: 'authflowtest@example.com',
  password: 'password123'
};

// JWT secret from environment
const JWT_SECRET = process.env.JWT_SECRET || 'default_jwt_secret';

describe('Authentication Flow', () => {
  let authToken;
  let userId;

  beforeAll(async () => {
    // Clean up any existing test data
    await User.deleteMany({ email: mockUserData.email });
  });

  afterAll(async () => {
    if (userId) {
      await User.deleteMany({ _id: userId });
    }
    await mongoose.connection.close();
  });

  test('Complete authentication flow: register → login → get profile → update profile', async () => {
    // Step 1: Register a new user
    let res = await request(app)
      .post('/api/users/register')
      .send(mockUserData)
      .expect(200);

    expect(res.body).toHaveProperty('token');
    expect(res.body.user).toHaveProperty('id');
    expect(res.body.user.email).toBe(mockUserData.email);
    
    authToken = res.body.token;
    userId = res.body.user.id;

    // Verify the token is valid
    const decoded = jwt.verify(authToken, JWT_SECRET);
    expect(decoded.user.id).toBe(userId);

    // Step 2: Login with the same credentials (should work)
    res = await request(app)
      .post('/api/users/login')
      .send({
        email: mockUserData.email,
        password: mockUserData.password
      })
      .expect(200);

    expect(res.body).toHaveProperty('token');
    expect(res.body.user.email).toBe(mockUserData.email);
    
    // Token should be different from registration
    expect(res.body.token).not.toBe(authToken);

    // Step 3: Get user profile with valid token
    res = await request(app)
      .get('/api/users/profile')
      .set('x-auth-token', res.body.token) // Use the login token
      .expect(200);

    expect(res.body).toHaveProperty('_id', userId);
    expect(res.body.email).toBe(mockUserData.email);

    // Step 4: Update user profile
    const updatedProfile = {
      name: 'Updated Test User',
      height: 175,
      weight: 70,
      age: 25,
      activityLevel: 'moderate',
      dietPreference: 'balanced',
      profileSetupComplete: true
    };

    res = await request(app)
      .put('/api/users/profile')
      .set('x-auth-token', res.body.token) // Use the token from login
      .send(updatedProfile)
      .expect(200);

    expect(res.body.name).toBe(updatedProfile.name);
    expect(res.body.height).toBe(updatedProfile.height);
    expect(res.body.weight).toBe(updatedProfile.weight);
    expect(res.body.age).toBe(updatedProfile.age);
    expect(res.body.activityLevel).toBe(updatedProfile.activityLevel);
    expect(res.body.dietPreference).toBe(updatedProfile.dietPreference);
    expect(res.body.profileSetupComplete).toBe(updatedProfile.profileSetupComplete);
  });

  test('Should not allow access with invalid token', async () => {
    // Try to access profile with invalid token
    const res = await request(app)
      .get('/api/users/profile')
      .set('x-auth-token', 'invalid-token')
      .expect(401);

    expect(res.body.msg).toBe('Token is not valid');
  });

  test('Should not allow access without token', async () => {
    // Try to access profile without token
    const res = await request(app)
      .get('/api/users/profile')
      .expect(401);

    expect(res.body.msg).toBe('No token, authorization denied');
  });

  test('Should not allow login with wrong password', async () => {
    const res = await request(app)
      .post('/api/users/login')
      .send({
        email: mockUserData.email,
        password: 'wrongpassword'
      })
      .expect(400);

    expect(res.body.msg).toBe('Invalid Credentials');
  });

  test('Should not allow login with non-existent user', async () => {
    const res = await request(app)
      .post('/api/users/login')
      .send({
        email: 'nonexistent@example.com',
        password: 'password123'
      })
      .expect(400);

    expect(res.body.msg).toBe('Invalid Credentials');
  });
});