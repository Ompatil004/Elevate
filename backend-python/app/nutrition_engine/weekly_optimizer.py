import logging
from typing import Dict, List, Any
from app.nutrition_engine.candidate_generator import CandidateGenerator
from app.nutrition_engine.meal_scorer import MealScorer
from app.nutrition_engine.portion_optimizer import PortionOptimizer
from app.nutrition_engine.variety_tracker import WeeklyVarietyTracker
from app.nutrition_engine.template_manager import TemplateManager
from app.nutrition_engine.nutrition_calculator import WeeklyMacroPlanner, MealMacroDistributor

logger = logging.getLogger(__name__)

class WeeklyOptimizer:
    """
    Phase 4.9: Weekly Optimizer with Strict Target Planning and Hard Limits.
    Coordinates the Weekly Macro Planner, Meal Distributor, Plate Builder, and Scorer.
    """
    def __init__(self, candidate_generator: CandidateGenerator, meal_scorer: MealScorer, portion_optimizer: PortionOptimizer, template_manager: TemplateManager, variety_tracker: WeeklyVarietyTracker):
        self.candidate_generator = candidate_generator
        self.meal_scorer = meal_scorer
        self.portion_optimizer = portion_optimizer
        self.template_manager = template_manager
        self.variety_tracker = variety_tracker
        
        # Phase 4.9 Planners
        self.weekly_planner = WeeklyMacroPlanner()
        self.meal_distributor = MealMacroDistributor()

    def generate_weekly_plan(self, user_profile: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generates a full 7-day meal plan respecting strict target compliance.
        Returns a dictionary containing "plan" and "stats".
        """
        stats = {
            "failure_reasons": {
                "template_exhausted": 0,
                "protein_impossible": 0,
                "calories_impossible": 0,
                "portion_exceeded": 0,
                "compatibility_violation": 0,
                "meal_suitability_violation": 0
            },
            "constraint_pressure": {
                "passed_structure": 0,
                "passed_compatibility": 0,
                "passed_portion": 0,
                "passed_macros": 0,
                "passed_variety": 0,
                "total_candidates": 0
            },
            "acceptance_stats": {
                "total_generated": 0,
                "total_accepted": 0,
                "recovery_successes": 0,
                "recovery_failures": 0
            }
        }
        
        # Normalize profile keys
        if 'weight' in user_profile and 'weight_kg' not in user_profile:
            user_profile['weight_kg'] = user_profile['weight']
        if 'height' in user_profile and 'height_cm' not in user_profile:
            user_profile['height_cm'] = user_profile['height']
            
        diet_val = user_profile.get('diet_type') or user_profile.get('dietary_preference') or 'NonVeg'
        if diet_val in ('Veg', 'Vegetarian'):
            user_profile['diet_type'] = 'Vegetarian'
        elif diet_val in ('Non-Veg', 'NonVeg'):
            user_profile['diet_type'] = 'NonVeg'
        elif diet_val in ('Vegan',):
            user_profile['diet_type'] = 'Vegan'
        else:
            user_profile['diet_type'] = diet_val

        # 1. Plan Explicit Weekly Targets (cycles calories based on workout intensity)
        weekly_daily_targets = self.weekly_planner.plan_week(user_profile)
        
        region = user_profile.get("region", "pan_indian")
        diet_type = user_profile.get("diet_type", "NonVeg")
        
        weekly_plan = {}
        
        for day_key, daily_target in weekly_daily_targets.items():
            day_num = int(day_key.split('_')[1])
            
            # Snapshot at the start of the day
            day_start_snapshot = self.variety_tracker.get_snapshot()
            
            # 2. Distribute daily target explicitly to 4 meals based on intensity ratios
            meal_split_targets = self.meal_distributor.distribute(daily_target)
            
            # Retry loop for per-day validation
            day_plan_valid = False
            attempts = 0
            best_day_plan = None
            best_day_macros = None
            best_combined_diff = 999.0
            
            while not day_plan_valid and attempts < 5:
                attempts += 1
                
                # Snapshot before this attempt
                attempt_snapshot = self.variety_tracker.get_snapshot()
                
                day_plan = {}
                day_total_macros = {"calories": 0, "protein": 0, "carbs": 0, "fat": 0}
                running_deficit = {"calories": 0.0, "protein": 0.0}
                whey_used_today = 0
                
                for meal_type, base_target_macros in meal_split_targets.items():
                    # Apply running deficit to current target, but cap min to 50% to prevent negative runaway targets
                    cals_def = running_deficit["calories"]
                    pro_def = running_deficit["protein"]
                    
                    if meal_type == "snack":
                        cals_def = min(cals_def, base_target_macros["calories"] * 0.5)
                        pro_def = min(pro_def, base_target_macros["protein"] * 0.5)
                        
                    target_macros = {
                        "calories": max(base_target_macros["calories"] * 0.5, base_target_macros["calories"] + cals_def),
                        "protein": max(base_target_macros["protein"] * 0.5, base_target_macros["protein"] + pro_def)
                    }
                    # 3. Get Templates and filter by feasibility
                    raw_templates = self.template_manager.get_templates_for_meal(meal_type, region)
                    feasible_templates = self.template_manager.filter_feasible_templates(raw_templates, target_macros)
                    
                    if not feasible_templates:
                        logger.warning(f"No feasible templates found for {meal_type} with target {target_macros['protein']}g protein.")
                        stats["failure_reasons"]["template_exhausted"] += 1
                        feasible_templates = raw_templates[:1] # Fallback to top template if none are mathematically feasible
                        
                    best_plate = None
                    best_score = -1000
                    best_effort_plate = None
                    best_effort_score = -1000
                    
                    # Pass 1: Strict constraints (Rotation & Portion limits)
                    for template in feasible_templates[:5]: 
                        candidates, gen_stats = self.candidate_generator.generate_candidates(template, meal_type, diet_type, count=3, user_profile=user_profile)
                        stats["constraint_pressure"]["total_candidates"] += gen_stats["total_candidates"]
                        stats["constraint_pressure"]["passed_structure"] += gen_stats["passed_structure"]
                        
                        for candidate_plate in candidates:
                            anchor_sem = candidate_plate[0]['semantics']
                            meal_id = anchor_sem['meal_id']
                            foods = [item['food_name'] for item in candidate_plate]
                            protein_source = anchor_sem.get('protein_source')
                            carb_source = anchor_sem.get('carb_source')
                            cuisine = anchor_sem.get('cuisine')
                            cooking_style = anchor_sem.get('cooking_style')
                            
                            # Enforce rotation & same-day duplicate prevention
                            if self.variety_tracker.is_duplicate_meal(meal_id, foods, protein_source, carb_source, day_num, cuisine, cooking_style):
                                continue
                                
                            # Supplement Policy Engine & Whey Limitation
                            has_whey = any('whey' in f.lower() for f in foods)
                            if has_whey:
                                if whey_used_today >= 1:
                                    continue
                                if meal_type == 'snack':
                                    if target_macros['protein'] <= 25.0:
                                        # Prefer whole foods over whey for low protein targets
                                        continue
                                    if target_macros['protein'] > 35.0 and len(foods) < 2:
                                        # For high targets, require whey + something else (not whey alone)
                                        continue
                            optimized_plate = self.portion_optimizer.optimize_portions(candidate_plate, target_macros)
                            
                            score_dict = self.meal_scorer.score_candidate_plate(optimized_plate, target_macros, day_num)
                            total_score = score_dict["total_score"]
                            
                            # Best effort tracking (ignores 85% rule and visual balance)
                            if total_score > best_effort_score:
                                best_effort_score = total_score
                                best_effort_plate = optimized_plate
                                
                            # Enforce Visual Plate Balance
                            if not self._is_plate_visually_balanced(optimized_plate):
                                continue
                                
                            plate_p = sum(float(i['nutrition']['protein']) for i in optimized_plate)
                            
                            # Must hit at least 85% of target protein for strict pass
                            if plate_p < target_macros['protein'] * 0.85:
                                continue
                            
                            if total_score > best_score:
                                best_score = total_score
                                best_plate = optimized_plate
 
                    # Pass 2: Fallback constraints if strict pass failed to find anything
                    if not best_plate:
                        for template in feasible_templates[:5]: 
                            candidates, _ = self.candidate_generator.generate_candidates(template, meal_type, diet_type, count=3, user_profile=user_profile)
                            for candidate_plate in candidates:
                                anchor_sem = candidate_plate[0]['semantics']
                                meal_id = anchor_sem.get('meal_id')
                                foods = [item['food_name'] for item in candidate_plate]
                                protein_source = anchor_sem.get('protein_source')
                                carb_source = anchor_sem.get('carb_source')
                                cuisine = anchor_sem.get('cuisine')
                                cooking_style = anchor_sem.get('cooking_style')
                                
                                # In Pass 2 Fallback, we do NOT strictly block duplicates.
                                # The meal_scorer will penalize duplicates, so the engine will
                                # naturally prefer the least offensive duplicate if no fresh meals are available.
                                
                                # Supplement Policy Engine & Whey Limitation
                                has_whey = any('whey' in f.lower() for f in foods)
                                if has_whey:
                                    if whey_used_today >= 1:
                                        continue
                                    if meal_type == 'snack':
                                        if target_macros['protein'] <= 25.0:
                                            continue
                                        if target_macros['protein'] > 35.0 and len(foods) < 2:
                                            continue
                                            
                                optimized_plate = self.portion_optimizer.optimize_portions(candidate_plate, target_macros)
                                
                                score_dict = self.meal_scorer.score_candidate_plate(optimized_plate, target_macros, day_num)
                                total_score = score_dict["total_score"] - 30 # Penalize fallback slightly
                                
                                # Best effort tracking (ignores 85% rule and visual balance)
                                if total_score > best_effort_score:
                                    best_effort_score = total_score
                                    best_effort_plate = optimized_plate
                                    
                                # Enforce Visual Plate Balance
                                if not self._is_plate_visually_balanced(optimized_plate):
                                    continue
                                    
                                plate_p = sum(float(i['nutrition']['protein']) for i in optimized_plate)
                                # No strict 85% protein threshold for fallback, we rely on the score
                                
                                if total_score > best_score:
                                    best_score = total_score
                                    best_plate = optimized_plate
                                    
                    # Pass 3: Best Effort Fallback
                    if not best_plate and best_effort_plate:
                        best_plate = best_effort_plate
                        logger.debug(f"Used best effort fallback for {meal_type} on day {day_num} (failed strict constraints)")
                                
                    stats["acceptance_stats"]["total_generated"] += 1
                    # 6. Apply Best Plate
                    if best_plate:
                        stats["acceptance_stats"]["total_accepted"] += 1
                        plate_p = sum(float(i['nutrition']['protein']) for i in best_plate)
                        plate_c = sum(float(i['nutrition']['calories']) for i in best_plate)
                        
                        day_plan[meal_type] = best_plate
                        day_total_macros["calories"] += plate_c
                        day_total_macros["protein"] += plate_p
                        
                        has_whey = any('whey' in i['food_name'].lower() for i in best_plate)
                        if has_whey:
                            whey_used_today += 1
                        
                        running_deficit["calories"] = target_macros["calories"] - plate_c
                        running_deficit["protein"] = target_macros["protein"] - plate_p
                        
                        # 7. Track variety
                        meal_id = best_plate[0]['semantics']['meal_id']
                        foods = [item['food_name'] for item in best_plate]
                        protein_source = best_plate[0]['semantics'].get('protein_source')
                        carb_source = best_plate[0]['semantics'].get('carb_source')
                        vegetables = best_plate[0]['semantics'].get('vegetables', [])
                        cuisine = best_plate[0]['semantics'].get('cuisine')
                        cooking_style = best_plate[0]['semantics'].get('cooking_style')
                        
                        self.variety_tracker.record_meal_selection(
                            meal_id=meal_id,
                            foods=foods,
                            protein_source=protein_source,
                            carb_source=carb_source,
                            vegetables=vegetables,
                            day_num=day_num,
                            cuisine=cuisine,
                            cooking_style=cooking_style
                        )
                        
                        for item in best_plate:
                            family = item['semantics'].get('family', 'other')
                            self.variety_tracker.record_food(item['food_id'], family, day_num)
                    else:
                        logger.warning(f"No valid candidates found for {meal_type} on day {day_num} (failed per-meal constraints)")
                        day_plan[meal_type] = []
                
                # 8. Strict Per-Day Validation
                target_cal = daily_target["calories"]
                target_pro = daily_target["protein"]
                
                cal_diff_pct = abs(day_total_macros["calories"] - target_cal) / max(target_cal, 1)
                pro_diff_pct = abs(day_total_macros["protein"] - target_pro) / max(target_pro, 1)
                
                combined_diff = cal_diff_pct + pro_diff_pct
                total_foods = sum(len(items) for items in day_plan.values())
                if total_foods > 0 and combined_diff < best_combined_diff:
                    best_combined_diff = combined_diff
                    best_day_plan = day_plan
                    best_day_macros = day_total_macros
                    
                # Soft Constraint Relaxation
                if attempts <= 2:
                    allowed_cal_var = 0.05
                    allowed_pro_var = 0.03
                elif attempts <= 4:
                    allowed_cal_var = 0.06
                    allowed_pro_var = 0.04
                else:
                    allowed_cal_var = 0.08
                    allowed_pro_var = 0.05
                    
                if cal_diff_pct <= allowed_cal_var and pro_diff_pct <= allowed_pro_var:
                    day_plan_valid = True
                    best_day_plan = day_plan
                    best_day_macros = day_total_macros
                    if attempts > 1:
                        stats["acceptance_stats"]["recovery_successes"] += 1
                else:
                    logger.debug(f"Per-Day Validation Failed: Cal diff {cal_diff_pct*100:.1f}%, Pro diff {pro_diff_pct*100:.1f}%")
                    # Rollback variety tracker for this attempt
                    self.variety_tracker.restore_snapshot(attempt_snapshot)
                    
            if not day_plan_valid:
                logger.error(f"Failed Day {day_key}. Targets: Cal {target_cal}, Pro {target_pro}. Soft accepting best attempt.")
                stats["acceptance_stats"]["recovery_failures"] += 1
                # Rollback to the start of the day to clean up failed attempts' pollution
                self.variety_tracker.restore_snapshot(day_start_snapshot)
                
                # Replay/record the chosen best_day_plan to variety tracker
                if best_day_plan:
                    for meal_type, best_plate in best_day_plan.items():
                        if best_plate:
                            meal_id = best_plate[0]['semantics']['meal_id']
                            foods = [item['food_name'] for item in best_plate]
                            protein_source = best_plate[0]['semantics'].get('protein_source')
                            carb_source = best_plate[0]['semantics'].get('carb_source')
                            vegetables = best_plate[0]['semantics'].get('vegetables', [])
                            cuisine = best_plate[0]['semantics'].get('cuisine')
                            cooking_style = best_plate[0]['semantics'].get('cooking_style')
                            
                            self.variety_tracker.record_meal_selection(
                                meal_id=meal_id,
                                foods=foods,
                                protein_source=protein_source,
                                carb_source=carb_source,
                                vegetables=vegetables,
                                day_num=day_num,
                                cuisine=cuisine,
                                cooking_style=cooking_style
                            )
                            for item in best_plate:
                                family = item['semantics'].get('family', 'other')
                                self.variety_tracker.record_food(item['food_id'], family, day_num)
                                
            # Accept best attempt (ensure it is never None)
            if not best_day_plan:
                best_day_plan = day_plan
            weekly_plan[day_key] = best_day_plan
            
        return {"plan": weekly_plan, "stats": stats}

    def _is_plate_visually_balanced(self, optimized_plate: List[Dict]) -> bool:
        """
        Ensures the plate is visually balanced (e.g. not 4 rotis with only 50g dal).
        """
        carb_qty = 0.0
        protein_qty = 0.0
        
        for item in optimized_plate:
            name_lower = str(item.get("food_name", "")).lower()
            qty = float(item.get("serving_qty", 1))
            unit = str(item.get("serving_unit", "g")).lower().strip()
            
            # Identify carbs
            if any(x in name_lower for x in ['roti', 'chapati', 'phulka', 'rice', 'pulao', 'bread', 'paratha', 'dosa']):
                carb_qty += qty if unit in ('piece', 'pieces', 'plate', 'plates', 'slice', 'slices') else (qty / 150.0)
                
            # Identify proteins/curries
            if any(x in name_lower for x in ['dal', 'paneer', 'chicken', 'egg', 'fish', 'soya', 'chana', 'rajma', 'curry']):
                protein_qty += qty if unit in ('bowl', 'bowls') else (qty / 150.0)
                
        # If we have a significant amount of carbs, we need a proportional amount of protein/curry to eat it with
        if carb_qty >= 3.0 and protein_qty < 0.8:
            return False # E.g., 3 rotis but less than 1 bowl of dal
            
        if carb_qty >= 2.0 and protein_qty < 0.4:
            return False
            
        return True


