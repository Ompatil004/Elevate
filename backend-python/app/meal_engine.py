"""
MealEngine — Legacy wrapper kept for backward compatibility only.

.. deprecated::
    BUG-P2: This module is **DEPRECATED**. Use ``DeterministicMealEngine``
    from ``app.deterministic_meal_engine`` directly for all new code.
    See ``docs/architecture.md`` for the migration plan.
    This class will be removed in the next major release.
"""

import os
from typing import Dict, List
from datetime import datetime, timezone
try:
    from zoneinfo import ZoneInfo  # Python 3.9+
except Exception:  # pragma: no cover - fallback for older runtimes
    ZoneInfo = None
from .deterministic_meal_engine import MealEngine as DatasetMealEngine

try:
    _IST = ZoneInfo('Asia/Kolkata') if ZoneInfo else timezone.utc
except Exception:
    _IST = timezone.utc


class MealEngine:
    """
    .. deprecated::
        Thin wrapper kept for backward-compatibility only.
        All heavy lifting is done by DatasetMealEngine (deterministic_meal_engine.py).
        Do NOT add new features here — use DatasetMealEngine directly.
    """

    def __init__(self):
        print("\n[MealEngine] Initializing...")
        self.engine = DatasetMealEngine()
        self.intensity_multipliers = {
            'rest': 0.90,
            'light': 0.95,
            'moderate': 1.00,
            'hard': 1.10,
            'very_hard': 1.18,
        }
        print("[MealEngine] Ready\n")

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

            explicit = day.get('intensity')
            if explicit:
                by_day[day_name] = self._normalize_intensity(explicit)
            else:
                by_day[day_name] = self._infer_intensity_from_workout_day(day)

        return by_day

    def _scale_meal_item(self, item: Dict, factor: float) -> Dict:
        scaled = dict(item)
        for key in ('calories', 'protein', 'carbs', 'fat'):
            value = float(item.get(key, 0) or 0)
            adjusted = value * factor
            scaled[key] = round(adjusted) if key == 'calories' else round(adjusted, 1)
        return scaled

    def _apply_intensity_adjustments(self, weekly_plan: Dict, intensity_by_day: Dict[str, str]) -> Dict:
        """Apply day-level intensity multipliers to a generated weekly meal plan."""
        adjusted_weekly = {}
        adjusted_targets_by_day = {}

        base_targets = weekly_plan.get('daily_targets', {})
        base_daily_cal = float(base_targets.get('daily_calories', 0) or 0)
        base_macros = base_targets.get('macro_targets_g', {})
        base_protein = float(base_macros.get('protein_g', 0) or 0)
        base_carbs = float(base_macros.get('carb_g', 0) or 0)
        base_fat = float(base_macros.get('fat_g', 0) or 0)

        # V2 engine returns plan under 'plan' key
        raw_plan = weekly_plan.get('plan') or weekly_plan.get('weekly_plan') or {}

        for day_name, meals in raw_plan.items():
            day_intensity = self._normalize_intensity(intensity_by_day.get(day_name, 'moderate'))
            factor = self.intensity_multipliers.get(day_intensity, 1.0)

            adjusted_weekly[day_name] = {}
            for meal_type, items in (meals or {}).items():
                adjusted_weekly[day_name][meal_type] = [
                    self._scale_meal_item(item, factor) for item in (items or [])
                ]

            adjusted_targets_by_day[day_name] = {
                'calories': round(base_daily_cal * factor),
                'protein': round(base_protein * factor, 1),
                'carbs': round(base_carbs * factor, 1),
                'fat': round(base_fat * factor, 1),
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
        print(f"[MealEngine] User profile: {user_profile}")

        # Use generate_meal_plan to ensure workout volume is properly integrated
        weekly_workout_plan = user_profile.get('weekly_workout_plan')
        weekly = self.generate_meal_plan(user_profile, weekly_workout_plan)

        adjusted_weekly_plan = weekly.get('weekly_plan', {})
        adjusted_targets_by_day = weekly.get('daily_targets_by_day', {})
        intensity_by_day = weekly.get('intensity_by_day', {})

        # Pick today's day (aligned to IST timezone like frontend)
        today_key = datetime.now(_IST).strftime('%A')
        if today_key not in adjusted_weekly_plan:
            today_key = list(adjusted_weekly_plan.keys())[0] if adjusted_weekly_plan else 'Monday'

        today_meals = adjusted_weekly_plan.get(today_key, {})
        today_target = adjusted_targets_by_day.get(today_key, {})

        normalized_intensity = self._normalize_intensity(workout_intensity)
        today_intensity = intensity_by_day.get(today_key, normalized_intensity)

        # Flatten into a single list of meals for the frontend
        flat_meals = []
        for meal_type, items in today_meals.items():
            for item in items:
                flat_meals.append({
                    'meal_type':    meal_type,
                    'name':         item.get('food_name', item.get('name', '')),
                    'food_name':    item.get('food_name', item.get('name', '')),
                    'serving':      item.get('serving', ''),
                    'calories':     item.get('calories', 0),
                    'protein':      item.get('protein', 0),
                    'carbs':        item.get('carbs', 0),
                    'fat':          item.get('fat', 0),
                    'fiber':        0,
                    'swap_group':   item.get('swap_group', ''),
                    'swap_options': item.get('swap_options', []),
                    'meal_role':    item.get('meal_role', ''),
                    'budget_level': item.get('budget_level', ''),
                    'availability': item.get('availability', ''),
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
            'consistency_score': weekly.get('weekly_summary', {}).get('consistency_score', 0),
            'shopping_list': weekly.get('weekly_summary', {}).get('shopping_list', {}),
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
        Generate weekly meal plan, adjusting activity level based on actual workout plan.
        """
        # BUG FIX: Derive activity level from workout plan if available
        enhanced_profile = {**profile}
        if weekly_workout_plan and isinstance(weekly_workout_plan, list):
            workout_days = sum(1 for d in weekly_workout_plan if d.get('type') == 'workout')
            total_exercises = sum(
                len(d.get('exercises', [])) for d in weekly_workout_plan if d.get('type') == 'workout'
            )
            avg_exercises = total_exercises / max(workout_days, 1)

            # Map exercise volume to activity level for TDEE calculation
            if avg_exercises >= 8 or workout_days >= 6:
                enhanced_profile['activity_level'] = 'Very Active'
            elif avg_exercises >= 6 or workout_days >= 5:
                enhanced_profile['activity_level'] = 'Active'
            elif avg_exercises >= 3 or workout_days >= 3:
                enhanced_profile['activity_level'] = 'Moderate'
            else:
                enhanced_profile['activity_level'] = 'Light'

            print(f"  [MealEngine] Workout-adjusted activity: {enhanced_profile['activity_level']} "
                  f"({workout_days} days, avg {avg_exercises:.0f} exercises/day)")
        enhanced_profile['weekly_workout_plan'] = weekly_workout_plan or []

        weekly_plan = self.engine.generate_weekly_plan(enhanced_profile)
        intensity_by_day = self._build_intensity_by_day(enhanced_profile, 'moderate')
        weekly_plan = self._apply_intensity_adjustments(weekly_plan, intensity_by_day)
        weekly_plan['workout_correlation'] = {
            'intensity_by_day': intensity_by_day,
            'correlation_version': '1.1',
        }
        return weekly_plan

    # ─────────────────────────────────────────────
    #  get_swap_options — used by /nutrition/swap
    # ─────────────────────────────────────────────

    def get_swap_options(self, food_name: str, meal_type: str,
                          profile: Dict, limit: int = 5) -> List[Dict]:
        return self.engine.get_swap_options(food_name, meal_type, profile, limit)


# ─── Singleton accessor ───

_meal_engine = None

def get_meal_engine():
    global _meal_engine
    if _meal_engine is None:
        _meal_engine = MealEngine()
    return _meal_engine