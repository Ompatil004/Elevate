const express = require('express');
const User = require('../models/User');
const Exercise = require('../models/Exercise');
const bcrypt = require('bcryptjs');
const jwt = require('jsonwebtoken');
const config = require('config');
const auth = require('../middleware/auth');
const {
  register,
  login,
  getProfile,
  updateProfile,
  completeProfile
} = require('../controllers/UserController');

const router = express.Router();

// @route    GET api/users/test
// @desc     Test users route
// @access   Public
router.get('/test', (req, res) => {
  res.json({ msg: 'Users route is working!' });
});

// @route    POST api/users/register
// @desc     Register user
// @access   Public
router.post('/register', async (req, res) => {
  try {
    const { name, email, password } = req.body;

    // Simple validation
    if (!name || !email || !password) {
      return res.status(400).json({ msg: 'Please enter all fields' });
    }

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

    // Create JWT token
    const payload = {
      user: {
        id: user.id
      }
    };

    jwt.sign(
      payload,
      config.get('jwtSecret'),
      { expiresIn: '7 days' },
      (err, token) => {
        if (err) throw err;
        res.json({
          token,
          user: {
            id: user.id,
            name: user.name,
            email: user.email,
            profileCompleted: user.profileCompleted
          }
        });
      }
    );

  } catch (err) {
    console.error(err.message);
    res.status(500).send('Server error');
  }
});

// @route    POST api/users/login
// @desc     Login user
// @access   Public
router.post('/login', async (req, res) => {
  try {
    const { email, password } = req.body;

    // Simple validation
    if (!email || !password) {
      return res.status(400).json({ msg: 'Please enter all fields' });
    }

    // Check if user exists
    let user = await User.findOne({ email });
    if (!user) {
      return res.status(400).json({ msg: 'Invalid credentials' });
    }

    // Check password
    const isMatch = await bcrypt.compare(password, user.password);
    if (!isMatch) {
      return res.status(400).json({ msg: 'Invalid credentials' });
    }

    // Create JWT token
    const payload = {
      user: {
        id: user.id
      }
    };

    jwt.sign(
      payload,
      config.get('jwtSecret'),
      { expiresIn: '7 days' },
      (err, token) => {
        if (err) throw err;
        res.json({
          token,
          user: {
            id: user.id,
            name: user.name,
            email: user.email,
            profileCompleted: user.profileCompleted
          }
        });
      }
    );

  } catch (err) {
    console.error(err.message);
    res.status(500).send('Server error');
  }
});

// @route    GET api/users/profile
// @desc     Get user profile
// @access   Private
router.get('/profile', auth, async (req, res) => {
  try {
    const user = await User.findById(req.user.id).select('-password');
    res.json({
      id: user.id,
      name: user.name,
      email: user.email,
      profileCompleted: user.profileCompleted,
      age: user.age,
      gender: user.gender,
      weight: user.weight,
      height: user.height,
      fitnessGoals: user.fitnessGoals,
      activityLevel: user.activityLevel,
      dietaryPreferences: user.dietaryPreferences,
      healthConditions: user.healthConditions,
      date: user.date
    });
  } catch (err) {
    console.error(err.message);
    res.status(500).send('Server error');
  }
});

// @route    PUT api/users/complete-profile
// @desc     Complete user profile with additional information
// @access   Private
router.put('/complete-profile', auth, async (req, res) => {
  try {
    const {
      age,
      gender,
      weight,
      height,
      fitnessGoals,
      activityLevel,
      dietaryPreferences,
      healthConditions
    } = req.body;

    // Validation - check required fields
    if (!age || !gender || !weight || !height || !fitnessGoals || !activityLevel) {
      return res.status(400).json({ msg: 'Please provide all required profile information' });
    }

    // Update user profile
    const user = await User.findByIdAndUpdate(
      req.user.id,
      {
        age,
        gender,
        weight,
        height,
        fitnessGoals,
        activityLevel,
        dietaryPreferences: dietaryPreferences || [],
        healthConditions: healthConditions || [],
        profileCompleted: true
      },
      { new: true }
    ).select('-password');

    res.json(user);
  } catch (err) {
    console.error(err.message);
    res.status(500).send('Server error');
  }
});

module.exports = router;