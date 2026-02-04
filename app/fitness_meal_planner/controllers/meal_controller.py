"""
Meal Controller for generating meal plans
"""

from flask import jsonify
from rules.nutrition_rules import NutritionRules
from ml.adaptive_engine import AdaptiveEngine
from models.meal_model import MealModel
from meal_plan_generator import MealPlanGenerator


class MealController:
    def __init__(self):
        self.nutrition_rules = NutritionRules()
        self.adaptive_engine = AdaptiveEngine()
        self.meal_model = MealModel()
        self.plan_generator = MealPlanGenerator()

    def generate_meal_plan(self, request_data):
        """Generate a personalized meal plan based on user profile"""
        try:
            user_profile = request_data.get('user_profile', {})

            # Use the meal plan generator to create a comprehensive plan
            meal_plan = self.plan_generator.generate_meal_plan(user_profile)

            # Save meal plan
            meal_id = self.meal_model.save_meal_plan(user_profile.get('user_id'), meal_plan)

            return jsonify({
                'success': True,
                'meal_plan': meal_plan,
                'meal_id': meal_id
            })
        except Exception as e:
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500

    def get_meal_history(self, user_id):
        """Get meal history for a user"""
        try:
            history = self.meal_model.get_meal_history(user_id)
            return jsonify({
                'success': True,
                'history': history
            })
        except Exception as e:
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500