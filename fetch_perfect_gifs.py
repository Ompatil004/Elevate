import pandas as pd
import requests
import re
from difflib import SequenceMatcher

def normalize_name(name):
    value = str(name).lower().strip()
    value = re.sub(r'\([^)]*\)', ' ', value)
    value = re.sub(r'[^a-z0-9\s]', ' ', value)
    value = re.sub(r'\s+', ' ', value).strip()
    return value

print("Downloading free-exercise-db...")
try:
    resp = requests.get('https://raw.githubusercontent.com/yuhonas/free-exercise-db/main/dist/exercises.json', timeout=15)
    resp.raise_for_status()
    db_data = resp.json()
    print(f"Loaded {len(db_data)} exercises from remote DB.")
except Exception as e:
    print(f"Failed to fetch exercise db: {e}")
    db_data = []

# Build mapping
db_mapping = {}
for ex in db_data:
    name = normalize_name(ex.get('name', ''))
    if name and ex.get('gifUrl'):
        db_mapping[name] = ex['gifUrl']

csv_path = 'backend-python/data/exercises_processed_repaired.csv'
print(f"Loading {csv_path}...")
df = pd.read_csv(csv_path)

print("Mapping GIFs...")
matched_count = 0
unmatched_count = 0

home_equipment = {'body weight', 'bodyweight', 'dumbbell', 'band', 'resistance band', 'none', 'no equipment'}

for idx, row in df.iterrows():
    # Only care about home exercises for the user's specific request
    eq = str(row.get('Equipment', '')).lower().strip()
    if eq not in home_equipment:
        continue

    target_name = normalize_name(row['Name'])
    
    # 1. Exact match
    if target_name in db_mapping:
        df.at[idx, 'Wger_Image_URL'] = db_mapping[target_name]
        df.at[idx, 'Video_URL'] = db_mapping[target_name]
        matched_count += 1
        continue
        
    # 2. Fuzzy match
    best_match = None
    best_score = 0
    for db_name, url in db_mapping.items():
        score = SequenceMatcher(None, target_name, db_name).ratio()
        if score > best_score:
            best_score = score
            best_match = url
            
    if best_score > 0.75 and best_match:
        df.at[idx, 'Wger_Image_URL'] = best_match
        df.at[idx, 'Video_URL'] = best_match
        matched_count += 1
    else:
        # Fallback logic if we can't find a high quality match
        unmatched_count += 1

print(f"Matched {matched_count} exercises.")
print(f"Failed to match {unmatched_count} exercises (will use what they had or placeholders).")

# Backup old
import shutil
shutil.copy(csv_path, csv_path + ".bak")

# Save new
df.to_csv(csv_path, index=False)
print("Saved updated CSV.")

