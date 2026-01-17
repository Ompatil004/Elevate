const express = require('express');
const auth = require('../middleware/auth');
const Workout = require('../models/Workout');

const router = express.Router();

// @route    POST api/workouts
// @desc     Create a new workout
// @access   Private
router.post('/', auth, async (req, res) => {
  try {
    const { name, description, exercises, duration, difficulty, category } = req.body;

    const newWorkout = new Workout({
      userId: req.user.id,
      name,
      description,
      exercises,
      duration,
      difficulty,
      category
    });

    const workout = await newWorkout.save();
    res.json(workout);
  } catch (err) {
    console.error(err.message);
    res.status(500).send('Server Error');
  }
});

// @route    GET api/workouts
// @desc     Get all workouts for a user
// @access   Private
router.get('/', auth, async (req, res) => {
  try {
    const workouts = await Workout.find({ userId: req.user.id }).sort({ createdAt: -1 });
    res.json(workouts);
  } catch (err) {
    console.error(err.message);
    res.status(500).send('Server Error');
  }
});

// @route    GET api/workouts/public
// @desc     Get all public workouts
// @access   Public
router.get('/public', async (req, res) => {
  try {
    const workouts = await Workout.find({ isPublic: true }).sort({ createdAt: -1 });
    res.json(workouts);
  } catch (err) {
    console.error(err.message);
    res.status(500).send('Server Error');
  }
});

// @route    GET api/workouts/:id
// @desc     Get a specific workout
// @access   Private
router.get('/:id', auth, async (req, res) => {
  try {
    const workout = await Workout.findById(req.params.id);

    if (!workout) {
      return res.status(404).json({ msg: 'Workout not found' });
    }

    res.json(workout);
  } catch (err) {
    console.error(err.message);
    res.status(500).send('Server Error');
  }
});

// @route    PUT api/workouts/:id
// @desc     Update a workout
// @access   Private
router.put('/:id', auth, async (req, res) => {
  try {
    let workout = await Workout.findById(req.params.id);

    if (!workout) {
      return res.status(404).json({ msg: 'Workout not found' });
    }

    // Check user
    if (workout.userId.toString() !== req.user.id) {
      return res.status(401).json({ msg: 'User not authorized' });
    }

    const { name, description, exercises, duration, difficulty, category, isPublic } = req.body;

    const workoutFields = {};
    if (name) workoutFields.name = name;
    if (description) workoutFields.description = description;
    if (exercises) workoutFields.exercises = exercises;
    if (duration) workoutFields.duration = duration;
    if (difficulty) workoutFields.difficulty = difficulty;
    if (category) workoutFields.category = category;
    if (typeof isPublic !== 'undefined') workoutFields.isPublic = isPublic;

    workout = await Workout.findByIdAndUpdate(
      req.params.id,
      { $set: workoutFields },
      { new: true }
    );

    res.json(workout);
  } catch (err) {
    console.error(err.message);
    res.status(500).send('Server Error');
  }
});

// @route    DELETE api/workouts/:id
// @desc     Delete a workout
// @access   Private
router.delete('/:id', auth, async (req, res) => {
  try {
    const workout = await Workout.findById(req.params.id);

    if (!workout) {
      return res.status(404).json({ msg: 'Workout not found' });
    }

    // Check user
    if (workout.userId.toString() !== req.user.id) {
      return res.status(401).json({ msg: 'User not authorized' });
    }

    await Workout.findByIdAndRemove(req.params.id);

    res.json({ msg: 'Workout removed' });
  } catch (err) {
    console.error(err.message);
    res.status(500).send('Server Error');
  }
});

module.exports = router;