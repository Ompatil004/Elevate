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
  fitnessGoal: {
    type: String,
    enum: ['weight-loss', 'muscle-gain', 'maintenance', 'endurance', 'flexibility'],
    default: 'maintenance'
  },
  height: {
    type: Number // in cm
  },
  weight: {
    type: Number // in kg
  },
  age: {
    type: Number
  },
  activityLevel: {
    type: String,
    enum: ['sedentary', 'light', 'moderate', 'active', 'very-active'],
    default: 'moderate'
  },
  dietPreference: {
    type: String,
    enum: ['balanced', 'low-carb', 'high-protein', 'vegetarian', 'vegan', 'keto'],
    default: 'balanced'
  },
  profileSetupComplete: {
    type: Boolean,
    default: false
  },
  date: {
    type: Date,
    default: Date.now
  }
});

module.exports = mongoose.model('User', UserSchema);