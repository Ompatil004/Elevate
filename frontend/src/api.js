/**
 * Elevate API Gateway
 *
 * Modularized in Phase P2. Domain-specific implementations are located in:
 *   - ./api/apiClient.js  (Axios instances, CSRF interceptors, base URLs)
 *   - ./api/authApi.js    (Registration, Login, Google OAuth, Passwords, Session)
 *   - ./api/profileApi.js (Profile setup, trends, activities, history sync)
 *   - ./api/workoutApi.js (Plan generation, async polling, deduplication, cache)
 *   - ./api/nutritionApi.js (Meal planning, macro targets, swaps, plate logging)
 *   - ./api/adminApi.js   (Admin authentication, user moderation, audit logs)
 *   - ./api/chatbotApi.js (Conversational coaching, Gemini proxying, health)
 */

export * from './api/index';
export { default } from './api/index';
