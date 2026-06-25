import pandas as pd
import numpy as np
import logging

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

class DataValidator:
    def __init__(self, df: pd.DataFrame):
        self.df = df
        self.errors = []

    def run_all_checks(self) -> bool:
        logger.info(f"Starting validation on {len(self.df)} records.")
        self.check_duplicates()
        self.check_negative_values()
        self.check_missing_macros()
        self.check_macro_calorie_balance()
        self.check_impossible_portions()
        self.check_categorization()
        
        if self.errors:
            logger.error("Validation Failed. Found the following errors:")
            for err in self.errors:
                logger.error(err)
            return False
        
        logger.info("Validation Passed! No critical errors found.")
        return True

    def check_duplicates(self):
        dups = self.df[self.df.duplicated('food_id')]
        if not dups.empty:
            self.errors.append(f"Duplicate food_ids found: {dups['food_id'].tolist()}")

        dup_names = self.df[self.df.duplicated('food_name')]
        if not dup_names.empty:
            logger.warning(f"Found duplicate food names (might be variations): {dup_names['food_name'].tolist()[:5]}...")

    def check_negative_values(self):
        cols_to_check = ['serving_size_g', 'calories_kcal', 'protein_g', 'carbohydrates_g', 'fat_g']
        for col in cols_to_check:
            if col in self.df.columns:
                negatives = self.df[self.df[col] < 0]
                if not negatives.empty:
                    self.errors.append(f"Negative values found in {col} for food_ids: {negatives['food_id'].tolist()}")

    def check_missing_macros(self):
        # We allow 0, but not NaN or completely blank if calories > 0
        macros = ['protein_g', 'carbohydrates_g', 'fat_g']
        for macro in macros:
            missing = self.df[self.df[macro].isna()]
            if not missing.empty:
                self.errors.append(f"Missing {macro} for food_ids: {missing['food_id'].tolist()}")

    def check_macro_calorie_balance(self):
        # Calories should roughly equal (protein*4 + carbs*4 + fat*9)
        # We allow a 20% margin of error due to rounding, fiber, etc.
        if set(['protein_g', 'carbohydrates_g', 'fat_g', 'calories_kcal']).issubset(self.df.columns):
            calculated_cals = (self.df['protein_g'] * 4) + (self.df['carbohydrates_g'] * 4) + (self.df['fat_g'] * 9)
            variance = abs(calculated_cals - self.df['calories_kcal']) / (self.df['calories_kcal'].replace(0, 1))
            
            # Find items with > 25% variance where calories > 10 (ignore very low cal items)
            bad_math = self.df[(variance > 0.25) & (self.df['calories_kcal'] > 10)]
            if not bad_math.empty:
                logger.warning(f"Found {len(bad_math)} items with misaligned macros/calories. Review required.")

    def check_impossible_portions(self):
        # e.g., protein > serving size
        if 'protein_g' in self.df.columns and 'serving_size_g' in self.df.columns:
            impossible = self.df[self.df['protein_g'] > self.df['serving_size_g']]
            if not impossible.empty:
                self.errors.append(f"Protein > Serving size for food_ids: {impossible['food_id'].tolist()}")

    def check_categorization(self):
        if 'category' in self.df.columns:
            allowed_categories = ['Healthy Beverage', 'Fruits', 'Traditional Meal', 'Dairy', 'Eggs', 'Chicken/Meat', 'Paneer', 'Whole Grains', 'Rice', 'Dal & Pulses', 'Vegetables', 'Salad', 'Snack', 'Dessert', 'Fish/Seafood', 'Nuts/Seeds']
            invalid_cats = self.df[~self.df['category'].isin(allowed_categories)]
            if not invalid_cats.empty:
                logger.warning(f"Found unfamiliar categories: {invalid_cats['category'].unique().tolist()}")

if __name__ == "__main__":
    import os
    file_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'nutrition_production_final_v4.csv')
    if os.path.exists(file_path):
        df = pd.read_csv(file_path)
        validator = DataValidator(df)
        validator.run_all_checks()
    else:
        logger.error(f"Dataset not found at {file_path}")
