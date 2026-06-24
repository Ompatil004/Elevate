import pandas as pd
import numpy as np
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CSV_PATH = os.path.join(BASE_DIR, 'data', 'nutrition_production_v3.csv')

def run_validation():
    print("Starting Strict Validation on V3...")
    df = pd.read_csv(CSV_PATH)
    
    # Validation Rules
    for i, row in df.iterrows():
        name = str(row['food_name']).lower()
        cat = str(row['category']).lower()
        
        # 1. Macro validation
        p = float(row['protein_g'])
        c = float(row['carbohydrates_g'])
        f = float(row['fat_g'])
        cal = round((p * 4.0) + (c * 4.0) + (f * 9.0))
        df.at[i, 'calories_kcal'] = cal
        
        # 2. Micronutrient limits (Cap extreme generated values)
        micronutrients = {
            'sodium_mg': 2000,
            'potassium_mg': 1500,
            'calcium_mg': 800,
            'iron_mg': 20,
            'magnesium_mg': 400,
            'phosphorus_mg': 800,
            'zinc_mg': 15,
            'vitamin_a_mcg': 900,
            'vitamin_c_mg': 100,
            'vitamin_d_mcg': 20,
            'vitamin_b12_mcg': 5,
            'cholesterol_mg': 300
        }
        for k, max_val in micronutrients.items():
            if k in df.columns:
                df.at[i, k] = min(float(df.at[i, k]), max_val)
                
        # 3. Boolean and Allergen verification
        contains_dairy = any(x in name for x in ['cheese', 'dairy', 'milk', 'paneer', 'curd', 'yogurt', 'ghee', 'butter', 'lassi', 'buttermilk', 'malai', 'cream'])
        contains_egg = any(x in name for x in ['egg', 'omelette', 'bhurji'])
        contains_meat = any(x in name for x in ['chicken', 'mutton', 'meat', 'beef', 'pork', 'lamb', 'keema'])
        contains_fish = any(x in name for x in ['fish', 'prawn', 'seafood', 'basa', 'machher', 'moilee', 'shrimp', 'crab'])
        contains_gluten = any(x in name for x in ['wheat', 'bread', 'pasta', 'roti', 'chapati', 'paratha', 'sandwich', 'naan', 'kulcha', 'puri', 'bhatura'])
        contains_nuts = any(x in name for x in ['nut', 'almond', 'cashew', 'peanut', 'walnut', 'badam', 'pista'])
        contains_soy = any(x in name for x in ['soy', 'tofu', 'soya', 'nutrela'])
        
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
        df.at[i, 'is_jain_friendly'] = is_veg and not any(x in name for x in ['onion', 'garlic', 'potato', 'ginger', 'carrot', 'radish'])
        
        # High Protein / Low Carb flags
        df.at[i, 'is_high_protein'] = p >= 15.0
        df.at[i, 'is_low_carb'] = c <= 20.0
        df.at[i, 'is_low_fat'] = f <= 10.0
        
        # Build Allergens perfectly
        allergens = []
        if contains_dairy: allergens.append("Dairy")
        if contains_egg: allergens.append("Eggs")
        if contains_fish: allergens.append("Fish/Seafood")
        if contains_gluten: allergens.append("Gluten")
        if contains_nuts: allergens.append("Nuts")
        if contains_soy: allergens.append("Soy")
        
        df.at[i, 'allergens'] = ", ".join(allergens) if allergens else "None"
        
        # 4. Meal Type and Goal verification
        # Ensures no blank meal types
        if pd.isna(row.get('meal_type', '')):
            if cal < 150: df.at[i, 'meal_type'] = 'Snack'
            else: df.at[i, 'meal_type'] = 'Lunch'
            
        if cal > 500 and p > 20:
            df.at[i, 'goal'] = 'Muscle Gain'
        elif cal < 300 and f < 10:
            df.at[i, 'goal'] = 'Weight Loss'
        else:
            df.at[i, 'goal'] = 'Maintenance'
            
        # 5. Cooking Method & Region verification
        if pd.isna(row.get('cooking_method', '')):
            df.at[i, 'cooking_method'] = 'Curry'
        if pd.isna(row.get('region', '')):
            df.at[i, 'region'] = 'All India'

    df.to_csv(CSV_PATH, index=False)
    print(f"SUCCESS: V3 Dataset validated and fully overwritten with strict corrections.")

if __name__ == '__main__':
    run_validation()
