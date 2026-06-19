"""
ARCH-7: circuit_breaker.py

Provides resilient retry + circuit-breaker decorators for all outbound
network calls in the Elevate Python backend (Gemini API, any future REST APIs).

Pattern: Tenacity-based exponential backoff + simple state-machine circuit breaker.

Usage
-----
    from app.circuit_breaker import with_retry, CircuitBreaker

    # 1. Simple retry with exponential backoff (no circuit breaker):
    @with_retry(max_attempts=3)
    def call_something():
        ...

    # 2. Full circuit breaker (opens after N consecutive failures):
    _cb = CircuitBreaker(failure_threshold=5, recovery_timeout=60)

    result = _cb.call(some_function, arg1, arg2)
"""

import time
import logging
import functools
from enum import Enum
from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    retry_if_exception_type,
    before_sleep_log,
)

logger = logging.getLogger(__name__)


# ──────────────────────────────────────────────────────────────────────────────
# Simple retry decorator (tenacity-backed)
# ──────────────────────────────────────────────────────────────────────────────

def with_retry(
    max_attempts: int = 3,
    min_wait: float = 1.0,   # seconds
    max_wait: float = 30.0,  # seconds
    reraise: bool = True,
    exceptions: tuple = (Exception,),
):
    """
    Decorator: retry the wrapped function with exponential backoff.

    Parameters
    ----------
    max_attempts : int
        Total number of attempts (including first try).
    min_wait : float
        Minimum wait between retries (seconds).
    max_wait : float
        Maximum wait between retries (seconds).
    reraise : bool
        If True (default) re-raise the last exception after exhausting attempts.
    exceptions : tuple[type, ...]
        Only retry on these exception types.
    """
    def decorator(fn):
        @functools.wraps(fn)
        def wrapper(*args, **kwargs):
            decorated = retry(
                stop=stop_after_attempt(max_attempts),
                wait=wait_exponential(multiplier=1, min=min_wait, max=max_wait),
                retry=retry_if_exception_type(exceptions),
                before_sleep=before_sleep_log(logger, logging.WARNING),
                reraise=reraise,
            )(fn)
            return decorated(*args, **kwargs)
        return wrapper
    return decorator


# ──────────────────────────────────────────────────────────────────────────────
# Full Circuit Breaker
# ──────────────────────────────────────────────────────────────────────────────

class _State(Enum):
    CLOSED  = "CLOSED"   # Normal — requests flow through
    OPEN    = "OPEN"     # Failing — requests are short-circuited
    HALF    = "HALF"     # Probing — one request let through to test recovery


class CircuitBreakerOpen(RuntimeError):
    """Raised when a call is attempted while the circuit breaker is OPEN."""


class CircuitBreaker:
    """
    Thread-safe (GIL-level) circuit breaker.

    States
    ------
    CLOSED  → normal operation; failure_count incremented on each failure.
    OPEN    → short-circuits calls; transitions to HALF after recovery_timeout.
    HALF    → allows one probe call; resets to CLOSED on success, OPEN on failure.

    Parameters
    ----------
    failure_threshold : int
        Number of consecutive failures before opening the circuit (default 5).
    recovery_timeout  : float
        Seconds to wait in OPEN before switching to HALF (default 60).
    name : str
        Human-readable label used in log messages.
    """

    def __init__(
        self,
        failure_threshold: int = 5,
        recovery_timeout: float = 60.0,
        name: str = "default",
    ):
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.name = name

        self._state = _State.CLOSED
        self._failure_count = 0
        self._last_failure_time: float = 0.0

    # ------------------------------------------------------------------
    # Public interface
    # ------------------------------------------------------------------

    @property
    def state(self) -> str:
        return self._state.value

    def call(self, fn, *args, **kwargs):
        """
        Execute *fn* through the circuit breaker.

        Raises
        ------
        CircuitBreakerOpen
            When the circuit is OPEN and the recovery timeout hasn't elapsed.
        """
        self._maybe_transition()

        if self._state is _State.OPEN:
            raise CircuitBreakerOpen(
                f"[CircuitBreaker:{self.name}] Circuit is OPEN — "
                f"calls are blocked for {self.recovery_timeout}s after "
                f"{self.failure_threshold} consecutive failures."
            )

        try:
            result = fn(*args, **kwargs)
            self._on_success()
            return result
        except Exception as exc:
            self._on_failure()
            raise

    # ------------------------------------------------------------------
    # Internal state machine
    # ------------------------------------------------------------------

    def _maybe_transition(self):
        if self._state is _State.OPEN:
            elapsed = time.monotonic() - self._last_failure_time
            if elapsed >= self.recovery_timeout:
                logger.info(
                    "[CircuitBreaker:%s] Transitioning OPEN → HALF after %.1fs",
                    self.name, elapsed,
                )
                self._state = _State.HALF

    def _on_success(self):
        if self._state is not _State.CLOSED:
            logger.info(
                "[CircuitBreaker:%s] Recovery probe succeeded — CLOSED",
                self.name,
            )
        self._state = _State.CLOSED
        self._failure_count = 0

    def _on_failure(self):
        self._failure_count += 1
        self._last_failure_time = time.monotonic()

        if self._state is _State.HALF or self._failure_count >= self.failure_threshold:
            logger.error(
                "[CircuitBreaker:%s] Tripped OPEN after %d failure(s)",
                self.name, self._failure_count,
            )
            self._state = _State.OPEN
        else:
            logger.warning(
                "[CircuitBreaker:%s] Failure %d/%d",
                self.name, self._failure_count, self.failure_threshold,
            )


# ──────────────────────────────────────────────────────────────────────────────
# Pre-built circuit breakers for Elevate external dependencies
# ──────────────────────────────────────────────────────────────────────────────

#: Circuit breaker for Gemini API calls (chatbot + workout config generation).
#: Opens after 5 consecutive failures; retries after 60 s.
gemini_cb = CircuitBreaker(failure_threshold=5, recovery_timeout=60, name="gemini")

#: Circuit breaker for any future external REST API calls.
external_api_cb = CircuitBreaker(failure_threshold=3, recovery_timeout=30, name="external_api")
