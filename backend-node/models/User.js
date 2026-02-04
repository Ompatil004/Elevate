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
  age: Number,
  weight: Number,
  height: Number,
  gender: String, // ADD THIS
  goal: {
    type: String,
    enum: ['Weight Loss', 'Muscle Gain', 'Maintenance', 'Athletic Performance']
  },
  experience: {
    type: String,
    enum: ['Beginner', 'Intermediate', 'Advanced']
  },
  equipment: [String], // ADD THIS - array of equipment
  allergies: [String], // ADD THIS - array of allergies
  dietary_preference: {
    type: String,
    default: 'Non-Veg'
  },
  streak: {
    type: Number,
    default: 0
  },
  lastWorkoutDate: String,
  trends: [{
    date: String,
    workout_completed: Boolean,
    meal_completed: Boolean,
    macros: { p: Number, c: Number, f: Number, calories: Number, fiber: Number },
    water_intake: Number,
    sleep_duration: Number,
    streak_days: Number
  }],
  createdAt: {
    type: Date,
    default: Date.now
  }
});

module.exports = mongoose.model('User', UserSchema);