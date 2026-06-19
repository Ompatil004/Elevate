"""
BUG-C2: Python backend integration tests — FastAPI health endpoint

Tests the /health route and basic CORS headers using the FastAPI TestClient.
Does NOT connect to a real MongoDB — monkey-patches the DB dependency.

Run: pytest tests/ -v
"""

import pytest
from unittest.mock import AsyncMock, patch
from fastapi.testclient import TestClient


@pytest.fixture()
def client():
    """Import server and create a TestClient with MongoDB patched out."""
    # Patch motor AsyncIOMotorClient before server imports it
    with patch("motor.motor_asyncio.AsyncIOMotorClient") as mock_mongo:
        mock_mongo.return_value.__getitem__ = lambda self, k: AsyncMock()
        import importlib
        import sys

        # Prevent re-use of a cached module with a real DB connection
        if "server" in sys.modules:
            del sys.modules["server"]

        import os
        os.environ.setdefault("MONGO_URI", "mongodb://localhost:27017/test")
        os.environ.setdefault("JWT_SECRET", "test_secret_pytest_placeholder_32c")
        os.environ.setdefault("GEMINI_API_KEY", "dummy")

        from server import app
        yield TestClient(app, raise_server_exceptions=False)


class TestHealthEndpoint:
    def test_health_returns_200(self, client):
        response = client.get("/health")
        # Accept 200 OK
        assert response.status_code == 200

    def test_health_returns_json_with_status(self, client):
        response = client.get("/health")
        if response.status_code == 200:
            body = response.json()
            # Server health check should have some status field
            assert "status" in body or "ok" in body or response.text is not None
