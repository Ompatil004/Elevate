import sys, json
sys.path.append('d:/Final Year Project/githubclone 22 mor/githubclone/ELEVATE_GITHUB/Elevate/backend-python')
from app.nutrition_engine.engine import NutritionEngineV6

try:
    engine = NutritionEngineV6()
    profile = {
        'age': 25, 'weight': 70, 'height': 175, 'gender': 'male',
        'goal': 'Muscle Gain', 'dietary_preference': 'veg',
        'allergies': [], 'activity_level': 'active', 'weekly_workout_plan': []
    }
    plan = engine.generate_plan(profile)
    with open('test_plan.json', 'w') as f:
        json.dump(plan, f, indent=2)
    print('SUCCESS')
except Exception as e:
    import traceback
    with open('test_err.log', 'w') as f:
        f.write(traceback.format_exc())
    print('FAILED')
