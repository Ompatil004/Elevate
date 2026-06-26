import json
import logging
import types
import pandas as pd
from typing import Dict, List, Optional, Any

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
                egg_keywords = ['egg']
                
                has_non_veg = any(kw in food_name_lower for kw in non_veg_keywords)
                has_egg = any(kw in food_name_lower for kw in egg_keywords) and not ('eggless' in food_name_lower or 'mock' in food_name_lower or 'vegan' in food_name_lower)
                
                if has_non_veg or has_egg:
                    is_vegan = False
                    is_vegetarian = False
                elif 'paneer' in food_name_lower or 'curd' in food_name_lower or 'milk' in food_name_lower or 'yogurt' in food_name_lower or 'cheese' in food_name_lower or 'butter' in food_name_lower or 'ghee' in food_name_lower or 'raita' in food_name_lower:
                    is_vegan = False
                
                node = {
                    "food_id": fid,
                    "food_name": meta.get("food_name", row['food_name']),
                    "type": meta.get("type", "INGREDIENT"),
                    "versions": meta.get("versions", {}),
                    "allergens": str(row.get('allergens', '')).lower().strip(),
                    "nutrition": {
                        "calories": float(row.get('calories_kcal', 0)),
                        "protein": float(row.get('protein_g', 0)),
                        "carbs": float(row.get('carbohydrates_g', 0)),
                        "fat": float(row.get('fat_g', 0)),
                        "fiber": float(row.get('fiber_g', 0)),
                        "serving_size_g": float(row.get('serving_size_g', 100))
                    },
                    "semantics": {
                        "category": meta.get("category"),
                        "subcategory": meta.get("subcategory"),
                        "cuisine": meta.get("cuisine"),
                        "dish_family": meta.get("dish_family", "other"),           # set by preprocess_food_metadata.py
                        "primary_ingredient": meta.get("primary_ingredient", "other"),  # set by preprocess_food_metadata.py
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
            
            node_diet = identity.get("diet", "NonVeg")
            if diet_type == "Vegan" and node_diet != "Vegan":
                continue
            if diet_type == "Vegetarian" and node_diet == "NonVeg":
                continue
                
            if metadata.get("prep_time_min", 999) > max_prep_time:
                continue
                
            valid_ids.append(fid)
            
        return valid_ids
