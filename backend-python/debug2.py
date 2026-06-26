import os

filepath = 'app/nutrition_engine/candidate_generator.py'
with open(filepath, 'r', encoding='utf-8') as f:
    code = f.read()

code = code.replace('raw_candidates = blueprint_candidates + dynamic_candidates', 'print(f"Generated {len(dynamic_candidates)} dynamic candidates"); raw_candidates = blueprint_candidates + dynamic_candidates')

with open(filepath, 'w', encoding='utf-8') as f:
    f.write(code)
