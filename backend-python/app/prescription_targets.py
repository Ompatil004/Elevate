# -*- coding: utf-8 -*-
"""
prescription_targets.py — Single source of truth for daily water and sleep targets.

Implements the target logic from the Smart Health Prescription System plan (Sections 5.1 & 5.2).
All routes and engines should import from here rather than hardcoding targets.

Water target:
    weight_loss / weight_gain → 3,000–3,500 ml
    maintain                  → 2,500–3,000 ml
    Age < 18 or > 60          → reduce by 300 ml
    Age 36–60                 → increase by 200 ml

Sleep target:
    beginner     → 8.0 hours
    intermediate → 8.5 hours
    advanced     → 8.5 hours
"""

from __future__ import annotations
from typing import Union


# ── Water targets (ml) ─────────────────────────────────────────────────────

_WATER_BASE_ML: dict[str, int] = {
    'weight_loss': 3250,    # midpoint of 3,000–3,500
    'maintain':    2750,    # midpoint of 2,500–3,000
    'weight_gain': 3250,    # midpoint of 3,000–3,500
    # Alias keys used in existing codebase
    'muscle_gain': 3250,
    'Muscle Gain': 3250,
    'Weight Loss': 3250,
    'Maintain':    2750,
}

_WATER_AGE_DELTA_ML: int = 200   # add for 36–60
_WATER_YOUNG_OLD_DELTA_ML: int = 300  # subtract for <18 or >60


def get_water_target(goal: str, age: Union[int, float]) -> int:
    """
    Return recommended daily water intake in ml for the given goal and age.

    Args:
        goal: One of 'weight_loss', 'maintain', 'weight_gain' (case-insensitive)
        age:  User's age in years

    Returns:
        Target water intake in ml (integer)

    Examples:
        >>> get_water_target('weight_loss', 28)
        3250
        >>> get_water_target('maintain', 45)   # age 36-60 → +200
        2950
        >>> get_water_target('weight_gain', 70) # >60 → -300
        2950
    """
    goal_key = str(goal).strip().lower().replace(' ', '_')
    base = _WATER_BASE_ML.get(goal_key, _WATER_BASE_ML.get(goal, 2750))

    age = int(float(age or 25))

    if age < 18 or age > 60:
        base -= _WATER_YOUNG_OLD_DELTA_ML
    elif 36 <= age <= 60:
        base += _WATER_AGE_DELTA_ML

    return max(1500, base)   # never below 1.5 L (absolute minimum)


# ── Sleep targets (hours) ──────────────────────────────────────────────────

_SLEEP_OPTIMAL_HOURS: dict[str, float] = {
    'beginner':     8.0,
    'intermediate': 8.5,
    'advanced':     8.5,
    # Alias keys
    'Beginner':     8.0,
    'Intermediate': 8.5,
    'Advanced':     8.5,
}

_SLEEP_MINIMUM_HOURS: dict[str, float] = {
    'beginner':     7.0,
    'intermediate': 7.5,
    'advanced':     8.0,
    'Beginner':     7.0,
    'Intermediate': 7.5,
    'Advanced':     8.0,
}


def get_sleep_target(level: str, *, optimal: bool = True) -> float:
    """
    Return recommended sleep hours for the given experience level.

    Args:
        level:   One of 'beginner', 'intermediate', 'advanced'
        optimal: If True return optimal hours, else return minimum hours

    Returns:
        Sleep target in hours (float)

    Examples:
        >>> get_sleep_target('beginner')
        8.0
        >>> get_sleep_target('advanced', optimal=False)
        8.0
    """
    level_key = str(level or 'beginner').strip()
    if optimal:
        return _SLEEP_OPTIMAL_HOURS.get(level_key, 8.0)
    return _SLEEP_MINIMUM_HOURS.get(level_key, 7.0)


# ── Convenience: both targets in one call ──────────────────────────────────

def get_prescription_targets(goal: str, level: str, age: Union[int, float]) -> dict:
    """
    Return both water and sleep targets together.

    Returns:
        {
            'water_target_ml':     int,
            'sleep_target_hours':  float,
            'sleep_minimum_hours': float,
        }
    """
    return {
        'water_target_ml':     get_water_target(goal, age),
        'sleep_target_hours':  get_sleep_target(level, optimal=True),
        'sleep_minimum_hours': get_sleep_target(level, optimal=False),
    }
