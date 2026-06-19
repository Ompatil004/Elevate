"""
BUG-C2: Python backend unit tests — JWT token validation helpers

Tests the token verification logic used in server.py without starting
the FastAPI server or connecting to MongoDB.

Run: pytest tests/ -v
"""

import pytest
import jwt
import time
from datetime import datetime, timedelta, timezone

# ── test constants ────────────────────────────────────────────────────────────
SECRET = "test_secret_min_32_chars_for_pytest"
ALGORITHM = "HS256"


def create_token(payload: dict, secret: str = SECRET, expires_in: int = 3600) -> str:
    """Helper: build a JWT the same way server.py does."""
    data = payload.copy()
    data["exp"] = datetime.now(timezone.utc) + timedelta(seconds=expires_in)
    return jwt.encode(data, secret, algorithm=ALGORITHM)


def decode_token(token: str, secret: str = SECRET) -> dict:
    """Helper: decode and verify a JWT."""
    return jwt.decode(token, secret, algorithms=[ALGORITHM])


# ── tests ─────────────────────────────────────────────────────────────────────
class TestTokenRoundTrip:
    def test_valid_token_decodes_correctly(self):
        payload = {"id": "user_abc", "email": "alice@example.com"}
        token = create_token(payload)
        decoded = decode_token(token)
        assert decoded["id"] == "user_abc"
        assert decoded["email"] == "alice@example.com"

    def test_expired_token_raises(self):
        token = create_token({"id": "x"}, expires_in=-1)
        with pytest.raises(jwt.ExpiredSignatureError):
            decode_token(token)

    def test_wrong_secret_raises(self):
        token = create_token({"id": "x"})
        with pytest.raises(jwt.InvalidSignatureError):
            decode_token(token, secret="completely_different_secret_value")

    def test_malformed_token_raises(self):
        with pytest.raises(jwt.DecodeError):
            decode_token("this.is.garbage")

    def test_missing_exp_claim_still_decodes(self):
        """Tokens without exp should decode — server.py sets options explicitly."""
        token = jwt.encode({"id": "no_exp"}, SECRET, algorithm=ALGORITHM)
        decoded = jwt.decode(token, SECRET, algorithms=[ALGORITHM], options={"verify_exp": False})
        assert decoded["id"] == "no_exp"


class TestSuspensionClaim:
    """Verifies that isSuspended can be read from the token payload."""

    def test_is_suspended_false_by_default(self):
        token = create_token({"id": "u1", "isSuspended": False})
        decoded = decode_token(token)
        assert decoded["isSuspended"] is False

    def test_suspended_user_flag_preserved(self):
        token = create_token({"id": "u2", "isSuspended": True})
        decoded = decode_token(token)
        assert decoded["isSuspended"] is True

    def test_missing_suspension_claim_returns_none(self):
        token = create_token({"id": "u3"})
        decoded = decode_token(token)
        assert decoded.get("isSuspended") is None
