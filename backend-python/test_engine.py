from app.nutrition_engine.engine import NutritionEngineV6
import json
import logging

logging.basicConfig(level=logging.INFO)

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

if 'weekly_plan' in result:
    plan = result['weekly_plan']
else:
    plan = result

import json
with open('debug_plan.json', 'w') as f:
    json.dump(result, f, indent=2)

print("Plan saved to debug_plan.json")
