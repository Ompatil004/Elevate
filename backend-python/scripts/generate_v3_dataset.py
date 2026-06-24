import pandas as pd
import numpy as np
import re
import random
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
INPUT_CSV = os.path.join(BASE_DIR, 'data', 'nutrition_production_v2.csv')
OUTPUT_CSV = os.path.join(BASE_DIR, 'data', 'nutrition_production_v3.csv')

def rewrite_description(row):
    name = str(row['food_name']).title()
    category = str(row['category'])
    region = str(row['region'])
    p = float(row['protein_g'])
    f = float(row['fat_g'])
    c = float(row['carbohydrates_g'])
    
    # Building features
    features = []
    if p > 15: features.append("is an excellent source of protein")
    elif p > 8: features.append("provides a good amount of protein")
    
    if f < 5: features.append("is wonderfully low in fat")
    if c > 30: features.append("is rich in energizing carbohydrates")
    elif c < 15: features.append("is a fantastic low-carb option")
    
    if row['is_high_fiber']: features.append("is packed with digestive fiber")
    
    feat_str = ""
    if len(features) > 1:
        feat_str = ", ".join(features[:-1]) + ", and " + features[-1]
    elif len(features) == 1:
        feat_str = features[0]
    else:
        feat_str = "offers a well-rounded nutritional profile"

    templates = [
        f"{name} is a beloved {category.lower()} dish from {region}. It {feat_str}, making it highly suitable for {row['goal'].lower()} goals.",
        f"A classic {region} staple, {name} is widely enjoyed for its taste and health benefits. Naturally, it {feat_str}.",
        f"Enjoy the authentic flavors of {name}. As a traditional {category.lower()}, it {feat_str} and is perfect for a {row['goal'].lower()} diet.",
        f"Incorporate {name} into your routine! This {region} favorite {feat_str}.",
        f"{name} provides the perfect balance of tradition and health. Originating from {region}, this {category.lower()} {feat_str}."
    ]
    
    # Special for beverages
    if 'Beverage' in category or 'Beverage' in str(row['meal_type']):
        bev_templates = [
            f"Refresh yourself with {name}. This beverage {feat_str} and fits seamlessly into a {row['goal'].lower()} plan.",
            f"{name} is a light and hydrating drink. It {feat_str}, ideal for {row['goal'].lower()}."
        ]
        return random.choice(bev_templates)
        
    return random.choice(templates)

def run_audit():
    print("Starting V3 Dataset Audit and Correction...")
    
    df = pd.read_csv(INPUT_CSV)
    
    for i, row in df.iterrows():
        name = str(row['food_name']).lower()
        cat = str(row['category']).lower()
        
        # 1. Light Beverage Macro Override
        if any(x in name for x in ['coffee', 'tea', 'espresso', 'lemon water', 'coconut water', 'jaljeera', 'aam panna']) and 'milkshake' not in name:
            if 'sugar' not in name and 'sweet' not in name:
                df.at[i, 'carbohydrates_g'] = min(float(row['carbohydrates_g']), 3.0)
                df.at[i, 'sugar_g'] = 0.0
            df.at[i, 'protein_g'] = min(float(row['protein_g']), 1.0)
            df.at[i, 'fat_g'] = min(float(row['fat_g']), 0.5)
            df.at[i, 'fiber_g'] = 0.0

        p = float(df.at[i, 'protein_g'])
        c = float(df.at[i, 'carbohydrates_g'])
        f = float(df.at[i, 'fat_g'])
        
        # 2. Strict Calorie Enforcement
        cal = round((p * 4.0) + (c * 4.0) + (f * 9.0))
        df.at[i, 'calories_kcal'] = cal
        
        # 3. Dietary Flag & Allergen Deep Audit
        contains_dairy = any(x in name for x in ['cheese', 'dairy', 'milk', 'paneer', 'curd', 'yogurt', 'ghee', 'butter', 'lassi', 'buttermilk'])
        contains_egg = any(x in name for x in ['egg', 'omelette'])
        contains_meat = any(x in name for x in ['chicken', 'mutton', 'meat', 'beef', 'pork'])
        contains_fish = any(x in name for x in ['fish', 'prawn', 'seafood', 'basa', 'machher', 'moilee'])
        contains_gluten = any(x in name for x in ['wheat', 'bread', 'pasta', 'roti', 'chapati', 'paratha', 'sandwich'])
        contains_nuts = any(x in name for x in ['nut', 'almond', 'cashew', 'peanut', 'walnut', 'badam'])
        contains_soy = any(x in name for x in ['soy', 'tofu', 'soya'])
        
        df.at[i, 'contains_dairy'] = contains_dairy
        df.at[i, 'contains_egg'] = contains_egg
        df.at[i, 'contains_meat'] = contains_meat
        df.at[i, 'contains_fish'] = contains_fish
        df.at[i, 'contains_gluten'] = contains_gluten
        df.at[i, 'contains_nuts'] = contains_nuts
        df.at[i, 'contains_soy'] = contains_soy
        
        is_veg = not (contains_meat or contains_fish)
        is_vegan = is_veg and not (contains_dairy or contains_egg)
        
        df.at[i, 'is_vegetarian'] = is_veg
        df.at[i, 'is_vegan'] = is_vegan
        if not is_veg:
            df.at[i, 'diet_type'] = 'Non Vegetarian'
        elif is_vegan:
            df.at[i, 'diet_type'] = 'Vegan'
        else:
            df.at[i, 'diet_type'] = 'Vegetarian'
            
        # Rebuild allergens list
        allergens = []
        if contains_dairy: allergens.append("Dairy")
        if contains_egg: allergens.append("Eggs")
        if contains_fish: allergens.append("Fish/Seafood")
        if contains_gluten: allergens.append("Gluten")
        if contains_nuts: allergens.append("Nuts")
        if contains_soy: allergens.append("Soy")
        
        df.at[i, 'allergens'] = ", ".join(allergens) if allergens else "None"
        
        # 4. Meal Type Fixes
        if 'beverage' in cat or 'drink' in name or 'tea' in name or 'coffee' in name or 'water' in name or 'juice' in name:
            if 'pre workout' in name or 'coffee' in name or 'espresso' in name:
                df.at[i, 'meal_type'] = 'Pre Workout'
            elif 'protein shake' in name:
                df.at[i, 'meal_type'] = 'Post Workout'
            else:
                df.at[i, 'meal_type'] = 'Beverage'
                
        # 5. Goal Mapping
        if cal > 500 and p > 20:
            df.at[i, 'goal'] = 'Muscle Gain'
        elif cal < 300 and f < 10:
            df.at[i, 'goal'] = 'Weight Loss'
        else:
            df.at[i, 'goal'] = 'Maintenance'
            
        # 6. Rewrite Description
        df.at[i, 'description'] = rewrite_description(df.iloc[i])
        
    df.to_csv(OUTPUT_CSV, index=False)
    print(f"SUCCESS: V3 Dataset generated with {len(df)} fully audited rows.")
    print(f"Saved to {OUTPUT_CSV}")

if __name__ == '__main__':
    run_audit()
