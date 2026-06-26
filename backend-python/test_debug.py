import os

filepath = 'tests/test_candidate_generator.py'
with open(filepath, 'r', encoding='utf-8') as f:
    code = f.read()

code = code.replace(
    'candidate = self.generator.generate_candidates(',
    'cands = self.generator.generate_candidates('
)
code = code.replace(
    'day_seed=42\n        )[0]',
    'day_seed=42\n        )\n        candidate = cands[0]\n        print(f"CANDS LEN: {len(cands)}")\n        print(f"CANDIDATE: {candidate}")'
)

with open(filepath, 'w', encoding='utf-8') as f:
    f.write(code)
