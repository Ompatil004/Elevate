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

    def _get_meal_cuisine(self, candidate_plate: List[Dict]) -> str:
        """
        Identifies and normalizes the cuisine of a meal by scanning all its items.
        Prioritizes non-Pan Indian cuisines if any item has one, so a Maharashtrian
        meal that includes a Pan Indian side dish is still classified as Maharashtrian.
        Falls back to 'Pan Indian' if no specific cuisine is found.
        """
        non_pan_indian = None
        for item in candidate_plate:
            sem = item.get('semantics', {})
            _rc = item.get('regional_cuisine') or sem.get('regional_cuisine') or sem.get('cuisine')
            cuisine = (_rc.get('primary') if isinstance(_rc, dict) else _rc) or 'Pan Indian'
            cuisine_clean = str(cuisine).strip()
            if cuisine_clean.lower() not in ('pan indian', 'pan_indian', ''):
                if non_pan_indian is None:
                    non_pan_indian = cuisine_clean
        return non_pan_indian if non_pan_indian else 'Pan Indian'

    def generate_weekly_plan(self, user_profile: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generates a full 7-day meal plan respecting strict target compliance.
        Returns a dictionary containing "plan" and "stats".
        """
        start_time = time.perf_counter()
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
        diet_val_lower = str(diet_val).strip().lower()
        if diet_val_lower in ('veg', 'vegetarian', 'lacto-vegetarian', 'lacto vegetarian'):
            user_profile['diet_type'] = 'Vegetarian'
        elif diet_val_lower in ('non-veg', 'nonveg', 'non veg', 'non vegetarian', 'non-vegetarian',
                                 'meat eater', 'omnivore'):
            user_profile['diet_type'] = 'NonVeg'
        elif diet_val_lower in ('vegan', 'plant-based', 'plant based'):
            user_profile['diet_type'] = 'Vegan'
        elif diet_val_lower in ('eggetarian',):
            # Eggetarian: vegetarian + eggs (treat as Vegetarian but allow egg foods)
            user_profile['diet_type'] = 'Vegetarian'
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
            
            total_meal_slots = 0
            fallback_meal_slots = 0
            
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
                        total_meal_slots += 1
                        # Apply running deficit to current target, but cap min to 50% to prevent negative runaway targets
                        cals_def = running_deficit["calories"]
                        pro_def = running_deficit["protein"]
                        carbs_def = running_deficit["carbs"]
                        fat_def = running_deficit["fat"]
                        
                        if meal_type == "snack":
                            cals_def = max(-base_target_macros["calories"] * 0.5, min(cals_def, base_target_macros["calories"] * 0.5))
                            pro_def = max(-10.0, min(pro_def, 10.0))  # cap snack protein deficit to ±10g
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
                        best_score_dict = {}
                        best_effort_plate = None
                        best_effort_score = -1000
                        best_effort_score_dict = {}
                        is_fallback_used = False

                        
                        # Pass 1: Strict constraints (Rotation & Portion limits)
                        # Seed = day_num * 1000 + meal_type_idx * 100 + attempts
                        # This guarantees a unique shuffle for every (day, meal_type, attempt) combination
                        _seed_p1 = day_num * 1000 + meal_type_idx * 100 + attempts
                        evaluated_templates = 0
                        
                        # Dynamic candidate distribution
                        target_counts = {'breakfast': 12, 'lunch': 15, 'dinner': 15, 'snack': 8}
                        total_target = target_counts.get(meal_type, 12)
                        per_template_count = max(2, total_target // max(1, len(feasible_templates)))
                        
                        candidate_pool = []
                        for template in feasible_templates:
                            t0 = time.perf_counter()
                            candidates, gen_stats = self.candidate_generator.generate_candidates(
                                template=template,
                                meal_type=meal_type,
                                diet_type=diet_type,
                                count=per_template_count,
                                user_profile=user_profile,
                                day_seed=_seed_p1,
                                excluded_foods=excluded_foods_today,
                                daily_context=daily_context,
                                daily_targets=daily_target,
                                variety_tracker=self.variety_tracker,
                                day_num=day_num,
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
                            
                            for candidate_plate in candidates:
                                anchor_sem = candidate_plate[0].get('semantics', {})
                                meal_id = anchor_sem.get('meal_id', 'dynamic_meal')
                                foods = [item['food_name'] for item in candidate_plate]
                                protein_source = anchor_sem.get('protein_source')
                                carb_source = anchor_sem.get('carb_source')
                                cuisine = self._get_meal_cuisine(candidate_plate)
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
                                        if target_macros['protein'] <= 15.0:
                                            # Prefer whole foods over whey for low protein targets
                                            continue
                                        if target_macros['protein'] > 35.0 and len(foods) < 2:
                                            # For high targets, require whey + something else (not whey alone)
                                            continue
                                            
                                # --- FAST PRUNING ---
                                # Check if this plate can mathematically reach the macro targets before running SciPy
                                max_cal, max_pro = self.portion_optimizer.get_max_capacity(candidate_plate)
                                # Use 0.50 for all meal types — 0.75 was too aggressive and caused near-zero acceptance
                                prune_factor = 0.50
                                if max_pro < target_macros['protein'] * prune_factor or max_cal < target_macros['calories'] * prune_factor:
                                    continue # Skip expensive optimization, this plate can never hit the targets
                                    
                                candidate_pool.append(candidate_plate)
                                
                            if evaluated_templates >= 5:
                                break

                        # Optimize portions and score all strict candidates
                        scored_candidates = []
                        for candidate_plate in candidate_pool:
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
                                previous_meals=[],
                                preferred_region=user_profile.get("preferred_region") or user_profile.get("region")
                            )
                            logger.info(f"[{day_key} - {meal_type}] Meal scoring: {time.perf_counter()-t2:.3f}s")
                            total_score = score_dict["total_score"]
                            
                            # Best effort tracking (ignores 85% rule and visual balance)
                            if total_score > best_effort_score:
                                best_effort_score = total_score
                                best_effort_plate = optimized_plate
                                best_effort_score_dict = score_dict
                                
                            # Enforce Visual Plate Balance
                            if not self._is_plate_visually_balanced(optimized_plate):
                                continue
                                
                            plate_p = sum(float(i['nutrition']['protein']) for i in optimized_plate)
                            
                            # Must hit between 85% and 115% of target protein for strict pass
                            if plate_p < target_macros['protein'] * 0.85 or plate_p > target_macros['protein'] * 1.15:
                                continue
                                
                            scored_candidates.append((optimized_plate, total_score, score_dict))

                        # Perform Weighted Selection for Strict Pass
                        if scored_candidates:
                            # Strict consecutive breakfast category filter
                            if meal_type.lower() == 'breakfast':
                                yesterday_cat = self.variety_tracker.daily_breakfast_category.get(day_num - 1)
                                if yesterday_cat:
                                    non_consec_candidates = []
                                    for plate, total_score, score_dict in scored_candidates:
                                        plate_cat = None
                                        for item in plate:
                                            plate_cat = item.get('semantics', {}).get('breakfast_category')
                                            if plate_cat:
                                                break
                                        if plate_cat != yesterday_cat:
                                            non_consec_candidates.append((plate, total_score, score_dict))
                                    if non_consec_candidates:
                                        scored_candidates = non_consec_candidates
                            
                            import math
                            import random as _rng
                            scored_candidates.sort(key=lambda x: x[1], reverse=True)
                            top_k = int(NUTRITION_RULES.get("candidate_selection", {}).get("top_k", 15))
                            temp = float(NUTRITION_RULES.get("candidate_selection", {}).get("temperature", 1.0))
                            top_candidates = scored_candidates[:top_k]
                            
                            max_score = max(item[1] for item in top_candidates)
                            # Scaled Softmax to avoid overflow
                            exp_scores = [math.exp((item[1] - max_score) / temp) for item in top_candidates]
                            sum_exp = sum(exp_scores)
                            weights = [e / sum_exp for e in exp_scores]
                            
                            rng_select = _rng.Random(_seed_p1)
                            best_plate, best_score, best_score_dict = rng_select.choices(top_candidates, weights=weights, k=1)[0]
                            
                        # Pass 2: Fallback constraints if strict pass failed to find anything
                        if not best_plate:
                            is_fallback_used = True
                            _seed_p2 = day_num * 1000 + meal_type_idx * 100 + attempts + 500
                            candidate_pool_fb = []
                            for template in feasible_templates[:5]:
                                candidates, _ = self.candidate_generator.generate_candidates(
                                    template=template,
                                    meal_type=meal_type,
                                    diet_type=diet_type,
                                    count=10,
                                    user_profile=user_profile,
                                    day_seed=_seed_p2,
                                    excluded_foods=excluded_foods_today,
                                    daily_context=daily_context,
                                    daily_targets=daily_target,
                                    variety_tracker=self.variety_tracker,
                                    day_num=day_num,
                                )
                                for candidate_plate in candidates:
                                    anchor_sem = candidate_plate[0]['semantics']
                                    meal_id = anchor_sem.get('meal_id')
                                    foods = [item['food_name'] for item in candidate_plate]
                                    
                                    # Fallback frequency checking
                                    if meal_id and self.variety_tracker.meal_appearance_counts.get(meal_id, 0) >= 2:
                                        continue
                                        
                                    # Enforce rotation & same-day duplicate prevention in fallback
                                    if self.variety_tracker.is_duplicate_meal(meal_id, foods, None, None, day_num, meal_type):
                                        continue
                                        
                                    has_whey = any('whey' in f.lower() for f in foods)
                                    if has_whey:
                                        if whey_used_today >= 1:
                                            continue
                                        if meal_type == 'snack':
                                            if target_macros['protein'] <= 15.0:
                                                continue
                                            if target_macros['protein'] > 35.0 and len(foods) < 2:
                                                continue
                                                
                                    max_cal, max_pro = self.portion_optimizer.get_max_capacity(candidate_plate)
                                    prune_factor_fb = 0.40 if meal_type == "snack" else 0.60
                                    if max_pro < target_macros['protein'] * prune_factor_fb or max_cal < target_macros['calories'] * prune_factor_fb:
                                        continue
                                        
                                    candidate_pool_fb.append(candidate_plate)
                                    
                            # Optimize and score fallback pool
                            scored_candidates_fb = []
                            for candidate_plate in candidate_pool_fb:
                                optimized_plate = self.portion_optimizer.optimize_portions(candidate_plate, target_macros)
                                
                                score_dict = self.meal_scorer.score_candidate_plate(
                                    optimized_plate, 
                                    target_macros, 
                                    current_day=day_num,
                                    meal_type=meal_type,
                                    goal=user_profile.get("goal", "Maintenance"),
                                    previous_meals=[],
                                    preferred_region=user_profile.get("preferred_region") or user_profile.get("region")
                                )
                                total_score = score_dict["total_score"] - 30 # Penalize fallback slightly
                                
                                # Best effort tracking (ignores 85% rule and visual balance)
                                if total_score > best_effort_score:
                                    best_effort_score = total_score
                                    best_effort_plate = optimized_plate
                                    best_effort_score_dict = score_dict
                                    
                                # Enforce Visual Plate Balance
                                if not self._is_plate_visually_balanced(optimized_plate):
                                    continue
                                    
                                scored_candidates_fb.append((optimized_plate, total_score, score_dict))
                                
                            if scored_candidates_fb:
                                # Strict consecutive breakfast category filter in fallback
                                if meal_type.lower() == 'breakfast':
                                    yesterday_cat = self.variety_tracker.daily_breakfast_category.get(day_num - 1)
                                    if yesterday_cat:
                                        non_consec_candidates_fb = []
                                        for plate, total_score, score_dict in scored_candidates_fb:
                                            plate_cat = None
                                            for item in plate:
                                                plate_cat = item.get('semantics', {}).get('breakfast_category')
                                                if plate_cat:
                                                    break
                                            if plate_cat != yesterday_cat:
                                                non_consec_candidates_fb.append((plate, total_score, score_dict))
                                        if non_consec_candidates_fb:
                                            scored_candidates_fb = non_consec_candidates_fb
                                            
                                import math
                                import random as _rng
                                scored_candidates_fb.sort(key=lambda x: x[1], reverse=True)
                                top_k = int(NUTRITION_RULES.get("candidate_selection", {}).get("top_k", 15))
                                temp = float(NUTRITION_RULES.get("candidate_selection", {}).get("temperature", 1.0))
                                top_candidates_fb = scored_candidates_fb[:top_k]
                                
                                max_score = max(item[1] for item in top_candidates_fb)
                                exp_scores = [math.exp((item[1] - max_score) / temp) for item in top_candidates_fb]
                                sum_exp = sum(exp_scores)
                                weights = [e / sum_exp for e in exp_scores]
                                
                                rng_select_fb = _rng.Random(_seed_p2)
                                best_plate, best_score, best_score_dict = rng_select_fb.choices(top_candidates_fb, weights=weights, k=1)[0]
                                
                        # Pass 4: Final Emergency Fallback
                        if not best_plate:
                            logger.warning(f"Final emergency fallback triggered for {meal_type} on day {day_num}")
                            fallback_plate = self.candidate_generator._build_fallback_meal(
                                meal_type=meal_type,
                                diet_type=diet_type,
                                excluded_foods=excluded_foods_today,
                                goal=user_profile.get("goal", "Maintenance"),
                                meal_cals=target_macros["calories"],
                                variety_tracker=self.variety_tracker,
                                day_num=day_num,
                                user_profile=user_profile
                            )
                            if fallback_plate:
                                best_plate = self.portion_optimizer.optimize_portions(fallback_plate, target_macros)
                                best_score_dict = {"total_score": 0}
                                    
                        stats["acceptance_stats"]["total_generated"] += 1
                        # 6. Apply Best Plate
                        if best_plate:
                            if is_fallback_used:
                                fallback_meal_slots += 1
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
                            cuisine = self._get_meal_cuisine(best_plate)
                            cooking_style = best_plate[0]['semantics'].get('cooking_style')

                            # Update daily context with this meal's ingredients
                            daily_context.record_meal(best_plate)
                            
                            # Attach score breakdown to selected items
                            for item in best_plate:
                                item["score_breakdown"] = best_score_dict.get("breakdown", {})

                            # Compute Meal Signature
                            sig_parts = []
                            for item in best_plate:
                                cat = item['semantics'].get('category', '')
                                icuisine = item['semantics'].get('cuisine', '')
                                sig_parts.append(f"{cat}-{icuisine}")
                            sig_parts.sort()
                            meal_signature = "|".join(sig_parts)

                            breakfast_category = None
                            if meal_type.lower() == 'breakfast':
                                for item in best_plate:
                                    breakfast_category = item.get('semantics', {}).get('breakfast_category')
                                    if breakfast_category:
                                        break

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
                                breakfast_category=breakfast_category,
                            )
                            
                            for item in best_plate:
                                family = item['semantics'].get('dish_family') or item['semantics'].get('family', 'other')
                                self.variety_tracker.record_food(item['food_id'], family, day_num)
                        else:
                            logger.warning(f"No strict candidates found for {meal_type} on day {day_num}; using best-effort plate")
                            if best_effort_plate:
                                # Use best available candidate even if it didn't pass all strict constraints
                                day_plan[meal_type] = best_effort_plate
                                logger.info(f"[{day_key} - {meal_type}] Best-effort plate applied: {[i.get('food_name') for i in best_effort_plate]}")
                            else:
                                logger.error(f"No candidates at all for {meal_type} on day {day_num}: meal left empty")
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
                    if attempts >= max_daily_attempts:
                        allowed_cal_var = _dv_cal.get("final", 0.08)
                        allowed_pro_var = _dv_pro.get("final", 0.08)
                    elif attempts <= 2:
                        allowed_cal_var = _dv_cal.get("first_attempt", 0.03)
                        allowed_pro_var = _dv_pro.get("first_attempt", 0.03)
                    else:
                        allowed_cal_var = _dv_cal.get("second_attempt", 0.05)
                        allowed_pro_var = _dv_pro.get("second_attempt", 0.05)

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
                                cuisine = self._get_meal_cuisine(best_plate)
                                cooking_style = best_plate[0]['semantics'].get('cooking_style')
                                
                                # Compute Meal Signature
                                sig_parts = []
                                for item in best_plate:
                                    cat = item['semantics'].get('category', '')
                                    icuisine = item['semantics'].get('cuisine', '')
                                    sig_parts.append(f"{cat}-{icuisine}")
                                sig_parts.sort()
                                meal_signature = "|".join(sig_parts)

                                breakfast_category = None
                                if meal_type.lower() == 'breakfast':
                                    for item in best_plate:
                                        breakfast_category = item.get('semantics', {}).get('breakfast_category')
                                        if breakfast_category:
                                            break

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
                                    breakfast_category=breakfast_category,
                                )
                                for item in best_plate:
                                    family = item['semantics'].get('dish_family') or item['semantics'].get('family', 'other')
                                    self.variety_tracker.record_food(item['food_id'], family, day_num)
                                    
                if not best_day_plan:
                    best_day_plan = day_plan

                # Store under the standard day key (Day_1, Day_2, ...)
                weekly_plan[day_key] = best_day_plan
                
                if not day_plan_valid:
                    pass # We do not mark week invalid because we soft-accepted the best attempt
                week_diff_score += best_combined_diff
            # ── end of per-day loop ──────────────────────────────────────────────
            
            # Calculate duration and stats, log structured weekly summary
            generation_duration = time.perf_counter() - start_time
            total_generated = stats["acceptance_stats"]["total_generated"]
            total_accepted = stats["acceptance_stats"]["total_accepted"]
            acceptance_rate = (total_accepted / total_generated * 100.0) if total_generated > 0 else 0.0
            fallback_rate = (fallback_meal_slots / total_meal_slots * 100.0) if total_meal_slots > 0 else 0.0
            
            logger.info(
                "\n"
                "==================================================\n"
                "                  WEEKLY_SUMMARY                  \n"
                "==================================================\n"
                f"  duration_seconds:           {generation_duration:.3f}\n"
                f"  total_meals:                {total_meal_slots}\n"
                f"  fallback_meals:             {fallback_meal_slots}\n"
                f"  fallback_rate:              {fallback_rate:.2f}%\n"
                f"  total_generated_candidates: {total_generated}\n"
                f"  total_accepted_candidates:  {total_accepted}\n"
                f"  acceptance_rate:            {acceptance_rate:.2f}%\n"
                f"  recovery_successes:         {stats['acceptance_stats']['recovery_successes']}\n"
                f"  recovery_failures:          {stats['acceptance_stats']['recovery_failures']}\n"
                "=================================================="
            )

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


