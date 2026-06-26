import os

filepath = 'app/nutrition_engine/candidate_generator.py'
with open(filepath, 'r', encoding='utf-8') as f:
    code = f.read()

code = code.replace(
    'print("template_mismatch at line 774"); return False, "template_mismatch"',
    'print(f"template_mismatch at line 774! Forb: {forb.get(\'role\')} in roles: {roles_in_plate}"); return False, "template_mismatch"'
)

with open(filepath, 'w', encoding='utf-8') as f:
    f.write(code)
