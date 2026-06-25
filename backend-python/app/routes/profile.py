from fastapi import APIRouter, HTTPException, Depends, Header, Request
from bson import ObjectId
from datetime import datetime, timezone, timedelta
from typing import Optional, List, Dict, Any
import logging
import traceback
import os
import jwt
import hashlib
import json

from app.db import get_database
from app.biometric_normalizer import BiometricNormalizer
from app.utils.activity_logger import log_user_activity, ActivityType
from app.utils.db_safe_write import safe_update_one, safe_find_one

logger = logging.getLogger(__name__)

# Prescription targets — single source of truth for water/sleep goals
try:
    from app.prescription_targets import get_prescription_targets
except Exception as _pt_err:
    logger.warning(f"prescription_targets import failed ({_pt_err}); using defaults")
    def get_prescription_targets(goal, level, age):
        return {'water_target_ml': 2750, 'sleep_target_hours': 8.0, 'sleep_minimum_hours': 7.0}

# Priority 3 — Adaptive modifier: adjust intensity/volume based on last 7 daily check-ins
try:
    from app.adaptive_modifier import compute_adaptive_modifiers, apply_modifiers_to_workout_stats
except Exception as _am_err:
    logger.warning(f"adaptive_modifier import failed ({_am_err}); adaptive plan adjustments disabled")
    compute_adaptive_modifiers = None
    apply_modifiers_to_workout_stats = None



def _utcnow() -> datetime:
    return datetime.now(timezone.utc)

# Import engine factories (lazy init at call-time).
try:
    from app.workout_engine import get_workout_engine
except Exception as e:
    logger.warning(f"Could not import get_workout_engine: {e}")
    get_workout_engine = None

try:
    from app.meal_engine import get_meal_engine
except Exception as e:
    logger.warning(f"Could not import get_meal_engine: {e}")
    get_meal_engine = None

try:
    from app.plan_cache import get_plan_cache
except Exception as e:
    logger.warning(f"Could not load PlanCache: {e}")
    get_plan_cache = None


def _get_plan_cache_if_available():
    if not callable(get_plan_cache):
        return None
    try:
        return get_plan_cache()
    except Exception as cache_exc:
        logger.warning(f"PlanCache unavailable: {cache_exc}")
        return None

router = APIRouter(prefix="/profile", tags=["profile"])

# Pydantic models
from pydantic import BaseModel, Field

class ProfileUpdateRequest(BaseModel):
    """Profile update request with validation - includes all fields needed for plan regeneration"""
    name: Optional[str] = None
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
    meal_frequency: Optional[int] = Field(None, ge=1, le=6)
    cooking_time: Optional[str] = None
    cuisine_preference: Optional[str] = None
    dietary_restrictions: Optional[List[str]] = None
    sleep_hours: Optional[float] = Field(None, ge=0, le=24)
    water_liters: Optional[float] = Field(None, ge=0, le=12)
    sleep_score: Optional[float] = Field(None, ge=1, le=10)
    hydration_score: Optional[float] = Field(None, ge=1, le=10)
    stress_level: Optional[float] = Field(None, ge=1, le=10)
    fatigue_level: Optional[float] = Field(None, ge=1, le=10)
    consistency: Optional[float] = Field(None, ge=0, le=1)
    streak: Optional[int] = Field(None, ge=0)

def get_current_user_from_token(
    request: Request,
    x_auth_token: Optional[str] = Header(None, alias="x-auth-token", description="JWT token"),
):
    """
    Extract and validate user from JWT token.
    """
    try:
        secret_key = os.getenv("JWT_SECRET")
        if not secret_key:
            raise HTTPException(
                status_code=500,
                detail="JWT secret not configured"
            )

        token = x_auth_token or request.cookies.get("elevate_token")
        if not token:
            raise HTTPException(
                status_code=401,
                detail="Invalid authentication token"
            )

        payload = jwt.decode(token, secret_key, algorithms=["HS256"])

        # Node backend signs token as: { user: { id: "..." } }
        user_id = None
        if isinstance(payload, dict):
            user_obj = payload.get("user") or {}
            user_id = user_obj.get("id") or payload.get("sub") or payload.get("id")

        if not user_id:
            raise HTTPException(
                status_code=401,
                detail="Invalid authentication token"
            )
        
        return {"user_id": user_id}
        
    except HTTPException:
        raise
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=401,
            detail="Authentication token expired"
        )
    except jwt.InvalidTokenError:
        raise HTTPException(
            status_code=401,
            detail="Invalid authentication token"
        )
    except Exception as e:
        logger.error(f"Token validation error: {e}")
        raise HTTPException(
            status_code=401,
            detail="Invalid authentication token"
        )

# Fields that affect workout plans
WORKOUT_PLAN_FIELDS = {
    'goal', 'experience', 'equipment', 'body_issues', 'days_per_week',
    'weight', 'age', 'height', 'session_time', 'sleep_hours', 'water_liters',
    'sleep_score', 'hydration_score', 'stress_level', 'fatigue_level',
    'consistency', 'streak'
}

# Fields that affect nutrition plans
NUTRITION_PLAN_FIELDS = {
    'goal', 'weight', 'height', 'age', 'dietary_preference', 'allergies',
    'meal_frequency', 'cooking_time', 'cuisine_preference', 'dietary_restrictions',
    'sleep_hours', 'water_liters', 'sleep_score', 'hydration_score', 'stress_level'
}

PROFILE_FINGERPRINT_FIELDS = {
    'age', 'weight', 'height', 'goal', 'experience', 'days_per_week',
    'equipment', 'body_issues', 'dietary_preference', 'allergies',
    'sleep_hours', 'water_liters', 'sleep_score', 'hydration_score',
    'stress_level', 'fatigue_level'
}


def _normalize_for_compare(value: Any) -> Any:
    if isinstance(value, list):
        normalized = [str(v).strip().lower() for v in value if v is not None]
        return sorted(normalized)
    return value


def _has_value_change(old_value: Any, new_value: Any) -> bool:
    return _normalize_for_compare(old_value) != _normalize_for_compare(new_value)


def _build_profile_fingerprint(profile: Dict[str, Any]) -> str:
    payload = {
        key: _normalize_for_compare(profile.get(key))
        for key in sorted(PROFILE_FINGERPRINT_FIELDS)
    }
    encoded = json.dumps(payload, sort_keys=True, default=str, separators=(',', ':'))
    return hashlib.sha256(encoded.encode()).hexdigest()[:32]


def _build_plan_profile(user_doc: Dict[str, Any], user_id: str) -> Dict[str, Any]:
    raw_sleep = user_doc.get('sleep_hours', user_doc.get('sleep_score', 7.0))
    raw_water = user_doc.get('water_liters', user_doc.get('hydration_score', 2.5))
    sleep_score = BiometricNormalizer.normalize_sleep(raw_sleep)
    hydration_score = BiometricNormalizer.normalize_hydration(raw_water)

    return {
        'user_id': user_id,
        'email': user_doc.get('email', ''),
        'created_at': user_doc.get('createdAt') or user_doc.get('created_at'),
        'registrationDate': user_doc.get('registrationDate') or user_doc.get('registration_date'),
        'age': user_doc.get('age', 25),
        'weight': user_doc.get('weight', 70.0),
        'height': user_doc.get('height', 175.0),
        'gender': user_doc.get('gender', 'male'),
        'goal': user_doc.get('goal', 'Muscle Gain'),
        'experience': user_doc.get('experience', 'Beginner'),
        'equipment': user_doc.get('equipment', []),
        'body_issues': user_doc.get('body_issues', []),
        'dietary_preference': user_doc.get('dietary_preference', 'Non-Veg'),
        'allergies': user_doc.get('allergies', []),
        'days_per_week': user_doc.get('days_per_week', 4),
        'session_time': user_doc.get('session_time', 60),
        'meal_frequency': user_doc.get('meal_frequency', 3),
        'sleep_hours': BiometricNormalizer.parse_sleep_hours(raw_sleep),
        'water_liters': BiometricNormalizer.parse_water_liters(raw_water),
        'sleep_score': sleep_score,
        'hydration_score': hydration_score,
        'stress_level': float(user_doc.get('stress_level', 5.0) or 5.0),
        'fatigue_level': float(user_doc.get('fatigue_level', 5.0) or 5.0),
        'consistency': float(user_doc.get('consistency', 0.7) or 0.7),
        'streak': int(user_doc.get('streak', 0) or 0),
    }


def _build_user_filter(user_id: str) -> Dict[str, Any]:
    if ObjectId.is_valid(user_id):
        return {'_id': ObjectId(user_id)}
    return {'_id': user_id}


def _is_cold_start(user_doc: Dict[str, Any], daily_log_count: int = 0) -> bool:
    """
    Detect if this is a Week 1 user who has no historical adaptation data yet.

    Returns True when:
    - Account is less than 7 days old, OR
    - User has fewer than 7 daily logs

    Per plan Section 11: cold-start users get base matrix + age modifier only.
    The weekly adaptive modifier is skipped until Day 8.
    """
    if daily_log_count < 7:
        return True

    created_at = user_doc.get('createdAt') or user_doc.get('created_at')
    if not created_at:
        return False  # no creation date → assume existing user, don't cold-start

    try:
        if isinstance(created_at, str):
            created_at = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
        if created_at.tzinfo is None:
            created_at = created_at.replace(tzinfo=timezone.utc)
        age_days = (_utcnow() - created_at).days
        return age_days < 7
    except Exception:
        return False


_COLD_START_MESSAGE = (
    "Your plan will personalise further after your first week based on your sleep "
    "and hydration. Keep logging daily!"
)

async def _load_adaptive_modifiers(user_id: str, water_target_ml: int = 2750, sleep_target_hours: float = 8.0) -> Dict[str, Any]:
    """Fetch last 7 daily check-ins and compute adaptive modifiers."""
    if not callable(compute_adaptive_modifiers):
        return {}
    try:
        db = get_database()
        cursor = db.daily_logs.find(
            {'user_id': user_id},
            {'_id': 0, 'sleep_hours': 1, 'water_ml': 1, 'workout_completed': 1}
        ).sort('date', -1).limit(7)
        logs = [doc async for doc in cursor]
        if not logs:
            return {}
        mods = compute_adaptive_modifiers(
            logs,
            water_target_ml=water_target_ml,
            sleep_target_hours=sleep_target_hours,
        )
        logger.info(f"Adaptive modifiers for {user_id}: {mods.get('reason', '')}")
        return mods
    except Exception as exc:
        logger.warning(f"Adaptive modifier load failed: {exc}")
        return {}


def _generate_workout_plan(user_profile: Dict[str, Any], request_id: str, adaptive_mods: Dict[str, Any] = None) -> Dict[str, Any]:
    workout_engine = get_workout_engine() if callable(get_workout_engine) else None
    if workout_engine is None:
        logger.warning(f"[{request_id}] WorkoutEngine not available")
        return {'status': 'skipped', 'reason': 'engine_not_available'}

    try:
        # Build workout_stats enriched with adaptive modifiers so the
        # progression engine can apply sleep/hydration-based adjustments.
        workout_stats: Dict[str, Any] = {}
        if adaptive_mods and callable(apply_modifiers_to_workout_stats):
            workout_stats = apply_modifiers_to_workout_stats({}, adaptive_mods)

        user_profile_copy = dict(user_profile)
        user_profile_copy['workout_stats'] = workout_stats

        new_workout_plan = workout_engine.generate_weekly_plan(
            profile=user_profile_copy,
            workout_history=None,
        )
        workout_days = sum(1 for day in new_workout_plan if day.get('type') == 'workout')
        return {
            'status': 'success',
            'plan': new_workout_plan,
            'workout_days': workout_days,
            'requested_days': user_profile.get('days_per_week', 4),
            'adaptive_applied': bool(adaptive_mods),
            'adaptive_reason': (adaptive_mods or {}).get('reason', ''),
        }
    except Exception as exc:
        logger.error(f"[{request_id}] Workout regeneration failed: {exc}")
        logger.error(f"[{request_id}] Traceback: {traceback.format_exc()}")
        return {'status': 'error', 'error': str(exc)}


def _generate_nutrition_plan(
    user_profile: Dict[str, Any],
    request_id: str,
    workout_plan: Optional[List[Dict[str, Any]]] = None,
) -> Dict[str, Any]:
    meal_engine = get_meal_engine() if callable(get_meal_engine) else None
    if meal_engine is None:
        logger.warning(f"[{request_id}] MealEngine not available")
        return {'status': 'skipped', 'reason': 'engine_not_available'}

    try:
        new_nutrition_plan = meal_engine.generate_meal_plan(
            profile=user_profile,
            weekly_workout_plan=workout_plan or [],
        )
        meals_count = 0
        if isinstance(new_nutrition_plan.get('weekly_plan'), dict):
            meals_count = sum(
                len(items or [])
                for day in new_nutrition_plan['weekly_plan'].values()
                for items in (day or {}).values()
            )
        return {
            'status': 'success',
            'plan': new_nutrition_plan,
            'meals_count': meals_count,
        }
    except Exception as exc:
        logger.error(f"[{request_id}] Nutrition regeneration failed: {exc}")
        logger.error(f"[{request_id}] Traceback: {traceback.format_exc()}")
        return {'status': 'error', 'error': str(exc)}


@router.put("/update")
async def update_profile(
    profile_update: ProfileUpdateRequest,
    x_auth_token: Optional[str] = Header(None, alias="x-auth-token", description="JWT token"),
    current_user: dict = Depends(get_current_user_from_token)
):
    """
    Update user profile in MongoDB with automatic plan regeneration
    
    When profile fields affecting workout or nutrition plans are changed,
    this endpoint automatically:
    1. Invalidates the old cached plans
    2. Regenerates new plans based on updated profile
    3. Saves the new plans to the database
    
    Requirements:
    - Valid JWT token required
    - Atomic update_one operation
    - Activity logging
    - Automatic plan regeneration when needed
    """
    request_id = _utcnow().strftime("%Y%m%d%H%M%S%f")
    user_id = current_user["user_id"]
    
    logger.info(f"[{request_id}] ===== PROFILE UPDATE STARTED =====")
    logger.info(f"[{request_id}] User ID: {user_id}")
    
    # Response structure
    response_data = {
        "success": False,
        "message": "",
        "request_id": request_id,
        "data": None,
        "profile_changes": None,
        "regenerated_workout": None,
        "regenerated_nutrition": None,
        "errors": []
    }
    
    try:
        db = get_database()
        users = db.users
        user_filter = _build_user_filter(user_id)

        if hasattr(profile_update, 'model_dump'):
            update_data = profile_update.model_dump(exclude_none=True)
        else:
            update_data = profile_update.dict(exclude_none=True)

        if not update_data:
            logger.warning(f"[{request_id}] No valid fields provided")
            raise HTTPException(
                status_code=400,
                detail={"error": "No valid fields to update", "request_id": request_id}
            )

        existing_user = await safe_find_one(
            collection=users,
            filter_query=user_filter,
            resource_name='user'
        )
        if not existing_user:
            raise HTTPException(
                status_code=404,
                detail={"error": "User not found", "request_id": request_id}
            )

        changed_fields = [
            field for field, value in update_data.items()
            if _has_value_change(existing_user.get(field), value)
        ]

        if not changed_fields:
            logger.info(f"[{request_id}] No effective field changes detected")
            existing_user.pop('password', None)
            existing_user['_id'] = str(existing_user['_id'])
            return {
                'success': True,
                'message': 'No profile changes detected',
                'request_id': request_id,
                'data': {'user': existing_user, 'matched_count': 1, 'modified_count': 0},
                'profile_changes': {
                    'changed_fields': [],
                    'workout_regenerated': False,
                    'nutrition_regenerated': False,
                },
                'regenerated_workout': None,
                'regenerated_nutrition': None,
                'errors': [],
            }

        merged_user = {**existing_user, **update_data}
        plan_profile = _build_plan_profile(merged_user, user_id)

        needs_workout_regen = any(field in WORKOUT_PLAN_FIELDS for field in changed_fields)

        logger.info(f"[{request_id}] Changed fields: {changed_fields}")
        logger.info(f"[{request_id}] Workout regeneration needed: {needs_workout_regen}")
        logger.info(f"[{request_id}] Meal plan regeneration will be handled on next GET /api/meal-plan")

        plan_cache = _get_plan_cache_if_available()
        if plan_cache and needs_workout_regen:
            try:
                old_plan_profile = _build_plan_profile(existing_user, user_id)
                plan_cache.invalidate(old_plan_profile)
                plan_cache.invalidate(plan_profile)
            except Exception as cache_exc:
                logger.warning(f"[{request_id}] Cache invalidation failed: {cache_exc}")

        # Compute prescription targets (water + sleep) for this user
        _targets = get_prescription_targets(
            goal=plan_profile.get('goal', 'Muscle Gain'),
            level=plan_profile.get('experience', 'Beginner'),
            age=int(plan_profile.get('age', 25)),
        )
        water_target_ml: int = _targets['water_target_ml']
        sleep_target_hours: float = _targets['sleep_target_hours']

        # Priority 3: Load adaptive modifiers from last 7 daily check-ins.
        # Done once and passed to both plan generators so they share the same
        # adjustment context for this profile update.
        # Cold-start detection: skip adaptive modifier in Week 1 (per plan Section 11).
        adaptive_mods: Dict[str, Any] = {}
        personalization_message: str = ''
        if needs_workout_regen:
            try:
                db_tmp = get_database()
                log_count = await db_tmp.daily_logs.count_documents({'user_id': user_id})
                cold_start = _is_cold_start(existing_user, daily_log_count=log_count)
                if cold_start:
                    personalization_message = _COLD_START_MESSAGE
                    logger.info(f"[{request_id}] Cold-start detected — skipping adaptive modifier")
                else:
                    adaptive_mods = await _load_adaptive_modifiers(
                        user_id,
                        water_target_ml=water_target_ml,
                        sleep_target_hours=sleep_target_hours,
                    )
            except Exception as am_exc:
                logger.warning(f"[{request_id}] Adaptive modifier load error: {am_exc}")


        workout_plan_result = None
        nutrition_plan_result = None

        if needs_workout_regen:
            workout_plan_result = _generate_workout_plan(plan_profile, request_id, adaptive_mods)
            response_data['regenerated_workout'] = workout_plan_result
            if workout_plan_result.get('status') == 'error':
                response_data['errors'].append({
                    'type': 'workout_regeneration',
                    'message': 'Workout plan regeneration failed',
                    'error': workout_plan_result.get('error')
                })



        update_payload: Dict[str, Any] = {
            **update_data,
            'updatedAt': _utcnow(),
            'profileFingerprint': _build_profile_fingerprint(merged_user),
            'lastProfileUpdate': _utcnow().isoformat(),
            'sleep_score': plan_profile['sleep_score'],
            'hydration_score': plan_profile['hydration_score'],
            'sleep_hours': plan_profile['sleep_hours'],
            'water_liters': plan_profile['water_liters'],
        }

        if isinstance(workout_plan_result, dict) and workout_plan_result.get('status') == 'success':
            update_payload.update({
                'workoutPlan': workout_plan_result['plan'],
                'workoutPlanGeneratedAt': _utcnow(),
                'workoutPlanRegenerated': True,
            })



        result = await safe_update_one(
            collection=users,
            filter_query=user_filter,
            update_query={'$set': update_payload},
            upsert=False,
            resource_name='user profile',
        )

        try:
            await log_user_activity(
                user_id=user_id,
                activity_type=ActivityType.PROFILE_UPDATE,
                metadata={
                    'fields_updated': changed_fields,
                    'changes': {k: update_data[k] for k in changed_fields},
                    'request_id': request_id,
                }
            )
        except Exception as log_error:
            logger.error(f"[{request_id}] Activity logging failed: {log_error}")

        updated_user = await safe_find_one(
            collection=users,
            filter_query=user_filter,
            resource_name='user'
        )
        if not updated_user:
            raise HTTPException(
                status_code=404,
                detail={"error": "User not found after update", "request_id": request_id}
            )

        updated_user.pop('password', None)
        updated_user['_id'] = str(updated_user['_id'])

        workout_regen_success = bool(
            isinstance(workout_plan_result, dict) and workout_plan_result.get('status') == 'success'
        )

        response_data['success'] = True
        response_data['message'] = 'Profile updated successfully'
        if response_data['errors']:
            response_data['message'] = 'Profile updated, but some plan regenerations failed'

        response_data['data'] = {
            'user': updated_user,
            'matched_count': result.matched_count,
            'modified_count': result.modified_count,
        }
        response_data['profile_changes'] = {
            'changed_fields': changed_fields,
            'workout_regenerated': bool(needs_workout_regen and workout_regen_success),
            'nutrition_regenerated': False, # Will be regenerated on next fetch
        }

        # Cold-start onboarding message (empty string when not applicable)
        response_data['personalization_message'] = personalization_message

        # Prescription targets included in every plan response so frontend
        # can display the correct water / sleep goals to the user.
        response_data['prescription_targets'] = {
            'water_target_ml':     water_target_ml,
            'sleep_target_hours':  sleep_target_hours,
            'sleep_minimum_hours': _targets.get('sleep_minimum_hours', 7.0),
        }

        logger.info(f"[{request_id}] ===== PROFILE UPDATE COMPLETED =====")
        return response_data
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"[{request_id}] CRITICAL ERROR: {e}")
        logger.error(f"[{request_id}] Traceback: {traceback.format_exc()}")
        raise HTTPException(
            status_code=500,
            detail={"error": "Internal server error", "message": str(e), "request_id": request_id}
        )

@router.get("/me")
async def get_current_user_profile(
    x_auth_token: Optional[str] = Header(None, alias="x-auth-token", description="JWT token"),
    current_user: dict = Depends(get_current_user_from_token)
):
    """Get current user profile"""
    request_id = _utcnow().strftime("%Y%m%d%H%M%S%f")
    user_id = current_user["user_id"]
    
    logger.info(f"[{request_id}] Getting profile for user: {user_id}")
    
    try:
        db = get_database()
        users = db.users
        
        user = await safe_find_one(
            collection=users,
            filter_query={"_id": ObjectId(user_id)},
            resource_name="user"
        )
        
        if not user:
            raise HTTPException(
                status_code=404,
                detail={"error": "User not found", "request_id": request_id}
            )
        
        # Remove sensitive data
        user.pop("password", None)
        user["_id"] = str(user["_id"])
        
        return {
            "success": True,
            "request_id": request_id,
            "data": user
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"[{request_id}] Error getting profile: {e}")
        raise HTTPException(
            status_code=500,
            detail={"error": "Internal server error", "message": str(e), "request_id": request_id}
        )
