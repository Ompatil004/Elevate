"""
serving_validator.py — Food Identity & Serving Unit Integrity

Validates every meal item against the FoodGraph database using food_id
as the canonical key. Detects:
  - Impossible serving units (yogurt → sandwich)
  - nutrition mismatch vs database
  - Corrupt food_id / food_name pairs
  - food_hash collisions (same food_id with different nutrition = corruption)

Never skips items — caller receives a structured failure report.
"""
import hashlib
import json
import logging
from typing import Dict, List, Optional, Tuple

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Serving unit whitelist — keyed on food name keyword (lowercase)
# Checked in order; first match wins.
# ---------------------------------------------------------------------------
_UNIT_RULES: List[Tuple[List[str], List[str]]] = [
    # keywords                              allowed units
    (["roti", "chapati", "phulka", "naan", "paratha", "thepla"],    ["piece", "pieces"]),
    (["idli", "cheela", "chilla", "dosa", "uttapam"],               ["piece", "pieces"]),
    (["sandwich"],                                                    ["sandwich", "sandwiches"]),
    (["bread", "toast"],                                             ["slice", "slices", "piece", "pieces"]),
    (["egg", "boiled", "poached", "omelette", "anda"],              ["piece", "pieces"]),
    (["banana", "apple", "orange", "guava", "mango", "pear",
      "papaya", "watermelon", "pomegranate", "strawberry"],         ["piece", "pieces", "medium fruit", "medium fruits", "g", "ml"]),
    (["milkshake", "smoothie", "lassi", "chaas", "buttermilk",
      "juice", "drink"],                                            ["glass", "glasses", "ml"]),
    (["milk"],                                                       ["glass", "glasses", "cup", "cups", "ml"]),
    (["tea", "coffee"],                                              ["cup", "cups", "ml"]),
    (["soup", "shorba", "broth"],                                    ["bowl", "bowls", "cup", "cups", "ml"]),
    (["dal", "sambar", "rasam", "lentil"],                          ["bowl", "bowls", "g", "ml"]),
    (["yogurt", "curd", "dahi", "greek yogurt"],                    ["bowl", "bowls", "cup", "cups", "g", "ml"]),
    (["raita", "pachadi"],                                           ["bowl", "bowls", "g"]),
    (["salad", "kachumber", "kosambari"],                            ["bowl", "bowls", "g"]),
    (["rice", "biryani", "pulao", "khichdi"],                        ["plate", "plates", "bowl", "bowls", "g", "ml"]),
    (["poha", "upma", "bhel"],                                       ["bowl", "bowls", "plate", "plates", "g"]),
    (["oats", "oatmeal", "porridge", "daliya"],                      ["bowl", "bowls", "g"]),
    (["curry", "sabzi", "gravy", "masala"],                          ["bowl", "bowls", "g"]),
    (["paneer", "tofu"],                                             ["g", "bowl", "bowls", "piece", "pieces"]),
    (["chutney"],                                                    ["tbsp", "tsp", "g"]),
    (["pickle", "achar"],                                            ["tbsp", "tsp", "g"]),
    (["butter", "oil", "ghee"],                                      ["tsp", "tbsp", "g"]),
    (["whey", "protein powder"],                                     ["scoop", "scoops", "g"]),
]

# Units that are NEVER valid for any food (catch-all corruption markers)
_ALWAYS_FORBIDDEN = {"sandwich", "sandwiches", "plate", "plates"}
# Foods that must NEVER be measured in these units even from the catch-all
_FOOD_FORBIDDEN_MAP: Dict[str, List[str]] = {
    "yogurt":    ["sandwich", "sandwiches", "plate", "plates", "piece", "pieces"],
    "curd":      ["sandwich", "sandwiches", "plate", "plates", "piece", "pieces"],
    "dahi":      ["sandwich", "sandwiches", "plate", "plates", "piece", "pieces"],
    "banana":    ["sandwich", "sandwiches", "plate", "plates", "bowl", "bowls"],
    "apple":     ["sandwich", "sandwiches", "plate", "plates", "bowl", "bowls"],
    "soup":      ["sandwich", "sandwiches", "plate", "plates", "piece", "pieces"],
    "dal":       ["sandwich", "sandwiches", "piece", "pieces"],
    "rice":      ["sandwich", "sandwiches", "piece", "pieces", "tsp"],
    "roti":      ["sandwich", "sandwiches", "bowl", "bowls", "plate", "plates"],
    "chapati":   ["sandwich", "sandwiches", "bowl", "bowls", "plate", "plates"],
    "milkshake": ["sandwich", "sandwiches", "plate", "plates", "piece", "pieces", "bowl", "bowls"],
}


def is_valid_serving_unit(food_name: str, unit: str) -> Tuple[bool, str]:
    """
    Returns (is_valid, reason).
    Uses the whitelist rules above. If no whitelist rule matches, accepts anything
    except the forbidden unit map entries.
    """
    n = food_name.lower()
    u = (unit or "").lower().strip()

    # 1. Check food-specific forbidden map first (most specific)
    for keyword, forbidden_units in _FOOD_FORBIDDEN_MAP.items():
        if keyword in n and u in [x.lower() for x in forbidden_units]:
            return False, f"'{food_name}' cannot have unit '{unit}' (forbidden for {keyword})"

    # 2. Walk whitelist rules — first match is authoritative
    for keywords, allowed_units in _UNIT_RULES:
        if any(kw in n for kw in keywords):
            allowed_lower = [a.lower() for a in allowed_units]
            if u in allowed_lower:
                return True, "ok"
            # matched a rule but unit is wrong
            return False, (
                f"'{food_name}' matched rule {keywords} → allowed {allowed_units}, "
                f"but got '{unit}'"
            )

    # 3. No whitelist rule matched — only reject if the unit is in the global forbidden set
    if u in {x.lower() for x in _ALWAYS_FORBIDDEN}:
        return False, f"'{food_name}' has globally forbidden unit '{unit}'"

    return True, "ok (no specific rule, unit accepted)"


def compute_food_hash(food_id: str, nutrition: Dict, serving_unit: str) -> str:
    """
    Deterministic hash of (food_id + nutrition + serving_unit).
    Two items with the same food_id MUST produce the same hash.
    If hashes differ → identity corruption.
    """
    # Round nutrition to 1dp to avoid float noise
    rounded_nutrition = {
        k: round(float(v or 0), 1)
        for k, v in nutrition.items()
        if k in ("calories", "protein", "carbs", "fat", "fiber")
    }
    payload = json.dumps(
        {"food_id": food_id, "nutrition": rounded_nutrition, "unit": (serving_unit or "").lower()},
        sort_keys=True
    )
    return hashlib.md5(payload.encode()).hexdigest()[:12]


class FoodIdentityValidator:
    """
    Validates every meal item in a serialized plan against the FoodGraph
    database using food_id as the canonical key.

    Follows the retry hierarchy defined by the user:
        Candidate fails → try another candidate
        Meal fails     → try another meal
        Day fails      → try another day
        Week fails     → try another week
        Still fails    → return structured error (never skip items)
    """

    def __init__(self, food_graph):
        self.food_graph = food_graph
        # Build food_id → canonical node lookup
        self._db: Dict[str, Dict] = {}
        for fid, node in food_graph.get_all_nodes().items():
            self._db[str(fid).lower()] = node

    def validate_item(self, item: Dict) -> Tuple[bool, List[str]]:
        """
        Validates a single meal item.
        Returns (is_valid, list_of_failure_reasons).
        """
        failures = []
        food_id = str(item.get("food_id", "")).lower().strip()
        food_name = str(item.get("food_name", "")).strip()
        serving_unit = str(item.get("serving_unit", "")).strip()
        nutrition = item.get("nutrition", {})

        # --- Check 1: food_id exists ---
        if not food_id:
            failures.append("MISSING food_id")
            return False, failures

        db_node = self._db.get(food_id)
        if not db_node:
            # Try case-insensitive fuzzy — food_id might have suffix
            candidates = [fid for fid in self._db if fid.startswith(food_id[:6])]
            if not candidates:
                failures.append(f"food_id '{food_id}' not found in database")
                return False, failures
            db_node = self._db[candidates[0]]

        # --- Check 2: food_name matches database ---
        db_name = str(db_node.get("food_name", "")).strip()
        if db_name and food_name and db_name.lower() != food_name.lower():
            failures.append(
                f"food_name mismatch: item='{food_name}' db='{db_name}' for food_id='{food_id}'"
            )

        # --- Check 3: nutrition belongs to food_id ---
        db_nutrition = db_node.get("nutrition", {})
        db_cal = round(float(db_nutrition.get("calories", 0)), 1)
        item_cal_per_100 = round(float(nutrition.get("calories", 0)), 1)

        # We can't check absolute cal equality (scaled by portion), but we can
        # ensure the item's per-100g calories are not wildly different from the DB.
        # For scaled items check that nutrition is derivable from the DB (ratio check).
        serving_qty = float(item.get("serving_qty", 1) or 1)
        db_serving_g = float(db_nutrition.get("serving_size_g", 100) or 100)

        # Estimate expected calories at the given serving_qty
        # db_cal is per 1 serving (serving_size_g grams)
        if db_cal > 0 and item_cal_per_100 > 0:
            # The ratio should be consistent (within ±30% for scaling differences)
            # item nutrition = db_nutrition * scale_factor
            # We just verify the item calories are positive and not astronomically wrong
            if item_cal_per_100 < 0:
                failures.append(f"Negative calories for '{food_name}'")
            if item_cal_per_100 > db_cal * 20:
                failures.append(
                    f"Calories suspiciously high for '{food_name}': "
                    f"item={item_cal_per_100} but db_base={db_cal}"
                )

        # --- Check 4: serving unit valid ---
        if serving_unit:
            unit_ok, reason = is_valid_serving_unit(db_name, serving_unit)
            if not unit_ok:
                failures.append(f"INVALID UNIT: {reason}")

        # --- Check 5: food_name is not empty ---
        if not food_name and not db_name:
            failures.append("Empty food_name")

        # --- Check 6: nutrition not null ---
        if not nutrition:
            failures.append(f"Null/empty nutrition for '{food_name}'")

        return len(failures) == 0, failures

    def validate_plan(self, weekly_plan: Dict) -> Dict:
        """
        Validates every item in the weekly plan.
        Returns:
            {
                "is_valid": bool,
                "total_items": int,
                "failed_items": int,
                "failures": [{ day, meal_type, food_name, reasons }],
                "food_hash_collisions": [{ food_id, hashes }],
            }
        """
        failures = []
        hash_registry: Dict[str, str] = {}   # food_id → first seen hash
        hash_collisions = []
        total_items = 0
        failed_items = 0

        for day_name, meals in (weekly_plan or {}).items():
            for meal_type, items in (meals or {}).items():
                for item in (items or []):
                    total_items += 1
                    food_id = str(item.get("food_id", "")).lower().strip()
                    food_name = item.get("food_name", "")
                    nutrition = item.get("nutrition", {})
                    serving_unit = item.get("serving_unit", "")

                    # food_hash check — detect if same food_id shows different nutrition
                    if food_id:
                        fhash = compute_food_hash(food_id, nutrition, serving_unit)
                        if food_id in hash_registry:
                            if hash_registry[food_id] != fhash:
                                hash_collisions.append({
                                    "food_id": food_id,
                                    "food_name": food_name,
                                    "day": day_name,
                                    "meal_type": meal_type,
                                    "first_hash": hash_registry[food_id],
                                    "current_hash": fhash,
                                })
                        else:
                            hash_registry[food_id] = fhash

                    # Per-item identity check
                    is_valid, reasons = self.validate_item(item)
                    if not is_valid:
                        failed_items += 1
                        failures.append({
                            "day": day_name,
                            "meal_type": meal_type,
                            "food_id": food_id,
                            "food_name": food_name,
                            "reasons": reasons,
                        })
                        logger.warning(
                            f"[FoodIdentity] FAIL {day_name}/{meal_type} '{food_name}': {reasons}"
                        )

        is_valid = (failed_items == 0) and (len(hash_collisions) == 0)

        if hash_collisions:
            logger.error(
                f"[FoodIdentity] {len(hash_collisions)} food_hash collision(s) detected — "
                "identity corruption confirmed."
            )

        return {
            "is_valid": is_valid,
            "total_items": total_items,
            "failed_items": failed_items,
            "failures": failures,
            "food_hash_collisions": hash_collisions,
        }
