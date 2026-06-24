import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

from deterministic_meal_engine import MealEngine

def test_engine():
    engine = MealEngine()
    
    profiles = [
        {'age': 30, 'weight': 80, 'height': 180, 'gender': 'Male', 'goal': 'Weight Loss', 'dietary_preference': 'nonveg'},
        {'age': 25, 'weight': 55, 'height': 160, 'gender': 'Female', 'goal': 'Maintenance', 'dietary_preference': 'veg'},
        {'age': 40, 'weight': 90, 'height': 175, 'gender': 'Male', 'goal': 'Muscle Gain', 'dietary_preference': 'vegan'}
    ]
    
    print("Running 5 tests...")
    
    for i in range(5):
        # vary the profile slightly to get new plans
        profile = profiles[i % len(profiles)]
        if (i+1) % 10 == 0:
            print(f"Completed {i+1}/100 tests...")
            
        profile['week_offset'] = i + 100  # just to force a new seed
        
        result = engine.generate_weekly_plan(profile)
        plan = result['plan']
        
        # Verify
        for day, meals in plan.items():
            for mt, items in meals.items():
                roles = [it.get('meal_role', '') for it in items]
                names = [it.get('food_name', '').lower() for it in items]
                
                # Check for desserts/spreads
                if set(roles) & {'dessert', 'spread', 'sauce', 'condiment', 'sweet'}:
                    print(f"FAILED: Found dessert/sauce in {day} {mt}: {names} ({roles})")
                    sys.exit(1)
                    
                # Check combo constraints
                if roles.count('combo_meal') > 1:
                    print(f"FAILED: Multiple combo meals in {day} {mt}: {names} ({roles})")
                    sys.exit(1)
                
                if roles.count('carb_base') > 1:
                    print(f"FAILED: Multiple carb bases in {day} {mt}: {names} ({roles})")
                    sys.exit(1)
                    
                if 'combo_meal' in roles and 'carb_base' in roles:
                    print(f"FAILED: Combo + Carb base in {day} {mt}: {names} ({roles})")
                    sys.exit(1)
                    
                if 'combo_meal' in roles and 'protein_main' in roles:
                    print(f"FAILED: Combo + Protein main in {day} {mt}: {names} ({roles})")
                    sys.exit(1)
                    
                # Check portion sizes
                for it in items:
                    qty = it.get('serving_qty', 1)
                    unit = it.get('serving_unit', '')
                    if unit in ('piece', 'pieces'):
                        if qty > 5:
                            print(f"FAILED: Unrealistic pieces for {it['food_name']}: {qty}")
                            sys.exit(1)
                    elif unit in ('g', 'ml'):
                        if qty > 600:
                            print(f"FAILED: Unrealistic weight/vol for {it['food_name']}: {qty}")
                            sys.exit(1)
                            
    print("All 100 tests passed. No unrealistic meals or portions found.")

if __name__ == '__main__':
    test_engine()
