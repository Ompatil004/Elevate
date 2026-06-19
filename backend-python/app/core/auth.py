import os
import uuid
import jwt
from typing import Optional
from fastapi import Request, HTTPException

def extract_auth_token_from_request(
    request: Optional[Request],
    x_auth_token: Optional[str] = None,
) -> Optional[str]:
    """Resolve auth token from header first, then HttpOnly cookie."""
    if x_auth_token and str(x_auth_token).strip():
        return str(x_auth_token).strip()
    if request is None:
        return None
    cookie_token = request.cookies.get("elevate_token")
    if cookie_token and str(cookie_token).strip():
        return str(cookie_token).strip()
    return None

def require_user_id_from_token(x_auth_token: Optional[str], request_id: Optional[str] = None) -> str:
    """Decode JWT and return user id, raising HTTP 401 on missing/invalid token."""
    rid = request_id or str(uuid.uuid4())[:8]
    if not x_auth_token:
        raise HTTPException(
            status_code=401,
            detail={"error": "Missing auth token", "request_id": rid}
        )

    try:
        payload = jwt.decode(
            x_auth_token,
            os.getenv("JWT_SECRET"),
            algorithms=["HS256"],
        )
        user_obj = payload.get("user") if isinstance(payload, dict) else None
        user_id = (user_obj or {}).get("id")
        
        if not user_id:
            raise ValueError("Token missing strictly formatted user identifier")
        return str(user_id)
    except Exception:
        raise HTTPException(
            status_code=401,
            detail={"error": "Invalid auth token", "request_id": rid}
        )

def require_user_id_from_request(
    request: Optional[Request],
    x_auth_token: Optional[str] = None,
    request_id: Optional[str] = None,
) -> str:
    """Extract auth token from request, then require and return user id."""
    token = extract_auth_token_from_request(request, x_auth_token)
    return require_user_id_from_token(token, request_id)
