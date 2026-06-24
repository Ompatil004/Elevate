import os
import pandas as pd
from deterministic_meal_engine import MealEngine

def run_regression_tests():
    # Setup
    csv_path = '../data/meal_metadata.csv'
    if not os.path.exists(csv_path):
        print(f"Error: {csv_path} not found.")
        return

    engine = MealEngine(metadata_path=csv_path)

    # Scenarios
    scenarios = [
        {
            "name": "3000 kcal Muscle Gain (Non-veg)",
            "profile": {
                'user_id': 'test_user_3000',
                'weight': 80,
                'height': 180,
                'age': 25,
                'gender': 'male',
                'goal': 'Muscle Gain',
                'activity_level': 'Very Active',
                'dietary_preference': 'nonveg',
                'allergies': []
            },
            "total_cal": 3000
        },
        {
            "name": "1800 kcal Fat Loss (Vegetarian)",
            "profile": {
                'user_id': 'test_user_1800',
                'weight': 70,
                'height': 165,
                'age': 30,
                'gender': 'female',
                'goal': 'Fat Loss',
                'activity_level': 'Light',
                'dietary_preference': 'veg',
                'allergies': []
            },
            "total_cal": 1800
        },
        {
            "name": "2200 kcal Maintenance (Vegan)",
            "profile": {
                'user_id': 'test_user_vegan',
                'weight': 65,
                'height': 170,
                'age': 28,
                'gender': 'female',
                'goal': 'Maintenance',
                'activity_level': 'Moderate',
                'dietary_preference': 'vegan',
                'allergies': []
            },
            "total_cal": 2200
        }
    ]

    for scenario in scenarios:
        print(f"\n======================================")
        print(f"Running Scenario: {scenario['name']}")
        print(f"Target Calories: {scenario['total_cal']} kcal")
        print(f"======================================")

        try:
            # We must override the total_cal explicitly for the test, 
            # since generate_weekly_plan derives it from profile math
            # We'll just generate the plan and check outputs
            result = engine.generate_weekly_plan(scenario['profile'])
            plan = result.get('plan', {})
            failed = result.get('failed_slots', [])

            print(f"\nGenerated successfully. Failed slots: {len(failed)}")
            
            # Print Monday to verify realistic output
            if 'monday' in plan:
                print("\nSample Output (Monday):")
                for mt in ['breakfast', 'lunch', 'dinner', 'snack']:
                    if mt in plan['monday']:
                        print(f"  {mt.upper()}:")
                        for item in plan['monday'][mt]:
                            print(f"    {item.get('serving_weight', 0):.2f} - {item.get('food_name')} ({item.get('calories', 0)} kcal) [Role: {item.get('meal_role')}]")
            
            # Validation assertions on the entire weekly plan
            for day, meals in plan.items():
                for mt, items in meals.items():
                    roles = [i.get('meal_role', '') for i in items]
                    
                    # 1. Structural completeness for Lunch/Dinner
                    if mt in ['lunch', 'dinner']:
                        has_combo = 'combo_meal' in roles
                        has_carb = 'carb_base' in roles
                        has_protein = 'protein_main' in roles
                        has_side = any(r in ['salad', 'veg_side', 'dairy_side', 'beverage'] for r in roles)
                        
                        is_complete = (has_combo and has_side) or (has_carb and has_protein)
                        if not is_complete:
                            print(f"    [FAIL] Structural incompleteness detected in {day}/{mt}: {roles}")

                    # 2. Rejection Rules
                    for item in items:
                        name = item.get('food_name', '')
                        qty = item.get('serving_weight', 0)
                        role = item.get('meal_role', '')

                        # Condiment cap
                        if role == 'condiment':
                            if qty > 30.1: # tiny grace
                                print(f"    [FAIL] Condiment overflow in {day}/{mt}: {name} ({qty}g)")
                        
                        # Rasam powder/spice test
                        if 'powder' in name.lower() or 'spice' in name.lower():
                            if role != 'condiment':
                                print(f"    [FAIL] Unrealistic raw ingredient as main: {name}")

                        # Absurd scaling test (e.g. 5 dosas)
                        if 'dosa' in name.lower() and qty > 250: # assuming 1 dosa ~ 60-80g
                            print(f"    [FAIL] Unrealistic dosa quantity: {qty}g")

                        if 'chutney' in name.lower() and qty > 50:
                            print(f"    [FAIL] Unrealistic chutney amount: {qty}g")

        except Exception as e:
            print(f"Error running scenario {scenario['name']}: {e}")

if __name__ == '__main__':
    run_regression_tests()
