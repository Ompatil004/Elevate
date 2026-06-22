import axios from 'axios';

// API service for profile updates with plan regeneration.
// Authenticated Python calls go through the Node proxy so the HttpOnly auth cookie
// is read by elevate-11 and forwarded to Python as x-auth-token server-side.
const NODE_API_BASE_URL = import.meta.env.VITE_API_URL || '/api';
const PYTHON_PROXY_BASE_URL = `${NODE_API_BASE_URL.replace(/\/+$/, "")}/python`;
const PUBLIC_PYTHON_API_URL = import.meta.env.VITE_PYTHON_API_URL || '';
const PROFILE_UPDATE_ENDPOINT = '/profile/update';

// Request timeout in milliseconds
const REQUEST_TIMEOUT = 15000;
const IS_DEV = import.meta.env.DEV;
const CSRF_SAFE_METHODS = new Set(['get', 'head', 'options']);
let _csrfToken = null;

const getCsrfToken = async () => {
  if (_csrfToken) return _csrfToken;
  try {
    const response = await axios.get(`${NODE_API_BASE_URL}/csrf-token`, { withCredentials: true });
    _csrfToken = response.data?.csrfToken || null;
  } catch {
    _csrfToken = null;
  }
  return _csrfToken;
};

const summarizeProfileForLog = (profileData) => {
  const payload = profileData && typeof profileData === 'object' ? profileData : {};
  return {
    fieldCount: Object.keys(payload).length,
    keys: Object.keys(payload).sort(),
  };
};

/**
 * Create axios instance with custom configuration
 */
const apiClient = axios.create({
  baseURL: PYTHON_PROXY_BASE_URL,
  timeout: REQUEST_TIMEOUT,
  withCredentials: true,
  headers: {
    'Content-Type': 'application/json',
  },
});

/**
 * Request interceptor
 */
apiClient.interceptors.request.use(
  async (config) => {
    if (!CSRF_SAFE_METHODS.has((config.method || 'get').toLowerCase())) {
      const csrf = await getCsrfToken();
      if (csrf) config.headers['x-csrf-token'] = csrf;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

/**
 * Response interceptor - Global error handling
 */
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    // Keep logs minimal to avoid leaking payloads or server internals in browser consoles.
    if (IS_DEV) {
      console.error('[API Interceptor] Error:', {
        message: error.message,
        status: error.response?.status,
        url: error.config?.url,
        method: error.config?.method,
      });
    }

    return Promise.reject(error);
  }
);

/**
 * Classify error types for better handling
 */
export const classifyError = (error) => {
  const errorInfo = {
    type: 'unknown',
    message: error.message || 'An unexpected error occurred',
    status: null,
    details: null,
    isRetryable: false,
  };

  // Network error (no response from server)
  if (!error.response) {
    if (error.code === 'ECONNABORTED' || error.message.includes('timeout')) {
      errorInfo.type = 'timeout';
      errorInfo.message = 'Request timed out. The backend is taking too long to respond.';
      errorInfo.isRetryable = true;
    } else if (error.code === 'ERR_NETWORK') {
      errorInfo.type = 'network';
      errorInfo.message = 'Network error. Cannot connect to backend server.';
    } else {
      errorInfo.type = 'connection';
      errorInfo.message = 'Cannot reach backend server at http://localhost:8000';
    }
    return errorInfo;
  }

  // HTTP error responses
  const status = error.response.status;
  errorInfo.status = status;
  errorInfo.details = error.response.data;

  switch (status) {
    case 400:
      errorInfo.type = 'validation';
      errorInfo.message = error.response.data?.detail?.message ||
        error.response.data?.detail?.error ||
        'Invalid request data';
      break;
    case 401:
      errorInfo.type = 'authentication';
      errorInfo.message = 'Authentication failed. Please log in again.';
      errorInfo.isRetryable = false;
      break;
    case 403:
      errorInfo.type = 'authorization';
      errorInfo.message = 'You do not have permission to perform this action.';
      break;
    case 404:
      errorInfo.type = 'not_found';
      errorInfo.message = 'Requested endpoint not found.';
      break;
    case 408:
      errorInfo.type = 'timeout';
      errorInfo.message = 'Request timeout.';
      errorInfo.isRetryable = true;
      break;
    case 429:
      errorInfo.type = 'rate_limit';
      errorInfo.message = 'Too many requests. Please try again later.';
      errorInfo.isRetryable = true;
      break;
    case 500:
      errorInfo.type = 'server';
      errorInfo.message = error.response.data?.detail?.message ||
        error.response.data?.detail ||
        'Internal server error';
      errorInfo.isRetryable = true;
      break;
    case 502:
    case 503:
    case 504:
      errorInfo.type = 'service_unavailable';
      errorInfo.message = 'Backend service temporarily unavailable.';
      errorInfo.isRetryable = true;
      break;
    default:
      errorInfo.type = 'http';
      errorInfo.message = `HTTP error ${status}`;
  }

  return errorInfo;
};

/**
 * Update user profile and regenerate workout/meal plans if needed
 * Uses the safe endpoint with graceful degradation
 */
export const updateProfileWithRegeneration = async (profileData, options = {}) => {
  const {
    timeout = REQUEST_TIMEOUT,
    retryCount = 0,
    onRetry,
  } = options;

  let lastError = null;

  for (let attempt = 0; attempt <= retryCount; attempt++) {
    try {
      if (IS_DEV) {
        console.log('🔄 [Profile API] Updating profile with regeneration:', summarizeProfileForLog(profileData));
        console.log('🔑 [Profile API] Auth mode: HttpOnly cookie (withCredentials)');
        console.log('🌐 [Profile API] Request URL:', `${PYTHON_PROXY_BASE_URL}${PROFILE_UPDATE_ENDPOINT}`);
      }

      // Health check before making the request (optional, can be disabled)
      if (attempt === 0 && PUBLIC_PYTHON_API_URL) {
        try {
          await axios.get(`${PUBLIC_PYTHON_API_URL}/health`, { timeout: 3000 });
          if (IS_DEV) {
            console.log('✅ [Profile API] Backend health check passed');
          }
        } catch (healthError) {
          if (IS_DEV) {
            console.warn('⚠️ [Profile API] Backend health check failed:', healthError.message);
          }
          // Continue anyway - backend might still respond
        }
      }

      // Retry delay (exponential backoff)
      if (attempt > 0) {
        const delay = Math.min(1000 * Math.pow(2, attempt - 1), 5000);
        if (IS_DEV) {
          console.log(`⏳ [Profile API] Retry attempt ${attempt}/${retryCount}, waiting ${delay}ms`);
        }
        await new Promise(resolve => setTimeout(resolve, delay));
        onRetry?.(attempt, delay);
      }

      // Make the request with timeout
      const controller = new AbortController();
      const timeoutId = setTimeout(() => controller.abort(), timeout);

      const response = await apiClient.put(PROFILE_UPDATE_ENDPOINT, profileData, {
        signal: controller.signal,
      });

      clearTimeout(timeoutId);
      if (IS_DEV) {
        console.log('✅ [Profile API] Request completed successfully');
      }

      // Log what was regenerated
      const data = response.data;
      if (data.profile_changes?.workout_regenerated) {
        if (IS_DEV) {
          console.log('🏋️ [Profile API] Workout plan regenerated and saved to DB');
        }
      }
      if (data.profile_changes?.nutrition_regenerated) {
        if (IS_DEV) {
          console.log('🥗 [Profile API] Nutrition plan regenerated and saved to DB');
        }
      }

      return data;
    } catch (error) {
      lastError = error;
      const errorInfo = classifyError(error);

      if (IS_DEV) {
        console.error('❌ [Profile API] Error:', {
          type: errorInfo.type,
          message: errorInfo.message,
          status: errorInfo.status,
          isRetryable: errorInfo.isRetryable,
        });
      }

      // Don't retry for certain error types
      if (!errorInfo.isRetryable) {
        if (IS_DEV) {
          console.error('❌ [Profile API] Non-retryable error, stopping retries');
        }
        break;
      }

      // If this was the last attempt, break and throw
      if (attempt >= retryCount) {
        if (IS_DEV) {
          console.error('❌ [Profile API] Max retry attempts reached');
        }
        break;
      }
    }
  }

  // All retries failed, throw formatted error
  const finalError = classifyError(lastError);
  const formattedError = new Error(finalError.message);
  formattedError.type = finalError.type;
  formattedError.status = finalError.status;
  formattedError.details = finalError.details;
  throw formattedError;
};

/**
 * Alternative endpoint for basic profile update (no regeneration)
 */
export const updateProfileBasic = async (profileData) => {
  try {
    if (IS_DEV) {
      console.log('🔄 [Profile API] Basic profile update:', summarizeProfileForLog(profileData));
    }

    const response = await apiClient.put(PROFILE_UPDATE_ENDPOINT, profileData, {
    });

    if (IS_DEV) {
      console.log('✅ [Profile API] Basic update completed');
    }
    return response.data;
  } catch (error) {
    const errorInfo = classifyError(error);
    if (IS_DEV) {
      console.error('❌ [Profile API] Basic update error:', {
        type: errorInfo.type,
        message: errorInfo.message,
        status: errorInfo.status,
      });
    }

    const formattedError = new Error(errorInfo.message);
    formattedError.type = errorInfo.type;
    formattedError.status = errorInfo.status;
    formattedError.details = errorInfo.details;
    throw formattedError;
  }
};

/**
 * Get available profile endpoints from backend
 */
export const getProfileEndpoints = async () => {
  if (!IS_DEV) {
    throw new Error('Endpoint discovery is available only in development mode');
  }

  try {
    if (!PUBLIC_PYTHON_API_URL) {
      throw new Error('Direct Python API URL is not configured');
    }
    const response = await axios.get(`${PUBLIC_PYTHON_API_URL}/openapi.json`, { timeout: 5000 });
    return response.data;
  } catch (error) {
    if (IS_DEV) {
      console.error('❌ [Profile API] Could not fetch API endpoints:', error.message);
    }
    throw new Error('Failed to fetch API endpoints');
  }
};

/**
 * Check backend health
 */
export const checkBackendHealth = async () => {
  try {
    const response = await axios.get(`${PUBLIC_PYTHON_API_URL}/health`, { timeout: 3000 });
    return {
      healthy: true,
      data: response.data,
    };
  } catch (error) {
    return {
      healthy: false,
      error: error.message,
    };
  }
};

export default {
  updateProfileWithRegeneration,
  updateProfileBasic,
  getProfileEndpoints,
  checkBackendHealth,
  classifyError,
};