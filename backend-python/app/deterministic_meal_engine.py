"""
Meal Engine V2  — 8-Phase Production Implementation
Follows ELEVATE AI NUTRITION SYSTEM — MEAL ENGINE V2 IMPLEMENTATION SPECIFICATION v2.0

Phases implemented:
  Phase 1  — Weekly Variety Engine (history, protein/carb/cuisine/template rotation)
  Phase 2  — Portion Optimizer (stepped, clamped, realistic servings)
  Phase 3  — Meal Completeness Engine (blueprints, role validation)
  Phase 4  — Meal Template Engine (predefined templates, rotation)
  Phase 5  — Smart Meal Swap Engine (role-compatible, nutrition-similar swaps)
  Phase 6  — Meal Scoring Engine (30–50 candidates, weighted scoring)
  Phase 7  — Budget & Availability Engine (priority-based selection)
  Phase 8  — Weekly Validator (duplicate, portion, budget, nutrition checks)
"""
import pandas as pd
import numpy as np
from datetime import datetime, timezone
from typing import Dict, List, Optional, Tuple, Set
import os
import random
import hashlib
import re
from collections import Counter, deque
import json
import math


# ---------------------------------------------------------------------------
# MODULE-LEVEL CONSTANTS
# ---------------------------------------------------------------------------

MEAL_DISTRIBUTION = {
    'breakfast': 0.25,
    'lunch':     0.35,
    'dinner':    0.28,
    'snack':     0.12,
}

# Blueprints: each entry is a list of required meal_roles for a meal slot.
# The engine picks a random blueprint then fills each role from the food pool.
BLUEPRINTS = {
    'breakfast': [
        ['protein_main', 'carb_base', 'beverage'],
        ['combo_meal', 'beverage'],
        ['combo_meal', 'snack_fruit'],
        ['combo_meal', 'condiment', 'beverage'],
    ],
    'lunch': [
        ['carb_base', 'protein_main', 'veg_side', 'salad', 'dairy_side'],
        ['carb_base', 'protein_main', 'veg_side', 'salad'],
        ['combo_meal', 'dairy_side', 'salad'],
        ['combo_meal', 'salad'],
        ['combo_meal', 'condiment', 'salad'],
    ],
    'dinner': [
        ['protein_main', 'veg_side', 'carb_base'],
        ['combo_meal', 'dairy_side'],
        ['combo_meal'],
        ['combo_meal', 'condiment'],
    ],
    'snack': [
        ['snack_fruit', 'snack'],
        ['snack'],
        ['beverage', 'snack'],
    ],
}

# Availability scoring weights
AVAILABILITY_SCORE = {
    'very_common': 10,
    'common':       7,
    'limited':      3,
    'rare':         0,
}

BUDGET_SCORE = {
    'Low':    10,
    'Medium':  6,
    'High':    2,
}

# Cuisine/region bonus for variety
REGION_ALIASES = {
    'North India':      'North Indian',
    'South India':      'South Indian',
    'East India':       'East Indian',
    'West India':       'West Indian',
    'Northeastern India': 'North East Indian',
    'Northeast India':  'North East Indian',
    'All India':        'Pan Indian',
}

# Foods to exclude from recommendations — unrealistic for daily meal planning
# Words that identify a food as a non-meal (raw bases, desserts, sugary drinks).
# NOTE: overly-broad descriptors were removed because they falsely rejected healthy
# composite dishes (verified against nutrition_production_final_v4.csv):
#   - 'sauce'   matched 17 valid mains (e.g. "Paneer In Butter Sauce",
#               "Baked Eggs In Tomato Sauce", "Spaghetti With Paneer Balls...").
#   - 'filling' was redundant with the more-specific 'curd filling' (same 2 dessert
#               items) while risking future false positives.
# Genuine unhealthy/non-meal filters are intentionally retained below.
FOOD_NAME_BLOCKLIST = [
    'stock', 'consomme', 'icing', 'gateau', 'fondant', 'aspic',
    'gelatin', 'sorbet', 'mousse', 'truffle', 'caviar', 'foie gras',
    'jam', 'jelly', 'syrup', 'punch', 'fruit squash', 'drink squash', 'cordial',
    'fudge', 'frosting', 'glaze', 'curd filling'
]


# ---------------------------------------------------------------------------
# PHASE 1 — WEEKLY VARIETY TRACKER
# ---------------------------------------------------------------------------

class WeeklyVarietyTracker:
    """
    Tracks what has been used across the full week so the engine can
    penalise repeats when scoring candidates.
    """
    def __init__(self):
        self.breakfast_history:  Set[str] = set()
        self.lunch_history:      Set[str] = set()
        self.dinner_history:     Set[str] = set()
        self.snack_history:      Set[str] = set()
        self.protein_history:    List[str] = []
        self.carb_history:       List[str] = []
        self.cuisine_history:    List[str] = []
        self.template_history:   List[int] = []   # blueprint indices used
        self.family_history:     List[str] = []   # track broad food families

    def meal_history(self, meal_type: str) -> Set[str]:
        return getattr(self, f'{meal_type}_history', set())

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


# ---------------------------------------------------------------------------
# PHASE 2 — PORTION OPTIMIZER
# ---------------------------------------------------------------------------

def get_food_family(name: str, swap_group: str) -> str:
    n = str(name).lower()
    sg = str(swap_group).lower()
    
    if 'sandwich' in n: return 'Sandwich'
    if 'salad' in n or 'kosambari' in n: return 'Salad'
    if 'raita' in n or 'pachadi' in n: return 'Raita'
    if 'soup' in n or 'shorba' in n or 'broth' in n: return 'Soup'
    if 'milkshake' in n or 'smoothie' in n or 'lassi' in n or 'drink' in n or 'juice' in n: return 'Drink'
    if 'fruit' in n or sg == 'fruits': return 'Fruit'
    if sg == 'yogurt/curd' or 'curd' in n or 'yogurt' in n: return 'Yogurt'
    if 'oats' in n or 'oatmeal' in n or 'porridge' in n or 'muesli' in n: return 'Oats'
    if 'dosa' in n or 'idli' in n or 'uttapam' in n or 'paniyaram' in n: return 'South Indian Breakfast'
    if 'paratha' in n or 'thepla' in n or 'cheela' in n or 'chilla' in n: return 'North Indian Breakfast'
    if 'khichdi' in n or 'biryani' in n or 'pulao' in n or 'rice' in n or 'bisi bele' in n: return 'Cooked Staple'
    if 'roti' in n or 'chapati' in n or 'phulka' in n or 'naan' in n: return 'Cooked Staple'
    if 'dal' in n or 'lentil' in n or 'sambar' in n or 'rasam' in n: return 'Cooked Staple'
    if 'chicken' in n or sg == 'chicken/meat': return 'Cooked Staple'
    if 'fish' in n or sg == 'fish & seafood': return 'Cooked Staple'
    if 'paneer' in n or sg == 'paneer': return 'Cooked Staple'
    if 'egg' in n or sg == 'eggs': return 'Cooked Staple'
    if 'sabzi' in n or 'curry' in n or sg == 'vegetable': return 'Cooked Staple'
    if 'pasta' in n or 'noodles' in n or 'thukpa' in n: return 'Cooked Staple'
    
    return sg.title() if sg else 'Other'

def is_realistic_meal_identity(meal_type: str, components: List[pd.Series]) -> bool:
    """
    Validates if the generated meal combinations make sense for the target meal.
    Prevents e.g. Lunch/Dinner being just a Sandwich + Drink.
    """
    if meal_type.lower() not in ('lunch', 'dinner'):
        return True
        
    families = [get_food_family(str(c.get('food_name', '')), str(c.get('swap_group', ''))) for c in components]
    
    # Lunch/Dinner must contain a Cooked Staple if it uses Breakfast/Snack mains
    if 'Sandwich' in families or 'Milkshake' in families or 'Oats' in families or 'Drink' in families or 'South Indian Breakfast' in families or 'North Indian Breakfast' in families:
        if 'Cooked Staple' not in families:
            return False
            
    return True

def optimize_portions(components: List[pd.Series],
                      target_cal: float) -> Tuple[List[Dict], float]:
    """
    Step-based portion optimizer. No continuous multiplier scaling.
    Steps portions incrementally until target_cal is reached or all max out.
    """
    if not components:
        return [], 0.0

    state = []
    total_cal = 0.0
    for c in components:
        base_qty  = float(c.get('serving_quantity', 1) or 1)
        p_min  = float(c.get('portion_min',  base_qty * 0.5) or 1)
        p_max  = float(c.get('portion_max',  base_qty * 2.0) or base_qty * 2)
        p_step = float(c.get('portion_step', 1) or 1)
        p_step = max(0.01, p_step)
        
        if c.get('serving_unit', '') in ('piece', 'pieces', 'unit', 'number'):
            p_step = max(1.0, round(p_step))
            p_min = max(1.0, round(p_min))
            p_max = max(1.0, round(p_max))
            
        family = get_food_family(str(c.get('food_name', '')), str(c.get('swap_group', '')))
        
            
        base_cal = float(c.get('calories_kcal', 0))
        cal_per_unit = base_cal / base_qty if base_qty > 0 else 0
        
        current_qty = p_min
        current_cal = current_qty * cal_per_unit
        
        state.append({
            'raw_c': c,
            'qty': current_qty,
            'p_min': p_min,
            'p_max': p_max,
            'p_step': p_step,
            'cal_per_unit': cal_per_unit,
            'base_qty': base_qty,
            'cal': current_cal
        })
        total_cal += current_cal
        
    loop_count = 0
    while total_cal < target_cal and loop_count < 1000:
        loop_count += 1
        steppable = [s for s in state if s['qty'] + s['p_step'] <= s['p_max'] * 1.001 and s['cal_per_unit'] > 0]
        if not steppable:
            break
            
        steppable.sort(key=lambda s: s['cal'])
        target_item = steppable[0]
        
        deficit = target_cal - total_cal
        cal_per_step = target_item['p_step'] * target_item['cal_per_unit']
        max_steps = int(round((target_item['p_max'] - target_item['qty']) / target_item['p_step']))
        
        if cal_per_step > 0:
            steps_needed = max(1, int(deficit / cal_per_step))
        else:
            steps_needed = 1
            
        jump_steps = min(max_steps, steps_needed)
        if jump_steps < 1:
            jump_steps = 1
            
        target_item['qty'] += target_item['p_step'] * jump_steps
        added_cal = (target_item['p_step'] * jump_steps) * target_item['cal_per_unit']
        target_item['cal'] += added_cal
        total_cal += added_cal
        
    result = []
    final_cal = 0.0
    for s in state:
        c = s['raw_c']
        qty = s['qty']
        
        if c.get('serving_unit', '') in ('piece', 'pieces', 'unit', 'number'):
            qty = max(1, round(qty))
            
        actual_scale = qty / s['base_qty'] if s['base_qty'] > 0 else 1.0
        cal  = float(c.get('calories_kcal', 0)) * actual_scale
        prot = float(c.get('protein_g',     0)) * actual_scale
        carb = float(c.get('carbohydrates_g', 0)) * actual_scale
        fat  = float(c.get('fat_g',          0)) * actual_scale
        final_cal += cal

        unit = str(c.get('serving_unit', 'g'))
        serving_str = _format_serving(qty, unit, name=str(c.get('food_name', '')), cal=cal)

        result.append({
            'food_id':      str(c.get('food_id', '')),
            'food_name':    str(c.get('food_name', '')),
            'serving':      serving_str,
            'serving_qty':  qty,
            'serving_unit': unit,
            'calories':     round(cal,  1),
            'protein':      round(prot, 1),
            'carbs':        round(carb, 1),
            'fat':          round(fat,  1),
            'budget_level': str(c.get('budget_level', 'Low')),
            'availability': str(c.get('availability', 'common')),
            'swap_group':   str(c.get('swap_group', '')),
            'meal_role':    str(c.get('meal_role', '')),
            'region':       str(c.get('region', 'All India')),
            '_raw':         c,   # kept for swap engine; stripped before output
        })

    return result, final_cal


import re

def _format_serving(qty: float, unit: str, name: str = '', cal: float = 0.0) -> str:
    """Produce a human-readable serving string based on food type and calories."""
    name_lower = str(name).lower() if name else ''
    cal = float(cal) if cal else 0.0
    qty = float(qty) if qty else 0.0
    
    # If explicitly pieces
    if unit in ('piece', 'pieces', 'unit', 'number'):
        n = int(qty)
        label = 'piece' if n == 1 else 'pieces'
        return f"{n} {label}"
        
    # If no name or calories provided, fallback to basic formatting
    if not name_lower or cal <= 0:
        if unit in ('g', 'ml'):
            return f"{int(qty)}{unit}"
        return f"{qty:g} {unit}"

    # 1. Eggs
    if 'egg' in name_lower or 'anda' in name_lower:
        p = max(1, round(cal / 70))
        return f"{p} piece{'s' if p > 1 else ''} (egg)"
        
    # 2. Roti / Chapati / Paratha / Naan / Bread
    if any(x in name_lower for x in ['roti', 'chapati', 'phulka']):
        p = max(1, round(cal / 85))
        return f"{p} piece{'s' if p > 1 else ''} (roti)"
    if 'paratha' in name_lower or 'parantha' in name_lower:
        p = max(1, round(cal / 180))
        return f"{p} piece{'s' if p > 1 else ''} (paratha)"
    if 'naan' in name_lower:
        p = max(0.5, round(cal / 250 * 2) / 2)
        return f"{p:g} piece{'s' if p > 1 else ''} (naan)"
    if 'bread' in name_lower or 'toast' in name_lower:
        p = max(1, round(cal / 80))
        return f"{p} slice{'s' if p > 1 else ''}"
        
    # 3. Idli / Dosa / Uttapam / Vada
    if 'idli' in name_lower:
        p = max(1, round(cal / 65))
        return f"{p} piece{'s' if p > 1 else ''}"
    if 'dosa' in name_lower:
        p = max(1, round(cal / 150))
        return f"{p} piece{'s' if p > 1 else ''} (dosa)"
    if 'vada' in name_lower:
        p = max(1, round(cal / 100))
        return f"{p} piece{'s' if p > 1 else ''}"
    if 'uttapam' in name_lower:
        p = max(0.5, round(cal / 200 * 2) / 2)
        return f"{p:g} piece{'s' if p > 1 else ''}"
        
    # 4. Whole fruits
    if re.search(r'apple|banana|orange|fruit\s*\(', name_lower):
        p = max(1, round(cal / 85))
        return f"{p} medium fruit{'s' if p > 1 else ''}"
        
    # 5. Beverages
    if re.search(r'juice|milk|smoothie|drink|shake|lassi|chaas|lemonade', name_lower):
        is_rich = bool(re.search(r'lassi|shake|milk|smoothie', name_lower))
        base_cal = 150 if is_rich else 80
        glasses = round(cal / base_cal * 2) / 2
        if glasses >= 1:
            return f"{glasses:g} glass{'es' if glasses > 1 else ''} (~{int(glasses * 250)}ml)"
        return f"~{int(cal * 2)}ml"
        
    # 6. Tea & Coffee
    if any(x in name_lower for x in ['tea', 'coffee', 'chai']):
        cups = max(0.5, round(cal / 60 * 2) / 2)
        return f"{cups:g} cup{'s' if cups > 1 else ''}"
        
    # 7. Dal, Sambar, Kadhi, Soups, Salad, Yogurt, Raita
    if re.search(r'dal|sambar|kadhi|soup|shorba|raita|yogurt|curd|salad', name_lower):
        is_heavy = bool(re.search(r'dal|sambar|kadhi|soup|shorba', name_lower))
        base_cal = 120 if is_heavy else 70
        bowls = max(0.5, round(cal / base_cal * 2) / 2)
        return f"{bowls:g} bowl{'s' if bowls > 1 else ''}"
        
    # 8. Rice, Pulao, Biryani, Noodles, Pasta
    if re.search(r'rice|pulao|biryani|noodle|pasta|spaghetti|macaroni|chowmein', name_lower):
        plates = max(0.5, round(cal / 200 * 2) / 2)
        return f"{plates:g} plate{'s' if plates > 1 else ''}"
        
    # 9. Protein Bars
    if 'bar' in name_lower:
        p = max(1, round(cal / 200))
        return f"{p} bar{'s' if p > 1 else ''}"
        
    # 10. Nuts & Seeds
    if re.search(r'almonds|walnuts|cashew|nuts|seeds', name_lower):
        handfuls = round(cal / 160 * 2) / 2
        g = int(round(cal / 160 * 28))
        if handfuls >= 1:
            return f"{handfuls:g} handful{'s' if handfuls > 1 else ''} (~{g}g)"
        return f"~{g}g"
        
    # Fallback for G / ML
    if unit in ('g', 'ml'):
        # For foods not caught above, format as `[X]g`
        return f"{int(qty)}{unit}"
        
    # Basic fallback
    n = f"{qty:.1f}".rstrip('0').rstrip('.')
    return f"{n} {unit}"


# ---------------------------------------------------------------------------
# PHASE 6 — MEAL SCORER
# ---------------------------------------------------------------------------

def score_meal(components: List[Dict],
               meal_cal: float,
               target_cal: float,
               variety_tracker: WeeklyVarietyTracker,
               meal_type: str,
               bp_idx: int) -> float:
    """
    Score a candidate meal (0–100).
    Weights per spec:
        Macro accuracy   30%
        Weekly variety   20%
        Meal completeness 15%
        Portion realism  10%
        Budget           10%
        Availability     10%
        Cuisine rotation  5%
    """
    score = 100.0

    # 1. Macro Accuracy (30 pts)
    if target_cal > 0:
        cal_err = abs(meal_cal - target_cal) / target_cal
        score -= min(30, cal_err * 60)

    # 2. Weekly Variety (20 pts) — subtract variety_penalty capped at 20
    if components:
        region = components[0].get('region', 'All India')
        vp = variety_tracker.variety_penalty(meal_type, components, bp_idx, region)
        score -= min(20, vp * 0.3)   # scale down since raw penalty can be high

    # 3. Meal Completeness (15 pts)
    roles = {c['meal_role'] for c in components}
    has_protein = bool(roles & {'protein_main', 'combo_meal'})
    has_carb    = bool(roles & {'carb_base', 'combo_meal'})
    if not has_protein:
        score -= 15
    if not has_carb and meal_type not in ('snack',):
        score -= 10

    # 4. Portion Realism (10 pts) — penalise components at their min/max boundary
    at_boundary = sum(
        1 for c in components
        if c.get('serving_qty', 0) in (
            float(c['_raw'].get('portion_min', 0)),
            float(c['_raw'].get('portion_max', 9999))
        )
    )
    score -= min(10, at_boundary * 3)

    # 5. Budget (10 pts)
    budget_pts = [BUDGET_SCORE.get(c.get('budget_level', 'Low'), 5) for c in components]
    avg_budget = sum(budget_pts) / max(len(budget_pts), 1)
    score += (avg_budget / 10) * 10 - 10   # normalize; contributes -10 to +10

    # 6. Availability (10 pts)
    avail_pts = [AVAILABILITY_SCORE.get(c.get('availability', 'common'), 5) for c in components]
    avg_avail = sum(avail_pts) / max(len(avail_pts), 1)
    score += (avg_avail / 10) * 10 - 10

    # 7. Cuisine rotation (5 pts)
    if components:
        region = components[0].get('region', 'All India')
        r = REGION_ALIASES.get(region, region)
        freq = variety_tracker.cuisine_history.count(r)
        score -= min(5, freq * 2)

    return max(0.0, score)


# ---------------------------------------------------------------------------
# PHASE 5 — SWAP ENGINE
# ---------------------------------------------------------------------------

def build_swap_options(component: Dict,
                       pool: pd.DataFrame,
                       profile: Dict,
                       meal_time: str = '',
                       limit: int = 4) -> List[Dict]:
    """
    Generate swap options for a single meal component.
    Rules: same meal_role, same meal_time, diet-compatible, allergy-free, ±30% calories,
    prefer common/low-budget.
    """
    role      = component.get('meal_role', '')
    sg        = component.get('swap_group', '')
    cal_ref   = component.get('calories', 0)
    food_name = component.get('food_name', '')

    # We convert to a list of dicts for much faster filtering compared to DataFrame masks
    # Only pick rows matching role
    role_mask = (pool['meal_role'] == role) & (pool['food_name'] != food_name)
    candidates_df = pool[role_mask]
    
    if candidates_df.empty:
        return []
        
    # Convert to native list of dicts for fast iteration
    candidates = candidates_df.to_dict('records')

    # Filter by meal_type to avoid cross-meal swaps (e.g. dinner biryani in breakfast swap)
    if meal_time:
        mt_cap = meal_time.capitalize()
        # Case insensitive check
        meal_filtered = [c for c in candidates if c.get('meal_type') and mt_cap.lower() in str(c.get('meal_type')).lower()]
        if meal_filtered:
            candidates = meal_filtered

    if not candidates:
        return []

    # Nutrition similarity filter — try tight window first, then widen
    if cal_ref > 0:
        tight = [c for c in candidates if cal_ref * 0.70 <= float(c.get('calories_kcal', 0)) <= cal_ref * 1.30]
        wide = [c for c in candidates if cal_ref * 0.40 <= float(c.get('calories_kcal', 0)) <= cal_ref * 1.60]
        
        if len(tight) >= 2:
            candidates = tight
        elif wide:
            candidates = wide

    # Prefer same swap_group first
    same_sg = []
    other_sg = []
    for c in candidates:
        if c.get('swap_group') == sg:
            same_sg.append(c)
        else:
            other_sg.append(c)

    # Score by availability + budget
    for c in same_sg + other_sg:
        c['_swap_score'] = AVAILABILITY_SCORE.get(c.get('availability', 'common'), 5) + \
                           BUDGET_SCORE.get(c.get('budget_level', 'Low'), 5)

    same_sg.sort(key=lambda x: x.get('_swap_score', 0), reverse=True)
    other_sg.sort(key=lambda x: x.get('_swap_score', 0), reverse=True)

    candidates = same_sg + other_sg

    # Take top N
    candidates = candidates[:limit]

    # Convert numeric values that were float64 to python floats for JSON safety
    for c in candidates:
        c['swap_group'] = sg  # ensure swap_group is preserved
        c['_raw'] = c.copy()

    return candidates

    options = []
    for _, row in candidates.head(limit * 2).iterrows():
        cand_cal = float(row.get('calories_kcal', 1))
        cand_cal = cand_cal if cand_cal > 0 else 1.0
        
        # Determine the ideal multiplier to match calories
        ideal_m = cal_ref / cand_cal if cal_ref > 0 else 1.0
        
        # Snap to valid portion step
        base_qty = float(row.get('serving_quantity', 1) or 1)
        p_step = float(row.get('portion_step', base_qty * 0.5) or base_qty * 0.5)
        p_min = float(row.get('portion_min', base_qty * 0.5) or base_qty * 0.5)
        p_max = float(row.get('portion_max', base_qty * 3.0) or base_qty * 3.0)
        
        # If the unit is piece/unit, force step to integer
        if str(row.get('serving_unit', '')).lower() in ('piece', 'pieces', 'unit', 'number'):
            p_step = max(1.0, round(p_step))
            p_min = max(1.0, round(p_min))
            p_max = max(1.0, round(p_max))
            
        # Calculate multiplier that represents the actual physical steps
        # Note: p_step in metadata is in the same unit as serving_quantity. 
        # So we figure out the ideal raw quantity, snap it to step, then find the true multiplier.
        ideal_qty = base_qty * ideal_m
        snapped_qty = max(p_min, min(p_max, round(ideal_qty / p_step) * p_step))
        
        true_m = snapped_qty / base_qty if base_qty > 0 else 1.0
        
        options.append({
            'food_id':   str(row['food_id']),
            'name':      str(row['food_name']),
            'food_name': str(row['food_name']),
            'serving':   _format_serving(snapped_qty, str(row.get('serving_unit', 'g')), name=str(row['food_name']), cal=round(cand_cal * true_m)),
            'serving_weight': snapped_qty,
            'serving_qty': snapped_qty,
            'serving_unit': str(row.get('serving_unit', 'g')),
            'calories':  round(cand_cal * true_m),
            'protein':   round(float(row.get('protein_g', 0)) * true_m, 1),
            'carbs':     round(float(row.get('carbohydrates_g', 0)) * true_m, 1),
            'fat':       round(float(row.get('fat_g', 0)) * true_m, 1),
        })
        if len(options) >= limit:
            break

    return options



# ---------------------------------------------------------------------------
# MAIN ENGINE CLASS
# ---------------------------------------------------------------------------

class MealEngine:
    """
    V2 Production Meal Engine implementing all 8 spec phases.
    """
    
    _cached_df = None

    def __init__(self,
                 nutrition_data_path: str = None,
                 metadata_path:       str = None):
        
        if MealEngine._cached_df is not None:
            self.df = MealEngine._cached_df.copy()
        else:
            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

            csv_path = nutrition_data_path or os.path.join(
                base_dir, 'data', 'nutrition_production_final_v4.csv')
            if not os.path.exists(csv_path):
                raise FileNotFoundError(f"Nutrition dataset not found: {csv_path}")

            meta_path = metadata_path or os.path.join(
                base_dir, 'data', 'meal_metadata.csv')
            if not os.path.exists(meta_path):
                raise FileNotFoundError(f"Metadata not found: {meta_path}")

            df_nutr = pd.read_csv(csv_path)
            df_meta = pd.read_csv(meta_path)

            # Normalise string columns
            for col in ['diet_type', 'allergens', 'goal', 'meal_type', 'region']:
                if col in df_nutr.columns:
                    df_nutr[col] = df_nutr[col].fillna('').astype(str)

            # Inner join on food_id
            self.df = pd.merge(df_nutr, df_meta, on='food_id', how='inner')
            # Drop desserts, spreads, sauces — never appear as base meals
            forbidden_roles = ['side_dish', 'dessert', 'spread', 'sauce', 'sweet']
            self.df = self.df[~self.df['meal_role'].isin(forbidden_roles)]
            print(f"[MealEngine V2] Loaded {len(self.df)} foods (post-merge)")
            MealEngine._cached_df = self.df.copy()

        self.breakfast_history:  Set[str] = set()
        self.lunch_history:      Set[str] = set()
        self.dinner_history:     Set[str] = set()
        self.snack_history:      Set[str] = set()
        self.protein_history:    List[str] = []
        self.carb_history:       List[str] = []
        self.cuisine_history:    List[str] = []
        self.template_history:   List[int] = []   # blueprint indices used

        # ---- Calorie / macro target parameters ----
        self._protein_per_kg = {
            'Weight Loss':  1.6,
            'Fat Loss':     1.8,
            'Muscle Gain':  1.8,
            'Strength':     1.8,
            'Endurance':    1.4,
            'Maintenance':  1.0,
            'Maintain':     1.0,
        }
        self._carb_fat_split = {
            'Weight Loss':  {'carbs': 0.50, 'fat': 0.50},
            'Fat Loss':     {'carbs': 0.40, 'fat': 0.60},
            'Muscle Gain':  {'carbs': 0.65, 'fat': 0.35},
            'Strength':     {'carbs': 0.70, 'fat': 0.30},
            'Endurance':    {'carbs': 0.75, 'fat': 0.25},
            'Maintenance':  {'carbs': 0.58, 'fat': 0.42},
            'Maintain':     {'carbs': 0.58, 'fat': 0.42},
        }
        self._activity_mult = {
            'Sedentary':   1.2,
            'Light':       1.375,
            'Moderate':    1.55,
            'Active':      1.725,
            'Very Active': 1.9,
        }

    # ------------------------------------------------------------------
    # HELPERS — determinism
    # ------------------------------------------------------------------

    def _user_entropy(self, profile: Dict) -> str:
        parts = [
            str(profile.get('user_id') or profile.get('_id') or '').strip(),
            str(profile.get('email') or '').strip().lower(),
            str(profile.get('created_at') or profile.get('createdAt') or '').strip(),
        ]
        raw = '|'.join(parts)
        if not raw.replace('|', '').strip():
            raw = 'anonymous-user'
        return hashlib.sha256(raw.encode()).hexdigest()[:24]

    def _profile_fp(self, profile: Dict) -> str:
        payload = {
            'age':    int(float(profile.get('age', 25) or 25)),
            'weight': round(float(profile.get('weight', 70.0) or 70.0), 1),
            'height': round(float(profile.get('height', 175.0) or 175.0), 1),
            'goal':   str(profile.get('goal', 'Maintenance')),
            'pref':   str(profile.get('dietary_preference', 'nonveg')),
            'allergy': sorted([str(x).lower() for x in (profile.get('allergies') or [])]),
        }
        return hashlib.sha256(
            json.dumps(payload, sort_keys=True, separators=(',', ':')).encode()
        ).hexdigest()[:24]

    def _seed(self, ue: str, fp: str, week: int, day: int, mt: str) -> int:
        raw = f"{ue}:{fp}:{week}:{day}:{mt}"
        return int(hashlib.sha256(raw.encode()).hexdigest()[:16], 16) % (10 ** 9)

    # ------------------------------------------------------------------
    # PHASE: DAILY TARGETS
    # ------------------------------------------------------------------

    def calculate_daily_targets(self, profile: Dict) -> Dict:
        gender = str(profile.get('gender', 'Male')).lower()
        weight = max(30.0, min(300.0, float(profile.get('weight', 70) or 70)))
        height = max(100.0, min(250.0, float(profile.get('height', 175) or 175)))
        age    = max(10,    min(100,   int(float(profile.get('age', 25) or 25))))

        if gender in ('male', 'm', 'man'):
            bmr = 10 * weight + 6.25 * height - 5 * age + 5
        elif gender in ('female', 'f', 'woman', 'women'):
            bmr = 10 * weight + 6.25 * height - 5 * age - 161
        else:
            bmr = 10 * weight + 6.25 * height - 5 * age - 78

        act  = self._activity_mult.get(profile.get('activity_level', 'Moderate'), 1.55)
        tdee = bmr * act

        goal = profile.get('goal', 'Maintenance')
        goal_mult = {
            'Weight Loss': 0.85, 'Fat Loss': 0.80,
            'Muscle Gain': 1.10, 'Strength': 1.05,
            'Endurance':   1.00, 'Maintenance': 1.00, 'Maintain': 1.00,
        }
        kcal = tdee * goal_mult.get(goal, 1.00)

        if gender in ('female', 'f', 'woman', 'women'):
            kcal *= 0.90
        elif gender not in ('male', 'm', 'man'):
            kcal *= 0.95
        kcal = max(1200.0, min(5000.0, kcal))

        pp_kg = self._protein_per_kg.get(goal, 1.0)
        if gender in ('female', 'f', 'woman', 'women'):
            pp_kg *= 0.90
        elif gender not in ('male', 'm', 'man'):
            pp_kg *= 0.95

        prot = round(pp_kg * weight, 1)
        prot = min(prot, round((kcal * 0.35) / 4, 1))

        prot_kcal  = prot * 4
        remaining  = max(0.0, kcal - prot_kcal)
        split      = self._carb_fat_split.get(goal, {'carbs': 0.58, 'fat': 0.42})
        carb = round((remaining * split['carbs']) / 4, 1)
        fat  = round((remaining * split['fat'])  / 9, 1)

        return {
            'daily_calories': round(kcal),
            'macro_targets_g': {
                'protein_g': prot,
                'carb_g':    carb,
                'fat_g':     fat,
            },
        }

    # ------------------------------------------------------------------
    # PHASE 7 — NUTRITION RULE ENGINE (diet + allergy filter)
    # ------------------------------------------------------------------

    def _apply_nutrition_rules(self, profile: Dict) -> pd.DataFrame:
        df = self.df.copy()

        pref = str(profile.get('dietary_preference') or 'nonveg').lower().strip()
        pref = {'veg': 'veg', 'vegetarian': 'veg',
                'vegan': 'vegan',
                'nonveg': 'nonveg', 'non-veg': 'nonveg',
                'non vegetarian': 'nonveg'}.get(pref, pref)

        if pref == 'veg':
            df = df[df['is_vegetarian'].astype(str).str.lower().isin(['true', '1', 'yes'])]
            # Guard against mislabeled CSV rows: exclude fish/meat even if is_vegetarian=True
            df = df[~df['contains_fish'].astype(str).str.lower().isin(['true', '1', 'yes'])]
            df = df[~df['contains_meat'].astype(str).str.lower().isin(['true', '1', 'yes'])]
        elif pref == 'vegan':
            df = df[df['is_vegan'].astype(str).str.lower().isin(['true', '1', 'yes'])]
            # Guard against mislabeled rows: exclude fish/meat/dairy for vegan
            df = df[~df['contains_fish'].astype(str).str.lower().isin(['true', '1', 'yes'])]
            df = df[~df['contains_meat'].astype(str).str.lower().isin(['true', '1', 'yes'])]
            df = df[~df['contains_dairy'].astype(str).str.lower().isin(['true', '1', 'yes'])]
        elif pref == 'nonveg':
            pass  # all foods allowed
        else:
            raise ValueError(
                f"Invalid dietary_preference '{pref}'. Supported: veg, nonveg, vegan.")

        allergies = profile.get('allergies') or []
        if allergies:
            expanded = []
            for a in allergies:
                al = a.strip().lower()
                if al in ('lactose', 'dairy'):
                    expanded.extend(['milk', 'dairy', 'lactose', 'cheese',
                                     'paneer', 'butter', 'ghee', 'cream'])
                elif al == 'gluten':
                    expanded.extend(['wheat', 'gluten', 'barley', 'rye',
                                     'maida', 'suji', 'semolina', 'atta'])
                elif al == 'nuts':
                    expanded.extend(['nuts', 'almond', 'cashew', 'walnut',
                                     'peanut', 'pistachio'])
                else:
                    expanded.append(al)
            pattern = '|'.join(r'\b' + re.escape(x) + r'\b' for x in expanded if x)
            if pattern:
                df = df[~df['allergens'].str.lower().str.contains(
                    pattern, na=False, regex=True)]

        blocklist_pattern = '|'.join(r'\b' + re.escape(t) + r'\b' for t in FOOD_NAME_BLOCKLIST)
        if blocklist_pattern:
            df = df[~df['food_name'].str.lower().str.contains(
                blocklist_pattern, na=False, regex=True)]

        # Extra safety check to drop any roles that slipped through
        df = df[~df['meal_role'].isin(['dessert', 'spread', 'sauce', 'condiment', 'sweet'])]

        never_recommend = profile.get('never_recommend') or []
        if never_recommend:
            never_pattern = '|'.join(re.escape(str(t).lower().strip()) for t in never_recommend if t)
            if never_pattern:
                df = df[~df['food_name'].str.lower().str.contains(
                    never_pattern, na=False, regex=True)]

        return df

    # ------------------------------------------------------------------
    # PHASE 3 & 4 — CANDIDATE GENERATION (blueprint + meal_time aware)
    # ------------------------------------------------------------------

    def _generate_candidates(self,
                              pool:          pd.DataFrame,
                              meal_type:     str,
                              rng:           random.Random,
                              tracker:       WeeklyVarietyTracker,
                              num_candidates: int = 40,
                              rejected_names: Optional[Set[str]] = None) -> List[Tuple[List[Dict], int]]:
        """
        Generate (components, blueprint_idx) tuples.
        Pool is filtered by meal_time so foods like Dosa don't appear at dinner.
        """
        blueprints = BLUEPRINTS.get(meal_type, [['combo_meal']])

        # Filter pool by meal_type from nutrition CSV
        # meal_type column values: Breakfast, Lunch, Dinner, Snack, Beverage
        mt_cap = meal_type.capitalize()
        meal_pool = pool[
            pool['meal_type'].str.contains(mt_cap, case=False, na=False) |
            pool['meal_type'].str.contains('Beverage', case=False, na=False)
        ]
        if meal_pool.empty:
            meal_pool = pool  # fallback: ignore meal_time filter

        candidates: List[Tuple[List[Dict], int]] = []
        
        # Precompute available items by role to avoid pandas mask evaluation in hot loop
        weights_map = {'very_common': 4, 'common': 2, 'limited': 1, 'rare': 0.25}
        meal_pool_dicts = meal_pool.to_dict('records')
        available_by_role = {}
        for b in blueprints:
            for role in b:
                if role not in available_by_role:
                    role_items = [row for row in meal_pool_dicts if row.get('meal_role') == role]
                    for item in role_items:
                        item['_base_weight'] = weights_map.get(item.get('availability', 'common'), 1)
                    available_by_role[role] = role_items

        full_pool_dicts = pool.to_dict('records')
        full_available_by_role = {}
        for b in blueprints:
            for role in b:
                if role not in full_available_by_role:
                    role_items = [row for row in full_pool_dicts if row.get('meal_role') == role]
                    for item in role_items:
                        item['_base_weight'] = weights_map.get(item.get('availability', 'common'), 1)
                    full_available_by_role[role] = role_items

        # Apply rejected_names filter ONCE upfront
        if rejected_names:
            for role, items in available_by_role.items():
                available_by_role[role] = [x for x in items if x.get('food_name') not in rejected_names]
            for role, items in full_available_by_role.items():
                full_available_by_role[role] = [x for x in items if x.get('food_name') not in rejected_names]

        # Convert history to set ONCE for O(1) lookups
        history_set = set(tracker.meal_history(meal_type))

        for attempt in range(num_candidates * 3):
            if len(candidates) >= num_candidates:
                break

            # Prefer unused templates first
            unused_idxs = [i for i in range(len(blueprints))
                           if i not in tracker.template_history[-len(blueprints):]]
            if unused_idxs:
                bp_idx = rng.choice(unused_idxs)
            else:
                # Least-recently used
                counts = Counter(tracker.template_history)
                bp_idx = min(range(len(blueprints)),
                             key=lambda i: counts.get(i, 0))

            blueprint = blueprints[bp_idx]
            components: List[Dict] = []
            valid = True
            pair_group: Optional[str] = None

            for role in blueprint:
                role_pool_items = available_by_role.get(role, [])

                # Try to match pair_group for cohesion (e.g. Idli + Sambar)
                if pair_group:
                    pg_pool = [x for x in role_pool_items if x.get('meal_pair_group') == pair_group]
                    if pg_pool and rng.random() > 0.25:
                        role_pool_items = pg_pool

                # Graceful Fallbacks if strict filtering exhausts options
                if not role_pool_items:
                    # Fallback 1: Try from full pool ignoring meal_time and pair_group
                    role_pool_items = full_available_by_role.get(role, [])
                
                if not role_pool_items:
                    valid = False
                    break

                # Prefer less-recently used foods (variety)
                unseen = [x for x in role_pool_items if x.get('food_name') not in history_set]
                sample_pool = unseen if unseen else role_pool_items

                # Availability-weighted sampling with tie-breaking noise for variety
                if '_base_weight' in sample_pool[0]:
                    w = [x.get('_base_weight', 1) + rng.uniform(0, 0.4) for x in sample_pool]
                    w_sum = sum(w)
                    if w_sum > 0:
                        w = [weight / w_sum for weight in w]
                        try:
                            selected = rng.choices(sample_pool, weights=w, k=1)[0]
                        except Exception:
                            selected = rng.choice(sample_pool)
                    else:
                        selected = rng.choice(sample_pool)
                else:
                    selected = rng.choice(sample_pool)

                if pair_group is None and role in ('combo_meal', 'carb_base', 'protein_main'):
                    pair_group = selected.get('meal_pair_group', '')

                components.append(selected)

            if valid and components:
                if is_realistic_meal_identity(meal_type, components):
                    candidates.append((components, bp_idx))

        return candidates

    # ------------------------------------------------------------------
    # PHASE 8 — WEEKLY VALIDATOR
    # ------------------------------------------------------------------

    def _validate_plan(self, plan: Dict) -> Dict:
        """
        Run all checks per spec.
        Returns dict with:
          'warnings': List[str]
          'failed':   List[Tuple[str, str]]  — (day_name, meal_type) pairs that failed
        """
        warnings: List[str] = []
        failed:   List[tuple] = []
        all_meals_by_type: Dict[str, List[str]] = {
            'breakfast': [], 'lunch': [], 'dinner': [], 'snack': []}

        for day, meals in plan.items():
            for mt, items in meals.items():
                names = [i['food_name'] for i in items]
                bucket = all_meals_by_type.get(mt, [])

                # CHECK 1 & 2: Duplicate meals across days
                for n in names:
                    if n in bucket:
                        msg = f"CHECK1 -- '{n}' repeated in {mt} across days"
                        warnings.append(msg)
                        if (day, mt) not in failed:
                            failed.append((day, mt))
                    bucket.append(n)

            # CHECK 3 & 4: Desserts, Spreads, strict completeness rules
            for mt, items in meals.items():
                roles = [i.get('meal_role', '') for i in items]
                
                # Check for structural completeness
                if mt in ['breakfast', 'lunch', 'dinner']:
                    has_combo = 'combo_meal' in roles
                    has_carb = 'carb_base' in roles
                    has_protein = 'protein_main' in roles
                    has_side = any(r in ['salad', 'veg_side', 'dairy_side', 'beverage', 'snack_fruit'] for r in roles)
                    
                    is_complete = (has_combo and has_side) or (has_carb and has_protein)
                    if not is_complete:
                        warnings.append(f"CHECK3 -- {day}/{mt} lacks structural completeness (requires carb+protein or combo+side).")
                        if (day, mt) not in failed: failed.append((day, mt))

                # Check condiment portion sizes
                for item in items:
                    if item.get('meal_role', '') == 'condiment':
                        qty = item.get('serving_weight', 0)
                        max_qty = item.get('portion_max', 30)
                        if qty > max_qty + 1: # +1 for rounding grace
                            warnings.append(f"CHECK3 -- {day}/{mt} condiment {item.get('food_name')} exceeds max portion ({qty} > {max_qty}).")
                            if (day, mt) not in failed: failed.append((day, mt))

                if set(roles) & {'dessert', 'spread', 'sauce', 'sweet'}:
                    warnings.append(f"CHECK3 -- {day}/{mt} contains forbidden dessert/sauce role.")
                    if (day, mt) not in failed: failed.append((day, mt))
                    
                if roles.count('combo_meal') > 1:
                    warnings.append(f"CHECK4 -- {day}/{mt} has multiple combo meals.")
                    if (day, mt) not in failed: failed.append((day, mt))
                    
                if roles.count('carb_base') > 1:
                    warnings.append(f"CHECK4 -- {day}/{mt} has multiple carb bases.")
                    if (day, mt) not in failed: failed.append((day, mt))

                if 'combo_meal' in roles and 'carb_base' in roles:
                    warnings.append(f"CHECK4 -- {day}/{mt} mixes combo_meal with carb_base.")
                    if (day, mt) not in failed: failed.append((day, mt))
                    
                if 'combo_meal' in roles and 'protein_main' in roles:
                    warnings.append(f"CHECK4 -- {day}/{mt} mixes combo_meal with protein_main.")
                    if (day, mt) not in failed: failed.append((day, mt))

            # CHECK 5: Meal Completeness per day
            for mt, items in meals.items():
                if mt == 'snack' or not items:
                    continue
                roles = {i.get('meal_role', '') for i in items}
                # combo_meal counts as both protein and carb
                has_combo = 'combo_meal' in roles
                has_p = has_combo or bool(roles & {'protein_main'})
                has_c = has_combo or bool(roles & {'carb_base'})
                if not has_p:
                    msg = f"CHECK5 -- {day}/{mt} missing protein component"
                    warnings.append(msg)
                    if (day, mt) not in failed:
                        failed.append((day, mt))
                if not has_c and mt in ('lunch', 'dinner'):
                    msg = f"CHECK5 -- {day}/{mt} missing carb component"
                    warnings.append(msg)
                    if (day, mt) not in failed:
                        failed.append((day, mt))

            # CHECK 6: Portion Realism — already enforced in optimize_portions
            # CHECK 7 & 8: Budget/Availability — enforced in scoring

        return {'warnings': warnings, 'failed': failed}

    # ------------------------------------------------------------------
    # MAIN: GENERATE WEEKLY PLAN
    # ------------------------------------------------------------------

    def generate_weekly_plan(self, profile: Dict) -> Dict:
        targets   = self.calculate_daily_targets(profile)
        total_cal = targets['daily_calories']

        ue       = self._user_entropy(profile)
        fp       = self._profile_fp(profile)
        import datetime
        current_iso_week = datetime.datetime.now().isocalendar()[1]
        week_off = int(profile.get('week_offset') or current_iso_week)

        filtered_pool = self._apply_nutrition_rules(profile)

        tracker   = WeeklyVarietyTracker()
        day_names = ['Monday', 'Tuesday', 'Wednesday',
                     'Thursday', 'Friday', 'Saturday', 'Sunday']
        meal_types = ['breakfast', 'lunch', 'snack', 'dinner']
        weekly_plan: Dict[str, Dict] = {}

        for day_idx, day_name in enumerate(day_names):
            weekly_plan[day_name] = {}

            for mt in meal_types:
                target_cal = total_cal * MEAL_DISTRIBUTION[mt]

                best_meal:       Optional[List[Dict]] = None
                best_score:      float = -1.0
                best_meal_cal:   float = 0.0
                best_bp_idx:     int   = 0

                local_rejected_names: Set[str] = set()

                for retry_count in range(3):  # Validator retry loop
                    seed = str(self._seed(ue, fp, week_off, day_idx, mt)) + "_" + str(retry_count)
                    rng  = random.Random(seed)

                    candidates = self._generate_candidates(
                        filtered_pool, mt, rng, tracker, num_candidates=15, rejected_names=local_rejected_names)

                    # Fallback 1: re-try with fewer candidates
                    if len(candidates) < 3:
                        candidates = self._generate_candidates(
                            filtered_pool, mt, rng, tracker, num_candidates=20, rejected_names=local_rejected_names)

                    # Fallback 2: if still empty, use robust multi-role fallbacks
                    if not candidates:
                        ROBUST_FALLBACK_BPS = {
                            'breakfast': [['combo_meal', 'beverage'], ['protein_main', 'carb_base', 'beverage']],
                            'lunch':     [['combo_meal', 'salad'], ['protein_main', 'carb_base', 'veg_side']],
                            'snack':     [['snack'], ['snack_fruit']],
                            'dinner':    [['combo_meal', 'dairy_side'], ['protein_main', 'carb_base', 'veg_side']],
                        }
                        for fallback_bp in ROBUST_FALLBACK_BPS.get(mt, [['combo_meal', 'salad']]):
                            all_roles_available = all(
                                not filtered_pool[filtered_pool['meal_role']==r].empty
                                for r in fallback_bp
                            )
                            if all_roles_available:
                                try:
                                    comps = [
                                        filtered_pool[filtered_pool['meal_role']==r].sample(
                                            n=1, random_state=rng.randint(0,1_000_000)).iloc[0]
                                        for r in fallback_bp
                                    ]
                                    candidates = [(comps, 0)]
                                    print(f"[MealEngine V2] Fallback multi-role blueprint for {day_name}/{mt}: {fallback_bp}")
                                    break
                                except Exception:
                                    continue

                    local_best_meal:       Optional[List[Dict]] = None
                    local_best_score:      float = -1.0
                    local_best_meal_cal:   float = 0.0
                    local_best_bp_idx:     int   = 0

                    for (raw_components, bp_idx) in candidates:
                        opt, meal_cal = optimize_portions(raw_components, target_cal)
                        if not opt:
                            continue
                        s = score_meal(opt, meal_cal, target_cal, tracker, mt, bp_idx)
                        if s > local_best_score:
                            local_best_score    = s
                            local_best_meal     = opt
                            local_best_meal_cal = meal_cal
                            local_best_bp_idx   = bp_idx
                            
                    if not local_best_meal:
                        break  # Pool is truly empty

                    # Inline Validation: If fails, regenerate this meal slot
                    names = [i['food_name'] for i in local_best_meal]
                    hist = tracker.meal_history(mt)
                    is_duplicate = any(n in hist for n in names)
                    
                    roles = {i.get('meal_role', '') for i in local_best_meal}
                    has_combo = 'combo_meal' in roles
                    has_p = has_combo or bool(roles & {'protein_main'})
                    has_c = has_combo or bool(roles & {'carb_base'})
                    
                    is_incomplete = False
                    if mt != 'snack':
                        if not has_p:
                            is_incomplete = True
                        if not has_c and mt in ('lunch', 'dinner'):
                            is_incomplete = True
                            
                    # Reject invalid strict rules during generation loops to save validator passes
                    is_invalid_combo = False
                    role_list = [i.get('meal_role', '') for i in local_best_meal]
                    if role_list.count('combo_meal') > 1 or role_list.count('carb_base') > 1:
                        is_invalid_combo = True
                    if 'combo_meal' in role_list and ('carb_base' in role_list or 'protein_main' in role_list):
                        is_invalid_combo = True
                    if set(role_list) & {'dessert', 'spread', 'sauce', 'condiment', 'sweet'}:
                        is_invalid_combo = True

                    if not is_duplicate and not is_incomplete and not is_invalid_combo:
                        # Validation Passed!
                        best_meal     = local_best_meal
                        best_score    = local_best_score
                        best_meal_cal = local_best_meal_cal
                        best_bp_idx   = local_best_bp_idx
                        break
                    else:
                        local_rejected_names.update(names)
                        print(f"[MealEngine V2] Inline reject {mt}: {names}")
                    
                    # If failed but it's the last retry, accept it anyway
                    if retry_count == 2 or best_meal is None:
                        best_meal     = local_best_meal
                        best_score    = local_best_score
                        best_meal_cal = local_best_meal_cal
                        best_bp_idx   = local_best_bp_idx

                formatted_foods: List[Dict] = []
                if best_meal:
                    # Register chosen meal in tracker
                    tracker.record_meal(mt, best_meal)
                    tracker.record_template(best_bp_idx)
                    tracker.record_cuisine(best_meal[0].get('region', 'All India'))

                    for c in best_meal:
                        # Build swap options — pass meal_time to avoid cross-meal swaps
                        swaps = build_swap_options(c, filtered_pool, profile, meal_time=mt)
                        food_out = {
                            'food_id':      c['food_id'],
                            'food_name':    c['food_name'],
                            'meal_type':    mt,
                            'meal_role':    c['meal_role'],
                            'serving':      c['serving'],
                            'serving_weight': round(c['serving_qty'], 1),
                            'calories':     round(c['calories']),
                            'protein':      round(c['protein'], 1),
                            'carbs':        round(c['carbs'], 1),
                            'fat':          round(c['fat'], 1),
                            'budget_level': c['budget_level'],
                            'availability': c['availability'],
                            'swap_group':   c['swap_group'],
                            'swap_options': swaps,
                        }
                        formatted_foods.append(food_out)

                weekly_plan[day_name][mt] = formatted_foods

        # Phase 8: Weekly Validator — runs once, then corrects failed meals
        validation_result   = self._validate_plan(weekly_plan)
        validation_warnings = validation_result['warnings']
        failed_slots        = validation_result['failed']

        if validation_warnings:
            print(f"[MealEngine V2] Validation warnings ({len(validation_warnings)}):")
            for w in validation_warnings[:5]:
                print(f"  [WARN] {w}")

        # Correction loop: regenerate only failed (day, meal_type) slots (up to 3 passes)
        if failed_slots:
            rejected_for_slot: Dict[tuple, Set[str]] = {}
            print(f"[MealEngine V2] Attempting to correct {len(failed_slots)} failed slots...")
            for correction_pass in range(3):
                if not failed_slots:
                    break
                still_failed = []
                for (fail_day, fail_mt) in failed_slots:
                    current_names = [i['food_name'] for i in weekly_plan[fail_day][fail_mt]]
                    if (fail_day, fail_mt) not in rejected_for_slot:
                        rejected_for_slot[(fail_day, fail_mt)] = set()
                    rejected_for_slot[(fail_day, fail_mt)].update(current_names)
                    print(f"  [CORRECTING] {fail_day}/{fail_mt} - Blacklisting: {current_names}")
                    
                    fail_day_idx = day_names.index(fail_day) if fail_day in day_names else 0
                    target_cal   = total_cal * MEAL_DISTRIBUTION[fail_mt]

                    # Use correction_pass as additional seed entropy
                    correction_seed_offset = 1000 + correction_pass * 100
                    seed = str(self._seed(ue, fp, week_off, fail_day_idx, fail_mt)) + f"_corr{correction_seed_offset}"
                    rng  = random.Random(seed)

                    candidates = self._generate_candidates(
                        filtered_pool, fail_mt, rng, tracker, num_candidates=40,
                        rejected_names=rejected_for_slot[(fail_day, fail_mt)])
                    if not candidates:
                        still_failed.append((fail_day, fail_mt))
                        continue

                    local_best_meal:     Optional[List[Dict]] = None
                    local_best_score:    float = -1.0
                    local_best_meal_cal: float = 0.0
                    local_best_bp_idx:   int   = 0

                    for (raw_components, bp_idx) in candidates:
                        opt, meal_cal = optimize_portions(raw_components, target_cal)
                        if not opt:
                            continue
                        s = score_meal(opt, meal_cal, target_cal, tracker, fail_mt, bp_idx)
                        if s > local_best_score:
                            local_best_score    = s
                            local_best_meal     = opt
                            local_best_meal_cal = meal_cal
                            local_best_bp_idx   = bp_idx

                    if not local_best_meal:
                        still_failed.append((fail_day, fail_mt))
                        continue

                    # Replace the slot
                    corrected_foods: List[Dict] = []
                    tracker.record_meal(fail_mt, local_best_meal)
                    tracker.record_template(local_best_bp_idx)
                    for c in local_best_meal:
                        swaps = build_swap_options(c, filtered_pool, profile, meal_time=fail_mt)
                        corrected_foods.append({
                            'food_id':        c['food_id'],
                            'food_name':      c['food_name'],
                            'meal_type':      fail_mt,
                            'meal_role':      c['meal_role'],
                            'serving':        c['serving'],
                            'serving_weight': round(c['serving_qty'], 1),
                            'calories':       round(c['calories']),
                            'protein':        round(c['protein'], 1),
                            'carbs':          round(c['carbs'], 1),
                            'fat':            round(c['fat'], 1),
                            'budget_level':   c['budget_level'],
                            'availability':   c['availability'],
                            'swap_group':     c['swap_group'],
                            'swap_options':   swaps,
                        })
                    weekly_plan[fail_day][fail_mt] = corrected_foods
                    print(f"  [CORRECTED] {fail_day}/{fail_mt} in pass {correction_pass + 1}")

                # Re-validate after corrections
                revalidation   = self._validate_plan(weekly_plan)
                failed_slots   = revalidation['failed']
                if revalidation['warnings']:
                    validation_warnings = revalidation['warnings']  # update with latest

            if failed_slots:
                print(f"[MealEngine V2] {len(failed_slots)} slots could not be fully corrected after 3 passes.")

        summary = self._build_summary(weekly_plan, targets)
        return {
            'plan':              weekly_plan,
            'daily_targets':     targets,
            'weekly_summary':    summary,
            'validation_warnings': validation_warnings,
        }

    # ------------------------------------------------------------------
    # SUMMARY & SHOPPING LIST
    # ------------------------------------------------------------------

    def _build_summary(self, plan: Dict, targets: Dict) -> Dict:
        total_cal = total_prot = total_carb = total_fat = 0.0
        shopping: Counter = Counter()

        for meals in plan.values():
            for items in meals.values():
                for item in items:
                    total_cal  += float(item.get('calories', 0))
                    total_prot += float(item.get('protein',  0))
                    total_carb += float(item.get('carbs',    0))
                    total_fat  += float(item.get('fat',      0))
                    shopping[item['food_name']] += 1

        days = max(len(plan), 1)
        target_cal = targets.get('daily_calories', 1)
        avg_cal = total_cal / days
        consistency = max(0.0, 1.0 - abs(avg_cal - target_cal) / max(target_cal, 1))

        return {
            'total_calories':   round(total_cal),
            'daily_average': {
                'calories':  round(avg_cal),
                'protein_g': round(total_prot / days, 1),
                'carbs_g':   round(total_carb / days, 1),
                'fat_g':     round(total_fat  / days, 1),
            },
            'consistency_score': round(consistency, 2),
            'shopping_list':     dict(shopping.most_common(30)),
        }

    # ------------------------------------------------------------------
    # PHASE 5 — PUBLIC SWAP API
    # ------------------------------------------------------------------

    def get_swap_options(self,
                         food_name: str,
                         meal_type: str,
                         profile:   Dict,
                         limit:     int = 5) -> List[Dict]:
        """
        Return swap options for a named food item.
        Called by /nutrition/swap endpoint.
        """
        pool = self._apply_nutrition_rules(profile)
        row  = pool[pool['food_name'].str.lower() == food_name.strip().lower()]
        if row.empty:
            return []

        component = {
            'food_name':    food_name,
            'meal_role':    str(row.iloc[0].get('meal_role', '')),
            'swap_group':   str(row.iloc[0].get('swap_group', '')),
            'calories':     float(row.iloc[0].get('calories_kcal', 0)),
            'protein':      float(row.iloc[0].get('protein_g', 0)),
        }
        return build_swap_options(component, pool, profile, meal_time=meal_type, limit=limit)
