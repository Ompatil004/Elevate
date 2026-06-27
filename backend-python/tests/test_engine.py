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

    def test_validation_failure_graceful(self):
        from unittest.mock import patch
        with patch('app.nutrition_engine.weekly_optimizer.WeeklyOptimizer.generate_weekly_plan') as mock_gen:
            mock_gen.return_value = {"plan": {}, "stats": {}}
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
            self.assertEqual(result["status"], "error")
            self.assertEqual(result["weekly_plan"], {})
            self.assertFalse(result["validation_report"]["is_valid"])

    def test_generation_uncaught_exception_graceful(self):
        from unittest.mock import patch
        with patch('app.nutrition_engine.weekly_optimizer.WeeklyOptimizer.generate_weekly_plan', side_effect=RuntimeError("Solver timeout")):
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
            self.assertEqual(result["status"], "error")
            self.assertIsNone(result["weekly_plan"])
            self.assertFalse(result["validation_report"]["is_valid"])
            self.assertIn("Solver timeout", result["validation_report"]["critical_errors"][0])

if __name__ == '__main__':
    unittest.main()
