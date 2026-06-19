import sys, os
sys.path.insert(0, '.')
from app.deterministic_meal_engine import MealEngine as DatasetMealEngine
from collections import Counter

engine = DatasetMealEngine()

# Test with a real Indian user profile
profile = {
    'age': 24, 'weight': 72, 'height': 175, 'gender': 'Male',
    'goal': 'Muscle Gain', 'dietary_preference': 'Non-Veg',
    'allergies': ['Nuts'], 'activity_level': 'Active',
}

# 1. Check targets
targets = engine.calculate_daily_targets(profile)
print("=== DAILY TARGETS ===")
print("Calories:", targets["daily_calories"])
print("Protein:", targets["macro_targets_g"]["protein_g"], "g")
print("Carbs:", targets["macro_targets_g"]["carb_g"], "g")
print("Fat:", targets["macro_targets_g"]["fat_g"], "g")
print()

# 2. Generate weekly plan
plan = engine.generate_weekly_plan(profile)

# 3. Analyze each day
print("=== WEEKLY PLAN ANALYSIS ===")
all_items = []
for day, meals in plan["weekly_plan"].items():
    day_cal = day_pro = day_carb = day_fat = 0
    day_items = []
    for mt, items in meals.items():
        for item in items:
            day_cal += item["calories"]
            day_pro += item["protein"]
            day_carb += item["carbs"]
            day_fat += item["fat"]
            day_items.append((mt, item["name"], item["calories"], item["protein"]))
            all_items.append(item["name"])

    target_cal = targets["daily_calories"]
    target_pro = targets["macro_targets_g"]["protein_g"]
    cal_pct = day_cal / target_cal * 100
    pro_pct = day_pro / target_pro * 100

    cal_ok = "PASS" if abs(cal_pct - 100) <= 10 else "FAIL"
    pro_ok = "PASS" if abs(pro_pct - 100) <= 10 else "FAIL"

    print(f"{day}:")
    print(f"  Cal: {day_cal:.0f}/{target_cal} ({cal_pct:.0f}%) [{cal_ok}]")
    print(f"  Pro: {day_pro:.1f}g/{target_pro}g ({pro_pct:.0f}%) [{pro_ok}]")
    print(f"  Carb: {day_carb:.1f}g | Fat: {day_fat:.1f}g")
    for mt, name, cal, pro in day_items:
        print(f"    {mt:10s} | {cal:4.0f} cal | {pro:5.1f}g P | {name}")
    print()

# 4. Diversity analysis
print("=== DIVERSITY ANALYSIS ===")
freq = Counter(all_items)
print(f"Total items used: {len(all_items)}")
print(f"Unique items: {len(freq)}")
print()
print("Top 15 most repeated items:")
for name, count in freq.most_common(15):
    flag = " *** EXCESSIVE" if count >= 5 else ""
    print(f"  {count}x  {name}{flag}")
print()

# 5. Snack quality check
print("=== SNACK QUALITY CHECK ===")
for day, meals in plan["weekly_plan"].items():
    if "snack" in meals:
        for item in meals["snack"]:
            is_meal = any(x in item["name"].lower() for x in ["biryani","curry","paneer","chicken","thali","rice","dal","roti","naan"])
            flag = " *** NOT A SNACK!" if is_meal else ""
            print(f"  {day}: {item['name']} ({item['calories']} cal, {item['protein']}g P){flag}")

# 6. Allergen check
print()
print("=== ALLERGEN CHECK (Nuts allergy) ===")
import re
for day, meals in plan["weekly_plan"].items():
    for mt, items in meals.items():
        for item in items:
            name_lower = item["name"].lower()
            # Check if 'nut' appears - should be filtered
            if "nut" in name_lower:
                has_boundary = bool(re.search(r'\bnut', name_lower))
                print(f"  WARNING: {day}/{mt}: '{item['name']}' contains 'nut' (boundary match: {has_boundary})")
            if "peanut" in name_lower:
                print(f"  DANGER: {day}/{mt}: '{item['name']}' - peanut slipped through allergen filter!")

# 7. Profile 2: Female weight loss vegetarian
print()
print("=" * 60)
print("=== TEST 2: Female, Weight Loss, Veg ===")
profile2 = {
    'age': 30, 'weight': 65, 'height': 160, 'gender': 'Female',
    'goal': 'Weight Loss', 'dietary_preference': 'Veg',
    'allergies': [], 'activity_level': 'Light',
}
targets2 = engine.calculate_daily_targets(profile2)
print("Target Cal:", targets2["daily_calories"], "| Target Protein:", targets2["macro_targets_g"]["protein_g"], "g")

plan2 = engine.generate_weekly_plan(profile2)
for day, meals in plan2["weekly_plan"].items():
    day_cal = sum(i["calories"] for items in meals.values() for i in items)
    day_pro = sum(i["protein"] for items in meals.values() for i in items)
    cal_pct = day_cal / targets2["daily_calories"] * 100
    pro_pct = day_pro / targets2["macro_targets_g"]["protein_g"] * 100
    cal_s = "PASS" if abs(cal_pct - 100) <= 10 else "FAIL"
    pro_s = "PASS" if abs(pro_pct - 100) <= 10 else "FAIL"
    print(f"  {day}: {day_cal:.0f} cal ({cal_pct:.0f}%) [{cal_s}] | {day_pro:.1f}g P ({pro_pct:.0f}%) [{pro_s}]")
