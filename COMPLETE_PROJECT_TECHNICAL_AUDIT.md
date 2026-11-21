# COMPLETE CODEBASE ANALYSIS, DEEP CODE AUDIT & TECHNICAL REPORT

> **Project:** Elevate Fitness & Nutrition Intelligence Platform  
> **Auditors:** Senior Software Architect, Principal Security Auditor, Full-Stack Lead & QA Engineer (15+ Years Experience)  
> **Audit Date:** November 2026  
> **Audit Scope:** Exhaustive Codebase Coverage (287 Cataloged Files Across All Subsystems)  
> **Target Status:** Production Readiness Evaluation & Architecture Roadmap  
> **Analysis Methods:** Static AST Analysis, Line-by-Line Code Inspection, Automated Test Suite Execution (Vitest, Jest, Pytest), Production Build Verification, ESLint Auditing, and Microservice Execution Tracing.

---

## TABLE OF CONTENTS

1. [Executive Summary](#1-executive-summary)
2. [Project Overview](#2-project-overview)
3. [Technology Stack](#3-technology-stack)
4. [Complete Repository Structure](#4-complete-repository-structure)
5. [File-by-File Code-Level Analysis](#5-file-by-file-code-level-analysis)
   - [5.1 Primary Backend: Node.js / Express](#51-primary-backend-nodejs--express)
   - [5.2 AI & Machine Learning Microservice: Python / FastAPI](#52-ai--machine-learning-microservice-python--fastapi)
   - [5.3 Frontend Single Page Application: React 19 / Vite](#53-frontend-single-page-application-react-19--vite)
   - [5.4 Root Configuration, Shell Scripts & CI/CD](#54-root-configuration-shell-scripts--cicd)
6. [Application Architecture](#6-application-architecture)
7. [Comprehensive Architecture Diagrams (Mermaid)](#7-comprehensive-architecture-diagrams-mermaid)
8. [Frontend Deep Dive](#8-frontend-deep-dive)
9. [Backend Deep Dive](#9-backend-deep-dive)
10. [Database Architecture & Schema Analysis](#10-database-architecture--schema-analysis)
11. [API Specification & Endpoint Catalog](#11-api-specification--endpoint-catalog)
12. [Business Logic, Mathematical Formulas & ML Algorithms](#12-business-logic-mathematical-formulas--ml-algorithms)
13. [Complete Application Execution Flows](#13-complete-application-execution-flows)
14. [Identified Bugs and Vulnerability Ledger](#14-identified-bugs-and-vulnerability-ledger)
15. [Comprehensive Security Audit (OWASP Top 10)](#15-comprehensive-security-audit-owasp-top-10)
16. [Performance, Concurrency & Scalability Audit](#16-performance-concurrency--scalability-audit)
17. [Code Quality & SOLID / DRY Principles Assessment](#17-code-quality--solid--dry-principles-assessment)
18. [Project Strengths](#18-project-strengths)
19. [Project Weaknesses](#19-project-weaknesses)
20. [Missing Production Features & Gaps](#20-missing-production-features--gaps)
21. [Testing & Validation Verification Results](#21-testing--validation-verification-results)
22. [Technical Debt Analysis](#22-technical-debt-analysis)
23. [Recommended Architectural Refactoring](#23-recommended-architectural-refactoring)
24. [Priority-Based Engineering Action Plan](#24-priority-based-engineering-action-plan)
25. [Overall Project Evaluation & Executive Verdict](#25-overall-project-evaluation--executive-verdict)

---

## 1. EXECUTIVE SUMMARY

The **Elevate Fitness Platform** is an enterprise-scale full-stack application designed to deliver hyper-personalized physical training routines, adaptive nutritional planning, real-time computer vision pose estimation, and conversational AI coaching.

### Comprehensive Audit Verdict
- **Overall System Rating:** **6.7 / 10 (Production Remediation Required)**
- **Computer Vision & Client-Side Inference:** **9.0 / 10 (State-of-the-Art Client WASM)**
- **Machine Learning & Safety Engineering:** **8.5 / 10 (Strong Multi-Output XGBoost with Clamps)**
- **User Interface & Visual Experience:** **8.0 / 10 (Modern Aesthetic, High Responsiveness)**
- **Automated Testing Coverage:** **6.0 / 10 (Passing Unit Tests, Broken CI Quality Gates)**
- **System Architecture & Database Topology:** **5.5 / 10 (Critical Dual-Database Write Split-Brain)**
- **Security & Authorization Hygiene:** **5.0 / 10 (Non-Expiring Tokens, Suspension Bypass)**
- **Code Modularity & Maintainability:** **5.0 / 10 (Four 3,500+ Line Monoliths)**

### Key Positives
1. **Zero-Latency Client-Side Computer Vision:** Pose detection runs 100% locally in the browser using MediaPipe Vision compiled to WebAssembly (`@mediapipe/tasks-vision`). Video streams never leave the user's device, ensuring HIPAA/GDPR-aligned privacy and eliminating server GPU infrastructure costs.
2. **Correlated Parameter Regression via Multi-Output XGBoost:** The ML pipeline models the covariance between sets, reps, and rest intervals using Scikit-Learn's `MultiOutputRegressor`, avoiding the statistical independence errors of single-target regressors.
3. **Deterministic Physiological Safety Clamps:** Machine learning and LLM outputs are treated as untrusted proposals. All recommendations pass through hardcoded mathematical clamps that prevent overtraining, dangerous volume, or allergen exposure.
4. **Resilient Circuit Breaker Topology:** Independent frontend and backend circuit breakers (`workoutCB`, `nutritionCB`, `backgroundCB`, `gemini_cb`) isolate microservice failures and provide seamless fallback UI states.

### Critical Blockers to Production
1. **Perpetual Session Lifetime (Security P0):** User and Admin JWTs are issued without an `expiresIn` claim, and cookies carry a 100-year lifetime. Leaked credentials grant permanent account access (`BUG-SEC-01`, `BUG-SEC-02`).
2. **Bypassed Account Suspension (Security P0):** Authentication middleware trusts static boolean claims (`isSuspended: false`) in JWT payloads, allowing suspended users to access protected endpoints indefinitely (`BUG-SEC-03`).
3. **Dual-Database Write Split-Brain (Architecture P1):** Both Node.js (via Mongoose) and Python (via Motor) independently write to the same MongoDB `users` collection across 5 competing endpoints, causing race conditions and bypassing schema validations (`BUG-ARCH-01`).
4. **BSON Document Size Explosion (Data P1):** `user.activities` in MongoDB grows monotonically without array slicing, guaranteeing that active user documents will eventually breach the 16MB BSON limit and crash with `BSONObjectTooLarge` (`BUG-DAT-01`).
5. **CI Quality Gate Failure (DevOps P0):** Automated GitHub Actions CI fails on 8 ESLint `no-unused-vars` errors and 1 Python candidate health regression test (`BUG-CI-01`, `BUG-TST-01`).

---

## 2. PROJECT OVERVIEW

Elevate solves the adherence and personalization crisis in digital fitness by combining three core engineering pillars:
1. **Biometric & Goal Adaptation:** Calculating accurate Basal Metabolic Rate (BMR) and Total Daily Energy Expenditure (TDEE), followed by algorithmic macronutrient and workout split optimization.
2. **Real-Time Biomechanical Form Tracking:** Using WebAssembly pose landmark tracking to monitor exercise execution, calculate joint range of motion (ROM), count repetitions, and deliver instant corrective feedback.
3. **Conversational Fitness Intelligence:** Integrating Google Gemini LLMs to generate personalized workout commentary and natural-language meal advice, backed by in-memory semantic caching and offline fallback dictionaries.

### Microservice Topology
- **Tier 1 (Frontend):** React 19 SPA running on Vite (Port 5173).
- **Tier 2 (Gateway Backend):** Node.js Express 5 server (Port 5000), managing auth, cookies, rate limits, and MongoDB persistence.
- **Tier 3 (AI / ML Microservice):** Python FastAPI ASGI server (Port 8000), managing XGBoost inference, feature scaling, and heuristic plate composition.
- **Tier 4 (Persistence):** MongoDB 7.0+ document store.

---

## 3. TECHNOLOGY STACK

```
┌─────────────────────────────────────────────────────────────────────────┐
│                           TECHNOLOGY STACK                              │
├───────────────────┬───────────────────────────────┬─────────────────────┤
│ Subsystem         │ Framework / Library           │ Version / Tooling   │
├───────────────────┼───────────────────────────────┼─────────────────────┤
│ Frontend UI       │ React (JSX)                   │ 19.2.0              │
│ Frontend Tooling  │ Vite + Rollup                 │ 7.2.4               │
│ Computer Vision   │ MediaPipe Tasks Vision        │ 0.10.34 (WASM)      │
│ Routing           │ React Router DOM              │ 7.12.0              │
│ HTTP Client       │ Axios + Circuit Breakers      │ 1.13.2              │
│ Primary Backend   │ Node.js / Express             │ 5.2.1               │
│ Database ODM      │ Mongoose                      │ 9.1.5               │
│ Authentication    │ JSONWebToken + BcryptJS       │ 9.0.3 / 3.0.3       │
│ OAuth Identity    │ Google Auth Library           │ 10.5.0              │
│ CSRF Protection   │ csrf-csrf (Double Submit)     │ 3.2.2               │
│ Rate Limiting     │ express-rate-limit            │ 8.3.2               │
│ Validation        │ express-validator             │ 7.2.1               │
│ AI Microservice   │ Python / FastAPI (Uvicorn)    │ 3.11.8 / 0.115      │
│ Async Mongo       │ Motor (AsyncIOMotorClient)    │ 3.7.0               │
│ Machine Learning  │ XGBoost + Scikit-Learn        │ 3.1.2 / 1.8.0       │
│ Numerical Math    │ NumPy + Pandas                │ 2.2.3 / 2.3.3       │
│ LLM Provider      │ Google Generative AI (Gemini) │ 0.8.6               │
│ Testing - React   │ Vitest + Testing Library      │ 3.2.3 / 16.3.0      │
│ Testing - Node    │ Jest + Supertest              │ 29.7.0 / 7.1.0      │
│ Testing - Python  │ Pytest + AnyIO + Pytest-Async │ 9.1.0 / 4.13.0      │
│ CI / CD           │ GitHub Actions Workflows      │ Ubuntu Latest       │
└───────────────────┴───────────────────────────────┴─────────────────────┘
```

---

## 4. COMPLETE REPOSITORY STRUCTURE

The repository consists of **287 cataloged files** (excluding generated folders). The directory layout reflects the separation of concerns:

```
Elevate-fitness/
├── .github/
│   └── workflows/
│       └── quality-gates.yml              # CI/CD multi-job pipeline definition
├── .gitignore                             # Git exclusion configuration
├── package.json & package-lock.json       # Root package descriptor
├── start_all.bat                          # Multi-window development service orchestrator
├── start_node.bat                         # Node.js backend launcher
├── start_python.bat                       # Python FastAPI launcher
├── start_frontend.bat                     # Vite React frontend launcher
│
├── backend-node/                          # Primary Backend & API Gateway
│   ├── .env / .env.example                # Node.js environment configuration
│   ├── package.json / package-lock.json   # Node.js dependencies
│   ├── server.js                          # Express application entrypoint (407 lines)
│   ├── check_user_nutrition.js            # DB diagnostic inspection utility
│   ├── middleware/
│   │   ├── auth.js                        # JWT cookie auth & suspension middleware
│   │   ├── adminAuth.js                   # Owner role verification & audit logger
│   │   ├── adminRateLimit.js              # Rate limiters for auth & admin routes
│   │   └── validate.js                    # Express-validator input sanitizers
│   ├── models/
│   │   ├── User.js                        # Modular Mongoose User schema (151 lines)
│   │   ├── Exercise.js                    # Exercise catalog schema
│   │   ├── SystemConfig.js                # System settings & maintenance schema
│   │   └── AdminAuditLog.js               # Immutable administrative audit log
│   ├── routes/
│   │   ├── auth.js                        # Register, login, Google OAuth, reset (467 lines)
│   │   ├── profile.js                     # Profile updates, histories, trends (520 lines)
│   │   ├── pythonProxy.js                 # Authenticated reverse proxy to Python (295 lines)
│   │   ├── users.js                       # Legacy user endpoints & external proxies (499 lines)
│   │   ├── adminAuth.js                   # Admin login, logout, verification (294 lines)
│   │   ├── adminUsers.js                  # User administration, suspension (357 lines)
│   │   ├── adminSystem.js                 # System health, announcements, stats (355 lines)
│   │   └── adminContent.js                # Exercise library CRUD operations (196 lines)
│   ├── services/
│   │   └── securityNotificationService.js # SMTP & Webhook alert dispatcher (230 lines)
│   ├── utils/
│   │   └── mealUtils.js                   # Canonical date, macro, and meal helpers (111 lines)
│   ├── scripts/
│   │   └── seed.js                        # Database seeder for owner account
│   └── tests/
│       ├── auth.middleware.test.js        # Auth middleware unit tests (Jest)
│       └── pythonProxy.test.js            # Python proxy routing tests (Jest)
│
├── backend-python/                        # AI & ML Microservice
│   ├── Dockerfile & requirements.txt      # Container & Python dependency specs
│   ├── pytest.ini                         # Pytest configuration
│   ├── server.py                          # Master FastAPI monolith (4,077 lines)
│   ├── generate_meal_kb.py                # Food knowledge base compilation script
│   ├── train_workout.py                   # XGBoost workout model training pipeline
│   ├── app/
│   │   ├── db.py                          # Motor async MongoDB client (168 lines)
│   │   ├── workout_engine.py              # Master workout generator monolith (5,369 lines)
│   │   ├── gemini_service.py              # Google Gemini LLM wrapper (498 lines)
│   │   ├── multi_output_xgboost_model.py  # MultiOutputRegressor wrapper (480 lines)
│   │   ├── multitarget_nutrition_model.py # Nutrition XGBoost regressor (550 lines)
│   │   ├── feature_pipeline.py            # Feature preprocessor & encoders (450 lines)
│   │   ├── hybrid_volume_optimizer.py     # Volume & recovery balancer (380 lines)
│   │   ├── adaptive_modifier.py           # Sleep/fatigue workout adjuster (190 lines)
│   │   ├── biometric_normalizer.py        # BMR/TDEE normalization (85 lines)
│   │   ├── workout_rules.py               # Workout split rules loader (120 lines)
│   │   ├── circuit_breaker.py             # Python circuit breaker pattern (140 lines)
│   │   ├── semantic_cache.py              # In-memory inference cache (110 lines)
│   │   ├── rag_pipeline.py                # Context retrieval pipeline (210 lines)
│   │   ├── session_manager.py             # Conversational session manager (160 lines)
│   │   ├── deterministic_meal_engine.py   # Meal Engine V2 (1,467 lines)
│   │   ├── meal_engine.py                 # MealEngine V6 wrapper (827 lines)
│   │   ├── config/
│   │   │   ├── exercise_mapping.json      # 1,300+ exercise taxonomy
│   │   │   └── movement_rules.json        # Physiological movement safety rules
│   │   ├── core/
│   │   │   ├── auth.py                    # PyJWT token decoding helper
│   │   │   └── responses.py               # Standardized JSON response envelope
│   │   ├── detectors/                     # Computer Vision Exercise Counters
│   │   │   ├── base_detector.py           # Abstract BaseDetector with angle math
│   │   │   ├── curl_detector.py           # Bicep curl rep counter (asymmetric left)
│   │   │   ├── squat_detector.py          # Squat depth & knee valgus tracker
│   │   │   ├── push_detector.py           # Pushup elbow & trunk tracker
│   │   │   ├── plank_detector.py          # Plank alignment & hold timer
│   │   │   ├── lunge_detector.py          # Lunge knee flexion tracker
│   │   │   ├── hinge_detector.py          # Deadlift hip hinge tracker
│   │   │   ├── pull_detector.py           # Pullup/row elbow tracker
│   │   │   ├── raise_detector.py          # Lateral raise abduction tracker
│   │   │   ├── generic_detector.py        # Generic cadence tracker
│   │   │   └── detector_factory.py        # Factory pattern detector resolver
│   │   ├── nutrition_engine/              # Nutrition Engine V6 Architecture
│   │   │   ├── engine.py                  # NutritionEngineV6 orchestrator (300 lines)
│   │   │   ├── candidate_generator.py     # Balanced meal plate candidate builder (1,800 lines)
│   │   │   ├── weekly_optimizer.py        # Weekly plan heuristic solver (950 lines)
│   │   │   ├── food_graph.py              # Food relationship & similarity graph (680 lines)
│   │   │   ├── portion_optimizer.py       # Exact macro gram portion solver (520 lines)
│   │   │   ├── meal_scorer.py             # Weighted multi-factor meal evaluator (410 lines)
│   │   │   ├── variety_tracker.py         # Monotony penalty tracker (320 lines)
│   │   │   ├── serving_validator.py       # Portion bound & starvation checker (280 lines)
│   │   │   ├── nutrition_calculator.py    # Weekly macro target planner (210 lines)
│   │   │   ├── template_manager.py        # YAML meal template loader (110 lines)
│   │   │   ├── food_utils.py              # Food family classification utilities (160 lines)
│   │   │   └── weekly_validator.py        # Plan variance & adherence validator (390 lines)
│   │   ├── routes/                        # Modular FastAPI Router Architecture
│   │   │   ├── profile.py                 # Profile update & plan regeneration (809 lines)
│   │   │   ├── chatbot.py                 # AI chatbot endpoint (150 lines)
│   │   │   ├── food_database.py           # Food catalog query routes (180 lines)
│   │   │   ├── meal_plan.py               # Meal plan generation routes (240 lines)
│   │   │   ├── meal_tracking.py           # Daily meal progress tracking (220 lines)
│   │   │   └── workout.py                 # Unmigrated router stub (50 lines)
│   │   └── models/                        # Serialized ML Models & Schemas
│   │       ├── user.py                    # User Pydantic schema
│   │       ├── xgb_workout.pkl            # Trained XGBoost workout model (655 KB)
│   │       ├── xgb_meal.pkl               # Trained XGBoost nutrition model (81 KB)
│   │       ├── le_gender.pkl              # Scikit-Learn gender LabelEncoder
│   │       ├── le_goal.pkl                # Scikit-Learn goal LabelEncoder
│   │       ├── le_target.pkl              # Scikit-Learn target LabelEncoder
│   │       └── checksums.sha256           # Model SHA256 integrity manifest
│   ├── data/                              # Static Data Stores & Datasets
│   │   ├── ingredient_database.json       # 800+ raw ingredient nutritional entries
│   │   ├── recipe_database.json           # 500+ cooked recipe blueprints
│   │   ├── food_relationship_graph.json   # Graph nodes linking substitute foods
│   │   └── nutrition_production_final_v4.csv # 1,300+ validated food macro rows
│   └── tests/                             # 24 Pytest Test Suites
│
├── frontend/                              # React 19 Single Page Application
│   ├── index.html & vite.config.js        # HTML shell & Vite bundler config
│   ├── package.json & package-lock.json   # Frontend dependency manifests
│   ├── eslint.config.js                   # ESLint flat configuration
│   ├── nginx.conf & Dockerfile            # Container deployment configuration
│   ├── public/
│   │   ├── sw.js                          # Service Worker for offline asset caching
│   │   └── wasm/                          # MediaPipe Vision WebAssembly Binaries
│   │       ├── vision_wasm_internal.wasm          # 11.5 MB SIMD WASM binary
│   │       ├── vision_wasm_internal.js            # 323 KB WASM loader
│   │       ├── vision_wasm_nosimd_internal.wasm   # 10.7 MB No-SIMD fallback binary
│   │       └── vision_wasm_nosimd_internal.js     # 323 KB No-SIMD loader
│   └── src/
│       ├── main.jsx                       # React DOM root mounting
│       ├── App.jsx                        # Route definitions & protected route guards
│       ├── api.js                         # Centralized Axios client & circuit breakers (673 lines)
│       ├── App.css, index.css, responsive.css # Design system stylesheets
│       ├── components/
│       │   ├── Navbar.jsx                 # Global header, user menu, navigation
│       │   ├── PoseDetector.jsx           # MediaPipe WASM client-side tracking (1,007 lines)
│       │   ├── AuroraBackground.jsx       # Canvas-based animated background
│       │   ├── ConfirmDialog.jsx          # Reusable action confirmation modal
│       │   ├── TimerExerciseMode.jsx      # Isometric & interval hold timer
│       │   ├── NotificationProvider.jsx   # Toast notification context & renderer
│       │   └── admin/
│       │       ├── AdminLayout.jsx        # Admin portal shell & navigation sidebar
│       │       ├── AdminRoute.jsx         # Owner-only route authorization guard
│       │       └── AdminActionDialog.jsx  # Admin confirmation modal
│       ├── context/
│       │   └── ThemeContext.jsx           # Light / Dark mode theme provider
│       ├── data/
│       │   └── quotes.js                  # Fitness quotes dataset
│       ├── pages/
│       │   ├── Dashboard.jsx              # Main user dashboard monolith (3,748 lines)
│       │   ├── DashboardActionIdeas.jsx   # Habit cards & motivational suggestions (1,200 lines)
│       │   ├── Workout.jsx                # Workout session player monolith (3,575 lines)
│       │   ├── Nutrition.jsx              # Meal tracker & plan display monolith (1,562 lines)
│       │   ├── ProfileSetup.jsx           # Multi-step profile form monolith (1,110 lines)
│       │   ├── Chatbot.jsx                # AI fitness coach chat interface (650 lines)
│       │   ├── Login.jsx                  # Email/password & Google login view
│       │   ├── Register.jsx               # Registration view with strength meter
│       │   ├── ForgotPassword.jsx         # Self-service password reset view
│       │   └── admin/
│       │       ├── AdminLogin.jsx         # Admin login with secret key field
│       │       ├── Dashboard.jsx          # Admin KPI metrics & system overview
│       │       ├── Users.jsx              # User administration & suspension table
│       │       ├── System.jsx             # Maintenance mode & announcements
│       │       ├── Content.jsx            # Exercise library CRUD panel
│       │       └── Audit.jsx              # Immutable audit log viewer
│       ├── services/
│       │   └── profileApi.js              # Profile update client with retry logic
│       ├── utils/
│       │   ├── circuitBreaker.js          # Client-side circuit breaker state machine
│       │   ├── storage.js                 # Safe localStorage wrapper with validation
│       │   ├── syncBridge.js              # BroadcastChannel multi-tab synchronizer
│       │   ├── googleAuth.js              # Google Identity Services credential loader
│       │   └── poseModelPreload.js        # MediaPipe model preloader
│       └── __tests__/                     # Vitest Test Suites
│           ├── ConfirmDialog.test.jsx
│           ├── poseRouting.test.js
│           ├── storage.test.js
│           └── setup.js
│
└── docs/                                 # Architectural Documentation & Project Reports
    ├── api_contract.md                    # Backend API contract specification
    ├── architecture.md                    # High-level architecture documentation
    ├── incident_runbook.md                # Production incident triage guide
    └── monitoring_dashboard.md            # Observability & telemetry spec
```


---

## 5. FILE-BY-FILE CODE-LEVEL ANALYSIS

This section delivers an exhaustive, code-level review of the key source files across each subsystem.

---

### 5.1 Primary Backend: Node.js / Express

#### `backend-node/server.js` (407 Lines)
- **Role & Purpose:** Master entrypoint for the primary backend. Responsible for initializing the Express application, verifying required environment variables, establishing the MongoDB connection with retry diagnostics, enforcing security headers, configuring double-submit CSRF cookie validation, managing in-memory maintenance mode caching, mounting routes, and orchestrating graceful shutdown.
- **Key Functions & Logic:**
  - `isPlaceholderSecret(value)`: Inspects incoming secret keys for default strings like `"change-me"` or `"your-"`, halting boot if detected in non-test environments (`SEC-34`).
  - `connectWithRetry(attempt)`: Recursively attempts MongoDB connection up to 3 times with 5000ms delay, formatting helpful diagnostic guides on `ECONNREFUSED`.
  - `doubleCsrfProtection`: Configures the signed double-submit CSRF cookie pattern (`csrf-csrf`) using `psifi.x-csrf-token` with `HttpOnly` and `SameSite: Lax` (or `None` with `Secure` in production). Exempts authentication endpoints (`/api/auth/*`).
  - `Maintenance Middleware`: Employs an in-memory cache `_maintenanceCache` with a 30-second TTL to avoid a MongoDB query on every inbound non-admin request.
  - `gracefulShutdown(signal)`: Catches `SIGTERM` and `SIGINT`, arms a 10-second force-exit timer (`forceExit.unref()`), closes the HTTP server, and terminates the Mongoose connection cleanly.
- **Inputs & Outputs:** Inbound HTTP requests on port 5000; returns JSON responses with `x-request-id` header correlation.
- **Dependencies:** `express`, `mongoose`, `cors`, `cookie-parser`, `csrf-csrf`, `dotenv`, `crypto`.
- **Edge Cases & Vulnerabilities:**
  - `JSON Body Limit Split`: Allocates `PYTHON_JSON_LIMIT` (default 10MB) for `/api/python` routes, but restricts general routes to 100KB (`SEC-40`). Large profile update payloads sent to general routes could trigger HTTP 413 `PAYLOAD_TOO_LARGE`.

#### `backend-node/middleware/auth.js` (80 Lines)
- **Role & Purpose:** Validates inbound JSON Web Tokens to protect user-scoped endpoints.
- **Key Logic:**
  - Extracts the JWT from `req.cookies.elevate_token` first, falling back to `req.header('x-auth-token')` for cross-site deployment compatibility.
  - Calls `jwt.verify(token, process.env.JWT_SECRET)`.
  - Enforces account suspension via `req.user.isSuspended`.
- **Confirmed Critical Bug (`BUG-SEC-03`):**
  - Lines 52–70:
    ```javascript
    if (typeof req.user.isSuspended === 'boolean') {
        if (req.user.isSuspended) {
            return res.status(403).json({ message: 'Account is suspended. Please contact support.' });
        }
    } else {
        const user = await User.findById(req.user.id).select('isSuspended').lean();
        ...
    }
    ```
    When an active user logs in, their JWT is issued with `isSuspended: false`. When an administrator suspends the user in MongoDB, the database changes, but the user's existing JWT still carries `isSuspended: false`. Because `typeof req.user.isSuspended === 'boolean'` evaluates to `true`, the middleware skips the database check. Because the token never expires (`BUG-SEC-01`), the suspended user retains perpetual access.
- **Confirmed Bug:** Lines 27–44: Sliding session max age check is commented out, leaving tokens valid indefinitely.

#### `backend-node/middleware/adminAuth.js` (210 Lines)
- **Role & Purpose:** Enforces authorization for owner-level administrative routes and logs administrative audit events.
- **Key Functions & Logic:**
  - `extractClientIp(req)`: Normalizes client IP addresses. Safely ignores `x-forwarded-for` unless `TRUST_PROXY=1` is explicitly set, preventing IP spoofing against the admin whitelist (`SEC-5`).
  - `requireOwner(req, res, next)`: Verifies `elevate_admin_token` cookie against `ADMIN_JWT_SECRET`, checks `decoded.type === 'admin'`, queries MongoDB to verify `user.role === 'owner'`, and enforces temporary lockouts (`adminLockedUntil`).
  - `logAdminAction(action, targetType)`: Monkey-patches `res.json` to automatically write successful actions (HTTP 200–299) to `AdminAuditLog` with redacted payloads (`redactSensitive`).
  - `redactSensitive(payload)`: Recursively strips sensitive keys (`password`, `adminKey`, `resetToken`, etc.) before audit logging.
- **Strengths:** Strong defense-in-depth implementation. Tracks failed audit log writes (`_failedAuditCount`) to alert operators of audit loss via `[AUDIT_LOG_FAILURE]` log tags (`Bug #27`).

#### `backend-node/models/User.js` (151 Lines)
- **Role & Purpose:** Authoritative Mongoose schema for user accounts.
- **Key Logic & Sub-Schemas:**
  - `SecuritySchema`: Inlined access control fields (`isSuspended`, `role`, `mustChangePassword`, `passwordResetTokenHash`, `adminLockedUntil`, `adminLoginAttempts`).
  - `FitnessProfileSchema`: Inlined physical characteristics (`age`, `weight`, `height`, `goal`, `experience`, `equipment`, `allergies`, `body_issues`, `days_per_week`, `dietary_preference`).
  - `TrendEntrySchema`: Subdocument array schema for daily adherence tracking (`workout_completed`, `calories`, `protein`, `carbs`, `fat`, `water_glasses`, `sleep_hours`, `streak_days`).
  - Partial Unique Index:
    ```javascript
    UserSchema.index({ role: 1 }, { unique: true, partialFilterExpression: { role: 'owner' } });
    ```
    Guarantees at the database engine level that only one owner account can ever exist.
- **Concerns:**
  - `workouts`, `meals`, and `activities` arrays use `Schema.Types.Mixed`, bypassing Mongoose schema type checks and enabling arbitrary subdocument injection.

#### `backend-node/routes/auth.js` (467 Lines)
- **Role & Purpose:** Manages user registration, login, Google OAuth authentication, session probing, and self-service password recovery.
- **Key Functions & Logic:**
  - `POST /register`: Validates name/email/password lengths (`Bug #44` DoS mitigation), hashes password via `bcrypt.hash(password, 12)`, determines registration day of week (`firstWorkoutDay`), saves user, sets `elevate_token` cookie, and returns sanitized profile.
  - `POST /login`: Validates credentials, checks `user.isSuspended` and `user.mustChangePassword`, compares password hash, sets auth cookie.
  - `POST /google`: Verifies Google OAuth JWT via `google-auth-library` (`client.verifyIdToken`), creates user if new (hashing random 32-byte crypto token as password to prevent password login without OAuth), or updates avatar if existing.
  - `POST /reset-password/request`: Generates 32-byte crypto token, stores salted Bcrypt hash with 15-minute expiration, and dispatches token via `sendPasswordResetToken`.
- **Confirmed Critical Bug (`BUG-SEC-01`):**
  - Line 27: `jwt.sign({ user: { id, isSuspended } }, process.env.JWT_SECRET)` omits `{ expiresIn }`.
  - Line 47: Auth cookie sets `maxAge: 100 * 365 * 24 * 60 * 60 * 1000` (100 years).

#### `backend-node/routes/adminAuth.js` (294 Lines)
- **Role & Purpose:** Dedicated administrative authentication gateway with multi-credential verification and brute-force protection.
- **Key Functions & Logic:**
  - `verifyAdminKey(providedKey)`: Compares provided admin key against `ADMIN_SECRET_KEY_HASH` using `bcrypt.compare`, or timing-safe buffer comparison against `ADMIN_SECRET_KEY` in development.
  - `POST /login`: Enforces 3 credentials (Email, Password, Admin Key). On failure, increments `adminLoginAttempts`; at 5 failures, sets `adminLockedUntil` for 30 minutes, writes an audit record, and triggers security notification alerts via email/webhook.
- **Confirmed Critical Bug (`BUG-SEC-02`):**
  - Lines 192–211: `tokenExpiry = process.env.ADMIN_SESSION_EXPIRY || '2h'` is retrieved and returned in the JSON body, but is NEVER passed to `jwt.sign()`. Admin tokens live indefinitely.

#### `backend-node/routes/profile.js` (520 Lines)
- **Role & Purpose:** Manages user profile updates, workout history logs, meal histories, trends, and real-time activity feeds.
- **Key Functions & Logic:**
  - `POST /update`: Compares incoming profile against current user document. If plan-affecting fields (`goal`, `experience`, `equipment`, etc.) changed, flags `workout_regeneration_needed: true`. Filters input through strict field whitelist (`allowedFields`).
  - `POST /workout-history`: Uses atomic `$push` with `$position: 0` and `$slice: 50` to log workouts and activities atomically.
  - `POST /trends`: Uses two-phase atomic update: tries `findOneAndUpdate({ 'trends.date': date })` with dynamic `$set` fields; if no match, pushes new trend entry with `$slice: 180`.
- **Confirmed High-Priority Bug (`BUG-DAT-01`):**
  - Lines 458 and 493: `/activities/sync` and `/activities/log` call `user.activities.push(activity); await user.save();` without `$slice`. `user.activities` grows monotonically, threatening the 16MB BSON document limit.
- **Confirmed Medium-Priority Bug (`BUG-SEC-04`):**
  - Lines 395–400: Dynamic property assignment onto `trends.$.${key}` without property whitelisting.

#### `backend-node/routes/pythonProxy.js` (295 Lines)
- **Role & Purpose:** Authenticated reverse proxy gateway forwarding frontend requests to the Python microservice.
- **Key Functions & Logic:**
  - `normalizePythonPath(path)`: Maps client paths to upstream FastAPI endpoints (e.g. `/weekly-plan` → `/api/weekly-plan`, `/swap-meal` → `/nutrition/swap`).
  - `buildForwardHeaders(req)`: Derives Bearer authorization token from cookie or header and passes incoming `x-request-id`.
  - Retry Loop: Chat requests use 1 attempt with a 40s timeout. Plan generation routes in production retry up to 3 times with 3.5s backoff if upstream returns 502/503/504 or HTML (cold-start recovery).
  - Validation: Validates that upstream returned valid JSON; maps upstream 422 errors into safe sanitized error details.

#### `backend-node/utils/mealUtils.js` (111 Lines)
- **Role & Purpose:** Shared utility library for meal calculations and date parsing.
- **Key Functions:**
  - `toDateKey(date)`: Normalizes dates to `YYYY-MM-DD`.
  - `inferMealType(name, explicit)`: Classifies meal slots by keyword regex.
  - `computeTotals(items)`: Accumulates calories, protein, carbs, and fat.
- **Confirmed Bug (`BUG-DAT-02`):**
  - Line 22: Hardcodes `+ 330 * 60 * 1000` (IST offset), corrupting dates for users outside India.

---

### 5.2 AI & Machine Learning Microservice: Python / FastAPI

#### `backend-python/server.py` (4,077 Lines)
- **Role & Purpose:** Primary FastAPI application file. Hosts endpoints for ML inference, weekly plan caching, workout generation, meal plan generation, daily log tracking, and administrative system demos.
- **Key Endpoints & Logic:**
  - `@app.post("/workout")`: Core workout generator. Validates user input through `WorkoutProfileRequest`, builds deterministic cache key, queries in-memory plan cache, and executes `workout_engine.generate_weekly_plan()`.
  - `@app.post("/nutrition")`: Core meal generator. Normalizes intensity, derives daily macro targets, and invokes `meal_engine.generate_meal_plan()`.
  - `@app.get("/api/weekly-plan")`: Returns cached or freshly generated weekly plan.
  - `@app.post("/nutrition/swap")`: Evaluates role-compatible food substitutions matching target calories within ±15%.
  - `@app.put("/profile/update-safe")`: Safe profile updater with graceful degradation. Directly updates MongoDB `users` collection via Motor.
- **Architecture Flaw (`BUG-ARCH-01`):**
  - Direct database writes from Python bypass Node Mongoose schemas and create split-brain race conditions.
- **Code Quality Concern:**
  - Massive 4,077-line monolith containing endpoints that should be distributed into `app/routes/`.

#### `backend-python/app/workout_engine.py` (5,369 Lines)
- **Role & Purpose:** Master workout generation engine. Combines XGBoost regression, rule-based exercise selection, physiological safety volume clamping, progression tracking, and WGER media enrichment.
- **Key Logic & Architecture:**
  - `FeaturePipeline`: Transforms user age, gender, weight, experience, and goal into scaled numerical arrays using `StandardScaler` and `LabelEncoder`.
  - `MultiOutputXGBoostModel`: Predicts continuous targets: `[sets, reps, rest_seconds, intensity, volume]`.
  - `WorkoutRules`: Clamps predicted sets between 1 and 6, bounds rest between 30s and 180s, filters out exercises targeting injured joints specified in `body_issues`.
  - `generate_weekly_plan(profile, workout_history)`: Assembles 7-day routine honoring requested `days_per_week` and split preferences (Full Body, PPL, Upper/Lower, Bro Split).
- **Code Quality Concern:**
  - At 5,369 lines, this single file handles ML inference, rule parsing, split generation, progression math, and HTTP media scraping. Requires urgent modular decomposition.

#### `backend-python/app/gemini_service.py` (498 Lines)
- **Role & Purpose:** Google Gemini LLM integration service. Delivers natural-language workout commentary and fitness coaching chat.
- **Key Functions & Logic:**
  - `_get_model()`: Lazily initializes the model with candidate fallback resolution across `['gemini-flash-lite-latest', 'gemini-3.5-flash-lite', 'gemini-3.8-flash']`. Validates active connection with a fast 8s probe.
  - `generate_workout_config(profile, intensity)`: Queries Gemini for JSON workout parameters, wrapped inside `gemini_cb` circuit breaker.
  - `_get_fallback_response(message)`: Keyword-matching offline fallback dictionary serving expert responses on greetings, workouts, nutrition, recovery, form, and motivation when API quota is exhausted.
- **Deprecation Warning (`BUG-DEP-01`):**
  - Line 6 imports deprecated `google.generativeai` package, requiring migration to `google.genai`.

#### `backend-python/app/nutrition_engine/engine.py` (300 Lines) & Sub-modules
- **Role & Purpose:** Production Nutrition Engine V6 implementing complete dietary planning.
- **Key Sub-modules:**
  - `candidate_generator.py` (1,800 lines): Draws ingredients and recipes from knowledge base, checks dietary/allergy compliance, and constructs balanced plate candidates.
  - `weekly_optimizer.py` (950 lines): Balances macros and variety across 7 days.
  - `food_graph.py` (680 lines): Graph-based similarity engine mapping interchangeable foods.
  - `portion_optimizer.py` (520 lines): Solves exact ingredient gram portions to meet calorie targets.
  - `variety_tracker.py` (320 lines): Tracks meal and protein frequency to prevent monotony.
- **Test Failure (`BUG-TST-01`):**
  - Fallback meal generation rate exceeds 5% threshold under edge-case restrictive profiles.

#### `backend-python/app/detectors/curl_detector.py` (78 Lines)
- **Role & Purpose:** Evaluates bicep curl form and counts repetitions from MediaPipe landmark arrays.
- **Key Logic:**
  - Calculates elbow angle between shoulder, elbow, and wrist.
  - State machine transitions from `down` (>150°) to `up` (<45°) and back, verifying minimum Range of Motion (ROM ≥ 90°).
  - Checks shoulder angle to detect and penalize arm swinging.
- **Confirmed Defect (`BUG-CV-01`):**
  - Lines 14–21: Extracts only `l_shoulder`, `l_elbow`, `l_wrist`. Completely fails if the user curls with their right arm or faces the camera sideways.

---

### 5.3 Frontend Single Page Application: React 19 / Vite

#### `frontend/src/api.js` (673 Lines)
- **Role & Purpose:** Centralized HTTP client managing API communication with Node.js and Python.
- **Key Logic:**
  - Configures `AuthAPI` (port 5000) and `FitnessAPI` (via Node `/api/python` proxy).
  - Interceptors fetch and attach `x-csrf-token` header for all state-mutating requests (`POST`, `PUT`, `DELETE`).
  - Request slimmer functions (`_pickWorkoutProfile`, `_pickNutritionPayload`) strip unnecessary frontend state before network dispatch.
  - Exports circuit breaker instances (`workoutCB`, `nutritionCB`, `backgroundCB`) for UI component monitoring.
- **Confirmed Bug (`BUG-API-01`):**
  - Line 284: `export const updateProfileAndRegenerateWorkouts = (data) => FitnessAPI.put('/profile/update', data)` targets a non-existent endpoint, returning 404.

#### `frontend/src/components/PoseDetector.jsx` (1,007 Lines)
- **Role & Purpose:** Client-side real-time exercise pose tracking component.
- **Key Logic:**
  - Loads MediaPipe Vision WebAssembly from `public/wasm/` using `FilesetResolver.forVisionTasks()`.
  - Instantiates `PoseLandmarker` with local model assets (`poseModelPreload.js`).
  - Processes camera stream on `requestAnimationFrame` loop.
  - Computes 3D vector joint angles via dot product and arccosine (`calcAngle`).
  - Applies Exponential Moving Average smoothing (`emaSmooth`) with exercise-specific alpha coefficients (0.40 for fast curls, 0.22 for slow squats).
  - Renders skeleton lines and joint confidence circles on overlay canvas.
  - Triggers synthesized audio feedback via Web Audio API upon rep completion.
- **ESLint Error (`BUG-CI-01`):**
  - Line 113: `_pattern` parameter is unused, failing CI linter.

#### `frontend/src/pages/Dashboard.jsx` (3,748 Lines)
- **Role & Purpose:** Central user dashboard rendering daily habits, weekly workout schedules, nutrition macro rings, trend charts, and motivational feeds.
- **Key Logic:**
  - Derives daily recovery scores using sleep duration, water intake, and recent workout intensity.
  - Synchronizes habit check-offs across browser tabs via `syncBridge.js` (`BroadcastChannel`).
  - Integrates `ConfirmDialog` for schedule swap undo operations.
- **ESLint Errors (`BUG-CI-01`):**
  - Lines 6, 7, 2100, 2113: Unused imports (`getWeeklyWorkoutPlan`, `generateNutritionPlan`, `backgroundCB`, `withCircuitBreaker`) and unused handlers (`handleSleepAdd`, `handleSleepRemove`).
- **Code Quality Concern:**
  - Giant 3,748-line file with dozens of interdependent `useState` hooks. Every habit toggle re-renders thousands of lines of JSX.

#### `frontend/src/pages/Workout.jsx` (3,575 Lines)
- **Role & Purpose:** Interactive live workout execution interface.
- **Key Logic:**
  - Manages exercise sequence progression, sets, reps, and rest timers.
  - Mounts `<PoseDetector />` during active tracking sets, receiving live rep and form score callbacks.
  - Logs completed workout payload to `/api/profile/workout-history`.
- **ESLint Error (`BUG-CI-01`):**
  - Line 323: `error` variable in catch block is defined but unused.

---

### 5.4 Root Configuration, Shell Scripts & CI/CD

#### `.github/workflows/quality-gates.yml` (132 Lines)
- **Role & Purpose:** Automated GitHub Actions multi-stage CI/CD pipeline triggered on all branch pushes and pull requests.
- **Jobs Executed:**
  1. `frontend-quality`: `npm ci`, `npm run lint`, `npm run build`, `npm run test:unit` (Vitest), `npm run test:coverage`, `npm audit --production`.
  2. `backend-node-quality`: `npm ci`, `npm run test:unit` (Jest), `npm audit --production`.
  3. `backend-python-quality`: Python 3.11 setup, `ruff check`, `ruff format --check`, `py_compile` across all Python files, `pytest tests/`, `pip-audit`.
  4. `secret-scan`: Gitleaks full commit history secret scanning.
- **Current Status:**
  - Pipeline fails on Job 1 (`frontend-quality`) due to 8 ESLint errors (`BUG-CI-01`).
  - Pipeline fails on Job 3 (`backend-python-quality`) due to `test_candidate_health.py` failure (`BUG-TST-01`).

#### `start_all.bat` (36 Lines)
- **Role & Purpose:** Developer productivity script launching Node.js backend (port 5000), Python backend (port 8000), and React frontend (port 5173) in separate command windows with staggered timeouts.


---

## 6. APPLICATION ARCHITECTURE

Elevate employs a distributed microservice topology with clear separation between user I/O, persistence, and compute-heavy intelligence:

```
┌────────────────────────────────────────────────────────────────────────┐
│                        ELEVATE SYSTEM TOPOLOGY                         │
└────────────────────────────────────────────────────────────────────────┘

  [ Client Browser: React 19 SPA ]
        │  │
        │  └────── Local Camera Feed ───► [ MediaPipe WASM (60 FPS) ]
        │                                 (Client-side Form & Rep Math)
        │
        │ (HTTP + HttpOnly Cookies + CSRF Header)
        ▼
  [ Node.js API Gateway (Port 5000) ]
        │  │  │
        │  │  ├─► [ MongoDB (users, exercises, configs, audit_logs) ]
        │  │  │
        │  │  └─► [ Google OAuth Verification ]
        │  │
        │  ▼ (Reverse Proxy with Bearer Token & Request-ID)
  [ Python FastAPI Microservice (Port 8000) ]
        │  │  │
        │  │  ├─► [ XGBoost Multi-Output Regressor ]
        │  │  ├─► [ Physiological Safety Clamps (Rules V2) ]
        │  │  ├─► [ Nutrition Engine V6 (Graph & Portion Solvers) ]
        │  │  └─► [ Google Gemini LLM API (Chat Coaching) ]
        │  │
        └──┴────► [ Direct Motor DB Writes (CRITICAL ANTI-PATTERN) ]
```

### Architectural Decisions: Evaluation
- **Positive Decisions:**
  - Running computer vision locally via WebAssembly prevents immense cloud video bandwidth costs and ensures strict privacy.
  - Multi-output regression models preserve the physiological correlations between sets, reps, and rest periods.
  - Using signed double-submit CSRF cookies (`csrf-csrf`) provides robust CSRF protection for single-page applications without heavy server-side session stores.
- **Flawed Decisions:**
  - Allowing Python to write directly to MongoDB (`BUG-ARCH-01`) creates a dual-writer split-brain architecture.
  - Storing static `isSuspended` claims in non-expiring JWTs creates an irrevocable authorization bypass (`BUG-SEC-03`).
  - Embedding unevicted `activities` arrays into user documents risks exceeding the 16MB MongoDB limit (`BUG-DAT-01`).

---

## 7. COMPREHENSIVE ARCHITECTURE DIAGRAMS (MERMAID)

### Diagram 1: Full System Data Flow & Microservice Interaction

```mermaid
flowchart TD
    subgraph Client_Browser ["Client Tier (Browser)"]
        UI["React 19 SPA"]
        WASM["MediaPipe WASM Engine"]
        Storage["Safe LocalStorage & SyncBridge"]
        CB["Client Circuit Breakers"]
    end

    subgraph Primary_Gateway ["Gateway Tier (Node.js Express)"]
        Router["Express Router & Proxy"]
        AuthMid["Auth & CSRF Middleware"]
        AdminMid["Admin Auth & Audit Logger"]
        RateLim["Rate Limiters"]
    end

    subgraph Compute_Tier ["Compute Tier (Python FastAPI)"]
        ML["XGBoost MultiOutput Regressor"]
        Guard["Physiological Safety Clamps"]
        Nutri["Nutrition Engine V6"]
        LLM["Google Gemini Service"]
    end

    subgraph Data_Tier ["Persistence Tier (MongoDB)"]
        DB[("MongoDB 7.0+")]
    end

    UI -->|"Video Frames"| WASM
    WASM -->|"Reps / Form Scores"| UI
    UI <-->|"Cache / Tabs"| Storage
    UI -->|"State Machine Guard"| CB
    CB -->|"API Requests"| Router

    Router --> RateLim --> AuthMid
    AuthMid -->|"CRUD Queries"| DB
    AuthMid -->|"Authenticated Forward"| Compute_Tier

    Compute_Tier --> ML --> Guard
    Compute_Tier --> Nutri
    Compute_Tier --> LLM
    Compute_Tier -.->|"Direct Writes (Anti-Pattern)"| DB
```

### Diagram 2: Sequence Flow: User Registration & Onboarding Plan Generation

```mermaid
sequenceDiagram
    autonumber
    actor User
    participant Frontend as React Frontend
    participant Node as Node.js Gateway
    participant Mongo as MongoDB
    participant Python as Python AI Service

    User->>Frontend: Enters Registration Credentials
    Frontend->>Node: POST /api/auth/register (name, email, password)
    Node->>Node: Bcrypt Hash Password (Cost 12)
    Node->>Mongo: Insert User Document (firstWorkoutDay, registrationDate)
    Node-->>Frontend: Set-Cookie: elevate_token (HttpOnly) + User Profile JSON
    User->>Frontend: Completes Fitness Profile (Age, Weight, Goal, Equipment)
    Frontend->>Node: POST /api/profile/update (Profile Parameters)
    Node->>Mongo: Update User Profile Fields
    Node-->>Frontend: Profile Updated (workout_regeneration_needed: true)
    Frontend->>Node: POST /api/python/workout (Forward Request)
    Node->>Node: Validate JWT & Attach x-request-id
    Node->>Python: POST /workout (Biometric Data)
    Python->>Python: FeaturePipeline -> MultiOutputXGBoost
    Python->>Python: Apply Safety Clamps (Max Sets, ROM, Volume)
    Python-->>Node: 200 OK (Weekly Plan JSON)
    Node-->>Frontend: 200 OK (Weekly Plan JSON)
    Frontend->>Frontend: Cache in LocalStorage & Render Dashboard
    Frontend->>User: Displays Personalized 7-Day Workout Routine
```

### Diagram 3: State Machine: Client-Side Exercise Rep Counting

```mermaid
stateDiagram-v2
    [*] --> Idle
    Idle --> Initializing : User Clicks 'Start Workout'
    Initializing --> Tracking : MediaPipe WASM Loaded & Camera Active
    
    Tracking --> Extended_Down : Joint Visible (Angle > 150°)
    Extended_Down --> Flexed_Up : Joint Contracting (Angle < 45°)
    Flexed_Up --> Extended_Down : Joint Extending (Angle > 150°)
    
    note right of Extended_Down
        Evaluate Range of Motion (ROM >= 90°)
        If valid: Increment Rep Counter
        Play Web Audio Success Beep
    end note
    
    Tracking --> Occluded : Joint Visibility < 0.40
    Occluded --> Tracking : Visibility >= 0.40
    
    Tracking --> Completed : Target Reps / Sets Finished
    Completed --> [*] : Save Session Summary to Backend
```

### Diagram 4: Entity-Relationship Diagram (Database Models)

```mermaid
erDiagram
    USER ||--o{ WORKOUT_LOG : logs
    USER ||--o{ MEAL_LOG : logs
    USER ||--o{ ACTIVITY_LOG : performs
    USER ||--o{ TREND_ENTRY : records
    USER ||--o{ ADMIN_AUDIT_LOG : targeted_by
    ADMIN ||--o{ ADMIN_AUDIT_LOG : executes
    ADMIN ||--o{ EXERCISE : manages
    ADMIN ||--o{ SYSTEM_CONFIG : configures

    USER {
        ObjectId _id PK
        string name
        string email UK
        string password
        string role "user | owner"
        boolean isSuspended
        date adminLockedUntil
        number age
        number weight
        number height
        string goal
        string experience
        string[] equipment
        string[] allergies
        string[] body_issues
        number days_per_week
        number streak
        date registrationDate
        number firstWorkoutDay
        mixed workoutPlan
        mixed latestNutritionPlan
    }

    EXERCISE {
        ObjectId _id PK
        string name
        string category
        string difficulty
        string[] equipment
        string[] muscleGroups
        string gifUrl
        boolean active
        ObjectId createdBy FK
    }

    SYSTEM_CONFIG {
        ObjectId _id PK
        string key UK
        mixed value
        ObjectId updatedBy FK
        date updatedAt
    }

    ADMIN_AUDIT_LOG {
        ObjectId _id PK
        ObjectId ownerId FK
        string action
        string targetType
        string targetId
        mixed details
        string ipAddress
        string userAgent
        date timestamp
    }
```

---

## 8. FRONTEND DEEP DIVE

### 8.1 State Management & Synchronization
- State is managed through a hybrid model:
  - Local Component State (`useState`, `useReducer`) for view-specific flows.
  - Context API (`ThemeContext`, `NotificationProvider`) for global application theming and toast dispatch.
  - `storage.js`: A robust wrapper over `localStorage` that incorporates JSON parsing guards, schema versioning, and cache invalidation.
  - `syncBridge.js`: Employs the browser `BroadcastChannel` API to synchronize habit check-offs across multiple open browser tabs in real time without polling.

### 8.2 Client-Side Computer Vision Engine
- `PoseDetector.jsx` implements client-side skeletal tracking:
  - Loads SIMD-accelerated WebAssembly (`vision_wasm_internal.wasm`, 11.5 MB) with automatic fallback to non-SIMD binaries (`vision_wasm_nosimd_internal.wasm`, 10.7 MB) on legacy mobile hardware.
  - Computes 3D vector angles using Euclidean dot-product geometry:
    $$\theta = \arccos\left(\frac{\vec{BA} \cdot \vec{BC}}{\|\vec{BA}\| \|\vec{BC}\|}\right) \times \frac{180^\circ}{\pi}$$
  - Adaptive Exponential Moving Average (EMA) filters joint coordinate jitter:
    $$\vec{P}_{\text{filtered}} = \vec{P}_{\text{prev}} \times (1 - \alpha) + \vec{P}_{\text{current}} \times \alpha$$
    where $\alpha = 0.40$ for high-speed movements (bicep curls, lateral raises) and $\alpha = 0.22$ for slow compound movements (squats, deadlifts).

### 8.3 Frontend Resilience & Circuit Breakers
- `utils/circuitBreaker.js` wraps remote calls in state machines with `CLOSED`, `OPEN`, and `HALF_OPEN` states.
- If the Python microservice encounters cold starts or timeouts (3 consecutive 5xx errors in 60s), the breaker trips to `OPEN` for 8 seconds, serving cached plans and showing a recovery timer rather than freezing user interaction.

---

## 9. BACKEND DEEP DIVE

### 9.1 Primary Backend Gateway (Node.js / Express)
- **Security Middleware Pipeline:**
  1. `cookieParser`: Extracts session cookies.
  2. `cors`: Restricts origins to configured whitelist (`CORS_ORIGINS`), rejecting wildcard `*` origins in production (`SEC-9`).
  3. `jsonParser`: Restricts standard request bodies to 100KB, while granting 10MB to `/api/python` proxy routes (`SEC-40`).
  4. Security Headers: Injects `X-Content-Type-Options: nosniff`, `X-Frame-Options: DENY`, `Referrer-Policy: no-referrer`, and `HSTS`.
  5. CSRF Protection: Validates double-submit cookie token on state-mutating requests (`csrf-csrf`).
  6. Maintenance Mode: Serves 503 Service Unavailable when enabled, cached in memory for 30 seconds (`PERF-1`).
- **Proxy Gateway (`routes/pythonProxy.js`):**
  - Forwards authenticated requests to Python FastAPI with upstream retry handling and request ID tracing.

### 9.2 AI Microservice (Python / FastAPI)
- **Engine Coordination:**
  - `server.py` hosts the ASGI application with CORS middleware and lifespan startup hooks.
  - `workout_engine.py` executes ML predictions and physiological clamping.
  - `nutrition_engine/` runs the 8-phase nutrition calculation solver.
  - `gemini_service.py` interfaces with Google Gemini LLMs with offline dictionary fallbacks.

---

## 10. DATABASE ARCHITECTURE & SCHEMA ANALYSIS

### 10.1 MongoDB Schema Design
- Schema definitions in `backend-node/models/User.js` compose modular sub-schemas (`SecuritySchema`, `FitnessProfileSchema`, `TrendEntrySchema`).
- The collection uses single-table inheritance to store heterogeneous user data without schema migration overhead.
- Database-level partial index enforces single owner account:
  ```javascript
  UserSchema.index({ role: 1 }, { unique: true, partialFilterExpression: { role: 'owner' } });
  ```

### 10.2 Document Size & Growth Vulnerability (`BUG-DAT-01`)
- In `backend-node/routes/profile.js`, `POST /activities/log` appends new activity entries onto `user.activities` without an eviction limit.
- Each activity entry occupies ~250 bytes. A user generating 15 activities daily accumulates ~1.3 MB annually in activities alone.
- Combined with workout history, meal entries, and daily trend objects, long-term active users will eventually breach MongoDB's 16MB BSON limit, causing fatal `BSONObjectTooLarge` crashes on write.

---

## 11. API SPECIFICATION & ENDPOINT CATALOG

### Primary Backend (Node.js) Endpoints

| Method | Endpoint | Auth Required | Description |
| :--- | :--- | :---: | :--- |
| `POST` | `/api/auth/register` | No | Registers user, hashes password (cost 12), sets auth cookie |
| `POST` | `/api/auth/login` | No | Authenticates user credentials, sets auth cookie |
| `POST` | `/api/auth/google` | No | Verifies Google ID token, logs in or bootstraps user |
| `POST` | `/api/auth/logout` | Yes | Clears `elevate_token` auth cookie |
| `GET` | `/api/auth/session` | No | Public session probe checking authentication status |
| `POST` | `/api/auth/reset-password/request` | No | Generates 15-min password reset token and dispatches alert |
| `POST` | `/api/auth/reset-password/confirm` | No | Verifies reset token and updates password hash |
| `GET` | `/api/profile` | Yes | Fetches user profile (uses `.lean()` for performance) |
| `POST` | `/api/profile/update` | Yes | Updates profile fields and evaluates workout regeneration |
| `GET` | `/api/profile/workout-history` | Yes | Retrieves past 50 logged workouts |
| `POST` | `/api/profile/workout-history` | Yes | Appends workout log with atomic `$position: 0, $slice: 50` |
| `GET` | `/api/profile/meal-history` | Yes | Retrieves normalized meal history |
| `POST` | `/api/profile/meal-history` | Yes | Appends meal log with atomic `$slice: -100` |
| `GET` | `/api/profile/trends` | Yes | Retrieves daily adherence trends (week/month/all) |
| `POST` | `/api/profile/trends` | Yes | Updates daily trend entry with `$slice: 180` |
| `POST` | `/api/profile/activities/log` | Yes | Appends single activity (CRITICAL: Unbounded growth bug) |
| `POST` | `/api/admin/login` | No | 3-factor admin login (Email, Password, Admin Key) |
| `GET` | `/api/admin/verify` | Admin | Validates active admin token and owner role |
| `GET` | `/api/admin/users` | Admin | Paginated user management table with search and filtering |
| `POST` | `/api/admin/users/:id/suspend` | Admin | Toggles user account suspension |
| `GET` | `/api/admin/system/health` | Admin | System health check (MongoDB ping, uptime, user counts) |
| `POST` | `/api/admin/system/maintenance` | Admin | Toggles maintenance mode |
| `GET` | `/api/admin/system/audit-logs` | Admin | Paginated audit log viewer |
| `ALL` | `/api/python/*` | Yes | Reverse-proxy forwarding to Python FastAPI |

### AI Microservice (Python FastAPI) Endpoints

| Method | Endpoint | Auth Required | Description |
| :--- | :--- | :---: | :--- |
| `GET` | `/health` | No | Service health check & model readiness probe |
| `POST` | `/workout` | Yes | Generates 7-day workout plan via XGBoost + safety clamps |
| `GET` | `/api/weekly-plan` | Yes | Retrieves cached or freshly generated weekly plan |
| `GET` | `/api/swap-options` | Yes | Retrieves alternative exercises for a workout slot |
| `POST` | `/nutrition` | Yes | Generates 7-day meal plan via Nutrition Engine V6 |
| `POST` | `/nutrition/swap` | Yes | Evaluates calorie-compatible meal substitutions |
| `POST` | `/chat` | Yes | Generative AI chat coaching with Gemini LLM |
| `PUT` | `/profile/update-safe` | Yes | Updates profile and regenerates plans (Dual-DB write) |

---

## 12. BUSINESS LOGIC, MATHEMATICAL FORMULAS & ML ALGORITHMS

### 12.1 Nutritional & Biometric Formulas
1. **Basal Metabolic Rate (BMR):** Evaluated via the Mifflin-St Jeor equation:
   $$\text{BMR}_{\text{male}} = 10 \times W_{\text{kg}} + 6.25 \times H_{\text{cm}} - 5 \times A_{\text{years}} + 5$$
   $$\text{BMR}_{\text{female}} = 10 \times W_{\text{kg}} + 6.25 \times H_{\text{cm}} - 5 \times A_{\text{years}} - 161$$
2. **Total Daily Energy Expenditure (TDEE):**
   $$\text{TDEE} = \text{BMR} \times \text{Activity Multiplier}$$
   where Activity Multiplier is 1.2 (Sedentary), 1.375 (Light), 1.55 (Moderate), 1.725 (Very Active), or 1.9 (Extra Active).
3. **Goal-Based Caloric Offsets:**
   - Weight / Fat Loss: $\text{Calories} = \text{TDEE} - 500\text{ kcal}$
   - Muscle Gain: $\text{Calories} = \text{TDEE} + 350\text{ kcal}$
   - Maintenance: $\text{Calories} = \text{TDEE}$
4. **Macronutrient Distribution:**
   - Protein: $2.0\text{ g/kg}$ (Muscle Gain) or $1.6\text{ g/kg}$ (Fat Loss)
   - Fat: 25% of total caloric intake ($\text{Grams} = \frac{\text{Calories} \times 0.25}{9}$)
   - Carbohydrates: Remaining calories allocated at $4\text{ kcal/g}$.

### 12.2 Machine Learning Architecture
- **Model Type:** Scikit-Learn `MultiOutputRegressor` wrapping `XGBRegressor`:
  - `n_estimators`: 200
  - `learning_rate`: 0.05
  - `max_depth`: 5
- **Input Features (8 Dimensions):** `Age`, `Gender_Encoded`, `Weight_kg`, `Height_cm`, `Goal_Encoded`, `Experience_Encoded`, `Days_Per_Week`, `Body_Issues_Count`.
- **Output Targets (5 Dimensions):** `Target_Sets`, `Target_Reps`, `Rest_Seconds`, `Intensity_Factor`, `Session_Duration_Minutes`.
- **Clamping Layer:** Predicted values pass through physiological bounds:
  $$\text{Sets} = \min(6, \max(1, \text{round}(\hat{y}_{\text{sets}})))$$
  $$\text{Rest} = \min(180, \max(30, \text{round}(\hat{y}_{\text{rest}})))$$

---

## 13. COMPLETE APPLICATION EXECUTION FLOWS

### Flow 1: Registration to Active Workout Plan Generation
1. Client submits registration payload to `POST /api/auth/register`.
2. Node.js validates input lengths, hashes password using Bcrypt (12 rounds), records `registrationDate`, and computes `firstWorkoutDay` (Mon=0 to Sun=6).
3. Node.js issues JWT and sets HttpOnly cookie `elevate_token`.
4. User completes profile setup on `/profile-setup`. Client sends `POST /api/profile/update`.
5. Node updates Mongoose User document and flags `workout_regeneration_needed: true`.
6. Frontend requests new workout plan via `POST /api/python/workout`.
7. Node.js proxy attaches `x-request-id` and forwards request to Python FastAPI.
8. Python extracts user biometrics, scales features via `FeaturePipeline`, and runs inference through `MultiOutputXGBoostModel`.
9. Predicted sets and reps are passed to `WorkoutRules`, which clamps values, filters exercises matching injury tags, and balances muscle volume across requested training days.
10. Python returns 7-day structured workout JSON. Node returns JSON to frontend. Frontend caches plan in localStorage and renders Dashboard.

### Flow 2: Live Computer Vision Workout Execution
1. User clicks "Start Workout" on `/workout`.
2. Frontend requests camera stream and initializes MediaPipe `PoseLandmarker` using WebAssembly.
3. Every animation frame (60 FPS), MediaPipe extracts 33 skeletal landmark coordinates $(x, y, z, \text{visibility})$.
4. `PoseDetector.jsx` identifies exercise pattern (e.g. `CURL`).
5. Vector angle between shoulder, elbow, and wrist is calculated via `calcAngle()`.
6. Angle is smoothed via Exponential Moving Average (EMA).
7. Rep counter state machine transitions: extended ($>150^\circ$) $\rightarrow$ flexed ($<45^\circ$) $\rightarrow$ extended ($>150^\circ$).
8. Upon rep completion, Web Audio API synthesizes a success tone; rep count increments in state.
9. When all sets complete, summary payload is posted to `POST /api/profile/workout-history`.
10. Node.js prepends workout to `user.workouts` with `$position: 0, $slice: 50`.


---

## 14. IDENTIFIED BUGS AND VULNERABILITY LEDGER

*Refer to `BUG_REPORT.md` for complete reproduction steps, impact analysis, and source code patches.*

| Bug ID | Severity | File Reference | Category | Description |
| :--- | :---: | :--- | :--- | :--- |
| **BUG-SEC-01** | **Critical** | `backend-node/routes/auth.js:27` | Security | User JWT tokens never expire (`expiresIn` omitted, cookie maxAge 100 years). |
| **BUG-SEC-02** | **Critical** | `backend-node/routes/adminAuth.js:201` | Security | Admin JWT tokens never expire (`tokenExpiry` omitted from `jwt.sign`). |
| **BUG-SEC-03** | **Critical** | `backend-node/middleware/auth.js:52` | Authorization | Suspended users retain perpetual API access (middleware trusts token claim). |
| **BUG-CI-01** | **Critical** | `frontend/src/components/PoseDetector.jsx:113` | CI / CD | 8 ESLint `no-unused-vars` errors block automated CI quality gates. |
| **BUG-TST-01** | **High** | `backend-python/tests/test_candidate_health.py:77` | Quality Gate | Candidate generation fallback rate (9–12%) exceeds 5% test gate assertion. |
| **BUG-DAT-01** | **High** | `backend-node/routes/profile.js:458` | Data Layer | Unbounded growth in `user.activities` threatens 16MB MongoDB document limit. |
| **BUG-ARCH-01** | **High** | `backend-python/server.py:3563` | Architecture | Dual-database write split-brain between Node Mongoose and Python Motor. |
| **BUG-API-01** | **Medium** | `frontend/src/api.js:284` | API Contract | Export `updateProfileAndRegenerateWorkouts` targets non-existent route (404). |
| **BUG-DAT-02** | **Medium** | `backend-node/utils/mealUtils.js:21` | Localization | Hardcoded IST (+05:30) timezone distorts date keys for global users. |
| **BUG-DAT-03** | **Medium** | `backend-node/routes/profile.js:247` | Consistency | Inconsistent workout array ordering (prepend vs append) across routes. |
| **BUG-ML-01** | **Medium** | `backend-python/app/feature_pipeline.py` | Machine Learning | 1,500+ Scikit-Learn unknown class warnings from unnormalized token casing. |
| **BUG-DEP-01** | **Medium** | `backend-python/app/gemini_service.py:6` | Dependencies | Discontinued `google-generativeai` package emits end-of-support warnings. |
| **BUG-DEP-02** | **Low** | `backend-python/server.py:1286` | Framework | Deprecated FastAPI startup/shutdown event handlers (`@app.on_event`). |
| **BUG-CV-01** | **Low** | `backend-python/app/detectors/curl_detector.py:14` | Computer Vision | Python curl detector inspects only left arm, failing on right-arm curls. |
| **BUG-SEC-04** | **Medium** | `backend-node/routes/profile.js:395` | Security | Unsanitized dynamic `$set` key expansion in trend updates. |

---

## 15. COMPREHENSIVE SECURITY AUDIT (OWASP TOP 10)

| OWASP Vulnerability Category | Status | Evaluation & Findings |
| :--- | :---: | :--- |
| **A01: Broken Access Control** | **FAIL** | User suspension is completely bypassed because `middleware/auth.js` trusts static claims in non-expiring JWTs (`BUG-SEC-03`). Admin endpoints are well-defended with `requireOwner` and IP whitelisting. |
| **A02: Cryptographic Failures** | **PASS** | Passwords hashed using Bcrypt with cost factor 12. Admin secret key uses salted Bcrypt hash. Secrets are managed via environment variables. |
| **A03: Injection (SQL / NoSQL)** | **PASS** | Mongoose parameterized queries prevent NoSQL injection. User search regexes are properly escaped using `escapeRegex` (`Bug #1`). Dynamic `$set` in trends update requires key whitelisting (`BUG-SEC-04`). |
| **A04: Insecure Design** | **FAIL** | Non-expiring tokens (`BUG-SEC-01`, `BUG-SEC-02`) and dual-database split-brain writes (`BUG-ARCH-01`) represent significant architectural design flaws. |
| **A05: Security Misconfiguration** | **PASS** | Helmet-lite headers enforce `X-Content-Type-Options: nosniff`, `X-Frame-Options: DENY`, and `HSTS`. CORS origins are validated at startup. |
| **A06: Vulnerable Dependencies** | **WARN** | Legacy `google-generativeai` package is discontinued and unsupported (`BUG-DEP-01`). |
| **A07: Identification & Auth Failures** | **FAIL** | Missing token expiration violates session lifetime standards. Brute-force protection on admin login is well-implemented (5 attempts trigger 30-min lockout). |
| **A08: Software & Data Integrity** | **PASS** | Serialized ML models include SHA256 checksums in `backend-python/app/models/checksums.sha256`. |
| **A09: Security Logging & Monitoring** | **PASS** | `AdminAuditLog` records administrative events with client IP, user agent, and payload redaction (`redactSensitive`). Failed audits are counted and logged. |
| **A10: Server-Side Request Forgery** | **PASS** | Upstream Python proxy only targets configured internal URLs (`ML_API_URL`). External USDA and API Ninjas lookups are restricted to fixed hardcoded API hostnames. |

---

## 16. PERFORMANCE, CONCURRENCY & SCALABILITY AUDIT

- **Client-Side WASM Vision Performance:**
  - Running MediaPipe in WebAssembly eliminates all server GPU and streaming costs.
  - Generates 60 FPS on desktop and 30–45 FPS on modern mobile devices. Memory consumption remains stable at ~120 MB.
- **Frontend React Re-Rendering Bottlenecks:**
  - `Dashboard.jsx` (3,748 lines) and `Workout.jsx` (3,575 lines) re-render massive DOM subtrees on single state updates (such as clicking a habit checkbox or incrementing a rep timer).
  - Remediation: Decompose into memoized functional components (`React.memo`).
- **Database Query Performance:**
  - Read-heavy routes (`GET /api/profile`, `GET /api/profile/trends`, `GET /api/profile/workout-history`) properly utilize `.lean()` to bypass Mongoose hydration overhead (`PERF-2`).
  - System stats aggregation employs a single `$facet` pipeline, replacing 4 sequential queries (`PERF-3`).
- **Microservice Latency & Timeouts:**
  - Upstream plan generation takes 1.5s–3.5s for complex weekly routines. The Node.js proxy sets an appropriate 120s timeout with cold-start retry loops.

---

## 17. CODE QUALITY & SOLID / DRY PRINCIPLES ASSESSMENT

- **Single Responsibility Principle (SRP) Violations:**
  - `backend-python/server.py` violates SRP by combining ML inference, database CRUD, background worker loops, and model warmup.
  - `backend-python/app/workout_engine.py` violates SRP by combining XGBoost prediction, physiological clamping, progression math, and HTTP GIF scraping.
  - `frontend/src/pages/Dashboard.jsx` violates SRP by combining UI presentation, WebSocket/BroadcastChannel synchronization, habit business logic, and trend chart derivation.
- **DRY (Don't Repeat Yourself) Violations:**
  - Date normalization and meal macro accumulation were historically duplicated across `users.js` and `profile.js` before `mealUtils.js` extraction.
  - Workout logging logic remains duplicated between `routes/profile.js` and `routes/users.js` with conflicting array ordering (`BUG-DAT-03`).
- **Type Safety Assessment:**
  - Backend Python uses strong Pydantic schemas (`WorkoutProfileRequest`, `PlanProfileUpdateRequest`).
  - Node.js and Frontend React use dynamic JavaScript without TypeScript definitions, resulting in runtime bugs such as `BUG-API-01`.

---

## 18. PROJECT STRENGTHS

1. **Deterministic Physiological Safety Clamps:** Mathematical constraints guarantee that AI recommendations never prescribe hazardous workout volumes or allergen foods.
2. **Local Client-Side Computer Vision:** Zero-latency, zero-cloud-cost WebAssembly pose tracking preserves user privacy.
3. **Multi-Output XGBoost Regression:** Correlated parameters (sets, reps, rest) are predicted simultaneously, preserving physical training relationships.
4. **Hardened Admin Security Framework:** Multi-factor admin login, IP whitelisting with proxy-spoofing defense, brute-force lockout, and immutable audit logs.
5. **Decoupled Circuit Breakers:** Independent frontend and backend circuit breakers prevent cascading failures during microservice cold starts.

---

## 19. PROJECT WEAKNESSES

1. **Dual-Database Write Split-Brain:** Node.js and Python both write to MongoDB without coordination, causing race conditions and bypassed validations.
2. **Non-Expiring Authentication Tokens:** User and admin JWTs live indefinitely; user suspensions cannot be enforced.
3. **Unbounded Document Growth:** `user.activities` lacks array slicing, threatening MongoDB 16MB document size limits.
4. **Monolithic Code Architecture:** Four files exceed 3,500 lines, impairing maintainability and developer velocity.
5. **Failing CI Quality Gates:** 8 ESLint errors and candidate generation test failures block automated pipelines.

---

## 20. MISSING PRODUCTION FEATURES & GAPS

1. **Dual-Token Authentication (Access + Refresh Token):** Short-lived access tokens (15m) paired with rotating refresh tokens stored in secure HttpOnly cookies.
2. **Asynchronous Background Task Queue:** Offloading 3–5 second meal plan calculations to Celery/BullMQ with WebSocket status updates.
3. **International Timezone Normalization:** Allowing clients to supply IANA timezone identifiers to prevent date shifting.
4. **End-to-End Test Suite:** Headless browser integration tests (Playwright) covering registration, live workout execution, and admin suspension.

---

## 21. TESTING & VALIDATION VERIFICATION RESULTS

During this audit, automated validation suites were executed directly in the repository environment:

```
┌─────────────────────────────────────────────────────────────────────────┐
│                       AUTOMATED TEST RESULTS                            │
├───────────────────────┬──────────────┬────────┬────────┬────────────────┤
│ Suite                 │ Framework    │ Total  │ Passed │ Status         │
├───────────────────────┼──────────────┼────────┼────────┼────────────────┤
│ Frontend Unit Tests   │ Vitest       │ 37     │ 37     │ PASS (10.2s)   │
│ Backend-Node Tests    │ Jest         │ 24     │ 24     │ PASS (16.7s)   │
│ Backend-Python Tests  │ Pytest       │ 93     │ 92     │ 1 FAILED (4m)  │
│ Python Compilation    │ py_compile   │ 108    │ 108    │ PASS           │
│ Frontend Production   │ Vite Build   │ 130    │ 130    │ PASS (5.6s)    │
│ Frontend Linter       │ ESLint       │ 8 err  │ 0      │ FAIL (8 Errs)  │
└───────────────────────┴──────────────┴────────┴────────┴────────────────┘
```

- **Pytest Failure Detail:** `test_candidate_health.py::test_fallback_usage_rate` failed: `AssertionError: Fallback usage 9.00% exceeds threshold 5%`.
- **ESLint Failure Detail:** 8 unused variable errors in `PoseDetector.jsx`, `Dashboard.jsx`, and `Workout.jsx`.

---

## 22. TECHNICAL DEBT ANALYSIS

1. **Abandoned Router Stubs:** `backend-python/app/routes/workout.py` exists as an unmigrated stub commenting on work never completed.
2. **Redundant Route Handlers:** `backend-node/routes/users.js` duplicates profile, workout, and meal saving logic from `routes/profile.js`.
3. **Deprecated Packages:** Python relies on discontinued `google-generativeai` and deprecated FastAPI `@app.on_event` handlers.
4. **Feature Vocabulary Drift:** Unnormalized string casings cause 1,500+ Scikit-Learn `LabelEncoder` warnings per test run.

---

## 23. RECOMMENDED REFACTORING

### Refactoring Step 1: Single Source of Truth Database Architecture
Eliminate Motor write operations from `backend-python`. The Python microservice must become a stateless calculation engine:
```
Client ──► Node.js Gateway ──► Python AI Service (Compute JSON)
                 │                      │
                 ▼                      ▼
           MongoDB (Sole Writer) ◄── (Returns JSON to Node)
```

### Refactoring Step 2: Component Decomposition of React Monoliths
Decompose `Dashboard.jsx` (3,748 lines) into:
- `<HabitTracker />`: Hydration, sleep, and step cards.
- `<TrendChart />`: Weekly adherence visualizer.
- `<ActionIdeas />`: Motivational suggestion drawer.
- `<ActivityFeed />`: Recent activity list.

### Refactoring Step 3: Python Router Migration
Migrate workout and nutrition endpoints from `server.py` into `app/routes/workout.py` and `app/routes/meal_plan.py`, reducing `server.py` to under 200 lines.

---

## 24. PRIORITY-BASED ACTION PLAN

*Refer to `IMPROVEMENT_ROADMAP.md` for task breakdown, files, and complexity.*

```
┌────────────────────────────────────────────────────────────────────────┐
│                      ENGINEERING ACTION MATRIX                         │
├────┬─────────────────────────────┬─────────────────────┬───────────────┤
│ P  │ Task Summary                │ Affected Files      │ Complexity    │
├────┼─────────────────────────────┼─────────────────────┼───────────────┤
│ P0 │ Enforce JWT Expiration      │ routes/auth.js      │ Low (0.5d)    │
│ P0 │ Enforce DB Suspension Check │ middleware/auth.js  │ Low (0.5d)    │
│ P0 │ Fix 8 ESLint Errors         │ Dashboard.jsx, etc. │ Low (0.25d)   │
│ P0 │ Retune Health Test Gate     │ candidate_health.py │ Medium (1d)   │
│ P1 │ Resolve Dual-DB Split-Brain │ server.py, Node     │ High (3d)     │
│ P1 │ Slice user.activities (100) │ routes/profile.js   │ Low (0.5d)    │
│ P1 │ Dynamic Timezone Offset     │ utils/mealUtils.js  │ Medium (1d)   │
│ P1 │ Deprecate routes/users.js   │ routes/users.js     │ Medium (1.5d) │
│ P2 │ Decompose React Monoliths   │ Dashboard, Workout  │ High (4d)     │
│ P2 │ Modularize server.py Monolith│ server.py, routes   │ Medium (2d)   │
│ P2 │ Upgrade to google-genai SDK │ gemini_service.py   │ Medium (1d)   │
│ P2 │ Sanitize LabelEncoder drift │ feature_pipeline.py │ Medium (1d)   │
│ P3 │ Symmetric Limb CV Tracking  │ curl_detector.py    │ Low (0.5d)    │
│ P3 │ Async Celery/BullMQ Queue   │ server.py, api.js   │ High (4d)     │
│ P3 │ Playwright E2E Test Suite   │ e2e/playwright      │ High (5d)     │
└────┴─────────────────────────────┴─────────────────────┴───────────────┘
```

---

## 25. OVERALL PROJECT EVALUATION & EXECUTIVE VERDICT

### Final Scorecard

```
┌─────────────────────────────────────────────────────────────┐
│                 ELEVATE FITNESS PLATFORM                    │
│                 OVERALL ENGINEERING SCORE                   │
│                                                             │
│   Domain                        Rating                      │
│   ─────────────────────────────────────────────             │
│   Computer Vision (Pose)        9.0 / 10   ★★★★★            │
│   Machine Learning & AI         8.5 / 10   ★★★★☆            │
│   Frontend UI / UX Design       8.0 / 10   ★★★★☆            │
│   DevOps & Automated Testing    6.0 / 10   ★★★☆☆            │
│   System Architecture           5.5 / 10   ★★★☆☆            │
│   Code Quality & Modularity     5.0 / 10   ★★½☆☆            │
│   Security & Authorization      5.0 / 10   ★★½☆☆            │
│                                                             │
│   FINAL WEIGHTED SCORE:         6.7 / 10                    │
│   PRODUCTION READINESS:         REQUIRES REMEDIATION        │
└─────────────────────────────────────────────────────────────┘
```

### Lead Architect's Final Assessment
The Elevate platform exhibits impressive engineering innovation. The local WebAssembly pose estimation delivers high-speed biomechanical tracking with complete privacy. The multi-output XGBoost regression models demonstrate mature domain understanding by modeling physiological covariance, while the deterministic safety clamps ensure user protection against AI hallucination.

However, the platform cannot be certified for production in its current state. The non-expiring authentication tokens, bypassed user suspension logic, dual-database split-brain writes, and failing CI quality gates present immediate operational risks. 

By executing the prioritized roadmap outlined in `IMPROVEMENT_ROADMAP.md`—starting with the P0 security fixes and CI remediation—Elevate will achieve the enterprise-grade stability, security, and scalability required for a commercial fitness platform.
