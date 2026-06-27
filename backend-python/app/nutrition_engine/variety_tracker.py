from typing import Set, List, Dict
from .food_utils import get_food_family
from app.nutrition_engine.config import NUTRITION_RULES

REGION_ALIASES = {
    'North India':      'North Indian',
    'South India':      'South Indian',
    'East India':       'East Indian',
    'West India':       'West Indian',
    'Northeastern India': 'North East Indian',
    'Northeast India':  'North East Indian',
    'All India':        'Pan Indian',
}

class WeeklyVarietyTracker:
    """
    Tracks what has been used across the full week so the engine can
    penalise repeats when scoring candidates.
    """
    def __init__(self):
        self.reset()

    def reset(self):
        self.breakfast_history: Set[str] = set()
        self.lunch_history: Set[str] = set()
        self.dinner_history: Set[str] = set()
        self.snack_history: Set[str] = set()
        self.protein_history: List[str] = []
        self.carb_history: List[str] = []
        self.cuisine_history: List[str] = []
        self.template_history: List[int] = []
        
        # Family Tracking to prevent multiple "Breads" or "Curries"
        self.family_history: List[str] = []
        
        # New Phase 4 Strict Trackers
        self.item_history: Dict[str, int] = {}
        self.daily_food_history: Dict[int, Set[str]] = {}      # food NAMES per day
        self.daily_all_foods_used: Dict[int, Set[str]] = {}    # food IDs across ALL meals today
        self.daily_protein_history: Dict[int, Set[str]] = {}
        self.daily_carb_history: Dict[int, Set[str]] = {}
        self.vegetable_history: Dict[int, Set[str]] = {}
        self.meal_identity_history: Dict[str, int] = {}
        self.meal_appearance_counts: Dict[str, int] = {}  # tracks total appearances per meal_id
        self.daily_cuisine_history: Dict[int, List[str]] = {}
        self.daily_cooking_style_history: Dict[int, List[str]] = {}
        self.cooking_style_history: List[str] = []
        self.meal_signature_usage: Dict[str, int] = {}
        
        # V6 Weekly counters & breakfast rotation trackers
        self.weekly_protein_counts: Dict[str, int] = {}
        self.weekly_carb_counts: Dict[str, int] = {}
        self.weekly_breakfast_category_counts: Dict[str, int] = {}
        self.weekly_cuisine_counts: Dict[str, int] = {}
        self.weekly_cooking_style_counts: Dict[str, int] = {}
        self.daily_breakfast_category: Dict[int, str] = {}
        self.weekly_food_counts: Dict[str, int] = {}
        self.weekly_dish_family_counts: Dict[str, int] = {}
        
    def get_snapshot(self) -> Dict:
        return {
            "breakfast_history": set(self.breakfast_history),
            "lunch_history": set(self.lunch_history),
            "dinner_history": set(self.dinner_history),
            "snack_history": set(self.snack_history),
            "protein_history": list(self.protein_history),
            "carb_history": list(self.carb_history),
            "cuisine_history": list(self.cuisine_history),
            "template_history": list(self.template_history),
            "family_history": list(self.family_history),
            "item_history": dict(self.item_history),
            "daily_food_history": {k: set(v) for k, v in self.daily_food_history.items()},
            "daily_all_foods_used": {k: set(v) for k, v in self.daily_all_foods_used.items()},
            "daily_protein_history": {k: set(v) for k, v in self.daily_protein_history.items()},
            "daily_carb_history": {k: set(v) for k, v in self.daily_carb_history.items()},
            "vegetable_history": {k: set(v) for k, v in self.vegetable_history.items()},
            "meal_identity_history": dict(self.meal_identity_history),
            "meal_appearance_counts": dict(self.meal_appearance_counts),
            "daily_cuisine_history": {k: list(v) for k, v in getattr(self, 'daily_cuisine_history', {}).items()},
            "daily_cooking_style_history": {k: list(v) for k, v in getattr(self, 'daily_cooking_style_history', {}).items()},
            "cooking_style_history": list(getattr(self, 'cooking_style_history', [])),
            "meal_signature_usage": dict(getattr(self, 'meal_signature_usage', {})),
            "weekly_protein_counts": dict(getattr(self, 'weekly_protein_counts', {})),
            "weekly_carb_counts": dict(getattr(self, 'weekly_carb_counts', {})),
            "weekly_breakfast_category_counts": dict(getattr(self, 'weekly_breakfast_category_counts', {})),
            "weekly_cuisine_counts": dict(getattr(self, 'weekly_cuisine_counts', {})),
            "weekly_cooking_style_counts": dict(getattr(self, 'weekly_cooking_style_counts', {})),
            "daily_breakfast_category": dict(getattr(self, 'daily_breakfast_category', {})),
            "weekly_food_counts": dict(getattr(self, 'weekly_food_counts', {})),
            "weekly_dish_family_counts": dict(getattr(self, 'weekly_dish_family_counts', {})),
        }

    def restore_snapshot(self, snapshot: Dict):
        self.breakfast_history = set(snapshot.get("breakfast_history", []))
        self.lunch_history = set(snapshot.get("lunch_history", []))
        self.dinner_history = set(snapshot.get("dinner_history", []))
        self.snack_history = set(snapshot.get("snack_history", []))
        self.protein_history = list(snapshot.get("protein_history", []))
        self.carb_history = list(snapshot.get("carb_history", []))
        self.cuisine_history = list(snapshot.get("cuisine_history", []))
        self.template_history = list(snapshot.get("template_history", []))
        self.family_history = list(snapshot.get("family_history", []))
        self.item_history = dict(snapshot.get("item_history", {}))
        self.daily_food_history = {k: set(v) for k, v in snapshot.get("daily_food_history", {}).items()}
        self.daily_all_foods_used = {k: set(v) for k, v in snapshot.get("daily_all_foods_used", {}).items()}
        self.daily_protein_history = {k: set(v) for k, v in snapshot.get("daily_protein_history", {}).items()}
        self.daily_carb_history = {k: set(v) for k, v in snapshot.get("daily_carb_history", {}).items()}
        self.vegetable_history = {k: set(v) for k, v in snapshot.get("vegetable_history", {}).items()}
        self.meal_identity_history = dict(snapshot.get("meal_identity_history", {}))
        self.meal_appearance_counts = dict(snapshot.get("meal_appearance_counts", {}))
        self.daily_cuisine_history = {k: list(v) for k, v in snapshot.get("daily_cuisine_history", {}).items()}
        self.daily_cooking_style_history = {k: list(v) for k, v in snapshot.get("daily_cooking_style_history", {}).items()}
        self.cooking_style_history = list(snapshot.get("cooking_style_history", []))
        self.meal_signature_usage = dict(snapshot.get("meal_signature_usage", [] if isinstance(snapshot.get("meal_signature_usage"), list) else snapshot.get("meal_signature_usage", {})))
        self.weekly_protein_counts = dict(snapshot.get("weekly_protein_counts", {}))
        self.weekly_carb_counts = dict(snapshot.get("weekly_carb_counts", {}))
        self.weekly_breakfast_category_counts = dict(snapshot.get("weekly_breakfast_category_counts", {}))
        self.weekly_cuisine_counts = dict(snapshot.get("weekly_cuisine_counts", {}))
        self.weekly_cooking_style_counts = dict(snapshot.get("weekly_cooking_style_counts", {}))
        self.daily_breakfast_category = dict(snapshot.get("daily_breakfast_category", {}))
        self.weekly_food_counts = dict(snapshot.get("weekly_food_counts", {}))
        self.weekly_dish_family_counts = dict(snapshot.get("weekly_dish_family_counts", {}))
        
    def meal_history(self, meal_type: str) -> Set[str]:
        return getattr(self, f'{meal_type.lower()}_history', set())

    def get_days_foods_used(self, day_num: int) -> Set[str]:
        """Returns the set of food_ids already assigned to ANY meal slot today.
        Used by weekly_optimizer to pass as excluded_foods to candidate_generator."""
        return set(self.daily_all_foods_used.get(day_num, set()))

    # --- V6 Interfaces ---
    
    def calculate_variety_penalty(self, food_id: str, family: str, current_day: int) -> float:
        penalty = 0.0
        
        # Penalize if food eaten in last 4 days
        last_eaten = self.item_history.get(food_id)
        if last_eaten is not None:
            if current_day - last_eaten < 3:
                penalty += 50
            elif current_day - last_eaten < 5:
                penalty += 20
                
        # Penalize repeated family
        if family not in ('Drink', 'Fruit', 'Salad', 'Raita', 'Yogurt', 'Other', 'Vegetable'):
            recent_families = self.family_history[-6:] # last 6 items
            freq = recent_families.count(family)
            if freq > 0:
                penalty += 20 * freq
                
        return penalty

    def record_food(self, food_id: str, family: str, current_day: int):
        self.item_history[food_id] = current_day
        fid_clean = food_id.lower().strip()
        self.weekly_food_counts[fid_clean] = self.weekly_food_counts.get(fid_clean, 0) + 1
        if family not in ('Drink', 'Fruit', 'Salad', 'Raita', 'Yogurt', 'Other', 'Vegetable'):
            self.family_history.append(family)
            fam_clean = family.lower().strip()
            self.weekly_dish_family_counts[fam_clean] = self.weekly_dish_family_counts.get(fam_clean, 0) + 1

    # --- Legacy Interfaces (Still supported for transition) ---

    def record_meal(self, meal_type: str, components: List[Dict]):
        """Register a chosen meal so future days can avoid repeats."""
        hist = self.meal_history(meal_type)
        for c in components:
            name = c.get('food_name', c.get('name', ''))
            sg = c.get('swap_group', '')
            
            hist.add(name)
            family = get_food_family(name, sg)
            if family not in ('Drink', 'Fruit', 'Salad', 'Raita', 'Yogurt', 'Other', 'Vegetable'):
                self.family_history.append(family)
            
            if sg in ('chicken/meat', 'dal & pulses', 'paneer', 'eggs',
                      'fish & seafood', 'tofu & soy'):
                self.protein_history.append(sg)
            if sg in ('rice', 'bread & roti', 'oats & cereals'):
                self.carb_history.append(sg)

    def record_cuisine(self, region: str):
        if not region:
            return
        r = REGION_ALIASES.get(region, region)
        self.cuisine_history.append(str(r).lower().strip())

    def record_template(self, bp_idx: int):
        self.template_history.append(bp_idx)

    def variety_penalty(self, meal_type: str, components: List[Dict],
                        bp_idx: int, region: str) -> float:
        """Return a penalty score (≥0) that is subtracted from the meal score."""
        penalty = 0.0
        hist = self.meal_history(meal_type)

        for c in components:
            name = c.get('food_name', c.get('name', ''))
            sg   = c.get('swap_group', '')
            family = get_food_family(name, sg)
            
            # Repeated food name
            if name in hist:
                penalty += 40 if meal_type == 'breakfast' else 35
                
            # Repeated family within the last 3 days (approx 12 main meals)
            if family not in ('Drink', 'Fruit', 'Salad', 'Raita', 'Yogurt', 'Other', 'Vegetable'):
                family_recent = self.family_history[-12:]
                freq = family_recent.count(family)
                if freq > 0:
                    penalty += 30 * freq # Heavily penalize multiple sandwiches or dosas
                
            # Repeated protein source
            if sg in ('chicken/meat', 'dal & pulses', 'paneer', 'eggs',
                      'fish & seafood', 'tofu & soy'):
                freq = self.protein_history.count(sg)
                penalty += min(20, freq * 7)
            # Repeated carb
            if sg in ('rice', 'bread & roti', 'oats & cereals'):
                freq = self.carb_history.count(sg)
                penalty += min(15, freq * 5)

        # Repeated cuisine
        if region:
            r = REGION_ALIASES.get(region, region)
            r_clean = str(r).lower().strip()
            cuisine_freq = self.cuisine_history.count(r_clean)
            penalty += min(10, cuisine_freq * 3)

        # Repeated template
        tmpl_freq = self.template_history.count(bp_idx)
        if tmpl_freq > 0:
            penalty += 25 if tmpl_freq == 1 else 50

        return penalty

    def record_meal_selection(self, meal_id: str, foods: List[str], protein_source: str, carb_source: str, vegetables: List[str], day_num: int, cuisine: str = None, cooking_style: str = None, meal_signature: str = None, food_ids: List[str] = None, breakfast_category: str = None):
        self.meal_identity_history[meal_id] = day_num
        self.meal_appearance_counts[meal_id] = self.meal_appearance_counts.get(meal_id, 0) + 1
        
        if day_num not in self.daily_food_history:
            self.daily_food_history[day_num] = set()
        for f in foods:
            self.daily_food_history[day_num].add(f.lower().strip())

        # Track food_ids across ALL meal slots for cross-meal exclusion
        if day_num not in self.daily_all_foods_used:
            self.daily_all_foods_used[day_num] = set()
        if food_ids:
            for fid in food_ids:
                self.daily_all_foods_used[day_num].add(str(fid).lower().strip())
        else:
            # Fallback: use food names as ids when food_ids not provided
            for f in foods:
                self.daily_all_foods_used[day_num].add(f.lower().strip())
            
        if day_num not in self.daily_protein_history:
            self.daily_protein_history[day_num] = set()
        if protein_source:
            p_clean = protein_source.lower().strip()
            self.daily_protein_history[day_num].add(p_clean)
            self.protein_history.append(p_clean)
            self.weekly_protein_counts[p_clean] = self.weekly_protein_counts.get(p_clean, 0) + 1
            
        if day_num not in self.daily_carb_history:
            self.daily_carb_history[day_num] = set()
        if carb_source:
            c_clean = carb_source.lower().strip()
            self.daily_carb_history[day_num].add(c_clean)
            self.carb_history.append(c_clean)
            self.weekly_carb_counts[c_clean] = self.weekly_carb_counts.get(c_clean, 0) + 1
            
        if day_num not in self.vegetable_history:
            self.vegetable_history[day_num] = set()
        for v in vegetables:
            self.vegetable_history[day_num].add(v.lower().strip())
            
        if cuisine:
            cuisine_clean = str(cuisine).lower().strip()
            if day_num not in self.daily_cuisine_history:
                self.daily_cuisine_history[day_num] = []
            self.daily_cuisine_history[day_num].append(cuisine_clean)
            self.weekly_cuisine_counts[cuisine_clean] = self.weekly_cuisine_counts.get(cuisine_clean, 0) + 1
            self.record_cuisine(cuisine_clean)
            
        if cooking_style:
            if day_num not in self.daily_cooking_style_history:
                self.daily_cooking_style_history[day_num] = []
            self.daily_cooking_style_history[day_num].append(cooking_style)
            self.cooking_style_history.append(cooking_style)
            self.weekly_cooking_style_counts[cooking_style] = self.weekly_cooking_style_counts.get(cooking_style, 0) + 1
            
        if breakfast_category:
            self.weekly_breakfast_category_counts[breakfast_category] = self.weekly_breakfast_category_counts.get(breakfast_category, 0) + 1
            self.daily_breakfast_category[day_num] = breakfast_category
            
        if meal_signature:
            self.meal_signature_usage[meal_signature] = self.meal_signature_usage.get(meal_signature, 0) + 1

    def is_duplicate_meal(self, meal_id: str, foods: List[str], protein_source: str, carb_source: str, day_num: int, meal_type: str, cuisine: str = None, cooking_style: str = None) -> bool:
        # 1. Same exact food: Cannot repeat within X days.
        limit = int(NUTRITION_RULES["variety"].get(f"{meal_type.lower()}_max_frequency_days", 7))
        
        # We can't check same_day duplicate directly because the user wants "Same exact food Cannot repeat within N days"
        # but specifically tailored to the meal_type's rule. Let's adjust is_same_day_duplicate
        # Only truly neutral, tiny-portion staple sides are exempt from the
        # repeat check. Main carbs like rotis and rice are NOT exempt so the
        # engine is forced to diversify them across the week.
        exempt_foods = {
            'sambar',
            'boiled rice (uble chawal)',
        }
        for f in foods:
            f_clean = f.lower().strip()
            if f_clean in exempt_foods:
                continue
            for d in range(max(1, day_num - limit + 1), day_num + 1):
                if f_clean in self.daily_food_history.get(d, set()):
                    return True

        # 2. Same meal identity: Cannot repeat within X days.
        if meal_id != 'dynamic_meal':
            limit_meal = limit
            last_eaten = self.meal_identity_history.get(meal_id)
            if last_eaten is not None and (day_num - last_eaten) < limit_meal:
                return True

        # 3. Same protein source: Maximum X consecutive meals.
        limit_protein = int(NUTRITION_RULES["variety"]["protein_source_consecutive_max"])
        if protein_source and len(self.protein_history) >= limit_protein:
            p_clean = protein_source.lower().strip()
            if all(p == p_clean for p in self.protein_history[-limit_protein:]):
                return True

        # 4. Same cuisine: Maximum X times/day.
        limit_cuisine = int(NUTRITION_RULES["variety"]["cuisine_daily_max"])
        if cuisine:
            cuisine_clean = str(cuisine).lower().strip()
            cuisine_count = self.daily_cuisine_history.get(day_num, []).count(cuisine_clean)
            if cuisine_count >= limit_cuisine:
                return True

        # 5. Same cooking method: Maximum X consecutive meals.
        limit_cooking = int(NUTRITION_RULES["variety"]["cooking_style_consecutive_max"])
        if cooking_style and len(self.cooking_style_history) >= limit_cooking:
            if all(c == cooking_style for c in self.cooking_style_history[-limit_cooking:]):
                return True

        return False
