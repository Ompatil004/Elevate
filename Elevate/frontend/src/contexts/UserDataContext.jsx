import { createContext, useContext, useState, useEffect } from 'react';
import { useAuth } from './AuthContext.jsx';
import { exerciseAPI, mlAPI, authAPI } from '../services/api.js';

// Create the context
const UserDataContext = createContext();

// Create the provider component
export const UserDataProvider = ({ children }) => {
  const [userProfile, setUserProfile] = useState(null);
  const [workoutPlan, setWorkoutPlan] = useState(null);
  const [mealPlan, setMealPlan] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const { user, updateUser } = useAuth();

  // Load user profile when user changes
  useEffect(() => {
    if (user) {
      setUserProfile(user);
    }
  }, [user]);

  // Load user profile from backend
  const loadUserProfile = async () => {
    setLoading(true);
    setError(null);
    try {
      const response = await authAPI.getProfile();
      setUserProfile(response.data);
    } catch (err) {
      setError(err.message || 'Failed to load user profile');
    } finally {
      setLoading(false);
    }
  };

  // Update user profile
  const updateProfile = async (profileData) => {
    setLoading(true);
    setError(null);
    try {
      const response = await authAPI.updateProfile(profileData);
      setUserProfile(response.data);
      // Also update in auth context
      await updateUser(response.data);
    } catch (err) {
      setError(err.message || 'Failed to update profile');
      throw err;
    } finally {
      setLoading(false);
    }
  };

  // Generate workout plan
  const generateWorkoutPlan = async (workoutData) => {
    setLoading(true);
    setError(null);
    try {
      const response = await mlAPI.recommendWorkout(workoutData);
      setWorkoutPlan(response.data);
    } catch (err) {
      setError(err.message || 'Failed to generate workout plan');
      throw err;
    } finally {
      setLoading(false);
    }
  };

  // Generate meal plan
  const generateMealPlan = async (mealData) => {
    setLoading(true);
    setError(null);
    try {
      const response = await mlAPI.recommendMeal(mealData);
      setMealPlan(response.data);
    } catch (err) {
      setError(err.message || 'Failed to generate meal plan');
      throw err;
    } finally {
      setLoading(false);
    }
  };

  const contextValue = {
    userProfile,
    setUserProfile,
    workoutPlan,
    setWorkoutPlan,
    mealPlan,
    setMealPlan,
    loading,
    error,
    loadUserProfile,
    updateProfile,
    generateWorkoutPlan,
    generateMealPlan,
  };

  return (
    <UserDataContext.Provider value={contextValue}>
      {children}
    </UserDataContext.Provider>
  );
};

// Custom hook to use the user data context
export const useUserData = () => {
  const context = useContext(UserDataContext);
  if (context === undefined) {
    throw new Error('useUserData must be used within a UserDataProvider');
  }
  return context;
};