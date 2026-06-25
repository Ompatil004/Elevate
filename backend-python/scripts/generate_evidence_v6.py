import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.nutrition_engine.engine import NutritionEngineV6

def format_plate(meal_name, plate, target_macros):
    lines = []
    lines.append(f"#### {meal_name.capitalize()}")
    lines.append(f"Target: {target_macros['protein']:.1f}g P | {target_macros['calories']:.1f} kcal")
    
    if not plate:
        lines.append("*FAILED TO GENERATE PLATE*")
        return "\n".join(lines)
        
    plate_p = 0
    plate_c = 0
    
    for item in plate:
        food_name = item['food_name']
        serving = item['serving']
        p = item['nutrition']['protein']
        c = item['nutrition']['calories']
        plate_p += p
        plate_c += c
        lines.append(f"- {serving} **{food_name}** ({p:.1f}g P, {c:.1f} kcal)")
        
    lines.append(f"**Total:** {plate_p:.1f}g P | {plate_c:.1f} kcal")
    lines.append("")
    return "\n".join(lines)

def main():
    engine = NutritionEngineV6(data_dir='data', config_dir='config')
    
    profiles = [
        {
            "name": "Profile 1: Male, 60kg, Muscle Gain, Non-Veg",
            "weight_kg": 60,
            "height_cm": 160,
            "age": 25,
            "gender": "male",
            "activity_level": "moderate",
            "goal": "muscle_gain",
            "diet_type": "NonVeg",
            "region": "pan_indian"
        },
        {
            "name": "Profile 2: Female, 55kg, Weight Loss, Vegetarian",
            "weight_kg": 55,
            "height_cm": 160,
            "age": 30,
            "gender": "female",
            "activity_level": "sedentary",
            "goal": "weight_loss",
            "diet_type": "Vegetarian",
            "region": "pan_indian"
        },
        {
            "name": "Profile 3: Male, 80kg, Maintenance, Non-Veg",
            "weight_kg": 80,
            "height_cm": 175,
            "age": 35,
            "gender": "male",
            "activity_level": "light",
            "goal": "maintenance",
            "diet_type": "NonVeg",
            "region": "pan_indian"
        },
        {
            "name": "Profile 4: Vegetarian, Muscle Gain, Nut Allergy",
            "weight_kg": 70,
            "height_cm": 170,
            "age": 28,
            "gender": "male",
            "activity_level": "heavy",
            "goal": "muscle_gain",
            "diet_type": "Vegetarian",
            "region": "pan_indian",
            "allergies": ["nuts", "peanuts"]
        }
    ]
    
    markdown_output = "# V6 Engine Output Evidence\n\n"
    
    for idx, profile in enumerate(profiles):
        markdown_output += f"## {profile['name']}\n\n"
        
        result = engine.generate_plan(profile)
        weekly_plan = result.get('weekly_plan', {})
        report = result.get('validation_report', {})
        
        # Display the targets from the engine's internal planner
        from app.nutrition_engine.nutrition_calculator import WeeklyMacroPlanner, MealMacroDistributor
        planner = WeeklyMacroPlanner()
        daily_targets = planner.plan_week(profile)
        distributor = MealMacroDistributor()
        
        markdown_output += f"### Validation Report\n```json\n{report}\n```\n\n"
        
        for day in range(1, 8):
            day_key = f"Day_{day}"
            day_plan = weekly_plan.get(day_key, {})
            target = daily_targets.get(day_key, {})
            
            markdown_output += f"### {day_key}\n"
            markdown_output += f"**Daily Target:** {target['protein']:.1f}g P | {target['calories']:.1f} kcal\n\n"
            
            meal_targets = distributor.distribute(target)
            
            day_p = 0
            day_c = 0
            
            for meal_type in ['breakfast', 'lunch', 'snack', 'dinner']:
                plate = day_plan.get(meal_type, [])
                mtarget = meal_targets[meal_type]
                
                markdown_output += format_plate(meal_type, plate, mtarget) + "\n"
                
                for item in plate:
                    day_p += item['nutrition']['protein']
                    day_c += item['nutrition']['calories']
                    
            markdown_output += f"**Day Total:** {day_p:.1f}g P | {day_c:.1f} kcal\n"
            markdown_output += "---\n\n"
            
    with open("evidence.md", "w", encoding="utf-8") as f:
        f.write(markdown_output)
        
    print("Evidence written to evidence.md")

if __name__ == "__main__":
    main()
