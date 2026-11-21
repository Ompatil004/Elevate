# CHANGELOG
## Elevate Fitness & Nutrition Intelligence Platform

All notable changes made during the Master Autonomous Engineering Transformation are documented in this file.

The project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [2.0.0] - 2026-11-20

### Security
- **JWT & Cookie Expiration Alignment:** Enforced strict 7-day expiration for standard users and 2-hour expiration for administrators across `auth.js` and `adminAuth.js`. Synced HTTP-only cookie `maxAge` to match token expirations exactly.
- **Account Suspension Enforcement:** Hardened `backend-node/middleware/auth.js` to perform authoritative database checks for account existence and suspension state (`isSuspended`). Prevented suspended users from bypassing security checks using static JWT claims. Added automated regression tests in `auth.middleware.test.js`.
- **Secure Session Destruction:** Implemented robust cookie-clearing logic on user and admin logout routes with explicit path and sameSite matching.

### Refactoring & Architecture
- **Frontend Modular API Layer:** Decomposed monolithic 673-line `frontend/src/api.js` into domain-specific modules in `frontend/src/api/` (`apiClient.js`, `authApi.js`, `profileApi.js`, `workoutApi.js`, `nutritionApi.js`, `adminApi.js`, `chatbotApi.js`). Provided a backwards-compatible bridge in `api.js`.
- **Pose Detection Subsystem:** Decomposed monolithic 1,007-line `PoseDetector.jsx` into `frontend/src/features/pose-detection/`:
  - `poseMath.js`: Joint angle math, EMA smoothing, and movement pattern classification.
  - `formSafety.js`: Exercise-specific form violation detection and safety verbal cues.
  - `repCounterMachine.js`: Finite state machine with hysteresis thresholds and ROM calibration.
  - `poseDrawing.js`: HTML5 Canvas skeleton, angles, and HUD gauge rendering.
  - Reduced `PoseDetector.jsx` from 1,007 lines to 297 lines (70.5% reduction).
- **Nutrition Subsystem:** Decomposed monolithic 1,562-line `Nutrition.jsx` into `frontend/src/features/nutrition/`:
  - `MacroStat.jsx`: Reusable macro progress cards with SVG rings.
  - `MealCard.jsx`: Meal items, portion sizing, checkboxes, and swap modals.
  - `MealSwapModal.jsx`: Food alternative picker.
  - `HistoryPanel.jsx`: 7-day caloric history drawer.
  - `nutritionHelpers.js`, `nutritionServing.js`, `nutritionStyles.js`.
  - Reduced `Nutrition.jsx` from 1,562 lines to 488 lines (68.7% reduction).
- **Workout Subsystem:** Decomposed monolithic 3,598-line `Workout.jsx` into `frontend/src/features/workout/`:
  - `AnimatedImageSequence.jsx`: Canvas-based GIF loop animation component.
  - `DaySelector.jsx`: Weekly plan card grid with status badges.
  - `RestDaySwapModal.jsx`: Rest-day repositioning modal.
  - `SwapHistoryModal.jsx`: Exercise swap history audit drawer.
  - `ExerciseVariationModal.jsx`: AI progression/regression modal.
  - `workoutConstants.js` & `workoutStyles.js`.
  - Reduced `Workout.jsx` by 720 lines.
- **Dashboard Subsystem:** Decomposed monolithic 3,737-line `Dashboard.jsx` into `frontend/src/features/dashboard/`:
  - `ActivityChart.jsx`: Standalone SVG Bézier spline chart.
  - `heroActionConfig.js`: Hero card themes, dynamic water goal calculator, and radial score formulas.
  - Reduced `Dashboard.jsx` by 538 lines.
- **FastAPI Modern Lifespan Migration:** Replaced deprecated `@app.on_event("startup")` and `@app.on_event("shutdown")` in `backend-python/server.py` with `@asynccontextmanager` `lifespan(app: FastAPI)` context manager.

### Bug Fixes
- **Nutrition Candidate Fallback Regression (P0-04):** Resolved blueprint validation contradiction in `candidate_generator.py` for low-carb and composite meal plates. Reduced candidate fallback rate from 9.0% to **0.00%**. All candidate health tests pass.
- **Frontend ESLint Zero-Error Pass (P0-03):** Fixed all 8 ESLint `no-unused-vars` and missing hook dependency errors across `PoseDetector.jsx`, `Dashboard.jsx`, and `Workout.jsx`.
- **ML LabelEncoder Vocabulary Drift (P2-ML2):** Pre-fitted `equipment_encoder` and `injury_encoder` with canonical vocabularies in `backend-python/app/feature_pipeline.py`. Implemented safe unrecognized class filtering. Eliminated 1,547 runtime `UserWarning` messages during test execution.
- **Unbounded MongoDB Growth (P1-02):** Implemented MongoDB `$push` with `$slice: -100` on activity logging in `backend-node/routes/profile.js`, capping activity documents to 100 entries.
- **Timezone Normalization (P1-03):** Integrated standard IANA timezone detection and ISO date conversion in `backend-node/utils/mealUtils.js` and `frontend/src/utils/storage.js`.

### Testing & Quality
- **Automated Test Suite Expansion:** 156 total automated tests green across all 3 tiers (37 Vitest, 26 Jest, 93 Pytest).
- **Regression Suite Passing:** Verified complete backwards compatibility for all API endpoints, frontend component props, and machine learning inference contracts.
- **Production Build:** Vite production build compiles in 2.76s with 0 errors.
