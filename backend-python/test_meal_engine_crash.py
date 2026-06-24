import sys
import os

sys.path.insert(0, r"D:\Final Year Project\githubclone 22 mor\githubclone\ELEVATE_GITHUB\Elevate\backend-python")

from app.workout_engine import WorkoutEngine
from app.meal_engine import get_meal_engine

def test():
    w = WorkoutEngine()
    e = get_meal_engine()
    
    profile = {
        'user_id': '123',
        'age': 30,
        'weight': 70,
        'height': 175,
        'gender': 'Male',
        'goal': 'Weight Loss',
        'dietary_preference': 'Vegetarian',
        'allergies': [],
        'activity_level': 'Moderate',
        'weekly_workout_plan': []
    }
    
    print("Testing generate_weekly_plan...")
    try:
        w_plan = w.generate_weekly_plan(profile)
        print("Success! Got workout plan.")
    except Exception as ex:
        import traceback
        traceback.print_exc()

    print("Testing generate_meal_plan...")
    try:
        plan = e.suggest_daily_meals(profile, 'moderate')
        print("Success! Got meal plan.")
    except Exception as ex:
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test()
