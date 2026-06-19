"""
Deterministic 7-Day Meal Engine — Dataset-Driven with Production-Level Food Classification

Loads ALL meals directly from data/nutrition_processed.csv.
Selects meals using Mifflin-St Jeor TDEE, macro ratios, dietary
preference filtering, allergen exclusion, and Swap_Group matching.

Features:
- Multi-layer food classification (main_meal, side_dish, ingredient)
- Regex-based filtering with whitelist protection
- Nutrition-based validation
- Indian meal combination suggestions

Every calorie/macro value displayed is the EXACT value from the
dataset — no random multipliers, no dummy data.
"""

import pandas as pd
import numpy as np
from datetime import datetime, timezone
from typing import Dict, List, Optional, Tuple
from enum import Enum
import os
import random
import hashlib
from collections import Counter
import json
import re

from .daily_planner import generate_day_plan


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


class FoodCategory(Enum):
    """Classification categories for food items."""
    MAIN_MEAL = "main_meal"
    SIDE_DISH = "side_dish"
    INGREDIENT = "ingredient"
    CONDIMENT = "condiment"
    BEVERAGE = "beverage"
    INVALID = "invalid"


class FoodClassifier:
    """
    Production-level food classifier for Indian cuisine dataset.
    Classifies food items and filters out non-meal entries.
    """
    
    # ==================================================================
    # WHITELIST: Known valid Indian dishes that should NEVER be removed
    # ==================================================================
    INDIAN_DISH_WHITELIST = {
        # Dosas and South Indian
        'masala dosa', 'plain dosa', 'rava dosa', 'uttapam', 'idli', 'vada', 'sambar',
        'rasam', 'pongal', 'upma', 'poha', 'appe', 'paniyaram',
        
        # North Indian Curries
        'butter chicken', 'paneer butter masala', 'dal makhani', 'dal tadka',
        'chole', 'chole bhature', 'rajma', 'kadhi', 'palak paneer',
        'shahi paneer', 'matar paneer', 'aloo gobi', 'aloo matar',
        'bhindi masala', 'baingan bharta', 'mixed vegetable', 'navratan korma',
        'vegetable korma', 'malai kofta', 'dum aloo', 'aloo jeera',
        
        # Breads
        'roti', 'chapati', 'paratha', 'naan', 'kulcha', 'bhatura',
        'poori', 'thepla', 'dhokla', 'handvo',
        
        # Rice dishes
        'biryani', 'pulao', 'fried rice', 'lemon rice', 'tamarind rice',
        'curd rice', 'sambar rice', 'bisibele bath', 'tahari',
        
        # Street food & Snacks
        'samosa', 'kachori', 'pakora', 'bhajiya', 'vada pav', 'pav bhaji',
        'chaat', 'dahi bhalla', 'aloo tikki', 'gol gappa', 'panipuri',
        
        # Sweets & Desserts (as snacks)
        'kheer', 'payasam', 'halwa', 'laddu', 'barfi', 'gulab jamun',
        'rasmalai', 'jalebi', 'mysore pak', 'soan papdi',
        
        # Soups & Starters
        'tomato soup', 'sweet corn soup', 'manchow soup', 'hot and sour soup',
        'dal shorba', 'mulligatawny soup', 'tandoori chicken', 'tikka',
        
        # Breakfast items
        'poha', 'upma', 'dalia', 'sabudana khichdi', 'sabudana vada',
        'misal pav', 'akuri', 'anda bhurji',
        
        # Regional
        'lassi', 'chaas', 'buttermilk', 'thali', 'meal', 'thali meal',
    }
    
    # ==================================================================
    # PATTERNS: Regex patterns for classification
    # ==================================================================
    
    # Raw ingredients - standalone items not suitable as meals
    INGREDIENT_PATTERNS = [
        # Pure spices and masalas (standalone only)
        r'^garam masala\b', r'^chat masala\b', r'^kashmiri masala\b',
        r'^rasam\b.*\b(powder|masala)\b', r'^sambar\b.*\b(powder|masala)\b',
        r'^bengal.*spice', r'^panch phoran\b',
        r'^turmeric\b', r'^cumin\b', r'^coriander powder\b',
        r'^chili powder\b', r'^red chili\b', r'^black pepper\b',
        r'^salt\b', r'^mustard seeds\b', r'^fenugreek\b',
        r'^cardamom\b', r'^cinnamon\b', r'^cloves\b', r'^bay leaves\b',
        r'^asafoetida\b', r'^hing\b', r'^carom seeds\b', r'^ajwain\b',
        r'^fennel seeds\b', r'^dry ginger\b', r'^mace\b', r'^star anise\b',
        r'^vanilla extract\b', r'^baking (powder|soda)\b',
        
        # Pure cooking mediums
        r'^ghee\b', r'^oil\b', r'^butter\b', r'^vinegar\b',
        r'^cooking oil\b', r'^vanilla essence\b', r'^food colou?r\b',
        
        # Standalone sauces (not dishes WITH sauce)
        r'^tomato (sauce|ketchup|puree|paste)\b',
        r'^tartare sauce\b', r'^barbeque sauce\b', r'^bread sauce\b',
        r'^bbq sauce\b', r'^green chilli sauce\b', r'^red chilli sauce\b',
        r'^soy sauce\b', r'^hot sauce\b', r'^sweet chilli\b',
        r'^hot cherry sauce\b', r'^cherry sauce\b',
        
        # Tadkas/Baghars (cooking tempering, not meals)
        r'baghar\b', r'tadka\b', r'jeera.*tadka', r'mustard.*tadka',
        r'cumin seeds.*baghar', r'onion tomato.*baghar',
        
        # Pure condiments (not raita or accompaniments)
        r'achaar\b', r'pickle\b', r'murabba\b', r'achar\b',
        r'squash\b', r'concentrate\b', r'^syrup\b',
    ]
    
    # Side dishes - valid accompaniments but not main meals alone
    SIDE_DISH_PATTERNS = [
        r'raita\b', r'chutney\b', r'papad\b', r'salad\b',
        r'pickle\b', r'achaar\b', r'chips\b', r'fries\b',
        r'crisps\b', r'dip\b', r'spread\b',
    ]
    
    # Main meal indicators
    MAIN_MEAL_PATTERNS = [
        r'\b(curry|sabzi|sabji|bhaji|bharta|fry|roast|grill)\b',
        r'\b(dal|sambar|rassam|kadhi|sambar)\b',
        r'\b(biryani|pulao|fried rice|rice)\b',
        r'\b(roti|chapati|paratha|naan|kulcha|bhatura|poori)\b',
        r'\b(dosa|idli|vada|uttapam|upma|poha)\b',
        r'\b(sandwich|burger|pizza|pasta|noodles)\b',
        r'\b(soup|stew|broth|shorba)\b',
        r'\b(egg|anda)\b', r'\b(chicken|mutton|fish|prawn|paneer)\b',
        r'\b(thali|meal|combo|platter)\b',
        r'\b(ladoo|halwa|kheer|payasam)\b',
    ]
    
    # Beverage indicators — items matching these should NEVER be a meal slot
    BEVERAGE_PATTERNS = [
        r'\bdrink\b', r'\bjuice\b', r'\bcooler\b', r'\blemonade\b',
        r'\bsherbet\b', r'\bsharbat\b', r'\baam panna\b', r'\bfruit punch\b',
        r'\binfused water\b', r'\biced tea\b', r'\bespresso\b',
        r'\bcold coffee\b', r'\bhot cocoa\b', r'\bchaas\b',
        r'\bmilkshake\b', r'\bshake\b', r'\bnog\b',
        r'\bsummer cooler\b', r'\bcoco pine\b', r'\bnimbu pani\b',
        r'\bsquash\b', r'\bcordial\b',
    ]
    
    # ==================================================================
    # NUTRITION THRESHOLDS
    # ==================================================================
    MIN_MEAL_CALORIES = 80  # Below this is likely a condiment
    MAX_SINGLE_ITEM_CALORIES = 700   # Single food item should never exceed 700 cal
                                      # Items above this (Poori=1844, Pulao=1454) are
                                      # full batch recipes, not per-serving values
    
    # Fat-based ingredient detection
    HIGH_FAT_THRESHOLD = 80  # grams
    LOW_PROTEIN_THRESHOLD = 10  # grams
    LOW_CARBS_THRESHOLD = 20  # grams
    
    def __init__(self):
        """Initialize classifier with compiled regex patterns."""
        self.ingredient_regex = re.compile(
            '|'.join(self.INGREDIENT_PATTERNS), 
            re.IGNORECASE
        )
        self.side_dish_regex = re.compile(
            '|'.join(self.SIDE_DISH_PATTERNS), 
            re.IGNORECASE
        )
        self.main_meal_regex = re.compile(
            '|'.join(self.MAIN_MEAL_PATTERNS), 
            re.IGNORECASE
        )
        self.beverage_regex = re.compile(
            '|'.join(self.BEVERAGE_PATTERNS),
            re.IGNORECASE
        )
    
    # ==================================================================
    # CORE CLASSIFICATION METHODS
    # ==================================================================
    
    def classify_food(self, name: str, nutrition: Dict) -> FoodCategory:
        """
        Classify a food item into category based on name and nutrition.
        
        Args:
            name: Food item name
            nutrition: Dict with calories, protein, carbs, fat
            
        Returns:
            FoodCategory enum value
        """
        name_lower = name.lower().strip()
        
        # STEP 0: Check for beverages FIRST — these are never a standalone meal
        if self.beverage_regex.search(name_lower):
            return FoodCategory.BEVERAGE
        
        # STEP 1: Check for raw ingredients FIRST (strict filtering)
        # This catches ingredients like "sambar powder" even though "sambar" is whitelisted
        if self._is_ingredient(name_lower):
            return FoodCategory.INGREDIENT
        
        # STEP 2: Check whitelist (but only for non-ingredients)
        if self._is_whitelisted(name_lower):
            # Whitelisted items need nutrition validation
            return self._validate_by_nutrition(nutrition, FoodCategory.MAIN_MEAL)
        
        # STEP 3: Check for side dishes
        if self._is_side_dish(name_lower):
            return FoodCategory.SIDE_DISH
        
        # STEP 4: Check for main meals by pattern
        if self._is_main_meal_by_pattern(name_lower):
            return self._validate_by_nutrition(nutrition, FoodCategory.MAIN_MEAL)
        
        # STEP 5: Fallback to nutrition-based classification
        return self._classify_by_nutrition_only(nutrition)
    
    def _is_whitelisted(self, name: str) -> bool:
        """Check if food is in the whitelist of known valid dishes."""
        import re
        
        # Exact match
        if name in self.INDIAN_DISH_WHITELIST:
            return True
        
        # Word boundary match - avoid partial matches like "sambar" matching "sambar powder"
        for dish in self.INDIAN_DISH_WHITELIST:
            # Use word boundary regex to ensure complete word match
            pattern = r'\b' + re.escape(dish) + r'\b'
            if re.search(pattern, name, re.IGNORECASE):
                return True
        
        return False
    
    def _is_ingredient(self, name: str) -> bool:
        """Check if item is a raw ingredient (not suitable as meal)."""
        # Must match ingredient pattern AND not be a compound dish
        if self.ingredient_regex.search(name):
            # Check it's not a dish that contains the ingredient
            # e.g., "Chicken with garam masala" is a dish, not an ingredient
            compound_indicators = [
                'with', 'and', 'in', 'ka', 'ke', 'ki', 'wala', 'wali',
                'dish', 'style', 'flavored', 'marinated'
            ]
            if any(ind in name for ind in compound_indicators):
                return False
            return True
        return False
    
    def _is_side_dish(self, name: str) -> bool:
        """Check if item is a side dish/accompaniment."""
        return bool(self.side_dish_regex.search(name))
    
    def _is_main_meal_by_pattern(self, name: str) -> bool:
        """Check if item matches main meal patterns."""
        return bool(self.main_meal_regex.search(name))
    
    def _validate_by_nutrition(self, nutrition: Dict, 
                                default_category: FoodCategory) -> FoodCategory:
        """
        Validate a food item by its nutrition profile.
        Reclassify to INVALID if nutrition doesn't match expected category.
        """
        calories = nutrition.get('calories', 0) or 0
        protein = nutrition.get('protein', 0) or 0
        carbs = nutrition.get('carbs', 0) or 0
        fat = nutrition.get('fat', 0) or 0
        
        # Too low calories = condiment/ingredient
        if calories < self.MIN_MEAL_CALORIES:
            return FoodCategory.CONDIMENT
        
        # Too high calories = possible data error
        if calories > self.MAX_SINGLE_ITEM_CALORIES:
            return FoodCategory.INVALID
        
        # Pure fat-based ingredient detection
        if (fat > self.HIGH_FAT_THRESHOLD and 
            protein < self.LOW_PROTEIN_THRESHOLD and 
            carbs < self.LOW_CARBS_THRESHOLD):
            return FoodCategory.INGREDIENT
        
        # Must have meaningful protein OR carbs for a meal
        if protein < 2 and carbs < 10:
            return FoodCategory.CONDIMENT
        
        return default_category
    
    def _classify_by_nutrition_only(self, nutrition: Dict) -> FoodCategory:
        """
        Classify based solely on nutrition when name patterns don't match.
        """
        calories = nutrition.get('calories', 0) or 0
        protein = nutrition.get('protein', 0) or 0
        carbs = nutrition.get('carbs', 0) or 0
        fat = nutrition.get('fat', 0) or 0
        
        # Very low calories = condiment
        if calories < 50:
            return FoodCategory.CONDIMENT
        
        # Low calories + low macros = side dish or condiment
        if calories < 150 and protein < 5 and carbs < 20:
            return FoodCategory.SIDE_DISH
        
        # Balanced nutrition = likely a main meal
        if calories >= 150 and (protein >= 5 or carbs >= 15):
            return FoodCategory.MAIN_MEAL
        
        # Fat dominant = ingredient
        if fat > 50 and protein < 5:
            return FoodCategory.INGREDIENT
        
        return FoodCategory.MAIN_MEAL  # Default assumption
    
    def is_valid_meal(self, name: str, nutrition: Dict, 
                      allow_side_dishes: bool = False) -> bool:
        """
        Check if an item is a valid meal option.
        
        Args:
            name: Food item name
            nutrition: Dict with nutrition values
            allow_side_dishes: If True, side_dish is also valid
            
        Returns:
            True if valid meal, False otherwise
        """
        category = self.classify_food(name, nutrition)
        
        valid_categories = [FoodCategory.MAIN_MEAL]
        if allow_side_dishes:
            valid_categories.append(FoodCategory.SIDE_DISH)
        
        return category in valid_categories
    
    # ==================================================================
    # DATASET CLEANING PIPELINE
    # ==================================================================
    
    def clean_dataset(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Main pipeline to clean the food dataset.
        
        Pipeline:
        1. Add classification column
        2. Filter out ingredients and invalid items
        3. Return only valid meals
        
        Args:
            df: DataFrame with food data (must have name, calories, protein, carbs, fat)
            
        Returns:
            Cleaned DataFrame with only valid meals
        """
        print(f"  [FoodClassifier] Starting dataset cleaning: {len(df)} items")
        
        # Create copy to avoid modifying original
        df = df.copy()
        
        # Add classification column
        df['food_category'] = df.apply(
            lambda row: self.classify_food(
                row['name'],
                {
                    'calories': row.get('calories', 0),
                    'protein': row.get('protein', 0),
                    'carbs': row.get('carbs', 0),
                    'fat': row.get('fat', 0)
                }
            ).value,
            axis=1
        )
        
        # Filter to valid meals only
        valid_categories = ['main_meal', 'side_dish']
        df_clean = df[df['food_category'].isin(valid_categories)].copy()
        
        # Additional nutrition-based filtering
        df_clean = self._apply_nutrition_filters(df_clean)
        
        print(f"  [FoodClassifier] Cleaning complete: {len(df_clean)} valid meals")
        print(f"  [FoodClassifier] Removed: {len(df) - len(df_clean)} items")
        
        return df_clean
    
    def _apply_nutrition_filters(self, df: pd.DataFrame) -> pd.DataFrame:
        """Apply additional nutrition-based filters."""
        # Remove items with unrealistic nutrition profiles
        mask = (
            (df['calories'].fillna(0) >= self.MIN_MEAL_CALORIES) &
            (df['calories'].fillna(0) <= self.MAX_SINGLE_ITEM_CALORIES) &
            # Must have some substance (not just water/liquid)
            ((df['protein'].fillna(0) >= 1) | (df['carbs'].fillna(0) >= 5))
        )
        df_filtered = df[mask].copy()
        
        # Data quality: Flag suspiciously high protein relative to calories
        # e.g. "Consomme au vermicelli" claims 45.7g protein in 89 cal
        # (45.7g protein = 183 cal from protein alone, but total is 89 cal)
        # These are likely data entry errors
        protein_cal = df_filtered['protein'].fillna(0) * 4  # cal from protein
        total_cal = df_filtered['calories'].fillna(1)
        protein_ratio = protein_cal / total_cal.clip(lower=1)
        # If protein calories exceed total calories, the data is wrong
        # Allow up to 80% protein ratio (e.g. grilled chicken breast is ~75%)
        suspicious = protein_ratio > 0.80
        if suspicious.any():
            flagged = df_filtered[suspicious]['name'].tolist()
            print(f"  [FoodClassifier] Flagged {len(flagged)} items with suspicious protein data")
            df_filtered = df_filtered[~suspicious]
        
        return df_filtered
    
    # ==================================================================
    # MEAL COMBINATION SUGGESTIONS
    # ==================================================================
    
    def suggest_meal_combinations(self, df: pd.DataFrame, 
                                   meal_type: str = 'lunch') -> List[Dict]:
        """
        Suggest complete Indian meal combinations.
        
        Typical Indian meal structure:
        - Roti/Rice (carb base)
        - Dal/Curry (protein)
        - Sabzi/Vegetable (fiber)
        - Side (raita/pickle/salad) - optional
        
        Args:
            df: DataFrame with classified food items
            meal_type: 'breakfast', 'lunch', 'dinner', 'snack'
            
        Returns:
            List of meal combination suggestions
        """
        combinations = []
        
        # Get items by category
        mains = df[df['food_category'] == 'main_meal']
        sides = df[df['food_category'] == 'side_dish']
        
        if meal_type in ['lunch', 'dinner']:
            # Typical North Indian meal
            roti_items = mains[mains['name'].str.contains('roti|chapati|naan|paratha', case=False, na=False)]
            rice_items = mains[mains['name'].str.contains('rice|biryani|pulao', case=False, na=False)]
            dal_items = mains[mains['name'].str.contains('dal|sambar|kadhi', case=False, na=False)]
            curry_items = mains[mains['name'].str.contains('curry|sabzi|paneer|chicken|mutton', case=False, na=False)]
            
            # Create combinations
            if not roti_items.empty and not dal_items.empty:
                combinations.append({
                    'name': 'North Indian Vegetarian Thali',
                    'items': [
                        roti_items.iloc[0]['name'],
                        dal_items.iloc[0]['name'],
                        curry_items.iloc[0]['name'] if not curry_items.empty else None,
                        sides.iloc[0]['name'] if not sides.empty else None
                    ],
                    'type': 'vegetarian'
                })
            
            if not rice_items.empty and not curry_items.empty:
                combinations.append({
                    'name': 'Rice & Curry Combo',
                    'items': [
                        rice_items.iloc[0]['name'],
                        curry_items.iloc[0]['name'],
                        sides.iloc[0]['name'] if not sides.empty else None
                    ],
                    'type': 'mixed'
                })
        
        elif meal_type == 'breakfast':
            # South Indian breakfast
            dosa_items = mains[mains['name'].str.contains('dosa', case=False, na=False)]
            idli_items = mains[mains['name'].str.contains('idli', case=False, na=False)]
            
            if not dosa_items.empty:
                combinations.append({
                    'name': 'South Indian Breakfast',
                    'items': [dosa_items.iloc[0]['name'], 'sambar', 'chutney'],
                    'type': 'south_indian'
                })
        
        return [c for c in combinations if any(c['items'])]


class MealBuilder:
    """
    Production-level meal builder for creating balanced Indian meals.
    
    Creates meals with proper macro balance:
    - 1 carb (roti, rice, etc.)
    - 1 protein (dal, paneer, chicken, etc.)
    - 1 vegetable (sabzi, bhaji, etc.)
    - Optional 1 side (raita, salad, chutney)
    
    No regional classification - works for all Indian cuisines.
    """
    
    # ==================================================================
    # FOOD TAGGING PATTERNS
    # ==================================================================
    
    # Carbohydrate sources
    CARB_PATTERNS = [
        r'\broti\b', r'\bchapati\b', r'\bnaan\b', r'\bkulcha\b',
        r'\bparatha\b', r'\bbhatura\b', r'\bpoori\b', r'\bpuri\b',
        r'\brice\b', r'\bbiryani\b', r'\bpulao\b', r'\bfried rice\b',
        r'\bpoha\b', r'\bupma\b', r'\bbread\b', r'\btoast\b',
        r'\biddli\b', r'\bidli\b', r'\bdosa\b', r'\buttapam\b',
        r'\bappam\b', r'\bputtu\b', r'\bpathiri\b',
    ]
    
    # Protein sources
    PROTEIN_PATTERNS = [
        r'\bdal\b', r'\bsambar\b', r'\bkadhi\b', r'\bchana\b',
        r'\bchole\b', r'\brajma\b', r'\blobia\b', r'\bmung\b',
        r'\bmoong\b', r'\burad\b', r'\btoor\b',
        r'\btuar\b', r'\bmasoor\b', r'\bchickpea\b', r'\bbean\b',
        r'\bpaneer\b', r'\btofu\b', r'\bsoya\b', r'\bsoy\b',
        r'\bchicken\b', r'\bmutton\b', r'\blamb\b', r'\bgoat\b',
        r'\bfish\b', r'\bprawn\b', r'\bshrimp\b', r'\begg\b',
        r'\banda\b', r'\bomelette\b', r'\bomelet\b', r'\bkeema\b',
        r'\bcheese\b', r'\bcottage cheese\b',
    ]
    
    # Vegetable dishes
    VEGETABLE_PATTERNS = [
        r'\bsabzi\b', r'\bsabji\b', r'\bbhaji\b', r'\bbharta\b',
        r'\baloo\b', r'\bpotato\b', r'\bgobi\b', r'\bcauliflower\b',
        r'\bbhindi\b', r'\bokra\b', r'\blady finger\b',
        r'\bbaingan\b', r'\bbrinjal\b', r'\beggplant\b',
        r'\bpalak\b', r'\bspinach\b', r'\bmethi\b', r'\bfenugreek\b',
        r'\bkarela\b', r'\bbitter gourd\b', r'\btinda\b',
        r'\btori\b', r'\bridge gourd\b', r'\blauki\b', r'\bbottle gourd\b',
        r'\bparwal\b', r'\bpointed gourd\b', r'\bdrumstick\b',
        r'\bcabbage\b', r'\bpatta\b', r'\bcarrot\b', r'\bgajar\b',
        r'\bbeetroot\b', r'\bchukandar\b', r'\bbeans\b', r'\bfrench beans\b',
        r'\bcluster beans\b', r'\bguar\b', r'\bpeas\b', r'\bmatar\b',
        r'\bcorn\b', r'\bmakai\b', r'\bbhutta\b', r'\bcapsicum\b',
        r'\bshimla\b', r'\bbell pepper\b', r'\btomato\b', r'\btamatar\b',
        r'\bonion\b', r'\bpyaaz\b', r'\bmushroom\b', r'\bmixed veg\b',
        r'\bmix veg\b', r'\bvegetable\b', r'\bkorma\b', r'\bkurma\b',
    ]
    
    # Side dishes/accompaniments
    SIDE_PATTERNS = [
        r'\braita\b', r'\bchutney\b', r'\bsalad\b', r'\bkoshimbir\b',
        r'\bpapad\b', r'\bpapadum\b', r'\bpickle\b', r'\bachaar\b',
        r'\bcurd\b', r'\bdahi\b', r'\byogurt\b', r'\bcurry\b',
        r'\bsoup\b', r'\bbuttermilk\b', r'\bchaas\b', r'\blassi\b',
    ]
    
    # ==================================================================
    # MEAL VALIDATION THRESHOLDS
    # ==================================================================
    MIN_MEAL_CALORIES = 300
    MAX_MEAL_CALORIES = 800
    
    def __init__(self, food_items: List[Dict] = None):
        """
        Initialize MealBuilder with food items.
        
        Args:
            food_items: List of food dicts with name, calories, protein, carbs, fat
        """
        self.food_items = food_items or []
        self.tagged_items = {}
        
        # Compile regex patterns
        self.carb_regex = re.compile('|'.join(self.CARB_PATTERNS), re.IGNORECASE)
        self.protein_regex = re.compile('|'.join(self.PROTEIN_PATTERNS), re.IGNORECASE)
        self.veg_regex = re.compile('|'.join(self.VEGETABLE_PATTERNS), re.IGNORECASE)
        self.side_regex = re.compile('|'.join(self.SIDE_PATTERNS), re.IGNORECASE)
        
        # Tag all items if provided
        if food_items:
            self._tag_all_items()
    
    # ==================================================================
    # FOOD TAGGING SYSTEM
    # ==================================================================
    
    def assign_food_tag(self, food_name: str) -> str:
        """
        Assign a food tag based on food name patterns.
        
        Priority order: protein > carb > vegetable > side
        (protein is most important for meal balance)
        
        Args:
            food_name: Name of the food item
            
        Returns:
            Tag: "carb", "protein", "vegetable", "side", or "other"
        """
        name = food_name.lower().strip()
        
        # Check protein first (highest priority)
        if self.protein_regex.search(name):
            return "protein"
        
        # Check carb
        if self.carb_regex.search(name):
            return "carb"
        
        # Check vegetable
        if self.veg_regex.search(name):
            return "vegetable"
        
        # Check side
        if self.side_regex.search(name):
            return "side"
        
        return "other"
    
    def _tag_all_items(self):
        """Tag all food items and group by tag."""
        self.tagged_items = {
            "carb": [],
            "protein": [],
            "vegetable": [],
            "side": [],
            "other": []
        }
        for item in self.food_items:
            tag = self.assign_food_tag(item.get('name', ''))
            self.tagged_items[tag].append(item)
    
    def get_items_by_tag(self, tag: str) -> List[Dict]:
        """Get all items with a specific tag."""
        return self.tagged_items.get(tag, [])

    # =================================================================:
    # MEAL BUILDER
    # ==================================================================

    def generate_meal(self, meal_type: str = "lunch",
                     include_side: bool = True,
                     goal: str = "maintain",
                     used_items: set = None,
                     seed: Optional[int] = None,
                     max_attempts: int = 60) -> Optional[Dict]:
        """
        Generate one balanced meal with diversity controls and validation.
        """
        if not self.food_items:
            return None

        if not self.tagged_items:
            self._tag_all_items()

        if used_items is None:
            used_items = set()

        if seed is None:
            seed = random.randint(1, 10000)
        rng = random.Random(seed)

        goal_key = (goal or "maintain").strip().lower()
        if goal_key == "weight_loss":
            calorie_range = (300, 500)
        elif goal_key == "muscle_gain":
            calorie_range = (500, 800)
        else:
            calorie_range = (400, 700)

        def _filter_pool(items: List[Dict]) -> List[Dict]:
            pool = items
            diverse_pool = [i for i in pool if i.get("name") not in used_items]
            if diverse_pool:
                return diverse_pool
            return pool

        carbs = _filter_pool(self.get_items_by_tag("carb"))
        proteins = _filter_pool(self.get_items_by_tag("protein"))
        vegetables = _filter_pool(self.get_items_by_tag("vegetable"))
        sides = _filter_pool(self.get_items_by_tag("side")) if include_side else []

        if not carbs or not proteins:
            raise Exception("Not enough data to build meal")

        best_meal = None
        best_penalty = float("inf")

        for _ in range(max_attempts):
            meal_items = []

            carb_item = rng.choice(carbs)
            protein_item = rng.choice(proteins)
            meal_items.append(self._to_meal_item(carb_item, "carb"))
            meal_items.append(self._to_meal_item(protein_item, "protein"))

            if vegetables:
                meal_items.append(self._to_meal_item(rng.choice(vegetables), "vegetable"))

            if include_side and sides and rng.random() < 0.65:
                meal_items.append(self._to_meal_item(rng.choice(sides), "side"))

            # If meal is too light, add extra carb/protein picks to meet goal range.
            additions = 0
            while sum(i["calories"] for i in meal_items) < calorie_range[0] and additions < 3:
                source_pool = proteins if rng.random() < 0.5 else carbs
                if source_pool:
                    extra_item = rng.choice(source_pool)
                    meal_items.append(
                        self._to_meal_item(extra_item, self.assign_food_tag(extra_item.get("name", "")))
                    )
                additions += 1

            meal = self._aggregate_meal(meal_items, meal_type)
            in_range = calorie_range[0] <= meal["total_calories"] <= calorie_range[1]

            if self.is_valid_meal(meal) and self.score_meal(meal) >= 2:
                penalty = 0 if in_range else min(
                    abs(meal["total_calories"] - calorie_range[0]),
                    abs(meal["total_calories"] - calorie_range[1])
                )
                if penalty < best_penalty:
                    best_meal = meal
                    best_penalty = penalty

                if in_range:
                    meal["explanation"] = "Balanced meal with protein, carbs and vegetables"
                    for item in meal_items:
                        used_items.add(item["name"])
                    return meal

        if best_meal is not None:
            best_meal["explanation"] = "Balanced meal with protein, carbs and vegetables"
            for item in best_meal.get("items", []):
                used_items.add(item["name"])
            return best_meal

        return None

    def _to_meal_item(self, item: Dict, tag: str) -> Dict:
        """Normalize a raw food item for meal output."""
        return {
            "name": str(item.get("name", "")),
            "tag": tag,
            "calories": round(float(item.get("calories", 0) or 0), 1),
            "protein": round(float(item.get("protein", 0) or 0), 1),
            "carbs": round(float(item.get("carbs", 0) or 0), 1),
            "fat": round(float(item.get("fat", 0) or 0), 1),
        }

    def _aggregate_meal(self, items: List[Dict], meal_type: str) -> Dict:
        """Build meal-level totals from selected items."""
        total_calories = sum(i.get("calories", 0) for i in items)
        total_protein = sum(i.get("protein", 0) for i in items)
        total_carbs = sum(i.get("carbs", 0) for i in items)
        total_fat = sum(i.get("fat", 0) for i in items)

        return {
            "meal_type": meal_type,
            "items": items,
            "total_calories": round(total_calories, 1),
            "calories": round(total_calories, 1),
            "protein": round(total_protein, 1),
            "total_protein": round(total_protein, 1),
            "carbs": round(total_carbs, 1),
            "fat": round(total_fat, 1),
            "score": 0,
        }

    def is_valid_meal(self, meal: Dict) -> bool:
        """Strong validation guard for generated meals."""
        return (
            meal["total_calories"] >= 300 and
            meal["total_calories"] <= 800 and
            meal["protein"] >= 5 and
            any(item['tag'] == 'carb' for item in meal['items'])
        )

    def score_meal(self, meal: Dict) -> int:
        """Simple quality score for acceptance filtering."""
        score = 0

        if meal["protein"] > 10:
            score += 2
        if meal["total_calories"] < 700:
            score += 1

        meal["score"] = score
        return score


class MealEngine:
    """Deterministic dataset-driven weekly meal planning engine."""

    def __init__(self, nutrition_data_path: str = None):
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        csv_path = nutrition_data_path or os.path.join(base_dir, 'data', 'nutrition_processed.csv')

        if os.path.exists(csv_path):
            self.nutrition_df = pd.read_csv(csv_path)
            print(f" [MealEngine] Loaded {len(self.nutrition_df)} foods from {csv_path}")
        else:
            raise FileNotFoundError(f"Nutrition dataset not found at {csv_path}")

        # Initialize the food classifier for production-level filtering
        self.classifier = FoodClassifier()
        print(f" [MealEngine] FoodClassifier initialized")

        # Standardise column names once
        col_map = {
            'Name': 'name',
            'Type': 'meal_type',
            'calories': 'calories',
            'protein': 'protein',
            'carbohydrate': 'carbs',
            'total_fat': 'fat',
            'Tags': 'tags',
            'Allergens': 'allergens',
            'Swap_Group': 'swap_group',
            'Goal': 'goal_tag',
        }
        self.nutrition_df.rename(columns=col_map, inplace=True)

        # Fill NaNs
        for col in ['tags', 'allergens', 'swap_group', 'goal_tag']:
            if col in self.nutrition_df.columns:
                self.nutrition_df[col] = self.nutrition_df[col].fillna('')

        # Normalise meal_type to lowercase (Breakfast → breakfast)
        self.nutrition_df['meal_type'] = self.nutrition_df['meal_type'].str.lower().str.strip()

        # Pre-clean the dataset using FoodClassifier
        print(f" [MealEngine] Cleaning dataset with FoodClassifier...")
        self.nutrition_df = self.classifier.clean_dataset(self.nutrition_df)
        print(f" [MealEngine] Final dataset: {len(self.nutrition_df)} valid meals")

        # Load food blacklist — 300+ items that should never appear in a fitness app
        # (ice cream, alcohol, Christmas biscuits, cooking sauces, cakes, etc.)
        blacklist_path = os.path.join(base_dir, 'data', 'food_blacklist.json')
        if os.path.exists(blacklist_path):
            with open(blacklist_path, encoding='utf-8') as _bl_file:
                self.food_blacklist = set(json.load(_bl_file))
            # Apply blacklist to the pre-cleaned dataset
            pre_bl = len(self.nutrition_df)
            self.nutrition_df = self.nutrition_df[~self.nutrition_df['name'].isin(self.food_blacklist)]
            print(f" [MealEngine] Blacklist applied: removed {pre_bl - len(self.nutrition_df)} items")
            print(f" [MealEngine] Final clean dataset: {len(self.nutrition_df)} items")
        else:
            self.food_blacklist = set()
            print(" [MealEngine] WARNING: food_blacklist.json not found — no items blocked")

        # Protein targets in grams per kg of bodyweight (evidence-based: ISSN/ADA guidelines)
        # These produce realistic ranges: ~50–160g/day for most users.
        # After protein is fixed, remaining calories are split between carbs and fat.
        self.protein_per_kg = {
            'Weight Loss':  1.6,   # High protein preserves muscle during deficit
            'Fat Loss':     1.8,   # Higher protein prevents muscle catabolism
            'Muscle Gain':  1.8,   # ~1.6-2.0 g/kg is the evidence-based range
            'Strength':     1.8,   # Same as muscle gain for heavy lifters
            'Endurance':    1.4,   # Moderate — endurance athletes need less than strength
            'Maintenance':  1.0,   # General population (WHO: 0.8, active: 1.0–1.2)
            'Maintain':     1.0,
        }

        # After protein calories are accounted for, the REMAINING calories
        # are split between carbs and fat using these ratios (carbs : fat)
        self.remaining_carb_fat_split = {
            'Weight Loss':  {'carbs': 0.50, 'fat': 0.50},  # Balanced low-cal rest
            'Fat Loss':     {'carbs': 0.40, 'fat': 0.60},  # More fat (keto-adjacent)
            'Muscle Gain':  {'carbs': 0.65, 'fat': 0.35},  # Carb-forward for training
            'Strength':     {'carbs': 0.70, 'fat': 0.30},  # Heavy carb for lifts
            'Endurance':    {'carbs': 0.75, 'fat': 0.25},  # Max carb for aerobics
            'Maintenance':  {'carbs': 0.58, 'fat': 0.42},  # Balanced general diet
            'Maintain':     {'carbs': 0.58, 'fat': 0.42},
        }

        # Activity multipliers (Mifflin-St Jeor)
        self.activity_multipliers = {
            'Sedentary':   1.2,
            'Light':       1.375,
            'Moderate':    1.55,
            'Active':      1.725,
            'Very Active': 1.9,
        }

        # Meal calorie distribution
        self.meal_distribution = {
            'breakfast': 0.25,
            'lunch':     0.35,
            'dinner':    0.30,
            'snack':     0.10,
        }

    def _create_user_entropy(self, profile: Dict) -> str:
        """Build stable user entropy so two similar profiles still diverge."""
        entropy_parts = [
            str(profile.get('user_id') or profile.get('_id') or '').strip(),
            str(profile.get('email') or '').strip().lower(),
            str(profile.get('created_at') or profile.get('createdAt') or '').strip(),
            str(profile.get('registrationDate') or profile.get('registration_date') or '').strip(),
        ]
        base = '|'.join(entropy_parts)
        if not base.replace('|', '').strip():
            base = 'anonymous-user'
        return hashlib.sha256(base.encode()).hexdigest()[:24]

    def _create_profile_fingerprint(self, profile: Dict) -> str:
        """Create fingerprint from plan-affecting profile fields."""
        payload = {
            'age': int(float(profile.get('age', 25) or 25)),
            'weight': round(float(profile.get('weight', 70.0) or 70.0), 1),
            'height': round(float(profile.get('height', 175.0) or 175.0), 1),
            'goal': str(profile.get('goal', 'Maintenance')),
            'experience': str(profile.get('experience', 'Beginner')),
            'dietary_preference': str(profile.get('dietary_preference', 'Non-Veg')),
            'equipment': sorted([str(x).strip().lower() for x in (profile.get('equipment') or [])]),
            'body_issues': sorted([str(x).strip().lower() for x in (profile.get('body_issues') or [])]),
            'allergies': sorted([str(x).strip().lower() for x in (profile.get('allergies') or [])]),
            'days_per_week': int(profile.get('days_per_week', 4) or 4),
        }
        encoded = json.dumps(payload, sort_keys=True, separators=(',', ':'))
        return hashlib.sha256(encoded.encode()).hexdigest()[:24]

    def _seed_for_meal_slot(
        self,
        *,
        user_entropy: str,
        profile_fingerprint: str,
        week_offset: int,
        day_idx: int,
        meal_type: str,
    ) -> int:
        seed_material = f"{user_entropy}:{profile_fingerprint}:{week_offset}:{day_idx}:{meal_type}"
        return int(hashlib.sha256(seed_material.encode()).hexdigest()[:16], 16) % (10**9)

    # ─────────────────────────────────────────────
    #  CORE:  calorie / macro target calculations
    # ─────────────────────────────────────────────

    def calculate_daily_targets(self, profile: Dict) -> Dict:
        """
        Mifflin-St Jeor BMR → TDEE → goal adjustment → macros.

        Protein is calculated using body-weight-based targets (g/kg) from
        ISSN/ADA evidence-based guidelines, NOT as a percentage of calories.
        This prevents the common bug of recommending 200g+ protein.
        Carbs and fat are derived from the remaining non-protein calories.
        
        Gender-based adjustments:
        - Female users: Lower BMR (-161), reduced protein target (0.9x), adjusted calories
        - Male users: Standard BMR (+5), full protein target
        - Other: Average of male/female BMR offsets
        """
        gender = profile.get('gender', 'Male')
        weight = max(30, min(300, float(profile.get('weight', 70))))
        height = max(100, min(250, profile.get('height', 175)))
        age    = max(10, min(100, profile.get('age', 25)))

        # BMR calculation with proper gender handling
        if gender.lower() in ('male', 'm', 'man'):
            bmr = 10 * weight + 6.25 * height - 5 * age + 5
        elif gender.lower() in ('female', 'f', 'woman', 'women'):
            bmr = 10 * weight + 6.25 * height - 5 * age - 161
        else:
            # For "Other": use average of male and female offsets ((+5 + -161) / 2 = -78)
            bmr = 10 * weight + 6.25 * height - 5 * age - 78

        activity = self.activity_multipliers.get(
            profile.get('activity_level', 'Moderate'), 1.55
        )
        tdee = bmr * activity

        goal = profile.get('goal', 'Maintenance')
        goal_mult = {
            'Weight Loss': 0.85, 'Fat Loss': 0.80,
            'Muscle Gain': 1.10, 'Strength': 1.05,
            'Endurance': 1.00, 'Maintenance': 1.00,
            'Maintain': 1.00,
        }
        daily_calories = tdee * goal_mult.get(goal, 1.00)
        
        # Gender-based calorie adjustment: females typically need 10-15% fewer calories
        if gender.lower() in ('female', 'f', 'woman', 'women'):
            daily_calories *= 0.90  # 10% reduction for female users
        elif gender.lower() not in ('male', 'm', 'man'):
            daily_calories *= 0.95  # 5% reduction for other/neutral
        
        daily_calories = max(1200, min(5000, daily_calories))

        # ── Step 1: Fix protein using body-weight target (g/kg) ──────────────
        # Evidence-based: ISSN (2017), ADA, WHO guidelines
        # Produces realistic values: 56–135g for 60–75kg users
        protein_per_kg = self.protein_per_kg.get(goal, 1.0)
        
        # Gender-based protein adjustment
        # Research shows women have slightly lower protein utilization efficiency
        if gender.lower() in ('female', 'f', 'woman', 'women'):
            protein_per_kg *= 0.90  # 10% reduction (1.6-2.0g/kg instead of 1.8-2.2g/kg)
        elif gender.lower() not in ('male', 'm', 'man'):
            protein_per_kg *= 0.95  # 5% reduction for other/neutral
            
        protein_g = round(protein_per_kg * weight, 1)
        # Cap: protein should not exceed 35% of calories (2.2g/kg is max evidence limit)
        max_protein_g = round((daily_calories * 0.35) / 4, 1)
        protein_g = min(protein_g, max_protein_g)

        # ── Step 2: Remaining calories go to carbs + fat ──────────────────────
        protein_kcal = protein_g * 4
        remaining_kcal = max(0, daily_calories - protein_kcal)

        split = self.remaining_carb_fat_split.get(goal, {'carbs': 0.58, 'fat': 0.42})
        carb_g = round((remaining_kcal * split['carbs']) / 4, 1)
        fat_g  = round((remaining_kcal * split['fat']) / 9, 1)

        macros_g = {
            'protein_g': protein_g,
            'carb_g':    carb_g,
            'fat_g':     fat_g,
        }

        return {
            'daily_calories': round(daily_calories),
            'macro_targets_g': macros_g,
        }


    # ─────────────────────────────────────────────
    #  FILTERING: dietary pref, allergens, goal
    # ─────────────────────────────────────────────

    def _filter_foods(self, profile: Dict) -> pd.DataFrame:
        """
        Filter foods based on user profile preferences.
        The dataset is already pre-cleaned by FoodClassifier in __init__.
        
        Bug #4 Fix: Filter out side dishes and condiments from standalone selection.
        Only allow main_meal and appropriate side_dish items.
        """
        df = self.nutrition_df.copy()

        # Bug #4 Fix: Filter out side dishes, ingredients, condiments, and beverages
        # Only keep main_meal items for standalone meal selection
        if 'food_category' in df.columns:
            df = df[df['food_category'].isin(['main_meal'])]

        # Dietary preference
        pref = (profile.get('dietary_preference') or 'Non-Veg').lower().strip()
        if pref in ('veg', 'vegetarian', 'vegan'):
            df = df[df['tags'].str.lower().str.contains('veg', na=False)]
            # Further exclude non-veg swap groups
            df = df[~df['swap_group'].str.lower().str.contains('non-veg', na=False)]

        # Allergens — use word-boundary matching to prevent false positives
        # e.g. 'nut' should NOT filter out 'coconut' or 'butternut'
        allergies = profile.get('allergies', [])
        if allergies:
            boundary_patterns = [r'\b' + re.escape(a.lower()) + r'\b' for a in allergies if a]
            pattern = '|'.join(boundary_patterns)
            if pattern:
                df = df[~df['allergens'].str.lower().str.contains(pattern, na=False, regex=True)]

        # Goal-match preference: prefer goal-matching foods, but fall back to all
        # NOTE: The goal tag in the dataset is unreliable (only 606/1900 are Weight Loss).
        # We apply this filter ONLY when it leaves a substantial pool (50+ items).
        # Otherwise the per-meal-type split creates tiny pools (e.g. 5 lunch items).
        goal = profile.get('goal', 'Maintenance')
        goal_map = {
            'Weight Loss': 'Weight Loss',
            'Fat Loss': 'Weight Loss',
            'Muscle Gain': 'Muscle Gain',
            'Strength': 'Muscle Gain',
            'Endurance': 'Maintain',
            'Maintenance': 'Maintain',
            'Maintain': 'Maintain',
        }
        mapped_goal = goal_map.get(goal, 'Maintain')
        goal_df = df[df['goal_tag'].str.strip().str.lower() == mapped_goal.lower()]
        # Only apply goal filter if it leaves enough items per meal type
        # Check that we'd still have >= 10 items in each major meal type
        if len(goal_df) >= 50:
            mt_counts = goal_df['meal_type'].value_counts()
            has_enough = all(mt_counts.get(mt, 0) >= 8 for mt in ['breakfast', 'lunch', 'dinner'])
            if has_enough:
                df = goal_df

        if df.empty:
            df = self.nutrition_df.copy()
            # Re-apply blacklist + side dish filter even on fallback
            if self.food_blacklist:
                df = df[~df['name'].isin(self.food_blacklist)]
            if 'food_category' in df.columns:
                df = df[df['food_category'].isin(['main_meal'])]

        return df

    def generate_daily_plan(self, profile: Dict, goal: Optional[str] = None,
                            seed: Optional[int] = None) -> Dict:
        """
        Build a daily plan using MealBuilder + daily_planner integration.
        """
        filtered = self._filter_foods(profile)
        food_items = filtered.to_dict(orient='records')
        meal_builder = MealBuilder(food_items=food_items)
        planner_goal = (goal or profile.get('goal') or 'maintain').strip().lower().replace(' ', '_')
        plan = generate_day_plan(meal_builder, goal=planner_goal, seed=seed)
        return plan

    # ─────────────────────────────────────────────
    #  MEAL SELECTION  — greedy calorie-fit picker
    # ─────────────────────────────────────────────

    def _pick_meals_for_slot(self, pool: pd.DataFrame, target_cal: float,
                              target_macros: Dict, used_names: set,
                              seed: int = 0, meal_type: str = 'lunch') -> List[Dict]:
        """
        Pick food items from `pool` whose summed calories are
        within ±15 % of `target_cal` and macros are balanced.
        Deterministic per seed.
        
        Bug #3 Fix: Added macro-aware selection and validation.
        - Main meals (breakfast/lunch/dinner) must have ≥15g protein each
        - Snacks capped at ≤10g protein (max 8g ideal)
        - Snack protein must never exceed any main meal's protein
        """
        if pool.empty:
            return []

        rng = random.Random(seed)

        # Exclude already-used names (cross-meal dedup for the day)
        candidates = pool[~pool['name'].isin(used_names)].copy()
        if candidates.empty:
            candidates = pool.copy()

        # Dynamic dish count by slot and calorie target.
        # This avoids rigid fixed counts across users and days.
        if meal_type == 'breakfast':
            max_items = 2 if target_cal < 380 else 3 if target_cal < 620 else 4
        elif meal_type in ('lunch', 'dinner'):
            max_items = 2 if target_cal < 450 else 3 if target_cal < 700 else 4
        elif meal_type == 'snack':
            # Snack is optional when the target allocation is very small.
            if target_cal < 130:
                return []
            max_items = 1 if target_cal < 260 else 2
        else:
            max_items = 3

        per_item_target = target_cal / max_items
        
        # Bug #3 Fix: Score candidates by both calorie proximity AND macro balance
        # Prefer items with reasonable protein (not too high for snacks, not too low for mains)
        candidates['_diff'] = abs(candidates['calories'] - per_item_target)
        
        # Add macro similarity score (lower is better)
        if target_macros and 'protein_g' in target_macros:
            target_protein = target_macros['protein_g']
            per_item_protein = target_protein / max_items
            candidates['_protein_diff'] = abs(candidates['protein'] - per_item_protein)
            # Combined score: 60% calorie fit, 40% macro fit
            candidates['_score'] = candidates['_diff'] * 0.6 + candidates['_protein_diff'] * 2.0
            candidates = candidates.sort_values('_score')
        else:
            candidates = candidates.sort_values('_diff')

        selected = []
        remaining_cal = target_cal

        # First pass: greedily pick items that fit
        indices = list(candidates.index)
        rng.shuffle(indices)  # shuffle for variety day-to-day

        for idx in indices:
            if remaining_cal <= 30:  # close enough
                break
            row = candidates.loc[idx]
            cal = row['calories']
            protein = float(row.get('protein', 0))
            
            if cal <= 0:
                continue
                
            # Bug #3 Fix: Enforce calorie + protein constraints per meal type
            if meal_type == 'snack':
                if cal > 250:
                    continue   # M3 Fix: snack items must be under 250 cal
                if protein > 15:
                    continue   # Skip extremely high-protein items in snacks
            if meal_type in ('breakfast', 'lunch', 'dinner') and protein < 5:
                continue  # Skip very low-protein main meals
            
            if cal <= remaining_cal * 1.3:
                selected.append({
                    'name': row['name'],
                    'calories': round(float(cal)),
                    'protein': round(float(protein), 1),
                    'carbs': round(float(row.get('carbs', 0)), 1),
                    'fat': round(float(row.get('fat', 0)), 1),
                    'swap_group': str(row.get('swap_group', '')),
                })
                remaining_cal -= cal
                used_names.add(row['name'])
            if len(selected) >= max_items:
                break

        # Bug #3 Fix: Validate and enforce minimums
        # If main meal has no items or too little protein, force-add a protein source
        if meal_type in ('breakfast', 'lunch', 'dinner') and selected:
            total_protein = sum(item['protein'] for item in selected)
            if total_protein < 15:  # Minimum 15g protein per main meal
                # Find a high-protein item from the pool
                high_protein = candidates[candidates['protein'] >= 15]
                if not high_protein.empty and len(selected) < max_items:
                    best = high_protein.iloc[0]
                    selected.append({
                        'name': best['name'],
                        'calories': round(float(best['calories'])),
                        'protein': round(float(best['protein']), 1),
                        'carbs': round(float(best.get('carbs', 0)), 1),
                        'fat': round(float(best.get('fat', 0)), 1),
                        'swap_group': str(best.get('swap_group', '')),
                    })
                    used_names.add(best['name'])

        # Make sure we got at least 1
        if not selected and not candidates.empty:
            row = candidates.iloc[0]
            selected.append({
                'name': row['name'],
                'calories': round(float(row['calories'])),
                'protein': round(float(row.get('protein', 0)), 1),
                'carbs': round(float(row.get('carbs', 0)), 1),
                'fat': round(float(row.get('fat', 0)), 1),
                'swap_group': str(row.get('swap_group', '')),
            })
            used_names.add(row['name'])

        return selected

    # ─────────────────────────────────────────────
    #  PUBLIC:  generate a 7-day weekly plan
    # ─────────────────────────────────────────────

    def generate_weekly_plan(self, profile: Dict) -> Dict:
        targets = self.calculate_daily_targets(profile)
        daily_cal = targets['daily_calories']
        macros_g  = targets['macro_targets_g']

        print(f"\n[DeterministicMealEngine] Generating weekly plan...")
        print(f"  - Daily calories target: {daily_cal}")
        print(f"  - Macro targets (g): {macros_g}")

        now = _utcnow()
        iso_year, iso_week, _ = now.isocalendar()
        _raw_offset = profile.get('week_offset')
        week_offset = int(_raw_offset if _raw_offset is not None else ((iso_year * 100) + iso_week))
        user_entropy = self._create_user_entropy(profile)
        profile_fingerprint = self._create_profile_fingerprint(profile)

        print(f"  - Filtering foods for profile: goal={profile.get('goal')}, dietary={profile.get('dietary_preference')}")
        filtered = self._filter_foods(profile)
        print(f"  - Foods after filtering: {len(filtered)}")
        if len(filtered) > 0:
            print(f"  - Sample foods: {filtered['name'].head(10).tolist()}")
            # Show meal_type distribution
            meal_type_dist = filtered['meal_type'].value_counts()
            print(f"  - Meal type distribution: {meal_type_dist.to_dict()}")
        else:
            print(f"  [WARNING] No foods after filtering! This will cause empty meal plans.")

        # Bug #4 Fix: Split pool by meal type, ensuring side dishes don't appear as mains
        # Snack pool gets additional filtering to remove heavy meals mislabelled as snacks
        SNACK_MEAL_BLACKLIST_PATTERNS = [
            'dal', 'khichdi', 'biryani', 'pulao', 'curry', 'sabzi', 'sabji',
            'sauce', 'baghar', 'tadka', 'pickle', 'achaar', 'achar', 'chutney',
            'korma', 'bharta', 'fry', 'roast', 'masala', 'paneer lababdar',
            'dal makhani', 'dalma', 'panchmel', 'horsegram', 'bengal gram',
            'ketchup', 'mayonnaise', 'dressing',
        ]
        MAX_SNACK_CALORIES = 250  # Snack items must be under 250 cal per item

        pools = {}
        for mt in ('breakfast', 'lunch', 'dinner', 'snack'):
            mp = filtered[filtered['meal_type'] == mt].copy()

            # Additional safety: Ensure no side dishes slip through
            if 'food_category' in mp.columns:
                mp = mp[mp['food_category'] == 'main_meal']

            if mt == 'snack':
                # M1 Fix: Remove heavy meal items that are mislabelled as snacks in dataset
                for pattern in SNACK_MEAL_BLACKLIST_PATTERNS:
                    mp = mp[~mp['name'].str.lower().str.contains(pattern, na=False)]
                # M3 Fix: Hard calorie cap — snack items must be under 250 cal per row
                mp = mp[mp['calories'] <= MAX_SNACK_CALORIES]

            pools[mt] = mp if not mp.empty else filtered
            print(f"  - {mt} pool: {len(mp)} items")

        weekly_plan = {}
        day_names = ['Monday', 'Tuesday', 'Wednesday', 'Thursday',
                     'Friday', 'Saturday', 'Sunday']

        for day_idx, day_name in enumerate(day_names):
            day_plan = {}
            used_names_today = set()

            for mt, ratio in self.meal_distribution.items():
                slot_cal = daily_cal * ratio
                slot_macros = {
                    'protein_g': macros_g['protein_g'] * ratio,
                    'carb_g':    macros_g['carb_g'] * ratio,
                    'fat_g':     macros_g['fat_g'] * ratio,
                }
                seed = self._seed_for_meal_slot(
                    user_entropy=user_entropy,
                    profile_fingerprint=profile_fingerprint,
                    week_offset=week_offset,
                    day_idx=day_idx,
                    meal_type=mt,
                )
                items = self._pick_meals_for_slot(
                    pools[mt], slot_cal, slot_macros,
                    used_names_today, seed=seed, meal_type=mt
                )
                day_plan[mt] = items
                if day_idx == 0:  # Only log for first day to avoid spam
                    print(f"    - {day_name} {mt}: picked {len(items)} items")

            weekly_plan[day_name] = day_plan

        # ─── Summary ───
        summary = self._build_weekly_summary(weekly_plan, targets)

        return {
            'user_profile': {
                'daily_calorie_target': daily_cal,
                'macro_targets_g': macros_g,
            },
            'daily_targets': targets,
            'weekly_plan': weekly_plan,
            'weekly_summary': summary,
            'mealWeekMetadata': {
                'generated_at': now.isoformat(),
                'week_offset': week_offset,
                'user_entropy': user_entropy,
                'profile_fingerprint': profile_fingerprint,
            },
            'generation_timestamp': datetime.now().isoformat(),
        }

    # ─────────────────────────────────────────────
    #  SWAP: Mathematical Macro Similarity Engine
    # ─────────────────────────────────────────────

    def get_swap_options(self, food_name: str, meal_type: str,
                         profile: Dict, limit: int = 5) -> List[Dict]:
        """
        Industry-level recommendation engine:
        Finds alternatives by calculating Euclidean distance across scaled macro vectors
        [calories, protein, carbs, fat], heavily penalizing items that disrupt the user's
        daily calorie or protein targets.
        """
        filtered = self._filter_foods(profile)

        # 1. Locate the original food item
        match = filtered[filtered['name'].str.lower() == food_name.lower()]
        if match.empty:
            match = self.nutrition_df[self.nutrition_df['name'].str.lower() == food_name.lower()]

        if match.empty:
            # Fallback: Just return random items of the same meal_type
            alt = filtered[filtered['meal_type'] == meal_type.lower()]
            alt = alt.sample(n=min(limit, len(alt))) if not alt.empty else alt
        else:
            orig = match.iloc[0]
            orig_cal = float(orig['calories'])
            orig_pro = float(orig.get('protein', 0))
            orig_car = float(orig.get('carbs', 0))
            orig_fat = float(orig.get('fat', 0))

            # 2. Candidate Pool: Same meal_type OR same Swap_Group, excluding the original
            # Also filter out low-calorie/non-meal items (< 50 cal) like raw spices
            swap_group = orig.get('swap_group', '')
            if swap_group:
                candidates = filtered[
                    ((filtered['meal_type'] == meal_type.lower()) | (filtered['swap_group'] == swap_group)) &
                    (filtered['name'].str.lower() != food_name.lower()) &
                    (filtered['calories'] >= 50)
                ].copy()
            else:
                candidates = filtered[
                    (filtered['meal_type'] == meal_type.lower()) &
                    (filtered['name'].str.lower() != food_name.lower()) &
                    (filtered['calories'] >= 50)
                ].copy()

            if candidates.empty:
                return []

            # 3. Vectorized Distance Calculation (Macro Similarity)
            # Weights: Calories (2.0x), Protein (1.5x), Carbs (1.0x), Fat (1.0x)
            # We normalize the diff by the original value (or 1 to avoid div-by-zero)
            
            cal_diff = ((candidates['calories'] - orig_cal) / max(orig_cal, 1)) ** 2 * 2.0
            pro_diff = ((candidates['protein'].fillna(0) - orig_pro) / max(orig_pro, 1)) ** 2 * 1.5
            car_diff = ((candidates['carbs'].fillna(0) - orig_car) / max(orig_car, 1)) ** 2 * 1.0
            fat_diff = ((candidates['fat'].fillna(0) - orig_fat) / max(orig_fat, 1)) ** 2 * 1.0

            # Total Euclid-like penalty score
            candidates['_score'] = np.sqrt(cal_diff + pro_diff + car_diff + fat_diff)

            # 4. Sort by best mathematical match
            alt = candidates.sort_values('_score').head(limit)

        # 5. Format results
        results = []
        for _, row in alt.iterrows():
            results.append({
                'name': row['name'],
                'calories': round(float(row['calories'])),
                'protein': round(float(row.get('protein', 0)), 1),
                'carbs': round(float(row.get('carbs', 0)), 1),
                'fat': round(float(row.get('fat', 0)), 1),
                'swap_group': str(row.get('swap_group', '')),
            })

        return results

    # ─────────────────────────────────────────────
    #  Internal helpers
    # ─────────────────────────────────────────────

    def _build_weekly_summary(self, weekly_plan: Dict, targets: Dict) -> Dict:
        total_cal = total_pro = total_carb = total_fat = 0

        for day_meals in weekly_plan.values():
            for items in day_meals.values():
                for item in items:
                    total_cal  += item['calories']
                    total_pro  += item['protein']
                    total_carb += item['carbs']
                    total_fat  += item['fat']

        daily_avg_cal = total_cal / 7
        target_cal    = targets['daily_calories']
        consistency   = max(0, 1 - abs(daily_avg_cal - target_cal) / max(target_cal, 1))

        # Shopping list
        shopping = Counter()
        for day_meals in weekly_plan.values():
            for items in day_meals.values():
                for item in items:
                    shopping[item['name']] += 1

        return {
            'total_calories': round(total_cal),
            'daily_average': {
                'calories': round(daily_avg_cal),
                'protein_g': round(total_pro / 7, 1),
                'carbs_g':   round(total_carb / 7, 1),
                'fat_g':     round(total_fat / 7, 1),
            },
            'consistency_score': round(consistency, 2),
            'shopping_list': dict(shopping),
        }


# ─── Module-level convenience functions kept for backward compat ───

def algorithm_logic():
    print("Deterministic dataset-driven meal engine. See MealEngine class.")

def pseudocode():
    print("See MealEngine.generate_weekly_plan() source.")

def optimization_strategy():
    print("Greedy calorie-fit with Swap_Group diversity.")

def example_weekly_json():
    print("Run MealEngine().generate_weekly_plan({...}) for live output.")

def shopping_list_generator_logic():
    print("Shopping list is auto-generated from the weekly plan aggregation.")