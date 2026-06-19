from motor.motor_asyncio import AsyncIOMotorClient
from bson import ObjectId
from datetime import datetime, timezone
from typing import Optional, Dict, Any
import logging

from app.db import get_database

logger = logging.getLogger(__name__)


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)

class ActivityType:
    """Activity type constants for consistent logging"""
    PROFILE_UPDATE = "profile_update"
    WORKOUT_COMPLETE = "workout_complete"
    MEAL_COMPLETE = "meal_complete"
    PLAN_REGENERATION = "plan_regeneration"
    GOAL_CHANGE = "goal_change"
    LOGIN = "login"
    LOGOUT = "logout"
    REGISTER = "register"

async def log_user_activity(
    user_id: str,
    activity_type: str,
    metadata: Dict[str, Any],
    source: str = "api",
    version: str = "1.0",
    ip_address: Optional[str] = None,
    user_agent: Optional[str] = None
):
    """
    Log user activity to MongoDB user_activity collection
    
    Args:
        user_id: User's MongoDB ObjectId (as string)
        activity_type: Type of activity (use ActivityType constants)
        metadata: Activity-specific data
        source: Request source (api/mobile/web)
        version: API version
        ip_address: Client IP (optional)
        user_agent: Client user agent (optional)
    
    Example:
        await log_user_activity(
            user_id="507f1f77bcf86cd799439011",
            activity_type=ActivityType.PROFILE_UPDATE,
            metadata={"fields_updated": ["goal", "weight"]}
        )
    """
    try:
        db = get_database()
        activity_logs = db.user_activity
        
        # Bug #67 fixed: guard against invalid ObjectId strings to prevent uncaught bson.errors.InvalidId
        from bson.errors import InvalidId
        try:
            user_oid = ObjectId(user_id)
        except (InvalidId, TypeError) as id_err:
            logger.error(f"Invalid user_id '{user_id}' passed to log_user_activity: {id_err}")
            return  # Don't propagate — logging failure must not break the main flow

        log_entry = {
            "user_id": user_oid,
            "activity_type": activity_type,
            "metadata": metadata,
            "timestamp": _utcnow(),
            "source": source,
            "version": version
        }
        
        # Add optional fields
        if ip_address:
            log_entry["ip_address"] = ip_address
        if user_agent:
            log_entry["user_agent"] = user_agent
        
        result = await activity_logs.insert_one(log_entry)
        
        if not result.acknowledged:
            logger.error(f"Failed to log activity for user {user_id}: Not acknowledged")
        else:
            logger.debug(f"Activity logged: {activity_type} for user {user_id}")
            
    except Exception as e:
        logger.error(f"Error logging activity for user {user_id}: {e}")
        # Don't raise - logging failure shouldn't break the main operation

