import os
import sys
import json

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.nutrition_engine.engine import NutritionEngineV6
from app.nutrition_engine.nutrition_calculator import WeeklyMacroPlanner

def test_profiles():
    engine = NutritionEngineV6(data_dir='data', config_dir='config')
    planner = WeeklyMacroPlanner()
    
    profiles = [
        {
            "name": "Profile 1 (Male, 60kg, Muscle Gain, Non-Veg)",
            "weight_kg": 60,
            "height_cm": 160,
            "age": 25,
            "gender": "male",
            "activity_level": "moderate",
            "goal": "muscle_gain",
            "diet_type": "NonVeg",
            "region": "pan_indian",
            "allergies": []
        },
        {
            "name": "Profile 2 (Female, 55kg, Weight Loss, Vegetarian)",
            "weight_kg": 55,
            "height_cm": 160,
            "age": 28,
            "gender": "female",
            "activity_level": "light",
            "goal": "weight_loss",
            "diet_type": "Vegetarian",
            "region": "pan_indian",
            "allergies": []
        },
        {
            "name": "Profile 3 (Male, 80kg, Maintenance, Non-Veg)",
            "weight_kg": 80,
            "height_cm": 175,
            "age": 30,
            "gender": "male",
            "activity_level": "moderate",
            "goal": "maintenance",
            "diet_type": "NonVeg",
            "region": "pan_indian",
            "allergies": []
        },
        {
            "name": "Profile 4 (Vegan, Muscle Gain, Nut Allergy)",
            "weight_kg": 70,
            "height_cm": 170,
            "age": 27,
            "gender": "male",
            "activity_level": "heavy",
            "goal": "muscle_gain",
            "diet_type": "Vegan",
            "region": "pan_indian",
            "allergies": ["nuts", "peanuts"]
        }
    ]

    report = "# Comprehensive V6 Engine Validation Report\n\n"

    for profile in profiles:
        report += f"## {profile['name']}\n\n"
        
        try:
            daily_targets = planner.plan_week(profile)
            result = engine.generate_plan(profile)
            weekly_plan = result.get('weekly_plan', {})
            stats = result.get('stats', {})
            
            if not weekly_plan:
                report += f"**Failed to generate plan.**\n\nStats: {json.dumps(stats, indent=2)}\n\n"
                continue
                
            report += "### Daily Breakdown\n"
            
            day_signatures = set()
            duplicate_days = 0
            
            for day_key in sorted(weekly_plan.keys()):
                target = daily_targets.get(day_key, {})
                target_p = target.get('protein', 0)
                target_c = target.get('calories', 0)
                
                day_plan = weekly_plan[day_key]
                day_p = 0
                day_c = 0
                
                day_str = ""
                daily_meal_ids = []
                
                for meal_type in ['breakfast', 'lunch', 'snack', 'dinner']:
                    plate = day_plan.get(meal_type, [])
                    if not plate:
                        day_str += f"- **{meal_type.capitalize()}**: *Empty/Failed*\n"
                        continue
                        
                    meal_p = sum(item['nutrition']['protein'] for item in plate)
                    meal_c = sum(item['nutrition']['calories'] for item in plate)
                    day_p += meal_p
                    day_c += meal_c
                    
                    items_str = ", ".join([f"{item.get('portion', 1):.1f}x {item['food_name']} ({item['nutrition']['protein']:.1f}g P)" for item in plate])
                    day_str += f"- **{meal_type.capitalize()}** ({meal_p:.1f}g P | {meal_c:.0f} kcal): {items_str}\n"
                    
                    # Track for duplicates
                    daily_meal_ids.extend([item['food_id'] for item in plate])
                    
                daily_meal_ids.sort()
                sig = str(daily_meal_ids)
                if sig in day_signatures:
                    duplicate_days += 1
                day_signatures.add(sig)
                
                p_err = abs(day_p - target_p) / max(target_p, 1) * 100
                c_err = abs(day_c - target_c) / max(target_c, 1) * 100
                
                report += f"#### {day_key.replace('_', ' ')} (Target: {target_p:.1f}g P, {target_c:.0f} kcal)\n"
                report += f"**Actual:** {day_p:.1f}g P (Err: {p_err:.1f}%), {day_c:.0f} kcal (Err: {c_err:.1f}%)\n"
                report += day_str + "\n"
                
            report += "### Week Summary\n"
            report += f"- **Duplicate Whole Days**: {duplicate_days} (Should be 0)\n"
            report += f"- **Total Meals Generated**: {sum(len(d) for d in weekly_plan.values())}/28\n"
            report += "---\n\n"
            
        except Exception as e:
            report += f"**Error generating plan:** {str(e)}\n\n"

    with open("comprehensive_validation.md", "w", encoding="utf-8") as f:
        f.write(report)
        
    print("Validation complete. Report written to comprehensive_validation.md")

if __name__ == "__main__":
    test_profiles()
