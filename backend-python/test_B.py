"""Test section B: Plan generation for 3 profiles + determinism + swap tests"""
import sys, io, os, re
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), 'app'))

from deterministic_meal_engine import MealEngine, FOOD_NAME_BLOCKLIST

PASS = "[PASS]"; FAIL = "[FAIL]"; WARN = "[WARN]"
fails = []; warns = []

def ok(label, cond, got="", exp=""):
    if cond:
        print(f"  {PASS} {label}")
    else:
        print(f"  {FAIL} {label}")
        if got: print(f"         got: {got!r}")
        if exp:  print(f"         exp: {exp!r}")
        fails.append(label)

def warn(label, cond, got="", exp=""):
    if cond:
        print(f"  {PASS} {label}")
    else:
        print(f"  {WARN} {label}")
        if got: print(f"         got: {got!r}")
        warns.append(label)

engine = MealEngine()
DAYS = ['Monday','Tuesday','Wednesday','Thursday','Friday','Saturday','Sunday']
MEAL_TYPES = ['breakfast','lunch','snack','dinner']
BL_PATTERN = '|'.join(re.escape(t) for t in FOOD_NAME_BLOCKLIST)
REQUIRED_FIELDS = ['food_id','food_name','meal_type','meal_role','serving',
                   'serving_weight','calories','protein','carbs','fat',
                   'budget_level','availability','swap_group','swap_options']

def check_plan(label, result):
    print(f"\n  --- {label} ---")
    plan = result.get('plan', {})
    targets = result.get('daily_targets', {})
    summary = result.get('weekly_summary', {})
    warnings = result.get('validation_warnings', [])

    ok(f"{label}: 7 days", len(plan) == 7, str(len(plan)), "7")
    ok(f"{label}: all day names", all(d in plan for d in DAYS), str(list(plan.keys())))

    # All meal types filled
    empty_slots = []
    for day in DAYS:
        for mt in MEAL_TYPES:
            items = plan.get(day,{}).get(mt,[])
            if not items:
                empty_slots.append(f"{day}/{mt}")
    ok(f"{label}: no empty meal slots", len(empty_slots)==0, str(empty_slots))

    # Required fields
    field_errors = []
    for day in DAYS:
        for mt in MEAL_TYPES:
            for item in plan.get(day,{}).get(mt,[]):
                for f in REQUIRED_FIELDS:
                    if f not in item:
                        field_errors.append(f"{day}/{mt}/{item.get('food_name','?')} missing '{f}'")
    ok(f"{label}: all required fields present", len(field_errors)==0, str(field_errors[:3]))

    # No blocklist foods
    blocked = []
    for day in DAYS:
        for mt in MEAL_TYPES:
            for item in plan.get(day,{}).get(mt,[]):
                if re.search(BL_PATTERN, item.get('food_name','').lower()):
                    blocked.append(item['food_name'])
    ok(f"{label}: no blocklist foods in plan", len(blocked)==0, str(blocked))

    # Calorie accuracy
    t_cal = targets.get('daily_calories', 0)
    avg_cal = summary.get('daily_average', {}).get('calories', 0)
    cal_err = abs(avg_cal - t_cal) / max(t_cal, 1)
    ok(f"{label}: calorie error <25%", cal_err < 0.25,
       f"err={cal_err:.1%}, target={t_cal}, avg={avg_cal}")

    # Meal roles: lunch should generally be heaviest
    lunch_cals = []
    dinner_cals = []
    for day in DAYS:
        lc = sum(i.get('calories',0) for i in plan.get(day,{}).get('lunch',[]))
        dc = sum(i.get('calories',0) for i in plan.get(day,{}).get('dinner',[]))
        lunch_cals.append(lc)
        dinner_cals.append(dc)
    avg_lunch = sum(lunch_cals)/len(lunch_cals)
    avg_dinner = sum(dinner_cals)/len(dinner_cals)
    warn(f"{label}: avg lunch >= avg dinner", avg_lunch >= avg_dinner,
         f"lunch={avg_lunch:.0f}, dinner={avg_dinner:.0f}")

    # Swap options
    no_swaps = []
    for day in DAYS:
        for mt in MEAL_TYPES:
            for item in plan.get(day,{}).get(mt,[]):
                if len(item.get('swap_options',[])) == 0:
                    no_swaps.append(item['food_name'])
    warn(f"{label}: all items have >=1 swap", len(no_swaps)==0,
         f"{len(no_swaps)} items have no swaps")

    # Breakfast uniqueness across 7 days
    bf_combos = [tuple(sorted(i['food_name'] for i in plan.get(d,{}).get('breakfast',[]))) for d in DAYS]
    n_unique = len(set(bf_combos))
    warn(f"{label}: >=5 unique breakfast combos", n_unique >= 5, f"only {n_unique}/7 unique")

    # Validation warnings count
    ok(f"{label}: validation warnings <5", len(warnings)<5,
       f"{len(warnings)} warnings: {warnings[:2]}")

    # Serving values are reasonable strings, not 'X unit unit'
    double_unit_errors = []
    for day in DAYS:
        for mt in MEAL_TYPES:
            for item in plan.get(day,{}).get(mt,[]):
                srv = item.get('serving','')
                for unit in ['cup','tbsp','tsp','bowl','scoop']:
                    if f'{unit} {unit}' in srv:
                        double_unit_errors.append(f"{item['food_name']}: '{srv}'")
    ok(f"{label}: no double-unit serving strings", len(double_unit_errors)==0, str(double_unit_errors[:3]))

    return result


# ── PLAN TESTS ───────────────────────────────────────────────────────────────
print("\n[B1] PLAN GENERATION - 3 KEY PROFILES")

profile_mg = {
    'email':'m@t.com', 'age':25, 'weight':70, 'height':175,
    'gender':'Male', 'goal':'Muscle Gain', 'dietary_preference':'nonveg',
    'allergies':[], 'activity_level':'Moderate',
}
profile_wl = {
    'email':'f@t.com', 'age':30, 'weight':60, 'height':165,
    'gender':'Female', 'goal':'Weight Loss', 'dietary_preference':'veg',
    'allergies':[], 'activity_level':'Light',
}
profile_vegan = {
    'email':'v@t.com', 'age':28, 'weight':65, 'height':170,
    'gender':'Male', 'goal':'Maintenance', 'dietary_preference':'vegan',
    'allergies':[], 'activity_level':'Active',
}

r_mg    = check_plan("Male/NonVeg/MuscleGain",  engine.generate_weekly_plan(profile_mg))
r_wl    = check_plan("Female/Veg/WeightLoss",   engine.generate_weekly_plan(profile_wl))
r_vegan = check_plan("Male/Vegan/Maintenance",  engine.generate_weekly_plan(profile_vegan))


# ── DETERMINISM ──────────────────────────────────────────────────────────────
print("\n[B2] DETERMINISM")

r1 = engine.generate_weekly_plan(profile_mg)
r2 = engine.generate_weekly_plan(profile_mg)
identical = all(
    [i['food_name'] for i in r1['plan'].get(d,{}).get(mt,[])] ==
    [i['food_name'] for i in r2['plan'].get(d,{}).get(mt,[])]
    for d in DAYS for mt in MEAL_TYPES
)
ok("Same profile = identical plan (determinism)", identical)

r3 = engine.generate_weekly_plan(profile_wl)
differs = r1['plan']['Monday']['breakfast'] != r3['plan']['Monday']['breakfast']
ok("Different profile = different plan", differs)

r_w0 = engine.generate_weekly_plan({**profile_mg, 'week_offset': 0})
r_w1 = engine.generate_weekly_plan({**profile_mg, 'week_offset': 1})
w0_bf = [i['food_name'] for i in r_w0['plan']['Monday'].get('breakfast',[])]
w1_bf = [i['food_name'] for i in r_w1['plan']['Monday'].get('breakfast',[])]
warn("week_offset=0 and week_offset=1 differ", w0_bf != w1_bf, f"w0={w0_bf}, w1={w1_bf}")


# ── SWAP TESTS ───────────────────────────────────────────────────────────────
print("\n[B3] SWAP ENGINE TESTS")

plan = r_mg['plan']
SWAP_FIELDS = ['food_id','food_name','serving','calories','protein','carbs','fat']

# Check all swap options have required keys
swap_field_errors = []
for day in DAYS[:3]:
    for mt in MEAL_TYPES:
        for item in plan.get(day,{}).get(mt,[]):
            for s in item.get('swap_options',[]):
                for k in SWAP_FIELDS:
                    if k not in s:
                        swap_field_errors.append(f"{item['food_name']} swap missing '{k}'")
ok("All swap options have required fields", len(swap_field_errors)==0, str(swap_field_errors[:3]))

# Swap food != original food
same_food_swaps = []
for day in DAYS[:3]:
    for mt in MEAL_TYPES:
        for item in plan.get(day,{}).get(mt,[]):
            for s in item.get('swap_options',[]):
                if s.get('food_name') == item.get('food_name'):
                    same_food_swaps.append(item['food_name'])
ok("Swap food is different from original", len(same_food_swaps)==0, str(same_food_swaps[:3]))

# Swap calories within ±40x of original (very loose to catch gross errors)
swap_cal_errors = []
for day in DAYS[:3]:
    for mt in MEAL_TYPES:
        for item in plan.get(day,{}).get(mt,[]):
            orig_cal = item.get('calories', 0)
            for s in item.get('swap_options',[]):
                sc = s.get('calories', 0)
                if orig_cal > 30 and sc > 0:
                    ratio = sc / orig_cal
                    if not (0.2 <= ratio <= 5.0):
                        swap_cal_errors.append(
                            f"{item['food_name']}({orig_cal}) -> {s['food_name']}({sc}) ratio={ratio:.2f}")
warn("Swap calorie ratio 0.2x-5.0x", len(swap_cal_errors)==0, str(swap_cal_errors[:3]))

# Public API: get_swap_options
pool = engine._apply_nutrition_rules(profile_mg)
food_name = pool.iloc[0]['food_name']
swaps_api = engine.get_swap_options(food_name, 'breakfast', profile_mg)
ok("get_swap_options returns list", isinstance(swaps_api, list))

swaps_unknown = engine.get_swap_options("SomeCompletelyUnknownFoodXYZ123", 'breakfast', profile_mg)
ok("get_swap_options unknown food returns []", swaps_unknown == [], str(swaps_unknown))


# ── ALLERGY PLAN TESTS (single plan each) ────────────────────────────────────
print("\n[B4] ALLERGY STRESS PLANS")

for allergy in ['egg', 'nuts', 'lactose', 'gluten']:
    r = engine.generate_weekly_plan({**profile_mg, 'allergies': [allergy]})
    items_flat = [i for d in DAYS for mt in MEAL_TYPES for i in r['plan'].get(d,{}).get(mt,[])]
    ok(f"Allergy '{allergy}': plan generated", len(items_flat) > 0)
    empty = [f"{d}/{mt}" for d in DAYS for mt in MEAL_TYPES if not r['plan'].get(d,{}).get(mt,[])]
    warn(f"Allergy '{allergy}': no empty slots", len(empty)==0, str(empty))

# Vegan + gluten (most restrictive)
r_vgf = engine.generate_weekly_plan({
    'email':'vgf@t.com', 'age':25, 'weight':60, 'height':165,
    'gender':'Female', 'goal':'Maintenance', 'dietary_preference':'vegan',
    'allergies':['gluten'], 'activity_level':'Moderate',
})
vgf_items = [i for d in DAYS for mt in MEAL_TYPES for i in r_vgf['plan'].get(d,{}).get(mt,[])]
ok("Vegan+Gluten: plan has items", len(vgf_items) > 0)
vgf_empty = [f"{d}/{mt}" for d in DAYS for mt in MEAL_TYPES if not r_vgf['plan'].get(d,{}).get(mt,[])]
warn("Vegan+Gluten: no empty slots", len(vgf_empty)==0, str(vgf_empty))


# ── EDGE CASES ───────────────────────────────────────────────────────────────
print("\n[B5] EDGE CASES")

# Null profile fields
try:
    r_null = engine.generate_weekly_plan({
        'email': None, 'age': None, 'weight': None, 'height': None,
        'gender': None, 'goal': None, 'dietary_preference': 'nonveg', 'allergies': None
    })
    ok("Null profile fields handled (7 days)", len(r_null.get('plan',{})) == 7,
       str(len(r_null.get('plan',{}))))
except Exception as e:
    ok("Null profile fields handled gracefully", False, str(e))

# Summary structure
summary = r_mg.get('weekly_summary', {})
ok("Summary: total_calories", 'total_calories' in summary)
ok("Summary: daily_average", 'daily_average' in summary)
ok("Summary: consistency_score", 'consistency_score' in summary)
ok("Summary: shopping_list", 'shopping_list' in summary)
ok("Summary: consistency 0-1", 0 <= summary.get('consistency_score',2) <= 1,
   str(summary.get('consistency_score')))
ok("Summary: daily_average has all macro keys",
   all(k in summary.get('daily_average',{}) for k in ['calories','protein_g','carbs_g','fat_g']))


# ── FINAL SUMMARY ─────────────────────────────────────────────────────────────
print()
print("=" * 60)
print(f"SECTION B RESULTS: {len(fails)} FAIL, {len(warns)} WARN")
if fails:
    print("FAILURES:")
    for f in fails: print(f"  - {f}")
if warns:
    print("WARNINGS:")
    for w in warns: print(f"  - {w}")
if not fails:
    print("ALL TESTS PASSED")
