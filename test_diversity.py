import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), "backend-python"))

from app.meal_engine import get_meal_engine

engine = get_meal_engine()
user_profile = {
    "age": 30,
    "weight": 70.0,
    "height": 175.0,
    "gender": "male",
    "goal": "maintenance",
    "dietary_preference": "Non-Veg",
    "allergies": [],
    "activity_level": "moderate",
    "weekly_workout_plan": []
}

weekly = engine.generate_meal_plan(user_profile)
for day, meals in weekly.get('weekly_plan', {}).items():
    print(f"=== {day} ===")
    for meal_type, items in meals.items():
        names = [i.get('name') for i in items]
        print(f"  {meal_type}: {names}")
