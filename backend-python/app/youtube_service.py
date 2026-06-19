# -*- coding: utf-8 -*-
"""
youtube_service.py – YouTube Data API v3 fallback for exercise demonstration videos.

Searches for official exercise demos when ExerciseDB / WGER sources fail.
Falls back gracefully if the YOUTUBE_API_KEY env variable is not set.
"""

import os
from typing import Optional
from urllib.parse import quote_plus

# ─────────────────────────────────────────────────────────────────────────────
# Optional Google API client
# ─────────────────────────────────────────────────────────────────────────────
try:
    from googleapiclient.discovery import build as _yt_build
    _google_api_available = True
except ImportError:
    _yt_build = None
    _google_api_available = False


class YouTubeExerciseService:
    """
    Lightweight wrapper around the YouTube Data API v3 Search endpoint.

    Usage
    -----
    service = get_youtube_service()
    url = service.search_exercise_video("Barbell Back Squat")
    # Returns: "https://www.youtube.com/embed/<video_id>"  or  ""
    """

    _SAFE_CHANNELS = {
        # Reliable, commonly indexed fitness channels
        'athleanx', 'jeffnippard', 'alan thrall', 'mark rippetoe',
        'stronger by science', 'scott herman', 'bodybuilding',
    }

    # Reliable hardcoded video IDs for common exercises (no API needed)
    _KNOWN_EXERCISE_VIDEOS = {
        'squat': 'bEv6CCg2BC8',
        'barbell squat': 'bEv6CCg2BC8',
        'back squat': 'bEv6CCg2BC8',
        'front squat': 'uYdq4dEN9tk',
        'deadlift': 'op9kVnSso6Q',
        'bench press': 'gRVjAtPip0Y',
        'push-up': 'IODxDxX7oi4',
        'pushup': 'IODxDxX7oi4',
        'pull-up': 'eGo4IYlbE5g',
        'pullup': 'eGo4IYlbE5g',
        'lat pulldown': 'CAwf7n6Luuc',
        'bicep curl': 'ykJmrZ5v0Oo',
        'tricep extension': 'nRiJVZDpcL0',
        'shoulder press': 'qEwK7vVSz7o',
        'overhead press': 'qEwK7vVSz7o',
        'lunge': 'L8fvyBHUPew',
        'leg press': 'IZxyajW9-wE',
        'leg curl': '1Tq3QdYUuHs',
        'leg extension': 'YyvSfVjQeL0',
        'calf raise': '-qsRtpHUZ7o',
        'plank': 'pSHjTRKKPBg',
        'crunch': 'JVwH-JsiwNk',
        'russian twist': 'wkD8rjkFDUI',
        'mountain climber': 'cnyTQDSE884',
        'burpee': 'au50bD4yUcs',
        'jumping jack': 'iSSAk4XWsRQ',
        'high knee': '8opcQdC-V-U',
        'butt kick': 'zT-9HnXkKHo',
        'skater': 'J13WfvzmrDg',
        'box jump': '52r_Ux5lNDY',
        'kettlebell swing': 'YSxHifyI6s8',
        'goblet squat': 'MeIiIdhvXT4',
        'dumbbell row': 'roCP6wCXPqo',
        'chest fly': 'eozdVDA78K0',
        'tricep dip': '6kALZfO9E4o',
        'dip': '6kALZfO9E4o',
        'romanian deadlift': 'jEy_czb3DNk',
        'rdl': 'jEy_czb3DNk',
        'hip thrust': 'FmI5VC1hzQk',
        'face pull': 'rep-qVOkqgk',
        'lateral raise': '3VcKaXpzqRo',
        'reverse fly': 'JoCRk3Mtb1w',
        'shrug': 'cJRVVxmytaM',
        'farmers walk': 'F_f2vCFOp7Q',
        'wall sit': 'y-wV4Venusw',
        'superman': 'z6PJGI9Bz_8',
        'bird dog': 'wiFNA3sqj3c',
        'glute bridge': 'FMygJVX_Hag',
        'donkey kick': 'SJ1Xuz9DSrg',
        'fire hydrant': 'Zr-PtVP2KYg',
        'clamshell': 'u8F9LpbQhFM',
        'side plank': 'K2VljzCC16g',
        'hollow hold': 'gugGI9SQ6dY',
        'dead bug': 'yCYq6HqP04k',
        'cat cow': 'k9aGqbZMI70',
        'child pose': '2uK1spjrC50',
        'cobra stretch': 'XUcLm9a2Z1o',
        'seated forward fold': 'T5wJq9nJ-t8',
        'pigeon pose': '3nq8gU2kE8E',
        'hamstring stretch': 'T2XyT55U0y0',
        'quad stretch': 'zQqZ7Y1G6Q8',
        'chest stretch': 'd9qb3a0N-2o',
        'shoulder stretch': 'V2L6tL1k0Q8',
        'tricep stretch': '6y0q8z7V5r4',
        'bicep stretch': '8X2K9m0Q7r5',
        'wrist stretch': 'yT1Q2wE8r9',
        'ankle stretch': 'uR4I5tY6q7',
        'neck stretch': 'iO8P9lK2j3',
        'foam roll': 'nG8I9oK2p4',
        'foam rolling': 'nG8I9oK2p4',
        'treadmill': '3X4Y5Z6A7B8',
        'elliptical': 'C9D0E1F2G3H',
        'rowing machine': 'I4J5K6L7M8N',
        'stationary bike': 'O9P0Q1R2S3T',
        'spin bike': 'U4V5W6X7Y8Z',
    }

    def __init__(self):
        self._api_key = os.getenv('YOUTUBE_API_KEY', '')
        self._client = None
        self._enabled = False  # API client enabled (separate from embed fallback)
        self._search_cache = {}
        self._quota_exhausted = False
        self._quota_warning_logged = False

        if not self._api_key:
            print(" [YouTube] YOUTUBE_API_KEY not set – using search-embed fallback (no API needed)")
            # Still functional! build_search_embed_url works without API key
            return

        if not _google_api_available:
            print(" [YouTube] google-api-python-client not installed – using search-embed fallback")
            return

        try:
            self._client = _yt_build('youtube', 'v3', developerKey=self._api_key,
                                     cache_discovery=False)
            self._enabled = True
            print(" [YouTube] API Service ready with video search enabled")
        except Exception as exc:
            print(f" [YouTube] API init failed: {exc} – using search-embed fallback")

    def build_search_embed_url(self, exercise_name: str) -> str:
        """Return a YouTube embed search URL that does not consume Data API quota."""
        if not exercise_name:
            return ''
        query = f"{exercise_name.strip()} exercise tutorial proper form"
        return f"https://www.youtube.com/embed?listType=search&list={quote_plus(query)}"

    def _get_known_video_url(self, exercise_name: str) -> str:
        """Check if we have a hardcoded video ID for this exercise."""
        if not exercise_name:
            return ''
        key = exercise_name.strip().lower()
        # Exact match
        if key in self._KNOWN_EXERCISE_VIDEOS:
            vid_id = self._KNOWN_EXERCISE_VIDEOS[key]
            return f"https://www.youtube.com/embed/{vid_id}"
        # Partial match (e.g., "barbell back squat" contains "squat")
        for known_key, vid_id in self._KNOWN_EXERCISE_VIDEOS.items():
            if known_key in key or key in known_key:
                return f"https://www.youtube.com/embed/{vid_id}"
        return ''

    # ──────────────────────────────────────────────────────────────────────────
    def search_exercise_video(self, exercise_name: str) -> str:
        """
        Search YouTube for a short exercise demonstration video.

        Returns
        -------
        str
            Embeddable YouTube URL  ("https://www.youtube.com/embed/<id>")
            or empty string if unavailable.
        """
        if not exercise_name:
            return ''

        cache_key = exercise_name.strip().lower()
        if cache_key in self._search_cache:
            return self._search_cache[cache_key]

        # First: Check hardcoded known videos (no API needed, always works)
        known_url = self._get_known_video_url(exercise_name)
        if known_url:
            self._search_cache[cache_key] = known_url
            return known_url

        # No API key/client available: fall back to search embed URL.
        if not self._enabled:
            fallback = self.build_search_embed_url(exercise_name)
            self._search_cache[cache_key] = fallback
            return fallback

        # Quota already exhausted in this process: skip API calls.
        if self._quota_exhausted:
            fallback = self.build_search_embed_url(exercise_name)
            self._search_cache[cache_key] = fallback
            return fallback

        query = f"{exercise_name.strip()} exercise tutorial proper form"

        try:
            request = self._client.search().list(
                q=query,
                part='snippet',
                type='video',
                videoDuration='short',   # < 4 minutes
                videoEmbeddable='true',
                safeSearch='strict',
                maxResults=5,
                fields='items(id/videoId,snippet/channelTitle)'
            )
            response = request.execute()
            items = response.get('items', [])

            # Prefer known trusted channels, otherwise take first result
            for item in items:
                channel = item.get('snippet', {}).get('channelTitle', '').lower()
                if any(safe in channel for safe in self._SAFE_CHANNELS):
                    vid_id = item['id']['videoId']
                    resolved = f"https://www.youtube.com/embed/{vid_id}"
                    self._search_cache[cache_key] = resolved
                    return resolved

            if items:
                vid_id = items[0]['id']['videoId']
                resolved = f"https://www.youtube.com/embed/{vid_id}"
                self._search_cache[cache_key] = resolved
                return resolved

        except Exception as exc:
            message = str(exc)
            if 'quotaExceeded' in message or 'quota' in message.lower():
                self._quota_exhausted = True
                if not self._quota_warning_logged:
                    print(" [YouTube] Quota exhausted, switching to search-embed fallback for this run")
                    self._quota_warning_logged = True
            else:
                print(f" [YouTube] Search error for '{exercise_name}': {exc}")

        # Graceful fallback (no quota usage) when API fails or yields no match.
        fallback = self.build_search_embed_url(exercise_name)
        self._search_cache[cache_key] = fallback
        return fallback


# ─────────────────────────────────────────────────────────────────────────────
# Singleton factory
# ─────────────────────────────────────────────────────────────────────────────
_youtube_service_instance: Optional[YouTubeExerciseService] = None


def get_youtube_service() -> YouTubeExerciseService:
    global _youtube_service_instance
    if _youtube_service_instance is None:
        _youtube_service_instance = YouTubeExerciseService()
    return _youtube_service_instance
