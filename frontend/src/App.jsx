import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { useState, useEffect } from 'react';
import { NotificationProvider } from './components/NotificationProvider';
import { validateToken } from './api';
import Login from './pages/Login';
import Register from './pages/Register';
import Dashboard from './pages/Dashboard';
import ProfileSetup from './pages/ProfileSetup';
import Workout from './pages/Workout';
import Nutrition from './pages/Nutrition';
import Chatbot from './pages/Chatbot';
import './App.css';

export default function App() {
    const [isAuthenticated, setIsAuthenticated] = useState(false);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        const token = localStorage.getItem('token');
        
        // If no token, not authenticated
        if (!token) {
            setIsAuthenticated(false);
            setLoading(false);
            return;
        }
        
        // Validate token with server
        const verifyToken = async () => {
            try {
                const response = await validateToken();
                if (response.data.valid) {
                    console.log('✅ Token validated with server');
                    setIsAuthenticated(true);
                } else {
                    console.error('❌ Token invalid from server');
                    localStorage.removeItem('token');
                    setIsAuthenticated(false);
                }
            } catch (error) {
                console.error('Token validation error:', error);
                localStorage.removeItem('token');
                setIsAuthenticated(false);
            } finally {
                setLoading(false);
            }
        };

        verifyToken();
    }, []);

    // Logout function
    const handleLogout = () => {
        localStorage.clear();
        setIsAuthenticated(false);
    };

    if (loading) {
        return <div>Loading...</div>;
    }

    return (
        <NotificationProvider>
            <BrowserRouter>
                <Routes>
                    <Route 
                        path="/login" 
                        element={!isAuthenticated ? <Login setIsAuthenticated={setIsAuthenticated} /> : <Navigate to="/dashboard" />} 
                    />
                    <Route 
                        path="/register" 
                        element={!isAuthenticated ? <Register /> : <Navigate to="/dashboard" />} 
                    />
                    <Route 
                        path="/dashboard" 
                        element={isAuthenticated ? <Dashboard onLogout={handleLogout} /> : <Navigate to="/login" />} 
                    />
                    <Route 
                        path="/profile-setup" 
                        element={isAuthenticated ? <ProfileSetup /> : <Navigate to="/login" />} 
                    />
                    <Route 
                        path="/profile" 
                        element={isAuthenticated ? <ProfileSetup /> : <Navigate to="/login" />} 
                    />
                    <Route 
                        path="/workout" 
                        element={isAuthenticated ? <Workout /> : <Navigate to="/login" />} 
                    />
                    <Route 
                        path="/nutrition" 
                        element={isAuthenticated ? <Nutrition /> : <Navigate to="/login" />} 
                    />
                    <Route 
                        path="/chatbot" 
                        element={isAuthenticated ? <Chatbot /> : <Navigate to="/login" />} 
                    />
                    <Route 
                        path="/" 
                        element={<Navigate to={isAuthenticated ? "/dashboard" : "/login"} />} 
                    />
                    <Route 
                        path="*" 
                        element={<Navigate to="/login" />} 
                    />
                </Routes>
            </BrowserRouter>
        </NotificationProvider>
    );
}