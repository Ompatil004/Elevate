import pytest
import pandas as pd
from app.safety_layer import (
    has_condition,
    apply_nutrition_safety,
    filter_exercises_by_movement,
    validate_workout_safety,
    build_safety_response,
)

# Mocked YAML rules from nutrition_rules.yaml
MOCK_NUTRITION_RULES = {
    "medical_safety": {
        "medical_condition_indicators": {
            "diabetes": ["diabetes", "diabetic", "high blood sugar"],
            "kidney_disease": ["kidney disease", "renal", "ckd"],
            "heart_disease": ["heart disease", "cardiac", "coronary"],
            "hypertension": ["hypertension", "high blood pressure"],
        },
        "safety_adjustments": {
            "diabetes": {"carb_max_g": 150, "label": "diabetes_carb_limit"},
            "kidney_disease": {"protein_multiplier": 0.75, "label": "kidney_disease_protein_reduction"},
            "heart_disease": {"fat_max_g": 60, "label": "heart_disease_fat_limit"},
            "hypertension": {"fat_max_g": 65, "label": "hypertension_fat_limit"},
        },
        "safety_adjustment_order": ["diabetes", "kidney_disease", "heart_disease", "hypertension"],
        "medical_disclaimer": "Safety adjustments applied. Consult your doctor."
    }
}

# Mocked YAML rules from workout_rules.yaml
MOCK_WORKOUT_RULES = {
    "age_scheduling": {
        "senior_age": 60
    },
    "safety": {
        "injury_blocked_patterns": {
            "knee_pain": {
                "condition_indicators": ["knee pain", "knee injury"],
                "blocked_check_types": ["squat_logic", "lunge_logic"],
            },
            "back_pain": {
                "condition_indicators": ["back pain", "lower back"],
                "blocked_check_types": ["crunch_logic", "row_logic", "deadlift_logic"],
            },
            "shoulder_pain": {
                "condition_indicators": ["shoulder pain", "shoulder injury"],
                "blocked_check_types": ["press_logic", "pushup_logic", "dip_logic"],
            },
        },
        "fallback_warning": "Exercises adjusted due to injury.",
        "senior_intensity_modifier": 0.85,
        "senior_volume_modifier": 0.80,
        "senior_rest_multiplier": 1.25,
        "medical_disclaimer": "Workout modified for age or physical limits."
    }
}


def test_has_condition():
    # Basic matching
    assert has_condition(["Type 2 Diabetes"], ["diabetes"]) is True
    assert has_condition(["Knee Injury"], ["knee pain", "knee injury"]) is True
    # Case insensitivity and whitespace
    assert has_condition(["  HYPERTENSION  "], ["hypertension"]) is True
    # Substring matching
    assert has_condition(["Chronic Kidney Disease (CKD)"], ["ckd"]) is True
    # No match
    assert has_condition(["Healthy"], ["diabetes"]) is False
    assert has_condition([], ["diabetes"]) is False
    assert has_condition(["Diabetes"], []) is False


def test_apply_nutrition_safety_diabetes():
    daily_targets = {"carbs_g": 250.0, "protein_g": 120.0, "fat_g": 70.0}
    profile = {"medical_conditions": ["Type 2 Diabetes"]}
    
    adjusted, adjustments = apply_nutrition_safety(daily_targets, profile, MOCK_NUTRITION_RULES)
    
    assert "diabetes_carb_limit" in adjustments
    assert adjusted["carbs_g"] == 150.0
    assert adjusted["protein_g"] == 120.0  # unchanged


def test_apply_nutrition_safety_kidney():
    daily_targets = {"carbs_g": 200.0, "protein_g": 100.0, "fat_g": 70.0}
    profile = {"medical_conditions": ["Chronic Kidney Disease"]}
    
    adjusted, adjustments = apply_nutrition_safety(daily_targets, profile, MOCK_NUTRITION_RULES)
    
    assert "kidney_disease_protein_reduction" in adjustments
    assert adjusted["protein_g"] == 75.0  # 100 * 0.75
    assert adjusted["carbs_g"] == 200.0   # unchanged


def test_apply_nutrition_safety_heart_and_hypertension():
    # Test Heart Disease
    daily_targets_1 = {"carbs_g": 200.0, "protein_g": 100.0, "fat_g": 90.0}
    profile_1 = {"medical_conditions": ["Heart Disease"]}
    adjusted_1, adjustments_1 = apply_nutrition_safety(daily_targets_1, profile_1, MOCK_NUTRITION_RULES)
    assert "heart_disease_fat_limit" in adjustments_1
    assert adjusted_1["fat_g"] == 60.0

    # Test Hypertension
    daily_targets_2 = {"carbs_g": 200.0, "protein_g": 100.0, "fat_g": 90.0}
    profile_2 = {"medical_conditions": ["High Blood Pressure"]}
    adjusted_2, adjustments_2 = apply_nutrition_safety(daily_targets_2, profile_2, MOCK_NUTRITION_RULES)
    assert "hypertension_fat_limit" in adjustments_2
    assert adjusted_2["fat_g"] == 65.0



def test_filter_exercises_by_movement():
    df = pd.DataFrame([
        {"Name": "Squat", "Check_Type": "squat_logic"},
        {"Name": "Lunge", "Check_Type": "lunge_logic"},
        {"Name": "Bench Press", "Check_Type": "press_logic"},
        {"Name": "Bicep Curl", "Check_Type": "curl_logic"},
    ])
    
    filtered, blocked = filter_exercises_by_movement(df, ["squat_logic", "lunge_logic"])
    assert blocked == 2
    assert len(filtered) == 2
    assert list(filtered["Name"]) == ["Bench Press", "Bicep Curl"]


def test_validate_workout_safety_senior():
    weekly_plan = [
        {
            "day": "Monday",
            "type": "workout",
            "intensity": 0.8,
            "intensity_metrics": {"intensity_score": 0.8},
            "exercises": [
                {"name": "Squat", "sets": 4, "rest": "60s"},
                {"name": "Bench Press", "sets": 3, "rest": "90"},
            ],
            "warmup": []
        }
    ]
    profile = {"age": 65}
    
    validated, adjustments, warnings = validate_workout_safety(
        weekly_plan, profile, MOCK_WORKOUT_RULES, None
    )
    
    assert "senior_adjustments" in adjustments
    assert validated[0]["intensity"] == round(0.8 * 0.85, 2)
    assert validated[0]["exercises"][0]["sets"] == round(4 * 0.80)  # 3 sets
    assert validated[0]["exercises"][0]["rest"] == "75s"           # 60 * 1.25
    assert validated[0]["exercises"][1]["sets"] == round(3 * 0.80)  # 2 sets
    assert validated[0]["exercises"][1]["rest"] == "115"           # 90 * 1.25 = 112.5 -> rounded to 115


def test_validate_workout_safety_injury():
    weekly_plan = [
        {
            "day": "Monday",
            "type": "workout",
            "intensity": 0.8,
            "exercises": [
                {"name": "Squat", "sets": 4, "rest": "60s", "Check_Type": "squat_logic"},
                {"name": "Bench Press", "sets": 3, "rest": "90", "Check_Type": "press_logic"},
            ],
            "warmup": []
        }
    ]
    profile = {"body_issues": ["knee injury"]}
    
    validated, adjustments, warnings = validate_workout_safety(
        weekly_plan, profile, MOCK_WORKOUT_RULES, None
    )
    
    assert "knee_pain_filter" in adjustments
    assert len(validated[0]["exercises"]) == 1
    assert validated[0]["exercises"][0]["name"] == "Bench Press"


def test_build_safety_response():
    resp = build_safety_response(["diabetes_carb_limit"], [], MOCK_NUTRITION_RULES, rules_key="medical_safety")
    assert resp["medical_adjustments_applied"] == ["diabetes_carb_limit"]
    assert resp["medical_disclaimer"] == "Safety adjustments applied. Consult your doctor."
