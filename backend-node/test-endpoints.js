const axios = require('axios');

// Test script to verify the new endpoints work
async function testEndpoints() {
  console.log('Testing new endpoints...\n');
  
  // First, register a test user
  try {
    console.log('1. Registering test user...');
    const registerResponse = await axios.post('http://localhost:5000/api/auth/register', {
      name: 'Test User',
      email: 'test@example.com',
      password: 'password123'
    });
    
    console.log('✓ User registered:', registerResponse.data.message);
    const token = registerResponse.data.token;
    console.log('✓ Token received');
    
    // Test the /api/users/save endpoint
    console.log('\n2. Testing /api/users/save endpoint...');
    const profileResponse = await axios.post('http://localhost:5000/api/users/save', {
      age: 30,
      weight: 70,
      height: 175,
      goal: 'Muscle Gain',
      experience: 'Intermediate'
    }, {
      headers: {
        'x-auth-token': token
      }
    });
    
    console.log('✓ Profile saved:', profileResponse.data.message);
    
    // Test the /api/users/workout/save endpoint
    console.log('\n3. Testing /api/users/workout/save endpoint...');
    const workoutResponse = await axios.post('http://localhost:5000/api/users/workout/save', {
      workoutName: 'Chest Day',
      exercises: [
        { name: 'Push-ups', reps: 15, sets: 3 },
        { name: 'Bench Press', reps: 10, sets: 4 }
      ],
      duration: 45
    }, {
      headers: {
        'x-auth-token': token
      }
    });
    
    console.log('✓ Workout saved:', workoutResponse.data.message);
    
    // Test the /api/users/meals/save endpoint
    console.log('\n4. Testing /api/users/meals/save endpoint...');
    const mealResponse = await axios.post('http://localhost:5000/api/users/meals/save', {
      mealType: 'Breakfast',
      foods: [
        { name: 'Oatmeal', quantity: '1 cup' },
        { name: 'Banana', quantity: '1 medium' }
      ],
      calories: 350
    }, {
      headers: {
        'x-auth-token': token
      }
    });
    
    console.log('✓ Meal saved:', mealResponse.data.message);
    
    console.log('\n🎉 All endpoints are working correctly!');
  } catch (error) {
    console.error('❌ Error during testing:', error.response?.data || error.message);
  }
}

testEndpoints();