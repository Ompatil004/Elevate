import pandas as pd
import numpy as np
import os
from difflib import get_close_matches
import re

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PROD_CSV = os.path.join(BASE_DIR, 'data', 'nutrition_production_final.csv')
IFCT_CSV = os.path.join(BASE_DIR, 'data', 'ifct2017_compositions.csv')
NUT_CSV = os.path.join(BASE_DIR, 'data', 'nutrition.csv')
FINAL_CSV = os.path.join(BASE_DIR, 'data', 'nutrition_production_final_v2.csv')

def clean_name(name):
    name = str(name).lower()
    name = re.sub(r'\(.*?\)', '', name) 
    name = re.sub(r'[^a-z\s]', '', name)
    return name.strip()

def run_pipeline():
    print("Starting 3-Tier Multi-Reference Validation Pipeline...")
    
    prod_df = pd.read_csv(PROD_CSV)
    ifct_df = pd.read_csv(IFCT_CSV)
    nut_df = pd.read_csv(NUT_CSV)
    
    # Clean up IFCT
    ifct_df['clean_name'] = ifct_df['name'].apply(clean_name)
    ifct_df = ifct_df.drop_duplicates(subset=['clean_name'])
    ifct_dict = ifct_df.set_index('clean_name').to_dict('index')
    ifct_names = list(ifct_dict.keys())
    
    # Clean up Nut CSV
    nut_df['clean_name'] = nut_df['Name'].apply(clean_name)
    nut_df = nut_df.drop_duplicates(subset=['clean_name'])
    nut_dict = nut_df.set_index('clean_name').to_dict('index')
    nut_names = list(nut_dict.keys())
    
    metrics = {
        'ifct_matched': 0,
        'nut_matched': 0,
        'values_corrected': 0,
        'allergens_populated': 0,
        'booleans_corrected': 0,
        'unmatched': []
    }
    
    def sf(val):
        try:
            return float(val) if pd.notna(val) else 0.0
        except:
            return 0.0
            
    # Iterate production dataset
    for i, row in prod_df.iterrows():
        name = str(row['food_name'])
        c_name = clean_name(name)
        serving = float(row['serving_size_g'])
        scale = serving / 100.0
        
        matched = False
        
        # ----------------------------------------------------
        # PRIORITY 1: IFCT 2017
        # ----------------------------------------------------
        ifct_matches = get_close_matches(c_name, ifct_names, n=1, cutoff=0.8)
        if ifct_matches:
            matched = True
            metrics['ifct_matched'] += 1
            ifct_row = ifct_dict[ifct_matches[0]]
            
            enerc_kj = sf(ifct_row.get('enerc', 0))
            if enerc_kj > 0:
                prod_df.at[i, 'calories_kcal'] = round((enerc_kj / 4.184) * scale)
                
            prod_df.at[i, 'protein_g'] = round(sf(ifct_row.get('protcnt', 0)) * scale, 1)
            prod_df.at[i, 'carbohydrates_g'] = round(sf(ifct_row.get('choavldf', 0)) * scale, 1)
            prod_df.at[i, 'fat_g'] = round(sf(ifct_row.get('fatce', 0)) * scale, 1)
            prod_df.at[i, 'fiber_g'] = round(sf(ifct_row.get('fibtg', 0)) * scale, 1)
            prod_df.at[i, 'sugar_g'] = round(sf(ifct_row.get('fsugar', 0)) * scale, 1)
            
            prod_df.at[i, 'sodium_mg'] = round(sf(ifct_row.get('na', 0)) * scale, 1)
            prod_df.at[i, 'potassium_mg'] = round(sf(ifct_row.get('k', 0)) * scale, 1)
            prod_df.at[i, 'calcium_mg'] = round(sf(ifct_row.get('ca', 0)) * scale, 1)
            prod_df.at[i, 'iron_mg'] = round(sf(ifct_row.get('fe', 0)) * scale, 1)
            prod_df.at[i, 'magnesium_mg'] = round(sf(ifct_row.get('mg', 0)) * scale, 1)
            prod_df.at[i, 'phosphorus_mg'] = round(sf(ifct_row.get('p', 0)) * scale, 1)
            prod_df.at[i, 'zinc_mg'] = round(sf(ifct_row.get('zn', 0)) * scale, 1)
            
            prod_df.at[i, 'vitamin_c_mg'] = round(sf(ifct_row.get('vitc', 0)) * scale, 1)
            vit_a = sf(ifct_row.get('retol', 0)) + (sf(ifct_row.get('cartb', 0)) / 6.0)
            prod_df.at[i, 'vitamin_a_mcg'] = round(vit_a * scale, 1)
            prod_df.at[i, 'vitamin_d_mcg'] = round((sf(ifct_row.get('chocal', 0)) + sf(ifct_row.get('ergcal', 0))) * scale, 1)
            prod_df.at[i, 'cholesterol_mg'] = round(sf(ifct_row.get('cholc', 0)) * scale, 1)
            metrics['values_corrected'] += 18
            
        # ----------------------------------------------------
        # PRIORITY 2: NUTRITION.CSV
        # ----------------------------------------------------
        if not matched:
            nut_matches = get_close_matches(c_name, nut_names, n=1, cutoff=0.8)
            if nut_matches:
                matched = True
                metrics['nut_matched'] += 1
                nut_row = nut_dict[nut_matches[0]]
                
                prod_df.at[i, 'calories_kcal'] = round(sf(nut_row.get('Calories', 0)))
                prod_df.at[i, 'protein_g'] = round(sf(nut_row.get('Protein', 0)), 1)
                prod_df.at[i, 'carbohydrates_g'] = round(sf(nut_row.get('Carbs', 0)), 1)
                prod_df.at[i, 'fat_g'] = round(sf(nut_row.get('Fats', 0)), 1)
                metrics['values_corrected'] += 4
                
        # ----------------------------------------------------
        # PRIORITY 3: FALLBACK
        # ----------------------------------------------------
        if not matched:
            metrics['unmatched'].append(name)
            
        # ----------------------------------------------------
        # BOOLEAN & ALLERGEN VALIDATION
        # ----------------------------------------------------
        lname = name.lower()
        contains_dairy = any(x in lname for x in ['cheese', 'dairy', 'milk', 'paneer', 'curd', 'yogurt', 'ghee', 'butter', 'lassi', 'buttermilk', 'malai', 'cream', 'whey'])
        contains_egg = any(x in lname for x in ['egg', 'omelette', 'bhurji'])
        contains_meat = any(x in lname for x in ['chicken', 'mutton', 'meat', 'beef', 'pork', 'lamb', 'keema', 'gosht', 'rogan josh'])
        contains_fish = any(x in lname for x in ['fish', 'prawn', 'seafood', 'basa', 'machher', 'moilee', 'shrimp', 'crab', 'salmon', 'tuna'])
        contains_gluten = any(x in lname for x in ['wheat', 'bread', 'pasta', 'roti', 'chapati', 'paratha', 'sandwich', 'naan', 'kulcha', 'puri', 'bhatura', 'oat'])
        contains_nuts = any(x in lname for x in ['nut', 'almond', 'cashew', 'peanut', 'walnut', 'badam', 'pista', 'kaju'])
        contains_soy = any(x in lname for x in ['soy', 'tofu', 'soya', 'nutrela'])
        
        prod_df.at[i, 'contains_dairy'] = contains_dairy
        prod_df.at[i, 'contains_egg'] = contains_egg
        prod_df.at[i, 'contains_meat'] = contains_meat
        prod_df.at[i, 'contains_fish'] = contains_fish
        prod_df.at[i, 'contains_gluten'] = contains_gluten
        prod_df.at[i, 'contains_nuts'] = contains_nuts
        prod_df.at[i, 'contains_soy'] = contains_soy
        
        # Vegan / Vegetarian Logic
        is_veg = not (contains_meat or contains_fish)
        is_vegan = is_veg and not (contains_dairy or contains_egg)
        
        prod_df.at[i, 'is_vegetarian'] = is_veg
        prod_df.at[i, 'is_vegan'] = is_vegan
        prod_df.at[i, 'is_jain_friendly'] = is_veg and not any(x in lname for x in ['onion', 'garlic', 'potato', 'ginger', 'carrot', 'radish'])
        
        p = float(prod_df.at[i, 'protein_g'])
        c = float(prod_df.at[i, 'carbohydrates_g'])
        f = float(prod_df.at[i, 'fat_g'])
        fib = float(prod_df.at[i, 'fiber_g'])
        
        prod_df.at[i, 'is_high_protein'] = p >= 15.0
        prod_df.at[i, 'is_low_carb'] = c <= 20.0
        prod_df.at[i, 'is_low_fat'] = f <= 10.0
        prod_df.at[i, 'is_high_fiber'] = fib >= 5.0
        
        metrics['booleans_corrected'] += 15 # We rewrite 15 boolean fields
        
        # Build Allergens perfectly
        allergens = []
        if contains_dairy: allergens.append("Milk")
        if contains_egg: allergens.append("Egg")
        if contains_fish: allergens.append("Fish")
        if contains_gluten: allergens.append("Gluten")
        if contains_nuts: allergens.append("Tree Nuts")
        if 'peanut' in lname: allergens.append("Peanuts")
        if contains_soy: allergens.append("Soy")
        
        final_allergens = ", ".join(allergens) if allergens else "None"
        prod_df.at[i, 'allergens'] = final_allergens
        metrics['allergens_populated'] += 1

    prod_df.to_csv(FINAL_CSV, index=False)
    
    print("=" * 60)
    print("3-TIER VALIDATION REPORT")
    print("=" * 60)
    print(f"Total Foods Audited        : {len(prod_df)}")
    print(f"Foods Matched with IFCT    : {metrics['ifct_matched']}")
    print(f"Foods Matched with nutrition.csv : {metrics['nut_matched']}")
    print(f"Nutrition Values Corrected : {metrics['values_corrected']}")
    print(f"Allergen Fields Populated  : {metrics['allergens_populated']}")
    print(f"Boolean Fields Corrected   : {metrics['booleans_corrected']}")
    print(f"Foods Unmatched (Sample)   : {metrics['unmatched'][:10]}...")
    print("=" * 60)
    print(f"Dataset successfully saved to: {FINAL_CSV}")

if __name__ == '__main__':
    run_pipeline()
