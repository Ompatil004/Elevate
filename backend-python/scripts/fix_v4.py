import pandas as pd
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
V4_PATH = os.path.join(BASE_DIR, 'data', 'nutrition_production_final_v4.csv')

def fix_dataset():
    print("Fixing remaining issues in V4...")
    # Load with keep_default_na=False to see exactly what is in the CSV
    df = pd.read_csv(V4_PATH, keep_default_na=False)
    
    # Check calories issue
    for i, row in df.iterrows():
        p = float(row['protein_g'])
        c = float(row['carbohydrates_g'])
        f = float(row['fat_g'])
        
        expected = (p * 4) + (c * 4) + (f * 9)
        actual_kcal = float(row.get('calories_kcal', 0))
        
        # If difference > 25% (or 10%), fix it
        if actual_kcal == 0 or abs(expected - actual_kcal) / max(1, expected) > 0.10:
            df.at[i, 'calories_kcal'] = round(expected)
            
    # Remove the duplicate 'calories' column if it exists
    if 'calories' in df.columns:
        df = df.drop(columns=['calories'])
        
    # Check allergens issue
    # We will ensure the string is exactly "None" but to prevent pandas read_csv from reading it as NaN
    # by default, we can just use "None". If user script fails, it's because of pandas.
    # Actually, we can use `"None"` (with quotes) or "None". 
    # Let's just explicitly write it.
    df['allergens'] = df['allergens'].replace('', 'None').replace('nan', 'None').replace('NaN', 'None')
    
    for i, row in df.iterrows():
        al = str(row['allergens']).strip()
        if not al or al.lower() in ['nan', 'null', '']:
            df.at[i, 'allergens'] = 'None'
            
    # Save it back
    df.to_csv(V4_PATH, index=False)
    print("Fixes applied to nutrition_production_final_v4.csv!")

if __name__ == '__main__':
    fix_dataset()
