class DashboardSyncBridge {
  constructor() {
    this.listeners = new Map();
    this.storageKey = '_dashboardSyncBridge';

    if (typeof window !== 'undefined') {
      window.addEventListener('storage', (event) => {
        if (event.key !== this.storageKey) return;
        if (!event.newValue) return;

        try {
          const data = JSON.parse(event.newValue);
          if (data?.type) {
            this.notify(data.type, data.payload);
          }
        } catch (error) {
          console.warn('syncBridge storage parse error:', error);
        }
      });
    }
  }

  subscribe(type, callback) {
    if (!type || typeof callback !== 'function') {
      return () => {};
    }

    if (!this.listeners.has(type)) {
      this.listeners.set(type, new Set());
    }

    const callbacks = this.listeners.get(type);
    callbacks.add(callback);

    return () => {
      callbacks.delete(callback);
      if (callbacks.size === 0) {
        this.listeners.delete(type);
      }
    };
  }

  notify(type, payload) {
    const callbacks = this.listeners.get(type);
    if (!callbacks || callbacks.size === 0) return;
    callbacks.forEach((callback) => {
      try {
        callback(payload);
      } catch (error) {
        console.error('syncBridge subscriber error:', error);
      }
    });
  }

  emit(type, payload = {}) {
    const data = {
      type,
      payload,
      timestamp: Date.now(),
    };

    try {
      localStorage.setItem(this.storageKey, JSON.stringify(data));
    } catch (error) {
      console.warn('syncBridge emit storage error:', error);
    }

    this.notify(type, payload);
  }
}

export const syncBridge = new DashboardSyncBridge();

export const SyncTypes = {
  WATER_ADDED: 'water_added',
  SLEEP_UPDATED: 'sleep_updated',
  MEAL_COMPLETED: 'meal_completed',
  WORKOUT_PROGRESS: 'workout_progress',
  WORKOUT_COMPLETED: 'workout_completed',
};
