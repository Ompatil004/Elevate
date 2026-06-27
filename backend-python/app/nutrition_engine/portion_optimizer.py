import re
from typing import List, Dict, Tuple
from app.nutrition_engine.food_utils import get_primary_unit
from app.nutrition_engine.config import NUTRITION_RULES

# Per-food calorie caps: prevents any single side item from being over-scaled
# Keys are substrings matched against food_name.lower()
FOOD_CALORIE_CAPS = NUTRITION_RULES.get("food_calorie_caps", {
    'salad':   150,   # max 150 cal for any salad
    'raita':   100,   # max 100 cal
    'kachumber': 120,
    'kosambari': 120,
    'tossed':  150,
    'chutney':  50,
    'pickle':   30,
    'achar':    30,
    'tea':      80,
    'coffee':   100,
})

# Overrides for salad-like foods: max bowls regardless of protein target
SALAD_MAX_BOWLS = float(NUTRITION_RULES.get("portions", {}).get("salad_raita_max_bowl", 1.0))
SALAD_KEYWORDS = {'salad', 'raita', 'kachumber', 'kosambari', 'tossed', 'pachadi'}

def _format_serving(qty: float, unit: str, name: str = '', cal: float = 0.0) -> str:
    """Produce a clean human-readable serving string based on database unit and quantity."""
    qty = float(qty) if qty else 0.0
    
    if unit in ('g', 'ml'):
        return f"{int(round(qty))}{unit}"
        
    if unit in ('piece', 'pieces', 'unit', 'number', 'slice', 'sandwich', 'medium fruit'):
        n = int(round(qty))
        if n <= 0:
            n = 1
            
        if unit == 'piece': label = 'piece' if n == 1 else 'pieces'
        elif unit == 'slice': label = 'slice' if n == 1 else 'slices'
        elif unit == 'sandwich': label = 'sandwich' if n == 1 else 'sandwiches'
        elif unit == 'medium fruit': label = 'medium fruit' if n == 1 else 'medium fruits'
        else: label = unit
        
        return f"{n} {label}"
        
    if unit in ('bowl', 'bowls', 'cup', 'cups', 'glass', 'glasses', 'plate', 'plates', 'tbsp', 'tsp', 'scoop'):
        qty = round(qty * 2) / 2 # Round to nearest 0.5
        n_str = f"{qty:.1f}".rstrip('0').rstrip('.')
        unit_clean = unit
        if float(qty) > 1.0 and (not unit.endswith('s') or unit == 'glass') and unit not in ('tbsp', 'tsp'):
            if unit == 'glass':
                unit_clean = 'glasses'
            else:
                unit_clean = unit + 's'
        elif float(qty) <= 1.0 and unit.endswith('s'):
            if unit == 'glasses':
                unit_clean = 'glass'
            else:
                unit_clean = unit[:-1]
        return f"{n_str} {unit_clean}"

    # Fallback
    n_str = f"{qty:.1f}".rstrip('0').rstrip('.')
    return f"{n_str} {unit}"

def _get_portion_profile(food_name: str, unit: str, base_qty: float) -> List[float]:
    # Deprecated: Static lists capped quantities too low for high-calorie goals (e.g., max 250g rice).
    # We now rely on dynamic p_step, p_min, and p_max to allow proper scaling.
    return None

class PortionOptimizer:
    """
    Step-based portion optimizer compatible with V6 Semantic Graph nodes.
    Steps portions incrementally until target_cal is reached or all max out.
    """
    def __init__(self):
        pass

    def get_max_capacity(self, components: List[Dict]) -> Tuple[float, float]:
        """Calculates the absolute maximum calories and protein a plate can provide based on household constraints."""
        if not components:
            return 0.0, 0.0
            
        max_cal = 0.0
        max_pro = 0.0
        
        for c in components:
            servings = c.get('servings', {})
            nutrition = c.get('nutrition', {})
            
            def get_val(keys, default=None):
                for k in keys:
                    if servings and k in servings and servings[k] is not None:
                        return servings[k]
                    if k in c and c[k] is not None:
                        return c[k]
                return default

            db_base_qty = float(get_val(['default', 'typical', 'serving_quantity'], 1.0) or 1.0)
            db_unit = str(get_val(['unit', 'serving_unit'], 'g'))
            internal_ratio = float(c.get('semantics', {}).get('internal_ratio', db_base_qty))
            primary_unit = get_primary_unit(str(c.get('food_name', '')))
            portion_rules = c.get('portion_rules', {})
            
            if primary_unit:
                unit = primary_unit
            elif portion_rules:
                unit = str(portion_rules.get('unit', db_unit))
            else:
                unit = db_unit

            if portion_rules:
                p_max = float(portion_rules.get('max_qty', internal_ratio * 2.0))
            else:
                p_max = float(get_val(['maximum', 'portion_max'], internal_ratio * 2.0) or internal_ratio * 2.0)
                p_max = max(p_max, internal_ratio * 5.0)
                
            food_name_lower = str(c.get('food_name', '')).lower()
            if 'whey' in food_name_lower or 'protein powder' in food_name_lower:
                p_max = min(p_max, float(NUTRITION_RULES.get("portions", {}).get("whey_max_scoop", 1.0)))
            if 'chutney' in food_name_lower or 'pickle' in food_name_lower:
                p_max = min(p_max, float(NUTRITION_RULES["portions"]["chutney_pickle_max_tbsp"]))
            if 'salad' in food_name_lower or 'raita' in food_name_lower:
                if unit in ('bowl', 'bowls', 'plate', 'plates'):
                    p_max = min(p_max, float(NUTRITION_RULES["portions"]["salad_raita_max_bowl"]))
            if any(drink in food_name_lower for drink in ('milkshake', 'smoothie', 'juice', 'drink', 'lassi', 'chaas', 'buttermilk', 'coffee', 'tea', 'water', 'lemonade')):
                if unit in ('glass', 'glasses', 'cup', 'cups', 'mug', 'mugs'):
                    p_max = min(p_max, float(NUTRITION_RULES.get("portions", {}).get("drink_max_glass", 1.0)))
                    
            if unit != db_unit and internal_ratio > 0:
                base_qty = internal_ratio
            else:
                base_qty = db_base_qty
                
            if not nutrition and 'calories_kcal' in c:
                base_cal = float(c.get('calories_kcal', 0))
                base_pro = float(c.get('protein_g', 0))
            else:
                base_cal = float(nutrition.get('calories', 0))
                base_pro = float(nutrition.get('protein', 0))
                
            cal_per_unit = base_cal / base_qty if base_qty > 0 else 0
            pro_per_unit = base_pro / base_qty if base_qty > 0 else 0
            
            max_cal += p_max * cal_per_unit
            max_pro += p_max * pro_per_unit
            
        return max_cal, max_pro

    def optimize_portions(self, components: List[Dict], target_macros: Dict) -> List[Dict]:
        """
        Phase 5: Scales the entire meal plate using the internal ratio multiplier.
        Guarantees meal identity preservation while finding the best portion bounds.
        """
        target_cal = target_macros.get("calories", 0)
        target_pro = target_macros.get("protein", 0)
        
        if not components or target_cal <= 0:
            return []

        def get_priority_level(food: Dict, unit: str) -> int:
            sem = food.get("semantics", {})
            cat = sem.get("category", "") or ""
            df = sem.get("dish_family", "") or ""
            name = str(food.get("food_name", "")).lower()

            # 1. Protein — scale first to hit protein/calorie targets
            _PROTEIN_GROUPS = {
                "Dal & Pulses", "Chicken/Meat", "Paneer", "Eggs", "Fish/Seafood",
                "Meat & Chicken", "Paneer & Tofu", "Seafood", "Soya & Tofu"
            }
            pdensity = sem.get("protein_density", 0)
            if cat in _PROTEIN_GROUPS or df in ("curry", "korma", "dal", "sambar", "egg_dish", "omelette") or pdensity > 0.12:
                return 1

            # 2. Carbohydrates / Staple — fill calorie gap second
            _CARB_GROUPS = {
                "Rice", "Whole Grains", "Millets & Whole Grains", "Breads & Roti", "Oats & Cereals"
            }
            if cat in _CARB_GROUPS or df in ("rice", "plain_rice", "fried_rice", "pulao", "biryani", "roti", "paratha", "bread", "naan", "dosa", "idli", "uttapam", "poha", "upma"):
                return 2

            # 3. Vegetables — volumetric, scale third
            if cat in ("Vegetables", "Leafy Greens") or df == "vegetable":
                return 3

            # 4. Side Dishes (Salad, Raita, Curd, Fruits, Chutney, Soup, Drink) — scale last
            if cat in ("Salad", "Fruits", "Dairy & Eggs", "Curd & Yogurt", "Beverages") or df in ("salad", "raita", "soup", "chutney"):
                return 4

            # 5. Fats / Oils / Condiments — never scale these up
            if "ghee" in name or "oil" in name or "butter" in name or cat in ("Fats", "Oils", "Nuts", "Seeds"):
                return 5

            return 1  # default to protein priority (catches combo_meals, etc.)

        # 1. Initialize State
        state = []
        for c in components:
            servings = c.get('servings', {})
            nutrition = c.get('nutrition', {})
            
            def get_val(keys, default=None):
                for k in keys:
                    if servings and k in servings and servings[k] is not None:
                        return servings[k]
                    if k in c and c[k] is not None:
                        return c[k]
                return default

            db_base_qty = float(get_val(['default', 'typical', 'serving_quantity'], 1.0) or 1.0)
            db_unit = str(get_val(['unit', 'serving_unit'], 'g'))
            
            metadata = c.get('metadata', {})
            sem = c.get('semantics', {})
            
            # Fetch priority keys from metadata, semantics, or root
            p_pref = metadata.get("preferred_serving") or sem.get("preferred_serving") or sem.get("typical_serving") or sem.get("typical_quantity") or sem.get("internal_ratio") or db_base_qty
            p_min = metadata.get("minimum_serving") or sem.get("minimum_serving") or sem.get("min_quantity") or sem.get("portion_min")
            p_max = metadata.get("maximum_serving") or sem.get("maximum_serving") or sem.get("max_quantity") or sem.get("portion_max")
            p_step = metadata.get("serving_step") or sem.get("serving_step") or sem.get("step_quantity") or sem.get("portion_step")
            
            # Fallbacks
            if p_pref is None or float(p_pref) <= 0:
                p_pref = db_base_qty
            p_pref = float(p_pref)
            
            if p_min is None:
                p_min = p_pref * 0.5
            p_min = float(p_min)
            
            if p_max is None:
                p_max = max(p_pref * 2.0, p_pref * 5.0)
            p_max = float(p_max)
            
            primary_unit = get_primary_unit(str(c.get('food_name', '')))
            portion_rules = c.get('portion_rules', {})
            if primary_unit:
                unit = primary_unit
            elif portion_rules:
                unit = str(portion_rules.get('unit', db_unit))
            else:
                unit = db_unit
                
            if p_step is None:
                if unit in ('piece', 'pieces', 'unit', 'number', 'slice', 'sandwich', 'medium fruit'):
                    p_step = 1.0
                elif unit in ('bowl', 'bowls', 'plate', 'plates', 'glass', 'glasses', 'tbsp', 'tsp', 'scoop'):
                    p_step = 0.5
                else:
                    p_step = 10.0 if unit in ('g', 'ml') else 1.0
            p_step = float(p_step)
            
            # Apply specific overrides from config/rules
            food_name_lower = str(c.get('food_name', '')).lower()
            if 'whey' in food_name_lower or 'protein powder' in food_name_lower:
                p_max = min(p_max, float(NUTRITION_RULES.get("portions", {}).get("whey_max_scoop", 1.0)))
            if 'chutney' in food_name_lower or 'pickle' in food_name_lower:
                p_max = min(p_max, float(NUTRITION_RULES.get("portions", {}).get("chutney_pickle_max_tbsp", 2.0)))
            if any(kw in food_name_lower for kw in SALAD_KEYWORDS) or 'salad' in food_name_lower or 'raita' in food_name_lower:
                if unit in ('bowl', 'bowls', 'plate', 'plates'):
                    p_max = min(p_max, float(NUTRITION_RULES.get("portions", {}).get("salad_raita_max_bowl", 1.0)))
                    p_min = max(p_min, float(NUTRITION_RULES.get("portions", {}).get("salad_raita_min_bowl", 0.5)))
            if any(drink in food_name_lower for drink in ('milkshake', 'smoothie', 'juice', 'drink', 'lassi', 'chaas', 'buttermilk', 'coffee', 'tea', 'water', 'lemonade')):
                if unit in ('glass', 'glasses', 'cup', 'cups', 'mug', 'mugs'):
                    p_max = min(p_max, float(NUTRITION_RULES.get("portions", {}).get("drink_max_glass", 1.0)))

            # ── V6 Realistic household serving caps ───────────────────────────
            # Roti / Paratha / Chapati / Naan / Bread — max 5 pieces
            sem_c = c.get('semantics', {})
            df_c  = sem_c.get('dish_family', '') or ''
            if df_c in ('roti', 'paratha', 'bread', 'naan') or any(
                kw in food_name_lower for kw in ('roti', 'chapati', 'paratha', 'naan', 'bread', 'phulka')
            ):
                if unit in ('piece', 'pieces', 'unit', 'number', 'slice'):
                    p_max = min(p_max, 5.0)

            # Rice / Pulao / Biryani — max 3 bowls
            if df_c in ('rice', 'plain_rice', 'fried_rice', 'pulao', 'biryani') or any(
                kw in food_name_lower for kw in ('rice', 'pulao', 'biryani', 'khichdi')
            ):
                if unit in ('bowl', 'bowls', 'plate', 'plates'):
                    p_max = min(p_max, 3.0)

            # Dal / Curry / Sabzi / Paneer / Meat / Egg — max 3 bowls
            cat_c = sem_c.get('category', '') or ''
            if df_c in ('curry', 'dal', 'sambar', 'korma') or cat_c in (
                'Dal & Pulses', 'Chicken/Meat', 'Meat & Chicken', 'Paneer & Tofu', 'Eggs'
            ):
                if unit in ('bowl', 'bowls'):
                    p_max = min(p_max, 3.0)

            # Milk / Yogurt / Lassi / Drinks — max 2 glasses/cups
            if any(kw in food_name_lower for kw in ('milk', 'yogurt', 'lassi', 'drink', 'juice')):
                if unit in ('glass', 'glasses', 'cup', 'cups'):
                    p_max = min(p_max, 2.0)
            
            # Snapping min/pref/max to steps
            p_min = max(0.0, round(p_min / p_step) * p_step)
            p_pref = max(p_min, round(p_pref / p_step) * p_step)
            p_max = max(p_pref, round(p_max / p_step) * p_step)
            
            if unit in ('piece', 'pieces', 'unit', 'number', 'slice', 'sandwich', 'medium fruit'):
                p_min = max(1.0, p_min)
                p_pref = max(1.0, p_pref)
                p_max = max(1.0, p_max)
                
            if not nutrition and 'calories_kcal' in c:
                base_cal = float(c.get('calories_kcal', 0))
                base_pro = float(c.get('protein_g', 0))
            else:
                base_cal = float(nutrition.get('calories', 0))
                base_pro = float(nutrition.get('protein', 0))
                
            cal_per_unit = base_cal / db_base_qty if db_base_qty > 0 else 0
            pro_per_unit = base_pro / db_base_qty if db_base_qty > 0 else 0
            
            # Apply side foods calorie cap
            for cap_kw, cap_val in FOOD_CALORIE_CAPS.items():
                if cap_kw in food_name_lower and cal_per_unit > 0:
                    max_by_cap = cap_val / cal_per_unit
                    max_by_cap = max(p_min, round(max_by_cap / p_step) * p_step)
                    p_max = min(p_max, max_by_cap)
                    break
            
            priority = get_priority_level(c, unit)
            
            state.append({
                'raw_c': c,
                'p_min': p_min,
                'p_max': p_max,
                'p_step': p_step,
                'p_pref': p_pref,
                'cal_per_unit': cal_per_unit,
                'pro_per_unit': pro_per_unit,
                'base_qty': db_base_qty,
                'unit': unit,
                'priority': priority,
                'qty': p_pref # start at preferred
            })

        # 2. Initial Analytical Scaling (with Protein Awareness if target_pro is provided)
        current_cal = sum(s['qty'] * s['cal_per_unit'] for s in state)
        current_pro = sum(s['qty'] * s['pro_per_unit'] for s in state)
        
        if current_cal > 0 and target_cal > 0:
            if target_pro > 0:
                # Group items
                g1 = [s for s in state if s['priority'] == 1]
                g2 = [s for s in state if s['priority'] in (2, 3, 4)]
                g3 = [s for s in state if s['priority'] == 5]
                
                C_p = sum(s['qty'] * s['cal_per_unit'] for s in g1)
                P_p = sum(s['qty'] * s['pro_per_unit'] for s in g1)
                C_c = sum(s['qty'] * s['cal_per_unit'] for s in g2)
                P_c = sum(s['qty'] * s['pro_per_unit'] for s in g2)
                C_f = sum(s['qty'] * s['cal_per_unit'] for s in g3)
                P_f = sum(s['qty'] * s['pro_per_unit'] for s in g3)
                
                T_C = max(0.0, target_cal - C_f)
                T_P = max(0.0, target_pro - P_f)
                
                x_p, x_c = 1.0, 1.0
                if g1 and g2:
                    # Solve equations:
                    # x_p * C_p + x_c * C_c = T_C
                    # x_p * P_p + x_c * P_c = T_P
                    D = C_p * P_c - C_c * P_p
                    if abs(D) > 1e-4:
                        x_p = (T_C * P_c - T_P * C_c) / D
                        x_c = (C_p * T_P - P_p * T_C) / D
                    
                    # Fallback to decoupled heuristic if solved values are out of bounds or negative
                    if x_p < 0.1 or x_c < 0.1 or x_p > 5.0 or x_c > 5.0 or abs(D) <= 1e-4:
                        x_p = T_P / P_p if P_p > 0 else 1.0
                        remaining_cals = T_C - (x_p * C_p)
                        x_c = remaining_cals / C_c if C_c > 0 else 1.0
                else:
                    # Decoupled heuristic if only one group is present
                    x_p = T_P / P_p if P_p > 0 else 1.0
                    x_c = T_C / C_c if C_c > 0 else 1.0
                
                # Clamp multipliers to safe range
                x_p = max(0.2, min(5.0, x_p))
                x_c = max(0.2, min(5.0, x_c))
                
                # Apply multipliers and snap
                for s in state:
                    if s['priority'] == 1:
                        scaled_qty = s['qty'] * x_p
                    elif s['priority'] in (2, 3, 4):
                        scaled_qty = s['qty'] * x_c
                    else:
                        scaled_qty = s['qty']
                    
                    if s['priority'] < 5:
                        snapped = round(scaled_qty / s['p_step']) * s['p_step']
                        s['qty'] = max(s['p_min'], min(s['p_max'], snapped))
            else:
                # Standard calorie-only scaling
                ratio = target_cal / current_cal
                ratio = max(0.2, min(5.0, ratio))
                for s in state:
                    if s['priority'] < 5:
                        scaled_qty = s['qty'] * ratio
                        snapped = round(scaled_qty / s['p_step']) * s['p_step']
                        s['qty'] = max(s['p_min'], min(s['p_max'], snapped))
            
            # Recalculate current values
            current_cal = sum(s['qty'] * s['cal_per_unit'] for s in state)
            current_pro = sum(s['qty'] * s['pro_per_unit'] for s in state)

        # 3. Fine-tuning Greedy Scaling with Protein and Calorie Awareness
        if target_pro > 0:
            # ── Phase 1: Fine-tune Protein using Group 1 (Protein-rich foods) ──
            # Track the combination that minimises the protein error to avoid overshoot.
            best_pro_error = abs(sum(s['qty'] * s['pro_per_unit'] for s in state) - target_pro)
            best_pro_qtys  = [s['qty'] for s in state]

            for _ in range(15):
                current_pro = sum(s['qty'] * s['pro_per_unit'] for s in state)
                diff_pro = current_pro - target_pro
                if abs(diff_pro) <= 1.0:
                    break

                if diff_pro < 0: # Need more protein
                    increments = []
                    for idx, s in enumerate(state):
                        if s['priority'] == 1 and s['qty'] + s['p_step'] <= s['p_max']:
                            increments.append(idx)
                    if not increments:
                        break
                    # Sort increments by protein density (protein per calorie) descending
                    increments.sort(key=lambda idx: state[idx]['pro_per_unit'] / max(state[idx]['cal_per_unit'], 1.0), reverse=True)
                    state[increments[0]]['qty'] += state[increments[0]]['p_step']
                else: # Too much protein
                    decrements = []
                    for idx, s in enumerate(state):
                        if s['priority'] == 1 and s['qty'] - s['p_step'] >= s['p_min']:
                            decrements.append(idx)
                    if not decrements:
                        break
                    # Sort decrements by protein density ascending (to minimize calorie impact when dropping protein)
                    decrements.sort(key=lambda idx: state[idx]['pro_per_unit'] / max(state[idx]['cal_per_unit'], 1.0))
                    state[decrements[0]]['qty'] -= state[decrements[0]]['p_step']

                # Track best protein configuration
                current_error = abs(sum(s['qty'] * s['pro_per_unit'] for s in state) - target_pro)
                if current_error < best_pro_error:
                    best_pro_error = current_error
                    best_pro_qtys  = [s['qty'] for s in state]

            # Restore best protein quantities before calorie phase
            for s, qty in zip(state, best_pro_qtys):
                s['qty'] = qty

            # ── Phase 2: Fine-tune Calories using Group 2 (Carb/other foods) ──
            # Track the combination that minimises the combined calorie+protein error.
            best_combined_error = (
                abs(sum(s['qty'] * s['cal_per_unit'] for s in state) - target_cal) +
                abs(sum(s['qty'] * s['pro_per_unit'] for s in state) - target_pro)
            )
            best_combined_qtys = [s['qty'] for s in state]

            for _ in range(15):
                current_cal = sum(s['qty'] * s['cal_per_unit'] for s in state)
                diff_cal = current_cal - target_cal
                if abs(diff_cal) <= 10.0:
                    break

                if diff_cal < 0: # Need more calories
                    increments = []
                    for idx, s in enumerate(state):
                        if s['priority'] in (2, 3, 4) and s['qty'] + s['p_step'] <= s['p_max']:
                            increments.append(idx)
                    if not increments:
                        break
                    # Sort by priority, then least scaled ratio
                    increments.sort(key=lambda idx: (state[idx]['priority'], state[idx]['qty'] / state[idx]['p_pref']))
                    state[increments[0]]['qty'] += state[increments[0]]['p_step']
                else: # Too many calories
                    decrements = []
                    for idx, s in enumerate(state):
                        if s['priority'] in (2, 3, 4) and s['qty'] - s['p_step'] >= s['p_min']:
                            decrements.append(idx)
                    if not decrements:
                        break
                    # Sort by reverse priority, then most scaled ratio
                    decrements.sort(key=lambda idx: (-state[idx]['priority'], - (state[idx]['qty'] / state[idx]['p_pref'])))
                    state[decrements[0]]['qty'] -= state[decrements[0]]['p_step']

                # Track best combined configuration
                current_error = (
                    abs(sum(s['qty'] * s['cal_per_unit'] for s in state) - target_cal) +
                    abs(sum(s['qty'] * s['pro_per_unit'] for s in state) - target_pro)
                )
                if current_error < best_combined_error:
                    best_combined_error = current_error
                    best_combined_qtys  = [s['qty'] for s in state]

            # Restore the best overall combination before building the result
            for s, qty in zip(state, best_combined_qtys):
                s['qty'] = qty
        else:
            # Standard Calorie-only Greedy Fine-Tuning
            if current_cal < target_cal:
                while True:
                    increments = []
                    for idx, s in enumerate(state):
                        if s['qty'] + s['p_step'] <= s['p_max']:
                            increments.append(idx)
                    if not increments:
                        break
                    increments.sort(key=lambda idx: (state[idx]['priority'], state[idx]['qty'] / state[idx]['p_pref']))
                    best_idx = increments[0]
                    state[best_idx]['qty'] += state[best_idx]['p_step']
                    current_cal = sum(s['qty'] * s['cal_per_unit'] for s in state)
                    if current_cal >= target_cal:
                        break
            elif current_cal > target_cal:
                while True:
                    decrements = []
                    for idx, s in enumerate(state):
                        if s['qty'] - s['p_step'] >= s['p_min']:
                            decrements.append(idx)
                    if not decrements:
                        break
                    decrements.sort(key=lambda idx: (-state[idx]['priority'], - (state[idx]['qty'] / state[idx]['p_pref'])))
                    best_idx = decrements[0]
                    state[best_idx]['qty'] -= state[best_idx]['p_step']
                    current_cal = sum(s['qty'] * s['cal_per_unit'] for s in state)
                    if current_cal <= target_cal:
                        break

        # 3. Build Result list
        result = []
        for s in state:
            c = s['raw_c']
            qty = s['qty']
            unit = s['unit']
            
            if unit in ('piece', 'pieces', 'unit', 'number'):
                qty = max(1.0, round(qty))
                
            actual_scale = qty / s['base_qty'] if s['base_qty'] > 0 else 1.0
            
            nutrition = c.get('nutrition', {})
            if not nutrition and 'calories_kcal' in c:
                cal  = float(c.get('calories_kcal', 0)) * actual_scale
                prot = float(c.get('protein_g', 0)) * actual_scale
                carb = float(c.get('carbohydrates_g', 0)) * actual_scale
                fat  = float(c.get('fat_g', 0)) * actual_scale
                fiber = float(c.get('fiber_g', 0)) * actual_scale
            else:
                cal  = float(nutrition.get('calories', 0)) * actual_scale
                prot = float(nutrition.get('protein', 0)) * actual_scale
                carb = float(nutrition.get('carbs', 0)) * actual_scale
                fat  = float(nutrition.get('fat', 0)) * actual_scale
                fiber = float(nutrition.get('fiber', 0)) * actual_scale

            food_name = str(c.get('food_name', ''))
            serving_str = _format_serving(qty, unit, name=food_name, cal=cal)

            result.append({
                'food_id':      str(c.get('food_id', '')),
                'food_name':    food_name,
                'serving':      serving_str,
                'serving_qty':  qty,
                'serving_unit': unit,
                'calories':     round(cal,  1),
                'protein':      round(prot, 1),
                'carbs':        round(carb, 1),
                'fat':          round(fat,  1),
                'fiber':        round(fiber, 1),
                'nutrition': {
                    'calories': round(cal,  1),
                    'protein':  round(prot, 1),
                    'carbs':    round(carb, 1),
                    'fat':      round(fat,  1),
                    'fiber':    round(fiber, 1),
                },
                'semantics': c.get('semantics', {})
            })

        return result

def optimize_portions(components: List[Dict], target_cal: float) -> Tuple[List[Dict], float]:
    """
    Module-level function compatible with original (flat) portion optimizer.
    Returns a tuple of (flatized result list, sum of calories).
    """
    optimizer = PortionOptimizer()
    res = optimizer.optimize_portions(components, {"calories": target_cal, "protein": 0})
    
    flat_res = []
    final_cal = 0.0
    for idx, s in enumerate(res):
        c = components[idx]
        n = s['nutrition']
        flat_res.append({
            'food_id':      s['food_id'],
            'food_name':    s['food_name'],
            'serving':      s['serving'],
            'serving_qty':  s['serving_qty'],
            'serving_unit': s['serving_unit'],
            'calories':     n['calories'],
            'protein':      n['protein'],
            'carbs':        n['carbs'],
            'fat':          n['fat'],
            'fiber':        n['fiber'],
            'budget_level': str(c.get('budget_level', 'Low')),
            'availability': str(c.get('availability', 'common')),
            'swap_group':   str(c.get('swap_group', '')),
            'meal_role':    str(c.get('meal_role', '')),
            'region':       str(c.get('region', 'All India')),
            '_raw':         c,
            'semantics':    s.get('semantics', {})
        })
        final_cal += n['calories']
        
    return flat_res, final_cal
