import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)

class WeeklyValidator:
    """
    Phase 4.8: Weekly Validator
    Checks the holistic outputs of the weekly meal plan to ensure it meets dietary goals.
    """
    def __init__(self):
        pass
        
    def validate_plan(self, weekly_plan: Dict[str, Any], user_profile: Dict[str, Any], daily_targets: Dict[str, float]) -> Dict[str, Any]:
        """
        Validates the weekly plan. Returns a report containing metrics and validation status.
        """
        report = {
            "is_valid": True,
            "warnings": [],
            "metrics": {
                "avg_daily_calories": 0,
                "avg_daily_protein": 0,
                "avg_daily_carbs": 0,
                "avg_daily_fat": 0
            }
        }
        
        total_calories = 0
        total_protein = 0
        total_carbs = 0
        total_fat = 0
        days_counted = len(weekly_plan)
        
        if days_counted == 0:
            report["is_valid"] = False
            report["warnings"].append("Weekly plan is empty.")
            return report
            
        for day, meals in weekly_plan.items():
            for meal_name, items in meals.items():
                for item in items:
                    nut = item.get('nutrition', {})
                    total_calories += nut.get('calories', 0)
                    total_protein += nut.get('protein', 0)
                    total_carbs += nut.get('carbs', 0)
                    total_fat += nut.get('fat', 0)
                    
        avg_cal = total_calories / days_counted
        avg_pro = total_protein / days_counted
        
        report["metrics"]["avg_daily_calories"] = round(avg_cal, 2)
        report["metrics"]["avg_daily_protein"] = round(avg_pro, 2)
        report["metrics"]["avg_daily_carbs"] = round(total_carbs / days_counted, 2)
        report["metrics"]["avg_daily_fat"] = round(total_fat / days_counted, 2)
        
        # Check holistic limits
        if daily_targets and any(k.startswith('Day_') for k in daily_targets):
            target_cal = sum(d.get('calories', 0) for d in daily_targets.values()) / len(daily_targets)
            target_pro = sum(d.get('protein', 0) for d in daily_targets.values()) / len(daily_targets)
        else:
            target_cal = daily_targets.get('calories', 0)
            target_pro = daily_targets.get('protein', 0)
        
        if target_cal > 0:
            cal_diff = abs(avg_cal - target_cal) / target_cal
            if cal_diff > 0.15:
                report["is_valid"] = False
                report["warnings"].append(f"Average calories ({avg_cal}) deviate more than 15% from target ({target_cal})")
                
        if target_pro > 0:
            pro_diff = abs(avg_pro - target_pro) / target_pro
            if pro_diff > 0.20:
                report["warnings"].append(f"Average protein ({avg_pro}) deviates significantly from target ({target_pro})")
                
        # Phase 5: The "Indian Family Test"
        self._indian_family_test(weekly_plan, report)
                
        return report

    def _indian_family_test(self, weekly_plan: Dict[str, Any], report: Dict[str, Any]):
        """
        Heuristic-based check to see if the plates actually look like Indian meals.
        """
        for day, meals in weekly_plan.items():
            for meal_name, items in meals.items():
                if meal_name.lower() == 'snack':
                    continue
                    
                food_names_lower = [str(item.get('food_name', '')).lower() for item in items]
                
                # Curry needs a carb
                has_curry = any('curry' in fn or 'dal' in fn or 'gravy' in fn for fn in food_names_lower)
                has_carb = any('rice' in fn or 'roti' in fn or 'chapati' in fn or 'paratha' in fn or 'bread' in fn or 'pulao' in fn or 'biryani' in fn for fn in food_names_lower)
                
                if has_curry and not has_carb:
                    # Could be eating just dal or just chicken curry
                    # Exempt if it's soup or stew
                    if not any('soup' in fn or 'shorba' in fn for fn in food_names_lower):
                        report["warnings"].append(f"Indian Family Test Failed on {day} {meal_name}: Curry served without roti or rice.")
                        
                # Excessive dryness
                has_dry = sum(1 for fn in food_names_lower if 'dry' in fn or 'tikka' in fn)
                has_wet = any('curry' in fn or 'dal' in fn or 'raita' in fn or 'chutney' in fn for fn in food_names_lower)
                if has_dry >= 2 and not has_wet:
                    report["warnings"].append(f"Indian Family Test Failed on {day} {meal_name}: Very dry meal (multiple dry dishes) without any dal, raita, or chutney.")
                    
                # Double heavy proteins
                has_heavy_pro = sum(1 for fn in food_names_lower if 'chicken' in fn or 'paneer' in fn or 'mutton' in fn or 'fish' in fn)
                if has_heavy_pro >= 2:
                    report["warnings"].append(f"Indian Family Test Failed on {day} {meal_name}: Multiple heavy protein sources (e.g. Chicken AND Paneer).")
