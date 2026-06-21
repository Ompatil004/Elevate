import os
import json

DEFAULT_METADATA = {
    "movement_pattern": "generic",
    "trackable": False
}

def normalize_name(name: str) -> str:
    """Normalize exercise names to prevent mismatches from spacing or casing."""
    return (name or "").strip().lower()

_GLOBAL_EXERCISE_MAPPING = {}

def _load_mapping():
    global _GLOBAL_EXERCISE_MAPPING
    # Determine config file path relative to this file (app/services/exercise_metadata.py)
    # The config directory is at app/config/
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    mapping_path = os.path.join(base_dir, 'config', 'exercise_mapping.json')
    
    if not os.path.exists(mapping_path):
        raise FileNotFoundError(f"Exercise mapping file not found at: {mapping_path}")
        
    try:
        with open(mapping_path, 'r', encoding='utf-8') as f:
            raw_data = json.load(f)
    except json.JSONDecodeError as jde:
        raise RuntimeError(f"Malformed exercise_mapping.json - JSON parsing failed: {jde}")
    except Exception as e:
        raise RuntimeError(f"Failed to read exercise mapping: {e}")

    # Validate mapping entry structure & normalize keys
    normalized = {}
    for key, value in raw_data.items():
        if not isinstance(value, dict):
            raise ValueError(f"Invalid entry for exercise '{key}': expected a dictionary configuration.")
        
        # Ensure contract keys are present
        if "movement_pattern" not in value:
            raise ValueError(f"Malformed exercise mapping: '{key}' is missing required field 'movement_pattern'.")
        if "trackable" not in value:
            raise ValueError(f"Malformed exercise mapping: '{key}' is missing required field 'trackable'.")
            
        normalized[normalize_name(key)] = {
            "movement_pattern": value["movement_pattern"],
            "trackable": bool(value["trackable"])
        }
        
    _GLOBAL_EXERCISE_MAPPING = normalized
    print(f"Loaded exercise metadata: {len(_GLOBAL_EXERCISE_MAPPING)} exercises")

# Initialize and validate mapping at module startup
_load_mapping()

def get_exercise_metadata(name: str) -> dict:
    """Get the full metadata contract dictionary for a given exercise name."""
    norm = normalize_name(name)
    return _GLOBAL_EXERCISE_MAPPING.get(norm, DEFAULT_METADATA)

def get_movement_pattern(name: str) -> str:
    """Get the movement pattern string for a given exercise name."""
    return get_exercise_metadata(name)["movement_pattern"]

def is_trackable(name: str) -> bool:
    """Get the trackability flag for a given exercise name."""
    return get_exercise_metadata(name)["trackable"]
