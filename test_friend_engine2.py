import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), "backend-python"))

from app.deterministic_meal_engine import MealEngine

engine = MealEngine()
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
weekly = engine.generate_weekly_plan(user_profile)
print("KEYS:", list(weekly.keys()))
if 'weekly_plan' in weekly:
    print("WEEKLY_PLAN TYPE:", type(weekly['weekly_plan']))
    if isinstance(weekly['weekly_plan'], dict):
        print("WEEKLY_PLAN KEYS:", list(weekly['weekly_plan'].keys()))
    elif isinstance(weekly['weekly_plan'], list):
        print("WEEKLY_PLAN LEN:", len(weekly['weekly_plan']))
