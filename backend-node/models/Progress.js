const mongoose = require('mongoose');

const progressSchema = new mongoose.Schema({
  userId: {
    type: mongoose.Schema.Types.ObjectId,
    ref: 'User',
    required: true
  },
  date: {
    type: Date,
    default: Date.now
  },
  weight: {
    type: Number,
    min: [30, 'Weight must be at least 30 kg'],
    max: [300, 'Weight cannot exceed 300 kg']
  },
  bodyFatPercentage: {
    type: Number,
    min: [0, 'Body fat percentage must be at least 0%'],
    max: [100, 'Body fat percentage cannot exceed 100%']
  },
  muscleMass: {
    type: Number
  },
  measurements: {
    chest: Number,
    waist: Number,
    hips: Number,
    arms: Number,
    thighs: Number
  },
  workoutLog: {
    workoutId: {
      type: mongoose.Schema.Types.ObjectId,
      ref: 'Workout'
    },
    duration: {
      type: Number, // in minutes
      required: true
    },
    caloriesBurned: {
      type: Number,
      required: true
    },
    exercisesCompleted: [{
      exerciseName: String,
      setsCompleted: Number,
      repsCompleted: Number,
      weightUsed: Number
    }]
  },
  mealLog: {
    mealId: {
      type: mongoose.Schema.Types.ObjectId,
      ref: 'Meal'
    },
    mealType: String, // Breakfast, Lunch, Dinner, Snack
    caloriesConsumed: {
      type: Number,
      required: true
    },
    macroDistribution: {
      protein: Number,
      carbs: Number,
      fat: Number
    }
  },
  repCounts: {
    exerciseName: String,
    repsCompleted: Number,
    setsCompleted: Number
  },
  mood: {
    type: String,
    enum: ['Happy', 'Neutral', 'Stressed', 'Tired', 'Energetic']
  },
  sleepHours: {
    type: Number,
    min: [0, 'Sleep hours cannot be negative'],
    max: [24, 'Sleep hours cannot exceed 24']
  },
  waterIntake: {
    type: Number, // in liters
    default: 0
  },
  notes: {
    type: String,
    trim: true
  }
}, {
  timestamps: true
});

module.exports = mongoose.model('Progress', progressSchema);