import logging
from typing import Dict, Any, List

logger = logging.getLogger(__name__)

class DailyRuleEngine:
    """
    Contextual decision maker. Sits above Candidate Generator.
    Reads contextual state (Day, Season, Weather, Gym status) and outputs strict constraints.
    """
    
    def __init__(self):
        pass
        
    def evaluate_context(self, user_profile: Dict, day_index: int, meal_type: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Evaluate context for a specific meal on a specific day.
        
        Args:
            user_profile: The user's preferences, goals, etc.
            day_index: 0=Monday, 6=Sunday
            meal_type: Breakfast, Lunch, Snack, Dinner, etc.
            context: External context like season, weather, workout schedule.
            
        Returns:
            A dictionary of constraints to be passed to the CandidateGenerator.
        """
        if context is None:
            context = {}
            
        constraints = {
            "max_prep_time": 999,
            "prefer_warm": False,
            "carb_ratio": "medium",
            "allowed_complexity": [1, 10], # Min, Max
            "tags_required": [],
            "tags_forbidden": []
        }
        
        is_weekend = (day_index >= 5)
        
        # 1. Day of week rules
        if is_weekend:
            # Weekends allow more elaborate cooking
            constraints["allowed_complexity"] = [1, 10]
            constraints["max_prep_time"] = 60
        else:
            # Weekdays
            if meal_type == "Breakfast":
                constraints["max_prep_time"] = 15
                constraints["allowed_complexity"] = [1, 4]
                constraints["tags_required"].append("quick")
            elif meal_type == "Lunch":
                constraints["max_prep_time"] = 30
                constraints["allowed_complexity"] = [1, 6]
                constraints["tags_required"].append("office_friendly")
                
        # 2. Workout Rules
        has_workout_today = context.get("workout_today", False)
        if has_workout_today:
            if meal_type in ["Pre Workout", "Post Workout"]:
                constraints["max_prep_time"] = 10
                constraints["allowed_complexity"] = [1, 3]
            if meal_type in ["Lunch", "Dinner"]:
                constraints["carb_ratio"] = "high"
                constraints["tags_required"].append("high_protein")
        else:
            if meal_type in ["Lunch", "Dinner"] and user_profile.get("goal") == "Weight Loss":
                constraints["carb_ratio"] = "low"
                
        # 3. Weather / Season Rules
        season = context.get("season", "Summer")
        if season == "Winter" or context.get("weather") == "Rainy":
            constraints["prefer_warm"] = True
            constraints["tags_forbidden"].append("cold")
            
        if season == "Summer":
            if meal_type in ["Snack", "Breakfast"]:
                constraints["tags_required"].append("hydrating")
                
        logger.debug(f"Daily rules generated for Day {day_index} {meal_type}: {constraints}")
        return constraints
