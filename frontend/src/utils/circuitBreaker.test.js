import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { CircuitBreaker, CircuitOpenError, isServiceError, workoutCB, nutritionCB, backgroundCB } from './circuitBreaker';

describe('isServiceError', () => {
  it('identifies status >= 500 as service error', () => {
    const error = { response: { status: 502 } };
    expect(isServiceError(error)).toBe(true);
  });

  it('identifies network failures (no response) as service error', () => {
    const error = { message: 'Network Error' };
    expect(isServiceError(error)).toBe(true);
  });

  it('identifies timeout as service error', () => {
    const error = { code: 'ECONNABORTED' };
    expect(isServiceError(error)).toBe(true);
    
    const errorMsg = { message: 'timeout of 1000ms exceeded' };
    expect(isServiceError(errorMsg)).toBe(true);
  });

  it('excludes client-side 4xx errors', () => {
    const error = { response: { status: 400 } };
    expect(isServiceError(error)).toBe(false);

    const error401 = { response: { status: 401 } };
    expect(isServiceError(error401)).toBe(false);

    const error422 = { response: { status: 422 } };
    expect(isServiceError(error422)).toBe(false);
  });

  it('excludes cancellation and abort errors', () => {
    const errAbort = { name: 'AbortError' };
    expect(isServiceError(errAbort)).toBe(false);

    const errCancel = { name: 'CanceledError' };
    expect(isServiceError(errCancel)).toBe(false);
  });
});

describe('CircuitBreaker Class', () => {
  let cb;

  beforeEach(() => {
    vi.useFakeTimers();
    cb = new CircuitBreaker('test-cb', {
      failureThreshold: 3,
      failureWindowMs: 60000,
      baseCooldownMs: 8000,
      maxCooldownMs: 60000,
    });
  });

  afterEach(() => {
    vi.useRealTimers();
  });

  it('starts in CLOSED state', () => {
    expect(cb.state).toBe('CLOSED');
    expect(cb.isOpen).toBe(false);
  });

  it('does not open on transient or client-side failures', () => {
    cb.recordFailure({ response: { status: 400 } });
    expect(cb.state).toBe('CLOSED');
    expect(cb.failureCount).toBe(0);
  });

  it('opens after 3 service failures within window', () => {
    const serviceError = { response: { status: 500 } };
    cb.recordFailure(serviceError);
    cb.recordFailure(serviceError);
    expect(cb.state).toBe('CLOSED');

    cb.recordFailure(serviceError);
    expect(cb.state).toBe('OPEN');
    expect(cb.isOpen).toBe(true);
    expect(cb.retryAfterMs).toBeGreaterThan(0);
  });

  it('throws CircuitOpenError if requested when open', () => {
    const serviceError = { response: { status: 500 } };
    cb.recordFailure(serviceError);
    cb.recordFailure(serviceError);
    cb.recordFailure(serviceError);

    expect(() => cb.beforeRequest()).toThrow(CircuitOpenError);
  });

  it('expires failures outside the rolling window', () => {
    const serviceError = { response: { status: 500 } };
    cb.recordFailure(serviceError);
    cb.recordFailure(serviceError);

    // Advance time past the 60s failure window
    vi.advanceTimersByTime(61000);

    expect(cb.failureCount).toBe(0);

    cb.recordFailure(serviceError);
    expect(cb.state).toBe('CLOSED'); // shouldn't trip because previous 2 expired
  });

  it('allows probe request after cooldown and closes on success', () => {
    const serviceError = { response: { status: 500 } };
    cb.recordFailure(serviceError);
    cb.recordFailure(serviceError);
    cb.recordFailure(serviceError); // OPEN

    expect(cb.state).toBe('OPEN');

    // Advance past cooldown (8s)
    vi.advanceTimersByTime(8500);

    // Check beforeRequest allows the probe (moves to HALF_OPEN)
    cb.beforeRequest();
    expect(cb.state).toBe('HALF_OPEN');

    // Success closes it
    cb.recordSuccess();
    expect(cb.state).toBe('CLOSED');
    expect(cb.failureCount).toBe(0);
  });

  it('applies exponential backoff on consecutive half-open probe failures', () => {
    const serviceError = { response: { status: 500 } };
    
    // First trip
    cb.recordFailure(serviceError);
    cb.recordFailure(serviceError);
    cb.recordFailure(serviceError); 
    expect(cb.cooldownMs).toBe(8000);

    // Cooldown 1st time
    vi.advanceTimersByTime(8500);
    cb.beforeRequest(); // HALF_OPEN
    
    // Probe fails -> opens again with 16s cooldown
    cb.recordFailure(serviceError);
    expect(cb.state).toBe('OPEN');
    expect(cb.cooldownMs).toBe(16000);

    // Cooldown 2nd time
    vi.advanceTimersByTime(16500);
    cb.beforeRequest(); // HALF_OPEN
    cb.recordFailure(serviceError); // probe fails
    expect(cb.cooldownMs).toBe(32000);
  });

  it('resets backoff cooldown after a successful request', () => {
    const serviceError = { response: { status: 500 } };
    
    // Trip twice to get to 16s cooldown
    cb.recordFailure(serviceError);
    cb.recordFailure(serviceError);
    cb.recordFailure(serviceError);
    vi.advanceTimersByTime(8500);
    cb.beforeRequest();
    cb.recordFailure(serviceError);
    expect(cb.cooldownMs).toBe(16000);

    // Cooldown and succeed
    vi.advanceTimersByTime(16500);
    cb.beforeRequest();
    cb.recordSuccess();
    expect(cb.cooldownMs).toBe(8000);
  });
});

describe('Exported instances', () => {
  it('separate breakers do not interfere with each other', () => {
    const serviceError = { response: { status: 500 } };
    
    // Trip workoutCB
    workoutCB.recordFailure(serviceError);
    workoutCB.recordFailure(serviceError);
    workoutCB.recordFailure(serviceError);

    expect(workoutCB.isOpen).toBe(true);
    expect(nutritionCB.isOpen).toBe(false);
    expect(backgroundCB.isOpen).toBe(false);

    // Reset for safety
    workoutCB.reset();
  });
});

describe('Integration Scenarios', () => {
  beforeEach(() => {
    vi.useFakeTimers();
    workoutCB.reset();
    backgroundCB.reset();
  });

  afterEach(() => {
    vi.useRealTimers();
  });

  it('background warmup failures do not block manual generation requests', async () => {
    const serviceError = { response: { status: 503 } };
    
    // Background warmup fails 5 times (its threshold is 5)
    for (let i = 0; i < 5; i++) {
      backgroundCB.recordFailure(serviceError);
    }
    expect(backgroundCB.isOpen).toBe(true);

    // User manually generates a workout plan
    const mockRequestFn = vi.fn().mockResolvedValue({ data: { success: true, workout: [] } });
    
    // Should execute successfully without throwing CircuitOpenError
    const result = await workoutCB.execute(mockRequestFn);
    expect(result.data.success).toBe(true);
    expect(workoutCB.state).toBe('CLOSED');
  });

  it('workout and nutrition breakers are fully independent', async () => {
    const serviceError = { response: { status: 503 } };
    
    // Fail workout 3 times to open it
    for (let i = 0; i < 3; i++) {
      workoutCB.recordFailure(serviceError);
    }
    expect(workoutCB.isOpen).toBe(true);
    expect(nutritionCB.isOpen).toBe(false);

    // Nutrition request should still succeed
    const mockRequestFn = vi.fn().mockResolvedValue({ data: { success: true, nutrition: { weekly_plan: {} } } });
    const result = await nutritionCB.execute(mockRequestFn);
    expect(result.data.success).toBe(true);
  });

  it('recovery closes the breaker and allows subsequent requests', async () => {
    const serviceError = { response: { status: 503 } };
    
    // Workout fails 3 times and opens
    for (let i = 0; i < 3; i++) {
      workoutCB.recordFailure(serviceError);
    }
    expect(workoutCB.isOpen).toBe(true);

    // Try executing -> throws CircuitOpenError
    const badRequestFn = vi.fn().mockResolvedValue({ data: { success: true } });
    await expect(workoutCB.execute(badRequestFn)).rejects.toThrow(CircuitOpenError);

    // Advance cooldown
    vi.advanceTimersByTime(8500);

    // Probe succeeds
    const successRequestFn = vi.fn().mockResolvedValue({ data: { success: true } });
    const res = await workoutCB.execute(successRequestFn);
    expect(res.data.success).toBe(true);

    // Circuit is closed now
    expect(workoutCB.state).toBe('CLOSED');
    expect(workoutCB.isOpen).toBe(false);
    expect(workoutCB.retryAfterMs).toBe(0);

    // Subsequent normal request succeeds
    const nextRes = await workoutCB.execute(successRequestFn);
    expect(nextRes.data.success).toBe(true);
  });
});

