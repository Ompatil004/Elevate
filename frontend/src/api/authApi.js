import { AuthAPI } from './apiClient';

export const registerUser = (userData) => AuthAPI.post('/auth/register', userData);
export const loginUser = (userData) => AuthAPI.post('/auth/login', userData);
export const loginWithGoogle = (tokenId) => AuthAPI.post('/auth/google', { token: tokenId });
export const logoutUser = () => AuthAPI.post('/auth/logout');
export const requestPasswordReset = (payload) => AuthAPI.post('/auth/reset-password/request', payload);
export const confirmPasswordReset = (payload) => AuthAPI.post('/auth/reset-password/confirm', payload);
export const getSessionStatus = () => AuthAPI.get('/auth/session');
