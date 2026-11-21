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
        backend_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
        if backend_dir not in sys.path:
            sys.path.insert(0, backend_dir)

        os.environ.setdefault("MONGO_URI", "mongodb://localhost:27017/test")
        os.environ.setdefault("JWT_SECRET", "test_secret_pytest_placeholder_32c")
        os.environ.setdefault("GEMINI_API_KEY", "dummy")

        from server import app
        yield TestClient(app, raise_server_exceptions=False)


class TestHealthEndpoint:
    def test_health_returns_200(self, client):
        response = client.get("/health")
        assert response.status_code == 200

    def test_health_returns_json_with_status(self, client):
        response = client.get("/health")
        assert response.status_code == 200
        body = response.json()
        assert body.get("status") == "ok"
        assert body.get("service") == "elevate-python"
        assert "timestamp" in body

    def test_health_aliases(self, client):
        res_z = client.get("/healthz")
        assert res_z.status_code == 200
        assert res_z.json().get("status") == "ok"

        res_api = client.get("/api/health")
        assert res_api.status_code == 200
        assert res_api.json().get("status") == "ok"

    def test_health_no_secrets_leaked(self, client):
        response = client.get("/health")
        text = response.text
        assert "mongodb" not in text
        assert "password" not in text
        assert "dummy" not in text


class TestReadinessEndpoint:
    def test_ready_returns_200_when_database_ok(self, client):
        with patch("server._check_database_health", new_callable=AsyncMock) as mock_db:
            mock_db.return_value = {"ok": True}
            response = client.get("/ready")
            assert response.status_code == 200
            body = response.json()
            assert body.get("status") == "ready"
            assert body.get("service") == "elevate-python"
            assert body.get("checks", {}).get("database") == "connected"

    def test_ready_returns_503_when_database_fails(self, client):
        with patch("server._check_database_health", new_callable=AsyncMock) as mock_db:
            mock_db.return_value = {"ok": False, "error": "Connection refused"}
            response = client.get("/ready")
            assert response.status_code == 503
            body = response.json()
            assert body.get("status") == "not_ready"
            assert body.get("checks", {}).get("database") == "disconnected"

    def test_ready_aliases(self, client):
        with patch("server._check_database_health", new_callable=AsyncMock) as mock_db:
            mock_db.return_value = {"ok": True}
            res_z = client.get("/readyz")
            assert res_z.status_code == 200

            res_api = client.get("/api/ready")
            assert res_api.status_code == 200
