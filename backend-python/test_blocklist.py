import json
import re
from app.deterministic_meal_engine import FOOD_NAME_BLOCKLIST

blocklist_str = '|'.join(r'\b' + re.escape(t) + r'\b' for t in FOOD_NAME_BLOCKLIST)
blocklist_pattern = re.compile(blocklist_str)

with open('data/ingredient_database.json', 'r', encoding='utf-8') as f:
    foods = json.load(f)

for fid, node in foods.items():
    name = node.get('food_name', '').lower()
    if blocklist_pattern.search(name):
        print(f"MATCH: {name}")
