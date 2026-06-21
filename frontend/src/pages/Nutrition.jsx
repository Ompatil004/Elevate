import React, { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { useNotification } from "../components/NotificationProvider";
import { useTheme } from "../context/ThemeContext";
import { getProfile, generateNutritionPlan, getNutritionSwapOptions, generateWorkout, saveUserMealToNode, getMealHistory, saveMealHistory, saveTrends } from "../api";
import { StorageKeys, getFromStorage, setToStorage, logoutSafe, getLocalDateStr, safeJSONParse } from "../utils/storage";
import ConfirmDialog from "../components/ConfirmDialog";
import { syncBridge, SyncTypes } from "../utils/syncBridge";
import AuroraBackground from "../components/AuroraBackground";

// Local-timezone date string helper is now imported from storage.js

const styles = {
  page: { background: "transparent", minHeight: "100dvh", color: "var(--app-text)", fontFamily: "'Inter', sans-serif", overflowX: "hidden", position: "relative", zIndex: 1, paddingTop: "clamp(64px, 9vw, 80px)" },
  navbar: { display: "flex", alignItems: "center", padding: "0 clamp(12px, 4vw, 40px)", height: "clamp(64px, 9vw, 80px)", gap: "clamp(8px, 2vw, 18px)", borderBottom: "1px solid var(--app-border)", background: 'var(--app-nav-bg, rgba(9, 9, 11, 0.6))', backdropFilter: "blur(16px)", position: "fixed", top: 0, left: 0, right: 0, zIndex: 1000, overflowX: "auto" },
  brand: { flex: 1, fontSize: "22px", fontWeight: "900", letterSpacing: "-1px", background: "var(--brand-grad, linear-gradient(to right, #ffffff, #a5b4fc))", WebkitBackgroundClip: "text", WebkitTextFillColor: "transparent", display: "flex", alignItems: "center", gap: "10px" },
  navCenter: { display: "flex", gap: "clamp(4px, 1.5vw, 8px)", height: "100%", alignItems: "center", justifyContent: "center" },
  navLink: { display: "flex", alignItems: "center", padding: "8px clamp(10px, 2vw, 20px)", fontSize: "clamp(11px, 1.7vw, 13px)", fontWeight: "600", color: "var(--app-text-muted)", cursor: "pointer", borderRadius: "20px", transition: "all 0.2s", textTransform: "uppercase", letterSpacing: "0.5px", border: "1px solid transparent" },
  navLinkActive: { background: "var(--app-border)", color: "var(--app-text)", boxShadow: "0 0 20px var(--app-border)", border: "1px solid var(--app-border)" },
  navRight: { flex: 1, display: "flex", alignItems: "center", gap: "clamp(8px, 2vw, 24px)", justifyContent: "flex-end" },
  brandDot: { width: "8px", height: "8px", background: "#6366f1", borderRadius: "50%", boxShadow: "0 0 15px #6366f1" },
  iconButton: { width: "clamp(36px, 6vw, 42px)", height: "clamp(36px, 6vw, 42px)", borderRadius: "12px", background: "var(--quote-bg)", border: "1px solid var(--app-border)", color: "var(--app-text)", display: "flex", alignItems: "center", justifyContent: "center", cursor: "pointer", fontSize: "18px", transition: "all 0.2s" },
  logoutBtn: { display: "flex", alignItems: "center", gap: "8px", padding: "0 clamp(10px, 2vw, 20px)", borderRadius: "12px", background: "rgba(239, 68, 68, 0.1)", border: "1px solid rgba(239, 68, 68, 0.2)", color: "#ef4444", cursor: "pointer", transition: "all 0.2s ease", height: "clamp(36px, 6vw, 42px)" },
  logoutText: { fontSize: "12px", fontWeight: "700", letterSpacing: "0.5px", textTransform: "uppercase" },
  container: { maxWidth: "1400px", margin: "0 auto", padding: "clamp(12px, 4vw, 40px)" },
  header: { fontSize: "clamp(28px, 5vw, 42px)", fontWeight: "800", color: "var(--app-text)", marginBottom: "clamp(18px, 3vw, 40px)", letterSpacing: "-1px", background: "var(--h1-grad)", WebkitBackgroundClip: "text", WebkitTextFillColor: "transparent", filter: "drop-shadow(0 4px 20px rgba(99, 102, 241, 0.3))" },
  daySelectorBar: { display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(90px, 1fr))", gap: "10px", marginBottom: "20px" },
  dayCard: { background: "var(--app-surface)", border: "1px solid var(--app-border)", borderRadius: "16px", padding: "clamp(8px, 1.8vw, 12px)", cursor: "pointer", transition: "all 0.3s ease", textAlign: "center", position: "relative", overflow: "hidden" },
  dayCardSelected: { background: 'var(--day-card-selected-bg, linear-gradient(145deg, #1e1b4b 0%, #312e81 100%))', border: "2px solid #6366f1", transform: "scale(1.05)", boxShadow: "0 0 30px rgba(99, 102, 241, 0.2)" },
  dayCardToday: { borderColor: "#10b981", boxShadow: "0 0 15px rgba(16, 185, 129, 0.15)" },
  dayName: { fontSize: "12px", fontWeight: "700", color: "var(--app-text-muted)", marginBottom: "4px", textTransform: "uppercase", letterSpacing: "1px" },
  dailySummaryCard: { background: "var(--app-surface)", borderRadius: "20px", padding: "clamp(12px, 2vw, 20px)", marginBottom: "20px", border: "1px solid var(--app-border)", display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(130px, 1fr))", gap: "clamp(10px, 2vw, 16px)", position: "relative", overflow: "hidden" },
  macroStat: { textAlign: "center", padding: "10px", borderRadius: "14px", background: 'var(--app-surface-hover, rgba(255,255,255,0.02))', border: "1px solid rgba(255,255,255,0.04)", transition: "all 0.2s ease" },
  macroValue: { fontSize: "clamp(18px, 3vw, 26px)", fontWeight: "800", color: "var(--app-text)", marginBottom: "2px", fontFamily: "'Inter', sans-serif" },
  macroLabel: { fontSize: "11px", color: "#71717a", textTransform: "uppercase", letterSpacing: "0.5px", fontWeight: "700" },
  mealList: { display: "grid", gap: "20px" },
  mealCard: { background: "var(--app-surface)", borderRadius: "20px", padding: "clamp(14px, 2.8vw, 28px)", border: "1px solid var(--app-border)", transition: "all 0.3s ease", position: "relative", overflowX: "auto", overflowY: "hidden" },
  mealCardCompleted: { border: "1px solid rgba(34, 197, 94, 0.4)", background: "var(--app-card-bg)" },
  completedBadge: { position: "absolute", top: "15px", right: "15px", background: "rgba(34, 197, 94, 0.1)", color: "#22c55e", padding: "6px 14px", borderRadius: "20px", fontSize: "11px", fontWeight: "800", border: "1px solid rgba(34, 197, 94, 0.3)" },
  mealHeader: { display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "20px", paddingBottom: "16px", borderBottom: '1px solid var(--app-border)', gap: "12px", flexWrap: "wrap" },
  mealName: { fontSize: "20px", fontWeight: "800", color: "var(--app-text)", letterSpacing: "-0.5px" },
  foodTableHeader: { display: "grid", gridTemplateColumns: "30px minmax(140px, 2fr) minmax(80px, 1fr) repeat(4, minmax(54px, 1fr)) 44px", gap: "10px", minWidth: "660px", padding: "0 16px 12px", fontSize: "11px", fontWeight: "700", color: "#52525b", textTransform: "uppercase", letterSpacing: "1px" },
  foodList: { display: "grid", gap: "8px" },
  foodItemRow: { display: "grid", gridTemplateColumns: "30px minmax(140px, 2fr) minmax(80px, 1fr) repeat(4, minmax(54px, 1fr)) 44px", gap: "10px", minWidth: "660px", padding: "14px 16px", background: 'var(--app-surface-hover, rgba(255,255,255,0.02))', borderRadius: "14px", alignItems: "center", fontSize: "14px", border: '1px solid var(--app-border)', transition: "all 0.2s ease" },
  checkbox: { width: "22px", height: "22px", borderRadius: "8px", border: "2px solid var(--app-border)", cursor: "pointer", display: "flex", alignItems: "center", justifyContent: "center", transition: "all 0.2s", background: "transparent", fontSize: "12px" },
  checkboxChecked: { background: "linear-gradient(135deg, #22c55e 0%, #16a34a 100%)", borderColor: "#22c55e", boxShadow: "0 0 10px rgba(34, 197, 94, 0.3)", color: "#ffffff" },
  swapBtn: { background: "rgba(99, 102, 241, 0.1)", border: "1px solid rgba(99, 102, 241, 0.2)", color: "#818cf8", cursor: "pointer", fontSize: "16px", padding: "6px", borderRadius: "10px", transition: "all 0.2s", width: "34px", height: "34px", display: "flex", alignItems: "center", justifyContent: "center" },
  mealMacroTotal: { display: "flex", justifyContent: "flex-end", gap: "24px", marginTop: "16px", paddingTop: "16px", borderTop: '1px solid var(--app-border)', flexWrap: "wrap" },
  historyPanel: { position: "fixed", top: "80px", right: "0", width: "min(96vw, 480px)", height: "calc(100dvh - 80px)", background: "var(--app-bg)", borderLeft: "1px solid var(--app-border)", zIndex: 1500, padding: "clamp(14px, 2.5vw, 24px)", overflowY: "auto", animation: "slideInRight 0.3s ease-out", boxShadow: "-20px 0 50px rgba(0,0,0,0.5)" },
  swapModal: { position: "fixed", top: 0, left: 0, width: "100%", height: "100%", background: "rgba(0,0,0,0.75)", backdropFilter: "blur(12px)", zIndex: 3000, display: "flex", alignItems: "center", justifyContent: "center", transition: "opacity 0.3s ease" },
  swapModalCard: { background: "var(--app-surface)", padding: "clamp(16px, 3vw, 32px)", borderRadius: "24px", width: "min(96vw, 480px)", maxWidth: "480px", border: "1px solid rgba(99, 102, 241, 0.2)", boxShadow: "0 20px 60px rgba(0,0,0,0.6), 0 0 40px rgba(99, 102, 241, 0.1)", animation: "scaleIn 0.3s ease-out", maxHeight: "84dvh", display: "flex", flexDirection: "column" },
  optionalBadge: { background: "rgba(245, 158, 11, 0.1)", color: "#f59e0b", padding: "4px 10px", borderRadius: "12px", fontSize: "10px", fontWeight: "800", border: "1px solid rgba(245, 158, 11, 0.3)", marginLeft: "10px", textTransform: "uppercase" },
};

const nutritionAnimations = `
  @keyframes slideInRight { from { transform: translateX(100%); opacity: 0; } to { transform: translateX(0); opacity: 1; } }
  @keyframes slideUp { from { transform: translateY(100%); } to { transform: translateY(0); } }
  @keyframes scaleIn { from { transform: scale(0.95) translateY(20px); opacity: 0; } to { transform: scale(1) translateY(0); opacity: 1; } }
  @keyframes fadeIn { from { opacity: 0; } to { opacity: 1; } }
  @keyframes pulse { 0% { transform: scale(1); } 50% { transform: scale(1.08); } 100% { transform: scale(1); } }
  .day-card-hover:hover { transform: translateY(-3px) !important; border-color: rgba(99, 102, 241, 0.3) !important; box-shadow: 0 8px 25px rgba(0,0,0,0.3) !important; }
  .food-row-hover:hover { background: rgba(255,255,255,0.04) !important; border-color: var(--app-border) !important; }
  .meal-card-hover:hover { border-color: rgba(99, 102, 241, 0.15) !important; box-shadow: 0 8px 30px rgba(0,0,0,0.2) !important; }
  .swap-btn-hover:hover { background: rgba(99, 102, 241, 0.2) !important; transform: scale(1.1); box-shadow: 0 0 12px rgba(99, 102, 241, 0.3); }
  .macro-stat-hover:hover { background: rgba(255,255,255,0.04) !important; transform: scale(1.03); }
  .icon-hover:hover { background: var(--app-border) !important; }
  .logout-btn:hover { background: rgba(239, 68, 68, 0.2) !important; }
`;

function Nutrition() {
  const navigate = useNavigate();
  const { showError, showSuccess, showInfo } = useNotification();
  const [confirmDialog, setConfirmDialog] = useState({ show: false, message: "", onConfirm: null });

  const [loading, setLoading] = useState(false);
  const [weeklyPlan, setWeeklyPlan] = useState(null);
  const [dailyTarget, setDailyTarget] = useState(null);
  const [selectedDayIndex, setSelectedDayIndex] = useState(0);
  const [userProfile, setUserProfile] = useState(null);
  const [showHistory, setShowHistory] = useState(false);
  const [mealHistory, setMealHistory] = useState([]);
  const [checkedFoods, setCheckedFoods] = useState({});
  const [tickTimes, setTickTimes] = useState({});
  const [lockedMeals, setLockedMeals] = useState({});

  // Swap state
  const [swapModal, setSwapModal] = useState({ show: false, food: null, mealType: null, dayIndex: null });
  const [swapOptions, setSwapOptions] = useState([]);
  const [swapLoading, setSwapLoading] = useState(false);
  const [selectedSwap, setSelectedSwap] = useState(null);

  const [expandedDates, setExpandedDates] = useState({});
  const [expandedMeals, setExpandedMeals] = useState({});
  const MEAL_ORDER = ["breakfast", "lunch", "dinner"];

  const isMealUnlocked = (mealType, dayIdx) => {
    if (dayIdx !== 0) return false;

    const normalizedType = String(mealType || "").toLowerCase();
    if (normalizedType === "snack") return true;

    const mealIndex = MEAL_ORDER.indexOf(normalizedType);
    if (mealIndex === -1 || mealIndex === 0) return true;

    const todayDate = weeklyPlan?.days?.[dayIdx]?.date || getLocalDateStr();
    for (let idx = 0; idx < mealIndex; idx++) {
      const prevMealType = MEAL_ORDER[idx];
      const prevMeal = weeklyPlan?.days?.[dayIdx]?.meals?.find(
        (meal) => String(meal?.meal_type || "").toLowerCase() === prevMealType
      );
      const prevMealName = prevMeal?.name || prevMealType;
      if (!lockedMeals[`${todayDate}-${prevMealName}`] && !lockedMeals[`${todayDate}-${prevMealType}`]) {
        return false;
      }
    }

    return true;
  };

  const getUnlockMessage = (mealType) => {
    const normalizedType = String(mealType || "").toLowerCase();
    const mealIndex = MEAL_ORDER.indexOf(normalizedType);
    if (mealIndex <= 0) return null;
    const prevType = MEAL_ORDER[mealIndex - 1];
    return `Complete ${prevType.charAt(0).toUpperCase() + prevType.slice(1)} to unlock`;
  };

  useEffect(() => {
    fetchNutritionPlan();
    loadHistory();
    loadCheckedFoods();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  // ✅ BUG FIX 2: Backend Persistence to Frontend
  useEffect(() => {
    if (!weeklyPlan?.days?.length || !mealHistory?.length) return;

    const localChecked = safeJSONParse("checkedFoods", {});
    const localTickTimes = safeJSONParse("tickTimes", {});
    const localLocked = safeJSONParse("lockedMeals", {});
    let updated = false;

    mealHistory.forEach((dayEntry) => {
      if (!dayEntry?.date || !dayEntry?.meals) return;
      const dayPlan = weeklyPlan.days.find((d) => d.date === dayEntry.date);
      if (!dayPlan) return;

      Object.values(dayEntry.meals).forEach((mealData) => {
        if (!mealData) return;
        const planMeal = dayPlan.meals.find((m) => m.meal_type === mealData.meal_type);
        if (!planMeal) return;

        const lockMealName = mealData.name || planMeal.name;
        const lockMealType = String(mealData.meal_type || planMeal.meal_type || '').toLowerCase();
        const mealLockKey = `${dayEntry.date}-${lockMealName}`;
        if (!localLocked[mealLockKey]) {
          localLocked[mealLockKey] = true;
          updated = true;
        }
        if (lockMealType && !localLocked[`${dayEntry.date}-${lockMealType}`]) {
          localLocked[`${dayEntry.date}-${lockMealType}`] = true;
          updated = true;
        }

        if (Array.isArray(mealData.foods) && mealData.foods.length > 0) {
          // Backend saved individual food items — match by name
          mealData.foods.forEach((food) => {
            const planFood = planMeal.foods.find((f) => f.name === food.name);
            if (!planFood) return;
            const checkKey = `${dayEntry.date}-${planFood.id}`;
            if (!localChecked[checkKey]) {
              localChecked[checkKey] = true;
              if (food.tick_time) {
                localTickTimes[checkKey] = food.tick_time;
              }
              updated = true;
            }
          });
        } else {
          // ✅ FIX: Backend only saves meal totals (foods: []), but the meal IS locked.
          // Synthetically mark ALL plan foods for this meal as checked to restore tick UI.
          planMeal.foods.forEach((planFood) => {
            const checkKey = `${dayEntry.date}-${planFood.id}`;
            if (!localChecked[checkKey]) {
              localChecked[checkKey] = true;
              updated = true;
            }
          });
        }
      });
    });

    if (updated) {
      setCheckedFoods(localChecked);
      setTickTimes(localTickTimes);
      setLockedMeals(localLocked);

      localStorage.setItem("checkedFoods", JSON.stringify(localChecked));
      localStorage.setItem("tickTimes", JSON.stringify(localTickTimes));
      localStorage.setItem("lockedMeals", JSON.stringify(localLocked));
    }
  }, [weeklyPlan, mealHistory]);

  const getTodayWorkoutIntensity = (workoutPlan = []) => {
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

  const getWorkoutPlanForNutrition = async (profile) => {
    const cachedPlan = safeJSONParse("workoutPlan", null);
    if (Array.isArray(cachedPlan)) {
      return cachedPlan;
    }

    // Do not block nutrition load on workout generation when cache is missing.
    // Use moderate intensity now; warm workout cache in background for next visit.
    generateWorkout(profile).then((workoutResponse) => {
      const generatedPlan = Array.isArray(workoutResponse?.data?.workout) ? workoutResponse.data.workout : [];
      if (generatedPlan.length > 0) {
        localStorage.setItem("workoutPlan", JSON.stringify(generatedPlan));
        localStorage.setItem("workoutPlanTimestamp", new Date().toISOString());
      }
    }).catch((err) => {
      console.warn('Background workout cache warmup failed:', err?.message || err);
    });

    return [];
  };

  const isTodayRestDay = () => {
    try {
      const workoutPlan = safeJSONParse("workoutPlan", []);
      if (!Array.isArray(workoutPlan) || workoutPlan.length === 0) return false;

      const jsDay = new Date().getDay();
      const todayIdx = (jsDay + 6) % 7;
      const todayPlan = workoutPlan.find((d) => (d?.day_of_week ?? -1) === todayIdx) || workoutPlan[todayIdx];
      if (!todayPlan) return false;
      // 1. Explicit type from backend engine
      if (todayPlan.type === 'rest') return true;
      // 2. Focus field
      const focus = `${todayPlan.focus || ""}`.toLowerCase();
      if (focus.includes('rest') || focus === 'active recovery') return true;
      // 3. Label / note
      const label = `${todayPlan.day || ""}`.toLowerCase();
      const note = `${todayPlan.note || ""}`.toLowerCase();
      if (label.includes('rest') || note.includes('rest') || note.includes('recovery')) return true;
      return false;
    } catch {
      return false;
    }
  };

  /* ──────────────────────────────────────────
   *  FETCH — builds 7-day plan from backend
   *  ✅ FIX 7: Date-aware caching with profile hash
   *  ✅ FIX 8: Cache invalidation on profile change
   * ────────────────────────────────────────── */
  const fetchNutritionPlan = async () => {
    try {
      setLoading(true);
      const profileRes = await getProfile();
      const profile = profileRes.data;
      setUserProfile(profile);

      // ✅ FIX 7+8: Check if we have a valid cached plan for today with same profile
      // ✅ PA-7: Use LOCAL timezone for consistent date across pages
      const todayStr = getLocalDateStr();
      const profileHash = `${profile.weight}-${profile.height}-${profile.goal}-${profile.dietary_preference || ''}-${profile.age}`;
      const cacheInvalid = getFromStorage(StorageKeys.NUTRITION_CACHE_INVALID) === 'true';
      const cachedDate = getFromStorage(StorageKeys.NUTRITION_CACHE_DATE);
      const cachedPlan = getFromStorage(StorageKeys.NUTRITION_CACHE);

      if (!cacheInvalid && cachedPlan && cachedDate === todayStr && cachedPlan._profileHash === profileHash && cachedPlan.days) {
        // Use cached plan — no network request needed
        setWeeklyPlan({ week_start: todayStr, days: cachedPlan.days });
        setDailyTarget(cachedPlan.daily_target || {});
        setSelectedDayIndex(0);
        setLoading(false);
        return;
      }

      // Clear invalidation flag since we're fetching fresh
      setToStorage(StorageKeys.NUTRITION_CACHE_INVALID, 'false');

      const workoutPlan = await getWorkoutPlanForNutrition(profile);
      const workoutIntensity = getTodayWorkoutIntensity(workoutPlan);

      const response = await generateNutritionPlan({
        age: profile.age,
        weight: profile.weight,
        height: profile.height,
        gender: profile.gender,
        goal: profile.goal,
        dietary_preference: profile.dietary_preference || "Non-Veg",
        allergies: profile.allergies || [],
        workout_intensity: workoutIntensity,
        weekly_workout_plan: workoutPlan,
      });

      if (response.data.success && response.data.nutrition) {
        const nutrition = response.data.nutrition;

        // Save daily target
        setDailyTarget(nutrition.daily_target || {});

        // Build 7-day display from weekly_plan the backend now returns
        const weekPlan = nutrition.weekly_plan;
        const dayNames = ["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday"];
        const today = new Date();

        const days = [];
        for (let i = 0; i < 7; i++) {
          const date = new Date(today); date.setDate(date.getDate() + i);
          const dName = date.toLocaleDateString('en-US', {weekday: 'long'});
          // Get the matching day from the backend weekly plan
          const backendDay = weekPlan?.[dName] || weekPlan?.[dayNames[i]] || {};

          // Build meals array from the backend day object
          const meals = [];
          for (const mealType of ['breakfast', 'lunch', 'dinner', 'snack']) {
            const items = backendDay[mealType] || [];
            const foods = items.map((item, idx) => ({
              id: `${mealType}-${item.name}-${i}-${idx}`,
              name: item.name,
              calories: item.calories || 0,
              protein_g: item.protein || 0,
              carbs_g: item.carbs || 0,
              fat_g: item.fat || 0,
              swap_group: item.swap_group || '',
            }));
            const totals = {
              calories: foods.reduce((s, f) => s + f.calories, 0),
              protein_g: Math.round(foods.reduce((s, f) => s + f.protein_g, 0) * 10) / 10,
              carbs_g: Math.round(foods.reduce((s, f) => s + f.carbs_g, 0) * 10) / 10,
              fat_g: Math.round(foods.reduce((s, f) => s + f.fat_g, 0) * 10) / 10,
            };
            meals.push({
              name: mealType.charAt(0).toUpperCase() + mealType.slice(1),
              meal_type: mealType,
              foods,
              totals,
            });
          }

          // Daily totals = sum of all meal totals
          const daily_totals = {
            calories: meals.reduce((s, m) => s + m.totals.calories, 0),
            protein_g: Math.round(meals.reduce((s, m) => s + m.totals.protein_g, 0) * 10) / 10,
            carbs_g: Math.round(meals.reduce((s, m) => s + m.totals.carbs_g, 0) * 10) / 10,
            fat_g: Math.round(meals.reduce((s, m) => s + m.totals.fat_g, 0) * 10) / 10,
          };

          days.push({
            date: getLocalDateStr(date),
            day_name: dName,
            is_today: i === 0,
            is_future: i > 0,
            daily_totals,
            meals,
          });
        }

        setWeeklyPlan({ week_start: getLocalDateStr(today), days });
        setSelectedDayIndex(0);

        setToStorage(StorageKeys.NUTRITION_CACHE, {
          days,
          daily_target: nutrition.daily_target || {},
          _profileHash: profileHash,
        });
        setToStorage(StorageKeys.NUTRITION_CACHE_DATE, todayStr);

        showSuccess("Nutrition plan loaded from dataset!", 3000);
        
        // ✅ FIX: Re-run loadHistory to tick off the newly generated food items 
        // using the backend completed meal history (in case the plan regenerated).
        loadHistory();
      } else {
        throw new Error(response.data.error || "Failed to load nutrition plan");
      }
    } catch (error) {
      console.error("Nutrition error:", error);
      showError(error.response?.data?.detail || error.response?.data?.error || "Failed to load nutrition plan.", 5000);
    } finally {
      setLoading(false);
    }
  };

  /* ──────────────────────────────────────────
   *  CHECKING / LOCKING meals
   * ────────────────────────────────────────── */
  const loadHistory = async () => {
    try {
      const response = await getMealHistory();
      const historyData = response.data || [];
      setMealHistory(historyData);
      
      // ✅ Populate lockedMeals directly from backed up daily history
      const localLocked = safeJSONParse("lockedMeals", {});
      const localChecked = safeJSONParse("checkedFoods", {});
      const todayDate = getLocalDateStr();
      const todayEntry = historyData.find(d => d.date === todayDate);
      
      if (todayEntry && todayEntry.meals) {
        Object.values(todayEntry.meals).forEach(mealData => {
          if (mealData && mealData.name) {
            const mealLockKey = `${todayDate}-${mealData.name}`;
            localLocked[mealLockKey] = true;
            const mealTypeKey = String(mealData.meal_type || '').toLowerCase();
            if (mealTypeKey) {
              localLocked[`${todayDate}-${mealTypeKey}`] = true;

              // ✅ FIX: Backfill checkedFoods for this locked meal using the current
              // nutrition plan from localStorage cache. The backend only stores meal totals
              // (not individual food items), so we reconstruct from the local plan.
              try {
                // StorageKeys.NUTRITION_CACHE = 'nutritionPlan'
                const cachedNutrition = safeJSONParse("nutritionPlan", null);
                const cachedDays = cachedNutrition?.days || [];
                const todayPlanDay = cachedDays[0]; // index 0 = today
                if (todayPlanDay) {
                  const planMeal = todayPlanDay.meals?.find(
                    (m) => String(m.meal_type || '').toLowerCase() === mealTypeKey
                  );
                  if (planMeal) {
                    planMeal.foods.forEach((food) => {
                      const checkKey = `${todayDate}-${food.id}`;
                      if (!localChecked[checkKey]) {
                        localChecked[checkKey] = true;
                      }
                    });
                  }
                }
              } catch {
                // Non-critical — checkedFoods will remain partially populated
              }
            }
          }
        });
      }

      setCheckedFoods(localChecked);
      localStorage.setItem("checkedFoods", JSON.stringify(localChecked));
      setLockedMeals(localLocked);
    } catch (err) {
      console.error("Failed to load meal history from db:", err);
      // Fallback
      setMealHistory(safeJSONParse("mealHistoryGrouped", []));
      setLockedMeals(safeJSONParse("lockedMeals", {}));
    }
    setTickTimes(safeJSONParse("tickTimes", {}));
  };
  const loadCheckedFoods = () => setCheckedFoods(safeJSONParse("checkedFoods", {}));

  const handleCheckFood = (foodId, mealName, mealType, dayIdx) => {
    if (dayIdx !== 0) { showInfo("You can only complete today's meals!", 2000); return; }

    const normalizedMealType = String(mealType || '').toLowerCase();
    if (!isMealUnlocked(normalizedMealType, dayIdx)) {
      const message = getUnlockMessage(normalizedMealType) || 'This meal is locked right now.';
      showInfo(message, 2200);
      return;
    }

    const selectedDayDate = weeklyPlan?.days?.[dayIdx]?.date || getLocalDateStr();
    const today = selectedDayDate;
    const mealLockKey = `${today}-${mealName}`;
    const mealTypeLockKey = `${today}-${normalizedMealType}`;
    if (lockedMeals[mealLockKey] || lockedMeals[mealTypeLockKey]) {
      showInfo("This meal is already completed and locked! 🔒", 2000);
      return;
    }

    const checkKey = `${today}-${foodId}`;
    const nowTicked = !checkedFoods[checkKey];
    const newChecked = { ...checkedFoods, [checkKey]: nowTicked };
    setCheckedFoods(newChecked);
    localStorage.setItem("checkedFoods", JSON.stringify(newChecked));

    const newTickTimes = { ...tickTimes };
    if (nowTicked) newTickTimes[checkKey] = new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" });
    else delete newTickTimes[checkKey];
    setTickTimes(newTickTimes);
    localStorage.setItem("tickTimes", JSON.stringify(newTickTimes));

    // Check if ALL items in this meal are now ticked
    const selectedDay = weeklyPlan?.days?.[dayIdx];
    if (selectedDay) {
      const meal = selectedDay.meals.find(
        (m) => m.name === mealName || String(m.meal_type || '').toLowerCase() === normalizedMealType
      );
      if (meal) {
        const allChecked = meal.foods.every(f => newChecked[`${today}-${f.id}`]);
        if (allChecked) {
          const mealTypeKey = String(meal.meal_type || normalizedMealType || '').toLowerCase();
          const newLocked = {
            ...lockedMeals,
            [mealLockKey]: true,
            ...(mealTypeKey ? { [`${today}-${mealTypeKey}`]: true } : {}),
          };
          setLockedMeals(newLocked);
          localStorage.setItem("lockedMeals", JSON.stringify(newLocked));

          const completedTimeStr = new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" });
          const mealData = {
            name: meal.name, meal_type: meal.meal_type,
            calories: meal.totals.calories, protein: meal.totals.protein_g,
            carbs: meal.totals.carbs_g, fat: meal.totals.fat_g,
            completed_at: new Date().toISOString(), completed_time_str: completedTimeStr,
            foods: meal.foods.map(f => ({
              name: f.name, calories: f.calories,
              protein: f.protein_g, carbs: f.carbs_g, fat: f.fat_g,
              tick_time: newTickTimes[`${today}-${f.id}`] || completedTimeStr,
            })),
          };

          let updatedHistory = [...mealHistory];
          let dateEntry = updatedHistory.find(e => e.date === today);
          if (!dateEntry) { dateEntry = { date: today, meals: {}, total_calories: 0, total_protein: 0, total_carbs: 0, total_fat: 0 }; updatedHistory.unshift(dateEntry); }
          dateEntry.meals[meal.meal_type] = mealData;
          dateEntry.total_calories = Object.values(dateEntry.meals).reduce((s, m) => s + (m.calories || 0), 0);
          dateEntry.total_protein = Object.values(dateEntry.meals).reduce((s, m) => s + (m.protein || 0), 0);
          dateEntry.total_carbs = Object.values(dateEntry.meals).reduce((s, m) => s + (m.carbs || 0), 0);
          dateEntry.total_fat = Object.values(dateEntry.meals).reduce((s, m) => s + (m.fat || 0), 0);
          updatedHistory.sort((a, b) => b.date.localeCompare(a.date));
          setMealHistory(updatedHistory);
          
          saveMealHistory(updatedHistory)
            .catch(err => console.error("Error saving meal history to db", err));
          
          setExpandedDates(prev => ({ ...prev, [today]: true }));

          const mealsCountLocal = ['breakfast', 'lunch', 'dinner'].filter(t => Boolean(dateEntry.meals?.[t])).length;
          syncBridge.emit(SyncTypes.MEAL_COMPLETED, {
            date: today,
            mealsCount: mealsCountLocal,
            calories: dateEntry.total_calories || 0,
            protein: dateEntry.total_protein || 0,
            carbs: dateEntry.total_carbs || 0,
            fat: dateEntry.total_fat || 0,
          });
          
          // Sync with Node Database & consume todayTotals for Dashboard macro update
          saveUserMealToNode({
            dayName: today,
            mealType: meal.meal_type,
            name: meal.name,
            calories: meal.totals.calories,
            protein: meal.totals.protein_g,
            carbs: meal.totals.carbs_g,
            fat: meal.totals.fat_g,
            completedAt: mealData.completed_at
          }).then(res => {
            // ✅ BUG FIX: Consume todayTotals from backend to signal Dashboard
            const totals = res?.data?.todayTotals;
            if (totals) {
              // Count how many of breakfast/lunch/dinner are done so far in this session
              const mealsCount = ['breakfast', 'lunch', 'dinner'].filter(t => Boolean(dateEntry.meals?.[t])).length;
              setToStorage('_macroSync', JSON.stringify({
                calories: totals.calories,
                protein: totals.protein,
                carbs: totals.carbs,
                fat: totals.fat,
                mealsCount,   // ✅ Dashboard uses this for per-meal circle progress
                ts: Date.now()
              }));
              syncBridge.emit(SyncTypes.MEAL_COMPLETED, {
                date: today,
                mealsCount,
                calories: totals.calories,
                protein: totals.protein,
                carbs: totals.carbs,
                fat: totals.fat,
              });
              console.log('✅ Macro sync signal stored for Dashboard:', totals, '| mealsCount:', mealsCount);
            }
          }).catch(err => console.error("Failed to sync meal to node db", err));

          // ✅ FIX 6: Snacks are OPTIONAL for day completion
          // Only Breakfast + Lunch + Dinner are required — Snack is bonus calories
          const requiredMeals = ["breakfast", "lunch", "dinner"];
          const allMealsDone = requiredMeals.every((mealType) => Boolean(dateEntry.meals?.[mealType]));

          const water = parseFloat(String(getFromStorage(StorageKeys.WATER_INTAKE, 0) || 0)) || 0;
          const sleep = parseFloat(String(getFromStorage(StorageKeys.SLEEP_HOURS, 0) || 0)) || 0;
          const restDay = isTodayRestDay();
          const workoutDone = getFromStorage(StorageKeys.TODAY_WORKOUT_DONE) === "true";

          // Keep trend/graph state in sync after every completed meal.
          saveTrends({
            date: today,
            workout_completed: restDay ? true : workoutDone,
            meal_completed: allMealsDone,
            calories: dateEntry.total_calories || 0,
            protein: dateEntry.total_protein || 0,
            carbs: dateEntry.total_carbs || 0,
            fat: dateEntry.total_fat || 0,
            water_intake: water,
            sleep_duration: sleep,
            water_glasses: water,
            sleep_hours: sleep,
          }).catch((err) => console.error("Failed to sync trends after meal update", err));

          if (allMealsDone) {
            setToStorage(StorageKeys.TODAY_MEALS_DONE, "true");
            if (restDay) {
              setToStorage(StorageKeys.TODAY_WORKOUT_DONE, "true");
              setToStorage("todayProgressStatus", "done");
            } else {
              setToStorage("todayProgressStatus", "meal");
            }
          }

          showSuccess(`${mealName} completed & locked! 🔒🎉`, 3000);
        }
      }
    }
  };

  /* ──────────────────────────────────────────
   *  SWAP — fetches alternatives from backend
   * ────────────────────────────────────────── */
  const openSwapModal = async (food, mealType, dayIdx) => {
    if (dayIdx !== 0) { showInfo("You can only swap today's meals!", 2000); return; }
    setSwapModal({ show: true, food, mealType, dayIndex: dayIdx });
    setSelectedSwap(null);
    setSwapLoading(true);
    try {
      const res = await getNutritionSwapOptions({
        food_name: food.name,
        meal_type: mealType,
        age: userProfile?.age, weight: userProfile?.weight,
        height: userProfile?.height, gender: userProfile?.gender,
        goal: userProfile?.goal,
        dietary_preference: userProfile?.dietary_preference || "Non-Veg",
        allergies: userProfile?.allergies || [],
      });
      setSwapOptions(res.data.success ? res.data.swap_options : []);
    } catch (e) {
      console.error("Swap fetch error", e);
      setSwapOptions([]);
    } finally {
      setSwapLoading(false);
    }
  };

  const confirmSwap = () => {
    if (!selectedSwap) return;
    const dayIdx = swapModal.dayIndex;
    const updatedDays = weeklyPlan.days.map((day, i) => {
      if (i !== dayIdx) return day;
      const updatedMeals = day.meals.map(meal => {
        if (meal.meal_type !== swapModal.mealType) return meal;
        const updatedFoods = meal.foods.map(f => {
          if (f.id !== swapModal.food.id) return f;
          return {
            ...f,
            name: selectedSwap.name,
            calories: selectedSwap.calories,
            protein_g: selectedSwap.protein,
            carbs_g: selectedSwap.carbs,
            fat_g: selectedSwap.fat,
            swap_group: selectedSwap.swap_group || '',
          };
        });
        const totals = {
          calories: updatedFoods.reduce((s, f) => s + f.calories, 0),
          protein_g: Math.round(updatedFoods.reduce((s, f) => s + f.protein_g, 0) * 10) / 10,
          carbs_g: Math.round(updatedFoods.reduce((s, f) => s + f.carbs_g, 0) * 10) / 10,
          fat_g: Math.round(updatedFoods.reduce((s, f) => s + f.fat_g, 0) * 10) / 10,
        };
        return { ...meal, foods: updatedFoods, totals };
      });
      const daily_totals = {
        calories: updatedMeals.reduce((s, m) => s + m.totals.calories, 0),
        protein_g: Math.round(updatedMeals.reduce((s, m) => s + m.totals.protein_g, 0) * 10) / 10,
        carbs_g: Math.round(updatedMeals.reduce((s, m) => s + m.totals.carbs_g, 0) * 10) / 10,
        fat_g: Math.round(updatedMeals.reduce((s, m) => s + m.totals.fat_g, 0) * 10) / 10,
      };
      return { ...day, meals: updatedMeals, daily_totals };
    });
    const updatedWeekly = { ...weeklyPlan, days: updatedDays };
    setWeeklyPlan(updatedWeekly);
    const cachedPlan = getFromStorage(StorageKeys.NUTRITION_CACHE) || {};
    setToStorage(StorageKeys.NUTRITION_CACHE, {
      ...cachedPlan,
      days: updatedWeekly.days,
      daily_target: cachedPlan.daily_target || dailyTarget || {},
    });
    setSwapModal({ show: false, food: null, mealType: null, dayIndex: null });
    showSuccess(`Swapped to ${selectedSwap.name}!`, 2000);
  };

  /* ──────────────────────────────────────────
   *  RENDER
   * ────────────────────────────────────────── */
  // ✅ BUG FIX 4: Logout confirmation handler for Navbar
  const handleLogout = () => {
    setConfirmDialog({ show: true, message: 'Log out of Elevate?', onConfirm: null });
  };

  const selectedDay = weeklyPlan?.days?.[selectedDayIndex];
  const today = getLocalDateStr();
  const selectedDayConsumedTotals = (() => {
    if (!selectedDay?.date) return { calories: 0, protein_g: 0, carbs_g: 0, fat_g: 0 };

    // Build a local fallback from current tick/lock state so refresh/relogin does not
    // temporarily show 0 before backend history sync completes.
    let localCalories = 0;
    let localProtein = 0;
    let localCarbs = 0;
    let localFat = 0;

    (selectedDay.meals || []).forEach((meal) => {
      const mealType = String(meal?.meal_type || '').toLowerCase();
      const mealLocked =
        Boolean(lockedMeals[`${selectedDay.date}-${meal?.name}`])
        || Boolean(mealType && lockedMeals[`${selectedDay.date}-${mealType}`]);

      if (mealLocked) {
        localCalories += Number(meal?.totals?.calories) || 0;
        localProtein += Number(meal?.totals?.protein_g) || 0;
        localCarbs += Number(meal?.totals?.carbs_g) || 0;
        localFat += Number(meal?.totals?.fat_g) || 0;
        return;
      }

      (meal?.foods || []).forEach((food) => {
        if (checkedFoods[`${selectedDay.date}-${food.id}`]) {
          localCalories += Number(food?.calories) || 0;
          localProtein += Number(food?.protein_g) || 0;
          localCarbs += Number(food?.carbs_g) || 0;
          localFat += Number(food?.fat_g) || 0;
        }
      });
    });

    // Removed unused history variables to pass lint

    return {
      calories: Math.round(localCalories),
      protein_g: Math.round(localProtein * 10) / 10,
      carbs_g: Math.round(localCarbs * 10) / 10,
      fat_g: Math.round(localFat * 10) / 10,
    };
  })();

  if (loading) {
    return (
      <div style={styles.page}>
        <AuroraBackground />
        <style>{nutritionAnimations}</style>
        <Navbar navigate={navigate} setShowHistory={setShowHistory} onLogout={handleLogout} />
        <div style={styles.container}>
          <div style={{ textAlign: "center", padding: "100px 20px" }}>
            <div style={{ fontSize: "48px", marginBottom: "16px", animation: "pulse 1.5s infinite" }}>⏳</div>
            <div style={{ fontSize: "18px", fontWeight: "700", color: "var(--app-text)" }}>Loading Your Nutrition Plan...</div>
            <div style={{ fontSize: "13px", color: "#71717a", marginTop: "8px" }}>Optimizing meals from dataset</div>
          </div>
        </div>
        <ConfirmDialog
          show={confirmDialog.show}
          message={confirmDialog.message}
          onConfirm={() => {
            if (confirmDialog.onConfirm) confirmDialog.onConfirm();
            else { logoutSafe(); navigate("/"); }
            setConfirmDialog({ show: false, message: "", onConfirm: null });
          }}
          onCancel={() => setConfirmDialog({ show: false, message: "", onConfirm: null })}
        />
      </div>
    );
  }

  if (!weeklyPlan) {
    return (
      <div style={styles.page}>
        <AuroraBackground />
        <style>{nutritionAnimations}</style>
        <Navbar navigate={navigate} setShowHistory={setShowHistory} onLogout={handleLogout} />
        <div style={styles.container}>
          <div style={{ textAlign: "center", padding: "100px 20px" }}>
            <div style={{ fontSize: "64px", marginBottom: "24px" }}>🍽️</div>
            <div style={{ fontSize: "24px", fontWeight: "800", color: "var(--app-text)", marginBottom: "12px" }}>No Nutrition Plan</div>
            <div style={{ fontSize: "14px", color: "#71717a", marginBottom: "32px" }}>Generate a personalized meal plan based on your profile</div>
            <button onClick={fetchNutritionPlan} style={{ padding: "16px 40px", background: "linear-gradient(135deg, #6366f1 0%, #4f46e5 100%)", color: "var(--app-text)", border: "none", borderRadius: "16px", fontSize: "16px", fontWeight: "700", cursor: "pointer", boxShadow: "0 4px 20px rgba(99, 102, 241, 0.4)" }}>Generate Plan</button>
          </div>
        </div>
        <ConfirmDialog
          show={confirmDialog.show}
          message={confirmDialog.message}
          onConfirm={() => {
            if (confirmDialog.onConfirm) confirmDialog.onConfirm();
            else { logoutSafe(); navigate("/"); }
            setConfirmDialog({ show: false, message: "", onConfirm: null });
          }}
          onCancel={() => setConfirmDialog({ show: false, message: "", onConfirm: null })}
        />
      </div>
    );
  }

  return (
    <div style={styles.page}>
      <AuroraBackground />
      <style>{nutritionAnimations}</style>
      <Navbar navigate={navigate} setShowHistory={setShowHistory} onLogout={handleLogout} />

      <div style={styles.container}>
        <h1 style={styles.header}>Weekly Nutrition Plan</h1>

        {/* Day Selector */}
        <div style={styles.daySelectorBar}>
          {weeklyPlan.days.map((day, index) => (
            <div key={day.date} onClick={() => setSelectedDayIndex(index)} className="day-card-hover" style={{ ...styles.dayCard, ...(selectedDayIndex === index ? styles.dayCardSelected : {}), ...(day.is_today ? styles.dayCardToday : {}), opacity: day.is_future && selectedDayIndex !== index ? 0.6 : 1 }}>
              {selectedDayIndex === index && <div style={{ position: "absolute", top: 0, left: 0, right: 0, height: "3px", background: "linear-gradient(90deg, #6366f1, #a78bfa)", borderRadius: "20px 20px 0 0" }} />}
              <div style={styles.dayName}>{day.day_name?.slice(0, 3)}</div>
              <div style={{ fontSize: "22px", fontWeight: "800", color: selectedDayIndex === index ? "var(--app-text)" : "#71717a", marginBottom: "8px", fontFamily: "monospace" }}>{new Date(day.date).getDate()}</div>
              {day.is_today && <div style={{ fontSize: "9px", color: "#10b981", fontWeight: "800", marginTop: "6px", textTransform: "uppercase", letterSpacing: "1px" }}>Today</div>}
            </div>
          ))}
        </div>

        {/* Daily Summary */}
        {selectedDay && (
          <div style={styles.dailySummaryCard}>
            <div style={{ position: "absolute", top: 0, left: 0, right: 0, height: "2px", background: "linear-gradient(90deg, #6366f1, #a78bfa, #6366f1)", opacity: 0.6 }} />
            <MacroStat value={selectedDay.daily_totals.calories} label="Calories" color="var(--app-text)" icon="🔥" />
            <MacroStat value={`${selectedDay.daily_totals.protein_g}g`} label="Protein" color="#10b981" icon="💪" />
            <MacroStat value={`${selectedDay.daily_totals.carbs_g}g`} label="Carbs" color="#3b82f6" icon="⚡" />
            <MacroStat value={`${selectedDay.daily_totals.fat_g}g`} label="Fats" color="#f59e0b" icon="🥑" />

            <MacroStat
              value={`${selectedDayConsumedTotals.calories} cal`}
              label={selectedDay.date === today ? "Consumed Today" : "Consumed"}
              color="#8b5cf6"
              icon="🎯"
            />
          </div>
        )}

        {/* Meal Cards */}
        <div style={styles.mealList}>
          {selectedDay?.meals.map((meal, mealIndex) => {
            const mealLockKey = `${selectedDay.date}-${meal.name}`;
            const mealTypeKey = String(meal.meal_type || '').toLowerCase();
            const mealTypeLockKey = `${selectedDay.date}-${mealTypeKey}`;
            const isCompleted = !!lockedMeals[mealLockKey] || !!lockedMeals[mealTypeLockKey];
            const isSequenceLocked = selectedDayIndex === 0 ? !isMealUnlocked(mealTypeKey, selectedDayIndex) : false;
            const unlockMessage = isSequenceLocked ? getUnlockMessage(mealTypeKey) : null;
            const checkedCount = meal.foods.filter(f => checkedFoods[`${selectedDay.date}-${f.id}`] || isCompleted).length;
            const isFutureDay = selectedDayIndex > 0;
            return (
              <MealCard
                key={mealIndex}
                meal={meal}
                isLocked={isCompleted}
                isSequenceLocked={isSequenceLocked}
                unlockMessage={unlockMessage}
                checkedFoods={checkedFoods} tickTimes={tickTimes}
                today={selectedDay.date} checkedCount={checkedCount}
                totalCount={meal.foods.length}
                onCheckFood={handleCheckFood}
                onSwapFood={openSwapModal}
                dayIndex={selectedDayIndex} isFutureDay={isFutureDay}
              />
            );
          })}
        </div>
      </div>

      {/* History Panel */}
      {showHistory && (
        <HistoryPanel
          mealHistory={mealHistory} expandedDates={expandedDates}
          setExpandedDates={setExpandedDates} expandedMeals={expandedMeals}
          setExpandedMeals={setExpandedMeals}
          onClose={() => setShowHistory(false)} today={today}
        />
      )}

      {/* Swap Modal — backend driven */}
      {swapModal.show && (
        <div style={styles.swapModal} onClick={() => setSwapModal({ show: false, food: null, mealType: null, dayIndex: null })}>
          <div style={styles.swapModalCard} onClick={e => e.stopPropagation()}>
            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "8px" }}>
              <div style={{ fontSize: "28px", fontWeight: "800", color: "var(--app-text)", letterSpacing: "-0.5px" }}>Swap Food</div>
              <button onClick={() => setSwapModal({ show: false, food: null, mealType: null, dayIndex: null })} style={{ background: "var(--app-border)", borderRadius: "50%", width: "36px", height: "36px", display: "flex", alignItems: "center", justifyContent: "center", color: "var(--app-text-muted)", border: "1px solid var(--app-border)", fontSize: "16px", cursor: "pointer", transition: "all 0.2s ease" }} className="icon-hover">✕</button>
            </div>
            <div style={{ fontSize: "15px", color: "var(--app-text-muted)", marginBottom: "24px", lineHeight: "1.5" }}>
              Looking for alternatives to <strong style={{ color: "var(--app-text)" }}>{swapModal.food?.name}</strong>? Choose an option below.
            </div>

            {swapLoading ? (
              <div style={{ textAlign: "center", padding: "60px 20px", color: "#71717a", flex: 1 }}>
                <div style={{ fontSize: "32px", marginBottom: "16px", animation: "pulse 1.5s infinite" }}>🔄</div>
                <div style={{ fontSize: "15px", fontWeight: "600" }}>Searching dataset for alternatives...</div>
              </div>
            ) : (
              <div style={{ display: "flex", flexDirection: "column", gap: "12px", marginBottom: "24px", overflowY: "auto", flex: 1, paddingRight: "8px" }} className="custom-scroll">
                {swapOptions.length === 0 ? (
                  <div style={{ textAlign: "center", padding: "40px", color: "#52525b", fontSize: "15px", background: 'var(--app-surface-hover, rgba(255,255,255,0.02))', borderRadius: "16px" }}>No similar swap options found.</div>
                ) : (
                  swapOptions.map((option, i) => (
                    <div key={i} onClick={() => setSelectedSwap(option)} style={{
                      display: "flex", justifyContent: "space-between", alignItems: "center", padding: "16px 20px",
                      background: selectedSwap?.name === option.name ? "rgba(99, 102, 241, 0.15)" : "var(--quote-bg)",
                      borderRadius: "16px",
                      border: selectedSwap?.name === option.name ? "2px solid #6366f1" : "1px solid var(--app-border)",
                      cursor: "pointer", transition: "all 0.2s ease",
                      boxShadow: selectedSwap?.name === option.name ? "0 4px 15px rgba(99, 102, 241, 0.2)" : "none"
                    }}>
                      <div>
                        <div style={{ fontSize: "16px", fontWeight: "700", color: selectedSwap?.name === option.name ? "var(--app-text)" : "var(--app-text)" }}>{option.name}</div>
                        <div style={{ display: "flex", gap: "12px", marginTop: "8px" }}>
                          <span style={{ fontSize: "12px", color: "#10b981", fontWeight: "600", fontFamily: "monospace" }}>P: {option.protein}g</span>
                          <span style={{ fontSize: "12px", color: "#3b82f6", fontWeight: "600", fontFamily: "monospace" }}>C: {option.carbs}g</span>
                          <span style={{ fontSize: "12px", color: "#f59e0b", fontWeight: "600", fontFamily: "monospace" }}>F: {option.fat}g</span>
                        </div>
                      </div>
                      <div style={{ fontSize: "16px", fontWeight: "800", color: "var(--app-text)", fontFamily: "monospace", background: "var(--app-border)", padding: "6px 12px", borderRadius: "12px" }}>
                        {option.calories} cal
                      </div>
                    </div>
                  ))
                )}
              </div>
            )}

            <div style={{ display: "flex", gap: "12px" }}>
              <button onClick={() => setSwapModal({ show: false, food: null, mealType: null, dayIndex: null })} style={{ flex: 1, padding: "14px", borderRadius: "14px", background: "var(--app-surface2)", color: "var(--app-text)", border: "1px solid var(--app-border)", fontWeight: "700", cursor: "pointer", fontSize: "14px" }}>Cancel</button>
              <button onClick={confirmSwap} disabled={!selectedSwap} style={{ flex: 1, padding: "14px", borderRadius: "14px", background: "linear-gradient(135deg, #6366f1 0%, #4f46e5 100%)", color: "var(--app-text)", border: "none", fontWeight: "700", cursor: "pointer", fontSize: "14px", opacity: selectedSwap ? 1 : 0.4, boxShadow: selectedSwap ? "0 4px 20px rgba(99, 102, 241, 0.4)" : "none" }}>Swap Food</button>
            </div>
          </div>
        </div>
      )}

      <ConfirmDialog
        show={confirmDialog.show}
        message={confirmDialog.message}
        onConfirm={() => {
          if (confirmDialog.onConfirm) {
            confirmDialog.onConfirm();
          } else {
            // Default action: logout
            logoutSafe();
            navigate("/");
          }
          setConfirmDialog({ show: false, message: "", onConfirm: null });
        }}
        onCancel={() => setConfirmDialog({ show: false, message: "", onConfirm: null })}
      />
    </div>
  );
}

/* ═══════════════════════════════════════════
 *  CHILD COMPONENTS
 * ═══════════════════════════════════════════ */

function Navbar({ navigate, setShowHistory, onLogout }) {
  const { theme, toggleTheme } = useTheme();
  return (
    <div style={styles.navbar}>
      <div style={styles.brand}><div style={styles.brandDot}></div>ELEVATE</div>
      <div style={styles.navCenter}>
        <div style={styles.navLink} onClick={() => navigate("/dashboard")}>Dashboard</div>
        <div style={styles.navLink} onClick={() => navigate("/workout")}>Workout</div>
        <div style={{ ...styles.navLink, ...styles.navLinkActive }}>Nutrition</div>
        <div style={styles.navLink} onClick={() => navigate("/chatbot")}>ChatBot</div>
      </div>
      <div style={styles.navRight}>
        <div style={styles.iconButton} className="icon-hover" onClick={() => setShowHistory(true)}>📊</div>
        <button
          className="theme-toggle-btn"
          onClick={toggleTheme}
          title={theme === 'dark' ? 'Switch to Light Mode' : 'Switch to Dark Mode'}
          aria-label="Toggle theme"
        >
          {theme === 'dark' ? '☀️' : '🌙'}
        </button>
        <div style={styles.logoutBtn} className="logout-btn" onClick={onLogout}>
          <span style={styles.logoutText}>Logout</span>
        </div>
      </div>
    </div>
  );
}

function MacroStat({ value, label, color, icon }) {
  return (
    <div style={styles.macroStat} className="macro-stat-hover">
      {icon && <div style={{ fontSize: "20px", marginBottom: "8px" }}>{icon}</div>}
      <div style={{ ...styles.macroValue, color }}>{value}</div>
      <div style={styles.macroLabel}>{label}</div>
    </div>
  );
}

function MealCard({ meal, isLocked, isSequenceLocked, unlockMessage, checkedFoods, tickTimes, today, checkedCount, totalCount, onCheckFood, onSwapFood, dayIndex, isFutureDay }) {
  const isDisabled = isFutureDay || isLocked || isSequenceLocked;
  return (
    <div
      className="meal-card-hover"
      style={{
        ...styles.mealCard,
        ...(isLocked ? styles.mealCardCompleted : {}),
        ...(isSequenceLocked
          ? {
              opacity: 0.55,
              cursor: "not-allowed",
              border: "1px dashed rgba(255,255,255,0.12)",
            }
          : {}),
      }}
    >
      {isLocked && <div style={styles.completedBadge}>✓ Completed</div>}
      {isSequenceLocked && (
        <div style={{
          position: "absolute",
          top: "15px",
          right: "15px",
          background: "rgba(113, 113, 122, 0.22)",
          color: "var(--app-text-muted)",
          padding: "6px 14px",
          borderRadius: "20px",
          fontSize: "11px",
          fontWeight: "700",
          border: "1px solid rgba(113, 113, 122, 0.35)",
        }}>
          Locked
        </div>
      )}

      <div style={styles.mealHeader}>
        <div style={{ display: "flex", alignItems: "center" }}>
          <div>
            <div style={{ display: "flex", alignItems: "center" }}>
              <div style={styles.mealName}>{meal.name}</div>
              {meal.meal_type.toLowerCase() === "snack" && <span style={styles.optionalBadge}>Always Open</span>}
            </div>
            <div style={{ fontSize: "13px", color: isLocked ? "#22c55e" : "#6366f1", fontWeight: "700", textTransform: "uppercase", marginTop: "4px", letterSpacing: "1px" }}>{meal.meal_type}</div>
            {isSequenceLocked && unlockMessage && (
              <div style={{ fontSize: "12px", color: "var(--app-text-muted)", marginTop: "6px" }}>{unlockMessage}</div>
            )}
          </div>
        </div>
        <div style={{ display: "flex", gap: "16px", alignItems: "center" }}>
          <div style={{ fontSize: "13px", fontWeight: "700", fontFamily: "monospace", color: isLocked ? "#22c55e" : checkedCount > 0 ? "#818cf8" : "#52525b" }}>
            {isLocked ? "✓ All" : `${checkedCount}/${totalCount}`}
          </div>
          <div style={{ width: "60px", height: "4px", background: "var(--app-surface2)", borderRadius: "4px", overflow: "hidden" }}>
            <div style={{ width: `${totalCount > 0 ? (checkedCount / totalCount) * 100 : 0}%`, height: "100%", background: isLocked ? "#22c55e" : "#6366f1", borderRadius: "4px", transition: "width 0.3s ease" }} />
          </div>
        </div>
      </div>

      <div style={styles.foodTableHeader}>
        <div></div><div>Food</div><div style={{ textAlign: "center", color: "#a78bfa" }}>Portion</div><div style={{ textAlign: "center" }}>Cal</div>
        <div style={{ textAlign: "center" }}>Pro</div><div style={{ textAlign: "center" }}>Carb</div>
        <div style={{ textAlign: "center" }}>Fat</div><div></div>
      </div>

      <div style={styles.foodList}>
        {meal.foods.map((food) => {
          const checkKey = `${today}-${food.id}`;
          const isChecked = !!checkedFoods[checkKey] || isLocked;
          const itemTickTime = tickTimes[checkKey];
          return (
            <div key={food.id} className="food-row-hover" style={{
              ...styles.foodItemRow,
              opacity: isChecked ? (isLocked ? 0.5 : 0.7) : 1,
              background: isChecked ? "rgba(34, 197, 94, 0.04)" : "rgba(255,255,255,0.02)",
              ...(isSequenceLocked ? { pointerEvents: "none", opacity: 0.5 } : {}),
            }}>
              <div onClick={() => !isDisabled && onCheckFood(food.id, meal.name, meal.meal_type, dayIndex)} style={{
                ...styles.checkbox, ...(isChecked ? styles.checkboxChecked : {}),
                ...(isDisabled && !isChecked ? { opacity: 0.3, cursor: "not-allowed" } : {}),
              }}>
                {isChecked && "✓"}
              </div>
              <div style={{ display: "flex", flexDirection: "column" }}>
                <span style={{ fontWeight: "600", color: isChecked ? "var(--app-text-muted)" : "var(--app-text)", textDecoration: isChecked ? "line-through" : "none" }}>{food.name}</span>
                {isChecked && itemTickTime && <span style={{ fontSize: "10px", color: "#22c55e", fontFamily: "monospace", marginTop: "2px" }}>✓ {itemTickTime}</span>}
              </div>
              <div style={{ textAlign: "center" }}>
                <span style={{
                  fontSize: "12px", fontWeight: "700", color: "#a78bfa",
                  background: "rgba(167,139,250,0.10)", borderRadius: "8px",
                  padding: "3px 7px", fontFamily: "monospace",
                  whiteSpace: "nowrap",
                }}>
                  {(() => {
                    const cal = food.calories || 0;
                    const name = (food.name || '').toLowerCase();
                    const isLiquid = /juice|milk|smoothie|drink|shake|tea|coffee|water|lassi|soup|broth/.test(name);
                    if (isLiquid) {
                      const ml = Math.round((cal / 60) * 200 / 50) * 50;
                      return `~${Math.max(100, Math.min(500, ml))}ml`;
                    }
                    const g = Math.round((cal / 250) * 200 / 25) * 25;
                    return `~${Math.max(50, Math.min(400, g))}g`;
                  })()}
                </span>
              </div>
              <div style={{ textAlign: "center", color: "var(--app-text)", fontWeight: "600", fontFamily: "monospace", fontSize: "13px" }}>{food.calories}</div>
              <div style={{ textAlign: "center", color: "#10b981", fontFamily: "monospace", fontSize: "13px" }}>{food.protein_g}g</div>
              <div style={{ textAlign: "center", color: "#3b82f6", fontFamily: "monospace", fontSize: "13px" }}>{food.carbs_g}g</div>
              <div style={{ textAlign: "center", color: "#f59e0b", fontFamily: "monospace", fontSize: "13px" }}>{food.fat_g}g</div>
              <button className="swap-btn-hover" onClick={() => !isDisabled && onSwapFood(food, meal.meal_type, dayIndex)} disabled={isDisabled} style={{ ...styles.swapBtn, ...(isDisabled ? { opacity: 0.3, cursor: "not-allowed" } : {}) }}>🔄</button>
            </div>
          );
        })}
      </div>

      <div style={styles.mealMacroTotal}>
        <div style={{ fontSize: "13px", fontWeight: "800", color: "var(--app-text)", fontFamily: "monospace" }}>{meal.totals.calories} cal</div>
        <div style={{ fontSize: "13px", fontWeight: "700", color: "#10b981", fontFamily: "monospace" }}>{meal.totals.protein_g}g pro</div>
        <div style={{ fontSize: "13px", fontWeight: "700", color: "#3b82f6", fontFamily: "monospace" }}>{meal.totals.carbs_g}g carb</div>
        <div style={{ fontSize: "13px", fontWeight: "700", color: "#f59e0b", fontFamily: "monospace" }}>{meal.totals.fat_g}g fat</div>
      </div>
    </div>
  );
}

function HistoryPanel({ mealHistory, expandedDates, setExpandedDates, expandedMeals, setExpandedMeals, onClose, today }) {
  const mealTypeIcons = { breakfast: "☀️", lunch: "🌤️", dinner: "🌙", snack: "🍎" };
  const mealTypeColors = { breakfast: "#f59e0b", lunch: "#3b82f6", dinner: "#8b5cf6", snack: "#10b981" };

  return (
    <div style={styles.historyPanel}>
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "24px" }}>
        <div>
          <div style={{ fontSize: "20px", fontWeight: "800", color: "var(--app-text)" }}>Meal History</div>
          <div style={{ fontSize: "12px", color: "#71717a", marginTop: "4px" }}>{mealHistory.length} day{mealHistory.length !== 1 ? "s" : ""} tracked</div>
        </div>
        <button onClick={onClose} style={{ background: "var(--app-border)", border: "1px solid var(--app-border)", color: "var(--app-text)", fontSize: "16px", cursor: "pointer", width: "36px", height: "36px", borderRadius: "10px", display: "flex", alignItems: "center", justifyContent: "center" }}>✕</button>
      </div>

      {mealHistory.length === 0 ? (
        <div style={{ textAlign: "center", padding: "60px 20px", color: "#3f3f46" }}>
          <div style={{ fontSize: "48px", marginBottom: "12px" }}>📋</div>
          <div style={{ fontSize: "16px", fontWeight: "700", color: "#52525b" }}>No meals completed yet</div>
          <div style={{ fontSize: "13px", color: "#3f3f46", marginTop: "8px" }}>Tick all items in a meal to save it here</div>
        </div>
      ) : (
        mealHistory.map((dayEntry) => {
          const dateObj = new Date(dayEntry.date + "T00:00:00");
          const dayName = dateObj.toLocaleDateString("en-US", { weekday: "long" });
          const dateText = dateObj.toLocaleDateString("en-US", { month: "short", day: "numeric", year: "numeric" });
          const isToday = dayEntry.date === today;
          const isExpanded = !!expandedDates[dayEntry.date];
          const mealCount = Object.keys(dayEntry.meals).length;

          return (
            <div key={dayEntry.date} style={{ marginBottom: "12px", borderRadius: "16px", overflow: "hidden", border: "1px solid rgba(255,255,255,0.06)" }}>
              <div onClick={() => setExpandedDates(prev => ({ ...prev, [dayEntry.date]: !prev[dayEntry.date] }))} style={{
                background: isToday ? "linear-gradient(135deg, rgba(99, 102, 241, 0.2) 0%, rgba(139, 92, 246, 0.15) 100%)" : "var(--quote-bg)",
                padding: "16px 20px", cursor: "pointer", display: "flex", justifyContent: "space-between", alignItems: "center",
                borderBottom: isExpanded ? "1px solid rgba(255,255,255,0.06)" : "none",
              }}>
                <div>
                  <div style={{ fontSize: "11px", fontWeight: "800", color: isToday ? "#818cf8" : "#71717a", textTransform: "uppercase", letterSpacing: "1px", marginBottom: "4px" }}>{isToday ? "⭐ Today" : dayName}</div>
                  <div style={{ fontSize: "15px", fontWeight: "700", color: "var(--app-text)" }}>{dateText}</div>
                  <div style={{ fontSize: "11px", color: "#52525b", marginTop: "4px" }}>{mealCount} meal{mealCount !== 1 ? "s" : ""} completed</div>
                </div>
                <div style={{ textAlign: "right", display: "flex", alignItems: "center", gap: "16px" }}>
                  <div>
                    <div style={{ fontSize: "20px", fontWeight: "800", color: "var(--app-text)", fontFamily: "monospace" }}>{dayEntry.total_calories}</div>
                    <div style={{ fontSize: "10px", color: "#71717a", textTransform: "uppercase", letterSpacing: "1px" }}>calories</div>
                  </div>
                  <div style={{ fontSize: "14px", color: "#52525b", transition: "transform 0.3s", transform: isExpanded ? "rotate(0deg)" : "rotate(-90deg)" }}>▼</div>
                </div>
              </div>

              {isExpanded && (
                <div style={{ background: "rgba(0,0,0,0.2)" }}>
                  {["breakfast", "lunch", "dinner", "snack"].map((mealType) => {
                    const meal = dayEntry.meals[mealType];
                    if (!meal) return null;
                    const mealKey = `${dayEntry.date}-${mealType}`;
                    const isMealExpanded = !!expandedMeals[mealKey];
                    return (
                      <div key={mealType} style={{ borderBottom: "1px solid rgba(255,255,255,0.04)" }}>
                        <div onClick={() => setExpandedMeals(prev => ({ ...prev, [mealKey]: !prev[mealKey] }))} style={{
                          padding: "14px 20px", display: "flex", justifyContent: "space-between", alignItems: "center", cursor: "pointer",
                        }}>
                          <div style={{ display: "flex", alignItems: "center", gap: "12px" }}>
                            <div style={{ width: "36px", height: "36px", borderRadius: "10px", background: (mealTypeColors[mealType] || "#6366f1") + "15", display: "flex", alignItems: "center", justifyContent: "center", fontSize: "16px" }}>
                              {mealTypeIcons[mealType] || "🍽️"}
                            </div>
                            <div>
                              <div style={{ fontSize: "13px", fontWeight: "700", color: "var(--app-text)", textTransform: "capitalize" }}>{mealType}</div>
                            </div>
                          </div>
                          <div style={{ display: "flex", alignItems: "center", gap: "12px" }}>
                            <div style={{ background: "rgba(34, 197, 94, 0.15)", color: "#22c55e", padding: "4px 10px", borderRadius: "10px", fontSize: "12px", fontWeight: "700", fontFamily: "monospace" }}>{meal.calories} cal</div>
                            <div style={{ fontSize: "12px", color: "#3f3f46", transition: "transform 0.3s", transform: isMealExpanded ? "rotate(0deg)" : "rotate(-90deg)" }}>▼</div>
                          </div>
                        </div>
                        {isMealExpanded && (
                          <div style={{ padding: "0 20px 14px 68px" }}>
                            <div style={{ display: "flex", gap: "16px", marginBottom: "10px", padding: "8px 12px", background: 'var(--app-surface-hover, rgba(255,255,255,0.02))', borderRadius: "10px" }}>
                              <span style={{ fontSize: "11px", color: "#10b981", fontWeight: "700", fontFamily: "monospace" }}>P: {meal.protein}g</span>
                              <span style={{ fontSize: "11px", color: "#3b82f6", fontWeight: "700", fontFamily: "monospace" }}>C: {meal.carbs}g</span>
                              <span style={{ fontSize: "11px", color: "#f59e0b", fontWeight: "700", fontFamily: "monospace" }}>F: {meal.fat}g</span>
                            </div>
                            {(meal.foods || []).map((food, fIdx) => (
                              <div key={fIdx} style={{ display: "flex", alignItems: "center", padding: "8px 0", borderBottom: fIdx < (meal.foods || []).length - 1 ? "1px solid rgba(255,255,255,0.03)" : "none" }}>
                                <div style={{ width: "20px", height: "20px", borderRadius: "6px", background: "linear-gradient(135deg, #22c55e 0%, #16a34a 100%)", display: "flex", alignItems: "center", justifyContent: "center", marginRight: "10px", fontSize: "10px", color: "var(--app-text)", flexShrink: 0 }}>✓</div>
                                <div style={{ flex: 1 }}>
                                  <div style={{ fontSize: "13px", fontWeight: "600", color: "#d4d4d8" }}>{food.name}</div>
                                  <div style={{ fontSize: "11px", color: "#52525b" }}>{food.calories} cal</div>
                                </div>
                                {food.tick_time && <div style={{ fontSize: "10px", color: "#71717a", background: "rgba(255,255,255,0.04)", padding: "3px 8px", borderRadius: "8px", fontFamily: "monospace" }}>🕐 {food.tick_time}</div>}
                              </div>
                            ))}
                          </div>
                        )}
                      </div>
                    );
                  })}
                </div>
              )}
            </div>
          );
        })
      )}
    </div>
  );
}

export default Nutrition;
