import os
import json
import logging
import datetime
import time
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Set, Tuple
from types import MappingProxyType
import random

def _unfreeze(obj):
    if isinstance(obj, (dict, MappingProxyType)):
        return {k: _unfreeze(v) for k, v in obj.items()}
    if isinstance(obj, (list, tuple)):
        return [_unfreeze(v) for v in obj]
    return obj
import difflib
from app.nutrition_engine.food_utils import get_meal_suitability
from app.nutrition_engine.config import NUTRITION_RULES

logger = logging.getLogger(__name__)

# ── Phase 0 Diagnostics ───────────────────────────────────────────────────
# JSONL file that accumulates one structured record per generate_candidates() call.
# Writing is best-effort: if the file cannot be written (permissions, disk full, etc.)
# the exception is caught and logged so meal generation is never blocked.
_METRICS_LOG_DIR  = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
    "logs"
)
_METRICS_LOG_PATH = os.path.join(_METRICS_LOG_DIR, "candidate_generation_metrics.jsonl")


def _write_candidate_metrics(record: dict) -> None:
    """Append one JSON object to the candidate-generation metrics JSONL file.

    Best-effort: any I/O error is swallowed so it never interrupts meal generation.
    """
    try:
        os.makedirs(_METRICS_LOG_DIR, exist_ok=True)
        with open(_METRICS_LOG_PATH, "a", encoding="utf-8") as fh:
            fh.write(json.dumps(record, ensure_ascii=False) + "\n")
    except Exception:
        logger.exception("[CandidateGenerator] Failed to write candidate metrics — ignoring")

# ── Meal-type suitability score thresholds ────────────────────────────────
# Foods scoring below these thresholds for a given meal type are rejected.
SUITABILITY_THRESHOLDS: Dict[str, int] = {
    'breakfast': 60,
    'lunch':     50,
    'dinner':    50,
    'snack':     60,
}

# Meal-type role guard: dish_family values not permitted for a meal type.
# These replace the old hardcoded keyword lists and are metadata-driven.
_MEAL_TYPE_BLOCKED_FAMILIES: Dict[str, set] = {
    'breakfast': {'biryani', 'pulao', 'fried_rice', 'rice', 'khichdi', 'dal',
                  'sambar', 'korma', 'curry', 'rasam'},
    'snack':     {'biryani', 'pulao', 'fried_rice', 'plain_rice', 'rice',
                  'khichdi', 'dal', 'sambar', 'korma', 'curry', 'paratha',
                  'roti', 'naan'},
}

# Side dish alternatives — used when a blueprint calls for a dominant/banned item
SIDE_OPTIONS = [
    "Cucumber Tomato Salad",
    "Carrot Salad",
    "Onion Salad",
    "Sprouted Moong",
    "Beetroot Salad",
    "Raita",
    "Plain Yogurt (Curd)",
    "Tomato Soup",
    "Vegetable Clear Soup",
    "Mixed Vegetable Salad With Curd Sauce",
]

@dataclass
class DailyMealContext:
    """
    Tracks which dish_family and primary_ingredient values have already
    appeared in earlier meals within the same day.

    Used by CandidateGenerator._get_dynamic_candidates() to:
      - Reduce sampling probability for already-used ingredients (soft diversity)
      - Block exact dish_family repeats within the same day (hard diversity, optional)

    Usage:
        ctx = DailyMealContext()
        candidates = generator.generate_candidates(..., daily_context=ctx)
        ctx.record_meal(winning_plate)   # call after meal is finalized

    The context is owned by WeeklyOptimizer and passed into each generate_candidates call.
    """
    used_dish_families: Set[str] = field(default_factory=set)
    used_primary_ingredients: Set[str] = field(default_factory=set)
    ingredient_counts: Dict[str, int] = field(default_factory=dict)

    def record_meal(self, plate: List[Dict]) -> None:
        """Call after a meal is finalized to update the daily context."""
        for item in plate:
            sem = item.get('semantics', {})
            df = sem.get('dish_family', 'other')
            pi = sem.get('primary_ingredient', 'other')
            if df and df != 'other':
                self.used_dish_families.add(df)
            if pi and pi != 'other':
                self.used_primary_ingredients.add(pi)
                self.ingredient_counts[pi] = self.ingredient_counts.get(pi, 0) + 1

    def diversity_weight(self, node: Dict) -> float:
        """
        Returns a multiplicative weight in (0, 1] for a food node.
        Foods whose primary_ingredient has appeared in earlier meals receive
        a lower weight, reducing their probability in weighted sampling.
        """
        pi = node.get('semantics', {}).get('primary_ingredient', 'other')
        count = self.ingredient_counts.get(pi, 0)
        if count == 0:
            return 1.0
        # Exponential decay: first repeat -> 0.5, second -> 0.25, etc.
        return 0.5 ** count


class CandidateGenerator:
    """
    Phase 4.9: Predefined Meal Candidate Generator.
    Generates candidates from a structured Meal Knowledge Base.
    """
    def __init__(self, food_graph):
        self.food_graph = food_graph
        
        data_dir = os.path.dirname(food_graph.nutrition_csv_path)
        kb_path = os.path.join(data_dir, 'meal_blueprint_library.json')
        
        try:
            with open(kb_path, 'r', encoding='utf-8') as f:
                self.meal_blueprints = json.load(f)
            logger.info(f"Loaded Meal Blueprint Library with {len(self.meal_blueprints)} meals.")
        except Exception as e:
            logger.error(f"Failed to load meal blueprint library: {e}")
            self.meal_blueprints = []
            
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
        # NOTE: aliases that map to "tossed salad" are REMOVED — they caused
        # Tossed Salad to dominate every meal slot.
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
            "kachumber salad": "mixed vegetable salad with curd sauce",
            "kachumber": "cucumber tomato salad",
            "lettuce salad": "mixed vegetable salad with curd sauce",
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
            "cucumber salad": "cucumber tomato salad",
            "multigrain bread": "whole wheat bread",
            "missi roti": "missi roti"
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

    def _is_meal_type_suitable(self, food_name: str, meal_type: str) -> bool:
        """
        Hard-block check independent of the score system.
        Returns False if the food clearly does not belong to this meal type.
        Uses dish_family metadata (from FoodGraph semantics) instead of keyword parsing.
        """
        node = self.name_to_node.get(food_name.lower().strip())
        if node:
            dish_family = node.get('semantics', {}).get('dish_family', 'other')
            blocked = _MEAL_TYPE_BLOCKED_FAMILIES.get(meal_type.lower(), set())
            if dish_family in blocked:
                return False

        mt = meal_type.lower()
        n = food_name.lower()

        # Legacy keyword guard for 'other' dish_family foods — avoids regressions
        if mt == 'breakfast':
            if 'salad' in n and 'fruit' not in n:
                return False
        elif mt in ('lunch', 'dinner'):
            if any(x in n for x in ['cornflakes', 'muesli', 'breakfast cereal']):
                return False

        return True

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

    def _is_safe_meal_with_reason(self, plate: List[Dict], user_profile: Dict) -> Tuple[bool, str]:
        if not user_profile:
            return True, ""
            
        allergy_pattern, never_pattern = self._get_user_patterns(user_profile)
            
        # Verify each food item in the plate
        for item in plate:
            name = item.get('food_name', '').lower()
            allergens = item.get('allergens', '').lower()
            
            # Check blocklist
            if self.blocklist_pattern:
                _m = self.blocklist_pattern.search(name)
                if _m:
                    logger.debug(
                        "[blocklist] '%s' rejected — matched keyword '%s'",
                        item.get('food_name', ''), _m.group(0),
                    )
                    return False, "blocklist_match"
                
            # Check allergies (against name and allergens field)
            if allergy_pattern:
                if allergy_pattern.search(name) or allergy_pattern.search(allergens):
                    return False, "allergy_match"
                    
            # Check never recommend
            if never_pattern and never_pattern.search(name):
                return False, "never_recommend_match"
                
        return True, ""

    def generate_candidates(
        self,
        template: Dict[str, Any],
        meal_type: str,
        diet_type: str,
        count: int = 5,
        user_profile: Dict = None,
        daily_rules: Dict = None,
        day_seed: int = 0,
        excluded_foods: Set[str] = None,
        daily_context: 'DailyMealContext' = None,   # within-day diversity memory
        daily_targets: Dict = None,                   # for protein/calorie bound checks
    ) -> tuple:
        """
        Generates candidate plates using Dual Source Generation (Blueprints + Dynamic Combinations).

        excluded_foods:  food_ids already used in other meals TODAY (cross-meal exclusion).
        daily_context:   DailyMealContext tracking dish_family/ingredient used so far today.
        daily_targets:   dict with 'calories' and 'protein' from WeeklyMacroPlanner, used by
                         the quick quality filter for calorie-bound checking.
        """
        import random as _rng
        _t_start = time.perf_counter()
        rng = _rng.Random(day_seed)

        excluded_foods  = excluded_foods or set()
        daily_context   = daily_context or DailyMealContext()
        daily_targets   = daily_targets or {}
        daily_protein   = daily_targets.get('protein', 0)
        daily_calories  = daily_targets.get('calories', 0)
        raw_goal        = (user_profile or {}).get('fitness_goal') or (user_profile or {}).get('goal') or 'Maintenance'
        goal_str = str(raw_goal).strip().lower().replace(" ", "_")
        if 'fat' in goal_str or 'loss' in goal_str or 'weight' in goal_str:
            goal = 'Weight Loss'
        elif 'gain' in goal_str or 'muscle' in goal_str or 'hypertrophy' in goal_str:
            goal = 'Muscle Gain'
        else:
            goal = 'Maintenance'
        target_cuisine  = (user_profile or {}).get('cuisine_preference', '')

        candidates = []

        # ── Phase 0: Full rejection statistics ───────────────────────────────
        # Each key maps to one specific rejection rule.  Counters are incremented
        # inside the filter loop and written to the JSONL metrics file at the end.
        rejection_stats: Dict[str, int] = {
            "template_mismatch":      0,   # legacy catch-all (should stay ~0 now)
            "empty_plate":            0,   # plate had no items
            "missing_role":           0,   # template required-role count not met
            "forbidden_role":         0,   # template forbidden role present in plate
            "meal_type_mismatch":     0,   # food fails hard meal-type suitability
            "meal_suitability_failure":0,  # food below meal-type suitability score
            "breakfast_structure":    0,   # breakfast structural rule violated
            "snack_structure":        0,   # snack structural rule violated
            "duplicate_dish_family":  0,   # two items share the same dish_family
            "duplicate_protein_main": 0,   # two protein_main items with same primary_ingredient
            "duplicate_carb_base":    0,   # two items with carb_base role
            "duplicate_side_category":0,   # two items with same side category
            "cuisine_compat":         0,   # incompatible cuisine mix (soft → currently tracked only)
            "daily_diversity":        0,   # dish_family already used earlier today
            "weekly_diversity":       0,   # food already used this week
            "protein_threshold":      0,   # plate cannot reach minimum protein
            "calorie_threshold":      0,   # plate outside calorie feasibility bounds
            "missing_required_role":  0,   # protein/carb/veg structural shortfall
            "allergy":                0,   # allergy / never-recommend violation
            "diet":                   0,   # diet incompatibility
            "duplicate_food_id":      0,   # duplicate food_id within a plate
            "duplicate_food_name":    0,   # duplicate food_name within a plate
        }
        gen_stats = {
            "total_candidates":   0,
            "passed_structure":   0,
            "failed_structure":   0,
            "failed_quality":     0,
            "passed_quick_filter": 0,
            "used_fallback":      False,
        }

        if not daily_rules:
            daily_rules = {}

        max_prep_time = daily_rules.get("max_prep_time", 999)
        allowed_complexity = daily_rules.get("allowed_complexity", [1, 10])

        perf = NUTRITION_RULES.get('performance', {})
        max_candidates = perf.get('max_candidates_per_meal', 15)

        # SOURCE 1: Meal Blueprint Library
        blueprint_candidates = self._get_blueprint_candidates(
            meal_type, diet_type, template, rng, max_prep_time, allowed_complexity, excluded_foods
        )

        # SOURCE 2: Dynamic Semantic Generation — template-driven (Phase 1A)
        dynamic_candidates = self._get_dynamic_candidates(
            template, meal_type, diet_type, rng, excluded_foods, goal, target_cuisine, daily_context
        )

        raw_candidates = blueprint_candidates + dynamic_candidates
        rng.shuffle(raw_candidates)
        gen_stats["total_candidates"] = len(raw_candidates)

        safe_candidates = []
        for meal in raw_candidates:
            # Allergy / never-recommend check
            safe_ok, safe_reason = self._is_safe_meal_with_reason(meal, user_profile)
            if not safe_ok:
                if safe_reason in rejection_stats:
                    rejection_stats[safe_reason] += 1
                else:
                    rejection_stats[safe_reason] = 1
                gen_stats["failed_structure"] += 1
                continue

            # Structural composition check — returns (bool, reason_str)
            comp_ok, comp_reason = self._is_valid_composition_with_reason(
                meal, meal_type, template
            )
            if not comp_ok:
                # Map reason string to the appropriate rejection counter
                if comp_reason in rejection_stats:
                    rejection_stats[comp_reason] += 1
                else:
                    rejection_stats["template_mismatch"] += 1
                gen_stats["failed_structure"] += 1
                logger.debug(
                    "[%s] Plate rejected — %s | foods=%s",
                    meal_type,
                    comp_reason,
                    [i.get('food_name', '') for i in meal],
                )
                continue

            # Hard post-validation: no duplicate food_ids within the plate
            plate_ids = [
                str(item.get("food_id") or item.get("food_name", "")).lower().strip()
                for item in meal
            ]
            if len(set(plate_ids)) != len(plate_ids):
                rejection_stats["duplicate_food_id"] += 1
                gen_stats["failed_structure"] += 1
                continue

            # Hard post-validation: no duplicate food names (case-insensitive)
            plate_names = [item.get("food_name", "").lower().strip() for item in meal]
            if len(set(plate_names)) != len(plate_names):
                rejection_stats["duplicate_food_name"] += 1
                gen_stats["failed_structure"] += 1
                continue

            # Quick Quality Filter — returns (passed, penalty, reason)
            qf_pass, qf_penalty, qf_reason = self._quick_quality_filter_with_reason(
                meal, meal_type, daily_protein, daily_calories, goal
            )
            if not qf_pass:
                if qf_reason in rejection_stats:
                    rejection_stats[qf_reason] += 1
                else:
                    rejection_stats["calorie_threshold"] += 1
                gen_stats["failed_quality"] += 1
                logger.debug(
                    "[%s] Quick-filter hard reject — %s | foods=%s",
                    meal_type,
                    qf_reason,
                    [i.get('food_name', '') for i in meal],
                )
                continue

            # Track soft cuisine incompatibility for diagnostics (not a reject)
            if qf_reason == "cuisine_compat":
                rejection_stats["cuisine_compat"] += 1

            # Attach penalty score for use by meal_scorer
            for item in meal:
                item.setdefault("_qf_penalty", qf_penalty)

            safe_candidates.append(meal)
            gen_stats["passed_structure"] += 1
            gen_stats["passed_quick_filter"] += 1

            if len(safe_candidates) >= max_candidates:
                break   # performance cap

        # ── Phase 1B: YAML-configurable diversity filter ──────────────────
        cg_cfg = NUTRITION_RULES.get("candidate_generation", {})
        df_pct = cg_cfg.get("diversity_filter", {}).get("top_n_percent", 0.50)
        
        # Simple proxy scoring function for the diversity filter
        def _score_plate(plate):
            score = 0.0
            for item in plate:
                sem = item.get("semantics", {})
                score += min(sem.get("protein_density", 0.0) / 0.30, 1.0)
                if target_cuisine and sem.get("cuisine", "") == target_cuisine:
                    score += 0.5
            return score
            
        diverse_candidates = self._diversity_filter(safe_candidates, top_n_percent=df_pct, score_fn=_score_plate)

        if len(diverse_candidates) > count:
            candidates = rng.sample(diverse_candidates, count)
        else:
            candidates = diverse_candidates

        # If still empty — build a guaranteed fallback plate
        used_fallback = False
        if not candidates:
            meal_cals_estimate = 0
            if daily_calories > 0:
                try:
                    intensity = daily_targets.get('intensity', 'moderate')
                    from app.nutrition_engine.nutrition_calculator import MealMacroDistributor
                    ratios = MealMacroDistributor.RATIOS.get(intensity, MealMacroDistributor.RATIOS["moderate"])
                    cal_ratio = ratios.get(meal_type.lower(), (0.25, 0, 0, 0))[0]
                    meal_cals_estimate = daily_calories * cal_ratio
                except Exception:
                    default_ratios = {'breakfast': 0.25, 'lunch': 0.35, 'dinner': 0.30, 'snack': 0.10}
                    meal_cals_estimate = daily_calories * default_ratios.get(meal_type.lower(), 0.25)

            fallback = self._build_fallback_meal(
                meal_type, diet_type, excluded_foods, goal, meal_cals=meal_cals_estimate
            )
            if fallback:
                candidates = [fallback]
                used_fallback = True
                gen_stats["used_fallback"] = True

        # ── Phase 0: Log summary + write JSONL metrics ────────────────────
        _elapsed_ms = int((time.perf_counter() - _t_start) * 1000)
        total_attempts  = gen_stats["total_candidates"]
        final_count     = len(candidates)
        passed_qf       = gen_stats["passed_quick_filter"]
        acceptance_rate = final_count / max(total_attempts, 1)

        _warn_threshold = cg_cfg.get("acceptance_rate_warning_threshold", 0.05)

        # Human-readable summary log (always)
        _rej_lines = "\n".join(
            f"    {k:<26}: {v}"
            for k, v in rejection_stats.items()
            if v > 0
        ) or "    (none)"
        logger.info(
            "[CandidateGenerator][%s] Summary:\n"
            "  Attempts             : %d\n"
            "  Rejected by:\n%s\n"
            "  Passed quick filter  : %d\n"
            "  Final candidates     : %d\n"
            "  Acceptance rate      : %.1f%%"
            "%s",
            meal_type, total_attempts,
            _rej_lines,
            passed_qf,
            final_count,
            acceptance_rate * 100,
            "  ← WARNING: below threshold" if acceptance_rate < _warn_threshold else "",
        )
        if used_fallback:
            logger.warning(
                "[CandidateGenerator] Used fallback meal builder for %s "
                "(goal=%s). No quality candidates found after %d attempts.",
                meal_type, goal, total_attempts,
            )
        if acceptance_rate < _warn_threshold and total_attempts > 0:
            logger.warning(
                "[CandidateGenerator][%s] Acceptance rate %.1f%% is below %.0f%% threshold. "
                "Top rejection cause: %s",
                meal_type,
                acceptance_rate * 100,
                _warn_threshold * 100,
                max(rejection_stats, key=rejection_stats.get, default="none"),
            )

        # Structured JSONL record — best-effort
        _metrics_record = {
            "timestamp":          datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds"),
            "meal_type":          meal_type,
            "attempts":           total_attempts,
            "passed_quick_filter": passed_qf,
            "final_candidates":   final_count,
            "acceptance_rate":    round(acceptance_rate, 6),
            "used_fallback":      used_fallback,
            "generation_time_ms": _elapsed_ms,
            "rejections":         {k: v for k, v in rejection_stats.items() if v > 0},
        }
        _write_candidate_metrics(_metrics_record)

        return candidates, gen_stats

    def _is_valid_composition(self, plate: List[Dict], meal_type: str, template: Dict = None) -> bool:
        """
        Validates the structural composition of the meal.
        Checks:
          - No duplicate food_ids (catches fuzzy-match collisions)
          - No duplicate dish_family within the plate (v4 enhancement)
          - Per-item meal-type suitability
          - Role-based structural constraints per meal_type
        """
        if not plate:
            return False

        # Template role validation (required and forbidden roles)
        if template:
            is_blueprint = any(item.get("semantics", {}).get("meal_id") for item in plate)
            roles_in_plate = [item.get("template_role") or item.get("semantics", {}).get("meal_role", "") for item in plate]
            
            # Enforce required roles for dynamic combos, with combo_meal flexibility
            if not is_blueprint:
                for req in template.get("required", []):
                    req_role = req.get("role")
                    req_count = req.get("count", 1)
                    
                    match_count = 0
                    for r in roles_in_plate:
                        if r == req_role:
                            match_count += 1
                        elif r == "combo_meal" and req_role in ("protein_main", "carb_base"):
                            match_count += 1
                            
                    if match_count < req_count:
                        return False
                        
            # Forbidden roles checked for both blueprints and dynamic combos
            for forb in template.get("forbidden", []):
                forb_role = forb.get("role")
                if forb_role in roles_in_plate:
                    return False

        # 1. Deduplication by food_id
        food_ids = [
            str(item.get("food_id") or item.get("food_name", "")).lower().strip()
            for item in plate
        ]
        if len(set(food_ids)) != len(food_ids):
            return False

        # 2. dish_family collision check (new in v4)
        dish_families = [
            item.get("semantics", {}).get("dish_family", "other")
            for item in plate
        ]
        non_other_families = [df for df in dish_families if df != "other"]
        if len(non_other_families) != len(set(non_other_families)):
            return False   # two items share the same dish_family

        foods = [item.get("food_name", "").lower().strip() for item in plate]

        # 3. Per-item meal-type suitability (hard type + score threshold)
        threshold = SUITABILITY_THRESHOLDS.get(meal_type.lower(), 50)
        for item in plate:
            fn = item.get("food_name", "")
            if not self._is_meal_type_suitable(fn, meal_type):
                return False
            if get_meal_suitability(fn, meal_type) < threshold:
                return False

        # Analyze components
        curry_count = 0
        salad_count = 0
        has_rice = False
        has_dal = False
        has_protein = False
        has_carb = False
        has_veg = False

        snack_allowed_cats = ['fruit', 'dairy', 'protein snack', 'nuts', 'smoothie', 'beverage']
        has_snack_item = False

        for item in plate:
            name = item.get("food_name", "").lower()
            sem = item.get("semantics", {})
            cat = sem.get("category", "")
            styles = sem.get("cooking_style", "")
            role = sem.get("meal_role", "")
            pdensity = sem.get("protein_density", 0)
            df = sem.get("dish_family", "other")

            if df in ("curry", "korma", "dal", "sambar") or \
               "Gravy" in styles or "Curry" in styles or \
               cat in ["Dal & Pulses", "Meat & Chicken", "Paneer & Tofu"]:
                curry_count += 1
            if "salad" in name or "raita" in name or cat == "Salad":
                salad_count += 1
            if df in ("rice", "plain_rice", "fried_rice", "pulao", "biryani") or \
               "rice" in name or "pulao" in name or "biryani" in name:
                has_rice = True
            if df == "dal" or "dal" in name or "sambar" in name:
                has_dal = True

            if pdensity > 0.12 or cat in ['Dal & Pulses', 'Paneer & Tofu', 'Meat & Chicken', 'Eggs', 'Seafood']:
                has_protein = True
            if cat in ['Rice', 'Whole Grains', 'Millets & Whole Grains', 'Breakfast', 'Breads & Roti', 'Oats & Cereals']:
                has_carb = True
            if cat in ['Vegetables', 'Leafy Greens', 'Salad']:
                has_veg = True

            if cat.lower() in snack_allowed_cats or "fruit" in name or "smoothie" in name or "shake" in name or "nut" in name:
                has_snack_item = True

        mt = meal_type.lower()
        if mt == "breakfast":
            if curry_count >= 2:
                return False
            if salad_count >= 1:
                return False
            if has_rice and has_dal:
                return False

        elif mt == "lunch":
            if not (has_protein and has_carb and has_veg):
                if not (has_protein and has_carb):
                    return False

        elif mt == "dinner":
            if not (has_protein and has_carb):
                return False

        elif mt == "snack":
            if df in _MEAL_TYPE_BLOCKED_FAMILIES.get('snack', set()) or \
               (has_rice and has_dal) or has_rice:
                return False
            if not has_snack_item:
                return False

        return True

    def _is_valid_composition_with_reason(
        self, plate: List[Dict], meal_type: str, template: Dict = None
    ) -> Tuple[bool, str]:
        """Thin wrapper around _is_valid_composition that also returns a rejection reason.

        Duplicates the check sequence so each early-return can be labelled.
        The labels map directly to keys in rejection_stats inside generate_candidates().

        Reason labels are intentionally granular so the JSONL metrics file shows
        *which* rule fired instead of a single overloaded ``template_mismatch``:
          empty_plate, missing_role, forbidden_role, duplicate_food_id,
          duplicate_dish_family, meal_type_mismatch, meal_suitability_failure,
          breakfast_structure, snack_structure, missing_required_role.
        """
        if not plate:
            return False, "empty_plate"

        # Resolve each item's effective role: dynamically-assigned template_role
        # takes precedence, falling back to the dataset's synthesized meal_role.
        # NEVER read/write semantics["meal_role"] destructively here.
        roles_in_plate = [
            item.get("template_role") or item.get("semantics", {}).get("meal_role", "")
            for item in plate
        ]

        if template:
            is_blueprint = any(item.get("semantics", {}).get("meal_id") for item in plate)

            if not is_blueprint:
                for req in template.get("required", []):
                    req_role  = req.get("role")
                    req_count = req.get("count", 1)
                    match_count = roles_in_plate.count(req_role)
                    if match_count < req_count:
                        self._log_composition_reject(
                            "missing_role", meal_type, template, plate,
                            roles_in_plate, detail=f"role '{req_role}' x{req_count} "
                            f"required, found {match_count}",
                        )
                        return False, "missing_role"

            for forb in template.get("forbidden", []):
                if forb.get("role") in roles_in_plate:
                    self._log_composition_reject(
                        "forbidden_role", meal_type, template, plate,
                        roles_in_plate, detail=f"forbidden role '{forb.get('role')}' present",
                    )
                    return False, "forbidden_role"

        food_ids = [
            str(item.get("food_id") or item.get("food_name", "")).lower().strip()
            for item in plate
        ]
        if len(set(food_ids)) != len(food_ids):
            return False, "duplicate_food_id"

        dish_families = [
            item.get("semantics", {}).get("dish_family", "other") for item in plate
        ]
        non_other = [df for df in dish_families if df != "other"]
        if len(non_other) != len(set(non_other)):
            # Quality rule retained — log which foods collide on dish_family.
            if logger.isEnabledFor(logging.DEBUG):
                seen: Dict[str, str] = {}
                for item in plate:
                    fam = item.get("semantics", {}).get("dish_family", "other")
                    if fam == "other":
                        continue
                    fn = item.get("food_name", "")
                    if fam in seen:
                        logger.debug(
                            "[%s] duplicate_dish_family — '%s' & '%s' share dish_family=%s",
                            meal_type, seen[fam], fn, fam,
                        )
                    else:
                        seen[fam] = fn
            return False, "duplicate_dish_family"

        threshold = SUITABILITY_THRESHOLDS.get(meal_type.lower(), 50)
        for item in plate:
            fn = item.get("food_name", "")
            if not self._is_meal_type_suitable(fn, meal_type):
                self._log_composition_reject(
                    "meal_type_mismatch", meal_type, template, plate,
                    roles_in_plate, detail=f"'{fn}' not suitable for {meal_type}",
                )
                return False, "meal_type_mismatch"
            if get_meal_suitability(fn, meal_type) < threshold:
                self._log_composition_reject(
                    "meal_suitability_failure", meal_type, template, plate,
                    roles_in_plate,
                    detail=f"'{fn}' suitability {get_meal_suitability(fn, meal_type)} < {threshold}",
                )
                return False, "meal_suitability_failure"

        # ── Structural composition heuristics ────────────────────────────────
        # Category sets below MUST match the strings actually used in the dataset
        # (data/ingredient_database.json).  Phantom names left over from an older
        # schema (e.g. "Meat & Chicken", "Paneer & Tofu", "Seafood") silently
        # disabled protein detection for chicken/fish/paneer dishes — fixed here.
        _PROTEIN_CATS = {
            "Dal & Pulses", "Chicken/Meat", "Paneer", "Eggs", "Fish/Seafood",
            # legacy aliases kept for forward-compatibility:
            "Meat & Chicken", "Paneer & Tofu", "Seafood",
        }
        _CURRY_CATS = {
            "Dal & Pulses", "Chicken/Meat", "Paneer",
            "Meat & Chicken", "Paneer & Tofu",
        }
        _CARB_CATS = {
            "Rice", "Whole Grains", "Millets & Whole Grains", "Breakfast",
            "Breads & Roti", "Oats & Cereals",
        }
        _VEG_CATS = {"Vegetables", "Leafy Greens", "Salad"}

        curry_count = salad_count = 0
        has_rice = has_dal = has_protein = has_carb = has_veg = has_snack_item = False
        snack_allowed_cats = ['fruit', 'dairy', 'protein snack', 'nuts', 'smoothie', 'beverage']
        df = "other"

        for item, role in zip(plate, roles_in_plate):
            name = item.get("food_name", "").lower()
            sem  = item.get("semantics", {})
            cat  = sem.get("category", "")
            styles   = sem.get("cooking_style", "")
            pdensity = sem.get("protein_density", 0)
            df       = sem.get("dish_family", "other")

            if df in ("curry", "korma", "dal", "sambar") or \
               "Gravy" in styles or "Curry" in styles or \
               cat in _CURRY_CATS:
                curry_count += 1
            if "salad" in name or "raita" in name or cat == "Salad":
                salad_count += 1
            if df in ("rice", "plain_rice", "fried_rice", "pulao", "biryani") or \
               "rice" in name or "pulao" in name or "biryani" in name:
                has_rice = True
            if df == "dal" or "dal" in name or "sambar" in name:
                has_dal = True
            # Role-aware protein detection: trust an explicit protein role, the
            # corrected category set, or a high protein density.
            if role in ("protein_main", "curry") or pdensity > 0.12 or cat in _PROTEIN_CATS:
                has_protein = True
            if role == "carb_base" or cat in _CARB_CATS:
                has_carb = True
            if role in ("veg_side", "salad") or cat in _VEG_CATS:
                has_veg = True
            if cat.lower() in snack_allowed_cats or "fruit" in name or "smoothie" in name or "shake" in name or "nut" in name:
                has_snack_item = True

        mt = meal_type.lower()
        if mt == "breakfast":
            if curry_count >= 2 or salad_count >= 1 or (has_rice and has_dal):
                self._log_composition_reject(
                    "breakfast_structure", meal_type, template, plate, roles_in_plate,
                    detail=f"curry={curry_count} salad={salad_count} "
                    f"rice={has_rice} dal={has_dal}",
                )
                return False, "breakfast_structure"
        elif mt == "lunch":
            if not (has_protein and has_carb and has_veg):
                if not (has_protein and has_carb):
                    self._log_composition_reject(
                        "missing_required_role", meal_type, template, plate, roles_in_plate,
                        detail=f"protein={has_protein} carb={has_carb} veg={has_veg}",
                    )
                    return False, "missing_required_role"
        elif mt == "dinner":
            if not (has_protein and has_carb):
                self._log_composition_reject(
                    "missing_required_role", meal_type, template, plate, roles_in_plate,
                    detail=f"protein={has_protein} carb={has_carb}",
                )
                return False, "missing_required_role"
        elif mt == "snack":
            if df in _MEAL_TYPE_BLOCKED_FAMILIES.get('snack', set()) or \
               (has_rice and has_dal) or has_rice:
                self._log_composition_reject(
                    "snack_structure", meal_type, template, plate, roles_in_plate,
                    detail=f"df={df} rice={has_rice} dal={has_dal}",
                )
                return False, "snack_structure"
            if not has_snack_item:
                return False, "missing_required_role"

        return True, ""

    def _log_composition_reject(
        self,
        reason: str,
        meal_type: str,
        template: Dict,
        plate: List[Dict],
        roles_in_plate: List[str],
        detail: str = "",
    ) -> None:
        """Emit a structured DEBUG record describing a composition rejection.

        Shows template id, meal type, required/detected/missing roles and a
        per-food ``name -> meal_role / dish_family / category`` breakdown so the
        cause can be diagnosed from logs without re-reading the validator code.
        """
        if not logger.isEnabledFor(logging.DEBUG):
            return
        template = template or {}
        required_roles = [r.get("role") for r in template.get("required", [])]
        detected = [r for r in roles_in_plate if r]
        missing = [r for r in required_roles if roles_in_plate.count(r) < 1]
        food_lines = []
        for item in plate:
            sem = item.get("semantics", {})
            food_lines.append(
                f"    {item.get('food_name', '?')} -> "
                f"meal_role={item.get('template_role') or sem.get('meal_role', '')} "
                f"dish_family={sem.get('dish_family', 'other')} "
                f"category={sem.get('category', '')}"
            )
        logger.debug(
            "[%s][Template %s] reject=%s %s\n"
            "  Required roles: %s\n"
            "  Detected roles: %s\n"
            "  Missing roles : %s\n"
            "  Foods:\n%s",
            meal_type.upper(),
            template.get("template_id", template.get("id", "?")),
            reason,
            f"({detail})" if detail else "",
            required_roles or "(none)",
            detected or "(none)",
            missing or "(none)",
            "\n".join(food_lines) or "    (empty)",
        )


    def _get_blueprint_candidates(
        self,
        meal_type: str,
        diet_type: str,
        template: Dict,
        rng,
        max_prep_time: int,
        allowed_complexity: List[int],
        excluded_foods: Set[str] = None,
    ) -> List[List[Dict]]:
        excluded_foods = excluded_foods or set()
        threshold = SUITABILITY_THRESHOLDS.get(meal_type.lower(), 50)

        possible_meals = [
            m for m in self.meal_blueprints
            if m["meal_type"].lower() == meal_type.lower()
            and self._is_diet_compatible(m["diet_type"], diet_type)
        ]

        anchor_role = template.get('anchor', {}).get('role')
        if anchor_role:
            filtered = [m for m in possible_meals if m.get("anchor_role") == anchor_role]
            if filtered:
                possible_meals = filtered

        plates = []
        _DOMINANT_SIDES = {"tossed salad", "kachumber", "kachumber salad", "mixed salad"}

        for meal in possible_meals:
            plate = []
            valid = True
            used_ids_in_plate: Set[str] = set()

            for food_name in meal["foods"]:
                fn_lower = food_name.lower().strip()

                # Replace dominant/banned side items with a varied alternative
                if fn_lower in _DOMINANT_SIDES:
                    replaced = False
                    for _ in range(10):
                        cand_name = rng.choice(SIDE_OPTIONS)
                        cand_node = self._fuzzy_match_food(cand_name)
                        if cand_node is None:
                            continue
                        cand_id = str(cand_node.get("food_id", cand_name)).lower()
                        if cand_id in used_ids_in_plate or cand_id in excluded_foods:
                            continue
                        if not self._is_meal_type_suitable(cand_node.get("food_name", ""), meal_type):
                            continue
                        if get_meal_suitability(cand_node.get("food_name", ""), meal_type) < threshold:
                            continue
                        food_name = cand_name
                        replaced = True
                        break
                    if not replaced:
                        valid = False
                        break

                node = self._fuzzy_match_food(food_name)
                if node:
                    food_id = str(node.get("food_id", food_name)).lower()

                    # Cross-meal exclusion
                    if food_id in excluded_foods:
                        valid = False
                        break

                    # Within-plate deduplication by food_id
                    if food_id in used_ids_in_plate:
                        valid = False
                        break

                    # Hard meal-type check
                    if not self._is_meal_type_suitable(node.get("food_name", ""), meal_type):
                        valid = False
                        break

                    # Suitability score check
                    if get_meal_suitability(node.get("food_name", ""), meal_type) < threshold:
                        valid = False
                        break

                    semantics = node.get("semantics", {})
                    complexity = semantics.get("complexity_score", 5)
                    prep_time = semantics.get("prep_time_minutes", 15)

                    if prep_time > max_prep_time or complexity < allowed_complexity[0] or complexity > allowed_complexity[1]:
                        valid = False
                        break

                    node_copy = _unfreeze(node)
                    node_copy["semantics"] = dict(node_copy.get("semantics", {}))
                    node_copy["semantics"]["meal_id"] = meal["meal_id"]
                    node_copy["semantics"]["meal_name"] = meal["meal_name"]
                    node_copy["semantics"]["protein_source"] = meal.get("protein_source")
                    node_copy["semantics"]["carb_source"] = meal.get("carb_source")
                    node_copy["semantics"]["cuisine"] = meal.get("cuisine", "Pan Indian")
                    node_copy["semantics"]["cooking_style"] = meal.get("cooking_style", "Mixed")
                    plate.append(node_copy)
                    used_ids_in_plate.add(food_id)
                else:
                    valid = False
                    break

            if valid and plate:
                plates.append(plate)

        return plates

    def _quick_quality_filter(
        self,
        plate: List[Dict],
        meal_type: str,
        daily_protein: float,
        daily_calories: float,
        goal: str,
    ) -> Tuple[bool, float]:
        """
        Lightweight pre-optimization filter. Runs in O(n) per plate before SciPy LP.

        Returns: (passed: bool, penalty_score: float)
          - passed=False → hard reject (plate is structurally invalid).
          - passed=True  → plate is accepted; penalty_score >= 0 (0 = perfect).

        Hard rejects (return False):
          - Duplicate dish_family (already caught in _is_valid_composition, double-checked)
          - Duplicate protein main (primary_ingredient)
          - Calorie bounds violated (from NUTRITION_RULES)

        Soft penalties (reduce score, plate still passes):
          - Repeated cuisine
          - Repeated cooking style
          - Incompatible cuisine mix (soft penalty to prevent starvation)
          Penalty is returned as a float and attached to each item as _qf_penalty
          for the meal scorer to use.
        """
        if not plate:
            return False, 0.0

        # Load bounds from config
        cal_bounds = NUTRITION_RULES.get('calorie_distribution', {}).get(meal_type.lower(), {})
        cal_min = cal_bounds.get('min', 0.08) * daily_calories
        cal_max = cal_bounds.get('max', 0.45) * daily_calories

        # ── Per-item tracking ────────────────────────────────────────────
        used_dish_families:    set = set()
        used_protein_mains:    set = set()
        cuisine_votes:         dict = {}
        cooking_style_votes:   dict = {}

        # Load cuisine compatibility map from config
        compat_map = NUTRITION_RULES.get('cuisine_compatibility', {})

        # Soft penalty accumulator
        penalty = 0.0

        for item in plate:
            sem  = item.get('semantics', {})
            df   = sem.get('dish_family', 'other')
            pi   = sem.get('primary_ingredient', 'other')
            cu   = sem.get('cuisine', '') or ''
            cs   = sem.get('cooking_style', '') or ''
            role = sem.get('meal_role', '')

            # Hard: duplicate dish_family
            if df != 'other':
                if df in used_dish_families:
                    return False, 0.0
                used_dish_families.add(df)

            # Hard: duplicate primary_ingredient when role is protein_main
            if role == 'protein_main' and pi != 'other':
                if pi in used_protein_mains:
                    return False, 0.0
                used_protein_mains.add(pi)

            # Soft: track cuisine
            if cu:
                cuisine_votes[cu] = cuisine_votes.get(cu, 0) + 1

            # Soft: track cooking style
            if cs:
                cooking_style_votes[cs] = cooking_style_votes.get(cs, 0) + 1

        # ── Hard: calorie bounds (pre-optimization estimate) ─────────────
        if daily_calories > 0:
            raw_cals = sum(
                float(i.get('nutrition', {}).get('calories', 0)) for i in plate
            )
            # Only reject if clearly out of range (pre-optimization estimate, not exact)
            # Using scaling factor range [0.3, 3.0] to check feasibility
            if raw_cals * 4.0 < cal_min:    # cannot possibly reach minimum even at 4x scale
                return False, 0.0
            if raw_cals * 0.2 > cal_max:    # cannot possibly scale down to maximum even at 0.2x
                return False, 0.0

        # ── Soft: incompatible cuisine mix ───────────────────────────────
        detected_cuisines = set(cuisine_votes.keys())
        if len(detected_cuisines) >= 2:
            # Find if any two cuisines belong to different groups
            cuisine_groups = []
            for cu in detected_cuisines:
                for group_name, group_members in compat_map.items():
                    if cu in group_members:
                        cuisine_groups.append(group_name)
                        break
                else:
                    cuisine_groups.append(cu)   # unknown cuisine = its own group
            if len(set(cuisine_groups)) >= 2:
                # Incompatible cuisine mix: soft penalty instead of hard reject
                penalty += 30.0

        # Cuisine repetition: penalise if any cuisine appears >1 time
        for cu, count in cuisine_votes.items():
            if count > 1:
                penalty += (count - 1) * 10.0

        # Cooking style repetition: penalise if any style appears >1 time
        for cs, count in cooking_style_votes.items():
            if count > 1:
                penalty += (count - 1) * 8.0

        return True, penalty

    def _quick_quality_filter_with_reason(
        self,
        plate: List[Dict],
        meal_type: str,
        daily_protein: float,
        daily_calories: float,
        goal: str,
    ) -> Tuple[bool, float, str]:
        """Thin wrapper around _quick_quality_filter that also returns a reason string.

        Returns (passed, penalty, reason) where reason is a rejection_stats key or
        'cuisine_compat' for soft-penalty cuisine incompatibility (plate still passes).
        """
        if not plate:
            return False, 0.0, "empty_plate"

        cal_bounds = NUTRITION_RULES.get('calorie_distribution', {}).get(meal_type.lower(), {})
        cal_min = cal_bounds.get('min', 0.08) * daily_calories
        cal_max = cal_bounds.get('max', 0.45) * daily_calories

        used_dish_families: set = set()
        used_protein_mains: set = set()
        cuisine_votes: dict = {}
        cooking_style_votes: dict = {}
        compat_map = NUTRITION_RULES.get('cuisine_compatibility', {})
        penalty = 0.0

        for item in plate:
            sem  = item.get('semantics', {})
            df   = sem.get('dish_family', 'other')
            pi   = sem.get('primary_ingredient', 'other')
            cu   = sem.get('cuisine', '') or ''
            cs   = sem.get('cooking_style', '') or ''
            role = sem.get('meal_role', '')

            if df != 'other':
                if df in used_dish_families:
                    return False, 0.0, "duplicate_dish_family"
                used_dish_families.add(df)

            if role == 'protein_main' and pi != 'other':
                if pi in used_protein_mains:
                    return False, 0.0, "duplicate_protein_main"
                used_protein_mains.add(pi)

            if cu:
                cuisine_votes[cu] = cuisine_votes.get(cu, 0) + 1
            if cs:
                cooking_style_votes[cs] = cooking_style_votes.get(cs, 0) + 1

        if daily_calories > 0:
            raw_cals = sum(float(i.get('nutrition', {}).get('calories', 0)) for i in plate)
            if raw_cals * 4.0 < cal_min:
                return False, 0.0, "calorie_threshold"
            if raw_cals * 0.2 > cal_max:
                return False, 0.0, "calorie_threshold"

        cuisine_soft_flag = ""
        detected_cuisines = set(cuisine_votes.keys())
        if len(detected_cuisines) >= 2:
            cuisine_groups = []
            for cu in detected_cuisines:
                for group_name, group_members in compat_map.items():
                    if cu in group_members:
                        cuisine_groups.append(group_name)
                        break
                else:
                    cuisine_groups.append(cu)
            if len(set(cuisine_groups)) >= 2:
                penalty += 30.0
                cuisine_soft_flag = "cuisine_compat"

        for cu, count in cuisine_votes.items():
            if count > 1:
                penalty += (count - 1) * 10.0
        for cs, count in cooking_style_votes.items():
            if count > 1:
                penalty += (count - 1) * 8.0

        return True, penalty, cuisine_soft_flag


    def _build_fallback_meal(
        self,
        meal_type: str,
        diet_type: str,
        excluded_foods: Set[str],
        goal: str,
        meal_cals: float = 0,
    ) -> Optional[List[Dict]]:
        """
        Guaranteed fallback: always returns at least one valid plate.
        Uses a deterministic slot-fill strategy:
          1. Pick highest protein_density food that fits the meal type and diet
          2. Pick highest protein_density carb for that meal type
          3. If meal_cals > 800, add a side dish (e.g. dal or veg side) to provide enough volume.
          4. Return the assembled plate

        Does NOT score or optimize — hands the plate straight to the portion optimizer.
        Eliminates 'No valid candidates found' errors.
        """
        ingredients = list(self.food_graph.get_ingredients().values())

        def _is_eligible(node: dict) -> bool:
            fn  = node.get('food_name', '')
            fid = str(node.get('food_id', '')).lower()
            ing_diet = 'Vegan' if node.get('identity', {}).get('is_vegan') else (
                'Vegetarian' if node.get('identity', {}).get('is_vegetarian') else 'NonVeg'
            )
            if fid in excluded_foods:
                return False
            if not self._is_diet_compatible(ing_diet, diet_type):
                return False
            if not self._is_meal_type_suitable(fn, meal_type):
                return False
            return True

        eligible = [i for i in ingredients if _is_eligible(i)]
        if not eligible:
            return None

        # Sort by protein_density descending
        eligible.sort(
            key=lambda x: x.get('semantics', {}).get('protein_density', 0),
            reverse=True
        )

        # Slot 1: best protein source
        protein_node = eligible[0]
        used_df = {protein_node.get('semantics', {}).get('dish_family', 'other')}
        used_pi = {protein_node.get('semantics', {}).get('primary_ingredient', 'other')}

        # Slot 2: best carb that does not repeat dish_family
        carb_categories = {'Rice', 'Whole Grains', 'Millets & Whole Grains',
                           'Breakfast', 'Breads & Roti', 'Oats & Cereals'}
        carb_node = None
        for node in eligible[1:]:
            sem = node.get('semantics', {})
            cat = sem.get('category', '')
            df  = sem.get('dish_family', 'other')
            if cat not in carb_categories:
                continue
            if df != 'other' and df in used_df:
                continue
            carb_node = node
            break

        plate = [_unfreeze(protein_node)]
        if carb_node:
            plate.append(_unfreeze(carb_node))
            used_df.add(carb_node.get('semantics', {}).get('dish_family', 'other'))

        # Slot 3: Side dish if meal target calories are high (> 800 kcal)
        if meal_cals > 800:
            side_categories = {'Dal & Pulses', 'Vegetables', 'Leafy Greens', 'Salad', 'Paneer & Tofu'}
            for node in eligible:
                if node.get('food_id') in (protein_node.get('food_id'), carb_node.get('food_id') if carb_node else None):
                    continue
                sem = node.get('semantics', {})
                cat = sem.get('category', '')
                df  = sem.get('dish_family', 'other')
                if cat not in side_categories:
                    continue
                if df != 'other' and df in used_df:
                    continue
                plate.append(_unfreeze(node))
                break

        logger.info(
            f"[FallbackMealBuilder] Built {meal_type} plate (meal_cals={meal_cals:.1f}): "
            + ", ".join(n.get('food_name', '') for n in plate)
        )
        return plate

    def _pick_food_for_role(
        self,
        role: str,
        meal_type: str,
        diet_type: str,
        used_df: Set[str],
        used_ids: Set[str],
        valid_ings: List[Dict],
        rng,
        goal_score_fn,
    ) -> Optional[Dict]:
        """Pick one food item that satisfies a template slot role.

        Respects:
        - Diet compatibility (already filtered into valid_ings)
        - Meal-type suitability (already filtered into valid_ings)
        - No dish_family collision with items already placed on this plate (used_df)
        - No food_id collision with items already placed (used_ids)

        Returns a deep-unfrozen copy of the food node, or None if no candidate found.
        """
        # Role → category/dish_family hints for weighted sampling
        _ROLE_CATEGORIES: Dict[str, Set[str]] = {
            "protein_main":   {'Dal & Pulses', 'Paneer & Tofu', 'Meat & Chicken',
                               'Eggs', 'Seafood', 'Soya & Tofu'},
            "carb_base":      {'Rice', 'Whole Grains', 'Millets & Whole Grains',
                               'Breakfast', 'Breads & Roti', 'Oats & Cereals'},
            "curry":          {'Dal & Pulses', 'Vegetables', 'Paneer & Tofu',
                               'Meat & Chicken'},
            "veg_side":       {'Vegetables', 'Leafy Greens'},
            "salad":          {'Salad'},
            "dairy_side":     {'Dairy & Eggs', 'Curd & Yogurt'},
            "combo_meal":     {'Dal & Pulses', 'Paneer & Tofu', 'Meat & Chicken',
                               'Rice', 'Breads & Roti'},
            "beverage":       {'Beverages'},
        }
        preferred_cats = _ROLE_CATEGORIES.get(role, set())

        # Split candidates into preferred (match role categories) and fallback
        preferred = []
        fallback  = []
        for ing in valid_ings:
            fid = str(ing.get('food_id', ing.get('food_name', ''))).lower()
            df  = ing.get('semantics', {}).get('dish_family', 'other')
            cat = ing.get('semantics', {}).get('category', '')

            if fid in used_ids:
                continue
            if df != 'other' and df in used_df:
                continue

            if cat in preferred_cats or not preferred_cats:
                preferred.append(ing)
            else:
                fallback.append(ing)

        if not preferred:
            logger.debug(
                "[_pick_food_for_role][%s] No preferred-category food for role='%s'; "
                "falling back. valid_cats=%s",
                meal_type, role,
                {i.get('semantics', {}).get('category') for i in valid_ings},
            )
        pool = preferred or fallback
        if not pool:
            return None

        scores = [max(0.001, goal_score_fn(ing)) for ing in pool]
        total  = sum(scores)
        weights = [s / total for s in scores]
        return _unfreeze(rng.choices(pool, weights=weights, k=1)[0])

    def _get_dynamic_candidates(
        self,
        template: Dict[str, Any],
        meal_type: str,
        diet_type: str,
        rng,
        excluded_foods: Set[str] = None,
        goal: str = 'Maintenance',
        target_cuisine: str = '',
        daily_context: 'DailyMealContext' = None,
    ) -> List[List[Dict]]:
        """Template-driven dynamic candidate generation (Phase 1A).

        The generator fills whatever slots `template["required"]` defines.
        It never knows the shape of a meal — the template does.
        This means adding a vegetable slot, a raita slot, or a millet slot to
        any template automatically populates that slot here without code changes.

        Weighted sampling is goal-aware and diversity-penalised by DailyMealContext.
        """
        excluded_foods  = excluded_foods or set()
        daily_context   = daily_context or DailyMealContext()
        threshold = SUITABILITY_THRESHOLDS.get(meal_type.lower(), 50)
        ingredients = list(self.food_graph.get_ingredients().values())

        # Goal-based weight vectors: (protein_density, role_match, cuisine_match, compatibility)
        _GOAL_WEIGHTS = {
            'Muscle Gain':  (0.45, 0.25, 0.15, 0.15),
            'Weight Loss':  (0.35, 0.25, 0.20, 0.20),
            'Maintenance':  (0.20, 0.25, 0.30, 0.25),
        }
        w_pd, w_role, w_cuis, w_compat = _GOAL_WEIGHTS.get(goal, _GOAL_WEIGHTS['Maintenance'])

        # Expected meal roles per meal_type (for role_match score)
        _EXPECTED_ROLES = {
            'breakfast': {'carb_base', 'protein_main'},
            'lunch':     {'protein_main', 'curry', 'carb_base', 'veg_side'},
            'dinner':    {'protein_main', 'curry', 'carb_base'},
            'snack':     {'dairy_side', 'salad', 'protein_main'},
        }
        expected_roles = _EXPECTED_ROLES.get(meal_type.lower(), set())

        # Pre-filter: diet + meal-type suitability + exclusion
        valid_ings: List[Dict] = []
        for ing in ingredients:
            ing_diet = 'Vegan' if ing.get('identity', {}).get('is_vegan') else (
                'Vegetarian' if ing.get('identity', {}).get('is_vegetarian') else 'NonVeg'
            )
            food_id = str(ing.get('food_id', '')).lower()
            fn = ing.get('food_name', '')

            if food_id in excluded_foods:
                continue
            if not self._is_meal_type_suitable(fn, meal_type):
                continue
            if get_meal_suitability(fn, meal_type) < threshold:
                continue
            if not self._is_diet_compatible(ing_diet, diet_type):
                continue
            valid_ings.append(ing)

        if not valid_ings:
            return []

        def _goal_score(node: dict) -> float:
            sem  = node.get('semantics', {})
            pd   = min(sem.get('protein_density', 0.0) / 0.30, 1.0)
            role = sem.get('meal_role', '')
            cu   = sem.get('cuisine', '') or ''

            role_score    = 1.0 if role in expected_roles else 0.3
            cuisine_score = 1.0 if (target_cuisine and cu == target_cuisine) else 0.5
            compat_score  = 0.5

            base = (
                w_pd    * pd +
                w_role  * role_score +
                w_cuis  * cuisine_score +
                w_compat * compat_score
            )
            return base * daily_context.diversity_weight(node)

        # Determine required slots from template; fall back to a sensible default
        required_slots = template.get("required", [])
        if not required_slots:
            # Template has no required slots — use a bare protein+carb default so
            # dynamic generation still produces something useful.
            required_slots = [
                {"role": "protein_main", "count": 1},
                {"role": "carb_base",    "count": 1},
            ]
            logger.debug(
                "[_get_dynamic_candidates][%s] Template has no required slots; "
                "using default [protein_main, carb_base]",
                meal_type,
            )

        # Generate N candidate plates, each filled slot-by-slot from the template
        perf = NUTRITION_RULES.get('performance', {})
        n_dynamic = perf.get('max_candidates_per_meal', 15)

        combos: List[List[Dict]] = []
        for _attempt in range(n_dynamic * 3):   # over-sample; duplicates are later filtered
            plate: List[Dict] = []
            used_df:  Set[str] = set()
            used_ids: Set[str] = set()
            plate_valid = True

            for slot in required_slots:
                slot_role  = slot.get("role", "")
                slot_count = slot.get("count", 1)

                for _ in range(slot_count):
                    food = self._pick_food_for_role(
                        role=slot_role,
                        meal_type=meal_type,
                        diet_type=diet_type,
                        used_df=used_df,
                        used_ids=used_ids,
                        valid_ings=valid_ings,
                        rng=rng,
                        goal_score_fn=_goal_score,
                    )
                    if food is None:
                        logger.debug(
                            "[_get_dynamic_candidates][%s] No food found for slot role='%s' — skipping plate",
                            meal_type, slot_role,
                        )
                        plate_valid = False
                        break

                    fid = str(food.get('food_id', food.get('food_name', ''))).lower()
                    df  = food.get('semantics', {}).get('dish_family', 'other')
                    
                    if "semantics" not in food:
                        food["semantics"] = {}
                    # GUARDRAIL: assign the template slot role to a SEPARATE field.
                    # Never write food["semantics"]["meal_role"] — that would destroy
                    # the dataset's original metadata. Validators read template_role
                    # first, then fall back to semantics.meal_role.
                    food["template_role"] = slot_role

                    used_ids.add(fid)
                    used_df.add(df)
                    plate.append(food)

                if not plate_valid:
                    break

            if plate_valid and plate:
                combos.append(plate)

            if len(combos) >= n_dynamic:
                break

        return combos

    def _diversity_filter(self, candidates: List[List[Dict]], top_n_percent: float = 0.5, score_fn=None) -> List[List[Dict]]:
        """
        Filters candidates by abstract Meal Signature to avoid clustered variants.
        """
        seen_signatures = set()
        diverse_candidates = []
        
        for plate in candidates:
            # Generate signature
            sig_parts = []
            for item in plate:
                sem = item.get("semantics", {})
                cat = sem.get("category", "")
                cuisine = sem.get("cuisine", "")
                sig_parts.append(f"{cat}-{cuisine}")
            
            sig_parts.sort()
            signature = "|".join(sig_parts)
            
            if signature not in seen_signatures:
                seen_signatures.add(signature)
                diverse_candidates.append(plate)
                
        # Sort by score if provided so we keep the best diverse candidates
        if score_fn:
            diverse_candidates.sort(key=score_fn, reverse=True)
            
        # Keep only the requested top percentage based on variety
        num_keep = max(1, int(len(diverse_candidates) * top_n_percent))
        return diverse_candidates[:num_keep]
