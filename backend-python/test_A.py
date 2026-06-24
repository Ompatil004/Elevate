"""Test section A: Init, format_serving, blocklist, diet filter, targets"""
import sys, io, os
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), 'app'))

from deterministic_meal_engine import MealEngine, _format_serving, FOOD_NAME_BLOCKLIST
import re

PASS = "[PASS]"
FAIL = "[FAIL]"
WARN = "[WARN]"

fails = []
warns = []

def ok(label, cond, got="", exp=""):
    if cond:
        print(f"  {PASS} {label}")
    else:
        print(f"  {FAIL} {label}")
        print(f"         got: {got!r}")
        print(f"         exp: {exp!r}")
        fails.append(label)

def warn(label, cond, got="", exp=""):
    if cond:
        print(f"  {PASS} {label}")
    else:
        print(f"  {WARN} {label}")
        print(f"         got: {got!r}")
        warns.append(label)

# ─── INIT ───
print("\n[A1] ENGINE INIT")
engine = MealEngine()
ok("Foods loaded > 1000", len(engine.df) > 1000, str(len(engine.df)))
ok("meal_role column", 'meal_role' in engine.df.columns)
ok("budget_level column", 'budget_level' in engine.df.columns)
ok("availability column", 'availability' in engine.df.columns)
ok("No condiment/side_dish in pool",
   not engine.df['meal_role'].isin(['condiment','side_dish']).any())
ok("portion_min <= portion_max",
   (engine.df['portion_min'] <= engine.df['portion_max']).all(),
   str((engine.df['portion_min'] > engine.df['portion_max']).sum()) + " violations")
ok("serving_quantity > 0",
   (engine.df['serving_quantity'] > 0).all(),
   str((engine.df['serving_quantity'] <= 0).sum()) + " violations")

# ─── FORMAT_SERVING ───
print("\n[A2] _format_serving BUG TEST")
tests_fmt = [
    (100.0, 'g',     '100g'),
    (250.0, 'ml',    '250ml'),
    (1.0,   'piece', '1 piece'),
    (2.0,   'piece', '2 pieces'),
    (1.5,   'cup',   '1.5 cup'),   # known bug: may produce '1.5 cup cup'
    (2.0,   'tbsp',  '2 tbsp'),    # known bug: may produce '2.0 tbsp tbsp'
    (1.0,   'cup',   '1 cup'),
    (0.5,   'tsp',   '0.5 tsp'),
]
for qty, unit, expected in tests_fmt:
    got = _format_serving(qty, unit)
    ok(f"format_serving({qty}, {unit!r}) = {expected!r}", got == expected, got, expected)

# ─── BLOCKLIST ───
print("\n[A3] BLOCKLIST")
bl_pattern = '|'.join(re.escape(t) for t in FOOD_NAME_BLOCKLIST)
for food in ['chicken stock', 'gum icing', 'black forest gateau', 'consomme au vermicelli', 'beef aspic']:
    ok(f"Blocklist: '{food}'", bool(re.search(bl_pattern, food.lower())))

for food in ['chicken tikka', 'dal makhani', 'paneer butter masala', 'grilled fish']:
    warn(f"Not blocked: '{food}'", not bool(re.search(bl_pattern, food.lower())))

# Verify no blocklist items in loaded pool
bl_in_pool = engine.df[engine.df['food_name'].str.lower().str.contains(bl_pattern, regex=True, na=False)]
ok(f"No blocklist foods in loaded pool (0 found)", len(bl_in_pool) == 0,
   str(len(bl_in_pool)) + " found: " + str(bl_in_pool['food_name'].tolist()[:5]))

# ─── DIET FILTERS ───
print("\n[A4] DIET FILTER TESTS")
base = {'email':'t@t.com','age':25,'weight':70,'height':175,
        'gender':'Male','goal':'Muscle Gain','dietary_preference':'nonveg','allergies':[]}

pool_veg    = engine._apply_nutrition_rules({**base, 'dietary_preference':'veg'})
pool_vegan  = engine._apply_nutrition_rules({**base, 'dietary_preference':'vegan'})
pool_nonveg = engine._apply_nutrition_rules({**base, 'dietary_preference':'nonveg'})

ok("Veg pool non-empty (>400)", len(pool_veg) > 400, str(len(pool_veg)))
ok("Vegan pool non-empty (>400)", len(pool_vegan) > 400, str(len(pool_vegan)))
ok("NonVeg pool largest",  len(pool_nonveg) >= len(pool_veg), f"nonveg={len(pool_nonveg)}, veg={len(pool_veg)}")

# Meat in veg pool check
meat_in_veg = pool_veg[pool_veg['allergens'].str.lower().str.contains(
    r'chicken|mutton|beef|pork|fish', na=False, regex=True)]
ok("Veg pool has 0 meat foods", len(meat_in_veg) == 0,
   f"{len(meat_in_veg)} meat foods: {meat_in_veg['food_name'].tolist()[:3]}")

# Dairy in vegan pool check
dairy_in_vegan = pool_vegan[pool_vegan['allergens'].str.lower().str.contains(
    r'milk|dairy|cheese|paneer|butter', na=False, regex=True)]
ok("Vegan pool has 0 dairy foods", len(dairy_in_vegan) == 0,
   f"{len(dairy_in_vegan)} dairy foods")

# Unknown diet raises ValueError
try:
    engine._apply_nutrition_rules({**base, 'dietary_preference':'jain'})
    ok("Jain diet raises ValueError", False, "no error raised")
except ValueError:
    ok("Jain diet raises ValueError", True)

# ─── ALLERGY FILTERS ───
print("\n[A5] ALLERGY FILTER TESTS")
allergy_cases = [
    ('egg',    r'\begg\b'),
    ('nuts',   r'almond|cashew|walnut|peanut'),
    ('gluten', r'wheat|maida|semolina|atta'),
    ('lactose',r'milk|paneer|cheese|butter'),
]
for allergy, pattern in allergy_cases:
    pool = engine._apply_nutrition_rules({**base, 'allergies': [allergy]})
    remaining = pool[pool['allergens'].str.lower().str.contains(pattern, na=False, regex=True)]
    ok(f"Allergy '{allergy}': 0 matches remain", len(remaining) == 0,
       f"{len(remaining)} foods still contain allergen")

pool_multi = engine._apply_nutrition_rules({**base, 'allergies': ['egg','nuts','lactose']})
ok("Multi-allergy pool non-empty (>50)", len(pool_multi) > 50, str(len(pool_multi)))

# ─── DAILY TARGETS ───
print("\n[A6] DAILY TARGETS")
t_male = engine.calculate_daily_targets({**base, 'goal':'Muscle Gain'})
t_female = engine.calculate_daily_targets({**base, 'gender':'Female','goal':'Weight Loss','activity_level':'Light'})

ok("Male MG kcal > 2000", t_male['daily_calories'] > 2000, str(t_male['daily_calories']))
ok("Male MG kcal < 5000", t_male['daily_calories'] < 5000, str(t_male['daily_calories']))
ok("Male MG protein > 100g", t_male['macro_targets_g']['protein_g'] > 100,
   str(t_male['macro_targets_g']['protein_g']))
ok("Female WL kcal < Male MG kcal",
   t_female['daily_calories'] < t_male['daily_calories'],
   f"female={t_female['daily_calories']}, male={t_male['daily_calories']}")
ok("Floor: kcal >= 1200", t_female['daily_calories'] >= 1200)
ok("Ceiling: edge weight=300 kcal <= 5000",
   engine.calculate_daily_targets({**base,'weight':300,'activity_level':'Very Active'})['daily_calories'] <= 5000)

# ─── SUMMARY ───
print()
print("=" * 60)
print(f"SECTION A RESULTS: {len(fails)} FAIL, {len(warns)} WARN")
if fails:
    print("FAILURES:")
    for f in fails:
        print(f"  - {f}")
if warns:
    print("WARNINGS:")
    for w in warns:
        print(f"  - {w}")
