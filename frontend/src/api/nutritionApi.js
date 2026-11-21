import axios from 'axios';
import { AuthAPI, FitnessAPI } from './apiClient';
import { nutritionCB, withCircuitBreaker } from '../utils/circuitBreaker';

const _slimStringList = (value, maxItems = 24) =>
  (Array.isArray(value) ? value : [])
    .slice(0, maxItems)
    .map((item) => (typeof item === 'string' ? item : String(item ?? '')).trim())
    .filter(Boolean);

const _slimWorkoutDayForNutrition = (day) => {
  if (!day || typeof day !== 'object') return day;
  return {
    day: day.day,
    day_of_week: day.day_of_week,
    type: day.type,
    focus: day.focus,
    note: day.note,
    exercises: Array.isArray(day.exercises)
      ? day.exercises.map((ex) => ({
          name: ex?.name,
          sets: ex?.sets,
          reps: ex?.reps,
        }))
      : [],
  };
};

export const _pickNutritionPayload = (payload) => {
  if (!payload || typeof payload !== 'object' || Array.isArray(payload)) return {};
  const weekly = payload.weekly_workout_plan;
  return {
    age: payload.age,
    weight: payload.weight,
    height: payload.height,
    gender: payload.gender,
    goal: payload.goal,
    dietary_preference: payload.dietary_preference,
    allergies: _slimStringList(payload.allergies),
    activity_level: payload.activity_level || 'Moderate',
    workout_intensity: payload.workout_intensity || 'moderate',
    weekly_workout_plan: Array.isArray(weekly) ? weekly.map(_slimWorkoutDayForNutrition) : [],
  };
};

const activeNutritionRequests = new Map();

const getNutritionDeduplicationKey = (payload) => {
  if (!payload || typeof payload !== 'object') return 'default';
  const userId = payload.user_id || payload._id || payload.id || 'anonymous';
  const p = _pickNutritionPayload(payload);
  return `nutrition:${userId}:${p.age}:${p.weight}:${p.height}:${p.goal}:${p.dietary_preference}:${p.workout_intensity}`;
};

export const generateNutritionPlan = (payload) => {
  const key = getNutritionDeduplicationKey(payload);
  if (activeNutritionRequests.has(key)) {
    const active = activeNutritionRequests.get(key);
    const wrappedPromise = Promise.resolve(active.promise);
    wrappedPromise.promise = active.promise;
    wrappedPromise.cancel = () => active.controller?.abort();
    return wrappedPromise;
  }

  const controller = new AbortController();
  const { signal } = controller;

  const promise = withCircuitBreaker(nutritionCB, async () => {
    const response = await FitnessAPI.post('/nutrition', _pickNutritionPayload(payload), { signal });
    if (!response?.data || response.data.success !== true || !response.data.nutrition?.weekly_plan) {
      throw new Error('Malformed nutrition response structure');
    }
    return response;
  })
    .catch((error) => {
      if (axios.isCancel?.(error) || error?.name === 'CanceledError' || error?.name === 'AbortError') {
        return null;
      }
      throw error;
    })
    .finally(() => {
      activeNutritionRequests.delete(key);
    });

  activeNutritionRequests.set(key, { promise, controller });

  const retPromise = promise;
  retPromise.promise = retPromise;
  retPromise.cancel = () => controller.abort();

  return retPromise;
};

export const getNutritionSwapOptions = (payload) =>
  FitnessAPI.post('/nutrition/swap', payload);

export const swapRestToWorkout = (payload) =>
  FitnessAPI.post('/api/swap-rest-to-workout', payload);

export const swapWorkoutToRest = (payload) =>
  FitnessAPI.post('/api/swap-workout-to-rest', payload);

export const suggestDailyMeals = (profileData, intensityFocus) =>
  FitnessAPI.post('/nutrition/daily', {
    profile: _pickNutritionPayload(profileData),
    intensity_focus: intensityFocus || 'moderate',
  });

export const saveMealPlan = (mealData) =>
  AuthAPI.post('/users/meals/save', mealData);

export const saveUserMealToNode = (mealData) =>
  AuthAPI.post('/users/meals/save', mealData);

export const saveMealCompletion = (mealData) =>
  FitnessAPI.post('/meal-completion', mealData);

export const getMealHistory = () =>
  AuthAPI.get('/profile/meal-history');

export const saveMealHistory = (data) =>
  AuthAPI.post('/profile/meal-history', data);

export const getExternalNutritionData = (query) =>
  AuthAPI.get('/users/external/nutrition', { params: { query } });
