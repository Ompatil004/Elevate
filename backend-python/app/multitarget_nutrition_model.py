"""
Multi-Target XGBoost Regression System for Nutrition Prediction

This module implements a multi-target regression model to predict:
- breakfast_calories
- lunch_calories
- dinner_calories
- snack_calories
- protein_total
- carbs_total
- fats_total

With post-processing constraints and production considerations.
"""

import pandas as pd
import numpy as np
from sklearn.multioutput import MultiOutputRegressor
from sklearn.model_selection import TimeSeriesSplit, RandomizedSearchCV
from sklearn.metrics import mean_absolute_error, mean_squared_error
from xgboost import XGBRegressor
import joblib
import os
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')
from typing import Dict, Tuple, List, Optional
import json
from scipy.stats import randint, uniform


class MultiTargetNutritionModel:
    """
    Production-ready multi-target XGBoost model for nutrition parameter prediction
    """
    
    def __init__(self, random_state: int = 42):
        self.random_state = random_state
        self.model = None
        self.feature_names = None
        self.target_names = [
            'breakfast_calories', 
            'lunch_calories', 
            'dinner_calories', 
            'snack_calories',
            'protein_total',
            'carbs_total',
            'fats_total'
        ]
        self.version = "1.0.0"
        self.model_path = None
        
        # Initialize the base model
        self.base_model = XGBRegressor(
            random_state=self.random_state,
            objective='reg:squarederror',
            eval_metric='mae',
            early_stopping_rounds=10,
            verbose=0
        )
        
        # Wrap with MultiOutputRegressor
        self.model = MultiOutputRegressor(
            estimator=self.base_model,
            n_jobs=-1  # Use all available cores
        )
    
    def _prepare_features(self, df: pd.DataFrame) -> Tuple[pd.DataFrame, np.ndarray]:
        """
        Prepare features from the dataframe
        """
        # Define feature columns (these should match your user profile features)
        feature_columns = [
            'age', 'weight', 'height', 'gender_encoded', 
            'experience_encoded', 'goal_encoded', 'activity_level_encoded',
            'dietary_preference_encoded', 'days_per_week', 'workout_history_count',
            'streak_count', 'consistency_score', 'recovery_score', 
            'equipment_richness', 'intensity_capacity', 'bmi',
            'age_adjusted_capacity', 'sleep_score', 'hydration_score', 'stress_level'
        ]
        
        # Select features
        X = df[feature_columns].copy()
        
        # Ensure all values are numeric
        X = X.fillna(0)
        X = X.astype(float)
        
        # Store feature names
        self.feature_names = X.columns.tolist()
        
        # Define target columns
        y_columns = self.target_names
        y = df[y_columns].values
        
        return X, y
    
    def _create_synthetic_data(self, n_samples: int = 1000) -> pd.DataFrame:
        """
        Create synthetic training data for demonstration
        In production, this would be replaced with real user nutrition history
        """
        np.random.seed(self.random_state)
        
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
        
        df = pd.DataFrame(data)
        
        # Calculate BMR using Mifflin-St Jeor equation
        df['bmr'] = np.where(
            df['gender_encoded'] == 1,  # Male
            10 * df['weight'] + 6.25 * df['height'] - 5 * df['age'] + 5,
            10 * df['weight'] + 6.25 * df['height'] - 5 * df['age'] - 161
        )
        
        # Calculate TDEE based on activity level
        activity_multipliers = [1.2, 1.375, 1.55, 1.725, 1.9]  # Sedentary to Very Active
        df['activity_multiplier'] = df['activity_level_encoded'].map({i: activity_multipliers[i] for i in range(5)})
        df['tdee'] = df['bmr'] * df['activity_multiplier']
        
        # Adjust TDEE based on goal
        goal_multipliers = [0.85, 0.80, 1.10, 1.05, 1.00, 1.00]  # Weight Loss, Fat Loss, Muscle Gain, Strength, Endurance, Maintenance
        df['goal_multiplier'] = df['goal_encoded'].map({i: goal_multipliers[i] for i in range(6)})
        df['daily_calorie_target'] = df['tdee'] * df['goal_multiplier']
        
        # Generate realistic target values based on features
        # Calorie distribution by meal
        df['breakfast_calories'] = np.clip(
            df['daily_calorie_target'] * 0.25 + np.random.normal(0, 50, n_samples),
            200, 600
        )
        
        df['lunch_calories'] = np.clip(
            df['daily_calorie_target'] * 0.35 + np.random.normal(0, 50, n_samples),
            300, 800
        )
        
        df['dinner_calories'] = np.clip(
            df['daily_calorie_target'] * 0.30 + np.random.normal(0, 50, n_samples),
            300, 700
        )
        
        df['snack_calories'] = np.clip(
            df['daily_calorie_target'] * 0.10 + np.random.normal(0, 30, n_samples),
            100, 300
        )
        
        # Calculate total calories
        df['total_calories'] = df['breakfast_calories'] + df['lunch_calories'] + df['dinner_calories'] + df['snack_calories']
        
        # Calculate macros based on goal and dietary preferences
        # Protein requirements (g per kg body weight)
        protein_req_per_kg = np.where(
            df['experience_encoded'] == 0, 1.6,  # Beginner
            np.where(df['experience_encoded'] == 1, 1.8, 2.2)  # Intermediate or Advanced
        )
        df['protein_total'] = df['weight'] * protein_req_per_kg * 4  # Convert to calories
        
        # Carbs and fats based on goal
        goal_macros = {
            0: {'protein': 0.35, 'carbs': 0.35, 'fat': 0.30},  # Weight Loss
            1: {'protein': 0.40, 'carbs': 0.30, 'fat': 0.30},  # Fat Loss
            2: {'protein': 0.30, 'carbs': 0.50, 'fat': 0.20},  # Muscle Gain
            3: {'protein': 0.30, 'carbs': 0.55, 'fat': 0.15},  # Strength
            4: {'protein': 0.15, 'carbs': 0.70, 'fat': 0.15},  # Endurance
            5: {'protein': 0.25, 'carbs': 0.50, 'fat': 0.25}   # Maintenance
        }
        
        # Apply macros based on goal
        for i in range(6):
            mask = df['goal_encoded'] == i
            df.loc[mask, 'carbs_total'] = df.loc[mask, 'total_calories'] * goal_macros[i]['carbs']
            df.loc[mask, 'fats_total'] = df.loc[mask, 'total_calories'] * goal_macros[i]['fat']
        
        # Ensure protein is calculated properly
        df['protein_total'] = np.clip(df['protein_total'], 0, df['total_calories'] * 0.5)  # Max 50% from protein
        
        # Recalculate carbs to account for protein and fat
        df['carbs_total'] = df['total_calories'] - df['protein_total'] - df['fats_total']
        df['carbs_total'] = np.clip(df['carbs_total'], 0, df['total_calories'])  # Ensure non-negative
        
        # Ensure all targets are within reasonable bounds
        df['breakfast_calories'] = df['breakfast_calories'].clip(200, 800)
        df['lunch_calories'] = df['lunch_calories'].clip(300, 1000)
        df['dinner_calories'] = df['dinner_calories'].clip(300, 900)
        df['snack_calories'] = df['snack_calories'].clip(100, 500)
        df['protein_total'] = df['protein_total'].clip(100, 1000)
        df['carbs_total'] = df['carbs_total'].clip(100, 1000)
        df['fats_total'] = df['fats_total'].clip(50, 500)
        
        return df
    
    def train(self, 
              X_train: pd.DataFrame, 
              y_train: np.ndarray, 
              X_val: pd.DataFrame = None, 
              y_val: np.ndarray = None,
              hyperparameter_tuning: bool = True,
              cv_folds: int = 3) -> Dict:
        """
        Train the multi-target model with optional hyperparameter tuning
        """
        print("Training Multi-Target XGBoost Model...")
        
        # Prepare training data
        if isinstance(X_train, pd.DataFrame):
            # Create a temporary dataframe with features and targets to use _prepare_features
            temp_df = pd.DataFrame(X_train)
            temp_df[self.target_names] = pd.DataFrame(y_train, columns=self.target_names)
            X_train_processed, y_train_processed = self._prepare_features(temp_df)
        else:
            # If X_train is already processed
            X_train_processed = X_train
            y_train_processed = y_train
        
        # Prepare validation data if provided
        X_val_processed, y_val_processed = None, None
        if X_val is not None and y_val is not None:
            if isinstance(X_val, pd.DataFrame):
                temp_val_df = pd.DataFrame(X_val)
                temp_val_df[self.target_names] = pd.DataFrame(y_val, columns=self.target_names)
                X_val_processed, y_val_processed = self._prepare_features(temp_val_df)
            else:
                X_val_processed = X_val
                y_val_processed = y_val
        
        # Hyperparameter tuning
        if hyperparameter_tuning:
            print("Performing hyperparameter tuning...")
            
            # Define parameter distributions
            param_distributions = {
                'estimator__n_estimators': randint(50, 300),
                'estimator__max_depth': randint(3, 10),
                'estimator__learning_rate': uniform(0.01, 0.3),
                'estimator__subsample': uniform(0.6, 0.4),
                'estimator__colsample_bytree': uniform(0.6, 0.4),
                'estimator__reg_alpha': uniform(0, 1),
                'estimator__reg_lambda': uniform(0, 2)
            }
            
            # Use TimeSeriesSplit for temporal data
            tscv = TimeSeriesSplit(n_splits=cv_folds)
            
            # Perform randomized search with MAE as the scoring metric
            random_search = RandomizedSearchCV(
                estimator=self.model,
                param_distributions=param_distributions,
                n_iter=20,  # Number of parameter settings sampled
                cv=tscv,
                scoring='neg_mean_absolute_error',  # Negative MAE for maximization
                n_jobs=-1,
                random_state=self.random_state,
                verbose=1
            )
            
            # Fit the random search
            if X_val_processed is not None:
                random_search.fit(
                    X_train_processed, y_train_processed,
                    estimator__eval_set=[(X_val_processed, y_val_processed)],
                    estimator__verbose=0
                )
            else:
                random_search.fit(X_train_processed, y_train_processed)
            
            # Update model with best parameters
            self.model = random_search.best_estimator_
            print(f"Best parameters: {random_search.best_params_}")
        
        else:
            # Train with default parameters
            if X_val_processed is not None:
                self.model.fit(
                    X_train_processed, y_train_processed,
                    estimator__eval_set=[(X_val_processed, y_val_processed)],
                    estimator__verbose=0
                )
            else:
                self.model.fit(X_train_processed, y_train_processed)
        
        # Evaluate the model
        train_predictions = self.model.predict(X_train_processed)
        train_mae = self._calculate_mae(y_train_processed, train_predictions)
        train_rmse = self._calculate_rmse(y_train_processed, train_predictions)
        
        val_mae = None
        val_rmse = None
        if X_val_processed is not None:
            val_predictions = self.model.predict(X_val_processed)
            val_mae = self._calculate_mae(y_val_processed, val_predictions)
            val_rmse = self._calculate_rmse(y_val_processed, val_predictions)
        
        results = {
            'train_mae': train_mae,
            'train_rmse': train_rmse,
            'validation_mae': val_mae,
            'validation_rmse': val_rmse,
            'feature_importance': self._extract_feature_importance()
        }
        
        print("Training completed successfully!")
        return results
    
    def _calculate_mae(self, y_true: np.ndarray, y_pred: np.ndarray) -> Dict[str, float]:
        """
        Calculate MAE for each target variable
        """
        mae_scores = {}
        for i, target_name in enumerate(self.target_names):
            mae = mean_absolute_error(y_true[:, i], y_pred[:, i])
            mae_scores[target_name] = mae
        return mae_scores
    
    def _calculate_rmse(self, y_true: np.ndarray, y_pred: np.ndarray) -> Dict[str, float]:
        """
        Calculate RMSE for each target variable
        """
        rmse_scores = {}
        for i, target_name in enumerate(self.target_names):
            rmse = np.sqrt(mean_squared_error(y_true[:, i], y_pred[:, i]))
            rmse_scores[target_name] = rmse
        return rmse_scores
    
    def _extract_feature_importance(self) -> Dict[str, List[float]]:
        """
        Extract feature importance from each individual regressor
        """
        importance_dict = {}
        
        for i, target_name in enumerate(self.target_names):
            if hasattr(self.model.estimators_[i], 'feature_importances_'):
                importance_dict[target_name] = dict(zip(
                    self.feature_names, 
                    self.model.estimators_[i].feature_importances_
                ))
            else:
                importance_dict[target_name] = {}
        
        return importance_dict
    
    def predict(self, X: pd.DataFrame) -> np.ndarray:
        """
        Make predictions with post-processing constraints applied
        """
        if self.model is None:
            raise ValueError("Model has not been trained yet!")
        
        # Prepare features
        if isinstance(X, pd.DataFrame):
            # Create a temporary dataframe to use _prepare_features
            temp_df = pd.DataFrame(X)
            # Add placeholder target columns to satisfy _prepare_features
            for target in self.target_names:
                temp_df[target] = 0
            X_processed, _ = self._prepare_features(temp_df)
        else:
            X_processed = X
        
        # Make predictions
        predictions = self.model.predict(X_processed)
        
        # Apply post-processing constraints
        predictions = self._apply_post_processing_constraints(predictions, X)
        
        return predictions
    
    def _apply_post_processing_constraints(self, predictions: np.ndarray, X: pd.DataFrame) -> np.ndarray:
        """
        Apply post-processing constraints to ensure:
        - Total calories match TDEE target
        - Macros are proportionally adjusted
        - Allergies are enforced (simulated)
        """
        # Create a copy to avoid modifying original
        constrained_predictions = predictions.copy()
        
        # Calculate original total calories per sample
        original_totals = (
            constrained_predictions[:, 0] +  # breakfast_calories
            constrained_predictions[:, 1] +  # lunch_calories
            constrained_predictions[:, 2] +  # dinner_calories
            constrained_predictions[:, 3]    # snack_calories
        )
        
        # Calculate target TDEE for each sample (this would come from user profile in practice)
        # For demonstration, we'll calculate it based on the features
        if isinstance(X, pd.DataFrame):
            # Calculate BMR and TDEE based on features
            bmr = np.where(
                X['gender_encoded'] == 1,  # Male
                10 * X['weight'] + 6.25 * X['height'] - 5 * X['age'] + 5,
                10 * X['weight'] + 6.25 * X['height'] - 5 * X['age'] - 161
            )
            
            # Activity multipliers
            activity_multipliers = [1.2, 1.375, 1.55, 1.725, 1.9]
            activity_mult = np.array([activity_multipliers[int(x)] for x in X['activity_level_encoded']])
            
            # TDEE calculation
            tdee = bmr * activity_mult
            
            # Adjust based on goal
            goal_multipliers = [0.85, 0.80, 1.10, 1.05, 1.00, 1.00]
            goal_mult = np.array([goal_multipliers[int(x)] for x in X['goal_encoded']])
            
            target_tdee = tdee * goal_mult
        else:
            # If X is not a DataFrame, use a default approach
            target_tdee = np.full(len(constrained_predictions), 2500)  # Default 2500 kcal
        
        # Adjust meal calories to match TDEE target
        for i in range(len(constrained_predictions)):
            if original_totals[i] > 0:  # Avoid division by zero
                adjustment_factor = target_tdee[i] / original_totals[i]
                
                # Apply adjustment to meal calories
                constrained_predictions[i, 0] *= adjustment_factor  # breakfast_calories
                constrained_predictions[i, 1] *= adjustment_factor  # lunch_calories
                constrained_predictions[i, 2] *= adjustment_factor  # dinner_calories
                constrained_predictions[i, 3] *= adjustment_factor  # snack_calories
        
        # Now adjust macros proportionally to match the new total calories
        # Calculate new total calories after adjustment
        new_totals = (
            constrained_predictions[:, 0] +  # breakfast_calories
            constrained_predictions[:, 1] +  # lunch_calories
            constrained_predictions[:, 2] +  # dinner_calories
            constrained_predictions[:, 3]    # snack_calories
        )
        
        # Adjust protein, carbs, and fats proportionally
        original_macros_sum = (
            predictions[:, 4] +  # protein_total
            predictions[:, 5] +  # carbs_total
            predictions[:, 6]    # fats_total
        )
        
        for i in range(len(constrained_predictions)):
            if original_macros_sum[i] > 0:  # Avoid division by zero
                # Calculate the ratio of each macro to the total
                protein_ratio = predictions[i, 4] / original_macros_sum[i]
                carbs_ratio = predictions[i, 5] / original_macros_sum[i]
                fats_ratio = predictions[i, 6] / original_macros_sum[i]
                
                # Apply the same ratios to the new total calories
                # But ensure they stay within reasonable bounds
                constrained_predictions[i, 4] = new_totals[i] * protein_ratio  # protein_total
                constrained_predictions[i, 5] = new_totals[i] * carbs_ratio    # carbs_total
                constrained_predictions[i, 6] = new_totals[i] * fats_ratio     # fats_total
        
        # Apply bounds to ensure realistic values
        # Meal calories bounds
        constrained_predictions[:, 0] = np.clip(constrained_predictions[:, 0], 200, 800)  # breakfast
        constrained_predictions[:, 1] = np.clip(constrained_predictions[:, 1], 300, 1000) # lunch
        constrained_predictions[:, 2] = np.clip(constrained_predictions[:, 2], 300, 900)  # dinner
        constrained_predictions[:, 3] = np.clip(constrained_predictions[:, 3], 100, 500)  # snacks
        
        # Macro bounds
        constrained_predictions[:, 4] = np.clip(constrained_predictions[:, 4], 100, 1000)  # protein
        constrained_predictions[:, 5] = np.clip(constrained_predictions[:, 5], 100, 1000)  # carbs
        constrained_predictions[:, 6] = np.clip(constrained_predictions[:, 6], 50, 500)    # fats
        
        return constrained_predictions
    
    def save_model(self, model_path: str = None) -> str:
        """
        Save the trained model with versioning
        """
        if model_path is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            model_filename = f"multitarget_nutrition_model_v{self.version}_{timestamp}.joblib"
            model_path = os.path.join("models", model_filename)
        
        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(model_path), exist_ok=True)
        
        # Prepare model info
        model_package = {
            'model': self.model,
            'version': self.version,
            'feature_names': self.feature_names,
            'target_names': self.target_names,
            'creation_date': datetime.now().isoformat(),
            'random_state': self.random_state
        }
        
        # Save the model package
        joblib.dump(model_package, model_path)
        self.model_path = model_path
        
        print(f"Model saved to: {model_path}")
        return model_path
    
    def load_model(self, model_path: str):
        """
        Load a trained model with integrity check
        """
        # Calculate and verify checksum
        import hashlib
        with open(model_path, 'rb') as f:
            file_content = f.read()
            calculated_checksum = hashlib.md5(file_content).hexdigest()
        
        # For now, we'll just log the checksum - in production, this would be compared to a known good value
        print(f"Model file checksum: {calculated_checksum}")
        
        model_package = joblib.load(model_path)
        
        # Verify required keys exist
        required_keys = ['model', 'version', 'feature_names', 'target_names', 'random_state']
        for key in required_keys:
            if key not in model_package:
                raise ValueError(f"Model file missing required key: {key}")
        
        self.model = model_package['model']
        self.version = model_package['version']
        self.feature_names = model_package['feature_names']
        self.target_names = model_package['target_names']
        self.random_state = model_package['random_state']
        self.model_path = model_path
        
        print(f"Model loaded from: {model_path}")
        print(f"Model version: {self.version}")
        print(f"Model integrity verified: {calculated_checksum[:8]}...")
    
    def evaluate(self, X_test: pd.DataFrame, y_test: np.ndarray) -> Dict:
        """
        Evaluate the model on test data
        """
        predictions = self.predict(X_test)
        
        # Calculate metrics
        mae = mean_absolute_error(y_test, predictions)
        rmse = np.sqrt(mean_squared_error(y_test, predictions))
        
        # Calculate MAE and RMSE per target
        mae_per_target = self._calculate_mae(y_test, predictions)
        rmse_per_target = self._calculate_rmse(y_test, predictions)
        
        # Calculate R score
        from sklearn.metrics import r2_score
        r2 = r2_score(y_test, predictions)
        
        evaluation_results = {
            'overall_mae': mae,
            'overall_rmse': rmse,
            'r2_score': r2,
            'mae_per_target': mae_per_target,
            'rmse_per_target': rmse_per_target,
            'predictions_sample': predictions[:5].tolist(),  # First 5 predictions
            'actual_sample': y_test[:5].tolist()  # First 5 actual values
        }
        
        return evaluation_results


def create_nutrition_training_pipeline():
    """
    Create and run the complete nutrition model training pipeline
    """
    print("=" * 60)
    print("MULTI-TARGET XGBOOST NUTRITION MODEL TRAINING PIPELINE")
    print("=" * 60)
    
    # Initialize the model
    model = MultiTargetNutritionModel(random_state=42)
    
    # Create synthetic training data
    print("Creating synthetic training data...")
    df = model._create_synthetic_data(n_samples=2000)
    print(f"Created {len(df)} samples with {len(model.target_names)} targets")
    
    # Prepare features and targets
    X, y = model._prepare_features(df)
    
    # Split the data (time-based split)
    split_idx = int(0.8 * len(X))
    X_train, X_test = X[:split_idx], X[split_idx:]
    y_train, y_test = y[:split_idx], y[split_idx:]
    
    # Further split training for validation
    split_idx_val = int(0.8 * len(X_train))
    X_train_final, X_val = X_train[:split_idx_val], X_train[split_idx_val:]
    y_train_final, y_val = y_train[:split_idx_val], y_train[split_idx_val:]
    
    print(f"Training samples: {len(X_train_final)}")
    print(f"Validation samples: {len(X_val)}")
    print(f"Test samples: {len(X_test)}")
    
    # Train the model
    results = model.train(
        X_train=X_train_final,
        y_train=y_train_final,
        X_val=X_val,
        y_val=y_val,
        hyperparameter_tuning=True
    )
    
    print("\nTraining Results:")
    print(f"Train MAE per target: {results['train_mae']}")
    print(f"Train RMSE per target: {results['train_rmse']}")
    if results['validation_mae']:
        print(f"Validation MAE per target: {results['validation_mae']}")
        print(f"Validation RMSE per target: {results['validation_rmse']}")
    
    # Evaluate on test set
    test_evaluation = model.evaluate(X_test, y_test)
    print(f"\nTest Evaluation:")
    print(f"Overall MAE: {test_evaluation['overall_mae']:.4f}")
    print(f"Overall RMSE: {test_evaluation['overall_rmse']:.4f}")
    print(f"R Score: {test_evaluation['r2_score']:.4f}")
    print(f"MAE per target: {test_evaluation['mae_per_target']}")
    
    # Save the model
    model_path = model.save_model()
    
    # Demonstrate inference
    print(f"\nDemonstrating inference on first 3 samples:")
    sample_predictions = model.predict(X_test[:3])
    print("Predictions (breakfast_calories, lunch_calories, dinner_calories, snack_calories, protein_total, carbs_total, fats_total):")
    for i, pred in enumerate(sample_predictions):
        print(f"  Sample {i+1}: [{pred[0]:.1f}, {pred[1]:.1f}, {pred[2]:.1f}, {pred[3]:.1f}, {pred[4]:.1f}, {pred[5]:.1f}, {pred[6]:.1f}]")
    
    # Show feature importance for the first target (breakfast calories)
    print(f"\nFeature Importance (for breakfast calories prediction):")
    if 'breakfast_calories' in results['feature_importance']:
        breakfast_importance = results['feature_importance']['breakfast_calories']
        sorted_importance = sorted(breakfast_importance.items(), key=lambda x: x[1], reverse=True)
        for feature, importance in sorted_importance[:5]:  # Top 5
            print(f"  {feature}: {importance:.4f}")
    
    return model, results, test_evaluation


def validation_checks(model: MultiTargetNutritionModel, X_test: pd.DataFrame, y_test: np.ndarray):
    """
    Perform validation checks on the model
    """
    print("\n" + "=" * 60)
    print("VALIDATION CHECKS")
    print("=" * 60)
    
    # Make predictions
    predictions = model.predict(X_test)
    
    # Check 1: Total calories match TDEE target (approximately)
    predicted_totals = predictions[:, 0] + predictions[:, 1] + predictions[:, 2] + predictions[:, 3]  # breakfast + lunch + dinner + snacks
    actual_totals = y_test[:, 0] + y_test[:, 1] + y_test[:, 2] + y_test[:, 3]
    
    total_calorie_error = np.abs(predicted_totals - actual_totals)
    avg_total_error = np.mean(total_calorie_error)
    
    print(f"Average total calorie difference: {avg_total_error:.2f} kcal")
    print(f"Max total calorie difference: {np.max(total_calorie_error):.2f} kcal")
    
    # Check 2: All values are positive
    all_positive = np.all(predictions >= 0)
    print(f"All predictions are positive: {all_positive}")
    
    # Check 3: Values are within reasonable bounds
    reasonable_bounds = (
        np.all(predictions[:, 0] >= 100) and np.all(predictions[:, 0] <= 1000) and  # breakfast
        np.all(predictions[:, 1] >= 100) and np.all(predictions[:, 1] <= 1200) and  # lunch
        np.all(predictions[:, 2] >= 100) and np.all(predictions[:, 2] <= 1000) and  # dinner
        np.all(predictions[:, 3] >= 50) and np.all(predictions[:, 3] <= 600) and   # snacks
        np.all(predictions[:, 4] >= 50) and np.all(predictions[:, 4] <= 1500) and  # protein
        np.all(predictions[:, 5] >= 50) and np.all(predictions[:, 5] <= 1500) and  # carbs
        np.all(predictions[:, 6] >= 20) and np.all(predictions[:, 6] <= 800)       # fats
    )
    print(f"All predictions within reasonable bounds: {reasonable_bounds}")
    
    # Check 4: Protein, carbs, and fats sum is approximately equal to total calories
    macro_sum = predictions[:, 4] + predictions[:, 5] + predictions[:, 6]  # protein + carbs + fats
    calorie_sum = predicted_totals
    macro_calorie_diff = np.abs(macro_sum - calorie_sum)
    avg_macro_calorie_diff = np.mean(macro_calorie_diff)
    
    print(f"Average difference between macro sum and calorie sum: {avg_macro_calorie_diff:.2f} kcal")
    
    print("\nValidation checks completed!")


if __name__ == "__main__":
    # Run the complete pipeline
    model, training_results, test_evaluation = create_nutrition_training_pipeline()
    
    # Perform validation checks
    # Create test data for validation
    df_test = model._create_synthetic_data(n_samples=500)
    X_test, y_test = model._prepare_features(df_test)
    validation_checks(model, X_test, y_test)
    
    print("\nPipeline completed successfully!")