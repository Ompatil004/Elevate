"""
MealEngine — Legacy wrapper kept for backward compatibility only.
Now powered by NutritionEngineV6 under the hood.
"""

import os
from typing import Dict, List
from datetime import datetime, timezone
try:
    from zoneinfo import ZoneInfo  # Python 3.9+
except Exception:  # pragma: no cover - fallback for older runtimes
    ZoneInfo = None

from .nutrition_engine.engine import NutritionEngineV6

try:
    _IST = ZoneInfo('Asia/Kolkata') if ZoneInfo else timezone.utc
except Exception:
    _IST = timezone.utc

class MealEngine:
    """
    Thin wrapper kept for backward-compatibility only.
    All heavy lifting is done by NutritionEngineV6.
    """

    def __init__(self):
        print("\n[MealEngine] Initializing Nutrition Engine V6...")
        base_dir = os.path.dirname(__file__)
        data_dir = os.path.join(base_dir, '..', 'data')
        config_dir = os.path.join(base_dir, '..', 'config')
        print(f"[MealEngine] Config directory resolved to: {config_dir}")
        print(f"[MealEngine] Config directory exists: {os.path.exists(config_dir)}")
        print(f"[MealEngine] Templates exist: {os.path.exists(os.path.join(config_dir, 'meal_templates.yaml'))}")
        self.engine = NutritionEngineV6(data_dir=data_dir, config_dir=config_dir)
        
        self.intensity_multipliers = {
            'rest': 0.90,
            'light': 0.95,
            'moderate': 1.00,
            'hard': 1.10,
            'very_hard': 1.18,
        }
        print("[MealEngine] V6 Engine Ready\n")

    def _normalize_intensity(self, value: str) -> str:
        text = str(value or '').strip().lower().replace(' ', '_')
        aliases = {
            'veryhard': 'very_hard',
            'very-hard': 'very_hard',
            'high': 'hard',
            'easy': 'light',
            'recovery': 'rest',
        }
        text = aliases.get(text, text)
        return text if text in self.intensity_multipliers else 'moderate'

    def _day_name_from_workout(self, day: Dict) -> str:
        day_name = day.get('day') or day.get('day_name')
        if isinstance(day_name, str) and day_name:
            return day_name.split()[0].title()

        idx = day.get('day_of_week')
        if isinstance(idx, int) and 0 <= idx <= 6:
            names = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
            return names[idx]
        return ''

    def _infer_intensity_from_workout_day(self, day: Dict) -> str:
        focus = str(day.get('focus', '')).lower()
        note = str(day.get('note', '')).lower()
        if day.get('type') == 'rest' or 'rest' in focus or 'rest' in note:
            return 'rest'

        exercises = day.get('exercises') or []
        count = len(exercises)
        total_sets = 0
        for ex in exercises:
            sets_raw = str((ex or {}).get('sets', '0'))
            digits = ''.join(ch for ch in sets_raw if ch.isdigit())
            if digits:
                total_sets += int(digits)

        if count >= 8 or total_sets >= 28:
            return 'very_hard'
        if count >= 6 or total_sets >= 20:
            return 'hard'
        if count >= 3 or total_sets >= 10:
            return 'moderate'
        return 'light'

    def _build_intensity_by_day(self, user_profile: Dict, fallback_intensity: str) -> Dict[str, str]:
        default_intensity = self._normalize_intensity(fallback_intensity)
        by_day = {
            'Monday': default_intensity,
            'Tuesday': default_intensity,
            'Wednesday': default_intensity,
            'Thursday': default_intensity,
            'Friday': default_intensity,
            'Saturday': default_intensity,
            'Sunday': default_intensity,
        }

        workout_plan = user_profile.get('weekly_workout_plan')
        if not isinstance(workout_plan, list) or not workout_plan:
            return by_day

        for day in workout_plan:
            if not isinstance(day, dict):
                continue
            day_name = self._day_name_from_workout(day)
            if not day_name:
                continue

            intensity_metrics = day.get('intensity_metrics')
            intensity_cat = intensity_metrics.get('category') if isinstance(intensity_metrics, dict) else None
            
            if isinstance(intensity_cat, str):
                by_day[day_name] = self._normalize_intensity(intensity_cat)
            else:
                explicit = day.get('intensity')
                if explicit is not None and explicit != '':
                    if isinstance(explicit, str):
                        by_day[day_name] = self._normalize_intensity(explicit)
                    elif isinstance(explicit, (int, float)):
                        score = float(explicit)
                        if score <= 0.05:
                            cat = 'rest'
                        elif score < 0.35:
                            cat = 'light'
                        elif score < 0.65:
                            cat = 'moderate'
                        elif score < 0.85:
                            cat = 'hard'
                        else:
                            cat = 'very_hard'
                        by_day[day_name] = cat
                    else:
                        by_day[day_name] = self._infer_intensity_from_workout_day(day)
                else:
                    by_day[day_name] = self._infer_intensity_from_workout_day(day)

        return by_day

    def _scale_meal_item(self, item: Dict, factor: float) -> Dict:
        import copy
        scaled = copy.deepcopy(item)  # FULL deep copy
        
        nutrition = scaled.setdefault('nutrition', {})
        for key in ('calories', 'protein', 'carbs', 'fat', 'fiber'):
            # Source of truth: nutrition sub-dict (set by portion_optimizer)
            value = float(nutrition.get(key, scaled.get(key, 0)) or 0)
            adjusted = round(value * factor, 1 if key != 'calories' else 0)
            nutrition[key] = adjusted    # update sub-dict
            scaled[key] = adjusted       # keep flat key in sync
        
        # food_name / name consistency
        food_name = scaled.get('food_name') or scaled.get('name', '')
        scaled['name'] = food_name
        scaled['food_name'] = food_name
        
        # serving string
        if 'serving' not in scaled and 'serving_qty' in scaled:
            qty = scaled['serving_qty']
            if isinstance(qty, float) and qty.is_integer():
                qty = int(qty)
            scaled['serving'] = f"{qty} {scaled.get('serving_unit', '')}"
            
        return scaled

    def _apply_intensity_adjustments(self, weekly_plan: Dict, intensity_by_day: Dict[str, str]) -> Dict:
        """Apply day-level intensity targets to a generated weekly meal plan without redundant scaling."""
        adjusted_weekly = {}
        adjusted_targets_by_day = {}

        # V6 now keys weekly_plan by day name (Monday..Sunday) directly.
        # Keep a fallback mapping for any legacy Day_N keys that may exist in the cache.
        _DAY_NAMES = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
        _legacy_to_name = {f"Day_{i+1}": name for i, name in enumerate(_DAY_NAMES)}
        # Reverse: day_name -> Day_N key used in plan_week() daily_targets
        _name_to_legacy = {name: f"Day_{i+1}" for i, name in enumerate(_DAY_NAMES)}

        raw_plan = weekly_plan.get('weekly_plan', {})
        # daily_targets is still keyed as Day_1..Day_7 from WeeklyMacroPlanner.plan_week()
        daily_targets = weekly_plan.get('daily_targets', {})

        for v6_day, meals in raw_plan.items():
            # Resolve to a human-readable day name
            day_name = _legacy_to_name.get(v6_day, v6_day)  # already a name if V6 new-style
            day_intensity = self._normalize_intensity(intensity_by_day.get(day_name, 'moderate'))
            factor = self.intensity_multipliers.get(day_intensity, 1.0)

            adjusted_weekly[day_name] = {}
            for meal_type, items in (meals or {}).items():
                adjusted_weekly[day_name][meal_type] = []
                for item in (items or []):
                    scaled_item = self._scale_meal_item(item, factor)
                    adjusted_weekly[day_name][meal_type].append(scaled_item)

            # Retrieve the planned target: try legacy Day_N key first, then day_name directly
            legacy_key = _name_to_legacy.get(day_name, v6_day)
            planned_target = daily_targets.get(legacy_key) or daily_targets.get(day_name) or daily_targets.get(v6_day, {})
            adjusted_targets_by_day[day_name] = {
                'calories': round(planned_target.get('calories', 2000)),
                'protein': round(planned_target.get('protein', 150), 1),
                'carbs': round(planned_target.get('carbs', 200), 1),
                'fat': round(planned_target.get('fat', 60), 1),
                'workout_intensity': day_intensity,
                'calorie_multiplier': factor,
            }

        weekly_plan['weekly_plan'] = adjusted_weekly
        weekly_plan['daily_targets_by_day'] = adjusted_targets_by_day
        weekly_plan['intensity_by_day'] = intensity_by_day
        return weekly_plan

    # ─────────────────────────────────────────────
    #  suggest_daily_meals — called by /nutrition
    # ─────────────────────────────────────────────

    def suggest_daily_meals(self, user_profile: Dict,
                            workout_intensity: str = "moderate") -> Dict:
        """
        Generate daily meal recommendations from the dataset.
        Returns exactly the format the frontend expects.
        """
        print(f"\n[MealEngine] Generating meals for {user_profile.get('goal', 'Maintenance')}"
              f" — intensity: {workout_intensity}")

        weekly_workout_plan = user_profile.get('weekly_workout_plan')
        weekly = self.generate_meal_plan(user_profile, weekly_workout_plan)

        adjusted_weekly_plan = weekly.get('weekly_plan', {})
        adjusted_targets_by_day = weekly.get('daily_targets_by_day', {})
        intensity_by_day = weekly.get('intensity_by_day', {})

        today_key = datetime.now(_IST).strftime('%A')
        if today_key not in adjusted_weekly_plan:
            today_key = list(adjusted_weekly_plan.keys())[0] if adjusted_weekly_plan else 'Monday'

        today_meals = adjusted_weekly_plan.get(today_key, {})
        today_target = adjusted_targets_by_day.get(today_key, {})

        normalized_intensity = self._normalize_intensity(workout_intensity)
        today_intensity = intensity_by_day.get(today_key, normalized_intensity)

        flat_meals = []
        for meal_type, items in today_meals.items():
            for item in items:
                flat_meals.append({
                    'meal_type':    meal_type,
                    'name':         item.get('food_name', ''),
                    'food_name':    item.get('food_name', ''),
                    'serving':      item.get('serving', ''),
                    'calories':     item.get('calories', 0),
                    'protein':      item.get('protein', 0),
                    'carbs':        item.get('carbs', 0),
                    'fat':          item.get('fat', 0),
                    'fiber':        item.get('fiber', 0),
                    'swap_group':   item.get('semantics', {}).get('family', ''),
                    'swap_options': [],
                    'meal_role':    item.get('semantics', {}).get('meal_role', ''),
                    'budget_level': item.get('semantics', {}).get('budget_level', ''),
                    'availability': 'common',
                    'tags':         '',
                    'intensity_adjusted': True,
                    'workout_intensity':  today_intensity,
                })

        print(f"[MealEngine] Generated {len(flat_meals)} meal items for {today_key}")
        
        result_dict = {
            'date': datetime.now(_IST).strftime('%Y-%m-%d'),
            'daily_target': today_target,
            'daily_targets_by_day': adjusted_targets_by_day,
            'meals': flat_meals,
            'note': (f"Daily plan for {user_profile.get('goal', 'Maintenance')} — {today_intensity} intensity"),
            'ml_powered': True,
            'consistency_score': 100,
            'shopping_list': {},
            'workout_intensity': today_intensity,
            'intensity_by_day': intensity_by_day,
            'weekly_plan': adjusted_weekly_plan,
        }

        return result_dict

    # ─────────────────────────────────────────────
    #  generate_meal_plan — weekly with workout integration
    # ─────────────────────────────────────────────

    def generate_meal_plan(self, profile: Dict,
                           weekly_workout_plan: List[Dict] = None) -> Dict:
        """
        Generate weekly meal plan using V6.
        """
        enhanced_profile = {**profile}
        if weekly_workout_plan and isinstance(weekly_workout_plan, list):
            workout_days = sum(1 for d in weekly_workout_plan if d.get('type') == 'workout')
            total_exercises = sum(
                len(d.get('exercises', [])) for d in weekly_workout_plan if d.get('type') == 'workout'
            )
            avg_exercises = total_exercises / max(workout_days, 1)

            if avg_exercises >= 8 or workout_days >= 6:
                enhanced_profile['activity_level'] = 'Very Active'
            elif avg_exercises >= 6 or workout_days >= 5:
                enhanced_profile['activity_level'] = 'Active'
            elif avg_exercises >= 3 or workout_days >= 3:
                enhanced_profile['activity_level'] = 'Moderate'
            else:
                enhanced_profile['activity_level'] = 'Light'

        enhanced_profile['weekly_workout_plan'] = weekly_workout_plan or []

        # Call V6 Engine
        weekly_plan = self.engine.generate_plan(enhanced_profile)
        
        # Apply intensity adjustments on top of the V6 plan
        intensity_by_day = self._build_intensity_by_day(enhanced_profile, 'moderate')
        weekly_plan = self._apply_intensity_adjustments(weekly_plan, intensity_by_day)
        
        weekly_plan['workout_correlation'] = {
            'intensity_by_day': intensity_by_day,
            'correlation_version': '1.1',
        }
        return weekly_plan

    def get_swap_options(self, food_name: str, meal_type: str,
                          profile: Dict, limit: int = 5,
                          target_calories: float = None,
                          target_protein: float = None) -> List[Dict]:
        """
        Fetch nutritionally similar foods from the FoodGraph.
        Nutrition values are SCALED to match the original item's calorie target
        so that swaps have the same or very similar macro values.
        Results are sorted by nutritional similarity (closest protein+calorie first).
        """
        from app.nutrition_engine.food_utils import get_food_family
        nodes = self.engine.food_graph.get_all_nodes()
        
        # 1. Find the target node and its family (multi-step fallback)
        target_node = None
        target_family = None
        food_name_lower = food_name.lower().strip()
        
        # Step 1a: exact match
        for fid, node in nodes.items():
            node_name = node.get("food_name", "").lower().strip()
            if node_name == food_name_lower or node.get("name", "").lower().strip() == food_name_lower:
                target_node = node
                target_family = node.get("semantics", {}).get("family")
                break
        
        # Step 1b: substring match (handles "Tossed Salad" → finds any salad node)
        if not target_node:
            for fid, node in nodes.items():
                node_name = node.get("food_name", "").lower().strip()
                if food_name_lower in node_name or node_name in food_name_lower:
                    target_node = node
                    target_family = node.get("semantics", {}).get("family")
                    break
        
        # Step 1c: infer family from food_utils (now uses granular families)
        if not target_family:
            target_family = get_food_family(food_name, "")
        
        # Step 1d: meal-type-based last-resort fallback
        if not target_family or target_family == "Other":
            meal_type_family_map = {
                'breakfast': 'South Indian Breakfast',
                'lunch': 'Roti',
                'dinner': 'Rice',
                'snack': 'Fruit',
            }
            target_family = meal_type_family_map.get(meal_type.lower(), 'Roti')
            
        if not target_family:
            return []

        # Use the passed targets or fall back to the original food's own nutrition at default serving
        orig_nutrition = target_node.get("nutrition", {}) if target_node else {}
        orig_serving_g = orig_nutrition.get("serving_size_g", 100.0) or 100.0
        orig_cal_per_100g = orig_nutrition.get("calories", 0)
        orig_prot_per_100g = orig_nutrition.get("protein", 0)

        # If caller provided target_calories, use those; otherwise use the food's own default serving nutrition
        if target_calories and target_calories > 0:
            cal_target = target_calories
        elif orig_cal_per_100g > 0:
            cal_target = (orig_cal_per_100g / 100.0) * orig_serving_g
        else:
            # Default reasonable calorie target per food item based on meal type
            default_cal_by_meal = {'breakfast': 200, 'lunch': 250, 'dinner': 250, 'snack': 150}
            cal_target = default_cal_by_meal.get(meal_type.lower(), 200)
        
        if target_protein and target_protein > 0:
            prot_target = target_protein
        elif orig_prot_per_100g > 0:
            prot_target = (orig_prot_per_100g / 100.0) * orig_serving_g
        else:
            prot_target = cal_target * 0.15 / 4  # default 15% protein by calories

        # 2. Extract User Diet
        user_diet = profile.get("diet_type") or profile.get("dietary_preference", "NonVeg")
        if user_diet in ('Veg', 'Vegetarian'):
            user_diet = 'Vegetarian'
        elif user_diet in ('Non-Veg', 'NonVeg', 'Non Vegetarian'):
            user_diet = 'NonVeg'
            
        def _collect_options_for_family(family_name: str) -> List:
            """Collect all graph nodes matching a family + diet filter."""
            opts = []
            for fid, node in nodes.items():
                if node == target_node:
                    continue
                node_diet = node.get("identity", {}).get("diet", "NonVeg")
                if user_diet == "Vegan" and node_diet != "Vegan":
                    continue
                if user_diet == "Vegetarian" and node_diet == "NonVeg":
                    continue
                # Also check diet via node-level food_utils family inference
                node_fname = node.get("food_name", "")
                node_sg = node.get("semantics", {}).get("swap_group", "")
                node_family = node.get("semantics", {}).get("family") or get_food_family(node_fname, node_sg)
                if node_family == family_name:
                    opts.append(node)
            return opts

        # 3. Find alternatives in same family — broaden if too few results
        options = _collect_options_for_family(target_family)
        
        # Broadening fallback: if fewer than 3 options in the specific family,
        # add foods from a related broader family
        if len(options) < 3:
            broader_map = {
                'Roti': 'South Indian Breakfast',
                'South Indian Breakfast': 'Paratha',
                'Paratha': 'Roti',
                'Rice': 'Roti',
                'Dal': 'Curry',
                'Chicken': 'Meat',
                'Meat': 'Chicken',
                'Fish': 'Chicken',
                'Paneer': 'Tofu',
                'Tofu': 'Paneer',
                'Eggs': 'Chicken',
            }
            broader_family = broader_map.get(target_family)
            if broader_family:
                extras = _collect_options_for_family(broader_family)
                options.extend(extras)

        # 4. Scale each option's nutrition to match cal_target and compute similarity score
        def _scale_and_score(node):
            n = node.get("nutrition", {})
            cal_per_100g = n.get("calories", 0)
            prot_per_100g = n.get("protein", 0)
            carb_per_100g = n.get("carbs", 0)
            fat_per_100g = n.get("fat", 0)
            fiber_per_100g = n.get("fiber", 0)
            
            # Avoid division by zero for foods with no calorie data
            if cal_per_100g <= 0:
                return None

            # Calculate how many grams we need to hit the calorie target
            grams_needed = (cal_target / cal_per_100g) * 100.0
            
            # Cap to a sensible range so we don't end up with 1000g of one food
            grams_needed = max(30.0, min(grams_needed, 500.0))
            
            scale_factor = grams_needed / 100.0
            scaled_cal  = round(cal_per_100g  * scale_factor, 1)
            scaled_prot = round(prot_per_100g * scale_factor, 1)
            scaled_carb = round(carb_per_100g * scale_factor, 1)
            scaled_fat  = round(fat_per_100g  * scale_factor, 1)
            scaled_fiber = round(fiber_per_100g * scale_factor, 1)
            
            # Similarity score: lower is better (weighted protein diff + calorie diff)
            prot_diff = abs(scaled_prot - prot_target)
            cal_diff  = abs(scaled_cal  - cal_target)
            similarity_score = (prot_diff * 2.0) + (cal_diff * 0.05)
            
            # Build a human-readable serving string
            default_unit = node.get("servings", {}).get("default_unit", "g")
            if default_unit in ("g", "ml"):
                qty = round(grams_needed)
                serving_str = f"{qty} {default_unit}"
                serving_qty = qty
                serving_unit = default_unit
            else:
                # Convert grams to the food's natural unit using its serving_size_g
                natural_unit_g = n.get("serving_size_g", 100.0) or 100.0
                units_needed = grams_needed / natural_unit_g
                units_needed = max(0.5, round(units_needed * 2) / 2)  # round to nearest 0.5
                if units_needed.is_integer():
                    units_needed = int(units_needed)
                serving_str = f"{units_needed} {default_unit}"
                serving_qty = units_needed
                serving_unit = default_unit
            
            return {
                "node": node,
                "scaled_cal": scaled_cal,
                "scaled_prot": scaled_prot,
                "scaled_carb": scaled_carb,
                "scaled_fat": scaled_fat,
                "scaled_fiber": scaled_fiber,
                "serving_str": serving_str,
                "serving_qty": serving_qty,
                "serving_unit": serving_unit,
                "similarity_score": similarity_score,
            }

        scored = []
        for opt in options:
            result = _scale_and_score(opt)
            if result:
                scored.append(result)
        
        # Sort by similarity (best match first)
        scored.sort(key=lambda x: x["similarity_score"])
        
        # 5. Format and return top results
        results = []
        for s in scored[:limit]:
            opt_node = s["node"]
            opt_name = opt_node.get("food_name", "")
            results.append({
                'meal_type':    meal_type,
                'name':         opt_name,
                'food_name':    opt_name,
                'serving':      s["serving_str"],
                'serving_qty':  s["serving_qty"],
                'serving_unit': s["serving_unit"],
                'calories':     s["scaled_cal"],
                'protein':      s["scaled_prot"],
                'carbs':        s["scaled_carb"],
                'fat':          s["scaled_fat"],
                'fiber':        s["scaled_fiber"],
                'swap_group':   target_family,
            })
        return results


_meal_engine = None

def get_meal_engine():
    global _meal_engine
    if _meal_engine is None:
        _meal_engine = MealEngine()
    return _meal_engine