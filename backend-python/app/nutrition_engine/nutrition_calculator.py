import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)

def calculate_base_daily_targets(user_profile: Dict[str, Any]) -> Dict[str, float]:
    weight_kg = user_profile.get("weight_kg", 70)
    height_cm = user_profile.get("height_cm", 170)
    age_years = user_profile.get("age", 30)
    gender = user_profile.get("gender", "male")
    activity_level = user_profile.get("activity_level", "moderate")
    goal = user_profile.get("goal", "maintain")

    # Normalize goal
    goal_str = str(goal).strip().lower().replace(" ", "_")
    if 'fat' in goal_str or 'loss' in goal_str or 'weight' in goal_str:
        goal_norm = 'fat_loss'
    elif 'gain' in goal_str or 'muscle' in goal_str or 'hypertrophy' in goal_str:
        goal_norm = 'muscle_gain'
    else:
        goal_norm = 'maintain'
        
    # Normalize activity level
    act_str = str(activity_level).strip().lower().replace(" ", "_")
    if 'very' in act_str:
        act_norm = 'very_active'
    elif 'extra' in act_str:
        act_norm = 'extra_active'
    elif 'light' in act_str:
        act_norm = 'lightly_active'
    elif 'mod' in act_str:
        act_norm = 'moderate'
    elif 'active' in act_str:
        act_norm = 'moderate'
    else:
        act_norm = 'sedentary'

    # BMR
    if gender.lower() == 'male':
        bmr = (10 * weight_kg) + (6.25 * height_cm) - (5 * age_years) + 5
    else:
        bmr = (10 * weight_kg) + (6.25 * height_cm) - (5 * age_years) - 161
        
    # Activity multiplier
    activity_multipliers = {
        'sedentary': 1.2,
        'lightly_active': 1.375,
        'moderate': 1.55,
        'moderately_active': 1.55,
        'very_active': 1.725,
        'extra_active': 1.9
    }
    tdee = bmr * activity_multipliers.get(act_norm, 1.2)
    
    # Goal adjustments
    if goal_norm == "muscle_gain":
        target_cal = tdee + 300
        protein_g = weight_kg * 2.0
    elif goal_norm == "fat_loss":
        target_cal = tdee - 500
        protein_g = weight_kg * 1.8
    else:
        target_cal = tdee
        protein_g = weight_kg * 1.4
        
    fat_g = weight_kg * 0.8
    carbs_cals = target_cal - ((protein_g * 4) + (fat_g * 9))
    carbs_g = max(0, carbs_cals / 4)
    
    return {
        "calories": target_cal,
        "protein": protein_g,
        "fat": fat_g,
        "carbs": carbs_g
    }

class WeeklyMacroPlanner:
    """
    Plans 7 days of precise daily targets, keeping protein stable 
    but cycling calories/carbs based on the workout plan intensity.
    """
    
    INTENSITY_MODIFIERS = {
        'rest': -100,
        'light': -50,
        'moderate': 0,
        'hard': +100,
        'very_hard': +150
    }

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

    def plan_week(self, user_profile: Dict[str, Any]) -> Dict[str, Dict[str, float]]:
        base_targets = calculate_base_daily_targets(user_profile)
        workout_plan = user_profile.get('weekly_workout_plan', [])
        
        # Map day 1-7 to workout intensity
        day_intensities = {}
        day_mapping = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
        
        for idx, dname in enumerate(day_mapping):
            intensity = "moderate"
            for w in workout_plan:
                if w.get('day_name', '').split(' ')[0] == dname or w.get('day') == dname:
                    intensity_metrics = w.get('intensity_metrics')
                    intensity_cat = intensity_metrics.get('category') if isinstance(intensity_metrics, dict) else None
                    
                    if isinstance(intensity_cat, str):
                        intensity = intensity_cat.lower().replace(' ', '_')
                    elif 'intensity' in w:
                        val = w['intensity']
                        if isinstance(val, str):
                            intensity = val.lower().replace(' ', '_')
                        elif isinstance(val, (int, float)):
                            score = float(val)
                            if score <= 0.05:
                                intensity = 'rest'
                            elif score < 0.35:
                                intensity = 'light'
                            elif score < 0.65:
                                intensity = 'moderate'
                            elif score < 0.85:
                                intensity = 'hard'
                            else:
                                intensity = 'very_hard'
                        else:
                            intensity = self._infer_intensity_from_workout_day(w)
                    else:
                        intensity = self._infer_intensity_from_workout_day(w)
                    break
            day_intensities[f"Day_{idx+1}"] = intensity

        weekly_plan = {}
        for day_key, intensity in day_intensities.items():
            mod = self.INTENSITY_MODIFIERS.get(intensity, 0)
            
            day_cals = base_targets["calories"] + mod
            day_pro = base_targets["protein"] # Protein stays identical
            day_fat = base_targets["fat"]     # Fat stays identical
            
            # Carbs absorb the variance
            carbs_cals = day_cals - ((day_pro * 4) + (day_fat * 9))
            day_carbs = max(0, carbs_cals / 4)
            
            weekly_plan[day_key] = {
                "calories": day_cals,
                "protein": day_pro,
                "carbs": day_carbs,
                "fat": day_fat,
                "intensity": intensity
            }
            
        return weekly_plan

class MealMacroDistributor:
    """
    Distributes daily targets into specific meals dynamically based on workout intensity.
    """
    
    # Ratios: (Calories, Protein)
    RATIOS = {
        "rest": {
            "breakfast": (0.22, 0.22),
            "lunch": (0.35, 0.30),
            "snack": (0.13, 0.18),
            "dinner": (0.30, 0.30)
        },
        "light": {
            "breakfast": (0.22, 0.22),
            "lunch": (0.35, 0.30),
            "snack": (0.13, 0.18),
            "dinner": (0.30, 0.30)
        },
        "moderate": {
            "breakfast": (0.22, 0.22),
            "lunch": (0.35, 0.30),
            "snack": (0.13, 0.18),
            "dinner": (0.30, 0.30)
        },
        "hard": {
            "breakfast": (0.22, 0.22),
            "lunch": (0.35, 0.30),
            "snack": (0.13, 0.18),
            "dinner": (0.30, 0.30)
        },
        "very_hard": {
            "breakfast": (0.22, 0.22),
            "lunch": (0.35, 0.30),
            "snack": (0.13, 0.18),
            "dinner": (0.30, 0.30)
        }
    }

    def distribute(self, daily_target: Dict[str, Any]) -> Dict[str, Dict[str, float]]:
        intensity = daily_target.get("intensity", "moderate")
        ratios = self.RATIOS.get(intensity, self.RATIOS["moderate"])
        
        cal = daily_target["calories"]
        pro = daily_target["protein"]
        carbs = daily_target["carbs"]
        fat = daily_target["fat"]
        
        distributed = {}
        for meal, (cal_ratio, pro_ratio) in ratios.items():
            distributed[meal] = {
                "calories": cal * cal_ratio,
                "protein": pro * pro_ratio,
                "carbs": carbs * cal_ratio,  # Using cal ratio for carbs/fat as simple approximation
                "fat": fat * cal_ratio
            }
            
        return distributed
