import unittest
from app.nutrition_engine.meal_scorer import MealScorer

class MockVarietyTracker:
    def calculate_variety_penalty(self, food_id, family, current_day):
        return 0 # No penalty

class TestMealScorer(unittest.TestCase):
    def setUp(self):
        self.scorer = MealScorer(variety_tracker=MockVarietyTracker())
        
        self.mock_plate = [
            {
                "food_id": "1",
                "semantics": {"meal_role": "protein_main", "family": "poultry"},
                "compatibility": {"carb_base": 100},
                "nutrition": {"calories": 300, "protein": 30, "carbs": 10, "fat": 15}
            },
            {
                "food_id": "2",
                "semantics": {"meal_role": "carb_base", "family": "grain"},
                "compatibility": {"protein_main": 100},
                "nutrition": {"calories": 200, "protein": 5, "carbs": 40, "fat": 2}
            }
        ]

    def test_score_candidate_plate(self):
        target_macros = {"calories": 500, "protein": 35}
        
        score_dict = self.scorer.score_candidate_plate(self.mock_plate, target_macros, current_day=1)
        
        self.assertIn("total_score", score_dict)
        self.assertIn("breakdown", score_dict)
        
        breakdown = score_dict["breakdown"]
        self.assertGreaterEqual(breakdown["macro_score"], 90, "Macros are perfectly matched, should be near 100")
        self.assertEqual(breakdown["semantic_score"], 100, "100 compatibility should yield 100 semantic score")
        self.assertEqual(breakdown["realism_score"], 100, "Valid plate should have 100 realism score")
        self.assertEqual(breakdown["variety_score"], 100, "Mock tracker has 0 penalty")

    def test_penalize_weird_combinations(self):
        bad_plate = [
            {
                "food_id": "1",
                "semantics": {"meal_role": "protein_main"},
                "compatibility": {"protein_main": 20},
                "nutrition": {"calories": 300, "protein": 30, "carbs": 10, "fat": 15}
            },
            {
                "food_id": "2",
                "semantics": {"meal_role": "protein_main"},
                "compatibility": {"protein_main": 20},
                "nutrition": {"calories": 300, "protein": 30, "carbs": 10, "fat": 15}
            }
        ]
        
        score_dict = self.scorer.score_candidate_plate(bad_plate, {"calories": 600, "protein": 60}, 1)
        self.assertLess(score_dict["breakdown"]["realism_score"], 100, "Two protein mains should be penalized")

if __name__ == '__main__':
    unittest.main()
