const express = require('express');
const router = express.Router();
const User = require('../models/User');
const bcrypt = require('bcryptjs');
const jwt = require('jsonwebtoken');
const crypto = require('crypto');
const { OAuth2Client } = require('google-auth-library');  // ✅ ADD THIS
const { sendPasswordResetToken } = require('../services/securityNotificationService');
// Bug #43/#45 fixed: import auth rate limiters
const { authLoginLimiter, authRegisterLimiter } = require('../middleware/adminRateLimit');
// ARCH-5: Centralized input validation
const { validate, registerRules, loginRules, forgotPasswordRules, resetPasswordRules } = require('../middleware/validate');

// Initialize Google OAuth client
const client = new OAuth2Client(process.env.GOOGLE_CLIENT_ID);
const BCRYPT_SALT_ROUNDS = parseInt(process.env.BCRYPT_SALT_ROUNDS || '12', 10);

// PERF-4: Embed isSuspended in the JWT so the auth middleware can enforce
// suspension without a DB round-trip on every request.
// NOTE: isSuspended is cached for the token lifetime (7 days). When an admin
// suspends a user their existing token will expire within 7 days; for instant
// revocation, call invalidateUserTokens() in the suspend endpoint.
const generateToken = (userId, isSuspended = false) => {
  if (!process.env.JWT_SECRET) {
    throw new Error('JWT_SECRET is not configured');
  }
  return jwt.sign(
    { user: { id: userId.toString(), isSuspended: Boolean(isSuspended) } },
    process.env.JWT_SECRET,
    { expiresIn: '7d' }
  );
};

/**
 * SEC-1: Set the JWT as an HttpOnly, SameSite=Strict cookie so it is
 * inaccessible to JavaScript running on the page.
 *
 * The response body still contains `token` during the transition period
 * so the existing frontend can keep working without changes. Once all
 * clients are updated to rely on the cookie, the body field will be removed.
 */
const setAuthCookie = (res, token) => {
  res.cookie('elevate_token', token, {
    httpOnly: true,                                              // not readable by JS
    secure: process.env.NODE_ENV === 'production',              // HTTPS-only in prod
    sameSite: process.env.NODE_ENV === 'production' ? 'strict' : 'lax',
    maxAge: 7 * 24 * 60 * 60 * 1000,                           // 7 days, mirrors JWT
    path: '/',
  });
};

const getSessionSnapshot = async (req) => {
  const token = req.cookies?.elevate_token;
  if (!token) {
    return { authenticated: false };
  }

  try {
    const decoded = jwt.verify(token, process.env.JWT_SECRET);
    if (typeof decoded?.user?.isSuspended === 'boolean' && decoded.user.isSuspended) {
      return { authenticated: false };
    }

    const userId = decoded?.user?.id || decoded?.id;
    if (!userId) {
      return { authenticated: false };
    }

    return { authenticated: true, userId: userId.toString() };
  } catch {
    return { authenticated: false };
  }
};

// Public session probe used by the SPA to avoid noisy 401s on fresh page loads.
router.get('/session', async (req, res) => {
  try {
    res.json(await getSessionSnapshot(req));
  } catch (error) {
    console.error('Session check error:', error);
    res.status(500).json({ authenticated: false });
  }
});

// ==========================================
// REGISTER
// ==========================================
router.post('/register', authRegisterLimiter, registerRules(), validate, async (req, res) => {
  try {
    const { email, password, name } = req.body;

    if (!email || !password || !name) {
      return res.status(400).json({ message: 'All fields required' });
    }

    // Bug #44 fixed: Enforce input length limits to prevent DoS via bcrypt with huge passwords
    if (String(email).length > 254) {
      return res.status(400).json({ message: 'Email address is too long' });
    }
    if (String(name).length > 100) {
      return res.status(400).json({ message: 'Name must be 100 characters or fewer' });
    }
    if (String(password).length > 128) {
      return res.status(400).json({ message: 'Password must be 128 characters or fewer' });
    }

    // Bug #17 fixed: enforce minimum password length on registration (consistent with reset-password endpoint)
    if (String(password).length < 8) {
      return res.status(400).json({ message: 'Password must be at least 8 characters long' });
    }

    // Check if user exists
    const existingUser = await User.findOne({ email });
    if (existingUser) {
      return res.status(400).json({ message: 'Email already registered' });
    }

    // Hash password
    const salt = await bcrypt.genSalt(BCRYPT_SALT_ROUNDS);
    const hashedPassword = await bcrypt.hash(password, salt);

    // Issue #1: capture registration date + day-of-week (remapped Mon=0 … Sun=6)
    const now = new Date();
    const jsDayOfWeek = now.getDay(); // 0=Sun,1=Mon,...6=Sat
    // remap: Mon→0, Tue→1, … Sun→6
    const firstWorkoutDay = jsDayOfWeek === 0 ? 6 : jsDayOfWeek - 1;

    // Create user
    const user = new User({
      name,
      email,
      password: hashedPassword,
      registrationDate: now,
      firstWorkoutDay
    });

    await user.save();

    // PERF-4: Pass isSuspended into the token payload.
    const token = generateToken(user._id, user.isSuspended);
    // SEC-1: Set HttpOnly cookie in addition to returning token in body
    setAuthCookie(res, token);

    res.status(201).json({
      message: 'User registered successfully',
      token,
      user: {
        id: user._id,
        name: user.name,
        email: user.email,
        age: user.age,
        gender: user.gender,
        height: user.height,
        weight: user.weight,
        goal: user.goal,
        experience: user.experience,
        dietary_preference: user.dietary_preference,
        allergies: user.allergies,
        equipment: user.equipment,
        body_issues: user.body_issues,
        days_per_week: user.days_per_week,
        registrationDate: user.registrationDate,
        firstWorkoutDay: user.firstWorkoutDay
      }
    });
  } catch (error) {
    console.error('Register error:', error);
    res.status(500).json({ message: 'Server error' });
  }
});

// ==========================================
// LOGIN
// ==========================================
router.post('/login', authLoginLimiter, loginRules(), validate, async (req, res) => {
  try {
    const { email, password } = req.body;

    if (!email || !password) {
      return res.status(400).json({ message: 'Email and password required' });
    }

    // Bug #44 fixed: cap login inputs to prevent bcrypt DoS
    if (String(email).length > 254 || String(password).length > 128) {
      return res.status(400).json({ message: 'Invalid credentials' });
    }

    const user = await User.findOne({ email });
    if (!user) {
      return res.status(400).json({ message: 'Invalid credentials' });
    }

    if (user.isSuspended) {
      return res.status(403).json({
        message: 'Account is suspended. Please contact support.'
      });
    }

    if (user.mustChangePassword) {
      return res.status(403).json({
        message: 'Password reset required. Use your reset token to set a new password.',
        mustChangePassword: true
      });
    }

    // Check password
    const isMatch = await bcrypt.compare(password, user.password);
    if (!isMatch) {
      return res.status(400).json({ message: 'Invalid credentials' });
    }

    // PERF-4: Pass isSuspended into the token payload.
    const token = generateToken(user._id, user.isSuspended);
    // SEC-1: Set HttpOnly cookie in addition to returning token in body
    setAuthCookie(res, token);

    res.json({
      message: 'Login successful',
      token,
      user: {
        id: user._id,
        name: user.name,
        email: user.email,
        age: user.age,
        gender: user.gender,
        height: user.height,
        weight: user.weight,
        goal: user.goal,
        experience: user.experience,
        dietary_preference: user.dietary_preference,
        allergies: user.allergies,
        equipment: user.equipment,
        body_issues: user.body_issues,
        days_per_week: user.days_per_week,
        avatar: user.avatar,
        registrationDate: user.registrationDate,
        firstWorkoutDay: user.firstWorkoutDay
      }
    });
  } catch (error) {
    console.error('Login error:', error);
    res.status(500).json({ message: 'Server error' });
  }
});

// ==========================================
// GOOGLE LOGIN
// ==========================================
router.post('/google', authLoginLimiter, async (req, res) => {
  try {
    const { token } = req.body;

    if (!token) {
      return res.status(400).json({ message: 'Token required' });
    }

    // Verify Google token
    const ticket = await client.verifyIdToken({
      idToken: token,
      audience: process.env.GOOGLE_CLIENT_ID
    });

    const { email, name, picture } = ticket.getPayload();

    // Find or create user
    let user = await User.findOne({ email });

    if (!user) {
      // Bug #2 fix: set registration tracking fields so rolling-week plan logic works
      // for users who sign up via Google (same as email registration).
      const now = new Date();
      const jsDayOfWeek = now.getDay(); // 0=Sun, 1=Mon … 6=Sat
      // Convert JS Sunday-first (0-6) → Monday-first (0=Mon … 6=Sun)
      const firstWorkoutDay = jsDayOfWeek === 0 ? 6 : jsDayOfWeek - 1;

      user = new User({
        name,
        email,
        // Bug #5 fixed: never store a predictable placeholder.
        // Hash a random token so no real password string exists and
        // bcrypt comparison against this value will always fail.
        password: await bcrypt.hash(crypto.randomBytes(32).toString('hex'), BCRYPT_SALT_ROUNDS),
        avatar: picture,
        registrationDate: now,
        firstWorkoutDay,
      });
      await user.save();
    } else if (picture && !user.avatar) {
      // Update avatar if user exists but doesn't have one
      user.avatar = picture;
      await user.save();
    }

    if (user.isSuspended) {
      return res.status(403).json({
        message: 'Account is suspended. Please contact support.'
      });
    }

    // BUG-6 fix: block Google OAuth if admin has forced a password change
    if (user.mustChangePassword) {
      return res.status(403).json({
        message: 'Your password must be changed before logging in. Please use the password reset flow.',
        code: 'MUST_CHANGE_PASSWORD'
      });
    }

    // PERF-4: Pass isSuspended into the token payload.
    const jwtToken = generateToken(user._id, user.isSuspended);
    // SEC-1: Set HttpOnly cookie in addition to returning token in body
    setAuthCookie(res, jwtToken);

    res.json({
      message: 'Google login successful',
      token: jwtToken,
      user: {
        id: user._id,
        name: user.name,
        email: user.email,
        avatar: user.avatar,
        registrationDate: user.registrationDate,
        firstWorkoutDay: user.firstWorkoutDay
      }
    });
  } catch (error) {
    console.error('Google login error:', error);
    res.status(500).json({ message: 'Authentication failed. Please try again.' });
  }
});

// ==========================================
// LOGOUT
// ==========================================
router.post('/logout', (req, res) => {
  // SEC-1: Clear the HttpOnly auth cookie on logout
  res.clearCookie('elevate_token', { path: '/', sameSite: 'strict', secure: process.env.NODE_ENV === 'production' });
  res.json({ message: 'Logged out successfully' });
});

// ==========================================
// PASSWORD RESET REQUEST (self-service)
// ==========================================
router.post('/reset-password/request', forgotPasswordRules(), validate, async (req, res) => {
  try {
    const { email } = req.body;

    if (!email) {
      return res.status(400).json({ message: 'Email is required' });
    }

    const user = await User.findOne({ email });

    // Return a generic response for unknown users to reduce account enumeration risk.
    if (!user || user.isSuspended) {
      return res.json({
        message:
          'If an account with that email exists, a reset token has been sent via configured secure channel.'
      });
    }

    const resetToken = crypto.randomBytes(32).toString('hex');
    const salt = await bcrypt.genSalt(BCRYPT_SALT_ROUNDS);

    user.passwordResetTokenHash = await bcrypt.hash(resetToken, salt);
    user.passwordResetTokenExpiresAt = new Date(Date.now() + 15 * 60 * 1000);
    user.passwordResetAt = new Date();
    await user.save();

    try {
      const deliveryResult = await sendPasswordResetToken({
        userEmail: user.email,
        userName: user.name,
        resetToken,
        expiresInMinutes: 15
      });

      return res.json({
        message:
          'If an account with that email exists, a reset token has been sent via configured secure channel.',
        deliveryChannels: deliveryResult.channels
      });
    } catch (deliveryError) {
      // Roll back reset token state when delivery fails.
      user.passwordResetTokenHash = null;
      user.passwordResetTokenExpiresAt = null;
      user.passwordResetAt = null;
      await user.save();

      // Explicit opt-in only: never expose reset tokens in production.
      if (
        process.env.ALLOW_DEV_RESET_TOKEN_RESPONSE === '1' &&
        process.env.NODE_ENV !== 'production'
      ) {
        return res.json({
          message: 'Password reset token generated (development mode)',
          resetToken,
          expiresInMinutes: 15,
          note: 'This token is returned only outside production environments.'
        });
      }

      if (process.env.NODE_ENV !== 'production') {
        console.warn(`[reset-password/request] Reset token generated for ${user.email} (token redacted)`);
      }

      console.error('Reset request delivery error:', deliveryError.message);
      return res.status(503).json({
        message:
          'Password reset delivery is not configured. Please contact support or configure SMTP/PASSWORD_RESET_WEBHOOK_URL.'
      });
    }
  } catch (error) {
    console.error('Reset password request error:', error);
    return res.status(500).json({ message: 'Server error' });
  }
});

// ==========================================
// PASSWORD RESET CONFIRM (token flow)
// ==========================================
router.post('/reset-password/confirm', resetPasswordRules(), validate, async (req, res) => {
  try {
    const { email, resetToken, newPassword } = req.body;

    if (!email || !resetToken || !newPassword) {
      return res.status(400).json({
        message: 'Email, reset token, and new password are required'
      });
    }

    if (String(newPassword).length < 8) {
      return res.status(400).json({
        message: 'New password must be at least 8 characters long'
      });
    }

    const user = await User.findOne({ email });
    if (!user || !user.passwordResetTokenHash || !user.passwordResetTokenExpiresAt) {
      return res.status(400).json({ message: 'Invalid or expired reset token' });
    }

    if (new Date() > new Date(user.passwordResetTokenExpiresAt)) {
      return res.status(400).json({ message: 'Invalid or expired reset token' });
    }

    const isTokenValid = await bcrypt.compare(resetToken, user.passwordResetTokenHash);
    if (!isTokenValid) {
      return res.status(400).json({ message: 'Invalid or expired reset token' });
    }

    const salt = await bcrypt.genSalt(BCRYPT_SALT_ROUNDS);
    user.password = await bcrypt.hash(newPassword, salt);
    user.passwordResetTokenHash = null;
    user.passwordResetTokenExpiresAt = null;
    user.passwordResetAt = new Date();
    user.mustChangePassword = false;
    await user.save();

    return res.json({ message: 'Password updated successfully' });
  } catch (error) {
    console.error('Reset password confirm error:', error);
    return res.status(500).json({ message: 'Server error' });
  }
});

module.exports = router;