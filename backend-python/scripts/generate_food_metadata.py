import os
import sys
import json
import pandas as pd
import logging

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

RECIPE_KEYWORDS = [
    "sandwich", "curry", "biryani", "chowmein", "lasagne", "yakhni", "soup", "salad", 
    "meal", "bhaji", "khichdi", "wrap", "smoothie", "dosa", "idli", "upma", "poha", 
    "pongal", "dhokla", "omelette", "bhurji", "chilla", "tikka", "masala", "stir fry",
    "korma", "bhuna", "roast", "gravy", "rice bowl", "thali", "paratha", "roti", "naan",
    "pancake", "waffle", "pasta", "pizza", "burger", "taco", "burrito", "kebab", "kofta",
    "dal", "sambar", "rasam", "chutney", "pickle", "tea", "coffee", "juice", "shake"
]

def is_recipe(food_name: str, category: str) -> bool:
    name_lower = food_name.lower()
    
    # Categories that are inherently recipes
    if category in ["Traditional Meal", "Breakfast", "Salad", "Soup", "Snack", "Healthy Beverage"]:
        return True
        
    for kw in RECIPE_KEYWORDS:
        if kw in name_lower:
            return True
            
    return False

def generate_food_metadata(csv_path: str, output_dir: str):
    if not os.path.exists(csv_path):
        logging.error(f"Dataset not found at {csv_path}")
        return
        
    df = pd.read_csv(csv_path)
    
    ingredients = {}
    recipes = {}
    
    for idx, row in df.iterrows():
        food_id = row['food_id']
        food_name = row['food_name']
        category = row['category']
        
        is_rec = is_recipe(food_name, category)
        
        # Base metadata
        metadata = {
            "food_id": food_id,
            "food_name": food_name,
            "category": category,
            "subcategory": row.get('subcategory', ''),
            "meal_type": row.get('meal_type', ''),
            "protein_density": round(row['protein_g'] * 4 / row['calories_kcal'], 2) if row['calories_kcal'] > 0 else 0,
            "calories_per_serving": row['calories_kcal'],
            "protein_per_serving": row['protein_g'],
            "carbs_per_serving": row['carbohydrates_g'],
            "fat_per_serving": row['fat_g'],
            "cuisine": row.get('region', 'All India'),
            "is_vegan": row.get('is_vegan', False),
            "is_vegetarian": row.get('is_vegetarian', False),
            "complexity_score": 5, # Default, can be edited manually
            "prep_time_minutes": 15, # Default
            "cook_time_minutes": 20, # Default
        }
        
        if is_rec:
            # It's a recipe
            metadata["type"] = "RECIPE"
            metadata["versions"] = {
                "v1_traditional": {
                    "ingredients": [], # To be populated by curators
                    "instructions": [],
                    "macros_multiplier": 1.0
                }
            }
            recipes[food_id] = metadata
        else:
            # It's a raw ingredient
            metadata["type"] = "INGREDIENT"
            ingredients[food_id] = metadata
            
    # Save the splits
    os.makedirs(output_dir, exist_ok=True)
    
    ing_path = os.path.join(output_dir, "ingredient_database.json")
    rec_path = os.path.join(output_dir, "recipe_database.json")
    
    with open(ing_path, 'w', encoding='utf-8') as f:
        json.dump(ingredients, f, indent=4)
        
    with open(rec_path, 'w', encoding='utf-8') as f:
        json.dump(recipes, f, indent=4)
        
    logging.info(f"Successfully generated metadata!")
    logging.info(f"Total Ingredients: {len(ingredients)}")
    logging.info(f"Total Recipes: {len(recipes)}")

if __name__ == "__main__":
    current_dir = os.path.dirname(os.path.abspath(__file__))
    csv_path = os.path.join(current_dir, "..", "data", "nutrition_production_final_v4.csv")
    output_dir = os.path.join(current_dir, "..", "data")
    
    generate_food_metadata(csv_path, output_dir)
