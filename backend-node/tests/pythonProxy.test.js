/**
 * Python Backend Proxy Route Unit Tests
 * Uses Jest + supertest to verify forwarding behavior, error handling, and headers
 */

const express = require('express');
const request = require('supertest');
const jwt = require('jsonwebtoken');
const cookieParser = require('cookie-parser');
const axios = require('axios');

// Mock axios
jest.mock('axios');

process.env.JWT_SECRET = 'test_secret_min_32_chars_for_testing_only';
process.env.ML_API_URL = 'https://elevate-pybackend.onrender.com';

const authMiddleware = require('../middleware/auth');
const pythonProxyRouter = require('../routes/pythonProxy');

function buildApp() {
  const app = express();
  app.use(express.json());
  app.use(cookieParser());
  app.use('/api/python', pythonProxyRouter);
  return app;
}

function makeToken(payload) {
  return jwt.sign(payload, process.env.JWT_SECRET, { expiresIn: '1h' });
}

describe('Python Backend Proxy Route', () => {
  let app;
  let validToken;

  beforeAll(() => {
    app = buildApp();
    validToken = makeToken({ id: 'user123', isSuspended: false });
  });

  beforeEach(() => {
    jest.clearAllMocks();
  });

  it('forwards incoming Authorization header unchanged (200)', async () => {
    // Mock successful Python backend response
    axios.mockResolvedValueOnce({
      status: 200,
      headers: { 'content-type': 'application/json' },
      data: { success: true, plan: 'mock_workout_plan' },
    });

    const res = await request(app)
      .post('/api/python/workout')
      .set('Cookie', `elevate_token=${validToken}`)
      .set('Authorization', 'Bearer incoming_custom_token')
      .send({ some: 'payload' });

    expect(res.status).toBe(200);
    expect(res.body.success).toBe(true);

    // Verify axios was called with the exact Authorization header
    expect(axios).toHaveBeenCalledTimes(1);
    const axiosArgs = axios.mock.calls[0][0];
    expect(axiosArgs.headers.Authorization).toBe('Bearer incoming_custom_token');
    expect(axiosArgs.url).toBe('https://elevate-pybackend.onrender.com/workout');
  });

  it('constructs Authorization Bearer header from legacy x-auth-token header (200)', async () => {
    axios.mockResolvedValueOnce({
      status: 200,
      headers: { 'content-type': 'application/json' },
      data: { success: true, nutrition: 'mock_nutrition_plan' },
    });

    const res = await request(app)
      .post('/api/python/nutrition')
      .set('x-auth-token', validToken)
      .send({ some: 'payload' });

    expect(res.status).toBe(200);
    expect(res.body.success).toBe(true);

    expect(axios).toHaveBeenCalledTimes(1);
    const axiosArgs = axios.mock.calls[0][0];
    expect(axiosArgs.headers.Authorization).toBe(`Bearer ${validToken}`);
    expect(axiosArgs.url).toBe('https://elevate-pybackend.onrender.com/nutrition');
  });

  it('rejects with 401 directly without calling Python when auth token is missing', async () => {
    // We bypass the Node auth middleware (or simulate it returning true but token missing)
    // Actually, our middleware 'auth' itself rejects if no token is found in cookie/x-auth-token.
    const res = await request(app)
      .post('/api/python/workout')
      .send({ some: 'payload' });

    expect(res.status).toBe(401);
    expect(axios).not.toHaveBeenCalled();
  });

  it('returns Python 401 as 401 with safe error message', async () => {
    axios.mockResolvedValueOnce({
      status: 401,
      headers: { 'content-type': 'application/json' },
      data: { error: 'Missing auth token' },
    });

    const res = await request(app)
      .post('/api/python/workout')
      .set('Authorization', 'Bearer bad_token')
      .set('Cookie', `elevate_token=${validToken}`)
      .send({ some: 'payload' });

    expect(res.status).toBe(401);
    expect(res.body.message).toBe('Authentication failed with AI service');
    expect(res.body.error).toBe('Unauthorized');
  });

  it('returns Python 422 as 422 with validation details', async () => {
    axios.mockResolvedValueOnce({
      status: 422,
      headers: { 'content-type': 'application/json' },
      data: { detail: 'validation failed' },
    });

    const res = await request(app)
      .post('/api/python/nutrition')
      .set('Authorization', 'Bearer valid_token')
      .set('Cookie', `elevate_token=${validToken}`)
      .send({ some: 'payload' });

    expect(res.status).toBe(422);
    expect(res.body.message).toBe('Invalid request payload sent to AI service');
    expect(res.body.error).toBe('Unprocessable Entity');
    expect(res.body.details).toEqual({ detail: 'validation failed' });
  });

  it('returns 503 on Python timeout / connection failure', async () => {
    // Simulate connection failure (reject promise)
    axios.mockRejectedValueOnce({
      code: 'ETIMEDOUT',
      message: 'timeout of 120000ms exceeded',
    });

    const res = await request(app)
      .post('/api/python/workout')
      .set('Authorization', 'Bearer valid_token')
      .set('Cookie', `elevate_token=${validToken}`)
      .send({ some: 'payload' });

    expect(res.status).toBe(503);
    expect(res.body.message).toBe('AI service is currently unavailable. Please try again later.');
    expect(res.body.code).toBe('PYTHON_PROXY_FAILED');
  });
});
