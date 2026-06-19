/* eslint-disable react-refresh/only-export-components */
import React, { createContext, useContext, useState, useCallback, useRef, useEffect } from 'react';

const NotificationContext = createContext();
const MAX_NOTIFICATIONS = 5;

export const useNotification = () => {
  const context = useContext(NotificationContext);
  if (!context) {
    throw new Error('useNotification must be used within a NotificationProvider');
  }
  return context;
};

export const NotificationProvider = ({ children }) => {
  const [notifications, setNotifications] = useState([]);
  // Bug #35 fixed: track all active timer IDs so they can be cancelled on unmount
  const timerMapRef = useRef({});

  // Clean up all pending timers when the provider unmounts
  useEffect(() => {
    const timerMap = timerMapRef.current;
    return () => {
      Object.values(timerMap).forEach(clearTimeout);
    };
  }, []);

  const showNotification = useCallback((message, type = 'info', duration = 4000) => {
    const id = Date.now() + Math.random();
    const notification = {
      id,
      message,
      type, // 'info', 'success', 'warning', 'error'
    };

    setNotifications(prev => {
      // Keep notification stack bounded to avoid viewport overflow.
      if (prev.length >= MAX_NOTIFICATIONS) {
        const overflow = prev.length - MAX_NOTIFICATIONS + 1;
        const dropped = prev.slice(0, overflow);
        dropped.forEach((n) => {
          if (timerMapRef.current[n.id]) {
            clearTimeout(timerMapRef.current[n.id]);
            delete timerMapRef.current[n.id];
          }
        });
        return [...prev.slice(overflow), notification];
      }
      return [...prev, notification];
    });

    // Bug #35 fixed: store timer ID so we can cancel it on early dismiss or unmount
    const timerId = setTimeout(() => {
      setNotifications(prev => prev.filter(n => n.id !== id));
      delete timerMapRef.current[id];
    }, duration);
    timerMapRef.current[id] = timerId;
  }, []);

  const showError = useCallback((message, duration = 5000) => {
    showNotification(message, 'error', duration);
  }, [showNotification]);

  const showSuccess = useCallback((message, duration = 4000) => {
    showNotification(message, 'success', duration);
  }, [showNotification]);

  const showWarning = useCallback((message, duration = 4000) => {
    showNotification(message, 'warning', duration);
  }, [showNotification]);

  const showInfo = useCallback((message, duration = 4000) => {
    showNotification(message, 'info', duration);
  }, [showNotification]);

  const removeNotification = useCallback((id) => {
    // Bug #35 fixed: cancel the pending auto-remove timer when manually dismissed
    if (timerMapRef.current[id]) {
      clearTimeout(timerMapRef.current[id]);
      delete timerMapRef.current[id];
    }
    setNotifications(prev => prev.filter(n => n.id !== id));
  }, []);

  return (
    <NotificationContext.Provider
      value={{
        notifications,
        showNotification,
        showError,
        showSuccess,
        showWarning,
        showInfo,
        removeNotification,
      }}
    >
      {children}
      <NotificationList notifications={notifications} removeNotification={removeNotification} />
    </NotificationContext.Provider>
  );
};

const NotificationList = ({ notifications, removeNotification }) => {
  return (
    <div className="notification-container">
      {notifications.map((notification) => (
        <NotificationItem
          key={notification.id}
          notification={notification}
          onClose={() => removeNotification(notification.id)}
        />
      ))}
    </div>
  );
};

const NotificationItem = ({ notification, onClose }) => {
  const getNotificationStyles = () => {
    switch (notification.type) {
      case 'success':
        return {
          background: 'linear-gradient(135deg, #166534 0%, #22c55e 100%)',
          border: '1px solid #22c55e',
          color: '#fff',
        };
      case 'error':
        return {
          background: 'linear-gradient(135deg, #7f1d1d 0%, #ef4444 100%)',
          border: '1px solid #ef4444',
          color: '#fff',
        };
      case 'warning':
        return {
          background: 'linear-gradient(135deg, #92400e 0%, #f59e0b 100%)',
          border: '1px solid #f59e0b',
          color: '#fff',
        };
      case 'info':
      default:
        return {
          background: 'linear-gradient(135deg, #1e40af 0%, #3b82f6 100%)',
          border: '1px solid #3b82f6',
          color: '#fff',
        };
    }
  };

  return (
    <div className="notification-item" style={getNotificationStyles()}>
      <div className="notification-content">
        <span className="notification-message">{notification.message}</span>
        <button className="notification-close" onClick={onClose}>
          ✕
        </button>
      </div>
    </div>
  );
};