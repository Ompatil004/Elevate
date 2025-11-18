const User = require('../models/User');
const jwt = require('jsonwebtoken');
const config = require('config');

// @desc    Register user
// @route   POST /api/users/register
// @access  Public
const register = async (req, res) => {
  const { name, email, password, fitnessGoals } = req.body;

  try {
    // Check if user already exists
    let user = await User.findOne({ email });
    if (user) {
      return res.status(400).json({ msg: 'User already exists' });
    }

    // Create new user
    user = new User({
      name,
      email,
      password,
      fitnessGoals: fitnessGoals || []
    });

    // Hash password and save user
    await user.save();

    // Create payload for JWT
    const payload = {
      user: {
        id: user.id
      }
    };

    // Sign and return JWT
    const token = jwt.sign(payload, config.get('jwtSecret'), {
      expiresIn: '24h'
    });

    res.status(201).json({
      token,
      user: {
        id: user.id,
        name: user.name,
        email: user.email,
        fitnessGoals: user.fitnessGoals,
        profileCompleted: user.profileCompleted
      }
    });
  } catch (error) {
    console.error(error.message);
    res.status(500).send('Server error');
  }
};

// @desc    Authenticate user & get token
// @route   POST /api/users/login
// @access  Public
const login = async (req, res) => {
  const { email, password } = req.body;

  try {
    // Check if user exists
    const user = await User.findOne({ email });
    if (!user) {
      return res.status(400).json({ msg: 'Invalid Credentials' });
    }

    // Compare password
    const isMatch = await user.comparePassword(password);
    if (!isMatch) {
      return res.status(400).json({ msg: 'Invalid Credentials' });
    }

    // Create payload for JWT
    const payload = {
      user: {
        id: user.id
      }
    };

    // Sign and return JWT
    const token = jwt.sign(payload, config.get('jwtSecret'), {
      expiresIn: '24h'
    });

    res.json({
      token,
      user: {
        id: user.id,
        name: user.name,
        email: user.email,
        fitnessGoals: user.fitnessGoals,
        profileCompleted: user.profileCompleted
      }
    });
  } catch (error) {
    console.error(error.message);
    res.status(500).send('Server error');
  }
};

// @desc    Get user profile
// @route   GET /api/users/profile
// @access  Private
const getProfile = async (req, res) => {
  try {
    const user = await User.findById(req.user.id).select('-password');
    
    if (!user) {
      return res.status(404).json({ msg: 'User not found' });
    }

    res.json(user);
  } catch (error) {
    console.error(error.message);
    res.status(500).send('Server error');
  }
};

// @desc    Update user profile
// @route   PUT /api/users/profile
// @access  Private
const updateProfile = async (req, res) => {
  try {
    const user = await User.findByIdAndUpdate(
      req.user.id,
      { $set: req.body },
      { new: true, runValidators: true }
    ).select('-password');

    if (!user) {
      return res.status(404).json({ msg: 'User not found' });
    }

    res.json(user);
  } catch (error) {
    console.error(error.message);
    res.status(500).send('Server error');
  }
};

// @desc    Complete user profile
// @route   PUT /api/users/complete-profile
// @access  Private
const completeProfile = async (req, res) => {
  try {
    const profileData = req.body;
    profileData.profileCompleted = true; // Mark as completed

    const user = await User.findByIdAndUpdate(
      req.user.id,
      { $set: profileData },
      { new: true, runValidators: true }
    ).select('-password');

    if (!user) {
      return res.status(404).json({ msg: 'User not found' });
    }

    res.json(user);
  } catch (error) {
    console.error(error.message);
    res.status(500).send('Server error');
  }
};

module.exports = {
  register,
  login,
  getProfile,
  updateProfile,
  completeProfile
};