import pandas as pd
import json

df = pd.read_csv('backend-python/data/exercises_processed_repaired.csv')
home_equipment = {'body weight', 'bodyweight', 'dumbbell', 'band', 'resistance band', 'none', 'no equipment'}
home_df = df[df['Equipment'].str.lower().str.strip().isin(home_equipment)]

# Let's see what media URLs they have
media_cols = ['Video_URL', 'Wger_Image_URL']
missing = 0
giphy = 0
for idx, row in home_df.iterrows():
    urls = []
    for col in media_cols:
        if pd.notna(row[col]):
            urls.append(str(row[col]).lower())
    
    valid = False
    for u in urls:
        if 'giphy' in u:
            giphy += 1
            valid = True
            break
        elif u.startswith('http') and u.endswith('.gif'):
            valid = True
            break
        elif u.startswith('http'):
            valid = True
            break
            
    if not valid:
        missing += 1

print(f"Total Home Exercises: {len(home_df)}")
print(f"Missing Media: {missing}")
print(f"Giphy (AI/Generic): {giphy}")

