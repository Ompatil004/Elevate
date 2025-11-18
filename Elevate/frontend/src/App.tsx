import { HashRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider, useAuth } from '@/context/AuthContext';
import { UserDataProvider } from '@/context/UserDataContext';
import { useState, useEffect } from 'react';
import { Landing } from '@/components/Landing';
import { Auth } from '@/components/Auth';
import { ProfileSetup } from '@/components/ProfileSetup';
import { Dashboard } from '@/components/Dashboard';
import { Workout } from '@/components/Workout';
import { MealPlan } from '@/components/MealPlan';
import { Analytics } from '@/components/Analytics';
import { Navbar } from '@/components/Navbar';
import { PoseDetection } from '@/components/pose-detection/PoseDetection';
import { Chatbot } from '@/components/chatbot/Chatbot';

// Wrapper component to access auth context
function AppContent() {
  const { isAuthenticated, isLoading } = useAuth();
  const [hasProfile, setHasProfile] = useState(false);

  if (isLoading) {
    return <div className="flex items-center justify-center min-h-screen">Loading...</div>;
  }

  return (
    <div className="min-h-screen bg-white">
      {isAuthenticated && <Navbar />}
      <Routes>
        <Route path="/" element={<Landing />} />
        <Route
          path="/auth"
          element={
            isAuthenticated ? <Navigate to="/dashboard" /> :
            <Auth />
          }
        />
        <Route
          path="/profile-setup"
          element={
            !isAuthenticated ? <Navigate to="/auth" /> :
            <ProfileSetup />
          }
        />
        <Route
          path="/dashboard"
          element={
            !isAuthenticated ? <Navigate to="/auth" /> :
            !hasProfile ? <Navigate to="/profile-setup" /> :
            <Dashboard />
          }
        />
        <Route
          path="/workout"
          element={
            !isAuthenticated ? <Navigate to="/auth" /> :
            <Workout />
          }
        />
        <Route
          path="/meal-plan"
          element={
            !isAuthenticated ? <Navigate to="/auth" /> :
            <MealPlan />
          }
        />
        <Route
          path="/analytics"
          element={
            !isAuthenticated ? <Navigate to="/auth" /> :
            <Analytics />
          }
        />
        <Route
          path="/pose-detection"
          element={
            !isAuthenticated ? <Navigate to="/auth" /> :
            <PoseDetection />
          }
        />
        <Route
          path="/chatbot"
          element={
            !isAuthenticated ? <Navigate to="/auth" /> :
            <Chatbot />
          }
        />
      </Routes>
    </div>
  );
}

export default function App() {
  return (
    <AuthProvider>
      <UserDataProvider>
        <Router>
          <AppContent />
        </Router>
      </UserDataProvider>
    </AuthProvider>
  );
}
