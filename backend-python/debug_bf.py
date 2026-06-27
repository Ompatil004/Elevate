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

# Generate plan 1
print("Generating weekly plan 1...")
plan = engine.generate_plan(profile, user_id="stabilization_test_user_0", week_start="stabilization_week_0")
weekly_plan = plan.get("weekly_plan", {})

for day in sorted(weekly_plan.keys()):
    day_plan = weekly_plan[day]
    bf_items = day_plan.get("breakfast", [])
    print(f"\n--- {day} Breakfast ---")
    for item in bf_items:
        name = item.get("food_name")
        sem = item.get("semantics", {})
        bf_cat = sem.get("breakfast_category")
        cuisine = sem.get("cuisine")
        df = sem.get("dish_family")
        print(f"  Food: {name} | Category: {bf_cat} | Cuisine: {cuisine} | Dish Family: {df}")
