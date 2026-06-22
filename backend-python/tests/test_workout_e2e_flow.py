import pytest
import datetime
import random
import json
import asyncio
import os
from bson import ObjectId
from fastapi.testclient import TestClient
from unittest.mock import MagicMock, AsyncMock
from concurrent.futures import ThreadPoolExecutor

from app.workout_engine import WorkoutEngine
from app.db import AsyncIOMotorClient
import server

# --- Mock Datetime ---
class FrozenDatetime(datetime.datetime):
    @classmethod
    def utcnow(cls):
        return datetime.datetime(2026, 6, 22, 12, 0, 0)
    
    @classmethod
    def now(cls, tz=None):
        if tz is not None:
            return datetime.datetime(2026, 6, 22, 12, 0, 0, tzinfo=tz)
        return datetime.datetime(2026, 6, 22, 12, 0, 0)

# --- Mock Database Adapters ---
class MockMongoCollection:
    def __init__(self, db_store, name):
        self.db_store = db_store
        self.name = name

    async def find_one(self, query, projection=None):
        user_id = str(query.get("_id"))
        user = self.db_store.get(user_id)
        if not user:
            return None
        import copy
        return copy.deepcopy(user)

    async def update_one(self, query, update_dict, upsert=False):
        user_id = str(query.get("_id"))
        if user_id not in self.db_store:
            if upsert:
                self.db_store[user_id] = {"_id": ObjectId(user_id)}
            else:
                mock_res = MagicMock()
                mock_res.matched_count = 0
                return mock_res

        # Apply $set operator
        set_ops = update_dict.get("$set", {})
        for k, v in set_ops.items():
            self.db_store[user_id][k] = v
            
        mock_res = MagicMock()
        mock_res.matched_count = 1
        return mock_res

class MockDatabase:
    def __init__(self, db_store):
        self.users = MockMongoCollection(db_store, "users")

# --- Test Fixtures ---
@pytest.fixture(autouse=True)
def setup_e2e_mocks(monkeypatch):
    # Lock time inputs to be deterministic
    monkeypatch.setattr("app.workout_engine.datetime", FrozenDatetime)
    monkeypatch.setattr("app.workout_engine._utcnow", lambda: datetime.datetime(2026, 6, 22, 12, 0, 0))
    monkeypatch.setattr("server.datetime", FrozenDatetime)
    monkeypatch.setattr("server._utcnow", lambda: datetime.datetime(2026, 6, 22, 12, 0, 0))

    # Mock Gemini AI calls
    monkeypatch.setattr("app.workout_engine.is_gemini_available", lambda: False)
    monkeypatch.setattr("server._ensure_chatbot_module_loaded", lambda: False)

    # Disable network threads and requests
    monkeypatch.setattr("app.workout_engine.WorkoutEngine._lazy_load_wger", lambda self: None)
    monkeypatch.setattr("app.workout_engine.WorkoutEngine._initialize_wger_media_index", lambda self: None)
    monkeypatch.setattr("app.workout_engine.WorkoutEngine._check_url_reachable", lambda self, url, accept_any_response=False: True)

    random.seed(42)

# ==============================================================================
# 1. End-To-End Lifecycle Validation with Debug Trace Checks
# ==============================================================================
def test_profile_update_to_persisted_fetch_e2e_flow(monkeypatch):
    """
    Simulate full system trace:
    - PUT /profile/update-safe updates profile, triggers regeneration, and attaches debug trace.
    - Python backend persists plans to MongoDB.
    - GET /api/weekly-plan retrieves plans and validates debug explainability.
    """
    mock_user_id = str(ObjectId())
    
    in_memory_db = {
        mock_user_id: {
            "_id": ObjectId(mock_user_id),
            "email": "user@example.com",
            "age": 30,
            "weight": 70,
            "height": 175,
            "gender": "Male",
            "goal": "Muscle Gain",
            "experience": "Intermediate",
            "days_per_week": 2,
            "equipment": ["Dumbbell"],
            "body_issues": [],
            "streak": 10,
            "consistency": 0.8,
            "workoutPlan": [],
            "workoutWeekMetadata": {}
        }
    }

    # Intercept Database requests
    mock_db = MockDatabase(in_memory_db)
    monkeypatch.setattr(server, "get_database", lambda: mock_db)
    
    # Mock Auth layer to decode user_id directly from header token
    monkeypatch.setattr(server, "_require_user_id_from_request", lambda req, token, req_id=None: token)
    monkeypatch.setattr(server, "_find_user_by_id", lambda uid: mock_db.users.find_one({"_id": ObjectId(uid)}))

    client = TestClient(server.app)

    # Update to 4 days, Female adjustments (reps shift +2, rest -15%)
    payload = {
        "age": 30,
        "weight": 75,
        "height": 175,
        "gender": "Female",
        "goal": "Muscle Gain",
        "experience": "Intermediate",
        "days_per_week": 4,
        "equipment": ["Dumbbells"],
        "body_issues": []
    }

    # --- PUT Profile Update ---
    response = client.put("/profile/update-safe", json=payload, headers={"x-auth-token": mock_user_id})
    assert response.status_code == 200
    body = response.json()
    assert body["success"] is True

    # --- DB Verification ---
    updated_user_doc = in_memory_db[mock_user_id]
    assert updated_user_doc["days_per_week"] == 4
    assert updated_user_doc["gender"] == "Female"
    
    db_workout_plan = updated_user_doc["workoutPlan"]
    assert len(db_workout_plan) == 7
    
    # Verify debug_trace exists in persisted DB plan
    for day in db_workout_plan:
        assert "debug_trace" in day, "debug_trace was not persisted in DB"
        trace = day["debug_trace"]
        assert trace["days_per_week_requested"] == 4
        assert trace["days_per_week_capped"] == 4
        assert trace["gender"] == "Female"
        assert trace["experience"] == "Intermediate"

    # --- GET Fetched Plan Parity & Parity Checks ---
    fetch_resp = client.get("/api/weekly-plan", headers={"x-auth-token": mock_user_id})
    assert fetch_resp.status_code == 200
    fetched_body = fetch_resp.json()
    fetched_plan = fetched_body["data"]["plan"]
    
    # Verify frontend-received payload has debug traces
    for day in fetched_plan:
        assert "debug_trace" in day
        assert day["debug_trace"]["days_per_week_capped"] == 4

# ==============================================================================
# 2. Concurrency & Race-Condition Validation
# ==============================================================================
def test_concurrent_profile_updates_no_state_leakage(monkeypatch):
    """
    Ensure the singleton engine remains stateless under multi-user concurrent requests,
    meaning User A's generation parameters never bleed into User B's generation.
    """
    # Create two users with distinct targets
    user_a_id = str(ObjectId())
    user_b_id = str(ObjectId())
    
    in_memory_db = {
        user_a_id: {
            "_id": ObjectId(user_a_id),
            "email": "a@example.com",
            "experience": "Intermediate",
            "days_per_week": 2,
            "workoutPlan": []
        },
        user_b_id: {
            "_id": ObjectId(user_b_id),
            "email": "b@example.com",
            "experience": "Advanced",
            "days_per_week": 2,
            "workoutPlan": []
        }
    }

    mock_db = MockDatabase(in_memory_db)
    monkeypatch.setattr(server, "get_database", lambda: mock_db)
    monkeypatch.setattr(server, "_require_user_id_from_request", lambda req, token, req_id=None: token)
    monkeypatch.setattr(server, "_find_user_by_id", lambda uid: mock_db.users.find_one({"_id": ObjectId(uid)}))

    client = TestClient(server.app)

    payload_a = {
        "age": 25, "weight": 60, "height": 160, "gender": "Female",
        "goal": "Muscle Gain", "experience": "Intermediate", "days_per_week": 4,
        "equipment": ["Dumbbells"], "body_issues": []
    }
    
    payload_b = {
        "age": 45, "weight": 90, "height": 185, "gender": "Male",
        "goal": "Strength", "experience": "Advanced", "days_per_week": 5,
        "equipment": ["Dumbbells"], "body_issues": []
    }

    # Run updates in parallel threads
    def call_update(user_id, payload):
        return client.put("/profile/update-safe", json=payload, headers={"x-auth-token": user_id})

    with ThreadPoolExecutor(max_workers=2) as executor:
        future_a = executor.submit(call_update, user_a_id, payload_a)
        future_b = executor.submit(call_update, user_b_id, payload_b)
        
        res_a = future_a.result()
        res_b = future_b.result()

    # Both must succeed
    assert res_a.status_code == 200
    assert res_b.status_code == 200

    # Verify User A did not get overwritten or corrupted by User B
    doc_a = in_memory_db[user_a_id]
    workout_days_a = sum(1 for d in doc_a["workoutPlan"] if d["type"] == "workout")
    assert workout_days_a == 4, f"User A has {workout_days_a} workout days, expected 4"
    assert doc_a["workoutPlan"][0]["debug_trace"]["experience"] == "Intermediate"
    assert doc_a["workoutPlan"][0]["debug_trace"]["gender"] == "Female"

    # Verify User B did not get corrupted by User A
    doc_b = in_memory_db[user_b_id]
    workout_days_b = sum(1 for d in doc_b["workoutPlan"] if d["type"] == "workout")
    assert workout_days_b == 5, f"User B has {workout_days_b} workout days, expected 5"
    assert doc_b["workoutPlan"][0]["debug_trace"]["experience"] == "Advanced"
    assert doc_b["workoutPlan"][0]["debug_trace"]["gender"] == "Male"

# ==============================================================================
# 3. Real MongoDB Integration Test (Conditional on connection)
# ==============================================================================
@pytest.mark.anyio
async def test_real_mongodb_connection_persistence_if_available():
    """
    If a local/reachable MongoDB server is running, execute a real integration 
    test writing and reading actual document structures.
    """
    mongo_uri = os.getenv("MONGO_URI", "mongodb://127.0.0.1:27017/elevate_fitness_test")
    try:
        # Create real Async Motor Client
        real_client = AsyncIOMotorClient(mongo_uri, serverSelectionTimeoutMS=2000)
        await real_client.admin.command("ping")
    except Exception:
        pytest.skip("Local/configured MongoDB is not running or reachable. Skipping real database test.")
        return

    # Database instance setup
    db_name = "elevate_fitness_test"
    db = real_client[db_name]
    
    test_user_id = ObjectId()
    
    # 1. Setup clean record
    await db.users.delete_one({"_id": test_user_id})
    await db.users.insert_one({
        "_id": test_user_id,
        "email": "integration@test.com",
        "days_per_week": 2,
        "workoutPlan": []
    })

    try:
        # 2. Simulate plan generation
        engine = WorkoutEngine()
        profile = {
            'user_id': str(test_user_id),
            'goal': 'Muscle Gain',
            'experience': 'Intermediate',
            'equipment': ['Dumbbell'],
            'body_issues': [],
            'days_per_week': 4,
            'age': 25,
            'streak': 10,
            'consistency': 0.8,
            'gender': 'Male',
            'week_offset': 202625
        }
        weekly_plan = engine.generate_weekly_plan(profile)

        # 3. Direct real write to Mongo
        await db.users.update_one(
            {"_id": test_user_id},
            {"$set": {
                "workoutPlan": weekly_plan,
                "days_per_week": 4,
                "updatedAt": datetime.datetime.utcnow()
            }}
        )

        # 4. Direct real read from Mongo
        doc = await db.users.find_one({"_id": test_user_id})
        assert doc is not None
        assert doc["days_per_week"] == 4
        assert len(doc["workoutPlan"]) == 7
        
        # Verify the structure inside real Mongo
        workout_days = sum(1 for d in doc["workoutPlan"] if d["type"] == "workout")
        assert workout_days == 4, f"Real Mongo stored plan has {workout_days} workout days, expected 4"

    finally:
        # Clean up database
        await db.users.delete_one({"_id": test_user_id})
        real_client.close()
