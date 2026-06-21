# -*- coding: utf-8 -*-
"""
adaptive_modifier.py — Priority 3: Weekly adaptive plan modifier.

Reads the last 7 daily check-ins (sleep_hours, water_ml, workout_completed)
from the daily_logs collection and returns a lightweight modifier dict that
profile.py applies before regenerating a plan.

Logic:
  - avg_sleep < 6 h        → recovery deload: −10% intensity
  - avg_water_ml < 1500    → dehydration: −5% intensity + flag
  - workout_streak ≥ 4/7   → consistency bonus: +1 bonus set
  - workout_streak < 2/7   → attendance gap: skip volume increase this week

These modifiers are advisory; they are applied inside the workout engine's
compute_progression() via the workout_stats dict.
"""

from __future__ import annotations
from typing import Dict, List, Optional, Any
import logging

logger = logging.getLogger(__name__)


def compute_adaptive_modifiers(weekly_logs: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Compute plan modifiers from the last 7 daily check-in logs.

    Args:
        weekly_logs: list of daily_log documents, each with keys:
            sleep_hours (float), water_ml (float), workout_completed (bool)

    Returns:
        {
            'intensity_delta':  float,   # e.g. -0.10 means reduce by 10%
            'bonus_sets':       int,     # extra sets from consistency
            'skip_volume':      bool,    # True → do not increase volume
            'dehydration_flag': bool,    # True → user is chronically dehydrated
            'deload_flag':      bool,    # True → full deload recommended
            'reason':           str,     # human-readable explanation
            'days_logged':      int,
        }
    """
    default: Dict[str, Any] = {
        'intensity_delta': 0.0,
        'bonus_sets': 0,
        'skip_volume': False,
        'dehydration_flag': False,
        'deload_flag': False,
        'reason': 'No check-in data available — using baseline plan.',
        'days_logged': 0,
    }

    if not weekly_logs:
        return default

    n = len(weekly_logs)

    avg_sleep = sum(float(l.get('sleep_hours', 7.0) or 7.0) for l in weekly_logs) / n
    avg_water = sum(float(l.get('water_ml', 2000) or 2000) for l in weekly_logs) / n
    workout_days = sum(1 for l in weekly_logs if l.get('workout_completed', False))

    intensity_delta = 0.0
    bonus_sets = 0
    skip_volume = False
    dehydration_flag = False
    deload_flag = False
    reasons: List[str] = []

    # ── Sleep-based recovery modifier ─────────────────────────────────────────
    if avg_sleep < 5.0:
        intensity_delta -= 0.15
        deload_flag = True
        reasons.append(f'avg sleep {avg_sleep:.1f} h (critical) → full deload')
    elif avg_sleep < 6.0:
        intensity_delta -= 0.10
        reasons.append(f'avg sleep {avg_sleep:.1f} h (low) → -10% intensity')
    elif avg_sleep >= 8.0:
        intensity_delta += 0.03
        reasons.append(f'avg sleep {avg_sleep:.1f} h (excellent) → +3% intensity')

    # ── Hydration-based modifier ───────────────────────────────────────────────
    if avg_water < 1000:
        intensity_delta -= 0.10
        dehydration_flag = True
        reasons.append(f'avg water {avg_water:.0f} ml (severe) → -10% intensity')
    elif avg_water < 1500:
        intensity_delta -= 0.05
        dehydration_flag = True
        reasons.append(f'avg water {avg_water:.0f} ml (low) → -5% intensity')

    # ── Workout attendance modifier ────────────────────────────────────────────
    attendance_rate = workout_days / n
    if attendance_rate >= (4 / 7):
        bonus_sets = 1
        reasons.append(f'{workout_days}/{n} workouts completed → +1 bonus set')
    elif attendance_rate < (2 / 7):
        skip_volume = True
        reasons.append(f'only {workout_days}/{n} workouts — skip volume increase this week')

    # ── Clamp intensity delta to reasonable bounds ─────────────────────────────
    intensity_delta = max(-0.25, min(0.10, round(intensity_delta, 3)))

    return {
        'intensity_delta': intensity_delta,
        'bonus_sets': bonus_sets,
        'skip_volume': skip_volume,
        'dehydration_flag': dehydration_flag,
        'deload_flag': deload_flag,
        'reason': '; '.join(reasons) if reasons else 'Baseline — all biometrics normal.',
        'days_logged': n,
        'avg_sleep_hours': round(avg_sleep, 1),
        'avg_water_ml': round(avg_water),
        'workout_completion_rate': round(attendance_rate, 2),
    }


def apply_modifiers_to_workout_stats(
    workout_stats: Dict[str, Any],
    modifiers: Dict[str, Any],
) -> Dict[str, Any]:
    """
    Apply adaptive modifiers to the workout_stats dict before passing
    it to compute_progression().

    The caller (profile.py / server.py) is responsible for obtaining both
    the workout_stats and the modifiers and combining them here.
    """
    if not modifiers or not isinstance(modifiers, dict):
        return workout_stats

    merged = dict(workout_stats)

    # Apply intensity delta
    if 'intensity_delta' in modifiers:
        cur = float(merged.get('intensity_delta', 0.0) or 0.0)
        merged['intensity_delta'] = round(cur + modifiers['intensity_delta'], 3)

    # Bonus sets
    if modifiers.get('bonus_sets'):
        merged['adaptive_bonus_sets'] = int(modifiers['bonus_sets'])

    # Skip volume flag
    if modifiers.get('skip_volume'):
        merged['skip_volume_increase'] = True

    # Deload flag overrides everything
    if modifiers.get('deload_flag'):
        merged['force_deload'] = True

    merged['adaptive_reason'] = modifiers.get('reason', '')
    return merged
