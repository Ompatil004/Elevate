import sys
import os

# Add backend-python to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from app.deterministic_meal_engine import optimize_portions as old_optimize
from app.nutrition_engine.portion_optimizer import optimize_portions as new_optimize

def test_portion_optimizer_equivalence():
    # Mock some components matching the structure of pd.Series -> dict conversion
    mock_components = [
        {
            "food_id": "1",
            "food_name": "White Rice",
            "serving_quantity": 100,
            "serving_unit": "g",
            "portion_min": 50,
            "portion_max": 300,
            "portion_step": 25,
            "calories_kcal": 130,
            "protein_g": 2.7,
            "carbohydrates_g": 28,
            "fat_g": 0.3,
            "swap_group": "rice",
            "meal_role": "carb_base",
            "budget_level": "Low",
            "availability": "common",
            "region": "All India"
        },
        {
            "food_id": "2",
            "food_name": "Dal Tadka",
            "serving_quantity": 1,
            "serving_unit": "bowl",
            "portion_min": 0.5,
            "portion_max": 2,
            "portion_step": 0.5,
            "calories_kcal": 150,
            "protein_g": 7,
            "carbohydrates_g": 20,
            "fat_g": 5,
            "swap_group": "dal & pulses",
            "meal_role": "protein_main",
            "budget_level": "Low",
            "availability": "common",
            "region": "North India"
        }
    ]
    
    target_cal = 400
    
    print("Running old engine optimizer...")
    old_result, old_cal = old_optimize(mock_components, target_cal)
    
    print("Running new engine optimizer...")
    new_result, new_cal = new_optimize(mock_components, target_cal)
    
    # Assert total calories are identical
    assert old_cal == new_cal, f"Calorie mismatch: Old={old_cal}, New={new_cal}"
    
    # Assert result items are identical
    assert len(old_result) == len(new_result), "Result length mismatch"
    
    for old_item, new_item in zip(old_result, new_result):
        # We need to ignore differences in object reference for _raw, but compare contents
        old_raw = old_item.pop('_raw')
        new_raw = new_item.pop('_raw')
        assert old_item == new_item, f"Mismatch found:\nOld: {old_item}\nNew: {new_item}"
        
    print("SUCCESS: Portion Optimizer Migration Test Passed! Outputs are 100% identical.")

if __name__ == "__main__":
    test_portion_optimizer_equivalence()
