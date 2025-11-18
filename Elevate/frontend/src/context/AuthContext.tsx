import { createContext, useContext, useEffect, useState } from 'react';
import { authAPI } from '../services/api';

// Define the shape of our authentication context
interface AuthContextType {
  user: any | null;
  token: string | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  login: (email: string, password: string) => Promise<void>;
  register: (userData: RegisterData) => Promise<void>;
  logout: () => void;
  updateUser: (userData: any) => Promise<void>;
}

interface RegisterData {
  name: string;
  email: string;
  password: string;
  fitnessGoal?: string;
}

// Create the context with a default value
const AuthContext = createContext<AuthContextType | undefined>(undefined);

// Create the provider component
export const AuthProvider = ({ children }: { children: React.ReactNode }) => {
  const [user, setUser] = useState<any | null>(null);
  const [token, setToken] = useState<string | null>(localStorage.getItem('token'));
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [isLoading, setIsLoading] = useState(true);

  // Check if user is authenticated on initial load
  useEffect(() => {
    const token = localStorage.getItem('token');
    if (token) {
      setToken(token);
      setIsAuthenticated(true);
      fetchUserProfile();
    } else {
      setIsLoading(false);
    }
  }, []);

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
  const login = async (email: string, password: string) => {
    try {
      const response = await authAPI.login({ email, password });
      
      // Save token to localStorage and state
      const { token, user: userData } = response.data;
      localStorage.setItem('token', token);
      setToken(token);
      setUser(userData);
      setIsAuthenticated(true);
      
      return response.data;
    } catch (error: any) {
      console.error('Login failed:', error);
      throw error.response?.data?.msg || 'Login failed';
    }
  };

  // Register function
  const register = async (userData: RegisterData) => {
    try {
      const response = await authAPI.register(userData);
      
      // Save token to localStorage and state
      const { token, user: createdUser } = response.data;
      localStorage.setItem('token', token);
      setToken(token);
      setUser(createdUser);
      setIsAuthenticated(true);
      
      return response.data;
    } catch (error: any) {
      console.error('Registration failed:', error);
      throw error.response?.data?.msg || 'Registration failed';
    }
  };

  // Logout function
  const logout = () => {
    localStorage.removeItem('token');
    setToken(null);
    setUser(null);
    setIsAuthenticated(false);
  };

  // Update user function
  const updateUser = async (userData: any) => {
    try {
      const response = await authAPI.updateProfile(userData);
      setUser(response.data);
      return response.data;
    } catch (error: any) {
      console.error('Update user failed:', error);
      throw error.response?.data?.msg || 'Update user failed';
    }
  };

  const contextValue: AuthContextType = {
    user,
    token,
    isAuthenticated,
    isLoading,
    login,
    register,
    logout,
    updateUser,
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