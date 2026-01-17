const express = require('express');
const auth = require('../middleware/auth');
const User = require('../models/User');

const router = express.Router();

// @route    GET api/users/profile
// @desc     Get user profile
// @access   Private
router.get('/profile', auth, async (req, res) => {
  try {
    const user = await User.findById(req.user.id).select('-password');
    res.json(user);
  } catch (err) {
    console.error(err.message);
    res.status(500).send('Server Error');
  }
});

// @route    PUT api/users/profile
// @desc     Update user profile
// @access   Private
router.put('/profile', auth, async (req, res) => {
  try {
    const { firstName, lastName, age, gender, weight, height, fitnessGoal, experienceLevel, preferences } = req.body;

    // Build profile object
    const profileFields = {};
    if (firstName) profileFields.firstName = firstName;
    if (lastName) profileFields.lastName = lastName;
    if (age) profileFields.age = age;
    if (gender) profileFields.gender = gender;
    if (weight) profileFields.weight = weight;
    if (height) profileFields.height = height;
    if (fitnessGoal) profileFields.fitnessGoal = fitnessGoal;
    if (experienceLevel) profileFields.experienceLevel = experienceLevel;
    if (preferences) profileFields.preferences = preferences;

    const user = await User.findByIdAndUpdate(
      req.user.id,
      { $set: profileFields },
      { new: true }
    ).select('-password');

    res.json(user);
  } catch (err) {
    console.error(err.message);
    res.status(500).send('Server Error');
  }
});

module.exports = router;