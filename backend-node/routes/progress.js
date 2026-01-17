const express = require('express');
const auth = require('../middleware/auth');
const Progress = require('../models/Progress');

const router = express.Router();

// @route    POST api/progress
// @desc     Log progress
// @access   Private
router.post('/', auth, async (req, res) => {
  try {
    const { date, weight, bodyFatPercentage, muscleMass, measurements, workoutLog, mealLog, repCounts, mood, sleepHours, waterIntake, notes } = req.body;

    const newProgress = new Progress({
      userId: req.user.id,
      date,
      weight,
      bodyFatPercentage,
      muscleMass,
      measurements,
      workoutLog,
      mealLog,
      repCounts,
      mood,
      sleepHours,
      waterIntake,
      notes
    });

    const progress = await newProgress.save();
    res.json(progress);
  } catch (err) {
    console.error(err.message);
    res.status(500).send('Server Error');
  }
});

// @route    GET api/progress
// @desc     Get all progress logs for a user
// @access   Private
router.get('/', auth, async (req, res) => {
  try {
    const progressLogs = await Progress.find({ userId: req.user.id }).sort({ date: -1 });
    res.json(progressLogs);
  } catch (err) {
    console.error(err.message);
    res.status(500).send('Server Error');
  }
});

// @route    GET api/progress/:date
// @desc     Get progress for a specific date
// @access   Private
router.get('/:date', auth, async (req, res) => {
  try {
    const date = new Date(req.params.date);
    const progress = await Progress.findOne({ 
      userId: req.user.id, 
      date: { 
        $gte: new Date(date.setHours(0, 0, 0, 0)), 
        $lt: new Date(date.setHours(23, 59, 59, 999)) 
      } 
    });

    if (!progress) {
      return res.status(404).json({ msg: 'No progress found for this date' });
    }

    res.json(progress);
  } catch (err) {
    console.error(err.message);
    res.status(500).send('Server Error');
  }
});

// @route    PUT api/progress/:id
// @desc     Update a progress log
// @access   Private
router.put('/:id', auth, async (req, res) => {
  try {
    let progress = await Progress.findById(req.params.id);

    if (!progress) {
      return res.status(404).json({ msg: 'Progress log not found' });
    }

    // Check user
    if (progress.userId.toString() !== req.user.id) {
      return res.status(401).json({ msg: 'User not authorized' });
    }

    const { weight, bodyFatPercentage, muscleMass, measurements, workoutLog, mealLog, repCounts, mood, sleepHours, waterIntake, notes } = req.body;

    const progressFields = {};
    if (weight) progressFields.weight = weight;
    if (bodyFatPercentage) progressFields.bodyFatPercentage = bodyFatPercentage;
    if (muscleMass) progressFields.muscleMass = muscleMass;
    if (measurements) progressFields.measurements = measurements;
    if (workoutLog) progressFields.workoutLog = workoutLog;
    if (mealLog) progressFields.mealLog = mealLog;
    if (repCounts) progressFields.repCounts = repCounts;
    if (mood) progressFields.mood = mood;
    if (sleepHours) progressFields.sleepHours = sleepHours;
    if (waterIntake) progressFields.waterIntake = waterIntake;
    if (notes) progressFields.notes = notes;

    progress = await Progress.findByIdAndUpdate(
      req.params.id,
      { $set: progressFields },
      { new: true }
    );

    res.json(progress);
  } catch (err) {
    console.error(err.message);
    res.status(500).send('Server Error');
  }
});

// @route    DELETE api/progress/:id
// @desc     Delete a progress log
// @access   Private
router.delete('/:id', auth, async (req, res) => {
  try {
    const progress = await Progress.findById(req.params.id);

    if (!progress) {
      return res.status(404).json({ msg: 'Progress log not found' });
    }

    // Check user
    if (progress.userId.toString() !== req.user.id) {
      return res.status(401).json({ msg: 'User not authorized' });
    }

    await Progress.findByIdAndRemove(req.params.id);

    res.json({ msg: 'Progress log removed' });
  } catch (err) {
    console.error(err.message);
    res.status(500).send('Server Error');
  }
});

module.exports = router;