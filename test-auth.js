const axios = require('axios');

// Test registration and login
async function testAuth() {
  const BASE_URL = 'http://localhost:5000/api';

  console.log('Testing registration...');

  const email = `test_${Date.now()}@example.com`;
  const username = `testuser_${Date.now()}`;

  try {
    // Test registration
    const registerResponse = await axios.post(`${BASE_URL}/auth/register`, {
      username: username,
      email: email,
      password: 'password123',
      firstName: 'Test',
      lastName: 'User'
    });

    console.log('✅ Registration successful!', registerResponse.data);
    const token = registerResponse.data.token;

    // Test login with the same credentials
    console.log('\nTesting login...');
    const loginResponse = await axios.post(`${BASE_URL}/auth/login`, {
      email: email, // Use the same email as registration
      password: 'password123'
    }, {
      headers: {
        'Content-Type': 'application/json'
      }
    });

    console.log('✅ Login successful!', loginResponse.data);

    // Test accessing a protected route
    console.log('\nTesting protected route access...');
    const profileResponse = await axios.get(`${BASE_URL}/users/profile`, {
      headers: {
        'x-auth-token': token
      }
    });

    console.log('✅ Protected route access successful!', profileResponse.data);

    console.log('\n🎉 All authentication tests passed!');
  } catch (error) {
    console.error('❌ Error during authentication test:', error.response?.data || error.message);
  }
}

testAuth();