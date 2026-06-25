import re
from typing import List, Dict, Tuple
from app.nutrition_engine.food_utils import get_primary_unit
from app.nutrition_engine.config import NUTRITION_RULES

# Per-food calorie caps: prevents any single side item from being over-scaled
# Keys are substrings matched against food_name.lower()
FOOD_CALORIE_CAPS = {
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
}

# Overrides for salad-like foods: max bowls regardless of protein target
SALAD_MAX_BOWLS = 1.5
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
                p_max = min(p_max, 1.0)
            if 'chutney' in food_name_lower or 'pickle' in food_name_lower:
                p_max = min(p_max, float(NUTRITION_RULES["portions"]["chutney_pickle_max_tbsp"]))
            if 'salad' in food_name_lower or 'raita' in food_name_lower:
                if unit in ('bowl', 'bowls', 'plate', 'plates'):
                    p_max = min(p_max, float(NUTRITION_RULES["portions"]["salad_raita_max_bowl"]))
            if any(drink in food_name_lower for drink in ('milkshake', 'smoothie', 'juice', 'drink', 'lassi', 'chaas', 'buttermilk', 'coffee', 'tea', 'water', 'lemonade')):
                if unit in ('glass', 'glasses', 'cup', 'cups', 'mug', 'mugs'):
                    p_max = min(p_max, 1.0)
                    
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
            
            # The actual base qty dictated by the meal identity
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
                p_min = float(portion_rules.get('min_qty', internal_ratio * 0.5))
                p_max = float(portion_rules.get('max_qty', internal_ratio * 2.0))
            else:
                p_min = float(get_val(['minimum', 'portion_min'], internal_ratio * 0.5) or internal_ratio * 0.5)
                p_max = float(get_val(['maximum', 'portion_max'], internal_ratio * 2.0) or internal_ratio * 2.0)
                p_max = max(p_max, internal_ratio * 5.0)
                
            food_name_lower = str(c.get('food_name', '')).lower()
            if 'whey' in food_name_lower or 'protein powder' in food_name_lower:
                p_max = min(p_max, 1.0) # Cap at 1 scoop/glass
            if 'chutney' in food_name_lower or 'pickle' in food_name_lower:
                p_max = min(p_max, float(NUTRITION_RULES["portions"]["chutney_pickle_max_tbsp"])) # Max 2 tbsp
            if any(kw in food_name_lower for kw in SALAD_KEYWORDS):
                if unit in ('bowl', 'bowls', 'plate', 'plates'):
                    p_max = min(p_max, SALAD_MAX_BOWLS)  # Max 1.5 bowl for salad/raita
                    p_min = max(0.5, p_min)              # Min 0.5 bowl
            elif 'salad' in food_name_lower or 'raita' in food_name_lower:
                if unit in ('bowl', 'bowls', 'plate', 'plates'):
                    p_max = min(p_max, float(NUTRITION_RULES["portions"]["salad_raita_max_bowl"])) # Max 1 bowl/plate
            if any(drink in food_name_lower for drink in ('milkshake', 'smoothie', 'juice', 'drink', 'lassi', 'chaas', 'buttermilk', 'coffee', 'tea', 'water', 'lemonade')):
                if unit in ('glass', 'glasses', 'cup', 'cups', 'mug', 'mugs'):
                    p_max = min(p_max, 1.0) # Cap at 1 glass/cup for drinks
                
            if unit in ('piece', 'pieces', 'unit', 'number', 'slice', 'sandwich', 'medium fruit'):
                p_step = 1.0
            elif unit in ('bowl', 'bowls', 'plate', 'plates', 'glass', 'glasses', 'tbsp', 'tsp', 'scoop'):
                p_step = 0.5
            else:
                p_step = 10.0 if unit in ('g', 'ml') else 1.0

            if unit != db_unit and internal_ratio > 0:
                base_qty = internal_ratio
            else:
                base_qty = db_base_qty
            
            p_step = max(0.01, p_step)
            
            if unit in ('piece', 'pieces', 'unit', 'number', 'slice', 'sandwich', 'medium fruit'):
                p_step = max(1.0, round(p_step))
                p_min = max(1.0, round(p_min))
                
            if not nutrition and 'calories_kcal' in c:
                base_cal = float(c.get('calories_kcal', 0))
                base_pro = float(c.get('protein_g', 0))
            else:
                base_cal = float(nutrition.get('calories', 0))
                base_pro = float(nutrition.get('protein', 0))
                
            cal_per_unit = base_cal / base_qty if base_qty > 0 else 0
            pro_per_unit = base_pro / base_qty if base_qty > 0 else 0
            
            portion_profile = _get_portion_profile(food_name_lower, unit, base_qty)
            
            state.append({
                'raw_c': c,
                'internal_ratio': internal_ratio,
                'p_min': p_min,
                'p_max': p_max,
                'p_step': p_step,
                'portion_profile': portion_profile,
                'cal_per_unit': cal_per_unit,
                'pro_per_unit': pro_per_unit,
                'base_qty': base_qty,
                'unit': unit,
                'qty': internal_ratio
            })

        # Priority Order Scaling & Independent Multipliers
        best_score = float('-inf')
        best_state = []
        
        multipliers = [0.5, 0.75, 1.0, 1.25, 1.5, 1.75, 2.0, 2.5]
        
        for m_pro in multipliers:
            for m_carb in multipliers:
                for m_other in multipliers:
                    current_state = []
                    total_cal = 0.0
                    total_pro = 0.0
                    
                    for s in state:
                        c_raw = s['raw_c']
                        cat = c_raw.get('semantics', {}).get('category', '')
                        pdensity = c_raw.get('semantics', {}).get('protein_density', 0)
                        
                        if pdensity > 0.12 or cat in ['Dal & Pulses', 'Paneer & Tofu', 'Meat & Chicken', 'Eggs', 'Seafood', 'Dairy']:
                            m = m_pro
                        elif cat in ['Rice', 'Whole Grains', 'Millets & Whole Grains', 'Breakfast', 'Breads & Roti', 'Oats & Cereals']:
                            m = m_carb
                        else:
                            m = min(m_other, float(NUTRITION_RULES["portions"]["side_dish_multiplier_max"]))
                            
                        raw_qty = s['internal_ratio'] * m
                        # Household bounds snapping
                        portion_profile = s.get('portion_profile')
                        if portion_profile:
                            stepped_qty = min(portion_profile, key=lambda x: abs(x - raw_qty))
                        else:
                            step = s['p_step']
                            stepped_qty = round(raw_qty / step) * step
                        
                        # Apply ±20% household bound preference (soft penalty below) and hard p_min/p_max
                        clamped_qty = max(s['p_min'], min(s['p_max'], stepped_qty))
                        
                        cal = clamped_qty * s['cal_per_unit']
                        pro = clamped_qty * s['pro_per_unit']

                        # ── Calorie cap for side foods (salad, raita, chutney, etc.) ─────
                        food_name_check = str(s['raw_c'].get('food_name', '')).lower()
                        for cap_kw, cap_val in FOOD_CALORIE_CAPS.items():
                            if cap_kw in food_name_check and cal > cap_val and s['cal_per_unit'] > 0:
                                capped_qty = cap_val / s['cal_per_unit']
                                # Round capped_qty to nearest step
                                step = s['p_step']
                                capped_qty = max(s['p_min'], min(s['p_max'], round(capped_qty / step) * step))
                                cal = capped_qty * s['cal_per_unit']
                                pro = capped_qty * s['pro_per_unit']
                                clamped_qty = capped_qty
                                break
                        
                        current_state.append({
                            'qty': clamped_qty,
                            'cal': cal,
                            'pro': pro,
                            'm': m
                        })
                        total_cal += cal
                        total_pro += pro
                        
                    # Score this combination
                    cal_diff = abs(total_cal - target_cal) / target_cal if target_cal > 0 else 0
                    pro_diff = abs(total_pro - target_pro) / target_pro if target_pro > 0 else 0
                    
                    score = -(cal_diff * 2.0 + pro_diff * 1.5)
                    
                    # Penalize divergence between plate components (we want balanced meals)
                    divergence = abs(m_pro - m_carb) + abs(m_carb - m_other)
                    score -= (divergence * 0.2)
                    
                    # Penalize straying too far from household base (1.0)
                    deviation = abs(m_pro - 1.0) + abs(m_carb - 1.0) + abs(m_other - 1.0)
                    score -= (deviation * 0.1)
                    
                    if total_pro < target_pro * 0.8:
                        score -= 10.0
                        
                    if total_cal > target_cal * 1.15:
                        score -= 10.0
                        
                    if score > best_score:
                        best_score = score
                        best_state = current_state
                        
        if not best_state:
            # Fallback
            best_state = [{'qty': s['internal_ratio']} for s in state]

        result = []
        for idx, s in enumerate(state):
            c = s['raw_c']
            qty = best_state[idx]['qty']
            unit = s['unit']
            
            if unit in ('piece', 'pieces', 'unit', 'number'):
                qty = max(1, round(qty))
                
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
