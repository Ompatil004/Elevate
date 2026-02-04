import axios from 'axios';

const API_URL = 'http://localhost:5000/api';
const API_BASE_URL = 'http://localhost:8000';

const API = axios.create({
    baseURL: API_URL,
    headers: {
        'Content-Type': 'application/json'
    }
});

API.interceptors.request.use(
    (config) => {
        const token = localStorage.getItem('token');
        console.log('🔑 Token from localStorage:', token ? 'EXISTS' : 'MISSING');

        if (token) {
            config.headers['x-auth-token'] = token;
            console.log('✅ Token attached to request');
        }

        return config;
    },
    (error) => {
        return Promise.reject(error);
    }
);

export const registerUser = (userData) => API.post('/auth/register', userData);
export const loginUser = (userData) => API.post('/auth/login', userData);
export const validateToken = () => API.post('/auth/validate');
export const loginWithGoogle = (token) => API.post('/auth/google', { token });

export const getProfile = () => API.get('/profile');
export const saveProfile = (profileData) => API.post('/profile/update', profileData);
export const saveUserProfile = (profileData) => API.post('/profile/update', profileData);

// Function to update profile and regenerate workouts
export const updateProfileAndRegenerateWorkouts = (profileData) =>
    axios.put(`${API_BASE_URL}/profile/update`, profileData);

// Function to clear workout plan cache when profile changes require regeneration
export const clearWorkoutPlanCache = () => {
    localStorage.removeItem('workoutPlan');
    localStorage.removeItem('workoutPlanProfile');
};

export const generateAIPlan = (profileData) =>
    axios.post(`${API_BASE_URL}/generate-plan`, profileData);

export const saveTrends = (trendData) => API.post('/profile/trends', trendData);
export const getTrends = (period = 'week') => API.get(`/profile/trends?period=${period}`);

export const saveWorkoutPlan = async (workoutData) => {
    const response = await fetch(`${API_BASE_URL}/api/workout/save`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(workoutData)
    });
    return await response.json();
};

export const saveWorkoutCompletion = (workoutData) =>
    axios.post(`${API_BASE_URL}/workout-completion`, workoutData);

export const getWorkoutHistory = () =>
    axios.get(`${API_BASE_URL}/workout-history`);

export const saveMealPlan = async (mealData) => {
    const response = await fetch(`${API_BASE_URL}/api/meals/save`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(mealData)
    });
    return await response.json();
};

export const saveMealCompletion = (mealData) =>
    axios.post(`${API_BASE_URL}/meal-completion`, mealData);

export const getMealHistory = () =>
    axios.get(`${API_BASE_URL}/meal-history`);

export const updateStreak = (streakData) =>
    axios.post(`${API_BASE_URL}/update-streak`, streakData);

export const getUserProgress = () =>
    axios.get(`${API_BASE_URL}/user-progress`);