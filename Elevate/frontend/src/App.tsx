import { HashRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { useState } from 'react';
import { Landing } from './components/Landing';
import { Auth } from './components/Auth';
import { ProfileSetup } from './components/ProfileSetup';
import { Dashboard } from './components/Dashboard';
import { Workout } from './components/Workout';
import { MealPlan } from './components/MealPlan';
import { Analytics } from './components/Analytics';
import { Navbar } from './components/Navbar';

export default function App() {
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [hasProfile, setHasProfile] = useState(false);

  return (
    <Router>
      <div className="min-h-screen bg-white">
        {isAuthenticated && <Navbar />}
        <Routes>
          <Route path="/" element={<Landing />} />
          <Route 
            path="/auth" 
            element={
              isAuthenticated ? <Navigate to="/dashboard" /> : 
              <Auth onAuth={() => setIsAuthenticated(true)} />
            } 
          />
          <Route 
            path="/profile-setup" 
            element={
              !isAuthenticated ? <Navigate to="/auth" /> :
              <ProfileSetup onComplete={() => setHasProfile(true)} />
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
        </Routes>
      </div>
    </Router>
  );
}
