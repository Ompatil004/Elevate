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
        for col in ['calories', 'protein', 'total_fat', 'carbohydrate']:
            df_nutr[col] = df_nutr[col].astype(str).str.replace(r'[^\d.]', '', regex=True)
            df_nutr[col] = pd.to_numeric(df_nutr[col], errors='coerce').fillna(0)

        # Assign Goals
        def assign_goal(row):
            if row['protein'] > 20: return 'Muscle Gain'
            elif row['calories'] < 400 and row['total_fat'] < 10: return 'Weight Loss'
            else: return 'Maintain'

        df_nutr['Goal'] = df_nutr.apply(assign_goal, axis=1)
        df_nutr.to_csv(PROCESSED_NUTRITION, index=False)
        print("✔ Nutrition data saved.")
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

        df_ex['Difficulty'] = df_ex['equipment'].apply(assign_difficulty)
        df_ex.to_csv(PROCESSED_EXERCISES, index=False)
        print("✔ Exercise data saved.")
    else:
        print(f"❌ Error: {RAW_EXERCISES} not found.")

if __name__ == "__main__":
    clean_data()