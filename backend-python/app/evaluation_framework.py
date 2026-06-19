"""
Reusable Evaluation Framework for Workout and Nutrition Models

This module provides a comprehensive evaluation framework for ML models
with metrics, safety checks, drift detection, and A/B testing capabilities.
"""

import pandas as pd
import numpy as np
from sklearn.metrics import mean_squared_error, mean_absolute_error, precision_score, recall_score
from sklearn.ensemble import RandomForestRegressor
from xgboost import XGBRegressor
from sklearn.model_selection import cross_val_score
import matplotlib.pyplot as plt
import seaborn as sns
import warnings
warnings.filterwarnings('ignore')
from typing import Dict, List, Tuple, Callable, Optional, Union
import json
import logging
from datetime import datetime
import joblib
import os
from scipy import stats
from sklearn.preprocessing import StandardScaler
import pickle


class ModelEvaluator:
    """
    Reusable evaluation framework for ML models
    """
    
    def __init__(self, model_name: str, model_type: str = "regression"):
        self.model_name = model_name
        self.model_type = model_type  # "regression" or "classification"
        self.results = {}
        self.feature_importance_history = []
        self.drift_threshold = 0.1  # Threshold for drift detection
        
        # Setup logging
        self.logger = self._setup_logging()
        
        # Initialize metrics
        self.metrics = {
            'rmse': self._rmse,
            'mae': self._mae,
            'precision': self._precision,
            'recall': self._recall,
            'safety_compliance': self._safety_compliance
        }
    
    def _setup_logging(self) -> logging.Logger:
        """
        Setup logging for the evaluator
        """
        logger = logging.getLogger(f"ModelEvaluator_{self.model_name}")
        logger.setLevel(logging.INFO)
        
        # Create formatter
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        
        # Console handler
        ch = logging.StreamHandler()
        ch.setFormatter(formatter)
        logger.addHandler(ch)
        
        # File handler
        log_dir = "logs"
        os.makedirs(log_dir, exist_ok=True)
        fh = logging.FileHandler(f"{log_dir}/{self.model_name}_evaluation.log")
        fh.setFormatter(formatter)
        logger.addHandler(fh)
        
        return logger
    
    def _rmse(self, y_true: np.ndarray, y_pred: np.ndarray) -> float:
        """Root Mean Square Error"""
        return np.sqrt(mean_squared_error(y_true, y_pred))
    
    def _mae(self, y_true: np.ndarray, y_pred: np.ndarray) -> float:
        """Mean Absolute Error"""
        return mean_absolute_error(y_true, y_pred)
    
    def _precision(self, y_true: np.ndarray, y_pred: np.ndarray) -> float:
        """Precision score"""
        return precision_score(y_true, y_pred, average='weighted', zero_division=0)
    
    def _recall(self, y_true: np.ndarray, y_pred: np.ndarray) -> float:
        """Recall score"""
        return recall_score(y_true, y_pred, average='weighted', zero_division=0)
    
    def _safety_compliance(self, y_true: np.ndarray, y_pred: np.ndarray, safety_bounds: Dict = None) -> float:
        """
        Calculate safety compliance percentage
        """
        if safety_bounds is None:
            # Default safety bounds for nutrition/workout models
            safety_bounds = {
                'min': 0.1,  # Minimum 10% of target
                'max': 1.5   # Maximum 150% of target
            }
        
        # Calculate how many predictions are within bounds
        lower_bound = y_true * safety_bounds['min']
        upper_bound = y_true * safety_bounds['max']
        
        within_bounds = ((y_pred >= lower_bound) & (y_pred <= upper_bound)).sum()
        total = len(y_pred)
        
        return (within_bounds / total) * 100 if total > 0 else 0.0
    
    def evaluate_model(self, 
                     model, 
                     X_test: pd.DataFrame, 
                     y_test: np.ndarray, 
                     safety_bounds: Dict = None,
                     feature_names: List[str] = None) -> Dict:
        """
        Comprehensive model evaluation
        """
        self.logger.info(f"Evaluating model: {self.model_name}")
        
        # Make predictions
        y_pred = model.predict(X_test)
        
        # Calculate metrics
        evaluation_results = {}
        for metric_name, metric_func in self.metrics.items():
            if metric_name == 'safety_compliance':
                evaluation_results[metric_name] = metric_func(y_test, y_pred, safety_bounds)
            else:
                evaluation_results[metric_name] = metric_func(y_test, y_pred)
        
        # Feature importance (if available)
        if hasattr(model, 'feature_importances_') and feature_names is not None:
            feature_importance = dict(zip(feature_names, model.feature_importances_))
            evaluation_results['feature_importance'] = feature_importance
            self.feature_importance_history.append({
                'timestamp': datetime.now(),
                'feature_importance': feature_importance
            })
        
        # Store results
        self.results = evaluation_results
        
        self.logger.info(f"Evaluation completed for {self.model_name}")
        return evaluation_results
    
    def detect_drift(self, X_current: pd.DataFrame, X_reference: pd.DataFrame, threshold: float = None) -> Dict:
        """
        Detect data drift between current and reference datasets
        """
        if threshold is None:
            threshold = self.drift_threshold
        
        drift_results = {}
        
        # Compare statistical properties of features
        for col in X_current.columns:
            if col in X_reference.columns:
                # Perform Kolmogorov-Smirnov test for distribution similarity
                statistic, p_value = stats.ks_2samp(X_reference[col], X_current[col])
                
                drift_detected = p_value < 0.05  # Significant difference
                drift_severity = 1 - p_value if p_value < 0.05 else 0
                
                drift_results[col] = {
                    'drift_detected': drift_detected,
                    'drift_severity': drift_severity,
                    'p_value': p_value,
                    'statistic': statistic
                }
        
        # Overall drift assessment
        total_features = len(drift_results)
        drifted_features = sum(1 for v in drift_results.values() if v['drift_detected'])
        drift_percentage = (drifted_features / total_features) * 100 if total_features > 0 else 0
        
        overall_drift = drift_percentage > (threshold * 100)
        
        drift_summary = {
            'overall_drift': overall_drift,
            'drift_percentage': drift_percentage,
            'drifted_features_count': drifted_features,
            'total_features': total_features,
            'details': drift_results
        }
        
        self.logger.info(f"Drift detection completed. Overall drift: {overall_drift}, {drift_percentage:.2f}% of features drifted")
        return drift_summary
    
    def compare_models(self, 
                      X_train: pd.DataFrame, 
                      y_train: np.ndarray, 
                      X_test: pd.DataFrame, 
                      y_test: np.ndarray,
                      feature_names: List[str] = None) -> Dict:
        """
        Compare XGBoost vs Random Forest models
        """
        self.logger.info("Comparing XGBoost vs Random Forest models")
        
        # Initialize models
        xgb_model = XGBRegressor(random_state=42, n_estimators=100)
        rf_model = RandomForestRegressor(random_state=42, n_estimators=100)
        
        # Train models
        xgb_model.fit(X_train, y_train)
        rf_model.fit(X_train, y_train)
        
        # Evaluate models
        xgb_results = self.evaluate_model(xgb_model, X_test, y_test, feature_names=feature_names)
        rf_results = self.evaluate_model(rf_model, X_test, y_test, feature_names=feature_names)
        
        # Cross-validation comparison
        xgb_cv_scores = cross_val_score(xgb_model, X_train, y_train, cv=5, scoring='neg_mean_squared_error')
        rf_cv_scores = cross_val_score(rf_model, X_train, y_train, cv=5, scoring='neg_mean_squared_error')
        
        comparison_results = {
            'xgboost': {
                'model': xgb_model,
                'evaluation': xgb_results,
                'cv_scores': xgb_cv_scores,
                'cv_mean': xgb_cv_scores.mean(),
                'cv_std': xgb_cv_scores.std()
            },
            'random_forest': {
                'model': rf_model,
                'evaluation': rf_results,
                'cv_scores': rf_cv_scores,
                'cv_mean': rf_cv_scores.mean(),
                'cv_std': rf_cv_scores.std()
            },
            'winner': 'xgboost' if xgb_results['rmse'] < rf_results['rmse'] else 'random_forest'
        }
        
        self.logger.info(f"Model comparison completed. Winner: {comparison_results['winner']}")
        return comparison_results
    
    def plot_feature_importance(self, feature_importance: Dict, top_n: int = 10) -> plt.Figure:
        """
        Plot feature importance
        """
        # Sort features by importance
        sorted_features = sorted(feature_importance.items(), key=lambda x: x[1], reverse=True)[:top_n]
        features, importances = zip(*sorted_features)
        
        fig, ax = plt.subplots(figsize=(10, 6))
        ax.barh(range(len(features)), importances)
        ax.set_yticks(range(len(features)))
        ax.set_yticklabels(features)
        ax.set_xlabel('Importance')
        ax.set_title(f'Top {top_n} Feature Importances - {self.model_name}')
        ax.invert_yaxis()
        
        plt.tight_layout()
        return fig
    
    def plot_predictions_vs_actual(self, y_true: np.ndarray, y_pred: np.ndarray) -> plt.Figure:
        """
        Plot predictions vs actual values
        """
        fig, ax = plt.subplots(figsize=(10, 6))
        ax.scatter(y_true, y_pred, alpha=0.6)
        ax.plot([y_true.min(), y_true.max()], [y_true.min(), y_true.max()], 'r--', lw=2)
        ax.set_xlabel('Actual Values')
        ax.set_ylabel('Predicted Values')
        ax.set_title(f'Predictions vs Actual - {self.model_name}')
        
        plt.tight_layout()
        return fig
    
    def generate_report(self, results: Dict, model_comparison: Dict = None) -> str:
        """
        Generate evaluation report
        """
        report = f"""
        Model Evaluation Report
        ======================
        Model Name: {self.model_name}
        Evaluation Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
        
        Metrics:
        --------
        RMSE: {results.get('rmse', 'N/A'):.4f}
        MAE: {results.get('mae', 'N/A'):.4f}
        Safety Compliance: {results.get('safety_compliance', 'N/A'):.2f}%
        """
        
        if model_comparison:
            winner = model_comparison['winner']
            xgb_rmse = model_comparison['xgboost']['evaluation']['rmse']
            rf_rmse = model_comparison['random_forest']['evaluation']['rmse']
            
            report += f"""
        Model Comparison:
        -----------------
        XGBoost RMSE: {xgb_rmse:.4f}
        Random Forest RMSE: {rf_rmse:.4f}
        Winner: {winner}
        """
        
        return report


class ABTestFramework:
    """
    A/B Testing framework for model comparison
    """
    
    def __init__(self, control_model, treatment_model, test_name: str = "A/B Test"):
        self.control_model = control_model
        self.treatment_model = treatment_model
        self.test_name = test_name
        self.results = {}
        
        # Setup logging
        self.logger = self._setup_logging()
    
    def _setup_logging(self) -> logging.Logger:
        """
        Setup logging for A/B testing
        """
        logger = logging.getLogger(f"ABTest_{self.test_name}")
        logger.setLevel(logging.INFO)
        
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        
        ch = logging.StreamHandler()
        ch.setFormatter(formatter)
        logger.addHandler(ch)
        
        log_dir = "logs"
        os.makedirs(log_dir, exist_ok=True)
        fh = logging.FileHandler(f"{log_dir}/{self.test_name}_ab_test.log")
        fh.setFormatter(formatter)
        logger.addHandler(fh)
        
        return logger
    
    def run_ab_test(self, 
                   X_test: pd.DataFrame, 
                   y_test: np.ndarray,
                   metric_func: Callable = mean_squared_error,
                   significance_level: float = 0.05) -> Dict:
        """
        Run A/B test between control and treatment models
        """
        self.logger.info(f"Running A/B test: {self.test_name}")
        
        # Get predictions from both models
        y_pred_control = self.control_model.predict(X_test)
        y_pred_treatment = self.treatment_model.predict(X_test)
        
        # Calculate metrics for both models
        metric_control = metric_func(y_test, y_pred_control)
        metric_treatment = metric_func(y_test, y_pred_treatment)
        
        # Perform statistical test (paired t-test)
        differences = (y_test - y_pred_control) - (y_test - y_pred_treatment)
        t_stat, p_value = stats.ttest_rel((y_test - y_pred_control)**2, (y_test - y_pred_treatment)**2)
        
        # Determine significance
        is_significant = p_value < significance_level
        
        ab_results = {
            'control_model_metric': metric_control,
            'treatment_model_metric': metric_treatment,
            'improvement': metric_control - metric_treatment,  # Positive means treatment is better
            't_statistic': t_stat,
            'p_value': p_value,
            'is_significant': is_significant,
            'significance_level': significance_level,
            'winner': 'treatment' if metric_treatment < metric_control else 'control'
        }
        
        self.results = ab_results
        self.logger.info(f"A/B test completed. Winner: {ab_results['winner']}, Significant: {is_significant}")
        
        return ab_results


def create_evaluation_folder_structure():
    """
    Create the recommended folder structure for the evaluation framework
    """
    folders = [
        "evaluation_framework",
        "evaluation_framework/models",
        "evaluation_framework/data",
        "evaluation_framework/results",
        "evaluation_framework/logs",
        "evaluation_framework/plots",
        "evaluation_framework/configs"
    ]
    
    for folder in folders:
        os.makedirs(folder, exist_ok=True)
    
    print("Folder structure created successfully!")


def example_execution_flow():
    """
    Example execution flow demonstrating the evaluation framework
    """
    print("=" * 60)
    print("REUSABLE EVALUATION FRAMEWORK - EXAMPLE EXECUTION")
    print("=" * 60)
    
    # Create sample data
    np.random.seed(42)
    n_samples = 1000
    
    # Simulated workout data
    X_workout = pd.DataFrame({
        'age': np.random.randint(18, 65, n_samples),
        'weight': np.random.uniform(50, 120, n_samples),
        'height': np.random.uniform(150, 200, n_samples),
        'experience_encoded': np.random.choice([0, 1, 2], n_samples),
        'goal_encoded': np.random.choice(range(6), n_samples),
        'days_per_week': np.random.randint(1, 7, n_samples),
        'consistency_score': np.random.uniform(0.3, 1.0, n_samples),
        'recovery_score': np.random.uniform(0.3, 1.0, n_samples)
    })
    
    # Simulated targets (sets, reps, rest_time, intensity)
    y_workout = np.column_stack([
        np.random.randint(1, 6, n_samples),           # sets
        np.random.randint(6, 15, n_samples),         # reps_low
        np.random.randint(10, 20, n_samples),        # reps_high
        np.random.randint(30, 180, n_samples),       # rest_time
        np.random.uniform(0.1, 1.0, n_samples)       # intensity
    ])
    
    # Split data
    split_idx = int(0.8 * n_samples)
    X_train, X_test = X_workout[:split_idx], X_workout[split_idx:]
    y_train, y_test = y_workout[:split_idx], y_workout[split_idx:]
    
    print(f"Created sample data: {X_train.shape[0]} training, {X_test.shape[0]} testing samples")
    
    # Initialize evaluator
    evaluator = ModelEvaluator(model_name="Workout_Prediction_Model", model_type="regression")
    
    # Train a sample model
    from sklearn.multioutput import MultiOutputRegressor
    model = MultiOutputRegressor(XGBRegressor(random_state=42, n_estimators=50))
    model.fit(X_train, y_train[:, 0])  # Just using first target for demo
    
    # Evaluate the model
    print("\n1. Evaluating model...")
    safety_bounds = {'min': 0.8, 'max': 1.2}  # Within 20% of target
    results = evaluator.evaluate_model(
        model=model,
        X_test=X_test,
        y_test=y_test[:, 0],  # Just first target
        safety_bounds=safety_bounds,
        feature_names=X_train.columns.tolist()
    )
    
    print(f"   RMSE: {results['rmse']:.4f}")
    print(f"   MAE: {results['mae']:.4f}")
    print(f"   Safety Compliance: {results['safety_compliance']:.2f}%")
    
    # Compare models
    print("\n2. Comparing XGBoost vs Random Forest...")
    comparison_results = evaluator.compare_models(
        X_train=X_train,
        y_train=y_train[:, 0],
        X_test=X_test,
        y_test=y_test[:, 0],
        feature_names=X_train.columns.tolist()
    )
    
    print(f"   XGBoost RMSE: {comparison_results['xgboost']['evaluation']['rmse']:.4f}")
    print(f"   Random Forest RMSE: {comparison_results['random_forest']['evaluation']['rmse']:.4f}")
    print(f"   Winner: {comparison_results['winner']}")
    
    # Detect drift
    print("\n3. Detecting data drift...")
    # Create slightly different reference data
    X_reference = X_train.sample(n=min(200, len(X_train)), random_state=42)
    drift_results = evaluator.detect_drift(X_current=X_test, X_reference=X_reference)
    
    print(f"   Overall drift detected: {drift_results['overall_drift']}")
    print(f"   Percentage of drifted features: {drift_results['drift_percentage']:.2f}%")
    
    # A/B Testing example
    print("\n4. Running A/B test...")
    control_model = MultiOutputRegressor(RandomForestRegressor(random_state=42, n_estimators=50))
    treatment_model = MultiOutputRegressor(XGBRegressor(random_state=42, n_estimators=50))
    
    control_model.fit(X_train, y_train[:, 0])
    treatment_model.fit(X_train, y_train[:, 0])
    
    ab_test = ABTestFramework(control_model, treatment_model, "Workout_Model_A_B_Test")
    ab_results = ab_test.run_ab_test(X_test, y_test[:, 0])
    
    print(f"   Control model RMSE: {ab_results['control_model_metric']:.4f}")
    print(f"   Treatment model RMSE: {ab_results['treatment_model_metric']:.4f}")
    print(f"   Winner: {ab_results['winner']}")
    print(f"   Statistically significant: {ab_results['is_significant']}")
    
    # Generate report
    print("\n5. Generating evaluation report...")
    report = evaluator.generate_report(results, comparison_results)
    print(report)
    
    # Save results
    results_path = "evaluation_framework/results/workout_model_evaluation.json"
    os.makedirs(os.path.dirname(results_path), exist_ok=True)
    
    with open(results_path, 'w') as f:
        json.dump({
            'evaluation_results': results,
            'comparison_results': comparison_results,
            'drift_results': drift_results,
            'ab_test_results': ab_results,
            'timestamp': datetime.now().isoformat()
        }, f, indent=2, default=str)
    
    print(f"\nResults saved to: {results_path}")
    
    print("\n" + "=" * 60)
    print("EXAMPLE EXECUTION COMPLETED SUCCESSFULLY!")
    print("=" * 60)


if __name__ == "__main__":
    # Create folder structure
    create_evaluation_folder_structure()
    
    # Run example execution
    example_execution_flow()