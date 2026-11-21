import { getLocalDateStr, safeJSONParse } from '../../utils/storage';

export const NUTRITION_WEEKDAYS = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"];

export const getTodayIdxIST = () => {
  const weekday = new Intl.DateTimeFormat('en-US', {
    timeZone: 'Asia/Kolkata',
    weekday: 'short',
  }).format(new Date());
  const indexByWeekday = { Mon: 0, Tue: 1, Wed: 2, Thu: 3, Fri: 4, Sat: 5, Sun: 6 };
  return indexByWeekday[weekday] ?? 0;
};

// Returns the 7 'YYYY-MM-DD' dates for the current ISO week, Monday→Sunday.
// Uses pure UTC calendar arithmetic anchored on today's IST date so the result
// never drifts across timezones, and guarantees week[todayIdx] === today (IST).
export const getWeekDatesIST = () => {
  const todayStr = getLocalDateStr(); // IST 'YYYY-MM-DD'
  const [y, m, d] = todayStr.split('-').map(Number);
  const todayIdx = getTodayIdxIST();
  const base = new Date(Date.UTC(y, m - 1, d));
  const pad = (n) => String(n).padStart(2, '0');
  const dates = [];
  for (let i = 0; i < 7; i++) {
    const dt = new Date(base);
    dt.setUTCDate(base.getUTCDate() + (i - todayIdx));
    dates.push(`${dt.getUTCFullYear()}-${pad(dt.getUTCMonth() + 1)}-${pad(dt.getUTCDate())}`);
  }
  return dates;
};

export const getTodayWorkoutIntensity = (workoutPlan = []) => {
  if (!Array.isArray(workoutPlan) || workoutPlan.length === 0) return "moderate";

  const jsDay = new Date().getDay();
  const todayIdx = (jsDay + 6) % 7; // Monday=0 ... Sunday=6
  const todayPlan = workoutPlan.find((d) => (d?.day_of_week ?? -1) === todayIdx) || workoutPlan[todayIdx];

  if (!todayPlan) return "moderate";
  const label = `${todayPlan.day || todayPlan.focus || ""}`.toLowerCase();
  const note = `${todayPlan.note || ""}`.toLowerCase();
  if (label.includes("rest") || note.includes("rest")) return "rest";

  const exercises = Array.isArray(todayPlan.exercises) ? todayPlan.exercises : [];
  const totalSets = exercises.reduce((sum, ex) => {
    const parsed = parseInt(String(ex?.sets ?? "0").replace(/[^0-9]/g, ""), 10);
    return sum + (Number.isFinite(parsed) ? parsed : 0);
  }, 0);

  if (exercises.length >= 8 || totalSets >= 28) return "very_hard";
  if (exercises.length >= 6 || totalSets >= 20) return "hard";
  if (exercises.length >= 3 || totalSets >= 10) return "moderate";
  return "light";
};

export const isTodayRestDay = () => {
  try {
    const workoutPlan = safeJSONParse("workoutPlan", []);
    if (!Array.isArray(workoutPlan) || workoutPlan.length === 0) return false;

    const jsDay = new Date().getDay();
    const todayIdx = (jsDay + 6) % 7;
    const todayPlan = workoutPlan.find((d) => (d?.day_of_week ?? -1) === todayIdx) || workoutPlan[todayIdx];
    if (!todayPlan) return false;
    if (todayPlan.type === 'rest') return true;
    const focus = `${todayPlan.focus || ""}`.toLowerCase();
    if (focus.includes('rest') || focus === 'active recovery') return true;
    const label = `${todayPlan.day || ""}`.toLowerCase();
    const note = `${todayPlan.note || ""}`.toLowerCase();
    if (label.includes('rest') || note.includes('rest') || note.includes('recovery')) return true;
    return false;
  } catch {
    return false;
  }
};
