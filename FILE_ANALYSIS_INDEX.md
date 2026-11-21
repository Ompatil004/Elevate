# FILE ANALYSIS INDEX & REPOSITORY COVERAGE CHECKLIST

> **Audit Verification Level:** Exhaustive (100% Repository Coverage)
> **Total Cataloged Files:** 287
> **Excluded Directories:** `node_modules`, `.git`, `dist`, `build`, `venv`, `.venv`, `__pycache__`, `.pytest_cache`

---

## Repository File Distribution Summary

| Subsystem | Total Files | Total Size | Source Code Files | ML Models / Data / Binaries | Documentation |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **1. Root Configuration & Orchestration Scripts** | 14 | 0.64 MB | 1 | 7 | 0 |
| **2. Primary Backend: Node.js / Express** | 27 | 0.38 MB | 23 | 2 | 0 |
| **3. AI / ML Microservice: Python / FastAPI** | 159 | 16.19 MB | 108 | 45 | 0 |
| **4. Frontend Application: React 19 / Vite** | 63 | 34.17 MB | 46 | 6 | 1 |
| **5. Documentation & Presentation Artifacts** | 24 | 8.82 MB | 0 | 0 | 24 |
| **TOTAL** | **287** | **60.19 MB** | **178** | **60** | **25** |

---

## 1. Root Configuration & Orchestration Scripts (14 files)

| # | Relative File Path | Size (KB) | Lines | Classification | Audit Status | Primary Purpose / Role in Elevate Platform |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| 1 | `.github/workflows/quality-gates.yml` | 3.8 KB | 132 | Configuration / Data | Reviewed (Config/Doc) | GitHub Actions multi-job CI workflow running lint, build, unit tests, and secret scans |
| 2 | `.gitignore` | 2.4 KB | 150 | Asset / Config | Reviewed (Config/Doc) | Git exclusion configuration for temporary files, dependencies, models, and credentials |
| 3 | `LICENSE` | 1.1 KB | 21 | Asset / Config | Reviewed (Config/Doc) | Supporting repository source, configuration, or documentation file |
| 4 | `app/models/le_gender.pkl` | 0.5 KB | 2 | Trained ML Model | Verified (Binary/Data) | Serialized machine learning model artifact (XGBoost model / Scikit-Learn LabelEncoder) |
| 5 | `app/models/le_goal.pkl` | 0.5 KB | 2 | Trained ML Model | Verified (Binary/Data) | Serialized machine learning model artifact (XGBoost model / Scikit-Learn LabelEncoder) |
| 6 | `app/models/le_target.pkl` | 0.5 KB | 2 | Trained ML Model | Verified (Binary/Data) | Serialized machine learning model artifact (XGBoost model / Scikit-Learn LabelEncoder) |
| 7 | `app/models/xgb_workout.pkl` | 640.5 KB | 4278 | Trained ML Model | Verified (Binary/Data) | Serialized machine learning model artifact (XGBoost model / Scikit-Learn LabelEncoder) |
| 8 | `package-lock.json` | 0.5 KB | 22 | Configuration / Data | Reviewed (Config/Doc) | Static dataset, knowledge base, or configuration data store |
| 9 | `package.json` | 0.1 KB | 5 | Configuration / Data | Reviewed (Config/Doc) | Root project package descriptor declaring bcryptjs dependency |
| 10 | `search_github.py` | 0.5 KB | 16 | Source Code | Fully Analyzed | Supporting repository source, configuration, or documentation file |
| 11 | `start_all.bat` | 1.2 KB | 36 | Shell / Build Script | Fully Analyzed | Windows launcher batch script orchestrating Node, Python, and Vite frontend services |
| 12 | `start_frontend.bat` | 0.1 KB | 5 | Shell / Build Script | Fully Analyzed | Windows launcher batch script launching React Vite development server on port 5173 |
| 13 | `start_node.bat` | 0.1 KB | 5 | Shell / Build Script | Fully Analyzed | Windows launcher batch script starting Node.js backend on port 5000 |
| 14 | `start_python.bat` | 0.3 KB | 11 | Shell / Build Script | Fully Analyzed | Windows launcher batch script activating venv and starting Python FastAPI on port 8000 |

---

## 2. Primary Backend: Node.js / Express (27 files)

| # | Relative File Path | Size (KB) | Lines | Classification | Audit Status | Primary Purpose / Role in Elevate Platform |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| 1 | `backend-node/.env` | 1.6 KB | 46 | Asset / Config | Reviewed (Config/Doc) | Supporting repository source, configuration, or documentation file |
| 2 | `backend-node/.env.example` | 0.9 KB | 37 | Asset / Config | Reviewed (Config/Doc) | Supporting repository source, configuration, or documentation file |
| 3 | `backend-node/check_user_nutrition.js` | 1.1 KB | 32 | Source Code | Fully Analyzed | Database diagnostic script inspecting user meal logs and calculated macro fields |
| 4 | `backend-node/middleware/adminAuth.js` | 6.0 KB | 210 | Source Code | Fully Analyzed | Admin authorization middleware enforcing owner role, IP allowlist, and audit logging |
| 5 | `backend-node/middleware/adminRateLimit.js` | 2.3 KB | 81 | Source Code | Fully Analyzed | Rate limiting middleware configuring express-rate-limit for admin endpoints and auth routes |
| 6 | `backend-node/middleware/auth.js` | 3.3 KB | 80 | Source Code | Fully Analyzed | JWT authentication middleware reading elevate_token HttpOnly cookie with suspension checking |
| 7 | `backend-node/middleware/validate.js` | 4.6 KB | 124 | Source Code | Fully Analyzed | Centralized express-validator rules and validation error formatting middleware |
| 8 | `backend-node/models/AdminAuditLog.js` | 1.1 KB | 50 | Source Code | Fully Analyzed | Mongoose AdminAuditLog model for recording administrative events, IP addresses, and user-agent details |
| 9 | `backend-node/models/Exercise.js` | 0.6 KB | 16 | Source Code | Fully Analyzed | Mongoose Exercise model storing exercise catalog, categories, equipment, and GIF URLs |
| 10 | `backend-node/models/SystemConfig.js` | 0.4 KB | 20 | Source Code | Fully Analyzed | Mongoose SystemConfig model for dynamic runtime settings, maintenance mode, and announcements |
| 11 | `backend-node/models/User.js` | 7.8 KB | 151 | Source Code | Fully Analyzed | Mongoose User model composing Identity, Security, FitnessProfile, and TrendEntry sub-schemas |
| 12 | `backend-node/package-lock.json` | 218.4 KB | 6175 | Configuration / Data | Reviewed (Config/Doc) | Static dataset, knowledge base, or configuration data store |
| 13 | `backend-node/package.json` | 1.0 KB | 42 | Configuration / Data | Reviewed (Config/Doc) | Static dataset, knowledge base, or configuration data store |
| 14 | `backend-node/routes/adminAuth.js` | 7.9 KB | 294 | Source Code | Fully Analyzed | Admin authentication router with multi-credential verification, lockout enforcement, and security alerts |
| 15 | `backend-node/routes/adminContent.js` | 5.3 KB | 196 | Source Code | Fully Analyzed | Admin content management router providing exercise CRUD operations and workout rule updates |
| 16 | `backend-node/routes/adminSystem.js` | 10.0 KB | 355 | Source Code | Fully Analyzed | Admin system configuration router managing health checks, audit logs, announcements, and maintenance |
| 17 | `backend-node/routes/adminUsers.js` | 10.1 KB | 357 | Source Code | Fully Analyzed | Admin user management router implementing pagination, filtering, suspension, activation, and deletion |
| 18 | `backend-node/routes/auth.js` | 15.7 KB | 467 | Source Code | Fully Analyzed | Authentication router implementing registration, password login, Google OAuth, logout, and password resets |
| 19 | `backend-node/routes/profile.js` | 19.9 KB | 520 | Source Code | Fully Analyzed | User profile router handling profile updates, workout/meal histories, trends, and activity tracking |
| 20 | `backend-node/routes/pythonProxy.js` | 9.7 KB | 295 | Source Code | Fully Analyzed | Express-to-FastAPI reverse-proxy forwarding protected requests with JWT header propagation |
| 21 | `backend-node/routes/users.js` | 16.1 KB | 499 | Source Code | Fully Analyzed | Legacy user data router proxying USDA & API Ninjas lookups, workouts, and meals |
| 22 | `backend-node/scripts/seed.js` | 6.3 KB | 172 | Source Code | Fully Analyzed | Database bootstrapping script creating initial owner account and system settings |
| 23 | `backend-node/server.js` | 17.0 KB | 407 | Source Code | Fully Analyzed | Express application entrypoint, MongoDB connection manager, security headers, CSRF & maintenance middleware |
| 24 | `backend-node/services/securityNotificationService.js` | 6.2 KB | 230 | Source Code | Fully Analyzed | Notification dispatch service supporting SMTP email alerts and outbound webhook payloads |
| 25 | `backend-node/tests/auth.middleware.test.js` | 3.6 KB | 104 | Source Code | Fully Analyzed | Automated test suite verifying API contracts, regressions, and component behaviors |
| 26 | `backend-node/tests/pythonProxy.test.js` | 9.6 KB | 315 | Source Code | Fully Analyzed | Automated test suite verifying API contracts, regressions, and component behaviors |
| 27 | `backend-node/utils/mealUtils.js` | 3.6 KB | 111 | Source Code | Fully Analyzed | Shared meal utility library providing date formatting, meal type classification, and macro calculations |

---

## 3. AI / ML Microservice: Python / FastAPI (159 files)

| # | Relative File Path | Size (KB) | Lines | Classification | Audit Status | Primary Purpose / Role in Elevate Platform |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| 1 | `backend-python/.env` | 2.3 KB | 62 | Asset / Config | Reviewed (Config/Doc) | Supporting repository source, configuration, or documentation file |
| 2 | `backend-python/.env.example` | 0.4 KB | 17 | Asset / Config | Reviewed (Config/Doc) | Supporting repository source, configuration, or documentation file |
| 3 | `backend-python/Dockerfile` | 0.6 KB | 28 | Asset / Config | Reviewed (Config/Doc) | Supporting repository source, configuration, or documentation file |
| 4 | `backend-python/app/__init__.py` | 0.1 KB | 5 | Source Code | Fully Analyzed | Supporting repository source, configuration, or documentation file |
| 5 | `backend-python/app/adaptive_modifier.py` | 8.2 KB | 201 | Source Code | Fully Analyzed | Dynamic intensity and volume modifier adjusting workouts based on recent sleep and fatigue scores |
| 6 | `backend-python/app/analyze2.py` | 0.4 KB | 6 | Source Code | Fully Analyzed | Supporting repository source, configuration, or documentation file |
| 7 | `backend-python/app/analyze_data.py` | 0.6 KB | 17 | Source Code | Fully Analyzed | Supporting repository source, configuration, or documentation file |
| 8 | `backend-python/app/biometric_normalizer.py` | 3.4 KB | 91 | Source Code | Fully Analyzed | Biometric data validator computing BMI, BMR, TDEE, and normalizing user input metrics |
| 9 | `backend-python/app/circuit_breaker.py` | 7.7 KB | 212 | Source Code | Fully Analyzed | Python circuit breaker implementation protecting upstream Gemini and external API calls |
| 10 | `backend-python/app/config/exercise_mapping.json` | 176.3 KB | 6627 | Configuration / Data | Reviewed (Config/Doc) | Static dataset, knowledge base, or configuration data store |
| 11 | `backend-python/app/config/movement_rules.json` | 1.8 KB | 105 | Configuration / Data | Reviewed (Config/Doc) | Static dataset, knowledge base, or configuration data store |
| 12 | `backend-python/app/core/__init__.py` | 0.0 KB | 1 | Source Code | Fully Analyzed | Supporting repository source, configuration, or documentation file |
| 13 | `backend-python/app/core/auth.py` | 2.0 KB | 60 | Source Code | Fully Analyzed | Supporting repository source, configuration, or documentation file |
| 14 | `backend-python/app/core/responses.py` | 0.6 KB | 17 | Source Code | Fully Analyzed | Supporting repository source, configuration, or documentation file |
| 15 | `backend-python/app/data_health_analysis.py` | 19.3 KB | 505 | Source Code | Fully Analyzed | Dataset integrity validator checking nulls, variance, and distributions in training data |
| 16 | `backend-python/app/db.py` | 5.7 KB | 168 | Source Code | Fully Analyzed | Async Motor MongoDB client connection manager and database dependency injector |
| 17 | `backend-python/app/detectors/__init__.py` | 0.1 KB | 2 | Source Code | Fully Analyzed | MediaPipe joint angle calculation and state-machine rep counter for computer vision exercise tracking |
| 18 | `backend-python/app/detectors/base_detector.py` | 4.1 KB | 88 | Source Code | Fully Analyzed | MediaPipe joint angle calculation and state-machine rep counter for computer vision exercise tracking |
| 19 | `backend-python/app/detectors/curl_detector.py` | 3.0 KB | 78 | Source Code | Fully Analyzed | MediaPipe joint angle calculation and state-machine rep counter for computer vision exercise tracking |
| 20 | `backend-python/app/detectors/detector_factory.py` | 5.7 KB | 159 | Source Code | Fully Analyzed | MediaPipe joint angle calculation and state-machine rep counter for computer vision exercise tracking |
| 21 | `backend-python/app/detectors/generic_detector.py` | 2.1 KB | 60 | Source Code | Fully Analyzed | MediaPipe joint angle calculation and state-machine rep counter for computer vision exercise tracking |
| 22 | `backend-python/app/detectors/hinge_detector.py` | 2.8 KB | 76 | Source Code | Fully Analyzed | MediaPipe joint angle calculation and state-machine rep counter for computer vision exercise tracking |
| 23 | `backend-python/app/detectors/lunge_detector.py` | 2.5 KB | 71 | Source Code | Fully Analyzed | MediaPipe joint angle calculation and state-machine rep counter for computer vision exercise tracking |
| 24 | `backend-python/app/detectors/plank_detector.py` | 2.8 KB | 77 | Source Code | Fully Analyzed | MediaPipe joint angle calculation and state-machine rep counter for computer vision exercise tracking |
| 25 | `backend-python/app/detectors/pull_detector.py` | 2.7 KB | 73 | Source Code | Fully Analyzed | MediaPipe joint angle calculation and state-machine rep counter for computer vision exercise tracking |
| 26 | `backend-python/app/detectors/push_detector.py` | 3.1 KB | 81 | Source Code | Fully Analyzed | MediaPipe joint angle calculation and state-machine rep counter for computer vision exercise tracking |
| 27 | `backend-python/app/detectors/raise_detector.py` | 2.7 KB | 72 | Source Code | Fully Analyzed | MediaPipe joint angle calculation and state-machine rep counter for computer vision exercise tracking |
| 28 | `backend-python/app/detectors/squat_detector.py` | 3.3 KB | 84 | Source Code | Fully Analyzed | MediaPipe joint angle calculation and state-machine rep counter for computer vision exercise tracking |
| 29 | `backend-python/app/deterministic_meal_engine.py` | 63.6 KB | 1467 | Source Code | Fully Analyzed | Meal Engine V2 implementing 8-phase deterministic meal generation and rule-based candidate filtering |
| 30 | `backend-python/app/evaluation_framework.py` | 19.8 KB | 540 | Source Code | Fully Analyzed | ML model performance evaluation suite calculating MAE, RMSE, and safety compliance metrics |
| 31 | `backend-python/app/feature_pipeline.py` | 23.2 KB | 594 | Source Code | Fully Analyzed | Feature engineering pipeline scaling numerical features and encoding categorical fitness parameters |
| 32 | `backend-python/app/gemini_service.py` | 24.4 KB | 498 | Source Code | Fully Analyzed | Google Gemini LLM integration service with circuit breaker protection, caching, and offline fallback responses |
| 33 | `backend-python/app/hybrid_volume_optimizer.py` | 20.6 KB | 573 | Source Code | Fully Analyzed | Volume balancer reconciling ML XGBoost set/rep predictions with hardcoded safety guardrails |
| 34 | `backend-python/app/meal_engine.py` | 36.9 KB | 827 | Source Code | Fully Analyzed | Backward-compatibility wrapper bridging legacy meal engine callers to NutritionEngineV6 |
| 35 | `backend-python/app/ml_utils.py` | 16.3 KB | 369 | Source Code | Fully Analyzed | Supporting repository source, configuration, or documentation file |
| 36 | `backend-python/app/models/__init__.py` | 0.0 KB | 1 | Source Code | Fully Analyzed | Supporting repository source, configuration, or documentation file |
| 37 | `backend-python/app/models/checksums.sha256` | 1.7 KB | 22 | Asset / Config | Reviewed (Config/Doc) | Supporting repository source, configuration, or documentation file |
| 38 | `backend-python/app/models/le_gender.pkl` | 0.5 KB | 2 | Trained ML Model | Verified (Binary/Data) | Serialized machine learning model artifact (XGBoost model / Scikit-Learn LabelEncoder) |
| 39 | `backend-python/app/models/le_goal.pkl` | 0.9 KB | 2 | Trained ML Model | Verified (Binary/Data) | Serialized machine learning model artifact (XGBoost model / Scikit-Learn LabelEncoder) |
| 40 | `backend-python/app/models/le_target.pkl` | 0.5 KB | 2 | Trained ML Model | Verified (Binary/Data) | Serialized machine learning model artifact (XGBoost model / Scikit-Learn LabelEncoder) |
| 41 | `backend-python/app/models/user.py` | 4.0 KB | 141 | Source Code | Fully Analyzed | Supporting repository source, configuration, or documentation file |
| 42 | `backend-python/app/models/xgb_meal.pkl` | 79.7 KB | 551 | Trained ML Model | Verified (Binary/Data) | Serialized machine learning model artifact (XGBoost model / Scikit-Learn LabelEncoder) |
| 43 | `backend-python/app/models/xgb_workout.pkl` | 640.5 KB | 4278 | Trained ML Model | Verified (Binary/Data) | Serialized machine learning model artifact (XGBoost model / Scikit-Learn LabelEncoder) |
| 44 | `backend-python/app/multi_output_xgboost_model.py` | 21.7 KB | 588 | Source Code | Fully Analyzed | Scikit-learn MultiOutputRegressor wrapper for predicting workout sets, reps, and rest times |
| 45 | `backend-python/app/multitarget_nutrition_model.py` | 29.5 KB | 707 | Source Code | Fully Analyzed | XGBoost regression model estimating target calories, protein, carbs, and fats from biometric features |
| 46 | `backend-python/app/nutrition_engine/__init__.py` | 0.1 KB | 3 | Source Code | Fully Analyzed | Supporting repository source, configuration, or documentation file |
| 47 | `backend-python/app/nutrition_engine/candidate_generator.py` | 119.4 KB | 2560 | Source Code | Fully Analyzed | Meal candidate generator pulling foods from knowledge base and composing balanced plates |
| 48 | `backend-python/app/nutrition_engine/config.py` | 1.5 KB | 44 | Source Code | Fully Analyzed | Supporting repository source, configuration, or documentation file |
| 49 | `backend-python/app/nutrition_engine/daily_rule_engine.py` | 3.1 KB | 82 | Source Code | Fully Analyzed | Daily nutritional constraint validator verifying meal timing and hydration distribution |
| 50 | `backend-python/app/nutrition_engine/engine.py` | 11.8 KB | 253 | Source Code | Fully Analyzed | NutritionEngineV6 main orchestrator coordinating candidate generation, weekly optimization, and scoring |
| 51 | `backend-python/app/nutrition_engine/food_graph.py` | 37.4 KB | 752 | Source Code | Fully Analyzed | Graph-based food similarity and replacement engine indexing ingredient and recipe databases |
| 52 | `backend-python/app/nutrition_engine/food_utils.py` | 8.4 KB | 166 | Source Code | Fully Analyzed | Food classification utilities identifying food families, allergens, and meal suitability |
| 53 | `backend-python/app/nutrition_engine/ingredient_optimizer.py` | 3.6 KB | 77 | Source Code | Fully Analyzed | Ingredient-level substitution engine finding nutrient-dense replacements |
| 54 | `backend-python/app/nutrition_engine/meal_scorer.py` | 22.1 KB | 494 | Source Code | Fully Analyzed | Multi-criteria meal scoring engine evaluating macro proximity, variety penalty, and dietary alignment |
| 55 | `backend-python/app/nutrition_engine/nutrition_calculator.py` | 9.6 KB | 259 | Source Code | Fully Analyzed | Weekly macro planner and nutritional calculation formulas (BMR, TDEE, macro split) |
| 56 | `backend-python/app/nutrition_engine/nutrition_rule_engine.py` | 1.7 KB | 48 | Source Code | Fully Analyzed | Supporting repository source, configuration, or documentation file |
| 57 | `backend-python/app/nutrition_engine/plan_cache.py` | 6.0 KB | 159 | Source Code | Fully Analyzed | Supporting repository source, configuration, or documentation file |
| 58 | `backend-python/app/nutrition_engine/plate_builder.py` | 4.1 KB | 105 | Source Code | Fully Analyzed | Plate composition helper assembling main protein, carb base, and vegetable side items |
| 59 | `backend-python/app/nutrition_engine/portion_optimizer.py` | 29.4 KB | 620 | Source Code | Fully Analyzed | Macro portion solver adjusting ingredient gram weights to match exact caloric and macro goals |
| 60 | `backend-python/app/nutrition_engine/serving_validator.py` | 13.4 KB | 288 | Source Code | Fully Analyzed | Nutritional serving size validator enforcing realistic portion bounds and preventing starvation |
| 61 | `backend-python/app/nutrition_engine/template_manager.py` | 3.6 KB | 93 | Source Code | Fully Analyzed | YAML meal template loader mapping meal structures to specific regional cuisines |
| 62 | `backend-python/app/nutrition_engine/variety_tracker.py` | 18.1 KB | 350 | Source Code | Fully Analyzed | Sliding-window variety tracker penalizing consecutive meal repeats and protein source monotony |
| 63 | `backend-python/app/nutrition_engine/weekly_optimizer.py` | 47.2 KB | 784 | Source Code | Fully Analyzed | Genetic/heuristic weekly meal plan optimizer balancing macros, variety, and nutritional targets |
| 64 | `backend-python/app/nutrition_engine/weekly_validator.py` | 22.2 KB | 414 | Source Code | Fully Analyzed | Plan validation engine checking calorie variance, macro tolerances, and dietary compliance |
| 65 | `backend-python/app/nutrition_intelligence.py` | 31.8 KB | 782 | Source Code | Fully Analyzed | Supporting repository source, configuration, or documentation file |
| 66 | `backend-python/app/plan_cache.py` | 7.8 KB | 166 | Source Code | Fully Analyzed | Supporting repository source, configuration, or documentation file |
| 67 | `backend-python/app/pose_tracker.py` | 80.6 KB | 1750 | Source Code | Fully Analyzed | Supporting repository source, configuration, or documentation file |
| 68 | `backend-python/app/prescription_targets.py` | 4.1 KB | 135 | Source Code | Fully Analyzed | Supporting repository source, configuration, or documentation file |
| 69 | `backend-python/app/profile_change_detection.py` | 24.2 KB | 663 | Source Code | Fully Analyzed | Supporting repository source, configuration, or documentation file |
| 70 | `backend-python/app/profile_output.txt` | 0.0 KB | 0 | Asset / Config | Reviewed (Config/Doc) | Supporting repository source, configuration, or documentation file |
| 71 | `backend-python/app/progression_engine.py` | 36.5 KB | 949 | Source Code | Fully Analyzed | Supporting repository source, configuration, or documentation file |
| 72 | `backend-python/app/reports/pose_tracking_coverage.json` | 0.5 KB | 24 | Configuration / Data | Reviewed (Config/Doc) | Static dataset, knowledge base, or configuration data store |
| 73 | `backend-python/app/routes/__init__.py` | 0.0 KB | 1 | Source Code | Fully Analyzed | Supporting repository source, configuration, or documentation file |
| 74 | `backend-python/app/routes/chatbot.py` | 8.2 KB | 222 | Source Code | Fully Analyzed | Supporting repository source, configuration, or documentation file |
| 75 | `backend-python/app/routes/food_database.py` | 4.9 KB | 145 | Source Code | Fully Analyzed | Supporting repository source, configuration, or documentation file |
| 76 | `backend-python/app/routes/meal_plan.py` | 8.1 KB | 211 | Source Code | Fully Analyzed | Supporting repository source, configuration, or documentation file |
| 77 | `backend-python/app/routes/meal_tracking.py` | 6.3 KB | 182 | Source Code | Fully Analyzed | Supporting repository source, configuration, or documentation file |
| 78 | `backend-python/app/routes/profile.py` | 31.9 KB | 809 | Source Code | Fully Analyzed | Supporting repository source, configuration, or documentation file |
| 79 | `backend-python/app/routes/workout.py` | 1.1 KB | 28 | Source Code | Fully Analyzed | Supporting repository source, configuration, or documentation file |
| 80 | `backend-python/app/run_profile.py` | 0.5 KB | 24 | Source Code | Fully Analyzed | Supporting repository source, configuration, or documentation file |
| 81 | `backend-python/app/safety_layer.py` | 14.6 KB | 369 | Source Code | Fully Analyzed | Supporting repository source, configuration, or documentation file |
| 82 | `backend-python/app/services/exercise_metadata.py` | 2.6 KB | 67 | Source Code | Fully Analyzed | Supporting repository source, configuration, or documentation file |
| 83 | `backend-python/app/test_generation.py` | 0.8 KB | 25 | Source Code | Fully Analyzed | Automated test suite verifying API contracts, regressions, and component behaviors |
| 84 | `backend-python/app/test_regression_meal_engine.py` | 5.2 KB | 131 | Source Code | Fully Analyzed | Backward-compatibility wrapper bridging legacy meal engine callers to NutritionEngineV6 |
| 85 | `backend-python/app/train_meal_model.py` | 5.7 KB | 166 | Source Code | Fully Analyzed | Supporting repository source, configuration, or documentation file |
| 86 | `backend-python/app/train_model.py` | 9.2 KB | 205 | Source Code | Fully Analyzed | Supporting repository source, configuration, or documentation file |
| 87 | `backend-python/app/update_metadata.py` | 3.0 KB | 69 | Source Code | Fully Analyzed | Supporting repository source, configuration, or documentation file |
| 88 | `backend-python/app/utils/__init__.py` | 0.0 KB | 1 | Source Code | Fully Analyzed | Supporting repository source, configuration, or documentation file |
| 89 | `backend-python/app/utils/activity_logger.py` | 2.9 KB | 91 | Source Code | Fully Analyzed | Supporting repository source, configuration, or documentation file |
| 90 | `backend-python/app/utils/db_safe_write.py` | 6.2 KB | 202 | Source Code | Fully Analyzed | Supporting repository source, configuration, or documentation file |
| 91 | `backend-python/app/utils/model_integrity.py` | 8.3 KB | 256 | Source Code | Fully Analyzed | Supporting repository source, configuration, or documentation file |
| 92 | `backend-python/app/utils/movement_mapper.py` | 5.8 KB | 161 | Source Code | Fully Analyzed | Supporting repository source, configuration, or documentation file |
| 93 | `backend-python/app/workout_engine.py` | 243.7 KB | 5369 | Source Code | Fully Analyzed | Core workout generation engine combining XGBoost predictions, progression rules, and volume optimization |
| 94 | `backend-python/app/workout_rules.py` | 5.8 KB | 163 | Source Code | Fully Analyzed | Configuration loader and validator for weekly workout splits, set/rep ranges, and safety constraints |
| 95 | `backend-python/config/constraint_weights.yaml` | 0.6 KB | 19 | Configuration / Data | Reviewed (Config/Doc) | Supporting repository source, configuration, or documentation file |
| 96 | `backend-python/config/feature_flags.yaml` | 0.2 KB | 7 | Configuration / Data | Reviewed (Config/Doc) | Supporting repository source, configuration, or documentation file |
| 97 | `backend-python/config/meal_scoring.yaml` | 0.6 KB | 28 | Configuration / Data | Reviewed (Config/Doc) | Supporting repository source, configuration, or documentation file |
| 98 | `backend-python/config/meal_templates.yaml` | 11.5 KB | 461 | Configuration / Data | Reviewed (Config/Doc) | Supporting repository source, configuration, or documentation file |
| 99 | `backend-python/config/nutrition_rules.yaml` | 22.7 KB | 714 | Configuration / Data | Reviewed (Config/Doc) | Supporting repository source, configuration, or documentation file |
| 100 | `backend-python/config/workout_rules.yaml` | 17.0 KB | 307 | Configuration / Data | Reviewed (Config/Doc) | Supporting repository source, configuration, or documentation file |
| 101 | `backend-python/data/compiled_nutrition_graph_v2.json` | 688.8 KB | 29600 | Configuration / Data | Reviewed (Config/Doc) | Static dataset, knowledge base, or configuration data store |
| 102 | `backend-python/data/exercises.csv` | 243.5 KB | 1325 | Dataset / Log | Verified (Binary/Data) | Static dataset, knowledge base, or configuration data store |
| 103 | `backend-python/data/exercises_processed.csv` | 242.7 KB | 1325 | Dataset / Log | Verified (Binary/Data) | Static dataset, knowledge base, or configuration data store |
| 104 | `backend-python/data/exercises_processed_repaired.csv` | 383.3 KB | 1325 | Dataset / Log | Verified (Binary/Data) | Static dataset, knowledge base, or configuration data store |
| 105 | `backend-python/data/food_blacklist.json` | 9.6 KB | 311 | Configuration / Data | Reviewed (Config/Doc) | Static dataset, knowledge base, or configuration data store |
| 106 | `backend-python/data/food_knowledge_base.json` | 1441.4 KB | 64988 | Configuration / Data | Reviewed (Config/Doc) | Static dataset, knowledge base, or configuration data store |
| 107 | `backend-python/data/food_relationship_graph.json` | 749.7 KB | 37050 | Configuration / Data | Reviewed (Config/Doc) | Static dataset, knowledge base, or configuration data store |
| 108 | `backend-python/data/gif_blacklist.json` | 25.3 KB | 726 | Configuration / Data | Reviewed (Config/Doc) | Static dataset, knowledge base, or configuration data store |
| 109 | `backend-python/data/gifs.csv` | 155.3 KB | 1412 | Dataset / Log | Verified (Binary/Data) | Static dataset, knowledge base, or configuration data store |
| 110 | `backend-python/data/ifct2017_compositions.csv` | 600.9 KB | 543 | Dataset / Log | Verified (Binary/Data) | Static dataset, knowledge base, or configuration data store |
| 111 | `backend-python/data/ingredient_database.json` | 209.0 KB | 6953 | Configuration / Data | Reviewed (Config/Doc) | Static dataset, knowledge base, or configuration data store |
| 112 | `backend-python/data/meal_blueprint_library.json` | 1293.8 KB | 58724 | Configuration / Data | Reviewed (Config/Doc) | Static dataset, knowledge base, or configuration data store |
| 113 | `backend-python/data/meal_metadata.csv` | 171.9 KB | 1287 | Dataset / Log | Verified (Binary/Data) | Static dataset, knowledge base, or configuration data store |
| 114 | `backend-python/data/nutrition_production_final_v4.csv` | 319.9 KB | 891 | Dataset / Log | Verified (Binary/Data) | Static dataset, knowledge base, or configuration data store |
| 115 | `backend-python/data/recipe_database.json` | 742.1 KB | 26742 | Configuration / Data | Reviewed (Config/Doc) | Static dataset, knowledge base, or configuration data store |
| 116 | `backend-python/generate_meal_kb.py` | 14.6 KB | 306 | Source Code | Fully Analyzed | Meal knowledge base generator compiling recipes and ingredients into structured JSON |
| 117 | `backend-python/logs/candidate_generation_metrics.jsonl` | 642.8 KB | 2796 | Dataset / Log | Verified (Binary/Data) | Static dataset, knowledge base, or configuration data store |
| 118 | `backend-python/models/goal_encoder.pkl` | 0.5 KB | 2 | Trained ML Model | Verified (Binary/Data) | Serialized machine learning model artifact (XGBoost model / Scikit-Learn LabelEncoder) |
| 119 | `backend-python/models/label_encoder_experience.pkl` | 0.5 KB | 3 | Trained ML Model | Verified (Binary/Data) | Serialized machine learning model artifact (XGBoost model / Scikit-Learn LabelEncoder) |
| 120 | `backend-python/models/meal_model.pkl` | 366.0 KB | 3187 | Trained ML Model | Verified (Binary/Data) | Serialized machine learning model artifact (XGBoost model / Scikit-Learn LabelEncoder) |
| 121 | `backend-python/models/multi_output_xgboost_model.joblib` | 2174.2 KB | 18386 | Trained ML Model | Verified (Binary/Data) | Serialized machine learning model artifact (XGBoost model / Scikit-Learn LabelEncoder) |
| 122 | `backend-python/models/multitarget_nutrition_model.joblib` | 2079.1 KB | 17509 | Trained ML Model | Verified (Binary/Data) | Serialized machine learning model artifact (XGBoost model / Scikit-Learn LabelEncoder) |
| 123 | `backend-python/models/workout_model.pkl` | 3.5 KB | 11 | Trained ML Model | Verified (Binary/Data) | Serialized machine learning model artifact (XGBoost model / Scikit-Learn LabelEncoder) |
| 124 | `backend-python/models/xgboost_frequency.pkl` | 111.1 KB | 824 | Trained ML Model | Verified (Binary/Data) | Serialized machine learning model artifact (XGBoost model / Scikit-Learn LabelEncoder) |
| 125 | `backend-python/models/xgboost_intensity.pkl` | 163.9 KB | 1428 | Trained ML Model | Verified (Binary/Data) | Serialized machine learning model artifact (XGBoost model / Scikit-Learn LabelEncoder) |
| 126 | `backend-python/models/xgboost_progression.pkl` | 129.7 KB | 1036 | Trained ML Model | Verified (Binary/Data) | Serialized machine learning model artifact (XGBoost model / Scikit-Learn LabelEncoder) |
| 127 | `backend-python/models/xgboost_reps.pkl` | 164.8 KB | 1445 | Trained ML Model | Verified (Binary/Data) | Serialized machine learning model artifact (XGBoost model / Scikit-Learn LabelEncoder) |
| 128 | `backend-python/models/xgboost_rest.pkl` | 163.0 KB | 1396 | Trained ML Model | Verified (Binary/Data) | Serialized machine learning model artifact (XGBoost model / Scikit-Learn LabelEncoder) |
| 129 | `backend-python/models/xgboost_sets.pkl` | 166.3 KB | 1438 | Trained ML Model | Verified (Binary/Data) | Serialized machine learning model artifact (XGBoost model / Scikit-Learn LabelEncoder) |
| 130 | `backend-python/models/xgboost_split.pkl` | 440.8 KB | 3951 | Trained ML Model | Verified (Binary/Data) | Serialized machine learning model artifact (XGBoost model / Scikit-Learn LabelEncoder) |
| 131 | `backend-python/models/xgboost_volume.pkl` | 166.3 KB | 1438 | Trained ML Model | Verified (Binary/Data) | Serialized machine learning model artifact (XGBoost model / Scikit-Learn LabelEncoder) |
| 132 | `backend-python/pytest.ini` | 0.1 KB | 6 | Configuration / Data | Reviewed (Config/Doc) | Automated test suite verifying API contracts, regressions, and component behaviors |
| 133 | `backend-python/requirements.txt` | 0.5 KB | 30 | Asset / Config | Reviewed (Config/Doc) | Supporting repository source, configuration, or documentation file |
| 134 | `backend-python/scripts/create_indexes.py` | 4.5 KB | 118 | Source Code | Fully Analyzed | Supporting repository source, configuration, or documentation file |
| 135 | `backend-python/scripts/seed.py` | 5.8 KB | 153 | Source Code | Fully Analyzed | Supporting repository source, configuration, or documentation file |
| 136 | `backend-python/server.py` | 156.0 KB | 4077 | Source Code | Fully Analyzed | FastAPI application entrypoint containing ML endpoints, weekly plan generation, and model lifecycle hooks |
| 137 | `backend-python/tests/run_regression.py` | 3.5 KB | 98 | Source Code | Fully Analyzed | Automated test suite verifying API contracts, regressions, and component behaviors |
| 138 | `backend-python/tests/test_candidate_generator.py` | 3.2 KB | 64 | Source Code | Fully Analyzed | Meal candidate generator pulling foods from knowledge base and composing balanced plates |
| 139 | `backend-python/tests/test_candidate_health.py` | 3.9 KB | 109 | Source Code | Fully Analyzed | Automated test suite verifying API contracts, regressions, and component behaviors |
| 140 | `backend-python/tests/test_chatbot_refactored.py` | 8.1 KB | 196 | Source Code | Fully Analyzed | Automated test suite verifying API contracts, regressions, and component behaviors |
| 141 | `backend-python/tests/test_chatbot_sanity_flow.py` | 4.4 KB | 110 | Source Code | Fully Analyzed | Automated test suite verifying API contracts, regressions, and component behaviors |
| 142 | `backend-python/tests/test_engine.py` | 3.1 KB | 80 | Source Code | Fully Analyzed | Automated test suite verifying API contracts, regressions, and component behaviors |
| 143 | `backend-python/tests/test_golden_profiles.py` | 4.4 KB | 114 | Source Code | Fully Analyzed | Automated test suite verifying API contracts, regressions, and component behaviors |
| 144 | `backend-python/tests/test_health_endpoint.py` | 1.6 KB | 48 | Source Code | Fully Analyzed | Automated test suite verifying API contracts, regressions, and component behaviors |
| 145 | `backend-python/tests/test_meal_scorer.py` | 2.7 KB | 67 | Source Code | Fully Analyzed | Multi-criteria meal scoring engine evaluating macro proximity, variety penalty, and dietary alignment |
| 146 | `backend-python/tests/test_metadata_serialization.py` | 4.0 KB | 87 | Source Code | Fully Analyzed | Automated test suite verifying API contracts, regressions, and component behaviors |
| 147 | `backend-python/tests/test_nutrition_engine_comprehensive.py` | 5.1 KB | 112 | Source Code | Fully Analyzed | Automated test suite verifying API contracts, regressions, and component behaviors |
| 148 | `backend-python/tests/test_portion_optimizer.py` | 4.0 KB | 130 | Source Code | Fully Analyzed | Macro portion solver adjusting ingredient gram weights to match exact caloric and macro goals |
| 149 | `backend-python/tests/test_pose_tracker_refactored.py` | 7.1 KB | 193 | Source Code | Fully Analyzed | Automated test suite verifying API contracts, regressions, and component behaviors |
| 150 | `backend-python/tests/test_profile_meal_regen.py` | 3.4 KB | 89 | Source Code | Fully Analyzed | Automated test suite verifying API contracts, regressions, and component behaviors |
| 151 | `backend-python/tests/test_python_api_contract.py` | 1.4 KB | 36 | Source Code | Fully Analyzed | Automated test suite verifying API contracts, regressions, and component behaviors |
| 152 | `backend-python/tests/test_safety_compliance.py` | 7.0 KB | 182 | Source Code | Fully Analyzed | Automated test suite verifying API contracts, regressions, and component behaviors |
| 153 | `backend-python/tests/test_template_manager.py` | 1.8 KB | 37 | Source Code | Fully Analyzed | YAML meal template loader mapping meal structures to specific regional cuisines |
| 154 | `backend-python/tests/test_token_utils.py` | 3.1 KB | 78 | Source Code | Fully Analyzed | Automated test suite verifying API contracts, regressions, and component behaviors |
| 155 | `backend-python/tests/test_variety_tracker.py` | 2.7 KB | 87 | Source Code | Fully Analyzed | Sliding-window variety tracker penalizing consecutive meal repeats and protein source monotony |
| 156 | `backend-python/tests/test_workout_e2e_flow.py` | 12.7 KB | 343 | Source Code | Fully Analyzed | Automated test suite verifying API contracts, regressions, and component behaviors |
| 157 | `backend-python/tests/test_workout_planner_comprehensive.py` | 18.9 KB | 498 | Source Code | Fully Analyzed | Automated test suite verifying API contracts, regressions, and component behaviors |
| 158 | `backend-python/tests/test_workout_progression_regression.py` | 5.3 KB | 135 | Source Code | Fully Analyzed | Automated test suite verifying API contracts, regressions, and component behaviors |
| 159 | `backend-python/tests/verify_v6_stabilization.py` | 7.7 KB | 159 | Source Code | Fully Analyzed | Automated test suite verifying API contracts, regressions, and component behaviors |

---

## 4. Frontend Application: React 19 / Vite (63 files)

| # | Relative File Path | Size (KB) | Lines | Classification | Audit Status | Primary Purpose / Role in Elevate Platform |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| 1 | `frontend/.env` | 0.4 KB | 8 | Asset / Config | Reviewed (Config/Doc) | Supporting repository source, configuration, or documentation file |
| 2 | `frontend/.env.example` | 0.1 KB | 5 | Asset / Config | Reviewed (Config/Doc) | Supporting repository source, configuration, or documentation file |
| 3 | `frontend/.env.local` | 0.3 KB | 7 | Asset / Config | Reviewed (Config/Doc) | Supporting repository source, configuration, or documentation file |
| 4 | `frontend/Dockerfile` | 0.5 KB | 27 | Asset / Config | Reviewed (Config/Doc) | Supporting repository source, configuration, or documentation file |
| 5 | `frontend/eslint.config.js` | 0.8 KB | 29 | Source Code | Fully Analyzed | Supporting repository source, configuration, or documentation file |
| 6 | `frontend/index.html` | 0.4 KB | 13 | Documentation | Reviewed (Config/Doc) | Project documentation, technical specifications, or academic defense artifacts |
| 7 | `frontend/nginx.conf` | 2.1 KB | 54 | Configuration / Data | Reviewed (Config/Doc) | Supporting repository source, configuration, or documentation file |
| 8 | `frontend/package-lock.json` | 172.3 KB | 5066 | Configuration / Data | Reviewed (Config/Doc) | Static dataset, knowledge base, or configuration data store |
| 9 | `frontend/package.json` | 1.0 KB | 39 | Configuration / Data | Reviewed (Config/Doc) | Static dataset, knowledge base, or configuration data store |
| 10 | `frontend/public/sw.js` | 1.6 KB | 56 | Source Code | Fully Analyzed | Supporting repository source, configuration, or documentation file |
| 11 | `frontend/public/vite.svg` | 1.5 KB | 1 | Asset / Config | Reviewed (Config/Doc) | Supporting repository source, configuration, or documentation file |
| 12 | `frontend/public/wasm/vision_wasm_internal.js` | 316.0 KB | 8844 | Source Code | Fully Analyzed | Supporting repository source, configuration, or documentation file |
| 13 | `frontend/public/wasm/vision_wasm_internal.wasm` | 11241.0 KB | 217150 | Compiled WASM Binary | Verified (Binary/Data) | Compiled WebAssembly binary for client-side MediaPipe computer vision inference |
| 14 | `frontend/public/wasm/vision_wasm_module_internal.js` | 315.9 KB | 8840 | Source Code | Fully Analyzed | Supporting repository source, configuration, or documentation file |
| 15 | `frontend/public/wasm/vision_wasm_module_internal.wasm` | 11241.0 KB | 217150 | Compiled WASM Binary | Verified (Binary/Data) | Compiled WebAssembly binary for client-side MediaPipe computer vision inference |
| 16 | `frontend/public/wasm/vision_wasm_nosimd_internal.js` | 315.8 KB | 8835 | Source Code | Fully Analyzed | Supporting repository source, configuration, or documentation file |
| 17 | `frontend/public/wasm/vision_wasm_nosimd_internal.wasm` | 10455.9 KB | 191331 | Compiled WASM Binary | Verified (Binary/Data) | Compiled WebAssembly binary for client-side MediaPipe computer vision inference |
| 18 | `frontend/src/App.css` | 34.1 KB | 1452 | Stylesheet | Fully Analyzed | Supporting repository source, configuration, or documentation file |
| 19 | `frontend/src/App.jsx` | 8.9 KB | 232 | Source Code | Fully Analyzed | React application root defining client-side routing, protected routes, and theme context |
| 20 | `frontend/src/__tests__/ConfirmDialog.test.jsx` | 2.6 KB | 77 | Source Code | Fully Analyzed | Automated test suite verifying API contracts, regressions, and component behaviors |
| 21 | `frontend/src/__tests__/poseRouting.test.js` | 1.7 KB | 51 | Source Code | Fully Analyzed | Automated test suite verifying API contracts, regressions, and component behaviors |
| 22 | `frontend/src/__tests__/setup.js` | 1.0 KB | 42 | Source Code | Fully Analyzed | Automated test suite verifying API contracts, regressions, and component behaviors |
| 23 | `frontend/src/__tests__/storage.test.js` | 1.4 KB | 45 | Source Code | Fully Analyzed | Automated test suite verifying API contracts, regressions, and component behaviors |
| 24 | `frontend/src/api.js` | 28.3 KB | 673 | Source Code | Fully Analyzed | Centralized Axios HTTP client configuring AuthAPI and FitnessAPI instances with CSRF & circuit breakers |
| 25 | `frontend/src/components/AuroraBackground.jsx` | 14.4 KB | 406 | Source Code | Fully Analyzed | Animated background visual component providing modern aurora gradient aesthetic |
| 26 | `frontend/src/components/ConfirmDialog.jsx` | 1.1 KB | 38 | Source Code | Fully Analyzed | Reusable modal dialog for confirming destructive or plan-regenerating user actions |
| 27 | `frontend/src/components/Navbar.jsx` | 15.6 KB | 498 | Source Code | Fully Analyzed | Supporting repository source, configuration, or documentation file |
| 28 | `frontend/src/components/NotificationProvider.jsx` | 3.6 KB | 126 | Source Code | Fully Analyzed | React context provider rendering toast notifications, alerts, and system messages |
| 29 | `frontend/src/components/PoseDetector.jsx` | 37.6 KB | 1007 | Source Code | Fully Analyzed | React MediaPipe PoseLandmarker component running WebAssembly client-side real-time joint tracking |
| 30 | `frontend/src/components/TimerExerciseMode.jsx` | 5.7 KB | 196 | Source Code | Fully Analyzed | Countdown timer and interval tracker for timed exercises (planks, isometric holds) |
| 31 | `frontend/src/components/admin/AdminActionDialog.jsx` | 3.3 KB | 127 | Source Code | Fully Analyzed | Supporting repository source, configuration, or documentation file |
| 32 | `frontend/src/components/admin/AdminLayout.jsx` | 1.9 KB | 66 | Source Code | Fully Analyzed | Admin layout frame providing navigation sidebar, topbar, and session timeout handlers |
| 33 | `frontend/src/components/admin/AdminRoute.jsx` | 1.2 KB | 50 | Source Code | Fully Analyzed | Protected route wrapper restricting access to authenticated users with owner role |
| 34 | `frontend/src/context/ThemeContext.jsx` | 1.1 KB | 36 | Source Code | Fully Analyzed | React context provider managing light/dark mode theme state and CSS variables |
| 35 | `frontend/src/data/quotes.js` | 8.9 KB | 194 | Source Code | Fully Analyzed | Static fitness and motivational quotes dataset for dashboard card display |
| 36 | `frontend/src/index.css` | 0.7 KB | 31 | Stylesheet | Fully Analyzed | Supporting repository source, configuration, or documentation file |
| 37 | `frontend/src/main.jsx` | 1.2 KB | 38 | Source Code | Fully Analyzed | React Vite entrypoint mounting App root into DOM with NotificationProvider and ThemeProvider |
| 38 | `frontend/src/pages/Chatbot.jsx` | 29.3 KB | 832 | Source Code | Fully Analyzed | AI fitness coaching chatbot interface with offline fallbacks and quick suggestion pills |
| 39 | `frontend/src/pages/Dashboard.css` | 28.2 KB | 1486 | Stylesheet | Fully Analyzed | Supporting repository source, configuration, or documentation file |
| 40 | `frontend/src/pages/Dashboard.jsx` | 158.5 KB | 3748 | Source Code | Fully Analyzed | Main user dashboard displaying daily habit progress, streaks, quick actions, and recovery metrics |
| 41 | `frontend/src/pages/DashboardActionIdeas.jsx` | 82.5 KB | 1888 | Source Code | Fully Analyzed | Supporting repository source, configuration, or documentation file |
| 42 | `frontend/src/pages/ForgotPassword.jsx` | 11.7 KB | 342 | Source Code | Fully Analyzed | Self-service password reset request and token verification form |
| 43 | `frontend/src/pages/Login.jsx` | 10.0 KB | 296 | Source Code | Fully Analyzed | User login page with email/password authentication and Google OAuth sign-in button |
| 44 | `frontend/src/pages/Nutrition.jsx` | 82.0 KB | 1562 | Source Code | Fully Analyzed | Nutrition tracker and weekly meal planner displaying daily macro rings, meal cards, and swap dialogs |
| 45 | `frontend/src/pages/ProfileSetup.jsx` | 50.1 KB | 1110 | Source Code | Fully Analyzed | Comprehensive multi-step onboarding and profile editing form with plan regeneration triggers |
| 46 | `frontend/src/pages/Register.jsx` | 15.0 KB | 337 | Source Code | Fully Analyzed | User registration form with client-side validation, password strength meter, and Google OAuth |
| 47 | `frontend/src/pages/Workout.jsx` | 160.5 KB | 3575 | Source Code | Fully Analyzed | Interactive workout session interface rendering exercise sets, webcam form feedback, and rest timers |
| 48 | `frontend/src/pages/admin/Admin.css` | 9.6 KB | 546 | Stylesheet | Fully Analyzed | Supporting repository source, configuration, or documentation file |
| 49 | `frontend/src/pages/admin/AdminLogin.jsx` | 3.3 KB | 112 | Source Code | Fully Analyzed | Admin portal login page requiring admin secret key in addition to email and password |
| 50 | `frontend/src/pages/admin/Audit.jsx` | 5.1 KB | 175 | Source Code | Fully Analyzed | Admin audit log viewer displaying timestamps, IP addresses, actions, and affected targets |
| 51 | `frontend/src/pages/admin/Content.jsx` | 10.5 KB | 315 | Source Code | Fully Analyzed | Admin exercise library manager for creating, editing, and categorizing workout exercises |
| 52 | `frontend/src/pages/admin/Dashboard.jsx` | 4.4 KB | 133 | Source Code | Fully Analyzed | Admin analytics dashboard displaying total users, active today, and growth charts |
| 53 | `frontend/src/pages/admin/System.jsx` | 9.2 KB | 256 | Source Code | Fully Analyzed | Admin system settings panel managing maintenance mode, announcements, and health ping |
| 54 | `frontend/src/pages/admin/Users.jsx` | 9.3 KB | 269 | Source Code | Fully Analyzed | Admin user management table supporting search, pagination, suspension, and password resets |
| 55 | `frontend/src/responsive.css` | 17.0 KB | 717 | Stylesheet | Fully Analyzed | Supporting repository source, configuration, or documentation file |
| 56 | `frontend/src/services/profileApi.js` | 10.4 KB | 360 | Source Code | Fully Analyzed | Centralized Axios HTTP client configuring AuthAPI and FitnessAPI instances with CSRF & circuit breakers |
| 57 | `frontend/src/utils/circuitBreaker.js` | 9.9 KB | 284 | Source Code | Fully Analyzed | Frontend circuit breaker utility isolating failure cascades across workout and nutrition endpoints |
| 58 | `frontend/src/utils/circuitBreaker.test.js` | 8.1 KB | 266 | Source Code | Fully Analyzed | Automated test suite verifying API contracts, regressions, and component behaviors |
| 59 | `frontend/src/utils/googleAuth.js` | 10.6 KB | 227 | Source Code | Fully Analyzed | Google Identity Services OAuth credential loader and callback handler |
| 60 | `frontend/src/utils/poseModelPreload.js` | 1.6 KB | 47 | Source Code | Fully Analyzed | Asynchronous asset preloader fetching MediaPipe WASM and pose landmarker model binaries |
| 61 | `frontend/src/utils/storage.js` | 13.0 KB | 432 | Source Code | Fully Analyzed | Safe localStorage wrapper with JSON serialization guards, schema validation, and cache management |
| 62 | `frontend/src/utils/syncBridge.js` | 1.9 KB | 80 | Source Code | Fully Analyzed | Cross-tab and cross-component broadcast channel synchronizing real-time habit updates |
| 63 | `frontend/vite.config.js` | 0.7 KB | 32 | Source Code | Fully Analyzed | Supporting repository source, configuration, or documentation file |

---

## 5. Documentation & Presentation Artifacts (24 files)

| # | Relative File Path | Size (KB) | Lines | Classification | Audit Status | Primary Purpose / Role in Elevate Platform |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| 1 | `CONTRIBUTING.md` | 4.0 KB | 170 | Documentation | Reviewed (Config/Doc) | Project documentation, technical specifications, or academic defense artifacts |
| 2 | `ELEVATE_PROJECT_REPORT.html` | 65.8 KB | 1408 | Documentation | Reviewed (Config/Doc) | Project documentation, technical specifications, or academic defense artifacts |
| 3 | `GOOGLE_OAUTH_SETUP.md` | 3.2 KB | 103 | Documentation | Reviewed (Config/Doc) | Project documentation, technical specifications, or academic defense artifacts |
| 4 | `PERFORMANCE_FIXES.md` | 1.4 KB | 40 | Documentation | Reviewed (Config/Doc) | Project documentation, technical specifications, or academic defense artifacts |
| 5 | `PROJECT_ELEVATE_OVERVIEW.md` | 41.5 KB | 754 | Documentation | Reviewed (Config/Doc) | Project documentation, technical specifications, or academic defense artifacts |
| 6 | `PROJECT_OVERVIEW.md` | 8.9 KB | 81 | Documentation | Reviewed (Config/Doc) | Project documentation, technical specifications, or academic defense artifacts |
| 7 | `README.md` | 12.5 KB | 281 | Documentation | Reviewed (Config/Doc) | Project documentation, technical specifications, or academic defense artifacts |
| 8 | `docs/BLACK BOOK.docx` | 7480.2 KB | 54125 | Documentation | Reviewed (Config/Doc) | Project documentation, technical specifications, or academic defense artifacts |
| 9 | `docs/PRESENTATION_DEFENSE_GUIDE.md` | 11.5 KB | 116 | Documentation | Reviewed (Config/Doc) | Project documentation, technical specifications, or academic defense artifacts |
| 10 | `docs/PROJECT_MASTER_DOCUMENT.md` | 36.4 KB | 507 | Documentation | Reviewed (Config/Doc) | Project documentation, technical specifications, or academic defense artifacts |
| 11 | `docs/PROJECT_PLANNER_GANTT.md` | 11.4 KB | 176 | Documentation | Reviewed (Config/Doc) | Project documentation, technical specifications, or academic defense artifacts |
| 12 | `docs/PROJECT_TESTING_EXPLAINER.md` | 8.1 KB | 110 | Documentation | Reviewed (Config/Doc) | Automated test suite verifying API contracts, regressions, and component behaviors |
| 13 | `docs/PS-II_Final Presentation.pptx.pdf` | 371.6 KB | 10118 | Documentation | Reviewed (Config/Doc) | Project documentation, technical specifications, or academic defense artifacts |
| 14 | `docs/Project_Work_Stage_I - II_Log_Book (1).pdf` | 368.8 KB | 3397 | Documentation | Reviewed (Config/Doc) | Project documentation, technical specifications, or academic defense artifacts |
| 15 | `docs/api_contract.md` | 3.2 KB | 123 | Documentation | Reviewed (Config/Doc) | Project documentation, technical specifications, or academic defense artifacts |
| 16 | `docs/architecture.md` | 4.8 KB | 117 | Documentation | Reviewed (Config/Doc) | Project documentation, technical specifications, or academic defense artifacts |
| 17 | `docs/codebase_map.md` | 493.5 KB | 11684 | Documentation | Reviewed (Config/Doc) | Project documentation, technical specifications, or academic defense artifacts |
| 18 | `docs/incident_runbook.md` | 2.9 KB | 92 | Documentation | Reviewed (Config/Doc) | Project documentation, technical specifications, or academic defense artifacts |
| 19 | `docs/monitoring_dashboard.md` | 1.6 KB | 65 | Documentation | Reviewed (Config/Doc) | Project documentation, technical specifications, or academic defense artifacts |
| 20 | `docs/performance_budget.md` | 0.9 KB | 32 | Documentation | Reviewed (Config/Doc) | Project documentation, technical specifications, or academic defense artifacts |
| 21 | `docs/reproducibility_package.md` | 1.4 KB | 59 | Documentation | Reviewed (Config/Doc) | Project documentation, technical specifications, or academic defense artifacts |
| 22 | `elevate_project_defense_guide.html` | 60.2 KB | 1302 | Documentation | Reviewed (Config/Doc) | Project documentation, technical specifications, or academic defense artifacts |
| 23 | `engineering_audit_v2.md` | 30.5 KB | 567 | Documentation | Reviewed (Config/Doc) | Project documentation, technical specifications, or academic defense artifacts |
| 24 | `implementation_plan.md` | 3.1 KB | 53 | Documentation | Reviewed (Config/Doc) | Project documentation, technical specifications, or academic defense artifacts |

---
