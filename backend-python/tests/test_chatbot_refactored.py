import pytest
import jwt
from unittest.mock import AsyncMock, patch
from fastapi.testclient import TestClient

from app.gemini_service import _extract_message_text, _map_role, _build_system_prompt
from server import app


@pytest.fixture()
def client():
    """Import server and create a TestClient with MongoDB patched out."""
    with patch("motor.motor_asyncio.AsyncIOMotorClient") as mock_mongo:
        mock_mongo.return_value.__getitem__ = lambda self, k: AsyncMock()
        import sys
        import os

        # Use environment variables set for testing
        os.environ["MONGO_URI"] = "mongodb://localhost:27017/test"
        os.environ["JWT_SECRET"] = "test_secret_pytest_placeholder_32c"
        os.environ["GEMINI_API_KEY"] = "dummy"

        yield TestClient(app, raise_server_exceptions=False)


class TestChatbotDefensiveHelpers:
    def test_extract_message_text(self):
        assert _extract_message_text({"text": "Hello"}) == "Hello"
        assert _extract_message_text({"content": "World"}) == "World"
        assert _extract_message_text({"message": "Hey"}) == "Hey"
        assert _extract_message_text({"body": "Hi"}) == "Hi"
        assert _extract_message_text({"other": "No"}) == ""
        assert _extract_message_text({}) == ""
        assert _extract_message_text({"text": "  Trim me  "}) == "Trim me"

    def test_map_role(self):
        assert _map_role("assistant") == "Coach"
        assert _map_role("bot") == "Coach"
        assert _map_role("coach") == "Coach"
        assert _map_role("BOT") == "Coach"
        assert _map_role("user") == "User"
        assert _map_role("USER") == "User"
        assert _map_role("anything_else") == "User"


class TestChatbotEndpoints:
    def test_consent_sanitization(self, client):
        token = jwt.encode({"user": {"id": "user_123"}}, "test_secret_pytest_placeholder_32c", algorithm="HS256")
        
        with patch("app.routes.chatbot.is_gemini_available", return_value=True), \
             patch("app.routes.chatbot.get_chatbot_response") as mock_get_response:
            mock_get_response.return_value = "Mocked reply"
            
            headers = {"x-auth-token": token}
            payload = {
                "message": "Hello",
                "profile": {
                    "goal": "muscle_gain",
                    "age": 25,
                    "weight": 70,
                    "height": 175,
                    "allergies": ["peanut"],
                    "body_issues": ["knee_pain"],
                    "equipment": ["dumbbell"]
                },
                "history": [],
                "consent_to_health_processing": False
            }
            
            # Clear rate limit dict for test reliability
            from app.routes.chatbot import _chat_rate_limits
            _chat_rate_limits.clear()

            response = client.post("/api/chat", json=payload, headers=headers)
            assert response.status_code == 200
            
            # Check profile passed to get_chatbot_response
            called_profile = mock_get_response.call_args[0][1]
            assert "goal" in called_profile
            assert "equipment" in called_profile
            assert "age" not in called_profile
            assert "weight" not in called_profile
            assert "height" not in called_profile
            assert "allergies" not in called_profile
            assert "body_issues" not in called_profile

    def test_consent_preservation(self, client):
        token = jwt.encode({"user": {"id": "user_123"}}, "test_secret_pytest_placeholder_32c", algorithm="HS256")
        
        with patch("app.routes.chatbot.is_gemini_available", return_value=True), \
             patch("app.routes.chatbot.get_chatbot_response") as mock_get_response:
            mock_get_response.return_value = "Mocked reply"
            
            headers = {"x-auth-token": token}
            payload = {
                "message": "Hello",
                "profile": {
                    "goal": "muscle_gain",
                    "age": 25,
                    "weight": 70,
                    "height": 175,
                    "allergies": ["peanut"],
                    "body_issues": ["knee_pain"],
                    "equipment": ["dumbbell"]
                },
                "history": [],
                "consent_to_health_processing": True
            }
            
            # Clear rate limit dict for test reliability
            from app.routes.chatbot import _chat_rate_limits
            _chat_rate_limits.clear()

            response = client.post("/api/chat", json=payload, headers=headers)
            assert response.status_code == 200
            
            called_profile = mock_get_response.call_args[0][1]
            assert called_profile.get("age") == 25
            assert called_profile.get("weight") == 70
            assert called_profile.get("height") == 175
            assert called_profile.get("allergies") == ["peanut"]
            assert called_profile.get("body_issues") == ["knee_pain"]

    def test_circuit_breaker_offline_fallback(self, client):
        token = jwt.encode({"user": {"id": "user_123"}}, "test_secret_pytest_placeholder_32c", algorithm="HS256")
        
        with patch("app.routes.chatbot.is_gemini_available", return_value=False):
            headers = {"x-auth-token": token}
            payload = {
                "message": "Hello",
                "profile": {},
                "history": [],
                "consent_to_health_processing": False
            }
            
            # Clear rate limit dict for test reliability
            from app.routes.chatbot import _chat_rate_limits
            _chat_rate_limits.clear()

            response = client.post("/api/chat", json=payload, headers=headers)
            assert response.status_code == 200
            body = response.json()
            assert body["data"]["offline_mode"] is True
            assert "AI service is temporarily unavailable" in body["data"]["reply"]

    def test_fallback_reply_offline_mode_flag(self, client):
        token = jwt.encode({"user": {"id": "user_123"}}, "test_secret_pytest_placeholder_32c", algorithm="HS256")
        
        with patch("app.routes.chatbot.is_gemini_available", return_value=True), \
             patch("app.routes.chatbot.get_chatbot_response") as mock_get_response:
            mock_get_response.return_value = "This is a response in offline mode to help you."
            
            headers = {"x-auth-token": token}
            payload = {
                "message": "Hello",
                "profile": {},
                "history": [],
                "consent_to_health_processing": False
            }
            
            # Clear rate limit dict for test reliability
            from app.routes.chatbot import _chat_rate_limits
            _chat_rate_limits.clear()

            response = client.post("/api/chat", json=payload, headers=headers)
            assert response.status_code == 200
            body = response.json()
            assert body["data"]["offline_mode"] is True

    def test_rate_limiting(self, client):
        token = jwt.encode({"user": {"id": "user_123"}}, "test_secret_pytest_placeholder_32c", algorithm="HS256")
        
        with patch("app.routes.chatbot.is_gemini_available", return_value=True), \
             patch("app.routes.chatbot.get_chatbot_response", return_value="Mocked reply"):
            headers = {"x-auth-token": token}
            payload = {
                "message": "Hello",
                "profile": {},
                "history": [],
                "consent_to_health_processing": False
            }
            
            from app.routes.chatbot import _chat_rate_limits
            _chat_rate_limits.clear()
            
            # First request passes
            response1 = client.post("/api/chat", json=payload, headers=headers)
            assert response1.status_code == 200
            
            # Second request immediately after is limited
            response2 = client.post("/api/chat", json=payload, headers=headers)
            assert response2.status_code == 429
            body2 = response2.json()
            assert body2["success"] is False
            assert body2["error"] == "rate_limited"

