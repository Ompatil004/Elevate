// Re-export circuit breakers for UI components
export {
  workoutCB,
  nutritionCB,
  backgroundCB,
  withCircuitBreaker,
  CircuitOpenError,
} from '../utils/circuitBreaker';

// Base client & URLs
export {
  API_BASE_URL,
  PYTHON_API_URL,
  AuthAPI,
  FitnessAPI,
  getCsrfToken,
  resetCsrfCache,
  default as apiClient,
} from './apiClient';

// Auth API
export {
  registerUser,
  loginUser,
  loginWithGoogle,
  logoutUser,
  requestPasswordReset,
  confirmPasswordReset,
  getSessionStatus,
} from './authApi';

// Profile API
export {
  getProfile,
  saveProfile,
  saveUserProfile,
  saveTrends,
  getTrends,
  updateStreak,
  getUserProgress,
  logActivityToBackend,
  getRecentActivities,
  syncActivitiesToBackend,
  updateProfileAndRegenerateWorkouts,
} from './profileApi';

// Workout API
export {
  getWeeklyWorkoutPlan,
  getWorkoutSwapOptions,
  generateAIPlan,
  saveWorkoutPlan,
  saveUserWorkoutToNode,
  saveWorkoutCompletion,
  getWorkoutHistory,
  saveWorkoutHistory,
  undoWorkoutSwapHistory,
  clearWorkoutPlanCache,
  generateWorkout,
  generateWorkoutAsync,
  invalidateWorkoutCache,
  postSessionResult,
  saveDailyLog,
  getWeeklyLogs,
  getExternalExerciseData,
  _pickWorkoutProfile,
} from './workoutApi';

// Nutrition API
export {
  generateNutritionPlan,
  getNutritionSwapOptions,
  swapRestToWorkout,
  swapWorkoutToRest,
  suggestDailyMeals,
  saveMealPlan,
  saveUserMealToNode,
  saveMealCompletion,
  getMealHistory,
  saveMealHistory,
  getExternalNutritionData,
  _pickNutritionPayload,
} from './nutritionApi';

// Admin API
export {
  adminLogin,
  adminLogout,
  adminVerify,
  adminGetUsers,
  adminGetUserStats,
  adminGetUser,
  adminSuspendUser,
  adminActivateUser,
  adminResetUserPassword,
  adminDeleteUser,
  adminGetHealth,
  adminGetSystemStats,
  adminGetMaintenance,
  adminSetMaintenance,
  adminGetAuditLogs,
  adminCreateAnnouncement,
  adminDeleteAnnouncement,
  adminGetAnnouncements,
  adminGetExercises,
  adminCreateExercise,
  adminUpdateExercise,
  adminDeleteExercise,
  adminGetWorkoutRules,
  adminSetWorkoutRules,
} from './adminApi';

// Chatbot API
export {
  sendChatbotMessage,
  getHealth,
} from './chatbotApi';

import { AuthAPI } from './apiClient';
export default AuthAPI;
