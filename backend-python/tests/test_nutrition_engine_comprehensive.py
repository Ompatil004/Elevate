import pytest
import time
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from app.deterministic_meal_engine import MealEngine

@pytest.fixture(scope="module")
def engine():
    return MealEngine()

def test_nutrition_targets_weight_loss(engine):
    profile = {'age': 30, 'weight': 80, 'height': 170, 'gender': 'Male', 'goal': 'Weight Loss', 'activity_level': 'Light'}
    targets = engine.calculate_daily_targets(profile)
    # BMR = 10*80 + 6.25*170 - 5*30 + 5 = 800 + 1062.5 - 150 + 5 = 1717.5
    # TDEE = 1717.5 * 1.375 = 2361.56
    # Weight Loss Goal Mult = 0.85
    # Kcal = 2361.56 * 0.85 = 2007.3
    assert abs(targets['daily_calories'] - 2007) <= 50

def test_nutrition_targets_maintenance(engine):
    profile = {'age': 30, 'weight': 70, 'height': 175, 'gender': 'Male', 'goal': 'Maintenance', 'activity_level': 'Moderate'}
    targets = engine.calculate_daily_targets(profile)
    # BMR = 10*70 + 6.25*175 - 5*30 + 5 = 700 + 1093.75 - 150 + 5 = 1648.75
    # TDEE = 1648.75 * 1.55 = 2555.56
    # Maintenance Goal Mult = 1.00
    # Kcal = 2555.56
    assert abs(targets['daily_calories'] - 2556) <= 50

def test_nutrition_targets_muscle_gain(engine):
    profile = {'age': 30, 'weight': 60, 'height': 160, 'gender': 'Male', 'goal': 'Muscle Gain', 'activity_level': 'Active'}
    targets = engine.calculate_daily_targets(profile)
    # BMR = 10*60 + 6.25*160 - 5*30 + 5 = 600 + 1000 - 150 + 5 = 1455
    # TDEE = 1455 * 1.725 = 2509.875
    # Muscle Gain Goal Mult = 1.10
    # Kcal = 2509.875 * 1.10 = 2760.86
    assert abs(targets['daily_calories'] - 2761) <= 50

def test_diet_and_allergies(engine):
    profiles = [
        {'dietary_preference': 'veg', 'allergies': ['Egg']},
        {'dietary_preference': 'vegan', 'allergies': ['Milk']},
        {'dietary_preference': 'nonveg', 'allergies': ['Nuts', 'Gluten']}
    ]
    for p in profiles:
        prof = {'age': 25, 'weight': 70, 'height': 175, 'gender': 'Male', 'goal': 'Maintenance'}
        prof.update(p)
        plan = engine.generate_weekly_plan(prof)
        
        for day, meals in plan['plan'].items():
            for mt, items in meals.items():
                for item in items:
                    name_lower = item.get('food_name', '').lower()
                    
                    if 'Egg' in prof['allergies']:
                        assert 'egg' not in name_lower
                    if 'Milk' in prof['allergies']:
                        assert 'milk' not in name_lower and 'paneer' not in name_lower
                    if 'Nuts' in prof['allergies']:
                        assert 'nut' not in name_lower
                    if 'Gluten' in prof['allergies']:
                        assert 'wheat' not in name_lower and 'roti' not in name_lower and 'bread' not in name_lower

def test_meal_quality_and_duplicates(engine):
    prof = {'age': 25, 'weight': 70, 'height': 175, 'gender': 'Male', 'goal': 'Maintenance', 'dietary_preference': 'nonveg'}
    plan = engine.generate_weekly_plan(prof)
    
    breakfasts = set()
    lunches = set()
    dinners = set()
    
    for day, meals in plan['plan'].items():
        # Completeness Check
        for mt in ['breakfast', 'lunch', 'dinner']:
            if mt in meals:
                roles = [i.get('meal_role') for i in meals[mt]]
                has_protein = 'protein_main' in roles or 'combo_meal' in roles
                has_carb = 'carb_base' in roles or 'combo_meal' in roles
                assert has_protein, f"{day} {mt} lacks protein. Roles: {roles}"
                assert has_carb, f"{day} {mt} lacks carb. Roles: {roles}"
        
        # Track duplicates
        if 'breakfast' in meals:
            b_names = tuple(sorted(i.get('food_name', '') for i in meals['breakfast']))
            assert b_names not in breakfasts, f"Duplicate breakfast: {b_names}"
            breakfasts.add(b_names)
        if 'lunch' in meals:
            l_names = tuple(sorted(i.get('food_name', '') for i in meals['lunch']))
            assert l_names not in lunches, f"Duplicate lunch: {l_names}"
            lunches.add(l_names)
        if 'dinner' in meals:
            d_names = tuple(sorted(i.get('food_name', '') for i in meals['dinner']))
            assert d_names not in dinners, f"Duplicate dinner: {d_names}"
            dinners.add(d_names)
            
        # Realistic portions
        for mt, items in meals.items():
            for it in items:
                qty = it.get('serving_qty', 1)
                unit = it.get('serving_unit', '').lower()
                if unit in ('piece', 'pieces', 'unit'):
                    assert qty <= 5, f"Unrealistic portion {qty} pieces for {it.get('food_name', '')}"
                elif unit in ('g', 'ml'):
                    assert qty <= 600, f"Unrealistic portion {qty} {unit} for {it.get('food_name', '')}"

def test_performance(engine):
    prof = {'age': 25, 'weight': 70, 'height': 175, 'gender': 'Male', 'goal': 'Maintenance', 'dietary_preference': 'nonveg'}
    start = time.time()
    plan = engine.generate_weekly_plan(prof)
    elapsed = time.time() - start
    assert elapsed < 15.0, f"Performance failed: generation took {elapsed:.2f} seconds"
