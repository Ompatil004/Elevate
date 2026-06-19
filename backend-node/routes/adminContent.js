const express = require('express');
const mongoose = require('mongoose');
const Exercise = require('../models/Exercise');
const SystemConfig = require('../models/SystemConfig');
const { requireOwner, logAdminAction } = require('../middleware/adminAuth');

const router = express.Router();

// Bug #1 fix: escape regex metacharacters to prevent ReDoS / NoSQL injection
const escapeRegex = (str) => String(str).replace(/[.*+?^${}()|[\]\\]/g, '\\$&');

// Bug #23 fix: validate MongoDB ObjectId format before DB calls
const isValidObjectId = (id) => mongoose.Types.ObjectId.isValid(id);

/**
 * GET /api/admin/content/exercises
 */
router.get('/exercises', requireOwner, async (req, res) => {
  try {
    const { category, difficulty, search } = req.query;

    const query = {};
    if (category) query.category = category;
    if (difficulty) query.difficulty = difficulty;
    // Bug #1 fixed: escape regex to prevent ReDoS / injection
    if (search) query.name = { $regex: escapeRegex(search), $options: 'i' };

    const exercises = await Exercise.find(query).sort({ createdAt: -1 });

    return res.json({ exercises, total: exercises.length });
  } catch (error) {
    return res.status(500).json({ message: 'Server error' });
  }
});

/**
 * POST /api/admin/content/exercises
 */
router.post('/exercises', requireOwner, logAdminAction('EXERCISE_ADD', 'exercise'), async (req, res) => {
  try {
    const {
      name,
      category,
      difficulty,
      description,
      equipment,
      muscleGroups,
      gifUrl
    } = req.body;

    if (!name || !category) {
      return res.status(400).json({ message: 'Name and category required' });
    }

    const exercise = new Exercise({
      name,
      category,
      difficulty: difficulty || 'intermediate',
      description,
      equipment: Array.isArray(equipment) ? equipment : [],
      muscleGroups: Array.isArray(muscleGroups) ? muscleGroups : [],
      gifUrl,
      createdBy: req.owner.id
    });

    await exercise.save();

    return res.status(201).json({
      message: 'Exercise added',
      exercise
    });
  } catch (error) {
    return res.status(500).json({ message: 'Server error' });
  }
});

/**
 * PUT /api/admin/content/exercises/:id
 */
router.put('/exercises/:id', requireOwner, logAdminAction('EXERCISE_EDIT', 'exercise'), async (req, res) => {
  try {
    // Bug #23 fixed: validate ObjectId before DB call
    if (!isValidObjectId(req.params.id)) {
      return res.status(400).json({ message: 'Invalid exercise ID format' });
    }
    const {
      name,
      category,
      difficulty,
      description,
      equipment,
      muscleGroups,
      gifUrl,
      active
    } = req.body;

    const exercise = await Exercise.findById(req.params.id);

    if (!exercise) {
      return res.status(404).json({ message: 'Exercise not found' });
    }

    if (name) exercise.name = name;
    if (category) exercise.category = category;
    if (difficulty) exercise.difficulty = difficulty;
    if (description !== undefined) exercise.description = description;
    if (equipment !== undefined) {
      exercise.equipment = Array.isArray(equipment) ? equipment : [];
    }
    if (muscleGroups !== undefined) {
      exercise.muscleGroups = Array.isArray(muscleGroups) ? muscleGroups : [];
    }
    if (gifUrl !== undefined) exercise.gifUrl = gifUrl;
    if (active !== undefined) exercise.active = active;

    exercise.updatedBy = req.owner.id;

    await exercise.save();

    return res.json({
      message: 'Exercise updated',
      exercise
    });
  } catch (error) {
    return res.status(500).json({ message: 'Server error' });
  }
});

/**
 * DELETE /api/admin/content/exercises/:id
 */
router.delete('/exercises/:id', requireOwner, logAdminAction('EXERCISE_DELETE', 'exercise'), async (req, res) => {
  try {
    // Bug #23 fixed: validate ObjectId before DB call
    if (!isValidObjectId(req.params.id)) {
      return res.status(400).json({ message: 'Invalid exercise ID format' });
    }
    const exercise = await Exercise.findByIdAndDelete(req.params.id);

    if (!exercise) {
      return res.status(404).json({ message: 'Exercise not found' });
    }

    return res.json({ message: 'Exercise deleted' });
  } catch (error) {
    return res.status(500).json({ message: 'Server error' });
  }
});

/**
 * POST /api/admin/content/workout-rules
 */
router.post('/workout-rules', requireOwner, logAdminAction('CONFIG_UPDATE', 'config'), async (req, res) => {
  try {
    const { rules } = req.body;

    let config = await SystemConfig.findOne({ key: 'workoutRules' });
    if (!config) {
      config = new SystemConfig({ key: 'workoutRules', value: {} });
    }

    config.value = {
      ...(config.value || {}),
      ...(rules || {}),
      updatedAt: new Date()
    };
    config.updatedBy = req.owner.id;
    config.updatedAt = new Date();

    await config.save();

    return res.json({
      message: 'Workout rules updated',
      rules: config.value
    });
  } catch (error) {
    return res.status(500).json({ message: 'Server error' });
  }
});

/**
 * GET /api/admin/content/workout-rules
 */
router.get('/workout-rules', requireOwner, async (req, res) => {
  try {
    const config = await SystemConfig.findOne({ key: 'workoutRules' });

    return res.json({
      rules: config?.value || {}
    });
  } catch (error) {
    return res.status(500).json({ message: 'Server error' });
  }
});

module.exports = router;
