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
    process.env.ML_API_URL = 'https://elevate-pybackend.onrender.com';
  });

  it('cookie-only elevate_token forwards Bearer token (200)', async () => {
    axios.mockResolvedValueOnce({
      status: 200,
      headers: { 'content-type': 'application/json' },
      data: { success: true },
    });

    const res = await request(app)
      .post('/api/python/workout')
      .set('Cookie', `elevate_token=${validToken}`)
      .send({ some: 'payload' });

    expect(res.status).toBe(200);
    expect(axios).toHaveBeenCalledTimes(1);
    const axiosArgs = axios.mock.calls[0][0];
    expect(axiosArgs.headers.Authorization).toBe(`Bearer ${validToken}`);
  });

  it('Authorization header takes precedence over cookie (200)', async () => {
    axios.mockResolvedValueOnce({
      status: 200,
      headers: { 'content-type': 'application/json' },
      data: { success: true },
    });

    const customToken = 'Bearer custom_precedence_token';
    const res = await request(app)
      .post('/api/python/workout')
      .set('Cookie', `elevate_token=${validToken}`)
      .set('Authorization', customToken)
      .send({ some: 'payload' });

    expect(res.status).toBe(200);
    expect(axios).toHaveBeenCalledTimes(1);
    const axiosArgs = axios.mock.calls[0][0];
    expect(axiosArgs.headers.Authorization).toBe(customToken);
  });

  it('missing all auth methods returns 401 JSON', async () => {
    const res = await request(app)
      .post('/api/python/workout')
      .send({ some: 'payload' });

    expect(res.status).toBe(401);
    expect(res.body.message).toBeDefined();
    expect(axios).not.toHaveBeenCalled();
  });

  it('malformed/missing ML_API_URL returns 503 JSON without crashing app', async () => {
    process.env.ML_API_URL = 'invalid-url-no-http';

    const res = await request(app)
      .post('/api/python/workout')
      .set('Cookie', `elevate_token=${validToken}`)
      .send({ some: 'payload' });

    expect(res.status).toBe(503);
    expect(res.body.success).toBe(false);
    expect(res.body.error.code).toBe('PYTHON_SERVICE_NOT_CONFIGURED');
    expect(axios).not.toHaveBeenCalled();
  });

  it('exact /nutrition route mapping (200)', async () => {
    axios.mockResolvedValueOnce({
      status: 200,
      headers: { 'content-type': 'application/json' },
      data: { success: true },
    });

    const res = await request(app)
      .post('/api/python/nutrition')
      .set('Cookie', `elevate_token=${validToken}`)
      .send({});

    expect(res.status).toBe(200);
    const axiosArgs = axios.mock.calls[0][0];
    expect(axiosArgs.url).toBe('https://elevate-pybackend.onrender.com/nutrition');
  });

  it('exact /week route mapping (200)', async () => {
    axios.mockResolvedValueOnce({
      status: 200,
      headers: { 'content-type': 'application/json' },
      data: { success: true },
    });

    const res = await request(app)
      .get('/api/python/week')
      .set('Cookie', `elevate_token=${validToken}`);

    expect(res.status).toBe(200);
    const axiosArgs = axios.mock.calls[0][0];
    expect(axiosArgs.url).toBe('https://elevate-pybackend.onrender.com/api/weekly-plan');
  });

  it('exact /weekly-plan route mapping (200)', async () => {
    axios.mockResolvedValueOnce({
      status: 200,
      headers: { 'content-type': 'application/json' },
      data: { success: true },
    });

    const res = await request(app)
      .get('/api/python/weekly-plan')
      .set('Cookie', `elevate_token=${validToken}`);

    expect(res.status).toBe(200);
    const axiosArgs = axios.mock.calls[0][0];
    expect(axiosArgs.url).toBe('https://elevate-pybackend.onrender.com/api/weekly-plan');
  });

  it('exact /api/weekly-plan route mapping (200)', async () => {
    axios.mockResolvedValueOnce({
      status: 200,
      headers: { 'content-type': 'application/json' },
      data: { success: true },
    });

    const res = await request(app)
      .get('/api/python/api/weekly-plan')
      .set('Cookie', `elevate_token=${validToken}`);

    expect(res.status).toBe(200);
    const axiosArgs = axios.mock.calls[0][0];
    expect(axiosArgs.url).toBe('https://elevate-pybackend.onrender.com/api/weekly-plan');
  });

  it('exact /api/daily-log/week route mapping (200)', async () => {
    axios.mockResolvedValueOnce({
      status: 200,
      headers: { 'content-type': 'application/json' },
      data: { success: true },
    });

    const res = await request(app)
      .get('/api/python/api/daily-log/week')
      .set('Cookie', `elevate_token=${validToken}`);

    expect(res.status).toBe(200);
    const axiosArgs = axios.mock.calls[0][0];
    expect(axiosArgs.url).toBe('https://elevate-pybackend.onrender.com/api/daily-log/week');
  });

  it('upstream HTML 502 becomes safe JSON 502', async () => {
    axios.mockResolvedValueOnce({
      status: 502,
      headers: { 'content-type': 'text/html' },
      data: '<html>Bad Gateway</html>',
    });

    const res = await request(app)
      .post('/api/python/workout')
      .set('Cookie', `elevate_token=${validToken}`);

    expect(res.status).toBe(502);
    expect(res.body.success).toBe(false);
    expect(res.body.error.code).toBe('PYTHON_UPSTREAM_ERROR');
    expect(res.body.error.message).toBe('AI service is temporarily unavailable');
  });

  it('upstream 500 preserves status', async () => {
    axios.mockResolvedValueOnce({
      status: 500,
      headers: { 'content-type': 'application/json' },
      data: { error: 'Internal Server Error' },
    });

    const res = await request(app)
      .post('/api/python/workout')
      .set('Cookie', `elevate_token=${validToken}`);

    expect(res.status).toBe(500);
    expect(res.body.success).toBe(false);
    expect(res.body.error.code).toBe('PYTHON_UPSTREAM_ERROR');
  });

  it('upstream 503 preserves status', async () => {
    axios.mockResolvedValueOnce({
      status: 503,
      headers: { 'content-type': 'application/json' },
      data: { error: 'Service Unavailable' },
    });

    const res = await request(app)
      .post('/api/python/workout')
      .set('Cookie', `elevate_token=${validToken}`);

    expect(res.status).toBe(503);
    expect(res.body.success).toBe(false);
    expect(res.body.error.code).toBe('PYTHON_UPSTREAM_ERROR');
  });

  it('connection failure returns JSON 503', async () => {
    axios.mockRejectedValueOnce({
      code: 'ECONNREFUSED',
      message: 'connect ECONNREFUSED',
    });

    const res = await request(app)
      .post('/api/python/workout')
      .set('Cookie', `elevate_token=${validToken}`);

    expect(res.status).toBe(503);
    expect(res.body.success).toBe(false);
    expect(res.body.error.code).toBe('PYTHON_UPSTREAM_ERROR');
  });

  it('valid upstream JSON object without success is passed through successfully', async () => {
    axios.mockResolvedValueOnce({
      status: 200,
      headers: { 'content-type': 'application/json' },
      data: { plan_id: '12345', custom_field: 'hello' },
    });

    const res = await request(app)
      .post('/api/python/workout')
      .set('Cookie', `elevate_token=${validToken}`);

    expect(res.status).toBe(200);
    expect(res.body).toEqual({ plan_id: '12345', custom_field: 'hello' });
  });

  it('valid upstream JSON array is passed through successfully', async () => {
    axios.mockResolvedValueOnce({
      status: 200,
      headers: { 'content-type': 'application/json' },
      data: [{ item: 'oats' }, { item: 'whey' }],
    });

    const res = await request(app)
      .post('/api/python/workout')
      .set('Cookie', `elevate_token=${validToken}`);

    expect(res.status).toBe(200);
    expect(res.body).toEqual([{ item: 'oats' }, { item: 'whey' }]);
  });

  it('upstream HTML 502 becomes Node JSON 502 with PYTHON_UPSTREAM_ERROR', async () => {
    axios.mockResolvedValueOnce({
      status: 502,
      headers: { 'content-type': 'text/html' },
      data: '<html>Bad Gateway</html>',
    });

    const res = await request(app)
      .post('/api/python/workout')
      .set('Cookie', `elevate_token=${validToken}`);

    expect(res.status).toBe(502);
    expect(res.body.success).toBe(false);
    expect(res.body.error.code).toBe('PYTHON_UPSTREAM_ERROR');
  });

  it('upstream empty body becomes Node JSON 502 with PYTHON_UPSTREAM_ERROR', async () => {
    axios.mockResolvedValueOnce({
      status: 502,
      headers: { 'content-type': 'application/json' },
      data: '',
    });

    const res = await request(app)
      .post('/api/python/workout')
      .set('Cookie', `elevate_token=${validToken}`);

    expect(res.status).toBe(502);
    expect(res.body.success).toBe(false);
    expect(res.body.error.code).toBe('PYTHON_UPSTREAM_ERROR');
  });
});
