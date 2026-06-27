import json
import logging
import types
import pandas as pd
from typing import Dict, List, Optional, Any
from app.nutrition_engine.config import NUTRITION_RULES
from app.nutrition_engine.food_utils import get_primary_unit

logger = logging.getLogger(__name__)

# Required fields that every node MUST have after loading.
# Missing any of these causes a startup failure — do NOT silently continue.
_REQUIRED_NODE_FIELDS = ("food_id", "food_name", "nutrition")
_REQUIRED_NUTRITION_FIELDS = ("calories", "protein", "carbs", "fat")


def _freeze(obj):
    """
    Recursively freeze a dict/list so it becomes immutable.
    dicts  → types.MappingProxyType
    lists  → tuple
    other  → unchanged
    """
    if isinstance(obj, dict):
        return types.MappingProxyType({k: _freeze(v) for k, v in obj.items()})
    if isinstance(obj, list):
        return tuple(_freeze(v) for v in obj)
    return obj


def _map_category_to_meal_role(category: str) -> str:
    """Map broad food categories to specific compatibility matrix meal roles."""
    if not category:
        return ""
    cat_lower = category.lower()
    
    if cat_lower in ["chicken/meat", "fish/seafood", "eggs", "paneer"]:
        return "protein_main"
    elif cat_lower in ["dal & pulses", "soup", "traditional meal"]:
        return "curry"
    elif cat_lower in ["rice", "millets & whole grains", "whole grains", "breakfast"]:
        return "carb_base"
    elif cat_lower in ["dairy", "healthy beverage"]:
        return "dairy_side"
    elif cat_lower in ["salad", "fruits"]:
        return "salad"
    elif cat_lower in ["vegetables", "leafy greens"]:
        return "veg_side"
        
    return ""


def _build_cuisine_keyword_map() -> dict:
    """
    Builds a {cuisine: [keyword, ...]} lookup from nutrition_rules.yaml.
    Called once at module load — no hardcoded keywords in Python.
    Returns an ordered list of (cuisine, keywords) tuples so that more-specific
    cuisines (longer keyword lists defined first in YAML) win over generic ones.
    """
    kw_map = NUTRITION_RULES.get("cuisine_keyword_map", {})
    # Preserve YAML ordering (most-specific first)
    return {cuisine: [str(k).lower() for k in kws] for cuisine, kws in kw_map.items()}

_CUISINE_KEYWORD_MAP = _build_cuisine_keyword_map()
_DATASET_REGION_MAP  = NUTRITION_RULES.get("dataset_region_to_cuisine", {})


def _detect_cuisine_by_keywords(food_name: str) -> Optional[str]:
    """
    Config-driven cuisine detection from cuisine_keyword_map in nutrition_rules.yaml.
    Returns the first matching cuisine, or None.
    Never falls back silently — callers must handle None.
    """
    name_lower = food_name.lower()
    for cuisine, keywords in _CUISINE_KEYWORD_MAP.items():
        if any(kw in name_lower for kw in keywords):
            return cuisine
    return None


def normalize_cuisine_name(name: str) -> str:
    if not name:
        return "Pan Indian"
    nl = name.lower().strip()
    if "maharashtra" in nl or "maharashtrian" in nl:
        return "Maharashtrian"
    if "gujarat" in nl or "gujarati" in nl:
        return "Gujarati"
    if "bengal" in nl or "bengali" in nl:
        return "Bengali"
    if "north east" in nl or "northeast" in nl:
        return "North East Indian"
    if "north indian" in nl or "north india" in nl:
        return "North Indian"
    if "south indian" in nl or "south india" in nl:
        return "South Indian"
    if "west indian" in nl or "west india" in nl:
        return "West Indian"
    if "east indian" in nl or "east india" in nl:
        return "East Indian"
    if "pan indian" in nl or "pan_indian" in nl or "all india" in nl or "all_india" in nl:
        return "Pan Indian"
    return name.title().strip()


def _csv_region_to_cuisine(region: str) -> str:
    """
    Converts a CSV `region` value to a cuisine string using the config map.
    Falls back to 'Pan Indian' for any unrecognised value.
    """
    if not region or str(region).strip().lower() in ('', 'nan', 'none'):
        return None
    res = _DATASET_REGION_MAP.get(str(region).strip(), None)
    return normalize_cuisine_name(res) if res else None


class FoodGraph:
    """
    3-Layer Knowledge Graph Loader.
    Loads nutrition CSV, metadata JSON, and relationship JSON.

    IMMUTABILITY GUARANTEE:
        After _load_layers() completes, every node in self._nodes is frozen
        (types.MappingProxyType). No downstream code may modify nodes in-place.
        CandidateGenerator and all other callers MUST deepcopy before mutating.
    """
    def __init__(self, ingredient_db_path: str, recipe_db_path: str, relationship_path: str, nutrition_csv_path: str):
        self.ingredient_db_path = ingredient_db_path
        self.recipe_db_path = recipe_db_path
        self.relationship_path = relationship_path
        self.nutrition_csv_path = nutrition_csv_path
        
        self._nodes: Dict[str, Any] = {}   # frozen MappingProxyType values
        self._ingredients: Dict[str, Any] = {}
        self._recipes: Dict[str, Any] = {}
        self._load_layers()

    def _load_layers(self):
        try:
            self._calorie_inconsistency_count = 0
            # 1. Load Ingredients
            with open(self.ingredient_db_path, 'r', encoding='utf-8') as f:
                self._ingredients = json.load(f)
                
            # 2. Load Recipes
            with open(self.recipe_db_path, 'r', encoding='utf-8') as f:
                self._recipes = json.load(f)
                
            # 3. Load Relationships (optional, fallback to empty if missing)
            relationships = {}
            if self.relationship_path:
                try:
                    with open(self.relationship_path, 'r', encoding='utf-8') as f:
                        relationships = json.load(f)
                except FileNotFoundError:
                    logger.warning(f"Relationship file not found at {self.relationship_path}. Proceeding without it.")
                
            # 4. Load Nutrition
            nutrition_df = pd.read_csv(self.nutrition_csv_path)
            
            # Combine meta
            all_meta = {**self._ingredients, **self._recipes}
            
            # Check for is_recommended flag in any metadata
            has_recommended_flag = False
            for fid, meta in all_meta.items():
                if "is_recommended" in meta or ("metadata" in meta and isinstance(meta["metadata"], dict) and "is_recommended" in meta["metadata"]):
                    has_recommended_flag = True
                    break
            
            if not has_recommended_flag:
                logger.warning(
                    "\nDATASET_WARNING\n"
                    "  Recommendation flag not found.\n"
                    "  All foods treated as eligible."
                )
                
            # Merge into a single node dictionary
            raw_nodes: Dict[str, dict] = {}
            for idx, row in nutrition_df.iterrows():
                fid = str(row['food_id'])
                if fid not in all_meta:
                    continue
                    
                meta = all_meta[fid]
                rel = relationships.get(fid, {})
                
                # Sanitize is_vegan and is_vegetarian against incorrect database entries
                food_name_lower = meta.get("food_name", row['food_name']).lower()
                is_vegan = bool(meta.get("is_vegan", False))
                is_vegetarian = bool(meta.get("is_vegetarian", False))
                
                non_veg_keywords = ['chicken', 'mutton', 'fish', 'prawn', 'shrimp', 'crab', 'lamb', 'beef', 'pork', 'salmon', 'tuna', 'basa', 'ilish', 'machher', 'meen', 'maach']
                egg_keywords = ['egg', 'omelette', 'omelet']
                
                allergens_val = str(row.get('allergens', '')).lower().strip()
                has_non_veg = any(kw in food_name_lower for kw in non_veg_keywords) or any(kw in allergens_val for kw in non_veg_keywords)
                has_egg = (any(kw in food_name_lower for kw in egg_keywords) or any(kw in allergens_val for kw in ['egg', 'eggs'])) and not ('eggless' in food_name_lower or 'mock' in food_name_lower or 'vegan' in food_name_lower)
                
                if has_non_veg or has_egg:
                    is_vegan = False
                    is_vegetarian = False
                elif 'paneer' in food_name_lower or 'curd' in food_name_lower or 'milk' in food_name_lower or 'yogurt' in food_name_lower or 'cheese' in food_name_lower or 'butter' in food_name_lower or 'ghee' in food_name_lower or 'raita' in food_name_lower:
                    is_vegan = False
                
                # Fetch baseline database nutrients
                listed_calories = float(row.get('calories_kcal', 0))
                protein = float(row.get('protein_g', 0))
                carbs = float(row.get('carbohydrates_g', 0))
                fat = float(row.get('fat_g', 0))
                fiber = float(row.get('fiber_g', 0))
                db_serving_g = float(row.get('serving_size_g', 100))
                if db_serving_g <= 0:
                    db_serving_g = 100.0
                
                # Logical Portion Normalization & Serving Limits (Phase 3, 4, 5, 8)
                is_standard = False
                target_unit = None
                target_serving_g = None
                p_min, p_max, p_step, p_pref = None, None, None, None
                
                if "thepla" in food_name_lower:
                    is_standard = True
                    target_unit = "piece"
                    target_serving_g = 40.0
                    p_min, p_max, p_step, p_pref = 1.0, 4.0, 1.0, 2.0
                elif "paratha" in food_name_lower:
                    is_standard = True
                    target_unit = "piece"
                    target_serving_g = 60.0
                    p_min, p_max, p_step, p_pref = 1.0, 3.0, 1.0, 1.0
                elif any(kw in food_name_lower for kw in ["jowar", "bajra", "makki", "multigrain", "soya", "bhakri"]) and any(r in food_name_lower for r in ["roti", "chapati", "bhakri"]):
                    is_standard = True
                    target_unit = "piece"
                    target_serving_g = 50.0
                    p_min, p_max, p_step, p_pref = 1.0, 3.0, 1.0, 1.0
                elif any(kw in food_name_lower for kw in ["chapati", "roti", "phulka"]):
                    is_standard = True
                    target_unit = "piece"
                    target_serving_g = 40.0
                    listed_calories = 110.0
                    protein = 3.5
                    carbs = 22.0
                    fat = 1.5
                    fiber = 2.0
                    p_min, p_max, p_step, p_pref = 1.0, 4.0, 1.0, 2.0
                elif any(kw in food_name_lower for kw in ["dal", "sambar", "kadhi", "rasam"]) or meta.get("category") == "Dal & Pulses":
                    is_standard = True
                    target_unit = "bowl"
                    target_serving_g = 150.0
                    p_min, p_max, p_step, p_pref = 1.0, 2.0, 0.5, 1.0
                elif any(kw in food_name_lower for kw in ["rice", "pulao", "biryani", "khichdi"]):
                    is_standard = True
                    target_unit = "plate"
                    target_serving_g = 150.0
                    p_min, p_max, p_step, p_pref = 0.5, 2.0, 0.5, 1.0
                elif any(kw in food_name_lower for kw in ["yogurt", "curd", "dahi"]):
                    is_standard = True
                    target_unit = "bowl"
                    target_serving_g = 150.0
                    p_min, p_max, p_step, p_pref = 0.5, 2.0, 0.5, 1.0
                elif any(kw in food_name_lower for kw in ["salad", "kachumber", "kosambari"]):
                    is_standard = True
                    target_unit = "bowl"
                    target_serving_g = 100.0
                    p_min, p_max, p_step, p_pref = 0.5, 1.0, 0.5, 1.0
                elif any(kw in food_name_lower for kw in ["soup", "shorba"]):
                    is_standard = True
                    target_unit = "bowl"
                    target_serving_g = 200.0
                    p_min, p_max, p_step, p_pref = 1.0, 2.0, 0.5, 1.0
                elif any(kw in food_name_lower for kw in ["chutney", "pickle", "achar", "chutny"]):
                    is_standard = True
                    target_unit = "tbsp"
                    target_serving_g = 15.0
                    p_min, p_max, p_step, p_pref = 0.5, 2.0, 0.5, 1.0
                elif (
                    "egg" in food_name_lower
                    and not any(kw in food_name_lower for kw in [
                        "curry", "bhurji", "salad", "omelette", "omelet",
                        "sandwich", "baked", "nog", "eggplant", "noodle",
                        "white", "pepper", "sauce", "fried rice", "pulao"
                    ])
                ):
                    # Plain boiled/poached egg — enforce per-egg serving bounds
                    # without overriding macros (those come correctly from CSV).
                    is_standard = True
                    target_unit = "piece"
                    target_serving_g = db_serving_g   # keep as-is, just set bounds
                    p_min, p_max, p_step, p_pref = 1.0, 4.0, 1.0, 2.0

                # Perform macro scaling for standard items
                if is_standard:
                    is_wheat_roti = any(kw in food_name_lower for kw in ["chapati", "roti", "phulka"]) and not any(kw in food_name_lower for kw in ["jowar", "bajra", "makki", "multigrain", "soya", "bhakri"])
                    if not is_wheat_roti:
                        scale = target_serving_g / db_serving_g
                        listed_calories *= scale
                        protein *= scale
                        carbs *= scale
                        fat *= scale
                        fiber *= scale
                    db_serving_g = target_serving_g
                    meta["serving_unit"] = target_unit
                
                # Calorie validation and correction logic (Phase 2)
                calculated_calories = protein * 4.0 + carbs * 4.0 + fat * 9.0
                val_cfg = NUTRITION_RULES.get("calorie_validation", {})
                if val_cfg.get("enabled", True):
                    tolerance = float(val_cfg.get("tolerance_pct", val_cfg.get("tolerance_percent", 20.0)))
                    policy = val_cfg.get("correction_policy", val_cfg.get("policy", "log_only"))
                    
                    diff = abs(listed_calories - calculated_calories)
                    denom = listed_calories if listed_calories > 0 else 1.0
                    diff_percent = (diff / denom) * 100.0
                    
                    if diff_percent > tolerance:
                        self._calorie_inconsistency_count += 1
                        logger.warning(
                            f"\nCALORIE_VALIDATION_WARNING\n"
                            f"  food_name:         {row['food_name']}\n"
                            f"  listed_calories:   {listed_calories}\n"
                            f"  calculated_calories: {calculated_calories}\n"
                            f"  difference_pct:    {diff_percent:.2f}%\n"
                        )
                        if policy == "auto_correct":
                            listed_calories = calculated_calories
                
                node_metadata = meta.get("metadata", {})
                if not isinstance(node_metadata, dict):
                    node_metadata = {}
                node_metadata = dict(node_metadata)
                
                is_rec = True
                if "is_recommended" in meta:
                    is_rec = bool(meta["is_recommended"])
                elif "is_recommended" in node_metadata:
                    is_rec = bool(node_metadata["is_recommended"])
                node_metadata["is_recommended"] = is_rec
                
                # Inject standard serving limits
                if p_min is not None:
                    node_metadata["minimum_serving"] = p_min
                if p_max is not None:
                    node_metadata["maximum_serving"] = p_max
                if p_step is not None:
                    node_metadata["serving_step"] = p_step
                if p_pref is not None:
                    node_metadata["preferred_serving"] = p_pref
                
                # ── Nutrition Validation (config-driven, Part 5) ──────────────
                nv_cfg = NUTRITION_RULES.get("nutrition_validation", {})
                reject_if = nv_cfg.get("reject_if", {})
                zero_cal_allowed_kws = [str(x).lower() for x in nv_cfg.get("zero_cal_allowed", [
                    "water", "black coffee", "plain tea", "green tea", "herbal tea"
                ])]
                is_allowed_zero = any(x in food_name_lower for x in zero_cal_allowed_kws)

                cal_lte = float(reject_if.get("calories_lte", 0))
                pro_lt  = float(reject_if.get("protein_lt",   0))
                car_lt  = float(reject_if.get("carbs_lt",     0))
                fat_lt  = float(reject_if.get("fat_lt",       0))

                _is_zero_nutrition = (
                    listed_calories <= cal_lte
                    and protein <= pro_lt
                    and carbs <= car_lt
                    and fat <= fat_lt
                )
                if _is_zero_nutrition and not is_allowed_zero:
                    logger.warning(
                        f"INVALID_NUTRITION_DATA | Excluding zero-nutrition food: "
                        f"{meta.get('food_name', row['food_name'])} ({fid}) | "
                        f"calories={listed_calories} protein={protein} carbs={carbs} fat={fat}"
                    )
                    continue

                # ── Regional cuisine resolution — data-first strategy ────────
                # Priority 1: CSV region column → cuisine via config map
                # Priority 2: metadata regional_cuisine field
                # Priority 3: YAML cuisine_keyword_map fallback (emits warning)
                # Priority 4: Pan Indian default (emits warning)
                csv_region = str(row.get('region', '')).strip()
                cuisine_from_csv = _csv_region_to_cuisine(csv_region)

                metadata_cuisine = meta.get("regional_cuisine") or node_metadata.get("regional_cuisine")
                has_specific_metadata = False
                if metadata_cuisine:
                    if isinstance(metadata_cuisine, dict):
                        prim = metadata_cuisine.get("primary", "Pan Indian")
                        if prim and normalize_cuisine_name(prim).lower().strip() not in ("pan indian", "pan_indian"):
                            has_specific_metadata = True
                    elif str(metadata_cuisine).strip() and normalize_cuisine_name(metadata_cuisine).lower().strip() not in ("pan indian", "pan_indian"):
                        has_specific_metadata = True

                if has_specific_metadata:
                    if not isinstance(metadata_cuisine, dict):
                        prim = normalize_cuisine_name(metadata_cuisine)
                        regional_cuisine = {
                            "primary": prim,
                            "secondary": [prim, "Pan Indian"]
                        }
                    else:
                        regional_cuisine = {
                            "primary": normalize_cuisine_name(metadata_cuisine.get("primary")),
                            "secondary": [normalize_cuisine_name(c) for c in metadata_cuisine.get("secondary", [])]
                        }
                elif cuisine_from_csv and cuisine_from_csv != "Pan Indian":
                    # Data-driven: trust the dataset region column if it is specific
                    regional_cuisine = {
                        "primary": cuisine_from_csv,
                        "secondary": [cuisine_from_csv, "Pan Indian"]
                    }
                else:
                    # Specific metadata is missing and CSV region is not specific (or is Pan Indian / missing).
                    # Run keyword detection to find a specific cuisine.
                    detected = _detect_cuisine_by_keywords(meta.get("food_name", row['food_name']))
                    if detected:
                        logger.warning(
                            f"CUISINE_KEYWORD_FALLBACK | '{meta.get('food_name', row['food_name'])}' "
                            f"has no specific region; keyword fallback detected: {detected}"
                        )
                        detected_norm = normalize_cuisine_name(detected)
                        regional_cuisine = {
                            "primary": detected_norm,
                            "secondary": [detected_norm, "Pan Indian"]
                        }
                    elif cuisine_from_csv: # Use Pan Indian from CSV
                        regional_cuisine = {
                            "primary": cuisine_from_csv,
                            "secondary": [cuisine_from_csv, "Pan Indian"]
                        }
                    elif metadata_cuisine: # Generic metadata cuisine
                        if not isinstance(metadata_cuisine, dict):
                            regional_cuisine = {"primary": "Pan Indian", "secondary": ["Pan Indian"]}
                        else:
                            regional_cuisine = {
                                "primary": normalize_cuisine_name(metadata_cuisine.get("primary", "Pan Indian")),
                                "secondary": [normalize_cuisine_name(c) for c in metadata_cuisine.get("secondary", ["Pan Indian"])]
                            }
                    else:
                        logger.warning(
                            f"METADATA_FALLBACK_WARNING | {meta.get('food_name', row['food_name'])} "
                            "| regional_cuisine → defaulting to Pan Indian"
                        )
                        regional_cuisine = {
                            "primary": "Pan Indian",
                            "secondary": ["Pan Indian"]
                        }


                # Construct the raw node structure
                node = {
                    "food_id": fid,
                    "food_name": meta.get("food_name", row['food_name']),
                    "type": meta.get("type", "INGREDIENT"),
                    "versions": meta.get("versions", {}),
                    "allergens": str(row.get('allergens', '')).lower().strip(),
                    "metadata": node_metadata,
                    "regional_cuisine": regional_cuisine,
                    "nutrition": {
                        "calories": listed_calories,
                        "protein": protein,
                        "carbs": carbs,
                        "fat": fat,
                        "fiber": fiber,
                        "serving_size_g": db_serving_g
                    },
                    "semantics": {
                        "category": meta.get("category"),
                        "subcategory": meta.get("subcategory"),
                        "cuisine": meta.get("cuisine"),
                        "regional_cuisine": regional_cuisine,
                        "dish_family": meta.get("dish_family", "other"),
                        "primary_ingredient": meta.get("primary_ingredient", "other"),
                        "complexity_score": meta.get("complexity_score", 5),
                        "prep_time_minutes": meta.get("prep_time_minutes", 15),
                        "cook_time_minutes": meta.get("cook_time_minutes", 20),
                        "protein_density": meta.get("protein_density", 0.0),
                        "meal_role": meta.get("meal_role") or (
                            "protein_main" if meta.get("dish_family") in ["chilla", "pancake", "egg_dish", "omelette"]
                            else "carb_base" if meta.get("dish_family") in ["poha", "upma", "dosa", "idli", "uttapam", "oats", "porridge", "cereal", "sandwich", "wrap", "roll", "roti", "paratha", "bread", "naan"]
                            else _map_category_to_meal_role(meta.get("category", ""))
                        )
                    },
                    "identity": {
                        "is_vegan": is_vegan,
                        "is_vegetarian": is_vegetarian
                    },
                    "structural_rules": rel.get("structural_rules", {}),
                    "compatibility": rel.get("compatibility", {}),
                    "batch_cooking": rel.get("batch_cooking", [])
                }
                
                # Validate, log warnings, and apply fallbacks for missing metadata
                food_name = node["food_name"]
                sem = node["semantics"]
                metadata_dict = node["metadata"]
                
                # ── Serving metadata & conversion for household units ──
                unit = str(meta.get("serving_unit") or get_primary_unit(food_name) or "g").lower().strip()
                serving_size_g = float(node["nutrition"].get("serving_size_g", 100))
                
                standard_weights = {
                    'tbsp': 15.0,
                    'tsp': 5.0,
                    'bowl': 200.0,
                    'glass': 250.0
                }
                
                conv_factor = 1.0
                if unit in standard_weights:
                    std_w = standard_weights[unit]
                    if serving_size_g > std_w:
                        conv_factor = serving_size_g / std_w
                elif unit in ('g', 'ml'):
                    conv_factor = serving_size_g
                
                typical_serving_qty = conv_factor
                
                preferred_serving = metadata_dict.get("preferred_serving") or sem.get("preferred_serving")
                if preferred_serving is None:
                    if unit == 'tbsp':
                        preferred_serving = 1.0
                    elif unit == 'tsp':
                        preferred_serving = 1.0
                    elif unit == 'bowl':
                        preferred_serving = 1.0
                    elif unit == 'glass':
                        preferred_serving = 1.0
                    elif unit in ('piece', 'pieces', 'unit', 'number', 'slice', 'sandwich', 'medium fruit'):
                        preferred_serving = 1.0
                    else:
                        preferred_serving = serving_size_g
                
                minimum_serving = metadata_dict.get("minimum_serving") or sem.get("minimum_serving")
                if minimum_serving is None:
                    if unit in ('tbsp', 'tsp', 'bowl', 'glass'):
                        minimum_serving = 0.5
                    elif unit in ('piece', 'pieces', 'unit', 'number', 'slice', 'sandwich', 'medium fruit'):
                        minimum_serving = 1.0
                    else:
                        minimum_serving = preferred_serving * 0.5
                    
                maximum_serving = metadata_dict.get("maximum_serving") or sem.get("maximum_serving")
                if maximum_serving is None:
                    if unit == 'tbsp':
                        maximum_serving = 2.0
                    elif unit == 'tsp':
                        maximum_serving = 2.0
                    elif unit == 'bowl':
                        maximum_serving = 2.5
                    elif unit == 'glass':
                        maximum_serving = 2.0
                    elif unit in ('piece', 'pieces', 'unit', 'number', 'slice', 'sandwich', 'medium fruit'):
                        maximum_serving = 4.0
                    else:
                        maximum_serving = preferred_serving * 2.5
                    
                serving_step = metadata_dict.get("serving_step") or sem.get("serving_step")
                if serving_step is None:
                    if unit in ('tbsp', 'tsp', 'bowl', 'glass'):
                        serving_step = 0.5
                    elif unit in ('piece', 'pieces', 'unit', 'number', 'slice', 'sandwich', 'medium fruit'):
                        serving_step = 1.0
                    else:
                        serving_step = 10.0 if unit in ('g', 'ml') else 1.0
                        
                metadata_dict["preferred_serving"] = preferred_serving
                metadata_dict["minimum_serving"] = minimum_serving
                metadata_dict["maximum_serving"] = maximum_serving
                metadata_dict["serving_step"] = serving_step
                
                # In-memory Serving unit & quantity exposure
                node["serving_unit"] = unit
                node["serving_quantity"] = typical_serving_qty
                node["servings"] = {
                    "serving_unit": unit,
                    "serving_quantity": typical_serving_qty,
                    "typical": typical_serving_qty,
                    "default": typical_serving_qty
                }
                
                # 2. food_group
                food_group = metadata_dict.get("food_group") or sem.get("food_group")
                if not food_group:
                    logger.warning(f"METADATA_FALLBACK_WARNING | {food_name} | food_group")
                    category = sem.get("category") or ""
                    cat_lower = category.lower()
                    if cat_lower in ["chicken/meat", "fish/seafood", "eggs", "paneer", "dal & pulses", "paneer & tofu", "seafood", "soya & tofu"]:
                        food_group = "protein"
                    elif cat_lower in ["rice", "whole grains", "millets & whole grains", "breakfast", "breads & roti", "oats & cereals"]:
                        food_group = "starch"
                    elif cat_lower in ["vegetables", "leafy greens", "vegetable"]:
                        food_group = "vegetable"
                    elif cat_lower in ["salad"]:
                        food_group = "salad"
                    elif cat_lower in ["fruits", "fruit"]:
                        food_group = "fruit"
                    elif cat_lower in ["dairy", "curd & yogurt"]:
                        food_group = "dairy"
                    else:
                        food_group = "other"
                sem["food_group"] = food_group
                
                # 3. meal_role
                meal_role = sem.get("meal_role")
                if not meal_role:
                    logger.warning(f"METADATA_FALLBACK_WARNING | {food_name} | meal_role")
                    dish_family = sem.get("dish_family", "other")
                    if dish_family in ["chilla", "pancake", "egg_dish", "omelette"]:
                        meal_role = "protein_main"
                    elif dish_family in ["poha", "upma", "dosa", "idli", "uttapam", "oats", "porridge", "cereal", "sandwich", "wrap", "roll", "roti", "paratha", "bread", "naan"]:
                        meal_role = "carb_base"
                    else:
                        meal_role = _map_category_to_meal_role(sem.get("category", "")) or "other"
                sem["meal_role"] = meal_role
                
                # 4. dish_family
                dish_family = sem.get("dish_family")
                if not dish_family or dish_family == "other":
                    logger.warning(f"METADATA_FALLBACK_WARNING | {food_name} | dish_family")
                    dish_family = "other"
                sem["dish_family"] = dish_family
                
                # 5. cuisine
                cuisine = sem.get("cuisine")
                if not cuisine:
                    cuisine = regional_cuisine.get("primary", "Pan Indian")
                sem["cuisine"] = normalize_cuisine_name(cuisine)
                
                # 6. cooking_style
                cooking_style = sem.get("cooking_style")
                if not cooking_style:
                    logger.warning(f"METADATA_FALLBACK_WARNING | {food_name} | cooking_style")
                    cooking_style = "steamed"
                sem["cooking_style"] = cooking_style
                
                # 7. breakfast_category (runtime only)
                breakfast_cat = meta.get("breakfast_category") or node_metadata.get("breakfast_category") or sem.get("breakfast_category")
                if not breakfast_cat:
                    br_cfg = NUTRITION_RULES.get("breakfast_rotation", {})
                    br_patterns = br_cfg.get("patterns", {})
                    breakfast_cat = "Traditional"
                    matched = False
                    
                    # We check patterns against: food_name, dish_family, cuisine, food_group, meal_role
                    check_str = f"{food_name} {sem.get('dish_family', '')} {sem.get('cuisine', '')} {sem.get('food_group', '')} {sem.get('meal_role', '')}".lower()
                    for cat_name, patterns in br_patterns.items():
                        for p in patterns:
                            if p.lower() in check_str:
                                breakfast_cat = cat_name
                                matched = True
                                break
                        if matched:
                            break
                sem["breakfast_category"] = breakfast_cat
                
                # ── Nutrition validity flag ───────────────────────────
                _is_nutrition_valid = (
                    (listed_calories > 0 and protein >= 0 and carbs >= 0 and fat >= 0)
                    or is_allowed_zero
                )
                node["runtime_flags"] = {"nutrition_valid": _is_nutrition_valid}
                if not _is_nutrition_valid:
                    logger.warning(
                        f"INVALID_NUTRITION_DATA | {node['food_name']} | {fid} | "
                        f"calories={listed_calories} protein={protein} carbs={carbs} fat={fat}"
                    )
                raw_nodes[fid] = node

            # ── STARTUP INTEGRITY VALIDATION ────────────────────────────────
            # Fail fast if any node is structurally corrupt.
            # Do NOT silently accept bad data — fix the dataset instead.
            invalid_nodes = []
            for fid, node in raw_nodes.items():
                for field in _REQUIRED_NODE_FIELDS:
                    if not node.get(field):
                        invalid_nodes.append((fid, f"missing '{field}'"))
                        break
                nutrition = node.get("nutrition", {})
                for nf in _REQUIRED_NUTRITION_FIELDS:
                    if nf not in nutrition:
                        invalid_nodes.append((fid, f"nutrition missing '{nf}'"))
                        break

            if invalid_nodes:
                # Log each bad node and raise exception - Fail Fast as user requested
                for fid, reason in invalid_nodes[:20]:
                    logger.error(f"[FoodGraph] Corrupt node food_id={fid}: {reason}")
                if len(invalid_nodes) > 20:
                    logger.error(f"[FoodGraph] ... and {len(invalid_nodes) - 20} more corrupt nodes.")
                
                raise ValueError(f"FoodGraph initialization failed: {len(invalid_nodes)} structurally corrupt nodes found.")

            # ── FREEZE ALL NODES ────────────────────────────────────────────
            # After freezing, no code may modify nodes in-place.
            # Every consumer MUST copy.deepcopy() before mutating.
            for fid, node in raw_nodes.items():
                self._nodes[fid] = _freeze(node)
                
            logger.info(
                f"[FoodGraph] Loaded: {len(self._ingredients)} Ingredients, "
                f"{len(self._recipes)} Recipes → {len(self._nodes)} valid frozen nodes. "
            )
        except Exception as e:
            logger.error(f"Failed to load FoodGraph layers: {e}")
            raise e

    def get_node(self, food_id: str) -> Optional[Any]:
        """Returns the frozen node for a food_id, or None."""
        return self._nodes.get(food_id)

    def get_all_nodes(self) -> Dict[str, Any]:
        """
        Returns the frozen node dictionary.
        DO NOT mutate the returned values — they are MappingProxyType.
        Always copy.deepcopy() before modifying a node.
        """
        return self._nodes

    def get_ingredients(self) -> Dict[str, Any]:
        return {k: v for k, v in self._nodes.items() if v.get("type") == "INGREDIENT"}

    def get_recipes(self) -> Dict[str, Any]:
        return {k: v for k, v in self._nodes.items() if v.get("type") == "RECIPE"}

    def get_compatibility_score(self, role: str, node: Any) -> int:
        """Returns how compatible this node is with a specific role."""
        comp = node.get("compatibility", {})
        return comp.get(role, 0)
        
    def filter_by_hard_constraints(self, diet_type: str, max_prep_time: int) -> List[str]:
        """Returns a list of food_ids that pass basic static filters."""
        valid_ids = []
        for fid, node in self._nodes.items():
            identity = node.get("identity", {})
            metadata = node.get("metadata", {})
            
            is_vegan = identity.get("is_vegan", False)
            is_veg = identity.get("is_vegetarian", False)
            node_diet = 'Vegan' if is_vegan else ('Vegetarian' if is_veg else 'NonVeg')
            if diet_type == "Vegan" and node_diet != "Vegan":
                continue
            if diet_type == "Vegetarian" and node_diet == "NonVeg":
                continue
                
            if metadata.get("prep_time_min", 999) > max_prep_time:
                continue
                
            valid_ids.append(fid)
            
        return valid_ids
