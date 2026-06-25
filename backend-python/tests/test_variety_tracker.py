import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.nutrition_engine.variety_tracker import WeeklyVarietyTracker

def test_variety_tracker_basic():
    tracker = WeeklyVarietyTracker()
    
    # Verify initial empty histories
    assert len(tracker.daily_cuisine_history) == 0
    assert len(tracker.protein_history) == 0
    
    # Record some meals
    tracker.record_meal_selection(
        meal_id="meal_1",
        foods=["Chicken Curry", "White Rice"],
        protein_source="chicken/meat",
        carb_source="rice",
        vegetables=[],
        day_num=1,
        cuisine="North Indian",
        cooking_style="Curry",
        meal_signature="protein_main-carb_base",
        food_ids=["chicken_curry_id", "white_rice_id"]
    )
    
    # Check that tracking works
    assert "chicken/meat" in tracker.protein_history
    assert "rice" in tracker.carb_history
    assert "North Indian" in tracker.daily_cuisine_history[1]
    
    # Calculate penalty for repeating cuisine
    # Note: calculate_variety_penalty penalizes recent items in item_history and family_history
    tracker.record_food("food_a", "Curry", 1)
    pen = tracker.calculate_variety_penalty("food_a", "Curry", 2)
    # Eaten 1 day ago (2 - 1 = 1 < 3), penalty should be >= 50
    assert pen >= 50, "Recent food repeat should trigger a variety penalty"

def test_variety_tracker_snapshot():
    tracker = WeeklyVarietyTracker()
    
    # Record a meal on day 1
    tracker.record_meal_selection(
        meal_id="meal_1",
        foods=["Chicken Curry"],
        protein_source="chicken/meat",
        carb_source="rice",
        vegetables=[],
        day_num=1,
        cuisine="North Indian",
        cooking_style="Curry",
        meal_signature="protein_main",
        food_ids=["chicken_curry_id"]
    )
    
    # Take a snapshot
    snapshot = tracker.get_snapshot()
    
    # Record another meal
    tracker.record_meal_selection(
        meal_id="meal_2",
        foods=["Fish Fry"],
        protein_source="fish/seafood",
        carb_source="rice",
        vegetables=[],
        day_num=1,
        cuisine="South Indian",
        cooking_style="Fried",
        meal_signature="protein_main",
        food_ids=["fish_fry_id"]
    )
    
    assert "fish/seafood" in tracker.protein_history
    
    # Restore the snapshot
    tracker.restore_snapshot(snapshot)
    
    # Check that fish is removed but chicken remains
    assert "fish/seafood" not in tracker.protein_history
    assert "chicken/meat" in tracker.protein_history

if __name__ == "__main__":
    test_variety_tracker_basic()
    test_variety_tracker_snapshot()
    print("All Variety Tracker tests passed!")
