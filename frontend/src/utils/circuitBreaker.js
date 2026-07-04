/**
 * ARCH-7: circuitBreaker.js
 *
 * Client-side circuit breaker for Python backend requests.
 * Protects the frontend from hammering an unreachable Python service.
 *
 * States:
 *   CLOSED    – normal operation, requests pass through
 *   OPEN      – service detected as down, requests fail fast
 *   HALF_OPEN – after cooldown, one probe request is allowed through
 *
 * Design:
 *   - Rolling failure window (default 60s) — old failures expire
 *   - Exponential backoff cooldown: 8s → 16s → 32s → 60s cap
 *   - Strict failure classification: only network errors, timeouts, 5xx
 *   - Separate instances per operation to isolate background warmups
 *   - Safe DEV-only diagnostics (never logs tokens/profiles/headers)
 */

const States = Object.freeze({
  CLOSED: 'CLOSED',
  OPEN: 'OPEN',
  HALF_OPEN: 'HALF_OPEN',
});

const DEFAULT_OPTIONS = {
  failureThreshold: 3,
  failureWindowMs: 60_000,
  baseCooldownMs: 8_000,
  maxCooldownMs: 60_000,
};

/**
 * Determine if an error represents a genuine backend service failure.
 * Only these should count toward opening the circuit:
 *   - Network failures with no HTTP response at all
 *   - Request timeout / ECONNABORTED
 *   - HTTP 500, 502, 503, 504
 *
 * These must NOT count:
 *   - HTTP 400, 401, 403, 404, 409, 422 (client errors / auth)
 *   - AbortError / CanceledError (user or component cancelled)
 *   - CircuitOpenError (our own preflight rejection)
 *   - Axios cancellation errors
 */
export function isServiceError(err) {
  if (!err) return false;

  // CircuitOpenError — our own class, never count
  if (err.isCircuitOpen) return false;

  // Cancellation / abort — user or component unmounted
  if (err.name === 'AbortError' || err.name === 'CanceledError') return false;
  if (err.code === 'ERR_CANCELED') return false;
  if (err.__CANCEL__) return false; // axios legacy cancel token

  // Timeout
  if (err.code === 'ECONNABORTED') return true;
  if (err.message && /timeout/i.test(err.message)) return true;

  // No HTTP response at all — network failure, DNS error, CORS block
  if (!err.response) return true;

  // HTTP status — only 5xx server errors
  const status = err.response?.status;
  if (status >= 500 && status <= 504) return true;

  // Everything else (4xx, etc.) is NOT a service failure
  return false;
}

export class CircuitBreaker {
  #state = States.CLOSED;
  #failureTimestamps = []; // rolling window of failure timestamps
  #openedAt = null;
  #consecutiveOpens = 0;   // for exponential backoff
  #currentCooldownMs;
  #name;
  #opts;

  constructor(name = 'default', options = {}) {
    this.#name = name;
    this.#opts = { ...DEFAULT_OPTIONS, ...options };
    this.#currentCooldownMs = this.#opts.baseCooldownMs;
  }

  // ── Public getters ──────────────────────────────────────────────────────

  get state() { return this.#state; }
  get isOpen() { return this.#state === States.OPEN; }
  get failureCount() { return this.#recentFailures().length; }
  get cooldownMs() { return this.#currentCooldownMs; }

  /** Milliseconds remaining before the breaker allows a probe. 0 if not OPEN. */
  get retryAfterMs() {
    if (this.#state !== States.OPEN || !this.#openedAt) return 0;
    const remaining = this.#currentCooldownMs - (Date.now() - this.#openedAt);
    return Math.max(0, remaining);
  }

  // ── Core API ────────────────────────────────────────────────────────────

  /**
   * Call before sending a request.
   * - CLOSED / HALF_OPEN: returns silently, request proceeds.
   * - OPEN + cooldown not elapsed: throws CircuitOpenError.
   * - OPEN + cooldown elapsed: transitions to HALF_OPEN, allows one probe.
   */
  beforeRequest() {
    if (this.#state === States.CLOSED || this.#state === States.HALF_OPEN) return;

    // State is OPEN
    const elapsed = Date.now() - this.#openedAt;
    if (elapsed < this.#currentCooldownMs) {
      const retryMs = this.#currentCooldownMs - elapsed;
      const err = new CircuitOpenError(
        `[CircuitBreaker:${this.#name}] Service unavailable. Retry in ${Math.ceil(retryMs / 1000)}s.`,
        retryMs,
      );
      if (import.meta.env.DEV) {
        console.warn(`[CB:${this.#name}] OPEN — blocking request. Retry in ${Math.ceil(retryMs / 1000)}s`);
      }
      throw err;
    }

    // Cooldown elapsed — transition to HALF_OPEN, allow one probe
    this.#state = States.HALF_OPEN;
    if (import.meta.env.DEV) {
      console.info(`[CB:${this.#name}] Cooldown elapsed → HALF_OPEN (allowing probe)`);
    }
  }

  /** Record a successful backend response. */
  recordSuccess() {
    const prevState = this.#state;
    this.#state = States.CLOSED;
    this.#failureTimestamps = [];
    this.#openedAt = null;
    this.#consecutiveOpens = 0;
    this.#currentCooldownMs = this.#opts.baseCooldownMs;

    if (import.meta.env.DEV && prevState !== States.CLOSED) {
      console.info(`[CB:${this.#name}] ${prevState} → CLOSED (success). Cooldown reset to ${this.#opts.baseCooldownMs}ms`);
    }
  }

  /** Wrapper function that executes an async task with this circuit breaker. */
  async execute(fn) {
    return withCircuitBreaker(this, fn);
  }

  /** Record a failed backend response/network error. */
  recordFailure(err) {
    // Strict classification — only genuine service errors count
    if (!isServiceError(err)) {
      if (import.meta.env.DEV) {
        const status = err?.response?.status || err?.name || 'unknown';
        console.log(`[CB:${this.#name}] Ignoring non-service error (${status}) — not counting`);
      }
      return;
    }

    const now = Date.now();
    this.#failureTimestamps.push(now);

    const recent = this.#recentFailures();
    this.#failureTimestamps = recent; // prune old entries

    if (import.meta.env.DEV) {
      const status = err?.response?.status || 'NETWORK_ERROR';
      console.warn(
        `[CB:${this.#name}] Service failure (${status}). ` +
        `Count: ${recent.length}/${this.#opts.failureThreshold} in rolling ${this.#opts.failureWindowMs / 1000}s window. ` +
        `State: ${this.#state}`
      );
    }

    // HALF_OPEN probe failed — re-open immediately with escalated cooldown
    if (this.#state === States.HALF_OPEN) {
      this.#openCircuit('half-open probe failed');
      return;
    }

    // CLOSED — check if threshold reached
    if (recent.length >= this.#opts.failureThreshold) {
      this.#openCircuit('threshold reached');
    }
  }

  /** Manually reset the circuit breaker (e.g., user-triggered retry). */
  reset() {
    this.#state = States.CLOSED;
    this.#failureTimestamps = [];
    this.#openedAt = null;
    this.#consecutiveOpens = 0;
    this.#currentCooldownMs = this.#opts.baseCooldownMs;
    if (import.meta.env.DEV) {
      console.info(`[CB:${this.#name}] Manual reset → CLOSED`);
    }
  }

  // ── Private helpers ─────────────────────────────────────────────────────

  #recentFailures() {
    const cutoff = Date.now() - this.#opts.failureWindowMs;
    return this.#failureTimestamps.filter(ts => ts > cutoff);
  }

  #openCircuit(reason) {
    this.#state = States.OPEN;
    this.#openedAt = Date.now();
    this.#consecutiveOpens++;

    // Exponential backoff: base * 2^(opens-1), capped at max
    this.#currentCooldownMs = Math.min(
      this.#opts.baseCooldownMs * Math.pow(2, this.#consecutiveOpens - 1),
      this.#opts.maxCooldownMs,
    );

    if (import.meta.env.DEV) {
      console.error(
        `[CB:${this.#name}] → OPEN (${reason}). ` +
        `Cooldown: ${this.#currentCooldownMs / 1000}s. ` +
        `Consecutive opens: ${this.#consecutiveOpens}`
      );
    }
  }
}

// ── CircuitOpenError ────────────────────────────────────────────────────────

export class CircuitOpenError extends Error {
  constructor(message, retryAfterMs = 0) {
    super(message);
    this.name = 'CircuitOpenError';
    this.isCircuitOpen = true;
    this.retryAfterMs = retryAfterMs;
  }
}

// ── Reusable wrapper ────────────────────────────────────────────────────────

/**
 * Execute an async request function through a circuit breaker.
 * Handles beforeRequest preflight, recordSuccess, and recordFailure.
 *
 * @param {CircuitBreaker} breaker
 * @param {() => Promise<any>} requestFn
 * @returns {Promise<any>}
 */
export async function withCircuitBreaker(breaker, requestFn) {
  breaker.beforeRequest();
  try {
    const response = await requestFn();
    breaker.recordSuccess();
    return response;
  } catch (error) {
    // Don't record CircuitOpenError as a failure (prevents recursive counting)
    if (!error?.isCircuitOpen) {
      breaker.recordFailure(error);
    }
    throw error;
  }
}

// ── Exported instances ──────────────────────────────────────────────────────
// Separate breakers so background warmup failures don't block user actions.

/** Circuit breaker for user-initiated workout generation. */
export const workoutCB = new CircuitBreaker('python-workout');

/** Circuit breaker for user-initiated nutrition generation. */
export const nutritionCB = new CircuitBreaker('python-nutrition');

/** Circuit breaker for background cache warmup requests (more lenient). */
export const backgroundCB = new CircuitBreaker('python-background', {
  failureThreshold: 5,
  baseCooldownMs: 15_000,
  maxCooldownMs: 60_000,
});

// Backward-compatible alias — consumers importing pythonBackendCB will
// get the workout breaker. Gradually migrate callers to specific breakers.
export const pythonBackendCB = workoutCB;
