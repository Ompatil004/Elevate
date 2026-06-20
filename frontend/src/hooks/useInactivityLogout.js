import { useEffect, useRef, useCallback } from 'react';

/**
 * Fires `onLogout` after `timeoutMs` of user inactivity.
 * Resets the timer on mouse movement, clicks, key presses, touch, or scroll.
 *
 * @param {() => void} onLogout   - Callback to invoke when the session expires.
 * @param {number}     timeoutMs  - Inactivity threshold in milliseconds. Default: 30 min.
 * @param {boolean}    enabled    - Pass `false` to disable (e.g. when user is not authenticated).
 */
const LAST_ACTIVE_KEY = 'elevate_last_active';

export function useInactivityLogout(onLogout, timeoutMs = 30 * 60 * 1000, enabled = true) {
  const onLogoutRef = useRef(onLogout);
  const intervalRef = useRef(null);
  const hasFiredRef = useRef(false);

  // Keep the callback ref up-to-date without restarting the effect
  useEffect(() => {
    onLogoutRef.current = onLogout;
  }, [onLogout]);

  const updateActivity = useCallback(() => {
    if (!enabled) return;
    try {
      const lastActiveStr = localStorage.getItem(LAST_ACTIVE_KEY);
      if (lastActiveStr) {
        const lastActive = parseInt(lastActiveStr, 10);
        if (Date.now() - lastActive >= timeoutMs) {
          // Time already expired! Don't reset, trigger logout.
          if (!hasFiredRef.current) {
            hasFiredRef.current = true;
            onLogoutRef.current?.();
          }
          return;
        }
      }
      localStorage.setItem(LAST_ACTIVE_KEY, Date.now().toString());
      hasFiredRef.current = false;
    } catch (e) {
      console.warn('LocalStorage quota exceeded or disabled, fallback to local tracking.', e);
    }
  }, [enabled, timeoutMs]);

  useEffect(() => {
    if (!enabled) return;

    // Initialize if not set
    if (!localStorage.getItem(LAST_ACTIVE_KEY)) {
      updateActivity();
    }

    const events = ['mousemove', 'mousedown', 'keydown', 'touchstart', 'scroll', 'wheel'];
    events.forEach((e) => window.addEventListener(e, updateActivity, { passive: true }));

    // Check periodically instead of using one long setTimeout
    // This is robust against browser tab sleeping/throttling
    intervalRef.current = setInterval(() => {
      const lastActiveStr = localStorage.getItem(LAST_ACTIVE_KEY);
      const lastActive = lastActiveStr ? parseInt(lastActiveStr, 10) : Date.now();
      
      if (Date.now() - lastActive >= timeoutMs) {
        if (!hasFiredRef.current) {
          hasFiredRef.current = true;
          onLogoutRef.current?.();
        }
      } else {
        // If user came back in another tab, reset the fired state
        hasFiredRef.current = false;
      }
    }, Math.min(10000, timeoutMs / 2)); // Check every 10s or less

    // Handle cross-tab activity synchronization
    const handleStorage = (e) => {
      if (e.key === LAST_ACTIVE_KEY) {
        const lastActive = parseInt(e.newValue, 10);
        if (Date.now() - lastActive < timeoutMs) {
            hasFiredRef.current = false;
        }
      }
    };
    window.addEventListener('storage', handleStorage);

    return () => {
      events.forEach((e) => window.removeEventListener(e, updateActivity));
      window.removeEventListener('storage', handleStorage);
      if (intervalRef.current) clearInterval(intervalRef.current);
    };
  }, [enabled, timeoutMs, updateActivity]);
}
