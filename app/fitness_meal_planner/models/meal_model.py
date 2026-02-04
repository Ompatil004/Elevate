"""
Meal Model for managing meal plans and history
"""

import json
import os
from datetime import datetime


class MealModel:
    def __init__(self, data_dir="data"):
        self.data_dir = data_dir
        self.meals_file = os.path.join(data_dir, "meals.json")
        self._ensure_data_dir_exists()
        self._initialize_meals_file()

    def _ensure_data_dir_exists(self):
        """Ensure the data directory exists"""
        if not os.path.exists(self.data_dir):
            os.makedirs(self.data_dir)

    def _initialize_meals_file(self):
        """Initialize the meals file if it doesn't exist"""
        if not os.path.exists(self.meals_file):
            with open(self.meals_file, 'w') as f:
                json.dump({}, f)

    def save_meal_plan(self, user_id, meal_plan):
        """Save a meal plan for a user"""
        meals = self._load_meals()
        
        # Generate new meal ID
        meal_id = len([ml for mls in meals.values() for ml in mls]) + 1
        
        # Add timestamp and user reference
        meal_plan['meal_id'] = meal_id
        meal_plan['user_id'] = user_id
        meal_plan['created_at'] = datetime.now().isoformat()
        meal_plan['updated_at'] = datetime.now().isoformat()
        
        # Add to user's meal history
        user_id_str = str(user_id)
        if user_id_str not in meals:
            meals[user_id_str] = []
        
        meals[user_id_str].append(meal_plan)
        
        # Save updated meals
        self._save_meals(meals)
        
        return meal_id

    def get_meal_history(self, user_id):
        """Get meal history for a user"""
        meals = self._load_meals()
        user_id_str = str(user_id)
        return meals.get(user_id_str, [])

    def _load_meals(self):
        """Load meals from file"""
        with open(self.meals_file, 'r') as f:
            return json.load(f)

    def _save_meals(self, meals):
        """Save meals to file"""
        with open(self.meals_file, 'w') as f:
            json.dump(meals, f, indent=2)