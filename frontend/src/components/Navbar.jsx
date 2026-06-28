/**
 * Shared Navbar component — Responsive Refactor.
 *
 * Props
 * ─────
 *  navigate      (fn)     — react-router-dom navigate function
 *  activePage    (str)    — 'dashboard' | 'workout' | 'nutrition' | 'chatbot'
 *  onLogout      (fn)     — called when user clicks Logout
 *  rightContent  (node)   — optional extra icon buttons to insert before Logout
 */
import React, { useState, useEffect, useRef } from 'react';
import { getFromStorage, setToStorage } from '../utils/storage';

const getStyles = (isDark) => ({
  navbar: {
    display: 'flex',
    alignItems: 'center',
    padding: '0 clamp(12px, 4vw, 40px)',
    height: 'clamp(64px, 9vw, 80px)',
    gap: 'clamp(8px, 2vw, 18px)',
    borderBottom: isDark ? '1px solid rgba(255,255,255,0.08)' : '1px solid rgba(0,0,0,0.08)',
    background: isDark ? 'rgba(9, 9, 11, 0.6)' : 'rgba(240,240,248,0.82)',
    backdropFilter: 'blur(16px)',
    position: 'fixed',
    top: 0,
    left: 0,
    right: 0,
    zIndex: 1000,
  },
  brand: {
    flex: 1,
    display: 'flex',
    alignItems: 'center',
    gap: '10px',
    cursor: 'pointer',
    userSelect: 'none',
  },
  brandText: {
    display: 'inline-block',
    fontSize: 'clamp(18px, 2.8vw, 22px)',
    fontWeight: '900',
    letterSpacing: '-1px',
    background: isDark ? 'linear-gradient(to right, #fff, #a5b4fc)' : 'linear-gradient(to right, #18181b, #4f46e5)',
    WebkitBackgroundClip: 'text',
    WebkitTextFillColor: 'transparent',
  },
  brandDot: {
    width: '8px',
    height: '8px',
    background: '#6366f1',
    borderRadius: '50%',
    boxShadow: '0 0 15px #6366f1',
    flexShrink: 0,
  },
  navCenter: {
    display: 'flex',
    gap: 'clamp(4px, 1.5vw, 8px)',
    height: '100%',
    alignItems: 'center',
    justifyContent: 'center',
  },
  navLink: {
    display: 'flex',
    alignItems: 'center',
    padding: '8px clamp(10px, 2vw, 20px)',
    fontSize: 'clamp(11px, 1.7vw, 13px)',
    fontWeight: '600',
    color: isDark ? '#a1a1aa' : '#52525b',
    cursor: 'pointer',
    borderRadius: '20px',
    transition: 'all 0.2s',
    textTransform: 'uppercase',
    letterSpacing: '0.5px',
    border: '1px solid transparent',
    userSelect: 'none',
  },
  navLinkActive: {
    background: isDark ? 'rgba(255,255,255,0.1)' : 'rgba(0,0,0,0.05)',
    color: isDark ? '#fff' : '#18181b',
    boxShadow: isDark ? '0 0 20px rgba(255,255,255,0.05)' : 'none',
    border: isDark ? '1px solid rgba(255,255,255,0.05)' : '1px solid rgba(0,0,0,0.05)',
  },
  navRight: {
    flex: 1,
    display: 'flex',
    alignItems: 'center',
    gap: 'clamp(8px, 2vw, 24px)',
    justifyContent: 'flex-end',
  },
  logoutBtn: {
    display: 'flex',
    alignItems: 'center',
    gap: '8px',
    padding: '0 clamp(10px, 2vw, 20px)',
    borderRadius: '12px',
    background: 'rgba(239, 68, 68, 0.1)',
    border: '1px solid rgba(239, 68, 68, 0.2)',
    color: '#ef4444',
    cursor: 'pointer',
    transition: 'all 0.2s ease',
    height: 'clamp(36px, 6vw, 42px)',
  },
  iconButton: {
    width: 'clamp(36px, 6vw, 42px)',
    height: 'clamp(36px, 6vw, 42px)',
    borderRadius: '12px',
    background: isDark ? 'rgba(255,255,255,0.05)' : 'rgba(0,0,0,0.04)',
    border: isDark ? '1px solid rgba(255,255,255,0.08)' : '1px solid rgba(0,0,0,0.08)',
    color: isDark ? '#fff' : '#18181b',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    cursor: 'pointer',
    fontSize: '18px',
    transition: 'all 0.2s',
    position: 'relative'
  },
  notifDropdown: {
    position: 'absolute',
    top: '60px',
    right: '0px',
    width: 'min(92vw, 340px)',
    background: isDark ? 'rgba(24,24,27,0.95)' : '#fff',
    border: isDark ? '1px solid rgba(255,255,255,0.08)' : '1px solid rgba(0,0,0,0.08)',
    borderRadius: '16px',
    padding: '16px',
    zIndex: 2000,
    boxShadow: '0 20px 50px rgba(0,0,0,0.5)',
    animation: 'slideDown 0.2s ease-out'
  },
  notifItem: {
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'space-between',
    padding: '10px 0',
    borderBottom: isDark ? '1px solid rgba(255,255,255,0.08)' : '1px solid rgba(0,0,0,0.08)',
    fontSize: '13px',
    color: isDark ? '#e4e4e7' : '#18181b'
  },
  logoutText: {
    fontSize: '12px',
    fontWeight: '700',
    letterSpacing: '0.5px',
    textTransform: 'uppercase',
  },
});

const responsiveNavbarStyles = `
  @keyframes slideDown { from { opacity: 0; transform: translateY(-20px); } to { opacity: 1; transform: translateY(0); } }
  .desktop-nav { display: flex; }
  .mobile-menu-btn { display: none; }
  .mobile-drawer {
    position: fixed;
    top: 0;
    right: -100%;
    width: 250px;
    height: 100dvh;
    background: rgba(9, 9, 11, 0.95);
    backdrop-filter: blur(20px);
    border-left: 1px solid rgba(255,255,255,0.08);
    z-index: 2000;
    transition: right 0.3s ease;
    display: flex;
    flex-direction: column;
    padding: 80px 20px 20px;
    box-shadow: -10px 0 30px rgba(0,0,0,0.5);
  }
  .mobile-drawer.open {
    right: 0;
  }
  .drawer-overlay {
    position: fixed;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    background: rgba(0,0,0,0.5);
    z-index: 1999;
    opacity: 0;
    pointer-events: none;
    transition: opacity 0.3s ease;
  }
  .drawer-overlay.open {
    opacity: 1;
    pointer-events: auto;
  }
  .hamburger {
    width: 24px;
    height: 20px;
    position: relative;
    cursor: pointer;
    display: flex;
    flex-direction: column;
    justify-content: space-between;
    z-index: 2001; /* Above the drawer */
  }
  .hamburger span {
    display: block;
    height: 2px;
    width: 100%;
    background: #fff;
    border-radius: 2px;
    transition: all 0.3s ease;
  }
  .hamburger.open span:nth-child(1) {
    transform: translateY(9px) rotate(45deg);
  }
  .hamburger.open span:nth-child(2) {
    opacity: 0;
  }
  .hamburger.open span:nth-child(3) {
    transform: translateY(-9px) rotate(-45deg);
  }
  
  @media (max-width: 850px) {
    .desktop-nav { display: none !important; }
    .mobile-menu-btn { display: flex; align-items: center; justify-content: center; width: 40px; height: 40px; }
  }
`;

const NAV_ITEMS = [
  { key: 'dashboard',  label: 'Dashboard',  path: '/dashboard'  },
  { key: 'workout',    label: 'Workout',    path: '/workout'    },
  { key: 'nutrition',  label: 'Nutrition',  path: '/nutrition'  },
  { key: 'chatbot',    label: 'ChatBot',    path: '/chatbot'    },
];

export default function Navbar({ navigate, activePage, onLogout, rightContent, isDark = true }) {
  const s = getStyles(isDark);
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);
  const [showNotif, setShowNotif] = useState(false);
  const [notifications, setNotifications] = useState(() => getFromStorage('active_notifications', []));
  const notifRef = useRef(null);

  // Sync notifications with localStorage
  useEffect(() => {
    const syncNotifs = () => {
      setNotifications(getFromStorage('active_notifications', []));
    };
    syncNotifs();
    window.addEventListener('storage', syncNotifs);
    const interval = setInterval(syncNotifs, 2000);
    return () => {
      window.removeEventListener('storage', syncNotifs);
      clearInterval(interval);
    };
  }, []);

  // Dismiss notification
  const dismissNotification = (id) => {
    const updated = notifications.filter((n) => n.id !== id);
    setNotifications(updated);
    setToStorage('active_notifications', updated);
  };

  // Close notifications dropdown on click outside
  useEffect(() => {
    const handleClickOutside = (event) => {
      if (notifRef.current && !notifRef.current.contains(event.target)) {
        setShowNotif(false);
      }
    };
    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  // Close menu when clicking escape
  useEffect(() => {
    const handleEsc = (e) => {
      if (e.key === 'Escape') setIsMobileMenuOpen(false);
    };
    window.addEventListener('keydown', handleEsc);
    return () => window.removeEventListener('keydown', handleEsc);
  }, []);

  // Prevent background scrolling when menu is open
  useEffect(() => {
    if (isMobileMenuOpen) {
      document.body.style.overflow = 'hidden';
    } else {
      document.body.style.overflow = '';
    }
    return () => {
      document.body.style.overflow = '';
    };
  }, [isMobileMenuOpen]);

  const toggleMenu = () => setIsMobileMenuOpen(!isMobileMenuOpen);
  const closeMenu = () => setIsMobileMenuOpen(false);

  const handleNavClick = (path, isActive) => {
    if (!isActive) navigate(path);
    closeMenu();
  };

  return (
    <>
      <style>{responsiveNavbarStyles}</style>
      <div style={s.navbar}>
        {/* Brand */}
        <div
          style={s.brand}
          onClick={() => navigate('/dashboard')}
          role="button"
          tabIndex={0}
          onKeyDown={(e) => {
            if (e.key === 'Enter' || e.key === ' ') {
              e.preventDefault();
              navigate('/dashboard');
            }
          }}
        >
          <div style={s.brandDot} />
          <span style={s.brandText}>ELEVATE</span>
        </div>

        {/* Centre nav links (Desktop) */}
        <div style={s.navCenter} className="desktop-nav">
          {NAV_ITEMS.map(({ key, label, path }) => {
            const isActive = activePage === key;
            return (
              <button
                key={key}
                type="button"
                className="nav-item"
                style={isActive ? { ...s.navLink, ...s.navLinkActive } : s.navLink}
                onClick={() => handleNavClick(path, isActive)}
                aria-current={isActive ? 'page' : undefined}
                aria-label={label}
                disabled={isActive}
              >
                {label}
              </button>
            );
          })}
        </div>

        {/* Right-side controls */}
        <div style={s.navRight}>
          {/* Bell Icon & Notifications Dropdown */}
          <div style={{ position: 'relative' }} ref={notifRef}>
            <button
              style={s.iconButton}
              className="icon-hover"
              onClick={() => setShowNotif(!showNotif)}
              title="Notifications"
            >
              🔔
              {notifications.length > 0 && (
                <span style={{
                  position: 'absolute',
                  top: '-4px',
                  right: '-4px',
                  background: '#ef4444',
                  color: '#fff',
                  borderRadius: '50%',
                  width: '18px',
                  height: '18px',
                  fontSize: '10px',
                  fontWeight: '700',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  boxShadow: '0 0 10px rgba(239, 68, 68, 0.4)'
                }}>
                  {notifications.length}
                </span>
              )}
            </button>
            {showNotif && (
              <div style={s.notifDropdown}>
                <div style={{ fontSize: '14px', fontWeight: '700', color: isDark ? '#fff' : '#18181b', marginBottom: '12px' }}>
                  Notifications
                </div>
                {notifications.length === 0 ? (
                  <div style={{ ...s.notifItem, borderBottom: 'none', color: isDark ? '#a1a1aa' : '#71717a', fontSize: '12px', justifyContent: 'center', marginTop: '8px' }}>
                    No new alerts
                  </div>
                ) : (
                  notifications.map((n, idx) => (
                    <div key={n.id} style={{
                      ...s.notifItem,
                      borderBottom: idx === notifications.length - 1 ? 'none' : `1px solid ${isDark ? 'rgba(255,255,255,0.08)' : 'rgba(0,0,0,0.08)'}`,
                      padding: '8px 0',
                      fontSize: '12px',
                      color: isDark ? '#e4e4e7' : '#18181b',
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'space-between',
                      width: '100%',
                      gap: '8px'
                    }}>
                      <div style={{ display: 'flex', alignItems: 'center', gap: '8px', flex: 1 }}>
                        <span>{n.type === 'error' ? '❌' : n.type === 'warning' ? '⚠️' : 'ℹ️'}</span>
                        <span style={{ lineHeight: '1.4' }}>{n.message}</span>
                      </div>
                      <button
                        onClick={(e) => {
                          e.stopPropagation();
                          dismissNotification(n.id);
                        }}
                        style={{
                          background: 'none',
                          border: 'none',
                          color: isDark ? '#a1a1aa' : '#71717a',
                          cursor: 'pointer',
                          fontSize: '14px',
                          padding: '0 4px',
                          display: 'flex',
                          alignItems: 'center',
                          justifyContent: 'center'
                        }}
                        className="icon-hover"
                      >
                        ×
                      </button>
                    </div>
                  ))
                )}
              </div>
            )}
          </div>
          {rightContent}
          <div
            style={s.logoutBtn}
            className="logout-btn desktop-nav"
            onClick={onLogout}
            role="button"
            tabIndex={0}
            onKeyDown={(e) => e.key === 'Enter' && onLogout?.()}
            aria-label="Logout"
          >
            <span style={s.logoutText}>Logout</span>
          </div>
          
          {/* Hamburger Menu Button */}
          <div className="mobile-menu-btn" onClick={toggleMenu} role="button" aria-label="Toggle Menu">
            <div className={`hamburger ${isMobileMenuOpen ? 'open' : ''}`}>
              <span />
              <span />
              <span />
            </div>
          </div>
        </div>
      </div>

      {/* Mobile Drawer Overlay */}
      <div 
        className={`drawer-overlay ${isMobileMenuOpen ? 'open' : ''}`} 
        onClick={closeMenu}
      />

      {/* Mobile Drawer */}
      <div className={`mobile-drawer ${isMobileMenuOpen ? 'open' : ''}`}>
        <div style={{ display: 'flex', flexDirection: 'column', gap: '15px', flex: 1 }}>
          {NAV_ITEMS.map(({ key, label, path }) => {
            const isActive = activePage === key;
            return (
              <button
                key={key}
                type="button"
                style={{
                  ...s.navLink,
                  ...(isActive ? s.navLinkActive : {}),
                  justifyContent: 'flex-start',
                  padding: '12px 20px',
                  fontSize: '14px',
                  width: '100%'
                }}
                onClick={() => handleNavClick(path, isActive)}
              >
                {label}
              </button>
            );
          })}
        </div>
        
        <div style={{ marginTop: 'auto', paddingTop: '20px', borderTop: '1px solid rgba(255,255,255,0.08)' }}>
          <div
            style={{ ...s.logoutBtn, justifyContent: 'center', width: '100%' }}
            onClick={() => {
              onLogout?.();
              closeMenu();
            }}
            role="button"
          >
            <span style={s.logoutText}>Logout</span>
          </div>
        </div>
      </div>
    </>
  );
}
