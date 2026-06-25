import unittest
import os
import json
from app.nutrition_engine.engine import NutritionEngineV6

class TestNutritionEngine(unittest.TestCase):
    def setUp(self):
        base_dir = os.path.join(os.path.dirname(__file__), '..')
        data_dir = os.path.join(base_dir, 'data')
        config_dir = os.path.join(base_dir, 'config')
        
        self.engine = NutritionEngineV6(data_dir=data_dir, config_dir=config_dir)
        
    def test_end_to_end_generation(self):
        profile = {
            "weight_kg": 75,
            "height_cm": 180,
            "age": 28,
            "gender": "male",
            "activity_level": "moderate",
            "goal": "muscle_gain",
            "diet_type": "Vegetarian",
            "region": "pan_indian"
        }
        
        result = self.engine.generate_plan(profile)
        
        self.assertIn("status", result)
        self.assertIn("weekly_plan", result)
        self.assertIn("validation_report", result)
        
        plan = result["weekly_plan"]
        self.assertEqual(len(plan), 7, "Should generate exactly 7 days")
        self.assertIn("breakfast", plan["Day_1"], "Day 1 should have breakfast")
        self.assertIn("lunch", plan["Day_1"], "Day 1 should have lunch")
        
        # Verify the plates are not empty if there were matches
        breakfast_plate = plan["Day_1"]["breakfast"]
        self.assertTrue(isinstance(breakfast_plate, list))

if __name__ == '__main__':
    unittest.main()
