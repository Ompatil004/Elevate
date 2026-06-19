import re
from typing import Dict, Tuple

# Centralised registry populated at initialization and pre-populated with core exercises
EXERCISE_METADATA: Dict[str, Dict] = {
    "Push-Up": {
        "pattern": "horizontal_push",
        "mechanic": "compound",
        "equipment": []
    },
    "Diamond Push-Up": {
        "pattern": "horizontal_push",
        "mechanic": "compound",
        "equipment": []
    },
    "Decline Push-Up": {
        "pattern": "horizontal_push",
        "mechanic": "compound",
        "equipment": []
    },
    "Pull-Up": {
        "pattern": "vertical_pull",
        "mechanic": "compound",
        "equipment": ["pullup_bar"]
    }
}

def get_movement_metadata(name: str, target_muscle: str = "") -> Dict[str, str]:
    """
    Analyzes an exercise name and its target muscle to heuristically determine
    its movement pattern and mechanic. Checks the EXERCISE_METADATA registry first.
    
    Returns:
        Dict with 'pattern' (e.g. 'horizontal_push', 'squat', 'isolation') and 
        'mechanic' ('compound' or 'isolation').
    """
    name_clean = name.strip()
    
    # 1. Exact registry lookup
    if name_clean in EXERCISE_METADATA:
        meta = EXERCISE_METADATA[name_clean]
        return {
            "pattern": meta.get("pattern", "unknown"),
            "mechanic": meta.get("mechanic", "compound")
        }
        
    # 2. Case-insensitive registry lookup
    for k, v in EXERCISE_METADATA.items():
        if k.lower() == name_clean.lower():
            return {
                "pattern": v.get("pattern", "unknown"),
                "mechanic": v.get("mechanic", "compound")
            }

    name_lower = name_clean.lower()
    muscle_lower = target_muscle.lower() if isinstance(target_muscle, str) else ""

    pattern = "unknown"
    mechanic = "compound"

    # 1. Cardio / Full Body
    if "cardio" in muscle_lower or any(x in name_lower for x in ["run", "jog", "jump", "burpee", "cycle", "rowing"]):
        return {"pattern": "cardio", "mechanic": "compound"}

    # 2. Chest (Horizontal Push vs Isolation)
    if "chest" in muscle_lower:
        if any(x in name_lower for x in ["fly", "pec", "cable crossover", "pullover"]):
            pattern = "isolation_upper"
            mechanic = "isolation"
        else:
            pattern = "horizontal_push"
            mechanic = "compound"

    # 3. Back (Pulls)
    elif "back" in muscle_lower or "lats" in muscle_lower:
        if any(x in name_lower for x in ["pull-up", "pullup", "chin-up", "chinup", "pulldown", "lat"]):
            pattern = "vertical_pull"
            mechanic = "compound"
        elif any(x in name_lower for x in ["row"]):
            pattern = "horizontal_pull"
            mechanic = "compound"
        elif any(x in name_lower for x in ["extension", "superman"]):
            pattern = "isolation_upper"
            mechanic = "isolation"
        else:
            # Default to horizontal pull for back if unsure
            pattern = "horizontal_pull"
            mechanic = "compound"

    # 4. Shoulders (Vertical Push vs Isolation)
    elif "shoulder" in muscle_lower or "delts" in muscle_lower:
        if any(x in name_lower for x in ["raise", "fly", "reverse"]):
            pattern = "isolation_upper"
            mechanic = "isolation"
        elif any(x in name_lower for x in ["press", "push"]):
            pattern = "vertical_push"
            mechanic = "compound"
        else:
            pattern = "isolation_upper"
            mechanic = "isolation"

    # 5. Legs (Squat, Hinge, Lunge, Isolation)
    elif "leg" in muscle_lower or "glute" in muscle_lower or "calve" in muscle_lower:
        if any(x in name_lower for x in ["calf", "calves", "extension", "curl", "kickback", "abductor", "adductor"]):
            pattern = "isolation_lower"
            mechanic = "isolation"
        elif any(x in name_lower for x in ["deadlift", "good morning", "swing", "hip thrust", "bridge"]):
            pattern = "hinge"
            mechanic = "compound"
        elif any(x in name_lower for x in ["lunge", "split", "step-up", "step up"]):
            pattern = "lunge"
            mechanic = "compound"
        elif any(x in name_lower for x in ["squat", "press"]):
            pattern = "squat"
            mechanic = "compound"
        else:
            pattern = "squat" # Default heavy leg movement
            mechanic = "compound"

    # 6. Arms (Biceps/Triceps/Forearms) -> Mostly Isolation
    elif "arm" in muscle_lower or "bicep" in muscle_lower or "tricep" in muscle_lower:
        pattern = "isolation_upper"
        mechanic = "isolation"
        if "dip" in name_lower or "close grip" in name_lower:
            pattern = "vertical_push" if "dip" in name_lower else "horizontal_push"
            mechanic = "compound"

    # 7. Core (Waist) -> Anti-rotation, flexion, etc.
    elif "waist" in muscle_lower or "abs" in muscle_lower or "core" in muscle_lower:
        mechanic = "isolation"
        if any(x in name_lower for x in ["plank", "hold", "hollow"]):
            pattern = "anti_rotation"
        elif any(x in name_lower for x in ["twist", "russian", "woodchopper"]):
            pattern = "rotation"
        else:
            pattern = "core"

    # Fallback overrides based purely on name keywords
    if pattern == "unknown":
        if "carry" in name_lower or "walk" in name_lower:
            pattern = "carry"
            mechanic = "compound"
        elif "push" in name_lower or "press" in name_lower:
            pattern = "horizontal_push"
        elif "pull" in name_lower or "row" in name_lower:
            pattern = "horizontal_pull"
        elif "squat" in name_lower:
            pattern = "squat"

    # Cache/register it for future exact lookups
    EXERCISE_METADATA[name_clean] = {
        "pattern": pattern,
        "mechanic": mechanic,
        "equipment": []
    }

    return {
        "pattern": pattern,
        "mechanic": mechanic
    }

