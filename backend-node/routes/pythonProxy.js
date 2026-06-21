const express = require('express');
const axios = require('axios');
const auth = require('../middleware/auth');

const router = express.Router();

const DEFAULT_PYTHON_URL = process.env.NODE_ENV === 'production'
  ? 'https://elevate-pybackend.onrender.com'
  : 'http://localhost:8000';

const getPythonBaseUrl = () => {
  const configured = process.env.PYTHON_API_URL
    || process.env.PYTHON_BACKEND_URL
    || process.env.VITE_PYTHON_API_URL
    || DEFAULT_PYTHON_URL;
  const trimmed = String(configured || '').trim().replace(/\/+$/, '');
  if (!/^https?:\/\//i.test(trimmed)) {
    throw new Error('PYTHON_API_URL must be an absolute http(s) URL for the Node proxy');
  }
  return trimmed;
};

const getProxyTimeoutMs = () => {
  const value = Number(process.env.PYTHON_PROXY_TIMEOUT_MS || 120000);
  return Number.isFinite(value) && value > 0 ? value : 120000;
};

const buildTargetUrl = (req) => {
  const suffix = req.originalUrl.slice(req.baseUrl.length) || '/';
  return `${getPythonBaseUrl()}${suffix}`;
};

const buildForwardHeaders = (req) => {
  const headers = {
    accept: req.headers.accept || 'application/json',
    'x-auth-token': req.token || req.cookies?.elevate_token || req.header('x-auth-token'),
  };

  if (req.headers['content-type']) {
    headers['content-type'] = req.headers['content-type'];
  }
  if (req.requestId) {
    headers['x-request-id'] = req.requestId;
  } else if (req.headers['x-request-id']) {
    headers['x-request-id'] = req.headers['x-request-id'];
  }

  return headers;
};

router.use(auth, async (req, res) => {
  try {
    const method = req.method.toUpperCase();
    const response = await axios({
      method,
      url: buildTargetUrl(req),
      headers: buildForwardHeaders(req),
      data: ['GET', 'HEAD'].includes(method) ? undefined : req.body,
      timeout: getProxyTimeoutMs(),
      validateStatus: () => true,
    });

    const contentType = response.headers?.['content-type'];
    if (contentType) {
      res.setHeader('content-type', contentType);
    }

    return res.status(response.status).send(response.data);
  } catch (error) {
    if (process.env.NODE_ENV !== 'production') {
      console.error('[python-proxy] Request failed:', error.message);
    }
    return res.status(502).json({
      message: 'Python backend proxy failed',
      code: 'PYTHON_PROXY_FAILED',
    });
  }
});

module.exports = router;