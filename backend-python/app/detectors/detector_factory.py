import os
import json
from typing import Dict, Any, Optional

from app.detectors.base_detector import BaseDetector
from app.detectors.squat_detector import SquatDetector
from app.detectors.push_detector import PushDetector
from app.detectors.pull_detector import PullDetector
from app.detectors.curl_detector import CurlDetector
from app.detectors.lunge_detector import LungeDetector
from app.detectors.hinge_detector import HingeDetector
from app.detectors.raise_detector import RaiseDetector
from app.detectors.plank_detector import PlankDetector
from app.detectors.generic_detector import GenericDetector

# Class registry mapping movement patterns to detector classes
DETECTOR_REGISTRY = {
    "squat": SquatDetector,
    "lunge": LungeDetector,
    "hinge": HingeDetector,
    "horizontal_push": PushDetector,
    "vertical_push": PushDetector,
    "horizontal_pull": PullDetector,
    "vertical_pull": PullDetector,
    "row": PullDetector,
    "dip": PullDetector,
    "curl": CurlDetector,
    "tricep_extension": PushDetector,  # Extensions fit push mechanics
    "lateral_raise": RaiseDetector,
    "plank": PlankDetector,
    "crunch": SquatDetector,           # Fallback or generic crunch can use generic or squat angle logic
    "generic": GenericDetector
}

class DetectorFactory:
    _exercise_mapping = {}
    _movement_rules = {}
    _lower_key_map = {}  # lowercase → original key for case-insensitive lookup
    _loaded = False

    # Keyword → movement_pattern fallback when exercise isn't in the mapping
    _KEYWORD_PATTERNS = [
        ("squat", "squat"),
        ("lunge", "lunge"),
        ("deadlift", "hinge"),
        ("hinge", "hinge"),
        ("push up", "horizontal_push"),
        ("pushup", "horizontal_push"),
        ("bench press", "horizontal_push"),
        ("overhead press", "vertical_push"),
        ("shoulder press", "vertical_push"),
        ("pull up", "vertical_pull"),
        ("pullup", "vertical_pull"),
        ("pulldown", "vertical_pull"),
        ("lat pull", "vertical_pull"),
        ("row", "row"),
        ("curl", "curl"),
        ("bicep", "curl"),
        ("tricep", "tricep_extension"),
        ("extension", "tricep_extension"),
        ("raise", "lateral_raise"),
        ("lateral", "lateral_raise"),
        ("plank", "plank"),
        ("crunch", "crunch"),
        ("sit-up", "crunch"),
        ("sit up", "crunch"),
        ("dip", "dip"),
        ("jump", "jump"),
        ("carry", "carry"),
    ]

    @classmethod
    def reset(cls):
        """Reset factory state. Useful for testing."""
        cls._exercise_mapping = {}
        cls._movement_rules = {}
        cls._lower_key_map = {}
        cls._loaded = False

    @classmethod
    def load_configs(cls):
        if cls._loaded:
            return
            
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        
        # Load exercise mapping
        mapping_path = os.path.join(base_dir, 'config', 'exercise_mapping.json')
        if os.path.exists(mapping_path):
            with open(mapping_path, 'r', encoding='utf-8') as f:
                cls._exercise_mapping = json.load(f)
            # Build lowercase key map for case-insensitive lookup
            cls._lower_key_map = {k.lower(): k for k in cls._exercise_mapping}
                
        # Load movement rules
        rules_path = os.path.join(base_dir, 'config', 'movement_rules.json')
        if os.path.exists(rules_path):
            with open(rules_path, 'r', encoding='utf-8') as f:
                cls._movement_rules = json.load(f)
                
        cls._loaded = True

    @classmethod
    def _infer_pattern(cls, exercise_name: str) -> str:
        """Infer the movement pattern from exercise name keywords."""
        name_lower = exercise_name.lower()
        for keyword, pattern in cls._KEYWORD_PATTERNS:
            if keyword in name_lower:
                return pattern
        return "generic"

    @classmethod
    def get_detector(cls, exercise_name: str) -> BaseDetector:
        """
        Retrieves the appropriate detector instance for the given exercise name.
        Supports exact match, case-insensitive match, and keyword-based fallback.
        """
        cls.load_configs()
        
        # 1. Try exact key match
        exercise_cfg = cls._exercise_mapping.get(exercise_name)
        
        # 2. Try case-insensitive match
        if exercise_cfg is None:
            original_key = cls._lower_key_map.get(exercise_name.lower())
            if original_key:
                exercise_cfg = cls._exercise_mapping[original_key]
        
        # 3. Get the movement pattern
        if exercise_cfg:
            pattern = exercise_cfg.get("movement_pattern", "generic")
        else:
            # Keyword-based inference for exercises not in the mapping
            pattern = cls._infer_pattern(exercise_name)
        
        # Look up detector class from the registry
        detector_class = DETECTOR_REGISTRY.get(pattern, GenericDetector)
        
        # Get thresholds for the pattern
        rules = cls._movement_rules.get(pattern, cls._movement_rules.get("generic", {}))
        
        # Return instantiated detector
        return detector_class(rules)

    @classmethod
    def get_exercise_config(cls, exercise_name: str) -> Dict[str, Any]:
        """Get the config for an exercise, with case-insensitive and fallback support."""
        cls.load_configs()
        cfg = cls._exercise_mapping.get(exercise_name)
        if cfg is None:
            original_key = cls._lower_key_map.get(exercise_name.lower())
            if original_key:
                cfg = cls._exercise_mapping[original_key]
        return cfg or {}

    @classmethod
    def get_mapping(cls) -> Dict[str, Any]:
        cls.load_configs()
        return cls._exercise_mapping
