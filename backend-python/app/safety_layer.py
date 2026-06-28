"""
safety_layer.py - Lightweight safety compliance patch for Elevate.

This module applies conservative safety adjustments for users who declare
medical conditions or injuries.  It is intentionally minimal:

  - All thresholds, indicators, and blocked patterns come from YAML config.
  - NO medical diagnosis is performed.
  - NO exact-string matching for conditions (partial, case-insensitive only).
  - NO exercise name matching (metadata Check_Type column only).
  - Applied AFTER existing AI calculations - never replaces them.

Public API
----------
  has_condition(user_conditions, indicators)            -> bool
  apply_nutrition_safety(daily_targets, profile, rules) -> (dict, list[str])
  filter_exercises_by_movement(df, blocked_types)       -> (DataFrame, int)
  validate_workout_safety(weekly_plan, profile, workout_rules, engine) -> (list, list[str], list[str])
  build_safety_response(adjustments, warnings, rules)   -> dict
  log_safety_adjustment(condition, adjustment)          -> None
"""

from __future__ import annotations

import logging
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Tuple

logger = logging.getLogger(__name__)


def _normalise(text: str) -> str:
    """Lowercase and strip whitespace for comparison."""
    return str(text).lower().strip()


# ---------------------------------------------------------------------------
# 1. Condition detection
# ---------------------------------------------------------------------------

def has_condition(user_conditions: List[str], indicators: List[str]) -> bool:
    """Return True if any indicator is a substring of any declared condition.

    Rules:
    - Case-insensitive partial substring match.
    - Returns False immediately when either list is empty.
    """
    if not user_conditions or not indicators:
        return False
    normalised_conditions = [_normalise(c) for c in user_conditions]
    normalised_indicators = [_normalise(ind) for ind in indicators]
    for condition in normalised_conditions:
        for indicator in normalised_indicators:
            if indicator in condition:
                return True
    return False


# ---------------------------------------------------------------------------
# 2. Nutrition safety adjustments
# ---------------------------------------------------------------------------

def _set_macro(targets: dict, macro: str, value: float) -> None:
    """Update all key aliases for a macro in the targets dict."""
    aliases = {
        "carbs":   ["carbs_g", "carbs", "carbohydrates_g", "carbohydrates"],
        "protein": ["protein_g", "protein"],
        "fat":     ["fat_g", "fat"],
    }
    for key in aliases.get(macro, [macro]):
        if key in targets:
            targets[key] = value


def apply_nutrition_safety(
    daily_targets: Dict[str, Any],
    user_profile: Dict[str, Any],
    nutrition_rules: Dict[str, Any],
) -> Tuple[Dict[str, Any], List[str]]:
    """Apply conservative macro adjustments for declared medical conditions.

    Called AFTER WeeklyMacroPlanner.plan_week(). Returns a copy of
    daily_targets with caps applied plus a list of applied adjustment labels.
    """
    import copy
    adjusted = copy.deepcopy(daily_targets)
    adjustments_applied: List[str] = []

    safety_cfg = nutrition_rules.get("medical_safety", {})
    if not safety_cfg:
        return adjusted, adjustments_applied

    user_conditions: List[str] = []
    for field in ("medical_conditions", "health_conditions", "body_issues"):
        val = user_profile.get(field)
        if isinstance(val, list):
            user_conditions.extend(val)
        elif isinstance(val, str) and val:
            user_conditions.append(val)

    if not user_conditions:
        return adjusted, adjustments_applied

    indicators_cfg = safety_cfg.get("medical_condition_indicators", {})
    adjustments_cfg = safety_cfg.get("safety_adjustments", {})
    processing_order = safety_cfg.get("safety_adjustment_order", list(adjustments_cfg.keys()))

    for condition_key in processing_order:
        indicators = indicators_cfg.get(condition_key, [])
        if not has_condition(user_conditions, indicators):
            continue

        adj = adjustments_cfg.get(condition_key, {})
        if not adj:
            continue

        label = adj.get("label", condition_key)

        # Carbohydrate cap
        carb_max = adj.get("carb_max_g")
        if carb_max is not None:
            current = float(adjusted.get("carbs_g", adjusted.get("carbs", 0)) or 0)
            if current > carb_max:
                _set_macro(adjusted, "carbs", carb_max)
                log_safety_adjustment(condition_key, f"carbs capped {current:.0f}g -> {carb_max}g")
                adjustments_applied.append(label)

        # Protein multiplier
        protein_mult = adj.get("protein_multiplier")
        if protein_mult is not None:
            current = float(adjusted.get("protein_g", adjusted.get("protein", 0)) or 0)
            new_val = round(current * protein_mult, 1)
            if new_val < current:
                _set_macro(adjusted, "protein", new_val)
                log_safety_adjustment(condition_key, f"protein {current:.0f}g -> {new_val}g (x{protein_mult})")
                adjustments_applied.append(label)

        # Fat cap
        fat_max = adj.get("fat_max_g")
        if fat_max is not None:
            current = float(adjusted.get("fat_g", adjusted.get("fat", 0)) or 0)
            if current > fat_max:
                _set_macro(adjusted, "fat", fat_max)
                log_safety_adjustment(condition_key, f"fat capped {current:.0f}g -> {fat_max}g")
                adjustments_applied.append(label)

    return adjusted, adjustments_applied


# ---------------------------------------------------------------------------
# 3. Workout safety - exercise pool filter
# ---------------------------------------------------------------------------

def filter_exercises_by_movement(exercises_df, blocked_check_types: List[str]):
    """Filter exercise DataFrame by Check_Type metadata column.

    Never uses exercise names. Returns (filtered_df, blocked_count).
    """
    if exercises_df is None or exercises_df.empty or not blocked_check_types:
        return exercises_df, 0

    if "Check_Type" not in exercises_df.columns:
        logger.warning("[SafetyLayer] Check_Type column missing - injury movement filter skipped")
        return exercises_df, 0

    normalised_blocked = {_normalise(ct) for ct in blocked_check_types}
    mask = exercises_df["Check_Type"].apply(
        lambda ct: _normalise(str(ct)) not in normalised_blocked if ct and str(ct).strip() else True
    )
    filtered = exercises_df[mask]
    return filtered, len(exercises_df) - len(filtered)


# ---------------------------------------------------------------------------
# 4. Workout safety - post-generation plan validation
# ---------------------------------------------------------------------------

def validate_workout_safety(
    weekly_plan: List[Dict[str, Any]],
    user_profile: Dict[str, Any],
    workout_rules: Dict[str, Any],
    engine: Any,
) -> Tuple[List[Dict[str, Any]], List[str], List[str]]:
    """Post-generation safety pass over the weekly plan.

    Removes exercises whose Check_Type matches an active injury-blocked pattern.
    Applies age-based multipliers to intensity/volume/rest for seniors.
    Adds fallback warnings when a day is left with no exercises.

    Returns (validated_plan, adjustments_applied, warnings).
    """
    import copy
    import re

    validated_plan = copy.deepcopy(weekly_plan)
    adjustments_applied: List[str] = []
    warnings: List[str] = []

    safety_cfg = workout_rules.get("safety", {})
    if not safety_cfg:
        return validated_plan, adjustments_applied, warnings

    # 1. Age/Senior adjustments
    age_cfg = workout_rules.get("age_scheduling", {})
    senior_age = age_cfg.get("senior_age", 60)
    try:
        user_age = int(float(user_profile.get("age", 30)))
    except Exception:
        user_age = 30

    is_senior = user_age >= senior_age
    senior_adjustments_triggered = False

    if is_senior:
        senior_int_mod = safety_cfg.get("senior_intensity_modifier", 0.85)
        senior_vol_mod = safety_cfg.get("senior_volume_modifier", 0.80)
        senior_rest_mult = safety_cfg.get("senior_rest_multiplier", 1.25)

        for day in validated_plan:
            if day.get("type") != "workout":
                continue

            # Modify daily intensity
            if "intensity" in day:
                day["intensity"] = round(day["intensity"] * senior_int_mod, 2)
            if isinstance(day.get("intensity_metrics"), dict) and "intensity_score" in day["intensity_metrics"]:
                day["intensity_metrics"]["intensity_score"] = round(day["intensity_metrics"]["intensity_score"] * senior_int_mod, 2)

            # Modify exercises and warmup exercises
            for key in ("exercises", "warmup"):
                for ex in day.get(key, []):
                    # Scale sets
                    if "sets" in ex:
                        try:
                            orig_sets = int(ex["sets"])
                            new_sets = max(1, round(orig_sets * senior_vol_mod))
                            if new_sets != orig_sets:
                                ex["sets"] = new_sets
                                senior_adjustments_triggered = True
                        except Exception:
                            pass
                    # Scale rest time
                    if "rest" in ex:
                        try:
                            rest_str = str(ex["rest"])
                            nums = re.findall(r"\d+", rest_str)
                            if nums:
                                orig_val = int(nums[0])
                                new_val = int(((orig_val * senior_rest_mult) + 2.5) // 5) * 5
                                if new_val != orig_val:
                                    ex["rest"] = rest_str.replace(nums[0], str(new_val))
                                    senior_adjustments_triggered = True
                        except Exception:
                            pass

        if senior_adjustments_triggered or is_senior:
            adjustments_applied.append("senior_adjustments")
            log_safety_adjustment("senior", f"applied age caps (age={user_age})")

    # 2. Injury adjustments (filtering by Check_Type)
    injury_patterns = safety_cfg.get("injury_blocked_patterns", {})
    if injury_patterns:
        user_conditions: List[str] = []
        for field in ("body_issues", "medical_conditions", "health_conditions", "injuries"):
            val = user_profile.get(field)
            if isinstance(val, list):
                user_conditions.extend(val)
            elif isinstance(val, str) and val:
                user_conditions.append(val)

        if user_conditions:
            active_conditions: List[str] = []
            all_blocked_types: set = set()

            for condition_key, cfg in injury_patterns.items():
                indicators = cfg.get("condition_indicators", [])
                if has_condition(user_conditions, indicators):
                    active_conditions.append(condition_key)
                    for ct in cfg.get("blocked_check_types", []):
                        all_blocked_types.add(_normalise(ct))
                    log_safety_adjustment(condition_key, f"active - blocking: {cfg.get('blocked_check_types', [])}")

            if all_blocked_types:
                fallback_warning = safety_cfg.get(
                    "fallback_warning",
                    "Some exercises were adjusted due to your reported condition.",
                )

                for day in validated_plan:
                    if day.get("type") != "workout":
                        continue

                    original_exercises = day.get("exercises", [])
                    kept: List[Dict[str, Any]] = []
                    removed_count = 0

                    for ex in original_exercises:
                        check_type = _normalise(str(ex.get("check_type", ex.get("Check_Type", "")) or ""))
                        if check_type and check_type in all_blocked_types:
                            removed_count += 1
                            log_safety_adjustment(
                                "/".join(active_conditions),
                                f"removed exercise (check_type={check_type})"
                            )
                        else:
                            kept.append(ex)

                    if removed_count == 0:
                        continue

                    if not kept:
                        logger.warning(
                            "[SafetyLayer] All exercises removed for day '%s' after injury filter",
                            day.get("day", "?"),
                        )
                        warnings.append(f"{fallback_warning} (Day: {day.get('day', 'Unknown')})")
                        day["exercises"] = []
                        day["exercises_total"] = 0
                        day["safety_warning"] = fallback_warning
                    else:
                        day["exercises"] = kept
                        day["exercises_total"] = len(kept)

                for c in active_conditions:
                    adjustments_applied.append(f"{c}_filter")

    return validated_plan, adjustments_applied, warnings


# ---------------------------------------------------------------------------
# 5. Build API response fields
# ---------------------------------------------------------------------------

def build_safety_response(
    adjustments_applied: List[str],
    warnings: List[str],
    rules: Dict[str, Any],
    *,
    rules_key: str = "medical_safety",
) -> Dict[str, Any]:
    """Build standardised safety fields for an API response.

    Returns dict with 'medical_adjustments_applied', 'medical_disclaimer',
    and 'safety_warnings'. All empty/blank when no adjustments fired.
    """
    disclaimer = ""
    if adjustments_applied:
        disclaimer = str(
            rules.get(rules_key, {}).get("medical_disclaimer", "")
        ).strip()

    return {
        "medical_adjustments_applied": adjustments_applied,
        "medical_disclaimer": disclaimer,
        "safety_warnings": warnings,
    }


# ---------------------------------------------------------------------------
# 6. Internal audit logging
# ---------------------------------------------------------------------------

def log_safety_adjustment(condition: str, adjustment: str) -> None:
    """Log a safety adjustment (DEBUG level, never exposed to frontend)."""
    ts = datetime.now(timezone.utc).isoformat()
    logger.debug(
        "SAFETY_ADJUSTMENT_APPLIED | condition=%s | adjustment=%s | ts=%s",
        condition, adjustment, ts,
    )
