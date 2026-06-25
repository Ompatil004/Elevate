import yaml
import logging
from typing import Dict

logger = logging.getLogger(__name__)

class NutritionRuleEngine:
    """
    Houses strict nutritional rules isolated from algorithmic generation.
    Loads rules from nutrition_rules.yaml.
    """
    def __init__(self, config_path: str):
        self.config_path = config_path
        self.rules = self._load_rules()

    def _load_rules(self) -> Dict:
        try:
            with open(self.config_path, 'r') as f:
                rules = yaml.safe_load(f)
                logger.info("Loaded Nutrition Rule Engine configuration.")
                return rules
        except Exception as e:
            logger.error(f"Failed to load rules from {self.config_path}: {e}")
            raise e

    def get_goal_multipliers(self, goal: str) -> Dict:
        """Returns the specific protein/fat multipliers and calorie offsets for a given goal."""
        goal_key = goal.lower().replace(" ", "_")
        
        # Fallback to maintenance if goal not found
        if goal_key not in self.rules.get('goals', {}):
            logger.warning(f"Goal '{goal}' not found in rules. Falling back to maintenance.")
            goal_key = "maintenance"
            
        return self.rules['goals'][goal_key]

    def get_meal_distribution(self, meal_type: str) -> Dict:
        """Returns the percentage distribution and minimums for a specific meal."""
        meal_key = meal_type.lower()
        dist = self.rules.get('meal_distribution', {}).get(meal_key)
        if not dist:
            # Default generic distribution if not defined
            return {
                "min_calories_pct": 20,
                "max_calories_pct": 30,
                "min_protein_g": 15
            }
        return dist
