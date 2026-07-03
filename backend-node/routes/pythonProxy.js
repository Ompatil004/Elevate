const express = require('express');
const axios = require('axios');
const auth = require('../middleware/auth');

const router = express.Router();

const DEFAULT_PYTHON_URL = process.env.NODE_ENV === 'production'
  ? 'https://elevate-pybackend.onrender.com'
  : 'http://localhost:8000';

const getProxyTimeoutMs = () => {
  const value = Number(process.env.PYTHON_PROXY_TIMEOUT_MS || 120000);
  return Number.isFinite(value) && value > 0 ? value : 120000;
};

// Route mapping helper
const mapPythonPath = (suffix) => {
  const cleanPath = '/' + suffix.replace(/^\/+/, '');
  if (cleanPath === '/week' || cleanPath === '/weekly-plan') {
    return '/api/weekly-plan';
  }
  return cleanPath;
};

// Credential derivation helper
const buildForwardHeaders = (req) => {
  let token = null;

  const authHeader = req.headers.authorization || req.headers.Authorization;
  if (authHeader && authHeader.toLowerCase().startsWith('bearer ')) {
    token = authHeader.slice(7).trim();
  }

  if (!token) {
    const xAuthToken = req.headers['x-auth-token'] || req.header?.('x-auth-token');
    if (xAuthToken && xAuthToken.trim()) {
      token = xAuthToken.trim();
    }
  }

  if (!token && req.cookies?.elevate_token) {
    token = req.cookies.elevate_token.trim();
  }

  if (!token) {
    const error = new Error('Missing authorization token');
    error.statusCode = 401;
    throw error;
  }

  const headers = {
    Authorization: `Bearer ${token}`,
    'x-auth-token': token,
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
  const reqId = req.requestId || 'N/A';

  try {
    // 1. Safe base URL normalization & validation
    const configured = process.env.ML_API_URL
      || process.env.PYTHON_API_URL
      || process.env.PYTHON_BACKEND_URL
      || process.env.VITE_PYTHON_API_URL
      || DEFAULT_PYTHON_URL;
    const base = String(configured || '').trim().replace(/\/+$/, '');

    if (!base || !/^https?:\/\/.+/.test(base)) {
      console.error(`[python-proxy] [${reqId}] Invalid ML_API_URL configured: "${base}"`);
      return res.status(503).json({
        success: false,
        error: {
          code: 'PYTHON_SERVICE_NOT_CONFIGURED',
          message: 'AI plan service is temporarily unavailable.',
          request_id: reqId,
        }
      });
    }

    // 2. Build target URL
    const suffix = req.originalUrl.slice(req.baseUrl.length) || '/';
    const mappedPath = mapPythonPath(suffix);
    const targetUrl = `${base}/${mappedPath.replace(/^\/+/, '')}`;

    // 3. Build headers (throws 401 if token missing)
    const headers = buildForwardHeaders(req);

    console.log(`[python-proxy] [${reqId}] Proxying ${method} to Python path: ${mappedPath}`);

    const response = await axios({
      method,
      url: targetUrl,
      headers,
      data: ['GET', 'HEAD'].includes(method) ? undefined : req.body,
      timeout: getProxyTimeoutMs(),
      validateStatus: () => true,
    });

    console.log(`[python-proxy] [${reqId}] Python target responded with status: ${response.status}`);

    // Validate if upstream response is valid JSON
    const isJson = response.headers?.['content-type']?.includes('json');
    if (!isJson && response.status >= 400) {
      console.error(`[python-proxy] [${reqId}] Upstream returned non-JSON error page`);
      return res.status(502).json({
        success: false,
        error: {
          code: 'PYTHON_UPSTREAM_ERROR',
          message: 'AI service returned an invalid response.',
          request_id: reqId,
        }
      });
    }

    if (response.status >= 400) {
      if (response.status === 401) {
        return res.status(401).json({
          success: false,
          error: {
            code: 'AUTH_REQUIRED',
            message: 'Authentication failed with AI service',
            request_id: reqId,
            details: response.data,
          }
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
          success: false,
          error: {
            code: 'PYTHON_UPSTREAM_ERROR',
            message: 'Invalid request payload sent to AI service',
            request_id: reqId,
            details: safeDetails,
          }
        });
      }

      const is500 = response.status === 500;
      const is503 = response.status === 503;
      return res.status(is500 ? 500 : (is503 ? 503 : 502)).json({
        success: false,
        error: {
          code: 'PYTHON_UPSTREAM_ERROR',
          message: `AI service returned an error status: ${response.status}`,
          request_id: reqId,
          details: response.data,
        }
      });
    }

    const contentType = response.headers?.['content-type'];
    if (contentType) {
      res.setHeader('content-type', contentType);
    }
    return res.status(response.status).send(response.data);

  } catch (error) {
    if (error.statusCode === 401) {
      console.warn(`[python-proxy] [${reqId}] Proxy rejected: Missing authorization token`);
      return res.status(401).json({
        success: false,
        error: {
          code: 'AUTH_REQUIRED',
          message: error.message,
          request_id: reqId,
        }
      });
    }

    const errCode = error.code || error.message;
    console.error(`[python-proxy] [${reqId}] Request to Python failed. Error: ${errCode}`);

    return res.status(503).json({
      success: false,
      error: {
        code: 'PYTHON_UPSTREAM_UNAVAILABLE',
        message: 'AI service is currently unavailable. Please try again later.',
        request_id: reqId,
        details: errCode,
      }
    });
  }
});

module.exports = router;