const mongoose = require('mongoose');

const UserSchema = new mongoose.Schema({
  name: {
    type: String,
    required: true
  },
  email: {
    type: String,
    required: true,
    unique: true
  },
  password: {
    type: String,
    required: true
  },
  // Profile completion fields
  profileCompleted: {
    type: Boolean,
    default: false
  },
  age: {
    type: Number,
    required: function() { return this.profileCompleted; }
  },
  gender: {
    type: String,
    enum: ['male', 'female', 'other'],
    required: function() { return this.profileCompleted; }
  },
  weight: {
    type: Number, // in kg
    required: function() { return this.profileCompleted; }
  },
  height: {
    type: Number, // in cm
    required: function() { return this.profileCompleted; }
  },
  fitnessGoals: {
    type: [String], // e.g., ['weight loss', 'muscle gain', 'endurance']
    required: function() { return this.profileCompleted; }
  },
  activityLevel: {
    type: String,
    enum: ['sedentary', 'light', 'moderate', 'active', 'very_active'],
    required: function() { return this.profileCompleted; }
  },
  dietaryPreferences: {
    type: [String], // e.g., ['vegetarian', 'vegan', 'gluten-free']
    default: []
  },
  healthConditions: {
    type: [String], // e.g., ['diabetes', 'hypertension']
    default: []
  },
  // ML model input fields - Workout preferences
  experienceLevel: {
    type: String,
    enum: ['beginner', 'intermediate', 'advanced'],
    default: 'beginner'
  },
  equipmentAvailable: {
    type: [String],
    default: []
  },
  timeAvailable: {
    type: Number, // in minutes
    default: 30
  },
  targetMuscleGroup: {
    type: String,
    enum: ['full-body', 'chest', 'back', 'legs', 'arms', 'core', 'shoulders'],
    default: 'full-body'
  },
  injuryHistory: {
    type: [String],
    default: []
  },
  preferredExerciseType: {
    type: String,
    enum: ['cardio', 'strength', 'flexibility', 'balance'],
    default: 'cardio'
  },
  intensityLevel: {
    type: String,
    enum: ['low', 'moderate', 'high', 'extreme'],
    default: 'moderate'
  },
  frequencyPerWeek: {
    type: Number,
    default: 3
  },
  focusArea: {
    type: String,
    enum: ['strength', 'hypertrophy', 'endurance', 'fat-loss'],
    default: 'strength'
  },
  gymOrHome: {
    type: String,
    enum: ['home', 'gym', 'outdoor', 'any'],
    default: 'home'
  },
  // ML model input fields - Nutrition preferences
  allergies: {
    type: [String], // e.g., ['nuts', 'shellfish', 'soy']
    default: []
  },
  mealTime: {
    type: String,
    enum: ['quick', 'moderate', 'extended'],
    default: 'moderate'
  },
  budget: {
    type: Number, // per meal in USD
    default: 15
  },
  proteinTarget: {
    type: Number, // daily protein target in grams
    default: 25
  },
  carbTarget: {
    type: Number, // daily carb target in grams
    default: 45
  },
  fatTarget: {
    type: Number, // daily fat target in grams
    default: 15
  },
  preferredCuisine: {
    type: String,
    enum: ['italian', 'asian', 'mexican', 'american', 'mediterranean', 'indian'],
    default: 'italian'
  },
  cookingSkill: {
    type: String,
    enum: ['beginner', 'intermediate', 'advanced'],
    default: 'intermediate'
  },
  ingredients: {
    type: [String], // ingredients user likes
    default: []
  },
  avoidIngredients: {
    type: [String], // ingredients to avoid
    default: []
  },
  spiceLevel: {
    type: Number, // 1-5 scale
    default: 3
  },
  prepTime: {
    type: Number, // maximum prep time in minutes
    default: 30
  },
  date: {
    type: Date,
    default: Date.now
  }
});

module.exports = mongoose.model('User', UserSchema);