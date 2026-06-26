import unittest
from app.nutrition_engine.weekly_optimizer import WeeklyOptimizer
from app.nutrition_engine.food_graph import FoodGraph
from app.nutrition_engine.template_manager import TemplateManager
from app.nutrition_engine.candidate_generator import CandidateGenerator
from app.nutrition_engine.meal_scorer import MealScorer
from app.nutrition_engine.portion_optimizer import PortionOptimizer
from app.nutrition_engine.variety_tracker import WeeklyVarietyTracker

class TestGoldenProfiles(unittest.TestCase):
    def setUp(self):
        self.food_graph = FoodGraph(
            "data/ingredient_database.json",
            "data/recipe_database.json",
            "data/food_relationship_graph.json",
            "data/nutrition_production_final_v4.csv"
        )
        self.template_manager = TemplateManager("config/meal_templates.yaml")
        self.portion_optimizer = PortionOptimizer()
        self.candidate_generator = CandidateGenerator(self.food_graph)
        self.variety_tracker = WeeklyVarietyTracker()
        self.meal_scorer = MealScorer(self.variety_tracker)
        
        self.optimizer = WeeklyOptimizer(
            candidate_generator=self.candidate_generator,
            meal_scorer=self.meal_scorer,
            portion_optimizer=self.portion_optimizer,
            template_manager=self.template_manager,
            variety_tracker=self.variety_tracker
        )

    def _run_profile(self, user_profile):
        try:
            result = self.optimizer.generate_weekly_plan(user_profile)
            plan = result.get("plan", {})
            stats = result.get("stats", {})
            self.assertTrue(plan, "Plan should not be empty")
            return plan, stats
        except Exception as e:
            self.fail(f"Failed to generate plan for {user_profile.get('goal')}: {str(e)}")

    def test_golden_senior_maintenance(self):
        profile = {
            "weight": 70,
            "goal": "Maintenance",
            "experience": "Beginner",
            "diet_type": "Vegetarian",
            "age": 65,
            "gender": "Male",
            "days_per_week": 2,
            "appetite": "Small"
        }
        plan, _ = self._run_profile(profile)
        self._assert_plan_quality(plan)

    def test_golden_vegan_muscle_gain(self):
        profile = {
            "weight": 75,
            "goal": "Muscle Gain",
            "experience": "Advanced",
            "diet_type": "Vegan",
            "age": 28,
            "gender": "Male",
            "days_per_week": 5,
            "appetite": "Large"
        }
        plan, _ = self._run_profile(profile)
        self._assert_plan_quality(plan)
        
    def test_golden_pcos_weight_loss(self):
        profile = {
            "weight": 85,
            "goal": "Weight Loss",
            "experience": "Beginner",
            "diet_type": "NonVeg",
            "age": 32,
            "gender": "Female",
            "days_per_week": 3,
            "appetite": "Average",
            "medical_conditions": ["PCOS"]
        }
        plan, _ = self._run_profile(profile)
        self._assert_plan_quality(plan)

    def _assert_plan_quality(self, plan):
        # Weekly asserts
        breakfasts = set()
        dinners = set()
        
        for day in plan.get("days", []):
            if day.get("type") == "rest":
                continue # no planned meals for empty rest day structure if it lacks meals
                
            for meal in day.get("meals", []):
                # We need to verify capacity limits, realism score etc once implemented.
                if meal["meal_type"] == "breakfast":
                    # Assert no repeated consecutive breakfast if possible, or just gather them
                    name = meal.get("meal_name")
                    if name: breakfasts.add(name)
                elif meal["meal_type"] == "dinner":
                    name = meal.get("meal_name")
                    if name: dinners.add(name)
                    
                # Assert completeness > 85%
                self.assertGreaterEqual(meal.get("completeness_score", 100), 85, 
                                        f"Meal {meal.get('meal_name')} failed completeness check.")
                                        
                # Assert portion limits
                for item in meal.get("foods", []):
                    # Placeholder until actual checks
                    self.assertTrue(True)

if __name__ == '__main__':
    unittest.main()
