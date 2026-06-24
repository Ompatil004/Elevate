import time
import json
import statistics
import functools
from app.deterministic_meal_engine import MealEngine, optimize_portions, score_meal, build_swap_options

timers = {}

def track_time(name):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            start = time.perf_counter()
            result = func(*args, **kwargs)
            end = time.perf_counter()
            elapsed = (end - start) * 1000
            if name not in timers:
                timers[name] = []
            timers[name].append(elapsed)
            return result
        return wrapper
    return decorator

# Patch the engine methods
MealEngine.calculate_daily_targets = track_time("Daily Macro Calculator")(MealEngine.calculate_daily_targets)
MealEngine._generate_candidates = track_time("Weekly Candidate Generation")(MealEngine._generate_candidates)
import app.deterministic_meal_engine as dme
dme.optimize_portions = track_time("Portion Optimization")(dme.optimize_portions)
dme.score_meal = track_time("Meal Scoring")(dme.score_meal)
MealEngine._validate_plan = track_time("Validator")(MealEngine._validate_plan)
dme.build_swap_options = track_time("Swap Generation")(dme.build_swap_options)

# We need to track Correction Passes separately.
# I'll just run it and we'll see the total time.

engine = MealEngine()

profile = {
    "age": 30,
    "weight": 80,
    "height": 180,
    "gender": "Male",
    "goal": "Muscle Gain",
    "dietary_preference": "nonveg",
    "allergies": ["nuts"],
    "activity_level": "Active",
    "weekly_workout_plan": [{"type": "workout"} for _ in range(5)]
}

print("Starting generation...")
start_total = time.perf_counter()
plan = engine.generate_weekly_plan(profile)

# Also time JSON serialization
start_json = time.perf_counter()
json_str = json.dumps(plan)
end_json = time.perf_counter()
timers["JSON Serialization"] = [(end_json - start_json) * 1000]

end_total = time.perf_counter()

print("\n--- PERFORMANCE REPORT ---")
for name, times in timers.items():
    total_time = sum(times)
    count = len(times)
    avg_time = total_time / count
    print(f"{name.ljust(35)} {total_time:.2f} ms (called {count} times, avg {avg_time:.2f} ms)")

print(f"Total .......................... {(end_total - start_total) * 1000:.2f} ms")
