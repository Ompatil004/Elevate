import os

filepath = 'tests/test_candidate_generator.py'
with open(filepath, 'r', encoding='utf-8') as f:
    code = f.read()

code = code.replace(
    'roles_in_plate = [item.get("semantics", {}).get("meal_role", "") for item in candidate]',
    'roles_in_plate = [item.get("template_role") or item.get("semantics", {}).get("meal_role", "") for item in candidate]'
)

with open(filepath, 'w', encoding='utf-8') as f:
    f.write(code)
