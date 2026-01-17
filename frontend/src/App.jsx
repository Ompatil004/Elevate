import React, { useState, useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { Container } from 'react-bootstrap';
import Navigation from './components/Navigation';
import Footer from './components/Footer';
import FloatingChatbot from './components/Chatbot/FloatingChatbot';

// Import pages
import HomePage from './pages/Home/HomePage';
import WorkoutsPage from './pages/Workouts/WorkoutsPage';
import NutritionPage from './pages/Nutrition/NutritionPage';
import TrackerPage from './pages/Tracker/TrackerPage';
import ProfilePage from './pages/Profile/ProfilePage';
import LoginPage from './pages/Auth/LoginPage';
import SignupPage from './pages/Auth/SignupPage';

// Protected Route Component
const ProtectedRoute = ({ children }) => {
  const token = localStorage.getItem('token');
  return token ? children : <Navigate to="/login" />;
};

function App() {
  const [isChatbotVisible, setIsChatbotVisible] = useState(false);
  const [isAuthenticated, setIsAuthenticated] = useState(false);

  const toggleChatbot = () => {
    setIsChatbotVisible(!isChatbotVisible);
  };

  const closeChatbot = () => {
    setIsChatbotVisible(false);
  };

  // Check authentication status on component mount and when localStorage changes
  useEffect(() => {
    const checkAuth = () => {
      const token = localStorage.getItem('token');
      setIsAuthenticated(!!token);
    };

    checkAuth();

    // Listen for storage events to handle auth changes from other tabs
    window.addEventListener('storage', checkAuth);

    return () => {
      window.removeEventListener('storage', checkAuth);
    };
  }, []);

  return (
    <Router>
      <div className="d-flex flex-column min-vh-100 position-relative">
        <Navigation />
        <Container fluid className="flex-grow-1">
          <Routes>
            <Route path="/" element={<HomePage />} />
            <Route path="/login" element={<LoginPage />} />
            <Route path="/signup" element={<SignupPage />} />
            <Route path="/workouts" element={
              <ProtectedRoute>
                <WorkoutsPage />
              </ProtectedRoute>
            } />
            <Route path="/nutrition" element={
              <ProtectedRoute>
                <NutritionPage />
              </ProtectedRoute>
            } />
            <Route path="/tracker" element={
              <ProtectedRoute>
                <TrackerPage />
              </ProtectedRoute>
            } />
            <Route path="/profile" element={
              <ProtectedRoute>
                <ProfilePage />
              </ProtectedRoute>
            } />
          </Routes>
        </Container>
        <Footer />

        {/* Floating Chatbot - Only show when user is authenticated */}
        {isAuthenticated && (
          <FloatingChatbot
            isVisible={isChatbotVisible}
            onClose={closeChatbot}
            onToggleVisibility={toggleChatbot}
          />
        )}
      </div>
    </Router>
  );
}

export default App;