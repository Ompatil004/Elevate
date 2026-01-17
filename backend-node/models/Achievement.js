const mongoose = require('mongoose');

const achievementSchema = new mongoose.Schema({
  name: {
    type: String,
    required: true,
    trim: true
  },
  description: {
    type: String,
    required: true,
    trim: true
  },
  icon: {
    type: String, // emoji or icon reference
    required: true
  },
  points: {
    type: Number,
    default: 10
  },
  category: {
    type: String,
    enum: ['Workout', 'Nutrition', 'Streak', 'Milestone', 'Social'],
    required: true
  },
  criteria: {
    type: String,
    required: true
  },
  rarity: {
    type: String,
    enum: ['Common', 'Uncommon', 'Rare', 'Epic', 'Legendary'],
    default: 'Common'
  },
  unlockedAt: {
    type: Date,
    default: Date.now
  }
}, {
  timestamps: true
});

module.exports = mongoose.model('Achievement', achievementSchema);