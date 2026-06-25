import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from app.deterministic_meal_engine import WeeklyVarietyTracker as OldTracker
from app.nutrition_engine.variety_tracker import WeeklyVarietyTracker as NewTracker

def test_variety_tracker_equivalence():
    old_tracker = OldTracker()
    new_tracker = NewTracker()
    
    # Mock meals to record
    meal1 = [
        {"food_name": "Chicken Curry", "swap_group": "chicken/meat"},
        {"food_name": "White Rice", "swap_group": "rice"},
        {"food_name": "Cucumber Salad", "swap_group": "vegetable"}
    ]
    meal2 = [
        {"food_name": "Paneer Tikka", "swap_group": "paneer"},
        {"food_name": "Roti", "swap_group": "bread & roti"}
    ]
    meal3 = [
        {"food_name": "Dal Makhani", "swap_group": "dal & pulses"},
        {"food_name": "Jeera Rice", "swap_group": "rice"}
    ]
    
    # Record meals
    for tracker in (old_tracker, new_tracker):
        tracker.record_meal('lunch', meal1)
        tracker.record_cuisine('North India')
        tracker.record_template(1)
        
        tracker.record_meal('dinner', meal2)
        tracker.record_cuisine('North India')
        tracker.record_template(2)
        
        tracker.record_meal('lunch', meal3)
        tracker.record_cuisine('All India')
        tracker.record_template(1)
        
    # Assert Internal State Parity
    assert old_tracker.protein_history == new_tracker.protein_history
    assert old_tracker.carb_history == new_tracker.carb_history
    assert old_tracker.cuisine_history == new_tracker.cuisine_history
    assert old_tracker.template_history == new_tracker.template_history
    assert old_tracker.family_history == new_tracker.family_history
    assert old_tracker.lunch_history == new_tracker.lunch_history
    assert old_tracker.dinner_history == new_tracker.dinner_history

    # Scenario 1: Same food, same carb, same protein
    candidate_1 = [
        {"food_name": "Chicken Curry", "swap_group": "chicken/meat"},
        {"food_name": "Brown Rice", "swap_group": "rice"}
    ]
    old_pen_1 = old_tracker.variety_penalty('lunch', candidate_1, 1, 'North India')
    new_pen_1 = new_tracker.variety_penalty('lunch', candidate_1, 1, 'North India')
    assert old_pen_1 == new_pen_1, f"Penalty 1 mismatch: Old {old_pen_1} != New {new_pen_1}"
    
    # Scenario 2: Completely new food, different template, different cuisine
    candidate_2 = [
        {"food_name": "Fish Curry", "swap_group": "fish & seafood"},
        {"food_name": "Quinoa", "swap_group": "oats & cereals"}
    ]
    old_pen_2 = old_tracker.variety_penalty('dinner', candidate_2, 3, 'South India')
    new_pen_2 = new_tracker.variety_penalty('dinner', candidate_2, 3, 'South India')
    assert old_pen_2 == new_pen_2, f"Penalty 2 mismatch: Old {old_pen_2} != New {new_pen_2}"
    
    # Scenario 3: Breakfast repeat
    candidate_3 = [
        {"food_name": "Oats Porridge", "swap_group": "oats & cereals"}
    ]
    # Record it once
    old_tracker.record_meal('breakfast', candidate_3)
    new_tracker.record_meal('breakfast', candidate_3)
    
    # Check penalty for repeat
    old_pen_3 = old_tracker.variety_penalty('breakfast', candidate_3, 0, 'All India')
    new_pen_3 = new_tracker.variety_penalty('breakfast', candidate_3, 0, 'All India')
    assert old_pen_3 == new_pen_3, f"Penalty 3 mismatch: Old {old_pen_3} != New {new_pen_3}"
    
    print("SUCCESS: Weekly Variety Tracker outputs and states are 100% identical across all scenarios.")

if __name__ == "__main__":
    test_variety_tracker_equivalence()
