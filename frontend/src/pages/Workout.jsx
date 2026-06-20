import React, { useState, useEffect, useRef, useCallback } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { useNotification } from '../components/NotificationProvider';
import {
  getProfile,
  generateWorkout,
  saveUserWorkoutToNode,
  getWorkoutHistory,
  saveWorkoutHistory,
  saveTrends,
  swapRestToWorkout,
  swapWorkoutToRest,
} from '../api';
import { setToStorage, getFromStorage, logoutSafe, StorageKeys } from '../utils/storage';
import ConfirmDialog from '../components/ConfirmDialog';
import Navbar from '../components/Navbar';
import PoseDetector from '../components/PoseDetector';
import TimerExerciseMode from '../components/TimerExerciseMode';
import { syncBridge, SyncTypes } from '../utils/syncBridge';
import { preloadPoseAssets } from '../utils/poseModelPreload';
import WorkoutDayCard from '../components/workout/WorkoutDayCard';
// BUG-F2/F8: WorkoutDayCard extracted to components/workout/WorkoutDayCard.jsx

// Define full weekday names array
const weekdayNames = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'];
const WORKOUT_PLAN_CACHE_VERSION = '2026-04-10-workout-fix-7-response-declared';
const DEFAULT_FALLBACK_GIF = 'https://media.giphy.com/media/3o7TKsQ8UQJ5n6WfTO/giphy.gif';

// --- STYLES (Your Exact Styles Preserved) ---
const styles = {
  page: { background: '#09090b', minHeight: '100dvh', color: '#e4e4e7', fontFamily: "'Inter', sans-serif", overflowX: 'hidden', width: '100vw' },
  navbar: {
    display: 'flex', alignItems: 'center',
    padding: '0 clamp(12px, 4vw, 40px)', height: 'clamp(64px, 9vw, 80px)',
    gap: 'clamp(8px, 2vw, 18px)',
    borderBottom: '1px solid rgba(255,255,255,0.08)',
    background: 'rgba(9, 9, 11, 0.6)', backdropFilter: 'blur(16px)',
    position: 'sticky', top: 0, zIndex: 1000,
    overflowX: 'auto'
  },
  brand: {
    flex: 1,
    fontSize: '22px', fontWeight: '900', letterSpacing: '-1px',
    background: 'linear-gradient(to right, #fff, #a5b4fc)',
    WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent',
    display: 'flex', alignItems: 'center', gap: '10px'
  },
  navCenter: {
    display: 'flex', gap: 'clamp(4px, 1.5vw, 8px)', height: '100%', alignItems: 'center',
    justifyContent: 'center'
  },
  navLink: {
    display: 'flex', alignItems: 'center', padding: '8px clamp(10px, 2vw, 20px)',
    fontSize: 'clamp(11px, 1.7vw, 13px)', fontWeight: '600', color: '#a1a1aa',
    cursor: 'pointer', borderRadius: '20px', transition: 'all 0.2s',
    textTransform: 'uppercase', letterSpacing: '0.5px',
    border: '1px solid transparent'
  },
  navLinkActive: {
    background: 'rgba(255,255,255,0.1)', color: '#fff',
    boxShadow: '0 0 20px rgba(255,255,255,0.05)',
    border: '1px solid rgba(255,255,255,0.05)'
  },
  navRight: {
    flex: 1,
    display: 'flex', alignItems: 'center', gap: 'clamp(8px, 2vw, 24px)',
    justifyContent: 'flex-end'
  },
  brandDot: { width: '8px', height: '8px', background: '#6366f1', borderRadius: '50%', boxShadow: '0 0 15px #6366f1' },
  dateDisplay: { fontSize: 'clamp(11px, 1.6vw, 13px)', fontWeight: '600', color: '#a1a1aa', fontFamily: 'sans-serif', letterSpacing: '0.5px', marginRight: '8px' },
  iconButton: { width: 'clamp(36px, 6vw, 42px)', height: 'clamp(36px, 6vw, 42px)', borderRadius: '12px', background: 'rgba(255,255,255,0.03)', border: '1px solid rgba(255,255,255,0.08)', color: '#fff', display: 'flex', alignItems: 'center', justifyContent: 'center', cursor: 'pointer', fontSize: '18px', transition: 'all 0.2s', position: 'relative' },
  notifDropdown: { position: 'absolute', top: '60px', right: '0px', width: 'min(92vw, 340px)', background: '#18181b', border: '1px solid rgba(255,255,255,0.1)', borderRadius: '16px', padding: '16px', zIndex: 2000, boxShadow: '0 20px 50px rgba(0,0,0,0.5)', animation: 'slideDown 0.2s ease-out' },
  notifItem: { padding: '12px 16px', borderBottom: '1px solid rgba(255,255,255,0.05)', fontSize: '13px', color: '#d4d4d8', wordBreak: 'break-word' },
  logoutBtn: { display: 'flex', alignItems: 'center', gap: '8px', padding: '0 clamp(10px, 2vw, 20px)', borderRadius: '12px', background: 'rgba(239, 68, 68, 0.1)', border: '1px solid rgba(239, 68, 68, 0.2)', color: '#ef4444', cursor: 'pointer', transition: 'all 0.2s ease', height: 'clamp(36px, 6vw, 42px)' },
  logoutText: { fontSize: '12px', fontWeight: '700', letterSpacing: '0.5px', textTransform: 'uppercase' },
  container: { width: '100%', maxWidth: '1600px', margin: '0 auto', padding: '40px' },
  h1: { fontSize: '42px', fontWeight: '800', marginBottom: '40px', color: '#fff', letterSpacing: '-1px', wordBreak: 'break-word' },
  grid: { display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))', gap: '20px' },
  card: { background: '#18181b', borderRadius: '20px', padding: '24px', border: '1px solid rgba(255,255,255,0.05)', position: 'relative', transition: 'all 0.3s ease', overflow: 'hidden', minHeight: '200px', display: 'flex', flexDirection: 'column' },
  cardDone: { opacity: 0.5, border: '1px solid #22c55e', background: 'rgba(34, 197, 94, 0.05)' },
  overlayDone: { position: 'absolute', top: 0, left: 0, width: '100%', height: '100%', display: 'flex', alignItems: 'center', justifyContent: 'center', background: 'rgba(0,0,0,0.6)', zIndex: 10, flexDirection: 'column', gap: '10px' },
  cardMissed: { opacity: 0.5, border: '1px solid #ef4444', background: 'rgba(239, 68, 68, 0.05)' },
  overlayMissed: { position: 'absolute', top: 0, left: 0, width: '100%', height: '100%', display: 'flex', alignItems: 'center', justifyContent: 'center', background: 'rgba(0,0,0,0.6)', zIndex: 10, flexDirection: 'column', gap: '10px' },
  cardLocked: { opacity: 0.6, cursor: 'not-allowed', border: '1px dashed rgba(255,255,255,0.1)' },
  overlayLocked: { position: 'absolute', top: 0, left: 0, width: '100%', height: '100%', display: 'flex', alignItems: 'center', justifyContent: 'center', background: 'rgba(0,0,0,0.4)', zIndex: 10, flexDirection: 'column', gap: '10px' },
  cardActive: { border: '2px solid #6366f1', background: 'linear-gradient(145deg, #1e1e2e 0%, #2a2a35 100%)', boxShadow: '0 0 30px rgba(99, 102, 241, 0.15)', cursor: 'pointer', transform: 'scale(1.02)' },
  dayTitle: { fontSize: '14px', fontWeight: '700', textTransform: 'uppercase', letterSpacing: '1px', marginBottom: '8px', color: '#a1a1aa' },
  focusText: { fontSize: '20px', fontWeight: '800', color: '#fff', marginBottom: '16px', lineHeight: '1.3', wordBreak: 'break-word' },
  exPreview: { fontSize: '13px', color: '#71717a', marginBottom: '4px', display: 'flex', justifyContent: 'space-between', gap: '8px' },
  sessionContainer: { position: 'fixed', top: '80px', left: 0, width: '100%', height: 'calc(100vh - 80px)', background: '#09090b', zIndex: 500, display: 'flex', padding: '20px', gap: '20px', animation: 'fadeIn 0.3s ease-out' },
  selectionList: { flex: '0 0 350px', background: '#18181b', borderRadius: '24px', border: '1px solid rgba(255,255,255,0.05)', display: 'flex', flexDirection: 'column', padding: '20px', overflowY: 'auto' },
  sidebarHeader: { fontSize: '18px', fontWeight: '800', color: '#fff', marginBottom: '20px', display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '10px' },
  backBtn: { fontSize: '12px', padding: '6px 12px', background: 'rgba(255,255,255,0.1)', borderRadius: '8px', color: '#fff', border: 'none', cursor: 'pointer' },
  selectionPreview: { flex: 1, background: '#000', borderRadius: '24px', border: '1px solid rgba(255,255,255,0.1)', display: 'flex', alignItems: 'center', justifyContent: 'center', flexDirection: 'column', color: '#52525b', padding: '20px', textAlign: 'center' },
  focusContainer: { width: '100%', height: '100%', display: 'flex', gap: '20px' },
  focusLeft: { flex: '4', display: 'flex', flexDirection: 'column', background: '#18181b', borderRadius: '24px', padding: '24px', border: '1px solid rgba(255,255,255,0.05)' },
  activeExTitle: { fontSize: 'clamp(20px, 4vw, 28px)', fontWeight: '800', color: '#fff', marginBottom: '8px', lineHeight: '1.2', wordBreak: 'break-word' },
  activeExStats: { fontSize: '16px', color: '#a5b4fc', fontWeight: '600', marginBottom: '20px', fontFamily: 'monospace' },
  gifLargeContainer: { flex: 1, background: '#09090b', borderRadius: '16px', overflow: 'hidden', display: 'flex', alignItems: 'center', justifyContent: 'center', position: 'relative', border: '1px solid rgba(255,255,255,0.1)', marginBottom: '20px' },
  gifLarge: { width: '100%', height: '100%', objectFit: 'contain', maxWidth: '100%' },
  controlsContainer: { height: '80px', display: 'flex', gap: '15px' },
  focusRight: { flex: '6', background: '#000', borderRadius: '24px', border: '2px solid #6366f1', overflow: 'hidden', position: 'relative', display: 'flex', alignItems: 'center', justifyContent: 'center', boxShadow: '0 0 50px rgba(99, 102, 241, 0.1)' },
  videoFeed: { width: '100%', height: '100%', objectFit: 'contain', transform: 'scaleX(-1)' },
  recBadge: { position: 'absolute', top: 20, left: 20, background: 'rgba(220, 38, 38, 0.9)', padding: '6px 12px', borderRadius: '8px', color: 'white', fontWeight: '700', fontSize: '14px', display: 'flex', alignItems: 'center', gap: '8px', zIndex: 10 },
  exerciseItem: { padding: '18px', borderRadius: '16px', marginBottom: '12px', background: 'rgba(255,255,255,0.03)', border: '1px solid rgba(255,255,255,0.05)', cursor: 'pointer', transition: 'all 0.2s ease', position: 'relative' },
  exerciseItemActive: { background: 'linear-gradient(135deg, #1e1b4b 0%, #312e81 100%)', borderColor: '#6366f1', boxShadow: '0 4px 20px rgba(99, 102, 241, 0.3)' },
  btnStartLarge: { padding: '15px 40px', fontSize: '16px', borderRadius: '12px', background: '#6366f1', color: 'white', border: 'none', fontWeight: '800', cursor: 'pointer', marginTop: '20px', boxShadow: '0 4px 20px rgba(99, 102, 241, 0.4)', width: '100%' },
  btnStop: { flex: 1, borderRadius: '16px', background: '#27272a', border: '1px solid rgba(255,255,255,0.1)', color: '#ef4444', fontWeight: '800', fontSize: '16px', cursor: 'pointer', transition: 'all 0.2s', padding: '10px' },
  btnDone: { flex: 1, borderRadius: '16px', background: '#22c55e', color: 'white', fontWeight: '800', fontSize: '16px', border: 'none', cursor: 'pointer', boxShadow: '0 4px 15px rgba(34, 197, 94, 0.3)', padding: '10px' },
  historyPanel: { position: 'fixed', top: '80px', right: '0', width: '100%', maxWidth: '400px', height: 'calc(100vh - 80px)', background: '#09090b', borderLeft: '1px solid rgba(255,255,255,0.1)', zIndex: 1500, padding: '24px', overflowY: 'auto', animation: 'slideInRight 0.3s ease-out', boxShadow: '-20px 0 50px rgba(0,0,0,0.5)' },
  historyItem: { background: '#18181b', borderRadius: '16px', padding: '20px', marginBottom: '16px', border: '1px solid rgba(255,255,255,0.05)', cursor: 'pointer', transition: 'all 0.2s' },
  historyDate: { fontSize: '14px', fontWeight: '700', color: '#fff', marginBottom: '12px' },
  historySection: { marginBottom: '10px' },
  historyLabel: { fontSize: '11px', color: '#a5b4fc', fontWeight: '700', textTransform: 'uppercase', marginBottom: '4px' },
  historyList: { fontSize: '13px', color: '#a1a1aa', lineHeight: '1.4' },
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
  return monday.toISOString().slice(0, 10);
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
  const videoRef = useRef(null);
  const notifRef = useRef(null);
  const { showError, showSuccess } = useNotification();
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
  const [poseTrackingError, setPoseTrackingError] = useState(null); // Bug #52 fixed: setter now available for error updates
  const [_loading, setLoading] = useState(false); // Bug #18 fixed: state variable properly destructured
  const [_errorMsg, setError] = useState(null); // Bug #18 fixed: state variable properly destructured
  const [pastWorkouts, setPastWorkouts] = useState([]);

  // Posture processing state
  const [currentSet, setCurrentSet] = useState(1);
  const [currentReps, setCurrentReps] = useState(0);
  const [isResting, setIsResting] = useState(false);
  const [restTimeLeft, setRestTimeLeft] = useState(0);
  const [exerciseTimeLeft, setExerciseTimeLeft] = useState(0);
  const [skippedExercises, setSkippedExercises] = useState(new Set());
  const [exerciseStatus, setExerciseStatus] = useState({});
  const [formFeedback, setFormFeedback] = useState(null); // { status: 'good'|'warning'|'tracking_lost', message: string|null }
  const [isDoneSession, setIsDoneSession] = useState(false);
  const [_completedExercisesCount, setCompletedExercisesCount] = useState(0); // tracks per-exercise progress for Dashboard
  const [mediaUrlIndex, setMediaUrlIndex] = useState(0);
  // Separate index for the active-session GIF so preview errors don't contaminate it
  const [sessionMediaUrlIndex, setSessionMediaUrlIndex] = useState(0);
  // Guide video fallback when media fails to load (unused placeholder deleted)

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

  const showConfirmDialog = (message, onConfirm) => {
    setConfirmDialog({ show: true, message, onConfirm });
  };

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

    let candidate = trimmed;
    if (candidate.startsWith('//')) {
      candidate = `https:${candidate}`;
    }

    // Convert giphy page URLs to direct media links.
    if (/^https?:\/\/giphy\.com\/gifs\//i.test(candidate)) {
      const slug = candidate.split('/').filter(Boolean).pop() || '';
      const gifId = slug.includes('-') ? slug.split('-').pop() : slug;
      if (gifId && gifId.length >= 5) {
        candidate = `https://media.giphy.com/media/${gifId}/giphy.gif`;
      }
    }

    try {
      const parsed = new URL(candidate);
      if (!['http:', 'https:'].includes(parsed.protocol)) return '';
      if (parsed.username || parsed.password) return '';
      return parsed.toString();
    } catch {
      return '';
    }
  };

  const getExerciseMediaCandidates = (exercise) => {
    if (!exercise) return [];
    const raw = [
      exercise.gif,
      exercise.video_url,
      exercise.videoUrl,
      exercise.image,
      exercise.thumbnail,
      exercise.media_url,
      exercise.mediaUrl,
      exercise.demo_url,
      exercise.demoUrl,
      exercise.Wger_Image_URL,
      exercise.wger_image_url,
      exercise.wgerImageUrl,
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

  // A plan is renderable if it has at least one day with exercises.
  // We intentionally DO NOT require GIF/media presence — exercises without
  // a GIF show a styled placeholder, which is valid and intentional.
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

  const parseDurationToSeconds = (value) => {
    const text = String(value ?? '').trim().toLowerCase();
    if (!text) return 0;

    const matches = text.match(/\d+/g) || [];
    const nums = matches.map((n) => parseInt(n, 10)).filter((n) => !Number.isNaN(n));
    if (nums.length === 0) return 0;

    const maxNum = Math.max(...nums);
    if (text.includes('min')) return maxNum * 60;
    if (text.includes('sec') || text.includes('second')) return maxNum;
    return 0;
  };

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

  const getExerciseDurationSeconds = (exercise) => {
    if (!exercise) return 0;

    const explicitDuration = Number(exercise.duration_seconds);
    if (Number.isFinite(explicitDuration) && explicitDuration > 0) {
      return Math.floor(explicitDuration);
    }

    const repsDuration = parseDurationToSeconds(exercise.reps);
    if (repsDuration > 0) return repsDuration;

    const fallbackDuration = parseDurationToSeconds(exercise.duration || exercise.time || '');
    return fallbackDuration > 0 ? fallbackDuration : 0;
  };

  const getExerciseStatusKey = (exercise) => {
    if (!exercise) return '';
    const name = String(exercise.name || '').trim();
    const sets = String(exercise.sets ?? '').trim();
    const reps = String(exercise.reps ?? '').trim();
    const warmup = exercise.is_warmup ? 'warmup' : 'main';
    return `${name}|${sets}|${reps}|${warmup}`;
  };

  const isPoseTrackableExercise = (exercise) => {
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
  };

  const exerciseNeedsCamera = (exercise) => {
    if (!exercise) return true;
    if (typeof exercise.needs_camera === 'boolean') return exercise.needs_camera;
    if (typeof exercise.needsCamera === 'boolean') return exercise.needsCamera;
    return isPoseTrackableExercise(exercise);
  };

  const isTimedExercise = (exercise) => {
    if (!exercise) return false;
    if (exercise.is_timed === true) return true;
    if (!exerciseNeedsCamera(exercise)) return true;
    return !isPoseTrackableExercise(exercise) && getExerciseDurationSeconds(exercise) > 0;
  };

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
        background: 'linear-gradient(145deg, #0f0f14 0%, #13131a 100%)',
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
          color: '#fff',
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
    console.warn(`Preview media failed at index ${mediaUrlIndex}. Trying next.`);
    setMediaUrlIndex((prev) => prev + 1);
  };

  const handleSessionMediaError = () => {
    console.warn(`Session media failed at index ${sessionMediaUrlIndex}. Trying next.`);
    setSessionMediaUrlIndex((prev) => prev + 1);
  };

  // Render media for the PREVIEW panel (before camera starts)
  const renderPreviewMedia = () => {
    if (activeExercise?.media_type === 'none') {
      return renderExerciseNoGifPlaceholder(activeExercise?.name);
    }
    const candidates = getExerciseMediaCandidates(activeExercise);
    const currentUrl = candidates[mediaUrlIndex] || '';
    if (!currentUrl) return renderExerciseNoGifPlaceholder(activeExercise?.name);
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
        <video key={currentUrl} autoPlay loop muted playsInline style={styles.gifLarge} onError={handleMediaError}>
          <source src={currentUrl} onError={handleMediaError} />
        </video>
      );
    }
    return (
      <img
        key={currentUrl}
        src={currentUrl}
        style={styles.gifLarge}
        alt={activeExercise?.name ? `${activeExercise.name} exercise guide` : 'Exercise guide'}
        onError={handleMediaError}
      />
    );
  };

  // Render media for the ACTIVE SESSION panel (camera-on). Uses its own index so
  // errors in the preview don't contaminate the session reference GIF.
  const renderSessionMedia = () => {
    if (activeExercise?.media_type === 'none') {
      return renderExerciseNoGifPlaceholder(activeExercise?.name);
    }
    const candidates = getExerciseMediaCandidates(activeExercise);
    const currentUrl = candidates[sessionMediaUrlIndex] || '';
    if (!currentUrl) return renderExerciseNoGifPlaceholder(activeExercise?.name);
    if (isYouTubeUrl(currentUrl)) {
      return (
        <iframe
          key={`session-${currentUrl}`}
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
        <video key={`session-${currentUrl}`} autoPlay loop muted playsInline style={styles.gifLarge} onError={handleSessionMediaError}>
          <source src={currentUrl} onError={handleSessionMediaError} />
        </video>
      );
    }
    return (
      <img
        key={`session-${currentUrl}`}
        src={currentUrl}
        style={{ ...styles.gifLarge, objectFit: 'contain' }}
        alt={activeExercise?.name ? `${activeExercise.name} form guide` : 'Form guide'}
        onError={handleSessionMediaError}
      />
    );
  };

  // Keep old name as alias so any remaining call sites still work (unused alias deleted)

  useEffect(() => {
    setMediaUrlIndex(0);
    setSessionMediaUrlIndex(0);
    if (activeExercise && isTimedExercise(activeExercise)) {
      setExerciseTimeLeft(getExerciseDurationSeconds(activeExercise) || 300);
    } else {
      setExerciseTimeLeft(0);
    }
  }, [activeExercise]);

  // Auto-clear posture feedback when entering rest period
  useEffect(() => {
    if (isResting) setFormFeedback(null);
  }, [isResting]);

  // Callback handler for structured posture feedback from PoseDetector
  const handleFormFeedback = useCallback((feedback) => {
    // PoseDetector now sends structured objects: { status, message }
    // Legacy string fallback for backward compatibility
    if (typeof feedback === 'string') {
      setFormFeedback({ status: 'warning', message: feedback });
    } else {
      setFormFeedback(feedback);
    }
  }, []);

  // Auto-dismiss the 'ready' overlay after 1.5s so it never blocks the camera feed
  useEffect(() => {
    if (poseLoadingStatus !== 'ready') return;
    const tid = setTimeout(() => setPoseLoadingStatus('done'), 1500);
    return () => clearTimeout(tid);
  }, [poseLoadingStatus]);

  useEffect(() => {
    const handleClickOutside = (event) => {
      if (notifRef.current && !notifRef.current.contains(event.target)) {
        setShowNotif(false);
      }
    };
    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  const saveLog = async (name, details) => {
    const newLog = {
      name: name,
      status: 'Completed',
      date: new Date().toISOString(),
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
      void videoRef.current.play().catch(() => { });
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

    let cancelWorkoutRequest = null; // Bug #63 fix: tracks cancel fn for in-flight generateWorkout

    const fetchWorkoutPlan = async (forceRefresh = false, profileData = null) => {
      let hydratedFromCache = false;
      try {
        if (isMounted) {
          setLoading(true);
          setError(null);
        }

        console.log('🏋️ Fetching workout plan...', forceRefresh ? '(Force Refresh)' : '(Cache Check)');

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
        let cachedPlan = sessionStorage.getItem('workoutPlan') || localStorage.getItem('workoutPlan');
        let cachedTimestamp = sessionStorage.getItem('workoutPlanTimestamp') || localStorage.getItem('workoutPlanTimestamp');
        const cachedVersion = localStorage.getItem('workoutPlanVersion');

        if (cachedPlan && cachedVersion !== WORKOUT_PLAN_CACHE_VERSION) {
          sessionStorage.removeItem('workoutPlan');
          sessionStorage.removeItem('workoutPlanTimestamp');
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
            sessionStorage.removeItem('workoutPlan');
            sessionStorage.removeItem('workoutPlanTimestamp');
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

        // **Fetch new plan from server using FULL profile data**
        console.log('🌐 Requesting workout plan from server...');

        let response;
        try {
          // Bug #63 fix: use { promise, cancel } API for AbortController support
          const workoutRequest = generateWorkout(userProfile);
          cancelWorkoutRequest = workoutRequest.cancel;
          response = await workoutRequest.promise;
          cancelWorkoutRequest = null; // clear on success
          if (!response) throw new Error('Workout request was cancelled');
          console.log('✅ Workout plan received:', response.data);
        } catch (err) {
          // Handle 429 rate-limit: fall back to cached plan or generate fallback
          if (err.response?.status === 429) {
            const retryAfter = err.response?.data?.retry_after || 10;
            console.warn(`⚠️ Rate limited by server (retry after ${retryAfter}s). Using cached plan or fallback.`);
            if (hydratedFromCache && isMounted) {
              setLoading(false);
              return; // already showing cached plan — no error needed
            }
            // No cache available — use fallback plan so the page doesn't stay blank
            console.warn('⚠️ No cache available after rate limit — using fallback plan');
            const fallback = createFallbackPlan();
            const normalizedFallback = normalizeWeeklyPlan(fallback);
            if (isMounted) {
              setPlan(normalizedFallback);
              setLoading(false);
            }
            return;
          }
          console.warn('⚠️ Workout request failed, will use cached plan if available:', err.message);
          throw err;
        }

        if (!response) {
          throw new Error('Failed to fetch workout plan');
        }

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
          sessionStorage.setItem('workoutPlan', JSON.stringify(normalizedPlan));
          sessionStorage.setItem('workoutPlanTimestamp', new Date().toISOString());
          localStorage.removeItem('workoutPlan');
          localStorage.removeItem('workoutPlanTimestamp');
          localStorage.setItem('workoutPlanVersion', WORKOUT_PLAN_CACHE_VERSION);
          sessionStorage.setItem(StorageKeys.WORKOUT_WEEK_METADATA, JSON.stringify(normalizedWeekMetadata));
          localStorage.removeItem(StorageKeys.WORKOUT_WEEK_METADATA);
          console.log('💾 Workout plan cached');
          console.log(`📊 Plan has ${normalizedPlan.length} days`);
        }
      } catch (err) {
        console.error('❌ Error fetching workout plan:', err);

        // Classify error for better user feedback
        let errorMessage = 'Failed to load workout plan';

        if (!err.response) {
          // Network error - backend not reachable
          errorMessage = 'Cannot connect to workout server. Please ensure the Python backend is running on port 8000.';
        } else if (err.response?.status === 404) {
          errorMessage = 'Workout endpoint not found. Backend may need updating.';
        } else if (err.response?.status === 500) {
          errorMessage = 'Backend error. Please check the server logs.';
        } else if (err.code === 'ECONNABORTED' || err.message?.includes('timeout')) {
          errorMessage = 'Request timed out. The backend is taking too long to respond.';
        } else if (err.response?.data?.detail) {
          errorMessage = err.response.data.detail;
        }

        if (isMounted) {
          if (hydratedFromCache) {
            // Cache is displayed — show a non-blocking warning
            showError(errorMessage, 5000);
          } else {
            // No cache — show error AND a fallback plan so the page is never blank
            setError(errorMessage);
            const fallback = createFallbackPlan();
            setPlan(normalizeWeeklyPlan(fallback));
          }
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

        const profileChanged = JSON.stringify(storedNormalized) !== JSON.stringify(currentNormalized);
        const cachedPlan = getFromStorage('workoutPlan', []);
        const hasLegacyDemoData = Array.isArray(cachedPlan) && cachedPlan.some((day) =>
          Array.isArray(day?.exercises) && day.exercises.some((ex) => String(ex?.id || '').startsWith('demo-bicep-'))
        );
        if (hasLegacyDemoData) {
          sessionStorage.removeItem('workoutPlan');
          sessionStorage.removeItem('workoutPlanTimestamp');
          localStorage.removeItem('workoutPlan');
          localStorage.removeItem('workoutPlanTimestamp');
          console.log('🧹 Removed legacy demo workout cache');
        }
        const hasCachedPlan = !!(sessionStorage.getItem('workoutPlan') || localStorage.getItem('workoutPlan'));

        console.log("🔍 Profile changed:", profileChanged);
        console.log("🔍 Has cached plan:", hasCachedPlan);
        console.log("📊 Profile comparison:", profileChanged ? 'CHANGED - Will fetch new plan' : 'UNCHANGED - Using cached plan');
        console.log("=".repeat(60) + "\n");

        if (!hasCachedPlan || profileChanged) {
          console.log("🔄 Fetching new workout plan...");
          // ✅ FIX: Pass the fresh profile to fetchWorkoutPlan
          await fetchWorkoutPlan(profileChanged, currentProfile);
          sessionStorage.setItem('workoutPlanProfile', JSON.stringify(currentNormalized));
          localStorage.removeItem('workoutPlanProfile');
          console.log("✅ New workout plan fetched and profile saved");
        } else {
          console.log("✅ Using cached workout plan");
          const cached = sessionStorage.getItem('workoutPlan') || localStorage.getItem('workoutPlan');
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
        setPastWorkouts(historyResponse.data || []);
      } catch (err) {
        console.error('Failed to fetch workout history:', err);
      }
    };

    checkAndFetchPlan();
    fetchHistory();

    // Cleanup function to prevent state updates on unmount
    // Bug #63 fix: also cancel any in-flight generateWorkout request
    return () => {
      isMounted = false;
      if (cancelWorkoutRequest) cancelWorkoutRequest();
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []); // Empty dependency - runs once on mount

  useEffect(() => {
    let timer;
    if (isResting && restTimeLeft > 0) {
      timer = setInterval(() => {
        setRestTimeLeft((prev) => prev - 1);
      }, 1000);
    } else if (isResting && restTimeLeft <= 0) {
      setIsResting(false);
      setCurrentSet((prev) => prev + 1);
      setCurrentReps(0);
      if (activeExercise && isTimedExercise(activeExercise)) {
        setExerciseTimeLeft(getExerciseDurationSeconds(activeExercise) || 300);
      }
    }
    return () => clearInterval(timer);
  }, [isResting, restTimeLeft, activeExercise]);

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

    if (exerciseTimeLeft > 0) {
      const timer = setInterval(() => {
        setExerciseTimeLeft((prev) => Math.max(0, prev - 1));
      }, 1000);
      return () => clearInterval(timer);
    }

    const targetSets = getTargetSets(activeExercise);
    if (currentSet >= targetSets) {
      handleExerciseComplete();
    } else {
      setRestTimeLeft(getRestSeconds(activeExercise));
      setIsResting(true);
    }

    return undefined;
  }, [isCameraOn, isResting, isDoneSession, activeExercise, exerciseTimeLeft, currentSet]);

  const toDayIndex = (value, fallback = 0) => {
    const parsed = Number(value);
    if (Number.isInteger(parsed) && parsed >= 0 && parsed <= 6) {
      return parsed;
    }
    return fallback;
  };

  const normalizeWeeklyPlan = (rawPlan = []) => {
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
  };

  const safePlan = Array.isArray(plan) ? plan : [];
  const todayIdx = getTodayIdx();

  // displayPlan is just the plan - backend handles swapping now
  const displayPlan = safePlan;
  const planByDayIndex = new Map(
    displayPlan.map((day, idx) => [toDayIndex(day?.day_of_week, idx), day])
  );
  const sortedDisplayPlan = [...displayPlan].sort(
    (a, b) => toDayIndex(a?.day_of_week, 0) - toDayIndex(b?.day_of_week, 0)
  );

  const completedIds = new Set(
    displayPlan
      .map((d, idx) => {
        const key = `workout_done_${d.day || `Day ${idx + 1}`}`;
        return getFromStorage(key) === 'true' ? (d.day_of_week ?? idx) : null;
      })
      .filter((v) => v !== null)
  );

  const swapHistory = Array.isArray(weekMetadata?.swap_history) ? weekMetadata.swap_history : [];
  const swapLimits = {
    max: Number(weekMetadata?.swap_limits?.max_swaps_per_week || 3),
    used: Number(weekMetadata?.swap_limits?.swaps_used || swapHistory.length || 0),
    remaining: Number(
      weekMetadata?.swap_limits?.swaps_remaining
      ?? Math.max(0, Number(weekMetadata?.swap_limits?.max_swaps_per_week || 3) - (swapHistory.length || 0))
    ),
  };

  const handleRestDayDecision = async () => {
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
          showSuccess('Swapping rest day...', 1500);

          const response = await swapRestToWorkout({
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
      const response = await swapWorkoutToRest({
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

  const handleDayClick = (dayIdx) => {
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
      setCompletedExercisesCount(0);
      setSkippedExercises(new Set());
      setExerciseStatus({});
    }
  };

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
  }, [autoStartDay, displayPlan, planByDayIndex]);

  const releaseCameraStream = () => {
    if (!stream) return;
    stream.getTracks().forEach((track) => track.stop());
    if (videoRef.current) {
      videoRef.current.srcObject = null;
    }
    setStream(null);
  };

  const getCameraErrorMessage = (error) => {
    const name = String(error?.name || '');
    if (name === 'NotAllowedError' || name === 'PermissionDeniedError') {
      return 'Camera permission denied. Please allow camera access in your browser settings.';
    }
    if (name === 'NotFoundError' || name === 'DevicesNotFoundError') {
      return 'No camera was found on this device.';
    }
    if (name === 'NotReadableError' || name === 'TrackStartError') {
      return 'The camera is already in use by another app or browser tab.';
    }
    return error?.message || 'Unable to start the camera.';
  };

  const ensureCameraStream = async () => {
    if (stream) return stream;
    try {
      const mediaStream = await navigator.mediaDevices.getUserMedia({
        video: { width: 640, height: 480, frameRate: { ideal: 30, max: 30 } },
      });
      setStream(mediaStream);
      setPoseTrackingError(null);
      return mediaStream;
    } catch (error) {
      const message = getCameraErrorMessage(error);
      setPoseTrackingError(message);
      showError(message, 5000);
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

    setPoseTrackingError(null);

    setCurrentSet(1);
    setCurrentReps(0);
    setIsResting(false);
    setFormFeedback(null);
    setIsDoneSession(false);
    if (isTimedExercise(activeExercise)) {
      setExerciseTimeLeft(getExerciseDurationSeconds(activeExercise) || 300);
    } else {
      setExerciseTimeLeft(0);
    }

    if (!exerciseNeedsCamera(activeExercise)) {
      setIsCameraOn(true);
      releaseCameraStream();
      return;
    }

    const mediaStream = await ensureCameraStream();
    if (!mediaStream) {
      setIsCameraOn(false);
      return;
    }

    setIsCameraOn(true);
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
      setExerciseTimeLeft(getExerciseDurationSeconds(ex) || 300);
    } else {
      setExerciseTimeLeft(0);
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
      setExerciseTimeLeft(getExerciseDurationSeconds(nextExercise) || 300);
    } else {
      setExerciseTimeLeft(0);
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
    await finishSession(skippedExercises.size > 0, {
      exerciseStatus: nextStatus,
      skippedExercises,
    });
  };

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

    const todayStr = new Date().toISOString().split('T')[0];
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
      if (currentSet >= targetSets) {
        handleExerciseComplete();
      } else {
        setRestTimeLeft(getRestSeconds(activeExercise));
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
        await saveLog(activeDay.focus || 'Workout', detail);
      } catch (err) {
        console.error("Workout history save failed:", err);
      }

      if (isPartialSession) {
        setToStorage(`workout_partial_${activeDay.day}`, 'true');
        setToStorage(`workout_skipped_${activeDay.day}`, JSON.stringify(skippedNames));
        setToStorage(StorageKeys.TODAY_WORKOUT_DONE, 'false');
      } else {
        setToStorage(`workout_done_${activeDay.day}`, 'true');
        setToStorage(StorageKeys.TODAY_WORKOUT_DONE, 'true');
      }

      try {
        await saveUserWorkoutToNode({
          dayName: activeDay.day,
          focus: activeDay.focus,
          exercises: activeDay.exercises.map(ex => ({
            name: ex.name,
            duration: ex.duration || "Custom"
          })),
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
        const todayStr = new Date().toISOString().split('T')[0];
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
        <style>{`
          @keyframes slideDown { from { opacity: 0; transform: translateY(-20px); } to { opacity: 1; transform: translateY(0); } }
          @keyframes fadeIn { from { opacity: 0; } to { opacity: 1; } }
          @keyframes slideInRight { from { transform: translateX(100%); } to { transform: translateX(0); } }
          .icon-hover:hover { background: rgba(255,255,255,0.1) !important; }
          .logout-btn:hover { background: rgba(239, 68, 68, 0.2) !important; transform: translateY(-2px); box-shadow: 0 4px 15px rgba(239, 68, 68, 0.2); }
          .active-card-pulse { animation: pulseBorder 2s infinite; }
          @keyframes pulseBorder { 0% { border-color: #6366f1; box-shadow: 0 0 0 0 rgba(99, 102, 241, 0.4); } 70% { border-color: #818cf8; box-shadow: 0 0 0 10px rgba(99, 102, 241, 0); } 100% { border-color: #6366f1; box-shadow: 0 0 0 0 rgba(99, 102, 241, 0); } }
          .ex-item:hover { transform: translateX(5px); background: rgba(255,255,255,0.06) !important; }
          .btn-stop:hover { background: rgba(239, 68, 68, 0.2) !important; }
          .btn-done:hover { transform: translateY(-2px); box-shadow: 0 8px 25px rgba(34, 197, 94, 0.5) !important; }
          .history-card:hover { border-color: #6366f1 !important; background: rgba(255,255,255,0.05) !important; }
        `}</style>

        {/* BUG-F3/F13: Replaced inline nav with shared Navbar component */}
        <Navbar
          navigate={navigate}
          activePage="workout"
          onLogout={handleLogout}
          rightContent={
            <>
              <div style={styles.dateDisplay}>{todayDate}</div>
              <button style={styles.iconButton} className="icon-hover" onClick={() => setShowHistory(!showHistory)} title="Past Workouts">🕒</button>
              <div style={{ position: 'relative' }} ref={notifRef}>
                <button style={styles.iconButton} className="icon-hover" onClick={() => setShowNotif(!showNotif)}>🔔</button>
                {showNotif && (
                  <div style={styles.notifDropdown}>
                    <div style={{ fontSize: '14px', fontWeight: '700', color: '#fff', marginBottom: '12px' }}>Notifications</div>
                    <div style={styles.notifItem}>🔥 You're on a 12-day streak!</div>
                    <div style={styles.notifItem}>🏋️ Leg Day today!</div>
                    <div style={{ ...styles.notifItem, borderBottom: 'none', color: '#a1a1aa', fontSize: '12px', justifyContent: 'center', marginTop: '8px' }}>No new alerts</div>
                  </div>
                )}
              </div>
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

        <div style={workoutLayout.container}>
          {!activeDay && (
            <>
              <h1 style={workoutLayout.h1}>Your Weekly Plan</h1>
              <div style={workoutLayout.grid}>
                {safePlan.length > 0 ? (
                  sortedDisplayPlan
                    .map((day, idx) => {
                      const dayIdx = toDayIndex(day.day_of_week, idx);
                      const isRest = isRestDay(day);
                      const isPlaceholder = !!day.is_placeholder;
                      const status = getDayStatus(day, todayIdx, completedIds);
                      const isToday = status === 'TODAY' || (status === 'REST' && dayIdx === todayIdx);

                      return (
                        <WorkoutDayCard
                          key={`${dayIdx}-${day.day || idx}`}
                          day={day}
                          dayIdx={dayIdx}
                          status={status}
                          isRest={isRest}
                          isPlaceholder={isPlaceholder}
                          isToday={isToday}
                          layout={workoutLayout}
                          styles={styles}
                          weekdayNames={weekdayNames}
                          onStartWorkout={handleDayClick}
                          onSwapToRest={openWorkoutToRestModal}
                          canSwapToRest={canSwapWorkoutToRest(dayIdx)}
                        />
                      );
                    })
                ) : (
                  <div style={{ gridColumn: '1 / -1', textAlign: 'center', padding: '40px', color: '#a1a1aa', fontSize: '16px' }}>
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
                        const status = exerciseStatus[key] || 'pending';
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
                                {isCompleted ? '✅' : isSkipped ? '⏭' : isWarmupSection ? '🔥' : '●'}
                              </span>
                              <div>
                                <div
                                  style={{
                                    color: isSkipped ? '#ef4444' : isWarmupSection ? '#f59e0b' : '#fff',
                                    fontWeight: '700',
                                    fontSize: '14px',
                                  }}
                                >
                                  {exercise.name}
                                  {isSkipped && <span style={{ fontSize: '11px', marginLeft: '8px' }}>(Skipped)</span>}
                                </div>
                                <div style={{ color: '#a1a1aa', fontSize: '12px' }}>
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
                        <div style={{ fontSize: '32px', fontWeight: '800', color: '#fff', marginBottom: '10px' }}>{activeExercise.name}</div>
                        <div style={{ fontSize: '16px', color: '#a5b4fc', marginBottom: '30px', fontFamily: 'monospace' }}>
                          {activeExerciseTimed
                            ? `${activeExerciseTargetSets} SETS x ${formatDurationClock(activeExerciseDuration)} TIMER`
                            : `${activeExercise.sets} SETS x ${activeExercise.reps} REPS`}
                        </div>
                        <div style={{ ...styles.gifLargeContainer, ...workoutLayout.previewMedia }}>
                          {renderPreviewMedia()}
                        </div>
                        <button style={styles.btnStartLarge} onClick={startCamera}>
                          {exerciseNeedsCamera(activeExercise) ? 'START AI CAMERA' : 'START TIMER MODE'}
                        </button>
                      </>
                    ) : (
                      <>
                        <div style={{ fontSize: '60px', marginBottom: '20px' }}>👈</div>
                        <div style={{ fontSize: '18px', fontWeight: '600' }}>Select an exercise from the left to begin</div>
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
                            <span style={{ color: '#fff' }}>SET {currentSet} OF {activeExerciseTargetSets}</span> • <span style={{ color: '#22c55e' }}>{formatDurationClock(exerciseTimeLeft)} LEFT</span>
                          </>
                        ) : (
                          <>
                            <span style={{ color: '#fff' }}>SET {currentSet} OF {activeExercise.sets}</span> • <span style={{ color: '#22c55e' }}>{currentReps} / {activeExercise.reps} REPS</span>
                          </>
                        )}
                      </div>
                    ) : (
                      <div style={{ ...styles.activeExStats, color: '#f59e0b', fontSize: '24px' }}>
                        RESTING: {restTimeLeft}s
                      </div>
                    )}

                    {formFeedback?.status === 'warning' && formFeedback?.message && !isResting && activeExercisePoseTrackable && (
                      <div style={{ background: 'rgba(239, 68, 68, 0.2)', color: '#ef4444', padding: '10px', borderRadius: '8px', marginBottom: '15px', fontWeight: 'bold', fontSize: '14px' }}>
                        ⚠️ {formFeedback.message}
                      </div>
                    )}
                    {formFeedback?.status === 'tracking_lost' && !isResting && activeExercisePoseTrackable && (
                      <div style={{ background: 'rgba(245, 158, 11, 0.15)', color: '#f59e0b', padding: '10px', borderRadius: '8px', marginBottom: '15px', fontWeight: 'bold', fontSize: '14px' }}>
                        ⚠ {formFeedback.message || 'Camera tracking lost'}
                      </div>
                    )}

                    <div style={{
                      ...styles.gifLargeContainer,
                      border: '2px solid rgba(99,102,241,0.35)',
                      boxShadow: '0 0 20px rgba(99,102,241,0.1)',
                      minHeight: '180px',
                    }}>
                      <div style={{
                        position: 'absolute', top: 10, left: 10, zIndex: 5,
                        background: 'linear-gradient(90deg,#6366f1,#818cf8)',
                        padding: '4px 12px', borderRadius: '20px',
                        fontSize: '11px', fontWeight: '800', color: 'white',
                        letterSpacing: '0.5px', textTransform: 'uppercase',
                        boxShadow: '0 2px 8px rgba(99,102,241,0.4)',
                      }}>📹 FORM GUIDE</div>
                      {renderSessionMedia()}
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
                        <div style={{ position: 'absolute', top: 20, left: 20, zIndex: 25, display: 'flex', flexDirection: 'column', gap: '10px' }}>
                          {!isResting && (
                            <div style={{ background: 'rgba(0,0,0,0.8)', padding: '10px 20px', borderRadius: '12px', border: '2px solid #3f3f46' }}>
                              <div style={{ color: '#a1a1aa', fontSize: '14px', fontWeight: 'bold' }}>SET {currentSet} OF {activeExerciseTargetSets}</div>
                              {activeExerciseTimed ? (
                                <div style={{ color: '#22c55e', fontSize: '48px', fontWeight: '900', lineHeight: '1' }}>{formatDurationClock(exerciseTimeLeft)}</div>
                              ) : (
                                <div style={{ color: '#22c55e', fontSize: '48px', fontWeight: '900', lineHeight: '1' }}>{currentReps} <span style={{ fontSize: '24px', color: '#fff' }}>/ {getTargetReps(activeExercise)}</span></div>
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
                            animation: 'fadeIn 0.3s ease-out',
                          }}>
                            <div style={{ fontSize: '32px', marginBottom: '8px' }}>✅</div>
                            AI Pose Ready!
                            <div style={{ fontSize: '13px', fontWeight: '500', marginTop: '8px', opacity: 0.8 }}>
                              Start moving — your reps will be counted!
                            </div>
                          </div>
                        )}
                        {/* Dynamic posture feedback overlay — tri-state: Good / Warning / Tracking Lost */}
                        {/* Replaces old static 'Pose AI Active' badge AND old static 'INCORRECT POSTURE' overlay */}
                        {poseLoadingStatus === 'done' && activeExercisePoseTrackable && !isResting && (() => {
                          const status = formFeedback?.status || 'good';
                          const message = formFeedback?.message;
                          const isWarning = status === 'warning' && message;
                          const isTrackingLost = status === 'tracking_lost';

                          if (isWarning) {
                            return (
                              <div style={{
                                position: 'absolute',
                                top: '50%',
                                left: '50%',
                                transform: 'translate(-50%, -50%)',
                                background: 'rgba(239, 68, 68, 0.92)',
                                color: '#fff',
                                padding: '18px 36px',
                                borderRadius: '16px',
                                zIndex: 30,
                                fontWeight: '900',
                                fontSize: '24px',
                                textAlign: 'center',
                                border: '3px solid rgba(255,255,255,0.8)',
                                boxShadow: '0 20px 40px rgba(0,0,0,0.5)',
                                transition: 'all 0.4s ease',
                                maxWidth: '80%',
                              }}>
                                ⚠️ INCORRECT POSTURE<br />
                                <span style={{ fontSize: '16px', fontWeight: '500', opacity: 0.9 }}>{message}</span>
                              </div>
                            );
                          }

                          if (isTrackingLost) {
                            return (
                              <div style={{
                                position: 'absolute',
                                bottom: 60,
                                left: '50%',
                                transform: 'translateX(-50%)',
                                zIndex: 26,
                                background: 'rgba(245, 158, 11, 0.2)',
                                border: '1px solid rgba(245, 158, 11, 0.5)',
                                borderRadius: '20px',
                                padding: '8px 18px',
                                color: '#fbbf24',
                                fontSize: '13px',
                                fontWeight: '700',
                                letterSpacing: '0.5px',
                                textTransform: 'uppercase',
                                transition: 'all 0.4s ease',
                              }}>
                                ⚠ Camera Tracking Lost — Stay in Frame
                              </div>
                            );
                          }

                          // Good form badge
                          return (
                            <div style={{
                              position: 'absolute',
                              bottom: 60,
                              left: '50%',
                              transform: 'translateX(-50%)',
                              zIndex: 26,
                              background: 'rgba(34,197,94,0.15)',
                              border: '1px solid rgba(34,197,94,0.4)',
                              borderRadius: '20px',
                              padding: '6px 16px',
                              color: '#4ade80',
                              fontSize: '12px',
                              fontWeight: '700',
                              letterSpacing: '0.5px',
                              textTransform: 'uppercase',
                              transition: 'all 0.4s ease',
                            }}>
                              ✅ Good Form
                            </div>
                          );
                        })()}

                        {isCameraOn && activeExercisePoseTrackable && (
                          <PoseDetector
                            videoRef={videoRef}
                            isActive={isCameraOn && !isResting}
                            exerciseName={activeExercise?.name || ''}
                            onRepUpdate={handleRepUpdate}
                            onFormFeedback={handleFormFeedback}
                            onLoadingChange={setPoseLoadingStatus}
                            resetKey={currentSet}  // Reset internal rep counter on each new set
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
                          <div style={styles.recBadge}><div style={{ width: 10, height: 10, background: 'white', borderRadius: '50%', animation: 'pulseBorder 1s infinite' }}></div>REC</div>
                        )}

                        {activeExerciseNeedsCamera && isResting && (
                          <div style={{ position: 'absolute', top: 0, left: 0, width: '100%', height: '100%', background: 'rgba(0,0,0,0.8)', display: 'flex', alignItems: 'center', justifyContent: 'center', flexDirection: 'column', zIndex: 30 }}>
                            <div style={{ fontSize: '32px', color: '#a1a1aa', marginBottom: '10px', fontWeight: '800' }}>RECOVERY TIME</div>
                            <div style={{ fontSize: '100px', fontWeight: '900', color: '#f59e0b' }}>{restTimeLeft}</div>
                            <div style={{ fontSize: '18px', color: '#fff', marginTop: '20px' }}>Next: Set {currentSet + 1} of {activeExercise.name}</div>
                            <button onClick={() => setRestTimeLeft(0)} style={{ marginTop: '30px', background: '#3f3f46', border: 'none', color: 'white', padding: '10px 20px', borderRadius: '8px', cursor: 'pointer', fontWeight: 'bold' }}>Skip Rest</button>
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
                background: '#18181b',
                border: '1px solid rgba(255,255,255,0.12)',
                borderRadius: '16px',
                padding: '20px',
                boxShadow: '0 25px 50px rgba(0,0,0,0.45)',
              }}
            >
              <div style={{ fontSize: '18px', fontWeight: '800', color: '#fff', marginBottom: '8px' }}>
                Move Workout To A Future Rest Day
              </div>
              <div style={{ color: '#a1a1aa', fontSize: '13px', marginBottom: '16px' }}>
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
                        border: isSelected ? '1px solid #6366f1' : '1px solid rgba(255,255,255,0.12)',
                        background: isSelected ? 'rgba(99, 102, 241, 0.18)' : 'rgba(255,255,255,0.03)',
                        color: '#fff',
                        cursor: 'pointer',
                      }}
                    >
                      <div style={{ fontWeight: '700', fontSize: '14px' }}>{weekdayNames[idx] || day?.day || `Day ${idx + 1}`}</div>
                      <div style={{ fontSize: '12px', color: '#a1a1aa' }}>Current: Rest Day</div>
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
                    border: '1px solid rgba(255,255,255,0.2)',
                    background: 'transparent',
                    color: '#d4d4d8',
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
                    background: selectedTargetRestDayIndex == null ? '#3f3f46' : '#6366f1',
                    color: '#fff',
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
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '24px' }}>
              <div style={{ fontSize: '20px', fontWeight: '800', color: '#fff' }}>History</div>
              <button onClick={() => setShowHistory(false)} style={{ background: 'none', border: 'none', color: '#fff', fontSize: '20px', cursor: 'pointer' }}>✕</button>
            </div>

            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '8px', marginBottom: '16px' }}>
              <button
                onClick={() => setHistoryTab('workout')}
                style={{
                  padding: '10px 12px',
                  borderRadius: '10px',
                  border: historyTab === 'workout' ? '1px solid #6366f1' : '1px solid rgba(255,255,255,0.12)',
                  background: historyTab === 'workout' ? 'rgba(99,102,241,0.18)' : 'rgba(255,255,255,0.03)',
                  color: '#fff',
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
                  border: historyTab === 'swap' ? '1px solid #f59e0b' : '1px solid rgba(255,255,255,0.12)',
                  background: historyTab === 'swap' ? 'rgba(245,158,11,0.15)' : 'rgba(255,255,255,0.03)',
                  color: '#fff',
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
                      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                        <div style={styles.historyDate}>{day.date || new Date().toLocaleDateString()}</div>
                        <div style={{ fontSize: '12px', fontWeight: '700', color: day.status === 'Completed' ? '#22c55e' : '#ef4444' }}>{day.status || 'Completed'}</div>
                      </div>
                      {selectedHistory === i && day.details && (
                        <div style={{ marginTop: '15px', paddingTop: '15px', borderTop: '1px solid rgba(255,255,255,0.1)' }}>
                          <div style={styles.historyLabel}>Details:</div>
                          <div style={styles.historyList}>
                            <div style={{ marginBottom: '4px' }}>{day.details}</div>
                          </div>
                        </div>
                      )}
                    </div>
                  ))
                ) : (
                  <div style={{ textAlign: 'center', padding: '40px', color: '#52525b' }}>No workout history yet</div>
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
                  <div style={{ fontSize: '13px', color: '#f4f4f5' }}>
                    Used: {swapLimits.used} / {swapLimits.max}
                  </div>
                  <div style={{ fontSize: '12px', color: '#a1a1aa', marginTop: '2px' }}>
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
                          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '8px' }}>
                            <div style={{ ...styles.historyDate, marginBottom: 0 }}>
                              {isRestToWorkout ? 'Rest -> Workout' : 'Workout -> Rest'}
                            </div>
                            <div style={{ fontSize: '11px', color: '#a1a1aa' }}>{formatSwapTimestamp(entry?.timestamp)}</div>
                          </div>
                          <div style={{ fontSize: '13px', color: '#e4e4e7', marginBottom: '6px' }}>
                            {`${fromLabel} -> ${toLabel}`}
                          </div>
                          <div style={{ fontSize: '12px', color: '#a1a1aa' }}>
                            Focus: {entry?.workout_focus || 'Workout'}
                          </div>
                        </div>
                      );
                    })
                ) : (
                  <div style={{ textAlign: 'center', padding: '40px', color: '#52525b' }}>No swaps recorded this week</div>
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
    </>
  );
}

export default Workout;