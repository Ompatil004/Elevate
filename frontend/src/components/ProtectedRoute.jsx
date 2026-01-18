import React from 'react';
import { Navigate } from 'react-router-dom';

const ProtectedRoute = ({ children }) => {
  // Check if user is authenticated (using localStorage as example)
  const isAuthenticated = localStorage.getItem('token') !== null;

  return isAuthenticated ? children : <Navigate to="/" replace />;
};

export default ProtectedRoute;