import pandas as pd
import numpy as np
import os

# Robust Paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, '../data')

class MLService:
    def __init__(self):
        self.exercises_df = None
        self.nutrition_df = None
        self.load_data()

    def load_data(self):
        print("Loading CSV Data...")
        try:
            ex_path = os.path.join(DATA_DIR, 'exercises_processed.csv')
            nut_path = os.path.join(DATA_DIR, 'nutrition_processed.csv')
            
            if os.path.exists(ex_path):
                self.exercises_df = pd.read_csv(ex_path)
            else:
                print(f"❌ Warning: {ex_path} not found")

            if os.path.exists(nut_path):
                self.nutrition_df = pd.read_csv(nut_path)
            else:
                print(f"❌ Warning: {nut_path} not found")
                
            print("✔ Data Loaded")
        except Exception as e:
            print(f"❌ Error loading data: {e}")

    def recommend_workout(self, experience_level):
        if self.exercises_df is None: return []
        
        # Filter by Difficulty
        candidates = self.exercises_df[self.exercises_df['Difficulty'] == experience_level]
        if candidates.empty: return []
        
        # Get random sample
        sample = candidates.sample(n=min(5, len(candidates)))
        
        # --- CRITICAL FIX: Replace NaN with None for JSON safety ---
        sample = sample.replace({np.nan: None})
        
        return sample.to_dict(orient='records')

    def recommend_meals(self, goal, calorie_limit=None):
        if self.nutrition_df is None: return []
        
        # Filter by Goal
        candidates = self.nutrition_df[self.nutrition_df['Goal'] == goal]
        if candidates.empty: return []
        
        sample = candidates.sample(n=min(3, len(candidates)))
        
        # --- CRITICAL FIX: Replace NaN with None for JSON safety ---
        sample = sample.replace({np.nan: None})
        
        return sample.to_dict(orient='records')

ml_service = MLService()