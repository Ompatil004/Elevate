const request = require('supertest');
const app = require('../app');
const User = require('../models/User');
const Exercise = require('../models/Exercise');
const jwt = require('jsonwebtoken');

// JWT secret from environment or default
const JWT_SECRET = process.env.JWT_SECRET || 'default_jwt_secret';

// Mock user data for authenticated requests
const mockUserData = {
  name: 'Test User',
  email: 'exercisetest@example.com',
  password: 'password123'
};

let authToken;

describe('Exercise API Endpoints', () => {
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
    await Exercise.deleteMany({ createdBy: { $exists: true } }); // Clean up exercises
    await mongoose.connection.close();
  });

  describe('GET /api/exercises', () => {
    it('should get all exercises', async () => {
      const res = await request(app)
        .get('/api/exercises')
        .expect(200);

      // Should return an array
      expect(Array.isArray(res.body)).toBe(true);
    });

    it('should get a specific exercise by ID', async () => {
      // First, create an exercise to retrieve
      const newExerciseData = {
        name: 'Push-ups',
        description: 'Upper body exercise',
        category: 'Strength',
        difficulty: 'intermediate',
        duration: 30,
        equipment: ['none'],
        steps: [
          { step: 1, description: 'Get in plank position' },
          { step: 2, description: 'Lower body to ground' },
          { step: 3, description: 'Push body back up' }
        ]
      };

      // Create exercise
      const createRes = await request(app)
        .post('/api/exercises')
        .set('x-auth-token', authToken)
        .send(newExerciseData)
        .expect(200);

      // Now retrieve it
      const res = await request(app)
        .get(`/api/exercises/${createRes.body._id}`)
        .expect(200);

      expect(res.body.name).toBe(newExerciseData.name);
      expect(res.body.description).toBe(newExerciseData.description);
    });
  });

  describe('POST /api/exercises', () => {
    it('should create a new exercise with valid token', async () => {
      const newExerciseData = {
        name: 'Squats',
        description: 'Lower body exercise',
        category: 'Strength',
        difficulty: 'beginner',
        duration: 25,
        equipment: ['body weight'],
        steps: [
          { step: 1, description: 'Stand with feet shoulder-width apart' },
          { step: 2, description: 'Lower hips back and down' },
          { step: 3, description: 'Return to standing position' }
        ]
      };

      const res = await request(app)
        .post('/api/exercises')
        .set('x-auth-token', authToken)
        .send(newExerciseData)
        .expect(200);

      expect(res.body.name).toBe(newExerciseData.name);
      expect(res.body.description).toBe(newExerciseData.description);
      expect(res.body.createdBy).toBe(authToken ? jwt.verify(authToken, JWT_SECRET).user.id : undefined);
    });

    it('should not create an exercise without valid token', async () => {
      const newExerciseData = {
        name: 'Lunges',
        description: 'Lower body exercise',
        category: 'Strength',
      };

      const res = await request(app)
        .post('/api/exercises')
        .send(newExerciseData)
        .expect(401);

      expect(res.body.msg).toBe('No token, authorization denied');
    });
  });

  describe('PUT /api/exercises/:id', () => {
    let exerciseId;

    beforeAll(async () => {
      // Create an exercise to update
      const newExerciseData = {
        name: 'Bicep Curls',
        description: 'Arm exercise',
        category: 'Strength',
        difficulty: 'beginner',
        duration: 20,
        equipment: ['dumbbell']
      };

      const res = await request(app)
        .post('/api/exercises')
        .set('x-auth-token', authToken)
        .send(newExerciseData)
        .expect(200);

      exerciseId = res.body._id;
    });

    it('should update an existing exercise', async () => {
      const updatedData = {
        name: 'Hammer Curls',
        description: 'Bicep exercise with neutral grip',
        category: 'Strength',
        difficulty: 'intermediate',
        duration: 25
      };

      const res = await request(app)
        .put(`/api/exercises/${exerciseId}`)
        .set('x-auth-token', authToken)
        .send(updatedData)
        .expect(200);

      expect(res.body.name).toBe(updatedData.name);
      expect(res.body.description).toBe(updatedData.description);
    });

    it('should not update an exercise without valid token', async () => {
      const updatedData = {
        name: 'Updated Bicep Curls',
        description: 'Updated description'
      };

      const res = await request(app)
        .put(`/api/exercises/${exerciseId}`)
        .send(updatedData)
        .expect(401);

      expect(res.body.msg).toBe('No token, authorization denied');
    });
  });

  describe('DELETE /api/exercises/:id', () => {
    let exerciseId;

    beforeAll(async () => {
      // Create an exercise to delete
      const newExerciseData = {
        name: 'Tricep Dips',
        description: 'Tricep exercise',
        category: 'Strength',
        difficulty: 'intermediate',
        duration: 15
      };

      const res = await request(app)
        .post('/api/exercises')
        .set('x-auth-token', authToken)
        .send(newExerciseData)
        .expect(200);

      exerciseId = res.body._id;
    });

    it('should delete an existing exercise', async () => {
      const res = await request(app)
        .delete(`/api/exercises/${exerciseId}`)
        .set('x-auth-token', authToken)
        .expect(200);

      expect(res.body.msg).toBe('Exercise removed');
    });

    it('should not delete an exercise without valid token', async () => {
      // Create another exercise to try to delete without token
      const newExerciseData = {
        name: 'Leg Press',
        description: 'Lower body exercise',
        category: 'Strength',
        difficulty: 'beginner',
        duration: 30
      };

      const createRes = await request(app)
        .post('/api/exercises')
        .set('x-auth-token', authToken)
        .send(newExerciseData)
        .expect(200);

      const res = await request(app)
        .delete(`/api/exercises/${createRes.body._id}`)
        .expect(401);

      expect(res.body.msg).toBe('No token, authorization denied');
    });
  });
});