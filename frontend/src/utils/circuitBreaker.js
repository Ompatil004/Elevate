/**
 * ARCH-7: circuitBreaker.js
 *
 * Lightweight client-side circuit breaker for FitnessAPI (Python backend).
 * Protects the frontend from hammering an unreachable Python service.
 *
 * States:
 *   CLOSED  – normal operation, requests pass through
 *   OPEN    – service detected as down, requests fail fast
 *   HALF    – after cooldown, one probe request is allowed through
 *
 * Configuration is intentionally conservative:
 *   - Opens after 3 consecutive failures
 *   - Stays open for 30 seconds before probing
 *   - Resets on any successful response
 */

const FAILURE_THRESHOLD = 3;    // consecutive failures before OPEN
const COOLDOWN_MS       = 30_000; // time to stay OPEN before probing again

const States = Object.freeze({ CLOSED: 'CLOSED', OPEN: 'OPEN', HALF: 'HALF' });

export class CircuitBreaker {
  #state       = States.CLOSED;
  #failures    = 0;
  #openedAt    = null;
  #name;

  constructor(name = 'default') {
    this.#name = name;
  }

  get state() { return this.#state; }
  get isOpen() { return this.#state === States.OPEN; }

  /**
   * Check whether a request is allowed right now.
   * - If OPEN and cooldown not elapsed: throw CircuitOpenError.
   * - If OPEN and cooldown elapsed: transition to HALF and allow one probe.
   */
  beforeRequest() {
    if (this.#state !== States.OPEN) return;

    const elapsed = Date.now() - this.#openedAt;
    if (elapsed < COOLDOWN_MS) {
      throw new CircuitOpenError(
        `[CircuitBreaker:${this.#name}] Service unavailable. Retry in ${Math.ceil((COOLDOWN_MS - elapsed) / 1000)}s.`
      );
    }

    // Cooldown elapsed — allow one probe request.
    this.#state = States.HALF;
  }

  /** Record a successful backend response. */
  recordSuccess() {
    this.#onSuccess();
  }

  /** Record a failed backend response/network error. */
  recordFailure(err) {
    this.#onFailure(err);
  }

  /**
   * Wrap an async axios call. Throws a CircuitOpenError immediately if OPEN.
   * Records success/failure and transitions state accordingly.
   *
   * @param {() => Promise<any>} fn - Async function that calls the backend
   * @returns {Promise<any>}
   */
  async execute(fn) {
    this.beforeRequest();

    try {
      const result = await fn();
      this.recordSuccess();
      return result;
    } catch (err) {
      this.recordFailure(err);
      throw err;
    }
  }

  #onSuccess() {
    if (this.#state !== States.CLOSED) {
      if (import.meta.env.DEV) {
        console.info(`[CircuitBreaker:${this.#name}] Probe succeeded — CLOSED`);
      }
    }
    this.#state    = States.CLOSED;
    this.#failures = 0;
    this.#openedAt = null;
  }

  #onFailure(err) {
    // Network errors, timeouts, and 5xx responses count as failures.
    // 4xx client errors (bad input) do NOT count.
    const isServiceError = !err?.response || (err?.response?.status ?? 0) >= 500;
    if (!isServiceError) return;

    this.#failures++;
    if (import.meta.env.DEV) {
      console.warn(`[CircuitBreaker:${this.#name}] Failure ${this.#failures}/${FAILURE_THRESHOLD}`);
    }

    if (this.#failures >= FAILURE_THRESHOLD || this.#state === States.HALF) {
      this.#state    = States.OPEN;
      this.#openedAt = Date.now();
      if (import.meta.env.DEV) {
        console.error(`[CircuitBreaker:${this.#name}] OPEN — blocking requests for ${COOLDOWN_MS / 1000}s`);
      }
    }
  }

  /** Manually reset (e.g. after a user-triggered retry) */
  reset() {
    this.#state    = States.CLOSED;
    this.#failures = 0;
    this.#openedAt = null;
  }
}

export class CircuitOpenError extends Error {
  constructor(message) {
    super(message);
    this.name = 'CircuitOpenError';
    this.isCircuitOpen = true;
  }
}

// Singleton for the Python backend
export const pythonBackendCB = new CircuitBreaker('python-backend');
