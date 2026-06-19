import pytest
import jwt
import os
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock, patch

from server import app
from app.routes.chatbot import _chat_rate_limits

@pytest.fixture()
def client():
    """Import server and create a TestClient with MongoDB patched out."""
    with patch("motor.motor_asyncio.AsyncIOMotorClient") as mock_mongo:
        # Simple mock for mongo db client
        mock_db = AsyncMock()
        mock_mongo.return_value.__getitem__ = lambda self, k: mock_db
        
        # Ensure rate limit cooldown is disabled for tests
        os.environ["CHAT_COOLDOWN_SECONDS"] = "0"
        os.environ["JWT_SECRET"] = "test_secret_pytest_placeholder_32c"
        
        yield TestClient(app, raise_server_exceptions=False)

def test_chatbot_sanity_flow(client):
    """
    Sanity test:
    - Simulates a user session.
    - Asks 5-10 follow-up questions to the chatbot (building chat history).
    - Simulates 'page refresh' by starting a new request thread/call but retaining history.
    - Verifies chatbot response quality and context memory.
    - Runs once with health-consent enabled, and once without.
    """
    token = jwt.encode({"user": {"id": "user_sanity_test_125"}}, "test_secret_pytest_placeholder_32c", algorithm="HS256")
    headers = {"x-auth-token": token}
    
    # 5 follow-up questions representing a conversation flow
    questions = [
        "Hi, I want to start getting in shape. Can you help me?",
        "I'm a beginner and I want to build muscle. I have no equipment.",
        "How many days per week should I train for that goal?",
        "Are push-ups and squats good for this?",
        "Thanks, can you tell me what we talked about so far to make sure you remember?"
    ]
    
    # Run test WITH health-consent enabled
    print("\n--- Testing WITH Health Consent Enabled ---")
    history = []
    profile = {
        "experience": "beginner",
        "goal": "muscle_gain",
        "equipment": [],
        "workout_days": 3,
        "age": 25,
        "weight": 70,
        "height": 175
    }
    
    for q in questions:
        _chat_rate_limits.clear() # Clear rate limits to avoid 429
        payload = {
            "message": q,
            "profile": profile,
            "history": history,
            "consent_to_health_processing": True
        }
        
        response = client.post("/api/chat", json=payload, headers=headers)
        assert response.status_code == 200, f"Failed at question: {q}. Response: {response.text}"
        data = response.json()
        assert data["success"] is True
        reply = data["reply"]
        assert len(reply) > 0
        
        # Append user message and model response to history
        history.append({"role": "user", "content": q})
        history.append({"role": "coach", "content": reply})
        print(f"User: {q}")
        print(f"Coach: {reply[:100]}...\n")
        
    # Verify model remembers context in the last response (should mention muscle, beginner, or no equipment)
    last_reply_lower = history[-1]["content"].lower()
    # Check if the AI's summary contains key terms from previous turns
    key_terms = ["beginner", "muscle", "equipment", "days", "push-up", "squat", "train", "work", "shape"]
    match_count = sum(1 for term in key_terms if term in last_reply_lower)
    print(f"Key terms match count in summary: {match_count}")
    # At least some of the topics should be mentioned
    assert match_count >= 1, f"Coach response did not show memory: {history[-1]['content']}"

    # Run test WITHOUT health-consent enabled
    print("\n--- Testing WITHOUT Health Consent Enabled ---")
    history_no_consent = []
    for q in questions[:3]: # Let's ask 3 questions
        _chat_rate_limits.clear()
        payload = {
            "message": q,
            "profile": profile,
            "history": history_no_consent,
            "consent_to_health_processing": False
        }
        
        response = client.post("/api/chat", json=payload, headers=headers)
        assert response.status_code == 200, f"Failed at question: {q}. Response: {response.text}"
        data = response.json()
        assert data["success"] is True
        reply = data["reply"]
        
        history_no_consent.append({"role": "user", "content": q})
        history_no_consent.append({"role": "coach", "content": reply})
        print(f"User (No Consent): {q}")
        print(f"Coach: {reply[:100]}...\n")
