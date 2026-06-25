import os
import sys
import json
import random
import time
from collections import defaultdict

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.nutrition_engine.engine import NutritionEngineV6

def generate_random_profiles(count=100):
    genders = ["male", "female"]
    goals = ["weight_loss", "maintenance", "muscle_gain"]
    diet_types = ["Vegetarian", "NonVeg", "Vegan", "Eggitarian"]
    activity_levels = ["sedentary", "light", "moderate", "heavy"]
    allergies_pool = [["nuts"], ["lactose"], ["gluten"], ["peanuts"], []]
    
    profiles = []
    for i in range(count):
        gender = random.choice(genders)
        goal = random.choice(goals)
        diet_type = random.choice(diet_types)
        activity_level = random.choice(activity_levels)
        allergies = random.choice(allergies_pool)
        
        weight = random.randint(50, 100) if gender == "male" else random.randint(45, 85)
        height = random.randint(160, 190) if gender == "male" else random.randint(150, 175)
        age = random.randint(18, 60)
        
        profiles.append({
            "name": f"Profile_{i+1}_{gender}_{goal}_{diet_type}",
            "weight_kg": weight,
            "height_cm": height,
            "age": age,
            "gender": gender,
            "activity_level": activity_level,
            "goal": goal,
            "diet_type": diet_type,
            "region": "pan_indian",
            "allergies": allergies
        })
    return profiles

def main():
    engine = NutritionEngineV6(data_dir='data', config_dir='config')
    profiles = generate_random_profiles(100)
    
    metrics = {
        "total_meals": 0,
        "total_days": 0,
        "protein_errors": [],
        "calorie_errors": [],
        "generation_times": [],
        "duplicate_meals": 0,
        "unrealistic_portions": 0,
        "unique_ingredients": set(),
        "total_ingredients_used": 0,
        "profiles_attempted": 0,
        "profiles_successful": 0,
        "profiles_failed": 0
    }
    
    agg_failure_reasons = defaultdict(int)
    agg_constraint_pressure = defaultdict(int)
    agg_acceptance_stats = defaultdict(int)
    
    print(f"Starting benchmark for {len(profiles)} profiles...")
    
    from app.nutrition_engine.nutrition_calculator import WeeklyMacroPlanner
    planner = WeeklyMacroPlanner()
    
    for idx, profile in enumerate(profiles):
        start_time = time.time()
        metrics["profiles_attempted"] += 1
        
        try:
            result = engine.generate_plan(profile)
            weekly_plan = result.get('weekly_plan', {})
            stats = result.get('stats', {})
            
            # Aggregate stats
            for k, v in stats.get("failure_reasons", {}).items():
                agg_failure_reasons[k] += v
            for k, v in stats.get("constraint_pressure", {}).items():
                agg_constraint_pressure[k] += v
            for k, v in stats.get("acceptance_stats", {}).items():
                agg_acceptance_stats[k] += v
                
            gen_time = time.time() - start_time
            metrics["generation_times"].append(gen_time)
            
            daily_targets = planner.plan_week(profile)
            
            for day_key, day_plan in weekly_plan.items():
                target = daily_targets.get(day_key, {})
                metrics["total_days"] += 1
                
                day_p = 0
                day_c = 0
                
                day_meals = []
                for meal_type in ['breakfast', 'lunch', 'snack', 'dinner']:
                    plate = day_plan.get(meal_type, [])
                    if not plate:
                        continue
                        
                    metrics["total_meals"] += 1
                    
                    meal_sig = []
                    for item in plate:
                        p = item['nutrition']['protein']
                        c = item['nutrition']['calories']
                        day_p += p
                        day_c += c
                        metrics["unique_ingredients"].add(item['food_id'])
                        metrics["total_ingredients_used"] += 1
                        meal_sig.append(item['food_id'])
                        
                        # Portion Realism check (simplistic heuristic for benchmark)
                        if item.get('qty', 1) > item.get('p_max', 5):
                            metrics["unrealistic_portions"] += 1
                            
                    meal_sig.sort()
                    day_meals.append(str(meal_sig))
                    
                if len(day_meals) != len(set(day_meals)):
                    metrics["duplicate_meals"] += 1
                
                if target.get('protein', 0) > 0:
                    metrics["protein_errors"].append(abs(day_p - target['protein']) / target['protein'])
                if target.get('calories', 0) > 0:
                    metrics["calorie_errors"].append(abs(day_c - target['calories']) / target['calories'])
            
            if result.get("status") == "success":
                metrics["profiles_successful"] += 1
            else:
                metrics["profiles_failed"] += 1
                
        except Exception as e:
            print(f"Failed to generate for {profile['name']}: {e}")
            metrics["profiles_failed"] += 1
            
        if (idx + 1) % 10 == 0:
            print(f"Processed {idx + 1}/{len(profiles)} profiles...")
            
    # Calculate aggregates
    avg_pro_err = (sum(metrics["protein_errors"]) / len(metrics["protein_errors"])) * 100 if metrics["protein_errors"] else 0
    max_pro_err = max(metrics["protein_errors"]) * 100 if metrics["protein_errors"] else 0
    avg_cal_err = (sum(metrics["calorie_errors"]) / len(metrics["calorie_errors"])) * 100 if metrics["calorie_errors"] else 0
    avg_gen_time = sum(metrics["generation_times"]) / len(metrics["generation_times"]) if metrics["generation_times"] else 0
    
    total_generated = agg_acceptance_stats["total_generated"]
    total_accepted = agg_acceptance_stats["total_accepted"]
    acceptance_rate = (total_accepted / max(total_generated, 1)) * 100
    
    total_failures = sum(agg_failure_reasons.values())
    failure_rows = ""
    for reason, count in sorted(agg_failure_reasons.items(), key=lambda x: x[1], reverse=True):
        pct = (count / max(total_failures, 1)) * 100
        failure_rows += f"| {reason.replace('_', ' ').title()} | {count} | {pct:.1f}% |\n"
        
    total_candidates = agg_constraint_pressure["total_candidates"]
    passed_structure = agg_constraint_pressure["passed_structure"]
    passed_portion = agg_constraint_pressure["passed_portion"]
    passed_macros = agg_constraint_pressure["passed_macros"]
    
    structure_pass_rate = (passed_structure / max(total_candidates, 1)) * 100
    portion_pass_rate = (passed_portion / max(passed_structure, 1)) * 100
    macro_pass_rate = (passed_macros / max(passed_portion, 1)) * 100
    
    recovery_successes = agg_acceptance_stats["recovery_successes"]
    recovery_failures = agg_acceptance_stats["recovery_failures"]
    total_recoveries = recovery_successes + recovery_failures
    recovery_rate = (recovery_successes / max(total_recoveries, 1)) * 100
    
    template_fail_pct = (agg_failure_reasons["template_exhausted"] / max(total_generated, 1)) * 100
    shopping_diversity = (len(metrics["unique_ingredients"]) / max(metrics["total_ingredients_used"], 1)) * 100
    
    report = f"""# V6 Engine Benchmark Report

## 📊 Core KPIs
| Metric | Target | Actual | Status |
|--------|--------|--------|--------|
| Generation Success Rate | ≥99% | {(metrics['profiles_successful'] / max(metrics['profiles_attempted'], 1)) * 100:.2f}% | {'✅' if metrics['profiles_successful'] >= metrics['profiles_attempted'] * 0.99 else '⚠️'} |
| Template Failure Rate | <1% | {template_fail_pct:.2f}% | {'✅' if template_fail_pct < 1 else '⚠️'} |
| Average Protein Error | <3% | {avg_pro_err:.2f}% | {'✅' if avg_pro_err < 3 else '⚠️'} |
| Maximum Protein Error | <5% | {max_pro_err:.2f}% | {'✅' if max_pro_err < 5 else '⚠️'} |
| Average Calorie Error | <3% | {avg_cal_err:.2f}% | {'✅' if avg_cal_err < 3 else '⚠️'} |
| Duplicate Meals | 0 | {metrics['duplicate_meals']} | {'✅' if metrics['duplicate_meals'] == 0 else '⚠️'} |
| Unrealistic Portions | 0 | {metrics['unrealistic_portions']} | {'✅' if metrics['unrealistic_portions'] == 0 else '⚠️'} |
| Weekly Plan Acceptance Rate | ≥95% | {acceptance_rate:.2f}% | {'✅' if acceptance_rate >= 95 else '⚠️'} |
| Average Generation Time | <2.0s | {avg_gen_time:.2f}s | {'✅' if avg_gen_time < 2.0 else '⚠️'} |
| Shopping Diversity Score | >85% | {(100 - shopping_diversity):.2f}% | (Experimental) |

## 📉 Failure Analysis
| Failure Reason | Count | % of Failures |
|----------------|-------|---------------|
{failure_rows}

## 🗜️ Constraint Pressure
| Stage | Pass Rate |
|-------|-----------|
| Structure | {structure_pass_rate:.1f}% |
| Portion | {portion_pass_rate:.1f}% |
| Macro | {macro_pass_rate:.1f}% |

## 🔄 Recovery
| Metric | Value |
|--------|-------|
| Recovery Attempts | {total_recoveries} |
| Recovery Success Rate | {recovery_rate:.1f}% |

## 📈 Details
- **Profiles Attempted:** {metrics['profiles_attempted']}
- **Profiles Successful:** {metrics['profiles_successful']}
- **Profiles Failed:** {metrics['profiles_failed']}
- **Total Days Generated:** {metrics['total_days']}
- **Total Meals Generated:** {metrics['total_meals']}
- **Total Generation Time:** {sum(metrics['generation_times']):.2f}s
"""

    with open("benchmark_report.md", "w", encoding="utf-8") as f:
        f.write(report)
        
    print("\nBenchmark completed. Report written to benchmark_report.md")

if __name__ == "__main__":
    main()
