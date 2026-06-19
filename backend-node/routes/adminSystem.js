const express = require('express');
const crypto = require('crypto');
const mongoose = require('mongoose');
const User = require('../models/User');
const SystemConfig = require('../models/SystemConfig');
const AdminAuditLog = require('../models/AdminAuditLog');
const { requireOwner, logAdminAction } = require('../middleware/adminAuth');

const router = express.Router();

// Bug #23 fix: validate MongoDB ObjectId format before DB calls
const isValidObjectId = (id) => mongoose.Types.ObjectId.isValid(id);

const parsePositiveInt = (value, fallback) => {
  const parsed = parseInt(value, 10);
  if (Number.isNaN(parsed) || parsed <= 0) return fallback;
  return parsed;
};

const sanitizeAnnouncementText = (value, maxLen) =>
  String(value || '')
    .replace(/[<>]/g, '')
    .replace(/[\u0000-\u001F\u007F]/g, ' ')
    .replace(/\s+/g, ' ')
    .trim()
    .slice(0, maxLen);

const ALLOWED_ANNOUNCEMENT_TYPES = new Set(['info', 'success', 'warning', 'error']);

/**
 * GET /api/admin/system/health
 */
router.get(
  '/health',
  requireOwner,
  logAdminAction('SYSTEM_HEALTH_CHECK', 'system'),
  async (req, res) => {
    try {
      const health = {
        timestamp: new Date().toISOString(),
        services: {}
      };

      try {
        await mongoose.connection.db.admin().ping();
        health.services.database = { status: 'healthy', latency: 'N/A' };
      } catch (err) {
        console.error('Admin health database ping failed:', err.message);
        health.services.database = { status: 'unhealthy', error: 'Database ping failed' };
      }

      health.services.nodeBackend = {
        status: 'healthy',
        uptime: process.uptime(),
        memory: process.memoryUsage()
      };

      // BUG-N6 fix: estimatedDocumentCount() uses metadata (O(1)) instead of
      // a full collection scan — correct for a health-check endpoint.
      // Active-today still needs a filtered count via countDocuments().
      const [totalUsers, activeToday] = await Promise.all([
        User.estimatedDocumentCount(),
        User.countDocuments({
          updatedAt: { $gte: new Date(Date.now() - 24 * 60 * 60 * 1000) }
        })
      ]);

      health.metrics = {
        totalUsers,
        activeToday
      };

      const allHealthy = Object.values(health.services).every(
        (service) => service.status === 'healthy'
      );
      health.overall = allHealthy ? 'healthy' : 'degraded';

      return res.json(health);
    } catch (error) {
      console.error('Health check error:', error);
      return res.status(500).json({
        overall: 'unhealthy'
      });
    }
  }
);

/**
 * GET /api/admin/system/stats
 */
router.get('/stats', requireOwner, async (req, res) => {
  try {
    const thirtyDaysAgo = new Date(Date.now() - 30 * 24 * 60 * 60 * 1000);

    // PERF-3: Single $facet aggregation replaces 4 separate round-trips.
    const [result] = await User.aggregate([
      {
        $facet: {
          userGrowth: [
            { $match: { createdAt: { $gte: thirtyDaysAgo } } },
            {
              $group: {
                _id: { $dateToString: { format: '%Y-%m-%d', date: '$createdAt' } },
                count: { $sum: 1 }
              }
            },
            { $sort: { _id: 1 } }
          ],
          workoutCompletions: [
            { $unwind: '$workouts' },
            {
              $group: {
                _id: {
                  $dateToString: {
                    format: '%Y-%m-%d',
                    date: { $ifNull: ['$workouts.date', '$createdAt'] }
                  }
                },
                count: { $sum: 1 }
              }
            },
            { $sort: { _id: -1 } },
            { $limit: 30 }
          ],
          goalDistribution: [
            { $group: { _id: '$goal', count: { $sum: 1 } } }
          ],
          experienceDistribution: [
            { $group: { _id: '$experience', count: { $sum: 1 } } }
          ]
        }
      }
    ]);

    return res.json(result || {});
  } catch (error) {
    console.error('System stats error:', error);
    return res.status(500).json({ message: 'Server error' });
  }
});

/**
 * POST /api/admin/system/maintenance
 */
router.post(
  '/maintenance',
  requireOwner,
  logAdminAction('MAINTENANCE_TOGGLE', 'system'),
  async (req, res) => {
    try {
      const { enabled, message } = req.body;

      let config = await SystemConfig.findOne({ key: 'maintenanceMode' });
      if (!config) {
        config = new SystemConfig({ key: 'maintenanceMode', value: {} });
      }

      config.value = {
        enabled: enabled === true,
        message:
          message || 'System is under maintenance. Please try again later.',
        updatedAt: new Date()
      };
      config.updatedBy = req.owner.id;
      config.updatedAt = new Date();

      await config.save();

      return res.json({
        message: `Maintenance mode ${enabled ? 'enabled' : 'disabled'}`,
        maintenance: config.value
      });
    } catch (error) {
      console.error('Maintenance toggle error:', error);
      return res.status(500).json({ message: 'Server error' });
    }
  }
);

/**
 * GET /api/admin/system/maintenance
 * Public endpoint so app can display maintenance status.
 */
router.get('/maintenance', async (req, res) => {
  try {
    const config = await SystemConfig.findOne({ key: 'maintenanceMode' });
    return res.json({
      enabled: config?.value?.enabled || false,
      message: config?.value?.message || null
    });
  } catch (error) {
    return res.status(500).json({ message: 'Server error' });
  }
});

/**
 * GET /api/admin/system/audit-logs
 */
router.get('/audit-logs', requireOwner, async (req, res) => {
  try {
    const page = parsePositiveInt(req.query.page, 1);
    const limit = Math.min(parsePositiveInt(req.query.limit, 50), 200);
    const { action, startDate, endDate } = req.query;

    const query = {};
    if (action) query.action = action;

    if (startDate || endDate) {
      query.timestamp = {};
      if (startDate) query.timestamp.$gte = new Date(startDate);
      if (endDate) query.timestamp.$lte = new Date(endDate);
    }

    const skip = (page - 1) * limit;

    const [logs, total] = await Promise.all([
      AdminAuditLog.find(query)
        .populate('ownerId', 'name email role')
        .sort({ timestamp: -1 })
        .skip(skip)
        .limit(limit)
        .lean(),
      AdminAuditLog.countDocuments(query)
    ]);

    return res.json({
      logs,
      pagination: {
        page,
        limit,
        total,
        pages: Math.ceil(total / limit)
      }
    });
  } catch (error) {
    console.error('Audit logs error:', error);
    return res.status(500).json({ message: 'Server error' });
  }
});

/**
 * POST /api/admin/system/announcement
 */
router.post(
  '/announcement',
  requireOwner,
  logAdminAction('ANNOUNCEMENT_CREATE', 'announcement'),
  async (req, res) => {
    try {
      const { title, message, type = 'info', startDate, endDate } = req.body;
      const safeTitle = sanitizeAnnouncementText(title, 140);
      const safeMessage = sanitizeAnnouncementText(message, 2000);
      const safeType = ALLOWED_ANNOUNCEMENT_TYPES.has(String(type || '').toLowerCase())
        ? String(type).toLowerCase()
        : 'info';

      if (!safeTitle || !safeMessage) {
        return res.status(400).json({ message: 'Title and message required' });
      }

      let config = await SystemConfig.findOne({ key: 'announcements' });
      if (!config) {
        config = new SystemConfig({ key: 'announcements', value: [] });
      }

      const announcement = {
        // Bug #26 fixed: use crypto.randomUUID() for guaranteed uniqueness
        // (Date.now() is not unique if two requests arrive within the same millisecond)
        id: crypto.randomUUID(),
        title: safeTitle,
        message: safeMessage,
        type: safeType,
        startDate: startDate || new Date(),
        endDate,
        createdAt: new Date(),
        createdBy: req.owner.id,
        active: true
      };

      config.value = [...(config.value || []), announcement];
      config.updatedBy = req.owner.id;
      config.updatedAt = new Date();
      await config.save();

      return res.json({
        message: 'Announcement created',
        announcement
      });
    } catch (error) {
      console.error('Announcement error:', error);
      return res.status(500).json({ message: 'Server error' });
    }
  }
);

/**
 * DELETE /api/admin/system/announcement/:announcementId
 */
router.delete(
  '/announcement/:announcementId',
  requireOwner,
  logAdminAction('ANNOUNCEMENT_DELETE', 'announcement'),
  async (req, res) => {
    try {
      const { announcementId } = req.params;
      const config = await SystemConfig.findOne({ key: 'announcements' });

      if (!config || !Array.isArray(config.value)) {
        return res.status(404).json({ message: 'Announcement not found' });
      }

      const nextAnnouncements = config.value.filter(
        (item) => String(item.id) !== String(announcementId)
      );

      if (nextAnnouncements.length === config.value.length) {
        return res.status(404).json({ message: 'Announcement not found' });
      }

      config.value = nextAnnouncements;
      config.updatedBy = req.owner.id;
      config.updatedAt = new Date();
      await config.save();

      return res.json({ message: 'Announcement deleted' });
    } catch (error) {
      console.error('Announcement delete error:', error);
      return res.status(500).json({ message: 'Server error' });
    }
  }
);

/**
 * GET /api/admin/system/announcements
 * Public endpoint for active announcements.
 */
router.get('/announcements', async (req, res) => {
  try {
    const config = await SystemConfig.findOne({ key: 'announcements' });
    const now = new Date();

    const activeAnnouncements = (config?.value || []).filter((item) => {
      if (!item.active) return false;
      if (item.startDate && new Date(item.startDate) > now) return false;
      if (item.endDate && new Date(item.endDate) < now) return false;
      return true;
    });

    return res.json({ announcements: activeAnnouncements });
  } catch (error) {
    return res.status(500).json({ message: 'Server error' });
  }
});

module.exports = router;
