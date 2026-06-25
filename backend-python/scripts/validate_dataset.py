import os
import sys
import pandas as pd
import logging

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

def validate_dataset(csv_path: str) -> bool:
    if not os.path.exists(csv_path):
        logging.error(f"Dataset not found at {csv_path}")
        return False

    df = pd.read_csv(csv_path)
    is_valid = True

    # 1. Duplicate IDs
    duplicate_ids = df[df.duplicated('food_id')]
    if not duplicate_ids.empty:
        logging.error(f"Found {len(duplicate_ids)} duplicate food_ids.")
        is_valid = False

    # 2. Duplicate Names
    duplicate_names = df[df.duplicated('food_name')]
    if not duplicate_names.empty:
        logging.error(f"Found {len(duplicate_names)} duplicate food_names.")
        is_valid = False

    # 3. Impossible Macros
    # 1g Protein = 4 kcal, 1g Carb = 4 kcal, 1g Fat = 9 kcal
    # Give a 20% tolerance due to fiber and rounding
    calculated_cals = (df['protein_g'] * 4) + (df['carbohydrates_g'] * 4) + (df['fat_g'] * 9)
    macro_mismatch = df[abs(df['calories_kcal'] - calculated_cals) > (0.2 * df['calories_kcal'] + 20)]
    
    if not macro_mismatch.empty:
        logging.error(f"Found {len(macro_mismatch)} items with impossible macros (calories don't match P/C/F).")
        # In a real strict environment, we'd fail here. We will just log warnings for now if we don't want to crash immediately on edge cases,
        # but the spec says "fail to start".
        is_valid = False

    # 4. Missing Portions
    missing_portions = df[df['serving_size_g'].isna() | (df['serving_size_g'] <= 0)]
    if not missing_portions.empty:
        logging.error(f"Found {len(missing_portions)} items with missing or 0 serving size.")
        is_valid = False
        
    # 5. Missing Semantics
    missing_category = df[df['category'].isna() | df['subcategory'].isna()]
    if not missing_category.empty:
        logging.error(f"Found {len(missing_category)} items missing category/subcategory.")
        is_valid = False

    if is_valid:
        logging.info("Dataset validation passed!")
    else:
        logging.error("Dataset validation failed! Please fix the dataset before starting the engine.")

    return is_valid

if __name__ == "__main__":
    current_dir = os.path.dirname(os.path.abspath(__file__))
    csv_path = os.path.join(current_dir, "..", "data", "nutrition_production_final_v4.csv")
    
    success = validate_dataset(csv_path)
    if not success:
        sys.exit(1)
    else:
        sys.exit(0)
