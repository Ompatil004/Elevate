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
        scaled = dict(item)
        for key in ('calories', 'protein', 'carbs', 'fat', 'fiber'):
            value = float(item.get('nutrition', {}).get(key, item.get(key, 0)) or 0)
            adjusted = value * factor
            scaled[key] = round(adjusted) if key == 'calories' else round(adjusted, 1)
        
        # Ensure both name and food_name are populated for compatibility
        food_name = scaled.get('food_name') or scaled.get('name', '')
        scaled['name'] = food_name
        scaled['food_name'] = food_name
        
        # Ensure serving is populated from serving_qty and serving_unit if missing
        if 'serving' not in scaled and 'serving_qty' in scaled and 'serving_unit' in scaled:
            qty = scaled['serving_qty']
            if isinstance(qty, float) and qty.is_integer():
                qty = int(qty)
            scaled['serving'] = f"{qty} {scaled['serving_unit']}"
            
        return scaled

    def _apply_intensity_adjustments(self, weekly_plan: Dict, intensity_by_day: Dict[str, str]) -> Dict:
        """Apply day-level intensity targets to a generated weekly meal plan without redundant scaling."""
        adjusted_weekly = {}
        adjusted_targets_by_day = {}

        # Map V6 "Day_1" to "Monday", etc.
        day_mapping = {
            "Day_1": "Monday",
            "Day_2": "Tuesday",
            "Day_3": "Wednesday",
            "Day_4": "Thursday",
            "Day_5": "Friday",
            "Day_6": "Saturday",
            "Day_7": "Sunday"
        }

        raw_plan = weekly_plan.get('weekly_plan', {})
        daily_targets = weekly_plan.get('daily_targets', {})

        for v6_day, meals in raw_plan.items():
            day_name = day_mapping.get(v6_day, v6_day)
            day_intensity = self._normalize_intensity(intensity_by_day.get(day_name, 'moderate'))
            factor = self.intensity_multipliers.get(day_intensity, 1.0)

            adjusted_weekly[day_name] = {}
            for meal_type, items in (meals or {}).items():
                adjusted_weekly[day_name][meal_type] = []
                for item in (items or []):
                    scaled_item = self._scale_meal_item(item, factor)
                    adjusted_weekly[day_name][meal_type].append(scaled_item)

            # Retrieve the planned target for this day from V6 daily_targets
            planned_target = daily_targets.get(v6_day, {})
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
                          profile: Dict, limit: int = 5) -> List[Dict]:
        """
        Fetch similar foods from the FoodGraph based on swap_group/family and diet restrictions.
        """
        nodes = self.engine.food_graph.get_all_nodes()
        
        # 1. Find the target node and its family
        target_node = None
        target_family = None
        for fid, node in nodes.items():
            node_name = node.get("food_name", "").lower().strip()
            if node_name == food_name.lower().strip() or node.get("name", "").lower().strip() == food_name.lower().strip():
                target_node = node
                target_family = node.get("semantics", {}).get("family")
                break
                
        if not target_node or not target_family:
            return []
            
        # 2. Extract User Diet
        user_diet = profile.get("diet_type") or profile.get("dietary_preference", "NonVeg")
        if user_diet in ('Veg', 'Vegetarian'):
            user_diet = 'Vegetarian'
        elif user_diet in ('Non-Veg', 'NonVeg'):
            user_diet = 'NonVeg'
            
        # 3. Find alternatives in same family and diet
        options = []
        for fid, node in nodes.items():
            if node == target_node:
                continue
            
            node_diet = node.get("identity", {}).get("diet", "NonVeg")
            if user_diet == "Vegan" and node_diet != "Vegan":
                continue
            if user_diet == "Vegetarian" and node_diet == "NonVeg":
                continue
                
            family = node.get("semantics", {}).get("family")
            if family == target_family:
                options.append(node)
                
        # 4. Format and select top alternatives
        import random
        random.shuffle(options)
        
        results = []
        for opt in options[:limit]:
            item = dict(opt)
            opt_name = item.get("food_name", "")
            
            qty = item.get("servings", {}).get("default_qty", 1)
            unit = item.get("servings", {}).get("default_unit", "g")
            if isinstance(qty, float) and qty.is_integer():
                qty = int(qty)
            
            results.append({
                'meal_type': meal_type,
                'name': opt_name,
                'food_name': opt_name,
                'serving': f"{qty} {unit}",
                'calories': item.get('nutrition', {}).get('calories', 0),
                'protein': item.get('nutrition', {}).get('protein', 0),
                'carbs': item.get('nutrition', {}).get('carbs', 0),
                'fat': item.get('nutrition', {}).get('fat', 0),
                'fiber': item.get('nutrition', {}).get('fiber', 0),
                'swap_group': target_family
            })
        return results

_meal_engine = None

def get_meal_engine():
    global _meal_engine
    if _meal_engine is None:
        _meal_engine = MealEngine()
    return _meal_engine