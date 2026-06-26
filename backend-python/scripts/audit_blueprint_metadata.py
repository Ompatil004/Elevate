"""Read-only audit of meal-blueprint food metadata (Task 7).

For every food name listed in ``data/meal_blueprint_library.json`` this script
resolves the food through the SAME fuzzy-matching path used at runtime
(``CandidateGenerator._fuzzy_match_food``) and reports:

  * foods that do not resolve to any FoodGraph node, and
  * resolved foods whose semantics are missing ``dish_family``, ``category`` or
    ``cuisine``.

It does NOT modify any data or assign placeholder values — it only reports, so a
human can decide whether to fix the dataset / preprocessing step.

Note: ``meal_role`` is intentionally NOT audited here because it is synthesized at
load time in ``food_graph.py`` and is therefore always present at runtime.

Usage:
    python scripts/audit_blueprint_metadata.py
Run from the ``backend-python`` directory (so relative data paths resolve).
"""
import json
import os
import sys

# Allow "import app.*" when run from backend-python/
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.nutrition_engine.engine import NutritionEngineV6  # noqa: E402

REQUIRED_FIELDS = ("dish_family", "category", "cuisine")


def main() -> int:
    blueprint_path = os.path.join("data", "meal_blueprint_library.json")
    with open(blueprint_path, "r", encoding="utf-8") as fh:
        blueprints = json.load(fh)
    if isinstance(blueprints, dict):
        blueprints = list(blueprints.values())

    engine = NutritionEngineV6()
    cg = engine.candidate_generator

    unresolved = []          # (meal_id, food_name)
    missing_meta = []        # (meal_id, food_name, [missing fields])
    seen_foods = set()
    total_food_refs = 0

    for meal in blueprints:
        meal_id = meal.get("meal_id", meal.get("meal_name", "?"))
        for food_name in meal.get("foods", []):
            total_food_refs += 1
            node = cg._fuzzy_match_food(food_name)
            if not node:
                unresolved.append((meal_id, food_name))
                continue
            sem = node.get("semantics", {})
            gaps = [f for f in REQUIRED_FIELDS if not sem.get(f)]
            if gaps:
                key = (node.get("food_name", food_name), tuple(gaps))
                if key not in seen_foods:
                    seen_foods.add(key)
                    missing_meta.append((meal_id, food_name, gaps))

    print("=" * 70)
    print("BLUEPRINT METADATA AUDIT")
    print("=" * 70)
    print(f"Blueprints scanned     : {len(blueprints)}")
    print(f"Total food references  : {total_food_refs}")
    print(f"Unresolved foods       : {len(unresolved)}")
    print(f"Foods missing metadata : {len(missing_meta)}")
    print()

    if unresolved:
        print("--- UNRESOLVED (fuzzy match returned no node) ---")
        for meal_id, food_name in unresolved:
            print(f"  [{meal_id}] {food_name!r}")
        print()

    if missing_meta:
        print("--- RESOLVED BUT MISSING dish_family / category / cuisine ---")
        for meal_id, food_name, gaps in missing_meta:
            print(f"  [{meal_id}] {food_name!r} -> missing {', '.join(gaps)}")
        print()

    if not unresolved and not missing_meta:
        print("All blueprint foods resolve and carry complete metadata. ✅")

    # Non-zero exit if problems found, so CI can flag it. Report-only otherwise.
    return 1 if (unresolved or missing_meta) else 0


if __name__ == "__main__":
    raise SystemExit(main())
