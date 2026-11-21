import axios from 'axios';

// ===== API CONFIGURATION =====
const VITE_API_URL = import.meta.env.VITE_API_URL || '/api';
const PYTHON_PROXY_API_URL = `${VITE_API_URL.replace(/\/+$/, '')}/python`;

export const API_BASE_URL = VITE_API_URL;
export const PYTHON_API_URL = PYTHON_PROXY_API_URL;

// SEC-12: Cache the CSRF token after first fetch.
let _csrfToken = null;
export const getCsrfToken = async () => {
  if (_csrfToken) return _csrfToken;
  try {
    const res = await axios.get(`${VITE_API_URL}/csrf-token`, { withCredentials: true });
    _csrfToken = res.data.csrfToken;
  } catch {
    _csrfToken = null;
  }
  return _csrfToken;
};

// Call on startup
getCsrfToken();

export const resetCsrfCache = () => {
  _csrfToken = null;
};

// Create axios instance for AUTH & Node.js endpoints
export const AuthAPI = axios.create({
  baseURL: VITE_API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 15000,
  withCredentials: true,
});

// Create axios instance for protected WORKOUT/NUTRITION endpoints via Node proxy
export const FitnessAPI = axios.create({
  baseURL: PYTHON_PROXY_API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 60000,
  withCredentials: true,
});

// Mutating methods require CSRF token
const MUTATING_METHODS = new Set(['post', 'put', 'delete', 'patch']);

const attachCsrfInterceptor = (instance) => {
  instance.interceptors.request.use(async (config) => {
    const method = (config.method || 'get').toLowerCase();
    if (MUTATING_METHODS.has(method)) {
      const token = await getCsrfToken();
      if (token) {
        config.headers['x-csrf-token'] = token;
      }
    }
    return config;
  }, (error) => Promise.reject(error));
};

attachCsrfInterceptor(AuthAPI);
attachCsrfInterceptor(FitnessAPI);

export default AuthAPI;
