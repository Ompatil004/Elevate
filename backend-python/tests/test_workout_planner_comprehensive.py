import pytest
import datetime
import random
import hashlib
import json
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock, MagicMock

from app.workout_engine import WorkoutEngine
import server


# --- Freeze Datetime Mock ---
class FrozenDatetime(datetime.datetime):
    @classmethod
    def utcnow(cls):
        return datetime.datetime(2026, 6, 22, 12, 0, 0)
    
    @classmethod
    def now(cls, tz=None):
        if tz is not None:
            return datetime.datetime(2026, 6, 22, 12, 0, 0, tzinfo=tz)
        return datetime.datetime(2026, 6, 22, 12, 0, 0)


@pytest.fixture(autouse=True)
def freeze_determinism(monkeypatch):
    # Freeze time in workout engine to ensure reproducible week/day matching
    monkeypatch.setattr("app.workout_engine.datetime", FrozenDatetime)
    monkeypatch.setattr("app.workout_engine._utcnow", lambda: datetime.datetime(2026, 6, 22, 12, 0, 0))
    # Mock Gemini to be unavailable so we don't trigger real network calls / quota blocks
    monkeypatch.setattr("app.workout_engine.is_gemini_available", lambda: False)
    # Mock background WGER loader to prevent starting slow threads that make network calls
    monkeypatch.setattr("app.workout_engine.WorkoutEngine._lazy_load_wger", lambda self: None)
    # Mock synchronous WGER media index load to prevent slow API requests
    monkeypatch.setattr("app.workout_engine.WorkoutEngine._initialize_wger_media_index", lambda self: None)
    # Mock network reachability check to prevent slow network request timeouts during tests
    monkeypatch.setattr("app.workout_engine.WorkoutEngine._check_url_reachable", lambda self, url, accept_any_response=False: True)
    # Force workout_engine_v2 to False for legacy comprehensive assertions
    import copy
    from app.workout_rules import load_workout_rules
    default_rules = copy.deepcopy(load_workout_rules())
    if "feature_flags" in default_rules:
        default_rules["feature_flags"]["workout_engine_v2"] = False
    monkeypatch.setattr("app.workout_rules.load_workout_rules", lambda: default_rules)
    # Seed the system random generator
    random.seed(42)


# ==============================================================================
# 1. Determinism and Stability Test
# ==============================================================================
def test_determinism_under_fixed_profile():
    """Verify that calling generate_weekly_plan twice returns identical plans."""
    engine = WorkoutEngine()
    profile = {
        'user_id': 'det_user_1',
        'goal': 'Muscle Gain',
        'experience': 'Intermediate',
        'equipment': ['Dumbbell'],
        'body_issues': [],
        'days_per_week': 4,
        'age': 30,
        'streak': 10,
        'consistency': 0.8,
        'gender': 'Male',
        'week_offset': 202625
    }

    plan_a = engine.generate_weekly_plan(profile)
    plan_b = engine.generate_weekly_plan(profile)

    # Convert to JSON to verify deep equality
    json_a = json.dumps(plan_a, sort_keys=True)
    json_b = json.dumps(plan_b, sort_keys=True)

    assert json_a == json_b, "Plan generation is non-deterministic under identical profiles"


# ==============================================================================
# 2. Age-Based Safety Clamps
# ==============================================================================
def test_senior_age_safety_filters():
    """Verify that seniors (>65 years) do not receive high-impact exercises."""
    engine = WorkoutEngine()
    profile = {
        'user_id': 'senior_user',
        'goal': 'Muscle Gain',
        'experience': 'Beginner',
        'equipment': ['Dumbbell'],
        'body_issues': [],
        'days_per_week': 3,
        'age': 68,
        'streak': 0,
        'consistency': 0.7,
        'gender': 'Male',
        'week_offset': 202625
    }

    plan = engine.generate_weekly_plan(profile)
    high_impact_keywords = ['jump', 'plyo', 'explosive', 'sprint']

    workout_days_found = 0
    for day in plan:
        if day['type'] == 'workout':
            workout_days_found += 1
            for ex in day['exercises']:
                name_lc = ex['name'].lower()
                for keyword in high_impact_keywords:
                    assert keyword not in name_lc, f"Senior trainee suggested high-impact exercise '{ex['name']}' containing '{keyword}'"

    assert workout_days_found > 0, "No workout days were generated"


# ==============================================================================
# 3. Frequency Gates
# ==============================================================================
def test_frequency_gating_beginner():
    """Verify that beginner training days are capped to 3 unless streak/consistency triggers unlocked."""
    engine = WorkoutEngine()
    
    # 1. Base beginner (should be capped at 3 days even though requesting 4)
    profile_base = {
        'user_id': 'beg_base',
        'goal': 'Muscle Gain',
        'experience': 'Beginner',
        'equipment': ['Dumbbell'],
        'body_issues': [],
        'days_per_week': 4,
        'age': 25,
        'streak': 0,
        'consistency': 0.7,
        'gender': 'Male',
        'week_offset': 202625
    }
    plan_base = engine.generate_weekly_plan(profile_base)
    workout_days_base = sum(1 for d in plan_base if d['type'] == 'workout')
    assert workout_days_base == 3, f"Expected 3 workout days for base beginner, got {workout_days_base}"

    # 2. Progression beginner (streak >= 21 and consistency >= 0.85 unlocks 4 days)
    profile_prog = {
        'user_id': 'beg_prog',
        'goal': 'Muscle Gain',
        'experience': 'Beginner',
        'equipment': ['Dumbbell'],
        'body_issues': [],
        'days_per_week': 4,
        'age': 25,
        'streak': 25,
        'consistency': 0.9,
        'gender': 'Male',
        'week_offset': 202625
    }
    plan_prog = engine.generate_weekly_plan(profile_prog)
    workout_days_prog = sum(1 for d in plan_prog if d['type'] == 'workout')
    assert workout_days_prog == 4, f"Expected 4 workout days for progressive beginner, got {workout_days_prog}"


def test_frequency_gating_intermediate():
    """Verify that intermediate training days are capped to 4 unless unlocked to 5."""
    engine = WorkoutEngine()
    
    # 1. Base intermediate (capped at 4 days even though requesting 5)
    profile_base = {
        'user_id': 'int_base',
        'goal': 'Muscle Gain',
        'experience': 'Intermediate',
        'equipment': ['Dumbbell'],
        'body_issues': [],
        'days_per_week': 5,
        'age': 25,
        'streak': 0,
        'consistency': 0.7,
        'gender': 'Male',
        'week_offset': 202625
    }
    plan_base = engine.generate_weekly_plan(profile_base)
    workout_days_base = sum(1 for d in plan_base if d['type'] == 'workout')
    assert workout_days_base == 4, f"Expected 4 workout days for base intermediate, got {workout_days_base}"

    # 2. Progression intermediate (streak >= 42 and consistency >= 0.90 unlocks 5 days)
    profile_prog = {
        'user_id': 'int_prog',
        'goal': 'Muscle Gain',
        'experience': 'Intermediate',
        'equipment': ['Dumbbell'],
        'body_issues': [],
        'days_per_week': 5,
        'age': 25,
        'streak': 50,
        'consistency': 0.95,
        'gender': 'Male',
        'week_offset': 202625
    }
    plan_prog = engine.generate_weekly_plan(profile_prog)
    workout_days_prog = sum(1 for d in plan_prog if d['type'] == 'workout')
    assert workout_days_prog == 5, f"Expected 5 workout days for progressive intermediate, got {workout_days_prog}"


def test_frequency_gating_advanced():
    """Verify that advanced training days are capped to 5 unless unlocked to 6."""
    engine = WorkoutEngine()
    
    # 1. Base advanced (capped at 5 days even though requesting 6)
    profile_base = {
        'user_id': 'adv_base',
        'goal': 'Muscle Gain',
        'experience': 'Advanced',
        'equipment': ['Dumbbell'],
        'body_issues': [],
        'days_per_week': 6,
        'age': 25,
        'streak': 0,
        'consistency': 0.7,
        'gender': 'Male',
        'week_offset': 202625
    }
    plan_base = engine.generate_weekly_plan(profile_base)
    workout_days_base = sum(1 for d in plan_base if d['type'] == 'workout')
    assert workout_days_base == 5, f"Expected 5 workout days for base advanced, got {workout_days_base}"

    # 2. Progression advanced (streak >= 10 and consistency >= 0.80 unlocks 6 days)
    profile_prog = {
        'user_id': 'adv_prog',
        'goal': 'Muscle Gain',
        'experience': 'Advanced',
        'equipment': ['Dumbbell'],
        'body_issues': [],
        'days_per_week': 6,
        'age': 25,
        'streak': 12,
        'consistency': 0.85,
        'gender': 'Male',
        'week_offset': 202625
    }
    plan_prog = engine.generate_weekly_plan(profile_prog)
    workout_days_prog = sum(1 for d in plan_prog if d['type'] == 'workout')
    assert workout_days_prog == 6, f"Expected 6 workout days for progressive advanced, got {workout_days_prog}"


# ==============================================================================
# 4. Gender-Based Parameter Adjustments
# ==============================================================================
def test_gender_parameter_adjustments_female():
    """Verify female parameter shifts: hypertrophy reps shift (+2), shorter rest (-15%), beginner sets reduction."""
    engine = WorkoutEngine()

    # 1. Hypertrophy Rep range shift & rest reduction
    profile = {
        'user_id': 'female_user',
        'goal': 'Muscle Gain', # Hypertrophy
        'experience': 'Intermediate',
        'equipment': ['Dumbbell'],
        'body_issues': [],
        'days_per_week': 4,
        'age': 30,
        'streak': 0,
        'consistency': 0.7,
        'gender': 'Female',
        'week_offset': 202625
    }

    plan = engine.generate_weekly_plan(profile)
    for day in plan:
        if day['type'] == 'workout':
            for ex in day['exercises']:
                if not ex.get('is_warmup'):
                    # Intermediate Female hypertrophic reps should be shifted (+2) from 8-12 to 10-14
                    assert ex['reps'] == '10-14', f"Expected reps to shift to 10-14 for female hypertrophy, got {ex['reps']}"
                    # Base hypertrophy rest is 60-90s. 60s * 0.85 = 51s rest string "51 seconds".
                    assert ex['rest'] == '51 seconds', f"Expected rest to shift to 51 seconds, got {ex['rest']}"
                    
    # 2. Beginner sets reduction
    profile_beg = {
        **profile,
        'experience': 'Beginner',
        'user_id': 'female_beg'
    }
    plan_beg = engine.generate_weekly_plan(profile_beg)
    for day in plan_beg:
        if day['type'] == 'workout':
            for ex in day['exercises']:
                if not ex.get('is_warmup'):
                    # Standard beginner is 3 sets, female beginner gets reduced to 2 sets
                    assert ex['sets'] == 2, f"Expected sets capped to 2 for female beginner, got {ex['sets']}"


# ==============================================================================
# 5. Priority Conflict Resolution
# ==============================================================================
def test_injury_override_trumps_hypertrophy_goal():
    """Verify that injury exclusion filters trump goal-based muscle selections (e.g. knee injury excludes leg day loading)."""
    engine = WorkoutEngine()
    profile = {
        'user_id': 'knee_injury_user',
        'goal': 'Muscle Gain',
        'experience': 'Intermediate',
        'equipment': ['Dumbbell'],
        'body_issues': ['knee'], # Knee injury
        'days_per_week': 4,
        'age': 25,
        'streak': 10,
        'consistency': 0.8,
        'gender': 'Male',
        'week_offset': 202625
    }

    # Find knee-restricted exercises in database
    knee_restricted = engine.exercises_df[
        engine.exercises_df['Avoid_If'].str.contains('knee', case=False, na=False)
    ]
    restricted_names = set(knee_restricted['Name'].tolist())

    plan = engine.generate_weekly_plan(profile)
    for day in plan:
        if day['type'] == 'workout':
            for ex in day['exercises']:
                assert ex['name'] not in restricted_names, f"Knee injury trainee recommended restricted exercise '{ex['name']}'"


def test_safety_clamp_overrides_frequency_boost():
    """Verify that beginner safety clamps override streak-based frequency overrides."""
    engine = WorkoutEngine()
    profile = {
        'user_id': 'beg_ultra_streak',
        'goal': 'Muscle Gain',
        'experience': 'Beginner',
        'equipment': ['Dumbbell'],
        'body_issues': [],
        'days_per_week': 6, # Requesting 6 days
        'age': 25,
        'streak': 100, # Very high streak
        'consistency': 0.99, # Perfect consistency
        'gender': 'Male',
        'week_offset': 202625
    }

    plan = engine.generate_weekly_plan(profile)
    workout_days = sum(1 for d in plan if d['type'] == 'workout')
    # Even with high streak/consistency, a beginner is clamped at max 4 workout days
    assert workout_days == 4, f"Beginner safety frequency clamp was overridden: got {workout_days} days instead of 4"


# ==============================================================================
# 6. Weekly Schedule Structure & deduplication
# ==============================================================================
def test_weekly_schedule_structure_and_no_consecutive_exercises():
    """Verify restReason generation, warmup separation, and that exercises do not repeat across the week."""
    engine = WorkoutEngine()
    profile = {
        'user_id': 'struct_user',
        'goal': 'Muscle Gain',
        'experience': 'Intermediate',
        'equipment': ['Dumbbell'],
        'body_issues': [],
        'days_per_week': 4,
        'age': 30,
        'streak': 10,
        'consistency': 0.8,
        'gender': 'Male',
        'week_offset': 202625
    }

    plan = engine.generate_weekly_plan(profile)
    assert len(plan) == 7, "Weekly plan must contain exactly 7 days"

    seen_exercises = set()
    for idx, day in enumerate(plan):
        # 1. Structure checks
        assert 'day' in day
        assert 'type' in day
        assert 'focus' in day
        assert 'exercises' in day

        if day['type'] == 'rest':
            # Check restReason is present and populated
            assert 'restReason' in day
            assert len(day['restReason']) > 0, f"Rest day {day['day']} has empty restReason"
        else:
            # Check warmups are separated
            assert 'warmup' in day
            assert len(day['warmup']) > 0, f"Workout day {day['day']} has no warmups"
            
            # Check exercises list has only main exercises (no warmup drill in 'exercises')
            for ex in day['exercises']:
                assert not ex.get('is_warmup'), f"Warmup exercise '{ex['name']}' found in main exercises list"
                
                # Check cross-day exercise deduplication
                assert ex['name'] not in seen_exercises, f"Exercise '{ex['name']}' repeated in the same week"
                seen_exercises.add(ex['name'])


# ==============================================================================
# 7. Regression Lock Snapshot Test
# ==============================================================================
def test_regression_lock_snapshot():
    """Lock in plan generation results via stable cryptographic hash check of output names."""
    engine = WorkoutEngine()
    profile = {
        'user_id': 'snapshot_locked_user',
        'goal': 'Muscle Gain',
        'experience': 'Intermediate',
        'equipment': ['Dumbbell'],
        'body_issues': [],
        'days_per_week': 4,
        'age': 30,
        'streak': 10,
        'consistency': 0.8,
        'gender': 'Male',
        'week_offset': 202625
    }

    plan = engine.generate_weekly_plan(profile)
    
    # Extract only day names and sorted lists of exercise names
    serialized = []
    for day in plan:
        day_info = {
            'day': day['day'],
            'type': day['type'],
            'focus': day['focus'],
            'exercises': sorted([ex['name'] for ex in day.get('exercises', [])])
        }
        serialized.append(day_info)

    output_str = json.dumps(serialized, sort_keys=True)
    current_hash = hashlib.md5(output_str.encode()).hexdigest()
    
    # Expected MD5 snapshot hash for intermediate, 4-day male hypertrophy, dumbbell-only plan
    expected_hash = "5a3c2b85e77b680d39f88df860543e68"
    
    assert current_hash == expected_hash, (
        f"Workout plan output regression detected!\n"
        f"Expected Hash: {expected_hash}\n"
        f"Current Hash:  {current_hash}\n"
        f"Serialized output: {output_str}"
    )


# ==============================================================================
# 8. API Response Contract Parity Test
# ==============================================================================
def test_api_contract_response_parity(monkeypatch):
    """Verify the FastAPI server response schema matches the expected shape and keys."""
    # Mock authentication to allow test running offline without MongoDB
    monkeypatch.setattr(server, "_require_user_id_from_request", lambda req, token: "mock_user_id")
    
    # Mock find_user_workouts to return None (no prior workouts)
    mock_find_user = AsyncMock(return_value=None)
    monkeypatch.setattr(server, "_find_user_workouts_by_id", mock_find_user)

    client = TestClient(server.app)

    payload = {
        "age": 25,
        "weight": 70,
        "height": 175,
        "gender": "Male",
        "goal": "Muscle Gain",
        "experience": "Beginner",
        "days_per_week": 3,
        "equipment": ["Dumbbell"],
        "body_issues": [],
        "streak": 0,
        "consistency": 0.7,
        "firstWorkoutDay": 0,
        "registrationDate": "2026-06-22T00:00:00Z",
        "is_new_user_week": True
    }

    # Request workout generation
    response = client.post("/workout", json=payload, headers={"x-auth-token": "dummy_token"})
    
    assert response.status_code == 200, f"API failed with status {response.status_code}: {response.text}"
    
    body = response.json()
    assert body["success"] is True, "Response success field is not True"
    assert "data" in body, "Response is missing 'data' envelope"
    
    data = body["data"]
    assert "workout" in data, "Data envelope is missing 'workout' key"
    assert "exercises_count" in data, "Data envelope is missing 'exercises_count'"
    assert "workout_days" in data, "Data envelope is missing 'workout_days'"
    assert "rest_days" in data, "Data envelope is missing 'rest_days'"
    assert "week_metadata" in data, "Data envelope is missing 'week_metadata'"
    
    # Verify workout day structures
    workout = data["workout"]
    assert len(workout) == 7, f"API returned {len(workout)} days instead of 7"
    for day in workout:
        assert "day" in day
        assert "type" in day
        assert "exercises" in day
        if day["type"] == "workout":
            assert len(day["exercises"]) > 0
            # Ensure no warmups are leaked into the exercises list in API output
            for ex in day["exercises"]:
                assert not ex.get("is_warmup")
