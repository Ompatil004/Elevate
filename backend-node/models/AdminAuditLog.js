const mongoose = require('mongoose');

const AdminAuditLogSchema = new mongoose.Schema({
  ownerId: {
    type: mongoose.Schema.Types.ObjectId,
    ref: 'User',
    required: true
  },
  action: {
    type: String,
    required: true,
    enum: [
      'LOGIN',
      'LOGOUT',
      'ADMIN_LOGIN_FAILED',
      'SECURITY_LOCKOUT',
      'USER_LIST',
      'USER_VIEW',
      'USER_SUSPEND',
      'USER_ACTIVATE',
      'USER_DELETE',
      'USER_PASSWORD_RESET',
      'CONFIG_UPDATE',
      'EXERCISE_ADD',
      'EXERCISE_EDIT',
      'EXERCISE_DELETE',
      'MAINTENANCE_TOGGLE',
      'ANNOUNCEMENT_CREATE',
      'ANNOUNCEMENT_DELETE',
      'SYSTEM_HEALTH_CHECK'
    ]
  },
  targetType: {
    type: String,
    enum: ['user', 'exercise', 'config', 'system', 'announcement', 'owner']
  },
  targetId: String,
  details: mongoose.Schema.Types.Mixed,
  ipAddress: String,
  userAgent: String,
  timestamp: {
    type: Date,
    default: Date.now
  }
});

AdminAuditLogSchema.index({ ownerId: 1, timestamp: -1 });
AdminAuditLogSchema.index({ action: 1, timestamp: -1 });

module.exports = mongoose.model('AdminAuditLog', AdminAuditLogSchema);
