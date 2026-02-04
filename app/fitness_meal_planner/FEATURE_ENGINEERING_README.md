# Feature Engineering for Fitness-Related ML Models

## Overview
This module creates interpretable and justifiable features for fitness-related ML models. The feature engineering pipeline follows strict ethical guidelines and only includes allowed features while excluding any medical inference or injury prediction features.

## Allowed Features

### 1. Normalized Demographics
- **Age**: Normalized to 0-1 range (18-100 years)
- **Weight**: Normalized to 0-1 range (30-150 kg)
- **Height**: Normalized to 0-1 range (120-220 cm)

### 2. Encoded Categorical Variables
- **Gender**: Label encoded (male, female, non-binary, etc.)
- **Fitness Goal**: Label encoded (strength, fat_loss, muscle_gain, etc.)
- **Experience Level**: Label encoded (beginner, intermediate, advanced)
- **Dietary Preference**: Label encoded (balanced, vegetarian, vegan, etc.)

### 3. Equipment Availability Vectors
- Binary indicators for each equipment type:
  - `has_equipment_none`
  - `has_equipment_dumbbells`
  - `has_equipment_yoga_mat`
  - `has_equipment_resistance_bands`
  - `has_equipment_kettlebell`
  - And others based on dataset

### 4. Dietary Preference Encoding
- Categorical encoding of dietary preferences
- Influences meal plan recommendations

### 5. Workout History Summaries
- `num_workouts_completed`: Total workouts in history
- `avg_exercise_rating`: Average rating from exercise history

### 6. Meal Adherence History
- `num_meals_recorded`: Total meals in history
- `avg_meal_rating`: Average rating from meal history

### 7. Interaction Features
- **Experience × Goal**: Combined effect of experience and goal
- **Weight × Goal**: Combined effect of weight and fitness goal
- **Age × Experience**: Combined effect of age and experience level

## Strictly Excluded Features

### ❌ Medical Inference Features
- No biomarker predictions
- No health metric estimations
- No physiological parameter inferences

### ❌ Injury Prediction Features
- No injury risk assessments
- No anatomical stress indicators
- No biomechanical risk factors

### ❌ Hormonal/Metabolic Assumptions
- No hormone level predictions
- No metabolic rate assumptions
- No endocrine function inferences

## Feature Engineering Pipeline

### 1. Preprocessing Steps
1. **Normalization**: Numerical features scaled to 0-1 range
2. **Label Encoding**: Categorical variables converted to numeric codes
3. **Binary Vector Creation**: Equipment/allergies converted to binary indicators
4. **Interaction Creation**: Allowed interaction features computed
5. **History Summarization**: Behavioral patterns extracted from history

### 2. Output Format
- **Shape**: (n_samples, n_features) numpy array
- **Scaling**: Standardized with zero mean and unit variance
- **Interpretability**: Each feature has a clear meaning and purpose

## Implementation Details

### Feature Names
The pipeline generates interpretable feature names:
- `gender_encoded`: Encoded gender value
- `fitness_goal_encoded`: Encoded fitness goal
- `age_normalized`: Age normalized to 0-1 range
- `has_equipment_dumbbells`: Binary indicator for dumbbell availability
- `exp_goal_interaction_encoded`: Combined experience-goal interaction
- `num_workouts_completed`: Count of completed workouts

### Validation
Each feature is validated to ensure:
- ✅ Interpretable and justifiable
- ✅ No medical inference
- ✅ No injury prediction
- ✅ No hormonal/metabolic assumptions
- ✅ Proper normalization/encoding

## Usage Example

```python
from feature_engineering import FeatureEngineeringPipeline
import pandas as pd

# Initialize pipeline
fe_pipeline = FeatureEngineeringPipeline()

# Fit and transform data
X_features, feature_names = fe_pipeline.fit_transform(df)

# Use features for ML model training
model.fit(X_features, y_target)
```

## Compliance Verification

The feature engineering pipeline has been verified to comply with all requirements:
- ✅ All features are interpretable and justifiable
- ✅ No medical inference features included
- ✅ No injury prediction features included
- ✅ No hormonal or metabolic assumptions
- ✅ All allowed features properly implemented
- ✅ Proper data preprocessing and scaling

## Integration
This module integrates seamlessly with the existing fitness and meal planner system, enhancing the ML components while maintaining ethical standards and safety requirements.