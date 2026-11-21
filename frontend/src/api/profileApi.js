import { AuthAPI, FitnessAPI } from './apiClient';

export const getProfile = () => AuthAPI.get('/profile');
export const saveProfile = (profileData) => AuthAPI.post('/profile/update', profileData);
export const saveUserProfile = (profileData) => AuthAPI.post('/profile/update', profileData);
export const saveTrends = (trendData) => AuthAPI.post('/profile/trends', trendData);
export const getTrends = (period = 'week') => AuthAPI.get(`/profile/trends?period=${period}`);
export const updateStreak = (streakData) => AuthAPI.post('/profile/streak', streakData);
export const getUserProgress = () => AuthAPI.get('/profile/progress');

// Activity logging
export const logActivityToBackend = (activityData) =>
  AuthAPI.post('/profile/activities/log', activityData);

export const getRecentActivities = (limit = 20) =>
  AuthAPI.get('/profile/activities/recent', { params: { limit } });

export const syncActivitiesToBackend = (activities) =>
  AuthAPI.post('/profile/activities/sync', { activities });

// Profile update with workout regeneration
export const updateProfileAndRegenerateWorkouts = (profileData) =>
  FitnessAPI.put('/profile/update-safe', profileData);
