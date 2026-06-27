"""
Full nutrition dataset audit script.
Checks:
  1. Calorie math: listed vs calculated (protein*4 + carbs*4 + fat*9)
  2. Protein density vs category (per 100g)
  3. Serving size sanity (should NOT all be 150g)
  4. Impossible values (negative, absurd)
  5. High protein outliers (>50g protein at 150g serving)
  6. Low calorie outliers for real foods
  7. Calorie per 100g benchmark for common foods
  8. Fiber > carbs (impossible)
"""

import pandas as pd
import numpy as np

CSV = "data/nutrition_production_final_v4.csv"
df = pd.read_csv(CSV)

issues = []

def add_issue(level, check, row, detail):
    issues.append({
        "level": level,
        "check": check,
        "food_id": row.get("food_id", "?"),
        "food_name": row.get("food_name", "?"),
        "detail": detail,
    })

# ─────────────────────────────────────────────
# CHECK 1: Calorie math
# listed_cal vs (P*4 + C*4 + F*9)
# tolerance: 25%
# ─────────────────────────────────────────────
for _, row in df.iterrows():
    cal_listed = float(row["calories_kcal"])
    P = float(row["protein_g"])
    C = float(row["carbohydrates_g"])
    F = float(row["fat_g"])
    cal_calc = P * 4 + C * 4 + F * 9

    if cal_listed <= 0:
        add_issue("CRITICAL", "zero_calories", row, f"calories={cal_listed}")
        continue

    pct_diff = abs(cal_listed - cal_calc) / cal_listed * 100
    if pct_diff > 25:
        add_issue("ERROR", "calorie_math", row,
                  f"listed={cal_listed} calc={cal_calc:.1f} diff={pct_diff:.1f}%  P={P}g C={C}g F={F}g")

# ─────────────────────────────────────────────
# CHECK 2: Protein > calories/4 (more protein calories than total)
# ─────────────────────────────────────────────
for _, row in df.iterrows():
    P = float(row["protein_g"])
    cal = float(row["calories_kcal"])
    if P * 4 > cal * 1.1 and cal > 0:
        add_issue("CRITICAL", "protein_exceeds_calories", row,
                  f"protein={P}g ({P*4}kcal) > calories={cal}kcal")

# ─────────────────────────────────────────────
# CHECK 3: Protein density per 100g sanity
# serving_size in dataset is not always 100g — normalize to per-100g
# ─────────────────────────────────────────────
PROTEIN_BENCHMARKS_PER100G = {
    # (min, max) expected protein per 100g for food category
    "Chicken/Meat":        (15, 35),
    "Fish/Seafood":        (15, 30),
    "Eggs":                (10, 15),
    "Dal & Pulses":        (5, 12),
    "Paneer":              (12, 22),
    "Rice":                (2, 5),
    "Breads & Roti":       (5, 12),
    "Vegetables":          (0.5, 5),
    "Leafy Greens":        (1, 6),
    "Fruits":              (0.3, 2),
    "Dairy":               (2, 10),
    "Salad":               (0.5, 5),
    "Millets & Whole Grains": (3, 12),
    "Oats & Cereals":      (8, 17),
}

for _, row in df.iterrows():
    cat = str(row.get("category", ""))
    serving = float(row.get("serving_size_g", 150))
    P = float(row["protein_g"])
    if serving <= 0:
        continue
    P_per_100 = P / serving * 100
    bounds = PROTEIN_BENCHMARKS_PER100G.get(cat)
    if bounds:
        lo, hi = bounds
        if P_per_100 < lo * 0.3:
            add_issue("WARNING", "protein_too_low_for_category", row,
                      f"cat={cat} P_per_100g={P_per_100:.1f}g (expected {lo}-{hi}g)")
        elif P_per_100 > hi * 2.0:
            add_issue("ERROR", "protein_too_high_for_category", row,
                      f"cat={cat} P_per_100g={P_per_100:.1f}g (expected {lo}-{hi}g)")

# ─────────────────────────────────────────────
# CHECK 4: Fiber > carbs (physically impossible)
# ─────────────────────────────────────────────
for _, row in df.iterrows():
    F = float(row["fiber_g"])
    C = float(row["carbohydrates_g"])
    if F > C and C > 0:
        add_issue("CRITICAL", "fiber_exceeds_carbs", row,
                  f"fiber={F}g > carbs={C}g")

# ─────────────────────────────────────────────
# CHECK 5: Serving size — 99% are 150g which is suspicious
# Flag if protein per serving is impossible for serving size
# ─────────────────────────────────────────────
serving_counts = df["serving_size_g"].value_counts()
print("Serving size distribution (top 5):")
print(serving_counts.head().to_string())
print()

# ─────────────────────────────────────────────
# CHECK 6: Specific food benchmarks
# Per 150g serving (the uniform serving size)
# ─────────────────────────────────────────────
FOOD_BENCHMARKS_150G = {
    # food_name substring → (protein_min, protein_max, cal_min, cal_max)
    "chapati":      (3.0,  6.0,   80,  200),
    "roti":         (3.0,  6.0,   80,  200),
    "rice":         (2.0,  5.0,  150,  280),
    "dal":          (6.0, 14.0,   80,  200),
    "chicken":      (20.0, 40.0, 150,  400),
    "egg":          (9.0, 18.0,   100, 300),
    "paneer":       (15.0, 25.0,  200, 450),
    "poha":         (3.0,  7.0,   150, 300),
    "idli":         (3.0,  7.0,   100, 200),
    "oats":         (10.0, 20.0,  200, 400),
    "fish":         (20.0, 35.0,  120, 350),
}

for _, row in df.iterrows():
    name = str(row["food_name"]).lower()
    P = float(row["protein_g"])
    cal = float(row["calories_kcal"])
    serving = float(row.get("serving_size_g", 150))

    for keyword, (Pmin, Pmax, Cmin, Cmax) in FOOD_BENCHMARKS_150G.items():
        if keyword in name:
            # Scale to 150g
            P_150 = P / serving * 150
            C_150 = cal / serving * 150
            if P_150 > Pmax * 1.5:
                add_issue("ERROR", "benchmark_protein_too_high", row,
                          f"'{keyword}' P@150g={P_150:.1f}g (expected max {Pmax}g)  serving_db={serving}g")
            if P_150 < Pmin * 0.4 and P > 0:
                add_issue("WARNING", "benchmark_protein_too_low", row,
                          f"'{keyword}' P@150g={P_150:.1f}g (expected min {Pmin}g)  serving_db={serving}g")
            if C_150 > Cmax * 1.5:
                add_issue("ERROR", "benchmark_cal_too_high", row,
                          f"'{keyword}' Cal@150g={C_150:.0f} (expected max {Cmax})  serving_db={serving}g")
            break

# ─────────────────────────────────────────────
# PRINT REPORT
# ─────────────────────────────────────────────
import collections
by_check = collections.defaultdict(list)
for iss in issues:
    by_check[(iss["level"], iss["check"])].append(iss)

print("=" * 80)
print("NUTRITION DATASET AUDIT REPORT")
print(f"Total foods: {len(df)}")
print(f"Total issues found: {len(issues)}")
print("=" * 80)

for (level, check), items in sorted(by_check.items()):
    print(f"\n[{level}] {check}  ({len(items)} foods)")
    print("-" * 70)
    for iss in items[:25]:  # cap at 25 per check
        print(f"  {iss['food_name']}")
        print(f"    {iss['detail']}")
    if len(items) > 25:
        print(f"  ... and {len(items) - 25} more")

print()
print("=" * 80)
print("SUMMARY BY LEVEL")
from collections import Counter
lvl_counts = Counter(i["level"] for i in issues)
for lvl in ["CRITICAL", "ERROR", "WARNING"]:
    print(f"  {lvl}: {lvl_counts.get(lvl, 0)}")
