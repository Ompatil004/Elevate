import React, { useState, useEffect, useRef, useCallback, useMemo } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import Navbar from '../components/Navbar';
import { useNotification } from '../components/NotificationProvider';
import { useTheme } from '../context/ThemeContext';
import {
  getProfile,
  generateWorkout,
  getWeeklyWorkoutPlan,
  saveUserWorkoutToNode,
  getWorkoutHistory,
  saveWorkoutHistory,
  saveTrends,
  swapRestToWorkout,
  swapWorkoutToRest,
  postSessionResult,
} from '../api';
import { setToStorage, getFromStorage, logoutSafe, StorageKeys, getLocalDateStr } from '../utils/storage';
import ConfirmDialog from '../components/ConfirmDialog';
import PoseDetector from '../components/PoseDetector';
import TimerExerciseMode from '../components/TimerExerciseMode';
import { syncBridge, SyncTypes } from '../utils/syncBridge';
import { preloadPoseAssets } from '../utils/poseModelPreload';
import AuroraBackground from '../components/AuroraBackground';

// Define full weekday names array
const weekdayNames = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'];
const WORKOUT_PLAN_CACHE_VERSION = '2026-04-10-workout-fix-6-seeded-shuffle-variety';
const DEFAULT_FALLBACK_GIF = 'https://media.giphy.com/media/3o7TKsQ8UQJ5n6WfTO/giphy.gif';

// --- STYLES (Your Exact Styles Preserved) ---
const styles = {
  page: { background: 'transparent', minHeight: '100dvh', color: 'var(--app-text)', fontFamily: "'Inter', sans-serif", overflowX: 'hidden', position: 'relative', zIndex: 1, paddingTop: 'clamp(64px, 9vw, 80px)' },
  navbar: {
    display: 'flex', alignItems: 'center',
    padding: '0 clamp(12px, 4vw, 40px)', height: 'clamp(64px, 9vw, 80px)',
    gap: 'clamp(8px, 2vw, 18px)',
    borderBottom: '1px solid var(--app-border)',
    background: 'var(--app-nav-bg, rgba(9, 9, 11, 0.6))', backdropFilter: 'blur(16px)',
    position: 'fixed', top: 0, left: 0, right: 0, zIndex: 1000,
    overflowX: 'auto'
  },
  brand: {
    flex: 1,
    fontSize: '22px', fontWeight: '900', letterSpacing: '-1px',
    background: 'var(--brand-grad, linear-gradient(to right, #ffffff, #a5b4fc))',
    WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent',
    display: 'flex', alignItems: 'center', gap: '10px'
  },
  navCenter: {
    display: 'flex', gap: 'clamp(4px, 1.5vw, 8px)', height: '100%', alignItems: 'center',
    justifyContent: 'center'
  },
  navLink: {
    display: 'flex', alignItems: 'center', padding: '8px clamp(10px, 2vw, 20px)',
    fontSize: 'clamp(11px, 1.7vw, 13px)', fontWeight: '600', color: 'var(--app-text-muted)',
    cursor: 'pointer', borderRadius: '20px', transition: 'all 0.2s',
    textTransform: 'uppercase', letterSpacing: '0.5px',
    border: '1px solid transparent'
  },
  navLinkActive: {
    background: 'var(--app-border)', color: 'var(--app-text)',
    boxShadow: '0 0 20px var(--app-border)',
    border: '1px solid var(--app-border)'
  },
  navRight: {
    flex: 1,
    display: 'flex', alignItems: 'center', gap: 'clamp(8px, 2vw, 24px)',
    justifyContent: 'flex-end'
  },
  brandDot: { width: '8px', height: '8px', background: '#6366f1', borderRadius: '50%', boxShadow: '0 0 15px #6366f1' },
  dateDisplay: { fontSize: 'clamp(11px, 1.6vw, 13px)', fontWeight: '600', color: 'var(--app-text-muted)', fontFamily: 'sans-serif', letterSpacing: '0.5px', marginRight: '8px' },
  iconButton: { width: 'clamp(36px, 6vw, 42px)', height: 'clamp(36px, 6vw, 42px)', borderRadius: '12px', background: 'var(--quote-bg)', border: '1px solid var(--app-border)', color: 'var(--app-text)', display: 'flex', alignItems: 'center', justifyContent: 'center', cursor: 'pointer', fontSize: '18px', transition: 'all 0.2s', position: 'relative' },
  notifDropdown: { position: 'absolute', top: '60px', right: '0px', width: 'min(92vw, 340px)', background: 'var(--app-surface)', border: '1px solid var(--app-border)', borderRadius: '16px', padding: '16px', zIndex: 2000, boxShadow: '0 20px 50px rgba(0,0,0,0.5)', animation: 'slideDown 0.2s ease-out' },
  notifItem: { padding: '12px 16px', borderBottom: '1px solid var(--app-border)', fontSize: '13px', color: 'var(--app-text)' },
  logoutBtn: { display: 'flex', alignItems: 'center', gap: '8px', padding: '0 clamp(10px, 2vw, 20px)', borderRadius: '12px', background: 'rgba(239, 68, 68, 0.1)', border: '1px solid rgba(239, 68, 68, 0.2)', color: '#ef4444', cursor: 'pointer', transition: 'all 0.2s ease', height: 'clamp(36px, 6vw, 42px)' },
  logoutText: { fontSize: '12px', fontWeight: '700', letterSpacing: '0.5px', textTransform: 'uppercase' },
  container: { maxWidth: '1600px', margin: '0 auto', padding: '40px' },
  h1: { fontSize: '42px', fontWeight: '800', marginBottom: '40px', background: 'var(--h1-grad)', WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent', letterSpacing: '-1px', filter: 'drop-shadow(0 2px 12px rgba(99,102,241,0.18))' },
  grid: { display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))', gap: '20px' },
  card: { background: 'var(--app-surface)', borderRadius: '20px', padding: '24px', border: '1px solid var(--app-border)', position: 'relative', transition: 'transform 0.22s ease, box-shadow 0.22s ease, border-color 0.22s ease', overflow: 'hidden', minHeight: '200px', display: 'flex', flexDirection: 'column' },
  cardDone: { opacity: 0.5, border: '1px solid #22c55e', background: 'rgba(34, 197, 94, 0.05)' },
  overlayDone: { position: 'absolute', top: 0, left: 0, width: '100%', height: '100%', display: 'flex', alignItems: 'center', justifyContent: 'center', background: 'var(--overlay-bg)', zIndex: 10, flexDirection: 'column', gap: '10px' },
  cardMissed: { opacity: 0.5, border: '1px solid #ef4444', background: 'rgba(239, 68, 68, 0.05)' },
  overlayMissed: { position: 'absolute', top: 0, left: 0, width: '100%', height: '100%', display: 'flex', alignItems: 'center', justifyContent: 'center', background: 'var(--overlay-bg)', zIndex: 10, flexDirection: 'column', gap: '10px' },
  cardLocked: { opacity: 0.6, cursor: 'not-allowed', border: '1px dashed var(--app-border)' },
  overlayLocked: { position: 'absolute', top: 0, left: 0, width: '100%', height: '100%', display: 'flex', alignItems: 'center', justifyContent: 'center', background: 'var(--overlay-bg)', zIndex: 10, flexDirection: 'column', gap: '10px' },
  cardActive: { border: '2px solid #6366f1', background: 'var(--day-card-selected-bg)', boxShadow: '0 0 30px rgba(99, 102, 241, 0.15)', cursor: 'pointer', transform: 'scale(1.02)' },
  dayTitle: { fontSize: '14px', fontWeight: '700', textTransform: 'uppercase', letterSpacing: '1px', marginBottom: '8px', color: 'var(--app-text-muted)' },
  focusText: { fontSize: '20px', fontWeight: '800', color: 'var(--app-text)', marginBottom: '16px', lineHeight: '1.3' },
  exPreview: { fontSize: '13px', color: 'var(--app-text-muted)', marginBottom: '4px', display: 'flex', justifyContent: 'space-between' },
  sessionContainer: { position: 'fixed', top: '80px', left: 0, width: '100%', height: 'calc(100vh - 80px)', background: 'var(--app-bg)', zIndex: 500, display: 'flex', padding: '20px', gap: '20px', animation: 'fadeIn 0.3s ease-out' },
  selectionList: { flex: '0 0 350px', background: 'var(--app-surface)', borderRadius: '24px', border: '1px solid var(--app-border)', display: 'flex', flexDirection: 'column', padding: '20px', overflowY: 'auto' },
  sidebarHeader: { fontSize: '18px', fontWeight: '800', color: 'var(--app-text)', marginBottom: '20px', display:'flex', justifyContent:'space-between', alignItems:'center' },
  backBtn: { fontSize: '12px', padding: '6px 12px', background: 'var(--app-border)', borderRadius: '8px', color: 'var(--app-text)', border:'none', cursor:'pointer' },
  selectionPreview: { flex: 1, background: 'var(--app-bg)', borderRadius: '24px', border: '1px solid var(--app-border)', display: 'flex', alignItems: 'center', justifyContent: 'center', flexDirection: 'column', color: '#52525b' },
  focusContainer: { width: '100%', height: '100%', display: 'flex', gap: '20px' },
  focusLeft: { flex: '4', display: 'flex', flexDirection: 'column', background: 'var(--app-surface)', borderRadius: '24px', padding: '24px', border: '1px solid var(--app-border)' },
  activeExTitle: { fontSize: '28px', fontWeight: '800', color: 'var(--app-text)', marginBottom: '8px', lineHeight: '1.2' },
  activeExStats: { fontSize: '16px', color: '#a5b4fc', fontWeight: '600', marginBottom: '20px', fontFamily: 'monospace' },
  gifLargeContainer: { flex: 1, background: 'var(--app-bg)', borderRadius: '16px', overflow: 'hidden', display: 'flex', alignItems: 'center', justifyContent: 'center', position: 'relative', border: '1px solid var(--app-border)', marginBottom: '20px' },
  gifLarge: { width: '100%', height: '100%', objectFit: 'contain' },
  controlsContainer: { height: '80px', display: 'flex', gap: '15px' },
  focusRight: { flex: '6', background: 'var(--app-bg)', borderRadius: '24px', border: '2px solid #6366f1', overflow: 'hidden', position: 'relative', display: 'flex', alignItems: 'center', justifyContent: 'center', boxShadow: '0 0 50px rgba(99, 102, 241, 0.1)' },
  videoFeed: { width: '100%', height: '100%', objectFit: 'contain', transform: 'scaleX(-1)' },
  recBadge: { position: 'absolute', top: 20, left: 20, background: 'rgba(220, 38, 38, 0.9)', padding: '6px 12px', borderRadius: '8px', color: 'white', fontWeight: '700', fontSize: '14px', display: 'flex', alignItems: 'center', gap: '8px', zIndex:10 },
  exerciseItem: { padding: '18px', borderRadius: '16px', marginBottom: '12px', background: 'var(--quote-bg)', border: '1px solid var(--app-border)', cursor: 'pointer', transition: 'all 0.2s ease', position: 'relative' },
  exerciseItemActive: { background: 'var(--day-card-selected-bg, linear-gradient(135deg, #1e1b4b 0%, #312e81 100%))', borderColor: '#6366f1', boxShadow: '0 4px 20px rgba(99, 102, 241, 0.3)' },
  btnStartLarge: { padding: '15px 40px', fontSize:'16px', borderRadius: '12px', background: '#6366f1', color: 'white', border: 'none', fontWeight: '800', cursor: 'pointer', marginTop:'20px', boxShadow: '0 4px 20px rgba(99, 102, 241, 0.4)' },
  btnStop: { flex: 1, borderRadius: '16px', background: 'var(--app-surface2)', border: '1px solid var(--app-border)', color: '#ef4444', fontWeight: '800', fontSize: '16px', cursor: 'pointer', transition:'all 0.2s' },
  btnDone: { flex: 1, borderRadius: '16px', background: '#22c55e', color: 'white', fontWeight: '800', fontSize: '16px', border:'none', cursor: 'pointer', boxShadow: '0 4px 15px rgba(34, 197, 94, 0.3)' },
  historyPanel: { position: 'fixed', top: '80px', right: '0', width: '400px', height: 'calc(100vh - 80px)', background: 'var(--app-bg)', borderLeft: '1px solid var(--app-border)', zIndex: 1500, padding: '24px', overflowY: 'auto', animation: 'slideInRight 0.3s ease-out', boxShadow: '-20px 0 50px rgba(0,0,0,0.5)' },
  historyItem: { background: 'var(--app-surface)', borderRadius: '16px', padding: '20px', marginBottom: '16px', border: '1px solid var(--app-border)', cursor: 'pointer', transition: 'all 0.2s' },
  historyDate: { fontSize: '14px', fontWeight: '700', color: 'var(--app-text)', marginBottom: '12px' },
  historySection: { marginBottom: '10px' },
  historyLabel: { fontSize: '11px', color: '#a5b4fc', fontWeight: '700', textTransform: 'uppercase', marginBottom: '4px' },
  historyList: { fontSize: '13px', color: 'var(--app-text-muted)', lineHeight: '1.4' },
  restDay: { padding: '20px', background: 'rgba(245, 158, 11, 0.1)', borderRadius: '12px', color: '#f59e0b', fontSize: '14px', textAlign: 'center', fontWeight: '500' }
};

// History dynamically fetched from node

const getTodayIdx = () => {
  // Use IST to stay aligned with date handling across the app/backend.
  const weekday = new Intl.DateTimeFormat('en-US', {
    timeZone: 'Asia/Kolkata',
    weekday: 'short',
  }).format(new Date());

  const indexByWeekday = {
    Mon: 0,
    Tue: 1,
    Wed: 2,
    Thu: 3,
    Fri: 4,
    Sat: 5,
    Sun: 6,
  };

  return indexByWeekday[weekday] ?? 0;
};

const isRestDay = (day) => {
  if (!day || day.is_placeholder) return false;
  // 1. Explicit type field from backend engine (most reliable)
  if (day.type === 'rest') return true;
  // 2. Focus field containing 'rest' (e.g. "Rest Day", "Rest", "Active Recovery")
  const focus = `${day.focus || ''}`.toLowerCase();
  if (focus.includes('rest') || focus === 'active recovery') return true;
  // 3. Day label or note containing 'rest'
  const label = `${day.day || ''}`.toLowerCase();
  const note = `${day.note || ''}`.toLowerCase();
  if (label.includes('rest') || note.includes('rest') || note.includes('recovery')) return true;
  // 4. No exercises AND type is not 'workout' → treat as rest
  const exercises = day.exercises || [];
  if (exercises.length === 0 && day.type !== 'workout') return true;
  return false;
};

const getDayStatus = (day, todayIdx, completedIds = new Set()) => {
  if (day?.is_placeholder && day?.type === 'past') return 'NOT_STARTED';
  if (day?.is_placeholder) return 'NO PLAN';
  if (isRestDay(day)) return 'REST';
  // Days before registration are explicitly marked as "past" by the backend.
  if (day.type === 'past') return 'NOT_STARTED';
  const dow = day.day_of_week ?? 0;
  if (completedIds.has(dow)) return 'COMPLETED';
  if (dow === todayIdx) return 'TODAY';
  if (dow < todayIdx) return 'PAST';
  return 'UPCOMING';
};

const findNextWorkoutDayIndex = (plan, todayIdx) => {
  const safe = Array.isArray(plan) ? plan : [];
  for (let idx = todayIdx + 1; idx <= 6; idx += 1) {
    const day = safe[idx];
    if (day && !day.is_placeholder && !isRestDay(day)) return idx;
  }
  return null;
};

const getFutureOriginalRestDays = (plan, sourceDayIdx, todayIdx) => {
  const safe = Array.isArray(plan) ? plan : [];
  return safe.filter((day) => {
    const idx = Number(day?.day_of_week);
    if (!Number.isInteger(idx)) return false;
    if (idx <= sourceDayIdx) return false;
    if (idx < todayIdx) return false;
    if (day?.is_placeholder) return false;
    if (!isRestDay(day)) return false;
    if (day?.is_original_rest === false) return false;
    if (day?.is_swapped) return false;
    if (day?.is_swappable === false) return false;
    return true;
  });
};

const getWeekStartDateIso = () => {
  const now = new Date();
  const day = now.getDay(); // 0=Sun..6=Sat
  const mondayOffset = day === 0 ? -6 : 1 - day;
  const monday = new Date(now);
  monday.setDate(now.getDate() + mondayOffset);
  return getLocalDateStr(monday);
};

const buildWeekMetadataFromPlan = (weeklyPlan = [], existingMetadata = null) => {
  const plan = Array.isArray(weeklyPlan) ? weeklyPlan : [];
  const metadata = (existingMetadata && typeof existingMetadata === 'object') ? existingMetadata : {};
  const existingSwapHistory = Array.isArray(metadata.swap_history) ? metadata.swap_history : [];
  const existingSwapLimits = metadata.swap_limits || {};

  const currentCounts = plan.reduce((acc, day) => {
    if (day?.is_placeholder) return acc;
    if (day?.type === 'rest') acc.rest_days += 1;
    if (day?.type === 'workout') acc.workout_days += 1;
    return acc;
  }, { rest_days: 0, workout_days: 0 });

  const originalCounts = plan.reduce((acc, day) => {
    if (day?.is_placeholder) return acc;
    const isOriginalRest = typeof day?.is_original_rest === 'boolean' ? day.is_original_rest : day?.type === 'rest';
    const isOriginalWorkout = typeof day?.is_original_workout === 'boolean' ? day.is_original_workout : day?.type === 'workout';
    if (isOriginalRest) acc.rest_days += 1;
    if (isOriginalWorkout) acc.workout_days += 1;
    return acc;
  }, { rest_days: 0, workout_days: 0 });

  const maxSwapsPerWeek = Math.max(1, Number(existingSwapLimits.max_swaps_per_week || 3));
  const swapsUsed = existingSwapHistory.length;

  return {
    week_start_date: metadata.week_start_date || getWeekStartDateIso(),
    user_registration_day: Number.isInteger(metadata.user_registration_day) ? metadata.user_registration_day : null,
    is_new_user_week: Boolean(metadata.is_new_user_week),
    swap_history: existingSwapHistory,
    swap_limits: {
      max_swaps_per_week: maxSwapsPerWeek,
      swaps_used: swapsUsed,
      swaps_remaining: Math.max(0, maxSwapsPerWeek - swapsUsed),
    },
    original_counts: originalCounts,
    current_counts: currentCounts,
    updated_at: metadata.updated_at || new Date().toISOString(),
  };
};

const formatSwapTimestamp = (value) => {
  if (!value) return 'Unknown time';
  const parsed = new Date(value);
  if (Number.isNaN(parsed.getTime())) return String(value);
  return parsed.toLocaleString();
};

const Workout = () => {
  const navigate = useNavigate();
  const location = useLocation();
  const autoStartDay = location.state?.autoStartDay;
  const autoStartHandledRef = useRef(false);
  const handleExerciseCompleteRef = useRef(null);
  const videoRef = useRef(null);
  const notifRef = useRef(null);
  const { showError, showSuccess } = useNotification();
  const { theme, toggleTheme } = useTheme();
  const [confirmDialog, setConfirmDialog] = useState({ show: false, message: '', onConfirm: null });
  const [showWorkoutToRestModal, setShowWorkoutToRestModal] = useState(false);
  const [swapWorkoutDayIndex, setSwapWorkoutDayIndex] = useState(null);
  const [selectedTargetRestDayIndex, setSelectedTargetRestDayIndex] = useState(null);

  // State declarations
  const [plan, setPlan] = useState([]);
  const [activeDay, setActiveDay] = useState(null);
  const [activeExercise, setActiveExercise] = useState(null);
  const [isCameraOn, setIsCameraOn] = useState(false);
  const [stream, setStream] = useState(null);
  const [showNotif, setShowNotif] = useState(false);
  const [showHistory, setShowHistory] = useState(false);
  const [historyTab, setHistoryTab] = useState('workout');
  const [selectedHistory, setSelectedHistory] = useState(null);
  const [weekMetadata, setWeekMetadata] = useState(() => getFromStorage(StorageKeys.WORKOUT_WEEK_METADATA, null));
  const [poseTrackingError] = useState(null);
  const [, setLoading] = useState(false);
  const [, setError] = useState(null);
  const [pastWorkouts, setPastWorkouts] = useState([]);
  // ✅ FIX: Track completed day indices in React state, hydrated from backend on mount.
  // Old approach read localStorage keys ('workout_done_Monday') which reset on every new browser session.
  const [completedDayIndices, setCompletedDayIndices] = useState(new Set());

  // Posture processing state
  const [currentSet, setCurrentSet] = useState(1);
  const [currentReps, setCurrentReps] = useState(0);
  const [isResting, setIsResting] = useState(false);
  const [restTimeLeft, setRestTimeLeft] = useState(0);
  const [restEndTime, setRestEndTime] = useState(0); // For background-safe timers
  const [exerciseTimeLeft, setExerciseTimeLeft] = useState(0);
  const [exerciseEndTime, setExerciseEndTime] = useState(0); // For background-safe timers
  const [skippedExercises, setSkippedExercises] = useState(new Set());
  const [completedSetsMap, setCompletedSetsMap] = useState({});
  // ✅ FIX: Pre-hydrate exerciseStatus from localStorage so red ticks survive refresh without a network call.
  const [exerciseStatus, setExerciseStatus] = useState(() => {
    try {
      const savedDate = localStorage.getItem('_exerciseStatusDate');
      const todayStr = new Date().toLocaleDateString('en-CA', { timeZone: 'Asia/Kolkata' });
      // Clear stale cache from a different day — don't show yesterday's skips today
      if (savedDate && savedDate !== todayStr) {
        localStorage.removeItem('_exerciseStatus');
        localStorage.removeItem('_exerciseStatusDate');
        localStorage.removeItem('_exerciseStatusDay');
        return {};
      }
      const saved = localStorage.getItem('_exerciseStatus');
      return saved ? JSON.parse(saved) : {};
    } catch { return {}; }
  });
  const [formFeedback, setFormFeedback] = useState(null);
  // Priority 1: variation suggestion returned by /api/workout/session-result
  const [variationResult, setVariationResult] = useState(null);
  const [isDoneSession, setIsDoneSession] = useState(false);
  const [_completedExercisesCount, setCompletedExercisesCount] = useState(0); // tracks per-exercise progress for Dashboard
  const [mediaUrlIndex, setMediaUrlIndex] = useState(0);
  
  // Bug #2 Fix: Pose detector loading state
  const [poseLoadingStatus, setPoseLoadingStatus] = useState('initializing'); // 'initializing' → 'warming' → 'ready'
  
  const [viewportWidth, setViewportWidth] = useState(
    typeof window !== 'undefined' ? window.innerWidth : 1280
  );

  useEffect(() => {
    const handleResize = () => setViewportWidth(window.innerWidth);
    window.addEventListener('resize', handleResize);
    return () => window.removeEventListener('resize', handleResize);
  }, []);

  const isMobileLayout = viewportWidth <= 980;
  const workoutLayout = isMobileLayout
    ? {
        container: { ...styles.container, padding: 'clamp(12px, 4vw, 24px)' },
        h1: { ...styles.h1, fontSize: 'clamp(28px, 5vw, 42px)', marginBottom: 'clamp(16px, 3vw, 30px)' },
        grid: { ...styles.grid, gridTemplateColumns: 'repeat(auto-fit, minmax(240px, 1fr))', gap: 'clamp(12px, 2.4vw, 20px)' },
        card: { ...styles.card, padding: 'clamp(14px, 2.4vw, 24px)', minHeight: '180px' },
        restDay: { ...styles.restDay, padding: 'clamp(12px, 2.8vw, 20px)' },
        sessionContainer: {
          ...styles.sessionContainer,
          height: 'calc(100dvh - 80px)',
          flexWrap: 'wrap',
          alignContent: 'flex-start',
          overflowY: 'auto',
          padding: 'clamp(10px, 2vw, 20px)',
          gap: 'clamp(10px, 2vw, 20px)'
        },
        selectionList: { ...styles.selectionList, flex: '1 1 min(100%, 350px)', maxWidth: 'min(100%, 360px)' },
        focusContainer: { ...styles.focusContainer, minHeight: 0, height: 'auto', flexWrap: 'wrap', gap: 'clamp(10px, 2vw, 20px)' },
        focusLeft: { ...styles.focusLeft, flex: '1 1 min(100%, 420px)', padding: 'clamp(12px, 2.5vw, 24px)' },
        controlsContainer: { ...styles.controlsContainer, height: 'auto', minHeight: '68px', gap: '12px', flexWrap: 'wrap' },
        focusRight: { ...styles.focusRight, flex: '1 1 min(100%, 520px)', minHeight: '280px' },
        historyPanel: { ...styles.historyPanel, width: 'min(96vw, 400px)', height: 'calc(100dvh - 80px)', padding: 'clamp(14px, 2.5vw, 24px)' },
        previewMedia: { width: 'min(100%, 420px)', aspectRatio: '16 / 10', marginBottom: '24px', flex: 'none' }
      }
    : {
        container: styles.container,
        h1: styles.h1,
        grid: styles.grid,
        card: styles.card,
        restDay: styles.restDay,
        sessionContainer: styles.sessionContainer,
        selectionList: styles.selectionList,
        focusContainer: styles.focusContainer,
        focusLeft: styles.focusLeft,
        controlsContainer: styles.controlsContainer,
        focusRight: styles.focusRight,
        historyPanel: styles.historyPanel,
        previewMedia: { width: '350px', height: '220px', marginBottom: '30px', flex: 'none' }
      };

  const showConfirmDialog = useCallback((message, onConfirm) => {
    setConfirmDialog({ show: true, message, onConfirm });
  }, []);

  const handleConfirm = () => {
    if (confirmDialog.onConfirm) {
      confirmDialog.onConfirm(true); // User clicked "Confirm" = Yes
    }
    setConfirmDialog({ show: false, message: '', onConfirm: null });
  };

  const handleCancelConfirm = () => {
    if (confirmDialog.onConfirm) {
      confirmDialog.onConfirm(false); // User clicked "Cancel" = No
    }
    setConfirmDialog({ show: false, message: '', onConfirm: null });
  };

  const todayDate = new Date().toLocaleDateString('en-US', { weekday: 'short', month: 'short', day: 'numeric' });

  const normalizeMediaUrl = (url) => {
    if (!url || typeof url !== 'string') return '';
    const trimmed = url.trim();
    if (!trimmed) return '';

    if (trimmed.startsWith('//')) {
      return `https:${trimmed}`;
    }

    // Convert giphy page URLs to direct media links.
    if (/^https?:\/\/giphy\.com\/gifs\//i.test(trimmed)) {
      const slug = trimmed.split('/').filter(Boolean).pop() || '';
      const gifId = slug.includes('-') ? slug.split('-').pop() : slug;
      if (gifId && gifId.length >= 5) {
        return `https://media.giphy.com/media/${gifId}/giphy.gif`;
      }
    }

    return trimmed;
  };

  const getExerciseMediaCandidates = (exercise) => {
    if (!exercise) return [];
    const raw = [
      exercise.Wger_Image_URL,
      exercise.wger_image_url,
      exercise.wgerImageUrl,
      exercise.gif,
      exercise.video_url,
      exercise.videoUrl,
      exercise.image,
      exercise.thumbnail,
      exercise.media_url,
      exercise.mediaUrl,
      exercise.demo_url,
      exercise.demoUrl,
    ];
    const seen = new Set();
    return raw.map(normalizeMediaUrl).filter((trimmed) => {
      if (!trimmed) return false;
      if (!trimmed.startsWith('http://') && !trimmed.startsWith('https://')) return false;
      if (seen.has(trimmed)) return false;
      seen.add(trimmed);
      return true;
    });
  };

  // A plan is renderable if it has at least one exercise. Exercises without a GIF
  // show a styled placeholder — that is intentional and correct. We only reject
  // plans that are completely empty or structurally malformed.
  const planHasRenderableMedia = (candidatePlan) => {
    if (!Array.isArray(candidatePlan) || candidatePlan.length === 0) return false;
    let exerciseCount = 0;
    for (const day of candidatePlan) {
      const exercises = Array.isArray(day?.exercises) ? day.exercises : [];
      exerciseCount += exercises.length;
    }
    return exerciseCount > 0;
  };

  const isVideoUrl = (url) => {
    if (!url || typeof url !== 'string') return false;
    const clean = url.toLowerCase().split('?')[0].split('#')[0];
    return ['.mp4', '.webm', '.ogg', '.mov', '.m3u8'].some((ext) => clean.endsWith(ext));
  };

  // Issue #3 – detect YouTube embed URLs returned by youtube_service.py
  const isYouTubeUrl = (url) => {
    if (!url || typeof url !== 'string') return false;
    return url.includes('youtube.com/embed') || url.includes('youtu.be/');
  };

  const getMovementCue = (exerciseName = '') => {
    const lower = String(exerciseName).toLowerCase();
    if (lower.includes('squat') || lower.includes('lunge') || lower.includes('leg')) return 'Control knee alignment and depth';
    if (lower.includes('curl') || lower.includes('bicep')) return 'Keep elbows pinned and use full range';
    if (lower.includes('press') || lower.includes('push')) return 'Brace core and press in a straight path';
    if (lower.includes('row') || lower.includes('pull') || lower.includes('deadlift')) return 'Keep back neutral and pull with control';
    if (lower.includes('plank') || lower.includes('core') || lower.includes('crunch')) return 'Maintain neutral spine and steady breathing';
    return 'Move smoothly with controlled tempo';
  };

  const parseDurationToSeconds = useCallback((value) => {
    const text = String(value ?? '').trim().toLowerCase();
    if (!text) return 0;

    const matches = text.match(/\d+/g) || [];
    const nums = matches.map((n) => parseInt(n, 10)).filter((n) => !Number.isNaN(n));
    if (nums.length === 0) return 0;

    const maxNum = Math.max(...nums);
    if (text.includes('min')) return maxNum * 60;
    if (text.includes('sec') || text.includes('second')) return maxNum;
    return 0;
  }, []);

  const getTargetSets = (exercise) => {
    if (!exercise) return 1;
    const parsedSets = parseInt(String(exercise.sets ?? '1').replace(/[^0-9]/g, ''), 10);
    if (!Number.isNaN(parsedSets) && parsedSets > 0) return parsedSets;
    return 1;
  };

  const getTargetReps = (exercise) => {
    if (!exercise) return 10;
    let text = String(exercise.reps ?? '10');
    if (text.includes('-')) text = text.split('-')[1];
    const parsedReps = parseInt(text.replace(/[^0-9]/g, ''), 10);
    if (!Number.isNaN(parsedReps) && parsedReps > 0) return parsedReps;
    return 10;
  };

  const getRestSeconds = (exercise) => {
    if (!exercise) return 60;
    const parsedRest = parseInt(String(exercise.rest ?? '60').replace(/[^0-9]/g, ''), 10);
    if (!Number.isNaN(parsedRest) && parsedRest > 0) return parsedRest;
    return 60;
  };

  const getExerciseDurationSeconds = useCallback((exercise) => {
    if (!exercise) return 0;

    const explicitDuration = Number(exercise.duration_seconds);
    if (Number.isFinite(explicitDuration) && explicitDuration > 0) {
      return Math.floor(explicitDuration);
    }

    const repsDuration = parseDurationToSeconds(exercise.reps);
    if (repsDuration > 0) return repsDuration;

    const fallbackDuration = parseDurationToSeconds(exercise.duration || exercise.time || '');
    return fallbackDuration > 0 ? fallbackDuration : 0;
  }, [parseDurationToSeconds]);

  const getExerciseStatusKey = (exercise) => {
    if (!exercise) return '';
    const name = String(exercise.name || '').trim();
    const sets = String(exercise.sets ?? '').trim();
    const reps = String(exercise.reps ?? '').trim();
    const warmup = exercise.is_warmup ? 'warmup' : 'main';
    return `${name}|${sets}|${reps}|${warmup}`;
  };

  const isPoseTrackableExercise = useCallback((exercise) => {
    if (!exercise) return false;

    if (exercise.needs_camera === false || exercise.needsCamera === false) {
      return false;
    }

    if (String(exercise.exercise_mode || '').toLowerCase() === 'cardio') {
      return false;
    }

    if (typeof exercise.trackable === 'boolean') {
      return exercise.trackable;
    }

    if (getExerciseDurationSeconds(exercise) > 0) {
      return false;
    }

    const lower = String(exercise.name || '').toLowerCase();
    const nonTrackableKeywords = [
      'walk', 'jog', 'run', 'bike', 'cycle', 'cardio',
      'stretch', 'mobility', 'warm-up', 'warm up'
    ];
    if (nonTrackableKeywords.some((kw) => lower.includes(kw))) {
      return false;
    }

    return true;
  }, [getExerciseDurationSeconds]);

  const exerciseNeedsCamera = useCallback((exercise) => {
    if (!exercise) return true;
    if (typeof exercise.needs_camera === 'boolean') return exercise.needs_camera;
    if (typeof exercise.needsCamera === 'boolean') return exercise.needsCamera;
    return isPoseTrackableExercise(exercise);
  }, [isPoseTrackableExercise]);

  const isTimedExercise = useCallback((exercise) => {
    if (!exercise) return false;
    if (exercise.is_timed === true) return true;
    if (!exerciseNeedsCamera(exercise)) return true;
    return !isPoseTrackableExercise(exercise) && getExerciseDurationSeconds(exercise) > 0;
  }, [exerciseNeedsCamera, isPoseTrackableExercise, getExerciseDurationSeconds]);

  const formatDurationClock = (seconds) => {
    const safe = Math.max(0, Number(seconds) || 0);
    const mins = Math.floor(safe / 60);
    const secs = safe % 60;
    return `${String(mins).padStart(2, '0')}:${String(secs).padStart(2, '0')}`;
  };

  // Shown when an exercise has no GIF/image available (blacklisted or failed to load).
  const renderExerciseNoGifPlaceholder = (exerciseName) => {
    const cue = getMovementCue(exerciseName);
    const emoji = (() => {
      const lower = String(exerciseName || '').toLowerCase();
      if (lower.includes('squat') || lower.includes('lunge')) return '🦵';
      if (lower.includes('curl') || lower.includes('bicep')) return '💪';
      if (lower.includes('press') || lower.includes('bench')) return '🏋️';
      if (lower.includes('row') || lower.includes('pull') || lower.includes('deadlift')) return '🔙';
      if (lower.includes('plank') || lower.includes('crunch') || lower.includes('core')) return '🧱';
      if (lower.includes('stretch') || lower.includes('mobility') || lower.includes('warm')) return '🧘';
      if (lower.includes('run') || lower.includes('walk') || lower.includes('jog') || lower.includes('cardio')) return '🏃';
      if (lower.includes('jump') || lower.includes('plyo') || lower.includes('burpee')) return '⚡';
      if (lower.includes('shoulder') || lower.includes('raise')) return '🏋️';
      if (lower.includes('calf') || lower.includes('ankle')) return '🦶';
      return '🏅';
    })();

    return (
      <div style={{
        ...styles.gifLarge,
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        justifyContent: 'center',
        gap: '12px',
        background: 'var(--workout-banner-bg)',
        padding: '20px',
        textAlign: 'center',
      }}>
        {/* Animated exercise icon */}
        <div style={{
          width: '88px',
          height: '88px',
          borderRadius: '50%',
          background: 'linear-gradient(135deg, rgba(99,102,241,0.15) 0%, rgba(34,211,238,0.1) 100%)',
          border: '2px solid rgba(99,102,241,0.3)',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          fontSize: '38px',
          animation: 'pulseBorder 2.5s infinite',
        }}>
          {emoji}
        </div>

        {/* Exercise name */}
        <div style={{
          color: 'var(--app-text)',
          fontWeight: 700,
          fontSize: '15px',
          maxWidth: '240px',
          lineHeight: 1.3,
        }}>
          {exerciseName || 'Exercise'}
        </div>

        {/* Coaching cue */}
        <div style={{
          color: '#a5b4fc',
          fontSize: '12px',
          maxWidth: '220px',
          lineHeight: 1.5,
          fontStyle: 'italic',
        }}>
          {cue}
        </div>

        {/* Badge */}
        <div style={{
          marginTop: '4px',
          padding: '4px 12px',
          background: 'rgba(99,102,241,0.12)',
          border: '1px solid rgba(99,102,241,0.25)',
          borderRadius: '20px',
          color: '#818cf8',
          fontSize: '10px',
          fontWeight: 700,
          textTransform: 'uppercase',
          letterSpacing: '0.8px',
        }}>
          Text Guide Mode
        </div>
      </div>
    );
  };

  const handleMediaError = () => {
    console.warn(`Media completely failed to load at index ${mediaUrlIndex}. Trying next.`);
    setMediaUrlIndex((prev) => prev + 1);
  };

  const renderActiveExerciseMedia = () => {
    // If the exercise is explicitly marked as having no GIF (blacklisted on backend),
    // show the no-GIF placeholder immediately without attempting to load any image.
    if (activeExercise?.media_type === 'none') {
      return renderExerciseNoGifPlaceholder(activeExercise?.name);
    }

    const candidates = getExerciseMediaCandidates(activeExercise);
    const currentUrl = candidates[mediaUrlIndex] || '';

    if (!currentUrl) {
      return renderExerciseNoGifPlaceholder(activeExercise?.name);
    }

    // Issue #3 – YouTube embed (from youtube_service.py fallback)
    if (isYouTubeUrl(currentUrl)) {
      return (
        <iframe
          key={currentUrl}
          src={currentUrl}
          title={activeExercise?.name || 'Exercise demo'}
          style={{ ...styles.gifLarge, border: 'none' }}
          allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
          allowFullScreen
        />
      );
    }

    if (isVideoUrl(currentUrl)) {
      return (
        <video
          key={currentUrl}
          autoPlay
          loop
          muted
          playsInline
          style={styles.gifLarge}
          onError={handleMediaError}
        >
          <source src={currentUrl} onError={handleMediaError} />
        </video>
      );
    }

    return (
      <img
        key={currentUrl}
        src={currentUrl}
        style={styles.gifLarge}
        alt="Guide"
        onError={handleMediaError}
      />
    );
  };

  useEffect(() => {
    setMediaUrlIndex(0);
    if (activeExercise && isTimedExercise(activeExercise)) {
      setExerciseTimeLeft(getExerciseDurationSeconds(activeExercise) || 300);
    } else {
      setExerciseTimeLeft(0);
    }
  }, [activeExercise, getExerciseDurationSeconds, isTimedExercise]);

  useEffect(() => {
    const handleClickOutside = (event) => {
      if (notifRef.current && !notifRef.current.contains(event.target)) {
        setShowNotif(false);
      }
    };
    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  const saveLog = async (name, details, dayName = '') => {
    const newLog = {
      name: name,
      status: 'Completed',
      // ✅ FIX: Store both ISO timestamp AND local date string.
      // `date` (ISO) is used for display; `dateStr` (YYYY-MM-DD local) is used for today-matching
      // in fetchHistory so it works correctly in all timezones (not just UTC).
      date: new Date().toISOString(),
      dateStr: getLocalDateStr(), // e.g. '2026-04-19' in local timezone
      dayName: dayName,           // e.g. 'Sunday' — critical for day-index hydration
      time: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
      details: details,
      type: "workout"
    };
    // Save to node backend instead of localstorage
    try {
      const response = await saveWorkoutHistory(newLog);
      if (response?.data?.success) {
        setPastWorkouts(response.data.history || []);
      }
      return response;
    } catch (err) {
      console.error("Error saving workout history:", err);
      throw err;
    }
  };

  useEffect(() => {
    if (isCameraOn && videoRef.current && stream) {
      videoRef.current.srcObject = stream;
    }
  }, [isCameraOn, stream]);

  // ===== HELPER FUNCTIONS =====
  
  /**
   * Create fallback workout plan if backend returns empty
   */
  const createFallbackPlan = () => {
    console.log('🔄 Creating fallback workout plan');
    const dayNames = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'];
    const fallbackExercises = [
      {
        name: 'Push-ups',
        sets: 3,
        reps: '10-12',
        rest: '60 seconds',
        notes: 'Bodyweight',
        gif: DEFAULT_FALLBACK_GIF,
        image: DEFAULT_FALLBACK_GIF,
        video_url: '',
        media_type: 'image'
      },
      {
        name: 'Squats',
        sets: 3,
        reps: '10-12',
        rest: '60 seconds',
        notes: 'Bodyweight',
        gif: DEFAULT_FALLBACK_GIF,
        image: DEFAULT_FALLBACK_GIF,
        video_url: '',
        media_type: 'image'
      },
      {
        name: 'Plank',
        sets: 3,
        reps: '30 seconds',
        rest: '60 seconds',
        notes: 'Core',
        gif: DEFAULT_FALLBACK_GIF,
        image: DEFAULT_FALLBACK_GIF,
        video_url: '',
        media_type: 'image'
      }
    ];
    
    return dayNames.map((day, idx) => ({
      day_of_week: idx,
      day: day,
      focus: idx < 4 ? 'Full Body' : 'Rest Day',
      type: idx < 4 ? 'workout' : 'rest',
      exercises: idx < 4 ? fallbackExercises : [],
      note: idx < 4 ? 'Full Body training' : 'Recovery and rest'
    }));
  };

  /**
   * Normalize plan to always have 7 days
   */
  const normalizeToSevenDays = (plan) => {
    const dayNames = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'];
    const normalized = [...plan];
    
    // Pad with rest days if less than 7
    while (normalized.length < 7) {
      const idx = normalized.length;
      normalized.push({
        day_of_week: idx,
        day: dayNames[idx],
        focus: 'Rest Day',
        type: 'rest',
        exercises: [],
        note: 'Recovery and rest'
      });
    }
    
    // Trim if more than 7
    return normalized.slice(0, 7);
  };

  useEffect(() => {
    // Track if component is mounted to prevent state updates after unmount
    let isMounted = true;

    // Preload pose assets when user reaches workout page for faster camera startup.
    preloadPoseAssets().catch((err) => {
      console.warn('Pose asset preload skipped:', err?.message || err);
    });

    const fetchWorkoutPlan = async (forceRefresh = false, profileData = null) => {
      let hydratedFromCache = false;

      const tryLoadPersistedPlan = async (reason = 'normal') => {
        try {
          const weeklyPlanResponse = await getWeeklyWorkoutPlan();
          const persistedPlan =
            weeklyPlanResponse?.data?.plan
            || weeklyPlanResponse?.data?.data?.plan
            || [];
          const persistedWeekMetadata =
            weeklyPlanResponse?.data?.week_metadata
            || weeklyPlanResponse?.data?.data?.week_metadata
            || null;

          if (!Array.isArray(persistedPlan) || persistedPlan.length === 0) {
            return false;
          }

          const normalizedPlan = normalizeWeeklyPlan(persistedPlan);
          const normalizedWeekMetadata = buildWeekMetadataFromPlan(
            normalizedPlan,
            persistedWeekMetadata || weekMetadata
          );

          if (isMounted) {
            setPlan(normalizedPlan);
            setWeekMetadata(normalizedWeekMetadata);
            localStorage.setItem('workoutPlan', JSON.stringify(normalizedPlan));
            localStorage.setItem('workoutPlanTimestamp', new Date().toISOString());
            localStorage.setItem('workoutPlanVersion', WORKOUT_PLAN_CACHE_VERSION);
            localStorage.setItem(StorageKeys.WORKOUT_WEEK_METADATA, JSON.stringify(normalizedWeekMetadata));
            console.log(`✅ Loaded persisted weekly plan from backend (${reason})`);
          }

          return true;
        } catch (persistedErr) {
          console.warn(`⚠️ Could not load persisted weekly plan (${reason}):`, persistedErr?.message || persistedErr);
          return false;
        }
      };

      try {
        if (isMounted) {
          setLoading(true);
          setError(null);
        }

        console.log('🏋️ Fetching workout plan...', forceRefresh ? '(Force Refresh)' : '(Cache Check)');

        const token = localStorage.getItem('token');
        if (!token) {
          throw new Error('No authentication token found');
        }

        // ✅ FIX: Use fresh profile from API instead of stale localStorage.user
        // localStorage.user only has {id, name, email} — no fitness profile fields!
        let userProfile = profileData;
        if (!userProfile) {
          try {
            const profileRes = await getProfile();
            userProfile = profileRes.data;
          } catch {
            userProfile = getFromStorage('user', {});
          }
        }
        console.log('👤 User profile for workout:', userProfile);

        // **Check if cached plan exists and is not expired**
        let cachedPlan = localStorage.getItem('workoutPlan');
        let cachedTimestamp = localStorage.getItem('workoutPlanTimestamp');
        const cachedVersion = localStorage.getItem('workoutPlanVersion');

        if (cachedPlan && cachedVersion !== WORKOUT_PLAN_CACHE_VERSION) {
          localStorage.removeItem('workoutPlan');
          localStorage.removeItem('workoutPlanTimestamp');
          localStorage.setItem('workoutPlanVersion', WORKOUT_PLAN_CACHE_VERSION);
          cachedPlan = null;
          cachedTimestamp = null;
          console.log('🧹 Cleared outdated workout cache version');
        }

        let parsedCachedPlan = [];
        if (cachedPlan) {
          parsedCachedPlan = getFromStorage('workoutPlan', []);
          if (!planHasRenderableMedia(parsedCachedPlan)) {
            localStorage.removeItem('workoutPlan');
            localStorage.removeItem('workoutPlanTimestamp');
            cachedPlan = null;
            cachedTimestamp = null;
            parsedCachedPlan = [];
            console.log('🧹 Cleared stale cache with missing exercise media');
          }
        }

        // Always hydrate immediately from any cached plan for fast first paint.
        if (cachedPlan) {
          if (Array.isArray(parsedCachedPlan) && parsedCachedPlan.length > 0 && isMounted) {
            setPlan(normalizeWeeklyPlan(parsedCachedPlan));
            setLoading(false);
            hydratedFromCache = true;
            console.log('⚡ Hydrated workout UI from cache immediately');
          }
        }

        if (cachedPlan && cachedTimestamp && !forceRefresh) {
          const timestamp = new Date(cachedTimestamp);
          const now = new Date();
          const hoursSinceCache = (now - timestamp) / (1000 * 60 * 60);

          // Cache valid for 24 hours
          if (hoursSinceCache < 24) {
            console.log('✅ Using cached workout plan (age: ' + hoursSinceCache.toFixed(1) + ' hours)');
            if (isMounted) setLoading(false);
            return;
          } else {
            console.log('⏰ Cache expired (age: ' + hoursSinceCache.toFixed(1) + ' hours), refreshing in background');
          }
        } else if (forceRefresh) {
          console.log('🔄 Force refresh requested, refreshing in background');
        } else {
          console.log('📭 No cached plan found, fetching from server');
        }

        // Try reading already persisted weekly plan first. This avoids blank workout pages
        // after relogin when generation is rate-limited or temporarily unavailable.
        const loadedPersistedPlan = await tryLoadPersistedPlan('pre-generate');
        if (loadedPersistedPlan && !forceRefresh) {
          if (isMounted) setLoading(false);
          return;
        }

        // **Fetch new plan from server using FULL profile data**
        console.log('🌐 Requesting workout plan from server...');
        const response = await generateWorkout(userProfile);

        // If the request was cancelled (e.g., component unmounted), response is null — exit cleanly.
        if (!response) {
          console.log('🚫 Workout request was cancelled (null response). Skipping update.');
          return;
        }

        console.log('✅ Workout plan received:', response.data);

        // ===== VALIDATE RESPONSE STRUCTURE =====
        // Backend returns: { success: true, workout: [...], exercises_count: number }
        
        if (!response.data) {
          throw new Error('Empty response from server');
        }

        if (response.data.success !== true) {
          const errorMsg = response.data.error || response.data.detail || 'Backend returned failure status';
          throw new Error(errorMsg);
        }

        // Check for workout array (could be at response.data.workout OR response.data.data.workout)
        let workoutPlan = null;
        
        if (Array.isArray(response.data.workout)) {
          // ✅ Correct structure: { success: true, workout: [...] }
          workoutPlan = response.data.workout;
          console.log('📊 Using response.data.workout');
        } else if (response.data.data && Array.isArray(response.data.data.weekly_plan)) {
          // Fallback for alternative structure: { success: true, data: { weekly_plan: [...] } }
          workoutPlan = response.data.data.weekly_plan;
          console.log('📊 Using response.data.data.weekly_plan (fallback)');
        } else {
          console.error('❌ Invalid response structure:', response.data);
          throw new Error('Backend returned invalid workout structure');
        }

        // Validate workout plan is not empty
        if (!Array.isArray(workoutPlan) || workoutPlan.length === 0) {
          console.warn('⚠️ Received empty workout plan');
          // Don't throw - use fallback
          workoutPlan = createFallbackPlan();
        }

        // Validate plan has 7 days
        if (workoutPlan.length !== 7) {
          console.warn(`⚠️ Expected 7 days, got ${workoutPlan.length}. Padding with rest days.`);
          workoutPlan = normalizeToSevenDays(workoutPlan);
        }

        const normalizedPlan = normalizeWeeklyPlan(workoutPlan);
        const serverWeekMetadata = response.data?.week_metadata
          || response.data?.data?.week_metadata
          || null;
        const normalizedWeekMetadata = buildWeekMetadataFromPlan(normalizedPlan, serverWeekMetadata || weekMetadata);

        if (isMounted) {
          setPlan(normalizedPlan);
          setWeekMetadata(normalizedWeekMetadata);

          // **Cache the new plan**
          localStorage.setItem('workoutPlan', JSON.stringify(normalizedPlan));
          localStorage.setItem('workoutPlanTimestamp', new Date().toISOString());
          localStorage.setItem('workoutPlanVersion', WORKOUT_PLAN_CACHE_VERSION);
          localStorage.setItem(StorageKeys.WORKOUT_WEEK_METADATA, JSON.stringify(normalizedWeekMetadata));
          console.log('💾 Workout plan cached');
          console.log(`📊 Plan has ${normalizedPlan.length} days`);
        }
      } catch (err) {
        console.error('❌ Error fetching workout plan:', err);

        if (!hydratedFromCache) {
          const recoveredFromPersistedPlan = await tryLoadPersistedPlan('recovery-after-error');
          if (recoveredFromPersistedPlan) {
            if (isMounted) setError(null);
            return;
          }
        }

        // Classify error for better user feedback
        let errorMessage = 'Failed to load workout plan';
        let showErrorMsg = true;

        if (err.response?.status === 429) {
          // Rate limited - show retry_after time
          const retryAfter = err.response?.data?.retry_after || 10;
          errorMessage = `⏳ Please wait ${retryAfter} seconds before requesting another workout plan.`;
          console.log(`⏳ Rate limited. Retry after ${retryAfter}s`);
          // Don't show error popup for rate limiting - just log it
          showErrorMsg = false;
        } else if (!err.response) {
          // Network error - backend not reachable
          errorMessage = 'Cannot connect to backend server. Please ensure it\'s running on port 8000.';
        } else if (err.response?.status === 404) {
          errorMessage = 'Workout endpoint not found. Backend may need updating.';
        } else if (err.response?.status === 500) {
          errorMessage = 'Backend error. Please try again later.';
        } else if (err.code === 'ECONNABORTED' || err.message?.includes('timeout')) {
          errorMessage = 'Request timed out. Backend is taking too long to respond.';
        } else if (err.response?.data?.detail) {
          errorMessage = err.response.data.detail;
        }

        if (isMounted && hydratedFromCache && showErrorMsg) {
          setError(errorMessage);
          showError(errorMessage, 5000);
        } else if (isMounted && !showErrorMsg) {
          // For rate limiting, just log without showing error popup
          console.warn('⚠️ Workout request rate limited. Will retry on next render.');
        }
      } finally {
        if (isMounted) {
          setLoading(false);
        }
      }
    };

    const checkAndFetchPlan = async () => {
      try {
        // Always fetch profile first to get latest data
        const profileRes = await getProfile();
        const profile = profileRes.data;

        // Bug #5 fix: use safe JSON parsing — corrupted localStorage won't crash the page.
        const storedProfile = getFromStorage('workoutPlanProfile', {});
        // Issue #1 – include registration day so the engine can generate a rolling week plan.
        const storedUser = getFromStorage('user', {});
        const currentProfile = {
          user_id: storedUser.id || profile._id || profile.id || null,
          goal: profile.goal || 'Muscle Gain',
          experience: profile.experience || 'Beginner',
          equipment: Array.isArray(profile.equipment) ? profile.equipment : (profile.equipment ? [profile.equipment] : []),
          body_issues: Array.isArray(profile.body_issues) ? profile.body_issues : (profile.body_issues ? [profile.body_issues] : []),
          days_per_week: profile.days_per_week || 4,
          weight: profile.weight || 70,
          height: profile.height || 175,
          age: profile.age || 25,
          gender: profile.gender || 'Male',
          firstWorkoutDay: storedUser.firstWorkoutDay ?? profile.firstWorkoutDay ?? null,
          registrationDate: storedUser.registrationDate ?? profile.registrationDate ?? null,
        };

        // Normalize arrays for comparison (sort to ensure consistent order)
        const normalizeForComparison = (obj) => {
          const normalized = { ...obj };
          if (Array.isArray(normalized.equipment)) {
            normalized.equipment = [...normalized.equipment].sort();
          }
          if (Array.isArray(normalized.body_issues)) {
            normalized.body_issues = [...normalized.body_issues].sort();
          }
          return normalized;
        };

        const storedNormalized = normalizeForComparison(storedProfile);
        const currentNormalized = normalizeForComparison(currentProfile);

        console.log("\n" + "=".repeat(60));
        console.log("WORKOUT PLAN CHECK");
        console.log("=".repeat(60));
        console.log("📊 Stored profile (from localStorage):", storedNormalized);
        console.log("📊 Current profile (from API):", currentNormalized);
        
        let profileChanged = false;
        if (storedProfile && Object.keys(storedProfile).length > 0) {
          profileChanged = JSON.stringify(storedNormalized) !== JSON.stringify(currentNormalized);
        }
        const cachedPlan = getFromStorage('workoutPlan', []);
        const hasLegacyDemoData = Array.isArray(cachedPlan) && cachedPlan.some((day) =>
          Array.isArray(day?.exercises) && day.exercises.some((ex) => String(ex?.id || '').startsWith('demo-bicep-'))
        );
        if (hasLegacyDemoData) {
          localStorage.removeItem('workoutPlan');
          localStorage.removeItem('workoutPlanTimestamp');
          console.log('🧹 Removed legacy demo workout cache');
        }
        const hasCachedPlan = !!localStorage.getItem('workoutPlan');

        console.log("🔍 Profile changed:", profileChanged);
        console.log("🔍 Has cached plan:", hasCachedPlan);
        const fetchReason = !hasCachedPlan
          ? 'NO CACHE - Will fetch new plan'
          : (profileChanged ? 'CHANGED - Will fetch new plan' : 'UNCHANGED - Using cached plan');
        console.log("📊 Profile comparison:", fetchReason);
        console.log("=".repeat(60) + "\n");

        if (!hasCachedPlan || profileChanged) {
          console.log("🔄 Fetching new workout plan...");
          // ✅ FIX: Pass the fresh profile to fetchWorkoutPlan
          await fetchWorkoutPlan(profileChanged, currentProfile);
          localStorage.setItem('workoutPlanProfile', JSON.stringify(currentNormalized));
          console.log("✅ New workout plan fetched and profile saved");
        } else {
          console.log("✅ Using cached workout plan");
          const cached = localStorage.getItem('workoutPlan');
          if (cached) {
            const parsed = getFromStorage('workoutPlan', []);
            console.log("📊 Cached plan has", parsed.breakfast ? 'nutrition plan' : Object.keys(parsed).length, "days");
            const normalizedPlan = normalizeWeeklyPlan(parsed);
            const cachedWeekMetadata = getFromStorage(StorageKeys.WORKOUT_WEEK_METADATA, null);
            setPlan(normalizedPlan);
            setWeekMetadata(buildWeekMetadataFromPlan(normalizedPlan, cachedWeekMetadata));
          }
        }
      } catch (err) {
        console.error('Failed to fetch data:', err);
        setError('Failed to load workout plan. Using fallback.');
        const fallback = createFallbackPlan();
        const normalizedFallback = normalizeWeeklyPlan(fallback);
        const fallbackMetadata = buildWeekMetadataFromPlan(normalizedFallback, weekMetadata);
        setPlan(normalizedFallback);
        setWeekMetadata(fallbackMetadata);
        setToStorage(StorageKeys.WORKOUT_WEEK_METADATA, fallbackMetadata);
      } finally {
        setLoading(false);
      }
    };
    
    const fetchHistory = async () => {
      try {
        const historyResponse = await getWorkoutHistory();
        const history = historyResponse.data || [];
        setPastWorkouts(history);

        // ✅ FIX: Derive which day indices were completed TODAY from the backend.
        const todayStr = getLocalDateStr(); // YYYY-MM-DD in local time
        const dayNameToIndex = { Monday: 0, Tuesday: 1, Wednesday: 2, Thursday: 3, Friday: 4, Saturday: 5, Sunday: 6 };
        const todayCompleted = new Set();

        (Array.isArray(history) ? history : []).forEach((entry) => {
          const rawEntryDate = entry?.date || entry?.timestamp || entry?.completedAt;
          const entryDateStr =
            entry?.dateStr ||
            (typeof rawEntryDate === 'string'
              ? rawEntryDate.slice(0, 10)
              : '');

          if (entryDateStr !== todayStr) return;

          // ✅ FIX: Hydrate per-exercise skip/complete status from backend on re-login.
          // The backend now stores exercise_status_by_name and per-exercise status in the exercises array.
          const statusByName = entry?.exercise_status_by_name;
          const exercisesWithStatus = Array.isArray(entry?.exercises) ? entry.exercises : [];

          if (statusByName || exercisesWithStatus.some(e => e?.status)) {
            // Re-build exerciseStatus keyed by exercise status key (name|sets|reps|warmup)
            // We match by name since the full key isn't stored — close enough for display.
            const restoredStatus = {};
            exercisesWithStatus.forEach((ex) => {
              if (!ex?.name) return;
              const st = (statusByName?.[ex.name]) || ex?.status;
              if (st && st !== 'pending') {
                // Store under name as a simplified key (the status key formula needs sets/reps too,
                // but we fall back to a name-based match for display purposes)
                restoredStatus[`__byname__${ex.name}`] = st;
              }
            });
            if (Object.keys(restoredStatus).length > 0) {
              setExerciseStatus((prev) => ({ ...prev, ...restoredStatus }));
              // Also update localStorage cache
              try {
                const merged = { ...restoredStatus };
                localStorage.setItem('_exerciseStatus', JSON.stringify(merged));
                localStorage.setItem('_exerciseStatusDay', entry.dayName || '');
                localStorage.setItem('_exerciseStatusDate', todayStr);
              } catch(e) { console.warn('LocalStorage error', e); }
              console.log('✅ Hydrated exerciseStatus from backend:', Object.keys(restoredStatus).length, 'exercises');
            }
          }

          // Fully completed days (not partial) add to completedDayIndices
          if (entry?.status !== 'partial' && entry?.status !== 'Partial') {
            const dayIdx = dayNameToIndex[entry?.dayName];
            if (typeof dayIdx === 'number') {
              todayCompleted.add(dayIdx);
            }
          }
        });

        if (todayCompleted.size > 0) {
          setCompletedDayIndices(todayCompleted);
          console.log('✅ Hydrated completedDayIndices from backend:', [...todayCompleted]);
        }
      } catch (err) {
        console.error('Failed to fetch workout history:', err);
      }
    };

    checkAndFetchPlan();
    fetchHistory();
    
    // Cleanup function to prevent state updates on unmount
    return () => {
      isMounted = false;
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []); // Empty dependency - runs once on mount

  const playTimerBeep = useCallback(() => {
    try {
      const AudioContext = window.AudioContext || window.webkitAudioContext;
      if (!AudioContext) return;
      const ctx = new AudioContext();
      const osc = ctx.createOscillator();
      const gain = ctx.createGain();
      osc.type = 'sine';
      osc.frequency.setValueAtTime(800, ctx.currentTime);
      gain.gain.setValueAtTime(0.1, ctx.currentTime);
      gain.gain.exponentialRampToValueAtTime(0.01, ctx.currentTime + 0.5);
      osc.connect(gain);
      gain.connect(ctx.destination);
      osc.start();
      osc.stop(ctx.currentTime + 0.5);
    } catch (e) {
      console.warn('Audio playback failed', e);
    }
  }, []);

  useEffect(() => {
    let timer;
    if (isResting && restEndTime > 0) {
      timer = setInterval(() => {
        const remaining = Math.ceil((restEndTime - Date.now()) / 1000);
        if (remaining > 0) {
          setRestTimeLeft(remaining);
        } else {
          setRestTimeLeft(0);
          setIsResting(false);
          setCurrentSet((prev) => prev + 1);
          setCurrentReps(0);
          playTimerBeep();
          if (activeExercise && isTimedExercise(activeExercise)) {
            const duration = getExerciseDurationSeconds(activeExercise) || 300;
            setExerciseTimeLeft(duration);
            setExerciseEndTime(Date.now() + duration * 1000);
          }
        }
      }, 500);
    }
    return () => clearInterval(timer);
  }, [isResting, restEndTime, activeExercise, getExerciseDurationSeconds, isTimedExercise, playTimerBeep]);

  useEffect(() => {
    if (
      !isCameraOn ||
      isResting ||
      isDoneSession ||
      !activeExercise ||
      !exerciseNeedsCamera(activeExercise) ||
      !isTimedExercise(activeExercise)
    ) {
      return undefined;
    }

    if (exerciseEndTime > 0) {
      const timer = setInterval(() => {
        const remaining = Math.max(0, Math.ceil((exerciseEndTime - Date.now()) / 1000));
        setExerciseTimeLeft(remaining);
        if (remaining === 0) {
          clearInterval(timer);
          playTimerBeep();
          const targetSets = getTargetSets(activeExercise);
          setCompletedSetsMap(prev => ({...prev, [activeExercise.name]: currentSet}));
          if (currentSet >= targetSets) {
            handleExerciseCompleteRef.current?.();
          } else {
            const rDuration = getRestSeconds(activeExercise);
            setRestTimeLeft(rDuration);
            setRestEndTime(Date.now() + rDuration * 1000);
            setIsResting(true);
          }
        }
      }, 500);
      return () => clearInterval(timer);
    }

    return undefined;
  }, [
    isCameraOn,
    isResting,
    isDoneSession,
    activeExercise,
    exerciseEndTime,
    currentSet,
    exerciseNeedsCamera,
    isTimedExercise,
    playTimerBeep,
  ]);

  // Add voice coaching for form feedback
  useEffect(() => {
    if (formFeedback) {
      if (typeof window !== 'undefined' && window.speechSynthesis) {
        // Cancel any ongoing speech to avoid queueing up old feedback
        window.speechSynthesis.cancel();
        const msg = new SpeechSynthesisUtterance(formFeedback);
        msg.rate = 1.1; // Slightly faster for workout pacing
        msg.pitch = 1.0;
        window.speechSynthesis.speak(msg);
      }
      
      // Auto-clear feedback after 3.5 seconds to prevent it from getting stuck
      const timer = setTimeout(() => setFormFeedback(null), 3500);
      return () => clearTimeout(timer);
    }
  }, [formFeedback]);

  const toDayIndex = useCallback((value, fallback = 0) => {
    const parsed = Number(value);
    if (Number.isInteger(parsed) && parsed >= 0 && parsed <= 6) {
      return parsed;
    }
    return fallback;
  }, []);

  const normalizeWeeklyPlan = useCallback((rawPlan = []) => {
    const days = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'];

    // Create a map from the backend response
    const indexed = new Map(
      (Array.isArray(rawPlan) ? rawPlan : []).map((d) => {
        const idx = toDayIndex(d.day_of_week, 0);
        const normalizedType = d.type || (isRestDay(d) ? 'rest' : 'workout');
        const normalizedExercises = Array.isArray(d.exercises) ? d.exercises : [];
        return [idx, { 
          ...d,
          day_of_week: idx,
          day: d.day || days[idx],
          type: normalizedType,
          exercises: normalizedExercises,
          is_placeholder: Boolean(d.is_placeholder),
          can_access: d.can_access !== false,
          is_original_rest: typeof d.is_original_rest === 'boolean' ? d.is_original_rest : normalizedType === 'rest',
          is_original_workout: typeof d.is_original_workout === 'boolean' ? d.is_original_workout : normalizedType === 'workout',
          is_swapped: Boolean(d.is_swapped),
          swapped_from: d.swapped_from ?? null,
          swapped_to: d.swapped_to ?? null,
          is_swappable: typeof d.is_swappable === 'boolean' ? d.is_swappable : !d.is_swapped,
          is_completed: Boolean(d.is_completed),
          exercises_completed: Number(d.exercises_completed || 0),
          exercises_total: Number(d.exercises_total || normalizedExercises.length || 0),
        }];
      })
    );

    // Map all 7 days, filling missing ones with placeholders
    return days.map((label, idx) =>
      indexed.get(idx) || {
        day_of_week: idx,
        day: label,
        focus: 'No Plan',
        note: 'Not scheduled',
        exercises: [],
        is_placeholder: true,
        can_access: false,
        type: 'unplanned',
        is_original_rest: false,
        is_original_workout: false,
        is_swapped: false,
        swapped_from: null,
        swapped_to: null,
        is_swappable: false,
        is_completed: false,
        exercises_completed: 0,
        exercises_total: 0,
      }
    );
  }, [toDayIndex]);

  const safePlan = Array.isArray(plan) ? plan : [];
  const todayIdx = getTodayIdx();

  // displayPlan is just the plan - backend handles swapping now
  const displayPlan = safePlan;
  const planByDayIndex = useMemo(
    () => new Map(displayPlan.map((day, idx) => [toDayIndex(day?.day_of_week, idx), day])),
    [displayPlan, toDayIndex]
  );
  const sortedDisplayPlan = [...displayPlan].sort(
    (a, b) => toDayIndex(a?.day_of_week, 0) - toDayIndex(b?.day_of_week, 0)
  );

  // ✅ FIX: Use state-based completedDayIndices (hydrated from backend on mount) instead of
  // reading volatile localStorage keys on every render.  Falls back to localStorage keys + plan
  // is_completed flags for the first render before the backend response arrives.
  const completedIds = (() => {
    const ids = new Set(completedDayIndices);
    // Also read is_completed from the plan itself (set when session finishes or loaded from cache)
    displayPlan.forEach((d, idx) => {
      if (d.is_completed) ids.add(d.day_of_week ?? idx);
      // Legacy localStorage fallback (keeps backward compat until history fetch completes)
      const key = `workout_done_${d.day || `Day ${idx + 1}`}`;
      if (getFromStorage(key) === 'true') ids.add(d.day_of_week ?? idx);
    });
    return ids;
  })();

  const swapHistory = Array.isArray(weekMetadata?.swap_history) ? weekMetadata.swap_history : [];
  const swapLimits = {
    max: Number(weekMetadata?.swap_limits?.max_swaps_per_week || 3),
    used: Number(weekMetadata?.swap_limits?.swaps_used || swapHistory.length || 0),
    remaining: Number(
      weekMetadata?.swap_limits?.swaps_remaining
      ?? Math.max(0, Number(weekMetadata?.swap_limits?.max_swaps_per_week || 3) - (swapHistory.length || 0))
    ),
  };

  const handleRestDayDecision = useCallback(async () => {
    const today = planByDayIndex.get(todayIdx);
    if (!today || !isRestDay(today)) return;

    showConfirmDialog(
      'Today is a rest day. Do you want to take rest today?\n\n• Click "Confirm" to rest\n• Click "Cancel" to workout instead',
      async (confirmed) => {
        // User clicked cancel/close - do nothing
        if (confirmed === null || confirmed === undefined) {
          return;
        }

        if (confirmed === true) {
          // User wants to rest - keep the plan as is
          showSuccess('Rest day kept as planned. Enjoy your recovery!', 2500);
          return;
        }

        // User clicked "Cancel" - wants to workout, swap rest day with next workout day
        const nextWorkoutIdx = findNextWorkoutDayIndex(displayPlan, todayIdx);
        if (nextWorkoutIdx == null) {
          showError('No upcoming workout day found to swap with.', 3000);
          return;
        }

        try {
          // Check if user is logged in
          const token = localStorage.getItem('token');
          if (!token) {
            showError('Please log in to swap rest days.', 3000);
            navigate('/login');
            return;
          }
          
          // Get user email - try localStorage first, then fetch from API if needed
          let email = '';
          
          const storedUser = getFromStorage('user', {});
          email = storedUser.email || '';
          
          // If email not found in localStorage, try fetching from API
          if (!email) {
            try {
              console.log('📧 Email not in localStorage, fetching from API...');
              const profileRes = await getProfile();
              email = profileRes.data?.email || '';
              console.log('📧 Email from API:', email);
            } catch (err) {
              console.error('Failed to fetch profile:', err);
            }
          } else {
            console.log('📧 Email from localStorage:', email);
          }
          
          if (!email) {
            showError('Unable to get user email. Please try logging in again.', 4000);
            console.error('❌ Email not found. User may need to re-login.');
            return;
          }

          showSuccess('Swapping rest day...', 1500);
          
          const response = await swapRestToWorkout({
            email: email,
            rest_day_index: todayIdx,
            current_day_index: todayIdx,
            current_plan: displayPlan
          });

          if (response.data && response.data.success) {
            // Update the workout plan with the swapped version from backend
            const swappedPlan = normalizeWeeklyPlan(response.data.workout);
            const updatedWeekMetadata = buildWeekMetadataFromPlan(
              swappedPlan,
              response.data?.week_metadata || response.data?.data?.week_metadata || weekMetadata
            );
            setPlan(swappedPlan);
            setWeekMetadata(updatedWeekMetadata);
            
            // Save to storage
            setToStorage('workoutPlan', swappedPlan);
            setToStorage('workoutPlanTimestamp', new Date().toISOString());
            setToStorage(StorageKeys.WORKOUT_WEEK_METADATA, updatedWeekMetadata);
            
            // DON'T save a decision - the plan is already swapped from backend
            // The displayPlan local swap logic should NOT apply here
            
            showSuccess(
              `Workout moved to today! ${weekdayNames[nextWorkoutIdx]} is now your rest day.`,
              3500
            );
          } else {
            const errorMsg = response.data?.message || 'Failed to swap rest day';
            showError(errorMsg + '. Please try again.', 4000);
          }
        } catch (error) {
          console.error('Error swapping rest day:', error);
          let errorMessage = 'Failed to swap rest day. ';
          
          if (error.response) {
            // Server responded with error
            errorMessage += error.response.data?.detail || error.response.data?.message || `Server error: ${error.response.status}`;
          } else if (error.request) {
            // Request made but no response
            errorMessage += 'No response from server. Check your connection.';
          } else {
            // Error setting up request
            errorMessage += error.message || 'Unknown error occurred.';
          }
          
          showError(errorMessage, 5000);
        }
      }
    );
  }, [
    planByDayIndex,
    todayIdx,
    showConfirmDialog,
    showSuccess,
    displayPlan,
    showError,
    navigate,
    normalizeWeeklyPlan,
    weekMetadata,
  ]);

  const getSwapEmail = async () => {
    const storedUser = getFromStorage('user', {});
    if (storedUser?.email) {
      return storedUser.email;
    }
    try {
      const profileRes = await getProfile();
      return profileRes?.data?.email || '';
    } catch {
      return '';
    }
  };

  const canSwapWorkoutToRest = (dayIdx) => {
    const day = planByDayIndex.get(dayIdx);
    if (!day || isRestDay(day)) return false;
    if (day.is_placeholder) return false;
    if (dayIdx < todayIdx) return false;
    if (day.is_original_workout === false) return false;
    if (day.is_swapped) return false;
    if (day.is_swappable === false) return false;
    if (day.is_completed || completedIds.has(dayIdx) || Number(day.exercises_completed || 0) > 0) return false;
    const futureRestDays = getFutureOriginalRestDays(displayPlan, dayIdx, todayIdx);
    return futureRestDays.length > 0;
  };

  const openWorkoutToRestModal = (dayIdx) => {
    const available = getFutureOriginalRestDays(displayPlan, dayIdx, todayIdx);
    if (available.length === 0) {
      showError('No future original rest day available for this swap.', 3000);
      return;
    }

    setSwapWorkoutDayIndex(dayIdx);
    setSelectedTargetRestDayIndex(available[0]?.day_of_week ?? null);
    setShowWorkoutToRestModal(true);
  };

  const handleConfirmWorkoutToRestSwap = async () => {
    if (swapWorkoutDayIndex == null || selectedTargetRestDayIndex == null) {
      showError('Please select a target rest day first.', 2500);
      return;
    }

    try {
      const token = localStorage.getItem('token');
      if (!token) {
        showError('Please log in to swap workout days.', 3000);
        navigate('/login');
        return;
      }

      const email = await getSwapEmail();
      if (!email) {
        showError('Unable to get user email. Please log in again.', 3500);
        return;
      }

      const response = await swapWorkoutToRest({
        email,
        workout_day_index: swapWorkoutDayIndex,
        target_rest_day_index: selectedTargetRestDayIndex,
        current_day_index: todayIdx,
        current_plan: displayPlan,
      });

      if (response.data?.success) {
        const swappedPlan = normalizeWeeklyPlan(response.data.workout);
        const updatedWeekMetadata = buildWeekMetadataFromPlan(
          swappedPlan,
          response.data?.week_metadata || response.data?.data?.week_metadata || weekMetadata
        );
        setPlan(swappedPlan);
        setWeekMetadata(updatedWeekMetadata);
        setToStorage('workoutPlan', swappedPlan);
        setToStorage('workoutPlanTimestamp', new Date().toISOString());
        setToStorage(StorageKeys.WORKOUT_WEEK_METADATA, updatedWeekMetadata);

        const targetDayLabel = weekdayNames[selectedTargetRestDayIndex] || `Day ${selectedTargetRestDayIndex + 1}`;
        showSuccess(`Workout moved successfully. Your workout is now on ${targetDayLabel}.`, 3500);
        setShowWorkoutToRestModal(false);
        setSwapWorkoutDayIndex(null);
        setSelectedTargetRestDayIndex(null);
      } else {
        showError(response.data?.message || 'Failed to move workout day.', 3500);
      }
    } catch (error) {
      const backendDetail = error?.response?.data?.detail;
      const backendMessage = typeof backendDetail === 'string'
        ? backendDetail
        : (backendDetail?.error || backendDetail?.message);
      showError(backendMessage || 'Failed to move workout day.', 4000);
    }
  };

  const handleDayClick = useCallback((dayIdx) => {
    const normalizedDayIdx = toDayIndex(dayIdx, -1);
    if (normalizedDayIdx < 0) return;

    const day = planByDayIndex.get(normalizedDayIdx) ?? displayPlan[normalizedDayIdx];
    if (!day) return;

    if (normalizedDayIdx === todayIdx && isRestDay(day)) {
      handleRestDayDecision();
      return;
    }

    if (!isRestDay(day)) {
      setActiveDay(day);
      setActiveExercise(null);
      setCurrentSet(1);
      setCurrentReps(0);
      setIsResting(false);
      setFormFeedback(null);
      setExerciseTimeLeft(0);
      setExerciseEndTime(0);
      setCompletedExercisesCount(0);
      setSkippedExercises(new Set());
      setExerciseStatus({});
    }
  }, [toDayIndex, planByDayIndex, displayPlan, todayIdx, handleRestDayDecision]);

  useEffect(() => {
    if (autoStartHandledRef.current) return;
    if (autoStartDay === undefined || autoStartDay === null) return;
    if (!displayPlan.length) return;

    const normalizedDay = toDayIndex(autoStartDay, -1);
    if (normalizedDay < 0) return;

    const day = planByDayIndex.get(normalizedDay) ?? displayPlan[normalizedDay];
    if (!day) return;
    if (day.is_placeholder || day.type === 'past' || isRestDay(day)) return;

    const timer = setTimeout(() => {
      handleDayClick(normalizedDay);
      autoStartHandledRef.current = true;
    }, 350);

    return () => clearTimeout(timer);
  }, [autoStartDay, displayPlan, planByDayIndex, handleDayClick, toDayIndex]);

  const releaseCameraStream = () => {
    if (!stream) return;
    stream.getTracks().forEach((track) => track.stop());
    setStream(null);
  };

  const ensureCameraStream = async () => {
    if (stream) return stream;
    try {
      const mediaStream = await navigator.mediaDevices.getUserMedia({
        video: { width: 640, height: 480, frameRate: { ideal: 30, max: 30 } },
      });
      setStream(mediaStream);
      return mediaStream;
    } catch {
      showError('Camera permission denied. Please allow camera access.', 5000);
      return null;
    }
  };

  const emitWorkoutProgress = (completedCount, totalCount, fullyDone = false) => {
    const payload = {
      completedCount,
      totalCount,
      dayId: activeDay?.day,
      ts: Date.now(),
      fullyDone,
    };
    setToStorage('_workoutSync', JSON.stringify(payload));
    syncBridge.emit(fullyDone ? SyncTypes.WORKOUT_COMPLETED : SyncTypes.WORKOUT_PROGRESS, payload);
  };

  const startCamera = async () => {
    if (!activeExercise) {
      showError('Select an exercise first.', 2500);
      return;
    }

    setIsCameraOn(true);
    setCurrentSet(1);
    setCurrentReps(0);
    setIsResting(false);
    setFormFeedback(null);
    setIsDoneSession(false);
    if (isTimedExercise(activeExercise)) {
      const duration = getExerciseDurationSeconds(activeExercise) || 300;
      setExerciseTimeLeft(duration);
      setExerciseEndTime(Date.now() + duration * 1000);
    } else {
      setExerciseTimeLeft(0);
      setExerciseEndTime(0);
    }

    if (!exerciseNeedsCamera(activeExercise)) {
      releaseCameraStream();
      return;
    }

    const mediaStream = await ensureCameraStream();
    if (!mediaStream) {
      setIsCameraOn(false);
    }
  };

  const stopCamera = () => {
    releaseCameraStream();
    setIsCameraOn(false);
    setExerciseTimeLeft(0);
  };

  const handleExerciseSelect = (ex) => {
    if (isCameraOn) return;
    setActiveExercise(ex);
    setCurrentSet(1);
    setCurrentReps(0);
    setIsResting(false);
    setFormFeedback(null);
    setIsDoneSession(false);
    if (isTimedExercise(ex)) {
      const duration = getExerciseDurationSeconds(ex) || 300;
      setExerciseTimeLeft(duration);
      setExerciseEndTime(Date.now() + duration * 1000);
    } else {
      setExerciseTimeLeft(0);
      setExerciseEndTime(0);
    }
  };

  const moveToExercise = async (nextExercise) => {
    if (!nextExercise) return;
    setActiveExercise(nextExercise);
    setCurrentSet(1);
    setCurrentReps(0);
    setIsResting(false);
    setFormFeedback(null);
    setIsDoneSession(false);
    if (isTimedExercise(nextExercise)) {
      const duration = getExerciseDurationSeconds(nextExercise) || 300;
      setExerciseTimeLeft(duration);
      setExerciseEndTime(Date.now() + duration * 1000);
    } else {
      setExerciseTimeLeft(0);
      setExerciseEndTime(0);
    }

    if (!isCameraOn) return;

    if (!exerciseNeedsCamera(nextExercise)) {
      releaseCameraStream();
      return;
    }

    const mediaStream = await ensureCameraStream();
    if (!mediaStream) {
      stopCamera();
    }
  };

  const handleExerciseComplete = async () => {
    if (!activeExercise || !activeDay?.exercises) return;

    const totalCount = activeDay.exercises.length;
    const statusKey = getExerciseStatusKey(activeExercise);
    const nextStatus = { ...exerciseStatus, [statusKey]: 'completed' };
    setExerciseStatus(nextStatus);

    const completedCount = Object.values(nextStatus).filter((s) => s === 'completed').length;
    setCompletedExercisesCount(completedCount);
    emitWorkoutProgress(completedCount, totalCount, false);

    showSuccess(`Completed ${activeExercise.name}!`, 3000);

    const currentIndex = activeDay.exercises.findIndex((e) =>
      e === activeExercise ||
      (e?.name === activeExercise?.name && e?.sets === activeExercise?.sets && e?.reps === activeExercise?.reps)
    );

    if (currentIndex >= 0 && currentIndex < totalCount - 1) {
      const nextEx = activeDay.exercises[currentIndex + 1];
      await moveToExercise(nextEx);
      return;
    }

    setIsDoneSession(true);
    setExerciseTimeLeft(0);
    setExerciseEndTime(0);

    const isPartialSession = skippedExercises.size > 0;
    const statusPayload = {
      isPartialSession,
      options: {
        exerciseStatus: nextStatus,
        skippedExercises,
      }
    };

    // Priority 1: Send exercise result to Python backend for variation suggestion.
    if (activeExercise?.name) {
      const totalCount = activeDay?.exercises?.length || 1;
      const completedSoFar = Object.values({ ...exerciseStatus, [getExerciseStatusKey(activeExercise)]: 'completed' }).filter(s => s === 'completed').length;
      const impliedScore = Math.min(1, completedSoFar / Math.max(totalCount, 1));
      
      // Stop the camera stream first
      releaseCameraStream();
      setIsCameraOn(false);

      // Set loading state
      setVariationResult({
        loading: true,
        exercise: activeExercise.name,
        statusPayload,
      });

      postSessionResult({
        exercise_name: activeExercise.name,
        form_score: impliedScore,
        rep_count: currentReps,
      }).then(res => {
        const data = res?.data || {};
        setVariationResult({
          loading: false,
          exercise: activeExercise.name,
          formScore: data.form_score ?? impliedScore,
          suggestion: data.variation_suggestion,
          coaching: data.coaching_feedback,
          statusPayload,
        });
      }).catch(async () => {
        // Fallback: silently finish if API fails so the user doesn't get stuck
        setVariationResult(null);
        await finishSession(isPartialSession, statusPayload.options);
      });
    } else {
      await finishSession(isPartialSession, statusPayload.options);
    }
  };

  handleExerciseCompleteRef.current = handleExerciseComplete;

  const handleExerciseSkipped = async (exercise = activeExercise) => {
    if (!exercise || !activeDay?.exercises) return;

    const totalCount = activeDay.exercises.length;
    const statusKey = getExerciseStatusKey(exercise);
    const nextStatus = { ...exerciseStatus, [statusKey]: 'skipped' };
    const nextSkipped = new Set(skippedExercises);
    if (exercise.name) {
      nextSkipped.add(exercise.name);
    }

    setExerciseStatus(nextStatus);
    setSkippedExercises(nextSkipped);

    const completedCount = Object.values(nextStatus).filter((s) => s === 'completed').length;
    setCompletedExercisesCount(completedCount);
    emitWorkoutProgress(completedCount, totalCount, false);

    showError(`Skipped: ${exercise.name}`, 2000);

    const todayStr = getLocalDateStr();
    saveTrends({
      date: todayStr,
      workout_partial: true,
      skipped_exercises: Array.from(nextSkipped),
    }).catch((error) => console.error('Failed to sync skip status:', error));

    const currentIndex = activeDay.exercises.findIndex((e) =>
      e === exercise ||
      (e?.name === exercise?.name && e?.sets === exercise?.sets && e?.reps === exercise?.reps)
    );

    if (currentIndex >= 0 && currentIndex < totalCount - 1) {
      const nextEx = activeDay.exercises[currentIndex + 1];
      await moveToExercise(nextEx);
      return;
    }

    setIsDoneSession(true);
    setExerciseTimeLeft(0);
    setExerciseEndTime(0);
    await finishSession(true, {
      exerciseStatus: nextStatus,
      skippedExercises: nextSkipped,
    });
  };

  const handleRepUpdate = (repsCount) => {
    if (isResting || isDoneSession || !activeExercise || !isPoseTrackableExercise(activeExercise)) return;
    
    setCurrentReps(repsCount);

    const targetReps = getTargetReps(activeExercise);
    const targetSets = getTargetSets(activeExercise);

    if (repsCount >= targetReps) {
      setCompletedSetsMap(prev => ({...prev, [activeExercise.name]: currentSet}));
      if (currentSet >= targetSets) {
         handleExerciseComplete();
      } else {
         const duration = getRestSeconds(activeExercise);
         setRestTimeLeft(duration);
         setRestEndTime(Date.now() + duration * 1000);
         setIsResting(true);
      }
    }
  };

  const finishSession = async (isPartial = false, snapshot = null) => {
    stopCamera();
    if (activeDay) {
      const statusSnapshot = snapshot?.exerciseStatus || exerciseStatus;
      const skippedSnapshot = snapshot?.skippedExercises || skippedExercises;
      const skippedNames = Array.from(skippedSnapshot);
      const totalCount = activeDay.exercises?.length || 0;
      const completedExercises = (activeDay.exercises || []).filter(
        (exercise) => statusSnapshot[getExerciseStatusKey(exercise)] === 'completed'
      );
      const isPartialSession = isPartial || skippedNames.length > 0;

      try {
        const detail = isPartialSession
          ? `Partial session: ${completedExercises.length}/${totalCount} exercises completed, ${skippedNames.length} skipped`
          : 'Completed session';
        await saveLog(activeDay.focus || 'Workout', detail, activeDay.day || '');
      } catch (err) {
        console.error("Workout history save failed:", err);
      }

      // ✅ FIX: Persist exerciseStatus to localStorage so red/green ticks survive a browser refresh.
      // Key is scoped to today's date + day name to avoid stale data bleeding into other days.
      const todayStatusKey = `_exerciseStatus_${getLocalDateStr()}_${activeDay.day}`;
      try {
        localStorage.setItem('_exerciseStatus', JSON.stringify(statusSnapshot));
        localStorage.setItem('_exerciseStatusKey', todayStatusKey);
        localStorage.setItem('_exerciseStatusDay', activeDay.day);
        localStorage.setItem('_exerciseStatusDate', getLocalDateStr());
      } catch (e) { console.warn('LocalStorage quota exceeded', e); }

      if (isPartialSession) {
        setToStorage(`workout_partial_${activeDay.day}`, 'true');
        setToStorage(`workout_skipped_${activeDay.day}`, JSON.stringify(skippedNames));
        setToStorage(StorageKeys.TODAY_WORKOUT_DONE, 'false');
      } else {
        setToStorage(`workout_done_${activeDay.day}`, 'true');
        setToStorage(StorageKeys.TODAY_WORKOUT_DONE, 'true');
        // Clear partial status cache since session is now fully done
        try { localStorage.removeItem('_exerciseStatus'); } catch(e) { console.warn('LocalStorage error', e); }

        // ✅ FIX: Update completedDayIndices React state so the UI reflects completion immediately.
        const completedDayIdx = activeDay.day_of_week ?? -1;
        if (completedDayIdx >= 0) {
          setCompletedDayIndices((prev) => new Set([...prev, completedDayIdx]));
        }

        // ✅ FIX: Mark is_completed:true on plan state + localStorage cache so it survives refresh.
        setPlan((prevPlan) => {
          const updatedPlan = prevPlan.map((d) =>
            d.day_of_week === completedDayIdx ? { ...d, is_completed: true } : d
          );
          // Persist the updated completion flag to cache
          setToStorage('workoutPlan', updatedPlan);
          return updatedPlan;
        });
      }
      
      try {
        // ✅ FIX: Persist exercise_status so skipped/completed ticks are restored on re-login.
        // Build a name-keyed map (readable) alongside the raw status key map.
        const exerciseStatusByName = {};
        (activeDay.exercises || []).forEach((ex) => {
          const key = getExerciseStatusKey(ex);
          if (statusSnapshot[key]) {
            exerciseStatusByName[ex.name] = statusSnapshot[key];
          }
        });
        await saveUserWorkoutToNode({
           dayName: activeDay.day,
           dateStr: getLocalDateStr(),
           focus: activeDay.focus,
           exercises: activeDay.exercises.map(ex => ({
             name: ex.name,
             duration: ex.duration || "Custom",
             status: statusSnapshot[getExerciseStatusKey(ex)] || 'pending',
           })),
           exercise_status_by_name: exerciseStatusByName,
           completedAt: new Date().toISOString(),
           status: isPartialSession ? 'partial' : 'completed',
           completed_exercises: completedExercises.length,
           skipped_exercises: skippedNames,
        });
        console.log("Workout saved to Node backend successfully.");
      } catch (err) {
        console.error("Failed to save workout to Node backend:", err);
      }

      // ✅ FIX: Sync workout_completed to backend trends so Dashboard streak works
      try {
        const todayStr = getLocalDateStr();
        await saveTrends({
          date: todayStr,
          workout_completed: !isPartialSession,
          workout_partial: isPartialSession,
          skipped_exercises: skippedNames,
        });
        console.log("Workout trends synced to backend.");
      } catch (err) {
        console.error("Failed to sync workout trends:", err);
      }

      emitWorkoutProgress(
        isPartialSession ? completedExercises.length : totalCount,
        totalCount,
        !isPartialSession
      );

      if (!isPartialSession) {
        syncBridge.emit(SyncTypes.WORKOUT_COMPLETED, {
          dayId: activeDay.day,
          completedCount: totalCount,
          totalCount,
        });
      }

      showSuccess(
        isPartialSession ? 'Workout saved as partial session.' : 'Great job! Workout Logged.',
        3000
      );
      setActiveDay(null);
      setActiveExercise(null);
      setSkippedExercises(new Set());
      setExerciseStatus({});
      setCompletedExercisesCount(0);
    }
  };

  const handleLogout = () => {
    showConfirmDialog("Log out of Elevate?", (confirmed) => {
      if (confirmed) {
        logoutSafe();
        navigate('/');
      }
    });
  };

  const activeExerciseNeedsCamera = !!activeExercise && exerciseNeedsCamera(activeExercise);
  const activeExercisePoseTrackable = !!activeExercise && activeExerciseNeedsCamera && isPoseTrackableExercise(activeExercise);
  const activeExerciseTimed = !!activeExercise && isTimedExercise(activeExercise);
  const activeExerciseTargetSets = activeExercise ? getTargetSets(activeExercise) : 1;
  const activeExerciseDuration = activeExercise
    ? (getExerciseDurationSeconds(activeExercise) || (activeExerciseTimed ? 300 : 0))
    : 0;

  return (
    <>
      <div style={styles.page}>
        {/* ✨ Aurora Mesh Gradient background — replaces bubble animation */}
        <AuroraBackground />
        <style>{`
          /* ── Base animations (session panels etc.) ── */
          @keyframes slideDown { from { opacity: 0; transform: translateY(-20px); } to { opacity: 1; transform: translateY(0); } }
          @keyframes fadeIn { from { opacity: 0; } to { opacity: 1; } }
          @keyframes slideInRight { from { transform: translateX(100%); } to { transform: translateX(0); } }

          /* ── Card hover lift ── */
          .plan-card { transition: transform 0.22s ease, box-shadow 0.22s ease, border-color 0.22s ease; }
          .plan-card:hover { transform: translateY(-5px) !important; box-shadow: 0 16px 40px rgba(0,0,0,0.22) !important; border-color: rgba(99,102,241,0.28) !important; }

          /* ── Nav & Icon hovers ── */
          .icon-hover:hover { background: var(--app-border) !important; transform: scale(1.08); }
          .logout-btn:hover { background: rgba(239, 68, 68, 0.2) !important; transform: translateY(-2px); box-shadow: 0 4px 15px rgba(239, 68, 68, 0.2); }

          /* ── Active card pulse ── */
          .active-card-pulse { animation: pulseBorder 2s infinite; }
          @keyframes pulseBorder { 0% { border-color: #6366f1; box-shadow: 0 0 0 0 rgba(99, 102, 241, 0.4); } 70% { border-color: #818cf8; box-shadow: 0 0 0 10px rgba(99, 102, 241, 0); } 100% { border-color: #6366f1; box-shadow: 0 0 0 0 rgba(99, 102, 241, 0); } }

          /* ── Exercise list item hover ── */
          .ex-item { transition: transform 0.18s ease, background 0.18s ease; }
          .ex-item:hover { transform: translateX(5px); background: rgba(255,255,255,0.06) !important; }

          /* ── Session buttons ── */
          .btn-stop:hover { background: rgba(239, 68, 68, 0.2) !important; transform: scale(1.03); }
          .btn-done:hover { transform: translateY(-2px); box-shadow: 0 8px 25px rgba(34, 197, 94, 0.5) !important; }

          /* ── History cards ── */
          .history-card { transition: border-color 0.2s, background 0.2s, transform 0.2s; }
          .history-card:hover { border-color: #6366f1 !important; background: var(--app-border) !important; transform: translateX(4px); }
        `}</style>

        <Navbar 
          isDark={theme === 'dark'}
          navigate={navigate} 
          activePage="workout" 
          onLogout={handleLogout}
          rightContent={
            <>
              <div style={styles.dateDisplay} className="desktop-nav">{todayDate}</div>
              <button style={styles.iconButton} className="icon-hover" onClick={() => setShowHistory(!showHistory)} title="Past Workouts">🕒</button>
              <div style={{position:'relative'}} ref={notifRef}>
                <button style={styles.iconButton} className="icon-hover" onClick={() => setShowNotif(!showNotif)}>🔔</button>
                {showNotif && (
                  <div style={styles.notifDropdown}>
                    <div style={{fontSize:'14px', fontWeight:'700', color:'var(--app-text)', marginBottom:'12px'}}>Notifications</div>
                    <div style={styles.notifItem}>🔥 You're on a 12-day streak!</div>
                    <div style={styles.notifItem}>🦵 Leg Day today!</div>
                    <div style={{...styles.notifItem, borderBottom:'none', color:'var(--app-text-muted)', fontSize:'12px', justifyContent:'center', marginTop:'8px'}}>No new alerts</div>
                  </div>
                )}
              </div>
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

        {poseTrackingError && (
          <div style={{
            padding: '12px',
            background: 'rgba(245, 158, 11, 0.1)',
            border: '1px solid rgba(245, 158, 11, 0.3)',
            borderRadius: '8px',
            margin: '20px 40px',
            color: '#f59e0b',
            fontSize: '13px'
          }}>
            ⚠️ {poseTrackingError}
          </div>
        )}

        <div style={workoutLayout.container} className="workout-container-enter">
          {!activeDay && (
            <>
              <h1 style={workoutLayout.h1} className="workout-page-h1">Your Weekly Plan</h1>
              <div style={workoutLayout.grid}>
                {safePlan.length > 0 ? (
                  sortedDisplayPlan
                    .map((day, idx) => {
                      const dayIdx = toDayIndex(day.day_of_week, idx);
                      const isRest = isRestDay(day);
                      const isPlaceholder = !!day.is_placeholder;
                      const status = getDayStatus(day, todayIdx, completedIds);
                      const isToday = status === 'TODAY' || (status === 'REST' && dayIdx === todayIdx);
                      const dayExercises = day.exercises || []; // FIXED: Define here
                      const previewExercises = dayExercises.filter((ex) => !ex?.is_warmup);
                      const displayExercises = previewExercises.length > 0 ? previewExercises : dayExercises;

                      let cardStyle = {...workoutLayout.card};
                      if (status === 'TODAY') {
                        cardStyle = {...cardStyle, ...styles.cardActive};
                      } else if (status === 'COMPLETED') {
                        cardStyle = {...cardStyle, ...styles.cardDone};
                      } else if (status === 'NOT_STARTED') {
                        cardStyle = {
                          ...cardStyle,
                          border: '1px dashed rgba(161, 161, 170, 0.25)',
                          background: 'rgba(113, 113, 122, 0.05)',
                          opacity: 0.75,
                        };
                      } else if (status === 'PAST') {
                        cardStyle = {...cardStyle, ...styles.cardMissed};
                      } else if (isRest || isPlaceholder) {
                        cardStyle = {...cardStyle, border: '1px dashed rgba(255,255,255,0.2)', opacity: 0.7};
                      }

                      return (
                        <div 
                          key={`${dayIdx}-${day.day || idx}`}
                          className="plan-card"
                          style={cardStyle}
                          onClick={() => !isPlaceholder && isToday && handleDayClick(dayIdx)}
                        >
                          <div style={{display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '8px'}}>
                            <div>
                              <div style={styles.dayTitle}>
                                {weekdayNames[dayIdx] || `Day ${idx + 1}`}
                              </div>
                              <div style={styles.focusText}>
                                {day.focus || day.day || 'Workout'}
                              </div>
                            </div>
                            <div style={{
                              padding: '4px 10px',
                              borderRadius: '20px',
                              fontSize: '11px',
                              fontWeight: '700',
                              textTransform: 'uppercase',
                              background: status === 'TODAY' ? 'rgba(99, 102, 241, 0.2)' :
                                         status === 'COMPLETED' ? 'rgba(34, 197, 94, 0.2)' :
                                     status === 'NOT_STARTED' ? 'rgba(113, 113, 122, 0.2)' :
                                         status === 'PAST' ? 'rgba(239, 68, 68, 0.2)' :
                                         status === 'REST' ? 'rgba(245, 158, 11, 0.2)' :
                                         status === 'NO PLAN' ? 'rgba(113, 113, 122, 0.2)' :
                                         'rgba(161, 161, 170, 0.2)',
                              color: status === 'TODAY' ? '#a5b4fc' :
                                    status === 'COMPLETED' ? '#22c55e' :
                                status === 'NOT_STARTED' ? 'var(--app-text-muted)' :
                                    status === 'PAST' ? '#ef4444' :
                                    status === 'REST' ? '#f59e0b' :
                                    status === 'NO PLAN' ? 'var(--app-text-muted)' :
                                    'var(--app-text-muted)',
                              border: `1px solid ${status === 'TODAY' ? 'rgba(99, 102, 241, 0.3)' :
                                       status === 'COMPLETED' ? 'rgba(34, 197, 94, 0.3)' :
                                   status === 'NOT_STARTED' ? 'rgba(113, 113, 122, 0.3)' :
                                       status === 'PAST' ? 'rgba(239, 68, 68, 0.3)' :
                                       status === 'REST' ? 'rgba(245, 158, 11, 0.3)' :
                                       status === 'NO PLAN' ? 'rgba(113, 113, 122, 0.3)' :
                                       'rgba(161, 161, 170, 0.3)'}`
                            }}>
                              {status}
                            </div>
                          </div>

                          {isRest ? (
                            <div style={workoutLayout.restDay}>
                              😴 Rest Day - Recovery & Preparation
                              <div style={{ marginTop: '12px', fontSize: '11px', opacity: 0.9 }}>
                                {isToday ? 'Tap this card to choose: keep rest day or borrow next workout.' : 'No workout today. Focus on recovery, stretching, or light walking.'}
                              </div>
                            </div>
                          ) : status === 'NOT_STARTED' ? (
                            <div style={{
                              ...workoutLayout.restDay,
                              display: 'flex',
                              flexDirection: 'column',
                              alignItems: 'center',
                              justifyContent: 'center',
                              gap: '8px',
                              color: 'var(--app-text-muted)',
                            }}>
                              <div style={{ fontSize: '34px' }}>📅</div>
                              <div style={{ fontSize: '14px', fontWeight: '700' }}>Not Started Yet</div>
                              <div style={{ fontSize: '12px', opacity: 0.9 }}>Your journey begins today!</div>
                            </div>
                          ) : isPlaceholder ? (
                            <div style={workoutLayout.restDay}>
                              📅 No plan for this day
                              <div style={{ marginTop: '12px', fontSize: '11px', opacity: 0.9 }}>
                                Generate a new plan to fill this day.
                              </div>
                            </div>
                          ) : (
                            <>
                              {displayExercises.length > 0 && (
                                <div style={{flex:1, marginBottom:'12px'}}>
                                  {displayExercises.slice(0, 3).map((ex, i) => (
                                    <div key={i} style={styles.exPreview}>
                                      <span>• {ex.name}</span>
                                      <span>{ex.sets}x{ex.reps}</span>
                                    </div>
                                  ))}
                                  {displayExercises.length > 3 && (
                                    <div style={{...styles.exPreview, color:'var(--app-text-muted)', fontSize:'11px'}}>
                                      +{displayExercises.length - 3} more exercises
                                    </div>
                                  )}
                                </div>
                              )}
                              {isToday && (
                                <div style={{ marginTop: 'auto', display: 'grid', gap: '10px' }}>
                                  <button
                                    onClick={() => handleDayClick(dayIdx)}
                                    style={{
                                      width: '100%',
                                      padding: '12px',
                                      borderRadius: '12px',
                                      border: 'none',
                                      background: '#6366f1',
                                      color: 'white',
                                      fontWeight: '700',
                                      fontSize: '14px',
                                      cursor: 'pointer',
                                    }}
                                  >
                                    START WORKOUT
                                  </button>
                                  {canSwapWorkoutToRest(dayIdx) && (
                                    <button
                                      onClick={() => openWorkoutToRestModal(dayIdx)}
                                      style={{
                                        width: '100%',
                                        padding: '10px 12px',
                                        borderRadius: '10px',
                                        border: '1px solid rgba(245, 158, 11, 0.45)',
                                        background: 'rgba(245, 158, 11, 0.12)',
                                        color: '#f59e0b',
                                        fontWeight: '700',
                                        fontSize: '12px',
                                        cursor: 'pointer',
                                      }}
                                    >
                                      NEED REST TODAY?
                                    </button>
                                  )}
                                </div>
                              )}
                            </>
                          )}
                        </div>
                      );
                    })
                ) : (
                  <div style={{gridColumn: '1 / -1', textAlign: 'center', padding: '40px', color: 'var(--app-text-muted)', fontSize: '16px'}}>
                    No plan yet. Generate to see your week.
                  </div>
                )}
              </div>
            </>
          )}

          {activeDay && (
            <div style={workoutLayout.sessionContainer}>
              {!isCameraOn && (
                <>
                  <div style={workoutLayout.selectionList}>
                    <div style={styles.sidebarHeader}>
                      Today's Routine
                      <button
                        style={styles.backBtn}
                        onClick={() => {
                          setActiveDay(null);
                          setActiveExercise(null);
                          setSkippedExercises(new Set());
                          setExerciseStatus({});
                          setCompletedExercisesCount(0);
                        }}
                      >
                        Exit
                      </button>
                    </div>
                    {(() => {
                      const warmupExercises = Array.isArray(activeDay.warmup) && activeDay.warmup.length > 0
                        ? activeDay.warmup
                        : (activeDay.exercises || []).filter((exercise) => exercise?.is_warmup);
                      const mainExercises = (activeDay.exercises || []).filter((exercise) => !exercise?.is_warmup);

                      const renderExerciseItem = (exercise, index, isWarmupSection = false) => {
                        const key = getExerciseStatusKey(exercise);
                        // ✅ FIX: Also look up via __byname__ key for status hydrated from backend on re-login.
                        // Backend hydration uses name-based keys since the full key (name|sets|reps|warmup)
                        // isn't stored on the server. The full key takes precedence if present.
                        const bynameKey = `__byname__${exercise.name}`;
                        const status = exerciseStatus[key] || exerciseStatus[bynameKey] || 'pending';
                        const isSkipped = status === 'skipped';
                        const isCompleted = status === 'completed';
                        const isSelected = getExerciseStatusKey(activeExercise) === key;

                        return (
                          <div
                            key={`${key}-${index}`}
                            className="ex-item"
                            onClick={() => !isCompleted && !isSkipped && handleExerciseSelect(exercise)}
                            style={{
                              ...styles.exerciseItem,
                              ...(isSelected ? styles.exerciseItemActive : {}),
                              ...(isWarmupSection
                                ? {
                                    borderColor: 'rgba(245, 158, 11, 0.3)',
                                    background: 'rgba(245, 158, 11, 0.06)',
                                  }
                                : {}),
                              ...(isCompleted
                                ? {
                                    opacity: 0.55,
                                    borderColor: '#22c55e',
                                  }
                                : {}),
                              ...(isSkipped
                                ? {
                                    opacity: 0.45,
                                    borderColor: '#ef4444',
                                    textDecoration: 'line-through',
                                  }
                                : {}),
                            }}
                          >
                            <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                              <span style={{ fontSize: '16px' }}>
                                {isCompleted ? '✓' : isSkipped ? '>>' : isWarmupSection ? 'W' : 'O'}
                              </span>
                              <div>
                                <div
                                  style={{
                                    color: isSkipped ? '#ef4444' : isWarmupSection ? '#f59e0b' : 'var(--app-text)',
                                    fontWeight: '700',
                                    fontSize: '14px',
                                  }}
                                >
                                  {exercise.name}
                                  {isSkipped && <span style={{ fontSize: '11px', marginLeft: '8px' }}>(Skipped)</span>}
                                </div>
                                <div style={{ color: 'var(--app-text-muted)', fontSize: '12px' }}>
                                  {exercise.sets} Sets • {exercise.reps} {isWarmupSection ? '• No Camera' : 'Reps'}
                                </div>
                              </div>
                            </div>
                          </div>
                        );
                      };

                      return (
                        <>
                          {warmupExercises.length > 0 && (
                            <div style={{ marginBottom: '16px' }}>
                              <div
                                style={{
                                  fontSize: '11px',
                                  fontWeight: '700',
                                  color: '#f59e0b',
                                  textTransform: 'uppercase',
                                  letterSpacing: '1px',
                                  marginBottom: '10px',
                                  padding: '8px 12px',
                                  background: 'rgba(245, 158, 11, 0.1)',
                                  borderRadius: '8px',
                                }}
                              >
                                Warmup - {activeDay.focus}
                              </div>
                              {warmupExercises.map((exercise, index) => renderExerciseItem(exercise, index, true))}
                            </div>
                          )}

                          {mainExercises.map((exercise, index) => renderExerciseItem(exercise, index, false))}
                        </>
                      );
                    })()}
                  </div>
                  <div style={styles.selectionPreview}>
                    {activeExercise ? (
                      <>
                        <div style={{fontSize:'32px', fontWeight:'800', color:'var(--app-text)', marginBottom:'10px'}}>{activeExercise.name}</div>
                        <div style={{fontSize:'16px', color:'#a5b4fc', marginBottom:'30px', fontFamily:'monospace'}}>
                          {(() => {
                            const targetSets = activeExerciseTimed ? activeExerciseTargetSets : activeExercise.sets;
                            const doneSets = completedSetsMap[activeExercise.name] || 0;
                            const isFullyDone = exerciseStatus[getExerciseStatusKey(activeExercise)] === 'completed';
                            const displaySets = isFullyDone ? targetSets : doneSets;
                            
                            if (displaySets > 0) {
                              return `${displaySets}/${targetSets} SETS COMPLETED x ${activeExerciseTimed ? formatDurationClock(activeExerciseDuration) + ' TIMER' : activeExercise.reps + ' REPS'}`;
                            } else {
                              return `${targetSets} SETS x ${activeExerciseTimed ? formatDurationClock(activeExerciseDuration) + ' TIMER' : activeExercise.reps + ' REPS'}`;
                            }
                          })()}
                        </div>
                        <div style={{...styles.gifLargeContainer, ...workoutLayout.previewMedia}}>
                          {renderActiveExerciseMedia()}
                        </div>
                        <button style={styles.btnStartLarge} onClick={startCamera}>
                          {exerciseNeedsCamera(activeExercise) ? 'START AI CAMERA' : 'START TIMER MODE'}
                        </button>
                      </>
                    ) : (
                      <>
                        <div style={{fontSize:'60px', marginBottom:'20px'}}>👈</div>
                        <div style={{fontSize:'18px', fontWeight:'600'}}>Select an exercise from the left to begin</div>
                      </>
                    )}
                  </div>
                </>
              )}

              {isCameraOn && (
                <div style={workoutLayout.focusContainer}>
                  <div style={workoutLayout.focusLeft}>
                    <div style={styles.activeExTitle}>{activeExercise.name}</div>
                    
                    {!isResting ? (
                      <div style={styles.activeExStats}>
                        {activeExerciseTimed ? (
                          <>
                            <span style={{color: 'var(--app-text)'}}>SET {currentSet} OF {activeExerciseTargetSets}</span> • <span style={{color: '#22c55e'}}>{formatDurationClock(exerciseTimeLeft)} LEFT</span>
                          </>
                        ) : (
                          <>
                            <span style={{color: 'var(--app-text)'}}>SET {currentSet} OF {activeExercise.sets}</span> • <span style={{color: '#22c55e'}}>{currentReps} / {activeExercise.reps} REPS</span>
                          </>
                        )}
                      </div>
                    ) : (
                      <div style={{...styles.activeExStats, color: '#f59e0b', fontSize: '24px'}}>
                        RESTING: {restTimeLeft}s
                      </div>
                    )}
                    
                    {formFeedback && !isResting && activeExercisePoseTrackable && (() => {
                       const isPos = ['Great job!', 'Keep it up!', 'Perfect form!', 'You got this!', 'Nice work!'].includes(formFeedback);
                       return (
                         <div style={{background: isPos ? 'rgba(34, 197, 94, 0.2)' : 'rgba(239, 68, 68, 0.2)', color: isPos ? '#4ade80' : '#ef4444', padding: '10px', borderRadius: '8px', marginBottom: '15px', fontWeight: 'bold', fontSize: '14px'}}>
                           {isPos ? '✅' : '⚠️'} {formFeedback}
                         </div>
                       );
                    })()}

                    {/* Priority 1: AI Variation Suggestion Card */}
                    {variationResult && (
                      <div style={{
                        background: 'linear-gradient(135deg, rgba(99,102,241,0.15) 0%, rgba(34,211,238,0.08) 100%)',
                        border: '1px solid rgba(99,102,241,0.35)',
                        borderRadius: '14px',
                        padding: '14px 16px',
                        marginBottom: '14px',
                        display: 'flex',
                        alignItems: 'flex-start',
                        gap: '12px',
                        position: 'relative',
                        animation: 'fadeIn 0.4s ease-out',
                      }}>
                        <button onClick={() => setVariationResult(null)} style={{ position: 'absolute', top: 8, right: 10, background: 'none', border: 'none', color: 'var(--app-text-muted)', fontSize: '16px', cursor: 'pointer' }}>✕</button>
                        <div style={{ fontSize: '26px', flexShrink: 0 }}>
                          {variationResult.suggestion?.action === 'progress' ? '🚀' : variationResult.suggestion?.action === 'regress' ? '🔄' : '✅'}
                        </div>
                        <div style={{ flex: 1, paddingRight: '20px' }}>
                          <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '4px', flexWrap: 'wrap' }}>
                            <span style={{ fontSize: '12px', fontWeight: 800, textTransform: 'uppercase', letterSpacing: '0.6px', color: '#a5b4fc' }}>AI Coach</span>
                            <span style={{ padding: '2px 8px', borderRadius: '20px', fontSize: '10px', fontWeight: 700,
                              background: variationResult.suggestion?.action === 'progress' ? 'rgba(34,197,94,0.2)' : variationResult.suggestion?.action === 'regress' ? 'rgba(239,68,68,0.2)' : 'rgba(245,158,11,0.2)',
                              color: variationResult.suggestion?.action === 'progress' ? '#22c55e' : variationResult.suggestion?.action === 'regress' ? '#ef4444' : '#f59e0b' }}>
                              {(variationResult.suggestion?.action || 'maintain').toUpperCase()}
                            </span>
                            <span style={{ fontSize: '11px', color: 'var(--app-text-muted)' }}>Score: {Math.round((variationResult.formScore || 0) * 100)}%</span>
                          </div>
                          {variationResult.suggestion?.next_exercise && (
                            <div style={{ fontSize: '13px', fontWeight: 700, color: 'var(--app-text)', marginBottom: '4px' }}>Next: {variationResult.suggestion.next_exercise}</div>
                          )}
                          {variationResult.coaching?.primary_message && (
                            <div style={{ fontSize: '12px', color: 'var(--app-text-muted)', lineHeight: 1.45 }}>{variationResult.coaching.primary_message}</div>
                          )}
                        </div>
                      </div>
                    )}

                    <div style={styles.gifLargeContainer}>
                      <div style={{position:'absolute', top:15, left:15, background:'rgba(0,0,0,0.7)', padding:'4px 10px', borderRadius:'6px', fontSize:'12px', fontWeight:'700', color:'white', zIndex:5}}>FORM GUIDE</div>
                      {renderActiveExerciseMedia()}
                    </div>

                    
                    <div style={workoutLayout.controlsContainer}>
                      <button style={styles.btnStop} className="btn-stop" onClick={stopCamera}>END SESSION</button>
                      <button style={styles.btnDone} className="btn-done" onClick={() => handleExerciseSkipped(activeExercise)}>SKIP TO NEXT</button>
                    </div>
                  </div>
                  <div style={workoutLayout.focusRight}>
                    {activeExercise && !activeExerciseNeedsCamera ? (
                      <TimerExerciseMode
                        key={getExerciseStatusKey(activeExercise) || activeExercise?.name || 'timer-mode'}
                        targetSets={activeExerciseTargetSets}
                        targetDuration={activeExerciseDuration || 300}
                        restDuration={getRestSeconds(activeExercise)}
                        onComplete={handleExerciseComplete}
                        onSkip={() => handleExerciseSkipped(activeExercise)}
                      />
                    ) : (
                      <>
                        <video ref={videoRef} autoPlay playsInline muted style={styles.videoFeed} />

                        {/* MASSIVE IN-VIDEO UI OVERLAYS FOR POSTURE AND REPS */}
                        <div style={{position: 'absolute', top: 20, left: 20, zIndex: 25, display: 'flex', flexDirection: 'column', gap: '10px'}}>
                            {!isResting && (
                                <div style={{background: 'var(--overlay-bg)', padding: '10px 20px', borderRadius: '12px', border: '2px solid var(--app-border)'}}>
                                    <div style={{color: 'var(--app-text-muted)', fontSize: '14px', fontWeight: 'bold'}}>SET {currentSet} OF {activeExerciseTargetSets}</div>
                                    {activeExerciseTimed ? (
                                      <div style={{color: '#22c55e', fontSize: '48px', fontWeight: '900', lineHeight: '1'}}>{formatDurationClock(exerciseTimeLeft)}</div>
                                    ) : (
                                      <div style={{color: '#22c55e', fontSize: '48px', fontWeight: '900', lineHeight: '1'}}>{currentReps} <span style={{fontSize: '24px', color: 'var(--app-text)'}}>/ {activeExercise.reps}</span></div>
                                    )}
                                </div>
                            )}
                        </div>

                        {/* Bug #2 Fix: Warming message overlay with auto-dismiss */}
                        {poseLoadingStatus === 'warming' && (
                          <div style={{
                            position: 'absolute',
                            top: '50%',
                            left: '50%',
                            transform: 'translate(-50%, -50%)',
                            zIndex: 30,
                            background: 'rgba(0, 0, 0, 0.85)',
                            backdropFilter: 'blur(8px)',
                            borderRadius: '16px',
                            padding: '24px 32px',
                            color: '#fbbf24',
                            fontWeight: '700',
                            fontSize: '18px',
                            textAlign: 'center',
                            border: '2px solid rgba(251, 191, 36, 0.5)',
                            boxShadow: '0 20px 40px rgba(0,0,0,0.5)',
                            animation: 'pulseBorder 1.5s infinite'
                          }}>
                            <div style={{ fontSize: '32px', marginBottom: '8px' }}>🔥</div>
                            AI is warming up...
                            <div style={{ fontSize: '13px', fontWeight: '500', marginTop: '8px', opacity: 0.8 }}>
                              Initializing pose detection model
                            </div>
                          </div>
                        )}
                        {poseLoadingStatus === 'ready' && (
                          <div style={{
                            position: 'absolute',
                            top: '50%',
                            left: '50%',
                            transform: 'translate(-50%, -50%)',
                            zIndex: 30,
                            background: 'rgba(0, 0, 0, 0.85)',
                            backdropFilter: 'blur(8px)',
                            borderRadius: '16px',
                            padding: '20px 28px',
                            color: '#4ade80',
                            fontWeight: '700',
                            fontSize: '18px',
                            textAlign: 'center',
                            border: '2px solid rgba(74, 222, 128, 0.5)',
                            boxShadow: '0 20px 40px rgba(0,0,0,0.5)',
                          }}>
                            <div style={{ fontSize: '32px', marginBottom: '8px' }}>✓</div>
                            Ready!
                            <div style={{ fontSize: '13px', fontWeight: '500', marginTop: '8px', opacity: 0.8 }}>
                              Pose detection active
                            </div>
                          </div>
                        )}

                        {formFeedback && !isResting && activeExercisePoseTrackable && (() => {
                            const isPos = ['Great job!', 'Keep it up!', 'Perfect form!', 'You got this!', 'Nice work!'].includes(formFeedback);
                            return (
                              <div style={{
                                  position: 'absolute', 
                                  top: '50%', 
                                  left: '50%', 
                                  transform: 'translate(-50%, -50%)', 
                                  background: isPos ? 'rgba(34, 197, 94, 0.9)' : 'rgba(239, 68, 68, 0.9)', 
                                  color: 'var(--app-text)', 
                                  padding: '20px 40px', 
                                  borderRadius: '16px', 
                                  zIndex: 30, 
                                  fontWeight: '900', 
                                  fontSize: '32px',
                                  textAlign: 'center',
                                  border: '4px solid #fff',
                                  boxShadow: '0 20px 40px rgba(0,0,0,0.5)',
                                  animation: 'pulseBorder 1s infinite'
                              }}>
                               {isPos ? '✅ EXCELLENT' : '⚠️ INCORRECT POSTURE'}<br/>
                               <span style={{fontSize: '18px', fontWeight: '500', opacity: 0.9}}>{formFeedback}</span>
                             </div>
                            );
                        })()}
                        {isCameraOn && activeExercisePoseTrackable && (
                          <PoseDetector
                            videoRef={videoRef}
                            isActive={isCameraOn && !isResting}
                            exercise={activeExercise}
                            currentReps={currentReps}
                            onRepUpdate={handleRepUpdate}
                            onFormFeedback={setFormFeedback}
                            onLoadingChange={setPoseLoadingStatus}
                          />
                        )}
                        {isCameraOn && !activeExercisePoseTrackable && (
                          <div style={{
                            position: 'absolute',
                            right: 20,
                            bottom: 20,
                            zIndex: 26,
                            background: 'rgba(0, 0, 0, 0.78)',
                            border: '1px solid rgba(34, 197, 94, 0.45)',
                            borderRadius: '10px',
                            padding: '10px 14px',
                            color: '#bbf7d0',
                            fontWeight: '700',
                            fontSize: '12px',
                            textTransform: 'uppercase',
                            letterSpacing: '0.6px'
                          }}>
                            Timer Mode: Pose AI paused for this movement
                          </div>
                        )}

                        {activeExerciseNeedsCamera && (
                          <div style={styles.recBadge}><div style={{width:10, height:10, background:'white', borderRadius:'50%', animation:'pulseBorder 1s infinite'}}></div>REC</div>
                        )}

                        {activeExerciseNeedsCamera && isResting && (
                           <div style={{position: 'absolute', top: 0, left: 0, width: '100%', height: '100%', background: 'var(--overlay-bg)', display: 'flex', alignItems: 'center', justifyContent: 'center', flexDirection: 'column', zIndex: 30}}>
                             <div style={{fontSize: '32px', color: 'var(--app-text-muted)', marginBottom: '10px', fontWeight: '800'}}>RECOVERY TIME</div>
                             <div style={{fontSize: '100px', fontWeight: '900', color: '#f59e0b'}}>{restTimeLeft}</div>
                             <div style={{fontSize: '24px', color: '#22c55e', fontWeight: 'bold', marginBottom: '5px'}}>Set {currentSet}/{activeExerciseTimed ? activeExerciseTargetSets : activeExercise.sets} Completed!</div>
                             <div style={{fontSize: '18px', color: 'var(--app-text)', marginTop: '10px', marginBottom: '30px'}}>Next: Set {currentSet + 1} of {activeExercise.name}</div>
                             <div style={{display: 'flex', gap: '15px'}}>
                               <button onClick={() => {
                                 const newTime = Math.max(0, restTimeLeft - 10);
                                 setRestTimeLeft(newTime);
                                 setRestEndTime(Date.now() + newTime * 1000);
                               }} style={{background: 'rgba(255,255,255,0.1)', border: '1px solid rgba(255,255,255,0.2)', color: 'white', padding: '12px 20px', borderRadius: '8px', cursor: 'pointer', fontWeight: 'bold'}}>-10s</button>
                               
                               <button onClick={() => {
                                 setRestTimeLeft(0);
                                 setRestEndTime(Date.now() - 100);
                               }} style={{background: 'var(--btn-skip-bg)', border: 'none', color: 'var(--btn-skip-text)', padding: '12px 24px', borderRadius: '8px', cursor: 'pointer', fontWeight: 'bold', fontSize: '16px'}}>Skip Rest</button>
                               
                               <button onClick={() => {
                                 const newTime = restTimeLeft + 30;
                                 setRestTimeLeft(newTime);
                                 setRestEndTime(Date.now() + newTime * 1000);
                               }} style={{background: 'rgba(255,255,255,0.1)', border: '1px solid rgba(255,255,255,0.2)', color: 'white', padding: '12px 20px', borderRadius: '8px', cursor: 'pointer', fontWeight: 'bold'}}>+30s</button>
                             </div>
                           </div>
                        )}
                      </>
                    )}
                  </div>
                </div>
              )}
            </div>
          )}
        </div>

        {showWorkoutToRestModal && swapWorkoutDayIndex != null && (
          <div
            style={{
              position: 'fixed',
              inset: 0,
              background: 'rgba(0,0,0,0.7)',
              zIndex: 2200,
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              padding: '16px',
            }}
          >
            <div
              style={{
                width: 'min(560px, 96vw)',
                background: 'var(--app-surface)',
                border: '1px solid var(--app-border)',
                borderRadius: '16px',
                padding: '20px',
                boxShadow: '0 25px 50px rgba(0,0,0,0.45)',
              }}
            >
              <div style={{ fontSize: '18px', fontWeight: '800', color: 'var(--app-text)', marginBottom: '8px' }}>
                Move Workout To A Future Rest Day
              </div>
              <div style={{ color: 'var(--app-text-muted)', fontSize: '13px', marginBottom: '16px' }}>
                Pick a future original rest day for this workout. Swapped days are locked and cannot be swapped again.
              </div>

              <div style={{ display: 'grid', gap: '10px', marginBottom: '14px' }}>
                {getFutureOriginalRestDays(displayPlan, swapWorkoutDayIndex, todayIdx).map((day) => {
                  const idx = toDayIndex(day?.day_of_week, -1);
                  const isSelected = idx === selectedTargetRestDayIndex;
                  return (
                    <button
                      key={`swap-target-${idx}`}
                      onClick={() => setSelectedTargetRestDayIndex(idx)}
                      style={{
                        textAlign: 'left',
                        padding: '12px 14px',
                        borderRadius: '10px',
                        border: isSelected ? '1px solid #6366f1' : '1px solid var(--app-border)',
                        background: isSelected ? 'rgba(99, 102, 241, 0.18)' : 'var(--quote-bg)',
                        color: 'var(--app-text)',
                        cursor: 'pointer',
                      }}
                    >
                      <div style={{ fontWeight: '700', fontSize: '14px' }}>{weekdayNames[idx] || day?.day || `Day ${idx + 1}`}</div>
                      <div style={{ fontSize: '12px', color: 'var(--app-text-muted)' }}>Current: Rest Day</div>
                    </button>
                  );
                })}
              </div>

              <div
                style={{
                  fontSize: '12px',
                  color: '#f59e0b',
                  background: 'rgba(245, 158, 11, 0.1)',
                  border: '1px solid rgba(245, 158, 11, 0.3)',
                  borderRadius: '10px',
                  padding: '10px 12px',
                  marginBottom: '16px',
                }}
              >
                This operation is one-time for both involved days. Use it only when needed.
              </div>

              <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '10px' }}>
                <button
                  onClick={() => {
                    setShowWorkoutToRestModal(false);
                    setSwapWorkoutDayIndex(null);
                    setSelectedTargetRestDayIndex(null);
                  }}
                  style={{
                    padding: '10px 14px',
                    borderRadius: '10px',
                    border: '1px solid var(--app-border)',
                    background: 'var(--app-surface2)',
                    color: 'var(--app-text)',
                    cursor: 'pointer',
                    fontWeight: '600',
                  }}
                >
                  Cancel
                </button>
                <button
                  onClick={handleConfirmWorkoutToRestSwap}
                  disabled={selectedTargetRestDayIndex == null}
                  style={{
                    padding: '10px 14px',
                    borderRadius: '10px',
                    border: 'none',
                    background: selectedTargetRestDayIndex == null ? 'var(--btn-skip-bg)' : '#6366f1',
                    color: selectedTargetRestDayIndex == null ? 'var(--btn-skip-text)' : 'var(--app-text)',
                    cursor: selectedTargetRestDayIndex == null ? 'not-allowed' : 'pointer',
                    fontWeight: '700',
                  }}
                >
                  Confirm Move
                </button>
              </div>
            </div>
          </div>
        )}

        {showHistory && (
          <div style={workoutLayout.historyPanel}>
            <div style={{display:'flex', justifyContent:'space-between', alignItems:'center', marginBottom:'24px'}}>
              <div style={{fontSize:'20px', fontWeight:'800', color:'var(--app-text)'}}>History</div>
              <button onClick={() => setShowHistory(false)} style={{background:'none', border:'none', color:'var(--app-text)', fontSize:'20px', cursor:'pointer'}}>✕</button>
            </div>

            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '8px', marginBottom: '16px' }}>
              <button
                onClick={() => setHistoryTab('workout')}
                style={{
                  padding: '10px 12px',
                  borderRadius: '10px',
                  border: historyTab === 'workout' ? '1px solid #6366f1' : '1px solid var(--app-border)',
                  background: historyTab === 'workout' ? 'rgba(99,102,241,0.18)' : 'var(--quote-bg)',
                  color: 'var(--app-text)',
                  fontWeight: '700',
                  cursor: 'pointer',
                }}
              >
                Workouts
              </button>
              <button
                onClick={() => setHistoryTab('swap')}
                style={{
                  padding: '10px 12px',
                  borderRadius: '10px',
                  border: historyTab === 'swap' ? '1px solid #f59e0b' : '1px solid var(--app-border)',
                  background: historyTab === 'swap' ? 'rgba(245,158,11,0.15)' : 'var(--quote-bg)',
                  color: 'var(--app-text)',
                  fontWeight: '700',
                  cursor: 'pointer',
                }}
              >
                Swaps ({swapLimits.used}/{swapLimits.max})
              </button>
            </div>

            {historyTab === 'workout' ? (
              <>
                {pastWorkouts && pastWorkouts.length > 0 ? (
                  pastWorkouts.map((day, i) => (
                    <div key={i} style={styles.historyItem} className="history-card" onClick={() => setSelectedHistory(selectedHistory === i ? null : i)}>
                      <div style={{display:'flex', justifyContent:'space-between', alignItems:'center'}}>
                        <div style={styles.historyDate}>{day.date || new Date().toLocaleDateString()}</div>
                        <div style={{fontSize:'12px', fontWeight:'700', color: day.status === 'Completed' ? '#22c55e' : '#ef4444'}}>{day.status || 'Completed'}</div>
                      </div>
                      {selectedHistory === i && day.details && (
                        <div style={{marginTop:'15px', paddingTop:'15px', borderTop:'1px solid var(--app-border)'}}>
                          <div style={styles.historyLabel}>Details:</div>
                          <div style={styles.historyList}>
                            <div style={{marginBottom:'4px'}}>{day.details}</div>
                          </div>
                        </div>
                      )}
                    </div>
                  ))
                ) : (
                  <div style={{textAlign:'center', padding:'40px', color:'#52525b'}}>No workout history yet</div>
                )}
              </>
            ) : (
              <>
                <div
                  style={{
                    background: 'rgba(245, 158, 11, 0.08)',
                    border: '1px solid rgba(245, 158, 11, 0.28)',
                    borderRadius: '12px',
                    padding: '12px',
                    marginBottom: '14px',
                  }}
                >
                  <div style={{ fontSize: '12px', color: '#fbbf24', fontWeight: '700', marginBottom: '4px' }}>
                    Weekly Swap Limits
                  </div>
                  <div style={{ fontSize: '13px', color: 'var(--app-text)' }}>
                    Used: {swapLimits.used} / {swapLimits.max}
                  </div>
                  <div style={{ fontSize: '12px', color: 'var(--app-text-muted)', marginTop: '2px' }}>
                    Remaining this week: {Math.max(0, swapLimits.remaining)}
                  </div>
                </div>

                {swapHistory.length > 0 ? (
                  swapHistory
                    .slice()
                    .reverse()
                    .map((entry, idx) => {
                      const fromIdx = Number(entry?.from_day);
                      const toIdx = Number(entry?.to_day);
                      const fromLabel = Number.isInteger(fromIdx) && fromIdx >= 0 && fromIdx <= 6 ? weekdayNames[fromIdx] : `Day ${fromIdx + 1}`;
                      const toLabel = Number.isInteger(toIdx) && toIdx >= 0 && toIdx <= 6 ? weekdayNames[toIdx] : `Day ${toIdx + 1}`;
                      const isRestToWorkout = entry?.direction === 'rest_to_workout';

                      return (
                        <div key={`swap-history-${idx}`} style={styles.historyItem} className="history-card">
                          <div style={{display:'flex', justifyContent:'space-between', alignItems:'center', marginBottom:'8px'}}>
                            <div style={{ ...styles.historyDate, marginBottom: 0 }}>
                              {isRestToWorkout ? 'Rest -> Workout' : 'Workout -> Rest'}
                            </div>
                            <div style={{ fontSize: '11px', color: 'var(--app-text-muted)' }}>{formatSwapTimestamp(entry?.timestamp)}</div>
                          </div>
                          <div style={{ fontSize: '13px', color: 'var(--app-text)', marginBottom: '6px' }}>
                            {`${fromLabel} -> ${toLabel}`}
                          </div>
                          <div style={{ fontSize: '12px', color: 'var(--app-text-muted)' }}>
                            Focus: {entry?.workout_focus || 'Workout'}
                          </div>
                        </div>
                      );
                    })
                ) : (
                  <div style={{textAlign:'center', padding:'40px', color:'#52525b'}}>No swaps recorded this week</div>
                )}
              </>
            )}
          </div>
        )}
      </div>
      <ConfirmDialog
        show={confirmDialog.show}
        message={confirmDialog.message}
        onConfirm={handleConfirm}
        onCancel={handleCancelConfirm}
      />
      {variationResult && (
        <div style={{
          position: 'fixed',
          top: 0,
          left: 0,
          right: 0,
          bottom: 0,
          background: 'rgba(15, 23, 42, 0.85)',
          backdropFilter: 'blur(8px)',
          display: 'flex',
          justifyContent: 'center',
          alignItems: 'center',
          zIndex: 9999,
          animation: 'fadeIn 0.3s ease-out',
        }}>
          <div style={{
            background: 'linear-gradient(135deg, rgba(30, 27, 75, 0.95) 0%, rgba(15, 23, 42, 0.98) 100%)',
            border: '1px solid rgba(99, 102, 241, 0.35)',
            boxShadow: '0 24px 64px rgba(0, 0, 0, 0.5), 0 0 40px rgba(99, 102, 241, 0.15)',
            borderRadius: '24px',
            width: '90%',
            maxWidth: '520px',
            padding: '30px',
            position: 'relative',
            color: 'var(--app-text)',
            textAlign: 'center',
            animation: 'slideDown 0.4s cubic-bezier(0.16, 1, 0.3, 1)',
          }}>
            {variationResult.loading ? (
              <div style={{ padding: '40px 0' }}>
                <div style={{
                  width: '60px',
                  height: '60px',
                  border: '4px solid rgba(99, 102, 241, 0.1)',
                  borderTop: '4px solid #6366f1',
                  borderRadius: '50%',
                  margin: '0 auto 20px',
                  animation: 'spin 1s linear  infinite',
                }} />
                <h3 style={{ fontSize: '20px', fontWeight: '800', marginBottom: '8px' }}>SESSION COMPLETE!</h3>
                <p style={{ color: 'var(--app-text-muted)', fontSize: '14px' }}>Analysing form and preparing progression suggestions...</p>
              </div>
            ) : (
              <>
                <div style={{ fontSize: '50px', marginBottom: '15px' }}>
                  {variationResult.suggestion?.action === 'progress' ? '🚀' : variationResult.suggestion?.action === 'regress' ? '🔄' : '🎉'}
                </div>
                
                <h2 style={{ fontSize: '24px', fontWeight: '800', marginBottom: '4px', textTransform: 'uppercase', letterSpacing: '0.5px' }}>
                  {variationResult.suggestion?.action === 'progress' ? 'Progression Unlocked!' : 
                   variationResult.suggestion?.action === 'regress' ? 'Form Correction Recommended' : 
                   'Workout Complete!'}
                </h2>
                <div style={{ display: 'inline-flex', alignItems: 'center', gap: '8px', background: 'rgba(99, 102, 241, 0.15)', padding: '4px 12px', borderRadius: '20px', fontSize: '12px', fontWeight: '700', color: '#a5b4fc', marginBottom: '24px' }}>
                  <span>AI COACH RATING</span> • <span>SCORE: {Math.round((variationResult.formScore || 0) * 100)}%</span>
                </div>

                <div style={{
                  background: 'rgba(255, 255, 255, 0.03)',
                  border: '1px solid rgba(255, 255, 255, 0.06)',
                  borderRadius: '16px',
                  padding: '18px',
                  marginBottom: '24px',
                  textAlign: 'left',
                }}>
                  <div style={{ fontSize: '11px', fontWeight: '800', color: 'var(--app-text-muted)', textTransform: 'uppercase', letterSpacing: '1px', marginBottom: '8px' }}>
                    Recommendation for {variationResult.exercise}
                  </div>
                  {variationResult.suggestion?.suggested_exercise && (
                    <div style={{ fontSize: '16px', fontWeight: '700', color: 'var(--app-text)', marginBottom: '8px' }}>
                      {variationResult.suggestion.action === 'progress' ? 'Try next: ' : 
                       variationResult.suggestion.action === 'regress' ? 'Easier swap: ' : 
                       'Keep variation: '}
                      <span style={{ color: '#22d3ee' }}>{variationResult.suggestion.suggested_exercise}</span>
                    </div>
                  )}
                  {variationResult.coaching?.primary_message ? (
                    <p style={{ fontSize: '13px', color: 'var(--app-text-muted)', margin: 0, lineHeight: '1.5' }}>
                      {variationResult.coaching.primary_message}
                    </p>
                  ) : variationResult.suggestion?.reason ? (
                    <p style={{ fontSize: '13px', color: 'var(--app-text-muted)', margin: 0, lineHeight: '1.5' }}>
                      {variationResult.suggestion.reason}
                    </p>
                  ) : null}
                </div>

                <button
                  onClick={async () => {
                    const payload = variationResult.statusPayload;
                    setVariationResult(null);
                    if (payload) {
                      await finishSession(payload.isPartialSession, payload.options);
                    }
                  }}
                  style={{
                    background: 'linear-gradient(135deg, #6366f1 0%, #4f46e5 100%)',
                    color: 'white',
                    border: 'none',
                    borderRadius: '12px',
                    padding: '14px 28px',
                    fontWeight: '800',
                    fontSize: '15px',
                    width: '100%',
                    cursor: 'pointer',
                    boxShadow: '0 8px 20px rgba(99, 102, 241, 0.3)',
                    transition: 'all 0.2s',
                  }}
                >
                  SAVE & EXIT WORKOUT
                </button>
              </>
            )}
          </div>
        </div>
      )}
    </>
  );
}

export default Workout;