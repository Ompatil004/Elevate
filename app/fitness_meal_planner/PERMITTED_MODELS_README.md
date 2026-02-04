# Permitted ML Models for Fitness and Meal Planner

## Overview
This module implements exactly the ML models that are permitted for the fitness and meal planner system. Each model has a specific, constrained function that operates within ethical and safety boundaries.

## Permitted Models

### 1. Workout Difficulty Adjustment Model
**Function**: Adjusts workout difficulty based on user feedback
- **Input**: User profile + recent workout feedback
- **Output**: Difficulty shift indicator (decrease / same / increase)
- **Purpose**: Helps maintain appropriate challenge level based on user experience

#### Features Used:
- User age and experience level
- Time since program start
- Average difficulty ratings from recent sessions
- Completion rates
- Effort scores

### 2. Workout Ranking Model
**Function**: Ranks pre-filtered exercises based on user preferences
- **Input**: User profile + historical completion data
- **Output**: Ranked list of pre-filtered exercises
- **Purpose**: Personalizes exercise selection while respecting safety constraints

#### Features Used:
- User demographics and experience
- Fitness goals
- Exercise category and difficulty
- Historical performance and ratings
- Completion patterns

### 3. Nutrition Adherence Prediction Model
**Function**: Predicts likelihood of meal adherence
- **Input**: User preferences + meal history
- **Output**: Probability of adherence (0.0 to 1.0)
- **Purpose**: Helps recommend meals users are likely to follow

#### Features Used:
- Dietary preferences and restrictions
- Preferred cuisines
- Disliked ingredients
- Meal characteristics (calories, prep time)
- Historical adherence patterns

## Prohibited Functions (NOT Implemented)

### ❌ Exercise Generation
- Models do not create new exercises
- Only rank or adjust existing, pre-filtered exercises

### ❌ Training Volume Decisions
- Models do not decide sets, reps, or volume
- Only adjust difficulty levels within safe parameters

### ❌ Rest Schedule Decisions
- Models do not determine rest days or recovery periods
- These are handled by rule-based systems

### ❌ Safety Constraint Bypassing
- All safety rules remain enforced
- ML models only operate within pre-filtered, safe options

## Implementation Details

### Model Types
- **Workout Difficulty**: Random Forest Classifier
- **Workout Ranking**: Gradient Boosting Regressor
- **Adherence Prediction**: Logistic Regression

### Data Flow
1. User data enters through validated interfaces
2. Features are engineered within ethical boundaries
3. Models make predictions within defined scope
4. Outputs are integrated with rule-based systems

### Safety Guarantees
- All models respect pre-filtered exercise lists
- Safety constraints are never bypassed
- Outputs are validated before application
- User safety remains primary concern

## Integration
These models integrate with the broader system:
- Work with rule-based safety systems
- Enhance user experience within constraints
- Maintain explainability and transparency
- Support ethical data practices

## Validation
Each model has been validated to ensure:
- ✅ Operates within permitted scope
- ✅ Respects safety constraints
- ✅ Uses only allowed features
- ✅ Maintains ethical standards
- ✅ Provides interpretable outputs

## Compliance
This implementation strictly adheres to the specified permissions and prohibitions, ensuring the ML components enhance the system while maintaining safety and ethical standards.