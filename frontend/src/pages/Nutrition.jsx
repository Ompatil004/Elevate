import React, { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { useNotification } from "../components/NotificationProvider";
import { useTheme } from "../context/ThemeContext";
import {
  getProfile,
  generateNutritionPlan,
  getNutritionSwapOptions,
  generateWorkout,
  saveUserMealToNode,
  getMealHistory,
  saveMealHistory,
  saveTrends,
  logActivityToBackend,
  backgroundCB,
} from "../api";
import { withCircuitBreaker } from "../utils/circuitBreaker";
import {
  StorageKeys,
  getFromStorage,
  setToStorage,
  logoutSafe,
  getLocalDateStr,
  safeJSONParse,
} from "../utils/storage";
import Navbar from "../components/Navbar";
import ConfirmDialog from "../components/ConfirmDialog";
import { syncBridge, SyncTypes } from "../utils/syncBridge";
import AuroraBackground from "../components/AuroraBackground";

import {
  styles,
  nutritionAnimations,
  NUTRITION_WEEKDAYS,
  getTodayIdxIST,
  getWeekDatesIST,
  getTodayWorkoutIntensity,
  isTodayRestDay,
  MacroStat,
  MealCard,
  MealSwapModal,
  HistoryPanel,
} from "../features/nutrition";

function Nutrition({ onLogout }) {
  const navigate = useNavigate();
  const { showError, showSuccess, showInfo } = useNotification();
  const { theme, toggleTheme } = useTheme();
  const [confirmDialog, setConfirmDialog] = useState({ show: false, message: "", onConfirm: null });

  const [loading, setLoading] = useState(false);
  const [weeklyPlan, setWeeklyPlan] = useState(null);
  const [dailyTarget, setDailyTarget] = useState(null);
  const [selectedDayIndex, setSelectedDayIndex] = useState(getTodayIdxIST());
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

  // Index (Mon=0…Sun=6) of real "today" within the fixed week. Only this day is interactive.
  const todayIdx = getTodayIdxIST();

  const isMealUnlocked = (mealType, dayIdx) => {
    if (dayIdx !== todayIdx) return false;

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

  const [circuitOpen, setCircuitOpen] = useState(false);
  const [retryCountdown, setRetryCountdown] = useState(0);

  useEffect(() => {
    fetchNutritionPlan();
    loadHistory();
    loadCheckedFoods();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  useEffect(() => {
    let timer;
    if (circuitOpen && retryCountdown > 0) {
      timer = setInterval(() => {
        setRetryCountdown(prev => {
          if (prev <= 1) {
            setCircuitOpen(false);
            return 0;
          }
          return prev - 1;
        });
      }, 1000);
    }
    return () => clearInterval(timer);
  }, [circuitOpen, retryCountdown]);

  // Backend Persistence to Frontend
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

  const getWorkoutPlanForNutrition = async (profile) => {
    const cachedPlan = safeJSONParse("workoutPlan", null);
    if (Array.isArray(cachedPlan)) {
      return cachedPlan;
    }

    withCircuitBreaker(backgroundCB, () => generateWorkout(profile)).then((workoutResponse) => {
      const generatedPlan = Array.isArray(workoutResponse?.data?.workout) ? workoutResponse.data.workout : [];
      if (generatedPlan.length > 0) {
        localStorage.setItem("workoutPlan", JSON.stringify(generatedPlan));
        localStorage.setItem("workoutPlanTimestamp", new Date().toISOString());
      }
    }).catch((err) => {
      if (err?.isCircuitOpen) {
        if (import.meta.env.DEV) console.log('Background workout cache warmup skipped (circuit open)');
        return;
      }
      console.warn('Background workout cache warmup failed:', err?.message || err);
    });

    return [];
  };

  const fetchNutritionPlan = async () => {
    try {
      setLoading(true);
      const profileRes = await getProfile();
      const profile = profileRes.data;
      setUserProfile(profile);

      const weekStartStr = getWeekDatesIST()[0];
      const profileHash = `${profile.weight}-${profile.height}-${profile.goal}-${profile.dietary_preference || ''}-${profile.age}`;
      const rawInvalid = getFromStorage(StorageKeys.NUTRITION_CACHE_INVALID);
      const cacheInvalid = rawInvalid === true || rawInvalid === 'true';
      const cachedDate = getFromStorage(StorageKeys.NUTRITION_CACHE_DATE);
      const cachedPlan = getFromStorage(StorageKeys.NUTRITION_CACHE);
      const hasValidDays = cachedPlan && Array.isArray(cachedPlan.days) && cachedPlan.days.length > 0;

      const isStale = cachedPlan && Array.isArray(cachedPlan.days) && cachedPlan.days.some(d => {
        const p = d.daily_totals?.protein_g;
        return p === undefined || p === null || isNaN(Number(p)) || Number(p) === 0;
      });

      if (!cacheInvalid && hasValidDays && !isStale && cachedDate === weekStartStr && cachedPlan._weekStart === weekStartStr && cachedPlan._profileHash === profileHash) {
        setWeeklyPlan({ week_start: weekStartStr, days: cachedPlan.days });
        setDailyTarget(cachedPlan.daily_target || {});
        setSelectedDayIndex(todayIdx);
        setLoading(false);
        return;
      }

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
        setDailyTarget(nutrition.daily_target || {});

        const weekPlan = nutrition.weekly_plan;
        const weekDates = getWeekDatesIST();

        const days = [];
        for (let i = 0; i < 7; i++) {
          const dName = NUTRITION_WEEKDAYS[i];
          const backendDay = weekPlan?.[dName] || {};

          const meals = [];
          for (const mealType of ['breakfast', 'lunch', 'dinner', 'snack']) {
            const items = backendDay[mealType] || [];
            const foods = items.map((item, idx) => ({
              id: `${mealType}-${item.name || item.food_name}-${i}-${idx}`,
              name: item.name || item.food_name,
              calories: item.calories || 0,
              protein_g: item.protein_g || item.protein || 0,
              carbs_g: item.carbs_g || item.carbs || 0,
              fat_g: item.fat_g || item.fat || 0,
              serving: item.serving || '',
              swap_group: item.swap_group || '',
            }));
            const totals = {
              calories: Math.round(foods.reduce((s, f) => s + f.calories, 0)),
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

          const daily_totals = {
            calories: Math.round(meals.reduce((s, m) => s + m.totals.calories, 0)),
            protein_g: Math.round(meals.reduce((s, m) => s + m.totals.protein_g, 0) * 10) / 10,
            carbs_g: Math.round(meals.reduce((s, m) => s + m.totals.carbs_g, 0) * 10) / 10,
            fat_g: Math.round(meals.reduce((s, m) => s + m.totals.fat_g, 0) * 10) / 10,
          };

          days.push({
            date: weekDates[i],
            day_name: dName,
            is_today: i === todayIdx,
            is_past: i < todayIdx,
            is_future: i > todayIdx,
            daily_totals,
            meals,
          });
        }

        const weekStart = weekDates[0];
        setWeeklyPlan({ week_start: weekStart, days });
        setSelectedDayIndex(todayIdx);

        setToStorage(StorageKeys.NUTRITION_CACHE, {
          days,
          daily_target: nutrition.daily_target || {},
          _profileHash: profileHash,
          _weekStart: weekStart,
        });
        setToStorage(StorageKeys.NUTRITION_CACHE_DATE, weekStart);

        showSuccess("Nutrition plan loaded from dataset!", 3000);
        loadHistory();
      } else {
        throw new Error(response.data.error || "Failed to load nutrition plan");
      }
    } catch (error) {
      console.error("Nutrition error:", error);
      if (error?.isCircuitOpen) {
        setCircuitOpen(true);
        const retrySec = Math.max(1, Math.ceil((error.retryAfterMs || 8000) / 1000));
        setRetryCountdown(retrySec);
        showError(`The AI planning service is temporarily unavailable. Please retry in ${retrySec} seconds.`, 5000);
      } else {
        const errorData = error.response?.data;
        let msg = "Failed to load nutrition plan.";
        if (typeof errorData?.error === 'string') {
          msg = errorData.error;
        } else if (errorData?.error?.message) {
          msg = errorData.error.message;
        } else if (errorData?.detail) {
          msg = typeof errorData.detail === 'string' ? errorData.detail : JSON.stringify(errorData.detail);
        } else if (error.message) {
          msg = error.message;
        }
        showError(msg, 5000);
      }
    } finally {
      setLoading(false);
    }
  };

  const loadHistory = async () => {
    try {
      const response = await getMealHistory();
      const historyData = response.data || [];
      setMealHistory(historyData);
      
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

              try {
                const cachedNutrition = safeJSONParse("nutritionPlan", null);
                const cachedDays = cachedNutrition?.days || [];
                const todayPlanDay = cachedDays[0];
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
                // Non-critical
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
      setMealHistory(safeJSONParse("mealHistoryGrouped", []));
      setLockedMeals(safeJSONParse("lockedMeals", {}));
    }
    setTickTimes(safeJSONParse("tickTimes", {}));
  };

  const loadCheckedFoods = () => setCheckedFoods(safeJSONParse("checkedFoods", {}));

  const handleCheckFood = (foodId, mealName, mealType, dayIdx) => {
    if (dayIdx !== todayIdx) { showInfo("You can only complete today's meals!", 2000); return; }

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
            calories: meal.totals?.calories || 0, protein: meal.totals?.protein_g || 0,
            carbs: meal.totals?.carbs_g || 0, fat: meal.totals?.fat_g || 0,
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
          
          saveUserMealToNode({
            dayName: today,
            mealType: meal.meal_type,
            name: meal.name,
            calories: meal.totals?.calories || 0,
            protein: meal.totals?.protein_g || 0,
            carbs: meal.totals?.carbs_g || 0,
            fat: meal.totals?.fat_g || 0,
            completedAt: mealData.completed_at
          }).then(res => {
            const totals = res?.data?.todayTotals;
            if (totals) {
              const mealsCount = ['breakfast', 'lunch', 'dinner'].filter(t => Boolean(dateEntry.meals?.[t])).length;
              setToStorage('_macroSync', JSON.stringify({
                calories: totals.calories,
                protein: totals.protein,
                carbs: totals.carbs,
                fat: totals.fat,
                mealsCount,
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

              const mealCal = meal.totals?.calories || 0;
              const actDetails = mealCal ? `${Math.round(mealCal)} cal consumed` : 'Meal logged';
              logActivityToBackend({
                activity_type: 'meal',
                name: 'Meal Completed',
                details: actDetails,
                type: 'meal',
                timestamp: new Date().toISOString()
              }).catch(err => console.error("Failed to log activity backup on frontend", err));
            }
          }).catch(err => console.error("Failed to sync meal to node db", err));

          const requiredMeals = ["breakfast", "lunch", "dinner"];
          const allMealsDone = requiredMeals.every((mType) => Boolean(dateEntry.meals?.[mType]));

          const water = parseFloat(String(getFromStorage(StorageKeys.WATER_INTAKE, 0) || 0)) || 0;
          const sleep = parseFloat(String(getFromStorage(StorageKeys.SLEEP_HOURS, 0) || 0)) || 0;
          const restDay = isTodayRestDay();
          const workoutDone = getFromStorage(StorageKeys.TODAY_WORKOUT_DONE) === "true";

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

  const openSwapModal = async (food, mealType, dayIdx) => {
    if (dayIdx !== todayIdx) { showInfo("You can only swap today's meals!", 2000); return; }
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
        current_calories: food.calories,
        current_protein: food.protein_g,
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
            serving: selectedSwap.serving || '',
            swap_group: selectedSwap.swap_group || '',
          };
        });
        const totals = {
          calories: Math.round(updatedFoods.reduce((s, f) => s + f.calories, 0)),
          protein_g: Math.round(updatedFoods.reduce((s, f) => s + f.protein_g, 0) * 10) / 10,
          carbs_g: Math.round(updatedFoods.reduce((s, f) => s + f.carbs_g, 0) * 10) / 10,
          fat_g: Math.round(updatedFoods.reduce((s, f) => s + f.fat_g, 0) * 10) / 10,
        };
        return { ...meal, foods: updatedFoods, totals };
      });
      const daily_totals = {
        calories: Math.round(updatedMeals.reduce((s, m) => s + m.totals.calories, 0)),
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

  const handleLogout = () => {
    setConfirmDialog({ 
      show: true, 
      message: 'Log out of Elevate?', 
      onConfirm: () => {
        if (typeof onLogout === 'function') {
          onLogout();
        } else {
          logoutSafe();
          navigate("/");
        }
      }
    });
  };

  const selectedDay = weeklyPlan?.days?.[selectedDayIndex];
  const today = getLocalDateStr();
  const selectedDayConsumedTotals = (() => {
    if (!selectedDay?.date) return { calories: 0, protein_g: 0, carbs_g: 0, fat_g: 0 };

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

    return {
      calories: Math.round(localCalories),
      protein_g: Math.round(localProtein * 10) / 10,
      carbs_g: Math.round(localCarbs * 10) / 10,
      fat_g: Math.round(localFat * 10) / 10,
    };
  })();

  const renderNavbarRight = () => (
    <>
      <div 
        style={styles.iconButton} 
        className="icon-hover" 
        onClick={() => setShowHistory(true)}
        title="Meal History"
      >
        📊
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
  );

  if (loading) {
    return (
      <div style={styles.page}>
        <AuroraBackground />
        <style>{nutritionAnimations}</style>
        <Navbar 
          isDark={theme === 'dark'}
          navigate={navigate} 
          activePage="nutrition" 
          onLogout={handleLogout}
          rightContent={renderNavbarRight()}
        />
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
            setConfirmDialog({ show: false, message: "", onConfirm: null });
          }}
          onCancel={() => setConfirmDialog({ show: false, message: "", onConfirm: null })}
        />
      </div>
    );
  }

  if (!weeklyPlan || !Array.isArray(weeklyPlan.days) || weeklyPlan.days.length === 0) {
    return (
      <div style={styles.page}>
        <AuroraBackground />
        <style>{nutritionAnimations}</style>
        <Navbar 
          isDark={theme === 'dark'}
          navigate={navigate} 
          activePage="nutrition" 
          onLogout={handleLogout}
          rightContent={renderNavbarRight()}
        />
        <div style={styles.container}>
          <div style={{ textAlign: "center", padding: "100px 20px" }}>
            <div style={{ fontSize: "64px", marginBottom: "24px" }}>🍽️</div>
            <div style={{ fontSize: "24px", fontWeight: "800", color: "var(--app-text)", marginBottom: "12px" }}>No Nutrition Plan</div>
            <div style={{ fontSize: "14px", color: "#71717a", marginBottom: "32px" }}>Generate a personalized meal plan based on your profile</div>
            <button
              onClick={fetchNutritionPlan}
              disabled={circuitOpen}
              style={{
                padding: "16px 40px",
                background: circuitOpen ? "var(--app-border)" : "linear-gradient(135deg, #6366f1 0%, #4f46e5 100%)",
                color: circuitOpen ? "var(--app-text-muted)" : "var(--app-text)",
                border: "none",
                borderRadius: "16px",
                fontSize: "16px",
                fontWeight: "700",
                cursor: circuitOpen ? "not-allowed" : "pointer",
                boxShadow: circuitOpen ? "none" : "0 4px 20px rgba(99, 102, 241, 0.4)",
                opacity: circuitOpen ? 0.6 : 1
              }}
            >
              {circuitOpen ? `Retry in ${retryCountdown}s` : "Generate Plan"}
            </button>
          </div>
        </div>
        <ConfirmDialog
          show={confirmDialog.show}
          message={confirmDialog.message}
          onConfirm={() => {
            if (confirmDialog.onConfirm) confirmDialog.onConfirm();
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
      <Navbar 
        isDark={theme === 'dark'}
        navigate={navigate} 
        activePage="nutrition" 
        onLogout={handleLogout}
        rightContent={renderNavbarRight()}
      />

      <div style={styles.container}>
        <h1 style={styles.header}>Weekly Nutrition Plan</h1>

        {/* Day Selector */}
        <div style={styles.daySelectorBar} className="nutrition-day-selector">
          {weeklyPlan.days.map((day, index) => {
            const isToday = index === todayIdx;
            const isOtherDay = index !== todayIdx;
            return (
              <div
                key={day.date}
                onClick={() => setSelectedDayIndex(index)}
                className="day-card-hover nutrition-day-card"
                data-selected={selectedDayIndex === index ? 'true' : 'false'}
                style={{
                  ...styles.dayCard,
                  ...(selectedDayIndex === index ? styles.dayCardSelected : {}),
                  ...(isToday ? styles.dayCardToday : {}),
                  opacity: isOtherDay && selectedDayIndex !== index ? 0.6 : 1
                }}
              >
                {selectedDayIndex === index && (
                  <div style={{ position: "absolute", top: 0, left: 0, right: 0, height: "3px", background: "linear-gradient(90deg, #6366f1, #a78bfa)", borderRadius: "20px 20px 0 0" }} />
                )}
                <div style={styles.dayName}>{day.day_name?.slice(0, 3)}</div>
                <div style={{ fontSize: "22px", fontWeight: "800", color: selectedDayIndex === index ? "var(--app-text)" : "#71717a", marginBottom: "8px", fontFamily: "monospace" }}>
                  {Number(String(day.date).split('-')[2])}
                </div>
                {isToday && <div style={{ fontSize: "9px", color: "#10b981", fontWeight: "800", marginTop: "6px", textTransform: "uppercase", letterSpacing: "1px" }}>Today</div>}
                {index < todayIdx && <div style={{ fontSize: "9px", color: "#71717a", fontWeight: "800", marginTop: "6px", textTransform: "uppercase", letterSpacing: "1px" }}>🔒 Past</div>}
                {index > todayIdx && <div style={{ fontSize: "9px", color: "#818cf8", fontWeight: "800", marginTop: "6px", textTransform: "uppercase", letterSpacing: "1px" }}>Upcoming</div>}
              </div>
            );
          })}
        </div>

        {/* Daily Summary */}
        {selectedDay && (
          <div style={styles.dailySummaryCard} className="nutrition-macro-grid">
            <div style={{ position: "absolute", top: 0, left: 0, right: 0, height: "2px", background: "linear-gradient(90deg, #6366f1, #a78bfa, #6366f1)", opacity: 0.6 }} />
            <MacroStat value={selectedDay.daily_totals?.calories || 0} label="Calories" color="var(--app-text)" icon="🔥" />
            <MacroStat value={`${selectedDay.daily_totals?.protein_g || 0}g`} label="Protein" color="#10b981" icon="💪" />
            <MacroStat value={`${selectedDay.daily_totals?.carbs_g || 0}g`} label="Carbs" color="#3b82f6" icon="⚡" />
            <MacroStat value={`${selectedDay.daily_totals?.fat_g || 0}g`} label="Fats" color="#f59e0b" icon="🥑" />
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
            const isSequenceLocked = selectedDayIndex === todayIdx ? !isMealUnlocked(mealTypeKey, selectedDayIndex) : false;
            const unlockMessage = isSequenceLocked ? getUnlockMessage(mealTypeKey) : null;
            const checkedCount = (meal.foods || []).filter(f => checkedFoods[`${selectedDay.date}-${f.id}`] || isCompleted).length;
            const isReadOnlyDay = selectedDayIndex !== todayIdx;

            return (
              <MealCard
                key={mealIndex}
                meal={meal}
                isLocked={isCompleted}
                isSequenceLocked={isSequenceLocked}
                unlockMessage={unlockMessage}
                checkedFoods={checkedFoods}
                tickTimes={tickTimes}
                today={selectedDay.date}
                checkedCount={checkedCount}
                totalCount={meal.foods ? meal.foods.length : 0}
                onCheckFood={handleCheckFood}
                onSwapFood={openSwapModal}
                dayIndex={selectedDayIndex}
                isFutureDay={isReadOnlyDay}
              />
            );
          })}
        </div>
      </div>

      {/* History Panel */}
      {showHistory && (
        <HistoryPanel
          mealHistory={mealHistory}
          expandedDates={expandedDates}
          setExpandedDates={setExpandedDates}
          expandedMeals={expandedMeals}
          setExpandedMeals={setExpandedMeals}
          onClose={() => setShowHistory(false)}
          today={today}
        />
      )}

      {/* Swap Modal */}
      <MealSwapModal
        show={swapModal.show}
        food={swapModal.food}
        swapLoading={swapLoading}
        swapOptions={swapOptions}
        selectedSwap={selectedSwap}
        setSelectedSwap={setSelectedSwap}
        onClose={() => setSwapModal({ show: false, food: null, mealType: null, dayIndex: null })}
        onConfirmSwap={confirmSwap}
      />

      <ConfirmDialog
        show={confirmDialog.show}
        message={confirmDialog.message}
        onConfirm={() => {
          if (confirmDialog.onConfirm) {
            confirmDialog.onConfirm();
          }
          setConfirmDialog({ show: false, message: "", onConfirm: null });
        }}
        onCancel={() => setConfirmDialog({ show: false, message: "", onConfirm: null })}
      />
    </div>
  );
}

export default Nutrition;
