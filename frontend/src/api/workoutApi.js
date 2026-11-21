import axios from 'axios';
import { AuthAPI, FitnessAPI } from './apiClient';
import { workoutCB, withCircuitBreaker } from '../utils/circuitBreaker';

const _slimStringList = (value, maxItems = 24) =>
  (Array.isArray(value) ? value : [])
    .slice(0, maxItems)
    .map((item) => (typeof item === 'string' ? item : String(item ?? '')).trim())
    .filter(Boolean);

export const _pickWorkoutProfile = (profile) => {
  if (!profile || typeof profile !== 'object' || Array.isArray(profile)) return {};
  const userId = profile.user_id || profile._id || profile.id;
  return {
    ...(userId ? { user_id: String(userId) } : {}),
    age: profile.age,
    weight: profile.weight,
    height: profile.height,
    gender: profile.gender,
    goal: profile.goal,
    experience: profile.experience,
    days_per_week: profile.days_per_week,
    equipment: _slimStringList(profile.equipment),
    body_issues: _slimStringList(profile.body_issues),
    streak: typeof profile.streak === 'number' ? profile.streak : undefined,
    consistency: typeof profile.consistency === 'number' ? profile.consistency : undefined,
    firstWorkoutDay: profile.firstWorkoutDay,
    registrationDate: profile.registrationDate,
    is_new_user_week: profile.is_new_user_week,
  };
};

const activeWorkoutRequests = new Map();

const getWorkoutDeduplicationKey = (payload) => {
  if (!payload || typeof payload !== 'object') return 'default';
  const userId = payload.user_id || payload._id || payload.id || 'anonymous';
  const p = _pickWorkoutProfile(payload);
  return `workout:${userId}:${p.age}:${p.weight}:${p.height}:${p.goal}:${p.experience}:${p.days_per_week}:${(p.equipment || []).join(',')}`;
};

export const getWeeklyWorkoutPlan = () =>
  FitnessAPI.get('/api/weekly-plan');

export const getWorkoutSwapOptions = (dayIndex) =>
  FitnessAPI.get('/api/swap-options', { params: { day_index: dayIndex } });

export const generateAIPlan = (profileData) =>
  FitnessAPI.post('/generate-plan', profileData);

export const saveWorkoutPlan = (workoutData) =>
  AuthAPI.post('/users/workout/save', workoutData);

export const saveUserWorkoutToNode = (workoutData) =>
  AuthAPI.post('/users/workout/save', workoutData);

export const saveWorkoutCompletion = (workoutData) =>
  FitnessAPI.post('/workout-completion', workoutData);

export const getWorkoutHistory = () =>
  AuthAPI.get('/profile/workout-history');

export const saveWorkoutHistory = (data) =>
  AuthAPI.post('/profile/workout-history', data);

export const undoWorkoutSwapHistory = () =>
  AuthAPI.post('/profile/workout-history/undo-swap');

export const clearWorkoutPlanCache = () => {
  try {
    localStorage.removeItem('workoutPlan');
    localStorage.removeItem('workoutPlanTimestamp');
    localStorage.removeItem('workoutPlanVersion');
    localStorage.removeItem('workoutPlanChecksum');
  } catch {
    // ignore
  }
};

export const generateWorkout = (profileData) => {
  const key = getWorkoutDeduplicationKey(profileData);
  if (activeWorkoutRequests.has(key)) {
    const active = activeWorkoutRequests.get(key);
    const wrappedPromise = Promise.resolve(active.promise);
    wrappedPromise.promise = active.promise;
    wrappedPromise.cancel = () => active.controller?.abort();
    return wrappedPromise;
  }

  const controller = new AbortController();
  const { signal } = controller;

  const promise = withCircuitBreaker(workoutCB, async () => {
    const response = await FitnessAPI.post('/workout', _pickWorkoutProfile(profileData), { signal });
    const hasWorkoutArray = Array.isArray(response?.data?.workout) || 
      Array.isArray(response?.data?.data?.workout) || 
      Array.isArray(response?.data?.data?.weekly_plan) ||
      Boolean(response?.data?.data?.weekly_schedule);
    if (!response?.data || response.data.success !== true || !hasWorkoutArray) {
      throw new Error('Malformed workout response structure');
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
      activeWorkoutRequests.delete(key);
    });

  activeWorkoutRequests.set(key, { promise, controller });

  const retPromise = promise;
  retPromise.promise = retPromise;
  retPromise.cancel = () => controller.abort();

  return retPromise;
};

export const generateWorkoutAsync = async (
  profileData,
  onProgress,
  pollMs = 2000,
  maxWait = 60000,
  abortSignal = null
) => {
  const startRes = await FitnessAPI.post('/workout/async', _pickWorkoutProfile(profileData));
  const startData = startRes.data;

  if (startData.status === 'complete') {
    onProgress && onProgress(100);
    return startData.plan;
  }

  const jobId = startData.job_id;
  if (!jobId) throw new Error('No job_id returned from async endpoint');

  const started = Date.now();
  let progress = 10;
  onProgress && onProgress(progress);

  return new Promise((resolve, reject) => {
    let settled = false;
    let timer = null;

    const cleanup = () => {
      if (timer) clearInterval(timer);
      timer = null;
      if (abortSignal) {
        abortSignal.removeEventListener('abort', onAbort);
      }
    };

    const finishResolve = (value) => {
      if (settled) return;
      settled = true;
      cleanup();
      resolve(value);
    };

    const finishReject = (err) => {
      if (settled) return;
      settled = true;
      cleanup();
      reject(err);
    };

    const onAbort = () => {
      finishReject(new Error('Workout generation cancelled'));
    };

    if (abortSignal?.aborted) {
      onAbort();
      return;
    }

    if (abortSignal) {
      abortSignal.addEventListener('abort', onAbort, { once: true });
    }

    timer = setInterval(async () => {
      if (settled) return;
      if (Date.now() - started > maxWait) {
        finishReject(new Error('Workout plan generation timed out after 60s'));
        return;
      }
      try {
        const pollRes = await FitnessAPI.get(`/workout/status/${jobId}`);
        const pollData = pollRes.data;
        if (pollData.status === 'complete') {
          onProgress && onProgress(100);
          finishResolve(pollData.plan);
        } else if (pollData.status === 'error') {
          finishReject(new Error(pollData.error || 'Plan generation failed'));
        } else {
          if (progress < 90) {
            progress = Math.min(progress + 15, 89);
            onProgress && onProgress(progress);
          } else {
            onProgress && onProgress(-1);
          }
        }
      } catch (err) {
        finishReject(err);
      }
    }, pollMs);
  });
};

export const invalidateWorkoutCache = async (profileData) => {
  try {
    await FitnessAPI.post('/workout/cache/invalidate', _pickWorkoutProfile(profileData));
  } catch {
    // silent
  }
};

export const postSessionResult = (payload) =>
  FitnessAPI.post('/api/workout/session-result', payload);

export const saveDailyLog = (payload, config = {}) =>
  FitnessAPI.post('/api/daily-log', payload, config);

export const getWeeklyLogs = (config = {}) =>
  FitnessAPI.get('/api/daily-log/week', config);

export const getExternalExerciseData = (muscle) =>
  AuthAPI.get('/users/external/exercise', { params: { muscle } });
