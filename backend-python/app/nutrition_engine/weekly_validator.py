import logging
from app.nutrition_engine.config import NUTRITION_RULES
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

    def validate_serialized_plan(self, serialized_plan: Dict[str, Any], daily_targets: Dict[str, float]) -> Dict[str, Any]:
        report = {
            "is_valid": True,
            "critical_errors": [],
            "warnings": [],
            "stats": {}
        }
        
        base_tol = float(NUTRITION_RULES["validation_thresholds"].get("macro_tolerance_percent", 12.0))
        warn_cal = base_tol / 100.0
        crit_cal = (base_tol + 5.0) / 100.0
        warn_pro = base_tol / 100.0
        crit_pro = (base_tol + 5.0) / 100.0
        if not serialized_plan:
            report["is_valid"] = False
            report["critical_errors"].append("Weekly plan is empty.")
            return report

        for day, meals in serialized_plan.items():
            day_cal = 0.0
            day_pro = 0.0
            meal_identities = []
            
            for meal_name, items in meals.items():
                if not items:
                    report["is_valid"] = False
                    report["critical_errors"].append(f"Missing meal: {meal_name} on {day}")
                    continue

                foods_in_meal = []
                meal_cal = 0.0
                meal_pro = 0.0
                has_side_dish = False
                side_dish_cal = 0.0
                condiment_cal = 0.0

                for item in items:
                    fname = item.get('food_name', '').lower().strip()
                    unit = item.get('serving_unit', '').lower().strip()
                    qty = item.get('serving_qty', 0)
                    
                    foods_in_meal.append(fname)
                    
                    # Nutrition
                    nut = item.get('nutrition', {})
                    c = nut.get('calories', 0)
                    p = nut.get('protein', 0)
                    meal_cal += c
                    meal_pro += p
                    
                    # Unit sanity
                    if 'rice' in fname and unit in ['tsp', 'tbsp']:
                        report["is_valid"] = False
                        report["critical_errors"].append(f"Impossible unit for {fname}: {unit} on {day} {meal_name}")
                        
                    if 'chutney' in fname or 'pickle' in fname:
                        condiment_cal += c
                        if qty > float(NUTRITION_RULES["portions"]["chutney_pickle_max_tbsp"]):
                            report["is_valid"] = False
                            report["critical_errors"].append(f"Portion exceeded for {fname}: {qty} {unit} on {day} {meal_name}")

                    if 'salad' in fname or 'raita' in fname:
                        side_dish_cal += c
                        if unit in ['bowl', 'plate'] and qty > float(NUTRITION_RULES["portions"]["salad_raita_max_bowl"]):
                            report["is_valid"] = False
                            report["critical_errors"].append(f"Portion exceeded for {fname}: {qty} {unit} on {day} {meal_name}")

                if len(set(foods_in_meal)) != len(foods_in_meal):
                    report["is_valid"] = False
                    report["critical_errors"].append(f"Duplicate food in same meal: {foods_in_meal} on {day} {meal_name}")

                if meal_cal == 0:
                    report["is_valid"] = False
                    report["critical_errors"].append(f"Zero calories for meal {meal_name} on {day}")

                if meal_cal > 0:
                    if (condiment_cal / meal_cal) * 100 > float(NUTRITION_RULES["portions"]["condiment_max_calories_percent"]):
                        report["warnings"].append(f"Condiments exceed % cal limit on {day} {meal_name}")
                    if (side_dish_cal / meal_cal) * 100 > float(NUTRITION_RULES["portions"]["side_dish_max_calories_percent"]):
                        report["warnings"].append(f"Side dishes exceed % cal limit on {day} {meal_name}")

                day_cal += meal_cal
                day_pro += meal_pro

            target_cal = daily_targets.get(day, daily_targets).get('calories', 0)
            target_pro = daily_targets.get(day, daily_targets).get('protein', 0)

            if target_cal > 0:
                cal_diff = abs(day_cal - target_cal) / target_cal
                if cal_diff > crit_cal:
                    report["is_valid"] = False
                    report["critical_errors"].append(f"Day {day} calories ({day_cal}) deviate critically from target ({target_cal})")
                elif cal_diff > warn_cal:
                    report["warnings"].append(f"Day {day} calories ({day_cal}) deviate from target ({target_cal})")

            if target_pro > 0:
                pro_diff = abs(day_pro - target_pro) / target_pro
                if pro_diff > crit_pro:
                    report["is_valid"] = False
                    report["critical_errors"].append(f"Day {day} protein ({day_pro}) deviates critically from target ({target_pro})")
                elif pro_diff > warn_pro:
                    report["warnings"].append(f"Day {day} protein ({day_pro}) deviates from target ({target_pro})")

        return report
