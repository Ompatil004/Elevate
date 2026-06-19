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
