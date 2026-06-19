"""
BUG-P1 Router Stub: app/routes/workout.py

Migration target for POST /workout, POST /workout/async,
GET /workout/status/{job_id}, POST /workout/cache/invalidate
currently defined at server.py:1620-1823.

STATUS: Ready for migration. Steps:
1. Move WorkoutProfileRequest model here (or import from app.models.requests)
2. Move _WorkoutRateLimiter class and _WORKOUT_RATE_LIMITER instance here
3. Move all workout route handlers here (change @app.post → @router.post)
4. In server.py: include this router, remove the @app.post/@app.get handlers

Dependencies to resolve before migrating:
- _rate_limit_key()  → move to app.utils.rate_limit
- _model_to_dict()   → move to app.utils.serialization
- _api_success()     → move to app.utils.responses
- get_workout_engine → already in app.workout_engine

Until migration is complete, the routes live in server.py.
See docs/architecture.md §Modularization Roadmap for the full plan.
"""

from fastapi import APIRouter

router = APIRouter(tags=["workout"])

# Placeholder — actual endpoints registered in server.py until migration complete.
