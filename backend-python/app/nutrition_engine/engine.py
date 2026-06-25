import os
import logging
from typing import Dict, Any

from app.nutrition_engine.food_graph import FoodGraph
from app.nutrition_engine.template_manager import TemplateManager
from app.nutrition_engine.candidate_generator import CandidateGenerator
from app.nutrition_engine.meal_scorer import MealScorer
from app.nutrition_engine.portion_optimizer import PortionOptimizer
from app.nutrition_engine.variety_tracker import WeeklyVarietyTracker
from app.nutrition_engine.weekly_optimizer import WeeklyOptimizer
from app.nutrition_engine.weekly_validator import WeeklyValidator
from app.nutrition_engine.nutrition_calculator import WeeklyMacroPlanner

logger = logging.getLogger(__name__)

class NutritionEngineV6:
    """
    The V6 Knowledge-Driven Recommendation Engine.
    This replaces the legacy monolith by orchestrating the modular pipeline.
    """
    def __init__(self, data_dir: str = 'data', config_dir: str = 'config'):
        metadata_path = os.path.join(data_dir, 'food_knowledge_base.json')
        relationship_path = os.path.join(data_dir, 'food_relationship_graph.json')
        nutrition_csv_path = os.path.join(data_dir, 'nutrition_production_final_v4.csv')
        template_path = os.path.join(config_dir, 'meal_templates.yaml')
        
        logger.info("Initializing Nutrition Engine V6...")
        self.food_graph = FoodGraph(metadata_path, relationship_path, nutrition_csv_path)
        self.template_manager = TemplateManager(template_path)
        self.portion_optimizer = PortionOptimizer()
        self.candidate_generator = CandidateGenerator(self.food_graph)
        self.weekly_validator = WeeklyValidator()

    def generate_plan(self, user_profile: Dict[str, Any]) -> Dict[str, Any]:
        """
        The main entry point. Generates a fully validated weekly meal plan.
        """
        logger.info(f"Generating meal plan for profile: {user_profile}")
        
        # Instantiate request-scoped modules
        variety_tracker = WeeklyVarietyTracker()
        meal_scorer = MealScorer(variety_tracker)
        weekly_optimizer = WeeklyOptimizer(
            candidate_generator=self.candidate_generator,
            meal_scorer=meal_scorer,
            portion_optimizer=self.portion_optimizer,
            template_manager=self.template_manager,
            variety_tracker=variety_tracker
        )
        
        # Generate the weekly layout
        weekly_plan_result = weekly_optimizer.generate_weekly_plan(user_profile)
        weekly_plan = weekly_plan_result.get("plan", {})
        stats = weekly_plan_result.get("stats", {})
        
        # Validate the generated plan holistically
        weekly_planner = WeeklyMacroPlanner()
        daily_targets = weekly_planner.plan_week(user_profile)
        # Assuming the validator checks the average or takes the dictionary of daily targets.
        validation_report = self.weekly_validator.validate_plan(weekly_plan, user_profile, daily_targets)
        
        return {
            "status": "success" if validation_report["is_valid"] else "warning",
            "validation_report": validation_report,
            "weekly_plan": weekly_plan,
            "stats": stats,
            "daily_targets": daily_targets
        }
