import axios from 'axios';

// API service for profile updates with plan regeneration
const API_BASE_URL = 'http://localhost:8000';

/**
 * Update user profile and regenerate workout/meal plans if needed
 */
export const updateProfileAndRegeneratePlans = async (profileData) => {
  try {
    console.log('🔄 Updating profile and regenerating plans with data:', profileData);
    
    const response = await axios.put(`${API_BASE_URL}/profile/update`, profileData, {
      headers: {
        'Content-Type': 'application/json',
      },
    });
    
    console.log('✅ Profile update response:', response.data);
    return response.data;
  } catch (error) {
    console.error('❌ Profile update error:', error);
    
    // Check if it's a 404 error (endpoint doesn't exist)
    if (error.response?.status === 404) {
      console.error('❌ Endpoint not found. Available endpoints:');
      
      // Try to get available endpoints
      try {
        const endpoints = await axios.get(`${API_BASE_URL}/docs`);
        console.log('Available endpoints:', endpoints.data);
      } catch (docsError) {
        console.error('Could not fetch API docs:', docsError.message);
      }
    }
    
    throw error;
  }
};

/**
 * Alternative endpoint for profile update with regeneration
 * This matches the actual backend endpoint
 */
export const updateProfileWithRegeneration = async (profileData) => {
  try {
    console.log('🔄 Updating profile with regeneration:', profileData);

    const response = await axios.put(`${API_BASE_URL}/profile/update-with-regeneration`, profileData, {
      headers: {
        'Content-Type': 'application/json',
      },
    });

    console.log('✅ Profile update with regeneration response:', response.data);
    return response.data;
  } catch (error) {
    console.error('❌ Profile update with regeneration error:', error);
    throw error;
  }
};

/**
 * Get available profile endpoints from backend
 */
export const getProfileEndpoints = async () => {
  try {
    const response = await axios.get(`${API_BASE_URL}/openapi.json`);
    return response.data;
  } catch (error) {
    console.error('❌ Could not fetch API endpoints:', error);
    throw error;
  }
};