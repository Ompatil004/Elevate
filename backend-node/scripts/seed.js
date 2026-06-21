#!/usr/bin/env node
/**
 * BUG-C10: Seed script for Node.js / MongoDB
 *
 * Creates a predictable set of test data for local development:
 *   - 1 admin (owner) user
 *   - 2 regular users (with full profiles)
 *   - Sample exercise records
 *
 * Usage:
 *   node scripts/seed.js
 *
 * Environment: MONGO_URI (or MONGODB_URI) must point to a non-production database.
 * The script refuses to run if MONGO_URI contains the string "prod".
 */

require('dotenv').config({ path: require('path').join(__dirname, '..', '.env') });
const mongoose = require('mongoose');
const bcrypt = require('bcryptjs');
const crypto = require('crypto');

const MONGO_URI = process.env.MONGO_URI || process.env.MONGODB_URI;

if (!MONGO_URI) {
  console.error('Error: MONGO_URI is not set.');
  process.exit(1);
}

if (/prod/i.test(MONGO_URI)) {
  console.error('❌ Refusing to seed: MONGO_URI appears to point at a production database.');
  process.exit(1);
}

// ---------------------------------------------------------------------------
// Inline minimal schema definitions to avoid importing the full User model
// (which has many hooks that are irrelevant for seeding).
// ---------------------------------------------------------------------------
const userSchema = new mongoose.Schema({}, { strict: false });
const UserModel = mongoose.model('User', userSchema, 'users');

const exerciseSchema = new mongoose.Schema({}, { strict: false });
const ExerciseModel = mongoose.model('Exercise', exerciseSchema, 'exercises');

async function hashPassword(plain) {
  const salt = await bcrypt.genSalt(10);
  return bcrypt.hash(plain, salt);
}

async function main() {
  await mongoose.connect(MONGO_URI, { serverSelectionTimeoutMS: 10000 });
  console.log('Connected:', MONGO_URI.replace(/\/\/[^@]+@/, '//***@'));

  // -----------------------------------------------------------------------
  // Clean existing seed data (identified by the __seed flag)
  // -----------------------------------------------------------------------
  const deletedUsers = await UserModel.deleteMany({ __seed: true });
  const deletedExercises = await ExerciseModel.deleteMany({ __seed: true });
  console.log(`Cleaned up ${deletedUsers.deletedCount} seed users, ${deletedExercises.deletedCount} seed exercises.`);

  // -----------------------------------------------------------------------
  // Create users
  // -----------------------------------------------------------------------
  const now = new Date();

  const ownerPassword = process.env.SEED_OWNER_PASSWORD || crypto.randomBytes(8).toString('hex');
  const userAPassword = process.env.SEED_USER_A_PASSWORD || crypto.randomBytes(8).toString('hex');
  const userBPassword = process.env.SEED_USER_B_PASSWORD || crypto.randomBytes(8).toString('hex');

  const seedUsers = [
    {
      __seed: true,
      name: 'Seed Owner',
      email: process.env.SEED_OWNER_EMAIL || 'owner@seed.local',
      password: await hashPassword(ownerPassword),
      role: 'owner',
      age: 30,
      gender: 'male',
      weight: 80,
      height: 178,
      goal: 'muscle_gain',
      experience: 'intermediate',
      dietary_preference: 'vegetarian',
      equipment: ['barbell', 'dumbbell'],
      days_per_week: 4,
      streak: 0,
      createdAt: now,
      updatedAt: now
    },
    {
      __seed: true,
      name: 'Seed User A',
      email: process.env.SEED_USER_A_EMAIL || 'user_a@seed.local',
      password: await hashPassword(userAPassword),
      role: 'user',
      age: 25,
      gender: 'female',
      weight: 65,
      height: 165,
      goal: 'weight_loss',
      experience: 'beginner',
      dietary_preference: 'vegan',
      equipment: ['bodyweight'],
      days_per_week: 3,
      streak: 5,
      createdAt: now,
      updatedAt: now
    },
    {
      __seed: true,
      name: 'Seed User B',
      email: process.env.SEED_USER_B_EMAIL || 'user_b@seed.local',
      password: await hashPassword(userBPassword),
      role: 'user',
      age: 35,
      gender: 'male',
      weight: 90,
      height: 182,
      goal: 'strength',
      experience: 'advanced',
      dietary_preference: 'omnivore',
      equipment: ['barbell', 'dumbbell', 'cable_machine'],
      days_per_week: 5,
      streak: 12,
      createdAt: now,
      updatedAt: now
    }
  ];

  const insertedUsers = await UserModel.insertMany(seedUsers, { ordered: true });
  console.log(`✅ Created ${insertedUsers.length} seed users:`);

  // Map to safely print passwords only during seed script execution
  const userPasswords = {
    [seedUsers[0].email]: ownerPassword,
    [seedUsers[1].email]: userAPassword,
    [seedUsers[2].email]: userBPassword
  };

  insertedUsers.forEach((u) =>
    console.log(`   ${u.role.padEnd(6)} | ${u.email.padEnd(25)} | password: ${userPasswords[u.email]}`)
  );
  console.log('ℹ️ Seed user passwords are dynamically generated unless provided in environment variables.');

  // -----------------------------------------------------------------------
  // Create sample exercises
  // -----------------------------------------------------------------------
  const seedExercises = [
    { __seed: true, name: 'Barbell Back Squat', muscleGroup: 'legs', equipment: 'barbell', difficulty: 'intermediate' },
    { __seed: true, name: 'Push-Up', muscleGroup: 'chest', equipment: 'bodyweight', difficulty: 'beginner' },
    { __seed: true, name: 'Pull-Up', muscleGroup: 'back', equipment: 'bodyweight', difficulty: 'intermediate' },
    { __seed: true, name: 'Dumbbell Shoulder Press', muscleGroup: 'shoulders', equipment: 'dumbbell', difficulty: 'beginner' },
    { __seed: true, name: 'Deadlift', muscleGroup: 'back', equipment: 'barbell', difficulty: 'advanced' }
  ];

  const insertedExercises = await ExerciseModel.insertMany(seedExercises, { ordered: true });
  console.log(`✅ Created ${insertedExercises.length} seed exercises.`);

  console.log('\n🌱 Seed complete. All seed documents are tagged with __seed:true for easy cleanup.');
  await mongoose.disconnect();
}

main().catch((err) => {
  console.error('Seed failed:', err);
  process.exit(1);
});
