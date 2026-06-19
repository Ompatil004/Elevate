"""
Complete ML Feature Pipeline for Elevate Fitness Workout Recommendation Engine

This module defines the full feature pipeline from raw user inputs to model-ready features,
with deterministic processing, safety overrides, and progressive overload capabilities.
"""

import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler, LabelEncoder, MultiLabelBinarizer
from sklearn.metrics.pairwise import cosine_similarity
from typing import Dict, List, Tuple, Optional, Union
import json
from datetime import datetime
try:
    from .biometric_normalizer import BiometricNormalizer  # package import
except ImportError:  # Bug #60 fixed: was bare except Exception which masked real errors
    from biometric_normalizer import BiometricNormalizer   # script / direct-run fallback
import warnings
warnings.filterwarnings('ignore')


class FeaturePipeline:
    """
    Complete feature pipeline for workout recommendation engine
    """
    
    def __init__(self):
        # Initialize encoders
        self.experience_encoder = LabelEncoder()
        self.goal_encoder = LabelEncoder()
        self.gender_encoder = LabelEncoder()
        self.equipment_encoder = MultiLabelBinarizer()
        self.injury_encoder = MultiLabelBinarizer()
        
        # Fit encoders with default values
        self._fit_encoders()
        
        # Scaler for numerical features
        self.scaler = StandardScaler()
        
        # Feature names for reference
        self.feature_names = []
        
        # Define target mappings
        self.target_mappings = {
            'exercise_category': ['Chest', 'Back', 'Legs', 'Shoulders', 'Arms', 'Core'],
            'sets': [1, 2, 3, 4, 5, 6],
            'rep_low': [1, 3, 5, 6, 8, 10, 12],
            'rep_high': [5, 8, 10, 12, 15, 20, 25],
            'rest_time': [30, 60, 90, 120, 180, 240],
            'intensity_level': ['Low', 'Moderate', 'High', 'Very High'],
            'workout_split': ['Full Body', 'Upper/Lower', 'Push/Pull/Legs', 'Bro Split', 'PPL']
        }
    
    def _fit_encoders(self):
        """Fit encoders with default values"""
        # Experience levels
        self.experience_encoder.fit(['Beginner', 'Intermediate', 'Advanced'])
        
        # Fitness goals
        self.goal_encoder.fit(['Weight Loss', 'Muscle Gain', 'Maintenance', 'Strength', 'Endurance', 'Athletic Performance'])
        
        # Gender
        self.gender_encoder.fit(['Male', 'Female', 'Other'])
        
        # Equipment (will be fitted when first data comes in)
        # Injury flags (will be fitted when first data comes in)
    
    def validate_input(self, user_profile: Dict) -> Dict:
        """
        Validate and sanitize raw user input
        """
        validated_profile = {}
        
        # Required fields with defaults
        required_fields = {
            'age': 25,
            'weight': 70.0,
            'height': 175.0,
            'gender': 'Male',
            'experience': 'Beginner',
            'goal': 'Muscle Gain',
            'equipment': [],
            'injuries': [],
            'days_per_week': 4,
            'session_time': 60,
            'workout_history_count': 0,
            'streak_count': 0,
            'consistency': 0.7,
            'sleep_score': 7.0,
            'hydration_score': 7.0,
            'stress_level': 5.0
        }
        
        for field, default in required_fields.items():
            if field not in user_profile:
                validated_profile[field] = default
            else:
                validated_profile[field] = user_profile[field]

        # Accept both raw biometric inputs and already-scored inputs.
        raw_sleep = user_profile.get('sleep_hours', validated_profile.get('sleep_score', 7.0))
        raw_hydration = user_profile.get('water_liters', validated_profile.get('hydration_score', 7.0))
        validated_profile['sleep_hours'] = BiometricNormalizer.parse_sleep_hours(raw_sleep)
        validated_profile['water_liters'] = BiometricNormalizer.parse_water_liters(raw_hydration)
        validated_profile['sleep_score'] = BiometricNormalizer.normalize_sleep(raw_sleep)
        validated_profile['hydration_score'] = BiometricNormalizer.normalize_hydration(raw_hydration)
        
        # Validate ranges
        validated_profile['age'] = max(18, min(80, validated_profile['age']))
        validated_profile['weight'] = max(40.0, min(200.0, validated_profile['weight']))
        validated_profile['height'] = max(120.0, min(250.0, validated_profile['height']))
        validated_profile['days_per_week'] = max(1, min(7, validated_profile['days_per_week']))
        validated_profile['session_time'] = max(15, min(180, validated_profile['session_time']))
        validated_profile['consistency'] = max(0.0, min(1.0, validated_profile['consistency']))
        validated_profile['sleep_score'] = max(1.0, min(10.0, validated_profile['sleep_score']))
        validated_profile['hydration_score'] = max(1.0, min(10.0, validated_profile['hydration_score']))
        validated_profile['stress_level'] = max(1.0, min(10.0, validated_profile['stress_level']))
        
        return validated_profile
    
    def calculate_derived_features(self, user_profile: Dict) -> Dict:
        """
        Calculate derived features from raw input
        """
        derived = user_profile.copy()

        # Ensure recovery metrics are normalized even if callers bypass validate_input.
        raw_sleep = derived.get('sleep_hours', derived.get('sleep_score', 7.0))
        raw_hydration = derived.get('water_liters', derived.get('hydration_score', 7.0))
        derived['sleep_score'] = BiometricNormalizer.normalize_sleep(raw_sleep)
        derived['hydration_score'] = BiometricNormalizer.normalize_hydration(raw_hydration)
        
        # BMI calculation
        height_m = derived['height'] / 100  # Convert cm to m
        derived['bmi'] = derived['weight'] / (height_m ** 2)
        
        # Experience score (numerical representation)
        experience_map = {'Beginner': 1, 'Intermediate': 2, 'Advanced': 3}
        derived['experience_score'] = experience_map.get(derived['experience'], 1)
        
        # Recovery score — 4-factor model (sleep, hydration, stress, fatigue)
        fatigue_level = max(1.0, min(10.0, float(derived.get('fatigue_level', 5.0))))
        stress_level = max(1.0, min(10.0, float(derived.get('stress_level', 5.0))))
        recovery_metrics = [
            derived['sleep_score'] / 10.0,
            derived['hydration_score'] / 10.0,
            (10.0 - stress_level) / 10.0,
            (10.0 - fatigue_level) / 10.0,
        ]
        derived['recovery_score'] = float(np.mean(recovery_metrics))
        derived['readiness_score'] = (
            derived['recovery_score'] * 0.6 +
            derived.get('consistency', 0.7) * 0.4
        )
        
        # Consistency score (already normalized)
        derived['consistency_score'] = derived['consistency']
        
        # Equipment richness score (normalized count of equipment)
        derived['equipment_richness'] = min(1.0, len(derived['equipment']) / 10.0)
        
        # Intensity capacity score (combines experience and recovery)
        derived['intensity_capacity'] = (
            derived['experience_score'] * 0.6 + 
            derived['recovery_score'] * 0.4
        )
        
        # ── Progressive overload delta (redesigned multi-factor formula) ──
        #
        # progression_delta = base_rate × adherence × recovery × experience_mod
        #
        # base_rate:       3-7 % depending on experience
        # adherence:       0.6 × completion + 0.4 × streak_factor
        # recovery:        4-factor recovery score (computed above)
        # experience_mod:  Beginner 0.70 | Intermediate 1.00 | Advanced 1.15
        #
        base_rates   = {'Beginner': 0.03, 'Intermediate': 0.05, 'Advanced': 0.07}
        exp_mods     = {'Beginner': 0.70, 'Intermediate': 1.00, 'Advanced': 1.15}
        
        base_rate    = base_rates.get(derived['experience'], 0.05)
        exp_mod      = exp_mods.get(derived['experience'], 1.0)
        
        # Adherence score: blend completion proxy (consistency) with streak
        days_pw       = max(1, derived.get('days_per_week', 4))
        streak_factor = min(derived.get('streak_count', 0) / max(1, 2 * days_pw), 1.0)
        adherence     = 0.60 * derived['consistency_score'] + 0.40 * streak_factor
        
        derived['progressive_overload_delta'] = round(
            max(0.0, min(0.10, base_rate * adherence * derived['recovery_score'] * exp_mod)),
            5
        )
        
        # Age-adjusted capacity (older users may need adjusted intensity)
        age_factor = max(0.7, 1.0 - (derived['age'] - 30) * 0.01)  # Reduce capacity after 30
        derived['age_adjusted_capacity'] = derived['intensity_capacity'] * age_factor
        
        return derived
    
    def encode_features(self, user_profile: Dict) -> np.ndarray:
        """
        Encode categorical and multi-categorical features
        """
        # Encode categorical features
        encoded_profile = user_profile.copy()
        
        # Experience encoding
        try:
            encoded_profile['experience_encoded'] = self.experience_encoder.transform([encoded_profile['experience']])[0]
        except ValueError:
            # If new value, use the most common (Beginner = 0)
            encoded_profile['experience_encoded'] = 0
        
        # Goal encoding
        try:
            encoded_profile['goal_encoded'] = self.goal_encoder.transform([encoded_profile['goal']])[0]
        except ValueError:
            # If new value, use the most common (Muscle Gain = 0)
            encoded_profile['goal_encoded'] = 0
        
        # Gender encoding
        try:
            encoded_profile['gender_encoded'] = self.gender_encoder.transform([encoded_profile['gender']])[0]
        except ValueError:
            # If new value, default to Male = 0
            encoded_profile['gender_encoded'] = 0
        
        # Equipment multi-hot encoding
        try:
            equipment_encoded = self.equipment_encoder.transform([encoded_profile['equipment']])
        except ValueError:
            # If new equipment list, fit and transform
            self.equipment_encoder.fit(encoded_profile['equipment'])
            equipment_encoded = self.equipment_encoder.transform([encoded_profile['equipment']])
        
        # Injury multi-hot encoding
        try:
            injury_encoded = self.injury_encoder.transform([encoded_profile['injuries']])
        except ValueError:
            # If new injury list, fit and transform
            self.injury_encoder.fit(encoded_profile['injuries'])
            injury_encoded = self.injury_encoder.transform([encoded_profile['injuries']])
        
        # Create feature vector
        feature_vector = np.array([
            encoded_profile['age'],
            encoded_profile['weight'],
            encoded_profile['height'],
            encoded_profile['bmi'],
            encoded_profile['gender_encoded'],
            encoded_profile['experience_encoded'],
            encoded_profile['goal_encoded'],
            encoded_profile['days_per_week'],
            encoded_profile['session_time'],
            encoded_profile['workout_history_count'],
            encoded_profile['streak_count'],
            encoded_profile['consistency_score'],
            encoded_profile['recovery_score'],
            encoded_profile['equipment_richness'],
            encoded_profile['intensity_capacity'],
            encoded_profile['progressive_overload_delta'],
            encoded_profile['age_adjusted_capacity']
        ])
        
        # Concatenate with encoded equipment and injury vectors
        feature_vector = np.concatenate([feature_vector, equipment_encoded[0], injury_encoded[0]])
        
        return feature_vector
    
    def scale_features(self, feature_vector: np.ndarray) -> np.ndarray:
        """
        Scale numerical features while preserving categorical encodings
        """
        # Reshape if needed
        if len(feature_vector.shape) == 1:
            feature_vector = feature_vector.reshape(1, -1)
        
        # Fit scaler if not already fitted
        if not hasattr(self.scaler, 'mean_'):
            self.scaler.fit(feature_vector)
        
        # Transform features
        scaled_features = self.scaler.transform(feature_vector)
        
        return scaled_features[0]  # Return as 1D array
    
    def process_user_profile(self, user_profile: Dict) -> np.ndarray:
        """
        Complete feature pipeline: Raw Input  Processed Features
        """
        # Step 1: Validate input
        validated_profile = self.validate_input(user_profile)
        
        # Step 2: Calculate derived features
        derived_profile = self.calculate_derived_features(validated_profile)
        
        # Step 3: Encode features
        encoded_features = self.encode_features(derived_profile)
        
        # Step 4: Scale features
        scaled_features = self.scale_features(encoded_features)
        
        return scaled_features
    
    def get_feature_importance_template(self) -> Dict:
        """
        Return template for feature importance explanation
        """
        return {
            'raw_features': [
                'age', 'weight', 'height', 'gender', 'experience', 'goal',
                'equipment', 'injuries', 'days_per_week', 'session_time'
            ],
            'derived_features': [
                'bmi', 'experience_score', 'recovery_score', 'consistency_score',
                'equipment_richness', 'intensity_capacity', 'progressive_overload_delta',
                'age_adjusted_capacity'
            ],
            'encoded_features': [
                'experience_encoded', 'goal_encoded', 'gender_encoded',
                'equipment_encoded_*', 'injury_encoded_*'
            ]
        }
    
    def cold_start_strategy(self, user_profile: Dict) -> Dict:
        """
        Handle cold start scenario with similarity-based matching
        """
        # For new users with limited history, use demographic and goal-based templates
        template = {
            'recommended_exercises': [],
            'baseline_intensity': 0.6,  # Start conservative
            'progression_rate': 0.05,  # 5% weekly increase
            'safety_factors': {
                'injury_risk': 0.1 if user_profile.get('injuries') else 0.0,
                'overtraining_risk': 0.2 if user_profile.get('experience') == 'Beginner' else 0.1
            }
        }
        
        # Base template on experience and goal
        if user_profile['experience'] == 'Beginner':
            template['baseline_intensity'] = 0.5
            template['progression_rate'] = 0.03
        elif user_profile['experience'] == 'Advanced':
            template['baseline_intensity'] = 0.8
            template['progression_rate'] = 0.07
        
        # Adjust for goal
        if user_profile['goal'] in ['Weight Loss', 'Endurance']:
            template['baseline_intensity'] *= 0.9
        elif user_profile['goal'] in ['Muscle Gain', 'Strength']:
            template['baseline_intensity'] *= 1.1
        
        return template


def explain_pipeline_design():
    """
    Detailed explanation of the feature pipeline design
    """
    
    print("=" * 80)
    print("ELEVATE FITNESS - WORKOUT RECOMMENDATION FEATURE PIPELINE DESIGN")
    print("=" * 80)
    
    print("\n" + "=" * 40)
    print("SECTION 1  RAW USER INPUT FEATURES")
    print("=" * 40)
    print("""
Schema Definition:
- age: Integer (18-80) - Affects intensity capacity and recovery
- weight: Float (40-200 kg) - Used for calculating BMI and load calculations
- height: Float (120-250 cm) - Used for calculating BMI
- gender: String (Male/Female/Other) - Affects normative values and recommendations
- experience: String (Beginner/Intermediate/Advanced) - Determines starting intensity
- goal: String (Weight Loss/Muscle Gain/Maintenance/Strength/Endurance/Athletic Performance) - Drives exercise selection
- equipment: List[String] - Determines exercise feasibility
- injuries: List[String] - Safety constraints for exercise selection
- days_per_week: Integer (1-7) - Schedules workout frequency
- session_time: Integer (15-180 min) - Influences workout structure
- workout_history_count: Integer - Tracks user progression
- streak_count: Integer - Motivation and consistency indicator
- consistency: Float (0.0-1.0) - Affects progression rate
- sleep_score: Float (1.0-10.0) - Recovery metric
- hydration_score: Float (1.0-10.0) - Recovery metric
- stress_level: Float (1.0-10.0) - Recovery metric (inverted)
    """)
    
    print("\n" + "=" * 40)
    print("SECTION 2  DERIVED FEATURES")
    print("=" * 40)
    print("""
Formulas and Importance:
1. BMI = weight / (height/100)^2
   - Importance: Health screening and load adjustment
   
2. Experience Score = mapping[experience] (1-3)
   - Importance: Determines baseline intensity and complexity
   
3. Recovery Score = avg(sleep/10, hydration/10, (10-stress)/10)
   - Importance: Adjusts intensity based on readiness to train
   
4. Consistency Score = user_provided_value
   - Importance: Influences progression rate and motivation strategies
   
5. Equipment Richness = min(1.0, len(equipment)/10)
   - Importance: Measures resource availability for exercise variety
   
6. Intensity Capacity = (experience_score * 0.6) + (recovery_score * 0.4)
   - Importance: Combined measure of ability to handle intense training
   
7. Progressive Overload Delta = base * adherence * recovery * experience_mod
   - Importance: Controls rate of progression to prevent plateaus
   
8. Age-Adjusted Capacity = intensity_capacity * age_factor
   - Importance: Accounts for age-related changes in recovery and capacity
    """)
    
    print("\n" + "=" * 40)
    print("SECTION 3  TARGET VARIABLES")
    print("=" * 40)
    print("""
ML Targets Defined:
- Exercise Category: Chest, Back, Legs, Shoulders, Arms, Core
  - Model: Multi-class classification
  - Purpose: Muscle group targeting based on goals and equipment

- Sets: 1-6 (integer regression/classification)
  - Model: Regression or ordinal classification
  - Purpose: Volume prescription based on experience and recovery

- Rep Range (low, high): 1-25 (pair of integers)
  - Model: Paired regression
  - Purpose: Intensity prescription based on goals (hypertrophy, strength, endurance)

- Rest Time: 30-240 seconds (integer regression)
  - Model: Regression
  - Purpose: Recovery optimization based on intensity and goals

- Intensity Level: Low, Moderate, High, Very High (classification)
  - Model: Multi-class classification
  - Purpose: Overall workout intensity based on capacity and goals

- Workout Split: Full Body, Upper/Lower, Push/Pull/Legs, etc. (classification)
  - Model: Multi-class classification
  - Purpose: Weekly structure based on days available and experience

Separate models needed because:
1. Different target types (classification vs regression)
2. Different feature importance for each target
3. Safety considerations vary by target
4. Different progression patterns for each aspect
    """)
    
    print("\n" + "=" * 40)
    print("SECTION 4  ENCODING STRATEGY")
    print("=" * 40)
    print("""
Encoding Approaches:
1. Label Encoding: 
   - Applied to: experience, goal, gender
   - Tradeoff: Preserves ordinal relationships but assumes equal distances between categories

2. One-Hot Encoding:
   - Applied to: exercise categories, workout splits
   - Tradeoff: Creates sparse matrices but treats categories equally

3. Multi-Hot Encoding (MultiLabelBinarizer):
   - Applied to: equipment, injuries
   - Tradeoff: Handles multiple simultaneous values but increases dimensionality

4. Binary Encoding:
   - Applied to: injury flags
   - Tradeoff: Efficient for yes/no features
    """)
    
    print("\n" + "=" * 40)
    print("SECTION 5  SCALING STRATEGY")
    print("=" * 40)
    print("""
Scaling Decisions:
1. Scaled: age, weight, height, bmi, days_per_week, session_time, 
          workout_history_count, streak_count, consistency_score, 
          recovery_score, equipment_richness, intensity_capacity, 
          progressive_overload_delta, age_adjusted_capacity
   - Reason: Ensures equal contribution to distance calculations and gradient descent

2. Left Raw: encoded categorical features (already normalized 0-1)
   - Reason: Already in appropriate range for ML models

3. Special Handling: equipment and injury vectors (binary, 0-1 range)
   - Reason: Natural binary representation
    """)
    
    print("\n" + "=" * 40)
    print("SECTION 6  COLD START STRATEGY")
    print("=" * 40)
    print("""
Cold Start Approach:
1. Similarity-Based Matching:
   - Compare new user demographics (age, gender, experience) to existing user clusters
   - Use k-nearest neighbors on demographic features
   - Apply successful patterns from similar users

2. Baseline Template Plans:
   - Beginner: Conservative intensity (50%), slow progression (3% weekly)
   - Intermediate: Moderate intensity (70%), moderate progression (5% weekly)
   - Advanced: Higher intensity (80%), faster progression (7% weekly)
   
3. Goal-Specific Adjustments:
   - Weight Loss: Higher volume, shorter rest, cardio emphasis
   - Muscle Gain: Moderate-heavy loads, 6-12 rep range, adequate rest
   - Strength: Heavy loads, 1-5 rep range, longer rest periods
   - Endurance: Lighter loads, higher reps, shorter rest periods
    """)
    
    print("\n" + "=" * 40)
    print("SECTION 7  PIPELINE FLOW")
    print("=" * 40)
    print("""
Step-by-Step Data Flow:
1. Raw Input  Validation
   - Sanitize and normalize input values
   - Apply default values for missing fields
   - Range-check all numerical inputs

2. Validation  Feature Engineering
   - Calculate derived features (BMI, scores, deltas)
   - Apply domain knowledge transformations
   - Create composite indicators

3. Feature Engineering  Encoding
   - Convert categorical to numerical representations
   - Apply multi-hot encoding for multi-value fields
   - Preserve interpretability where possible

4. Encoding  Scaling
   - Apply standardization to numerical features
   - Maintain binary nature of encoded features
   - Prepare for ML algorithm requirements

5. Scaling  Model
   - Feed to trained ML models for predictions
   - Generate multiple target predictions
   - Apply ensemble methods if available

6. Model  Safety Override
   - Check for injury contraindications
   - Verify intensity is appropriate for experience
   - Apply safety caps and limits

7. Safety Override  Final Output
   - Format recommendations for frontend
   - Include confidence scores
   - Provide safety warnings if needed
    """)


if __name__ == "__main__":
    # Example usage
    pipeline = FeaturePipeline()
    
    # Example user profile
    user_profile = {
        'age': 28,
        'weight': 75.0,
        'height': 180.0,
        'gender': 'Male',
        'experience': 'Intermediate',
        'goal': 'Muscle Gain',
        'equipment': ['Dumbbell', 'Barbell', 'Bench'],
        'injuries': ['Knee'],
        'days_per_week': 4,
        'session_time': 60,
        'workout_history_count': 25,
        'streak_count': 3,
        'consistency': 0.8,
        'sleep_score': 8.0,
        'hydration_score': 7.5,
        'stress_level': 4.0
    }
    
    # Process the profile
    features = pipeline.process_user_profile(user_profile)
    print(f"Generated feature vector shape: {features.shape}")
    print(f"Sample of features: {features[:10]}...")  # First 10 features
    
    # Show cold start strategy
    cold_start = pipeline.cold_start_strategy(user_profile)
    print(f"Cold start template: {cold_start}")
    
    # Explain the design
    explain_pipeline_design()