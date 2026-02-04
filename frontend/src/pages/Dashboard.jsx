import React, { useState, useEffect, useMemo, useRef, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import { useNotification } from '../components/NotificationProvider';
import ConfirmDialog from '../components/ConfirmDialog';
import { getProfile, updateStreak as updateStreakAPI, saveTrends, getTrends } from '../api';
import { QUOTES } from '../data/quotes';
import {
  getFromStorage,
  setToStorage,
  removeFromStorage,
  clearAllStorage,
  keyExistsInStorage,
  StorageKeys,
  getMultipleFromStorage,
  setMultipleToStorage
} from '../utils/storage';

// Helper function to get today's date string
const getTodayStr = () => new Date().toISOString().split('T')[0];

// --- FULL PREMIUM STYLES (JS Object - Static Only) ---
const styles = {
  page: {
    background: '#09090b',
    minHeight: '100vh',
    color: '#e4e4e7',
    fontFamily: "'Inter', -apple-system, BlinkMacSystemFont, sans-serif",
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
    padding: '0 40px',
    height: '80px',
    borderBottom: '1px solid rgba(255,255,255,0.08)',
    background: 'rgba(9, 9, 11, 0.6)',
    backdropFilter: 'blur(16px)',
    position: 'sticky',
    top: 0,
    zIndex: 1000
  },
  brand: {
    flex: 1,
    fontSize: '22px',
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
    gap: '8px',
    height: '100%',
    alignItems: 'center',
    justifyContent: 'center'
  },
  navLink: {
    display: 'flex',
    alignItems: 'center',
    padding: '8px 20px',
    fontSize: '13px',
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
    gap: '24px',
    justifyContent: 'flex-end'
  },
  iconButton: {
    width: '42px',
    height: '42px',
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
    width: '340px',
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
    padding: '0 20px',
    borderRadius: '12px',
    background: 'rgba(239, 68, 68, 0.1)',
    border: '1px solid rgba(239, 68, 68, 0.2)',
    color: '#ef4444',
    cursor: 'pointer',
    transition: 'all 0.2s ease',
    height: '42px'
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
    padding: '40px',
    display: 'grid',
    gridTemplateColumns: 'repeat(12, 1fr)',
    gap: '24px'
  },
  bentoBox: {
    background: '#18181b',
    border: '1px solid rgba(255,255,255,0.05)',
    borderRadius: '24px',
    padding: '32px',
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
    alignItems: 'center',
    justifyContent: 'space-between',
    gap: '40px',
    minHeight: '360px',
    padding: '48px',
    boxShadow: '0 20px 40px rgba(0,0,0,0.2)'
  },
  heroLeft: {
    display: 'flex',
    alignItems: 'flex-start',
    gap: '32px',
    flex: 1.2,
    minWidth: '400px'
  },
  avatarWrapper: {
    position: 'relative',
    width: '160px',
    height: '160px',
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
    fontSize: '64px',
    fontWeight: '700',
    color: '#fff',
    objectFit: 'cover'
  },
  editIconBadge: {
    position: 'absolute',
    bottom: '5px',
    right: '5px',
    width: '40px',
    height: '40px',
    borderRadius: '50%',
    background: '#4f46e5',
    border: '4px solid #18181b',
    color: '#fff',
    fontSize: '18px',
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
    gap: '12px',
    paddingTop: '15px'
  },
  h1: {
    fontSize: '52px',
    fontWeight: '800',
    background: 'linear-gradient(to right, #ffffff 0%, #a5b4fc 100%)',
    WebkitBackgroundClip: 'text',
    WebkitTextFillColor: 'transparent',
    margin: 0,
    whiteSpace: 'nowrap',
    display: 'flex',
    alignItems: 'center',
    gap: '10px',
    filter: 'drop-shadow(0 4px 20px rgba(99, 102, 241, 0.3))',
    lineHeight: '1.1'
  },
  quoteCard: {
    background: 'rgba(255,255,255,0.03)',
    borderLeft: '4px solid #6366f1',
    padding: '16px 24px',
    borderRadius: '0 12px 12px 0',
    fontStyle: 'italic',
    color: '#a1a1aa',
    fontSize: '15px',
    lineHeight: '1.6',
    marginTop: '8px',
    maxWidth: '450px'
  },
  heroCenter: {
    flex: 0.8,
    display: 'flex',
    justifyContent: 'center',
    alignItems: 'center'
  },
  circleBtn: {
    width: '200px',
    height: '200px',
    borderRadius: '50%',
    border: 'none',
    cursor: 'pointer',
    display: 'flex',
    flexDirection: 'column',
    alignItems: 'center',
    justifyContent: 'center',
    gap: '8px',
    color: '#fff',
    transition: 'all 0.3s ease',
    textShadow: '0 2px 10px rgba(0,0,0,0.3)',
    position: 'relative',
    zIndex: 10
  },
  btnBlue: {
    background: 'linear-gradient(135deg, #4f46e5 0%, #312e81 100%)'
  },
  btnPink: {
    background: 'linear-gradient(135deg, #ec4899 0%, #be185d 100%)'
  },
  btnGreen: {
    background: 'linear-gradient(135deg, #22c55e 0%, #14532d 100%)'
  },
  heroRight: {
    display: 'flex',
    flexDirection: 'column',
    alignItems: 'flex-end',
    justifyContent: 'center',
    gap: '20px',
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
    fontSize: '90px',
    fontWeight: '900',
    lineHeight: 0.8,
    background: 'linear-gradient(to bottom, #fff 30%, #6366f1 100%)',
    WebkitBackgroundClip: 'text',
    WebkitTextFillColor: 'transparent',
    filter: 'drop-shadow(0 0 30px rgba(99,102,241,0.3))'
  },
  weekGrid: {
    display: 'flex',
    gap: '10px'
  },
  dayCircle: {
    width: '46px',
    height: '46px',
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
    maxWidth: '280px'
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
    height: '550px'
  },
  activitySection: {
    gridColumn: 'span 4',
    height: '550px',
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
    fontSize: '22px',
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
    gap: '16px'
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

  .btn-blue-pulse:hover,
  .btn-pink-pulse:hover,
  .btn-green-pulse:hover {
    animation-duration: 1s;
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

  @keyframes pulse-blue-intense {
    0% {
      box-shadow: 0 0 7px 0 rgba(79, 70, 229, 0.6);
      transform: scale(1.03);
    }
    50% {
      box-shadow: 0 0 30px 8px rgba(79, 70, 229, 0.45);
      transform: scale(1.04);
    }
    100% {
      box-shadow: 0 0 7px 0 rgba(79, 70, 229, 0.6);
      transform: scale(1.03);
    }
  }

  .btn-blue-pulse {
    box-shadow: 0 0 0 0 rgba(79, 70, 229, 0.5);
    animation: pulse-blue-intense 2.5s infinite;
  }

  .btn-pink-pulse {
    box-shadow: 0 0 0 0 rgba(236, 72, 153, 0.5);
    animation: pulse-blue-intense 2.5s infinite;
  }

  .btn-pink-pulse:hover {
    box-shadow: 0 0 30px 8px rgba(236, 72, 153, 0.45);
  }

  .btn-green-pulse {
    box-shadow: 0 0 0 0 rgba(34, 197, 94, 0.5);
    animation: pulse-blue-intense 2.5s infinite;
  }

  .btn-green-pulse:hover {
    box-shadow: 0 0 30px 8px rgba(34, 197, 94, 0.45);
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
      height: 400px;
    }

    .activitySection {
      grid-column: span 12;
      height: 400px;
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
      height: 400px;
    }

    .activitySection {
      grid-column: span 12;
      height: 400px;
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
      height: 450px;
    }

    .activitySection {
      height: 450px;
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
      height: 550px;
    }

    .activitySection {
      height: 550px;
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
const ActivityChart = React.memo(({ data, mode, period }) => {
  const [hoveredPoint, setHoveredPoint] = useState(null);
  if (!data || data.length === 0) return null;

  const width = 1000;
  const height = 300;
  const padding = { top: 10, right: 30, bottom: 40, left: 60 };
  const chartWidth = width - padding.left - padding.right;
  const chartHeight = height - padding.top - padding.bottom;

  let yMax = Math.max(...data) * 1.2;
  let yMin = 0;
  let unit = '';
  const steps = 4;

  if (mode === 'water') {
    unit = ' L';
    yMax = 4;
  } else if (mode === 'sleep') {
    unit = ' h';
    yMax = 12;
  } else if (mode === 'meal') {
    unit = '';
    yMax = 3000;
  } else if (mode === 'workout') {
    unit = ' min';
    yMax = 120;
  }

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
    yLabels.push({
      y: padding.top + chartHeight - (i * (chartHeight / steps)),
      val: labelVal
    });
  }

  const xLabels = period === 'week' ? ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'] : [];

  return (
    <div style={{ flex: 1, position: 'relative', width: '100%', cursor: 'crosshair', overflow: 'hidden' }}>
      <svg
        key={mode}
        viewBox={`0 0 ${width} ${height}`}
        style={{ width: '100%', height: '100%', overflow: 'visible', animation: 'fadeIn 0.6s ease' }}
      >
        <defs>
          <linearGradient id="chartGradient" x1="0" y1="0" x2="0" y2="1">
            <stop offset="0%" stopColor="#818cf8" stopOpacity="0.5" />
            <stop offset="100%" stopColor="#818cf8" stopOpacity="0" />
          </linearGradient>
        </defs>

        {yLabels.map((label, i) => (
          <g key={i}>
            <line
              x1={padding.left}
              y1={label.y}
              x2={width - padding.right}
              y2={label.y}
              stroke="rgba(255,255,255,0.05)"
              strokeWidth="1"
            />
            <text
              x={padding.left - 15}
              y={label.y + 4}
              textAnchor="end"
              fill="#a1a1aa"
              fontSize="12"
              fontFamily="'Inter', sans-serif"
              fontWeight="500"
            >
              {label.val}{unit}
            </text>
          </g>
        ))}

        {period === 'week' &&
          xLabels.map((day, i) => {
            const xPos = padding.left + i * stepX;
            return (
              <text
                key={i}
                x={xPos}
                y={height - 10}
                textAnchor="middle"
                fill="#a1a1aa"
                fontSize="12"
                fontFamily="'Inter', sans-serif"
                fontWeight="500"
              >
                {day}
              </text>
            );
          })}

        <path d={areaPath} fill="url(#chartGradient)" />
        <path
          d={d}
          fill="none"
          stroke="#818cf8"
          strokeWidth="3"
          strokeLinecap="round"
          strokeLinejoin="round"
        />

        {data.map((val, i) => {
          const [cx, cy] = getPoint(i);
          return (
            <g
              key={i}
              onMouseEnter={() => setHoveredPoint(i)}
              onMouseLeave={() => setHoveredPoint(null)}
            >
              <rect
                x={cx - stepX / 2}
                y={padding.top}
                width={stepX}
                height={chartHeight}
                fill="transparent"
              />
              <circle
                cx={cx}
                cy={cy}
                r={hoveredPoint === i ? 6 : 0}
                fill="#09090b"
                stroke="#fff"
                strokeWidth="2"
                style={{
                  transition: 'all 0.15s ease-out',
                  filter: 'drop-shadow(0 0 6px rgba(255,255,255,0.8))'
                }}
              />
            </g>
          );
        })}
      </svg>

      <div
        style={{
          position: 'absolute',
          left: 0,
          top: 0,
          width: '100%',
          height: '100%',
          pointerEvents: 'none',
          opacity: hoveredPoint !== null ? 1 : 0,
          transition: 'opacity 0.2s ease'
        }}
      >
        {hoveredPoint !== null && (() => {
          const [cx, cy] = getPoint(hoveredPoint);
          const val =
            (mode === 'water' || mode === 'sleep')
              ? data[hoveredPoint].toFixed(1)
              : Math.round(data[hoveredPoint]);
          return (
            <div
              style={{
                position: 'absolute',
                left: `${(cx / width) * 100}%`,
                top: `${(cy / height) * 100}%`,
                transform: 'translate(-50%, -130%)',
                transition: 'left 0.1s linear, top 0.1s linear',
                background: 'rgba(24, 24, 27, 0.95)',
                border: '1px solid rgba(255,255,255,0.15)',
                borderRadius: '8px',
                padding: '8px 16px',
                boxShadow: '0 4px 20px rgba(0,0,0,0.5)',
                textAlign: 'center',
                minWidth: '70px',
                backdropFilter: 'blur(8px)'
              }}
            >
              <div
                style={{
                  fontSize: '10px',
                  color: '#a1a1aa',
                  textTransform: 'uppercase',
                  letterSpacing: '1px',
                  marginBottom: '2px'
                }}
              >
                {mode}
              </div>
              <div
                style={{
                  fontSize: '16px',
                  fontWeight: '700',
                  color: '#fff',
                  fontFamily: 'sans-serif'
                }}
              >
                {val}
                <span style={{ fontSize: '12px', color: '#818cf8', marginLeft: '2px' }}>
                  {unit}
                </span>
              </div>
              <div
                style={{
                  position: 'absolute',
                  bottom: '-5px',
                  left: '50%',
                  transform: 'translateX(-50%) rotate(45deg)',
                  width: '10px',
                  height: '10px',
                  background: 'rgba(24,24,27,0.95)',
                  borderRight: '1px solid rgba(255,255,255,0.15)',
                  borderBottom: '1px solid rgba(255,255,255,0.15)'
                }}
              />
            </div>
          );
        })()}
      </div>
    </div>
  );
}, (prevProps, nextProps) => {
  return (
    prevProps.data === nextProps.data &&
    prevProps.mode === nextProps.mode &&
    prevProps.period === nextProps.period
  );
});

// --- DEFAULT HISTORY ---
const DEFAULT_HISTORY = [];

function Dashboard() {
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

  const resetDailyMacros = () =>
    setMacros((prev) => ({
      ...prev,
      p: 0,
      c: 0,
      f: 0,
      calories: 0,
      fiber: 0
    }));

  const updateMacrosFromMeal = (mealData) => {
    try {
      const protein = mealData.protein || 0;
      const carbs = mealData.carbs || 0;
      const fats = mealData.fats || 0;
      const calories = mealData.calories || 0;
      const fiber = mealData.fiber || 0;

      setMacros((prev) => ({
        ...prev,
        p: prev.p + protein,
        c: prev.c + carbs,
        f: prev.f + fats,
        calories: prev.calories + calories,
        fiber: prev.fiber + fiber
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

  const [water, setWater] = useState(0);
  const [sleep, setSleep] = useState(0);
  const [status, setStatus] = useState('workout');
  const [workoutIntensity, setWorkoutIntensity] = useState(0);
  const [recoveryScore, setRecoveryScore] = useState(0);
  const [notifications, setNotifications] = useState([]);
  const [lastNotificationCheck, setLastNotificationCheck] = useState(null);
  const [showWaterCelebration, setShowWaterCelebration] = useState(false);
  const [showSleepCelebration, setShowSleepCelebration] = useState(false);
  const [chartMode, setChartMode] = useState('workout');
  const [chartPeriod, setChartPeriod] = useState('week');
  const [chartData, setChartData] = useState([0, 0, 0, 0, 0, 0, 0]);
  const [recentHistory, setRecentHistory] = useState([]);
  const [weeklyProgress, setWeeklyProgress] = useState([]);
  const [loading, setLoading] = useState(true);

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

  // --- EFFECTS & LIFECYCLE ---

  // Fetch user and init dashboard
  useEffect(() => {
    const fetchUserData = async () => {
      try {
        await checkDailyReset();
        checkInterruptedSessions();

        const { data } = await getProfile();
        if (!data.goal || !data.weight) {
          navigate('/profile-setup', { replace: true });
          return;
        }

        if (data.name) setDisplayName(data.name.split(' ')[0]);

        if (data.goal === 'Muscle Gain') {
          setMacros({
            p: 0,
            c: 0,
            f: 0,
            calories: 0,
            fiber: 0,
            pMax: 180,
            cMax: 300,
            fMax: 80,
            calMax: 2800
          });
        } else if (data.goal === 'Weight Loss') {
          setMacros({
            p: 0,
            c: 0,
            f: 0,
            calories: 0,
            fiber: 0,
            pMax: 160,
            cMax: 150,
            fMax: 60,
            calMax: 1800
          });
        }

        // ✅ UPDATED: Use storage utility
        const storedHistory = getFromStorage(StorageKeys.ACTIVITY_HISTORY, []);
        if (storedHistory && Array.isArray(storedHistory)) {
          setRecentHistory(storedHistory);
        }

        // ✅ UPDATED: Use storage utility
        const storedAvatar = getFromStorage(StorageKeys.USER_AVATAR);
        if (storedAvatar) setUserAvatar(storedAvatar);

        // ✅ UPDATED: Use storage utility
        const storedStreak = getFromStorage(StorageKeys.CURRENT_STREAK, 0);
        if (storedStreak) {
          setStats((prev) => ({ ...prev, streak: parseInt(storedStreak, 10) }));
        }
      } catch (error) {
        console.error('Error fetching profile:', error);
        navigate('/login', { replace: true });
      } finally {
        setLoading(false);
      }
    };

    const initializeDashboard = async () => {
      await fetchUserData();
      await checkDayReset();
      generateWeeklyData();
    };

    initializeDashboard();
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
        setWater(0);
        setSleep(0);
        resetDailyMacros();
        setStatus('workout');
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

  useEffect(() => {
    const handlePageVisibilityChange = () => {
      if (!document.hidden) checkDailyReset();
    };
    document.addEventListener('visibilitychange', handlePageVisibilityChange);
    return () => document.removeEventListener('visibilitychange', handlePageVisibilityChange);
  }, []);

  const addNotification = (message, type = 'info') => {
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
  };

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
      type
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

  const checkWaterThresholdNotifications = (oldWater, newWater) => {
    try {
      if (
        oldWater < 2.0 &&
        newWater >= 2.0 &&
        newWater < 3.0 &&
        !hasNotificationBeenShownToday('water-status')
      ) {
        addNotification(
          `You're improving your hydration! Current: ${newWater.toFixed(1)}L/3.0L.`,
          'info'
        );
        markNotificationAsShownToday('water-status');
      }
      if (
        oldWater < 3.0 &&
        newWater >= 3.0 &&
        !hasNotificationBeenShownToday('water-goal')
      ) {
        addNotification(
          `Great! You've reached your daily water goal of ${newWater.toFixed(1)}L.`,
          'success'
        );
        markNotificationAsShownToday('water-goal');
        setShowWaterCelebration(true);
        setTimeout(() => setShowWaterCelebration(false), 3000);
      }
    } catch (error) {
      console.error('Error in checkWaterThresholdNotifications:', error);
    }
  };

  const checkSleepThresholdNotifications = (oldSleep, newSleep) => {
    try {
      if (
        oldSleep < 7.0 &&
        newSleep >= 7.0 &&
        newSleep <= 9.0 &&
        !hasNotificationBeenShownToday('sleep-minimum')
      ) {
        addNotification(
          `Good job! You've reached the minimum recommended sleep of ${newSleep.toFixed(1)}h.`,
          'info'
        );
        markNotificationAsShownToday('sleep-minimum');
      }
      if (
        oldSleep <= 9.0 &&
        newSleep > 9.0 &&
        !hasNotificationBeenShownToday('sleep-maximum')
      ) {
        addNotification(
          `You've exceeded the recommended maximum sleep of 9.0h. Current: ${newSleep.toFixed(1)}h.`,
          'info'
        );
        markNotificationAsShownToday('sleep-maximum');
      }
    } catch (error) {
      console.error('Error in checkSleepThresholdNotifications:', error);
    }
  };

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

      if (currentHour < 10 && !hasDailyReminderBeenShown('water')) {
        if (water < 0.5) {
          const newNotification = {
            id: `water-reminder-${todayStr}`,
            type: 'info',
            message: `Start your day hydrated! Current water intake: ${water.toFixed(1)}L. Aim for 3L today.`,
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
        } catch (parseError) {
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
  }, [chartMode, chartPeriod]);

  const updateRecoveryScore = (currentWater, currentSleep) => {
    const waterScore = Math.min(100, (currentWater / 3.0) * 100);
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

  const adjustWorkoutIntensity = (recoveryLevel) => {
    if (recoveryLevel > 80) return 100;
    if (recoveryLevel > 60) return 75;
    if (recoveryLevel > 40) return 50;
    if (recoveryLevel > 20) return 25;
    return 10;
  };

  // ✅ UPDATED: useCallback for water handlers
  const handleWaterAdd = useCallback(() => {
    const newWaterValue = water + 0.2;
    checkWaterThresholdNotifications(water, newWaterValue);
    setWater(newWaterValue);
    logActivity('water', 'Hydration', '+200ml Water');
    updateRecoveryScore(newWaterValue, sleep);
  }, [water, sleep]);

  const handleWaterRemove = useCallback(() => {
    if (water > 0) {
      const newWaterValue = Math.max(0, water - 0.2);
      checkWaterThresholdNotifications(water, newWaterValue);
      setWater(newWaterValue);
      removeLastLog('water');
      updateRecoveryScore(newWaterValue, sleep);
    }
  }, [water, sleep]);

  // ✅ UPDATED: useCallback for sleep handlers
  const handleSleepAdd = useCallback(() => {
    const newSleepValue = sleep + 0.5;
    checkSleepThresholdNotifications(sleep, newSleepValue);
    setSleep(newSleepValue);
    logActivity('sleep', 'Sleep Update', 'Added 30 mins');
    updateRecoveryScore(water, newSleepValue);
  }, [sleep, water]);

  const handleSleepRemove = useCallback(() => {
    if (sleep > 0) {
      const newSleepValue = Math.max(0, sleep - 0.5);
      checkSleepThresholdNotifications(sleep, newSleepValue);
      setSleep(newSleepValue);
      removeLastLog('sleep');
      updateRecoveryScore(water, newSleepValue);
    }
  }, [sleep, water]);

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
  }, []);

  const updateChart = (mode, period) => {
    if (mode === 'water') setChartData([water, water, water, water, water, water, water]);
    else if (mode === 'sleep')
      setChartData([sleep, sleep, sleep, sleep, sleep, sleep, sleep]);
    else if (mode === 'recovery')
      setChartData([
        recoveryScore,
        recoveryScore,
        recoveryScore,
        recoveryScore,
        recoveryScore,
        recoveryScore,
        recoveryScore
      ]);
    else if (mode === 'intensity')
      setChartData([
        workoutIntensity,
        workoutIntensity,
        workoutIntensity,
        workoutIntensity,
        workoutIntensity,
        workoutIntensity,
        workoutIntensity
      ]);
    else setChartData([0, 0, 0, 0, 0, 0, 0]);
  };

  const generateWeeklyData = () => {
    const currentDayIndex = new Date().getDay();
    const jsToOurIndex = [6, 0, 1, 2, 3, 4, 5];
    const ourCurrentDayIndex = jsToOurIndex[currentDayIndex];
    const days = ['M', 'T', 'W', 'T', 'F', 'S', 'S'];
    const weeklyData = days.map((day, index) => ({ day, status: 'pending' }));
    updateWeeklyProgressFromLocal(weeklyData, ourCurrentDayIndex);
  };

  // ✅ UPDATED: Weekly progress uses storage utilities
  const updateWeeklyProgressFromLocal = (initialData, currentDayIndex) => {
    try {
      const startOfWeek = new Date();
      const day = startOfWeek.getDay();
      const diff = startOfWeek.getDate() - day + (day === 0 ? -6 : 1);
      startOfWeek.setDate(diff);
      startOfWeek.setHours(0, 0, 0, 0);

      const updatedData = initialData.map((dayObj, index) => {
        const dayDate = new Date(startOfWeek);
        dayDate.setDate(startOfWeek.getDate() + index);
        const dateStr = dayDate.toISOString().split('T')[0];
        // ✅ UPDATED: Use storage utility with helper
        const stored = getFromStorage(StorageKeys.getWorkoutDoneKey(dateStr));
        if (stored === 'true' || stored === 'false')
          return {
            ...dayObj,
            status: stored === 'true' ? 'done' : 'missed'
          };
        if (index < currentDayIndex)
          return {
            ...dayObj,
            status: 'missed'
          };
        return dayObj;
      });

      setWeeklyProgress(updatedData);
    } catch (error) {
      console.error('Error updating weekly progress:', error);
      setWeeklyProgress(initialData);
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
  const updateTrends = async () => {
    try {
      const { data: profileData } = await getProfile();
      const userId = profileData._id || profileData.id;
      const todayStr = getTodayStr();
      const currentWeek = Math.ceil(new Date().getDate() / 7);
      const currentMonth = new Date().getMonth() + 1;

      // ✅ UPDATED: Use storage utilities
      const workoutDone = getFromStorage(StorageKeys.TODAY_WORKOUT_DONE) === 'true';
      const mealDone = getFromStorage(StorageKeys.TODAY_MEALS_DONE) === 'true';

      const trendData = {
        user_id: userId,
        date: todayStr,
        week: currentWeek,
        month: currentMonth,
        workout_completed: workoutDone,
        meal_completed: mealDone,
        macros,
        water_intake: water,
        sleep_duration: sleep,
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
        newChartData[adjustedIndex] = trendData.meal_completed ? 1 : 0;
      else if (chartMode === 'water') newChartData[adjustedIndex] = trendData.water_intake;
      else if (chartMode === 'sleep') newChartData[adjustedIndex] = trendData.sleep_duration;

      setChartData(newChartData);
    } catch (error) {
      console.error('Error updating local trend data:', error);
    }
  };

  // ✅ UPDATED: Day reset uses storage utilities
  const checkDayReset = async () => {
    try {
      const todayStr = getTodayStr();
      // ✅ UPDATED: Use storage utilities
      const workoutDoneFlag = getFromStorage(StorageKeys.TODAY_WORKOUT_DONE) === 'true';
      const mealDoneFlag = getFromStorage(StorageKeys.TODAY_MEALS_DONE) === 'true';

      if (!workoutDoneFlag && !mealDoneFlag) setStatus('workout');
      else if (workoutDoneFlag && !mealDoneFlag) setStatus('meal');
      else setStatus('done');

      // ✅ UPDATED: Use storage utility
      const storedStreak = getFromStorage(StorageKeys.CURRENT_STREAK, 0);
      if (storedStreak)
        setStats((prev) => ({ ...prev, streak: parseInt(storedStreak, 10) }));

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

  const handleAction = async () => {
    try {
      if (status === 'workout') {
        startWorkoutSession({ startedAt: new Date().toISOString(), expectedCompletion: true });
        const enrichedData = await getCachedEnrichedData();
        navigate('/workout', { state: { recoveryScore, workoutIntensity, enrichedData } });
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

  // ✅ UPDATED: Logout uses storage utility with immediate navigation
  const handleLogout = () => {
    showConfirmDialog('Log out?', (confirmed) => {
      if (confirmed) {
        // Disable all interactions immediately
        document.body.style.pointerEvents = 'none';
        
        // Clear storage
        clearAllStorage();
        
        // Navigate immediately without waiting
        navigate('/login', { replace: true });
        
        // Re-enable after navigation completes
        setTimeout(() => {
          document.body.style.pointerEvents = 'auto';
        }, 500);
      }
    });
  };

  const handleMealComplete = async (mealData) => {
    try {
      const todayStr = getTodayStr();
      // ✅ UPDATED: Use storage utility
      const todayMealsDone = getFromStorage(StorageKeys.TODAY_MEALS_DONE) === 'true';
      if (todayMealsDone) {
        console.log('Meal already marked as completed today');
        return;
      }
      updateMacrosFromMeal(mealData);
      setStatus('done');
      // ✅ UPDATED: Use storage utility
      setToStorage(StorageKeys.TODAY_MEALS_DONE, 'true');
      await updateTrends();
    } catch (error) {
      console.error('Error in handleMealComplete:', error);
      showError(
        'There was an issue recording your meal completion. Please try again.',
        3000
      );
    }
  };

  // ✅ UPDATED: Workout completion uses storage utilities
  const handleWorkoutComplete = async () => {
    try {
      if (status !== 'workout') {
        console.log('Workout status has changed, skipping manual completion');
        return;
      }
      const todayStr = getTodayStr();
      const todayWorkoutDone = getFromStorage(StorageKeys.TODAY_WORKOUT_DONE) === 'true';
      if (todayWorkoutDone) {
        console.log('Workout already marked as completed today');
        return;
      }

      const yesterdayStr = new Date(Date.now() - 86400000).toISOString().split('T')[0];
      const yesterdayWorkoutDone =
        getFromStorage(StorageKeys.getWorkoutDoneKey(yesterdayStr)) === 'true';

      const newStreakVal = yesterdayWorkoutDone ? stats.streak + 1 : 1;

      setStatus('meal');
      setToStorage(StorageKeys.TODAY_WORKOUT_DONE, 'true');
      setToStorage(StorageKeys.getWorkoutDoneKey(todayStr), 'true');
      setToStorage(StorageKeys.LAST_WORKOUT_DATE, todayStr);

      setStats((prev) => ({ ...prev, streak: newStreakVal }));
      setToStorage(StorageKeys.CURRENT_STREAK, newStreakVal.toString());

      try {
        await updateStreakAPI({ workout_completed: true });
      } catch (error) {
        console.error('Error updating streak:', error);
      }
      await updateTrends();
    } catch (error) {
      console.error('Error in handleWorkoutComplete:', error);
      showError(
        'There was an issue recording your workout completion. Please try again.',
        3000
      );
    }
  };

  // ✅ UPDATED: Workout skip uses storage utilities
  const handleWorkoutSkip = async () => {
    try {
      if (status !== 'workout') {
        console.log('Workout status has changed, skipping manual skip');
        return;
      }
      const todayStr = getTodayStr();
      const todayWorkoutDone = getFromStorage(StorageKeys.TODAY_WORKOUT_DONE) === 'true';
      if (todayWorkoutDone) {
        console.log('Workout already marked as completed/skipped today');
        return;
      }

      setStatus('meal');
      setToStorage(StorageKeys.TODAY_WORKOUT_DONE, 'true');
      setToStorage(StorageKeys.getWorkoutDoneKey(todayStr), 'false');

      try {
        await updateStreakAPI({ workout_completed: false });
      } catch (error) {
        console.error('Error updating streak:', error);
      }
      await updateTrends();
    } catch (error) {
      console.error('Error in handleAutoWorkoutComplete:', error);
      showError(
        'There was an issue recording your workout completion. Please try again.',
        3000
      );
    }
  };

  if (loading) {
    return (
      <div style={{ ...styles.page, display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
        <div style={{ color: '#6366f1', fontSize: '18px', fontWeight: '600' }}>
          Loading Dashboard...
        </div>
      </div>
    );
  }

  return (
    <>
      <div style={styles.page} className="page">
        <style>{responsiveStyles}</style>

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
        <nav style={styles.navbar}>
          <div style={styles.brand}>
            <div style={styles.brandDot}></div> ELEVATE
          </div>
          <div style={styles.navCenter}>
            <div style={{ ...styles.navLink, ...styles.navLinkActive }}>Dashboard</div>
            <div
              style={styles.navLink}
              onClick={() => navigate('/workout')}
            >
              Workout
            </div>
            <div
              style={styles.navLink}
              onClick={() => navigate('/nutrition')}
            >
              Nutrition
            </div>
            <div
              style={styles.navLink}
              onClick={() => navigate('/chatbot')}
            >
              ChatBot
            </div>
          </div>
          <div style={styles.navRight}>
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
                  <div
                    style={{
                      ...styles.notifItem,
                      borderBottom: 'none',
                      color: '#a1a1aa',
                      fontSize: '12px',
                      justifyContent: 'center',
                      marginTop: '8px'
                    }}
                  >
                    {notifications.length === 0 ? 'No new alerts' : `${notifications.length} alert(s)`}
                  </div>
                </div>
              )}
            </div>
            <button style={styles.logoutBtn} className="logout-btn" onClick={handleLogout}>
              <span style={styles.logoutText}>LOGOUT</span>
            </button>
          </div>
        </nav>

        {/* MAIN CONTAINER */}
        <div style={styles.container} className="container">

          {/* WATER CELEBRATION */}
          {showWaterCelebration && (
            <div
              style={{
                position: 'fixed',
                top: '50%',
                left: '50%',
                transform: 'translate(-50%, -50%)',
                zIndex: 9999,
                pointerEvents: 'none',
                fontSize: '48px',
                fontWeight: 'bold',
                color: '#10b981',
                textShadow: '0 0 10px rgba(16, 185, 129, 0.8)',
                animation: 'celebrate 2s ease-out forwards',
                userSelect: 'none'
              }}
            >
              💧 Hydration goal reached!
            </div>
          )}

          {/* SLEEP CELEBRATION */}
          {showSleepCelebration && (
            <div
              style={{
                position: 'fixed',
                top: '50%',
                left: '50%',
                transform: 'translate(-50%, -50%)',
                zIndex: 9999,
                pointerEvents: 'none',
                fontSize: '48px',
                fontWeight: 'bold',
                color: '#3b82f6',
                textShadow: '0 0 10px rgba(59, 130, 246, 0.8)',
                animation: 'celebrate 2s ease-out forwards',
                userSelect: 'none'
              }}
            >
              😴 Excellent Rest! 😴
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
              {status === 'workout' && (
                <button
                  style={{
                    ...styles.circleBtn,
                    ...styles.btnBlue,
                    width: '160px',
                    height: '160px'
                  }}
                  className="btn-blue-pulse circleBtn"
                  onClick={handleAction}
                >
                  <span style={{ fontSize: '24px' }}>💪</span>
                  <span style={{ fontSize: '12px', fontWeight: '800' }}>START</span>
                </button>
              )}
              {status === 'meal' && (
                <button
                  style={{
                    ...styles.circleBtn,
                    ...styles.btnPink,
                    width: '160px',
                    height: '160px'
                  }}
                  className="btn-pink-pulse circleBtn"
                  onClick={handleAction}
                >
                  <span style={{ fontSize: '24px' }}>🥗</span>
                  <span style={{ fontSize: '12px', fontWeight: '800' }}>LOG MEAL</span>
                </button>
              )}
              {status === 'done' && (
                <button
                  style={{
                    ...styles.circleBtn,
                    ...styles.btnGreen,
                    width: '160px',
                    height: '160px'
                  }}
                  className="btn-green-pulse circleBtn"
                  disabled
                >
                  <span style={{ fontSize: '24px' }}>✅</span>
                  <span style={{ fontSize: '12px', fontWeight: '800' }}>ALL SET</span>
                </button>
              )}
            </div>

            <div style={styles.heroRight} className="heroRight">
              <div style={{ textAlign: 'right' }}>
                <div style={styles.streakLabel}>CURRENT STREAK</div>
                <div style={{ display: 'flex', gap: 15 }}>
                  <div style={styles.streakNumber} className="streakNumber">
                    {stats.streak}
                  </div>
                  <div style={{ fontSize: '80px', animation: 'float 3s infinite' }}>🔥</div>
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
          <div style={styles.statsRow}>
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
                  {macros.calories} / {macros.calMax} cal
                </div>
              </div>
              <div
                className="macro-item"
                style={{ marginBottom: '12px', cursor: 'pointer' }}
                title={`Total: ${macros.calories} cal`}
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
                  title={`${macros.p}g Protein`}
                >
                  <div style={{ fontSize: '10px', color: '#a1a1aa', marginBottom: '4px' }}>
                    Prot ({macros.p}g)
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
                  title={`${macros.c}g Carbs`}
                >
                  <div style={{ fontSize: '10px', color: '#a1a1aa', marginBottom: '4px' }}>
                    Carb ({macros.c}g)
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
                  title={`${macros.f}g Fats`}
                >
                  <div style={{ fontSize: '10px', color: '#a1a1aa', marginBottom: '4px' }}>
                    Fat ({macros.f}g)
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
              {/* Fiber */}
              <div
                className="macro-item"
                style={{ marginTop: '12px', cursor: 'pointer' }}
                title={`${macros.fiber}g Fiber`}
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
                  <span>Fiber Estimate</span>
                  <span>
                    {macros.fiber}g / 35g
                  </span>
                </div>
                <div style={{ ...styles.macroBarBG, overflow: 'hidden' }}>
                  <div
                    style={{
                      ...styles.macroBarFill,
                      width: `${Math.min(100, (macros.fiber / 35) * 100)}%`,
                      background: '#a855f7'
                    }}
                  ></div>
                </div>
              </div>
            </div>

            {/* HYDRATION BOX */}
            <div
              style={{
                ...styles.bentoBox,
                background: 'linear-gradient(135deg, #1e3a8a 0%, #172554 100%)',
                border: '1px solid rgba(96, 165, 250, 0.2)'
              }}
              className="hover-card bentoBox"
            >
              <div style={{ fontSize: '14px', fontWeight: '700', color: '#fff', marginBottom: '10px' }}>
                HYDRATION
              </div>
              <div
                style={{
                  flex: 1,
                  display: 'flex',
                  flexDirection: 'column',
                  justifyContent: 'center',
                  alignItems: 'center'
                }}
              >
                <div style={{ fontSize: '48px', fontWeight: '800', color: '#fff' }}>
                  {water.toFixed(1)} <span style={{ fontSize: '16px', fontWeight: '500', color: '#93c5fd' }}>L</span>
                </div>
                <div style={{ fontSize: '12px', color: '#bfdbfe' }}>Goal: 3.0 L</div>
              </div>
              <div
                style={{
                  display: 'flex',
                  justifyContent: 'center',
                  flexDirection: 'column',
                  alignItems: 'center'
                }}
              >
                <div style={styles.glassPill} className="glassPill">
                  <button
                    style={styles.glassBtn}
                    className="control-btn-hover glassBtn"
                    onClick={handleWaterRemove}
                  >
                    -
                  </button>
                  <span style={styles.glassText}>ADJUST</span>
                  <button
                    style={styles.glassBtn}
                    className="control-btn-hover glassBtn"
                    onClick={handleWaterAdd}
                  >
                    +
                  </button>
                </div>
                <div
                  style={{
                    marginTop: '10px',
                    fontSize: '12px',
                    color:
                      recoveryScore > 60 ? '#22c55e' : recoveryScore > 40 ? '#f59e0b' : '#ef4444'
                  }}
                >
                  Recovery: {recoveryScore}%
                </div>
              </div>
            </div>

            {/* READINESS BOX */}
            <div style={{ ...styles.bentoBox }} className="hover-card bentoBox">
              <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                <div style={{ fontSize: '14px', fontWeight: '700', color: '#fff', marginBottom: '10px' }}>
                  READINESS
                </div>
                <div
                  style={{
                    fontSize: '14px',
                    fontWeight: '800',
                    color: stats.focusScore > 80 ? '#22c55e' : '#f59e0b'
                  }}
                >
                  {stats.focusScore} %
                </div>
              </div>
              <div
                style={{
                  flex: 1,
                  display: 'flex',
                  flexDirection: 'column',
                  justifyContent: 'center',
                  alignItems: 'center'
                }}
              >
                <div style={{ fontSize: '48px', fontWeight: '800', color: '#fff', fontFamily: 'monospace' }}>
                  {Math.floor(sleep)}
                  <span style={{ color: '#6366f1' }}>: </span>
                  {((sleep % 1) * 60)
                    .toString()
                    .padStart(2, '0')}
                </div>
                <div style={{ fontSize: '12px', color: '#a1a1aa' }}>Hours Slept</div>
              </div>
              <div
                style={{
                  display: 'flex',
                  justifyContent: 'center',
                  flexDirection: 'column',
                  alignItems: 'center'
                }}
              >
                <div style={styles.glassPill} className="glassPill">
                  <button
                    style={styles.glassBtn}
                    className="control-btn-hover glassBtn"
                    onClick={handleSleepRemove}
                  >
                    -
                  </button>
                  <span style={styles.glassText}>SET TIME</span>
                  <button
                    style={styles.glassBtn}
                    className="control-btn-hover glassBtn"
                    onClick={handleSleepAdd}
                  >
                    +
                  </button>
                </div>
                <div
                  style={{
                    marginTop: '10px',
                    fontSize: '12px',
                    color:
                      recoveryScore > 60 ? '#22c55e' : recoveryScore > 40 ? '#f59e0b' : '#ef4444'
                  }}
                >
                  Intensity: {workoutIntensity}%
                </div>
              </div>
            </div>
          </div>

          {/* CHART SECTION */}
          <div style={{ ...styles.bentoBox, ...styles.chartSection }} className="bentoBox chartSection">
            <div style={styles.sectionHeader} className="sectionHeader">
              <div style={styles.sectionTitle} className="sectionTitle">
                <div style={styles.sectionAccent}></div> TRENDS
              </div>
              <div style={styles.chartControls}>
                <div style={styles.chartTabs}>
                  {['workout', 'meal', 'sleep', 'water', 'recovery', 'intensity'].map((m) => (
                    <button
                      key={m}
                      style={{
                        ...styles.chartTab,
                        ...(chartMode === m ? styles.chartTabActive : {})
                      }}
                      onClick={() => setChartMode(m)}
                    >
                      {m.toUpperCase()}
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
            <ActivityChart data={chartData} mode={chartMode} period={chartPeriod} />
          </div>

          {/* ACTIVITY SECTION */}
          <div style={{ ...styles.bentoBox, ...styles.activitySection }} className="bentoBox activitySection">
            <div style={styles.sectionHeader}>
              <div style={styles.sectionTitle}>
                <div style={styles.sectionAccent}></div> ACTIVITY
              </div>
            </div>
            <div className="activity-list" style={{ flex: 1, overflowY: 'auto', paddingRight: '4px' }}>
              {recentHistory.map((h, i) => (
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
              ))}
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
