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

// Require AFTER env is set
const authMiddleware = require('../middleware/auth');

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
  });
});
