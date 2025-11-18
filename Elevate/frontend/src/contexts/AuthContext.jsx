import { createContext, useContext, useEffect, useState } from 'react';
import { authAPI } from '../services/api.js';

// Create the context
const AuthContext = createContext();

// Create the provider component
export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [token, setToken] = useState(localStorage.getItem('token'));
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [isLoading, setIsLoading] = useState(true);

  // Check if user is authenticated on initial load
  useEffect(() => {
    const token = localStorage.getItem('token');
    if (token && !user) { // Only fetch profile if token exists and user is not already set
      setToken(token);
      setIsAuthenticated(true);
      fetchUserProfile();
    } else {
      setIsLoading(false);
    }
  }, []); // Empty dependency array to only run once on mount

  // Fetch user profile if authenticated
  const fetchUserProfile = async () => {
    try {
      const response = await authAPI.getProfile();
      setUser(response.data);
      setIsAuthenticated(true);
    } catch (error) {
      console.error('Failed to fetch user profile:', error);
      logout();
    } finally {
      setIsLoading(false);
    }
  };

  // Login function
  const login = async (email, password) => {
    try {
      const response = await authAPI.login({ email, password });

      // Save token to localStorage and state
      const { token, user: userData } = response.data;
      localStorage.setItem('token', token);
      setToken(token);
      setUser(userData);
      setIsAuthenticated(true);
      setIsLoading(false); // Set loading to false after successful login

      return response.data;
    } catch (error) {
      console.error('Login failed:', error);
      setIsLoading(false); // Ensure loading state is properly handled after error
      throw error.response?.data?.msg || 'Login failed';
    }
  };

  // Register function
  const register = async (userData) => {
    try {
      const response = await authAPI.register(userData);

      // Save token to localStorage and state
      const { token, user: createdUser } = response.data;
      localStorage.setItem('token', token);
      setToken(token);
      setUser(createdUser);
      setIsAuthenticated(true);
      setIsLoading(false); // Set loading to false after successful registration

      return response.data;
    } catch (error) {
      console.error('Registration failed:', error);
      setIsLoading(false); // Ensure loading state is properly handled after error
      throw error.response?.data?.msg || 'Registration failed';
    }
  };

  // Logout function
  const logout = () => {
    localStorage.removeItem('token');
    setToken(null);
    setUser(null);
    setIsAuthenticated(false);
    setIsLoading(false);
  };

  // Update user function
  const updateUser = async (userData) => {
    try {
      const response = await authAPI.updateProfile(userData);
      setUser(response.data);
      return response.data;
    } catch (error) {
      console.error('Update user failed:', error);
      throw error.response?.data?.msg || 'Update user failed';
    }
  };

  // Complete user profile function
  const completeProfile = async (profileData) => {
    try {
      const response = await authAPI.completeProfile(profileData);
      setUser(response.data);
      return response.data;
    } catch (error) {
      console.error('Complete profile failed:', error);
      throw error.response?.data?.msg || 'Complete profile failed';
    }
  };

  // Check profile setup completion
  const checkProfileSetup = () => {
    return user?.profileCompleted || false;
  };

  const contextValue = {
    user,
    token,
    isAuthenticated,
    isLoading,
    login,
    register,
    logout,
    updateUser,
    completeProfile,
    profileSetupComplete: user?.profileCompleted || false,
    checkProfileSetup,
  };

  return (
    <AuthContext.Provider value={contextValue}>
      {children}
    </AuthContext.Provider>
  );
};

// Custom hook to use the auth context
export const useAuth = () => {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};