import os
import json
import re
from collections import Counter
from app.nutrition_engine.food_graph import FoodGraph
from app.nutrition_engine.template_manager import TemplateManager
from app.nutrition_engine.candidate_generator import CandidateGenerator

base_dir = r"d:\Final Year Project\githubclone 22 mor\githubclone\ELEVATE_GITHUB\Elevate\backend-python"
ingredient_db_path = os.path.join(base_dir, 'data', 'ingredient_database.json')
recipe_db_path = os.path.join(base_dir, 'data', 'recipe_database.json')
relationship_path = os.path.join(base_dir, 'data', 'food_relationship_graph.json')
nutrition_path = os.path.join(base_dir, 'data', 'nutrition_production_final_v4.csv')
template_path = os.path.join(base_dir, 'config', 'meal_templates.yaml')

food_graph = FoodGraph(ingredient_db_path, recipe_db_path, relationship_path, nutrition_path)
template_manager = TemplateManager(template_path)
generator = CandidateGenerator(food_graph)

user_profile = {
    "weight_kg": 75,
    "height_cm": 180,
    "age": 28,
    "gender": "male",
    "activity_level": "moderate",
    "goal": "muscle_gain",
    "diet_type": "Vegetarian",
    "region": "pan_indian",
    "allergies": [],
    "never_recommend": []
}

original_is_safe_meal = generator._is_safe_meal
original_is_valid_composition = generator._is_valid_composition_with_reason
original_quick_quality_filter = generator._quick_quality_filter_with_reason

safe_meal_rejections = []
rejection_counter = Counter()
candidate_journeys = []

def patched_is_safe_meal(self, plate, user_profile):
    allergy_pattern, never_pattern = self._get_user_patterns(user_profile)
    for item in plate:
        name = item.get('food_name', '').lower()
        allergens = item.get('allergens', '').lower()
        
        reason = None
        if self.blocklist_pattern and self.blocklist_pattern.search(name):
            reason = 'BLOCKLIST_MATCH'
        elif allergy_pattern and (allergy_pattern.search(name) or allergy_pattern.search(allergens)):
            reason = 'ALLERGY_MATCH'
        elif never_pattern and never_pattern.search(name):
            reason = 'NEVER_RECOMMEND_MATCH'
            
        if reason:
            log_entry = {
                "food_name": item.get('food_name', ''),
                "food_id": item.get('food_id', ''),
                "user_diet": user_profile.get('diet_type', ''),
                "user_allergies": user_profile.get('allergies', []),
                "food_allergens": allergens,
                "reason_code": reason,
                "meal_role": item.get('semantics', {}).get('meal_role', ''),
                "dish_family": item.get('semantics', {}).get('dish_family', ''),
                "diet": item.get('identity', {}).get('diet', ''),
                "food_group": item.get('identity', {}).get('food_group', '')
            }
            safe_meal_rejections.append(log_entry)
            return False, reason
            
    return True, None

print("--- RUNNING GENERATION TO COLLECT DATA ---")
def generate_candidates_intercept(template, meal_type, diet_type, count, user_profile, day_seed):
    import random
    rng = random.Random(day_seed)
    
    blueprint_candidates = generator._get_blueprint_candidates(meal_type, diet_type, template, rng, 999, [1,10], set())
    dynamic_candidates = generator._get_dynamic_candidates(template, meal_type, diet_type, rng, set(), user_profile.get('goal'), user_profile.get('region'), {})
    
    raw_candidates = blueprint_candidates + dynamic_candidates
    rng.shuffle(raw_candidates)
    
    journeys_recorded = 0
    
    for plate in raw_candidates:
        journey = {
            "template": template.get('name', 'unknown'),
            "plate": [item.get('food_name', '') for item in plate],
            "roles": [item.get('semantics', {}).get('meal_role', '') for item in plate],
            "stages": []
        }
        
        safe, reason = patched_is_safe_meal(generator, plate, user_profile)
        if not safe:
            journey["stages"].append({"stage": "Safety", "result": "FAIL", "reason": reason})
            rejection_counter[reason] += 1
            if journeys_recorded < 20:
                candidate_journeys.append(journey)
                journeys_recorded += 1
            continue
        journey["stages"].append({"stage": "Safety", "result": "PASS"})
        
        comp_ok, comp_reason = original_is_valid_composition(plate, meal_type, template)
        if not comp_ok:
            journey["stages"].append({"stage": "Composition", "result": "FAIL", "reason": comp_reason})
            rejection_counter[comp_reason] += 1
            if journeys_recorded < 20:
                candidate_journeys.append(journey)
                journeys_recorded += 1
            continue
        journey["stages"].append({"stage": "Composition", "result": "PASS"})
        
        qf_pass, qf_penalty, qf_reason = original_quick_quality_filter(plate, meal_type, 150, 3000, user_profile.get('goal'))
        if not qf_pass:
            journey["stages"].append({"stage": "Quality", "result": "FAIL", "reason": qf_reason})
            rejection_counter[qf_reason] += 1
            if journeys_recorded < 20:
                candidate_journeys.append(journey)
                journeys_recorded += 1
            continue
        journey["stages"].append({"stage": "Quality", "result": "PASS"})
        
    return [], {}

templates = template_manager.get_templates_for_meal('lunch', 'pan_indian')
for i in range(10):  # Generate 10 days of candidates to get a good distribution
    generate_candidates_intercept(templates[0], 'Lunch', 'Vegetarian', 5, user_profile, i)

print("\n\n=== TASK 1 & 4: _is_safe_meal() DIAGNOSTICS & DATASET AUDIT (Sample of 5) ===")
for r in safe_meal_rejections[:5]:
    print(f"Rejected")
    print(f"Food: {r['food_name']}")
    print(f"Reason Code: {r['reason_code']}")
    print(f"User Allergies: {r['user_allergies']}")
    print(f"Food Allergens: {r['food_allergens']}")
    print(f"meal_role: {r['meal_role']}")
    print(f"dish_family: {r['dish_family']}")
    print(f"diet: {r['diet']}")
    print(f"food_group: {r['food_group']}")
    print("-" * 20)

print("\n\n=== TASK 2: REJECTION BREAKDOWN ===")
for reason, count in rejection_counter.most_common():
    print(f"{reason.ljust(25)} {count}")

print("\n\n=== TASK 3: CANDIDATE JOURNEYS (Sample of 3) ===")
for j in candidate_journeys[:3]:
    print(f"Template: {j['template']}")
    for food, role in zip(j['plate'], j['roles']):
        print(f"  {role} selected: {food}")
    for s in j['stages']:
        print(f"  -> {s['stage']}: {s['result']} {s.get('reason', '')}")
    print("-" * 20)

print("\n\n=== TASK 5: BLUEPRINT AUDIT (Sample of 3) ===")
lunch_bps = [bp for bp in generator.meal_blueprints if bp.get('meal_type', '').lower() == 'lunch']
for bp in lunch_bps[:3]:
    bp_id = bp.get('meal_id', 'unknown')
    required_roles = set(r.get('role', '') for r in templates[0].get('required', []))
    actual_roles = set(item.get('semantics', {}).get('meal_role', '') for item in bp.get('plate', []))
    missing = required_roles - actual_roles
    print(f"Blueprint ID: {bp_id}")
    print(f"Required: {required_roles}")
    print(f"Actual: {actual_roles}")
    print(f"Missing: {missing}")
    print("-" * 20)

print("\n\n=== TASK 6: CANDIDATE STATISTICS ===")
total_rejections = sum(rejection_counter.values())
print(f"{'Rule'.ljust(25)} {'Count'.ljust(10)} {'Percent'}")
for reason, count in rejection_counter.most_common():
    pct = (count / total_rejections) * 100 if total_rejections else 0
    print(f"{reason.ljust(25)} {count:<10} {pct:.1f}%")

