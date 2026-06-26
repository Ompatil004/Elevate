import logging
import hashlib
import json
from typing import Dict, Any, Optional
from datetime import datetime, timezone

logger = logging.getLogger(__name__)

class WeeklyPlanManager:
    """
    Manages caching and persistence of Weekly Nutrition Plans.
    Prevents the engine from regenerating plans unnecessarily.
    """
    def __init__(self, db_client=None):
        self.db = db_client # Motor/PyMongo client

    def _generate_profile_hash(self, user_profile: Dict) -> str:
        """Generates a hash of the user's macro targets, diet type, and restrictions."""
        relevant_data = {
            "target_calories": user_profile.get("target_calories", 0),
            "target_protein": user_profile.get("target_protein", 0),
            "diet_type": user_profile.get("diet_type", "Standard"),
            "allergies": sorted(user_profile.get("allergies", [])),
            "dislikes": sorted(user_profile.get("dislikes", []))
        }
        data_str = json.dumps(relevant_data, sort_keys=True)
        return hashlib.md5(data_str.encode('utf-8')).hexdigest()

    def get_valid_plan(self, user_id: str, user_profile: Dict, week_start: str) -> Optional[Dict]:
        """
        Retrieves a valid plan from the database if one exists and the profile hasn't changed.
        """
        if not self.db:
            return None
            
        try:
            collection = self.db.nutrition_plans
            plan = collection.find_one({
                "user_id": user_id,
                "week_start": week_start,
                "status": "active"
            })
            
            if not plan:
                return None
                
            # Verify profile hasn't changed significantly
            current_hash = self._generate_profile_hash(user_profile)
            if plan.get("profile_hash") != current_hash:
                logger.info(f"User {user_id} profile changed. Invalidating cached plan.")
                return None
                
            logger.info(f"Returning cached plan for user {user_id} for week {week_start}")
            return plan.get("plan_data")
            
        except Exception as e:
            logger.error(f"Error fetching cached plan: {e}")
            return None

    def save_plan(self, user_id: str, user_profile: Dict, week_start: str, plan_data: Dict) -> str:
        """
        Saves a newly generated plan to the database.
        """
        if not self.db:
            return "mock_plan_id"
            
        try:
            collection = self.db.nutrition_plans
            
            # Deactivate older plans for this week
            collection.update_many(
                {"user_id": user_id, "week_start": week_start},
                {"$set": {"status": "archived"}}
            )
            
            plan_doc = {
                "user_id": user_id,
                "week_start": week_start,
                "profile_hash": self._generate_profile_hash(user_profile),
                "plan_version": "v7",
                "created_at": datetime.now(timezone.utc),
                "status": "active",
                "plan_data": plan_data
            }
            
            result = collection.insert_one(plan_doc)
            return str(result.inserted_id)
            
        except Exception as e:
            logger.error(f"Error saving plan to cache: {e}")
            return "error_saving_plan"

    def get_cached_swaps(self, user_id: str, user_profile: Dict, week_start: str, day: int, meal_type: str, meal_hash: str) -> Optional[List[Dict]]:
        """
        Retrieves valid cached swaps for a specific meal, ensuring profile compatibility.
        """
        if not self.db:
            return None
            
        try:
            collection = self.db.meal_swaps
            profile_hash = self._generate_profile_hash(user_profile)
            
            cached = collection.find_one({
                "user_id": user_id,
                "profile_hash": profile_hash,
                "week_start": week_start,
                "day": day,
                "meal_type": meal_type,
                "meal_hash": meal_hash
            })
            
            if cached and "swaps" in cached:
                logger.info(f"Returning cached swaps for {user_id} - {meal_type}")
                return cached["swaps"]
            return None
            
        except Exception as e:
            logger.error(f"Error fetching cached swaps: {e}")
            return None

    def save_cached_swaps(self, user_id: str, user_profile: Dict, week_start: str, day: int, meal_type: str, meal_hash: str, swaps: List[Dict]):
        """
        Saves generated swaps to the cache using a strict tuple key.
        """
        if not self.db:
            return
            
        try:
            collection = self.db.meal_swaps
            profile_hash = self._generate_profile_hash(user_profile)
            
            swap_doc = {
                "user_id": user_id,
                "profile_hash": profile_hash,
                "week_start": week_start,
                "day": day,
                "meal_type": meal_type,
                "meal_hash": meal_hash,
                "swaps": swaps,
                "created_at": datetime.now(timezone.utc)
            }
            
            # Upsert
            collection.update_one({
                "user_id": user_id,
                "profile_hash": profile_hash,
                "week_start": week_start,
                "day": day,
                "meal_type": meal_type,
                "meal_hash": meal_hash
            }, {"$set": swap_doc}, upsert=True)
            
        except Exception as e:
            logger.error(f"Error saving swaps to cache: {e}")
