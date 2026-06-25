from fastapi import APIRouter, HTTPException, Depends, Header, Request
from pydantic import BaseModel
from datetime import datetime, timezone, timedelta
from typing import Optional, Dict, Any
import hashlib
import json
import uuid

from app.db import get_database, get_weekly_meal_plans_collection
from app.routes.profile import get_current_user_from_token, safe_find_one
from app.meal_engine import get_meal_engine
from bson import ObjectId

router = APIRouter(prefix="/api/meal-plan", tags=["meal-plan"])

ENGINE_VERSION = "6.0.0"
DATASET_VERSION = "nutrition_v4"

def _utcnow() -> datetime:
    return datetime.now(timezone.utc)

def _build_user_filter(user_id: str) -> Dict[str, Any]:
    if ObjectId.is_valid(user_id):
        return {'_id': ObjectId(user_id)}
    return {'_id': user_id}

def _generate_profile_hash(profile: dict) -> str:
    """Generate SHA256 hash using specific profile fields."""
    allergies = profile.get("allergies")
    if not isinstance(allergies, list):
        allergies = []
    
    payload = {
        "age": profile.get("age"),
        "gender": profile.get("gender"),
        "height": profile.get("height"),
        "weight": profile.get("weight"),
        "goal": profile.get("goal"),
        "diet": profile.get("dietary_preference", profile.get("diet")),
        "activity": profile.get("activity_level"),
        "allergies": sorted([str(a).lower().strip() for a in allergies]),
        "dataset_version": DATASET_VERSION,
        "engine_version": ENGINE_VERSION
    }
    encoded = json.dumps(payload, sort_keys=True, default=str, separators=(',', ':'))
    return hashlib.sha256(encoded.encode()).hexdigest()

async def _archive_old_plans(user_id: str):
    """Marks all ACTIVE plans for this user as ARCHIVED."""
    plans_col = get_weekly_meal_plans_collection()
    await plans_col.update_many(
        {"user_id": user_id, "status": "ACTIVE"},
        {"$set": {"status": "ARCHIVED"}}
    )

async def _generate_and_save_new_plan(user_id: str, profile: dict) -> dict:
    """Force new generation, archive old, save new ACTIVE, return."""
    await _archive_old_plans(user_id)
    
    # Generate new plan
    try:
        meal_engine = get_meal_engine()
        # Ensure we pass the correct structure
        # _generate_nutrition_plan from profile.py called generate_meal_plan(profile=profile, weekly_workout_plan=[])
        # If it's V6, let's just use generate_plan.
        # Wait, the engine wrapper in meal_engine.py might still have generate_meal_plan 
        # But we saw in app.meal_engine that it wraps V6. Let's call the wrapper method,
        # or use get_meal_engine().generate_plan(profile) if available.
        # Actually in profile.py it called meal_engine.generate_meal_plan(profile, weekly_workout_plan=[])
        workout_plan_for_nutrition = profile.get("workoutPlan", [])
        
        # We will try both interfaces just to be safe
        if hasattr(meal_engine, "generate_meal_plan"):
            new_plan_result = meal_engine.generate_meal_plan(profile=profile, weekly_workout_plan=workout_plan_for_nutrition)
        elif hasattr(meal_engine, "generate_plan"):
            new_plan_result = meal_engine.generate_plan(profile)
        else:
            raise ValueError("No suitable generate method found on meal engine")
            
        if isinstance(new_plan_result, dict):
            meal_plan = new_plan_result.get("weekly_plan", new_plan_result)
            stats = new_plan_result.get("stats", {})
            shopping_list = new_plan_result.get("shopping_list", {})
        else:
            meal_plan = new_plan_result
            stats = {}
            shopping_list = {}
            
    except Exception as e:
        print(f"Error generating meal plan: {e}")
        raise HTTPException(status_code=500, detail="Failed to generate meal plan")

    profile_hash = _generate_profile_hash(profile)
    now = _utcnow()
    # Expire in 7 days
    expires_at = now + timedelta(days=7)

    new_doc = {
        "user_id": user_id,
        "profile_hash": profile_hash,
        "engine_version": ENGINE_VERSION,
        "dataset_version": DATASET_VERSION,
        "week_start": now.strftime("%Y-%m-%d"),
        "week_end": expires_at.strftime("%Y-%m-%d"),
        "status": "ACTIVE",
        "meal_plan": meal_plan,
        "shopping_list": shopping_list,
        "generated_at": now.isoformat(),
        "expires_at": expires_at.isoformat(),
        "created_by": "NutritionEngineV6"
    }

    plans_col = get_weekly_meal_plans_collection()
    await plans_col.insert_one(new_doc)
    
    # Return without the _id to make it JSON serializable
    new_doc.pop("_id", None)
    return new_doc


@router.get("/")
async def get_meal_plan(
    x_auth_token: Optional[str] = Header(None, alias="x-auth-token", description="JWT token"),
    current_user: dict = Depends(get_current_user_from_token)
):
    """
    Find ACTIVE plan. 
    If not found or profile hash differs or expired, generate a new one.
    """
    user_id = current_user["user_id"]
    db = get_database()
    users_col = db.users
    user_profile = await safe_find_one(users_col, _build_user_filter(user_id), "user")
    if not user_profile:
        raise HTTPException(status_code=404, detail="User not found")
        
    current_hash = _generate_profile_hash(user_profile)
    
    plans_col = get_weekly_meal_plans_collection()
    active_plan = await plans_col.find_one({"user_id": user_id, "status": "ACTIVE"})
    
    now = _utcnow()
    
    if active_plan:
        plan_expired = False
        expires_at_str = active_plan.get("expires_at")
        if expires_at_str:
            try:
                expires_at = datetime.fromisoformat(expires_at_str)
                if now >= expires_at:
                    plan_expired = True
            except ValueError:
                pass
                
        if active_plan.get("profile_hash") == current_hash and not plan_expired:
            active_plan.pop("_id", None)
            return {
                "success": True,
                "message": "Returned saved meal plan",
                "data": active_plan
            }
            
    # Need regeneration (either missing, hash mismatch, or expired)
    new_plan_doc = await _generate_and_save_new_plan(user_id, user_profile)
    
    return {
        "success": True,
        "message": "Generated new weekly meal plan",
        "data": new_plan_doc
    }


@router.post("/generate")
async def force_generate_meal_plan(
    x_auth_token: Optional[str] = Header(None, alias="x-auth-token", description="JWT token"),
    current_user: dict = Depends(get_current_user_from_token)
):
    """Force new generation, archive old plan, create new ACTIVE plan, return."""
    user_id = current_user["user_id"]
    db = get_database()
    users_col = db.users
    user_profile = await safe_find_one(users_col, _build_user_filter(user_id), "user")
    if not user_profile:
        raise HTTPException(status_code=404, detail="User not found")
        
    new_plan_doc = await _generate_and_save_new_plan(user_id, user_profile)
    
    return {
        "success": True,
        "message": "Force generated new weekly meal plan",
        "data": new_plan_doc
    }
