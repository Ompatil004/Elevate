import os

filepath = 'app/nutrition_engine/candidate_generator.py'
with open(filepath, 'r', encoding='utf-8') as f:
    lines = f.readlines()

for i, line in enumerate(lines):
    if 'return False, "template_mismatch"' in line:
        lines[i] = line.replace('return False, "template_mismatch"', f'print("template_mismatch at line {i+1}"); return False, "template_mismatch"')
    elif 'return False, 0.0, "template_mismatch"' in line:
        lines[i] = line.replace('return False, 0.0, "template_mismatch"', f'print("template_mismatch at line {i+1}"); return False, 0.0, "template_mismatch"')

with open(filepath, 'w', encoding='utf-8') as f:
    f.writelines(lines)
