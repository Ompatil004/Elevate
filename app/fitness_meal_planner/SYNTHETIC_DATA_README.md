# Synthetic Data Generation for Fitness and Meal Planner

## Overview
This system generates synthetic user behavior data to bootstrap ML models for the fitness and meal planner application. The data follows ethical guidelines and represents realistic user patterns without encoding optimal solutions or guaranteed results.

## Data Generated

### 1. Synthetic User Profiles (150 users)
- **Age**: Realistic ranges by experience level
- **Weight/Height**: User-reported values (not measured)
- **Experience Level**: Distributed as 40% beginner, 40% intermediate, 20% advanced
- **Equipment**: Likelihood based on experience level
- **Goals**: Various fitness objectives
- **Dietary Preferences**: Realistic dietary patterns
- **Allergies/Constraints**: Randomly assigned with realistic probabilities

### 2. Workout Behaviors (1,200 records)
- **Completion Status**: Varies by experience level (higher completion for advanced users)
- **Perceived Difficulty**: Matches experience level expectations
- **Fatigue Levels**: Appropriate to experience level
- **User Experience Notes**: Realistic feedback patterns
- **Adherence Patterns**: Reflects typical user behavior

### 3. Meal Behaviors (1,050 records)
- **Adherence Level**: Followed, partial, or skipped based on user characteristics
- **Enjoyment Ratings**: Realistic satisfaction levels
- **Satisfaction Levels**: Appropriate to adherence
- **User Feedback**: Natural language feedback patterns

## Ethical Guidelines Followed

### ✅ Permitted
- Representing typical user responses by experience level
- Modeling realistic behavior patterns
- Bootstrapping ML models with synthetic data
- Indicating difficulty perception patterns
- Showing adherence likelihood patterns
- Representing completion probability patterns

### ❌ Strictly Forbidden (Not Encoded)
- Optimal workout routines
- Guaranteed results or outcomes
- Injury recovery predictions
- Medical diagnostic patterns
- "Perfect" or "optimal" solutions
- Treatment protocols

## Data Characteristics

### Experience-Level Patterns
- **Beginners**: 60% workout completion rate, 50% meal adherence
- **Intermediate**: 80% workout completion rate, 70% meal adherence  
- **Advanced**: 90% workout completion rate, 85% meal adherence

### Behavioral Realism
- Realistic age distributions
- Appropriate equipment ownership by level
- Natural variation in responses
- Common reasons for skipping or partial completion
- Varied user feedback patterns

## File Structure
```
synthetic_data/
├── synthetic_user_profiles.json     # 150 user profiles
├── synthetic_workout_behaviors.json # 1,200 workout records
└── synthetic_meal_behaviors.json    # 1,050 meal records
```

## Usage
The generated data can be used to:
- Bootstrap ML model training
- Test system functionality
- Validate data processing pipelines
- Simulate user behavior patterns
- Evaluate recommendation algorithms

## Important Note
This synthetic data represents **user behavior patterns only**, not medical truths or optimal solutions. It is designed solely for ML model bootstrapping and system testing purposes.

## Validation
- No medical diagnostic patterns encoded
- No guaranteed outcome predictions
- No "optimal" workout or meal plans
- All data reflects user experience, not correctness
- Privacy-safe synthetic identities