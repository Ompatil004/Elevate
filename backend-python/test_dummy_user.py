import sys
import json
import asyncio
from datetime import datetime
from bson import ObjectId

# Setup imports
from app.workout_engine import WorkoutEngine
from app.nutrition_engine.engine import NutritionEngineV6
from app.workout_rules import load_workout_rules
import yaml

def test_generation():
    print("Initializing Engines...")
    workout_engine = WorkoutEngine()
    meal_engine = NutritionEngineV6()
    
    dummy_profile = {
        'user_id': str(ObjectId()),
        'age': 65,  # Senior
        'weight': 80,
        'height': 175,
        'gender': 'Male',
        'goal': 'Weight Loss',
        'activity_level': 'Light',
        'experience': 'Beginner',
        'days_per_week': 3,
        'equipment': ['Body Weight', 'Dumbbell'],
        'body_issues': ['lower back'],  # Should trigger back_pain filter
        'medical_conditions': ['Type 2 Diabetes'], # Should trigger carb limit
        'streak': 0,
        'consistency': 0,
        'week_offset': int(datetime.utcnow().strftime("%Y%W")),
        'dietary_preference': 'nonveg',
        'allergies': []
    }

    print("\n" + "="*50)
    print("DUMMY PROFILE")
    print("="*50)
    print(json.dumps(dummy_profile, indent=2))

    print("\n" + "="*50)
    print("TESTING NUTRITION ENGINE")
    print("="*50)
    
    try:
        meal_plan = meal_engine.generate_weekly_plan(dummy_profile)
        print("\nNutrition Plan generated successfully!")
        
        # Check safety fields
        print(f"Medical Adjustments Applied: {meal_plan.get('medical_adjustments_applied', [])}")
        if meal_plan.get('medical_disclaimer'):
            print(f"Medical Disclaimer: {meal_plan.get('medical_disclaimer')}")
            
        print("\nDaily Targets for Monday:")
        monday_plan = meal_plan['plan'].get('Monday', {})
        print(json.dumps(meal_plan['daily_targets'], indent=2))
        
    except Exception as e:
        print(f"Error generating meal plan: {e}")

    print("\n" + "="*50)
    print("TESTING WORKOUT ENGINE (with safety_layer)")
    print("="*50)
    
    try:
        # Load rules and validate safety
        workout_rules = load_workout_rules()
        from app.safety_layer import validate_workout_safety
        
        weekly_workout_plan = workout_engine.generate_weekly_plan(dummy_profile)
        print("\nBase Workout Plan generated successfully!")
        
        validated_plan, adjustments, warnings = validate_workout_safety(
            weekly_workout_plan, 
            dummy_profile, 
            workout_rules, 
            workout_engine
        )
        
        print(f"\nMedical Adjustments Applied: {adjustments}")
        print(f"Warnings: {warnings}")
        
        # Let's inspect the first workout day
        workout_days = [d for d in validated_plan if d.get('type') == 'workout']
        if workout_days:
            first_day = workout_days[0]
            print(f"\nFirst Workout Day ({first_day['day']}):")
            print(f"Intensity: {first_day.get('intensity')}")
            print(f"Exercises ({len(first_day.get('exercises', []))} total):")
            for ex in first_day.get('exercises', [])[:3]:
                print(f"  - {ex['name']} | Sets: {ex.get('sets')} | Reps: {ex.get('reps')} | Rest: {ex.get('rest')}")
            if len(first_day.get('exercises', [])) > 3:
                print("  - ...")
        
    except Exception as e:
        print(f"Error generating workout plan: {e}")

if __name__ == '__main__':
    test_generation()
