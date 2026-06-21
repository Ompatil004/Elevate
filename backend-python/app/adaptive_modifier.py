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


def compute_adaptive_modifiers(
    weekly_logs: List[Dict[str, Any]],
    *,
    water_target_ml: int = 2750,
    sleep_target_hours: float = 8.0,
) -> Dict[str, Any]:
    """
    Compute plan modifiers from the last 7 daily check-in logs.

    Args:
        weekly_logs:       list of daily_log documents, each with keys:
                           sleep_hours (float), water_ml (float), workout_completed (bool)
        water_target_ml:   user's personalised daily water target (from prescription_targets)
        sleep_target_hours: user's optimal sleep target (from prescription_targets)

    Returns:
        {
            'intensity_delta':  float,   # e.g. -0.10 means reduce by 10%
            'bonus_sets':       int,     # extra sets from consistency
            'skip_volume':      bool,    # True → do not increase volume
            'dehydration_flag': bool,    # True → user is chronically dehydrated
            'deload_flag':      bool,    # True → full deload recommended
            'hydration_tip':    str,     # user-facing tip (empty when hydration is fine)
            'sleep_tip':        str,     # user-facing tip (empty when sleep is fine)
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
        'hydration_tip': '',
        'sleep_tip': '',
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
    hydration_tip = ''
    sleep_tip = ''
    reasons: List[str] = []

    # ── Sleep-based recovery modifier ────────────────────────────────────────
    # Compare against the user's personal sleep target, not a fixed 8h cutoff.
    sleep_deficit = sleep_target_hours - avg_sleep   # positive = under target

    if sleep_deficit > 3.0:                          # severely under target
        intensity_delta -= 0.15
        deload_flag = True
        sleep_tip = (
            f'You averaged only {avg_sleep:.1f} h sleep — aim for '
            f'{sleep_target_hours:.0f} h. A recovery week is recommended.'
        )
        reasons.append(f'avg sleep {avg_sleep:.1f} h (critical) → full deload')
    elif sleep_deficit > 2.0:                        # meaningfully under target
        intensity_delta -= 0.10
        sleep_tip = (
            f'You averaged {avg_sleep:.1f} h sleep — try to reach '
            f'{sleep_target_hours:.0f} h for better recovery.'
        )
        reasons.append(f'avg sleep {avg_sleep:.1f} h (low) → -10% intensity')
    elif sleep_deficit < -0.5:                       # sleeping above target
        intensity_delta += 0.03
        reasons.append(f'avg sleep {avg_sleep:.1f} h (excellent) → +3% intensity')

    # ── Hydration-based modifier ───────────────────────────────────────────────
    # Ratio-based check against the user's personalised water target.
    # Plan Section 6: > 30% deficit → reduce cardio; 10-30% deficit → tip only.
    if avg_water > 0:
        water_deficit_ratio = (water_target_ml - avg_water) / water_target_ml
    else:
        water_deficit_ratio = 1.0  # treat zero as fully dehydrated

    if water_deficit_ratio > 0.30:                   # drank < 70% of target
        intensity_delta -= 0.10
        dehydration_flag = True
        hydration_tip = (
            f'You drank an average of {avg_water:.0f} ml — '
            f'your target is {water_target_ml} ml/day. '
            'Reduce cardio intensity and add a hydrating snack (e.g. cucumber raita or coconut water).'
        )
        reasons.append(
            f'avg water {avg_water:.0f} ml ({water_deficit_ratio*100:.0f}% deficit, severe) → -10% intensity'
        )
    elif water_deficit_ratio > 0.10:                 # drank < 90% of target
        dehydration_flag = True
        hydration_tip = (
            f'You averaged {avg_water:.0f} ml — try to reach {water_target_ml} ml/day. '
            'Stay hydrated between sets to maintain performance.'
        )
        reasons.append(
            f'avg water {avg_water:.0f} ml ({water_deficit_ratio*100:.0f}% deficit, moderate) → tip sent'
        )

    # ── Workout attendance modifier ───────────────────────────────────────────
    attendance_rate = workout_days / n
    if attendance_rate >= (4 / 7):
        bonus_sets = 1
        reasons.append(f'{workout_days}/{n} workouts completed → +1 bonus set')
    elif attendance_rate < (2 / 7):
        skip_volume = True
        reasons.append(f'only {workout_days}/{n} workouts — skip volume increase this week')

    # ── Clamp intensity delta to reasonable bounds ────────────────────────────
    intensity_delta = max(-0.25, min(0.10, round(intensity_delta, 3)))

    return {
        'intensity_delta': intensity_delta,
        'bonus_sets': bonus_sets,
        'skip_volume': skip_volume,
        'dehydration_flag': dehydration_flag,
        'deload_flag': deload_flag,
        'hydration_tip': hydration_tip,
        'sleep_tip': sleep_tip,
        'reason': '; '.join(reasons) if reasons else 'Baseline — all biometrics normal.',
        'days_logged': n,
        'avg_sleep_hours': round(avg_sleep, 1),
        'avg_water_ml': round(avg_water),
        'water_target_ml': water_target_ml,
        'sleep_target_hours': sleep_target_hours,
        'water_deficit_ratio': round(water_deficit_ratio, 3),
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
