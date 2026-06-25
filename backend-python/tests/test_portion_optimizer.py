import sys
import os

# Add backend-python to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.nutrition_engine.portion_optimizer import PortionOptimizer

def test_portion_optimizer_basic():
    optimizer = PortionOptimizer()
    
    mock_components = [
        {
            "food_id": "1",
            "food_name": "White Rice",
            "servings": {
                "typical": 100.0,
                "unit": "g",
                "minimum": 50.0,
                "maximum": 300.0,
            },
            "nutrition": {
                "calories": 130.0,
                "protein": 2.7,
                "carbs": 28.0,
                "fat": 0.3,
                "fiber": 0.4
            },
            "semantics": {
                "category": "Rice",
                "meal_role": "carb_base",
                "internal_ratio": 100.0,
                "protein_density": 0.08
            }
        },
        {
            "food_id": "2",
            "food_name": "Paneer Tikka",
            "servings": {
                "typical": 100.0,
                "unit": "g",
                "minimum": 50.0,
                "maximum": 250.0,
            },
            "nutrition": {
                "calories": 250.0,
                "protein": 18.0,
                "carbs": 5.0,
                "fat": 17.0,
                "fiber": 1.0
            },
            "semantics": {
                "category": "Paneer & Tofu",
                "meal_role": "protein_main",
                "internal_ratio": 100.0,
                "protein_density": 0.28
            }
        }
    ]
    
    target_macros = {
        "calories": 500,
        "protein": 25
    }
    
    result = optimizer.optimize_portions(mock_components, target_macros)
    
    assert len(result) == 2, "Should return 2 components"
    
    total_cal = sum(item["nutrition"]["calories"] for item in result)
    total_pro = sum(item["nutrition"]["protein"] for item in result)
    
    # Assert macros are optimized reasonably close to target
    assert 400 <= total_cal <= 600, f"Calorie optimized {total_cal} is not close to target 500"
    assert 18 <= total_pro <= 35, f"Protein optimized {total_pro} is not close to target 25"
    
    # Assert portion limits are respected
    for item in result:
        qty = item["serving_qty"]
        if item["food_id"] == "1":
            assert 50 <= qty <= 300, f"White Rice quantity {qty} out of bounds [50, 300]"
        elif item["food_id"] == "2":
            assert 50 <= qty <= 250, f"Paneer Tikka quantity {qty} out of bounds [50, 250]"

def test_portion_optimizer_salad_cap():
    optimizer = PortionOptimizer()
    
    mock_components = [
        {
            "food_id": "3",
            "food_name": "Onion Cucumber Raita",
            "servings": {
                "typical": 1.0,
                "unit": "bowl",
                "minimum": 0.5,
                "maximum": 2.0,
            },
            "nutrition": {
                "calories": 80.0,
                "protein": 3.0,
                "carbs": 8.0,
                "fat": 4.0,
                "fiber": 1.0
            },
            "semantics": {
                "category": "Dairy",
                "meal_role": "dairy_side",
                "internal_ratio": 1.0,
                "protein_density": 0.15
            }
        }
    ]
    
    # Raita is capped at 100 calories or 1.5 bowls by portion optimizer rules
    target_macros = {
        "calories": 500,
        "protein": 30
    }
    
    result = optimizer.optimize_portions(mock_components, target_macros)
    
    assert len(result) == 1
    raita_item = result[0]
    assert raita_item["nutrition"]["calories"] <= 120, f"Raita calories {raita_item['nutrition']['calories']} exceeded cap limit"
    assert raita_item["serving_qty"] <= 1.5, f"Raita quantity {raita_item['serving_qty']} exceeded salad cap limit"

if __name__ == "__main__":
    test_portion_optimizer_basic()
    test_portion_optimizer_salad_cap()
    print("All Portion Optimizer tests passed!")
