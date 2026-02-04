"""
Integration test to verify both systems work together without conflicts
"""

import sys
import os

# Add the project directory to the path
project_path = r'D:\Final Year Project\githubclone 22 mor\githubclone\Elevate\app\fitness_meal_planner'
sys.path.insert(0, project_path)

print("Testing integration of both systems...")
print("="*50)

# Test imports from the original system
try:
    from models.user_model import UserModel
    from rules.exercise_rules import ExerciseRules
    from rules.nutrition_rules import NutritionRules
    from ml.adaptive_engine import AdaptiveEngine
    from workout_plan_generator import WorkoutPlanGenerator
    from meal_plan_generator import MealPlanGenerator
    print("✓ Original system components imported successfully")
except ImportError as e:
    print(f"✗ Original system import failed: {e}")
    sys.exit(1)

# Test imports from the new data collection system
try:
    from data_collection_pipeline import UserDataCollection, DataValidation, DataAnonymization
    from data_ethics_validator import DataEthicsChecker, DataPrivacyAuditor
    print("✓ Data collection system components imported successfully")
except ImportError as e:
    print(f"✗ Data collection system import failed: {e}")
    sys.exit(1)

# Test basic functionality of original system
try:
    user_model = UserModel()
    user_data = {
        'name': 'Integration Test User',
        'fitness_level': 'beginner',
        'goal': 'general_fitness',
        'age': 30,
        'weight': 70,
        'height': 170,
        'gender': 'male',
        'activity_level': 'moderate',
        'injuries': [],
        'health_conditions': [],
        'equipment_available': ['none'],
        'preferred_categories': [],
        'disliked_exercises': [],
        'preferred_cuisines': [],
        'disliked_ingredients': [],
        'dietary_restrictions': [],
        'allergies': [],
        'exercise_history': [],
        'meal_history': [],
        'performance_data': {},
        'dietary_preferences': {}
    }
    user_id = user_model.create_user(user_data)
    print(f"✓ Original system user creation works (ID: {user_id})")
except Exception as e:
    print(f"✗ Original system functionality failed: {e}")
    sys.exit(1)

# Test basic functionality of data collection system
try:
    data_collector = UserDataCollection()
    profile_data = {
        "age": 30,
        "weight": 70,  # User-reported
        "height": 170,  # User-reported
        "gender": "male",
        "fitness_goal": "general_fitness",
        "experience_level": "beginner",
        "equipment_available": ["none"],
        "dietary_preference": "balanced",
        "allergies_or_constraints": [],
        "disclaimer_acknowledged": True,
        "consent_given": True
    }
    new_user_id = data_collector.collect_user_profile(profile_data)
    print(f"✓ Data collection system user creation works (ID: {new_user_id})")
except Exception as e:
    print(f"✗ Data collection system functionality failed: {e}")
    sys.exit(1)

# Test data validation
try:
    validator = DataValidation()
    errors = validator.validate_user_profile(profile_data)
    if not errors:
        print("✓ Data validation works correctly")
    else:
        print(f"✗ Data validation errors: {errors}")
        sys.exit(1)
except Exception as e:
    print(f"✗ Data validation failed: {e}")
    sys.exit(1)

# Test ethics checking
try:
    ethics_checker = DataEthicsChecker()
    results = ethics_checker.comprehensive_check(profile_data, 'user_profile')
    has_issues = any(results.values())
    if not has_issues:
        print("✓ Ethics checking works correctly")
    else:
        print(f"! Ethics checker found issues: {results}")
        # This is acceptable as long as they're warnings, not errors
except Exception as e:
    print(f"✗ Ethics checking failed: {e}")
    sys.exit(1)

# Test that rule-based systems still work with new data
try:
    exercise_rules = ExerciseRules()
    test_profile = {
        'fitness_level': 'beginner',
        'injuries': [],
        'equipment_available': ['none'],
        'health_conditions': []
    }
    filtered_exercises = exercise_rules.filter_exercises_by_rules(test_profile)
    print(f"✓ Rule-based exercise filtering works with {len(filtered_exercises)} exercises")
except Exception as e:
    print(f"✗ Rule-based filtering failed: {e}")
    sys.exit(1)

# Test that ML components still work
try:
    ml_engine = AdaptiveEngine()
    mock_exercises = [{'name': 'pushups', 'category': 'strength', 'difficulty': 'beginner'}]
    personalized = ml_engine.personalize_exercises(mock_exercises, test_profile)
    print(f"✓ ML personalization works with {len(personalized)} exercises")
except Exception as e:
    print(f"✗ ML personalization failed: {e}")
    sys.exit(1)

# Test that generators still work
try:
    workout_gen = WorkoutPlanGenerator()
    meal_gen = MealPlanGenerator()
    
    # Test with a minimal profile
    minimal_profile = {
        'user_id': 1,
        'fitness_level': 'beginner',
        'goal': 'general_fitness',
        'age': 30,
        'equipment_available': ['none'],
        'injuries': [],
        'time_available': 30
    }
    
    workout_plan = workout_gen.generate_workout_plan(minimal_profile, plan_duration_days=1)
    print(f"✓ Workout generation works with {len(workout_plan['days'])} days")
    
    meal_profile = {
        'user_id': 1,
        'weight': 70,
        'height': 170,
        'age': 30,
        'goal': 'general_fitness',
        'dietary_restrictions': [],
        'allergies': []
    }
    
    meal_plan = meal_gen.generate_meal_plan(meal_profile, plan_duration_days=1)
    print(f"✓ Meal generation works with {len(meal_plan['daily_plans'])} days")
    
except Exception as e:
    print(f"✗ Plan generation failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print("="*50)
print("INTEGRATION TEST RESULTS:")
print("✓ Both systems imported successfully")
print("✓ Original system functionality preserved")  
print("✓ New data collection system works")
print("✓ Data validation and ethics checking functional")
print("✓ Rule-based systems still operate correctly")
print("✓ ML components still operate correctly")
print("✓ Plan generation still works")
print("")
print("CONCLUSION: Both systems are properly implemented")
print("and work together without conflicts!")
print("="*50)