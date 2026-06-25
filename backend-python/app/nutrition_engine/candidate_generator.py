import os
import json
import logging
from typing import Dict, List, Any
import random
import difflib
from app.nutrition_engine.food_utils import get_meal_suitability

logger = logging.getLogger(__name__)

class CandidateGenerator:
    """
    Phase 4.9: Predefined Meal Candidate Generator.
    Generates candidates from a structured Meal Knowledge Base.
    """
    def __init__(self, food_graph):
        self.food_graph = food_graph
        
        # Load Meal Knowledge Base dynamically from the same folder as nutrition CSV
        data_dir = os.path.dirname(food_graph.nutrition_csv_path)
        kb_path = os.path.join(data_dir, 'meal_knowledge_base.json')
        
        try:
            with open(kb_path, 'r', encoding='utf-8') as f:
                self.meal_kb = json.load(f)
            logger.info(f"Loaded Meal Knowledge Base with {len(self.meal_kb)} meals.")
        except Exception as e:
            logger.error(f"Failed to load meal knowledge base: {e}")
            self.meal_kb = []
            
        # Build food name -> node mapping
        self.name_to_node = {}
        self.available_food_names = []
        for fid, node in food_graph.get_all_nodes().items():
            food_name = node["food_name"].lower().strip()
            self.name_to_node[food_name] = node
            self.available_food_names.append(food_name)
            
        import re
        from app.deterministic_meal_engine import FOOD_NAME_BLOCKLIST
        blocklist_str = '|'.join(r'\b' + re.escape(t) + r'\b' for t in FOOD_NAME_BLOCKLIST)
        self.blocklist_pattern = re.compile(blocklist_str) if blocklist_str else None
        
        self._user_pattern_cache = {}
        self._fuzzy_cache = {}
            
    def _fuzzy_match_food(self, query: str) -> dict:
        if query in self._fuzzy_cache:
            return self._fuzzy_cache[query]
            
        query_lower = query.lower().strip()
        
        # 1. Exact match
        if query_lower in self.name_to_node:
            self._fuzzy_cache[query] = self.name_to_node[query_lower]
            return self._fuzzy_cache[query]
            
        # 2. Handle common aliases BEFORE substring matching
        aliases = {
            "yellow moong dal": "washed moong",
            "toor dal": "arhar",
            "masoor dal": "masoor dal",
            "chana dal": "channa curry",
            "vegetable pulao": "mixed vegetable pulao",
            "chapati (roti)": "chapati",
            "chole (chickpea curry)": "chickpeas curry",
            "capsicum besan sabzi": "stuffed capsicum",
            "cabbage sabzi": "cabbage and peas",
            "tori sabzi": "tori",
            "soya bean curry": "soyabean curry",
            "soya chunks curry": "soya chunks and peas",
            "aloo gobi": "aloo gobhi",
            "lauki sabzi": "lauki",
            "kachumber salad": "tossed salad",
            "sprout salad": "sprouted moong",
            "palak paneer": "spinach paneer",
            "kadhai paneer": "kadhai paneer",
            "matar paneer": "paneer matar",
            "rajma curry": "kidney bean curry",
            "lobia curry": "lobia curry",
            "paneer butter masala": "paneer",
            "tofu curry": "tofu bhurji",
            "bhindi masala": "bhindi",
            "plain yogurt (curd)": "greek yogurt",
            "jeera rice": "cumin pulao",
            "lettuce salad": "tossed salad",
            "cucumber salad": "cucumber tomato salad",
            "tomato": "tossed salad",
            "multigrain bread": "multigrain roti",
            "missi roti": "multigrain roti"
        }
        if query_lower in aliases:
            # Re-run fuzzy match with the alias
            query_lower = aliases[query_lower]

        # Exact partial match
        for name in self.available_food_names:
            if query_lower == name.split("(")[0].strip().lower() or query_lower == name.lower():
                self._fuzzy_cache[query] = self.name_to_node[name]
                return self._fuzzy_cache[query]

        # 3. Simple Substring matching (e.g. "masoor dal" inside "whole masoor (masoor ki dal)")
        for name in self.available_food_names:
            if query_lower in name.lower() and len(query_lower) > 3:
                self._fuzzy_cache[query] = self.name_to_node[name]
                return self._fuzzy_cache[query]
        for name in self.available_food_names:
            if name.lower() in query_lower and len(name) > 3:
                self._fuzzy_cache[query] = self.name_to_node[name]
                return self._fuzzy_cache[query]
                    
        # 4. Fallback to difflib
        matches = difflib.get_close_matches(query_lower, self.available_food_names, n=1, cutoff=0.5)
        if matches:
            self._fuzzy_cache[query] = self.name_to_node[matches[0]]
            return self._fuzzy_cache[query]
            
        self._fuzzy_cache[query] = None
        return None

    def _is_diet_compatible(self, meal_diet: str, user_diet: str) -> bool:
        if user_diet == "Vegan":
            return meal_diet == "Vegan"
        elif user_diet == "Vegetarian":
            return meal_diet in ("Vegan", "Vegetarian")
        return True

    def _get_user_patterns(self, user_profile: Dict):
        profile_str = str(user_profile)
        if profile_str in self._user_pattern_cache:
            return self._user_pattern_cache[profile_str]
            
        import re
        allergies = user_profile.get('allergies') or []
        allergy_regex = None
        if allergies:
            expanded = []
            for a in allergies:
                al = a.strip().lower()
                if al in ('lactose', 'dairy'):
                    expanded.extend(['milk', 'dairy', 'lactose', 'cheese',
                                     'paneer', 'butter', 'ghee', 'cream', 'yogurt', 'curd'])
                elif al == 'gluten':
                    expanded.extend(['wheat', 'roti', 'chapati', 'gluten', 'barley', 'rye',
                                     'maida', 'suji', 'semolina', 'atta', 'bread', 'toast'])
                elif al == 'nuts':
                    expanded.extend(['nuts', 'almond', 'cashew', 'walnut',
                                     'peanut', 'pistachio'])
                else:
                    expanded.append(al)
            allergy_str = '|'.join(r'\b' + re.escape(x) + r'\b' for x in expanded if x)
            allergy_regex = re.compile(allergy_str) if allergy_str else None
            
        never_recommend = user_profile.get('never_recommend') or []
        never_regex = None
        if never_recommend:
            never_str = '|'.join(re.escape(str(t).lower().strip()) for t in never_recommend if t)
            never_regex = re.compile(never_str) if never_str else None
            
        self._user_pattern_cache[profile_str] = (allergy_regex, never_regex)
        return allergy_regex, never_regex

    def _is_safe_meal(self, plate: List[Dict], user_profile: Dict) -> bool:
        if not user_profile:
            return True
            
        allergy_pattern, never_pattern = self._get_user_patterns(user_profile)
            
        # Verify each food item in the plate
        for item in plate:
            name = item.get('food_name', '').lower()
            allergens = item.get('allergens', '').lower()
            
            # Check blocklist
            if self.blocklist_pattern and self.blocklist_pattern.search(name):
                return False
                
            # Check allergies (against name and allergens field)
            if allergy_pattern:
                if allergy_pattern.search(name) or allergy_pattern.search(allergens):
                    return False
                    
            # Check never recommend
            if never_pattern and never_pattern.search(name):
                return False
                
        return True

    def generate_candidates(self, template: Dict[str, Any], meal_type: str, diet_type: str, count: int = 5, user_profile: Dict = None, day_seed: int = 0) -> tuple[List[List[Dict]], Dict]:
        """
        Generates candidate plates based on predefined Meal Identities.
        Returns a tuple of (plates, stats).
        day_seed is used to shuffle the candidate pool differently for each day,
        preventing the same meals from always appearing in the same order on retries.
        """
        candidates = []
        gen_stats = {
            "total_candidates": 0,
            "passed_structure": 0,
            "failed_structure": 0
        }
        
        # 1. Filter meals based on type and diet compatibility
        possible_meals = [
            m for m in self.meal_kb
            if m["meal_type"].lower() == meal_type.lower()
            and self._is_diet_compatible(m["diet_type"], diet_type)
        ]
        
        # Fallback for missing diet-specific meals in knowledge base (e.g., no Vegan lunch)
        if not possible_meals and diet_type == "Vegan":
            possible_meals = [
                m for m in self.meal_kb
                if m["meal_type"].lower() == meal_type.lower()
                and self._is_diet_compatible(m["diet_type"], "Vegetarian")
            ]
        elif not possible_meals and diet_type == "Pescatarian":
            possible_meals = [
                m for m in self.meal_kb
                if m["meal_type"].lower() == meal_type.lower()
                and self._is_diet_compatible(m["diet_type"], "NonVeg")
            ]
        
        # 2. Filter by template anchor role
        anchor_role = template.get('anchor', {}).get('role')
        filtered_meals = possible_meals
        if anchor_role:
            filtered_meals = [
                m for m in possible_meals
                if m.get("anchor_role") == anchor_role
            ]
            if not filtered_meals:
                filtered_meals = possible_meals
                
        # Phase 5: Hard filter by Meal Suitability Intelligence
        suitable_meals = []
        for m in filtered_meals:
            score = get_meal_suitability(m["meal_name"], meal_type)
            if score >= 50:
                suitable_meals.append(m)
            else:
                logger.debug(f"Rejected {m['meal_name']} for {meal_type} due to low suitability ({score})")
                
        if suitable_meals:
            filtered_meals = suitable_meals
        else:
            logger.warning(f"No suitable meals found for {meal_type} with role {anchor_role}. Relaxing suitability filter.")
            
        gen_stats["total_candidates"] = len(filtered_meals)
        
        # Shuffle using a deterministic but day-specific seed so each day tries different meals
        # This prevents the same meals appearing in the same order on every retry attempt
        import random as _rng
        rng = _rng.Random(day_seed)
        shuffled_meals = list(filtered_meals)
        rng.shuffle(shuffled_meals)
        
        # 3. Build plates from meal definitions
        for meal in shuffled_meals:
            plate = []
            meal_valid = True
            for food_name in meal["foods"]:
                node = self._fuzzy_match_food(food_name)
                if node:
                    node_copy = dict(node)
                    # Inject meal identity & metadata for portion optimizer & scorer
                    node_copy["semantics"] = dict(node_copy.get("semantics", {}))
                    node_copy["semantics"]["meal_id"] = meal["meal_id"]
                    node_copy["semantics"]["meal_name"] = meal["meal_name"]
                    node_copy["semantics"]["protein_source"] = meal.get("protein_source")
                    node_copy["semantics"]["carb_source"] = meal.get("carb_source")
                    node_copy["semantics"]["vegetables"] = meal.get("vegetables", [])
                    node_copy["semantics"]["meal_rules"] = meal.get("rules", [])
                    node_copy["semantics"]["cuisine"] = meal.get("cuisine", "Pan Indian")
                    node_copy["semantics"]["cooking_style"] = meal.get("cooking_style", "Mixed")
                    
                    if "portion_rules" in meal and food_name in meal["portion_rules"]:
                        node_copy["portion_rules"] = meal["portion_rules"][food_name]
                        
                    if "internal_ratio" in meal and food_name in meal["internal_ratio"]:
                        node_copy["semantics"]["internal_ratio"] = meal["internal_ratio"][food_name]
                        
                    plate.append(node_copy)
                else:
                    logger.warning(f"Food name '{food_name}' in meal '{meal['meal_id']}' not found in FoodGraph.")
                    meal_valid = False
                    break
                    
            if meal_valid and plate:
                if self._is_safe_meal(plate, user_profile):
                    candidates.append(plate)
                    gen_stats["passed_structure"] += 1
                else:
                    gen_stats["failed_structure"] += 1
            else:
                gen_stats["failed_structure"] += 1
                
        # Sample to ensure some variety if we have more than count
        if len(candidates) > count:
            candidates = rng.sample(candidates, count)
            
        return candidates, gen_stats
