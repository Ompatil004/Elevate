const mongoose = require('mongoose');
const User = require('../models/User');
const Exercise = require('../models/Exercise');

// Test data
const validUserData = {
  name: 'Test User',
  email: 'testmodel@example.com',
  password: 'password123',
  fitnessGoal: 'muscle-gain',
  height: 180,
  weight: 75,
  age: 30,
  activityLevel: 'active',
  dietPreference: 'high-protein'
};

const validExerciseData = {
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

describe('Database Models', () => {
  beforeAll(async () => {
    // Connect to a test database
    await mongoose.connect(process.env.MONGODB_URI || 'mongodb://localhost:27017/test', {
      useNewUrlParser: true,
      useUnifiedTopology: true,
    });
  });

  afterAll(async () => {
    // Clean up test data
    await User.deleteMany({ email: { $regex: /testmodel|authflow|exercisetest/i } });
    await Exercise.deleteMany({ name: { $regex: /Push-ups|Squats|Bicep Curls|Tricep Dips/i } });
    await mongoose.connection.close();
  });

  describe('User Model', () => {
    it('should create a valid user', async () => {
      const user = new User(validUserData);
      const savedUser = await user.save();

      expect(savedUser._id).toBeDefined();
      expect(savedUser.name).toBe(validUserData.name);
      expect(savedUser.email).toBe(validUserData.email);
      expect(savedUser.password).not.toBe(validUserData.password); // Should be hashed
      expect(savedUser.fitnessGoal).toBe(validUserData.fitnessGoal);
      expect(savedUser.height).toBe(validUserData.height);
      expect(savedUser.weight).toBe(validUserData.weight);
      expect(savedUser.age).toBe(validUserData.age);
      expect(savedUser.activityLevel).toBe(validUserData.activityLevel);
      expect(savedUser.dietPreference).toBe(validUserData.dietPreference);
      expect(savedUser.profileSetupComplete).toBe(false); // Default value
      expect(savedUser.date).toBeDefined();
    });

    it('should require name field', async () => {
      const user = new User({
        ...validUserData,
        name: undefined
      });

      let err;
      try {
        await user.save();
      } catch (error) {
        err = error;
      }

      expect(err).toBeDefined();
      expect(err.errors.name).toBeDefined();
      expect(err.errors.name.message).toBe('Path `name` is required.');
    });

    it('should require email field', async () => {
      const user = new User({
        ...validUserData,
        email: undefined
      });

      let err;
      try {
        await user.save();
      } catch (error) {
        err = error;
      }

      expect(err).toBeDefined();
      expect(err.errors.email).toBeDefined();
    });

    it('should enforce unique email constraint', async () => {
      // Create first user
      const firstUser = new User(validUserData);
      await firstUser.save();

      // Try to create second user with same email
      const secondUser = new User({
        ...validUserData,
        email: validUserData.email // Same email
      });

      let err;
      try {
        await secondUser.save();
      } catch (error) {
        err = error;
      }

      expect(err).toBeDefined();
      expect(err.code).toBe(11000); // MongoDB duplicate key error
    });

    it('should validate fitnessGoal enum', async () => {
      const user = new User({
        ...validUserData,
        fitnessGoal: 'invalid-goal'
      });

      let err;
      try {
        await user.save();
      } catch (error) {
        err = error;
      }

      expect(err).toBeDefined();
      expect(err.errors.fitnessGoal).toBeDefined();
    });

    it('should validate activityLevel enum', async () => {
      const user = new User({
        ...validUserData,
        activityLevel: 'invalid-level'
      });

      let err;
      try {
        await user.save();
      } catch (error) {
        err = error;
      }

      expect(err).toBeDefined();
      expect(err.errors.activityLevel).toBeDefined();
    });

    it('should validate dietPreference enum', async () => {
      const user = new User({
        ...validUserData,
        dietPreference: 'invalid-diet'
      });

      let err;
      try {
        await user.save();
      } catch (error) {
        err = error;
      }

      expect(err).toBeDefined();
      expect(err.errors.dietPreference).toBeDefined();
    });

    it('should validate difficulty enum for fitnessGoal', async () => {
      const user = new User({
        ...validUserData,
        fitnessGoal: 'invalid-goal'
      });

      let err;
      try {
        await user.save();
      } catch (error) {
        err = error;
      }

      expect(err).toBeDefined();
      expect(err.errors.fitnessGoal).toBeDefined();
    });

    it('should have default values', async () => {
      const user = new User({
        name: 'Default User',
        email: 'default@example.com',
        password: 'password123'
      });

      const savedUser = await user.save();

      expect(savedUser.fitnessGoal).toBe('maintenance'); // Default value
      expect(savedUser.activityLevel).toBe('moderate'); // Default value
      expect(savedUser.dietPreference).toBe('balanced'); // Default value
      expect(savedUser.profileSetupComplete).toBe(false); // Default value
    });
  });

  describe('Exercise Model', () => {
    it('should create a valid exercise', async () => {
      const exercise = new Exercise(validExerciseData);
      const savedExercise = await exercise.save();

      expect(savedExercise._id).toBeDefined();
      expect(savedExercise.name).toBe(validExerciseData.name);
      expect(savedExercise.description).toBe(validExerciseData.description);
      expect(savedExercise.category).toBe(validExerciseData.category);
      expect(savedExercise.difficulty).toBe(validExerciseData.difficulty);
      expect(savedExercise.duration).toBe(validExerciseData.duration);
      expect(savedExercise.equipment).toEqual(validExerciseData.equipment);
      expect(savedExercise.steps).toEqual(validExerciseData.steps);
      expect(savedExercise.createdAt).toBeDefined();
    });

    it('should require name field', async () => {
      const exercise = new Exercise({
        ...validExerciseData,
        name: undefined
      });

      let err;
      try {
        await exercise.save();
      } catch (error) {
        err = error;
      }

      expect(err).toBeDefined();
      expect(err.errors.name).toBeDefined();
      expect(err.errors.name.message).toBe('Path `name` is required.');
    });

    it('should require description field', async () => {
      const exercise = new Exercise({
        ...validExerciseData,
        description: undefined
      });

      let err;
      try {
        await exercise.save();
      } catch (error) {
        err = error;
      }

      expect(err).toBeDefined();
      expect(err.errors.description).toBeDefined();
      expect(err.errors.description.message).toBe('Path `description` is required.');
    });

    it('should require category field', async () => {
      const exercise = new Exercise({
        ...validExerciseData,
        category: undefined
      });

      let err;
      try {
        await exercise.save();
      } catch (error) {
        err = error;
      }

      expect(err).toBeDefined();
      expect(err.errors.category).toBeDefined();
      expect(err.errors.category.message).toBe('Path `category` is required.');
    });

    it('should validate difficulty enum', async () => {
      const exercise = new Exercise({
        ...validExerciseData,
        difficulty: 'invalid-difficulty'
      });

      let err;
      try {
        await exercise.save();
      } catch (error) {
        err = error;
      }

      expect(err).toBeDefined();
      expect(err.errors.difficulty).toBeDefined();
    });

    it('should have default values', async () => {
      const exercise = new Exercise({
        name: 'Test Exercise',
        description: 'A test exercise',
        category: 'Strength'
      });

      const savedExercise = await exercise.save();

      expect(savedExercise.difficulty).toBe('beginner'); // Default value
      expect(savedExercise.duration).toBe(30); // Default value
      expect(savedExercise.steps).toEqual([]); // Default value
      expect(savedExercise.equipment).toEqual([]); // Default value
    });
  });
});