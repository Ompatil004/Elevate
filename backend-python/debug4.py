import os

filepath = 'app/nutrition_engine/candidate_generator.py'
with open(filepath, 'r', encoding='utf-8') as f:
    code = f.read()

code = code.replace(
    'pool = preferred or fallback',
    'if not preferred: print(f"Preferred empty for {role} in {meal_type}! Valid cats: {set([i.get(\'semantics\', {}).get(\'category\') for i in valid_ings])}"); pool = preferred or fallback\n        pool = preferred or fallback'
)

with open(filepath, 'w', encoding='utf-8') as f:
    f.write(code)
