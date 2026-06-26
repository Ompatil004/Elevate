import os

filepath = 'app/nutrition_engine/candidate_generator.py'
with open(filepath, 'r', encoding='utf-8') as f:
    code = f.read()

code = code.replace(
    'logger.warning(',
    'print(f"Rejection stats: {rejection_stats}"); logger.warning('
)

with open(filepath, 'w', encoding='utf-8') as f:
    f.write(code)
