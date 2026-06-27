import os
import sys

# Ensure backend-python is in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), ".")))

from app.nutrition_engine.engine import NutritionEngineV6
from app.nutrition_engine.variety_tracker import WeeklyVarietyTracker

# Apply the dynamic_meal fix to this run
original_is_duplicate_meal = WeeklyVarietyTracker.is_duplicate_meal
def patched_is_duplicate_meal(self, meal_id, foods, protein_source, carb_source, day_num, meal_type, cuisine=None, cooking_style=None):
    if meal_id == 'dynamic_meal':
        # Temporarily bypass the meal_id check
        had_dynamic = "dynamic_meal" in self.meal_identity_history
        val = self.meal_identity_history.pop("dynamic_meal", None)
        res = original_is_duplicate_meal(self, meal_id, foods, protein_source, carb_source, day_num, meal_type, cuisine, cooking_style)
        if had_dynamic:
            self.meal_identity_history["dynamic_meal"] = val
        return res
    return original_is_duplicate_meal(self, meal_id, foods, protein_source, carb_source, day_num, meal_type, cuisine, cooking_style)

WeeklyVarietyTracker.is_duplicate_meal = patched_is_duplicate_meal

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

print("Generating plan 1...")
plan = engine.generate_plan(profile, user_id="stabilization_test_user_0", week_start="stabilization_week_0")
weekly_plan = plan.get("weekly_plan", {})

# We need to print target vs actual for each day
# Let's get the daily targets planned for the week
from app.nutrition_engine.nutrition_calculator import WeeklyMacroPlanner
planner = WeeklyMacroPlanner()
daily_targets = planner.plan_week(profile)

print("\n=== WEEKLY NUTRITION VALUES AUDIT ===")
print(f"User Profile: Weight 60kg | Goal: Muscle Gain")
print(f"Expected Daily Protein Target: {profile['weight_kg'] * 2.0:.1f}g\n")

print(f"{'Day':<12} | {'Target Cals':<12} | {'Actual Cals':<12} | {'Target Pro':<12} | {'Actual Pro':<12} | {'Pro Dev %':<10}")
print("-" * 85)

for day in sorted(weekly_plan.keys()):
    day_plan = weekly_plan[day]
    target = daily_targets[day]
    
    actual_cals = 0.0
    actual_pro = 0.0
    
    for meal_type, items in day_plan.items():
        for item in items:
            nutrition = item.get("nutrition", {})
            actual_cals += float(nutrition.get("calories", 0.0))
            actual_pro += float(nutrition.get("protein", 0.0))
            
    dev_pct = ((actual_pro - target["protein"]) / target["protein"]) * 100.0
    print(f"{day:<12} | {target['calories']:<12.1f} | {actual_cals:<12.1f} | {target['protein']:<12.1f} | {actual_pro:<12.1f} | {dev_pct:<+10.2f}%")
