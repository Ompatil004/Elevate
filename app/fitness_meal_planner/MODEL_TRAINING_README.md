# Model Training for Fitness System ML Models

## Overview
This module trains the permitted ML models for the fitness system using only explainable algorithms. The training process follows strict requirements to ensure models are interpretable and safe.

## Permitted Models Trained

### 1. Workout Difficulty Adjustment Model
- **Algorithm**: Random Forest Classifier
- **Purpose**: Adjusts workout difficulty based on user feedback
- **Input**: User profile + recent workout feedback
- **Output**: Difficulty shift indicator (decrease / same / increase)

### 2. Workout Ranking Model
- **Algorithm**: Gradient Boosting Regressor
- **Purpose**: Ranks pre-filtered exercises based on user profile
- **Input**: User profile + historical completion
- **Output**: Ranked list of pre-filtered exercises

### 3. Nutrition Adherence Prediction Model
- **Algorithm**: Random Forest Classifier
- **Purpose**: Predicts probability of meal adherence
- **Input**: User preferences + meal history
- **Output**: Probability of adherence

## Training Requirements Met

### ✅ Explainable Models Only
- Decision Trees
- Random Forests (ensemble of decision trees)
- Shallow Gradient Boosting
- No deep learning, reinforcement learning, or black-box models

### ✅ Proper Validation Process
- Train/validation/test splits (60/20/20)
- Cross-validation with k=5 folds
- Hyperparameter tuning with grid search
- Feature importance analysis
- Overfitting prevention measures

### ✅ Safety and Consistency Focus
- Models learn patterns of consistency and adherence
- No intensity extremes learned
- Conservative hyperparameters to prevent overfitting
- Regularization techniques applied

## Training Process

### 1. Data Preparation
- Standard scaling applied to numerical features
- Proper train/validation/test splits
- Stratified sampling where appropriate

### 2. Model Selection
- Conservative hyperparameters to prevent overfitting
- Shallow trees for interpretability
- Ensemble methods for robustness

### 3. Validation
- Cross-validation scores reported
- Validation and test set performance
- Feature importance rankings
- Overfitting analysis

### 4. Evaluation Metrics
- **Classification tasks**: Accuracy, AUC-ROC
- **Regression tasks**: RMSE, MSE
- **Cross-validation**: Mean and standard deviation

## Key Features

### Model Interpretability
- Feature importance rankings provided
- Shallow tree structures for interpretability
- Clear relationship between inputs and outputs

### Overfitting Prevention
- Conservative model parameters
- Cross-validation for generalization
- Early stopping where applicable
- Regularization techniques

### Safety Compliance
- No exercise generation
- No training volume decisions
- No rest schedule decisions
- No safety constraint bypassing

## Integration Ready
The trained models are ready for integration with the fitness system:
- Models saved with appropriate scalers
- Feature names preserved for interpretation
- Performance metrics validated
- Safety constraints maintained