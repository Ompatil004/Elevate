"""
Deterministic Progressive Overload Engine
==========================================
Computes workout progression using:
  progression_delta = base_rate * adherence * recovery * experience_mod

All outputs are clamped by age-based safety caps.
Streak milestones trigger volume or difficulty upgrades.
"""

from typing import Dict, List, Optional, Tuple
from enum import Enum
import math
import os
from datetime import datetime

try:
    import pandas as pd
    _pd_available = True
except ImportError:
    pd = None
    _pd_available = False


# ── CONSTANTS ──

BASE_PROGRESSION_RATES = {
    'Beginner':     0.03,
    'Intermediate': 0.05,
    'Advanced':     0.07,
}

EXPERIENCE_MODIFIERS = {
    'Beginner':     0.70,
    'Intermediate': 1.00,
    'Advanced':     1.15,
}

STREAK_VOLUME_THRESHOLD    = 10
STREAK_DIFFICULTY_THRESHOLD = 30

MAX_SETS_ABSOLUTE      = 6
MAX_REPS_ABSOLUTE      = 20
MAX_INTENSITY_ABSOLUTE = 1.0
MIN_SETS               = 2
MIN_REPS               = 3
MIN_INTENSITY          = 0.30

AGE_CAPS = {
    'senior': {'age_min': 65, 'max_intensity': 0.70, 'max_sets': 3, 'max_exercises': 6, 'rep_range': (10, 12), 'rest_min': 90},
    'mature': {'age_min': 51, 'age_max': 60, 'max_intensity': 0.80, 'exercise_reduce': 2, 'rest_min': 60, 'avoid_high_impact': True},
    'middle': {'age_min': 36, 'age_max': 50, 'max_intensity': 0.85, 'max_exercises': 8, 'rep_min': 8, 'rest_multiplier': 1.2},
    'youth':  {'age_max': 18, 'max_intensity': 0.80, 'max_sets': 4, 'rep_range': (10, 20)},
}


class ProgressionMethod(str, Enum):
    VOLUME_INCREASE    = "volume_increase"
    REP_INCREASE       = "rep_increase"
    EXERCISE_UPGRADE   = "exercise_upgrade"
    INTENSITY_INCREASE = "intensity_increase"
    MAINTAIN           = "maintain"


# ── CORE CALCULATIONS ──

def calculate_adherence_score(
    completion_pct: float,
    streak_days: int,
    days_per_week: int = 4,
) -> float:
    """
    adherence = 0.60 * completion_pct + 0.40 * streak_factor
    streak_factor = min(streak_days / (2 * days_per_week), 1.0)
    """
    completion_pct = max(0.0, min(1.0, completion_pct))
    streak_factor = min(streak_days / max(1, 2 * days_per_week), 1.0)
    return round(0.60 * completion_pct + 0.40 * streak_factor, 4)


def calculate_recovery_factor(
    sleep_score: float,
    hydration_score: float,
    stress_level: float,
    fatigue_level: float = 5.0,
) -> float:
    """
    recovery factor calculated from readiness score as single source of truth
    """
    readiness = calculate_readiness_data(sleep_score, fatigue_level, stress_level)
    return readiness['recovery_score']


def calculate_progression_delta(
    experience: str,
    adherence: float,
    recovery: float,
) -> float:
    """
    delta = base_rate * adherence * recovery * experience_mod
    Clamped to [0.0, 0.10].
    """
    base = BASE_PROGRESSION_RATES.get(experience, 0.05)
    exp_mod = EXPERIENCE_MODIFIERS.get(experience, 1.0)
    raw = base * adherence * recovery * exp_mod
    return round(max(0.0, min(0.10, raw)), 5)


# ── SAFETY OVERRIDES ──

def apply_age_safety_caps(
    age: int,
    sets: int,
    reps_low: int,
    reps_high: int,
    intensity: float,
    current_exercises: int = 6,
    current_rest: int = 60,
) -> Tuple[int, int, int, float]:
    """
    Apply age-based safety caps on all prescription parameters.

    Five bands (per plan Section 3):
      <  18  : youth  — max 4 sets, max intensity 0.80, reps 10-20
      18–35  : baseline — no change
      36–50  : middle  — max exercises 8, rest × 1.2, min 8 reps, max intensity 0.85
      51–60  : mature  — exercises –2, min 60s rest, avoid high-impact, max intensity 0.80
      60+    : senior  — max 6 exercises, max 3 sets, reps 10-12, min 90s rest, max intensity 0.70

    Returns:
        (sets, reps_low, reps_high, intensity)
        Callers can inspect AGE_CAPS directly for avoid_high_impact / exercise limits.
    """
    if age >= AGE_CAPS['senior']['age_min']:          # 65+ (strict senior)
        cap = AGE_CAPS['senior']
        intensity = min(intensity, cap['max_intensity'])
        sets      = min(sets, cap['max_sets'])
        reps_low  = max(reps_low, cap['rep_range'][0])
        reps_high = min(reps_high, cap['rep_range'][1])

    elif age >= AGE_CAPS['mature']['age_min']:         # 51–60
        cap = AGE_CAPS['mature']
        intensity = min(intensity, cap['max_intensity'])
        # rest is advisory — returned via get_age_modifiers, not changed here

    elif age >= AGE_CAPS['middle']['age_min']:         # 36–50
        cap = AGE_CAPS['middle']
        intensity = min(intensity, cap['max_intensity'])
        reps_low  = max(reps_low, cap.get('rep_min', 8))

    elif age < AGE_CAPS['youth'].get('age_max', 18):  # Under 18
        cap = AGE_CAPS['youth']
        intensity = min(intensity, cap['max_intensity'])
        sets      = min(sets, cap['max_sets'])
        reps_low  = max(reps_low, cap['rep_range'][0])
        reps_high = min(reps_high, cap['rep_range'][1])

    sets      = max(MIN_SETS, min(MAX_SETS_ABSOLUTE, sets))
    reps_low  = max(MIN_REPS, reps_low)
    reps_high = min(MAX_REPS_ABSOLUTE, max(reps_high, reps_low + 1))
    intensity = max(MIN_INTENSITY, min(MAX_INTENSITY_ABSOLUTE, intensity))
    return sets, reps_low, reps_high, round(intensity, 3)


def get_age_modifiers(age: int, base_exercises: int = 6, base_rest: int = 60) -> Dict:
    """
    Return a complete age-modifier dict used by the workout engine and meal engine.

    Keys:
        exercises       : adjusted exercise count
        rest_seconds    : adjusted rest time
        avoid_high_impact: bool — True for 51+ users
        level_cap       : 'beginner' | None — forced level for 60+
        meal_note       : user-facing nutrition tip for this age group
        age_group       : label string
    """
    if age >= 60:
        return {
            'exercises': min(base_exercises, AGE_CAPS['senior'].get('max_exercises', 6)),
            'rest_seconds': max(AGE_CAPS['senior']['rest_min'], base_rest),
            'avoid_high_impact': True,
            'level_cap': 'beginner',
            'meal_note': 'Prioritise calcium and protein-rich items. Reduce snack count by 1.',
            'age_group': '60+',
        }
    elif age >= 51:
        return {
            'exercises': max(4, base_exercises - AGE_CAPS['mature']['exercise_reduce']),
            'rest_seconds': max(AGE_CAPS['mature']['rest_min'], base_rest),
            'avoid_high_impact': True,
            'level_cap': None,
            'meal_note': 'Add 1 extra protein item per meal slot.',
            'age_group': '51-60',
        }
    elif age >= 36:
        return {
            'exercises': min(base_exercises, AGE_CAPS['middle']['max_exercises']),
            'rest_seconds': int(base_rest * AGE_CAPS['middle']['rest_multiplier']),
            'avoid_high_impact': False,
            'level_cap': None,
            'meal_note': 'Swap 1 carb item for a fibre-rich sabzi or dal per meal.',
            'age_group': '36-50',
        }
    elif age < 18:
        return {
            'exercises': base_exercises,
            'rest_seconds': base_rest + 15,
            'avoid_high_impact': False,
            'level_cap': None,
            'meal_note': 'No supplements. Add 1 milk or fruit item per meal.',
            'age_group': 'under-18',
        }
    else:  # 18–35 baseline
        return {
            'exercises': base_exercises,
            'rest_seconds': base_rest,
            'avoid_high_impact': False,
            'level_cap': None,
            'meal_note': '',
            'age_group': '18-35',
        }


def build_form_feedback(form_score: float, exercise_name: str = '') -> Dict:
    """
    Build a user-facing form feedback dict for a given exercise form score.

    Per plan Section 7 / pose_tracker logic:
        form_score < 0.50   → poor form: reduce reps to min, reduce weight
        0.50 ≤ score < 0.75 → acceptable: maintain, specific cues
        0.75 ≤ score < 0.90 → good: maintain weight
        score ≥ 0.90        → excellent: increase weight suggestion

    Args:
        form_score:    Float 0.0–1.0 (fraction of correct reps / total reps).
                       Detectors return 0–100 int; pass as float 0.0–1.0 here.
        exercise_name: Optional exercise name for personalised messages.

    Returns:
        {
            'form_score_used':     float,
            'form_band':           str,   # 'poor' | 'acceptable' | 'good' | 'excellent'
            'weight_suggestion':   str,   # 'reduce' | 'maintain' | 'increase'
            'weight_change_pct':   int,   # suggested % change (negative = reduce)
            'form_message':        str,   # user-facing message shown in the UI
            'form_emoji':          str,
        }
    """
    score = float(form_score or 0.75)
    name_hint = f' on {exercise_name}' if exercise_name else ''

    if score < 0.50:
        return {
            'form_score_used': round(score, 2),
            'form_band': 'poor',
            'weight_suggestion': 'reduce',
            'weight_change_pct': -10,
            'form_message': (
                f'Form needs improvement{name_hint} ({int(score * 100)}%). '
                'Reduce weight by 10% and focus on full range of motion before progressing.'
            ),
            'form_emoji': '⚠️',
        }
    elif score < 0.75:
        return {
            'form_score_used': round(score, 2),
            'form_band': 'acceptable',
            'weight_suggestion': 'maintain',
            'weight_change_pct': 0,
            'form_message': (
                f'Acceptable form{name_hint} ({int(score * 100)}%). '
                'Maintain current weight and focus on tempo and control.'
            ),
            'form_emoji': '🟡',
        }
    elif score < 0.90:
        return {
            'form_score_used': round(score, 2),
            'form_band': 'good',
            'weight_suggestion': 'maintain',
            'weight_change_pct': 0,
            'form_message': (
                f'Good form{name_hint} ({int(score * 100)}%). '
                'Keep it up — when you hit the top rep range consistently, consider progressing.'
            ),
            'form_emoji': '🟢',
        }
    else:  # score >= 0.90
        return {
            'form_score_used': round(score, 2),
            'form_band': 'excellent',
            'weight_suggestion': 'increase',
            'weight_change_pct': 5,
            'form_message': (
                f'Excellent form{name_hint} ({int(score * 100)}%)! '
                'You are ready to increase weight by ~5% next session.'
            ),
            'form_emoji': '🌟',
        }



def get_streak_adjustments(
    streak_days: int,
    consistency: float,
    current_sets: int,
    experience: str,
) -> Dict:
    adj = {
        'bonus_sets': 0,
        'exercise_upgrade': False,
        'intensity_bump': 0.0,
        'reason': '',
    }
    if consistency < 0.75:
        return adj

    if streak_days >= STREAK_DIFFICULTY_THRESHOLD:
        adj['exercise_upgrade'] = True
        adj['intensity_bump'] = 0.05
        adj['bonus_sets'] = 1
        adj['reason'] = f'{streak_days}-day streak -> exercise upgrade + volume bump'
    elif streak_days >= STREAK_VOLUME_THRESHOLD:
        adj['bonus_sets'] = 1
        adj['reason'] = f'{streak_days}-day streak -> +1 set volume increase'

    max_bonus = MAX_SETS_ABSOLUTE - current_sets
    adj['bonus_sets'] = max(0, min(adj['bonus_sets'], max_bonus))
    return adj


# ── PROGRESSION METHOD SELECTOR ──

def select_progression_method(
    delta: float,
    streak_days: int,
    current_sets: int,
    current_reps_high: int,
    experience: str,
    recovery: float,
) -> ProgressionMethod:
    if recovery < 0.45:
        return ProgressionMethod.MAINTAIN
    if delta < 0.01:
        return ProgressionMethod.MAINTAIN
    if streak_days >= STREAK_DIFFICULTY_THRESHOLD:
        return ProgressionMethod.EXERCISE_UPGRADE

    exp_max_sets = {'Beginner': 4, 'Intermediate': 5, 'Advanced': 6}.get(experience, 5)
    if current_sets < exp_max_sets:
        return ProgressionMethod.VOLUME_INCREASE
    if current_reps_high < MAX_REPS_ABSOLUTE:
        return ProgressionMethod.REP_INCREASE
    return ProgressionMethod.INTENSITY_INCREASE


# ── EXERCISE VARIATION LADDER ──

def get_exercise_variation_suggestion(
    exercise_name: str,
    form_score: float,
    exercises_df=None,
) -> Dict:
    """
    Based on form score, suggest an easier or harder exercise variation.
    Uses Progression_Next and Alternative_Swap columns from exercises_home_v1.csv.

    Args:
        exercise_name: Current exercise name (e.g. 'Push-Up')
        form_score: 0.0 to 1.0 from pose tracker (correct_reps / total_reps)
        exercises_df: DataFrame of exercises with Progression_Next, Alternative_Swap columns

    Returns:
        {
            'action': 'progress' | 'regress' | 'maintain',
            'suggested_exercise': str,
            'reason': str,
            'current_difficulty': str,
            'next_difficulty': str,
        }
    """
    default = {
        'action': 'maintain',
        'suggested_exercise': exercise_name,
        'reason': f'Form score: {int(form_score * 100)}%. Keep practising this variation.',
        'current_difficulty': '',
        'next_difficulty': 'same',
    }

    if exercises_df is None or not _pd_available:
        # Try loading the default dataset
        try:
            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            csv_path = os.path.join(base_dir, 'data', 'exercises_processed.csv')
            if os.path.exists(csv_path):
                exercises_df = pd.read_csv(csv_path)
            else:
                return default
        except Exception:
            return default

    # Find exercise in dataset (case-insensitive partial match)
    name_lower = exercise_name.lower().strip()
    mask = exercises_df['Name'].str.lower().str.strip() == name_lower
    if not mask.any():
        # Try partial match
        mask = exercises_df['Name'].str.lower().str.contains(name_lower, na=False)
    if not mask.any():
        return default

    row = exercises_df[mask].iloc[0]
    current_difficulty = str(row.get('Difficulty', ''))

    if form_score >= 0.85:
        # Excellent form → progress to harder variation
        next_ex = str(row.get('Progression_Next', '')).strip()
        if next_ex and next_ex.lower() not in ('', 'nan', 'none', exercise_name.lower()):
            return {
                'action': 'progress',
                'suggested_exercise': next_ex,
                'reason': f'Excellent form ({int(form_score * 100)}%)! Try the harder version next session.',
                'current_difficulty': current_difficulty,
                'next_difficulty': 'harder',
            }

    elif form_score < 0.50:
        # Poor form → regress to easier variation
        alt_ex = str(row.get('Alternative_Swap', '')).strip()
        if alt_ex and alt_ex.lower() not in ('', 'nan', 'none', exercise_name.lower()):
            return {
                'action': 'regress',
                'suggested_exercise': alt_ex,
                'reason': f'Form needs work ({int(form_score * 100)}%). Try the easier version to build correct movement.',
                'current_difficulty': current_difficulty,
                'next_difficulty': 'easier',
            }

    return {
        'action': 'maintain',
        'suggested_exercise': exercise_name,
        'reason': f'Good form ({int(form_score * 100)}%). Keep practising this variation.',
        'current_difficulty': current_difficulty,
        'next_difficulty': 'same',
    }


# ── STAGE/READINESS HELPERS ──

def is_bodyweight_exercise(name: str, exercises_df=None) -> bool:
    name_clean = name.strip()
    import app.utils.movement_mapper as mm
    
    # 1. Check EXERCISE_METADATA registry first
    meta = mm.EXERCISE_METADATA.get(name_clean)
    if not meta:
        # Check case-insensitive
        for k, v in mm.EXERCISE_METADATA.items():
            if k.lower() == name_clean.lower():
                meta = v
                break
    if meta:
        equipment = meta.get("equipment", [])
        if not equipment or any(e in ("body weight", "bodyweight", "none", "assisted") for e in equipment):
            return True
        return False

    if exercises_df is not None:
        name_lower = name.lower().strip()
        mask = exercises_df['Name'].str.lower().str.strip() == name_lower
        if not mask.any():
            mask = exercises_df['Name'].str.lower().str.contains(name_lower, na=False)
        if mask.any():
            row = exercises_df[mask].iloc[0]
            equip = str(row.get('Equipment', '')).lower()
            return 'body weight' in equip or 'bodyweight' in equip or 'none' in equip or 'assisted' in equip
            
    name_lower = name.lower()
    return 'push-up' in name_lower or 'squat' in name_lower or 'dip' in name_lower or 'pull-up' in name_lower or 'chin-up' in name_lower or 'crunch' in name_lower or 'plank' in name_lower


def calculate_readiness_data(sleep_score: float, fatigue_score: float, stress_level: float) -> dict:
    sleep_norm = max(0.0, min(1.0, float(sleep_score or 7.0) / 10.0))
    fatigue_norm = max(0.0, min(1.0, (10.0 - float(fatigue_score or 5.0)) / 10.0))
    stress_norm = max(0.0, min(1.0, (10.0 - float(stress_level or 5.0)) / 10.0))
    
    readiness_score = round((sleep_norm * 0.4 + fatigue_norm * 0.35 + stress_norm * 0.25) * 100)
    readiness_score = max(0, min(100, int(readiness_score)))
    
    if readiness_score >= 80:
        level = "optimal"
    elif readiness_score >= 60:
        level = "good"
    else:
        level = "fatigued"
        
    return {
        "readiness_score": readiness_score,
        "readiness_level": level,
        "recovery_score": readiness_score / 100.0
    }


def calculate_consistent_weeks(workout_history: List[Dict]) -> int:
    if not workout_history:
        return 0
    now = datetime.now()
    active_weeks = set()
    for session in workout_history:
        date_str = session.get('date') or session.get('created_at')
        try:
            if date_str:
                session_date = datetime.fromisoformat(date_str.replace("Z", "+00:00")).replace(tzinfo=None)
            else:
                continue
        except Exception:
            continue
        days_ago = (now - session_date).days
        if days_ago < 0:
            continue
        week_idx = days_ago // 7
        active_weeks.add(week_idx)
        
    consecutive_from_0 = 0
    while consecutive_from_0 in active_weeks:
        consecutive_from_0 += 1
        
    consecutive_from_1 = 0
    while (consecutive_from_1 + 1) in active_weeks:
        consecutive_from_1 += 1
        
    return max(consecutive_from_0, consecutive_from_1)


# ── MAIN ENGINE ──

class ProgressionEngine:
    """Stateless, deterministic progression engine."""

    def evaluate_deload(self, workout_history: List[Dict], readiness_score: int, fatigue_level: float, avg_form_score: float) -> bool:
        consistent_weeks = calculate_consistent_weeks(workout_history)
        recovery_factor = readiness_score / 100.0
        
        deload_score = 0
        if consistent_weeks >= 4:
            deload_score += 1
        if recovery_factor < 0.45:
            deload_score += 1
        if fatigue_level >= 8:
            deload_score += 1
        if avg_form_score < 0.75:
            deload_score += 1
            
        should_deload = deload_score >= 2
        
        # High fatigue emergency override
        if recovery_factor < 0.35 and fatigue_level >= 9:
            should_deload = True
            
        return should_deload

    def detect_plateaus(self, workout_history: List[Dict], exercises_df=None) -> Dict:
        from app.utils.movement_mapper import get_movement_metadata
        
        history_by_pattern = {}
        sorted_history = []
        for session in (workout_history or []):
            date_str = session.get('date') or session.get('created_at')
            try:
                if date_str:
                    session_date = datetime.fromisoformat(date_str.replace("Z", "+00:00")).replace(tzinfo=None)
                else:
                    continue
            except Exception:
                continue
            sorted_history.append((session_date, session))
        sorted_history.sort(key=lambda x: x[0])
        
        for s_date, session in sorted_history:
            date_key = s_date.date()
            for ex in session.get('exercises', []):
                name = ex.get('name', '')
                if not name:
                    continue
                target_muscle = ex.get('target_muscle', '')
                
                meta = get_movement_metadata(name, target_muscle)
                pattern = meta['pattern']
                if pattern == 'unknown':
                    continue
                    
                reps = float(ex.get('reps', 10) or 10)
                weight = float(ex.get('weight', 0.0) or 0.0)
                is_bw = is_bodyweight_exercise(name, exercises_df)
                
                if is_bw:
                    value = reps
                else:
                    value = weight * (1.0 + reps / 30.0)
                    
                if pattern not in history_by_pattern:
                    history_by_pattern[pattern] = []
                    
                existing_entry = next((item for item in history_by_pattern[pattern] if item[0] == date_key), None)
                if existing_entry:
                    idx = history_by_pattern[pattern].index(existing_entry)
                    history_by_pattern[pattern][idx] = (date_key, max(existing_entry[1], value))
                else:
                    history_by_pattern[pattern].append((date_key, value))
                    
        plateaued_movements = {}
        for pattern, entries in history_by_pattern.items():
            if len(entries) < 3:
                continue
            last_3 = entries[-3:]
            v1, v2, v3 = last_3[0][1], last_3[1][1], last_3[2][1]
            
            if v2 <= v1 and v3 <= v2:
                plateaued_movements[pattern] = {
                    "severity": "severe" if v3 < v1 else "moderate",
                    "sessions_stalled": 3
                }
                
        return plateaued_movements

    def get_progression_state(self, user_profile: Dict, workout_history: List[Dict], exercises_df=None) -> Dict:
        sleep = float(user_profile.get('sleep_score', 7.0) or 7.0)
        fatigue = float(user_profile.get('fatigue_level', 5.0) or user_profile.get('fatigue', 5.0) or 5.0)
        stress = float(user_profile.get('stress_level', 5.0) or 5.0)
        
        readiness = calculate_readiness_data(sleep, fatigue, stress)
        
        now = datetime.now()
        last_week_scores = []
        for session in (workout_history or []):
            date_str = session.get('date') or session.get('created_at')
            try:
                if date_str:
                    session_date = datetime.fromisoformat(date_str.replace("Z", "+00:00")).replace(tzinfo=None)
                else:
                    continue
            except Exception:
                continue
            if (now - session_date).days <= 7:
                for ex in session.get('exercises', []):
                    correct = ex.get('correct_reps', 0)
                    total = ex.get('total_reps', 0)
                    if total > 0:
                        last_week_scores.append(correct / total)
                    elif 'form_score' in ex:
                        last_week_scores.append(ex['form_score'])
                    elif 'form_score' in session:
                        last_week_scores.append(session['form_score'])
                        
        avg_form_score = sum(last_week_scores) / len(last_week_scores) if last_week_scores else 1.0
        
        should_deload = self.evaluate_deload(
            workout_history=workout_history or [],
            readiness_score=readiness['readiness_score'],
            fatigue_level=fatigue,
            avg_form_score=avg_form_score
        )
        
        plateaued_movements = self.detect_plateaus(workout_history or [], exercises_df)
        
        # Authoritative phase mapping: deload takes precedence
        phase = "deload" if should_deload else "progression"
        is_deload = (phase == "deload")
        
        return {
            "phase": phase,
            "readiness_score": readiness["readiness_score"],
            "readiness_level": readiness["readiness_level"],
            "is_deload": is_deload,
            "plateaued_movements": plateaued_movements,
            "fatigue_level": fatigue,
            "recovery_score": readiness["recovery_score"]
        }

    def generate_structured_coaching_feedback(self, state: Dict, user_profile: Dict) -> Dict:
        phase = state.get("phase", "progression")
        readiness_score = state.get("readiness_score", 70)
        readiness_level = state.get("readiness_level", "good")
        plateaued_movements = state.get("plateaued_movements", {})
        
        focus = "recovery" if phase == "deload" else "progression"
        
        if phase == "deload":
            week_summary = "Deload week active: focus on recovery, joint restoration, and muscle rebuilding."
        else:
            week_summary = f"Progression week: readiness is {readiness_level} ({readiness_score}/100). Focus on progressive overload."
            
        if readiness_level == "optimal":
            recovery_tip = "Readiness is optimal! Great time to attempt personal records or hit high efforts."
        elif readiness_level == "good":
            recovery_tip = "Readiness is solid. Aim for consistency and solid execution."
        else:
            recovery_tip = "Systemic recovery is low. Make sure to sleep 8+ hours and focus on hydration."
            
        if phase == "deload":
            progression_tip = "Eccentric control is key this week. Focus on quality repetitions rather than heavy loads."
        else:
            progression_tip = "Strive for progressive volume or intensity. Add a rep or increase load if form is solid."
            
        if plateaued_movements:
            stalled_str = ", ".join(m.replace('_', ' ') for m in plateaued_movements.keys())
            plateau_tip = f"We noticed stalling on: {stalled_str}. To break this, we scaled down volume/intensity or triggered variations."
        else:
            plateau_tip = "No stalls detected. Muscle adaptation is proceeding normally."
            
        return {
            "week_summary": week_summary,
            "focus": focus,
            "recovery_tip": recovery_tip,
            "progression_tip": progression_tip,
            "plateau_tip": plateau_tip
        }

    def parse_history(self, workout_history: List[Dict]) -> Dict:
        """
        Extracts historical usage from the user's workout history.
        Returns a memory object tracking recent exercises, movement patterns, and current fatigue (weekly volume).
        """
        memory = {
            'recent_exercises': set(),       # Avoid repeating same exact exercise too soon
            'recent_movements': set(),       # Ensure variety of movements
            'weekly_muscle_volume': {},      # Sets per muscle in the last 7 days (Fatigue Management)
            'last_trained_muscles': set(),   # Muscles trained in the last 48 hours (Recovery Rules)
        }
        
        if not workout_history:
            return memory
            
        now = datetime.now()
        
        for session in workout_history:
            # Parse date, fallback to old if not present
            date_str = session.get('date') or session.get('created_at')
            try:
                if date_str:
                    # simplistic parse
                    session_date = datetime.fromisoformat(date_str.replace("Z", "+00:00")).replace(tzinfo=None)
                else:
                    session_date = now
            except Exception:
                session_date = now
                
            days_ago = (now - session_date).days
            
            for ex in session.get('exercises', []):
                name = str(ex.get('name', '')).lower().strip()
                muscle = str(ex.get('target_muscle', '')).lower().strip()
                sets = int(ex.get('sets', 3))
                
                if not name:
                    continue
                    
                if days_ago <= 30:
                    memory['recent_exercises'].add(name)
                    
                if days_ago <= 14:
                    from app.utils.movement_mapper import get_movement_metadata
                    meta = get_movement_metadata(name, muscle)
                    memory['recent_movements'].add(meta['pattern'])
                    
                if days_ago <= 7:
                    if muscle not in memory['weekly_muscle_volume']:
                        memory['weekly_muscle_volume'][muscle] = 0
                    memory['weekly_muscle_volume'][muscle] += sets
                    
                if days_ago <= 2:
                    memory['last_trained_muscles'].add(muscle)
                    
        return memory

    def compute_progression(
        self,
        user_profile: Dict,
        current_params: Dict,
        workout_stats: Optional[Dict] = None,
        workout_history: Optional[List[Dict]] = None,
        exercises_df = None
    ) -> Dict:
        age          = int(user_profile.get('age', 25))
        experience   = str(user_profile.get('experience', 'Beginner'))
        consistency  = float(user_profile.get('consistency', 0.7))
        streak       = int(user_profile.get('streak', 0))
        days_pw      = int(user_profile.get('days_per_week', 4))
        sleep        = float(user_profile.get('sleep_score', 7.0))
        hydration    = float(user_profile.get('hydration_score', 7.0))
        stress       = float(user_profile.get('stress_level', 5.0))

        cur_sets      = int(current_params.get('sets', 3))
        cur_reps_low  = int(current_params.get('reps_low', 8))
        cur_reps_high = int(current_params.get('reps_high', 12))
        cur_intensity = float(current_params.get('intensity', 0.70))
        cur_rest      = int(current_params.get('rest_seconds', 90))

        stats = workout_stats or {}
        completion_pct = float(stats.get('completion_pct', consistency))
        fatigue        = float(stats.get('fatigue_level', 5.0))
        form_score     = float(stats.get('form_score', 0.75))

        # Calculate progression state
        prog_state = self.get_progression_state(user_profile, workout_history or [], exercises_df)
        is_deload = prog_state.get('is_deload', False) or stats.get('force_deload', False)
        readiness_score = prog_state.get('readiness_score', 70)
        plateaued_movements = prog_state.get('plateaued_movements', {})

        # Form score gates progression: if form is below 50%,
        # force MAINTAIN regardless of other factors
        if form_score < 0.50:
            sets, reps_low, reps_high, intensity = apply_age_safety_caps(
                age, cur_sets, cur_reps_low, cur_reps_high, cur_intensity
            )
            if is_deload:
                sets = max(2, sets - 1)
                intensity = max(0.3, intensity * 0.8)
            return {
                'sets': sets,
                'reps': f'{reps_low}-{reps_high}',
                'reps_low': reps_low,
                'reps_high': reps_high,
                'intensity': intensity,
                'rest_seconds': cur_rest,
                'exercise_upgrade_suggested': False,
                'progression_method': 'maintain_poor_form',
                'progression_delta': 0.0,
                'metadata': {
                    'form_score': form_score,
                    'reason': f'Form below 50% ({int(form_score * 100)}%) — maintaining current level until form improves.',
                    'adherence_score': 0.0,
                    'recovery_factor': 0.0,
                    'streak_adjustment': {},
                    'age_caps_applied': age >= 65 or age < 18,
                    'recovery_gating_applied': False,
                    'form_gating_applied': True,
                    'progression_state': prog_state
                },
            }

        # Check for plateau on the movement pattern of this exercise
        exercise_name = current_params.get('exercise_name', '')
        import app.utils.movement_mapper as mm
        meta = mm.get_movement_metadata(exercise_name)
        ex_pattern = meta.get('pattern', 'unknown')
        is_stalled = ex_pattern in plateaued_movements
        
        adherence = calculate_adherence_score(completion_pct, streak, days_pw)
        recovery  = calculate_readiness_data(sleep, fatigue, stress)['recovery_score']
        delta     = calculate_progression_delta(experience, adherence, recovery)

        if is_stalled:
            method = ProgressionMethod.EXERCISE_UPGRADE
            reason_str = f"Plateau detected on {ex_pattern.replace('_', ' ')}: triggering exercise variation swap to break the plateau."
        elif is_deload:
            method = ProgressionMethod.MAINTAIN
            reason_str = "Deload active: training intensity and volume reduced for CNS recovery."
        else:
            method    = select_progression_method(
                delta, streak, cur_sets, cur_reps_high, experience, recovery
            )
            # Apply biometrics-based volume gating: skip volume/rep increases if attendance is low
            if stats.get('skip_volume_increase') and method in (ProgressionMethod.VOLUME_INCREASE, ProgressionMethod.REP_INCREASE):
                method = ProgressionMethod.MAINTAIN
                reason_str = "Attendance low: volume increase skipped this week."
            else:
                reason_str = "Progressive overload applied based on adherence and readiness."

        new_sets      = cur_sets
        new_reps_low  = cur_reps_low
        new_reps_high = cur_reps_high
        new_intensity = cur_intensity
        new_rest      = cur_rest
        exercise_upgrade = False

        if method == ProgressionMethod.VOLUME_INCREASE:
            new_sets = cur_sets + 1
        elif method == ProgressionMethod.REP_INCREASE:
            new_reps_low  = cur_reps_low + 1
            new_reps_high = cur_reps_high + 2
        elif method == ProgressionMethod.INTENSITY_INCREASE:
            new_intensity = cur_intensity + delta
        elif method == ProgressionMethod.EXERCISE_UPGRADE:
            exercise_upgrade = True
            new_intensity = cur_intensity + 0.05

        if not is_deload and not is_stalled:
            streak_adj = get_streak_adjustments(streak, consistency, new_sets, experience)
            new_sets += streak_adj['bonus_sets']
            new_intensity += streak_adj['intensity_bump']
            if streak_adj['exercise_upgrade']:
                exercise_upgrade = True
        else:
            streak_adj = {}

        if recovery < 0.40:
            new_sets      = max(MIN_SETS, new_sets - 1)
            new_intensity = max(MIN_INTENSITY, new_intensity - 0.05)
            new_rest      = min(cur_rest + 30, 240)

        # Autoregulation: Optimal readiness (+5%), Fatigued (-10%)
        if readiness_score >= 85:
            new_intensity = min(1.0, new_intensity + 0.05)
        elif readiness_score < 50:
            new_intensity = max(0.3, new_intensity - 0.10)

        if is_deload:
            new_sets = max(2, new_sets - 1)
            new_intensity = max(0.3, new_intensity * 0.8)

        # Apply weekly sleep/hydration-based modifiers
        new_sets += int(stats.get('adaptive_bonus_sets', 0))
        new_intensity += float(stats.get('intensity_delta', 0.0))

        new_sets, new_reps_low, new_reps_high, new_intensity = apply_age_safety_caps(
            age, new_sets, new_reps_low, new_reps_high, new_intensity
        )

        return {
            'sets': new_sets,
            'reps': f'{new_reps_low}-{new_reps_high}',
            'reps_low': new_reps_low,
            'reps_high': new_reps_high,
            'intensity': round(new_intensity, 2),
            'rest_seconds': new_rest,
            'exercise_upgrade_suggested': exercise_upgrade,
            'progression_method': "plateau_breaker" if is_stalled else method.value,
            'progression_delta': delta,
            'metadata': {
                'adherence_score': adherence,
                'recovery_factor': recovery,
                'streak_adjustment': streak_adj,
                'age_caps_applied': age >= 65 or age < 18,
                'recovery_gating_applied': recovery < 0.40,
                'progression_state': prog_state,
                'reason': reason_str
            },
        }


# ── SINGLETON ──

_engine: Optional[ProgressionEngine] = None

def get_progression_engine() -> ProgressionEngine:
    global _engine
    if _engine is None:
        _engine = ProgressionEngine()
    return _engine
