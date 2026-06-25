import os
import sys
import random
import time
import json
from collections import defaultdict

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.nutrition_engine.engine import NutritionEngineV6

def generate_random_profile(i):
    diet_types = ['Standard', 'Vegetarian', 'Vegan', 'Keto', 'High Protein']
    allergies_pool = ['Dairy', 'Nuts', 'Gluten', 'Soy', 'Eggs', 'Seafood']
    
    diet = random.choice(diet_types)
    cal = random.randint(1500, 3200)
    
    if diet == 'High Protein':
        prot = random.randint(150, 220)
    elif diet == 'Vegan':
        prot = random.randint(80, 140)
    else:
        prot = random.randint(100, 180)
        
    num_allergies = random.choices([0, 1, 2], weights=[0.7, 0.2, 0.1])[0]
    allergies = random.sample(allergies_pool, num_allergies) if num_allergies > 0 else []
    
    return {
        "user_id": f"qa_user_{i}",
        "target_calories": cal,
        "target_protein": prot,
        "diet_type": diet,
        "allergies": allergies,
        "dislikes": []
    }

def run_qa():
    engine = NutritionEngineV6()
    num_profiles = 50
    flagged_plans = []
    
    print(f"Starting Automated QA on {num_profiles} Profiles...")
    print("-" * 50)
    
    for i in range(num_profiles):
        profile = generate_random_profile(i)
        try:
            result = engine.generate_plan(profile, user_id=profile["user_id"], week_start=f"qa_week_{i}")
            if result.get("status") in ["success", "warning"]:
                plan = result["weekly_plan"]
                targets = result["daily_targets"]
                
                flags = []
                
                # State tracking for variety
                food_counts = defaultdict(int)
                meal_id_counts = defaultdict(int)
                
                for day, day_plan in plan.items():
                    target_cal = targets[day]["calories"]
                    target_pro = targets[day]["protein"]
                    actual_cal = 0
                    actual_pro = 0
                    
                    for meal_type, plate in day_plan.items():
                        if not plate: continue
                        
                        if len(plate) > 0 and 'semantics' in plate[0]:
                            meal_id = plate[0]['semantics'].get('meal_id', 'unknown')
                            meal_id_counts[meal_id] += 1
                            if meal_id_counts[meal_id] > 3:
                                flags.append(f"Meal Identity '{meal_id}' repeated > 3 times.")
                                
                        for item in plate:
                            actual_cal += float(item['nutrition']['calories'])
                            actual_pro += float(item['nutrition']['protein'])
                            
                            food_name = item.get('food_name', '')
                            food_counts[food_name] += 1
                            
                            if food_counts[food_name] > 5:
                                flags.append(f"Food '{food_name}' repeated > 5 times.")
                                
                            unit = item.get('serving_unit', '')
                            qty = float(item.get('serving_qty', 1.0))
                            
                            if unit in ('slice', 'slices') and qty > 4:
                                flags.append(f"Portion issue: {qty} {unit} of {food_name}")
                            if unit in ('bowl', 'bowls') and qty > 3:
                                flags.append(f"Portion issue: {qty} {unit} of {food_name}")
                                
                    cal_err = abs(actual_cal - target_cal) / max(1, target_cal) * 100
                    if cal_err > 15:
                        flags.append(f"Day {day} Calorie Skew > 15% ({actual_cal} vs {target_cal})")
                        
                # Ensure we only keep unique flags
                flags = list(set(flags))
                
                if flags:
                    flagged_plans.append({
                        "profile": profile,
                        "flags": flags
                    })
                    print(f"[FLAGGED] Profile {i}: {len(flags)} issues found.")
                    for f in flags:
                        print(f"   -> {f}")
                        
        except Exception as e:
            print(f"Profile {i} generation failed: {e}")
            
    print("=" * 50)
    print(f"QA Completed. Flagged {len(flagged_plans)} / {num_profiles} plans.")
    
    if flagged_plans:
        os.makedirs("qa_reports", exist_ok=True)
        report_path = "qa_reports/flagged_plans.json"
        with open(report_path, "w", encoding='utf-8') as f:
            json.dump(flagged_plans, f, indent=2)
        print(f"Flag details saved to {report_path}")

if __name__ == "__main__":
    run_qa()
