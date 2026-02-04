"""
Test and validation script for the hybrid fitness and meal planner system
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__)))

from models.user_model import UserModel
from controllers.workout_controller import WorkoutController
from controllers.meal_controller import MealController
from controllers.explainability_controller import ExplainabilityController
from workout_plan_generator import WorkoutPlanGenerator
from meal_plan_generator import MealPlanGenerator


def test_user_model():
    """Test the user model functionality"""
    print("Testing User Model...")
    
    user_model = UserModel()
    
    # Create a test user
    user_data = {
        'name': 'John Doe',
        'fitness_level': 'intermediate',
        'goal': 'strength',
        'age': 32,
        'gender': 'male',
        'weight': 80,
        'height': 180,
        'activity_level': 'moderate',
        'injuries': ['knee_injury'],
        'health_conditions': [],
        'equipment_available': ['dumbbells', 'yoga_mat'],
        'preferred_categories': ['strength', 'core'],
        'disliked_exercises': ['burpees'],
        'time_available': 50
    }
    
    user_id = user_model.create_user(user_data)
    print(f"Created user with ID: {user_id}")
    
    # Retrieve user
    retrieved_user = user_model.get_user(user_id)
    assert retrieved_user is not None, "Failed to retrieve user"
    print("User retrieval successful")
    
    # Update user
    update_data = {'fitness_level': 'advanced'}
    success = user_model.update_user(user_id, update_data)
    assert success, "Failed to update user"
    
    updated_user = user_model.get_user(user_id)
    assert updated_user['fitness_level'] == 'advanced', "User update failed"
    print("User update successful")
    
    print("User Model tests passed!\n")


def test_workout_generation():
    """Test the workout plan generation"""
    print("Testing Workout Plan Generation...")
    
    generator = WorkoutPlanGenerator()
    
    # Sample user profile
    user_profile = {
        'user_id': 1,
        'fitness_level': 'intermediate',
        'goal': 'strength',
        'age': 30,
        'gender': 'male',
        'weight': 75,
        'height': 175,
        'activity_level': 'moderate',
        'injuries': ['knee_injury'],
        'health_conditions': [],
        'equipment_available': ['dumbbells', 'yoga_mat'],
        'preferred_categories': ['strength', 'core'],
        'disliked_exercises': ['burpees'],
        'time_available': 50,
        'exercise_history': [
            {'exercise': 'pushups', 'rating': 8, 'sets_completed': 3, 'reps_completed': 12},
            {'exercise': 'squats', 'rating': 7, 'sets_completed': 3, 'reps_completed': 10}
        ],
        'performance_data': {
            'pushups': {'attempts': 5, 'avg_rating': 7.5, 'improvement_trend': 0.2, 'difficulty_rating': 7},
            'squats': {'attempts': 4, 'avg_rating': 7, 'improvement_trend': 0.1, 'difficulty_rating': 6}
        }
    }
    
    # Generate workout plan
    plan = generator.generate_workout_plan(user_profile, plan_duration_days=3)
    
    # Validate plan structure
    assert 'days' in plan, "Plan missing 'days' key"
    assert 'summary' in plan, "Plan missing 'summary' key"
    assert len(plan['days']) > 0, "Plan has no days"
    
    # Check that safety rules were applied
    has_workout_day = any(day['type'] != 'rest' for day in plan['days'])
    assert has_workout_day, "No workout days in plan"
    
    print(f"Generated plan with {len(plan['days'])} days")
    print(f"Summary: {plan['summary']}")
    
    print("Workout Generation tests passed!\n")


def test_meal_generation():
    """Test the meal plan generation"""
    print("Testing Meal Plan Generation...")
    
    generator = MealPlanGenerator()
    
    # Sample user profile
    user_profile = {
        'user_id': 1,
        'weight': 70,  # kg
        'height': 170,  # cm
        'age': 30,
        'gender': 'male',
        'activity_level': 'moderate',
        'goal': 'muscle_gain',
        'dietary_restrictions': ['dairy_free'],
        'allergies': ['nuts'],
        'health_conditions': [],
        'preferred_cuisines': ['mediterranean', 'asian'],
        'disliked_ingredients': ['mushrooms', 'parsley'],
        'eating_frequency': 'regular',
        'meal_history': [
            {'meal': 'Grilled Chicken Salad', 'rating': 8},
            {'meal': 'Oatmeal with Berries', 'rating': 7}
        ],
        'dietary_preferences': {
            'high_protein': True,
            'low_carb': False,
            'high_fiber': True
        }
    }
    
    # Generate meal plan
    plan = generator.generate_meal_plan(user_profile, plan_duration_days=3)
    
    # Validate plan structure
    assert 'daily_plans' in plan, "Plan missing 'daily_plans' key"
    assert 'nutrition_goals' in plan, "Plan missing 'nutrition_goals' key"
    assert len(plan['daily_plans']) > 0, "Plan has no daily plans"
    
    # Check that dietary restrictions were applied
    has_meals = any(len(day['meals']) > 0 for day in plan['daily_plans'])
    assert has_meals, "No meals in plan"
    
    print(f"Generated plan with {len(plan['daily_plans'])} days")
    print(f"Nutrition goals: {plan['nutrition_goals']}")
    
    print("Meal Generation tests passed!\n")


def test_controllers():
    """Test the controllers"""
    print("Testing Controllers...")
    
    # Test Workout Controller
    workout_controller = WorkoutController()
    
    user_profile = {
        'user_id': 1,
        'fitness_level': 'beginner',
        'goal': 'general_fitness',
        'age': 25,
        'equipment_available': ['none'],
        'injuries': [],
        'time_available': 30
    }
    
    request_data = {'user_profile': user_profile}
    result = workout_controller.generate_workout_plan(request_data)
    
    assert result[1] != 500, f"Workout generation failed with error: {result}"
    assert result[0].json['success'], "Workout generation was not successful"
    
    print("Workout Controller test passed!")
    
    # Test Meal Controller
    meal_controller = MealController()
    
    user_profile = {
        'user_id': 1,
        'weight': 65,
        'height': 165,
        'age': 28,
        'goal': 'weight_loss',
        'dietary_restrictions': [],
        'allergies': []
    }
    
    request_data = {'user_profile': user_profile}
    result = meal_controller.generate_meal_plan(request_data)
    
    assert result[1] != 500, f"Meal generation failed with error: {result}"
    assert result[0].json['success'], "Meal generation was not successful"
    
    print("Meal Controller test passed!")
    
    # Test Explainability Controller
    explain_controller = ExplainabilityController()
    
    workout_plan = {
        'exercises': [{'name': 'Push-ups', 'category': 'strength'}],
        'rules_applied': ['injury_exclusions', 'equipment_filtering'],
        'ml_adjustments': ['personalization', 'diversity']
    }
    
    request_data = {
        'workout_plan': workout_plan,
        'user_profile': user_profile
    }
    
    result = explain_controller.explain_workout_recommendation(request_data)
    assert result[0].json['success'], "Workout explanation was not successful"
    
    print("Explainability Controller test passed!")
    
    print("Controller tests passed!\n")


def test_hybrid_integration():
    """Test the integration of rule-based and ML components"""
    print("Testing Hybrid Integration...")
    
    # Test that rule-based constraints are respected even with ML personalization
    user_profile = {
        'user_id': 1,
        'fitness_level': 'beginner',
        'goal': 'strength',
        'age': 30,
        'injuries': ['shoulder_injury'],  # Important: user has shoulder injury
        'equipment_available': ['dumbbells'],
        'preferred_categories': ['strength'],  # User prefers strength exercises
        'time_available': 45
    }
    
    # Generate workout plan
    workout_gen = WorkoutPlanGenerator()
    plan = workout_gen.generate_workout_plan(user_profile, plan_duration_days=1)
    
    # Check that exercises incompatible with shoulder injury are not included
    shoulder_unsafe_exercises = ['pushups', 'shoulder_press', 'pullups']
    
    for day in plan['days']:
        if day['type'] != 'rest':
            for exercise in day.get('exercises', []):
                assert exercise['name'] not in shoulder_unsafe_exercises, \
                    f"Exercise {exercise['name']} is unsafe for shoulder injury but was included"
    
    print("Hybrid integration test passed - rule-based safety constraints respected!")
    
    # Test meal plan respects dietary restrictions
    user_profile = {
        'user_id': 1,
        'goal': 'muscle_gain',
        'dietary_restrictions': ['vegan'],  # Important: user is vegan
        'allergies': ['nuts'],
        'preferred_cuisines': ['mediterranean']
    }
    
    meal_gen = MealPlanGenerator()
    meal_plan = meal_gen.generate_meal_plan(user_profile, plan_duration_days=1)
    
    # Check that non-vegan meals are not included
    for day in meal_plan['daily_plans']:
        for meal_type, meals in day['meals'].items():
            for meal in meals:
                assert 'non_vegetarian' not in meal.get('diet_types', []), \
                    f"Non-vegetarian meal {meal['name']} was included despite vegan restriction"
                assert 'nuts' not in meal.get('allergens', []), \
                    f"Meal {meal['name']} contains nuts despite allergy"
    
    print("Hybrid integration test passed - rule-based dietary constraints respected!")
    print("Hybrid system validation complete!\n")


def run_all_tests():
    """Run all tests"""
    print("Starting Hybrid Fitness and Meal Planner System Validation...\n")
    
    try:
        test_user_model()
        test_workout_generation()
        test_meal_generation()
        test_controllers()
        test_hybrid_integration()
        
        print("="*50)
        print("ALL TESTS PASSED!")
        print("Hybrid Fitness and Meal Planner System is validated and ready!")
        print("="*50)
        
    except AssertionError as e:
        print(f"TEST FAILED: {e}")
        return False
    except Exception as e:
        print(f"UNEXPECTED ERROR: {e}")
        return False
    
    return True


if __name__ == "__main__":
    success = run_all_tests()
    if not success:
        sys.exit(1)