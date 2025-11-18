const request = require('supertest');
const app = require('../app');
const axios = require('axios');

// Mock user data for authenticated requests
const mockUserData = {
  name: 'Test User',
  email: 'mlintegrationtest@example.com',
  password: 'password123'
};

let authToken;

// Mock axios to simulate ML backend responses
jest.mock('axios');

describe('ML API Integration', () => {
  beforeAll(async () => {
    // Register a test user and get auth token
    await request(app)
      .post('/api/users/register')
      .send(mockUserData)
      .expect(200)
      .then(res => {
        authToken = res.body.token;
      });
  });

  beforeEach(() => {
    jest.clearAllMocks();
  });

  describe('ML Health Check', () => {
    test('should return health status when ML backend is accessible', async () => {
      // Mock successful response from ML backend
      axios.get.mockResolvedValue({
        data: { message: 'ML backend is running!' },
        status: 200
      });

      const res = await request(app)
        .get('/api/ml-health')
        .expect(200);

      expect(res.body.status).toBe('ML backend is running');
      expect(res.body.details).toEqual({ message: 'ML backend is running!' });
    });

    test('should return error status when ML backend is not accessible', async () => {
      // Mock failed response from ML backend
      axios.get.mockRejectedValue(new Error('ML backend not accessible'));

      const res = await request(app)
        .get('/api/ml-health')
        .expect(500);

      expect(res.body.status).toBe('ML backend is not accessible');
      expect(res.body.error).toBeDefined();
    });
  });

  describe('Workout Recommendations', () => {
    test('should proxy workout recommendation request to ML backend', async () => {
      const workoutData = {
        goal: 'Strength',
        experience: 'Intermediate',
        equipment_available: ['dumbbell', 'barbell'],
        time_available: 60
      };

      // Mock successful response from ML backend
      const mockMLResponse = {
        data: {
          title: 'Strength Training Workout',
          exercises: [
            { name: 'Bench Press', sets: 3, reps: 8 },
            { name: 'Squats', sets: 3, reps: 10 }
          ]
        }
      };

      axios.post.mockResolvedValue(mockMLResponse);

      const res = await request(app)
        .post('/api/ml/recommend-workout')
        .set('x-auth-token', authToken)
        .send(workoutData)
        .expect(200);

      expect(axios.post).toHaveBeenCalledWith(
        expect.stringContaining('/ml/recommend-workout'),
        workoutData,
        expect.any(Object) // config object
      );
      expect(res.body).toEqual(mockMLResponse.data);
    });

    test('should handle ML backend errors gracefully', async () => {
      const workoutData = {
        goal: 'Strength',
        experience: 'Beginner'
      };

      // Mock error response from ML backend
      axios.post.mockRejectedValue(new Error('ML service error'));

      const res = await request(app)
        .post('/api/ml/recommend-workout')
        .set('x-auth-token', authToken)
        .send(workoutData)
        .expect(500);

      expect(res.body.msg).toBe('Error getting prediction from ML model');
      expect(res.body.error).toBeDefined();
    });
  });

  describe('Meal Recommendations', () => {
    test('should proxy meal recommendation request to ML backend', async () => {
      const mealData = {
        goal: 'muscle-gain',
        calorie_target: 500,
        meal_type: 'Breakfast'
      };

      // Mock successful response from ML backend
      const mockMLResponse = {
        data: {
          title: 'Muscle Gain Breakfast',
          meals: [
            { name: 'Protein Oatmeal', calories: 450, protein: 25 }
          ]
        }
      };

      axios.post.mockResolvedValue(mockMLResponse);

      const res = await request(app)
        .post('/api/ml/recommend-meal')
        .set('x-auth-token', authToken)
        .send(mealData)
        .expect(200);

      expect(axios.post).toHaveBeenCalledWith(
        expect.stringContaining('/ml/recommend-meal'),
        mealData,
        expect.any(Object) // config object
      );
      expect(res.body).toEqual(mockMLResponse.data);
    });

    test('should handle ML backend errors for meal recommendations', async () => {
      const mealData = {
        goal: 'weight-loss',
        calorie_target: 300
      };

      // Mock error response from ML backend
      axios.post.mockRejectedValue(new Error('ML service error'));

      const res = await request(app)
        .post('/api/ml/recommend-meal')
        .set('x-auth-token', authToken)
        .send(mealData)
        .expect(500);

      expect(res.body.msg).toBe('Error getting prediction from ML model');
      expect(res.body.error).toBeDefined();
    });
  });

  describe('AI Chat', () => {
    test('should proxy chat request to ML backend', async () => {
      const chatData = {
        prompt: 'How do I build muscle?',
        response_length: 'Moderate'
      };

      // Mock successful response from ML backend
      const mockMLResponse = {
        data: {
          response: 'To build muscle, focus on protein intake and resistance training.'
        }
      };

      axios.post.mockResolvedValue(mockMLResponse);

      const res = await request(app)
        .post('/api/ml/chat')
        .set('x-auth-token', authToken)
        .send(chatData)
        .expect(200);

      expect(axios.post).toHaveBeenCalledWith(
        expect.stringContaining('/ml/chat'),
        chatData,
        expect.any(Object) // config object
      );
      expect(res.body).toEqual(mockMLResponse.data);
    });

    test('should handle AI chat errors gracefully', async () => {
      const chatData = {
        prompt: 'Tell me about fitness',
        response_length: 'Brief'
      };

      // Mock error response from ML backend
      axios.post.mockRejectedValue(new Error('AI service error'));

      const res = await request(app)
        .post('/api/ml/chat')
        .set('x-auth-token', authToken)
        .send(chatData)
        .expect(500);

      expect(res.body.msg).toBe('Error communicating with AI health assistant');
      expect(res.body.error).toBeDefined();
    });
  });

  describe('Creative Meal Plan', () => {
    test('should proxy creative meal plan request to ML backend', async () => {
      const mealPlanData = {
        goal: 'maintain',
        meals: [
          { name: 'Grilled Chicken', calories: 300, protein: 35 }
        ]
      };

      // Mock successful response from ML backend
      const mockMLResponse = {
        data: {
          response: 'Create a meal plan with grilled chicken...'
        }
      };

      axios.post.mockResolvedValue(mockMLResponse);

      const res = await request(app)
        .post('/api/ml/generate-meal-plan-creative')
        .set('x-auth-token', authToken)
        .send(mealPlanData)
        .expect(200);

      expect(axios.post).toHaveBeenCalledWith(
        expect.stringContaining('/ml/generate-meal-plan-creative'),
        mealPlanData,
        expect.any(Object) // config object
      );
      expect(res.body).toEqual(mockMLResponse.data);
    });
  });

  describe('Exercise Tracking', () => {
    test('should proxy exercise tracking request to ML backend', async () => {
      const trackingData = {
        exercise_name: 'Push-ups',
        camera_index: 0
      };

      // Mock successful response from ML backend
      const mockMLResponse = {
        data: {
          message: 'Tracking started for Push-ups',
          exercise: 'Push-ups'
        }
      };

      axios.post.mockResolvedValue(mockMLResponse);

      const res = await request(app)
        .post('/api/ml/start-exercise-tracking')
        .set('x-auth-token', authToken)
        .send(trackingData)
        .expect(200);

      expect(axios.post).toHaveBeenCalledWith(
        expect.stringContaining('/ml/start-exercise-tracking'),
        trackingData,
        expect.any(Object) // config object
      );
      expect(res.body).toEqual(mockMLResponse.data);
    });
  });

  describe('Supported Exercises', () => {
    test('should proxy supported exercises request to ML backend', async () => {
      // Mock successful response from ML backend
      const mockMLResponse = {
        data: {
          supported_exercises: ['Push-ups', 'Squats', 'Planks'],
          message: 'Supporting 3 exercises'
        }
      };

      axios.get.mockResolvedValue(mockMLResponse);

      const res = await request(app)
        .get('/api/ml/get-supported-exercises')
        .set('x-auth-token', authToken)
        .expect(200);

      expect(axios.get).toHaveBeenCalledWith(
        expect.stringContaining('/ml/get-supported-exercises'),
        expect.any(Object) // config object
      );
      expect(res.body).toEqual(mockMLResponse.data);
    });
  });
});