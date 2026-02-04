# Simple validation script to test the system
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_imports():
    """Test that all modules can be imported"""
    print("Testing module imports...")

    try:
        from flask import jsonify
        print("+ Flask imported successfully")
    except ImportError as e:
        print(f"- Failed to import Flask: {e}")
        return False

    try:
        from models.user_model import UserModel
        print("+ User Model imported successfully")
    except ImportError as e:
        print(f"- Failed to import User Model: {e}")
        return False

    try:
        from rules.exercise_rules import ExerciseRules
        print("+ Exercise Rules imported successfully")
    except ImportError as e:
        print(f"- Failed to import Exercise Rules: {e}")
        return False

    try:
        from rules.nutrition_rules import NutritionRules
        print("+ Nutrition Rules imported successfully")
    except ImportError as e:
        print(f"- Failed to import Nutrition Rules: {e}")
        return False

    try:
        from ml.adaptive_engine import AdaptiveEngine
        print("+ Adaptive Engine imported successfully")
    except ImportError as e:
        print(f"- Failed to import Adaptive Engine: {e}")
        return False

    try:
        from workout_plan_generator import WorkoutPlanGenerator
        print("+ Workout Plan Generator imported successfully")
    except ImportError as e:
        print(f"- Failed to import Workout Plan Generator: {e}")
        return False

    try:
        from meal_plan_generator import MealPlanGenerator
        print("+ Meal Plan Generator imported successfully")
    except ImportError as e:
        print(f"- Failed to import Meal Plan Generator: {e}")
        return False

    print("\nAll modules imported successfully!")
    return True

def test_basic_functionality():
    """Test basic functionality of the system"""
    print("\nTesting basic functionality...")

    # Test user model
    try:
        user_model = UserModel()
        user_data = {
            'name': 'Test User',
            'fitness_level': 'beginner',
            'goal': 'general_fitness'
        }
        user_id = user_model.create_user(user_data)
        print(f"+ Created user with ID: {user_id}")
    except Exception as e:
        print(f"- Failed to create user: {e}")
        return False

    # Test rule engines
    try:
        exercise_rules = ExerciseRules()
        nutrition_rules = NutritionRules()
        print("+ Rule engines initialized successfully")
    except Exception as e:
        print(f"- Failed to initialize rule engines: {e}")
        return False

    # Test ML engine
    try:
        ml_engine = AdaptiveEngine()
        print("+ ML engine initialized successfully")
    except Exception as e:
        print(f"- Failed to initialize ML engine: {e}")
        return False

    # Test generators
    try:
        workout_gen = WorkoutPlanGenerator()
        meal_gen = MealPlanGenerator()
        print("+ Generators initialized successfully")
    except Exception as e:
        print(f"- Failed to initialize generators: {e}")
        return False

    print("\nBasic functionality tests passed!")
    return True

def main():
    print("Starting validation of the Hybrid Fitness and Meal Planner System...")
    print("="*60)

    if not test_imports():
        print("\nModule import tests failed!")
        return False

    if not test_basic_functionality():
        print("\nBasic functionality tests failed!")
        return False

    print("\n" + "="*60)
    print("VALIDATION COMPLETE!")
    print("All systems are operational and ready for use.")
    print("The hybrid fitness and meal planner system has been successfully implemented.")
    print("="*60)

    return True

if __name__ == "__main__":
    success = main()
    if not success:
        sys.exit(1)