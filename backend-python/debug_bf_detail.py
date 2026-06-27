import os
import sys

# Ensure backend-python is in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), ".")))

from app.nutrition_engine.engine import NutritionEngineV6

engine = NutritionEngineV6()
profile = {
    "age": 32,
    "gender": "male",
    "weight_kg": 60,
    "height_cm": 170,
    "activity_level": "moderate",
    "goal": "muscle_gain",
    "diet_type": "NonVeg",
    "cuisine_preferences": ["North Indian", "South Indian", "Pan Indian"],
    "preferred_region": "North Indian"
}

# Patch weekly_optimizer to trace all candidates for Day 3 Breakfast
import app.nutrition_engine.weekly_optimizer as wo
original_generate_weekly_plan = wo.WeeklyOptimizer.generate_weekly_plan

def patched_generate_weekly_plan(self, user_profile):
    # Wrap variety_tracker.is_duplicate_meal to ignore 'dynamic_meal' check
    original_is_duplicate_meal = self.variety_tracker.is_duplicate_meal
    def patched_is_duplicate_meal(meal_id, foods, protein_source, carb_source, day_num, meal_type, cuisine=None, cooking_style=None):
        if meal_id == 'dynamic_meal':
            # Skip the meal ID duplicate check by temporarily removing it from meal_identity_history
            pass
        res = original_is_duplicate_meal(meal_id, foods, protein_source, carb_source, day_num, meal_type, cuisine, cooking_style)
        return res
        
    self.variety_tracker.is_duplicate_meal = patched_is_duplicate_meal
    return original_generate_weekly_plan(self, user_profile)

wo.WeeklyOptimizer.generate_weekly_plan = patched_generate_weekly_plan

# Let's override is_duplicate_meal in variety_tracker.py logic dynamically for this run
from app.nutrition_engine.variety_tracker import WeeklyVarietyTracker
original_is_duplicate_meal_method = WeeklyVarietyTracker.is_duplicate_meal

def patched_is_duplicate_meal_method(self, meal_id, foods, protein_source, carb_source, day_num, meal_type, cuisine=None, cooking_style=None):
    # If meal_id is dynamic_meal, temporarily remove it from meal_identity_history to bypass the meal id check
    had_dynamic = "dynamic_meal" in self.meal_identity_history
    val = self.meal_identity_history.pop("dynamic_meal", None)
    
    res = original_is_duplicate_meal_method(self, meal_id, foods, protein_source, carb_source, day_num, meal_type, cuisine, cooking_style)
    
    if had_dynamic:
        self.meal_identity_history["dynamic_meal"] = val
    return res

WeeklyVarietyTracker.is_duplicate_meal = patched_is_duplicate_meal_method

print("Generating plan 1...")
plan = engine.generate_plan(profile, user_id="stabilization_test_user_0", week_start="stabilization_week_0")
weekly_plan = plan.get("weekly_plan", {})

# Check for consecutive breakfast category collision
prev_breakfast_cat = None
has_collision = False
for day in sorted(weekly_plan.keys()):
    day_plan = weekly_plan[day]
    bf_items = day_plan.get("breakfast", [])
    current_cat = None
    for item in bf_items:
        current_cat = item.get("semantics", {}).get("breakfast_category")
        if current_cat:
            break
    print(f"{day} Breakfast: {[i['food_name'] for i in bf_items]} | Category: {current_cat}")
    if current_cat and prev_breakfast_cat:
        if current_cat == prev_breakfast_cat:
            print(f"  --> COLLISION! Consecutive breakfasts have duplicate category '{current_cat}'")
            has_collision = True
    if current_cat:
        prev_breakfast_cat = current_cat

print(f"\nCollision found? {has_collision}")
