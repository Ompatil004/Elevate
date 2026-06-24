# -*- coding: utf-8 -*-
import json
import pandas as pd
import numpy as np
import os
import re
import time
import copy
import threading
import hashlib
from datetime import datetime, timezone
from difflib import SequenceMatcher
from urllib.parse import quote_plus
from typing import List, Dict, Set, Optional
import joblib
import requests
from .feature_pipeline import FeaturePipeline
from .multi_output_xgboost_model import MultiOutputXGBoostModel
from .hybrid_volume_optimizer import HybridVolumeOptimizer, get_hybrid_optimizer

# Import progression engine
try:
    from .progression_engine import (
        get_progression_engine,
        apply_age_safety_caps as prog_age_caps,
        get_age_modifiers,
        build_form_feedback,
    )
except ImportError:
    get_progression_engine = None
    prog_age_caps = None
    get_age_modifiers = None
    build_form_feedback = None

try:
    from .gemini_service import generate_workout_config, is_gemini_available
except ImportError:
    generate_workout_config = None
    is_gemini_available = None

# Issue #3 – YouTube video fallback
try:
    from .youtube_service import get_youtube_service as _get_yt
except ImportError:
    _get_yt = None

# Issue #4 – plan caching
try:
    from .plan_cache import get_plan_cache as _get_cache
except ImportError:
    _get_cache = None


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)
from .services.exercise_metadata import get_movement_pattern



class WorkoutEngine:
    def __init__(self):
        print("\n[WORKOUT] Initializing WorkoutEngine...")

        # Initialize feature pipeline
        self.feature_pipeline = FeaturePipeline()

        # Media URL reliability cache (avoid repeated dead-link checks)
        self._media_url_cache = {}
        self._media_cache_ttl_seconds = 6 * 60 * 60
        self._media_check_timeout = 2.5
        self._wger_name_to_media = {}
        self._wger_media_to_names = {}
        self._wger_video_name_cache = {}
        self._audit_name_to_media = {}
        self._audit_media_index_ready = False
        self._wger_index_ready = False
        # BUG-P8 fix: Event that is set once _lazy_load_wger finishes.
        # Callers that need WGER GIFs can do: engine._wger_ready_event.wait(timeout=5)
        self._wger_ready_event = threading.Event()
        # Exercises confirmed to have no matching GIF — must not use random fallbacks.
        self._gif_blacklist: set = set()
        
        # Initialize multi-output XGBoost model
        self.multi_output_model = MultiOutputXGBoostModel()
        
        # Initialize progression engine
        self.progression_engine = get_progression_engine() if get_progression_engine else None
        if self.progression_engine:
            print(" ProgressionEngine loaded - multi-factor overload active")
        
        # Get base directory
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        exercises_home_v1    = os.path.join(base_dir, 'data', 'exercises_home_v1.csv')
        exercises_processed_repaired = os.path.join(base_dir, 'data', 'exercises_processed_repaired.csv')
        exercises_processed = os.path.join(base_dir, 'data', 'exercises_processed.csv')
        exercises_raw = os.path.join(base_dir, 'data', 'exercises.csv')

        # HOME_WORKOUT_ONLY mode: load home dataset first (fail-fast if missing)
        _home_only_mode = str(os.environ.get('HOME_WORKOUT_ONLY', 'true')).strip().lower() in ('1', 'true', 'yes', 'on')

        # Load exercises from CSV or create fallback
        try:
            if _home_only_mode and os.path.exists(exercises_home_v1):
                self.exercises_df = pd.read_csv(exercises_home_v1)
                print(f" [HOME MODE] Loaded {len(self.exercises_df)} exercises from home-only CSV (exercises_home_v1.csv)")
                # Standardize column names to TitleCase format to match expected format
                self.exercises_df.columns = self.exercises_df.columns.str.strip().str.title().str.replace(' ', '_')
            else:
                # If _home_only_mode is True but exercises_home_v1.csv is missing, OR if _home_only_mode is False,
                # load the standard processed/raw files and filter them in memory if _home_only_mode is True.
                if os.path.exists(exercises_processed_repaired):
                    self.exercises_df = pd.read_csv(exercises_processed_repaired)
                    print(f" Loaded {len(self.exercises_df)} exercises from repaired processed CSV")
                elif os.path.exists(exercises_processed):
                    self.exercises_df = pd.read_csv(exercises_processed)
                    print(f" Loaded {len(self.exercises_df)} exercises from processed CSV")
                elif os.path.exists(exercises_raw):
                    self.exercises_df = pd.read_csv(exercises_raw)
                    print(f" Loaded {len(self.exercises_df)} exercises from raw CSV")
                else:
                    # Fallback exercises
                    print(" CSV files not found, using fallback exercises")
                    self.exercises_df = pd.DataFrame({
                        'Name': [
                            'Push-ups', 'Squats', 'Deadlifts', 'Bench Press',
                            'Dumbbell Rows', 'Pull-ups', 'Lunges', 'Plank',
                            'Bicep Curls', 'Tricep Dips', 'Shoulder Press', 'Leg Press',
                            'Lat Pulldown', 'Chest Fly', 'Leg Curl', 'Calf Raises'
                        ],
                        'Target_Muscle': [
                            'Chest', 'Legs', 'Back', 'Chest',
                            'Back', 'Back', 'Legs', 'Core',
                            'Arms', 'Arms', 'Shoulders', 'Legs',
                            'Back', 'Chest', 'Legs', 'Legs'
                        ],
                        'Equipment': [
                            'Body Weight', 'Body Weight', 'Barbell', 'Barbell',
                            'Dumbbell', 'Body Weight', 'Body Weight', 'Body Weight',
                            'Dumbbell', 'Body Weight', 'Dumbbell', 'Machine',
                            'Machine', 'Dumbbell', 'Machine', 'Body Weight'
                        ],
                        'Avoid_If': [
                            'None', 'Knee Issues', 'Back Issues', 'Shoulder Issues',
                            'None', 'Shoulder Issues', 'Knee Issues', 'None',
                            'None', 'Shoulder Issues', 'Shoulder Issues', 'Knee Issues',
                            'None', 'Shoulder Issues', 'None', 'None'
                        ],
                        'Check_Type': ['strength'] * 16,
                        'Risk_Level': ['Low', 'Medium', 'High', 'High', 'Medium', 'Medium', 'Medium', 'Low', 'Low', 'Low', 'Medium', 'Medium', 'Medium', 'Low', 'Low', 'Low'],
                        'Progression_Next': [''] * 16,
                        'Alternative_Swap': [''] * 16
                    })

                # Standardize column names
                self.exercises_df.columns = self.exercises_df.columns.str.strip().str.title().str.replace(' ', '_')

                # Apply home equipment filter in memory if in home-only mode and loaded full CSV
                if _home_only_mode:
                    HOME_EQUIPMENT_VALUES = {
                        'body weight', 'bodyweight', 'dumbbell', 'band', 'resistance band',
                        'kettlebell', 'medicine ball', 'stability ball', 'bosu ball', 'roller',
                        'wheel roller', 'rope', 'weighted', 'none', 'no equipment', 'assisted'
                    }
                    if 'Equipment' in self.exercises_df.columns:
                        before_cnt = len(self.exercises_df)
                        self.exercises_df = self.exercises_df[
                            self.exercises_df['Equipment'].str.lower().str.strip().isin(HOME_EQUIPMENT_VALUES)
                        ]
                        print(f" [HOME MODE FILTER] Filtered dataset from {before_cnt} to {len(self.exercises_df)} home-friendly exercises.")

            # Fill missing values
            fill_values = {
                'Avoid_If': 'None',
                'Check_Type': 'strength',
                'Progression_Next': '',
                'Alternative_Swap': ''
            }

            for col, val in fill_values.items():
                if col in self.exercises_df.columns:
                    self.exercises_df[col] = self.exercises_df[col].fillna(val)

        except Exception as e:
            print(f" Error loading exercises: {e}")
            raise

        # Load ML models
        self.xgb_volume_model = None
        self.xgb_intensity_model = None
        self.xgb_split_model = None
        self.xgb_frequency_model = None
        self.xgb_sets_model = None
        self.xgb_reps_model = None
        self.xgb_rest_model = None
        self.xgb_progression_model = None
        self.le_goal = None
        self.le_experience = None
        self._load_ml_models()

        if all(m is None for m in [self.xgb_volume_model, self.xgb_intensity_model, self.xgb_split_model]) and self.multi_output_model.model is None:
            print(" ML models unavailable - using validated rule-based fallback")
        
        # Initialize hybrid optimizer (rule-based + ML hooks + user adaptation)
        self.hybrid_optimizer = get_hybrid_optimizer()

        # Issue #4 – Load WGER in a background thread so __init__ returns quickly
        self._wger_thread = threading.Thread(
            target=self._lazy_load_wger, daemon=True, name="wger-media-loader"
        )
        self._wger_thread.start()

        # Issue #3 – YouTube service (lazy singleton, opt-in only)
        # Keep disabled by default because GIF/image fallbacks now cover all exercises.
        enable_youtube_fallback = str(os.getenv('ENABLE_YOUTUBE_FALLBACK', '0')).strip().lower() in ('1', 'true', 'yes', 'on')
        self._youtube_fallback_enabled = enable_youtube_fallback
        self._youtube_svc = _get_yt() if (enable_youtube_fallback and _get_yt) else None
        if not enable_youtube_fallback:
            print(" [YouTube] Fallback disabled (set ENABLE_YOUTUBE_FALLBACK=1 to enable)")

        # Issue #4 – plan cache (lazy singleton)
        self._plan_cache = _get_cache() if _get_cache else None

        # High-confidence exact/fuzzy mappings harvested from local audit output.
        self._initialize_audit_media_index(base_dir)

        # Load GIF blacklist — exercises with no valid exercise-specific media.
        self._load_gif_blacklist(base_dir)

        print(f" WorkoutEngine initialized successfully!\n")

    def _lazy_load_wger(self):
        """Background thread: build WGER media index without blocking startup."""
        try:
            self._initialize_wger_media_index()
        except Exception as e:
            print(f" [WGER-bg] Media index load failed: {e}")

    def _normalize_exercise_name(self, name: str) -> str:
        if not name:
            return ''
        value = str(name).lower().strip()
        value = re.sub(r'\([^)]*\)', ' ', value)
        value = re.sub(r'[^a-z0-9\s]', ' ', value)
        value = re.sub(r'\s+', ' ', value).strip()
        stop_words = {'with', 'and', 'the', 'a', 'an'}
        parts = [p for p in value.split(' ') if p and p not in stop_words]
        return ' '.join(parts)

    def _create_user_entropy(self, profile: dict) -> str:
        parts = [
            str(profile.get('user_id') or '').strip(),
            str(profile.get('email') or '').strip().lower(),
            str(profile.get('created_at') or profile.get('createdAt') or '').strip(),
            str(profile.get('registrationDate') or profile.get('registration_date') or '').strip(),
        ]
        base = '|'.join(parts)
        if not base.replace('|', '').strip():
            base = 'anonymous-user'
        return hashlib.sha256(base.encode()).hexdigest()[:24]

    def _create_profile_fingerprint(self, profile: dict) -> str:
        payload = {
            'age': int(float(profile.get('age', 25) or 25)),
            'weight': round(float(profile.get('weight', 70.0) or 70.0), 1),
            'height': round(float(profile.get('height', 175.0) or 175.0), 1),
            'goal': str(profile.get('goal', 'Muscle Gain')),
            'experience': str(profile.get('experience', 'Beginner')),
            'days_per_week': int(profile.get('days_per_week', 4) or 4),
            'equipment': sorted([str(x).strip().lower() for x in (profile.get('equipment') or [])]),
            'body_issues': sorted([str(x).strip().lower() for x in (profile.get('body_issues') or [])]),
        }
        payload_str = json.dumps(payload, sort_keys=True, separators=(',', ':'))
        return hashlib.sha256(payload_str.encode()).hexdigest()[:24]

    def _build_day_seed(self, profile: dict, focus: str, day_idx: int) -> int:
        user_id = str(profile.get('user_id', 'default'))
        week_offset = int(profile.get('week_offset', 0) or 0)
        entropy = self._create_user_entropy(profile)
        fingerprint = self._create_profile_fingerprint(profile)
        seed_str = f"{user_id}:{entropy}:{fingerprint}:{focus}:{day_idx}:{week_offset}"
        return int(hashlib.sha256(seed_str.encode()).hexdigest(), 16)

    def _build_intensity_metrics(self, intensity_data) -> Dict:
        """Build intensity metrics dict for workout day.
        
        Accepts either:
        - Dict with comprehensive metrics (from new _calculate_day_intensity)
        - Float score (legacy, for backward compatibility)
        """
        # Handle legacy float input
        if isinstance(intensity_data, (int, float)):
            score = max(0.0, min(1.0, float(intensity_data)))
            calorie_multiplier = round(0.90 + (score * 0.35), 2)
            if score <= 0.05:
                category = 'rest'
            elif score < 0.35:
                category = 'light'
            elif score < 0.65:
                category = 'moderate'
            elif score < 0.85:
                category = 'hard'
            else:
                category = 'very_hard'
            return {
                'intensity_score': round(score, 2),
                'volume_load': 0,
                'calorie_multiplier': calorie_multiplier,
                'category': category,
            }
        
        # Handle new Dict input
        return {
            'intensity_score': intensity_data.get('intensity_score', 0.0),
            'volume_load': intensity_data.get('volume_load', 0),
            'calorie_multiplier': intensity_data.get('calorie_multiplier', 1.0),
            'category': intensity_data.get('category', 'moderate'),
        }

    def _extract_movement_tokens(self, value: str) -> set:
        """Return canonical movement tokens for strict name matching."""
        tokens = set(self._normalize_exercise_name(value).split())
        if not tokens:
            return set()

        movement_aliases = {
            'squat': {'squat', 'squats', 'cossack', 'lunge', 'lunges', 'split', 'stepup', 'step', 'adduction', 'abduction'},
            'hinge': {'hinge', 'deadlift', 'rdl', 'goodmorning', 'good', 'morning', 'thrust'},
            'push': {'push', 'pushup', 'press', 'bench', 'dip', 'dips'},
            'pull': {'pull', 'pullup', 'chinup', 'row', 'pulldown'},
            'curl': {'curl', 'curls', 'biceps', 'hammer'},
            'extension': {'extension', 'extensions', 'triceps', 'kickback'},
            'raise': {'raise', 'raises', 'lateral', 'front'},
            'plank': {'plank', 'hollow', 'stability'},
            'crunch': {'crunch', 'situp', 'twist', 'rotation'},
            'bridge': {'bridge', 'glute', 'hip'},
            'jump': {'jump', 'plyo', 'burpee', 'hop'},
            'walk': {'walk', 'walkout', 'crawl', 'march', 'jog', 'run'},
            'mobility': {'mobility', 'stretch', 'circles', 'swing', 'warmup', 'warm'},
        }

        matched = set()
        for canonical, aliases in movement_aliases.items():
            if tokens.intersection(aliases):
                matched.add(canonical)
        return matched

    def _name_similarity_score(self, source_name: str, candidate_name: str) -> float:
        source = self._normalize_exercise_name(source_name)
        candidate = self._normalize_exercise_name(candidate_name)
        if not source or not candidate:
            return 0.0

        src_tokens = set(source.split())
        cand_tokens = set(candidate.split())
        if not src_tokens or not cand_tokens:
            return 0.0

        shared_tokens = src_tokens.intersection(cand_tokens)
        token_overlap = len(shared_tokens) / max(len(src_tokens), len(cand_tokens), 1)
        seq_ratio = SequenceMatcher(None, source, candidate).ratio()

        src_moves = self._extract_movement_tokens(source)
        cand_moves = self._extract_movement_tokens(candidate)
        if src_moves and cand_moves:
            move_overlap = len(src_moves.intersection(cand_moves)) / max(len(src_moves), len(cand_moves), 1)
        elif src_moves or cand_moves:
            move_overlap = 0.0
        else:
            move_overlap = 1.0 if shared_tokens else 0.0

        score = (0.45 * token_overlap) + (0.35 * seq_ratio) + (0.20 * move_overlap)
        if src_moves and cand_moves and not src_moves.intersection(cand_moves):
            score *= 0.6
        return score

    def _is_confident_name_match(self, source_name: str, candidate_name: str, strict: bool = True) -> bool:
        source = self._normalize_exercise_name(source_name)
        candidate = self._normalize_exercise_name(candidate_name)
        if not source or not candidate:
            return False

        if source == candidate:
            return True

        src_tokens = set(source.split())
        cand_tokens = set(candidate.split())
        shared_count = len(src_tokens.intersection(cand_tokens))

        src_moves = self._extract_movement_tokens(source)
        cand_moves = self._extract_movement_tokens(candidate)
        if src_moves and cand_moves and not src_moves.intersection(cand_moves):
            return False

        score = self._name_similarity_score(source, candidate)
        min_score = 0.74 if strict else 0.62
        if shared_count >= 2 and score >= (min_score - 0.08):
            return True
        return score >= min_score

    def _extract_wger_video_id(self, video_url: str) -> Optional[int]:
        if not video_url:
            return None
        match = re.search(r'/exercise-video/(\d+)/', str(video_url))
        if not match:
            return None
        try:
            return int(match.group(1))
        except Exception:
            return None

    def _get_wger_exercise_name_by_id(self, exercise_id: int) -> str:
        if not exercise_id:
            return ''

        cached = self._wger_video_name_cache.get(exercise_id)
        if cached is not None:
            return cached

        resolved_name = ''
        try:
            endpoint = f'https://wger.de/api/v2/exerciseinfo/{exercise_id}/'
            resp = requests.get(endpoint, timeout=8)
            if resp.status_code < 400:
                payload = resp.json() or {}
                resolved_name = self._extract_wger_name(payload)
        except Exception:
            resolved_name = ''

        self._wger_video_name_cache[exercise_id] = resolved_name
        return resolved_name

    def _is_wger_video_url_compatible(self, video_url: str, exercise_name: str) -> bool:
        """Accept WGER video fallback only when its canonical exercise name matches."""
        if not video_url:
            return False

        clean = str(video_url).strip().lower()
        if '/exercise-video/' not in clean or 'wger.de' not in clean:
            return True

        exercise_id = self._extract_wger_video_id(video_url)
        if not exercise_id:
            return False

        canonical_name = self._get_wger_exercise_name_by_id(exercise_id)
        if not canonical_name:
            return False

        return self._is_confident_name_match(exercise_name, canonical_name, strict=False)

    def _load_gif_blacklist(self, base_dir: Optional[str] = None) -> None:
        """Load gif_blacklist.json built by build_exercise_gif_map.py."""
        try:
            resolved_base = base_dir or os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            bl_path = os.path.join(resolved_base, 'data', 'gif_blacklist.json')
            if not os.path.exists(bl_path):
                return
            with open(bl_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            raw_list = data.get('exercises', [])
            self._gif_blacklist = {
                self._normalize_exercise_name(n) for n in raw_list if n
            }
            print(f" [GIFBlacklist] Loaded {len(self._gif_blacklist)} blacklisted exercises (no exercise-specific GIF)")
        except Exception as e:
            print(f" [GIFBlacklist] Load failed: {e}")

    def _is_gif_blacklisted(self, exercise_name: str) -> bool:
        """Return True if the exercise is confirmed to have no matching GIF."""
        if not exercise_name or not self._gif_blacklist:
            return False
        return self._normalize_exercise_name(exercise_name) in self._gif_blacklist

    def _initialize_audit_media_index(self, base_dir: Optional[str] = None) -> None:
        """Load high-confidence exercise-name -> media mappings from audit artifacts."""
        if self._audit_media_index_ready:
            return

        try:
            resolved_base = base_dir or os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            candidates = [
                os.path.join(resolved_base, 'data', 'gif_link_audit_details_after_fix.csv'),
                os.path.join(resolved_base, 'data', 'gif_link_audit_details.csv'),
            ]

            loaded = 0
            for path in candidates:
                if not os.path.exists(path):
                    continue

                df = pd.read_csv(path)
                cols_lower = {str(c).lower(): c for c in df.columns}
                name_col = cols_lower.get('name')
                gif_col = cols_lower.get('gif_url')
                if not name_col or not gif_col:
                    continue

                name_series = df[name_col].fillna('').astype(str).str.strip()
                gif_series = df[gif_col].fillna('').astype(str).str.strip()
                valid = df[gif_series.str.startswith(('http://', 'https://'))].copy()
                if valid.empty:
                    continue

                url_counts = valid[gif_col].astype(str).value_counts()
                generic_urls = set(url_counts.head(3).index.tolist())

                for _, row in valid.iterrows():
                    raw_name = str(row[name_col]).strip()
                    raw_url = str(row[gif_col]).strip()
                    if not raw_name or not raw_url or raw_url in generic_urls:
                        continue

                    normalized = self._normalize_exercise_name(raw_name)
                    if not normalized or normalized in self._audit_name_to_media:
                        continue

                    self._audit_name_to_media[normalized] = raw_url
                    loaded += 1

                # First matching artifact is sufficient.
                break

            if loaded:
                print(f" [AuditMedia] Loaded {loaded} non-generic exact media mappings")

        except Exception as e:
            print(f" [AuditMedia] Load failed: {e}")
        finally:
            self._audit_media_index_ready = True

    def _get_audit_media_for_name(self, exercise_name: str) -> str:
        """Resolve media from locally-audited mappings with strict confidence checks."""
        if not exercise_name:
            return ''

        if not self._audit_name_to_media and not self._audit_media_index_ready:
            self._initialize_audit_media_index()

        if not self._audit_name_to_media:
            return ''

        key = self._normalize_exercise_name(exercise_name)
        if not key:
            return ''

        direct = self._audit_name_to_media.get(key, '')
        if direct:
            return direct

        best_key = ''
        best_url = ''
        best_score = 0.0
        for mapped_key, mapped_url in self._audit_name_to_media.items():
            score = self._name_similarity_score(key, mapped_key)
            if score > best_score:
                best_score = score
                best_key = mapped_key
                best_url = mapped_url

        if best_url and best_score >= 0.66 and self._is_confident_name_match(key, best_key, strict=False):
            return best_url
        return ''

    def _extract_wger_name(self, exercise: Dict) -> str:
        translations = exercise.get('translations', []) or []
        english = next((t for t in translations if t.get('language') == 2 and t.get('name')), None)
        if english:
            return str(english.get('name')).strip()
        any_named = next((t for t in translations if t.get('name')), None)
        if any_named:
            return str(any_named.get('name')).strip()
        return ''

    def _normalize_wger_media_url(self, value: str) -> str:
        """Normalize WGER media paths to absolute URLs."""
        clean = str(value or '').strip()
        if not clean:
            return ''
        if clean.startswith('//'):
            return f"https:{clean}"
        if clean.startswith('/'):
            return f"https://wger.de{clean}"
        if clean.startswith(('http://', 'https://')):
            return clean
        return ''

    def _extract_wger_media_url(self, exercise: Dict) -> str:
        images = exercise.get('images', []) or []
        normalized_images = []
        for img in images:
            media = self._normalize_wger_media_url(img.get('image') or img.get('url') or img.get('source'))
            if media:
                normalized_images.append((bool(img.get('is_main')), media))

        if normalized_images:
            # Prefer animated GIFs first when available.
            for _, media in normalized_images:
                if media.lower().split('?')[0].split('#')[0].endswith('.gif'):
                    return media

            # Then prefer main image, else first available image.
            main_media = next((media for is_main, media in normalized_images if is_main), '')
            if main_media:
                return main_media

            return normalized_images[0][1]

        # Fall back to videos only when image/GIF is unavailable.
        videos = exercise.get('videos', []) or []
        for vid in videos:
            for key in ('video', 'url', 'source'):
                value = self._normalize_wger_media_url(vid.get(key, ''))
                if value:
                    return value

        return ''

    def _initialize_wger_media_index(self):
        """Build a local name -> media URL map from WGER API for robust fallback media."""
        if self._wger_index_ready:
            return

        url = 'https://wger.de/api/v2/exerciseinfo/?limit=200'
        fetched = 0
        max_records = 1000
        mapped = 0
        seen_pages = 0

        while url and fetched < max_records and seen_pages < 8:
            resp = requests.get(url, timeout=12)
            if resp.status_code >= 400:
                print(f" WGER request failed: {resp.status_code}")
                break

            payload = resp.json()
            results = payload.get('results', []) or []
            if not results:
                break

            for exercise in results:
                fetched += 1
                name = self._extract_wger_name(exercise)
                media_url = self._extract_wger_media_url(exercise)
                if not name or not media_url:
                    continue

                key = self._normalize_exercise_name(name)
                if key:
                    self._wger_media_to_names.setdefault(media_url, set()).add(key)
                if key and key not in self._wger_name_to_media:
                    self._wger_name_to_media[key] = media_url
                    mapped += 1

            url = payload.get('next')
            seen_pages += 1

        self._wger_index_ready = True
        print(f" WGER media index ready: {mapped} mapped exercise names")

    def _get_wger_media_for_name(self, exercise_name: str) -> str:
        if not exercise_name:
            return ''

        # If background loading failed or has not completed, try a one-time
        # synchronous initialization so we can still provide specific media.
        if not self._wger_name_to_media and not self._wger_index_ready:
            try:
                self._initialize_wger_media_index()
            except Exception:
                pass

        key = self._normalize_exercise_name(exercise_name)
        if key in self._wger_name_to_media:
            return self._wger_name_to_media[key]

        if not key:
            return ''

        best_match = ''
        best_key = ''
        best_score = 0.0
        for mapped_key, media_url in list(self._wger_name_to_media.items()):
            score = self._name_similarity_score(key, mapped_key)
            if score > best_score:
                best_score = score
                best_key = mapped_key
                best_match = media_url

        if best_match and self._is_confident_name_match(key, best_key, strict=True):
            return best_match
        return ''

    def _get_related_wger_media_for_name(self, exercise_name: str) -> str:
        """Relaxed name-based lookup used only before generic fallback.

        This keeps results exercise-specific when strict fuzzy matching fails.
        """
        if not exercise_name:
            return ''

        if not self._wger_name_to_media and not self._wger_index_ready:
            try:
                self._initialize_wger_media_index()
            except Exception:
                pass

        if not self._wger_name_to_media:
            return ''

        key = self._normalize_exercise_name(exercise_name)
        if not key:
            return ''

        best_media = ''
        best_key = ''
        best_score = 0.0

        for mapped_key, media_url in list(self._wger_name_to_media.items()):
            score = self._name_similarity_score(key, mapped_key)
            if score > best_score:
                best_score = score
                best_key = mapped_key
                best_media = media_url

        if not best_media or best_score < 0.58:
            return ''
        if self._is_confident_name_match(key, best_key, strict=False):
            return best_media
        return ''

    def _get_exercise_specific_wger_fallback_pool(self, exercise_name: str, target_muscle: str = '') -> List[str]:
        """Return only name-relevant WGER media candidates (no generic random pool)."""
        if not self._wger_name_to_media and not self._wger_index_ready:
            try:
                self._initialize_wger_media_index()
            except Exception:
                pass

        if not self._wger_name_to_media:
            return []

        _ = target_muscle
        scored = []
        video_exts = ('.mp4', '.webm', '.ogg', '.mov', '.m3u8')

        for mapped_key, media_url in list(self._wger_name_to_media.items()):
            if not media_url:
                continue

            media_lower = media_url.lower().split('?')[0].split('#')[0]
            if media_lower.endswith(video_exts):
                continue

            if not self._is_confident_name_match(exercise_name, mapped_key, strict=False):
                continue

            score = self._name_similarity_score(exercise_name, mapped_key)
            scored.append((score, media_url))

        scored.sort(key=lambda item: item[0], reverse=True)

        pool = []
        seen = set()
        for _, url in scored:
            if url not in seen:
                pool.append(url)
                seen.add(url)
            if len(pool) >= 40:
                break

        return pool

    def _get_row_value(self, row, candidates: List[str], default=''):
        """Return first matching value from row by trying multiple key styles."""
        if row is None:
            return default

        row_dict = row.to_dict() if hasattr(row, 'to_dict') else dict(row)

        for key in candidates:
            if key in row_dict and pd.notna(row_dict.get(key)):
                val = str(row_dict.get(key)).strip()
                if val and val.lower() not in {'nan', 'none', 'null'}:
                    return val

        lowered = {str(k).lower(): v for k, v in row_dict.items()}
        for key in candidates:
            lk = key.lower()
            if lk in lowered and pd.notna(lowered.get(lk)):
                val = str(lowered.get(lk)).strip()
                if val and val.lower() not in {'nan', 'none', 'null'}:
                    return val

        return default

    def _parse_duration_seconds(self, reps_value) -> int:
        """Parse time-based reps strings like '5 min' or '30-45 seconds'."""
        text = str(reps_value or '').strip().lower()
        if not text:
            return 0

        nums = [int(n) for n in re.findall(r'\d+', text)]
        if not nums:
            return 0

        if any(token in text for token in ('min', 'minute')):
            return max(nums) * 60
        if any(token in text for token in ('sec', 'second')):
            return max(nums)
        return 0

    def _is_trackable_exercise(self, name: str, reps_value, explicit: Optional[bool] = None) -> bool:
        """
        Decide if pose-based rep counting should be enabled.

        Time-based and locomotion/mobility style movements are treated as non-trackable
        so the frontend can use a timer instead of rep counting.
        """
        if isinstance(explicit, bool):
            return explicit

        if self._parse_duration_seconds(reps_value) > 0:
            return False

        lower_name = str(name or '').lower()
        non_trackable_markers = (
            'walk', 'jog', 'run', 'bike', 'cycle', 'cardio',
            'stretch', 'mobility', 'warm-up', 'warm up'
        )
        if any(marker in lower_name for marker in non_trackable_markers):
            return False

        return True

    def _classify_exercise_mode(self, name: str, equipment: str, reps_value,
                                 explicit_trackable: Optional[bool] = None) -> Dict:
        """Classify whether an exercise needs camera tracking or timer-only mode."""
        lower_name = str(name or '').lower()
        lower_equipment = str(equipment or '').lower()

        non_camera_keywords = (
            'walk', 'jog', 'run', 'brisk', 'cardio', 'bike', 'cycle', 'cycling',
            'elliptical', 'rowing', 'treadmill', 'stair', 'stepper', 'warm-up',
            'warm up', 'mobility', 'stretch'
        )
        non_camera_equipment = (
            'elliptical', 'bike', 'treadmill', 'rowing', 'stepmill', 'ergometer', 'stationary bike'
        )

        duration_seconds = self._parse_duration_seconds(reps_value)
        trackable = self._is_trackable_exercise(name, reps_value, explicit=explicit_trackable)
        keyword_cardio = any(kw in lower_name for kw in non_camera_keywords)
        equipment_cardio = any(kw in lower_equipment for kw in non_camera_equipment)
        is_timed = duration_seconds > 0 or keyword_cardio or equipment_cardio
        needs_camera = bool(trackable and not is_timed and not keyword_cardio and not equipment_cardio)

        # Look up movement pattern from global mapping service
        movement_pattern = get_movement_pattern(name)

        return {
            'trackable': bool(trackable),
            'duration_seconds': int(duration_seconds),
            'is_timed': bool(is_timed),
            'needs_camera': bool(needs_camera),
            'movement_pattern': movement_pattern,
            'exercise_mode': 'cardio' if (keyword_cardio or equipment_cardio or is_timed) else 'strength',
        }

    def _build_search_embed_url(self, exercise_name: str, unique_suffix: str = '') -> str:
        name = str(exercise_name or '').strip()
        if not name:
            return ''
        query = f"{name} exercise tutorial proper form {unique_suffix}".strip()
        return f"https://www.youtube.com/embed?listType=search&list={quote_plus(query)}"

    def _get_exercise_primary_media_url(self, exercise: Dict) -> str:
        if not isinstance(exercise, dict):
            return ''

        keys = (
            'video_url', 'gif', 'image', 'media_url', 'mediaUrl', 'demo_url', 'demoUrl',
            'thumbnail', 'Wger_Image_URL', 'wger_image_url'
        )
        for key in keys:
            value = exercise.get(key)
            if isinstance(value, str):
                clean = value.strip()
                if clean.startswith(('http://', 'https://')):
                    return clean
        return ''

    def _set_exercise_media_url(self, exercise: Dict, media_url: str) -> None:
        if not isinstance(exercise, dict):
            return

        clean = str(media_url or '').strip()
        if not clean.startswith(('http://', 'https://')):
            exercise['gif'] = ''
            exercise['video_url'] = ''
            exercise['image'] = ''
            exercise['media_type'] = 'none'
            return

        lower = clean.lower().split('?')[0].split('#')[0]
        is_video = lower.endswith(('.mp4', '.webm', '.ogg', '.mov', '.m3u8'))
        is_youtube = 'youtube.com/embed' in clean

        exercise['gif'] = '' if (is_video or is_youtube) else clean
        exercise['video_url'] = clean if (is_video or is_youtube) else ''
        exercise['image'] = '' if (is_video or is_youtube) else clean
        exercise['media_type'] = 'youtube' if is_youtube else ('video' if is_video else 'image')

    def _enforce_unique_media_per_day(self, exercises: List[Dict]) -> List[Dict]:
        """Keep media stable per exercise; avoid random duplicate rewrites."""
        used_urls: Dict[str, str] = {}

        for idx, ex in enumerate(exercises or []):
            if not isinstance(ex, dict):
                continue

            media_url = self._get_exercise_primary_media_url(ex)
            if not media_url:
                continue

            name_key = self._normalize_exercise_name(ex.get('name', '')) or f'row-{idx}'
            previous_name = used_urls.get(media_url)

            if previous_name and previous_name != name_key:
                # Preserve originally resolved media rather than forcing substitutions.
                used_urls[media_url] = name_key
                continue

            if media_url:
                used_urls[media_url] = name_key

        return exercises

    # Known exercise-media CDN domains we trust without live HTTP checks.
    # The frontend's onError handler will fall back gracefully if a URL fails.
    _TRUSTED_MEDIA_DOMAINS = (
        'wger.de',
        'i.imgur.com',
        'imgur.com',
        'giphy.com',
        'media.giphy.com',
        'upload.wikimedia.org',
        'cdn.musclewiki.com',
        'musclewiki.com',
        'i.pinimg.com',
        'images.ctfassets.net',
        'assets.jefit.com',
        'cdn.jefit.com',
    )

    _EXERCISEDB_DOMAINS = (
        'exercisedb.io',
        'v2.exercisedb.io',
        'api.exercisedb.io',
    )

    _GLOBAL_GIF_FALLBACK_POOL = (
        'https://wger.de/media/exercise-images/1227/57415c3c-2963-4130-9f6f-79f6a96113b6.gif',
        'https://wger.de/media/exercise-images/1519/fab7f641-27d4-40b5-8edd-1a0a137bfd94.gif',
        'https://wger.de/media/exercise-images/1594/e030d44e-d023-4fef-a3bd-934d70f65d96.gif',
        'https://wger.de/media/exercise-images/1084/91dd5a95-1c45-46f2-a074-de41b6ad599b.jpg',
        'https://wger.de/media/exercise-images/1088/9f66b288-ce8f-4154-ba80-78fee267263c.jpg',
        'https://wger.de/media/exercise-images/1644/cde4f147-d49a-492f-9c8a-e3c76788fd26.jpg',
        'https://wger.de/media/exercise-images/203/1c052351-2af0-4227-aeb0-244008e4b0a8.jpeg',
        'https://wger.de/media/exercise-images/203/300a44ac-4368-48e2-8b18-beea32ab915d.gif',
    )

    _MUSCLE_GIF_FALLBACK_POOLS = {
        'upper legs': (
            'https://wger.de/media/exercise-images/1594/e030d44e-d023-4fef-a3bd-934d70f65d96.gif',
            'https://wger.de/media/exercise-images/1088/9f66b288-ce8f-4154-ba80-78fee267263c.jpg',
            'https://wger.de/media/exercise-images/203/300a44ac-4368-48e2-8b18-beea32ab915d.gif',
        ),
        'lower legs': (
            'https://wger.de/media/exercise-images/1594/e030d44e-d023-4fef-a3bd-934d70f65d96.gif',
            'https://wger.de/media/exercise-images/1088/9f66b288-ce8f-4154-ba80-78fee267263c.jpg',
            'https://wger.de/media/exercise-images/203/300a44ac-4368-48e2-8b18-beea32ab915d.gif',
        ),
        'upper arms': (
            'https://wger.de/media/exercise-images/1519/fab7f641-27d4-40b5-8edd-1a0a137bfd94.gif',
            'https://wger.de/media/exercise-images/203/1c052351-2af0-4227-aeb0-244008e4b0a8.jpeg',
            'https://wger.de/media/exercise-images/203/300a44ac-4368-48e2-8b18-beea32ab915d.gif',
        ),
        'lower arms': (
            'https://wger.de/media/exercise-images/1519/fab7f641-27d4-40b5-8edd-1a0a137bfd94.gif',
            'https://wger.de/media/exercise-images/203/1c052351-2af0-4227-aeb0-244008e4b0a8.jpeg',
            'https://wger.de/media/exercise-images/203/300a44ac-4368-48e2-8b18-beea32ab915d.gif',
        ),
        'shoulders': (
            'https://wger.de/media/exercise-images/1227/57415c3c-2963-4130-9f6f-79f6a96113b6.gif',
            'https://wger.de/media/exercise-images/1084/91dd5a95-1c45-46f2-a074-de41b6ad599b.jpg',
            'https://wger.de/media/exercise-images/1644/cde4f147-d49a-492f-9c8a-e3c76788fd26.jpg',
        ),
        'chest': (
            'https://wger.de/media/exercise-images/1227/57415c3c-2963-4130-9f6f-79f6a96113b6.gif',
            'https://wger.de/media/exercise-images/1084/91dd5a95-1c45-46f2-a074-de41b6ad599b.jpg',
            'https://wger.de/media/exercise-images/1644/cde4f147-d49a-492f-9c8a-e3c76788fd26.jpg',
        ),
        'back': (
            'https://wger.de/media/exercise-images/1227/57415c3c-2963-4130-9f6f-79f6a96113b6.gif',
            'https://wger.de/media/exercise-images/1084/91dd5a95-1c45-46f2-a074-de41b6ad599b.jpg',
            'https://wger.de/media/exercise-images/1644/cde4f147-d49a-492f-9c8a-e3c76788fd26.jpg',
        ),
        'waist': (
            'https://wger.de/media/exercise-images/1594/e030d44e-d023-4fef-a3bd-934d70f65d96.gif',
            'https://wger.de/media/exercise-images/203/300a44ac-4368-48e2-8b18-beea32ab915d.gif',
            'https://wger.de/media/exercise-images/203/1c052351-2af0-4227-aeb0-244008e4b0a8.jpeg',
        ),
        'cardio': (
            'https://wger.de/media/exercise-images/1594/e030d44e-d023-4fef-a3bd-934d70f65d96.gif',
            'https://wger.de/media/exercise-images/1088/9f66b288-ce8f-4154-ba80-78fee267263c.jpg',
            'https://wger.de/media/exercise-images/1644/cde4f147-d49a-492f-9c8a-e3c76788fd26.jpg',
        ),
        'neck': (
            'https://wger.de/media/exercise-images/1227/57415c3c-2963-4130-9f6f-79f6a96113b6.gif',
            'https://wger.de/media/exercise-images/203/1c052351-2af0-4227-aeb0-244008e4b0a8.jpeg',
        ),
    }

    # No-YouTube visual fallback URLs (stable direct GIFs) used when source media is unavailable.
    _MUSCLE_GIF_FALLBACKS = {
        'upper legs': 'https://wger.de/media/exercise-images/1594/e030d44e-d023-4fef-a3bd-934d70f65d96.gif',
        'lower legs': 'https://wger.de/media/exercise-images/1594/e030d44e-d023-4fef-a3bd-934d70f65d96.gif',
        'upper arms': 'https://wger.de/media/exercise-images/1519/fab7f641-27d4-40b5-8edd-1a0a137bfd94.gif',
        'lower arms': 'https://wger.de/media/exercise-images/1519/fab7f641-27d4-40b5-8edd-1a0a137bfd94.gif',
        'shoulders': 'https://wger.de/media/exercise-images/1227/57415c3c-2963-4130-9f6f-79f6a96113b6.gif',
        'chest': 'https://wger.de/media/exercise-images/1227/57415c3c-2963-4130-9f6f-79f6a96113b6.gif',
        'back': 'https://wger.de/media/exercise-images/1227/57415c3c-2963-4130-9f6f-79f6a96113b6.gif',
        'waist': 'https://wger.de/media/exercise-images/1594/e030d44e-d023-4fef-a3bd-934d70f65d96.gif',
        'cardio': 'https://wger.de/media/exercise-images/1594/e030d44e-d023-4fef-a3bd-934d70f65d96.gif',
        'neck': 'https://wger.de/media/exercise-images/1227/57415c3c-2963-4130-9f6f-79f6a96113b6.gif',
    }

    # Exact-name fallbacks for known rows that still have no direct media URL.
    # Keys must match _normalize_exercise_name(name).
    _EXERCISE_GIF_NAME_OVERRIDES = {
        'barbell incline bench press': 'https://wger.de/media/exercise-images/1227/57415c3c-2963-4130-9f6f-79f6a96113b6.gif',
        'cable incline bench press': 'https://wger.de/media/exercise-images/1227/57415c3c-2963-4130-9f6f-79f6a96113b6.gif',
        'dumbbell incline alternate press': 'https://wger.de/media/exercise-images/1227/57415c3c-2963-4130-9f6f-79f6a96113b6.gif',
        'dumbbell incline bench press': 'https://wger.de/media/exercise-images/1227/57415c3c-2963-4130-9f6f-79f6a96113b6.gif',
        'dumbbell incline hammer press': 'https://wger.de/media/exercise-images/1227/57415c3c-2963-4130-9f6f-79f6a96113b6.gif',
        'smith incline bench press': 'https://wger.de/media/exercise-images/1227/57415c3c-2963-4130-9f6f-79f6a96113b6.gif',
        'dumbbell decline triceps extension': 'https://wger.de/media/exercise-images/1519/fab7f641-27d4-40b5-8edd-1a0a137bfd94.gif',
        'dumbbell incline triceps extension': 'https://wger.de/media/exercise-images/1519/fab7f641-27d4-40b5-8edd-1a0a137bfd94.gif',
        'dumbbell lying triceps extension': 'https://wger.de/media/exercise-images/1519/fab7f641-27d4-40b5-8edd-1a0a137bfd94.gif',
        'dumbbell seated triceps extension': 'https://wger.de/media/exercise-images/1519/fab7f641-27d4-40b5-8edd-1a0a137bfd94.gif',
        'dumbbell standing triceps extension': 'https://wger.de/media/exercise-images/1519/fab7f641-27d4-40b5-8edd-1a0a137bfd94.gif',
        'lever seated hip adduction': 'https://wger.de/media/exercise-images/1594/e030d44e-d023-4fef-a3bd-934d70f65d96.gif',
        # Curated overrides for custom/non-dataset exercise names used by the planner.
        'arm circles': 'https://wger.de/media/exercise-images/1862/93d993f8-1d8c-4e21-99c6-08b2fe424a17.png',
        'band pull apart towel pull': 'https://wger.de/media/exercise-images/158/02e8a7c3-dc67-434e-a4bc-77fdecf84b49.webp',
        'band row activation isometric row': 'https://wger.de/media/exercise-images/1117/e74255c0-67a0-4309-b78d-2d79e6ff8c11.png',
        'bench dip knees bent': 'https://wger.de/media/exercise-images/1648/63ae02d6-6dd9-4e9e-84da-d4905e78a33c.jpg',
        'bench dip on floor': 'https://wger.de/media/exercise-images/1648/63ae02d6-6dd9-4e9e-84da-d4905e78a33c.jpg',
        'biceps narrow pull ups': 'https://wger.de/media/exercise-images/475/b0554016-16fd-4dbe-be47-a2a17d16ae0e.jpg',
        'biceps pull up': 'https://wger.de/media/exercise-images/1765/7ac179ab-f1ca-4138-ad1a-3e0133272348.png',
        'bodyweight squat warm up': 'https://wger.de/media/exercise-images/1627/86d0b85a-66b7-4e5f-bf8d-bb4d7eb03f59.webp',
        'bodyweight squatting row': 'https://wger.de/media/exercise-images/1117/e74255c0-67a0-4309-b78d-2d79e6ff8c11.png',
        'bodyweight squatting row towel': 'https://wger.de/media/exercise-images/1117/e74255c0-67a0-4309-b78d-2d79e6ff8c11.png',
        'bodyweight standing close grip one arm row': 'https://wger.de/media/exercise-images/1637/a1fbe83a-a3e5-49f6-a2c2-5d5b533c2be8.png',
        'brisk walk light cardio': 'https://wger.de/media/exercise-images/1615/7792295c-83b6-4ea8-9353-ce02f0ad2559.jpg',
        'cat cow mobility': 'https://wger.de/media/exercise-images/1871/85a6b9de-4eec-445b-8ebb-f1950b076aba.png',
        'chest dip': 'https://wger.de/media/exercise-images/83/Bench-dips-1.png',
        'chest tap push up male': 'https://wger.de/media/exercise-images/1554/49207a62-8799-4b47-8c0b-7bde02926f3d.png',
        'curtsey squat': 'https://wger.de/media/exercise-images/1627/86d0b85a-66b7-4e5f-bf8d-bb4d7eb03f59.webp',
        'doorway chest stretch': 'https://wger.de/media/exercise-images/1874/66fca8a5-41e8-42d1-8776-5e46a4902650.png',
        'dumbbell alternate side press': 'https://wger.de/media/exercise-images/1644/cde4f147-d49a-492f-9c8a-e3c76788fd26.jpg',
        'dumbbell arnold press': 'https://wger.de/media/exercise-images/1676/ac441fa8-cf11-45a5-9633-18ae49fb9320.webp',
        'dumbbell clean': 'https://wger.de/media/exercise-images/1645/9e730259-1dcd-4b5e-b4cc-9ebc0cfda75c.webp',
        'dumbbell contralateral forward lunge': 'https://wger.de/media/exercise-images/1651/04ab2679-a04d-4d05-9c85-0d36e898328c.webp',
        'dumbbell deadlift': 'https://wger.de/media/exercise-images/1652/0306c8c0-70cc-45d4-92de-6fa72ceaa834.webp',
        'dynamic joint circles': 'https://wger.de/media/exercise-images/1862/93d993f8-1d8c-4e21-99c6-08b2fe424a17.png',
        'glute bridge activation': 'https://wger.de/media/exercise-images/1613/a851fe9d-771f-44da-82f0-799e02ae3fd1.jpg',
        'hip hinge drill': 'https://wger.de/media/exercise-images/1652/0306c8c0-70cc-45d4-92de-6fa72ceaa834.webp',
        'inchworm walkout': 'https://wger.de/media/exercise-images/1551/a6a9e561-3965-45c6-9f2b-ee671e1a3a45.png',
        'leg swing': 'https://wger.de/media/exercise-images/1861/0ffe4e99-71ad-47fb-b98c-1f243faa0499.png',
        'scapular push ups': 'https://wger.de/media/exercise-images/1551/a6a9e561-3965-45c6-9f2b-ee671e1a3a45.png',
        'standing hip circles': 'https://wger.de/media/exercise-images/1862/93d993f8-1d8c-4e21-99c6-08b2fe424a17.png',
        'barbell one arm snatch': 'https://wger.de/media/exercise-images/1638/046c09b0-c35d-48d0-a552-39dd49f956d2.webp',
        '3 4 sit up': 'https://wger.de/media/exercise-images/56/Decline-crunch-1.png',
        'air bike': 'https://wger.de/media/exercise-images/176/Cross-body-crunch-1.png',
    }
    _DEFAULT_GIF_FALLBACK = 'https://wger.de/media/exercise-images/1594/e030d44e-d023-4fef-a3bd-934d70f65d96.gif'

    def _pick_deterministic_fallback(self, options: List[str], exercise_name: str) -> str:
        valid = [u for u in options if isinstance(u, str) and u.strip()]
        if not valid:
            return self._DEFAULT_GIF_FALLBACK

        key = self._normalize_exercise_name(exercise_name) or str(exercise_name or 'fallback')
        digest = hashlib.md5(key.encode('utf-8')).hexdigest()
        idx = int(digest, 16) % len(valid)
        return valid[idx]

    def _get_gif_fallback_for_target(self, target_muscle: str, exercise_name: str = '', allow_generic: bool = False) -> str:
        key = str(target_muscle or '').strip().lower()

        # Prefer exercise-name-aware WGER fallback pools for better per-exercise
        # specificity and reduced repeated generic media.
        if exercise_name:
            named_wger_pool = self._get_exercise_specific_wger_fallback_pool(exercise_name, target_muscle)
            if named_wger_pool:
                return self._pick_deterministic_fallback(named_wger_pool, f"{key}:{exercise_name}")

        # Avoid random muscle-group substitutions unless explicitly requested.
        if not allow_generic:
            return ''

        if key in self._MUSCLE_GIF_FALLBACK_POOLS:
            return self._pick_deterministic_fallback(list(self._MUSCLE_GIF_FALLBACK_POOLS[key]), exercise_name)

        # Unknown muscle group: choose from global fallback pool using exercise-name hash.
        return self._pick_deterministic_fallback(list(self._GLOBAL_GIF_FALLBACK_POOL), exercise_name)

    def _get_gif_fallback_for_exercise_name(self, exercise_name: str) -> str:
        normalized = self._normalize_exercise_name(exercise_name)
        override = self._EXERCISE_GIF_NAME_OVERRIDES.get(normalized, '')
        if override:
            return override
        return self._get_audit_media_for_name(exercise_name)

    def _check_url_reachable(self, url: str, accept_any_response: bool = False) -> bool:
        """Best-effort live URL check with short timeout + in-memory cache.

        Args:
            url: The URL to check
            accept_any_response: If True, accept any HTTP response (not just 2xx)
                                to be more lenient with external CDNs
        """
        now = time.time()
        cached = self._media_url_cache.get(url)
        if cached:
            verdict, ts = cached
            if now - ts < self._media_cache_ttl_seconds:
                return bool(verdict)

        verdict = False
        try:
            head = requests.head(url, timeout=self._media_check_timeout, allow_redirects=True)
            if head.status_code < 400:
                verdict = True
            elif accept_any_response and head.status_code < 500:
                # Accept 4xx errors too (e.g., 403 forbidden but server is up)
                verdict = True
            elif head.status_code in (403, 405):
                # Some hosts block HEAD but allow GET.
                get_resp = requests.get(url, timeout=self._media_check_timeout, allow_redirects=True, stream=True)
                verdict = get_resp.status_code < 400 or (accept_any_response and get_resp.status_code < 500)
                get_resp.close()
        except Exception:
            try:
                get_resp = requests.get(url, timeout=self._media_check_timeout, allow_redirects=True, stream=True)
                verdict = get_resp.status_code < 400 or (accept_any_response and get_resp.status_code < 500)
                get_resp.close()
            except Exception:
                verdict = False

        self._media_url_cache[url] = (verdict, now)
        return verdict

    def _validate_media_url(self, url: str) -> bool:
        """
        Validate whether a URL is acceptable to pass to the frontend.

        Strategy:
          1. Must be a non-empty https:// or http:// URL.
          2. YouTube embed URLs are accepted directly.
          3. Trusted domains are accepted without live checks (frontend handles errors).
          4. Other URLs checked with a short cached reachability probe.
        """
        if not url or not isinstance(url, str):
            return False

        clean = url.strip()
        if not clean.startswith(('http://', 'https://')):
            return False

        # YouTube embed URLs are always accepted
        if 'youtube.com/embed' in clean or 'youtu.be/' in clean:
            return True

        # Fast check: trusted CDN domains - accept without live check
        # Frontend has onError handlers to fall back gracefully
        try:
            from urllib.parse import urlparse
            parsed_host = urlparse(clean).hostname or ''

            # Accept trusted domains directly (wger, imgur, etc.)
            if any(parsed_host == d or parsed_host.endswith('.' + d) for d in self._TRUSTED_MEDIA_DOMAINS):
                return True

            # ExerciseDB: try live check first, but accept if it looks valid
            if any(parsed_host == d or parsed_host.endswith('.' + d) for d in self._EXERCISEDB_DOMAINS):
                # Quick check but don't be too strict - accept if server responds at all
                return self._check_url_reachable(clean, accept_any_response=True)
        except Exception:
            pass

        # Accept any URL that looks like a media file by extension
        path_lower = clean.lower().split('?')[0].split('#')[0]
        media_exts = ('.gif', '.jpg', '.jpeg', '.png', '.webp', '.mp4', '.webm', '.ogg', '.mov', '.svg')
        if any(path_lower.endswith(ext) for ext in media_exts):
            # Be more lenient - accept if the URL structure looks valid
            return True

        # For wger-style URLs that have /image/ in the path
        if '/image/' in clean or '/images/' in clean or '/media/' in clean or '/gif/' in clean:
            return True

        return False

    def _resolve_exercise_media(self, row) -> Dict[str, str]:
        """
        Pick a working media URL and normalize payload fields.

        Exercise-specific source priority:
          1. Wger_Image_Url dataset column (primary source)
          2. Exact WGER name-index image/GIF
          3. Dataset GIF/Image/Thumbnail columns
          4. Fuzzy WGER image/GIF
          5. Exact exercise-name GIF override (known gaps)
          6. YouTube fallback only if explicitly enabled and all image/GIF paths fail

        NOTE: Generic muscle-group fallback GIFs are intentionally disabled.
              Exercises in the GIF blacklist always return media_type='none' so
              the frontend shows a descriptive placeholder instead of the wrong GIF.
        """
        exercise_name = self._get_row_value(row, ['Name', 'name'], '')

        # Short-circuit: blacklisted exercises have no valid exercise-specific GIF.
        # Return 'none' so the frontend shows its text/illustration placeholder.
        if self._is_gif_blacklisted(exercise_name):
            return {
                'gif': '',
                'video_url': '',
                'image': '',
                'media_type': 'none',
            }
        audit_media = self._get_audit_media_for_name(exercise_name)
        normalized_name = self._normalize_exercise_name(exercise_name)
        exact_wger = self._wger_name_to_media.get(normalized_name, '')
        fuzzy_wger = '' if exact_wger else self._get_wger_media_for_name(exercise_name)
        related_wger = '' if (exact_wger or fuzzy_wger) else self._get_related_wger_media_for_name(exercise_name)

        media_candidates = [
            # 0. Pre-fetched Wger image from exercises_processed.csv — most reliable,
            #    since exercisedb.io has been returning HTTP 500 errors.
            self._get_row_value(row, ['Wger_Image_Url', 'Wger_Image_URL', 'Wger_Image_url']),
            # 0b. Local audited name->media mapping (non-generic URLs only).
            audit_media,
            # 1. Exact WGER live-API match from cached index.
            exact_wger,
            # 2. Dataset image-like URLs (prefer over video).
            self._get_row_value(row, ['GIF_URL', 'Gif_URL', 'Gif_Url', 'GifUrl', 'GIF', 'Gif']),
            self._get_row_value(row, ['Image_URL', 'Image_Url', 'ImageUrl', 'Image']),
            self._get_row_value(row, ['Thumbnail_URL', 'Thumbnail_Url', 'ThumbnailUrl', 'Thumbnail']),
            # 3. Conservative fuzzy WGER match for better per-exercise specificity.
            fuzzy_wger,
            # 3b. Relaxed related WGER match before generic fallback.
            related_wger,
            # 4. Keep dataset video URL as a last optional candidate.
            self._get_row_value(row, ['Video_URL', 'Video_Url', 'VideoUrl', 'Video']),
        ]

        media_candidates = [u for u in media_candidates if isinstance(u, str) and u.strip().startswith(('http://', 'https://'))]

        media_url = ''
        deferred_youtube_url = ''
        deferred_video_url = ''

        # Force exact-name GIF overrides first for known rows missing image/GIF media.
        exercise_override = self._get_gif_fallback_for_exercise_name(exercise_name)
        if exercise_override and self._validate_media_url(exercise_override):
            media_url = exercise_override
        else:
            for candidate in media_candidates:
                if candidate and self._validate_media_url(candidate):
                    lower_candidate = candidate.lower().split('?')[0].split('#')[0]
                    is_video_candidate = lower_candidate.endswith(('.mp4', '.webm', '.ogg', '.mov', '.m3u8'))
                    if 'youtube.com/embed' in candidate or 'youtu.be/' in candidate:
                        if not self._youtube_fallback_enabled:
                            continue
                        if not deferred_youtube_url:
                            deferred_youtube_url = candidate
                        continue
                    if is_video_candidate:
                        if not deferred_video_url:
                            deferred_video_url = candidate
                        continue
                    media_url = candidate
                    break

        # Prefer strict name-based GIF fallback over video/youtube when direct sources fail.
        if not media_url:
            target_muscle = self._get_row_value(row, ['Target_Muscle', 'Target_Muscle_Group', 'Muscle'], '')
            fallback_gif = self._get_gif_fallback_for_target(
                target_muscle,
                exercise_name=exercise_name,
                allow_generic=False,
            )
            if fallback_gif and self._validate_media_url(fallback_gif):
                media_url = fallback_gif

        # Use any existing video URL only when no image/GIF fallback was possible.
        if not media_url and deferred_video_url:
            if self._is_wger_video_url_compatible(deferred_video_url, exercise_name):
                media_url = deferred_video_url

        # Use any existing YouTube URL only when no image/GIF/video fallback was possible.
        if not media_url and self._youtube_fallback_enabled and deferred_youtube_url:
            media_url = deferred_youtube_url

        # Issue #3 – YouTube fallback: prefer YouTube over an unvalidated URL candidate.
        youtube_url = ''
        if not media_url and self._youtube_fallback_enabled and self._youtube_svc and exercise_name:
            youtube_url = self._youtube_svc.search_exercise_video(exercise_name)
            if youtube_url:
                media_url = youtube_url

        # NOTE: Generic muscle-group fallback is intentionally disabled.
        # We do NOT fall back to a random GIF for a different exercise — use 'none' instead.
        # (The allow_generic=True path previously here caused wrong GIFs to be shown.)

        # Optional final YouTube search embed only when YouTube fallback is enabled.
        if not media_url and self._youtube_fallback_enabled and exercise_name:
            media_url = self._build_search_embed_url(exercise_name)

        if not media_url:
            return {
                'gif': '',
                'video_url': '',
                'image': '',
                'media_type': 'none',
            }

        lower = media_url.lower().split('?')[0].split('#')[0]
        is_video = lower.endswith(('.mp4', '.webm', '.ogg', '.mov', '.m3u8'))
        is_youtube = 'youtube.com/embed' in media_url

        return {
            'gif':       '' if (is_video or is_youtube) else media_url,
            'video_url': media_url if (is_video or is_youtube) else '',
            'image':     '' if (is_video or is_youtube) else media_url,
            'media_type': 'youtube' if is_youtube else ('video' if is_video else 'image'),
        }

    def _load_ml_models(self):
        """Load pre-trained ML models (optional)"""
        try:
            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            model_dir = os.path.join(base_dir, 'models')

            # Try loading the multi-output model first
            multi_output_path = os.path.join(model_dir, 'multi_output_xgboost_model.joblib')
            multi_output_loaded = False
            
            if os.path.exists(multi_output_path):
                try:
                    self.multi_output_model.load_model(multi_output_path)
                    print(" Multi-Output ML model loaded successfully")
                    multi_output_loaded = True
                except Exception as e:
                    print(f" Failed to load Multi-Output ML model: {e}")

            # Load multiple models for different aspects
            volume_path = os.path.join(model_dir, 'xgboost_volume.pkl')
            intensity_path = os.path.join(model_dir, 'xgboost_intensity.pkl')
            split_path = os.path.join(model_dir, 'xgboost_split.pkl')
            frequency_path = os.path.join(model_dir, 'xgboost_frequency.pkl')
            sets_path = os.path.join(model_dir, 'xgboost_sets.pkl')
            reps_path = os.path.join(model_dir, 'xgboost_reps.pkl')
            rest_path = os.path.join(model_dir, 'xgboost_rest.pkl')
            progression_path = os.path.join(model_dir, 'xgboost_progression.pkl')
            le_goal_path = os.path.join(model_dir, 'goal_encoder.pkl')  # match train.py
            le_exp_path = os.path.join(model_dir, 'label_encoder_experience.pkl')

            # Only print missing model warnings if the multi-output model wasn't loaded
            if os.path.exists(volume_path):
                self.xgb_volume_model = joblib.load(volume_path)
                if not multi_output_loaded: print(" Volume ML model loaded successfully")
            else:
                if not multi_output_loaded: print(" Volume ML model not found, using rule-based system")

            if os.path.exists(intensity_path):
                self.xgb_intensity_model = joblib.load(intensity_path)
                if not multi_output_loaded: print(" Intensity ML model loaded successfully")
            else:
                if not multi_output_loaded: print(" Intensity ML model not found, using rule-based system")

            if os.path.exists(split_path):
                self.xgb_split_model = joblib.load(split_path)
                if not multi_output_loaded: print(" Split ML model loaded successfully")
            else:
                if not multi_output_loaded: print(" Split ML model not found, using rule-based system")

            if os.path.exists(frequency_path):
                self.xgb_frequency_model = joblib.load(frequency_path)
                if not multi_output_loaded: print(" Frequency ML model loaded successfully")
            else:
                if not multi_output_loaded: print(" Frequency ML model not found, using rule-based system")

            if os.path.exists(sets_path):
                self.xgb_sets_model = joblib.load(sets_path)
                if not multi_output_loaded: print(" Sets ML model loaded successfully")
            else:
                if not multi_output_loaded: print(" Sets ML model not found, using rule-based system")

            if os.path.exists(reps_path):
                self.xgb_reps_model = joblib.load(reps_path)
                if not multi_output_loaded: print(" Reps ML model loaded successfully")
            else:
                if not multi_output_loaded: print(" Reps ML model not found, using rule-based system")

            if os.path.exists(rest_path):
                self.xgb_rest_model = joblib.load(rest_path)
                if not multi_output_loaded: print(" Rest ML model loaded successfully")
            else:
                if not multi_output_loaded: print(" Rest ML model not found, using rule-based system")

            if os.path.exists(progression_path):
                self.xgb_progression_model = joblib.load(progression_path)
                if not multi_output_loaded: print(" Progression ML model loaded successfully")
            else:
                if not multi_output_loaded: print(" Progression ML model not found, using rule-based system")

            if os.path.exists(le_goal_path):
                self.le_goal = joblib.load(le_goal_path)
                if not multi_output_loaded: print(" Goal label encoder loaded successfully")
            else:
                if not multi_output_loaded: print(" Goal label encoder not found")

            if os.path.exists(le_exp_path):
                self.le_experience = joblib.load(le_exp_path)
                if not multi_output_loaded: print(" Experience label encoder loaded successfully")
            else:
                if not multi_output_loaded: print(" Experience label encoder not found")

        except Exception as e:
            print(f" Could not load ML models: {e}")
            self.xgb_volume_model = None
            self.xgb_intensity_model = None
            self.xgb_split_model = None
            self.xgb_frequency_model = None
            self.xgb_sets_model = None
            self.xgb_reps_model = None
            self.xgb_rest_model = None
            self.xgb_progression_model = None
            self.le_goal = None
            self.le_experience = None

    def filter_by_equipment(self, exercises: pd.DataFrame, available_equipment: List[str]) -> pd.DataFrame:
        """Filter exercises by available equipment - HOME-V1 POLICY ENFORCEMENT.

        Loads equipment_synonyms_home_v1.json to translate frontend display labels
        to their canonical CSV Equipment column values, then filters the dataset.
        Includes Rope split logic: Jump Rope is allowed, Battling Ropes is blocked.
        Body Weight exercises are ALWAYS included regardless of profile.
        """
        if not available_equipment or exercises.empty:
            return exercises

        try:
            if 'Equipment' not in exercises.columns:
                print(" 'Equipment' column not found")
                return exercises

            # ── Load home-v1 synonym + policy files ───────────────────────
            import json as _json
            _data_dir = os.path.join(
                os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data'
            )
            _synonyms_path = os.path.join(_data_dir, 'equipment_synonyms_home_v1.json')
            _policy_path   = os.path.join(_data_dir, 'equipment_policy_home_v1.json')

            _frontend_to_csv: dict = {}
            _always_include: List[str] = ['body weight', 'bodyweight', 'none', 'no equipment']
            _rope_allowed_pats: List[str] = ['jump rope', 'skipping rope']
            _rope_blocked_pats: List[str] = ['battling rope', 'battle rope']

            if os.path.exists(_synonyms_path):
                with open(_synonyms_path, 'r', encoding='utf-8') as _f:
                    _synonyms = _json.load(_f)
                _frontend_to_csv = _synonyms.get('frontend_to_csv', {})
                _always_include  = [v.lower() for v in _synonyms.get('always_include_csv', _always_include)]

            if os.path.exists(_policy_path):
                with open(_policy_path, 'r', encoding='utf-8') as _f:
                    _policy = _json.load(_f)
                _rsplit = _policy.get('policy', {}).get('rope_split', {})
                _rope_allowed_pats = [p.lower() for p in _rsplit.get('allowed_name_patterns', _rope_allowed_pats)]
                _rope_blocked_pats = [p.lower() for p in _rsplit.get('blocked_name_patterns', _rope_blocked_pats)]

            # ── Build allowed CSV value set from profile equipment labels ──
            allowed_csv: set = set(_always_include)
            _rope_in_profile = False

            for label in available_equipment:
                label_str = str(label).strip()
                if label_str in _frontend_to_csv:
                    for csv_val in _frontend_to_csv[label_str]:
                        allowed_csv.add(csv_val.lower())
                        if csv_val.lower() == 'rope':
                            _rope_in_profile = True
                else:
                    lower_label = label_str.lower()
                    allowed_csv.add(lower_label)
                    if lower_label == 'dumbbell':
                        allowed_csv.add('dumbbells')
                    if lower_label == 'barbell':
                        allowed_csv.add('barbells')
                # Handle "Jump Rope" label directly
                if 'jump rope' in label_str.lower():
                    allowed_csv.add('rope')
                    _rope_in_profile = True

            # ── Row-level filter with Rope split logic ─────────────────────
            eq_series   = exercises['Equipment'].str.lower().str.strip()
            name_col    = 'Name' if 'Name' in exercises.columns else ('name' if 'name' in exercises.columns else None)
            name_series = exercises[name_col].str.lower().str.strip() if name_col else pd.Series([''] * len(exercises))

            def _is_allowed(eq_lc: str, nm_lc: str) -> bool:
                if eq_lc in _always_include or eq_lc == '':
                    return True
                if eq_lc == 'rope':
                    if not _rope_in_profile:
                        return False
                    for pat in _rope_blocked_pats:
                        if pat in nm_lc:
                            return False
                    for pat in _rope_allowed_pats:
                        if pat in nm_lc:
                            return True
                    return False  # Unknown rope name → block by default
                return eq_lc in allowed_csv

            mask = [
                _is_allowed(eq, nm)
                for eq, nm in zip(eq_series.tolist(), name_series.tolist())
            ]

            filtered = exercises[mask]

            if filtered.empty:
                print(f" No exercises for equipment: {available_equipment}, returning all")
                return exercises

            print(f" Filtered to {len(filtered)} exercises (home-safe policy)")
            return filtered

        except Exception as e:
            print(f" Error filtering by equipment: {e}")
            return exercises

    def filter_by_injuries(self, exercises: pd.DataFrame, body_issues: List[str]) -> pd.DataFrame:
        """Filter exercises to avoid injuries - RULE-BASED SAFETY LOGIC"""
        if not body_issues or exercises.empty:
            return exercises

        try:
            if 'Avoid_If' not in exercises.columns:
                print(" 'Avoid_If' column not found")
                return exercises

            filtered = exercises.copy()

            for issue in body_issues:
                filtered = filtered[
                    ~filtered['Avoid_If'].str.contains(issue, case=False, na=False)
                ]
                if 'shoulder' in issue.lower():
                    # Rule-based safety logic: filter out exercises with shoulder forbidden terms
                    forbidden_words = ["pull-up", "pullup", "overhead press", "pike push", "handstand", "shoulder press", "military press", "neck press"]
                    pattern = "|".join(forbidden_words)
                    if 'Name' in filtered.columns:
                        filtered = filtered[~filtered['Name'].str.contains(pattern, case=False, na=False)]

            if filtered.empty:
                print(f" All exercises filtered out by injuries, returning safe defaults")
                return exercises

            print(f" Filtered out exercises for: {body_issues}")
            return filtered

        except Exception as e:
            print(f" Error filtering by injuries: {e}")
            return exercises

    def _build_feature_vector(self, profile: dict) -> np.ndarray:
        """Build a comprehensive feature vector using the feature pipeline"""
        # Use the feature pipeline to process the user profile
        processed_profile = {
            'age': profile.get('age', 25),
            'weight': profile.get('weight', 70.0),
            'height': profile.get('height', 175.0),
            'gender': profile.get('gender', 'Male'),
            'experience': profile.get('experience', 'Beginner'),
            'goal': profile.get('goal', 'Muscle Gain'),
            'equipment': profile.get('equipment', []),
            'injuries': profile.get('body_issues', []),  # Map body_issues to injuries
            'days_per_week': profile.get('days_per_week', 4),
            'session_time': profile.get('session_time', 60),  # Default session time
            'workout_history_count': profile.get('workout_history_count', 0),  # Default to 0
            'streak_count': profile.get('streak', 0),  # Map streak to streak_count
            'consistency': profile.get('consistency', 0.7),
            'sleep_score': profile.get('sleep_score', 7.0),  # Default sleep score
            'hydration_score': profile.get('hydration_score', 7.0),  # Default hydration score
            'stress_level': profile.get('stress_level', 5.0)  # Default stress level
        }
        
        # Process through the feature pipeline
        features = self.feature_pipeline.process_user_profile(processed_profile)
        
        return features

    def _get_multi_output_predictions(self, profile: dict) -> list:
        if self.multi_output_model.model is None:
            return None
        
        try:
            feature_vector = self._build_feature_vector(profile)
            feature_array = feature_vector.reshape(1, -1)
            feature_df = pd.DataFrame(feature_array, columns=self.feature_pipeline.get_feature_importance_template()['raw_features'] + 
                                      self.feature_pipeline.get_feature_importance_template()['derived_features'] +
                                      ['experience_encoded', 'goal_encoded', 'gender_encoded'] +
                                      [f'equipment_encoded_{i}' for i in range(feature_array.shape[1]-17)] +
                                      [f'injury_encoded_{i}' for i in range(5)])
            
            predictions = self.multi_output_model.predict(feature_df)
            return predictions[0]  # [sets, reps_low, reps_high, rest_time, intensity]
        except Exception as e:
            return None

    def _get_intensity_adjustment(self, profile: dict) -> float:
        """Get intensity adjustment based on ML model or rules - HYBRID APPROACH"""
        feature_vector = self._build_feature_vector(profile)

        # Try to use multi-output model if available
        predictions = self._get_multi_output_predictions(profile)
        if predictions is not None:
            try:
                # Extract intensity from the predictions (assuming it's the 5th element: [sets, reps_low, reps_high, rest_time, intensity])
                ml_intensity = predictions[4]  # Index 4 corresponds to intensity
                validated_intensity = max(0.1, min(1.0, ml_intensity))
                print(f"    Multi-output ML predicted intensity: {ml_intensity:.2f}, validated: {validated_intensity:.2f}")
                return float(validated_intensity)
            except Exception as e:
                print(f" Multi-output ML intensity extraction failed: {e}")

        # Fall back to original logic
        experience = profile.get('experience', 'Beginner')
        if experience == 'Beginner':
            return 0.7
        elif experience == 'Intermediate':
            return 0.85
        else:
            return 1.0

    def _get_optimized_workout_split(self, profile: dict, days_per_week: int) -> List[str]:
        """Get workout split optimized by ML model with rule-based validation - HYBRID APPROACH"""
        allowed_splits = {
            1: [['Full Body']],
            2: [['Upper Body', 'Lower Body'], ['Push', 'Pull']],
            3: [['Upper Body', 'Lower Body', 'Full Body'], ['Push', 'Pull', 'Legs']],
            4: [['Chest & Triceps', 'Back & Biceps', 'Legs', 'Shoulders & Core']],
            5: [['Chest', 'Back', 'Legs', 'Shoulders', 'Arms']],
            6: [['Chest', 'Back', 'Legs', 'Shoulders', 'Arms', 'Core']],
            7: [['Chest', 'Back', 'Legs', 'Shoulders', 'Arms', 'Core', 'Active Recovery']]
        }

        if self.xgb_split_model is not None:
            try:
                feature_vector = self._build_feature_vector(profile)
                ml_prediction = self.xgb_split_model.predict(feature_vector.reshape(1, -1))[0]
                split_idx = int(ml_prediction) % len(allowed_splits.get(days_per_week, allowed_splits[4]))
                valid_splits = allowed_splits.get(days_per_week, allowed_splits[4])
                split = valid_splits[split_idx % len(valid_splits)]
                print(f"    ML selected split: {split}")
                return split
            except Exception as e:
                print(f" ML split selection failed: {e}")

        return self._generate_dynamic_split(days_per_week, profile.get('goal', 'Muscle Gain'))

    def _get_optimized_training_volume(self, profile: dict) -> tuple:
        """Get optimized training volume (sets, reps, rest) using ML with rule-based validation - HYBRID APPROACH"""
        if self.xgb_volume_model is not None:
            try:
                feature_vector = self._build_feature_vector(profile)
                ml_prediction = self.xgb_volume_model.predict(feature_vector.reshape(1, -1))[0]
                volume_level = int(ml_prediction) % 3
                base_sets = 3 + volume_level
                base_reps = ['8-12', '6-10', '4-8'][volume_level]
                base_rest = [60, 90, 120][volume_level]

                experience = profile.get('experience', 'Beginner')
                goal = profile.get('goal', 'Muscle Gain')

                if experience == 'Beginner':
                    base_sets = min(base_sets, 4)
                    base_rest = max(base_rest, 60)

                if goal == 'Endurance':
                    base_reps = '12-15'
                    base_rest = 30

                print(f"    ML optimized volume: {base_sets} sets, {base_reps} reps, {base_rest}s rest")
                return base_sets, base_reps, base_rest
            except Exception as e:
                print(f" ML volume optimization failed: {e}")

        experience = profile.get('experience', 'Beginner')
        goal = profile.get('goal', 'Muscle Gain')
        sets = self._calculate_sets(experience, goal)
        reps = self._calculate_reps(goal, 0.8)
        rest = self._calculate_rest_time(goal, experience)
        return sets, reps, rest

    def _get_optimized_sets(self, profile: dict) -> int:
        """Get optimized number of sets using ML with rule-based validation - HYBRID APPROACH"""
        predictions = self._get_multi_output_predictions(profile)
        if predictions is not None:
            try:
                sets = int(round(predictions[0]))

                experience = profile.get('experience', 'Beginner')
                goal = profile.get('goal', 'Muscle Gain')

                if experience == 'Beginner':
                    sets = min(sets, 4)
                elif experience == 'Intermediate':
                    sets = min(sets, 5)
                else:
                    sets = min(sets, 6)

                if goal == 'Endurance':
                    sets = min(sets, 4)

                sets = max(sets, 2)
                print(f"    Multi-output ML optimized sets: {sets}")
                return sets
            except Exception as e:
                print(f" Multi-output ML sets prediction failed: {e}")

        if self.xgb_sets_model is not None:
            try:
                feature_vector = self._build_feature_vector(profile)
                ml_prediction = self.xgb_sets_model.predict(feature_vector.reshape(1, -1))[0]
                sets = int(round(ml_prediction))

                experience = profile.get('experience', 'Beginner')
                goal = profile.get('goal', 'Muscle Gain')

                if experience == 'Beginner':
                    sets = min(sets, 4)
                elif experience == 'Intermediate':
                    sets = min(sets, 5)
                else:
                    sets = min(sets, 6)

                if goal == 'Endurance':
                    sets = min(sets, 4)

                sets = max(sets, 2)
                print(f"    ML optimized sets: {sets}")
                return sets
            except Exception as e:
                print(f" ML sets optimization failed: {e}")

        experience = profile.get('experience', 'Beginner')
        goal = profile.get('goal', 'Muscle Gain')
        return self._calculate_sets(experience, goal)

    def _get_optimized_reps(self, profile: dict, intensity: float) -> str:
        """Get optimized rep range using ML with rule-based validation - HYBRID APPROACH"""
        predictions = self._get_multi_output_predictions(profile)
        if predictions is not None:
            try:
                rep_low = int(round(predictions[1]))
                rep_high = int(round(predictions[2]))
                
                goal = profile.get('goal', 'Muscle Gain')
                rep_low = max(rep_low, 1)
                rep_high = max(rep_low + 2, min(rep_high, 30))
                
                rep_range = f"{rep_low}-{rep_high}"
                print(f"    Multi-output ML optimized reps: {rep_range}")
                return rep_range
            except Exception as e:
                print(f" Multi-output ML reps prediction failed: {e}")

        if self.xgb_reps_model is not None:
            try:
                feature_vector = self._build_feature_vector(profile)
                ml_prediction = self.xgb_reps_model.predict(feature_vector.reshape(1, -1))[0]
                rep_value = int(round(ml_prediction))
                goal = profile.get('goal', 'Muscle Gain')

                if goal == 'Strength':
                    rep_range = f"{max(1, rep_value - 2)}-{max(rep_value - 1, 3)}"
                elif goal == 'Endurance':
                    rep_range = f"{rep_value + 2}-{rep_value + 6}"
                else:
                    rep_range = f"{max(1, rep_value - 1)}-{rep_value + 3}"

                parts = rep_range.split('-')
                low = int(parts[0])
                high = int(parts[1])

                if goal == 'Strength':
                    low = max(low, 1)
                    high = min(high, 8)
                elif goal == 'Endurance':
                    low = max(low, 12)
                    high = min(high, 20)
                else:
                    low = max(low, 6)
                    high = min(high, 15)

                rep_range = f"{low}-{high}"
                print(f"    ML optimized reps: {rep_range}")
                return rep_range
            except Exception as e:
                print(f" ML reps optimization failed: {e}")

        goal = profile.get('goal', 'Muscle Gain')
        return self._calculate_reps(goal, intensity)

    def _get_optimized_rest_time(self, profile: dict) -> int:
        """Get optimized rest time using ML with rule-based validation - HYBRID APPROACH"""
        predictions = self._get_multi_output_predictions(profile)
        if predictions is not None:
            try:
                rest_time = int(round(predictions[3]))

                experience = profile.get('experience', 'Beginner')
                goal = profile.get('goal', 'Muscle Gain')

                if experience == 'Beginner':
                    rest_time = max(rest_time, 60)
                elif experience == 'Advanced':
                    rest_time = max(rest_time, 30)

                if goal == 'Strength':
                    rest_time = max(rest_time, 120)
                elif goal == 'Endurance':
                    rest_time = min(rest_time, 60)

                rest_time = max(30, min(rest_time, 300))
                print(f"    Multi-output ML optimized rest: {rest_time}s")
                return rest_time
            except Exception as e:
                print(f" Multi-output ML rest prediction failed: {e}")

        if self.xgb_rest_model is not None:
            try:
                feature_vector = self._build_feature_vector(profile)
                ml_prediction = self.xgb_rest_model.predict(feature_vector.reshape(1, -1))[0]
                rest_time = int(round(ml_prediction))

                experience = profile.get('experience', 'Beginner')
                goal = profile.get('goal', 'Muscle Gain')

                if experience == 'Beginner':
                    rest_time = max(rest_time, 60)
                elif experience == 'Advanced':
                    rest_time = max(rest_time, 30)

                if goal == 'Strength':
                    rest_time = max(rest_time, 120)
                elif goal == 'Endurance':
                    rest_time = min(rest_time, 60)

                rest_time = max(30, min(rest_time, 300))
                print(f"    ML optimized rest: {rest_time}s")
                return rest_time
            except Exception as e:
                print(f" ML rest optimization failed: {e}")

        goal = profile.get('goal', 'Muscle Gain')
        experience = profile.get('experience', 'Beginner')
        return self._calculate_rest_time(goal, experience)

    def _get_optimized_frequency(self, profile: dict) -> int:
        """Get optimized training frequency using ML with rule-based validation - HYBRID APPROACH"""
        if 'days_per_week' in profile and profile.get('days_per_week') is not None:
            return max(1, min(int(profile.get('days_per_week')), 7))

        if self.xgb_frequency_model is not None:
            try:
                feature_vector = self._build_feature_vector(profile)
                ml_prediction = self.xgb_frequency_model.predict(feature_vector.reshape(1, -1))[0]

                frequency = int(round(ml_prediction))
                experience = profile.get('experience', 'Beginner')
                goal = profile.get('goal', 'Muscle Gain')

                if experience == 'Beginner':
                    frequency = min(frequency, 4)
                elif experience == 'Intermediate':
                    frequency = min(frequency, 5)
                else:
                    frequency = min(frequency, 6)

                if goal == 'Recovery' or goal == 'Maintenance':
                    frequency = min(frequency, 3)

                return max(1, min(frequency, 7))
            except Exception as e:
                print(f" ML frequency optimization failed: {e}")

        return profile.get('days_per_week', 4)

    def _get_optimized_progression(self, profile: dict) -> Dict:
        """Get optimized progression timing using ML with rule-based validation - HYBRID APPROACH"""
        if self.xgb_progression_model is not None:
            try:
                feature_vector = self._build_feature_vector(profile)
                ml_prediction = self.xgb_progression_model.predict(feature_vector.reshape(1, -1))[0]
                weeks_until_progression = int(max(1, round(ml_prediction)))
                experience = profile.get('experience', 'Beginner')

                if experience == 'Beginner':
                    weeks_until_progression = max(weeks_until_progression, 3)
                elif experience == 'Advanced':
                    weeks_until_progression = min(weeks_until_progression, 2)

                weeks_until_progression = min(weeks_until_progression, 4)

                progression_info = {
                    'weeks_until_next_progression': weeks_until_progression,
                    'progression_method': 'volume_increase' if weeks_until_progression <= 2 else 'intensity_increase'
                }

                print(f"    ML optimized progression: {progression_info}")
                return progression_info
            except Exception as e:
                print(f" ML progression optimization failed: {e}")

        experience = profile.get('experience', 'Beginner')
        return {
            'weeks_until_next_progression': 2 if experience == 'Beginner' else 1,
            'progression_method': 'intensity_increase'
        }

    def _generate_dynamic_split(self, days_per_week: int, goal: str) -> List[str]:
        """Generate workout split based on days and goal - RULE-BASED LOGIC"""
        splits = {
            3: ['Upper Body', 'Lower Body', 'Full Body'],
            4: ['Chest & Triceps', 'Back & Biceps', 'Legs', 'Shoulders & Core'],
            5: ['Chest', 'Back', 'Legs', 'Shoulders', 'Arms'],
            6: ['Chest', 'Back', 'Legs', 'Shoulders', 'Arms', 'Core'],
            7: ['Chest', 'Back', 'Legs', 'Shoulders', 'Arms', 'Core', 'Active Recovery']
        }

        return splits.get(days_per_week, splits[4])

    def _calculate_rest_days(self, days_per_week: int, profile: dict = None, intensity: float = None) -> List[int]:
        """Calculate optimal rest days in the week using intensity-aware logic"""
        rest_days = 7 - days_per_week

        if rest_days <= 0:
            return []

        if intensity is None:
            intensity = 0.75

        if intensity >= 0.85:
            positions = []
            for i in range(rest_days):
                pos = int(round((i + 1) * 7 / (rest_days + 1))) - 1
                pos = max(0, min(6, pos))
                positions.append(pos)
            unique = []
            for p in positions:
                if p not in unique:
                    unique.append(p)
            while len(unique) < rest_days:
                for p in range(7):
                    if p not in unique:
                        unique.append(p)
                        if len(unique) == rest_days:
                            break
            return sorted(unique)

        if intensity <= 0.65:
            return list(range(7 - rest_days, 7))

        if self.xgb_rest_model is not None and profile is not None:
            try:
                experience = profile.get('experience', 'Beginner')

                if experience == 'Beginner':
                    if rest_days == 1:
                        return [3]
                    elif rest_days == 2:
                        return [2, 5]
                    elif rest_days == 3:
                        return [1, 3, 5]
                    else:
                        return [0, 2, 4, 6]
                elif experience == 'Advanced':
                    if rest_days == 1:
                        return [6]
                    elif rest_days == 2:
                        return [5, 6]
                    else:
                        return [0, 3, 6]
                else:
                    if rest_days == 1:
                        return [3]
                    elif rest_days == 2:
                        return [2, 6]
                    elif rest_days == 3:
                        return [1, 4, 6]
                    else:
                        return [0, 2, 4, 6]

            except Exception as e:
                print(f" ML rest day calculation failed: {e}")

        if rest_days == 1:
            return [3]
        elif rest_days == 2:
            return [2, 5]
        elif rest_days == 3:
            return [1, 3, 5]
        elif rest_days == 4:
            return [0, 2, 4, 6]
        else:
            interval = 7 // (rest_days + 1)
            return [i * interval for i in range(1, rest_days + 1)]

    def _create_optimal_schedule(self, weekly_plan: List[Dict], rest_days: List[int]) -> List[Dict]:
        """Create week schedule with rest days - HYBRID APPROACH"""
        schedule = []
        workout_index = 0

        for day in range(7):
            if day in rest_days:
                schedule.append({
                    'day': f'Day {day + 1}',
                    'day_of_week': day,
                    'focus': 'Rest',
                    'exercises': []
                })
            else:
                if workout_index < len(weekly_plan):
                    schedule.append(weekly_plan[workout_index])
                    workout_index += 1

        return schedule

    def _calculate_exercise_count(self, experience: str, goal: str) -> int:
        """Calculate number of exercises per workout - RULE-BASED LOGIC"""
        base_counts = {
            'Beginner': 5,
            'Intermediate': 6,
            'Advanced': 7
        }

        count = base_counts.get(experience, 6)

        if goal == 'Endurance':
            count += 1

        return count

    def _calculate_sets(self, experience: str, goal: str) -> int:
        """Calculate number of sets - RULE-BASED LOGIC"""
        if experience == 'Beginner':
            return 3
        elif experience == 'Intermediate':
            return 4
        else:
            return 5 if goal == 'Muscle Gain' else 4

    def _calculate_reps(self, goal: str, intensity: float) -> str:
        """Calculate rep range based on goal - RULE-BASED LOGIC"""
        if goal == 'Strength':
            return '4-6' if intensity > 0.9 else '5-8'
        elif goal == 'Muscle Gain':
            return '8-12'
        elif goal == 'Endurance':
            return '12-15'
        else:
            return '10-15'

    def _calculate_rest_time(self, goal: str, experience: str) -> int:
        """Calculate rest time between sets - RULE-BASED LOGIC"""
        if goal == 'Strength':
            return 180 if experience == 'Advanced' else 120
        elif goal == 'Muscle Gain':
            return 90 if experience == 'Advanced' else 60
        elif goal == 'Endurance':
            return 45
        else:
            return 30

    def _adjust_reps_for_intensity(self, base_reps: str, intensity: float) -> str:
        """Adjust reps based on intensity - RULE-BASED LOGIC"""
        if intensity < 0.7:
            return base_reps

        parts = base_reps.split('-')
        if len(parts) == 2:
            low = int(parts[0])
            high = int(parts[1])

            if intensity > 0.9:
                low = max(low - 2, 1)
                high = max(high - 2, low + 2)

            return f"{low}-{high}"

        return base_reps

    def _estimate_reps_avg(self, reps_range: str) -> float:
        """Estimate avg reps from a range string like '8-12'"""
        try:
            parts = str(reps_range).split('-')
            if len(parts) == 2:
                low = float(parts[0])
                high = float(parts[1])
                return (low + high) / 2.0
            return float(parts[0])
        except Exception:
            return 10.0

    def _apply_age_based_caps(self, profile: dict, sets: int, reps: str, rest_time: int, intensity: float) -> tuple:
        """Apply age-based safety caps to workout parameters - RULE-BASED SAFETY LOGIC"""
        try:
            age = int(float(profile.get('age', 30)))
        except Exception:
            age = 30

        # Log initial values before applying rules
        print(f"    Age-based safety check: age={age}, initial sets={sets}, reps='{reps}', rest={rest_time}s, intensity={intensity:.2f}")

        # Apply age-appropriate limits
        if age > 65:
            # For older adults, reduce intensity and volume
            original_intensity = intensity
            original_sets = sets
            original_rest = rest_time

            intensity = min(intensity, 0.7)
            sets = min(sets, 3)
            rest_time = max(rest_time, 90)  # More rest for recovery

            # Adjust reps to safer range for older adults
            try:
                low, high = map(int, reps.split('-'))
                low = max(low, 8)  # Minimum of 8 reps to avoid heavy loads
                high = min(high, 15)  # Maximum of 15 reps
                reps = f"{low}-{high}"
            except ValueError:
                # Handle cases where reps is not in x-y format
                print(f"    Reps format not recognized: '{reps}', using default safe range")
                reps = "10-15"

            # Log changes applied by rules
            if original_intensity != intensity or original_sets != sets or original_rest != rest_time:
                print(f"    Applied senior safety rules: intensity {original_intensity:.2f}->{intensity:.2f}, sets {original_sets}->{sets}, rest {original_rest}s->{rest_time}s")

        elif age < 18:
            # For younger individuals, focus on form over heavy loads
            original_intensity = intensity
            original_sets = sets

            intensity = min(intensity, 0.8)
            sets = min(sets, 4)

            # Higher rep ranges for skill development
            try:
                low, high = map(int, reps.split('-'))
                low = max(low, 10)
                high = min(high, 20)
                reps = f"{low}-{high}"
            except ValueError:
                # Handle cases where reps is not in x-y format
                print(f"    Reps format not recognized: '{reps}', using default safe range")
                reps = "12-15"

            # Log changes applied by rules
            if original_intensity != intensity or original_sets != sets:
                print(f"    Applied youth safety rules: intensity {original_intensity:.2f}->{intensity:.2f}, sets {original_sets}->{sets}")

        else:
            print(f"    No age-based adjustments needed for age {age}")

        return sets, reps, rest_time, intensity

    def _filter_biomechanics(self, exercises: pd.DataFrame, profile: dict) -> pd.DataFrame:
        """Filter exercises based on biomechanical safety - RULE-BASED SAFETY LOGIC"""
        if exercises.empty:
            return exercises

        try:
            print(f"    Applying biomechanical safety filters...")

            original_count = len(exercises)
            experience = profile.get('experience', 'Beginner')
            try:
                age = int(float(profile.get('age', 30)))
            except Exception:
                age = 30

            # For beginners, filter out complex movements
            if experience == 'Beginner' and 'Name' in exercises.columns:
                # Avoid overly complex exercises for beginners
                complex_exercises_keywords = ['Olympic lift', 'Clean and jerk', 'Snatch', 'Advanced', 'Plyometric']

                for keyword in complex_exercises_keywords:
                    exercises = exercises[
                        ~exercises['Name'].str.contains(keyword, case=False, na=False)
                    ]

            # Use Check_Type column if available (e.g., filter out cardio for strength-focused plans)
            if 'Check_Type' in exercises.columns:
                goal = profile.get('goal', 'Muscle Gain')

                # For strength-focused goals, prioritize strength exercises
                if goal == 'Strength' and 'strength' in exercises['Check_Type'].values:
                    exercises = exercises[exercises['Check_Type'] == 'strength']
                elif goal == 'Endurance' and 'cardio' in exercises['Check_Type'].values:
                    # For endurance-focused goals, include more cardio exercises
                    pass  # Allow all types but this could be expanded

            # Use Risk_Level column if available (assuming lower risk is better for beginners)
            if 'Risk_Level' in exercises.columns:
                risk_mapping = {'Low': 1, 'Medium': 2, 'High': 3}

                if experience == 'Beginner':
                    # Filter out high-risk exercises for beginners
                    exercises = exercises[
                        exercises['Risk_Level'].map(risk_mapping).fillna(2) <= 2
                    ]  # Allow Low and Medium risk
                elif age > 65:
                    # For seniors, only allow low-risk exercises
                    exercises = exercises[
                        exercises['Risk_Level'].map(risk_mapping).fillna(1) <= 1
                    ]  # Only Low risk
            else:
                # If Risk_Level column doesn't exist, create a basic risk assessment based on other factors
                print(f"    Risk_Level column not found, using basic heuristics for safety")

            # Additional biomechanical filters based on age
            if age > 65:
                # Avoid high-impact exercises for seniors
                high_impact_keywords = ['jump', 'plyo', 'explosive', 'sprint']
                for keyword in high_impact_keywords:
                    exercises = exercises[
                        ~exercises['Name'].str.contains(keyword, case=False, na=False)
                    ]

            # Log the results of biomechanical filtering
            filtered_count = len(exercises)
            if original_count != filtered_count:
                print(f"    Applied biomechanical filters: {original_count} -> {filtered_count} exercises")
            else:
                print(f"    No biomechanical filters applied, kept all {original_count} exercises")

            return exercises

        except Exception as e:
            print(f" Error in biomechanics filtering: {e}")
            return exercises

    def _infer_rest_days_count(self, profile: dict, intensity: float, sets: int, reps: str, num_exercises: int) -> int:
        """Decide rest days based on weekly load + profile (MODEL-DRIVEN LOGIC)"""
        reps_avg = self._estimate_reps_avg(reps)
        weekly_load = intensity * sets * reps_avg * num_exercises * 7

        if weekly_load >= 300:
            rest_days = 3
        elif weekly_load >= 220:
            rest_days = 2
        elif weekly_load >= 150:
            rest_days = 1
        else:
            rest_days = 0

        experience = profile.get('experience', 'Beginner')
        goal = profile.get('goal', 'Muscle Gain')
        streak = profile.get('streak', 0)
        consistency = profile.get('consistency', 0.7)

        if experience == 'Beginner':
            rest_days += 1
        elif experience == 'Advanced':
            rest_days -= 1

        if goal in ['Strength', 'Recovery']:
            rest_days += 1
        if goal == 'Endurance':
            rest_days -= 1

        if streak >= 10 and consistency >= 0.8:
            rest_days -= 1

        return max(0, min(3, rest_days))

    # ──────────────────────────────────────────────────────────────────────────
    # Issue #1 – Rolling week: build an adaptive partial week for new users
    # ──────────────────────────────────────────────────────────────────────────
    def _is_registration_in_current_week(self, registration_value) -> bool:
        """Return True when registration date belongs to the current ISO week."""
        if not registration_value:
            return False

        reg_dt = None
        if isinstance(registration_value, datetime):
            reg_dt = registration_value
        else:
            text = str(registration_value).strip()
            if not text:
                return False
            text = text.replace('Z', '+00:00')
            try:
                reg_dt = datetime.fromisoformat(text)
            except Exception:
                try:
                    reg_dt = datetime.strptime(text[:10], '%Y-%m-%d')
                except Exception:
                    return False

        now_year, now_week, _ = datetime.utcnow().isocalendar()
        reg_year, reg_week, _ = reg_dt.isocalendar()
        return now_year == reg_year and now_week == reg_week

    def _calculate_partial_week_ratio(self, total_available: int,
                                      preferred_workout_days: int,
                                      experience: str) -> Dict[str, int]:
        """Return a safe workout/rest split for shortened new-user weeks."""
        total_available = max(1, min(7, int(total_available or 1)))
        preferred_workout_days = max(1, min(7, int(preferred_workout_days or 4)))
        experience = str(experience or 'Beginner')

        if total_available <= 1:
            return {'workout_days': 1, 'rest_days': 0}
        if total_available == 2:
            return {'workout_days': 1, 'rest_days': 1}
        if total_available == 3:
            return {'workout_days': 2, 'rest_days': 1}
        if total_available == 4:
            if experience == 'Beginner':
                return {'workout_days': 2, 'rest_days': 2}
            return {'workout_days': 3, 'rest_days': 1}
        if total_available == 5:
            if experience == 'Advanced':
                return {'workout_days': 4, 'rest_days': 1}
            return {'workout_days': 3, 'rest_days': 2}

        workout_days = min(preferred_workout_days, total_available - 1)
        workout_days = max(1, workout_days)
        return {'workout_days': workout_days, 'rest_days': total_available - workout_days}

    def _select_partial_week_splits(self, workout_day_count: int,
                                    experience: str, goal: str) -> List[str]:
        """Choose a practical split for short onboarding weeks."""
        workout_day_count = max(0, int(workout_day_count or 0))
        if workout_day_count == 0:
            return []

        if experience == 'Beginner':
            beginner_patterns = {
                1: ['Full Body (Intro)'],
                2: ['Full Body A', 'Full Body B'],
                3: ['Full Body (Upper Focus)', 'Full Body (Lower Focus)', 'Full Body (Push-Pull)'],
                4: ['Upper Body', 'Lower Body', 'Full Body (Push Focus)', 'Full Body (Pull Focus)'],
            }
            template = beginner_patterns.get(workout_day_count, beginner_patterns[4])
            if len(template) >= workout_day_count:
                return template[:workout_day_count]

        base_split = self._get_split_for_experience(experience, max(3, workout_day_count), goal)
        while len(base_split) < workout_day_count:
            base_split.append('Full Body')
        return base_split[:workout_day_count]

    def _ensure_non_consecutive_rests(self, rest_positions: Set[int],
                                      available_indices: List[int]) -> Set[int]:
        """Shift rest days when possible so two rests are never adjacent."""
        if not rest_positions:
            return set()

        available_set = set(available_indices)
        ordered = sorted(rest_positions)
        normalized: List[int] = []

        for rest_day in ordered:
            if not normalized:
                normalized.append(rest_day)
                continue

            previous = normalized[-1]
            if rest_day - previous != 1:
                normalized.append(rest_day)
                continue

            # Try moving current rest one day forward.
            shifted_forward = rest_day + 1
            if shifted_forward in available_set and shifted_forward not in normalized and shifted_forward - previous > 1:
                normalized.append(shifted_forward)
                continue

            # Try moving previous rest one day backward.
            shifted_back = previous - 1
            if shifted_back in available_set and shifted_back not in normalized:
                if len(normalized) == 1 or shifted_back - normalized[-2] > 1:
                    normalized[-1] = shifted_back
                    if rest_day - shifted_back > 1:
                        normalized.append(rest_day)
                    continue

            # Keep only one of the consecutive rests as a safe fallback.
            continue

        return set(normalized)

    def _build_partial_week_rest_positions(self, available_indices: List[int],
                                           rest_count: int) -> Set[int]:
        """Place rest days across available days while preserving day-one onboarding."""
        if rest_count <= 0 or not available_indices:
            return set()

        # Keep registration day as workout to avoid a dead first impression.
        candidate_days = list(available_indices[1:]) if len(available_indices) > 1 else []
        if not candidate_days:
            return set()

        rest_count = min(rest_count, len(candidate_days))
        if rest_count <= 0:
            return set()

        positions: Set[int] = set()
        interval = len(candidate_days) / float(rest_count + 1)
        for i in range(rest_count):
            idx = int(round((i + 1) * interval - 1))
            idx = max(0, min(len(candidate_days) - 1, idx))
            positions.add(candidate_days[idx])

        if len(positions) < rest_count:
            for day_idx in candidate_days:
                positions.add(day_idx)
                if len(positions) >= rest_count:
                    break

        return self._ensure_non_consecutive_rests(positions, available_indices)

    def _build_new_user_plan(self, profile: dict, split: List[str],
                              user_start_day: int) -> List[Dict]:
        """Build an adaptive onboarding week that starts from registration day."""
        day_names = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        goal = profile.get('goal', 'Muscle Gain')
        experience = profile.get('experience', 'Beginner')
        equipment = profile.get('equipment', ['Body Weight'])
        body_issues = profile.get('body_issues', [])

        user_start_day = max(0, min(6, int(user_start_day or 0)))
        available_indices = list(range(user_start_day, 7))
        total_available = len(available_indices)

        ratio = self._calculate_partial_week_ratio(
            total_available=total_available,
            preferred_workout_days=int(profile.get('days_per_week', 4) or 4),
            experience=experience,
        )

        workout_day_count = ratio['workout_days']
        rest_day_count = ratio['rest_days']
        partial_splits = self._select_partial_week_splits(workout_day_count, experience, goal)
        rest_positions = self._build_partial_week_rest_positions(available_indices, rest_day_count)

        weekly_plan: List[Dict] = []
        split_idx = 0
        global_used_names: Set[str] = set()

        for day_idx in range(7):
            if day_idx < user_start_day:
                weekly_plan.append({
                    'day_of_week': day_idx,
                    'day': day_names[day_idx],
                    'focus': 'Not Started',
                    'exercises': [],
                    'type': 'past',
                    'is_placeholder': True,
                    'can_access': False,
                    'status': 'NOT_STARTED',
                    'intensity': 0,
                    'note': 'You joined after this day',
                    'status_message': 'Your fitness journey starts today!',
                    'is_original_rest': False,
                    'is_original_workout': False,
                    'is_swapped': False,
                    'swapped_from': None,
                    'swapped_to': None,
                    'is_swappable': False,
                    'is_completed': False,
                    'exercises_completed': 0,
                    'exercises_total': 0,
                })
                continue

            if day_idx in rest_positions or split_idx >= len(partial_splits):
                weekly_plan.append({
                    'day_of_week': day_idx,
                    'day': day_names[day_idx],
                    'focus': 'Rest Day',
                    'exercises': [],
                    'type': 'rest',
                    'is_placeholder': False,
                    'can_access': True,
                    'intensity': 0,
                    'note': 'Recovery and rest - light stretching recommended',
                    'is_original_rest': True,
                    'is_original_workout': False,
                    'is_swapped': False,
                    'swapped_from': None,
                    'swapped_to': None,
                    'is_swappable': True,
                    'is_completed': False,
                    'exercises_completed': 0,
                    'exercises_total': 0,
                    'intensity_metrics': self._build_intensity_metrics(0.0),
                })
                continue

            focus = partial_splits[split_idx]
            split_idx += 1

            day_seed = self._build_day_seed(profile, focus, day_idx)

            exercises = self._get_exercises_for_day(
                focus, goal, experience, equipment, body_issues, profile,
                day_seed=day_seed,
                global_used_names=global_used_names,
            )
            for ex in exercises:
                global_used_names.add(ex.get('name', ''))

            warmup = self._get_warmup_for_focus(focus, exercises=exercises, day_seed=day_seed)
            intensity_metrics = self._calculate_day_intensity(exercises, experience, goal, profile=profile)
            intensity_score = intensity_metrics.get('intensity_score', 0.0) if isinstance(intensity_metrics, dict) else float(intensity_metrics)
            full_session = self._enforce_unique_media_per_day(warmup + exercises)
            warmup_clean = [ex for ex in full_session if ex.get('is_warmup') is True]
            exercises_clean = [ex for ex in full_session if not ex.get('is_warmup')]

            weekly_plan.append({
                'day_of_week': day_idx,
                'day': day_names[day_idx],
                'focus': focus,
                'warmup': warmup_clean,
                'exercises': exercises_clean,
                'type': 'workout',
                'is_placeholder': False,
                'can_access': True,
                'intensity': round(intensity_score, 2),
                'note': f'{focus} training',
                'is_original_rest': False,
                'is_original_workout': True,
                'is_swapped': False,
                'swapped_from': None,
                'swapped_to': None,
                'is_swappable': True,
                'is_completed': False,
                'exercises_completed': 0,
                'exercises_total': len(exercises_clean),
                'intensity_metrics': self._build_intensity_metrics(intensity_metrics),
            })

        return weekly_plan

    def generate_weekly_plan(self, profile: dict, workout_history: List[Dict] = None,
                              user_start_day: Optional[int] = None,
                              is_new_user: bool = False,
                              registration_day: Optional[int] = None) -> List[Dict]:
        """
        Generate weekly workout plan – deterministic with optional Gemini guidance.

                Issue #1 support:
          user_start_day (0=Mon … 6=Sun): day the user registered; drives rolling week.
          is_new_user: when True, days before user_start_day are labelled 'past'.
                    registration_day: optional alias for user_start_day.

        Issue #4 support:
          Result is cached by profile hash + ISO week. Cache is checked first.
        """
        print(f"\n{'='*60}")
        print(f" GENERATING WEEKLY WORKOUT PLAN (DETERMINISTIC / AI DRIVEN)")
        print(f"{'='*60}")

        # Issue #4 – try cache first
        if self._plan_cache:
            cached = self._plan_cache.get(profile)
            if cached and not is_new_user:
                print("  [Cache] Returning cached weekly plan")
                return cached

        # Work on a local copy so transient generation fields never mutate caller state.
        profile = dict(profile)

        # If caller does not provide week_offset, derive one from ISO year/week.
        # This keeps generation deterministic within a week while rotating weekly.
        if profile.get('week_offset') is None:
            iso_year, iso_week, _ = datetime.utcnow().isocalendar()
            profile['week_offset'] = (iso_year * 100) + iso_week

        experience = profile.get('experience', 'Beginner')
        user_days = int(profile.get('days_per_week', 4))
        user_days = max(1, min(7, user_days))

        if user_start_day is None and registration_day is not None:
            user_start_day = int(registration_day)
            is_new_user = True

        # --- Detect new user start day from profile if not supplied ---
        if user_start_day is None:
            fwd = profile.get('firstWorkoutDay')
            registration_value = profile.get('registrationDate') or profile.get('registration_date')
            explicit_new_user_week = bool(profile.get('is_new_user_week'))

            if fwd is not None and (explicit_new_user_week or self._is_registration_in_current_week(registration_value)):
                user_start_day = int(fwd)
                is_new_user = True

        # --- Base Variables ---
        workout_days = user_days
        rest_day_positions = []
        streak = int(profile.get('streak', 0) or 0)
        consistency = float(profile.get('consistency', 0.7) or 0.7)

        # Experience-based weekly frequency with conservative progression gates.
        if experience == 'Beginner':
            recommended_days = 4 if (streak >= 21 and consistency >= 0.85) else 3
            if recommended_days == 4:
                print(f"  Beginner progression unlocked: 4 workout days, 3 rest days (streak={streak}, consistency={consistency:.0%})")
            else:
                print("  Beginner base split: 3 workout days, 4 rest days")
        elif experience == 'Intermediate':
            recommended_days = 5 if (streak >= 42 and consistency >= 0.90) else 4
            if recommended_days == 5:
                print(f"  Intermediate progression unlocked: 5 workout days, 2 rest days (streak={streak}, consistency={consistency:.0%})")
            else:
                print("  Intermediate base split: 4 workout days, 3 rest days")
        elif experience == 'Advanced':
            recommended_days = 6 if (streak >= 10 and consistency >= 0.80) else 5
            if recommended_days == 6:
                print(f"  Advanced progression unlocked: 6 workout days, 1 rest day (streak={streak}, consistency={consistency:.0%})")
            else:
                print("  Advanced base split: 5 workout days, 2 rest days")
        else:
            recommended_days = min(4, user_days)

        # Respect explicit user preference when it is lower than recommendation.
        workout_days = max(1, min(recommended_days, user_days))
        
        # --- Inject Gemini AI Intelligence Config ---
        # FIX: Disabled synchronous LLM call during workout generation to prevent 3-8s latency
        gemini_enabled = False
        if gemini_enabled:
            cfg = generate_workout_config(profile, 0.75)
            if cfg:
                g_sets, g_reps, g_rest, g_rest_days = cfg
                profile['_gemini_config'] = {
                    'sets': g_sets,
                    'reps': g_reps,
                    'rest': f"{g_rest} seconds"
                }
                rest_day_positions = sorted({int(d) for d in (g_rest_days or []) if 0 <= int(d) <= 6})
                gemini_workout_days = max(1, 7 - len(rest_day_positions))

                if gemini_workout_days != workout_days:
                    print(
                        f"  Gemini volume config applied ({g_sets} Sets | {g_reps} Reps | {g_rest}s Rest), "
                        f"but frequency policy keeps {workout_days} workout days; recomputing rest placement."
                    )
                    rest_day_positions = []
                else:
                    print(
                        f"  Gemini config applied: {g_sets} Sets | {g_reps} Reps | {g_rest}s Rest | "
                        f"{gemini_workout_days} Days On | Rest {rest_day_positions}"
                    )
            else:
                print("  Gemini config unavailable at runtime, falling back to rule-based schedule.")



        print(f"  Experience: {experience}")
        print(f"  User requested: {user_days} days")
        print(f"  Capped workout days: {workout_days}")
        if is_new_user and user_start_day is not None:
            print(f"  New user – week starts at day index {user_start_day}")

        # --- Step 2: Get workout split ---
        split = self._get_split_for_experience(experience, workout_days, profile.get('goal', 'Muscle Gain'), workout_history)
        print(f"  Split: {split}")

        # --- Step 3: Distribute rest days ---
        goal = profile.get('goal', 'Muscle Gain')
        if not rest_day_positions:
            # Issue #2 – use smart intensity-based rest placement
            rest_count_needed = 7 - workout_days
            rest_day_positions = self._calculate_smart_rest_days(
                split, rest_count_needed, experience, goal
            )
        print(f"  Rest day positions (0-indexed): {rest_day_positions}")

        # --- Step 4: Build the 7-day schedule ---
        if is_new_user and user_start_day is not None:
            weekly_plan = self._build_new_user_plan(profile, split, user_start_day)
        else:
            weekly_plan = self._build_weekly_plan(profile, split, rest_day_positions)

        total_exercises = sum(len(day.get('exercises', [])) for day in weekly_plan)
        workout_count = sum(1 for day in weekly_plan if day['type'] == 'workout')
        rest_count = sum(1 for day in weekly_plan if day['type'] == 'rest')

        # --- Inject debug_trace into each day of the plan for transparency and testing ---
        for day in weekly_plan:
            day['debug_trace'] = {
                'experience': experience,
                'goal': profile.get('goal', 'Muscle Gain'),
                'gender': profile.get('gender', 'Male'),
                'days_per_week_requested': user_days,
                'days_per_week_recommended': recommended_days,
                'days_per_week_capped': workout_days,
                'streak': streak,
                'consistency': consistency,
                'age': int(float(profile.get('age', 25))),
                'week_offset': profile.get('week_offset'),
            }

        print(f"\n  Generated: {workout_count} workout days, {rest_count} rest days, {total_exercises} total exercises")
        print(f"{'='*60}\n")

        # Issue #4 – cache the result
        if self._plan_cache and not is_new_user:
            self._plan_cache.set(profile, weekly_plan)

        return weekly_plan

    def _get_split_for_experience(self, experience: str, workout_days: int, goal: str, workout_history: List[Dict] = None) -> List[str]:
        """
        Return scientifically balanced muscle-group combinations by experience.
        Deterministic: same inputs always produce same split, unless history-based rotation applies.
        """
        workout_days = max(1, min(6, int(workout_days or 1)))

        # Stateful rotation: Determine the last workout focus from history
        last_focus = None
        if workout_history and len(workout_history) > 0:
            last_valid = [w for w in workout_history if isinstance(w, dict) and w.get('focus')]
            if last_valid:
                last_focus = last_valid[-1].get('focus')

        def _rotate(base: List[str]) -> List[str]:
            if not last_focus or last_focus not in base:
                return base
            idx = base.index(last_focus)
            shift = (idx + 1) % len(base)
            return base[shift:] + base[:shift]

        if experience == 'Beginner':
            patterns = {
                1: ['Full Body (Upper Focus)'],
                2: ['Full Body (Upper Focus)', 'Full Body (Lower Focus)'],
                3: ['Full Body (Upper Focus)', 'Full Body (Lower Focus)', 'Full Body (Push-Pull)'],
                4: ['Full Body (Upper Focus)', 'Full Body (Lower Focus)', 'Full Body (Push Focus)', 'Full Body (Pull Focus)'],
                5: ['Full Body (Upper Focus)', 'Full Body (Lower Focus)', 'Full Body (Push-Pull)', 'Full Body (Push Focus)', 'Full Body (Pull Focus)'],
                6: ['Full Body (Upper Focus)', 'Full Body (Lower Focus)', 'Full Body (Push-Pull)', 'Full Body (Push Focus)', 'Full Body (Pull Focus)', 'Full Body (Legs Focus)'],
            }
            template = patterns.get(workout_days, patterns[4])
            return _rotate(template)[:workout_days]

        elif experience == 'Intermediate':
            patterns = {
                3: ['Chest & Back', 'Legs & Shoulders', 'Arms & Core'],
                4: ['Chest & Back', 'Legs & Shoulders', 'Arms & Core', 'Pull & Legs'],
                5: ['Chest & Back', 'Legs & Shoulders', 'Arms & Core', 'Pull & Legs', 'Push & Pull'],
                6: ['Chest & Back', 'Legs & Shoulders', 'Arms & Core', 'Pull & Legs', 'Push & Pull', 'Shoulders & Traps'],
            }
            template = patterns.get(workout_days, patterns[4])
            return _rotate(template)[:workout_days]

        else:  # Advanced
            patterns = {
                3: ['Chest & Triceps', 'Back & Biceps', 'Legs (Quads)'],
                4: ['Chest & Triceps', 'Back & Biceps', 'Legs (Quads)', 'Shoulders & Traps'],
                5: ['Chest & Triceps', 'Back & Biceps', 'Legs (Quads)', 'Shoulders & Traps', 'Legs (Posterior)'],
                6: ['Chest & Triceps', 'Back & Biceps', 'Legs (Quads)', 'Shoulders & Traps', 'Legs (Posterior)', 'Arms & Core'],
            }
            template = patterns.get(workout_days, patterns[5])
            return _rotate(template)[:workout_days]

    def _distribute_rest_days(self, workout_days: int, split: List[str]) -> List[int]:
        """
        Distribute rest days in a 7-day week to maximize recovery.
        
        Rules:
        - Never place rest days at the very start if possible
        - Space rest days as evenly as possible
        - For PPL: rest after every 3rd day
        - For Upper/Lower: rest after every 2nd day
        - For Full Body: rest between every workout day
        """
        rest_count = 7 - workout_days

        if rest_count <= 0:
            return []

        if rest_count >= 4:
            # Many rest days - alternate workout/rest, fill remaining at end
            positions = []
            day = 1  # start placing rest after first workout
            for _ in range(rest_count):
                if day < 7 and day not in positions:
                    positions.append(day)
                day += 2
            for d in range(6, -1, -1):
                if len(positions) >= rest_count:
                    break
                if d not in positions:
                    positions.append(d)
            return sorted(positions[:rest_count])

        if rest_count == 1:
            return [3]   # Wednesday
        if rest_count == 2:
            return [2, 5]  # Wednesday + Saturday
        if rest_count == 3:
            return [2, 4, 6]

        interval = 7 / (rest_count + 1)
        return sorted([int(round(interval * (i + 1))) for i in range(rest_count)])

    # ──────────────────────────────────────────────────────────────────────────
    # Issue #2 – Smart rest day placement based on workout intensity
    # ──────────────────────────────────────────────────────────────────────────
    def _calculate_workout_intensity_score(self, focus: str, experience: str,
                                            goal: str) -> float:
        """
        Estimate 0-1 intensity for a workout focus without running full exercise selection.
        Used by the smart rest-day placer to avoid the high-cost exercise DB lookup at
        plan-layout time.
        """
        base = {'Beginner': 0.45, 'Intermediate': 0.65, 'Advanced': 0.85}.get(experience, 0.6)

        # Compound / heavy days are more stressful
        high_intensity_keywords = {'legs', 'quads', 'posterior', 'heavy', 'deadlift', 'squat', 'pull & legs'}
        focus_lower = focus.lower()
        intensity_boost = 0.12 if any(kw in focus_lower for kw in high_intensity_keywords) else 0.0

        # Goal modifier
        goal_adj = {'Strength': 0.1, 'Muscle Gain': 0.05, 'Endurance': -0.05}.get(goal, 0.0)

        return round(max(0.1, min(1.0, base + intensity_boost + goal_adj)), 3)

    def _get_muscle_group_from_focus(self, focus: str) -> Set[str]:
        """Return a simplified set of primary muscles for overlap detection."""
        muscle_map = {
            'Chest & Back': {'chest', 'back'},
            'Chest & Triceps': {'chest', 'triceps'},
            'Back & Biceps': {'back', 'biceps'},
            'Legs & Shoulders': {'quads', 'hamstrings', 'glutes', 'shoulders'},
            'Arms & Core': {'biceps', 'triceps', 'core', 'abs'},
            'Pull & Legs': {'back', 'biceps', 'quads', 'hamstrings', 'glutes'},
            'Push & Pull': {'chest', 'back', 'shoulders', 'biceps', 'triceps'},
            'Shoulders & Traps': {'shoulders', 'traps'},
            'Legs (Quads)': {'quads', 'glutes', 'calves'},
            'Legs (Posterior)': {'hamstrings', 'glutes', 'calves'},
            'Full Body (Upper Focus)': {'chest', 'back', 'shoulders', 'biceps', 'triceps'},
            'Full Body (Lower Focus)': {'quads', 'hamstrings', 'glutes', 'core'},
            'Full Body (Push-Pull)': {'chest', 'back', 'shoulders'},
            'Full Body (Push Focus)': {'chest', 'shoulders', 'triceps'},
            'Full Body (Pull Focus)': {'back', 'biceps'},
            'Full Body (Legs Focus)': {'quads', 'hamstrings', 'glutes', 'calves'},
            'Chest': {'chest', 'triceps'},
            'Push': {'chest', 'shoulders', 'triceps'},
            'Push (Heavy)': {'chest', 'shoulders', 'triceps'},
            'Push (Volume)': {'chest', 'shoulders', 'triceps'},
            'Back': {'back', 'biceps'},
            'Pull': {'back', 'biceps'},
            'Pull (Heavy)': {'back', 'biceps'},
            'Pull (Volume)': {'back', 'biceps'},
            'Legs': {'quads', 'hamstrings', 'glutes'},
            'Legs (Heavy)': {'quads', 'hamstrings', 'glutes'},
            'Legs (Volume)': {'quads', 'hamstrings', 'glutes', 'core'},
            'Shoulders': {'shoulders', 'traps'},
            'Arms': {'biceps', 'triceps'},
            'Core': {'core', 'abs'},
            'Upper Body': {'chest', 'back', 'shoulders', 'biceps', 'triceps'},
            'Lower Body': {'quads', 'hamstrings', 'glutes', 'core'},
            'Full Body': {'chest', 'back', 'legs', 'core', 'shoulders'},
        }
        focus_lower = focus.lower()
        for key, muscles in muscle_map.items():
            if key.lower() in focus_lower or focus_lower in key.lower():
                return muscles
        return {'general'}

    def _validate_muscle_recovery(self, schedule: List[Dict]) -> Dict:
        """
        Validate that no muscle group is trained again within 48 hours (2 consecutive
        active-workout days) in the given 7-day schedule.

        Args:
            schedule: list of day dicts as returned by _build_weekly_plan / generate_weekly_plan.
                      Each day must have 'day_of_week' (0-6), 'type' ('workout'|'rest'),
                      and 'focus' (str).

        Returns:
            {
                'valid': bool,
                'violations': [
                    {
                        'muscle': str,
                        'day_a': int,   # 0-indexed day that first trained the muscle
                        'day_b': int,   # 0-indexed day that trained it again too soon
                        'focus_a': str,
                        'focus_b': str,
                        'gap_days': int
                    },
                    ...
                ],
                'summary': str          # human-readable summary
            }
        """
        # Build (day_index, focus) for workout days only, sorted by day
        workout_days = sorted(
            [(d['day_of_week'], d['focus']) for d in schedule if d.get('type') == 'workout'],
            key=lambda x: x[0]
        )

        violations = []

        for i in range(len(workout_days)):
            day_a, focus_a = workout_days[i]
            muscles_a = self._get_muscle_group_from_focus(focus_a)

            for j in range(i + 1, len(workout_days)):
                day_b, focus_b = workout_days[j]
                gap = day_b - day_a          # days between the two sessions
                if gap >= 2:
                    break                    # 48 h satisfied; no need to check further

                muscles_b = self._get_muscle_group_from_focus(focus_b)
                overlap = muscles_a & muscles_b
                if overlap and 'general' not in overlap:
                    for muscle in sorted(overlap):
                        violations.append({
                            'muscle': muscle,
                            'day_a': day_a,
                            'day_b': day_b,
                            'focus_a': focus_a,
                            'focus_b': focus_b,
                            'gap_days': gap,
                        })

        valid = len(violations) == 0
        if valid:
            summary = 'All muscle groups have at least 48 h recovery between sessions.'
        else:
            unique_muscles = sorted({v['muscle'] for v in violations})
            summary = (
                f"{len(violations)} recovery violation(s) found for: "
                f"{', '.join(unique_muscles)}. "
                f"Consider adding a rest day or reordering sessions."
            )

        return {'valid': valid, 'violations': violations, 'summary': summary}

    def _calculate_smart_rest_days(self, split: List[str], rest_count: int,
                                    experience: str, goal: str) -> List[int]:
        """
        Place rest days so workouts are evenly spread across the 7-day week.

        Correct algorithm:
          1. Use even-interval spacing: interval = 7 / (rest_count + 1)
             e.g. rest_count=3 → interval=1.75 → rest at {2, 4, 5} (all within 0-6)
          2. After placing the base grid, swap a rest position to immediately
             follow a 'Legs' or 'Pull (Heavy)' day when that improves recovery
             without creating back-to-back rest days.

        Example outputs:
          4 workouts, 3 rest  → [2, 4, 6]  → Mon Tue [R] Thu [R] Sat [R]
          5 workouts, 2 rest  → [2, 5]     → Mon Tue [R] Thu Fri [R] Sun
          6 workouts, 1 rest  → [3]        → Mon Tue Wed [R] Fri Sat Sun
          3 workouts, 4 rest  → [1, 3, 5, 6]
        """
        if rest_count <= 0:
            return []
        if rest_count >= 7:
            return list(range(7))

        n_workout = len(split)

        # --- Step 1: evenly-spaced base grid ---
        # place rest days at round(interval * i) for i in 1..rest_count
        interval = 7.0 / (rest_count + 1)
        base_positions = []
        for i in range(1, rest_count + 1):
            pos = int(round(interval * i))
            pos = max(0, min(6, pos))
            base_positions.append(pos)

        # Deduplicate while preserving order
        seen = set()
        positions = []
        for p in base_positions:
            if p not in seen:
                seen.add(p)
                positions.append(p)

        # If dedup removed some, fill from end of week
        for d in range(6, 0, -1):
            if len(positions) >= rest_count:
                break
            if d not in seen:
                seen.add(d)
                positions.append(d)

        positions = sorted(positions[:rest_count])

        # --- Step 2: build day→split-slot map from base positions ---
        day_to_split: Dict[int, int] = {}
        si = 0
        for d in range(7):
            if d not in positions and si < n_workout:
                day_to_split[d] = si
                si += 1

        # --- Step 3: micro-adjust — move rest to immediately after heavy days ---
        high_intensity_keywords = {'legs', 'heavy'}
        adjusted = list(positions)

        for idx, rest_pos in enumerate(positions):
            before = rest_pos - 1
            if before < 0 or before not in day_to_split:
                continue
            split_slot = day_to_split[before]
            if split_slot >= len(split):
                continue
            focus_lower = split[split_slot].lower()
            is_heavy = any(kw in focus_lower for kw in high_intensity_keywords)
            if not is_heavy:
                # Check if the day AFTER the rest is heavy — if so, rest is already well placed
                continue
            # rest_pos already follows a heavy day — perfect, no adjustment needed
            # (we only adjust when rest is NOT after a heavy day, handled below)

        # Find heavy days that are NOT followed by a rest
        for d, si_val in day_to_split.items():
            if si_val >= len(split):
                continue
            focus_lower = split[si_val].lower()
            is_heavy = any(kw in focus_lower for kw in high_intensity_keywords)
            next_day = d + 1
            if is_heavy and next_day <= 6 and next_day not in adjusted:
                # Try to swap: remove the furthest rest and insert after this heavy day
                # Only if it doesn't create consecutive rests
                candidates_to_swap = [
                    p for p in adjusted
                    if p != next_day
                    and abs(p - next_day) > 1  # no consecutive rests
                ]
                if candidates_to_swap:
                    # Remove the rest that's farthest from the heavy day
                    to_remove = max(candidates_to_swap, key=lambda p: abs(p - d))
                    adjusted.remove(to_remove)
                    adjusted.append(next_day)
                    adjusted = sorted(adjusted)
                    break  # one adjustment per pass

        return sorted(adjusted[:rest_count])

    def _build_weekly_plan(self, profile: dict, split: List[str], rest_positions: List[int]) -> List[Dict]:
        """Build the full 7-day plan with exercises for workout days and rest for rest days.
        
        Rest days now include a `restReason` field explaining why that day is a rest day,
        as required by REST_DAY_LOGIC_PLAN.md.
        """
        day_names = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        weekly_plan = []
        split_idx = 0

        goal = profile.get('goal', 'Muscle Gain')
        experience = profile.get('experience', 'Beginner')
        equipment = profile.get('equipment', ['Body Weight'])
        body_issues = profile.get('body_issues', [])

        # First pass: map each non-rest day to its split focus so we can generate rest reasons
        day_to_focus: Dict[int, str] = {}
        temp_idx = 0
        for d in range(7):
            if d not in rest_positions and temp_idx < len(split):
                day_to_focus[d] = split[temp_idx]
                temp_idx += 1

        def _get_rest_reason(day_idx: int) -> str:
            """Return a human-readable reason this day is a rest day."""
            prev_day = day_idx - 1
            next_day = day_idx + 1

            # Check if preceding day was high-intensity
            if prev_day >= 0 and prev_day in day_to_focus:
                prev_focus = day_to_focus[prev_day].lower()
                if 'leg' in prev_focus:
                    return 'Recovery after Legs day — your largest muscle group needs 48h'
                if 'heavy' in prev_focus:
                    return 'Recovery after heavy compound session'
                if 'pull' in prev_focus or 'back' in prev_focus:
                    return 'Recovery after Pull day — allowing posterior chain to repair'
                if 'push' in prev_focus or 'chest' in prev_focus:
                    return 'Recovery after Push day — chest and shoulders repairing'
                return f'Recovery after {day_to_focus[prev_day]} session'

            # Check if following day is high-intensity — pre-load rest
            if next_day <= 6 and next_day in day_to_focus:
                next_focus = day_to_focus[next_day].lower()
                if 'leg' in next_focus:
                    return 'Pre-session rest — be fresh for Legs tomorrow'
                if 'heavy' in next_focus or 'full' in next_focus:
                    return 'Pre-session rest — be fresh for a heavy session tomorrow'
                return f'Rest before {day_to_focus[next_day]} session'

            # Generic mid-week / end-week rest
            if day_idx in (5, 6):
                return 'Weekend recovery — consolidate the week\'s gains'
            if day_idx in (2, 3):
                return 'Mid-week recovery — maintain intensity across the week'
            return 'Scheduled recovery day'

        # Cross-day exercise deduplication: no exercise should appear twice in the same week
        global_used_names: Set[str] = set()

        for day_idx in range(7):
            if day_idx in rest_positions or split_idx >= len(split):
                rest_reason = _get_rest_reason(day_idx)
                weekly_plan.append({
                    'day_of_week': day_idx,
                    'day': day_names[day_idx],
                    'focus': 'Rest Day',
                    'exercises': [],
                    'type': 'rest',
                    'intensity': 0,
                    'restReason': rest_reason,
                    'note': 'Recovery and rest - light stretching recommended',
                    'is_placeholder': False,
                    'can_access': True,
                    'is_original_rest': True,
                    'is_original_workout': False,
                    'is_swapped': False,
                    'swapped_from': None,
                    'swapped_to': None,
                    'is_swappable': True,
                    'is_completed': False,
                    'exercises_completed': 0,
                    'exercises_total': 0,
                    'intensity_metrics': self._build_intensity_metrics(0.0),
                })
            else:
                focus = split[split_idx]

                day_seed = self._build_day_seed(profile, focus, day_idx)

                split_idx += 1

                exercises = self._get_exercises_for_day(
                    focus, goal, experience, equipment, body_issues, profile,
                    day_seed=day_seed,
                    global_used_names=global_used_names
                )
                # Track which exercises were used this week to prevent cross-day repeats
                for ex in exercises:
                    global_used_names.add(ex.get('name', ''))

                warmup_exercises = self._get_warmup_for_focus(focus, exercises=exercises, day_seed=day_seed)
                full_session = self._enforce_unique_media_per_day(warmup_exercises + exercises)
                warmup_clean = [ex for ex in full_session if ex.get('is_warmup') is True]
                exercises_clean = [ex for ex in full_session if not ex.get('is_warmup')]

                # Calculate day intensity metrics (returns a dict with intensity_score, category, etc.)
                intensity_metrics = self._calculate_day_intensity(exercises_clean, experience, goal, profile=profile)
                intensity_score = intensity_metrics.get('intensity_score', 0.0) if isinstance(intensity_metrics, dict) else float(intensity_metrics)

                weekly_plan.append({
                    'day_of_week': day_idx,
                    'day': day_names[day_idx],
                    'focus': focus,
                    'warmup': warmup_clean,
                    'exercises': exercises_clean,
                    'type': 'workout',
                    'intensity': round(intensity_score, 2),
                    'note': f'{focus} training',
                    'is_placeholder': False,
                    'can_access': True,
                    'is_original_rest': False,
                    'is_original_workout': True,
                    'is_swapped': False,
                    'swapped_from': None,
                    'swapped_to': None,
                    'is_swappable': True,
                    'is_completed': False,
                    'exercises_completed': 0,
                    'exercises_total': len(exercises_clean),
                    'intensity_metrics': self._build_intensity_metrics(intensity_metrics),
                })

        return weekly_plan

    def swap_rest_with_next_workout(self, weekly_plan: List[Dict], rest_day_index: int,
                                    current_day_index: Optional[int] = None) -> List[Dict]:
        """Swap an original rest day with the next original workout day in the same week."""
        if not isinstance(weekly_plan, list) or len(weekly_plan) != 7:
            return weekly_plan

        if not isinstance(rest_day_index, int) or rest_day_index < 0 or rest_day_index > 6:
            return weekly_plan

        if current_day_index is not None:
            if not isinstance(current_day_index, int) or current_day_index < 0 or current_day_index > 6:
                return weekly_plan
            if rest_day_index < current_day_index:
                return weekly_plan

        rest_day_candidate = weekly_plan[rest_day_index] if isinstance(weekly_plan[rest_day_index], dict) else {}
        if rest_day_candidate.get('type') != 'rest' or rest_day_candidate.get('is_placeholder'):
            return weekly_plan

        if not rest_day_candidate.get('is_original_rest', True):
            return weekly_plan
        if rest_day_candidate.get('is_swapped', False):
            return weekly_plan
        if rest_day_candidate.get('is_swappable', True) is False:
            return weekly_plan

        # Find the next workout day in the same week only (no wrap-around).
        next_workout_idx = None
        for idx in range(rest_day_index + 1, 7):
            day = weekly_plan[idx] if isinstance(weekly_plan[idx], dict) else {}
            if day.get('type') != 'workout':
                continue
            if day.get('is_placeholder'):
                continue
            if not day.get('is_original_workout', True):
                continue
            if day.get('is_swapped', False):
                continue
            if day.get('is_swappable', True) is False:
                continue
            if current_day_index is not None and idx < current_day_index:
                continue
            next_workout_idx = idx
            break

        if next_workout_idx is None:
            return weekly_plan

        plan_copy = [copy.deepcopy(day) if isinstance(day, dict) else {} for day in weekly_plan]
        rest_day = plan_copy[rest_day_index]
        workout_day = plan_copy[next_workout_idx]

        rest_day_name = rest_day.get('day', '')
        rest_day_of_week = rest_day.get('day_of_week', rest_day_index)
        workout_day_name = workout_day.get('day', '')
        workout_day_of_week = workout_day.get('day_of_week', next_workout_idx)
        moved_focus = workout_day.get('focus', 'Workout') or 'Workout'

        moved_workout_day = {
            **workout_day,
            'type': 'workout',
            'day': rest_day_name,
            'day_of_week': rest_day_of_week,
            'is_placeholder': False,
            'can_access': True,
            'is_swapped': True,
            'swapped_from': next_workout_idx,
            'swapped_to': rest_day_of_week,
            'is_original_rest': False,
            'is_original_workout': False,
            'is_swappable': False,
            'is_completed': False,
            'exercises_completed': 0,
            'exercises_total': len(workout_day.get('exercises', []) or []),
            'note': f"{moved_focus} (Moved from {workout_day_name})",
        }

        moved_rest_day = {
            **rest_day,
            'type': 'rest',
            'focus': 'Rest Day',
            'warmup': [],
            'exercises': [],
            'day': workout_day_name,
            'day_of_week': workout_day_of_week,
            'intensity': 0,
            'is_placeholder': False,
            'can_access': True,
            'is_swapped': True,
            'swapped_from': rest_day_index,
            'swapped_to': workout_day_of_week,
            'is_original_rest': False,
            'is_original_workout': False,
            'is_swappable': False,
            'is_completed': False,
            'exercises_completed': 0,
            'exercises_total': 0,
            'note': f"Rest Day (Swapped from {rest_day_name})",
        }

        plan_copy[rest_day_index] = moved_workout_day
        plan_copy[next_workout_idx] = moved_rest_day
        return plan_copy

    def swap_workout_with_future_rest(self, weekly_plan: List[Dict], workout_day_index: int,
                                      target_rest_day_index: int,
                                      current_day_index: Optional[int] = None) -> List[Dict]:
        """Swap an original workout day with a future original rest day."""
        if not isinstance(weekly_plan, list) or len(weekly_plan) != 7:
            return weekly_plan

        if not isinstance(workout_day_index, int) or workout_day_index < 0 or workout_day_index > 6:
            return weekly_plan
        if not isinstance(target_rest_day_index, int) or target_rest_day_index < 0 or target_rest_day_index > 6:
            return weekly_plan
        if workout_day_index == target_rest_day_index:
            return weekly_plan

        if current_day_index is not None:
            if not isinstance(current_day_index, int) or current_day_index < 0 or current_day_index > 6:
                return weekly_plan
            if workout_day_index < current_day_index:
                return weekly_plan
            if target_rest_day_index < current_day_index:
                return weekly_plan

        if target_rest_day_index <= workout_day_index:
            return weekly_plan

        workout_day_candidate = weekly_plan[workout_day_index] if isinstance(weekly_plan[workout_day_index], dict) else {}
        target_rest_day_candidate = weekly_plan[target_rest_day_index] if isinstance(weekly_plan[target_rest_day_index], dict) else {}

        if workout_day_candidate.get('type') != 'workout' or workout_day_candidate.get('is_placeholder'):
            return weekly_plan
        if target_rest_day_candidate.get('type') != 'rest' or target_rest_day_candidate.get('is_placeholder'):
            return weekly_plan

        if not workout_day_candidate.get('is_original_workout', True):
            return weekly_plan
        if workout_day_candidate.get('is_swapped', False):
            return weekly_plan
        if workout_day_candidate.get('is_swappable', True) is False:
            return weekly_plan

        if not target_rest_day_candidate.get('is_original_rest', True):
            return weekly_plan
        if target_rest_day_candidate.get('is_swapped', False):
            return weekly_plan
        if target_rest_day_candidate.get('is_swappable', True) is False:
            return weekly_plan

        if workout_day_candidate.get('is_completed') or int(workout_day_candidate.get('exercises_completed', 0) or 0) > 0:
            return weekly_plan

        remaining_rest_days = sum(
            1 for day in weekly_plan
            if isinstance(day, dict) and day.get('type') == 'rest' and not day.get('is_placeholder')
        )
        if remaining_rest_days <= 0:
            return weekly_plan

        plan_copy = [copy.deepcopy(day) if isinstance(day, dict) else {} for day in weekly_plan]
        workout_day = plan_copy[workout_day_index]
        target_rest_day = plan_copy[target_rest_day_index]

        workout_day_name = workout_day.get('day', '')
        workout_day_of_week = workout_day.get('day_of_week', workout_day_index)
        target_rest_name = target_rest_day.get('day', '')
        target_rest_of_week = target_rest_day.get('day_of_week', target_rest_day_index)
        moved_focus = workout_day.get('focus', 'Workout') or 'Workout'

        plan_copy[workout_day_index] = {
            **target_rest_day,
            'type': 'rest',
            'focus': 'Rest Day',
            'warmup': [],
            'exercises': [],
            'day': workout_day_name,
            'day_of_week': workout_day_of_week,
            'intensity': 0,
            'is_placeholder': False,
            'can_access': True,
            'is_swapped': True,
            'swapped_from': target_rest_day_index,
            'swapped_to': workout_day_of_week,
            'is_original_rest': False,
            'is_original_workout': False,
            'is_swappable': False,
            'is_completed': False,
            'exercises_completed': 0,
            'exercises_total': 0,
            'note': f"Rest Day (Swapped from {target_rest_name})",
        }

        plan_copy[target_rest_day_index] = {
            **workout_day,
            'type': 'workout',
            'day': target_rest_name,
            'day_of_week': target_rest_of_week,
            'is_placeholder': False,
            'can_access': True,
            'is_swapped': True,
            'swapped_from': workout_day_index,
            'swapped_to': target_rest_of_week,
            'is_original_rest': False,
            'is_original_workout': False,
            'is_swappable': False,
            'is_completed': False,
            'exercises_completed': 0,
            'exercises_total': len(workout_day.get('exercises', []) or []),
            'note': f"{moved_focus} (Moved from {workout_day_name})",
        }

        return plan_copy

    def _get_warmup_for_focus(self, focus: str, exercises: List[Dict] = None, day_seed: int = 0) -> List[Dict]:
        """Return a muscle-targeted warm-up block (max 6 drills) dynamically and randomly."""
        focus_lower = str(focus or '').lower()

        focus_to_muscles = {
            'chest & back': ['chest', 'back'],
            'chest & triceps': ['chest', 'triceps'],
            'back & biceps': ['back', 'biceps'],
            'legs & shoulders': ['legs', 'shoulders'],
            'arms & core': ['biceps', 'triceps', 'core'],
            'pull & legs': ['back', 'biceps', 'legs'],
            'push & pull': ['chest', 'back', 'shoulders'],
            'shoulders & traps': ['shoulders', 'traps'],
            'legs (quads)': ['legs', 'calves'],
            'legs (posterior)': ['legs', 'calves'],
            'arms (bi/tri)': ['biceps', 'triceps'],
            'upper body': ['chest', 'back', 'shoulders'],
            'lower body': ['legs', 'core'],
            'full body': ['chest', 'back', 'legs'],
            'full body (upper focus)': ['chest', 'back'],
            'full body (lower focus)': ['legs', 'core'],
            'full body (push-pull)': ['chest', 'back'],
            'full body (push focus)': ['chest', 'shoulders'],
            'full body (pull focus)': ['back', 'biceps'],
            'full body (legs focus)': ['legs', 'calves'],
        }

        target_muscles = []
        if exercises:
            for ex in exercises:
                m_group = str(ex.get('muscle_group') or ex.get('Target_Muscle') or '').strip().lower()
                if m_group:
                    if 'chest' in m_group:
                        target_muscles.append('chest')
                    elif 'back' in m_group:
                        target_muscles.append('back')
                    elif 'shoulder' in m_group:
                        target_muscles.append('shoulders')
                    elif 'leg' in m_group or 'quad' in m_group or 'glute' in m_group or 'hamstring' in m_group:
                        target_muscles.append('legs')
                    elif 'bicep' in m_group:
                        target_muscles.append('biceps')
                    elif 'tricep' in m_group:
                        target_muscles.append('triceps')
                    elif 'core' in m_group or 'abs' in m_group or 'abdominal' in m_group:
                        target_muscles.append('core')
                    elif 'calf' in m_group or 'calves' in m_group:
                        target_muscles.append('calves')
                    elif 'trap' in m_group:
                        target_muscles.append('traps')

        # Fallback to focus_to_muscles mapping if target_muscles is empty
        if not target_muscles:
            target_muscles = list(focus_to_muscles.get(focus_lower, []))

        # Fallback parsing for custom focus names.
        if not target_muscles:
            if 'chest' in focus_lower or 'push' in focus_lower:
                target_muscles.extend(['chest', 'shoulders', 'triceps'])
            if 'back' in focus_lower or 'pull' in focus_lower:
                target_muscles.extend(['back', 'biceps'])
            if 'leg' in focus_lower or 'lower' in focus_lower:
                target_muscles.extend(['legs'])
            if 'shoulder' in focus_lower:
                target_muscles.extend(['shoulders'])
            if 'arm' in focus_lower or 'biceps' in focus_lower or 'triceps' in focus_lower:
                target_muscles.extend(['biceps', 'triceps'])
            if 'trap' in focus_lower:
                target_muscles.extend(['traps'])
            if 'core' in focus_lower:
                target_muscles.extend(['core'])

        if not target_muscles:
            target_muscles = ['general']

        # Preserve order while removing duplicates.
        target_muscles = list(dict.fromkeys(target_muscles))

        warmup_drills = {
            'chest': [
                {'name': 'Arm Circles (Forward)', 'reps': '30 seconds', 'muscle_group': 'Chest'},
                {'name': 'Arm Circles (Backward)', 'reps': '30 seconds', 'muscle_group': 'Chest'},
                {'name': 'Band Pull-Aparts', 'reps': '15 reps', 'muscle_group': 'Chest'},
                {'name': 'Push-Up Plus', 'reps': '10 reps', 'muscle_group': 'Chest'},
            ],
            'back': [
                {'name': 'Cat-Cow Stretch', 'reps': '10 reps', 'muscle_group': 'Back'},
                {'name': 'Band Face Pulls', 'reps': '15 reps', 'muscle_group': 'Back'},
                {'name': 'Scapular Wall Slides', 'reps': '12 reps', 'muscle_group': 'Back'},
                {'name': 'Dead Bug', 'reps': '8 each side', 'muscle_group': 'Core/Back'},
            ],
            'shoulders': [
                {'name': 'Arm Circles', 'reps': '30 seconds each direction', 'muscle_group': 'Shoulders'},
                {'name': 'Band Pull-Aparts', 'reps': '15 reps', 'muscle_group': 'Shoulders'},
                {'name': 'Shoulder Dislocations (Band)', 'reps': '10 reps', 'muscle_group': 'Shoulders'},
                {'name': 'Light Lateral Raises', 'reps': '12 reps', 'muscle_group': 'Shoulders'},
            ],
            'legs': [
                {'name': 'Leg Swings (Front/Back)', 'reps': '15 each leg', 'muscle_group': 'Legs'},
                {'name': 'Leg Swings (Side/Side)', 'reps': '15 each leg', 'muscle_group': 'Legs'},
                {'name': 'Bodyweight Squats', 'reps': '15 reps', 'muscle_group': 'Legs'},
                {'name': 'Walking Lunges', 'reps': '8 each leg', 'muscle_group': 'Legs'},
                {'name': 'Calf Raises', 'reps': '20 reps', 'muscle_group': 'Calves'},
            ],
            'biceps': [
                {'name': 'Wrist Circles', 'reps': '20 each direction', 'muscle_group': 'Arms'},
                {'name': 'Light Band Curls', 'reps': '15 reps', 'muscle_group': 'Arms'},
                {'name': 'Arm Swings', 'reps': '20 reps', 'muscle_group': 'Arms'},
            ],
            'triceps': [
                {'name': 'Overhead Tricep Stretch', 'reps': '30 seconds each', 'muscle_group': 'Arms'},
                {'name': 'Diamond Push-Ups (Light)', 'reps': '10 reps', 'muscle_group': 'Arms'},
                {'name': 'Band Tricep Pushdowns', 'reps': '15 reps', 'muscle_group': 'Arms'},
            ],
            'core': [
                {'name': 'Dead Bug', 'reps': '10 reps each side', 'muscle_group': 'Core'},
                {'name': 'Bird Dog', 'reps': '10 reps each side', 'muscle_group': 'Core'},
                {'name': 'McGill Curl-Up', 'reps': '5 reps each side', 'muscle_group': 'Core'},
                {'name': 'Side Plank', 'reps': '20 seconds each side', 'muscle_group': 'Core'},
            ],
            'calves': [
                {'name': 'Ankle Circles', 'reps': '12 each direction', 'muscle_group': 'Calves'},
                {'name': 'Bodyweight Calf Raises', 'reps': '20 reps', 'muscle_group': 'Calves'},
                {'name': 'Tibialis Raises', 'reps': '15 reps', 'muscle_group': 'Calves'},
            ],
            'traps': [
                {'name': 'Neck Mobility Rolls', 'reps': '8 each direction', 'muscle_group': 'Traps'},
                {'name': 'Scapular Shrugs', 'reps': '15 reps', 'muscle_group': 'Traps'},
                {'name': 'Band Face Pulls', 'reps': '15 reps', 'muscle_group': 'Traps'},
            ],
            'general': [
                {'name': 'Brisk Walk / Light Cardio', 'reps': '3 min', 'muscle_group': 'Full Body'},
                {'name': 'Dynamic Joint Circles', 'reps': '10 reps/side', 'muscle_group': 'Mobility'},
                {'name': 'High Knees', 'reps': '30 seconds', 'muscle_group': 'Full Body'},
                {'name': 'Torso Twists', 'reps': '20 reps', 'muscle_group': 'Full Body'},
            ],
        }

        import random
        rng = random.Random(day_seed)

        selected_drills = []
        seen_names = set()
        
        # 1. Pick drills from target muscle groups
        for muscle in target_muscles:
            drills = list(warmup_drills.get(muscle, warmup_drills['general']))
            rng.shuffle(drills)
            muscle_picked = 0
            for drill in drills:
                drill_name = str(drill.get('name', '')).strip()
                if not drill_name or drill_name in seen_names:
                    continue
                seen_names.add(drill_name)
                selected_drills.append({
                    **drill,
                    'sets': 1,
                    'rest': '20 seconds',
                    'is_warmup': True,
                })
                muscle_picked += 1
                if muscle_picked >= 2 or len(selected_drills) >= 5:
                    break
            if len(selected_drills) >= 5:
                break

        # 2. If we need more drills to reach a minimum of 4, fill from 'general' category
        if len(selected_drills) < 4:
            general_drills = list(warmup_drills['general'])
            rng.shuffle(general_drills)
            for drill in general_drills:
                drill_name = str(drill.get('name', '')).strip()
                if not drill_name or drill_name in seen_names:
                    continue
                seen_names.add(drill_name)
                selected_drills.append({
                    **drill,
                    'sets': 1,
                    'rest': '20 seconds',
                    'is_warmup': True,
                })
                if len(selected_drills) >= 4:
                    break

        warmups = []
        for drill in selected_drills:
            warmup_name = str(drill.get('name', '')).strip()
            warmup_muscle = str(drill.get('muscle_group', '')).strip()
            warmup_media = self._resolve_exercise_media({
                'Name': warmup_name,
                'Target_Muscle': warmup_muscle,
            })

            fallback_gif = self._get_gif_fallback_for_target(
                warmup_muscle,
                exercise_name=warmup_name,
            )

            media_url = (
                warmup_media.get('gif')
                or warmup_media.get('image')
                or warmup_media.get('video_url')
                or fallback_gif
            )
            self._set_exercise_media_url(drill, media_url)
            drill['notes'] = f'Warm-up for {focus}'

            classification = self._classify_exercise_mode(
                warmup_name,
                drill.get('equipment', ''),
                drill.get('reps', ''),
                explicit_trackable=False,
            )
            drill.update(classification)
            drill['needs_camera'] = False
            drill['exercise_mode'] = 'warmup'
            warmups.append(drill)

        return warmups

    def _get_exercises_for_day(self, focus: str, goal: str, experience: str,
                                equipment: List[str], body_issues: List[str],
                                profile: dict, day_seed: int = 0,
                                global_used_names: Set[str] = None) -> List[Dict]:
        """
        Select exercises deterministically for a given focus day.

        day_seed: unique per-day offset so different days (even with the same
                  focus category) get different exercises from the pool.
        """
        # --- Muscle group mapping ---
        muscle_map = {
            'Full Body': ['Chest', 'Back', 'Legs', 'Shoulders', 'Arms', 'Core'],
            'Upper Body': ['Chest', 'Back', 'Shoulders', 'Arms'],
            'Upper Body (Volume)': ['Chest', 'Back', 'Shoulders', 'Arms'],
            'Lower Body': ['Legs', 'Core'],
            'Lower Body (Volume)': ['Legs', 'Core'],
            'Push': ['Chest', 'Shoulders', 'Arms'],
            'Push (Heavy)': ['Chest', 'Shoulders'],
            'Push (Volume)': ['Chest', 'Shoulders', 'Arms'],
            'Pull': ['Back', 'Arms'],
            'Pull (Heavy)': ['Back'],
            'Pull (Volume)': ['Back', 'Arms'],
            'Legs': ['Legs'],
            'Legs (Heavy)': ['Legs'],
            'Legs (Volume)': ['Legs', 'Core'],
            'Legs (Accessory)': ['Legs', 'Core'],
            'Chest': ['Chest'],
            'Back': ['Back'],
            'Shoulders': ['Shoulders'],
            'Arms': ['Arms'],
            'Core': ['Core'],
            'Chest & Back': ['Chest', 'Back'],
            'Legs & Shoulders': ['Legs', 'Shoulders'],
            'Legs & Arms': ['Legs', 'Arms'],
            'Pull & Legs': ['Back', 'Arms', 'Legs'],
            'Push & Pull': ['Chest', 'Back', 'Shoulders', 'Arms'],
            'Back & Arms': ['Back', 'Arms'],
            'Chest & Shoulders': ['Chest', 'Shoulders'],
            'Arms (Bi/Tri)': ['Arms'],
            'Chest & Triceps': ['Chest', 'Arms'],
            'Back & Biceps': ['Back', 'Arms'],
            'Arms & Core': ['Arms', 'Core'],
            'Shoulders & Traps': ['Shoulders', 'Traps'],
            'Legs (Quads)': ['Legs', 'Calves'],
            'Legs (Posterior)': ['Legs', 'Calves'],
            'Full Body (Upper Focus)': ['Chest', 'Back', 'Shoulders'],
            'Full Body (Lower Focus)': ['Legs', 'Core'],
            'Full Body (Push-Pull)': ['Chest', 'Back'],
            'Full Body (Push Focus)': ['Chest', 'Shoulders'],
            'Full Body (Pull Focus)': ['Back', 'Arms'],
            'Full Body (Legs Focus)': ['Legs', 'Calves'],
        }        
        # Bug #1a Fix: Map beginner sub-focus variants to standard muscle groups
        # so the existing muscle_map lookup still works correctly.
        beginner_focus_to_standard = {
            'Full Body (Upper Focus)': 'Upper Body',
            'Full Body (Lower Focus)': 'Lower Body',
            'Full Body (Push-Pull)': 'Chest & Back',
            'Full Body (Push Focus)': 'Push',
            'Full Body (Pull Focus)': 'Pull',
            'Full Body (Legs Focus)': 'Legs',
            'Full Body (Core & Conditioning)': 'Full Body',
            'Full Body (Conditioning)': 'Full Body',
        }
        effective_focus = beginner_focus_to_standard.get(focus, focus)
        target_muscles = muscle_map.get(effective_focus, muscle_map.get(focus, ['Chest', 'Back', 'Legs']))

        # Focus-specific distribution: keep two primary muscles loaded and
        # use additional mapped muscles as accessories where applicable.
        focus_distribution = {
            'Chest & Back': {'primary': ['Chest', 'Back']},
            'Legs & Shoulders': {'primary': ['Legs', 'Shoulders']},
            'Arms & Core': {'primary': ['Arms', 'Core']},
            'Pull & Legs': {'primary': ['Back', 'Legs'], 'accessory': ['Arms']},
            'Push & Pull': {'primary': ['Chest', 'Back'], 'accessory': ['Shoulders']},
            'Shoulders & Traps': {'primary': ['Shoulders', 'Traps']},
            'Chest & Triceps': {'primary': ['Chest', 'Arms']},
            'Back & Biceps': {'primary': ['Back', 'Arms']},
            'Legs (Quads)': {'primary': ['Legs', 'Calves']},
            'Legs (Posterior)': {'primary': ['Legs', 'Calves']},
            'Full Body (Upper Focus)': {'primary': ['Chest', 'Back'], 'accessory': ['Shoulders']},
            'Full Body (Lower Focus)': {'primary': ['Legs', 'Core']},
            'Full Body (Push-Pull)': {'primary': ['Chest', 'Back']},
            'Full Body (Push Focus)': {'primary': ['Chest', 'Shoulders']},
            'Full Body (Pull Focus)': {'primary': ['Back', 'Arms']},
            'Full Body (Legs Focus)': {'primary': ['Legs', 'Calves']},
        }

        distribution = focus_distribution.get(effective_focus, focus_distribution.get(focus, {}))
        primary_muscles = [m for m in distribution.get('primary', []) if m in target_muscles]
        if not primary_muscles:
            primary_muscles = list(target_muscles)

        accessory_muscles = [m for m in distribution.get('accessory', []) if m in target_muscles and m not in primary_muscles]
        for muscle in target_muscles:
            if muscle not in primary_muscles and muscle not in accessory_muscles:
                accessory_muscles.append(muscle)

        # Compound exercise indicators (multi-joint movements)
        compound_keywords = [
            'press', 'squat', 'deadlift', 'row', 'pull-up', 'pullup',
            'push-up', 'pushup', 'lunge', 'clean', 'snatch', 'dip',
            'bench', 'overhead', 'thrust', 'chin-up', 'chinup'
        ]

        # --- Exercise count by experience ---
        count_ranges = {
            'Beginner': (5, 7),
            'Intermediate': (6, 8),
            'Advanced': (7, 10),
        }
        min_count, max_count = count_ranges.get(experience, (5, 7))

        # For Full Body days, use the higher end; for isolation days, use the lower end
        if len(target_muscles) >= 4:
            target_count = max_count
        elif len(target_muscles) >= 2:
            target_count = (min_count + max_count) // 2
        else:
            target_count = min_count
        
        # Bug #1 Fix: Gender-based volume adjustment
        # Research: Women have lower absolute strength but similar relative strength
        # and better recovery capacity. Reduce volume by 1-2 exercises for safety.
        gender = profile.get('gender', 'Male')
        if gender and gender.lower() in ('female', 'f', 'woman', 'women'):
            # Reduce exercise count by 1 for female users (lower absolute volume)
            target_count = max(4, target_count - 1)
        elif gender and gender.lower() not in ('male', 'm', 'man'):
            # Minimal adjustment for "Other" gender
            target_count = max(4, target_count - 0)  # No change, keep standard

        if goal in ('Muscle Gain', 'Strength', 'Fat Loss', 'Weight Loss', 'Endurance'):
            target_count = min(max_count, target_count + 1)

        # Experience-based volume targets per muscle group.
        volume_targets = {
            'Beginner': {'primary': (2, 3), 'accessory': (1, 1)},
            'Intermediate': {'primary': (3, 4), 'accessory': (1, 2)},
            'Advanced': {'primary': (4, 5), 'accessory': (1, 2)},
        }
        profile_targets = volume_targets.get(experience, volume_targets['Beginner'])
        p_min, p_max = profile_targets['primary']
        a_min, a_max = profile_targets['accessory']

        desired_minimum = len(primary_muscles) * p_min + len(accessory_muscles) * a_min
        target_count = max(min_count, min(max_count, max(target_count, min(desired_minimum, max_count))))

        # Build per-muscle quotas with priority for primary muscles.
        muscle_targets = {muscle: 0 for muscle in target_muscles}

        def _assign_round_robin(targets: Dict[str, int], muscles: List[str], cap: int,
                                total_limit: int, current_total: int) -> int:
            if not muscles:
                return current_total
            changed = True
            while current_total < total_limit and changed:
                changed = False
                for m in muscles:
                    if current_total >= total_limit:
                        break
                    if targets[m] < cap:
                        targets[m] += 1
                        current_total += 1
                        changed = True
            return current_total

        allocated = 0
        allocated = _assign_round_robin(muscle_targets, primary_muscles, p_min, target_count, allocated)
        allocated = _assign_round_robin(muscle_targets, accessory_muscles, a_min, target_count, allocated)
        allocated = _assign_round_robin(muscle_targets, primary_muscles, p_max, target_count, allocated)
        allocated = _assign_round_robin(muscle_targets, accessory_muscles, a_max, target_count, allocated)
        allocated = _assign_round_robin(muscle_targets, target_muscles, target_count, target_count, allocated)

        allocation_order = list(primary_muscles) + [m for m in target_muscles if m not in primary_muscles]

        # --- Get exercise parameters based on goal + experience ---
        params = self._get_exercise_params(goal, experience, profile)

        # --- Filter exercise pool ---
        pool = self.exercises_df.copy()

        # Bodyweight-always terms (always allowed regardless of equipment selection)
        BODYWEIGHT_TERMS = ['body weight', 'bodyweight', 'assisted']

        # Equipment filter
        # IMPORTANT: empty equipment list = bodyweight ONLY (not "show everything")
        effective_equipment = [str(e).lower().strip() for e in (equipment or [])]
        # Strip sentinel values the frontend may send
        effective_equipment = [e for e in effective_equipment if e not in ('none', 'no equipment', '')]

        if not effective_equipment:
            # User has no equipment — restrict to bodyweight exercises only
            pool = pool[pool['Equipment'].str.lower().str.strip().isin(BODYWEIGHT_TERMS)]
        else:
            equip_lower = list(effective_equipment)
            # Expand equipment synonyms: bridge ALL frontend UI labels → dataset Equipment column values.
            # Dataset values: 'Assisted','Band','Barbell','Body Weight','Bosu Ball','Cable',
            # 'Dumbbell','Elliptical Machine','Ez Barbell','Hammer','Kettlebell',
            # 'Leverage Machine','Medicine Ball','Olympic Barbell','Resistance Band','Roller',
            # 'Rope','Skierg Machine','Sled Machine','Smith Machine','Stability Ball',
            # 'Stationary Bike','Stepmill Machine','Tire','Trap Bar',
            # 'Upper Body Ergometer','Weighted','Wheel Roller'
            SYNONYM_MAP = {
                # Dumbbells
                'dumbbells': ['dumbbell'],
                'dumbbell': ['dumbbell'],
                # Barbells
                'barbell': ['barbell'],
                'olympic barbell': ['olympic barbell', 'barbell'],
                'ez curl bar': ['ez barbell'],
                'trap bar': ['trap bar'],
                # Kettlebell
                'kettlebell': ['kettlebell'],
                'kettlebells': ['kettlebell'],
                # Cable
                'cable machine': ['cable', 'rope'],
                'cable': ['cable', 'rope'],
                # Machines
                'weight machine': ['leverage machine'],
                'smith machine': ['smith machine'],
                'assisted machine': ['assisted'],
                # Resistance/bands
                'resistance bands': ['resistance band', 'band'],
                'resistance band': ['resistance band', 'band'],
                'resistance bands (light)': ['band', 'resistance band'],
                # Cardio/specialty machines
                'elliptical': ['elliptical machine'],
                'stationary bike': ['stationary bike'],
                'skierg machine': ['skierg machine'],
                'sled': ['sled machine'],
                'stepmill': ['stepmill machine'],
                'upper body ergometer': ['upper body ergometer'],
                # Free accessories
                'medicine ball': ['medicine ball'],
                'stability / yoga ball': ['stability ball'],   # bosu ball is a separate option
                'bosu ball': ['bosu ball'],
                'foam roller': ['roller'],
                'jump rope': ['rope'],                         # home-safe subset of Rope
                'battle rope / jump rope': ['rope'],           # legacy label kept for compat
                'weighted vest': ['weighted'],
                'ab wheel': ['wheel roller'],
                'hammer / sledgehammer': ['hammer'],
                'tire': ['tire'],
                # Catch-all labels (legacy / user typed values)
                'pull-up bar': ['body weight'],   # plan §5.2 Rule 4: maps to Body Weight, NOT Weighted
                'pull up bar': ['body weight'],   # plan §5.2 Rule 4
                'yoga mat': ['roller', 'stability ball'],
                'gym': ['dumbbell', 'barbell', 'cable', 'leverage machine', 'smith machine',
                        'kettlebell', 'ez barbell', 'olympic barbell', 'trap bar', 'weighted',
                        'band', 'resistance band', 'rope', 'medicine ball'],
                'full gym': ['dumbbell', 'barbell', 'cable', 'leverage machine', 'smith machine',
                             'kettlebell', 'ez barbell', 'olympic barbell', 'trap bar', 'weighted',
                             'band', 'resistance band', 'rope', 'medicine ball'],
            }
            synonyms_to_add = []
            for label in equip_lower:
                mapped = SYNONYM_MAP.get(label, [label])  # fallback: use label as-is
                synonyms_to_add.extend(mapped)
            equip_lower = list(set(equip_lower + synonyms_to_add + BODYWEIGHT_TERMS))

            pool = pool[pool['Equipment'].str.lower().str.strip().isin(equip_lower)]

        # Injury filter
        if body_issues:
            for issue in body_issues:
                if 'Avoid_If' in pool.columns:
                    pool = pool[~pool['Avoid_If'].str.contains(issue, case=False, na=False)]
                if 'shoulder' in issue.lower():
                    # Rule-based safety logic: filter out exercises with shoulder forbidden terms
                    forbidden_words = ["pull-up", "pullup", "overhead press", "pike push", "handstand", "shoulder press", "military press", "neck press"]
                    pattern = "|".join(forbidden_words)
                    if 'Name' in pool.columns:
                        pool = pool[~pool['Name'].str.contains(pattern, case=False, na=False)]

        # Biomechanical safety filter
        pool = self._filter_biomechanics(pool, profile)

        if pool.empty:
            print(f"    WARNING: No exercises after filtering for {focus}, using fallback")
            return self._get_fallback_exercises(params)

        # --- Select exercises per target muscle, compound first ---
        selected = []
        # Merge local + cross-day used names to prevent any repetition
        used_names: Set[str] = set(global_used_names) if global_used_names else set()

        for muscle in allocation_order:
            target_for_muscle = int(muscle_targets.get(muscle, 1) or 0)
            if target_for_muscle <= 0:
                continue

            # Get candidates for this muscle
            candidates = pool[pool['Target_Muscle'].str.contains(muscle, case=False, na=False)].copy()

            if candidates.empty:
                continue

            # Mark compound vs isolation
            candidates['_is_compound'] = candidates['Name'].str.lower().apply(
                lambda name: any(kw in name for kw in compound_keywords)
            )

            # --- SEEDED SHUFFLE: true variety per day, stable per (user, day, week) ---
            # Shuffle within each priority tier so we don't always get A-Z first.
            # Uses day_seed which is a large hash unique to (user_id, focus, day_index, week).
            seed_compound = int(day_seed % (2**31))
            seed_isolation = int((day_seed + 0xDEADBEEF) % (2**31))

            compound_df = candidates[candidates['_is_compound']].sample(
                frac=1, random_state=seed_compound
            ).reset_index(drop=True)
            isolation_df = candidates[~candidates['_is_compound']].sample(
                frac=1, random_state=seed_isolation
            ).reset_index(drop=True)
            # Keep compounds first (better programming order), then isolation
            candidates = pd.concat([compound_df, isolation_df], ignore_index=True)

            # Pick exercises for this muscle (avoid duplicates across days too)
            selected_for_muscle = 0

            for _, row in candidates.iterrows():
                name = row.get('Name', 'Exercise')
                if name in used_names:
                    continue

                used_names.add(name)
                target = row.get('Target_Muscle', muscle)
                media = self._resolve_exercise_media(row)
                classification = self._classify_exercise_mode(
                    name,
                    row.get('Equipment', ''),
                    params['reps'],
                )

                selected.append({
                    'name': name,
                    'sets': params['sets'],
                    'reps': params['reps'],
                    'rest': params['rest'],
                    'muscle_group': target,
                    'notes': f'Target: {target}',
                    'equipment': str(row.get('Equipment', '')).strip(),  # ✅ pass equipment for UI + test verification
                    'gif': media['gif'],
                    'video_url': media['video_url'],
                    'image': media['image'],
                    'media_type': media['media_type'],
                    'trackable': classification['trackable'],
                    'duration_seconds': classification['duration_seconds'],
                    'is_timed': classification['is_timed'],
                    'needs_camera': classification['needs_camera'],
                    'exercise_mode': classification['exercise_mode'],
                    'movement_pattern': classification.get('movement_pattern', ''),
                    '_is_compound': row.get('_is_compound', False),
                })

                selected_for_muscle += 1
                if selected_for_muscle >= target_for_muscle:
                    break

            if len(selected) >= target_count:
                break

        # If we don't have enough, fill from remaining pool (also shuffled)
        if len(selected) < min_count:
            seed_fill = int((day_seed + 0xCAFEBABE) % (2**31))
            remaining = pool[~pool['Name'].isin(used_names)].sample(
                frac=1, random_state=seed_fill
            )
            for _, row in remaining.iterrows():
                if len(selected) >= target_count:
                    break
                name = row.get('Name', 'Exercise')
                if name not in used_names:
                    used_names.add(name)
                    media = self._resolve_exercise_media(row)
                    classification = self._classify_exercise_mode(
                        name,
                        row.get('Equipment', ''),
                        params['reps'],
                    )
                    selected.append({
                        'name': name,
                        'sets': params['sets'],
                        'reps': params['reps'],
                        'rest': params['rest'],
                        'muscle_group': row.get('Target_Muscle', 'General'),
                        'notes': f'Target: {row.get("Target_Muscle", "General")}',
                        'equipment': str(row.get('Equipment', '')).strip(),  # ✅ pass equipment for UI + test verification
                        'gif': media['gif'],
                        'video_url': media['video_url'],
                        'image': media['image'],
                        'media_type': media['media_type'],
                        'trackable': classification['trackable'],
                        'duration_seconds': classification['duration_seconds'],
                        'is_timed': classification['is_timed'],
                        'needs_camera': classification['needs_camera'],
                        'exercise_mode': classification['exercise_mode'],
                        'movement_pattern': classification.get('movement_pattern', ''),
                        '_is_compound': False,
                    })

        # Cap at target_count
        selected = selected[:target_count]

        # Keep compounds first but preserve seeded shuffled order within each tier.
        selected.sort(key=lambda x: (not x.get('_is_compound', False),))

        # Apply age-based safety caps
        age = profile.get('age', 25)
        if age:
            for ex in selected:
                # Safely parse rest time
                rest_str = str(ex.get('rest', '60'))
                rest_val = 60
                try:
                    import re as _re
                    _nums = _re.findall(r'\d+', rest_str)
                    if _nums:
                        rest_val = int(_nums[0])
                except Exception:
                    rest_val = 60
                ex['sets'], ex['reps'], _, _ = self._apply_age_based_caps(
                    profile, ex['sets'], ex['reps'],
                    rest_val,
                    0.8
                )

        # Clean internal fields
        for ex in selected:
            ex.pop('_is_compound', None)

        selected = self._enforce_unique_media_per_day(selected)

        # Fallback if still empty
        if not selected:
            return self._get_fallback_exercises(params)

        print(f"    {focus}: {len(selected)} exercises selected (target: {target_count})")
        return selected

    def _get_exercise_params(self, goal: str, experience: str, profile: dict) -> Dict:
        """
        Return deterministic sets/reps/rest based on goal and experience.
        When ProgressionEngine is available AND the user has history,
        use computed progression; otherwise fall back to static tables.
        """
        # Check Gemini extracted config first
        if '_gemini_config' in profile:
            return profile['_gemini_config']
        # Try progression engine first
        if self.progression_engine is not None and profile.get('streak', 0) > 0:
            try:
                # Static baseline
                goal_params = {
                    'Weight Loss':  {'reps_low': 12, 'reps_high': 15, 'rest': '30-45 seconds'},
                    'Fat Loss':     {'reps_low': 12, 'reps_high': 15, 'rest': '30-45 seconds'},
                    'Muscle Gain':  {'reps_low': 8,  'reps_high': 12, 'rest': '60-90 seconds'},
                    'Strength':     {'reps_low': 4,  'reps_high': 6,  'rest': '120-180 seconds'},
                    'Endurance':    {'reps_low': 15, 'reps_high': 20, 'rest': '20-30 seconds'},
                    'Maintenance':  {'reps_low': 10, 'reps_high': 12, 'rest': '60 seconds'},
                }
                gp = goal_params.get(goal, goal_params['Muscle Gain'])
                sets_map = {'Beginner': 3, 'Intermediate': 4, 'Advanced': 5}
                base_sets = min(sets_map.get(experience, 3), 5)

                current_params = {
                    'sets': base_sets,
                    'reps_low': gp['reps_low'],
                    'reps_high': gp['reps_high'],
                    'intensity': 0.75,
                    'rest_seconds': 90,
                }

                result = self.progression_engine.compute_progression(
                    user_profile=profile,
                    current_params=current_params,
                    workout_stats=profile.get('workout_stats'),
                )

                prog_sets = result['sets']
                prog_reps = result['reps']
                method    = result['progression_method']

                prog_state = profile.get('_progression_state', {})
                if prog_state.get('is_deload', False):
                    prog_sets = max(2, prog_sets - 1)

                print(f"    Progression -> {prog_sets} sets x {prog_reps} ({method})")

                return {
                    'sets': prog_sets,
                    'reps': prog_reps,
                    'rest': gp['rest'],
                }
            except Exception as e:
                print(f"    ProgressionEngine param calc failed: {e}")

        # Fallback: static tables
        goal_params = {
            'Weight Loss':  {'reps': '12-15', 'rest': '30-45 seconds'},
            'Fat Loss':     {'reps': '12-15', 'rest': '30-45 seconds'},
            'Muscle Gain':  {'reps': '8-12',  'rest': '60-90 seconds'},
            'Strength':     {'reps': '4-6',   'rest': '120-180 seconds'},
            'Endurance':    {'reps': '15-20', 'rest': '20-30 seconds'},
            'Maintenance':  {'reps': '10-12', 'rest': '60 seconds'},
        }
        gp = goal_params.get(goal, goal_params['Muscle Gain'])

        sets_map = {
            'Beginner': 3,
            'Intermediate': 4,
            'Advanced': 5,
        }
        sets = min(sets_map.get(experience, 3), 5)

        prog_state = profile.get('_progression_state', {})
        if prog_state.get('is_deload', False):
            sets = max(2, sets - 1)

        reps = gp['reps']

        # Bug #1f Fix: Gender-based intensity adjustment
        # Research-based adjustments for physiological differences
        gender = profile.get('gender', 'Male')
        
        # Parse rest time from string (e.g., "60 seconds" → 60)
        try:
            rest_str = gp['rest']
            rest_seconds = int(rest_str.split()[0])  # Extract number from "60 seconds"
        except Exception:
            rest_seconds = 60  # Default fallback
        
        if gender and gender.lower() in ('female', 'f', 'woman', 'women'):
            # Females: Higher rep ranges for hypertrophy, better recovery capacity
            try:
                parts = reps.split('-')
                low  = int(parts[0]) + 2
                high = int(parts[1]) + 2
                reps = f"{low}-{high}"
            except Exception:
                pass  # keep original reps if parsing fails
            
            # Reduce sets by 1 for beginners to prevent overtraining
            if experience == 'Beginner':
                sets = max(2, sets - 1)

            # Shorter rest periods for female users (10-15% reduction)
            # Women recover faster between sets due to hormonal differences
            rest_seconds = max(30, int(rest_seconds * 0.85))  # 15% reduction, minimum 30s

        elif gender and gender.lower() not in ('male', 'm', 'man'):
            # "Other" gender: minimal adjustment (5% changes)
            try:
                parts = reps.split('-')
                low  = int(parts[0]) + 1
                high = int(parts[1]) + 1
                reps = f"{low}-{high}"
            except Exception:
                pass
            rest_seconds = max(30, int(rest_seconds * 0.95))  # 5% reduction
        else:
            # Male users: standard rest times
            pass  # rest_seconds already parsed above

        # Format rest time back to string
        rest_formatted = f"{rest_seconds} seconds"

        return {
            'sets': sets,
            'reps': reps,
            'rest': rest_formatted,
            'gender_adjusted': gender.lower() in ('female', 'f', 'woman', 'women') if gender else False,
            'gender': gender,
        }

    def _calculate_day_intensity(self, exercises: List[Dict], experience: str, goal: str, profile: dict = None) -> Dict:
        """
        Calculate comprehensive intensity metrics for meal plan correlation.
        
        Returns Dict with:
            - intensity_score: 0.0-1.0 overall day intensity
            - volume_load: Sets × Reps (proxy for training volume)
            - category: 'rest', 'light', 'moderate', 'hard', 'very_hard'
            - calorie_multiplier: 0.85-1.25 TDEE adjustment factor
        """
        if not exercises:
            return {
                'intensity_score': 0.0,
                'volume_load': 0,
                'category': 'rest',
                'calorie_multiplier': 0.90
            }

        # Exercise intensity coefficients (METs-based)
        EXERCISE_INTENSITY = {
            # Compound movements - high intensity
            'squat': 1.0, 'deadlift': 1.0, 'bench press': 0.95,
            'overhead press': 0.90, 'pull-up': 0.85, 'row': 0.80,
            'lunge': 0.75, 'dip': 0.80, 'clean': 1.0,
            
            # Isolation movements - moderate intensity
            'bicep curl': 0.50, 'tricep extension': 0.50, 'lateral raise': 0.45,
            'leg extension': 0.55, 'leg curl': 0.55, 'calf raise': 0.40,
            'curl': 0.50, 'extension': 0.50, 'raise': 0.45,
            
            # Bodyweight exercises
            'push-up': 0.70, 'pushup': 0.70, 'sit-up': 0.60,
            'plank': 0.55, 'crunch': 0.50,
        }

        total_intensity = 0
        total_volume = 0

        for ex in exercises:
            # Base exercise intensity
            ex_name = ex.get('name', '').lower()
            base_intensity = 0.6  # Default moderate intensity
            
            # Match exercise name to intensity coefficient
            for keyword, intensity in EXERCISE_INTENSITY.items():
                if keyword in ex_name:
                    base_intensity = intensity
                    break

            # Volume factor (sets × reps)
            # ── FIX: coerce sets/reps to safe types before arithmetic ──
            # The ML pipeline can return sets/reps as int, float, str, or dict.
            # Calling `'-' in int_value` raises TypeError; `dict * int` raises TypeError.
            raw_sets = ex.get('sets', 3)
            raw_reps = ex.get('reps', '10')

            # Safely convert sets to int
            try:
                if isinstance(raw_sets, dict):
                    sets = int(raw_sets.get('value', 3))
                elif isinstance(raw_sets, (int, float)):
                    sets = max(1, int(raw_sets))
                else:
                    digits = ''.join(filter(str.isdigit, str(raw_sets)))
                    sets = int(digits) if digits else 3
            except Exception:
                sets = 3

            # Safely convert reps to a numeric value
            try:
                reps_str = str(raw_reps) if not isinstance(raw_reps, str) else raw_reps
                if '-' in reps_str:
                    parts = reps_str.split('-')
                    reps = sum(int(''.join(filter(str.isdigit, p)) or '10') for p in parts) / max(len(parts), 1)
                else:
                    digits = ''.join(filter(str.isdigit, reps_str))
                    reps = int(digits) if digits else 10
            except Exception:
                reps = 10

            volume_factor = (sets * reps) / 30  # Normalize to ~1.0
            total_volume += sets * reps

            # Calculate exercise intensity contribution
            ex_intensity = base_intensity * volume_factor
            total_intensity += ex_intensity

        # Normalize intensity score (0-1 scale)
        # Typical workout has 5-8 exercises
        intensity_score = min(total_intensity / 5, 1.0)

        # Apply Phase 3 readiness autoregulation and deload scaling
        if profile:
            prog_state = profile.get('_progression_state', {})
            readiness_score = prog_state.get('readiness_score', 70)
            is_deload = prog_state.get('is_deload', False)
            
            # Autoregulation: Optimal readiness (+5%), Fatigued (-10%)
            if readiness_score >= 85:
                intensity_score = min(1.0, intensity_score + 0.05)
            elif readiness_score < 50:
                intensity_score = max(0.1, intensity_score - 0.10)
                
            # Deload: -20% intensity
            if is_deload:
                intensity_score = max(0.1, intensity_score * 0.8)

        # Calorie multiplier based on intensity
        # Rest day: 0.90, Light: 0.95, Moderate: 1.00, Hard: 1.10, Very Hard: 1.18
        calorie_multiplier = 0.90 + (intensity_score * 0.35)

        # Categorize intensity
        if intensity_score < 0.3:
            category = 'light'
        elif intensity_score < 0.5:
            category = 'moderate'
        elif intensity_score < 0.75:
            category = 'hard'
        else:
            category = 'very_hard'

        return {
            'intensity_score': round(intensity_score, 2),
            'volume_load': int(total_volume),
            'category': category,
            'calorie_multiplier': round(calorie_multiplier, 2),
        }

    def _get_fallback_exercises(self, params: Dict) -> List[Dict]:
        """Return safe fallback exercises when database filtering yields nothing."""
        fallback = [
            {'name': 'Push-ups', 'sets': params['sets'], 'reps': params['reps'], 'rest': params['rest'], 'muscle_group': 'Chest', 'notes': 'Bodyweight compound'},
            {'name': 'Bodyweight Squats', 'sets': params['sets'], 'reps': params['reps'], 'rest': params['rest'], 'muscle_group': 'Legs', 'notes': 'Bodyweight compound'},
            {'name': 'Plank', 'sets': min(params['sets'], 3), 'reps': '30-45 seconds', 'rest': '30 seconds', 'muscle_group': 'Core', 'notes': 'Isometric hold'},
            {'name': 'Lunges', 'sets': params['sets'], 'reps': params['reps'], 'rest': params['rest'], 'muscle_group': 'Legs', 'notes': 'Bodyweight compound'},
        ]

        for ex in fallback:
            classification = self._classify_exercise_mode(
                ex.get('name', ''),
                ex.get('equipment', ''),
                ex.get('reps', ''),
            )
            ex.update(classification)

        return fallback

# ==========================================
# FACTORY FUNCTION
# ==========================================

_workout_engine_instance = None

def get_workout_engine():
    """Get or create the singleton WorkoutEngine instance"""
    global _workout_engine_instance
    if _workout_engine_instance is None:
        _workout_engine_instance = WorkoutEngine()
    return _workout_engine_instance