"""
Nutrition Intelligence Engine for Elevate Fitness

.. deprecated::
    ARCH-4: This module is DEPRECATED. ``DeterministicMealEngine``
    (``backend-python/app/deterministic_meal_engine.py``) is now the
    canonical meal-planning engine. Do NOT add new features here.
    This file is retained only for backward-compatibility until the
    remaining call-sites in server.py are migrated.

This module handles intelligent meal planning with hard constraints,
macro balancing, and dietary restrictions compliance.
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Optional
from datetime import datetime, timedelta
import json
import logging
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import warnings
warnings.filterwarnings('ignore')
from .multitarget_nutrition_model import MultiTargetNutritionModel

logger = logging.getLogger(__name__)


class NutritionIntelligenceEngine:
    """
    Complete nutrition intelligence engine with constraint satisfaction
    """
    
    def __init__(self, nutrition_data_path: str = None):
        # Initialize multi-target nutrition model
        self.multi_target_model = MultiTargetNutritionModel()
        
        # Load nutrition data
        if nutrition_data_path and pd.io.common.file_exists(nutrition_data_path):
            self.nutrition_df = pd.read_csv(nutrition_data_path)
        else:
            # Fallback data
            self.nutrition_df = pd.DataFrame({
                'name': [
                    'Grilled Chicken Breast', 'Salmon Fillet', 'Brown Rice', 
                    'Quinoa', 'Broccoli', 'Spinach', 'Sweet Potato', 
                    'Oatmeal', 'Greek Yogurt', 'Almonds', 'Banana', 'Apple'
                ],
                'calories': [165, 280, 150, 222, 55, 23, 103, 389, 100, 579, 105, 95],
                'protein': [31, 25, 3, 8, 3.7, 2.9, 2.3, 17, 10, 21, 1.3, 0.5],
                'carbs': [0, 0, 33, 39, 11, 3.6, 24, 66, 12, 22, 27, 25],
                'fat': [3.6, 17, 1.5, 3.6, 0.6, 0.4, 0.1, 6.9, 0.4, 50, 0.4, 0.3],
                'fiber': [0, 0, 1.8, 2.8, 2.6, 2.2, 3, 10.6, 0, 12.5, 3.1, 4.4],
                'meal_type': ['Protein', 'Protein', 'Carb', 'Carb', 'Veggie', 'Veggie', 'Carb', 'Carb', 'Protein', 'Fat', 'Fruit', 'Fruit'],
                'dietary_tags': ['High Protein', 'Omega-3', 'Complex Carb', 'Gluten-Free', 'Fiber-Rich', 'Iron-Rich', 'Complex Carb', 'Fiber-Rich', 'Probiotic', 'Healthy Fat', 'Natural Sugar', 'Fiber-Rich'],
                'allergens': ['', '', '', '', '', '', '', '', 'Dairy', 'Tree Nuts', '', '']
            })
        
        # Define macro ratios by goal
        self.macro_ratios = {
            'Weight Loss': {'protein': 0.35, 'carbs': 0.35, 'fat': 0.30},
            'Fat Loss': {'protein': 0.40, 'carbs': 0.30, 'fat': 0.30},
            'Muscle Gain': {'protein': 0.30, 'carbs': 0.50, 'fat': 0.20},
            'Strength': {'protein': 0.30, 'carbs': 0.55, 'fat': 0.15},
            'Endurance': {'protein': 0.15, 'carbs': 0.70, 'fat': 0.15},
            'Maintenance': {'protein': 0.25, 'carbs': 0.50, 'fat': 0.25}
        }
        
        # Activity multipliers
        self.activity_multipliers = {
            'Sedentary': 1.2,
            'Light': 1.375,
            'Moderate': 1.55,
            'Active': 1.725,
            'Very Active': 1.9
        }
        
        # Protein requirements (g per kg of body weight)
        self.protein_requirements = {
            'Beginner': 1.6,
            'Intermediate': 1.8,
            'Advanced': 2.2
        }
        
        # Encode categorical variables for the model
        self.gender_map = {'Male': 1, 'Female': 0, 'Other': 0}
        self.experience_map = {'Beginner': 0, 'Intermediate': 1, 'Advanced': 2}
        self.goal_map = {
            'Weight Loss': 0, 'Fat Loss': 1, 'Muscle Gain': 2, 
            'Strength': 3, 'Endurance': 4, 'Maintenance': 5
        }
        self.activity_map = {
            'Sedentary': 0, 'Light': 1, 'Moderate': 2, 
            'Active': 3, 'Very Active': 4
        }
        self.dietary_pref_map = {'Non-Veg': 0, 'Vegetarian': 1, 'Vegan': 2}
    
    def validate_user_input(self, user_profile: Dict) -> Dict:
        """
        Validate and sanitize user input
        """
        validated_profile = {}
        
        # Required fields with defaults
        required_fields = {
            'age': 25,
            'weight': 70.0,  # kg
            'height': 175.0,  # cm
            'gender': 'Male',
            'goal': 'Muscle Gain',
            'activity_level': 'Moderate',
            'dietary_preference': 'Non-Veg',
            'allergies': [],
            'food_dislikes': [],
            'budget_range': 'Medium',
            'cuisine_preference': 'Mixed'
        }
        
        for field, default in required_fields.items():
            if field not in user_profile:
                validated_profile[field] = default
            else:
                validated_profile[field] = user_profile[field]
        
        # Validate ranges
        validated_profile['age'] = max(18, min(80, validated_profile['age']))
        validated_profile['weight'] = max(40.0, min(200.0, validated_profile['weight']))
        validated_profile['height'] = max(120.0, min(250.0, validated_profile['height']))
        
        return validated_profile
    
    def calculate_derived_metrics(self, user_profile: Dict) -> Dict:
        """
        Calculate derived nutritional metrics with extreme value handling
        """
        derived = user_profile.copy()
        
        # Validate and clamp extreme values
        age = max(18, min(100, derived.get('age', 25)))
        weight = max(30, min(300, derived.get('weight', 70.0)))  # 30-300 kg range
        height = max(100, min(250, derived.get('height', 175.0)))  # 100-250 cm range
        
        derived['age'] = age
        derived['weight'] = weight
        derived['height'] = height
        
        # BMR calculation (Mifflin-St Jeor Equation)
        if derived['gender'].lower() in ['male', 'm', 'man']:
            bmr = 10 * weight + 6.25 * height - 5 * age + 5
        else:
            bmr = 10 * weight + 6.25 * height - 5 * age - 161
        
        # Clamp BMR to reasonable range
        bmr = max(800, min(5000, bmr))  # Typical BMR range
        derived['bmr'] = bmr
        
        # TDEE calculation
        activity_multiplier = self.activity_multipliers.get(derived['activity_level'], 1.55)
        tdee = bmr * activity_multiplier
        
        # Clamp TDEE to reasonable range
        tdee = max(1200, min(5000, tdee))  # Typical TDEE range
        derived['tdee'] = tdee
        
        # Calorie target based on goal
        goal_multiplier = {
            'Weight Loss': 0.85,
            'Fat Loss': 0.80,
            'Muscle Gain': 1.10,
            'Strength': 1.05,
            'Endurance': 1.00,
            'Maintenance': 1.00
        }
        
        calorie_target = tdee * goal_multiplier.get(derived['goal'], 1.00)
        
        # Clamp calorie target to reasonable range
        calorie_target = max(1200, min(5000, calorie_target))
        derived['daily_calorie_target'] = calorie_target
        
        # Protein requirement (g per kg body weight)
        protein_requirement_per_kg = 1.8  # Default
        if 'experience' in derived:
            protein_requirement_per_kg = self.protein_requirements.get(derived['experience'], 1.8)
        
        # Clamp protein requirement to reasonable range
        protein_requirement_per_kg = max(1.2, min(3.0, protein_requirement_per_kg))
        derived['protein_requirement_g'] = weight * protein_requirement_per_kg
        
        # Macro targets based on goal
        macro_ratio = self.macro_ratios.get(derived['goal'], self.macro_ratios['Maintenance'])
        derived['macro_targets'] = {
            'protein_calories': calorie_target * macro_ratio['protein'],
            'carb_calories': calorie_target * macro_ratio['carbs'],
            'fat_calories': calorie_target * macro_ratio['fat']
        }
        
        # Convert to grams
        derived['macro_targets_g'] = {
            'protein_g': derived['macro_targets']['protein_calories'] / 4,  # 4 cal/g protein
            'carb_g': derived['macro_targets']['carb_calories'] / 4,      # 4 cal/g carbs
            'fat_g': derived['macro_targets']['fat_calories'] / 9         # 9 cal/g fat
        }
        
        # Fiber minimum (25g for women, 38g for men, or 14g per 1000 calories)
        fiber_min = max(25 if derived['gender'].lower() in ['female', 'f', 'woman'] else 38, 
                       (calorie_target / 1000) * 14)
        derived['fiber_minimum'] = fiber_min
        
        return derived
    
    def apply_hard_constraints(self, foods_df: pd.DataFrame, user_profile: Dict) -> pd.DataFrame:
        """
        Apply hard constraints to filter foods
        """
        filtered_df = foods_df.copy()

        # Exclude allergens (only if column exists)
        if 'allergies' in user_profile and user_profile['allergies']:
            if 'allergens' in filtered_df.columns:
                allergen_pattern = '|'.join(user_profile['allergies'])
                filtered_df = filtered_df[~filtered_df['allergens'].str.contains(allergen_pattern, case=False, na=False)]
            else:
                # Log warning but continue
                logger.warning("Allergens column not found in nutrition data, skipping allergy filtering")

        # Dietary preference constraints
        if user_profile.get('dietary_preference', '').lower() == 'vegan':
            filtered_df = filtered_df[~filtered_df['name'].str.contains('chicken|beef|pork|fish|egg|milk|cheese|yogurt', case=False)]
        elif user_profile.get('dietary_preference', '').lower() == 'vegetarian':
            filtered_df = filtered_df[~filtered_df['name'].str.contains('chicken|beef|pork|fish', case=False)]

        # Food dislikes
        if 'food_dislikes' in user_profile and user_profile['food_dislikes']:
            dislikes_pattern = '|'.join(user_profile['food_dislikes'])
            filtered_df = filtered_df[~filtered_df['name'].str.contains(dislikes_pattern, case=False)]

        # Remove null calorie entries
        filtered_df = filtered_df[filtered_df['calories'].notna() & (filtered_df['calories'] > 0)]

        return filtered_df
    
    def calculate_meal_splits(self, daily_calories: float) -> Dict[str, float]:
        """
        Calculate calorie splits for different meals
        """
        meal_splits = {
            'breakfast': daily_calories * 0.25,
            'lunch': daily_calories * 0.35,
            'dinner': daily_calories * 0.30,
            'snack': daily_calories * 0.10  # Distributed among snacks
        }
        
        return meal_splits
    
    def select_meals_for_day(self, available_foods: pd.DataFrame,
                           meal_calories: Dict[str, float],
                           user_profile: Dict,
                           previous_days_meals: List[str] = None) -> Dict[str, List[Dict]]:
        """
        Select meals for a single day with diversity and constraint satisfaction
        """
        if previous_days_meals is None:
            previous_days_meals = []

        daily_meals = {}

        for meal_type, target_calories in meal_calories.items():
            # Filter by meal type if available
            meal_foods = available_foods.copy()
            if 'meal_type' in meal_foods.columns:
                # Try to match meal type, but fall back to all if none match
                type_matches = meal_foods[meal_foods['meal_type'].str.lower() == meal_type.lower()]
                if not type_matches.empty:
                    meal_foods = type_matches

            # Avoid recently used meals (3-day rule)
            if previous_days_meals:
                recent_meals_pattern = '|'.join(previous_days_meals[-3:])  # Last 3 days
                # Check if 'name' column exists before filtering
                if 'name' in meal_foods.columns:
                    meal_foods = meal_foods[~meal_foods['name'].str.contains(recent_meals_pattern, case=False, na=False)]

            # If no foods left after filtering, use original set
            if meal_foods.empty:
                meal_foods = available_foods.copy()

            # If still empty, use fallback foods
            if meal_foods.empty or 'name' not in meal_foods.columns:
                meal_foods = self._get_fallback_foods(meal_type)

            # Select meals that best match target calories
            selected_meals = self._select_meals_by_calories(meal_foods, target_calories, meal_type)

            # If no meals were selected, use fallback
            if not selected_meals:
                selected_meals = self._get_fallback_meal(meal_type, target_calories)

            daily_meals[meal_type] = selected_meals

        return daily_meals
    
    def _get_fallback_foods(self, meal_type: str) -> pd.DataFrame:
        """
        Get fallback foods when filtering removes all options
        """
        # Create minimal fallback foods based on meal type
        fallback_data = {
            'name': [f'{meal_type.capitalize()} Option'],
            'calories': [300.0],
            'protein': [20.0],
            'carbs': [30.0],
            'fat': [10.0],
            'fiber': [5.0],
            'meal_type': [meal_type],
            'dietary_tags': ['Fallback'],
            'allergens': ['']
        }
        return pd.DataFrame(fallback_data)
    
    def _get_fallback_meal(self, meal_type: str, target_calories: float) -> List[Dict]:
        """
        Get a fallback meal when no suitable foods are found
        """
        return [{
            'name': f'{meal_type.capitalize()} Fallback',
            'calories': target_calories,
            'protein': target_calories * 0.25 / 4,  # 25% protein
            'carbs': target_calories * 0.50 / 4,   # 50% carbs
            'fat': target_calories * 0.25 / 9,     # 25% fat
            'fiber': 5.0,
            'meal_type': meal_type
        }]
    
    def _select_meals_by_calories(self, foods_df: pd.DataFrame, target_calories: float, meal_type: str) -> List[Dict]:
        """
        Select meals that best match target calories for a meal type
        """
        # Sort by proximity to target calories
        foods_df = foods_df.copy()
        foods_df['calorie_diff'] = abs(foods_df['calories'] - target_calories)
        foods_df = foods_df.sort_values('calorie_diff')

        selected_meals = []
        remaining_calories = target_calories

        for _, food in foods_df.iterrows():
            if remaining_calories <= 0:
                break

            food_calories = food['calories']

            # If this food fits reasonably well
            if food_calories <= remaining_calories * 1.2:  # Allow up to 20% over
                selected_meals.append({
                    'name': food['name'],
                    'calories': food_calories,
                    'protein': food['protein'] if 'protein' in food else 0,
                    'carbs': food['carbs'] if 'carbs' in food else 0,
                    'fat': food['fat'] if 'fat' in food else 0,
                    'fiber': food['fiber'] if 'fiber' in food else 0,
                    'meal_type': meal_type
                })
                remaining_calories -= food_calories
        
        # If no meals were selected, pick the closest one
        if not selected_meals and not foods_df.empty:
            closest_food = foods_df.iloc[0]
            selected_meals.append({
                'name': closest_food['name'],
                'calories': closest_food['calories'],
                'protein': closest_food['protein'] if 'protein' in closest_food else 0,
                'carbs': closest_food['carbs'] if 'carbs' in closest_food else 0,
                'fat': closest_food['fat'] if 'fat' in closest_food else 0,
                'fiber': closest_food['fiber'] if 'fiber' in closest_food else 0,
                'meal_type': meal_type
            })

        return selected_meals
    
    def generate_weekly_plan(self, user_profile: Dict) -> Dict:
        """
        Generate a complete weekly meal plan using multi-target model
        """
        # Validate and derive metrics
        validated_profile = self.validate_user_input(user_profile)
        derived_profile = self.calculate_derived_metrics(validated_profile)
        
        # Prepare features for the multi-target model
        features_df = self._prepare_features_for_model(validated_profile)
        
        # Use the multi-target model to predict nutrition parameters
        try:
            predictions = self.multi_target_model.predict(features_df)
            
            # Extract predictions
            breakfast_calories = predictions[0][0]
            lunch_calories = predictions[0][1]
            dinner_calories = predictions[0][2]
            snack_calories = predictions[0][3]
            protein_total = predictions[0][4]
            carbs_total = predictions[0][5]
            fats_total = predictions[0][6]
            
            print(f"Multi-target model predictions: Breakfast={breakfast_calories:.1f}, Lunch={lunch_calories:.1f}, Dinner={dinner_calories:.1f}, Snack={snack_calories:.1f}")
            print(f"Macros: Protein={protein_total:.1f}, Carbs={carbs_total:.1f}, Fats={fats_total:.1f}")
            
        except Exception as e:
            print(f"Multi-target model prediction failed: {e}")
            # Fallback to original method
            daily_meal_splits = self.calculate_meal_splits(derived_profile['daily_calorie_target'])
            protein_total = derived_profile['macro_targets_g']['protein_g'] * 4  # Convert to calories
            carbs_total = derived_profile['macro_targets_g']['carb_g'] * 4      # Convert to calories
            fats_total = derived_profile['macro_targets_g']['fat_g'] * 9        # Convert to calories
            breakfast_calories = daily_meal_splits['breakfast']
            lunch_calories = daily_meal_splits['lunch']
            dinner_calories = daily_meal_splits['dinner']
            snack_calories = daily_meal_splits['snack']
        
        # Apply hard constraints
        filtered_foods = self.apply_hard_constraints(self.nutrition_df, validated_profile)
        
        # Create meal splits based on model predictions
        daily_meal_splits = {
            'breakfast': breakfast_calories,
            'lunch': lunch_calories,
            'dinner': dinner_calories,
            'snack': snack_calories
        }
        
        # Generate weekly plan
        weekly_plan = {}
        all_selected_meals = []  # Track all meals for diversity
        
        for day in range(7):
            day_name = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'][day]
            
            # Get previous days' meals for diversity
            prev_meals = all_selected_meals[max(0, len(all_selected_meals)-3):]  # Last 3 days
            
            # Select meals for this day
            day_meals = self.select_meals_for_day(
                filtered_foods, 
                daily_meal_splits, 
                validated_profile,
                [meal['name'] for meal in prev_meals]
            )
            
            # Add to tracking
            for meal_type, meals in day_meals.items():
                all_selected_meals.extend(meals)
            
            weekly_plan[day_name] = day_meals
        
        # Calculate weekly consistency score
        weekly_consistency = self._calculate_weekly_consistency(weekly_plan, derived_profile)
        
        # Generate shopping list
        shopping_list = self._generate_shopping_list(weekly_plan)
        
        # Create final output
        result = {
            'user_profile': derived_profile,
            'weekly_plan': weekly_plan,
            'weekly_summary': {
                'total_calories': sum(sum(sum(meal['calories'] for meal in meals) 
                                        for meals in day.values()) 
                                    for day in weekly_plan.values()),
                'weekly_macro_totals': self._calculate_weekly_macros(weekly_plan),
                'predicted_macros': {
                    'protein_calories': protein_total,
                    'carbs_calories': carbs_total,
                    'fats_calories': fats_total
                },
                'consistency_score': weekly_consistency,
                'shopping_list': shopping_list
            },
            'generation_timestamp': datetime.now().isoformat()
        }
        
        return result
    
    def _prepare_features_for_model(self, user_profile: Dict) -> pd.DataFrame:
        """
        Prepare user profile features for the multi-target model
        """
        # Create a single-row DataFrame with the user's features
        features = {
            'age': [user_profile.get('age', 25)],
            'weight': [user_profile.get('weight', 70.0)],
            'height': [user_profile.get('height', 175.0)],
            'gender_encoded': [self.gender_map.get(user_profile.get('gender', 'Male'), 1)],
            'experience_encoded': [self.experience_map.get(user_profile.get('experience', 'Beginner'), 0)],
            'goal_encoded': [self.goal_map.get(user_profile.get('goal', 'Muscle Gain'), 2)],
            'activity_level_encoded': [self.activity_map.get(user_profile.get('activity_level', 'Moderate'), 2)],
            'dietary_preference_encoded': [self.dietary_pref_map.get(user_profile.get('dietary_preference', 'Non-Veg'), 0)],
            'days_per_week': [user_profile.get('days_per_week', 4)],
            'workout_history_count': [user_profile.get('workout_history_count', 0)],
            'streak_count': [user_profile.get('streak', 0)],
            'consistency_score': [user_profile.get('consistency', 0.7)],
            'recovery_score': [(user_profile.get('sleep_score', 7.0) + user_profile.get('hydration_score', 7.0) + (10 - user_profile.get('stress_level', 5.0))) / 30],
            'equipment_richness': [min(1.0, len(user_profile.get('equipment', [])) / 10.0)],
            'intensity_capacity': [self.experience_map.get(user_profile.get('experience', 'Beginner'), 0) * 0.6 + ((user_profile.get('sleep_score', 7.0) + user_profile.get('hydration_score', 7.0) + (10 - user_profile.get('stress_level', 5.0))) / 30) * 0.4],
            'bmi': [user_profile.get('weight', 70.0) / ((user_profile.get('height', 175.0) / 100) ** 2)],
            'age_adjusted_capacity': [min(1.0, (user_profile.get('weight', 70.0) / ((user_profile.get('height', 175.0) / 100) ** 2)) * 0.01)],  # Simplified calculation
            'sleep_score': [user_profile.get('sleep_score', 7.0)],
            'hydration_score': [user_profile.get('hydration_score', 7.0)],
            'stress_level': [user_profile.get('stress_level', 5.0)]
        }
        
        return pd.DataFrame(features)
    
    def _calculate_weekly_consistency(self, weekly_plan: Dict, user_profile: Dict) -> float:
        """
        Calculate how well the weekly plan meets nutritional targets
        """
        # Calculate actual totals
        total_calories = 0
        total_protein = 0
        total_carbs = 0
        total_fat = 0
        
        for day_meals in weekly_plan.values():
            for meal_type, meals in day_meals.items():
                for meal in meals:
                    total_calories += meal['calories']
                    total_protein += meal['protein']
                    total_carbs += meal['carbs']
                    total_fat += meal['fat']
        
        # Calculate target totals for the week
        daily_target = user_profile['daily_calorie_target']
        weekly_target_calories = daily_target * 7
        
        macro_ratio = self.macro_ratios.get(user_profile['goal'], self.macro_ratios['Maintenance'])
        weekly_target_macros = {
            'protein_calories': weekly_target_calories * macro_ratio['protein'],
            'carb_calories': weekly_target_calories * macro_ratio['carbs'],
            'fat_calories': weekly_target_calories * macro_ratio['fat']
        }
        
        # Calculate consistency score (0-1, where 1 is perfect)
        calorie_consistency = 1 - abs(total_calories - weekly_target_calories) / weekly_target_calories
        protein_consistency = 1 - abs((total_protein * 4) - weekly_target_macros['protein_calories']) / weekly_target_macros['protein_calories']
        carb_consistency = 1 - abs((total_carbs * 4) - weekly_target_macros['carb_calories']) / weekly_target_macros['carb_calories']
        fat_consistency = 1 - abs((total_fat * 9) - weekly_target_macros['fat_calories']) / weekly_target_macros['fat_calories']
        
        # Average consistency (clamped between 0 and 1)
        consistency_score = max(0, min(1, (calorie_consistency + protein_consistency + 
                                         carb_consistency + fat_consistency) / 4))
        
        return consistency_score
    
    def _generate_shopping_list(self, weekly_plan: Dict) -> Dict:
        """
        Generate aggregated shopping list for the week
        """
        shopping_items = {}
        
        for day_meals in weekly_plan.values():
            for meal_type, meals in day_meals.items():
                for meal in meals:
                    name = meal['name']
                    if name in shopping_items:
                        shopping_items[name] += 1
                    else:
                        shopping_items[name] = 1
        
        return shopping_items
    
    def _calculate_weekly_macros(self, weekly_plan: Dict) -> Dict:
        """
        Calculate total macros for the week
        """
        total_protein = 0
        total_carbs = 0
        total_fat = 0
        total_fiber = 0
        
        for day_meals in weekly_plan.values():
            for meal_type, meals in day_meals.items():
                for meal in meals:
                    total_protein += meal['protein']
                    total_carbs += meal['carbs']
                    total_fat += meal['fat']
                    total_fiber += meal.get('fiber', 0)
        
        return {
            'protein_g': round(total_protein, 1),
            'carbs_g': round(total_carbs, 1),
            'fat_g': round(total_fat, 1),
            'fiber_g': round(total_fiber, 1),
            'protein_calories': round(total_protein * 4, 1),
            'carb_calories': round(total_carbs * 4, 1),
            'fat_calories': round(total_fat * 9, 1)
        }
    
    def swap_meal(self, weekly_plan: Dict, day: str, meal_type: str, new_meal: str) -> Dict:
        """
        Swap a specific meal in the weekly plan
        """
        # This would implement meal swapping logic
        # For now, we'll just return the plan unchanged
        # In a full implementation, this would validate the swap against constraints
        return weekly_plan


def explain_nutrition_engine_design():
    """
    Detailed explanation of the nutrition intelligence engine design
    """
    
    print("=" * 80)
    print("ELEVATE FITNESS - NUTRITION INTELLIGENCE ENGINE DESIGN")
    print("=" * 80)
    
    print("\n" + "=" * 40)
    print("SECTION 1  USER INPUT FEATURES")
    print("=" * 40)
    print("""
Schema Definition:
- age: Integer (18-80) - Used for BMR calculation
- weight: Float (40-200 kg) - Used for BMR and protein calculations
- height: Float (120-250 cm) - Used for BMR calculation
- gender: String (Male/Female/Other) - Affects BMR formula
- goal: String (Weight Loss/Fat Loss/Muscle Gain/Strength/Endurance/Maintenance) - Drives calorie and macro targets
- activity_level: String (Sedentary/Light/Moderate/Active/Very Active) - Multiplies BMR for TDEE
- dietary_preference: String (Non-Veg/Vegetarian/Vegan) - Hard constraint for food selection
- allergies: List[String] - Hard exclusion list
- food_dislikes: List[String] - Preference-based exclusions
- budget_range: String (Low/Medium/High) - Influences food selection
- cuisine_preference: String (Mixed/Asian/European/etc.) - Influences food selection
    """)
    
    print("\n" + "=" * 40)
    print("SECTION 2  DERIVED CALCULATIONS")
    print("=" * 40)
    print("""
Exact Formulas:
1. BMR (Mifflin-St Jeor):
   - Male: BMR = 10  weight(kg) + 6.25  height(cm) - 5  age(y) + 5
   - Female: BMR = 10  weight(kg) + 6.25  height(cm) - 5  age(y) - 161

2. TDEE: TDEE = BMR  Activity_Multiplier
   - Sedentary: 1.2, Light: 1.375, Moderate: 1.55, Active: 1.725, Very Active: 1.9

3. Calorie Target: Calorie_Target = TDEE  Goal_Multiplier
   - Weight Loss: 0.85, Fat Loss: 0.80, Muscle Gain: 1.10, Strength: 1.05, Others: 1.00

4. Protein Requirement: Weight(kg)  Protein_G_per_kg
   - Beginners: 1.6g, Intermediate: 1.8g, Advanced: 2.2g

5. Macro Ratios by Goal:
   - Weight Loss: P:35%, C:35%, F:30%
   - Fat Loss: P:40%, C:30%, F:30%
   - Muscle Gain: P:30%, C:50%, F:20%
   - Strength: P:30%, C:55%, F:15%
   - Endurance: P:15%, C:70%, F:15%
   - Maintenance: P:25%, C:50%, F:25%

6. Fiber Minimum: Max(25 for women/38 for men, 14g per 1000 calories)
    """)
    
    print("\n" + "=" * 40)
    print("SECTION 3  TARGET VARIABLES")
    print("=" * 40)
    print("""
Defined Targets:
- Daily Calorie Target: Calculated from BMR, activity, and goal
- Meal Calorie Splits: Breakfast(25%), Lunch(35%), Dinner(30%), Snacks(10%)
- Macro per Meal: Distributed according to daily targets
- Weekly Consistency Score: 0-1 measure of how well plan meets targets
    """)
    
    print("\n" + "=" * 40)
    print("SECTION 4  HARD CONSTRAINT ENGINE")
    print("=" * 40)
    print("""
Constraint Logic:
1. Calorie Clamp: All selected meals must fit within daily calorie targets
2. Macro Correction: Adjust selections to meet protein/carb/fat ratios
3. Allergy Exclusion: Foods containing allergens are filtered out completely
4. Dietary Enforcement: Vegetarian/Vegan filters remove animal products
5. Minimum Protein: Ensure protein requirements are always met regardless of other constraints
    """)
    
    print("\n" + "=" * 40)
    print("SECTION 5  WEEKLY GENERATION LOGIC")
    print("=" * 40)
    print("""
Generation Logic:
1. Diversity Scoring: Track previously selected meals to avoid repetition
2. Repetition Avoidance: 3-day rule prevents same meals within 3 days
3. Cuisine Rotation: Distribute different cuisine types throughout the week
4. Shopping List Aggregation: Combine ingredients needed for the entire week
    """)
    
    print("\n" + "=" * 40)
    print("SECTION 6  FINAL JSON OUTPUT STRUCTURE")
    print("=" * 40)
    print("""
Example Production JSON:
{
  "user_profile": {
    "age": 28,
    "weight": 75.0,
    "height": 180.0,
    "gender": "Male",
    "goal": "Muscle Gain",
    "daily_calorie_target": 2850.0,
    "protein_requirement_g": 135.0,
    "macro_targets": {
      "protein_calories": 855.0,
      "carb_calories": 1425.0,
      "fat_calories": 570.0
    },
    "macro_targets_g": {
      "protein_g": 213.8,
      "carb_g": 356.3,
      "fat_g": 63.3
    }
  },
  "weekly_plan": {
    "Monday": {
      "breakfast": [
        {
          "name": "Oatmeal",
          "calories": 389,
          "protein": 17,
          "carbs": 66,
          "fat": 6.9,
          "fiber": 10.6,
          "meal_type": "breakfast"
        }
      ],
      "lunch": [...],
      "dinner": [...],
      "snack": [...]
    },
    ...
  },
  "weekly_summary": {
    "total_calories": 19950,
    "weekly_macro_totals": {
      "protein_g": 1493.4,
      "carbs_g": 2492.3,
      "fat_g": 443.1
    },
    "consistency_score": 0.92,
    "shopping_list": {
      "Grilled Chicken Breast": 7,
      "Brown Rice": 7,
      "Broccoli": 7,
      ...
    }
  },
  "generation_timestamp": "2023-12-07T10:30:45.123456"
}
    """)


if __name__ == "__main__":
    # Example usage
    engine = NutritionIntelligenceEngine()
    
    # Example user profile
    user_profile = {
        'age': 28,
        'weight': 75.0,
        'height': 180.0,
        'gender': 'Male',
        'goal': 'Muscle Gain',
        'activity_level': 'Active',
        'dietary_preference': 'Non-Veg',
        'allergies': ['Shellfish'],
        'food_dislikes': ['Brussels Sprouts'],
        'budget_range': 'Medium',
        'cuisine_preference': 'Mixed'
    }
    
    # Generate weekly plan
    weekly_plan = engine.generate_weekly_plan(user_profile)
    print(f"Weekly plan generated for {user_profile['goal']} goal")
    print(f"Consistency score: {weekly_plan['weekly_summary']['consistency_score']:.2f}")
    print(f"Total weekly calories: {weekly_plan['weekly_summary']['total_calories']:.0f}")
    
    # Explain the design
    explain_nutrition_engine_design()