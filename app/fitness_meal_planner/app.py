"""
Main application file for the Hybrid Fitness and Meal Planner
This application implements a hybrid architecture with rule-based logic as the primary
decision maker and machine learning as secondary for adaptive personalization.
"""

from flask import Flask, request, jsonify, render_template
import os
from controllers.user_controller import UserController
from controllers.workout_controller import WorkoutController
from controllers.meal_controller import MealController
from controllers.explainability_controller import ExplainabilityController
from controllers.profile_controller import ProfileController


def create_app():
    app = Flask(__name__)

    # Initialize controllers
    user_controller = UserController()
    workout_controller = WorkoutController()
    meal_controller = MealController()
    explainability_controller = ExplainabilityController()
    profile_controller = ProfileController()
    
    # User routes
    @app.route('/api/user', methods=['POST'])
    def create_user():
        return user_controller.create_user(request.json)
    
    @app.route('/api/user/<int:user_id>', methods=['GET'])
    def get_user(user_id):
        return user_controller.get_user(user_id)
    
    @app.route('/api/user/<int:user_id>', methods=['PUT'])
    def update_user(user_id):
        return user_controller.update_user(user_id, request.json)

    @app.route('/api/profile/update', methods=['PUT'])
    def update_profile():
        """Update user profile and regenerate plans if needed"""
        try:
            user_data = request.json
            user_id = user_data.get('user_id')

            if not user_id:
                return jsonify({
                    'success': False,
                    'error': 'User ID is required'
                }), 400

            # Call profile controller to update profile and check for plan regeneration
            result = profile_controller.update_profile_and_regenerate_plans(user_id, user_data)
            return result
        except Exception as e:
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500
    
    # Workout routes
    @app.route('/api/workout/generate', methods=['POST'])
    def generate_workout():
        return workout_controller.generate_workout_plan(request.json)
    
    @app.route('/api/workout/<int:user_id>', methods=['GET'])
    def get_workout_history(user_id):
        return workout_controller.get_workout_history(user_id)
    
    # Meal routes
    @app.route('/api/meal/generate', methods=['POST'])
    def generate_meal_plan():
        return meal_controller.generate_meal_plan(request.json)
    
    @app.route('/api/meal/<int:user_id>', methods=['GET'])
    def get_meal_history(user_id):
        return meal_controller.get_meal_history(user_id)
    
    # Explainability routes
    @app.route('/api/explain/workout', methods=['POST'])
    def explain_workout():
        return explainability_controller.explain_workout_recommendation(request.json)
    
    @app.route('/api/explain/meal', methods=['POST'])
    def explain_meal():
        return explainability_controller.explain_meal_recommendation(request.json)
    
    # Frontend routes
    @app.route('/')
    def index():
        return render_template('index.html')
    
    @app.route('/dashboard')
    def dashboard():
        return render_template('dashboard.html')
    
    @app.route('/workout-planner')
    def workout_planner():
        return render_template('workout_planner.html')
    
    @app.route('/meal-planner')
    def meal_planner():
        return render_template('meal_planner.html')
    
    return app


if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, host='0.0.0.0', port=5000)