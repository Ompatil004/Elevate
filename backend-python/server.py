from fastapi import FastAPI, HTTPException, Header, Query, BackgroundTasks, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field, EmailStr
from typing import Optional, List, Dict, Any
from dotenv import load_dotenv
from datetime import datetime, timedelta, timezone
import os
import sys
import logging
import traceback
import uuid
import re
import threading
import time
from contextvars import ContextVar
from collections import OrderedDict
import jwt
from bson import ObjectId


def _configure_stdio_for_windows() -> None:
    """Avoid UnicodeEncodeError on Windows cp1252 consoles for logs with Unicode chars."""
    for stream_name in ("stdout", "stderr"):
        stream = getattr(sys, stream_name, None)
        if stream is None:
            continue
        reconfigure = getattr(stream, "reconfigure", None)
        if callable(reconfigure):
            try:
                reconfigure(encoding="utf-8", errors="replace")
            except Exception:
                # Best-effort only; do not block server startup.
                pass


_configure_stdio_for_windows()


def _utcnow() -> datetime:
    """Return naive UTC datetime without using deprecated _utcnow()."""
    return datetime.now(timezone.utc).replace(tzinfo=None)


def _format_integrity_summary(results: Dict[str, str]) -> str:
    issue_items = [f"{name}={status}" for name, status in results.items() if status != "ok"]
    if not issue_items:
        return "all required model checks passed"
    return "issues: " + ", ".join(issue_items)

# CRITICAL: Load .env BEFORE any imports that read environment variables
# (e.g., gemini_service reads GEMINI_API_KEY at module level)
_SERVER_DIR = os.path.dirname(os.path.abspath(__file__))
_DOTENV_PATH = os.path.join(_SERVER_DIR, ".env")
load_dotenv(dotenv_path=_DOTENV_PATH, override=True)

# Add app to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.workout_engine import get_workout_engine
from app.meal_engine import get_meal_engine
from app.db import get_database

# SEC-10: Verify ML model file integrity at startup.
# In production this raises ModelIntegrityError to prevent loading tampered pickles.
# Run  python -c "from app.utils.model_integrity import generate_checksums; generate_checksums()"
# once after training to create app/models/checksums.sha256.
try:
    from app.utils.model_integrity import verify_all_models, ModelIntegrityError
    _is_prod = os.environ.get("NODE_ENV", os.environ.get("PYTHON_ENV", "")).lower() == "production"
    _integrity_results = verify_all_models(strict=_is_prod)
    print(f"[SEC-10] Model integrity check complete ({_format_integrity_summary(_integrity_results)})")
except ModelIntegrityError as _integrity_exc:
    # Hard fail in production — do not serve with compromised models.
    print(f"[SEC-10] FATAL: ML model integrity check failed — {_integrity_exc}")
    raise SystemExit(1) from _integrity_exc
except Exception as _integrity_exc:
    # Missing checksums file or import error — warn but don't block startup.
    print(f"[SEC-10] WARNING: Model integrity check skipped — {_integrity_exc}")


# Optional/demo imports (do not block API startup)
try:
    from app.data_health_analysis import analyze_exercises_data, analyze_nutrition_data, main as run_data_health_analysis
except Exception:
    analyze_exercises_data = None
    analyze_nutrition_data = None
    run_data_health_analysis = None

try:
    from app.feature_pipeline import FeaturePipeline, explain_pipeline_design
except Exception:
    FeaturePipeline = None
    explain_pipeline_design = None

try:
    from app.nutrition_intelligence import NutritionIntelligenceEngine, explain_nutrition_engine_design
except Exception:
    NutritionIntelligenceEngine = None
    explain_nutrition_engine_design = None

try:
    from app.multi_output_xgboost_model import MultiOutputXGBoostModel, create_training_pipeline, production_notes
except Exception:
    MultiOutputXGBoostModel = None
    create_training_pipeline = None
    production_notes = None

try:
    from app.multitarget_nutrition_model import MultiTargetNutritionModel, create_nutrition_training_pipeline
except Exception:
    MultiTargetNutritionModel = None
    create_nutrition_training_pipeline = None

try:
    from app.evaluation_framework import ModelEvaluator, ABTestFramework, example_execution_flow
except Exception:
    ModelEvaluator = None
    ABTestFramework = None
    example_execution_flow = None

try:
    from app.profile_change_detection import ProfileChangeManager, setup_database, example_usage
except Exception:
    ProfileChangeManager = None
    setup_database = None
    example_usage = None

try:
    from app.deterministic_meal_engine import MealEngine, algorithm_logic, pseudocode, optimization_strategy, example_weekly_json, shopping_list_generator_logic
except Exception:
    pass

_gemini_import_error: Optional[Exception] = None
is_gemini_available = None

try:
    from app.gemini_service import get_chatbot_response, is_gemini_available
except Exception as exc:
    get_chatbot_response = None
    is_gemini_available = None
    _gemini_import_error = exc
    print("[WARN] Failed to import app.gemini_service at startup.")
    traceback.print_exc()

# Import new route modules
from app.routes.profile import router as profile_router
from app.routes.food_database import router as food_router
from app.routes.meal_tracking import router as meal_tracking_router
from app.routes.chatbot import router as chatbot_router


# load_dotenv() already called at top — before imports that need env vars

# Configure logging
_request_id_ctx: ContextVar[str] = ContextVar("request_id", default="-")


class _RequestIdFilter(logging.Filter):
    def filter(self, record: logging.LogRecord) -> bool:
        record.request_id = _request_id_ctx.get("-")
        return True


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s [request_id=%(request_id)s] %(name)s: %(message)s",
)
for _handler in logging.getLogger().handlers:
    _handler.addFilter(_RequestIdFilter())

logger = logging.getLogger(__name__)

DEFAULT_WEEKLY_SWAP_LIMIT = 3
MAX_SWAP_HISTORY_ITEMS = 100


def _today_weekday_index() -> int:
    """Return 0=Mon..6=Sun using IST when available."""
    try:
        from zoneinfo import ZoneInfo
        return datetime.now(ZoneInfo("Asia/Kolkata")).weekday()
    except Exception:
        return _utcnow().weekday()


def _current_week_start_date_iso() -> str:
    """Return ISO date for current week's Monday (IST when available)."""
    try:
        from zoneinfo import ZoneInfo
        now = datetime.now(ZoneInfo("Asia/Kolkata"))
    except Exception:
        now = _utcnow()

    monday = now - timedelta(days=now.weekday())
    return monday.date().isoformat()


def _safe_day_index(value: Any) -> Optional[int]:
    try:
        idx = int(value)
        return idx if 0 <= idx <= 6 else None
    except Exception:
        return None


def _is_registration_in_current_week(registration_value: Any) -> bool:
    """Return True when registration_date belongs to current ISO week."""
    if not registration_value:
        return False

    reg_dt = None
    if isinstance(registration_value, datetime):
        reg_dt = registration_value
    else:
        text = str(registration_value).strip()
        if not text:
            return False
        text = text.replace("Z", "+00:00")
        try:
            reg_dt = datetime.fromisoformat(text)
        except Exception:
            try:
                reg_dt = datetime.strptime(text[:10], "%Y-%m-%d")
            except Exception:
                return False

    # BUG-P6 fix: use IST (consistent with _today_weekday_index) instead of UTC
    # so week-boundary classification matches the rest of the codebase.
    try:
        from zoneinfo import ZoneInfo
        now = datetime.now(ZoneInfo("Asia/Kolkata"))
    except Exception:
        now = _utcnow()
    now_year, now_week, _ = now.isocalendar()
    reg_year, reg_week, _ = reg_dt.isocalendar()
    return now_year == reg_year and now_week == reg_week


def _normalize_swap_history(items: Any) -> List[Dict[str, Any]]:
    if not isinstance(items, list):
        return []
    clean_items = [entry for entry in items if isinstance(entry, dict)]
    return clean_items[-MAX_SWAP_HISTORY_ITEMS:]


def _get_swap_limit_state(existing_metadata: Optional[Dict[str, Any]]) -> Dict[str, int]:
    default_state = {
        "max_swaps_per_week": DEFAULT_WEEKLY_SWAP_LIMIT,
        "swaps_used": 0,
        "swaps_remaining": DEFAULT_WEEKLY_SWAP_LIMIT,
    }
    if not isinstance(existing_metadata, dict):
        return default_state

    swap_limits = existing_metadata.get("swap_limits") if isinstance(existing_metadata.get("swap_limits"), dict) else {}
    history = _normalize_swap_history(existing_metadata.get("swap_history"))

    current_week_start = _current_week_start_date_iso()
    # Only count history items from the current week
    current_week_history = [
        entry for entry in history 
        if str(entry.get("timestamp", "")) >= current_week_start
    ]

    try:
        max_swaps = int(swap_limits.get("max_swaps_per_week", DEFAULT_WEEKLY_SWAP_LIMIT))
        max_swaps = max(1, max_swaps)
    except Exception:
        max_swaps = DEFAULT_WEEKLY_SWAP_LIMIT

    swaps_used = len(current_week_history)
    swaps_remaining = max(0, max_swaps - swaps_used)

    return {
        "max_swaps_per_week": max_swaps,
        "swaps_used": swaps_used,
        "swaps_remaining": swaps_remaining,
    }


def _count_current_day_types(weekly_plan: List[Dict[str, Any]]) -> Dict[str, int]:
    rest_days = 0
    workout_days = 0

    for day in weekly_plan or []:
        if not isinstance(day, dict) or day.get("is_placeholder"):
            continue
        day_type = day.get("type")
        if day_type == "rest":
            rest_days += 1
        elif day_type == "workout":
            workout_days += 1

    return {
        "rest_days": rest_days,
        "workout_days": workout_days,
    }


def _count_original_day_types(weekly_plan: List[Dict[str, Any]]) -> Dict[str, int]:
    original_rest = 0
    original_workout = 0

    for day in weekly_plan or []:
        if not isinstance(day, dict) or day.get("is_placeholder"):
            continue

        day_type = day.get("type")
        is_original_rest = day.get("is_original_rest")
        is_original_workout = day.get("is_original_workout")

        if is_original_rest is None:
            is_original_rest = day_type == "rest"
        if is_original_workout is None:
            is_original_workout = day_type == "workout"

        if bool(is_original_rest):
            original_rest += 1
        if bool(is_original_workout):
            original_workout += 1

    return {
        "rest_days": original_rest,
        "workout_days": original_workout,
    }


def _build_week_metadata(
    weekly_plan: List[Dict[str, Any]],
    *,
    registration_day_index: Optional[int] = None,
    is_new_user_week: bool = False,
    existing_metadata: Optional[Dict[str, Any]] = None,
    new_swap_record: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    existing_metadata = existing_metadata if isinstance(existing_metadata, dict) else {}

    # Self-healing: If the plan contains no swapped days, we reset the week's swap history.
    # This prevents users from getting locked out of swaps if their plan was regenerated/reset.
    has_swaps_in_plan = any(day.get("is_swapped") for day in weekly_plan if isinstance(day, dict))
    if not has_swaps_in_plan and not isinstance(new_swap_record, dict):
        swap_history = []
    else:
        swap_history = _normalize_swap_history(existing_metadata.get("swap_history"))
        if isinstance(new_swap_record, dict):
            swap_history.append(new_swap_record)
        swap_history = swap_history[-MAX_SWAP_HISTORY_ITEMS:]

    swap_limits = _get_swap_limit_state(existing_metadata)
    
    current_week_start = _current_week_start_date_iso()
    current_week_history = [
        entry for entry in swap_history 
        if str(entry.get("timestamp", "")) >= current_week_start
    ]
    
    swap_limits["swaps_used"] = len(current_week_history)
    swap_limits["swaps_remaining"] = max(0, swap_limits["max_swaps_per_week"] - swap_limits["swaps_used"])

    if registration_day_index is None:
        registration_day_index = _safe_day_index(existing_metadata.get("user_registration_day"))

    return {
        "week_start_date": _current_week_start_date_iso(),
        "user_registration_day": registration_day_index,
        "is_new_user_week": bool(is_new_user_week),
        "swap_history": swap_history,
        "swap_limits": swap_limits,
        "original_counts": _count_original_day_types(weekly_plan),
        "current_counts": _count_current_day_types(weekly_plan),
        "updated_at": _utcnow().isoformat(),
    }


def _build_workout_profile_from_user(user_doc: Dict[str, Any]) -> Dict[str, Any]:
    """Build engine-compatible workout profile payload from Mongo user document."""
    return {
        "user_id": str(user_doc.get("_id")),
        "age": user_doc.get("age", 25),
        "weight": user_doc.get("weight", 70),
        "height": user_doc.get("height", 175),
        "gender": user_doc.get("gender", "Male"),
        "goal": user_doc.get("goal", "Muscle Gain"),
        "experience": user_doc.get("experience", "Beginner"),
        "days_per_week": user_doc.get("days_per_week", 4),
        "equipment": user_doc.get("equipment") or ["Dumbbell"],
        "body_issues": user_doc.get("body_issues") or [],
        "streak": user_doc.get("streak", 0),
        "consistency": user_doc.get("consistency", 0.7),
        "firstWorkoutDay": _safe_day_index(user_doc.get("firstWorkoutDay")),
        "registrationDate": user_doc.get("registrationDate"),
        "is_new_user_week": _is_registration_in_current_week(user_doc.get("registrationDate")),
    }


async def _find_user_by_id(user_id: str) -> Optional[Dict[str, Any]]:
    """Fetch a user document by ID from MongoDB.

    SEC-11 fix: Reject any user_id that is not a valid ObjectId string BEFORE
    making any database query. This eliminates the unsafe fallback path where
    an arbitrary string could be passed as `_id` to MongoDB.
    """
    if not user_id or not ObjectId.is_valid(user_id):
        return None
    db = get_database()
    return await db.users.find_one({"_id": ObjectId(user_id)})


async def _find_user_workouts_by_id(user_id: str, limit: int = 50) -> Optional[Dict[str, Any]]:
    """Fetch user document with sliced workouts list to avoid performance bottlenecks."""
    if not user_id or not ObjectId.is_valid(user_id):
        return None
    db = get_database()
    return await db.users.find_one(
        {"_id": ObjectId(user_id)},
        {"workouts": {"$slice": -limit}}
    )


async def _find_user_by_email(email: str) -> Optional[Dict[str, Any]]:
    email = str(email or "").strip().lower()
    if not email:
        return None

    db = get_database()
    users = db.users
    # Bug #12 fixed: use an exact case-insensitive match with collation instead
    # of a $regex, which is slower on large collections and susceptible to ReDoS.
    try:
        return await users.find_one(
            {"email": email},
            collation={"locale": "en", "strength": 2}  # strength=2 → case+accent insensitive
        )
    except Exception as exc:
        # Some Mongo deployments do not support collation in this context.
        logger.warning("Email lookup collation unsupported, falling back to exact match: %s", exc)
        return await users.find_one({"email": email})



async def _persist_workout_plan_and_metadata(
    user_filter: Dict[str, Any],
    weekly_plan: List[Dict[str, Any]],
    week_metadata: Dict[str, Any],
) -> None:
    db = get_database()
    users = db.users
    await users.update_one(
        user_filter,
        {
            "$set": {
                "workoutPlan": weekly_plan,
                "workoutWeekMetadata": week_metadata,
                "workoutPlanGeneratedAt": _utcnow(),
            }
        },
        upsert=False,
    )


async def _append_swap_audit(user_id: Any, week_metadata: Dict[str, Any], swap_record: Dict[str, Any]) -> None:
    """Store swap audit trail in dedicated collection (best-effort)."""
    try:
        db = get_database()
        await db.swap_history.insert_one(
            {
                "user_id": user_id,
                "week_start_date": week_metadata.get("week_start_date"),
                "swap_type": swap_record.get("direction"),
                "from_day_index": swap_record.get("from_day"),
                "to_day_index": swap_record.get("to_day"),
                "workout_focus": swap_record.get("workout_focus"),
                "performed_at": swap_record.get("timestamp") or _utcnow().isoformat(),
                "created_at": _utcnow(),
            }
        )
    except Exception as audit_err:
        logger.warning("Unable to persist swap audit log: %s", audit_err)


async def _load_or_generate_user_weekly_plan(user_doc: Dict[str, Any]) -> Dict[str, Any]:
    """Load user plan from DB; generate and persist if missing/invalid or stale week."""
    weekly_plan = user_doc.get("workoutPlan")
    has_valid_plan = isinstance(weekly_plan, list) and len(weekly_plan) == 7

    # Check if the saved plan belongs to a past week
    saved_metadata = user_doc.get("workoutWeekMetadata") or {}
    saved_week_start = saved_metadata.get("week_start_date")
    current_week_start = _current_week_start_date_iso()
    is_stale_week = bool(saved_week_start and saved_week_start != current_week_start)

    registration_day_index = _safe_day_index(user_doc.get("firstWorkoutDay"))
    is_new_user_week = _is_registration_in_current_week(user_doc.get("registrationDate"))

    if not has_valid_plan or is_stale_week:
        engine = _ensure_workout_engine_ready()
        profile = _build_workout_profile_from_user(user_doc)

        # If it's a rolled-over week, ensure is_new_user_week is False
        if is_stale_week:
            profile['is_new_user_week'] = False
            is_new_user_week = False

        # Check in-memory plan cache before running ML generation.
        # On a cache hit we skip generate_weekly_plan() entirely — page navigation
        # becomes instant for the same profile within the same week.
        plan_cache = getattr(engine, "_plan_cache", None)
        cached_plan = plan_cache.get(profile) if plan_cache else None
        if cached_plan:
            logger.info("[PlanCache] HIT in _load_or_generate — skipping ML generation")
            weekly_plan = cached_plan
        else:
            weekly_plan = engine.generate_weekly_plan(profile)
            # Cache the freshly generated plan for subsequent requests
            if plan_cache and weekly_plan:
                try:
                    plan_cache.set(profile, weekly_plan)
                except Exception as cache_set_err:
                    logger.warning("Could not store plan in cache: %s", cache_set_err)

        has_valid_plan = True

        # Recalculate nutrition plan to align with the new workout volume/intensity
        # (only on a real generation, not a cache hit — avoids unnecessary DB writes)
        if not cached_plan:
            try:
                from app.meal_engine import get_meal_engine
                meal_engine = get_meal_engine()

                # Use the user_doc directly since meal_engine expects the full profile
                weekly_schedule = weekly_plan.get("schedule", []) if isinstance(weekly_plan, dict) else []
                meal_plan = meal_engine.generate_meal_plan(user_doc, weekly_workout_plan=weekly_schedule)
                db_instance = get_database()
                await db_instance.users.update_one(
                    {"_id": user_doc["_id"]},
                    {"$set": {"latestNutritionPlan": meal_plan}}
                )
                logger.info("Successfully rolled forward nutrition plan with workout plan.")
            except Exception as meal_err:
                logger.warning("Could not regenerate nutrition plan during week rollover: %s", meal_err)

    week_metadata = _build_week_metadata(
        weekly_plan,
        registration_day_index=registration_day_index,
        is_new_user_week=is_new_user_week,
        existing_metadata=user_doc.get("workoutWeekMetadata"),
    )

    # Bug #32 fixed: compare without the updated_at timestamp so that identical
    # plans aren't unnecessarily re-persisted on every API call.
    def _meta_comparable(m: dict) -> dict:
        return {k: v for k, v in (m or {}).items() if k != "updated_at"}

    needs_persist = (not has_valid_plan) or is_stale_week or (
        _meta_comparable(user_doc.get("workoutWeekMetadata")) != _meta_comparable(week_metadata)
    )
    if needs_persist:
        await _persist_workout_plan_and_metadata({"_id": user_doc.get("_id")}, weekly_plan, week_metadata)


    return {
        "plan": weekly_plan,
        "week_metadata": week_metadata,
        "user_context": {
            "registration_day": registration_day_index,
            "is_new_user": bool(is_new_user_week),
            "today_index": _today_weekday_index(),
        },
    }


async def _persist_swap_result_for_email(
    email: str,
    swapped_plan: List[Dict[str, Any]],
    swap_record: Dict[str, Any],
    existing_user: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """Persist swapped plan and week metadata to users collection + audit log."""
    user_doc = existing_user or await _find_user_by_email(email)

    if not user_doc:
        return _build_week_metadata(swapped_plan, new_swap_record=swap_record)

    registration_day_index = _safe_day_index(user_doc.get("firstWorkoutDay"))
    is_new_user_week = _is_registration_in_current_week(user_doc.get("registrationDate"))

    week_metadata = _build_week_metadata(
        swapped_plan,
        registration_day_index=registration_day_index,
        is_new_user_week=is_new_user_week,
        existing_metadata=user_doc.get("workoutWeekMetadata"),
        new_swap_record=swap_record,
    )

    await _persist_workout_plan_and_metadata({"_id": user_doc.get("_id")}, swapped_plan, week_metadata)
    await _append_swap_audit(user_doc.get("_id"), week_metadata, swap_record)
    return week_metadata


def _ensure_chatbot_module_loaded() -> bool:
    """Try to (re)load chatbot module if startup import failed."""
    global get_chatbot_response, is_gemini_available, _gemini_import_error

    if get_chatbot_response is not None:
        return True

    try:
        from app.gemini_service import get_chatbot_response as chatbot_fn, is_gemini_available as gemini_probe
        get_chatbot_response = chatbot_fn
        is_gemini_available = gemini_probe
        _gemini_import_error = None
        logger.info("Gemini chatbot module loaded lazily.")
        return True
    except Exception as exc:
        _gemini_import_error = exc
        logger.error("Gemini chatbot module import failed on-demand: %s", exc)
        logger.debug("Gemini import traceback:\n%s", traceback.format_exc())
        return False

from pydantic import field_validator, model_validator


def _model_to_dict(model_obj: BaseModel) -> Dict[str, Any]:
    if hasattr(model_obj, "model_dump"):
        return model_obj.model_dump(exclude_none=True)
    return model_obj.dict(exclude_none=True)


_SENSITIVE_LOG_FIELDS = {
    "name",
    "email",
    "weight",
    "height",
    "age",
    "allergies",
    "body_issues",
    "equipment",
    "dietary_restrictions",
    "weekly_workout_plan",
}


def _redact_sensitive_fields(payload: Any) -> Any:
    if not isinstance(payload, dict):
        return payload

    redacted: Dict[str, Any] = {}
    for key, value in payload.items():
        if key in _SENSITIVE_LOG_FIELDS:
            if isinstance(value, list):
                redacted[key] = f"[redacted list: {len(value)} items]"
            elif isinstance(value, dict):
                redacted[key] = "[redacted object]"
            else:
                redacted[key] = "[redacted]"
        else:
            redacted[key] = value
    return redacted


def _validate_required_env() -> None:
    required = ["MONGO_URI", "JWT_SECRET"]
    missing = [k for k in required if not os.getenv(k)]
    if missing:
        raise RuntimeError(f"Missing required environment variables: {', '.join(missing)}")

    if os.getenv("NODE_ENV", os.getenv("PYTHON_ENV", "")).lower() != "test":
        jwt_secret = str(os.getenv("JWT_SECRET", "")).strip().lower()
        if (
            not jwt_secret
            or "change-me" in jwt_secret
            or "your-" in jwt_secret
            or "placeholder" in jwt_secret
        ):
            raise RuntimeError("JWT_SECRET uses a placeholder/default value; set a strong secret before startup")


from app.core.responses import api_success as _api_success



from app.core.auth import (
    extract_auth_token_from_request as _extract_auth_token_from_request,
    require_user_id_from_token as _require_user_id_from_token,
    require_user_id_from_request as _require_user_id_from_request,
)



_TRUST_PROXY = str(os.getenv("TRUST_PROXY", "0")).strip() == "1"


def _extract_client_ip_for_limits(request: Request) -> str:
    """Resolve client IP for rate-limiting with conservative proxy trust.

    Only trust forwarding headers when TRUST_PROXY=1 is explicitly enabled.
    """
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


_validate_required_env()

# FastAPI app
app = FastAPI(title="Elevate Fitness API", version="1.0.0")

# ── SEC-8: In-process rate limiter for CPU-heavy ML endpoints ─────────────────
# Uses a token-bucket algorithm per user/IP key.
# Keeps memory bounded: evicts keys that haven't been seen in 10 minutes.
class _TokenBucket:
    """Thread-safe token bucket for a single client key."""
    __slots__ = ("tokens", "last_refill", "capacity", "refill_rate")

    def __init__(self, capacity: int, refill_rate: float):
        self.capacity = capacity          # max burst size
        self.refill_rate = refill_rate    # tokens added per second
        self.tokens = float(capacity)
        self.last_refill = time.monotonic()

    def consume(self) -> bool:
        now = time.monotonic()
        elapsed = now - self.last_refill
        self.tokens = min(self.capacity, self.tokens + elapsed * self.refill_rate)
        self.last_refill = now
        if self.tokens >= 1:
            self.tokens -= 1
            return True
        return False


class _RateLimiter:
    """
    Per-key token-bucket rate limiter.

    Args:
        requests_per_minute: sustained allowed rate (averaged over 60 s).
        burst: maximum allowed burst (defaults to requests_per_minute).
    """

    def __init__(self, requests_per_minute: int = 10, burst: int = None):
        self._rpm = requests_per_minute
        self._burst = burst or requests_per_minute
        self._buckets: dict = {}
        self._lock = threading.Lock()
        self._last_eviction = time.monotonic()

    def _evict_stale(self) -> None:
        """Remove buckets inactive for >10 minutes to prevent unbounded growth."""
        now = time.monotonic()
        if now - self._last_eviction < 600:
            return
        cutoff = now - 600
        stale_keys = [k for k, b in self._buckets.items() if b.last_refill < cutoff]
        for k in stale_keys:
            del self._buckets[k]
        self._last_eviction = now

    def is_allowed(self, key: str) -> bool:
        with self._lock:
            self._evict_stale()
            if key not in self._buckets:
                self._buckets[key] = _TokenBucket(
                    capacity=self._burst,
                    refill_rate=self._rpm / 60.0,
                )
            return self._buckets[key].consume()


# 10 requests/min per user — enough for normal use; blocks floods on heavy ML routes.
_WORKOUT_RATE_LIMITER = _RateLimiter(requests_per_minute=10)
_NUTRITION_RATE_LIMITER = _RateLimiter(requests_per_minute=10)
_PLAN_RATE_LIMITER = _RateLimiter(requests_per_minute=6)
_DATA_HEALTH_RATE_LIMITER = _RateLimiter(requests_per_minute=2)


def _rate_limit_key(request: Request, x_auth_token: Optional[str] = None) -> str:
    """Return a stable key: JWT sub-claim if present, else client IP."""
    token = _extract_auth_token_from_request(request, x_auth_token)
    if token:
        try:
            payload = jwt.decode(
                token,
                os.getenv("JWT_SECRET"),
                algorithms=["HS256"],
            )
            user_id = payload.get("user", {}).get("id") or payload.get("sub") or payload.get("id")
            if user_id:
                return f"user:{user_id}"
        except Exception:
            pass
    # Fallback: client IP (forwarding headers are trusted only when configured)
    ip = _extract_client_ip_for_limits(request)
    return f"ip:{ip}"
# ─────────────────────────────────────────────────────────────────────────────



@app.middleware("http")
async def request_context_middleware(request: Request, call_next):
    request_id = request.headers.get("x-request-id") or str(uuid.uuid4())
    token = _request_id_ctx.set(request_id)
    started_at = time.perf_counter()
    status_code = 500

    try:
        response = await call_next(request)
        status_code = response.status_code
        response.headers["x-request-id"] = request_id
        return response
    except Exception as exc:
        # Log unhandled exceptions that would otherwise silently return 500
        elapsed_ms = (time.perf_counter() - started_at) * 1000.0
        logger.error(
            "[%s] UNHANDLED %s %s after %.2f ms: %s\n%s",
            request_id, request.method, request.url.path, elapsed_ms,
            exc, traceback.format_exc(),
        )
        raise
    finally:
        elapsed_ms = (time.perf_counter() - started_at) * 1000.0
        logger.info("%s %s -> %s (%.2f ms)", request.method, request.url.path, status_code, elapsed_ms)
        _request_id_ctx.reset(token)

# ===== PYDANTIC MODELS =====



class NutritionRequest(BaseModel):
    """Validated nutrition request model"""
    age: Optional[int] = Field(25, ge=1, le=120)
    weight: Optional[float] = Field(70, ge=20, le=500)
    height: Optional[float] = Field(175, ge=50, le=300)
    gender: Optional[str] = Field("Male")
    goal: Optional[str] = Field("Maintenance")
    dietary_preference: Optional[str] = Field("Non-Veg")
    allergies: Optional[List[str]] = Field(default_factory=list)
    activity_level: Optional[str] = Field("Moderate")
    workout_intensity: Optional[str] = Field("moderate")
    weekly_workout_plan: Optional[List[Dict[str, Any]]] = Field(default_factory=list)
    
    @field_validator('goal')
    @classmethod
    def validate_goal(cls, v):
        valid_goals = ['Weight Loss', 'Fat Loss', 'Muscle Gain', 'Strength', 'Endurance', 'Maintenance']
        return v if v in valid_goals else 'Maintenance'
    
    @field_validator('workout_intensity')
    @classmethod
    def validate_intensity(cls, v):
        valid = ['rest', 'light', 'moderate', 'hard', 'very_hard']
        return v if v in valid else 'moderate'


class WorkoutProfileRequest(BaseModel):
    user_id: Optional[str] = None
    age: Optional[int] = Field(25, ge=1, le=120)
    weight: Optional[float] = Field(70, ge=20, le=500)
    height: Optional[float] = Field(175, ge=50, le=300)
    gender: Optional[str] = Field("Male")
    goal: Optional[str] = Field("Muscle Gain")
    experience: Optional[str] = Field("Beginner")
    days_per_week: Optional[int] = Field(4, ge=1, le=7)
    equipment: Optional[List[str]] = Field(default_factory=lambda: ["Dumbbell"])
    body_issues: Optional[List[str]] = Field(default_factory=list)
    streak: Optional[int] = Field(0, ge=0)
    consistency: Optional[float] = Field(0.7, ge=0, le=1)
    firstWorkoutDay: Optional[int] = Field(None, ge=0, le=6)
    registrationDate: Optional[str] = None
    is_new_user_week: Optional[bool] = False

    @field_validator('equipment')
    @classmethod
    def _normalize_empty_equipment(cls, v):
        """Bug #70 fixed: replace empty equipment list with Bodyweight default.
        An empty list causes the workout engine to generate no feasible exercises."""
        if not v:  # None or []
            return ["Bodyweight"]
        return v


class PlanProfileUpdateRequest(BaseModel):
    name: Optional[str] = None
    age: Optional[int] = Field(None, ge=1, le=120)
    weight: Optional[float] = Field(None, ge=20, le=500)
    height: Optional[float] = Field(None, ge=50, le=300)
    gender: Optional[str] = None
    goal: Optional[str] = None
    experience: Optional[str] = None
    equipment: Optional[List[str]] = None
    body_issues: Optional[List[str]] = None
    dietary_preference: Optional[str] = None
    allergies: Optional[List[str]] = None
    days_per_week: Optional[int] = Field(None, ge=1, le=7)
    session_time: Optional[int] = Field(None, ge=10, le=180)
    meal_frequency: Optional[int] = Field(None, ge=1, le=10)
    cooking_time: Optional[str] = None
    cuisine_preference: Optional[str] = None
    dietary_restrictions: Optional[str] = None

    @model_validator(mode='after')
    def check_bmi_plausibility(self):
        # Only validate if both weight and height are provided
        if self.weight is not None and self.height is not None:
            # height is in cm
            height_m = self.height / 100.0
            if height_m > 0:
                bmi = self.weight / (height_m * height_m)
                if bmi < 10 or bmi > 100:
                    raise ValueError(f"Calculated BMI ({bmi:.1f}) is highly implausible. Please check weight and height.")
        return self

def generate_fallback_meal_plan(user_profile: Dict) -> Dict:
    """Generate safe fallback meal plan when engine fails.
    
    Bug #74 fixed: schema now matches the real engine output — every field that
    callers access (intensity_focus, fiber per meal) is present.
    """
    base_calories = 2000
    
    # Adjust by goal
    goal = user_profile.get('goal', 'Maintenance')
    if goal in ['Weight Loss', 'Fat Loss']:
        base_calories = 1600
    elif goal == 'Muscle Gain':
        base_calories = 2800
    
    fallback_meals = [
        {
            'meal_type': 'breakfast',
            'name': 'Oatmeal with Protein',
            'calories': 400,
            'protein': 30,
            'carbs': 50,
            'fat': 10,
            'fiber': 6,  # Bug #74: fiber now included to match validated_meal schema
        },
        {
            'meal_type': 'lunch',
            'name': 'Grilled Chicken with Rice',
            'calories': 600,
            'protein': 45,
            'carbs': 70,
            'fat': 15,
            'fiber': 4,
        },
        {
            'meal_type': 'dinner',
            'name': 'Salmon with Vegetables',
            'calories': 550,
            'protein': 40,
            'carbs': 40,
            'fat': 25,
            'fiber': 8,
        },
        {
            'meal_type': 'snack',
            'name': 'Greek Yogurt with Berries',
            'calories': 200,
            'protein': 20,
            'carbs': 25,
            'fat': 5,
            'fiber': 3,
        }
    ]

    weekly_plan = {}
    for day_name in ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]:
        per_day = {"breakfast": [], "lunch": [], "dinner": [], "snack": []}
        for item in fallback_meals:
            per_day[item["meal_type"]].append({
                "name": item["name"],
                "calories": item["calories"],
                "protein": item["protein"],
                "carbs": item["carbs"],
                "fat": item["fat"],
                "swap_group": item["meal_type"],
            })
        weekly_plan[day_name] = per_day

    daily_target = {
        'calories': base_calories,
        'protein': 150,
        'carbs': 200,
        'fat': 60
    }

    return {
        'date': datetime.now().strftime('%Y-%m-%d'),
        'daily_target': daily_target,
        'daily_targets_by_day': {day: {**daily_target, 'workout_intensity': 'moderate'} for day in weekly_plan.keys()},
        'weekly_plan': weekly_plan,
        # Bug #74: added intensity_focus so callers don't silently get the default
        'intensity_focus': 'maintenance',
        'meals': fallback_meals,
        'note': 'Fallback meal plan - engine unavailable',
        'workout_intensity': 'moderate'
    }


# CORS middleware
# CRITICAL: Cannot use "*" with allow_credentials=True
_raw_cors = os.getenv("CORS_ORIGINS", "")
if not _raw_cors.strip():
    raise Exception(
        f"CORS_ORIGINS environment variable is missing or empty. "
        f"Set it in {_DOTENV_PATH} (or your deployment environment)."
    )

cors_origins = [o.strip() for o in _raw_cors.split(",") if o.strip()]

# DEV safety: ensure common Vite fallback ports are always allowed in non-production.
# Vite uses strictPort: false, so it may land on 5174, 5175, etc. when 5173 is busy.
_is_production = os.getenv("PYTHON_ENV", os.getenv("NODE_ENV", "")).lower() == "production"
if not _is_production:
    for _dev_origin in ["http://localhost:5173", "http://localhost:5174", "http://localhost:5175", "http://localhost:3000"]:
        if _dev_origin not in cors_origins:
            cors_origins.append(_dev_origin)
cors_methods = [
    m.strip().upper()
    for m in os.getenv("CORS_METHODS", "GET,POST,PUT,PATCH,DELETE,OPTIONS").split(",")
    if m.strip()
]
cors_headers = [
    h.strip()
    for h in os.getenv("CORS_HEADERS", "Authorization,Content-Type,X-Auth-Token,Accept").split(",")
    if h.strip()
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,  # Allow cookies/auth headers
    allow_methods=cors_methods,
    allow_headers=cors_headers,
)
print(f"[CORS] Allowed origins: {cors_origins}")

# Initialize engines on startup
workout_engine = None
meal_engine = None
_model_init_lock = threading.Lock()
_model_warmup_lock = threading.Lock()
_model_warmup_in_progress = False
_model_warmup_started_at: Optional[str] = None
_model_warmup_completed_at: Optional[str] = None
_model_status: Dict[str, Dict[str, Any]] = {
    "workout": {
        "state": "not_started",
        "ready": False,
        "last_error": None,
        "last_loaded_at": None,
        "load_time_ms": None,
    },
    "meal": {
        "state": "not_started",
        "ready": False,
        "last_error": None,
        "last_loaded_at": None,
        "load_time_ms": None,
    },
}


def _set_model_status(model_name: str, *, state: str, ready: bool,
                      last_error: Optional[str] = None,
                      load_time_ms: Optional[float] = None) -> None:
    entry = _model_status[model_name]
    entry["state"] = state
    entry["ready"] = ready
    entry["last_error"] = last_error
    if load_time_ms is not None:
        entry["load_time_ms"] = round(load_time_ms, 2)
    if ready:
        entry["last_loaded_at"] = _utcnow().isoformat()


def _initialize_workout_engine() -> Any:
    global workout_engine
    if workout_engine is not None:
        return workout_engine

    with _model_init_lock:
        if workout_engine is not None:
            return workout_engine

        started = time.perf_counter()
        _set_model_status("workout", state="loading", ready=False, last_error=None)
        try:
            workout_engine = get_workout_engine()
            elapsed_ms = (time.perf_counter() - started) * 1000.0
            _set_model_status("workout", state="ready", ready=True, load_time_ms=elapsed_ms)
            logger.info("WorkoutEngine initialized in %.2f ms", elapsed_ms)
            return workout_engine
        except Exception as exc:
            elapsed_ms = (time.perf_counter() - started) * 1000.0
            workout_engine = None
            _set_model_status(
                "workout",
                state="error",
                ready=False,
                last_error=f"{type(exc).__name__}: {exc}",
                load_time_ms=elapsed_ms,
            )
            logger.exception("WorkoutEngine initialization failed")
            return None


def _initialize_meal_engine() -> Any:
    global meal_engine
    if meal_engine is not None:
        return meal_engine

    with _model_init_lock:
        if meal_engine is not None:
            return meal_engine

        started = time.perf_counter()
        _set_model_status("meal", state="loading", ready=False, last_error=None)
        try:
            meal_engine = get_meal_engine()
            elapsed_ms = (time.perf_counter() - started) * 1000.0
            _set_model_status("meal", state="ready", ready=True, load_time_ms=elapsed_ms)
            logger.info("MealEngine initialized in %.2f ms", elapsed_ms)
            return meal_engine
        except Exception as exc:
            elapsed_ms = (time.perf_counter() - started) * 1000.0
            meal_engine = None
            _set_model_status(
                "meal",
                state="error",
                ready=False,
                last_error=f"{type(exc).__name__}: {exc}",
                load_time_ms=elapsed_ms,
            )
            logger.exception("MealEngine initialization failed")
            return None


def _warm_models() -> None:
    global _model_warmup_in_progress, _model_warmup_started_at, _model_warmup_completed_at

    with _model_warmup_lock:
        if _model_warmup_in_progress:
            return
        _model_warmup_in_progress = True
        _model_warmup_started_at = _utcnow().isoformat()

    try:
        _initialize_workout_engine()
        _initialize_meal_engine()
    finally:
        with _model_warmup_lock:
            _model_warmup_in_progress = False
            _model_warmup_completed_at = _utcnow().isoformat()


def _trigger_model_warmup(background: bool = True) -> Dict[str, Any]:
    if background:
        thread = threading.Thread(target=_warm_models, daemon=True, name="model-warmup")
        thread.start()
        return {"started": True, "background": True}

    _warm_models()
    return {"started": True, "background": False}


def _get_model_status_payload() -> Dict[str, Any]:
    return {
        "warmup": {
            "in_progress": _model_warmup_in_progress,
            "started_at": _model_warmup_started_at,
            "completed_at": _model_warmup_completed_at,
        },
        "models": {
            "workout": dict(_model_status["workout"]),
            "meal": dict(_model_status["meal"]),
        },
    }


def _ensure_workout_engine_ready() -> Any:
    engine = workout_engine or _initialize_workout_engine()
    if engine is None:
        detail = _model_status["workout"].get("last_error") or "Workout engine unavailable"
        raise HTTPException(status_code=503, detail=f"Workout engine unavailable: {detail}")
    return engine


def _ensure_meal_engine_ready() -> Any:
    engine = meal_engine or _initialize_meal_engine()
    if engine is None:
        detail = _model_status["meal"].get("last_error") or "Meal engine unavailable"
        raise HTTPException(status_code=503, detail=f"Meal engine unavailable: {detail}")
    return engine


async def _check_database_health() -> Dict[str, Any]:
    try:
        db = get_database()
        await db.command("ping")
        return {"ok": True}
    except Exception as exc:
        return {"ok": False, "error": f"{type(exc).__name__}: {exc}"}


@app.on_event("startup")
async def startup_event():
    print("\n" + "=" * 60)
    print("FastAPI Server Starting...")
    print("=" * 60)

    # Connect to MongoDB
    from app.db import connect_to_mongo

    try:
        await connect_to_mongo()
        print("MongoDB connected successfully")
    except Exception as e:
        print(f"MongoDB connection error: {e}")
        import traceback

        traceback.print_exc()

    warmup_info = _trigger_model_warmup(background=True)
    print(f"Model warmup started (background={warmup_info['background']})")

    print("=" * 60)
    print(f"Server ready at http://localhost:{os.getenv('PORT', '8000')}")
    print("FastAPI startup successful")
    print("=" * 60 + "\n")


@app.on_event("shutdown")
async def shutdown_event():
    from app.db import close_mongo_connection
    await close_mongo_connection()

# Include routers
from app.routes.profile import router as profile_router
from app.routes.food_database import router as food_router
from app.routes.meal_tracking import router as meal_tracking_router
from app.routes.chatbot import router as chatbot_router
from app.routes.meal_plan import router as meal_plan_router

app.include_router(profile_router)  # Profile routes (/profile/...)
app.include_router(food_router)  # Food database (/food-database)
app.include_router(meal_tracking_router)  # Meal tracking routes (/api/meals/...)
app.include_router(chatbot_router)  # Chatbot routes (/api/chat)
app.include_router(meal_plan_router)  # Meal plan routes (/api/meal-plan)


# ==========================================
# HEALTH & STATUS
# ==========================================


@app.get("/")
async def root():
    return {"message": " Elevate Fitness API", "version": "1.0.0", "status": "running"}


@app.get("/health")
async def health_check():
    status_payload = _get_model_status_payload()
    database = await _check_database_health()
    overall_status = "healthy" if database.get("ok") else "degraded"
    return {
        "status": overall_status,
        "service": "elevate_fitness",
        "timestamp": _utcnow().isoformat(),
        "engines": {
            "workout": status_payload["models"]["workout"]["ready"],
            "meal": status_payload["models"]["meal"]["ready"],
        },
        "dependencies": {
            "mongo": database,
        },
        "model_warmup": status_payload["warmup"],
    }


@app.get("/debug/status")
async def debug_status():
    """Diagnostics endpoint for verifying backend component health."""
    opencv_ok = False
    try:
        from app.pose_tracker import _ensure_cv2
        opencv_ok = _ensure_cv2()
    except Exception:
        pass

    mediapipe_ok = False
    try:
        from app.pose_tracker import AI_AVAILABLE
        mediapipe_ok = AI_AVAILABLE
    except Exception:
        pass

    detector_factory_ok = False
    mapping_loaded = False
    try:
        from app.detectors import DetectorFactory
        DetectorFactory.load_configs()
        detector_factory_ok = True
        mapping_loaded = bool(DetectorFactory._exercise_mapping)
    except Exception:
        pass

    return {
        "fastapi_running": True,
        "opencv_available": opencv_ok,
        "mediapipe_available": mediapipe_ok,
        "detector_factory_loaded": detector_factory_ok,
        "exercise_mapping_loaded": mapping_loaded,
        "workout_engine_ready": _model_status.get("workout", {}).get("ready", False),
        "meal_engine_ready": _model_status.get("meal", {}).get("ready", False),
        "timestamp": _utcnow().isoformat(),
    }


@app.get("/api/models/status")
async def models_status():
    payload = _get_model_status_payload()
    return _api_success("Model status fetched", data=payload, models=payload["models"], warmup=payload["warmup"])


@app.post("/api/models/warmup")
async def warmup_models(
    request: Request,
    background: bool = Query(True),
    x_auth_token: Optional[str] = Header(None, alias="x-auth-token"),
):
    _require_user_id_from_request(request, x_auth_token)
    info = _trigger_model_warmup(background=background)
    payload = _get_model_status_payload()
    return _api_success(
        "Model warmup triggered",
        data={"trigger": info, "status": payload},
        trigger=info,
        models=payload["models"],
        warmup=payload["warmup"],
    )


@app.get("/data-health-analysis")
async def data_health_analysis(
    request: Request,
    x_auth_token: Optional[str] = Header(None, alias="x-auth-token"),
):
    """Run comprehensive data health analysis on exercises and nutrition datasets"""
    try:
        _require_user_id_from_request(request, x_auth_token)
        rl_key = _rate_limit_key(request, x_auth_token)
        if not _DATA_HEALTH_RATE_LIMITER.is_allowed(rl_key):
            raise HTTPException(
                status_code=429,
                detail="Too many data health analysis requests. Please wait and try again.",
            )

        print(f"\n{'='*60}")
        print(f" DATA HEALTH ANALYSIS REQUESTED")
        print(f"{'='*60}")
        
        # Run the data health analysis
        if run_data_health_analysis is None:
            raise HTTPException(status_code=503, detail="Data health analysis module unavailable")
        run_data_health_analysis()
        
        print(f" Data health analysis completed successfully")
        print(f"{'='*60}\n")
        
        return {
            "success": True,
            "message": "Data health analysis completed successfully",
            "timestamp": _utcnow().isoformat(),
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"\n{'='*60}")
        print(f" CRITICAL ERROR in /data-health-analysis endpoint")
        print(f"{'='*60}")
        print(f"Error type: {type(e).__name__}")
        print(f"Error message: {str(e)}")

        import traceback

        print(f"\nFull traceback:")
        traceback.print_exc()
        print(f"{'='*60}\n")

        raise HTTPException(status_code=500, detail="Internal server error")


@app.get("/feature-pipeline-design")
async def feature_pipeline_design(
    request: Request,
    x_auth_token: Optional[str] = Header(None, alias="x-auth-token"),
):
    """Return the feature pipeline design documentation"""
    try:
        _require_user_id_from_request(request, x_auth_token)
        print(f"\n{'='*60}")
        print(f"  FEATURE PIPELINE DESIGN REQUESTED")
        print(f"{'='*60}")
        
        # Run the pipeline design explanation
        if explain_pipeline_design is None:
            raise HTTPException(status_code=503, detail="Feature pipeline module unavailable")
        explanation = []
        # Capture the print statements from explain_pipeline_design
        import io
        import sys
        from contextlib import redirect_stdout
        
        f = io.StringIO()
        with redirect_stdout(f):
            explain_pipeline_design()
        explanation = f.getvalue()
        
        print(f" Feature pipeline design retrieved successfully")
        print(f"{'='*60}\n")
        
        return {
            "success": True,
            "message": "Feature pipeline design retrieved successfully",
            "design_documentation": explanation,
            "timestamp": _utcnow().isoformat(),
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"\n{'='*60}")
        print(f" CRITICAL ERROR in /feature-pipeline-design endpoint")
        print(f"{'='*60}")
        print(f"Error type: {type(e).__name__}")
        print(f"Error message: {str(e)}")

        import traceback

        print(f"\nFull traceback:")
        traceback.print_exc()
        print(f"{'='*60}\n")

        raise HTTPException(status_code=500, detail="Internal server error")


@app.get("/nutrition-intelligence-design")
async def nutrition_intelligence_design(
    request: Request,
    x_auth_token: Optional[str] = Header(None, alias="x-auth-token"),
):
    """Return the nutrition intelligence engine design documentation"""
    try:
        _require_user_id_from_request(request, x_auth_token)
        print(f"\n{'='*60}")
        print(f" NUTRITION INTELLIGENCE DESIGN REQUESTED")
        print(f"{'='*60}")
        
        # Run the nutrition engine design explanation
        if explain_nutrition_engine_design is None:
            raise HTTPException(status_code=503, detail="Nutrition intelligence module unavailable")
        explanation = []
        # Capture the print statements from explain_nutrition_engine_design
        import io
        import sys
        from contextlib import redirect_stdout
        
        f = io.StringIO()
        with redirect_stdout(f):
            explain_nutrition_engine_design()
        explanation = f.getvalue()
        
        print(f" Nutrition intelligence design retrieved successfully")
        print(f"{'='*60}\n")
        
        return {
            "success": True,
            "message": "Nutrition intelligence design retrieved successfully",
            "design_documentation": explanation,
            "timestamp": _utcnow().isoformat(),
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"\n{'='*60}")
        print(f" CRITICAL ERROR in /nutrition-intelligence-design endpoint")
        print(f"{'='*60}")
        print(f"Error type: {type(e).__name__}")
        print(f"Error message: {str(e)}")

        import traceback

        print(f"\nFull traceback:")
        traceback.print_exc()
        print(f"{'='*60}\n")

        raise HTTPException(status_code=500, detail="Internal server error")


@app.get("/multi-output-model-training")
async def multi_output_model_training(
    request: Request,
    x_auth_token: Optional[str] = Header(None, alias="x-auth-token"),
):
    """Train and evaluate the multi-output XGBoost model"""
    try:
        _require_user_id_from_request(request, x_auth_token)
        print(f"\n{'='*60}")
        print(f" MULTI-OUTPUT MODEL TRAINING REQUESTED")
        print(f"{'='*60}")
        
        # Run the training pipeline
        if create_training_pipeline is None:
            raise HTTPException(status_code=503, detail="Multi-output training pipeline unavailable")
        model, training_results, test_evaluation = create_training_pipeline()
        
        print(f" Multi-output model training completed successfully")
        print(f"{'='*60}\n")
        
        return {
            "success": True,
            "message": "Multi-output model training completed successfully",
            "training_results": training_results,
            "test_evaluation": test_evaluation,
            "timestamp": _utcnow().isoformat(),
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"\n{'='*60}")
        print(f" CRITICAL ERROR in /multi-output-model-training endpoint")
        print(f"{'='*60}")
        print(f"Error type: {type(e).__name__}")
        print(f"Error message: {str(e)}")

        import traceback

        print(f"\nFull traceback:")
        traceback.print_exc()
        print(f"{'='*60}\n")

        raise HTTPException(status_code=500, detail="Internal server error")


@app.get("/multitarget-nutrition-model-training")
async def multitarget_nutrition_model_training(
    request: Request,
    x_auth_token: Optional[str] = Header(None, alias="x-auth-token"),
):
    """Train and evaluate the multi-target nutrition XGBoost model"""
    try:
        _require_user_id_from_request(request, x_auth_token)
        print(f"\n{'='*60}")
        print(f" MULTITARGET NUTRITION MODEL TRAINING REQUESTED")
        print(f"{'='*60}")
        
        # Run the nutrition model training pipeline
        if create_nutrition_training_pipeline is None:
            raise HTTPException(status_code=503, detail="Nutrition training pipeline unavailable")
        model, training_results, test_evaluation = create_nutrition_training_pipeline()
        
        print(f" Multi-target nutrition model training completed successfully")
        print(f"{'='*60}\n")
        
        return {
            "success": True,
            "message": "Multi-target nutrition model training completed successfully",
            "training_results": training_results,
            "test_evaluation": test_evaluation,
            "timestamp": _utcnow().isoformat(),
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"\n{'='*60}")
        print(f" CRITICAL ERROR in /multitarget-nutrition-model-training endpoint")
        print(f"{'='*60}")
        print(f"Error type: {type(e).__name__}")
        print(f"Error message: {str(e)}")

        import traceback

        print(f"\nFull traceback:")
        traceback.print_exc()
        print(f"{'='*60}\n")

        raise HTTPException(status_code=500, detail="Internal server error")


@app.get("/evaluation-framework-demo")
async def evaluation_framework_demo(
    request: Request,
    x_auth_token: Optional[str] = Header(None, alias="x-auth-token"),
):
    """Run the evaluation framework demo"""
    try:
        _require_user_id_from_request(request, x_auth_token)
        print(f"\n{'='*60}")
        print(f" EVALUATION FRAMEWORK DEMO REQUESTED")
        print(f"{'='*60}")
        
        # Run the evaluation framework demo
        if example_execution_flow is None:
            raise HTTPException(status_code=503, detail="Evaluation framework module unavailable")
        example_execution_flow()
        
        print(f" Evaluation framework demo completed successfully")
        print(f"{'='*60}\n")
        
        return {
            "success": True,
            "message": "Evaluation framework demo completed successfully",
            "timestamp": _utcnow().isoformat(),
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"\n{'='*60}")
        print(f" CRITICAL ERROR in /evaluation-framework-demo endpoint")
        print(f"{'='*60}")
        print(f"Error type: {type(e).__name__}")
        print(f"Error message: {str(e)}")

        import traceback

        print(f"\nFull traceback:")
        traceback.print_exc()
        print(f"{'='*60}\n")

        raise HTTPException(status_code=500, detail="Internal server error")


@app.get("/profile-change-detection-demo")
async def profile_change_detection_demo(
    request: Request,
    x_auth_token: Optional[str] = Header(None, alias="x-auth-token"),
):
    """Run the profile change detection demo"""
    try:
        _require_user_id_from_request(request, x_auth_token)
        print(f"\n{'='*60}")
        print(f" PROFILE CHANGE DETECTION DEMO REQUESTED")
        print(f"{'='*60}")
        
        # Setup database and run the profile change detection demo
        if setup_database is None or example_usage is None:
            raise HTTPException(status_code=503, detail="Profile change detection module unavailable")
        setup_database()
        example_usage()
        
        print(f" Profile change detection demo completed successfully")
        print(f"{'='*60}\n")
        
        return {
            "success": True,
            "message": "Profile change detection demo completed successfully",
            "timestamp": _utcnow().isoformat(),
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"\n{'='*60}")
        print(f" CRITICAL ERROR in /profile-change-detection-demo endpoint")
        print(f"{'='*60}")
        print(f"Error type: {type(e).__name__}")
        print(f"Error message: {str(e)}")

        import traceback

        print(f"\nFull traceback:")
        traceback.print_exc()
        print(f"{'='*60}\n")

        raise HTTPException(status_code=500, detail="Internal server error")


@app.get("/deterministic-meal-engine-demo")
async def deterministic_meal_engine_demo(
    request: Request,
    x_auth_token: Optional[str] = Header(None, alias="x-auth-token"),
):
    """Run the deterministic meal engine demo"""
    try:
        _require_user_id_from_request(request, x_auth_token)
        print(f"\n{'='*60}")
        print(f" DETERMINISTIC MEAL ENGINE DEMO REQUESTED")
        print(f"{'='*60}")
        
        # Create example user profile
        user_profile = {
            'age': 28,
            'weight': 75.0,
            'height': 180.0,
            'gender': 'Male',
            'goal': 'Muscle Gain',
            'activity_level': 'Active',
            'dietary_preference': 'Non-Veg',
            'allergies': ['Shellfish'],
            'food_dislikes': ['Brussels Sprouts']
        }
        
        # Initialize and run the meal engine
        engine = MealEngine()
        weekly_plan = engine.generate_weekly_plan(user_profile)
        
        print(f" Deterministic meal engine demo completed successfully")
        print(f"Consistency score: {weekly_plan['weekly_summary']['consistency_score']:.2f}")
        print(f"Diversity score: {weekly_plan['weekly_summary']['diversity_score']:.2f}")
        print(f"Total items in shopping list: {len(weekly_plan['shopping_list'])}")
        print(f"{'='*60}\n")
        
        return {
            "success": True,
            "message": "Deterministic meal engine demo completed successfully",
            "weekly_plan": weekly_plan,
            "timestamp": _utcnow().isoformat(),
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"\n{'='*60}")
        print(f" CRITICAL ERROR in /deterministic-meal-engine-demo endpoint")
        print(f"{'='*60}")
        print(f"Error type: {type(e).__name__}")
        print(f"Error message: {str(e)}")

        import traceback

        print(f"\nFull traceback:")
        traceback.print_exc()
        print(f"{'='*60}\n")

        raise HTTPException(status_code=500, detail="Internal server error")


# ==========================================
# CHATBOT ENDPOINT (GEMINI AI)
# ==========================================

# Bug #41 fix: rate limiters now key on the real client IP address, not a
# hardcoded "default" string. The helper below extracts the best available
# IP across direct connections and common reverse-proxy headers.



# ==========================================
# WORKOUT ENDPOINT
# ==========================================


@app.post("/workout")
async def generate_workout(
    profile: WorkoutProfileRequest,
    request: Request,
    x_auth_token: Optional[str] = Header(None, alias="x-auth-token"),
):
    """Generate workout plan using local ML engine with rate limiting"""
    # SEC-8: Enforce per-user rate limit before any expensive ML work.
    rl_key = _rate_limit_key(request, x_auth_token)
    if not _WORKOUT_RATE_LIMITER.is_allowed(rl_key):
        raise HTTPException(
            status_code=429,
            detail="Too many workout generation requests. Please wait a moment and try again.",
        )

    authenticated_user_id = _require_user_id_from_request(request, x_auth_token)

    try:
        profile_dict = _model_to_dict(profile)

        print(f"\n{'='*60}")
        print(f" WORKOUT REQUEST RECEIVED")
        print(f"{'='*60}")
        print("Received workout generation request")

        engine = _ensure_workout_engine_ready()

        # Safely extract fields with defaults â€” include ALL profile fields
        user_data = {
            "user_id": authenticated_user_id,
            "age": profile_dict.get("age", 25),
            "weight": profile_dict.get("weight", 70),
            "height": profile_dict.get("height", 175),
            "gender": profile_dict.get("gender", "Male"),
            "goal": profile_dict.get("goal", "Muscle Gain"),
            "experience": profile_dict.get("experience", "Beginner"),
            "days_per_week": profile_dict.get("days_per_week", 4),
            "equipment": profile_dict.get("equipment", ["Dumbbell"]),
            "body_issues": profile_dict.get("body_issues", []),
            "streak": profile_dict.get("streak", 0),
            "consistency": profile_dict.get("consistency", 0.7),
            "firstWorkoutDay": profile_dict.get("firstWorkoutDay"),
            "registrationDate": profile_dict.get("registrationDate"),
            "is_new_user_week": profile_dict.get("is_new_user_week", False),
        }

        print(f"Generating workout for {user_data['experience']} ({user_data['days_per_week']} days requested)...")

        # Fetch user document with sliced workout history
        user_id_for_persist = str(user_data.get("user_id") or "").strip()
        workout_history = []
        user_doc_for_persist = None
        if user_id_for_persist:
            try:
                user_doc_for_persist = await _find_user_workouts_by_id(user_id_for_persist, limit=50)
                if user_doc_for_persist:
                    workout_history = user_doc_for_persist.get("workouts", [])
            except Exception as lookup_err:
                logger.warning("Could not lookup user workout history: %s", lookup_err)

        # Check in-memory plan cache before running ML generation.
        # Cache key is deterministic: it combines profile fields + ISO-week number.
        # A hit means the same profile already generated a plan this week — no ML needed.
        plan_cache = getattr(engine, "_plan_cache", None)
        cached_weekly_plan = plan_cache.get(user_data) if plan_cache else None
        if cached_weekly_plan:
            print(" [PlanCache] HIT — returning cached plan, skipping ML generation")
            weekly_plan = cached_weekly_plan
        else:
            # Generate workout (ML computation happens here)
            weekly_plan = engine.generate_weekly_plan(user_data, workout_history=workout_history)
            # Store the freshly generated plan so subsequent page visits are instant
            if plan_cache and weekly_plan:
                try:
                    plan_cache.set(user_data, weekly_plan)
                except Exception as cache_err:
                    logger.warning("Could not store plan in cache: %s", cache_err)

        if not weekly_plan or len(weekly_plan) == 0:
            print("ERROR: Generated plan is empty!")
            raise HTTPException(status_code=500, detail="Generated empty workout plan")


        # Compute progression state and structured coaching feedback
        progression_state = {}
        coaching_feedback = {}
        if engine.progression_engine:
            progression_state = engine.progression_engine.get_progression_state(user_data, workout_history, engine.exercises_df)
            coaching_feedback = engine.progression_engine.generate_structured_coaching_feedback(progression_state, user_data)

        total_exercises = sum(len(day.get("exercises", [])) for day in weekly_plan)
        workout_days_count = sum(1 for day in weekly_plan if day.get("type") == "workout")
        rest_days_count = 7 - workout_days_count

        registration_day_index = _safe_day_index(user_data.get("firstWorkoutDay"))
        is_new_user_week = bool(user_data.get("is_new_user_week")) or _is_registration_in_current_week(user_data.get("registrationDate"))

        week_metadata = _build_week_metadata(
            weekly_plan,
            registration_day_index=registration_day_index,
            is_new_user_week=is_new_user_week,
            existing_metadata=(user_doc_for_persist or {}).get("workoutWeekMetadata"),
        )
        user_context = {
            "registration_day": registration_day_index,
            "is_new_user": bool(is_new_user_week),
            "today_index": _today_weekday_index(),
        }

        # Persist the generated weekly plan when a valid user_id is supplied.
        if user_doc_for_persist:
            try:
                await _persist_workout_plan_and_metadata({"_id": user_doc_for_persist.get("_id")}, weekly_plan, week_metadata)
            except Exception as persist_err:
                logger.warning("Could not persist generated workout plan metadata: %s", persist_err)

        print(
            f"SUCCESS: Generated {len(weekly_plan)} days ({workout_days_count} workout, {rest_days_count} rest) with {total_exercises} total exercises"
        )
        print(f"{'='*60}\n")

        return _api_success(
            "Workout generated successfully",
            data={
                "workout": weekly_plan,
                "exercises_count": total_exercises,
                "workout_days": workout_days_count,
                "rest_days": rest_days_count,
                "week_metadata": week_metadata,
                "user_context": user_context,
                "progression_state": progression_state,
                "coaching_feedback": coaching_feedback,
            },
            workout=weekly_plan,
            exercises_count=total_exercises,
            workout_days=workout_days_count,
            rest_days=rest_days_count,
            week_metadata=week_metadata,
            user_context=user_context,
            progression_state=progression_state,
            coaching_feedback=coaching_feedback,
        )

    except HTTPException:
        raise
    except Exception as e:
        print(f"\n{'='*60}")
        print(f" CRITICAL ERROR in /workout endpoint")
        print(f"{'='*60}")
        print(f"Error type: {type(e).__name__}")
        print(f"Error message: {str(e)}")

        import traceback

        print(f"\nFull traceback:")
        traceback.print_exc()
        print(f"{'='*60}\n")

        raise HTTPException(status_code=500, detail="Internal server error")


_async_workout_jobs: Dict[str, Dict[str, Any]] = {}
_ASYNC_WORKOUT_JOB_TTL_SECONDS = int(os.getenv("ASYNC_WORKOUT_JOB_TTL_SECONDS", "1800"))
_ASYNC_WORKOUT_MAX_JOBS = int(os.getenv("ASYNC_WORKOUT_MAX_JOBS", "1000"))


def _cleanup_async_workout_jobs() -> None:
    """Evict stale/completed jobs and cap memory use for async job state."""
    if not _async_workout_jobs:
        return

    now = _utcnow()
    stale_before = now - timedelta(seconds=_ASYNC_WORKOUT_JOB_TTL_SECONDS)

    for job_id, job in list(_async_workout_jobs.items()):
        status = job.get("status")
        if status not in {"complete", "error"}:
            continue

        ts_raw = job.get("updated_at") or job.get("created_at")
        if not ts_raw:
            continue

        try:
            ts = datetime.fromisoformat(str(ts_raw).replace("Z", "+00:00"))
            if ts.tzinfo is not None:
                ts = ts.replace(tzinfo=None)
        except Exception:
            continue

        if ts < stale_before:
            _async_workout_jobs.pop(job_id, None)

    if len(_async_workout_jobs) > _ASYNC_WORKOUT_MAX_JOBS:
        overflow = len(_async_workout_jobs) - _ASYNC_WORKOUT_MAX_JOBS
        oldest_first = sorted(
            _async_workout_jobs.items(),
            key=lambda item: item[1].get("updated_at") or item[1].get("created_at") or "",
        )
        for job_id, _ in oldest_first[:overflow]:
            _async_workout_jobs.pop(job_id, None)


async def _generate_workout_job(job_id: str, profile_data: Dict[str, Any]) -> None:
    try:
        engine = _ensure_workout_engine_ready()
        
        user_id = profile_data.get("user_id")
        workout_history = []
        user_doc = None
        if user_id:
            try:
                user_doc = await _find_user_workouts_by_id(str(user_id).strip(), limit=50)
                if user_doc:
                    workout_history = user_doc.get("workouts", [])
            except Exception as lookup_err:
                logger.warning("Could not lookup user workout history: %s", lookup_err)
                
        plan = engine.generate_weekly_plan(profile_data, workout_history=workout_history)
        
        # Compute progression state and structured coaching feedback
        progression_state = {}
        coaching_feedback = {}
        if engine.progression_engine:
            progression_state = engine.progression_engine.get_progression_state(profile_data, workout_history, engine.exercises_df)
            coaching_feedback = engine.progression_engine.generate_structured_coaching_feedback(progression_state, profile_data)
            
        registration_day_index = _safe_day_index(profile_data.get("firstWorkoutDay"))
        is_new_user_week = bool(profile_data.get("is_new_user_week")) or _is_registration_in_current_week(profile_data.get("registrationDate"))

        week_metadata = _build_week_metadata(
            plan,
            registration_day_index=registration_day_index,
            is_new_user_week=is_new_user_week,
            existing_metadata=(user_doc or {}).get("workoutWeekMetadata"),
        )
        user_context = {
            "registration_day": registration_day_index,
            "is_new_user": bool(is_new_user_week),
            "today_index": _today_weekday_index(),
        }

        # Persist generated weekly plan if user doc exists
        if user_doc:
            try:
                await _persist_workout_plan_and_metadata({"_id": user_doc.get("_id")}, plan, week_metadata)
            except Exception as persist_err:
                logger.warning("Could not persist generated workout plan metadata in job: %s", persist_err)

        _async_workout_jobs[job_id] = {
            "status": "complete",
            "plan": plan,
            "week_metadata": week_metadata,
            "user_context": user_context,
            "progression_state": progression_state,
            "coaching_feedback": coaching_feedback,
            "updated_at": _utcnow().isoformat(),
        }
    except Exception as exc:
        _async_workout_jobs[job_id] = {
            "status": "error",
            "error": f"{type(exc).__name__}: {exc}",
            "updated_at": _utcnow().isoformat(),
        }


@app.post("/workout/async")
async def generate_workout_async(profile: WorkoutProfileRequest, background_tasks: BackgroundTasks):
    """Start background workout generation and return a polling job id."""
    _cleanup_async_workout_jobs()
    profile_dict = _model_to_dict(profile)
    engine = _ensure_workout_engine_ready()

    # Fast path: return server-side cached plan immediately when available.
    cache = getattr(engine, "_plan_cache", None)
    if cache:
        cached_plan = cache.get(profile_dict)
        if cached_plan:
            return {
                "status": "complete",
                "cached": True,
                "plan": cached_plan,
                "job_id": None,
            }

    job_id = str(uuid.uuid4())
    _async_workout_jobs[job_id] = {
        "status": "processing",
        "created_at": _utcnow().isoformat(),
    }
    background_tasks.add_task(_generate_workout_job, job_id, profile_dict)
    return {
        "status": "processing",
        "cached": False,
        "job_id": job_id,
        "estimated_seconds": 15,
    }


@app.get("/workout/status/{job_id}")
async def get_workout_status(job_id: str):
    _cleanup_async_workout_jobs()
    job = _async_workout_jobs.get(job_id)
    if not job:
        raise HTTPException(status_code=404, detail=f"Job {job_id} not found")
    return job


@app.post("/workout/cache/invalidate")
async def invalidate_workout_cache(profile: Dict[str, Any]):
    engine = _ensure_workout_engine_ready()
    cache = getattr(engine, "_plan_cache", None)
    if not cache:
        return _api_success("No cache configured", data={"invalidated": False})

    cache.invalidate(profile or {})
    return _api_success("Workout cache invalidated", data={"invalidated": True})


# ==========================================
# WEEKLY PLAN & SWAP OPTIONS ENDPOINTS
# ==========================================


@app.get("/api/weekly-plan")
async def get_weekly_plan(
    request: Request,
    x_auth_token: Optional[str] = Header(None, alias="x-auth-token"),
):
    """Return user's persisted weekly plan with week-level metadata."""
    try:
        _ensure_workout_engine_ready()

        user_id = _require_user_id_from_request(request, x_auth_token)
        user_doc = await _find_user_by_id(user_id)
        if not user_doc:
            raise HTTPException(status_code=404, detail="User not found")

        payload = await _load_or_generate_user_weekly_plan(user_doc)

        return _api_success(
            "Weekly plan fetched successfully",
            data={
                "plan": payload["plan"],
                "week_metadata": payload["week_metadata"],
                "user_context": payload["user_context"],
            },
            plan=payload["plan"],
            week_metadata=payload["week_metadata"],
            user_context=payload["user_context"],
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error("[weekly-plan] Error: %s", e)
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail="Internal server error")


@app.get("/api/swap-options")
async def get_workout_swap_options(
    request: Request,
    day_index: int = Query(..., ge=0, le=6),
    x_auth_token: Optional[str] = Header(None, alias="x-auth-token"),
):
    """Return swap eligibility and available target rest days for a specific day."""
    try:
        _ensure_workout_engine_ready()

        user_id = _require_user_id_from_request(request, x_auth_token)
        user_doc = await _find_user_by_id(user_id)
        if not user_doc:
            raise HTTPException(status_code=404, detail="User not found")

        payload = await _load_or_generate_user_weekly_plan(user_doc)
        weekly_plan = payload["plan"]
        week_metadata = payload["week_metadata"]
        user_context = payload["user_context"]
        today_index = int(user_context.get("today_index", _today_weekday_index()))

        if not isinstance(weekly_plan, list) or len(weekly_plan) != 7:
            raise HTTPException(status_code=500, detail="Weekly plan is invalid")

        day = weekly_plan[day_index] if isinstance(weekly_plan[day_index], dict) else {}
        can_swap_to_workout = False
        can_swap_to_rest = False
        available_rest_days: List[Dict[str, Any]] = []
        block_reason = None

        if not day or day.get("is_placeholder"):
            block_reason = "Selected day is not available"
        elif day_index < today_index:
            block_reason = "Cannot swap past days"
        else:
            day_type = day.get("type")

            if day_type == "rest":
                if not day.get("is_original_rest", True):
                    block_reason = "Only original planned rest days can be swapped"
                elif day.get("is_swapped") or day.get("is_swappable", True) is False:
                    block_reason = "This rest day is already locked"
                else:
                    for idx in range(day_index + 1, 7):
                        candidate = weekly_plan[idx] if isinstance(weekly_plan[idx], dict) else {}
                        if candidate.get("type") != "workout":
                            continue
                        if candidate.get("is_placeholder"):
                            continue
                        if not candidate.get("is_original_workout", True):
                            continue
                        if candidate.get("is_swapped"):
                            continue
                        if candidate.get("is_swappable", True) is False:
                            continue
                        if idx < today_index:
                            continue
                        can_swap_to_workout = True
                        break

                    if not can_swap_to_workout:
                        block_reason = "No future original workout day available"

            elif day_type == "workout":
                if not day.get("is_original_workout", True):
                    block_reason = "Only original planned workout days can be swapped"
                elif day.get("is_swapped") or day.get("is_swappable", True) is False:
                    block_reason = "This workout day is already locked"
                elif day.get("is_completed") or int(day.get("exercises_completed", 0) or 0) > 0:
                    block_reason = "Cannot swap started or completed workout day"
                else:
                    for idx in range(day_index + 1, 7):
                        candidate = weekly_plan[idx] if isinstance(weekly_plan[idx], dict) else {}
                        if candidate.get("type") != "rest":
                            continue
                        if candidate.get("is_placeholder"):
                            continue
                        if not candidate.get("is_original_rest", True):
                            continue
                        if candidate.get("is_swapped"):
                            continue
                        if candidate.get("is_swappable", True) is False:
                            continue
                        if idx < today_index:
                            continue

                        available_rest_days.append(
                            {
                                "day_of_week": idx,
                                "day": candidate.get("day") or f"Day {idx + 1}",
                                "date": candidate.get("date"),
                            }
                        )

                    can_swap_to_rest = len(available_rest_days) > 0
                    if not can_swap_to_rest:
                        block_reason = "No future original rest day available"
            else:
                block_reason = "Swap is not available for this day"

        return _api_success(
            "Swap options computed",
            data={
                "day_index": day_index,
                "can_swap_to_workout": can_swap_to_workout,
                "can_swap_to_rest": can_swap_to_rest,
                "available_rest_days": available_rest_days,
                "block_reason": block_reason,
                "week_metadata": week_metadata,
                "user_context": user_context,
            },
            day_index=day_index,
            can_swap_to_workout=can_swap_to_workout,
            can_swap_to_rest=can_swap_to_rest,
            available_rest_days=available_rest_days,
            block_reason=block_reason,
            week_metadata=week_metadata,
            user_context=user_context,
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error("[swap-options] Error: %s", e)
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail="Internal server error")


# ==========================================
# NUTRITION SWAP ENDPOINT
# ==========================================

class SwapRequest(BaseModel):
    food_name: str
    meal_type: str
    age: Optional[int] = 25
    weight: Optional[float] = 70
    height: Optional[float] = 175
    gender: Optional[str] = "Male"
    goal: Optional[str] = "Maintenance"
    dietary_preference: Optional[str] = "Non-Veg"
    allergies: Optional[List[str]] = Field(default_factory=list)
    # Pass these so swaps are scaled to the same nutrition as the current item
    current_calories: Optional[float] = None
    current_protein: Optional[float] = None

@app.post("/nutrition/swap")
async def get_swap_options(
    body: SwapRequest,
    http_request: Request,
    x_auth_token: Optional[str] = Header(None, alias="x-auth-token"),
):
    """Return swap alternatives for a given food item using Swap_Group from dataset"""
    try:
        _require_user_id_from_request(http_request, x_auth_token)
        meal_runtime = _ensure_meal_engine_ready()
        profile = {
            'age': body.age,
            'weight': body.weight,
            'height': body.height,
            'gender': body.gender,
            'goal': body.goal,
            'dietary_preference': body.dietary_preference,
            'allergies': body.allergies,
        }
        import re
        food_name_clean = body.food_name
        if food_name_clean:
            food_name_clean = re.sub(r'\s*\(.*?\)', '', food_name_clean).strip()

        options = meal_runtime.get_swap_options(
            food_name_clean, body.meal_type, profile, limit=5,
            target_calories=body.current_calories,
            target_protein=body.current_protein,
        )
        return _api_success(
            "Swap options generated",
            data={
                "swap_options": options,
                "original_food": body.food_name,
            },
            swap_options=options,
            original_food=body.food_name,
        )
    except Exception as e:
        logger.error(f"Swap error: {e}")
        return {
            'success': False,
            'message': 'Failed to generate swap options',
            'data': {},
            'swap_options': [],
            'timestamp': _utcnow().isoformat(),
        }


def _perform_undo_swap(weekly_plan: List[Dict[str, Any]], day_a_idx: int, day_b_idx: int) -> List[Dict[str, Any]]:
    import copy
    plan_copy = [copy.deepcopy(day) for day in weekly_plan]
    day_a = plan_copy[day_a_idx]
    day_b = plan_copy[day_b_idx]
    
    if day_a.get('type') == 'rest':
        rest_day = day_a
        workout_day = day_b
        rest_idx = day_a_idx
        workout_idx = day_b_idx
    else:
        rest_day = day_b
        workout_day = day_a
        rest_idx = day_b_idx
        workout_idx = day_a_idx
        
    rest_day_name = workout_day.get('day', '')
    rest_day_of_week = workout_day.get('day_of_week', workout_idx)
    
    restored_rest_day = {
        **workout_day,
        'type': 'rest',
        'focus': 'Rest Day',
        'warmup': [],
        'exercises': [],
        'day': rest_day_name,
        'day_of_week': rest_day_of_week,
        'intensity': 0,
        'is_placeholder': False,
        'can_access': True,
        'is_swapped': False,
        'swapped_from': None,
        'swapped_to': None,
        'is_original_rest': True,
        'is_original_workout': False,
        'is_swappable': True,
        'is_completed': False,
        'exercises_completed': 0,
        'exercises_total': 0,
        'note': 'Rest Day',
    }
    restored_rest_day.pop('exercises_completed_detail', None)
    
    workout_day_name = rest_day.get('day', '')
    workout_day_of_week = rest_day.get('day_of_week', rest_idx)
    
    restored_workout_day = {
        **rest_day,
        'type': 'workout',
        'focus': workout_day.get('focus', 'Workout'),
        'warmup': workout_day.get('warmup', []),
        'exercises': workout_day.get('exercises', []),
        'day': workout_day_name,
        'day_of_week': workout_day_of_week,
        'intensity': workout_day.get('intensity', 1),
        'is_placeholder': False,
        'can_access': True,
        'is_swapped': False,
        'swapped_from': None,
        'swapped_to': None,
        'is_original_rest': False,
        'is_original_workout': True,
        'is_swappable': True,
        'is_completed': False,
        'exercises_completed': 0,
        'exercises_total': len(workout_day.get('exercises', [])),
        'note': workout_day.get('focus', 'Workout'),
    }
    
    plan_copy[rest_idx] = restored_workout_day
    plan_copy[workout_idx] = restored_rest_day
    return plan_copy


async def _persist_undo_swap_result(
    email: str,
    swapped_plan: List[Dict[str, Any]],
    day_a_idx: int,
    day_b_idx: int,
    existing_user: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    user_doc = existing_user or await _find_user_by_email(email)
    if not user_doc:
        return _build_week_metadata(swapped_plan)

    registration_day_index = _safe_day_index(user_doc.get("firstWorkoutDay"))
    is_new_user_week = _is_registration_in_current_week(user_doc.get("registrationDate"))

    existing_metadata = user_doc.get("workoutWeekMetadata") or {}
    existing_history = _normalize_swap_history(existing_metadata.get("swap_history"))
    
    new_history = []
    removed = False
    for entry in existing_history:
        from_day = entry.get("from_day")
        to_day = entry.get("to_day")
        if not removed and (
            (from_day == day_a_idx and to_day == day_b_idx) or
            (from_day == day_b_idx and to_day == day_a_idx)
        ):
            removed = True
            continue
        new_history.append(entry)

    temp_metadata = {**existing_metadata, "swap_history": new_history}
    
    if "swap_limits" in temp_metadata and isinstance(temp_metadata["swap_limits"], dict):
        current_week_start = _current_week_start_date_iso()
        current_week_history = [
            e for e in new_history 
            if str(e.get("timestamp", "")) >= current_week_start
        ]
        temp_metadata["swap_limits"]["swaps_used"] = len(current_week_history)
        temp_metadata["swap_limits"]["swaps_remaining"] = max(0, temp_metadata["swap_limits"]["max_swaps_per_week"] - len(current_week_history))

    week_metadata = _build_week_metadata(
        swapped_plan,
        registration_day_index=registration_day_index,
        is_new_user_week=is_new_user_week,
        existing_metadata=temp_metadata,
    )

    await _persist_workout_plan_and_metadata({"_id": user_doc.get("_id")}, swapped_plan, week_metadata)
    
    try:
        db = get_database()
        await db.swap_history.delete_one({
            "user_id": user_doc.get("_id"),
            "$or": [
                {"from_day_index": day_a_idx, "to_day_index": day_b_idx},
                {"from_day_index": day_b_idx, "to_day_index": day_a_idx}
            ]
        })
    except Exception as err:
        logger.warning("Unable to delete swap audit log for undo: %s", err)

    return week_metadata


# ==========================================
# REST DAY SWAP ENDPOINT
# ==========================================

class SwapRestDayRequest(BaseModel):
    """Request to swap a rest day with the next workout day"""
    # Deprecated identity field kept optional for backward compatibility.
    # User identity is resolved from JWT, not request payload.
    email: Optional[EmailStr] = Field(default=None)
    rest_day_index: int = Field(ge=0, le=6, description="Index of the rest day to swap (0-6)")
    current_day_index: Optional[int] = Field(default=None, ge=0, le=6)
    current_plan: List[Dict[str, Any]]


class SwapWorkoutToRestRequest(BaseModel):
    """Request to move a workout day onto a future rest day."""
    # Deprecated identity field kept optional for backward compatibility.
    # User identity is resolved from JWT, not request payload.
    email: Optional[EmailStr] = Field(default=None)
    workout_day_index: int = Field(ge=0, le=6)
    target_rest_day_index: int = Field(ge=0, le=6)
    current_day_index: Optional[int] = Field(default=None, ge=0, le=6)
    current_plan: List[Dict[str, Any]]


@app.post("/api/swap-rest-day")
@app.post("/api/swap-rest-to-workout")
async def swap_rest_day(
    request: SwapRestDayRequest,
    http_request: Request,
    x_auth_token: Optional[str] = Header(None, alias="x-auth-token"),
):
    """
    Swap a rest day with the next available workout day.
    
    When a user wants to workout on a rest day, this endpoint swaps
    today's rest with tomorrow's workout, making the workout available
    today and moving the rest to the next workout day.
    
    Returns:
        {
            success: bool,
            workout: [...],  # Updated 7-day plan
            message: str,
            swapped_days: {
                rest_day_index: int,
                workout_day_index: int
            }
        }
    """
    try:
        # SEC-29 fix: resolve user identity from JWT (header/cookie), not payload email.
        user_id = _require_user_id_from_request(http_request, x_auth_token)
        user_doc = await _find_user_by_id(user_id)
        if not user_doc:
            raise HTTPException(status_code=404, detail="User not found")

        workout_runtime = _ensure_workout_engine_ready()
        
        # Validate current plan
        if not request.current_plan or len(request.current_plan) != 7:
            raise HTTPException(status_code=400, detail="current_plan must contain exactly 7 days")

        if any(not isinstance(day, dict) for day in request.current_plan):
            raise HTTPException(status_code=400, detail="current_plan must be an array of day objects")
            
        # Check if it is an undo swap
        rest_day = request.current_plan[request.rest_day_index]
        is_undo = False
        target_workout_idx = None
        
        if rest_day.get('is_swapped'):
            swapped_from_idx = rest_day.get('swapped_from')
            if isinstance(swapped_from_idx, int) and 0 <= swapped_from_idx <= 6:
                other_day = request.current_plan[swapped_from_idx]
                if other_day.get('is_swapped') and other_day.get('type') == 'workout':
                    is_undo = True
                    target_workout_idx = swapped_from_idx

        if is_undo:
            swapped_plan = _perform_undo_swap(request.current_plan, request.rest_day_index, target_workout_idx)
            swapped_days = {
                "rest_day_index": request.rest_day_index,
                "workout_day_index": target_workout_idx,
            }
            week_metadata = await _persist_undo_swap_result(
                str(user_doc.get("email") or ""),
                swapped_plan,
                request.rest_day_index,
                target_workout_idx,
                existing_user=user_doc,
            )
            return _api_success(
                "Swap undone successfully",
                data={
                    "workout": swapped_plan,
                    "swapped_days": swapped_days,
                    "week_metadata": week_metadata,
                },
                workout=swapped_plan,
                swapped_days=swapped_days,
                week_metadata=week_metadata,
            )

        swap_limit_state = _get_swap_limit_state(user_doc.get("workoutWeekMetadata"))
        if swap_limit_state["swaps_remaining"] <= 0:
            raise HTTPException(status_code=400, detail="Weekly swap limit reached")
        
        # Check if the specified day is actually a rest day
        rest_day = request.current_plan[request.rest_day_index]
        if rest_day.get('type') != 'rest':
            raise HTTPException(
                status_code=400, 
                detail=f"Day {request.rest_day_index} is not a rest day"
            )
        if rest_day.get('is_placeholder'):
            raise HTTPException(status_code=400, detail="Cannot swap placeholder days")
        if request.current_day_index is not None and request.rest_day_index < request.current_day_index:
            raise HTTPException(status_code=400, detail="Cannot swap past rest days")
        if not rest_day.get('is_original_rest', True):
            raise HTTPException(status_code=400, detail="Only original planned rest days can be swapped")
        if rest_day.get('is_swapped'):
            raise HTTPException(status_code=400, detail="This rest day has already been swapped")
        if rest_day.get('is_swappable', True) is False:
            raise HTTPException(status_code=400, detail="This rest day is locked and cannot be swapped")
        
        # Find next eligible workout day in the same week (no wrap-around)
        next_workout_idx = None
        for idx in range(request.rest_day_index + 1, 7):
            day = request.current_plan[idx]
            if day.get('type') != 'workout':
                continue
            if day.get('is_placeholder'):
                continue
            if not day.get('is_original_workout', True):
                continue
            if day.get('is_swapped'):
                continue
            if day.get('is_swappable', True) is False:
                continue
            if request.current_day_index is not None and idx < request.current_day_index:
                continue
            next_workout_idx = idx
            break
        
        if next_workout_idx is None:
            raise HTTPException(
                status_code=400,
                detail="No workout day found to swap with"
            )
        
        # Perform the swap using the workout engine
        if not hasattr(workout_runtime, 'swap_rest_with_next_workout'):
            raise HTTPException(status_code=501, detail="swap_rest_with_next_workout is not implemented in WorkoutEngine")
            
        swapped_plan = workout_runtime.swap_rest_with_next_workout(
            request.current_plan, 
            request.rest_day_index,
            request.current_day_index,
        )

        if not isinstance(swapped_plan, list) or len(swapped_plan) != 7:
            raise HTTPException(status_code=500, detail="Swap produced an invalid plan")

        swapped_days = {
            "rest_day_index": request.rest_day_index,
            "workout_day_index": next_workout_idx,
        }
        workout_focus = request.current_plan[next_workout_idx].get("focus") if isinstance(request.current_plan[next_workout_idx], dict) else "Workout"
        swap_record = {
            "timestamp": _utcnow().isoformat(),
            "from_day": request.rest_day_index,
            "to_day": next_workout_idx,
            "direction": "rest_to_workout",
            "workout_focus": workout_focus,
        }

        week_metadata = await _persist_swap_result_for_email(
            str(user_doc.get("email") or ""),
            swapped_plan,
            swap_record,
            existing_user=user_doc,
        )
        
        return _api_success(
            "Rest day swapped successfully",
            data={
                "workout": swapped_plan,
                "swapped_days": swapped_days,
                "week_metadata": week_metadata,
            },
            workout=swapped_plan,
            swapped_days=swapped_days,
            week_metadata=week_metadata,
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"[swap-rest-day] Error: {e}")
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail="Internal server error")


@app.post("/api/swap-workout-to-rest")
async def swap_workout_to_rest(
    request: SwapWorkoutToRestRequest,
    http_request: Request,
    x_auth_token: Optional[str] = Header(None, alias="x-auth-token"),
):
    """Move an original workout day to a selected future original rest day."""
    try:
        # SEC-29 fix: resolve user identity from JWT (header/cookie), not payload email.
        user_id = _require_user_id_from_request(http_request, x_auth_token)
        user_doc = await _find_user_by_id(user_id)
        if not user_doc:
            raise HTTPException(status_code=404, detail="User not found")

        workout_runtime = _ensure_workout_engine_ready()
        
        # Validate current plan
        if not request.current_plan or len(request.current_plan) != 7:
            raise HTTPException(status_code=400, detail="current_plan must contain exactly 7 days")
        if any(not isinstance(day, dict) for day in request.current_plan):
            raise HTTPException(status_code=400, detail="current_plan must be an array of day objects")
        if request.workout_day_index == request.target_rest_day_index:
            raise HTTPException(status_code=400, detail="Cannot swap a day with itself")
        if request.target_rest_day_index <= request.workout_day_index:
            raise HTTPException(status_code=400, detail="Target rest day must be in the future")

        source_day = request.current_plan[request.workout_day_index]
        target_day = request.current_plan[request.target_rest_day_index]
        
        is_undo = False
        if source_day.get('is_swapped') and target_day.get('is_swapped'):
            if source_day.get('swapped_from') == request.target_rest_day_index and target_day.get('swapped_from') == request.workout_day_index:
                is_undo = True

        if is_undo:
            swapped_plan = _perform_undo_swap(request.current_plan, request.workout_day_index, request.target_rest_day_index)
            swapped_days = {
                "workout_day_index": request.workout_day_index,
                "rest_day_index": request.target_rest_day_index,
            }
            week_metadata = await _persist_undo_swap_result(
                str(user_doc.get("email") or ""),
                swapped_plan,
                request.workout_day_index,
                request.target_rest_day_index,
                existing_user=user_doc,
            )
            return _api_success(
                "Swap undone successfully",
                data={
                    "workout": swapped_plan,
                    "swapped_days": swapped_days,
                    "week_metadata": week_metadata,
                },
                workout=swapped_plan,
                swapped_days=swapped_days,
                week_metadata=week_metadata,
            )

        swap_limit_state = _get_swap_limit_state(user_doc.get("workoutWeekMetadata"))
        if swap_limit_state["swaps_remaining"] <= 0:
            raise HTTPException(status_code=400, detail="Weekly swap limit reached")

        if source_day.get('type') != 'workout':
            raise HTTPException(status_code=400, detail="Source day is not a workout day")
        if source_day.get('is_placeholder'):
            raise HTTPException(status_code=400, detail="Cannot swap placeholder workout days")
        if request.current_day_index is not None and request.workout_day_index < request.current_day_index:
            raise HTTPException(status_code=400, detail="Cannot swap past workout days")
        if not source_day.get('is_original_workout', True):
            raise HTTPException(status_code=400, detail="Only original planned workout days can be swapped")
        if source_day.get('is_swapped'):
            raise HTTPException(status_code=400, detail="This workout day has already been swapped")
        if source_day.get('is_swappable', True) is False:
            raise HTTPException(status_code=400, detail="This workout day is locked and cannot be swapped")
        if source_day.get('is_completed') or int(source_day.get('exercises_completed', 0) or 0) > 0:
            raise HTTPException(status_code=400, detail="Cannot swap a completed or started workout day")

        if target_day.get('type') != 'rest':
            raise HTTPException(status_code=400, detail="Target day is not a rest day")
        if target_day.get('is_placeholder'):
            raise HTTPException(status_code=400, detail="Cannot swap into placeholder days")
        if not target_day.get('is_original_rest', True):
            raise HTTPException(status_code=400, detail="Can only swap with original planned rest days")
        if target_day.get('is_swapped'):
            raise HTTPException(status_code=400, detail="Target rest day is already swapped")
        if target_day.get('is_swappable', True) is False:
            raise HTTPException(status_code=400, detail="Target rest day is locked and cannot be used")

        if not hasattr(workout_runtime, 'swap_workout_with_future_rest'):
            raise HTTPException(status_code=501, detail="swap_workout_with_future_rest is not implemented in WorkoutEngine")
            
        swapped_plan = workout_runtime.swap_workout_with_future_rest(
            request.current_plan,
            request.workout_day_index,
            request.target_rest_day_index,
            request.current_day_index,
        )

        if not isinstance(swapped_plan, list) or len(swapped_plan) != 7:
            raise HTTPException(status_code=500, detail="Swap produced an invalid plan")

        workout_focus = source_day.get("focus") if isinstance(source_day, dict) else "Workout"
        swap_record = {
            "timestamp": _utcnow().isoformat(),
            "from_day": request.workout_day_index,
            "to_day": request.target_rest_day_index,
            "direction": "workout_to_rest",
            "workout_focus": workout_focus,
        }

        week_metadata = await _persist_swap_result_for_email(
            str(user_doc.get("email") or ""),
            swapped_plan,
            swap_record,
            existing_user=user_doc,
        )

        return _api_success(
            "Workout day moved to selected rest day successfully",
            data={
                "workout": swapped_plan,
                "swapped_days": {
                    "workout_day_index": request.workout_day_index,
                    "target_rest_day_index": request.target_rest_day_index,
                },
                "week_metadata": week_metadata,
            },
            workout=swapped_plan,
            swapped_days={
                "workout_day_index": request.workout_day_index,
                "target_rest_day_index": request.target_rest_day_index,
            },
            week_metadata=week_metadata,
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"[swap-workout-to-rest] Error: {e}")
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail="Internal server error")


# ==========================================
# NUTRITION ENDPOINT
# ==========================================


def _current_meal_week_key() -> str:
    """Return a stable ISO-week key (e.g. '2026-W26') for cache invalidation.

    Uses the same IST calendar the meal engine uses to pick "today", so the
    weekly cache rolls over on the same boundary the day-slicing does.
    """
    try:
        from app.meal_engine import _IST
        now = datetime.now(_IST)
    except Exception:
        now = _utcnow()
    iso_year, iso_week, _ = now.isocalendar()
    return f"{iso_year}-W{iso_week:02d}"


def _compute_meal_profile_hash(user_profile: Dict) -> str:
    """Deterministic hash of the profile fields that actually change the plan.

    Any change to these fields (or a new ISO week, included separately in the
    cache key) yields a different hash, giving automatic cache invalidation.
    The raw weekly_workout_plan payload is deliberately excluded — it varies in
    representation and the workout plan is itself week-stable via its own cache.
    """
    import hashlib
    import json

    allergies = user_profile.get("allergies") or []
    if not isinstance(allergies, list):
        allergies = [allergies]

    key_fields = {
        "age": user_profile.get("age"),
        "weight": user_profile.get("weight"),
        "height": user_profile.get("height"),
        "gender": user_profile.get("gender"),
        "goal": user_profile.get("goal"),
        "dietary_preference": user_profile.get("dietary_preference"),
        "allergies": sorted(str(a) for a in allergies),
        "activity_level": user_profile.get("activity_level"),
    }
    serialized = json.dumps(key_fields, sort_keys=True, default=str)
    return hashlib.sha256(serialized.encode("utf-8")).hexdigest()


@app.post("/nutrition")
async def generate_nutrition(
    body: NutritionRequest,
    http_request: Request,
    x_auth_token: Optional[str] = Header(None, alias="x-auth-token")
):
    """
    Generate nutrition plan with full error handling and defensive checks
    
    Returns:
    {
        "success": bool,
        "nutrition": {...},
        "request_id": str,
        "timestamp": str
    }
    """
    # SEC-8: Enforce per-user rate limit before any expensive ML work.
    rl_key = _rate_limit_key(http_request, x_auth_token)
    if not _NUTRITION_RATE_LIMITER.is_allowed(rl_key):
        raise HTTPException(
            status_code=429,
            detail="Too many nutrition plan requests. Please wait a moment and try again.",
        )

    # Alias so existing code using 'request' still works.
    request = body
    request_id = str(uuid.uuid4())[:8]
    timestamp = _utcnow().isoformat()
    
    try:
        # ===== STEP 1: LOG INCOMING REQUEST =====
        logger.info(f"[{request_id}] ===== NUTRITION REQUEST STARTED =====")
        logger.info(f"[{request_id}] Timestamp: {timestamp}")
        logger.debug(f"[{request_id}] Incoming request: {_redact_sensitive_fields(_model_to_dict(request))}")
        
        # Require authenticated user for expensive nutrition generation.
        user_id = _require_user_id_from_request(http_request, x_auth_token, request_id)
        logger.info(f"[{request_id}] Authenticated user: {user_id}")
        
        # ===== STEP 2: VALIDATE ENGINES INITIALIZED =====
        try:
            meal_runtime = _ensure_meal_engine_ready()
        except HTTPException:
            logger.error(f"[{request_id}] MealEngine not initialized")
            raise
        
        # ===== STEP 3: PREPARE USER PROFILE =====
        user_profile = {
            "age": request.age,
            "weight": request.weight,
            "height": request.height,
            "gender": request.gender,
            "goal": request.goal,
            "dietary_preference": request.dietary_preference,
            "allergies": request.allergies,
            "activity_level": request.activity_level,
            "weekly_workout_plan": request.weekly_workout_plan or [],
        }
        
        logger.info(f"[{request_id}] Generating nutrition for goal: {request.goal}")
        logger.info(f"[{request_id}] Workout intensity: {request.workout_intensity}")
        logger.info(f"[{request_id}] User profile: {user_profile}")

        # ===== STEP 4: GENERATE MEAL PLAN (with durable per-week cache) =====
        # Mirror the workout endpoint's "generate once per user per ISO-week" behaviour,
        # but backed by MongoDB so it survives server restarts and re-logins. A hit
        # serves the stored weekly plan re-sliced for today's weekday — no ML run.
        profile_hash = _compute_meal_profile_hash(user_profile)
        week_key = _current_meal_week_key()

        meal_plan = None
        cache_collection = None
        try:
            from app.db import get_meal_plan_cache_collection
            cache_collection = get_meal_plan_cache_collection()
        except Exception as cache_init_err:
            logger.warning(f"[{request_id}] Meal cache unavailable, generating fresh: {cache_init_err}")
            cache_collection = None

        if cache_collection is not None:
            try:
                cached_doc = await cache_collection.find_one({"user_id": user_id})
                if (
                    cached_doc
                    and cached_doc.get("profile_hash") == profile_hash
                    and cached_doc.get("week_key") == week_key
                    and isinstance(cached_doc.get("payload"), dict)
                ):
                    logger.info(f"[{request_id}] [MealCache] HIT — serving stored weekly plan (no ML)")
                    # Re-slice the stored weekly plan for today's weekday.
                    meal_plan = meal_runtime.slice_today_from_cached(cached_doc["payload"])
            except Exception as cache_read_err:
                logger.warning(f"[{request_id}] Meal cache read failed, generating fresh: {cache_read_err}")
                meal_plan = None

        if meal_plan is None:
            logger.info(f"[{request_id}] [MealCache] MISS — calling suggest_daily_meals...")
            meal_plan = meal_runtime.suggest_daily_meals(user_profile, request.workout_intensity)

            # Store the freshly generated plan so subsequent visits are instant.
            # Store failures are logged but never block the response.
            if cache_collection is not None and isinstance(meal_plan, dict) and meal_plan.get("meals"):
                try:
                    await cache_collection.replace_one(
                        {"user_id": user_id},
                        {
                            "user_id": user_id,
                            "profile_hash": profile_hash,
                            "week_key": week_key,
                            "payload": meal_plan,
                            "generated_at": _utcnow(),
                        },
                        upsert=True,
                    )
                    logger.info(f"[{request_id}] [MealCache] stored plan for week {week_key}")
                except Exception as cache_write_err:
                    logger.warning(f"[{request_id}] Could not store meal plan in cache: {cache_write_err}")

        logger.info(f"[{request_id}] meal plan returned keys: {list(meal_plan.keys()) if isinstance(meal_plan, dict) else 'NOT A DICT'}")
        logger.info(f"[{request_id}] Meal plan has weekly_plan: {'weekly_plan' in (meal_plan or {})}")
        logger.info(f"[{request_id}] Meal plan has meals array: {len(meal_plan.get('meals', []))} items" if isinstance(meal_plan, dict) else "[{request_id}] No meals array")

        # Validate meal plan structure
        if not meal_plan or not isinstance(meal_plan, dict):
            logger.error(f"[{request_id}] Meal plan generation returned invalid response")
            meal_plan = generate_fallback_meal_plan(user_profile)

        meals = meal_plan.get('meals', [])
        if not meals or len(meals) == 0:
            logger.warning(f"[{request_id}] No meals generated (empty meals array), using fallback")
            logger.info(f"[{request_id}] Meal plan keys: {list(meal_plan.keys())}")
            meal_plan = generate_fallback_meal_plan(user_profile)
            meals = meal_plan.get('meals', [])

        logger.info(f"[{request_id}] Generated {len(meals)} meals")
        
        # ===== STEP 5: VALIDATE MEAL DATA =====
        # Ensure all meals have required fields
        validated_meals = []
        for i, meal in enumerate(meals):
            if not isinstance(meal, dict):
                logger.warning(f"[{request_id}] Meal {i} is not a dict, skipping")
                continue
            
            validated_meal = {
                'meal_type': meal.get('meal_type', 'snack'),
                'name': meal.get('name', f'Meal {i+1}'),
                'calories': max(0, meal.get('calories', 0)),  # Ensure non-negative
                'protein': meal.get('protein', 0),
                'carbs': meal.get('carbs', 0),
                'fat': meal.get('fat', 0),
                'fiber': meal.get('fiber', 0),
            }
            validated_meals.append(validated_meal)
        
        meal_plan['meals'] = validated_meals
        
        # ===== STEP 6: BUILD RESPONSE =====
        response = _api_success(
            "Nutrition generated successfully",
            data={
                "nutrition": meal_plan,
                "ml_powered": True,
                "source": "MealEngine",
                "meals_count": len(validated_meals),
                "workout_intensity": request.workout_intensity,
                "intensity_focus": meal_plan.get("intensity_focus", "performance"),
                "request_id": request_id,
            },
            nutrition=meal_plan,
            ml_powered=True,
            source="MealEngine",
            meals_count=len(validated_meals),
            workout_intensity=request.workout_intensity,
            intensity_focus=meal_plan.get("intensity_focus", "performance"),
            request_id=request_id,
            timestamp=timestamp,
        )
        
        logger.info(f"[{request_id}] ===== NUTRITION REQUEST COMPLETED =====")
        
        return response
        
    except HTTPException:
        logger.error(f"[{request_id}] HTTP exception")
        raise
    except Exception as e:
        logger.error(f"[{request_id}] CRITICAL ERROR: {e}")
        logger.error(f"[{request_id}] Traceback:\n{traceback.format_exc()}")
        
        # Return generic server error; detailed trace stays in logs.
        raise HTTPException(
            status_code=500,
            detail={
                "error": "Failed to generate nutrition plan",
                "request_id": request_id,
            }
        )




# ==========================================
# PROFILE UPDATE ENDPOINT
# ==========================================


@app.put("/profile/update-with-plans")
async def update_profile(
    profile_update: PlanProfileUpdateRequest,
    http_request: Request,
    x_auth_token: Optional[str] = Header(None, alias="x-auth-token"),
):
    """Update user profile and regenerate workouts based on new parameters"""
    try:
        workout_runtime = _ensure_workout_engine_ready()
        meal_runtime = _ensure_meal_engine_ready()

        print(f"\n{'='*60}")
        print(f" PROFILE UPDATE REQUEST RECEIVED")
        print(f"{'='*60}")
        profile_dict = _model_to_dict(profile_update)
        print(f"Profile fields: {sorted(profile_dict.keys())}")
        print(f"Profile summary: {_redact_sensitive_fields(profile_dict)}")
        print(f"{'='*60}\n")

        request_id = str(uuid.uuid4())[:8]
        user_id = _require_user_id_from_request(http_request, x_auth_token, request_id)
        print(f"Authenticated user: {user_id}")

        # **CRITICAL: Force regenerate workout plan with updated profile**
        print("Regenerating workout plan with updated profile...")
        
        # Log the exact data being sent to workout engine
        print("User data sent to workout engine:")
        print(f"   - days_per_week: {profile_dict.get('days_per_week', 'NOT PROVIDED')}")
        print(f"   - goal: {profile_dict.get('goal', 'NOT PROVIDED')}")
        print(f"   - experience: {profile_dict.get('experience', 'NOT PROVIDED')}")
        print(f"   - equipment_count: {len(profile_dict.get('equipment', []) or [])}")
        print(f"   - body_issues_count: {len(profile_dict.get('body_issues', []) or [])}")
        
        # Generate new workout plan
        new_workout_plan = workout_runtime.generate_weekly_plan(
            profile=profile_dict,
            workout_history=None  # **Fresh start - no history bias**
        )

        # **Validate generated plan**
        workout_days = sum(1 for day in new_workout_plan if day.get('type') == 'workout')
        requested_days = profile_dict.get('days_per_week', 4)
        
        print("\nWorkout Plan Generation Summary:")
        print(f"   - Requested days_per_week: {requested_days}")
        print(f"   - Generated workout days: {workout_days}")
        print(f"   - Generated rest days: {len(new_workout_plan) - workout_days}")
        print(f"   - Total plan days: {len(new_workout_plan)}")
        
        if workout_days != requested_days:
            print(f"WARNING: Generated workout days ({workout_days}) don't match requested ({requested_days})")
        else:
            print("Workout days match requested days_per_week")

        # **Generate new nutrition plan**
        print("\nRegenerating nutrition plan with updated profile...")
        if hasattr(meal_runtime, "generate_meal_plan"):
            new_nutrition_plan = meal_runtime.generate_meal_plan(
                profile=profile_dict,
                weekly_workout_plan=new_workout_plan
            )
        else:
            # Fallback if only daily meal API exists
            daily = meal_runtime.suggest_daily_meals(profile_dict, "moderate")
            new_nutrition_plan = {
                "weekly_plan": [daily] * 7,
                "generated_via_fallback": True
            }

        print("Nutrition plan generated")
        # **Return regenerated plans**
        response_data = {
            "success": True,
            "message": "Profile updated and plans regenerated successfully",
            "data": {
                "profile": profile_dict,
                "workout_plan": new_workout_plan,
                "nutrition_plan": new_nutrition_plan,
                "plan_generated_at": _utcnow().isoformat()  # Fixed typo
            }
        }

        print("\nProfile update completed successfully")
        print(f"{'='*60}\n")

        return response_data

    except HTTPException:
        raise
    except Exception as e:
        print(f"\nProfile update error: {str(e)}")
        print(f"Traceback: {traceback.format_exc()}")
        print(f"{'='*60}\n")
        raise HTTPException(status_code=500, detail="Internal server error")


# ==========================================
# SAFE PROFILE UPDATE ENDPOINT (Production Ready)
# ==========================================


@app.put("/profile/update-safe")
async def update_profile_safe(
    profile_update: PlanProfileUpdateRequest,
    http_request: Request,
    x_auth_token: Optional[str] = Header(None, alias="x-auth-token"),
):
    """
    SAFE PROFILE UPDATE ENDPOINT - Production Ready
    
    Features:
    - Graceful degradation (profile updates even if regeneration fails)
    - Comprehensive error handling
    - Transaction-like safety
    - Detailed logging with request IDs
    - Proper HTTP status codes
    
    Request Body:
    - All fields optional (partial updates supported)
    - Validates profile data
    
    HTTP Status Codes:
    - 200: Profile updated successfully (may include regeneration errors)
    - 400: Invalid request data
    - 401: Authentication failed (if JWT enabled)
    - 500: Unexpected internal error
    """
    import uuid
    request_id = str(uuid.uuid4())[:8]
    timestamp = _utcnow().isoformat()
    
    # Initialize response structure
    response_data = {
        "success": False,
        "message": "",
        "request_id": request_id,
        "timestamp": timestamp,
        "data": None,
        "profile_changes": None,
        "regenerated_workout": None,
        "regenerated_nutrition": None,
        "errors": []
    }
    
    try:
        workout_runtime = _ensure_workout_engine_ready()
        meal_runtime = _ensure_meal_engine_ready()

        # ===== STEP 1: LOG INCOMING REQUEST =====
        logger.info(f"[{request_id}] ===== PROFILE UPDATE STARTED =====")
        logger.info(f"[{request_id}] Timestamp: {timestamp}")
        print(f"\n{'='*60}")
        print(f"[{request_id}] SAFE PROFILE UPDATE REQUEST")
        print(f"{'='*60}")
        payload = _model_to_dict(profile_update)
        print(f" Incoming payload fields: {sorted(payload.keys())}")
        print(f" Incoming payload summary: {_redact_sensitive_fields(payload)}")
        print(f"{'='*60}\n")
        
        # ===== STEP 2: VALIDATE INPUT =====
        if not payload:
            logger.warning(f"[{request_id}] Invalid or empty payload")
            raise HTTPException(
                status_code=400,
                detail={"error": "Invalid request body", "message": "Request body must be a valid JSON object", "request_id": request_id}
            )
        
        # ===== STEP 3: AUTHENTICATION =====
        user_id = _require_user_id_from_request(http_request, x_auth_token, request_id)
        logger.info(f"[{request_id}] User ID: {user_id}")
        
        # Load user document from DB to merge profile updates and support generation
        user_doc = await _find_user_by_id(user_id)
        if not user_doc:
            raise HTTPException(
                status_code=404,
                detail={"error": "User not found", "message": "The requested user was not found", "request_id": request_id}
            )
        
        # ===== STEP 4: EXTRACT PROFILE DATA =====
        # Keep only valid profile fields
        valid_fields = [
            'name', 'age', 'gender', 'weight', 'height', 'goal', 'experience',
            'equipment', 'body_issues', 'dietary_preference', 'allergies',
            'days_per_week', 'session_time', 'meal_frequency',
            'cooking_time', 'cuisine_preference', 'dietary_restrictions'
        ]
        filtered_profile = {k: v for k, v in payload.items() if k in valid_fields}
        
        if not filtered_profile:
            logger.warning(f"[{request_id}] No valid profile fields provided")
            raise HTTPException(
                status_code=400,
                detail={"error": "No valid profile fields", "message": "Provide at least one valid profile field", "request_id": request_id}
            )
        
        # Build complete user profile by merging existing DB document with current updates
        full_profile = _build_workout_profile_from_user(user_doc)
        for k, v in filtered_profile.items():
            full_profile[k] = v

        # If only 'name' was changed, update DB and return success early
        plan_affecting_fields = {k for k in filtered_profile if k != 'name'}
        if not plan_affecting_fields:
            logger.info(f"[{request_id}] Name-only update, skipping plan regeneration")
            db = get_database()
            await db.users.update_one(
                {"_id": ObjectId(user_id)},
                {"$set": filtered_profile}
            )
            response_data["success"] = True
            response_data["message"] = "Profile updated successfully (name only, no plan changes)"
            response_data["data"] = {"profile": filtered_profile, "user_id": user_id, "updated_at": timestamp}
            response_data["profile_changes"] = {"changed_fields": list(filtered_profile.keys()), "workout_regenerated": False, "nutrition_regenerated": False}
            return response_data
        
        logger.info(f"[{request_id}] Filtered profile fields: {sorted(filtered_profile.keys())}")
        
        # ===== STEP 5: REGENERATE WORKOUT PLAN (ISOLATED) =====
        workout_error = None
        if any(k in filtered_profile for k in ['goal', 'experience', 'equipment', 'body_issues', 'days_per_week']):
            try:
                logger.info(f"[{request_id}] Starting workout regeneration...")
                print(f"[{request_id}] Regenerating workout plan...")
                
                new_workout_plan = workout_runtime.generate_weekly_plan(
                    profile=full_profile,
                    workout_history=None
                )
                
                response_data["regenerated_workout"] = {
                    "status": "success",
                    "message": "Workout plan regenerated successfully",
                    "plan": new_workout_plan,
                    "days_count": len([d for d in new_workout_plan if d.get('type') == 'workout'])
                }
                logger.info(f"[{request_id}] Workout regeneration completed")
                print(f"[{request_id}] Workout regeneration completed")
                
            except Exception as e:
                workout_error = str(e)
                logger.error(f"[{request_id}] Workout regeneration failed: {e}")
                print(f"[{request_id}] Workout regeneration failed: {e}")
                response_data["errors"].append({
                    "type": "workout_regeneration",
                    "message": "Workout regeneration failed, will use cached plan",
                    "error": workout_error
                })
        
        # ===== STEP 6: REGENERATE NUTRITION PLAN (ISOLATED) =====
        nutrition_error = None
        if any(k in filtered_profile for k in ['goal', 'weight', 'height', 'age', 'dietary_preference', 'allergies']):
            try:
                logger.info(f"[{request_id}] Starting nutrition regeneration...")
                print(f"[{request_id}] Regenerating nutrition plan...")
                
                # Get workout plan for nutrition calculation (use regenerated or generate fresh)
                workout_for_nutrition = response_data.get("regenerated_workout", {}).get("plan")
                if not workout_for_nutrition:
                    workout_for_nutrition = workout_runtime.generate_weekly_plan(
                        profile=full_profile,
                        workout_history=None
                    )
                
                new_nutrition_plan = meal_runtime.generate_meal_plan(
                    profile=full_profile,
                    weekly_workout_plan=workout_for_nutrition
                )
                
                response_data["regenerated_nutrition"] = {
                    "status": "success",
                    "message": "Nutrition plan regenerated successfully",
                    "plan": new_nutrition_plan,
                    "meals_count": len(new_nutrition_plan.get("meals", []))
                }
                logger.info(f"[{request_id}] Nutrition regeneration completed")
                print(f"[{request_id}] Nutrition regeneration completed")
                
            except Exception as e:
                nutrition_error = str(e)
                logger.error(f"[{request_id}] Nutrition regeneration failed: {e}")
                print(f"[{request_id}] Nutrition regeneration failed: {e}")
                response_data["errors"].append({
                    "type": "nutrition_regeneration",
                    "message": "Nutrition regeneration failed, will use cached plan",
                    "error": nutrition_error
                })
        
        # ===== STEP 6.5: PERSIST PROFILE AND GENERATED PLANS TO MONGODB =====
        try:
            db = get_database()
            users = db.users
            
            # Save profile updates
            await users.update_one(
                {"_id": ObjectId(user_id)},
                {"$set": filtered_profile}
            )
            
            # Save workout plan and week metadata if generated
            if response_data["regenerated_workout"]:
                new_workout = response_data["regenerated_workout"]["plan"]
                week_metadata = _build_week_metadata(
                    new_workout,
                    registration_day_index=_safe_day_index(user_doc.get("firstWorkoutDay")),
                    is_new_user_week=_is_registration_in_current_week(user_doc.get("registrationDate")),
                    existing_metadata=user_doc.get("workoutWeekMetadata"),
                )
                await _persist_workout_plan_and_metadata(
                    {"_id": ObjectId(user_id)},
                    new_workout,
                    week_metadata
                )
                
            # Save nutrition plan if generated
            if response_data["regenerated_nutrition"]:
                new_nutrition = response_data["regenerated_nutrition"]["plan"]
                await users.update_one(
                    {"_id": ObjectId(user_id)},
                    {"$set": {"latestNutritionPlan": new_nutrition, "updatedAt": _utcnow()}}
                )
                
            logger.info(f"[{request_id}] Changes successfully persisted to MongoDB")
            print(f"[{request_id}] Changes successfully persisted to MongoDB")
        except Exception as persist_err:
            logger.error(f"[{request_id}] Failed to persist profile/plans: {persist_err}")
            response_data["errors"].append({
                "type": "database_persistence",
                "message": "Failed to persist profile/plans to database",
                "error": str(persist_err)
            })

        # ===== STEP 7: BUILD SUCCESS RESPONSE =====
        response_data["success"] = True
        response_data["message"] = "Profile updated successfully" if not response_data["errors"] else "Profile updated, but some regenerations failed"
        response_data["data"] = {
            "profile": filtered_profile,
            "user_id": user_id,
            "updated_at": timestamp
        }
        response_data["profile_changes"] = {
            "changed_fields": list(filtered_profile.keys()),
            "workout_regenerated": response_data["regenerated_workout"] is not None,
            "nutrition_regenerated": response_data["regenerated_nutrition"] is not None
        }
        
        # Log final status
        if response_data["errors"]:
            logger.warning(f"[{request_id}] Profile update succeeded with errors")
            print(f"[{request_id}] Profile update succeeded with errors")
        else:
            logger.info(f"[{request_id}] Profile update completed successfully with full regeneration and persistence")
            print(f"[{request_id}] Profile update completed successfully")
        
        print(
            f"[{request_id}] Response summary: "
            f"success={response_data['success']}, "
            f"errors={len(response_data['errors'])}, "
            f"changed_fields={response_data.get('profile_changes', {}).get('changed_fields', [])}"
        )
        print(f"{'='*60}\n")
        
        return response_data
        
    except HTTPException:
        raise
    except ValueError as ve:
        logger.error(f"[{request_id}] Validation error: {ve}")
        raise HTTPException(
            status_code=400,
            detail={"error": "Invalid input data", "message": str(ve), "request_id": request_id}
        )
    except Exception as e:
        logger.error(f"[{request_id}] CRITICAL ERROR: {e}")
        logger.error(f"[{request_id}] Full traceback:\n{traceback.format_exc()}")
        print(f"[{request_id}] CRITICAL ERROR: {e}")
        print(f"[{request_id}] Traceback: {traceback.format_exc()}")
        raise HTTPException(
            status_code=500,
            detail={"error": "Internal server error", "request_id": request_id}
        )


# ==========================================
# GENERATE PLAN ENDPOINT (Called by Frontend ProfileSetup)
# ==========================================


@app.post("/generate-plan")
async def generate_plan(
    profile: dict,
    http_request: Request,
    x_auth_token: Optional[str] = Header(None, alias="x-auth-token"),
):
    """Generate full workout + nutrition plan from profile data"""
    try:
        rl_key = _rate_limit_key(http_request, x_auth_token)
        if not _PLAN_RATE_LIMITER.is_allowed(rl_key):
            raise HTTPException(
                status_code=429,
                detail="Too many plan generation requests. Please wait a moment and try again.",
            )

        workout_runtime = _ensure_workout_engine_ready()
        meal_runtime = _ensure_meal_engine_ready()

        print(f"\n{'='*60}")
        print(f" GENERATE PLAN REQUEST RECEIVED")
        print(f"{'='*60}")
        print("Profile payload received")

        request_id = str(uuid.uuid4())[:8]
        user_id = _require_user_id_from_request(http_request, x_auth_token, request_id)
        print(f"Authenticated user: {user_id}")

        result = {"success": True, "data": {}}

        # Generate workout plan
        try:
            weekly_plan = workout_runtime.generate_weekly_plan(profile)
            result["data"]["workout_plan"] = weekly_plan
            result["data"]["workout_days"] = sum(1 for d in weekly_plan if d.get("type") == "workout")
            result["data"]["rest_days"] = sum(1 for d in weekly_plan if d.get("type") == "rest")
            print(f" Workout plan generated: {result['data']['workout_days']} workout days")
        except Exception as e:
            print(f" Workout generation failed: {e}")
            result["data"]["workout_error"] = "Workout generation failed"

        # Generate nutrition plan — BUG FIX: use generated workout to derive intensity
        try:
            # Derive workout intensity from the generated plan
            generated_workout = result["data"].get("workout_plan", [])
            workout_days_count = sum(1 for d in generated_workout if d.get("type") == "workout")

            # Calculate intensity from exercise volume
            workout_intensity = "moderate"  # default
            if generated_workout:
                total_exercises = sum(
                    len(d.get("exercises", [])) for d in generated_workout if d.get("type") == "workout"
                )
                avg_exercises = total_exercises / max(workout_days_count, 1)
                if avg_exercises >= 8:
                    workout_intensity = "very_hard"
                elif avg_exercises >= 6:
                    workout_intensity = "hard"
                elif avg_exercises >= 3:
                    workout_intensity = "moderate"
                else:
                    workout_intensity = "light"

            print(f"  Derived workout intensity: {workout_intensity} ({workout_days_count} workout days)")

            meal_plan = meal_runtime.suggest_daily_meals(profile, workout_intensity)
            result["data"]["nutrition_plan"] = meal_plan
            result["data"]["workout_intensity"] = workout_intensity
            print(f"  Nutrition plan generated")
        except Exception as e:
            print(f"  Nutrition generation failed: {e}")
            result["data"]["nutrition_error"] = "Nutrition generation failed"

        result["data"]["plan_generated_at"] = _utcnow().isoformat()
        result["message"] = "Plan generated successfully"
        result["timestamp"] = _utcnow().isoformat()

        # Bug #11 fixed: persist the generated plans to MongoDB (best-effort)
        weekly_plan = result["data"].get("workout_plan")
        if user_id and weekly_plan:
            try:
                user_doc = await _find_user_by_id(user_id)
                if user_doc:
                    week_metadata = _build_week_metadata(
                        weekly_plan,
                        registration_day_index=_safe_day_index(
                            (user_doc or {}).get("firstWorkoutDay")
                        ),
                        is_new_user_week=_is_registration_in_current_week(
                            (user_doc or {}).get("registrationDate")
                        ),
                        existing_metadata=(user_doc or {}).get("workoutWeekMetadata"),
                    )
                    await _persist_workout_plan_and_metadata(
                        {"_id": user_doc["_id"]},
                        weekly_plan,
                        week_metadata,
                    )
                    # Also persist nutrition plan
                    nutrition = result["data"].get("nutrition_plan")
                    if nutrition:
                        db_instance = get_database()
                        await db_instance.users.update_one(
                            {"_id": user_doc["_id"]},
                            {"$set": {"latestNutritionPlan": nutrition, "updatedAt": _utcnow()}},
                        )
                    result["data"]["persisted"] = True
                    print(f"  Generated plans persisted for user {user_id}")
            except Exception as persist_err:
                # Non-fatal: plans are still returned to the client
                print(f"  Warning: could not persist plans: {persist_err}")
                result["data"]["persisted"] = False

        print(f" Plan generation complete")
        print(f"{'='*60}\n")

        return result


    except HTTPException:
        raise
    except Exception as e:
        print(f" CRITICAL ERROR in /generate-plan: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail="Internal server error")


# ==========================================
# ERROR HANDLER
# ==========================================


@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "success": False,
            "error": exc.detail,
            "timestamp": _utcnow().isoformat(),
        },
    )


@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    """Catch-all exception handler — logs full details server-side and returns
    a structured error response to help frontend debugging (Bug #33 fix).
    """
    import traceback
    req_id = str(uuid.uuid4())[:8]
    exc_type = type(exc).__name__
    exc_msg = str(exc)[:200]  # Truncate long messages
    logger.error(
        "[%s] Unhandled exception on %s %s\n%s",
        req_id,
        request.method,
        request.url.path,
        traceback.format_exc(),
    )

    return JSONResponse(
        status_code=500,
        content={
            "success": False,
            "error": f"Internal server error: {exc_type}",
            "detail": exc_msg,
            "path": request.url.path,
            "request_id": req_id,
            "timestamp": _utcnow().isoformat(),
        },
    )


# ─────────────────────────────────────────────────────────────────────────────
# Priority 1: Exercise Variation Ladder — POST /api/workout/session-result
# ─────────────────────────────────────────────────────────────────────────────

class SessionResultRequest(BaseModel):
    """Request body for workout session result."""
    exercise_name: str
    correct_reps: int = Field(ge=0, description="Reps with correct form")
    total_reps: int = Field(ge=1, description="Total reps attempted")


@app.post("/api/workout/session-result")
async def workout_session_result(
    request_body: SessionResultRequest,
    http_request: Request,
    x_auth_token: Optional[str] = Header(None, alias="x-auth-token"),
):
    """
    After a set completes, submit the form score and get:
    1. A variation suggestion (progress/regress/maintain)
    2. A progression update (sets/reps/intensity changes)
    """
    req_id = str(uuid.uuid4())[:8]

    try:
        from app.progression_engine import (
            get_exercise_variation_suggestion,
            get_progression_engine,
        )

        form_score = request_body.correct_reps / max(request_body.total_reps, 1)
        form_score = max(0.0, min(1.0, form_score))

        # Get variation suggestion from the exercise dataset
        variation = get_exercise_variation_suggestion(
            exercise_name=request_body.exercise_name,
            form_score=form_score,
        )

        # Get progression update
        user_id = _require_user_id_from_request(http_request, x_auth_token, req_id)

        user_profile = {}
        workout_history = []
        if user_id:
            user_doc = await _find_user_workouts_by_id(user_id, limit=50)
            if user_doc:
                user_profile = {
                    'age': user_doc.get('age', 25),
                    'experience': user_doc.get('experience', 'Beginner'),
                    'consistency': user_doc.get('consistency', 0.7),
                    'streak': user_doc.get('streak', 0),
                    'days_per_week': user_doc.get('days_per_week', 4),
                    'sleep_score': user_doc.get('sleep_score', 7.0),
                    'hydration_score': user_doc.get('hydration_score', 7.0),
                    'stress_level': user_doc.get('stress_level', 5.0),
                }
                workout_history = user_doc.get("workouts", [])

        engine = _ensure_workout_engine_ready()
        exercises_df = engine.exercises_df if engine else None

        progression_engine = get_progression_engine()
        progression_result = progression_engine.compute_progression(
            user_profile=user_profile or {'age': 25, 'experience': 'Beginner'},
            current_params={
                'sets': 3,
                'reps_low': 8,
                'reps_high': 12,
                'intensity': 0.70,
                'exercise_name': request_body.exercise_name
            },
            workout_stats={
                'completion_pct': form_score,
                'fatigue_level': 5.0,
                'form_score': form_score,
            },
            workout_history=workout_history,
            exercises_df=exercises_df
        )

        progression_state = (progression_result.get('metadata') or {}).get('progression_state', {})
        coaching_feedback = progression_engine.generate_structured_coaching_feedback(progression_state, user_profile)

        return {
            "success": True,
            "request_id": req_id,
            "form_score": round(form_score, 3),
            "variation_suggestion": variation,
            "progression_update": progression_result,
            "progression_state": progression_state,
            "coaching_feedback": coaching_feedback,
        }

    except Exception as exc:
        logger.error(f"[{req_id}] session-result error: {exc}")
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail=str(exc))


# ─────────────────────────────────────────────────────────────────────────────
# Priority 3: Daily Log — POST /api/daily-log + GET /api/daily-log/week
# ─────────────────────────────────────────────────────────────────────────────

class DailyLogRequest(BaseModel):
    """Request body for daily check-in."""
    sleep_hours: float = Field(ge=0, le=24)
    water_ml: float = Field(ge=0, le=10000)
    workout_completed: bool = False
    date: Optional[str] = None  # ISO date, defaults to today


@app.post("/api/daily-log")
async def save_daily_log(
    request_body: DailyLogRequest,
    http_request: Request,
    x_auth_token: Optional[str] = Header(None, alias="x-auth-token"),
):
    """Save a daily sleep/water check-in for the adaptive modifier."""
    req_id = str(uuid.uuid4())[:8]

    try:
        user_id = _require_user_id_from_request(http_request, x_auth_token, req_id)

        log_date = request_body.date or _utcnow().strftime("%Y-%m-%d")

        db = get_database()
        daily_logs = db.daily_logs

        # Upsert — one log per user per day
        await daily_logs.update_one(
            {"user_id": user_id, "date": log_date},
            {"$set": {
                "user_id": user_id,
                "date": log_date,
                "sleep_hours": request_body.sleep_hours,
                "water_ml": request_body.water_ml,
                "workout_completed": request_body.workout_completed,
                "updated_at": _utcnow(),
            }},
            upsert=True,
        )

        return {
            "success": True,
            "request_id": req_id,
            "message": f"Daily log saved for {log_date}",
        }

    except HTTPException:
        raise
    except Exception as exc:
        logger.error(f"[{req_id}] daily-log save error: {exc}")
        raise HTTPException(status_code=500, detail=str(exc))


@app.get("/api/daily-log/week")
async def get_weekly_logs(
    http_request: Request,
    x_auth_token: Optional[str] = Header(None, alias="x-auth-token"),
):
    """Get last 7 daily logs for the current user."""
    req_id = str(uuid.uuid4())[:8]

    try:
        user_id = _require_user_id_from_request(http_request, x_auth_token, req_id)

        db = get_database()
        daily_logs = db.daily_logs

        cursor = daily_logs.find(
            {"user_id": user_id},
            {"_id": 0, "user_id": 0},
        ).sort("date", -1).limit(7)

        logs = []
        async for doc in cursor:
            doc.pop("updated_at", None)
            logs.append(doc)

        # Compute weekly averages
        if logs:
            avg_sleep = sum(l.get("sleep_hours", 0) for l in logs) / len(logs)
            avg_water = sum(l.get("water_ml", 0) for l in logs) / len(logs)
            completed = sum(1 for l in logs if l.get("workout_completed"))
        else:
            avg_sleep = 0
            avg_water = 0
            completed = 0

        # Calculate biometrics adaptive modifier reasoning
        from app.adaptive_modifier import compute_adaptive_modifiers
        adaptive_mods = compute_adaptive_modifiers(logs) if logs else {}

        return {
            "success": True,
            "request_id": req_id,
            "logs": logs,
            "summary": {
                "days_logged": len(logs),
                "avg_sleep_hours": round(avg_sleep, 1),
                "avg_water_ml": round(avg_water),
                "workout_completion_rate": round(completed / max(len(logs), 1), 2),
                "adaptive_reason": adaptive_mods.get('reason', 'Baseline — all biometrics normal.'),
                "deload_flag": adaptive_mods.get('deload_flag', False),
                "dehydration_flag": adaptive_mods.get('dehydration_flag', False),
                "intensity_delta": adaptive_mods.get('intensity_delta', 0.0),
            },
        }

    except HTTPException:
        raise
    except Exception as exc:
        logger.error(f"[{req_id}] daily-log week error: {exc}")
        raise HTTPException(status_code=500, detail=str(exc))


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("server:app", host="0.0.0.0", port=8000, reload=True, log_level="info")

