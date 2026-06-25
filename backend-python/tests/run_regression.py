import sys
import os

# Ensure the backend is in path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.nutrition_engine.engine import NutritionEngineV6
from app.nutrition_engine.nutrition_calculator import WeeklyMacroPlanner

import logging
logging.basicConfig(level=logging.DEBUG)

PROFILES = [
    {
        "name": "Weight Loss (Veg)",
        "profile": {
            "weight": 85, "goal": "Weight Loss", "diet_type": "Vegetarian", "age": 30, "gender": "Female", "days_per_week": 3, "appetite": "Average"
        }
    },
    {
        "name": "Weight Loss (Non-Veg)",
        "profile": {
            "weight": 90, "goal": "Weight Loss", "diet_type": "Non-Veg", "age": 35, "gender": "Male", "days_per_week": 4, "appetite": "Large"
        }
    },
    {
        "name": "Maintenance",
        "profile": {
            "weight": 70, "goal": "Maintenance", "diet_type": "Vegetarian", "age": 28, "gender": "Male", "days_per_week": 3, "appetite": "Average"
        }
    },
    {
        "name": "Muscle Gain",
        "profile": {
            "weight": 75, "goal": "Muscle Gain", "diet_type": "Non-Veg", "age": 25, "gender": "Male", "days_per_week": 5, "appetite": "Large"
        }
    },
    {
        "name": "High-Protein Vegetarian",
        "profile": {
            "weight": 65, "goal": "Muscle Gain", "diet_type": "Vegetarian", "age": 27, "gender": "Female", "days_per_week": 4, "appetite": "Average"
        }
    }
]

def run_regression():
    print("Loading Engine components...")
    
    success = True
    for test in PROFILES:
        print(f"\n--- Running Regression: {test['name']} ---")
        
        try:
            # We instantiate per-profile to reset variety tracker state cleanly
            engine = NutritionEngineV6(data_dir="data", config_dir="config")
            
            # Using generate_plan from engine
            result = engine.generate_plan(test["profile"], user_id="regression_user", week_start="2026-06-22")
            plan = result.get("weekly_plan") or {}
            
            if not plan:
                print("FAILED: Plan is empty.")
                print("Validation Report:", result.get("validation_report"))
                success = False
                continue
            
            # Validation: Macros within tolerance
            macro_planner = WeeklyMacroPlanner()
            daily_targets = macro_planner.plan_week(test["profile"])
            
            print(f"SUCCESS: Generated {len(plan.get('days', []))} days.")
            
            # Just some basic macro checks on the generated stats vs target
            for day, day_data in plan.items():
                if day_data is None:
                    continue
                day_cals = sum(
                    item.get("nutrition", {}).get("calories", 0) 
                    for meal in day_data.values() for item in meal
                )
                target_cals = daily_targets.get(day, daily_targets).get("calories", 0)
                if target_cals > 0:
                    dev = abs(day_cals - target_cals) / target_cals * 100
                    if dev > 15:
                        print(f"WARNING: {day} calories {day_cals:.0f} deviates from {target_cals:.0f} by {dev:.1f}%")
            
        except Exception as e:
            print(f"FAILED: Exception raised - {str(e)}")
            success = False

    if not success:
        sys.exit(1)
    else:
        print("\n[SUCCESS] All Regression Tests Passed!")
        sys.exit(0)

if __name__ == "__main__":
    run_regression()
