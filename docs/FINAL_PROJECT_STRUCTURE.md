# FINAL PROJECT STRUCTURE REPORT
## Elevate Fitness & Nutrition Intelligence Platform

> **Date:** November 20, 2026  
> **Status:** Current Verified Directory Structure  
> **Repository:** `Elevate-fitness`  

---

## 1. Directory Tree Overview

```
Elevate-fitness/
├── backend-node/                 # Node.js API Gateway, Auth, & Persistence Service
│   ├── config/                   # Database & runtime configuration
│   ├── middleware/               # Express middleware (auth, rate limits, error handlers)
│   ├── models/                   # Mongoose schemas (User, AuditLog, etc.)
│   ├── routes/                   # HTTP route controllers
│   ├── tests/                    # Jest automated unit and integration tests
│   ├── utils/                    # Shared Node helper utilities
│   ├── package.json              # Node.js dependencies and scripts
│   └── server.js                 # Node.js gateway entrypoint
│
├── backend-python/               # Python FastAPI Machine Learning & Algorithmic Engine
│   ├── app/                      # Application packages & domain engines
│   │   ├── engines/              # Specialized domain calculation engines
│   │   ├── nutrition_engine/     # Nutrition V6 candidate generator & portion optimizer
│   │   ├── routes/               # Modular FastAPI APIRouters
│   │   ├── utils/                # Movement mappers & biomechanics utilities
│   │   ├── db.py                 # Async Motor MongoDB connection pool
│   │   ├── feature_pipeline.py   # Machine learning feature vector transformation
│   │   ├── gemini_service.py     # Google Gemini AI assistant integration
│   │   ├── pose_tracker.py       # Biomechanical joint analysis
│   │   ├── workout_engine.py     # XGBoost & rule-based workout plan generator
│   │   └── workout_rules.py      # Exercise safety, frequency gating, and split rules
│   ├── data/                     # Food datasets, nutrition templates, and exercises
│   ├── models/                   # Serialized XGBoost models and scikit-learn encoders
│   ├── tests/                    # Pytest automated test suite (93 tests)
│   ├── pytest.ini                # Pytest configuration
│   ├── requirements.txt          # Python virtual environment dependencies
│   └── server.py                 # FastAPI service entrypoint with lifespan manager
│
├── frontend/                     # React Single-Page Application (SPA) with Vite
│   ├── public/                   # Static assets, models, and manifests
│   ├── src/                      # Source code
│   │   ├── __tests__/            # Vitest unit and integration test specs
│   │   ├── api/                  # Modular API client layer (domain-sliced)
│   │   ├── components/           # Reusable UI components & layouts
│   │   ├── context/              # React Context providers (Auth, Theme, Notification)
│   │   ├── features/             # Feature-sliced modules (Dashboard, Workout, Nutrition, Pose)
│   │   ├── hooks/                # Custom React hooks
│   │   ├── pages/                # High-level route views (Dashboard, Login, Admin, etc.)
│   │   ├── services/             # Background sync bridges and caching
│   │   ├── utils/                # Client-side utility functions and circuit breakers
│   │   ├── App.jsx               # Root application router and route guards
│   │   └── main.jsx              # Application bootstrap entrypoint
│   ├── index.html                # Vite HTML template
│   ├── package.json              # Frontend npm dependencies and scripts
│   └── vite.config.js            # Vite build configuration
│
├── AUTONOMOUS_REFACTORING_PROGRESS.md # Real-time implementation tracking ledger
├── FINAL_IMPLEMENTATION_REPORT.md     # Detailed transformation implementation report
├── FINAL_TEST_REPORT.md               # Complete test execution and verification report
├── FINAL_PROJECT_ARCHITECTURE.md      # Architectural design and flow diagrams
├── FINAL_PROJECT_STRUCTURE.md         # Complete repository structure documentation
├── REMAINING_ISSUES.md                # Theoretical edge cases and future roadmap items
├── CHANGELOG.md                       # Chronological log of changes and bug fixes
└── README.md                          # Project overview, installation, and run guide
```

---

## 2. Detailed Subsystem Breakdown

### 2.1 `frontend/src/features/` (Modular Domain Subsystems)

#### `frontend/src/features/dashboard/`
- **`ActivityChart.jsx`:** Standalone SVG spline chart with animated Bézier curves, interactive hover tooltips, and dynamic y-axis scaling for activity metrics.
- **`heroActionConfig.js`:** Encapsulates `HERO_ACTION_VARIANTS` styling configurations, dynamic daily water target math based on body weight/sleep/activity, and multi-factor trend score calculations.
- **`index.js`:** Barrel export.

#### `frontend/src/features/nutrition/`
- **`MacroStat.jsx`:** Animated radial progress cards displaying protein, carbs, fats, and calorie targets vs actual consumption.
- **`MealCard.jsx`:** Modular meal display card containing ingredient breakdowns, quantity adjustments, completion checkboxes, and swap modals.
- **`MealSwapModal.jsx`:** Searchable modal for substituting meal items while maintaining strict caloric and macro bounds.
- **`HistoryPanel.jsx`:** Slide-out drawer presenting the user's historical 7-day adherence and caloric trends.
- **`nutritionHelpers.js`:** Date manipulation utilities, IST/UTC week index calculation, and daily workout intensity estimation.
- **`nutritionServing.js`:** Standard serving size conversions and default gram weights.
- **`nutritionStyles.js`:** CSS-in-JS style configurations, color palettes, and glassmorphic surface definitions.
- **`index.js`:** Barrel export.

#### `frontend/src/features/pose-detection/`
- **`poseMath.js`:** Trigonometric calculation functions (`calculateAngle`), Exponential Moving Average (`smoothLandmarks`), and movement pattern classification (`getMovementPattern`).
- **`formSafety.js`:** Biomechanical violation checks (e.g. knee valgus collapse, spinal hyperextension, excessive elbow flare) and verbal feedback cue generation.
- **`repCounterMachine.js`:** Finite state machine managing rep states (`READY`, `ECCENTRIC`, `INFLECTION`, `CONCENTRIC`, `COMPLETED`) with hysteresis filtering to prevent jitter.
- **`poseDrawing.js`:** HTML5 Canvas drawing routines for skeletal joints, angle indicators, and visual HUD gauges.
- **`index.js`:** Feature barrel export.

#### `frontend/src/features/workout/`
- **`AnimatedImageSequence.jsx`:** Canvas-based GIF loop animation component for exercise demonstration with automatic fallback illustrations.
- **`DaySelector.jsx`:** Interactive weekly workout schedule selector displaying day badges, rest-day chips, and completion checkboxes.
- **`RestDaySwapModal.jsx`:** Dedicated modal allowing users to safely reposition rest days in their training split without breaking volume spacing.
- **`SwapHistoryModal.jsx`:** Audit drawer displaying timestamps and details of previously swapped exercises.
- **`ExerciseVariationModal.jsx`:** Modal presenting AI-recommended exercise progressions (harder variations) and regressions (easier variations).
- **`workoutConstants.js`:** Exercise metadata dictionary, status computation utilities, and day name arrays.
- **`workoutStyles.js`:** Component styles, button variants, and responsive layout definitions.
- **`index.js`:** Feature barrel export.

---

### 2.2 `frontend/src/api/` (Modular API Domain Clients)

- **`apiClient.js`:** Central Axios instance configured with `withCredentials: true`, timeout settings, CSRF token header injection, and global response error interceptors.
- **`authApi.js`:** Handles `login`, `register`, `googleAuth`, `logout`, `verifySession`, `forgotPassword`, and `resetPassword`.
- **`profileApi.js`:** Handles `getProfile`, `updateProfileSafe`, `updateMetrics`, `getAvatar`, and `uploadAvatar`.
- **`workoutApi.js`:** Handles `generateWorkoutPlan`, `getWorkoutPlan`, `logWorkoutSession`, `swapWorkoutExercise`, and `getExerciseVariations`.
- **`nutritionApi.js`:** Handles `getMealPlan`, `generateMealPlan`, `searchFoodDatabase`, `swapMealItem`, and `logMealConsumption`.
- **`adminApi.js`:** Handles `getUsers`, `suspendUser`, `unsuspendUser`, `getSystemTelemetry`, and `getAuditLogs`.
- **`chatbotApi.js`:** Handles `sendChatMessage`, `getChatHistory`, and `clearChatSession`.
- **`index.js`:** Central barrel aggregator.
- **`frontend/src/api.js`:** Backwards-compatibility bridge maintaining zero breaking changes for existing page imports.

---

### 2.3 `backend-node/` (Node.js API Gateway & Authority)

- **`server.js`:** Express application initialization, CORS configuration with credentials support, cookie parser, and route mounting.
- **`middleware/auth.js`:** Authoritative JWT authentication middleware verifying signatures and performing database status checks (`isSuspended`).
- **`middleware/rateLimiter.js`:** Sliding window rate limiting protecting authentication and generation endpoints from abuse.
- **`routes/auth.js`:** User authentication endpoints enforcing 7-day token expiration and HTTP-only cookie setting.
- **`routes/adminAuth.js`:** Admin authentication endpoints enforcing 2-hour session expiration.
- **`routes/pythonProxy.js`:** Reverse proxy forwarding machine learning requests to Python with circuit breaker protection and request ID tracking.
- **`routes/profile.js`:** Profile management with bounded activity logging (`$slice: -100`) and safe updates.
- **`models/User.js`:** Mongoose schema for user accounts, credentials, preferences, and profile statistics.

---

### 2.4 `backend-python/` (Python FastAPI Intelligence Service)

- **`server.py`:** FastAPI application entrypoint utilizing modern `@asynccontextmanager` `lifespan(app: FastAPI)` lifecycle management.
- **`app/feature_pipeline.py`:** Standardized machine learning feature extraction pipeline with pre-fitted canonical vocabularies for equipment and injuries.
- **`app/workout_engine.py`:** Multi-output XGBoost workout generation engine applying volume optimization and biomechanical safety bounds.
- **`app/workout_rules.py`:** Rule-based expert system governing frequency gating, split assignment, and injury exclusions.
- **`app/nutrition_engine/candidate_generator.py`:** Combinatorial meal candidate generator enforcing a 0.00% fallback rate.
- **`app/nutrition_engine/engine.py`:** Full nutrition engine coordinator optimizing weekly micronutrient and macronutrient adherence.
- **`app/pose_tracker.py`:** Joint landmark processing and angle computation for MediaPipe pose estimation.
- **`app/gemini_service.py`:** Resilient Google Gemini conversational assistant service with circuit breaker offline fallbacks.
- **`app/db.py`:** Motor asynchronous MongoDB connection manager.
