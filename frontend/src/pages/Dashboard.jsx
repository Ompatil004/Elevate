import React, { useState, useEffect, useMemo, useRef, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import { useNotification } from '../components/NotificationProvider';
import { useTheme } from '../context/ThemeContext';
import ConfirmDialog from '../components/ConfirmDialog';
import { getProfile, saveTrends, getTrends, logActivityToBackend, getRecentActivities, syncActivitiesToBackend, saveDailyLog, getWeeklyLogs, getWeeklyWorkoutPlan } from '../api';
import Navbar from '../components/Navbar';
import { preloadPoseAssets } from '../utils/poseModelPreload';
import { QUOTES } from '../data/quotes';
import {
  getFromStorage,
  setToStorage,
  removeFromStorage,
  logoutSafe,
  StorageKeys,
  getLocalDateStr,
  getTodayStr,
  safeJSONParse
} from '../utils/storage';
import { syncBridge, SyncTypes } from '../utils/syncBridge';
import AuroraBackground from '../components/AuroraBackground';

// --- FULL PREMIUM STYLES (JS Object - Static Only) ---
const styles = {
  page: {
    background: 'transparent',
    minHeight: '100dvh',
    color: 'var(--app-text)',
    fontFamily: "'Inter', -apple-system, BlinkMacSystemFont, sans-serif",
    overflowX: 'hidden',
    position: 'relative',
    zIndex: 1,
    paddingBottom: '40px',
    paddingTop: 'clamp(64px, 9vw, 80px)'
  },
  dateDisplay: {
    fontSize: '13px',
    fontWeight: '600',
    color: 'var(--app-text-muted)',
    fontFamily: 'sans-serif',
    letterSpacing: '0.5px',
    marginRight: '8px'
  },
  navbar: {
    display: 'flex',
    alignItems: 'center',
    padding: '0 clamp(12px, 4vw, 40px)',
    height: 'clamp(64px, 9vw, 80px)',
    gap: 'clamp(8px, 2vw, 18px)',
    borderBottom: '1px solid var(--app-border)',
    background: 'var(--app-nav-bg, rgba(9, 9, 11, 0.6))',
    backdropFilter: 'blur(16px)',
    position: 'fixed',
    top: 0,
    left: 0,
    right: 0,
    zIndex: 1000,
    overflowX: 'auto'
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
    gap: '10px'
  },
  navCenter: {
    display: 'flex',
    gap: 'clamp(4px, 1.5vw, 8px)',
    height: '100%',
    alignItems: 'center',
    justifyContent: 'center'
  },
  navLink: {
    display: 'flex',
    alignItems: 'center',
    padding: '8px clamp(10px, 2vw, 20px)',
    fontSize: 'clamp(11px, 1.7vw, 13px)',
    fontWeight: '600',
    color: 'var(--app-text-muted)',
    cursor: 'pointer',
    borderRadius: '20px',
    transition: 'all 0.2s',
    textTransform: 'uppercase',
    letterSpacing: '0.5px',
    border: '1px solid transparent'
  },
  navLinkActive: {
    background: 'var(--app-border)',
    color: 'var(--app-text)',
    boxShadow: '0 0 20px var(--app-border)',
    border: '1px solid var(--app-border)'
  },
  navRight: {
    flex: 1,
    display: 'flex',
    alignItems: 'center',
    gap: 'clamp(8px, 2vw, 24px)',
    justifyContent: 'flex-end'
  },
  iconButton: {
    width: 'clamp(36px, 6vw, 42px)',
    height: 'clamp(36px, 6vw, 42px)',
    borderRadius: '12px',
    background: 'var(--quote-bg)',
    border: '1px solid var(--app-border)',
    color: 'var(--app-text)',
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
    background: 'var(--app-surface)',
    border: '1px solid var(--app-border)',
    borderRadius: '16px',
    padding: '16px',
    zIndex: 2000,
    boxShadow: '0 20px 50px rgba(0,0,0,0.5)',
    animation: 'slideDown 0.2s ease-out'
  },
  notifItem: {
    padding: '12px 16px',
    borderBottom: '1px solid var(--app-border)',
    fontSize: '13px',
    color: '#d4d4d8',
    display: 'flex',
    gap: '10px',
    alignItems: 'center'
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
    height: 'clamp(36px, 6vw, 42px)'
  },
  logoutText: {
    fontSize: '12px',
    fontWeight: '700',
    letterSpacing: '0.5px',
    textTransform: 'uppercase'
  },
  brandDot: {
    width: '8px',
    height: '8px',
    background: '#6366f1',
    borderRadius: '50%',
    boxShadow: '0 0 15px #6366f1'
  },
  container: {
    maxWidth: '1600px',
    margin: '0 auto',
    padding: 'clamp(10px, 2.5vw, 24px)',
    display: 'grid',
    gridTemplateColumns: 'repeat(12, 1fr)',
    gap: 'clamp(10px, 1.6vw, 16px)'
  },
  bentoBox: {
    background: 'var(--app-surface-glass, var(--app-surface))',
    border: '1px solid var(--app-border)',
    borderRadius: '18px',
    padding: 'clamp(12px, 1.8vw, 20px)',
    display: 'flex',
    flexDirection: 'column',
    position: 'relative',
    overflow: 'hidden',
    transition: 'transform 0.2s ease, border-color 0.2s ease',
    backdropFilter: 'blur(14px)',
    boxShadow: '0 14px 34px rgba(0,0,0,0.22)'
  },
  heroSection: {
    gridColumn: 'span 12',
    background: 'var(--app-hero-glass, var(--app-bg-grad))',
    display: 'flex',
    flexDirection: 'row',
    flexWrap: 'wrap',
    alignItems: 'center',
    justifyContent: 'space-between',
    gap: 'clamp(10px, 1.8vw, 20px)',
    minHeight: 'auto',
    padding: 'clamp(12px, 2vw, 22px)',
    boxShadow: '0 12px 28px rgba(0,0,0,0.2)'
  },
  heroLeft: {
    display: 'flex',
    alignItems: 'flex-start',
    gap: 'clamp(10px, 2.2vw, 24px)',
    flexWrap: 'wrap',
    flex: 1.2,
    minWidth: 0
  },
  avatarWrapper: {
    position: 'relative',
    width: 'clamp(64px, 8vw, 96px)',
    height: 'clamp(64px, 8vw, 96px)',
    flexShrink: 0,
    cursor: 'pointer'
  },
  avatarContainer: {
    width: '100%',
    height: '100%',
    borderRadius: '50%',
    background: 'conic-gradient(from 0deg, #6366f1, #ec4899, #6366f1)',
    padding: '4px',
    boxShadow: '0 10px 50px rgba(99, 102, 241, 0.3)',
    transition: 'transform 0.2s'
  },
  avatarImage: {
    width: '100%',
    height: '100%',
    borderRadius: '50%',
    background: 'var(--app-surface)',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    fontSize: 'clamp(24px, 5vw, 44px)',
    fontWeight: '700',
    color: 'var(--app-text)',
    objectFit: 'cover'
  },
  editIconBadge: {
    position: 'absolute',
    bottom: '5px',
    right: '5px',
    width: 'clamp(30px, 6vw, 40px)',
    height: 'clamp(30px, 6vw, 40px)',
    borderRadius: '50%',
    background: '#4f46e5',
    border: '4px solid var(--app-bg)',
    color: 'var(--app-text)',
    fontSize: 'clamp(14px, 2.6vw, 18px)',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    boxShadow: '0 4px 20px rgba(0,0,0,0.6)',
    zIndex: 10,
    transition: 'all 0.2s ease'
  },
  heroTextContent: {
    display: 'flex',
    flexDirection: 'column',
    alignItems: 'flex-start',
    gap: '10px',
    paddingTop: '8px'
  },
  h1: {
    fontSize: 'clamp(22px, 3.5vw, 36px)',
    fontWeight: '800',
    background: 'var(--h1-grad)',
    WebkitBackgroundClip: 'text',
    WebkitTextFillColor: 'transparent',
    margin: 0,
    whiteSpace: 'normal',
    display: 'flex',
    alignItems: 'center',
    gap: '8px',
    filter: 'drop-shadow(0 4px 20px rgba(99, 102, 241, 0.3))',
    lineHeight: '1.1'
  },
  quoteCard: {
    background: 'var(--quote-bg)',
    borderLeft: '4px solid #6366f1',
    padding: '12px 18px',
    borderRadius: '0 12px 12px 0',
    fontStyle: 'italic',
    color: 'var(--app-text-muted)',
    fontSize: '15px',
    lineHeight: '1.6',
    marginTop: '8px',
    maxWidth: 'min(100%, 450px)'
  },
  heroCenter: {
    flex: 0.8,
    display: 'flex',
    flexDirection: 'column',
    justifyContent: 'center',
    alignItems: 'center',
    gap: '10px'
  },
  circleBtn: {
    width: 'min(100%, 260px)',
    minHeight: '118px',
    borderRadius: '18px',
    border: '1px solid rgba(255,255,255,0.16)',
    cursor: 'pointer',
    display: 'flex',
    flexDirection: 'column',
    alignItems: 'flex-start',
    justifyContent: 'space-between',
    gap: '8px',
    padding: '12px 14px 10px',
    textAlign: 'left',
    color: 'var(--app-text)',
    transition: 'all 0.3s ease',
    textShadow: '0 2px 10px rgba(0,0,0,0.3)',
    position: 'relative',
    zIndex: 10,
    boxShadow: '0 10px 24px rgba(0,0,0,0.28)',
    backdropFilter: 'blur(12px)',
    overflow: 'hidden',
    letterSpacing: '0.6px'
  },
  actionTopRow: {
    width: '100%',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'space-between'
  },
  actionIconPill: {
    width: '36px',
    height: '36px',
    borderRadius: '10px',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    fontSize: '18px',
    border: '1px solid rgba(255,255,255,0.3)',
    background: 'var(--app-border)',
    boxShadow: 'inset 0 0 0 1px var(--app-border)'
  },
  actionStateTag: {
    fontSize: '11px',
    fontWeight: '800',
    letterSpacing: '1px',
    textTransform: 'uppercase',
    padding: '6px 10px',
    borderRadius: '999px',
    border: '1px solid rgba(255,255,255,0.25)',
    background: 'rgba(0,0,0,0.2)',
    color: '#eef2ff'
  },
  actionTextWrap: {
    display: 'flex',
    flexDirection: 'column',
    gap: '6px'
  },
  actionTitle: {
    fontSize: 'clamp(14px, 1.6vw, 18px)',
    fontWeight: '800',
    letterSpacing: '-0.3px',
    lineHeight: 1.15,
    color: 'var(--app-text)'
  },
  actionSubtitle: {
    fontSize: '13px',
    lineHeight: 1.5,
    color: 'rgba(230, 235, 255, 0.92)',
    maxWidth: '30ch'
  },
  actionHint: {
    fontSize: '12px',
    fontWeight: '700',
    color: 'var(--app-text-muted)',
    textTransform: 'uppercase',
    letterSpacing: '1.2px',
    background: 'rgba(255,255,255,0.04)',
    border: '1px solid var(--app-border)',
    borderRadius: '999px',
    padding: '8px 14px'
  },
  btnBlue: {
    background: 'linear-gradient(145deg, rgba(79,70,229,0.95) 0%, rgba(49,46,129,0.95) 100%)'
  },
  btnPink: {
    background: 'linear-gradient(145deg, rgba(236,72,153,0.95) 0%, rgba(157,23,77,0.95) 100%)'
  },
  btnGreen: {
    background: 'linear-gradient(145deg, rgba(34,197,94,0.92) 0%, rgba(20,83,45,0.95) 100%)'
  },
  heroRight: {
    display: 'flex',
    flexDirection: 'column',
    alignItems: 'flex-end',
    justifyContent: 'center',
    gap: '16px',
    flex: 1
  },
  streakLabel: {
    fontSize: '13px',
    fontWeight: '700',
    color: 'var(--app-text-muted)',
    letterSpacing: '3px',
    textTransform: 'uppercase'
  },
  streakNumber: {
    fontSize: '54px',
    fontWeight: '900',
    lineHeight: 0.9,
    background: 'linear-gradient(to bottom, #fff 30%, #6366f1 100%)',
    WebkitBackgroundClip: 'text',
    WebkitTextFillColor: 'transparent',
    filter: 'drop-shadow(0 0 20px rgba(99,102,241,0.3))'
  },
  weekGrid: {
    display: 'flex',
    gap: '8px',
    flexWrap: 'wrap'
  },
  dayCircle: {
    width: 'clamp(34px, 5.5vw, 42px)',
    height: 'clamp(34px, 5.5vw, 42px)',
    borderRadius: '14px',
    background: 'var(--app-surface2)',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    fontSize: '16px',
    border: '1px solid var(--app-border)',
    transition: 'all 0.3s cubic-bezier(0.25, 0.8, 0.25, 1)',
    cursor: 'default',
    fontWeight: '700',
    color: 'var(--app-text-muted)'
  },
  dayActive: {
    background: 'rgba(99, 102, 241, 0.1)',
    borderColor: '#6366f1',
    boxShadow: '0 0 15px rgba(99, 102, 241, 0.2)',
    color: 'var(--app-text)'
  },
  dayDone: {
    background: 'rgba(34, 197, 94, 0.1)',
    borderColor: '#22c55e',
    color: 'var(--app-text)',
    boxShadow: '0 0 15px rgba(34, 197, 94, 0.2)'
  },
  statsRow: {
    gridColumn: 'span 12',
    display: 'grid',
    gridTemplateColumns: 'repeat(3, 1fr)',
    gap: '24px'
  },
  statBox: {
    minHeight: '280px'
  },
  macroBarBG: {
    width: '100%',
    height: '8px',
    background: 'var(--app-surface2)',
    borderRadius: '10px',
    marginTop: '8px',
    overflow: 'hidden'
  },
  macroBarFill: {
    height: '100%',
    borderRadius: '10px',
    transition: 'width 0.5s ease'
  },
  glassPill: {
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'space-between',
    background: 'var(--quote-bg)',
    borderRadius: '50px',
    padding: '4px',
    marginTop: '20px',
    border: '1px solid var(--app-border)',
    boxShadow: 'inset 0 2px 10px rgba(0,0,0,0.3)',
    width: '100%',
    maxWidth: '100%'
  },
  glassBtn: {
    width: '40px',
    height: '40px',
    borderRadius: '50%',
    background: 'transparent',
    border: 'none',
    color: 'var(--app-text)',
    fontSize: '20px',
    cursor: 'pointer',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    transition: 'all 0.2s cubic-bezier(0.25, 0.8, 0.25, 1)'
  },
  glassText: {
    fontSize: '12px',
    fontWeight: '700',
    color: 'var(--app-text-muted)',
    letterSpacing: '1px',
    textTransform: 'uppercase'
  },
  chartSection: {
    gridColumn: 'span 8',
    height: '360px'
  },
  activitySection: {
    gridColumn: 'span 4',
    height: '360px',
    display: 'flex',
    flexDirection: 'column'
  },
  sectionHeader: {
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: '14px'
  },
  sectionTitle: {
    fontSize: 'clamp(14px, 1.8vw, 17px)',
    fontWeight: '800',
    color: 'var(--app-text)',
    display: 'flex',
    alignItems: 'center',
    gap: '8px',
    letterSpacing: '-0.5px'
  },
  sectionAccent: {
    width: '4px',
    height: '24px',
    background: '#6366f1',
    borderRadius: '4px'
  },
  chartControls: {
    display: 'flex',
    gap: '16px',
    flexWrap: 'wrap'
  },
  chartTabs: {
    display: 'flex',
    gap: '4px',
    background: 'var(--app-border)',
    padding: '4px',
    borderRadius: '10px'
  },
  chartTab: {
    padding: '6px 14px',
    borderRadius: '8px',
    fontSize: '11px',
    fontWeight: '700',
    cursor: 'pointer',
    transition: 'all 0.2s',
    border: 'none',
    color: '#71717a',
    background: 'transparent'
  },
  chartTabActive: {
    background: 'var(--app-surface2)',
    color: 'var(--app-text)',
    boxShadow: '0 2px 10px rgba(0,0,0,0.2)'
  },
  listRow: {
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'space-between',
    padding: '18px 16px',
    borderBottom: '1px solid var(--app-border)',
    borderRadius: '16px',
    marginBottom: '8px',
    cursor: 'pointer',
    background: 'transparent'
  },
  modalOverlay: {
    position: 'fixed',
    top: 0,
    left: 0,
    width: '100%',
    height: '100%',
    background: 'rgba(0, 0, 0, 0.85)',
    backdropFilter: 'blur(10px)',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    zIndex: 10000,
    animation: 'fadeIn 0.3s ease'
  },
  modalContent: {
    position: 'relative',
    maxWidth: '500px',
    width: '90%',
    background: 'var(--app-surface)',
    borderRadius: '24px',
    padding: '10px',
    boxShadow: '0 25px 50px rgba(0,0,0,0.5)',
    border: '1px solid var(--app-border)'
  },
  modalImage: {
    width: '100%',
    borderRadius: '16px',
    display: 'block'
  },
  closeModalBtn: {
    position: 'absolute',
    top: '-15px',
    right: '-15px',
    width: '32px',
    height: '32px',
    borderRadius: '50%',
    background: 'var(--app-text)',
    color: 'var(--app-bg)',
    border: 'none',
    fontSize: '16px',
    fontWeight: 'bold',
    cursor: 'pointer',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    boxShadow: '0 4px 10px rgba(0,0,0,0.3)'
  },
  notificationsContainer: {
    position: 'fixed',
    top: '20px',
    right: '20px',
    zIndex: 10000,
    display: 'flex',
    flexDirection: 'column',
    gap: '10px',
    maxWidth: '400px',
    width: '100%'
  },
  notificationItem: {
    padding: '12px 16px',
    borderRadius: '12px',
    boxShadow: '0 4px 12px rgba(0,0,0,0.15)',
    backdropFilter: 'blur(10px)',
    border: '1px solid var(--app-border)',
    display: 'flex',
    alignItems: 'center',
    animation: 'slideInRight 0.3s ease-out',
    background: 'rgba(24, 24, 27, 0.9)'
  },
  notificationSuccess: {
    borderLeft: '4px solid #22c55e'
  },
  notificationWarning: {
    borderLeft: '4px solid #f59e0b'
  },
  notificationInfo: {
    borderLeft: '4px solid #3b82f6'
  },
  notificationClose: {
    background: 'var(--app-border)',
    border: 'none',
    color: 'var(--app-text)',
    fontSize: '16px',
    cursor: 'pointer',
    padding: '4px 8px',
    borderRadius: '6px',
    transition: 'background 0.2s',
    marginLeft: '8px'
  },
  notificationCloseHover: {
    background: 'rgba(255, 255, 255, 0.2)'
  },
  notificationContent: {
    display: 'flex',
    alignItems: 'center',
    gap: '8px',
    flex: 1
  },
  notificationMessage: {
    color: 'var(--app-text)',
    fontSize: '14px',
    lineHeight: 1.4
  }
};

// --- RESPONSIVE CSS STRING (Animations, Media Queries, Hover States) ---
const responsiveStyles = `
  * {
    box-sizing: border-box;
  }

  body {
    margin: 0;
  }

  /* ===== HOVER EFFECTS ===== */
  .hover-card:hover {
    transform: translateY(-4px);
    border-color: rgba(255, 255, 255, 0.12) !important;
    cursor: pointer;
    box-shadow: 0 7px 20px rgba(0, 0, 0, 0.25);
  }

  .hover-scale:hover {
    transform: scale(1.03);
  }

  .nav-item:hover {
    color: #fff !important;
  }

  .macro-item {
    transition: transform 0.2s cubic-bezier(0.25, 0.8, 0.25, 1), filter 0.2s;
  }

  .macro-item:hover {
    transform: scale(1.03);
    filter: brightness(1.15);
  }

  .icon-hover:hover {
    background: var(--app-border) !important;
    animation: ring 1.2s ease;
  }

  .edit-icon-hover:hover {
    transform: scale(1.1);
    background: #4338ca !important;
    box-shadow: 0 0 15px rgba(79, 70, 229, 0.6) !important;
  }

  .logout-btn:hover {
    background: rgba(239, 68, 68, 0.15) !important;
    transform: translateY(-1.5px);
    box-shadow: 0 3px 12px rgba(239, 68, 68, 0.15);
  }

  .control-btn-hover:hover {
    background: rgba(255, 255, 255, 0.12) !important;
    transform: scale(1.07);
  }

  .day-item:hover {
    transform: scale(1.1);
    border-color: #6366f1 !important;
    box-shadow: 0 0 15px rgba(99, 102, 241, 0.3) !important;
    color: #fff;
  }

  .activity-row {
    border-left: 3px solid transparent;
    transition: all 0.2s ease;
  }

  .activity-row:hover {
    background: rgba(255, 255, 255, 0.07) !important;
    transform: translateX(7px);
    border-left: 3px solid #6366f1;
    box-shadow: 0 3px 15px rgba(0, 0, 0, 0.3);
  }

  .hero-action-btn:not(:disabled):hover {
    transform: translateY(-4px);
    box-shadow: 0 18px 34px rgba(0, 0, 0, 0.35);
    border-color: rgba(255, 255, 255, 0.3);
  }

  .hero-action-btn:not(:disabled):active {
    transform: translateY(-1px);
  }

  /* ===== ANIMATIONS ===== */
  @keyframes ring {
    0% { transform: rotate(0); }
    10% { transform: rotate(10deg); }
    20% { transform: rotate(-10deg); }
    30% { transform: rotate(7deg); }
    40% { transform: rotate(-7deg); }
    100% { transform: rotate(0); }
  }

  @keyframes float {
    0% { transform: translateY(0px); }
    50% { transform: translateY(-7px); }
    100% { transform: translateY(0px); }
  }

  .action-icon {
    display: inline-block;
    transform-origin: center;
    animation: iconFloat 2.2s ease-in-out infinite;
  }

  @keyframes iconFloat {
    0%, 100% { transform: translateY(0); }
    50% { transform: translateY(-3px); }
  }

  .hero-ring-glow {
    animation: heroRingGlow 2.4s ease-in-out infinite;
  }

  .neon-radial-btn {
    transition: transform 0.2s ease;
  }

  .neon-radial-btn:not(:disabled):hover {
    transform: translateY(-1px) scale(1.01) !important;
    box-shadow: none !important;
    border-color: transparent !important;
  }

  .neon-radial-btn .hero-ring-glow {
    transition: transform 0.2s ease, filter 0.2s ease;
  }

  .neon-radial-btn:not(:disabled):hover .hero-ring-glow {
    transform: scale(1.06);
    filter: drop-shadow(0 0 14px rgba(236, 72, 153, 0.42));
  }

  .neon-radial-btn .neon-cta {
    transition: transform 0.2s ease, box-shadow 0.2s ease;
  }

  .neon-radial-btn:not(:disabled):hover .neon-cta {
    transform: translateY(-1px);
    box-shadow: 0 0 18px rgba(236, 72, 153, 0.38) !important;
  }

  .neon-radial-btn.neon-state-workout:not(:disabled):hover .neon-cta,
  .neon-radial-btn.neon-state-meal:not(:disabled):hover .neon-cta {
    background: rgba(236, 72, 153, 0.32) !important;
    color: #fff1f8 !important;
  }

  @keyframes heroRingGlow {
    0%, 100% {
      transform: scale(1);
      filter: drop-shadow(0 0 0 rgba(34, 211, 238, 0.18));
    }
    50% {
      transform: scale(1.03);
      filter: drop-shadow(0 0 10px rgba(34, 211, 238, 0.34));
    }
  }

  /* ===== SCROLLBAR ===== */
  .activity-list::-webkit-scrollbar {
    width: 6px;
  }

  .activity-list::-webkit-scrollbar-track {
    background: transparent;
  }

  .activity-list::-webkit-scrollbar-thumb {
    background: var(--app-surface2);
    border-radius: 4px;
  }

  /* ===== ANIMATIONS (Entry/Exit) ===== */
  @keyframes slideDown {
    from {
      opacity: 0;
      transform: translateY(-10px);
    }
    to {
      opacity: 1;
      transform: translateY(0);
    }
  }

  @keyframes slideInRight {
    from {
      opacity: 0;
      transform: translateX(100px);
    }
    to {
      opacity: 1;
      transform: translateX(0);
    }
  }

  @keyframes fadeIn {
    from {
      opacity: 0;
    }
    to {
      opacity: 1;
    }
  }

  @keyframes celebrate {
    0% {
      transform: translate(-50%, -50%) scale(0.5);
      opacity: 0;
    }
    50% {
      transform: translate(-50%, -50%) scale(1.2);
      opacity: 1;
    }
    100% {
      transform: translate(-50%, -50%) scale(1);
      opacity: 0;
    }
  }

  @keyframes floatUp {
    0% { transform: translateY(0) scale(0); opacity: 0; }
    15% { opacity: 1; transform: translateY(-30px) scale(1); }
    100% { transform: translateY(-200px) scale(0.4) rotate(45deg); opacity: 0; }
  }

  @keyframes celebrateCard {
    0% { transform: scale(0.3); opacity: 0; }
    100% { transform: scale(1); opacity: 1; }
  }

  @keyframes bounce {
    0% { transform: scale(0); }
    50% { transform: scale(1.3); }
    70% { transform: scale(0.9); }
    100% { transform: scale(1); }
  }

  @keyframes pulse {
    0% {
      transform: scale(1);
    }
    50% {
      transform: scale(1.05);
    }
    100% {
      transform: scale(1);
    }
  }

  .pulse-animation {
    animation: pulse 1.5s infinite;
  }

  /* ===== RESPONSIVE MEDIA QUERIES ===== */

  /* Extra Small Mobile (320px - 480px) */
  @media (max-width: 480px) {
    .page {
      padding: 8px;
    }

    .container {
      padding: 16px;
      gap: 16px;
    }

    .bentoBox {
      flex-direction: column;
      gap: 16px;
      padding: 16px;
    }

    .heroSection {
      flex-direction: column;
      gap: 20px;
      padding: 20px;
    }

    .heroLeft,
    .heroCenter,
    .heroRight {
      width: 100%;
      text-align: center;
    }

    .avatarWrapper {
      margin: 0 auto 16px auto;
    }

    .statsRow {
      grid-template-columns: 1fr;
      gap: 16px;
    }

    .chartSection {
      grid-column: span 12;
      height: 340px;
    }

    .activitySection {
      grid-column: span 12;
      height: 340px;
    }

    .glassPill {
      flex-direction: column;
      gap: 8px;
      padding: 12px;
      width: 100%;
      max-width: 240px;
      margin: 0 auto;
    }

    .glassBtn {
      width: 100%;
      padding: 10px;
    }

    .sectionHeader {
      flex-direction: column;
      gap: 12px;
      align-items: flex-start;
    }

    .chartControls {
      width: 100%;
      flex-direction: column;
      gap: 12px;
      align-items: center;
    }

    .chartTabs {
      width: 100%;
      justify-content: center;
    }

    .chartTab {
      padding: 4px 10px;
      font-size: 10px;
    }

    .listRow {
      padding: 12px;
      flex-direction: column;
      gap: 6px;
      align-items: center;
    }

    .navbar {
      padding: 0 16px;
      height: 50px;
    }

    .brand {
      font-size: 16px;
    }

    .navLink {
      padding: 6px 10px;
      font-size: 11px;
    }

    .dateDisplay {
      font-size: 11px;
    }

    .iconButton {
      width: 36px;
      height: 36px;
    }

    .logoutBtn {
      padding: 0 12px;
    }

    .logoutText {
      font-size: 10px;
    }

    .notifDropdown {
      width: 280px;
      right: -120px;
    }

    .circleBtn {
      width: 150px;
      height: 150px;
      font-size: 14px;
    }

    .h1 {
      font-size: 32px;
    }

    .quoteCard {
      max-width: 100%;
      padding: 12px 16px;
    }

    .streakNumber {
      font-size: 60px;
    }

    .weekGrid {
      gap: 6px;
    }

    .dayCircle {
      width: 36px;
      height: 36px;
      font-size: 14px;
    }

    .macroBar {
      height: 12px;
    }

    .modalContent {
      width: 95%;
      padding: 8px;
    }

    .closeModalBtn {
      width: 28px;
      height: 28px;
      font-size: 14px;
    }
  }

  /* Small Mobile (481px - 768px) */
  @media (min-width: 481px) and (max-width: 768px) {
    .page {
      padding: 10px;
    }

    .container {
      padding: 20px;
      gap: 20px;
    }

    .bentoBox {
      flex-direction: column;
      gap: 16px;
      padding: 16px;
    }

    .heroSection {
      flex-direction: column;
      gap: 20px;
      padding: 20px;
    }

    .heroLeft,
    .heroCenter,
    .heroRight {
      width: 100%;
      text-align: center;
    }

    .avatarWrapper {
      margin: 0 auto 16px;
    }

    .statsRow {
      grid-template-columns: 1fr;
      gap: 16px;
    }

    .chartSection {
      grid-column: span 12;
      height: 340px;
    }

    .activitySection {
      grid-column: span 12;
      height: 340px;
    }

    .glassPill {
      flex-direction: column;
      gap: 8px;
      padding: 12px;
      width: 100%;
      max-width: 240px;
      margin: 0 auto;
    }

    .glassBtn {
      width: 100%;
      padding: 10px;
    }

    .sectionHeader {
      flex-direction: column;
      gap: 12px;
      align-items: center;
    }

    .chartControls {
      width: 100%;
      flex-direction: column;
      gap: 12px;
      align-items: center;
    }

    .chartTabs {
      width: 100%;
      justify-content: center;
    }

    .chartTab {
      padding: 4px 10px;
      font-size: 10px;
    }

    .listRow {
      padding: 14px 12px;
      flex-direction: column;
      gap: 8px;
      align-items: center;
    }

    .navbar {
      padding: 0 20px;
      height: 60px;
    }

    .brand {
      font-size: 18px;
    }

    .navLink {
      padding: 6px 12px;
      font-size: 12px;
    }

    .circleBtn {
      width: 150px;
      height: 150px;
      font-size: 14px;
    }

    .h1 {
      font-size: 28px;
    }

    .quoteCard {
      max-width: 100%;
      padding: 12px 16px;
    }

    .streakNumber {
      font-size: 60px;
    }

    .weekGrid {
      gap: 6px;
      justify-content: center;
    }

    .dayCircle {
      width: 36px;
      height: 36px;
      font-size: 14px;
    }

    .macroBar {
      height: 12px;
    }

    .sectionTitle {
      font-size: 18px;
    }

    .listRow {
      padding: 14px 12px;
      flex-direction: column;
      gap: 8px;
      align-items: center;
    }

    .modalContent {
      width: 95%;
      padding: 8px;
    }

    .closeModalBtn {
      width: 28px;
      height: 28px;
      font-size: 14px;
    }
  }

  /* Tablet (769px - 1024px) */
  @media (min-width: 769px) and (max-width: 1024px) {
    .bentoBox {
      padding: 20px;
    }

    .heroSection {
      flex-direction: row;
      gap: 30px;
    }

    .statsRow {
      grid-template-columns: repeat(2, 1fr);
      gap: 20px;
    }

    .chartSection {
      height: 380px;
    }

    .activitySection {
      height: 380px;
    }

    .navbar {
      padding: 0 30px;
    }

    .circleBtn {
      width: 170px;
      height: 170px;
    }

    .h1 {
      font-size: 40px;
    }

    .streakNumber {
      font-size: 70px;
    }

    .dayCircle {
      width: 40px;
      height: 40px;
    }

    .sectionTitle {
      font-size: 20px;
    }
  }

  /* Desktop (1025px+) */
  @media (min-width: 1025px) {
    .bentoBox {
      padding: 32px;
    }

    .heroSection {
      gap: 40px;
    }

    .statsRow {
      gap: 24px;
    }

    .chartSection {
      height: 460px;
    }

    .activitySection {
      height: 460px;
    }

    .circleBtn {
      width: 200px;
      height: 200px;
    }

    .h1 {
      font-size: 52px;
    }

    .streakNumber {
      font-size: 90px;
    }

    .dayCircle {
      width: 46px;
      height: 46px;
    }

    .sectionTitle {
      font-size: 22px;
    }
  }
`;

// --- CHART COMPONENT ---
const ActivityChart = React.memo(({ data, mode, period, xLabels: propXLabels }) => {
  const [hoveredPoint, setHoveredPoint] = useState(null);
  if (!data || data.length === 0) return null;

  const xLabels = propXLabels || (period === 'week' ? ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'] : ['W1', 'W2', 'W3', 'W4']);

  const width = 1000;
  const height = 300;
  const padding = { top: 10, right: 30, bottom: 40, left: 60 };
  const chartWidth = width - padding.left - padding.right;
  const chartHeight = height - padding.top - padding.bottom;

  let yMax = Math.max(...data) * 1.2;
  let yMin = 0;
  let unit = '';
  const steps = 4;

  const modeConfig = {
    all: { unit: '%', yMax: 100, color1: '#6366f1', color2: '#a855f7', gradId: 'allGrad' },
    water: { unit: ' L', yMax: 4, color1: '#38bdf8', color2: '#0ea5e9', gradId: 'waterGrad' },
    sleep: { unit: ' h', yMax: 12, color1: '#a78bfa', color2: '#8b5cf6', gradId: 'sleepGrad' },
    meal:  { unit: '', yMax: 3000, color1: '#f472b6', color2: '#ec4899', gradId: 'mealGrad' },
    workout: { unit: ' min', yMax: 120, color1: '#34d399', color2: '#10b981', gradId: 'workoutGrad' },
  };
  const cfg = modeConfig[mode] || modeConfig.workout;
  unit = cfg.unit;
  yMax = Math.max(cfg.yMax, Math.max(...data) * 1.2);

  const yRange = Math.max(yMax - yMin, 1);
  const stepX = chartWidth / Math.max(data.length - 1, 1);

  const getPoint = (i) => {
    const x = padding.left + i * stepX;
    const y = padding.top + chartHeight - (((data[i] - yMin) / yRange) * chartHeight);
    return [x, y];
  };

  const [startX, startY] = getPoint(0);
  let d = `M ${startX} ${startY}`;

  for (let i = 0; i < data.length - 1; i++) {
    const [x0, y0] = getPoint(Math.max(i - 1, 0));
    const [x1, y1] = getPoint(i);
    const [x2, y2] = getPoint(i + 1);
    const [x3, y3] = getPoint(Math.min(i + 2, data.length - 1));

    const cp1x = x1 + (x2 - x0) / 6;
    const cp1y = y1 + (y2 - y0) / 6;
    const cp2x = x2 - (x3 - x1) / 6;
    const cp2y = y2 - (y3 - y1) / 6;
    d += ` C ${cp1x} ${cp1y}, ${cp2x} ${cp2y}, ${x2} ${y2}`;
  }

  const areaPath = `${d} L ${padding.left + chartWidth} ${padding.top + chartHeight} L ${padding.left} ${padding.top + chartHeight} Z`;

  const yLabels = [];
  for (let i = 0; i <= steps; i++) {
    const val = yMin + (yRange / steps) * i;
    const labelVal = (mode === 'water' || mode === 'sleep') ? val.toFixed(1) : Math.round(val);
    yLabels.push({ y: padding.top + chartHeight - (i * (chartHeight / steps)), val: labelVal });
  }

  return (
    <div style={{ flex: 1, position: 'relative', width: '100%', cursor: 'crosshair', overflow: 'hidden' }}>
      <svg key={`${mode}-${data.length}`} viewBox={`0 0 ${width} ${height}`} style={{ width: '100%', height: '100%', overflow: 'visible', animation: 'fadeIn 0.6s ease' }}>
        <defs>
          <linearGradient id={cfg.gradId} x1="0" y1="0" x2="0" y2="1">
            <stop offset="0%" stopColor={cfg.color1} stopOpacity="0.5" />
            <stop offset="100%" stopColor={cfg.color1} stopOpacity="0" />
          </linearGradient>
        </defs>

        {yLabels.map((label, i) => (
          <g key={i}>
            <line x1={padding.left} y1={label.y} x2={width - padding.right} y2={label.y} stroke="var(--app-border)" strokeWidth="1" />
            <text x={padding.left - 15} y={label.y + 4} textAnchor="end" fill="var(--app-text-muted)" fontSize="12" fontFamily="'Inter', sans-serif" fontWeight="500">{label.val}{unit}</text>
          </g>
        ))}

        {xLabels.map((day, i) => {
          const xPos = padding.left + i * stepX;
          return (<text key={i} x={xPos} y={height - 10} textAnchor="middle" fill="var(--app-text-muted)" fontSize="12" fontFamily="'Inter', sans-serif" fontWeight="500">{day}</text>);
        })}

        <path d={areaPath} fill={`url(#${cfg.gradId})`} />
        <path d={d} fill="none" stroke={cfg.color2} strokeWidth="3" strokeLinecap="round" strokeLinejoin="round" />

        {data.map((val, i) => {
          const [cx, cy] = getPoint(i);
          return (
            <g key={i} onMouseEnter={() => setHoveredPoint(i)} onMouseLeave={() => setHoveredPoint(null)}>
              <rect x={cx - stepX / 2} y={padding.top} width={stepX} height={chartHeight} fill="transparent" />
              <circle cx={cx} cy={cy} r={hoveredPoint === i ? 6 : 0} fill="var(--app-bg)" stroke={cfg.color1} strokeWidth="2"
                style={{ transition: 'all 0.15s ease-out', filter: `drop-shadow(0 0 6px ${cfg.color1})` }} />
            </g>
          );
        })}
      </svg>

      <div style={{ position: 'absolute', left: 0, top: 0, width: '100%', height: '100%', pointerEvents: 'none', opacity: hoveredPoint !== null ? 1 : 0, transition: 'opacity 0.2s ease' }}>
        {hoveredPoint !== null && (() => {
          const [cx, cy] = getPoint(hoveredPoint);
          const val = (mode === 'water' || mode === 'sleep') ? data[hoveredPoint].toFixed(1) : Math.round(data[hoveredPoint]);
          const dayLabel = xLabels[hoveredPoint] || '';
          return (
            <div style={{ position: 'absolute', left: `${(cx / width) * 100}%`, top: `${(cy / height) * 100}%`, transform: 'translate(-50%, -130%)', transition: 'left 0.1s linear, top 0.1s linear', background: 'rgba(24, 24, 27, 0.95)', border: `1px solid ${cfg.color1}40`, borderRadius: '8px', padding: '8px 16px', boxShadow: `0 4px 20px rgba(0,0,0,0.5)`, textAlign: 'center', minWidth: '70px', backdropFilter: 'blur(8px)' }}>
              <div style={{ fontSize: '10px', color: 'var(--app-text-muted)', textTransform: 'uppercase', letterSpacing: '1px', marginBottom: '2px' }}>{dayLabel}</div>
              <div style={{ fontSize: '16px', fontWeight: '700', color: 'var(--app-text)', fontFamily: 'sans-serif' }}>
                {val}<span style={{ fontSize: '12px', color: cfg.color1, marginLeft: '2px' }}>{unit}</span>
              </div>
              <div style={{ position: 'absolute', bottom: '-5px', left: '50%', transform: 'translateX(-50%) rotate(45deg)', width: '10px', height: '10px', background: 'rgba(24,24,27,0.95)', borderRight: `1px solid ${cfg.color1}40`, borderBottom: `1px solid ${cfg.color1}40` }} />
            </div>
          );
        })()}
      </div>
    </div>
  );
}, (prevProps, nextProps) => {
  return (
    JSON.stringify(prevProps.data) === JSON.stringify(nextProps.data) &&
    prevProps.mode === nextProps.mode &&
    prevProps.period === nextProps.period &&
    JSON.stringify(prevProps.xLabels) === JSON.stringify(nextProps.xLabels)
  );
});



// --- DEFAULT HISTORY ---
const DEFAULT_HISTORY = [];

// Switch this value to: 'minimal' | 'bold' | 'glass' | 'orbitFusion' | 'glassSlideNeo' | 'neonRadial'
const HERO_ACTION_VARIANT = 'neonRadial';

const HERO_ACTION_VARIANTS = {
  minimal: {
    sync: {
      surface: 'linear-gradient(145deg, rgba(39,39,42,0.96) 0%, rgba(24,24,27,0.96) 100%)',
      border: '1px solid rgba(161,161,170,0.34)',
      shadow: '0 12px 24px rgba(0,0,0,0.3)',
      iconBg: 'rgba(255,255,255,0.09)',
      iconBorder: '1px solid rgba(255,255,255,0.2)',
      iconColor: '#f4f4f5',
      tagBg: 'var(--app-border)',
      tagBorder: '1px solid rgba(255,255,255,0.2)',
      tagColor: '#d4d4d8',
      subtitleColor: 'rgba(228,228,231,0.9)'
    },
    workout: {
      surface: 'linear-gradient(145deg, rgba(36,49,108,0.98) 0%, rgba(30,41,59,0.98) 100%)',
      border: '1px solid rgba(129,140,248,0.46)',
      shadow: '0 14px 28px rgba(49,46,129,0.35)',
      iconBg: 'rgba(129,140,248,0.24)',
      iconBorder: '1px solid rgba(199,210,254,0.45)',
      iconColor: '#e0e7ff',
      tagBg: 'rgba(129,140,248,0.2)',
      tagBorder: '1px solid rgba(129,140,248,0.38)',
      tagColor: '#e0e7ff',
      subtitleColor: 'rgba(224,231,255,0.92)'
    },
    meal: {
      surface: 'linear-gradient(145deg, rgba(131,24,67,0.96) 0%, rgba(63,13,44,0.96) 100%)',
      border: '1px solid rgba(244,114,182,0.45)',
      shadow: '0 14px 28px rgba(131,24,67,0.34)',
      iconBg: 'rgba(244,114,182,0.24)',
      iconBorder: '1px solid rgba(251,207,232,0.42)',
      iconColor: '#fce7f3',
      tagBg: 'rgba(244,114,182,0.2)',
      tagBorder: '1px solid rgba(244,114,182,0.36)',
      tagColor: '#fce7f3',
      subtitleColor: 'rgba(252,231,243,0.9)'
    },
    done: {
      surface: 'linear-gradient(145deg, rgba(20,83,45,0.95) 0%, rgba(22,101,52,0.95) 100%)',
      border: '1px solid rgba(74,222,128,0.42)',
      shadow: '0 14px 28px rgba(21,128,61,0.32)',
      iconBg: 'rgba(74,222,128,0.2)',
      iconBorder: '1px solid rgba(187,247,208,0.42)',
      iconColor: '#dcfce7',
      tagBg: 'rgba(74,222,128,0.2)',
      tagBorder: '1px solid rgba(74,222,128,0.36)',
      tagColor: '#dcfce7',
      subtitleColor: 'rgba(220,252,231,0.92)'
    }
  },
  bold: {
    sync: {
      surface: 'linear-gradient(135deg, var(--app-surface2) 0%, var(--app-surface) 100%)',
      border: '1px solid rgba(255,255,255,0.18)',
      shadow: '0 16px 30px rgba(0,0,0,0.34)',
      iconBg: 'var(--app-border)',
      iconBorder: '1px solid rgba(255,255,255,0.3)',
      iconColor: '#f4f4f5',
      tagBg: 'rgba(255,255,255,0.12)',
      tagBorder: '1px solid rgba(255,255,255,0.25)',
      tagColor: '#f4f4f5',
      subtitleColor: 'rgba(228,228,231,0.92)'
    },
    workout: {
      surface: 'linear-gradient(145deg, rgba(79,70,229,0.96) 0%, rgba(49,46,129,0.96) 100%)',
      border: '1px solid rgba(199,210,254,0.36)',
      shadow: '0 18px 34px rgba(79,70,229,0.4)',
      iconBg: 'rgba(199,210,254,0.25)',
      iconBorder: '1px solid rgba(224,231,255,0.45)',
      iconColor: '#eef2ff',
      tagBg: 'rgba(224,231,255,0.18)',
      tagBorder: '1px solid rgba(224,231,255,0.35)',
      tagColor: '#eef2ff',
      subtitleColor: 'rgba(224,231,255,0.95)'
    },
    meal: {
      surface: 'linear-gradient(145deg, rgba(236,72,153,0.96) 0%, rgba(157,23,77,0.96) 100%)',
      border: '1px solid rgba(251,207,232,0.35)',
      shadow: '0 18px 34px rgba(190,24,93,0.36)',
      iconBg: 'rgba(251,207,232,0.2)',
      iconBorder: '1px solid rgba(251,207,232,0.4)',
      iconColor: '#fff1f8',
      tagBg: 'rgba(251,207,232,0.17)',
      tagBorder: '1px solid rgba(251,207,232,0.34)',
      tagColor: '#fff1f8',
      subtitleColor: 'rgba(255,241,248,0.94)'
    },
    done: {
      surface: 'linear-gradient(145deg, rgba(34,197,94,0.94) 0%, rgba(20,83,45,0.96) 100%)',
      border: '1px solid rgba(187,247,208,0.35)',
      shadow: '0 18px 34px rgba(21,128,61,0.34)',
      iconBg: 'rgba(187,247,208,0.22)',
      iconBorder: '1px solid rgba(220,252,231,0.4)',
      iconColor: '#ecfdf5',
      tagBg: 'rgba(220,252,231,0.16)',
      tagBorder: '1px solid rgba(220,252,231,0.32)',
      tagColor: '#ecfdf5',
      subtitleColor: 'rgba(236,253,245,0.93)'
    }
  },
  glass: {
    sync: {
      surface: 'linear-gradient(150deg, rgba(63,63,70,0.62) 0%, rgba(24,24,27,0.75) 100%)',
      border: '1px solid rgba(228,228,231,0.24)',
      shadow: '0 18px 32px rgba(0,0,0,0.34)',
      iconBg: 'rgba(255,255,255,0.13)',
      iconBorder: '1px solid rgba(255,255,255,0.24)',
      iconColor: '#f4f4f5',
      tagBg: 'var(--app-border)',
      tagBorder: '1px solid rgba(255,255,255,0.2)',
      tagColor: 'var(--app-text)',
      subtitleColor: 'rgba(228,228,231,0.9)'
    },
    workout: {
      surface: 'linear-gradient(150deg, rgba(79,70,229,0.44) 0%, rgba(15,23,42,0.82) 100%)',
      border: '1px solid rgba(129,140,248,0.45)',
      shadow: '0 20px 36px rgba(79,70,229,0.34)',
      iconBg: 'rgba(129,140,248,0.22)',
      iconBorder: '1px solid rgba(199,210,254,0.38)',
      iconColor: '#e0e7ff',
      tagBg: 'rgba(129,140,248,0.18)',
      tagBorder: '1px solid rgba(129,140,248,0.34)',
      tagColor: '#e0e7ff',
      subtitleColor: 'rgba(224,231,255,0.9)'
    },
    meal: {
      surface: 'linear-gradient(150deg, rgba(236,72,153,0.4) 0%, rgba(63,13,44,0.84) 100%)',
      border: '1px solid rgba(244,114,182,0.4)',
      shadow: '0 20px 36px rgba(190,24,93,0.32)',
      iconBg: 'rgba(244,114,182,0.2)',
      iconBorder: '1px solid rgba(251,207,232,0.35)',
      iconColor: '#fdf2f8',
      tagBg: 'rgba(244,114,182,0.16)',
      tagBorder: '1px solid rgba(244,114,182,0.32)',
      tagColor: '#fdf2f8',
      subtitleColor: 'rgba(252,231,243,0.9)'
    },
    done: {
      surface: 'linear-gradient(150deg, rgba(34,197,94,0.36) 0%, rgba(20,83,45,0.84) 100%)',
      border: '1px solid rgba(74,222,128,0.38)',
      shadow: '0 20px 36px rgba(21,128,61,0.3)',
      iconBg: 'rgba(74,222,128,0.18)',
      iconBorder: '1px solid rgba(187,247,208,0.35)',
      iconColor: '#f0fdf4',
      tagBg: 'rgba(74,222,128,0.16)',
      tagBorder: '1px solid rgba(74,222,128,0.3)',
      tagColor: '#f0fdf4',
      subtitleColor: 'rgba(220,252,231,0.9)'
    }
  },
  orbitFusion: {
    sync: {
      surface: 'transparent',
      border: '2px solid rgba(6,182,212,0.75)',
      shadow: '0 0 0 1px rgba(6,182,212,0.2), 0 16px 30px rgba(8,47,73,0.36)',
      iconBg: 'rgba(56,189,248,0.18)',
      iconBorder: '1px solid rgba(125,211,252,0.36)',
      iconColor: '#e0f2fe',
      tagBg: 'rgba(56,189,248,0.15)',
      tagBorder: '1px solid rgba(56,189,248,0.35)',
      tagColor: '#bae6fd',
      subtitleColor: 'rgba(224,242,254,0.95)'
    },
    workout: {
      surface: 'transparent',
      border: '2px solid rgba(79,70,229,0.78)',
      shadow: '0 0 0 1px rgba(79,70,229,0.22), 0 18px 34px rgba(49,46,129,0.4)',
      iconBg: 'rgba(99,102,241,0.22)',
      iconBorder: '1px solid rgba(199,210,254,0.42)',
      iconColor: '#eef2ff',
      tagBg: 'rgba(129,140,248,0.2)',
      tagBorder: '1px solid rgba(199,210,254,0.38)',
      tagColor: '#e0e7ff',
      subtitleColor: 'rgba(224,231,255,0.96)'
    },
    meal: {
      surface: 'transparent',
      border: '2px solid rgba(236,72,153,0.78)',
      shadow: '0 0 0 1px rgba(236,72,153,0.22), 0 18px 34px rgba(157,23,77,0.4)',
      iconBg: 'rgba(236,72,153,0.2)',
      iconBorder: '1px solid rgba(251,207,232,0.38)',
      iconColor: '#fdf2f8',
      tagBg: 'rgba(236,72,153,0.18)',
      tagBorder: '1px solid rgba(244,114,182,0.36)',
      tagColor: '#fbcfe8',
      subtitleColor: 'rgba(252,231,243,0.95)'
    },
    done: {
      surface: 'transparent',
      border: '2px solid rgba(34,197,94,0.72)',
      shadow: '0 0 0 1px rgba(34,197,94,0.2), 0 18px 34px rgba(21,128,61,0.34)',
      iconBg: 'rgba(74,222,128,0.2)',
      iconBorder: '1px solid rgba(187,247,208,0.38)',
      iconColor: '#f0fdf4',
      tagBg: 'rgba(74,222,128,0.17)',
      tagBorder: '1px solid rgba(134,239,172,0.36)',
      tagColor: '#dcfce7',
      subtitleColor: 'rgba(220,252,231,0.95)'
    }
  },
  glassSlideNeo: {
    sync: {
      surface: 'rgba(15,23,42,0.42)',
      border: '1px solid rgba(56,189,248,0.38)',
      shadow: '0 14px 30px rgba(0,0,0,0.34), inset 0 1px 0 rgba(255,255,255,0.06)',
      iconBg: 'linear-gradient(135deg, #1f2937 0%, #111827 100%)',
      iconBorder: '1px solid rgba(56,189,248,0.28)',
      iconColor: '#bae6fd',
      subtitleColor: '#cbd5e1',
      ctaBorder: 'rgba(56,189,248,0.55)',
      ctaBg: 'rgba(14,165,233,0.14)',
      ctaText: '#e0f2fe',
      slideTrackBg: 'rgba(15,23,42,0.72)',
      slideTrackBorder: '1px solid rgba(56,189,248,0.3)',
      slideKnob: 'linear-gradient(135deg, #06b6d4, #0891b2)',
      slideText: '#bae6fd'
    },
    workout: {
      surface: 'rgba(15,23,42,0.42)',
      border: '1px solid rgba(129,140,248,0.4)',
      shadow: '0 14px 30px rgba(0,0,0,0.34), inset 0 1px 0 rgba(255,255,255,0.06)',
      iconBg: 'linear-gradient(135deg, #2b2f3a 0%, #171a22 100%)',
      iconBorder: '1px solid rgba(129,140,248,0.3)',
      iconColor: '#e0e7ff',
      subtitleColor: '#cbd5e1',
      ctaBorder: 'rgba(99,102,241,0.62)',
      ctaBg: 'rgba(79,70,229,0.18)',
      ctaText: '#eef2ff',
      slideTrackBg: 'rgba(15,23,42,0.72)',
      slideTrackBorder: '1px solid rgba(129,140,248,0.32)',
      slideKnob: 'linear-gradient(135deg, #4f46e5, #06b6d4)',
      slideText: '#c7d2fe'
    },
    meal: {
      surface: 'rgba(15,23,42,0.42)',
      border: '1px solid rgba(244,114,182,0.4)',
      shadow: '0 14px 30px rgba(0,0,0,0.34), inset 0 1px 0 rgba(255,255,255,0.06)',
      iconBg: 'linear-gradient(135deg, #2b2f3a 0%, #171a22 100%)',
      iconBorder: '1px solid rgba(244,114,182,0.3)',
      iconColor: '#fbcfe8',
      subtitleColor: '#d8b4fe',
      ctaBorder: 'rgba(236,72,153,0.62)',
      ctaBg: 'rgba(236,72,153,0.16)',
      ctaText: '#fdf2f8',
      slideTrackBg: 'rgba(15,23,42,0.72)',
      slideTrackBorder: '1px solid rgba(244,114,182,0.3)',
      slideKnob: 'linear-gradient(135deg, #ec4899, #06b6d4)',
      slideText: '#fbcfe8'
    },
    done: {
      surface: 'rgba(15,23,42,0.42)',
      border: '1px solid rgba(74,222,128,0.4)',
      shadow: '0 14px 30px rgba(0,0,0,0.34), inset 0 1px 0 rgba(255,255,255,0.06)',
      iconBg: 'linear-gradient(135deg, #2b2f3a 0%, #171a22 100%)',
      iconBorder: '1px solid rgba(74,222,128,0.3)',
      iconColor: '#bbf7d0',
      subtitleColor: '#bbf7d0',
      ctaBorder: 'rgba(34,197,94,0.58)',
      ctaBg: 'rgba(34,197,94,0.15)',
      ctaText: '#dcfce7',
      slideTrackBg: 'rgba(15,23,42,0.72)',
      slideTrackBorder: '1px solid rgba(74,222,128,0.3)',
      slideKnob: 'linear-gradient(135deg, #22c55e, #16a34a)',
      slideText: '#bbf7d0'
    }
  },
  neonRadial: {
    sync: {
      surface: 'transparent',
      border: 'none',
      shadow: 'none',
      ringColor: '#06b6d4',
      ringGlow: 'rgba(6,182,212,0.34)',
      coreBg: '#0b1220',
      coreBorder: 'none',
      iconColor: '#bae6fd',
      titleColor: '#e0f2fe',
      subtitleColor: '#bae6fd',
      ctaBorder: 'rgba(6,182,212,0.62)',
      ctaBg: 'rgba(6,182,212,0.14)',
      ctaText: '#e0f2fe'
    },
    workout: {
      surface: 'transparent',
      border: 'none',
      shadow: 'none',
      ringColor: '#ec4899',
      ringGlow: 'rgba(236,72,153,0.34)',
      coreBg: '#17131f',
      coreBorder: 'none',
      iconColor: '#fbcfe8',
      titleColor: '#fce7f3',
      subtitleColor: '#fbcfe8',
      ctaBorder: 'rgba(236,72,153,0.64)',
      ctaBg: 'rgba(236,72,153,0.16)',
      ctaText: '#fff1f8'
    },
    meal: {
      surface: 'transparent',
      border: 'none',
      shadow: 'none',
      ringColor: '#4f46e5',
      ringGlow: 'rgba(79,70,229,0.34)',
      coreBg: '#111827',
      coreBorder: 'none',
      iconColor: '#c7d2fe',
      titleColor: '#e0e7ff',
      subtitleColor: '#c7d2fe',
      ctaBorder: 'rgba(79,70,229,0.66)',
      ctaBg: 'rgba(79,70,229,0.16)',
      ctaText: '#eef2ff'
    },
    done: {
      surface: 'transparent',
      border: 'none',
      shadow: 'none',
      ringColor: '#22c55e',
      ringGlow: 'rgba(34,197,94,0.32)',
      coreBg: '#102019',
      coreBorder: 'none',
      iconColor: '#bbf7d0',
      titleColor: '#dcfce7',
      subtitleColor: '#bbf7d0',
      ctaBorder: 'rgba(34,197,94,0.62)',
      ctaBg: 'rgba(34,197,94,0.14)',
      ctaText: '#dcfce7'
    }
  }
};

const getHeroActionTheme = (variantName, stateKey) => {
  const variant = HERO_ACTION_VARIANTS[variantName] || HERO_ACTION_VARIANTS.bold;
  return variant[stateKey] || variant.sync;
};

// Progress circle score is now computed dynamically inside Dashboard component
// based on real daily metrics (workout done, meals logged, water intake, sleep hours).
// This function is kept only as a fallback for status-only contexts.
const getFallbackRadialScore = (status) => {
  if (status === 'workout') return 42;
  if (status === 'meal') return 74;
  if (status === 'done') return 100;
  return 18;
};

const getHeroActionMeta = (status) => {
  if (status === 'workout') {
    return {
      stateKey: 'workout',
      icon: '🏋️‍♂️',
      tag: '',
      title: 'Start Workout',
      subtitle: '',
      disabled: false
    };
  }

  if (status === 'meal') {
    return {
      stateKey: 'meal',
      icon: '🍽️',
      tag: '',
      title: 'Complete Meals',
      subtitle: '',
      disabled: false
    };
  }

  if (status === 'done') {
    return {
      stateKey: 'done',
      icon: '✅',
      tag: '',
      title: 'All Set',
      subtitle: '',
      disabled: true
    };
  }

  return {
    stateKey: 'sync',
    icon: '⏳',
    tag: '',
    title: 'Preparing Data',
    subtitle: '',
    disabled: true
  };
};

const calculateOverallTrendScore = (entry, calorieGoal, waterGoal) => {
  if (!entry || typeof entry !== 'object') return 0;

  const safeCaloriesGoal = Math.max(1, Number(calorieGoal) || 2200);
  const safeWaterGoal = Math.max(0.1, Number(waterGoal) || 2.3);

  const workoutScore = entry.workout_completed ? 100 : (entry.workout_partial ? 50 : 0);
  const mealRaw = Number(entry.calories) || 0;
  const mealScore = entry.meal_completed
    ? 100
    : (mealRaw > 0 ? Math.min(100, (mealRaw / safeCaloriesGoal) * 100) : 0);
  const waterRaw = Number(entry.water_intake ?? entry.water_glasses) || 0;
  const sleepRaw = Number(entry.sleep_duration ?? entry.sleep_hours) || 0;
  const waterScore = Math.min(100, (waterRaw / safeWaterGoal) * 100);
  const sleepScore = Math.min(100, (sleepRaw / 8) * 100);

  return Math.round(
    (workoutScore * 0.3) +
    (mealScore * 0.25) +
    (waterScore * 0.25) +
    (sleepScore * 0.2)
  );
};

function Dashboard({ onLogout }) {
  const navigate = useNavigate();
  const { showInfo, showError } = useNotification();
  const { theme, toggleTheme } = useTheme();

  // --- STATE DECLARATIONS ---
  const [displayName, setDisplayName] = useState('Titan');
  const [userAvatar, setUserAvatar] = useState(null);
  const [showImageModal, setShowImageModal] = useState(false);
  const [confirmDialog, setConfirmDialog] = useState({
    show: false,
    message: '',
    onConfirm: null
  });

  const [stats, setStats] = useState({
    workoutCount: 0,
    mealCount: 0,
    streak: 0,
    focusScore: 0
  });
  const [macros, setMacros] = useState({
    p: 0,
    c: 0,
    f: 0,
    pMax: 180,
    cMax: 250,
    fMax: 70,
    calories: 0,
    calMax: 2500,
    remaining: 2500   // calMax - calories: how much the user can still eat today
  });

  // ✅ FIX 2: Cross-page macro update — called when meal is saved from Nutrition page
  // Sets absolute macro values (not incremental) from today's totals returned by the backend
  const _setMacrosFromTotals = (totals) => {
    try {
      if (!totals) return;
      const calories = Math.round(Number(totals.calories) || 0);
      setMacros((prev) => ({
        ...prev,
        p: Math.round(Number(totals.protein) || prev.p),
        c: Math.round(Number(totals.carbs) || prev.c),
        f: Math.round(Number(totals.fat) || prev.f),
        calories: calories || prev.calories,
        remaining: Math.max(0, prev.calMax - (calories || prev.calories)),
      }));
    } catch (error) {
      console.error('Error setting macros from totals:', error);
    }
  };

  const _updateMacrosFromMeal = async (mealData) => {
    try {
      const protein = mealData.protein || 0;
      const carbs = mealData.carbs || 0;
      const fats = mealData.fat || mealData.fats || 0;
      const calories = mealData.calories || 0;

      setMacros((prev) => {
        const newCalories = Math.round(prev.calories + calories);
        return {
          ...prev,
          p: Math.round(prev.p + protein),
          c: Math.round(prev.c + carbs),
          f: Math.round(prev.f + fats),
          calories: newCalories,
          remaining: Math.max(0, prev.calMax - newCalories),
        };
      });

      await logActivity(
        'macros',
        'Macro Update',
        `+${calories} cal, +${protein}g P, +${carbs}g C, +${fats}g F`
      );
    } catch (error) {
      console.error('Error updating macros from meal:', error);
      showInfo('There was an issue updating your daily macros. Please try again.', 3000);
    }
  };

  const lastSaved = useRef({ water: 0, sleep: 0, workout_completed: false });

  const [water, setWater] = useState(0);
  const [weeklyAverages, setWeeklyAverages] = useState(null);
  const [sleep, setSleep] = useState(0);
  const [status, setStatus] = useState(null);
  const [dailyProgress, setDailyProgress] = useState(0); // 0-100, computed from real metrics
  const [mealsLoggedToday, setMealsLoggedToday] = useState(0); // 0-3: how many of breakfast/lunch/dinner done
  const [workoutProgress, setWorkoutProgress] = useState(0); // 0-1 ratio: exercises completed / total
  const [workoutIntensity] = useState(0);
  const [recoveryScore, setRecoveryScore] = useState(0);
  const [notifications, setNotifications] = useState(() => getFromStorage('active_notifications', []));
  const [activeToasts, setActiveToasts] = useState([]);

  useEffect(() => {
    setToStorage('active_notifications', notifications);
  }, [notifications]);
  const [lastNotificationCheck, setLastNotificationCheck] = useState(null);
  const [showWaterCelebration, setShowWaterCelebration] = useState(false);
  const [showSleepCelebration, setShowSleepCelebration] = useState(false);
  const [chartMode, setChartMode] = useState('workout');
  const [chartPeriod, setChartPeriod] = useState('week');
  const [chartData, setChartData] = useState([0, 0, 0, 0, 0, 0, 0]);
  const [chartXLabels, setChartXLabels] = useState(['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']);
  const [recentHistory, setRecentHistory] = useState([]);
  const [weeklyProgress, setWeeklyProgress] = useState([]);
  const [loading, setLoading] = useState(true);
  const [viewportWidth, setViewportWidth] = useState(
    typeof window !== 'undefined' ? window.innerWidth : 1280
  );

  useEffect(() => {
    const handleResize = () => setViewportWidth(window.innerWidth);
    window.addEventListener('resize', handleResize);
    return () => window.removeEventListener('resize', handleResize);
  }, []);

  const isCompactLayout = viewportWidth <= 1024;
  const dashboardLayout = {
    statsRow: isCompactLayout
      ? { ...styles.statsRow, gridTemplateColumns: '1fr' }
      : styles.statsRow,
    chartSection: isCompactLayout
      ? { ...styles.chartSection, gridColumn: 'span 12', height: '360px' }
      : styles.chartSection,
    activitySection: isCompactLayout
      ? { ...styles.activitySection, gridColumn: 'span 12', height: '360px' }
      : styles.activitySection
  };

  const todayDate = new Date().toLocaleDateString('en-US', {
    weekday: 'short',
    month: 'short',
    day: 'numeric'
  });

  const currentQuote = useMemo(() => {
    if (!QUOTES || QUOTES.length === 0) return 'Stay hard.';
    const now = new Date();
    const start = new Date(now.getFullYear(), 0, 0);
    const dayOfYear = Math.floor((now - start) / (1000 * 60 * 60 * 24));
    const year = now.getFullYear();
    const infiniteIndex = dayOfYear + year * 365;
    return QUOTES[infiniteIndex % QUOTES.length];
  }, []);

  // --- Compute dailyProgress (0-100) from real daily metrics ---
  //
  // ✅ Breakdown (25 pts each):
  //   Workout: granular per exercise (completedCount / totalCount) × 25
  //   Meals:   exact per meal (0, 1, 2, or 3 of B/L/D) × 25
  //   Water:   intake / (weight × 0.033L) × 25, updates on every glass added
  //   Sleep:   hours / 7h × 25, updates on every 30-min increment
  //
  // Triggers: status, water, sleep (all already live state), mealsLoggedToday, workoutProgress
  useEffect(() => {
    try {
      // 1. Workout (25 pts) — granular per-exercise ratio
      //    If full workout done via status flag, give full 25.
      //    Otherwise use workoutProgress (0-1) from _workoutSync.
      let workoutPts;
      if (status === 'meal' || status === 'done') {
        workoutPts = 25; // full workout completed & logged
      } else {
        workoutPts = Math.round(workoutProgress * 25);
      }

      // 2. Meals (25 pts) — exact per-meal credit (breakfast/lunch/dinner = ~8.3pts each)
      let mealPts;
      if (status === 'done') {
        mealPts = 25;
      } else {
        mealPts = Math.round((mealsLoggedToday / 3) * 25);
      }

      // 3. Water (25 pts) — intake vs personal goal (weight × 0.033 L), updates per glass
      const userWeight = parseFloat(safeJSONParse('user', {})?.weight || '70');
      const _isWkDone = (typeof status !== "undefined" && (status === "done" || status === "meal")) || (typeof workoutProgress !== "undefined" && workoutProgress === 1);
      const waterGoal = getDynamicWaterGoal(typeof userWeight !== "undefined" ? userWeight : 70, typeof sleep !== "undefined" ? sleep : 0, _isWkDone);
      const waterRatio = Math.min(1, water / waterGoal);
      const waterPts = Math.round(waterRatio * 25);

      // 4. Sleep (25 pts) — hours / 7h, updates every +30 min logged
      const sleepRatio = Math.min(1, sleep / 7);
      const sleepPts = Math.round(sleepRatio * 25);

      let total = workoutPts + mealPts + waterPts + sleepPts;
      
      // Prevent progress bar from going up just because of pre-filled sleep data
      if (workoutPts === 0 && mealPts === 0 && waterPts === 0) {
        total = 0;
      }
      setDailyProgress(Math.min(100, Math.max(0, total)));
    } catch (err) {
      console.error('Error computing daily progress:', err);
    }
  }, [status, water, sleep, mealsLoggedToday, workoutProgress]);

  useEffect(() => {
    const unsubWater = syncBridge.subscribe(SyncTypes.WATER_ADDED, (data) => {
      const amount = Number(data?.amount);
      if (!Number.isFinite(amount)) return;
      setWater((prev) => (Math.abs(prev - amount) > 0.001 ? amount : prev));
    });

    const unsubSleep = syncBridge.subscribe(SyncTypes.SLEEP_UPDATED, (data) => {
      const amount = Number(data?.hours);
      if (!Number.isFinite(amount)) return;
      setSleep((prev) => (Math.abs(prev - amount) > 0.001 ? amount : prev));
    });

    const unsubMeal = syncBridge.subscribe(SyncTypes.MEAL_COMPLETED, (data) => {
      const mealsCount = Number(data?.mealsCount);
      if (Number.isFinite(mealsCount)) {
        setMealsLoggedToday(Math.max(0, Math.min(3, mealsCount)));
      }
      const cal = Number(data?.calories);
      const details = Number.isFinite(cal) && cal > 0 ? `${Math.round(cal)} cal consumed` : 'Meal logged';
      logActivity('meal', 'Meal Completed', details);
    });

    const unsubWorkoutProgress = syncBridge.subscribe(SyncTypes.WORKOUT_PROGRESS, (data) => {
      const completed = Number(data?.completedCount) || 0;
      const total = Math.max(1, Number(data?.totalCount) || 1);
      const ratio = Math.max(0, Math.min(1, completed / total));
      setWorkoutProgress(ratio);
      logActivity('workout', 'Workout In Progress', `${completed}/${total} exercises done`);
    });

    const unsubWorkoutDone = syncBridge.subscribe(SyncTypes.WORKOUT_COMPLETED, (data) => {
      setWorkoutProgress(1);
      const completed = Number(data?.completedCount) || 0;
      const total = Number(data?.totalCount) || completed;
      const details = total > 0 ? `${completed}/${total} exercises completed` : 'Workout completed';
      logActivity('workout', 'Workout Completed 💪', details);
    });

    return () => {
      unsubWater();
      unsubSleep();
      unsubMeal();
      unsubWorkoutProgress();
      unsubWorkoutDone();
    };
  }, []);

  const getWorkoutPlanForDate = (dateObj) => {
    try {
      const raw = getFromStorage('workoutPlan');
      const plan = Array.isArray(raw) ? raw : [];
      if (plan.length === 0) return null;
      const jsDay = dateObj.getDay();
      const idx = (jsDay + 6) % 7;
      return plan.find((d) => (d?.day_of_week ?? -1) === idx) || plan[idx] || null;
    } catch {
      return null;
    }
  };

  const isRestDayForDate = (dateObj) => {
    const dayPlan = getWorkoutPlanForDate(dateObj);
    if (!dayPlan) return false;
    // 1. Explicit type from backend engine
    if (dayPlan.type === 'rest') return true;
    // 2. Focus field
    const focus = `${dayPlan.focus || ''}`.toLowerCase();
    if (focus.includes('rest') || focus === 'active recovery') return true;
    // 3. Label / note
    const label = `${dayPlan.day || ''}`.toLowerCase();
    const note = `${dayPlan.note || ''}`.toLowerCase();
    if (label.includes('rest') || note.includes('rest') || note.includes('recovery')) return true;
    return false;
  };

  const normalizeMealEntries = (rawMeals = []) => {
    const normalized = [];
    (Array.isArray(rawMeals) ? rawMeals : []).forEach((entry) => {
      if (entry && typeof entry === 'object' && entry.meals && typeof entry.meals === 'object') {
        const baseDate = entry.date || '';
        Object.values(entry.meals).forEach((meal) => {
          if (!meal || typeof meal !== 'object') return;
          normalized.push({
            ...meal,
            date: baseDate,
            name: meal.name || meal.meal_type || 'Meal',
            calories: Number(meal.calories) || 0,
            protein: Number(meal.protein) || 0,
            carbs: Number(meal.carbs) || 0,
            fat: Number(meal.fat) || 0,
            completedAt: meal.completed_at || meal.completedAt || baseDate
          });
        });
      } else if (entry && typeof entry === 'object') {
        normalized.push(entry);
      }
    });
    return normalized;
  };

  // --- EFFECTS & LIFECYCLE ---

  // Fetch user and init dashboard
  useEffect(() => {
    const fetchUserData = async () => {
      try {
        checkInterruptedSessions();

        const { data } = await getProfile();
        if (!data.goal || !data.weight || !data.age) {
          navigate('/profile-setup', { replace: true });
          return;
        }

        if (data.name) setDisplayName(data.name.split(' ')[0]);

        // Start background preloading of workout cache and pose assets after 3s delay
        try {
          setTimeout(() => {
            // 1. Warm workout plan cache if missing or expired
            const cachedPlan = localStorage.getItem('workoutPlan');
            const cachedTimestamp = localStorage.getItem('workoutPlanTimestamp');
            const cachedVersion = localStorage.getItem('workoutPlanVersion');

            const WORKOUT_PLAN_CACHE_VERSION = '2026-04-10-workout-fix-6-seeded-shuffle-variety';
            let needsWarmup = !cachedPlan || cachedVersion !== WORKOUT_PLAN_CACHE_VERSION;
            if (cachedPlan && cachedTimestamp && !needsWarmup) {
              const timestamp = new Date(cachedTimestamp);
              const now = new Date();
              const hoursSinceCache = (now - timestamp) / (1000 * 60 * 60);
              if (hoursSinceCache >= 24) {
                needsWarmup = true;
              }
            }

            if (needsWarmup) {
              console.log('[Dashboard] Warming up workout plan cache in background...');
              getWeeklyWorkoutPlan().then((workoutResponse) => {
                const plan = workoutResponse?.data?.plan || workoutResponse?.data?.data?.plan || [];
                if (plan.length > 0) {
                  localStorage.setItem('workoutPlan', JSON.stringify(plan));
                  localStorage.setItem('workoutPlanTimestamp', new Date().toISOString());
                  localStorage.setItem('workoutPlanVersion', WORKOUT_PLAN_CACHE_VERSION);
                  console.log('[Dashboard] Background workout cache pre-warmed successfully');
                }
              }).catch((err) => {
                console.warn('[Dashboard] Background workout cache warmup failed:', err?.message || err);
              });
            }


            // 2. Nutrition plan is now cached on the backend (generate once per
            // user per ISO-week, served instantly thereafter). The previous
            // background warmup here was broken — it read response.data.plan
            // (always undefined; the real field is response.data.nutrition) and
            // wrote nutritionCache/nutritionCacheDate while Nutrition.jsx reads
            // nutritionPlan/nutritionPlanDate via StorageKeys — so it cached
            // nothing and only triggered the slow generation path. Removed.
            // Nutrition.jsx's own on-demand fetch is now a fast backend cache hit.


            // 3. Preload MediaPipe pose assets in background
            preloadPoseAssets().catch((err) => {
              console.warn('[Dashboard] Background pose assets preloading skipped/failed:', err?.message || err);
            });
          }, 500);
        } catch (preloadErr) {
          console.warn('[Dashboard] Background preloading setup failed:', preloadErr);
        }

        // ✅ BACKEND SYNC: Parse MongoDB history instead of localStorage
        const todayStr = getTodayStr();

        // Normalize meal history because backend can return either grouped day objects
        // or flat meal entries depending on write path.
        const normalizedMeals = normalizeMealEntries(data.meals || []);

        // Calculate exact macros eaten TODAY from MongoDB
        let cEaten = 0, pEaten = 0, fEaten = 0, carbEaten = 0;
        // ✅ FIX: Only count meals with actual calories as "completed".
        // Zero-calorie entries from old sessions / partial saves must not inflate mealsLoggedToday.
        const mealsToday = normalizedMeals.filter(m => {
          const d = String(m.date || m.completedAt || '');
          return d.startsWith(todayStr) && (Number(m.calories) > 0);
        });
        mealsToday.forEach(m => {
           cEaten += Number(m.calories) || 0;
           pEaten += Number(m.protein) || 0;
           carbEaten += Number(m.carbs) || 0;
           fEaten += Number(m.fat) || 0;
        });

        // Fallback hydration from local checked/locked state so values persist across
        // refresh/relogin even when backend meal-history write is still catching up.
        try {
          const cachedNutrition = getFromStorage(StorageKeys.NUTRITION_CACHE);
          const checkedFoods = safeJSONParse('checkedFoods', {});
          const lockedMeals = safeJSONParse('lockedMeals', {});
          const todayPlan = cachedNutrition?.days?.find((d) => d?.date === todayStr) || cachedNutrition?.days?.[0];

          if (todayPlan && Array.isArray(todayPlan.meals)) {
            let localCalories = 0;
            let localProtein = 0;
            let localCarbs = 0;
            let localFat = 0;

            todayPlan.meals.forEach((meal) => {
              const mealType = String(meal?.meal_type || '').toLowerCase();
              const mealLocked =
                Boolean(lockedMeals[`${todayStr}-${meal?.name}`])
                || Boolean(mealType && lockedMeals[`${todayStr}-${mealType}`]);

              if (mealLocked) {
                localCalories += Number(meal?.totals?.calories) || 0;
                localProtein += Number(meal?.totals?.protein_g) || 0;
                localCarbs += Number(meal?.totals?.carbs_g) || 0;
                localFat += Number(meal?.totals?.fat_g) || 0;
                return;
              }

              (meal?.foods || []).forEach((food) => {
                if (checkedFoods[`${todayStr}-${food.id}`]) {
                  localCalories += Number(food?.calories) || 0;
                  localProtein += Number(food?.protein_g) || 0;
                  localCarbs += Number(food?.carbs_g) || 0;
                  localFat += Number(food?.fat_g) || 0;
                }
              });
            });

            cEaten = Math.max(cEaten, localCalories);
            pEaten = Math.max(pEaten, localProtein);
            carbEaten = Math.max(carbEaten, localCarbs);
            fEaten = Math.max(fEaten, localFat);
          }
        } catch (macroHydrationError) {
          console.warn('Local macro hydration fallback failed:', macroHydrationError);
        }

        // ✅ FIX: Round all macro values to integers
        cEaten = Math.round(cEaten);
        pEaten = Math.round(pEaten);
        carbEaten = Math.round(carbEaten);
        fEaten = Math.round(fEaten);

        // ✅ FIX: Only use meal_type (not .name) to identify meal type — avoids false positives
        // where old entries with name="Breakfast" (meal_type undefined) are counted as completed.
        const completedMealTypesToday = new Set(
          mealsToday.map((m) => String(m.meal_type || m.mealType || '').toLowerCase()).filter(Boolean)
        );
        // ✅ Count exactly how many of breakfast/lunch/dinner have been logged today (0-3)
        const MAIN_MEALS = ['breakfast', 'lunch', 'dinner'];
        setMealsLoggedToday(MAIN_MEALS.filter(t => completedMealTypesToday.has(t)).length);

        const mealsDoneToday = ['breakfast', 'lunch', 'dinner'].every((type) =>
          completedMealTypesToday.has(type)
        );
        if (mealsDoneToday) {
          setToStorage(StorageKeys.TODAY_MEALS_DONE, 'true');
          const todayDateObj = new Date();
          if (isRestDayForDate(todayDateObj)) {
            // On rest day, meal completion is sufficient to mark day as completed.
            setToStorage(StorageKeys.TODAY_WORKOUT_DONE, 'true');
            setToStorage(StorageKeys.getWorkoutDoneKey(todayStr), 'true');
          }
        }

        // ✅ FIX 1: Macro targets from nutrition plan's daily_target (computed by Python TDEE engine)
        // Priority: cached nutrition plan → goal-based defaults
        let calMax = data.goal === 'Muscle Gain' ? 2800 : data.goal === 'Weight Loss' ? 1800 : 2200;
        let pMax = data.goal === 'Muscle Gain' ? 180 : data.goal === 'Weight Loss' ? 160 : 120;
        let cMax = data.goal === 'Muscle Gain' ? 300 : data.goal === 'Weight Loss' ? 150 : 250;
        let fMax = data.goal === 'Muscle Gain' ? 80 : data.goal === 'Weight Loss' ? 60 : 70;
        try {
          const cachedNutrition = getFromStorage(StorageKeys.NUTRITION_CACHE);
          if (cachedNutrition && cachedNutrition.days && cachedNutrition.days.length > 0) {
            // The meal week is now a fixed Mon–Sun window, so days[0] is Monday — not
            // necessarily today. Pick today's day by date for correct macro targets.
            const todayDay = cachedNutrition.days.find((d) => d?.date === todayStr) || cachedNutrition.days[0];
            const dt = todayDay.daily_totals || cachedNutrition.daily_target;
            if (dt) {
              if (dt.calories && Number(dt.calories) > 0) calMax = Math.round(Number(dt.calories));
              if ((dt.protein_g || dt.protein) && Number(dt.protein_g || dt.protein) > 0) pMax = Math.round(Number(dt.protein_g || dt.protein));
              if ((dt.carbs_g || dt.carbs) && Number(dt.carbs_g || dt.carbs) > 0) cMax = Math.round(Number(dt.carbs_g || dt.carbs));
              if ((dt.fat_g || dt.fat || dt.fats) && Number(dt.fat_g || dt.fat || dt.fats) > 0) fMax = Math.round(Number(dt.fat_g || dt.fat || dt.fats));
            }
          } else if (cachedNutrition && cachedNutrition.daily_target) {
            const dt = cachedNutrition.daily_target;
            if (dt.calories && Number(dt.calories) > 0) calMax = Math.round(Number(dt.calories));
            if (dt.protein && Number(dt.protein) > 0) pMax = Math.round(Number(dt.protein));
            if (dt.carbs && Number(dt.carbs) > 0) cMax = Math.round(Number(dt.carbs));
            if ((dt.fat || dt.fats) && Number(dt.fat || dt.fats) > 0) fMax = Math.round(Number(dt.fat || dt.fats));
          }
        } catch { /* use goal-based defaults as last resort */ }

        setMacros({
          p: pEaten,
          c: carbEaten,
          f: fEaten,
          calories: cEaten,
          remaining: Math.max(0, calMax - cEaten),
          pMax,
          cMax,
          fMax,
          calMax
        });

        const combinedHistory = [];
        (data.workouts || []).forEach(w => {
            combinedHistory.push({
                type: 'workout',
                name: w.focus || w.dayName || 'Completed Workout',
                details: w.exercises_count ? `${w.exercises_count} exercises` : 'Daily Routine',
                date: new Date(w.completedAt || w.date || new Date()).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
                timestamp: new Date(w.completedAt || w.date || new Date()).getTime(),
            });
        });
        normalizedMeals.forEach(m => {
            if (Number(m.calories) > 0) {
                combinedHistory.push({
                    type: 'meal',
                    name: m.name || m.mealType || 'Logged Meal',
                    details: `${Math.round(Number(m.calories) || 0)} cal`,
                    date: new Date(m.completedAt || m.date || new Date()).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
                    timestamp: new Date(m.completedAt || m.date || new Date()).getTime(),
                });
            }
        });
        (Array.isArray(data.recent_activities) ? data.recent_activities : []).forEach((a) => {
          combinedHistory.push({
            type: a?.type || 'activity',
            name: a?.name || 'Activity',
            details: a?.details || '',
            date: a?.date || new Date(a?.timestamp || Date.now()).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
            timestamp: a?.timestamp || new Date().toISOString(),
          });
        });
        const persistedActivities = getFromStorage(StorageKeys.ACTIVITY_HISTORY, []);
        (Array.isArray(persistedActivities) ? persistedActivities : []).forEach((a) => {
          combinedHistory.push(a);
        });

        const deduped = [];
        const dedupeKeySet = new Set();
        combinedHistory.forEach((item) => {
          const ts = item?.timestamp ? new Date(item.timestamp).getTime() : 0;
          const key = `${item?.type || ''}|${item?.name || ''}|${item?.details || ''}|${Number.isFinite(ts) ? ts : item?.date || ''}`;
          if (!dedupeKeySet.has(key)) {
            dedupeKeySet.add(key);
            deduped.push(item);
          }
        });

        deduped.sort((a, b) => {
          const ta = a?.timestamp ? new Date(a.timestamp).getTime() : 0;
          const tb = b?.timestamp ? new Date(b.timestamp).getTime() : 0;
          return tb - ta;
        });

        setRecentHistory(deduped.slice(0, 20));
        setToStorage(StorageKeys.ACTIVITY_HISTORY, deduped.slice(0, 20));

        // ✅ Avatar Sync
        const storedAvatar = getFromStorage(StorageKeys.USER_AVATAR);
        if (storedAvatar) setUserAvatar(storedAvatar);

        // ✅ State Sync from DB Trends (Water, Sleep, Streak)
        if (data.trends && Array.isArray(data.trends)) {
           // Synchronize today's latest data points
           const todayRecord = data.trends.find(t => String(t.date).startsWith(todayStr));
           if (todayRecord) {
             let syncedWater = 0;
             let syncedSleep = 0;
             if (todayRecord.water_intake !== undefined) syncedWater = Number(todayRecord.water_intake);
             else if (todayRecord.water_glasses !== undefined) syncedWater = Number(todayRecord.water_glasses);
             
             if (todayRecord.sleep_duration !== undefined) syncedSleep = Number(todayRecord.sleep_duration);
             else if (todayRecord.sleep_hours !== undefined) syncedSleep = Number(todayRecord.sleep_hours);

             // ✅ KEY FIX: localStorage is updated synchronously on every button click, while the
             // backend lags by the debounce window (500ms). If the user reduced water then
             // quickly refreshed (before the debounce fired), the DB still holds the OLD value.
             // Prefer localStorage for today's session if it holds a valid number.
             const lsWater = parseFloat(localStorage.getItem(StorageKeys.WATER_INTAKE));
             const lsSleep = parseFloat(localStorage.getItem(StorageKeys.SLEEP_HOURS));
             if (Number.isFinite(lsWater)) syncedWater = lsWater;
             if (Number.isFinite(lsSleep)) syncedSleep = lsSleep;
             
             setWater(syncedWater);
             setSleep(syncedSleep);
             // IMPORTANT: initialise lastSaved.current to match whatever we just set into
             // state (localStorage-preferred). This ensures the debounce diff check fires
             // correctly even when the user reduces water back to the same value that is
             // stored in the DB (e.g. add 0→0.25 then remove 0.25→0: if lastSaved were the
             // DB value 0 the diff would be 0===0 and the save would be silently skipped).
             lastSaved.current = { water: syncedWater, sleep: syncedSleep, workout_completed: !!todayRecord?.workout_completed };

            // Sync to Python AI coach on load
            try {
              await saveDailyLog({
                sleep_hours: syncedSleep,
                water_ml: syncedWater * 1000,
                workout_completed: !!todayRecord?.workout_completed
              });
              const weeklyRes = await getWeeklyLogs();
              if (weeklyRes?.data?.success && weeklyRes?.data?.summary) {
                setWeeklyAverages(weeklyRes.data.summary);
              }
            } catch (pyErr) {
              console.warn('Initial Python sync failed', pyErr);
            }

           }

           // ✅ FIX: Advanced Streak Calculation incorporating Rest Days
           // A day is "completed" if meal_completed AND (workout_completed OR isRestDay)
           let currentStreak = 0;
           // Build a map: date-string -> trend entry (pick latest if duplicates)
           const trendsByDate = new Map();
           data.trends.forEach(t => {
             if (t.date) trendsByDate.set(String(t.date).split('T')[0], t);
           });

           const registrationDate = new Date(data.user?.createdAt || data.createdAt || Date.now());
           registrationDate.setHours(0, 0, 0, 0);

           // Walk backwards from today, day by day
           const dateCursor = new Date();
           dateCursor.setHours(0, 0, 0, 0);
           for (let attempts = 0; attempts < 365; attempts++) {
             if (dateCursor < registrationDate) {
               break;
             }

             const dateKey = getLocalDateStr(dateCursor);
             const entry = trendsByDate.get(dateKey);

             if (!entry) {
               if (attempts === 0) {
                 dateCursor.setDate(dateCursor.getDate() - 1);
                 continue;
               }
               break; // No record for this date = streak broken
             }

             const mealDone = !!entry.meal_completed;
             const workoutDone = !!entry.workout_completed;
             // Streak is only extended if user actually completes the main daily tasks.
             const dayCompleted = workoutDone || mealDone;

             if (dayCompleted) {
               currentStreak++;
               dateCursor.setDate(dateCursor.getDate() - 1);
             } else {
               if (attempts === 0) {
                 dateCursor.setDate(dateCursor.getDate() - 1);
                 continue;
               }
               break;
             }
           }
           setStats((prev) => ({ ...prev, streak: currentStreak }));

           // ✅ FIX: Build weekly progress from backend trends data
           const days = ['M', 'T', 'W', 'T', 'F', 'S', 'S'];
           const startOfWeek = new Date();
           const dow = startOfWeek.getDay();
           const diffToMon = startOfWeek.getDate() - dow + (dow === 0 ? -6 : 1);
           startOfWeek.setDate(diffToMon);
           startOfWeek.setHours(0, 0, 0, 0);
           const currentDayIndex = new Date().getDay();
           const ourIdx = currentDayIndex === 0 ? 6 : currentDayIndex - 1;

           const weekData = days.map((day, index) => {
             const dayDate = new Date(startOfWeek);
             dayDate.setDate(startOfWeek.getDate() + index);
             const dateKey = getLocalDateStr(dayDate);
             const entry = trendsByDate.get(dateKey);
             const restDay = isRestDayForDate(dayDate);
             const storedDone = getFromStorage(StorageKeys.getWorkoutDoneKey(dateKey));

             let status = 'pending';
             if (entry) {
               const mDone = !!entry.meal_completed;
               const wDone = !!entry.workout_completed;
               if (mDone && (wDone || restDay)) status = 'done';
               else if (index < ourIdx) status = 'missed';
             } else if (storedDone === 'true') {
               status = 'done';
             } else if (index < ourIdx) {
               status = 'missed';
             }
             return { day, status };
           });
           setWeeklyProgress(weekData);

        } else {
           // Fallback to workout count - Calculate consecutive streak properly
           const workouts = data.workouts || [];
           const completedWorkouts = workouts.filter(w => w.completed || String(w.status).toLowerCase() === 'completed' || w.completedAt);
           const uniqueDays = new Set(completedWorkouts.map(w => (w.completedAt || w.date || '').split('T')[0]));
           let currentStreak = 0;
           const dateCursor = new Date();
           dateCursor.setHours(0, 0, 0, 0);
           for (let i = 0; i < 365; i++) {
             const dateKey = getLocalDateStr(dateCursor);
             if (uniqueDays.has(dateKey)) {
               currentStreak++;
               dateCursor.setDate(dateCursor.getDate() - 1);
             } else {
               if (i === 0) {
                 dateCursor.setDate(dateCursor.getDate() - 1);
                 continue;
               }
               break;
             }
           }
           setStats((prev) => ({ ...prev, streak: currentStreak }));

           // ✅ FIX: Still build weekly progress even without trends
           const days = ['M', 'T', 'W', 'T', 'F', 'S', 'S'];
           const currentDayIndex = new Date().getDay();
           const ourIdx = currentDayIndex === 0 ? 6 : currentDayIndex - 1;
           setWeeklyProgress(days.map((day, i) => ({ day, status: i < ourIdx ? 'missed' : 'pending' })));
        }

        // Derive definitive status
        const todayRecordForStatus = data.trends && Array.isArray(data.trends) ? data.trends.find(t => String(t.date).startsWith(todayStr)) : null;
        let finalWorkoutDone = todayRecordForStatus ? !!todayRecordForStatus.workout_completed : false;
        let finalMealDone = todayRecordForStatus ? !!todayRecordForStatus.meal_completed : false;
        
        // Fallback calculations if trend data is lagging
        const workoutsTodayArray = (data.workouts || []).filter((w) => {
          const workoutDate = String(w.completedAt || w.date || '');
          if (!workoutDate.startsWith(todayStr)) return false;

          // Only completed workout records should count toward today's done status.
          const hasCompletionTimestamp = Boolean(w.completedAt);
          const explicitCompleted = String(w.status || '').toLowerCase() === 'completed' || w.completed === true;
          return hasCompletionTimestamp || explicitCompleted;
        });
        if (workoutsTodayArray.length > 0) finalWorkoutDone = true;
        if (mealsDoneToday) finalMealDone = true;

        if (finalWorkoutDone) {
            setToStorage(StorageKeys.TODAY_WORKOUT_DONE, 'true');
            setToStorage(StorageKeys.getWorkoutDoneKey(todayStr), 'true');
        }
        if (finalMealDone) {
            setToStorage(StorageKeys.TODAY_MEALS_DONE, 'true');
        }
        
        // Fetch weekly averages for adaptive coaching card
        try {
          const weeklyRes = await getWeeklyLogs();
          if (weeklyRes?.data?.success && weeklyRes?.data?.summary) {
            setWeeklyAverages(weeklyRes.data.summary);
          }
        } catch (weeklyErr) {
          console.warn('Failed to load weekly logs for AI Coach:', weeklyErr);
        }
        
        return { workoutDone: finalWorkoutDone, mealDone: finalMealDone };
      } catch (error) {
        console.error('Error fetching profile:', error);
        const status = error?.response?.status;
        if (status === 401 || status === 403) {
          navigate('/login', { replace: true });
        } else {
          showInfo('Could not sync latest dashboard data. Showing last known state.', 3000);
        }
        return null;
      } finally {
        setLoading(false);
      }
    };

    fetchUserData().then((derivedStatus) => {
      // Run daily reset AFTER backend data is loaded.
      // NOTE: checkDailyReset no longer zeroes macros — DB values are authoritative.
      checkDailyReset();
      // ✅ FIX: Call checkDayReset to properly set workout→meal→done status flow
      if (derivedStatus) {
         checkDayReset(derivedStatus.workoutDone, derivedStatus.mealDone);
      } else {
         checkDayReset();
      }
    });
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [navigate]);

  // ✅ NEW: Load activities from backend on mount
  useEffect(() => {
    loadActivitiesFromBackend();
  }, []);

  // Session recovery on mount
  useEffect(() => {
    const recoverSession = () => {
      try {
        // ✅ UPDATED: Use storage utility
        const lastWorkoutDate = getFromStorage(StorageKeys.LAST_WORKOUT_DATE);
        const todayStr = getTodayStr();
        if (lastWorkoutDate === todayStr) {
          // ✅ UPDATED: Use storage utility
          const todayWorkoutDone = getFromStorage(StorageKeys.TODAY_WORKOUT_DONE);
          if (!todayWorkoutDone) {
            console.log('Detected incomplete workout session for today, resetting status');
          }
        }
      } catch (error) {
        console.error('Error in session recovery:', error);
      }
    };
    recoverSession();
  }, []);

  // ✅ FIXED: Daily reset logic with storage utilities
  // BUG WAS HERE: The old condition `lastActivityDate !== today || dailyResetPerformed !== today`
  // would fire on EVERY fresh login (when keys don't exist in storage), wiping
  // TODAY_WORKOUT_DONE / TODAY_MEALS_DONE even though the day hadn't changed.
  //
  // FIX: Only clear session flags when lastActivityDate exists AND is a DIFFERENT day
  // (i.e. the user is logging in on a new calendar day). On a fresh login same day,
  // just write the tracking keys without clearing anything.
  const checkDailyReset = async () => {
    try {
      const today = getTodayStr();
      const lastActivityDate = getFromStorage(StorageKeys.LAST_ACTIVITY_DATE);

      // ✅ KEY FIX: only reset if we KNOW it was a different day previously
      const isNewDay = lastActivityDate && lastActivityDate !== today;

      // Always stamp today so future checks detect a new day correctly
      setToStorage(StorageKeys.LAST_ACTIVITY_DATE, today);
      setToStorage(StorageKeys.DAILY_RESET_PERFORMED, today);

      if (isNewDay) {
        // A real calendar day has rolled over — clear yesterday's session state
        setNotifications([]);
        removeFromStorage(StorageKeys.TODAY_WORKOUT_DONE);
        removeFromStorage(StorageKeys.TODAY_MEALS_DONE);

        // Clear notification flags for the old day
        const keysToRemove = [];
        for (let i = 0; i < localStorage.length; i++) {
          const key = localStorage.key(i);
          if (key && (key.includes('notification_') || key.includes('reminder_'))) {
            keysToRemove.push(key);
          }
        }
        keysToRemove.forEach(k => removeFromStorage(k));
      }
      // If lastActivityDate is null/empty (first login ever) OR same as today,
      // do NOT clear any flags — the backend data loaded by fetchUserData() is authoritative.
    } catch (error) {
      console.error('Error in checkDailyReset:', error);
      showInfo('There was an issue checking for daily reset. Please try again later.', 3000);
    }
  };


  // ✅ FIX 2: Cross-page macro sync — re-fetch today's data when user returns to Dashboard
  useEffect(() => {
    const handlePageVisibilityChange = async () => {
      if (!document.hidden) {
        checkDailyReset();
        try {
          // Re-fetch profile to get updated meal data (e.g., after completing meals on Nutrition page)
          const { data } = await getProfile();
          const todayStr = getTodayStr();
          const normalizedMeals = normalizeMealEntries(data.meals || []);
          let cEaten = 0, pEaten = 0, carbEaten = 0, fEaten = 0;
          // ✅ FIX: Same calories>0 guard as in fetchUserData — only real meals count
          const mealsToday = normalizedMeals.filter(m => {
            const d = String(m.date || m.completedAt || '');
            return d.startsWith(todayStr) && (Number(m.calories) > 0);
          });
          mealsToday.forEach(m => {
            cEaten += Number(m.calories) || 0;
            pEaten += Number(m.protein) || 0;
            carbEaten += Number(m.carbs) || 0;
            fEaten += Number(m.fat) || 0;
          });
          setMacros(prev => ({
            ...prev,
            p: Math.round(pEaten),
            c: Math.round(carbEaten),
            f: Math.round(fEaten),
            calories: Math.round(cEaten),
            remaining: Math.max(0, prev.calMax - Math.round(cEaten)),
          }));
          // ✅ PA-6: Also refresh the chart so it reflects latest data
          updateChart(chartMode, chartPeriod);

          // ✅ FIX: Re-evaluate central button status using fresh backend data.
          // This ensures when user returns from Nutrition page after completing meals,
          // the button correctly shows "START WORKOUT" instead of "ALL SET".
          const todayTrend = data.trends && Array.isArray(data.trends)
            ? data.trends.find(t => String(t.date).startsWith(todayStr))
            : null;
          const workoutsTodayVis = (data.workouts || []).filter(w => {
            const wd = String(w.completedAt || w.date || '');
            return wd.startsWith(todayStr) && (Boolean(w.completedAt) || String(w.status || '').toLowerCase() === 'completed' || w.completed === true);
          });
          // ✅ FIX: Only use meal_type (not .name) so old flat entries don\'t produce false meal counts
          const completedMealTypes = new Set(
            mealsToday.map(m => String(m.meal_type || m.mealType || '').toLowerCase()).filter(Boolean)
          );
          const mealsDone = ['breakfast', 'lunch', 'dinner'].every(t => completedMealTypes.has(t));
          // ✅ Keep mealsLoggedToday in sync after visibility refresh
          const MAIN_MEALS_VIS = ['breakfast', 'lunch', 'dinner'];
          setMealsLoggedToday(MAIN_MEALS_VIS.filter(t => completedMealTypes.has(t)).length);

          let visFinalWorkoutDone = todayTrend ? !!todayTrend.workout_completed : false;
          let visFinalMealDone = todayTrend ? !!todayTrend.meal_completed : false;
          if (workoutsTodayVis.length > 0) visFinalWorkoutDone = true;
          if (mealsDone) visFinalMealDone = true;

          checkDayReset(visFinalWorkoutDone, visFinalMealDone);
        } catch (err) {
          console.error('Visibility sync error:', err);
        }
      }
    };
   document.addEventListener('visibilitychange', handlePageVisibilityChange);
    return () => document.removeEventListener('visibilitychange', handlePageVisibilityChange);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  // ✅ BUG FIX: Listen for macro sync from Nutrition page via localStorage 'storage' event
  // Also handles mealsCount key so the progress circle updates immediately per-meal.
  useEffect(() => {
    const handleStorageSync = (e) => {
      if (e.key === '_macroSync' && e.newValue) {
        try {
          const totals = JSON.parse(e.newValue);
          if (totals && totals.calories !== undefined) {
            setMacros(prev => ({
              ...prev,
              p: Math.round(Number(totals.protein) || prev.p),
              c: Math.round(Number(totals.carbs) || prev.c),
              f: Math.round(Number(totals.fat) || prev.f),
              calories: Math.round(Number(totals.calories) || prev.calories),
              remaining: Math.max(0, prev.calMax - Math.round(Number(totals.calories) || prev.calories)),
            }));
            // ✅ If Nutrition page signals the meal count, update circle immediately
            if (totals.mealsCount !== undefined) {
              setMealsLoggedToday(Math.min(3, Math.max(0, Number(totals.mealsCount) || 0)));
            }
            console.log('✅ Dashboard macros updated from Nutrition sync:', totals);
          }
        } catch (error) {
          console.warn('[Dashboard] Failed to parse _macroSync data:', error);
        }
      }
      // ✅ Listen for exercise-by-exercise workout progress from Workout page
      if (e.key === '_workoutSync' && e.newValue) {
        try {
          const data = JSON.parse(e.newValue);
          if (data && data.totalCount > 0) {
            const ratio = Math.min(1, data.completedCount / data.totalCount);
            setWorkoutProgress(ratio);
            console.log(`✅ Workout progress: ${data.completedCount}/${data.totalCount} (${Math.round(ratio * 100)}%)`);
          }
        } catch (error) {
          console.warn('[Dashboard] Failed to parse _workoutSync data:', error);
        }
      }
    };
    window.addEventListener('storage', handleStorageSync);
    return () => window.removeEventListener('storage', handleStorageSync);
  }, []);

  const addNotification = useCallback((message, type = 'info') => {
    const id = Date.now() + Math.random();
    const newNotification = {
      id,
      message,
      type,
      timestamp: new Date()
    };
    setNotifications((prev) => [...prev, newNotification]);
    setActiveToasts((prev) => [...prev, newNotification]);
    setTimeout(
      () => setActiveToasts((prev) => prev.filter((t) => t.id !== id)),
      5000
    );
  }, []);

  const dismissNotification = (id) =>
    setNotifications((prev) => prev.filter((n) => n.id !== id));

  const dismissToast = (id) => {
    setActiveToasts((prev) => prev.filter((t) => t.id !== id));
    dismissNotification(id);
  };

  // ✅ FIXED: logActivity uses storage utility AND saves to backend
  // Added ISO timestamp so deduplication works correctly in loadActivitiesFromBackend
  const logActivity = async (type, name, details) => {
    const now = new Date();
    const newLog = {
      name,
      date: now.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
      details,
      type,
      timestamp: now.toISOString()  // ← required for deduplication & sorting
    };

    // Update local state and storage first (for immediate UI feedback)
    setRecentHistory((prev) => {
      const updated = [newLog, ...prev];
      setToStorage(StorageKeys.ACTIVITY_HISTORY, updated);
      return updated;
    });

    // Also save to backend for persistence across sessions
    try {
      await logActivityToBackend({
        activity_type: type,
        name,
        details,
        type,
        timestamp: newLog.timestamp
      });
    } catch (error) {
      // Don't break the UI if backend logging fails
      console.warn('Failed to log activity to backend:', error);
    }
  };


  const removeLastLog = (type) => {
    setRecentHistory((prev) => {
      const index = prev.findIndex((item) => item.type === type);
      if (index !== -1) {
        const newHistory = [...prev];
        newHistory.splice(index, 1);
        setToStorage(StorageKeys.ACTIVITY_HISTORY, newHistory);
        return newHistory;
      }
      return prev;
    });
  };

  // ✅ NEW: Load activities from backend on mount
  const loadActivitiesFromBackend = async () => {
    const localActivities = getFromStorage(StorageKeys.ACTIVITY_HISTORY, []);

    try {
      if (Array.isArray(localActivities) && localActivities.length > 0) {
        try {
          await syncActivitiesToBackend(localActivities);
        } catch (syncError) {
          console.warn('Failed to sync local activities to backend:', syncError);
        }
      }

      const response = await getRecentActivities(20);
      if (response.data && response.data.success && Array.isArray(response.data.data)) {
        const backendActivities = response.data.data;

        // Merge with local storage activities (in case some were logged while offline)

        // Create a map to deduplicate by type/name/details/timestamp
        const activityMap = new Map();

        // Add backend activities first (they're the authoritative source)
        backendActivities.forEach(activity => {
          const ts = activity?.timestamp ? new Date(activity.timestamp).getTime() : 0;
          const key = `${activity?.type || ''}|${activity?.name || ''}|${activity?.details || ''}|${Number.isFinite(ts) ? ts : activity?.date || ''}`;
          activityMap.set(key, activity);
        });

        // Add local activities that might not be synced yet
        localActivities.forEach(activity => {
          const ts = activity?.timestamp ? new Date(activity.timestamp).getTime() : 0;
          const key = `${activity?.type || ''}|${activity?.name || ''}|${activity?.details || ''}|${Number.isFinite(ts) ? ts : activity?.date || ''}`;
          if (!activityMap.has(key)) {
            activityMap.set(key, activity);
          }
        });

        // Convert to array and sort by timestamp (most recent first)
        const merged = Array.from(activityMap.values());
        merged.sort((a, b) => {
          const timeA = a.timestamp ? new Date(a.timestamp).getTime() : 0;
          const timeB = b.timestamp ? new Date(b.timestamp).getTime() : 0;
          return timeB - timeA;
        });

        // Update state and localStorage
        setRecentHistory(merged.slice(0, 20));
        setToStorage(StorageKeys.ACTIVITY_HISTORY, merged.slice(0, 20));
      }
    } catch (error) {
      console.warn('Failed to load activities from backend:', error);
      // Fall back to localStorage if backend fails
      const localActivities = getFromStorage(StorageKeys.ACTIVITY_HISTORY, []);
      setRecentHistory(localActivities);
    }
  };

  // ✅ UPDATED: Notification tracking with storage utilities
  const hasNotificationBeenShownToday = (notificationId) => {
    const todayStr = getTodayStr();
    const lastShownDate = getFromStorage(StorageKeys.getNotificationKey(notificationId));
    return lastShownDate === todayStr;
  };

  const markNotificationAsShownToday = (notificationId) => {
    const todayStr = getTodayStr();
    setToStorage(StorageKeys.getNotificationKey(notificationId), todayStr);
  };

  const checkWaterThresholdNotifications = useCallback((oldWater, newWater) => {
    try {
      const userWeight = parseFloat(safeJSONParse('user', {})?.weight || '70');
      const _isWkDone = (typeof status !== "undefined" && (status === "done" || status === "meal")) || (typeof workoutProgress !== "undefined" && workoutProgress === 1);
    const waterGoal = getDynamicWaterGoal(typeof userWeight !== "undefined" ? userWeight : 70, typeof sleep !== "undefined" ? sleep : 0, _isWkDone);
      const halfGoal = parseFloat((waterGoal / 2).toFixed(1));

      if (
        oldWater < halfGoal &&
        newWater >= halfGoal &&
        newWater < waterGoal &&
        !hasNotificationBeenShownToday('water-status')
      ) {
        addNotification(
          `Halfway there! 💧 ${newWater.toFixed(1)}L of ${waterGoal}L — keep drinking!`,
          'info'
        );
        markNotificationAsShownToday('water-status');
      }
      if (
        oldWater < waterGoal &&
        newWater >= waterGoal &&
        !hasNotificationBeenShownToday('water-goal')
      ) {
        addNotification(
          `🎉 Daily hydration goal reached! ${newWater.toFixed(1)}L of ${waterGoal}L.`,
          'success'
        );
        markNotificationAsShownToday('water-goal');
        setShowWaterCelebration(true);
        setTimeout(() => setShowWaterCelebration(false), 4000);
      }
    } catch (error) {
      console.error('Error in checkWaterThresholdNotifications:', error);
    }
  }, [addNotification]);

  const checkSleepThresholdNotifications = useCallback((oldSleep, newSleep) => {
    try {
      if (
        oldSleep < 7.0 &&
        newSleep >= 7.0 &&
        newSleep <= 9.0 &&
        !hasNotificationBeenShownToday('sleep-minimum')
      ) {
        addNotification(
          `Good job! You've reached the recommended sleep of ${newSleep.toFixed(1)}h. Your body recovers best between 7-9 hours.`,
          'success'
        );
        markNotificationAsShownToday('sleep-minimum');
        setShowSleepCelebration(true);
        setTimeout(() => setShowSleepCelebration(false), 4000);
      }
      if (
        oldSleep <= 9.0 &&
        newSleep > 9.0 &&
        !hasNotificationBeenShownToday('sleep-maximum')
      ) {
        addNotification(
          `You've exceeded the recommended maximum sleep of 9.0h. Current: ${newSleep.toFixed(1)}h. Oversleeping can impact energy levels.`,
          'warning'
        );
        markNotificationAsShownToday('sleep-maximum');
      }
    } catch (error) {
      console.error('Error in checkSleepThresholdNotifications:', error);
    }
  }, [addNotification]);

  // ✅ UPDATED: Reminder tracking with storage utilities
  const hasDailyReminderBeenShown = (reminderType) => {
    const todayStr = getTodayStr();
    const lastShownDate = getFromStorage(StorageKeys.getReminderKey(reminderType));
    return lastShownDate === todayStr;
  };

  const markDailyReminderAsShown = (reminderType) => {
    const todayStr = getTodayStr();
    setToStorage(StorageKeys.getReminderKey(reminderType), todayStr);
  };

  const checkDailyReminders = () => {
    try {
      if (loading) return;
      const todayStr = getTodayStr();
      if (lastNotificationCheck === todayStr) return;
      setLastNotificationCheck(todayStr);

      const currentHour = new Date().getHours();
      if (currentHour >= 20 && !hasDailyReminderBeenShown('sleep')) {
        if (sleep < 7.0) {
          const newNotification = {
            id: `sleep-reminder-${todayStr}`,
            type: 'warning',
            message: `It's getting late. Remember to get enough sleep tonight for better recovery tomorrow. Current sleep: ${sleep.toFixed(1)}h/7.0h.`,
            timestamp: new Date()
          };
          setNotifications((prev) => {
            const exists = prev.some((n) => n.id === newNotification.id);
            if (exists) return prev;
            markDailyReminderAsShown('sleep');
            return [...prev, newNotification].slice(-5);
          });
        } else {
          markDailyReminderAsShown('sleep');
        }
      }

      // Morning hydration reminder
      if (currentHour < 10 && !hasDailyReminderBeenShown('water')) {
        const userWeight = parseFloat(safeJSONParse('user', {})?.weight || '70');
        const _isWkDone = (typeof status !== "undefined" && (status === "done" || status === "meal")) || (typeof workoutProgress !== "undefined" && workoutProgress === 1);
    const waterGoal = getDynamicWaterGoal(typeof userWeight !== "undefined" ? userWeight : 70, typeof sleep !== "undefined" ? sleep : 0, _isWkDone);
        if (water < 0.5) {
          const newNotification = {
            id: `water-reminder-${todayStr}`,
            type: 'info',
            message: `☀️ Good morning! Start hydrating — your daily goal is ${waterGoal}L based on your weight.`,
            timestamp: new Date()
          };
          setNotifications((prev) => {
            const exists = prev.some((n) => n.id === newNotification.id);
            if (exists) return prev;
            markDailyReminderAsShown('water');
            return [...prev, newNotification].slice(-5);
          });
        } else {
          markDailyReminderAsShown('water');
        }
      }

      // Afternoon hydration check
      if (currentHour >= 14 && currentHour < 16 && !hasDailyReminderBeenShown('water-afternoon')) {
        const userWeight = parseFloat(safeJSONParse('user', {})?.weight || '70');
        const _isWkDone = (typeof status !== "undefined" && (status === "done" || status === "meal")) || (typeof workoutProgress !== "undefined" && workoutProgress === 1);
    const waterGoal = getDynamicWaterGoal(typeof userWeight !== "undefined" ? userWeight : 70, typeof sleep !== "undefined" ? sleep : 0, _isWkDone);
        if (water < waterGoal * 0.5) {
          const newNotification = {
            id: `water-afternoon-${todayStr}`,
            type: 'warning',
            message: `⚠️ You're behind on hydration! ${water.toFixed(1)}L of ${waterGoal}L — try to catch up before evening.`,
            timestamp: new Date()
          };
          setNotifications((prev) => {
            const exists = prev.some((n) => n.id === newNotification.id);
            if (exists) return prev;
            markDailyReminderAsShown('water-afternoon');
            return [...prev, newNotification].slice(-5);
          });
        } else {
          markDailyReminderAsShown('water-afternoon');
        }
      }
    } catch (error) {
      console.error('Error in checkDailyReminders:', error);
      showInfo(
        'There was an issue checking your daily reminders. Please try again later.',
        3000
      );
    }
  };

  useEffect(() => {
    if (!loading) {
      checkDailyReminders();
    }
    const interval = setInterval(() => {
      if (!loading) {
        checkDailyReminders();
      }
    }, 60 * 60 * 1000);
    return () => clearInterval(interval);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [loading]);

  // Removed: Empty resize listener that did nothing (was a waste of resources)

  const checkInterruptedSessions = () => {
    try {
      const todayStr = getTodayStr();
      // ✅ UPDATED: Use storage utility
      const ongoingWorkout = getFromStorage(StorageKeys.ONGOING_WORKOUT);
      if (ongoingWorkout) {
        try {
          if (ongoingWorkout.date === todayStr) {
            showInfo(
              'Previous workout session was interrupted. Resume where you left off or start fresh?',
              5000
            );
          } else {
            removeFromStorage(StorageKeys.ONGOING_WORKOUT);
          }
        } catch {
          removeFromStorage(StorageKeys.ONGOING_WORKOUT);
        }
      }
    } catch (error) {
      console.error('Error checking for interrupted sessions:', error);
    }
  };

  // ✅ UPDATED: Workout session management with storage utilities
  const startWorkoutSession = (sessionDetails = null) => {
    try {
      const todayStr = getTodayStr();
      const sessionData = {
        date: todayStr,
        startTime: new Date().toISOString(),
        details: sessionDetails || {}
      };
      setToStorage(StorageKeys.ONGOING_WORKOUT, sessionData);
    } catch (error) {
      console.error('Error starting workout session:', error);
    }
  };

  const endWorkoutSession = () => {
    try {
      removeFromStorage(StorageKeys.ONGOING_WORKOUT);
    } catch (error) {
      console.error('Error ending workout session:', error);
    }
  };

  useEffect(() => {
    updateChart(chartMode, chartPeriod);
    // updateChart is intentionally excluded to avoid effect loops from function identity changes.
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [chartMode, chartPeriod]);

  // Separate lightweight local-only chart update for water/sleep/all live changes
  useEffect(() => {
    if (chartMode === 'water' || chartMode === 'sleep' || chartMode === 'all') {
      setChartData(prev => {
        const next = [...prev];
        const todayJsDay = new Date().getDay();
        const todayIdx = todayJsDay === 0 ? 6 : todayJsDay - 1;
        if (chartMode === 'water') next[todayIdx] = water;
        if (chartMode === 'sleep') next[todayIdx] = sleep;
        if (chartMode === 'all') next[todayIdx] = dailyProgress;
        return next;
      });
    }
  }, [water, sleep, dailyProgress, chartMode]);

  // ✅ FIXED: Debounce-sync water & sleep to MongoDB trends
  // BUG WAS HERE: lastSaved.current was written BEFORE the async save completed.
  // If saveTrends() silently failed, the ref already matched the new values so the
  // next button click produced no diff and the save was never retried.
  //
  // FIX: Only update the ref on success; roll it back on failure so the next
  // state change (or page visibility change) re-triggers the save attempt.
  useEffect(() => {
    const workout_completed = status === 'done' || status === 'meal' || workoutProgress === 1;
    if (
      water === lastSaved.current.water &&
      sleep === lastSaved.current.sleep &&
      workout_completed === lastSaved.current.workout_completed
    ) {
      return;
    }

    const prevSaved = { ...lastSaved.current }; // snapshot before timer fires

    const timer = setTimeout(async () => {
      const todayStr = getTodayStr();
      // Optimistically record what we're about to save
      lastSaved.current = { water, sleep, workout_completed };
      try {
        await saveTrends({
          date: todayStr,
          water_intake: water,
          water_glasses: water,
          sleep_duration: sleep,
          sleep_hours: sleep,
          workout_completed: workout_completed,
        });

        // Sync with the Python daily logs backend
        try {
          await saveDailyLog({
            sleep_hours: sleep,
            water_ml: water * 1000, // liters to ml
            workout_completed: workout_completed,
            date: todayStr,
          });

          // Re-fetch weekly logs to update dashboard card
          const weeklyRes = await getWeeklyLogs();
          if (weeklyRes?.data?.success && weeklyRes?.data?.summary) {
            setWeeklyAverages(weeklyRes.data.summary);
          }
        } catch (pyErr) {
          console.warn('Python daily log sync failed:', pyErr);
        }
      } catch (err) {
        console.error('Failed to sync water/sleep/workout to backend:', err);
        // Roll back so the next value change will retry the write
        lastSaved.current = prevSaved;
      }
    }, 500); // 0.5 second debounce — short enough to beat a quick page refresh

    return () => clearTimeout(timer);
  }, [water, sleep, status, workoutProgress]);


  const updateRecoveryScore = (currentWater, currentSleep) => {
    const userWeight = parseFloat(safeJSONParse('user', {})?.weight || '70');
    const _isWkDone = (typeof status !== "undefined" && (status === "done" || status === "meal")) || (typeof workoutProgress !== "undefined" && workoutProgress === 1);
    const waterGoal = getDynamicWaterGoal(typeof userWeight !== "undefined" ? userWeight : 70, typeof sleep !== "undefined" ? sleep : 0, _isWkDone);
    const waterScore = Math.min(100, (currentWater / waterGoal) * 100);
    const sleepScore = Math.min(100, (currentSleep / 9.0) * 100);
    const newRecoveryScore = Math.round((waterScore + sleepScore) / 2);
    setRecoveryScore(newRecoveryScore);
    let score =
      50 +
      Math.min(currentSleep * 4, 32) +
      Math.min(currentWater * 6, 18) +
      newRecoveryScore * 0.2;
    if (score > 100) score = 100;
    setStats((prev) => ({ ...prev, focusScore: Math.floor(score) }));
  };

   // ✅ FIX 4: Use StorageKeys for water persistence
   const handleWaterAdd = useCallback(() => {
    const newWaterValue = parseFloat((water + 0.25).toFixed(2));
    checkWaterThresholdNotifications(water, newWaterValue);
    setWater(newWaterValue);
    setToStorage(StorageKeys.WATER_INTAKE, String(newWaterValue));
      const userWeight = parseFloat(safeJSONParse('user', {})?.weight || '70');
      const _isWkDone = (typeof status !== "undefined" && (status === "done" || status === "meal")) || (typeof workoutProgress !== "undefined" && workoutProgress === 1);
    const waterGoal = getDynamicWaterGoal(typeof userWeight !== "undefined" ? userWeight : 70, typeof sleep !== "undefined" ? sleep : 0, _isWkDone);
      const percentage = Math.min(100, (newWaterValue / waterGoal) * 100);
      syncBridge.emit(SyncTypes.WATER_ADDED, {
        amount: newWaterValue,
        previousAmount: water,
        percentage,
        glasses: Math.floor(newWaterValue / 0.25),
      });
    logActivity('water', 'Hydration', '+250ml Water');
    updateRecoveryScore(newWaterValue, sleep);
  }, [water, sleep, checkWaterThresholdNotifications]);

  const handleWaterRemove = useCallback(() => {
    if (water > 0) {
      const newWaterValue = parseFloat(Math.max(0, water - 0.25).toFixed(2));
      checkWaterThresholdNotifications(water, newWaterValue);
      setWater(newWaterValue);
      setToStorage(StorageKeys.WATER_INTAKE, String(newWaterValue));
      const userWeight = parseFloat(safeJSONParse('user', {})?.weight || '70');
      const _isWkDone = (typeof status !== "undefined" && (status === "done" || status === "meal")) || (typeof workoutProgress !== "undefined" && workoutProgress === 1);
    const waterGoal = getDynamicWaterGoal(typeof userWeight !== "undefined" ? userWeight : 70, typeof sleep !== "undefined" ? sleep : 0, _isWkDone);
      const percentage = Math.min(100, (newWaterValue / waterGoal) * 100);
      syncBridge.emit(SyncTypes.WATER_ADDED, {
        amount: newWaterValue,
        previousAmount: water,
        percentage,
        glasses: Math.floor(newWaterValue / 0.25),
      });
      removeLastLog('water');
      updateRecoveryScore(newWaterValue, sleep);
    }
  }, [water, sleep, checkWaterThresholdNotifications]);

  // ✅ UPDATED: useCallback for sleep handlers
  // ✅ FIX 4: Use StorageKeys for sleep persistence
  const handleSleepAdd = useCallback(() => {
    const newSleepValue = parseFloat((sleep + 0.5).toFixed(1));
    checkSleepThresholdNotifications(sleep, newSleepValue);
    setSleep(newSleepValue);
    setToStorage(StorageKeys.SLEEP_HOURS, String(newSleepValue));
    syncBridge.emit(SyncTypes.SLEEP_UPDATED, {
      hours: newSleepValue,
      previousHours: sleep,
    });
    logActivity('sleep', 'Sleep Update', '+30 min sleep logged');
    updateRecoveryScore(water, newSleepValue);
  }, [sleep, water, checkSleepThresholdNotifications]);

  const handleSleepRemove = useCallback(() => {
    if (sleep > 0) {
      const newSleepValue = parseFloat(Math.max(0, sleep - 0.5).toFixed(1));
      checkSleepThresholdNotifications(sleep, newSleepValue);
      setSleep(newSleepValue);
      setToStorage(StorageKeys.SLEEP_HOURS, String(newSleepValue));
      syncBridge.emit(SyncTypes.SLEEP_UPDATED, {
        hours: newSleepValue,
        previousHours: sleep,
      });
      removeLastLog('sleep');
      updateRecoveryScore(water, newSleepValue);
    }
  }, [sleep, water, checkSleepThresholdNotifications]);

  const fetchExternalNutritionData = async (foodQuery) => {
    try {
      // Using USDA FoodData Central API (Requires API key)
      const apiKey = import.meta.env.VITE_USDA_API_KEY;

      if (!apiKey) {
        console.warn('USDA API key not configured, using fallback nutrition data');
        // Return mock nutrition data as fallback
        return {
          food_name: foodQuery,
          calories: 0,
          protein: 0,
          carbs: 0,
          fat: 0,
          fiber: 0,
          serving_weight_grams: 100,
          source: 'fallback',
          nix_item_name: foodQuery,
          full_nutrients: []
        };
      }

      const controller = new AbortController();
      const timeoutId = setTimeout(() => controller.abort(), 10000);

      const response = await fetch(
        `https://api.nal.usda.gov/fdc/v1/foods/search?query=${encodeURIComponent(foodQuery)}&pageSize=1&api_key=${apiKey}`,
        {
          method: 'GET',
          headers: {
            'Content-Type': 'application/json'
          },
          signal: controller.signal
        }
      );

      clearTimeout(timeoutId);

      if (!response.ok) {
        console.warn(`USDA API returned status ${response.status}`);
        // Return fallback data if API fails
        return {
          food_name: foodQuery,
          calories: 0,
          protein: 0,
          carbs: 0,
          fat: 0,
          fiber: 0,
          serving_weight_grams: 100,
          source: 'fallback',
          nix_item_name: foodQuery,
          full_nutrients: []
        };
      }

      const data = await response.json();

      if (!data.foods || data.foods.length === 0) {
        console.warn('USDA API returned no results for:', foodQuery);
        return {
          food_name: foodQuery,
          calories: 0,
          protein: 0,
          carbs: 0,
          fat: 0,
          fiber: 0,
          serving_weight_grams: 100,
          source: 'fallback',
          nix_item_name: foodQuery,
          full_nutrients: []
        };
      }

      const food = data.foods[0];

      // Extract nutrients from USDA format
      const getNutrient = (nutrientId) => {
        const nutrient = food.foodNutrients?.find(
          n => n.nutrient?.id === nutrientId
        );
        return nutrient?.value || 0;
      };

      // USDA Nutrient IDs:
      // 1008 = Energy (kcal)
      // 1003 = Protein (g)
      // 1005 = Carbohydrate (g)
      // 1004 = Fat (g)
      // 1079 = Fiber (g)

      return {
        food_name: food.description,
        calories: getNutrient(1008) || 0,
        protein: getNutrient(1003) || 0,
        carbs: getNutrient(1005) || 0,
        fat: getNutrient(1004) || 0,
        fiber: getNutrient(1079) || 0,
        serving_weight_grams: 100,
        source: 'USDA FoodData Central',
        nix_item_name: food.description,
        full_nutrients: food.foodNutrients || []
      };
    } catch (error) {
      if (error.name === 'AbortError') {
        console.warn('USDA API request timeout');
      } else {
        console.error('USDA API error:', error.message);
      }
      // Return fallback data on error
      return {
        food_name: foodQuery || 'unknown food',
        calories: 0,
        protein: 0,
        carbs: 0,
        fat: 0,
        fiber: 0,
        serving_weight_grams: 100,
        source: 'fallback',
        nix_item_name: foodQuery || 'unknown food',
        full_nutrients: []
      };
    }
  };

  const fetchExternalExerciseData = async (exerciseQuery) => {
    try {
      const apiKey = import.meta.env.VITE_API_NINJAS_KEY;

      if (!apiKey) {
        console.warn('API Ninjas credentials not configured, using fallback exercise data');
        // Return mock exercise data as fallback
        return [{
          name: exerciseQuery || 'generic exercise',
          type: 'strength',
          muscle: exerciseQuery || 'mixed',
          equipment: 'bodyweight',
          difficulty: 'beginner',
          instructions: 'Perform the exercise with proper form'
        }];
      }

      const controller = new AbortController();
      const timeoutId = setTimeout(() => controller.abort(), 10000);

      const response = await fetch(
        `https://api.api-ninjas.com/v1/exercises?muscle=${encodeURIComponent(exerciseQuery)}`,
        {
          headers: { 'X-Api-Key': apiKey },
          signal: controller.signal
        }
      );

      clearTimeout(timeoutId);

      if (!response.ok) {
        console.warn(`API Ninjas returned status ${response.status}`);
        // Return fallback data if API fails
        return [{
          name: exerciseQuery || 'generic exercise',
          type: 'strength',
          muscle: exerciseQuery || 'mixed',
          equipment: 'bodyweight',
          difficulty: 'beginner',
          instructions: 'Perform the exercise with proper form'
        }];
      }

      const data = await response.json();

      if (!Array.isArray(data) || data.length === 0) {
        console.warn('API Ninjas returned no exercise data');
        return [{
          name: exerciseQuery || 'generic exercise',
          type: 'strength',
          muscle: exerciseQuery || 'mixed',
          equipment: 'bodyweight',
          difficulty: 'beginner',
          instructions: 'Perform the exercise with proper form'
        }];
      }

      return data;
    } catch (error) {
      if (error.name === 'AbortError') {
        console.warn('API Ninjas request timeout, using fallback data');
      } else {
        console.error('API Ninjas error:', error.message);
      }
      // Return fallback data on error
      return [{
        name: exerciseQuery || 'generic exercise',
        type: 'strength',
        muscle: exerciseQuery || 'mixed',
        equipment: 'bodyweight',
        difficulty: 'beginner',
        instructions: 'Perform the exercise with proper form'
      }];
    }
  };

  const enrichDataWithExternalAPIs = async () => {
    try {
      const [nutritionEnrichment, exerciseEnrichment] = await Promise.allSettled([
        fetchExternalNutritionData('chicken breast'),
        fetchExternalExerciseData('biceps')
      ]);

      return {
        nutrition:
          nutritionEnrichment.status === 'fulfilled' ? nutritionEnrichment.value : null,
        exercise:
          exerciseEnrichment.status === 'fulfilled' ? exerciseEnrichment.value : null
      };
    } catch (error) {
      console.error('Error enriching data with external APIs:', error.message);
      return { nutrition: null, exercise: null };
    }
  };

  // ✅ UPDATED: Cached data uses storage utilities
  const getCachedEnrichedData = async () => {
    try {
      const cachedData = getFromStorage(StorageKeys.CACHED_ENRICHED_DATA);
      const cacheTimestamp = getFromStorage(StorageKeys.CACHED_ENRICHED_DATA_TIMESTAMP);
      const now = Date.now();

      if (cachedData && cacheTimestamp) {
        const age = now - parseInt(cacheTimestamp, 10);
        if (age < 24 * 60 * 60 * 1000) {
          if (cachedData && typeof cachedData === 'object') {
            return cachedData;
          }
        }
      }

      const enrichedData = await enrichDataWithExternalAPIs();

      if (enrichedData && (enrichedData.nutrition || enrichedData.exercise)) {
        setToStorage(StorageKeys.CACHED_ENRICHED_DATA, enrichedData);
        setToStorage(StorageKeys.CACHED_ENRICHED_DATA_TIMESTAMP, now.toString());
      }

      return enrichedData;
    } catch (error) {
      console.error('Error getting cached enriched data:', error.message);
      return { nutrition: null, exercise: null };
    }
  };

  useEffect(() => {
    const maybeEnrich = async () => {
      try {
        const lastEnrichment = getFromStorage(StorageKeys.LAST_API_ENRICHMENT, 0);
        const now = Date.now();

        if (now - parseInt(lastEnrichment, 10) > 24 * 60 * 60 * 1000) {
          await getCachedEnrichedData();
          setToStorage(StorageKeys.LAST_API_ENRICHMENT, now.toString());
        }
      } catch (error) {
        console.error('Error in background API enrichment:', error.message);
      }
    };
    maybeEnrich();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const updateChart = async (mode, period) => {
    try {
      const trendsResponse = await getTrends(period);
      const trends = Array.isArray(trendsResponse?.data) ? trendsResponse.data : [];
      const userWeight = parseFloat(safeJSONParse('user', {})?.weight || '70');
      const _isWkDone = (typeof status !== "undefined" && (status === "done" || status === "meal")) || (typeof workoutProgress !== "undefined" && workoutProgress === 1);
    const waterGoal = getDynamicWaterGoal(typeof userWeight !== "undefined" ? userWeight : 70, typeof sleep !== "undefined" ? sleep : 0, _isWkDone);
      const calorieGoal = Math.max(1, Number(macros.calMax) || 2200);

      if (period === 'month') {
        // --- MONTH VIEW: Group into 4 weeks ---
        const now = new Date();
        const weekLabels = ['Week 1', 'Week 2', 'Week 3', 'Week 4'];
        const weekBuckets = [[], [], [], []];

        trends.forEach((entry) => {
          const dateObj = new Date(entry?.date);
          if (Number.isNaN(dateObj.getTime())) return;
          const daysAgo = Math.floor((now - dateObj) / (1000 * 60 * 60 * 24));
          const weekIdx = Math.min(3, Math.floor(daysAgo / 7));
          weekBuckets[3 - weekIdx].push(entry); // oldest first
        });

        const series = weekBuckets.map((bucket) => {
          if (bucket.length === 0) return 0;
          if (mode === 'all') {
            const scores = bucket.map((entry) => calculateOverallTrendScore(entry, calorieGoal, waterGoal));
            const avg = scores.reduce((sum, score) => sum + score, 0) / Math.max(1, scores.length);
            return Math.round(avg);
          }
          if (mode === 'workout') {
            const scoreSum = bucket.reduce((sum, e) => sum + (e?.workout_completed ? 100 : (e?.workout_partial ? 50 : 0)), 0);
            return bucket.length > 0 ? Math.round(scoreSum / bucket.length) : 0;
          }
          if (mode === 'meal') {
            const totalCal = bucket.reduce((s, e) => s + (e?.calories || 0), 0);
            return bucket.length > 0 ? Math.round(totalCal / bucket.length) : 0;
          }
          if (mode === 'water') {
            const total = bucket.reduce((s, e) => s + (e?.water_intake || e?.water_glasses || 0), 0);
            return parseFloat((total / bucket.length).toFixed(1));
          }
          if (mode === 'sleep') {
            const total = bucket.reduce((s, e) => s + (e?.sleep_duration || e?.sleep_hours || 0), 0);
            return parseFloat((total / bucket.length).toFixed(1));
          }
          return 0;
        });

        setChartXLabels(weekLabels);
        setChartData(series);
      } else {
        // --- WEEK VIEW: 7-day slots Mon-Sun ---
        const series = [0, 0, 0, 0, 0, 0, 0];

        const startOfWeek = new Date();
        const dow = startOfWeek.getDay();
        const diffToMon = startOfWeek.getDate() - dow + (dow === 0 ? -6 : 1);
        startOfWeek.setDate(diffToMon);
        startOfWeek.setHours(0, 0, 0, 0);

        trends.forEach((entry) => {
          const dateObj = new Date(entry?.date);
          if (Number.isNaN(dateObj.getTime())) return;
          
          // Exclude entries that are before the start of the current week
          if (dateObj < startOfWeek) return;

          const jsDay = dateObj.getDay();
          const idx = jsDay === 0 ? 6 : jsDay - 1;

          if (mode === 'all') {
            const score = calculateOverallTrendScore(entry, calorieGoal, waterGoal);
            series[idx] = score;
          }
          else if (mode === 'workout') series[idx] = entry?.workout_completed ? 100 : (entry?.workout_partial ? 50 : 0);
          else if (mode === 'meal') series[idx] = entry?.calories || (entry?.meal_completed ? 1 : 0);
          else if (mode === 'water') series[idx] = entry?.water_intake || entry?.water_glasses || 0;
          else if (mode === 'sleep') series[idx] = entry?.sleep_duration || entry?.sleep_hours || 0;
        });

        // Keep today's slot live for selected realtime modes.
        if (mode === 'water' || mode === 'sleep' || mode === 'all') {
          const todayJsDay = new Date().getDay();
          const todayIdx = todayJsDay === 0 ? 6 : todayJsDay - 1;
          if (mode === 'water') series[todayIdx] = water;
          if (mode === 'sleep') series[todayIdx] = sleep;
          if (mode === 'all') series[todayIdx] = dailyProgress;
        }

        setChartXLabels(['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']);
        setChartData(series);
      }
    } catch (error) {
      console.error('Error fetching chart trends:', error);
      if (period === 'month') {
        setChartXLabels(['Week 1', 'Week 2', 'Week 3', 'Week 4']);
        setChartData([0, 0, 0, 0]);
      } else {
        setChartXLabels(['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']);
        const fallback = [0, 0, 0, 0, 0, 0, 0];
        const td = new Date().getDay();
        const tIdx = td === 0 ? 6 : td - 1;
        if (mode === 'water') fallback[tIdx] = water;
        else if (mode === 'sleep') fallback[tIdx] = sleep;
        else if (mode === 'all') fallback[tIdx] = dailyProgress;
        setChartData(fallback);
      }
    }
  };

  const saveTrendsToBackend = async (trendData) => {
    try {
      return await saveTrends(trendData);
    } catch (error) {
      console.error('Error saving trends to backend:', error);
      showInfo(
        'There was an issue saving your progress trends. Data will sync when connection is restored.',
        3000
      );
      return null;
    }
  };

  // ✅ UPDATED: Trends uses storage utilities
  const _updateTrends = async () => {
    try {
      const { data: profileData } = await getProfile();
      const userId = profileData._id || profileData.id;
      const todayStr = getTodayStr();
      const currentWeek = Math.ceil(new Date().getDate() / 7);
      const currentMonth = new Date().getMonth() + 1;

      // ✅ UPDATED: Use storage utilities
      const workoutDoneFlag = getFromStorage(StorageKeys.TODAY_WORKOUT_DONE) === 'true';
      const mealDone = getFromStorage(StorageKeys.TODAY_MEALS_DONE) === 'true';
      const restDayToday = isRestDayForDate(new Date());
      const workoutDone = restDayToday ? true : workoutDoneFlag;

      // ✅ FIX: Send flat macro fields instead of nested `macros` object.
      // The Mongoose schema now expects top-level `calories`, `protein`, `carbs`, `fat`.
      const trendData = {
        user_id: userId,
        date: todayStr,
        week: currentWeek,
        month: currentMonth,
        workout_completed: workoutDone,
        meal_completed: mealDone,
        calories: macros.calories || 0,
        protein: macros.p || 0,
        carbs: macros.c || 0,
        fat: macros.f || 0,
        water_intake: water,
        sleep_duration: sleep,
        water_glasses: water,
        sleep_hours: sleep,
        streak_days: stats.streak,
        timestamp: new Date().toISOString()
      };

      await saveTrendsToBackend(trendData);
      updateLocalTrendData(trendData);
    } catch (error) {
      console.error('Error updating trends:', error);
      showInfo('There was an issue updating your progress trends. Please try again.', 3000);
    }
  };

  const updateLocalTrendData = (trendData) => {
    try {
      const newChartData = [...chartData];
      const dayIndex = new Date(trendData.date).getDay();
      const adjustedIndex = dayIndex === 0 ? 6 : dayIndex - 1;

      if (chartMode === 'workout')
        newChartData[adjustedIndex] = trendData.workout_completed ? 1 : 0;
      else if (chartMode === 'meal')
        newChartData[adjustedIndex] = trendData.calories || (trendData.meal_completed ? 1 : 0);
      else if (chartMode === 'water') newChartData[adjustedIndex] = trendData.water_intake;
      else if (chartMode === 'sleep') newChartData[adjustedIndex] = trendData.sleep_duration;
      else if (chartMode === 'all') {
        const userWeight = parseFloat(safeJSONParse('user', {})?.weight || '70');
        const _isWkDone = (typeof status !== "undefined" && (status === "done" || status === "meal")) || (typeof workoutProgress !== "undefined" && workoutProgress === 1);
    const waterGoal = getDynamicWaterGoal(typeof userWeight !== "undefined" ? userWeight : 70, typeof sleep !== "undefined" ? sleep : 0, _isWkDone);
        const calorieGoal = Math.max(1, Number(macros.calMax) || 2200);
        newChartData[adjustedIndex] = calculateOverallTrendScore(trendData, calorieGoal, waterGoal);
      }

      setChartData(newChartData);
    } catch (error) {
      console.error('Error updating local trend data:', error);
    }
  };

  // ✅ UPDATED: Day reset uses deriving from backend or fallback to storage
  const checkDayReset = async (forceWorkoutDone, forceMealDone) => {
    try {
      const todayStr = getTodayStr();
      const workoutDoneFlag = forceWorkoutDone !== undefined ? forceWorkoutDone : getFromStorage(StorageKeys.TODAY_WORKOUT_DONE) === 'true';
      const mealDoneFlag = forceMealDone !== undefined ? forceMealDone : getFromStorage(StorageKeys.TODAY_MEALS_DONE) === 'true';

      const restDayToday = isRestDayForDate(new Date());
      if (restDayToday) {
        if (mealDoneFlag) setStatus('done');
        else setStatus('meal');
      } else if (!workoutDoneFlag) {
        setStatus('workout');
      } else if (!mealDoneFlag) {
        setStatus('meal');
      } else {
        setStatus('done');
      }

      // Streak is now computed from backend trends in fetchUserData.
      // Do NOT override with stale localStorage values.

      // ✅ UPDATED: Use storage utility
      const ongoingSession = getFromStorage(StorageKeys.ONGOING_WORKOUT);
      if (ongoingSession) {
        if (ongoingSession.date !== todayStr) endWorkoutSession();
      }
    } catch (error) {
      console.error('Error in checkDayReset:', error);
      showInfo(
        'There was an issue checking your daily progress. Using default values.',
        3000
      );
    }
  };

  const getTodaysWorkoutDay = () => {
    try {
      const workoutPlan = safeJSONParse('workoutPlan', []);
      if (!Array.isArray(workoutPlan) || workoutPlan.length === 0) return null;

      const jsDay = new Date().getDay();
      const todayIdx = (jsDay + 6) % 7;
      const todayPlan = workoutPlan.find((day) => (day?.day_of_week ?? -1) === todayIdx) || null;

      if (todayPlan && todayPlan.type !== 'rest' && !todayPlan.is_placeholder && todayPlan.type !== 'past') {
        return todayPlan;
      }
      return null;
    } catch {
      return null;
    }
  };

  const handleAction = async () => {
    try {
      if (!status) return;
      if (status === 'workout') {
        startWorkoutSession({ startedAt: new Date().toISOString(), expectedCompletion: true });
        const enrichedData = await getCachedEnrichedData();
        const todaysWorkout = getTodaysWorkoutDay();

        if (todaysWorkout) {
          navigate('/workout', {
            state: {
              recoveryScore,
              workoutIntensity,
              autoStartDay: todaysWorkout.day_of_week,
              enrichedData,
            },
          });
        } else {
          navigate('/workout', { state: { recoveryScore, workoutIntensity, enrichedData } });
        }
      } else if (status === 'meal') {
        const enrichedData = await getCachedEnrichedData();
        navigate('/nutrition', { state: { enrichedData } });
      }
    } catch (error) {
      console.error('Error in handleAction:', error);
      showError('There was an issue navigating to the requested page. Please try again.', 3000);
    }
  };

  const showConfirmDialog = (message, onConfirm) =>
    setConfirmDialog({ show: true, message, onConfirm });

  const handleConfirm = () => {
    if (confirmDialog.onConfirm) confirmDialog.onConfirm(true);
    setConfirmDialog({ show: false, message: '', onConfirm: null });
  };

  const handleCancelConfirm = () => {
    if (confirmDialog.onConfirm) confirmDialog.onConfirm(false);
    setConfirmDialog({ show: false, message: '', onConfirm: null });
  };

  // ✅ FIX: Delegate logout to App.jsx via onLogout prop.
  //    This ensures App.jsx's isAuthenticated flips to false BEFORE navigate()
  //    is called, so the route guard never sees a logged-in user on /login.
  const handleLogout = () => {
    showConfirmDialog('Log out of Elevate?', (confirmed) => {
      if (confirmed) {
        if (typeof onLogout === 'function') {
          // onLogout() clears storage, sets isAuthenticated=false, and navigates
          onLogout();
        } else {
          // Fallback if prop wasn't passed
          logoutSafe();
          navigate('/login', { replace: true });
        }
      }
    });
  };

  // ✅ BUG FIX 1: Listen for macro sync signals from Nutrition page
  // When user switches back to Dashboard tab, read _macroSync from localStorage
  useEffect(() => {
    const handleVisibilityChange = () => {
      if (document.visibilityState === 'visible') {
        try {
          const raw = localStorage.getItem('_macroSync');
          if (raw) {
            const sync = JSON.parse(raw);
            // Only apply if the signal is recent (within last 5 minutes)
            if (sync.ts && (Date.now() - sync.ts) < 5 * 60 * 1000) {
              setMacros(prev => ({
                ...prev,
                calories: Math.round(sync.calories || prev.calories),
                p: Math.round(sync.protein || prev.p),
                c: Math.round(sync.carbs || prev.c),
                f: Math.round(sync.fat || prev.f),
                remaining: Math.max(0, prev.calMax - Math.round(sync.calories || prev.calories)),
              }));
              console.log('✅ Dashboard macros updated from Nutrition sync:', sync);
            }
            // Clear the signal after consuming it
            localStorage.removeItem('_macroSync');
          }
        } catch (err) {
          console.warn('Failed to process macro sync signal:', err);
        }
      }
    };

    document.addEventListener('visibilitychange', handleVisibilityChange);
    return () => document.removeEventListener('visibilitychange', handleVisibilityChange);
  }, []);

  return (
    <>
      <div style={styles.page} className="page">
        <style>{responsiveStyles}</style>
        {/* ✨ Aurora Mesh Gradient background — replaces bubble animation */}
        <AuroraBackground />

        {loading && (
          <div style={{
            position: 'fixed',
            inset: 0,
            zIndex: 9998,
            background: 'rgba(9, 9, 11, 0.55)',
            backdropFilter: 'blur(2px)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center'
          }}>
            <div style={{ color: '#6366f1', fontSize: '18px', fontWeight: '600' }}>
              Loading Dashboard...
            </div>
          </div>
        )}

        {/* IMAGE MODAL */}
        {showImageModal && userAvatar && (
          <div style={styles.modalOverlay} onClick={() => setShowImageModal(false)}>
            <div style={styles.modalContent} onClick={(e) => e.stopPropagation()}>
              <button
                style={styles.closeModalBtn}
                onClick={() => setShowImageModal(false)}
              >
                ×
              </button>
              <img src={userAvatar} alt="Full Profile" style={styles.modalImage} />
            </div>
          </div>
        )}

        {/* NAVBAR */}
        <Navbar 
          isDark={theme === 'dark'}
          navigate={navigate} 
          activePage="dashboard" 
          onLogout={handleLogout}
          rightContent={
            <>
              <div style={styles.dateDisplay} className="desktop-nav">{todayDate}</div>
              <button
                className="theme-toggle-btn"
                onClick={toggleTheme}
                title={theme === 'dark' ? 'Switch to Light Mode' : 'Switch to Dark Mode'}
                aria-label="Toggle theme"
              >
                {theme === 'dark' ? '☀️' : '🌙'}
              </button>
            </>
          }
        />

        {/* MAIN CONTAINER */}
        <div style={styles.container} className="container responsive-grid-12">

          {/* WATER CELEBRATION */}
          {showWaterCelebration && (
            <div style={{ position: 'fixed', inset: 0, zIndex: 9999, pointerEvents: 'none', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
              <div style={{ position: 'absolute', inset: 0, background: 'radial-gradient(circle, rgba(14,165,233,0.15) 0%, transparent 70%)', animation: 'fadeIn 0.3s ease' }} />
              {[...Array(20)].map((_, i) => (
                <div key={i} style={{
                  position: 'absolute',
                  fontSize: `${12 + Math.random() * 24}px`,
                  left: `${5 + Math.random() * 90}%`,
                  top: `${Math.random() * 100}%`,
                  animation: `floatUp ${2 + Math.random() * 2}s ease-out forwards`,
                  animationDelay: `${Math.random() * 0.5}s`,
                  opacity: 0,
                }}>{['💧', '🌊', '💦', '✨'][Math.floor(Math.random() * 4)]}</div>
              ))}
              <div style={{
                background: 'rgba(14, 165, 233, 0.1)', backdropFilter: 'blur(20px)',
                border: '1px solid rgba(56, 189, 248, 0.3)', borderRadius: '24px',
                padding: '32px 48px', textAlign: 'center',
                animation: 'celebrateCard 0.6s cubic-bezier(0.34, 1.56, 0.64, 1) forwards',
                boxShadow: '0 25px 50px rgba(0,0,0,0.4), 0 0 60px rgba(56,189,248,0.2)',
              }}>
                <div style={{ fontSize: '56px', marginBottom: '8px', animation: 'bounce 0.6s ease 0.3s both' }}>💧</div>
                <div style={{ fontSize: '24px', fontWeight: '800', color: 'var(--app-text)', letterSpacing: '-0.5px' }}>Hydration Complete!</div>
                <div style={{ fontSize: '14px', color: '#7dd3fc', marginTop: '4px' }}>Daily water goal reached</div>
              </div>
            </div>
          )}

          {/* SLEEP CELEBRATION */}
          {showSleepCelebration && (
            <div style={{ position: 'fixed', inset: 0, zIndex: 9999, pointerEvents: 'none', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
              <div style={{ position: 'absolute', inset: 0, background: 'radial-gradient(circle, rgba(139,92,246,0.15) 0%, transparent 70%)', animation: 'fadeIn 0.3s ease' }} />
              {[...Array(20)].map((_, i) => (
                <div key={i} style={{
                  position: 'absolute',
                  fontSize: `${12 + Math.random() * 24}px`,
                  left: `${5 + Math.random() * 90}%`,
                  top: `${Math.random() * 100}%`,
                  animation: `floatUp ${2 + Math.random() * 2}s ease-out forwards`,
                  animationDelay: `${Math.random() * 0.5}s`,
                  opacity: 0,
                }}>{['🌙', '⭐', '✨', '😴'][Math.floor(Math.random() * 4)]}</div>
              ))}
              <div style={{
                background: 'rgba(139, 92, 246, 0.1)', backdropFilter: 'blur(20px)',
                border: '1px solid rgba(167, 139, 250, 0.3)', borderRadius: '24px',
                padding: '32px 48px', textAlign: 'center',
                animation: 'celebrateCard 0.6s cubic-bezier(0.34, 1.56, 0.64, 1) forwards',
                boxShadow: '0 25px 50px rgba(0,0,0,0.4), 0 0 60px rgba(139,92,246,0.2)',
              }}>
                <div style={{ fontSize: '56px', marginBottom: '8px', animation: 'bounce 0.6s ease 0.3s both' }}>🌙</div>
                <div style={{ fontSize: '24px', fontWeight: '800', color: 'var(--app-text)', letterSpacing: '-0.5px' }}>Optimal Sleep!</div>
                <div style={{ fontSize: '14px', color: '#c4b5fd', marginTop: '4px' }}>You hit the 7-9 hour sweet spot</div>
              </div>
            </div>
          )}

          {/* HERO SECTION */}
          <div style={{ ...styles.bentoBox, ...styles.heroSection }} className="bentoBox heroSection">

            <div style={{ ...styles.heroLeft, position: 'relative', zIndex: 1 }} className="heroLeft">
              <div
                style={styles.avatarWrapper}
                className="avatarWrapper"
                onClick={() => navigate('/profile-setup', { state: { isEditing: true } })}
              >
                <div style={styles.avatarContainer}>
                  {userAvatar ? (
                    <img src={userAvatar} alt="Profile" style={styles.avatarImage} />
                  ) : (
                    <div style={styles.avatarImage}>
                      {displayName ? displayName.charAt(0).toUpperCase() : 'T'}
                    </div>
                  )}
                </div>
                <div style={styles.editIconBadge} className="edit-icon-hover">
                  ✎
                </div>
              </div>
              <div style={styles.heroTextContent}>
                <h1 style={styles.h1} className="h1">
                  Hello, {displayName}
                </h1>
                <div style={styles.quoteCard} className="quoteCard">
                  "{currentQuote}"
                </div>
              </div>
            </div>

            <div style={{ ...styles.heroCenter, position: 'relative', zIndex: 1 }} className="heroCenter">
              {(() => {
                const heroAction = getHeroActionMeta(status);
                const heroTheme = getHeroActionTheme(HERO_ACTION_VARIANT, heroAction.stateKey);
                // Always use computed daily progress so first render starts at 0%.
                const radialScore = Number.isFinite(dailyProgress)
                  ? Math.min(100, Math.max(0, Math.round(dailyProgress)))
                  : getFallbackRadialScore(status);
                const ctaLabel =
                  heroAction.stateKey === 'meal'
                    ? 'Open Meals'
                    : heroAction.stateKey === 'done'
                    ? (radialScore < 100 ? 'Finish Habits' : 'Completed')
                    : heroAction.stateKey === 'sync'
                    ? 'Syncing...'
                    : 'Start Workout';

                return (
                  <button
                    style={{
                      ...styles.circleBtn,
                      width:
                        HERO_ACTION_VARIANT === 'neonRadial'
                          ? 'min(100%, 224px)'
                          : styles.circleBtn.width,
                      minHeight:
                        HERO_ACTION_VARIANT === 'neonRadial'
                          ? '206px'
                          : styles.circleBtn.minHeight,
                      padding:
                        HERO_ACTION_VARIANT === 'neonRadial'
                          ? '12px 10px'
                          : styles.circleBtn.padding,
                      gap:
                        HERO_ACTION_VARIANT === 'neonRadial'
                          ? '10px'
                          : styles.circleBtn.gap,
                      alignItems:
                        HERO_ACTION_VARIANT === 'neonRadial'
                          ? 'center'
                          : styles.circleBtn.alignItems,
                      textAlign:
                        HERO_ACTION_VARIANT === 'neonRadial'
                          ? 'center'
                          : styles.circleBtn.textAlign,
                      borderRadius:
                        HERO_ACTION_VARIANT === 'neonRadial'
                          ? '20px'
                          : styles.circleBtn.borderRadius,
                      justifyContent:
                        HERO_ACTION_VARIANT === 'neonRadial'
                          ? 'center'
                          : styles.circleBtn.justifyContent,
                      alignSelf:
                        HERO_ACTION_VARIANT === 'neonRadial'
                          ? 'center'
                          : 'auto',
                      background: HERO_ACTION_VARIANT === 'neonRadial' ? 'transparent' : heroTheme.surface,
                      border: heroTheme.border,
                      boxShadow: heroTheme.shadow,
                      backdropFilter: HERO_ACTION_VARIANT === 'neonRadial' ? 'none' : 'blur(10px)',
                      cursor: heroAction.disabled ? 'default' : 'pointer',
                      outline: 'none'
                    }}
                    className={`hero-action-btn ${HERO_ACTION_VARIANT === 'neonRadial' ? `neon-radial-btn neon-state-${heroAction.stateKey}` : ''}`}
                    disabled={heroAction.disabled}
                    onClick={heroAction.disabled ? undefined : handleAction}
                  >
                    <div style={{ display: 'grid', placeItems: 'center', marginTop: '2px' }}>
                      <div
                        className="hero-ring-glow"
                        style={{
                          width: '120px',
                          height: '120px',
                          borderRadius: '50%',
                          background: `conic-gradient(${heroTheme.ringColor} ${radialScore}%, var(--app-border) ${radialScore}% 100%)`,
                          display: 'grid',
                          placeItems: 'center',
                          boxShadow: `0 0 18px ${heroTheme.ringGlow}`,
                          transition: 'background 0.7s cubic-bezier(0.4, 0, 0.2, 1)',
                        }}
                      >
                        <div
                          style={{
                            width: '96px',
                            height: '96px',
                            borderRadius: '50%',
                            background: heroTheme.coreBg.startsWith('#') ? `${heroTheme.coreBg}cc` : heroTheme.coreBg, /* 80% opacity */
                            border: heroTheme.coreBorder,
                            display: 'grid',
                            placeItems: 'center',
                            boxShadow: 'inset 0 1px 8px rgba(0,0,0,0.35)'
                          }}
                        >
                          <div style={{ textAlign: 'center' }}>
                            <div style={{ fontSize: '22px', lineHeight: 1, color: heroTheme.iconColor }}>{heroAction.icon}</div>
                            <div style={{ marginTop: '4px', fontSize: '14px', color: heroTheme.titleColor, fontWeight: 800 }}>{radialScore}%</div>
                          </div>
                        </div>
                      </div>
                    </div>

                    <div
                      className={HERO_ACTION_VARIANT === 'neonRadial' ? 'neon-cta' : undefined}
                      style={{
                        marginTop: '4px',
                        border: 'none',
                        borderRadius: '999px',
                        background: heroTheme.ctaBg,
                        color: heroTheme.ctaText,
                        fontWeight: 800,
                        fontSize: '13px',
                        textTransform: 'uppercase',
                        letterSpacing: '0.4px',
                        padding: '9px 14px',
                        minWidth: '152px',
                        textAlign: 'center',
                        boxShadow: `0 0 14px ${heroTheme.ringGlow}`
                      }}
                    >
                      {ctaLabel}
                    </div>

                    {heroAction.subtitle ? (
                      <div style={{ fontSize: '12px', color: heroTheme.subtitleColor, lineHeight: 1.45, textAlign: 'center', maxWidth: '220px' }}>
                        {heroAction.subtitle}
                      </div>
                    ) : null}
                  </button>
                );
              })()}
            </div>

            <div style={{ ...styles.heroRight, position: 'relative', zIndex: 1 }} className="heroRight">
              <div style={{ textAlign: 'right' }}>
                <div style={styles.streakLabel}>CURRENT STREAK</div>
                <div style={{ display: 'flex', gap: 15, flexWrap: 'wrap', justifyContent: 'flex-end' }}>
                  <div style={styles.streakNumber} className="streakNumber">
                    {stats.streak}
                  </div>
                  <div style={{ animation: 'firePulse 2.5s infinite alternate ease-in-out', display: 'flex', alignItems: 'center' }}>
                    <style>{`
                      @keyframes firePulse {
                        0% { transform: scale(0.95); filter: drop-shadow(0 0 8px rgba(249, 115, 22, 0.4)); }
                        50% { transform: scale(1.03); filter: drop-shadow(0 0 18px rgba(249, 115, 22, 0.8)); }
                        100% { transform: scale(0.98); filter: drop-shadow(0 0 14px rgba(239, 68, 68, 0.6)); }
                      }
                    `}</style>
                    <svg style={{ width: 'clamp(42px, 10vw, 80px)', height: 'auto' }} viewBox="0 0 24 24" fill="url(#streakFireGrad)" stroke="none">
                      <defs>
                        <linearGradient id="streakFireGrad" x1="0%" y1="100%" x2="0%" y2="0%">
                          <stop offset="0%" stopColor="#f59e0b" />
                          <stop offset="50%" stopColor="#f97316" />
                          <stop offset="100%" stopColor="#ef4444" />
                        </linearGradient>
                      </defs>
                      <path fillRule="evenodd" d="M12.963 2.286a.75.75 0 00-1.071-.136 9.742 9.742 0 00-3.539 6.177A7.547 7.547 0 016.648 6.61a.75.75 0 00-1.152-.082A9 9 0 1015.68 4.534a7.46 7.46 0 01-2.717-2.248zM15.75 14.25a3.75 3.75 0 11-7.313-1.172c.628.465 1.353.81 2.133 1a5.99 5.99 0 011.925-3.545 3.75 3.75 0 013.255 3.717z" clipRule="evenodd" />
                    </svg>
                  </div>
                </div>
              </div>
              <div style={styles.weekGrid} className="weekGrid">
                {weeklyProgress.map((item, i) => (
                  <div
                    key={i}
                    className="day-item dayCircle"
                    style={{
                      ...styles.dayCircle,
                      ...(item.status === 'done' ? styles.dayDone : styles.dayActive)
                    }}
                  >
                    {item.status === 'done' ? '✅' : item.day}
                  </div>
                ))}
              </div>
            </div>
          </div>

          {/* STATS ROW (MACRO, HYDRATION, READINESS) */}
          <div style={dashboardLayout.statsRow} className="responsive-stats-row">
            {/* MACROS BOX */}
            <div style={{ ...styles.bentoBox, ...styles.statBox }} className="hover-card">
              <div
                style={{
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'space-between',
                  marginBottom: '16px'
                }}
              >
                <div style={{ fontSize: '14px', fontWeight: '700', color: 'var(--app-text)' }}>
                  MACROS TODAY
                </div>
                <div style={{ fontSize: '12px', color: 'var(--app-text-muted)' }}>
                  {Math.round(macros.calories)} / {Math.round(macros.calMax)} cal
                </div>
              </div>
              <div
                className="macro-item"
                style={{ marginBottom: '12px', cursor: 'pointer' }}
                title={`Total: ${Math.round(macros.calories)} cal`}
              >
                <div
                  style={{
                    display: 'flex',
                    justifyContent: 'space-between',
                    fontSize: '11px',
                    color: 'var(--app-text)',
                    marginBottom: '4px'
                  }}
                >
                  <span>Total Calories</span>
                </div>
                <div style={{ ...styles.macroBarBG, overflow: 'hidden' }}>
                  <div
                    style={{
                      ...styles.macroBarFill,
                      width: `${Math.min(100, (macros.calories / macros.calMax) * 100)}%`,
                      background: 'var(--app-text)'
                    }}
                  ></div>
                </div>
              </div>
              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr 1fr', gap: '12px' }}>
                {/* Protein */}
                <div
                  className="macro-item"
                  style={{ cursor: 'pointer' }}
                  title={`${Math.round(macros.p)}g Protein`}
                >
                  <div style={{ fontSize: '10px', color: 'var(--app-text-muted)', marginBottom: '4px' }}>
                    Prot ({Math.round(macros.p)}g)
                  </div>
                  <div style={{ ...styles.macroBarBG, height: '4px', overflow: 'hidden' }}>
                    <div
                      style={{
                        ...styles.macroBarFill,
                        width: `${Math.min(100, (macros.p / macros.pMax) * 100)}%`,
                        background: '#6366f1'
                      }}
                    ></div>
                  </div>
                </div>
                {/* Carbs */}
                <div
                  className="macro-item"
                  style={{ cursor: 'pointer' }}
                  title={`${Math.round(macros.c)}g Carbs`}
                >
                  <div style={{ fontSize: '10px', color: 'var(--app-text-muted)', marginBottom: '4px' }}>
                    Carb ({Math.round(macros.c)}g)
                  </div>
                  <div style={{ ...styles.macroBarBG, height: '4px', overflow: 'hidden' }}>
                    <div
                      style={{
                        ...styles.macroBarFill,
                        width: `${Math.min(100, (macros.c / macros.cMax) * 100)}%`,
                        background: '#22c55e'
                      }}
                    ></div>
                  </div>
                </div>
                {/* Fats */}
                <div
                  className="macro-item"
                  style={{ cursor: 'pointer' }}
                  title={`${Math.round(macros.f)}g Fats`}
                >
                  <div style={{ fontSize: '10px', color: 'var(--app-text-muted)', marginBottom: '4px' }}>
                    Fat ({Math.round(macros.f)}g)
                  </div>
                  <div style={{ ...styles.macroBarBG, height: '4px', overflow: 'hidden' }}>
                    <div
                      style={{
                        ...styles.macroBarFill,
                        width: `${Math.min(100, (macros.f / macros.fMax) * 100)}%`,
                        background: '#eab308'
                      }}
                    ></div>
                  </div>
                </div>
              </div>
              {/* Meals Logged Today */}
              <div style={{ marginTop: '14px' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '8px' }}>
                  <span style={{ fontSize: '11px', color: 'var(--app-text-muted)' }}>Meals Logged</span>
                  <span style={{ fontSize: '11px', color: mealsLoggedToday === 3 ? '#34d399' : 'var(--app-text-muted)' }}>
                    {mealsLoggedToday} / 3
                  </span>
                </div>
                <div style={{ display: 'flex', gap: '6px' }}>
                  {[
                    { label: 'B', name: 'breakfast' },
                    { label: 'L', name: 'lunch' },
                    { label: 'D', name: 'dinner' },
                  ].map(({ label, name }) => {
                    const done = mealsLoggedToday > 0 && (
                      name === 'breakfast' ? mealsLoggedToday >= 1 :
                      name === 'lunch'     ? mealsLoggedToday >= 2 :
                                             mealsLoggedToday >= 3
                    );
                    return (
                      <div
                        key={name}
                        title={`${name.charAt(0).toUpperCase() + name.slice(1)} ${done ? 'logged ✅' : 'not logged yet'}`}
                        style={{
                          flex: 1,
                          padding: '5px 0',
                          borderRadius: '6px',
                          textAlign: 'center',
                          fontSize: '11px',
                          fontWeight: '600',
                          background: done
                            ? 'linear-gradient(135deg, #065f46, #047857)'
                            : 'var(--app-border)',
                          color: done ? '#34d399' : '#52525b',
                          border: `1px solid ${done ? 'rgba(52,211,153,0.3)' : 'rgba(255,255,255,0.06)'}`,
                          transition: 'all 0.3s ease',
                        }}
                      >
                        {label}
                      </div>
                    );
                  })}
                </div>
              </div>
            </div>

            {/* HYDRATION BOX */}
            {(() => {
              const userWeight = parseFloat(safeJSONParse('user', {})?.weight || localStorage.getItem('userWeight') || '70');
              const _isWkDone = (typeof status !== "undefined" && (status === "done" || status === "meal")) || (typeof workoutProgress !== "undefined" && workoutProgress === 1);
    const waterGoal = getDynamicWaterGoal(typeof userWeight !== "undefined" ? userWeight : 70, typeof sleep !== "undefined" ? sleep : 0, _isWkDone);
              const waterPercent = Math.min(100, Math.round((water / waterGoal) * 100));
              return (
              <div
                style={{
                  ...styles.bentoBox,
                  ...styles.statBox,
                  background: 'linear-gradient(135deg, rgba(30, 58, 138, 0.82) 0%, rgba(23, 37, 84, 0.82) 100%)',
                  border: '1px solid rgba(96, 165, 250, 0.2)',
                  position: 'relative',
                  overflow: 'hidden',
                }}
                className="hover-card bentoBox"
              >
                {/* Animated water fill background */}
                <div style={{
                  position: 'absolute', bottom: 0, left: 0, right: 0,
                  height: `${waterPercent}%`,
                  background: 'linear-gradient(180deg, rgba(56, 189, 248, 0.15) 0%, rgba(14, 165, 233, 0.08) 100%)',
                  transition: 'height 0.8s cubic-bezier(0.4, 0, 0.2, 1)',
                  borderTop: '1px solid rgba(56, 189, 248, 0.2)',
                }} />
                <div style={{ position: 'relative', zIndex: 1, display: 'flex', flexDirection: 'column', height: '100%' }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '10px' }}>
                    <div style={{ fontSize: '14px', fontWeight: '700', color: 'var(--app-text)' }}>HYDRATION</div>
                    <div style={{ fontSize: '12px', fontWeight: '700', color: waterPercent >= 100 ? '#34d399' : '#93c5fd' }}>{waterPercent}%</div>
                  </div>
                  <div style={{ flex: 1, display: 'flex', flexDirection: 'column', justifyContent: 'center', alignItems: 'center' }}>
                    <div style={{ fontSize: '48px', fontWeight: '800', color: 'var(--app-text)' }}>
                      {water.toFixed(1)} <span style={{ fontSize: '16px', fontWeight: '500', color: '#93c5fd' }}>L</span>
                    </div>
                    <div style={{ fontSize: '12px', color: '#bfdbfe' }}>Goal: {waterGoal} L ({Math.round(userWeight)}kg)</div>
                    {/* Progress bar */}
                    <div style={{ width: '80%', height: '4px', background: 'var(--app-border)', borderRadius: '2px', marginTop: '8px', overflow: 'hidden' }}>
                      <div style={{ width: `${waterPercent}%`, height: '100%', background: waterPercent >= 100 ? 'linear-gradient(90deg, #34d399, #22c55e)' : 'linear-gradient(90deg, #38bdf8, #0ea5e9)', borderRadius: '2px', transition: 'width 0.6s ease' }} />
                    </div>
                  </div>
                  <div style={{ display: 'flex', justifyContent: 'center', flexDirection: 'column', alignItems: 'center' }}>
                    <div style={styles.glassPill} className="glassPill">
                      <button style={styles.glassBtn} className="control-btn-hover glassBtn" onClick={handleWaterRemove}>-</button>
                      <span style={styles.glassText}>+250ML</span>
                      <button style={styles.glassBtn} className="control-btn-hover glassBtn" onClick={handleWaterAdd}>+</button>
                    </div>
                    <div style={{ marginTop: '10px', fontSize: '12px', color: recoveryScore > 60 ? '#22c55e' : recoveryScore > 40 ? '#f59e0b' : '#ef4444' }}>
                      Recovery: {recoveryScore}%
                    </div>
                  </div>
                </div>
              </div>
              );
            })()}

            {/* READINESS BOX */}
            {(() => {
              const sleepQuality = sleep === 0 ? 0 : sleep >= 7 && sleep <= 9 ? 100 : sleep >= 6 && sleep <= 10 ? 75 : sleep >= 5 ? 50 : 25;
              const qualityLabel = sleepQuality >= 90 ? 'Optimal' : sleepQuality >= 70 ? 'Good' : sleepQuality >= 40 ? 'Fair' : sleep > 0 ? 'Low' : '—';
              const qualityColor = sleepQuality >= 90 ? '#22c55e' : sleepQuality >= 70 ? '#34d399' : sleepQuality >= 40 ? '#f59e0b' : '#ef4444';
              return (
              <div style={{ ...styles.bentoBox, ...styles.statBox, position: 'relative', overflow: 'hidden' }} className="hover-card bentoBox">
                <div style={{ position: 'absolute', bottom: '-20px', left: '50%', transform: 'translateX(-50%)', width: '150px', height: '80px', background: `radial-gradient(circle, ${qualityColor}15 0%, transparent 70%)`, transition: 'all 0.6s ease' }} />
                <div style={{ position: 'relative', zIndex: 1, display: 'flex', flexDirection: 'column', height: '100%' }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                    <div style={{ fontSize: '14px', fontWeight: '700', color: 'var(--app-text)', marginBottom: '10px' }}>SLEEP</div>
                    <div style={{ fontSize: '12px', fontWeight: '700', padding: '2px 10px', borderRadius: '12px', background: `${qualityColor}15`, color: qualityColor, border: `1px solid ${qualityColor}30` }}>
                      {qualityLabel}
                    </div>
                  </div>
                  <div style={{ flex: 1, display: 'flex', flexDirection: 'column', justifyContent: 'center', alignItems: 'center' }}>
                    <div style={{ fontSize: '48px', fontWeight: '800', color: 'var(--app-text)', fontFamily: 'monospace' }}>
                      {Math.floor(sleep)}<span style={{ color: '#6366f1' }}>:</span>{String(Math.round((sleep % 1) * 60)).padStart(2, '0')}
                    </div>
                    <div style={{ fontSize: '12px', color: 'var(--app-text-muted)' }}>Hours Slept • Target 7-9h</div>
                    <div style={{ width: '80%', height: '4px', background: 'var(--app-border)', borderRadius: '2px', marginTop: '8px', overflow: 'hidden' }}>
                      <div style={{ width: `${sleepQuality}%`, height: '100%', background: `linear-gradient(90deg, ${qualityColor}, ${qualityColor}cc)`, borderRadius: '2px', transition: 'width 0.6s ease' }} />
                    </div>
                  </div>
                  <div style={{ display: 'flex', justifyContent: 'center', flexDirection: 'column', alignItems: 'center' }}>
                    <div style={styles.glassPill} className="glassPill">
                      <button style={styles.glassBtn} className="control-btn-hover glassBtn" onClick={handleSleepRemove}>-</button>
                      <span style={styles.glassText}>+30 MIN</span>
                      <button style={styles.glassBtn} className="control-btn-hover glassBtn" onClick={handleSleepAdd}>+</button>
                    </div>
                    <div style={{ marginTop: '10px', fontSize: '12px', color: qualityColor }}>
                      Readiness: {stats.focusScore}%
                    </div>
                  </div>
                </div>
              </div>
              );
            })()
          }
          </div>

          {/* AI COACH SUMMARY / ADAPTIVE MODIFIERS */}
          {weeklyAverages && (
            <div
              style={{
                ...styles.bentoBox,
                gridColumn: 'span 12',
                background: 'linear-gradient(135deg, rgba(30, 27, 75, 0.7) 0%, rgba(15, 23, 42, 0.8) 100%)',
                border: '1px solid rgba(139, 92, 246, 0.2)',
                padding: '20px',
                marginBottom: '20px',
                display: 'flex',
                flexDirection: 'column',
                gap: '15px',
                position: 'relative',
                overflow: 'hidden',
              }}
              className="hover-card bentoBox"
            >
              {/* Decorative radial gradient glow */}
              <div
                style={{
                  position: 'absolute',
                  top: '-40px',
                  right: '-40px',
                  width: '180px',
                  height: '180px',
                  background: 'radial-gradient(circle, rgba(139, 92, 246, 0.15) 0%, transparent 70%)',
                  pointerEvents: 'none',
                }}
              />
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', flexWrap: 'wrap', gap: '12px' }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
                  <div style={{ fontSize: '24px', background: 'rgba(139, 92, 246, 0.2)', padding: '8px', borderRadius: '12px', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>🤖</div>
                  <div style={{ display: 'flex', flexDirection: 'column', gap: '2px' }}>
                    <span style={{ fontSize: '16px', fontWeight: '900', color: 'var(--app-text)', letterSpacing: '0.5px', textTransform: 'uppercase' }}>
                      AI Coach
                    </span>
                    <span style={{ fontSize: '11px', fontWeight: '700', color: '#c084fc', letterSpacing: '1px', textTransform: 'uppercase' }}>
                      Adaptive Auto-Regulation
                    </span>
                  </div>
                </div>
                <div
                  style={{
                    fontSize: '11px',
                    fontWeight: '700',
                    padding: '3px 10px',
                    borderRadius: '20px',
                    background: 'rgba(139, 92, 246, 0.15)',
                    color: '#c084fc',
                    border: '1px solid rgba(139, 92, 246, 0.3)',
                    textTransform: 'uppercase',
                  }}
                >
                  {(weeklyAverages.days_logged || 0)} Days Tracked
                </div>
              </div>

              <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(180px, 1fr))', gap: '15px' }}>
                {/* Sleep Metrics */}
                <div style={{ background: 'rgba(255, 255, 255, 0.02)', padding: '12px', borderRadius: '10px', border: '1px solid rgba(255,255,255,0.05)' }}>
                  <div style={{ fontSize: '11px', color: 'var(--app-text-muted)', marginBottom: '4px' }}>WEEKLY SLEEP AVG</div>
                  <div style={{ fontSize: '24px', fontWeight: '800', color: '#a78bfa' }}>
                    {(weeklyAverages.avg_sleep_hours || 0)} <span style={{ fontSize: '13px', fontWeight: '500', color: 'var(--app-text-muted)' }}>hours / night</span>
                  </div>
                  {weeklyAverages.deload_flag ? (
                    <div style={{ fontSize: '11px', color: '#f87171', marginTop: '6px', fontWeight: '600' }}>
                      ⚠️ Critical sleep deficit. Recovery Deload active.
                    </div>
                  ) : (weeklyAverages.avg_sleep_hours || 0) < 6.0 ? (
                    <div style={{ fontSize: '11px', color: '#fbbf24', marginTop: '6px', fontWeight: '600' }}>
                      ⚠️ Sleep deficit. Intensity reduced by 10%.
                    </div>
                  ) : (
                    <div style={{ fontSize: '11px', color: '#34d399', marginTop: '6px', fontWeight: '600' }}>
                      ✓ Sleep is optimal. Recovery normal.
                    </div>
                  )}
                </div>

                {/* Hydration Metrics */}
                <div style={{ background: 'rgba(255, 255, 255, 0.02)', padding: '12px', borderRadius: '10px', border: '1px solid rgba(255,255,255,0.05)' }}>
                  <div style={{ fontSize: '11px', color: 'var(--app-text-muted)', marginBottom: '4px' }}>WEEKLY HYDRATION AVG</div>
                  <div style={{ fontSize: '24px', fontWeight: '800', color: '#60a5fa' }}>
                    {((weeklyAverages.avg_water_ml || 0) / 1000).toFixed(2)} <span style={{ fontSize: '13px', fontWeight: '500', color: 'var(--app-text-muted)' }}>L / day</span>
                  </div>
                  {weeklyAverages.dehydration_flag ? (
                    <div style={{ fontSize: '11px', color: '#f87171', marginTop: '6px', fontWeight: '600' }}>
                      ⚠️ Dehydration detected. Cardio & work reduced.
                    </div>
                  ) : (
                    <div style={{ fontSize: '11px', color: '#34d399', marginTop: '6px', fontWeight: '600' }}>
                      ✓ Hydration targets met.
                    </div>
                  )}
                </div>

                {/* Workout Consistency */}
                <div style={{ background: 'rgba(255, 255, 255, 0.02)', padding: '12px', borderRadius: '10px', border: '1px solid rgba(255,255,255,0.05)' }}>
                  <div style={{ fontSize: '11px', color: 'var(--app-text-muted)', marginBottom: '4px' }}>WORKOUT FREQUENCY</div>
                  <div style={{ fontSize: '24px', fontWeight: '800', color: '#34d399' }}>
                    {Math.round((weeklyAverages.workout_completion_rate || 0) * 100)}% <span style={{ fontSize: '13px', fontWeight: '500', color: 'var(--app-text-muted)' }}>completion</span>
                  </div>
                  <div style={{ fontSize: '11px', color: (weeklyAverages.workout_completion_rate || 0) >= 0.57 ? '#34d399' : '#f87171', marginTop: '6px', fontWeight: '600' }}>
                    {(weeklyAverages.workout_completion_rate || 0) >= 0.57 
                      ? '🔥 Consistency bonus active: +1 set!' 
                      : '⚠️ Attendance deficit. Volume increases paused.'}
                  </div>
                </div>
              </div>

              {/* Coach Adaptation Explanation */}
              <div
                style={{
                  background: 'rgba(139, 92, 246, 0.05)',
                  border: '1px dashed rgba(139, 92, 246, 0.2)',
                  padding: '12px 16px',
                  borderRadius: '8px',
                  fontSize: '13px',
                  lineHeight: '1.5',
                  color: '#e9d5ff',
                }}
              >
                <strong>Coach Adaptation Decision:</strong> {weeklyAverages.adaptive_reason || 'Baseline — all biometrics normal.'}
              </div>
            </div>
          )}
          {/* CHART SECTION */}
          <div style={{ ...styles.bentoBox, ...dashboardLayout.chartSection }} className="bentoBox chartSection responsive-grid-span-8">
            <div style={styles.sectionHeader} className="sectionHeader">
              <div style={styles.sectionTitle} className="sectionTitle">
                <div style={styles.sectionAccent}></div> TRENDS
              </div>
              <div style={styles.chartControls}>
                <div style={styles.chartTabs}>
                  {['all', 'workout', 'meal', 'sleep', 'water'].map((m) => (
                    <button
                      key={m}
                      style={{
                        ...styles.chartTab,
                        ...(chartMode === m ? styles.chartTabActive : {})
                      }}
                      onClick={() => setChartMode(m)}
                    >
                      {m === 'all' ? 'ALL' : m.toUpperCase()}
                    </button>
                  ))}
                </div>
                <div style={styles.chartTabs}>
                  {['week', 'month'].map((p) => (
                    <button
                      key={p}
                      style={{
                        ...styles.chartTab,
                        ...(chartPeriod === p ? styles.chartTabActive : {})
                      }}
                      onClick={() => setChartPeriod(p)}
                    >
                      {p.toUpperCase()}
                    </button>
                  ))}
                </div>
              </div>
            </div>
            <ActivityChart data={chartData} mode={chartMode} period={chartPeriod} xLabels={chartXLabels} />
          </div>

          {/* ACTIVITY SECTION */}
          <div style={{ ...styles.bentoBox, ...dashboardLayout.activitySection }} className="bentoBox activitySection responsive-grid-span-4">
            <div style={styles.sectionHeader}>
              <div style={styles.sectionTitle}>
                <div style={styles.sectionAccent}></div> ACTIVITY
              </div>
            </div>
            <div className="activity-list" style={{ flex: 1, overflowY: 'auto', paddingRight: '4px' }}>
              {(() => {
                const todayDateStr = new Date().toLocaleDateString('en-CA'); // "YYYY-MM-DD" in local time
                const todaysHistory = recentHistory.filter(h => {
                  if (h.timestamp) {
                    return new Date(h.timestamp).toLocaleDateString('en-CA') === todayDateStr;
                  }
                  // fallback: entries without timestamp (legacy) — try the old heuristic
                  const todayStr = new Date().toLocaleDateString('en-US', { weekday: 'short', month: 'short', day: 'numeric' });
                  return h.date === todayStr || String(h.date).includes('Today');
                });
                
                return todaysHistory.length === 0 ? (
                <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', padding: '40px 20px', color: '#52525b' }}>
                  <div style={{ fontSize: '32px', marginBottom: '12px' }}>📋</div>
                  <div style={{ fontSize: '14px', fontWeight: '600', color: '#71717a' }}>No activity yet</div>
                  <div style={{ fontSize: '12px', color: '#52525b', marginTop: '4px' }}>Complete a workout or log a meal to see your activity here</div>
                </div>
              ) : (
              todaysHistory.map((h, i) => (
                <div key={i} style={styles.listRow} className="activity-row listRow">
                  <div style={{ display: 'flex', gap: '12px', alignItems: 'center' }}>
                    <div
                      style={{
                        width: '36px',
                        height: '36px',
                        borderRadius: '10px',
                        background:
                          h.type === 'workout'
                            ? 'rgba(34, 197, 94, 0.1)'
                            : h.type === 'meal'
                              ? 'rgba(236, 72, 153, 0.1)'
                              : h.type === 'sleep'
                                ? 'rgba(99, 102, 241, 0.1)'
                                : h.type === 'water'
                                  ? 'rgba(56, 189, 248, 0.1)'
                                  : 'rgba(245, 158, 11, 0.1)',
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'center',
                        fontSize: '16px'
                      }}
                    >
                      {h.type === 'workout'
                        ? '💪'
                        : h.type === 'meal'
                          ? '🥗'
                          : h.type === 'sleep'
                            ? '😴'
                            : h.type === 'water'
                              ? '💧'
                              : '📊'}
                    </div>
                    <div>
                      <div style={{ color: 'var(--app-text)', fontSize: '14px', fontWeight: '600' }}>
                        {h.name}
                      </div>
                      <div style={{ color: '#71717a', fontSize: '13px', fontFamily: 'sans-serif' }}>
                        {h.date}
                      </div>
                    </div>
                  </div>
                  <div style={{ fontSize: '12px', color: 'var(--app-text-muted)', fontWeight: '500' }}>
                    {h.details}
                  </div>
                </div>
              ))
              )
              })()}
            </div>
          </div>
        </div>

        {/* NOTIFICATIONS CONTAINER */}
        {activeToasts.length > 0 && (
          <div style={styles.notificationsContainer}>
            {activeToasts.map((notification) => (
              <div
                key={notification.id}
                style={{
                  ...styles.notificationItem,
                  ...(notification.type === 'success'
                    ? styles.notificationSuccess
                    : notification.type === 'warning'
                      ? styles.notificationWarning
                      : styles.notificationInfo)
                }}
              >
                <div style={styles.notificationContent}>
                  <span style={styles.notificationMessage}>{notification.message}</span>
                  <button
                    style={styles.notificationClose}
                    onClick={() => dismissToast(notification.id)}
                  >
                    ×
                  </button>
                </div>
              </div>
            ))}
          </div>
        )}

        {/* CONFIRM DIALOG */}
        <ConfirmDialog
          show={confirmDialog.show}
          message={confirmDialog.message}
          onConfirm={handleConfirm}
          onCancel={handleCancelConfirm}
        />
      </div>
    </>
  );
}

// Helper function to calculate dynamic water goal in Liters
const getDynamicWaterGoal = (weightKg = 70, sleepHours = 0, workoutCompleted = false) => {
  // Base requirement: 33ml per kg
  let targetLiters = weightKg * 0.033;
  
  // +500ml on workout days
  if (workoutCompleted) targetLiters += 0.5;
  
  // +250ml if sleep is poor (< 7 hours)
  if (sleepHours > 0 && sleepHours < 7) targetLiters += 0.25;
  
  return Math.min(5.0, Math.max(2.0, targetLiters));
};

export default Dashboard;
