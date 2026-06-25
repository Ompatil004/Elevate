import json
import yaml
import os

def run_audit():
    with open('data/food_knowledge_base.json', 'r', encoding='utf-8') as f:
        kb = json.load(f)
        
    with open('config/meal_templates.yaml', 'r', encoding='utf-8') as f:
        templates = yaml.safe_load(f)

    issues = {
        "diet_classification": [],
        "meal_suitability": [],
        "portion_realism": [],
        "template_feasibility": [],
        "data_gaps": []
    }

    # 1 & 2. Diet & Suitability
    for fid, food in kb.items():
        name = food.get("food_name", "").lower()
        diet = food.get("diet_type", "")
        
        # Check Vegetarian for eggs/meat
        if diet == "Vegetarian":
            bad_words = ["egg", "anda", "chicken", "mutton", "fish", "beef", "pork", "meat", "boti", "tikka", "kebab"]
            # Exclude paneer tikka etc
            meat_words = ["chicken", "mutton", "fish", "beef", "pork", "meat"]
            egg_words = ["egg", "anda", "omelet"]
            
            if any(w in name for w in meat_words):
                issues["diet_classification"].append(f"[Meat in Veg] {food['food_name']}")
            elif any(w in name for w in egg_words):
                issues["diet_classification"].append(f"[Egg in Veg] {food['food_name']}")
                
        # Check Vegan for dairy/honey/meat
        if diet == "Vegan":
            dairy = ["milk", "cheese", "paneer", "curd", "yogurt", "ghee", "butter", "honey", "egg", "chicken", "mutton", "fish"]
            if any(w in name for w in dairy):
                issues["diet_classification"].append(f"[Animal product in Vegan] {food['food_name']}")

        # Meal Suitability
        mp = food.get("meal_priority", {})
        def get_score(m):
            v = mp.get(m, 0)
            return v.get("score", 0) if isinstance(v, dict) else float(v)
            
        brk = get_score("breakfast")
        lun = get_score("lunch")
        din = get_score("dinner")
        snk = get_score("snack")
        
        if "chicken" in name or "mutton" in name or "fish" in name:
            if brk > 0.3:
                issues["meal_suitability"].append(f"[Heavy Meat for Breakfast] {food['food_name']} (score: {brk})")
            if snk > 0.5 and "kebab" not in name and "tikka" not in name:
                issues["meal_suitability"].append(f"[Curry/Heavy Meat for Snack] {food['food_name']} (score: {snk})")
                
        if "milkshake" in name or "smoothie" in name:
            if lun > 0.3 or din > 0.3:
                issues["meal_suitability"].append(f"[Liquid Sweet for Main Meal] {food['food_name']} (Lunch: {lun}, Dinner: {din})")

        # Portion Realism
        cap = food.get("nutrition_capacity", {})
        max_q = cap.get("max_qty", 0)
        unit = food.get("serving_unit", "")
        
        if unit in ["g", "ml"] and max_q > 600:
            issues["portion_realism"].append(f"[Massive Portion] {food['food_name']} allows up to {max_q}{unit}")
        if unit in ["pieces", "slice", "bowl"] and max_q > 6:
            issues["portion_realism"].append(f"[High Item Count] {food['food_name']} allows up to {max_q} {unit}")
            
        if "salad" in name and unit == "g" and max_q < 100:
            issues["portion_realism"].append(f"[Tiny Salad Limit] {food['food_name']} max is {max_q}{unit}")

    # Template Feasibility
    regions = templates.get("regions", {})
    for region, region_data in regions.items():
        for meal_type, meals in region_data.items():
            for t in meals:
                t_id = t.get("id")
                req = t.get("required", [])
                
                # Check if template has anchor
                if "anchor" not in t:
                    issues["template_feasibility"].append(f"[No Anchor] Template {t_id}")
                    
                cap = t.get("nutrition", {}).get("capacity", {})
                max_p = cap.get("protein", {}).get("max", 0)
                
                # If template allows > 80g protein but only requires low protein roles
                roles = [r["role"] for r in req]
                if max_p > 80 and "protein_main" not in roles and "meat_main" not in roles:
                    issues["template_feasibility"].append(f"[High Protein without Protein Role] Template {t_id} (Max P: {max_p}g) roles: {roles}")

    with open('red_team_audit_results.json', 'w', encoding='utf-8') as f:
        json.dump(issues, f, indent=4)
        
    print("Audit complete. Results saved to red_team_audit_results.json")

if __name__ == "__main__":
    run_audit()
