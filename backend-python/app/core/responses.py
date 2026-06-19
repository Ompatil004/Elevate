from datetime import datetime, timezone
from typing import Dict, Any, Optional

def _utcnow() -> datetime:
    """Return naive UTC datetime without using deprecated utcnow()."""
    return datetime.now(timezone.utc).replace(tzinfo=None)

def api_success(message: str, data: Optional[Dict[str, Any]] = None, **extra: Any) -> Dict[str, Any]:
    """Standard success envelope while retaining backward-compatible top-level fields."""
    payload: Dict[str, Any] = {
        "success": True,
        "message": message,
        "data": data or {},
        "timestamp": _utcnow().isoformat(),
    }
    payload.update(extra)
    return payload
