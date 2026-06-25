import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), "backend-python"))

from app.meal_engine import get_meal_engine

engine = get_meal_engine()
user_profile = {
    "age": 25,
    "weight": 70,
    "height": 175,
    "gender": "Male",
    "goal": "Muscle Gain",
    "dietary_preference": "Non-Veg",
    "allergies": [],
    "activity_level": "moderate",
    "weekly_workout_plan": []
}

meal_plan = engine.suggest_daily_meals(user_profile, "moderate")
print("MEALS COUNT:", len(meal_plan.get('meals', [])))
print("MEAL PLAN KEYS:", list(meal_plan.keys()))
