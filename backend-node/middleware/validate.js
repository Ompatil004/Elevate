/**
 * ARCH-5: Centralized input validation schemas using express-validator.
 *
 * Usage in routes:
 *   const { validate, registerRules, loginRules } = require('../middleware/validate');
 *   router.post('/register', authRegisterLimiter, registerRules(), validate, handler);
 *
 * All validation errors are returned in a consistent shape:
 *   { success: false, errors: [{ field, message }] }
 */

const { body, param, query, validationResult } = require('express-validator');

/**
 * Runs accumulated validators and short-circuits with 422 if any fail.
 * Call this as the *last* middleware before the route handler.
 */
const validate = (req, res, next) => {
    const errors = validationResult(req);
    if (!errors.isEmpty()) {
        return res.status(422).json({
            success: false,
            errors: errors.array().map(e => ({ field: e.path, message: e.msg })),
        });
    }
    return next();
};

// ── Auth routes ──────────────────────────────────────────────────────────────

const registerRules = () => [
    body('email')
        .isEmail().withMessage('A valid email address is required')
        .normalizeEmail()
        .isLength({ max: 254 }).withMessage('Email address is too long'),
    body('password')
        .isLength({ min: 8 }).withMessage('Password must be at least 8 characters')
        .isLength({ max: 128 }).withMessage('Password must be 128 characters or fewer'),
    body('name')
        .trim()
        .notEmpty().withMessage('Name is required')
        .isLength({ max: 100 }).withMessage('Name must be 100 characters or fewer')
        .matches(/^[\p{L}\p{M}\s\-'.]+$/u).withMessage('Name contains invalid characters'),
];

const loginRules = () => [
    body('email')
        .isEmail().withMessage('A valid email address is required')
        .normalizeEmail(),
    body('password')
        .notEmpty().withMessage('Password is required')
        .isLength({ max: 128 }).withMessage('Password is too long'),
];

const forgotPasswordRules = () => [
    body('email')
        .isEmail().withMessage('A valid email address is required')
        .normalizeEmail(),
];

const resetPasswordRules = () => [
    body('token')
        .notEmpty().withMessage('Reset token is required')
        .isHexadecimal().withMessage('Invalid reset token format'),
    body('password')
        .isLength({ min: 8 }).withMessage('Password must be at least 8 characters')
        .isLength({ max: 128 }).withMessage('Password must be 128 characters or fewer'),
];

// ── Profile routes ────────────────────────────────────────────────────────────

const profileUpdateRules = () => [
    body('name')
        .optional()
        .trim()
        .isLength({ max: 100 }).withMessage('Name must be 100 characters or fewer'),
    body('age')
        .optional()
        .isInt({ min: 13, max: 120 }).withMessage('Age must be between 13 and 120'),
    body('weight')
        .optional()
        .isFloat({ min: 20, max: 500 }).withMessage('Weight must be between 20 and 500 kg'),
    body('height')
        .optional()
        .isFloat({ min: 50, max: 300 }).withMessage('Height must be between 50 and 300 cm'),
    body('fitnessGoal')
        .optional()
        .isIn(['weight_loss', 'muscle_gain', 'maintenance', 'endurance', 'flexibility'])
        .withMessage('Invalid fitness goal'),
    body('activityLevel')
        .optional()
        .isIn(['sedentary', 'lightly_active', 'moderately_active', 'very_active', 'extra_active'])
        .withMessage('Invalid activity level'),
];

// ── Admin routes ──────────────────────────────────────────────────────────────

const adminLoginRules = () => [
    body('email')
        .isEmail().withMessage('A valid email address is required')
        .normalizeEmail(),
    body('password')
        .notEmpty().withMessage('Password is required')
        .isLength({ max: 128 }).withMessage('Password is too long'),
    body('adminKey')
        .notEmpty().withMessage('Admin key is required')
        .isLength({ max: 256 }).withMessage('Admin key is too long'),
];

const mongoIdRules = (paramName = 'id') => [
    param(paramName)
        .isMongoId().withMessage(`${paramName} must be a valid MongoDB ObjectId`),
];

module.exports = {
    validate,
    registerRules,
    loginRules,
    forgotPasswordRules,
    resetPasswordRules,
    profileUpdateRules,
    adminLoginRules,
    mongoIdRules,
};
