import { getLocalDateStr } from '../../utils/storage';

export const weekdayNames = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'];
export const WORKOUT_PLAN_CACHE_VERSION = '2026-06-29-muscle-groups-weekly-cache';
export const DEFAULT_FALLBACK_GIF = '';

export const getTodayIdx = () => {
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

export const getMuscleTagStyle = (muscle) => {
  const m = (muscle || '').toLowerCase();
  if (m === 'chest') return { bg: 'rgba(239,68,68,0.15)', text: '#f87171', border: 'rgba(239,68,68,0.3)' };
  if (m === 'back') return { bg: 'rgba(59,130,246,0.15)', text: '#60a5fa', border: 'rgba(59,130,246,0.3)' };
  if (m === 'legs') return { bg: 'rgba(16,185,129,0.15)', text: '#34d399', border: 'rgba(16,185,129,0.3)' };
  if (m === 'shoulders') return { bg: 'rgba(245,158,11,0.15)', text: '#fbbf24', border: 'rgba(245,158,11,0.3)' };
  if (m === 'arms') return { bg: 'rgba(168,85,247,0.15)', text: '#c084fc', border: 'rgba(168,85,247,0.3)' };
  if (m === 'core') return { bg: 'rgba(236,72,153,0.15)', text: '#f472b6', border: 'rgba(236,72,153,0.3)' };
  return { bg: 'rgba(113,113,122,0.15)', text: 'var(--app-text-muted)', border: 'rgba(113,113,122,0.3)' };
};

export const getDisplayFocus = (focus) => {
  if (!focus) return 'Workout';
  const match = focus.match(/Full Body \((.+)\)/);
  if (match) return match[1];
  return focus;
};

export const isRestDay = (day) => {
  if (!day || day.is_placeholder) return false;
  if (day.type === 'rest') return true;
  const focus = `${day.focus || ''}`.toLowerCase();
  if (focus.includes('rest') || focus === 'active recovery') return true;
  const label = `${day.day || ''}`.toLowerCase();
  const note = `${day.note || ''}`.toLowerCase();
  if (label.includes('rest') || note.includes('rest') || note.includes('recovery')) return true;
  const exercises = day.exercises || [];
  if (exercises.length === 0 && day.type !== 'workout') return true;
  return false;
};

export const getDayStatus = (day, todayIdx, completedIds = new Set()) => {
  if (day?.is_placeholder && day?.type === 'past') return 'NOT_STARTED';
  if (day?.is_placeholder) return 'NO PLAN';
  if (isRestDay(day)) return 'REST';
  if (day.type === 'past') return 'NOT_STARTED';
  const dow = day.day_of_week ?? 0;
  if (completedIds.has(dow)) return 'COMPLETED';
  if (dow === todayIdx) return 'TODAY';
  if (dow < todayIdx) return 'PAST';
  return 'UPCOMING';
};

export const findNextWorkoutDayIndex = (plan, todayIdx) => {
  const safe = Array.isArray(plan) ? plan : [];
  for (let idx = todayIdx + 1; idx <= 6; idx += 1) {
    const day = safe[idx];
    if (day && !day.is_placeholder && !isRestDay(day)) return idx;
  }
  return null;
};

export const getFutureOriginalRestDays = (plan, sourceDayIdx, todayIdx) => {
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

export const getWeekStartDateIso = () => {
  const now = new Date();
  const day = now.getDay();
  const mondayOffset = day === 0 ? -6 : 1 - day;
  const monday = new Date(now);
  monday.setDate(now.getDate() + mondayOffset);
  return getLocalDateStr(monday);
};

export const buildWeekMetadataFromPlan = (weeklyPlan = [], existingMetadata = null) => {
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
  const swapsUsed = typeof existingSwapLimits.swaps_used === 'number' ? existingSwapLimits.swaps_used : existingSwapHistory.length;

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

export const formatSwapTimestamp = (value) => {
  if (!value) return 'Unknown time';
  const parsed = new Date(value);
  if (Number.isNaN(parsed.getTime())) return String(value);
  return parsed.toLocaleString();
};

export const getTargetSets = (exercise) => {
  if (!exercise) return 1;
  const parsedSets = parseInt(String(exercise.sets ?? '1').replace(/[^0-9]/g, ''), 10);
  if (!Number.isNaN(parsedSets) && parsedSets > 0) return parsedSets;
  return 1;
};

export const getTargetReps = (exercise) => {
  if (!exercise) return 10;
  let text = String(exercise.reps ?? '10');
  if (text.includes('-')) text = text.split('-')[1];
  const parsedReps = parseInt(text.replace(/[^0-9]/g, ''), 10);
  if (!Number.isNaN(parsedReps) && parsedReps > 0) return parsedReps;
  return 10;
};

export const getRestSeconds = (exercise) => {
  if (!exercise) return 60;
  const parsedRest = parseInt(String(exercise.rest ?? '60').replace(/[^0-9]/g, ''), 10);
  if (!Number.isNaN(parsedRest) && parsedRest > 0) return parsedRest;
  return 60;
};

export const getExerciseStatusKey = (exercise) => {
  if (!exercise) return '';
  const name = String(exercise.name || '').trim();
  const sets = String(exercise.sets ?? '').trim();
  const reps = String(exercise.reps ?? '').trim();
  const warmup = exercise.is_warmup ? 'warmup' : 'main';
  return `${name}|${sets}|${reps}|${warmup}`;
};

export const formatDurationClock = (seconds) => {
  const safe = Math.max(0, Number(seconds) || 0);
  const mins = Math.floor(safe / 60);
  const secs = safe % 60;
  return `${String(mins).padStart(2, '0')}:${String(secs).padStart(2, '0')}`;
};
