import os
import sys
import random
import time
import logging
import json
from collections import defaultdict
from typing import Dict, Any

# Ensure project root is in PYTHONPATH
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.nutrition_engine.engine import NutritionEngineV6

# Setup basic logging
logging.basicConfig(level=logging.WARNING, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

def generate_random_profiles(num_profiles=100) -> list:
    profiles = []
    diet_types = ['Standard', 'Vegetarian', 'Vegan', 'Keto', 'High Protein']
    allergies_pool = ['Dairy', 'Nuts', 'Gluten', 'Soy', 'Eggs', 'Seafood']
    
    for i in range(num_profiles):
        diet = random.choice(diet_types)
        cal = random.randint(1500, 3200)
        
        # High protein means 2.2g per kg, standard 1.6g. Say roughly 100-220g.
        if diet == 'High Protein':
            prot = random.randint(150, 220)
        elif diet == 'Vegan':
            prot = random.randint(80, 140)
        else:
            prot = random.randint(100, 180)
            
        num_allergies = random.choices([0, 1, 2], weights=[0.7, 0.2, 0.1])[0]
        allergies = random.sample(allergies_pool, num_allergies) if num_allergies > 0 else []
        
        # Feasibility Heuristics
        is_feasible = True
        if diet == 'Vegan' and prot > 100:
            is_feasible = False
        if prot > (cal * 0.35) / 4.0: # Protein calories > 35% of total
            is_feasible = False
            
        profiles.append({
            "user_id": f"test_user_{i}",
            "target_calories": cal,
            "target_protein": prot,
            "diet_type": diet,
            "allergies": allergies,
            "dislikes": [],
            "is_feasible": is_feasible
        })
    return profiles

def run_benchmark():
    engine = NutritionEngineV6()
    profiles = generate_random_profiles(100)
    
    total_time = 0
    success_count = 0
    soft_accept_count = 0
    
    feasible_cal_errors = []
    feasible_pro_errors = []
    impossible_cal_errors = []
    impossible_pro_errors = []
    
    unique_meals_all = []
    used_foods = set()
    category_usage = defaultdict(set)
    
    # Get total foods
    total_ingredients = len(engine.food_graph.get_ingredients())
    total_recipes = len(engine.food_graph.get_recipes())
    total_foods_db = total_ingredients + total_recipes
    
    print(f"Starting Benchmark: 100 Profiles x 7 Days (2800 Meals)")
    print("-" * 50)
    
    start_time = time.time()
    
    for i, profile in enumerate(profiles):
        p_start = time.time()
        
        try:
            # We skip cache for benchmarking by forcing a unique week or user
            result = engine.generate_plan(profile, user_id=profile["user_id"], week_start="bench_week")
            p_time = time.time() - p_start
            total_time += p_time
            
            if result.get("status") in ["success", "warning"]:
                if result.get("status") == "success":
                    success_count += 1
                else:
                    soft_accept_count += 1
                    
                plan = result["weekly_plan"]
                targets = result["daily_targets"]
                
                # Analyze plan
                unique_meals = set()
                
                for day, day_plan in plan.items():
                    target_cal = targets[day]["calories"]
                    target_pro = targets[day]["protein"]
                    
                    actual_cal = 0
                    actual_pro = 0
                    
                    for meal_type, plate in day_plan.items():
                        if not plate:
                            continue
                        
                        # Derive meal signature for diversity tracking
                        if len(plate) > 0 and 'semantics' in plate[0]:
                            meal_id = plate[0]['semantics'].get('meal_id', 'unknown')
                            unique_meals.add(meal_id)
                            
                        for item in plate:
                            actual_cal += float(item['nutrition']['calories'])
                            actual_pro += float(item['nutrition']['protein'])
                            
                            food_id = item.get('food_id')
                            if food_id:
                                used_foods.add(food_id)
                                cat = item.get('semantics', {}).get('category', 'Other')
                                category_usage[cat].add(food_id)
                            
                    # Calculate daily errors
                    cal_err = abs(actual_cal - target_cal) / max(1, target_cal) * 100
                    pro_err = abs(actual_pro - target_pro) / max(1, target_pro) * 100
                    
                    if profile["is_feasible"]:
                        feasible_cal_errors.append(cal_err)
                        feasible_pro_errors.append(pro_err)
                    else:
                        impossible_cal_errors.append(cal_err)
                        impossible_pro_errors.append(pro_err)
                    
                unique_meals_all.append(len(unique_meals))
                
        except Exception as e:
            print(f"Profile {i} failed: {e}")
            
        if (i + 1) % 10 == 0:
            print(f"Processed {i + 1}/100 profiles...")
            
    end_time = time.time()
    
    # Compile Results
    avg_f_cal_err = sum(feasible_cal_errors) / len(feasible_cal_errors) if feasible_cal_errors else 0
    avg_f_pro_err = sum(feasible_pro_errors) / len(feasible_pro_errors) if feasible_pro_errors else 0
    
    avg_i_cal_err = sum(impossible_cal_errors) / len(impossible_cal_errors) if impossible_cal_errors else 0
    avg_i_pro_err = sum(impossible_pro_errors) / len(impossible_pro_errors) if impossible_pro_errors else 0
    
    avg_unique = sum(unique_meals_all) / len(unique_meals_all) if unique_meals_all else 0
    
    print("\n" + "=" * 50)
    print("V7 NUTRITION ENGINE BENCHMARK RESULTS")
    print("=" * 50)
    print(f"Total Profiles: 100")
    print(f"Success Rate: {success_count}/100 (Soft Accepted: {soft_accept_count}/100)")
    print(f"Total Time: {end_time - start_time:.2f}s (Avg: {total_time/100:.2f}s per plan)")
    print("-" * 50)
    print("Feasible Profiles:")
    print(f"  Average Calorie Error: {avg_f_cal_err:.2f}%")
    print(f"  Average Protein Error: {avg_f_pro_err:.2f}%")
    print("\nImpossible Profiles:")
    print(f"  Average Calorie Error: {avg_i_cal_err:.2f}%")
    print(f"  Average Protein Error: {avg_i_pro_err:.2f}%")
    print("-" * 50)
    print("Diversity KPIs:")
    print(f"  Average Unique Meals Per Week: {avg_unique:.1f} (Target: >15)")
    print(f"  Overall Dataset Utilization: {len(used_foods)} / {total_foods_db}")
    print("\nUtilization per Category:")
    
    for cat, items in sorted(category_usage.items()):
        print(f"  {cat}: {len(items)} items")
    print("=" * 50)

if __name__ == "__main__":
    run_benchmark()
