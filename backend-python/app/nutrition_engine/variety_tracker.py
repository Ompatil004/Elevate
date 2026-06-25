from typing import Set, List, Dict
from .food_utils import get_food_family

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
        self.daily_food_history: Dict[int, Set[str]] = {}
        self.daily_protein_history: Dict[int, Set[str]] = {}
        self.daily_carb_history: Dict[int, Set[str]] = {}
        self.vegetable_history: Dict[int, Set[str]] = {}
        self.meal_identity_history: Dict[str, int] = {}
        self.meal_appearance_counts: Dict[str, int] = {}  # tracks total appearances per meal_id
        self.daily_cuisine_history: Dict[int, Set[str]] = {}
        self.daily_cooking_style_history: Dict[int, Set[str]] = {}
        
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
            "daily_protein_history": {k: set(v) for k, v in self.daily_protein_history.items()},
            "daily_carb_history": {k: set(v) for k, v in self.daily_carb_history.items()},
            "vegetable_history": {k: set(v) for k, v in self.vegetable_history.items()},
            "meal_identity_history": dict(self.meal_identity_history),
            "meal_appearance_counts": dict(self.meal_appearance_counts),
            "daily_cuisine_history": {k: set(v) for k, v in getattr(self, 'daily_cuisine_history', {}).items()},
            "daily_cooking_style_history": {k: set(v) for k, v in getattr(self, 'daily_cooking_style_history', {}).items()},
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
        self.daily_protein_history = {k: set(v) for k, v in snapshot.get("daily_protein_history", {}).items()}
        self.daily_carb_history = {k: set(v) for k, v in snapshot.get("daily_carb_history", {}).items()}
        self.vegetable_history = {k: set(v) for k, v in snapshot.get("vegetable_history", {}).items()}
        self.meal_identity_history = dict(snapshot.get("meal_identity_history", {}))
        self.meal_appearance_counts = dict(snapshot.get("meal_appearance_counts", {}))
        self.daily_cuisine_history = {k: set(v) for k, v in snapshot.get("daily_cuisine_history", {}).items()}
        self.daily_cooking_style_history = {k: set(v) for k, v in snapshot.get("daily_cooking_style_history", {}).items()}
        
    def meal_history(self, meal_type: str) -> Set[str]:
        return getattr(self, f'{meal_type.lower()}_history', set())

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
        if family not in ('Drink', 'Fruit', 'Salad', 'Raita', 'Yogurt', 'Other', 'Vegetable'):
            self.family_history.append(family)

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
        r = REGION_ALIASES.get(region, region)
        self.cuisine_history.append(r)

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
        r = REGION_ALIASES.get(region, region)
        cuisine_freq = self.cuisine_history.count(r)
        penalty += min(10, cuisine_freq * 3)

        # Repeated template
        tmpl_freq = self.template_history.count(bp_idx)
        if tmpl_freq > 0:
            penalty += 25 if tmpl_freq == 1 else 50

        return penalty

    def record_meal_selection(self, meal_id: str, foods: List[str], protein_source: str, carb_source: str, vegetables: List[str], day_num: int, cuisine: str = None, cooking_style: str = None):
        self.meal_identity_history[meal_id] = day_num
        self.meal_appearance_counts[meal_id] = self.meal_appearance_counts.get(meal_id, 0) + 1
        
        if day_num not in self.daily_food_history:
            self.daily_food_history[day_num] = set()
        for f in foods:
            self.daily_food_history[day_num].add(f.lower().strip())
            
        if day_num not in self.daily_protein_history:
            self.daily_protein_history[day_num] = set()
        if protein_source:
            self.daily_protein_history[day_num].add(protein_source.lower().strip())
            self.protein_history.append(protein_source.lower().strip())
            
        if day_num not in self.daily_carb_history:
            self.daily_carb_history[day_num] = set()
        if carb_source:
            self.daily_carb_history[day_num].add(carb_source.lower().strip())
            self.carb_history.append(carb_source.lower().strip())
            
        if day_num not in self.vegetable_history:
            self.vegetable_history[day_num] = set()
        for v in vegetables:
            self.vegetable_history[day_num].add(v.lower().strip())
            
        if cuisine:
            if day_num not in self.daily_cuisine_history:
                self.daily_cuisine_history[day_num] = set()
            self.daily_cuisine_history[day_num].add(cuisine)
            
        if cooking_style:
            if day_num not in self.daily_cooking_style_history:
                self.daily_cooking_style_history[day_num] = set()
            self.daily_cooking_style_history[day_num].add(cooking_style)

    def is_same_day_duplicate(self, foods: List[str], day_num: int) -> bool:
        exempt_foods = {
            'sambar', 
            'multigrain roti',
            'whole wheat chapati',
            'boiled rice (uble chawal)'
        }
        daily_foods = self.daily_food_history.get(day_num, set())
        for f in foods:
            f_clean = f.lower().strip()
            if f_clean in exempt_foods:
                continue
            if f_clean in daily_foods:
                return True
        return False

    def is_duplicate_meal(self, meal_id: str, foods: List[str], protein_source: str, carb_source: str, day_num: int, cuisine: str = None, cooking_style: str = None) -> bool:
        # 1. Same-day food duplicates check
        if self.is_same_day_duplicate(foods, day_num):
            return True

        # 2. Hard cap: no meal_id more than 2 times in the full week
        all_appearances = sum(
            1 for d, mid in self.meal_identity_history.items()
            if mid == meal_id
        ) if isinstance(self.meal_identity_history, dict) else 0
        # Actually meal_identity_history maps meal_id -> last_day, not day -> meal_id
        # So count by tracking appearances separately
        appearances = self.meal_appearance_counts.get(meal_id, 0)
        if appearances >= 2:
            return True

        # 3. No duplicate meal identity in last 2 days (reduced from 4 to allow more variety)
        last_eaten = self.meal_identity_history.get(meal_id)
        if last_eaten is not None and (day_num - last_eaten) <= 2:
            return True

        # 4. Protein source rotation in the same day (removed strict block)
        # Handled by scorer penalties

        # 5. Carb source rotation in the same day (removed strict block)
        # Handled by scorer penalties

        # 6. Over-representation of cooking style in the same day
        # Removed strict block on cooking style since it's common to eat Curry twice a day.
        # It is now handled by the variety penalty score in meal_scorer.py

        return False
