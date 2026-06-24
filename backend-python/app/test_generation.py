import os
from deterministic_meal_engine import MealEngine

profile = {
    'diet_type': 'Vegetarian',
    'cuisine_preferences': ['North Indian', 'South Indian'],
    'tdee': 2000,
    'macro_preference': 'Balanced',
    'id': 'test1',
    'disease_filters': []
}

engine = MealEngine()
try:
    plan = engine.generate_weekly_plan(profile)['plan']
    for day in ['Monday', 'Tuesday']:
        print(f"\n--- {day} ---")
        for meal in ['breakfast', 'lunch', 'dinner', 'snack']:
            print(f"\n{meal.upper()}:")
            if meal in plan[day]:
                for item in plan[day][meal]:
                    print(f"  {item.get('serving_weight', 0):.2f} - {item.get('food_name', '')} ({item.get('calories', 0):.0f} kcal) [Role: {item.get('meal_role', '')}]")
except Exception as e:
    import traceback
    traceback.print_exc()
