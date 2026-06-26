"""
preprocess_food_metadata.py
===========================
One-time preprocessing script that enriches ingredient_database.json and
recipe_database.json with two new metadata fields:

    dish_family        — the cooking archetype (e.g. "biryani", "dal", "roti")
    primary_ingredient — the dominant protein/carb (e.g. "chicken", "paneer", "potato")

Usage
-----
    python scripts/preprocess_food_metadata.py [--dry-run] [--report]

Flags
-----
    --dry-run   Print what would be written but don't modify files.
    --report    After enrichment, print all entries still classified as "other"
                so they can be manually curated.

IMPORTANT
---------
This script is IDEMPOTENT. It never overwrites a field that already has a
non-"other" value. To manually override a classification, set the field in the
JSON directly and re-run — the script will leave it untouched.

After running this script, commit the enriched JSON files. The FoodGraph loader
reads these fields directly at startup — no runtime inference.
"""

import json
import pathlib
import sys
import argparse

# ── Path configuration ──────────────────────────────────────────────────────
ROOT = pathlib.Path(__file__).resolve().parent.parent
INGREDIENT_DB = ROOT / "data" / "ingredient_database.json"
RECIPE_DB     = ROOT / "data" / "recipe_database.json"

# ── Classification Maps ──────────────────────────────────────────────────────
# Each entry is (keyword, family). First match wins.
# Entries are ordered specific → generic to avoid early generic matches.
# Human curators can override any entry directly in the JSON files.

DISH_FAMILY_MAP = [
    # Specific rice dishes (must come before generic "rice")
    ("biryani",           "biryani"),
    ("fried rice",        "fried_rice"),
    ("jeera rice",        "plain_rice"),
    ("plain rice",        "plain_rice"),
    ("steamed rice",      "plain_rice"),
    ("steam rice",        "plain_rice"),
    ("white rice",        "plain_rice"),
    ("boiled rice",       "plain_rice"),
    ("uble chawal",       "plain_rice"),
    ("zeera pulao",       "pulao"),
    ("cumin pulao",       "pulao"),
    ("pulao",             "pulao"),
    ("khichdi",           "khichdi"),
    ("bisi bele",         "khichdi"),
    ("rice",              "rice"),
    # Flatbreads
    ("paratha",           "paratha"),
    ("naan",              "naan"),
    ("chapati",           "roti"),
    ("phulka",            "roti"),
    ("missi roti",        "roti"),
    ("jowar roti",        "roti"),
    ("roti",              "roti"),
    ("bread",             "bread"),
    ("toast",             "bread"),
    ("puri",              "puri"),
    ("bhatura",           "bhatura"),
    ("kulcha",            "kulcha"),
    ("luchi",             "puri"),
    # South Indian
    ("idli",              "idli"),
    ("dosa",              "dosa"),
    ("uttapam",           "uttapam"),
    ("upma",              "upma"),
    ("poha",              "poha"),
    ("pongal",            "pongal"),
    ("appam",             "appam"),
    ("adai",              "dosa"),
    ("koozh",             "porridge"),
    ("mudde",             "porridge"),
    ("avial",             "curry"),
    ("thoran",            "stir_fry"),
    ("poriyal",           "stir_fry"),
    ("foogath",           "stir_fry"),
    ("kosambari",         "salad"),
    ("sundal",            "salad"),
    # Lentils
    ("dal makhani",       "dal"),
    ("dal fry",           "dal"),
    ("dal tadka",         "dal"),
    ("masoor dal",        "dal"),
    ("moong dal",         "dal"),
    ("chana dal",         "dal"),
    ("toor dal",          "dal"),
    ("arhar dal",         "dal"),
    ("washed moong",      "dal"),
    ("dalma",             "dal"),
    ("kadhi",             "kadhi"),
    ("dal",               "dal"),
    ("sambar",            "sambar"),
    ("rasam",             "rasam"),
    # Grilled / Baked / Roasted
    ("grilled",           "grilled"),
    ("baked",             "baked"),
    ("roasted",           "roasted"),
    ("air fried",         "stir_fry"),
    ("air-fried",         "stir_fry"),
    # Kebabs & Tandoor
    ("kebab",             "kebab"),
    ("kabab",             "kebab"),
    ("tikka",             "kebab"),
    ("tandoori",          "kebab"),
    ("seekh",             "kebab"),
    ("boti",              "kebab"),
    # Curried dishes
    ("korma",             "korma"),
    ("chettinad",         "curry"),
    ("butter chicken",    "curry"),
    ("tikka masala",      "curry"),
    ("stew",              "stew"),
    ("jhol",              "curry"),
    ("moilee",            "curry"),
    ("doi maach",         "curry"),
    ("machher",           "curry"),
    ("manchurian",        "manchurian"),
    ("chilli ",           "manchurian"),
    ("curry",             "curry"),
    ("masala",            "curry"),
    ("gravy",             "curry"),
    # Dry / stir-fried veg
    ("sabzi",             "sabzi"),
    ("bhaji",             "sabzi"),
    ("bhartha",           "sabzi"),
    ("bharta",            "sabzi"),
    ("stir fry",          "stir_fry"),
    ("stir-fry",          "stir_fry"),
    ("bhurji",            "bhurji"),
    ("fry",               "fry"),
    # Sides / condiments
    ("raita",             "raita"),
    ("salad",             "salad"),
    ("soup",              "soup"),
    ("shorba",            "soup"),
    ("broth",             "soup"),
    ("stock",             "soup"),
    ("chutney",           "chutney"),
    ("pickle",            "pickle"),
    ("papad",             "papad"),
    ("chaas",             "buttermilk"),
    ("buttermilk",        "buttermilk"),
    ("canjee",            "porridge"),
    # Beverages
    ("smoothie",          "smoothie"),
    ("shake",             "shake"),
    ("lassi",             "lassi"),
    ("milkshake",         "shake"),
    ("aam panna",         "beverage"),
    ("drink",             "beverage"),
    ("juice",             "beverage"),
    ("tea",               "beverage"),
    ("coffee",            "beverage"),
    # Breakfast
    ("oats",              "oats"),
    ("muesli",            "oats"),
    ("granola",           "granola"),
    ("cornflakes",        "cereal"),
    ("cereal",            "cereal"),
    ("porridge",          "porridge"),
    ("pancake",           "pancake"),
    ("waffle",            "waffle"),
    ("chilla",            "chilla"),
    ("cheela",            "chilla"),
    ("sandwich",          "sandwich"),
    ("wrap",              "wrap"),
    ("roll",              "roll"),
    # Snacks / munchies
    ("chaat",             "chaat"),
    ("bhel",              "chaat"),
    ("pani puri",         "chaat"),
    ("dhokla",            "dhokla"),
    ("handvo",            "dhokla"),
    ("makhana",           "snack"),
    ("chiwda",            "snack"),
    ("chivda",            "snack"),
    ("murmura",           "snack"),
    ("groundnut",         "snack"),
    ("peanut",            "snack"),
    ("nut",               "snack"),
    ("seed",              "snack"),
    # Desserts
    ("halwa",             "dessert"),
    ("ladoo",             "dessert"),
    ("laddoo",            "dessert"),
    ("barfi",             "dessert"),
    ("burfi",             "dessert"),
    ("kheer",             "dessert"),
    ("pudding",           "dessert"),
    ("gateau",            "dessert"),
    ("cake",              "dessert"),
    ("mithai",            "dessert"),
    ("mittai",            "dessert"),
    ("kadalai",           "dessert"),
    ("frosting",          "dessert"),
    ("fool",              "dessert"),
    ("souffle",           "dessert"),
    # Eggs
    ("omelette",          "omelette"),
    ("scrambled",         "scrambled_egg"),
    ("boiled egg",        "boiled_egg"),
    ("fried egg",         "fried_egg"),
    ("egg nog",           "beverage"),
    ("egg",               "egg_dish"),
    # Spice blends / condiments (classify last to avoid false matches)
    ("spice blend",       "spice"),
    ("spice mix",         "spice"),
    ("panch phoran",      "spice"),
    ("paste",             "condiment"),
    ("puree",             "condiment"),
]

PRIMARY_INGREDIENT_MAP = [
    # Non-veg proteins (specific compounds first)
    ("butter chicken",    "chicken"),
    ("afghani chicken",   "chicken"),
    ("cajun chicken",     "chicken"),
    ("creamy chicken",    "chicken"),
    ("chicken manchurian","chicken"),
    ("chilli chicken",    "chicken"),
    ("broccoli chicken",  "chicken"),
    ("chicken",           "chicken"),
    ("mutton",            "mutton"),
    ("lamb",              "lamb"),
    ("basa",              "fish"),
    ("ilish",             "fish"),
    ("machher",           "fish"),
    ("meen",              "fish"),
    ("doi maach",         "fish"),
    ("maach",             "fish"),
    ("salmon",            "fish"),
    ("tuna",              "fish"),
    ("fish",              "fish"),
    ("prawn",             "shrimp"),
    ("shrimp",            "shrimp"),
    ("crab",              "crab"),
    ("egg nog",           "dairy"),
    ("egg",               "egg"),
    # Veg proteins
    ("chilli paneer",     "paneer"),
    ("paneer",            "paneer"),
    ("tofu",              "tofu"),
    ("soya chunk",        "soy"),
    ("soya bean",         "soy"),
    ("soy",               "soy"),
    ("black bean",        "black_bean"),
    ("black channa",      "chickpea"),
    ("chana",             "chickpea"),
    ("chickpea",          "chickpea"),
    ("chole",             "chickpea"),
    ("rajma",             "kidney_bean"),
    ("kidney bean",       "kidney_bean"),
    ("lobia",             "black_eyed_pea"),
    ("black eyed",        "black_eyed_pea"),
    ("black-eyed",        "black_eyed_pea"),
    ("moong",             "moong"),
    ("masoor",            "masoor"),
    ("toor",              "toor"),
    ("arhar",             "toor"),
    ("urad",              "urad"),
    ("peanut",            "peanut"),
    ("groundnut",         "peanut"),
    ("almond",            "almond"),
    ("makhana",           "makhana"),
    ("mushroom",          "mushroom"),
    # Grains / carb primaries
    ("bajra",             "bajra"),
    ("jowar",             "jowar"),
    ("ragi",              "ragi"),
    ("quinoa",            "quinoa"),
    ("millet",            "millet"),
    ("brown rice",        "brown_rice"),
    ("red rice",          "red_rice"),
    ("sweet potato",      "sweet_potato"),
    ("potato",            "potato"),
    ("aloo",              "potato"),
    ("baingan",           "brinjal"),
    ("brinjal",           "brinjal"),
    ("eggplant",          "brinjal"),
    ("palak",             "spinach"),
    ("spinach",           "spinach"),
    ("methi",             "fenugreek"),
    ("fenugreek",         "fenugreek"),
    ("cauliflower",       "cauliflower"),
    ("gobi",              "cauliflower"),
    ("broccoli",          "broccoli"),
    ("pumpkin",           "pumpkin"),
    ("bitter gourd",      "bitter_gourd"),
    ("karela",            "bitter_gourd"),
    ("bhindi",            "okra"),
    ("okra",              "okra"),
    ("lauki",             "bottle_gourd"),
    ("bottle gourd",      "bottle_gourd"),
    ("tori",              "ridge_gourd"),
    ("beetroot",          "beetroot"),
    ("carrot",            "carrot"),
    ("cabbage",           "cabbage"),
    ("beans",             "beans"),
    ("bamboo",            "bamboo"),
    ("pineapple",         "pineapple"),
    ("banana",            "banana"),
    ("mango",             "mango"),
    ("apple",             "apple"),
    ("apricot",           "apricot"),
    ("oat",               "oats"),
    ("wheat",             "wheat"),
    ("corn",              "corn"),
    ("maize",             "corn"),
    ("besan",             "chickpea_flour"),
    ("atta",              "wheat"),
    ("maida",             "wheat"),
    # Dairy
    ("yogurt",            "yogurt"),
    ("greek yogurt",      "yogurt"),
    ("curd",              "yogurt"),
    ("milk",              "milk"),
    ("cheese",            "cheese"),
    ("ghee",              "ghee"),
    ("butter",            "butter"),
    ("cream",             "cream"),
]


def classify(food_name: str) -> dict:
    """
    Returns dish_family and primary_ingredient for a food name.
    First-match wins on each map.
    """
    n = food_name.lower().strip()

    dish_family = "other"
    for keyword, family in DISH_FAMILY_MAP:
        if keyword in n:
            dish_family = family
            break

    primary_ingredient = "other"
    for keyword, ing in PRIMARY_INGREDIENT_MAP:
        if keyword in n:
            primary_ingredient = ing
            break

    return {"dish_family": dish_family, "primary_ingredient": primary_ingredient}


def enrich_database(db_path: pathlib.Path, dry_run: bool = False) -> dict:
    """
    Adds dish_family and primary_ingredient to every entry that doesn't
    already have a non-'other' value. Returns enrichment stats.
    """
    data = json.loads(db_path.read_text(encoding="utf-8"))

    stats = {
        "total": len(data),
        "newly_enriched": 0,
        "already_set": 0,
        "still_other_dish": [],
        "still_other_ingredient": [],
    }

    for fid, entry in data.items():
        name = entry.get("food_name", "")
        result = classify(name)

        # dish_family — only set if missing or "other"
        existing_df = entry.get("dish_family", "other")
        if not existing_df or existing_df == "other":
            entry["dish_family"] = result["dish_family"]
            if result["dish_family"] == "other":
                stats["still_other_dish"].append(name)
            else:
                stats["newly_enriched"] += 1
        else:
            stats["already_set"] += 1

        # primary_ingredient — only set if missing or "other"
        existing_pi = entry.get("primary_ingredient", "other")
        if not existing_pi or existing_pi == "other":
            entry["primary_ingredient"] = result["primary_ingredient"]
            if result["primary_ingredient"] == "other":
                stats["still_other_ingredient"].append(name)

    if not dry_run:
        db_path.write_text(
            json.dumps(data, indent=2, ensure_ascii=False),
            encoding="utf-8"
        )

    return stats


def print_report(db_name: str, stats: dict):
    total    = stats["total"]
    enriched = stats["newly_enriched"]
    manual   = stats["already_set"]
    unclassed_dish = stats["still_other_dish"]
    unclassed_ing  = stats["still_other_ingredient"]

    coverage = round(100 * (1 - len(unclassed_dish) / total), 1) if total else 0

    print(f"\n-- {db_name} ------------------------------------------")
    print(f"  Total entries   : {total}")
    print(f"  Newly enriched  : {enriched}")
    print(f"  Already set     : {manual}")
    print(f"  dish_family coverage : {coverage}%")
    print(f"  Needs manual dish_family ({len(unclassed_dish)} entries):")
    for name in sorted(unclassed_dish)[:30]:
        print(f"    - {name}")
    if len(unclassed_dish) > 30:
        print(f"    ... and {len(unclassed_dish)-30} more")

    print(f"  Needs manual primary_ingredient ({len(unclassed_ing)} entries):")
    for name in sorted(unclassed_ing)[:20]:
        print(f"    - {name}")
    if len(unclassed_ing) > 20:
        print(f"    ... and {len(unclassed_ing)-20} more")


def main():
    parser = argparse.ArgumentParser(
        description="Enrich food databases with dish_family and primary_ingredient."
    )
    parser.add_argument("--dry-run", action="store_true",
                        help="Preview changes without writing files.")
    parser.add_argument("--report", action="store_true",
                        help="Print unclassified entries after enrichment.")
    args = parser.parse_args()

    mode = "DRY RUN" if args.dry_run else "WRITE"
    print(f"\npreprocess_food_metadata.py — {mode} mode")
    print(f"Ingredient DB : {INGREDIENT_DB}")
    print(f"Recipe DB     : {RECIPE_DB}")

    ing_stats    = enrich_database(INGREDIENT_DB, dry_run=args.dry_run)
    recipe_stats = enrich_database(RECIPE_DB,     dry_run=args.dry_run)

    if args.report or True:   # always show report for visibility
        print_report("ingredient_database.json", ing_stats)
        print_report("recipe_database.json", recipe_stats)

    if args.dry_run:
        print("\n[DRY RUN] No files were modified.")
    else:
        print("\n[OK] Files updated. Commit ingredient_database.json and recipe_database.json.")
        print("  Review the 'Needs manual' lists above and set dish_family/primary_ingredient")
        print("  directly in the JSON for any entries still showing 'other'.")


if __name__ == "__main__":
    main()
