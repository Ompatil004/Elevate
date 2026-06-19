/**
 * Shared Navbar component — Bug #57 fix.
 *
 * Replaces the duplicate inline Navbar definitions that existed in
 * Nutrition.jsx, Dashboard.jsx, Workout.jsx, and Chatbot.jsx.
 *
 * Props
 * ─────
 *  navigate      (fn)     — react-router-dom navigate function
 *  activePage    (str)    — 'dashboard' | 'workout' | 'nutrition' | 'chatbot'
 *  onLogout      (fn)     — called when user clicks Logout
 *  rightContent  (node)   — optional extra icon buttons to insert before Logout
 */
import React from 'react';

const s = {
  navbar: {
    display: 'flex',
    alignItems: 'center',
    padding: '0 clamp(12px, 4vw, 40px)',
    height: 'clamp(64px, 9vw, 80px)',
    gap: 'clamp(8px, 2vw, 18px)',
    borderBottom: '1px solid rgba(255,255,255,0.08)',
    background: 'rgba(9, 9, 11, 0.6)',
    backdropFilter: 'blur(16px)',
    position: 'sticky',
    top: 0,
    zIndex: 1000,
    overflowX: 'auto',
  },
  brand: {
    flex: 1,
    fontSize: 'clamp(18px, 2.8vw, 22px)',
    fontWeight: '900',
    letterSpacing: '-1px',
    background: 'linear-gradient(to right, #fff, #a5b4fc)',
    WebkitBackgroundClip: 'text',
    WebkitTextFillColor: 'transparent',
    display: 'flex',
    alignItems: 'center',
    gap: '10px',
    cursor: 'pointer',
    userSelect: 'none',
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
    color: '#a1a1aa',
    cursor: 'pointer',
    borderRadius: '20px',
    transition: 'all 0.2s',
    textTransform: 'uppercase',
    letterSpacing: '0.5px',
    border: '1px solid transparent',
    userSelect: 'none',
  },
  navLinkActive: {
    background: 'rgba(255,255,255,0.1)',
    color: '#fff',
    boxShadow: '0 0 20px rgba(255,255,255,0.05)',
    border: '1px solid rgba(255,255,255,0.05)',
  },
  navRight: {
    flex: 1,
    display: 'flex',
    alignItems: 'center',
    gap: 'clamp(8px, 2vw, 24px)',
    justifyContent: 'flex-end',
  },
  iconButton: {
    width: 'clamp(36px, 6vw, 42px)',
    height: 'clamp(36px, 6vw, 42px)',
    borderRadius: '12px',
    background: 'rgba(255,255,255,0.03)',
    border: '1px solid rgba(255,255,255,0.08)',
    color: '#fff',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    cursor: 'pointer',
    fontSize: '18px',
    transition: 'all 0.2s',
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
  logoutText: {
    fontSize: '12px',
    fontWeight: '700',
    letterSpacing: '0.5px',
    textTransform: 'uppercase',
  },
};

const NAV_ITEMS = [
  { key: 'dashboard',  label: 'Dashboard',  path: '/dashboard'  },
  { key: 'workout',    label: 'Workout',    path: '/workout'    },
  { key: 'nutrition',  label: 'Nutrition',  path: '/nutrition'  },
  { key: 'chatbot',    label: 'ChatBot',    path: '/chatbot'    },
];

export default function Navbar({ navigate, activePage, onLogout, rightContent }) {
  return (
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
        ELEVATE
      </div>

      {/* Centre nav links */}
      <div style={s.navCenter}>
        {NAV_ITEMS.map(({ key, label, path }) => {
          const isActive = activePage === key;
          return (
            <button
              key={key}
              type="button"
              className="nav-item"
              style={isActive ? { ...s.navLink, ...s.navLinkActive } : s.navLink}
              onClick={() => !isActive && navigate(path)}
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
        {rightContent}
        <div
          style={s.logoutBtn}
          className="logout-btn"
          onClick={onLogout}
          role="button"
          tabIndex={0}
          onKeyDown={(e) => e.key === 'Enter' && onLogout?.()}
          aria-label="Logout"
        >
          <span style={s.logoutText}>Logout</span>
        </div>
      </div>
    </div>
  );
}
