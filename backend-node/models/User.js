/**
 * BUG-N7 / ARCH-3: User.js
 *
 * Refactored from a flat schema to use named sub-schemas per domain:
 *   - SecuritySchema  — auth, passwords, suspension, admin access
 *   - FitnessProfileSchema — physical stats, goals, equipment
 *   - ActivityMetricsSchema — streaks, patterns, rest preferences
 *
 * Single-collection approach retained (no data migration needed).
 * Fields are identical — only organizational structure changed.
 */

'use strict';

const mongoose = require('mongoose');
const { Schema } = mongoose;

// ─────────────────────────────────────────────────────────────────────────────
// Sub-schema: Security & Access Control
// Owns all authentication, password management, and account-status data.
// ─────────────────────────────────────────────────────────────────────────────
const SecuritySchema = new Schema({
  // Account Status
  isSuspended:              { type: Boolean, default: false },
  suspendedAt:              Date,
  suspensionReason:         String,
  role:                     { type: String, enum: ['user', 'owner'], default: 'user' },

  // Password management
  passwordResetAt:          Date,
  mustChangePassword:       { type: Boolean, default: false },
  passwordResetTokenHash:   String,
  passwordResetTokenExpiresAt: Date,

  // Admin login tracking
  adminLastLoginAt:         Date,
  adminLoginAttempts:       { type: Number, default: 0 },
  adminLockedUntil:         Date,
  adminProfile: {
    phone:                  String,
    notificationsEnabled:   { type: Boolean, default: true },
  },
}, { _id: false });

// ─────────────────────────────────────────────────────────────────────────────
// Sub-schema: Fitness Profile
// Physical characteristics and training preferences.
// ─────────────────────────────────────────────────────────────────────────────
const FitnessProfileSchema = new Schema({
  age:     Number,
  weight:  Number,
  height:  Number,
  gender:  String,
  goal: {
    type: String,
    // Bug #6c: Added 'Maintenance' (full word) + 'Maintain' (short form used in meal engine).
    enum: ['Weight Loss', 'Fat Loss', 'Muscle Gain', 'Maintenance', 'Maintain', 'Strength', 'Endurance', 'Athletic Performance'],
  },
  experience: { type: String, enum: ['Beginner', 'Intermediate', 'Advanced'] },
  equipment:           [String],
  allergies:           [String],
  body_issues:         [String],
  days_per_week:       { type: Number, default: 4, min: 1, max: 7 },
  dietary_preference:  { type: String, default: 'Non-Veg' },
}, { _id: false });

// ─────────────────────────────────────────────────────────────────────────────
// Sub-schema: Daily Trend Entry (element type for the trends array)
// ─────────────────────────────────────────────────────────────────────────────
const TrendEntrySchema = new Schema({
  date:              String,
  workout_completed: Boolean,
  workout_partial:   Boolean,
  workout_attempted: Boolean, // NEW: Tracks if user attempted workout (even if skipped)
  meal_completed:    Boolean,
  // Macro nutrients logged for the day
  protein:   Number,
  carbs:     Number,
  fat:       Number,
  calories:  Number,
  fiber:     Number,
  // Hydration & recovery
  water_intake:    Number,
  sleep_duration:  Number,
  water_glasses:   Number, // Frontend alias
  sleep_hours:     Number, // Frontend alias
  streak_days:     Number,
  // Skipped exercises tracking
  skipped_exercises: [String],
}, { _id: false });

// ─────────────────────────────────────────────────────────────────────────────
// Root User Schema
// Composes sub-schemas by spreading them inline so the MongoDB document
// shape is unchanged — no migration required.
// ─────────────────────────────────────────────────────────────────────────────
const UserSchema = new Schema({
  // ── Identity ───────────────────────────────────────────────────────────────
  name:  { type: String, required: true },
  email: { type: String, required: true, unique: true },
  password: { type: String, required: true },
  avatar: String, // Google OAuth avatar or uploaded photo

  // ── Domain sub-schemas ─────────────────────────────────────────────────────
  // Security / access-control fields (inlined for single-collection simplicity)
  ...SecuritySchema.obj,

  // Fitness profile fields
  ...FitnessProfileSchema.obj,

  // ── Activity & History ─────────────────────────────────────────────────────
  streak:          { type: Number, default: 0 },
  lastWorkoutDate: String,
  trends:          [TrendEntrySchema],
  workouts:        [{ type: Schema.Types.Mixed }],
  meals:           [{ type: Schema.Types.Mixed }],

  // ── Workout Schedule Preferences ───────────────────────────────────────────
  workoutPatterns: {
    type: String,
    enum: ['Full Body', 'PPL', 'Upper/Lower', 'Bro Split', 'Custom'],
    default: null,
  },
  restDayPreferences: { type: [Number], default: [] },

  // ── Timestamps ─────────────────────────────────────────────────────────────
  updatedAt: Date,
  createdAt: { type: Date, default: Date.now },
  // Issue #1: track exact registration moment for rolling-week logic
  registrationDate: { type: Date, default: Date.now },
  // 0 = Monday … 6 = Sunday
  firstWorkoutDay: { type: Number, min: 0, max: 6, default: null },
});

// ── Indexes ──────────────────────────────────────────────────────────────────
// Enforce single owner account at database level.
UserSchema.index(
  { role: 1 },
  { unique: true, partialFilterExpression: { role: 'owner' } }
);

module.exports = mongoose.model('User', UserSchema);