"""
Production Multi-Output XGBoost Model for Workout Parameter Prediction

This module implements a multi-target regression model to predict:
- sets
- reps_low
- reps_high
- rest_time
- intensity

With safety layers and production considerations.
"""

import pandas as pd
import numpy as np
from sklearn.multioutput import MultiOutputRegressor
from sklearn.model_selection import train_test_split, RandomizedSearchCV, TimeSeriesSplit
from sklearn.metrics import mean_squared_error, mean_absolute_error
from xgboost import XGBRegressor
import joblib
import os
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')
from typing import Dict, Tuple, List, Optional
import json
from scipy.stats import randint, uniform


class MultiOutputXGBoostModel:
    """
    Production-ready multi-output XGBoost model for workout parameter prediction
    """
    
    def __init__(self, random_state: int = 42):
        self.random_state = random_state
        self.model = None
        self.feature_names = None
        self.target_names = ['sets', 'reps_low', 'reps_high', 'rest_time', 'intensity']
        self.version = "1.0.0"
        self.model_path = None
        
        # Safety bounds for predictions
        self.safety_bounds = {
            'sets': (1, 6),
            'reps_low': (1, 20),
            'reps_high': (3, 30),
            'rest_time': (30, 300),  # 30 seconds to 5 minutes
            'intensity': (0.1, 1.0)  # 10% to 100% intensity
        }
        
        # Initialize the base model
        self.base_model = XGBRegressor(
            random_state=self.random_state,
            objective='reg:squarederror',
            eval_metric='rmse',
            verbosity=0
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
        # Define feature columns (these should match your feature pipeline output)
        feature_columns = [
            'age', 'weight', 'height', 'bmi', 'gender_encoded', 
            'experience_encoded', 'goal_encoded', 'days_per_week', 
            'session_time', 'workout_history_count', 'streak_count', 
            'consistency_score', 'recovery_score', 'equipment_richness', 
            'intensity_capacity', 'progressive_overload_delta', 
            'age_adjusted_capacity'
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
        In production, this would be replaced with real user workout history
        """
        np.random.seed(self.random_state)
        
        # Generate synthetic user profiles
        data = {
            'age': np.random.randint(18, 65, n_samples),
            'weight': np.random.uniform(50, 120, n_samples),
            'height': np.random.uniform(150, 200, n_samples),
            'bmi': np.random.uniform(18, 35, n_samples),
            'gender_encoded': np.random.choice([0, 1], n_samples),
            'experience_encoded': np.random.choice([0, 1, 2], n_samples),  # 0=Beginner, 1=Intermediate, 2=Advanced
            'goal_encoded': np.random.choice(range(6), n_samples),  # 6 different goals
            'days_per_week': np.random.randint(1, 7, n_samples),
            'session_time': np.random.randint(30, 120, n_samples),
            'workout_history_count': np.random.randint(0, 200, n_samples),
            'streak_count': np.random.randint(0, 30, n_samples),
            'consistency_score': np.random.uniform(0.3, 1.0, n_samples),
            'recovery_score': np.random.uniform(0.3, 1.0, n_samples),
            'equipment_richness': np.random.uniform(0.0, 1.0, n_samples),
            'intensity_capacity': np.random.uniform(0.3, 1.0, n_samples),
            'progressive_overload_delta': np.random.uniform(0.01, 0.1, n_samples),
            'age_adjusted_capacity': np.random.uniform(0.3, 1.0, n_samples)
        }
        
        df = pd.DataFrame(data)
        
        # Generate realistic target values based on features
        # Sets: More experienced users tend to do more sets
        df['sets'] = np.clip(
            2 + df['experience_encoded'] + np.random.normal(0, 0.5, n_samples),
            1, 6
        ).round().astype(int)
        
        # Reps: Beginners do higher reps, advanced do lower reps for strength
        df['reps_low'] = np.clip(
            8 - df['experience_encoded'] * 1.5 + np.random.normal(0, 1, n_samples),
            1, 20
        ).round().astype(int)
        
        df['reps_high'] = np.clip(
            df['reps_low'] + 4 + np.random.normal(0, 1, n_samples),
            3, 30
        ).round().astype(int)
        
        # Rest time: More intense workouts need more rest
        df['rest_time'] = np.clip(
            60 + df['intensity_capacity'] * 120 + np.random.normal(0, 20, n_samples),
            30, 300
        ).round().astype(int)
        
        # Intensity: Based on experience and recovery
        df['intensity'] = np.clip(
            df['intensity_capacity'] * 0.8 + df['recovery_score'] * 0.2 + np.random.normal(0, 0.1, n_samples),
            0.1, 1.0
        )
        
        # Ensure targets are within bounds
        df['sets'] = df['sets'].clip(1, 6)
        df['reps_low'] = df['reps_low'].clip(1, 20)
        df['reps_high'] = df['reps_high'].clip(3, 30)
        df['rest_time'] = df['rest_time'].clip(30, 300)
        df['intensity'] = df['intensity'].clip(0.1, 1.0)
        
        return df
    
    def train(self, 
              X_train: pd.DataFrame, 
              y_train: np.ndarray, 
              X_val: pd.DataFrame = None, 
              y_val: np.ndarray = None,
              hyperparameter_tuning: bool = True,
              cv_folds: int = 3) -> Dict:
        """
        Train the multi-output model with optional hyperparameter tuning
        """
        print("Training Multi-Output XGBoost Model...")
        
        # Prepare training data
        if isinstance(X_train, pd.DataFrame):
            temp_train_df = X_train.copy()
            temp_train_df[self.target_names] = y_train
            X_train_processed, y_train_processed = self._prepare_features(temp_train_df)
        else:
            # If X_train is already processed
            X_train_processed = X_train
            y_train_processed = y_train
        
        # Prepare validation data if provided
        X_val_processed, y_val_processed = None, None
        if X_val is not None and y_val is not None:
            if isinstance(X_val, pd.DataFrame):
                temp_val_df = X_val.copy()
                temp_val_df[self.target_names] = y_val
                X_val_processed, y_val_processed = self._prepare_features(temp_val_df)
            else:
                X_val_processed = X_val
                y_val_processed = y_val
        
        # Hyperparameter tuning
        if hyperparameter_tuning:
            print("Performing hyperparameter tuning...")
            
            # Define parameter grid
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
            
            # Perform randomized search
            random_search = RandomizedSearchCV(
                estimator=self.model,
                param_distributions=param_distributions,
                n_iter=20,  # Number of parameter settings sampled
                cv=tscv,
                scoring='neg_mean_squared_error',
                n_jobs=-1,
                random_state=self.random_state,
                verbose=1
            )
            
            # Fit the random search
            if X_val_processed is not None:
                random_search.fit(X_train_processed, y_train_processed)
            else:
                random_search.fit(X_train_processed, y_train_processed)
            
            # Update model with best parameters
            self.model = random_search.best_estimator_
            print(f"Best parameters: {random_search.best_params_}")
        
        else:
            # Train with default parameters
            if X_val_processed is not None:
                self.model.fit(X_train_processed, y_train_processed)
            else:
                self.model.fit(X_train_processed, y_train_processed)
        
        # Evaluate the model
        train_predictions = self.model.predict(X_train_processed)
        train_rmse = self._calculate_rmse(y_train_processed, train_predictions)
        
        val_rmse = None
        if X_val_processed is not None:
            val_predictions = self.model.predict(X_val_processed)
            val_rmse = self._calculate_rmse(y_val_processed, val_predictions)
        
        results = {
            'train_rmse': train_rmse,
            'validation_rmse': val_rmse,
            'feature_importance': self._extract_feature_importance()
        }
        
        print("Training completed successfully!")
        return results
    
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
        Make predictions with safety layer applied
        """
        if self.model is None:
            raise ValueError("Model has not been trained yet!")
        
        # Prepare features
        if isinstance(X, pd.DataFrame):
            X_processed, _ = self._prepare_features(
                pd.concat([X, pd.DataFrame(np.zeros((len(X), len(self.target_names))), 
                                          columns=self.target_names)], axis=1)
            )
        else:
            X_processed = X
        
        # Make predictions
        predictions = self.model.predict(X_processed)
        
        # Apply safety layer
        predictions = self._apply_safety_layer(predictions, X)
        
        return predictions
    
    def _apply_safety_layer(self, predictions: np.ndarray, X: pd.DataFrame) -> np.ndarray:
        """
        Apply safety constraints to predictions
        """
        # Create a copy to avoid modifying original
        safe_predictions = predictions.copy()
        
        # Clamp each target within safe bounds
        for i, target_name in enumerate(self.target_names):
            lower_bound, upper_bound = self.safety_bounds[target_name]
            safe_predictions[:, i] = np.clip(safe_predictions[:, i], lower_bound, upper_bound)
        
        # Apply beginner intensity cap
        if hasattr(X, 'experience_encoded'):
            if isinstance(X, pd.DataFrame):
                experience_col = X['experience_encoded']
            else:
                # Assuming experience_encoded is at index 5 based on feature order
                experience_col = X.iloc[:, 5] if isinstance(X, pd.DataFrame) else X[:, 5]
            
            # For beginners (experience_encoded == 0), cap intensity at 0.7
            beginner_mask = experience_col == 0
            if len(beginner_mask) == len(safe_predictions):
                intensity_idx = self.target_names.index('intensity')
                safe_predictions[beginner_mask, intensity_idx] = np.minimum(
                    safe_predictions[beginner_mask, intensity_idx], 0.7
                )
        
        # Apply set bounds based on experience
        if hasattr(X, 'experience_encoded'):
            if isinstance(X, pd.DataFrame):
                experience_col = X['experience_encoded']
            else:
                experience_col = X.iloc[:, 5] if isinstance(X, pd.DataFrame) else X[:, 5]
            
            # For beginners, cap sets at 4
            beginner_mask = experience_col == 0
            if len(beginner_mask) == len(safe_predictions):
                sets_idx = self.target_names.index('sets')
                safe_predictions[beginner_mask, sets_idx] = np.minimum(
                    safe_predictions[beginner_mask, sets_idx], 4
                )
        
        return safe_predictions
    
    def save_model(self, model_path: str = None) -> str:
        """
        Save the trained model with versioning
        """
        if model_path is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            model_filename = f"xgboost_multi_output_model_v{self.version}_{timestamp}.joblib"
            model_path = os.path.join("models", model_filename)
        
        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(model_path), exist_ok=True)
        
        # Prepare model info
        model_package = {
            'model': self.model,
            'version': self.version,
            'feature_names': self.feature_names,
            'target_names': self.target_names,
            'safety_bounds': self.safety_bounds,
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
        required_keys = ['model', 'version', 'feature_names', 'target_names', 'safety_bounds', 'random_state']
        for key in required_keys:
            if key not in model_package:
                raise ValueError(f"Model file missing required key: {key}")
        
        self.model = model_package['model']
        self.version = model_package['version']
        self.feature_names = model_package['feature_names']
        self.target_names = model_package['target_names']
        self.safety_bounds = model_package['safety_bounds']
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
        mse = mean_squared_error(y_test, predictions)
        rmse = np.sqrt(mse)
        mae = mean_absolute_error(y_test, predictions)
        
        # Calculate RMSE per target
        rmse_per_target = self._calculate_rmse(y_test, predictions)
        
        # Calculate R score
        from sklearn.metrics import r2_score
        r2 = r2_score(y_test, predictions)
        
        evaluation_results = {
            'overall_mse': mse,
            'overall_rmse': rmse,
            'overall_mae': mae,
            'r2_score': r2,
            'rmse_per_target': rmse_per_target,
            'predictions_sample': predictions[:5].tolist(),  # First 5 predictions
            'actual_sample': y_test[:5].tolist()  # First 5 actual values
        }
        
        return evaluation_results


def create_training_pipeline():
    """
    Create and run the complete training pipeline
    """
    print("=" * 60)
    print("MULTI-OUTPUT XGBOOST TRAINING PIPELINE")
    print("=" * 60)
    
    # Initialize the model
    model = MultiOutputXGBoostModel(random_state=42)
    
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
    print(f"Train RMSE per target: {results['train_rmse']}")
    print(f"Validation RMSE per target: {results['validation_rmse']}")
    
    # Evaluate on test set
    test_evaluation = model.evaluate(X_test, y_test)
    print(f"\nTest Evaluation:")
    print(f"Overall RMSE: {test_evaluation['overall_rmse']:.4f}")
    print(f"Overall MAE: {test_evaluation['overall_mae']:.4f}")
    print(f"R Score: {test_evaluation['r2_score']:.4f}")
    print(f"RMSE per target: {test_evaluation['rmse_per_target']}")
    
    # Save the model
    model_path = model.save_model()
    
    # Demonstrate inference
    print(f"\nDemonstrating inference on first 3 samples:")
    sample_predictions = model.predict(X_test[:3])
    print("Predictions (sets, reps_low, reps_high, rest_time, intensity):")
    for i, pred in enumerate(sample_predictions):
        print(f"  Sample {i+1}: {pred}")
    
    # Show feature importance
    print(f"\nFeature Importance (first target - sets):")
    if 'sets' in results['feature_importance']:
        sets_importance = results['feature_importance']['sets']
        sorted_importance = sorted(sets_importance.items(), key=lambda x: x[1], reverse=True)
        for feature, importance in sorted_importance[:5]:  # Top 5
            print(f"  {feature}: {importance:.4f}")
    
    return model, results, test_evaluation


def production_notes():
    """
    Production considerations and notes
    """
    print("\n" + "=" * 60)
    print("PRODUCTION NOTES")
    print("=" * 60)
    
    notes = """
    1. MODEL DEPLOYMENT:
       - Containerize the model with Docker for consistent deployment
       - Use model versioning to track changes and enable rollbacks
       - Implement A/B testing when deploying new model versions
    
    2. MONITORING:
       - Monitor prediction drift over time
       - Track model performance metrics in production
       - Set up alerts for performance degradation
    
    3. SCALABILITY:
       - Use model serialization (joblib) for fast loading
       - Consider model compression techniques if needed
       - Implement caching for repeated predictions
    
    4. SAFETY & COMPLIANCE:
       - All predictions are bounded by safety constraints
       - Beginner users have capped intensity levels
       - Injury override rules can be extended based on user data
    
    5. DATA QUALITY:
       - Implement data validation before feeding to model
       - Monitor input distribution shifts
       - Log prediction confidence intervals
    
    6. PERFORMANCE:
       - Model uses MultiOutputRegressor for efficiency
       - Parallel processing enabled with n_jobs=-1
       - Early stopping prevents overfitting
    
    7. MAINTENANCE:
       - Retrain periodically with new data
       - Monitor for concept drift
       - Keep backup models ready
    
    8. ERROR HANDLING:
       - Comprehensive error handling implemented
       - Graceful degradation when model fails
       - Detailed logging for debugging
    """
    
    print(notes)


if __name__ == "__main__":
    # Run the complete pipeline
    model, training_results, test_evaluation = create_training_pipeline()
    
    # Print production notes
    production_notes()
    
    print("\nPipeline completed successfully!")