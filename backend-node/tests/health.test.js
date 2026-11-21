/**
 * Health and Readiness Endpoint Tests for Node.js API Gateway
 */

const request = require('supertest');
const mongoose = require('mongoose');
const app = require('../server');

describe('Node.js Health & Readiness Probes', () => {
  describe('GET /health (Liveness Probe)', () => {
    it('returns HTTP 200 with service information and ISO timestamp', async () => {
      const res = await request(app).get('/health');
      expect(res.status).toBe(200);
      expect(res.body).toHaveProperty('status', 'ok');
      expect(res.body).toHaveProperty('service', 'elevate-node');
      expect(res.body).toHaveProperty('timestamp');
      expect(new Date(res.body.timestamp).toISOString()).toBe(res.body.timestamp);
    });

    it('does not require authentication or CSRF tokens', async () => {
      const res = await request(app).get('/health');
      expect(res.status).not.toBe(401);
      expect(res.status).not.toBe(403);
    });

    it('does not leak secrets, URIs, or credentials', async () => {
      const res = await request(app).get('/health');
      const text = JSON.stringify(res.body);
      expect(text).not.toContain('mongodb');
      expect(text).not.toContain('password');
      expect(text).not.toContain('secret');
      expect(text).not.toContain('MONGO_URI');
    });

    it('supports alias /healthz and /api/health', async () => {
      const resZ = await request(app).get('/healthz');
      expect(resZ.status).toBe(200);
      expect(resZ.body.status).toBe('ok');

      const resApi = await request(app).get('/api/health');
      expect(resApi.status).toBe(200);
      expect(resApi.body.status).toBe('ok');
    });
  });

  describe('GET /ready (Readiness Probe)', () => {
    it('returns HTTP 200 when database connection is ready', async () => {
      // If mongoose is connected (in test harness or live environment)
      if (mongoose.connection && mongoose.connection.readyState === 1) {
        const res = await request(app).get('/ready');
        expect(res.status).toBe(200);
        expect(res.body).toHaveProperty('status', 'ready');
        expect(res.body.checks).toHaveProperty('database', 'connected');
      } else {
        const res = await request(app).get('/ready');
        expect([200, 503]).toContain(res.status);
      }
    });

    it('returns HTTP 503 when database is disconnected', async () => {
      const originalState = mongoose.connection.readyState;
      try {
        mongoose.connection.readyState = 0;
        const res = await request(app).get('/ready');
        expect(res.status).toBe(503);
        expect(res.body).toHaveProperty('status', 'not_ready');
        expect(res.body.checks).toHaveProperty('database', 'disconnected');
      } finally {
        mongoose.connection.readyState = originalState;
      }
    });

    it('does not leak database connection details or stack traces on error', async () => {
      const originalState = mongoose.connection.readyState;
      try {
        mongoose.connection.readyState = 0;
        const res = await request(app).get('/ready');
        const text = JSON.stringify(res.body);
        expect(text).not.toContain('mongodb');
        expect(text).not.toContain('cluster');
        expect(text).not.toContain('Error:');
      } finally {
        mongoose.connection.readyState = originalState;
      }
    });

    it('supports alias /readyz and /api/ready', async () => {
      const resZ = await request(app).get('/readyz');
      expect([200, 503]).toContain(resZ.status);

      const resApi = await request(app).get('/api/ready');
      expect([200, 503]).toContain(resApi.status);
    });
  });
});
