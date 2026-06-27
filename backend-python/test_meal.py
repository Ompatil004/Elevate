from app.nutrition_engine.engine import NutritionEngineV6
import json
import logging

# Disable verbose debug logs for testing
logging.basicConfig(level=logging.WARNING)

engine = NutritionEngineV6(
    data_dir='data',
    config_dir='config'
)

profile = {
    'diet_type': 'Non-Vegetarian',
    'allergies': [],
    'target_calories': 2000,
    'target_protein': 150,
    'meals_per_day': 4,
    'goal': 'Maintenance',
    'activity_level': 'Moderate',
    'region': 'Maharashtrian'
}

result = engine.generate_plan(profile)
plan = result.get('weekly_plan', {})

if not plan:
    print("Plan generation failed entirely!")
    if "validation_report" in result:
        print("Critical errors:", result["validation_report"].get("critical_errors"))
        print("Warnings:", result["validation_report"].get("warnings"))
else:
    for day, meals in plan.items():
        print(f'\n--- {day} ---')
        day_protein = 0
        day_calories = 0
        for meal_type, items in meals.items():
            if not items:
                print(f'  {meal_type}: EMPTY!')
                continue
            # Extract meal_name from first item or generate combo name
            first_sem = items[0].get("semantics", {})
            meal_name = first_sem.get("meal_name") or (items[0].get("food_name", "") + " Combo" if len(items) > 1 else items[0].get("food_name", ""))
            print(f'  {meal_type}: {meal_name}')
            meal_p = sum(float(item.get('nutrition', {}).get('protein', 0)) for item in items)
            meal_c = sum(float(item.get('nutrition', {}).get('calories', 0)) for item in items)
            day_protein += meal_p
            day_calories += meal_c
            for item in items:
                reg = item.get('semantics', {}).get('cuisine', '')
                print(f'    - {item["food_name"]} ({reg}) [{item.get("calories", 0):.0f} cal, {item.get("protein", 0):.1f} P]')
        print(f'  Day Protein: {day_protein:.1f} / {profile["target_protein"]}')
        print(f'  Day Calories: {day_calories:.1f} / {profile["target_calories"]}')
