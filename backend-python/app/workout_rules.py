"""
Workout Rules Configuration Loader

Mirrors the pattern from app/nutrition_engine/config.py:
- Loads workout_rules.yaml from config/ directory
- Provides module-level WORKOUT_RULES dict
- Falls back to hardcoded defaults if YAML missing/malformed
- Never crashes workout generation due to config issues
"""

import os
import yaml
import logging

logger = logging.getLogger(__name__)

CONFIG_FILE = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "config",
    "workout_rules.yaml"
)

def load_workout_rules():
    """Load workout rules from YAML with hardcoded fallback."""
    try:
        with open(CONFIG_FILE, "r") as f:
            rules = yaml.safe_load(f)
            logger.info(f"Loaded workout_rules.yaml from {CONFIG_FILE}")
            return rules
    except Exception as e:
        logger.warning(f"Could not load workout_rules.yaml: {e}")
        logger.warning("Using hardcoded fallback workout rules")

        # Hardcoded fallback — exact copy of the YAML structure
        return {
            "feature_flags": {
                "workout_engine_v2": True
            },
            "frequency": {
                "Beginner": {"preferred": 3, "maximum": 4},
                "Intermediate": {"preferred": 4, "maximum": 5},
                "Advanced": {"preferred": 5, "maximum": 6}
            },
            "progression_gates": {
                "Beginner": {"streak_required": 21, "consistency_required": 0.85},
                "Intermediate": {"streak_required": 42, "consistency_required": 0.90},
                "Advanced": {"streak_required": 10, "consistency_required": 0.80}
            },
            "age_scheduling": {
                "senior_age": 60,
                "senior_score_penalty": 5,
                "senior_max_consecutive_days": 2
            },
            "exercises_per_session": {
                "Beginner": 4,
                "Intermediate": 5,
                "Advanced": 6
            },
            "split_selection": {
                "beginner_max_sets": 12,
                "intermediate_max_sets": 20,
                "max_session_duration_minutes": 75,
                "min_session_duration_minutes": 20
            },
            "recovery_hours": {
                "Push": 48,
                "Pull": 48,
                "Legs": 72,
                "Core": 24
            },
            "categories": {
                "A": {
                    "name": "Push",
                    "split_type": "Push",
                    "muscles": ["Chest", "Shoulders", "Arms"]
                },
                "B": {
                    "name": "Pull",
                    "split_type": "Pull",
                    "muscles": ["Back", "Shoulders", "Arms"]
                },
                "C": {
                    "name": "Legs",
                    "split_type": "Legs",
                    "muscles": ["Legs", "Calves"]
                },
                "D": {
                    "name": "Core",
                    "split_type": "Core",
                    "muscles": ["Core"]
                }
            },
            "muscle_overlap_map": {
                "Chest": ["Push"],
                "Back": ["Pull"],
                "Shoulders": ["Push", "Pull"],
                "Arms": ["Push", "Pull"],
                "Legs": ["Legs"],
                "Calves": ["Legs"],
                "Core": ["Core"]
            },
            "muscle_dataset_map": {
                "Chest": "Chest",
                "Back": "Back",
                "Shoulders": "Shoulders",
                "Arms": "Arms",
                "Legs": "Legs",
                "Core": "Waist",
                "Calves": "Lower Legs",
                "Traps": "Shoulders"
            },
            "splits": {
                "full_body": [
                    ["Full Body", "Full Body", "Full Body"],
                    ["Full Body (Upper Focus)", "Full Body (Lower Focus)",
                     "Full Body (Push-Pull)", "Full Body"]
                ],
                "upper_lower": [
                    ["Upper Body", "Lower Body", "Upper Body", "Lower Body"],
                    ["Upper Body", "Lower Body", "Upper Body", "Lower Body", "Full Body"]
                ],
                "push_pull_legs": [
                    ["Push", "Pull", "Legs"],
                    ["Push", "Pull", "Legs", "Push"],
                    ["Push", "Pull", "Legs", "Push", "Pull"],
                    ["Push", "Pull", "Legs", "Push", "Pull", "Legs"]
                ],
                "hybrid": [
                    ["Chest & Back", "Legs & Shoulders", "Arms & Core"],
                    ["Chest & Back", "Legs & Shoulders", "Arms & Core", "Pull & Legs"],
                    ["Chest & Back", "Legs & Shoulders", "Arms & Core", "Pull & Legs", "Push & Pull"],
                    ["Chest & Triceps", "Back & Biceps", "Legs (Quads)",
                     "Shoulders & Traps", "Legs (Posterior)", "Arms & Core"]
                ]
            },
            "duration": {
                "per_set_seconds": 40,
                "transition_seconds": 30,
                "warmup_minutes": 5
            },
            "validation": {
                "weekly_validation_retry_limit": 3,
                "required_muscle_groups": ["Chest", "Back", "Legs", "Shoulders", "Arms", "Core"]
            },
            "equipment": {
                "default_equipment": ["Body Weight"]
            },
            "tie_breaking": [
                "coverage",
                "recovery_spacing",
                "diversity",
                "duration"
            ],
            "rest_placement": {
                "max_backtrack_attempts": 3
            },
            "skip_workout_handling": {
                "max_reschedule_lookahead": 3
            }
        }

# Module-level singleton — loaded once at import
WORKOUT_RULES = load_workout_rules()
