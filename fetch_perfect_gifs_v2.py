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

base_img_url = "https://raw.githubusercontent.com/yuhonas/free-exercise-db/main/exercises/"
db_mapping = {}
for ex in db_data:
    name = normalize_name(ex.get('name', ''))
    images = ex.get('images', [])
    if name and images:
        # Convert to full URLs and join by comma
        full_urls = [base_img_url + img for img in images]
        db_mapping[name] = ",".join(full_urls)

csv_path = 'backend-python/data/exercises_processed_repaired.csv'
print(f"Loading {csv_path}...")
df = pd.read_csv(csv_path)

print("Mapping Media...")
matched_count = 0
unmatched_count = 0

home_equipment = {'body weight', 'bodyweight', 'dumbbell', 'band', 'resistance band', 'none', 'no equipment'}

for idx, row in df.iterrows():
    eq = str(row.get('Equipment', '')).lower().strip()
    if eq not in home_equipment:
        continue

    target_name = normalize_name(row['Name'])
    
    # Check if they already have a valid GIF
    current_media = str(row.get('Wger_Image_URL', ''))
    if current_media.endswith('.gif') and 'giphy' not in current_media and 'gfycat' not in current_media:
        continue # Keep existing good GIF

    # 1. Exact match
    if target_name in db_mapping:
        df.at[idx, 'Wger_Image_URL'] = db_mapping[target_name]
        df.at[idx, 'Video_URL'] = '' # clear video so it uses images
        matched_count += 1
        continue
        
    # 2. Fuzzy match
    best_match = None
    best_score = 0
    for db_name, urls in db_mapping.items():
        score = SequenceMatcher(None, target_name, db_name).ratio()
        if score > best_score:
            best_score = score
            best_match = urls
            
    if best_score > 0.80 and best_match:
        df.at[idx, 'Wger_Image_URL'] = best_match
        df.at[idx, 'Video_URL'] = ''
        matched_count += 1
    else:
        unmatched_count += 1

print(f"Matched {matched_count} home exercises.")
print(f"Failed to match {unmatched_count} home exercises.")

import shutil
shutil.copy(csv_path, csv_path + ".bak2")
df.to_csv(csv_path, index=False)
print("Saved updated CSV.")
