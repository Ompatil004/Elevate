const express = require('express');
const bcrypt = require('bcryptjs');
const crypto = require('crypto');
const mongoose = require('mongoose');
const { sendPasswordResetToken } = require('../services/securityNotificationService');
const User = require('../models/User');
const { requireOwner, logAdminAction } = require('../middleware/adminAuth');

const router = express.Router();

// Bug #1 fix: escape regex metacharacters to prevent ReDoS / NoSQL injection
const escapeRegex = (str) => String(str).replace(/[.*+?^${}()|[\]\\]/g, '\\$&');

// Bug #23 fix: validate MongoDB ObjectId format before DB calls
const isValidObjectId = (id) => mongoose.Types.ObjectId.isValid(id);

const parsePositiveInt = (value, fallback) => {
  const parsed = parseInt(value, 10);
  if (Number.isNaN(parsed) || parsed <= 0) return fallback;
  return parsed;
};

const allowedSortFields = new Set([
  'createdAt',
  'updatedAt',
  'name',
  'email',
  'goal',
  'experience',
  'isSuspended'
]);

/**
 * GET /api/admin/users/stats/overview
 */
router.get('/stats/overview', requireOwner, async (req, res) => {
  try {
    const today = new Date();
    const dateKey = today.toISOString().slice(0, 10);
    const lastWeek = new Date(today.getTime() - 7 * 24 * 60 * 60 * 1000);
    const lastMonth = new Date(today.getTime() - 30 * 24 * 60 * 60 * 1000);

    const [
      totalUsers,
      newUsersThisWeek,
      newUsersThisMonth,
      usersByGoal,
      suspendedUsers,
      activeToday
    ] = await Promise.all([
      User.countDocuments(),
      User.countDocuments({ createdAt: { $gte: lastWeek } }),
      User.countDocuments({ createdAt: { $gte: lastMonth } }),
      User.aggregate([
        { $group: { _id: '$goal', count: { $sum: 1 } } },
        { $sort: { count: -1 } }
      ]),
      User.countDocuments({ isSuspended: true }),
      User.countDocuments({
        $or: [
          { lastWorkoutDate: { $gte: dateKey } },
          { 'meals.date': { $gte: dateKey } }
        ]
      })
    ]);

    return res.json({
      totalUsers,
      newUsersThisWeek,
      newUsersThisMonth,
      usersByGoal,
      suspendedUsers,
      activeToday
    });
  } catch (error) {
    console.error('User stats error:', error);
    return res.status(500).json({ message: 'Server error' });
  }
});

/**
 * GET /api/admin/users
 */
router.get('/', requireOwner, logAdminAction('USER_LIST', 'user'), async (req, res) => {
  try {
    const page = parsePositiveInt(req.query.page, 1);
    const limit = Math.min(parsePositiveInt(req.query.limit, 20), 100);
    const {
      search,
      role,
      goal,
      isSuspended,
      sortBy = 'createdAt',
      sortOrder = 'desc'
    } = req.query;

    const query = {};

    if (search) {
      query.$or = [
        // Bug #1 fixed: escape regex to prevent ReDoS / injection
        { name: { $regex: escapeRegex(search), $options: 'i' } },
        { email: { $regex: escapeRegex(search), $options: 'i' } }
      ];
    }

    if (role) query.role = role;
    if (goal) query.goal = goal;
    if (isSuspended !== undefined) query.isSuspended = isSuspended === 'true';

    const safeSortBy = allowedSortFields.has(sortBy) ? sortBy : 'createdAt';
    const sort = { [safeSortBy]: sortOrder === 'asc' ? 1 : -1 };
    const skip = (page - 1) * limit;

    const [users, total] = await Promise.all([
      User.find(query)
        .select('-password -passwordResetTokenHash -passwordResetTokenExpiresAt')
        .sort(sort)
        .skip(skip)
        .limit(limit)
        .lean(),
      User.countDocuments(query)
    ]);

    return res.json({
      users,
      pagination: {
        page,
        limit,
        total,
        pages: Math.ceil(total / limit)
      }
    });
  } catch (error) {
    console.error('List users error:', error);
    return res.status(500).json({ message: 'Server error' });
  }
});

/**
 * GET /api/admin/users/:id
 */
router.get('/:id', requireOwner, logAdminAction('USER_VIEW', 'user'), async (req, res) => {
  try {
    // Bug #23 fixed: validate ObjectId before DB call
    if (!isValidObjectId(req.params.id)) {
      return res.status(400).json({ message: 'Invalid user ID format' });
    }
    const user = await User.findById(req.params.id).select(
      '-password -passwordResetTokenHash -passwordResetTokenExpiresAt'
    );

    if (!user) {
      return res.status(404).json({ message: 'User not found' });
    }

    return res.json({
      user,
      summary: {
        workoutCount: Array.isArray(user.workouts) ? user.workouts.length : 0,
        mealCount: Array.isArray(user.meals) ? user.meals.length : 0,
        trendsCount: Array.isArray(user.trends) ? user.trends.length : 0
      }
    });
  } catch (error) {
    console.error('Get user error:', error);
    return res.status(500).json({ message: 'Server error' });
  }
});

/**
 * POST /api/admin/users/:id/suspend
 */
router.post('/:id/suspend', requireOwner, logAdminAction('USER_SUSPEND', 'user'), async (req, res) => {
  try {
    const { reason } = req.body;
    // Bug #23 fixed: validate ObjectId before DB call
    if (!isValidObjectId(req.params.id)) {
      return res.status(400).json({ message: 'Invalid user ID format' });
    }
    const user = await User.findById(req.params.id);

    if (!user) {
      return res.status(404).json({ message: 'User not found' });
    }

    if (user.role === 'owner') {
      return res.status(403).json({ message: 'Cannot suspend owner account' });
    }

    // Bug #9 fixed: use findByIdAndUpdate for atomic operation
    const updatedUser = await User.findByIdAndUpdate(
      req.params.id,
      {
        $set: {
          isSuspended: true,
          suspendedAt: new Date(),
          suspensionReason: reason || 'Administrative action'
        }
      },
      { new: true }
    );

    return res.json({
      message: 'User suspended successfully',
      user: {
        id: updatedUser._id,
        name: updatedUser.name,
        email: updatedUser.email,
        isSuspended: updatedUser.isSuspended,
        suspendedAt: updatedUser.suspendedAt
      }
    });
  } catch (error) {
    console.error('Suspend user error:', error);
    return res.status(500).json({ message: 'Server error' });
  }
});

/**
 * POST /api/admin/users/:id/activate
 */
router.post('/:id/activate', requireOwner, logAdminAction('USER_ACTIVATE', 'user'), async (req, res) => {
  try {
    // Bug #23 fixed: validate ObjectId before DB call
    if (!isValidObjectId(req.params.id)) {
      return res.status(400).json({ message: 'Invalid user ID format' });
    }
    const user = await User.findById(req.params.id);

    if (!user) {
      return res.status(404).json({ message: 'User not found' });
    }

    // Bug #9 fixed: use findByIdAndUpdate for atomic operation
    const updatedUser = await User.findByIdAndUpdate(
      req.params.id,
      {
        $set: {
          isSuspended: false,
          suspendedAt: null,
          suspensionReason: null
        }
      },
      { new: true }
    );

    return res.json({
      message: 'User activated successfully',
      user: {
        id: updatedUser._id,
        name: updatedUser.name,
        email: updatedUser.email,
        isSuspended: updatedUser.isSuspended
      }
    });
  } catch (error) {
    console.error('Activate user error:', error);
    return res.status(500).json({ message: 'Server error' });
  }
});

/**
 * POST /api/admin/users/:id/reset-password
 */
router.post('/:id/reset-password', requireOwner, logAdminAction('USER_PASSWORD_RESET', 'user'), async (req, res) => {
  try {
    // Bug #23 fixed: validate ObjectId before DB call
    if (!isValidObjectId(req.params.id)) {
      return res.status(400).json({ message: 'Invalid user ID format' });
    }
    const user = await User.findById(req.params.id);

    if (!user) {
      return res.status(404).json({ message: 'User not found' });
    }

    if (user.role === 'owner') {
      return res.status(403).json({
        message: 'Cannot reset owner password from this endpoint'
      });
    }

    const resetToken = crypto.randomBytes(32).toString('hex');
    const salt = await bcrypt.genSalt(10);

    user.passwordResetTokenHash = await bcrypt.hash(resetToken, salt);
    user.passwordResetTokenExpiresAt = new Date(Date.now() + 15 * 60 * 1000);
    user.passwordResetAt = new Date();
    user.mustChangePassword = true;
    await user.save();

    try {
      const deliveryResult = await sendPasswordResetToken({
        userEmail: user.email,
        userName: user.name,
        resetToken,
        expiresInMinutes: 15,
        requestedBy: req.owner
      });

      return res.json({
        message: 'Password reset initiated and delivered securely',
        expiresInMinutes: 15,
        deliveryChannels: deliveryResult.channels
      });
    } catch (deliveryError) {
      user.passwordResetTokenHash = null;
      user.passwordResetTokenExpiresAt = null;
      user.passwordResetAt = null;
      user.mustChangePassword = false;
      await user.save();

      console.error('Secure reset delivery error:', deliveryError.message);
      return res.status(503).json({
        message:
          'Secure reset delivery is not configured or failed. Configure SMTP or PASSWORD_RESET_WEBHOOK_URL.'
      });
    }
  } catch (error) {
    console.error('Reset password error:', error);
    return res.status(500).json({ message: 'Server error' });
  }
});

/**
 * DELETE /api/admin/users/:id
 */
router.delete('/:id', requireOwner, logAdminAction('USER_DELETE', 'user'), async (req, res) => {
  try {
    // Bug #23 fixed: validate ObjectId before DB call
    if (!isValidObjectId(req.params.id)) {
      return res.status(400).json({ message: 'Invalid user ID format' });
    }
    const user = await User.findById(req.params.id);

    if (!user) {
      return res.status(404).json({ message: 'User not found' });
    }

    if (user.role === 'owner') {
      return res.status(403).json({ message: 'Cannot delete owner account' });
    }

    await User.findByIdAndDelete(req.params.id);

    return res.json({
      message: 'User deleted successfully',
      deletedUserId: req.params.id
    });
  } catch (error) {
    console.error('Delete user error:', error);
    return res.status(500).json({ message: 'Server error' });
  }
});

module.exports = router;
