"""
Food Database API Endpoint
Serves real food data from nutrition.csv
"""

from fastapi import APIRouter, HTTPException
from typing import Dict, List
import pandas as pd
import os
import logging

logger = logging.getLogger(__name__)
router = APIRouter(tags=["food-database"])

# Load food database
FOOD_DATABASE = None

def load_food_database():
    """Load food database from CSV"""
    global FOOD_DATABASE
    
    if FOOD_DATABASE is not None:
        return FOOD_DATABASE
    
    try:
        base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        csv_path = os.path.join(base_dir, 'data', 'nutrition_production_final_v4.csv')
        
        if not os.path.exists(csv_path):
            logger.error(f"Food database not found at {csv_path}")
            return None
        
        df = pd.read_csv(csv_path)
        
        # Categorize by meal type
        FOOD_DATABASE = {
            'breakfast': [],
            'lunch': [],
            'dinner': [],
            'snack': []
        }
        
        for _, row in df.iterrows():
            meal_type = str(row.get('meal_type', '')).lower()
            
            # Map meal types
            if 'breakfast' in meal_type:
                category = 'breakfast'
            elif 'lunch' in meal_type:
                category = 'lunch'
            elif 'dinner' in meal_type:
                category = 'dinner'
            elif 'snack' in meal_type:
                category = 'snack'
            else:
                continue
            
            # Determine if vegetarian
            is_veg = bool(row.get('is_vegetarian', False)) or bool(row.get('is_vegan', False))
            
            # Get swap group
            swap_group = str(row.get('subcategory', ''))
            
            # Get goal
            goal = str(row.get('goal', 'Maintenance'))
            
            # Get allergens
            allergens = str(row.get('allergens', ''))
            
            food_item = {
                'name': str(row.get('food_name', 'Unknown')),
                'calories': float(row.get('calories_kcal', 0)),
                'protein': float(row.get('protein_g', 0)),
                'carbs': float(row.get('carbohydrates_g', 0)),
                'fat': float(row.get('fat_g', 0)),
                'unit': 'g',
                'baseQty': float(row.get('serving_size_g', 100)),
                'category': categorize_food(str(row.get('food_name', ''))),
                'isVeg': is_veg,
                'swapGroup': swap_group,
                'goal': goal,
                'allergens': allergens if allergens and allergens.lower() != 'nan' else 'No Known Allergens'
            }
            
            FOOD_DATABASE[category].append(food_item)
        
        logger.info(f"Loaded food database: {sum(len(v) for v in FOOD_DATABASE.values())} items")
        return FOOD_DATABASE
        
    except Exception as e:
        logger.error(f"Error loading food database: {e}")
        return None

def categorize_food(name: str) -> str:
    """Categorize food based on name"""
    name_lower = name.lower()
    
    if any(x in name_lower for x in ['roti', 'rice', 'bread', 'daliya', 'oats', 'poha', 'upma', 'idli', 'dosa', 'paratha', 'khichdi', 'sandwich', 'toast', 'cereal', 'flakes']):
        return 'grains'
    elif any(x in name_lower for x in ['chicken', 'fish', 'egg', 'paneer', 'dal', 'chole', 'rajma', 'keema', 'curry', 'bhurji', 'curd', 'yogurt', 'cheese', 'milk', 'sprouts', 'chana']):
        return 'protein'
    elif any(x in name_lower for x in ['veg', 'vegetable', 'palak', 'broccoli', 'salad', 'cucumber', 'tomato', 'onion', 'mixed']):
        return 'vegetables'
    elif any(x in name_lower for x in ['fruit', 'apple', 'banana', 'mango', 'orange', 'papaya', 'berries', 'chaat']):
        return 'fruits'
    elif any(x in name_lower for x in ['oil', 'ghee', 'butter', 'peanut', 'almond', 'nuts', 'seeds']):
        return 'fats'
    elif any(x in name_lower for x in ['milk', 'curd', 'yogurt', 'cheese', 'lassi', 'shake']):
        return 'dairy'
    else:
        return 'other'

@router.get("/food-database")
async def get_food_database():
    """
    Get the complete food database categorized by meal type
    
    Returns:
    {
        "success": true,
        "data": {
            "breakfast": [...],
            "lunch": [...],
            "dinner": [...],
            "snack": [...]
        }
    }
    """
    try:
        food_db = load_food_database()
        
        if food_db is None:
            raise HTTPException(status_code=500, detail="Failed to load food database")
        
        return {
            "success": True,
            "data": food_db,
            "total_items": sum(len(v) for v in food_db.values())
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error serving food database: {e}")
        raise HTTPException(status_code=500, detail=str(e))
