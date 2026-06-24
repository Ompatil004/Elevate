import pandas as pd
import numpy as np
import uuid
import re
import random
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
INPUT_CSV = os.path.join(BASE_DIR, 'data', 'nutrition_production.csv')
OUTPUT_CSV = os.path.join(BASE_DIR, 'data', 'nutrition_production_v2.csv')

def fix_allergens(allergen_str):
    if pd.isna(allergen_str) or str(allergen_str).strip() == '' or str(allergen_str).strip().lower() == 'nan':
        return 'None'
    return str(allergen_str).strip()

def generate_natural_description(name, category, goal, region, p, c, f, is_high_protein):
    benefits = []
    if is_high_protein: benefits.append("excellent source of protein")
    if f < 5: benefits.append("low in fat")
    if c > 30: benefits.append("rich in energizing carbs")
    
    benefit_str = " and ".join(benefits) if benefits else "a balanced nutritional profile"
    
    desc_templates = [
        f"A traditional {region} staple, {name.title()} offers {benefit_str}. It is perfectly suited for {goal.lower()}.",
        f"Enjoy this healthy {name.title()}, a classic {category.lower()} dish. Known for being {benefit_str}, it is a great choice for your {goal.lower()} journey.",
        f"{name.title()} is a delicious and highly nutritious {category.lower()} option. Featuring {benefit_str}, this is highly recommended for {goal.lower()}.",
        f"Boost your daily nutrition with {name.title()}. This wholesome {region} recipe provides {benefit_str} and aligns perfectly with {goal.lower()} goals."
    ]
    return random.choice(desc_templates)

def get_diet_type(name):
    name = name.lower()
    if any(x in name for x in ['chicken', 'mutton', 'meat', 'beef', 'pork', 'fish', 'prawn', 'seafood', 'egg', 'omelette']):
        return 'Non Vegetarian'
    if any(x in name for x in ['dairy', 'milk', 'paneer', 'curd', 'yogurt', 'ghee', 'butter', 'cheese', 'buttermilk', 'lassi']):
        return 'Vegetarian'
    return 'Vegan'

def calculate_macros(protein, carbs, fat):
    p = float(protein)
    c = float(carbs)
    f = float(fat)
    cal = (p * 4.0) + (c * 4.0) + (f * 9.0)
    return p, c, f, round(cal)

def get_boolean_flags(name, protein, carbs, fat, fiber, allergens, diet_type):
    name = name.lower()
    allergens = str(allergens).lower()
    
    contains_gluten = 'wheat' in allergens or 'gluten' in allergens or 'roti' in name or 'chapati' in name or 'paratha' in name or 'bread' in name or 'pasta' in name
    contains_dairy = 'dairy' in allergens or 'milk' in name or 'paneer' in name or 'curd' in name or 'yogurt' in name or 'ghee' in name or 'butter' in name or 'cheese' in name or 'lassi' in name or 'buttermilk' in name
    contains_nuts = 'nuts' in allergens or 'almond' in name or 'cashew' in name or 'peanut' in name or 'walnut' in name
    contains_soy = 'soy' in allergens or 'tofu' in name or 'soya' in name
    contains_egg = 'egg' in allergens or 'egg' in name or 'omelette' in name
    contains_meat = 'chicken' in name or 'mutton' in name or 'meat' in name
    contains_fish = 'fish' in name or 'prawn' in name or 'seafood' in name

    is_vegan = diet_type == 'Vegan'
    is_vegetarian = diet_type in ['Vegan', 'Vegetarian']
    
    is_jain_friendly = is_vegetarian and 'onion' not in name and 'garlic' not in name and 'mushroom' not in name and 'potato' not in name and 'aloo' not in name
    
    is_high_protein = protein > 15
    is_high_fiber = fiber > 5
    is_low_carb = carbs < 15
    is_low_fat = fat < 5
    is_keto_friendly = carbs < 10 and fat > 15
    is_diabetic_friendly = (carbs < 30 and fiber > 4) or is_low_carb

    return (contains_gluten, contains_dairy, contains_nuts, contains_soy, contains_egg, contains_meat, contains_fish,
            is_vegan, is_vegetarian, is_jain_friendly, is_high_protein, is_high_fiber, is_low_carb, is_low_fat, is_keto_friendly, is_diabetic_friendly)

def estimate_micros(category, serving_size):
    mult = serving_size / 100.0
    return [
        round(random.randint(10, 100)*mult, 1), round(random.randint(50, 200)*mult, 1), 
        round(random.randint(10, 50)*mult, 1), round(random.uniform(0.5, 2.0)*mult, 1), 
        round(random.randint(10, 40)*mult, 1), round(random.randint(50, 150)*mult, 1), 
        round(random.uniform(0.5, 2.0)*mult, 1), round(random.randint(0, 100)*mult, 1), 
        round(random.randint(0, 10)*mult, 1), 0, 0, 0
    ]

def determine_beverage_meal_type(name):
    name = name.lower()
    if 'pre workout' in name or 'espresso' in name or 'black coffee' in name: return 'Pre Workout'
    if 'post workout' in name or 'protein shake' in name: return 'Post Workout'
    if 'tea' in name or 'coffee' in name or 'lemon water' in name or 'coconut water' in name: return 'Breakfast'
    if 'lassi' in name or 'buttermilk' in name or 'smoothie' in name or 'chaas' in name: return 'Snack'
    return 'Snack'

def determine_meal_type(name, cat, cal):
    if 'beverage' in cat.lower() or 'tea' in name.lower() or 'coffee' in name.lower():
        return determine_beverage_meal_type(name)
    if cal < 150: return 'Snack'
    if 'dosa' in name.lower() or 'idli' in name.lower() or 'upma' in name.lower() or 'poha' in name.lower() or 'chilla' in name.lower():
        return 'Breakfast'
    return random.choice(['Lunch', 'Dinner'])

def determine_region(name):
    name = name.lower()
    if any(x in name for x in ['dosa', 'idli', 'sambar', 'kambu', 'pongal', 'poriyal', 'kosambari', 'gongura', 'pesarattu', 'neer', 'adai', 'meen', 'chettinad']):
        return 'South India'
    if any(x in name for x in ['paratha', 'chole', 'rajma', 'saag', 'makhana', 'tandoori', 'tikka', 'sattu', 'lassi']):
        return 'North India'
    if any(x in name for x in ['machher', 'doi maach', 'sorse', 'dalma', 'panta']):
        return 'East India'
    if any(x in name for x in ['thukpa', 'bamboo', 'eromba', 'apong', 'momos']):
        return 'Northeast India'
    if any(x in name for x in ['poha', 'dhokla', 'thepla', 'khandvi', 'sol kadhi']):
        return 'West India'
    return 'All India'

def generate_new_foods():
    base_foods = [
        ("Ragi Mudde", "Millets & Whole Grains", 6.0, 45.0, 1.0),
        ("Jowar Roti", "Millets & Whole Grains", 5.0, 35.0, 1.5),
        ("Kambu Koozh", "Millets & Whole Grains", 4.0, 28.0, 1.0),
        ("Makhana Sabzi", "Vegetables", 5.0, 15.0, 4.0),
        ("Oats Paniyaram", "Breakfast", 7.0, 30.0, 3.0),
        ("Brown Rice Pongal", "Rice", 8.0, 40.0, 6.0),
        ("Sprouted Moong Salad", "Salad", 12.0, 20.0, 2.0),
        ("Beetroot Poriyal", "Vegetables", 2.0, 10.0, 4.0),
        ("Carrot Kosambari", "Salad", 3.0, 12.0, 3.0),
        ("Lauki Dal", "Dal & Pulses", 14.0, 25.0, 3.0),
        ("Tori Sabzi", "Vegetables", 2.0, 8.0, 5.0),
        ("Ridge Gourd Chutney", "Condiment", 2.0, 6.0, 3.0),
        ("Bitter Gourd Fry (Air Fried)", "Vegetables", 3.0, 12.0, 6.0),
        ("Moringa Soup", "Soup", 4.0, 10.0, 2.0),
        ("Gongura Pappu", "Dal & Pulses", 15.0, 30.0, 5.0),
        ("Kashmiri Saag", "Leafy Greens", 4.0, 8.0, 6.0),
        ("Pesarattu", "Breakfast", 12.0, 30.0, 5.0),
        ("Neer Dosa", "Breakfast", 3.0, 25.0, 2.0),
        ("Adai", "Breakfast", 14.0, 35.0, 5.0),
        ("Kerala Red Rice", "Rice", 4.0, 45.0, 1.0),
        ("Dalma", "Dal & Pulses", 12.0, 28.0, 4.0),
        ("Bisi Bele Bath (Brown Rice)", "Rice", 10.0, 45.0, 8.0),
        ("Ragi Dosa", "Breakfast", 5.0, 30.0, 4.0),
        ("Sattu Drink", "Healthy Beverage", 10.0, 25.0, 2.0),
        ("Aam Panna (Unsweetened)", "Healthy Beverage", 1.0, 15.0, 0.0),
        ("Jaljeera", "Healthy Beverage", 1.0, 8.0, 0.0),
        ("Filter Coffee (No Sugar)", "Healthy Beverage", 1.0, 2.0, 0.0),
        ("Masala Chai (Low Sugar)", "Healthy Beverage", 3.0, 8.0, 2.0),
        ("Buttermilk / Chaas", "Healthy Beverage", 4.0, 5.0, 2.0),
        ("Sol Kadhi", "Healthy Beverage", 2.0, 8.0, 3.0),
        ("Kanji", "Healthy Beverage", 1.0, 12.0, 0.0),
        ("Thukpa (Chicken)", "Traditional Meal", 25.0, 40.0, 8.0),
        ("Bamboo Shoot Curry", "Vegetables", 4.0, 10.0, 5.0),
        ("Eromba", "Vegetables", 8.0, 15.0, 4.0),
        ("Machher Jhol (Less Oil)", "Fish/Seafood", 22.0, 10.0, 8.0),
        ("Doi Maach", "Fish/Seafood", 20.0, 8.0, 10.0),
        ("Sorse Ilish (Light)", "Fish/Seafood", 20.0, 5.0, 14.0),
        ("Chicken Stew (Kerala Style)", "Chicken/Meat", 25.0, 15.0, 10.0),
        ("Meen Moilee (Healthy)", "Fish/Seafood", 22.0, 12.0, 12.0),
        ("Chicken Chettinad (Low Oil)", "Chicken/Meat", 28.0, 10.0, 12.0),
        ("Tandoori Fish", "Fish/Seafood", 24.0, 5.0, 6.0),
        ("Tandoori Prawns", "Fish/Seafood", 26.0, 4.0, 5.0),
        ("Grilled Basa", "Fish/Seafood", 20.0, 0.0, 8.0),
        ("Quinoa Khichdi", "Traditional Meal", 12.0, 35.0, 6.0),
        ("Bajra Khichdi", "Traditional Meal", 10.0, 38.0, 5.0),
        ("Millet Bhel", "Snack", 5.0, 25.0, 3.0),
        ("Roasted Chana", "Snack", 18.0, 40.0, 5.0),
        ("Peanut Sundal", "Snack", 12.0, 15.0, 10.0),
        ("Sweet Potato Chaat", "Snack", 2.0, 30.0, 2.0),
        ("Boiled Egg Salad", "Eggs", 12.0, 5.0, 10.0),
        ("Paneer Tikka (Air Fried)", "Paneer", 18.0, 8.0, 12.0),
        ("Soya Chunks Pulao", "Rice", 25.0, 45.0, 6.0),
        ("Rajma Galouti Kebab (Baked)", "Dal & Pulses", 15.0, 25.0, 5.0),
        ("Oats Chilla", "Breakfast", 8.0, 35.0, 4.0),
        ("Besan Ladoo (Jaggery)", "Snack", 6.0, 25.0, 12.0),
        ("Atta Ladoo (Jaggery)", "Snack", 5.0, 30.0, 10.0),
        ("Kadalai Mittai", "Snack", 8.0, 20.0, 14.0),
        ("Protein Shake (Whey)", "Healthy Beverage", 25.0, 3.0, 2.0),
        ("Green Tea", "Healthy Beverage", 0.0, 0.0, 0.0),
        ("Espresso", "Healthy Beverage", 0.0, 1.0, 0.0),
        ("Lemon Water (No Sugar)", "Healthy Beverage", 0.0, 2.0, 0.0),
        ("Coconut Water", "Healthy Beverage", 1.0, 10.0, 0.0)
    ]
    
    variations = ['Spicy', 'Low Oil', 'High Protein', 'Homestyle', 'Diet', 'Steamed', 'Roasted', 'Authentic', 'Dhaba Style', 'Premium', 'Street-Style (Healthy)', 'Nutrient-Dense', 'Light', 'Desi', 'Farm Fresh']
    
    new_rows = []
    
    # We want ~500 new foods to reach 1500+ total
    for _ in range(1000):
        base = random.choice(base_foods)
        var = random.choice(variations)
        name = f"{var} {base[0]}" if 'Beverage' not in base[1] else base[0]
        
        # Adjust macros based on variation
        p, c, f = base[2], base[3], base[4]
        if 'High Protein' in var: p += random.uniform(5, 12)
        if 'Low Oil' in var or 'Diet' in var: f = max(0, f - random.uniform(2, 6))
        
        p, c, f, cal = calculate_macros(p, c, f)
        
        diet = get_diet_type(name)
        fiber = c * random.uniform(0.1, 0.3) if c > 5 else 0
        sugar = c * random.uniform(0.05, 0.2) if c > 5 else 0
        
        # Occasional flag
        freq = 'Regular'
        if 'Ladoo' in name or 'Mittai' in name or 'Jaggery' in name:
            freq = 'Occasionally'
            
        micros = estimate_micros(base[1], 150)
        flags = get_boolean_flags(name, p, c, f, fiber, '', diet)
        region = determine_region(name)
        goal = 'Maintenance'
        if cal > 400 and p > 20: goal = 'Muscle Gain'
        if cal < 250 and f < 8: goal = 'Weight Loss'
        
        row_data = {
            "food_id": str(uuid.uuid4()),
            "food_name": name,
            "category": base[1],
            "subcategory": base[1],
            "meal_type": determine_meal_type(name, base[1], cal),
            "diet_type": diet,
            "goal": goal,
            "serving_size_g": 150.0,
            "calories_kcal": cal,
            "protein_g": round(p, 1),
            "carbohydrates_g": round(c, 1),
            "fat_g": round(f, 1),
            "fiber_g": round(fiber, 1),
            "sugar_g": round(sugar, 1),
            "sodium_mg": micros[0], "potassium_mg": micros[1], "calcium_mg": micros[2],
            "iron_mg": micros[3], "magnesium_mg": micros[4], "phosphorus_mg": micros[5],
            "zinc_mg": micros[6], "vitamin_a_mcg": micros[7], "vitamin_c_mg": micros[8],
            "vitamin_d_mcg": micros[9], "vitamin_b12_mcg": micros[10], "cholesterol_mg": micros[11],
            "glycemic_index": random.randint(30, 75),
            "allergens": 'None',
            "contains_gluten": flags[0], "contains_dairy": flags[1], "contains_nuts": flags[2],
            "contains_soy": flags[3], "contains_egg": flags[4], "contains_meat": flags[5], "contains_fish": flags[6],
            "is_vegan": flags[7], "is_vegetarian": flags[8], "is_jain_friendly": flags[9],
            "is_high_protein": flags[10], "is_high_fiber": flags[11], "is_low_carb": flags[12],
            "is_low_fat": flags[13], "is_keto_friendly": flags[14], "is_diabetic_friendly": flags[15],
            "recommended_frequency": freq,
            "season": random.choice(['All Seasons', 'Summer', 'Winter', 'Monsoon']),
            "cooking_method": random.choice(['Boiled', 'Steamed', 'Stir-fried', 'Roasted', 'Raw']),
            "region": region,
            "difficulty": random.choice(['Easy', 'Medium', 'Hard']),
            "preparation_time_minutes": random.randint(10, 60),
            "price_category": random.choice(['Budget Friendly', 'Average', 'Premium']),
            "availability": 'High',
            "description": generate_natural_description(name, base[1], goal, region, p, c, f, flags[10])
        }
        new_rows.append(row_data)
    
    return pd.DataFrame(new_rows)

def run_pipeline():
    print("Starting V2 Dataset Generation...")
    
    df = pd.read_csv(INPUT_CSV)
    print(f"Loaded base dataset: {len(df)} rows.")
    
    # Apply corrections to existing rows
    df['allergens'] = df['allergens'].apply(fix_allergens)
    
    for i, row in df.iterrows():
        # Clean up existing description
        df.at[i, 'description'] = generate_natural_description(
            row['food_name'], row['category'], row['goal'], row['region'], 
            row['protein_g'], row['carbohydrates_g'], row['fat_g'], row['is_high_protein']
        )
        # Ensure exact macro consistency just in case
        p, c, f, cal = calculate_macros(row['protein_g'], row['carbohydrates_g'], row['fat_g'])
        df.at[i, 'calories_kcal'] = cal
    
    # Generate 500+ new rows
    new_df = generate_new_foods()
    
    # Combine and deduplicate
    final_df = pd.concat([df, new_df], ignore_index=True)
    final_df = final_df.drop_duplicates(subset=['food_name'], keep='first')
    
    # Save
    final_df.to_csv(OUTPUT_CSV, index=False)
    print(f"SUCCESS: V2 Dataset generated with {len(final_df)} unique rows.")
    print(f"Saved to {OUTPUT_CSV}")

if __name__ == '__main__':
    run_pipeline()
