import pytest
from unittest.mock import AsyncMock, MagicMock
import pandas as pd

from app.utils.movement_mapper import get_movement_metadata, EXERCISE_METADATA
from app.workout_engine import WorkoutEngine
from app.progression_engine import get_progression_engine

# 1. Movement Mapping Test
def test_movement_mapping():
    """Verify that Push-Up variations resolve correctly to horizontal_push."""
    pushup_variations = ["Push-Up", "Decline Push-Up", "Diamond Push-Up"]
    for name in pushup_variations:
        meta = get_movement_metadata(name)
        assert meta["pattern"] == "horizontal_push", f"{name} did not map to horizontal_push"

# 2. Equipment Constraint Test
def test_equipment_constraint():
    """Verify that if available equipment is empty, dumbbell-only exercises are not returned."""
    engine = WorkoutEngine()
    
    # Generate exercises with no equipment
    exercises = engine._get_exercises_for_day(
        focus="Chest",
        goal="Muscle Gain",
        experience="Beginner",
        equipment=[],
        body_issues=[],
        profile={"age": 25, "streak": 0}
    )
    
    # Verify no selected exercise requires dumbbells
    for ex in exercises:
        assert "dumbbell" not in ex["name"].lower(), f"Dumbbell exercise '{ex['name']}' returned when no equipment is available"
        assert "dumbbell" not in ex["equipment"].lower(), f"Dumbbell equipment requirement found in '{ex['name']}'"

# 3. Injury Constraint Test
def test_injury_constraint():
    """Verify that exercises flagged as avoid are filtered out for specific injuries."""
    engine = WorkoutEngine()
    
    # Identify which exercises in the CSV are restricted for "shoulder" issues
    shoulder_restricted = engine.exercises_df[
        engine.exercises_df['Avoid_If'].str.contains('shoulder', case=False, na=False)
    ]
    restricted_names = set(shoulder_restricted['Name'].tolist())
    
    # We should have some restricted shoulder exercises
    assert len(restricted_names) > 0, "No shoulder-restricted exercises found in CSV database"
    
    # Generate exercises with 'shoulder' issue
    exercises = engine._get_exercises_for_day(
        focus="Chest",
        goal="Muscle Gain",
        experience="Intermediate",
        equipment=["Dumbbell"],
        body_issues=["shoulder"],
        profile={"age": 25, "streak": 0}
    )
    
    # Verify none of the returned exercises are shoulder-restricted
    for ex in exercises:
        assert ex["name"] not in restricted_names, f"Shoulder-restricted exercise '{ex['name']}' was returned despite injury constraint"

# 4. History Truncation Test
@pytest.mark.anyio
async def test_history_truncation(monkeypatch):
    """Verify that _find_user_workouts_by_id respects MongoDB $slice to only load the last 50 entries."""
    import server
    from bson import ObjectId
    
    # Mock the database client and find_one method
    mock_db = MagicMock()
    mock_find_one = AsyncMock(return_value={"_id": ObjectId("507f1f77bcf86cd799439011"), "workouts": []})
    mock_db.users.find_one = mock_find_one
    
    # Patch the database connection
    monkeypatch.setattr(server, "get_database", lambda: mock_db)
    
    user_id = "507f1f77bcf86cd799439011"
    
    # Call the database helper with limit=50
    await server._find_user_workouts_by_id(user_id, limit=50)
    
    # Assert find_one was called with the correct projection containing $slice of -50
    mock_find_one.assert_called_once_with(
        {"_id": ObjectId(user_id)},
        {"workouts": {"$slice": -50}}
    )

# 5. Home Workout Only & Warm-up Separation Test
def test_home_workout_only_and_warmup_separation():
    """Verify that only home equipment exercises are loaded, and that weekly plans separate warm-ups from main exercises."""
    engine = WorkoutEngine()
    
    # 1. Verify only home equipment exercises are in the database
    allowed_equipments = {
        'body weight', 'bodyweight', 'dumbbell', 'band', 'resistance band',
        'kettlebell', 'medicine ball', 'stability ball', 'bosu ball', 'roller',
        'wheel roller', 'rope', 'weighted', 'none', 'no equipment', 'assisted'
    }
    
    for eq in engine.exercises_df['Equipment'].unique():
        assert eq.lower().strip() in allowed_equipments, f"Forbidden gym equipment '{eq}' found in loaded database!"
        
    # 2. Generate weekly plan and verify separate warm-up count
    profile = {
        'goal': 'Muscle Gain',
        'experience': 'Beginner',
        'equipment': ['Dumbbells', 'Resistance Bands'],
        'body_issues': [],
        'days_per_week': 3,
        'age': 25,
        'streak': 0,
        'weight': 70,
        'height': 175,
        'gender': 'male'
    }
    
    plan = engine.generate_weekly_plan(profile)
    assert len(plan) == 7
    
    for day in plan:
        if day['type'] == 'workout':
            # Check warmups are populated
            assert 'warmup' in day
            assert len(day['warmup']) > 0
            
            # Check exercises list has only main exercises (no warmup exercises should be in 'exercises' list)
            for ex in day['exercises']:
                assert not ex.get('is_warmup'), f"Warm-up exercise '{ex['name']}' found in 'exercises' list!"
                
            # Check that exercises_total is correct and only counts main exercises
            assert day['exercises_total'] == len(day['exercises'])

