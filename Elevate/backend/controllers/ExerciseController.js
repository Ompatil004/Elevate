const Exercise = require('../models/Exercise');

// @desc    Get all exercises for the authenticated user
// @route   GET /api/exercises
// @access  Private
const getAllExercises = async (req, res) => {
  try {
    const exercises = await Exercise.find({ userId: req.user.id }).sort({ date: -1 });
    res.json(exercises);
  } catch (err) {
    console.error(err.message);
    res.status(500).send('Server error');
  }
};

// @desc    Get exercise by ID
// @route   GET /api/exercises/:id
// @access  Private
const getExerciseById = async (req, res) => {
  try {
    const exercise = await Exercise.findById(req.params.id);

    if (!exercise) {
      return res.status(404).json({ msg: 'Exercise not found' });
    }

    if (exercise.userId.toString() !== req.user.id) {
      return res.status(401).json({ msg: 'User not authorized' });
    }

    res.json(exercise);
  } catch (err) {
    console.error(err.message);
    if (err.kind === 'ObjectId') {
      return res.status(404).json({ msg: 'Exercise not found' });
    }
    res.status(500).send('Server error');
  }
};

// @desc    Add new exercise
// @route   POST /api/exercises
// @access  Private
const createExercise = async (req, res) => {
  try {
    const { name, description, category, muscleGroup, difficulty } = req.body;

    const newExercise = new Exercise({
      name,
      description,
      category,
      muscleGroup,
      difficulty,
      userId: req.user.id
    });

    const exercise = await newExercise.save();
    res.json(exercise);
  } catch (err) {
    console.error(err.message);
    res.status(500).send('Server error');
  }
};

// @desc    Update exercise
// @route   PUT /api/exercises/:id
// @access  Private
const updateExercise = async (req, res) => {
  try {
    let exercise = await Exercise.findById(req.params.id);

    if (!exercise) {
      return res.status(404).json({ msg: 'Exercise not found' });
    }

    // Check user
    if (exercise.userId.toString() !== req.user.id) {
      return res.status(401).json({ msg: 'User not authorized' });
    }

    exercise = await Exercise.findByIdAndUpdate(
      req.params.id,
      { $set: req.body },
      { new: true }
    );

    res.json(exercise);
  } catch (err) {
    console.error(err.message);
    if (err.kind === 'ObjectId') {
      return res.status(404).json({ msg: 'Exercise not found' });
    }
    res.status(500).send('Server error');
  }
};

// @desc    Delete exercise
// @route   DELETE /api/exercises/:id
// @access  Private
const deleteExercise = async (req, res) => {
  try {
    let exercise = await Exercise.findById(req.params.id);

    if (!exercise) {
      return res.status(404).json({ msg: 'Exercise not found' });
    }

    // Check user
    if (exercise.userId.toString() !== req.user.id) {
      return res.status(401).json({ msg: 'User not authorized' });
    }

    await Exercise.findByIdAndRemove(req.params.id);

    res.json({ msg: 'Exercise removed' });
  } catch (err) {
    console.error(err.message);
    if (err.kind === 'ObjectId') {
      return res.status(404).json({ msg: 'Exercise not found' });
    }
    res.status(500).send('Server error');
  }
};

module.exports = {
  getAllExercises,
  getExerciseById,
  createExercise,
  updateExercise,
  deleteExercise
};