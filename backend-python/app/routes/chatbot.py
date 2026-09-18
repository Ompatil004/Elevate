import os
import time
import logging
import traceback
import threading
from collections import OrderedDict
from typing import Dict, List, Any, Optional

from fastapi import APIRouter, Request, Header, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

from app.core.auth import require_user_id_from_request
from app.core.responses import api_success
from app.gemini_service import get_chatbot_response, is_gemini_available
from app.db import get_database

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api", tags=["chatbot"])

class ChatRequest(BaseModel):
    message: str = Field(..., max_length=4096)
    profile: Dict[str, Any] = Field(default_factory=dict)
    history: List[Dict[str, Any]] = Field(default_factory=list, max_length=50)
    consent_to_health_processing: bool = False


# --- Rate Limiting variables ---
_chat_rate_limits: "OrderedDict[str, float]" = OrderedDict()
_chat_rate_limits_lock = threading.Lock()
CHAT_COOLDOWN_SECONDS = 1.5  # Minimum seconds between requests per user
CHAT_RATE_LIMIT_MAX_CLIENTS = 1024

_TRUST_PROXY = str(os.getenv("TRUST_PROXY", "0")).strip() == "1"


def _get_client_ip(request: Request) -> str:
    """Extract the best-effort real client IP from the request for rate limiting."""
    if _TRUST_PROXY:
        forwarded = request.headers.get("x-forwarded-for", "").strip()
        if forwarded:
            return forwarded.split(",")[0].strip() or "unknown"
        real_ip = request.headers.get("x-real-ip", "").strip()
        if real_ip:
            return real_ip

    if request.client and request.client.host:
        return request.client.host
    return "unknown"


@router.post("/chat")
async def chatbot_endpoint(
    request: ChatRequest,
    http_request: Request,
    x_auth_token: Optional[str] = Header(None, alias="x-auth-token"),
):
    """
    AI Chatbot endpoint powered by Gemini.
    
    Features:
    - Rate limiting to prevent abuse (keyed on real client IP)
    - Input validation
    - Conversation history support
    - Graceful degradation when AI is unavailable
    """
    import time as _time
    _t0 = _time.monotonic()
    logger.info(f"[Chatbot-Python] request received")

    try:
        user_id = require_user_id_from_request(http_request, x_auth_token)

        # --- Rate Limiting ---
        client_id = _get_client_ip(http_request)
        now = time.time()
        with _chat_rate_limits_lock:
            last_request = _chat_rate_limits.get(client_id, 0)
            is_limited = (now - last_request) < CHAT_COOLDOWN_SECONDS

            if not is_limited:
                _chat_rate_limits[client_id] = now
                _chat_rate_limits.move_to_end(client_id)

                # Drop stale entries first, then enforce strict max size to prevent memory growth.
                cutoff = now - 60
                stale = [cid for cid, ts in list(_chat_rate_limits.items()) if ts < cutoff]
                for cid in stale:
                    _chat_rate_limits.pop(cid, None)

                while len(_chat_rate_limits) > CHAT_RATE_LIMIT_MAX_CLIENTS:
                    _chat_rate_limits.popitem(last=False)

        if is_limited:
            return JSONResponse(
                status_code=429,
                content={
                    "success": False,
                    "message": "Rate limit exceeded",
                    "data": {},
                    "reply": "You're sending messages too fast! Please wait a moment.",
                    "error": "rate_limited"
                }
            )

        # --- Validate Input ---
        message = request.message.strip()
        if not message:
            return api_success(
                "Chat response generated",
                data={"reply": "I didn't catch that. Could you try again? 🤔"},
                reply="I didn't catch that. Could you try again? 🤔",
            )

        if len(message) > 2000:
            message = message[:2000]

        # --- Get AI Response ---
        raw_profile = request.profile or {}
        if request.consent_to_health_processing:
            allowed_keys = {
                "goal",
                "experience",
                "activity_level",
                "dietary_preference",
                "equipment",
                "age",
                "weight",
                "height",
                "allergies",
                "body_issues",
            }
        else:
            allowed_keys = {
                "goal",
                "experience",
                "activity_level",
                "dietary_preference",
                "equipment",
            }

        profile = {
            key: value
            for key, value in raw_profile.items()
            if key in allowed_keys
        }
        
        # Fetch real-time activity and workout history — with explicit timeouts
        _db_t0 = _time.monotonic()
        logger.info(f"[Chatbot-Python] DB lookup start (+{_db_t0-_t0:.2f}s)")
        try:
            from datetime import datetime, timezone
            from bson import ObjectId
            import asyncio as _asyncio
            db = get_database()
            today_str = datetime.now(timezone.utc).strftime("%Y-%m-%d")
            # Hard 5s timeout on DB queries — prevents indefinite hang if Mongo is slow
            daily_log, user_doc = await _asyncio.wait_for(
                _asyncio.gather(
                    db.daily_logs.find_one({"user_id": user_id, "date": today_str}),
                    db.users.find_one({"_id": ObjectId(user_id)}),
                ),
                timeout=5.0,
            )
            
            profile["_daily_log"] = {
                "water_ml": daily_log.get("water_ml", 0) if daily_log else 0,
                "sleep_hours": daily_log.get("sleep_hours", 0) if daily_log else 0,
                "workout_completed": daily_log.get("workout_completed", False) if daily_log else False,
            }
            if user_doc:
                workouts = user_doc.get("workouts", [])
                profile["_recent_workouts"] = [
                    {
                        "name": w.get("name"),
                        "date": w.get("date") or w.get("completed_at"),
                        "duration": w.get("duration"),
                    } for w in workouts[-3:]
                ]
        except Exception as db_exc:
            logger.warning(f"[Chatbot-Python] DB lookup failed after {_time.monotonic()-_db_t0:.2f}s: {db_exc}")

        logger.info(f"[Chatbot-Python] DB lookup complete (+{_time.monotonic()-_t0:.2f}s)")

        history = request.history or []

        logger.info(f"[Chatbot-Python] AI provider request start (+{_time.monotonic()-_t0:.2f}s)")
        reply = get_chatbot_response(message, profile, history)
        logger.info(f"[Chatbot-Python] AI provider response received (+{_time.monotonic()-_t0:.2f}s)")

        offline_mode = not is_gemini_available()

        # Check if reply is from fallback
        is_fallback = isinstance(reply, str) and (
            "offline mode" in reply.lower() or 
            "ai service temporarily unavailable" in reply.lower()
        )
        
        logger.info(f"[Chatbot-Python] responding in {_time.monotonic()-_t0:.2f}s offline={offline_mode or is_fallback}")
        return api_success(
            "Chat response generated", 
            data={"reply": reply, "offline_mode": offline_mode or is_fallback},
            reply=reply
        )

    except Exception as e:
        logger.error(f"[Chatbot-Python] unhandled error after {_time.monotonic()-_t0:.2f}s: {e}")
        traceback.print_exc()
        fallback_reply = "I'm having a brief technical issue. Please try again in a moment! 🔄"
        return api_success("Chat response generated", data={"reply": fallback_reply, "offline_mode": True}, reply=fallback_reply)

