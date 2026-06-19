# Elevate Backend Architecture Decisions

> **Location:** `docs/architecture.md`
> **Scope:** Canonical decisions for the Python backend services.

---

## BUG-P2: Meal Engine Canonical Choice

### Decision

The **`DeterministicMealEngine`** (`backend-python/app/deterministic_meal_engine.py`) is the **canonical meal planning engine** as of April 2026.

| Engine | Status | Notes |
|--------|--------|-------|
| `DeterministicMealEngine` | ✅ **Primary** | Rule-based, reproducible, timezone-aware (IST), handles all dietary restrictions |
| `MealEngine` (`meal_engine.py`) | ⚠️ Deprecated | Legacy engine; kept for backward compatibility only — do not add features here |
| `MLService.recommend_meals` (`nutrition_intelligence.py`) | 🔴 Deprecated | ML-based; trained on synthetic data only (see BUG-P3); marked DEPRECATED in module docstring |

### Rationale

- `DeterministicMealEngine` is reliable, testable, and yields consistent output — critical for user trust.
- The ML engine was trained on `np.random` synthetic data (see BUG-P3) and has no real predictive value.
- Maintaining three engines creates confusion about which is authoritative and duplicates calorie/macro calculation logic.

### Migration Path

1. All new meal-related endpoints **must** import from `deterministic_meal_engine.py`.
2. `meal_engine.py` — mark route handlers that still import it with a `# DEPRECATED: migrate to DeterministicMealEngine` comment. Remove in the next major version.
3. `MLService.recommend_meals` — already marked DEPRECATED in the module docstring; safe to remove when `nutrition_intelligence.py` is fully sunset.

---

## BUG-P3: ML Models Are Demonstration-Only

### Decision

The machine learning models in `backend-python/app/train_model.py` and `train_meal_model.py` are **demonstration-only** and **must not be presented to users as personalised recommendations**.

### Why

Both models are trained with `numpy.random` synthetic data:

```python
# train_model.py (example)
X = np.random.rand(1000, 8)
y = np.random.randint(0, 5, 1000)
```

This means:
- Predictions are uncorrelated with real user behaviour.
- All users receive effectively random exercise/meal suggestions from these models.
- The models only prove that the pipeline (train → serialize → load → infer) works end-to-end.

### What To Do

| Context | Action |
|---------|--------|
| Development / demo | ✅ Keep as-is — demonstrates architecture |
| Production with real users | ⛔ Must be replaced with models trained on consented real data |
| Documentation / UI | Label any ML-driven suggestion as _"AI-powered (beta)"_ with a disclaimer |

### Production Roadmap (when ready)

1. Implement an opt-in data collection pipeline.
2. Store anonymised exercise completion + meal adherence data with user consent.
3. Re-train models on real data; version checkpoints with SHA-256 checksums (see `app/utils/model_integrity.py`).
4. A/B test the real model against the deterministic engine before full rollout.

---

## Server Modularisation (BUG-P1)

`backend-python/server.py` is currently ~2990 lines and is being split incrementally.

### Current Status

| File | Status | Lines |
|------|--------|-------|
| `app/routes/profile.py` | ✅ Live — routes moved | ~300 |
| `app/routes/food_database.py` | ✅ Live — routes moved | ~100 |
| `app/routes/meal_tracking.py` | ✅ Live — routes moved | ~200 |
| `app/routes/chatbot.py` | 🟡 Stub created — migration docs inside | 30 |
| `app/routes/workout.py` | 🟡 Stub created — migration docs inside | 30 |
| `server.py` remaining | 🔴 Still large — all routes not yet migrated | ~2300 |

### Proposed Final Structure

```
backend-python/
  app/
    routes/
      chatbot.py     ← /api/chat (stub ready — see migration notes in file)
      workout.py     ← /workout, /workout/async (stub ready)
      nutrition.py   ← /nutrition, /api/weekly-plan, /api/swap-* (to create)
      profile.py     ← ✅ already migrated
      food_database.py ← ✅ already migrated
    models/
      pydantic_models.py  ← all Pydantic request/response models
    utils/
      responses.py    ← _api_success() helper (to extract from server.py)
      rate_limit.py   ← _rate_limit_key(), _WorkoutRateLimiter (to extract)
    circuit_breaker.py  ← ✅ implemented (ARCH-7)
  server.py           ← thin entry point: imports routers, adds middleware
```

### Migration Ordering

Split one router group at a time (smallest first):
1. `chatbot.py` — depends only on `gemini_service` + `_api_success` helper
2. `workout.py` — depends on `workout_engine` + rate limiter
3. `nutrition.py` — depends on `meal_engine` + swap logic
4. Extract shared utils (`_api_success`, `_rate_limit_key`) before step 1

Each router must be covered by at least one pytest test before the
corresponding code is deleted from `server.py`.

