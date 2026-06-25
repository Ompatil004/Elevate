import unittest
import os
import yaml
from app.nutrition_engine.template_manager import TemplateManager

class TestMealTemplates(unittest.TestCase):
    def setUp(self):
        # We assume tests are run from the backend-python root
        self.config_path = os.path.join(os.path.dirname(__file__), '..', 'config', 'meal_templates.yaml')
        self.manager = TemplateManager(self.config_path)

    def test_file_exists(self):
        self.assertTrue(os.path.exists(self.config_path), "meal_templates.yaml must exist.")

    def test_templates_load(self):
        pan_indian_lunch = self.manager.get_templates_for_meal('lunch', 'pan_indian')
        self.assertTrue(len(pan_indian_lunch) > 0, "Should have at least one pan_indian lunch template")
        
        north_indian_lunch = self.manager.get_templates_for_meal('lunch', 'north_indian')
        self.assertTrue(len(north_indian_lunch) > 0, "Should have at least one north_indian lunch template")
        
        # Test fallback
        north_indian_snack = self.manager.get_templates_for_meal('snack', 'north_indian')
        self.assertTrue(len(north_indian_snack) > 0, "Should fallback to pan_indian snack")

    def test_template_schema(self):
        templates = self.manager.get_templates_for_meal('breakfast', 'pan_indian')
        for t in templates:
            self.assertTrue(self.manager.validate_template_schema(t), f"Template {t.get('id')} failed schema validation")

    def test_sorting_by_priority(self):
        templates = self.manager.get_templates_for_meal('lunch', 'pan_indian')
        priorities = [t.get('priority', 0) for t in templates]
        self.assertEqual(priorities, sorted(priorities, reverse=True), "Templates should be sorted by priority descending")

if __name__ == '__main__':
    unittest.main()
