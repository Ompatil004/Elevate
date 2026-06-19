"""
Audit the nutrition dataset and generate food_blacklist.json
Identifies items that should NEVER appear in a fitness meal plan.
"""
import pandas as pd
import json
import re
import os

df = pd.read_csv('data/nutrition_processed.csv')

blacklist = set()

# Category A: Junk / Unhealthy / Alcohol
junk_patterns = [
    r'\bice cream\b', r'\bicecream\b', r'\bgin\b', r'\brum\b', r'\bwine\b',
    r'\bbeer\b', r'\bwhiskey\b', r'\bvodka\b', r'\bcocktail\b', r'\blem-o-gin\b',
    r'\bcold coffee with ice cream\b',
]
junk_regex = re.compile('|'.join(junk_patterns), re.IGNORECASE)

# Category B: Pure desserts/cakes/cookies/biscuits that are > 500 cal
dessert_patterns = [
    r'\bcake\b', r'\bcookie\b', r'\bbiscuit\b', r'\bicing\b',
    r'\bpudding\b', r'\btart\b', r'\bpastry\b', r'\bpie\b',
    r'\bgateaux?\b', r'\bmousse\b', r'\bflan\b', r'\btrifle\b',
    r'\bmeringue\b', r'\bscone\b', r'\bmuffin\b', r'\bcupcake\b',
    r'\bshortbread\b', r'\bchristmas\b', r'\bchocolate\b.*\b(drop|shell|chip)\b',
]
dessert_regex = re.compile('|'.join(dessert_patterns), re.IGNORECASE)

# Category C: Pure cooking sauces / condiments / dressings with high calories
sauce_patterns = [
    r'\btartare sauce\b', r'\bmayonnaise\b', r'\bfrench dressing\b',
    r'\bwhite sauce\b', r'\bcheese sauce\b', r'\bmustard sauce\b',
    r'\bhot cherry sauce\b', r'\bbread sauce\b', r'\bbarbeque sauce\b',
    r'\bgreen chilli sauce\b', r'\btomato ketchup\b', r'\bpasta.*sauce\b',
    r'\bglace icing\b', r'\bbutter icing\b', r'\bchocolate.*icing\b',
    r'\bjam filling\b', r'\broyal icing\b', r'\bfondant\b',
]
sauce_regex = re.compile('|'.join(sauce_patterns), re.IGNORECASE)

count_a = count_b = count_c = count_d = 0

for _, row in df.iterrows():
    name = str(row['Name'])
    cal = float(row.get('calories', 0) or 0)
    fat = float(row.get('total_fat', 0) or 0)
    
    # Category A: Junk/Alcohol
    if junk_regex.search(name):
        blacklist.add(name)
        count_a += 1
        continue
    
    # Category B: Desserts/cakes/cookies > 400 cal
    if dessert_regex.search(name) and cal > 400:
        blacklist.add(name)
        count_b += 1
        continue
    
    # Category C: Pure sauces/condiments
    if sauce_regex.search(name):
        blacklist.add(name)
        count_c += 1
        continue
    
    # Category D: Extreme calories (> 1000 cal per row = batch recipe, not serving)
    if cal > 900:
        blacklist.add(name)
        count_d += 1
        continue

print(f"Category A (Junk/Alcohol): {count_a}")
print(f"Category B (Desserts > 400 cal): {count_b}")
print(f"Category C (Sauces/Condiments): {count_c}")
print(f"Category D (Extreme cal > 900): {count_d}")
print(f"Total blacklisted: {len(blacklist)}")
print(f"Remaining: {len(df) - len(blacklist)} / {len(df)}")

# Save
output_path = os.path.join('data', 'food_blacklist.json')
with open(output_path, 'w', encoding='utf-8') as f:
    json.dump(sorted(list(blacklist)), f, ensure_ascii=False, indent=2)

print(f"\nSaved to {output_path}")

# Print sample
print("\n=== SAMPLE BLACKLISTED ITEMS ===")
for item in sorted(list(blacklist))[:30]:
    row = df[df['Name'] == item].iloc[0]
    print(f"  [{row['Type']:9s}] cal={row['calories']:5.0f}  {item}")
