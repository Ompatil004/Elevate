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
function normalizePythonPath(path) {
  const cleanPath = path.replace(/^\/api\/python/, '');

  const routeMap = {
    '/nutrition': '/nutrition',
    '/weekly-plan': '/api/weekly-plan',
    '/api/weekly-plan': '/api/weekly-plan',
    '/week': '/api/weekly-plan',
    '/daily-log/week': '/api/daily-log/week',
    '/api/daily-log/week': '/api/daily-log/week',
    '/workout': '/workout',
    '/api/workout': '/workout',
    '/swap-meal': '/nutrition/swap',
    '/chat': '/chat',
  };

  return routeMap[cleanPath] || cleanPath;
}

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
    const resolvedPath = normalizePythonPath(req.path);
    const targetUrl = `${base}/${resolvedPath.replace(/^\/+/, '')}`;

    // 3. Build headers (throws 401 if token missing)
    const headers = buildForwardHeaders(req);

    // [python-proxy] structured logging (Phase 3)
    console.log(`[python-proxy] requestId=${reqId} method=${method} incoming=${req.path} resolved=${resolvedPath} upstream=${base}${resolvedPath}`);

    const response = await axios({
      method,
      url: targetUrl,
      headers,
      params: req.query,
      data: ['GET', 'HEAD'].includes(method) ? undefined : req.body,
      timeout: getProxyTimeoutMs(),
      validateStatus: () => true,
    });

    const contentType = response.headers?.['content-type'] || 'unknown';
    console.log(`[python-proxy] requestId=${reqId} upstreamStatus=${response.status} contentType=${contentType}`);

    // Parse and validate JSON safely with fallback parsing
    let isJson = false;
    let parsedData = null;
    const rawData = response.data;
    
    if (contentType.includes('json')) {
      if (typeof rawData === 'string' && rawData.trim() === '') {
        isJson = false;
      } else {
        isJson = true;
        parsedData = rawData;
      }
    } else if (typeof rawData === 'string') {
      if (rawData.trim() !== '') {
        try {
          parsedData = JSON.parse(rawData);
          isJson = true;
        } catch (e) {
          // Not valid JSON string
        }
      }
    } else if (rawData && typeof rawData === 'object') {
      isJson = true;
      parsedData = rawData;
    }

    if (!isJson) {
      console.error(`[python-proxy] [${reqId}] Upstream returned non-JSON/malformed response with status ${response.status}`);
      return res.status(502).json({
        success: false,
        error: {
          code: 'PYTHON_UPSTREAM_ERROR',
          message: 'AI service is temporarily unavailable',
          requestId: reqId
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
            details: parsedData,
          }
        });
      }

      if (response.status === 422) {
        let safeDetails = parsedData;
        if (parsedData && Array.isArray(parsedData.detail)) {
          safeDetails = {
            detail: parsedData.detail.map(d => {
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
          message: 'AI service is temporarily unavailable',
          requestId: reqId
        }
      });
    }

    res.setHeader('content-type', 'application/json');
    return res.status(response.status).json(parsedData);

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
    console.error(`[python-proxy] requestId=${reqId} networkError=${errCode} message="Request to Python failed"`);

    return res.status(503).json({
      success: false,
      error: {
        code: 'PYTHON_UPSTREAM_ERROR',
        message: 'AI service is temporarily unavailable',
        requestId: reqId
      }
    });
  }
});

module.exports = router;