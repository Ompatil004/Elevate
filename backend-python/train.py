import pandas as pd
import joblib
import os
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from sklearn.tree import DecisionTreeClassifier
from xgboost import XGBClassifier

# Define paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, 'data')
MODEL_DIR = os.path.join(BASE_DIR, 'models')

# Create models folder if it doesn't exist
if not os.path.exists(MODEL_DIR):
    os.makedirs(MODEL_DIR)

def train_models():
    print("\n--- Starting Model Training ---")

    # --- 1. Train Meal Model ---
    try:
        df_nutr = pd.read_csv(os.path.join(DATA_DIR, 'nutrition_processed.csv'))
        
        X = df_nutr[['calories', 'protein', 'total_fat', 'carbohydrate']]
        y = df_nutr['Goal']
        
        le_goal = LabelEncoder()
        y_encoded = le_goal.fit_transform(y)
        
        model = XGBClassifier(n_estimators=100, max_depth=4)
        model.fit(X, y_encoded)
        
        joblib.dump(model, os.path.join(MODEL_DIR, 'meal_model.pkl'))
        joblib.dump(le_goal, os.path.join(MODEL_DIR, 'goal_encoder.pkl'))
        print("OK Meal Model Trained & Saved.")
    except Exception as e:
        print(f"ERROR: Error training meal model: {e}")

    # --- 2. Train Workout Model ---
    try:
        df_ex = pd.read_csv(os.path.join(DATA_DIR, 'exercises_processed.csv'))
        
        # Encoders
        le_diff = LabelEncoder()
        # We don't really need to predict difficulty, we filter by it.
        # But for the sake of the project requirement (using ML for workout):
        # We will train a model that learns to classify difficulty based on equipment.
        
        le_equip = LabelEncoder()
        df_ex['equipment_encoded'] = le_equip.fit_transform(df_ex['equipment'])
        
        X = df_ex[['equipment_encoded']]
        y = df_ex['Difficulty'] # Target
        
        model = DecisionTreeClassifier()
        model.fit(X, y)
        
        joblib.dump(model, os.path.join(MODEL_DIR, 'workout_model.pkl'))
        print("OK Workout Model Trained & Saved.")

    except Exception as e:
        print(f"ERROR: Error training workout model: {e}")

if __name__ == "__main__":
    train_models()