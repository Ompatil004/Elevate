# PROJECT ELEVATE — Complete Technical Overview

> Generated from full codebase inspection on 2026-09-18. Every claim cites actual files and functions.

---

## 1. PROJECT PURPOSE & SCOPE

### What does this project do?

Elevate is an **AI-powered fitness web application** that generates personalized weekly workout plans and meal plans, tracks exercise form via real-time camera-based pose detection, provides an AI chatbot coach (powered by Google Gemini), and logs daily health metrics (sleep, hydration, workout completion). It also includes a full admin panel for platform management.

### Who are the intended users?

- **Primary**: Fitness enthusiasts (beginner to advanced) who want personalized, data-driven workout and nutrition plans without hiring a human coach.
- **Secondary**: A single platform **owner/admin** who manages users, exercises, announcements, and system configuration.

### What problem does it solve?

It replaces generic cookie-cutter workout templates with ML-driven personalization that adapts to the user's biometrics, experience level, available equipment, injuries, and consistency streaks. Real-time pose tracking provides form correction that typically requires an in-person trainer.

---

## 2. TECH STACK

### Languages & Frameworks

| Layer | Technology | Version (from manifests) |
|---|---|---|
| Frontend | React (Vite) | React 19.2.0, Vite 7.2.4 |
| Backend (Auth/Profile) | Node.js / Express | Express 5.2.1 |
| Backend (AI/ML) | Python / FastAPI | FastAPI 0.135.2 |
| Database | MongoDB (Mongoose + Motor) | Mongoose 9.1.5, Motor 3.7.1 |

### Major Libraries

**Frontend** (`frontend/package.json`):
- `@mediapipe/tasks-vision` ^0.10.34 — Browser-side pose landmark detection
- `axios` ^1.13.2 — HTTP client
- `react-router-dom` ^7.12.0 — SPA routing
- Testing: Vitest 3.2.3, Testing Library React 16.3.0

**Node Backend** (`backend-node/package.json`):
- `bcryptjs` ^3.0.3 — Password hashing
- `jsonwebtoken` ^9.0.3 — JWT auth
- `google-auth-library` ^10.5.0 — Google OAuth
- `csrf-csrf` ^3.2.2 — Double-submit CSRF protection
- `express-rate-limit` ^8.3.2 — Rate limiting
- `express-validator` ^7.2.1 — Input validation
- `nodemailer` ^8.0.5 — Email sending (password reset)
- `mongoose` ^9.1.5 — MongoDB ODM

**Python Backend** (`backend-python/requirements.txt`):
- `xgboost` 3.2.0 — ML workout/nutrition prediction
- `scikit-learn` 1.8.0 — ML utilities, MultiOutputRegressor
- `mediapipe` 0.10.33, `opencv-python` 4.13.0.92 — Server-side pose tracking
- `google-generativeai` 0.8.6 — Gemini AI chatbot
- `tenacity` 9.1.2 — Retry/circuit breaker
- `motor` 3.7.1, `pymongo` 4.16.0 — Async MongoDB driver
- `pyjwt` 2.12.1 — JWT verification on Python side
- `redis` 7.4.0, `celery` 5.6.3 — Listed but used for optional plan caching
- `pandas` 3.0.1, `numpy` 2.4.3 — Data processing

### Database

**MongoDB** — Single database `elevate_fitness` shared by both backends. Chosen for flexible schema (user profiles contain embedded workout plans, meal histories, and trend arrays that vary per user).

### Third-Party Services

| Service | Purpose | Config Key |
|---|---|---|
| Google OAuth 2.0 | Social login | `GOOGLE_CLIENT_ID`, `GOOGLE_CLIENT_SECRET` |
| Google Gemini API | AI chatbot + workout config generation | `GEMINI_API_KEY` |
| SMTP (Nodemailer) | Password reset emails | `SMTP_HOST`, `SMTP_USER`, `SMTP_PASS` |
| API Ninjas | External exercise data (frontend) | `VITE_API_NINJAS_KEY` |
| USDA FoodData Central | External nutrition data (frontend) | `VITE_USDA_API_KEY` |
| Redis (optional) | Plan cache layer | `REDIS_URL` / `PLAN_CACHE_REDIS_URL` |

---

## 3. ARCHITECTURE

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        BROWSER (SPA)                            │
│  React/Vite on port 5173                                        │
│  ┌─────────────┐  ┌──────────────┐  ┌─────────────────────────┐ │
│  │ AuthAPI      │  │ FitnessAPI   │  │ MediaPipe PoseLandmarker│ │
│  │ (→ :5000)    │  │ (→ :5000     │  │ (in-browser WASM)       │ │
│  │              │  │  /api/python)│  │                         │ │
│  └──────┬───────┘  └──────┬───────┘  └─────────────────────────┘ │
└─────────┼──────────────────┼────────────────────────────────────┘
          │                  │
          ▼                  ▼
┌─────────────────┐  ┌─────────────────┐
│ Node.js/Express  │  │ (Reverse proxy) │
│ Port 5000        │──│ /api/python/*   │
│ Auth, Profiles,  │  │ → Python :8000  │
│ Admin, CSRF      │  └────────┬────────┘
└────────┬─────────┘           │
         │                     ▼
         │           ┌─────────────────┐
         │           │ Python/FastAPI   │
         │           │ Port 8000        │
         │           │ Workout engine,  │
         │           │ Nutrition engine,│
         │           │ Gemini chatbot,  │
         │           │ XGBoost ML,      │
         │           │ Pose tracking    │
         │           └────────┬─────────┘
         │                    │
         ▼                    ▼
    ┌──────────────────────────────┐
    │        MongoDB               │
    │   Database: elevate_fitness  │
    └──────────────────────────────┘
```

**Key architectural decision**: The Node backend acts as a **reverse proxy** for Python API calls (`/api/python/*` → `http://localhost:8000`). This means the frontend never talks directly to Python — all requests go through Node, which handles auth cookie forwarding, CSRF, and structured error wrapping. See `backend-node/routes/pythonProxy.js`.

### Folder Structure

```
Elevate-fitness/
├── frontend/                     # React SPA (Vite)
│   └── src/
│       ├── pages/                # Route-level page components
│       │   ├── Dashboard.jsx     # Main dashboard (162KB — largest file)
│       │   ├── Workout.jsx       # Workout plan view + execution (165KB)
│       │   ├── Nutrition.jsx     # Meal plan view + tracking (84KB)
│       │   ├── Chatbot.jsx       # AI chat interface
│       │   ├── ProfileSetup.jsx  # Onboarding profile form
│       │   ├── Login.jsx / Register.jsx / ForgotPassword.jsx
│       │   └── admin/            # Admin panel pages
│       ├── components/
│       │   ├── PoseDetector.jsx  # MediaPipe pose detection + rep counting
│       │   ├── Navbar.jsx        # Global navigation
│       │   ├── AuroraBackground.jsx # Animated background
│       │   └── NotificationProvider.jsx
│       ├── utils/                # Circuit breaker, storage, Google auth
│       ├── context/              # ThemeContext
│       ├── api.js                # All API call functions (centralized)
│       └── App.jsx               # Router + auth state management
│
├── backend-node/                 # Node.js/Express backend
│   ├── server.js                 # App bootstrap, middleware, route mounting
│   ├── routes/
│   │   ├── auth.js               # Register, login, Google OAuth, password reset
│   │   ├── profile.js            # User profile CRUD, trends, workout/meal history
│   │   ├── pythonProxy.js        # Reverse proxy to Python backend
│   │   ├── users.js              # Workout/meal save, external API proxy
│   │   ├── adminAuth.js          # Admin login/logout/verify
│   │   ├── adminUsers.js         # User management (suspend, delete, etc.)
│   │   ├── adminSystem.js        # System health, maintenance, announcements
│   │   └── adminContent.js       # Exercise + workout rules CRUD
│   ├── models/                   # Mongoose schemas
│   │   ├── User.js               # Main user model (all profile data)
│   │   ├── Exercise.js           # Custom exercises
│   │   ├── SystemConfig.js       # KV store (maintenance mode, etc.)
│   │   └── AdminAuditLog.js      # Admin action audit trail
│   ├── middleware/
│   │   ├── auth.js               # JWT verification (HttpOnly cookie)
│   │   ├── adminAuth.js          # Admin JWT + IP whitelist
│   │   ├── adminRateLimit.js     # Rate limiters for all endpoints
│   │   └── validate.js           # express-validator schemas
│   ├── services/
│   │   └── securityNotificationService.js  # Email + webhook alerts
│   └── utils/
│       └── mealUtils.js          # Shared meal data helpers
│
├── backend-python/               # Python/FastAPI AI backend
│   ├── server.py                 # Main FastAPI app (4045 lines, 158KB)
│   ├── app/
│   │   ├── workout_engine.py     # Workout plan generation (250KB!)
│   │   ├── meal_engine.py        # Nutrition plan generation
│   │   ├── deterministic_meal_engine.py  # Rule-based meal planning
│   │   ├── gemini_service.py     # Google Gemini AI integration
│   │   ├── circuit_breaker.py    # Retry + circuit breaker pattern
│   │   ├── safety_layer.py       # Medical safety constraints
│   │   ├── multi_output_xgboost_model.py  # XGBoost for workout params
│   │   ├── multitarget_nutrition_model.py # XGBoost for nutrition
│   │   ├── feature_pipeline.py   # ML feature engineering
│   │   ├── evaluation_framework.py # Model evaluation + A/B testing
│   │   ├── pose_tracker.py       # Server-side MediaPipe pose tracking
│   │   ├── progression_engine.py # Progressive overload logic
│   │   ├── profile_change_detection.py # Detect profile changes
│   │   ├── plan_cache.py         # Redis/in-memory plan caching
│   │   ├── db.py                 # MongoDB connection (Motor async)
│   │   ├── detectors/            # Exercise-specific pose detectors
│   │   ├── routes/               # FastAPI sub-routers
│   │   ├── models/               # Pydantic models + pickled ML models
│   │   ├── config/               # exercise_mapping.json (1300+ exercises)
│   │   └── utils/                # Model integrity, movement mapper
│   ├── data/                     # Training datasets (CSV, JSON)
│   ├── tests/                    # Pytest test suite (23 test files)
│   └── scripts/                  # DB index creation, seed data
│
├── docs/                         # Project documentation
└── .github/workflows/
    └── quality-gates.yml         # CI pipeline
```

### Key Design Patterns

1. **Proxy Gateway** — Node serves as API gateway for Python, forwarding auth tokens
2. **Circuit Breaker** — Both frontend (`utils/circuitBreaker.js`) and backend (`app/circuit_breaker.py`) implement circuit breakers with exponential backoff for Gemini API calls
3. **State Machine** — Rep counting uses a 3-phase state machine: `rest → contracting → extended → rest` (`PoseDetector.jsx:L320-L345`)
4. **Strategy Pattern** — `DetectorFactory` selects exercise-specific pose detectors at runtime (`app/detectors/detector_factory.py`)
5. **Safety Layer Pattern** — All ML predictions pass through a safety layer that clamps outputs to physiological bounds
6. **Request Deduplication** — Frontend deduplicates concurrent identical API calls for workout/nutrition generation (`api.js:L294-L309`)

---

## 4. DATA MODEL

### MongoDB Collections

All reside in the `elevate_fitness` database.

#### `users` (Primary collection)

Defined in `backend-node/models/User.js`. Single-collection design with inlined sub-schemas.

| Field Group | Key Fields | Notes |
|---|---|---|
| **Identity** | `name`, `email` (unique), `password` (bcrypt hash), `avatar` | `email` is required + unique |
| **Security** | `isSuspended`, `role` (user\|owner), `passwordResetTokenHash`, `mustChangePassword`, `adminLastLoginAt`, `adminLockedUntil` | Only one `owner` role allowed (unique partial index) |
| **Fitness Profile** | `age`, `weight`, `height`, `gender`, `goal`, `experience`, `equipment[]`, `allergies[]`, `body_issues[]`, `days_per_week`, `dietary_preference` | `goal` enum: Weight Loss, Fat Loss, Muscle Gain, Maintenance, Strength, Endurance, Athletic Performance |
| **Activity** | `streak`, `lastWorkoutDate`, `trends[]` (TrendEntrySchema), `workouts[]`, `meals[]`, `activities[]` | `trends` stores daily snapshots: workout/meal completion, macros, water, sleep |
| **Workout Schedule** | `workoutPatterns`, `restDayPreferences[]`, `firstWorkoutDay` | Patterns: Full Body, PPL, Upper/Lower, Bro Split, Custom |
| **Generated Plans** | `workoutPlan` (Mixed), `workoutWeekMetadata` (Mixed), `latestNutritionPlan` (Mixed), `nutritionWeekMetadata` | Plans cached per-user, regenerated weekly |
| **Timestamps** | `createdAt`, `updatedAt`, `registrationDate`, `workoutPlanGeneratedAt`, `nutritionPlanGeneratedAt` | |

#### `exercises`

Defined in `backend-node/models/Exercise.js`. Admin-managed exercise library.

| Field | Type | Notes |
|---|---|---|
| `name` | String (required) | |
| `category` | String (required) | |
| `difficulty` | String | Default: 'intermediate' |
| `equipment` | [String] | |
| `muscleGroups` | [String] | |
| `gifUrl` | String | Animation URL |
| `active` | Boolean | Soft-delete flag |
| `createdBy` / `updatedBy` | ObjectId → User | |

#### `adminauditlogs`

Defined in `backend-node/models/AdminAuditLog.js`. Immutable audit trail.

| Field | Type | Notes |
|---|---|---|
| `ownerId` | ObjectId → User | Who performed the action |
| `action` | Enum | LOGIN, USER_SUSPEND, MAINTENANCE_TOGGLE, etc. (17 values) |
| `targetType` | Enum | user, exercise, config, system, announcement, owner |
| `details` | Mixed | Action-specific payload |
| `ipAddress`, `userAgent` | String | Request context |
| Indexed on | | `(ownerId, timestamp)`, `(action, timestamp)` |

#### `systemconfigs`

Defined in `backend-node/models/SystemConfig.js`. Key-value store.

| Used Keys | Purpose |
|---|---|
| `maintenanceMode` | `{ enabled: bool, message: string }` — global kill switch |
| (announcements) | Stored as system config entries |

#### Additional Collections (Python-side)

Accessed via `app/db.py` helper functions:

| Collection | Purpose |
|---|---|
| `weekly_workout_plans` | Cached generated plans per user per ISO-week |
| `weekly_meal_plans` | Meal plan storage |
| `meal_plan_cache` | Durable meal-plan cache keyed by profile hash + ISO-week |
| `workout_completions` | Workout completion records |
| `meal_completions` | Meal completion records |
| `swap_history` | Audit trail for day swaps (rest↔workout) |
| `workout_history` | Historical workout records |
| `meal_history` | Historical meal records |
| `daily_logs` | Daily check-in logs (sleep, water, workout status) |

### Business Rules in Schema

1. **Single owner constraint**: `User.role = 'owner'` has a unique partial index — only one admin account can exist (`User.js:L147-L150`).
2. **Goal enum**: Must be one of 8 predefined values; `'Maintain'` is a short alias for `'Maintenance'` (`User.js:L58`).
3. **Days per week**: Constrained to `min: 1, max: 7` at schema level.
4. **Workout patterns**: Enum-validated to 5 options.

---

## 5. CORE FEATURES & BUSINESS LOGIC

### 5.1 AI Workout Plan Generation

**Flow**: User profile → `POST /workout` → `workout_engine.py` → XGBoost prediction → Safety layer → 7-day plan

- **Engine**: `app/workout_engine.py` (250KB, the largest module) generates a complete 7-day plan with exercises, sets, reps, rest times.
- **ML Model**: `MultiOutputXGBoostModel` (`app/multi_output_xgboost_model.py`) predicts 5 targets: `sets`, `reps_low`, `reps_high`, `rest_time`, `intensity` from 17 user features.
- **Feature Pipeline**: `app/feature_pipeline.py` transforms raw profile into model-ready features (BMI calculation, experience encoding, equipment richness scoring, age-adjusted capacity).
- **Safety Layer**: `app/safety_layer.py` applies post-prediction constraints:
  - Seniors (60+): intensity × 0.85, volume × 0.80, rest × 1.25
  - Injury filtering: exercises with blocked `Check_Type` are removed (e.g., knee injury → no `squat_logic`)
  - Beginner caps: max 70% intensity, max 4 sets
- **Gemini Enhancement**: `gemini_service.py:generate_workout_config()` optionally uses AI to determine optimal sets/reps/rest/rest-days, with circuit breaker fallback.
- **Caching**: Plans are cached per-user per ISO-week in MongoDB + optional Redis. Stale plans trigger automatic regeneration.
- **Async Generation**: `POST /workout/async` returns a `job_id`; frontend polls `GET /workout/status/{job_id}` until complete.

### 5.2 AI Nutrition Plan Generation

**Flow**: Profile + workout plan → `POST /nutrition` → `meal_engine.py` → 7-day meal plan

- **Engine**: `app/meal_engine.py` (38KB) + `app/deterministic_meal_engine.py` (65KB) generate daily meal plans.
- **ML Model**: `MultiTargetNutritionModel` (`app/multitarget_nutrition_model.py`) predicts caloric/macro targets.
- **Nutrition Intelligence**: `app/nutrition_intelligence.py` handles food knowledge base, ingredient compatibility, dietary preference filtering.
- **Data Sources**: 15 data files in `backend-python/data/` including `food_knowledge_base.json` (1.5MB), `recipe_database.json`, IFCT2017 Indian food composition data, meal blueprints.
- **Meal Swapping**: `POST /nutrition/swap` allows users to swap individual meals with alternatives within weekly limits (default: 3 swaps/week).

### 5.3 Real-Time Pose Detection & Rep Counting

**Frontend** (`PoseDetector.jsx`, 1008 lines):

1. **MediaPipe PoseLandmarker** runs in-browser via WASM, detecting 33 body landmarks per frame.
2. **Movement Pattern Classification**: Maps 1300+ exercises to 10 movement patterns (CURL, PRESS, SQUAT, HINGE, LUNGE, RAISE, CORE, CARDIO, CALF, GENERIC) via `PATTERN_MAP` and `LEGACY_MOVEMENT_PATTERNS` keyword fallback.
3. **3D Angle Calculation**: `calcAngle()` computes joint angles using dot-product + arccos on 3D vectors.
4. **Rep Counting State Machine**: 3-phase (`rest → contracting → extended → rest`) with:
   - Multi-frame noise gate (2-3 consecutive frames required to confirm transition)
   - Hysteresis bands (entry: 5°, exit: 8°)
   - Auto-calibration after each rep (narrows thresholds to user's personal ROM)
   - ROM validation (minimum 20% range-of-motion to count a rep)
   - Per-pattern cooldowns (400-600ms)
5. **Form Analysis**: `checkForm()` provides real-time safety warnings per exercise pattern (e.g., "Keep elbows closer to your sides" for curls with shoulder > 100°).
6. **Adaptive EMA Smoothing**: Different alpha values per exercise speed category (fast=0.40, slow=0.22).

**Backend** (`pose_tracker.py`, 1751 lines):

- Server-side pose tracking using OpenCV + MediaPipe Python.
- `DetectorFactory` (`app/detectors/`) provides exercise-specific detector classes: `SquatDetector`, `CurlDetector`, `PushDetector`, `HingeDetector`, `LungeDetector`, `PlankDetector`, `PullDetector`, `RaiseDetector`, `GenericDetector`.
- Exercise mapping from `config/exercise_mapping.json` (180KB, 1300+ exercises with trackability flags).

### 5.4 AI Chatbot

**Flow**: User message → `POST /api/chat` → `gemini_service.py` → Gemini API → response

- **System Prompt**: Built from user profile (goal, experience, age, injuries, equipment, recent workouts, daily activity log). Strict scope constraint: only fitness/nutrition/Elevate topics allowed.
- **Conversation History**: Last 20 messages, each capped at 500 chars.
- **Privacy**: `consent_to_health_processing` flag controls whether PII (age, weight, allergies) is sent to Gemini.
- **Fallback**: When Gemini is unavailable, `_build_contextual_offline_response()` returns profile-aware deterministic responses across 6 categories (greeting, workout, nutrition, recovery, form, motivation).
- **Rate Limiting**: 1.5s cooldown per client IP.

### 5.5 Dashboard & Progress Tracking

- **Trend Tracking**: `TrendEntrySchema` records daily: workout/meal completion, macros, water intake, sleep, streak.
- **Streak System**: Consecutive workout days tracked with progressive overload adjustments.
- **Daily Check-in**: `POST /api/daily-log` saves sleep hours, water intake, workout completion. `GET /api/daily-log/week` returns last 7 days + summary.
- **Session Results**: `POST /api/workout/session-result` accepts form score and rep count per exercise.

### 5.6 Day Swapping

Users can swap rest days ↔ workout days within their weekly plan:
- `POST /api/swap-rest-to-workout` — Convert a rest day to a workout day (generates exercises).
- `POST /api/swap-workout-to-rest` — Convert a workout day to a rest day.
- Weekly swap limit: 3 per week (configurable). Tracked in `workoutWeekMetadata.swap_history`.
- Swap audit trail stored in `swap_history` collection.

### 5.7 Admin Panel

Full admin panel accessible at `/admin/*`:
- **User Management**: List, view, suspend, activate, delete users, force password reset.
- **Content Management**: CRUD for exercises, workout rules.
- **System Controls**: Maintenance mode toggle, system health check, announcements.
- **Audit Logging**: All admin actions logged to `AdminAuditLog` with IP, user agent, timestamp.
- **Security**: Separate `ADMIN_JWT_SECRET`, IP whitelist (`ADMIN_ALLOWED_IPS`), admin-specific rate limits, admin lockout after failed attempts.

---

## 6. API SURFACE

### Node.js Backend (port 5000)

#### Auth Routes (`/api/auth`)

| Method | Path | Purpose | Auth | Rate Limit |
|---|---|---|---|---|
| POST | `/register` | Create account | None | 5/hr per IP |
| POST | `/login` | Email/password login | None | 10/15min per IP |
| POST | `/google` | Google OAuth login | None | — |
| POST | `/logout` | Clear auth cookie | Authenticated | — |
| GET | `/session` | Check session status (cookie probe) | None | — |
| POST | `/reset-password/request` | Send password reset email | None | — |
| POST | `/reset-password/confirm` | Reset password with token | None | — |

#### Profile Routes (`/api/profile`)

| Method | Path | Purpose | Auth |
|---|---|---|---|
| GET | `/` | Get full user profile | ✅ |
| POST | `/update` | Update profile fields | ✅ |
| GET | `/trends` | Get trend data (daily snapshots) | ✅ |
| POST | `/trends` | Save trend data | ✅ |
| GET | `/workout-history` | Get workout history | ✅ |
| POST | `/workout-history` | Save workout history | ✅ |
| POST | `/workout-history/undo-swap` | Undo last workout swap | ✅ |
| GET | `/meal-history` | Get meal history | ✅ |
| POST | `/meal-history` | Save meal history | ✅ |
| POST | `/activities/log` | Log an activity | ✅ |
| GET | `/activities/recent` | Get recent activities | ✅ |
| POST | `/activities/sync` | Bulk sync activities | ✅ |

#### Python Proxy (`/api/python/*`)

All requests forwarded to Python backend with auth token. See Python endpoints below.

#### Admin Routes (`/api/admin`)

| Method | Path | Purpose |
|---|---|---|
| POST | `/login` | Admin authentication |
| POST | `/logout` | Admin logout |
| GET | `/verify` | Verify admin session |
| GET | `/users` | List users (paginated, searchable) |
| GET | `/users/stats/overview` | User statistics |
| GET | `/users/:id` | Get specific user |
| POST | `/users/:id/suspend` | Suspend user |
| POST | `/users/:id/activate` | Reactivate user |
| POST | `/users/:id/reset-password` | Force password reset |
| DELETE | `/users/:id` | Delete user |
| GET | `/system/health` | System health check |
| GET | `/system/stats` | System statistics |
| GET/POST | `/system/maintenance` | Get/set maintenance mode |
| GET | `/system/audit-logs` | Query audit logs |
| POST | `/system/announcement` | Create announcement |
| DELETE | `/system/announcement/:id` | Delete announcement |
| GET | `/system/announcements` | List announcements |
| GET | `/content/exercises` | List exercises |
| POST | `/content/exercises` | Create exercise |
| PUT | `/content/exercises/:id` | Update exercise |
| DELETE | `/content/exercises/:id` | Delete exercise |
| GET/POST | `/content/workout-rules` | Get/set workout rules |

### Python Backend (port 8000)

| Method | Path | Purpose |
|---|---|---|
| POST | `/workout` | Generate 7-day workout plan |
| POST | `/workout/async` | Start async workout generation (returns `job_id`) |
| GET | `/workout/status/{job_id}` | Poll async job status |
| POST | `/workout/cache/invalidate` | Invalidate cached plan |
| GET | `/api/weekly-plan` | Get user's current weekly plan |
| GET | `/api/swap-options` | Get available swap options for a day |
| POST | `/api/swap-rest-to-workout` | Swap rest day → workout day |
| POST | `/api/swap-workout-to-rest` | Swap workout day → rest day |
| POST | `/nutrition` | Generate 7-day nutrition plan |
| POST | `/nutrition/swap` | Swap a meal within the plan |
| POST | `/api/chat` | AI chatbot (Gemini) |
| POST | `/api/workout/session-result` | Submit exercise form score |
| POST | `/api/daily-log` | Save daily check-in |
| GET | `/api/daily-log/week` | Get last 7 daily logs |
| POST | `/generate-plan` | Generate AI-driven plan |
| PUT | `/profile/update-with-plans` | Update profile + regenerate plans |
| PUT | `/profile/update-safe` | Safe profile update |
| GET | `/api/models/status` | ML model status |
| POST | `/api/models/warmup` | Warm up ML models |
| GET | `/health` | Health check |

### Authentication Model

1. **User Auth**: JWT stored in HttpOnly cookie (`elevate_token`). Set on login/register. Verified by `middleware/auth.js`.
   - Cookie: `httpOnly: true`, `sameSite: 'none'` (prod) / `'lax'` (dev), `secure` in prod.
   - Fallback: `x-auth-token` header still accepted for cross-site deployments.
   - Suspension check embedded in JWT payload (`isSuspended` field) to avoid DB lookup on every request.

2. **Admin Auth**: Separate JWT (`ADMIN_JWT_SECRET`), IP whitelist, admin lockout after failed attempts. Stored in separate cookie.

3. **CSRF**: Double-submit cookie pattern via `csrf-csrf`. Token fetched via `GET /api/csrf-token`, sent in `x-csrf-token` header on all mutating requests. Auth endpoints (login/register/Google) are exempt.

4. **Python Backend Auth**: Receives JWT forwarded from Node proxy. Verifies using shared `JWT_SECRET` via `pyjwt`. See `app/core/auth.py`.

### Rate Limiting

| Endpoint | Window | Max Requests |
|---|---|---|
| Login | 15 min | 10 per IP |
| Register | 60 min | 5 per IP |
| Admin login | 15 min | 10 per IP |
| Admin API | 1 min | 120 per IP |
| Chatbot | 1.5s cooldown | 1 per IP per 1.5s |

### Error Handling

- Node: Consistent JSON error format: `{ message: string, code?: string }`. CSRF failures return 403 with `code: 'CSRF_INVALID'`. Python proxy errors wrapped with `code: 'PYTHON_UPSTREAM_ERROR'`.
- Python: FastAPI `HTTPException` with structured error details. Pydantic validation returns 422 with `detail` array.
- Frontend: Circuit breaker pattern prevents cascading failures; separate breakers for workout, nutrition, and background requests.

---

## 7. KEY WORKFLOWS

### User Onboarding

1. User visits `/register` → Fills name, email, password → `POST /api/auth/register` → bcrypt hash → User created in MongoDB → JWT cookie set → Redirect to `/profile-setup`.
2. **OR** User clicks "Sign in with Google" → `POST /api/auth/google` with Google ID token → `google-auth-library` verifies → User created/found → JWT cookie set.
3. Profile setup page (`ProfileSetup.jsx`) collects: age, weight, height, gender, goal, experience, equipment, allergies, body issues, days per week, dietary preference → `POST /api/profile/update`.
4. On first visit to `/workout`, the workout plan is generated via `POST /api/python/workout`.

### Workout Execution

1. User navigates to `/workout` → Frontend fetches profile → Calls `POST /api/python/workout` (or uses cached plan).
2. Plan displays 7 days. User selects today's workout.
3. User starts exercise → Camera activates → `PoseDetector.jsx` loads MediaPipe (WASM + model, preloaded at module import).
4. Real-time: landmarks extracted → angles calculated → rep counting state machine updates → form warnings displayed.
5. On exercise completion → Reps saved → `POST /api/workout/session-result` sends form score.
6. On workout completion → `POST /api/python/workout-completion` → Trends updated → Streak incremented.

### Day Swap Flow

1. User clicks "Swap to Workout" on a rest day → `POST /api/python/api/swap-rest-to-workout` with `{ day_index }`.
2. Server checks swap limit (3/week) → Generates exercises for that day → Updates plan in DB → Returns updated plan.
3. Swap recorded in `workoutWeekMetadata.swap_history` + `swap_history` collection.

### Password Reset

1. User clicks "Forgot Password" → `POST /api/auth/reset-password/request` with email.
2. Server generates random token, stores `sha256(token)` + expiry in user doc → Sends email via Nodemailer with reset link.
3. User clicks link → Frontend at `/reset-password?token=...&email=...` → User enters new password → `POST /api/auth/reset-password/confirm`.
4. Server verifies token hash + expiry → Updates password → Clears reset token.

### CI/CD Pipeline

`.github/workflows/quality-gates.yml` runs on every push/PR:

| Job | Steps |
|---|---|
| `frontend-quality` | npm ci → ESLint → Build → Vitest → Coverage → npm audit |
| `backend-node-quality` | npm ci → Jest → npm audit |
| `backend-python-quality` | ruff lint → ruff format check → py_compile (all modules) → pytest → pip-audit |
| `secret-scan` | gitleaks across full git history |

---

## 8. CONFIGURATION & ENVIRONMENT

### Frontend (`.env`)

| Variable | Purpose |
|---|---|
| `VITE_API_URL` | Node backend URL (default: `http://localhost:5000/api`) |
| `VITE_PYTHON_API_URL` | Python backend URL (only for dev reference) |
| `VITE_GOOGLE_CLIENT_ID` | Google OAuth client ID |
| `VITE_API_NINJAS_KEY` | API Ninjas key for exercise data |
| `VITE_USDA_API_KEY` | USDA API key for nutrition data |

### Node Backend (`.env`)

| Variable | Purpose | Default |
|---|---|---|
| `PORT` | Server port | 5000 |
| `NODE_ENV` | Environment (development/production) | — |
| `MONGO_URI` | MongoDB connection string | — |
| `JWT_SECRET` | JWT signing secret (validated against placeholders) | — |
| `ADMIN_JWT_SECRET` | Admin JWT signing secret | — |
| `ADMIN_SECRET_KEY_HASH` | bcrypt hash of admin bootstrap key | — |
| `GOOGLE_CLIENT_ID` | Google OAuth client ID | — |
| `GOOGLE_CLIENT_SECRET` | Google OAuth client secret | — |
| `CORS_ORIGINS` | Comma-separated allowed origins | — |
| `FRONTEND_URL` | Frontend URL for password reset emails | — |
| `SMTP_*` | Email configuration (HOST, PORT, USER, PASS, FROM) | — |
| `SECURITY_ALERT_EMAIL` | Email for security alerts | — |
| `SESSION_MAX_MS` | Session duration (currently commented out) | 14400000 |
| `BCRYPT_SALT_ROUNDS` | Password hashing cost | 12 |
| `TRUST_PROXY` | Trust X-Forwarded-For | 0 |
| Various `*_RATE_LIMIT_*` | Rate limit configuration | See defaults above |
| `ALLOW_INSECURE_MONGO` | Allow non-TLS Mongo in prod | 0 |
| `ENABLE_TEST_DB_ENDPOINT` | Enable /test-db diagnostic endpoint | 0 |

### Python Backend (`.env`)

| Variable | Purpose | Default |
|---|---|---|
| `PORT` | Server port | 8000 |
| `MONGO_URI` | MongoDB connection string | — |
| `JWT_SECRET` | Must match Node's JWT_SECRET | — |
| `GEMINI_API_KEY` | Google Gemini API key | — |
| `CORS_ORIGINS` | Comma-separated allowed origins | — |
| `REDIS_URL` | Redis for plan caching (optional) | — |
| `ASYNC_WORKOUT_JOB_TTL_SECONDS` | Async job expiry | 1800 |
| `ASYNC_WORKOUT_MAX_JOBS` | Max concurrent async jobs | 1000 |
| `PYTHON_PROXY_TIMEOUT_MS` | Proxy timeout from Node | 120000 |

### Build & Deploy

- **Frontend**: `npm run build` → Vite produces static assets. Dockerized via `frontend/Dockerfile` with nginx for production serving (`frontend/nginx.conf`).
- **Python Backend**: `python -m uvicorn server:app --reload --port 8000`. Dockerized via `backend-python/Dockerfile`.
- **Node Backend**: `node server.js` or `npm start`.
- **Local**: `start_all.bat` launches all three services.

---

## 9. DEPENDENCIES & INTEGRATIONS

### External APIs

| Service | Integration Point | Failure Mode |
|---|---|---|
| **Google Gemini** | `app/gemini_service.py` | Circuit breaker → offline fallback responses. Model fallback chain: `gemini-1.5-flash` → `gemini-1.5-pro` → `gemini-2.5-flash` → etc. |
| **Google OAuth** | `backend-node/routes/auth.js` | Login fails; user shown error |
| **API Ninjas** | Frontend-direct call via `api.js:getExternalExerciseData()` proxied through Node | Graceful degradation |
| **USDA FoodData** | Frontend-direct call via `api.js:getExternalNutritionData()` proxied through Node | Graceful degradation |
| **SMTP** | `securityNotificationService.js` | Best-effort; errors logged but don't block operations |

### Known Version Constraints

- `bcrypt==3.2.0` in Python: Pinned; newer versions have breaking API changes. Listed in requirements but may not be actively used (Node uses `bcryptjs`).
- MediaPipe WASM requires CDN access or self-hosted WASM files (served from `/wasm` path in dev).
- `redis` and `celery` listed in requirements but Redis is optional — the system works without it using in-memory caching.

### Fragile Dependencies

- **MediaPipe model loading**: Falls back through 5 model/delegate combinations (`poseModelPreload.js:L3-L9`). If all fail, pose detection is disabled.
- **Gemini API quota**: Can exhaust quickly; circuit breaker opens after repeated failures. All features degrade gracefully.
- **MongoDB connectivity**: Both backends crash if MongoDB is unreachable (Node retries 3 times with 5s delay).

---

## 10. KNOWN ISSUES / TODOs / TECH DEBT

### No TODO/FIXME/HACK Comments Found

A grep for `TODO`, `FIXME`, `HACK`, `XXX` across all `.py`, `.js`, and `.jsx` files returned **zero results**.

### Observed Tech Debt & Incomplete Features

1. **Session expiration disabled**: In `middleware/auth.js:L28-L44`, the session max-age check is commented out with the note "Session expiration check commented out as requested so sessions do not expire." JWTs currently never expire.

2. **`server.py` is 4045 lines**: The Python main server file is monolithic. Route handlers for workout generation, nutrition, day swapping, profile updates, and demo endpoints are all in one file instead of being split into the `app/routes/` modules.

3. **Demo/documentation endpoints in production**: Endpoints like `/data-health-analysis`, `/feature-pipeline-design`, `/multi-output-model-training`, `/evaluation-framework-demo` exist in `server.py` and serve documentation/demo content. These should be gated behind `NODE_ENV !== 'production'`.

4. **Synthetic training data**: `MultiOutputXGBoostModel._create_synthetic_data()` generates random training data. The comment says "In production, this would be replaced with real user workout history." The shipped `xgb_workout.pkl` model may be trained on synthetic data.

5. **Large page components**: `Dashboard.jsx` (162KB), `Workout.jsx` (165KB), `Nutrition.jsx` (84KB) are very large single-file components that would benefit from decomposition.

6. **Redis integration partial**: Redis and Celery are listed in requirements but Redis connection is optional. No Celery workers or task definitions were found in active use.

7. **Cross-site cookie complexity**: Auth cookie uses `sameSite: 'none'` in production with `secure: true`, plus a localStorage `x-auth-token` fallback for "cross-site deployments (e.g., Render)". This dual approach adds complexity.

8. **Model integrity in dev**: `SEC-10` model integrity checking logs warnings but doesn't block startup when checksums are missing (only strict in production).

---

## 11. TESTING

### Test Coverage

**Python Backend** (23 test files in `backend-python/tests/`):

| Test File | What It Tests |
|---|---|
| `test_engine.py` | Core workout engine |
| `test_workout_e2e_flow.py` | End-to-end workout generation (13KB) |
| `test_workout_planner_comprehensive.py` | Comprehensive planner tests (19KB) |
| `test_workout_progression_regression.py` | Progression regression tests |
| `test_pose_tracker_refactored.py` | Pose tracker: detector selection, rep counting, confidence, form scores |
| `test_chatbot_refactored.py` | Chatbot: helper functions, consent, circuit breaker, rate limiting |
| `test_chatbot_sanity_flow.py` | Chatbot end-to-end sanity |
| `test_safety_compliance.py` | Safety layer: condition detection, nutrition adjustments, exercise filtering, senior adjustments, injury blocking |
| `test_golden_profiles.py` | Golden profile regression tests |
| `test_candidate_generator.py` | Exercise candidate generation |
| `test_candidate_health.py` | Candidate health checks |
| `test_meal_scorer.py` | Meal scoring logic |
| `test_nutrition_engine_comprehensive.py` | Nutrition engine tests |
| `test_portion_optimizer.py` | Portion optimization |
| `test_variety_tracker.py` | Food variety tracking |
| `test_template_manager.py` | Workout template management |
| `test_token_utils.py` | JWT token utilities |
| `test_health_endpoint.py` | Health endpoint |
| `test_metadata_serialization.py` | Metadata serialization |
| `test_profile_meal_regen.py` | Profile change → meal regeneration |
| `test_python_api_contract.py` | Verifies all expected API routes exist in source |
| `run_regression.py` | Regression test runner |
| `verify_v6_stabilization.py` | v6 stabilization verification |

**Node Backend** (2 test files in `backend-node/tests/`):

| Test File | What It Tests |
|---|---|
| `auth.middleware.test.js` | Auth middleware: valid/invalid/missing tokens, suspension check |
| `pythonProxy.test.js` | Python proxy: route normalization, header forwarding, error handling |

**Frontend** (4 test files in `frontend/src/__tests__/`):

| Test File | What It Tests |
|---|---|
| `ConfirmDialog.test.jsx` | Confirm dialog rendering and interactions |
| `poseRouting.test.js` | Pose movement pattern routing |
| `storage.test.js` | Storage utility functions |
| `circuitBreaker.test.js` | Circuit breaker state transitions |

### What's NOT Tested

- No integration tests that run all three services together.
- No end-to-end browser tests (Playwright/Cypress).
- Frontend page components (Dashboard, Workout, Nutrition) have no unit tests.
- Admin panel routes have no dedicated test files.
- Meal swap and day swap logic has no dedicated test in Node backend.

### How to Run Tests

```bash
# Frontend
cd frontend
npm run test:unit          # Vitest
npm run test:coverage      # With coverage

# Node Backend
cd backend-node
npm run test:unit          # Jest

# Python Backend
cd backend-python
.\.venv\Scripts\activate
pytest tests/ -v --tb=short
```

---

## 12. GLOSSARY

| Term | Meaning |
|---|---|
| **Movement Pattern** | Classification of exercises into biomechanical categories (CURL, PRESS, SQUAT, HINGE, LUNGE, RAISE, CORE, CARDIO, CALF, GENERIC). Used for pose detection routing. |
| **ROM** | Range of Motion — the angular displacement of a joint during an exercise rep. |
| **EMA** | Exponential Moving Average — smoothing algorithm applied to landmark positions to reduce jitter. |
| **Hysteresis** | A threshold buffer to prevent state oscillation in the rep counting state machine. Entry hysteresis = 5°, exit = 8°. |
| **Check_Type** | Column in exercise dataset indicating the pose detection logic type (e.g., `squat_logic`, `curl_logic`). Used by safety layer to filter exercises for injuries. |
| **Safety Bounds** | Hard limits on ML predictions: sets (1-6), reps_low (1-20), reps_high (3-30), rest_time (30-300s), intensity (0.1-1.0). |
| **Circuit Breaker** | Pattern that stops calling a failing external service after N consecutive failures, auto-recovering after a timeout. |
| **Plan Cache** | Server-side cache of generated workout/nutrition plans keyed by user ID + ISO-week to avoid expensive regeneration. |
| **ISO Week** | The Monday-to-Sunday week number per ISO 8601. Plans are regenerated at week boundaries. |
| **Owner** | The single admin user role (enforced by unique partial index). Different from regular `user` role. |
| **Swap** | Converting a rest day to workout day (or vice versa) within a weekly plan. Limited to 3/week by default. |
| **PPL** | Push/Pull/Legs — a workout split pattern where training days are organized by movement type. |
| **Bro Split** | Workout pattern targeting one major muscle group per day (e.g., Chest Monday, Back Tuesday). |
| **Trend Entry** | A daily snapshot stored in the `trends` array on the User document, tracking workout/meal completion, macros, water, and sleep. |
| **Warming** | The brief period after the MediaPipe WASM model loads but before pose detection is fully responsive. A 3-second "warming" message is shown. |
| **Golden Profile** | A predefined test user profile used for regression testing to ensure consistent plan outputs. |
| **dynDown / dynUp** | Auto-calibrated rep counting thresholds that adapt to each user's observed range of motion after their first rep. |
| **IST** | Indian Standard Time (Asia/Kolkata) — the timezone used for week boundary calculations throughout the codebase. |
