# -*- coding: utf-8 -*-
"""
plan_cache.py – In-memory (+ optional Redis) caching for generated workout plans.

Key   : hash(user_id + goal + experience + equipment + body_issues + days_per_week + streak + consistency + ISO week number)
TTL   : 7 days (plans expire weekly so a new plan is generated each week)
Redis : Optional – falls back gracefully to pure in-memory dict if redis is unavailable.
"""

import hashlib
import json
import time
import os
from datetime import datetime
from typing import Optional, Dict


# ─────────────────────────────────────────────────────────────────────────────
# Optional Redis import
# ─────────────────────────────────────────────────────────────────────────────
try:
    import redis as _redis_lib
    _redis_available = True
except ImportError:
    _redis_lib = None
    _redis_available = False


class PlanCache:
    """
    Two-level plan cache:
      Level 1: in-process dict (fast, zero-latency)
      Level 2: Redis (optional, survives process restarts)
    """

    DEFAULT_TTL = 7 * 24 * 60 * 60  # 7 days in seconds
    CACHE_SCHEMA_VERSION = '2026-06-19-workout-diversity-v5'

    def __init__(self, redis_host: str = 'localhost', redis_port: int = 6379,
                 redis_db: int = 0, ttl: int = DEFAULT_TTL):
        self._memory: Dict[str, dict] = {}          # { key: {'plan': ..., 'expires_at': float} }
        self._ttl = ttl
        self._redis = None

        if _redis_available:
            try:
                connect_timeout = float(os.getenv("PLAN_CACHE_REDIS_CONNECT_TIMEOUT", "0.3"))
                io_timeout = float(os.getenv("PLAN_CACHE_REDIS_SOCKET_TIMEOUT", "0.3"))
                client = _redis_lib.Redis(
                    host=redis_host, port=redis_port, db=redis_db,
                    socket_connect_timeout=connect_timeout,
                    socket_timeout=io_timeout,
                )
                self._redis = client
                print(f" [PlanCache] Redis client enabled for {redis_host}:{redis_port} (lazy connect)")
            except Exception as exc:
                print(f" [PlanCache] Redis unavailable ({exc}), using in-memory only")

    def _disable_redis(self, reason: str) -> None:
        if self._redis is not None:
            print(f" [PlanCache] Redis disabled after runtime error: {reason}")
        self._redis = None

    # ─────────────────────────────────────────────────────────────────────────
    # Key generation
    # ─────────────────────────────────────────────────────────────────────────
    def _generate_key(self, profile: dict, week_offset: int = 0) -> str:
        """Deterministic cache key from stable profile fields + ISO-week number."""
        key_data = {
            'cache_schema': self.CACHE_SCHEMA_VERSION,
            'user_id':      profile.get('user_id') or profile.get('email', 'anon'),
            'goal':         profile.get('goal', ''),
            'experience':   profile.get('experience', ''),
            'equipment':    sorted(profile.get('equipment', [])),
            'body_issues':  sorted(profile.get('body_issues', [])),
            'days_per_week': int(profile.get('days_per_week', 4)),
            'streak':       int(profile.get('streak', 0) or 0),
            'consistency':  round(float(profile.get('consistency', 0.0) or 0.0), 3),
            # Bug fix: Include body metrics in cache key so weight/height/age
            # changes produce a new plan instead of returning stale cached plan
            'weight':       round(float(profile.get('weight', 70) or 70), 1),
            'height':       round(float(profile.get('height', 170) or 170), 1),
            'age':          int(profile.get('age', 25) or 25),
            'gender':       str(profile.get('gender', '')).lower().strip(),
            'week':         datetime.now().isocalendar()[1] + week_offset,
            'year':         datetime.now().isocalendar()[0],
        }
        key_str = json.dumps(key_data, sort_keys=True)
        return f"workout_plan:{hashlib.md5(key_str.encode()).hexdigest()}"

    # ─────────────────────────────────────────────────────────────────────────
    # Public API
    # ─────────────────────────────────────────────────────────────────────────
    def get(self, profile: dict) -> Optional[Dict]:
        """Return cached plan, or None if missing/expired."""
        key = self._generate_key(profile)

        # Level 1 – memory
        entry = self._memory.get(key)
        if entry and time.time() < entry['expires_at']:
            print(f" [PlanCache] Memory HIT for {key[:16]}…")
            return entry['plan']

        # Level 2 – Redis
        if self._redis:
            try:
                raw = self._redis.get(key)
                if raw:
                    plan = json.loads(raw)
                    # Warm L1
                    self._memory[key] = {
                        'plan': plan,
                        'expires_at': time.time() + self._ttl
                    }
                    print(f" [PlanCache] Redis HIT for {key[:16]}…")
                    return plan
            except Exception as exc:
                self._disable_redis(f"GET failed ({exc})")

        print(f" [PlanCache] MISS for {key[:16]}…")
        return None

    def set(self, profile: dict, plan: dict) -> None:
        """Store plan in both levels."""
        key = self._generate_key(profile)
        expires_at = time.time() + self._ttl

        # Level 1
        self._memory[key] = {'plan': plan, 'expires_at': expires_at}

        # Level 2
        if self._redis:
            try:
                self._redis.setex(key, self._ttl, json.dumps(plan))
            except Exception as exc:
                self._disable_redis(f"SET failed ({exc})")

        print(f" [PlanCache] Stored plan for {key[:16]}… (TTL={self._ttl}s)")

    def invalidate(self, profile: dict) -> None:
        """Remove cached plan for a profile (call after profile change)."""
        key = self._generate_key(profile)
        self._memory.pop(key, None)
        if self._redis:
            try:
                self._redis.delete(key)
            except Exception as exc:
                self._disable_redis(f"DELETE failed ({exc})")
        print(f" [PlanCache] Invalidated {key[:16]}…")

    def clear_all(self) -> None:
        """Clear all in-memory entries (Redis keys survive process lifetime)."""
        self._memory.clear()


# ─────────────────────────────────────────────────────────────────────────────
# Singleton factory
# ─────────────────────────────────────────────────────────────────────────────
_plan_cache_instance: Optional[PlanCache] = None


def get_plan_cache() -> PlanCache:
    global _plan_cache_instance
    if _plan_cache_instance is None:
        _plan_cache_instance = PlanCache()
    return _plan_cache_instance
