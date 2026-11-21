import { AuthAPI } from './apiClient';

export const adminLogin = (payload) => AuthAPI.post('/admin/login', payload);
export const adminLogout = () => AuthAPI.post('/admin/logout');
export const adminVerify = () => AuthAPI.get('/admin/verify');

export const adminGetUsers = (params) => AuthAPI.get('/admin/users', { params });
export const adminGetUserStats = () => AuthAPI.get('/admin/users/stats/overview');
export const adminGetUser = (id) => AuthAPI.get(`/admin/users/${id}`);
export const adminSuspendUser = (id, reason) => AuthAPI.post(`/admin/users/${id}/suspend`, { reason });
export const adminActivateUser = (id) => AuthAPI.post(`/admin/users/${id}/activate`);
export const adminResetUserPassword = (id) => AuthAPI.post(`/admin/users/${id}/reset-password`);
export const adminDeleteUser = (id) => AuthAPI.delete(`/admin/users/${id}`);

export const adminGetHealth = () => AuthAPI.get('/admin/system/health');
export const adminGetSystemStats = () => AuthAPI.get('/admin/system/stats');
export const adminGetMaintenance = () => AuthAPI.get('/admin/system/maintenance');
export const adminSetMaintenance = (payload) => AuthAPI.post('/admin/system/maintenance', payload);
export const adminGetAuditLogs = (params) => AuthAPI.get('/admin/system/audit-logs', { params });
export const adminCreateAnnouncement = (payload) => AuthAPI.post('/admin/system/announcement', payload);
export const adminDeleteAnnouncement = (announcementId) => AuthAPI.delete(`/admin/system/announcements/${announcementId}`);
export const adminGetAnnouncements = () => AuthAPI.get('/admin/system/announcements');

export const adminGetExercises = (params) => AuthAPI.get('/admin/content/exercises', { params });
export const adminCreateExercise = (payload) => AuthAPI.post('/admin/content/exercises', payload);
export const adminUpdateExercise = (id, payload) => AuthAPI.put(`/admin/content/exercises/${id}`, payload);
export const adminDeleteExercise = (id) => AuthAPI.delete(`/admin/content/exercises/${id}`);
export const adminGetWorkoutRules = () => AuthAPI.get('/admin/content/workout-rules');
export const adminSetWorkoutRules = (rules) => AuthAPI.post('/admin/content/workout-rules', { rules });
