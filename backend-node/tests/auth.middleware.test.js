/**
 * BUG-C2: Node.js backend integration tests — auth middleware
 *
 * Uses Jest + a lightweight Express app (no real Mongoose connection).
 * Tests: unauthenticated rejection, malformed token, missing header.
 *
 * Run: npm test
 */

const express = require('express');
const request = require('supertest');
const jwt = require('jsonwebtoken');
const cookieParser = require('cookie-parser');

// ── minimal env for tests (no real .env needed) ─────────────────────────────
process.env.JWT_SECRET = 'test_secret_min_32_chars_for_testing_only';

// Mock User model for authoritative suspension check
const mockUsers = {
  user_abc: { _id: 'user_abc', isSuspended: false, role: 'user' },
  user_xyz: { _id: 'user_xyz', isSuspended: false, role: 'user' },
  user_suspended: { _id: 'user_suspended', isSuspended: true, role: 'user' },
  user_suspension_bypass_attempt: { _id: 'user_suspension_bypass_attempt', isSuspended: true, role: 'user' }
};

jest.mock('../models/User', () => ({
  findById: jest.fn().mockImplementation((id) => ({
    select: jest.fn().mockReturnValue({
      lean: jest.fn().mockImplementation(async () => mockUsers[id] || null)
    })
  }))
}));

// Require AFTER env and mocks are set
const authMiddleware = require('../middleware/auth');
const User = require('../models/User');

// ── helpers ─────────────────────────────────────────────────────────────────
function buildApp() {
  const app = express();
  app.use(express.json());
  app.use(cookieParser());
  app.get('/protected', authMiddleware, (req, res) =>
    res.json({ ok: true, userId: req.user.id })
  );
  return app;
}

function makeToken(payload, secret = process.env.JWT_SECRET, options = {}) {
  return jwt.sign(payload, secret, { expiresIn: '1h', ...options });
}

// ── tests ────────────────────────────────────────────────────────────────────
describe('auth middleware', () => {
  let app;

  beforeAll(() => {
    app = buildApp();
  });

  it('rejects requests with no auth cookie (401)', async () => {
    const res = await request(app).get('/protected');
    expect(res.status).toBe(401);
    expect(res.body).toHaveProperty('message');
  });

  it('rejects requests with a malformed token (401)', async () => {
    const res = await request(app)
      .get('/protected')
      .set('Cookie', 'elevate_token=this.is.garbage');
    expect(res.status).toBe(401);
  });

  it('rejects tokens signed with the wrong secret (401)', async () => {
    const token = makeToken({ id: 'user123', isSuspended: false }, 'wrong_secret');
    const res = await request(app)
      .get('/protected')
      .set('Cookie', `elevate_token=${token}`);
    expect(res.status).toBe(401);
  });

  it('rejects expired tokens (401)', async () => {
    const token = makeToken(
      { id: 'user123', isSuspended: false },
      process.env.JWT_SECRET,
      { expiresIn: '-1s' }
    );
    const res = await request(app)
      .get('/protected')
      .set('Cookie', `elevate_token=${token}`);
    expect(res.status).toBe(401);
  });

  it('allows a valid token through (200)', async () => {
    const token = makeToken({ id: 'user_abc', isSuspended: false });
    const res = await request(app)
      .get('/protected')
      .set('Cookie', `elevate_token=${token}`);
    expect(res.status).toBe(200);
    expect(res.body.ok).toBe(true);
    expect(res.body.userId).toBe('user_abc');
  });

  it('blocks suspended users even with a valid token (403)', async () => {
    const token = makeToken({ id: 'user_suspended', isSuspended: true });
    const res = await request(app)
      .get('/protected')
      .set('Cookie', `elevate_token=${token}`);
    expect(res.status).toBe(403);
    expect(res.body.message).toMatch(/Account is suspended/i);
  });

  it('blocks suspended users even if JWT payload contains isSuspended: false (403)', async () => {
    // Attack scenario: token has isSuspended: false, but DB has user suspended
    const token = makeToken({ id: 'user_suspension_bypass_attempt', isSuspended: false });
    const res = await request(app)
      .get('/protected')
      .set('Cookie', `elevate_token=${token}`);
    expect(res.status).toBe(403);
    expect(res.body.message).toMatch(/Account is suspended/i);
  });

  it('rejects tokens when user does not exist in database (401)', async () => {
    // Attack scenario: valid JWT signature for deleted or non-existent user
    const token = makeToken({ id: 'deleted_user_999', isSuspended: false });
    const res = await request(app)
      .get('/protected')
      .set('Cookie', `elevate_token=${token}`);
    expect(res.status).toBe(401);
    expect(res.body.message).toMatch(/User not found/i);
  });

  it('allows a valid token sent via x-auth-token header (200)', async () => {
    const token = makeToken({ id: 'user_xyz', isSuspended: false });
    const res = await request(app)
      .get('/protected')
      .set('x-auth-token', token);
    expect(res.status).toBe(200);
    expect(res.body.ok).toBe(true);
    expect(res.body.userId).toBe('user_xyz');
  });
});
