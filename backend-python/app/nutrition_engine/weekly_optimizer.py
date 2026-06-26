import logging
import time
from typing import Dict, List, Any
from app.nutrition_engine.candidate_generator import CandidateGenerator, DailyMealContext
from app.nutrition_engine.meal_scorer import MealScorer
from app.nutrition_engine.portion_optimizer import PortionOptimizer
from app.nutrition_engine.variety_tracker import WeeklyVarietyTracker
from app.nutrition_engine.template_manager import TemplateManager
from app.nutrition_engine.nutrition_calculator import WeeklyMacroPlanner, MealMacroDistributor
from app.nutrition_engine.config import NUTRITION_RULES

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
        
        from app.nutrition_engine.serving_validator import FoodIdentityValidator
        self.identity_validator = FoodIdentityValidator(candidate_generator.food_graph)

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


        week_attempts = 0
        best_weekly_plan = None
        best_weekly_stats = None
        best_weekly_score = 999.0

        # Day name mapping (Day_1 = Monday .. Day_7 = Sunday)
        _DAY_NAMES = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
        
        while week_attempts < 1: # USER REQUIREMENT: Never regenerate the whole week!
            week_attempts += 1
            
            # 1. Plan Explicit Weekly Targets (cycles calories based on workout intensity)
            weekly_daily_targets = self.weekly_planner.plan_week(user_profile)
            
            region = user_profile.get("region", "pan_indian")
            diet_type = user_profile.get("diet_type", "NonVeg")
            
            weekly_plan = {}
            week_valid = True
            week_diff_score = 0.0
            
            # Full week reset for variety tracker
            self.variety_tracker.reset()
            
            # ── iterate over every day (Day_1 … Day_7) ──────────────────────────
            for day_key, daily_target in weekly_daily_targets.items():
                day_num = int(day_key.split('_')[1])
                # Use a human-readable day name as the plan key so both
                # meal_engine.py and the frontend can look up by "Monday" etc.
                day_name = _DAY_NAMES[day_num - 1]

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
                
                # Use configuration-driven daily retry limit instead of hardcoding attempts < 1
                max_daily_attempts = int(NUTRITION_RULES.get("validation_thresholds", {}).get("daily_retry_limit") or NUTRITION_RULES.get("retry_limits", {}).get("day", 5))
                while not day_plan_valid and attempts < max_daily_attempts:
                    attempts += 1
                    
                    # Snapshot before this attempt
                    attempt_snapshot = self.variety_tracker.get_snapshot()
                    
                    day_plan = {}
                    day_total_macros = {"calories": 0, "protein": 0, "carbs": 0, "fat": 0}
                    running_deficit = {"calories": 0.0, "protein": 0.0, "carbs": 0.0, "fat": 0.0}
                    whey_used_today = 0

                    # Create a fresh daily context for diversity tracking
                    daily_context = DailyMealContext()

                    # Ensure snack is always processed last so it can fill remaining macro gap
                    meal_order = [
                        (mt, macro)
                        for mt, macro in meal_split_targets.items()
                        if mt != 'snack'
                    ] + [
                        (mt, macro)
                        for mt, macro in meal_split_targets.items()
                        if mt == 'snack'
                    ]

                    for meal_type_idx, (meal_type, base_target_macros) in enumerate(meal_order):
                        # Apply running deficit to current target, but cap min to 50% to prevent negative runaway targets
                        cals_def = running_deficit["calories"]
                        pro_def = running_deficit["protein"]
                        carbs_def = running_deficit["carbs"]
                        fat_def = running_deficit["fat"]
                        
                        if meal_type == "snack":
                            cals_def = max(-base_target_macros["calories"] * 0.5, min(cals_def, base_target_macros["calories"] * 0.5))
                            pro_def = max(-base_target_macros["protein"] * 0.5, min(pro_def, base_target_macros["protein"] * 0.5))
                            carbs_def = max(-base_target_macros["carbs"] * 0.5, min(carbs_def, base_target_macros["carbs"] * 0.5))
                            fat_def = max(-base_target_macros["fat"] * 0.5, min(fat_def, base_target_macros["fat"] * 0.5))
                        else:
                            cals_def = max(-base_target_macros["calories"] * 0.4, min(cals_def, base_target_macros["calories"] * 0.4))
                            pro_def = max(-base_target_macros["protein"] * 0.4, min(pro_def, base_target_macros["protein"] * 0.4))
                            carbs_def = max(-base_target_macros["carbs"] * 0.4, min(carbs_def, base_target_macros["carbs"] * 0.4))
                            fat_def = max(-base_target_macros["fat"] * 0.4, min(fat_def, base_target_macros["fat"] * 0.4))
                            
                        target_macros = {
                            "calories": max(base_target_macros["calories"] * 0.5, base_target_macros["calories"] + cals_def),
                            "protein": max(base_target_macros["protein"] * 0.5, base_target_macros["protein"] + pro_def),
                            "carbs": max(base_target_macros["carbs"] * 0.5, base_target_macros["carbs"] + carbs_def),
                            "fat": max(base_target_macros["fat"] * 0.5, base_target_macros["fat"] + fat_def)
                        }
                        
                        # 3. Get Templates and filter by static schema (loose bounds)
                        raw_templates = self.template_manager.get_templates_for_meal(meal_type, region)
                        feasible_templates = self.template_manager.filter_feasible_templates(raw_templates, target_macros)
                        
                        if not feasible_templates:
                            # Fallback to all templates, let the data-driven validation handle it
                            feasible_templates = raw_templates

                        # Cross-meal exclusion: collect food_ids already committed to earlier meals today
                        excluded_foods_today = self.variety_tracker.get_days_foods_used(day_num)
                            
                        best_plate = None
                        best_score = -1000
                        best_effort_plate = None
                        best_effort_score = -1000
                        
                        # Pass 1: Strict constraints (Rotation & Portion limits)
                        # Seed = day_num * 1000 + meal_type_idx * 100 + attempts
                        # This guarantees a unique shuffle for every (day, meal_type, attempt) combination
                        _seed_p1 = day_num * 1000 + meal_type_idx * 100 + attempts
                        evaluated_templates = 0
                        
                        # Dynamic candidate distribution
                        target_counts = {'breakfast': 12, 'lunch': 15, 'dinner': 15, 'snack': 8}
                        total_target = target_counts.get(meal_type, 12)
                        per_template_count = max(2, total_target // max(1, len(feasible_templates)))
                        
                        for template in feasible_templates:
                            t0 = time.perf_counter()
                            candidates, gen_stats = self.candidate_generator.generate_candidates(
                                template, meal_type, diet_type, count=per_template_count,
                                user_profile=user_profile, day_seed=_seed_p1,
                                excluded_foods=excluded_foods_today,
                                daily_context=daily_context,
                                daily_targets=daily_target,
                            )
                            logger.info(f"[{day_key} - {meal_type}] Candidate generation (count={per_template_count}): {time.perf_counter()-t0:.3f}s")
                            stats["constraint_pressure"]["total_candidates"] += gen_stats["total_candidates"]
                            stats["constraint_pressure"]["passed_structure"] += gen_stats["passed_structure"]
                            
                            # Data-driven template feasibility check
                            template_can_hit_macros = False
                            for cand in candidates:
                                max_cal, max_pro = self.portion_optimizer.get_max_capacity(cand)
                                if max_pro >= target_macros['protein'] * 0.60 and max_cal >= target_macros['calories'] * 0.60:
                                    template_can_hit_macros = True
                                    break
                                    
                            if not template_can_hit_macros and candidates:
                                # Reject the template
                                logger.debug(f"Template {template.get('id')} rejected dynamically: unable to reach macros.")
                                stats["failure_reasons"]["protein_impossible"] += 1
                                continue
                                
                            evaluated_templates += 1
                            
                            feasible_candidates = []
                            for candidate_plate in candidates:
                                anchor_sem = candidate_plate[0].get('semantics', {})
                                meal_id = anchor_sem.get('meal_id', 'dynamic_meal')
                                foods = [item['food_name'] for item in candidate_plate]
                                protein_source = anchor_sem.get('protein_source')
                                carb_source = anchor_sem.get('carb_source')
                                cuisine = anchor_sem.get('cuisine')
                                cooking_style = anchor_sem.get('cooking_style')
                                
                                # Enforce rotation & same-day duplicate prevention
                                if self.variety_tracker.is_duplicate_meal(meal_id, foods, protein_source, carb_source, day_num, meal_type, cuisine, cooking_style):
                                    continue
                                    
                                # Supplement Policy Engine & Whey Limitation
                                has_whey = any('whey' in f.lower() for f in foods)
                                if has_whey:
                                    whey_limit = 2 if user_profile.get('goal') == 'Muscle Gain' else 1
                                    if whey_used_today >= whey_limit:
                                        continue
                                    if meal_type == 'snack':
                                        if target_macros['protein'] <= 25.0:
                                            # Prefer whole foods over whey for low protein targets
                                            continue
                                        if target_macros['protein'] > 35.0 and len(foods) < 2:
                                            # For high targets, require whey + something else (not whey alone)
                                            continue
                                            
                                # --- FAST PRUNING ---
                                # Check if this plate can mathematically reach the macro targets before running SciPy
                                max_cal, max_pro = self.portion_optimizer.get_max_capacity(candidate_plate)
                                prune_factor = 0.50 if meal_type == "snack" else 0.75
                                if max_pro < target_macros['protein'] * prune_factor or max_cal < target_macros['calories'] * prune_factor:
                                    continue # Skip expensive optimization, this plate can never hit the targets
                                    
                                cul_score = self.meal_scorer.score_culinary(candidate_plate, day_num)
                                feasible_candidates.append((cul_score, candidate_plate))
                            
                            # Sort by culinary score to optimize the most realistic meals first, limit to top 1
                            feasible_candidates.sort(key=lambda x: x[0], reverse=True)
                            
                            for cul_score, candidate_plate in feasible_candidates[:1]:
                                t1 = time.perf_counter()
                                optimized_plate = self.portion_optimizer.optimize_portions(candidate_plate, target_macros)
                                logger.info(f"[{day_key} - {meal_type}] Portion optimization: {time.perf_counter()-t1:.3f}s")
                                
                                t2 = time.perf_counter()
                                score_dict = self.meal_scorer.score_candidate_plate(
                                    optimized_plate, 
                                    target_macros, 
                                    current_day=day_num,
                                    meal_type=meal_type,
                                    goal=user_profile.get("goal", "Maintenance"),
                                    previous_meals=[]
                                )
                                logger.info(f"[{day_key} - {meal_type}] Meal scoring: {time.perf_counter()-t2:.3f}s")
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
                            
                            # Early Exit: If we found an excellent plate, stop evaluating more templates
                            if best_score >= 75:
                                break
                                    
                            if evaluated_templates >= 5:
                                break
                        # Pass 2: Fallback constraints if strict pass failed to find anything
                        if not best_plate:
                            _seed_p2 = day_num * 1000 + meal_type_idx * 100 + attempts + 500
                            for template in feasible_templates[:5]:
                                candidates, _ = self.candidate_generator.generate_candidates(
                                    template, meal_type, diet_type, count=10,
                                    user_profile=user_profile, day_seed=_seed_p2,
                                    excluded_foods=excluded_foods_today,
                                    daily_context=daily_context,
                                    daily_targets=daily_target,
                                )
                                feasible_candidates = []
                                for candidate_plate in candidates:
                                    anchor_sem = candidate_plate[0]['semantics']
                                    meal_id = anchor_sem.get('meal_id')
                                    foods = [item['food_name'] for item in candidate_plate]
                                    
                                    # Pass 2 Fallback: Allow meals with at most 1 prior appearance,
                                    # but hard-block any meal that has already appeared 2+ times this week.
                                    # This prevents repetition even in fallback scenarios.
                                    if meal_id and self.variety_tracker.meal_appearance_counts.get(meal_id, 0) >= 2:
                                        continue
                                    
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
                                                
                                    # Fast pruning for fallback as well
                                    max_cal, max_pro = self.portion_optimizer.get_max_capacity(candidate_plate)
                                    prune_factor_fb = 0.40 if meal_type == "snack" else 0.60
                                    if max_pro < target_macros['protein'] * prune_factor_fb or max_cal < target_macros['calories'] * prune_factor_fb:
                                        continue
                                        
                                    cul_score = self.meal_scorer.score_culinary(candidate_plate, day_num)
                                    feasible_candidates.append((cul_score, candidate_plate))
                                
                                feasible_candidates.sort(key=lambda x: x[0], reverse=True)
                                
                                for cul_score, candidate_plate in feasible_candidates[:1]:
                                    optimized_plate = self.portion_optimizer.optimize_portions(candidate_plate, target_macros)
                                    
                                    score_dict = self.meal_scorer.score_candidate_plate(
                                        optimized_plate, 
                                        target_macros, 
                                        current_day=day_num,
                                        meal_type=meal_type,
                                        goal=user_profile.get("goal", "Maintenance"),
                                        previous_meals=[]
                                    )
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
                                
                                # Early Exit for Fallback
                                if best_score >= 50:
                                    break
                                        
                        # Pass 3: Best Effort Fallback — still enforce food-name uniqueness within plate
                        if not best_plate and best_effort_plate:
                            # Guard: reject if any food_name appears twice in the plate
                            plate_names_p3 = [item.get("food_name", "").lower().strip() for item in best_effort_plate]
                            if len(set(plate_names_p3)) == len(plate_names_p3):
                                best_plate = best_effort_plate
                                logger.debug(f"Used best effort fallback for {meal_type} on day {day_num} (failed strict constraints)")
                                    
                        stats["acceptance_stats"]["total_generated"] += 1
                        # 6. Apply Best Plate
                        if best_plate:
                            stats["acceptance_stats"]["total_accepted"] += 1
                            plate_p = sum(float(i['nutrition']['protein']) for i in best_plate)
                            plate_c = sum(float(i['nutrition']['calories']) for i in best_plate)
                            plate_p = sum(float(i['nutrition']['protein']) for i in best_plate)
                            plate_carbs = sum(float(i['nutrition']['carbs']) for i in best_plate)
                            plate_f = sum(float(i['nutrition']['fat']) for i in best_plate)
                            
                            day_plan[meal_type] = best_plate
                            day_total_macros["calories"] += plate_c
                            day_total_macros["protein"] += plate_p
                            day_total_macros["carbs"] += plate_carbs
                            day_total_macros["fat"] += plate_f
                            
                            has_whey = any('whey' in i['food_name'].lower() for i in best_plate)
                            if has_whey:
                                whey_used_today += 1
                            
                            running_deficit["calories"] = target_macros["calories"] - plate_c
                            running_deficit["protein"] = target_macros["protein"] - plate_p
                            running_deficit["carbs"] = target_macros["carbs"] - plate_carbs
                            running_deficit["fat"] = target_macros["fat"] - plate_f
                            
                            # 7. Track variety
                            anchor_sem = best_plate[0].get('semantics', {})
                            meal_id = anchor_sem.get('meal_id', 'dynamic_meal')
                            foods = [item['food_name'] for item in best_plate]
                            protein_source = best_plate[0]['semantics'].get('protein_source')
                            carb_source = best_plate[0]['semantics'].get('carb_source')
                            vegetables = best_plate[0]['semantics'].get('vegetables', [])
                            cuisine = best_plate[0]['semantics'].get('cuisine')
                            cooking_style = best_plate[0]['semantics'].get('cooking_style')

                            # Update daily context with this meal's ingredients
                            daily_context.record_meal(best_plate)
                            
                            # Compute Meal Signature
                            sig_parts = []
                            for item in best_plate:
                                cat = item['semantics'].get('category', '')
                                icuisine = item['semantics'].get('cuisine', '')
                                sig_parts.append(f"{cat}-{icuisine}")
                            sig_parts.sort()
                            meal_signature = "|".join(sig_parts)

                            self.variety_tracker.record_meal_selection(
                                meal_id=meal_id,
                                foods=foods,
                                protein_source=protein_source,
                                carb_source=carb_source,
                                vegetables=vegetables,
                                day_num=day_num,
                                cuisine=cuisine,
                                cooking_style=cooking_style,
                                meal_signature=meal_signature,
                                food_ids=[str(i.get('food_id', i.get('food_name', ''))).lower() for i in best_plate],
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
                        
                    # Soft Constraint Relaxation — tolerances driven by nutrition_rules.yaml
                    # [daily_validator.calories/protein.first_attempt / second_attempt / final]
                    _dv = NUTRITION_RULES.get("daily_validator", {})
                    _dv_cal = _dv.get("calories", {})
                    _dv_pro = _dv.get("protein", {})
                    if attempts <= 2:
                        allowed_cal_var = _dv_cal.get("first_attempt", 0.12)
                        allowed_pro_var = _dv_pro.get("first_attempt", 0.12)
                    elif attempts <= 4:
                        allowed_cal_var = _dv_cal.get("second_attempt", 0.15)
                        allowed_pro_var = _dv_pro.get("second_attempt", 0.15)
                    else:
                        allowed_cal_var = _dv_cal.get("final", 0.20)
                        allowed_pro_var = _dv_pro.get("final", 0.20)

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
                                anchor_sem = best_plate[0].get('semantics', {})
                                meal_id = anchor_sem.get('meal_id', 'dynamic_meal')
                                foods = [item['food_name'] for item in best_plate]
                                protein_source = best_plate[0]['semantics'].get('protein_source')
                                carb_source = best_plate[0]['semantics'].get('carb_source')
                                vegetables = best_plate[0]['semantics'].get('vegetables', [])
                                cuisine = best_plate[0]['semantics'].get('cuisine')
                                cooking_style = best_plate[0]['semantics'].get('cooking_style')
                                
                                # Compute Meal Signature
                                sig_parts = []
                                for item in best_plate:
                                    cat = item['semantics'].get('category', '')
                                    icuisine = item['semantics'].get('cuisine', '')
                                    sig_parts.append(f"{cat}-{icuisine}")
                                sig_parts.sort()
                                meal_signature = "|".join(sig_parts)

                                self.variety_tracker.record_meal_selection(
                                    meal_id=meal_id,
                                    foods=foods,
                                    protein_source=protein_source,
                                    carb_source=carb_source,
                                    vegetables=vegetables,
                                    day_num=day_num,
                                    cuisine=cuisine,
                                    cooking_style=cooking_style,
                                    meal_signature=meal_signature,
                                    food_ids=[str(i.get('food_id', i.get('food_name', ''))).lower() for i in best_plate],
                                )
                                for item in best_plate:
                                    family = item['semantics'].get('family', 'other')
                                    self.variety_tracker.record_food(item['food_id'], family, day_num)
                                    
                if not best_day_plan:
                    best_day_plan = day_plan

                # Store under the standard day key (Day_1, Day_2, ...)
                weekly_plan[day_key] = best_day_plan
                
                if not day_plan_valid:
                    pass # We do not mark week invalid because we soft-accepted the best attempt
                week_diff_score += best_combined_diff
            # ── end of per-day loop ──────────────────────────────────────────────
            
            # Always return the weekly plan after one full pass! (Never throw away 6 good days just because 1 failed)
            return {"plan": weekly_plan, "stats": stats}


    def _is_plate_visually_balanced(self, optimized_plate: List[Dict]) -> bool:
        """
        Ensures the plate is visually balanced (e.g. not 4 rotis with only 50g dal).
        """
        carb_qty = 0.0
        protein_qty = 0.0
        has_gravy_or_curry = False
        has_carb_base = False
        has_protein_main = False
        
        for item in optimized_plate:
            name_lower = str(item.get("food_name", "")).lower()
            qty = float(item.get("serving_qty", 1))
            unit = str(item.get("serving_unit", "g")).lower().strip()
            role = item.get("semantics", {}).get("meal_role", "")
            styles = item.get("semantics", {}).get("cooking_style", "")
            
            if role == "carb_base":
                has_carb_base = True
            if role == "protein_main":
                has_protein_main = True
                
            if "Gravy" in styles or "Curry" in styles or "dal" in name_lower:
                has_gravy_or_curry = True
                
            # Identify carbs
            if any(x in name_lower for x in ['roti', 'chapati', 'phulka', 'rice', 'pulao', 'bread', 'paratha', 'dosa']):
                carb_qty += qty if unit in ('piece', 'pieces', 'plate', 'plates', 'slice', 'slices') else (qty / 150.0)
                
            # Identify proteins/curries
            if any(x in name_lower for x in ['dal', 'paneer', 'chicken', 'egg', 'fish', 'soya', 'chana', 'rajma', 'curry']):
                protein_qty += qty if unit in ('bowl', 'bowls') else (qty / 150.0)
                
        # Dry meal check (e.g. Chicken + Rice but no gravy)
        if has_protein_main and has_carb_base and not has_gravy_or_curry:
            # Maybe it's a dry protein and a dry carb, which is too dry
            pass # We rely on realism score for this, but could hard-fail
            
        # Missing carb base check for main meals (Lunch/Dinner)
        # Assuming lunch/dinner usually have a carb base or are a combo meal
        # Since we don't have meal_type here easily, we rely on the candidate generator rules
                
        # If we have a significant amount of carbs, we need a proportional amount of protein/curry to eat it with
        if carb_qty >= 3.0 and protein_qty < 0.8:
            return False # E.g., 3 rotis but less than 1 bowl of dal
            
        if carb_qty >= 2.0 and protein_qty < 0.4:
            return False
            
        # Is it just Dal + Raita? (Missing carb base but has high protein/side volume)
        if protein_qty >= 1.0 and carb_qty == 0.0:
            # It's possible for low carb diets, so we let it pass if macros demand it,
            # but usually candidate generator will ensure a carb base exists if required.
            pass
            
        return True


