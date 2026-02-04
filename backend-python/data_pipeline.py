import pandas as pd
import os

# Define paths relative to this script
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, 'data')

RAW_NUTRITION = os.path.join(DATA_DIR, 'nutrition.csv')
PROCESSED_NUTRITION = os.path.join(DATA_DIR, 'nutrition_processed.csv')

RAW_EXERCISES = os.path.join(DATA_DIR, 'exercises.csv')
PROCESSED_EXERCISES = os.path.join(DATA_DIR, 'exercises_processed.csv')

def clean_data():
    print("--- Starting Data Pipeline ---")
    
    # 1. PROCESS NUTRITION
    if os.path.exists(RAW_NUTRITION):
        print(f"Processing {RAW_NUTRITION}...")
        df_nutr = pd.read_csv(RAW_NUTRITION)
        
        # Clean units (remove 'g', 'mg', etc)
        # Map actual column names to expected names
        column_mapping = {
            'Calories': 'calories',
            'Protein': 'protein',
            'Fats': 'total_fat',
            'Carbs': 'carbohydrate'
        }

        # Rename columns to expected format
        for old_col, new_col in column_mapping.items():
            if old_col in df_nutr.columns:
                df_nutr = df_nutr.rename(columns={old_col: new_col})

        # Apply cleaning to the renamed columns
        for col in ['calories', 'protein', 'total_fat', 'carbohydrate']:
            if col in df_nutr.columns:
                df_nutr[col] = df_nutr[col].astype(str).str.replace(r'[^\d.]', '', regex=True)
                df_nutr[col] = pd.to_numeric(df_nutr[col], errors='coerce').fillna(0)

        # Assign Goals
        def assign_goal(row):
            protein_val = row.get('protein', 0)
            calorie_val = row.get('calories', 0)
            fat_val = row.get('total_fat', 0)

            if protein_val > 20: return 'Muscle Gain'
            elif calorie_val < 400 and fat_val < 10: return 'Weight Loss'
            else: return 'Maintain'

        # Only apply goal assignment if required columns exist
        if 'protein' in df_nutr.columns and 'calories' in df_nutr.columns and 'total_fat' in df_nutr.columns:
            df_nutr['Goal'] = df_nutr.apply(assign_goal, axis=1)
        else:
            # Default goal if columns don't exist
            df_nutr['Goal'] = 'Maintain'
        df_nutr.to_csv(PROCESSED_NUTRITION, index=False)
        print("OK Nutrition data saved.")
    else:
        print(f"❌ Error: {RAW_NUTRITION} not found.")

    # 2. PROCESS EXERCISES
    if os.path.exists(RAW_EXERCISES):
        print(f"Processing {RAW_EXERCISES}...")
        df_ex = pd.read_csv(RAW_EXERCISES)

        # Assign Difficulty
        def assign_difficulty(equip):
            equip = str(equip).lower()
            if any(x in equip for x in ['body weight', 'assisted', 'band']): return 'Beginner'
            elif any(x in equip for x in ['dumbbell', 'barbell', 'cable']): return 'Intermediate'
            else: return 'Advanced'

        # Check if 'equipment' column exists, otherwise use the actual column name
        if 'equipment' in df_ex.columns:
            df_ex['Difficulty'] = df_ex['equipment'].apply(assign_difficulty)
        elif 'Equipment' in df_ex.columns:  # Use actual column name from the data
            df_ex['Difficulty'] = df_ex['Equipment'].apply(assign_difficulty)
            # Rename to standard name
            df_ex = df_ex.rename(columns={'Equipment': 'equipment'})
        else:
            # Default difficulty if no equipment column exists
            df_ex['Difficulty'] = 'Beginner'
        df_ex.to_csv(PROCESSED_EXERCISES, index=False)
        print("OK Exercise data saved.")
    else:
        print(f"ERROR: {RAW_EXERCISES} not found.")

if __name__ == "__main__":
    clean_data()