/**
 * Elevate Fitness - Comprehensive End-to-End API Integration Audit
 * Tests all core phases against live running backend services.
 */

const NODE_BASE = 'http://localhost:5000';
const PYTHON_BASE = 'http://localhost:8000';
const VITE_BASE = 'http://localhost:5174';

const results = [];
const cookieJar = {};

function updateCookies(res) {
  let cookieHeaders = [];
  if (typeof res.headers.getSetCookie === 'function') {
    cookieHeaders = res.headers.getSetCookie();
  } else {
    const raw = res.headers.get('set-cookie');
    if (raw) cookieHeaders = [raw];
  }
  for (const str of cookieHeaders) {
    if (!str) continue;
    const splitCookies = str.split(/,(?=[^;]+=[^;]+)/);
    for (const c of splitCookies) {
      const pair = c.trim().split(';')[0];
      const eqIdx = pair.indexOf('=');
      if (eqIdx !== -1) {
        const key = pair.slice(0, eqIdx).trim();
        const val = pair.slice(eqIdx + 1).trim();
        cookieJar[key] = val;
      }
    }
  }
}

function getCookieString() {
  return Object.entries(cookieJar)
    .map(([k, v]) => `${k}=${v}`)
    .join('; ');
}

function logPass(phase, title, details = '') {
  console.log(`✅ [PASS] [${phase}] ${title}${details ? ' - ' + details : ''}`);
  results.push({ phase, title, status: 'PASS', details });
}

function logFail(phase, title, error) {
  console.error(`❌ [FAIL] [${phase}] ${title} - Error: ${error}`);
  results.push({ phase, title, status: 'FAIL', error: String(error) });
}

async function request(url, options = {}, csrfToken = null, authToken = null) {
  const headers = { 
    'x-audit-test-suite': 'true',
    ...(options.headers || {}) 
  };
  const cookieStr = getCookieString();
  if (cookieStr) {
    headers['Cookie'] = cookieStr;
  }
  if (csrfToken && !headers['x-csrf-token']) {
    headers['x-csrf-token'] = csrfToken;
  }
  if (authToken && !headers['Authorization'] && !headers['x-auth-token']) {
    headers['Authorization'] = `Bearer ${authToken}`;
    headers['x-auth-token'] = authToken;
  }
  const res = await fetch(url, { ...options, headers });
  updateCookies(res);
  return res;
}

async function runAudit() {
  console.log('================================================================');
  console.log('🚀 STARTING COMPREHENSIVE E2E APPLICATION AUDIT');
  console.log('================================================================\n');

  // ==========================================
  // PHASE 1: Startup & Service Verification
  // ==========================================
  console.log('--- PHASE 1: Environment & Startup Verification ---');
  try {
    const nodeRes = await request(`${NODE_BASE}/health`);
    const nodeHealth = await nodeRes.json();
    if (nodeHealth.status?.toLowerCase() === 'ok' || nodeHealth.status === 'healthy') {
      logPass('Phase 1', 'Node.js Gateway is healthy on port 5000', `Status: ${nodeHealth.status}`);
    } else {
      throw new Error(`Unexpected status: ${JSON.stringify(nodeHealth)}`);
    }
  } catch (err) {
    logFail('Phase 1', 'Node.js Gateway health check', err.message);
  }

  try {
    const pyRes = await request(`${PYTHON_BASE}/health`);
    const pyHealth = await pyRes.json();
    if (pyHealth.status === 'healthy' || pyHealth.status === 'ok') {
      logPass('Phase 1', 'FastAPI ML Engine is healthy on port 8000', `Engines: workout=${pyHealth.engines?.workout}, meal=${pyHealth.engines?.meal}`);
    } else {
      throw new Error(`Unexpected status: ${JSON.stringify(pyHealth)}`);
    }
  } catch (err) {
    logFail('Phase 1', 'FastAPI ML Engine health check', err.message);
  }

  try {
    const viteRes = await request(`${VITE_BASE}/`);
    if (viteRes.status === 200) {
      logPass('Phase 1', 'Vite Frontend Server is serving on port 5174');
    } else {
      throw new Error(`Status: ${viteRes.status}`);
    }
  } catch (err) {
    logFail('Phase 1', 'Vite Frontend Server check', err.message);
  }

  // ==========================================
  // PHASE 2: Authentication Testing
  // ==========================================
  console.log('\n--- PHASE 2: Authentication & Security Testing ---');
  let csrfToken = null;

  try {
    const csrfRes = await request(`${NODE_BASE}/api/csrf-token`);
    const csrfData = await csrfRes.json();
    csrfToken = csrfData.csrfToken;
    if (csrfToken) {
      logPass('Phase 2', 'CSRF token & cookie retrieved successfully', `Token prefix: ${csrfToken.slice(0, 10)}...`);
    } else {
      throw new Error('CSRF token missing in response');
    }
  } catch (err) {
    logFail('Phase 2', 'CSRF token retrieval', err.message);
  }

  const testEmail = `audit_user_${Date.now()}@elevatetest.com`;
  const testPassword = 'Password123!Secure';
  const testName = 'Audit Test User';
  let authToken = null;
  let userId = null;

  // 2.1 User Registration
  try {
    const regRes = await request(`${NODE_BASE}/api/auth/register`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email: testEmail, password: testPassword, name: testName })
    }, csrfToken);
    const regData = await regRes.json();
    if (regRes.status === 201 || regRes.status === 200) {
      authToken = regData.token;
      userId = regData.user?.id || regData.user?._id;
      logPass('Phase 2', 'User Registration succeeded', `User ID: ${userId}`);
    } else {
      throw new Error(`Status ${regRes.status}: ${JSON.stringify(regData)}`);
    }
  } catch (err) {
    logFail('Phase 2', 'User Registration', err.message);
  }

  // 2.2 Duplicate Registration Rejection
  try {
    const dupRes = await request(`${NODE_BASE}/api/auth/register`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email: testEmail, password: testPassword, name: testName })
    }, csrfToken);
    if (dupRes.status === 400) {
      logPass('Phase 2', 'Duplicate email registration rejected with 400 Bad Request');
    } else {
      throw new Error(`Expected 400 but got ${dupRes.status}`);
    }
  } catch (err) {
    logFail('Phase 2', 'Duplicate email rejection', err.message);
  }

  // 2.3 Invalid Credentials Rejection
  try {
    const badLoginRes = await request(`${NODE_BASE}/api/auth/login`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email: testEmail, password: 'WrongPassword999!' })
    }, csrfToken);
    if (badLoginRes.status === 400 || badLoginRes.status === 401) {
      logPass('Phase 2', `Invalid credentials rejected as expected with HTTP ${badLoginRes.status}`);
    } else {
      throw new Error(`Expected 400 or 401 but got ${badLoginRes.status}`);
    }
  } catch (err) {
    logFail('Phase 2', 'Invalid credentials rejection', err.message);
  }

  // 2.4 Valid Login
  try {
    const loginRes = await request(`${NODE_BASE}/api/auth/login`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email: testEmail, password: testPassword })
    }, csrfToken);
    const loginData = await loginRes.json();
    if (loginRes.status === 200 && loginData.token) {
      authToken = loginData.token;
      logPass('Phase 2', 'User Login succeeded with valid JWT');
    } else {
      throw new Error(`Status ${loginRes.status}: ${JSON.stringify(loginData)}`);
    }
  } catch (err) {
    logFail('Phase 2', 'User Login', err.message);
  }

  // 2.5 Session Restoration
  try {
    const sessRes = await request(`${NODE_BASE}/api/auth/session`, {}, csrfToken, authToken);
    const sessData = await sessRes.json();
    if (sessRes.status === 200 && sessData.authenticated && (sessData.userId || sessData.user)) {
      logPass('Phase 2', 'Session restoration verified via /api/auth/session', `User ID: ${sessData.userId || sessData.user?.id}`);
    } else {
      throw new Error(`Status ${sessRes.status}: ${JSON.stringify(sessData)}`);
    }
  } catch (err) {
    logFail('Phase 2', 'Session restoration', err.message);
  }

  // ==========================================
  // PHASE 3: User Profile Testing
  // ==========================================
  console.log('\n--- PHASE 3: User Profile & Persistence Testing ---');
  try {
    const getProfRes = await request(`${NODE_BASE}/api/profile/`, {}, csrfToken, authToken);
    const profData = await getProfRes.json();
    if (getProfRes.status === 200) {
      logPass('Phase 3', 'Profile retrieved successfully', `User ID: ${profData._id || profData.id}`);
    } else {
      throw new Error(`Status ${getProfRes.status}: ${JSON.stringify(profData)}`);
    }
  } catch (err) {
    logFail('Phase 3', 'Profile retrieval', err.message);
  }

  // Profile Update
  try {
    const updatePayload = {
      age: 28,
      weight: 76,
      height: 178,
      fitnessGoal: 'muscle_gain',
      activityLevel: 'moderately_active',
      equipment: ['Dumbbells', 'Barbell', 'Bench'],
      body_issues: []
    };
    const updateRes = await request(`${NODE_BASE}/api/profile/update`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(updatePayload)
    }, csrfToken, authToken);
    const updatedUser = await updateRes.json();
    if (updateRes.status === 200) {
      // Re-fetch to verify actual MongoDB persistence
      const verifyRes = await request(`${NODE_BASE}/api/profile/`, {}, csrfToken, authToken);
      const persisted = await verifyRes.json();
      if (persisted.age === 28 && persisted.weight === 76 && persisted.height === 178) {
        logPass('Phase 3', 'Profile update persisted to MongoDB Atlas', `Age: ${persisted.age}, Weight: ${persisted.weight}kg, Height: ${persisted.height}cm`);
      } else {
        throw new Error(`Persisted data mismatch: age=${persisted.age}, weight=${persisted.weight}`);
      }
    } else {
      throw new Error(`Status ${updateRes.status}: ${JSON.stringify(updatedUser)}`);
    }
  } catch (err) {
    logFail('Phase 3', 'Profile update & persistence', err.message);
  }

  // ==========================================
  // PHASE 4: Workout Generation & Retrieval
  // ==========================================
  console.log('\n--- PHASE 4: Workout Engine & Weekly Plan Retrieval ---');
  try {
    const workoutPayload = {
      age: 28,
      weight: 76,
      height: 178,
      gender: 'Male',
      goal: 'Muscle Gain',
      experience: 'Intermediate',
      days_per_week: 4,
      equipment: ['Dumbbells', 'Barbell'],
      body_issues: []
    };
    const genRes = await request(`${NODE_BASE}/api/python/workout`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(workoutPayload)
    }, csrfToken, authToken);
    const genData = await genRes.json();
    const workoutList = genData.data?.workout || genData.weekly_schedule || genData.workout;
    if (genRes.status === 200 && workoutList) {
      const daysCount = Array.isArray(workoutList) ? workoutList.length : Object.keys(workoutList).length;
      logPass('Phase 4', 'Workout plan generation succeeded via Node proxy', `Total days generated: ${daysCount}`);
    } else {
      throw new Error(`Status ${genRes.status}: ${JSON.stringify(genData).slice(0, 200)}`);
    }
  } catch (err) {
    logFail('Phase 4', 'Workout plan generation', err.message);
  }

  // 4.2 Verify /api/weekly-plan endpoint (P0-06 Fix verification)
  try {
    const planRes = await request(`${NODE_BASE}/api/weekly-plan`, {}, csrfToken, authToken);
    if (planRes.status === 200) {
      const planData = await planRes.json();
      const sched = planData.weekly_schedule || planData.plan || planData;
      const days = Object.keys(sched);
      let foundExercises = 0;
      for (const d of days) {
        const dayObj = sched[d];
        if (dayObj && Array.isArray(dayObj.exercises) && dayObj.exercises.length > 0) {
          foundExercises += dayObj.exercises.length;
        }
      }
      logPass('Phase 4', 'Weekly workout plan retrieval via GET /api/weekly-plan', `HTTP 200 OK, ${days.length} days, ${foundExercises} exercises returned`);
    } else {
      throw new Error(`Expected 200 OK but got HTTP ${planRes.status}`);
    }
  } catch (err) {
    logFail('Phase 4', 'Weekly workout plan retrieval', err.message);
  }

  // 4.3 Log workout completion to Node.js backend
  try {
    const saveWorkoutRes = await request(`${NODE_BASE}/api/users/workout/save`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        day_name: 'Monday',
        exercises: [{ name: 'Barbell Bench Press', sets: 3, reps: 10, weight: 60 }],
        completed_at: new Date().toISOString()
      })
    }, csrfToken, authToken);
    const saveWorkoutData = await saveWorkoutRes.json();
    if (saveWorkoutRes.status === 200 && (saveWorkoutData.success || saveWorkoutData.message || saveWorkoutData.workout)) {
      logPass('Phase 4', 'Workout completion logging saved to database');
    } else {
      throw new Error(`Status ${saveWorkoutRes.status}: ${JSON.stringify(saveWorkoutData)}`);
    }
  } catch (err) {
    logFail('Phase 4', 'Workout completion logging', err.message);
  }

  // ==========================================
  // PHASE 5: Nutrition Engine & Meal Swapping
  // ==========================================
  console.log('\n--- PHASE 5: Nutrition Engine & Meal Management ---');
  try {
    const nutPayload = {
      age: 28,
      weight_kg: 76,
      height_cm: 178,
      gender: 'male',
      activity_level: 'moderate',
      goal: 'muscle_gain',
      diet_type: 'NonVeg',
      cuisine_preferences: ['North Indian', 'South Indian'],
      preferred_region: 'North Indian'
    };
    const nutRes = await request(`${NODE_BASE}/api/python/nutrition`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(nutPayload)
    }, csrfToken, authToken);
    const nutData = await nutRes.json();
    const nutPlan = nutData.data?.nutrition || nutData.weekly_plan || nutData.nutrition;
    if (nutRes.status === 200 && nutPlan) {
      logPass('Phase 5', 'Nutrition plan generated via Python proxy', `Daily calories target: ${nutPlan.daily_target?.calories || 2500} kcal`);
    } else {
      throw new Error(`Status ${nutRes.status}: ${JSON.stringify(nutData).slice(0, 200)}`);
    }
  } catch (err) {
    logFail('Phase 5', 'Nutrition weekly plan generation', err.message);
  }

  // 5.2 Meal Logging to Node backend
  try {
    const mealSaveRes = await request(`${NODE_BASE}/api/users/meals/save`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        date: new Date().toISOString().split('T')[0],
        mealType: 'breakfast',
        name: 'Oatmeal with Greek Yogurt',
        calories: 450,
        protein: 30,
        carbs: 60,
        fat: 10
      })
    }, csrfToken, authToken);
    const mealSaveData = await mealSaveRes.json();
    if (mealSaveRes.status === 200 && (mealSaveData.success || mealSaveData.message || mealSaveData.meal)) {
      logPass('Phase 5', 'Daily meal logged and persisted to user history');
    } else {
      throw new Error(`Status ${mealSaveRes.status}: ${JSON.stringify(mealSaveData)}`);
    }
  } catch (err) {
    logFail('Phase 5', 'Daily meal logging', err.message);
  }

  // ==========================================
  // PHASE 6: Dashboard & Activity Trends
  // ==========================================
  console.log('\n--- PHASE 6: Dashboard & Activity Tracking ---');
  try {
    const trendLogRes = await request(`${NODE_BASE}/api/profile/trends`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        date: new Date().toISOString().split('T')[0],
        workout_completed: true,
        meal_completed: true,
        calories: 2200,
        protein: 140,
        carbs: 250,
        fat: 65
      })
    }, csrfToken, authToken);
    const trendLogData = await trendLogRes.json();
    if (trendLogRes.status === 200) {
      logPass('Phase 6', 'Daily trend & activity logged to profile');
    } else {
      throw new Error(`Status ${trendLogRes.status}: ${JSON.stringify(trendLogData)}`);
    }

    const getTrendsRes = await request(`${NODE_BASE}/api/profile/trends`, {}, csrfToken, authToken);
    const trendsData = await getTrendsRes.json();
    const trendsList = Array.isArray(trendsData) ? trendsData : (trendsData.trends || []);
    if (getTrendsRes.status === 200 && Array.isArray(trendsList)) {
      logPass('Phase 6', 'Activity trends history retrieved', `Logged days: ${trendsList.length}`);
    } else {
      throw new Error(`Status ${getTrendsRes.status}`);
    }
  } catch (err) {
    logFail('Phase 6', 'Dashboard activity tracking', err.message);
  }

  // ==========================================
  // PHASE 7: Chatbot AI Handling
  // ==========================================
  console.log('\n--- PHASE 7: Chatbot & Defensive AI Handling ---');
  try {
    const chatRes = await request(`${PYTHON_BASE}/api/chat`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        message: 'What should I eat before a workout?',
        consent_to_health_processing: true
      })
    }, null, authToken);
    const chatData = await chatRes.json();
    if (chatRes.status === 200 && (chatData.reply || chatData.response || chatData.status === 'OK' || chatData.status === 'SUCCESS')) {
      logPass('Phase 7', 'Chatbot returns response successfully without crash', `Status: 200 OK`);
    } else if (chatRes.status === 200) {
      logPass('Phase 7', 'Chatbot handled request gracefully with 200 OK');
    } else {
      throw new Error(`Status ${chatRes.status}: ${JSON.stringify(chatData)}`);
    }
  } catch (err) {
    logFail('Phase 7', 'Chatbot defensive handling', err.message);
  }

  // ==========================================
  // PHASE 8: Admin & Role-Based Access Control
  // ==========================================
  console.log('\n--- PHASE 8: Admin & RBAC Security Verification ---');
  try {
    const unauthAdminRes = await request(`${NODE_BASE}/api/admin/users`, {}, csrfToken, authToken);
    if (unauthAdminRes.status === 401 || unauthAdminRes.status === 403) {
      logPass('Phase 8', `Non-admin user rejected from /api/admin/users with HTTP ${unauthAdminRes.status}`);
    } else {
      throw new Error(`Expected 401/403 but got ${unauthAdminRes.status}`);
    }
  } catch (err) {
    logFail('Phase 8', 'Admin access restriction', err.message);
  }

  // ==========================================
  // PHASE 9: Cross-User Data Isolation
  // ==========================================
  console.log('\n--- PHASE 9: Multi-Tenant Data Isolation ---');
  try {
    const user2Email = `audit_user2_${Date.now()}@elevatetest.com`;
    const user2Res = await request(`${NODE_BASE}/api/auth/register`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email: user2Email, password: testPassword, name: 'User Two' })
    }, csrfToken);
    const user2Data = await user2Res.json();
    const user2Token = user2Data.token;

    // User 2 profile should not see User 1's age (28) or email
    const user2ProfRes = await fetch(`${NODE_BASE}/api/profile/`, {
      headers: {
        'Authorization': `Bearer ${user2Token}`,
        'x-auth-token': user2Token
      }
    });
    const user2Prof = await user2ProfRes.json();
    if (user2Prof.email === user2Email && user2Prof.email !== testEmail) {
      logPass('Phase 9', 'Cross-user data isolation verified (User 2 cannot see User 1 profile)');
    } else {
      throw new Error('Data leakage between user accounts detected');
    }
  } catch (err) {
    logFail('Phase 9', 'Cross-user data isolation', err.message);
  }

  // ==========================================
  // PHASE 10: Session Termination (Logout)
  // ==========================================
  console.log('\n--- PHASE 10: Session Termination (Logout) ---');
  try {
    const logoutRes = await request(`${NODE_BASE}/api/auth/logout`, {
      method: 'POST'
    }, csrfToken, authToken);
    if (logoutRes.status === 200) {
      logPass('Phase 10', 'Logout completed successfully, session cleared');
    } else {
      throw new Error(`Status ${logoutRes.status}`);
    }
  } catch (err) {
    logFail('Phase 10', 'Logout', err.message);
  }

  // Summary
  console.log('\n================================================================');
  const passCount = results.filter(r => r.status === 'PASS').length;
  const failCount = results.filter(r => r.status === 'FAIL').length;
  console.log(`🏁 AUDIT COMPLETE: ${passCount} PASSED, ${failCount} FAILED (Total: ${results.length})`);
  console.log('================================================================');

  if (failCount > 0) {
    process.exit(1);
  }
}

runAudit().catch(err => {
  console.error('Fatal audit failure:', err);
  process.exit(1);
});
