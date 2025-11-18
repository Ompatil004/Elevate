const express = require('express');
const router = express.Router();
const Exercise = require('../models/Exercise');
const auth = require('../middleware/auth');

// @route   GET api/exercises
// @desc    Get all exercises
// @access  Public
router.get('/', async (req, res) => {
  try {
    const exercises = await Exercise.find();
    res.json(exercises);
  } catch (error) {
    console.error(error.message);
    res.status(500).send('Server error');
  }
});

// @route   GET api/exercises/:id
// @desc    Get exercise by ID
// @access  Public
router.get('/:id', async (req, res) => {
  try {
    const exercise = await Exercise.findById(req.params.id);
    if (!exercise) {
      return res.status(404).json({ msg: 'Exercise not found' });
    }
    res.json(exercise);
  } catch (error) {
    console.error(error.message);
    res.status(500).send('Server error');
  }
});

// @route   POST api/exercises
// @desc    Create a new exercise
// @access  Private
router.post('/', auth, async (req, res) => {
  try {
    const { name, description, category, difficulty } = req.body;

    const newExercise = new Exercise({
      name,
      description,
      category,
      difficulty,
      createdBy: req.user.id
    });

    const exercise = await newExercise.save();
    res.json(exercise);
  } catch (error) {
    console.error(error.message);
    res.status(500).send('Server error');
  }
});

// @route   PUT api/exercises/:id
// @desc    Update an exercise
// @access  Private
router.put('/:id', auth, async (req, res) => {
  try {
    const exercise = await Exercise.findById(req.params.id);
    if (!exercise) {
      return res.status(404).json({ msg: 'Exercise not found' });
    }

    // Check if user owns the exercise
    if (exercise.createdBy.toString() !== req.user.id) {
      return res.status(401).json({ msg: 'User not authorized' });
    }

    const updatedExercise = await Exercise.findByIdAndUpdate(
      req.params.id,
      { $set: req.body },
      { new: true }
    );

    res.json(updatedExercise);
  } catch (error) {
    console.error(error.message);
    res.status(500).send('Server error');
  }
});

// @route   DELETE api/exercises/:id
// @desc    Delete an exercise
// @access  Private
router.delete('/:id', auth, async (req, res) => {
  try {
    const exercise = await Exercise.findById(req.params.id);
    if (!exercise) {
      return res.status(404).json({ msg: 'Exercise not found' });
    }

    // Check if user owns the exercise
    if (exercise.createdBy.toString() !== req.user.id) {
      return res.status(401).json({ msg: 'User not authorized' });
    }

    await Exercise.findByIdAndDelete(req.params.id);
    res.json({ msg: 'Exercise removed' });
  } catch (error) {
    console.error(error.message);
    res.status(500).send('Server error');
  }
});

module.exports = router;