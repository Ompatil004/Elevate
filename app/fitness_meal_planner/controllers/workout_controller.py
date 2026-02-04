"""
Workout Controller for generating workout plans
"""

from flask import jsonify
from rules.exercise_rules import ExerciseRules
from ml.adaptive_engine import AdaptiveEngine
from models.workout_model import WorkoutModel
from workout_plan_generator import WorkoutPlanGenerator


class WorkoutController:
    def __init__(self):
        self.exercise_rules = ExerciseRules()
        self.adaptive_engine = AdaptiveEngine()
        self.workout_model = WorkoutModel()
        self.plan_generator = WorkoutPlanGenerator()

    def generate_workout_plan(self, request_data):
        """Generate a personalized workout plan based on user profile"""
        try:
            user_profile = request_data.get('user_profile', {})

            # Use the workout plan generator to create a comprehensive plan
            workout_plan = self.plan_generator.generate_workout_plan(user_profile)

            # Save workout plan
            workout_id = self.workout_model.save_workout_plan(user_profile.get('user_id'), workout_plan)

            return jsonify({
                'success': True,
                'workout_plan': workout_plan,
                'workout_id': workout_id
            })
        except Exception as e:
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500

    def get_workout_history(self, user_id):
        """Get workout history for a user"""
        try:
            history = self.workout_model.get_workout_history(user_id)
            return jsonify({
                'success': True,
                'history': history
            })
        except Exception as e:
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500