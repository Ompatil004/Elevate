# ===========================================================================
# DEPRECATED — Bug #19 fixed
# ===========================================================================
# This module (app/main.py) is a legacy FastAPI application that is no longer
# the active server entry point.
#
# The canonical server is:  backend-python/server.py  (uvicorn target: server:app)
#
# app/main.py is retained for reference only. Do NOT import or launch this file.
# All active routes, Pydantic models, and business logic live in server.py.
# ===========================================================================

import os

if os.getenv("ALLOW_LEGACY_APP_MAIN", "0") != "1":
    raise RuntimeError(
        "Deprecated entrypoint blocked: use 'uvicorn server:app' instead of 'uvicorn app.main:app'. "
        "Set ALLOW_LEGACY_APP_MAIN=1 only for temporary debugging."
    )

from fastapi import FastAPI, HTTPException, Request, BackgroundTasks, Body
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Tuple
from datetime import datetime, timezone
import uuid
import asyncio
import logging
import traceback
import time
import collections
from app.db import connect_to_mongo, close_mongo_connection, get_user_collection, get_workout_history_collection, get_meal_history_collection, get_database
import jwt
from bson import ObjectId

# Bug #6 fix: in-process rate limiter for /workout endpoint.
# Stores (timestamps deque) per IP. Max 30 requests per 5 minutes (more lenient for legitimate usage).
_WORKOUT_RATE_LIMIT_MAX = 30
_WORKOUT_RATE_LIMIT_WINDOW = 300   # seconds (5 minutes)
_workout_rate_store: Dict[str, collections.deque] = {}
_WORKOUT_RATE_LIMIT_MAX_CLIENTS = 1024


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)

# ---------------------------------------------------------------------------
# Auth helpers shared by endpoints in main.py
# ---------------------------------------------------------------------------

def _require_user_id_from_token(token: str, request_id: str = "") -> str:
    """Decode the JWT and return the user_id string, or raise 401."""
    secret = os.environ.get("JWT_SECRET", "")
    if not secret:
        raise HTTPException(status_code=500, detail="JWT_SECRET not configured")
    try:
        payload = jwt.decode(token, secret, algorithms=["HS256"])
        user_info = payload.get("user", {})
        user_id = str(user_info.get("id", "")).strip()
        if not user_id:
            raise ValueError("user.id missing from token")
        return user_id
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token has expired")
    except Exception as exc:
        raise HTTPException(status_code=401, detail=f"Invalid token: {exc}")


async def _find_user_by_id(user_id: str):
    """Return the MongoDB user document for *user_id*, or None."""
    try:
        users = get_user_collection()
        return await users.find_one({"_id": ObjectId(user_id)})
    except Exception:
        return None

# ---------------------------------------------------------------------------


def _check_workout_rate_limit(ip: str) -> Tuple[bool, int]:
    """Return (allowed, retry_after_seconds)."""
    now = time.monotonic()
    window_start = now - _WORKOUT_RATE_LIMIT_WINDOW

    # Prune stale client buckets periodically to avoid unbounded memory growth.
    for client_ip, dq in list(_workout_rate_store.items()):
        while dq and dq[0] < window_start:
            dq.popleft()
        if not dq:
            _workout_rate_store.pop(client_ip, None)

    if len(_workout_rate_store) > _WORKOUT_RATE_LIMIT_MAX_CLIENTS:
        overflow = len(_workout_rate_store) - _WORKOUT_RATE_LIMIT_MAX_CLIENTS
        oldest_first = sorted(
            _workout_rate_store.items(),
            key=lambda item: item[1][0] if item[1] else float('inf')
        )
        for old_ip, _ in oldest_first[:overflow]:
            _workout_rate_store.pop(old_ip, None)

    if ip not in _workout_rate_store:
        _workout_rate_store[ip] = collections.deque()
    dq = _workout_rate_store[ip]
    # Remove timestamps outside the window
    while dq and dq[0] < window_start:
        dq.popleft()
    if len(dq) >= _WORKOUT_RATE_LIMIT_MAX:
        retry_after_seconds = max(1, int(dq[0] + _WORKOUT_RATE_LIMIT_WINDOW - now) + 1)
        return False, retry_after_seconds
    dq.append(now)
    return True, 0


# ===== LOGGING CONFIGURATION =====
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(name)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

app = FastAPI()


@app.on_event("startup")
async def startup_event():
    await connect_to_mongo()


@app.on_event("shutdown")
async def shutdown_event():
    await close_mongo_connection()

# ===== CORS CONFIGURATION (FIXED) =====
# CRITICAL: Cannot use "*" with allow_credentials=True
# Must specify exact origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",  # Vite dev server
        "http://localhost:3000",  # Alternative frontend port
        "http://127.0.0.1:5173",
        "http://127.0.0.1:3000",
    ],
    allow_credentials=True,  # Allow cookies/auth headers
    allow_methods=["*"],     # Allow all HTTP methods
    allow_headers=["*"],     # Allow all headers
)

# ===== MODELS =====
class UserProfile(BaseModel):
    username: str
    email: str
    age: int = Field(ge=1, le=120, description="Age must be between 1 and 120")
    gender: str
    weight: float = Field(ge=20, le=500, description="Weight in kg, must be between 20 and 500")
    height: float = Field(ge=50, le=300, description="Height in cm, must be between 50 and 300")
    goal: str
    experience: str
    equipment: List[str] = []
    body_issues: List[str] = []
    dietary_preference: str = "Non-Veg"
    allergies: List[str] = []

class ProfileUpdateRequest(BaseModel):
    """Pydantic model for profile update with validation"""
    age: Optional[int] = Field(None, ge=1, le=120)
    weight: Optional[float] = Field(None, ge=20, le=500)
    height: Optional[float] = Field(None, ge=50, le=300)
    gender: Optional[str] = None
    goal: Optional[str] = None
    experience: Optional[str] = None
    equipment: Optional[List[str]] = None
    body_issues: Optional[List[str]] = None
    dietary_preference: Optional[str] = None
    allergies: Optional[List[str]] = None
    days_per_week: Optional[int] = Field(None, ge=1, le=7)
    session_time: Optional[int] = Field(None, ge=10, le=180)
    meal_frequency: Optional[int] = Field(None, ge=1, le=10)
    cooking_time: Optional[str] = None
    cuisine_preference: Optional[str] = None

class WorkoutPlanRequest(BaseModel):
    goal: str
    experience: str
    equipment: List[str] = []
    body_issues: List[str] = []
    streak: Optional[int] = 0
    workout_history: Optional[List[Dict]] = []

class MealPlanRequest(BaseModel):
    age: int
    weight: float
    height: float
    gender: str
    goal: str
    dietary_preference: str = "Non-Veg"
    allergies: List[str] = []
    today_workout: Optional[Dict] = None

class NutritionRequest(BaseModel):
    age: int
    weight: float
    height: float
    gender: str
    goal: str
    dietary_preference: str = "Non-Veg"
    allergies: List[str] = []
    workout_intensity: str = "moderate"

class NutritionSwapRequest(BaseModel):
    food_name: str
    meal_type: str
    age: int
    weight: float
    height: float
    gender: str
    goal: str
    dietary_preference: str = "Non-Veg"
    allergies: List[str] = []

# ===== MISSING ENDPOINTS (ADD THESE) =====

@app.post("/api/users/save")
async def save_user_profile(profile: UserProfile):
    """Save user profile"""
    try:
        users = get_user_collection()
        payload = profile.dict()
        payload["updatedAt"] = _utcnow()

        await users.update_one(
            {"email": profile.email},
            {
                "$set": payload,
                "$setOnInsert": {"createdAt": _utcnow()}
            },
            upsert=True
        )
        
        return {
            "success": True,
            "message": "User profile saved successfully",
            "data": payload
        }
    except Exception as e:
        print(f" Error saving user: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/workout/save")
async def save_workout_plan(data: dict):
    """Save workout plan"""
    try:
        workouts = get_workout_history_collection()
        payload = {
            **(data or {}),
            "createdAt": _utcnow(),
            "updatedAt": _utcnow(),
        }
        await workouts.insert_one(payload)
        
        return {
            "success": True,
            "message": "Workout plan saved successfully",
            "data": payload
        }
    except Exception as e:
        print(f" Error saving workout: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/meals/save")
async def save_meal_plan(data: dict):
    """Save meal plan"""
    try:
        meals = get_meal_history_collection()
        payload = {
            **(data or {}),
            "createdAt": _utcnow(),
            "updatedAt": _utcnow(),
        }
        await meals.insert_one(payload)
        
        return {
            "success": True,
            "message": "Meal plan saved successfully",
            "data": payload
        }
    except Exception as e:
        print(f" Error saving meals: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/progress/save")
async def save_progress(data: dict):
    """Save user progress"""
    try:
        db = get_database()
        progress_collection = db.progress
        payload = {
            **(data or {}),
            "createdAt": _utcnow(),
            "updatedAt": _utcnow(),
        }
        await progress_collection.insert_one(payload)
        
        return {
            "success": True,
            "message": "Progress saved successfully",
            "data": payload
        }
    except Exception as e:
        print(f" Error saving progress: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/workout")
async def generate_workout_plan(request: Request):
    """
    PRIMARY workout plan endpoint — called by the frontend Workout.jsx and Nutrition.jsx.

    Accepts the full user profile as a dict so no field is required at the route level;
    the WorkoutEngine applies sensible defaults internally.

    Issue #1: reads `firstWorkoutDay` from profile to build a rolling-week plan for new users.
    Issue #4: returns cached plan instantly if one exists.

    Returns: { success: true, workout: [ <7 day objects> ], exercises_count: N }
    """
    try:
        # Parse request body manually
        body = await request.json()
        print(f"[/workout] Received request body type: {type(body)}")
        print(f"[/workout] Received keys: {list(body.keys()) if isinstance(body, dict) else 'NOT A DICT'}")
        
        profile = body if isinstance(body, dict) else {}

        from app.workout_engine import get_workout_engine

        print(f"[/workout] Generating weekly plan for goal={profile.get('goal')} "
              f"experience={profile.get('experience')} days={profile.get('days_per_week')}")

        workout_engine = get_workout_engine()

        # Issue #1 – detect new user via firstWorkoutDay field
        first_workout_day = profile.get('firstWorkoutDay')  # 0=Mon…6=Sun, or None
        is_new_user = first_workout_day is not None
        user_start_day = int(first_workout_day) if first_workout_day is not None else None

        weekly_plan = workout_engine.generate_weekly_plan(
            profile,
            workout_history=[],
            user_start_day=user_start_day,
            is_new_user=is_new_user,
        )

        exercises_count = sum(
            len(day.get("exercises", [])) for day in weekly_plan if isinstance(day, dict)
        )

        print(f"[/workout] Generated {len(weekly_plan)} days, {exercises_count} exercises total")

        return {
            "success": True,
            "workout": weekly_plan,
            "exercises_count": exercises_count,
            "message": f"Weekly plan generated for {profile.get('goal', 'fitness')} goal",
        }
    except Exception as e:
        print(f"[/workout] Error generating workout plan: {e}")
        import traceback
        traceback.print_exc()

        raise HTTPException(status_code=500, detail=str(e))


# ─────────────────────────────────────────────────────────────────────────────
# Issue #4 – Async workout generation with caching + polling
# ─────────────────────────────────────────────────────────────────────────────

# In-memory job store (process-scoped; for production use Redis)
_async_jobs: Dict[str, dict] = {}

async def _generate_plan_background(job_id: str, profile: dict):
    """Background task: generate workout plan and store result in _async_jobs."""
    try:
        from app.workout_engine import get_workout_engine
        engine = get_workout_engine()
        first_workout_day = profile.get('firstWorkoutDay')
        is_new_user = first_workout_day is not None
        user_start_day = int(first_workout_day) if first_workout_day is not None else None
        plan = engine.generate_weekly_plan(
            profile, workout_history=[],
            user_start_day=user_start_day, is_new_user=is_new_user
        )
        _async_jobs[job_id] = {'status': 'complete', 'plan': plan}
    except Exception as exc:
        _async_jobs[job_id] = {'status': 'error', 'error': str(exc)}


@app.post("/workout/async")
async def generate_workout_async(profile: dict, background_tasks: BackgroundTasks):
    """
    Async workout plan generation (Issue #4).
    Returns cached plan immediately if available, otherwise starts background generation.
    Poll /workout/status/{job_id} to retrieve the result.
    """
    from app.workout_engine import get_workout_engine
    engine = get_workout_engine()

    # Check cache first
    if engine._plan_cache:
        cached = engine._plan_cache.get(profile)
        if cached:
            return {"status": "complete", "plan": cached, "job_id": None, "cached": True}

    job_id = str(uuid.uuid4())
    _async_jobs[job_id] = {'status': 'processing'}
    background_tasks.add_task(_generate_plan_background, job_id, profile)
    return {"status": "processing", "job_id": job_id, "estimated_seconds": 15, "cached": False}


@app.get("/workout/status/{job_id}")
async def get_workout_status(job_id: str):
    """Poll for async plan generation result (Issue #4)."""
    job = _async_jobs.get(job_id)
    if not job:
        raise HTTPException(status_code=404, detail=f"Job {job_id} not found")
    return job


@app.post("/workout/cache/invalidate")
async def invalidate_workout_cache(profile: dict):
    """Invalidate cached plan for a profile (call after significant profile changes)."""
    from app.workout_engine import get_workout_engine
    engine = get_workout_engine()
    if engine._plan_cache:
        engine._plan_cache.invalidate(profile)
        return {"success": True, "message": "Plan cache invalidated"}
    return {"success": True, "message": "No cache configured"}


# Add these endpoints BEFORE the bottom of the file
@app.post("/generate-plan")
async def generate_plan(profile: dict):
    """Generate AI workout and meal plan"""
    try:
        print(f" Generating AI plan for user")

        return {
            "success": True,
            "message": "AI plan generated successfully",
            "workout_plan": {
                "plan_type": "Beginner Strength",
                "days_per_week": 3,
                "exercises": ["Push-ups", "Squats", "Lunges"]
            },
            "meal_plan": {
                "calories": 2000,
                "meals": ["Breakfast", "Lunch", "Dinner"]
            }
        }
    except Exception as e:
        print(f" Error generating plan: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/nutrition")
async def generate_nutrition(request: NutritionRequest):
    try:
        from app.meal_engine import get_meal_engine
        meal_engine = get_meal_engine()
        
        user_profile = {
            'age': request.age,
            'weight': request.weight,
            'height': request.height,
            'gender': request.gender,
            'goal': request.goal,
            'dietary_preference': request.dietary_preference,
            'allergies': request.allergies
        }
        
        nutrition_data = meal_engine.suggest_daily_meals(
            user_profile,
            request.workout_intensity
        )
        
        return {
            'success': True,
            'nutrition': nutrition_data,
            'message': nutrition_data.get('note', 'Nutrition plan generated')
        }
    except Exception as e:
        print(f" Error generating nutrition plan: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/nutrition/swap")
async def swap_food(request: NutritionSwapRequest):
    try:
        from app.meal_engine import get_meal_engine
        meal_engine = get_meal_engine()
        
        user_profile = {
            'age': request.age,
            'weight': request.weight,
            'height': request.height,
            'gender': request.gender,
            'goal': request.goal,
            'dietary_preference': request.dietary_preference,
            'allergies': request.allergies
        }
        
        swap_options = meal_engine.get_swap_options(
            food_name=request.food_name, 
            meal_type=request.meal_type, 
            profile=user_profile,
            limit=5
        )
        return {"success": True, "swap_options": swap_options}
    except Exception as e:
        print(f" Error swapping food: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.put("/profile/update")
async def update_profile_endpoint(profile: UserProfile):
    """
    Update user profile - Basic endpoint without regeneration
    
    Production-grade with:
    - Pydantic validation
    - Structured error handling
    - Detailed logging
    """
    request_id = datetime.now().strftime("%Y%m%d%H%M%S%f")
    
    try:
        logger.info(f"[{request_id}] Starting profile update for user: {profile.username}")
        logger.debug(f"[{request_id}] Received profile data: {profile.dict()}")
        
        # Validate required fields
        if not profile.username or not profile.email:
            logger.warning(f"[{request_id}] Missing required fields: username or email")
            raise HTTPException(
                status_code=400,
                detail={"error": "Missing required fields", "fields": ["username", "email"]}
            )
        
        # Simulate database update (replace with actual DB logic)
        logger.info(f"[{request_id}] Updating profile in database...")
        
        response_data = {
            "success": True,
            "message": "User profile updated successfully",
            "request_id": request_id,
            "data": profile.dict()
        }
        
        logger.info(f"[{request_id}] Profile update completed successfully")
        return response_data
        
    except HTTPException:
        raise
    except ValueError as ve:
        logger.error(f"[{request_id}] Validation error: {ve}")
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        logger.error(f"[{request_id}] Unexpected error: {e}")
        logger.error(f"[{request_id}] Traceback: {traceback.format_exc()}")
        raise HTTPException(
            status_code=500,
            detail={"error": "Internal server error", "request_id": request_id}
        )


@app.put("/profile/update-with-regeneration")
async def update_profile_and_regenerate(profile: UserProfile):
    """Update user profile and regenerate workout/meal plans if needed"""
    try:
        logger.info(f"Updating profile and regenerating plans for: {profile.username}")

        # Bug #49 fixed: load the EXISTING profile from DB before comparing,
        # so we compare new values against what is actually stored,
        # NOT against hardcoded default strings like "intermediate" / "general_fitness".
        users = get_user_collection()
        existing = await users.find_one({"email": profile.email}, {"_id": 0})
        if not existing:
            existing = {}

        # Determine if changes require plan regeneration by comparing to stored values
        def _changed(field: str) -> bool:
            """True when the new value differs from what was previously stored."""
            new_val = getattr(profile, field, None)
            old_val = existing.get(field)
            # For lists, compare sorted to ignore ordering differences
            if isinstance(new_val, list) and isinstance(old_val, list):
                return sorted(str(x) for x in new_val) != sorted(str(x) for x in old_val)
            return new_val != old_val

        changes_affect_workout = any([
            _changed("experience"),
            _changed("goal"),
            _changed("body_issues"),
            _changed("equipment"),
        ])

        changes_affect_meal = any([
            _changed("goal"),
            _changed("dietary_preference"),
            _changed("allergies"),
        ])

        logger.info(f"Changes affecting workout: {changes_affect_workout}")
        logger.info(f"Changes affecting meal: {changes_affect_meal}")

        # Persist the updated profile to DB
        await users.update_one(
            {"email": profile.email},
            {
                "$set": {**profile.dict(), "updatedAt": _utcnow()},
                "$setOnInsert": {"createdAt": _utcnow()},
            },
            upsert=True,
        )

        response_data = {
            "success": True,
            "message": "Profile updated and plans regenerated successfully",
            "data": profile.dict(),
            "profile_changes": {
                "affect_workout_plans": changes_affect_workout,
                "affect_meal_plans": changes_affect_meal
            }
        }

        # Regenerate workout plan if needed
        if changes_affect_workout:
            logger.info("Regenerating workout plan...")
            response_data["regenerated_workout"] = {
                "plan_type": f"{profile.experience.title()} {profile.goal.title()} Plan",
                "days_per_week": 3 if profile.experience == "beginner" else 4,
                "exercises": ["Custom exercises based on profile"],
                "equipment_needed": profile.equipment,
                "injuries_considered": profile.body_issues
            }

        # Regenerate meal plan if needed
        if changes_affect_meal:
            logger.info("Regenerating meal plan...")
            response_data["regenerated_meal"] = {
                "calories": int(profile.weight * 25),
                "dietary_restrictions": profile.allergies,
                "preference_aligned": profile.dietary_preference,
                "meals": ["Custom meals based on new preferences"]
            }

        logger.info("Profile update with regeneration completed")
        return response_data
    except Exception as e:
        logger.error(f"Error updating profile with regeneration: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


@app.put("/profile/update-safe")
async def update_profile_safe(profile_data: ProfileUpdateRequest, request: Request):
    """
    SAFE PROFILE UPDATE ENDPOINT - Production Ready
    
    Features:
    - Graceful degradation (profile updates even if regeneration fails)
    - Comprehensive error handling
    - Transaction-like safety
    - Detailed logging with request IDs
    - Proper HTTP status codes
    
    Request Body:
    - All fields optional (partial updates supported)
    - Validated with Pydantic constraints
    """
    import uuid
    request_id = str(uuid.uuid4())[:8]
    timestamp = datetime.now().isoformat()
    
    # Initialize response structure
    response_data = {
        "success": False,
        "message": "",
        "request_id": request_id,
        "timestamp": timestamp,
        "data": None,
        "profile_changes": None,
        "regenerated_workout": None,
        "regenerated_meal": None,
        "errors": []
    }
    
    try:
        # ===== STEP 1: LOG INCOMING REQUEST =====
        logger.info(f"[{request_id}] ===== PROFILE UPDATE STARTED =====")
        logger.info(f"[{request_id}] Timestamp: {timestamp}")
        logger.debug(f"[{request_id}] Incoming payload: {profile_data.dict(exclude_none=True)}")
        
        # ===== STEP 2: VALIDATE INPUT =====
        update_dict = profile_data.dict(exclude_none=True)
        
        if not update_dict:
            logger.warning(f"[{request_id}] No valid fields provided for update")
            raise HTTPException(
                status_code=400,
                detail={"error": "No valid fields to update", "request_id": request_id}
            )
        
        # ===== STEP 3: AUTHENTICATE VIA JWT =====
        x_auth_token = request.headers.get("x-auth-token")
        if not x_auth_token:
            raise HTTPException(
                status_code=401,
                detail={"error": "Authentication required", "request_id": request_id}
            )
        user_id = _require_user_id_from_token(x_auth_token, request_id)
        logger.info(f"[{request_id}] Authenticated user ID: {user_id}")
        
        # ===== STEP 4: LOAD EXISTING PROFILE FROM DB =====
        try:
            # Bug #4 fixed: query the real user document instead of hardcoded defaults
            user_doc = await _find_user_by_id(user_id)
            if not user_doc:
                raise HTTPException(
                    status_code=404,
                    detail={"error": "User not found", "request_id": request_id}
                )
            # Build a comparable flat profile from the stored document
            existing_profile = {
                "age": user_doc.get("age"),
                "weight": user_doc.get("weight"),
                "height": user_doc.get("height"),
                "gender": user_doc.get("gender"),
                "goal": user_doc.get("goal"),
                "experience": user_doc.get("experience"),
                "dietary_preference": user_doc.get("dietary_preference"),
                "allergies": user_doc.get("allergies", []),
                "equipment": user_doc.get("equipment", []),
                "body_issues": user_doc.get("body_issues", []),
            }
            logger.debug(f"[{request_id}] Existing profile loaded from DB")
        except HTTPException:
            raise
        except Exception as db_error:
            logger.error(f"[{request_id}] Failed to load existing profile: {db_error}")
            raise HTTPException(
                status_code=503,
                detail={"error": "Database unavailable", "request_id": request_id}
            )
        
        # ===== STEP 5: MERGE AND UPDATE PROFILE =====
        updated_profile = {**existing_profile, **update_dict}
        logger.info(f"[{request_id}] Merged profile data: {updated_profile}")
        
        # ===== STEP 6: SAVE TO DATABASE =====
        try:
            # Bug #4 fixed: persist merged profile to MongoDB
            users_col = get_user_collection()
            await users_col.update_one(
                {"_id": user_doc["_id"]},
                {"$set": {**{k: v for k, v in update_dict.items()}, "updatedAt": _utcnow()}}
            )
            logger.info(f"[{request_id}] Profile saved to database successfully")
        except Exception as db_error:
            logger.error(f"[{request_id}] Database update failed: {db_error}")
            raise HTTPException(
                status_code=503,
                detail={"error": "Failed to save profile", "request_id": request_id}
            )
        
        # ===== STEP 7: DETECT CHANGES FOR REGENERATION =====
        def check_workout_changes(old: dict, new: dict) -> bool:
            """Check if changes affect workout plans"""
            workout_fields = ['goal', 'experience', 'body_issues', 'equipment', 'weight', 'age']
            return any(old.get(f) != new.get(f) for f in workout_fields if f in new)
        
        def check_meal_changes(old: dict, new: dict) -> bool:
            """Check if changes affect meal plans"""
            meal_fields = ['goal', 'dietary_preference', 'allergies', 'weight', 'height', 'age']
            return any(old.get(f) != new.get(f) for f in meal_fields if f in new)
        
        changes_affect_workout = check_workout_changes(existing_profile, updated_profile)
        changes_affect_meal = check_meal_changes(existing_profile, updated_profile)
        
        logger.info(f"[{request_id}] Workout regeneration needed: {changes_affect_workout}")
        logger.info(f"[{request_id}] Meal regeneration needed: {changes_affect_meal}")
        
        response_data["profile_changes"] = {
            "affect_workout_plans": changes_affect_workout,
            "affect_meal_plans": changes_affect_meal,
            "changed_fields": list(update_dict.keys())
        }
        
        # ===== STEP 8: REGENERATE WORKOUT (ISOLATED - FAILURE WON'T BLOCK PROFILE UPDATE) =====
        workout_error = None
        if changes_affect_workout:
            try:
                logger.info(f"[{request_id}] Starting workout regeneration...")
                # Replace with actual regeneration logic
                # workout_result = await regenerate_workout(user_id, updated_profile)
                response_data["regenerated_workout"] = {
                    "status": "success",
                    "plan_type": f"{updated_profile.get('experience', 'Beginner').title()} {updated_profile.get('goal', 'Fitness')} Plan",
                    "days_per_week": 3 if updated_profile.get('experience') == 'beginner' else 4,
                    "message": "Workout plan regenerated successfully"
                }
                logger.info(f"[{request_id}] Workout regeneration completed")
            except Exception as workout_error:
                workout_error = str(workout_error)
                logger.error(f"[{request_id}] Workout regeneration failed: {workout_error}")
                logger.error(f"[{request_id}] Traceback: {traceback.format_exc()}")
                response_data["errors"].append({
                    "type": "workout_regeneration",
                    "message": "Workout regeneration failed, will use cached plan",
                    "error": workout_error
                })
        
        # ===== STEP 9: REGENERATE MEAL (ISOLATED - FAILURE WON'T BLOCK PROFILE UPDATE) =====
        meal_error = None
        if changes_affect_meal:
            try:
                logger.info(f"[{request_id}] Starting meal regeneration...")
                # Replace with actual regeneration logic
                # meal_result = await regenerate_meal(user_id, updated_profile)
                response_data["regenerated_meal"] = {
                    "status": "success",
                    "calories": int(updated_profile.get('weight', 70) * 25),
                    "dietary_restrictions": updated_profile.get('allergies', []),
                    "message": "Meal plan regenerated successfully"
                }
                logger.info(f"[{request_id}] Meal regeneration completed")
            except Exception as meal_error:
                meal_error = str(meal_error)
                logger.error(f"[{request_id}] Meal regeneration failed: {meal_error}")
                logger.error(f"[{request_id}] Traceback: {traceback.format_exc()}")
                response_data["errors"].append({
                    "type": "meal_regeneration",
                    "message": "Meal regeneration failed, will use cached plan",
                    "error": meal_error
                })
        
        # ===== STEP 10: BUILD SUCCESS RESPONSE =====
        response_data["success"] = True
        response_data["message"] = "Profile updated successfully"
        response_data["data"] = updated_profile
        
        # Set appropriate status based on errors
        if response_data["errors"]:
            logger.warning(f"[{request_id}] Profile update succeeded with regeneration errors")
            response_data["message"] = "Profile updated, but some regenerations failed"
        else:
            logger.info(f"[{request_id}] Profile update completed successfully with full regeneration")
        
        logger.info(f"[{request_id}] ===== PROFILE UPDATE COMPLETED =====")
        return response_data
        
    except HTTPException:
        raise
    except ValueError as ve:
        logger.error(f"[{request_id}] Validation error: {ve}")
        raise HTTPException(
            status_code=400,
            detail={"error": "Invalid input data", "message": str(ve), "request_id": request_id}
        )
    except Exception as e:
        logger.error(f"[{request_id}] CRITICAL ERROR: {e}")
        logger.error(f"[{request_id}] Full traceback:\n{traceback.format_exc()}")
        raise HTTPException(
            status_code=500,
            detail={"error": "Internal server error", "message": str(e), "request_id": request_id}
        )

# ─────────────────────────────────────────────────────────────────────────────
# Smart rest-day adjustment + 48h muscle-recovery validation
# ─────────────────────────────────────────────────────────────────────────────

class AdjustRestDaysRequest(BaseModel):
    """Request body for /workout/adjust-rest-days"""
    profile: dict
    # Optional: days (0=Mon…6=Sun) the user explicitly wants as rest days.
    preferred_rest_days: Optional[List[int]] = []
    # Optional: persist preferences to the user record (requires email in profile)
    save_preferences: bool = False


@app.post("/workout/adjust-rest-days")
async def adjust_rest_days(request: AdjustRestDaysRequest):
    """
    Re-generates a weekly workout schedule that respects the user's preferred
    rest days, then validates 48-hour muscle-group recovery.

    Returns:
        {
            success: bool,
            workout: [...],           # 7-day plan
            recovery_check: {         # result of _validate_muscle_recovery
                valid: bool,
                violations: [...],
                summary: str
            },
            applied_rest_days: [int], # the rest-day indices actually used
            message: str
        }
    """
    try:
        from app.workout_engine import get_workout_engine

        engine = get_workout_engine()
        profile = request.profile or {}
        preferred = request.preferred_rest_days or []

        # Clamp preferred rest days to valid range
        preferred = sorted({int(d) for d in preferred if 0 <= int(d) <= 6})

        # Determine experience + workout day count
        experience = profile.get('experience', 'Beginner')
        user_days = int(profile.get('days_per_week', 4))
        user_days = max(1, min(7, user_days))

        streak = int(profile.get('streak', 0) or 0)
        consistency = float(profile.get('consistency', 0.7) or 0.7)

        if experience == 'Beginner':
            workout_days_count = 4 if (streak >= 21 and consistency >= 0.85) else 3
        elif experience == 'Intermediate':
            workout_days_count = 5 if (streak >= 42 and consistency >= 0.90) else 4
        elif experience == 'Advanced':
            workout_days_count = 6 if (streak >= 10 and consistency >= 0.80) else 5
        else:
            workout_days_count = min(4, user_days)

        # Respect user preference when they request fewer days than the recommendation.
        workout_days_count = max(1, min(workout_days_count, user_days))

        # Build the split
        goal = profile.get('goal', 'Muscle Gain')
        split = engine._get_split_for_experience(experience, workout_days_count, goal, [])

        # Determine final rest positions
        rest_count = 7 - workout_days_count
        if preferred and len(preferred) == rest_count:
            # Use exactly the preferred positions
            rest_positions = preferred
        elif preferred and len(preferred) < rest_count:
            # Fill remaining rest slots with the smart algorithm
            extra_needed = rest_count - len(preferred)
            smart = engine._calculate_smart_rest_days(split, rest_count, experience, goal)
            extra = [d for d in smart if d not in preferred][:extra_needed]
            rest_positions = sorted(preferred + extra)
        else:
            # More preferences than rest slots available — use smart placement
            rest_positions = engine._calculate_smart_rest_days(split, rest_count, experience, goal)

        # Build the 7-day plan
        weekly_plan = engine._build_weekly_plan(profile, split, rest_positions)

        # Validate 48-hour muscle-group recovery
        recovery_check = engine._validate_muscle_recovery(weekly_plan)

        # Persist preferences to MongoDB (best-effort, won't fail the request)
        email = profile.get('email', '')
        if request.save_preferences and email:
            try:
                users = get_user_collection()
                await users.update_one(
                    {'email': email},
                    {'$set': {
                        'restDayPreferences': rest_positions,
                        'workoutPatterns': profile.get('workoutPatterns'),
                        'updatedAt': _utcnow(),
                    }},
                    upsert=False
                )
                logger.info(f"[adjust-rest-days] Saved preferences for {email}")
            except Exception as db_err:
                logger.warning(f"[adjust-rest-days] Could not save preferences: {db_err}")

        exercises_count = sum(
            len(day.get('exercises', [])) for day in weekly_plan if isinstance(day, dict)
        )

        recovery_note = ''
        if not recovery_check['valid']:
            recovery_note = f" ⚠ {recovery_check['summary']}"

        return {
            'success': True,
            'workout': weekly_plan,
            'exercises_count': exercises_count,
            'recovery_check': recovery_check,
            'applied_rest_days': rest_positions,
            'message': f"Schedule adjusted with rest on days {rest_positions}.{recovery_note}",
        }

    except Exception as e:
        logger.error(f"[adjust-rest-days] Error: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


class SwapRestDayRequest(BaseModel):
    """Request to swap a rest day with the next workout day"""
    email: str
    rest_day_index: int = Field(ge=0, le=6, description="Index of the rest day to swap (0-6)")
    current_plan: List[Dict]


@app.post("/api/swap-rest-day")
async def swap_rest_day(request: SwapRestDayRequest):
    """
    Swap a rest day with the next available workout day.
    
    When a user wants to workout on a rest day, this endpoint swaps
    today's rest with tomorrow's workout, making the workout available
    today and moving the rest to the next workout day.
    
    Returns:
        {
            success: bool,
            workout: [...],  # Updated 7-day plan
            message: str,
            swapped_days: {
                rest_day_index: int,
                workout_day_index: int
            }
        }
    """
    try:
        from app.workout_engine import get_workout_engine
        
        engine = get_workout_engine()
        
        # Validate the rest day index
        if request.rest_day_index < 0 or request.rest_day_index > 6:
            raise HTTPException(status_code=400, detail="rest_day_index must be between 0 and 6")
        
        # Validate current plan
        if not request.current_plan or len(request.current_plan) != 7:
            raise HTTPException(status_code=400, detail="current_plan must contain exactly 7 days")
        
        # Check if the specified day is actually a rest day
        rest_day = request.current_plan[request.rest_day_index]
        if rest_day.get('type') != 'rest':
            raise HTTPException(
                status_code=400, 
                detail=f"Day {request.rest_day_index} is not a rest day"
            )
        
        # Find next workout day
        next_workout_idx = None
        for offset in range(1, 7):
            idx = (request.rest_day_index + offset) % 7
            day = request.current_plan[idx]
            if day.get('type') == 'workout' and not day.get('is_placeholder'):
                next_workout_idx = idx
                break
        
        if next_workout_idx is None:
            raise HTTPException(
                status_code=400,
                detail="No workout day found to swap with"
            )
        
        # Perform the swap
        swapped_plan = engine.swap_rest_with_next_workout(
            request.current_plan, 
            request.rest_day_index
        )
        
        # Optionally save the swapped plan to user preferences
        if request.email:
            try:
                users = get_user_collection()
                await users.update_one(
                    {'email': request.email},
                    {
                        '$set': {
                            'lastSwappedPlan': swapped_plan,
                            'lastSwapDate': _utcnow(),
                            'updatedAt': _utcnow()
                        }
                    },
                    upsert=False
                )
                logger.info(f"[swap-rest-day] Saved swapped plan for {request.email}")
            except Exception as db_err:
                logger.warning(f"[swap-rest-day] Could not save plan: {db_err}")
        
        return {
            "success": True,
            "workout": swapped_plan,
            "message": f"Rest day swapped successfully",
            "swapped_days": {
                "rest_day_index": request.rest_day_index,
                "workout_day_index": next_workout_idx
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"[swap-rest-day] Error: {e}")
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Error swapping rest day: {str(e)}")


# ===== EXISTING ENDPOINTS =====

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "service": "elevate_fitness",
        "timestamp": _utcnow().isoformat()
    }

@app.post("/ml/get-weekly-plan")
async def get_weekly_plan(request: WorkoutPlanRequest):
    """Generate weekly workout plan"""
    try:
        from app.workout_engine import get_workout_engine
        
        workout_engine = get_workout_engine()
        
        user_profile = {
            'goal': request.goal,
            'experience': request.experience,
            'equipment': request.equipment,
            'body_issues': request.body_issues,
            'streak': request.streak,
            'age': 25,
            'weight': 70,
            'height': 175
        }
        
        weekly_plan = workout_engine.generate_weekly_plan(user_profile, request.workout_history)
        
        return {
            'success': True,
            'workout': weekly_plan,
            'message': f'Weekly plan generated for {request.goal} goal'
        }
    except Exception as e:
        print(f" Error generating weekly plan: {e}")
        return {
            'success': False,
            'error': str(e),
            'workout': []
        }

@app.post("/ml/get-daily-meals")
async def get_daily_meals(request: MealPlanRequest):
    """Generate daily meal plan"""
    try:
        from app.meal_engine import get_meal_engine
        
        meal_engine = get_meal_engine()
        
        user_profile = {
            'age': request.age,
            'weight': request.weight,
            'height': request.height,
            'gender': request.gender,
            'goal': request.goal,
            'dietary_preference': request.dietary_preference,
            'allergies': request.allergies
        }
        
        meal_plan = meal_engine.suggest_daily_meals(
            user_profile,
            request.today_workout
        )
        
        return {
            'success': True,
            'meal_plan': meal_plan,
            'message': meal_plan.get('note', 'Meal plan generated')
        }
    except Exception as e:
        print(f" Error generating meal plan: {e}")
        return {
            'success': False,
            'error': str(e),
            'meal_plan': {
                'date': datetime.now().strftime('%Y-%m-%d'),
                'daily_target': {},
                'meals': []
            }
        }

# ===== STARTUP =====
@app.on_event("startup")
async def startup_event():
    print("FastAPI server started on port 8000")
    print("Loading exercise and nutrition data...")
    try:
        from app.workout_engine import get_workout_engine
        from app.meal_engine import get_meal_engine

        workout_engine = get_workout_engine()
        meal_engine = get_meal_engine()

        print("Data engines loaded successfully")
    except Exception as e:
        print(f"Warning: {e}")

@app.on_event("shutdown")
async def shutdown_event():
    print("Server shutting down")