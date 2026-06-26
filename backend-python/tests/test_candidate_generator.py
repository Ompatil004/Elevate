import unittest
import os
from app.nutrition_engine.food_graph import FoodGraph
from app.nutrition_engine.template_manager import TemplateManager
from app.nutrition_engine.candidate_generator import CandidateGenerator

class TestCandidateGenerator(unittest.TestCase):
    def setUp(self):
        base_dir = os.path.join(os.path.dirname(__file__), '..')
        
        ingredient_db_path = os.path.join(base_dir, 'data', 'ingredient_database.json')
        recipe_db_path = os.path.join(base_dir, 'data', 'recipe_database.json')
        relationship_path = os.path.join(base_dir, 'data', 'food_relationship_graph.json')
        nutrition_path = os.path.join(base_dir, 'data', 'nutrition_production_final_v4.csv')
        template_path = os.path.join(base_dir, 'config', 'meal_templates.yaml')
        
        self.food_graph = FoodGraph(ingredient_db_path, recipe_db_path, relationship_path, nutrition_path)
        self.template_manager = TemplateManager(template_path)
        self.candidate_generator = CandidateGenerator(self.food_graph)

    def test_generate_lunch_candidates(self):
        templates = self.template_manager.get_templates_for_meal('lunch', 'pan_indian')
        self.assertTrue(len(templates) > 0, "No lunch templates found")
        
        standard_thali = templates[0]
        
        # Generate 3 candidates for a Vegetarian diet
        candidates, _ = self.candidate_generator.generate_candidates(
            template=standard_thali,
            meal_type="Lunch",
            diet_type="Vegetarian",
            count=3
        )
        
        self.assertTrue(len(candidates) > 0, "Should generate at least one candidate")
        print(f"LENGTH OF CANDIDATES: {len(candidates)}")
        print(f"FIRST CANDIDATE ROLES: {[node.get('template_role') or node.get('semantics', {}).get('meal_role') for node in candidates[0]]}")
        for plate in candidates:
            roles_in_plate = [node.get('template_role', node.get('semantics', {}).get('meal_role')) for node in plate]
            is_blueprint = any(item.get("semantics", {}).get("meal_id") for item in plate)
            if not is_blueprint:
                self.assertIn("protein_main", roles_in_plate, "Plate must contain the anchor protein_main")
                self.assertIn("carb_base", roles_in_plate, "Plate must contain the required carb_base")
            self.assertLessEqual(len(plate), 5, "Plate must respect max_total_items (5)")

    def test_forbidden_roles_not_included(self):
        templates = self.template_manager.get_templates_for_meal('breakfast', 'pan_indian')
        template = templates[0] # heavy_traditional_breakfast
        
        candidates, _ = self.candidate_generator.generate_candidates(
            template=template,
            meal_type="Breakfast",
            diet_type="Vegetarian",
            count=2
        )
        
        for plate in candidates:
            roles_in_plate = [node.get('template_role', node.get('semantics', {}).get('meal_role')) for node in plate]
            self.assertNotIn("curry", roles_in_plate, "Curry is forbidden in this breakfast template")

if __name__ == '__main__':
    unittest.main()
