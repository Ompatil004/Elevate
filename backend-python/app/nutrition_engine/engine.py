import os
import logging
from typing import Dict, Any,List

from app.nutrition_engine.food_graph import FoodGraph
from app.nutrition_engine.template_manager import TemplateManager
from app.nutrition_engine.candidate_generator import CandidateGenerator
from app.nutrition_engine.meal_scorer import MealScorer
from app.nutrition_engine.portion_optimizer import PortionOptimizer
from app.nutrition_engine.variety_tracker import WeeklyVarietyTracker
from app.nutrition_engine.weekly_optimizer import WeeklyOptimizer
from app.nutrition_engine.weekly_validator import WeeklyValidator
from app.nutrition_engine.nutrition_calculator import WeeklyMacroPlanner
from app.nutrition_engine.ingredient_optimizer import IngredientOptimizer
from app.nutrition_engine.plan_cache import WeeklyPlanManager

logger = logging.getLogger(__name__)

class NutritionEngineV6:
    """
    The V6 Knowledge-Driven Recommendation Engine.
    This replaces the legacy monolith by orchestrating the modular pipeline.
    """
    def __init__(self, data_dir: str = 'data', config_dir: str = 'config', db_client=None):
        ingredient_db_path = os.path.join(data_dir, 'ingredient_database.json')
        recipe_db_path = os.path.join(data_dir, 'recipe_database.json')
        relationship_path = os.path.join(data_dir, 'food_relationship_graph.json')
        nutrition_csv_path = os.path.join(data_dir, 'nutrition_production_final_v4.csv')
        template_path = os.path.join(config_dir, 'meal_templates.yaml')
        
        logger.info("Initializing Nutrition Engine V6...")
        self.food_graph = FoodGraph(ingredient_db_path, recipe_db_path, relationship_path, nutrition_csv_path)
        self.template_manager = TemplateManager(template_path)
        self.portion_optimizer = PortionOptimizer()
        self.candidate_generator = CandidateGenerator(self.food_graph)
        self.weekly_validator = WeeklyValidator()
        self.ingredient_optimizer = IngredientOptimizer(self.food_graph)
        self.plan_manager = WeeklyPlanManager(db_client)

    def generate_plan(self, user_profile: Dict[str, Any], user_id: str = "mock_user", week_start: str = "2026-06-22") -> Dict[str, Any]:
        """
        The main entry point. Generates a fully validated weekly meal plan.
        """
        logger.info(f"Generating meal plan for profile: {user_profile}")
        
        # 1. Check cache first
        cached_plan = self.plan_manager.get_valid_plan(user_id, user_profile, week_start)
        if cached_plan:
            return {
                "status": "success",
                "validation_report": {"is_valid": True, "message": "Loaded from cache"},
                "weekly_plan": cached_plan,
                "stats": {"cache_hit": True},
                "daily_targets": {}
            }
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
        
        # 3. Optimize ingredients (batch reuse)
        # DISABLED: IngredientOptimizer swaps food_ids without fetching correct macros/units,
        # violating strict food identity and causing duplicates within the same meal.
        # weekly_plan = self.ingredient_optimizer.optimize(weekly_plan)
        
        # 4. Validate the generated plan holistically
        weekly_planner = WeeklyMacroPlanner()
        daily_targets = weekly_planner.plan_week(user_profile)
        
        # New Serialized Validation Step
        validation_report = self.weekly_validator.validate_serialized_plan(weekly_plan, daily_targets)
        
        # 5. Save to Cache if valid

        if validation_report["is_valid"]:
            self.plan_manager.save_plan(user_id, user_profile, week_start, weekly_plan)
        else:
            logger.error(f"Weekly plan failed strict serialization validation: {validation_report.get('message')}")
        
        return {
            "status": "success" if validation_report["is_valid"] else "error",
            "validation_report": validation_report,
            "weekly_plan": weekly_plan,
            "stats": stats,
            "daily_targets": daily_targets
        }

    def generate_meal_swaps(self, user_profile: Dict[str, Any], week_start: str, day: int, meal_type: str, original_meal: Dict[str, Any], user_id: str = "mock_user", count: int = 3) -> List[Dict[str, Any]]:
        """
        Generates structural swaps for a specific meal, enforcing strict macro and semantic bounds.
        Uses caching to avoid redundant generation for identical user profiles.
        """
        if not original_meal or not isinstance(original_meal, list) or len(original_meal) == 0:
            return []
            
        anchor_item = original_meal[0]
        anchor_sem = anchor_item.get("semantics", {})
        meal_hash = anchor_sem.get("meal_id", "unknown")
        
        # 1. Check Cache
        cached = self.plan_manager.get_cached_swaps(user_id, user_profile, week_start, day, meal_type, meal_hash)
        if cached:
            return cached
            
        # Extract original properties for validation
        orig_cal = sum(float(i.get("nutrition", {}).get("calories", 0)) for i in original_meal)
        orig_pro = sum(float(i.get("nutrition", {}).get("protein", 0)) for i in original_meal)
        orig_weight = sum(float(i.get("nutrition", {}).get("serving_size_g", 0)) for i in original_meal)
        orig_prep = anchor_sem.get("preparation_time", 15)
        
        # We need a template that matches the original meal structure
        diet_type = user_profile.get("diet_type", "Standard")
        region = user_profile.get("region", "India")
        raw_templates = self.template_manager.get_templates_for_meal(meal_type, region)
        feasible_templates = self.template_manager.filter_feasible_templates(raw_templates, {
            "calories": orig_cal,
            "protein": orig_pro
        })
        
        target_macros = {
            "calories": orig_cal,
            "protein": orig_pro
        }
        
        valid_swaps = []
        seed = 9999 # swap specific seed base
        
        variety_tracker = WeeklyVarietyTracker() # Dummy tracker to prevent basic repetition
        variety_tracker.meal_identity_history[meal_hash] = day # ensure we don't return the original
        
        meal_scorer = MealScorer(variety_tracker)
        
        for template in feasible_templates:
            if len(valid_swaps) >= count:
                break
                
            seed += 1
            candidates, _ = self.candidate_generator.generate_candidates(template, meal_type, diet_type, count=10, user_profile=user_profile, day_seed=seed)
            
            for candidate_plate in candidates:
                if len(valid_swaps) >= count:
                    break
                    
                cand_anchor = candidate_plate[0].get("semantics", {})
                cand_meal_id = cand_anchor.get("meal_id")
                
                # Prevent suggesting the exact same meal
                if cand_meal_id == meal_hash:
                    continue
                    
                optimized_plate = self.portion_optimizer.optimize_portions(candidate_plate, target_macros)
                
                # Validation
                cand_cal = sum(float(i.get("nutrition", {}).get("calories", 0)) for i in optimized_plate)
                cand_pro = sum(float(i.get("nutrition", {}).get("protein", 0)) for i in optimized_plate)
                cand_weight = sum(float(i.get("nutrition", {}).get("serving_size_g", 0)) for i in optimized_plate)
                cand_prep = cand_anchor.get("preparation_time", 15)
                
                # Structural Bounds Check
                cal_diff = abs(cand_cal - orig_cal) / max(1, orig_cal)
                pro_diff = abs(cand_pro - orig_pro) / max(1, orig_pro)
                
                if cal_diff > 0.10: continue
                if pro_diff > 0.10: continue
                
                # Optional weight/prep bounds, but typically we want them somewhat similar
                if cand_weight > orig_weight * 2 or cand_weight < orig_weight * 0.5: continue
                
                valid_swaps.append(optimized_plate)
                
        # 3. Save to Cache
        if valid_swaps:
            self.plan_manager.save_cached_swaps(user_id, user_profile, week_start, day, meal_type, meal_hash, valid_swaps)
            
        return valid_swaps
