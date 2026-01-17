// Initialize sample data in MongoDB
const mongoose = require('mongoose');
require('dotenv').config();

// Import models
const User = require('./models/User');
const Workout = require('./models/Workout');
const Meal = require('./models/Meal');
const Progress = require('./models/Progress');
const Achievement = require('./models/Achievement');

async function initializeSampleData() {
  try {
    // Connect to MongoDB
    await mongoose.connect(process.env.MONGODB_URI);
    console.log('✅ Connected to MongoDB Atlas');
    
    // Clear existing sample data (optional - comment out if you want to keep existing data)
    await User.deleteMany({ email: { $regex: /sample|test/i } });
    await Workout.deleteMany({ name: { $regex: /sample|test/i } });
    await Meal.deleteMany({ name: { $regex: /sample|test/i } });
    console.log('🧹 Cleared existing sample data');
    
    // Create a sample user
    const sampleUser = new User({
      username: 'johndoe_fitness',
      email: 'john.doe@example.com',
      password: 'securePassword123',
      firstName: 'John',
      lastName: 'Doe',
      age: 28,
      gender: 'Male',
      weight: 75,
      height: 180,
      fitnessGoal: 'Muscle Gain',
      experienceLevel: 'Intermediate',
      preferences: {
        dietaryRestrictions: ['None'],
        notificationSettings: {
          email: true,
          push: true,
          whatsapp: false
        }
      }
    });
    
    // Save the user (password will be hashed automatically)
    const savedUser = await sampleUser.save();
    console.log('✅ Created sample user:', savedUser.username);
    
    // Create a sample workout
    const sampleWorkout = new Workout({
      userId: savedUser._id,
      name: 'Upper Body Strength',
      description: 'A comprehensive upper body strength training routine',
      exercises: [
        {
          name: 'Push-ups',
          bodyPart: 'Chest',
          sets: 3,
          reps: 12,
          weight: 0,
          restTime: 60
        },
        {
          name: 'Bicep Curls',
          bodyPart: 'Arms',
          sets: 3,
          reps: 10,
          weight: 15,
          restTime: 60
        },
        {
          name: 'Shoulder Press',
          bodyPart: 'Shoulders',
          sets: 3,
          reps: 8,
          weight: 20,
          restTime: 90
        }
      ],
      duration: 45,
      difficulty: 'Intermediate',
      category: 'Strength'
    });
    
    const savedWorkout = await sampleWorkout.save();
    console.log('✅ Created sample workout:', savedWorkout.name);
    
    // Create a sample meal
    const sampleMeal = new Meal({
      userId: savedUser._id,
      name: 'Protein Rich Breakfast',
      description: 'High protein breakfast to fuel your day',
      mealType: 'Breakfast',
      ingredients: [
        {
          name: 'Oatmeal',
          quantity: '1 cup',
          calories: 150,
          protein: 5,
          carbs: 27,
          fat: 2.5
        },
        {
          name: 'Protein Powder',
          quantity: '1 scoop',
          calories: 120,
          protein: 25,
          carbs: 2,
          fat: 1
        },
        {
          name: 'Banana',
          quantity: '1 medium',
          calories: 105,
          protein: 1.3,
          carbs: 27,
          fat: 0.4
        }
      ],
      totalCalories: 375,
      protein: 31.3,
      carbs: 56,
      fat: 3.9,
      prepTime: 5,
      difficulty: 'Easy',
      dietaryRestrictions: ['Vegetarian'],
      recipe: 'Mix oatmeal with protein powder, add sliced banana on top.',
      nutritionGoals: ['Muscle Gain']
    });
    
    const savedMeal = await sampleMeal.save();
    console.log('✅ Created sample meal:', savedMeal.name);
    
    // Create a sample progress log
    const sampleProgress = new Progress({
      userId: savedUser._id,
      date: new Date(),
      weight: 75,
      bodyFatPercentage: 15,
      measurements: {
        chest: 100,
        waist: 85,
        arms: 35
      },
      workoutLog: {
        workoutId: savedWorkout._id,
        duration: 45,
        caloriesBurned: 320,
        exercisesCompleted: [
          {
            exerciseName: 'Push-ups',
            setsCompleted: 3,
            repsCompleted: 12,
            weightUsed: 0
          }
        ]
      },
      mealLog: {
        mealId: savedMeal._id,
        mealType: 'Breakfast',
        caloriesConsumed: 375,
        macroDistribution: {
          protein: 31.3,
          carbs: 56,
          fat: 3.9
        }
      },
      repCounts: {
        exerciseName: 'Push-ups',
        repsCompleted: 36,
        setsCompleted: 3
      },
      mood: 'Energetic',
      sleepHours: 7.5,
      waterIntake: 2.5,
      notes: 'Had a great workout session today!'
    });
    
    const savedProgress = await sampleProgress.save();
    console.log('✅ Created sample progress log');
    
    // Create a sample achievement
    const sampleAchievement = new Achievement({
      name: 'First Workout',
      description: 'Completed your first workout',
      icon: '💪',
      points: 10,
      category: 'Workout',
      criteria: 'Complete 1 workout',
      rarity: 'Common'
    });
    
    const savedAchievement = await sampleAchievement.save();
    console.log('✅ Created sample achievement:', savedAchievement.name);
    
    // Update user with the achievement
    savedUser.achievements.push(savedAchievement._id);
    await savedUser.save();
    
    console.log('\n🎉 Sample data initialization completed successfully!');
    console.log('📊 Created 1 user, 1 workout, 1 meal, 1 progress log, and 1 achievement');
    
    // Close the connection
    await mongoose.connection.close();
    console.log('\n🔒 Database connection closed');
    
  } catch (error) {
    console.error('❌ Error initializing sample data:', error.message);
    console.error(error.stack);
  }
}

initializeSampleData();