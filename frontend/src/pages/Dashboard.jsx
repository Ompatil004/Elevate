import React, { useState, useEffect, useMemo, useRef, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import { useNotification } from '../components/NotificationProvider';
import ConfirmDialog from '../components/ConfirmDialog';
import {
  getProfile,
  saveTrends,
  getTrends,
  getExternalNutritionData,
  getExternalExerciseData,
} from '../api';
import Navbar from '../components/Navbar';
// BUG-F2/F8: ActivityChart extracted to its own component file (no Dashboard coupling)
import ActivityChart from '../components/dashboard/ActivityChart';
// BUG-F5: QUOTES lazy-loaded after mount to reduce initial bundle parse time.
import {
  getFromStorage,
  setToStorage,
  removeFromStorage,
  logoutSafe,
  StorageKeys,
  getTodayStr,
  safeJSONParse
} from '../utils/storage';
import { persistSessionUser } from '../utils/sessionUtils';
import { syncBridge, SyncTypes } from '../utils/syncBridge';


// --- FULL PREMIUM STYLES (JS Object - Static Only) ---
const styles = {
  page: {
    background: '#09090b',
    minHeight: '100dvh',
    color: '#e4e4e7',
    fontFamily: "'Inter', -apple-system, BlinkMacSystemFont, sans-serif",
    overflowX: 'hidden',
    backgroundImage: `
      radial-gradient(circle at 15% 50%, rgba(99, 102, 241, 0.08), transparent 25%),
      radial-gradient(circle at 85% 30%, rgba(139, 92, 246, 0.08), transparent 25%)
    `,
    paddingBottom: '40px'
  },
  dateDisplay: {
    fontSize: '13px',
    fontWeight: '600',
    color: '#a1a1aa',
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
    borderBottom: '1px solid rgba(255,255,255,0.08)',
    background: 'rgba(9, 9, 11, 0.6)',
    backdropFilter: 'blur(16px)',
    position: 'sticky',
    top: 0,
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
    color: '#a1a1aa',
    cursor: 'pointer',
    borderRadius: '20px',
    transition: 'all 0.2s',
    textTransform: 'uppercase',
    letterSpacing: '0.5px',
    border: '1px solid transparent'
  },
  navLinkActive: {
    background: 'rgba(255,255,255,0.1)',
    color: '#fff',
    boxShadow: '0 0 20px rgba(255,255,255,0.05)',
    border: '1px solid rgba(255,255,255,0.05)'
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
    background: 'rgba(255,255,255,0.03)',
    border: '1px solid rgba(255,255,255,0.08)',
    color: '#fff',
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
    background: '#18181b',
    border: '1px solid rgba(255,255,255,0.1)',
    borderRadius: '16px',
    padding: '16px',
    zIndex: 2000,
    boxShadow: '0 20px 50px rgba(0,0,0,0.5)',
    animation: 'slideDown 0.2s ease-out'
  },
  notifItem: {
    padding: '12px 16px',
    borderBottom: '1px solid rgba(255,255,255,0.05)',
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
    padding: 'clamp(12px, 4vw, 40px)',
    display: 'grid',
    gridTemplateColumns: 'repeat(12, 1fr)',
    gap: 'clamp(12px, 2.4vw, 24px)'
  },
  bentoBox: {
    background: '#18181b',
    border: '1px solid rgba(255,255,255,0.05)',
    borderRadius: '24px',
    padding: 'clamp(16px, 3vw, 32px)',
    display: 'flex',
    flexDirection: 'column',
    position: 'relative',
    overflow: 'hidden',
    transition: 'transform 0.2s ease, border-color 0.2s ease'
  },
  heroSection: {
    gridColumn: 'span 12',
    background: 'linear-gradient(120deg, #18181b 0%, #0f0f11 100%)',
    display: 'flex',
    flexDirection: 'row',
    flexWrap: 'wrap',
    alignItems: 'center',
    justifyContent: 'space-between',
    gap: 'clamp(12px, 2.5vw, 28px)',
    minHeight: 'auto',
    padding: 'clamp(14px, 3vw, 34px)',
    boxShadow: '0 20px 40px rgba(0,0,0,0.2)'
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
    width: 'clamp(88px, 16vw, 140px)',
    height: 'clamp(88px, 16vw, 140px)',
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
    background: '#18181b',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    fontSize: 'clamp(34px, 8vw, 64px)',
    fontWeight: '700',
    color: '#fff',
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
    border: '4px solid #18181b',
    color: '#fff',
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
    fontSize: 'clamp(30px, 6vw, 52px)',
    fontWeight: '800',
    background: 'linear-gradient(to right, #ffffff 0%, #a5b4fc 100%)',
    WebkitBackgroundClip: 'text',
    WebkitTextFillColor: 'transparent',
    margin: 0,
    whiteSpace: 'normal',
    display: 'flex',
    alignItems: 'center',
    gap: '10px',
    filter: 'drop-shadow(0 4px 20px rgba(99, 102, 241, 0.3))',
    lineHeight: '1.1'
  },
  quoteCard: {
    background: 'rgba(255,255,255,0.03)',
    borderLeft: '4px solid #6366f1',
    padding: '12px 18px',
    borderRadius: '0 12px 12px 0',
    fontStyle: 'italic',
    color: '#a1a1aa',
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
    width: 'min(100%, 300px)',
    minHeight: '154px',
    borderRadius: '24px',
    border: '1px solid rgba(255,255,255,0.16)',
    cursor: 'pointer',
    display: 'flex',
    flexDirection: 'column',
    alignItems: 'flex-start',
    justifyContent: 'space-between',
    gap: '10px',
    padding: '16px 16px 14px',
    textAlign: 'left',
    color: '#fff',
    transition: 'all 0.3s ease',
    textShadow: '0 2px 10px rgba(0,0,0,0.3)',
    position: 'relative',
    zIndex: 10,
    boxShadow: '0 14px 34px rgba(0,0,0,0.32)',
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
    width: '46px',
    height: '46px',
    borderRadius: '14px',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    fontSize: '22px',
    border: '1px solid rgba(255,255,255,0.3)',
    background: 'rgba(255,255,255,0.15)',
    boxShadow: 'inset 0 0 0 1px rgba(255,255,255,0.08)'
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
    fontSize: 'clamp(20px, 2.4vw, 24px)',
    fontWeight: '800',
    letterSpacing: '-0.3px',
    lineHeight: 1.15,
    color: '#ffffff'
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
    color: '#a1a1aa',
    textTransform: 'uppercase',
    letterSpacing: '1.2px',
    background: 'rgba(255,255,255,0.04)',
    border: '1px solid rgba(255,255,255,0.08)',
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
    color: '#a1a1aa',
    letterSpacing: '3px',
    textTransform: 'uppercase'
  },
  streakNumber: {
    fontSize: '78px',
    fontWeight: '900',
    lineHeight: 0.8,
    background: 'linear-gradient(to bottom, #fff 30%, #6366f1 100%)',
    WebkitBackgroundClip: 'text',
    WebkitTextFillColor: 'transparent',
    filter: 'drop-shadow(0 0 30px rgba(99,102,241,0.3))'
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
    background: '#27272a',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    fontSize: '16px',
    border: '1px solid rgba(255,255,255,0.05)',
    transition: 'all 0.3s cubic-bezier(0.25, 0.8, 0.25, 1)',
    cursor: 'default',
    fontWeight: '700',
    color: '#71717a'
  },
  dayActive: {
    background: 'rgba(99, 102, 241, 0.1)',
    borderColor: '#6366f1',
    boxShadow: '0 0 15px rgba(99, 102, 241, 0.2)',
    color: '#fff'
  },
  dayDone: {
    background: 'rgba(34, 197, 94, 0.1)',
    borderColor: '#22c55e',
    color: '#fff',
    boxShadow: '0 0 15px rgba(34, 197, 94, 0.2)'
  },
  statsRow: {
    gridColumn: 'span 12',
    display: 'grid',
    gridTemplateColumns: 'repeat(3, 1fr)',
    gap: '24px'
  },
  macroBarBG: {
    width: '100%',
    height: '8px',
    background: '#27272a',
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
    background: 'rgba(255,255,255,0.03)',
    borderRadius: '50px',
    padding: '4px',
    marginTop: '20px',
    border: '1px solid rgba(255,255,255,0.08)',
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
    color: '#fff',
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
    color: '#a1a1aa',
    letterSpacing: '1px',
    textTransform: 'uppercase'
  },
  chartSection: {
    gridColumn: 'span 8',
    height: '460px'
  },
  activitySection: {
    gridColumn: 'span 4',
    height: '460px',
    display: 'flex',
    flexDirection: 'column'
  },
  sectionHeader: {
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: '24px'
  },
  sectionTitle: {
    fontSize: 'clamp(18px, 2.8vw, 22px)',
    fontWeight: '800',
    color: '#fff',
    display: 'flex',
    alignItems: 'center',
    gap: '12px',
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
    background: 'rgba(255,255,255,0.05)',
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
    background: '#27272a',
    color: '#fff',
    boxShadow: '0 2px 10px rgba(0,0,0,0.2)'
  },
  listRow: {
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'space-between',
    padding: '18px 16px',
    borderBottom: '1px solid rgba(255,255,255,0.05)',
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
    background: '#18181b',
    borderRadius: '24px',
    padding: '10px',
    boxShadow: '0 25px 50px rgba(0,0,0,0.5)',
    border: '1px solid rgba(255,255,255,0.1)'
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
    background: '#fff',
    color: '#000',
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
    border: '1px solid rgba(255,255,255,0.1)',
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
    background: 'rgba(255, 255, 255, 0.1)',
    border: 'none',
    color: '#ffffff',
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
    color: '#e4e4e7',
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
    background: rgba(255, 255, 255, 0.08) !important;
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
    background: #27272a;
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

// BUG-F2/F8: ActivityChart extracted to components/dashboard/ActivityChart.jsx
// The component was fully self-contained (no Dashboard.jsx dependencies).
// See that file for configuration and implementation details.


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
      tagBg: 'rgba(255,255,255,0.08)',
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
      surface: 'linear-gradient(135deg, #3f3f46 0%, #27272a 100%)',
      border: '1px solid rgba(255,255,255,0.18)',
      shadow: '0 16px 30px rgba(0,0,0,0.34)',
      iconBg: 'rgba(255,255,255,0.15)',
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
      tagBg: 'rgba(255,255,255,0.08)',
      tagBorder: '1px solid rgba(255,255,255,0.2)',
      tagColor: '#e4e4e7',
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

  // --- STATE DECLARATIONS ---
  const [displayName, setDisplayName] = useState('Titan');
  const [userAvatar, setUserAvatar] = useState(null);
  const [showImageModal, setShowImageModal] = useState(false);
  const [showNotif, setShowNotif] = useState(false);
  const [confirmDialog, setConfirmDialog] = useState({
    show: false,
    message: '',
    onConfirm: null
  });
  const notifRef = useRef(null);

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
    fiber: 0
  });

  // ✅ FIX 2: Cross-page macro update — called when meal is saved from Nutrition page
  // Sets absolute macro values (not incremental) from today's totals returned by the backend
  const _setMacrosFromTotals = (totals) => {
    try {
      if (!totals) return;
      setMacros((prev) => ({
        ...prev,
        p: Math.round(Number(totals.protein) || prev.p),
        c: Math.round(Number(totals.carbs) || prev.c),
        f: Math.round(Number(totals.fat) || prev.f),
        calories: Math.round(Number(totals.calories) || prev.calories),
      }));
    } catch (error) {
      console.error('Error setting macros from totals:', error);
    }
  };

  const _updateMacrosFromMeal = (mealData) => {
    try {
      const protein = mealData.protein || 0;
      const carbs = mealData.carbs || 0;
      const fats = mealData.fat || mealData.fats || 0;
      const calories = mealData.calories || 0;
      const fiber = mealData.fiber || 0;

      setMacros((prev) => ({
        ...prev,
        p: Math.round(prev.p + protein),
        c: Math.round(prev.c + carbs),
        f: Math.round(prev.f + fats),
        calories: Math.round(prev.calories + calories),
        fiber: Math.round(prev.fiber + fiber)
      }));

      logActivity(
        'macros',
        'Macro Update',
        `+${calories} cal, +${protein}g P, +${carbs}g C, +${fats}g F`
      );
    } catch (error) {
      console.error('Error updating macros from meal:', error);
      showInfo('There was an issue updating your daily macros. Please try again.', 3000);
    }
  };

  // ✅ FIX: Initialize water/sleep from localStorage FIRST to prevent reset on page refresh
  // Then they'll be updated from backend when fetchUserData completes
  const [water, setWater] = useState(() => {
    try {
      const cached = getFromStorage(StorageKeys.WATER_INTAKE);
      return cached ? Number(cached) : 0;
    } catch {
      return 0;
    }
  });
  const [sleep, setSleep] = useState(() => {
    try {
      const cached = getFromStorage(StorageKeys.SLEEP_HOURS);
      return cached ? Number(cached) : 0;
    } catch {
      return 0;
    }
  });
  const [status, setStatus] = useState(null);
  const [dailyProgress, setDailyProgress] = useState(0); // 0-100, computed from real metrics
  const [mealsLoggedToday, setMealsLoggedToday] = useState(0); // 0-3: how many of breakfast/lunch/dinner done
  const [workoutProgress, setWorkoutProgress] = useState(0); // 0-1 ratio: exercises completed / total
  const [workoutIntensity] = useState(0);
  const [workoutPartial, setWorkoutPartial] = useState(false); // NEW: Track if workout was partial/skipped
  const [recoveryScore, setRecoveryScore] = useState(0);
  const [notifications, setNotifications] = useState([]);
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

  // PERF-7/8: Memoize breakpoint boolean — only recomputes when viewportWidth changes
  const isCompactLayout = useMemo(() => viewportWidth <= 1024, [viewportWidth]);
  // PERF-7/8: Memoized so spread of styles.statsRow etc. is only re-created
  // when the viewport crosses the 1024px breakpoint — not on every state update.
  const dashboardLayout = useMemo(() => ({
    statsRow: isCompactLayout
      ? { ...styles.statsRow, gridTemplateColumns: '1fr' }
      : styles.statsRow,
    chartSection: isCompactLayout
      ? { ...styles.chartSection, gridColumn: 'span 12', height: '340px' }
      : styles.chartSection,
    activitySection: isCompactLayout
      ? { ...styles.activitySection, gridColumn: 'span 12', height: '340px' }
      : styles.activitySection
  }), [isCompactLayout]);

  // PERF-7/8: todayDate changes at most once per day — memoize so
  // toLocaleDateString() is not called on every render.
  const todayDate = useMemo(() => new Date().toLocaleDateString('en-US', {
    weekday: 'short',
    month: 'short',
    day: 'numeric'
  }), []);

  // BUG-F5: Lazy-load quotes after first paint, then pick today's quote.
  const [currentQuote, setCurrentQuote] = useState('Stay hard.');
  useEffect(() => {
    import('../data/quotes').then(({ QUOTES: Q }) => {
      if (!Q || Q.length === 0) return;
      const now = new Date();
      const start = new Date(now.getFullYear(), 0, 0);
      const dayOfYear = Math.floor((now - start) / (1000 * 60 * 60 * 24));
      const infiniteIndex = dayOfYear + now.getFullYear() * 365;
      setCurrentQuote(Q[infiniteIndex % Q.length]);
    }).catch(() => { /* keep default */ });
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
      //    FIX: Don't give full points if workout was partial/skipped
      //    Only give full 25 if status is 'meal' or 'done' AND not a partial session
      let workoutPts;
      if ((status === 'meal' || status === 'done') && !workoutPartial) {
        workoutPts = 25; // full workout completed & logged
      } else if ((status === 'meal' || status === 'done') && workoutPartial) {
        // Partial session - give proportional points based on what was actually completed
        workoutPts = Math.round(workoutProgress * 25);
        console.log(`[Dashboard] Partial workout detected, giving ${workoutPts}/25 points (${Math.round(workoutProgress * 100)}% completed)`);
      } else {
        workoutPts = Math.round(workoutProgress * 25);
      }

      // 2. Meals (25 pts) — exact per-meal credit (breakfast/lunch/dinner = ~8.3pts each)
      const mealPts = Math.round((mealsLoggedToday / 3) * 25);

      // 3. Water (25 pts) — intake vs personal goal (weight × 0.033 L), updates per glass
      const userWeight = parseFloat(safeJSONParse('user', {})?.weight || '70');
      const waterGoal = parseFloat((userWeight * 0.033).toFixed(2)) || 2.3;
      const waterRatio = Math.min(1, water / waterGoal);
      const waterPts = Math.round(waterRatio * 25);

      // 4. Sleep (25 pts) — hours / 7h, updates every +30 min logged
      const sleepRatio = Math.min(1, sleep / 7);
      const sleepPts = Math.round(sleepRatio * 25);

      const total = workoutPts + mealPts + waterPts + sleepPts;
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
      if (data?.calories !== undefined) {
        _setMacrosFromTotals({
          calories: data.calories,
          protein: data.protein,
          carbs: data.carbs,
          fat: data.fat,
        });
      }
    });

    const unsubWorkoutProgress = syncBridge.subscribe(SyncTypes.WORKOUT_PROGRESS, (data) => {
      const completed = Number(data?.completedCount) || 0;
      const total = Math.max(1, Number(data?.totalCount) || 1);
      const ratio = Math.max(0, Math.min(1, completed / total));
      setWorkoutProgress(ratio);
      // Check if this is a partial session (some exercises skipped)
      const hasSkips = data?.hasSkipped === true || data?.fullyDone === false;
      if (hasSkips && ratio < 1) {
        setWorkoutPartial(true);
      }
    });

    const unsubWorkoutDone = syncBridge.subscribe(SyncTypes.WORKOUT_COMPLETED, () => {
      setWorkoutProgress(1);
      setWorkoutPartial(false); // Full completion, not partial
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

        // Keep session user profile in sync so other pages don't fall back to zero/default values.
        persistSessionUser(data);

        if (data.name) setDisplayName(data.name.split(' ')[0]);

        // ✅ BACKEND SYNC: Parse MongoDB history instead of localStorage
        const todayStr = getTodayStr();

        // Normalize meal history because backend can return either grouped day objects
        // or flat meal entries depending on write path.
        const normalizedMeals = normalizeMealEntries(data.meals || []);

        // Calculate exact macros eaten TODAY from MongoDB
        let cEaten = 0, pEaten = 0, fEaten = 0, carbEaten = 0;
        const mealsToday = normalizedMeals.filter(m => {
          const d = String(m.date || m.completedAt || '');
          return d.startsWith(todayStr);
        });
        mealsToday.forEach(m => {
           cEaten += Number(m.calories) || 0;
           pEaten += Number(m.protein) || 0;
           carbEaten += Number(m.carbs) || 0;
           fEaten += Number(m.fat) || 0;
        });
        // ✅ FIX: Round all macro values to integers
        cEaten = Math.round(cEaten);
        pEaten = Math.round(pEaten);
        carbEaten = Math.round(carbEaten);
        fEaten = Math.round(fEaten);

        const completedMealTypesToday = new Set(
          mealsToday.map((m) => String(m.meal_type || m.mealType || m.name || '').toLowerCase())
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
            const dt = cachedNutrition.days[0].daily_totals || cachedNutrition.daily_target;
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
          fiber: 0,
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
            combinedHistory.push({
                type: 'meal',
                name: m.name || m.mealType || 'Logged Meal',
                details: `${Math.round(Number(m.calories) || 0)} cal`,
                date: new Date(m.completedAt || m.date || new Date()).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
                timestamp: new Date(m.completedAt || m.date || new Date()).getTime(),
            });
        });

        const localActivity = getFromStorage(StorageKeys.ACTIVITY_HISTORY, []);
        const normalizedLocal = (Array.isArray(localActivity) ? localActivity : [])
          .filter((item) => item && typeof item === 'object')
          .map((item) => ({
            ...item,
            timestamp: Number(item.timestamp) || Date.now(),
          }));

        const mergedMap = new Map();
        [...combinedHistory, ...normalizedLocal].forEach((entry) => {
          const key = `${entry.type || ''}|${entry.name || ''}|${entry.details || ''}|${entry.timestamp || 0}`;
          if (!mergedMap.has(key)) {
            mergedMap.set(key, entry);
          }
        });

        const mergedHistory = Array.from(mergedMap.values())
          .sort((a, b) => (Number(b.timestamp) || 0) - (Number(a.timestamp) || 0));

        setRecentHistory(mergedHistory.slice(0, 5));
        setToStorage(StorageKeys.ACTIVITY_HISTORY, mergedHistory.slice(0, 50));

        // ✅ Avatar Sync
        const storedAvatar = getFromStorage(StorageKeys.USER_AVATAR);
        if (storedAvatar) setUserAvatar(storedAvatar);

        // ✅ State Sync from DB Trends (Water, Sleep, Streak)
        if (data.trends && Array.isArray(data.trends)) {
           console.log(`[Dashboard] Loaded ${data.trends.length} trend entries from backend`);
           // Synchronize today's latest data points
           const todayRecord = data.trends.find(t => String(t.date).startsWith(todayStr));
           if (todayRecord) {
             console.log('[Dashboard] Found today\'s trend record:', todayRecord);
             if (todayRecord.water_intake !== undefined) {
               const waterValue = Number(todayRecord.water_intake);
               console.log(`[Dashboard] Setting water from backend: ${waterValue}L`);
               setWater(waterValue);
               setToStorage(StorageKeys.WATER_INTAKE, String(waterValue));
             }
             if (todayRecord.water_glasses !== undefined) {
               const waterValue = Number(todayRecord.water_glasses);
               console.log(`[Dashboard] Setting water from water_glasses: ${waterValue}L`);
               setWater(waterValue);
               setToStorage(StorageKeys.WATER_INTAKE, String(waterValue));
             }
             if (todayRecord.sleep_duration !== undefined) {
               const sleepValue = Number(todayRecord.sleep_duration);
               console.log(`[Dashboard] Setting sleep from backend: ${sleepValue}h`);
               setSleep(sleepValue);
               setToStorage(StorageKeys.SLEEP_HOURS, String(sleepValue));
             }
             if (todayRecord.sleep_hours !== undefined) {
               const sleepValue = Number(todayRecord.sleep_hours);
               console.log(`[Dashboard] Setting sleep from sleep_hours: ${sleepValue}h`);
               setSleep(sleepValue);
               setToStorage(StorageKeys.SLEEP_HOURS, String(sleepValue));
             }
           } else {
             console.log('[Dashboard] No trend record found for today:', todayStr);
             setWorkoutPartial(false);
             removeFromStorage('TODAY_WORKOUT_ATTEMPTED');
           }

           // Also check for workout_partial flag
           if (todayRecord?.workout_partial === true) {
             console.log('[Dashboard] Found partial workout flag for today');
             setWorkoutPartial(true);
           }
           if (todayRecord?.workout_attempted === true) {
             console.log('[Dashboard] Found workout_attempted flag for today');
             setToStorage('TODAY_WORKOUT_ATTEMPTED', 'true');
           } else if (todayRecord) {
             removeFromStorage('TODAY_WORKOUT_ATTEMPTED');
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
           const dateCursor = new Date(todayStr);
           for (let attempts = 0; attempts < 365; attempts++) {
             if (dateCursor < registrationDate) {
               break;
             }

             const dateKey = dateCursor.toISOString().split('T')[0];
             const entry = trendsByDate.get(dateKey);

             if (!entry) break; // No record for this date = streak broken

             const mealDone = !!entry.meal_completed;
             const workoutDone = !!entry.workout_completed;
             const restDay = isRestDayForDate(dateCursor);
             const dayCompleted = mealDone && (workoutDone || restDay);

             if (dayCompleted) {
               currentStreak++;
               dateCursor.setDate(dateCursor.getDate() - 1);
             } else {
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
             const dateKey = dayDate.toISOString().split('T')[0];
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
           // Fallback to workout count
           const workouts = data.workouts || [];
           const uniqueDays = new Set(workouts.map(w => (w.date || '').split('T')[0]));
           setStats((prev) => ({ ...prev, streak: uniqueDays.size }));

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

  // ✅ UPDATED: Daily reset logic with storage utilities
  const checkDailyReset = async () => {
    try {
      const today = getTodayStr();
      const lastActivityDate = getFromStorage(StorageKeys.LAST_ACTIVITY_DATE);
      const dailyResetPerformed = getFromStorage(StorageKeys.DAILY_RESET_PERFORMED);

      if (lastActivityDate !== today || dailyResetPerformed !== today) {
        setToStorage(StorageKeys.LAST_ACTIVITY_DATE, today);
        setToStorage(StorageKeys.DAILY_RESET_PERFORMED, today);
        // ✅ FIX: Do NOT call resetDailyMacros() here!
        // Macros are loaded from MongoDB by fetchUserData() and are authoritative.
        // Zeroing them would overwrite the real data from the database.
        // Keep status unchanged here; checkDayReset() derives the final state
        // after backend sync to avoid startup button flicker.
        setNotifications([]);
        removeFromStorage(StorageKeys.TODAY_WORKOUT_DONE);
        removeFromStorage(StorageKeys.TODAY_MEALS_DONE);
        
        // Clear notification flags
        for (let i = 0; i < localStorage.length; i++) {
          const key = localStorage.key(i);
          if (key && (key.includes('notification_') || key.includes('reminder_'))) {
            removeFromStorage(key);
          }
        }
      }
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
          const mealsToday = normalizedMeals.filter(m => {
            const d = String(m.date || m.completedAt || '');
            return d.startsWith(todayStr);
          });
          let cEaten = 0, pEaten = 0, carbEaten = 0, fEaten = 0;
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
            calories: Math.round(cEaten)
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
          const completedMealTypes = new Set(
            mealsToday.map(m => String(m.meal_type || m.mealType || m.name || '').toLowerCase())
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
            }));
            // ✅ If Nutrition page signals the meal count, update circle immediately
            if (totals.mealsCount !== undefined) {
              setMealsLoggedToday(Math.min(3, Math.max(0, Number(totals.mealsCount) || 0)));
            }
            console.log('✅ Dashboard macros updated from Nutrition sync:', totals);
          }
        } catch { /* ignore parse errors */ }
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
        } catch { /* ignore */ }
      }
    };
    window.addEventListener('storage', handleStorageSync);
    return () => window.removeEventListener('storage', handleStorageSync);
  }, []);

  const addNotification = useCallback((message, type = 'info') => {
    const newNotification = {
      id: Date.now() + Math.random(),
      message,
      type,
      timestamp: new Date()
    };
    setNotifications((prev) => [...prev, newNotification]);
    setTimeout(
      () => setNotifications((prev) => prev.filter((n) => n.id !== newNotification.id)),
      5000
    );
  }, []);

  const dismissNotification = (id) =>
    setNotifications((prev) => prev.filter((n) => n.id !== id));

  const handleClickOutside = (event) => {
    if (notifRef.current && !notifRef.current.contains(event.target))
      setShowNotif(false);
  };

  useEffect(() => {
    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  // ✅ UPDATED: logActivity uses storage utility
  const logActivity = (type, name, details) => {
    const newLog = {
      name,
      date: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
      details,
      type,
      timestamp: Date.now(),
    };
    setRecentHistory((prev) => {
      const updated = [newLog, ...prev];
      setToStorage(StorageKeys.ACTIVITY_HISTORY, updated);
      return updated;
    });
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
      const waterGoal = parseFloat((userWeight * 0.033).toFixed(1));
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
        const waterGoal = parseFloat((userWeight * 0.033).toFixed(1));
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
        const waterGoal = parseFloat((userWeight * 0.033).toFixed(1));
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
    checkDailyReminders();
    const interval = setInterval(checkDailyReminders, 60 * 60 * 1000);
    return () => clearInterval(interval);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  useEffect(() => {
    const handleResize = () => {};
    window.addEventListener('resize', handleResize);
    return () => window.removeEventListener('resize', handleResize);
  }, []);

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

  // ✅ BACKEND PERSISTENCE: Debounce-sync water & sleep to MongoDB trends
  // IMPROVED: Added error handling and user notification on failure
  const latestDataRef = useRef({ water: 0, sleep: 0 });
  const isDirtyRef = useRef(false);
  useEffect(() => {
    // Wait for initial profile hydration before attempting background sync.
    if (loading) return;

    // Don't sync on initial mount (values are 0)
    if (water === 0 && sleep === 0) return;

    latestDataRef.current = { water, sleep };
    isDirtyRef.current = true;

    const timer = setTimeout(async () => {
      const todayStr = getTodayStr();
      try {
        await saveTrends({
          date: todayStr,
          water_intake: water,
          water_glasses: water,
          sleep_duration: sleep,
          sleep_hours: sleep,
        });
        // Successfully saved - update localStorage with confirmed values
        isDirtyRef.current = false;
        setToStorage(StorageKeys.WATER_INTAKE, String(water));
        setToStorage(StorageKeys.SLEEP_HOURS, String(sleep));
      } catch (err) {
        console.error('[Dashboard] Failed to sync water/sleep to backend:', err);
        // Only treat confirmed session-expiry as logout-worthy.
        const status = err?.response?.status;
        const code = err?.response?.data?.code;
        if (status === 401 && code === 'SESSION_EXPIRED') {
          console.error('[Dashboard] Session expired during trend sync');
          showInfo('Session expired. Please refresh the page or re-login to save your data.', 5000);
        } else if (status === 401) {
          console.error('[Dashboard] Unauthorized trend sync request');
          showInfo('Could not verify your session for saving. Please try again.', 3500);
        } else if (status === 403) {
          // 403 can happen transiently (e.g. CSRF token refresh race on reload).
          showInfo('Sync delayed for a moment. Retrying automatically...', 2500);
        } else {
          showInfo('Failed to save water/sleep data. Will retry automatically.', 3000);
        }
        // Retry once after 5 seconds
        setTimeout(async () => {
          try {
            await saveTrends({
              date: todayStr,
              water_intake: water,
              water_glasses: water,
              sleep_duration: sleep,
              sleep_hours: sleep,
            });
          } catch (retryErr) {
            console.error('[Dashboard] Retry also failed:', retryErr);
          }
        }, 5000);
      }
    }, 1500); // 1.5 second debounce to batch rapid clicks

    return () => clearTimeout(timer);
  }, [water, sleep, loading, showInfo]);

  // Flush unsaved data on unmount (e.g., when logging out rapidly)
  useEffect(() => {
    return () => {
      if (isDirtyRef.current) {
        const { water, sleep } = latestDataRef.current;
        const now = new Date();
        const yyyy = now.getFullYear();
        const mm = String(now.getMonth() + 1).padStart(2, '0');
        const dd = String(now.getDate()).padStart(2, '0');
        const todayStr = `${yyyy}-${mm}-${dd}`;
        
        saveTrends({
          date: todayStr,
          water_intake: water,
          water_glasses: water,
          sleep_duration: sleep,
          sleep_hours: sleep,
        }).catch((err) => console.error('[Dashboard] Unmount flush failed:', err));
      }
    };
  }, []); // Empty dependency array ensures this cleanup ONLY runs on unmount

  const updateRecoveryScore = (currentWater, currentSleep) => {
    const userWeight = parseFloat(safeJSONParse('user', {})?.weight || '70');
    const waterGoal = parseFloat((userWeight * 0.033).toFixed(1));
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
      const waterGoal = parseFloat((userWeight * 0.033).toFixed(1)) || 2.3;
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
      const waterGoal = parseFloat((userWeight * 0.033).toFixed(1)) || 2.3;
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
      const response = await getExternalNutritionData(foodQuery);
      if (response?.data?.success && response?.data?.data) {
        return response.data.data;
      }
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
    } catch (error) {
      console.error('Nutrition proxy error:', error.message);
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
      const response = await getExternalExerciseData(exerciseQuery);
      const data = response?.data?.data;
      if (Array.isArray(data) && data.length > 0) {
        return data;
      }
      return [{
        name: exerciseQuery || 'generic exercise',
        type: 'strength',
        muscle: exerciseQuery || 'mixed',
        equipment: 'bodyweight',
        difficulty: 'beginner',
        instructions: 'Perform the exercise with proper form'
      }];
    } catch (error) {
      console.error('Exercise proxy error:', error.message);
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
      const waterGoal = parseFloat((userWeight * 0.033).toFixed(2)) || 2.3;
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
          if (mode === 'workout') return bucket.filter(e => e?.workout_completed).length;
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

        trends.forEach((entry) => {
          const dateObj = new Date(entry?.date);
          if (Number.isNaN(dateObj.getTime())) return;
          const jsDay = dateObj.getDay();
          const idx = jsDay === 0 ? 6 : jsDay - 1;

          if (mode === 'all') {
            const score = calculateOverallTrendScore(entry, calorieGoal, waterGoal);
            series[idx] = Math.max(series[idx], score);
          }
          else if (mode === 'workout') series[idx] = entry?.workout_completed ? 1 : 0;
          else if (mode === 'meal') series[idx] = entry?.calories || (entry?.meal_completed ? 1 : 0);
          else if (mode === 'water') series[idx] = entry?.water_intake || entry?.water_glasses || 0;
          else if (mode === 'sleep') series[idx] = entry?.sleep_duration || entry?.sleep_hours || 0;
        });

        // Keep today's slot live for selected realtime modes.
        if (mode === 'water' || mode === 'sleep' || mode === 'all') {
          const todayJsDay = new Date().getDay();
          const todayIdx = todayJsDay === 0 ? 6 : todayJsDay - 1;
          if (mode === 'water') series[todayIdx] = Math.max(series[todayIdx], water);
          if (mode === 'sleep') series[todayIdx] = Math.max(series[todayIdx], sleep);
          if (mode === 'all') series[todayIdx] = Math.max(series[todayIdx], dailyProgress);
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
        fiber: macros.fiber || 0,
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
        const waterGoal = parseFloat((userWeight * 0.033).toFixed(2)) || 2.3;
        const calorieGoal = Math.max(1, Number(macros.calMax) || 2200);
        newChartData[adjustedIndex] = calculateOverallTrendScore(trendData, calorieGoal, waterGoal);
      }

      setChartData(newChartData);
    } catch (error) {
      console.error('Error updating local trend data:', error);
    }
  };

  // ✅ UPDATED: Day reset uses deriving from backend or fallback to storage
  // FIX: Added support for workout_attempted flag so partial/skipped sessions can progress
  const checkDayReset = async (forceWorkoutDone, forceMealDone) => {
    try {
      const todayStr = getTodayStr();
      const workoutDoneFlag = forceWorkoutDone !== undefined ? forceWorkoutDone : getFromStorage(StorageKeys.TODAY_WORKOUT_DONE) === 'true';
      const mealDoneFlag = forceMealDone !== undefined ? forceMealDone : getFromStorage(StorageKeys.TODAY_MEALS_DONE) === 'true';
      const workoutAttempted = getFromStorage('TODAY_WORKOUT_ATTEMPTED') === 'true'; // NEW

      const restDayToday = isRestDayForDate(new Date());
      if (restDayToday) {
        if (mealDoneFlag) setStatus('done');
        else setStatus('meal');
      } else if (!workoutDoneFlag && !workoutAttempted) {
        // Only show workout status if user hasn't attempted yet
        setStatus('workout');
      } else if (!workoutDoneFlag && workoutAttempted) {
        // User attempted but didn't complete (skipped/partial) - let them proceed to meals
        console.log('[Dashboard] Workout was attempted but not completed, transitioning to meal stage');
        setStatus('meal');
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

        {/* BUG-F3/F13: Replaced inline nav with shared Navbar component */}
        <Navbar
          navigate={navigate}
          activePage="dashboard"
          onLogout={handleLogout}
          rightContent={
            <>
              <div style={styles.dateDisplay}>{todayDate}</div>
              <div style={{ position: 'relative' }} ref={notifRef}>
                <button
                  style={styles.iconButton}
                  className="icon-hover"
                  onClick={() => setShowNotif(!showNotif)}
                >
                  🔔
                </button>
                {showNotif && (
                  <div style={styles.notifDropdown}>
                    <div style={{ fontSize: '14px', fontWeight: '700', color: '#fff', marginBottom: '12px' }}>
                      Notifications
                    </div>
                    {notifications.length === 0 ? (
                      <div style={{...styles.notifItem, borderBottom: 'none', color: '#a1a1aa', fontSize: '12px', justifyContent: 'center', marginTop: '8px'}}>
                          No new alerts
                      </div>
                    ) : (
                      notifications.map((n, idx) => (
                        <div key={n.id} style={{
                            ...styles.notifItem,
                            borderBottom: idx === notifications.length - 1 ? 'none' : '1px solid #27272a',
                            padding: '8px 0',
                            fontSize: '12px',
                            color: '#e4e4e7',
                            display: 'flex',
                            alignItems: 'center',
                            gap: '8px'
                        }}>
                            <span>{n.type === 'error' ? '❌' : n.type === 'warning' ? '⚠️' : 'ℹ️'}</span>
                            <span style={{lineHeight: '1.4'}}>{n.message}</span>
                        </div>
                      ))
                    )}
                  </div>
                )}
              </div>
            </>
          }
        />

        {/* MAIN CONTAINER */}
        <div style={styles.container} className="container">

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
                <div style={{ fontSize: '24px', fontWeight: '800', color: '#fff', letterSpacing: '-0.5px' }}>Hydration Complete!</div>
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
                <div style={{ fontSize: '24px', fontWeight: '800', color: '#fff', letterSpacing: '-0.5px' }}>Optimal Sleep!</div>
                <div style={{ fontSize: '14px', color: '#c4b5fd', marginTop: '4px' }}>You hit the 7-9 hour sweet spot</div>
              </div>
            </div>
          )}

          {/* HERO SECTION */}
          <div style={{ ...styles.bentoBox, ...styles.heroSection }} className="bentoBox heroSection">
            <div style={styles.heroLeft} className="heroLeft">
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

            <div style={styles.heroCenter} className="heroCenter">
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
                    ? 'Completed'
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
                      background: heroTheme.surface,
                      border: heroTheme.border,
                      boxShadow: heroTheme.shadow,
                      backdropFilter: 'blur(10px)',
                      cursor: heroAction.disabled ? 'default' : 'pointer'
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
                          background: `conic-gradient(${heroTheme.ringColor} ${radialScore}%, rgba(255,255,255,0.08) ${radialScore}% 100%)`,
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
                            background: heroTheme.coreBg,
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

            <div style={styles.heroRight} className="heroRight">
              <div style={{ textAlign: 'right' }}>
                <div style={styles.streakLabel}>CURRENT STREAK</div>
                <div style={{ display: 'flex', gap: 15, flexWrap: 'wrap', justifyContent: 'flex-end' }}>
                  <div style={styles.streakNumber} className="streakNumber">
                    {stats.streak}
                  </div>
                  <div style={{ fontSize: 'clamp(42px, 10vw, 80px)', animation: 'float 3s infinite' }}>🔥</div>
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
          <div style={dashboardLayout.statsRow}>
            {/* MACROS BOX */}
            <div style={{ ...styles.bentoBox }} className="hover-card">
              <div
                style={{
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'space-between',
                  marginBottom: '16px'
                }}
              >
                <div style={{ fontSize: '14px', fontWeight: '700', color: '#fff' }}>
                  MACROS TODAY
                </div>
                <div style={{ fontSize: '12px', color: '#a1a1aa' }}>
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
                    color: '#fff',
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
                      background: '#fff'
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
                  <div style={{ fontSize: '10px', color: '#a1a1aa', marginBottom: '4px' }}>
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
                  <div style={{ fontSize: '10px', color: '#a1a1aa', marginBottom: '4px' }}>
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
                  <div style={{ fontSize: '10px', color: '#a1a1aa', marginBottom: '4px' }}>
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
              {/* Recovery Score - combines water, sleep, and workout completion */}
              {(() => {
                const userWeight = parseFloat(safeJSONParse('user', {})?.weight || '70');
                const waterGoal = parseFloat((userWeight * 0.033).toFixed(1)) || 2.3;
                const waterScore = Math.min(100, (water / waterGoal) * 100);
                const sleepScore = Math.min(100, (sleep / 8) * 100);
                const recoveryScore = Math.round((waterScore + sleepScore) / 2);
                
                let recoveryLabel = 'Needs Work';
                let recoveryColor = '#ef4444';
                if (recoveryScore >= 90) {
                  recoveryLabel = 'Excellent';
                  recoveryColor = '#22c55e';
                } else if (recoveryScore >= 70) {
                  recoveryLabel = 'Good';
                  recoveryColor = '#3b82f6';
                } else if (recoveryScore >= 50) {
                  recoveryLabel = 'Fair';
                  recoveryColor = '#f59e0b';
                }
                
                return (
                <div
                  className="macro-item"
                  style={{ marginTop: '12px', cursor: 'pointer' }}
                  title={`Recovery Score: ${recoveryScore}% - Based on hydration and sleep goals`}
                >
                  <div
                    style={{
                      display: 'flex',
                      justifyContent: 'space-between',
                      fontSize: '11px',
                      color: '#a1a1aa',
                      marginBottom: '4px'
                    }}
                  >
                    <span>Recovery Score</span>
                    <span style={{ color: recoveryColor, fontWeight: '700' }}>
                      {recoveryScore}% - {recoveryLabel}
                    </span>
                  </div>
                  <div style={{ ...styles.macroBarBG, overflow: 'hidden' }}>
                    <div
                      style={{
                        ...styles.macroBarFill,
                        width: `${recoveryScore}%`,
                        background: `linear-gradient(90deg, ${recoveryColor}, ${recoveryColor}dd)`
                      }}
                    ></div>
                  </div>
                </div>
                );
              })()}
            </div>

            {/* HYDRATION BOX */}
            {(() => {
              const userWeight = parseFloat(safeJSONParse('user', {})?.weight || '70');
              const waterGoal = parseFloat((userWeight * 0.033).toFixed(1));
              const waterPercent = Math.min(100, Math.round((water / waterGoal) * 100));
              return (
              <div
                style={{
                  ...styles.bentoBox,
                  background: 'linear-gradient(135deg, #1e3a8a 0%, #172554 100%)',
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
                    <div style={{ fontSize: '14px', fontWeight: '700', color: '#fff' }}>HYDRATION</div>
                    <div style={{ fontSize: '12px', fontWeight: '700', color: waterPercent >= 100 ? '#34d399' : '#93c5fd' }}>{waterPercent}%</div>
                  </div>
                  <div style={{ flex: 1, display: 'flex', flexDirection: 'column', justifyContent: 'center', alignItems: 'center' }}>
                    <div style={{ fontSize: '48px', fontWeight: '800', color: '#fff' }}>
                      {water.toFixed(1)} <span style={{ fontSize: '16px', fontWeight: '500', color: '#93c5fd' }}>L</span>
                    </div>
                    <div style={{ fontSize: '12px', color: '#bfdbfe' }}>Goal: {waterGoal} L ({Math.round(userWeight)}kg)</div>
                    {/* Progress bar */}
                    <div style={{ width: '80%', height: '4px', background: 'rgba(255,255,255,0.1)', borderRadius: '2px', marginTop: '8px', overflow: 'hidden' }}>
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
              <div style={{ ...styles.bentoBox, position: 'relative', overflow: 'hidden' }} className="hover-card bentoBox">
                <div style={{ position: 'absolute', bottom: '-20px', left: '50%', transform: 'translateX(-50%)', width: '150px', height: '80px', background: `radial-gradient(circle, ${qualityColor}15 0%, transparent 70%)`, transition: 'all 0.6s ease' }} />
                <div style={{ position: 'relative', zIndex: 1, display: 'flex', flexDirection: 'column', height: '100%' }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                    <div style={{ fontSize: '14px', fontWeight: '700', color: '#fff', marginBottom: '10px' }}>SLEEP</div>
                    <div style={{ fontSize: '12px', fontWeight: '700', padding: '2px 10px', borderRadius: '12px', background: `${qualityColor}15`, color: qualityColor, border: `1px solid ${qualityColor}30` }}>
                      {qualityLabel}
                    </div>
                  </div>
                  <div style={{ flex: 1, display: 'flex', flexDirection: 'column', justifyContent: 'center', alignItems: 'center' }}>
                    <div style={{ fontSize: '48px', fontWeight: '800', color: '#fff', fontFamily: 'monospace' }}>
                      {Math.floor(sleep)}<span style={{ color: '#6366f1' }}>:</span>{String(Math.round((sleep % 1) * 60)).padStart(2, '0')}
                    </div>
                    <div style={{ fontSize: '12px', color: '#a1a1aa' }}>Hours Slept • Target 7-9h</div>
                    <div style={{ width: '80%', height: '4px', background: 'rgba(255,255,255,0.1)', borderRadius: '2px', marginTop: '8px', overflow: 'hidden' }}>
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
            })()}
          </div>


          {/* CHART SECTION */}
          <div style={{ ...styles.bentoBox, ...dashboardLayout.chartSection }} className="bentoBox chartSection">
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
          <div style={{ ...styles.bentoBox, ...dashboardLayout.activitySection }} className="bentoBox activitySection">
            <div style={styles.sectionHeader}>
              <div style={styles.sectionTitle}>
                <div style={styles.sectionAccent}></div> ACTIVITY
              </div>
            </div>
            <div className="activity-list" style={{ flex: 1, overflowY: 'auto', paddingRight: '4px' }}>
              {recentHistory.length === 0 ? (
                <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', padding: '40px 20px', color: '#52525b' }}>
                  <div style={{ fontSize: '32px', marginBottom: '12px' }}>📋</div>
                  <div style={{ fontSize: '14px', fontWeight: '600', color: '#71717a' }}>No activity yet</div>
                  <div style={{ fontSize: '12px', color: '#52525b', marginTop: '4px' }}>Complete a workout or log a meal to see your activity here</div>
                </div>
              ) : (
              recentHistory.map((h, i) => (
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
                      <div style={{ color: '#fff', fontSize: '14px', fontWeight: '600' }}>
                        {h.name}
                      </div>
                      <div style={{ color: '#71717a', fontSize: '13px', fontFamily: 'sans-serif' }}>
                        {h.date}
                      </div>
                    </div>
                  </div>
                  <div style={{ fontSize: '12px', color: '#a1a1aa', fontWeight: '500' }}>
                    {h.details}
                  </div>
                </div>
              ))
              )}
            </div>
          </div>
        </div>

        {/* NOTIFICATIONS CONTAINER */}
        {notifications.length > 0 && (
          <div style={styles.notificationsContainer}>
            {notifications.map((notification) => (
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
                    onClick={() => dismissNotification(notification.id)}
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

export default Dashboard;
