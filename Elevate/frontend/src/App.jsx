import { HashRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider, useAuth } from '@/contexts/AuthContext.jsx';
import { UserDataProvider } from '@/contexts/UserDataContext.jsx';
import { useState, useEffect } from 'react';
import { Landing } from '@/features/auth/components/Landing.jsx';
import { Auth } from '@/features/auth/components/Auth.jsx';
import { ProfileSetup } from '@/features/user/components/ProfileSetup.jsx';
import { Dashboard } from '@/features/user/components/Dashboard.jsx';
import { Workout } from '@/features/workout/components/Workout.jsx';
import { MealPlan } from '@/features/mealPlanner/components/MealPlan.jsx';
import { Analytics } from '@/features/user/components/Analytics.jsx';
import { Navbar } from '@/components/Navbar.jsx';
import { PoseDetection } from '@/features/poseDetection/components/PoseDetection.jsx';
import { Chatbot } from '@/features/chatbot/components/Chatbot.jsx';

// Wrapper component to access auth context
function AppContent() {
  const { isAuthenticated, isLoading, checkProfileSetup } = useAuth();

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
            isAuthenticated ?
            (checkProfileSetup() ? <Navigate to="/dashboard" /> : <Navigate to="/profile-setup" />) :
            <Auth />
          }
        />
        <Route
          path="/profile-setup"
          element={
            !isAuthenticated ? <Navigate to="/auth" /> :
            checkProfileSetup() ? <Navigate to="/dashboard" /> :
            <ProfileSetup />
          }
        />
        <Route
          path="/dashboard"
          element={
            !isAuthenticated ? <Navigate to="/auth" /> :
            !checkProfileSetup() ? <Navigate to="/profile-setup" /> :
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