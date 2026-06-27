import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from fastapi.testclient import TestClient
import os
import sys

# Ensure backend-python is in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

@pytest.fixture()
def client():
    with patch("motor.motor_asyncio.AsyncIOMotorClient") as mock_mongo:
        if "server" in sys.modules:
            del sys.modules["server"]
        os.environ.setdefault("MONGO_URI", "mongodb://localhost:27017/test")
        os.environ.setdefault("JWT_SECRET", "test_secret_pytest_placeholder_32c")
        os.environ.setdefault("GEMINI_API_KEY", "dummy")
        
        from server import app
        from app.routes.profile import get_current_user_from_token
        
        # Override dependency
        app.dependency_overrides[get_current_user_from_token] = lambda: {"user_id": "507f1f77bcf86cd799439011"}
        
        yield TestClient(app, raise_server_exceptions=False)
        
        # Clean up
        app.dependency_overrides.clear()

def test_profile_update_nutrition_regeneration(client):
    # Mock database functions and safe_find_one/safe_update_one
    mock_existing_user = {
        "_id": "507f1f77bcf86cd799439011",
        "email": "test@example.com",
        "age": 25,
        "weight": 70.0,
        "height": 175.0,
        "gender": "male",
        "goal": "Muscle Gain",
        "experience": "Beginner",
        "dietary_preference": "Vegetarian",
        "workoutPlan": []
    }
    
    # Safe update mock result
    mock_update_result = MagicMock()
    mock_update_result.matched_count = 1
    mock_update_result.modified_count = 1

    # Mock meal engine generation
    mock_nutrition_plan = {
        "status": "success",
        "plan": {
            "weekly_plan": {
                "Day_1": {"breakfast": [], "lunch": [], "dinner": [], "snack": []}
            },
            "shopping_list": {}
        }
    }

    # Apply patches
    with patch("app.routes.profile.safe_find_one", side_effect=[mock_existing_user, {**mock_existing_user, "dietary_preference": "Non-Veg"}]), \
         patch("app.routes.profile.safe_update_one", return_value=mock_update_result), \
         patch("app.routes.profile._generate_nutrition_plan", return_value=mock_nutrition_plan), \
         patch("app.routes.profile.get_database"), \
         patch("app.routes.profile.get_prescription_targets", return_value={'water_target_ml': 2000, 'sleep_target_hours': 8.0}), \
         patch("app.routes.meal_plan._archive_old_plans", new_callable=AsyncMock), \
         patch("app.db.get_weekly_meal_plans_collection") as mock_weekly_plans:
         
         # Mock insert_one on weekly_plans collection
         mock_coll = AsyncMock()
         mock_weekly_plans.return_value = mock_coll
         
         # Headers with auth token
         headers = {"x-auth-token": "dummy_token"}
         
         # Update dietary_preference to trigger nutrition regeneration
         response = client.put(
             "/profile/update",
             json={"dietary_preference": "Non-Veg"},
             headers=headers
         )
         
         # Verify responses
         assert response.status_code == 200
         data = response.json()
         assert data["success"] is True
         assert data["profile_changes"]["nutrition_regenerated"] is True
         assert data["profile_changes"]["workout_regenerated"] is False
