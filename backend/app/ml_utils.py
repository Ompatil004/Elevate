import pandas as pd
import numpy as np
import os
import joblib
from sklearn.preprocessing import LabelEncoder

# Robust Paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, '../data')
MODELS_DIR = os.path.join(BASE_DIR, '../models')

class MLService:
    def __init__(self):
        self.exercises_df = None
        self.nutrition_df = None
        self.meal_model = None
        self.workout_model = None
        self.goal_encoder = None
        self.load_data()
        self.load_models()

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

    def load_models(self):
        print("Loading ML Models...")
        try:
            meal_model_path = os.path.join(MODELS_DIR, 'meal_model.pkl')
            workout_model_path = os.path.join(MODELS_DIR, 'workout_model.pkl')
            goal_encoder_path = os.path.join(MODELS_DIR, 'goal_encoder.pkl')

            if os.path.exists(meal_model_path):
                self.meal_model = joblib.load(meal_model_path)
                print("✔ Meal model loaded")
            else:
                print(f"❌ Warning: {meal_model_path} not found")

            if os.path.exists(workout_model_path):
                self.workout_model = joblib.load(workout_model_path)
                print("✔ Workout model loaded")
            else:
                print(f"❌ Warning: {workout_model_path} not found")

            if os.path.exists(goal_encoder_path):
                self.goal_encoder = joblib.load(goal_encoder_path)
                print("✔ Goal encoder loaded")
            else:
                print(f"❌ Warning: {goal_encoder_path} not found")

        except Exception as e:
            print(f"❌ Error loading models: {e}")

    def recommend_workout(self, experience_level):
        if self.exercises_df is None: return []

        # Try ML-based recommendation first
        if self.workout_model is not None:
            try:
                # Prepare features for prediction
                # Assuming the model expects experience level encoding
                experience_mapping = {'Beginner': 0, 'Intermediate': 1, 'Advanced': 2}
                experience_encoded = experience_mapping.get(experience_level, 0)

                # Get prediction (assuming model outputs exercise indices or categories)
                prediction = self.workout_model.predict([[experience_encoded]])[0]

                # Filter exercises based on prediction
                if isinstance(prediction, (int, np.integer)):
                    # If prediction is an index, get exercise by index
                    if prediction < len(self.exercises_df):
                        recommended_exercise = self.exercises_df.iloc[prediction:prediction+1]
                    else:
                        recommended_exercise = self.exercises_df.sample(n=1)
                else:
                    # If prediction is a category, filter by difficulty
                    candidates = self.exercises_df[self.exercises_df['Difficulty'] == prediction]
                    recommended_exercise = candidates.sample(n=1) if not candidates.empty else self.exercises_df.sample(n=1)

                # Get 4 more exercises for a complete workout
                remaining_exercises = self.exercises_df[self.exercises_df.index != recommended_exercise.index[0]]
                additional_exercises = remaining_exercises.sample(n=min(4, len(remaining_exercises)))

                recommendations = pd.concat([recommended_exercise, additional_exercises])

            except Exception as e:
                print(f"ML prediction failed, falling back to filtering: {e}")
                # Fallback to original filtering
                candidates = self.exercises_df[self.exercises_df['Difficulty'] == experience_level]
                recommendations = candidates.sample(n=min(5, len(candidates))) if not candidates.empty else self.exercises_df.sample(n=5)
        else:
            # Original filtering approach
            candidates = self.exercises_df[self.exercises_df['Difficulty'] == experience_level]
            if candidates.empty: return []
            recommendations = candidates.sample(n=min(5, len(candidates)))

        # --- CRITICAL FIX: Replace NaN with None for JSON safety ---
        recommendations = recommendations.replace({np.nan: None})

        return recommendations.to_dict(orient='records')

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