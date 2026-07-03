const express = require('express');
const axios = require('axios');
const auth = require('../middleware/auth');

const router = express.Router();

const DEFAULT_PYTHON_URL = process.env.NODE_ENV === 'production'
  ? 'https://elevate-pybackend.onrender.com'
  : 'http://localhost:8000';

const getPythonBaseUrl = () => {
  const configured = process.env.ML_API_URL
    || process.env.PYTHON_API_URL
    || process.env.PYTHON_BACKEND_URL
    || process.env.VITE_PYTHON_API_URL
    || DEFAULT_PYTHON_URL;
  const trimmed = String(configured || '').trim().replace(/\/+$/, '');
  if (!/^https?:\/\//i.test(trimmed)) {
    throw new Error('ML_API_URL must be an absolute http(s) URL for the Node proxy');
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
  const incomingAuthorization = req.headers.authorization;
  const legacyToken = req.headers['x-auth-token'] || req.cookies?.elevate_token || req.header('x-auth-token');

  const authorization = incomingAuthorization ||
    (legacyToken ? `Bearer ${legacyToken}` : null);

  if (!authorization) {
    const error = new Error('Missing authorization token');
    error.statusCode = 401;
    throw error;
  }

  const headers = {
    Authorization: authorization,
    'x-auth-token': legacyToken || '',
    accept: req.headers.accept || 'application/json',
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
  const method = req.method.toUpperCase();
  const url = buildTargetUrl(req);
  const reqId = req.requestId || 'N/A';

  try {
    const headers = buildForwardHeaders(req);

    // Safe logging - target path only, no secrets
    console.log(`[python-proxy] [${reqId}] Proxying ${method} to Python path: ${req.path}`);

    const response = await axios({
      method,
      url,
      headers,
      data: ['GET', 'HEAD'].includes(method) ? undefined : req.body,
      timeout: getProxyTimeoutMs(),
      validateStatus: () => true,
    });

    console.log(`[python-proxy] [${reqId}] Python target responded with status: ${response.status}`);

    const contentType = response.headers?.['content-type'];
    if (contentType) {
      res.setHeader('content-type', contentType);
    }

    if (response.status === 401) {
      return res.status(401).json({
        message: 'Authentication failed with AI service',
        error: 'Unauthorized',
        details: response.data,
      });
    }

    if (response.status === 422) {
      let safeDetails = response.data;
      if (response.data && Array.isArray(response.data.detail)) {
        safeDetails = {
          detail: response.data.detail.map(d => {
            if (d && typeof d === 'object') {
              const { input, ...rest } = d;
              return rest;
            }
            return d;
          })
        };
      }
      return res.status(422).json({
        message: 'Invalid request payload sent to AI service',
        error: 'Unprocessable Entity',
        details: safeDetails,
      });
    }

    return res.status(response.status).send(response.data);
  } catch (error) {
    if (error.statusCode === 401) {
      console.warn(`[python-proxy] [${reqId}] Proxy rejected: Missing authorization token`);
      return res.status(401).json({
        message: error.message,
        error: 'Unauthorized',
      });
    }

    const errCode = error.code || error.message;
    console.error(`[python-proxy] [${reqId}] Request to Python path ${req.path} failed. Error: ${errCode}`);

    return res.status(503).json({
      message: 'AI service is currently unavailable. Please try again later.',
      code: 'PYTHON_PROXY_FAILED',
      details: errCode,
    });
  }
});

module.exports = router;