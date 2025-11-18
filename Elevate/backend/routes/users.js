const express = require('express');
const router = express.Router();
const bcrypt = require('bcryptjs');
const jwt = require('jsonwebtoken');
const User = require('../models/User');
const auth = require('../middleware/auth');

// @route   POST api/users/register
// @desc    Register user
// @access  Public
router.post('/register', async (req, res) => {
  try {
    const { name, email, password } = req.body;

    // Check if user already exists
    let user = await User.findOne({ email });
    if (user) {
      return res.status(400).json({ msg: 'User already exists' });
    }

    // Create new user
    user = new User({
      name,
      email,
      password
    });

    // Hash password
    const salt = await bcrypt.genSalt(10);
    user.password = await bcrypt.hash(password, salt);

    await user.save();

    // Generate JWT token
    const payload = {
      user: {
        id: user.id
      }
    };

    const token = jwt.sign(
      payload,
      process.env.JWT_SECRET || 'default_jwt_secret',
      { expiresIn: '7 days' }
    );

    res.json({
      token,
      user: {
        id: user.id,
        name: user.name,
        email: user.email,
        fitnessGoal: user.fitnessGoal,
        profileSetupComplete: user.profileSetupComplete
      }
    });
  } catch (error) {
    console.error(error.message);
    res.status(500).send('Server error');
  }
});

// @route   POST api/users/login
// @desc    Authenticate user & get token
// @access  Public
router.post('/login', async (req, res) => {
  try {
    const { email, password } = req.body;

    // Check for user
    let user = await User.findOne({ email });
    if (!user) {
      return res.status(400).json({ msg: 'Invalid Credentials' });
    }

    const isMatch = await bcrypt.compare(password, user.password);
    if (!isMatch) {
      return res.status(400).json({ msg: 'Invalid Credentials' });
    }

    // Generate JWT token
    const payload = {
      user: {
        id: user.id
      }
    };

    const token = jwt.sign(
      payload,
      process.env.JWT_SECRET || 'default_jwt_secret',
      { expiresIn: '7 days' }
    );

    res.json({
      token,
      user: {
        id: user.id,
        name: user.name,
        email: user.email,
        fitnessGoal: user.fitnessGoal,
        profileSetupComplete: user.profileSetupComplete
      }
    });
  } catch (error) {
    console.error(error.message);
    res.status(500).send('Server error');
  }
});

// @route   GET api/users/profile
// @desc    Get user profile
// @access  Private
router.get('/profile', auth, async (req, res) => {
  try {
    const user = await User.findById(req.user.id).select('-password');
    res.json(user);
  } catch (error) {
    console.error(error.message);
    res.status(500).send('Server error');
  }
});

// @route   PUT api/users/profile
// @desc    Update user profile
// @access  Private
router.put('/profile', auth, async (req, res) => {
  try {
    const {
      name,
      email,
      fitnessGoal,
      height,
      weight,
      age,
      activityLevel,
      dietPreference,
      profileSetupComplete
    } = req.body;

    // Build profile object
    const profileFields = {};

    // Only update fields that are provided
    if (name) profileFields.name = name;
    if (height !== undefined) profileFields.height = height;
    if (weight !== undefined) profileFields.weight = weight;
    if (age !== undefined) profileFields.age = age;
    if (fitnessGoal) profileFields.fitnessGoal = fitnessGoal;
    if (activityLevel) profileFields.activityLevel = activityLevel;
    if (dietPreference) profileFields.dietPreference = dietPreference;
    if (profileSetupComplete !== undefined) profileFields.profileSetupComplete = profileSetupComplete;

    // Only check for email if it's being updated
    if (email && email !== req.user.email) {
      // Check if email already exists (excluding current user)
      const existingUser = await User.findOne({
        email,
        _id: { $ne: req.user.id }
      });
      if (existingUser) {
        return res.status(400).json({ msg: 'Email already exists' });
      }
      profileFields.email = email;
    }

    // Update profile
    const user = await User.findByIdAndUpdate(
      req.user.id,
      { $set: profileFields },
      { new: true } // Return updated document
    ).select('-password');

    if (!user) {
      return res.status(404).json({ msg: 'User not found' });
    }

    res.json(user);
  } catch (error) {
    console.error('Update profile error:', error.message);
    res.status(500).json({ msg: 'Server error', error: error.message });
  }
});

module.exports = router;