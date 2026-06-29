"""
MealEngine — Legacy wrapper kept for backward compatibility only.
Now powered by NutritionEngineV6 under the hood.
"""

import os
import logging
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

logger = logging.getLogger(__name__)

class MealEngine:
    """
    Thin wrapper kept for backward-compatibility only.
    All heavy lifting is done by NutritionEngineV6.
    """

    def __init__(self):
        logger.info("Initializing Nutrition Engine V6...")
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
        logger.info("V6 Engine Ready")

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
        
        # serving string scaling
        if 'serving_qty' in scaled:
            scaled['serving_qty'] = float(scaled['serving_qty']) * factor
            from app.nutrition_engine.portion_optimizer import _format_serving
            scaled['serving'] = _format_serving(
                scaled['serving_qty'],
                scaled.get('serving_unit', 'g'),
                name=food_name,
                cal=scaled['calories']
            )
        elif 'serving' not in scaled and 'serving_qty' in scaled:
            qty = scaled['serving_qty']
            if isinstance(qty, float) and qty.is_integer():
                qty = int(qty)
            scaled['serving'] = f"{qty} {scaled.get('serving_unit', '')}"
            
        return scaled

    def _apply_intensity_adjustments(self, weekly_plan: Dict, intensity_by_day: Dict[str, str], profile: Dict = None) -> Dict:
        """Apply day-level intensity targets to a generated weekly meal plan without redundant scaling."""
        adjusted_weekly = {}
        adjusted_targets_by_day = {}

        # V6 now keys weekly_plan by day name (Monday..Sunday) directly.
        # Keep a fallback mapping for any legacy Day_N keys that may exist in the cache.
        _DAY_NAMES = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
        _legacy_to_name = {f"Day_{i+1}": name for i, name in enumerate(_DAY_NAMES)}
        # Reverse: day_name -> Day_N key used in plan_week() daily_targets
        _name_to_legacy = {name: f"Day_{i+1}" for i, name in enumerate(_DAY_NAMES)}

        raw_plan = weekly_plan.get('weekly_plan')
        # daily_targets is still keyed as Day_1..Day_7 from WeeklyMacroPlanner.plan_week()
        daily_targets = weekly_plan.get('daily_targets', {})

        day_keys = {'Day_1', 'Day_2', 'Day_3', 'Day_4', 'Day_5', 'Day_6', 'Day_7',
                    'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'}

        if raw_plan is None:
            if any(k in weekly_plan for k in day_keys):
                raw_plan = {k: v for k, v in weekly_plan.items() if k in day_keys}
            else:
                weekly_plan['weekly_plan'] = None
                weekly_plan['daily_targets_by_day'] = {}
                weekly_plan['intensity_by_day'] = intensity_by_day
                return weekly_plan

        if not daily_targets and profile:
            try:
                from app.nutrition_engine.nutrition_calculator import WeeklyMacroPlanner
                daily_targets = WeeklyMacroPlanner().plan_week(profile)
            except Exception as e:
                logger.warning(f"Failed to generate daily targets for cached plan: {e}")


        for v6_day, meals in raw_plan.items():
            # Resolve to a human-readable day name
            day_name = _legacy_to_name.get(v6_day, v6_day)  # already a name if V6 new-style
            day_intensity = self._normalize_intensity(intensity_by_day.get(day_name, 'moderate'))
            factor = self.intensity_multipliers.get(day_intensity, 1.0)

            adjusted_weekly[day_name] = {}
            for meal_type, items in (meals or {}).items():
                adjusted_weekly[day_name][meal_type] = []
                for item in (items or []):
                    # V6 WeeklyOptimizer already optimises portions for each day's
                    # intensity-adjusted calorie target — do NOT scale again here.
                    # Scaling would cause protein to swing ±15% across days even
                    # though the weekly plan intentionally keeps protein constant.
                    import copy
                    adjusted_weekly[day_name][meal_type].append(copy.deepcopy(item))

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
        logger.info(f"Generating meals for {user_profile.get('goal', 'Maintenance')} — intensity: {workout_intensity}")

        weekly_workout_plan = user_profile.get('weekly_workout_plan')
        weekly = self.generate_meal_plan(user_profile, weekly_workout_plan)

        adjusted_weekly_plan = weekly.get('weekly_plan') or {}
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

        logger.info(f"Generated {len(flat_meals)} meal items for {today_key}")
        
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
    #  slice_today_from_cached — re-slice a stored weekly plan for "today"
    # ─────────────────────────────────────────────

    def slice_today_from_cached(self, cached_result: Dict) -> Dict:
        """
        Re-slice an already-generated weekly meal plan for the current IST weekday.

        Pure transform over data produced by `suggest_daily_meals` — performs NO
        regeneration. Used when serving a cached plan so that `date`, `meals`
        (today's flat list), `daily_target` and `workout_intensity` stay correct
        on day 2–7 of the same week, while leaving the stored weekly view intact.

        Falls back to returning the cached dict unchanged if it is malformed.
        """
        if not isinstance(cached_result, dict):
            return cached_result

        adjusted_weekly_plan = cached_result.get('weekly_plan') or {}
        adjusted_targets_by_day = cached_result.get('daily_targets_by_day', {})
        intensity_by_day = cached_result.get('intensity_by_day', {})

        # Without a weekly plan there is nothing to re-slice; return as-is.
        if not adjusted_weekly_plan:
            return cached_result

        today_key = datetime.now(_IST).strftime('%A')
        if today_key not in adjusted_weekly_plan:
            today_key = list(adjusted_weekly_plan.keys())[0] if adjusted_weekly_plan else 'Monday'

        today_meals = adjusted_weekly_plan.get(today_key, {})
        today_target = adjusted_targets_by_day.get(today_key, {})
        today_intensity = intensity_by_day.get(today_key, cached_result.get('workout_intensity', 'moderate'))

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

        # Copy so we never mutate the cached payload that may be reused.
        result_dict = dict(cached_result)
        result_dict['date'] = datetime.now(_IST).strftime('%Y-%m-%d')
        result_dict['daily_target'] = today_target
        result_dict['meals'] = flat_meals
        result_dict['workout_intensity'] = today_intensity
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

        user_id = profile.get('user_id') or profile.get('_id')
        if user_id:
            user_id = str(user_id)
        else:
            user_id = 'mock_user'

        # Dynamically calculate Monday week_start in IST (Asia/Kolkata)
        from datetime import datetime, timedelta, timezone
        try:
            from zoneinfo import ZoneInfo
            now = datetime.now(ZoneInfo('Asia/Kolkata'))
        except Exception:
            # Fallback if zoneinfo is not installed or has issues
            try:
                now = datetime.now(timezone(timedelta(hours=5, minutes=30)))
            except Exception:
                now = datetime.now(timezone.utc)

        monday = now - timedelta(days=now.weekday())
        week_start = monday.date().isoformat()

        # Call V6 Engine
        weekly_plan = self.engine.generate_plan(enhanced_profile, user_id=user_id, week_start=week_start)
        
        # Apply intensity adjustments on top of the V6 plan
        intensity_by_day = self._build_intensity_by_day(enhanced_profile, 'moderate')
        weekly_plan = self._apply_intensity_adjustments(weekly_plan, intensity_by_day, enhanced_profile)
        
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
        Swaps are not limited to the same dish family, but prioritize:
        1) Same role (exact match), 2) Preferred regional cuisine match,
        3) Macro/nutrition profile similarity.
        Portions are scaled and snapped to realistic serving sizes.
        """
        from app.nutrition_engine.food_utils import get_food_family, get_meal_suitability
        from app.nutrition_engine.config import NUTRITION_RULES
        import re
        
        nodes = self.engine.food_graph.get_all_nodes()
        
        # 1. Find the target node
        target_node = None
        food_name_lower = food_name.lower().strip()
        
        # Step 1a: exact match
        for fid, node in nodes.items():
            node_name = node.get("food_name", "").lower().strip()
            if node_name == food_name_lower or node.get("name", "").lower().strip() == food_name_lower:
                target_node = node
                break
        
        # Step 1b: substring match fallback
        if not target_node:
            for fid, node in nodes.items():
                node_name = node.get("food_name", "").lower().strip()
                if food_name_lower in node_name or node_name in food_name_lower:
                    target_node = node
                    break

        def get_node_role(node: Dict) -> str:
            sem = node.get("semantics", {})
            role = sem.get("meal_role", "")
            if role:
                return role
            # Fallback mapping using keywords or category
            fname = node.get("food_name", "").lower().strip()
            dish_family = (sem.get("dish_family") or "").lower().strip()
            category = (sem.get("category") or "").lower().strip()
            fg = (sem.get("food_group") or category).lower().strip()
            
            if any(w in fname for w in ("raita", "pachadi")) or dish_family == "raita":
                return "raita"
            if any(w in fname for w in ("salad", "kachumber", "kosambari")) or dish_family == "salad":
                return "salad"
            if any(w in fname for w in ("chutney", "pickle", "achar")) or dish_family == "chutney":
                return "chutney"
            if any(w in fname for w in ("soup", "shorba")) or dish_family == "soup":
                return "soup"
            if "fruit" in fname or category in ("fruits", "fruit"):
                return "fruit"
            
            _PROTEIN_GROUPS = {"dal & pulses", "chicken/meat", "paneer", "eggs", "fish/seafood", "meat & chicken", "paneer & tofu", "seafood", "soya & tofu", "protein", "protein_main"}
            if fg in _PROTEIN_GROUPS or dish_family in ("curry", "korma", "dal", "sambar", "egg_dish", "omelette"):
                return "protein_main"
                
            _CARB_GROUPS = {"rice", "whole grains", "millets & whole grains", "breads & roti", "oats & cereals", "carb", "carb_base"}
            if fg in _CARB_GROUPS or dish_family in ("rice", "plain_rice", "fried_rice", "pulao", "biryani", "roti", "paratha", "bread", "naan", "dosa", "idli", "uttapam", "poha", "upma"):
                return "carb_base"
                
            return "veg_side"

        if target_node:
            target_role = get_node_role(target_node)
            target_family = target_node.get("semantics", {}).get("dish_family") or target_node.get("semantics", {}).get("family") or "Other"
        else:
            target_role = get_node_role({"food_name": food_name})
            target_family = "Other"

        is_breakfast_main = False
        if meal_type.lower() == "breakfast" and target_role in ("carb_base", "protein_main", "combo_meal"):
            is_breakfast_main = True

        # Determine target calories and macros
        orig_nutrition = target_node.get("nutrition", {}) if target_node else {}
        orig_serving_g = orig_nutrition.get("serving_size_g", 100.0) or 100.0
        orig_cal_per_100g = orig_nutrition.get("calories", 0)
        
        if target_calories and target_calories > 0:
            cal_target = target_calories
        elif orig_cal_per_100g > 0:
            cal_target = (orig_cal_per_100g / 100.0) * orig_serving_g
        else:
            default_cal_by_meal = {'breakfast': 200, 'lunch': 250, 'dinner': 250, 'snack': 150}
            cal_target = default_cal_by_meal.get(meal_type.lower(), 200)
            
        if target_protein and target_protein > 0:
            prot_target = target_protein
        elif orig_nutrition.get("protein", 0) > 0:
            prot_target = (orig_nutrition.get("protein", 0) / 100.0) * orig_serving_g
        else:
            prot_target = cal_target * 0.15 / 4.0
            
        if orig_nutrition.get("carbs", 0) > 0:
            carb_target = (orig_nutrition.get("carbs", 0) / 100.0) * orig_serving_g
        else:
            carb_target = (cal_target * 0.5) / 4.0
            
        if orig_nutrition.get("fat", 0) > 0:
            fat_target = (orig_nutrition.get("fat", 0) / 100.0) * orig_serving_g
        else:
            fat_target = (cal_target * 0.3) / 9.0

        # Extract User Diet (case-insensitive sub-string match)
        raw_diet = str(profile.get("diet_type") or profile.get("dietary_preference") or "NonVeg").strip().lower()
        if 'vegan' in raw_diet:
            user_diet = 'Vegan'
        elif 'non' in raw_diet:
            user_diet = 'NonVeg'
        elif 'veg' in raw_diet:
            user_diet = 'Vegetarian'
        else:
            user_diet = 'NonVeg'
            
        def _is_diet_compatible(meal_diet: str, user_diet: str) -> bool:
            if user_diet == "Vegan":
                return meal_diet == "Vegan"
            elif user_diet == "Vegetarian":
                return meal_diet in ("Vegan", "Vegetarian")
            return True

        # Extract Allergies and Exclusions
        allergies = profile.get('allergies') or []
        allergy_pattern = None
        if allergies:
            expanded = []
            for a in allergies:
                al = str(a).strip().lower()
                if al in ('lactose', 'dairy'):
                    expanded.extend(['milk', 'dairy', 'lactose', 'cheese',
                                     'paneer', 'butter', 'ghee', 'cream', 'yogurt', 'curd'])
                elif al == 'gluten':
                    expanded.extend(['wheat', 'roti', 'chapati', 'gluten', 'barley', 'rye',
                                     'maida', 'suji', 'semolina', 'atta', 'bread', 'toast'])
                elif al == 'nuts':
                    expanded.extend(['nuts', 'almond', 'cashew', 'walnut',
                                     'peanut', 'pistachio'])
                else:
                    expanded.append(al)
            allergy_str = '|'.join(r'\b' + re.escape(x) + r'\b' for x in expanded if x)
            if allergy_str:
                allergy_pattern = re.compile(allergy_str)
                
        never_recommend = profile.get('never_recommend') or []
        never_pattern = None
        if never_recommend:
            never_str = '|'.join(re.escape(str(t).lower().strip()) for t in never_recommend if t)
            if never_str:
                never_pattern = re.compile(never_str)

        # Collect suitable options from FoodGraph
        options = []
        for fid, node in nodes.items():
            if target_node and node == target_node:
                continue
            if node.get("food_name", "").lower().strip() == food_name_lower:
                continue
                
            # Must be nutrition-valid
            if not node.get("runtime_flags", {}).get("nutrition_valid", True):
                continue
                
            # Exclude zero nutrition
            n = node.get("nutrition", {})
            if (n.get("calories", 0) <= 0 and n.get("protein", 0) <= 0 and
                n.get("carbs", 0) <= 0 and n.get("fat", 0) <= 0):
                continue
                
            # Diet compatibility
            is_vegan = node.get("identity", {}).get("is_vegan", False)
            is_veg = node.get("identity", {}).get("is_vegetarian", False)
            node_diet = 'Vegan' if is_vegan else ('Vegetarian' if is_veg else 'NonVeg')
            
            if not _is_diet_compatible(node_diet, user_diet):
                continue
                
            # Suitability check
            fn = node.get("food_name", "")
            if get_meal_suitability(fn, meal_type) < 60:
                continue
                
            # Allergy Check
            name_lower = fn.lower()
            allergens_lower = str(node.get("allergens", "")).lower()
            if allergy_pattern:
                if allergy_pattern.search(name_lower) or allergy_pattern.search(allergens_lower):
                    continue
            if never_pattern and never_pattern.search(name_lower):
                continue
                
            if is_breakfast_main:
                opt_role = get_node_role(node)
                if opt_role not in ("carb_base", "protein_main", "combo_meal"):
                    continue
                if any(x in name_lower for x in ["dal", "curry", "sabzi", "gravy"]):
                    continue

            options.append(node)

        role_compatibility = {
            "carb_base": ["carb_base"],
            "protein_main": ["protein_main"],
            "veg_side": ["veg_side", "protein_main"],
            "dairy_side": ["dairy_side", "raita"],
            "raita": ["raita", "dairy_side"],
            "salad": ["salad"],
            "soup": ["soup"],
            "chutney": ["chutney"],
            "fruit": ["fruit"],
            "beverage": ["beverage", "dairy_side"]
        }

        # Regional Preference priorities
        reg_cfg = NUTRITION_RULES.get("regional_preferences", {})
        pref_reg = (profile.get("preferred_region") or reg_cfg.get("default_region", "Maharashtra") or "Maharashtra").lower().strip()
        priority_list = [c.lower().strip() for c in reg_cfg.get("cuisine_priority", [])]
        
        target_rc = target_node.get("semantics", {}).get("regional_cuisine", "Pan Indian") if target_node else "Pan Indian"
        target_region = (str(target_rc.get("primary", "Pan Indian")) if isinstance(target_rc, dict) else str(target_rc)).lower().strip()
        if target_region in ("pan indian", "pan_indian", "all india", "all_india"):
            target_region = "pan indian"

        def snap_portion(grams, node):
            n = node.get("nutrition", {})
            default_unit = node.get("servings", {}).get("default_unit", "g")
            serving_size_g = n.get("serving_size_g", 100.0) or 100.0
            
            if default_unit in ("g", "ml"):
                qty = float(round(grams / 5.0) * 5.0)
                qty = max(5.0, qty)
                actual_grams = qty
                serving_str = f"{int(qty)} {default_unit}"
                serving_qty = qty
                serving_unit = default_unit
            else:
                units_needed = grams / serving_size_g
                if default_unit in ("piece", "unit", "slice", "sandwich", "medium fruit"):
                    qty = float(round(units_needed))
                    qty = max(1.0, qty)
                else:
                    qty = float(round(units_needed * 2.0) / 2.0)
                    qty = max(0.5, qty)
                    
                actual_grams = qty * serving_size_g
                serving_qty = qty
                serving_unit = default_unit
                if qty.is_integer():
                    serving_str = f"{int(qty)} {default_unit}"
                else:
                    serving_str = f"{qty} {default_unit}"
            return actual_grams, serving_qty, serving_unit, serving_str

        def _scale_and_score(node):
            n = node.get("nutrition", {})
            cal_per_100g = n.get("calories", 0)
            if cal_per_100g <= 0:
                return None
                
            # Grams needed to hit calorie target
            grams_needed = (cal_target / cal_per_100g) * 100.0
            grams_needed = max(10.0, min(grams_needed, 600.0))
            
            # Snap portion
            actual_grams, serving_qty, serving_unit, serving_str = snap_portion(grams_needed, node)
            
            scale_factor = actual_grams / 100.0
            scaled_cal = round(cal_per_100g * scale_factor, 1)
            scaled_prot = round(n.get("protein", 0) * scale_factor, 1)
            scaled_carb = round(n.get("carbs", 0) * scale_factor, 1)
            scaled_fat = round(n.get("fat", 0) * scale_factor, 1)
            scaled_fiber = round(n.get("fiber", 0) * scale_factor, 1)
            
            # Compute macro score
            cal_diff = abs(scaled_cal - cal_target)
            prot_diff = abs(scaled_prot - prot_target)
            carb_diff = abs(scaled_carb - carb_target)
            fat_diff = abs(scaled_fat - fat_target)
            macro_score = (prot_diff * 4.0) + (cal_diff * 0.1) + (carb_diff * 0.5) + (fat_diff * 0.5)
            
            # Role compatibility score
            opt_role = get_node_role(node)
            if is_breakfast_main:
                if opt_role in ("carb_base", "protein_main", "combo_meal"):
                    role_score = 0
                else:
                    role_score = 2
            else:
                if opt_role == target_role:
                    role_score = 0
                elif opt_role in role_compatibility.get(target_role, []):
                    role_score = 1
                else:
                    role_score = 2

            # Family penalty (Phase 7: Prevent same-family swaps)
            opt_family = node.get("semantics", {}).get("dish_family") or node.get("semantics", {}).get("family") or "Other"
            family_penalty = 1 if opt_family == target_family else 0
                
            # Cuisine preference score
            rc = node.get("semantics", {}).get("regional_cuisine", "Pan Indian")
            opt_region = (str(rc.get("primary", "Pan Indian")) if isinstance(rc, dict) else str(rc)).lower().strip()
            if opt_region in ("pan indian", "pan_indian", "all india", "all_india"):
                opt_region = "pan indian"
                
            if opt_region == target_region:
                cuisine_score = 0
            elif opt_region == pref_reg:
                cuisine_score = 1
            elif opt_region in priority_list:
                cuisine_score = 2 + priority_list.index(opt_region)
            elif opt_region == "pan indian":
                cuisine_score = len(priority_list) + 2
            else:
                cuisine_score = len(priority_list) + 3
                
            # Sorting key: 1) Same role, 2) Family penalty, 3) Same cuisine preference, 4) Similar macros
            sort_key = (role_score, family_penalty, cuisine_score, macro_score)
            
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
                "explore_other_regions": (cuisine_score > 1),
                "swap_group": node.get("semantics", {}).get("dish_family") or node.get("semantics", {}).get("family") or "Other",
                "sort_key": sort_key,
            }

        scored = []
        for opt in options:
            result = _scale_and_score(opt)
            if result:
                scored.append(result)
                
        # Sort based on multi-criteria key
        scored.sort(key=lambda x: x["sort_key"])
        
        # Format results
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
                'explore_other_regions': s["explore_other_regions"],
                'swap_group':   s["swap_group"],
            })
        return results


_meal_engine = None

def get_meal_engine():
    global _meal_engine
    if _meal_engine is None:
        _meal_engine = MealEngine()
    return _meal_engine