import json
import logging
import pandas as pd
from typing import Dict, List, Optional, Any

logger = logging.getLogger(__name__)

class FoodGraph:
    """
    3-Layer Knowledge Graph Loader.
    Loads nutrition CSV, metadata JSON, and relationship JSON.
    """
    def __init__(self, metadata_path: str, relationship_path: str, nutrition_csv_path: str):
        self.metadata_path = metadata_path
        self.relationship_path = relationship_path
        self.nutrition_csv_path = nutrition_csv_path
        
        self._nodes = {} # Merged data
        self._load_layers()

    def _load_layers(self):
        try:
            # 1. Load Metadata
            with open(self.metadata_path, 'r', encoding='utf-8') as f:
                metadata = json.load(f)
                
            # 2. Load Relationships
            with open(self.relationship_path, 'r', encoding='utf-8') as f:
                relationships = json.load(f)
                
            # 3. Load Nutrition
            nutrition_df = pd.read_csv(self.nutrition_csv_path)
            
            # Merge into a single node dictionary
            for idx, row in nutrition_df.iterrows():
                fid = str(row['food_id'])
                if fid not in metadata or fid not in relationships:
                    continue
                    
                meta = metadata[fid]
                rel = relationships[fid]
                
                self._nodes[fid] = {
                    "food_id": fid,
                    "food_name": meta.get("food_name", row['food_name']),
                    "allergens": str(row.get('allergens', '')).lower().strip(),
                    "nutrition": {
                        "calories": float(row.get('calories_kcal', 0)),
                        "protein": float(row.get('protein_g', 0)),
                        "carbs": float(row.get('carbohydrates_g', 0)),
                        "fat": float(row.get('fat_g', 0)),
                        "fiber": float(row.get('fiber_g', 0)),
                        "serving_size_g": float(row.get('serving_size_g', 100))
                    },
                    "semantics": meta.get("semantics", {}),
                    "identity": meta.get("identity", {}),
                    "meal_suitability": meta.get("meal_suitability", {}),
                    "servings": meta.get("servings", {}),
                    "metadata": meta.get("metadata", {}),
                    "structural_rules": rel.get("structural_rules", {}),
                    "compatibility": rel.get("compatibility", {}),
                    "batch_cooking": rel.get("batch_cooking", [])
                }
                
            logger.info(f"Loaded 3-Layer FoodGraph with {len(self._nodes)} items.")
        except Exception as e:
            logger.error(f"Failed to load FoodGraph layers: {e}")
            raise e

    def get_node(self, food_id: str) -> Optional[Dict]:
        return self._nodes.get(food_id)

    def get_all_nodes(self) -> Dict[str, Dict]:
        return self._nodes

    def get_compatibility_score(self, role: str, node: Dict) -> int:
        """Returns how compatible this node is with a specific role, based on its compatibility matrix."""
        comp = node.get("compatibility", {})
        return comp.get(role, 0)
        
    def filter_by_hard_constraints(self, diet_type: str, max_prep_time: int) -> List[str]:
        """Returns a list of food_ids that pass basic static filters."""
        valid_ids = []
        for fid, node in self._nodes.items():
            identity = node.get("identity", {})
            metadata = node.get("metadata", {})
            
            # Simple diet check
            node_diet = identity.get("diet", "NonVeg")
            if diet_type == "Vegan" and node_diet != "Vegan":
                continue
            if diet_type == "Vegetarian" and node_diet == "NonVeg":
                continue
                
            # Simple prep time check
            if metadata.get("prep_time_min", 999) > max_prep_time:
                continue
                
            valid_ids.append(fid)
            
        return valid_ids
