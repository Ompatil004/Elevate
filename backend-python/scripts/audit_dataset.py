import os
import json
import pandas as pd
from typing import Dict, List, Any

BASE_DIR = r"d:\Final Year Project\githubclone 22 mor\githubclone\ELEVATE_GITHUB\Elevate\backend-python"
DATA_PATH = os.path.join(BASE_DIR, 'data', 'nutrition_production_final_v4.csv')
REPORT_JSON_PATH = os.path.join(BASE_DIR, 'data', 'dataset_qa_report.json')
REPORT_MD_PATH = os.path.join(BASE_DIR, 'data', 'dataset_qa_report.md')

def main():
    print(f"Loading dataset from {DATA_PATH}...")
    try:
        df = pd.read_csv(DATA_PATH)
    except Exception as e:
        print(f"Error loading CSV: {e}")
        return

    # Report structure
    report = {
        "critical": [],
        "warning": [],
        "info": [],
        "alias_map": {}
    }

    # 1. Critical: Duplicate IDs
    id_counts = df['food_id'].value_counts()
    dupe_ids = id_counts[id_counts > 1].index.tolist()
    for did in dupe_ids:
        report["critical"].append(f"Duplicate food_id found: {did}")

    # 2. Critical: Exact Duplicate Names
    name_counts = df['food_name'].str.lower().str.strip().value_counts()
    dupe_names = name_counts[name_counts > 1].index.tolist()
    for dname in dupe_names:
        report["critical"].append(f"Exact duplicate food_name found: {dname}")

    # Process rows
    names_seen = {}
    
    for idx, row in df.iterrows():
        name = str(row.get('food_name', '')).strip()
        if not name or pd.isna(name) or name.lower() == 'nan':
            report["critical"].append(f"Row {idx} has missing food_name.")
            continue
            
        name_lower = name.lower()

        # Build rough alias map (e.g. Curd Rice / Dahi Rice)
        words = set(name_lower.replace(',', '').split())
        
        # Simple alias detection heuristics
        base_names = ['rice', 'roti', 'chapati', 'dal', 'paneer', 'chicken', 'salad', 'curry']
        for bn in base_names:
            if bn in words:
                if bn not in report["alias_map"]:
                    report["alias_map"][bn] = []
                report["alias_map"][bn].append(name)
        
        # 3. Critical: Impossible Macros (Deviation > 15%)
        cal = pd.to_numeric(row.get('calories_kcal', 0), errors='coerce') or 0.0
        pro = pd.to_numeric(row.get('protein_g', 0), errors='coerce') or 0.0
        carb = pd.to_numeric(row.get('carbohydrates_g', 0), errors='coerce') or 0.0
        fat = pd.to_numeric(row.get('fat_g', 0), errors='coerce') or 0.0
        
        calc_cal = (pro * 4) + (carb * 4) + (fat * 9)
        
        if calc_cal > 0:
            diff = abs(cal - calc_cal) / calc_cal
            if diff > 0.15:
                report["critical"].append(f"[{name}] Macro mismatch! Stated Cal: {cal}, Calculated: {calc_cal:.1f} (Deviation: {diff*100:.1f}%)")
        elif cal > 0:
            report["critical"].append(f"[{name}] Has {cal} calories but zero macros.")
        elif cal == 0 and (pro > 0 or carb > 0 or fat > 0):
            report["critical"].append(f"[{name}] Has 0 calories but non-zero macros.")

        # 4. Warnings: Contradictions
        vegan = row.get('is_vegan', False)
        dairy = row.get('contains_dairy', False)
        meat = row.get('contains_meat', False)
        egg = row.get('contains_egg', False)
        fish = row.get('contains_fish', False)
        
        if vegan in [True, 'True', '1', 1, 'Yes', 'yes']:
            if dairy in [True, 'True', '1', 1, 'Yes', 'yes']:
                report["warning"].append(f"[{name}] Marked as Vegan but Contains Dairy.")
            if meat in [True, 'True', '1', 1, 'Yes', 'yes']:
                report["warning"].append(f"[{name}] Marked as Vegan but Contains Meat.")
            if egg in [True, 'True', '1', 1, 'Yes', 'yes']:
                report["warning"].append(f"[{name}] Marked as Vegan but Contains Egg.")

    # Convert alias map to suggestions
    for base, variants in list(report["alias_map"].items()):
        if len(variants) > 1:
            report["info"].append(f"Alias group detected for '{base.title()}': {', '.join(variants)}")
        else:
            del report["alias_map"][base] # remove if only 1

    # Write JSON report
    with open(REPORT_JSON_PATH, 'w') as f:
        json.dump(report, f, indent=4)
        
    # Write MD report
    with open(REPORT_MD_PATH, 'w', encoding='utf-8') as f:
        f.write("# Dataset QA Report\n\n")
        
        f.write("## 🔴 Critical (Blocks Production)\n")
        if not report["critical"]:
            f.write("*None*\n")
        for item in report["critical"][:100]:
            f.write(f"- {item}\n")
        if len(report["critical"]) > 100:
            f.write(f"- *...and {len(report['critical']) - 100} more.*\n")
            
        f.write("\n## 🟡 Warnings (Review Needed)\n")
        if not report["warning"]:
            f.write("*None*\n")
        for item in report["warning"][:100]:
            f.write(f"- {item}\n")
        if len(report["warning"]) > 100:
            f.write(f"- *...and {len(report['warning']) - 100} more.*\n")
            
        f.write("\n## 🔵 Info (Suggestions & Aliases)\n")
        if not report["info"]:
            f.write("*None*\n")
        for item in report["info"][:100]:
            f.write(f"- {item}\n")
        if len(report["info"]) > 100:
            f.write(f"- *...and {len(report['info']) - 100} more.*\n")

    print(f"Audit complete. Found {len(report['critical'])} critical issues, {len(report['warning'])} warnings, {len(report['info'])} info logs.")
    print(f"Reports saved to {REPORT_JSON_PATH} and {REPORT_MD_PATH}")

if __name__ == '__main__':
    main()
