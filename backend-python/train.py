import pandas as pd
import numpy as np
import joblib
import os
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.tree import DecisionTreeClassifier
from xgboost import XGBClassifier, XGBRegressor
from app.feature_pipeline import FeaturePipeline
from app.nutrition_intelligence import NutritionIntelligenceEngine
from app.multi_output_xgboost_model import MultiOutputXGBoostModel
from app.multitarget_nutrition_model import MultiTargetNutritionModel, create_nutrition_training_pipeline
from app.evaluation_framework import ModelEvaluator

# Define paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, 'data')
MODEL_DIR = os.path.join(BASE_DIR, 'models')

# Create models folder if it doesn't exist
if not os.path.exists(MODEL_DIR):
    os.makedirs(MODEL_DIR)

def train_models():
    print("\n--- Starting Model Training ---")

    # Initialize the feature pipeline
    feature_pipeline = FeaturePipeline()

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

    # --- 2. Train Multi-Output Workout Model ---
    try:
        df_ex = pd.read_csv(os.path.join(DATA_DIR, 'exercises_processed.csv'))

        # Initialize the multi-output model
        multi_output_model = MultiOutputXGBoostModel(random_state=42)

        # Create synthetic training data based on exercise properties
        # This simulates having historical workout data
        n_samples = len(df_ex)
        df_synthetic = multi_output_model._create_synthetic_data(n_samples=n_samples)
        X_synthetic, y_synthetic = multi_output_model._prepare_features(df_synthetic)
        
        # Split data for training and validation
        split_idx = int(0.8 * len(X_synthetic))
        X_train = X_synthetic[:split_idx]
        X_val = X_synthetic[split_idx:]
        y_train = y_synthetic[:split_idx]
        y_val = y_synthetic[split_idx:]
        
        # Train the multi-output model
        results = multi_output_model.train(
            X_train=X_train,
            y_train=y_train,
            X_val=X_val,
            y_val=y_val,
            hyperparameter_tuning=True,
            cv_folds=3
        )
        
        # Save the multi-output model
        model_path = multi_output_model.save_model(
            model_path=os.path.join(MODEL_DIR, 'multi_output_xgboost_model.joblib')
        )
        
        print("OK Multi-Output Workout Model Trained & Saved.")
        print(f"  - Model saved to: {model_path}")
        print(f"  - Training RMSE per target: {results['train_rmse']}")
        if results['validation_rmse']:
            print(f"  - Validation RMSE per target: {results['validation_rmse']}")
        
        # Also save individual models for backward compatibility if needed
        # (keeping the old models for compatibility with existing code)
        X_full = X_synthetic
        y_full = y_synthetic
        
        # Individual XGBoost models for WorkoutEngine (using correct filenames)
        
        # Volume model (uses sets as proxy for volume level)
        volume_model = XGBRegressor(n_estimators=100, max_depth=4, random_state=42)
        volume_model.fit(X_full, y_full[:, 0])  # sets column
        joblib.dump(volume_model, os.path.join(MODEL_DIR, 'xgboost_volume.pkl'))
        print("  - xgboost_volume.pkl")
        
        # Intensity model (uses intensity column)
        intensity_model = XGBRegressor(n_estimators=100, max_depth=4, random_state=42)
        intensity_model.fit(X_full, y_full[:, 4])  # intensity column
        joblib.dump(intensity_model, os.path.join(MODEL_DIR, 'xgboost_intensity.pkl'))
        print("  - xgboost_intensity.pkl")
        
        # Split model (classifier for workout split type)
        split_targets = (X_full.iloc[:, 0] % 4).astype(int).values  # derive split from days_per_week
        split_model = XGBClassifier(n_estimators=100, max_depth=4, random_state=42)
        split_model.fit(X_full, split_targets)
        joblib.dump(split_model, os.path.join(MODEL_DIR, 'xgboost_split.pkl'))
        print("  - xgboost_split.pkl")
        
        # Frequency model (days per week prediction)
        freq_model = XGBRegressor(n_estimators=100, max_depth=4, random_state=42)
        freq_targets = X_full.iloc[:, 0].values  # days_per_week column
        freq_model.fit(X_full, freq_targets)
        joblib.dump(freq_model, os.path.join(MODEL_DIR, 'xgboost_frequency.pkl'))
        print("  - xgboost_frequency.pkl")
        
        # Sets model
        sets_model = XGBRegressor(n_estimators=100, max_depth=4, random_state=42)
        sets_model.fit(X_full, y_full[:, 0])
        joblib.dump(sets_model, os.path.join(MODEL_DIR, 'xgboost_sets.pkl'))
        print("  - xgboost_sets.pkl")
        
        # Reps model (multi-output for reps_low and reps_high)
        reps_model = XGBRegressor(n_estimators=100, max_depth=4, random_state=42)
        reps_targets = (y_full[:, 1] + y_full[:, 2]) / 2  # average reps
        reps_model.fit(X_full, reps_targets)
        joblib.dump(reps_model, os.path.join(MODEL_DIR, 'xgboost_reps.pkl'))
        print("  - xgboost_reps.pkl")
        
        # Rest model
        rest_model = XGBRegressor(n_estimators=100, max_depth=4, random_state=42)
        rest_model.fit(X_full, y_full[:, 3])
        joblib.dump(rest_model, os.path.join(MODEL_DIR, 'xgboost_rest.pkl'))
        print("  - xgboost_rest.pkl")
        
        # Progression model
        progression_targets = 0.5 + (X_full.iloc[:, 2].values / 100)  # derive from consistency
        prog_model = XGBRegressor(n_estimators=100, max_depth=4, random_state=42)
        prog_model.fit(X_full, progression_targets)
        joblib.dump(prog_model, os.path.join(MODEL_DIR, 'xgboost_progression.pkl'))
        print("  - xgboost_progression.pkl")
        
        # Label encoders
        le_exp = LabelEncoder()
        le_exp.fit(['Beginner', 'Intermediate', 'Advanced'])
        joblib.dump(le_exp, os.path.join(MODEL_DIR, 'label_encoder_experience.pkl'))
        print("  - label_encoder_experience.pkl")
        
        print("\nAll XGBoost models trained and saved!")

    except Exception as e:
        print(f"ERROR: Error training multi-output workout model: {e}")
        import traceback
        traceback.print_exc()

    # --- 3. Train Multi-Target Nutrition Model ---
    try:
        print("\n--- Training Multi-Target Nutrition Model ---")
        
        # Initialize the multi-target nutrition model
        multi_target_nutrition_model = MultiTargetNutritionModel(random_state=42)

        # Create synthetic training data for nutrition model
        n_samples = 1500
        np.random.seed(42)
        
        # Generate synthetic user profiles
        data = {
            'age': np.random.randint(18, 65, n_samples),
            'weight': np.random.uniform(50, 120, n_samples),
            'height': np.random.uniform(150, 200, n_samples),
            'gender_encoded': np.random.choice([0, 1], n_samples),  # 0=Female, 1=Male
            'experience_encoded': np.random.choice([0, 1, 2], n_samples),  # 0=Beginner, 1=Intermediate, 2=Advanced
            'goal_encoded': np.random.choice(range(6), n_samples),  # 6 different goals
            'activity_level_encoded': np.random.choice(range(5), n_samples),  # 5 activity levels
            'dietary_preference_encoded': np.random.choice(range(3), n_samples),  # 3 dietary prefs
            'days_per_week': np.random.randint(1, 7, n_samples),
            'workout_history_count': np.random.randint(0, 200, n_samples),
            'streak_count': np.random.randint(0, 30, n_samples),
            'consistency_score': np.random.uniform(0.3, 1.0, n_samples),
            'recovery_score': np.random.uniform(0.3, 1.0, n_samples),
            'equipment_richness': np.random.uniform(0.0, 1.0, n_samples),
            'intensity_capacity': np.random.uniform(0.3, 1.0, n_samples),
            'bmi': np.random.uniform(18, 35, n_samples),
            'age_adjusted_capacity': np.random.uniform(0.3, 1.0, n_samples),
            'sleep_score': np.random.uniform(5, 10, n_samples),
            'hydration_score': np.random.uniform(5, 10, n_samples),
            'stress_level': np.random.uniform(1, 10, n_samples)
        }
        
        df_features = pd.DataFrame(data)
        
        # Calculate BMR and TDEE
        df_features['bmr'] = np.where(
            df_features['gender_encoded'] == 1,  # Male
            10 * df_features['weight'] + 6.25 * df_features['height'] - 5 * df_features['age'] + 5,
            10 * df_features['weight'] + 6.25 * df_features['height'] - 5 * df_features['age'] - 161
        )
        
        # Calculate TDEE based on activity level
        activity_multipliers = [1.2, 1.375, 1.55, 1.725, 1.9]
        df_features['activity_multiplier'] = df_features['activity_level_encoded'].map({i: activity_multipliers[i] for i in range(5)})
        df_features['tdee'] = df_features['bmr'] * df_features['activity_multiplier']
        
        # Adjust TDEE based on goal
        goal_multipliers = [0.85, 0.80, 1.10, 1.05, 1.00, 1.00]
        df_features['goal_multiplier'] = df_features['goal_encoded'].map({i: goal_multipliers[i] for i in range(6)})
        df_features['daily_calorie_target'] = df_features['tdee'] * df_features['goal_multiplier']
        
        # Generate target values based on features
        targets = []
        for idx, row in df_features.iterrows():
            # Meal distribution
            breakfast_cal = row['daily_calorie_target'] * 0.25 + np.random.normal(0, 30)
            lunch_cal = row['daily_calorie_target'] * 0.35 + np.random.normal(0, 40)
            dinner_cal = row['daily_calorie_target'] * 0.30 + np.random.normal(0, 40)
            snack_cal = row['daily_calorie_target'] * 0.10 + np.random.normal(0, 20)
            
            # Ensure meal calories are positive and within reasonable bounds
            breakfast_cal = max(200, min(600, breakfast_cal))
            lunch_cal = max(300, min(800, lunch_cal))
            dinner_cal = max(300, min(700, dinner_cal))
            snack_cal = max(100, min(400, snack_cal))
            
            # Calculate total calories
            total_cal = breakfast_cal + lunch_cal + dinner_cal + snack_cal
            
            # Calculate macros based on goal
            goal_idx = int(row['goal_encoded'])
            goal_macros = [
                {'protein': 0.35, 'carbs': 0.35, 'fat': 0.30},  # Weight Loss
                {'protein': 0.40, 'carbs': 0.30, 'fat': 0.30},  # Fat Loss
                {'protein': 0.30, 'carbs': 0.50, 'fat': 0.20},  # Muscle Gain
                {'protein': 0.30, 'carbs': 0.55, 'fat': 0.15},  # Strength
                {'protein': 0.15, 'carbs': 0.70, 'fat': 0.15},  # Endurance
                {'protein': 0.25, 'carbs': 0.50, 'fat': 0.25}   # Maintenance
            ]
            
            protein_cal = total_cal * goal_macros[goal_idx]['protein']
            carbs_cal = total_cal * goal_macros[goal_idx]['carbs']
            fats_cal = total_cal * goal_macros[goal_idx]['fat']
            
            targets.append([
                breakfast_cal,
                lunch_cal,
                dinner_cal,
                snack_cal,
                protein_cal,
                carbs_cal,
                fats_cal
            ])
        
        # Convert to numpy array
        y_targets = np.array(targets)
        
        # Split data for training and validation
        split_idx = int(0.8 * len(df_features))
        X_train = df_features.iloc[:split_idx]
        X_val = df_features.iloc[split_idx:]
        y_train = y_targets[:split_idx]
        y_val = y_targets[split_idx:]
        
        # Train the multi-target nutrition model
        results = multi_target_nutrition_model.train(
            X_train=X_train,
            y_train=y_train,
            X_val=X_val,
            y_val=y_val,
            hyperparameter_tuning=True,
            cv_folds=3
        )
        
        # Save the multi-target nutrition model
        model_path = multi_target_nutrition_model.save_model(
            model_path=os.path.join(MODEL_DIR, 'multitarget_nutrition_model.joblib')
        )
        
        print("OK Multi-Target Nutrition Model Trained & Saved.")
        print(f"  - Model saved to: {model_path}")
        print(f"  - Training MAE per target: {results['train_mae']}")
        if results['validation_mae']:
            print(f"  - Validation MAE per target: {results['validation_mae']}")
        
    except Exception as e:
        print(f"ERROR: Error training multi-target nutrition model: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    train_models()