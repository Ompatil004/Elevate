# ELEVATE PLATFORM: PRIORITY-BASED ENGINEERING IMPROVEMENT ROADMAP

> **Target State:** Hardened, Scalable, Production-Ready Microservice Fitness & Nutrition Architecture  
> **Roadmap Structure:** Categorized into P0 (Critical Immediate), P1 (High Priority Pre-Production), P2 (Medium Priority Reliability), and P3 (Low Priority Enhancements).  
> **Audience:** Core Engineering Team, DevOps Leads, and Technical Stakeholders.

---

## Roadmap Overview & Milestone Summary

```mermaid
timeline
    title Elevate Engineering Roadmap & Target Milestones
    section P0 : Immediate Fixes (Week 1)
        Token Expiration & Security Clamps : Enforce 7d/2h JWT exp & DB suspension check
        Restore CI Quality Gates : Clean 8 ESLint errors & adjust health test threshold
    section P1 : Pre-Production (Weeks 2-3)
        Resolve Dual-DB Split Brain : Route all Mongo writes exclusively through Node
        Prevent BSON Document Overflow : Cap user.activities with $slice: 100
        Dynamic Timezone Resolution : Replace hardcoded IST with client offset
        Clean Redundant Routes : Deprecate routes/users.js in favor of profile.js
    section P2 : Code Quality & Maintainability (Weeks 4-6)
        Component Decomposition : Decompose Dashboard.jsx & Workout.jsx monoliths
        Python Server Modularization : Migrate server.py routes into app/routes/
        Update Google Generative AI SDK : Migrate from google-generativeai to google-genai
        Sanitize ML Feature Pipeline : Standardize LabelEncoder tokens to fix 1,500+ warnings
    section P3 : Strategic Enhancements (Weeks 7+)
        Bi-directional CV Keypoint Tracking : Support left & right limb tracking in Python
        Async Worker Queue for Heavy ML : Offload 5-second meal optimizations to Celery/BullMQ
        Comprehensive E2E Cypress/Playwright : Add headless browser UI smoke tests
```

---

## Phase P0: Critical Fixes (Must Fix Immediately)

### TASK-P0-01: Enforce JWT Expiration & Cookie Lifetime
- **Task Description:** Add explicit expiration periods to all JWT token generation calls (`7d` for standard users, `2h` for admins) and reduce auth cookie `maxAge` from 100 years to match token lifetimes.
- **Related Files:**
  - `backend-node/routes/auth.js`
  - `backend-node/routes/adminAuth.js`
- **Why It Matters:** Without expiration, leaked or intercepted tokens grant perpetual access to user and admin accounts, violating OWASP Session Management standards (`BUG-SEC-01`, `BUG-SEC-02`).
- **Expected Outcome:** Expired tokens are rejected with 401 Unauthorized; stolen tokens have a limited window of exposure.
- **Estimated Complexity:** Low (0.5 day)

---

### TASK-P0-02: Fix Account Suspension Enforcement in Auth Middleware
- **Task Description:** In `backend-node/middleware/auth.js`, query MongoDB (`User.findById(req.user.id).select('isSuspended').lean()`) or query a Redis suspension cache to verify that the account has not been banned or suspended, rather than blindly trusting the static boolean claim in the JWT payload.
- **Related Files:**
  - `backend-node/middleware/auth.js`
  - `backend-node/routes/adminUsers.js`
- **Why It Matters:** Currently, suspending a user does not prevent them from continuing to use the platform (`BUG-SEC-03`).
- **Expected Outcome:** Any suspended user is blocked immediately with 403 Forbidden across all protected endpoints.
- **Estimated Complexity:** Low (0.5 day)

---

### TASK-P0-03: Fix 8 ESLint Errors to Green the CI/CD Pipeline
- **Task Description:** Remove unused variable declarations and imports in `PoseDetector.jsx`, `Dashboard.jsx`, and `Workout.jsx` to satisfy `eslint .` without errors.
- **Related Files:**
  - `frontend/src/components/PoseDetector.jsx`
  - `frontend/src/pages/Dashboard.jsx`
  - `frontend/src/pages/Workout.jsx`
  - `.github/workflows/quality-gates.yml`
- **Why It Matters:** The automated GitHub Actions CI pipeline fails on every pull request due to these 8 errors (`BUG-CI-01`).
- **Expected Outcome:** `npm run lint` exits cleanly with code 0; CI quality gate passes.
- **Estimated Complexity:** Low (0.25 day)

---

### TASK-P0-04: Recalibrate Candidate Generation Fallback Gate
- **Task Description:** In `backend-python/app/nutrition_engine/candidate_generator.py`, expand candidate query criteria for restrictive diets (vegan, lactose intolerant, PCOS) and re-tune `THRESHOLDS['fallback_usage_max']` in `backend-python/tests/test_candidate_health.py` to reflect actual verified generation distributions.
- **Related Files:**
  - `backend-python/app/nutrition_engine/candidate_generator.py`
  - `backend-python/tests/test_candidate_health.py`
  - `backend-python/logs/candidate_generation_metrics.jsonl`
- **Why It Matters:** `pytest tests/` fails in CI because fallback rate (9–12%) exceeds the 5% assertion (`BUG-TST-01`).
- **Expected Outcome:** `pytest tests/` passes 100% cleanly in automated CI/CD.
- **Estimated Complexity:** Medium (1 day)

---

## Phase P1: High Priority (Fix Before Production Release)

### TASK-P1-01: Reconcile Dual-Database Write Architecture (Single Source of Truth)
- **Task Description:** Discontinue Python Motor write access to the MongoDB `users` collection. Re-architect the Python FastAPI service as a purely stateless mathematical calculation engine:
  1. Python receives user biometric parameters and returns generated workout/meal JSON.
  2. Node.js backend receives the calculated JSON from Python and persists it to MongoDB through Mongoose schemas.
  3. Remove `/profile/update-with-plans`, `/profile/update-safe`, and direct DB writes from `server.py`.
- **Related Files:**
  - `backend-python/server.py`
  - `backend-python/app/db.py`
  - `backend-node/routes/pythonProxy.js`
  - `backend-node/routes/profile.js`
- **Why It Matters:** Eliminates concurrent write race conditions, schema drift, and bypassed Mongoose validation hooks (`BUG-ARCH-01`).
- **Expected Outcome:** Node.js is the sole authority for MongoDB data persistence; Python is a stateless, horizontally scalable AI computation service.
- **Estimated Complexity:** High (3 days)

---

### TASK-P1-02: Prevent MongoDB Document Size Overflow via Bounded Activity Slicing
- **Task Description:** In `backend-node/routes/profile.js`, update `/activities/log` and `/activities/sync` to use atomic `$push` with `$slice: 100` and `$position: 0` instead of unbounded `push()`.
- **Related Files:**
  - `backend-node/routes/profile.js`
- **Why It Matters:** Prevents active user documents from exceeding MongoDB's 16MB BSON limit and crashing with fatal `BSONObjectTooLarge` errors (`BUG-DAT-01`).
- **Expected Outcome:** Activity arrays stay bounded at 100 items, keeping document size under 50KB.
- **Estimated Complexity:** Low (0.5 day)

---

### TASK-P1-03: Dynamic Client Timezone Normalization
- **Task Description:** In `backend-node/utils/mealUtils.js`, replace the hardcoded `+330` (IST) offset in `toDateKey()` with dynamic client timezone handling via an incoming `x-timezone` header or ISO client date timestamp.
- **Related Files:**
  - `backend-node/utils/mealUtils.js`
  - `frontend/src/api.js`
- **Why It Matters:** Prevents date shifting and broken streaks for users outside India Standard Time (`BUG-DAT-02`).
- **Expected Outcome:** Daily meal and workout logs are attributed to the user's actual local calendar day.
- **Estimated Complexity:** Medium (1 day)

---

### TASK-P1-04: Deprecate `routes/users.js` & Consolidate Workout/Meal History Handlers
- **Task Description:** Consolidate redundant endpoints in `backend-node/routes/users.js` (`/save`, `/workout/save`, `/meals/save`) into `routes/profile.js`. Enforce a consistent newest-first array ordering (`$position: 0`) and unified slice limit (100 items) across all workout history writes.
- **Related Files:**
  - `backend-node/routes/users.js`
  - `backend-node/routes/profile.js`
  - `frontend/src/api.js`
- **Why It Matters:** Eliminates conflicting array slice directions (`BUG-DAT-03`) and removes duplicate, divergent code.
- **Expected Outcome:** Single canonical route for workout and meal persistence.
- **Estimated Complexity:** Medium (1.5 days)

---

### TASK-P1-05: Clean Dead API Exports in Frontend
- **Task Description:** Remove or correct the broken `updateProfileAndRegenerateWorkouts` export in `frontend/src/api.js` that targets non-existent `PUT /profile/update` (`BUG-API-01`).
- **Related Files:**
  - `frontend/src/api.js`
  - `frontend/src/services/profileApi.js`
- **Why It Matters:** Eliminates broken endpoints that produce 404 errors if invoked.
- **Expected Outcome:** Clean, type-safe API contract matching active backend routes.
- **Estimated Complexity:** Low (0.25 day)

---

## Phase P2: Medium Priority (Improve Reliability & Maintainability)

### TASK-P2-01: Decompose Mega-Monolithic React Components
- **Task Description:** Split 3,500+ line components (`Dashboard.jsx`, `Workout.jsx`, `Nutrition.jsx`) into focused, modular sub-components:
  - `Dashboard.jsx`: Extract `<HabitTracker />`, `<StreakCard />`, `<TrendChart />`, `<ActionIdeasList />`, `<ActivityFeed />`.
  - `Workout.jsx`: Extract `<ExercisePlayer />`, `<SetRepTracker />`, `<WorkoutControls />`, `<RestTimerModal />`.
  - `Nutrition.jsx`: Extract `<MacroRings />`, `<DailyPlateCard />`, `<MealSwapModal />`, `<GroceryListDrawer />`.
- **Related Files:**
  - `frontend/src/pages/Dashboard.jsx` (3,748 lines)
  - `frontend/src/pages/Workout.jsx` (3,575 lines)
  - `frontend/src/pages/Nutrition.jsx` (1,562 lines)
- **Why It Matters:** Massive components cause unnecessary re-renders across 3,500 lines of JSX on every state change, degrading UI responsiveness (`BUG-MONO-01`).
- **Expected Outcome:** Modular, testable React components under 300 lines each; improved frame rates and maintainability.
- **Estimated Complexity:** High (4 days)

---

### TASK-P2-02: Complete Python Route Migration & Disintegrate `server.py` Monolith
- **Task Description:** Complete the migration started in `backend-python/app/routes/workout.py`:
  - Move `@app.post("/workout")`, `@app.post("/workout/async")`, and `@app.get("/api/weekly-plan")` out of `server.py` into `app/routes/workout.py`.
  - Move nutrition routes into `app/routes/meal_plan.py`.
  - Reduce `server.py` from 4,077 lines to under 200 lines as a pure FastAPI bootstrap entrypoint.
- **Related Files:**
  - `backend-python/server.py`
  - `backend-python/app/routes/workout.py`
  - `backend-python/app/routes/meal_plan.py`
- **Why It Matters:** Monolithic server files make concurrent team development prone to git merge conflicts and obscure route discovery (`BUG-ARCH-02`).
- **Expected Outcome:** Clean modular FastAPI routers using `include_router`.
- **Estimated Complexity:** Medium (2 days)

---

### TASK-P2-03: Upgrade Discontinued `google-generativeai` SDK to `google-genai`
- **Task Description:** Replace deprecated `google-generativeai` package with the modern official `google-genai` SDK in `requirements.txt` and `backend-python/app/gemini_service.py`.
- **Related Files:**
  - `backend-python/app/gemini_service.py`
  - `backend-python/requirements.txt`
- **Why It Matters:** Google has ended maintenance for `google-generativeai`; future API revisions will trigger breaking exceptions (`BUG-DEP-01`).
- **Expected Outcome:** Eliminates deprecation warnings; ensures long-term AI chat stability.
- **Estimated Complexity:** Medium (1 day)

---

### TASK-P2-04: Fix Scikit-Learn LabelEncoder Token Drift (1,500+ Warnings)
- **Task Description:** In `backend-python/app/feature_pipeline.py` and `workout_engine.py`, add explicit vocabulary sanitization maps that convert token variants (e.g. `"Dumbbells"` → `"dumbbell"`, `"Resistance Bands"` → `"bands"`) into the exact canonical categories learned during model training.
- **Related Files:**
  - `backend-python/app/feature_pipeline.py`
  - `backend-python/app/workout_engine.py`
- **Why It Matters:** Eliminates 1,500+ `UserWarning: unknown class(es)` per test run and prevents XGBoost from defaulting unrecognized parameters to 0 (`BUG-ML-01`).
- **Expected Outcome:** Clean feature matrices with improved model prediction accuracy.
- **Estimated Complexity:** Medium (1 day)

---

### TASK-P2-05: Adopt FastAPI `lifespan` Context Manager Protocol
- **Task Description:** Migrate `@app.on_event("startup")` and `@app.on_event("shutdown")` in `backend-python/server.py` to FastAPI's recommended `asynccontextmanager` `lifespan(app)` hook.
- **Related Files:**
  - `backend-python/server.py`
- **Why It Matters:** Resolves deprecation warnings and prevents breakage in future FastAPI/Starlette major releases (`BUG-DEP-02`).
- **Expected Outcome:** Idiomatic, future-proof startup/shutdown connection handling.
- **Estimated Complexity:** Low (0.5 day)

---

## Phase P3: Low Priority (Long-Term Architectural Enhancements)

### TASK-P3-01: Symmetric Bi-Directional Keypoint Tracking in Python Detectors
- **Task Description:** Upgrade `backend-python/app/detectors/curl_detector.py` and sibling detectors to compute visibility for both left and right limbs simultaneously, dynamically tracking the limb with higher camera confidence (matching the client-side `PoseDetector.jsx` implementation).
- **Related Files:**
  - `backend-python/app/detectors/curl_detector.py`
  - `backend-python/app/detectors/base_detector.py`
- **Why It Matters:** Ensures Python-based pose evaluation can handle users performing curls or raises on either side of their body (`BUG-CV-01`).
- **Expected Outcome:** Accurate form scoring and rep counting regardless of camera orientation.
- **Estimated Complexity:** Low (0.5 day)

---

### TASK-P3-02: Implement Asynchronous Job Queue for Plan Generation
- **Task Description:** Replace synchronous HTTP plan generation with an asynchronous background task queue (Celery with Redis or BullMQ on Node.js). Long-running meal optimizations (which take 3–5 seconds) return a job ID immediately with WebSocket / polling updates.
- **Related Files:**
  - `backend-python/server.py`
  - `frontend/src/api.js`
- **Why It Matters:** Prevents HTTP gateway timeouts on slow mobile connections or during traffic spikes.
- **Expected Outcome:** Immediate UI responsiveness with progress bars during heavy plan synthesis.
- **Estimated Complexity:** High (4 days)

---

### TASK-P3-03: End-to-End Headless Browser Test Suite (Playwright)
- **Task Description:** Implement an automated Playwright E2E suite covering:
  1. User Registration → Profile Setup → Onboarding Plan Generation.
  2. Workout Session Execution → Exercise Progression → Completion Logging.
  3. Daily Habit Tracking → Streak Update → Dashboard Trend Reflection.
  4. Admin Login → User Suspension → Verification of Access Block.
- **Related Files:**
  - `e2e/playwright.config.js`
  - `.github/workflows/quality-gates.yml`
- **Why It Matters:** Validates cross-service contracts across React, Node, and Python in a real browser environment.
- **Expected Outcome:** Comprehensive end-to-end regression protection before production deployments.
- **Estimated Complexity:** High (5 days)
