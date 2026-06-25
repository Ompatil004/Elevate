import pandas as pd
import json
import os
from datetime import datetime, timezone

METADATA_FILE = 'data/food_knowledge_base.json'
RELATIONSHIP_FILE = 'data/food_relationship_graph.json'
REPORT_FILE = 'data/semantic_graph_report.json'
NUTRITION_FILE = 'data/nutrition_production_final_v4.csv'
GENERATION_VERSION = "1.0.0"

def load_json_if_exists(filepath):
    if os.path.exists(filepath):
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return {}
    return {}

def infer_food_semantics(row):
    name = str(row.get('food_name', '')).lower()
    cat = str(row.get('category', '')).lower()
    subcat = str(row.get('subcategory', '')).lower()
    prot = float(row.get('protein_g', 0))
    cal = float(row.get('calories_kcal', 0))
    
    # Defaults and confidence
    confidence = 90
    family = "unknown"
    plate_role = "unknown"
    meal_role = "unknown"
    food_type = "unknown"
    course = "main_course"
    
    # 1. Infer Family & Type using multiple signals (name, cat, subcat)
    if 'chicken' in name or 'poultry' in cat:
        family, food_type = "poultry", "meat"
    elif 'fish' in name or 'prawn' in name or 'seafood' in cat:
        family, food_type = "seafood", "meat"
    elif 'egg' in name or 'omelette' in name or 'anda' in name:
        family, food_type = "egg", "egg_dish"
    elif 'paneer' in name:
        family, food_type = "dairy", "paneer_dish"
    elif 'dal' in name or 'lentil' in name or 'sambar' in name or 'rajma' in name or 'chole' in name or 'legume' in cat:
        family, food_type = "legume", "dal_curry"
    elif 'rice' in name or 'pulao' in name or 'biryani' in name or 'khichdi' in name:
        family, food_type = "grain", "rice_dish"
    elif 'roti' in name or 'chapati' in name or 'paratha' in name or 'naan' in name or 'bread' in name or 'breads' in cat:
        family, food_type = "grain", "flatbread"
    elif 'oats' in name or 'muesli' in name or 'porridge' in name:
        family, food_type = "grain", "cereal"
    elif 'salad' in name or 'kosambari' in name or 'salad' in cat:
        family, food_type = "vegetable", "salad"
    elif 'soup' in name or 'shorba' in name or 'soup' in cat:
        family, food_type = "vegetable", "soup"
    elif 'milk' in name or 'shake' in name or 'lassi' in name or 'chaas' in name or 'juice' in name or 'tea' in name or 'coffee' in name or 'beverage' in cat:
        family, food_type = "beverage", "drink"
        course = "beverage"
    elif 'fruit' in name or 'apple' in name or 'banana' in name or 'orange' in name or 'fruit' in cat:
        family, food_type = "fruit", "whole_fruit"
    elif 'curd' in name or 'yogurt' in name or 'raita' in name:
        family, food_type = "dairy", "yogurt"
    elif 'sabzi' in name or 'curry' in name or 'bhindi' in name or 'aloo' in name:
        family, food_type = "vegetable", "curry"
    elif 'dosa' in name or 'idli' in name or 'uttapam' in name or 'poha' in name or 'upma' in name:
        family, food_type = "grain", "breakfast_item"
    elif 'nuts' in name or 'almond' in name or 'walnut' in name or 'seeds' in name or 'nut' in cat:
        family, food_type = "nuts_seeds", "snack"
    elif 'whey' in name or 'protein' in name or 'supplement' in cat:
        family, food_type = "supplement", "drink"
    elif 'snack' in cat:
        family, food_type = "other", "snack"
    else:
        # Fallback based on macros
        confidence = 50
        if prot > 15:
            family, food_type = "unknown", "meat"
        elif cal < 50:
            family, food_type = "vegetable", "side"

    # 2. Infer Plate Role & Meal Role
    if food_type in ['rice_dish', 'flatbread', 'cereal']:
        plate_role = "base"
        meal_role = "carb_base"
        if 'biryani' in name or 'khichdi' in name:
            plate_role = "main"
            meal_role = "combo_meal"
    elif food_type in ['meat', 'egg_dish', 'paneer_dish', 'dal_curry']:
        plate_role = "main"
        meal_role = "protein_main" if prot > 5 else "veg_side"
    elif food_type == 'curry':
        plate_role = "main" if prot > 10 else "side"
        meal_role = "protein_main" if prot > 10 else "veg_side"
    elif food_type == 'salad':
        plate_role = "side"
        meal_role = "salad"
    elif food_type == 'yogurt':
        plate_role = "accompaniment"
        meal_role = "dairy_side"
    elif food_type == 'drink':
        plate_role = "drink"
        meal_role = "beverage"
    elif food_type == 'breakfast_item':
        plate_role = "main"
        meal_role = "combo_meal"
    elif food_type in ['whole_fruit', 'snack']:
        plate_role = "snack"
        meal_role = "snack"
    else:
        confidence -= 20
        
    # 3. Suitability Scoring
    suitability = {"breakfast": 0, "lunch": 0, "dinner": 0, "snack": 0}
    
    # Contextual check: e.g. "sandwich" isn't strictly breakfast if it has chicken
    if meal_role == "combo_meal" and food_type == "breakfast_item":
        suitability = {"breakfast": 100, "lunch": 20, "dinner": 20, "snack": 60}
    elif food_type in ['cereal']:
        suitability = {"breakfast": 100, "lunch": 0, "dinner": 0, "snack": 30}
    elif meal_role in ['protein_main', 'carb_base', 'veg_side', 'salad']:
        if food_type in ['egg_dish', 'flatbread']:
            suitability = {"breakfast": 80, "lunch": 100, "dinner": 100, "snack": 20}
        else:
            suitability = {"breakfast": 10, "lunch": 100, "dinner": 100, "snack": 10}
    elif meal_role == "beverage":
        if 'tea' in name or 'coffee' in name:
            suitability = {"breakfast": 100, "lunch": 10, "dinner": 5, "snack": 100}
        elif 'shake' in name or 'smoothie' in name:
            suitability = {"breakfast": 80, "lunch": 10, "dinner": 10, "snack": 100}
        else:
            suitability = {"breakfast": 80, "lunch": 80, "dinner": 80, "snack": 80}
    elif meal_role == "snack":
        suitability = {"breakfast": 60, "lunch": 10, "dinner": 10, "snack": 100}
    else:
        suitability = {"breakfast": 50, "lunch": 50, "dinner": 50, "snack": 50}

    # 4. Servings
    unit = "g"
    step = 50.0
    def_qty = float(row.get('serving_size_g', 100))
    min_qty = def_qty * 0.5
    max_qty = def_qty * 2.0
    
    if 'bowl' in str(row.get('serving_unit', 'g')).lower() or food_type in ['dal_curry', 'curry', 'salad', 'soup', 'yogurt', 'cereal']:
        unit = "bowl"
        def_qty, step, min_qty, max_qty = 1.0, 0.5, 0.5, 2.0
    elif food_type in ['flatbread', 'egg_dish', 'whole_fruit', 'breakfast_item'] and 'oats' not in name:
        unit = "piece"
        def_qty, step, min_qty, max_qty = 2.0, 1.0, 1.0, 4.0
        if food_type == 'whole_fruit':
            def_qty, max_qty = 1.0, 2.0
    elif food_type == 'rice_dish':
        unit = "plate"
        def_qty, step, min_qty, max_qty = 1.0, 0.5, 0.5, 1.5
    elif food_type == 'drink':
        unit = "glass" if 'tea' not in name and 'coffee' not in name else "cup"
        def_qty, step, min_qty, max_qty = 1.0, 0.5, 0.5, 2.0

    servings = {
        "unit": unit,
        "default": def_qty,
        "typical": def_qty,
        "minimum": min_qty,
        "maximum": max_qty,
        "step": step
    }
    
    # 5. Metadata
    frequency = "weekly"
    if family in ['grain', 'legume', 'vegetable', 'fruit', 'dairy', 'egg']:
        frequency = "daily"
    if food_type in ['rice_dish', 'meat'] and ('biryani' in name or 'mutton' in name):
        frequency = "occasional"
        
    return {
        "semantics": {
            "meal_role": meal_role,
            "food_type": food_type,
            "plate_role": plate_role,
            "course": course,
            "family": family
        },
        "identity": {
            "cuisine": str(row.get('region', 'All India')),
            "meal_style": food_type.replace('_', ' ').title(),
            "diet": "Vegan" if row.get('is_vegan', False) else "Vegetarian" if row.get('is_vegetarian', False) else "NonVeg"
        },
        "meal_suitability": suitability,
        "servings": servings,
        "metadata": {
            "frequency": frequency,
            "requires_stove": True if food_type not in ['whole_fruit', 'salad', 'yogurt', 'drink', 'snack'] else False,
            "requires_blender": True if 'smoothie' in name or 'shake' in name else False,
            "prep_time_min": 30 if plate_role == 'main' else 10
        },
        "audit": {
            "status": "generated",
            "confidence": confidence,
            "generated_by": "heuristics_v1",
            "generation_version": GENERATION_VERSION,
            "last_updated": datetime.now(timezone.utc).isoformat()
        }
    }

def infer_relationships(food_id, name, semantics):
    req = []
    pref = []
    opt = []
    comp = {
        "carb_base": 50,
        "protein_main": 50,
        "veg_side": 50,
        "salad": 50,
        "dairy_side": 50,
        "beverage": 50,
        "snack": 50,
        "combo_meal": 50
    }
    
    plate_role = semantics['plate_role']
    meal_role = semantics['meal_role']
    
    # Structured relationship objects
    if meal_role == "protein_main":
        req = [{"role": "carb_base", "minimum": 1, "maximum": 1}]
        pref = [{"role": "salad", "weight": 80}, {"role": "dairy_side", "weight": 70}]
        opt = [{"role": "veg_side", "weight": 40}]
        comp.update({"carb_base": 100, "salad": 90, "dairy_side": 80, "beverage": 30})
    elif meal_role == "carb_base":
        req = [{"role": "protein_main", "minimum": 1, "maximum": 1}]
        pref = [{"role": "veg_side", "weight": 90}, {"role": "dairy_side", "weight": 80}]
        comp.update({"protein_main": 100, "veg_side": 90, "dairy_side": 80, "salad": 80})
    elif meal_role == "combo_meal":
        pref = [{"role": "dairy_side", "weight": 90}, {"role": "beverage", "weight": 80}]
        opt = [{"role": "salad", "weight": 50}]
        comp.update({"protein_main": 0, "carb_base": 0, "dairy_side": 90, "beverage": 80})
    elif meal_role == "snack":
        comp.update({"snack": 80, "beverage": 90, "protein_main": 0, "carb_base": 0})
        
    return {
        "food_name": name,
        "structural_rules": {
            "requires": req,
            "preferred": pref,
            "optional": opt
        },
        "compatibility": comp,
        "batch_cooking": [name] if plate_role == 'main' or meal_role == 'carb_base' else []
    }

def main():
    print(f"Loading {NUTRITION_FILE}...")
    try:
        df = pd.read_csv(NUTRITION_FILE)
    except FileNotFoundError:
        print(f"File {NUTRITION_FILE} not found. Please ensure it exists.")
        return
        
    old_meta = load_json_if_exists(METADATA_FILE)
    old_rel = load_json_if_exists(RELATIONSHIP_FILE)
    
    new_meta = {}
    new_rel = {}
    
    report = {
        "foods_processed": len(df),
        "metadata_generated": 0,
        "manual_preserved": 0,
        "missing_family": 0,
        "missing_meal_role": 0,
        "low_confidence": 0,
        "graph_version": GENERATION_VERSION
    }
    
    for idx, row in df.iterrows():
        fid = str(row['food_id'])
        fname = str(row['food_name'])
        
        # Check idempotency
        existing_meta = old_meta.get(fid, {})
        status = existing_meta.get('audit', {}).get('status', '')
        if status in ['reviewed', 'dietitian_verified']:
            new_meta[fid] = existing_meta
            new_rel[fid] = old_rel.get(fid, {})
            report["manual_preserved"] += 1
            continue
            
        # Generate Metadata
        meta = infer_food_semantics(row)
        meta['food_name'] = fname
        new_meta[fid] = meta
        
        # Tracking metrics for report
        report["metadata_generated"] += 1
        if meta['semantics']['family'] == "unknown":
            report["missing_family"] += 1
        if meta['semantics']['meal_role'] == "unknown":
            report["missing_meal_role"] += 1
        if meta['audit']['confidence'] <= 50:
            report["low_confidence"] += 1
        
        # Generate Relationships
        rel = infer_relationships(fid, fname, meta['semantics'])
        new_rel[fid] = rel
        
    # Save Outputs
    with open(METADATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(new_meta, f, indent=2)
        
    with open(RELATIONSHIP_FILE, 'w', encoding='utf-8') as f:
        json.dump(new_rel, f, indent=2)
        
    with open(REPORT_FILE, 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2)
        
    print(f"Generated 3-Layer Graph (Version {GENERATION_VERSION})")
    print(f"   - Nodes Processed: {report['foods_processed']}")
    print(f"   - Nodes Generated: {report['metadata_generated']}")
    print(f"   - Manual Preserved: {report['manual_preserved']}")
    print(f"   - Low Confidence: {report['low_confidence']}")
    print(f"   - Saved report -> {REPORT_FILE}")

if __name__ == "__main__":
    main()
