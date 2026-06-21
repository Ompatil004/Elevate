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
    from .progression_engine import get_progression_engine, apply_age_safety_caps as prog_age_caps
except ImportError:
    get_progression_engine = None
    prog_age_caps = None

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
        exercises_processed_repaired = os.path.join(base_dir, 'data', 'exercises_processed_repaired.csv')
        exercises_processed = os.path.join(base_dir, 'data', 'exercises_processed.csv')
        exercises_raw = os.path.join(base_dir, 'data', 'exercises.csv')

        # Load exercises from CSV or create fallback
        try:
            if os.path.exists(exercises_processed_repaired):
                self.exercises_df = pd.read_csv(exercises_processed_repaired)
                print(f" Loaded {len(self.exercises_df)} exercises from repaired processed CSV")
                # Standardize column names to TitleCase format to match expected format
                self.exercises_df.columns = self.exercises_df.columns.str.strip().str.title().str.replace(' ', '_')
            elif os.path.exists(exercises_processed):
                self.exercises_df = pd.read_csv(exercises_processed)
                print(f" Loaded {len(self.exercises_df)} exercises from processed CSV")
                # Standardize column names to TitleCase format to match expected format
                self.exercises_df.columns = self.exercises_df.columns.str.strip().str.title().str.replace(' ', '_')
            elif os.path.exists(exercises_raw):
                self.exercises_df = pd.read_csv(exercises_raw)
                print(f" Loaded {len(self.exercises_df)} exercises from raw CSV")
                # Standardize column names to TitleCase format to match expected format
                self.exercises_df.columns = self.exercises_df.columns.str.strip().str.title().str.replace(' ', '_')
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

                # Standardize column names for fallback DataFrame too
                self.exercises_df.columns = self.exercises_df.columns.str.strip().str.title().str.replace(' ', '_')

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

        # Centralised dynamic registry population
        try:
            import app.utils.movement_mapper as mm
            for idx, row in self.exercises_df.iterrows():
                name = str(row.get('Name', '')).strip()
                target_muscle = str(row.get('Target_Muscle', '')).strip()
                equip = str(row.get('Equipment', '')).strip()
                meta = mm.get_movement_metadata(name, target_muscle)
                mm.EXERCISE_METADATA[name] = {
                    "pattern": meta["pattern"],
                    "mechanic": meta["mechanic"],
                    "equipment": [e.strip().lower() for e in equip.split(',')] if equip else []
                }
            print(f" Registered {len(mm.EXERCISE_METADATA)} exercises in EXERCISE_METADATA registry.")
        except Exception as e:
            print(f" Failed to build EXERCISE_METADATA registry: {e}")

        print(f" WorkoutEngine initialized successfully!\n")

    def _lazy_load_wger(self):
        """Background thread: build WGER media index without blocking startup.

        BUG-P8 fix: signals _wger_ready_event after completion (or failure) so
        callers can safely wait with a timeout instead of reading an empty map.
        """
        try:
            self._initialize_wger_media_index()
        except Exception as e:
            print(f" [WGER-bg] Media index load failed: {e}")
        finally:
            # Always signal — even on failure — so waiters are never blocked forever.
            self._wger_index_ready = True
            self._wger_ready_event.set()

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

    def _normalize_body_issues(self, body_issues: Optional[List[str]]) -> List[str]:
        """Drop placeholder values so injury filters only use real issues."""
        if not body_issues:
            return []
        skip = {'none', 'no issue', 'no issues', 'n/a', 'na', 'nil', 'null', 'undefined'}
        cleaned: List[str] = []
        for issue in body_issues:
            label = str(issue or '').strip().lower()
            if not label or label in skip:
                continue
            cleaned.append(str(issue).strip())
        return cleaned

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
        for mapped_key, media_url in self._wger_name_to_media.items():
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

        for mapped_key, media_url in self._wger_name_to_media.items():
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

        for mapped_key, media_url in self._wger_name_to_media.items():
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
            import glob

            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            # Canonical location: backend-python/app/models
            # Legacy fallback:   backend-python/models
            model_dirs = [
                os.path.join(base_dir, 'models'),
                os.path.join(os.path.dirname(base_dir), 'models'),
            ]

            def _resolve_model_path(*filenames):
                for filename in filenames:
                    if not filename:
                        continue
                    if os.path.isabs(filename) and os.path.exists(filename):
                        return filename
                    for model_dir in model_dirs:
                        candidate = os.path.join(model_dir, filename)
                        if os.path.exists(candidate):
                            return candidate
                return None

            # Try loading the multi-output model first
            versioned_multi_output_paths = []
            for model_dir in model_dirs:
                versioned_multi_output_paths.extend(
                    glob.glob(os.path.join(model_dir, 'xgboost_multi_output_model_v*.joblib'))
                )

            multi_output_path = _resolve_model_path(
                'multi_output_xgboost_model.joblib',
                sorted(versioned_multi_output_paths)[-1] if versioned_multi_output_paths else None,
            )
            multi_output_loaded = False
            
            if multi_output_path:
                try:
                    self.multi_output_model.load_model(multi_output_path)
                    print(" Multi-Output ML model loaded successfully")
                    multi_output_loaded = True
                except Exception as e:
                    print(f" Failed to load Multi-Output ML model: {e}")

            # Load models for different aspects (canonical names first, legacy aliases second)
            volume_path = _resolve_model_path('xgboost_volume.pkl')
            intensity_path = _resolve_model_path('xgboost_intensity.pkl')
            split_path = _resolve_model_path('xgboost_split.pkl')
            frequency_path = _resolve_model_path('xgboost_frequency.pkl')
            sets_path = _resolve_model_path('xgboost_sets.pkl')
            reps_path = _resolve_model_path('xgboost_reps.pkl')
            rest_path = _resolve_model_path('xgboost_rest.pkl')
            progression_path = _resolve_model_path('xgboost_progression.pkl')
            le_goal_path = _resolve_model_path('le_goal.pkl', 'goal_encoder.pkl')
            le_exp_path = _resolve_model_path('label_encoder_experience.pkl')

            # Only print missing model warnings if the multi-output model wasn't loaded
            if volume_path:
                self.xgb_volume_model = joblib.load(volume_path)
                if not multi_output_loaded: print(" Volume ML model loaded successfully")
            else:
                if not multi_output_loaded: print(" Volume ML model not found, using rule-based system")

            if intensity_path:
                self.xgb_intensity_model = joblib.load(intensity_path)
                if not multi_output_loaded: print(" Intensity ML model loaded successfully")
            else:
                if not multi_output_loaded: print(" Intensity ML model not found, using rule-based system")

            if split_path:
                self.xgb_split_model = joblib.load(split_path)
                if not multi_output_loaded: print(" Split ML model loaded successfully")
            else:
                if not multi_output_loaded: print(" Split ML model not found, using rule-based system")

            if frequency_path:
                self.xgb_frequency_model = joblib.load(frequency_path)
                if not multi_output_loaded: print(" Frequency ML model loaded successfully")
            else:
                if not multi_output_loaded: print(" Frequency ML model not found, using rule-based system")

            if sets_path:
                self.xgb_sets_model = joblib.load(sets_path)
                if not multi_output_loaded: print(" Sets ML model loaded successfully")
            else:
                if not multi_output_loaded: print(" Sets ML model not found, using rule-based system")

            if reps_path:
                self.xgb_reps_model = joblib.load(reps_path)
                if not multi_output_loaded: print(" Reps ML model loaded successfully")
            else:
                if not multi_output_loaded: print(" Reps ML model not found, using rule-based system")

            if rest_path:
                self.xgb_rest_model = joblib.load(rest_path)
                if not multi_output_loaded: print(" Rest ML model loaded successfully")
            else:
                if not multi_output_loaded: print(" Rest ML model not found, using rule-based system")

            if progression_path:
                self.xgb_progression_model = joblib.load(progression_path)
                if not multi_output_loaded: print(" Progression ML model loaded successfully")
            else:
                if not multi_output_loaded: print(" Progression ML model not found, using rule-based system")

            if le_goal_path:
                self.le_goal = joblib.load(le_goal_path)
                if not multi_output_loaded: print(" Goal label encoder loaded successfully")
            else:
                if not multi_output_loaded: print(" Goal label encoder not found")

            if le_exp_path:
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
        """Filter exercises by available equipment - RULE-BASED SAFETY LOGIC"""
        if not available_equipment or exercises.empty:
            return exercises

        try:
            if 'Equipment' not in exercises.columns:
                print(" 'Equipment' column not found")
                return exercises

            equipment_lower = [str(e).lower().strip() for e in available_equipment]

            # Add variations
            if 'dumbbell' in equipment_lower:
                equipment_lower.append('dumbbells')
            if 'barbell' in equipment_lower:
                equipment_lower.append('barbells')

            # Always include bodyweight
            bodyweight_terms = ['body weight', 'bodyweight', 'none', 'no equipment']
            equipment_lower.extend(bodyweight_terms)

            filtered = exercises[
                exercises['Equipment'].str.lower().str.strip().isin(equipment_lower)
            ]

            if filtered.empty:
                print(f" No exercises for equipment: {available_equipment}, returning all")
                return exercises

            print(f" Filtered to {len(filtered)} exercises")
            return filtered

        except Exception as e:
            print(f" Error filtering by equipment: {e}")
            return exercises

    def filter_by_injuries(self, exercises: pd.DataFrame, body_issues: List[str]) -> pd.DataFrame:
        """Filter exercises to avoid injuries - RULE-BASED SAFETY LOGIC"""
        body_issues = self._normalize_body_issues(body_issues)
        if not body_issues or exercises.empty:
            return exercises

        # Name-based contraindications for robust injury protection
        NAME_CONTRAINDICATIONS = {
            "shoulder": ["pull-up", "pullup", "overhead press", "pike push", "handstand", "shoulder press", "military press", "neck press", "lateral raise", "front raise", "rear delt"],
            "knee": ["squat", "lunge", "leg extension"],
            "back": ["deadlift", "good morning"],
            "wrist": ["push-up", "pushup", "bench press", "dip"]
        }

        try:
            if 'Avoid_If' not in exercises.columns:
                print(" 'Avoid_If' column not found")
                return exercises

            filtered = exercises.copy()

            for issue in body_issues:
                # 1. DB Avoid_If column check
                filtered = filtered[
                    ~filtered['Avoid_If'].str.contains(issue, case=False, na=False)
                ]
                
                # 2. Hardcoded contraindicated name keywords check
                issue_lower = issue.lower().strip()
                if issue_lower in NAME_CONTRAINDICATIONS:
                    for kw in NAME_CONTRAINDICATIONS[issue_lower]:
                        filtered = filtered[
                            ~filtered['Name'].str.lower().str.contains(kw, na=False)
                        ]

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

        now_year, now_week, _ = _utcnow().isocalendar()
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
                              user_start_day: int, history_memory: dict = None) -> List[Dict]:
        """Build an adaptive onboarding week that starts from registration day."""
        day_names = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        goal = profile.get('goal', 'Muscle Gain')
        experience = profile.get('experience', 'Beginner')
        equipment = profile.get('equipment', ['Dumbbell'])
        body_issues = self._normalize_body_issues(profile.get('body_issues', []))

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
        global_movement_counts: Dict[str, int] = {}

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
                global_movement_counts=global_movement_counts,
                history_memory=history_memory
            )
            for ex in exercises:
                global_used_names.add(ex.get('name', ''))
                # Update movement counts
                moves = self._extract_movement_tokens(ex.get('name', ''))
                for move in moves:
                    global_movement_counts[move] = global_movement_counts.get(move, 0) + 1

            warmup = self._get_warmup_for_focus(focus)
            intensity_metrics = self._calculate_day_intensity(exercises, experience, goal, profile=profile)
            intensity_score = float(intensity_metrics.get('intensity_score', 0.0))
            full_session_exercises = self._enforce_unique_media_per_day(warmup + exercises)

            weekly_plan.append({
                'day_of_week': day_idx,
                'day': day_names[day_idx],
                'focus': focus,
                'warmup': warmup,
                'exercises': full_session_exercises,
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
                'exercises_total': len(full_session_exercises),
                'intensity_metrics': self._build_intensity_metrics(intensity_metrics),
            })

        return weekly_plan

    def _validate_workout(self, day_plan: dict) -> bool:
        """
        Validates workout structural quality (e.g. score > 80, required movements met).
        Returns True if valid, False if it needs regeneration.
        """
        exercises = day_plan.get('exercises', [])
        if not exercises:
            return False
            
        focus = day_plan.get('focus', '').lower()
        
        # Check volume
        if len(exercises) < 3 or len(exercises) > 12:
            return False
            
        # Ensure we have at least one compound movement if not an arms/core day
        has_compound = any(ex.get('mechanic') == 'compound' for ex in exercises)
        if 'arms' not in focus and 'core' not in focus and not has_compound:
            return False
            
        return True

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
            iso_year, iso_week, _ = _utcnow().isocalendar()
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
        gemini_enabled = bool(generate_workout_config and is_gemini_available and is_gemini_available())
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


        from app.progression_engine import get_progression_engine
        prog_engine = get_progression_engine()
        history_memory = prog_engine.parse_history(workout_history) if workout_history else {}
        
        # Phase 3: compute and inject progression state
        progression_state = {}
        if prog_engine:
            progression_state = prog_engine.get_progression_state(profile, workout_history, self.exercises_df)
        profile['_progression_state'] = progression_state
        
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
            weekly_plan = self._build_new_user_plan(profile, split, user_start_day, history_memory)
        else:
            weekly_plan = self._build_weekly_plan(profile, split, rest_day_positions, history_memory)

        total_exercises = sum(len(day.get('exercises', [])) for day in weekly_plan)
        workout_count = sum(1 for day in weekly_plan if day['type'] == 'workout')
        rest_count = sum(1 for day in weekly_plan if day['type'] == 'rest')

        print(f"\n  Generated: {workout_count} workout days, {rest_count} rest days, {total_exercises} total exercises")
        print(f"{'='*60}\n")

        # Issue #4 – cache the result
        if self._plan_cache and not is_new_user:
            self._plan_cache.set(profile, weekly_plan)

        return weekly_plan

    def _get_split_for_experience(self, experience: str, workout_days: int, goal: str, workout_history: List[Dict] = None) -> List[str]:
        """
        Structured templates as requested by the user.
        """
        workout_days = max(1, min(6, int(workout_days or 1)))

        if experience == 'Beginner':
            # Beginner: Full Body, Rest, Full Body, Rest, Full Body
            template = ['Full Body (Upper Focus)', 'Full Body (Lower Focus)', 'Full Body (Push-Pull)', 'Full Body (Upper Focus)', 'Full Body (Lower Focus)', 'Full Body (Push-Pull)']
            return template[:workout_days]
        elif experience == 'Intermediate':
            # Intermediate: Push, Pull, Legs, Upper, Lower
            template = ['Push Focus', 'Pull Focus', 'Legs Focus', 'Upper Focus', 'Lower Focus', 'Push Focus']
            return template[:workout_days]
        else:
            # Advanced: Chest+Triceps, Back+Biceps, Legs, Shoulders, Arms
            template = ['Chest & Triceps', 'Back & Biceps', 'Legs (Quads)', 'Shoulders & Traps', 'Arms & Core', 'Legs (Posterior)']
            return template[:workout_days]

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

    def _allocate_movements(self, focus: str, experience: str) -> List[str]:
        """
        Maps a workout focus to a strict list of required movement patterns.
        """
        focus_lower = focus.lower()
        if 'full body' in focus_lower:
            return ['squat', 'horizontal_push', 'horizontal_pull', 'hinge', 'vertical_push', 'core']
        elif 'upper' in focus_lower:
            return ['horizontal_push', 'horizontal_pull', 'vertical_push', 'vertical_pull', 'isolation_upper']
        elif 'lower' in focus_lower or 'legs' in focus_lower:
            return ['squat', 'hinge', 'lunge', 'isolation_lower', 'core']
        elif 'push' in focus_lower and 'pull' not in focus_lower:
            return ['horizontal_push', 'vertical_push', 'isolation_upper', 'isolation_upper']
        elif 'pull' in focus_lower and 'push' not in focus_lower:
            return ['horizontal_pull', 'vertical_pull', 'isolation_upper', 'isolation_upper']
        elif 'chest & triceps' in focus_lower:
            return ['horizontal_push', 'horizontal_push', 'isolation_upper', 'isolation_upper']
        elif 'back & biceps' in focus_lower:
            return ['horizontal_pull', 'vertical_pull', 'isolation_upper', 'isolation_upper']
        elif 'shoulders & traps' in focus_lower:
            return ['vertical_push', 'vertical_push', 'isolation_upper', 'isolation_upper']
        elif 'arms & core' in focus_lower:
            return ['isolation_upper', 'isolation_upper', 'isolation_upper', 'core', 'anti_rotation']
        else:
            return ['horizontal_push', 'horizontal_pull', 'squat', 'hinge', 'core']

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

    def _build_weekly_plan(self, profile: dict, split: List[str], rest_positions: List[int], history_memory: dict = None) -> List[Dict]:
        """Build the full 7-day plan with exercises for workout days and rest for rest days.
        
        Rest days now include a `restReason` field explaining why that day is a rest day,
        as required by REST_DAY_LOGIC_PLAN.md.
        """
        day_names = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        weekly_plan = []
        split_idx = 0

        goal = profile.get('goal', 'Muscle Gain')
        experience = profile.get('experience', 'Beginner')
        equipment = profile.get('equipment', ['Dumbbell'])
        body_issues = self._normalize_body_issues(profile.get('body_issues', []))

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
        global_movement_counts: Dict[str, int] = {}

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
                    'intensity_metrics': {'intensity_score': 0.0, 'volume_load': 0, 'category': 'rest', 'calorie_multiplier': 0.90},
                })
            else:
                focus = split[split_idx]

                day_seed = self._build_day_seed(profile, focus, day_idx)

                split_idx += 1

                exercises = self._get_exercises_for_day(
                    focus, goal, experience, equipment, body_issues, profile,
                    day_seed=day_seed,
                    global_used_names=global_used_names,
                    global_movement_counts=global_movement_counts,
                    history_memory=history_memory
                )
                # Track which exercises were used this week to prevent cross-day repeats
                for ex in exercises:
                    global_used_names.add(ex.get('name', ''))
                    # Update movement counts
                    moves = self._extract_movement_tokens(ex.get('name', ''))
                    for move in moves:
                        global_movement_counts[move] = global_movement_counts.get(move, 0) + 1

                warmup_exercises = self._get_warmup_for_focus(focus)
                full_session_exercises = self._enforce_unique_media_per_day(warmup_exercises + exercises)

                intensity_metrics = self._calculate_day_intensity(exercises, experience, goal, profile=profile)
                intensity_score = float(intensity_metrics.get('intensity_score', 0.0))

                weekly_plan.append({
                    'day_of_week': day_idx,
                    'day': day_names[day_idx],
                    'focus': focus,
                    'warmup': warmup_exercises,
                    'exercises': full_session_exercises,
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
                    'exercises_total': len(full_session_exercises),
                    'intensity_metrics': intensity_metrics,
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

    def _get_warmup_for_focus(self, focus: str) -> List[Dict]:
        """Return a muscle-targeted warm-up block (max 6 drills)."""
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

        selected_drills = []
        seen_names = set()
        for muscle in target_muscles:
            drills = warmup_drills.get(muscle, warmup_drills['general'])
            for drill in drills[:2]:
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
                if len(selected_drills) >= 5:
                    break
            if len(selected_drills) >= 5:
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

    def _score_exercises(self, candidates: pd.DataFrame, target_muscle: str, goal: str, experience: str, effective_equipment: List[str], global_movement_counts: Dict[str, int], day_seed: int, history_memory: dict = None) -> pd.DataFrame:
        """Score and rank exercise candidates based on multiple factors."""
        if candidates.empty:
            return candidates

        scored = candidates.copy()
        scores = []
        
        import random
        rng = random.Random(day_seed)

        equip_set = set([str(e).lower().strip() for e in effective_equipment])
        
        for _, row in scored.iterrows():
            score = 0.0
            
            name = str(row.get('Name', '')).strip()
            row_equip = str(row.get('Equipment', '')).lower().strip()
            row_diff = str(row.get('Difficulty', '')).strip()
            row_type = str(row.get('Type', '')).strip()
            
            # 1. Experience Match
            if row_diff == experience:
                score += 3.0
            elif (experience == 'Beginner' and row_diff == 'Intermediate') or \
                 (experience == 'Intermediate' and row_diff in ('Beginner', 'Advanced')) or \
                 (experience == 'Advanced' and row_diff == 'Intermediate'):
                score += 1.0
            elif experience == 'Beginner' and row_diff == 'Advanced':
                score -= 5.0  # Penalize heavy mismatch
            elif experience == 'Advanced' and row_diff == 'Beginner':
                score -= 2.0
            
            # 2. Equipment Match
            if equip_set:
                if row_equip in equip_set:
                    score += 2.0
            
            # 3. Goal & Type Match
            is_compound = any(kw in name.lower() for kw in ['press', 'squat', 'deadlift', 'row', 'pull-up', 'push-up', 'lunge', 'clean', 'snatch', 'dip', 'bench', 'overhead']) or row_type == 'Compound'
            
            if is_compound:
                if goal in ('Strength', 'Muscle Gain'):
                    score += 2.0
                else:
                    score += 1.0
            else:
                if goal == 'Muscle Gain':
                    score += 1.0
                    
            # 4. Diversity/Movement frequency penalty
            if global_movement_counts:
                moves = self._extract_movement_tokens(name)
                penalty = 0.0
                for move in moves:
                    count = global_movement_counts.get(move, 0)
                    if count >= 2:
                        penalty -= 5.0 * (count - 1)
                score += penalty
            
            # Tie breaker: small random noise to ensure diversity between days
            score += rng.uniform(0.0, 0.8)
            
            scores.append(score)
            
        scored['_score'] = scores
        return scored.sort_values(by='_score', ascending=False)

    def _get_exercises_for_day(self, focus: str, goal: str, experience: str,
                                equipment: List[str], body_issues: List[str],
                                profile: dict, day_seed: int = 0,
                                global_used_names: Set[str] = None,
                                global_movement_counts: Dict[str, int] = None,
                                history_memory: dict = None) -> List[Dict]:
        """
        New Intelligence Layer Pipeline:
        1. Allocates strict movement patterns based on the day's focus.
        2. Tags all exercises with heuristic movement patterns.
        3. Scores exercises based on history, fatigue, and progression.
        4. Selects the highest scoring exercise for each required pattern.
        """
        import random
        from app.utils.movement_mapper import get_movement_metadata
        
        if global_used_names is None: global_used_names = set()
        if global_movement_counts is None: global_movement_counts = {}
        
        # Determine strict movement patterns required for this day
        required_patterns = self._allocate_movements(focus, experience)
        
        # --- Get exercise parameters based on goal + experience ---
        params = self._get_exercise_params(goal, experience, profile)
        
        # --- Filter exercise pool ---
        pool = self.exercises_df.copy()
        
        BODYWEIGHT_TERMS = ['body weight', 'bodyweight', 'assisted']
        effective_equipment = [str(e).lower().strip() for e in (equipment or []) if str(e).lower().strip() not in ('none', 'no equipment', '')]
        
        if not effective_equipment:
            pool = pool[pool['Equipment'].str.lower().str.strip().isin(BODYWEIGHT_TERMS)]
        else:
            equip_lower = list(effective_equipment)
            SYNONYM_MAP = {
                'dumbbells': ['dumbbell'], 'dumbbell': ['dumbbell'],
                'barbell': ['barbell'], 'olympic barbell': ['olympic barbell', 'barbell'],
                'kettlebell': ['kettlebell'], 'cable': ['cable', 'rope'],
                'resistance bands': ['resistance band', 'band'], 'band': ['resistance band', 'band'],
                'medicine ball': ['medicine ball'], 'stability / yoga ball': ['stability ball', 'bosu ball'],
                'bosu ball': ['bosu ball'], 'foam roller': ['roller'],
                'ab wheel': ['wheel roller'], 'yoga mat': ['roller', 'stability ball']
            }
            expanded = set(equip_lower)
            for eq in equip_lower:
                if eq in SYNONYM_MAP:
                    expanded.update(SYNONYM_MAP[eq])
            
            allowed = list(expanded) + BODYWEIGHT_TERMS
            pool = pool[
                pool['Equipment'].str.lower().str.strip().isin(allowed) |
                pool['Equipment'].str.lower().str.strip().apply(
                    lambda eq_str: any(term in eq_str for term in allowed)
                )
            ]
            
        # Filter by injuries
        pool = self.filter_by_injuries(pool, body_issues)
            
        # Tag the pool with movement patterns dynamically
        if '_pattern' not in pool.columns:
            def _tag(row):
                return get_movement_metadata(str(row.get('Name', '')), str(row.get('Target_Muscle', '')))['pattern']
            pool['_pattern'] = pool.apply(_tag, axis=1)

        selected = []
        used_names = set(global_used_names)
        
        for idx, pattern in enumerate(required_patterns):
            candidates = pool[pool['_pattern'] == pattern].copy()
            
            if candidates.empty:
                candidates = pool[pool['_pattern'].isin(['core', 'cardio'])].copy()
                
            if candidates.empty:
                continue
                
            # Score candidates
            scored = self._score_exercises(
                candidates,
                target_muscle=pattern,
                goal=goal,
                experience=experience,
                effective_equipment=effective_equipment,
                global_movement_counts=global_movement_counts,
                day_seed=day_seed + idx,
                history_memory=history_memory
            )
            
            scored_unused = scored[~scored['Name'].isin(used_names)]
            if scored_unused.empty:
                scored_unused = scored.copy()
            
            scored_unused = scored_unused.sort_values(by='_score', ascending=False)
            best_row = scored_unused.iloc[0]
            
            # Plateau swap logic: if this movement pattern is currently plateaued,
            # swap with Progression_Next or Alternative_Swap from candidates to break it
            prog_state = profile.get('_progression_state', {})
            plateaued_movements = prog_state.get('plateaued_movements', {})
            if pattern in plateaued_movements:
                next_ex = str(best_row.get('Progression_Next', '')).strip()
                alt_ex = str(best_row.get('Alternative_Swap', '')).strip()
                
                swap_candidate = None
                for candidate_name in [next_ex, alt_ex]:
                    if candidate_name and candidate_name.lower() not in ('', 'nan', 'none'):
                        matching_rows = candidates[candidates['Name'].str.lower().str.strip() == candidate_name.lower().strip()]
                        if not matching_rows.empty:
                            matching_unused = matching_rows[~matching_rows['Name'].isin(used_names)]
                            if not matching_unused.empty:
                                swap_candidate = matching_unused.iloc[0]
                                break
                            else:
                                swap_candidate = matching_rows.iloc[0]
                                break
                # Fallback: if no matching progression/alternative swap is available in the candidates pool,
                # select the next highest scoring exercise in the pool that has a different name to break the plateau
                if swap_candidate is None:
                    other_candidates = scored_unused[scored_unused['Name'].str.lower().str.strip() != best_row['Name'].lower().strip()]
                    if not other_candidates.empty:
                        swap_candidate = other_candidates.iloc[0]

                if swap_candidate is not None:
                    best_row = swap_candidate
            
            name = best_row.get('Name', 'Exercise')
            
            used_names.add(name)
            global_used_names.add(name)
            
            media = self._resolve_exercise_media(best_row)
            classification = self._classify_exercise_mode(
                name,
                best_row.get('Equipment', ''),
                params['reps'],
            )
            
            ex_obj = {
                'name': name,
                'sets': params['sets'],
                'reps': params['reps'],
                'rest': params['rest'],
                'muscle_group': str(best_row.get('Target_Muscle', '')),
                'notes': f'Pattern: {pattern.replace("_", " ").title()}',
                'equipment': str(best_row.get('Equipment', '')).strip(),
                'gif': media['gif'],
                'video_url': media['video_url'],
                'image': media['image'],
                'media_type': media['media_type'],
                '_is_compound': best_row.get('_is_compound', False),
            }
            ex_obj.update(classification)
            selected.append(ex_obj)
            
        def _sort_key(ex):
            return 0 if ex.get('_is_compound') else 1
        selected.sort(key=_sort_key)
        
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
            sets = ex.get('sets', 3)
            reps_str = ex.get('reps', '10')
            # Parse rep range (e.g., "8-12" → 10)
            try:
                if '-' in reps_str:
                    reps = sum(int(x) for x in reps_str.split('-')) / 2
                else:
                    reps = int(''.join(filter(str.isdigit, reps_str)) or '10')
            except:
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