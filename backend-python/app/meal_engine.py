import pandas as pd
import os
import numpy as np
from typing import Dict, List
from datetime import datetime

class MealEngine:
    def __init__(self):
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        
        # Load nutrition data
        nutrition_processed = os.path.join(base_dir, 'data', 'nutrition_processed.csv')
        nutrition_raw = os.path.join(base_dir, 'data', 'nutrition.csv')
        
        print(f"📁 Looking for nutrition data...")
        print(f"   Processed: {nutrition_processed}")
        print(f"   Raw: {nutrition_raw}")
        
        if os.path.exists(nutrition_processed):
            self.nutrition_df = pd.read_csv(nutrition_processed)
            print(f"✅ Loaded {len(self.nutrition_df)} meals from processed data")
        elif os.path.exists(nutrition_raw):
            self.nutrition_df = pd.read_csv(nutrition_raw)
            print(f"✅ Loaded {len(self.nutrition_df)} meals from raw data")
        else:
            print(f"❌ No nutrition data found!")
            # Create dummy data as fallback
            self.nutrition_df = pd.DataFrame({
                'Name': ['Chicken Breast', 'Brown Rice', 'Broccoli', 'Salmon', 'Sweet Potato'],
                'Type': ['Breakfast', 'Lunch', 'Lunch', 'Dinner', 'Snack'],
                'Calories': [165, 150, 55, 280, 103],
                'Protein': [31, 3, 3.7, 25, 2.3],
                'Carbs': [0, 33, 11, 0, 24],
                'Fats': [3.6, 1.5, 0.6, 17, 0.1],
                'Tags': ['High Protein', 'Lean Meat', 'Carbs', 'Omega-3', 'Carbs']
            })
            print(f"⚠️ Using fallback dummy data with {len(self.nutrition_df)} meals")
        
        # Standardize column names (CSV uses 'Type', 'Name', 'Fats')
        column_mapping = {
            'Type': 'meal_type',
            'Name': 'name',
            'Fats': 'fat',
            'Total_Fat': 'fat',
            'total_fat': 'fat',
            'Calories': 'calories',
            'Protein': 'protein',
            'Carbs': 'carbs',
            'Carbohydrate': 'carbs',
            'carbohydrate': 'carbs',
            'Tags': 'tags'
        }
        
        self.nutrition_df.rename(columns=column_mapping, inplace=True)
        self.nutrition_df.columns = self.nutrition_df.columns.str.lower().str.strip()
        
        print(f"📊 Columns available: {list(self.nutrition_df.columns)}")
        
        # Fill missing values
        if 'meal_type' in self.nutrition_df.columns:
            self.nutrition_df['meal_type'].fillna('Snack', inplace=True)
        if 'tags' in self.nutrition_df.columns:
            self.nutrition_df['tags'].fillna('', inplace=True)
        
        # Show sample data
        print(f"📋 Sample meals:")
        print(self.nutrition_df[['name', 'meal_type', 'calories']].head(3).to_string(index=False))
        
        # Macro ratios by goal
        self.goal_macros = {
            'Weight Loss': {'protein': 0.35, 'carbs': 0.35, 'fat': 0.30},
            'Fat Loss': {'protein': 0.35, 'carbs': 0.35, 'fat': 0.30},
            'Muscle Gain': {'protein': 0.30, 'carbs': 0.50, 'fat': 0.20},
            'Maintenance': {'protein': 0.25, 'carbs': 0.50, 'fat': 0.25}
        }
        
        print("✅ MealEngine initialized\n")
    
    def calculate_bmr(self, weight: float, height: float, age: int, gender: str) -> float:
        """Calculate Basal Metabolic Rate (Mifflin-St Jeor)"""
        if gender.lower() in ['male', 'm']:
            return 88.362 + (13.397 * weight) + (4.799 * height) - (5.677 * age)
        else:
            return 447.593 + (9.247 * weight) + (3.098 * height) - (4.330 * age)
    
    def calculate_daily_calories(self, user_profile: Dict, activity_multiplier: float = 1.55) -> float:
        """Calculate daily calorie needs based on user profile"""
        bmr = self.calculate_bmr(
            user_profile.get('weight', 70),
            user_profile.get('height', 175),
            user_profile.get('age', 25),
            user_profile.get('gender', 'Male')
        )
        
        goal = user_profile.get('goal', 'Maintenance')
        tdee = bmr * activity_multiplier
        
        # Adjust for goal
        if goal == 'Weight Loss' or goal == 'Fat Loss':
            return tdee * 0.85  # 15% deficit
        elif goal == 'Muscle Gain':
            return tdee * 1.10  # 10% surplus
        else:
            return tdee
    
    def suggest_daily_meals(self, user_profile: Dict) -> Dict:
        """Generate daily meal recommendations"""
        print(f"🍽️ Generating meals for {user_profile.get('goal', 'Maintenance')}")
        
        # Calculate daily targets
        daily_calories = self.calculate_daily_calories(user_profile)
        goal = user_profile.get('goal', 'Maintenance')
        macros = self.goal_macros.get(goal, self.goal_macros['Maintenance'])
        
        target_protein = (daily_calories * macros['protein']) / 4
        target_carbs = (daily_calories * macros['carbs']) / 4
        target_fat = (daily_calories * macros['fat']) / 9
        
        daily_target = {
            'calories': round(daily_calories),
            'protein': round(target_protein, 1),
            'carbs': round(target_carbs, 1),
            'fat': round(target_fat, 1)
        }
        
        print(f"   Daily targets: {daily_calories:.0f} cal, {target_protein:.0f}g protein")
        
        # Meal type distribution (based on CSV 'Type' column values)
        meal_types = {
            'breakfast': 0.25,
            'lunch': 0.35,
            'snack': 0.10,
            'dinner': 0.30
        }
        
        suggested_meals = []
        
        for meal_type, ratio in meal_types.items():
            cal_target = daily_calories * ratio
            
            # Filter meals by type (case-insensitive match)
            available = self.nutrition_df.copy()
            
            if 'meal_type' in available.columns:
                type_meals = available[
                    available['meal_type'].str.lower().str.strip().str.contains(meal_type, case=False, na=False)
                ]
            else:
                type_meals = available
            
            # If no exact match, use all meals
            if type_meals.empty:
                type_meals = available
            
            # Find meal closest to calorie target
            if not type_meals.empty:
                type_meals = type_meals.copy()
                type_meals['cal_diff'] = (type_meals['calories'].fillna(0) - cal_target).abs()
                best_meal = type_meals.nsmallest(1, 'cal_diff').iloc[0]
                
                suggested_meals.append({
                    'meal_type': meal_type,
                    'name': str(best_meal.get('name', f'{meal_type.capitalize()} Meal')),
                    'calories': int(best_meal.get('calories', 500)),
                    'protein': float(best_meal.get('protein', 20)),
                    'carbs': float(best_meal.get('carbs', best_meal.get('carbohydrate', 50))),  # ← Handle both column names
                    'fat': float(best_meal.get('fat', best_meal.get('total_fat', 15))),  # ← Handle both column names
                    'fiber': float(best_meal.get('fiber', 0)),
                    'tags': str(best_meal.get('tags', ''))
                })
        
        print(f"✅ Generated {len(suggested_meals)} meals\n")
        
        return {
            'date': datetime.now().strftime('%Y-%m-%d'),
            'daily_target': daily_target,
            'meals': suggested_meals,
            'note': f'Daily plan optimized for {goal}',
            'ml_powered': True
        }


# Singleton pattern
_meal_engine = None

def get_meal_engine():
    global _meal_engine
    if _meal_engine is None:
        _meal_engine = MealEngine()
    return _meal_engine