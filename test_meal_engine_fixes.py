import sys
import os

# Add backend app directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), "backend-python"))

from app.meal_engine import get_meal_engine

if __name__ == "__main__":
    engine = get_meal_engine()
    
    # 1. Test swap options
    profile = {"diet_type": "NonVeg"}
    swaps = engine.get_swap_options("Chicken Sandwich", "lunch", profile, limit=3)
    print("Swaps for Chicken Breast:", [s['name'] for s in swaps])
    assert len(swaps) > 0, "Swaps should not be empty"
    
    # 2. Test suggest_daily_meals with scale factor
    profile['goal'] = "Muscle Gain"
    profile['weekly_workout_plan'] = [
        {"day_of_week": 0, "type": "workout", "intensity": "very_hard", "exercises": [{"sets": 4} for _ in range(8)]},
        {"day_of_week": 1, "type": "workout", "intensity": "moderate"},
        {"day_of_week": 2, "type": "workout", "intensity": "very_hard"},
        {"day_of_week": 3, "type": "rest"},
    ]
    meals = engine.suggest_daily_meals(profile, workout_intensity="moderate")
    
    print("\n--- Daily Meals Output ---")
    for meal in meals.get("meals", [])[:3]:
        print(f"{meal['meal_type']} - {meal['name']} | Cals: {meal['calories']} | Pro: {meal['protein']}")
        
    print("\n--- Weekly Plan Check ---")
    weekly_plan = meals.get("weekly_plan", {})
    for day, day_meals in list(weekly_plan.items())[:3]:
        print(f"\nDay: {day}")
        for meal_type, items in day_meals.items():
            names = [i['name'] for i in items]
            print(f"  {meal_type}: {names}")

    print("\nAll tests pass!")
