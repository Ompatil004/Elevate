const mongoose = require('mongoose');

const workoutSchema = new mongoose.Schema({
  userId: {
    type: mongoose.Schema.Types.ObjectId,
    ref: 'User',
    required: true
  },
  name: {
    type: String,
    required: true,
    trim: true
  },
  description: {
    type: String,
    trim: true
  },
  exercises: [{
    name: {
      type: String,
      required: true
    },
    bodyPart: {
      type: String,
      required: true
    },
    sets: {
      type: Number,
      default: 3
    },
    reps: {
      type: Number,
      default: 10
    },
    weight: {
      type: Number,
      default: 0
    },
    restTime: {
      type: Number, // in seconds
      default: 60
    }
  }],
  duration: {
    type: Number, // in minutes
    required: true
  },
  difficulty: {
    type: String,
    enum: ['Beginner', 'Intermediate', 'Advanced'],
    required: true
  },
  category: {
    type: String,
    enum: ['Strength', 'Cardio', 'Flexibility', 'HIIT', 'Yoga', 'Pilates'],
    default: 'Strength'
  },
  isPublic: {
    type: Boolean,
    default: false
  },
  likes: {
    type: Number,
    default: 0
  },
  createdBy: {
    type: mongoose.Schema.Types.ObjectId,
    ref: 'User'
  }
}, {
  timestamps: true
});

module.exports = mongoose.model('Workout', workoutSchema);