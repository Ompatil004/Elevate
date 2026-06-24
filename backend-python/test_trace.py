import sys
from app.deterministic_meal_engine import MealEngine

profile = {'age': 40, 'weight': 90, 'height': 175, 'gender': 'Male', 'goal': 'Muscle Gain', 'dietary_preference': 'vegan', 'week_offset': 100}
engine = MealEngine()

def trace_calls(frame, event, arg):
    if event == 'call':
        func_name = frame.f_code.co_name
        if func_name in ['generate_weekly_plan', '_generate_candidates', 'optimize_portions', '_validate_plan', '_apply_nutrition_rules']:
            print(f"CALL {func_name}")
    elif event == 'line':
        func_name = frame.f_code.co_name
        if func_name in ['_generate_candidates', 'optimize_portions']:
            pass # print(f"LINE {func_name} {frame.f_lineno}")
    return trace_calls

sys.settrace(trace_calls)
print("Starting generation")
plan = engine.generate_weekly_plan(profile)
print("Done")
