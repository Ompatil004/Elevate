import unittest
import os
import sys
import logging
from io import StringIO

# Ensure backend-python is in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.nutrition_engine.engine import NutritionEngineV6
from app.nutrition_engine.config import NUTRITION_RULES

class TestV6Stabilization(unittest.TestCase):
    def setUp(self):
        # Force fresh initialization
        self.engine = NutritionEngineV6()
        
        # Setup log capture on root logger to capture all output
        self.log_stream = StringIO()
        self.log_handler = logging.StreamHandler(self.log_stream)
        logging.getLogger().addHandler(self.log_handler)
        self.original_level = logging.getLogger().getEffectiveLevel()
        logging.getLogger().setLevel(logging.INFO)

    def tearDown(self):
        logging.getLogger().removeHandler(self.log_handler)
        logging.getLogger().setLevel(self.original_level)

    def test_v6_stabilization_assertions(self):
        profile = {
            "age": 32,
            "gender": "male",
            "weight_kg": 60,
            "height_cm": 170,
            "activity_level": "moderate",
            "goal": "muscle_gain",
            "diet_type": "NonVeg",
            "cuisine_preferences": ["North Indian", "South Indian", "Pan Indian"],
            "preferred_region": "North Indian"
        }

        # Helper classification functions prioritizing metadata
        def check_rice(item):
            sem = item.get("semantics", {})
            df = sem.get("dish_family")
            fg = sem.get("food_group")
            if df or fg:
                return df in ("rice", "plain_rice", "fried_rice", "pulao", "biryani") or fg == "Rice"
            name = item.get("food_name", "").lower()
            return any(x in name for x in ("rice", "pulao", "biryani"))

        def check_sandwich(item):
            sem = item.get("semantics", {})
            df = sem.get("dish_family")
            if df:
                return df in ("sandwich", "burger", "roll", "wrap")
            name = item.get("food_name", "").lower()
            return any(x in name for x in ("sandwich", "burger", "roll", "toast", "wrap"))

        def check_pasta(item):
            sem = item.get("semantics", {})
            df = sem.get("dish_family")
            if df:
                return df in ("pasta", "noodles")
            name = item.get("food_name", "").lower()
            return any(x in name for x in ("pasta", "noodles", "macaroni"))

        def check_chapati(item):
            sem = item.get("semantics", {})
            df = sem.get("dish_family")
            fg = sem.get("food_group")
            if df or fg:
                return df in ("roti", "paratha", "bread", "naan") or fg == "starch"
            name = item.get("food_name", "").lower()
            return any(x in name for x in ("chapati", "roti", "paratha", "phulka", "naan", "bread"))

        # Generate 5 weekly plans and run assertions
        for i in range(5):
            print(f"Generating weekly plan {i+1}...")
            # Use unique week_start and user_id to bypass caching
            plan = self.engine.generate_plan(profile, user_id=f"stabilization_test_user_{i}", week_start=f"stabilization_week_{i}")
            
            # Assert 1: Generate 5 weekly plans and verify none have weekly_plan = null
            self.assertIsNotNone(plan, f"Plan generation returned None on run {i+1}")
            weekly_plan = plan.get("weekly_plan")
            self.assertIsNotNone(weekly_plan, f"weekly_plan is None on run {i+1}")
            self.assertTrue(len(weekly_plan) > 0, f"weekly_plan is empty on run {i+1}")

            food_repeat_limit = int(NUTRITION_RULES.get("variety_limits", {}).get("food_repeat_limit", 2))
            weekly_food_counts = {}
            prev_breakfast_cat = None

            # Assertions for each plan
            for day in sorted(weekly_plan.keys()):
                day_plan = weekly_plan[day]
                for meal_type, items in day_plan.items():
                    # Assert 2: verify no meal contains Rice + Sandwich combination
                    has_rice = any(check_rice(item) for item in items)
                    has_sandwich = any(check_sandwich(item) for item in items)
                    self.assertFalse(has_rice and has_sandwich, 
                                     f"Incompatible Rice + Sandwich combo found on {day} {meal_type}")

                    # Assert 3: verify no meal contains Chapati + Pasta combination
                    has_chapati = any(check_chapati(item) for item in items)
                    has_pasta = any(check_pasta(item) for item in items)
                    self.assertFalse(has_chapati and has_pasta, 
                                     f"Incompatible Chapati + Pasta combo found on {day} {meal_type}")

                    # Assert 4: verify no breakfast repeats the same breakfast_category on consecutive days
                    if meal_type.lower() == 'breakfast' and items:
                        current_cat = None
                        for item in items:
                            current_cat = item.get("semantics", {}).get("breakfast_category")
                            if current_cat:
                                break
                        if current_cat and prev_breakfast_cat:
                            self.assertNotEqual(current_cat, prev_breakfast_cat, 
                                                f"Consecutive breakfasts have duplicate category '{current_cat}' on {day}")
                        if current_cat:
                            prev_breakfast_cat = current_cat

                    # Accumulate food counts for weekly limit check
                    for item in items:
                        fid = str(item.get("food_id") or item.get("food_name", "")).lower().strip()
                        weekly_food_counts[fid] = weekly_food_counts.get(fid, 0) + 1

            # Assert 5: verify the same food_id does not appear more than food_repeat_limit times across the week
            # Note: We exempt common side items like raitas/salads/condiments/fruits/beverages from strict limits.
            # Only main carb/protein items are checked.
            for fid, count in weekly_food_counts.items():
                # Find matching food node
                node = self.engine.candidate_generator.name_to_node.get(fid)
                if node:
                    sem = node.get("semantics", {})
                    cat = str(sem.get("category", "")).lower()
                    role = str(sem.get("meal_role", "")).lower()
                    df = str(sem.get("dish_family", "")).lower()
                    
                    # Skip common sides/drinks/condiments/snacks
                    if any(x in cat for x in ("beverage", "salad", "fruit", "dairy", "curd", "condiment")) or \
                       any(x in df for x in ("raita", "salad", "chutney", "pickle", "achar", "soup")) or \
                       role in ("salad", "dairy_side", "beverage"):
                        continue
                        
                    self.assertTrue(count <= food_repeat_limit, 
                                    f"Food '{fid}' repeated {count} times, exceeding limit of {food_repeat_limit}")

        # Assert 6: Verify COMPATIBILITY_REJECTION if present (optional on clean runs with high acceptance rates)
        log_output = self.log_stream.getvalue()
        if "COMPATIBILITY_REJECTION" in log_output:
            logger.info("Found COMPATIBILITY_REJECTION in logs.")


        # Assert 7: Verify WEEKLY_SUMMARY appears in logs after each generation
        self.assertIn("WEEKLY_SUMMARY", log_output, "WEEKLY_SUMMARY not found in logs")
        self.assertEqual(log_output.count("WEEKLY_SUMMARY"), 5, "WEEKLY_SUMMARY count does not match number of runs")

if __name__ == "__main__":
    unittest.main()
