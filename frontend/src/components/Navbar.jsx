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
import React, { useState, useEffect } from 'react';

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

const responsiveNavbarStyles = `
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

export default function Navbar({ navigate, activePage, onLogout, rightContent }) {
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);

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
          ELEVATE
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
